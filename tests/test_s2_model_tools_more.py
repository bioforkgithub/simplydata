"""S2: the model tools for grouped rows and for every outcome, and glmer with time=, out_of= and link=.

R 4.6.2, lme4 2.1.0, emmeans 2.0.4, MASS, nnet, betareg, pscl, lmtest. s <- read.csv("school.csv")
(sdata.example("school")); m, tr, g: sdata.example("meadow"), ("trial"), ("growth"); z: ZEROS below.
The R call is next to each value.
"""

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table

from test_s2_more_outcomes import ZEROS, graded_school


@pytest.fixture
def school():
    return make_table(sdata.example("school"))


def by_term(result, key="term"):
    frame = result.as_pandas()
    return {(r[key] if isinstance(key, str) else tuple(r[k] for k in key)): r for r in frame.to_dict("records")}


def school2():
    """The school table with a made-up time enrolled and a number right out of a number of tries."""
    s = sdata.example("school")
    i = np.arange(len(s))
    s["enrolled"] = 150 + (i * 37) % 60
    s["tries"] = 5 + i % 4
    s["right"] = np.minimum(s.tries, np.round(s.marks / 100 * s.tries)).astype(int)
    return s


# ---------------------------------------------------------------- check_model(grouped_by=)
def test_check_model_for_a_mixed_model_matches_lme4(school, capsys):
    # R: l <- lmer(marks ~ hours + breakfast + (1 | school), data = s)
    page = school.check_model("marks", using=["hours", "breakfast"], grouped_by="school")
    n = page._check_numbers
    # resid(l, scaled = TRUE)[1:3]
    assert n["scaled"][:3] == pytest.approx([-0.388112388273080, 0.715679939203338, 1.895614082262317], rel=1e-5)
    # q <- qqnorm(ranef(l)$school[, 1]); sort(q$x)[1:3]; sort(q$y)[1:3]
    assert n["group_qq"]["theoretical"][:3] == pytest.approx([-1.731664396122245, -1.150349380376008,
                                                              -0.812217801499913], rel=1e-12)
    assert n["group_qq"]["ordered"][:3] == pytest.approx([-10.41647917670644, -5.95326822855641, -2.14807521873210],
                                                         rel=1e-5)
    # qqline: diff(quantile(r, c(.25, .75))) / diff(qnorm(c(.25, .75)))
    assert n["group_qq"]["slope"] == pytest.approx(4.14576280260444, rel=1e-5)
    out = capsys.readouterr().out
    assert "in 4 pictures" in out and "qqnorm(ranef(m)$school[, 1])" in out


def test_check_model_for_a_glmm_matches_glmer(school, capsys, needs_r, tmp_path):
    # R: gm <- glmer(y ~ hours + breakfast + (1 | school), family = binomial)
    page = school.check_model("passed", using=["hours", "breakfast"], outcome="yes or no", grouped_by="school")
    n = page._check_numbers
    assert n["residual"][:3] == pytest.approx([-0.226589713182266, -0.215634882955150, 2.912815226306792],
                                              rel=1e-5)  # resid(gm, type = "pearson")
    assert n["fitted"][:3] == pytest.approx([0.0488355399668663, 0.0444323685779375, 0.1054352666215893], rel=1e-5)
    assert n["ranef"][:3] == pytest.approx([-1.724742366528416, -0.106089685179955, -2.544587666260495], rel=1e-4)
    assert "in 3 pictures" in capsys.readouterr().out
    page.save(str(tmp_path / "glmm.png"))


def test_check_model_for_other_glms_matches_plot_glm(capsys):
    # R: n1 <- MASS::glm.nb(nettle ~ grazed + field, m); cooks.distance(n1)[1:3]; rstandard(n1, type = "pearson")
    n = make_table(sdata.example("meadow")).check_model("nettle", using=["grazed", "field"],
                                                        outcome="counts that vary a lot")._check_numbers
    assert n["cooks"][:3] == pytest.approx([7.36467749086892e-05, 9.90928961622743e-03, 7.36467749086891e-05], rel=1e-4)
    assert n["pearson"][:2] == pytest.approx([0.0512453396565338, -0.5944273319135019], rel=1e-5)
    # R: q1 <- glm(days_absent ~ hours + breakfast, quasipoisson); rstandard(q1, type = "deviance")[1:2]
    n = make_table(sdata.example("school")).check_model("days_absent", using=["hours", "breakfast"],
                                                        outcome="counts (overdispersed)")._check_numbers
    assert n["standardised"][:2] == pytest.approx([-0.807931920708964, -0.329276595711568], rel=1e-6)
    assert n["cooks"][:2] == pytest.approx([3.04208995264717e-03, 3.86988725560222e-04], rel=1e-6)
    # R: d1 <- glm(days ~ treatment + age, Gamma(link = "log")); R glm() stops at epsilon = 1e-8, so 1e-3
    n = make_table(sdata.example("trial")).check_model("days", using=["treatment", "age"],
                                                       outcome="positive numbers")._check_numbers
    assert n["cooks"][:2] == pytest.approx([2.17241039500616e-05, 6.53606091488464e-03], rel=1e-3)
    assert n["pearson"][:2] == pytest.approx([-0.0467223121931202, 1.0688425948755622], rel=1e-3)


