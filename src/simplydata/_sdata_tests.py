"""Tests from summary numbers: sdata.compare_averages(...) and sdata.compare_counts(...).

For when only the numbers of a paper or a report are at hand, not the rows. The same tests as
table.compare_averages_of and table.compare_counts_of, from SciPy and statsmodels:

* sdata.compare_averages(averages=[63.2, 68.9], standard_deviations=[8.1, 9.0], counts=[20, 22]):
  two groups: Welch's t-test from the summary numbers (SciPy ttest_ind_from_stats(equal_var=False),
  as R BSDA::tsum.test()); the 95 % interval of the difference comes from R BSDA::tsum.test()
  (SciPy gives none from summary numbers). Three or more groups: Welch's one-way ANOVA
  (statsmodels anova_generic(use_var="unequal"), the same numbers as R oneway.test() on the rows).
  test_method="student" / "anova" assume equal spreads.
* sdata.compare_counts([[20, 40], [30, 30]]): the chi-square test of independence on a table of
  counts, as table.compare_counts_of (R chisq.test()); test_method="fisher", "g", "barnard", "boschloo" as there.
"""

from __future__ import annotations

import math

import numpy as np

from ._errors import SimplydataError, choice_error, friendly

SUMMARY_TESTS_TWO = ("welch", "student")
SUMMARY_TESTS_MANY = ("welch anova", "anova")


def _numbers(step, option, values, example, whole=False):
    if isinstance(values, (str, bytes)) or not hasattr(values, "__len__"):
        raise SimplydataError(f"{step}() needs {option} as a list of numbers, one per group.\nFor example, {example}")
    out = []
    for v in values:
        if isinstance(v, bool) or not isinstance(v, (int, float, np.integer, np.floating)) or not math.isfinite(v):
            raise SimplydataError(f"{step}() needs {option} as numbers; {v!r} is not one.\nFor example, {example}")
        if whole and (v != int(v) or v < 2):
            raise SimplydataError(f"{option} are the number of values in each group: whole numbers of 2 or more "
                                  f"({v!r} is not).\nFor example, {example}")
        out.append(float(v))
    return out


def _table():
    """An empty table, so the results come back as a simplydata table like every test's."""
    from .table import table

    return table({"group": ["-"]})


