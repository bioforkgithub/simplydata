"""S1 Part C3-C5: compare_to_truth, compare_accuracy and sdata.compare_to_truth.

Reference values: R 4.6.2 (epiR 3.0.0, pROC 1.19.1) on the example table clinic (rapid_test against infected:
39 found, 11 missed, 10 false alarms, 140 correct negatives). Script: F:/claude_work/scratch/simplydata/s1_c/acc_ref.R.
"""

import math

import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table

REL = 1e-9


@pytest.fixture(params=["pandas", "polars"])
def clinic(request):
    data = sdata.example("clinic")
    if request.param == "polars":
        pl = pytest.importorskip("polars")
        return make_table(pl.from_pandas(data))
    return make_table(data)


def rows(result):
    return {r["measure"]: r.to_dict() for _, r in result._frame.to_pandas().iterrows()}


def ci(row, level=95):
    return row["estimate"], row[f"estimate {level} % CI low"], row[f"estimate {level} % CI high"]


def test_yes_no_test(clinic, needs_r, capsys):
    got = rows(clinic.compare_to_truth("rapid_test", truth="infected"))
    # R: epiR::epi.tests(table(rapid_test, infected), method = "exact")$detail
    assert ci(got["sensitivity"]) == pytest.approx((0.78, 0.6403881114342, 0.8847341739622), rel=REL)
    assert ci(got["specificity"]) == pytest.approx((0.9333333333333, 0.8808160229331, 0.9675702718413), rel=REL)
    assert ci(got["positive predictive value"]) == pytest.approx((0.7959183673469, 0.6565700069535, 0.8975506145048),
                                                                 rel=REL)
    assert ci(got["negative predictive value"]) == pytest.approx((0.9271523178808, 0.8733948215349, 0.9630754174459),
                                                                 rel=REL)
    assert ci(got["positive likelihood ratio"]) == pytest.approx((11.7, 6.315332693445, 21.67581767182), rel=REL)
    assert ci(got["negative likelihood ratio"]) == pytest.approx((0.2357142857143, 0.1396245127039, 0.3979331667042),
                                                                 rel=REL)
    assert ci(got["diagnostic odds ratio"]) == pytest.approx((49.63636363636, 19.64328170981, 125.4255083971), rel=REL)
    assert got["sensitivity"]["count"] == 39 and got["sensitivity"]["out of"] == 50
    out = capsys.readouterr().out
    assert 'Counted as positive: "rapid_test" = "positive"; as having it: "infected" = "yes".' in out
    assert "Of 1000 people like these (25.0 % have it in this table), 250 have it: the test finds 195" in out
    assert "and 50 test positive by mistake" in out
    assert "A positive result is 11.7 times more common" in out
    assert "give prevalence=1" in out


def test_level_and_prevalence(clinic, capsys):
    got = rows(clinic.compare_to_truth("rapid_test", truth="infected", interval=90, prevalence=1))
    # R: epi.tests(..., conf.level = 0.9)$detail, se lower
    assert got["sensitivity"]["estimate 90 % CI low"] == pytest.approx(0.6622255149586, rel=REL)
    # Bayes' rule [D]: 0.78 * 0.01 / (0.78 * 0.01 + (1 - 14/15) * 0.99)
    ppv = 0.78 * 0.01 / (0.78 * 0.01 + (1 / 15) * 0.99)
    assert got["positive predictive value where 1 % have it"]["estimate"] == pytest.approx(ppv, rel=1e-12)
    out = capsys.readouterr().out
    assert "Of 1000 people like these (1.00 % have it), 10 have it: the test finds 8" in out
    assert "So of the 74 positive results, 8" in out


