"""Tests for spectra: nums.spectrum and table.find_spectrum_of.

Reference values from R 4.6.2 (stats spec.pgram; lomb 2.5.0); the R call is written next to each
value. The test signal is made by a formula, so R builds the very same numbers:
    i <- 0:199; t <- i * 0.01
    x <- sin(2 * pi * 5 * t) + 0.5 * sin(2 * pi * 20 * t) + ((i * 37) %% 11 - 5) / 10
"""

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError

ENGINES = ["pandas", "polars"]
I = np.arange(200)
T = I * 0.01
X = np.sin(2 * np.pi * 5 * T) + 0.5 * np.sin(2 * np.pi * 20 * T) + ((I * 37) % 11 - 5) / 10
# uneven times for Lomb-Scargle:  k <- 0:79; tt <- k * 0.1 + 0.03 * sin(k)
K = np.arange(80)
TT = K * 0.1 + 0.03 * np.sin(K)
YY = np.sin(2 * np.pi * 1.2 * TT) + ((K * 13) % 7 - 3) / 10


@pytest.fixture(params=ENGINES)
def engine(request):
    return request.param


def make(frame, engine):
    if engine == "polars":
        pytest.importorskip("polars")
        return sdata.table(frame, fast=True)
    return sdata.table(frame)


def column(result, name):
    return np.asarray(result._frame[name].to_list(), dtype=float)


# ---------------------------------------------------------------------------- periodogram
def test_periodogram_matches_r_spec_pgram(capsys):
    # s <- spec.pgram(ts(x, frequency = 100), taper = 0, detrend = FALSE, demean = TRUE, fast = FALSE)
    got = sdata.numbers(X.tolist()).find_spectrum(time_step=0.01)
    freq, power = column(got, "frequency"), column(got, "power")
    assert len(freq) == 101 and freq[0] == 0 and freq[-1] == pytest.approx(50)
    assert freq[10] == pytest.approx(5) and freq[40] == pytest.approx(20)
    # SciPy's one-sided density = 2 x R's spec, except at the top frequency (not doubled)
    assert power[10] == pytest.approx(2 * 0.500929552566148, rel=1e-10)  # s$spec[10], freq 5
    assert power[40] == pytest.approx(2 * 0.123148803830861, rel=1e-10)  # s$spec[40], freq 20
    assert power[1] == pytest.approx(2 * 1.80490176620546e-05, rel=1e-8)  # s$spec[1], freq 0.5
    assert power[100] == pytest.approx(7.99999999999943e-06, rel=1e-8)  # s$spec[100], Nyquist
    # the powers times the frequency step add up to the variance (n divisor): mean((x - mean(x))^2)
    assert power.sum() * 0.5 == pytest.approx(0.724335941758618, rel=1e-10)
    assert column(got, "share of variance (%)").sum() == pytest.approx(100, rel=1e-10)
    assert column(got, "repeats every")[10] == pytest.approx(0.2)
    out = capsys.readouterr().out
    assert "The strongest cycle in the numbers has frequency 5 per unit of time (it repeats every 0.2 units of " \
           "time) and holds 69 % of the variance; next: 20 per unit of time (17 %)" in out
    assert "spec.pgram(x, taper = 0, detrend = FALSE, fast = FALSE)" in out and "100 readings per unit" in out


def test_spectrum_other_spellings_and_shows():
    nums = sdata.numbers(X.tolist())
    base = column(nums.find_spectrum(time_step=0.01), "power")
    assert np.allclose(column(nums.find_spectrum(sampling_rate=100), "power"), base)
    assert np.allclose(column(nums.find_spectrum(fs=100), "power"), base)
    decibels = column(nums.find_spectrum(time_step=0.01, show="decibels"), "power (decibels)")
    assert decibels[10] == pytest.approx(10 * np.log10(2 * 0.500929552566148), rel=1e-10)
    # amplitude: the size of the 5-per-second sine is 1, of the 20-per-second sine 0.5
    amplitude = column(nums.find_spectrum(time_step=0.01, show="amplitude"), "amplitude")
    assert amplitude[10] == pytest.approx(1.0, abs=0.05) and amplitude[40] == pytest.approx(0.5, abs=0.05)
    between = nums.find_spectrum(time_step=0.01, between=[4, 6])
    assert column(between, "frequency").tolist() == [4.0, 4.5, 5.0, 5.5, 6.0]
    plain = nums.find_spectrum()  # no time step: cycles per reading
    assert column(plain, "frequency")[10] == pytest.approx(0.05)


# ---------------------------------------------------------------------------- welch
def test_welch_matches_scipys_formula_written_in_r(capsys):
    # welch_r <- function(x, fs, m) { w <- 0.5 - 0.5 * cos(2 * pi * (0:(m - 1)) / m); pieces from
    #   seq(1, n - m + 1, by = m / 2), each mean removed, x w, Mod(fft)^2 / (fs * sum(w^2)), averaged,
    #   all but the first and last doubled };  W <- welch_r(x, 100, 64)
    got = sdata.numbers(X.tolist()).find_spectrum(time_step=0.01, method="welch", window=64)
    power = column(got, "power")
    assert len(power) == 33
    assert power[3] == pytest.approx(0.202465540197663, rel=1e-10)  # W[4], freq 4.6875
    assert power[13] == pytest.approx(0.0511069606711551, rel=1e-10)  # W[14], freq 20.3125
    assert power[0] == pytest.approx(0.000998553605597233, rel=1e-8)  # W[1]
    assert power[32] == pytest.approx(7.44664965653067e-08, rel=1e-6)  # W[33]
    assert "Welch's method" in capsys.readouterr().out


