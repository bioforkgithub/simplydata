"""Tests for check_steady (R urca::ur.df or tseries::adf.test, and tseries::kpss.test, run through rpy2).

The series come from a small integer generator that gives the same numbers in Python and R:
    lcg <- function(n, seed = 12345) { u <- numeric(n); s <- seed
      for (j in 1:n) { s <- (69069 * s + 1) %% 2^32; u[j] <- s / 2^32 - 0.5 }; u }
    noise <- lcg(150); walk <- cumsum(noise)
Reference values from R 4.6.2, tseries 0.10.63, urca 1.3-4; the R call is next to each value. Around a
level the ADF test has a constant only (tseries::adf.test always allows a trend), so it is urca's:
    u <- urca::ur.df(x, type = "drift", lags = 5, selectlags = "Fixed")
    urca::punitroot(u@teststat[1], N = length(u@res), trend = "c", statistic = "t")
"""

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError


def lcg(n, seed=12345):
    out, s = [], seed
    for _ in range(n):
        s = (69069 * s + 1) % 2 ** 32
        out.append(s / 2 ** 32 - 0.5)
    return np.array(out)


NOISE = lcg(150)
WALK = np.cumsum(NOISE)


@pytest.fixture(params=["pandas", "polars"])
def engine(request):
    return request.param


def make(frame, engine):
    if engine == "polars":
        pytest.importorskip("polars")
        return sdata.table(frame, fast=True)
    return sdata.table(frame)


def rows(result):
    frame = result._frame
    return {r["test"]: r for r in (frame.to_pandas() if hasattr(frame, "to_pandas") else frame).to_dict("records")}


def test_the_generator_matches_r():
    assert NOISE[:3] == pytest.approx([-0.301475367043167, 0.397873695706949, -0.261711216531694], rel=1e-12)


def test_steady_noise_with_p_values_outside_the_tables(engine, capsys, needs_r):
    frame = pd.DataFrame({"time": np.arange(150), "level": NOISE})
    got = rows(make(frame, engine).check_steady_over_time("level", sorted_by="time"))
    out = capsys.readouterr().out
    adf, kpss = got["augmented Dickey-Fuller"], got["KPSS"]
    # urca::ur.df(noise, "drift", lags = 5): tau2 -5.18991318133887; punitroot(N = 144) 1.97423488320605e-05
    assert adf["statistic"] == pytest.approx(-5.18991318133887, rel=1e-10)
    assert adf["rows back"] == 5 and adf["p-value"] == pytest.approx(1.97423488320605e-05, rel=1e-8)
    assert adf["p-value is"] == "exact"
    # tseries::kpss.test(noise, null = "Level"): stat 0.087157636332688, lag 4, p 0.1 ("greater")
    assert kpss["statistic"] == pytest.approx(0.087157636332688, rel=1e-10)
    assert kpss["rows back"] == 4 and kpss["p-value"] == 0.1 and kpss["p-value is"] == "above"
    assert adf["reading"] == "steady"
    assert '"level" looks steady: it stays around a steady level (both tests agree: ADF p < 0.0001, KPSS p ' \
           "above 0.1)." in out
    assert 'urca::ur.df(x, type = "drift"' in out and 'tseries::kpss.test(x, null = "Level")' in out
    assert "Note from R" not in out  # the table-edge warnings become "below" / "above", not notes


