"""Regression tests for the fixes from the method reviews and the reference-data notebooks (simplydata_tests
FINDINGS.md A1-A3): fit_curve's standard errors on NIST Filip, fit_formula's flat-region stop on NIST BoxBOD and
arctan for NIST Roszman1, the exact-ties R check of compare_survival(followed_from=), the same question for both
tests of check_steady_over_time, the independence check of find_trend_of, the group-size check of
add_axes_that_separate_groups, and the colour notes.

The series come from the integer generator of tests/test_time_series.py, which gives the same numbers on every
computer (no random numbers, so nothing depends on the platform).
"""

import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError

NIST = Path(__file__).resolve().parents[1] / "validation" / "data" / "nist"


def lcg(n, seed=12345):
    out, s = [], seed
    for _ in range(n):
        s = (69069 * s + 1) % 2 ** 32
        out.append(s / 2 ** 32 - 0.5)
    return np.array(out)


def read_nist(name):
    """(data with columns y and x, the header text) of a NIST StRD file."""
    import re

    lines = (NIST / name).read_text(encoding="ascii").splitlines()
    first, last = map(int, re.search(r"Data\s*[:(]\s*lines\s+(\d+)\s+to\s+(\d+)", "\n".join(lines)).groups())
    data = np.array([[float(v) for v in line.split()] for line in lines[first - 1:last]])
    return pd.DataFrame({"y": data[:, 0], "x": data[:, 1]}), "\n".join(lines[:first - 1])


def lre(got, want):
    return -math.log10(abs(got - want) / abs(want)) if got != want else 15.0


def frame_of(result):
    native = result._frame.to_native()
    return native.to_pandas() if hasattr(native, "to_pandas") else native


# ---------------------------------------------------------------- 8 / A1: fit_curve on NIST Filip
def test_fit_curve_gives_filip_standard_errors_to_nine_digits(capsys):
    import re

    data, header = read_nist("Filip.dat")
    certified = [(float(b), float(sd)) for b, sd in re.findall(r"^\s*B\d+\s+(\S+)\s+(\S+)\s*$", header, flags=re.M)]
    got = frame_of(sdata.table(data).fit_curve(x="x", y="y", of_degree=10))
    assert len(certified) == 11 == len(got)
    # simplydata 0.2.0 (a QR fit on the raw powers) gave no standard error for x**5 to x**10 and 45.7 for the
    # intercept (NIST 298.08); on the mapped powers every estimate and standard error agrees to 13 digits
    for (b, sd), estimate, error in zip(certified, got["estimate"], got["standard error"]):
        assert lre(estimate, b) >= 9 and lre(error, sd) >= 9
    assert got["R squared"][0] == pytest.approx(0.996727416185620, rel=1e-12)


def test_fit_curve_still_matches_an_easy_polynomial():
    # R: lm(y ~ poly(x, 2, raw = TRUE)) with x = 1..8, y below: 0.4464286 + 1.2797619 x - 0.0297619 x^2
    x = np.arange(1.0, 9.0)
    y = np.array([1.7, 3.0, 3.9, 5.0, 6.1, 6.9, 7.8, 8.5])
    from simplydata.table.fitting import fit_curve_core
    from statsmodels.regression.linear_model import OLS

    fit = fit_curve_core(x, y, 2)
    plain = OLS(y, np.vander(x, 3, increasing=True)).fit()
    assert fit["beta"] == pytest.approx(plain.params, rel=1e-10)
    assert fit["se"] == pytest.approx(plain.bse, rel=1e-10)
    assert fit["p"] == pytest.approx(plain.pvalues, rel=1e-8)


# ---------------------------------------------------------------- 6 / A2: fit_formula on NIST BoxBOD, start 1
def test_a_fit_stopped_in_a_flat_region_does_not_say_converged(capsys):
    data, _ = read_nist("BoxBOD.dat")
    got = frame_of(sdata.table(data).fit_formula("y = b1 * (1 - exp(-b2 * x))", start={"b1": 1, "b2": 1})).iloc[0]
    out = capsys.readouterr().out
    assert got["converged"] == "no" and got["R squared"] < 0.01
    assert "the search may have stopped in a flat region" in out and 'search="whole range"' in out
    assert "the data do not pin down" not in out
    # from NIST's start 2 the fit reaches the certified values and says converged
    good = frame_of(sdata.table(data).fit_formula("y = b1 * (1 - exp(-b2 * x))",
                                                  start={"b1": 100, "b2": 0.75})).iloc[0]
    assert good["converged"] == "yes" and lre(good["b1"], 2.1380940889e02) >= 6
    assert "flat region" not in capsys.readouterr().out


