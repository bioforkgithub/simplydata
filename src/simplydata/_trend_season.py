"""Cross-correlation, trend and season, and trend tests for time series.

Every number comes from a package, with the options that give R's numbers:
* cross-correlation: statsmodels ccf(x, y, adjusted=False) in both directions = R ccf(a, b)
  (simplydata's shift s pairs the first column at row t with the second at row t + s, which is R's
  lag -s; R's lag k pairs a[t + k] with b[t]). The noise band is +/- qnorm(0.975) / sqrt(n), the dashed
  lines of R plot.ccf (display arithmetic).
* trend and season, test_method="loess": statsmodels STL with R stl()'s settings (season degree 0, R's
  trend and low-pass spans and its jumps; inner 2 / outer 0 passes, or 1 / 15 with robust=True), which
  give R stl(x, s.window =) to about 1e-12. season_window="fixed" runs R stl(s.window = "periodic")
  itself through rpy2 (statsmodels has no periodic option; its STL with a long window differs by about
  1e-4).
* test_method="moving averages": statsmodels seasonal_decompose(two_sided=True) = R decompose() (added or
  multiplied seasons).
* test_method="straight line": one statsmodels OLS fit on the row number and, with repeats_every=, one effect per
  place in the cycle that add up to 0 = R lm(x ~ time + place, contrasts = list(place = "contr.sum")); the
  trend is the line from the fit, the season the rest of the fitted values.
* find_trend_of: Sen's slope and its 95 % interval from SciPy theilslopes (= R trend::sens.slope); the
  Mann-Kendall test, the seasonal Mann-Kendall test and the seasonal Sen slope run in R itself
  (trend::mk.test, trend::smk.test, trend::sea.sens.slope: SciPy has no continuity correction).
"""

from __future__ import annotations

import math
import warnings

import numpy as np

from ._errors import SimplydataError, choice_error

TREND_METHODS = ("loess", "moving averages", "straight line")
TREND_ALIASES = {"stl": "loess", "classical": "moving averages", "decompose": "moving averages",
                 "line": "straight line", "linear": "straight line"}
SEASONS = ("added", "multiplied")
SEASON_ALIASES = {"additive": "added", "multiplicative": "multiplied"}
CYCLE_WORDS = {("months", "year"): 12, ("quarters", "year"): 4, ("days", "week"): 7, ("days", "year"): 365}


def read_repeats_every(repeats_every, series, step_name, needed=True):
    """repeats_every= as a whole number of readings: 12, or "year" for months (12) and quarters (4),
    "week" for days (7)."""
    if repeats_every is None:
        if needed:
            raise SimplydataError(f'{step_name}() needs repeats_every= : how many readings make one cycle, such as '
                                  'repeats_every=12, or repeats_every="year" for monthly readings.')
        return None
    if isinstance(repeats_every, str):
        word = repeats_every.strip().lower()
        if (series.unit, word) in CYCLE_WORDS:
            return CYCLE_WORDS[(series.unit, word)]
        raise SimplydataError(f'repeats_every="{repeats_every}" needs readings by date that fit it ("year" for '
                              f'months or quarters, "week" for days); here the readings are {series.describe()}. '
                              "Give the number of readings in one cycle, such as repeats_every=12.")
    if isinstance(repeats_every, bool) or not isinstance(repeats_every, (int, np.integer)) or repeats_every < 2:
        raise SimplydataError(f"{step_name}() needs repeats_every= as a whole number of readings of at least 2, or "
                              'a word such as "year".')
    return int(repeats_every)


# ---------------------------------------------------------------------------- cross-correlation
def cross_correlation(a, b, rows_back):
    """Shifts -rows_back .. rows_back: corr(a[t], b[t + shift]) as R ccf(a, b) at lag -shift."""
    from scipy import stats
    from statsmodels.tsa.stattools import ccf

    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    later = ccf(b, a, adjusted=False, fft=False)[: rows_back + 1]  # corr(b[t + s], a[t])
    earlier = ccf(a, b, adjusted=False, fft=False)[: rows_back + 1]  # corr(a[t + s], b[t])
    shifts = np.arange(-rows_back, rows_back + 1)
    values = np.concatenate([earlier[1:][::-1], later])
    half = float(stats.norm.ppf(0.975) / math.sqrt(len(a)))
    return shifts, values, half


