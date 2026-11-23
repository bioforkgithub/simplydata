"""S1 Part A, second half: compare_matched, compare_shapes, check_random_order, McNemar,
Bowker and the sign test in compare_before_after, more tests in compare_shape_to, percent
intervals (method=), and tests from summary numbers (sdata.compare_averages / compare_counts).

Reference values: R 4.6.2. m <- read.csv(".../marks.csv") (example_frame("marks"));
w <- reshape(m[, c("name", "subject", "marks")], idvar = "name", timevar = "subject",
direction = "wide"); mm <- as.matrix(w[, -1]) (columns Maths, Science, English);
a, b, cc = the marks of classes A, B and C.
"""

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table
from conftest import example_frame

REL = 1e-9


@pytest.fixture(params=["pandas", "polars"])
def engine(request):
    return request.param


def make(data, engine):
    if engine == "polars":
        pl = pytest.importorskip("polars")
        return make_table(data, fast=True)
    return make_table(data)


def row(result):
    return result._frame.to_pandas().iloc[0].to_dict()


@pytest.fixture
def marks():
    return example_frame("marks")


@pytest.fixture
def wide(marks, engine):
    w = marks.pivot(index="name", columns="subject", values="marks").reset_index()
    return make(w[["name", "Maths", "Science", "English"]], engine)


@pytest.fixture
def wide_yes_no(marks, engine):
    w = marks.pivot(index="name", columns="subject", values="marks").reset_index()
    for c in ("Maths", "Science", "English"):
        w[c] = np.where(w[c] > 60, "yes", "no")
    return make(w[["name", "Maths", "Science", "English"]], engine)


# ---------------------------------------------------------------------------- compare_matched
def test_friedman(wide, capsys, needs_r):
    got = row(wide.compare_matched_columns("Maths", "Science", "English"))
    # R: friedman.test(mm)
    assert got["statistic"] == pytest.approx(5.77777777778, rel=REL)
    assert got["p-value"] == pytest.approx(0.0556379982778, rel=REL)
    assert got["degrees of freedom"] == 2
    # R: set.seed(1); effectsize::kendalls_w(mm, ci = 0.95, alternative = "two.sided")
    assert got["effect size"] == pytest.approx(0.16049382716, rel=REL)
    assert got["effect size 95 % CI low"] == pytest.approx(0.0216049382716, rel=1e-8)
    assert got["effect size 95 % CI high"] == pytest.approx(0.527611365427, rel=1e-8)
    assert got["median of Science"] == 70
    out = capsys.readouterr().out
    assert "because the columns hold numbers" in out and "R friedman.test()" in out
    assert "about 6 of 100 studies" in out and "95 % bootstrap CI, R seed 1" in out


def test_friedman_without_r_still_tests(wide, capsys, monkeypatch):
    from simplydata import _r

    def missing(*args, **kwargs):
        raise _r.RMissing("no R")

    monkeypatch.setattr(_r, "r_call", missing)
    got = row(wide.compare_matched_columns(["Maths", "Science", "English"]))
    assert got["p-value"] == pytest.approx(0.0556379982778, rel=REL)
    assert np.isnan(got["effect size"])
    assert 'install.packages("effectsize")' in capsys.readouterr().out


def test_quade(wide, needs_r):
    got = row(wide.compare_matched_columns("Maths", "Science", "English", test_method="quade"))
    # R: quade.test(mm)
    assert got["statistic"] == pytest.approx(1.67488109114, rel=REL)
    assert got["p-value"] == pytest.approx(0.202417611028, rel=REL)
    assert (got["degrees of freedom 1"], got["degrees of freedom 2"]) == (2, 34)


def test_cochran(wide_yes_no, capsys):
    got = row(wide_yes_no.compare_matched_columns("Maths", "Science", "English"))
    # R: y <- mm > 60; DescTools::CochranQTest(y)
    assert got["statistic"] == pytest.approx(1.846153846, rel=1e-9)
    assert got["p-value"] == pytest.approx(0.397294713, rel=1e-8)
    assert got["count of yes in Science"] == 13
    out = capsys.readouterr().out
    assert "because the columns are yes/no" in out and "DescTools::CochranQTest()" in out


def test_matched_two_columns_is_before_after(wide, capsys):
    got = row(wide.compare_matched_columns("Maths", "Science"))
    assert got["test"] == "Wilcoxon signed-rank test"
    assert 'is compare_before_and_after("Maths", "Science")' in capsys.readouterr().out


