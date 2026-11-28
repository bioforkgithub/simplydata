"""Spectra over time, zoomed spectra, spline resampling and phase locking (families for 100 %, batches 17-18).

Plan section 2.7 (approved by Manish 2026-11-28). Every number comes from SciPy; own code only arranges SciPy's
output as a table:

* take_fourier_transform(over_time=True): SciPy ShortTimeFFT(win, hop, fs).stft (pieces of window= readings, hop
  half of it, SciPy get_window weights of the shape asked for; the pieces at the ends padded with zeros, SciPy's
  default), and find_inverse_fourier_transform gives the numbers back with ShortTimeFFT.istft (which refuses
  weights that cannot come back: SciPy's check_NOLA rule);
* take_fourier_transform(between=[low, high], how_many=): SciPy zoom_fft(x, [low, high], m=how_many, fs=..,
  endpoint=True): the discrete Fourier transform at those frequencies only (a chirp z-transform, SciPy czt, on
  the unit circle; as R gsignal::czt);
* find_spectrum(over_time=True): SciPy signal.spectrogram, as chart.draw_spectrum_over_time;
* change_time_step("cubic spline" / "quadratic spline"): SciPy cspline1d + cspline1d_eval (qspline1d +
  qspline1d_eval);
* numbers.find_phase_locking_to(period=): SciPy vectorstrength.
"""

from __future__ import annotations

import numpy as np

from ._errors import SimplydataError


def _pieces(n, window, step_name):
    size = min(256, n) if window is None else window
    if isinstance(size, bool) or not isinstance(size, (int, np.integer)) or not 4 <= size <= n:
        raise SimplydataError(f"{step_name}() needs window= as the number of readings in each piece: a whole number "
                              f"from 4 to {n}.")
    return int(size)


def _short_time(n, step, size, window_shape):
    from scipy import signal

    try:
        win = signal.get_window(window_shape, size)
    except (ValueError, TypeError) as error:
        raise SimplydataError(f"window_shape={window_shape!r} is not a SciPy window ({error}). Try \"hann\", "
                              "\"hamming\" or (\"kaiser\", 5).") from None
    return signal.ShortTimeFFT(win, hop=size // 2, fs=1.0 / step)


def short_time_table(x, step, words, window, window_shape):
    """take_fourier_transform(over_time=True): a long table of time, frequency, size, phase, real and imaginary
    part (SciPy ShortTimeFFT.stft)."""
    import pandas as pd

    from .table import Table

    n = len(x)
    size = _pieces(n, window, "take_fourier_transform")
    sft = _short_time(n, step, size, window_shape)
    z = sft.stft(x)  # frequencies x pieces
    freq, times = sft.f, sft.t(n)
    grid_t, grid_f = np.meshgrid(times, freq)
    flat = z.T.ravel()
    print(f"Short-time Fourier transform of {n} readings ({words}): {len(times)} pieces of {size} readings (half "
          f"overlap, {window_shape} weights), {len(freq)} frequencies from 0 to {freq[-1]:g} each.")
    print("Method: SciPy signal.ShortTimeFFT(win, hop, fs).stft, not scaled (the sizes of the plain transform of each "
          "weighted piece; SciPy's legacy stft divides them by the sum of the weights), the pieces at the ends padded "
          "with zeros.")
    table = Table(pd.DataFrame({"time": grid_t.T.ravel(), "frequency": grid_f.T.ravel(), "size": np.abs(flat),
                                "phase": np.degrees(np.angle(flat)), "real part": flat.real,
                                "imaginary part": flat.imag}))
    table._fourier = {"n": n, "show": "over time", "time_step": step, "window": size, "window_shape": window_shape,
                      "frequency": grid_f.T.ravel().copy(), "time": grid_t.T.ravel().copy(),
                      "shape": z.shape}
    return table


def inverse_short_time(table, info):
    """find_inverse_fourier_transform of an over_time=True table: SciPy ShortTimeFFT.istft."""
    from .numbers import number_list

    frame = table._frame
    columns = set(frame.columns)
    if not {"time", "frequency", "real part", "imaginary part"} <= columns:
        raise SimplydataError("find_inverse_fourier_transform() needs the columns time, frequency, real part and "
                              "imaginary part of the table that take_fourier_transform(over_time=True) gave back.")
    freq = np.asarray(frame["frequency"].to_numpy(), dtype=float)
    times = np.asarray(frame["time"].to_numpy(), dtype=float)
    if len(freq) != len(info["frequency"]) or not (np.array_equal(freq, info["frequency"])
                                                   and np.array_equal(times, info["time"])):
        raise SimplydataError("find_inverse_fourier_transform() needs the rows of the table as take_fourier_transform("
                              "over_time=True) made them, but they have changed. Keep every row; to take some out, "
                              "set their real part and imaginary part to 0.")
    z = (np.asarray(frame["real part"].to_numpy(), dtype=float)
         + 1j * np.asarray(frame["imaginary part"].to_numpy(), dtype=float))
    rows, cols = info["shape"]
    sft = _short_time(info["n"], info["time_step"], info["window"], info["window_shape"])
    try:
        values = sft.istft(z.reshape(cols, rows).T, k1=info["n"])
    except ValueError as error:
        raise SimplydataError(f"SciPy cannot turn these pieces back into numbers ({error}).") from None
    nums = number_list(np.asarray(values, dtype=float))
    nums._time_step = info["time_step"]
    print(f"{info['n']} numbers back from the short-time Fourier transform (SciPy ShortTimeFFT.istft).")
    return nums


def zoom_table(x, step, words, between, how_many):
    """take_fourier_transform(between=[low, high], how_many=): SciPy zoom_fft at how_many frequencies."""
    import pandas as pd
    from scipy import signal

    from .table import Table

    nyquist = 0.5 / step
    if (not isinstance(between, (list, tuple)) or len(between) != 2
            or not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in between)
            or not 0 <= between[0] < between[1] <= nyquist):
        raise SimplydataError(f"between= needs two frequencies from 0 to {nyquist:g} (half the readings per unit of "
                              "time), the lower first, such as between=[1, 5].")
    m = 100 if how_many is None else how_many
    if isinstance(m, bool) or not isinstance(m, (int, np.integer)) or m < 2:
        raise SimplydataError("how_many= needs a whole number of frequencies, 2 or more.")
    z = signal.zoom_fft(x, [float(between[0]), float(between[1])], m=int(m), fs=1.0 / step, endpoint=True)
    freq = np.linspace(float(between[0]), float(between[1]), int(m))
    top = int(np.argmax(np.abs(z)))
    print(f"Fourier transform of {len(x)} readings ({words}) at {int(m)} frequencies from {between[0]:g} to "
          f"{between[1]:g}: the biggest size is at {freq[top]:.6g}.")
    print("Method: SciPy signal.zoom_fft (the chirp z-transform on the unit circle, SciPy czt; as R gsignal::czt), "
          "the same numbers as fft at those frequencies.")
    table = Table(pd.DataFrame({"frequency": freq, "size": np.abs(z), "phase": np.degrees(np.angle(z)),
                                "real part": z.real, "imaginary part": z.imag}))
    table._fourier = {"show": "zoom"}
    return table


