"""Signals: the spectrum of a series (which repeating cycles it holds and how strong each is).

Every number comes from a package: SciPy's periodogram and Welch estimates, and for uneven times
R lomb::lsp() itself (SciPy's lombscargle gives other numbers). Own code only words the result:
"repeats every" is 1 / frequency. (The share of the variance at each frequency, power x frequency step /
variance, was simplydata's own arithmetic and is no longer given.)

Conventions (said in the word's docstring and tested):
* periodogram: SciPy periodogram(detrend="constant", window="boxcar", scaling="density"): one-sided,
  so the powers times the frequency step add up to the variance (n divisor). R spec.pgram is
  two-sided: SciPy's value = 2 x R spec.pgram(x, taper = 0, detrend = FALSE, fast = FALSE)$spec at
  every frequency but the top (Nyquist) one, which is not doubled; R has no row for frequency 0.
* welch: SciPy welch, pieces of window= readings (default min(256, n)), half overlap, hann window,
  each piece's mean removed, the average of the pieces' periodograms.
* lomb-scargle: R lomb::lsp(y, times = t, type = "frequency", normalize = "standard", ofac = 1).
"""

from __future__ import annotations

import math
import warnings

import numpy as np

from ._errors import SimplydataError, choice_error

METHODS = ("periodogram", "welch", "lomb-scargle")
METHOD_ALIASES = {"lombscargle": "lomb-scargle", "lomb scargle": "lomb-scargle", "lomb": "lomb-scargle",
                  "pgram": "periodogram", "spec.pgram": "periodogram"}
SHOWS = ("power", "decibels", "amplitude")
TOP = 3  # strongest cycles named in the sentence


def _num(x) -> str:
    """3 significant digits without trailing zeros: 5, 0.2, 12, 0.0833."""
    return f"{float(x):.3g}"


def read_method(method, step_name):
    if not isinstance(method, str):
        raise choice_error(step_name, "test_method", method, list(METHODS))
    name = METHOD_ALIASES.get(method.strip().lower(), method.strip().lower())
    if name not in METHODS:
        raise choice_error(step_name, "test_method", method, list(METHODS))
    return name


def _unit_words(unit: str):
    """('per day', 'days') for the sentence: how frequencies and periods are said."""
    if unit == "rows":
        return "per reading", "readings"
    if unit in ("days", "seconds", "months", "quarters", "years"):
        return f"per {unit[:-1]}", unit
    if unit == "time units":
        return "per unit of time", "units of time"
    return f'per unit of "{unit}"', f'units of "{unit}"'