# ---------------------------------------------------------------- show_rows_that_pull(grouped_by=)
def test_groups_that_pull_match_lme4_influence(school, capsys, needs_r):
    # R: cooks.distance(influence(l, groups = "school")): School D 0.16073893087278512 is the largest
    school.show_rows_that_pull("marks", using=["hours", "breakfast"], grouped_by="school")
    out = capsys.readouterr().out
    assert "0 of 12 groups" in out and "the largest: School D, 0.161" in out
    model, _ = school._one_model("x", "marks", ["hours", "breakfast"], "numbers", "school")
    from simplydata.table.models_r import group_influence

    got = group_influence(model)
    assert list(got["cooks"][:3]) == pytest.approx([0.04572338909560377, 0.04627140571750372, 0.10979353520767073],
                                                   rel=1e-4)
    # R: cooks.distance(influence(gm, groups = "school")) for the glmer: School C 0.11019925496131416
    school.show_rows_that_pull("passed", using=["hours", "breakfast"], outcome="yes or no", grouped_by="school")
    assert "the largest: School C, 0.110" in capsys.readouterr().out


# ---------------------------------------------------------------- compare_models(grouped_by=, other outcomes)
def test_compare_mixed_models_refits_by_maximum_likelihood(school, capsys):
    # R: anova(lmer(marks ~ hours + (1 | school)), lmer(marks ~ hours + breakfast + (1 | school))) (refits with ML):
    #    Chisq 7.26046253050367, Pr 0.0070489; AIC 1243.65176234863 1238.39129981813; BIC 1256.42358975219 1254.35608407258
    got = school.compare_models("marks", using=["hours"], against=["hours", "breakfast"], grouped_by="school").as_pandas()
    assert got["AIC"][:2].tolist() == pytest.approx([1243.65176234863, 1238.39129981813], rel=1e-9)
    assert got["BIC"][:2].tolist() == pytest.approx([1256.42358975219, 1254.35608407258], rel=1e-9)
    assert got["statistic"][2] == pytest.approx(7.26046253050367, rel=1e-7)
    assert got["p-value"][2] == pytest.approx(0.0070489, rel=1e-4)
    assert "maximum likelihood" in capsys.readouterr().out


def test_compare_glmms(school, needs_r):
    # R: anova(glmer(y ~ hours + (1 | school), binomial), gm): Chisq 1.36989179153494, Pr 0.241830476282927;
    #    AIC 183.438326768241 184.068434976706
    got = school.compare_models("passed", using=["hours"], against=["hours", "breakfast"], outcome="yes or no",
                                grouped_by="school").as_pandas()
    assert got["statistic"][2] == pytest.approx(1.36989179153494, rel=1e-5)
    assert got["p-value"][2] == pytest.approx(0.241830476282927, rel=1e-5)
    assert got["AIC"][:2].tolist() == pytest.approx([183.438326768241, 184.068434976706], rel=1e-7)


