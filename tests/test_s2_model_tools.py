"""S2: model_averages_of, check_model, show_rows_that_pull and compare_models, checked against R.

R 4.6.2, emmeans 2.0.4, lme4 2.1.0, pbkrtest 0.5.5; s <- read.csv("school.csv") (sdata.get_example("school")).
The R call is next to each value.
"""

import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table


@pytest.fixture
def school():
    return make_table(sdata.get_example("school"))


def by_term(result):
    return {r["term"]: r for r in result.as_pandas().to_dict("records")}


# ---------------------------------------------------------------- model_averages_of (R emmeans)
def test_model_averages_match_emmeans(school, capsys, needs_r):
    # R: m <- lm(marks ~ hours + breakfast + school, data = s); e <- emmeans(m, ~ school)
    #    summary(e); summary(pairs(e), infer = c(TRUE, TRUE))   (Tukey)
    got = by_term(school.find_model_averages_of("marks", for_each_group_in="school", using=["hours", "breakfast"]))
    out = capsys.readouterr().out
    a = got["School A"]
    assert a["model average"] == pytest.approx(41.4920943063947, rel=1e-9)
    assert a["standard error"] == pytest.approx(1.80394605170487, rel=1e-9)
    assert a["95 % CI low"] == pytest.approx(37.9304594139909, rel=1e-9)
    assert a["degrees of freedom"] == 166
    assert got["School D"]["95 % CI high"] == pytest.approx(60.8906400265140, rel=1e-9)
    pair = got["School A - School H"]
    assert pair["difference"] == pytest.approx(-8.38962018528855, rel=1e-9)
    assert pair["95 % CI low"] == pytest.approx(-16.77107426419871, rel=1e-6)
    assert pair["95 % CI high"] == pytest.approx(-0.00816610637839, rel=1e-4)
    assert pair["statistic"] == pytest.approx(-8.38962018528855 / 2.52810158701578, rel=1e-9)
    assert pair["p-value (Tukey)"] == pytest.approx(0.0495, abs=5e-5)
    assert len([t for t in got if " - " in t]) == 66
    assert "Tukey's adjustment for 66 comparisons" in out and "emmeans::emmeans(m, ~ school)" in out
    assert '"hours" held at its average' in out and '"breakfast" counted equally' in out
    assert 'Note: "school" was not in using=' in out


def test_model_averages_for_yes_or_no_are_chances_and_odds_ratios(school, capsys, needs_r):
    # R: g <- glm(y ~ hours + breakfast, family = binomial); e <- emmeans(g, ~ breakfast, type = "response")
    got = by_term(school.find_model_averages_of("passed", for_each_group_in="breakfast", using=["hours", "breakfast"],
                                           outcome="yes or no"))
    out = capsys.readouterr().out
    assert got["no"]["model average"] == pytest.approx(0.366684828561320, rel=1e-6)
    assert got["yes"]["95 % CI high"] == pytest.approx(0.573365685964980, rel=1e-6)
    assert got["no / yes"]["odds ratio"] == pytest.approx(0.659974, rel=1e-5)
    assert "chance of yes 0.367" in out and "one pair, so nothing to adjust for" in out
    assert "was not in using=" not in out


def test_model_averages_for_counts(school, needs_r):
    # R: g <- glm(days_absent ~ hours + breakfast, family = poisson); emmeans(g, ~ breakfast, type = "response")
    got = by_term(school.find_model_averages_of("days_absent", for_each_group_in="breakfast", using=["hours"], outcome="counts"))
    assert got["no"]["model average"] == pytest.approx(3.03606968621364, rel=1e-6)
    assert got["yes"]["standard error"] == pytest.approx(0.159220790257380, rel=1e-5)
    assert got["no / yes"]["rate ratio"] == pytest.approx(1.06874682375207, rel=1e-6)
    assert got["no / yes"]["95 % CI low"] == pytest.approx(0.900245590281028, rel=1e-6)
    assert got["no / yes"]["p-value (Tukey)"] == pytest.approx(0.4476, abs=5e-5)