def spectrum(values, time_step=1.0, method="periodogram", window=None, window_shape="hann", show="power",
             times=None, unit="rows", what="the numbers", step_name="spectrum"):
    """dict(frequency, repeats every, value column, share (always None), sentence, method sentence)."""
    from scipy import signal

    x = np.asarray(values, dtype=float)
    n = len(x)
    if n < 4:
        raise SimplydataError(f"{step_name}() needs at least 4 readings; there are {n}.")
    if show not in SHOWS:
        raise choice_error(step_name, "show", show, list(SHOWS))
    fs = 1.0 / time_step
    shares = None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if method == "periodogram":
            if window is not None:
                raise SimplydataError('window= is for test_method="welch"; the periodogram uses every reading at once.')
            freq, density = signal.periodogram(x, fs=fs, detrend="constant", window="boxcar", scaling="density")
            spec = signal.periodogram(x, fs=fs, detrend="constant", window="boxcar", scaling="spectrum")[1]
            r_call = "2 x R spec.pgram(x, taper = 0, detrend = FALSE, fast = FALSE)$spec"
            how = "periodogram (squared size of the Fourier transform, one-sided, scaled so the powers add up to the variance)"
        elif method == "welch":
            pieces = min(256, n) if window is None else window
            if isinstance(pieces, bool) or not isinstance(pieces, (int, np.integer)) or not 4 <= pieces <= n:
                raise SimplydataError(f"window= is the number of readings in each piece: a whole number from 4 to {n}.")
            freq, density = signal.welch(x, fs=fs, window=window_shape, nperseg=int(pieces), noverlap=int(pieces) // 2,
                                         detrend="constant", scaling="density")
            spec = signal.welch(x, fs=fs, window=window_shape, nperseg=int(pieces), noverlap=int(pieces) // 2,
                                detrend="constant", scaling="spectrum")[1]
            r_call = "SciPy signal.welch (the same steps written in R give the same numbers)"
            how = (f"Welch's method (the average periodogram of pieces of {int(pieces)} readings with half overlap and "
                   f"a {window_shape} window)")
        else:
            if show != "power":
                raise SimplydataError('test_method="lomb-scargle" gives a normalised power (0 to 1), so show= can only be '
                                      '"power".')
            freq, density = _lomb_scargle(x, times)
            spec = None
            r_call = 'R lomb::lsp(y, times = t, type = "frequency", normalize = "standard")'
            how = "Lomb-Scargle periodogram (for uneven times; standard normalisation, 0 to 1)"
    if show == "power":
        column, shown = "power", density
    elif show == "decibels":
        column = "power (decibels)"
        with np.errstate(divide="ignore"):
            shown = 10 * np.log10(density)
    else:
        column, shown = "amplitude", np.sqrt(2 * spec)
    per, periods = _unit_words(unit)
    with np.errstate(divide="ignore"):
        repeats = np.where(freq > 0, 1.0 / np.where(freq > 0, freq, 1.0), np.inf)
    sentence = _top_sentence(freq, density, what, per, periods)
    return {"frequency": freq, "repeats every": repeats, column: shown, "share": shares, "column": column,
            "sentence": sentence, "method": f"Method: {how}, as {r_call}."}


def _lomb_scargle(y, times):
    from ._r import r_call

    if times is None:
        raise SimplydataError('test_method="lomb-scargle" needs the times of the readings (sorted_by= or time_points=).')
    out = r_call("l <- lomb::lsp(y, times = t, type = 'frequency', normalize = 'standard', ofac = 1, plot = FALSE); "
                 "list(f = l$scanned, p = l$power)", packages=("lomb",), what="A Lomb-Scargle spectrum",
                 python_note="SciPy lombscargle is similar but scaled differently, so its numbers differ",
                 source="lomb::lsp", y=np.asarray(y, dtype=float), t=np.asarray(times, dtype=float))
    return (np.asarray(out["f"], dtype=float), np.asarray(out["p"], dtype=float))


def strongest_cycles(freq, values, top=TOP):
    """The positions (in freq) of the strongest cycles: the local peaks above frequency 0 (SciPy find_peaks, the
    ends counting as peaks), strongest first, at most top of them. The sentence of find_spectrum_of names them
    and chart.spectrum labels them, so both always show the same cycles."""
    from scipy.signal import find_peaks

    freq, values = np.asarray(freq, dtype=float), np.asarray(values, dtype=float)
    where = np.flatnonzero(freq > 0)
    p = values[where]
    tops, _ = find_peaks(np.concatenate([[-np.inf], p, [-np.inf]]))
    tops = tops - 1
    if not len(tops):
        tops = np.array([int(np.argmax(p))])
    return where[tops[np.argsort(-p[tops], kind="stable")][:top]]


def _top_sentence(freq, power, what, per, periods):
    keep = freq > 0
    f, p = freq[keep], power[keep]
    tops = strongest_cycles(f, p)

    def one(i, first):
        if first:
            return f"has frequency {_num(f[i])} {per} (it repeats every {_num(1 / f[i])} {periods})"
        return f"{_num(f[i])} {per}"

    text = f"The strongest cycle in {what} " + one(tops[0], True)
    if len(tops) > 1:
        text += "; next: " + " and ".join(one(i, False) for i in tops[1:])
    return text + "."


def check_frequency_range(between, step_name):
    if between is None:
        return None
    if (not isinstance(between, (list, tuple)) or len(between) != 2 or
            not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in between)
            or between[0] >= between[1]):
        raise SimplydataError(f"{step_name}() needs between= as two frequencies, low then high, such as between=[1, 30].")
    return float(between[0]), float(between[1])
