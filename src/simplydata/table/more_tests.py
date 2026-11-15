"""More tests in plain words: matched measurements, whole shapes, and random order.

Like stat_tests.py, these words never change the table: they print the answer in words, with
the test used and why, and give back a one-row result table. Every number comes from SciPy,
statsmodels or R (through simplydata[r]); simplydata only checks the input and words the answer.

* compare_matched("week_0", "week_4", "week_8"): the same rows measured three or more times.
  Numbers: the Friedman test (R friedman.test(), SciPy friedmanchisquare), with Kendall's W from
  R effectsize::kendalls_w (its interval is a bootstrap interval, R seed 1); test="quade": the
  Quade test, run in R (stats::quade.test(); Python has none). Yes/no columns: Cochran's Q
  (statsmodels cochrans_q, as R DescTools::CochranQTest()). The kind of column decides, and the
  sentence says so. With two columns it is compare_before_after (one door, printed).
* compare_shapes("marks", for_each="class"): do the groups differ in their whole shape (where
  the values lie and how they spread), not only in their average? Two groups: the two-sample
  Kolmogorov-Smirnov test (SciPy ks_2samp, exact as R ks.test(); with tied values R's exact
  p-value, which SciPy does not give, comes from R). Three or more: the Anderson-Darling
  k-sample test (SciPy anderson_ksamp, the midrank version for ties, as R kSamples::ad.test()
  version 2), with a p-value from shuffling the group labels (shuffles=9999, seed=1).
* check_random_order("marks"): the runs test. Each value is above or below the median; a
  random order gives a usual number of runs (unbroken stretches on one side). Values equal to
  the median are left out, as R randtests::runs.test() does (printed); then statsmodels
  runstest_1samp(correction=False) gives R's numbers.
"""

from __future__ import annotations

import math
import warnings

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, friendly
from .models import YES_NO_PAIRS, _sort_key
from .stat_tests import ALIKE, _label, _list_words, _num, _skipped_note, _whole
from .summaries import _p_sentence, _say_label

MATCHED_TESTS = ("friedman", "quade", "cochran", "page")
MATCHED_ALIASES = {"cochran's q": "cochran", "cochran q": "cochran", "cochrans q": "cochran",
                   "friedman test": "friedman", "quade test": "quade"}
SHUFFLES = 9999  # compare_shapes, 3 or more groups: the group labels are shuffled this often


def _yes_no(column, values):
    """(yes value, 0/1 array, words saying which value is yes) for a column with 2 different values."""
    distinct = sorted(set(values), key=_sort_key)
    lowered = {str(v).strip().lower(): v for v in distinct}
    for word, other in YES_NO_PAIRS:
        if set(lowered) == {word, other}:
            yes = lowered[word]
            return yes, np.array([v == yes for v in values], dtype=float), f'"{_label(yes)}"'
    yes = distinct[1]
    return (yes, np.array([v == yes for v in values], dtype=float),
            f'"{_label(yes)}" (the second value in sorted order, as R; "{_label(distinct[0])}" is the other)')


def _shares(values, at):
    """The share of the values at or below a value (display only: a count divided by n)."""
    return float(np.mean(np.asarray(values) <= at))


