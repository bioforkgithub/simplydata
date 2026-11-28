"""Numbers words: take_fourier_transform, envelope, convolve_with, deconvolve_by, change_time_step (to merge)."""

from __future__ import annotations

from .._typing import _Same

import math

import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from .._time_axis import read_time_step

FOURIER_SHOWS = ("half", "all")
ENVELOPE_SHOWS = ("envelope", "phase", "frequency")
KEEPS = {"all": "full", "same": "same", "overlap": "valid"}
RESAMPLE_METHODS = ("fourier", "polyphase", "filter then keep", "cubic spline", "quadratic spline")


def envelope_values(x, show, step):
    """Envelope, phase (degrees, unwrapped) or frequency (cycles per unit of time; last one empty) from
    SciPy signal.hilbert (the analytic signal, as R gsignal::hilbert)."""
    from scipy import signal

    z = signal.hilbert(x)
    if show == "envelope":
        return np.abs(z)
    phase = np.degrees(np.unwrap(np.angle(z)))
    return phase if show == "phase" else np.append(np.diff(phase) / 360.0 / step, np.nan)


class FourierNumberWords:
    @friendly(renamed={"nperseg": "window", "fn": "between", "m": "how_many"})
    def take_fourier_transform(self, time_step=None, show="half", sampling_rate=None, fs=None,
                               with_zero_in_middle=False, over_time=False, window=None, window_shape="hann",
                               between=None, how_many=None):
        """The numbers as a sum of waves: the size and phase of each frequency (the Fourier transform).

        numbers.take_fourier_transform(time_step=0.005)
        Gives back a table: frequency, size, phase (degrees), real part, imaginary part. show="half" (0 up
        to the highest frequency the readings can show, SciPy rfft) or "all" (every frequency, negative
        ones too, SciPy fft). The sizes are R's Mod(fft(x)) and the phases Arg(fft(x)) in degrees.
        with_zero_in_middle=True gives every frequency in order, the negative ones first and 0 in the middle (SciPy
        fftshift); it implies show="all".
        over_time=True takes the transform of pieces of window= readings (min(256, n)) that overlap by half,
        each weighted by window_shape="hann": the short-time Fourier transform (SciPy ShortTimeFFT.stft; the
        pieces at the ends are padded with zeros so the numbers can come back). The table gets a time column (the
        middle of each piece) before frequency. between=[low, high] with how_many= (100) gives the transform at
        how_many evenly spaced frequencies from low to high only, finer than the plain transform (the zoom FFT:
        SciPy zoom_fft, a chirp z-transform on the unit circle).
        sdata.find_inverse_fourier_transform(table) turns the table back into the numbers (not after between=).
        """
        import pandas as pd
        from scipy import fft

        from ..table import Table

        if show not in FOURIER_SHOWS:
            raise choice_error("take_fourier_transform", "show", show, list(FOURIER_SHOWS))
        if not isinstance(with_zero_in_middle, bool):
            raise SimplydataError("with_zero_in_middle= needs True or False (no quotes).")
        if with_zero_in_middle and show == "half":
            show = "all"  # the half spectrum has no negative frequencies to put before 0
        x = np.asarray(self._values, dtype=float).ravel()
        if np.isnan(x).any():
            raise SimplydataError("take_fourier_transform() needs a value at every step; fill the empty ones first.")
        step, words = read_time_step(time_step, sampling_rate, fs, getattr(self, "_time_step", None),
                                     "take_fourier_transform")
        if not isinstance(over_time, bool):
            raise SimplydataError("over_time= needs True or False (no quotes).")
        if over_time and between is not None:
            raise SimplydataError("over_time= and between= are two different transforms: give one of them.")
        if not over_time and (window is not None or window_shape != "hann"):
            raise SimplydataError("window= and window_shape= go with over_time=True (the transform of pieces).")
        if between is None and how_many is not None:
            raise SimplydataError("how_many= goes with between=[low, high] (the frequencies to zoom in on).")
        if over_time or between is not None:
            if show != "half" or with_zero_in_middle:
                raise SimplydataError("over_time= and between= give the frequencies from 0 up (show=\"half\").")
            from .._signal_spectra import short_time_table, zoom_table

            if over_time:
                return short_time_table(x, step, words, window, window_shape)
            return zoom_table(x, step, words, between, how_many)
        n = len(x)
        if show == "half":
            z, freq = fft.rfft(x), fft.rfftfreq(n, d=step)
        else:
            z, freq = fft.fft(x), fft.fftfreq(n, d=step)
        if with_zero_in_middle:
            z, freq = fft.fftshift(z), fft.fftshift(freq)
        print(f"Fourier transform of {n} readings ({words}): {len(z)} frequencies from {freq.min():g} to "
              f"{freq.max():g}; the biggest size (after frequency 0) is at "
              f"{freq[freq != 0][np.argmax(np.abs(z[freq != 0]))]:g}.")
        print("Method: SciPy fft" + (".rfft" if show == "half" else ".fft")
              + (", then fft.fftshift (0 in the middle)" if with_zero_in_middle else "")
              + ", as R Mod(fft(x)) and Arg(fft(x)).")
        table = Table(pd.DataFrame({"frequency": freq, "size": np.abs(z), "phase": np.degrees(np.angle(z)),
                                    "real part": z.real, "imaginary part": z.imag}))
        # the frequencies are kept too: find_inverse_fourier_transform checks the rows are still these
        table._fourier = {"n": n, "show": show, "time_step": step, "frequency": freq.copy(),
                          "zero_in_middle": with_zero_in_middle}
        return table

    @friendly
    def find_envelope(self: _Same, show="envelope", time_step=None, sampling_rate=None, fs=None) -> _Same:
        """The envelope of the numbers: how big the wave is at each moment (from the Hilbert transform).

        numbers.find_envelope()
        show="envelope" (the size of the analytic signal), "phase" (in degrees, unwrapped) or "frequency"
        (how fast the phase turns, cycles per unit of time; the last value is empty). SciPy
        signal.hilbert, as R gsignal::hilbert. Undo with numbers.undo().
        """
        if show not in ENVELOPE_SHOWS:
            raise choice_error("envelope", "show", show, list(ENVELOPE_SHOWS))
        x = np.asarray(self._values, dtype=float).ravel()
        if np.isnan(x).any():
            raise SimplydataError("find_envelope() needs a value at every step; fill the empty ones first.")
        step, _ = read_time_step(time_step, sampling_rate, fs, getattr(self, "_time_step", None), "envelope")
        out = envelope_values(x, show, step)
        print(f"The {show} of the numbers, from the analytic signal (SciPy signal.hilbert, as R gsignal::hilbert).")
        return self._change(f"envelope ({show})", out)

    @friendly
    def convolve_with(self: _Same, other, keep="all") -> _Same:
        """Convolve the numbers with other numbers: each result is a sum of products as one list slides along.

        numbers.convolve_with([1, 2, 1])
        keep="all" (every overlap, n + m - 1 numbers; R convolve(x, rev(y), type = "open")), "same" (the
        middle n) or "overlap" (only where they overlap fully; R type = "filter"). SciPy signal.convolve.
        Sliding sums without the flip: numbers.convolve_with(other.reverse()). Undo with numbers.undo().
        """
        from scipy import signal

        if keep not in KEEPS:
            raise choice_error("convolve_with", "keep", keep, list(KEEPS))
        y = np.asarray(getattr(other, "_values", other), dtype=float).ravel()
        x = np.asarray(self._values, dtype=float).ravel()
        if not len(y):
            raise SimplydataError("convolve_with() needs some numbers to convolve with, such as [1, 2, 1].")
        out = signal.convolve(x, y, mode=KEEPS[keep])
        print(f"Convolved {len(x)} numbers with {len(y)}: {len(out)} numbers (keep=\"{keep}\").")
        return self._change("convolve", out)

    @friendly
    def deconvolve_by(self: _Same, other) -> _Same:
        """Undo a convolution: the numbers divided by other numbers (polynomial division).

        numbers.deconvolve_by([1, 2, 3])
        Gives the quotient as the new numbers and prints the size of what is left over (the remainder).
        SciPy signal.deconvolve, as R pracma::deconv. Undo with numbers.undo().
        """
        from scipy import signal

        y = np.asarray(getattr(other, "_values", other), dtype=float).ravel()
        x = np.asarray(self._values, dtype=float).ravel()
        if not len(y) or y[0] == 0:
            raise SimplydataError("deconvolve_by() needs numbers whose first one is not 0.")
        if len(y) > len(x):
            raise SimplydataError("deconvolve_by() needs fewer numbers to divide by than there are numbers.")
        quotient, remainder = signal.deconvolve(x, y)
        print(f"Deconvolved by {len(y)} numbers: {len(quotient)} numbers left; the remainder's biggest size is "
              f"{np.max(np.abs(remainder)):.3g}. (As R pracma::deconv.)")
        return self._change("deconvolve", quotient)

    @friendly(renamed={"method": "test_method"})
    def change_time_step(self, to=None, time_step=None, test_method="fourier", sampling_rate=None, fs=None):
        """Change the time between readings (resample): fewer readings (with a filter first) or more.

        numbers.change_time_step(to=0.01, time_step=0.001)
        to= is the new time between readings; time_step= the present one (or remembered). test_method="fourier"
        (SciPy signal.resample: treats the recording as repeating), "polyphase" (SciPy resample_poly with
        the ratio as a fraction, Kaiser window 5) or "filter then keep" (SciPy decimate: a Chebyshev filter
        run both ways, then every n-th reading; to= must be a whole number of steps), "cubic spline" or
        "quadratic spline" (SciPy cspline1d / qspline1d and their _eval: a spline through every reading, ends
        mirrored, read at the new times from the first reading on; no filter, so make the step smaller or take
        the fast cycles out first). Keeping every n-th
        reading without a filter is keep_numbers_by_position(1, step=n), which can fold fast cycles into
        slow ones (aliasing). The numbers remember the new time step. Undo with numbers.undo().
        """
        from fractions import Fraction

        from scipy import signal

        if test_method not in RESAMPLE_METHODS:
            raise choice_error("change_time_step", "test_method", test_method, list(RESAMPLE_METHODS))
        step, _ = read_time_step(time_step, sampling_rate, fs, getattr(self, "_time_step", None), "change_time_step")
        if isinstance(to, bool) or not isinstance(to, (int, float)) or to <= 0:
            raise SimplydataError("change_time_step() needs to= as the new time between readings, such as to=0.01.")
        x = np.asarray(self._values, dtype=float).ravel()
        if np.isnan(x).any():
            raise SimplydataError("change_time_step() needs a value at every step; fill the empty ones first.")
        ratio = Fraction(step / to).limit_denominator(1000)  # new readings per old reading
        if test_method == "fourier":
            n_new = int(round(len(x) * step / to))
            if n_new < 1:
                raise SimplydataError(f"change_time_step() would leave no readings: to= is more than {len(x)} time steps.")
            out = signal.resample(x, n_new)
            actual = step * len(x) / n_new  # the same total time over a whole number of readings
        elif test_method == "polyphase":
            out = signal.resample_poly(x, ratio.numerator, ratio.denominator)
            actual = step * ratio.denominator / ratio.numerator  # the ratio as a fraction (denominator at most 1000)
        elif test_method in ("cubic spline", "quadratic spline"):
            from .._signal_spectra import spline_resample

            out = spline_resample(x, step, float(to), test_method)
            actual = float(to)
        else:
            factor = to / step
            if abs(factor - round(factor)) > 1e-9 or round(factor) < 2:
                raise SimplydataError('test_method="filter then keep" needs to= a whole number (2 or more) of time steps.')
            out = signal.decimate(x, int(round(factor)), ftype="iir", zero_phase=True)
            actual = step * int(round(factor))
        exact = math.isclose(actual, to, rel_tol=1e-9)
        note = "" if exact else (f" The time step is {actual:.6g}, not exactly {to:g}: {len(out)} readings must fill "
                                 f"the same time as {len(x)}" + (" (the ratio is a fraction with a denominator of at "
                                                                  "most 1000)" if test_method == "polyphase" else "") + ".")
        print(f"Changed the time step from {step:g} to {actual:.6g}: {len(x)} readings became {len(out)} (method "
              f"\"{test_method}\", SciPy).{note}")
        changed = self._change("change time step", out)
        self._time_step = float(to) if exact else float(actual)
        return changed