@friendly(renamed={"test": "test_method", "groups": "names"})
def compare_averages(averages=None, standard_deviations=None, counts=None, names=None, test_method=None):
    """Are the averages of the groups different? From the summary numbers of each group.

    sdata.compare_averages(averages=[63.2, 68.9], standard_deviations=[8.1, 9.0], counts=[20, 22])
    For when only the summary numbers are given (a paper, a report), not the rows. Two groups:
    Welch's t-test (SciPy ttest_ind_from_stats, as R BSDA::tsum.test()), with the 95 % interval of
    the difference from R (BSDA::tsum.test(), simplydata[r]). Three or more groups: Welch's one-way
    ANOVA (statsmodels anova_generic, the same numbers as R oneway.test() on the rows).
    test_method="student" (two groups) or test_method="anova" (three or more) assume the groups have the same
    spread. names= names the groups (default "group 1", "group 2", ...). With the rows at hand use
    table.compare_averages_of(...), which also gives the effect size. Gives back a one-row table.
    """
    step = "compare_averages"
    example = "sdata.compare_averages(averages=[63.2, 68.9], standard_deviations=[8.1, 9.0], counts=[20, 22])"
    if averages is None or standard_deviations is None or counts is None:
        raise SimplydataError(f"sdata.{step}() needs averages=, standard_deviations= and counts= (one number per "
                              f"group).\nFor example, {example}\nWith a table of rows, use table.{step}_of(...).")
    means = _numbers(step, "averages=", averages, example)
    sds = _numbers(step, "standard_deviations=", standard_deviations, example)
    ns = _numbers(step, "counts=", counts, example, whole=True)
    k = len(means)
    if k < 2 or len(sds) != k or len(ns) != k:
        raise SimplydataError(f"sdata.{step}() needs the same number of averages, standard deviations and counts, "
                              f"for 2 or more groups (it got {len(means)}, {len(sds)} and {len(ns)}).\n"
                              f"For example, {example}")
    if any(s <= 0 for s in sds):
        raise SimplydataError("standard_deviations= must all be above 0.")
    if names is not None and (isinstance(names, (str, bytes)) or not hasattr(names, "__iter__")):
        raise SimplydataError(f"names= needs a list of {k} names, one per group, like names={['A', 'B', 'C'][:k] if k <= 3 else '[...]'}.")
    names = [f"group {i + 1}" for i in range(k)] if names is None else [str(g) for g in names]
    if len(names) != k or len(set(names)) != k:
        raise SimplydataError(f"names= needs {k} different names, one per group.")
    allowed = SUMMARY_TESTS_TWO if k == 2 else SUMMARY_TESTS_MANY
    test_method = test_method or allowed[0]
    if test_method not in allowed:
        raise choice_error(step, "test_method", test_method, list(allowed))
    from .table.stat_tests import ALIKE, _list_words, _num, _whole
    from .table.summaries import _p_sentence

    row = {"test": None, "what it compares": f"the averages of {_list_words(names)}, from summary numbers"}
    for n, m, s, c in zip(names, means, sds, ns):
        row.update({f"average in {n}": m, f"standard deviation in {n}": s, f"count in {n}": int(c)})
    if k == 2:
        from scipy import stats

        from ._r import RMissing, r_call

        equal = test_method == "student"
        result = stats.ttest_ind_from_stats(means[0], sds[0], ns[0], means[1], sds[1], ns[1], equal_var=equal)
        t, p = float(result.statistic), float(result.pvalue)
        name = "Student's t-test" if equal else "Welch's t-test"
        diff = means[0] - means[1]
        try:
            found = r_call("r <- BSDA::tsum.test(m1, s1, n1, m2, s2, n2, var.equal = equal); "
                           "list(ci = unname(r$conf.int), df = unname(r$parameter))", packages=("BSDA",),
                           what="the 95 % interval of the difference from summary numbers (R BSDA::tsum.test())",
                           m1=means[0], s1=sds[0], n1=ns[0], m2=means[1], s2=sds[1], n2=ns[1], equal=equal)
            low, high = (float(v) for v in np.asarray(found["ci"]))
            df = float(np.asarray(found["df"])[0])
            interval = f" (95 % CI of the difference {_num(low)} to {_num(high)})"
            note = ""
        except RMissing:
            low = high = df = math.nan
            interval = ""
            note = ('Note: the 95 % CI of the difference comes from the R package BSDA (tsum.test), which is not '
                    'ready here; to add it: pip install "simplydata[r]", install R, then in R install.packages("BSDA").')
        row.update({"test": name, "statistic name": "t", "statistic": t, "degrees of freedom": df, "p-value": p,
                    "difference": diff, "difference 95 % CI low": low, "difference 95 % CI high": high})
        print(f"The average is {_num(means[0])} in {names[0]} and {_num(means[1])} in {names[1]}: {names[0]} is "
              f"{_num(abs(diff))} {'higher' if diff > 0 else 'lower'}{interval}.")
        print(_p_sentence(p, "there were truly no difference"))
        why = ("it does not assume both groups have the same spread" if not equal else
               "chosen with test_method=; it assumes both groups have the same spread")
        print(f"Test: {name} from summary numbers (t = {_num(t)}" + ("" if math.isnan(df) else f", df = {_whole(df)}")
              + f"), as R BSDA::tsum.test(); {why}.")
        if note:
            print(note)
    else:
        from statsmodels.stats.oneway import anova_generic

        equal = test_method == "anova"
        result = anova_generic(np.array(means), np.array(sds) ** 2, np.array(ns),
                               use_var="equal" if equal else "unequal", welch_correction=True)
        f, p = float(result.statistic), float(result.pvalue)
        df1, df2 = (float(v) for v in result.df)
        name = "one-way ANOVA" if equal else "Welch's one-way ANOVA"
        row.update({"test": name, "statistic name": "F", "statistic": f, "degrees of freedom 1": df1,
                    "degrees of freedom 2": df2, "p-value": p})
        print(f"The average is {_list_words(f'{_num(m)} in {n}' for n, m in zip(names, means))}.")
        print(_p_sentence(p, *ALIKE))
        why = ("it does not assume the groups have the same spread" if not equal else
               "chosen with test_method=; it assumes the groups have the same spread")
        print(f"Test: {name} from summary numbers (F = {_num(f)}, df = {_whole(df1)} and {_whole(df2)}), the same "
              f"numbers as R oneway.test({'var.equal = TRUE' if equal else ''}) on the rows; {why}.")
    return _table()._result_table(row)


@friendly(renamed={"test": "test_method"})
def compare_counts(counts=None, test_method=None):
    """Are the rows and columns of a table of counts linked? From the counts alone.

    sdata.compare_counts([[20, 40], [30, 30]])
    A table of counts: one list per row (or a pandas DataFrame of counts, whose row and column
    names are used). The chi-square test of independence (as R chisq.test(), with Yates'
    continuity correction for 2 x 2 tables), with Cramer's V; test_method="fisher", "g", "barnard" or
    "boschloo" as in table.compare_counts_of() (Barnard's and Boschloo's tests take the two rows as the two
    samples). With a table of rows use table.compare_counts_of(column,
    for_each_group_in=). Gives back a one-row table.
    """
    step = "compare_counts"
    example = "sdata.compare_counts([[20, 40], [30, 30]])"
    if counts is None:
        raise SimplydataError(f"sdata.{step}() needs a table of counts, one list per row.\nFor example, {example}\n"
                              f"With a table of rows, use table.{step}_of(column, for_each_group_in=...).")
    try:
        observed = np.asarray(counts.to_numpy() if hasattr(counts, "to_numpy") else counts, dtype=float)
    except (TypeError, ValueError):
        raise SimplydataError(f"sdata.{step}() needs whole numbers in a table, one list per row.\n"
                              f"For example, {example}") from None
    if observed.ndim != 2 or min(observed.shape) < 2:
        raise SimplydataError(f"sdata.{step}() needs at least 2 rows and 2 columns of counts.\nFor example, {example}")
    if np.isnan(observed).any() or (observed < 0).any() or (observed != np.round(observed)).any():
        raise SimplydataError("The counts must be whole numbers of 0 or more.")
    from .table.stat_tests import COUNT_TESTS

    if test_method is not None and test_method not in COUNT_TESTS:
        raise choice_error(step, "test_method", test_method, list(COUNT_TESTS))
    shape = f"{observed.shape[0]} rows and {observed.shape[1]} columns"
    return _table()._counts_engine(observed.astype(np.int64), "row", "column", test_method,
                                   what=f"the counts in {shape}", unit="counted",
                                   unrelated="the rows and the columns were truly unrelated")
