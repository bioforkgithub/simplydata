"""Smoothing a series, and taking away its trend. Every number comes from a package:

* "moving average" (and weights=): scipy.ndimage.convolve1d with the weights scaled to add up to 1,
  ends "empty" (as R stats::filter(x, w, sides = 2)) or "mirror" (SciPy mode "reflect");
  ends="shorter windows" averages what is there (pandas rolling(center=True, min_periods=1), as R
  zoo::rollapply(partial = TRUE)); plain averages only;
* "median": R stats::runmed(x, k, endrule =) itself (SciPy's median filters pad the ends with zeros or
  repeat them; neither is Tukey's end rule), ends "tukey" (R's "median"), "keep" or "constant";
* "savitzky-golay": scipy.signal.savgol_filter(mode="interp") = R signal::sgolayfilt;
* "exponential": pandas ewm(alpha=, adjust=False).mean() = R stats::filter(a * x, 1 - a, method =
  "recursive", init = x[1]);
* "gaussian": scipy.ndimage.gaussian_filter1d(sigma=width, truncate=4, mode="reflect");
* "lowess": statsmodels lowess with R lowess()'s settings (3 robustness steps, delta 1 % of the range);
* "loess": R stats::loess(degree = 2, span = smoothness=, normally 0.75) itself, with predict(se = TRUE) for its
  confidence band (interval=); not lowess: loess fits local curves (degree 2) without robustness steps;
* "spline": SciPy make_smoothing_spline as table.values_at(smoothness=) (R smooth.spline);
* "whittaker": scipy.signal.whittaker_henderson(lamb=, order=2);
* "wiener": scipy.signal.wiener(mysize=window);
* remove_trend: scipy.signal.detrend(type="linear" or "constant", bp=breaks).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from ._errors import SimplydataError, choice_error

METHODS = ("moving average", "median", "savitzky-golay", "exponential", "gaussian", "lowess", "loess", "spline",
           "whittaker", "wiener")
ALIASES = {"moving_average": "moving average", "mean": "moving average", "average": "moving average",
           "rolling average": "moving average", "running median": "median", "runmed": "median",
           "savgol": "savitzky-golay", "savitzky golay": "savitzky-golay", "sgolay": "savitzky-golay",
           "ewm": "exponential", "ewma": "exponential", "exponential smoothing": "exponential",
           "gauss": "gaussian", "local regression": "loess", "smoothing spline": "spline", "whittaker-henderson": "whittaker"}
ENDS = {"moving average": ("empty", "shorter windows", "mirror"), "median": ("tukey", "keep", "constant"),
        "savitzky-golay": ("fitted curve",), "gaussian": ("mirror",)}
WINDOW_METHODS = ("moving average", "median", "savitzky-golay", "wiener")
OPTIONS = {"moving average": {"weights"}, "savitzky-golay": {"of_degree"},
           "exponential": {"newest_weight", "alpha", "span", "half_life", "com"}, "gaussian": {"width"},
           "lowess": {"smoothness"}, "loess": {"smoothness", "interval"}, "spline": {"smoothness"}, "whittaker": {"smoothness"}}
R_ENDRULE = {"tukey": "median", "keep": "keep", "constant": "constant"}


@dataclass
class SmoothResult:
    values: np.ndarray
    sentence: str  # what was done, in words
    r_call: str  # the R call that gives the same numbers
    low: np.ndarray | None = None  # method="loess" with interval=: the ends of the confidence band
    high: np.ndarray | None = None


def read_method(method, step_name):
    chosen = ALIASES.get(method.strip().lower(), method.strip().lower()) if isinstance(method, str) else method
    if chosen not in METHODS:
        raise choice_error(step_name, "test_method", method, list(METHODS))
    return chosen


def _odd_window(window, step_name, method):
    if isinstance(window, bool) or not isinstance(window, (int, np.integer)) or window < 3 or window % 2 == 0:
        raise SimplydataError(f'{step_name}() with test_method="{method}" needs window= as an odd whole number of readings, '
                              "at least 3, such as window=5, so the window is centred on each reading. (For a "
                              "12-month season, use add_trend_and_season.)")
    return int(window)


def _newest_weight(options, step_name):
    given = {k: v for k, v in options.items() if k in OPTIONS["exponential"] and v is not None}
    if len(given) > 1:
        raise SimplydataError(f"{step_name}() needs only one of newest_weight=, alpha=, span=, half_life= or com=.")
    name, value = next(iter(given.items())) if given else ("newest_weight", 0.3)
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)) or value <= 0:
        raise SimplydataError(f"{step_name}() needs {name}= as a number above 0.")
    if name in ("newest_weight", "alpha"):
        if value > 1:
            raise SimplydataError(f"{step_name}() needs {name}= from above 0 up to 1 (the weight of the newest reading).")
        return float(value), f"newest_weight={_g(value)}"
    if name == "span":
        if value < 1:
            raise SimplydataError("span= needs a number of at least 1.")
        return 2.0 / (value + 1.0), f"span={_g(value)}, so newest_weight = 2 / (span + 1) = {_g(2 / (value + 1))}"
    if name == "half_life":
        a = 1.0 - math.exp(-math.log(2.0) / value)
        return a, f"half_life={_g(value)}, so newest_weight = 1 - exp(-ln 2 / half_life) = {_g(a)}"
    return 1.0 / (1.0 + value), f"com={_g(value)}, so newest_weight = 1 / (1 + com) = {_g(1 / (1 + value))}"


def _opt(options, name, default):
    value = options.get(name)
    return default if value is None else value


def _g(x) -> str:
    return f"{float(x):.4g}"


def smooth(values, method="moving average", window=5, ends=None, times=None, step_name="smooth", **options):
    """SmoothResult for one evenly spaced series (lowess and spline use times=, the x values)."""
    from . import _r

    method = read_method(method, step_name)
    allowed = OPTIONS.get(method, set())
    extra = sorted(k for k, v in options.items() if v is not None and k not in allowed)
    if extra:
        hint = ", ".join(f"{k}=" for k in sorted(allowed)) or "no other options"
        raise SimplydataError(f'{step_name}() with test_method="{method}" does not take {extra[0]}= (it takes {hint}).')
    x = np.asarray(values, dtype=float)
    n = len(x)
    if method in ENDS:
        ends = ENDS[method][0] if ends is None else ends
        if ends not in ENDS[method]:
            raise choice_error(step_name, "ends", ends, list(ENDS[method]))
    elif ends is not None:
        raise SimplydataError(f'test_method="{method}" has no ends= choice (it needs none).')
    if method not in ("lowess", "loess", "spline") and np.isnan(x).any():
        raise SimplydataError(f"{step_name}() needs a value at every step, but {int(np.isnan(x).sum())} are empty. "
                              'Fill them first (fill_empty_cells_in(..., with_the="line between neighbours")).')

    if method == "moving average":
        weights = options.get("weights")
        if weights is not None:
            w = np.asarray(weights, dtype=float).ravel()
            if len(w) < 3 or len(w) % 2 == 0 or not np.isfinite(w).all() or w.sum() <= 0:
                raise SimplydataError("weights= needs an odd number of weights (at least 3) that add up to more than 0, "
                                      "such as weights=[1, 2, 1].")
            if ends == "shorter windows":
                raise SimplydataError('ends="shorter windows" is for a plain moving average (no weights=).')
            k, how = len(w), f"a weighted moving average over {len(w)} readings (weights {', '.join(_g(v) for v in w)}, scaled to add up to 1)"
        else:
            k = _odd_window(window, step_name, method)
            w, how = np.ones(k), f"a moving average over {k} readings centred on each one"
        if n < k:
            raise SimplydataError(f"{step_name}() needs at least {k} readings for this window; there are {n}.")
        w = w / w.sum()
        w_r = "w / sum(w)" if weights is not None else f"rep(1 / {k}, {k})"
        if ends == "shorter windows":
            import pandas as pd

            out = pd.Series(x).rolling(k, center=True, min_periods=1).mean().to_numpy()
            return SmoothResult(out, how + "; near the ends, the average of the readings there are",
                                f"zoo::rollapply(x, {k}, mean, partial = TRUE)")
        from scipy import ndimage

        out = ndimage.convolve1d(x, w, mode="reflect")
        if ends == "empty":
            half = k // 2
            out[:half] = np.nan
            out[n - half:] = np.nan
            return SmoothResult(out, how + f"; the first and last {half} readings have no full window, so they are empty",
                                f"stats::filter(x, {w_r}, sides = 2)")
        return SmoothResult(out, how + "; at the ends the readings are mirrored", f"filter of the mirrored readings ({w_r})")

    if method == "median":
        k = _odd_window(window, step_name, method)
        if n < k:
            raise SimplydataError(f"{step_name}() needs at least {k} readings for this window; there are {n}.")
        out = _r.r_call(f'as.numeric(stats::runmed(x, {k}, endrule = "{R_ENDRULE[ends]}"))',
                        what="The running median (R stats::runmed())",
                        python_note="scipy.signal.medfilt is the Python alternative; it pads the ends with zeros, so "
                                    "its first and last values differ", source="stats::runmed", x=x)
        end_words = {"tukey": "Tukey's end rule (the ends from medians of 3)", "keep": "the end readings kept as they are",
                     "constant": "the end readings set to the median of the first and last window"}[ends]
        return SmoothResult(np.asarray(out, dtype=float), f"a running median over {k} readings, {end_words}, run in R",
                            f'runmed(x, {k}, endrule = "{R_ENDRULE[ends]}")')

    if method == "savitzky-golay":
        from scipy import signal

        k = _odd_window(window, step_name, method)
        degree = _opt(options, "of_degree", 2)
        if isinstance(degree, bool) or not isinstance(degree, (int, np.integer)) or not 0 <= degree < k:
            raise SimplydataError(f"of_degree= needs a whole number from 0 to {k - 1} (below the window).")
        if n < k:
            raise SimplydataError(f"{step_name}() needs at least {k} readings for this window; there are {n}.")
        out = signal.savgol_filter(x, k, int(degree), mode="interp")
        return SmoothResult(out, f"a Savitzky-Golay filter (a degree-{int(degree)} curve fitted in each window of {k} "
                                 f"readings); the first and last {k // 2} readings use the curve of the first and last "
                                 "window", f"signal::sgolayfilt(x, {int(degree)}, {k})")

    if method == "exponential":
        import pandas as pd

        a, words = _newest_weight(options, step_name)
        out = pd.Series(x).ewm(alpha=a, adjust=False).mean().to_numpy()
        return SmoothResult(out, f"exponential smoothing ({words}): each value is newest_weight x the reading + "
                                 "(1 - newest_weight) x the value before, starting at the first reading",
                            f'stats::filter({_g(a)} * x, {_g(1 - a)}, method = "recursive", init = x[1])')

    if method == "gaussian":
        from scipy import ndimage

        width = _opt(options, "width", 2)
        if isinstance(width, bool) or not isinstance(width, (int, float, np.integer, np.floating)) or width <= 0:
            raise SimplydataError("width= needs a number of readings above 0 (the bell curve's standard deviation).")
        out = ndimage.gaussian_filter1d(x, sigma=float(width), truncate=4.0, mode="reflect")
        radius = int(4.0 * float(width) + 0.5)
        return SmoothResult(out, f"weights from a bell curve with a standard deviation of {_g(width)} readings, cut "
                                 f"{radius} readings each side; at the ends the readings are mirrored",
                            "SciPy ndimage.gaussian_filter1d (in R: dnorm weights on the mirrored readings)")

    if method == "loess":
        return _loess(x, times, _opt(options, "smoothness", None), _opt(options, "interval", None))
    if method in ("lowess", "spline"):
        t = np.arange(1.0, n + 1.0) if times is None else np.asarray(times, dtype=float)
        keep = ~np.isnan(x)
        out = np.full(n, np.nan)
        if method == "lowess":
            from .words.stats import lowess

            frac = _opt(options, "smoothness", 2 / 3)
            if isinstance(frac, bool) or not isinstance(frac, (int, float, np.integer, np.floating)) or not 0 < frac <= 1:
                raise SimplydataError('test_method="lowess" needs smoothness= as the share of readings in each local fit, '
                                      "above 0 and up to 1 (R lowess f=, normally 2/3).")
            tt, yy = t[keep], x[keep]
            xs, fitted = lowess(tt, yy, frac=float(frac), iterations=3, delta=0.01 * float(np.ptp(tt)))
            order = np.argsort(tt, kind="stable")
            back = np.empty_like(fitted)
            back[order] = fitted
            out[keep] = back
            return SmoothResult(out, f"LOWESS (a local straight line through the nearest {_g(frac)} of the readings, "
                                     "with 3 robustness steps)", f"lowess(t, x, f = {_g(frac)})")
        from .table.between import smoothing_spline, smoothness_choice

        smoothness = smoothness_choice(step_name, _opt(options, "smoothness", "auto"))
        curve = smoothing_spline(t[keep], x[keep], smoothness)
        out = np.asarray(curve(t), dtype=float)
        how = "chosen by R (generalised cross-validation)" if smoothness == "auto" else f"lambda {_g(smoothness)}"
        return SmoothResult(out, f"a smoothing spline (smoothness {how})",
                            "smooth.spline(t, x, all.knots = TRUE" + (")" if smoothness == "auto" else f", lambda = {_g(smoothness)})"))

    if method == "whittaker":
        from scipy import signal

        lam = _opt(options, "smoothness", 100)
        if isinstance(lam, bool) or not isinstance(lam, (int, float, np.integer, np.floating)) or lam <= 0:
            raise SimplydataError('test_method="whittaker" needs smoothness= as a number above 0 (bigger is smoother).')
        if not hasattr(signal, "whittaker_henderson"):
            import scipy

            raise SimplydataError(f'test_method="whittaker" needs SciPy 1.17 or newer (this computer has SciPy '
                                  f"{scipy.__version__}): pip install --upgrade scipy. SciPy 1.17 needs Python 3.12 or "
                                  'newer. The other methods work, such as test_method="savitzky-golay".')
        out =np.asarray(signal.whittaker_henderson(x, lamb=float(lam), order=2).x, dtype=float)
        return SmoothResult(out, f"a Whittaker-Henderson smoother (smoothness {_g(lam)}: closeness to the readings "
                                 "against the size of the second differences)",
                            f"solve(diag(n) + {_g(lam)} * crossprod(diff(diag(n), differences = 2)), x)")

    # wiener
    from scipy import signal

    k = _odd_window(window, step_name, method)
    out = np.asarray(signal.wiener(x, mysize=k), dtype=float)
    return SmoothResult(out, f"a Wiener filter over windows of {k} readings (it smooths more where the local spread "
                             "is close to the noise)", "SciPy signal.wiener (no R function; its formula in R by hand)")


LOESS_SPAN = 0.75  # R loess()'s span


def loess_span(smoothness, step_name) -> float:
    """smoothness= of test_method="loess": the share of readings in each local fit (R loess span=, normally 0.75)."""
    if smoothness is None or smoothness == "auto":
        return LOESS_SPAN
    if isinstance(smoothness, bool) or not isinstance(smoothness, (int, float, np.integer, np.floating)) \
            or not 0 < smoothness <= 1:
        raise SimplydataError('test_method="loess" takes smoothness= as the share of readings in each local fit, above 0 '
                              "and up to 1 (R loess span=, normally 0.75).")
    return float(smoothness)


def _loess(x, times, smoothness, interval):
    """R stats::loess(degree = 2) at every reading, with the ends of its confidence band when interval= is given."""
    from .table.lines_r import loess

    n = len(x)
    t = np.arange(1.0, n + 1.0) if times is None else np.asarray(times, dtype=float)
    keep = ~np.isnan(x) & ~np.isnan(t)
    span = loess_span(smoothness, "smooth")
    level = 0.95 if interval is None else interval / 100
    if int(keep.sum()) < 5:
        raise SimplydataError('test_method="loess" needs at least 5 readings.')
    got = loess(t[keep], x[keep], span, t[keep], level)
    out, low, high = np.full(n, np.nan), np.full(n, np.nan), np.full(n, np.nan)
    out[keep] = np.atleast_1d(got["fit"]).astype(float)
    low[keep] = np.atleast_1d(got["low"]).astype(float)
    high[keep] = np.atleast_1d(got["high"]).astype(float)
    share = f"{_g(span)}, R's default" if span == LOESS_SPAN and smoothness in (None, "auto") else _g(span)
    sentence = (f"loess (R stats::loess: a local curve of degree 2 through the nearest share of the readings "
                f"({share}), no robustness steps; not lowess, which fits local straight lines with 3 robustness "
                "steps)")
    return SmoothResult(out, sentence, f"loess(x ~ t, span = {_g(span)}, degree = 2)",
                        low if interval is not None else None, high if interval is not None else None)


TREND_METHODS = ("straight line", "average")
TREND_ALIASES = {"linear": "straight line", "line": "straight line", "constant": "average", "mean": "average"}


def remove_trend(values, method="straight line", breaks=None, step_name="remove_trend"):
    """(values without the trend, sentence, R call) from scipy.signal.detrend."""
    from scipy import signal

    chosen = TREND_ALIASES.get(method.strip().lower(), method.strip().lower()) if isinstance(method, str) else method
    if chosen not in TREND_METHODS:
        raise choice_error(step_name, "test_method", method, list(TREND_METHODS))
    x = np.asarray(values, dtype=float)
    n = len(x)
    if np.isnan(x).any():
        raise SimplydataError(f"{step_name}() needs a value at every place; {int(np.isnan(x).sum())} are empty.")
    if n < 3:
        raise SimplydataError(f"{step_name}() needs at least 3 numbers.")
    if breaks is not None:
        if chosen != "straight line":
            raise SimplydataError('breaks= goes with test_method="straight line".')
        if isinstance(breaks, (int, np.integer)) and not isinstance(breaks, bool):
            breaks = [breaks]
        if not (isinstance(breaks, (list, tuple)) and breaks and all(
                isinstance(b, (int, np.integer)) and not isinstance(b, bool) and 2 <= b <= n - 2 for b in breaks)):
            raise SimplydataError(f"breaks= needs positions from 2 to {n - 2} (counting from 1), such as breaks=[200, "
                                  "500]: a new straight line starts after each.")
        breaks = sorted(set(int(b) for b in breaks))
    out = signal.detrend(x, type="linear" if chosen == "straight line" else "constant", bp=breaks or 0)
    if chosen == "average":
        return out, "took away the average", "x - mean(x)"
    if breaks:
        pieces = [1] + [b + 1 for b in breaks]
        ends = breaks + [n]
        words = ", ".join(f"{a} to {b}" for a, b in zip(pieces, ends))
        return (out, f"took away a separate least-squares straight line from each piece (readings {words}); the "
                     "lines may jump at a break (SciPy detrend; MATLAB and R pracma join them)",
                "residuals(lm(x ~ t)) on each piece")
    return out, "took away the least-squares straight line", "residuals(lm(x ~ seq_along(x)))"
