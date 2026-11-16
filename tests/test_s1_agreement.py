"""S1 Part D: agreement_between, limits_of_agreement, reliability_of.

Reference values: R 4.6.2 (irr 0.85, psych 2.6.9, DescTools 0.99.60, BlandAltmanLeh 0.3.1) on the example
table clinic. Script: F:/claude_work/scratch/simplydata/s1_d/d_ref.R.
"""

import math

import numpy as np
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table

REL = 1e-9
ORDER = ["mild", "moderate", "severe"]


@pytest.fixture(params=["pandas", "polars"])
def engine(request):
    return request.param


def make(engine, data=None):
    data = sdata.get_example("clinic") if data is None else data
    if engine == "polars":
        pl = pytest.importorskip("polars")
        return make_table(pl.from_pandas(data))
    return make_table(data)


def row(result):
    return result._frame.to_pandas().iloc[0].to_dict()


def test_cohens_kappa(engine, capsys):
    got = row(make(engine).agreement_between("nurse_rating", "doctor_rating"))
    # R: irr::kappa2(cbind(nurse, doctor)): value, statistic; psych::cohen.kappa()$confid[1, ]
    assert got["estimate"] == pytest.approx(0.5159765551144, rel=REL)
    assert (got["statistic name"], got["statistic"]) == ("z", pytest.approx(10.3622779984, rel=REL))
    assert (got["estimate 95 % CI low"], got["estimate 95 % CI high"]) == pytest.approx(
        (0.4179143113528, 0.614038798876), rel=REL)
    assert got["raw agreement"] == pytest.approx(136 / 200)
    out = capsys.readouterr().out
    assert '"nurse_rating" and "doctor_rating" agree on 136 of 200 rows (68.0 %)' in out
    assert "Cohen's kappa = 0.516 (95 % CI 0.418 to 0.614): they agree 52 % of the way from chance to perfect" in out
    assert "Agreement is not correlation" in out


def test_weighted_kappa_and_level(engine):
    t = make(engine)
    got = row(t.agreement_between("nurse_rating", "doctor_rating", near_misses="linear", in_order=ORDER))
    # R: irr::kappa2(..., weight = "equal"): value 0.582587954681, statistic 10.82609453405
    assert (got["estimate"], got["statistic"]) == pytest.approx((0.582587954681, 10.82609453405), rel=REL)
    got = row(t.agreement_between("nurse_rating", "doctor_rating", near_misses="quadratic", in_order=ORDER))
    # R: kappa2(..., weight = "squared"): 0.6564005866331, z 9.359837975856; psych::cohen.kappa weighted CI
    assert (got["estimate"], got["statistic"]) == pytest.approx((0.6564005866331, 9.359837975856), rel=REL)
    assert (got["estimate 95 % CI low"], got["estimate 95 % CI high"]) == pytest.approx(
        (0.5632888923777, 0.7495122808886), rel=REL)
    got = row(t.agreement_between("nurse_rating", "doctor_rating", interval=90))
    # R: psych::cohen.kappa(..., alpha = 0.10)$confid[1, 1]
    assert got["estimate 90 % CI low"] == pytest.approx(0.433680125899, rel=REL)


def test_fleiss_kappa(engine, needs_r):
    data = sdata.get_example("clinic")
    data["crp_rating"] = np.where(data.crp > 3, "severe", np.where(data.crp > 1.5, "moderate", "mild"))
    got = row(make(engine, data).agreement_between("nurse_rating", "doctor_rating", "crp_rating"))
    # R: irr::kappam.fleiss(cbind(nurse, doctor, crp coded 1-3)): value, statistic
    assert got["estimate"] == pytest.approx(0.2553084431921, rel=REL)
    assert (got["statistic name"], got["statistic"]) == ("z", pytest.approx(8.818284886262, rel=1e-9))


