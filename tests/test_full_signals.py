"""Families for 100 %, batches 17-18 (plan 2.7, approved by Manish 2026-11-28): SciPy signals and systems.

Every new option value and word is checked against SciPy itself (scipy.signal), called directly here: the FIR
designs, the steepness found for the losses asked, analog filters, the steady start, the least delay, gammatone,
the sections and partial fractions of a system, pole placement, the group delay, the short-time and zoomed Fourier
transforms, the spectrum over time, maximum length sequences, polynomial sweeps, spline resampling and phase
locking. None of these options or words existed before this batch, so each test fails on the old code.
"""

from __future__ import annotations

import contextlib
import io

import numpy as np
import pytest
from scipy import signal

import simplydata as sdata
from simplydata import SimplydataError


def sensor():
    return sdata.get_example("sensor").get_column("signal")


def raw():
    return np.asarray(sensor()._values, dtype=float).copy()


def values(nums):
    return np.asarray(nums._values, dtype=float)


def quiet(call, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return call(*args, **kwargs)


# ---------------------------------------------------------------------------------------- FIR filters
def test_fir_window_method_is_firwin_run_both_ways():
    nums = sensor()
    quiet(nums.keep_each_frequency_that, is_below=10, time_step=0.005, test_method="fir", how_many_weights=51,
          window_shape="blackman")
    taps = signal.firwin(51, 10, window="blackman", fs=200)
    assert values(nums) == pytest.approx(signal.filtfilt(taps, [1.0], raw()), rel=1e-12, abs=1e-12)


def test_fir_weights_follow_firwins_own_formula():
    """The window method written out: a windowed sinc, scaled so the weights add up to 1 (firwin's scale=True)."""
    system = quiet(sdata.frequency_filter, keep_below=10, time_step=0.005, test_method="fir", how_many_weights=21)
    weights = system.table().as_pandas()["numerator"].to_numpy()
    k = np.arange(21) - 10
    ideal = 0.1 * np.sinc(0.1 * k)  # 2 x cutoff / readings per second = 2 x 10 / 200
    by_hand = ideal * np.hamming(21)
    assert weights == pytest.approx(by_hand / by_hand.sum(), abs=1e-14)


@pytest.mark.parametrize("method, design", [
    ("fir least squares", lambda: signal.firls(51, [0, 8, 12, 100], [1, 1, 0, 0], fs=200)),
    ("fir equiripple", lambda: signal.remez(51, [0, 8, 12, 100], [1, 0], fs=200)),
    ("fir frequency sampling", lambda: signal.firwin2(51, [0, 8, 12, 100], [1, 1, 0, 0], fs=200)),
])
def test_other_fir_designs_are_scipys(method, design):
    nums = sensor()
    quiet(nums.keep_each_frequency_that, is_below=10, time_step=0.005, test_method=method, how_many_weights=51,
          transition_width=4)
    assert values(nums) == pytest.approx(signal.filtfilt(design(), [1.0], raw()), rel=1e-12, abs=1e-12)


def test_fir_band_kinds_and_the_jump_of_frequency_sampling():
    nums = sensor()
    quiet(nums.remove_each_frequency_that, is_between=[40, 60], time_step=0.005, test_method="fir least squares",
          how_many_weights=61, transition_width=6)
    taps = signal.firls(61, [0, 37, 43, 57, 63, 100], [1, 1, 0, 0, 1, 1], fs=200)
    assert values(nums) == pytest.approx(signal.filtfilt(taps, [1.0], raw()), rel=1e-12, abs=1e-12)
    nums = sensor()
    quiet(nums.keep_each_frequency_that, is_above=20, time_step=0.005, test_method="fir frequency sampling",
          how_many_weights=51)
    taps = signal.firwin2(51, [0.0, 20.0, 20.0, 100.0], [0, 0, 1, 1], fs=200)  # floats: SciPy nudges the repeat
    assert values(nums) == pytest.approx(signal.filtfilt(taps, [1.0], raw()), rel=1e-12, abs=1e-12)


def test_fir_spellings_are_scipys_and_rs_names():
    for spelling in ("firls", "least squares"):
        nums = sensor()
        quiet(nums.keep_each_frequency_that, is_below=10, time_step=0.005, test_method=spelling, transition_width=4)
    for spelling in ("remez", "parks-mcclellan", "equiripple"):
        quiet(sensor().keep_each_frequency_that, is_below=10, time_step=0.005, test_method=spelling,
              transition_width=4)


def test_fir_options_are_checked():
    with pytest.raises(SimplydataError, match="transition_width="):
        quiet(sensor().keep_each_frequency_that, is_below=10, time_step=0.005, test_method="fir equiripple")
    with pytest.raises(SimplydataError, match="odd"):
        quiet(sensor().keep_each_frequency_that, is_below=10, time_step=0.005, test_method="fir", how_many_weights=50)
    with pytest.raises(SimplydataError, match="how_many_weights= goes with an FIR"):
        quiet(sensor().keep_each_frequency_that, is_below=10, time_step=0.005, how_many_weights=51)
    with pytest.raises(SimplydataError, match="transition_width= goes with"):
        quiet(sensor().keep_each_frequency_that, is_below=10, time_step=0.005, transition_width=2)
    with pytest.raises(SimplydataError, match="too wide"):
        quiet(sensor().keep_each_frequency_that, is_below=10, time_step=0.005, test_method="fir least squares",
              transition_width=30)


def test_frequency_filter_of_an_fir_design_is_a_system_with_its_weights():
    system = quiet(sdata.frequency_filter, keep_below=10, time_step=0.005, test_method="fir", how_many_weights=31)
    taps = signal.firwin(31, 10, fs=200)
    got = quiet(system.frequency_response, between=[1, 90], how_many=5, unit="cycles per second").as_pandas()
    w, h = signal.freqz(taps, [1.0], worN=np.logspace(0, np.log10(90), 5), fs=200)
    assert got["gain"].to_numpy() == pytest.approx(np.abs(h), rel=1e-10)


def test_table_add_filtered_column_takes_the_fir_options():
    table = sdata.table(sdata.get_example("sensor"))
    quiet(table.add_filtered_column, "slow", from_column="signal", keep_below=10, sorted_by="time",
          test_method="fir equiripple", how_many_weights=41, transition_width=4)
    taps = signal.remez(41, [0, 8, 12, 100], [1, 0], fs=200)
    in_time = table.as_pandas().sort_values("time")
    x = np.asarray(in_time["signal"], dtype=float)
    assert np.asarray(in_time["slow"]) == pytest.approx(signal.filtfilt(taps, [1.0], x), rel=1e-12, abs=1e-12)


# ---------------------------------------------------------------------------------------- order finding
@pytest.mark.parametrize("method, finder, design", [
    ("butterworth", signal.buttord, lambda n, wn: signal.butter(n, wn, output="sos", fs=200)),
    ("chebyshev", signal.cheb1ord, lambda n, wn: signal.cheby1(n, 0.5, wn, output="sos", fs=200)),
    ("chebyshev 2", signal.cheb2ord, lambda n, wn: signal.cheby2(n, 40, wn, output="sos", fs=200)),
    ("elliptic", signal.ellipord, lambda n, wn: signal.ellip(n, 0.5, 40, wn, output="sos", fs=200)),
])
def test_find_order_for_is_scipys_order_selection(method, finder, design, capsys):
    nums = sensor()
    nums.keep_each_frequency_that(is_below=10, time_step=0.005, test_method=method, find_order_for={"loss_at": 20})
    n, wn = finder(10, 20, 0.5, 40, fs=200)
    assert f"steepness {n} found by SciPy {finder.__name__}" in capsys.readouterr().out
    assert values(nums) == pytest.approx(signal.sosfiltfilt(design(n, wn), raw()), rel=1e-10, abs=1e-12)


def test_find_order_for_a_band_and_the_kaiser_window():
    system = quiet(sdata.frequency_filter, keep_between=[20, 40], time_step=0.005, find_order_for={"loss_at": [10, 60]})
    n, wn = signal.buttord([20, 40], [10, 60], 0.5, 40, fs=200)
    b, a = signal.sos2tf(signal.butter(n, wn, btype="bandpass", output="sos", fs=200))
    got = system.table().as_pandas()
    assert got["denominator"].to_numpy() == pytest.approx(a, rel=1e-9, abs=1e-12)
    nums = sensor()
    quiet(nums.keep_each_frequency_that, is_below=10, time_step=0.005, test_method="fir",
          find_order_for={"loss_at": 20})
    numtaps, beta = signal.kaiserord(40, 10 / 100)
    numtaps += 1 - numtaps % 2
    taps = signal.firwin(numtaps, 15, window=("kaiser", beta), fs=200)
    assert values(nums) == pytest.approx(signal.filtfilt(taps, [1.0], raw()), rel=1e-12, abs=1e-12)


def test_find_order_for_is_checked():
    with pytest.raises(SimplydataError, match="above the cutoff"):
        quiet(sensor().keep_each_frequency_that, is_below=10, time_step=0.005, find_order_for={"loss_at": 5})
    with pytest.raises(SimplydataError, match="loss_at"):
        quiet(sensor().keep_each_frequency_that, is_below=10, time_step=0.005, find_order_for=20)
    with pytest.raises(SimplydataError, match="bessel"):
        quiet(sensor().keep_each_frequency_that, is_below=10, time_step=0.005, test_method="bessel",
              find_order_for={"loss_at": 20})
    with pytest.raises(SimplydataError, match="leave"):
        quiet(sensor().keep_each_frequency_that, is_below=10, time_step=0.005, steepness=6,
              find_order_for={"loss_at": 20})


# ---------------------------------------------------------------------------------------- analog filters
@pytest.mark.parametrize("method, prototype", [
    ("butterworth", lambda: signal.buttap(4)),
    ("chebyshev", lambda: signal.cheb1ap(4, 0.5)),
    ("chebyshev 2", lambda: signal.cheb2ap(4, 40)),
    ("elliptic", lambda: signal.ellipap(4, 0.5, 40)),
])
def test_analog_band_filter_is_the_prototype_moved_by_lp2bp(method, prototype):
    system = quiet(sdata.frequency_filter, keep_between=[1, 5], analog=True, test_method=method)
    z, p, k = prototype()
    w0, bw = 2 * np.pi * np.sqrt(1 * 5), 2 * np.pi * (5 - 1)
    zz, pp, kk = signal.lp2bp_zpk(z, p, k, wo=w0, bw=bw)  # analog: the band edges as given, nothing pre-warped
    b, a = signal.zpk2tf(zz, pp, kk)
    got = system.table().as_pandas()
    top = np.concatenate([np.zeros(len(a) - len(b)), b])
    assert got["denominator"].to_numpy() == pytest.approx(a / a[0], rel=1e-8)
    assert got["numerator"].to_numpy() == pytest.approx(top / a[0], rel=1e-8, abs=1e-6 * abs(kk))


@pytest.mark.parametrize("option, move", [
    ("keep_below", lambda z, p, k: signal.lp2lp_zpk(z, p, k, wo=2 * np.pi * 3)),
    ("keep_above", lambda z, p, k: signal.lp2hp_zpk(z, p, k, wo=2 * np.pi * 3)),
])
def test_analog_low_and_high_are_lp2lp_and_lp2hp(option, move):
    system = quiet(sdata.frequency_filter, analog=True, **{option: 3})
    zz, pp, kk = move(*signal.buttap(4))
    poles = system._poles()
    assert np.sort_complex(poles) == pytest.approx(np.sort_complex(pp), rel=1e-10)


def test_analog_band_stop_and_bessel_and_the_order_found():
    system = quiet(sdata.frequency_filter, remove_between=[1, 5], analog=True)
    pp = signal.lp2bs_zpk(*signal.buttap(4), wo=2 * np.pi * np.sqrt(5), bw=2 * np.pi * 4)[1]
    assert np.sort_complex(system._poles()) == pytest.approx(np.sort_complex(pp), rel=1e-8)
    system = quiet(sdata.frequency_filter, keep_below=3, analog=True, test_method="bessel")
    pp = signal.lp2lp_zpk(*signal.besselap(4, norm="phase"), wo=2 * np.pi * 3)[1]
    assert np.sort_complex(system._poles()) == pytest.approx(np.sort_complex(pp), rel=1e-10)
    system = quiet(sdata.frequency_filter, keep_below=3, analog=True, find_order_for={"loss_at": 6})
    n, wn = signal.buttord(2 * np.pi * 3, 2 * np.pi * 6, 0.5, 40, analog=True)
    assert len(system._poles()) == n
    pp = signal.butter(n, wn, analog=True, output="zpk")[1]
    assert np.sort_complex(system._poles()) == pytest.approx(np.sort_complex(pp), rel=1e-9)


def test_analog_filter_is_continuous_and_refuses_steps():
    system = quiet(sdata.frequency_filter, keep_below=3, analog=True)
    assert system._time_step is None
    w = 2 * np.pi * np.array([1.0, 3.0, 9.0])
    got = quiet(system.frequency_response, between=[1, 9], how_many=3).as_pandas()["gain"].to_numpy()
    b, a = signal.butter(4, 2 * np.pi * 3, analog=True)
    assert got == pytest.approx(np.abs(signal.freqs(b, a, worN=w)[1]), rel=1e-10)
    with pytest.raises(SimplydataError, match="leave out time_step"):
        quiet(sdata.frequency_filter, keep_below=3, analog=True, time_step=0.01)
    with pytest.raises(SimplydataError, match="notch"):
        quiet(sdata.frequency_filter, remove_at=3, analog=True)


# ---------------------------------------------------------------------------------------- starts, delay, gammatone
def test_start_from_first_value_is_sosfilt_with_its_steady_state():
    nums = sensor()
    quiet(nums.keep_each_frequency_that, is_below=10, time_step=0.005, both_ways=False, start_from="first value")
    sos = signal.butter(4, 10, output="sos", fs=200)
    x = raw()
    assert values(nums) == pytest.approx(signal.sosfilt(sos, x, zi=signal.sosfilt_zi(sos) * x[0])[0], rel=1e-12)
    nums = sensor()
    quiet(nums.keep_each_frequency_that, is_below=10, time_step=0.005, both_ways=False, start_from="first value",
          test_method="fir", how_many_weights=31)
    taps = signal.firwin(31, 10, fs=200)
    assert values(nums) == pytest.approx(signal.lfilter(taps, [1.0], x, zi=signal.lfilter_zi(taps, [1.0]) * x[0])[0],
                                         rel=1e-12)
    with pytest.raises(SimplydataError, match="both_ways=False"):
        quiet(sensor().keep_each_frequency_that, is_below=10, time_step=0.005, start_from="first value")


def test_with_least_delay_is_minimum_phase():
    nums = sensor()
    quiet(nums.keep_each_frequency_that, is_below=10, time_step=0.005, test_method="fir", how_many_weights=41,
          both_ways=False, with_least_delay=True)
    taps = signal.minimum_phase(signal.firwin(41, 10, fs=200), method="homomorphic", half=False)
    assert values(nums) == pytest.approx(signal.lfilter(taps, [1.0], raw()), rel=1e-12, abs=1e-12)
    with pytest.raises(SimplydataError, match="FIR"):
        quiet(sensor().keep_each_frequency_that, is_below=10, time_step=0.005, both_ways=False, with_least_delay=True)
    with pytest.raises(SimplydataError, match="both_ways=False"):
        quiet(sensor().keep_each_frequency_that, is_below=10, time_step=0.005, test_method="fir",
              with_least_delay=True)


def test_gammatone_keeps_one_frequency():
    nums = sensor()
    quiet(nums.keep_each_frequency_that, is_equal_to=5, time_step=0.005, test_method="gammatone")
    b, a = signal.gammatone(5, "iir", fs=200)
    assert values(nums) == pytest.approx(signal.filtfilt(b, a, raw()), rel=1e-10, abs=1e-12)
    with pytest.raises(SimplydataError, match="keeps one frequency"):
        quiet(sensor().remove_each_frequency_that, is_equal_to=5, time_step=0.005, test_method="gammatone")


# ---------------------------------------------------------------------------------------- system forms
def test_sections_of_a_filter_and_of_any_system():
    system = quiet(sdata.frequency_filter, keep_below=10, time_step=0.005)
    got = quiet(system.table, form="sections").as_pandas().iloc[:, 1:].to_numpy()
    assert got == pytest.approx(signal.butter(4, 10, output="sos", fs=200), rel=1e-12, abs=1e-15)
    plain = quiet(sdata.system, "(z**2 + 1) / (z**2 - 0.5*z + 0.06)", time_step=0.1)
    got = quiet(plain.table, form="second-order sections").as_pandas().iloc[:, 1:].to_numpy()
    assert got == pytest.approx(signal.zpk2sos(*signal.tf2zpk([1, 0, 1], [1, -0.5, 0.06])), rel=1e-12, abs=1e-15)


def test_a_system_from_sections_is_sos2tf():
    sos = signal.butter(4, 10, output="sos", fs=200)
    system = quiet(sdata.system, sections=sos, time_step=0.005)
    b, a = signal.sos2tf(sos)
    got = system.table().as_pandas()
    assert got["numerator"].to_numpy() == pytest.approx(b, rel=1e-10)
    assert got["denominator"].to_numpy() == pytest.approx(a, rel=1e-10)
    assert np.sort_complex(system._poles()) == pytest.approx(np.sort_complex(signal.sos2zpk(sos)[1]), rel=1e-12)
    with pytest.raises(SimplydataError, match="time_step="):
        quiet(sdata.system, sections=sos)


def test_partial_fractions_are_residue_and_residuez_and_come_back():
    system = quiet(sdata.system, "(s + 3) / (s**2 + 3*s + 2)")
    got = quiet(system.table, form="partial fractions").as_pandas()
    r, p, k = signal.residue([1, 3], [1, 3, 2])
    assert got["residue (real part)"].to_numpy() == pytest.approx(r.real, abs=1e-12)
    assert got["pole (real part)"].to_numpy() == pytest.approx(p.real, abs=1e-12)
    back = quiet(sdata.system, residues=r, poles=p)
    assert back.table().as_pandas()["numerator"].to_numpy() == pytest.approx([0, 1, 3], abs=1e-12)
    steps = quiet(sdata.system, "(z + 1) / (z**2 - 0.5*z + 0.06)", time_step=0.1)
    got = quiet(steps.table, form="partial fractions").as_pandas()
    r, p, k = signal.residuez([0, 1, 1], [1, -0.5, 0.06])
    fractions = got[got["kind"] == "fraction"]
    assert fractions["residue (real part)"].to_numpy() == pytest.approx(r.real, rel=1e-12)
    assert got[got["kind"] == "direct term"]["residue (real part)"].to_numpy() == pytest.approx(k, rel=1e-12)
    back = quiet(sdata.system, residues=r, poles=p, direct_terms=k, time_step=0.1)
    b, a = signal.invresz(r, p, k)
    assert back.table().as_pandas()["denominator"].to_numpy() == pytest.approx(a, rel=1e-12)


def test_move_poles_to_is_place_poles():
    system = quiet(sdata.system, "1 / (s**2 + 2*s + 5)")
    moved = quiet(system.move_poles_to, [-2, -3])
    assert np.sort(moved._poles().real) == pytest.approx([-3, -2], rel=1e-10)
    a, b, c, d = signal.tf2ss([1], [1, 2, 5])
    k = signal.place_poles(a, b, [-2, -3]).gain_matrix
    num, den = signal.ss2tf(a - b @ k, b, c - d @ k, d)
    assert moved.table().as_pandas()["denominator"].to_numpy() == pytest.approx(den.ravel(), rel=1e-10)
    moved = quiet(system.move_poles_to, [-1 + 1j, -1 - 1j])
    assert np.sort_complex(moved._poles()) == pytest.approx(np.array([-1 - 1j, -1 + 1j]), rel=1e-10)
    with pytest.raises(SimplydataError, match="needs 2 poles"):
        quiet(system.move_poles_to, [-2])
    with pytest.raises(SimplydataError, match="pairs"):
        quiet(system.move_poles_to, [-1 + 1j, -2])


def test_frequency_response_with_delay_is_group_delay():
    system = quiet(sdata.frequency_filter, keep_below=10, time_step=0.005)
    got = quiet(system.frequency_response, between=[1, 50], how_many=4, with_delay=True).as_pandas()
    b, a = signal.sos2tf(signal.butter(4, 10, output="sos", fs=200))
    f = np.logspace(0, np.log10(50), 4)
    expected = signal.group_delay((b, a), w=f, fs=200)[1] * 0.005
    assert got["delay"].to_numpy() == pytest.approx(expected, rel=1e-8)
    with pytest.raises(SimplydataError, match="in steps"):
        quiet(quiet(sdata.system, "1 / (s + 1)").frequency_response, with_delay=True)


# ---------------------------------------------------------------------------------------- spectra
def test_fourier_over_time_is_short_time_fft_and_comes_back():
    nums = sensor()
    table = quiet(nums.take_fourier_transform, time_step=0.005, over_time=True, window=64)
    sft = signal.ShortTimeFFT(signal.get_window("hann", 64), hop=32, fs=200)
    z = sft.stft(raw())
    got = table.as_pandas()
    assert len(got) == z.size
    assert got["real part"].to_numpy() == pytest.approx(z.T.ravel().real, abs=1e-12)
    assert got["imaginary part"].to_numpy() == pytest.approx(z.T.ravel().imag, abs=1e-12)
    assert sorted(set(got["time"])) == pytest.approx(sft.t(len(raw())))
    back = quiet(sdata.find_inverse_fourier_transform, table)
    assert values(back) == pytest.approx(raw(), abs=1e-10)


def test_fourier_between_is_zoom_fft_and_the_fft_at_its_frequencies():
    x = raw()
    table = quiet(sensor().take_fourier_transform, time_step=0.005, between=[0, 50], how_many=51)
    got = table.as_pandas()
    z = signal.zoom_fft(x, [0, 50], m=51, fs=200, endpoint=True)
    assert got["real part"].to_numpy() == pytest.approx(z.real, abs=1e-9)
    full = np.fft.fft(x)  # 1000 readings at 200 a second: bins every 0.2, so 0, 1, ..., 50 are bins 0, 5, ..., 250
    assert got["size"].to_numpy() == pytest.approx(np.abs(full[::5][:51]), rel=1e-9)
    w = np.exp(-2j * np.pi * 1 / 200)
    assert z == pytest.approx(signal.czt(x, 51, w=w, a=1), abs=1e-8)
    with pytest.raises(SimplydataError, match="cannot give the numbers back"):
        quiet(sdata.find_inverse_fourier_transform, table)


def test_spectrum_over_time_is_scipys_spectrogram():
    got = quiet(sensor().find_spectrum, time_step=0.005, over_time=True, window=100).as_pandas()
    f, t, p = signal.spectrogram(raw(), fs=200, window="hann", nperseg=100, noverlap=50, detrend="constant",
                                 scaling="density", mode="psd")
    assert got["power"].to_numpy() == pytest.approx(p.T.ravel(), rel=1e-12)
    assert got["time"].to_numpy()[:: len(f)] == pytest.approx(t)
    db = quiet(sensor().find_spectrum, time_step=0.005, over_time=True, window=100, show="decibels",
               between=[0, 20]).as_pandas()
    assert set(db.columns) == {"time", "frequency", "power (decibels)"} and db["frequency"].max() <= 20


# ---------------------------------------------------------------------------------------- waves, resampling, phase
def test_maximum_length_sequence_and_polynomial_sweep():
    mls = quiet(sdata.make_wave, "maximum length sequence", time_step=0.01, how_many=127)
    assert values(mls) == pytest.approx(signal.max_len_seq(7, length=127)[0].astype(float))
    assert values(quiet(sdata.make_wave, "mls", time_step=0.01, how_many=20)) == pytest.approx(
        signal.max_len_seq(5, length=20)[0].astype(float))
    sweep = quiet(sdata.make_wave, "chirp", sweep="polynomial", frequency=[2, 1], time_step=0.01, how_many=300)
    assert values(sweep) == pytest.approx(signal.sweep_poly(np.arange(300) * 0.01, [2, 1]), abs=1e-12)
    with pytest.raises(SimplydataError, match="polynomial"):
        quiet(sdata.make_wave, "chirp", sweep="polynomial", frequency=3, time_step=0.01, how_many=30)


@pytest.mark.parametrize("method, make, read", [
    ("cubic spline", signal.cspline1d, signal.cspline1d_eval),
    ("quadratic spline", signal.qspline1d, signal.qspline1d_eval),
])
def test_change_time_step_by_spline(method, make, read):
    nums = sensor()
    quiet(nums.change_time_step, to=0.002, time_step=0.005, test_method=method)
    new_times = np.arange(int(np.floor(999 * 0.005 / 0.002 + 1e-9)) + 1) * 0.002
    assert values(nums) == pytest.approx(read(make(raw()), new_times, dx=0.005, x0=0.0), rel=1e-12, abs=1e-12)
    assert nums._time_step == pytest.approx(0.002)


def test_find_phase_locking_to_is_vectorstrength():
    events = [0.01, 0.11, 0.205, 0.31, 0.4, 0.52, 0.61]
    nums = sdata.number_list(events)
    strength = quiet(nums.find_phase_locking_to, period=0.1)
    s, ph = signal.vectorstrength(events, 0.1)
    assert strength == pytest.approx(s, rel=1e-12)
    table = quiet(nums.find_phase_locking_to, period=[0.1, 0.2, 0.3]).as_pandas()
    s, ph = signal.vectorstrength(events, [0.1, 0.2, 0.3])
    assert table["strength"].to_numpy() == pytest.approx(s, rel=1e-12)
    assert table["phase (degrees)"].to_numpy() == pytest.approx(np.degrees(ph), rel=1e-12)
    with pytest.raises(SimplydataError, match="period="):
        quiet(nums.find_phase_locking_to)


# ---------------------------------------------------------------------------------------- help pointers
@pytest.mark.parametrize("typed, word", [
    ("scipy.signal.buttord", "find_order_for"), ("signal.kaiserord", "find_order_for"),
    ("signal.lp2bp", "analog=True"), ("scipy.signal.buttap", "analog=True"), ("signal.tf2sos", 'form="sections"'),
    ("signal.residue", "partial fractions"), ("signal.invres", "residues="), ("signal.place_poles", "move_poles_to"),
    ("signal.group_delay", "with_delay=True"), ("signal.stft", "over_time=True"), ("signal.istft", "inverse"),
    ("signal.zoom_fft", "between="), ("signal.czt", "between="), ("signal.firwin", '"fir"'),
    ("signal.firls", "fir least squares"), ("signal.remez", "fir equiripple"),
    ("signal.firwin2", "fir frequency sampling"), ("signal.minimum_phase", "with_least_delay"),
    ("signal.gammatone", 'test_method="gammatone"'), ("signal.sosfilt_zi", "start_from"),
    ("signal.max_len_seq", "maximum length"),
    ("signal.sweep_poly", "polynomial"), ("signal.cspline1d", "cubic spline"),
    ("signal.vectorstrength", "find_phase_locking_to"), ("signal.bilinear", 'test_method="bilinear"'),
    ("signal.sos2tf", "sections="), ("signal.ss2tf", "sdata.system(a="),
])
def test_help_points_scipy_signal_names_to_their_word(typed, word, capsys):
    sdata.help(typed)
    assert word in capsys.readouterr().out


def test_two_dimensional_and_helper_names_point_to_the_hand_over(capsys):
    for name in ("check_COLA", "symiirorder1"):
        sdata.help(f"scipy.signal.{name}")
        assert "as_numpy() hands" in capsys.readouterr().out, name
    # the 2-D names became grid words in batches 20-21: their pointers name the word
    for name, word in (("order_filter", 'grid.smooth(test_method="rank"'), ("hilbert2", "grid.find_envelope()"),
                       ("correlate2d", "grid.convolve_with(")):
        sdata.help(f"scipy.signal.{name}")
        assert word in capsys.readouterr().out, name


# ---------------------------------------------------------------------------------------- independent review fixes
@pytest.mark.parametrize("options, design", [
    ({"keep_below": 1000}, lambda: signal.butter(4, 2 * np.pi * 1000, analog=True)),
    ({"keep_above": 50, "steepness": 6}, lambda: signal.butter(6, 2 * np.pi * 50, "highpass", analog=True)),
    ({"keep_between": [1, 5], "steepness": 8, "test_method": "chebyshev 2"},
     lambda: signal.cheby2(8, 40, 2 * np.pi * np.array([1, 5]), "bandpass", analog=True)),
])
def test_analog_filters_keep_every_coefficient_scipy_designed(options, design):
    """The relative noise trim of System once zeroed the small real coefficients of an analog design."""
    system = quiet(sdata.frequency_filter, analog=True, **options)
    b, a = design()
    assert len(system._poles()) == len(a) - 1
    f = np.array([0.5, 1.0, 2.0]) * (options.get("keep_below") or options.get("keep_above") or 2.5)
    got = quiet(system.frequency_response, between=[f[0], f[-1]], how_many=3, unit="cycles per second")
    expected = np.abs(signal.freqs(b, a, worN=2 * np.pi * f)[1])
    assert got.as_pandas()["gain"].to_numpy() == pytest.approx(expected, rel=1e-8, abs=1e-12)


def test_sections_of_a_formula_are_not_one_step_early():
    system = quiet(sdata.system, "0.5 / (z - 0.5)", time_step=0.1)
    rows = quiet(system.table, form="sections")
    sos = np.array(rows.as_pandas().iloc[:, 1:].to_numpy(), dtype=float, order="C")
    impulse = signal.unit_impulse(6)
    expected = np.asarray(signal.dimpulse(signal.dlti([0.5], [1, -0.5], dt=0.1), n=6)[1][0]).ravel()
    assert signal.sosfilt(sos, impulse) == pytest.approx(expected, abs=1e-14)  # 0, 0.5, 0.25 ... not 0.5, 0.25
    three = quiet(sdata.system, "1 / ((z - 0.5) * (z - 0.2) * (z + 0.1))", time_step=0.1)  # three steps of delay
    rows3 = np.array(quiet(three.table, form="sections").as_pandas().iloc[:, 1:].to_numpy(), dtype=float, order="C")
    expected3 = np.asarray(signal.dimpulse(signal.dlti(three._num, three._den, dt=0.1), n=8)[1][0]).ravel()
    assert signal.sosfilt(rows3, signal.unit_impulse(8)) == pytest.approx(expected3, abs=1e-14)
    back = quiet(sdata.system, sections=rows, time_step=0.1)  # the table itself, its section column left out
    assert quiet(back.impulse_response, how_many=6).as_pandas()["output"].to_numpy() == pytest.approx(expected,
                                                                                                    abs=1e-14)
    with pytest.raises(SimplydataError, match="in steps"):
        quiet(quiet(sdata.system, "1 / (s + 1)").table, form="sections")


def test_group_delay_of_a_narrow_band_is_added_up_over_its_sections(capsys):
    system = quiet(sdata.frequency_filter, keep_between=[20, 21], time_step=0.005, steepness=8)
    got = system.frequency_response(between=[20.5, 30], how_many=2, with_delay=True).as_pandas()["delay"]
    sos = signal.butter(8, [20, 21], btype="bandpass", output="sos", fs=200)
    expected = [sum(signal.group_delay((r[:3], r[3:]), w=[f], fs=200)[1][0] for r in sos) * 0.005 for f in (20.5, 30)]
    assert got.to_numpy() == pytest.approx(expected, rel=1e-9)
    assert got.iloc[0] > 1.5  # the multiplied-out formula gave 0 here
    assert "may not be exact" in capsys.readouterr().out  # SciPy's warning is said, not hidden


def test_find_order_for_run_both_ways_says_the_losses_double(capsys):
    quiet_out = sensor()
    quiet_out.keep_each_frequency_that(is_below=10, time_step=0.005, find_order_for={"loss_at": 20})
    out = capsys.readouterr().out
    assert "the losses double: at most 1 dB lost where it keeps and at least 80 dB removed" in out
    assert "steepness 16 in effect" in out


def test_a_pole_given_twice_is_refused_with_the_reason():
    with pytest.raises(SimplydataError, match="acker"):
        quiet(quiet(sdata.system, "1 / (s**2 + 2*s + 5)").move_poles_to, [-2, -2])