# ---------------------------------------------------------------------------- trend and season
def _nextodd(x) -> int:
    x = int(round(x))
    return x if x % 2 else x + 1


def _stl_statsmodels(x, period, season_window, robust):
    from statsmodels.tsa.seasonal import STL

    trend = _nextodd(math.ceil(1.5 * period / (1 - 1.5 / season_window)))
    low = _nextodd(period)
    fit = STL(x, period=period, seasonal=season_window, trend=trend, low_pass=low, seasonal_deg=0, trend_deg=1,
              low_pass_deg=1, seasonal_jump=math.ceil(season_window / 10), trend_jump=math.ceil(trend / 10),
              low_pass_jump=math.ceil(low / 10), robust=robust)
    result = fit.fit(inner_iter=1 if robust else 2, outer_iter=15 if robust else 0)
    return np.asarray(result.trend), np.asarray(result.seasonal), np.asarray(result.resid)


def _r_stl_periodic(x, period, robust):
    """R stl(ts(x, frequency = period), s.window = "periodic") itself."""
    from ._r import r_call

    out = r_call(f"s <- stats::stl(stats::ts(x, frequency = {int(period)}), s.window = 'periodic', "
                 f"robust = {'TRUE' if robust else 'FALSE'}); "
                 "list(trend = as.numeric(s$time.series[, 'trend']), season = as.numeric(s$time.series[, 'seasonal']), "
                 "rest = as.numeric(s$time.series[, 'remainder']))",
                 what='A fixed season (R stl(s.window = "periodic"))',
                 python_note="statsmodels STL with a long season window is the Python alternative; it differs by "
                             "about 1e-4", source="stats::stl", x=x)
    return (np.asarray(out["trend"], dtype=float), np.asarray(out["season"], dtype=float),
            np.asarray(out["rest"], dtype=float))


def trend_and_season(values, period, method="loess", season="added", season_window=7, robust=False,
                     step_name="add_trend_and_season"):
    """dict(trend, season, rest, method sentence, R call)."""
    x = np.asarray(values, dtype=float)
    n = len(x)
    if method == "straight line":
        # one least-squares fit of the time and (with a cycle) one effect per place in the cycle, the
        # effects adding to 0 (sum contrasts): R lm(x ~ time + place, contrasts = list(place = "contr.sum"))
        import pandas as pd
        from statsmodels.formula.api import ols

        time = np.arange(1, n + 1, dtype=float)
        data = pd.DataFrame({"x": x, "time": time, "place": np.arange(n) % (period or 1)})
        formula = "x ~ time + C(place, Sum)" if period else "x ~ time"
        fit = ols(formula, data).fit()
        trend = fit.params["Intercept"] + fit.params["time"] * time
        season_part = np.asarray(fit.fittedvalues) - trend
        rest = np.asarray(fit.resid)
        call = ('lm(x ~ time + place, contrasts = list(place = "contr.sum")), place = factor((time - 1) %% '
                f"{period})" if period else "lm(x ~ time)")
        return dict(trend=trend, season=season_part, rest=rest,
                    how="one least-squares fit of a straight line over time" + (
                        " and an effect for each place in the cycle (the effects add up to 0)" if period else ""),
                    call=call)
    if period is None:
        raise SimplydataError(f'test_method="{method}" needs repeats_every= (how many readings make one cycle).')
    if n < 2 * period:
        raise SimplydataError(f"{step_name}() needs at least two full cycles ({2 * period} readings) to find a "
                              f"season; there are {n}.")
    if method == "moving averages":
        from statsmodels.tsa.seasonal import seasonal_decompose

        if season == "multiplied" and (x <= 0).any():
            raise SimplydataError('season="multiplied" needs values above 0.')
        model = "multiplicative" if season == "multiplied" else "additive"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = seasonal_decompose(x, model=model, period=period, two_sided=True)
        kind = ', type = "multiplicative"' if season == "multiplied" else ""
        return dict(trend=np.asarray(result.trend), season=np.asarray(result.seasonal), rest=np.asarray(result.resid),
                    how=f"classical decomposition by moving averages over one cycle ({'multiplied' if season == 'multiplied' else 'added'} season)",
                    call=f"decompose(ts(x, frequency = {period}){kind})")
    # loess (STL)
    if season == "multiplied":
        raise SimplydataError('season="multiplied" works with test_method="moving averages". For test_method="loess", take the '
                              'log first, for example table.add_column("log_visitors", "log(visitors)").')
    robust_words = ", robust = TRUE" if robust else ""
    if season_window == "fixed":
        trend, season_part, rest = _r_stl_periodic(x, period, robust)
        return dict(trend=trend, season=season_part, rest=rest,
                    how="STL (season and trend by loess), the same season in every cycle, run in R",
                    call=f'stl(ts(x, frequency = {period}), s.window = "periodic"{robust_words})')
    if isinstance(season_window, bool) or not isinstance(season_window, (int, np.integer)) or season_window < 7 \
            or season_window % 2 == 0:
        raise SimplydataError(f'{step_name}() needs season_window= as an odd whole number of cycles, at least 7, or '
                              '"fixed" (the same season in every cycle).')
    trend, season_part, rest = _stl_statsmodels(x, period, int(season_window), robust)
    return dict(trend=trend, season=season_part, rest=rest,
                how=f"STL (season and trend by loess, season window {int(season_window)}"
                    f"{', robust to outliers' if robust else ''}), statsmodels with R's settings",
                call=f"stl(ts(x, frequency = {period}), s.window = {int(season_window)}{robust_words})")