def test_roc(clinic, needs_r, capsys):
    got = rows(clinic.compare_to_truth("crp", truth="infected"))
    # R: pROC::ci.auc(pROC::roc(truth, crp, levels = c(0, 1), direction = "<"), method = "delong")
    assert ci(got["area under the ROC curve (AUC)"]) == pytest.approx((0.8926, 0.845472585868, 0.939727414132), rel=REL)
    # R: pROC::coords(r, "best", best.method = "youden"): threshold 2.15, sensitivity 0.9, specificity 0.78
    assert got["best cut-off (Youden's index)"]["estimate"] == pytest.approx(2.15, rel=REL)
    assert got["sensitivity"]["estimate"] == pytest.approx(0.9, rel=REL)
    assert got["specificity"]["estimate"] == pytest.approx(0.78, rel=REL)
    out = capsys.readouterr().out
    assert "AUC 0.893 (95 % CI 0.845 to 0.940): a person who has it scores higher" in out
    assert '"crp" 2.15 or more counts as positive' in out and "looks better here than it will on new data" in out


def test_roc_cut_off_and_direction(clinic, needs_r, capsys):
    got = rows(clinic.compare_to_truth("crp", truth="infected", cut_off=3))
    # R: pROC::coords(r, 3, input = "threshold"): sensitivity 0.72, specificity 0.86
    assert got["sensitivity"]["estimate"] == pytest.approx(0.72, rel=REL)
    assert got["specificity"]["estimate"] == pytest.approx(0.86, rel=REL)
    got = rows(clinic.compare_to_truth("crp", truth="infected", positive_when="lower"))
    # R: pROC::auc(pROC::roc(truth, crp, levels = c(0, 1), direction = ">")) = 0.1074
    assert got["area under the ROC curve (AUC)"]["estimate"] == pytest.approx(0.1074, rel=REL)
    assert "the AUC is below 0.5" in capsys.readouterr().out


def test_compare_accuracy(clinic, needs_r, capsys):
    got = rows(clinic.compare_accuracy("crp", "procalcitonin", truth="infected"))
    # R: pROC::roc.test(r_crp, r_pct, method = "delong", paired = TRUE): statistic, p.value, conf.int
    diff = got["difference in AUC (crp minus procalcitonin)"]
    assert diff["statistic"] == pytest.approx(3.773182385548, rel=REL)
    assert diff["p-value"] == pytest.approx(0.0001611783712565, rel=1e-8)
    assert (diff["estimate 95 % CI low"], diff["estimate 95 % CI high"]) == pytest.approx(
        (0.08528234065708, 0.2696509926763), rel=1e-9)
    # R: ci.auc(r_pct, method = "delong")
    assert got["AUC of procalcitonin"]["estimate"] == pytest.approx(0.7151333333333, rel=REL)
    assert got["AUC of procalcitonin"]["estimate 95 % CI low"] == pytest.approx(0.6356566991099, rel=REL)
    assert "DeLong's test" in capsys.readouterr().out


def test_errors(clinic):
    with pytest.raises(SimplydataError, match="two values"):
        clinic.compare_to_truth("rapid_test", truth="age_group")
    with pytest.raises(SimplydataError, match="cut_off= is for a column of numbers"):
        clinic.compare_to_truth("rapid_test", truth="infected", cut_off=2)
    with pytest.raises(SimplydataError, match="prevalence="):
        clinic.compare_to_truth("rapid_test", truth="infected", prevalence=0)
    with pytest.raises(SimplydataError, match="two score columns"):
        clinic.compare_accuracy("crp", truth="infected")
    with pytest.raises(SimplydataError, match="different columns"):
        clinic.compare_to_truth("infected", truth="infected")


def test_top_level_counts(needs_r, capsys):
    got = rows(sdata.compare_to_truth(found=45, missed=5, false_alarms=30, correct_negatives=920))
    # R: epiR::epi.tests(as.table(matrix(c(45, 5, 30, 920), nrow = 2)), method = "exact")$detail
    assert got["sensitivity"]["estimate 95 % CI low"] == pytest.approx(0.7818646335658, rel=REL)
    assert got["positive predictive value"]["estimate 95 % CI low"] == pytest.approx(0.4803704692543, rel=REL)
    assert ci(got["positive likelihood ratio"])[:2] == pytest.approx((28.5, 19.80315974344), rel=REL)
    assert "Of 1000 people like these (5.00 % have it in this table), 50 have it" in capsys.readouterr().out