def test_compare_models_for_other_outcomes(school, capsys, needs_r):
    # R: anova(glm(days_absent ~ hours, quasipoisson), glm(days_absent ~ hours + breakfast, quasipoisson), test = "F")
    got = school.compare_models("days_absent", using=["hours"], against=["hours", "breakfast"],
                                outcome="counts (overdispersed)").as_pandas()
    assert got["statistic"][2] == pytest.approx(0.563754389528979, rel=1e-6)
    assert got["p-value"][2] == pytest.approx(0.453748519762509, rel=1e-6)
    assert "no AIC or BIC" in capsys.readouterr().out
    # R: anova(MASS::glm.nb(nettle ~ grazed, m), MASS::glm.nb(nettle ~ grazed + field, m)): LR stat. 5.76721998734973
    got = make_table(sdata.example("meadow")).compare_models("nettle", using=["grazed"], against=["grazed", "field"],
                                                             outcome="counts that vary a lot").as_pandas()
    assert got["statistic"][2] == pytest.approx(5.76721998734973, rel=1e-5)
    assert got["p-value"][2] == pytest.approx(0.0559324820312497, rel=1e-5)
    assert got["AIC"][:2].tolist() == pytest.approx([167.675782833008, 165.908562845658], rel=1e-7)
    # R: anova(glm(days ~ age, Gamma("log"), tr), glm(days ~ treatment + age, ...), test = "F"); AIC()
    got = make_table(sdata.example("trial")).compare_models("days", using=["age"], against=["treatment", "age"],
                                                            outcome="positive numbers").as_pandas()
    assert got["statistic"][2] == pytest.approx(0.00749887187355431, rel=1e-4)
    assert got["p-value"][2] == pytest.approx(0.931140649728849, rel=1e-5)
    assert got["AIC"][:2].tolist() == pytest.approx([1686.48180896534, 1688.47620194811], rel=1e-8)
    assert got["BIC"][:2].tolist() == pytest.approx([1694.84428419368, 1699.62616891924], rel=1e-8)
    # R: anova(MASS::polr(grade ~ hours), MASS::polr(grade ~ hours + breakfast)): LR stat. 3.16073851136383
    #    (polr stops a little short of the optimum that statsmodels reaches, so 1e-4)
    got = make_table(graded_school()).compare_models("grade", using=["hours"], against=["hours", "breakfast"],
                                                     outcome="ordered groups",
                                                     in_order=["low", "middle", "high"]).as_pandas()
    assert got["statistic"][2] == pytest.approx(3.16073851136383, rel=1e-4)
    assert got["AIC"][:2].tolist() == pytest.approx([301.641835744638, 300.481097233274], rel=1e-6)
    # R: anova(nnet::multinom(field ~ clover), nnet::multinom(field ~ clover + grazed)): 0.484643081133576, df 2
    got = make_table(sdata.example("meadow")).compare_models("field", using=["clover"], against=["clover", "grazed"],
                                                             outcome="groups").as_pandas()
    assert got["statistic"][2] == pytest.approx(0.484643081133576, rel=1e-5)
    assert got["degrees of freedom"][2] == 2
    assert got["p-value"][2] == pytest.approx(0.784803790722016, rel=1e-5)
    # R: lmtest::lrtest(betareg(share ~ year, g), betareg(share ~ year + country, g)): 214.58739324085; AIC, BIC
    growth = sdata.example("growth").assign(share=lambda d: d.forest / 100)
    got = make_table(growth).compare_models("share", using=["year"], against=["year", "country"],
                                            outcome="shares").as_pandas()
    assert got["statistic"][2] == pytest.approx(214.58739324085, rel=1e-7)
    assert got["BIC"][:2].tolist() == pytest.approx([-23.7834149775786, -226.5170770626847], rel=1e-8)
    # R: lrtest(zeroinfl(count ~ depth | depth, z), zeroinfl(count ~ depth + site | depth + site, z)): df 2
    got = make_table(ZEROS).compare_models("count", using=["depth"], against=["depth", "site"],
                                           outcome="counts with many zeros").as_pandas()
    assert got["statistic"][2] == pytest.approx(5.89984666933995, rel=1e-5)
    assert got["p-value"][2] == pytest.approx(0.0523437187430815, rel=1e-5)
    assert got["AIC"][:2].tolist() == pytest.approx([188.564084045263, 186.664237375923], rel=1e-7)


# ---------------------------------------------------------------- model_averages_of for other outcomes
def test_model_averages_for_counts_that_vary_a_lot_and_positive_numbers(needs_r):
    # R: emmeans(MASS::glm.nb(nettle ~ grazed + field, m), ~ field, type = "response"); pairs() (Tukey)
    got = by_term(make_table(sdata.example("meadow")).model_averages_of(
        "nettle", for_each="field", using=["grazed", "field"], outcome="counts that vary a lot"))
    assert got["River field"]["model average"] == pytest.approx(7.77946832000096, rel=1e-5)
    assert got["North field"]["standard error"] == pytest.approx(0.806951269786026, rel=1e-5)
    pair = got["North field / River field"]
    assert pair["rate ratio"] == pytest.approx(0.470673261200484, rel=1e-5)
    assert pair["p-value (Tukey)"] == pytest.approx(0.0217, abs=5e-5)
    # R: emmeans(glm(days ~ treatment + age, Gamma(link = "log"), tr), ~ treatment, type = "response")
    got = by_term(make_table(sdata.example("trial")).model_averages_of(
        "days", for_each="treatment", using=["treatment", "age"], outcome="positive numbers"))
    assert got["new medicine"]["model average"] == pytest.approx(471.711901757791, rel=1e-4)
    assert got["new medicine / usual care"]["ratio of averages"] == pytest.approx(1.00915310300603, rel=1e-4)
    assert got["new medicine / usual care"]["degrees of freedom"] == 117
    # R: emmeans(glm(days_absent ~ hours + breakfast, quasipoisson), ~ breakfast, type = "response")
    got = by_term(make_table(sdata.example("school")).model_averages_of(
        "days_absent", for_each="breakfast", using=["hours"], outcome="counts (overdispersed)"))
    assert got["no / yes"]["95 % CI high"] == pytest.approx(1.27067667533494, rel=1e-6)
    assert got["no / yes"]["p-value (Tukey)"] == pytest.approx(0.4515, abs=5e-5)


def test_model_averages_for_shares_and_many_zeros(needs_r):
    # R: emmeans(betareg::betareg(share ~ year + country, g), ~ country, type = "response"); pairs()
    growth = sdata.example("growth").assign(share=lambda d: d.forest / 100)
    got = by_term(make_table(growth).model_averages_of("share", for_each="country", using=["year", "country"],
                                                       outcome="shares"))
    assert got["Applia"]["model average"] == pytest.approx(0.535206548322908, rel=1e-6)
    assert got["Cherria - Dateland"]["difference"] == pytest.approx(0.468554561127672, rel=1e-6)
    # R: emmeans(pscl::zeroinfl(count ~ depth + site | depth + site, z), ~ site); pairs()
    got = by_term(make_table(ZEROS).model_averages_of("count", for_each="site", using=["depth", "site"],
                                                      outcome="counts with many zeros"))
    assert got["shore"]["model average"] == pytest.approx(1.814915017371868, rel=1e-5)
    assert got["deep - shore"]["difference"] == pytest.approx(-0.967983527321306, rel=1e-5)
    assert got["deep - shore"]["p-value (Tukey)"] == pytest.approx(0.0319, abs=5e-5)


