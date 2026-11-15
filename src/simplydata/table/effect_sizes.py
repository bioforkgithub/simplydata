"""Effect sizes with their 95 % intervals, from the R package effectsize (through rpy2).

simplydata writes no effect-size formula. Each effect size and its interval comes from R
effectsize (Ben-Shachar, Luedecke and Makowski 2020), the same function an R user would call:
exact, noncentral-t intervals for d and g, two-sided intervals for every measure (effectsize 1.0
gives one-sided ones for omega-squared and Cramer's V by default; simplydata asks for two-sided,
like every other interval). Where Python has a function that gives the same number (Cramer's V:
SciPy; Cohen's w and h: statsmodels), the number comes from Python and only its interval from R.

Without R the test still runs; the effect size from R is left empty and a one-line note says how
to add it.
"""

from __future__ import annotations

import math

import numpy as np

# kind -> (R expression, name of the R result column, the name used in sentences)
_R = {
    "hedges_g": ("effectsize::hedges_g(a, b, ci = 0.95)", "Hedges_g", "Hedges' g"),
    "cohens_d_one": ("effectsize::cohens_d(x, mu = mu, ci = 0.95)", "Cohens_d", "Cohen's d"),
    "omega_squared": ('effectsize::omega_squared(stats::aov(y ~ factor(g)), partial = FALSE, ci = 0.95, '
                      'alternative = "two.sided")', "Omega2", "omega-squared"),
    "rank_biserial": ("effectsize::rank_biserial(a, b, ci = 0.95)", "r_rank_biserial", "rank-biserial correlation"),
    "rank_biserial_one": ("effectsize::rank_biserial(x, mu = mu, ci = 0.95)", "r_rank_biserial",
                          "rank-biserial correlation"),
    # its interval is a bootstrap interval in effectsize, so R's random numbers are seeded (set.seed(1))
    "rank_epsilon_squared": ('{ set.seed(1); effectsize::rank_epsilon_squared(y ~ factor(g), ci = 0.95, '
                             'alternative = "two.sided") }',
                             "rank_epsilon_squared", "epsilon-squared"),
    "cohens_w": ('effectsize::cohens_w(x, p = p, ci = 0.95, alternative = "two.sided")', "Cohens_w", "Cohen's w"),
    "cramers_v": ('effectsize::cramers_v(x, adjust = FALSE, ci = 0.95, alternative = "two.sided")', "Cramers_v",
                  "Cramer's V"),
}


def effect_size(kind: str, **values) -> dict:
    """{value, low, high, note}: R effectsize's estimate and two-sided 95 % interval.

    note is "" when R gave the answer, otherwise a one-line note saying how to add it (value,
    low and high are then NaN)."""
    from .._r import RMissing, r_call

    expression, column, name = _R[kind]
    code = f"es <- as.data.frame({expression}); list(value = es[[{column!r}]], low = es$CI_low, high = es$CI_high)"
    try:
        found = r_call(code, packages=("effectsize",), what=f"{name} with its 95 % interval (R effectsize)",
                       **values)
    except RMissing:
        return {"value": math.nan, "low": math.nan, "high": math.nan, "note": missing_note(name)}
    return {"value": float(np.asarray(found["value"])[0]), "low": float(np.asarray(found["low"])[0]),
            "high": float(np.asarray(found["high"])[0]), "note": ""}


def interval_only(kind: str, **values) -> dict:
    """R effectsize's interval for an effect size whose value comes from Python."""
    found = effect_size(kind, **values)
    note = missing_note(_R[kind][2], interval_only=True) if found["note"] else ""
    return {"low": found["low"], "high": found["high"], "note": note}


def missing_note(name: str, interval_only: bool = False) -> str:
    what = f"the 95 % CI of {name} comes" if interval_only else f"{name} and its 95 % CI come"
    return (f"Note: {what} from the R package effectsize, which is not ready here; to add "
            f'{"it" if interval_only else "them"}: pip install "simplydata[r]", install R, then in R '
            'install.packages("effectsize").')


def interval_text(low: float, high: float) -> str:
    """" (95 % CI 0.10 to 1.13)", or "" when there is no interval."""
    from .stat_tests import _num

    if math.isnan(low) or math.isnan(high):
        return ""
    return f" (95 % CI {_num(low)} to {_num(high)})"