def test_model_averages_with_a_mixed_model_use_kenward_roger(school, capsys, needs_r):
    # R: m <- lme4::lmer(marks ~ hours + breakfast + (1 | school)); emmeans(m, ~ breakfast)  (Kenward-Roger df)
    got = by_term(school.find_model_averages_of("marks", for_each_group_in="breakfast", using=["hours"], grouped_by="school"))
    assert got["no"]["model average"] == pytest.approx(46.5661990141125, rel=1e-5)
    assert got["no"]["degrees of freedom"] == pytest.approx(15.16, abs=0.01)
    assert got["no - yes"]["difference"] == pytest.approx(-2.97464502138913, rel=1e-5)
    assert got["no - yes"]["95 % CI high"] == pytest.approx(-0.799499517157336, rel=1e-4)
    assert "Kenward-Roger" in capsys.readouterr().out


def test_model_averages_checks(school):
    with pytest.raises(SimplydataError, match="holds numbers"):
        school.find_model_averages_of("marks", for_each_group_in="hours", using=["breakfast"])
    with pytest.raises(SimplydataError, match="outcome"):
        school.find_model_averages_of("marks", for_each_group_in="breakfast", outcome="words")
    with pytest.raises(SimplydataError, match="for_each_group_in="):
        school.find_model_averages_of("marks", using=["hours"])


# ---------------------------------------------------------------- check_model (R plot(lm))
def test_check_model_numbers_match_plot_lm(school, capsys):
    # R: m <- lm(marks ~ hours + breakfast, data = s)
    page = school.check_model_of("marks", using=["hours", "breakfast"])
    n = page._check_numbers
    assert n["standardised"][:3] == pytest.approx([-0.984880038908449, -0.130995839615752, 0.804864739416768],
                                                  rel=1e-9)  # rstandard(m)
    assert n["hat"][:3] == pytest.approx([0.015784631937297, 0.0111591626536684, 0.00874201939475134], rel=1e-9)
    assert n["cooks"][:3] == pytest.approx([0.0051854891955031, 6.45504040497405e-05, 0.00190436248467202],
                                           rel=1e-9)  # cooks.distance(m)
    # qqnorm(rstandard(m))$x, sorted; qqline(): slope and intercept through the quartiles
    assert n["theoretical"][:3] == pytest.approx([-2.77292129460866, -2.39397979981851, -2.20041058121003], rel=1e-9)
    assert n["slope"] == pytest.approx(0.938226365384966, rel=1e-9)
    assert n["intercept"] == pytest.approx(0.0521134031290118, rel=1e-8)
    out = capsys.readouterr().out
    assert "plot(lm(marks ~ hours + breakfast))" in out and "normal Q-Q" in out


def test_check_model_for_yes_or_no_matches_plot_glm(school, tmp_path):
    # R: g <- glm(y ~ hours + breakfast, family = binomial); plot(g) in R 4.6 uses
    #    residuals(g, "pearson") ~ predict(g), qqnorm(rstandard(g, type = "deviance")),
    #    rstandard(g, type = "pearson") ~ hatvalues(g)
    page = school.check_model_of("passed", using=["hours", "breakfast"], outcome="yes or no")
    n = page._check_numbers
    assert n["residual"][:3] == pytest.approx([-0.63699762812732, -0.623451721102957, 1.12281457406205], rel=1e-6)
    assert n["standardised"][:3] == pytest.approx([-0.832971393390656, -0.815543285044286, 1.2847171806472], rel=1e-6)
    assert n["pearson"][:3] == pytest.approx([-0.64289766021112, -0.627419743690155, 1.12938145646158], rel=1e-6)
    assert n["cooks"][:3] == pytest.approx([0.00256398581857035, 0.00167562284155314, 0.00498780419438291], rel=1e-5)
    assert n["fitted"][:3] == pytest.approx([-0.901978693843798, -0.94496789786461, -0.231677091052982], rel=1e-6)
    page.save(str(tmp_path / "checks.png"))
    assert (tmp_path / "checks.png").exists()


