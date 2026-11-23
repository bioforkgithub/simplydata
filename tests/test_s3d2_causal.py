"""S3d-2, epidemiology and cause and effect: balancing groups (compare_balanced_groups_of), attributable fractions
(compare_risks(show=)), standardised rates (rate_of(standard_population=), compare_rates(standard_rates=)), mediation
(explain(through=)), the 2 x 2 crossover (compare_averages_of(period=)) and multiple imputation for other words
(find_correlation_between and explain_survival with empty_cells=).

The numbers are checked against the packages underneath (statsmodels here; R in the tests marked needs_r, and in the
reliability study on published data).
"""

import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from conftest import r_table
from simplydata import SimplydataError

DATA = Path(__file__).resolve().parents[1] / "validation" / "data"
COLUMNS = ["age", "educ", "race", "married", "nodegree", "re74", "re75"]
NATIONAL = {"0-19": 0.3, "20-39": 1.0, "40-59": 4.0, "60-69": 12.0, "70-79": 30.0, "80+": 90.0}


def _r(code, packages=(), **values):
    from simplydata._r import r_call

    return r_call(code, packages=packages, **values)


# The reference datasets of Schütz, Labes & Fuglsang (2014) are (c) AAPS with no open licence, so they are not shipped
# (DATA_LICENSES.md): the tests of their published answers read them from a file the user names, and skip otherwise.
SCHUTZ_FILE = "SIMPLYDATA_SCHUTZ2014_FILE"


def _schutz(name):
    """Reference dataset A, B or C of Schütz et al. (2014), from the CSV file named by SIMPLYDATA_SCHUTZ2014_FILE
    (columns dataset, subject, period, formulation, auc). Skipped when no file is given; nothing is downloaded."""
    import os

    path = os.environ.get(SCHUTZ_FILE)
    if not path:
        pytest.skip(f"the Schütz et al. (2014) reference datasets are not shipped; name a local copy with {SCHUTZ_FILE}")
    data = pd.read_csv(path)
    return data[data["dataset"] == name].drop(columns="dataset").reset_index(drop=True)


def _crossover(name="A"):
    """A 2 x 2 crossover: the made-up practice table drug_levels, or (B, C) a Schütz reference dataset."""
    return sdata.table(sdata.get_example("drug_levels") if name == "A" else _schutz(name))


def _flutd(swap=False):
    rows = [{"food": "dry", "flutd": "yes"}] * 13 + [{"food": "dry", "flutd": "no"}] * 2163
    rows += [{"food": "other", "flutd": "yes"}] * 5 + [{"food": "other", "flutd": "no"}] * 3349
    return sdata.table(pd.DataFrame(rows))


# ---------------------------------------------------------------- I05: the 2 x 2 crossover (no R)
@pytest.mark.parametrize("name, ratio, low, high", [("A", 95.09, 90.76, 99.62), ("B", 71.10, 51.45, 98.26),
                                                     ("C", 58.56, 39.41, 87.03)])
def test_crossover_gives_the_published_reference_results(name, ratio, low, high):
    """Schütz, Labes & Fuglsang (2014), Table II (R, SAS and WinNonlin agree); needs a local copy of the data."""
    r = sdata.table(_schutz(name)).compare_averages_of("auc", for_each_group_in="formulation", matched_by="subject",
                                                       period="period", same_within=[0.8, 1.25]).get_row(1)
    assert round(r["estimate"] * 100, 2) == ratio
    assert round(r["90 % CI low"] * 100, 2) == low and round(r["90 % CI high"] * 100, 2) == high


