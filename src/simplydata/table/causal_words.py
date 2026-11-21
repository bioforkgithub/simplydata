"""Cause and effect from observational data (phase S3d-2): compare_balanced_groups_of.

table.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=["age", "educ", "race"]) makes two
groups alike in the columns of allowing_for= (by weighting or by matching on the propensity score, the chance of
being in a group given those columns), shows how alike they became (the balance table), and then compares the
outcome. Every number comes from R WeightIt, MatchIt and cobalt (table/causal_r.py has the calls). simplydata checks
the columns, counts the rows outside the overlap of the scores, words the answer and always prints what the answer
rests on.
"""

from __future__ import annotations

import re

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, friendly
from .stat_tests import _label, _list_words
from .summaries import _p_sentence

METHODS = ("weighting", "matching")
SHOW = ("balance", "propensity scores")
GUIDE = 0.1  # the usual guide for a standardised difference (Austin 2009)
BIG_WEIGHT = 20  # a weight above this gets a note (extreme weights)
EXAMPLE = ('table.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=["age", "educ", "race", '
           '"married", "nodegree", "re74", "re75"])   (with sdata.get_example("job_training"))')
ASSUMPTIONS = ("This is the effect of {g} only if nothing that was not measured affects both {g} and {y} (the columns "
               "of allowing_for= are all that matter), every row could have been in either group (the scores "
               "overlap), and the propensity model is right. Balancing cannot make up for a column that was not "
               "measured.")


def _num(x) -> str:
    from .risk_words import _num as num

    return num(x)


def _read_choice(step, option, value, choices, spellings=None):
    text = value.strip().lower() if isinstance(value, str) else value
    text = (spellings or {}).get(text, text)
    if text not in choices:
        quoted = [f'"{c}"' for c in choices]
        raise SimplydataError(f"{option}= takes {', '.join(quoted[:-1])} or {quoted[-1]}.\n"
                              f"For example, {EXAMPLE}")
    return text


