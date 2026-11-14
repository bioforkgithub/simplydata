"""S1: effect sizes and their 95 % intervals come from R effectsize (or a Python package that gives
the same number), never from a formula in simplydata.

Reference values: R 4.6.2, effectsize 1.0.3, on sdata.example("marks") (m <- read.csv(".../marks.csv");
a, b = the marks of classes A and B; w = one row per child, a column per subject) and the counts
written next to each value. Every interval is two-sided (alternative = "two.sided").
"""

import math

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata.table import table as make_table

REL = 1e-9


@pytest.fixture(params=["pandas", "polars"])
def engine(request):
    return request.param


def make(data, engine):
    if engine == "polars":
        pl = pytest.importorskip("polars")
        return make_table(pl.from_pandas(data))
    return make_table(data)


def row(result):
    return result._frame.to_pandas().iloc[0].to_dict()


def check(got, value, low, high, rel=REL):
    assert got["effect size"] == pytest.approx(value, rel=rel)
    assert got["effect size 95 % CI low"] == pytest.approx(low, rel=rel, abs=1e-12)
    assert got["effect size 95 % CI high"] == pytest.approx(high, rel=rel)


@pytest.fixture
def marks():
    return sdata.example("marks")


def wide(marks):
    return marks.pivot(index="name", columns="subject", values="marks").reset_index()


def test_hedges_g(marks, engine, capsys, needs_r):
    ab = marks[marks["class"].isin(["A", "B"])].reset_index(drop=True)
    got = row(make(ab, engine).compare_averages("marks", for_each="class"))
    # R: hedges_g(a, b)
    check(got, 0.51610559576354, -0.137916399718482, 1.162824300438)
    assert "Hedges' g = 0.516 (95 % CI -0.138 to 1.16)" in capsys.readouterr().out


def test_omega_squared(marks, engine, capsys, needs_r):
    got = row(make(marks, engine).compare_averages("marks", for_each="class"))
    # R: omega_squared(aov(marks ~ class, data = m), partial = FALSE, alternative = "two.sided")
    check(got, 0.0966893251462588, 0.0, 0.25505950656041)
    assert "Omega-squared = 0.0967 (95 % CI 0 to 0.255)" in capsys.readouterr().out


def test_rank_biserial_two_groups(marks, engine, needs_r):
    ab = marks[marks["class"].isin(["A", "B"])].reset_index(drop=True)
    got = row(make(ab, engine).compare_averages("marks", for_each="class", based_on="ranks"))
    # R: rank_biserial(a, b)
    check(got, 0.317901234567901, -0.053037711867011, 0.611747283108239)


def test_rank_epsilon_squared_is_seeded(marks, engine, capsys, needs_r):
    got = row(make(marks, engine).compare_averages("marks", for_each="class", based_on="ranks"))
    # R: set.seed(1); rank_epsilon_squared(marks ~ factor(class), data = m, alternative = "two.sided")
    # (its interval is a bootstrap interval, so the seed matters)
    check(got, 0.142220101781171, 0.0365679234841254, 0.358476382847193)
    assert "95 % bootstrap CI, R seed 1, 0.0366 to 0.358" in capsys.readouterr().out


def test_paired_d_z_and_rank_biserial(marks, engine, needs_r):
    t = make(wide(marks), engine)
    # R: cohens_d(w$marks.Science, w$marks.Maths, paired = TRUE)  (d_z)
    check(row(t.compare_before_after("Maths", "Science")), 0.343140520876757, -0.137518864396722, 0.814356210703588)
    # R: rank_biserial(w$marks.Science, w$marks.Maths, paired = TRUE)
    check(row(t.compare_before_after("Maths", "Science", based_on="ranks")),
          0.415204678362573, -0.0842847502564112, 0.747935458117184)


def test_one_sample_d_and_rank_biserial(marks, engine, needs_r):
    t = make(marks, engine)
    # R: cohens_d(m$marks, mu = 60)
    check(row(t.compare_average_to("marks", 60)), 0.326564908279835, 0.0512707381458087, 0.598936826988719)
    # R: rank_biserial(m$marks, mu = 60)
    check(row(t.compare_average_to("marks", 60, based_on="ranks")),
          0.35959595959596, 0.0697328888433453, 0.593464504368646)


def test_cohens_w_interval(engine, needs_r):
    data = pd.DataFrame({"pea": ["round yellow"] * 315 + ["round green"] * 108 + ["wrinkled yellow"] * 101
                         + ["wrinkled green"] * 32})
    expected = {"round yellow": 9 / 16, "round green": 3 / 16, "wrinkled yellow": 3 / 16, "wrinkled green": 1 / 16}
    got = row(make(data, engine).compare_counts_to("pea", expected=expected))
    # R: cohens_w(c(315, 108, 101, 32), p = c(9, 3, 3, 1) / 16, alternative = "two.sided")
    check(got, 0.0290751934124272, 0.0, 0.0657318699884045)


def test_cramers_v_interval(marks, engine, needs_r):
    data = marks.assign(result=np.where(marks["marks"] >= 60, "pass", "fail"))
    got = row(make(data, engine).compare_counts("result", for_each="class"))
    # R: cramers_v(matrix(c(14, 4, 11, 7, 8, 10), 2), adjust = FALSE, alternative = "two.sided")
    check(got, 0.279145263119541, 0.0, 0.521471238299739)


def test_each_pair_rank_biserial(marks, engine, needs_r):
    table = make(marks, engine).compare_each_pair("marks", for_each="class", based_on="ranks")
    rows = table._frame.to_pandas()
    # R: rank_biserial(a, b); rank_biserial(a, c); rank_biserial(b, c)
    want = [(0.317901234567901, -0.053037711867011, 0.611747283108239),
            (0.518518518518519, 0.18959127532783, 0.742805552481671),
            (0.237654320987654, -0.139201924510926, 0.554381384394156)]
    for (_, got), (value, low, high) in zip(rows.iterrows(), want):
        assert got["rank-biserial correlation"] == pytest.approx(value, rel=REL)
        assert got["rank-biserial correlation 95 % CI low"] == pytest.approx(low, rel=REL)
        assert got["rank-biserial correlation 95 % CI high"] == pytest.approx(high, rel=REL)


def test_without_r_the_test_runs_and_a_note_says_how_to_add_the_effect_size(marks, capsys, monkeypatch):
    from simplydata import _r

    monkeypatch.setattr(_r, "_STATE", {"error": "no R", "missing": "rpy2"})
    ab = marks[marks["class"].isin(["A", "B"])].reset_index(drop=True)
    got = row(make_table(ab).compare_averages("marks", for_each="class"))
    out = capsys.readouterr().out
    assert 0 < got["p-value"] < 1 and got["test"] == "Welch's t-test"  # the test itself still runs
    assert math.isnan(got["effect size"]) and math.isnan(got["effect size 95 % CI low"])
    assert "Hedges' g" not in out.split("\n")[0]
    assert ("Note: Hedges' g and its 95 % CI come from the R package effectsize, which is not ready here; to add "
            'them: pip install "simplydata[r]", install R, then in R install.packages("effectsize").') in out
    # Cramer's V still comes from SciPy; only its interval needs R
    data = marks.assign(result=np.where(marks["marks"] >= 60, "pass", "fail"))
    got = row(make_table(data).compare_counts("result", for_each="class"))
    assert got["effect size"] == pytest.approx(0.279145263119541, rel=REL)
    assert math.isnan(got["effect size 95 % CI low"])
    assert "the 95 % CI of Cramer's V comes from the R package effectsize" in capsys.readouterr().out