def test_crossover_is_the_ema_model_of_statsmodels(capsys):
    import statsmodels.formula.api as smf

    df = sdata.get_example("drug_levels")
    first = df[df["period"] == 1].set_index("subject")["formulation"]
    df = df.assign(sequence=df["subject"].map(first))
    m = smf.ols("np.log(auc) ~ C(sequence) + C(subject) + C(period) + C(formulation)", data=df).fit()
    r = _crossover("A").compare_averages_of("auc", for_each_group_in="formulation", matched_by="subject",
                                            period="period").get_row(1)
    assert r["estimate"] == pytest.approx(math.exp(m.params["C(formulation)[T.test]"]), rel=1e-12)
    assert r["within-subject CV"] == pytest.approx(math.sqrt(math.exp(m.mse_resid) - 1), rel=1e-12)
    assert r["degrees of freedom"] == 16
    out = capsys.readouterr().out
    assert "90 % CI" in out and "carry-over" in out and "EMA" in out
    assert "bioequivalent" not in out  # no margin given, no verdict


def test_crossover_verdicts_and_margin_spellings(capsys):
    t = _crossover("A")
    a = t.compare_averages_of("auc", for_each_group_in="formulation", matched_by="subject", period="period",
                              same_within=1.25).get_row(1)
    assert a["answer"] == "same within the margin" and a["margin low"] == pytest.approx(0.8)
    assert "bioequivalent" in capsys.readouterr().out
    b = _crossover("B").compare_averages_of("auc", for_each_group_in="formulation", matched_by="subject",
                                            period="period", same_within=[0.8, 1.25]).get_row(1)
    assert b["answer"] == "the data cannot tell"
    assert "this does not show that they differ" in capsys.readouterr().out


def test_crossover_against_turns_the_ratio_round():
    t = _crossover("A")
    usual = t.compare_averages_of("auc", for_each_group_in="formulation", matched_by="subject", period="period")
    turned = t.compare_averages_of("auc", for_each_group_in="formulation", matched_by="subject", period="period",
                                   against="test")
    assert turned.get_cell_at(row=1, column="estimate") == pytest.approx(
        1 / usual.get_cell_at(row=1, column="estimate"), rel=1e-12)


def test_crossover_leaves_out_and_names_subjects_without_both_periods(capsys):
    df = sdata.get_example("drug_levels")
    df = df[~((df["subject"] == 3) & (df["period"] == 2))]
    r = sdata.table(df).compare_averages_of("auc", for_each_group_in="formulation", matched_by="subject",
                                            period="period").get_row(1)
    assert r["subjects"] == 17
    assert "1 subject without both formulations" in capsys.readouterr().out


@pytest.mark.parametrize("change, message", [
    (dict(same_within=[0.9, 0.95]), "ratio limits"),
    (dict(same_within=0.8), "margin on the ratio"),
    (dict(sides=1, higher="test"), "leave out sides="),
    (dict(matched_by=None), "give matched_by= the subject column"),
])
def test_crossover_refusals(change, message):
    call = dict(for_each_group_in="formulation", matched_by="subject", period="period")
    call.update(change)
    with pytest.raises(SimplydataError, match=message):
        _crossover("A").compare_averages_of("auc", **call)


def test_crossover_refuses_zero_values_and_one_order():
    df = sdata.get_example("drug_levels")
    zero = df.copy()
    zero.loc[zero.index[0], "auc"] = 0
    with pytest.raises(SimplydataError, match="log scale"):
        sdata.table(zero).compare_averages_of("auc", for_each_group_in="formulation", matched_by="subject",
                                              period="period")
    one_order = df[df["subject"].isin(df[(df["period"] == 1) & (df["formulation"] == "test")]["subject"])]
    with pytest.raises(SimplydataError, match="same order"):
        sdata.table(one_order).compare_averages_of("auc", for_each_group_in="formulation", matched_by="subject",
                                                   period="period")


def test_against_without_period_is_refused():
    with pytest.raises(SimplydataError, match="period="):
        sdata.table(sdata.get_example("marks")).compare_averages_of("marks", for_each_group_in="class", against="A")


