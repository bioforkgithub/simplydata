"""Combining studies (meta-analysis, phase S3b-1): table.combine_studies.

A table with one row per study goes in; the combined effect comes out, said in words, with how much the studies
differ (the prediction interval, the between-study spread tau and I-squared) and, from 10 studies, the notes on
small-study effects. Every number comes from R metafor (table/meta_r.py); simplydata checks the columns, chooses
and prints the defaults, and words the answer (design_evidence_private/s3b_design.md, section 3.3).

* The input routes, one per call: counts (events=, out_of=), estimates with their intervals or standard errors
  (estimates=, standard_errors=), averages (averages=, standard_deviations=, counts=), events and time (events=,
  time=) and correlations (correlations=, counts=).
* simplydata chooses: random effects with REML, Hartung-Knapp intervals with the ad hoc rule (never narrower than
  the normal interval; they change the p-value too), the prediction interval always (from 3 studies), risk ratios
  for counts and standardised differences (Hedges' g) for averages, Peters' test for counts and the classic Egger
  test for the rest, from 10 studies only, worded as small-study effects.
* The result table has one row per study and then the combined rows ("row kind"), with the columns forest_plot
  and draw_funnel_plot read.
"""

from __future__ import annotations

import math
import re

import numpy as np

from .._errors import SimplydataError, friendly
from .checking_more import _new_rows_table
from .stat_tests import _list_words, _num, _skipped_note
from .summaries import _p_sentence

EXAMPLE = ('table.combine_studies(names="trial", events=["tb_vaccinated", "tb_unvaccinated"], '
           'out_of=["vaccinated", "unvaccinated"])   (with sdata.get_example("bcg"))')
SETS = "sets of studies like these"
NL = chr(10)

# show= : (metafor measure, the measure in words, a ratio?, the route it belongs to)
SHOW = {
    "risk ratios": ("RR", "risk ratio", True, "counts"),
    "odds ratios": ("OR", "odds ratio", True, "counts"),
    "risk differences": ("RD", "risk difference", False, "counts"),
    "rate ratios": ("IRR", "rate ratio", True, "rates"),
    "standardised differences": ("SMD", "standardised difference (Hedges' g)", False, "averages"),
    "differences in averages": ("MD", "difference in averages", False, "averages"),
    "ratios of averages": ("ROM", "ratio of averages", True, "averages"),
}
# the measure in words -> its plural ("the true risk ratios")
PLURALS = {"risk ratio": "risk ratios", "odds ratio": "odds ratios", "risk difference": "risk differences",
           "rate ratio": "rate ratios", "standardised difference (Hedges' g)": "standardised differences",
           "difference in averages": "differences in averages", "ratio of averages": "ratios of averages",
           "correlation": "correlations"}
# names that say an estimate is a ratio, as whole words ("duration" is not one)
RATIO_NAME = re.compile(r"(?<![a-z0-9])(ratios?|or|hr|rr|irr|sir|smr)(?![a-z0-9])", re.IGNORECASE)
# the "combined on" column of the result: how forest_plot and draw_funnel_plot know the scale
ON_SCALE = {"exp": "log scale (ratios)", "ztor": "Fisher's z scale", "none": "plain scale"}
SHOW_SPELLINGS = {
    "risk ratio": "risk ratios", "relative risks": "risk ratios", "relative risk": "risk ratios", "rr": "risk ratios",
    "odds ratio": "odds ratios", "or": "odds ratios", "risk difference": "risk differences",
    "rd": "risk differences", "rate ratio": "rate ratios", "incidence rate ratios": "rate ratios",
    "irr": "rate ratios", "standardized differences": "standardised differences",
    "standardised difference": "standardised differences", "standardized difference": "standardised differences",
    "hedges g": "standardised differences", "hedges' g": "standardised differences",
    "smd": "standardised differences", "difference in averages": "differences in averages",
    "mean differences": "differences in averages", "md": "differences in averages",
    "ratio of averages": "ratios of averages", "response ratios": "ratios of averages",
    "log response ratios": "ratios of averages", "rom": "ratios of averages",
}
ROUTE_DEFAULT = {"counts": "risk ratios", "rates": "rate ratios", "averages": "standardised differences"}

# test_method= : (metafor method, in words, random effects?). The values are written in lower case, as every
# test_method= value is; the capitalised forms ("REML", "Peto" ...) are still accepted.
METHODS = {
    "reml": ("REML", "random effects, REML", True),
    "dersimonian-laird": ("DL", "random effects, DerSimonian-Laird", True),
    "paule-mandel": ("PM", "random effects, Paule-Mandel", True),
    "common effect": ("EE", "common effect", False),
    "mantel-haenszel": ("MH", "common effect, Mantel-Haenszel", False),
    "peto": ("PETO", "common effect, Peto", False),
}
METHOD_SPELLINGS = {
    "reml": "reml", "random effects": "reml", "random effect": "reml", "random": "reml",
    "dersimonian-laird": "dersimonian-laird", "dersimonian laird": "dersimonian-laird", "dl": "dersimonian-laird",
    "paule-mandel": "paule-mandel", "paule mandel": "paule-mandel", "pm": "paule-mandel",
    "common effect": "common effect", "common": "common effect", "fixed effect": "common effect",
    "fixed effects": "common effect", "fixed": "common effect", "equal effects": "common effect",
    "fe": "common effect", "ee": "common effect",
    "mantel-haenszel": "mantel-haenszel", "mantel haenszel": "mantel-haenszel", "mh": "mantel-haenszel",
    "peto": "peto",
}
INTERVALS = {"Hartung-Knapp": "adhoc", "normal": "z"}
INTERVAL_SPELLINGS = {"hartung-knapp": "Hartung-Knapp", "knapp-hartung": "Hartung-Knapp", "hksj": "Hartung-Knapp",
                      "knha": "Hartung-Knapp", "hartung knapp": "Hartung-Knapp", "normal": "normal", "z": "normal",
                      "wald": "normal"}