class CausalWords:
    # ------------------------------------------------------------------ compare_balanced_groups_of
    @friendly(renamed={"method": "test_method", "for_each": "for_each_group_in", "caliper": "match_within", "estimand": "effect_for"})
    def compare_balanced_groups_of(self, column=None, for_each_group_in=None, allowing_for=None, test_method="weighting",
                                   effect_for=None, against=None, match_within=None, show=None, interval=95):
        """Make two groups alike in other columns, then compare them (propensity scores, weighting, matching).

        table.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=["age", "educ", "race",
        "married", "nodegree", "re74", "re75"])   (with sdata.get_example("job_training"))
        In observational data the groups often differ before anything happens (older, sicker ...). This word
        first models each row's chance of being in a group from the columns of allowing_for= (the propensity
        score, R glm), then makes the groups alike in those columns and compares the column:
        test_method="weighting" (the default) weights each row by its score (R WeightIt::weightit() and
        lm_weightit(), whose standard errors allow for the estimated weights); test_method="matching" pairs each row
        of one group with the row of the other group with the nearest score (R MatchIt::matchit(), 1:1
        nearest neighbour), with match_within=0.2 leaving out pairs further apart than 0.2 standard deviations
        of the logit of the score (Austin 2011). effect_for="everyone" (the default for weighting): the effect
        if everyone were in one group rather than the other (ATE); effect_for="<a group>" (needed for
        matching): the effect among the rows of that group (ATT). against= is the group compared with (default:
        the first in sorted order; with effect_for= a group, the other group).
        Prints the overlap of the scores, the balance table (standardised differences of each column before
        and after, R cobalt::bal.tab(); the guide is 0.1), the effect with its interval and p-value, and the
        assumptions it rests on. Gives back the effect row; show="balance" gives the balance table and
        show="propensity scores" the table with a column "propensity score". A yes or no column gives the
        difference in the chance of yes (a risk difference).
        """
        step = "compare_balanced_groups_of"
        from .risk_words import _event_value, _level, _rows_table

        level = _level(step, interval, EXAMPLE)
        test_method = _read_choice(step, "test_method", test_method, METHODS, {"weights": "weighting", "ipw": "weighting",
                                                                 "iptw": "weighting", "match": "matching"})
        shown = None if show is None else _read_choice(step, "show", show, SHOW, {"propensity score": "propensity scores",
                                                                                   "balance table": "balance"})
        for option, value in (("the column", column), ("for_each_group_in=", for_each_group_in)):
            self._need_name(step, option, value, EXAMPLE)
        allowing = [allowing_for] if isinstance(allowing_for, str) else list(allowing_for or [])
        if not allowing or not all(isinstance(a, str) for a in allowing):
            raise SimplydataError(f"{step}() needs allowing_for= with the columns to make the groups alike in (those "
                                  f"that affect both the group and the outcome).\nFor example, {EXAMPLE}")
        names = [column, for_each_group_in] + allowing
        if len(set(names)) != len(names):
            raise SimplydataError(f"{step}() needs different columns for the outcome, for_each_group_in= and "
                                  f"allowing_for=.\nFor example, {EXAMPLE}")
        if match_within is not None:
            if test_method != "matching":
                raise SimplydataError('match_within= is the caliper of matching; add test_method="matching".')
            if isinstance(match_within, bool) or not isinstance(match_within, (int, float)) or match_within <= 0:
                raise SimplydataError("match_within= is a number of standard deviations of the logit of the "
                                      "propensity score, such as match_within=0.2 (Austin 2011).")
        self._need_columns(*names)
        kept = self._two_columns_frame(step, names, EXAMPLE)
        groups_raw = kept[for_each_group_in].to_list()
        groups = sorted(set(groups_raw), key=lambda v: (str(type(v)), v))
        if len(groups) != 2:
            raise SimplydataError(f'{step}() compares two groups at a time; "{for_each_group_in}" has {len(groups)}. '
                                  "Keep two groups first, for example with table.keep_rows_where(...).")
        labels = [_label(g) for g in groups]

        def find(value, option):
            for g, lab in zip(groups, labels):
                if value == g or str(value) == lab:
                    return g
            raise SimplydataError(f'{option}="{value}" is not one of the groups in "{for_each_group_in}" '
                                  f"({_list_words(chr(34) + lab + chr(34) for lab in labels)}).")

        if effect_for is None:
            if test_method == "matching":
                raise SimplydataError(
                    "Matching pairs each row of one group with a row of the other, so it gives the effect among the "
                    f"rows of that group: say which with effect_for=, such as effect_for=\"{labels[1]}\". For the "
                    'effect for everyone, use test_method="weighting".\nFor example, '
                    f'table.{step}("{column}", for_each_group_in="{for_each_group_in}", allowing_for={allowing!r}, '
                    f'test_method="matching", effect_for="{labels[1]}")')
            effect = "everyone"
        elif isinstance(effect_for, str) and effect_for.strip().lower() in ("everyone", "all", "ate"):
            if test_method == "matching":
                raise SimplydataError('Nearest-neighbour matching gives the effect among one group\'s rows, not for '
                                      f'everyone: use test_method="weighting", or effect_for="{labels[1]}".')
            effect = "everyone"
        else:
            effect = find(effect_for, "effect_for")
        if effect != "everyone":
            focal = effect
            ref = next(g for g in groups if g is not focal and str(g) != str(focal))
            if against is not None and find(against, "against") == focal:
                raise SimplydataError(f'against= is the group compared with, so it cannot be the effect_for= group '
                                      f'("{_label(focal)}").')
        else:
            ref = groups[0] if against is None else find(against, "against")
            focal = next(g for g in groups if g is not ref and str(g) != str(ref))
            if against is None:
                print(f'Note: "{_label(focal)}" compared against "{_label(ref)}" (the first in sorted order, as R); '
                      "choose another with against=.")
        t = np.array([1.0 if (g == focal or str(g) == str(focal)) else 0.0 for g in groups_raw])
        values = kept[column].to_list()
        yes_words = None
        if self._frame.schema[column].is_numeric() and not set(values) <= {0, 1}:
            y = np.asarray(values, dtype=float)
        else:
            if len(set(values)) != 2:
                raise SimplydataError(f'{step}() needs numbers in "{column}", or two values (yes or no).')
            event, yes_words = _event_value(step, column, values, None, what="yes")
            yes_words = yes_words.replace("; choose with positive=", "")
            y = np.array([1.0 if v == event else 0.0 for v in values])
        columns, shown_names = {}, {}
        for i, name in enumerate(allowing):
            key = f"x{i + 1}"
            shown_names[key] = name
            if self._frame.schema[name].is_numeric():
                columns[key] = np.asarray(kept[name].to_list(), dtype=float)
            else:
                columns[key] = np.array([_label(v) for v in kept[name].to_list()], dtype=object)
        n_focal, n_ref = int(t.sum()), int(len(t) - t.sum())
        if min(n_focal, n_ref) < 5 or len(t) < len(allowing) + 10:
            raise SimplydataError(f"{step}() needs more rows: {n_focal} in {_label(focal)} and {n_ref} in "
                                  f"{_label(ref)}, for {len(allowing)} columns to make alike.")
        from .causal_r import balance

        found = balance(test_method, effect, y, t, columns, level, match_within)
        ps = found["ps"]
        if shown == "propensity scores":
            return self._with_scores(kept, names, ps)
        # ---- 1. the propensity model, 2. overlap
        print(f'Groups made alike in {_list_words(allowing)} ({test_method}), then compared: "{column}" in '
              f'"{_label(focal)}" against "{_label(ref)}" ({len(t)} rows: {n_focal} and {n_ref}).')
        print(f"Propensity score: each row's chance of being in \"{_label(focal)}\" given {_list_words(allowing)}, "
              f"from logistic regression (R glm(family = binomial)).")
        in_f, in_r = ps[t == 1], ps[t == 0]
        outside_f = int(((in_f < in_r.min()) | (in_f > in_r.max())).sum())
        outside_r = int(((in_r < in_f.min()) | (in_r > in_f.max())).sum())
        print(f"Overlap: the scores run from {_num(in_f.min())} to {_num(in_f.max())} in \"{_label(focal)}\" and from "
              f"{_num(in_r.min())} to {_num(in_r.max())} in \"{_label(ref)}\"; {outside_f} row"
              f"{'' if outside_f == 1 else 's'} of \"{_label(focal)}\" and {outside_r} of \"{_label(ref)}\" lie "
              "outside the other group's range" + (" (no row like them in the other group: their effect is guessed "
                                                   "from the model)." if outside_f + outside_r else "."))
        # ---- 3. the balance table
        rows_b = [self._balance_name(r, shown_names) for r in found["rows"]]
        width = max(len(r) for r in rows_b)
        print(f'Balance (standardised differences, positive: higher in "{_label(focal)}"; within 0.1 is the usual '
              "guide, Austin 2009):")
        print(f"  {'column':<{width}}  before  after")
        for name, before, after in zip(rows_b, found["before"], found["after"]):
            print(f"  {name:<{width}}  {before:6.3f}  {after:6.3f}")
        left = [n for n, a in zip(rows_b, found["after"]) if abs(a) > GUIDE]
        if shown == "balance":
            return _rows_table(lambda d: self._new_table(nw.from_dict(d, backend=self._frame.implementation)),
                               [{"column": n, "difference before": float(b), "difference after": float(a)}
                                for n, b, a in zip(rows_b, found["before"], found["after"])])
        if left:
            hint = (" try match_within=0.2, or add those columns' squares or groups"
                    if test_method == "matching" and match_within is None
                    else " try a smaller match_within=, or add those columns' squares or groups" if test_method == "matching"
                    else " add those columns' squares or groups to allowing_for=, or check the overlap")
            print(f"Note: {_list_words(left)} {'is' if len(left) == 1 else 'are'} still more than 0.1 apart after "
                  f"{test_method}: the groups are not fully alike, so the effect below may still mix in that difference;"
                  f"{hint}.")
        if test_method == "weighting":
            big = int((found["weights"] > BIG_WEIGHT).sum())
            if big:
                print(f"Note: {big} row{'' if big == 1 else 's'} {'has' if big == 1 else 'have'} a weight above "
                      f"{BIG_WEIGHT} (largest {_num(found['weights'].max())}): a few rows count for many, so the "
                      "answer rests on them. Check the overlap.")
        else:
            unmatched = found.get("unmatched")
            if unmatched is not None and unmatched.size == 2 and unmatched[1] > 0:
                n_left = int(unmatched[1])
                why = (f"no match within {_num(match_within)} standard deviations" if match_within is not None
                       else f'no partner left (\"{_label(ref)}\" has fewer rows)')
                print(f"Note: {n_left} row{'' if n_left == 1 else 's'} of \"{_label(focal)}\" had {why} and "
                      f"{'was' if n_left == 1 else 'were'} left out, so the effect is for the matched rows of that group "
                      "only.")
        # ---- 4. the effect
        who = ("everyone (the average effect, ATE)" if effect == "everyone"
               else f'those in "{_label(focal)}" (the effect among them, ATT)')
        thing = ("the chance of yes (a risk difference)" if yes_words else f'the average of "{column}"')
        est, low, high, p = (float(found[k][0]) for k in ("estimate", "low", "high", "p"))
        ci = f"{level:g} % CI"
        print(f"Effect for {who}: {thing} is {_num(est)} higher in \"{_label(focal)}\" than in \"{_label(ref)}\" "
              f"({ci} {_num(low)} to {_num(high)}), once the groups are made alike." if est >= 0 else
              f"Effect for {who}: {thing} is {_num(-est)} lower in \"{_label(focal)}\" than in \"{_label(ref)}\" "
              f"({ci} of how much lower: {_num(-high)} to {_num(-low)}), once the groups are made alike.")
        if yes_words:
            print(f'"{column}" is yes or no: {yes_words} counts as yes.')
        print(_p_sentence(p, if_none="the groups, once made alike, truly did not differ",
                          this="a difference this big or bigger"))
        # ---- 5. the assumptions and the method
        print(ASSUMPTIONS.format(g=f'"{for_each_group_in}"', y=f'"{column}"'))
        if test_method == "weighting":
            print(f"Method: inverse probability weighting (R WeightIt::weightit(method = \"glm\", estimand = "
                  f"\"{'ATE' if effect == 'everyone' else 'ATT'}\")), the effect from WeightIt::glm_weightit(family = gaussian), as lm_weightit(), with "
                  "standard errors that allow for the estimated weights (M-estimation, z test); balance from R "
                  "cobalt::bal.tab().")
        else:
            caliper = ("" if match_within is None else f", caliper {_num(match_within)} standard deviations of the "
                       "logit of the score (link = \"linear.logit\")")
            print(f"Method: 1:1 nearest-neighbour matching on the propensity score without replacement (R "
                  f"MatchIt::matchit(method = \"nearest\", distance = \"glm\"{caliper})), the effect from lm() on the "
                  "matched rows with standard errors clustered on the pairs (sandwich::vcovCL, t test), as the "
                  "MatchIt vignette does; balance from R cobalt::bal.tab().")
        row = {"term": f"{_label(focal)} against {_label(ref)}", "estimate": est,
               "standard error": float(found["se"][0]), f"estimate {ci} low": low, f"estimate {ci} high": high,
               "p-value": p, "effect for": "everyone (ATE)" if effect == "everyone" else f"{_label(focal)} (ATT)",
               "rows": len(t), "method": f"{test_method} on the propensity score (R {'WeightIt' if test_method == 'weighting' else 'MatchIt'})"}
        return _rows_table(lambda d: self._new_table(nw.from_dict(d, backend=self._frame.implementation)), [row])

    @staticmethod
    def _balance_name(row, shown_names):
        """cobalt's row name ("x3_black") in the table's own names ("race: black")."""
        found = re.match(r"^(x\d+)(?:_(.*))?$", row)
        if not found or found.group(1) not in shown_names:
            return row
        name = shown_names[found.group(1)]
        return f"{name}: {found.group(2)}" if found.group(2) else name

    def _with_scores(self, kept, names, ps):
        """show="propensity scores": the table's rows used, with a column "propensity score"."""
        frame = kept.with_columns(nw.new_series("propensity score", ps.tolist(), nw.Float64,
                                                backend=self._frame.implementation))
        print(f"The propensity score of each of the {len(ps)} rows used (rows with an empty cell in "
              f"{_list_words(names)} left out): the chance of being in the compared group given the columns of "
              "allowing_for=, from logistic regression (R glm(family = binomial)).")
        return self._new_table(frame)