def test_a_fit_no_better_than_a_flat_line_gets_a_hint(capsys):
    x = np.arange(1.0, 21.0)
    # the pattern 1, -1, -1, 1 has no slope at all, and the small noise keeps R squared just above 0
    frame = pd.DataFrame({"x": x, "y": np.tile([1.0, -1.0, -1.0, 1.0], 5) + 0.01 * lcg(20)})
    got = frame_of(sdata.table(frame).fit_formula("y = a + b * x")).iloc[0]
    assert got["converged"] == "yes"  # the fit itself is fine: the formula just explains nothing
    assert "no better than a flat line" in capsys.readouterr().out


# ---------------------------------------------------------------- 7 / A3: arctan for NIST Roszman1
def test_arctan_lets_roszman1_be_written(capsys):
    data, _ = read_nist("Roszman1.dat")
    got = frame_of(sdata.table(data).fit_formula("y = b1 - b2 * x - arctan(b3 / (x - b4)) / pi",
                                                 start={"b1": 0.1, "b2": -0.00001, "b3": 1000, "b4": -100})).iloc[0]
    certified = {"b1": 2.0196866396e-01, "b2": -6.1953516256e-06, "b3": 1.2044556708e03, "b4": -1.8134269537e02}
    for name, value in certified.items():
        assert lre(got[name], value) >= 6, name


def test_inverse_trigonometric_functions_and_r_names():
    x = np.linspace(-0.9, 0.9, 12)
    frame = pd.DataFrame({"x": x, "y1": 2 * np.arcsin(x), "y2": 3 * np.arccos(x), "y3": np.arctan2(x, 2.0)})
    t = sdata.table(frame)
    assert frame_of(t.fit_formula("y1 = a * asin(x)"))["a"][0] == pytest.approx(2, rel=1e-8)
    assert frame_of(t.fit_formula("y2 = a * arccos(x)"))["a"][0] == pytest.approx(3, rel=1e-8)
    assert frame_of(t.fit_formula("y3 = arctan2(x, a)", start={"a": 1.5}))["a"][0] == pytest.approx(2, rel=1e-6)
    with pytest.raises(SimplydataError, match="arctan2\\(\\) was given 1 thing"):
        t.fit_formula("y3 = arctan2(a * x)")


# ---------------------------------------------------------------- 2: check_steady_over_time asks one question
def test_a_series_steady_around_a_sloping_line_no_longer_shows_as_disagree(capsys, needs_r):
    # x = 0.01 * (1:150) + lcg(150): steady around a rising line. Before, around="level" paired
    # tseries::adf.test (which allows a trend: p 0.01, "steady") with kpss.test(null = "Level") (p 0.01,
    # "wanders"), and the two "disagreed". Now the ADF test of a level has a constant only:
    # urca::ur.df(x, type = "drift", lags = 5) tau2 -1.5140154983721, punitroot(N = 144) 0.523830568917384
    frame = pd.DataFrame({"time": np.arange(150), "x": 0.01 * np.arange(1, 151) + lcg(150)})
    t = sdata.table(frame)
    level = {r["test"]: r for r in frame_of(t.check_steady_over_time("x", sorted_by="time")).to_dict("records")}
    out = capsys.readouterr().out
    adf = level["augmented Dickey-Fuller"]
    assert adf["statistic"] == pytest.approx(-1.5140154983721, rel=1e-10)
    assert adf["p-value"] == pytest.approx(0.523830568917384, rel=1e-8) and adf["p-value is"] == "exact"
    assert adf["reading"] == "wanders" and adf["question"] == "steady around one level?"
    assert "Question: does it stay steady around one level? Both tests ask it." in out
    assert 'urca::ur.df(x, type = "drift"' in out and "tseries::adf.test" not in out
    # around a straight line both tests allow the slope, and agree it is steady
    line = {r["test"]: r for r in frame_of(t.check_steady_over_time("x", sorted_by="time", around="straight line"))
            .to_dict("records")}
    assert line["KPSS"]["reading"] == "steady" and line["KPSS"]["question"] == "steady around a straight line?"
    assert "tseries::adf.test(x)" in capsys.readouterr().out


def test_a_short_series_says_the_adf_p_value_is_rough(capsys, needs_r):
    # 12 readings: 12 - 2 lags - 1 = 9 rows in the test regression; urca::punitroot() prints that N may be too small
    frame = pd.DataFrame({"time": np.arange(12), "x": lcg(12)})
    sdata.table(frame).check_steady_over_time("x", sorted_by="time")
    assert "has only 9 rows in its test regression" in capsys.readouterr().out