# ---------------------------------------------------------------- AD07: mediation (no R)
def test_mediation_is_statsmodels_mediation(capsys):
    import statsmodels.formula.api as smf
    from statsmodels.stats.mediation import Mediation

    df = sdata.get_example("job_search")
    med = smf.ols("job_seek ~ treat + econ_hard + sex + age", data=df)
    out = smf.ols("depress2 ~ treat + job_seek + econ_hard + sex + age", data=df)
    s = Mediation(out, med, "treat", "job_seek").fit(n_rep=1000, rng=1).summary()
    r = sdata.table(df).explain("depress2", using="treat", through="job_seek",
                                allowing_for=["econ_hard", "sex", "age"]).as_pandas().set_index("term")
    for ours, theirs in (("indirect effect (through job_seek)", "ACME (average)"), ("direct effect", "ADE (average)"),
                         ("total effect", "Total effect"), ("share through job_seek", "Prop. mediated (average)")):
        assert r.loc[ours, "estimate"] == pytest.approx(s.loc[theirs, "Estimate"], rel=1e-12)
        assert r.loc[ours, "95 % CI low"] == pytest.approx(s.loc[theirs, "Lower CI bound"], rel=1e-12)
        assert r.loc[ours, "p-value"] == pytest.approx(s.loc[theirs, "P-value"], rel=1e-12)
    text = capsys.readouterr().out
    assert "only if nothing that was not measured" in text and "Baron-Kenny" in text
    assert "the total effect is not clear here" not in text  # made-up data with a built-in effect: it is clear


def test_job_search_is_made_up_with_the_effects_it_says():
    """docs/make_job_search.py draws the table with a fixed seed: a = +0.30, b = -0.30, direct -0.04."""
    import importlib.util

    import statsmodels.formula.api as smf

    from simplydata.data import EXAMPLES

    script = Path(__file__).resolve().parents[1] / "docs" / "make_job_search.py"
    spec = importlib.util.spec_from_file_location("make_job_search", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    shipped = sdata.get_example("job_search")
    pd.testing.assert_frame_equal(module.make().astype(str), shipped.astype(str), check_dtype=False)
    a = smf.ols("job_seek ~ treat + econ_hard + sex + age", data=shipped).fit()
    b = smf.ols("depress2 ~ treat + job_seek + econ_hard + sex + age", data=shipped).fit()
    # within about 2 standard errors of the values built in (the clipping to 1-5 and rounding shrink them a little)
    assert abs(a.params["treat"] - 0.30) < 2 * a.bse["treat"]
    assert abs(b.params["job_seek"] + 0.30) < 2 * b.bse["job_seek"]
    assert abs(b.params["treat"] + 0.04) < 2 * b.bse["treat"]
    assert EXAMPLES["job_search"][0].startswith("MADE-UP DATA")


def test_mediation_simulation_estimates_the_product_of_coefficients():
    import statsmodels.formula.api as smf

    df = sdata.get_example("job_search")
    a = smf.ols("job_seek ~ treat + econ_hard + sex + age", data=df).fit().params["treat"]
    b = smf.ols("depress2 ~ treat + job_seek + econ_hard + sex + age", data=df).fit().params["job_seek"]
    r = sdata.table(df).explain("depress2", using="treat", through="job_seek",
                                allowing_for=["econ_hard", "sex", "age"]).as_pandas().set_index("term")
    assert r.loc["indirect effect (through job_seek)", "estimate"] == pytest.approx(a * b, rel=0.05)


def test_mediation_with_a_yes_or_no_outcome_and_a_text_exposure(capsys):
    df = sdata.get_example("job_search").assign(group=lambda d: np.where(d["treat"] == 1, "workshop", "booklet"))
    r = sdata.table(df).explain("work1", using="group", through="job_seek", outcome="yes or no", against="booklet")
    assert len(r) == 4
    text = capsys.readouterr().out
    assert "workshop against booklet" in text and "logistic regression" in text and '"psyump"' in text


@pytest.mark.parametrize("change, message", [
    (dict(using=["treat", "sex"]), "using= takes the one column"),
    (dict(through="treat"), "must be different columns"),
    (dict(using="age"), "needs two values"),
    (dict(grouped_by="sex"), "leave out grouped_by="),
    (dict(outcome="counts"), 'outcome= is "numbers"'),
])
def test_mediation_refusals(change, message):
    call = dict(using="treat", through="job_seek")
    call.update(change)
    with pytest.raises(SimplydataError, match=message):
        sdata.table(sdata.get_example("job_search")).explain("depress2", **call)


def test_allowing_for_on_explain_needs_through():
    with pytest.raises(SimplydataError, match="go with through="):
        sdata.table(sdata.get_example("school")).explain("marks", using="hours", allowing_for="sleep")


# ---------------------------------------------------------------- AD01-AD03: balancing groups (R)
def test_weighting_is_weightit_with_its_balance_table(needs_r, capsys):
    t = sdata.table(r_table("job_training"))
    r = t.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=COLUMNS).as_pandas().iloc[0]
    assert r["estimate"] == pytest.approx(224.6763, abs=1e-3)  # WeightIt lm_weightit (design: 224.7, SE 876)
    assert r["standard error"] == pytest.approx(876.1932, abs=1e-3)
    assert r["effect for"] == "everyone (ATE)"
    text = capsys.readouterr().out
    for part in ("Overlap:", "Balance (standardised differences", "race: black", "weight above 20",
                 "only if nothing that was not measured", "WeightIt::weightit", "still more than 0.1 apart"):
        assert part in text, part