def test_matched_errors(wide):
    with pytest.raises(SimplydataError, match="comes later"):
        wide.compare_matched_columns("Maths", "Science", "English", based_on="averages")
    with pytest.raises(SimplydataError, match='Did you mean test_method="quade"'):
        wide.compare_matched_columns("Maths", "Science", "English", test_method="quad")
    with pytest.raises(SimplydataError, match="yes/no columns"):
        wide.compare_matched_columns("Maths", "Science", "English", test_method="cochran")
    with pytest.raises(SimplydataError, match="same column twice"):
        wide.compare_matched_columns("Maths", "Maths", "English")


# ---------------------------------------------------------------------------- compare_shapes
def test_shapes_two_groups_without_ties(engine, capsys):
    data = pd.DataFrame({"group": ["x"] * 8 + ["y"] * 8,
                         "value": [3.1, 4.7, 5.2, 6.8, 7.3, 8.9, 9.4, 10.6, 5.9, 7.7, 8.1, 9.8, 11.2, 12.5, 13.3, 14.0]})
    got = row(make(data, engine).compare_shapes_of("value", for_each_group_in="group"))
    # R: ks.test(c(3.1, 4.7, 5.2, 6.8, 7.3, 8.9, 9.4, 10.6), c(5.9, 7.7, 8.1, 9.8, 11.2, 12.5, 13.3, 14.0))
    assert got["statistic"] == pytest.approx(0.5)
    assert got["p-value"] == pytest.approx(0.282672882673, rel=1e-9)
    assert got["biggest gap at"] == pytest.approx(7.3)
    out = capsys.readouterr().out
    assert "62 % of x's values are at or below it, but only 12 % of y's" in out


def test_shapes_two_groups_with_ties_from_r(marks, engine, needs_r):
    ab = make(marks[marks["class"].isin(["A", "B"])].reset_index(drop=True), engine)
    got = row(ab.compare_shapes_of("marks", for_each_group_in="class"))
    # R: ks.test(a, b) (exact, with ties)
    assert got["statistic"] == pytest.approx(1 / 3)
    assert got["p-value"] == pytest.approx(0.246938074, rel=1e-8)


def test_shapes_three_groups(marks, engine, capsys):
    got = row(make(marks, engine).compare_shapes_of("marks", for_each_group_in="class"))
    # R: kSamples::ad.test(a, b, cc) version 2 (midrank): T.AD 2.3389; set.seed(1);
    # ad.test(a, b, cc, method = "simulated", Nsim = 100000): sim. p 0.03516 (Monte Carlo, SE about 0.0018)
    assert got["statistic"] == pytest.approx(2.338929394250999, rel=1e-9)
    assert got["p-value"] == pytest.approx(0.03516, abs=0.006)
    assert got["p-value"] == pytest.approx(0.0373, abs=1e-12)  # SciPy, seed 1: the same every time
    assert "shuffling the group labels 9999 times (seed 1)" in capsys.readouterr().out


# ---------------------------------------------------------------------------- check_random_order
def test_runs(marks, engine, capsys):
    got = row(make(marks, engine).check_if_random_order("marks"))
    # R: randtests::runs.test(m$marks)
    assert got["statistic"] == pytest.approx(-1.648620247, rel=1e-9)
    assert got["p-value"] == pytest.approx(0.0992254582, rel=1e-8)
    assert got["runs"] == 22
    assert "fewer runs than a random order" in capsys.readouterr().out


def test_runs_leaves_out_the_median(marks, engine, capsys):
    got = row(make(marks.iloc[:53], engine).check_if_random_order("marks"))
    # R: randtests::runs.test(m$marks[1:53]) (one value equals the median, 68, and is left out)
    assert got["statistic"] == pytest.approx(-1.680659211, rel=1e-9)
    assert got["p-value"] == pytest.approx(0.0928291276, rel=1e-8)
    assert got["values equal to the median (left out)"] == 1
    assert "1 value was equal to the median and left out, as R does" in capsys.readouterr().out


def test_runs_sorted_by(marks, engine):
    by_height = row(make(marks, engine).check_if_random_order("marks", sorted_by="height"))
    assert by_height["what it compares"].startswith('the order of "marks" (order of "height")')


# ---------------------------------------------------------------------------- McNemar, Bowker, sign test
@pytest.fixture
def pain(engine):
    before = ["yes"] * 22 + ["no"] * 8
    after = ["yes"] * 9 + ["no"] * 13 + ["yes"] + ["no"] * 7
    return make(pd.DataFrame({"pain_before": before, "pain_after": after}), engine)