def test_model_averages_for_ordered_groups_and_groups_are_chances(capsys, needs_r):
    # R: emmeans(MASS::polr(grade ~ hours + breakfast, Hess = TRUE), ~ breakfast | grade, mode = "prob"); pairs()
    got = by_term(make_table(graded_school()).model_averages_of(
        "grade", for_each="breakfast", using=["hours", "breakfast"], outcome="ordered groups",
        in_order=["low", "middle", "high"]), key=("term", "grade group"))
    assert got[("no", "low")]["model chance"] == pytest.approx(0.164241312668601, rel=1e-4)
    assert got[("yes", "high")]["95 % CI high"] == pytest.approx(0.384045508990566, rel=1e-4)
    assert got[("no - yes", "high")]["difference in chance"] == pytest.approx(-0.1031396876882832, rel=1e-4)
    out = capsys.readouterr().out
    assert 'mode = "prob"' in out and 'within each "grade" group' in out
    # R: emmeans(nnet::multinom(field ~ clover + grazed), ~ grazed | field, mode = "prob"): df 6
    got = by_term(make_table(sdata.example("meadow")).model_averages_of(
        "field", for_each="grazed", using=["clover", "grazed"], outcome="groups"), key=("term", "field group"))
    assert got[("no", "North field")]["model chance"] == pytest.approx(0.348158013128585, rel=1e-4)
    assert got[("no - yes", "South field")]["p-value (Tukey)"] == pytest.approx(0.5382, abs=5e-4)


# ---------------------------------------------------------------- glmer with time=, out_of=, link=
def test_glmer_with_time_out_of_and_link(needs_r):
    s = make_table(school2())
    # R: glmer(days_absent ~ hours + offset(log(enrolled)) + (1 | school), family = poisson)
    got = by_term(s.explain("days_absent", using=["hours"], outcome="counts", time="enrolled", grouped_by="school"))
    assert got["hours"]["log rate ratio"] == pytest.approx(-0.146494893178562, rel=1e-4)
    assert got["hours"]["standard error"] == pytest.approx(0.0200149640245626, rel=1e-4)
    # R: glmer(cbind(right, tries - right) ~ hours + (1 | school), family = binomial)
    got = by_term(s.explain("right", using=["hours"], outcome="yes or no", out_of="tries", grouped_by="school"))
    assert got["hours"]["log odds ratio"] == pytest.approx(0.107757537252535, rel=1e-4)
    assert got["(intercept)"]["standard error"] == pytest.approx(0.1398259726919389, rel=1e-4)
    # R: glmer(y ~ hours + breakfast + (1 | school), family = binomial(link = "probit"))
    got = by_term(s.explain("passed", using=["hours", "breakfast"], outcome="yes or no", link="probit",
                            grouped_by="school"))
    assert got["breakfast (yes)"]["effect (probit scale)"] == pytest.approx(0.306483958285557, rel=1e-4)
    assert got["hours"]["standard error"] == pytest.approx(0.0650073290575004, rel=1e-4)
    # R: glmer(days_absent ~ hours + offset(log(enrolled)) + (1 + hours | school), family = poisson)
    got = by_term(s.explain("days_absent", using=["hours"], outcome="counts", time="enrolled", grouped_by="school",
                            own_slope_for="hours"))
    assert got["hours"]["log rate ratio"] == pytest.approx(-0.147979181853003, rel=1e-3)


def test_friendly_errors_for_combinations_without_a_package(school):
    s = make_table(school2())
    with pytest.raises(SimplydataError, match="geepack has no such link"):
        s.explain("days_absent", using=["hours"], outcome="counts", link="sqrt", grouped_by="school",
                  effects="for the whole population")
    with pytest.raises(SimplydataError, match="satterthwaite"):
        s.explain("days_absent", using=["hours"], outcome="counts", time="enrolled", grouped_by="school",
                  p_value_by="satterthwaite")
    with pytest.raises(SimplydataError, match="outcome"):
        school.check_model("grade", using=["hours"], outcome="shares")
    with pytest.raises(SimplydataError, match="in_order="):
        school.compare_models("marks", using=["hours"], against=["hours", "sleep"], in_order=["a"])


