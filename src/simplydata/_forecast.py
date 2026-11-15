"""Forecasts, their accuracy, and change points: all run in R itself (simplydata[r]).

Python has no package that gives R's numbers here, so every number comes from R through
simplydata._r.r_call:
* "last value", "same season last time", "average", "straight on": R forecast::naive, snaive, meanf,
  rwf(drift = TRUE), with their own interval formulas;
* "exponential smoothing": R stats::HoltWinters (statsmodels ExponentialSmoothing updates the season
  in another order and gives other numbers), forecast with intervals by forecast::forecast(), which
  uses R's predict(fit, prediction.interval = TRUE);
* "arima": R stats::arima(method = "ML") (statsmodels SARIMAX matches the estimates only to about
  2e-5), forecast by forecast::forecast() (the forecast +/- the normal quantile times predict()'s
  standard error);
* check_on_last= / compare_forecasts: R forecast::accuracy() on the held-back readings (MASE scaled
  by the in-sample error of the seasonal naive forecast);
* the leftover errors: R Box.test(residuals, lag, type = "Ljung-Box", fitdf = number of ARIMA
  estimates), lag as forecast::checkresiduals (2 cycles, or 10, at most a fifth of the readings);
* find_change_points: R changepoint::cpt.mean (PELT) on the readings divided by
  mad(diff(x)) / sqrt(2) (cpt.mean assumes noise with standard deviation 1), or cpt.meanvar.
"""

from __future__ import annotations

import math

import numpy as np

from ._errors import SimplydataError, choice_error

METHODS = ("last value", "same season last time", "average", "straight on", "exponential smoothing", "arima")
METHOD_ALIASES = {
    "naive": "last value", "seasonal naive": "same season last time", "snaive": "same season last time",
    "mean": "average", "meanf": "average", "drift": "straight on", "rwf": "straight on",
    "line from first to last": "straight on",
    "holt-winters": "exponential smoothing", "holt winters": "exponential smoothing",
    "holtwinters": "exponential smoothing", "hw": "exponential smoothing", "sarima": "arima",
}
R_NAME = {"last value": "naive", "same season last time": "snaive", "average": "meanf", "straight on": "drift",
          "exponential smoothing": "hw", "arima": "arima"}
SEASONAL = ("same season last time",)
CHANGES = ("average", "average and spread")
CHANGE_ALIASES = {"mean": "average", "mean and variance": "average and spread", "meanvar": "average and spread"}
PENALTIES = {"mbic": "MBIC", "bic": "BIC", "aic": "AIC", "hannan-quinn": "Hannan-Quinn"}
PENALTY_ALIASES = {"sic": "bic", "hq": "hannan-quinn"}

_R_FORECAST = """
y <- stats::ts(x, frequency = m)
fit <- NULL
f <- switch(method,
  naive = forecast::naive(y, h = h, level = level),
  snaive = forecast::snaive(y, h = h, level = level),
  meanf = forecast::meanf(y, h = h, level = level),
  drift = forecast::rwf(y, h = h, drift = TRUE, level = level),
  hw = { fit <- stats::HoltWinters(y, beta = if (with_trend) NULL else FALSE,
                                   gamma = if (m > 1) NULL else FALSE, seasonal = seasonal)
         forecast::forecast(fit, h = h, level = level) },
  arima = { fit <- stats::arima(y, order = order, seasonal = list(order = sorder, period = m), method = "ML")
            forecast::forecast(fit, h = h, level = level) })
b <- stats::Box.test(stats::residuals(f), lag = box_lag, type = "Ljung-Box", fitdf = fitdf)
out <- list(mean = as.numeric(f$mean), low = as.numeric(f$lower), high = as.numeric(f$upper),
            box = c(unname(b$statistic), b$p.value))
if (method == "hw") {
  out$terms <- c("alpha", "beta", "gamma", "sum of squared errors")
  out$estimates <- c(fit$alpha, if (isFALSE(fit$beta)) NA else fit$beta,
                     if (isFALSE(fit$gamma)) NA else fit$gamma, fit$SSE)
  out$errors <- rep(NA_real_, 4)
}
if (method == "arima") {
  se <- if (length(fit$coef)) sqrt(diag(fit$var.coef)) else numeric(0)
  out$terms <- c(names(fit$coef), "sigma^2", "log-likelihood", "AIC")
  out$estimates <- c(unname(fit$coef), fit$sigma2, fit$loglik, fit$aic)
  out$errors <- c(unname(se), NA, NA, NA)
}
if (!is.null(test)) {
  a <- forecast::accuracy(f, test)
  out$accuracy <- unname(a["Test set", c("MAE", "RMSE", "MAPE", "MASE")])
}
out
"""

