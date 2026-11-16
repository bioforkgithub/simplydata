"""S1: one-sided tests (sides=1, higher=) and Kendall's tau-b.

Every number is checked against R 4.6.2 (the R call is written next to each value). The data is
sdata.get_example("school"), read in R with s <- read.csv(".../data/school.csv"); d is s without
the rows that have an empty cell in the columns used. Every table test runs on pandas and Polars.
"""

import math

import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table

REL = 1e-9

BEFORE = [12.1, 14.3, 11.8, 13.0, 15.2, 12.7, 14.9, 13.3, 12.2, 14.0]
AFTER = [13.4, 15.0, 12.1, 14.6, 15.0, 14.1, 16.0, 13.9, 13.7, 14.8]  # no tied changes, so both exact


@pytest.fixture(params=["pandas", "polars"])
def engine(request):
    return request.param


def make(data, engine):
    if engine == "polars":
        pl = pytest.importorskip("polars")
        return make_table(pl.from_pandas(data))
    return make_table(data)


def one_row(result):
    return result._frame.to_pandas().iloc[0].to_dict()


@pytest.fixture
def school(engine):
    return make(sdata.get_example("school"), engine)


@pytest.fixture
def paired(engine):
    return make(pd.DataFrame({"before": BEFORE, "after": AFTER}), engine)


# ---------------------------------------------------------------------------- two groups
def test_welch_one_sided(school, capsys):
    # R: t.test(marks ~ breakfast, data = d, alternative = "less")  (no minus yes)
    r = one_row(school.compare_averages_of("marks", for_each_group_in="breakfast", sides=1, higher="yes"))
    assert r["statistic"] == pytest.approx(-1.9730177601226, rel=REL)
    assert r["p-value"] == pytest.approx(0.0253040147019375, rel=1e-8)
    assert math.isinf(r["difference 95 % CI low"]) and r["difference 95 % CI low"] < 0
    assert r["difference 95 % CI high"] == pytest.approx(-0.545768234156755, rel=1e-8)
    assert r["sides"] == "one-sided: yes higher"
    out = capsys.readouterr().out
    assert "one-sided 95 % CI of the difference at most -0.546" in out
    assert "One-sided, as you asked before seeing the data: it only looks for yes higher than no" in out
    # the other way: alternative = "greater", p 0.974695985298063, CI from -6.26092072905395
    r = one_row(school.compare_averages_of("marks", for_each_group_in="breakfast", sides=1, higher="no"))
    assert r["p-value"] == pytest.approx(0.974695985298063, rel=1e-8)
    assert r["difference 95 % CI low"] == pytest.approx(-6.26092072905395, rel=1e-8)
    # var.equal = TRUE: p 0.0243051559708369, CI high -0.569330601690158
    r = one_row(school.compare_averages_of("marks", for_each_group_in="breakfast", test="student", sides=1, higher="yes"))
    assert r["p-value"] == pytest.approx(0.0243051559708369, rel=1e-8)
    assert r["difference 95 % CI high"] == pytest.approx(-0.569330601690158, rel=1e-8)


def test_mann_whitney_one_sided(school):
    # R: wilcox.test(marks ~ breakfast, data = d, alternative = "less"): W 3126.5, p 0.0344358958589947
    r = one_row(school.compare_averages_of("marks", for_each_group_in="breakfast", based_on="ranks", sides=1, higher="yes"))
    assert r["statistic"] == pytest.approx(3126.5)
    assert r["p-value"] == pytest.approx(0.0344358958589947, rel=1e-8)


def test_r_alternative_is_accepted_and_translated(school, capsys):
    r = one_row(school.compare_averages_of("marks", for_each_group_in="breakfast", alternative="less"))
    assert r["p-value"] == pytest.approx(0.0253040147019375, rel=1e-8)
    assert 'alternative="less" is sides=1, higher="yes" in simplydata' in capsys.readouterr().out
    two = one_row(school.compare_averages_of("marks", for_each_group_in="breakfast", alternative="two-sided"))
    assert "sides" not in two


def test_two_sided_output_is_unchanged(school, capsys):
    r = one_row(school.compare_averages_of("marks", for_each_group_in="breakfast"))
    assert "sides" not in r
    assert "One-sided" not in capsys.readouterr().out