def spectrum_over_time_table(values, step, words, window, window_shape, show, between):
    """find_spectrum(over_time=True): SciPy signal.spectrogram as chart.draw_spectrum_over_time."""
    import pandas as pd

    from .table import Table
    from .words.time_charts import spectrum_over_time

    if show not in ("power", "decibels"):
        raise SimplydataError('find_spectrum(over_time=True) shows "power" or "decibels".')
    size = _pieces(len(values), window, "find_spectrum")
    freq, times, power = spectrum_over_time(values, step, size, window_shape)
    grid_t, grid_f = np.meshgrid(times, freq)
    t, f, p = grid_t.T.ravel(), grid_f.T.ravel(), power.T.ravel()
    keep = np.ones(len(f), dtype=bool) if between is None else (f >= between[0]) & (f <= between[1])
    column = "power"
    if show == "decibels":
        column = "power (decibels)"
        with np.errstate(divide="ignore"):
            p = 10 * np.log10(p)
    loudest = int(np.argmax(power.max(axis=0)))
    print(f"Spectrum over time ({words}): {len(times)} pieces of {size} readings (half overlap, {window_shape} "
          f"weights), frequencies 0 to {freq[-1]:.4g}; the strongest piece is the one around time "
          f"{times[loudest]:.4g}.")
    print("Method: SciPy signal.spectrogram (each piece's mean removed, one-sided density), as "
          "chart.draw_spectrum_over_time.")
    return Table(pd.DataFrame({"time": t[keep], "frequency": f[keep], column: p[keep]}))


def spline_resample(x, step, to, method):
    """change_time_step("cubic spline" / "quadratic spline"): SciPy cspline1d / qspline1d coefficients read at
    the new times (cspline1d_eval / qspline1d_eval), from the first reading to the last."""
    from scipy import signal

    if len(x) < 4:
        raise SimplydataError("A spline needs at least 4 readings.")
    new_times = np.arange(int(np.floor((len(x) - 1) * step / to + 1e-9)) + 1) * to
    if method == "cubic spline":
        return signal.cspline1d_eval(signal.cspline1d(x), new_times, dx=step, x0=0.0)
    return signal.qspline1d_eval(signal.qspline1d(x), new_times, dx=step, x0=0.0)


def phase_locking(events, period):
    """(strengths, phases in degrees) from SciPy vectorstrength(events, period)."""
    from scipy import signal

    strength, phase = signal.vectorstrength(np.asarray(events, dtype=float), period)
    return np.atleast_1d(np.asarray(strength, dtype=float)), np.degrees(np.atleast_1d(np.asarray(phase, dtype=float)))