def test_mcnemar(pain, capsys, needs_r):
    got = row(pain.compare_before_and_after("pain_before", "pain_after"))
    # R: tab <- table(before, after) (yes/no first: 9 13 / 1 7); mcnemar.test(tab)
    assert got["statistic"] == pytest.approx(8.64285714286, rel=REL)
    assert got["p-value"] == pytest.approx(0.00328346098607, rel=REL)
    # R: exact2x2::mcnemarExactDP(x = 1, m = 14, n = 30): -0.4, CI -0.608030041090 to -0.131290821224
    assert got["effect size"] == pytest.approx(-40.0)
    assert got["effect size 95 % CI low"] == pytest.approx(-60.8030041090, rel=1e-9)
    assert got["effect size 95 % CI high"] == pytest.approx(-13.1290821224, rel=1e-9)
    out = capsys.readouterr().out
    assert "13 rows changed" in out and "because both columns are yes/no" in out


def test_mcnemar_exact(pain, needs_r):
    got = row(pain.compare_before_and_after("pain_before", "pain_after", p_value_by="exact"))
    # R: exact2x2::exact2x2(tab, paired = TRUE)$p.value = binom.test(13, 14)$p.value
    assert got["p-value"] == pytest.approx(0.0018310546875, rel=REL)


def test_mcnemar_without_r(pain, capsys, monkeypatch):
    from simplydata import _r

    def missing(*args, **kwargs):
        raise _r.RMissing("no R")

    monkeypatch.setattr(_r, "r_call", missing)
    got = row(pain.compare_before_and_after("pain_before", "pain_after"))
    assert got["p-value"] == pytest.approx(0.00328346098607, rel=REL)
    assert 'install.packages("exact2x2")' in capsys.readouterr().out


def test_mcnemar_on_zero_one_numbers(engine, needs_r):
    data = pd.DataFrame({"b": [1] * 22 + [0] * 8, "a": [1] * 9 + [0] * 13 + [1] + [0] * 7})
    got = row(make(data, engine).compare_before_and_after("b", "a"))
    assert got["test"] == "McNemar's test with continuity correction"
    assert got["p-value"] == pytest.approx(0.00328346098607, rel=REL)


def test_bowker(engine, capsys):
    r1 = ("mild mild moderate severe mild moderate moderate severe mild severe moderate mild severe moderate mild "
          "mild severe moderate mild moderate severe mild").split()
    r2 = ("mild moderate moderate severe mild mild severe severe moderate moderate moderate mild severe severe mild "
          "moderate moderate moderate mild mild mild severe").split()
    got = row(make(pd.DataFrame({"r1": r1, "r2": r2}), engine).compare_before_and_after("r1", "r2"))
    # R: mcnemar.test(table(factor(r1, lev), factor(r2, lev)))
    assert got["statistic"] == pytest.approx(0.2, rel=REL)
    assert got["p-value"] == pytest.approx(0.977589297762, rel=REL)
    assert got["degrees of freedom"] == 3
    assert "because the columns hold 3 categories" in capsys.readouterr().out


def test_bowker_empty_pair(engine):
    data = pd.DataFrame({"r1": ["a", "a", "b", "c", "a", "b", "c"], "r2": ["a", "b", "b", "c", "b", "a", "c"]})
    with pytest.raises(SimplydataError, match="Merge categories"):
        make(data, engine).compare_before_and_after("r1", "r2")


def test_sign_test(wide):
    got = row(wide.compare_before_and_after("Maths", "Science", test_method="sign"))
    # R: DescTools::SignTest(Science, Maths): S = 13 of 18, p 0.0962524414
    assert got["p-value"] == pytest.approx(0.09625244140625, rel=REL)
    assert got["rows that went up"] == 13 and got["rows that went down"] == 5


def test_before_after_errors(pain, wide):
    with pytest.raises(SimplydataError, match="leave out sides="):
        pain.compare_before_and_after("pain_before", "pain_after", sides=1, higher="after")
    with pytest.raises(SimplydataError, match="for yes/no columns"):
        wide.compare_before_and_after("Maths", "Science", p_value_by="exact")
    with pytest.raises(SimplydataError, match='Did you mean test_method="sign"'):
        wide.compare_before_and_after("Maths", "Science", test_method="sing")


