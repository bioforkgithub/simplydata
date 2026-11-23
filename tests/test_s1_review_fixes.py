"""S1 review fixes: zero cells in risks and rates, kappa's chance agreement, friendly answers where a number
cannot be worked out, one-sided wording, likelihood ratios below 1, the ICC call, the partial correlation's
rows and Kendall's interval.

Reference values: R 4.6.2 (epitools 0.5.10.1, epiR 3.0.0, irr, ppcor, DescTools); the R call is next to each
value. Scripts: F:/claude_work/scratch/simplydata/s1_fix/r_zero.R, r_ref.R, r_ref2.R.
"""

import math

import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table
from conftest import example_frame

REL = 1e-9


def rows(result):
    frame = result._frame.to_pandas()
    return {r["measure"] + ("" if pd.isna(r.get("group")) else " " + str(r["group"])): r.to_dict()
            for _, r in frame.iterrows()}


def ci(row):
    return row["estimate"], row["estimate 95 % CI low"], row["estimate 95 % CI high"]


# ------------------------------------------------------------------ item 1: a 0 in the 2 x 2 table
def test_risk_zero_cell_as_r(capsys):
    got = rows(sdata.compare_risks(events=[5, 0], out_of=[10, 10], against="group 2"))
    # R: prop.test(c(5, 0), c(10, 10))$p.value (the shifted table gave 0.070)
    assert got["risk difference group 1"]["p-value"] == pytest.approx(0.03886710381, rel=REL)
    # R: epitools::riskratio(matrix(c(10, 0, 5, 5), 2, byrow = TRUE), method = "wald")$measure[2, ]: Inf NaN Inf
    rr = got["risk ratio group 1"]
    assert rr["estimate"] == math.inf and math.isnan(rr["estimate 95 % CI low"])
    # R: epitools::oddsratio(same, method = "wald")$measure[2, ]: Inf NaN Inf
    assert got["odds ratio group 1"]["estimate"] == math.inf
    out = capsys.readouterr().out
    assert "Risk ratio infinite (its interval cannot be worked out): there are no events in group 2." in out
    assert "Odds ratio infinite (its interval cannot be worked out)." in out
    assert "simplydata does not add 0.5 to the empty cells" in out
    assert "p = 0.039" in out and "nan" not in out


def test_risk_zero_cell_in_the_no_event_column():
    got = rows(sdata.compare_risks(events=[10, 5], out_of=[10, 10], against="group 2"))
    # R: epitools::riskratio(matrix(c(5, 5, 0, 10), 2, byrow = TRUE), method = "wald")$measure[2, ]
    assert ci(got["risk ratio group 1"]) == pytest.approx((2.0, 1.076109420, 3.717094121), rel=1e-9)
    # R: epitools::oddsratio(same, method = "wald")$measure[2, 1]: Inf
    assert got["odds ratio group 1"]["estimate"] == math.inf
    # R: prop.test(c(10, 5), c(10, 10))$p.value
    assert got["risk difference group 1"]["p-value"] == pytest.approx(0.03886710381, rel=REL)


@pytest.mark.parametrize("events, words", [([0, 0], "no events in either group"),
                                           ([10, 10], "the event in every row")])
def test_risk_no_test_when_a_whole_column_is_empty(events, words, capsys):
    got = rows(sdata.compare_risks(events=events, out_of=[10, 10]))
    # R: prop.test(c(0, 0), c(10, 10))$p.value and prop.test(c(10, 10), c(10, 10))$p.value: NaN
    assert math.isnan(got["risk difference group 2"]["p-value"])
    # R: epitools::oddsratio(...)$measure[2, 1]: NaN in both
    assert math.isnan(got["odds ratio group 2"]["estimate"])
    if events == [0, 0]:  # R epitools::riskratio: NaN
        assert math.isnan(got["risk ratio group 2"]["estimate"])
    else:  # R epitools::riskratio(matrix(c(0, 10, 0, 10), 2, byrow = TRUE), method = "wald"): 1, 1, 1
        assert ci(got["risk ratio group 2"]) == pytest.approx((1.0, 1.0, 1.0))
    out = capsys.readouterr().out
    assert "The p-value cannot be worked out" in out and words in out
    assert "nan" not in out


@pytest.fixture(params=["pandas", "polars"])
def engine(request):
    return request.param


