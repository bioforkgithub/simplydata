"""Numbers words: fourier_transform, envelope, convolve_with, deconvolve_by, change_time_step (to merge)."""

from __future__ import annotations

import math

import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from .._time_axis import read_time_step

FOURIER_SHOWS = ("half", "all")
ENVELOPE_SHOWS = ("envelope", "phase", "frequency")
KEEPS = {"all": "full", "same": "same", "overlap": "valid"}
RESAMPLE_METHODS = ("fourier", "polyphase", "filter then keep")


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
    @friendly
    def fourier_transform(self, time_step=None, show="half", sampling_rate=None, fs=None):
        """The numbers as a sum of waves: the size and phase of each frequency (the Fourier transform).

        nums.fourier_transform(time_step=0.005)
        Gives back a table: frequency, size, phase (degrees), real part, imaginary part. show="half" (0 up
        to the highest frequency the readings can show, SciPy rfft) or "all" (every frequency, negative
        ones too, SciPy fft). The sizes are R's Mod(fft(x)) and the phases Arg(fft(x)) in degrees.
        sdata.inverse_fourier_transform(table) turns the table back into the numbers.
        """
        import pandas as pd
        from scipy import fft

        from ..table import Table

        if show not in FOURIER_SHOWS:
            raise choice_error("fourier_transform", "show", show, list(FOURIER_SHOWS))
        x = np.asarray(self._values, dtype=float).ravel()
        if np.isnan(x).any():
            raise SimplydataError("fourier_transform() needs a value at every step; fill the empty ones first.")
        step, words = read_time_step(time_step, sampling_rate, fs, getattr(self, "_time_step", None),
                                     "fourier_transform")
        n = len(x)
        if show == "half":
            z, freq = fft.rfft(x), fft.rfftfreq(n, d=step)
        else:
            z, freq = fft.fft(x), fft.fftfreq(n, d=step)
        print(f"Fourier transform of {n} readings ({words}): {len(z)} frequencies from {freq.min():g} to "
              f"{freq.max():g}; the biggest size (after frequency 0) is at {freq[1:][np.argmax(np.abs(z[1:]))]:g}.")
        print("Method: SciPy fft" + (".rfft" if show == "half" else ".fft") + ", as R Mod(fft(x)) and Arg(fft(x)).")
        table = Table(pd.DataFrame({"frequency": freq, "size": np.abs(z), "phase": np.degrees(np.angle(z)),
                                    "real part": z.real, "imaginary part": z.imag}))
        table._fourier = {"n": n, "show": show, "time_step": step}
        return table

    @friendly
    def envelope(self, show="envelope", time_step=None, sampling_rate=None, fs=None):
        """The envelope of the numbers: how big the wave is at each moment (from the Hilbert transform).

        nums.envelope()
        show="envelope" (the size of the analytic signal), "phase" (in degrees, unwrapped) or "frequency"
        (how fast the phase turns, cycles per unit of time; the last value is empty). SciPy
        signal.hilbert, as R gsignal::hilbert. Undo with nums.undo().
        """
        if show not in ENVELOPE_SHOWS:
            raise choice_error("envelope", "show", show, list(ENVELOPE_SHOWS))
        x = np.asarray(self._values, dtype=float).ravel()
        if np.isnan(x).any():
            raise SimplydataError("envelope() needs a value at every step; fill the empty ones first.")
        step, _ = read_time_step(time_step, sampling_rate, fs, getattr(self, "_time_step", None), "envelope")
        out = envelope_values(x, show, step)
        print(f"The {show} of the numbers, from the analytic signal (SciPy signal.hilbert, as R gsignal::hilbert).")
        return self._change(f"envelope ({show})", out)

    @friendly
    def convolve_with(self, other, keep="all"):
        """Convolve the numbers with other numbers: each result is a sum of products as one list slides along.

        nums.convolve_with([1, 2, 1])
        keep="all" (every overlap, n + m - 1 numbers; R convolve(x, rev(y), type = "open")), "same" (the
        middle n) or "overlap" (only where they overlap fully; R type = "filter"). SciPy signal.convolve.
        Sliding sums without the flip: nums.convolve_with(other.reverse()). Undo with nums.undo().
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
    def deconvolve_by(self, other):
        """Undo a convolution: the numbers divided by other numbers (polynomial division).

        nums.deconvolve_by([1, 2, 3])
        Gives the quotient as the new numbers and prints the size of what is left over (the remainder).
        SciPy signal.deconvolve, as R pracma::deconv. Undo with nums.undo().
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

    @friendly
    def change_time_step(self, to=None, time_step=None, method="fourier", sampling_rate=None, fs=None):
        """Change the time between readings (resample): fewer readings (with a filter first) or more.

        nums.change_time_step(to=0.01, time_step=0.001)
        to= is the new time between readings; time_step= the present one (or remembered). method="fourier"
        (SciPy signal.resample: treats the recording as repeating), "polyphase" (SciPy resample_poly with
        the ratio as a fraction, Kaiser window 5) or "filter then keep" (SciPy decimate: a Chebyshev filter
        run both ways, then every n-th reading; to= must be a whole number of steps). Keeping every n-th
        reading without a filter is keep_numbers_by_position(1, step=n), which can fold fast cycles into
        slow ones (aliasing). The numbers remember the new time step. Undo with nums.undo().
        """
        from fractions import Fraction

        from scipy import signal

        if method not in RESAMPLE_METHODS:
            raise choice_error("change_time_step", "method", method, list(RESAMPLE_METHODS))
        step, _ = read_time_step(time_step, sampling_rate, fs, getattr(self, "_time_step", None), "change_time_step")
        if isinstance(to, bool) or not isinstance(to, (int, float)) or to <= 0:
            raise SimplydataError("change_time_step() needs to= as the new time between readings, such as to=0.01.")
        x = np.asarray(self._values, dtype=float).ravel()
        if np.isnan(x).any():
            raise SimplydataError("change_time_step() needs a value at every step; fill the empty ones first.")
        ratio = Fraction(step / to).limit_denominator(1000)  # new readings per old reading
        if method == "fourier":
            n_new = int(round(len(x) * step / to))
            if n_new < 1:
                raise SimplydataError(f"change_time_step() would leave no readings: to= is more than {len(x)} time steps.")
            out = signal.resample(x, n_new)
            actual = step * len(x) / n_new  # the same total time over a whole number of readings
        elif method == "polyphase":
            out = signal.resample_poly(x, ratio.numerator, ratio.denominator)
            actual = step * ratio.denominator / ratio.numerator  # the ratio as a fraction (denominator at most 1000)
        else:
            factor = to / step
            if abs(factor - round(factor)) > 1e-9 or round(factor) < 2:
                raise SimplydataError('method="filter then keep" needs to= a whole number (2 or more) of time steps.')
            out = signal.decimate(x, int(round(factor)), ftype="iir", zero_phase=True)
            actual = step * int(round(factor))
        exact = math.isclose(actual, to, rel_tol=1e-9)
        note = "" if exact else (f" The time step is {actual:.6g}, not exactly {to:g}: {len(out)} readings must fill "
                                 f"the same time as {len(x)}" + (" (the ratio is a fraction with a denominator of at "
                                                                  "most 1000)" if method == "polyphase" else "") + ".")
        print(f"Changed the time step from {step:g} to {actual:.6g}: {len(x)} readings became {len(out)} (method "
              f"\"{method}\", SciPy).{note}")
        changed = self._change("change time step", out)
        self._time_step = float(to) if exact else float(actual)
        return changed
