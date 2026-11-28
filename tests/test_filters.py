"""keep_frequencies / remove_frequencies, find_peaks / find_dips, fourier_transform, envelope, convolution,
change_time_step, sdata.make_wave and sdata.make_window_shape, checked against R.

Reference values: R 4.6.2 with signal 1.8.1, gsignal 0.3.7 and pracma 2.4.6 (ref_partC_filters.R,
ref_partC_more.R, ref_waves.R in the v0.6 scratch folder): x <- read.csv("sensor.csv")$signal
(200 readings per second).
"""

import numpy as np
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from conftest import example_frame


def sensor():
    return sdata.get_example("sensor").get_column("signal")


def values(nums):
    return np.asarray(nums._values, dtype=float)


def test_low_pass_both_ways_matches_r_in_the_middle(capsys):
    nums = sensor()
    nums.keep_each_frequency_that(is_below=10, time_step=0.005)
    # R: signal::filtfilt(signal::butter(4, 10 / 100), x)[c(300, 500)]
    assert values(nums)[[299, 499]] == pytest.approx([0.472444558628213, 0.360961693964092], rel=1e-8)
    out = capsys.readouterr().out
    assert "Kept the frequencies below 10 in 1000 readings (0.005 apart): Butterworth filter, steepness 4" in out
    assert "steepness 8 in effect" in out and "signal::butter(4, 0.1)" in out


def test_low_pass_one_way_matches_r_exactly():
    nums = sensor()
    nums.keep_each_frequency_that(is_below=10, time_step=0.005, both_ways=False)
    # R: signal::filter(signal::butter(4, 10 / 100), x)[c(1, 2, 500)]
    assert values(nums)[[0, 1, 499]] == pytest.approx([-9.910895072833e-05, -0.000434960360571508, 1.1659453665398],
                                                      rel=1e-9)


def test_filter_coefficients_match_r():
    from simplydata import _filters

    def ba(kind, cut, method="butterworth", steepness=4):
        return _filters.coefficients(_filters.design(kind, cut, 0.005, method, steepness))

    b, a = ba("low", 10)
    assert b[:2] == pytest.approx([0.000416599204406599, 0.0016663968176264], rel=1e-9)  # signal::butter(4, 0.1)$b
    assert a[:2] == pytest.approx([1, -3.18063854887472], rel=1e-12)
    assert ba("high", 2)[0][:2] == pytest.approx([0.921170993499942, -3.68468397399977], rel=1e-9)  # type = "high"
    assert ba("pass", [3, 8], steepness=2)[1][:3] == pytest.approx([1, -3.73387569709592, 5.27377500341993], rel=1e-9)
    b, a = ba("low", 10, "chebyshev")  # R: signal::cheby1(4, 0.5, 0.1)
    assert b[:2] == pytest.approx([0.000182040286002943, 0.000728161144011772], rel=1e-8)
    assert a[:2] == pytest.approx([1, -3.53281334706192], rel=1e-9)
    assert ba("low", 10, "chebyshev 2")[0][:2] == pytest.approx([0.00973557065607794, -0.0321353678092417], rel=1e-8)
    # R: signal::ellip(4, 0.5, 40, 0.1)$a[1:2]; R signal solves the elliptic degree equation less precisely
    assert ba("low", 10, "elliptic")[1][:2] == pytest.approx([1, -3.53221477677517], rel=1e-5)


def test_band_stop_and_notch():
    nums = sensor()
    nums.remove_each_frequency_that(is_between=[45, 55], time_step=0.005, steepness=2)
    # R: signal::filtfilt(signal::butter(2, c(45, 55) / 100, type = "stop"), x)[500]
    assert values(nums)[499] == pytest.approx(0.701235162036394, rel=1e-8)
    from simplydata import _filters

    b, a = _filters.coefficients(_filters.design_single(False, 50, 0.005, width=1))
    # R: SciPy's iirnotch formula written out (ref_partC_filters.R)
    assert b == pytest.approx([0.984533708596897, 0, 0.984533708596897], abs=1e-12)
    assert a == pytest.approx([1, 0, 0.969067417193793], abs=1e-12)