# ---------------------------------------------------------------- show_rows_that_pull (influence)
def test_rows_that_pull_match_cooks_distance(school, capsys):
    # R: m <- lm(marks ~ hours + breakfast); sort(cooks.distance(m), decreasing = TRUE)[1:3]: rows 48, 15, 69
    #    rstudent(m)[1:3] = -0.98479607936417 -0.130631603159207 0.804060640550196
    assert school.show_rows_that_pull_model("marks", using=["hours", "breakfast"]) is None
    out = capsys.readouterr().out
    first = [line for line in out.splitlines() if line.startswith("  row ")][:3]
    assert [line.split(":")[0].strip() for line in first] == ["row 48", "row 15", "row 69"]
    assert "Cook's distance 0.0459" in first[0]
    assert "above 4 / 180" in out and "rstudent()" in out
    model, _ = school._one_model("show_rows_that_pull", "marks", ["hours", "breakfast"], "numbers")
    numbers = school._pull_numbers(model)
    assert numbers["studentised"][:3] == pytest.approx([-0.98479607936417, -0.130631603159207, 0.804060640550196],
                                                       rel=1e-9)
    assert numbers["cooks"].max() == pytest.approx(0.0458686566162323, rel=1e-9)


def test_rows_that_pull_for_counts(school, capsys):
    # R: p <- glm(days_absent ~ hours + sleep, family = poisson); sort(cooks.distance(p), TRUE)[1:2]:
    #    row 113 0.119513356660033, row 53 0.108200456643233; rstandard(p, type = "pearson")["113"] 1.83736782001097
    school.show_rows_that_pull_model("days_absent", using=["hours", "sleep"], outcome="counts")
    rows = [line for line in capsys.readouterr().out.splitlines() if line.startswith("  row ")]
    assert rows[0].startswith("  row 113:") and "Cook's distance 0.120" in rows[0]
    assert "standardised residual 1.84" in rows[0] and rows[1].startswith("  row 53:")


# ---------------------------------------------------------------- compare_models (R anova(m0, m1))
def test_compare_models_f_test_and_aic(school, capsys):
    # R: d <- na.omit(s[, c("marks", "hours", "breakfast", "sleep")])
    #    anova(lm(marks ~ hours, d), lm(marks ~ hours + breakfast + sleep, d)): F 7.71333, Pr 0.00063779
    #    AIC 1162.99242298392 1151.90250081799; BIC 1172.23663607887 1167.30952264291
    got = school.compare_models("marks", using=["hours"], against=["hours", "breakfast", "sleep"]).as_pandas()
    assert got["AIC"][:2].tolist() == pytest.approx([1162.99242298392, 1151.90250081799], rel=1e-10)
    assert got["BIC"][:2].tolist() == pytest.approx([1172.23663607887, 1167.30952264291], rel=1e-10)
    assert got["statistic"][2] == pytest.approx(1114.254974206 / 2 / (11339.97548493 / 157), rel=1e-9)
    assert got["p-value"][2] == pytest.approx(0.00063779, rel=1e-4)
    out = capsys.readouterr().out
    assert 'Do "breakfast" and "sleep" help? F test' in out and "19 rows" in out


def test_compare_models_likelihood_ratio_for_yes_or_no(school, capsys):
    # R: anova(glm(y ~ hours, binomial), glm(y ~ hours + breakfast, binomial), test = "Chisq"):
    #    Deviance 1.344435348637, Pr 0.24625; AIC 204.307476098345 204.963040749707
    got = school.compare_models("passed", using=["hours", "breakfast"], against=["hours"],
                                outcome="yes or no").as_pandas()
    assert got["statistic"][2] == pytest.approx(1.344435348637, rel=1e-8)
    assert got["p-value"][2] == pytest.approx(0.24625, abs=5e-6)
    assert got["AIC"][:2].tolist() == pytest.approx([204.963040749707, 204.307476098345], rel=1e-10)
    out = capsys.readouterr().out
    assert 'Does "breakfast" help?' in out and "Lower AIC: the against= model" in out


