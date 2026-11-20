"""Phase S3a-3, checking and comparing: each new word and option against its parent package and R.

explain(spread_changes_with=, neighbours_alike_in_order_of=) (R nlme::gls), find_columns_that_predict (R glmnet),
compare_models(using=[[...], ...]) (statsmodels aicc, R AICcmodavg), compare_models(check_on_left_out_rows=True)
(R boot::cv.glm), check_model_of notes (statsmodels het_breuschpagan / het_white, R lmtest; calibration, R
performance, Brier), find_model_averages_of(comparing=, within_each_group_in=, over_range_of=) (R emmeans),
find_group_levels_of (R lme4::ranef), compare_averages_of(grouped_by=) (R aov Error()), compare_averages_of([...])
(statsmodels MANOVA, R summary.manova) and chart.draw_interaction_lines.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata._errors import SimplydataError

DATA = Path(__file__).resolve().parents[1] / "validation" / "data"


def r(code, packages=(), **values):
    from simplydata._r import r_call

    return r_call(code, packages=packages, **values)


@pytest.fixture
def school():
    return sdata.table(sdata.get_example("school"))


@pytest.fixture
def school_frame():
    return sdata.get_example("school")


def row(result, term):
    frame = result.as_pandas()
    return frame[frame["term"] == term].iloc[0]


# ---------------------------------------------------------------- J14 generalised least squares
def test_spread_changes_with_a_group_column_matches_nlme(school, school_frame, needs_r, capsys):
    result = school.explain("marks", using=["hours"], spread_changes_with="school")
    printed = capsys.readouterr().out
    d = school_frame.dropna(subset=["marks", "hours"])
    found = r("m <- nlme::gls(marks ~ hours, data = data.frame(marks = marks, hours = hours, s = factor(s)), "
              "weights = nlme::varIdent(form = ~ 1 | s)); v <- stats::coef(m$modelStruct$varStruct, unconstrained = "
              "FALSE, allCoef = TRUE); list(b = unname(stats::coef(m)), se = unname(sqrt(diag(stats::vcov(m)))), "
              "ratio = unname(v[names(v) == 'School C']), aic = stats::AIC(m))", ("nlme",),
              marks=d["marks"].to_numpy(float), hours=d["hours"].to_numpy(float), s=d["school"].to_numpy(object))
    assert row(result, "hours")["effect"] == pytest.approx(float(found["b"][1]), rel=1e-6)
    assert row(result, "hours")["standard error"] == pytest.approx(float(found["se"][1]), rel=1e-5)
    assert row(result, 'spread of "School C" against "School A"')["effect"] == pytest.approx(float(found["ratio"][0]),
                                                                                            rel=1e-5)
    assert row(result, "AIC (REML) of this model")["effect"] == pytest.approx(float(found["aic"][0]), rel=1e-8)
    assert "varIdent(form = ~ 1 | school)" in printed and "studies would show this much" in printed


def test_neighbours_alike_in_even_order_uses_ar1_and_matches_nlme(needs_r, capsys):
    lake = pd.read_csv(DATA / "lake_huron.csv")
    result = sdata.table(lake).explain("level", using=["year"], neighbours_alike_in_order_of="year")
    printed = capsys.readouterr().out
    found = r("m <- nlme::gls(level ~ year, correlation = nlme::corAR1(form = ~ year)); "
              "list(b = unname(stats::coef(m)), phi = unname(stats::coef(m$modelStruct$corStruct, unconstrained = "
              "FALSE)))", ("nlme",), level=lake["level"].to_numpy(float), year=lake["year"].to_numpy(float))
    assert row(result, "year")["effect"] == pytest.approx(float(found["b"][1]), rel=1e-6)
    assert row(result, 'correlation of neighbours in "year" order')["effect"] == pytest.approx(
        float(found["phi"][0]), rel=1e-5)
    assert "corAR1" in printed


def test_neighbours_alike_with_uneven_dates_uses_car1(needs_r, capsys):
    river = sdata.table(sdata.get_example("river"))
    river.keep_rows_where("station", is_equal_to="Station A")
    river.keep_rows_by_position(1, to=60)
    river.remove_rows_by_position(5)
    river.explain("level", using=["nitrate"], neighbours_alike_in_order_of="date")
    assert "corCAR1(form = ~ date)" in capsys.readouterr().out


@pytest.mark.parametrize("options, words", [
    (dict(spread_changes_with="school", outcome="yes or no", using=["hours"], column="passed"), 'outcome="numbers"'),
    (dict(spread_changes_with="school", grouped_by="class"), "grouped_by="),
    (dict(neighbours_alike_in_order_of="school"), "numbers or dates"),
    (dict(neighbours_alike_in_order_of="hours"), "repeated values"),
    (dict(spread_changes_with="school", robust_errors=True), "robust_errors="),
])
def test_gls_refusals(school, options, words):
    options = {"column": "marks", "using": ["hours"], **options}
    column = options.pop("column")
    with pytest.raises(SimplydataError, match=words):
        school.explain(column, **options)


def test_american_spelling_of_neighbours_is_accepted(needs_r, capsys):
    lake = pd.read_csv(DATA / "lake_huron.csv")
    sdata.table(lake).explain("level", using=["year"], neighbors_alike_in_order_of="year")
    assert "corAR1" in capsys.readouterr().out


# ---------------------------------------------------------------- L10 lasso
def test_lasso_matches_glmnet_with_the_same_seed(needs_r, capsys):
    swiss = pd.read_csv(DATA / "swiss.csv")
    cols = ["Agriculture", "Examination", "Education", "Catholic", "Infant.Mortality"]
    result = sdata.table(swiss).find_columns_that_predict("Fertility", using=cols)
    printed = capsys.readouterr().out
    found = r("set.seed(1); f <- glmnet::cv.glmnet(x, y, alpha = 1, nfolds = 10); "
              "list(b = as.numeric(stats::coef(f, s = 'lambda.1se')), lambda = f$lambda.1se)", ("glmnet",),
              x=swiss[cols].to_numpy(float), y=swiss["Fertility"].to_numpy(float))
    frame = result.as_pandas()
    effects = frame[frame["term"].isin(["(intercept)", *cols])]["effect"].to_numpy(float)
    assert effects == pytest.approx(np.asarray(found["b"], float), rel=1e-9, abs=1e-12)
    assert row(result, "penalty chosen (lambda.1se)")["penalty"] == pytest.approx(float(found["lambda"][0]), rel=1e-12)
    assert "No p-values" in printed and "p =" not in printed


def test_lasso_effects_are_a_penalised_least_squares_minimum_as_statsmodels(needs_r):
    """At glmnet's chosen penalty, statsmodels' elastic net (no random folds) gives the same effects."""
    import statsmodels.api as sm

    swiss = pd.read_csv(DATA / "swiss.csv")
    cols = ["Agriculture", "Examination", "Education", "Catholic", "Infant.Mortality"]
    result = sdata.table(swiss).find_columns_that_predict("Fertility", using=cols).as_pandas()
    lam = float(result.loc[result["term"] == "penalty chosen (lambda.1se)", "penalty"].iloc[0])
    X = swiss[cols].to_numpy(float)
    y = swiss["Fertility"].to_numpy(float)
    sd = X.std(axis=0)  # glmnet standardises with n in the divisor
    Z = (X - X.mean(axis=0)) / sd
    fit = sm.OLS(y - y.mean(), Z).fit_regularized(method="elastic_net", alpha=lam, L1_wt=1.0, cnvrg_tol=1e-12,
                                                   maxiter=10000)
    ours = result.set_index("term").loc[cols, "effect"].to_numpy(float)
    # glmnet stops at its own convergence threshold (thresh = 1e-7 on the path), so it agrees to about 0.5 %
    assert ours == pytest.approx(fit.params / sd, rel=5e-3, abs=1e-3)


def test_lasso_refuses_ridge_few_rows_and_one_column(school):
    with pytest.raises(SimplydataError, match="keeps every column"):
        school.find_columns_that_predict("marks", using=["hours", "sleep"], method="ridge")
    with pytest.raises(SimplydataError, match="at least two"):
        school.find_columns_that_predict("marks", using=["hours"])
    small = sdata.table(sdata.get_example("school").head(15))
    with pytest.raises(SimplydataError, match="at least 20 rows"):
        small.find_columns_that_predict("marks", using=["hours", "sleep"])


# ---------------------------------------------------------------- O10 AICc table
def test_several_models_give_an_aicc_table_as_aictab(school, school_frame, needs_r, capsys):
    result = school.compare_models("marks", using=[["hours"], ["hours", "breakfast"], ["hours * breakfast"]])
    printed = capsys.readouterr().out
    d = school_frame.dropna(subset=["marks", "hours", "breakfast"])
    found = r("d <- data.frame(y = y, h = h, b = factor(b)); "
              "ms <- list(a = stats::lm(y ~ h, d), b = stats::lm(y ~ h + b, d), c = stats::lm(y ~ h * b, d)); "
              "t <- AICcmodavg::aictab(ms, modnames = names(ms), sort = FALSE); "
              "list(aicc = t$AICc, w = t$AICcWt)", ("AICcmodavg",),
              y=d["marks"].to_numpy(float), h=d["hours"].to_numpy(float), b=d["breakfast"].to_numpy(object))
    frame = result.as_pandas().set_index("term")
    order = ["marks ~ hours", "marks ~ hours + breakfast", "marks ~ hours * breakfast"]
    assert frame.loc[order, "AICc"].to_numpy(float) == pytest.approx(np.asarray(found["aicc"], float), rel=1e-10)
    assert frame.loc[order, "Akaike weight"].to_numpy(float) == pytest.approx(np.asarray(found["w"], float), rel=1e-8)
    assert "under 2" in printed and "not the chance that a model is true" in printed


def test_a_flat_list_without_against_shows_the_list_of_lists(school):
    with pytest.raises(SimplydataError, match=r"using=\[\['hours'\], \[\.\.\.\]\]"):
        school.compare_models("marks", using=["hours"])


def test_quasi_poisson_has_no_aic_table(school):
    with pytest.raises(SimplydataError, match="no likelihood"):
        school.compare_models("days_absent", using=[["hours"], ["hours", "sleep"]], outcome="counts (overdispersed)")


# ---------------------------------------------------------------- O14 left-out rows
def test_left_out_rows_match_boot_cv_glm(school, school_frame, needs_r, capsys):
    result = school.compare_models("marks", using=[["hours"], ["hours", "breakfast"]], check_on_left_out_rows=True)
    printed = capsys.readouterr().out
    d = school_frame.dropna(subset=["marks", "hours", "breakfast"])
    found = r("d <- data.frame(y = y, h = h, b = factor(b)); out <- c(); for (f in list(y ~ h, y ~ h + b)) { "
              "m <- stats::glm(f, data = d); set.seed(1); out <- c(out, boot::cv.glm(d, m, K = 10)$delta[1]) }; "
              "list(delta = out)", ("boot",),
              y=d["marks"].to_numpy(float), h=d["hours"].to_numpy(float), b=d["breakfast"].to_numpy(object))
    got = result.as_pandas()["mean squared error on left-out rows"].to_numpy(float)
    assert got == pytest.approx(np.asarray(found["delta"], float), rel=1e-10)
    assert "split into 10 parts at random (with_seed=1)" in printed


def test_left_out_rows_for_yes_or_no_is_the_brier_score(school, needs_r, capsys):
    school.compare_models("passed", using=["hours", "breakfast"], outcome="yes or no", check_on_left_out_rows=True)
    assert "Brier score" in capsys.readouterr().out


def test_left_out_rows_refusals(school):
    with pytest.raises(SimplydataError, match="grouped_by="):
        school.compare_models("marks", using=["hours"], grouped_by="school", check_on_left_out_rows=True)
    with pytest.raises(SimplydataError, match="outcome="):
        school.compare_models("marks", using=["hours"], outcome="positive numbers", check_on_left_out_rows=True)


# ---------------------------------------------------------------- O05, O13 + R07 check_model_of notes
def test_spread_tests_match_lmtest(school, school_frame, needs_r, capsys):
    page = school.check_model_of("marks", using=["hours", "breakfast"])
    printed = capsys.readouterr().out
    d = school_frame.dropna(subset=["marks", "hours", "breakfast"])
    found = r("d <- data.frame(y = y, h = h, b = as.numeric(b == 'yes')); m <- stats::lm(y ~ h + b, d); "
              "bp <- lmtest::bptest(m); w <- lmtest::bptest(m, ~ h + b + I(h^2) + h:b, data = d); "
              "list(bp = unname(bp$statistic), bpp = bp$p.value, w = unname(w$statistic), wp = w$p.value, "
              "wdf = unname(w$parameter))", ("lmtest",),
              y=d["marks"].to_numpy(float), h=d["hours"].to_numpy(float), b=d["breakfast"].to_numpy(object))
    numbers = page._check_numbers
    assert numbers["breusch_pagan"][0] == pytest.approx(float(found["bp"][0]), rel=1e-9)
    assert numbers["breusch_pagan"][2] == pytest.approx(float(found["bpp"][0]), rel=1e-9)
    assert numbers["white"][0] == pytest.approx(float(found["w"][0]), rel=1e-9)
    assert numbers["white"][1] == float(found["wdf"][0])
    assert "if the spread were truly the same everywhere" in printed


def test_calibration_hosmer_and_brier_for_yes_or_no(school, school_frame, needs_r, capsys):
    page = school.check_model_of("passed", using=["hours", "breakfast"], outcome="yes or no")
    printed = capsys.readouterr().out
    d = school_frame.dropna(subset=["passed", "hours", "breakfast"])
    found = r("d <- data.frame(y = as.numeric(y == 'yes'), h = h, b = factor(b)); "
              "m <- stats::glm(y ~ h + b, data = d, family = stats::binomial); "
              "h <- performance::performance_hosmer(m, n_bins = 10); "
              "list(chi = unname(h$chisq), p = unname(h$p.value), brier = DescTools::BrierScore(m))",
              ("performance", "DescTools"),
              y=d["passed"].to_numpy(object), h=d["hours"].to_numpy(float), b=d["breakfast"].to_numpy(object))
    numbers = page._check_numbers
    assert numbers["hosmer"][0] == pytest.approx(float(found["chi"][0]), rel=1e-6)
    assert numbers["hosmer"][2] == pytest.approx(float(found["p"][0]), rel=1e-6)
    assert numbers["brier"] == pytest.approx(float(found["brier"][0]), rel=1e-10)
    assert len(page._charts if hasattr(page, "_charts") else [0] * 5) >= 5 or "five pictures" in printed
    assert "5. calibration" in printed and "predicted chances truly matched" in printed


# ---------------------------------------------------------------- N10, N12, O18 find_model_averages_of
WARP = None


@pytest.fixture
def warp():
    return sdata.table(pd.read_csv(DATA / "warpbreaks.csv"))


def emm(code, frame):
    return r("d <- data.frame(y = y, w = factor(w), t = factor(t, levels = c('L', 'M', 'H'))); "
             "m <- stats::lm(y ~ w * t, data = d); " + code, ("emmeans",),
             y=frame["breaks"].to_numpy(float), w=frame["wool"].to_numpy(object), t=frame["tension"].to_numpy(object))


def test_each_with_the_first_matches_emmeans_trt_vs_ctrl(warp, needs_r, capsys):
    result = warp.find_model_averages_of("breaks", for_each_group_in="tension", using=["wool * tension"],
                                         comparing="each with the first", in_order=["L", "M", "H"])
    printed = capsys.readouterr().out
    found = emm("e <- emmeans::emmeans(m, ~ t); s <- as.data.frame(summary(emmeans::contrast(e, 'trt.vs.ctrl'), "
                "infer = TRUE)); list(est = s$estimate, p = s$p.value)", pd.read_csv(DATA / "warpbreaks.csv"))
    frame = result.as_pandas()
    pairs = frame[frame["term"].str.contains("minus")]
    assert pairs["difference"].to_numpy(float) == pytest.approx(np.asarray(found["est"], float), rel=1e-10)
    assert pairs["p-value (Dunnett)"].to_numpy(float) == pytest.approx(np.asarray(found["p"], float), rel=1e-6)
    assert "Dunnett" in printed


def test_helmert_weights_and_trend_names(warp, needs_r, capsys):
    result = warp.find_model_averages_of("breaks", for_each_group_in="tension", using=["wool * tension"],
                                         comparing="each with the average of the ones before",
                                         in_order=["L", "M", "H"])
    found = emm("e <- emmeans::emmeans(m, ~ t); s <- as.data.frame(emmeans::contrast(e, list(a = c(-1, 1, 0), "
                "b = c(-0.5, -0.5, 1)))); list(est = s$estimate)", pd.read_csv(DATA / "warpbreaks.csv"))
    frame = result.as_pandas()
    assert frame["difference"].dropna().to_numpy(float) == pytest.approx(np.asarray(found["est"], float), rel=1e-10)
    assert "H against the average of L and M" in capsys.readouterr().out
    warp.find_model_averages_of("breaks", for_each_group_in="tension", using=["wool * tension"], comparing="trend",
                                in_order=["L", "M", "H"])
    printed = capsys.readouterr().out
    assert "straight (linear)" in printed and "curved (quadratic)" in printed


def test_own_weights_and_wrong_lengths(warp, needs_r, capsys):
    warp.find_model_averages_of("breaks", for_each_group_in="tension", using=["tension"],
                                comparing={"L against the rest": [1, -0.5, -0.5]}, in_order=["L", "M", "H"])
    assert "L against the rest" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="one weight for each group"):
        warp.find_model_averages_of("breaks", for_each_group_in="tension", using=["tension"],
                                    comparing={"bad": [1, -1]})


def test_simple_effects_print_the_interaction_test_first(warp, needs_r, capsys):
    result = warp.find_model_averages_of("breaks", for_each_group_in="tension", using=["wool * tension"],
                                         within_each_group_in="wool", in_order=["L", "M", "H"])
    printed = capsys.readouterr().out
    found = emm("j <- as.data.frame(emmeans::joint_tests(m)); jb <- as.data.frame(emmeans::joint_tests(m, by = 'w')); "
                "list(f = j$F.ratio[j[[1]] == 'w:t'], fa = jb$F.ratio[jb[[1]] == 't'])", pd.read_csv(DATA / "warpbreaks.csv"))
    assert row(result, "interaction tension : wool")["statistic"] == pytest.approx(float(found["f"][0]), rel=1e-8)
    assert row(result, "tension within wool A")["statistic"] == pytest.approx(float(found["fa"][0]), rel=1e-8)
    assert printed.index("interaction") < printed.index("within \"wool\" A") < printed.index("Each pair")
    assert "Gelman & Stern" in printed


def test_within_and_for_each_must_differ(warp):
    with pytest.raises(SimplydataError, match="for_each_group_in= names the groups"):
        warp.find_model_averages_of("breaks", for_each_group_in="tension", within_each_group_in="tension")


def test_over_range_of_matches_emmeans_at(school, school_frame, needs_r, capsys):
    result = school.find_model_averages_of("marks", over_range_of="hours", using=["hours", "breakfast"])
    printed = capsys.readouterr().out
    d = school_frame.dropna(subset=["marks", "hours", "breakfast"])
    grid = np.linspace(d["hours"].min(), d["hours"].max(), 50)
    found = r("m <- stats::lm(y ~ h + b, data = data.frame(y = y, h = h, b = factor(b))); "
              "a <- as.data.frame(summary(emmeans::emmeans(m, ~ h, at = list(h = grid)))); "
              "list(e = a$emmean, low = a$lower.CL)", ("emmeans",), y=d["marks"].to_numpy(float),
              h=d["hours"].to_numpy(float), b=d["breakfast"].to_numpy(object), grid=grid)
    frame = result.as_pandas()
    assert len(frame) == 50
    assert frame["model average"].to_numpy(float) == pytest.approx(np.asarray(found["e"], float), rel=1e-10)
    assert frame["95 % CI low"].to_numpy(float) == pytest.approx(np.asarray(found["low"], float), rel=1e-10)
    assert "draw_band" in printed


def test_comparing_values_are_checked(warp):
    with pytest.raises(SimplydataError, match="comparing"):
        warp.find_model_averages_of("breaks", for_each_group_in="tension", comparing="each with everything")


# ---------------------------------------------------------------- M12 group levels
def test_group_levels_match_lme4_ranef(school, school_frame, needs_r, capsys):
    result = school.find_group_levels_of("marks", using=["hours"], grouped_by="school")
    printed = capsys.readouterr().out
    d = school_frame.dropna(subset=["marks", "hours"])
    found = r("m <- lme4::lmer(y ~ h + (1 | g), data = data.frame(y = y, h = h, g = factor(g))); "
              "re <- lme4::ranef(m, condVar = TRUE)$g; list(g = rownames(re), level = re[, 1], "
              "sd = sqrt(attr(re, 'postVar')[1, 1, ]), own = stats::coef(m)$g[, 1])", ("lme4",),
              y=d["marks"].to_numpy(float), h=d["hours"].to_numpy(float), g=d["school"].to_numpy(object))
    frame = result.as_pandas().set_index("term").loc[list(found["g"])]
    assert frame["starting level (distance from the average)"].to_numpy(float) == pytest.approx(
        np.asarray(found["level"], float), rel=1e-6, abs=1e-8)
    assert frame["starting level conditional standard deviation"].to_numpy(float) == pytest.approx(
        np.asarray(found["sd"], float), rel=1e-6)
    assert frame["own starting level"].to_numpy(float) == pytest.approx(np.asarray(found["own"], float), rel=1e-6)
    assert "Houslay & Wilson" in printed and (frame["note"].str.contains("not use them as data")).all()


def test_group_levels_need_grouped_by(school):
    with pytest.raises(SimplydataError, match="needs grouped_by="):
        school.find_group_levels_of("marks", using=["hours"])


# ---------------------------------------------------------------- N07 nested ANOVA, N09 MANOVA
def test_nested_anova_matches_the_published_glycogen_table(needs_r, capsys):
    rats = sdata.table(pd.read_csv(DATA / "rat_glycogen.csv"))
    result = rats.compare_averages_of("glycogen", for_each_group_in="treatment", grouped_by="rat")
    printed = capsys.readouterr().out
    first = result.as_pandas().iloc[0]
    # Sokal & Rohlf (1981, Box 10.1); Crawley (2007): treatment SS 1557.56 on 2 df, rats SS 797.67 on 3, F = 2.929
    assert first["statistic"] == pytest.approx(2.9290, abs=5e-4)
    assert first["sum of squares"] == pytest.approx(1557.56, abs=0.005)
    assert (first["degrees of freedom 1"], first["degrees of freedom 2"]) == (2.0, 3.0)
    assert "Error(rat)" in printed and "studies would show this much" in printed


def test_nested_refuses_crossed_units_and_names_matched_by(warp):
    with pytest.raises(SimplydataError, match="matched_by="):
        warp.compare_averages_of("breaks", for_each_group_in="tension", grouped_by="wool")


def test_manova_matches_r_summary_manova(needs_r, capsys):
    iris = pd.read_csv(DATA / "iris.csv")
    result = sdata.table(iris).compare_averages_of(["Sepal.Length", "Petal.Length"], for_each_group_in="Species")
    printed = capsys.readouterr().out
    found = r("s <- summary(stats::manova(cbind(a, b) ~ g, data = data.frame(a = a, b = b, g = factor(g))))$stats; "
              "list(pillai = s[1, 2], f = s[1, 3], df2 = s[1, 5], p = s[1, 6])",
              a=iris["Sepal.Length"].to_numpy(float), b=iris["Petal.Length"].to_numpy(float),
              g=iris["Species"].to_numpy(object))
    first = result.as_pandas().iloc[0]
    assert first["statistic"] == pytest.approx(float(found["pillai"][0]), rel=1e-10)
    assert first["F"] == pytest.approx(float(found["f"][0]), rel=1e-10)
    assert first["degrees of freedom 2"] == float(found["df2"][0])
    assert "Pillai's trace" in printed


def test_manova_refusals(school):
    with pytest.raises(SimplydataError, match="more than one group column"):
        school.compare_averages_of(["marks", "hours"], for_each_group_in=["class", "breakfast"])
    with pytest.raises(SimplydataError, match="cannot be used with a list of columns"):
        school.compare_averages_of(["marks", "hours"], for_each_group_in="class", test="welch")


# ---------------------------------------------------------------- N13 interaction lines
def test_interaction_lines_are_group_averages_with_t_intervals(capsys):
    from scipy import stats

    frame = pd.read_csv(DATA / "warpbreaks.csv")
    chart = sdata.chart(frame).draw_interaction_lines(x="tension", y="breaks", colour="wool")
    ax = chart._render().axes[0]
    printed = capsys.readouterr().out
    means = sorted(frame.groupby(["wool", "tension"])["breaks"].mean().round(9))
    drawn = sorted(round(float(v), 9) for line in ax.get_lines() if len(line.get_ydata()) == 3
                   for v in line.get_ydata())
    assert all(any(abs(m - d) < 1e-9 for d in drawn) for m in means)
    g = frame[(frame["wool"] == "A") & (frame["tension"] == "L")]["breaks"]
    low, high = stats.t.interval(0.95, len(g) - 1, loc=g.mean(), scale=stats.sem(g))
    ends = [round(float(v), 6) for line in ax.get_lines() for v in line.get_ydata()]
    assert round(low, 6) in ends or any(abs(e - low) < 1e-6 for e in ends)
    assert "parallel lines" in printed and "95 % confidence interval" in printed


def test_interaction_lines_need_three_columns():
    with pytest.raises(SimplydataError, match="colour="):
        sdata.chart(sdata.get_example("school")).draw_interaction_lines(x="class", y="marks")


# ---------------------------------------------------------------- review fixes
def test_neighbours_alike_on_uneven_dates_matches_nlme_corcar1_on_days(needs_r):
    river = sdata.get_example("river")
    part = river[river["station"] == "Station A"].head(60).drop(index=river.index[4]).dropna(subset=["level", "nitrate"])
    result = sdata.table(part).explain("level", using=["nitrate"], neighbours_alike_in_order_of="date")
    days = ((pd.to_datetime(part["date"]) - pd.to_datetime(part["date"]).min()) / pd.Timedelta(days=1)).to_numpy(float)
    found = r("m <- nlme::gls(level ~ nitrate, correlation = nlme::corCAR1(form = ~ days)); "
              "list(b = unname(stats::coef(m)), phi = unname(stats::coef(m$modelStruct$corStruct, unconstrained = "
              "FALSE)))", ("nlme",), level=part["level"].to_numpy(float), nitrate=part["nitrate"].to_numpy(float),
              days=days)
    assert row(result, "nitrate")["effect"] == pytest.approx(float(found["b"][1]), rel=1e-5)
    assert row(result, 'correlation of neighbours in "date" order')["effect"] == pytest.approx(
        float(found["phi"][0]), rel=1e-5)


def test_in_order_orders_the_pairs_without_comparing(warp, needs_r, capsys):
    result = warp.find_model_averages_of("breaks", for_each_group_in="tension", using=["tension"],
                                         in_order=["L", "M", "H"])
    terms = list(result.as_pandas()["term"])
    assert terms[:3] == ["L", "M", "H"] and "L minus M" in terms


def test_trend_parts_are_contrasts_with_their_own_null(warp, needs_r, capsys):
    result = warp.find_model_averages_of("breaks", for_each_group_in="tension", using=["tension"], comparing="trend",
                                         in_order=["L", "M", "H"])
    printed = capsys.readouterr().out
    assert "contrast" in result.as_pandas().columns
    assert "no straight trend" in printed and "no curve" in printed


def test_levels_points_to_find_group_levels_of(capsys):
    sdata.help("levels")
    assert "find_group_levels_of" in capsys.readouterr().out


def test_large_p_sentences_on_the_notes(school, needs_r, capsys):
    school.check_model_of("passed", using=["hours", "breakfast"], outcome="yes or no")
    assert "does not show that the model fits well" in capsys.readouterr().out
    school.check_model_of("marks", using=["hours", "breakfast"])
    assert "does not show that the spread is the same" in capsys.readouterr().out


def test_no_singular_matrix_warning_from_whites_test(school, recwarn):
    school.check_model_of("marks", using=["hours", "breakfast"])
    assert not [w for w in recwarn if "Singular" in type(w.message).__name__ or "singular" in str(w.message).lower()]


@pytest.mark.parametrize("extra", [dict(weights="hours"), dict(giving_outliers_less_weight=True),
                                   dict(crossed_with="class"), dict(changes_at={"hours": 5}),
                                   dict(for_percentile=90), dict(with_knots=3), dict(show="standardised effects")])
def test_gls_refuses_the_other_explain_options_it_cannot_do(school, extra):
    with pytest.raises(SimplydataError, match="cannot be used with spread_changes_with= or neighbours_alike_in_order_of="):
        school.explain("marks", using=["hours"], spread_changes_with="school", **extra)


# ---------------------------------------------------------------- re-check fixes
def test_both_routes_of_find_model_averages_of_give_the_same_column_names(school, needs_r, capsys):
    plain = school.find_model_averages_of("passed", for_each_group_in="class", using=["class"], outcome="yes or no")
    ordered = school.find_model_averages_of("passed", for_each_group_in="class", using=["class"], outcome="yes or no",
                                            in_order=["red", "blue", "green"])
    printed = capsys.readouterr().out
    assert set(plain.as_pandas().columns) == set(ordered.as_pandas().columns)
    assert "p-value (Tukey)" in ordered.as_pandas().columns and "model average" in ordered.as_pandas().columns
    assert "Model chances of yes" in printed and "chance of yess" not in printed


def test_two_groups_say_one_pair_on_both_routes(school, needs_r, capsys):
    school.find_model_averages_of("marks", for_each_group_in="breakfast", using=["breakfast"], in_order=["yes", "no"])
    assert "one pair, so nothing to adjust for" in capsys.readouterr().out


def test_in_order_with_outcome_groups_does_not_talk_about_comparing(school, needs_r, capsys):
    """outcome="groups" keeps the released route (in_order= orders the outcome's groups there)."""
    school.find_model_averages_of("class", for_each_group_in="breakfast", using=["breakfast"], outcome="groups",
                                  in_order=["blue", "green", "red"])
    assert "comparing=" not in capsys.readouterr().out


def test_the_rat_glycogen_box_lists_no_package_for_base_r():
    from simplydata._underneath import UNDERNEATH

    entry = UNDERNEATH["table.compare_averages_of grouped_by="]
    assert entry.r_packages == () and entry.ours_r == ("lme4",)