def test_fir_is_scipy_firwin_run_both_ways():
    # Offered since plan 2.7 (approved by Manish 2026-11-28): SciPy firwin, not R signal::fir1 (R makes fir1 by
    # frequency sampling, so its weights add up to 1.0015); the weights are firwin's (tests/test_full_signals.py
    # checks them against firwin's own formula)
    from scipy import signal

    nums = sensor()
    raw = values(nums).copy()
    nums.keep_each_frequency_that(is_below=10, time_step=0.005, test_method="fir")
    taps = signal.firwin(101, 10, window="hamming", fs=200)
    assert values(nums) == pytest.approx(signal.filtfilt(taps, [1.0], raw), rel=1e-12, abs=1e-12)


def test_filter_errors():
    nums = sensor()
    with pytest.raises(SimplydataError, match="exactly one of"):
        nums.keep_each_frequency_that(is_below=5, is_above=1, time_step=0.005)
    with pytest.raises(SimplydataError, match="the highest frequency"):
        nums.keep_each_frequency_that(is_below=150, time_step=0.005)
    with pytest.raises(SimplydataError, match="method"):
        nums.keep_each_frequency_that(is_below=5, time_step=0.005, test_method="kalman")
    with pytest.raises(SimplydataError, match="lower first"):
        nums.keep_each_frequency_that(is_between=[5, 1], time_step=0.005)


def test_peaks_match_r_pracma(capsys):
    result = sensor().find_each_peak_that(is_at_least=1, apart=10)
    # R: pk <- pracma::findpeaks(x, minpeakheight = 1, minpeakdistance = 10); nrow(pk) = 41; first positions
    frame = result._frame.to_pandas()
    assert len(frame) == 41
    assert frame["position"].tolist()[:5] == [4, 14, 50, 91, 133]
    # R: the prominence by its definition (prom() in ref_partC_more.R) of the first peak = 0.6494
    assert frame["stands out by"].iloc[0] == pytest.approx(0.6494, rel=1e-12)
    out = capsys.readouterr().out
    assert "Found 41 peaks" in out and "the highest is 3.48 at position 778" in out  # R: max at 778, 3.4792


def test_dips_match_r_pracma():
    # R: nrow(pracma::findpeaks(-x, minpeakheight = 1, minpeakdistance = 10)) = 24
    assert len(sensor().find_each_dip_that(is_at_most=-1, apart=10)._frame) == 24


def test_fourier_and_back():
    nums = sdata.get_example("sensor").get_column("signal").keep_first_numbers(8)
    table = nums.take_fourier_transform(show="all")
    frame = table._frame.to_pandas()
    # R: f <- fft(x[1:8]); Mod(f)[1:5]; Arg(f)[2] * 180 / pi
    assert frame["size"].tolist()[:5] == pytest.approx([4.3293, 1.82513172796631, 0.175694763723908,
                                                        0.985125390785714, 1.5627], rel=1e-12)
    assert frame["phase"].iloc[1] == pytest.approx(179.55464931432, rel=1e-12)
    back = sdata.find_inverse_fourier_transform(table)
    assert values(back)[:2] == pytest.approx([-0.2379, 0.6642], rel=1e-12)  # R: Re(fft(f, inverse = TRUE) / 8)


def test_envelope_matches_r():
    nums = sensor()
    nums.find_envelope()
    assert values(nums)[[0, 499]] == pytest.approx([0.954709332626447, 0.453261712062559], rel=1e-10)  # gsignal::hilbert


def test_convolution_matches_r():
    nums = sdata.number_list([1, 2, 3])
    nums.convolve_with([0, 1, 0.5])
    assert values(nums) == pytest.approx([0, 1, 2.5, 4, 1.5], abs=1e-12)  # R: convolve(a, rev(b), type = "open")
    nums = sdata.number_list([1, 2, 3, 4])
    nums.convolve_with([0, 1, 0.5], keep="overlap")
    assert values(nums) == pytest.approx([2.5, 4])  # R: type = "filter"
    nums = sdata.number_list([0, 1, 2.5, 4, 1.5])
    nums.deconvolve_by([1, 2, 3])
    assert values(nums) == pytest.approx([0, 1, 0.5], abs=1e-12)  # R: pracma::deconv(...)$q