def test_compare_models_not_nested_gives_aic_only(school, capsys):
    got = school.compare_models("marks", using=["hours"], against=["sleep"]).as_pandas()
    assert len(got) == 2
    assert "no test between them" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="against="):
        school.compare_models("marks", using=["hours"])
    with pytest.raises(SimplydataError, match="same model"):
        school.compare_models("marks", using=["hours"], against=["hours"])


# ---------------------------------------------------------------- compare_averages(matched_by=) (R afex)
def test_repeated_measures_anova_matches_afex(capsys, needs_r):
    # R: a <- afex::aov_ez(id = "name", dv = "marks", data = marks, within = "subject")
    #    anova(a, correction = "GG", es = "ges"); summary(a)$sphericity.tests; summary(a)$pval.adjustments
    marks = make_table(sdata.get_example("marks"))
    got = marks.compare_averages_of("marks", for_each_group_in="subject", matched_by="name").as_pandas().iloc[0]
    assert got["statistic"] == pytest.approx(1.68371, rel=1e-5)
    assert got["degrees of freedom 1"] == pytest.approx(1.818875248089, rel=1e-9)
    assert got["degrees of freedom 2"] == pytest.approx(30.92087921751, rel=1e-9)
    assert got["p-value"] == pytest.approx(0.20387830557673, rel=1e-9)
    assert got["generalised eta-squared"] == pytest.approx(0.05128570124447, rel=1e-9)
    assert got["Greenhouse-Geisser epsilon"] == pytest.approx(0.909437624044368, rel=1e-9)
    assert got["Mauchly W"] == pytest.approx(0.9004193651535, rel=1e-9)
    assert got["Mauchly p-value"] == pytest.approx(0.4320744778274, rel=1e-9)
    out = capsys.readouterr().out
    assert "repeated-measures ANOVA" in out and "Greenhouse-Geisser corrected" in out
    assert 'afex::aov_ez(id = "name", dv = "marks", within = "subject")' in out


def test_mixed_anova_matches_afex(needs_r):
    # R: aov_ez(id = "name", dv = "marks", data = marks, within = "subject", between = "class");
    #    anova(b, correction = "GG", es = "ges")
    marks = make_table(sdata.get_example("marks"))
    got = by_term(marks.compare_averages_of("marks", for_each_group_in=["subject", "class"], matched_by="name"))
    assert got["class"]["statistic"] == pytest.approx(3.325196299463586, rel=1e-9)
    assert got["class"]["p-value"] == pytest.approx(0.0637809703747278, rel=1e-9)
    assert got["subject"]["degrees of freedom 2"] == pytest.approx(27.2762243043168, rel=1e-9)
    assert got["class : subject"]["generalised eta-squared"] == pytest.approx(0.0273004164052683, rel=1e-9)
    assert got["class : subject"]["p-value"] == pytest.approx(0.8339198309763058, rel=1e-9)


def test_matched_by_checks():
    marks = make_table(sdata.get_example("marks"))
    with pytest.raises(SimplydataError, match="nothing is matched"):
        marks.compare_averages_of("marks", for_each_group_in="class", matched_by="name")
    with pytest.raises(SimplydataError, match="leave out based_on="):
        marks.compare_averages_of("marks", for_each_group_in="subject", matched_by="name", based_on="ranks")
    with pytest.raises(SimplydataError, match="leave out sides="):
        marks.compare_averages_of("marks", for_each_group_in="subject", matched_by="name", sides=1)
    with pytest.raises(SimplydataError, match="leave out sides="):
        marks.compare_averages_of("marks", for_each_group_in="subject", matched_by="name", in_order=["a", "b"])


