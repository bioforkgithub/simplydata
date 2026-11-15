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
    assert got[("no", "low")]["model average"] == pytest.approx(0.164241312668601, rel=1e-4)
    assert got[("yes", "high")]["95 % CI high"] == pytest.approx(0.384045508990566, rel=1e-4)
    assert got[("no - yes", "high")]["difference in chance"] == pytest.approx(-0.1031396876882832, rel=1e-4)
    out = capsys.readouterr().out
    assert 'mode = "prob"' in out and 'within each "grade" group' in out
    # R: emmeans(nnet::multinom(field ~ clover + grazed), ~ grazed | field, mode = "prob"): df 6
    got = by_term(make_table(sdata.example("meadow")).model_averages_of(
        "field", for_each="grazed", using=["clover", "grazed"], outcome="groups"), key=("term", "field group"))
    assert got[("no", "North field")]["model average"] == pytest.approx(0.348158013128585, rel=1e-4)
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
    with pytest.raises(SimplydataError, match="GEE"):
        s.explain("days_absent", using=["hours"], outcome="counts", time="enrolled", grouped_by="school",
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
    assert got["predicted marks low"][:2].tolist() == pytest.approx([42.3066608832910, 43.3235488908063], rel=1e-10)
    assert got["predicted marks high"][:2].tolist() == pytest.approx([46.595751594717, 46.929865113441], rel=1e-10)
    school.undo()
    # R: predict(l, interval = "prediction", level = 0.9)[1:2, ]
    school.add_predicted_column("marks", using=["hours", "breakfast"], interval=90, for_new_rows=True)
    got = school.as_pandas()
    assert got["predicted marks low"][:2].tolist() == pytest.approx([30.0367782261514, 30.7451351510011], rel=1e-10)
    assert got["predicted marks high"][:2].tolist() == pytest.approx([58.8656342518566, 59.5082788532462], rel=1e-10)
    assert "90 % prediction interval" in capsys.readouterr().out
    school.undo()
    # R: g <- glm(y ~ hours + breakfast, binomial); p <- predict(g, se.fit = TRUE); plogis(p$fit +- qnorm(0.975) * p$se.fit) (R glm stops at epsilon 1e-8)
    school.add_predicted_column("passed", using=["hours", "breakfast"], outcome="yes or no", interval=95)
    got = school.as_pandas()
    assert got["predicted passed low"][:2].tolist() == pytest.approx([0.184428388984262, 0.192292479315084], rel=1e-6)
    assert got["predicted passed high"][:2].tolist() == pytest.approx([0.421326728708436, 0.388231216653463], rel=1e-6)


def test_prediction_interval_checks(school):
    with pytest.raises(SimplydataError, match="outcome=\"numbers\""):
        school.add_predicted_column("passed", using=["hours"], outcome="yes or no", for_new_rows=True)
    with pytest.raises(SimplydataError, match="grouped_by="):
        school.add_predicted_column("marks", using=["hours"], grouped_by="school", interval=95)
    with pytest.raises(SimplydataError, match="percent"):
        school.add_predicted_column("marks", using=["hours"], interval=150)


# ---------------------------------------------------------------- explain(robust=True)
def test_robust_errors_for_least_squares_match_sandwich(school, capsys):
    # R: l <- lm(marks ~ hours + breakfast, s); v <- sandwich::vcovHC(l, type = "HC3"); lmtest::coeftest(l, v); coefci()
    got = by_term(school.explain("marks", using=["hours", "breakfast"], robust=True))
    assert got["hours"]["standard error"] == pytest.approx(0.2643265988481, rel=1e-9)
    assert got["breakfast (yes)"]["p-value"] == pytest.approx(0.019341, rel=1e-4)
    assert got["breakfast (yes)"]["95 % CI low"] == pytest.approx(0.52623524050107, rel=1e-9)
    out = capsys.readouterr().out
    assert "Wald F with robust errors = 57.8" in out  # lmtest::waldtest(l, vcov = v): F 57.78372
    # R: l2 <- lm(marks ~ hours + school, s); car::Anova(l2, vcov. = vcovHC(l2, type = "HC3")): school F 9.30990
    got = by_term(school.explain("marks", using=["hours", "school"], robust=True))
    assert got["school (whole column)"]["statistic"] == pytest.approx(9.30990, rel=1e-5)
    assert got["school (whole column)"]["p-value"] == pytest.approx(6.2737e-13, rel=1e-4)


def test_robust_errors_for_glms_match_sandwich(school, needs_r):
    # R: g <- glm(y ~ hours + breakfast, binomial); lmtest::coeftest(g, vcov. = sandwich::vcovHC(g, type = "HC3"))
    got = by_term(school.explain("passed", using=["hours", "breakfast"], outcome="yes or no", robust=True))
    assert got["hours"]["standard error"] == pytest.approx(0.09450506237416, rel=1e-6)
    assert got["breakfast (yes)"]["p-value"] == pytest.approx(0.25542, rel=1e-4)
    assert got["(intercept)"]["95 % CI low"] == pytest.approx(np.exp(-4.244554061363768), rel=1e-6)
    # R: ga <- glm(days ~ treatment + age, Gamma(link = "log"), tr); coeftest(ga, vcov. = vcovHC(ga, type = "HC3")): z
    got = by_term(make_table(sdata.example("trial")).explain("days", using=["treatment", "age"],
                                                            outcome="positive numbers", robust=True))
    assert got["age"]["standard error"] == pytest.approx(0.003625833265235, rel=1e-4)
    assert got["treatment (usual care)"]["p-value"] == pytest.approx(0.93169233, rel=1e-4)
    assert got["age"]["statistic name"] == "z"


def test_robust_checks(school):
    with pytest.raises(SimplydataError, match="GEE"):
        school.explain("marks", using=["hours"], grouped_by="school", robust=True)
    with pytest.raises(SimplydataError, match="True or False"):
        school.explain("marks", using=["hours"], robust="yes")


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
