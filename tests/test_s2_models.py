"""S2: more outcome families and options for explain(), each checked against R.

R 4.6.2 (MASS 7.3); the R call is next to each value. rates and tries are small tables made here;
the same rows went to R as rates.csv and tries.csv.
"""

import math

import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table
from conftest import example_frame

RATES = pd.DataFrame({
    "area": ["north"] * 4 + ["south"] * 4 + ["east"] * 4,
    "years": [120, 95, 140, 80, 110, 130, 90, 150, 100, 85, 125, 105],
    "cases": [8, 5, 12, 4, 15, 22, 11, 25, 9, 6, 14, 10],
    "smokers": [0.2, 0.3, 0.25, 0.15, 0.4, 0.45, 0.35, 0.5, 0.3, 0.2, 0.35, 0.3],
})
TRIES = pd.DataFrame({"dose": [1, 2, 3, 4, 5, 6] * 2, "tries": [20] * 6 + [15] * 6,
                      "yes": [2, 4, 7, 10, 14, 16, 1, 4, 6, 8, 11, 13]})


def rows(result):
    frame = result.as_pandas()
    return {r["term"]: r for r in frame.to_dict("records")}


def check(got, expected, rel=1e-6):
    for key, value in expected.items():
        assert got[key] == pytest.approx(value, rel=rel), key


# ---------------------------------------------------------------- negative binomial
def test_negative_binomial_matches_glm_nb(capsys):
    got = rows(make_table(sdata.get_example("meadow")).explain("nettle", using=["grazed", "field"],
                                                           outcome="counts that vary a lot"))
    out = capsys.readouterr().out
    # R: m <- MASS::glm.nb(nettle ~ grazed + field, data = meadow); summary(m); m$theta  4.93725072911898
    check(got["(intercept)"], {"log rate ratio": 1.94313908744789, "standard error": 0.229712298401667}, rel=1e-5)
    check(got["grazed (yes)"], {"log rate ratio": -1.2904844591407, "standard error": 0.239059991858828,
                                "p-value": 6.73272265388694e-08}, rel=1e-5)
    check(got["field (River field)"], {"log rate ratio": 0.753591138646026, "standard error": 0.283948310127411,
                                       "p-value": 0.00795502000026502}, rel=1e-5)
    # R: drop1(m, test = "Chisq"): field LRT 7.10655006304397, p 0.0286307194337032 (theta held)
    check(got["field (whole column)"], {"statistic": 7.10655006304397, "p-value": 0.0286307194337032}, rel=1e-5)
    assert "MASS::glm.nb(nettle ~ grazed + field) (theta = 4.94" in out
    # R: deviance 36.2357526498111, null 77.0471910394427, AIC 165.908562845658
    assert "Residual deviance 36.2 on 26 df (with no columns: 77.0 on 29 df)" in out and "AIC 166, BIC" in out
    assert got["grazed (yes)"]["statistic name"] == "z"


def test_overdispersion_note_names_both_choices(capsys):
    school = example_frame("school").assign(days_absent=lambda d: d.days_absent * 3)
    make_table(school).explain("days_absent", using="hours", outcome="counts")
    out = capsys.readouterr().out
    assert 'outcome="counts that vary a lot" (negative binomial)' in out and "(quasi-Poisson)" in out


# ---------------------------------------------------------------- Gamma
def test_gamma_regression_matches_r(capsys):
    got = rows(make_table(sdata.get_example("trial")).explain("days", using=["treatment", "age"],
                                                          outcome="positive numbers"))
    out = capsys.readouterr().out
    # R: m <- glm(days ~ treatment + age, data = trial, family = Gamma(link = "log")); summary(m)
    # R glm() stops when the deviance changes by less than 1e-8 of itself; statsmodels goes on a little
    # further, so the two agree to about 1e-6 here.
    check(got["(intercept)"], {"log ratio of averages": 6.98038043732365, "standard error": 0.252718258242586},
          rel=1e-5)
    # a coefficient near 0: compared in absolute terms (2e-7 apart, about 2e-6 standard errors)
    assert got["treatment (usual care)"]["log ratio of averages"] == pytest.approx(-0.0091114672302262, abs=1e-6)
    check(got["treatment (usual care)"], {"standard error": 0.10519261282503, "p-value": 0.931124024281044},
          rel=1e-5)
    check(got["age"], {"log ratio of averages": -0.0132300564473025, "standard error": 0.00391591541428839},
          rel=1e-5)
    assert got["age"]["p-value"] == pytest.approx(0.000990430324657162, rel=1e-3)  # small p moves about t^2 times more
    assert got["age"]["statistic name"] == "t"
    # R: summary(m)$dispersion 0.331302127988121; deviance 57.3137815771215, null 60.7386322822247
    assert "dispersion 0.331" in out and "Residual deviance 57.3 on 117 df (with no columns: 60.7 on 119 df)" in out
    assert 'Gamma(link = "log")' in out and "multiplies the expected \"days\" by 0.987" in out


