"""The reliability study for phase S3d-3, Bayesian methods: test_method="bayesian" on compare_averages_of,
compare_before_and_after, compare_average_to, find_correlation_between and compare_counts_of (R BayesFactor), and on
explain (R rstanarm stan_glm and stan_glmer).

cases.py loads this file at its end and calls add_to(), which adds the cases below to its own CASES.

How the numbers are checked:
* The Bayes factors are worked out without random draws, so they are checked against an independent Python version of
  the published formulas: the JZS integral of Rouder et al. (2009, equation 1), done by SciPy quad, and the closed form
  of the Gunel-Dickey Bayes factor for independent multinomial sampling (Jamil et al. 2017), done with SciPy's log
  gamma function; both agree with R BayesFactor to its own stated numerical error (about 1e-5 of the value, its
  "error" column), so the tolerance is 1e-4.
* The credible intervals come from random draws: they are checked against R with the same seed (the same draws, so
  the tolerance is 1e-9). How close they are to the exact posterior is a Monte Carlo question, checked in
  tests/test_s3d3_bayesian.py against long runs within four Monte Carlo standard errors.
"""

from __future__ import annotations

import textwrap

SEED = 'set.seed(1, kind = "Mersenne-Twister", normal.kind = "Inversion", sample.kind = "Rejection")'
OURS_R = {"table.explain": ("rstanarm", "rstan", "posterior"), "table.check_model_of": ("rstanarm", "rstan", "posterior")}
LIGHT = ("BayesFactor",)
HEAVY = ("rstanarm", "rstan", "posterior")
JZS = """
    import numpy as np
    from scipy import integrate

    def jzs(t, n_eff, df, r):
        # Rouder et al. (2009), equation 1, with the prior scale r (g ~ inverse gamma(1/2, r^2 / 2))
        def f(g):
            return ((1 + n_eff * g) ** -0.5 * (1 + t ** 2 / ((1 + n_eff * g) * df)) ** (-(df + 1) / 2)
                    * r / np.sqrt(2 * np.pi) * g ** -1.5 * np.exp(-r ** 2 / (2 * g)))
        return integrate.quad(f, 0, np.inf, limit=200)[0] / (1 + t ** 2 / df) ** (-(df + 1) / 2)
"""


def _join(*parts) -> str:
    return "\n".join(textwrap.dedent(part).strip("\n") for part in parts)