# ---------------------------------------------------------------- add_predicted_column(interval=, for_new_rows=)
def test_prediction_intervals_match_predict(school, capsys):
    # R: l <- lm(marks ~ hours + breakfast, s); predict(l, interval = "confidence")[1:2, ]
    school.add_predicted_column("marks", using=["hours", "breakfast"], interval=95)
    got = school.as_pandas()
    assert got["predicted marks 95 % CI low"][:2].tolist() == pytest.approx([42.3066608832910, 43.3235488908063], rel=1e-10)
    assert got["predicted marks 95 % CI high"][:2].tolist() == pytest.approx([46.595751594717, 46.929865113441], rel=1e-10)
    school.undo()
    # R: predict(l, interval = "prediction", level = 0.9)[1:2, ]
    school.add_predicted_column("marks", using=["hours", "breakfast"], interval=90, for_new_rows=True)
    got = school.as_pandas()
    assert got["predicted marks 90 % prediction low"][:2].tolist() == pytest.approx([30.0367782261514, 30.7451351510011], rel=1e-10)
    assert got["predicted marks 90 % prediction high"][:2].tolist() == pytest.approx([58.8656342518566, 59.5082788532462], rel=1e-10)
    assert "90 % prediction interval" in capsys.readouterr().out
    school.undo()
    # R: g <- glm(y ~ hours + breakfast, binomial); p <- predict(g, se.fit = TRUE); plogis(p$fit +- qnorm(0.975) * p$se.fit) (R glm stops at epsilon 1e-8)
    school.add_predicted_column("passed", using=["hours", "breakfast"], outcome="yes or no", interval=95)
    got = school.as_pandas()
    assert got["predicted passed 95 % CI low"][:2].tolist() == pytest.approx([0.184428388984262, 0.192292479315084], rel=1e-6)
    assert got["predicted passed 95 % CI high"][:2].tolist() == pytest.approx([0.421326728708436, 0.388231216653463], rel=1e-6)


def test_prediction_interval_checks(school):
    with pytest.raises(SimplydataError, match="outcome=\"numbers\""):
        school.add_predicted_column("passed", using=["hours"], outcome="yes or no", for_new_rows=True)
    with pytest.raises(SimplydataError, match="grouped_by="):
        school.add_predicted_column("marks", using=["hours"], grouped_by="school", interval=95)
    with pytest.raises(SimplydataError, match="percent"):
        school.add_predicted_column("marks", using=["hours"], interval=150)


# ---------------------------------------------------------------- explain(robust_errors=True)
def test_robust_errors_for_least_squares_match_sandwich(school, capsys):
    # R: l <- lm(marks ~ hours + breakfast, s); v <- sandwich::vcovHC(l, type = "HC3"); lmtest::coeftest(l, v); coefci()
    got = by_term(school.explain("marks", using=["hours", "breakfast"], robust_errors=True))
    assert got["hours"]["standard error"] == pytest.approx(0.2643265988481, rel=1e-9)
    assert got["breakfast (yes)"]["p-value"] == pytest.approx(0.019341, rel=1e-4)
    assert got["breakfast (yes)"]["95 % CI low"] == pytest.approx(0.52623524050107, rel=1e-9)
    out = capsys.readouterr().out
    assert "Wald F with robust errors = 57.8" in out  # lmtest::waldtest(l, vcov = v): F 57.78372
    # R: l2 <- lm(marks ~ hours + school, s); car::Anova(l2, vcov. = vcovHC(l2, type = "HC3")): school F 9.30990
    got = by_term(school.explain("marks", using=["hours", "school"], robust_errors=True))
    assert got["school (whole column)"]["statistic"] == pytest.approx(9.30990, rel=1e-5)
    assert got["school (whole column)"]["p-value"] == pytest.approx(6.2737e-13, rel=1e-4)


def test_robust_errors_for_glms_match_sandwich(school, needs_r):
    # R: g <- glm(y ~ hours + breakfast, binomial); lmtest::coeftest(g, vcov. = sandwich::vcovHC(g, type = "HC3"))
    got = by_term(school.explain("passed", using=["hours", "breakfast"], outcome="yes or no", robust_errors=True))
    assert got["hours"]["standard error"] == pytest.approx(0.09450506237416, rel=1e-6)
    assert got["breakfast (yes)"]["p-value"] == pytest.approx(0.25542, rel=1e-4)
    assert got["(intercept)"]["95 % CI low"] == pytest.approx(np.exp(-4.244554061363768), rel=1e-6)
    # R: ga <- glm(days ~ treatment + age, Gamma(link = "log"), tr); coeftest(ga, vcov. = vcovHC(ga, type = "HC3")): z
    got = by_term(make_table(sdata.example("trial")).explain("days", using=["treatment", "age"],
                                                            outcome="positive numbers", robust_errors=True))
    assert got["age"]["standard error"] == pytest.approx(0.003625833265235, rel=1e-4)
    assert got["treatment (usual care)"]["p-value"] == pytest.approx(0.93169233, rel=1e-4)
    assert got["age"]["statistic name"] == "z"


def test_robust_checks(school):
    with pytest.raises(SimplydataError, match="GEE"):
        school.explain("marks", using=["hours"], grouped_by="school", robust_errors=True)
    with pytest.raises(SimplydataError, match="True or False"):
        school.explain("marks", using=["hours"], robust_errors="yes")


def test_old_name_robust_still_works_with_a_note(school, capsys):
    new = by_term(school.explain("marks", using=["hours", "breakfast"], robust_errors=True))
    capsys.readouterr()
    old = by_term(school.explain("marks", using=["hours", "breakfast"], robust=True))
    out = capsys.readouterr().out
    assert 'Note: "robust=" is now called "robust_errors=".' in out
    assert old["hours"]["standard error"] == new["hours"]["standard error"]