_R_CHANGES = """
if (change == "average") {
  s <- stats::mad(diff(x)) / sqrt(2)
  if (!is.finite(s) || s == 0) stop("no_noise")
  found <- changepoint::cpt.mean(x / s, method = "PELT", penalty = penalty)
} else {
  s <- NA_real_
  found <- changepoint::cpt.meanvar(x, method = "PELT", penalty = penalty)
}
ends <- changepoint::cpts(found)
starts <- c(1, ends + 1); ends <- c(ends, length(x))
list(scale = s, starts = starts, ends = ends,
     average = sapply(seq_along(starts), function(i) mean(x[starts[i]:ends[i]])),
     spread = sapply(seq_along(starts), function(i) if (ends[i] > starts[i]) stats::sd(x[starts[i]:ends[i]]) else NA_real_))
"""


def read_method(method, step_name):
    chosen = METHOD_ALIASES.get(method.strip().lower(), method.strip().lower()) if isinstance(method, str) else method
    if chosen not in METHODS:
        raise choice_error(step_name, "method", method, list(METHODS))
    return chosen


def read_whole(value, name, step_name, lowest=1, example="12"):
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < lowest:
        raise SimplydataError(f"{step_name}() needs {name}= as a whole number of at least {lowest}, such as "
                              f"{name}={example}.")
    return int(value)


def read_interval(interval, step_name):
    if isinstance(interval, bool) or not isinstance(interval, (int, float, np.integer, np.floating)) or \
            not 50 <= interval < 100:
        raise SimplydataError(f"{step_name}() needs interval= as a percent from 50 to below 100, such as interval=95.")
    return float(interval)


def read_order(order, name, step_name):
    if order is None:
        return None
    if not (isinstance(order, (list, tuple)) and len(order) == 3 and
            all(isinstance(v, (int, np.integer)) and not isinstance(v, bool) and v >= 0 for v in order)):
        raise SimplydataError(f"{step_name}() needs {name}= as three whole numbers (past values, differences, past "
                              f"errors), such as {name}=(0, 1, 1).")
    return tuple(int(v) for v in order)


def check_options(method, period, n, season, order, seasonal_order, step_name):
    """Friendly errors before R is asked."""
    if method in SEASONAL and period is None:
        raise SimplydataError(f'method="{method}" needs repeats_every= (how many readings make one cycle, such as 12).')
    if season == "multiplied" and method != "exponential smoothing":
        raise SimplydataError('season="multiplied" is for method="exponential smoothing".')
    if method == "arima":
        if order is None:
            raise SimplydataError('method="arima" needs order= : how many past values, differences and past errors, '
                                  "such as order=(0, 1, 1). simplydata does not choose the order for you.")
        if seasonal_order is not None and period is None:
            raise SimplydataError("seasonal_order= needs repeats_every= (how many readings make one cycle).")
    elif order is not None or seasonal_order is not None:
        raise SimplydataError('order= and seasonal_order= are for method="arima".')
    if method == "exponential smoothing" and period is not None and n < 2 * period:
        raise SimplydataError(f"Exponential smoothing with a season needs at least two full cycles ({2 * period} "
                              f"readings); there are {n}.")
    if n < 3:
        raise SimplydataError(f"{step_name}() needs at least 3 readings; there are {n}.")


