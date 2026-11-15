"""Equivalence and non-inferiority (same_within=): two one-sided tests, from statsmodels.

simplydata only prepares the data and words the answer; every number comes from statsmodels or SciPy:

* two groups: statsmodels ttost_ind(usevar="unequal") (Welch, the R TOSTER::t_TOST() default;
  statsmodels' own default is the pooled test), with the 90 % interval from SciPy ttest_ind;
* matched rows: statsmodels ttost_paired, interval from SciPy ttest_rel;
* one column against a value: statsmodels DescrStatsW.ttost_mean, interval from ttest_1samp;
* non-inferiority (same_within= with sides=1, higher=): one one-sided test against the margin,
  statsmodels CompareMeans.ttest_ind(value=-margin, alternative="larger"), as R
  TOSTER::t_TOST(hypothesis = "MET") or t.test(mu = -margin, alternative = "greater").

The answer is always one of three: the same within the margin, different, or the data cannot tell
(the wording rule after a large p-value: never "no difference").
"""

from __future__ import annotations

import numpy as np

from .._errors import SimplydataError


def margin(step, same_within):
    """same_within=5 -> (-5, 5); same_within=[-3, 5] -> (-3, 5)."""
    example = f"table.{step}(..., same_within=5)   (or same_within=[-3, 5] for a lopsided margin)"
    if isinstance(same_within, bool):
        raise SimplydataError(f"same_within= needs a number in the data's units.\nFor example, {example}")
    if isinstance(same_within, (int, float, np.integer, np.floating)):
        if same_within <= 0:
            raise SimplydataError(f"same_within= needs a number above 0 (the biggest difference that does not "
                                  f"matter).\nFor example, {example}")
        return -float(same_within), float(same_within)
    if isinstance(same_within, (list, tuple)) and len(same_within) == 2 and all(
            isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, bool) for v in same_within):
        low, high = (float(v) for v in same_within)
        if not low < 0 < high:
            raise SimplydataError(f"same_within=[low, high] needs low below 0 and high above 0, such as [-3, 5].\n"
                                  f"For example, {example}")
        return low, high
    raise SimplydataError(f"same_within= needs a number, or two numbers [low, high].\nFor example, {example}")


def tost(kind, data, low, high):
    """Two one-sided tests. kind "two groups" (data = (a, b), a minus b), "paired" (data = (after, before),
    after minus before) or "one sample" (data = (x,), x minus 0; shift x first for another value).
    Gives back {difference, p_low, p_high, p, ci90, ci95, df}."""
    from scipy import stats
    from statsmodels.stats.weightstats import DescrStatsW, ttost_ind, ttost_paired

    if kind == "two groups":
        a, b = data
        p, lower, upper = ttost_ind(a, b, low, high, usevar="unequal")
        usual = stats.ttest_ind(a, b, equal_var=False)
        difference = float(np.mean(a) - np.mean(b))
    elif kind == "paired":
        after, before = data
        p, lower, upper = ttost_paired(after, before, low, high)
        usual = stats.ttest_rel(after, before)
        difference = float(np.mean(np.asarray(after) - np.asarray(before)))
    else:
        (x,) = data
        p, lower, upper = DescrStatsW(x).ttost_mean(low, high)
        usual = stats.ttest_1samp(x, 0)
        difference = float(np.mean(x))
    ci90, ci95 = usual.confidence_interval(0.90), usual.confidence_interval(0.95)
    return {"difference": difference, "p_low": float(lower[1]), "p_high": float(upper[1]), "p": float(p),
            "ci90": (float(ci90.low), float(ci90.high)), "ci95": (float(ci95.low), float(ci95.high)),
            "p_usual": float(usual.pvalue), "df": float(lower[2])}


def non_inferior(kind, data, edge, toward):
    """One one-sided test that the difference is above edge (toward="higher") or below it ("lower").
    Same data conventions as tost(). Gives back {difference, p, ci (one-sided 95 %), df}."""
    from scipy import stats

    alternative = "greater" if toward == "higher" else "less"
    if kind == "two groups":
        from statsmodels.stats.weightstats import CompareMeans, DescrStatsW

        a, b = data
        compare = CompareMeans(DescrStatsW(np.asarray(a, dtype=float)), DescrStatsW(np.asarray(b, dtype=float)))
        side = "larger" if toward == "higher" else "smaller"
        _, p, df = compare.ttest_ind(alternative=side, usevar="unequal", value=edge)
        ci = compare.tconfint_diff(alpha=0.05, alternative=side, usevar="unequal")
        return {"difference": float(np.mean(a) - np.mean(b)), "p": float(p), "ci": (float(ci[0]), float(ci[1])),
                "df": float(df)}
    if kind == "paired":
        after, before = data
        result = stats.ttest_1samp(np.asarray(after) - np.asarray(before), edge, alternative=alternative)
        difference = float(np.mean(np.asarray(after) - np.asarray(before)))
    else:
        (x,) = data
        result = stats.ttest_1samp(x, edge, alternative=alternative)
        difference = float(np.mean(x))
    ci = result.confidence_interval(0.95)
    return {"difference": difference, "p": float(result.pvalue), "ci": (float(ci.low), float(ci.high)),
            "df": float(result.df)}


def say(result, low, high, unit_words, names, method, if_far):
    """The three-answer sentences for an equivalence test; returns (lines, verdict)."""
    from .stat_tests import _interval_words, _num
    from .summaries import _p_sentence

    lo90, hi90 = result["ci90"]
    lo95, hi95 = result["ci95"]
    span = f"{low:g} to {high:g}"
    within = f"{high:g}" if low == -high else span
    if result["p"] < 0.05:
        verdict = "the same within the margin"
        answer = f"so {names} are the same within {within} {unit_words}".rstrip()
    elif lo95 > 0 or hi95 < 0:
        verdict = "different"
        answer = (f"and the 95 % interval, {_interval_words(lo95, hi95)}, leaves out 0, so {names} differ, "
                  "and by an amount the margin may not allow")
    else:
        verdict = "the data cannot tell"
        answer = (f"so the data cannot tell whether {names} are the same within {within}: values from "
                  f"{_num(lo95)} to {_num(hi95)} fit the data (95 % CI). More data would narrow the interval")
    inside = "lies inside" if low < lo90 and hi90 < high else "does not lie inside"
    first = (f"The difference is {_num(result['difference'])}; the 90 % confidence interval, {_num(lo90)} to "
             f"{_num(hi90)}, {inside} {span}, {answer}.")
    second = _p_sentence(result["p"], if_far, "a difference this far inside the margin",
                         "that they differ by more than the margin")
    third = (f"Method: two one-sided tests (TOST, {method}); the larger of the two p-values counts (p = "
             f"{_num(result['p_low'])} against {low:g}, p = {_num(result['p_high'])} against {high:g}). "
             "The 90 % interval goes with the two 5 % tests.")
    return [first, second, third], verdict