@pytest.mark.parametrize("options, name, expected", [
    # R: irr::icc(cbind(device_a, device_b), model =, type =, unit =): value, lbound, ubound
    ({}, "twoway_agreement_single", (0.938834756965, 0.8937258725702, 0.9616016437585)),
    ({"raters": "these only", "checking_for": "consistency"}, "twoway_consistency_single",
     (0.9483786034937, 0.9323498556937, 0.9606868305061)),
    ({"raters": "different per row"}, "oneway_consistency_single", (0.9385254375713, 0.9195943831064,
                                                                     0.9531126639668)),
    # McGraw and Wong's words are accepted too
    ({"raters": "fixed", "checking_for": "consistency"}, "twoway_consistency_single",
     (0.9483786034937, 0.9323498556937, 0.9606868305061)),
    ({"raters": "different"}, "oneway_consistency_single", (0.9385254375713, 0.9195943831064, 0.9531126639668)),
    ({"of": "average of raters"}, "twoway_agreement_average", (0.9684525755404, 0.9434971279195, 0.9805034834157)),
])
def test_icc(engine, needs_r, options, name, expected):
    got = row(make(engine).agreement_between("device_a", "device_b", **options))
    assert (got["estimate"], got["estimate 95 % CI low"], got["estimate 95 % CI high"]) == pytest.approx(
        expected, rel=1e-9)


def test_icc_names_the_form(engine, needs_r, capsys):
    got = row(make(engine).agreement_between("pain_week_0", "pain_week_4", "pain_week_8"))
    # R: irr::icc(cbind(pain_week_0, pain_week_4, pain_week_8), "twoway", "agreement", "single")
    assert got["estimate"] == pytest.approx(0.5418222881951, rel=1e-9)
    assert got["estimate 95 % CI low"] == pytest.approx(0.1954946896383, rel=1e-9)
    # R: irr::icc(cbind(pain_week_0, pain_week_4, pain_week_8), "twoway", "agreement", "single")$Fvalue
    assert (got["statistic name"], got["statistic"]) == ("F", pytest.approx(8.512933300136, rel=1e-9))
    out = capsys.readouterr().out
    assert "ICC(A,1), two-way random" in out and "Shrout and Fleiss ICC(2,1)" in out
    assert "Koo and Li's guide the interval runs from poor to moderate" in out


def test_krippendorff_and_lin(engine, needs_r):
    t = make(engine)
    # R: irr::kripp.alpha(t(codes), method = "ordinal" / "nominal" / "interval")$value
    got = row(t.agreement_between("nurse_rating", "doctor_rating", method="krippendorff", in_order=ORDER))
    assert got["estimate"] == pytest.approx(0.6581141431302, rel=1e-9)
    got = row(t.agreement_between("nurse_rating", "doctor_rating", method="krippendorff"))
    assert got["estimate"] == pytest.approx(0.5154551147037, rel=1e-9)
    got = row(t.agreement_between("device_a", "device_b", method="krippendorff"))
    assert got["estimate"] == pytest.approx(0.9383804965401, rel=1e-9)
    assert got["kind of data"] == "numbers (interval data)"
    # R: DescTools::CCC(device_a, device_b)$rho.c
    got = row(t.agreement_between("device_a", "device_b", method="lin"))
    assert (got["estimate"], got["estimate 95 % CI low"], got["estimate 95 % CI high"]) == pytest.approx(
        (0.9385462825355, 0.9199064864308, 0.952954422034), rel=1e-9)


def test_limits_of_agreement(engine, needs_r, capsys):
    got = row(make(engine).limits_of_agreement("device_a", "device_b"))
    # R: BlandAltmanLeh::bland.altman.stats(device_a, device_b): mean.diffs, lower.limit, upper.limit, CI.lines
    assert got["average difference"] == pytest.approx(-2.18, rel=REL)
    assert (got["lower limit"], got["upper limit"]) == pytest.approx((-11.68858126898, 7.328581268977), rel=REL)
    assert (got["lower limit 95 % CI low"], got["lower limit 95 % CI high"]) == pytest.approx(
        (-12.860244, -10.516919), abs=1e-6)
    assert (got["upper limit 95 % CI low"], got["upper limit 95 % CI high"]) == pytest.approx(
        (6.156919, 8.500244), abs=1e-6)
    assert (got["average difference 95 % CI low"], got["average difference 95 % CI high"]) == pytest.approx(
        (-2.856460, -1.503540), abs=1e-6)
    assert got["concordance correlation"] == pytest.approx(0.9385462825355, rel=1e-9)
    out = capsys.readouterr().out
    assert '"device_a" reads on average 2.18 lower than "device_b"' in out
    assert "between -11.7 and 7.33" in out and "Bland and Altman 1986" in out