class MoreTestWords:
    # ------------------------------------------------------------------ compare_matched
    def _matched_columns(self, step, columns, example):
        names = []
        for value in columns:
            names.extend(value if isinstance(value, (list, tuple)) else [value])
        if not names:
            raise SimplydataError(f"{step}() needs the columns to compare, for example {example}.")
        for name in names:
            self._need_name(step, "each column", name, example)
        if len(set(names)) != len(names):
            raise SimplydataError(f"{step}() was given the same column twice; give each column once.\n"
                                  f"For example, {example}")
        self._need_columns(*names)
        return names

    @friendly
    def compare_matched(self, *columns, based_on="ranks", test=None):
        """Do three or more measurements of the same rows differ, such as pain at week 0, 4 and 8?

        table.compare_matched("Maths", "Science", "English")   (one column per measurement)
        Each row is one person (or plant, or field) measured in every column. The kind of
        column decides the test, and the sentence says which:
        numbers: the Friedman test (R friedman.test(), SciPy friedmanchisquare), which compares
        the ranks within each row, so it needs no bell shape; effect size Kendall's W (0: the
        rows rank the columns in no common order, 1: every row ranks them the same), from R
        effectsize::kendalls_w with a bootstrap 95 % interval (R seed 1). test="quade": the Quade
        test, which also weighs how much each row varies, run in R (stats::quade.test()).
        test="page": Page's test for a trend: do the values rise in the order the columns are
        given? (SciPy page_trend_test, as R crank::page.trend.test(); for a fall, give the columns
        the other way round.)
        yes/no columns (two values, such as "yes"/"no" or True/False): Cochran's Q test
        (statsmodels cochrans_q, as R DescTools::CochranQTest()).
        With two columns it gives compare_before_after (Wilcoxon signed-rank). Rows with an
        empty cell in any of the columns are skipped. based_on="averages" (the repeated-measures
        ANOVA) is not here yet. Gives back a one-row table.
        """
        step = "compare_matched"
        example = 'table.compare_matched("week_0", "week_4", "week_8")'
        names = self._matched_columns(step, columns, example)
        if based_on == "averages":
            raise SimplydataError(f"{step}() compares ranks for now (the Friedman test); the repeated-measures "
                                  "ANOVA on averages comes later.\nUse based_on=\"ranks\" (the default).")
        self._check_choice(step, "based_on", based_on, ("ranks",))
        if isinstance(test, str):
            test = MATCHED_ALIASES.get(test.strip().lower(), test.strip().lower())
        if test is not None:
            self._check_choice(step, "test", test, MATCHED_TESTS)
        if len(names) == 2:
            print(f'Note: with two columns, {step}() is compare_before_after("{names[0]}", "{names[1]}"), the '
                  "test for one measurement before and one after.")
            return self.compare_before_after(names[0], names[1], based_on="ranks")
        if len(names) < 2:
            raise SimplydataError(f"{step}() needs at least 2 columns (3 or more for a test of matched measurements).\n"
                                  f"For example, {example}")
        frame = self._frame
        floats = [c for c in names if frame.schema[c].is_float()]
        if floats:
            frame = frame.with_columns(nw.col(c).fill_nan(None) for c in floats)
        kept = frame.select(*names).drop_nulls()
        _skipped_note(len(frame) - len(kept), names)
        raw = {c: kept[c].to_list() for c in names}
        two_values = all(len(set(raw[c])) <= 2 for c in names) and len(set().union(*map(set, raw.values()))) == 2
        numeric = all(frame.schema[c].is_numeric() for c in names)
        if two_values and (not numeric or set().union(*map(set, raw.values())) <= {0, 1}):
            if test not in (None, "cochran"):
                raise SimplydataError(f'test="{test}" compares numbers, but the columns are yes/no; for yes/no '
                                      "columns the test is Cochran's Q (leave out test=).")
            return self._cochran(step, names, raw, len(kept))
        if not numeric:
            text = next(c for c in names if not frame.schema[c].is_numeric())
            raise SimplydataError(f'{step}() needs columns of numbers, or yes/no columns; "{text}" holds text with '
                                  "more than two different values.")
        if test == "cochran":
            raise SimplydataError("test=\"cochran\" is for yes/no columns; these columns hold numbers. Leave out test= "
                                  "for the Friedman test.")
        matrix = np.column_stack([np.asarray(raw[c], dtype=float) for c in names])
        if len(matrix) < 2:
            raise SimplydataError(f"{step}() needs at least 2 rows with a number in every column.")
        if test == "page":
            return self._page(names, matrix)
        return self._friedman(step, names, matrix, test or "friedman")

    def _page(self, names, matrix):
        from scipy import stats

        result = stats.page_trend_test(matrix)
        stat, p = float(result.statistic), float(result.pvalue)
        n, k = matrix.shape
        medians = [float(np.median(matrix[:, j])) for j in range(k)]
        listed = _list_words(f'{_num(m)} in "{c}"' for c, m in zip(names, medians))
        print(f"The median is {listed} ({n} rows, each measured {k} times, in this order).")
        print(_p_sentence(p, "the values truly did not rise along this order", "a rise this steady or steadier",
                          "that there is no rise"))
        print(f"Test: Page's test for a trend (L = {_whole(stat)}, {result.method}): it only looks for values that "
              "rise from the first column to the last; a fall would not count (give the columns the other way round "
              "for a fall). SciPy page_trend_test, as R crank::page.trend.test().")
        row = {"test": "Page's trend test", "what it compares": "a rise along " + _list_words(f'"{c}"' for c in names),
               "statistic name": "L", "statistic": stat, "p-value": p, "rows": n,
               "sides": "one-sided: values rise along the order given"}
        for c, m in zip(names, medians):
            row[f"median of {c}"] = m
        return self._result_table(row)

    def _friedman(self, step, names, matrix, test):
        from scipy import stats

        from .._r import RMissing, r_call

        n, k = matrix.shape
        medians = [float(np.median(matrix[:, j])) for j in range(k)]
        quoted = _list_words(f'"{c}"' for c in names)
        what = f"{quoted}, measured in the same {n} rows"
        row = {"test": None, "what it compares": what}
        if test == "friedman":
            result = stats.friedmanchisquare(*[matrix[:, j] for j in range(k)])
            stat, p = float(result.statistic), float(result.pvalue)
            row.update({"test": "Friedman test", "statistic name": "chi-square", "statistic": stat,
                        "degrees of freedom": float(k - 1), "p-value": p})
            second = (f"Test: Friedman test (chi-square = {_num(stat)}, df = {k - 1}), because the columns hold numbers "
                      "measured in the same rows; it compares the ranks within each row, so it does not need "
                      "bell-shaped values. As R friedman.test().")
        else:
            found = r_call("r <- stats::quade.test(y); list(f = unname(r$statistic), df = unname(r$parameter), "
                           "p = r$p.value)", packages=(), what="the Quade test (R stats::quade.test())",
                           python_note="Python has no Quade test; the Friedman test (leave out test=) needs no R",
                           y=matrix)
            stat, p = float(np.asarray(found["f"])[0]), float(np.asarray(found["p"])[0])
            df1, df2 = (float(v) for v in np.asarray(found["df"]))
            row.update({"test": "Quade test", "statistic name": "F", "statistic": stat, "degrees of freedom 1": df1,
                        "degrees of freedom 2": df2, "p-value": p})
            second = (f"Test: Quade test (F = {_num(stat)}, df = {_whole(df1)} and {_whole(df2)}), chosen with test=; "
                      "like Friedman's it ranks within each row, and it gives more weight to rows that vary more. "
                      "Run in R: stats::quade.test().")
        try:
            w = r_call("set.seed(1); es <- as.data.frame(effectsize::kendalls_w(y, ci = 0.95, alternative = "
                       '"two.sided")); list(value = es$Kendalls_W, low = es$CI_low, high = es$CI_high)',
                       packages=("effectsize",), what="Kendall's W with its 95 % interval (R effectsize)", y=matrix)
            w = {key: float(np.asarray(w[key])[0]) for key in ("value", "low", "high")}
            note = ""
        except RMissing:
            w = {"value": math.nan, "low": math.nan, "high": math.nan}
            from .effect_sizes import missing_note

            note = missing_note("Kendall's W")
        row.update({"effect size name": "how alike the rows rank the columns, 0 to 1 (Kendall's W)",
                    "effect size": w["value"], "effect size 95 % CI low": w["low"],
                    "effect size 95 % CI high": w["high"], "rows": n})
        for c, m in zip(names, medians):
            row[f"median of {c}"] = m
        listed = _list_words(f'{_num(m)} in "{c}"' for c, m in zip(names, medians))
        first = f"The median is {listed} ({n} rows, each measured {k} times)."
        if not note:
            first += (f" Kendall's W = {_num(w['value'])} (95 % bootstrap CI, R seed 1, {_num(w['low'])} to "
                      f"{_num(w['high'])}): how alike the rows rank the columns, from 0 (no common order) to 1 "
                      "(every row the same).")
        print(first)
        print(_p_sentence(p, "the columns truly did not differ", ALIKE[1], "that the columns are alike"))
        print(second)
        if note:
            print(note)
        return self._result_table(row)

    def _cochran(self, step, names, raw, n):
        from statsmodels.stats.contingency_tables import cochrans_q

        values = [v for c in names for v in raw[c]]
        yes, _, yes_words = _yes_no(names[0], values)
        matrix = np.column_stack([np.array([v == yes for v in raw[c]], dtype=float) for c in names])
        if n < 2:
            raise SimplydataError(f"{step}() needs at least 2 rows with a value in every column.")
        result = cochrans_q(matrix)
        stat, p, df = float(result.statistic), float(result.pvalue), int(result.df)
        k = len(names)
        shares = matrix.mean(axis=0)
        quoted = _list_words(f'"{c}"' for c in names)
        row = {"test": "Cochran's Q test", "what it compares": f"the share of {yes_words} in {quoted}, measured in "
               f"the same {n} rows",
               "statistic name": "Q", "statistic": stat, "degrees of freedom": float(df), "p-value": p, "rows": n}
        for c, s, count in zip(names, shares, matrix.sum(axis=0)):
            row[f"count of {_say_label(yes)} in {c}"] = int(count)
            row[f"percent {_say_label(yes)} in {c}"] = float(s) * 100
        listed = _list_words(f'{int(c)} of {n} in "{name}"' for name, c in zip(names, matrix.sum(axis=0)))
        print(f'"{_label(yes)}": {listed} (each row measured {k} times).')
        print(_p_sentence(p, "the columns truly did not differ", ALIKE[1], "that the columns are alike"))
        print(f"Test: Cochran's Q test (Q = {_num(stat)}, df = {df}), because the columns are yes/no "
              f"(counted as yes: {yes_words}); as R DescTools::CochranQTest().")
        return self._result_table(row)

    # ------------------------------------------------------------------ compare_shapes
    @friendly
    def compare_shapes(self, column=None, for_each=None, shuffles=SHUFFLES, seed=1):
        """Do the groups differ in the whole shape of their values, not only in the average?

        table.compare_shapes("marks", for_each="class")   (with sdata.example("marks"))
        Two groups: the two-sample Kolmogorov-Smirnov test, which looks for the biggest gap
        between the groups' cumulative shares (the share of values at or below each value);
        SciPy ks_2samp, exact as R ks.test(). With tied values R gives an exact p-value that
        SciPy does not, so that p-value comes from R (simplydata[r]).
        Three or more groups: the Anderson-Darling k-sample test (SciPy anderson_ksamp, the
        midrank version for ties, as R kSamples::ad.test() version 2), with its p-value from
        shuffling the group labels shuffles=9999 times (seed=1, printed; the same seed gives the
        same p-value). Empty cells are skipped. Gives back a one-row table.
        """
        step = "compare_shapes"
        example = 'table.compare_shapes("marks", for_each="class")'
        if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
            raise SimplydataError("seed= needs a whole number, such as seed=1 (the same seed gives the same p-value).")
        if isinstance(shuffles, bool) or not isinstance(shuffles, (int, np.integer)) or shuffles < 99:
            raise SimplydataError("shuffles= needs a whole number of 99 or more, such as shuffles=9999.")
        groups = self._groups(step, column, for_each, example)
        if len(groups) == 2:
            return self._ks_two(column, for_each, groups)
        return self._ad_many(column, for_each, groups, int(shuffles), int(seed))

    def _ks_two(self, column, for_each, groups):
        from scipy import stats

        (name_a, a), (name_b, b) = groups
        exact = len(a) * len(b) < 10000  # R ks.test(): exact below 10000 pairs
        result = stats.ks_2samp(a, b, method="exact" if exact else "asymp")
        d, at = float(result.statistic), float(result.statistic_location)
        ties = len(np.unique(np.concatenate([a, b]))) < len(a) + len(b)
        if ties and exact:
            from .._r import r_call

            p = float(np.asarray(r_call("ks.test(a, b)$p.value", packages=(),
                                        what="the exact Kolmogorov-Smirnov p-value with tied values (R ks.test())",
                                        python_note="SciPy ks_2samp gives a p-value that ignores the ties and so "
                                                    "differs from R's", a=a, b=b))[0])
            how = "exact, with the tied values taken into account, run in R"
        else:
            p = float(result.pvalue)
            how = "exact" if exact else "normal approximation for large groups"
        share_a, share_b = _shares(a, at), _shares(b, at)
        row = {"test": "two-sample Kolmogorov-Smirnov test", "what it compares":
               f'the shape of "{column}" in each "{for_each}" ({name_a}, {name_b})', "statistic name": "D",
               "statistic": d, "p-value": p, "biggest gap at": at, f"share at or below it in {name_a}": share_a,
               f"share at or below it in {name_b}": share_b, f"count in {name_a}": len(a), f"count in {name_b}": len(b)}
        ahead, behind = (name_a, name_b) if share_a > share_b else (name_b, name_a)
        print(f'The biggest gap between the groups is at "{column}" = {_num(at)}: {round(max(share_a, share_b) * 100)} % '
              f"of {ahead}'s values are at or below it, but only {round(min(share_a, share_b) * 100)} % of {behind}'s "
              f"(D = {_num(d)}), so {behind}'s values lie higher there.")
        print(_p_sentence(p, "the two groups truly had the same shape", "a gap this big or bigger",
                          "that the groups have the same shape"))
        print(f"Test: two-sample Kolmogorov-Smirnov test ({how}), which compares the whole shapes, as R ks.test().")
        return self._result_table(row)

    def _ad_many(self, column, for_each, groups, shuffles, seed):
        from scipy import stats

        names = [g[0] for g in groups]
        arrays = [g[1] for g in groups]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = stats.anderson_ksamp(arrays, midrank=True, method=stats.PermutationMethod(
                n_resamples=shuffles, rng=np.random.default_rng(seed)))
        t, p = float(result.statistic), float(result.pvalue)
        row = {"test": "Anderson-Darling k-sample test", "what it compares":
               f'the shape of "{column}" in each "{for_each}" ({", ".join(names)})',
               "statistic name": "T (standardised Anderson-Darling)", "statistic": t, "p-value": p,
               "p-value by": f"shuffled {shuffles} times, seed {seed}"}
        parts = []
        for n, v in zip(names, arrays):
            low, mid, high = (float(q) for q in np.percentile(v, [25, 50, 75]))
            row[f"median in {n}"], row[f"count in {n}"] = mid, len(v)
            parts.append(f"{_num(mid)} ({_num(low)} to {_num(high)}) in {n}")
        print(f'The median "{column}" (and the middle half of the values) is {_list_words(parts)}.')
        print(_p_sentence(p, "the groups truly had the same shape", "differences in shape this big or bigger",
                          "that the groups have the same shape"))
        print(f"Test: Anderson-Darling k-sample test (T = {_num(t)}, the midrank version for tied values, as R "
              f"kSamples::ad.test() version 2), which compares the whole shapes. The p-value comes from shuffling "
              f"the group labels {shuffles} times (seed {seed}); the same seed gives the same p-value.")
        return self._result_table(row)

    # ------------------------------------------------------------------ check_random_order
    @friendly
    def check_random_order(self, column=None, sorted_by=None):
        """Do the values come in a random order, or in clumps or waves?

        table.check_random_order("marks")   (the rows in table order)
        table.check_random_order("weight", sorted_by="date")
        The runs test: each value is above or below the median, and a run is an unbroken
        stretch on one side. Too few runs means values clump together (a trend or waves); too
        many means they flip back and forth. Values equal to the median are left out, as R
        randtests::runs.test() does (printed). statsmodels runstest_1samp(correction=False),
        the same numbers as R. Empty cells are skipped. Gives back a one-row table.
        """
        step = "check_random_order"
        example = 'table.check_random_order("marks")'
        self._need_name(step, "the column", column, example)
        frame = self._number_frame(step, [column])
        if sorted_by is not None:
            self._need_name(step, "sorted_by=", sorted_by, f'table.check_random_order("{column}", '
                                                            'sorted_by="date")')
            self._need_columns(sorted_by)
            if sorted_by == column:
                raise SimplydataError(f'sorted_by= should be another column than "{column}" (the order to test).')
            frame = frame.sort(sorted_by, nulls_last=True)
        values = frame[column].to_numpy().astype(float)
        keep = ~np.isnan(values)
        _skipped_note(int((~keep).sum()), [column])
        x = values[keep]
        if len(x) < 3:
            raise SimplydataError(f'{step}() needs at least 3 numbers in "{column}".')
        median = float(np.median(x))
        left_out = int((x == median).sum())
        x = x[x != median]
        if len(np.unique(x > median)) < 2:
            raise SimplydataError(f'{step}() needs values on both sides of the median of "{column}".')
        from statsmodels.sandbox.stats.runs import Runs

        runs = Runs((x > median).astype(int))
        z, p = (float(v) for v in runs.runs_test(correction=False))
        n_runs, above = int(runs.n_runs), int((x > median).sum())
        order = "table order" if sorted_by is None else f'order of "{sorted_by}"'
        row = {"test": "runs test", "what it compares": f'the order of "{column}" ({order}) with a random order',
               "statistic name": "z", "statistic": z, "p-value": p, "runs": n_runs, "median": median,
               "values above the median": above, "values below the median": len(x) - above,
               "values equal to the median (left out)": left_out}
        lean = ("fewer runs than a random order usually gives: values on one side of the median tend to come "
                "together" if z < 0 else "more runs than a random order usually gives: values tend to flip from "
                "one side of the median to the other")
        print(f'"{column}" in {order}: {n_runs} runs above and below the median ({_num(median)}) among {len(x)} '
              f"values, {lean}.")
        print(_p_sentence(p, "the order were truly random", "a number of runs this far from the usual or further",
                          "that the order is random"))
        dropped = ""
        if left_out:
            dropped = (f" {left_out} value{' was' if left_out == 1 else 's were'} equal to the median and left out, "
                       "as R does.")
        print(f"Test: runs test (z = {_num(z)}), as R randtests::runs.test() and statsmodels runstest_1samp().{dropped}")
        return self._result_table(row)
