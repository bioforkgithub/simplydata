"""Frequency filters: keep or remove frequencies. Every number comes from SciPy:

* designs: scipy.signal.butter, cheby1, cheby2, ellip, bessel (norm="phase") as second-order sections
  (output="sos": stable at high steepness), iirnotch / iirpeak for one frequency (and_multiples=True: one
  iirnotch at each multiple, as second-order sections; not iircomb, which also removes frequency 0); coefficients
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

METHODS = ("butterworth", "chebyshev", "chebyshev 2", "elliptic", "bessel", "fir", "fir least squares",
           "fir equiripple", "fir frequency sampling")
# The FIR designs (families for 100 %, batches 17-18; plan 2.7 approved by Manish 2026-11-28): SciPy firwin, firls,
# remez, firwin2 (simplydata._filter_design). firwin's weights are not R signal::fir1's (R makes fir1 by frequency
# sampling, so its weights add up to 1.0015 for fir1(100, 0.1)); they are checked against firwin's own formula.
ALIASES = {"butter": "butterworth", "cheby1": "chebyshev", "chebyshev 1": "chebyshev", "cheby2": "chebyshev 2",
           "ellip": "elliptic", "besself": "bessel", "firwin": "fir", "fir1": "fir", "window method": "fir",
           "firls": "fir least squares", "least squares": "fir least squares", "remez": "fir equiripple",
           "equiripple": "fir equiripple", "parks-mcclellan": "fir equiripple", "firpm": "fir equiripple",
           "firwin2": "fir frequency sampling", "fir2": "fir frequency sampling",
           "frequency sampling": "fir frequency sampling"}
R_DESIGN = {"butterworth": "signal::butter({n}, {w}{t})", "chebyshev": "signal::cheby1({n}, {rp}, {w}{t})",
            "chebyshev 2": "signal::cheby2({n}, {rs}, {w}{t})", "elliptic": "signal::ellip({n}, {rp}, {rs}, {w}{t})",
            "bessel": "gsignal::as.Arma(gsignal::bilinear(gsignal::besself({n}, 2 * {fs} * tan(pi * {f} / {fs}){t}), "
                      "T = 1 / {fs}))"}
SCIPY_TYPE = {"low": "lowpass", "high": "highpass", "pass": "bandpass", "stop": "bandstop"}
R_TYPE = {"low": "", "high": ', type = "high"', "pass": ', type = "pass"', "stop": ', type = "stop"'}
NAMES = {"butterworth": "Butterworth", "chebyshev": "Chebyshev (type 1)", "chebyshev 2": "Chebyshev (type 2)",
         "elliptic": "elliptic", "bessel": "Bessel"}


def read_method(method, step_name, single=False):
    """The design asked for; single=True (is_equal_to=) also allows "gammatone"."""
    chosen = ALIASES.get(method.strip().lower(), method.strip().lower()) if isinstance(method, str) else method
    if single and chosen == "gammatone":
        return chosen
    if chosen not in METHODS:
        raise choice_error(step_name, "test_method", method, list(METHODS) + (["gammatone"] if single else []))
    return chosen


def _g(x) -> str:
    return f"{float(x):.4g}"


def design(kind, cutoffs, step, method="butterworth", steepness=4, ripple=0.5, removed_by=40, window=None,
           window_shape="hamming", step_name="keep_each_frequency_that", transition_width=None, find_order_for=None,
           with_least_delay=False):
    """kind: "low", "high", "pass", "stop"; cutoffs in cycles per unit of time. Returns dict(sos or ba,
    words, r_call). window: the number of FIR weights (101 when None); find_order_for={"loss_at": f}: the
    steepness (or number of FIR weights) found by SciPy buttord ... kaiserord (simplydata._filter_design)."""
    from scipy import signal

    from . import _filter_design as fd

    nyquist = 0.5 / step
    cut = np.atleast_1d(np.asarray(cutoffs, dtype=float))
    if (cut <= 0).any() or (cut >= nyquist).any():
        raise SimplydataError(f"The frequencies must lie between 0 and {_g(nyquist)}: the highest frequency readings "
                              f"{_g(step)} apart can show is {_g(nyquist)} per unit of time (half the readings per "
                              "unit of time).")
    if isinstance(steepness, bool) or not isinstance(steepness, (int, np.integer)) or not 1 <= steepness <= 20:
        raise SimplydataError(f"{step_name}() needs steepness= as a whole number from 1 to 20 (the filter order).")
    fir = method in fd.FIR_METHODS
    if transition_width is not None and method not in ("fir least squares", "fir equiripple",
                                                       "fir frequency sampling"):
        raise SimplydataError('transition_width= goes with test_method="fir least squares", "fir equiripple" or '
                              '"fir frequency sampling".')
    if with_least_delay and not fir:
        raise SimplydataError('with_least_delay=True goes with an FIR test_method (such as "fir"): it gives an FIR '
                              "filter the least delay for the same gain.")
    loss_at = None
    if find_order_for is not None:
        if steepness != 4 or window is not None:
            raise SimplydataError("find_order_for= finds the steepness (or the number of FIR weights) itself: leave "
                                  "out steepness= and how_many_weights=.")
        loss_at = fd.read_order_request(find_order_for, kind, cut, nyquist)
    if fir:
        found = ""
        beta = None
        if loss_at is not None:
            if method != "fir":
                raise SimplydataError('find_order_for= with an FIR filter works with test_method="fir" (the Kaiser '
                                      "window method, SciPy kaiserord).")
            window, beta, cut, found = fd.kaiser_order(kind, cut, loss_at, step, removed_by)
        weights = fd.check_weights(window, method)
        made = fd.design_fir(kind, cut, step, method, weights, window_shape, transition_width, beta)
        b, a = made["ba"]
        words = made["words"] + (f"; {found}" if found else "")
        call = f"SciPy {made['scipy']}"
        if loss_at is not None:
            call = f"SciPy signal.kaiserord, then {made['scipy']}"
        if with_least_delay:
            b = fd.least_delay(b)
            words += "; the least delay for the same gain (minimum phase)"
            call += ', then signal.minimum_phase(method="homomorphic", half=False)'
        elif method == "fir least squares":
            call += f" (as R gsignal::firls({weights - 1}, edges / {_g(nyquist)}, gains))"
        elif method == "fir equiripple":
            call += f" (as R signal::remez({weights - 1}, edges / {_g(nyquist)}, gains))"
        return dict(ba=(b, a), words=words, r_call=call, scipy_only=True)
    if window is not None:
        fd.check_weights(window, method)
    n, cut_used, found = int(steepness), cut, ""
    if loss_at is not None:
        n, cut_used, found = fd.find_order(method, kind, cut, loss_at, step, ripple, removed_by)
        if n > 20:
            raise SimplydataError(f"That needs steepness {n} (SciPy {fd.ORDER_FINDERS[method]}), more than 20: ask for "
                                  'less (a smaller removed_by=, a "loss_at" further from the cutoff) or use '
                                  'test_method="elliptic", the steepest design.')
    w = cut_used / nyquist
    w_r = _g(w[0]) if len(w) == 1 else f"c({_g(w[0])}, {_g(w[1])})"
    args = dict(N=n, Wn=float(cut_used[0]) if len(cut_used) == 1 else cut_used, btype=SCIPY_TYPE[kind], output="sos",
                fs=1 / step)
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
    f_r = (_g(cut_used[0]) if len(cut_used) == 1 else  # cutoffs in cycles per unit of time
           f"c({_g(cut_used[0])}, {_g(cut_used[1])})")
    words = f"{NAMES[method]} filter, " + (found if found else f"steepness {n}")
    return dict(sos=sos, words=words, steepness=n, losses=(float(ripple), float(removed_by)) if found else None,
                r_call=R_DESIGN[method].format(n=n, w=w_r, t=R_TYPE[kind], rp=_g(ripple), rs=_g(removed_by),
                                               fs=_g(1 / step), f=f_r))


def design_single(keep, frequency, step, width=1.0, and_multiples=False, step_name="remove_each_frequency_that"):
    """One frequency: iirnotch (remove), iirnotch at each multiple (remove with its multiples) or iirpeak (keep)."""
    from scipy import signal

    nyquist = 0.5 / step
    f = float(frequency)
    if not 0 < f < nyquist:
        raise SimplydataError(f"is_equal_to= must lie between 0 and {_g(nyquist)} (half the readings per unit of time).")
    if isinstance(width, bool) or not isinstance(width, (int, float, np.integer, np.floating)) or width <= 0:
        raise SimplydataError("width= needs a number above 0: how wide the removed (or kept) band is, in frequency.")
    quality = f / float(width)
    if and_multiples:
        if keep:
            raise SimplydataError("and_multiples= goes with remove_each_frequency_that(is_equal_to=...).")
        return _notches_at_multiples(f, step, float(width))
    elif keep:
        b, a = signal.iirpeak(f, quality, fs=1 / step)
        words, call = f"peak filter at {_g(f)} (width {_g(width)})", "SciPy signal.iirpeak"
    else:
        b, a = signal.iirnotch(f, quality, fs=1 / step)
        words, call = f"notch filter at {_g(f)} (width {_g(width)})", "SciPy signal.iirnotch"
    return dict(ba=(b, a), words=words, r_call=call, scipy_only=True)


def _notches_at_multiples(f, step, width):
    """and_multiples=True: one SciPy iirnotch at f and at each multiple of f below half the readings per unit of
    time, each as one second-order section, run one after the other (sosfiltfilt / sosfilt).

    Not SciPy iircomb: its notching comb puts a notch at frequency 0 too (pass_zero=False, the default), so it
    also removes the average; pass_zero=True moves the notches to the odd multiples of f / 2 instead (SciPy
    iircomb documentation). Each notch has the same width, as the notches of a comb (quality = frequency / width).
    """
    from scipy import signal

    fs = 1 / step
    nyquist = 0.5 * fs
    count = int(np.floor(nyquist / f))
    multiples = [k * f for k in range(1, count + 1)]
    at_top = bool(np.isclose(multiples[-1], nyquist, rtol=1e-12, atol=0))
    if at_top:  # iirnotch needs a frequency below half the readings per unit of time
        multiples = multiples[:-1]
    sections = []
    for m in multiples:
        b, a = signal.iirnotch(m, m / width, fs=fs)
        sections.append(np.concatenate([b, a]))
    shown = (f"{_g(multiples[0])}" if len(multiples) == 1 else
             f"{_g(multiples[0])}, {_g(multiples[1])}" + (" ... " if len(multiples) > 3 else ", ") + _g(multiples[-1]))
    several = len(multiples) != 1
    words = (f"{len(multiples)} notch filter{'s' if several else ''} at {shown} (width {_g(width)}"
             f"{' each' if several else ''}); the average (frequency 0) stays")
    if at_top:
        words += (f"; the multiple at {_g(nyquist)}, half the readings per unit of time, cannot have a notch (SciPy "
                  "iirnotch needs a frequency below it), so it stays too")
    return dict(sos=np.vstack(sections), words=words, r_call="SciPy signal.iirnotch at each multiple",
                scipy_only=True)


def apply(values, made, both_ways=True, start_from="rest"):
    """The filtered values: forwards and backwards (both_ways) or forwards, from rest or (start_from="first
    value", both_ways=False only) in the steady state for the first value: SciPy sosfilt_zi / lfilter_zi times the
    first reading, as R gsignal::filter_zi."""
    from scipy import signal

    x = np.asarray(values, dtype=float)
    if np.isnan(x).any():
        raise SimplydataError(f"Filtering needs a value at every step, but {int(np.isnan(x).sum())} are empty. Fill "
                              'them first (with_the="line between neighbours").')
    steady = start_from == "first value"
    if "sos" in made:
        sos = made["sos"]
        if both_ways:
            pad = 3 * (2 * len(sos) + 1 - min((sos[:, 2] == 0).sum(), (sos[:, 5] == 0).sum()))
            if len(x) <= pad:
                raise SimplydataError(f"Filtering both ways needs more than {pad} readings for this steepness; "
                                      f"there are {len(x)}. Use a smaller steepness= or both_ways=False.")
            return signal.sosfiltfilt(sos, x)
        if steady:
            return signal.sosfilt(sos, x, zi=signal.sosfilt_zi(sos) * x[0])[0]
        return signal.sosfilt(sos, x)
    b, a = made["ba"]
    if both_ways:
        pad = 3 * max(len(a), len(b))
        if len(x) <= pad:
            raise SimplydataError(f"Filtering both ways needs more than {pad} readings; there are {len(x)}.")
        return signal.filtfilt(b, a, x)
    if steady:
        return signal.lfilter(b, a, x, zi=signal.lfilter_zi(b, a) * x[0])[0]
    return signal.lfilter(b, a, x)


START_FROM = ("rest", "first value")


def read_start(start_from, both_ways, step_name):
    """start_from= "rest" (the default) or "first value" (with both_ways=False)."""
    if start_from not in START_FROM:
        raise choice_error(step_name, "start_from", start_from, list(START_FROM))
    if start_from == "first value" and both_ways:
        raise SimplydataError('start_from="first value" goes with both_ways=False: run both ways, the filter already '
                              "starts in its steady state at each end (SciPy's padding).")
    return start_from


def coefficients(made):
    """(b, a) of the whole filter (sos2tf for second-order sections), as long as each other."""
    from scipy import signal

    if "sos" in made:
        return signal.sos2tf(made["sos"])
    b, a = (np.asarray(c, dtype=float) for c in made["ba"])
    size = max(len(b), len(a))  # powers of 1/z: zeros at the end change nothing, and both read as powers of z
    return np.concatenate([b, np.zeros(size - len(b))]), np.concatenate([a, np.zeros(size - len(a))])