# ---------------------------------------------------------------------------- trend tests
def sen_slope(values):
    """Sen's slope with its 95 % interval, SciPy theilslopes (= R trend::sens.slope)."""
    from scipy import stats

    result = stats.theilslopes(np.asarray(values, dtype=float), alpha=0.95)
    return float(result.slope), float(result.low_slope), float(result.high_slope)


def lag1_after_sen_line(values, times=None) -> dict:
    """The lag-1 autocorrelation of the readings left after Sen's line (statsmodels acf) and the Ljung-Box test
    at lag 1 (statsmodels acorr_ljungbox): the check of find_trend_of that its readings are independent. Taking
    out the trend first matters: a trend alone makes neighbouring readings alike (Yue et al. 2002)."""
    from scipy import stats
    from statsmodels.stats.diagnostic import acorr_ljungbox
    from statsmodels.tsa.stattools import acf

    values = np.asarray(values, dtype=float)
    x = np.arange(len(values), dtype=float) if times is None else np.asarray(times, dtype=float)
    fit = stats.theilslopes(values, x)
    rest = values - (fit.intercept + fit.slope * x)  # [D] the readings left after SciPy's Sen line
    if np.ptp(rest) <= 1e-10 * max(1.0, float(np.max(np.abs(values)))):  # on the line but for rounding
        return {"r": math.nan, "p": 1.0}
    r = float(acf(rest, nlags=1, fft=False)[1])
    p = float(np.asarray(acorr_ljungbox(rest, lags=[1])["lb_pvalue"])[0])
    return {"r": r, "p": p}


def _r_mann_kendall(values, period=None):
    """R trend::mk.test (or smk.test and sea.sens.slope with a season): z, p, S, tau, seasonal slope."""
    from ._r import r_call

    if period is None:
        code = ("m <- trend::mk.test(x); list(z = unname(m$statistic), p = m$p.value, S = unname(m$estimates['S']), "
                "tau = unname(m$estimates['tau']))")
    else:
        code = (f"y <- stats::ts(x, frequency = {int(period)}); m <- trend::smk.test(y); "
                "list(z = unname(m$statistic), p = m$p.value, slope = unname(trend::sea.sens.slope(y)))")
    out = r_call(code, packages=("trend",), what="The Mann-Kendall trend test (R trend::mk.test())",
                 python_note="SciPy kendalltau gives a similar test without R's continuity correction, so its "
                             "p-value differs", source="trend", x=np.asarray(values, dtype=float))
    return {k: float(np.asarray(v).ravel()[0]) for k, v in out.items()}


def mann_kendall(values, period=None):
    """The R test, or None when R is not ready (the slope is still given; a note says how to add the test)."""
    from ._r import RMissing

    try:
        return _r_mann_kendall(values, period), None
    except RMissing as missing:
        return None, str(missing)