# ---------------------------------------------------------------- grouped_by=[outer, inner] (groups inside groups)
def school3():
    """The school table with a made-up class (red, blue, green) inside each school."""
    s = sdata.example("school")
    i = np.arange(len(s))
    s["class"] = np.where((i * 7) % 3 == 0, "red", np.where((i * 7) % 3 == 1, "blue", "green"))
    return s


def test_groups_inside_groups_match_lmer(capsys):
    # R: m <- lmer(marks ~ hours + breakfast + (1 | school/class), data = s3); fixef(m); sqrt(diag(vcov(m)));
    #    VarCorr(m): class:school 1.95399695536127, school 29.57986256345465, Residual 45.40780385987338
    got = by_term(make_table(school3()).explain("marks", using=["hours", "breakfast"], grouped_by=["school", "class"]))
    assert got["hours"]["effect"] == pytest.approx(2.78907088839001, rel=1e-6)
    assert got["breakfast (yes)"]["standard error"] == pytest.approx(1.100876180289312, rel=1e-5)
    assert got["(intercept)"]["standard error"] == pytest.approx(2.098714858344615, rel=1e-5)
    out = capsys.readouterr().out
    assert "(1 | school/class)" in out and "Variance between them 29.6" in out and "inside them 1.95" in out


def test_groups_inside_groups_for_yes_or_no_match_glmer(capsys, needs_r):
    # R: glmer(y ~ hours + (1 | school/class), family = binomial, data = s3): VarCorr class:school 0.500482788159272
    got = by_term(make_table(school3()).explain("passed", using=["hours"], outcome="yes or no",
                                                grouped_by=["school", "class"]))
    assert got["hours"]["log odds ratio"] == pytest.approx(0.688748051378485, rel=1e-4)
    assert got["hours"]["standard error"] == pytest.approx(0.125779280036650, rel=1e-4)
    assert "inside them 0.500" in capsys.readouterr().out


def test_groups_inside_groups_checks():
    table = make_table(school3())
    with pytest.raises(SimplydataError, match="outer one first"):
        table.explain("marks", using=["hours"], grouped_by=["school", "class", "pupil"])
    with pytest.raises(SimplydataError, match="plain mixed model"):
        table.explain("marks", using=["hours"], grouped_by=["school", "class"], own_slope_for="hours")


# ---------------------------------------------------------------- groups inside groups in the model tools
def test_model_averages_with_groups_inside_groups_match_emmeans(capsys, needs_r):
    got = make_table(school3()).model_averages_of("marks", for_each="breakfast", using=["hours", "breakfast"],
                                                  grouped_by=["school", "class"]).as_pandas()
    # R: m <- lmer(marks ~ hours + breakfast + (1 | school/class), data = s3); e <- emmeans(m, ~ breakfast)
    #    summary(e): emmean 46.6885080618374 49.4717128346135, SE 1.81102322437145 1.71286609064128,
    #    df 15.1641161447397 12.244422344008 (Kenward-Roger)
    #    summary(pairs(e), infer = c(TRUE, TRUE)): -2.78320477277612, SE 1.11589495432077, df 168.377804417041,
    #    p 0.0135907075236144
    assert got["model average"][:2].tolist() == pytest.approx([46.6885080618374, 49.4717128346135], rel=1e-5)
    assert got["standard error"][:2].tolist() == pytest.approx([1.81102322437145, 1.71286609064128], rel=1e-4)
    assert got["degrees of freedom"][:2].tolist() == pytest.approx([15.1641161447397, 12.244422344008], rel=1e-3)
    assert got["difference"][2] == pytest.approx(-2.78320477277612, rel=1e-5)
    assert got["p-value (Tukey)"][2] == pytest.approx(0.0135907075236144, rel=1e-3)
    assert "(1 | school/class)" in capsys.readouterr().out


def test_model_averages_yes_or_no_with_groups_inside_groups(needs_r):
    got = make_table(school3()).model_averages_of("passed", for_each="breakfast", using=["hours", "breakfast"],
                                                  outcome="yes or no", grouped_by=["school", "class"]).as_pandas()
    # R: g1 <- glmer(y ~ hours + breakfast + (1 | school/class), family = binomial, data = s3)
    #    emmeans(g1, ~ breakfast, type = "response"): prob 0.305062172718965 0.422721124614989;
    #    pairs(): odds ratio 0.599479202784986, p 0.261728255614999
    assert got["model average"][:2].tolist() == pytest.approx([0.305062172718965, 0.422721124614989], rel=1e-4)
    assert got["odds ratio"][2] == pytest.approx(0.599479202784986, rel=1e-4)
    assert got["p-value (Tukey)"][2] == pytest.approx(0.261728255614999, rel=1e-3)