# ---------------------------------------------------------------- 3: find_trend_of checks independence
def test_find_trend_of_notes_correlated_readings(capsys):
    noise = lcg(80)
    correlated = np.zeros(80)
    for i in range(80):  # AR(1) with 0.8, built from the generator: the same numbers everywhere
        correlated[i] = (0.8 * correlated[i - 1] if i else 0.0) + noise[i]
    frame = pd.DataFrame({"t": np.arange(80), "plain": 0.01 * np.arange(80) + noise,
                          "sticky": 0.01 * np.arange(80) + correlated})
    t = sdata.table(frame)
    got = frame_of(t.find_trend_of("sticky", sorted_by="t")).iloc[0]
    out = capsys.readouterr().out
    assert got["lag-1 autocorrelation"] > 0.5 and got["Ljung-Box p-value (lag 1)"] < 0.05
    assert "are correlated with the one before" in out and "modified Mann-Kendall" in out
    assert "Both assume independent readings" in out
    plain = frame_of(t.find_trend_of("plain", sorted_by="t")).iloc[0]
    assert plain["Ljung-Box p-value (lag 1)"] > 0.05
    assert "correlated with the one before" not in capsys.readouterr().out


def test_negative_autocorrelation_gets_no_note(capsys):
    # readings that swing up and down around the line: the Mann-Kendall p-value is then too big, not too small
    frame = pd.DataFrame({"t": np.arange(60), "y": 0.05 * np.arange(60) + np.tile([1.0, -1.0], 30) + 0.1 * lcg(60)})
    got = frame_of(sdata.table(frame).find_trend_of("y", sorted_by="t")).iloc[0]
    assert got["lag-1 autocorrelation"] < -0.5 and got["Ljung-Box p-value (lag 1)"] < 0.05
    assert "correlated with the one before" not in capsys.readouterr().out


def test_the_lag1_check_matches_statsmodels():
    from scipy import stats
    from statsmodels.stats.diagnostic import acorr_ljungbox
    from statsmodels.tsa.stattools import acf

    from simplydata._trend_season import lag1_after_sen_line

    y = 0.02 * np.arange(40) + lcg(40)
    fit = stats.theilslopes(y, np.arange(40.0))
    rest = y - (fit.intercept + fit.slope * np.arange(40.0))
    got = lag1_after_sen_line(y)
    assert got["r"] == pytest.approx(acf(rest, nlags=1, fft=False)[1], rel=1e-12)
    assert got["p"] == pytest.approx(float(acorr_ljungbox(rest, lags=[1])["lb_pvalue"].iloc[0]), rel=1e-12)


# ---------------------------------------------------------------- 4: discriminant axes and small groups
def test_too_few_rows_for_the_pooled_spread_are_refused():
    # 7 rows - 3 groups = 4, not more than 4 columns: MASS::lda cannot work out the pooled covariance
    frame = pd.DataFrame({c: lcg(7, seed) for c, seed in zip("abcd", (1, 7, 99, 5))})
    frame["kind"] = ["x", "x", "x", "y", "y", "z", "z"]
    with pytest.raises(SimplydataError, match=r"7 rows - 3 groups = 4, with 4 columns"):
        sdata.table(frame).add_axes_that_separate_groups(columns=list("abcd"), for_each_group_in="kind")


def test_a_group_with_no_more_rows_than_columns_gets_a_note(capsys, needs_r):
    frame = pd.DataFrame({"a": lcg(13), "b": lcg(13, 7), "c": lcg(13, 99),
                          "kind": ["x"] * 5 + ["y"] * 5 + ["z"] * 3})
    frame.loc[frame["kind"] == "y", "a"] += 1
    sdata.table(frame).add_axes_that_separate_groups(columns=["a", "b", "c"], for_each_group_in="kind")
    assert '"z" (3 rows) in "kind" has no more rows than there are columns (3)' in capsys.readouterr().out


# ---------------------------------------------------------------- 5: colour notes
def test_more_groups_than_colours_get_a_note(capsys):
    frame = pd.DataFrame({"x": np.arange(20.0), "y": lcg(20), "g": [f"g{i % 10}" for i in range(20)]})
    chart = sdata.chart(frame)
    chart.draw_dots(x="x", y="y", colour="g")
    chart._render()
    out = capsys.readouterr().out
    assert "there are 10 groups but 8 different colours" in out
    few = sdata.chart(frame.iloc[:8].assign(g=[f"g{i}" for i in range(8)]))
    few.draw_dots(x="x", y="y", colour="g")
    few._render()
    assert "different colours" not in capsys.readouterr().out


def test_a_rainbow_scale_gets_a_note(capsys):
    from simplydata.words._colour_scale import resolve_map

    resolve_map(("turbo",))
    assert '"turbo" is a rainbow scale' in capsys.readouterr().out
    resolve_map(("viridis",))
    resolve_map(("magma",))
    assert "rainbow" not in capsys.readouterr().out
