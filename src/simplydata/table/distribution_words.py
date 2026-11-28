"""Table words for distributions: fit_distribution_to, compare_distributions_for, and the shape_test engine.

The numbers come from simplydata.distributions (maximum likelihood, as R MASS::fitdistr and
fitdistrplus); see that module for every choice.
"""

from __future__ import annotations

from .._typing import _Same

import math

import narwhals as nw
import numpy as np

from .. import distributions as _d
from .._errors import SimplydataError, friendly
from .summaries import GROUPS_IN_SENTENCE, _key, _order, _say_label

DEFAULT_COMPARED = ("normal", "lognormal", "gamma", "weibull")
# compare_distributions_for(show=): families for 100 %, batches 3-4 (approved by Manish 2026-11-28); the distance
# between the values of each pair of groups (SciPy wasserstein_distance, wasserstein_distance_nd, energy_distance)
DISTANCE_SHOWS = ("wasserstein distance", "energy distance")
DISTANCE_SPELLINGS = {"wasserstein": "wasserstein distance", "earth mover's distance": "wasserstein distance",
                      "earth movers distance": "wasserstein distance", "wasserstein_distance": "wasserstein distance",
                      "wasserstein_distance_nd": "wasserstein distance", "energy": "energy distance",
                      "energy_distance": "energy distance"}


def shape_test(values, name, seed=_d.SEED, samples=_d.SHAPE_TEST_SAMPLES, column=None) -> dict:
    """compare_shape_to(column, shape) for any shape but "normal": see distributions.shape_test."""
    return _d.shape_test(values, name, seed=seed, samples=samples, column=column)