def test_matching_is_matchit_with_pair_clustered_errors(needs_r, capsys):
    t = sdata.table(r_table("job_training"))
    r = t.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=COLUMNS, test_method="matching",
                                     effect_for=1).as_pandas().iloc[0]
    assert r["estimate"] == pytest.approx(894.3675, abs=1e-3)  # the MatchIt vignette's 894, SE 705
    assert r["standard error"] == pytest.approx(705.2298, abs=1e-3)
    assert r["effect for"] == "1 (ATT)"
    caliper = t.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=COLUMNS,
                                           test_method="matching", effect_for=1, match_within=0.2)
    assert caliper.as_pandas()["estimate"][0] == pytest.approx(1770.6029, abs=1e-3)
    assert "68 rows of \"1\" had no match" in capsys.readouterr().out


def test_balance_table_and_propensity_scores(needs_r):
    t = sdata.table(r_table("job_training"))
    b = t.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=COLUMNS,
                                     show="balance").as_pandas()
    assert list(b.columns) == ["column", "difference before", "difference after"]
    assert b.set_index("column").loc["race: black", "difference before"] == pytest.approx(1.6708, abs=1e-4)
    scores = t.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=COLUMNS,
                                          show="propensity scores").as_pandas()
    fitted = _r("stats::fitted(stats::glm(t ~ age + educ + race + married + nodegree + re74 + re75, "
                "family = stats::binomial()))", t=scores["treat"].to_numpy(float), age=scores["age"].to_numpy(float),
                educ=scores["educ"].to_numpy(float), race=scores["race"].to_numpy(object),
                married=scores["married"].to_numpy(float), nodegree=scores["nodegree"].to_numpy(float),
                re74=scores["re74"].to_numpy(float), re75=scores["re75"].to_numpy(float))
    np.testing.assert_allclose(scores["propensity score"], np.asarray(fitted, dtype=float), rtol=1e-9)


def test_effect_for_a_group_with_weighting_is_the_att(needs_r):
    t = sdata.table(r_table("job_training"))
    r = t.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=COLUMNS, effect_for=1)
    assert r.as_pandas()["estimate"][0] == pytest.approx(1214.0712, abs=1e-3)


def test_a_yes_or_no_outcome_gives_a_risk_difference(needs_r, capsys):
    df = r_table("job_training").assign(earned=lambda d: np.where(d["re78"] > 0, "yes", "no"))
    r = sdata.table(df).compare_balanced_groups_of("earned", for_each_group_in="treat", allowing_for=COLUMNS)
    assert -1 < r.as_pandas()["estimate"][0] < 1
    assert "risk difference" in capsys.readouterr().out