# ---------------------------------------------------------------- review fixes: group names, df method, afex rows
def test_model_averages_pairs_keep_group_names_with_signs(school, capsys, needs_r):
    import numpy as np

    frame = sdata.get_example("school")
    frame["school"] = frame["school"].str.replace("School ", "low-")
    got = by_term(make_table(frame).find_model_averages_of("marks", for_each_group_in="school", using=["hours"]))
    # R: s$school <- sub("School ", "low-", s$school); e <- emmeans(lm(marks ~ hours + school, s), ~ school)
    #    summary(pairs(e, adjust = "tukey", parens = NULL), infer = c(TRUE, TRUE)): low-A - low-B -6.84304033357429
    #    (p 0.240433711161091), low-A - low-C 5.89432193087528, low-A - low-D -15.3309069521327
    assert got["low-A - low-B"]["difference"] == pytest.approx(-6.84304033357429, rel=1e-6)
    assert got["low-A - low-B"]["p-value (Tukey)"] == pytest.approx(0.240433711161091, rel=1e-4)
    assert got["low-A - low-D"]["difference"] == pytest.approx(-15.3309069521327, rel=1e-6)
    assert "(low-A)" not in capsys.readouterr().out
    frame = sdata.get_example("school")
    frame["breakfast"] = np.where(frame["breakfast"] == "yes", "yes - some", "no - none")
    make_table(frame).find_model_averages_of("marks", for_each_group_in="breakfast", using=["hours"])
    # R: emmeans(lm(marks ~ hours + breakfast, s7), ~ breakfast); pairs(): estimate -3.20972276354947,
    #    lower.CL -5.85876298123696 ("no - none - yes - some")
    out = capsys.readouterr().out
    assert "no - none minus yes - some: difference -3.21 (95 % CI -5.86 to" in out