# ---------------------------------------------------------------------------- compare_shape_to(test=)
@pytest.mark.parametrize("test, statistic, p, rel", [
    # R: moments / fBasics::dagoTest(m$marks): omnibus chi2 0.861554399020, p 0.650003715789
    ("dagostino", 0.861554399020, 0.650003715789, 1e-9),
    # R: tseries::jarque.bera.test(m$marks)
    ("jarque-bera", 0.9517696535, 0.621335039, 1e-8),
])
def test_shape_tests_python(marks, engine, test, statistic, p, rel):
    got = row(make(marks, engine).compare_shape_to("marks", "normal", test_method=test))
    assert got["statistic"] == pytest.approx(statistic, rel=rel)
    assert got["p-value"] == pytest.approx(p, rel=rel)


def test_lilliefors_from_r(marks, engine, needs_r):
    got = row(make(marks, engine).compare_shape_to("marks", "normal", test_method="lilliefors"))
    # R: nortest::lillie.test(m$marks)
    assert got["statistic"] == pytest.approx(0.1073207791, rel=1e-9)
    assert got["p-value"] == pytest.approx(0.125638638, rel=1e-8)


def test_shape_against_fixed_distribution(marks, engine, capsys):
    dist = sdata.distribution("normal", average=60, standard_deviation=15)
    t = make(marks, engine)
    got = row(t.compare_shape_to("marks", dist))
    # R: ks.test(m$marks, "pnorm", 60, 15) (ties, so the asymptotic p-value, as R)
    assert got["statistic"] == pytest.approx(0.2257468822, rel=1e-9)
    assert got["p-value"] == pytest.approx(0.00814206366, rel=1e-8)
    got = row(t.compare_shape_to("marks", dist, test_method="cramer-von-mises"))
    # R: goftest::cvm.test(m$marks, "pnorm", mean = 60, sd = 15)
    assert got["statistic"] == pytest.approx(0.7205431156, rel=1e-9)
    assert got["p-value"] == pytest.approx(0.0110539382, rel=1e-8)
    assert 'as R goftest::cvm.test(x, "pnorm", ...)' in capsys.readouterr().out


def test_shape_test_errors(marks, engine):
    t = make(marks, engine)
    with pytest.raises(SimplydataError, match="fixed numbers"):
        t.compare_shape_to("marks", "normal", test_method="kolmogorov-smirnov")
    with pytest.raises(SimplydataError, match='Did you mean test_method="jarque-bera"'):
        t.compare_shape_to("marks", "normal", test_method="jarque-berra")
    with pytest.raises(SimplydataError, match="leave out test_method="):
        t.compare_shape_to("marks", "gamma", test_method="lilliefors")


# ---------------------------------------------------------------------------- percent intervals
@pytest.mark.parametrize("method, low, high", [
    # R: DescTools::BinomCI(78, 180, method = "clopper-pearson" / "wilson" / "agresti-coull")
    ("wilson", 0.363081784442, 0.506370948614),
    ("agresti-coull", 0.363068525819, 0.506384207238),
])
def test_percent_to_intervals(engine, method, low, high):
    school = make(example_frame("school"), engine)
    got = row(school.compare_percent_to("passed", value="yes", percent=50, interval_by=method))
    assert got["percent 95 % CI low"] == pytest.approx(low * 100, rel=1e-9)
    assert got["percent 95 % CI high"] == pytest.approx(high * 100, rel=1e-9)
    # R: binom.test(78, 180, p = 0.5): the test does not change
    assert got["p-value"] == pytest.approx(0.0861873133287, rel=1e-9)


def test_percent_to_one_sided_wilson(engine):
    school = make(example_frame("school"), engine)
    got = row(school.compare_percent_to("passed", value="yes", percent=50, interval_by="wilson", sides=1,
                                        higher="percent"))
    # R: DescTools::BinomCI(78, 180, method = "wilson", sides = "left")
    assert got["percent 95 % CI low"] == pytest.approx(37.401122265, rel=1e-9)
    with pytest.raises(SimplydataError, match="two-sided interval only"):
        school.compare_percent_to("passed", value="yes", percent=50, interval_by="agresti-coull", sides=1,
                                  higher="percent")