def test_positive_numbers_need_numbers_above_zero():
    data = pd.DataFrame({"y": [1.0, 2.0, 0.0, 3.0, 4.0], "x": [1, 2, 3, 4, 5]})
    with pytest.raises(SimplydataError, match="numbers above 0"):
        make_table(data).explain("y", using="x", outcome="positive numbers")


# ---------------------------------------------------------------- rates (time=)
def test_rates_with_time_match_r_offset(capsys):
    got = rows(make_table(RATES).explain("cases", using=["area", "smokers"], outcome="counts", time="years"))
    out = capsys.readouterr().out
    # R: m <- glm(cases ~ area + smokers, offset = log(years), data = rates, family = poisson)
    check(got["(intercept)"], {"log rate ratio": -2.99975586895387, "standard error": 0.510094186280636})
    check(got["area (north)"], {"log rate ratio": -0.202590375222932, "p-value": 0.448453447636275})
    check(got["smokers"], {"log rate ratio": 2.13499127776612, "standard error": 1.61321371851483})
    # R: drop1(m, test = "Chisq"): area LRT 0.945135700836481; AIC 59.9329053470574
    check(got["area (whole column)"], {"statistic": 0.945135700836481})
    assert "offset = log(years)" in out and "AIC 59.9, BIC" in out and 'per 1 of "years"' in out
    assert "the rate (count per time)" in out


def test_time_needs_counts_and_positive_times():
    with pytest.raises(SimplydataError, match="time= .* is for counts"):
        make_table(RATES).explain("cases", using="area", time="years")
    bad = RATES.assign(years=RATES.years.where(RATES.index != 2, 0))
    with pytest.raises(SimplydataError, match="times above 0"):
        make_table(bad).explain("cases", using="area", outcome="counts", time="years")


# ---------------------------------------------------------------- successes out of tries (out_of=)
def test_successes_out_of_tries_match_r_cbind(capsys):
    got = rows(make_table(TRIES).explain("yes", using="dose", outcome="yes or no", out_of="tries"))
    out = capsys.readouterr().out
    # R: m <- glm(cbind(yes, tries - yes) ~ dose, data = tries, family = binomial); summary(m); AIC(m)
    check(got["(intercept)"], {"log odds ratio": -2.84072811898695, "standard error": 0.431987557049358})
    check(got["dose"], {"log odds ratio": 0.743995997325895, "standard error": 0.109265474305808,
                        "odds ratio": math.exp(0.743995997325895)})
    assert "cbind(yes, tries - yes) ~ dose" in out and "AIC 40.7, BIC" in out  # R: 40.6696039348049
    assert "Residual deviance 1.25 on 10 df (with no columns: 63.6 on 11 df)" in out


def test_out_of_checks():
    with pytest.raises(SimplydataError, match='goes with outcome="yes or no"'):
        make_table(TRIES).explain("yes", using="dose", outcome="counts", out_of="tries")
    bad = TRIES.assign(yes=TRIES.yes.where(TRIES.index != 0, 25))
    with pytest.raises(SimplydataError, match="cannot be more than the number of tries"):
        make_table(bad).explain("yes", using="dose", outcome="yes or no", out_of="tries")


def test_negative_binomial_without_extra_variation_says_so():
    # R: MASS::glm.nb(days_absent ~ hours + school, data = s) warns "iteration limit reached": theta grows without
    #    limit (the counts vary no more than Poisson allows); statsmodels finds no theta at all
    with pytest.raises(SimplydataError, match="theta grows without limit"):
        make_table(sdata.get_example("school")).explain("days_absent", using=["hours", "school"],
                                                    outcome="counts that vary a lot")