def test_one_sided_errors(school):
    with pytest.raises(SimplydataError, match="needs higher="):
        school.compare_averages_of("marks", for_each_group_in="breakfast", sides=1)
    with pytest.raises(SimplydataError, match="goes with sides=1"):
        school.compare_averages_of("marks", for_each_group_in="breakfast", higher="yes")
    with pytest.raises(SimplydataError, match='Did you mean higher="yes"'):
        school.compare_averages_of("marks", for_each_group_in="breakfast", sides=1, higher="yess")
    with pytest.raises(SimplydataError, match="sides=2 .* or sides=1"):
        school.compare_averages_of("marks", for_each_group_in="breakfast", sides=3)
    with pytest.raises(SimplydataError, match="no one direction"):
        school.compare_averages_of("marks", for_each_group_in="school", sides=1, higher="School A")
    with pytest.raises(SimplydataError, match="give only one of them"):
        school.compare_averages_of("marks", for_each_group_in="breakfast", sides=1, higher="yes", alternative="less")


# ---------------------------------------------------------------------------- before / after
def test_paired_one_sided(paired, capsys):
    # R: t.test(after, before, paired = TRUE, alternative = "greater")
    r = one_row(paired.compare_before_and_after("before", "after", sides=1, higher="after"))
    assert r["statistic"] == pytest.approx(4.97681564037139, rel=REL)
    assert r["p-value"] == pytest.approx(0.000381377570221779, rel=1e-8)
    assert r["average change 95 % CI low"] == pytest.approx(0.574819256075016, rel=1e-8)
    assert math.isinf(r["average change 95 % CI high"])
    assert r["sides"] == 'one-sided: "after" higher'
    assert "at least 0.575" in capsys.readouterr().out
    # alternative = "less": p 0.999618622429778
    r = one_row(paired.compare_before_and_after("before", "after", sides=1, higher="before"))
    assert r["p-value"] == pytest.approx(0.999618622429778, rel=1e-8)
    # wilcox.test(after, before, paired = TRUE, alternative = "greater"): V 54, p 0.001953125 (exact)
    r = one_row(paired.compare_before_and_after("before", "after", based_on="ranks", sides=1, higher="after"))
    assert r["statistic"] == pytest.approx(54)
    assert r["p-value"] == pytest.approx(0.001953125, rel=1e-9)


# ---------------------------------------------------------------------------- one sample
def test_average_to_one_sided(school):
    # R: t.test(d$marks, mu = 60, alternative = "less"): p 1.4865222960572e-30, CI high 49.8390112944356
    r = one_row(school.compare_average_to("marks", 60, sides=1, lower="average"))
    assert r["p-value"] == pytest.approx(1.4865222960572e-30, rel=1e-6)
    assert r["average 95 % CI high"] == pytest.approx(49.8390112944356, rel=1e-8)
    # alternative = "greater": t -13.89544397879, p 1, CI low 47.0943220388977
    r = one_row(school.compare_average_to("marks", 60, sides=1, higher="average"))
    assert r["statistic"] == pytest.approx(-13.89544397879, rel=REL)
    assert r["p-value"] == pytest.approx(1.0)
    assert r["average 95 % CI low"] == pytest.approx(47.0943220388977, rel=1e-8)
    # wilcox.test(d$marks, mu = 60, alternative = "greater"): V 1102.5, p 1
    r = one_row(school.compare_average_to("marks", 60, based_on="ranks", sides=1, higher="average"))
    assert r["statistic"] == pytest.approx(1102.5)
    assert r["p-value"] == pytest.approx(1.0)


def test_percent_to_one_sided(school, capsys):
    # R: binom.test(78, 180, 0.5, alternative = "less"): p 0.0430936566643476
    r = one_row(school.compare_percent_to("passed", value="yes", percent=50, sides=1, lower="percent"))
    assert r["p-value"] == pytest.approx(0.0430936566643476, rel=1e-9)
    assert 'alternative = "less"' in capsys.readouterr().out
    # alternative = "greater": p 0.968946617073507
    r = one_row(school.compare_percent_to("passed", value="yes", percent=50, sides=1, higher="percent"))
    assert r["p-value"] == pytest.approx(0.968946617073507, rel=1e-9)