def test_change_time_step():
    nums = sensor()
    nums.change_time_step(to=0.01, time_step=0.005, test_method="filter then keep")
    assert len(values(nums)) == 500 and nums._time_step == 0.01
    nums = sensor()
    nums.change_time_step(to=0.01, time_step=0.005)
    assert len(values(nums)) == 500


def test_waves_and_windows_match_r():
    nums = sdata.make_wave("square", frequency=5, time_step=0.01, how_many=10)
    assert values(nums) == pytest.approx([1] * 10)  # R: gsignal::square(2 * pi * 5 * t), t <- (0:9) * 0.01
    nums = sdata.make_wave("sawtooth", frequency=5, time_step=0.01, how_many=10)
    assert values(nums)[:4] == pytest.approx([-1, -0.9, -0.8, -0.7])  # R: gsignal::sawtooth(...)
    assert nums._time_step == 0.01
    assert values(sdata.make_window_shape("hann", how_many=5)) == pytest.approx([0, 0.5, 1, 0.5, 0])  # gsignal::hann(5)
    assert values(sdata.make_window_shape("hamming", how_many=5)) == pytest.approx([0.08, 0.54, 1, 0.54, 0.08])


def test_table_filter_and_peaks(capsys):
    import pandas as pd

    from simplydata.table import table as make_table

    for engine in ("pandas", "polars"):
        data = example_frame("sensor")
        t = make_table(data) if engine == "pandas" else make_table(data, fast=True)
        t.add_filtered_column("slow", from_column="signal", keep_below=10, sorted_by="time")
        # R: signal::filtfilt(signal::butter(4, 10 / 100), x)[500] (time steps of 0.005 s)
        assert np.asarray(t._frame["slow"].to_numpy(), dtype=float)[499] == pytest.approx(0.360961693964092, rel=1e-8)
        peaks = t.find_each_peak_that("signal", sorted_by="time", is_at_least=1, apart=0.05)
        frame = peaks._frame.to_pandas() if hasattr(peaks._frame, "to_pandas") else peaks._frame
        # R: pracma::findpeaks(x, minpeakheight = 1, minpeakdistance = 10): 41 peaks, the first at reading 4
        assert len(frame) == 41 and frame["position"].iloc[0] == 4
        assert frame["time"].iloc[0] == pytest.approx(0.015)
        t.undo()
        assert "slow" not in t._frame.columns
    out = capsys.readouterr().out
    assert 'the highest is 3.48 at time 3.885' in out


def test_wav_reading_matches_r_tuner(capsys):
    import pathlib

    file = pathlib.Path(__file__).parent / "data" / "tone_r.wav"
    # R: w <- tuneR::Wave(left = c(0L, 1000L, -2000L, 32767L, -32768L), right = 5:9, samp.rate = 8000, bit = 16)
    #    tuneR::writeWave(w, "tone_r.wav"); tuneR::readWave("tone_r.wav")@left, @right
    # sdata.number_list scales whole numbers to -1 to 1: in R, readWave(...)@left / 2^(16 - 1)
    left = sdata.number_list(str(file))
    assert values(left).tolist() == [v / 32768 for v in (0, 1000, -2000, 32767, -32768)]
    assert left._time_step == 1 / 8000
    out = capsys.readouterr().out
    assert "8,000 readings per second" in out and "16-bit whole numbers, scaled to -1 to 1 (divided by 2^15)" in out
    assert values(sdata.number_list(str(file), channel=2)).tolist() == [v / 32768 for v in (5, 6, 7, 8, 9)]
    with pytest.raises(SimplydataError, match="channel="):
        sdata.number_list(str(file), channel=3)


def test_wav_round_trip(tmp_path, capsys):
    nums = sdata.make_wave("sine", frequency=440, time_step=1 / 8000, how_many=800)
    nums.save(str(tmp_path / "tone.wav"))
    back = sdata.number_list(str(tmp_path / "tone.wav"))
    assert values(back) == pytest.approx(values(nums), abs=1e-7) and back._time_step == 1 / 8000
    nums.save(str(tmp_path / "tone16.wav"), bits=16)
    back = sdata.number_list(str(tmp_path / "tone16.wav"))
    assert values(back) == pytest.approx(values(nums), abs=1 / 32768)
    with pytest.raises(SimplydataError, match="time_step="):
        sdata.number_list([0.1, 0.2]).save(str(tmp_path / "x.wav"))


