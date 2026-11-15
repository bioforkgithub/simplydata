"""keep_frequencies / remove_frequencies, find_peaks / find_dips, fourier_transform, envelope, convolution,
change_time_step, sdata.wave and sdata.window_shape, checked against R.

Reference values: R 4.6.2 with signal 1.8.1, gsignal 0.3.7 and pracma 2.4.6 (ref_partC_filters.R,
ref_partC_more.R, ref_waves.R in the v0.6 scratch folder): x <- read.csv("sensor.csv")$signal
(200 readings per second).
"""

import numpy as np
import pytest

import simplydata as sdata
from simplydata import SimplydataError


def sensor():
    return sdata.numbers(sdata.example("sensor")["signal"])


def values(nums):
    return np.asarray(nums._values, dtype=float)


def test_low_pass_both_ways_matches_r_in_the_middle(capsys):
    nums = sensor()
    nums.keep_frequencies(below=10, time_step=0.005)
    # R: signal::filtfilt(signal::butter(4, 10 / 100), x)[c(300, 500)]
    assert values(nums)[[299, 499]] == pytest.approx([0.472444558628213, 0.360961693964092], rel=1e-8)
    out = capsys.readouterr().out
    assert "Kept the frequencies below 10 in 1000 readings (0.005 apart): Butterworth filter, steepness 4" in out
    assert "steepness 8 in effect" in out and "signal::butter(4, 0.1)" in out


def test_low_pass_one_way_matches_r_exactly():
    nums = sensor()
    nums.keep_frequencies(below=10, time_step=0.005, both_ways=False)
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
    nums.remove_frequencies(between=[45, 55], time_step=0.005, steepness=2)
    # R: signal::filtfilt(signal::butter(2, c(45, 55) / 100, type = "stop"), x)[500]
    assert values(nums)[499] == pytest.approx(0.701235162036394, rel=1e-8)
    from simplydata import _filters

    b, a = _filters.coefficients(_filters.design_single(False, 50, 0.005, width=1))
    # R: SciPy's iirnotch formula written out (ref_partC_filters.R)
    assert b == pytest.approx([0.984533708596897, 0, 0.984533708596897], abs=1e-12)
    assert a == pytest.approx([1, 0, 0.969067417193793], abs=1e-12)


def test_fir_is_not_offered_yet():
    # SciPy firwin and R signal::fir1(100, 0.1) give different weights (R's add up to 1.0015): owner to decide
    with pytest.raises(SimplydataError, match="not ready"):
        sensor().keep_frequencies(below=10, time_step=0.005, method="fir")


def test_filter_errors():
    nums = sensor()
    with pytest.raises(SimplydataError, match="exactly one of"):
        nums.keep_frequencies(below=5, above=1, time_step=0.005)
    with pytest.raises(SimplydataError, match="the highest frequency"):
        nums.keep_frequencies(below=150, time_step=0.005)
    with pytest.raises(SimplydataError, match="method"):
        nums.keep_frequencies(below=5, time_step=0.005, method="kalman")
    with pytest.raises(SimplydataError, match="lower first"):
        nums.keep_frequencies(between=[5, 1], time_step=0.005)


def test_peaks_match_r_pracma(capsys):
    result = sensor().find_peaks(at_least=1, apart=10)
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
    assert len(sensor().find_dips(at_most=-1, apart=10)._frame) == 24


def test_fourier_and_back():
    nums = sdata.numbers(sdata.example("sensor")["signal"][:8])
    table = nums.fourier_transform(show="all")
    frame = table._frame.to_pandas()
    # R: f <- fft(x[1:8]); Mod(f)[1:5]; Arg(f)[2] * 180 / pi
    assert frame["size"].tolist()[:5] == pytest.approx([4.3293, 1.82513172796631, 0.175694763723908,
                                                        0.985125390785714, 1.5627], rel=1e-12)
    assert frame["phase"].iloc[1] == pytest.approx(179.55464931432, rel=1e-12)
    back = sdata.inverse_fourier_transform(table)
    assert values(back)[:2] == pytest.approx([-0.2379, 0.6642], rel=1e-12)  # R: Re(fft(f, inverse = TRUE) / 8)


