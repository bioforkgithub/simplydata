"""S2: own_slope_for=, p_value_by="satterthwaite" and effects="for the whole population" (GEE), checked
against R.

R 4.6.2, lme4 2.1.0, lmerTest 3.2.1, geepack 1.3.13. FARMS is a small made-up table (15 farms of 12
rows, made with numpy's random numbers, seed 7); the same rows went to R as slopes.csv. The R call is
next to each value.
"""

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table


def _farms():
    rng = np.random.default_rng(7)
    rows = []
    for g in range(15):
        a, b = rng.normal(0, 3), rng.normal(0, 0.8)
        for i in range(12):
            x = round(float(rng.uniform(0, 10)), 1)
            grp = "yes" if rng.uniform() < 0.5 else "no"
            y = 20 + a + (2 + b) * x + (1.5 if grp == "yes" else 0) + rng.normal(0, 2)
            sick = "yes" if rng.uniform() < 1 / (1 + np.exp(-(-2 + 0.3 * x + a / 3))) else "no"
            rows.append({"farm": f"F{g + 1:02d}", "feed": x, "organic": grp, "growth": round(y, 1), "sick": sick,
                         "visit": i + 1})
    frame = pd.DataFrame(rows)
    frame["band"] = np.where(frame.visit <= 4, "a", np.where(frame.visit <= 8, "b", "c"))
    return frame


FARMS = _farms()


@pytest.fixture
def farms():
    return make_table(FARMS.copy())


def by_term(result):
    return {r["term"]: r for r in result.as_pandas().to_dict("records")}


def test_farms_table_is_the_one_sent_to_r():
    assert FARMS.shape == (180, 7)
    assert FARMS.growth[:3].tolist() == [38.1, 19.2, 28.4] and FARMS.feed[:3].tolist() == [7.8, 0.1, 3.0]


# ---------------------------------------------------------------- own_slope_for= (R lme4)
def test_own_slopes_match_lmer(farms, capsys, needs_r):
    # R: m <- lme4::lmer(growth ~ feed + organic + (1 + feed | farm), data = d, REML = TRUE)
    #    fixef(m); sqrt(diag(vcov(m))); as.data.frame(VarCorr(m))
    got = by_term(farms.explain("growth", using=["feed", "organic"], grouped_by="farm", own_slope_for="feed"))
    assert got["(intercept)"]["effect"] == pytest.approx(20.6735862366696, rel=1e-6)
    assert got["feed"]["effect"] == pytest.approx(1.80493702584345, rel=1e-6)
    assert got["organic (yes)"]["standard error"] == pytest.approx(0.294430956834481, rel=1e-5)
    assert got["feed"]["standard error"] == pytest.approx(0.273455220565582, rel=1e-5)
    out = capsys.readouterr().out
    assert "(1 + feed | farm)" in out and "own slope" in out
    assert 'Variance of the own slopes between groups: "feed" 1.08' in out  # vcov 1.07836408868318
    assert "Correlation of starting level and slope: 0.261." in out          # sdcor 0.260556888644997
    assert "starting levels between groups 18.1" in out                       # vcov 18.07991878413713


def test_own_slopes_for_yes_or_no_match_glmer(farms, capsys, needs_r):
    # R: lme4::glmer(sick ~ feed + (1 + feed | farm), family = binomial): fixef -2.13121181918898
    #    0.303966952456517; se 0.586856566053439 0.0722508861251644 (a singular fit: correlation -1)
    got = by_term(farms.explain("sick", using=["feed"], outcome="yes or no", grouped_by="farm", own_slope_for="feed"))
    assert got["feed"]["log odds ratio"] == pytest.approx(0.303966952456517, rel=1e-5)
    assert got["feed"]["standard error"] == pytest.approx(0.0722508861251644, rel=1e-4)
    out = capsys.readouterr().out
    assert "lme4::glmer(sick ~ feed + (1 + feed | farm)" in out and "cannot tell the slopes apart" in out


def test_own_slope_checks(farms):
    with pytest.raises(SimplydataError, match="in using= too"):
        farms.explain("growth", using=["organic"], grouped_by="farm", own_slope_for="feed")
    with pytest.raises(SimplydataError, match="holds groups"):
        farms.explain("growth", using=["feed", "organic"], grouped_by="farm", own_slope_for="organic")
    with pytest.raises(SimplydataError, match="goes with grouped_by="):
        farms.explain("growth", using=["feed"], own_slope_for="feed")


# ---------------------------------------------------------------- p_value_by="satterthwaite" (R lmerTest)
def test_satterthwaite_matches_lmertest(capsys, needs_r):
    # R: m <- lmerTest::lmer(marks ~ hours + breakfast + (1 | school), data = s); coef(summary(m));
    #    contest(m, L[i, ], confint = TRUE, joint = FALSE)
    school = make_table(sdata.get_example("school"))
    got = by_term(school.explain("marks", using=["hours", "breakfast"], grouped_by="school",
                                 p_value_by="satterthwaite"))
    assert got["(intercept)"]["degrees of freedom"] == pytest.approx(26.8318529454399, rel=1e-5)
    assert got["breakfast (yes)"]["degrees of freedom"] == pytest.approx(168.4550265552475, rel=1e-5)
    assert got["breakfast (yes)"]["p-value"] == pytest.approx(7.55914277966171e-03, rel=1e-5)
    assert got["breakfast (yes)"]["95 % CI low"] == pytest.approx(0.802718996244734, rel=1e-5)
    assert got["hours"]["95 % CI high"] == pytest.approx(3.23299558964559, rel=1e-6)
    assert got["hours"]["statistic name"] == "t"
    assert "Satterthwaite" in capsys.readouterr().out