def test_top_level_base_rate(capsys):
    # Casscells et al. (1978): 1 in 1000 have it, 5 % false positives, every case found
    got = rows(sdata.compare_to_truth(sensitivity=100, specificity=95, prevalence=0.1))
    out = capsys.readouterr().out
    assert "1 has it: the test finds 1 (sensitivity 100 %) and misses 0" in out
    assert "So of the 51 positive results, 1 (1.96 %) really have it" in out
    assert got["positive predictive value"]["estimate"] == pytest.approx(0.001 / (0.001 + 0.05 * 0.999), rel=1e-12)
    with pytest.raises(SimplydataError, match="four counts"):
        sdata.compare_to_truth(sensitivity=90)


def test_without_r_keeps_python_part(clinic, monkeypatch, capsys):
    from simplydata import _r

    def missing(*args, **kwargs):
        raise _r.RMissing("no R")

    monkeypatch.setattr(_r, "r_call", missing)
    got = rows(clinic.compare_to_truth("rapid_test", truth="infected"))
    assert got["sensitivity"]["estimate"] == pytest.approx(0.78)
    assert math.isnan(got["positive likelihood ratio"]["estimate"])
    assert 'install.packages("epiR")' in capsys.readouterr().out
    with pytest.raises(_r.RMissing):
        clinic.compare_to_truth("crp", truth="infected")


def test_top_level_risks_and_rates(needs_r):
    got = sdata.compare_risks(events=[20, 30], out_of=[60, 60], names=["new medicine", "usual care"],
                              against="usual care")._frame.to_pandas().set_index("measure")
    # R: epitools::riskratio(matrix(c(30, 30, 40, 20), 2, byrow = TRUE), method = "wald"): 0.4301048003 to 1.033339884
    assert got.loc["risk ratio", "estimate 95 % CI low"] == pytest.approx(0.4301048003, rel=1e-9)
    assert got.loc["risk ratio", "estimate 95 % CI high"] == pytest.approx(1.033339884, rel=1e-9)
    # R: DescTools::BinomDiffCI(20, 60, 30, 60, method = "score"): -0.3288011693 to 0.009241460436
    assert got.loc["risk difference", "estimate 95 % CI low"] == pytest.approx(-0.3288011693, rel=1e-9)
    got = sdata.compare_rates(events=[15, 30], time=[1200, 1100])._frame.to_pandas().set_index("measure")
    # R: poisson.test(c(30, 15), c(1100, 1200))$p.value = 0.01599749855 (the same test either way round)
    assert got.loc["rate ratio", "p-value"] == pytest.approx(0.01599749855, rel=1e-9)
    with pytest.raises(SimplydataError, match="at most its out_of="):
        sdata.compare_risks(events=[70, 30], out_of=[60, 60])
    assert isinstance(got, pd.DataFrame)


def test_other_names_of_the_counts(capsys):
    a = sdata.compare_to_truth(found=45, missed=5, false_alarms=30, correct_negatives=920)._frame.to_pandas()
    b = sdata.compare_to_truth(tp=45, fn=5, fp=30, tn=920)._frame.to_pandas()
    assert a["estimate"].iloc[:4].tolist() == b["estimate"].iloc[:4].tolist()
    c = sdata.compare_to_truth(true_positives=45, false_negatives=5, false_positives=30,
                               true_negatives=920)._frame.to_pandas()
    assert a["estimate"].iloc[:4].tolist() == c["estimate"].iloc[:4].tolist()
    out = capsys.readouterr().out
    assert "Note: tp= is found= in simplydata." in out and "Note: true_negatives= is correct_negatives=" in out