def test_envelope_matches_r():
    nums = sensor()
    nums.envelope()
    assert values(nums)[[0, 499]] == pytest.approx([0.954709332626447, 0.453261712062559], rel=1e-10)  # gsignal::hilbert


def test_convolution_matches_r():
    nums = sdata.numbers([1, 2, 3])
    nums.convolve_with([0, 1, 0.5])
    assert values(nums) == pytest.approx([0, 1, 2.5, 4, 1.5], abs=1e-12)  # R: convolve(a, rev(b), type = "open")
    nums = sdata.numbers([1, 2, 3, 4])
    nums.convolve_with([0, 1, 0.5], keep="overlap")
    assert values(nums) == pytest.approx([2.5, 4])  # R: type = "filter"
    nums = sdata.numbers([0, 1, 2.5, 4, 1.5])
    nums.deconvolve_by([1, 2, 3])
    assert values(nums) == pytest.approx([0, 1, 0.5], abs=1e-12)  # R: pracma::deconv(...)$q


def test_change_time_step():
    nums = sensor()
    nums.change_time_step(to=0.01, time_step=0.005, method="filter then keep")
    assert len(values(nums)) == 500 and nums._time_step == 0.01
    nums = sensor()
    nums.change_time_step(to=0.01, time_step=0.005)
    assert len(values(nums)) == 500


def test_waves_and_windows_match_r():
    nums = sdata.wave("square", frequency=5, time_step=0.01, how_many=10)
    assert values(nums) == pytest.approx([1] * 10)  # R: gsignal::square(2 * pi * 5 * t), t <- (0:9) * 0.01
    nums = sdata.wave("sawtooth", frequency=5, time_step=0.01, how_many=10)
    assert values(nums)[:4] == pytest.approx([-1, -0.9, -0.8, -0.7])  # R: gsignal::sawtooth(...)
    assert nums._time_step == 0.01
    assert values(sdata.window_shape("hann", how_many=5)) == pytest.approx([0, 0.5, 1, 0.5, 0])  # gsignal::hann(5)
    assert values(sdata.window_shape("hamming", how_many=5)) == pytest.approx([0.08, 0.54, 1, 0.54, 0.08])


def test_table_filter_and_peaks(capsys):
    import pandas as pd

    from simplydata.table import table as make_table

    for engine in ("pandas", "polars"):
        data = sdata.example("sensor")
        t = make_table(data) if engine == "pandas" else make_table(pytest.importorskip("polars").from_pandas(data))
        t.add_filtered_column("slow", from_column="signal", keep_below=10, sorted_by="time")
        # R: signal::filtfilt(signal::butter(4, 10 / 100), x)[500] (time steps of 0.005 s)
        assert np.asarray(t._frame["slow"].to_numpy(), dtype=float)[499] == pytest.approx(0.360961693964092, rel=1e-8)
        peaks = t.find_peaks("signal", sorted_by="time", at_least=1, apart=0.05)
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
    left = sdata.numbers(str(file))
    assert values(left).tolist() == [0, 1000, -2000, 32767, -32768] and left._time_step == 1 / 8000
    assert "8,000 readings per second" in capsys.readouterr().out
    assert values(sdata.numbers(str(file), channel=2)).tolist() == [5, 6, 7, 8, 9]
    with pytest.raises(SimplydataError, match="channel="):
        sdata.numbers(str(file), channel=3)


def test_wav_round_trip(tmp_path, capsys):
    nums = sdata.wave("sine", frequency=440, time_step=1 / 8000, how_many=800)
    nums.save(str(tmp_path / "tone.wav"))
    back = sdata.numbers(str(tmp_path / "tone.wav"))
    assert values(back) == pytest.approx(values(nums), abs=1e-7) and back._time_step == 1 / 8000
    nums.save(str(tmp_path / "tone16.wav"), bits=16)
    back = sdata.numbers(str(tmp_path / "tone16.wav"))
    assert values(back) / 32767 == pytest.approx(values(nums), abs=1e-4)
    with pytest.raises(SimplydataError, match="time_step="):
        sdata.numbers([0.1, 0.2]).save(str(tmp_path / "x.wav"))
