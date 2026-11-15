"""Frequency filters: keep or remove frequencies. Every number comes from SciPy:

* designs: scipy.signal.butter, cheby1, cheby2, ellip, bessel (norm="phase") as second-order sections
  (output="sos": stable at high steepness), iirnotch / iircomb / iirpeak for one frequency; coefficients
  for printing come from sos2tf. butter, cheby1 and cheby2 match R signal to 1e-9; ellip to about 2e-6
  (R signal solves the elliptic degree equation less precisely); bessel matches R gsignal::besself (an
  analog design) turned digital by gsignal::bilinear, with the cutoff pre-warped as SciPy does:
  w = 2 * fs * tan(pi * f / fs) radians per unit of time (to 1e-12);
* both_ways=True: sosfiltfilt (filtfilt for FIR): forwards then backwards, so nothing moves in time.
  SciPy's ends rule: the series is extended at each end by an odd reflection of 3 x (filter length)
  readings and the filter starts in its steady state (as MATLAB filtfilt). R signal::filtfilt pads only
  with zeros and starts from rest, so the first and last readings differ; the middle agrees;
* both_ways=False: sosfilt / lfilter from rest (what a live instrument does), as R signal::filter.
"""

from __future__ import annotations

import numpy as np

from ._errors import SimplydataError, choice_error

METHODS = ("butterworth", "chebyshev", "chebyshev 2", "elliptic", "bessel")
# "fir" (scipy.signal.firwin) is built but not offered: its weights differ from R signal::fir1 (R's add up
# to 1.0015, SciPy's to 1), so the owner decides which to follow before it becomes a choice.
ALIASES = {"butter": "butterworth", "cheby1": "chebyshev", "chebyshev 1": "chebyshev", "cheby2": "chebyshev 2",
           "ellip": "elliptic", "besself": "bessel", "firwin": "fir", "fir1": "fir"}
R_DESIGN = {"butterworth": "signal::butter({n}, {w}{t})", "chebyshev": "signal::cheby1({n}, {rp}, {w}{t})",
            "chebyshev 2": "signal::cheby2({n}, {rs}, {w}{t})", "elliptic": "signal::ellip({n}, {rp}, {rs}, {w}{t})",
            "bessel": "gsignal::as.Arma(gsignal::bilinear(gsignal::besself({n}, 2 * {fs} * tan(pi * {f} / {fs}){t}), "
                      "T = 1 / {fs}))",
            "fir": "signal::fir1({m}, {w}{t})"}
SCIPY_TYPE = {"low": "lowpass", "high": "highpass", "pass": "bandpass", "stop": "bandstop"}
R_TYPE = {"low": "", "high": ', type = "high"', "pass": ', type = "pass"', "stop": ', type = "stop"'}
NAMES = {"butterworth": "Butterworth", "chebyshev": "Chebyshev (type 1)", "chebyshev 2": "Chebyshev (type 2)",
         "elliptic": "elliptic", "bessel": "Bessel", "fir": "FIR (windowed)"}


def read_method(method, step_name):
    chosen = ALIASES.get(method.strip().lower(), method.strip().lower()) if isinstance(method, str) else method
    if chosen == "fir":
        raise SimplydataError('method="fir" is not ready: SciPy firwin and R signal::fir1 give different weights. '
                              'Use method="butterworth" (or another listed method).')
    if chosen not in METHODS:
        raise choice_error(step_name, "method", method, list(METHODS))
    return chosen


def _g(x) -> str:
    return f"{float(x):.4g}"