def test_compare_models_with_groups_inside_groups_match_anova(capsys):
    got = make_table(school3()).compare_models("marks", using=["hours"], against=["hours", "breakfast"],
                                               grouped_by=["school", "class"]).as_pandas()
    # R: m0 <- lmer(marks ~ hours + (1 | school/class)); m1 <- lmer(marks ~ hours + breakfast + (1 | school/class))
    #    anova(m0, m1) (refitted with ML): AIC 1243.99171775392 1240.02079421887; BIC 1259.95650200837
    #    1259.17853532421; Chisq 5.97092353505059, Pr 0.0145436619568889
    assert got["AIC"][:2].tolist() == pytest.approx([1243.99171775392, 1240.02079421887], rel=1e-9)
    assert got["BIC"][:2].tolist() == pytest.approx([1259.95650200837, 1259.17853532421], rel=1e-9)
    assert got["statistic"][2] == pytest.approx(5.97092353505059, rel=1e-6)
    assert got["p-value"][2] == pytest.approx(0.0145436619568889, rel=1e-6)
    assert 'in "class" groups inside "school" groups' in capsys.readouterr().out


def test_compare_models_yes_or_no_with_groups_inside_groups(needs_r):
    got = make_table(school3()).compare_models("passed", using=["hours"], against=["hours", "breakfast"],
                                               outcome="yes or no", grouped_by=["school", "class"]).as_pandas()
    # R: anova(g0, g1) for glmer(... + (1 | school/class), family = binomial): AIC 184.50503185845
    #    185.227145069215; Chisq 1.27788678923488, Pr 0.258292321103151
    assert got["AIC"][:2].tolist() == pytest.approx([184.50503185845, 185.227145069215], rel=1e-6)
    assert got["statistic"][2] == pytest.approx(1.27788678923488, rel=1e-4)


def test_check_model_with_groups_inside_groups_shows_both_levels(capsys):
    page = make_table(school3()).check_model("marks", using=["hours", "breakfast"], grouped_by=["school", "class"])
    numbers = page._check_numbers
    # R: ranef(m)$school[, 1]: School A -5.80439586418727, School B 0.607824236738937;
    #    ranef(m)$`class:school`: blue:School A 0.568054116114745, blue:School B -0.2456833465033,
    #    blue:School C -1.26591728870938
    assert numbers["ranef"][:2].tolist() == pytest.approx([-5.80439586418727, 0.607824236738937], rel=1e-4)
    inner = dict(zip(numbers["inner_ranef_groups"], numbers["inner_ranef"]))
    assert [inner["blue:School A"], inner["blue:School B"], inner["blue:School C"]] == pytest.approx(
        [0.568054116114745, -0.2456833465033, -1.26591728870938], rel=1e-3)
    out = capsys.readouterr().out
    assert "in 5 pictures" in out and "ranef(m)$`class:school`" in out


def test_check_model_yes_or_no_with_groups_inside_groups(capsys, needs_r):
    page = make_table(school3()).check_model("passed", using=["hours"], outcome="yes or no",
                                             grouped_by=["school", "class"])
    numbers = page._check_numbers
    # R: g <- glmer(y ~ hours + (1 | school/class), family = binomial); ranef(g)$school[, 1] -1.58543929640108
    #    -0.116825979777635; ranef(g)$`class:school`[, 1] 0.0130518090088387 -0.219021743173109 -0.0650283235988507
    assert numbers["ranef"][:2].tolist() == pytest.approx([-1.58543929640108, -0.116825979777635], rel=1e-3)
    assert numbers["inner_ranef"][:3].tolist() == pytest.approx(
        [0.0130518090088387, -0.219021743173109, -0.0650283235988507], rel=1e-2, abs=1e-4)
    assert "in 4 pictures" in capsys.readouterr().out


def test_groups_that_pull_with_groups_inside_groups(capsys, needs_r):
    make_table(school3()).show_rows_that_pull("marks", using=["hours", "breakfast"], grouped_by=["school", "class"])
    # R: inf <- influence(m, groups = "school"); max(cooks.distance(inf)) 0.145212595135807
    out = capsys.readouterr().out
    assert "the largest: School D, 0.145" in out and "(1 | school/class)" in out


# ---------------------------------------------------------------- GEE with time=, out_of=, link=
# R: s <- read.csv("school2.csv"); s$y <- as.numeric(s$passed == "yes"); s$g <- factor(s$school, levels =
#    unique(s$school)); s <- s[order(s$g), ]; geepack 1.3.13
def test_gee_with_time_matches_geeglm(capsys):
    pop = dict(grouped_by="school", effects="for the whole population")
    got = by_term(make_table(school2()).explain("days_absent", using=["hours"], outcome="counts", time="enrolled",
                                                **pop))
    # R: geeglm(days_absent ~ hours + offset(log(enrolled)), id = g, family = poisson, corstr = "exchangeable"):
    #    coef -3.42207738107801 -0.138470429340252; se 0.0861259122953703 0.0189024886661671
    assert got["hours"]["log rate ratio"] == pytest.approx(-0.138470429340252, rel=1e-5)
    assert got["hours"]["standard error"] == pytest.approx(0.0189024886661671, rel=1e-4)
    assert got["(intercept)"]["log rate ratio"] == pytest.approx(-3.42207738107801, rel=1e-5)
    assert "offset(log(enrolled))" in capsys.readouterr().out


