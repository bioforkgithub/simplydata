"""S1 Part A: more test_method= choices on compare_averages, compare_spreads and compare_counts.

Reference values: R 4.6.2 on sdata.get_example("marks") (m <- read.csv(".../marks.csv"); a, b, cc = the marks of
classes A, B and C; ab = the rows of classes A and B; res = ifelse(m$marks >= 60, "60 or more", "below 60")).
"""

import numpy as np
import pytest

import simplydata as sdata
from simplydata import SimplydataError
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


@pytest.fixture
def marks():
    return sdata.get_example("marks")


@pytest.fixture
def ab(marks, engine):
    return make(marks[marks["class"].isin(["A", "B"])].reset_index(drop=True), engine)


@pytest.fixture
def counts(marks, engine):
    return make(marks.assign(result=np.where(marks["marks"] >= 60, "60 or more", "below 60")), engine)


# ---------------------------------------------------------------------------- compare_averages
def test_yuen(ab, capsys):
    got = row(ab.compare_averages_of("marks", for_each_group_in="class", test_method="yuen"))
    # R: WRS2::yuen(marks ~ class, data = ab, tr = 0.2)
    assert got["statistic"] == pytest.approx(1.53468088195914, rel=REL)
    assert got["p-value"] == pytest.approx(0.13915081007666, rel=1e-8)
    assert got["degrees of freedom"] == pytest.approx(21.9509839847125, rel=REL)
    assert got["difference 95 % CI low"] == pytest.approx(-2.37271466231451, rel=1e-8)
    assert got["difference 95 % CI high"] == pytest.approx(15.8727146623145, rel=1e-8)
    assert "WRS2::yuen(tr = 0.2)" in capsys.readouterr().out


def test_brunner_munzel(ab):
    got = row(ab.compare_averages_of("marks", for_each_group_in="class", test_method="brunner-munzel"))
    # R: brunnermunzel::brunnermunzel.test(a, b)
    assert got["statistic"] == pytest.approx(-1.695062129278, rel=REL)
    assert got["p-value"] == pytest.approx(0.0993777514031908, rel=1e-8)
    ranks = row(ab.compare_averages_of("marks", for_each_group_in="class", based_on="ranks", test_method="brunner-munzel"))
    assert ranks["p-value"] == got["p-value"]


def test_alexander_govern(marks, engine):
    got = row(make(marks, engine).compare_averages_of("marks", for_each_group_in="class", test_method="alexander-govern"))
    # R: onewaytests::ag.test(marks ~ class, data = m)  (onewaytests 3.2)
    assert got["statistic"] == pytest.approx(7.10054816479951, rel=REL)
    assert got["p-value"] == pytest.approx(0.0287167678148864, rel=1e-8)


def test_mood_median_test(marks, engine, capsys):
    got = row(make(marks, engine).compare_averages_of("marks", for_each_group_in="class", test_method="median"))
    # R: chisq.test(table(m$class, m$marks > median(m$marks)))
    assert got["statistic"] == pytest.approx(4.0, rel=REL)
    assert got["p-value"] == pytest.approx(0.135335283236613, rel=1e-8)
    assert got["overall median"] == 68.5
    assert "above the overall median (68.5)" in capsys.readouterr().out


def test_more_average_tests_errors(marks, ab):
    with pytest.raises(SimplydataError, match="exactly 2 groups"):
        make_table(marks).compare_averages_of("marks", for_each_group_in="class", test_method="yuen")
    with pytest.raises(SimplydataError, match="no one direction"):
        ab.compare_averages_of("marks", for_each_group_in="class", test_method="median", sides=1, higher="B")
    with pytest.raises(SimplydataError, match='based_on="ranks"'):
        ab.compare_averages_of("marks", for_each_group_in="class", based_on="ranks", test_method="yuen")


# ---------------------------------------------------------------------------- compare_spreads
def test_ansari_and_mood(ab):
    # R: ansari.test(a, b): AB 160.5, p 0.504390721965635
    got = row(ab.compare_spreads_of("marks", for_each_group_in="class", test_method="ansari"))
    assert got["statistic"] == 160.5 and got["p-value"] == pytest.approx(0.504390721965635, rel=1e-8)
    # R: mood.test(a, b): Z 0.409386412856107, p 0.682256109163144
    got = row(ab.compare_spreads_of("marks", for_each_group_in="class", test_method="mood"))
    assert got["statistic"] == pytest.approx(0.409386412856107, rel=REL)
    assert got["p-value"] == pytest.approx(0.682256109163144, rel=1e-8)


def test_f_test_of_two_variances(ab, needs_r):
    got = row(ab.compare_spreads_of("marks", for_each_group_in="class", test_method="f"))
    # R: var.test(a, b): F 0.854854218132868 on 17 and 17 df, p 0.7501632316422, CI 0.319774846319096 to 2.28528210605512
    assert got["statistic"] == pytest.approx(0.854854218132868, rel=REL)
    assert (got["degrees of freedom 1"], got["degrees of freedom 2"]) == (17, 17)
    assert got["p-value"] == pytest.approx(0.7501632316422, rel=1e-8)
    assert got["ratio 95 % CI low"] == pytest.approx(0.319774846319096, rel=1e-8)
    assert got["ratio 95 % CI high"] == pytest.approx(2.28528210605512, rel=1e-8)


def test_two_group_spread_tests_need_two_groups(marks):
    with pytest.raises(SimplydataError, match="exactly 2 groups"):
        make_table(marks).compare_spreads_of("marks", for_each_group_in="class", test_method="ansari")


# ---------------------------------------------------------------------------- compare_counts
def test_g_test(counts, capsys):
    got = row(counts.compare_counts_of("result", for_each_group_in="class", test_method="g"))
    # R: DescTools::GTest(table(res, m$class)): G 4.31385046826758, df 2, p 0.115680264495438
    assert got["statistic"] == pytest.approx(4.31385046826758, rel=REL)
    assert got["degrees of freedom"] == 2
    assert got["p-value"] == pytest.approx(0.115680264495438, rel=1e-8)


def test_barnard_and_boschloo_from_r(marks, engine, needs_r):
    data = marks[marks["class"] != "C"].reset_index(drop=True)
    t = make(data.assign(result=np.where(data["marks"] >= 60, "60 or more", "below 60")), engine)
    # R: tab <- matrix(c(14, 4, 11, 7), 2) (rows: result, columns: class). The classes are the two samples and
    # exact.test fixes the row totals, so: Exact::exact.test(t(tab), method = "z-pooled")$p.value
    assert row(t.compare_counts_of("result", for_each_group_in="class", test_method="barnard"))["p-value"] == \
        pytest.approx(0.316097877618, rel=1e-8)
    # Exact::exact.test(t(tab), method = "boschloo")$p.value
    assert row(t.compare_counts_of("result", for_each_group_in="class", test_method="boschloo"))["p-value"] == \
        pytest.approx(0.315498311133, rel=1e-8)


def test_barnard_needs_two_by_two(counts):
    with pytest.raises(SimplydataError, match="2 x 2 tables"):
        counts.compare_counts_of("result", for_each_group_in="class", test_method="barnard")