# ---------------------------------------------------------------------------- lomb-scargle (R)
def test_lomb_scargle_is_r_lsp(capsys, needs_r):
    # l <- lomb::lsp(yy, times = tt, type = "frequency", normalize = "standard", ofac = 1)
    got = sdata.numbers(YY.tolist()).find_spectrum(method="lomb-scargle", time_points=TT.tolist())
    freq, power = column(got, "frequency"), column(got, "power")
    assert len(freq) == 40
    assert freq[:3] == pytest.approx([0.126796120620927, 0.253592241241854, 0.380388361862780], rel=1e-12)
    assert power[:3] == pytest.approx([0.00504460550147034, 0.00509043462287422, 0.03133789435001058], rel=1e-10)
    assert freq[np.argmax(power)] == pytest.approx(1.14116508558834, rel=1e-12)  # l$peak.at
    assert power.max() == pytest.approx(0.453399963047636, rel=1e-10)  # l$peak
    assert "share of variance (%)" not in got.get_column_names()
    assert "lomb::lsp" in capsys.readouterr().out


# ---------------------------------------------------------------------------- table.find_spectrum_of
def test_spectrum_of_table_matches_numbers(engine, capsys):
    frame = pd.DataFrame({"time": T, "level": X})
    got = make(frame, engine).find_spectrum_of("level", sorted_by="time")
    out = capsys.readouterr().out
    assert column(got, "power")[10] == pytest.approx(2 * 0.500929552566148, rel=1e-10)
    assert 'The strongest cycle in "level" has frequency 5 per unit of "time" (it repeats every 0.2 units of ' \
           '"time")' in out
    assert 'one reading every 0.01 in "time" (200 readings)' in out


def test_spectrum_of_sorts_and_groups(engine, capsys):
    shuffled = np.random.default_rng(1).permutation(200)
    frame = pd.DataFrame({"time": np.concatenate([T, T]), "level": np.concatenate([X, 2 * X]),
                          "station": ["A"] * 200 + ["B"] * 200}).iloc[np.concatenate([shuffled, shuffled + 200])]
    got = make(frame, engine).find_spectrum_of("level", sorted_by="time", for_each_group_in="station")
    rows = got._frame.to_pandas() if hasattr(got._frame, "to_pandas") else got._frame
    a = rows[rows["station"] == "A"]["power"].to_numpy(float)
    b = rows[rows["station"] == "B"]["power"].to_numpy(float)
    assert a[10] == pytest.approx(2 * 0.500929552566148, rel=1e-10) and b[10] == pytest.approx(4 * a[10], rel=1e-10)
    assert 'for A has frequency 5' in capsys.readouterr().out


def test_spectrum_of_monthly_dates(engine, capsys):
    months = pd.date_range("2010-01-01", periods=48, freq="MS")
    level = np.sin(2 * np.pi * np.arange(48) / 12)
    got = make(pd.DataFrame({"month": months, "level": level}), engine).find_spectrum_of("level", sorted_by="month")
    out = capsys.readouterr().out
    assert "frequency 0.0833 per month (it repeats every 12 months)" in out
    assert column(got, "repeats every")[4] == pytest.approx(12)


def test_spectrum_of_lomb_scargle_on_uneven_times(engine, needs_r):
    frame = pd.DataFrame({"t": TT, "y": YY})
    got = make(frame, engine).find_spectrum_of("y", sorted_by="t", method="lomb-scargle")
    assert column(got, "power").max() == pytest.approx(0.453399963047636, rel=1e-10)


def test_spectrum_errors(engine):
    frame = pd.DataFrame({"time": [0, 1, 2, 4, 5, 6.0], "level": [1, 2, 1, 2, 1, 2.0]})
    t = make(frame, engine)
    with pytest.raises(SimplydataError, match="evenly spaced"):
        t.find_spectrum_of("level", sorted_by="time")
    gaps = make(pd.DataFrame({"time": [0, 1, 2, 3, 4.0], "level": [1, None, 1, 2, 1]}), engine)
    with pytest.raises(SimplydataError, match="empty cell"):
        gaps.find_spectrum_of("level", sorted_by="time")
    with pytest.raises(SimplydataError, match="method"):
        t.find_spectrum_of("level", method="fourier")
    with pytest.raises(SimplydataError, match="between="):
        sdata.numbers(X.tolist()).find_spectrum(between=[5])
    with pytest.raises(SimplydataError, match="only one of"):
        sdata.numbers(X.tolist()).find_spectrum(time_step=0.01, fs=100)
    with pytest.raises(SimplydataError, match="welch"):
        sdata.numbers(X.tolist()).find_spectrum(window=64)