SMALL_STUDIES = 10   # Egger / Peters and trim and fill from 10 studies (Sterne et al. 2011)
FEW_STUDIES = 5      # under 5 studies the between-study spread is hard to estimate
PI_STUDIES = 3       # a prediction interval needs 3 studies


def _text_choice(value, spellings, choices, option, step="combine_studies"):
    """A choice given as text, matched without regard to case or other spellings; None stays None."""
    if value is None:
        return None
    if isinstance(value, str):
        key = " ".join(value.strip().split())
        if key in choices:
            return key
        found = spellings.get(key.lower())
        if found:
            return found
        for choice in choices:
            if choice.lower() == key.lower():
                return choice
    listed = ", ".join(f'"{c}"' for c in choices)
    raise SimplydataError(f"{step}() does not know {option}={value!r}. It takes {listed}.")


def _pct(x) -> str:
    return "nan" if x is None or math.isnan(x) else f"{x:.0f} %"


def _p_meta(p, if_none, this, not_shown, shown=None):
    """The W2 sentence, said of sets of studies: "... would turn up in about 3 of 100 sets of studies like
    these (p = 0.031)"."""
    return _p_sentence(p, if_none=if_none, this=this, not_shown=not_shown, shown=shown, like=SETS)


def _value(x):
    """A number from R (a length-1 array or a float) as a float; NaN when R gave none."""
    if x is None:
        return math.nan
    arr = np.atleast_1d(np.asarray(x, dtype=float))
    return float(arr[0]) if arr.size else math.nan


def _floats(x, n=None):
    arr = np.atleast_1d(np.asarray([np.nan] * (n or 0) if x is None else x, dtype=float))
    return arr


def _pair(step, option, value):
    """A list of two column names (the first group, then the second)."""
    if (not isinstance(value, (list, tuple)) or len(value) != 2
            or not all(isinstance(v, str) for v in value)):
        raise SimplydataError(f"{step}() needs {option} as a list of two column names: the first group, then the "
                              f"second (the group compared with).\nFor example, {EXAMPLE}")
    return list(value)