class DistributionTableWords:
    # ------------------------------------------------------------------ helpers
    def _distribution_groups(self, step, column, for_each, example):
        """(group column names, [(key, label, values)]) with empty cells skipped (with a note)."""
        if not isinstance(column, str):
            raise SimplydataError(f"{step}() needs the column as a name in quotes.\nFor example, {example}")
        groups = self._group_columns(step, for_each, [column]) if for_each is not None else []
        frame = self._number_frame(step, [column])
        values = frame.select(nw.col(column).cast(nw.Float64))[column].to_numpy().astype(float)
        keys = [_key(r) for r in frame.select(groups).rows()] if groups else [()] * len(values)
        by_group: dict = {}
        for key, v in zip(keys, values):
            by_group.setdefault(key, [])
            if not math.isnan(v):
                by_group[key].append(v)
        skipped = int(np.isnan(values).sum())
        if skipped:
            rows = "row" if skipped == 1 else "rows"
            verb = "was" if skipped == 1 else "were"
            print(f'Note: {skipped} {rows} with an empty cell in "{column}" {verb} skipped.')
        order = sorted(by_group, key=lambda k: tuple(_order(v) for v in k))
        out = [(key, " / ".join(_say_label(x) for x in key), np.asarray(by_group[key], dtype=float)) for key in order]
        return groups, out

    def _distribution_rows_table(self, rows):
        columns = list(rows[0])
        data = {c: [r.get(c) for r in rows] for c in columns}
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    # ------------------------------------------------------------------ fit_distribution_to
    @friendly(renamed={"for_each": "for_each_group_in"}, others={"censored": "censored_by",
                                                                 "right_censored": "censored_by"})
    def fit_distribution_to(self, column=None, distribution="normal", for_each_group_in=None, fixed=None,
                            censored_by=None):
        """Fit a distribution to a column by maximum likelihood; gives back the fitted distribution.

        fit = table.fit_distribution_to("sales", "lognormal")   (with sdata.get_example("shop"))
        then fit.find_chance_that_value(is_above=600), fit.find_percentile(90), fit.draw_chart(), and fit.turn_into_table() for the
        result table (values, standard errors, log-likelihood, AIC, BIC, rows). As R
        MASS::fitdistr(x, "gamma") (fitdistrplus::fitdist for beta and others); standard
        errors from the observed information. Families without a location in R (gamma,
        weibull, lognormal, exponential, beta) keep it at 0, as R. fixed={"shape": 2} holds a
        parameter. With for_each_group_in= it gives back a result table, one row per group.
        Empty cells are skipped.
        "kernel density" gives a smooth curve that follows the values, with no family chosen:
        SciPy gaussian_kde with Silverman's bandwidth (statsmodels bw_silverman), as R density(x).
        censored_by="still_alive" (families for 100 %) names a yes/no column that is yes for the rows whose value
        is only a lower limit (followed until then, the event not seen yet): the fit allows for them (SciPy
        CensoredData, as R fitdistrplus::fitdistcens(); a Weibull as R survival::survreg()).
          fit = table.fit_distribution_to("days", "weibull", censored_by="still_alive")
        """
        step = "fit_distribution_to"
        example = 'with sdata.get_example("trial"): table.fit_distribution_to("days", "gamma")'
        if censored_by is not None:
            return self._fit_censored(step, column, distribution, for_each_group_in, fixed, censored_by)
        if for_each_group_in is not None and _d._is_kernel(distribution):
            raise SimplydataError('A kernel density is made for one group at a time: keep its rows first, then '
                                  'table.fit_distribution_to("marks", "kernel density").')
        groups, parts = self._distribution_groups(step, column, for_each_group_in, example)
        backend = self._frame.implementation
        if not groups:
            values = parts[0][2] if parts else np.asarray([])
            return _d.fit(values, distribution, fixed=fixed, say=True, column=column, backend=backend)
        rows, lines, fits = [], [], []
        for key, label, values in parts:
            dist = _d.fit(values, distribution, fixed=fixed, column=column, backend=backend)
            fits.append(dist)
            info = dist._fit_info
            row = {g: k for g, k in zip(groups, key)}
            row.update({"distribution": dist.name, "column": column, **info["row"]})
            rows.append(row)
            lines.append(f"  {label} ({info['rows']} values): {_d._fit_parts(dist)}; log-likelihood "
                         f"{info['log-likelihood']:.1f}, AIC {info['AIC']:.1f}")
        names = " and ".join(f'"{g}"' for g in groups)
        family = fits[0]._family
        title = (family.title if isinstance(family, _d.Family) else f"{family.plain} (SciPy {family})"
                 if getattr(family, "plain", None) else f"SciPy {fits[0].name}")
        article = "an" if title[0].lower() in "aeiou" else "a"
        print(f'Fitted {article} {title} distribution to "{column}" for each {names}:')
        for line in lines[:GROUPS_IN_SENTENCE]:
            print(line)
        if len(lines) > GROUPS_IN_SENTENCE:
            print(f"  ... and {len(lines) - GROUPS_IN_SENTENCE} more (the result table has them all)")
        print(f"Method: maximum likelihood, as {_d._r_fit_text(fits[0])}, for each group. For one group's "
              "distribution (to ask chances), keep its rows first and fit again.")
        if fits[0].name == "normal" and not fits[0]._fit_info["held"].get("standard_deviation"):
            print("Note: the maximum-likelihood standard deviation divides by n, so it is a little smaller than R sd().")
        return self._distribution_rows_table(rows)

    def _fit_censored(self, step, column, distribution, for_each, fixed, censored_by):
        from .more_tests import _yes_no

        example = 'table.fit_distribution_to("days", "weibull", censored_by="still_alive")'
        if for_each is not None:
            raise SimplydataError("censored_by= fits one group; keep its rows first, then fit.\n"
                                  f"For example:  {example}")
        for name, what in ((column, "the column"), (censored_by, "censored_by=")):
            if not isinstance(name, str):
                raise SimplydataError(f"{step}() needs {what} as a name in quotes.\nFor example:  {example}")
        if column == censored_by:
            raise SimplydataError("censored_by= is another column: the yes/no column that says which values are "
                                  "censored.")
        self._need_columns(column, censored_by)
        frame = self._number_frame(step, [column]).drop_nulls(subset=[column, censored_by])
        skipped = len(self._frame) - len(frame)
        if skipped:
            print(f"Note: {skipped} row{'' if skipped == 1 else 's'} with an empty cell in \"{column}\" or "
                  f"\"{censored_by}\" {'was' if skipped == 1 else 'were'} skipped.")
        values = frame[column].cast(nw.Float64).to_numpy().astype(float)
        flags = frame[censored_by].to_list()
        distinct = set(flags)
        if distinct <= {True, False}:
            censored = np.asarray(flags, dtype=bool)
        elif distinct <= {0, 1}:
            censored = np.asarray(flags, dtype=float) == 1
        elif len(distinct) == 2:
            yes, marks, words = _yes_no(censored_by, flags)
            censored = marks == 1
            print(f'Censored rows: those where "{censored_by}" is {words}.')
        else:
            raise SimplydataError(f'censored_by= needs a yes/no column (True/False, 1/0 or two values such as "yes" '
                                  f'and "no"); "{censored_by}" has {len(distinct)} different values.')
        return _d.fit_censored(values, censored, distribution, fixed=fixed, say=True, column=column,
                               backend=self._frame.implementation, censored_by=censored_by)

    # ------------------------------------------------------------------ compare_distributions_for(show=)
    def _distances_between_groups(self, step, column, for_each, show, distributions):
        from scipy import stats

        example = 'table.compare_distributions_for("marks", for_each_group_in="class", show="wasserstein distance")'
        shown = show.strip().lower() if isinstance(show, str) else show
        shown = DISTANCE_SPELLINGS.get(shown, shown)
        self._check_choice(step, "show", shown, DISTANCE_SHOWS)
        if distributions is not DEFAULT_COMPARED and tuple(distributions) != DEFAULT_COMPARED:
            raise SimplydataError(f'show="{shown}" compares the groups\' own values, with no distribution fitted; '
                                  "leave out distributions=.")
        if for_each is None:
            raise SimplydataError(f'show="{shown}" compares groups, so it needs for_each_group_in=.\n'
                                  f"For example:  {example}")
        columns = [column] if isinstance(column, str) else list(column) if isinstance(column, (list, tuple)) else None
        if not columns or not all(isinstance(c, str) for c in columns):
            raise SimplydataError(f"{step}() needs the column (or a list of columns) in quotes.\nFor example:  "
                                  f"{example}")
        if len(columns) > 1 and shown == "energy distance":
            raise SimplydataError('show="energy distance" compares one column; "wasserstein distance" takes a list.')
        groups = self._group_columns(step, for_each, columns)
        frame = self._number_frame(step, columns).drop_nulls(subset=columns)
        skipped = len(self._frame) - len(frame)
        if skipped:
            print(f"Note: {skipped} row{'' if skipped == 1 else 's'} with an empty cell "
                  f"{'was' if skipped == 1 else 'were'} skipped.")
        values = np.column_stack([frame[c].cast(nw.Float64).to_numpy().astype(float) for c in columns])
        keys = [_key(r) for r in frame.select(groups).rows()]
        order = sorted(set(keys), key=lambda k: tuple(_order(v) for v in k))
        if len(order) < 2:
            raise SimplydataError(f'{step}() needs at least 2 groups in {", ".join(groups)}.')
        parts = {k: values[[i for i, key in enumerate(keys) if key == k]] for k in order}
        rows, lines = [], []
        for i, first in enumerate(order):
            for second in order[i + 1:]:
                a, b = parts[first], parts[second]
                if shown == "energy distance":
                    distance = float(stats.energy_distance(a[:, 0], b[:, 0]))
                elif len(columns) == 1:
                    distance = float(stats.wasserstein_distance(a[:, 0], b[:, 0]))
                else:
                    distance = float(stats.wasserstein_distance_nd(a, b))
                label_a = " / ".join(_say_label(x) for x in first)
                label_b = " / ".join(_say_label(x) for x in second)
                rows.append({"first group": label_a, "second group": label_b, shown: distance,
                             "count in first": len(a), "count in second": len(b)})
                lines.append(f"  {label_a} and {label_b}: {distance:.4g}")
        names = " and ".join(f'"{c}"' for c in columns)
        print(f"The {shown} between the values of {names} of each pair of {', '.join(groups)}:")
        for line in lines[:GROUPS_IN_SENTENCE * 2]:
            print(line)
        if len(lines) > GROUPS_IN_SENTENCE * 2:
            print("  ... (the result table has every pair)")
        how = {"energy distance": ("SciPy energy_distance (Szekely's energy distance: the square root of "
                                   "2E|X - Y| - E|X - X'| - E|Y - Y'|)"),
               "wasserstein distance": ("SciPy wasserstein_distance, the area between the groups' cumulative shares, "
                                        "as R transport::wasserstein1d()") if len(columns) == 1 else
               "SciPy wasserstein_distance_nd, the cheapest way to move one group's points onto the other's"}[shown]
        print(f"Method: {how}. 0 means the same values; bigger means further apart, in the units of the values.")
        return self._distribution_rows_table(rows)

    # ------------------------------------------------------------------ compare_distributions_for
    @friendly(renamed={"for_each": "for_each_group_in", "between": "for_each_group_in"})
    def compare_distributions_for(self: _Same, column=None, distributions=DEFAULT_COMPARED, for_each_group_in=None,
                                  show=None) -> _Same:
        """Fit several distributions to a column and rank them by AIC (smaller is better).

        table.compare_distributions_for("sales")   (with sdata.get_example("shop"))
        distributions=("normal", "lognormal", "gamma", "weibull") by default. Each is fitted by
        maximum likelihood (as fit_distribution_to); the result table has one row per
        distribution with its values, log-likelihood, AIC, BIC, the AIC difference from the
        best, and the Anderson-Darling, Kolmogorov-Smirnov and Cramer-von Mises statistics, as
        R fitdistrplus::gofstat(). An AIC difference below 2 is too small to choose between them.
        show="wasserstein distance" (families for 100 %) compares the groups' own values instead, with no
        distribution fitted: the distance between the values of each pair of for_each_group_in= groups, how much
        of the values must move how far to turn one group into the other (in the column's units; SciPy
        wasserstein_distance, or wasserstein_distance_nd for a list of columns). show="energy distance" gives the
        energy distance (SciPy energy_distance). One row per pair of groups.
          table.compare_distributions_for("marks", for_each_group_in="class", show="wasserstein distance")
        """
        step = "compare_distributions_for"
        if show is not None:
            return self._distances_between_groups(step, column, for_each_group_in, show, distributions)
        example = 'with sdata.get_example("trial"): table.compare_distributions_for("days")'
        if isinstance(distributions, str):
            distributions = [distributions]
        groups, parts = self._distribution_groups(step, column, for_each_group_in, example)
        rows, sentences = [], []
        for key, label, values in parts:
            ranked, notes = _d.compare_fits(values, distributions, column=column)
            for note in notes:
                sentences.append(note if not groups else f"  {label}: {note}")
            sentence = _d._ranking_sentence(ranked)
            sentences.append(sentence if not groups else f"  {label} ({len(values)} values): {sentence}")
            for r in ranked:
                row = {g: k for g, k in zip(groups, key)}
                row.update({c: r[c] for c in _d.COMPARE_COLUMNS})
                rows.append(row)
        if groups:
            names = " and ".join(f'"{g}"' for g in groups)
            print(f'Distributions of "{column}" ranked by AIC for each {names} (smaller is better):')
            shown = [s for s in sentences]
            for line in shown[:GROUPS_IN_SENTENCE * 2]:
                print(line)
            if len(parts) > GROUPS_IN_SENTENCE:
                print("  ... (the result table has every group)")
        else:
            for line in sentences:
                print(line)
        print("A difference below 2 is too small to choose between them. Method: maximum likelihood for each, "
              "ranked by AIC, as R fitdistrplus::gofstat().")
        return self._distribution_rows_table(rows)