def test_satterthwaite_with_own_slopes_and_a_whole_column_f_test(farms, needs_r):
    # R: lmerTest::lmer(growth ~ feed + organic + (1 + feed | farm)): df 14.8133371152508 13.9761609225204
    got = by_term(farms.explain("growth", using=["feed", "organic"], grouped_by="farm", own_slope_for="feed",
                                p_value_by="few groups"))
    assert got["feed"]["degrees of freedom"] == pytest.approx(13.9761609225204, rel=1e-4)
    assert got["feed"]["p-value"] == pytest.approx(1.19853794581959e-05, rel=1e-3)
    # R: anova(lmerTest::lmer(growth ~ feed + band + (1 | farm)), type = 2): band F 1.54278, DenDF 162.0055856437,
    #    Pr 0.21691
    got = by_term(farms.explain("growth", using=["feed", "band"], grouped_by="farm", p_value_by="satterthwaite"))
    band = got["band (whole column)"]
    assert band["statistic"] == pytest.approx(1.54278, rel=1e-5)
    assert band["p-value"] == pytest.approx(0.21691, abs=5e-6)
    assert band["degrees of freedom"] == 2


def test_p_value_by_checks(farms):
    with pytest.raises(SimplydataError, match='p_value_by= is "wald"'):
        farms.explain("growth", using=["feed"], grouped_by="farm", p_value_by="kenward")
    with pytest.raises(SimplydataError, match='is for outcome="numbers"'):
        farms.explain("sick", using=["feed"], outcome="yes or no", grouped_by="farm", p_value_by="satterthwaite")


# ---------------------------------------------------------------- effects="for the whole population" (GEE)
# R: geepack::geeglm(y ~ feed + organic, id = farm, data = d, corstr = cs, family = ...); coef(); sqrt(diag(vcov()))
@pytest.mark.parametrize("within, outcome, column, coef, se", [
    ("alike", "numbers", "growth", (19.8508712661295, 1.89201285733745, 2.12830054774922),
     (1.09069538506398, 0.254090569292608, 0.647056760385818)),
    ("alike", "yes or no", "sick", (-1.55870181244647, 0.214283516593158, 0.0885924931166883),
     (0.504419731489873, 0.0517931045452539, 0.331762773448095)),
    ("independent", "numbers", "growth", (20.2383891452732, 1.79027185004245, 2.40786181956193),
     (1.82719831910632, 0.235567559208768, 0.790202167200604)),
])
def test_gee_matches_geeglm(farms, within, outcome, column, coef, se):
    got = farms.explain(column, using=["feed", "organic"], outcome=outcome, grouped_by="farm",
                        effects="for the whole population", within_groups=within).as_pandas()
    estimates = got["effect"] if outcome == "numbers" else got["log odds ratio"]
    assert estimates[:3].tolist() == pytest.approx(coef, rel=2e-6)
    assert got["standard error"][:3].tolist() == pytest.approx(se, rel=2e-5)


def test_gee_prints_the_working_correlation(farms, capsys):
    # R: geeglm(..., corstr = "exchangeable"): alpha 0.819239942304716, scale 59.3092846255035
    farms.explain("growth", using=["feed", "organic"], grouped_by="farm", effects="for the whole population")
    out = capsys.readouterr().out
    assert "Working correlation between rows of a group: 0.819" in out and "Scale (variance) 59.3" in out
    assert 'corstr = "exchangeable"' in out and "only 15 groups" in out


def test_gee_in_time_order_runs_geepack(farms, capsys, needs_r):
    # R: geeglm(sick01 ~ feed + organic, id = farm, corstr = "ar1", family = binomial): coef -1.51744437888916
    #    0.211885867896645 0.0720243623834647; se 0.53408258759421 0.0503760445431337 0.317170673315832;
    #    alpha 0.450489327903139
    got = farms.explain("sick", using=["feed", "organic"], outcome="yes or no", grouped_by="farm",
                        effects="whole population", within_groups="in time order").as_pandas()
    assert got["log odds ratio"][:3].tolist() == pytest.approx(
        [-1.51744437888916, 0.211885867896645, 0.0720243623834647], rel=1e-9)
    assert got["standard error"][:3].tolist() == pytest.approx(
        [0.53408258759421, 0.0503760445431337, 0.317170673315832], rel=1e-9)
    assert "0.450" in capsys.readouterr().out


def test_gee_checks(farms):
    with pytest.raises(SimplydataError, match='goes with effects="for the whole population"'):
        farms.explain("growth", using=["feed"], grouped_by="farm", within_groups="independent")
    with pytest.raises(SimplydataError, match="not for GEE"):
        farms.explain("growth", using=["feed"], grouped_by="farm", effects="for the whole population",
                      own_slope_for="feed")
    with pytest.raises(SimplydataError, match='effects= is "for the average group"'):
        farms.explain("growth", using=["feed"], grouped_by="farm", effects="marginal")
    with pytest.raises(SimplydataError, match='within_groups= is "alike"'):
        farms.explain("growth", using=["feed"], grouped_by="farm", effects="for the whole population",
                      within_groups="unstructured")