@pytest.mark.parametrize("engine", ["pandas", "polars"])
def test_add_envelope_column_matches_r(engine, capsys):
    from simplydata.table import table as make_table

    data = example_frame("sensor")
    t = make_table(data) if engine == "pandas" else make_table(data, fast=True)
    t.add_envelope_column("size", from_column="signal", sorted_by="time")
    t.add_envelope_column("turn", from_column="signal", show="frequency", sorted_by="time")
    t.add_envelope_column("signal_phase", from_column="signal", show="phase")
    got = t._frame.to_pandas() if hasattr(t._frame, "to_pandas") else t._frame
    # R: h <- gsignal::hilbert(x); Mod(h)[c(1, 500, 1000)]
    assert got["size"].to_numpy()[[0, 499, 999]] == pytest.approx(
        [0.954709332626447, 0.453261712062559, 0.122856561154862], rel=1e-10)
    # R: ph <- unwrap(Arg(h)) * 180 / pi; ph[c(1, 500)]; (diff(ph) / 360 / 0.005)[c(1, 500, 999)]
    assert got["signal_phase"].to_numpy()[[0, 499]] == pytest.approx([-104.429336719275, 6864.45442085428], rel=1e-10)
    assert got["turn"].to_numpy()[[0, 499, 998]] == pytest.approx(
        [40.0246074443493, -3.48555707784928, -55.8621502064792], rel=1e-8)
    assert np.isnan(float(got["turn"].to_numpy()[999]))
    out = capsys.readouterr().out
    assert 'The frequency of "signal" (cycles per unit of "time") in order of "time"' in out
    assert "gsignal::hilbert" in out
    t.undo()
    assert "signal_phase" not in t._frame.columns
    with pytest.raises(SimplydataError, match="already a column"):
        t.add_envelope_column("size", from_column="signal")
    with pytest.raises(SimplydataError, match="needs a name for the new column"):
        t.add_envelope_column(from_column="signal")  # every add_..._column word asks for the name


def test_add_envelope_column_for_each():
    import pandas as pd

    data = example_frame("sensor").assign(half=["first"] * 500 + ["second"] * 500)
    t = sdata.table(data)
    t.add_envelope_column("size", from_column="signal", sorted_by="time", for_each_group_in="half")
    size = t._frame["size"].to_numpy()
    # R: Mod(gsignal::hilbert(x[1:500]))[c(1, 500)], Mod(gsignal::hilbert(x[501:1000]))[c(1, 500)]
    assert size[[0, 499, 500, 999]] == pytest.approx(
        [0.339299130140183, 0.76920013401219, 0.954272677944954, 0.441922202475026], rel=1e-10)


@pytest.mark.parametrize("engine", ["pandas", "polars"])
def test_sinc_in_formulas_matches_r(engine):
    import pandas as pd

    from simplydata.table import table as make_table

    data = pd.DataFrame({"x": [0, 0.5, 1.5, -0.25, 3]})
    t = make_table(data) if engine == "pandas" else make_table(data, fast=True)
    t.add_column("s", "sinc(x)")
    got = t._frame["s"].to_list()
    # R: ifelse(x == 0, 1, sin(pi * x) / (pi * x))
    assert got == pytest.approx([1, 0.636619772367581, -0.212206590789194, 0.900316316157106, 0], rel=1e-12,
                                abs=1e-15)
    from simplydata._maths_formula import read_formula

    assert float(read_formula("sinc(x / 2)")({"x": 1.0})) == pytest.approx(0.636619772367581, rel=1e-12)