def test_risk_zero_cell_table_route(engine, capsys):
    data = pd.DataFrame({"g": ["A"] * 6 + ["B"] * 6, "ev": ["no"] * 6 + ["yes"] * 3 + ["no"] * 3})
    if engine == "polars":
        pl = pytest.importorskip("polars")
        data = pl.from_pandas(data)
    got = rows(make_table(data).compare_risks("ev", for_each_group_in="g", against="A"))
    # R: prop.test(c(3, 0), c(6, 6))$p.value (the shifted table gave 0.301)
    assert got["risk difference B"]["p-value"] == pytest.approx(0.18242243945, rel=REL)
    # R: epitools::riskratio(matrix(c(6, 0, 3, 3), 2, byrow = TRUE), method = "wald")$measure[2, 1]: Inf
    assert got["risk ratio B"]["estimate"] == math.inf
    assert "Risk ratio infinite" in capsys.readouterr().out


def test_risk_zero_cell_exact():
    got = rows(sdata.compare_risks(events=[5, 0], out_of=[10, 10], against="group 2", p_value_by="exact"))
    # R: fisher.test(matrix(c(5, 0, 5, 10), 2)): p.value, estimate, conf.int
    odds = got["odds ratio group 1"]
    assert odds["p-value"] == pytest.approx(0.03250773993808, rel=REL)
    assert odds["estimate"] == math.inf
    # SciPy's root search for the conditional interval stops within about 3e-5 of R's
    assert odds["estimate 95 % CI low"] == pytest.approx(1.19539603854492, rel=1e-4)


def test_risk_zero_cell_one_sided(needs_r, capsys):
    got = rows(sdata.compare_risks(events=[5, 0], out_of=[10, 10], against="group 2", sides=1, higher="group 1"))
    # R: prop.test(c(5, 0), c(10, 10), alternative = "greater")$p.value
    assert got["risk difference group 1"]["p-value"] == pytest.approx(0.01943355190621, rel=REL)
    # item 5: the house null wording
    assert "If the risk in group 1 were truly not higher than in group 2, a difference" in capsys.readouterr().out


# ------------------------------------------------------------------ item 3: no raw errors
def test_rates_with_no_events(capsys):
    got = rows(sdata.compare_rates(events=[0, 0], time=[100, 100]))
    # R: poisson.test(c(0, 0), c(100, 100))$estimate: NaN
    assert math.isnan(got["rate ratio group 2"]["estimate"])
    out = capsys.readouterr().out
    assert "the rate ratio is 0 / 0, which cannot be worked out" in out and "nan" not in out


def test_rates_with_no_events_in_one_group(needs_r, capsys):
    got = rows(sdata.compare_rates(events=[5, 0], time=[100, 100], against="group 2"))
    # R: poisson.test(c(5, 0), c(100, 100)): estimate Inf, conf.int 0.9163558573155 Inf, p.value 0.0625
    ratio = got["rate ratio group 1"]
    assert ratio["estimate"] == math.inf
    assert ratio["estimate 95 % CI low"] == pytest.approx(0.9163558573155, rel=1e-9)
    assert ratio["p-value"] == pytest.approx(0.0625, rel=REL)
    assert "Rate ratio infinite (95 % CI 0.916 to infinite): there are no events in group 2." in capsys.readouterr().out


def test_rates_one_sided_wording(needs_r, capsys):
    got = rows(sdata.compare_rates(events=[30, 15], time=[1100, 1200], names=["A", "B"], against="B", sides=1,
                                   higher="A"))
    # R: poisson.test(c(30, 15), c(1100, 1200), alternative = "greater")$p.value
    assert got["rate ratio A"]["p-value"] == pytest.approx(0.008385036268266, rel=1e-9)
    assert "If the rate in A were truly not higher than in B, a difference" in capsys.readouterr().out


def test_counts_with_an_empty_column():
    # R: chisq.test(matrix(c(0, 0, 5, 7), 2))$p.value: NaN
    with pytest.raises(SimplydataError, match="only zeros in column 1"):
        sdata.compare_counts([[0, 5], [0, 7]])


def test_truth_from_percents_with_no_positives(capsys):
    got = rows(sdata.compare_to_truth(sensitivity=0, specificity=100, prevalence=1))
    assert math.isnan(got["positive predictive value"]["estimate"])
    # 990 of 1000 negatives are right (Bayes' rule): 0.99
    assert got["negative predictive value"]["estimate"] == pytest.approx(0.99)
    out = capsys.readouterr().out
    assert "no one tests positive" in out and "nan" not in out


def test_truth_from_counts_with_no_positives(needs_r, capsys):
    got = rows(sdata.compare_to_truth(found=0, missed=5, false_alarms=0, correct_negatives=50))
    # R: epiR::epi.tests(as.table(matrix(c(0, 5, 0, 50), nrow = 2)), method = "exact")$detail: lr.pos NaN,
    # lr.neg 1 (1 to 1), pv.pos NaN
    assert math.isnan(got["positive likelihood ratio"]["estimate"])
    assert ci(got["negative likelihood ratio"]) == pytest.approx((1.0, 1.0, 1.0))
    assert math.isnan(got["positive predictive value"]["estimate"])
    out = capsys.readouterr().out
    assert "The positive likelihood ratio cannot be worked out" in out and "nan" not in out


