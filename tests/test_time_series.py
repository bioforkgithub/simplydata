"""Tests for check_steady (R tseries::adf.test and kpss.test, run through rpy2).

The series come from a small integer generator that gives the same numbers in Python and R:
    lcg <- function(n, seed = 12345) { u <- numeric(n); s <- seed
      for (j in 1:n) { s <- (69069 * s + 1) %% 2^32; u[j] <- s / 2^32 - 0.5 }; u }
    noise <- lcg(150); walk <- cumsum(noise)
Reference values from R 4.6.2, tseries 0.10.63; the R call is next to each value.
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
    got = rows(make(frame, engine).check_steady("level", sorted_by="time"))
    out = capsys.readouterr().out
    adf, kpss = got["augmented Dickey-Fuller"], got["KPSS"]
    # tseries::adf.test(noise): stat -5.19599343506283, lag 5, p 0.01 ("p-value smaller than printed")
    assert adf["statistic"] == pytest.approx(-5.19599343506283, rel=1e-10)
    assert adf["rows back"] == 5 and adf["p-value"] == 0.01 and adf["p-value is"] == "below"
    # tseries::kpss.test(noise, null = "Level"): stat 0.087157636332688, lag 4, p 0.1 ("greater")
    assert kpss["statistic"] == pytest.approx(0.087157636332688, rel=1e-10)
    assert kpss["rows back"] == 4 and kpss["p-value"] == 0.1 and kpss["p-value is"] == "above"
    assert adf["reading"] == "steady"
    assert '"level" looks steady: it stays around a steady level (both tests agree: ADF p below 0.01, KPSS p ' \
           "above 0.1)." in out
    assert "tseries::adf.test(x)" in out and 'tseries::kpss.test(x, null = "Level")' in out
    assert "Note from R" not in out  # the table-edge warnings become "below" / "above", not notes


def test_a_wandering_series(engine, capsys, needs_r):
    frame = pd.DataFrame({"time": np.arange(150), "level": WALK})
    t = make(frame, engine)
    got = rows(t.check_steady("level", sorted_by="time"))
    out = capsys.readouterr().out
    # tseries::adf.test(walk): stat -2.20574229670145, lag 5, p 0.490677791882187
    assert got["augmented Dickey-Fuller"]["statistic"] == pytest.approx(-2.20574229670145, rel=1e-10)
    assert got["augmented Dickey-Fuller"]["p-value"] == pytest.approx(0.490677791882187, rel=1e-10)
    assert got["augmented Dickey-Fuller"]["p-value is"] == "exact"
    # tseries::kpss.test(walk, null = "Level"): stat 0.40588796556497, p 0.0746172562219957
    assert got["KPSS"]["statistic"] == pytest.approx(0.40588796556497, rel=1e-10)
    assert got["KPSS"]["p-value"] == pytest.approx(0.0746172562219957, rel=1e-10)
    assert got["KPSS"]["reading"] == "the tests disagree" and "The two tests disagree" in out
    # around a straight line: tseries::kpss.test(walk, null = "Trend"): stat 0.324899635996193, p 0.01 (smaller)
    line = rows(t.check_steady("level", sorted_by="time", around="straight line"))
    assert line["KPSS"]["statistic"] == pytest.approx(0.324899635996193, rel=1e-10)
    assert line["KPSS"]["p-value is"] == "below" and line["KPSS"]["reading"] == "wanders"
    assert "wanders: it does not stay around a steady straight line" in capsys.readouterr().out


def test_one_test_and_groups(engine, capsys, needs_r):
    frame = pd.DataFrame({"time": np.concatenate([np.arange(150)] * 2), "level": np.concatenate([NOISE, WALK]),
                          "site": ["A"] * 150 + ["B"] * 150})
    got = make(frame, engine).check_steady("level", sorted_by="time", method="kpss", for_each="site")
    data = got._frame.to_pandas() if hasattr(got._frame, "to_pandas") else got._frame
    assert data["site"].tolist() == ["A", "B"] and set(data["test"]) == {"KPSS"}
    assert data["statistic"].tolist() == pytest.approx([0.087157636332688, 0.40588796556497], rel=1e-10)
    out = capsys.readouterr().out
    assert '"level" for A could well be steady' in out and "augmented" not in out.split("Method:")[1]


def test_steady_errors(engine):
    t = make(pd.DataFrame({"time": [0, 1, 2, 4.0] * 3, "level": np.arange(12.0)}), engine)
    with pytest.raises(SimplydataError, match="around"):
        t.check_steady("level", around="flat")
    with pytest.raises(SimplydataError, match="method"):
        t.check_steady("level", method="phillips-perron")
    with pytest.raises(SimplydataError, match="same"):
        t.check_steady("level", sorted_by="time")
    short = make(pd.DataFrame({"level": [1.0, 2, 3]}), engine)
    with pytest.raises(SimplydataError, match="at least 10"):
        short.check_steady("level")