def test_percent_of_methods(marks, engine, capsys):
    t = make(marks, engine)
    t.find_percent_of_rows_where("marks", is_above=60, interval_by="wilson")
    # R: DescTools::BinomCI(33, 54, method = "wilson"): 0.477882985382 to 0.729580661709
    assert "95 % CI 47.8 % to 73.0 %, Wilson score interval" in capsys.readouterr().out
    got = t.find_percent_of_rows_where("marks", is_above=60, for_each_group_in="class", interval_by="agresti-coull")._frame.to_pandas()
    # R: DescTools::BinomCI(c(14, 11, 8), 18, method = "agresti-coull")
    assert got["percent 95 % CI low"].tolist() == pytest.approx([54.2501488614, 38.5425626440, 24.5406689603],
                                                                rel=1e-9)
    with pytest.raises(SimplydataError, match='Did you mean interval_by="wilson"'):
        t.find_percent_of_rows_where("marks", is_above=60, interval_by="wilsn")


# ---------------------------------------------------------------------------- summary numbers
def test_sdata_compare_averages_two(capsys, needs_r):
    got = row(sdata.compare_averages(averages=[63.2, 68.9], standard_deviations=[8.1, 9.0], counts=[20, 22]))
    # R: BSDA::tsum.test(63.2, 8.1, 20, 68.9, 9.0, 22)
    assert got["statistic"] == pytest.approx(-2.16021969969, rel=REL)
    assert got["p-value"] == pytest.approx(0.0368034565793, rel=REL)
    assert got["difference 95 % CI low"] == pytest.approx(-11.032860696171, rel=REL)
    assert got["difference 95 % CI high"] == pytest.approx(-0.367139303829, rel=1e-8)
    assert got["degrees of freedom"] == pytest.approx(39.99765861, rel=1e-8)
    got = row(sdata.compare_averages(averages=[63.2, 68.9], standard_deviations=[8.1, 9.0], counts=[20, 22],
                                     test_method="student"))
    # R: BSDA::tsum.test(63.2, 8.1, 20, 68.9, 9.0, 22, var.equal = TRUE)
    assert got["p-value"] == pytest.approx(0.0377245777462, rel=REL)
    assert got["difference 95 % CI low"] == pytest.approx(-11.060241569315, rel=REL)


def test_sdata_compare_averages_many():
    got = row(sdata.compare_averages(averages=[71.8333333333333333, 64.2777777777777778, 58.6111111111111111],
                                     standard_deviations=[13.7423775663628, 14.8633206469347, 14.1800974396755],
                                     counts=[18, 18, 18], names=["A", "B", "C"]))
    # R: oneway.test(marks ~ class, m) on the rows (these are their averages and standard deviations)
    assert got["statistic"] == pytest.approx(3.99431889864, rel=1e-9)
    assert got["degrees of freedom 2"] == pytest.approx(33.9653259624, rel=1e-9)
    assert got["p-value"] == pytest.approx(0.0276731022463, rel=1e-9)
    got = row(sdata.compare_averages(averages=[71.8333333333333333, 64.2777777777777778, 58.6111111111111111],
                                     standard_deviations=[13.7423775663628, 14.8633206469347, 14.1800974396755],
                                     counts=[18, 18, 18], test_method="anova"))
    # R: oneway.test(marks ~ class, m, var.equal = TRUE)
    assert got["p-value"] == pytest.approx(0.0267711379274, rel=1e-9)


def test_sdata_compare_counts(capsys):
    got = row(sdata.compare_counts([[20, 40], [30, 30]]))
    # R: chisq.test(matrix(c(20, 30, 40, 30), 2))
    assert got["statistic"] == pytest.approx(2.777142857, rel=1e-9)
    assert got["p-value"] == pytest.approx(0.0956186087806, rel=REL)
    assert "120 counted" in capsys.readouterr().out
    got = row(sdata.compare_counts(pd.DataFrame([[20, 40], [30, 30]]), test_method="fisher"))
    # R: fisher.test(matrix(c(20, 30, 40, 30), 2))
    assert got["p-value"] == pytest.approx(0.0951740873461, rel=1e-9)


def test_summary_errors():
    with pytest.raises(SimplydataError, match="table.compare_averages_of"):
        sdata.compare_averages(averages=[1, 2])
    with pytest.raises(SimplydataError, match="whole numbers of 2 or more"):
        sdata.compare_averages(averages=[1, 2], standard_deviations=[1, 1], counts=[2.5, 3])
    with pytest.raises(SimplydataError, match="whole numbers of 0 or more"):
        sdata.compare_counts([[1, -2], [3, 4]])
    with pytest.raises(SimplydataError, match="at least 2 rows and 2 columns"):
        sdata.compare_counts([1, 2, 3])
