"""Filter design for 100 % of scipy.signal (families for 100 %, batches 17-18, plan section 2.7).

Every number comes from SciPy; own code only turns plain options into SciPy's arguments:

* FIR filters (test_method="fir", "fir least squares", "fir equiripple", "fir frequency sampling"):
  scipy.signal.firwin, firls, remez and firwin2. The band edges of least squares and equiripple are the cutoff
  plus and minus half of transition_width= (the cutoff in the middle of the change from kept to removed, as
  SciPy kaiserord's documentation puts it). firls matches R gsignal::firls and remez R signal::remez (to 1e-12);
  firwin2 matches R gsignal::fir2 when both use the same frequency grid.
* find_order_for={"loss_at": f}: the smallest steepness (filter order) that keeps the loss in the kept band
  within ripple= decibels and removes at least removed_by= decibels from frequency f on: SciPy buttord,
  cheb1ord, cheb2ord and ellipord (as R gsignal::buttord ...), and kaiserord for test_method="fir" (the Kaiser
  window method: kaiser_beta inside it; the window is ("kaiser", beta)).
* analog=True (sdata.frequency_filter only): the continuous filter of SciPy butter, cheby1, cheby2, ellip and
  bessel with analog=True; SciPy builds it from the prototypes buttap, cheb1ap, cheb2ap, ellipap, besselap moved
  to the cutoff by lp2lp, lp2hp, lp2bp or lp2bs (the _zpk forms), at 2 pi x the cutoff in radians per unit of time.
* with_least_delay=True: SciPy minimum_phase(method="homomorphic", half=False): the same gain at each frequency,
  the least delay (FIR only).
* test_method="gammatone" (keep one frequency): SciPy gammatone(f, "iir", fs=...).
"""

from __future__ import annotations

import numpy as np

from ._errors import SimplydataError

FIR_METHODS = ("fir", "fir least squares", "fir equiripple", "fir frequency sampling")
FIR_NAMES = {"fir": "FIR (window method)", "fir least squares": "FIR (least squares)",
             "fir equiripple": "FIR (equiripple, Parks-McClellan)",
             "fir frequency sampling": "FIR (frequency sampling)"}
FIR_SCIPY = {"fir": "firwin", "fir least squares": "firls", "fir equiripple": "remez",
             "fir frequency sampling": "firwin2"}
ORDER_FINDERS = {"butterworth": "buttord", "chebyshev": "cheb1ord", "chebyshev 2": "cheb2ord", "elliptic": "ellipord",
                 "fir": "kaiserord"}
DEFAULT_WEIGHTS = 101


def _g(x) -> str:
    return f"{float(x):.4g}"


def check_weights(how_many_weights, method):
    """The number of FIR weights (odd, 3 or more); 101 when not given."""
    if how_many_weights is None:
        return DEFAULT_WEIGHTS
    if method not in FIR_METHODS:
        raise SimplydataError("how_many_weights= goes with an FIR test_method (\"fir\", \"fir least squares\", \"fir "
                              "equiripple\" or \"fir frequency sampling\"); steepness= sets the other filters.")
    if (isinstance(how_many_weights, bool) or not isinstance(how_many_weights, (int, np.integer))
            or how_many_weights < 3 or how_many_weights % 2 == 0):
        raise SimplydataError("how_many_weights= needs an odd whole number of 3 or more, such as how_many_weights=101 "
                              "(an odd number keeps the filter symmetric, so it works for every kind of band).")
    return int(how_many_weights)


