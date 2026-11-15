"""sdata.wave(...) and sdata.window_shape(...): made-up signals and window weights, from SciPy."""

from __future__ import annotations

import numpy as np

from ._errors import SimplydataError, choice_error, friendly

SHAPES = ("sine", "square", "sawtooth", "chirp", "pulse", "impulse")
SWEEPS = ("linear", "quadratic", "logarithmic", "hyperbolic")


@friendly
def wave(shape="sine", frequency=1, time_step=None, how_many=None, high_share=0.5, rising_share=1.0,
         sweep="linear", bandwidth=0.5, at=1, sampling_rate=None, fs=None):
    """Numbers that make a wave: a sine, square, sawtooth, chirp, pulse or impulse. sdata.wave("sine", frequency=5, time_step=0.01, how_many=100)

    frequency= is cycles per unit of time (for "chirp", [start, end] with sweep= "linear",
    "quadratic", "logarithmic" or "hyperbolic"); time_step= the time between readings (sampling_rate= or
    fs= instead); how_many= the number of readings. "square" is high for high_share= of each cycle;
    "sawtooth" rises for rising_share= of each cycle (1: rises then drops); "pulse" is a Gaussian pulse
    with bandwidth= (centred in the middle); "impulse" is 1 at position at= (from 1) and 0 elsewhere.
    SciPy signal.square, sawtooth, chirp, gausspulse, unit_impulse; R gsignal gives the same. The
    numbers remember their time step.
    """
    from scipy import signal

    from ._time_axis import read_time_step
    from .numbers import numbers

    if shape not in SHAPES:
        raise choice_error("wave", "shape", shape, list(SHAPES))
    if isinstance(how_many, bool) or not isinstance(how_many, int) or how_many < 1:
        raise SimplydataError('wave() needs how_many= as the number of readings, such as sdata.wave("sine", '
                              "frequency=5, time_step=0.01, how_many=100).")
    step, words = read_time_step(time_step, sampling_rate, fs, None, "wave")
    t = np.arange(how_many) * step
    if shape == "impulse":
        if isinstance(at, bool) or not isinstance(at, int) or not 1 <= at <= how_many:
            raise SimplydataError(f"at= needs a position from 1 to {how_many}.")
        values = signal.unit_impulse(how_many, at - 1)
    elif shape == "chirp":
        if not (isinstance(frequency, (list, tuple)) and len(frequency) == 2):
            raise SimplydataError('shape="chirp" needs frequency=[start, end], such as frequency=[1, 20].')
        if sweep not in SWEEPS:
            raise choice_error("wave", "sweep", sweep, list(SWEEPS))
        values = signal.chirp(t, f0=float(frequency[0]), t1=t[-1] if how_many > 1 else 1.0, f1=float(frequency[1]),
                              method=sweep)
    else:
        if isinstance(frequency, bool) or not isinstance(frequency, (int, float)) or frequency <= 0:
            raise SimplydataError("wave() needs frequency= as a number above 0 (cycles per unit of time).")
        angle = 2 * np.pi * float(frequency) * t
        if shape == "sine":
            values = np.sin(angle)
        elif shape == "square":
            values = signal.square(angle, duty=float(high_share))
        elif shape == "sawtooth":
            values = signal.sawtooth(angle, width=float(rising_share))
        else:
            values = signal.gausspulse(t - t[len(t) // 2], fc=float(frequency), bw=float(bandwidth))
    nums = numbers(values)
    nums._time_step = step
    print(f"A {shape} wave of {how_many} readings ({words}).")
    return nums


@friendly
def window_shape(name="hann", how_many=64, periodic=False):
    """The weights of a window (taper), such as "hann": high in the middle, low at the ends. sdata.window_shape("hann", how_many=64)

    Any SciPy window name: "hann", "hamming", "blackman", "bartlett", "kaiser" (give ("kaiser", 5)),
    "tukey" ... Symmetric by default, as R gsignal::hann and NumPy hanning; periodic=True gives the
    version used inside spectra (SciPy get_window's default).
    """
    from scipy import signal

    from .numbers import numbers

    if isinstance(how_many, bool) or not isinstance(how_many, int) or how_many < 1:
        raise SimplydataError("window_shape() needs how_many= as a whole number of weights, such as how_many=64.")
    try:
        values = signal.get_window(name, how_many, fftbins=bool(periodic))
    except (ValueError, TypeError) as error:
        raise SimplydataError(f'window_shape() does not know the window {name!r} ({error}). Try "hann", "hamming", '
                              '"blackman" or ("kaiser", 5).') from None
    print(f"{how_many} weights of a {'periodic' if periodic else 'symmetric'} {name} window (SciPy get_window).")
    return numbers(values)


@friendly
def inverse_fourier_transform(table=None):
    """Numbers back from a Fourier transform table (its real and imaginary parts). sdata.inverse_fourier_transform(table)

    table is what nums.fourier_transform() gave back (show="half" or "all"). SciPy irfft / ifft, as R
    Re(fft(z, inverse = TRUE)) / n. A round trip gives the numbers back (to about 1e-12).
    """
    from scipy import fft

    from .numbers import numbers

    info = getattr(table, "_fourier", None)
    if info is None:
        raise SimplydataError("inverse_fourier_transform() needs the table that nums.fourier_transform() gave back.")
    frame = table._frame
    z = np.asarray(frame["real part"].to_numpy(), dtype=float) + 1j * np.asarray(frame["imaginary part"].to_numpy(),
                                                                                    dtype=float)
    values = fft.irfft(z, n=info["n"]) if info["show"] == "half" else fft.ifft(z).real
    nums = numbers(values)
    nums._time_step = info["time_step"]
    print(f"{info['n']} numbers back from the Fourier transform (SciPy {'irfft' if info['show'] == 'half' else 'ifft'}).")
    return nums