@pytest.mark.parametrize("change, message", [
    (dict(test_method="matching"), "say which with effect_for="),
    (dict(test_method="matching", effect_for="everyone"), 'use test_method="weighting"'),
    (dict(match_within=0.2), 'add test_method="matching"'),
    (dict(allowing_for=None), "needs allowing_for="),
    (dict(effect_for=3), "is not one of the groups"),
    (dict(test_method="stratification"), 'test_method= takes "weighting" or "matching"'),
])
def test_balancing_refusals(change, message):
    call = dict(for_each_group_in="treat", allowing_for=COLUMNS)
    call.update(change)
    with pytest.raises(SimplydataError, match=message):
        sdata.table(r_table("job_training")).compare_balanced_groups_of("re78", **call)


def test_balancing_refuses_three_groups():
    with pytest.raises(SimplydataError, match="two groups at a time"):
        sdata.table(sdata.get_example("marks")).compare_balanced_groups_of("marks", for_each_group_in="class",
                                                                           allowing_for=["hours"])


# ---------------------------------------------------------------- S03: attributable fractions (R)
def test_attributable_fractions_are_epirs(needs_r, capsys):
    r = _flutd().compare_risks("flutd", for_each_group_in="food", against="other",
                               show="attributable fractions").as_pandas()
    assert list(r["measure"]) == ["attributable fraction among the exposed", "attributable fraction in the population"]
    # epiR's help: 75.05 % (32.91 to 90.72) and 54.20 % (32.38 to 74.91)
    assert r["estimate"][0] == pytest.approx(0.750470, abs=1e-6)
    assert r["estimate 95 % CI low"][0] == pytest.approx(0.329129, abs=1e-6)
    assert r["estimate"][1] == pytest.approx(0.542006, abs=1e-6)
    text = capsys.readouterr().out
    assert "Crude: not adjusted" in text and "cohort or a cross-sectional" in text


def test_a_protective_exposure_gets_the_preventable_fraction(needs_r, capsys):
    r = _flutd().compare_risks("flutd", for_each_group_in="food", against="dry",
                               show="attributable fractions").as_pandas()
    pf = r.loc[r["measure"] == "preventable fraction among the exposed", "estimate"].iloc[0]
    assert pf == pytest.approx(1 - (5 / 3354) / (13 / 2176), rel=1e-12)
    assert "preventable fraction" in capsys.readouterr().out


def test_attributable_fractions_refusals():
    t = sdata.table(sdata.get_example("clinic"))
    with pytest.raises(SimplydataError, match="crude fractions of two groups"):
        t.compare_risks("infected", for_each_group_in="ward", allowing_for="age_group",
                        show="attributable fractions")
    with pytest.raises(SimplydataError, match='show="attributable fractions"'):
        t.compare_risks("infected", for_each_group_in="ward", show="fractions")


# ---------------------------------------------------------------- S07: standardised rates (R)
def test_direct_standardisation_is_epitools_ageadjust_direct(needs_r, capsys):
    data = pd.read_csv(DATA / "down_syndrome.csv")
    r = sdata.table(data).rate_of("cases", time="births", for_each_group_in="birth_order", allowing_for="mother_age",
                                  standard_population="whole table", per=100000).as_pandas().set_index("group")
    # the epitools help: 92.30 (80.44 to 105.76) per 100,000 for the first born
    assert r.loc["1", "adjusted rate"] == pytest.approx(92.30453, abs=1e-5)
    assert r.loc["1", "adjusted rate 95 % CI low"] == pytest.approx(80.44175, abs=1e-5)
    assert r.loc["1", "crude rate"] == pytest.approx(412 / 731177 * 1e5, rel=1e-12)
    assert "Fay & Feuer" in capsys.readouterr().out