def _cases(Case):
    return [
        # ---------------------------------------------------------------- Z01-Z02: Bayes factors
        Case("table.compare_averages_of", "test_method=\"bayesian\": Student's sleep data, the two drugs as two groups",
             "Student's sleep data", "real data",
             ours="""
                 r = sdata.table(data).compare_averages_of("extra", for_each_group_in="group",
                                                           test_method="bayesian").as_pandas()
                 {"Bayes factor": r["Bayes factor"][0], "difference": r["difference"][0],
                  "95 % low": r["difference 95 % credible interval low"][0],
                  "95 % high": r["difference 95 % credible interval high"][0]}
             """,
             parent=_join(JZS, """
                 from scipy import stats
                 a = data.loc[data["group"] == "drug 1", "extra"].to_numpy(dtype=float)
                 b = data.loc[data["group"] == "drug 2", "extra"].to_numpy(dtype=float)
                 t = stats.ttest_ind(a, b).statistic
                 {"Bayes factor": jzs(t, len(a) * len(b) / (len(a) + len(b)), len(a) + len(b) - 2, np.sqrt(2) / 2)}
             """), parent_label="SciPy quad of the JZS integral (Rouder et al. 2009, eq. 1)", parent_tolerance=1e-4,
             r=f"""
                 x <- extra[group == "drug 1"]; y <- extra[group == "drug 2"]
                 b <- BayesFactor::ttestBF(x = x, y = y, rscale = "medium")
                 {SEED}
                 q <- summary(BayesFactor::posterior(b, iterations = 10000, progress = FALSE))$quantiles
                 list(`Bayes factor` = BayesFactor::extractBF(b)$bf, difference = q["beta (x - y)", "50%"],
                      `95 % low` = q["beta (x - y)", "2.5%"], `95 % high` = q["beta (x - y)", "97.5%"])
             """, r_packages=LIGHT, r_tolerance=1e-9,
             note="BayesFactor's documentation gives 1.27 for this Bayes factor; the interval is checked with the "
                  "same seed (same draws), its Monte Carlo error in the tests."),
        Case("table.compare_before_and_after", "test_method=\"bayesian\": Student's sleep data, each patient on both drugs",
             "Student's sleep data", "real data",
             ours="""
                 wide = pd.DataFrame({"drug_1": data.loc[data["group"] == "drug 1", "extra"].to_numpy(),
                                      "drug_2": data.loc[data["group"] == "drug 2", "extra"].to_numpy()})
                 r = sdata.table(wide).compare_before_and_after("drug_1", "drug_2", test_method="bayesian").as_pandas()
                 {"Bayes factor": r["Bayes factor"][0], "average change": r["average change"][0],
                  "95 % low": r["average change 95 % credible interval low"][0],
                  "95 % high": r["average change 95 % credible interval high"][0]}
             """,
             parent=_join(JZS, """
                 d = (data.loc[data["group"] == "drug 2", "extra"].to_numpy(dtype=float)
                      - data.loc[data["group"] == "drug 1", "extra"].to_numpy(dtype=float))
                 t = d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))
                 {"Bayes factor": jzs(t, len(d), len(d) - 1, np.sqrt(2) / 2)}
             """), parent_label="SciPy quad of the JZS integral (Rouder et al. 2009, eq. 1)", parent_tolerance=1e-4,
             r=f"""
                 b <- BayesFactor::ttestBF(x = extra[group == "drug 2"], y = extra[group == "drug 1"], paired = TRUE)
                 {SEED}
                 q <- summary(BayesFactor::posterior(b, iterations = 10000, progress = FALSE))$quantiles
                 list(`Bayes factor` = BayesFactor::extractBF(b)$bf, `average change` = q["mu", "50%"],
                      `95 % low` = q["mu", "2.5%"], `95 % high` = q["mu", "97.5%"])
             """, r_packages=LIGHT, r_tolerance=1e-9,
             note="BayesFactor's documentation gives 17.26 for this paired Bayes factor (the example of ttestBF's help)."),
        Case("table.compare_average_to", "test_method=\"bayesian\": Student's sleep data, drug 1 against 1 extra hour",
             "Student's sleep data", "real data",
             ours="""
                 one = pd.DataFrame({"extra": data.loc[data["group"] == "drug 1", "extra"].to_numpy()})
                 r = sdata.table(one).compare_average_to("extra", 1, test_method="bayesian", prior_width="wide").as_pandas()
                 {"Bayes factor": r["Bayes factor"][0], "difference": r["difference"][0],
                  "95 % low": r["difference 95 % credible interval low"][0],
                  "95 % high": r["difference 95 % credible interval high"][0]}
             """,
             parent=_join(JZS, """
                 x = data.loc[data["group"] == "drug 1", "extra"].to_numpy(dtype=float)
                 t = (x.mean() - 1) / (x.std(ddof=1) / np.sqrt(len(x)))
                 {"Bayes factor": jzs(t, len(x), len(x) - 1, 1.0)}
             """), parent_label="SciPy quad of the JZS integral (Rouder et al. 2009, eq. 1), r = 1",
             parent_tolerance=1e-4,
             r=f"""
                 x <- extra[group == "drug 1"]
                 b <- BayesFactor::ttestBF(x = x, mu = 1, rscale = "wide")
                 bs <- BayesFactor::ttestBF(x = x - 1, rscale = "wide")
                 {SEED}
                 q <- summary(BayesFactor::posterior(bs, iterations = 10000, progress = FALSE))$quantiles
                 list(`Bayes factor` = BayesFactor::extractBF(b)$bf, difference = q["mu", "50%"],
                      `95 % low` = q["mu", "2.5%"], `95 % high` = q["mu", "97.5%"])
             """, r_packages=LIGHT, r_tolerance=1e-9,
             note="The Bayes factor is R's own ttestBF(x, mu = 1); the interval is that of the average minus 1, from "
                  "ttestBF(x - 1), because BayesFactor's posterior() leaves mu = out."),
        Case("table.find_correlation_between", "test_method=\"bayesian\": mtcars, fuel use and weight",
             "mtcars", "real data",
             ours="""
                 r = sdata.table(data).find_correlation_between("mpg", "wt", test_method="bayesian").as_pandas()
                 {"Bayes factor": r["Bayes factor"][0], "r": r["r"][0], "95 % low": r["r 95 % credible interval low"][0],
                  "95 % high": r["r 95 % credible interval high"][0]}
             """,
             r=f"""
                 b <- BayesFactor::correlationBF(y = mpg, x = wt, rscale = "medium")
                 {SEED}
                 q <- summary(BayesFactor::posterior(b, iterations = 10000, progress = FALSE))$quantiles
                 list(`Bayes factor` = BayesFactor::extractBF(b)$bf, r = q["rho", "50%"], `95 % low` = q["rho", "2.5%"],
                      `95 % high` = q["rho", "97.5%"])
             """, r_packages=LIGHT, r_tolerance=1e-9,
             note="The design check of 2026-11-20 gave a Bayes factor of 1.3 x 10^7 for this pair (BayesFactor "
                  "0.9.12-4.8)."),
        Case("table.compare_counts_of", "test_method=\"bayesian\": mtcars, gearbox (automatic or manual) by engine shape",
             "mtcars", "real data",
             ours="""
                 t = sdata.table(data.assign(gearbox=data["am"].map({0: "automatic", 1: "manual"}),
                                             engine=data["vs"].map({0: "V-shaped", 1: "straight"})))
                 r = t.compare_counts_of("gearbox", for_each_group_in="engine", test_method="bayesian").as_pandas()
                 {"Bayes factor": r["Bayes factor"][0], "share manual, straight": r["share manual in straight"][0],
                  "95 % low": r["share manual in straight 95 % credible interval low"][0]}
             """,
             parent="""
                 import numpy as np
                 from scipy.special import gammaln
                 tab = pd.crosstab(data["vs"], data["am"]).to_numpy(dtype=float)  # groups (engine) as rows
                 def log_b(alpha):
                     return gammaln(alpha).sum() - gammaln(alpha.sum())
                 a = np.ones(tab.shape[1])
                 log_bf = sum(log_b(row + a) - log_b(a) for row in tab) - (log_b(tab.sum(axis=0) + a) - log_b(a))
                 {"Bayes factor": float(np.exp(log_bf))}
             """, parent_label="the Gunel-Dickey closed form, independent multinomial, a = 1 (SciPy gammaln)",
             parent_tolerance=1e-4,
             r=f"""
                 tab <- table(factor(ifelse(vs == 1, "straight", "V-shaped"), levels = c("V-shaped", "straight")),
                              factor(ifelse(am == 1, "manual", "automatic")))
                 b <- BayesFactor::contingencyTableBF(tab, sampleType = "indepMulti", fixedMargin = "rows")
                 {SEED}
                 q <- summary(BayesFactor::posterior(b, iterations = 10000, progress = FALSE))$quantiles
                 list(`Bayes factor` = BayesFactor::extractBF(b)$bf, `share manual, straight` = q["omega[2,2]", "50%"],
                      `95 % low` = q["omega[2,2]", "2.5%"])
             """, r_packages=LIGHT, r_tolerance=1e-9,
             note="simplydata orders the groups as text (\"V-shaped\" before \"straight\"), so the R table lists them "
                  "in that order too."),
        # ---------------------------------------------------------------- Z03-Z06: Bayesian models
        Case("table.explain", "test_method=\"bayesian\": mtcars, fuel use from weight and horsepower (rstanarm stan_glm)",
             "mtcars", "real data",
             ours="""
                 r = sdata.table(data).explain("mpg", using=["wt", "hp"], test_method="bayesian").as_pandas().set_index("term")
                 {"wt": r.loc["wt", "effect"], "wt 95 % low": r.loc["wt", "95 % credible interval low"],
                  "wt 95 % high": r.loc["wt", "95 % credible interval high"], "hp": r.loc["hp", "effect"],
                  "sigma": r.loc["spread around the model (sigma)", "effect"], "wt R-hat": r.loc["wt", "R-hat"]}
             """,
             r="""
                 m <- rstanarm::stan_glm(mpg ~ wt + hp, data = data.frame(mpg, wt, hp), chains = 4, iter = 2000,
                                         seed = 1, refresh = 0, cores = 1)
                 ci <- rstanarm::posterior_interval(m, prob = 0.95)
                 s <- posterior::summarise_draws(posterior::as_draws_array(as.array(m)), "rhat")
                 list(wt = unname(coef(m)["wt"]), `wt 95 % low` = ci["wt", 1], `wt 95 % high` = ci["wt", 2],
                      hp = unname(coef(m)["hp"]), sigma = stats::sigma(m), `wt R-hat` = s$rhat[s$variable == "wt"])
             """, r_packages=HEAVY, r_tolerance=1e-9,
             note="lm() gives -3.88 for wt and -0.0318 for hp; the posterior medians are close to them because "
                  "rstanarm's priors are weak here."),
        Case("table.explain", "test_method=\"bayesian\", grouped_by=: sleepstudy, reaction time over days (rstanarm stan_glmer)",
             "sleepstudy (lme4)", "real data",
             ours="""
                 r = sdata.table(data).explain("Reaction", using=["Days"], grouped_by="Subject",
                                               test_method="bayesian").as_pandas().set_index("term")
                 {"Days": r.loc["Days", "effect"], "Days 95 % low": r.loc["Days", "95 % credible interval low"],
                  "Days 95 % high": r.loc["Days", "95 % credible interval high"],
                  "intercept": r.loc["(intercept)", "effect"]}
             """,
             r="""
                 m <- rstanarm::stan_glmer(Reaction ~ Days + (1 | Subject), data = data.frame(Reaction, Days, Subject),
                                           chains = 4, iter = 2000, seed = 1, refresh = 0, cores = 1)
                 ci <- rstanarm::posterior_interval(m, prob = 0.95, pars = "Days")
                 list(Days = unname(rstanarm::fixef(m)["Days"]), `Days 95 % low` = ci[1, 1], `Days 95 % high` = ci[1, 2],
                      intercept = unname(rstanarm::fixef(m)[1]))
             """, r_packages=HEAVY, r_tolerance=1e-9,
             note="lme4's REML estimates are 251.4 and 10.47 (Bates et al. 2015); the posterior medians are close."),
        Case("table.check_model_of", "test_method=\"bayesian\": mtcars, the posterior predictive check of fuel use from weight",
             "mtcars", "real data",
             ours="""
                 c = sdata.table(data).check_model_of("mpg", using=["wt"], test_method="bayesian")._check_numbers
                 {"data density at point 100": c["observed"][99], "set 3 at point 100": c["made"][2][99],
                  "set 50 at point 200": c["made"][49][199], "grid end": c["grid"][-1]}
             """,
             r="""
                 m <- rstanarm::stan_glm(mpg ~ wt, data = data.frame(mpg, wt), chains = 4, iter = 2000, seed = 1,
                                         refresh = 0, cores = 1)
                 yrep <- rstanarm::posterior_predict(m, draws = 50, seed = 1)
                 r <- range(c(mpg, yrep))
                 d <- function(v) stats::density(v, from = r[1], to = r[2], n = 256)$y
                 list(`data density at point 100` = d(mpg)[100], `set 3 at point 100` = d(yrep[3, ])[100],
                      `set 50 at point 200` = d(yrep[50, ])[200], `grid end` = r[2])
             """, r_packages=HEAVY, r_tolerance=1e-9,
             note="The picture's lines are R stats::density() of the data and of each set made up by "
                  "posterior_predict(), on one grid from the smallest to the largest value."),
    ]


def add_to(namespace) -> None:
    """Add the S3d-3 cases to cases.py."""
    Case = namespace["Case"]
    import dataclasses

    cases = []
    for c in _cases(Case):
        head = c.title.split(":")[0]
        ours_r = OURS_R.get(c.word, LIGHT)
        cases.append(dataclasses.replace(c, ours_r=ours_r, option=head if "=" in head else ""))
    namespace["CASES"].extend(cases)