def test_show_filter_shows_the_chart_and_the_line_that_saves_it(monkeypatch, tmp_path, capsys):
    import warnings

    import matplotlib.pyplot as plt

    shown = []
    monkeypatch.setattr(plt, "show", lambda *a, **k: shown.append(1))
    nums = sensor()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        nums.keep_each_frequency_that(is_below=10, time_step=0.005, show_filter=True)
    out = capsys.readouterr().out
    line = 'To save this chart: sdata.frequency_filter(keep_below=10, time_step=0.005).chart().save("filter.png")'
    assert line in out and shown
    # the filtered numbers are the same as without the chart (R: signal::filtfilt(signal::butter(4, 0.1), x)[500])
    assert values(nums)[499] == pytest.approx(0.360961693964092, rel=1e-8)
    # the printed line works as it stands
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sdata.frequency_filter(keep_below=10, time_step=0.005).chart().save(str(tmp_path / "filter.png"))
    assert (tmp_path / "filter.png").exists()
    t = sdata.table(sdata.get_example("sensor"))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        t.add_filtered_column("hum", from_column="signal", remove_at=50, sorted_by="time", show_filter=True)
        sensor().remove_each_frequency_that(is_below=2, time_step=0.005, test_method="chebyshev", show_filter=True)
    out = capsys.readouterr().out
    assert "sdata.frequency_filter(remove_at=50, time_step=0.005).chart()" in out
    assert 'sdata.frequency_filter(keep_above=2, time_step=0.005, test_method="chebyshev").chart()' in out
    with pytest.raises(SimplydataError, match=r"show_filter= is True .* or False\. To save the chart: "
                                              r"sdata\.frequency_filter\(keep_below=10"):
        sensor().keep_each_frequency_that(is_below=10, time_step=0.005, show_filter="filter.png")
    with pytest.raises(SimplydataError, match="show_filter="):
        sensor().keep_each_frequency_that(is_below=10, time_step=0.005, show_filter=3)


def _write_pcm(path, width, whole_numbers):
    """A one-channel whole-number .wav file written with Python's wave module (8-bit is stored from 0 to 255)."""
    import wave

    if width == 1:
        raw = bytes(int(v) for v in whole_numbers)
    else:
        raw = b"".join(int(v).to_bytes(4, "little", signed=True)[:width] for v in whole_numbers)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(width)
        w.setframerate(8000)
        w.writeframes(raw)