def test_direct_standardisation_with_a_standard_table(needs_r):
    t = sdata.table(sdata.get_example("deaths_by_age"))
    std = pd.DataFrame({"age_band": list(NATIONAL), "population": [100, 100, 100, 100, 100, 100]})
    r = t.rate_of("deaths", time="person_years", for_each_group_in="county", allowing_for="age_band",
                  standard_population=std).as_pandas().set_index("group")
    rates = sdata.get_example("deaths_by_age").query("county == 'Eastmere'")
    assert r.loc["Eastmere", "adjusted rate"] == pytest.approx((rates["deaths"] / rates["person_years"]).mean() * 1000,
                                                               rel=1e-9)  # equal weights: the plain average rate


def test_indirect_standardisation_is_observed_over_expected(needs_r, capsys):
    t = sdata.table(sdata.get_example("deaths_by_age"))
    r = t.compare_rates("deaths", time="person_years", for_each_group_in="county", allowing_for="age_band",
                        standard_rates=NATIONAL).as_pandas().set_index("group")
    df = sdata.get_example("deaths_by_age").query("county == 'Northvale'")
    expected = (df["person_years"] * df["age_band"].map(NATIONAL) / 1000).sum()
    assert r.loc["Northvale", "expected"] == pytest.approx(expected, rel=1e-12)
    assert r.loc["Northvale", "observed / expected"] == pytest.approx(df["deaths"].sum() / expected, rel=1e-12)
    found = _r("p <- stats::poisson.test(o, e); list(low = p$conf.int[1], high = p$conf.int[2], p = p$p.value)",
               o=float(df["deaths"].sum()), e=expected)
    assert r.loc["Northvale", "observed / expected 95 % CI low"] == pytest.approx(float(np.ravel(found["low"])[0]), rel=1e-9)
    assert r.loc["Northvale", "p-value"] == pytest.approx(float(np.ravel(found["p"])[0]), rel=1e-9)
    assert "SMR" in capsys.readouterr().out


@pytest.mark.parametrize("call, message", [
    (dict(allowing_for="age_band"), "go together"),
    (dict(standard_population="whole table"), "go together"),
    (dict(allowing_for="age_band", standard_population={"0-19": 1}), "has no value for"),
    (dict(allowing_for="age_band", standard_population="the world"), 'takes "whole table"'),
])
def test_direct_standardisation_refusals(call, message):
    with pytest.raises(SimplydataError, match=message):
        sdata.table(sdata.get_example("deaths_by_age")).rate_of("deaths", time="person_years",
                                                               for_each_group_in="county", **call)


def test_direct_standardisation_refuses_an_empty_band():
    df = sdata.get_example("deaths_by_age")
    df.loc[(df["county"] == "Eastmere") & (df["age_band"] == "80+"), ["deaths", "person_years"]] = 0
    with pytest.raises(SimplydataError, match="no \"person_years\" for 80\\+ in Eastmere"):
        sdata.table(df).rate_of("deaths", time="person_years", for_each_group_in="county", allowing_for="age_band",
                                standard_population="whole table")


def test_indirect_standardisation_refusals():
    t = sdata.table(sdata.get_example("deaths_by_age"))
    with pytest.raises(SimplydataError, match="no rate for"):
        t.compare_rates("deaths", time="person_years", allowing_for="age_band", standard_rates={"0-19": 1.0})
    with pytest.raises(SimplydataError, match="leave out against="):
        t.compare_rates("deaths", time="person_years", for_each_group_in="county", allowing_for="age_band",
                        standard_rates=NATIONAL, against="Eastmere")
    with pytest.raises(SimplydataError, match="one column of numbers"):
        t.compare_rates("deaths", time="person_years", allowing_for="age_band",
                        standard_rates=pd.DataFrame({"age_band": list(NATIONAL), "a": 1.0, "b": 2.0}))


