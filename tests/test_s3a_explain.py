"""S3a-1: explain() grows. Each new option against the package underneath (statsmodels, SciPy, patsy) and,
where R is installed, against R itself (the R numbers are worked out by R in the test, from the same rows).

Real data from validation/data (galton_peas, crowder_seeds, infert, birthwt, stackloss, mtcars, penicillin,
nmes1988; sources and licences in validation/README.md); the practice tables for the printouts; made-up rows
only for edge cases, labelled as such.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError

DATA = Path(__file__).resolve().parents[1] / "validation" / "data"


def read(name):
    return pd.read_csv(DATA / f"{name}.csv")


def rows(result, key="term"):
    frame = result.as_pandas()
    return {r[key] if isinstance(key, str) else tuple(r[k] for k in key): r for r in frame.to_dict("records")}


def school():
    s = sdata.get_example("school")
    s["w"] = (np.arange(len(s)) % 4 + 1).astype(float)
    return s


def r(code, packages=(), **values):
    from simplydata._r import r_call

    return r_call(code, packages=packages, what="the test's own R check", **values)


def X_of(*columns):
    return np.column_stack([np.ones(len(columns[0]))] + [np.asarray(c, dtype=float) for c in columns])


# ---------------------------------------------------------------- weights= (J06)
def test_weights_numbers_match_statsmodels_wls(capsys):
    s = school()
    got = rows(sdata.table(s).explain("marks", using=["hours", "breakfast"], weights="w"))
    out = capsys.readouterr().out
    import statsmodels.api as sm

    X = X_of(s.hours, s.breakfast == "yes")
    fit = sm.WLS(s.marks.to_numpy(float), X, weights=s.w.to_numpy(float)).fit()
    assert got["hours"]["effect"] == pytest.approx(fit.params[1], rel=1e-10)
    assert got["hours"]["standard error"] == pytest.approx(fit.bse[1], rel=1e-10)
    assert got["breakfast (yes)"]["p-value"] == pytest.approx(fit.pvalues[2], rel=1e-8)
    assert f"R squared = {fit.rsquared:.3f}" in out
    assert "lm(marks ~ hours + breakfast, weights = w)" in out and "precision weights" in out


def test_weights_match_r_lm_and_glm(needs_r, capsys):
    s = school()
    t = sdata.table(s)
    lm = rows(t.explain("marks", using=["hours", "breakfast"], weights="w"))
    out = capsys.readouterr().out
    pois = rows(t.explain("days_absent", using=["hours", "school"], outcome="counts", weights="w"))
    gamma_out = capsys.readouterr().out
    gamma = rows(t.explain("marks", using=["hours"], outcome="positive numbers", weights="w"))
    gamma_out = capsys.readouterr().out
    quasi = rows(t.explain("days_absent", using=["hours"], outcome="counts (overdispersed)", weights="w"))
    capsys.readouterr()
    found = r("d <- data.frame(m = m, h = h, b = b, a = a, s = s, w = w); "
              "f1 <- lm(m ~ h + b, data = d, weights = w); f2 <- glm(a ~ h + s, data = d, family = poisson, weights = w); "
              "f3 <- glm(m ~ h, data = d, family = Gamma(link = 'log'), weights = w); "
              "list(b1 = coef(f1), se1 = sqrt(diag(vcov(f1))), aic1 = AIC(f1), b2 = coef(f2), se2 = sqrt(diag(vcov(f2))), "
              "b3 = coef(f3), se3 = sqrt(diag(vcov(f3))), aic3 = AIC(f3), "
              "se4 = sqrt(diag(vcov(glm(a ~ h, data = d, family = quasipoisson, weights = w)))))",
              m=s.marks.to_numpy(float), h=s.hours.to_numpy(float), b=s.breakfast.astype(str).to_numpy(object),
              a=s.days_absent.to_numpy(float), s=s.school.astype(str).to_numpy(object), w=s.w.to_numpy(float))
    assert lm["hours"]["effect"] == pytest.approx(found["b1"][1], rel=1e-9)
    assert lm["breakfast (yes)"]["standard error"] == pytest.approx(found["se1"][2], rel=1e-9)
    assert f"AIC {round(float(found['aic1'][0]))}" in out
    assert pois["hours"]["log rate ratio"] == pytest.approx(found["b2"][1], rel=1e-7)
    assert pois["school (School L)"]["standard error"] == pytest.approx(found["se2"][-1], rel=1e-6)
    assert gamma["hours"]["log ratio of averages"] == pytest.approx(found["b3"][1], rel=1e-6)
    assert gamma["hours"]["standard error"] == pytest.approx(found["se3"][1], rel=1e-5)
    assert f"AIC {round(float(found['aic3'][0]))}" in gamma_out
    assert quasi["hours"]["standard error"] == pytest.approx(found["se4"][1], rel=1e-6)


def test_weights_leave_out_zero_weights_as_r_and_refuse_bad_ones(capsys):
    # made-up edge case: two rows with weight 0
    d = pd.DataFrame({"x": [1.0, 2, 3, 4, 5, 6, 7, 8], "y": [2.1, 3.9, 6.2, 8.1, 9.7, 12.2, 30.0, 31.0],
                      "w": [1.0, 2, 1, 2, 1, 2, 0, 0]})
    got = rows(sdata.table(d).explain("y", using=["x"], weights="w"))
    out = capsys.readouterr().out
    alone = rows(sdata.table(d.iloc[:6]).explain("y", using=["x"], weights="w"))
    assert got["x"]["degrees of freedom"] == 4 == alone["x"]["degrees of freedom"]
    assert got["x"]["standard error"] == pytest.approx(alone["x"]["standard error"], rel=1e-12)
    assert "2 rows with weight 0 were left out" in out
    with pytest.raises(SimplydataError, match="negative values"):
        sdata.table(d.assign(w=[1.0, -1, 1, 1, 1, 1, 1, 1])).explain("y", using=["x"], weights="w")
    with pytest.raises(SimplydataError, match="needs a column of numbers"):
        sdata.table(d.assign(w=list("abcdefgh"))).explain("y", using=["x"], weights="w")
    with pytest.raises(SimplydataError, match="grouped_by= yet"):
        sdata.table(school()).explain("marks", using=["hours"], weights="w", grouped_by="school")
    with pytest.raises(SimplydataError, match="number of tries"):
        sdata.table(read("crowder_seeds").assign(w=1.0)).explain("germ", using=["extract"], outcome="yes or no",
                                                                 out_of="n", weights="w")
    with pytest.raises(SimplydataError, match="cannot be weights= and also be"):
        sdata.table(d).explain("y", using=["x", "w"], weights="w")


# ---------------------------------------------------------------- outcome="yes or no (overdispersed)" (K07)
def test_quasi_binomial_matches_statsmodels_and_r(needs_r, capsys):
    c = read("crowder_seeds")
    got = rows(sdata.table(c).explain("germ", using=["gen * extract"], outcome="yes or no (overdispersed)",
                                      out_of="n"))
    out = capsys.readouterr().out
    found = r("m <- glm(cbind(g, n - g) ~ gen * ext, family = quasibinomial); s <- summary(m); "
              "list(b = coef(m), se = s$coefficients[, 2], p = s$coefficients[, 4], disp = s$dispersion)",
              g=c.germ.to_numpy(float), n=c.n.to_numpy(float), gen=c.gen.to_numpy(object),
              ext=c.extract.to_numpy(object))
    for label, j in (("(intercept)", 0), ("gen (O75)", 1), ("extract (cucumber)", 2),
                     ("gen (O75) : extract (cucumber)", 3)):
        assert got[label]["log odds ratio"] == pytest.approx(found["b"][j], rel=1e-7)
        assert got[label]["standard error"] == pytest.approx(found["se"][j], rel=1e-6)
        assert got[label]["p-value"] == pytest.approx(found["p"][j], rel=1e-5)
    assert f"dispersion {float(found['disp'][0]):.3g}" in out and "family = quasibinomial" in out
    assert "no AIC" in out


def test_quasi_binomial_against_statsmodels_without_r():
    import statsmodels.api as sm

    c = read("crowder_seeds")
    got = rows(sdata.table(c).explain("germ", using=["extract"], outcome="yes or no (overdispersed)", out_of="n"))
    X = X_of(c.extract == "cucumber")
    fit = sm.GLM((c.germ / c.n).to_numpy(float), X, family=sm.families.Binomial(),
                 var_weights=c.n.to_numpy(float)).fit(scale="X2")
    assert got["extract (cucumber)"]["standard error"] == pytest.approx(fit.bse[1], rel=1e-8)


def test_binomial_out_of_points_to_quasi_binomial_and_needs_tries(capsys):
    c = read("crowder_seeds")
    sdata.table(c).explain("germ", using=["gen * extract"], outcome="yes or no", out_of="n")
    out = capsys.readouterr().out
    assert 'outcome="yes or no (overdispersed)"' in out and "residual deviance / df = 1.96" in out
    with pytest.raises(SimplydataError, match="out_of="):
        sdata.table(c).explain("germ", using=["extract"], outcome="yes or no (overdispersed)")
    with pytest.raises(SimplydataError, match="fits outcome"):
        sdata.table(c).add_predicted_column("germ", using=["extract"], outcome="yes or no (overdispersed)")


# ---------------------------------------------------------------- matched_by= (K16)
def test_conditional_logistic_matches_statsmodels_and_r(needs_r, capsys):
    from statsmodels.discrete.conditional_models import ConditionalLogit

    i = read("infert")
    got = rows(sdata.table(i).explain("case", using=["spontaneous", "induced"], outcome="yes or no",
                                      matched_by="stratum"))
    out = capsys.readouterr().out
    fit = ConditionalLogit(i.case.to_numpy(float), i[["spontaneous", "induced"]].to_numpy(float),
                           groups=i.stratum.to_numpy()).fit(disp=0)
    assert got["spontaneous"]["log odds ratio"] == pytest.approx(fit.params[0], rel=1e-5)
    found = r("m <- survival::clogit(case ~ sp + ind + strata(st), method = 'exact'); s <- summary(m); "
              "list(b = coef(m), se = s$coefficients[, 3], aic = AIC(m), lr = s$logtest[1])", packages=("survival",),
              case=i.case.to_numpy(float), sp=i.spontaneous.to_numpy(float), ind=i.induced.to_numpy(float),
              st=i.stratum.to_numpy(float))
    assert got["spontaneous"]["log odds ratio"] == pytest.approx(found["b"][0], rel=1e-6)
    assert got["induced"]["standard error"] == pytest.approx(found["se"][1], rel=1e-5)
    assert "(intercept)" not in got
    assert f"likelihood-ratio chi-square = {float(found['lr'][0]):.3g}" in out
    assert f"AIC {round(float(found['aic'][0]))}" in out and "strata(stratum)" in out


def test_matched_sets_leave_out_sets_without_both_and_refuse_flat_columns(capsys):
    # made-up edge case: set 3 has no case, so it adds nothing (as R clogit)
    d = pd.DataFrame({"set": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7],
                      "case": [1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
                      "dose": [3.0, 1, 2, 2.5, 1, 2, 4, 1, 2, 3, 5, 2, 1, 0.5],
                      "site": ["a", "a", "b", "b", "c", "c", "a", "a", "b", "b", "c", "c", "a", "a"]})
    got = rows(sdata.table(d).explain("case", using=["dose"], outcome="yes or no", matched_by="set"))
    out = capsys.readouterr().out
    assert "1 sets of" in out and "left out (2 rows)" in out and "within 6 matched sets" in out
    alone = rows(sdata.table(d[d.set != 3]).explain("case", using=["dose"], outcome="yes or no", matched_by="set"))
    assert got["dose"]["log odds ratio"] == pytest.approx(alone["dose"]["log odds ratio"], rel=1e-10)
    with pytest.raises(SimplydataError, match='do not change within any set|does not change within any set'):
        sdata.table(d).explain("case", using=["site"], outcome="yes or no", matched_by="set")
    with pytest.raises(SimplydataError, match='goes with outcome="yes or no"'):
        sdata.table(d).explain("dose", using=["case"], matched_by="set")


# ---------------------------------------------------------------- show="risk ratios" (K18)
def test_risk_ratios_match_modified_poisson_and_the_two_by_two_table(capsys):
    import statsmodels.api as sm

    b = read("birthwt")
    got = rows(sdata.table(b).explain("low", using=["smoke"], outcome="yes or no", show="risk ratios"))
    out = capsys.readouterr().out
    smokers, others = b[b.smoke == 1].low.mean(), b[b.smoke == 0].low.mean()
    assert got["smoke"]["risk ratio"] == pytest.approx(smokers / others, rel=1e-9)  # the 2 x 2 risk ratio
    two = rows(sdata.table(b).explain("low", using=["smoke", "age"], outcome="yes or no", show="risk ratios"))
    fit = sm.GLM(b.low.to_numpy(float), X_of(b.smoke, b.age), family=sm.families.Poisson()).fit(cov_type="HC0")
    assert two["smoke"]["log risk ratio"] == pytest.approx(fit.params[1], rel=1e-8)
    assert two["age"]["standard error"] == pytest.approx(fit.bse[2], rel=1e-5)
    assert "modified Poisson" in out and 'type = "HC0"' in out and "risk ratio" in out


def test_risk_ratios_match_r_sandwich_and_log_binomial(needs_r, capsys):
    b = read("birthwt")
    got = rows(sdata.table(b).explain("low", using=["smoke", "age"], outcome="yes or no", show="risk ratios"))
    lb = rows(sdata.table(b).explain("low", using=["smoke", "age"], outcome="yes or no", show="risk ratios",
                                     method="log-binomial"))
    out = capsys.readouterr().out
    found = r("m <- glm(y ~ s + a, family = poisson); v <- sandwich::vcovHC(m, type = 'HC0'); "
              "l <- glm(y ~ s + a, family = binomial(link = 'log')); "
              "list(b = coef(m), se = sqrt(diag(v)), lb = coef(l), lse = sqrt(diag(vcov(l))))",
              packages=("sandwich",), y=b.low.to_numpy(float), s=b.smoke.to_numpy(float), a=b.age.to_numpy(float))
    assert got["smoke"]["log risk ratio"] == pytest.approx(found["b"][1], rel=1e-7)
    assert got["smoke"]["standard error"] == pytest.approx(found["se"][1], rel=1e-5)
    assert lb["smoke"]["log risk ratio"] == pytest.approx(found["lb"][1], rel=1e-5)
    assert lb["age"]["standard error"] == pytest.approx(found["lse"][2], rel=1e-5)
    assert 'binomial(link = "log")' in out


def test_odds_ratio_note_when_yes_is_common_and_risk_ratio_refusals(capsys):
    sdata.table(sdata.get_example("school")).explain("passed", using=["hours"], outcome="yes or no")
    out = capsys.readouterr().out
    assert "an odds ratio is not a risk ratio here" in out and 'show="risk ratios"' in out
    with pytest.raises(SimplydataError, match='is for outcome="yes or no"'):
        sdata.table(sdata.get_example("school")).explain("marks", using=["hours"], show="risk ratios")
    with pytest.raises(SimplydataError, match='goes with show="risk ratios"'):
        sdata.table(sdata.get_example("school")).explain("passed", using=["hours"], outcome="yes or no",
                                                         method="log-binomial")
    with pytest.raises(SimplydataError, match="show= is one of"):
        sdata.table(sdata.get_example("school")).explain("passed", using=["hours"], outcome="yes or no",
                                                         show="hazard ratios")


# ---------------------------------------------------------------- giving_outliers_less_weight= (L02)
def test_huber_matches_statsmodels_rlm(capsys):
    import statsmodels.api as sm

    s = read("stackloss")
    got = rows(sdata.table(s).explain("stack_loss", using=["air_flow", "water_temp", "acid_conc"],
                                      giving_outliers_less_weight=True))
    out = capsys.readouterr().out
    fit = sm.RLM(s.stack_loss.to_numpy(float), X_of(s.air_flow, s.water_temp, s.acid_conc),
                 M=sm.robust.norms.HuberT()).fit(scale_est="mad", cov="H1", tol=1e-10, maxiter=200)
    for j, label in enumerate(["(intercept)", "air_flow", "water_temp", "acid_conc"]):
        assert got[label]["effect"] == pytest.approx(fit.params[j], rel=1e-9)
        assert got[label]["standard error"] == pytest.approx(fit.bse[j], rel=1e-9)
    assert "row 21 (weight 0.37)" in out and "row 4 (weight 0.50)" in out and "MASS::rlm(" in out
    assert "Huber" in out and "show_rows_that_pull_model" in out


def test_huber_matches_r_mass_rlm(needs_r):
    s = read("stackloss")
    got = rows(sdata.table(s).explain("stack_loss", using=["air_flow", "water_temp", "acid_conc"],
                                      giving_outliers_less_weight=True))
    found = r("m <- MASS::rlm(y ~ a + w + c, acc = 1e-12, maxit = 200); list(b = coef(m), se = summary(m)$coefficients[, 2])",
              packages=("MASS",), y=s.stack_loss.to_numpy(float), a=s.air_flow.to_numpy(float),
              w=s.water_temp.to_numpy(float), c=s.acid_conc.to_numpy(float))
    for j, label in enumerate(["(intercept)", "air_flow", "water_temp", "acid_conc"]):
        assert got[label]["effect"] == pytest.approx(found["b"][j], rel=1e-5)
        # summary.rlm's small-sample correction differs a little from Huber's H1 (said in the printout)
        assert got[label]["standard error"] == pytest.approx(found["se"][j], rel=5e-3)


def test_huber_refusals():
    t = sdata.table(sdata.get_example("school"))
    with pytest.raises(SimplydataError, match='is for outcome="numbers"'):
        t.explain("passed", using=["hours"], outcome="yes or no", giving_outliers_less_weight=True)
    with pytest.raises(SimplydataError, match="True or False"):
        t.explain("marks", using=["hours"], giving_outliers_less_weight="yes")


# ---------------------------------------------------------------- with_knots= (L04)
def test_knots_give_the_curves_of_r_ns(needs_r, capsys):
    s = sdata.get_example("school")
    got = rows(sdata.table(s).explain("marks", using=["hours", "breakfast"], curve_for="hours", with_knots=3))
    out = capsys.readouterr().out
    found = r("d <- data.frame(m = m, h = h, b = b); f <- lm(m ~ splines::ns(h, df = 4) + b, data = d); "
              "g <- lm(m ~ b, data = d); a <- anova(g, f); "
              "list(b = coef(f), se = sqrt(diag(vcov(f))), F = a$F[2], p = a[2, 'Pr(>F)'])",
              m=s.marks.to_numpy(float), h=s.hours.to_numpy(float), b=s.breakfast.astype(str).to_numpy(object))
    assert got["breakfast (yes)"]["effect"] == pytest.approx(found["b"][-1], rel=1e-9)
    assert got["breakfast (yes)"]["standard error"] == pytest.approx(found["se"][-1], rel=1e-9)
    assert got["hours (whole curve)"]["statistic"] == pytest.approx(found["F"][0], rel=1e-9)
    assert got["hours (whole curve)"]["p-value"] == pytest.approx(found["p"][0], rel=1e-7)
    assert "hours (curve part 1)" not in got and "splines::ns(hours, df = 4)" in out
    assert "the points where the pieces of the curve join" in out


def test_knots_are_patsy_natural_splines_without_r():
    import statsmodels.api as sm
    from patsy import dmatrix

    s = sdata.get_example("school")
    got = rows(sdata.table(s).explain("marks", using=["hours"], curve_for="hours", with_knots=2))
    x = s.hours.to_numpy(float)
    knots = np.quantile(x, [1 / 3, 2 / 3])  # R ns() places the knots at the quantiles of all the values
    B = np.asarray(dmatrix("cr(x, knots=knots, constraints='center') - 1", {"x": x, "knots": knots}))
    fit = sm.OLS(s.marks.to_numpy(float), np.column_stack([np.ones(len(s)), B])).fit()
    assert got["hours (whole curve)"]["statistic"] == pytest.approx(fit.fvalue, rel=1e-9)
    with pytest.raises(SimplydataError, match="goes with curve_for="):
        sdata.table(s).explain("marks", using=["hours"], with_knots=3)
    with pytest.raises(SimplydataError, match="from 1 to 10"):
        sdata.table(s).explain("marks", using=["hours"], curve_for="hours", with_knots=12)


# ---------------------------------------------------------------- show="standardised effects" (F07)
def test_standardised_effects_match_effectsize(needs_r, capsys):
    m = read("mtcars")
    got = rows(sdata.table(m).explain("mpg", using=["wt", "hp", "am"], show="standardised effects"))
    out = capsys.readouterr().out
    found = r("d <- data.frame(mpg = mpg, wt = wt, hp = hp, am = am); f <- lm(mpg ~ wt + hp + am, data = d); "
              "e <- effectsize::standardize_parameters(f, method = 'refit'); list(v = e$Std_Coefficient, "
              "lo = e$CI_low, hi = e$CI_high)", packages=("effectsize",),
              mpg=m.mpg.to_numpy(float), wt=m.wt.to_numpy(float), hp=m.hp.to_numpy(float), am=m.am.to_numpy(float))
    for j, label in enumerate(["(intercept)", "wt", "hp", "am"]):
        assert got[label]["effect"] == pytest.approx(found["v"][j], rel=1e-8, abs=1e-12)
        assert got[label]["95 % CI low"] == pytest.approx(found["lo"][j], rel=1e-8, abs=1e-12)
    assert "standard deviations" in out and "Greenland" in out and f'"wt" {m.wt.std():.3g}' in out


def test_standardised_effects_of_a_glm_refit_on_z_scores():
    import statsmodels.api as sm

    s = sdata.get_example("school").dropna(subset=["sleep"])
    got = rows(sdata.table(s).explain("passed", using=["hours", "sleep"], outcome="yes or no",
                                      show="standardized effects"))
    def z(v):
        return (v - v.mean()) / v.std(ddof=1)
    fit = sm.GLM((s.passed.astype(str) == "yes").to_numpy(float), X_of(z(s.hours), z(s.sleep)),
                 family=sm.families.Binomial()).fit()
    assert got["hours"]["log odds ratio"] == pytest.approx(fit.params[1], rel=1e-8)
    with pytest.raises(SimplydataError, match="grouped_by="):
        sdata.table(s).explain("marks", using=["hours"], grouped_by="school", show="standardised effects")


# ---------------------------------------------------------------- interval_by="bootstrap" (H07)
def test_bootstrap_intervals_are_scipys_bca_of_the_refits(capsys):
    import statsmodels.api as sm
    from scipy import stats

    s = read("stackloss")
    got = rows(sdata.table(s).explain("stack_loss", using=["air_flow"], interval_by="bootstrap", resamples=999,
                                      with_seed=3))
    out = capsys.readouterr().out
    X, y = X_of(s.air_flow), s.stack_loss.to_numpy(float)
    res = stats.bootstrap((np.arange(len(y)),), lambda i: sm.OLS(y[i.astype(int)], X[i.astype(int)]).fit().params,
                          n_resamples=999, method="BCa", vectorized=False, rng=np.random.default_rng(3))
    assert got["air_flow"]["95 % CI low"] == pytest.approx(res.confidence_interval.low[1], rel=1e-9)
    assert got["air_flow"]["95 % CI high"] == pytest.approx(res.confidence_interval.high[1], rel=1e-9)
    assert "999 times (with_seed=3)" in out and "BCa" in out
    with pytest.raises(SimplydataError, match='goes with interval_by="bootstrap"|for interval_by="bootstrap"'):
        sdata.table(s).explain("stack_loss", using=["air_flow"], resamples=999)
    with pytest.raises(SimplydataError, match="grouped_by="):
        sdata.table(sdata.get_example("school")).explain("marks", using=["hours"], grouped_by="school",
                                                         interval_by="bootstrap")


# ---------------------------------------------------------------- interval_by="profile", p_value_by="likelihood ratio" (O17)
def test_profile_intervals_and_likelihood_ratio_tests_match_r(needs_r, capsys):
    b = read("birthwt")
    b["race"] = b.race.map({1: "white", 2: "black", 3: "other"})
    t = sdata.table(b)
    prof = rows(t.explain("low", using=["smoke", "age", "race"], outcome="yes or no", interval_by="profile"))
    lr = rows(t.explain("low", using=["smoke", "age", "race"], outcome="yes or no", p_value_by="likelihood ratio"))
    out = capsys.readouterr().out
    found = r("race <- factor(race, levels = c('black', 'other', 'white')); "
              "m <- glm(low ~ smoke + age + race, family = binomial); ci <- confint(m); d <- drop1(m, test = 'LRT'); "
              "list(lo = ci[, 1], hi = ci[, 2], p = d[['Pr(>Chi)']])",
              low=b.low.to_numpy(float), smoke=b.smoke.to_numpy(float), age=b.age.to_numpy(float),
              race=b.race.to_numpy(object))
    assert np.log(prof["smoke"]["95 % CI low"]) == pytest.approx(found["lo"][1], rel=1e-6)
    assert np.log(prof["age"]["95 % CI high"]) == pytest.approx(found["hi"][2], rel=1e-6)
    assert lr["smoke"]["p-value"] == pytest.approx(found["p"][1], rel=1e-7)
    assert lr["age"]["p-value"] == pytest.approx(found["p"][2], rel=1e-7)
    assert lr["race (whole column)"]["p-value"] == pytest.approx(found["p"][3], rel=1e-7)
    assert "profile-likelihood" in out and 'drop1(m, test = "LRT")' in out and 'the groups of "race"' in out


def test_likelihood_ratio_tests_against_statsmodels_refits():
    import statsmodels.api as sm
    from scipy import stats

    b = read("birthwt")
    lr = rows(sdata.table(b).explain("low", using=["smoke", "age"], outcome="yes or no",
                                     p_value_by="likelihood ratio"))
    y = b.low.to_numpy(float)
    full = sm.GLM(y, X_of(b.smoke, b.age), family=sm.families.Binomial()).fit()
    small = sm.GLM(y, X_of(b.age), family=sm.families.Binomial()).fit()
    assert lr["smoke"]["p-value"] == pytest.approx(stats.chi2.sf(small.deviance - full.deviance, 1), rel=1e-8)
    with pytest.raises(SimplydataError, match="likelihood ratio"):
        sdata.table(b).explain("bwt", using=["smoke"], p_value_by="likelihood ratio")
    with pytest.raises(SimplydataError, match='interval_by="profile" works'):
        sdata.table(b).explain("bwt", using=["smoke"], interval_by="profile")


# ---------------------------------------------------------------- Nagelkerke and Tjur (O11)
def test_nagelkerke_and_tjur_match_r_performance(needs_r, capsys):
    b = read("birthwt")
    sdata.table(b).explain("low", using=["smoke", "age"], outcome="yes or no")
    out = capsys.readouterr().out
    found = r("d <- data.frame(y = y, s = s, a = a); m <- glm(y ~ s + a, family = binomial, data = d); "
              "list(n = unname(unlist(performance::r2_nagelkerke(m))), t = unname(unlist(performance::r2_tjur(m))))",
              packages=("performance",), y=b.low.to_numpy(float), s=b.smoke.to_numpy(float),
              a=b.age.to_numpy(float))
    assert f"Nagelkerke {float(found['n'][0]):.3f}, Tjur {float(found['t'][0]):.3f}" in out


def test_nagelkerke_and_tjur_from_statsmodels(capsys):
    import statsmodels.api as sm

    b = read("birthwt")
    sdata.table(b).explain("low", using=["smoke"], outcome="yes or no")
    out = capsys.readouterr().out
    y = b.low.to_numpy(float)
    fit = sm.GLM(y, X_of(b.smoke), family=sm.families.Binomial()).fit()
    nagelkerke = fit.pseudo_rsquared("cs") / (1 - np.exp(2 * fit.llnull / len(y)))
    tjur = fit.fittedvalues[y == 1].mean() - fit.fittedvalues[y == 0].mean()
    assert f"Nagelkerke {nagelkerke:.3f}, Tjur {tjur:.3f}" in out and "none is a share explained" in out


# ---------------------------------------------------------------- crossed_with= (M05)
def test_crossed_groups_match_lme4(needs_r, capsys):
    s = sdata.get_example("school")
    got = rows(sdata.table(s).explain("marks", using=["hours"], grouped_by="school", crossed_with="class"))
    out = capsys.readouterr().out
    satt = rows(sdata.table(s).explain("marks", using=["hours"], grouped_by="school", crossed_with="class",
                                       p_value_by="satterthwaite"))
    keep = s.marks.notna() & s.hours.notna()
    found = r("m <- lmerTest::lmer(y ~ x + (1 | g) + (1 | c)); v <- as.data.frame(lme4::VarCorr(m)); "
              "s <- summary(m)$coefficients; list(b = lme4::fixef(m), se = s[, 2], df = s[, 3], v = v$vcov, g = v$grp)",
              packages=("lme4", "lmerTest"), y=s.marks[keep].to_numpy(float), x=s.hours[keep].to_numpy(float),
              g=s.school[keep].astype(str).to_numpy(object), c=s["class"][keep].astype(str).to_numpy(object))
    variances = dict(zip([str(g) for g in found["g"]], np.asarray(found["v"], dtype=float)))
    assert got["hours"]["effect"] == pytest.approx(found["b"][1], rel=1e-6)
    assert got["hours"]["standard error"] == pytest.approx(found["se"][1], rel=1e-5)
    assert satt["hours"]["degrees of freedom"] == pytest.approx(found["df"][1], rel=1e-4)
    assert f"{variances['c']:.3g}" in out and f"{variances['g']:.3g}" in out
    assert '12 groups in "school" and 3 in "class"' in out and "(1 | school) + (1 | class)" in out
    assert 'only 3 groups in "class"' in out


def test_crossed_groups_for_yes_or_no_match_glmer(needs_r, capsys):
    s = sdata.get_example("school")
    got = rows(sdata.table(s).explain("passed", using=["hours"], outcome="yes or no", grouped_by="school",
                                      crossed_with="class"))
    out = capsys.readouterr().out
    keep = s.passed.notna() & s.hours.notna()
    found = r("m <- lme4::glmer(y ~ x + (1 | g) + (1 | c), family = binomial); "
              "list(b = lme4::fixef(m), se = sqrt(diag(as.matrix(vcov(m)))))", packages=("lme4",),
              y=(s.passed[keep].astype(str) == "yes").to_numpy(float), x=s.hours[keep].to_numpy(float),
              g=s.school[keep].astype(str).to_numpy(object), c=s["class"][keep].astype(str).to_numpy(object))
    assert got["hours"]["log odds ratio"] == pytest.approx(found["b"][1], rel=1e-6)
    assert got["hours"]["standard error"] == pytest.approx(found["se"][1], rel=1e-5)
    assert "lme4::glmer(passed ~ hours + (1 | school) + (1 | class)" in out


def test_crossed_with_needs_grouped_by_and_one_grouping():
    t = sdata.table(sdata.get_example("school"))
    with pytest.raises(SimplydataError, match='grouped_by="subject", crossed_with="class"'):
        t.explain("marks", using=["hours"], crossed_with="class")
    with pytest.raises(SimplydataError, match="groups inside groups"):
        t.explain("marks", using=["hours"], grouped_by=["school", "class"], crossed_with="pupil")
    with pytest.raises(SimplydataError, match="GEE"):
        t.explain("marks", using=["hours"], grouped_by="school", crossed_with="class",
                  effects="for the whole population")


# ---------------------------------------------------------------- the zero outcomes (K10, K11) and zero_part_using=
NMES = ["hospital", "health", "chronic", "gender", "school", "insurance"]


def test_hurdle_gives_the_published_nmes_numbers(needs_r, capsys):
    n = read("nmes1988")
    got = rows(sdata.table(n).explain("visits", using=NMES, outcome="counts in two steps that vary a lot"),
               key=("part", "term"))
    out = capsys.readouterr().out
    # Zeileis, Kleiber & Jackman (2008), JSS 27(8), summary(fm_hurdle0): the count part and the zero hurdle
    count = {"(intercept)": (1.197699, 0.058973), "hospital": (0.211898, 0.021396), "health (poor)": (0.315958, 0.048056),
             "health (excellent)": (-0.331861, 0.066093), "chronic": (0.126421, 0.012452),
             "gender (male)": (-0.068317, 0.032416), "school": (0.020693, 0.004535), "insurance (yes)": (0.100172, 0.042619)}
    zero = {"(intercept)": (0.043147, 0.139852), "hospital": (0.312449, 0.091437), "health (poor)": (-0.008716, 0.161024),
            "health (excellent)": (-0.289570, 0.142682), "chronic": (0.535213, 0.045378),
            "gender (male)": (-0.415658, 0.087608), "school": (0.058541, 0.011989), "insurance (yes)": (0.747120, 0.100880)}
    for part, table in (("count", count), ("more than 0", zero)):
        for term, (estimate, se) in table.items():
            assert got[(part, term)]["log ratio"] == pytest.approx(estimate, abs=5e-6), (part, term)
            assert got[(part, term)]["standard error"] == pytest.approx(se, abs=5e-6), (part, term)
    assert "Theta 1.40" in out and "pscl::hurdle(" in out and 'zero.dist = "binomial"' in out


def test_zero_part_using_gives_the_published_table_2(needs_r, capsys):
    n = read("nmes1988")
    zero_cols = ["hospital", "chronic", "insurance", "school", "gender"]
    hurdle = rows(sdata.table(n).explain("visits", using=NMES, outcome="hurdle that vary a lot",
                                         zero_part_using=zero_cols), key=("part", "term"))
    zinb = rows(sdata.table(n).explain("visits", using=NMES, outcome="counts with many zeros that vary a lot",
                                       zero_part_using=zero_cols), key=("part", "term"))
    out = capsys.readouterr().out
    # Table 2 of Zeileis, Kleiber & Jackman (2008): the zero parts of fm_hurdle and fm_zinb, 3 decimals
    for term, h, z in (("(intercept)", 0.016, -0.047), ("hospital", 0.318, -0.800), ("chronic", 0.548, -1.248),
                       ("insurance (yes)", 0.746, -1.176), ("school", 0.057, -0.084), ("gender (male)", -0.419, 0.648)):
        assert hurdle[("more than 0", term)]["log ratio"] == pytest.approx(h, abs=5e-4), term
        assert zinb[("extra zeros", term)]["log ratio"] == pytest.approx(z, abs=5e-4), term
    assert zinb[("count", "hospital")]["log ratio"] == pytest.approx(0.201, abs=5e-4)
    assert ("extra zeros", "health (poor)") not in zinb
    assert "| hospital + chronic + insurance + school + gender" in out


def test_zinb_estimates_match_statsmodels(needs_r):
    from statsmodels.discrete.count_model import ZeroInflatedNegativeBinomialP

    n = read("nmes1988")
    got = rows(sdata.table(n).explain("visits", using=["hospital", "chronic"],
                                      outcome="counts with many zeros that vary a lot",
                                      zero_part_using=["chronic"]), key=("part", "term"))
    X = X_of(n.hospital, n.chronic)
    model = ZeroInflatedNegativeBinomialP(n.visits.to_numpy(float), X, exog_infl=X_of(n.chronic), p=2)
    first = model.fit(method="bfgs", maxiter=2000, disp=0)
    fit = model.fit(start_params=first.params, method="newton", maxiter=100, disp=0)
    assert got[("count", "hospital")]["log ratio"] == pytest.approx(fit.params[3], rel=1e-4)
    assert got[("extra zeros", "chronic")]["log ratio"] == pytest.approx(fit.params[1], rel=1e-4)


def test_zero_outcomes_refuse_counts_without_zeros_and_zero_part_elsewhere():
    d = pd.DataFrame({"n": [1, 2, 3, 4, 5, 6, 7, 8.0], "x": [1, 2, 3, 4, 5, 6, 7, 8.0]})  # made-up, no zeros
    with pytest.raises(SimplydataError, match="no zeros to model"):
        sdata.table(d).explain("n", using=["x"], outcome="counts in two steps")
    with pytest.raises(SimplydataError, match="zero_part_using= names the columns of the zero part"):
        sdata.table(d).explain("n", using=["x"], outcome="counts", zero_part_using=["x"])


# ---------------------------------------------------------------- review fixes (PR #14)
def rare_group_table():
    # made-up edge case: group "b" has only 3 of 40 rows, so some resamples draw none of them
    rng = np.random.default_rng(0)
    g = np.array(["a"] * 37 + ["b"] * 3)
    x = rng.normal(size=40)
    y = 1 + 0.5 * x + (g == "b") * 2 + rng.normal(size=40)
    return pd.DataFrame({"y": y, "x": x, "g": g, "yes": np.where(y > 1.5, "yes", "no")})


@pytest.mark.parametrize("column, outcome", [("y", "numbers"), ("yes", "yes or no")])
def test_bootstrap_refuses_a_group_too_rare_to_resample(column, outcome):
    with pytest.raises(SimplydataError, match=r'"g \(b\)" \(3 of 40 rows\).*cannot be bootstrapped'):
        sdata.table(rare_group_table()).explain(column, using=["x", "g"], outcome=outcome, interval_by="bootstrap",
                                                resamples=999)


def test_weighted_yes_or_no_prints_r_aic_for_whole_weights_and_none_otherwise(needs_r, capsys):
    b = read("birthwt")
    t = sdata.table(b.assign(w=b.ftv + 1, v=b.lwt / 100))
    t.explain("low", using=["smoke", "age"], outcome="yes or no", weights="w")
    whole = capsys.readouterr().out
    found = r("list(aic = AIC(glm(y ~ s + a, family = binomial, weights = w)))", y=b.low.to_numpy(float),
              s=b.smoke.to_numpy(float), a=b.age.to_numpy(float), w=(b.ftv + 1).to_numpy(float))
    assert f"AIC {round(float(found['aic'][0]))}" in whole
    t.explain("low", using=["smoke", "age"], outcome="yes or no", weights="v")
    part = capsys.readouterr().out
    assert "no AIC, BIC or pseudo R squared is printed" in part and "AIC 2" not in part


def test_a_list_of_choices_is_refused_with_both_calls_in_mind():
    t = sdata.table(sdata.get_example("school"))
    with pytest.raises(SimplydataError, match="one choice at a time"):
        t.explain("passed", using=["hours"], outcome="yes or no", show=["risk ratios", "standardised effects"])
    with pytest.raises(SimplydataError, match="one choice at a time"):
        t.explain("passed", using=["hours"], outcome="yes or no", interval_by=["profile"])
    with pytest.raises(SimplydataError, match="method= is one of"):
        t.explain("passed", using=["hours"], outcome="yes or no", show="risk ratios", method="poisson")


def test_likelihood_ratio_rows_hold_the_chi_square_and_the_method_says_so(capsys):
    import statsmodels.api as sm

    b = read("birthwt")
    got = rows(sdata.table(b).explain("low", using=["smoke", "age"], outcome="yes or no",
                                      p_value_by="likelihood ratio", interval_by="bootstrap", resamples=199))
    out = capsys.readouterr().out
    y = b.low.to_numpy(float)
    full = sm.GLM(y, X_of(b.smoke, b.age), family=sm.families.Binomial()).fit()
    small = sm.GLM(y, X_of(b.age), family=sm.families.Binomial()).fit()
    assert got["smoke"]["statistic name"] == "chi-square (likelihood ratio)"
    assert got["smoke"]["statistic"] == pytest.approx(small.deviance - full.deviance, rel=1e-8)
    assert got["smoke"]["degrees of freedom"] == 1 and got["(intercept)"]["statistic name"] == "z"
    method = next(line for line in out.splitlines() if line.startswith("Method:"))
    assert "95 % bootstrap intervals (BCa)" in method and "likelihood-ratio tests" in method
    assert "Wald 95 % intervals" not in method and "The p-values are likelihood-ratio tests" in out


def test_profile_method_line_and_odds_note_without_a_refused_suggestion(needs_r, capsys):
    sdata.table(sdata.get_example("school")).explain("passed", using=["hours"], outcome="yes or no",
                                                     interval_by="profile")
    out = capsys.readouterr().out
    method = next(line for line in out.splitlines() if line.startswith("Method:"))
    assert "profile-likelihood 95 % intervals" in method
    assert "an odds ratio is not a risk ratio here" in out and 'show="risk ratios"' not in out


def test_standardised_effects_leave_out_aic_and_print_a_zero_intercept(capsys):
    sdata.table(read("mtcars")).explain("mpg", using=["wt", "hp"], show="standardised effects")
    out = capsys.readouterr().out
    import re

    assert "intercept: 0 standard deviations" in out and "on z-scores the AIC and BIC" in out
    assert not re.search(r"AIC -?[0-9]", out)


def test_nagelkerke_and_tjur_to_1e_10_of_r_performance(needs_r):
    import statsmodels.api as sm

    from simplydata.table.models_extra import other_pseudo

    b = read("birthwt")
    y = b.low.to_numpy(float)
    fit = sm.GLM(y, X_of(b.smoke, b.age, b.lwt), family=sm.families.Binomial()).fit(tol=1e-12)
    nagelkerke, tjur = other_pseudo(fit, y)
    found = r("m <- glm(y ~ s + a + l, family = binomial, control = glm.control(epsilon = 1e-12)); "
              "list(n = unname(unlist(performance::r2_nagelkerke(m))), t = unname(unlist(performance::r2_tjur(m))))",
              packages=("performance",), y=y, s=b.smoke.to_numpy(float), a=b.age.to_numpy(float),
              l=b.lwt.to_numpy(float))
    assert nagelkerke == pytest.approx(float(found["n"][0]), rel=1e-10)
    assert tjur == pytest.approx(float(found["t"][0]), rel=1e-10)


def test_knots_with_zero_weight_rows_are_placed_as_r_ns(needs_r):
    s = sdata.get_example("school")
    w = np.where(np.arange(len(s)) % 7 == 0, 0.0, 1.0 + np.arange(len(s)) % 3)
    got = rows(sdata.table(s.assign(w=w)).explain("marks", using=["hours", "breakfast"], curve_for="hours",
                                                  with_knots=3, weights="w"))
    found = r("d <- data.frame(m = m, h = h, b = b, w = w); f <- lm(m ~ splines::ns(h, df = 4) + b, data = d, "
              "weights = w); list(b = coef(f), se = sqrt(diag(vcov(f))))",
              m=s.marks.to_numpy(float), h=s.hours.to_numpy(float), b=s.breakfast.astype(str).to_numpy(object), w=w)
    assert got["breakfast (yes)"]["effect"] == pytest.approx(found["b"][-1], rel=1e-9)
    assert got["breakfast (yes)"]["standard error"] == pytest.approx(found["se"][-1], rel=1e-9)


def _method_line(**options):
    import contextlib
    import io

    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        sdata.table(sdata.get_example("school")).explain(using=["hours"], **options)
    return next(line for line in printed.getvalue().splitlines() if line.startswith("Method:"))


def test_method_lines_name_only_the_intervals_used():
    assert _method_line(column="marks", outcome="positive numbers", interval_by="bootstrap", resamples=199) == (
        'Method: Gamma regression with a log link for positive, skewed numbers, as R glm(marks ~ hours, family = '
        'Gamma(link = "log")): each effect multiplies the average (dispersion 0.0356); t-tests as R summary(), 95 % '
        "bootstrap intervals (BCa).")
    assert _method_line(column="days_absent", outcome="counts (overdispersed)", interval_by="bootstrap",
                        resamples=199) == (
        "Method: quasi-Poisson regression, as R glm(days_absent ~ hours, family = quasipoisson): Poisson rate ratios "
        "with standard errors widened for counts that vary more than Poisson allows (dispersion 1.02); t-tests as R "
        "summary(), 95 % bootstrap intervals (BCa).")


def test_profile_method_line_for_counts(needs_r):
    assert _method_line(column="days_absent", outcome="counts", interval_by="profile") == (
        "Method: Poisson regression, as R glm(days_absent ~ hours, family = poisson). profile-likelihood 95 % "
        "intervals (R confint()) and z-tests, as R summary().")


def test_no_risk_ratio_suggestion_beside_standardised_effects(capsys):
    sdata.table(sdata.get_example("school")).explain("passed", using=["hours"], outcome="yes or no",
                                                     show="standardised effects")
    out = capsys.readouterr().out
    assert "an odds ratio is not a risk ratio here" in out and 'show="risk ratios"' not in out