def design(kind, cutoffs, step, method="butterworth", steepness=4, ripple=0.5, removed_by=40, window=101,
           window_shape="hamming", step_name="keep_frequencies"):
    """kind: "low", "high", "pass", "stop"; cutoffs in cycles per unit of time. Returns dict(sos or ba,
    words, r_call)."""
    from scipy import signal

    nyquist = 0.5 / step
    cut = np.atleast_1d(np.asarray(cutoffs, dtype=float))
    if (cut <= 0).any() or (cut >= nyquist).any():
        raise SimplydataError(f"The frequencies must lie between 0 and {_g(nyquist)}: the highest frequency readings "
                              f"{_g(step)} apart can show is {_g(nyquist)} per unit of time (half the readings per "
                              "unit of time).")
    if isinstance(steepness, bool) or not isinstance(steepness, (int, np.integer)) or not 1 <= steepness <= 20:
        raise SimplydataError(f"{step_name}() needs steepness= as a whole number from 1 to 20 (the filter order).")
    w = cut / nyquist
    w_r = _g(w[0]) if len(w) == 1 else f"c({_g(w[0])}, {_g(w[1])})"
    if method == "fir":
        if isinstance(window, bool) or not isinstance(window, (int, np.integer)) or window < 3 or window % 2 == 0:
            raise SimplydataError('method="fir" needs window= as an odd number of weights, such as window=101.')
        taps = signal.firwin(int(window), float(cut[0]) if len(cut) == 1 else cut, window=window_shape, pass_zero=kind in ("low", "stop"), fs=1 / step)
        return dict(ba=(taps, np.array([1.0])), words=f"FIR filter with {int(window)} weights ({window_shape} window)",
                    r_call=R_DESIGN["fir"].format(m=int(window) - 1, w=w_r, t=R_TYPE[kind]))
    args = dict(N=int(steepness), Wn=float(cut[0]) if len(cut) == 1 else cut, btype=SCIPY_TYPE[kind], output="sos", fs=1 / step)
    if method == "butterworth":
        sos = signal.butter(**args)
    elif method == "chebyshev":
        sos = signal.cheby1(rp=float(ripple), **args)
    elif method == "chebyshev 2":
        sos = signal.cheby2(rs=float(removed_by), **args)
    elif method == "elliptic":
        sos = signal.ellip(rp=float(ripple), rs=float(removed_by), **args)
    else:
        sos = signal.bessel(norm="phase", **args)
    f_r = _g(cut[0]) if len(cut) == 1 else f"c({_g(cut[0])}, {_g(cut[1])})"  # cutoffs in cycles per unit of time
    return dict(sos=sos, words=f"{NAMES[method]} filter, steepness {int(steepness)}",
                r_call=R_DESIGN[method].format(n=int(steepness), w=w_r, t=R_TYPE[kind], rp=_g(ripple),
                                               rs=_g(removed_by), fs=_g(1 / step), f=f_r))


def design_single(keep, frequency, step, width=1.0, and_multiples=False, step_name="remove_frequencies"):
    """One frequency: iirnotch (remove), iircomb (remove with its multiples) or iirpeak (keep)."""
    from scipy import signal

    nyquist = 0.5 / step
    f = float(frequency)
    if not 0 < f < nyquist:
        raise SimplydataError(f"equal_to= must lie between 0 and {_g(nyquist)} (half the readings per unit of time).")
    if isinstance(width, bool) or not isinstance(width, (int, float, np.integer, np.floating)) or width <= 0:
        raise SimplydataError("width= needs a number above 0: how wide the removed (or kept) band is, in frequency.")
    quality = f / float(width)
    if and_multiples:
        if keep:
            raise SimplydataError("and_multiples= goes with remove_frequencies(equal_to=...).")
        fs = 1 / step
        if abs(fs / f - round(fs / f)) > 1e-9:
            raise SimplydataError("and_multiples=True needs a frequency that divides the readings per unit of time "
                                  "a whole number of times.")
        b, a = signal.iircomb(f, quality, ftype="notch", fs=fs)
        words, call = f"comb filter at {_g(f)} and its multiples (width {_g(width)})", "SciPy signal.iircomb"
    elif keep:
        b, a = signal.iirpeak(f, quality, fs=1 / step)
        words, call = f"peak filter at {_g(f)} (width {_g(width)})", "SciPy signal.iirpeak"
    else:
        b, a = signal.iirnotch(f, quality, fs=1 / step)
        words, call = f"notch filter at {_g(f)} (width {_g(width)})", "SciPy signal.iirnotch"
    return dict(ba=(b, a), words=words, r_call=call)


def apply(values, made, both_ways=True):
    """The filtered values: forwards and backwards (both_ways) or forwards from rest."""
    from scipy import signal

    x = np.asarray(values, dtype=float)
    if np.isnan(x).any():
        raise SimplydataError(f"Filtering needs a value at every step, but {int(np.isnan(x).sum())} are empty. Fill "
                              'them first (with_the="line between neighbours").')
    if "sos" in made:
        sos = made["sos"]
        if both_ways:
            pad = 3 * (2 * len(sos) + 1 - min((sos[:, 2] == 0).sum(), (sos[:, 5] == 0).sum()))
            if len(x) <= pad:
                raise SimplydataError(f"Filtering both ways needs more than {pad} readings for this steepness; "
                                      f"there are {len(x)}. Use a smaller steepness= or both_ways=False.")
            return signal.sosfiltfilt(sos, x)
        return signal.sosfilt(sos, x)
    b, a = made["ba"]
    if both_ways:
        pad = 3 * max(len(a), len(b))
        if len(x) <= pad:
            raise SimplydataError(f"Filtering both ways needs more than {pad} readings; there are {len(x)}.")
        return signal.filtfilt(b, a, x)
    return signal.lfilter(b, a, x)


def coefficients(made):
    """(b, a) of the whole filter (sos2tf for second-order sections)."""
    from scipy import signal

    if "sos" in made:
        return signal.sos2tf(made["sos"])
    return made["ba"]