class MetaWords:
    # ------------------------------------------------------------------ combine_studies
    @friendly(renamed={"method": "test_method"}, others={"slab": "names", "studlab": "names", "subgroup": "for_each_group_in", "byvar": "for_each_group_in",
                      "mods": "using", "moderators": "using", "sei": "standard_errors", "measure": "show",
                      "sm": "show", "test": "interval_by", "ri": "correlations"})
    def combine_studies(self, names=None, events=None, out_of=None, estimates=None, standard_errors=None,
                        averages=None, standard_deviations=None, counts=None, time=None, correlations=None,
                        show=None, test_method="reml", interval_by=None, for_each_group_in=None, using=None,
                        estimates_are_ratios=None):
        """Combine the results of several studies into one (a meta-analysis), with how much they differ.

        table.combine_studies(names="trial", events=["tb_vaccinated", "tb_unvaccinated"],
        out_of=["vaccinated", "unvaccinated"])   (with sdata.get_example("bcg"))
        One row per study. Give one way in, each as columns of the table:
        counts: events=[first, second] and out_of=[first, second], the events and the people in
          the two groups of each study; show="risk ratios" (default), "odds ratios" or "risk
          differences".
        estimates: estimates="odds ratio" with the columns "odds ratio 95 % CI low" and "... high"
          next to it (any level), or with standard_errors="se". Ratios (a name with "ratio", or
          estimates_are_ratios=True) are combined on the log scale and shown back as ratios; with
          standard_errors=, give the standard errors of the log ratios, as a model reports them.
        averages: averages=[first, second], standard_deviations=[...], counts=[...]; show=
          "standardised differences" (Hedges' g, default), "differences in averages" (the same
          units in every study) or "ratios of averages" (the log response ratio of ecology).
        names="trial" names the rows. Prints the combined effect with its 95 % interval and
        p-value, the prediction interval (where the true effect of a new setting like these
        would lie), tau (how much the true effects differ, as a factor for ratios) and I-squared
        (the share of the spread that is beyond chance), and from 10 studies the notes on
        small-study effects (Peters' test for risk and odds ratios from counts, Egger's test
        for the rest, and trim and fill as a what-if). Gives back one row per study (estimate, interval, standard error,
        weight %) and the combined rows ("row kind"), ready for forest_plot and draw_funnel_plot.
        More: events= with time= (rate ratios); correlations="r" with counts="n";
        test_method="reml" (default), "dersimonian-laird", "paule-mandel", "common effect",
        "mantel-haenszel", "peto"; interval_by="Hartung-Knapp" (default for random effects; it
        changes the p-value too) or "normal"; for_each_group_in="region" (subgroups, each with
        its own spread, and the test of their difference first); using=["latitude"]
        (meta-regression). Needs R metafor (pip install "simplydata[r]"). Other names:
        meta-analysis, rma, metagen, metabin, hksj, egger, trimfill, i2.
        """
        from .meta_r import combine

        step = "combine_studies"
        route, cols = self._meta_route(step, events, out_of, estimates, standard_errors, averages,
                                       standard_deviations, counts, time, correlations)
        method_name = _text_choice(test_method if test_method is not None else "reml", METHOD_SPELLINGS, tuple(METHODS),
                                   "test_method")
        r_method, method_words, random = METHODS[method_name]
        interval_name = _text_choice(interval_by, INTERVAL_SPELLINGS, tuple(INTERVALS), "interval_by")
        if interval_name is None:
            interval_name = "Hartung-Knapp" if random else "normal"
        elif interval_name == "Hartung-Knapp" and not random:
            raise SimplydataError(f'interval_by="Hartung-Knapp" is for random effects; test_method="{method_name}" assumes '
                                  "one common effect and gives the normal interval. Leave out interval_by=, or use "
                                  'test_method="reml".')
        test = INTERVALS[interval_name]
        if estimates_are_ratios is not None and not isinstance(estimates_are_ratios, bool):
            raise SimplydataError("estimates_are_ratios= is True or False.")
        if estimates_are_ratios is not None and route not in ("intervals", "errors"):
            raise SimplydataError("estimates_are_ratios= goes with estimates=: it says whether the estimates are "
                                  "ratios (combined on the log scale). The other ways in know it from show=.")
        # what is shown
        show_name = _text_choice(show, SHOW_SPELLINGS, tuple(SHOW), "show")
        if route in ("intervals", "errors", "correlations"):
            if show_name is not None:
                raise SimplydataError(f"show= chooses the effect worked out from counts, events and time, or "
                                      f"averages; with {'correlations=' if route == 'correlations' else 'estimates='} "
                                      "the effect is the one in the table. Leave out show=.")
            if route == "correlations":
                measure, words, ratio, transform = "ZCOR", "correlation", False, "ztor"
            else:
                ratio = (estimates_are_ratios if estimates_are_ratios is not None
                         else bool(RATIO_NAME.search(estimates.replace("_", " "))))
                measure, words, transform = "GEN", estimates, ("exp" if ratio else "none")
        else:
            if method_name == "peto" and route != "counts":
                raise SimplydataError('test_method="peto" combines counts: it needs events= and out_of=.')
            if method_name == "peto" and show_name is None:
                show_name = "odds ratios"
            show_name = show_name or ROUTE_DEFAULT[route]
            r_measure, words, ratio, belongs = SHOW[show_name]
            if belongs != route:
                raise SimplydataError(self._show_error(show_name, route))
            measure, transform = r_measure, ("exp" if ratio else "none")
        if method_name == "peto" and measure != "OR":
            raise SimplydataError('test_method="peto" gives odds ratios only. For example, table.combine_studies(names='
                                  '"trial", events=[...], out_of=[...], show="odds ratios", test_method="peto").')
        if method_name == "mantel-haenszel" and route not in ("counts", "rates"):
            raise SimplydataError('test_method="mantel-haenszel" combines counts: it needs events= with out_of= (or with '
                                  "time=). For estimates, averages or correlations use the default test_method=\"reml\" or "
                                  'test_method="common effect".')
        if method_name == "peto" and route != "counts":
            raise SimplydataError('test_method="peto" combines counts: it needs events= and out_of=.')
        if for_each_group_in is not None and using is not None:
            raise SimplydataError("Give for_each_group_in= (subgroups) or using= (meta-regression), not both.")
        mods_names = [] if using is None else ([using] if isinstance(using, str) else list(using))
        if using is not None and (not mods_names or not all(isinstance(m, str) for m in mods_names)):
            raise SimplydataError('using= takes the number columns that may explain the differences between studies, '
                                  'such as using=["latitude"].')
        if mods_names and method_name in ("mantel-haenszel", "peto"):
            raise SimplydataError(f'using= (meta-regression) needs the default test_method="reml" (or another '
                                  f'inverse-variance method), not test_method="{method_name}".')
        if for_each_group_in is not None:
            self._need_name(step, "for_each_group_in=", for_each_group_in, EXAMPLE)
        if names is not None:
            self._need_name(step, "names=", names, EXAMPLE)
        # the rows
        number_cols = [c for c in cols.values() if isinstance(c, str)]
        extra = mods_names + ([for_each_group_in] if for_each_group_in else []) + ([names] if names else [])
        self._need_columns(*number_cols, *extra)
        for c in number_cols + mods_names:
            if not self._frame.schema[c].is_numeric():
                raise SimplydataError(f'{step}() needs numbers in "{c}".' + (
                    ' For a text column, use for_each_group_in= (subgroups).' if c in mods_names else ""))
        used = list(dict.fromkeys(number_cols + extra))
        frame = self._frame.select(*used).to_pandas()
        keep = ~frame.isna().any(axis=1)
        _skipped_note(int((~keep).sum()), used)
        frame = frame[keep]
        k = len(frame)
        if k < 2:
            raise SimplydataError(f"{step}() needs at least 2 studies with every value given (here {k}).")
        labels = ([str(v) for v in frame[names]] if names else [f"study {i}" for i in range(1, k + 1)])
        values = {key: frame[c].to_numpy(dtype=float) if isinstance(c, str) else c for key, c in cols.items()}
        self._meta_check_values(step, route, values, cols, ratio, measure, labels)
        if route in ("intervals", "errors"):
            values["ratio"] = bool(ratio)
        informative = self._meta_double_zero(route, values, measure)
        studies_with = int(informative.sum())
        if studies_with < 2:
            raise SimplydataError(f"{step}() needs at least 2 studies with an event in some group; the others have "
                                  "no events in either group, so they tell nothing about a ratio.")
        group = levels = None
        if for_each_group_in is not None:
            group = [str(v) for v in frame[for_each_group_in]]
            found = list(dict.fromkeys(group))  # the order of first appearance
            levels = [g for g in found if any(informative[i] for i in range(k) if group[i] == g)]
            empty = [g for g in found if g not in levels]
            if empty:
                print(f'Note: {_list_words(chr(34) + g + chr(34) for g in empty)} of "{for_each_group_in}" '
                      f"{'has' if len(empty) == 1 else 'have'} no study with an event in either group, so "
                      f"{'it is' if len(empty) == 1 else 'they are'} left out of the subgroups.")
            if len(levels) < 2:
                raise SimplydataError(f'for_each_group_in="{for_each_group_in}" has only one group with studies to '
                                      "combine in the rows used.")
        mods = None
        if mods_names:
            mods = np.column_stack([frame[m].to_numpy(dtype=float) for m in mods_names])
        peters = route == "counts" and measure in ("RR", "OR")
        # with Peto, each study's own odds ratio is Peto's too (escalc measure "PETO")
        study_measure = "PETO" if method_name == "peto" else measure
        try:
            out = combine(route, values, study_measure, r_method, test, transform, drop00=measure != "RD",
                          group=group, levels=levels, mods=mods, small=True, peters=peters)
        except SimplydataError as error:
            if "converge" not in str(error).lower():
                raise
            raise SimplydataError(f"{error}" + NL + "REML did not settle on the between-study spread with these studies. Try "
                                  'test_method="paule-mandel" or test_method="dersimonian-laird".') from None
        info = dict(step=step, route=route, cols=cols, measure=measure, words=words, ratio=ratio,
                    transform=transform, method_name=method_name, method_words=method_words, random=random,
                    interval_name=interval_name, test=test, labels=labels, k=k, peters=peters,
                    for_each=for_each_group_in, group=group, levels=levels, mods_names=mods_names)
        rows = self._meta_say(out, info)
        return _new_rows_table(self, rows)

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _show_error(show_name, route):
        wanted = {"counts": "events= and out_of=", "rates": "events= and time=",
                  "averages": "averages=, standard_deviations= and counts="}[SHOW[show_name][3]]
        given = {"counts": "events= and out_of=", "rates": "events= and time=",
                 "averages": "averages=, standard_deviations= and counts="}[route]
        return (f'show="{show_name}" is worked out from {wanted}, but the table gives {given}. The effects for '
                f"{given}: " + ", ".join(f'"{s}"' for s, v in SHOW.items() if v[3] == route) + ".")

    def _meta_route(self, step, events, out_of, estimates, standard_errors, averages, standard_deviations, counts,
                    time, correlations):
        """The one way in (route) and its columns: {name in R: column}."""
        starts = {"events=": events, "estimates=": estimates, "averages=": averages, "correlations=": correlations}
        given = [k for k, v in starts.items() if v is not None]
        if len(given) > 1:
            raise SimplydataError(f"{step}() takes one way in at a time, but {_list_words(given)} were given. Choose "
                                  f"one, for example {EXAMPLE}")
        if not given:
            raise SimplydataError(f"{step}() needs the studies' results: events= and out_of= (counts), estimates= "
                                  "(with their intervals or standard_errors=), or averages=, standard_deviations= and "
                                  f"counts=.\nFor example, {EXAMPLE}")

        def stray(allowed):
            others = {"out_of=": out_of, "standard_errors=": standard_errors, "standard_deviations=": standard_deviations,
                      "counts=": counts, "time=": time}
            extra = [k for k, v in others.items() if v is not None and k not in allowed]
            if extra:
                raise SimplydataError(f"{_list_words(extra)} {'does' if len(extra) == 1 else 'do'} not go with "
                                      f"{given[0]}. For example, {EXAMPLE}")

        if events is not None:
            first = _pair(step, "events=", events)
            if (out_of is None) == (time is None):
                raise SimplydataError(f"{step}() with events= needs out_of= (the people in each group) or time= (the "
                                      f"time each group was followed), one of them.\nFor example, {EXAMPLE}")
            if out_of is not None:
                stray(("out_of=",))
                second = _pair(step, "out_of=", out_of)
                return "counts", {"a1": first[0], "n1": second[0], "a2": first[1], "n2": second[1]}
            stray(("time=",))
            second = _pair(step, "time=", time)
            return "rates", {"x1": first[0], "t1": second[0], "x2": first[1], "t2": second[1]}
        if averages is not None:
            stray(("standard_deviations=", "counts="))
            if standard_deviations is None or counts is None:
                raise SimplydataError(f"{step}() with averages= needs standard_deviations= and counts= too, each a list "
                                      "of two columns: table.combine_studies(names=\"study\", averages=[\"mean_new\", "
                                      "\"mean_usual\"], standard_deviations=[\"sd_new\", \"sd_usual\"], counts=[\"n_new\", "
                                      "\"n_usual\"])")
            m, s, c = (_pair(step, o, v) for o, v in (("averages=", averages), ("standard_deviations=", standard_deviations),
                                                      ("counts=", counts)))
            return "averages", {"m1": m[0], "s1": s[0], "c1": c[0], "m2": m[1], "s2": s[1], "c2": c[1]}
        if correlations is not None:
            stray(("counts=",))
            if not isinstance(correlations, str) or not isinstance(counts, str):
                raise SimplydataError(f'{step}() with correlations= needs counts= too, each one column: '
                                      'table.combine_studies(names="study", correlations="r", counts="n")')
            return "correlations", {"r": correlations, "n": counts}
        stray(("standard_errors=",))
        if not isinstance(estimates, str):
            raise SimplydataError(f'{step}() needs estimates= as one column name, such as estimates="odds ratio".')
        if standard_errors is not None:
            if not isinstance(standard_errors, str):
                raise SimplydataError("standard_errors= is one column name, such as standard_errors=\"se\".")
            return "errors", {"est": estimates, "se": standard_errors}
        from ..words.agreement_charts import _all_interval_columns

        found = _all_interval_columns(list(self._frame.columns), estimates)
        if not found:
            raise SimplydataError(
                f'{step}() did not find the interval of "{estimates}": it looks for the columns "{estimates} 95 % CI low" '
                f'and "{estimates} 95 % CI high" (any level, such as 90 %). Two ways in:\n'
                f'  table.combine_studies(names="study", estimates="{estimates}", standard_errors="se")   with a column '
                "of standard errors\n"
                f'  table.rename_column("lower", "{estimates} 95 % CI low")   and the same for the upper end, then '
                f'table.combine_studies(names="study", estimates="{estimates}")')
        low, high, level = found[0]
        return "intervals", {"est": estimates, "lo": low, "hi": high, "level": float(level.split()[0])}

    @staticmethod
    def _meta_check_values(step, route, v, cols, ratio, measure, labels):
        def bad(mask, text):
            if np.any(mask):
                rows = ", ".join(f'"{labels[i]}"' for i in np.flatnonzero(mask)[:10])
                raise SimplydataError(f"{step}(): {text} (in {rows}).")

        if route == "counts":
            for e, n in (("a1", "n1"), ("a2", "n2")):
                bad((v[e] < 0) | (v[e] != np.round(v[e])), f'"{cols[e]}" should hold counts of events (whole numbers of 0 '
                                                           "or more)")
                bad((v[n] <= 0) | (v[n] != np.round(v[n])), f'"{cols[n]}" should hold the number of people (whole '
                                                            "numbers above 0)")
                bad(v[e] > v[n], f'"{cols[e]}" is bigger than "{cols[n]}" in some studies: there cannot be more events '
                                 "than people")
        elif route == "rates":
            for e, t in (("x1", "t1"), ("x2", "t2")):
                bad((v[e] < 0) | (v[e] != np.round(v[e])), f'"{cols[e]}" should hold counts of events (whole numbers of 0 '
                                                           "or more)")
                bad(v[t] <= 0, f'"{cols[t]}" should hold the time each group was followed (above 0)')
        elif route == "averages":
            for s, c in (("s1", "c1"), ("s2", "c2")):
                bad(v[s] <= 0, f'"{cols[s]}" should hold standard deviations above 0')
                bad((v[c] < 2) | (v[c] != np.round(v[c])), f'"{cols[c]}" should hold the number of values in each group '
                                                           "(whole numbers, 2 or more)")
            if measure == "ROM":
                bad((v["m1"] <= 0) | (v["m2"] <= 0), 'show="ratios of averages" needs averages above 0 (the log of a '
                                                     "ratio of averages)")
        elif route == "intervals":
            bad((v["lo"] > v["est"]) | (v["est"] > v["hi"]), f'each estimate should lie inside its interval ("{cols["lo"]}" '
                                                             f'to "{cols["hi"]}")')
            bad(v["lo"] == v["hi"], "an interval has no width, so the study's standard error would be 0")
            if ratio:
                bad(v["lo"] <= 0, f'"{cols["est"]}" are ratios, so they and their intervals must be above 0 (or say '
                                  "estimates_are_ratios=False)")
        elif route == "errors":
            bad(v["se"] <= 0, f'"{cols["se"]}" should hold standard errors above 0')
            if ratio:
                bad(v["est"] <= 0, f'"{cols["est"]}" are ratios, so they must be above 0 (or say '
                                   "estimates_are_ratios=False)")
        else:
            bad((v["r"] <= -1) | (v["r"] >= 1), f'"{cols["r"]}" should hold correlations between -1 and 1')
            bad(v["n"] < 4, f'"{cols["n"]}" should hold the number of pairs in each study (4 or more)')

    @staticmethod
    def _meta_double_zero(route, v, measure):
        """Which studies have an effect: for ratios from counts, a study with no events in either group (or
        events in everyone) says nothing and is left out (counting only; metafor's drop00)."""
        if route == "counts" and measure != "RD":
            none = ((v["a1"] == 0) & (v["a2"] == 0)) | ((v["a1"] == v["n1"]) & (v["a2"] == v["n2"]))
            return ~none
        if route == "rates":
            return ~((v["x1"] == 0) & (v["x2"] == 0))
        return np.ones(len(next(v[key] for key in v if not isinstance(v[key], (bool, float)))), dtype=bool)

    # ------------------------------------------------------------------ the words
    def _meta_say(self, out, info):
        words = info["words"]
        k, labels = info["k"], info["labels"]
        what = self._meta_what(info)
        rows = []
        study = _floats(out["study"]); low = _floats(out["study_low"]); high = _floats(out["study_high"])
        se = _floats(out["study_se"]); weights = _floats(out["weights"], k)
        groups = info["group"]
        if groups is not None:  # with subgroups, each study's weight inside its own subgroup
            weights = np.full(k, np.nan)
            for level in info["levels"]:
                inside = _floats(out["groups"][level]["weights"], k)
                weights = np.where(np.isnan(inside), weights, inside)
        on = ON_SCALE[info["transform"]]
        for i in range(k):
            row = {"study": labels[i], "row kind": "study"}
            if groups is not None:
                row["subgroup"] = groups[i]
            row.update({"measure": words, "estimate": float(study[i]), "estimate 95 % CI low": float(low[i]),
                        "estimate 95 % CI high": float(high[i]), "standard error": float(se[i]),
                        "weight %": float(weights[i]), "combined on": on})
            rows.append(row)
        left = [labels[int(i) - 1] for i in np.atleast_1d(out.get("double_zero", [])).astype(int)] if out.get(
            "double_zero") is not None else []
        used = k - len(left)
        how = f"{info['method_words']}" + (", Hartung-Knapp" if info["interval_name"] == "Hartung-Knapp" else "")
        print(f"Combining {used} studies ({how}): {what}.")
        if left:
            print(f"Note: {len(left)} {'study has' if len(left) == 1 else 'studies have'} no events in either group "
                  f"({_list_words(chr(34) + s + chr(34) for s in left)}), so {'it says' if len(left) == 1 else 'they say'}"
                  f" nothing about a {words} and {'is' if len(left) == 1 else 'are'} left out (as in Cochrane reviews).")
        corrected = int(_value(out.get("corrected")) or 0)
        if corrected:
            print(f"Note: {corrected} {'study has' if corrected == 1 else 'studies have'} a 0 in one group; metafor "
                  "added 1/2 to every cell of those tables so their effect and its variance can be worked out (add = 1/2, "
                  "to = \"only0\").")
        if info["mods_names"]:
            rows += self._meta_regression(out["mods"], info)
        else:
            if info["for_each"] is not None:
                rows += self._meta_subgroups(out, info)
                print("All the studies together:")
            rows += self._meta_combined(out["all"], info, used, label="combined", indent="")
            rows += self._meta_small_studies(out, info, used)
        print(self._meta_method_line(info))
        print("simplydata chooses: random effects with REML, Hartung-Knapp intervals for random effects (never narrower "
              "than the normal interval), the prediction interval from 3 studies, and the notes on small-study effects "
              "from 10 studies (Peters' test for risk and odds ratios from counts, Egger's test for the rest); test_method= "
              "and interval_by= change them.")
        return rows

    @staticmethod
    def _meta_what(info):
        cols, route, words = info["cols"], info["route"], info["words"]
        if route == "counts":
            return (f'{words} of "{cols["a1"]}" out of "{cols["n1"]}" against "{cols["a2"]}" out of "{cols["n2"]}"')
        if route == "rates":
            return f'{words} of "{cols["x1"]}" per "{cols["t1"]}" against "{cols["x2"]}" per "{cols["t2"]}"'
        if route == "averages":
            return f'{words} of "{cols["m1"]}" against "{cols["m2"]}"'
        if route == "correlations":
            return f'correlations "{cols["r"]}" (combined as Fisher\'s z, shown back as correlations)'
        if info["ratio"]:
            return f'"{words}" (ratios, combined on the log scale and shown back as ratios; estimates_are_ratios=False ' \
                   "says they are not)"
        return f'"{words}"'

    def _meta_combined(self, a, info, used, label, indent, subgroup=None):
        """The combined effect, the prediction interval and the spread, in words; and their rows."""
        ratio, words = info["ratio"], info["words"]
        null = 1 if ratio else 0
        est, lo, hi, p = (_value(a[x]) for x in ("est", "low", "high", "p"))
        interval = "Hartung-Knapp" if info["interval_name"] == "Hartung-Knapp" and a.get("df") is not None and \
            not math.isnan(_value(a["df"])) else "normal"
        name = f"Combined {words}" if subgroup is None else f'"{subgroup}": combined {words}'
        if int(_value(a["k"])) == 1:
            interval = "normal, the study's own"
        print(f"{indent}{name} {_num(est)} (95 % CI {_num(lo)} to {_num(hi)}, {interval}; {int(_value(a['k']))} "
              f"{'study' if int(_value(a['k'])) == 1 else 'studies'}).")
        if subgroup is None:
            print(indent + _p_meta(p, if_none=f"there were truly no effect on average ({_a(words)} of {null})",
                                   this=f"a combined effect this far from {null} or further",
                                   not_shown="that there is no effect"))
        row = {"study": label if subgroup is None else f"{subgroup}: combined", "row kind": "combined" if subgroup is None
               else "combined in subgroup"}
        if info["group"] is not None:
            row["subgroup"] = subgroup if subgroup is not None else "all"
        row.update({"measure": words, "estimate": est, "estimate 95 % CI low": lo, "estimate 95 % CI high": hi,
                    "standard error": _value(a["se"]), "weight %": 100.0, "combined on": ON_SCALE[info["transform"]],
                    "p-value": p, "studies": float(_value(a["k"]))})
        k = int(_value(a["k"]))
        rows = [row]
        if k < 2:
            print(f"{indent}One study: it is its own result, with no spread between studies to judge.")
            row.update({"tau": math.nan, "tau squared": math.nan, "I squared %": math.nan, "Q": math.nan,
                        "Q degrees of freedom": math.nan, "Q p-value": math.nan})
            return rows
        if not info["random"]:
            print(f"{indent}A common-effect model assumes every study measured the same effect, so it gives no "
                  "prediction interval and no between-study spread; the Q test and I-squared below still show how "
                  "much the studies differ.")
        elif k < PI_STUDIES:
            print(f"{indent}With {k} studies there is no prediction interval (it needs {PI_STUDIES}).")
            if k == 2 and interval == "Hartung-Knapp":
                print(f"{indent}With 2 studies the Hartung-Knapp interval is very wide; that is honest, not an error.")
        else:
            pl, ph = _value(a["pi_low"]), _value(a["pi_high"])
            dist = str(np.atleast_1d(a.get("pi_dist", [""]))[0])
            df = _value(a.get("pi_df"))
            dist_words = (f"t with {int(df)} degrees of freedom, as metafor uses with Hartung-Knapp; Higgins et al. 2009 "
                          f"use {int(df) - 1}") if dist == "t" and not math.isnan(df) else "normal"
            print(f"{indent}In a new setting like these studies, the true {words} would lie between {_num(pl)} and "
                  f"{_num(ph)} (95 % prediction interval, {dist_words}).")
            rows.append({"study": "prediction interval" if subgroup is None else f"{subgroup}: prediction interval",
                         "row kind": "prediction interval", **({"subgroup": row["subgroup"]} if "subgroup" in row else {}),
                         "measure": words, "estimate": est, "estimate 95 % CI low": pl, "estimate 95 % CI high": ph})
        tau, tau2 = _value(a["tau"]), _value(a["tau2"])
        if info["random"] and k >= 2:
            t2l, t2h = _value(a["tau2_low"]), _value(a["tau2_high"])
            t2ci = "" if math.isnan(t2l) else f", 95 % CI {_num(t2l)} to {_num(t2h)}"
            if ratio:
                factor = _value(a["tau_factor"])
                print(f"{indent}The true {_plural(words)} typically differ from the average by a factor of about {_num(factor)} up "
                      f"or down (tau = {_num(tau)} on the log scale; tau-squared = {_num(tau2)}{t2ci}).")
            elif info["transform"] == "ztor":
                print(f"{indent}The true effects typically differ from the average by tau = {_num(tau)} on Fisher's z "
                      f"scale (tau-squared = {_num(tau2)}{t2ci}).")
            else:
                unit = f"in {_plural(words)}" if words in PLURALS else f'in the units of "{words}"'
                print(f"{indent}The true effects typically differ from the average by tau = {_num(tau)} ({unit}: "
                      f"the typical spread of the true effects; tau-squared = {_num(tau2)}{t2ci}).")
        i2, il, ih = _value(a["I2"]), _value(a["I2_low"]), _value(a["I2_high"])
        i2ci = "" if math.isnan(il) else f" (95 % CI {_pct(il)[:-2]} to {_pct(ih)})"
        if not math.isnan(i2):
            print(f"{indent}I-squared = {_pct(i2)}{i2ci}: the share of the spread in the study results that is beyond "
                  "chance; it says how much of the spread is real, not how big it is.")
        q, qdf, qp = _value(a["Q"]), _value(a["Q_df"]), _value(a["Q_p"])
        if k >= 2 and not math.isnan(q):
            print(indent + _p_meta(qp, if_none="every study truly measured the same effect",
                                   this="differences between the studies this big or bigger",
                                   not_shown="that the studies measured the same effect",
                                   shown=f"Q = {_num(q)}, {_df(qdf)}, {_p_short(qp)}"))
        if info["random"] and 2 <= k < FEW_STUDIES and subgroup is None:
            print(f"{indent}Note: with {k} studies the between-study spread is hard to estimate.")
        row.update({"tau": tau, "tau squared": tau2, "I squared %": i2, "Q": q, "Q degrees of freedom": qdf,
                    "Q p-value": qp})
        return rows

    def _meta_subgroups(self, out, info):
        between = out["between"]
        q, df, p = _value(between["Q"]), _value(between["df"]), _value(between["p"])
        g = info["for_each"]
        print(f'Test of subgroup difference (each "{g}" group with its own between-study spread):')
        print("  " + _p_meta(p, if_none=f'the "{g}" groups truly had the same average effect',
                             this="differences between the groups this big or bigger",
                             not_shown="that the groups have the same effect",
                             shown=f"Q = {_num(q)}, {_df(df)}, {_p_short(p)}"))
        print("  Compare the groups with this test, not by which group's own interval leaves out "
              f"{1 if info['ratio'] else 0} (Sun et al. 2010).")
        rows = [{"study": f'difference between the "{g}" groups', "row kind": "subgroup difference", "subgroup": "all",
                 "measure": "Q test", "Q": q, "Q degrees of freedom": df, "p-value": p}]
        for level in info["levels"]:
            a = out["groups"][level]
            rows += self._meta_combined(a, info, int(_value(a["k"])), label=level, indent="  ", subgroup=level)
            if 1 < int(_value(a["k"])) < FEW_STUDIES and info["random"]:
                print(f'  Note: "{level}" has {int(_value(a["k"]))} studies, so its between-study spread is guessed from '
                      "almost nothing.")
        return rows

    def _meta_regression(self, m, info):
        names = ["intercept"] + info["mods_names"]
        b, lo, hi, p = (_floats(m[x]) for x in ("beta", "low", "high", "p"))
        sb, sl, sh = (_floats(m[x]) for x in ("shown", "shown_low", "shown_high"))
        k = int(_value(m["k"]))
        words = info["words"]
        scale_word = {"exp": f"log {words}", "ztor": "Fisher's z"}.get(info["transform"], words)
        print(f"Meta-regression of the {scale_word} on {_list_words(chr(34) + n + chr(34) for n in info['mods_names'])} "
              f"({k} studies):")
        rows = []
        for j, name in enumerate(names):
            if j == 0:
                continue
            change = f'  per 1 more "{name}", the {scale_word} changes by {_num(b[j])} (95 % CI {_num(lo[j])} to {_num(hi[j])})'
            if info["transform"] == "exp":
                change += f": the {words} is multiplied by {_num(sb[j])} (95 % CI {_num(sl[j])} to {_num(sh[j])})"
            print(change + ".")
            print("  " + _p_meta(p[j], if_none=f'"{name}" were truly unrelated to the effect',
                                 this="a link this strong or stronger", not_shown=f'that "{name}" is unrelated to the effect'))
        for j, name in enumerate(names):
            rows.append({"study": name if j == 0 else f'per 1 more "{name}"', "row kind": "meta-regression",
                         "measure": f"change in {scale_word}" if j else scale_word, "estimate": float(b[j]),
                         "estimate 95 % CI low": float(lo[j]), "estimate 95 % CI high": float(hi[j]),
                         "p-value": float(p[j])})
        r2 = _value(m["R2"])
        if not math.isnan(r2):
            print(f"  {_list_words(chr(34) + n + chr(34) for n in info['mods_names'])} "
                  f"{'accounts' if len(info['mods_names']) == 1 else 'account'} for {_pct(r2)} of the between-study "
                  f"spread (R-squared); the spread left: tau-squared = {_num(_value(m['tau2']))}.")
        print("  Note: a link between studies, not within them (ecological): studies at a higher value differ in many "
              "ways, so this does not show what happens to one person or place when the value changes.")
        if k < SMALL_STUDIES * len(info["mods_names"]):
            print(f"  Note: {k} studies for {len(info['mods_names'])} "
                  f"column{'s' if len(info['mods_names']) > 1 else ''}; with fewer than 10 studies per column a "
                  "meta-regression easily finds links that are chance (Thompson & Higgins 2002).")
        return rows

    def _meta_small_studies(self, out, info, used):
        if used < SMALL_STUDIES:
            print("Small-study effects: too few studies (under 10) to judge them (Sterne et al. 2011).")
            return []
        e = out.get("egger")
        if e is None:
            return []
        info["small_ran"] = True
        info["trimfill_ran"] = out.get("trimfill") is not None
        test = "Peters' test, for risk and odds ratios from counts" if info["peters"] else "Egger's regression test"
        print(f"Small-study effects ({test}): "
              + _p_meta(_value(e["p"]), if_none="small and large studies truly showed the same effect",
                        this="a link between study size and effect this strong or stronger",
                        not_shown="that there are no small-study effects",
                        shown=f"t = {_num(_value(e['stat']))}, {_df(_value(e['df']))}, "
                              f"{_p_short(_value(e['p']))}")
              + " Small-study effects are not proof of publication bias: they can also come from real differences "
                "between small and large studies, or from chance, and this test does not say which.")
        rows = [{"study": test, "row kind": "small-study effects", "measure": "t statistic",
                 "estimate": _value(e["stat"]), "p-value": _value(e["p"])}]
        t = out.get("trimfill")
        if t is None:
            print("Trim and fill needs an inverse-variance model (the default test_method=\"reml\"), so it is left out with "
                  f'test_method="{info["method_name"]}".')
            return rows
        k0 = int(_value(t["k0"]))
        side = str(np.atleast_1d(t["side"])[0])
        caution = (" With this much difference between studies (I-squared above 50 %), trim and fill is a rough guess."
                   if _value(out["all"]["I2"]) > 50 else "")
        if k0 == 0:
            print("Trim and fill (a what-if, not a correction): no study seems to be missing." + caution)
        else:
            print(f"Trim and fill (a what-if, not a correction): {k0} {'study' if k0 == 1 else 'studies'} might be "
                  f"missing on the {side}; with {'it' if k0 == 1 else 'them'} the combined {info['words']} would be "
                  f"{_num(_value(t['est']))} (95 % CI {_num(_value(t['low']))} to {_num(_value(t['high']))}, "
                  f"{'normal interval, as metafor trimfill() refits' if str(np.atleast_1d(t.get('test', ['z']))[0]) == 'z' else 'Hartung-Knapp'})."
                  + caution)
        rows.append({"study": "trim and fill (a what-if)", "row kind": "trim and fill", "measure": info["words"],
                     "estimate": _value(t["est"]), "estimate 95 % CI low": _value(t["low"]),
                     "estimate 95 % CI high": _value(t["high"]), "studies added": float(k0)})
        return rows

    @staticmethod
    def _meta_method_line(info):
        route, measure, cols = info["route"], info["measure"], info["cols"]
        calls = {"counts": f'metafor::escalc(measure = "{"PETO" if info["method_name"] == "peto" else measure}", ai, n1i, ci, n2i' + (")" if measure == "RD" else
                                                                                       ", drop00 = TRUE)"),
                 "rates": 'metafor::escalc(measure = "IRR", x1i, t1i, x2i, t2i, drop00 = TRUE)',
                 "averages": f'metafor::escalc(measure = "{measure}", m1i, sd1i, n1i, m2i, sd2i, n2i)',
                 "intervals": "metafor::conv.wald(out, ci.lb, ci.ub, level = " + f"{cols.get('level', 95):g}"
                              + (", transf = log)" if info["ratio"] else ")"),
                 "errors": 'metafor::escalc(measure = "GEN", yi' + (" = log(estimate)" if info["ratio"] else "")
                           + ", sei)",
                 "correlations": 'metafor::escalc(measure = "ZCOR", ri, ni)'}
        method = METHODS[info["method_name"]][0]
        if method == "MH":
            fit = f'metafor::rma.mh(measure = "{measure}")'
        elif method == "PETO":
            fit = "metafor::rma.peto()"
        else:
            mods = (", mods = ~ " + " + ".join(info["mods_names"])) if info["mods_names"] else ""
            fit = f'metafor::rma(yi, vi{mods}, method = "{method}", test = "{info["test"]}")'
        extra = ""
        if info["for_each"] is not None:
            extra = ("; each subgroup its own rma(), and the test of their difference rma(estimates, sei, mods = ~ group, "
                     'method = "EE")')
        if info["interval_name"] == "Hartung-Knapp":
            extra += ('; Hartung-Knapp (for the interval and the p-value) with the ad hoc rule, so it is never narrower '
                      "than the normal interval")
        elif info["random"]:
            extra += "; the normal (z) interval, as in older meta-analyses"
        if info["mods_names"]:
            after = "; the slopes, their intervals and R-squared from the fit"
        elif info["random"]:
            after = ("; predict() for the combined effect and the prediction interval, confint() for the intervals of "
                     "tau-squared and I-squared")
        else:
            after = "; predict() for the combined effect"
        if METHODS[info["method_name"]][0] in ("MH", "PETO"):
            calls[route] = calls[route] + " for each study's own effect"
        small = ""
        if info.get("small_ran"):
            small = ("; small-study effects by metafor::regtest(model = \"lm\", predictor = "
                     + ("\"ninv\") with Peters' weights" if info["peters"] else "\"sei\")")
                     + (" and metafor::trimfill()" if info.get("trimfill_ran") else ""))
        return f"Method: R {calls[route]}, then {fit}{after}{extra}{small}."


def _a(words: str) -> str:
    """ "a risk ratio", "an odds ratio"."""
    return ("an " if words[:1].lower() in "aeiou" else "a ") + words


def _df(df) -> str:
    return "1 degree of freedom" if int(df) == 1 else f"{int(df)} degrees of freedom"


def _plural(words: str) -> str:
    return PLURALS.get(words, words + "s")


def _p_short(p) -> str:
    from .summaries import _p_shown

    return _p_shown(p)