# ---------------------------------------------------------------- X05: multiple imputation for other words (R)
def test_correlation_with_multiple_imputation_pools_with_miceadds(needs_r, capsys):
    t = sdata.table(sdata.get_example("school"))
    r = t.find_correlation_between("sleep", "marks", empty_cells="multiple imputation")
    plain = t.find_correlation_between("sleep", "marks")
    assert -1 < r < 1 and abs(r - plain) < 0.1
    text = capsys.readouterr().out
    assert "filled in 20 times" in text and "micombine.cor" in text and "Fisher's z" in text


def test_correlation_imputation_refusals():
    t = sdata.table(sdata.get_example("school"))
    with pytest.raises(SimplydataError, match="leave out show="):
        t.find_correlation_between("sleep", "marks", empty_cells="multiple imputation", allowing_for="hours")
    with pytest.raises(SimplydataError, match='empty_cells= takes "leave out"'):
        t.find_correlation_between("sleep", "marks", empty_cells="fill")


def test_correlation_imputation_without_empty_cells_is_the_ordinary_one(needs_r, capsys):
    t = sdata.table(sdata.get_example("marks"))
    assert t.find_correlation_between("hours", "marks", empty_cells="multiple imputation") == \
        pytest.approx(t.find_correlation_between("hours", "marks"))
    assert "no empty cells to fill in" in capsys.readouterr().out


def test_cox_model_with_multiple_imputation_pools_with_mice(needs_r, capsys):
    df = sdata.get_example("trial")
    df.loc[df.index[::6], "age"] = None
    r = sdata.table(df).explain_survival(time="days", event="died", using=["treatment", "age"],
                                         empty_cells="multiple imputation").as_pandas()
    assert list(r["term"]) == ["treatment: usual care vs new medicine", "age"]
    full = sdata.table(sdata.get_example("trial")).explain_survival(time="days", event="died",
                                                                    using=["treatment", "age"]).as_pandas()
    assert r["hazard ratio"][1] == pytest.approx(full["hazard ratio"][1], rel=0.05)
    text = capsys.readouterr().out
    assert "Nelson-Aalen" in text and "mice(...)" in text and "share" not in text.split("Method")[0]


def test_cox_imputation_refuses_other_models():
    with pytest.raises(SimplydataError, match="fills in a plain Cox model"):
        sdata.table(sdata.get_example("trial")).explain_survival(time="days", event="died", using=["age"],
                                                                 distribution="weibull",
                                                                 empty_cells="multiple imputation")


# ---------------------------------------------------------------- practice tables and names
@pytest.mark.parametrize("name, rows", [("job_training", 614), ("job_search", 899), ("drug_levels", 36),
                                        ("deaths_by_age", 24)])
def test_new_practice_tables(name, rows):
    assert len(sdata.get_example(name)) == rows


@pytest.mark.parametrize("name", ["bcg", "passive_smoking", "ability_tests", "sea_levels", "sampled_schools",
                                  "job_training", "drug_levels"])