def test_positive_likelihood_ratio_below_one(needs_r, capsys):
    got = rows(sdata.compare_to_truth(found=5, missed=15, false_alarms=40, correct_negatives=40))
    # R: epiR::epi.tests(as.table(matrix(c(5, 15, 40, 40), nrow = 2)), method = "exact")$detail["lr.pos", ]
    assert ci(got["positive likelihood ratio"]) == pytest.approx((0.5, 0.2269027150107, 1.101793779718), rel=1e-9)
    out = capsys.readouterr().out
    assert "A positive result is less common in people who have it than in people who do not: only 0.500 times" in out
    assert "times more common" not in out


def test_p_sentence_with_nan():
    from simplydata.table.summaries import _p_sentence

    assert _p_sentence(math.nan) == ("The p-value cannot be worked out with these numbers (it is NaN), so this test "
                                     "gives no answer.")


# ------------------------------------------------------------------ item 2: kappa
ORDER = ["mild", "moderate", "severe"]


def kappa_table():
    data = example_frame("clinic")
    return make_table(data)


def test_weighted_kappa_leaves_out_chance(capsys):
    got = kappa_table().agreement_between("nurse_rating", "doctor_rating", near_misses="quadratic", in_order=ORDER)
    frame = got._frame.to_pandas()
    assert "agreement by chance" not in frame.columns
    # R: irr::kappa2(cbind(factor(nurse, lv), factor(doctor, lv)), weight = "squared")$value
    assert frame["estimate"][0] == pytest.approx(0.6564005866331, rel=REL)
    out = capsys.readouterr().out
    assert "by chance alone" not in out and "sorted order" not in out
    assert "agree exactly on 136 of 200 rows" in out and "Weighted kappa (quadratic weights) = 0.656" in out


def test_unweighted_kappa_keeps_chance(capsys):
    got = kappa_table().agreement_between("nurse_rating", "doctor_rating")._frame.to_pandas()
    # read back from R irr::kappa2()$value 0.5159765551144 and the raw agreement 136 / 200
    assert got["agreement by chance"][0] == pytest.approx((0.68 - 0.5159765551144) / (1 - 0.5159765551144), rel=1e-9)
    assert "by chance alone they would agree on about 33.9 %" in capsys.readouterr().out


def test_perfect_kappa_has_no_nan(capsys):
    t = make_table(pd.DataFrame({"a": list("xyxyxy"), "b": list("xyxyxy")}))
    got = t.agreement_between("a", "b")._frame.to_pandas()
    assert got["estimate"][0] == pytest.approx(1.0)
    out = capsys.readouterr().out
    assert "agree on 6 of 6 rows (100 %). Cohen's kappa = 1.00" in out and "nan" not in out


def test_icc_one_way_names_the_call(needs_r, capsys):
    got = kappa_table().agreement_between("pain_week_0", "pain_week_4", raters="different per row")
    method = got.get_row(1)["method"]
    # the one-way ICC is psych::ICC's row ICC1 whatever checking_for= says (irr::icc ignored type= there too)
    assert method == "R psych::ICC(lmer = FALSE), row ICC1"
    assert "its row ICC1" in capsys.readouterr().out


# ------------------------------------------------------------------ items 4 and 9: correlation
def test_partial_correlation_whole_r_on_the_same_rows(needs_r, capsys):
    t = make_table(pd.DataFrame({"a": [1, 2, 3, 4, 5, 6, 7, 8.], "b": [1, 3, 2, 5, 4, 7, 6, 1.],
                                 "z": [3, 1, 4, 1, 5, 9, 2, None]}))
    t.find_correlation_between("a", "b", allowing_for="z")
    out = capsys.readouterr().out
    # R: ppcor::pcor.test(a[1:7], b[1:7], z[1:7])$estimate 0.8744360902256; cor(a[1:7], b[1:7]) 0.8928571428571
    # (cor(a, b) on all 8 rows is 0.3735488486479)
    assert "is r = 0.87 (Pearson, 7 rows)" in out and "without allowing for it, r = 0.89." in out


def test_kendall_interval_words(needs_r, capsys):
    t = make_table(sdata.get_example("marks"))
    t.find_correlation_between("hours", "marks", test_method="kendall")
    # R: DescTools::KendallTauB(hours, marks, conf.level = 0.95): an asymptotic standard error, not Fisher's z
    out = capsys.readouterr().out
    assert "asymptotic standard error, R DescTools" in out and "Fisher's z" not in out