def test_a_wandering_series(engine, capsys, needs_r):
    frame = pd.DataFrame({"time": np.arange(150), "level": WALK})
    t = make(frame, engine)
    got = rows(t.check_steady_over_time("level", sorted_by="time"))
    out = capsys.readouterr().out
    # urca::ur.df(walk, "drift", lags = 5): tau2 -2.11408908090633; punitroot(N = 144) 0.239533634696584
    assert got["augmented Dickey-Fuller"]["statistic"] == pytest.approx(-2.11408908090633, rel=1e-10)
    assert got["augmented Dickey-Fuller"]["p-value"] == pytest.approx(0.239533634696584, rel=1e-8)
    assert got["augmented Dickey-Fuller"]["p-value is"] == "exact"
    # tseries::kpss.test(walk, null = "Level"): stat 0.40588796556497, p 0.0746172562219957
    assert got["KPSS"]["statistic"] == pytest.approx(0.40588796556497, rel=1e-10)
    assert got["KPSS"]["p-value"] == pytest.approx(0.0746172562219957, rel=1e-10)
    assert got["KPSS"]["reading"] == "the tests disagree" and "The two tests disagree" in out
    # around a straight line: tseries::kpss.test(walk, null = "Trend"): stat 0.324899635996193, p 0.01 (smaller)
    line = rows(t.check_steady_over_time("level", sorted_by="time", around="straight line"))
    assert line["KPSS"]["statistic"] == pytest.approx(0.324899635996193, rel=1e-10)
    # with the trend in the ADF test too: tseries::adf.test(walk): stat -2.20574229670145, p 0.490677791882187
    assert line["augmented Dickey-Fuller"]["statistic"] == pytest.approx(-2.20574229670145, rel=1e-10)
    assert line["augmented Dickey-Fuller"]["p-value"] == pytest.approx(0.490677791882187, rel=1e-10)
    assert line["KPSS"]["p-value is"] == "below" and line["KPSS"]["reading"] == "wanders"
    assert "wanders: it does not stay around a steady straight line" in capsys.readouterr().out


def test_one_test_and_groups(engine, capsys, needs_r):
    frame = pd.DataFrame({"time": np.concatenate([np.arange(150)] * 2), "level": np.concatenate([NOISE, WALK]),
                          "site": ["A"] * 150 + ["B"] * 150})
    got = make(frame, engine).check_steady_over_time("level", sorted_by="time", test_method="kpss", for_each_group_in="site")
    data = got._frame.to_pandas() if hasattr(got._frame, "to_pandas") else got._frame
    assert data["site"].tolist() == ["A", "B"] and set(data["test"]) == {"KPSS"}
    assert data["statistic"].tolist() == pytest.approx([0.087157636332688, 0.40588796556497], rel=1e-10)
    out = capsys.readouterr().out
    assert '"level" for A could well be steady' in out and "augmented" not in out.split("Method:")[1]


def test_steady_errors(engine):
    t = make(pd.DataFrame({"time": [0, 1, 2, 4.0] * 3, "level": np.arange(12.0)}), engine)
    with pytest.raises(SimplydataError, match="around"):
        t.check_steady_over_time("level", around="flat")
    with pytest.raises(SimplydataError, match="method"):
        t.check_steady_over_time("level", test_method="phillips-perron")
    with pytest.raises(SimplydataError, match="same"):
        t.check_steady_over_time("level", sorted_by="time")
    short = make(pd.DataFrame({"level": [1.0, 2, 3]}), engine)
    with pytest.raises(SimplydataError, match="at least 10"):
        short.check_steady_over_time("level")


# ---------------------------------------------------------------------------- autocorrelation_of
# k <- 0:95; x <- sin(2 * pi * k / 12) + 0.02 * k + lcg(96)
K96 = np.arange(96)
SEASONAL = np.sin(2 * np.pi * K96 / 12) + 0.02 * K96 + lcg(96)


def acf_rows(result):
    frame = result._frame
    return frame.to_pandas() if hasattr(frame, "to_pandas") else frame


def test_autocorrelation_matches_r_acf(engine, capsys):
    frame = pd.DataFrame({"month": K96, "x": SEASONAL})
    got = acf_rows(make(frame, engine).find_autocorrelation_of("x", sorted_by="month"))
    out = capsys.readouterr().out
    # a <- acf(x): lag.max = floor(10 * log10(96)) = 19
    assert len(got) == 19 and got["rows back"].tolist() == list(range(1, 20))
    assert got["correlation"][:3].tolist() == pytest.approx([0.802483779911213, 0.593424437316948,
                                                             0.276559102571370], rel=1e-10)
    assert got["correlation"][11] == pytest.approx(0.707571939651603, rel=1e-10)  # a$acf[13], 12 rows back
    assert got["correlation"][18] == pytest.approx(-0.302428792808212, rel=1e-10)  # a$acf[20]
    assert got["band high"][0] == pytest.approx(0.200037986514805, rel=1e-10)  # qnorm(0.975) / sqrt(96)
    # Box.test(x, lag = 19, type = "Ljung-Box"): 362.92338071157
    assert got["Ljung-Box statistic"][0] == pytest.approx(362.92338071157, rel=1e-10)
    assert '"x" is most like itself 1 row back' in out and "Ljung-Box test up to 19 rows back" in out
    assert "acf(x, lag.max = 19)" in out