@pytest.mark.parametrize("bits, stored, expected", [
    # R: w <- tuneR::readWave(file); (w@left - (w@bit == 8) * 128) / 2^(w@bit - 1)
    (8, [128, 0, 255, 192, 64], [0, -1, 0.9921875, 0.5, -0.5]),
    (16, [0, 1000, -2000, 32767, -32768], [0, 0.030517578125, -0.06103515625, 0.999969482421875, -1]),
    (24, [0, 1000, -2000, 8388607, -8388608], [0, 0.000119209289550781, -0.000238418579101562, 0.99999988079071, -1]),
    (32, [0, 1000, -2000, 2147483647, -2147483647], [0, 4.65661287307739e-07, -9.31322574615479e-07,
                                                    0.999999999534339, -0.999999999534339]),
])
def test_wav_files_of_every_size_read_to_one_scale_and_round_trip(tmp_path, capsys, bits, stored, expected):
    file = tmp_path / f"w{bits}.wav"
    _write_pcm(file, bits // 8, stored)
    nums = sdata.number_list(str(file))
    assert values(nums) == pytest.approx(expected, rel=1e-12, abs=1e-15)
    assert f"{bits}-bit whole numbers, scaled to -1 to 1" in capsys.readouterr().out
    nums.save(str(tmp_path / "again.wav"))  # 32-bit floating point keeps them
    assert values(sdata.number_list(str(tmp_path / "again.wav"))) == pytest.approx(expected, abs=1e-7)
    if bits == 16:  # saving 16-bit gives back the same whole numbers, none clipped
        from scipy.io import wavfile

        nums.save(str(tmp_path / "again16.wav"), bits=16)
        assert wavfile.read(str(tmp_path / "again16.wav"))[1].tolist() == stored
        assert "clipped" not in capsys.readouterr().out


def test_wav_16_bit_round_trip_keeps_every_value(tmp_path, capsys):
    from scipy.io import wavfile

    x = (np.sin(np.arange(800) / 10) * 20000).astype(np.int16)
    wavfile.write(str(tmp_path / "a16.wav"), 8000, x)
    sdata.number_list(str(tmp_path / "a16.wav")).save(str(tmp_path / "b16.wav"), bits=16)
    assert np.array_equal(wavfile.read(str(tmp_path / "b16.wav"))[1], x)
    assert "clipped" not in capsys.readouterr().out


def test_undo_after_change_time_step_brings_the_time_step_back(capsys):
    nums = sdata.make_wave("sine", frequency=5, time_step=0.01, how_many=100)
    nums.change_time_step(to=0.02)
    assert nums._time_step == 0.02 and len(values(nums)) == 50
    nums.undo()
    assert nums._time_step == 0.01 and len(values(nums)) == 100
    nums.change_time_step(to=0.02)
    nums.add(1)
    nums.start_again()
    assert nums._time_step == 0.01 and len(values(nums)) == 100


def test_change_time_step_remembers_the_step_it_gives(capsys):
    nums = sdata.make_wave("sine", frequency=5, time_step=0.01, how_many=101)
    capsys.readouterr()
    nums.change_time_step(to=0.03)  # 101 readings cannot become exactly 0.03 apart: 34 fill the same time
    assert len(values(nums)) == 34 and nums._time_step == pytest.approx(0.01 * 101 / 34, rel=1e-12)
    assert "The time step is 0.0297059, not exactly 0.03" in capsys.readouterr().out
    nums = sdata.make_wave("sine", frequency=5, time_step=0.01, how_many=100)
    nums.change_time_step(to=0.02)
    assert nums._time_step == 0.02 and "not exactly" not in capsys.readouterr().out


def test_bessel_matches_r_gsignal_with_the_prewarped_cutoff(capsys):
    from scipy import signal

    nums = sensor()
    nums.keep_each_frequency_that(is_below=10, time_step=0.005, test_method="bessel")
    # R: z <- gsignal::as.Arma(gsignal::bilinear(gsignal::besself(4, 2 * 200 * tan(pi * 10 / 200)), T = 1 / 200))
    #    signal::filtfilt(z, x)[c(300, 500)]
    assert values(nums)[[299, 499]] == pytest.approx([0.365463543645377, 0.330800987305200], rel=1e-10)
    out = capsys.readouterr().out
    assert "gsignal::besself(4, 2 * 200 * tan(pi * 10 / 200))" in out
    b, a = signal.sos2tf(signal.bessel(4, 30, "high", norm="phase", fs=200, output="sos"))
    # R: gsignal::as.Arma(gsignal::bilinear(gsignal::besself(4, 2 * 200 * tan(pi * 30 / 200), "high"), T = 1 / 200))
    assert b == pytest.approx([0.235195010278628, -0.940780041114512, 1.411170061671768, -0.940780041114512,
                               0.235195010278628], rel=1e-10)
    assert a == pytest.approx([1, -1.4502103303751783, 0.9699838065630142, -0.3045315433134006, 0.0383944842064527],
                              rel=1e-10)
    nums = sensor()
    nums.keep_each_frequency_that(is_between=[10, 30], time_step=0.005, test_method="bessel", steepness=2)
    # R: signal::filtfilt(gsignal::as.Arma(gsignal::bilinear(gsignal::besself(2, 2 * 200 * tan(pi * c(10, 30) / 200),
    #    type = "pass"), T = 1 / 200)), x)[c(300, 500)]
    assert values(nums)[[299, 499]] == pytest.approx([-0.263351352212425, 0.114621142699148], rel=1e-10)


def test_peaks_wide_at_least_needs_even_times():
    import pandas as pd

    from simplydata.table import table as make_table

    t = make_table(pd.DataFrame({"t": [0, 1, 2, 3, 5, 6, 7, 8.0], "x": [0, 1, 0, 2, 0, 3, 0, 1.0]}))
    with pytest.raises(SimplydataError, match="evenly spaced"):
        t.find_each_peak_that("x", sorted_by="t", wide_at_least=1)
    with pytest.raises(SimplydataError, match="evenly spaced"):
        t.find_each_dip_that("x", sorted_by="t", wide_at_least=1)