# ---------------------------------------------------------------------------- correlations
def test_kendall_tau_b(school, capsys):
    # R: cor.test(hours, marks, method = "kendall", exact = FALSE): tau 0.431552246850169, p 3.06411038565608e-17
    r = school.find_correlation_between("hours", "marks", method="kendall")
    assert r == pytest.approx(0.431552246850169, rel=1e-9)
    assert "Kendall's tau-b" in capsys.readouterr().out
    table = school.find_correlation_between("hours", "marks", "sleep", method="kendall", show="each pair")
    first = table._frame.to_pandas().iloc[0]
    assert first["method"] == "Kendall's tau-b" and first["r"] == pytest.approx(0.431552246850169, rel=1e-9)
    assert first["p-value"] == pytest.approx(3.06411038565608e-17, rel=1e-6)


@pytest.mark.parametrize("method, r_value", [
    ("pearson", 0.61980333949393),   # cor.test(hours, marks, alternative = "greater"): p 8.74847121796118e-21
    ("spearman", 0.59486942541815),  # ..., method = "spearman", exact = FALSE: p 6.5292274128961e-19
    ("kendall", 0.431552246850169),  # ..., method = "kendall", exact = FALSE: p 1.53205519282804e-17
])
def test_correlation_one_sided(school, capsys, method, r_value):
    r = school.find_correlation_between("hours", "marks", method=method, sides=1, higher="positive")
    assert r == pytest.approx(r_value, rel=1e-9)
    out = capsys.readouterr().out
    assert "it only looks for a positive correlation" in out and 'alternative = "greater"' in out


def test_correlation_one_sided_p_values():
    from simplydata.table.summaries import SummaryWords

    frame = make_table(sdata.get_example("school"))._frame
    for method, side, p in [("pearson", "greater", 8.74847121796118e-21), ("spearman", "greater", 6.5292274128961e-19),
                            ("kendall", "greater", 1.53205519282804e-17), ("kendall", "less", 1.0)]:
        _, got, _ = SummaryWords._correlate("x", frame, "hours", "marks", method, side)
        assert got == pytest.approx(p, rel=1e-6), (method, side)


def test_correlation_one_sided_errors(school):
    with pytest.raises(SimplydataError, match="two columns"):
        school.find_correlation_between("hours", "marks", "sleep", sides=1, higher="positive")
    with pytest.raises(SimplydataError, match="needs higher="):
        school.find_correlation_between("hours", "marks", sides=1)


# ---------------------------------------------------------------------------- lower= (the mirror of higher=)
def test_lower_is_the_mirror_of_higher(school, paired):
    # R: t.test(marks ~ breakfast, data = d, alternative = "less"): lower="no" is higher="yes"
    lower = one_row(school.compare_averages_of("marks", for_each_group_in="breakfast", sides=1, lower="no"))
    assert lower["p-value"] == pytest.approx(0.0253040147019375, rel=1e-8)
    assert lower["sides"] == "one-sided: yes higher"
    # R: t.test(after, before, paired = TRUE, alternative = "greater"): lower="before" is higher="after"
    r = one_row(paired.compare_before_and_after("before", "after", sides=1, lower="before"))
    assert r["p-value"] == pytest.approx(0.000381377570221779, rel=1e-8)


def test_r_alternative_names_lower_for_one_sample(school, capsys):
    # R: t.test(d$marks, mu = 60, alternative = "less")
    r = one_row(school.compare_average_to("marks", 60, alternative="less"))
    assert r["p-value"] == pytest.approx(1.4865222960572e-30, rel=1e-6)
    assert 'alternative="less" is sides=1, lower="average" in simplydata' in capsys.readouterr().out


def test_higher_and_lower_errors(school):
    with pytest.raises(SimplydataError, match="both higher= and lower="):
        school.compare_averages_of("marks", for_each_group_in="breakfast", sides=1, higher="yes", lower="no")
    with pytest.raises(SimplydataError, match='Did you mean lower="no"'):
        school.compare_averages_of("marks", for_each_group_in="breakfast", sides=1, lower="noo")
    with pytest.raises(SimplydataError, match="goes with sides=1"):
        school.compare_averages_of("marks", for_each_group_in="breakfast", lower="no")
    with pytest.raises(SimplydataError, match='does not know higher="value"'):
        school.compare_average_to("marks", 60, sides=1, higher="value")  # the old word is gone
    with pytest.raises(SimplydataError, match='does not know lower="given"'):
        school.compare_percent_to("passed", value="yes", percent=50, sides=1, lower="given")
    with pytest.raises(SimplydataError, match="takes higher= for a one-sided test, not lower="):
        school.find_correlation_between("hours", "marks", sides=1, lower="negative")
