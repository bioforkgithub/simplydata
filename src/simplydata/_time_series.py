"""Time series: correlation of a series with its own past (autocorrelation), with a noise band and
the Ljung-Box test.

Every number comes from statsmodels, with the options that give R's numbers:
* correlation: statsmodels acf(x, nlags, adjusted=False, fft=False) = R acf(x) (divides by n);
* partial: statsmodels pacf(x, nlags, method="ywm") = R pacf(x) (statsmodels' default "yw" differs);
* covariance: statsmodels acovf(x, adjusted=False) = R acf(x, type = "covariance");
* band="bartlett": statsmodels acf(alpha=0.05) Bartlett intervals = R plot.acf(ci.type = "ma");
* Ljung-Box: statsmodels acorr_ljungbox = R Box.test(x, lag, type = "Ljung-Box").
The white-noise band is +/- qnorm(0.975) / sqrt(n), the dashed lines of R plot.acf (display
arithmetic). The default number of rows back is R's: floor(10 * log10(n)), at most n - 1.
"""

from __future__ import annotations

import math
import warnings

import numpy as np

from ._errors import SimplydataError, choice_error

SHOWS = ("correlation", "partial", "covariance")
BANDS = ("white noise", "bartlett")


def default_rows_back(n: int) -> int:
    """R acf's lag.max: floor(10 * log10(n)), at most n - 1."""
    return int(min(math.floor(10 * math.log10(n)), n - 1))


def read_rows_back(rows_back, n, step_name):
    if rows_back is None:
        return default_rows_back(n)
    if isinstance(rows_back, bool) or not isinstance(rows_back, (int, np.integer)) or not 1 <= rows_back <= n - 1:
        raise SimplydataError(f"{step_name}() needs rows_back= as a whole number from 1 to {n - 1} (the number "
                              "of readings minus 1).")
    return int(rows_back)


def autocorrelation(values, rows_back=None, show="correlation", band="white noise", step_name="autocorrelation_of"):
    """dict(rows back, values, column, band low/high, outside, ljung_box (stat, p), k, sentence pieces)."""
    from scipy import stats
    from statsmodels.stats.diagnostic import acorr_ljungbox
    from statsmodels.tsa.stattools import acf, acovf, pacf

    if show not in SHOWS:
        raise choice_error(step_name, "show", show, list(SHOWS))
    if band not in BANDS:
        raise choice_error(step_name, "band", band, list(BANDS))
    if band == "bartlett" and show != "correlation":
        raise SimplydataError('band="bartlett" is for show="correlation"; partial correlations use the '
                              'white-noise band.')
    x = np.asarray(values, dtype=float)
    n = len(x)
    if n < 4:
        raise SimplydataError(f"{step_name}() needs at least 4 readings; there are {n}.")
    if np.ptp(x) == 0:
        raise SimplydataError(f"{step_name}() needs readings that change; every value is the same.")
    k = read_rows_back(rows_back, n, step_name)
    if show == "partial" and k >= n // 2:
        raise SimplydataError(f'show="partial" needs rows_back= below half the readings ({n // 2}).')
    lags = np.arange(1, k + 1)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if show == "correlation":
            if band == "bartlett":
                values_all, confint = acf(x, nlags=k, adjusted=False, fft=False, alpha=0.05, bartlett_confint=True)
                half = (confint[:, 1] - values_all)[1:]
            else:
                values_all = acf(x, nlags=k, adjusted=False, fft=False)
                half = np.full(k, stats.norm.ppf(0.975) / math.sqrt(n))
            shown, column = values_all[1:], "correlation"
        elif show == "partial":
            shown = pacf(x, nlags=k, method="ywm")[1:]
            half, column = np.full(k, stats.norm.ppf(0.975) / math.sqrt(n)), "partial correlation"
        else:
            shown = acovf(x, adjusted=False, fft=False, nlag=k)[1:]
            half, column = None, "covariance"
        box = acorr_ljungbox(x, lags=[k], return_df=True)
    stat, p = float(box["lb_stat"].iloc[0]), float(box["lb_pvalue"].iloc[0])
    low = -half if half is not None else np.full(k, np.nan)
    high = half if half is not None else np.full(k, np.nan)
    outside = (np.abs(shown) > half) if half is not None else np.zeros(k, dtype=bool)
    return dict(rows_back=lags, values=np.asarray(shown, dtype=float), column=column, low=low, high=high,
                outside=outside, ljung_box=(stat, p), k=k, n=n, half=half)


def sentence(result, what, show, band):
    """The plain sentence about one series' autocorrelation."""
    from .table.stat_tests import _num
    from .table.summaries import _p_words

    values, lags, k = result["values"], result["rows_back"], result["k"]
    stat, p = result["ljung_box"]
    if show == "covariance":
        return (f"{what}: covariance with itself 1 to {k} rows back; Ljung-Box test up to {k} rows back: "
                f"{_p_words(p)}.")
    best = int(np.argmax(values))
    word = "correlation" if show == "correlation" else "partial correlation"
    text = f"{what} is most like itself {lags[best]} row{'s' if lags[best] != 1 else ''} back ({word} {_num(values[best])})"
    if lags[best] > 1 and values[best] > values[best - 1]:
        text += f": a pattern that repeats about every {lags[best]} rows"
    count = int(result["outside"].sum())
    band_words = (f"+/- {_num(result['half'][0])}" if band == "white noise" else "Bartlett's band, wider further back")
    text += (f". {count} of the {k} {word}s are outside the band expected from random noise ({band_words}). "
             f"Ljung-Box test up to {k} rows back: {_p_words(p)}.")
    return text


def method_sentence(show, band, k):
    call = {"correlation": f"acf(x, lag.max = {k})", "partial": f"pacf(x, lag.max = {k})",
            "covariance": f'acf(x, lag.max = {k}, type = "covariance")'}[show]
    what = {"correlation": "correlation of the column with itself", "partial": "partial correlation (each "
            "rows back with the shorter ones held fixed)", "covariance": "covariance of the column with itself"}[show]
    band_words = "" if show == "covariance" else (
        "; band +/- 1.96 / sqrt(n), as the dashed lines of R plot.acf" if band == "white noise"
        else '; Bartlett band, as R plot(acf(x), ci.type = "ma")')
    return (f"Method: {what} 1 to {k} rows back, as R {call} (statsmodels){band_words}; Ljung-Box as R "
            f'Box.test(x, lag = {k}, type = "Ljung-Box").')