def test_model_averages_say_the_degrees_of_freedom_emmeans_used(capsys, needs_r):
    import numpy as np
    import pandas as pd

    i = np.arange(3200)
    frame = pd.DataFrame({"g": [f"g{k % 40:02d}" for k in i], "x": ((i * 7) % 13).astype(float),
                          "grp": np.where((i // 3) % 2 == 0, "a", "b")})
    frame["y"] = 5 + 0.3 * frame.x + (frame.grp == "b") + ((i * 17) % 23) / 4 + (i % 40) / 10
    # R: i <- 0:3199; d8 <- data.frame(g = sprintf("g%02d", i %% 40), x = (i * 7) %% 13,
    #    grp = c("a", "b")[(i %/% 3) %% 2 + 1]); d8$y <- 5 + 0.3 * d8$x + (d8$grp == "b") + ((i * 17) %% 23) / 4 +
    #    (i %% 40) / 10; e <- emmeans(lmer(y ~ x + grp + (1 | g), d8), ~ grp): above pbkrtest.limit (3000) emmeans
    #    says "Degrees-of-freedom method: asymptotic"; emmean 11.4985448933657 12.4997371017639, df Inf Inf
    got = by_term(make_table(frame).find_model_averages_of("y", for_each_group_in="grp", using=["x"], grouped_by="g"))
    assert got["a"]["model average"] == pytest.approx(11.4985448933657, rel=1e-6)
    assert got["b"]["model average"] == pytest.approx(12.4997371017639, rel=1e-6)
    assert got["a"]["degrees of freedom"] == float("inf")
    out = capsys.readouterr().out
    assert "asymptotic (z) degrees of freedom" in out and "Kenward-Roger" not in out


def test_repeated_measures_averages_are_of_the_rows_afex_used(capsys, needs_r):
    import numpy as np
    import pandas as pd

    frame = pd.DataFrame([{"id": f"s{s}", "cond": c} for s in range(12) for c in "abc"])
    frame["y"] = 10 + (frame.cond == "b") + np.sin(np.arange(len(frame)))
    frame = frame.drop(index=[0])  # s0 is not measured in "a"
    # R: d <- expand.grid(cond = c("a", "b", "c"), id = sprintf("s%d", 0:11))[, 2:1]; k <- seq_len(36) - 1;
    #    d$y <- 10 + (d$cond == "b") + sin(k); d <- d[-1, ]; a <- aov_ez(id = "id", dv = "y", data = d,
    #    within = "cond"); tapply(a$data$long$y, a$data$long$cond, mean): a 10.0487167374033, b 10.9902774265512,
    #    c 9.94077700488995 (all rows: b 11.0612102230725, c 10.0214870400513); nrow(a$data$wide) 11;
    #    anova(a, correction = "GG", es = "ges")$F 5.7216830269679
    got = make_table(frame).compare_averages_of("y", for_each_group_in="cond", matched_by="id").as_pandas().iloc[0]
    assert got["statistic"] == pytest.approx(5.7216830269679, rel=1e-6)
    out = capsys.readouterr().out
    assert 'average "y" for each "cond": a 10.0, b 11.0, c 9.94' in out
    assert '11 "id" each measured' in out and '1 "id" left out by afex' in out


def test_repeated_measures_keep_the_group_names_of_the_table(capsys, needs_r):
    import pandas as pd

    # Student's sleep data, R datasets::sleep. R: a <- afex::aov_ez(id = "ID", dv = "extra", data = sleep,
    #    within = "group"); anova(a)$F 16.5009, p 0.002833; afex names the levels "X1", "X2" (make.names), the
    #    table calls them 1 and 2 (the reliability study found 'for each "group": X1 0.750, X2 2.33')
    extra = [0.7, -1.6, -0.2, -1.2, -0.1, 3.4, 3.7, 0.8, 0.0, 2.0, 1.9, 0.8, 1.1, 0.1, -0.1, 4.4, 5.5, 1.6, 4.6, 3.4]
    sleep = pd.DataFrame({"extra": extra, "group": [1] * 10 + [2] * 10, "ID": list(range(1, 11)) * 2})
    got = make_table(sleep).compare_averages_of("extra", for_each_group_in="group", matched_by="ID").as_pandas()
    assert got.iloc[0]["statistic"] == pytest.approx(16.5008812, rel=1e-6)
    assert got.iloc[0]["p-value"] == pytest.approx(0.00283289, rel=1e-4)
    out = capsys.readouterr().out
    assert 'average "extra" for each "group": 1 0.750, 2 2.33' in out
    assert "X1" not in out and "X2" not in out
    # names that make.names would change ("a b" -> "a.b", "2nd" -> "X2nd"), within and between
    frame = pd.DataFrame([{"id": f"s{s}", "when": w, "arm": "drug A" if s < 6 else "2nd drug"}
                          for s in range(12) for w in ("week 1", "week-2")])
    frame["y"] = [float((7 * i) % 11) + (row.when == "week-2") * 2 for i, row in enumerate(frame.itertuples())]
    result = make_table(frame).compare_averages_of("y", for_each_group_in=["when", "arm"], matched_by="id")
    out = capsys.readouterr().out
    assert 'for each "when": week 1 ' in out and ", week-2 " in out
    assert 'for each "arm": 2nd drug ' in out and ", drug A " in out
    assert "week.1" not in out and "X2nd" not in out and "drug.A" not in out
    assert set(result.as_pandas()["term"]) == {"when", "arm", "arm : when"}


def test_greenhouse_geisser_is_claimed_only_when_applied(capsys, needs_r):
    import pandas as pd

    # R: anova(afex::aov_ez(id = "ID", dv = "extra", data = sleep, within = "group"), correction = "GG"):
    #    with two levels summary(a)$pval.adjustments gives GG eps NaN and the df stay 1 and 9, so nothing was
    #    corrected (the line used to say "(Greenhouse-Geisser corrected)")
    extra = [0.7, -1.6, -0.2, -1.2, -0.1, 3.4, 3.7, 0.8, 0.0, 2.0, 1.9, 0.8, 1.1, 0.1, -0.1, 4.4, 5.5, 1.6, 4.6, 3.4]
    sleep = pd.DataFrame({"extra": extra, "group": [1] * 10 + [2] * 10, "ID": list(range(1, 11)) * 2})
    make_table(sleep).compare_averages_of("extra", for_each_group_in="group", matched_by="ID")
    out = capsys.readouterr().out
    assert '"group": F = 16.5, df = 1.00 and 9.00 (two matched groups, so no correction is needed), ' in out
    assert "corrected" not in out and "are corrected with Greenhouse-Geisser" not in out
    assert "with two matched groups each person has one difference" in out
    # mixed, two repeated groups: neither the independent "arm" nor the repeated terms are corrected
    frame = pd.DataFrame([{"id": f"s{s}", "when": w, "arm": "drug A" if s < 6 else "2nd drug"}
                          for s in range(12) for w in ("week 1", "week-2")])
    frame["y"] = [float((7 * i) % 11) + (row.when == "week-2") * 2 for i, row in enumerate(frame.itertuples())]
    make_table(frame).compare_averages_of("y", for_each_group_in=["when", "arm"], matched_by="id")
    out = capsys.readouterr().out
    assert '"arm": F = 0.300, df = 1.00 and 10.0, generalised' in out
    assert '"when": F = 2.34, df = 1.00 and 10.0 (two matched groups, so no correction is needed)' in out
    assert "the interaction arm : when: F = 0.294, df = 1.00 and 10.0 (two matched groups, so no correction" in out
    assert "corrected" not in out
    # three repeated groups (epsilon 0.909): the correction is applied and said, in the mixed design too
    marks = make_table(sdata.get_example("marks"))
    marks.compare_averages_of("marks", for_each_group_in=["subject", "class"], matched_by="name")
    out = capsys.readouterr().out
    assert '"class": F = 3.33, df = 2.00 and 15.0, generalised' in out
    assert '"subject": F = 1.55, df = 1.82 and 27.3 (Greenhouse-Geisser corrected)' in out
    assert "df = 3.64 and 27.3 (Greenhouse-Geisser corrected)" in out
    assert "are corrected with Greenhouse-Geisser's epsilon" in out


def _numbers(i):
    return float((i * 7) % 11) / 2


def test_greenhouse_geisser_without_an_epsilon_is_not_called_two_groups(capsys, needs_r):
    import pandas as pd

    # 3 people, 5 groups: afex gives no epsilon (summary(a)$pval.adjustments is NaN) and keeps df 4 and 8;
    #    R: anova(aov_ez(id = "id", dv = "y", data = d, within = "t"), correction = "GG")$F 0.968
    rows = [{"id": s, "t": t} for s in range(3) for t in "abcde"]
    frame = pd.DataFrame(rows).assign(y=[_numbers(i) for i in range(len(rows))])
    make_table(frame).compare_averages_of("y", for_each_group_in="t", matched_by="id")
    out = capsys.readouterr().out
    assert ('"t": F = 0.968, df = 4.00 and 8.00 (afex could not estimate Greenhouse-Geisser\'s epsilon, so the '
            "degrees of freedom are not corrected)") in out
    assert "two matched groups" not in out and "epsilon is 1" not in out
    assert ("afex could not estimate Greenhouse-Geisser's epsilon for \"t\" (for example with fewer people than "
            "groups, or with no spread in the differences), so its degrees of freedom are not corrected.") in out
    # exactly built values, 6 people and 3 groups: no sphericity rows from afex either
    rows = [{"id": s, "t": t, "y": float(s + i + (0.5 if (s + i) % 2 else -0.5))}
            for s in range(6) for i, t in enumerate("abc")]
    make_table(pd.DataFrame(rows)).compare_averages_of("y", for_each_group_in="t", matched_by="id")
    out = capsys.readouterr().out
    assert '"t": F = 15.0, df = 2.00 and 10.0 (afex could not estimate' in out and "two matched groups" not in out
    # two repeated columns: "w" has two groups, "t" five with no epsilon
    rows = [{"id": s, "t": t, "w": w} for s in range(3) for t in "abcde" for w in ("p", "q")]
    frame = pd.DataFrame(rows).assign(y=[_numbers(i) for i in range(len(rows))])
    make_table(frame).compare_averages_of("y", for_each_group_in=["t", "w"], matched_by="id")
    out = capsys.readouterr().out
    assert '"t": F = 0.554, df = 4.00 and 8.00 (afex could not estimate' in out
    assert '"w": F = 0.0992, df = 1.00 and 2.00 (two matched groups, so no correction is needed)' in out
    assert "the interaction t : w: F = 0.182, df = 4.00 and 8.00 (afex could not estimate" in out
    assert ('"w" has two matched groups, so there is nothing for Greenhouse-Geisser\'s correction to correct; afex '
            'could not estimate Greenhouse-Geisser\'s epsilon for "t" and "t : w"') in out
    # mixed: an independent column and five repeated groups with no epsilon
    rows = [{"id": s, "arm": "A" if s < 2 else "B", "t": t} for s in range(4) for t in "abcde"]
    frame = pd.DataFrame(rows).assign(y=[_numbers(i) for i in range(len(rows))])
    make_table(frame).compare_averages_of("y", for_each_group_in=["t", "arm"], matched_by="id")
    out = capsys.readouterr().out
    assert '"arm": F = 8.00, df = 1.00 and 2.00, generalised' in out
    assert '"t": F = 0.564, df = 4.00 and 8.00 (afex could not estimate' in out
    assert "the interaction arm : t: F = 1.75, df = 4.00 and 8.00 (afex could not estimate" in out
    assert "two matched groups" not in out


def test_repeated_measures_notes_and_order_use_the_group_names(capsys, needs_r):
    import pandas as pd

    # afex's note on people left out shows its wide table, whose columns are the codes sent to R
    rows = [{"id": s, "t": t} for s in range(6) for t in ("first", "second", "third")]
    frame = pd.DataFrame(rows).assign(y=[_numbers(i) for i in range(len(rows))]).drop(index=[2])
    make_table(frame).compare_averages_of("y", for_each_group_in="t", matched_by="id")
    out = capsys.readouterr().out
    assert "Note from R (afex::aov_ez): Missing values for 1 ID(s)" in out
    assert "id first second third" in out and "L0x" not in out
    # "a b" and "a.b" are one name after R's make.names ("a.b", "a.b.1"): each keeps its own average
    rows = [{"id": s, "t": t, "y": float(s % 2) * 2 + 10 * i}
            for s in range(8) for i, t in enumerate(("a b", "a.b", "c"))]
    frame = pd.DataFrame(rows)
    means = frame.groupby("t")["y"].mean()  # a b 1.00, a.b 11.0, c 21.0
    make_table(frame).compare_averages_of("y", for_each_group_in="t", matched_by="id")
    out = capsys.readouterr().out
    assert means["a b"] == 1.0 and means["a.b"] == 11.0
    assert 'average "y" for each "t": a b 1.00, a.b 11.0, c 21.0' in out
    # number names in order of their value, not as text (1, 2, ..., 10, not 1, 10, 2)
    rows = [{"id": s, "t": t} for s in range(12) for t in range(1, 11)]
    frame = pd.DataFrame(rows).assign(y=[_numbers(i) for i in range(len(rows))])
    make_table(frame).compare_averages_of("y", for_each_group_in="t", matched_by="id")
    out = capsys.readouterr().out
    line = next(x for x in out.splitlines() if 'for each "t":' in x)
    assert [part.split()[0] for part in line.split(": ", 1)[1].split(", ")] == [str(k) for k in range(1, 11)]