def test_gee_with_a_link_matches_geeglm():
    pop = dict(grouped_by="school", effects="for the whole population")
    got = by_term(make_table(school2()).explain("passed", using=["hours", "breakfast"], outcome="yes or no",
                                                link="probit", **pop))
    # R: geeglm(y ~ hours + breakfast, id = g, family = binomial(link = "probit"), corstr = "exchangeable"):
    #    coef -1.80173799511293 0.297052181163462 0.233197120156732; se 0.284568095276144 0.0448261710007466
    #    0.125653550297156
    assert got["hours"]["effect (probit scale)"] == pytest.approx(0.297052181163462, rel=1e-5)
    assert got["breakfast (yes)"]["standard error"] == pytest.approx(0.125653550297156, rel=1e-4)


def test_gee_out_of_and_in_time_order_run_geepack(capsys, needs_r):
    pop = dict(grouped_by="school", effects="for the whole population")
    s = make_table(school2())
    got = by_term(s.explain("right", using=["hours"], outcome="yes or no", out_of="tries", **pop))
    # R: geeglm(cbind(right, tries - right) ~ hours, id = g, family = binomial, corstr = "exchangeable"):
    #    coef -0.581266841811507 0.10799352903193; se 0.0777610313424693 0.00892299443472997
    #    (statsmodels GEE with weights = tries gives -0.5946, so R itself)
    assert got["hours"]["log odds ratio"] == pytest.approx(0.10799352903193, rel=1e-6)
    assert got["hours"]["standard error"] == pytest.approx(0.00892299443472997, rel=1e-6)
    assert "(R geepack itself)" in capsys.readouterr().out
    got = by_term(s.explain("passed", using=["hours", "breakfast"], outcome="yes or no", link="cloglog",
                            within_groups="in time order", **pop))
    # R: geeglm(y ~ hours + breakfast, id = g, family = binomial(link = "cloglog"), corstr = "ar1"):
    #    coef -2.50648994506536 0.335809523590286 0.267568503533754; se 0.450105964061854 0.0603892808025738
    assert got["hours"]["effect (cloglog scale)"] == pytest.approx(0.335809523590286, rel=1e-6)
    assert got["hours"]["standard error"] == pytest.approx(0.0603892808025738, rel=1e-6)
    got = by_term(s.explain("days_absent", using=["hours"], outcome="counts", time="enrolled",
                            within_groups="in time order", **pop))
    # R: geeglm(days_absent ~ hours + offset(log(enrolled)), id = g, family = poisson, corstr = "ar1"):
    #    coef -3.39915165197502 -0.144406974756399; se 0.0900884756843403 0.0196083912065467
    assert got["hours"]["log rate ratio"] == pytest.approx(-0.144406974756399, rel=1e-6)
    assert got["hours"]["standard error"] == pytest.approx(0.0196083912065467, rel=1e-6)


# ---------------------------------------------------------------- variance inflation factors in check_model
# R: s <- na.omit(school[, c("marks", "hours", "sleep", "breakfast", "school", "passed")]); car 3.1
def test_check_model_vif_least_squares_matches_car(capsys):
    page = make_table(sdata.example("school")).check_model("marks", using=["hours", "sleep", "breakfast"])
    vif = page._check_numbers["vif"]
    # R: car::vif(lm(marks ~ hours + sleep + breakfast, data = s)): 1.00677016088655 1.00659219080555 1.00066265703536
    assert [vif[c][0] for c in ("hours", "sleep", "breakfast")] == pytest.approx(
        [1.00677016088655, 1.00659219080555, 1.00066265703536], rel=1e-10)
    out = capsys.readouterr().out
    assert "variance inflation factor, statsmodels variance_inflation_factor, as R car::vif()" in out


def test_check_model_vif_group_column_and_glm_from_car(capsys, needs_r):
    table = make_table(sdata.example("school"))
    vif = table.check_model("marks", using=["hours", "sleep", "school"])._check_numbers["vif"]
    # R: car::vif(lm(marks ~ hours + sleep + school, data = s)): GVIF 1.09843722228602 1.04708485508232
    #    1.13475290777979, Df 1 1 11, GVIF^(1/(2*Df)) for school 1.00576267363551
    assert vif["hours"][0] == pytest.approx(1.09843722228602, rel=1e-10)
    assert vif["school"] == pytest.approx((1.13475290777979, 11, 1.00576267363551), rel=1e-10)
    assert "(generalised, 11 df; 1.01 on the scale of one column)" in capsys.readouterr().out
    vif = table.check_model("passed", using=["hours", "sleep", "breakfast"], outcome="yes or no")._check_numbers["vif"]
    # R: car::vif(glm(y ~ hours + sleep + breakfast, family = binomial, data = s)): 1.06403521191058
    #    1.05054939802213 1.02141847706422
    assert [vif[c][0] for c in ("hours", "sleep", "breakfast")] == pytest.approx(
        [1.06403521191058, 1.05054939802213, 1.02141847706422], rel=1e-6)


def test_check_model_vif_not_for_interactions(capsys):
    page = make_table(sdata.example("school")).check_model("marks", using=["hours * breakfast"])
    assert page._check_numbers["vif"] == {}
    assert "not given for a model with interactions" in capsys.readouterr().out