def _edges(kind, cut, width, nyquist, method):
    """Band edges (cutoff -/+ width / 2) and the wanted gain at each edge, for firls, remez and firwin2 (for
    firwin2 without a width: a jump at each cutoff, the cutoff given twice, as SciPy firwin2 allows)."""
    if width is None and method == "fir frequency sampling":
        width = 0.0
    elif width is None:
        raise SimplydataError(f'test_method="{method}" needs transition_width=: how wide the change from kept to '
                              "removed is, in frequency (the cutoff sits in its middle), such as "
                              "transition_width=2.")
    if isinstance(width, bool) or not isinstance(width, (int, float, np.integer, np.floating)) or width < 0 or (
            width == 0 and method != "fir frequency sampling"):
        raise SimplydataError("transition_width= needs a number above 0 (a frequency).")
    half = float(width) / 2
    inner = []
    for c in cut:
        inner += [c - half, c + half]
    edges = [0.0] + inner + [nyquist]
    if any(b < a or (b == a and half > 0) for a, b in zip(edges, edges[1:])) or edges[1] <= 0 or edges[-2] >= nyquist:
        raise SimplydataError(f"transition_width={_g(width)} is too wide: the bands from each cutoff minus and plus "
                              f"half of it must stay apart and between 0 and {_g(nyquist)}.")
    first = 1.0 if kind in ("low", "stop") else 0.0
    gains = []
    for i in range(len(edges) // 2):
        on = first if i % 2 == 0 else 1.0 - first
        gains.append(on)
    return edges, gains


def design_fir(kind, cut, step, method, how_many_weights, window_shape, transition_width, kaiser_beta=None):
    """dict(ba, words, scipy) of an FIR design (cut: cutoffs in cycles per unit of time)."""
    from scipy import signal

    fs = 1.0 / step
    nyquist = 0.5 * fs
    n = int(how_many_weights)
    cutoff = float(cut[0]) if len(cut) == 1 else [float(c) for c in cut]
    if method == "fir":
        window = ("kaiser", float(kaiser_beta)) if kaiser_beta is not None else window_shape
        try:
            taps = signal.firwin(n, cutoff, window=window, pass_zero=kind in ("low", "stop"), fs=fs)
        except (ValueError, TypeError) as error:
            raise SimplydataError(f"SciPy firwin could not make this filter ({error}).") from None
        shown = f"Kaiser window, beta {kaiser_beta:.4g}" if kaiser_beta is not None else f"{window_shape} window"
        call = (f"signal.firwin({n}, {cutoff!r}, window={window!r}, pass_zero={kind in ('low', 'stop')}, fs={_g(fs)})")
        words = f"{FIR_NAMES[method]}, {n} weights ({shown})"
    else:
        edges, gains = _edges(kind, list(map(float, cut)), transition_width, nyquist, method)
        if method == "fir least squares":
            desired = [g for g in gains for _ in (0, 1)]
            taps = signal.firls(n, edges, desired, fs=fs)
            call = f"signal.firls({n}, {[_g(e) for e in edges]}, {desired}, fs={_g(fs)})"
        elif method == "fir equiripple":
            try:
                taps = signal.remez(n, edges, gains, fs=fs)
            except ValueError as error:
                raise SimplydataError(f"SciPy remez could not make this filter ({error}).") from None
            call = f"signal.remez({n}, {[_g(e) for e in edges]}, {gains}, fs={_g(fs)})"
        else:
            desired = [g for g in gains for _ in (0, 1)]
            taps = signal.firwin2(n, edges, desired, window=window_shape, fs=fs)
            call = f"signal.firwin2({n}, {[_g(e) for e in edges]}, {desired}, window={window_shape!r}, fs={_g(fs)})"
        words = f"{FIR_NAMES[method]}, {n} weights, " + (f"transition width {_g(transition_width)}"
                                                           if transition_width is not None else "a jump at the cutoff")
    return dict(ba=(np.asarray(taps, dtype=float), np.array([1.0])), words=words, scipy=call)


def read_order_request(find_order_for, kind, cut, nyquist, analog=False):
    """The frequency (or two) where removed_by= must be reached, checked against the kind of band."""
    if not isinstance(find_order_for, dict) or set(find_order_for) != {"loss_at"}:
        raise SimplydataError('find_order_for= needs a dict with "loss_at": the frequency from which at least '
                              'removed_by= decibels are removed, such as find_order_for={"loss_at": 20}.')
    at = find_order_for["loss_at"]
    values = np.atleast_1d(np.asarray(at, dtype=float))
    if len(values) != len(cut):
        raise SimplydataError(f'find_order_for={{"loss_at": ...}} needs {len(cut)} frequenc'
                              f'{"y" if len(cut) == 1 else "ies"}, one for each cutoff.')
    top = np.inf if analog else nyquist
    if (values <= 0).any() or (values >= top).any():
        raise SimplydataError(f'"loss_at" must lie between 0 and {_g(top)}.')
    if kind == "low" and not values[0] > cut[0]:
        raise SimplydataError('For a filter that keeps the low frequencies, "loss_at" must be above the cutoff.')
    if kind == "high" and not values[0] < cut[0]:
        raise SimplydataError('For a filter that keeps the high frequencies, "loss_at" must be below the cutoff.')
    if kind == "pass" and not (values[0] < cut[0] and values[1] > cut[1]):
        raise SimplydataError('For a band kept, "loss_at" needs a frequency below the band and one above it.')
    if kind == "stop" and not (cut[0] < values[0] < values[1] < cut[1]):
        raise SimplydataError('For a band removed, "loss_at" needs two frequencies inside the band, the lower first.')
    return values


def find_order(method, kind, cut, loss_at, step, ripple, removed_by, analog=False):
    """(steepness, natural frequencies, words): SciPy buttord / cheb1ord / cheb2ord / ellipord. For analog=True the
    frequencies are cycles per unit of time, handed to SciPy in radians per unit of time."""
    from scipy import signal

    if method not in ORDER_FINDERS or method == "fir":
        raise SimplydataError(f'find_order_for= works with test_method="butterworth", "chebyshev", "chebyshev 2", '
                              f'"elliptic" and "fir" (Kaiser window); not with "{method}".')
    finder = getattr(signal, ORDER_FINDERS[method])
    wp = cut if len(cut) > 1 else cut[0]
    ws = loss_at if len(loss_at) > 1 else loss_at[0]
    if analog:
        n, wn = finder(2 * np.pi * np.asarray(wp), 2 * np.pi * np.asarray(ws), float(ripple), float(removed_by),
                       analog=True)
        wn = np.atleast_1d(wn) / (2 * np.pi)
    else:
        n, wn = finder(wp, ws, float(ripple), float(removed_by), fs=1.0 / step)
        wn = np.atleast_1d(wn)
    words = (f"steepness {int(n)} found by SciPy {ORDER_FINDERS[method]} (at most {_g(ripple)} dB lost where it "
             f"keeps, at least {_g(removed_by)} dB removed from {', '.join(_g(v) for v in loss_at)} on)")
    return int(n), wn, words


def kaiser_order(kind, cut, loss_at, step, removed_by):
    """(number of weights, beta, cutoffs, words): SciPy kaiserord(removed_by, width) with width the distance from
    the cutoff (the edge of the band kept) to "loss_at" (where the band removed starts); firwin's cutoff is then the
    middle of the two, as SciPy kaiserord's documentation does. The number of weights is made odd."""
    from scipy import signal

    nyquist = 0.5 / step
    cut, loss_at = np.asarray(cut, dtype=float), np.asarray(loss_at, dtype=float)
    width = float(np.min(np.abs(loss_at - cut)))
    numtaps, beta = signal.kaiserord(float(removed_by), width / nyquist)
    numtaps = int(numtaps) + (1 - int(numtaps) % 2)  # odd: symmetric for every kind of band
    middle = (cut + loss_at) / 2
    words = (f"{numtaps} weights found by SciPy kaiserord (at least {_g(removed_by)} dB removed, transition width "
             f"{_g(width)}, cutoff {', '.join(_g(m) for m in middle)} in its middle)")
    return numtaps, float(beta), middle, words


def design_analog(kind, cut, method, steepness, ripple, removed_by, natural=None):
    """(b, a, words, call): the continuous filter (SciPy butter / cheby1 / cheby2 / ellip / bessel, analog=True) at
    2 pi x the cutoffs (cycles per unit of time), as numerator and denominator in s."""
    from scipy import signal

    btype = {"low": "lowpass", "high": "highpass", "pass": "bandpass", "stop": "bandstop"}[kind]
    w = 2 * np.pi * np.asarray(natural if natural is not None else cut, dtype=float)
    wn = float(w[0]) if len(w) == 1 else w
    n = int(steepness)
    args = dict(N=n, Wn=wn, btype=btype, analog=True, output="zpk")
    if method == "butterworth":
        z, p, k = signal.butter(**args)
        call = "butter"
    elif method == "chebyshev":
        z, p, k = signal.cheby1(rp=float(ripple), **args)
        call = "cheby1"
    elif method == "chebyshev 2":
        z, p, k = signal.cheby2(rs=float(removed_by), **args)
        call = "cheby2"
    elif method == "elliptic":
        z, p, k = signal.ellip(rp=float(ripple), rs=float(removed_by), **args)
        call = "ellip"
    elif method == "bessel":
        z, p, k = signal.bessel(norm="phase", **args)
        call = "bessel"
    else:
        raise SimplydataError(f'analog=True makes a continuous filter with test_method="butterworth", "chebyshev", '
                              f'"chebyshev 2", "elliptic" or "bessel"; not "{method}".')
    b, a = signal.zpk2tf(z, p, k)
    return np.real_if_close(b).real, np.real_if_close(a).real, call


def least_delay(taps):
    """SciPy minimum_phase(taps, method="homomorphic", half=False): the same gain, the least delay."""
    from scipy import signal

    return np.asarray(signal.minimum_phase(np.asarray(taps, dtype=float), method="homomorphic", half=False),
                      dtype=float)


def gammatone(frequency, step):
    """(b, a) of SciPy gammatone(frequency, "iir", fs=1 / step)."""
    from scipy import signal

    b, a = signal.gammatone(float(frequency), "iir", fs=1.0 / step)
    return np.asarray(b, dtype=float), np.asarray(a, dtype=float)