def test_limits_level(engine, needs_r):
    got = row(make(engine).limits_of_agreement("device_a", "device_b", interval=90))
    # R: bland.altman.stats(..., conf.int = 0.90)$CI.lines[1]; the limits themselves stay at 1.96 SD
    assert got["lower limit 90 % CI low"] == pytest.approx(-12.670463, abs=1e-6)
    assert got["lower limit"] == pytest.approx(-11.68858126898, rel=REL)


def test_reliability_of(engine, needs_r, capsys):
    items = ["item_1", "item_2", "item_3", "item_4", "item_5"]
    got = make(engine).reliability_of(items)._frame.to_pandas().set_index("measure")
    # R: psych::alpha(clinic[, item_1:item_5]): total$raw_alpha, feldt$lower.ci / upper.ci, alpha.drop$raw_alpha
    alpha = got.loc["Cronbach's alpha"]
    assert (alpha["estimate"], alpha["estimate 95 % CI low"], alpha["estimate 95 % CI high"]) == pytest.approx(
        (0.8652461208651, 0.8332882485658, 0.8926695915909), rel=1e-9)
    assert got.loc["alpha without item_3", "estimate"] == pytest.approx(0.8254930, abs=1e-7)
    assert got.loc["alpha without item_1", "estimate"] == pytest.approx(0.8475974, abs=1e-7)
    out = capsys.readouterr().out
    assert "No single item raises alpha" in out and "does not show that the items measure one thing" in out


def test_errors(engine):
    t = make(engine)
    with pytest.raises(SimplydataError, match="at least 2 columns"):
        t.agreement_between("device_a")
    with pytest.raises(SimplydataError, match="near_misses= is for Cohen's kappa"):
        t.agreement_between("device_a", "device_b", near_misses="linear")
    with pytest.raises(SimplydataError, match="in_order= leaves out"):
        t.agreement_between("nurse_rating", "doctor_rating", near_misses="linear", in_order=["mild", "severe"])
    with pytest.raises(SimplydataError, match='method="icc" needs columns of numbers'):
        t.agreement_between("nurse_rating", "doctor_rating", method="icc")
    with pytest.raises(SimplydataError, match="two columns of numbers"):
        t.limits_of_agreement("device_a", "ward")
    with pytest.raises(SimplydataError, match="same column twice"):
        t.agreement_between("device_a", "device_a")


def test_fleiss_without_r_keeps_kappa(engine, monkeypatch, capsys):
    from simplydata import _r

    def missing(*args, **kwargs):
        raise _r.RMissing("no R")

    monkeypatch.setattr(_r, "r_call", missing)
    data = sdata.get_example("clinic")
    data["third"] = data["doctor_rating"]
    got = row(make(engine, data).agreement_between("nurse_rating", "doctor_rating", "third"))
    assert math.isnan(got["p-value"]) and got["estimate"] > 0
    assert 'install.packages("irr")' in capsys.readouterr().out


def test_old_and_other_names_of_near_misses(engine, capsys):
    t = make(engine)
    new = row(t.agreement_between("nurse_rating", "doctor_rating", near_misses="linear", in_order=ORDER))
    for option in ("weights", "weight", "wt"):
        old = row(t.agreement_between("nurse_rating", "doctor_rating", in_order=ORDER, **{option: "linear"}))
        assert old["estimate"] == new["estimate"]
    out = capsys.readouterr().out
    assert '"weights=" is now called "near_misses="' in out
    assert "Note: weight= is near_misses= in simplydata." in out and "Note: wt= is near_misses=" in out