def test_practice_tables_after_real_studies_are_made_up_by_their_script(name):
    """docs/make_practice_tables.py draws them with a fixed seed (DATA_LICENSES.md: the real data are not shipped)."""
    import importlib.util

    from simplydata.data import EXAMPLES

    script = Path(__file__).resolve().parents[1] / "docs" / "make_practice_tables.py"
    spec = importlib.util.spec_from_file_location("make_practice_tables", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    shipped = sdata.get_example(name)
    made = module.TABLES[name]()
    assert list(made.columns) == list(shipped.columns) and len(made) == len(shipped)
    pd.testing.assert_frame_equal(made.astype(str).replace("nan", ""), shipped.astype(str).replace("nan", ""),
                                  check_dtype=False)
    assert EXAMPLES[name][0].startswith("MADE-UP DATA") and "DATA_LICENSES.md" in EXAMPLES[name][0]


@pytest.mark.parametrize("typed", ["propensity", "matchit", "mediation", "smr", "ageadjust", "bioequivalence",
                                   "attributable_fraction"])
def test_other_names_point_to_the_new_options(typed, capsys):
    sdata.help(typed)
    assert "In simplydata" in capsys.readouterr().out


# ---------------------------------------------------------------- review fixes
def test_standardised_ratios_are_read_back_by_group_name(needs_r):
    """epiR sorts its strata as text (by the locale): every group must keep its own numbers."""
    df = sdata.get_example("deaths_by_age")
    names = {"Northvale": "2", "Eastmere": "10", "Southby": "bergen", "Westford": "Oslo"}
    df["county"] = df["county"].map(names)
    r = sdata.table(df).compare_rates("deaths", time="person_years", for_each_group_in="county",
                                      allowing_for="age_band", standard_rates=NATIONAL).as_pandas().set_index("group")
    for name in names.values():
        rows = df[df["county"] == name]
        expected = (rows["person_years"] * rows["age_band"].map(NATIONAL) / 1000).sum()
        assert r.loc[name, "observed"] == rows["deaths"].sum()
        assert r.loc[name, "expected"] == pytest.approx(expected, rel=1e-12)
    d = sdata.table(df).rate_of("deaths", time="person_years", for_each_group_in="county", allowing_for="age_band",
                                standard_population="whole table").as_pandas().set_index("group")
    for name in names.values():
        rows = df[df["county"] == name]
        assert d.loc[name, "crude rate"] == pytest.approx(rows["deaths"].sum() / rows["person_years"].sum() * 1000,
                                                          rel=1e-9)


def test_matching_with_fewer_rows_in_the_other_group_says_so(needs_r, capsys):
    t = sdata.table(r_table("job_training"))
    t.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=COLUMNS, test_method="matching",
                                 effect_for=0)
    assert 'no partner left ("1" has fewer rows)' in capsys.readouterr().out


def test_attributable_fractions_with_no_events_in_a_group_are_refused():
    rows = [{"g": "a", "e": "yes"}] * 10 + [{"g": "a", "e": "no"}] * 90 + [{"g": "b", "e": "no"}] * 100
    with pytest.raises(SimplydataError, match="no events in b"):
        sdata.table(pd.DataFrame(rows)).compare_risks("e", for_each_group_in="g", against="b",
                                                      show="attributable fractions")


def test_attributable_fractions_need_against():
    with pytest.raises(SimplydataError, match="needs against="):
        _flutd().compare_risks("flutd", for_each_group_in="food", show="attributable fractions")


def test_a_lower_effect_gives_the_interval_of_how_much_lower(needs_r, capsys):
    t = sdata.table(r_table("job_training"))
    t.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=COLUMNS, against=1)
    assert "lower" in capsys.readouterr().out.split("Effect for")[1].splitlines()[0]


def test_mediation_refuses_a_text_outcome_as_numbers():
    with pytest.raises(SimplydataError, match='outcome="yes or no"'):
        sdata.table(sdata.get_example("job_search")).explain("work1", using="treat", through="job_seek")


def test_crossover_period_order_follows_the_values():
    df = sdata.get_example("drug_levels")
    named = df.assign(period=df["period"].map({1: "early", 2: "late"}))
    r = sdata.table(named).compare_averages_of("auc", for_each_group_in="formulation", matched_by="subject",
                                               period="period").get_row(1)
    plain = _crossover("A").compare_averages_of("auc", for_each_group_in="formulation", matched_by="subject",
                                                period="period").get_row(1)
    assert r["estimate"] == pytest.approx(plain["estimate"], rel=1e-12)


def test_weighting_still_works_after_r_drc_is_attached(needs_r):
    """fit_dose_response attaches R drc, whose gaussian() masks stats::gaussian(); lm_weightit asks for it by name."""
    _r("invisible(1)", packages=("drc",))
    t = sdata.table(r_table("job_training"))
    r = t.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=COLUMNS)
    assert r.as_pandas()["estimate"][0] == pytest.approx(224.6763, abs=1e-3)
