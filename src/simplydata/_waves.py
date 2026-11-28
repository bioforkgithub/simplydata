"""sdata.make_wave(...) and sdata.make_window_shape(...): made-up signals and window weights, from SciPy."""

from __future__ import annotations

import numpy as np

from ._errors import SimplydataError, choice_error, friendly

SHAPES = ("sine", "square", "sawtooth", "chirp", "pulse", "impulse", "maximum length sequence")
SHAPE_SPELLINGS = {"mls": "maximum length sequence", "max_len_seq": "maximum length sequence",
                   "pseudo-random binary": "maximum length sequence", "prbs": "maximum length sequence",
                   "sweep": "chirp", "gausspulse": "pulse", "unit_impulse": "impulse"}
SWEEPS = ("linear", "quadratic", "logarithmic", "hyperbolic", "polynomial")


@friendly
def make_wave(shape="sine", frequency=1, time_step=None, how_many=None, high_share=0.5, rising_share=1.0,
              sweep="linear", bandwidth=0.5, at=1, sampling_rate=None, fs=None):
    """Numbers that make a wave: a sine, square, sawtooth, chirp, pulse or impulse. sdata.make_wave("sine", frequency=5, time_step=0.01, how_many=100)

    frequency= is cycles per unit of time (for "chirp", [start, end] with sweep= "linear",
    "quadratic", "logarithmic" or "hyperbolic"; with sweep="polynomial", frequency= is the polynomial of the
    frequency in time, highest power first: [2, 1] is 2 t + 1, SciPy sweep_poly); "maximum length sequence"
    ("mls") is a pseudo-random run of 0s and 1s that repeats only after 2 ** bits - 1 readings, used to measure
    systems (SciPy max_len_seq with the fewest bits whose run is at least how_many= long, from its usual start);
    time_step= the time between readings (sampling_rate= or
    fs= instead); how_many= the number of readings. "square" is high for high_share= of each cycle;
    "sawtooth" rises for rising_share= of each cycle (1: rises then drops); "pulse" is a Gaussian pulse
    with bandwidth= (centred in the middle); "impulse" is 1 at position at= (from 1) and 0 elsewhere.
    SciPy signal.square, sawtooth, chirp, gausspulse, unit_impulse; R gsignal gives the same. The
    numbers remember their time step.
    """
    from scipy import signal

    from ._time_axis import read_time_step
    from .numbers import number_list

    if isinstance(shape, str):
        shape = SHAPE_SPELLINGS.get(shape.strip().lower(), shape.strip().lower())
    if shape not in SHAPES:
        raise choice_error("wave", "shape", shape, list(SHAPES))
    if isinstance(how_many, bool) or not isinstance(how_many, int) or how_many < 1:
        raise SimplydataError('make_wave() needs how_many= as the number of readings, such as sdata.make_wave("sine", '
                              "frequency=5, time_step=0.01, how_many=100).")
    step, words = read_time_step(time_step, sampling_rate, fs, None, "wave")
    t = np.arange(how_many) * step
    if shape == "impulse":
        if isinstance(at, bool) or not isinstance(at, int) or not 1 <= at <= how_many:
            raise SimplydataError(f"at= needs a position from 1 to {how_many}.")
        values = signal.unit_impulse(how_many, at - 1)
    elif shape == "maximum length sequence":
        bits = max(2, int(np.ceil(np.log2(how_many + 1))))
        if bits > 32:
            raise SimplydataError("A maximum length sequence of more than 2 ** 32 - 1 readings is not known to SciPy.")
        values = signal.max_len_seq(bits, length=how_many)[0].astype(float)
    elif shape == "chirp" and sweep == "polynomial":
        poly = np.atleast_1d(np.asarray(frequency, dtype=float)) if isinstance(frequency, (list, tuple)) else None
        if poly is None or not len(poly):
            raise SimplydataError('sweep="polynomial" needs frequency= as the polynomial of the frequency in time, '
                                  "highest power first, such as frequency=[2, 1] for 2 t + 1.")
        values = signal.sweep_poly(t, poly)
    elif shape == "chirp":
        if not (isinstance(frequency, (list, tuple)) and len(frequency) == 2):
            raise SimplydataError('shape="chirp" needs frequency=[start, end], such as frequency=[1, 20].')
        if sweep not in SWEEPS:
            raise choice_error("wave", "sweep", sweep, list(SWEEPS))
        values = signal.chirp(t, f0=float(frequency[0]), t1=t[-1] if how_many > 1 else 1.0, f1=float(frequency[1]),
                              method=sweep)
    else:
        if isinstance(frequency, bool) or not isinstance(frequency, (int, float)) or frequency <= 0:
            raise SimplydataError("make_wave() needs frequency= as a number above 0 (cycles per unit of time).")
        angle = 2 * np.pi * float(frequency) * t
        if shape == "sine":
            values = np.sin(angle)
        elif shape == "square":
            values = signal.square(angle, duty=float(high_share))
        elif shape == "sawtooth":
            values = signal.sawtooth(angle, width=float(rising_share))
        else:
            values = signal.gausspulse(t - t[len(t) // 2], fc=float(frequency), bw=float(bandwidth))
    nums = number_list(values)
    nums._time_step = step
    print(f"A {shape} " + ("" if shape == "maximum length sequence" else "wave ") + f"of {how_many} readings "
          f"({words})." + (f" SciPy max_len_seq with {bits} bits (the run repeats after {2 ** bits - 1} readings)."
                           if shape == "maximum length sequence" else ""))
    return nums


@friendly
def make_window_shape(name="hann", how_many=64, periodic=False):
    """The weights of a window (taper), such as "hann": high in the middle, low at the ends. sdata.make_window_shape("hann", how_many=64)

    Any SciPy window name: "hann", "hamming", "blackman", "bartlett", "kaiser" (give ("kaiser", 5)),
    "tukey" ... Symmetric by default, as R gsignal::hann and NumPy hanning; periodic=True gives the
    version used inside spectra (SciPy get_window's default).
    """
    from scipy import signal

    from .numbers import number_list

    if isinstance(how_many, bool) or not isinstance(how_many, int) or how_many < 1:
        raise SimplydataError("make_window_shape() needs how_many= as a whole number of weights, such as how_many=64.")
    try:
        values = signal.get_window(name, how_many, fftbins=bool(periodic))
    except (ValueError, TypeError) as error:
        raise SimplydataError(f'make_window_shape() does not know the window {name!r} ({error}). Try "hann", "hamming", '
                              '"blackman" or ("kaiser", 5).') from None
    print(f"{how_many} weights of a {'periodic' if periodic else 'symmetric'} {name} window (SciPy get_window).")
    return number_list(values)


def _same_rows_as_made(info, frame):
    """Refuse a Fourier table whose rows changed after take_fourier_transform made it: the number of readings it
    came from (n, which irfft needs) and the order of its frequencies then no longer fit the rows, and SciPy would
    quietly cut or pad them. Changing the real and imaginary parts (setting some frequencies to 0) is fine."""
    if not {"frequency", "real part", "imaginary part"} <= set(frame.columns):
        raise SimplydataError("find_inverse_fourier_transform() needs the columns frequency, real part and imaginary "
                              "part of the table that numbers.take_fourier_transform() gave back.")
    made = info.get("frequency")
    now = np.asarray(frame["frequency"].to_numpy(), dtype=float)
    if made is not None and (len(now) != len(made) or not np.array_equal(now, made)):
        said = (f"it had {len(made)} rows and now has {len(now)}" if len(now) != len(made) else
                "its frequencies are no longer the ones it made, in the same order")
        raise SimplydataError(
            "find_inverse_fourier_transform() needs the rows of the table as numbers.take_fourier_transform() made "
            f"them, but they have changed ({said}), so it is no longer known how many numbers they came from.\n"
            "Keep every row. To take some frequencies out, set their real part and imaginary part to 0 instead, "
            "or undo the step that changed the rows (table.undo()).")


@friendly
def find_inverse_fourier_transform(table=None):
    """Numbers back from a Fourier transform table (its real and imaginary parts). sdata.find_inverse_fourier_transform(table)

    table is what numbers.take_fourier_transform() gave back (show="half" or "all"), or grid.take_fourier_transform()
    (a grid comes back: SciPy irfft2 / ifft2, or irfft / ifft over one direction). SciPy irfft / ifft, as R
    Re(fft(z, inverse = TRUE)) / n; for a table of over_time=True, SciPy ShortTimeFFT.istft (the inverse
    short-time transform; SciPy checks the pieces overlap enough to come back, check_NOLA). A round trip gives
    the numbers back (to about 1e-12). Its rows must stay
    as they were made: to take frequencies out, set their real and imaginary parts to 0 (removing or
    reordering rows is refused, since the number of readings then no longer fits).
    """
    from scipy import fft

    from .numbers import number_list

    info = getattr(table, "_fourier", None)
    if info is None:
        raise SimplydataError("find_inverse_fourier_transform() needs the table that numbers.take_fourier_transform() gave back.")
    if info.get("show") == "zoom":
        raise SimplydataError("A transform at some frequencies only (between=) cannot give the numbers back: it leaves "
                              "the other frequencies out. Take numbers.take_fourier_transform() without between= for a "
                              "round trip.")
    if info.get("show") == "over time":
        from ._signal_spectra import inverse_short_time

        return inverse_short_time(table, info)
    frame = table._frame
    if "grid" in info:  # families for 100 %, batch 11: the table grid.take_fourier_transform() gave back
        from .numbers.numpy_grid_words import inverse_grid_fourier

        return inverse_grid_fourier(info, frame)
    _same_rows_as_made(info, frame)
    z = np.asarray(frame["real part"].to_numpy(), dtype=float) + 1j * np.asarray(frame["imaginary part"].to_numpy(),
                                                                                    dtype=float)
    if info.get("zero_in_middle"):
        z = fft.ifftshift(z)  # back to SciPy's own order before ifft
    values = fft.irfft(z, n=info["n"]) if info["show"] == "half" else fft.ifft(z).real
    nums = number_list(values)
    nums._time_step = info["time_step"]
    print(f"{info['n']} numbers back from the Fourier transform (SciPy {'irfft' if info['show'] == 'half' else 'ifft'}).")
    return nums