def box_lag(n, period):
    """forecast::checkresiduals: 2 cycles (or 10 without a season), at most a fifth of the readings."""
    return int(max(1, min(2 * period if period and period > 1 else 10, n // 5)))


def r_forecast(values, period, method, steps, interval, trend=True, season="added", order=None,
               seasonal_order=None, test=None):
    """R's forecast (and its accuracy on test=): dict(mean, low, high, box, terms, estimates, errors, accuracy)."""
    from ._r import r_call

    x = np.asarray(values, dtype=float)
    m = int(period) if period else 1
    fitdf = sum(order or (0, 0, 0)) - (order[1] if order else 0)
    if seasonal_order:
        fitdf += seasonal_order[0] + seasonal_order[2]
    out = r_call(_R_FORECAST, packages=("forecast",), what=f'The forecast by "{method}" (R forecast and stats)',
                 python_note=("statsmodels SARIMAX and ExponentialSmoothing are the Python alternatives; they give "
                              "slightly different numbers" if method in ("arima", "exponential smoothing") else None),
                 source="forecast", x=x, m=float(m), h=float(steps), level=float(interval), method=R_NAME[method],
                 with_trend=bool(trend), seasonal="multiplicative" if season == "multiplied" else "additive",
                 order=[float(v) for v in (order or (0, 0, 0))],
                 sorder=[float(v) for v in (seasonal_order or (0, 0, 0))],
                 box_lag=float(box_lag(int((~np.isnan(x)).sum()), period)), fitdf=float(fitdf),
                 test=None if test is None else np.asarray(test, dtype=float))
    got = {key: np.asarray(out[key], dtype=float) for key in ("mean", "low", "high", "box")}
    for key in ("estimates", "errors", "accuracy"):
        if out.get(key) is not None:
            got[key] = np.asarray(out[key], dtype=float)
    if out.get("terms") is not None:
        got["terms"] = [str(t) for t in np.atleast_1d(out["terms"])]
    return got


def method_words(method, period, trend, season, order, seasonal_order):
    """(name, what it does, R call) for the sentences."""
    if method == "last value":
        return "the last value", "every future step is the last reading", "forecast::naive(x, h)"
    if method == "same season last time":
        return ("the same season last time", f"each future step is the reading one cycle ({period} readings) earlier",
                "forecast::snaive(x, h)")
    if method == "average":
        return "the average", "every future step is the average of all readings", "forecast::meanf(x, h)"
    if method == "straight on":
        return ("straight on", "the straight line from the first to the last reading, carried on",
                "forecast::rwf(x, h, drift = TRUE)")
    if method == "exponential smoothing":
        parts = ["a level"] + (["a trend"] if trend else []) + (
            [f"a season every {period} readings ({'multiplied' if season == 'multiplied' else 'added'})"] if period else [])
        options = ([] if trend else ["beta = FALSE"]) + ([] if period else ["gamma = FALSE"]) + (
            ['seasonal = "multiplicative"'] if season == "multiplied" else [])
        call = "HoltWinters(x" + "".join(", " + o for o in options) + ")"
        return ("exponential smoothing", "Holt-Winters, with " + ", ".join(parts[:-1]) +
                (" and " if len(parts) > 1 else "") + parts[-1],
                f"{call} and forecast::forecast(fit, h), which uses predict(fit, h, prediction.interval = TRUE)")
    p, d, q = order
    seasonal = f", seasonal = list(order = c({', '.join(map(str, seasonal_order))}), period = {period})"         if seasonal_order else ""
    return (f"ARIMA{arima_label(order, seasonal_order, period)}", arima_words(order, seasonal_order, period),
            f'arima(x, order = c({p}, {d}, {q}){seasonal}, method = "ML") and forecast::forecast(fit, h)')


def arima_label(order, seasonal_order, period):
    label = "(" + ",".join(map(str, order)) + ")"
    if seasonal_order:
        label += "(" + ",".join(map(str, seasonal_order)) + f")[{period}]"
    return label


def _count(n, one, many):
    return f"{n} {one if n == 1 else many}"


def arima_words(order, seasonal_order, period):
    """ARIMA(0,1,1)(0,1,1)[12] in words."""
    def part(o, back=""):
        p, d, q = o
        bits = []
        if d:
            bits.append(_count(d, "difference", "differences") + back)
        if p:
            bits.append(_count(p, "past value", "past values") + back)
        if q:
            bits.append(_count(q, "past error", "past errors") + back)
        return " and ".join(bits) if bits else "nothing"
    text = part(order)
    if order[1] == 0 and not (seasonal_order and seasonal_order[1]):
        text += ", with an average"
    if seasonal_order:
        text += f"; for the season, {part(seasonal_order, f' {period} rows back')}"
    return text


def r_change_points(values, change, penalty):
    """R changepoint: dict(scale, starts, ends (positions from 1), average, spread)."""
    from ._r import r_call

    try:
        out = r_call(_R_CHANGES, packages=("changepoint",), what="The search for change points (R changepoint)",
                     source="changepoint", x=np.asarray(values, dtype=float), change=change,
                     penalty=PENALTIES[penalty])
    except SimplydataError as error:
        if "no_noise" in str(error):
            raise SimplydataError("find_change_points() needs readings that vary from one to the next; here the "
                                  "differences are mostly 0.") from None
        raise
    return {"scale": float(np.asarray(out["scale"]).ravel()[0]),
            "starts": np.asarray(out["starts"], dtype=float).astype(int),
            "ends": np.asarray(out["ends"], dtype=float).astype(int),
            "average": np.asarray(out["average"], dtype=float), "spread": np.asarray(out["spread"], dtype=float)}


def read_change(change, step_name):
    chosen = CHANGE_ALIASES.get(change.strip().lower(), change.strip().lower()) if isinstance(change, str) else change
    if chosen not in CHANGES:
        raise choice_error(step_name, "change", change, list(CHANGES))
    return chosen


def read_penalty(penalty, step_name):
    chosen = penalty.strip().lower() if isinstance(penalty, str) else penalty
    chosen = PENALTY_ALIASES.get(chosen, chosen)
    if chosen not in PENALTIES:
        raise choice_error(step_name, "penalty", penalty, list(PENALTIES))
    return chosen


def is_nan(x) -> bool:
    return isinstance(x, float) and math.isnan(x)