def test_autocorrelation_partial_covariance_and_bartlett():
    nums = sdata.numbers(SEASONAL.tolist())
    partial = acf_rows(nums.find_autocorrelation(rows_back=24, show="partial"))
    # pa <- pacf(x, lag.max = 24)
    assert partial["partial correlation"][:3].tolist() == pytest.approx(
        [0.802483779911213, -0.142002726029874, -0.439521824753959], rel=1e-9)
    assert partial["partial correlation"][11] == pytest.approx(-0.0349121262778547, rel=1e-8)
    assert partial["partial correlation"][23] == pytest.approx(0.00938365469116159, rel=1e-7)
    # Box.test(x, lag = 24, type = "Ljung-Box"): 438.003452315306
    assert partial["Ljung-Box statistic"][0] == pytest.approx(438.003452315306, rel=1e-10)
    covariance = acf_rows(nums.find_autocorrelation(rows_back=24, show="covariance"))
    # acf(x, lag.max = 24, type = "covariance")$acf[2:3]
    assert covariance["covariance"][:2].tolist() == pytest.approx([0.648981989297812, 0.479912219372830], rel=1e-10)
    bartlett = acf_rows(nums.find_autocorrelation(rows_back=24, band="bartlett"))
    # qnorm(0.975) * sqrt(cumsum(c(1, 2 * r[-24]^2)) / 96), as R plot.acf(ci.type = "ma")
    assert bartlett["band high"][:3].tolist() == pytest.approx([0.200037986514805, 0.302577569096385,
                                                                0.346029034908633], rel=1e-9)
    assert bartlett["band high"][11] == pytest.approx(0.445197225397543, rel=1e-9)


def test_autocorrelation_finds_a_repeating_pattern(capsys):
    k = np.arange(120)
    sdata.numbers((np.sin(2 * np.pi * k / 12) + 0.1 * lcg(120)).tolist()).find_autocorrelation(rows_back=24)
    assert "a pattern that repeats about every 12 rows" in capsys.readouterr().out


def test_autocorrelation_errors(engine):
    t = make(pd.DataFrame({"x": SEASONAL}), engine)
    with pytest.raises(SimplydataError, match="rows_back="):
        t.find_autocorrelation_of("x", rows_back=0)
    with pytest.raises(SimplydataError, match="show"):
        t.find_autocorrelation_of("x", show="spectrum")
    with pytest.raises(SimplydataError, match="bartlett"):
        t.find_autocorrelation_of("x", show="partial", band="bartlett")
    with pytest.raises(SimplydataError, match="empty"):
        make(pd.DataFrame({"x": [1.0, None, 3, 4, 5, 6]}), engine).find_autocorrelation_of("x")


def test_partial_autocorrelation_of_few_readings_by_default(capsys):
    x = np.sin(np.arange(25.0)) + np.arange(25) * 0.01
    got = acf_rows(sdata.numbers(list(x)).find_autocorrelation(show="partial"))
    # R: pacf(x, lag.max = 11)$acf[1:3] (statsmodels needs fewer rows back than half the readings, so 11)
    assert len(got) == 11
    assert got["partial correlation"].to_numpy()[:3] == pytest.approx(
        [0.531820840817996, -0.915925292375954, -0.101062055524772], rel=1e-10)
    assert "lag.max = 11" in capsys.readouterr().out


def test_time_words_with_r_on_sixty_readings(needs_r, capsys):
    # the reviewer's run of the R-backed words on a plain numbered series: each gives its answer
    frame = pd.DataFrame({"t": np.arange(60.0), "x": np.sin(np.arange(60.0)) + np.arange(60) * 0.01})
    t = sdata.table(frame)
    t.check_steady_over_time("x", sorted_by="t")
    t.add_smoothed_column("m", from_column="x", test_method="median", sorted_by="t")
    t.forecast("x", sorted_by="t", steps_ahead=3)
    t.find_change_points_in("x", sorted_by="t")
    sdata.numbers(list(frame.x)).find_spectrum(test_method="lomb", time_points=list(frame.t))
    assert "Method" in capsys.readouterr().out
