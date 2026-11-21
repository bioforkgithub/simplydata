"""The reliability study for phase S3d-2, epidemiology and cause and effect: balancing groups (compare_balanced_groups_of,
weighting and matching), attributable fractions (compare_risks(show="attributable fractions")), direct and indirect
standardisation (rate_of(standard_population=), compare_rates(standard_rates=)), mediation (explain(through=)), the
2 x 2 crossover (compare_averages_of(period=)) and multiple imputation for other words (find_correlation_between and
explain_survival with empty_cells="multiple imputation").

cases.py loads this file at its end and calls add_to(), which adds the datasets and cases below to its own DATASETS
and CASES and teaches load() the datasets read from R (airquality: R datasets; lung: R survival).

Published answers: Schütz, Labes & Fuglsang (2014) for the three bioequivalence reference datasets (the ratio and its
90 % interval, to the 2 decimals of percent they print). The other numbers are checked against R: the packages
simplydata runs (WeightIt, MatchIt, epiR), independent ones (epitools for the standardised rates, base R lm for the
crossover and for the product of coefficients that mediation estimates by simulation), and R mice with its own
filling-in for multiple imputation (a looser tolerance, because two random fillings differ).
"""

from __future__ import annotations

import textwrap

R_DATA_CAUSAL = {
    # as.numeric(): an empty cell of an R whole-number column comes through as R's NA, not as a huge negative number
    "airquality (R datasets)": ((), "d <- datasets::airquality; lapply(d[c(\"Ozone\", \"Solar.R\", \"Temp\", "
                                    "\"Wind\")], as.numeric)"),
    "lung with weight loss (survival)": (("survival",), "d <- survival::lung; lapply(d[c(\"time\", \"status\", \"age\", \"sex\", "
                                        "\"ph.karno\", \"wt.loss\")], as.numeric)"),
}
OURS_R = {"table.compare_balanced_groups_of": ("WeightIt", "MatchIt", "cobalt", "sandwich", "lmtest"),
          "table.compare_risks": ("epiR",), "table.rate_of": ("epiR",), "table.compare_rates": ("epiR",),
          "table.find_correlation_between": ("mice", "miceadds"), "table.explain_survival": ("mice", "survival")}
COLUMNS = '["age", "educ", "race", "married", "nodegree", "re74", "re75"]'
LALONDE_R = ("d <- data.frame(t = treat, y = re78, age = age, educ = educ, race = race, married = married, "
             "nodegree = nodegree, re74 = re74, re75 = re75)\n"
             "f <- t ~ age + educ + race + married + nodegree + re74 + re75")
SCHUTZ = "Schütz, Labes & Fuglsang (2014), AAPS J 16:1292-1297, Table II"
DOWN = """
    std = data.groupby("mother_age", as_index=False)["births"].sum()
"""


def _join(*parts) -> str:
    return "\n".join(textwrap.dedent(part).strip("\n") for part in parts)


def _datasets(Dataset):
    return [
        Dataset("lalonde", "lalonde.csv",
                "614 men: 185 in the National Supported Work job training and 429 from a population survey (PSID), "
                "with age, schooling, race, marriage, degree and earnings in 1974, 1975 and 1978",
                "LaLonde, R. J. (1986). Evaluating the econometric evaluations of training programs with experimental "
                "data. American Economic Review 76, 604-620; Dehejia, R. H. & Wahba, S. (1999). Journal of the "
                "American Statistical Association 94, 1053-1062. As shipped by the R package MatchIt (lalonde).",
                "Public study data (US Department of Labor NSW); the MatchIt copy is GPL (>= 2). Also the practice "
                "table job_training.",
                "https://doi.org/10.1080/01621459.1999.10473858"),
        Dataset("JOBS II", "jobs_ii.csv",
                "899 unemployed workers in a randomised job-search workshop: treatment, job-search confidence, "
                "depression six months later, economic hardship, sex, age and others",
                "Vinokur, A. D., Price, R. H. & Schul, Y. (1995). American Journal of Community Psychology 23, "
                "39-74; Tingley, D. et al. (2014). mediation: R Package for Causal Mediation Analysis. Journal of "
                "Statistical Software 59(5). As shipped by the R package mediation (jobs).",
                "GPL (>= 2) (mediation); stored with its numbers unchanged. Also the practice table job_search.",
                "https://doi.org/10.18637/jss.v059.i05"),
        Dataset("dry cat food and FLUTD", "flutd.csv",
                "a cross-sectional study of dry cat food and feline lower urinary tract disease: 13 of 2176 cats on "
                "dry food and 5 of 3354 on other food had the disease",
                "Willeberg, P. (1977). Animal disease information processing: epidemiologic analyses of the feline "
                "urologic syndrome. Acta Veterinaria Scandinavica 18 (Suppl. 64), 1-48; the first example of R "
                "epiR::epi.2by2.",
                "Published counts (facts); stored unchanged.",
                "https://cran.r-project.org/package=epiR"),
        Dataset("Down syndrome by birth order", "down_syndrome.csv",
                "Down syndrome cases and live births in Michigan by birth order and mother's age (6 x 6 bands)",
                "Selvin, S. (2004). Statistical Analysis of Epidemiologic Data, 3rd ed. Oxford University Press; the "
                "example of R epitools::ageadjust.direct (Fay & Feuer 1997, Statistics in Medicine 16, 791-801).",
                "Published counts (facts); stored unchanged.",
                "https://cran.r-project.org/package=epitools"),
        Dataset("bioequivalence reference datasets", "bioequivalence_reference.csv",
                "three 2 x 2 crossover bioequivalence studies (AUC of a test and a reference formulation): A, 18 "
                "subjects (Sauter et al. 1992); B, 18 subjects (Clayton & Leslie 1981); C, 13 subjects (B with "
                "subjects removed, unbalanced)",
                "Schütz, H., Labes, D. & Fuglsang, A. (2014). Reference Datasets for 2-Treatment, 2-Sequence, 2-Period "
                "Bioequivalence Studies. The AAPS Journal 16, 1292-1297 (supplementary data sets A, B and C; "
                "dataset A is also the practice table drug_levels).",
                "Measured values from published studies (facts), stored unchanged; the article is (c) AAPS 2014.",
                "https://doi.org/10.1208/s12248-014-9661-0"),
        Dataset("airquality (R datasets)", "",
                "daily air quality in New York, May to September 1973: ozone (37 empty cells), solar radiation (7 "
                "empty), wind and temperature",
                "Chambers, J. M. et al. (1983). Graphical Methods for Data Analysis. Wadsworth; data from the New "
                "York State Department of Conservation and the National Weather Service. R's datasets package.",
                "Public data; R's datasets package is GPL-2 | GPL-3; read from R, so it needs R.",
                "https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/airquality.html"),
        Dataset("lung with weight loss (survival)", "",
                "228 patients with advanced lung cancer: survival time, status, age, sex, Karnofsky score (empty "
                "cells) and weight loss (14 empty cells)",
                "Loprinzi, C. L. et al. (1994). Journal of Clinical Oncology 12, 601-607. As shipped by the R package "
                "survival (lung).",
                "LGPL (>= 2) (survival); read from the installed package, so it needs R.",
                "https://doi.org/10.1200/JCO.1994.12.3.601"),
    ]


def _cases(Case):
    return [
        # ---------------------------------------------------------------- AD01-AD03: balancing groups
        Case("table.compare_balanced_groups_of", "lalonde: weighting, the effect for everyone (ATE)", "lalonde",
             "real data",
             ours=f"""
                 r = sdata.table(data).compare_balanced_groups_of("re78", for_each_group_in="treat",
                                                                  allowing_for={COLUMNS}).as_pandas().iloc[0]
                 {{"effect": r["estimate"], "standard error": r["standard error"], "p-value": r["p-value"]}}
             """,
             r=_join(LALONDE_R, """
                 W <- WeightIt::weightit(f, data = d, method = "glm", estimand = "ATE")
                 co <- summary(WeightIt::glm_weightit(y ~ t, data = d, weightit = W, family = stats::gaussian()))$coefficients
                 list(effect = co["t", 1], `standard error` = co["t", 2], `p-value` = co["t", 4])
             """), r_packages=("WeightIt",), r_tolerance=1e-9,
             note="The randomised NSW experiment found 1794 dollars (Dehejia & Wahba 1999); the survey comparison "
                  "group is very unlike the trained men, so balancing on these columns does not recover it fully."),
        Case("table.compare_balanced_groups_of", "lalonde: the balance table (standardised differences, cobalt)",
             "lalonde", "real data",
             ours=f"""
                 b = sdata.table(data).compare_balanced_groups_of("re78", for_each_group_in="treat",
                                                                  allowing_for={COLUMNS}, show="balance").as_pandas()
                 b = b.set_index("column")
                 {{"race black before": b.loc["race: black", "difference before"],
                   "race black after": b.loc["race: black", "difference after"],
                   "re74 after": b.loc["re74", "difference after"]}}
             """,
             r=_join(LALONDE_R, """
                 W <- WeightIt::weightit(f, data = d, method = "glm", estimand = "ATE")
                 bb <- cobalt::bal.tab(W, un = TRUE, binary = "std", continuous = "std")$Balance
                 list(`race black before` = bb["race_black", "Diff.Un"], `race black after` = bb["race_black", "Diff.Adj"],
                      `re74 after` = bb["re74", "Diff.Adj"])
             """), r_packages=("WeightIt", "cobalt"), r_tolerance=1e-9),
        Case("table.compare_balanced_groups_of",
             'test_method="matching": lalonde, 1:1 nearest neighbour, the effect among the trained men (ATT)', "lalonde",
             "real data",
             ours=f"""
                 r = sdata.table(data).compare_balanced_groups_of("re78", for_each_group_in="treat",
                                                                  allowing_for={COLUMNS}, test_method="matching",
                                                                  effect_for=1).as_pandas().iloc[0]
                 {{"effect": r["estimate"], "standard error": r["standard error"]}}
             """,
             r=_join(LALONDE_R, """
                 m <- MatchIt::matchit(f, data = d, method = "nearest", distance = "glm")
                 md <- MatchIt::match.data(m)
                 fit <- stats::lm(y ~ t, data = md, weights = weights)
                 co <- lmtest::coeftest(fit, vcov. = sandwich::vcovCL(fit, cluster = ~subclass))
                 list(effect = co["t", 1], `standard error` = co["t", 2])
             """), r_packages=("MatchIt", "sandwich", "lmtest"), r_tolerance=1e-9,
             note="The MatchIt vignette's own analysis of lalonde: ATT 894, clustered standard error 705."),
        Case("table.compare_balanced_groups_of",
             'test_method="matching": lalonde, with a caliper of 0.2 standard deviations of the logit (match_within=0.2)',
             "lalonde", "real data",
             ours=f"""
                 r = sdata.table(data).compare_balanced_groups_of("re78", for_each_group_in="treat",
                                                                  allowing_for={COLUMNS}, test_method="matching",
                                                                  effect_for=1, match_within=0.2).as_pandas().iloc[0]
                 {{"effect": r["estimate"], "standard error": r["standard error"]}}
             """,
             r=_join(LALONDE_R, """
                 m <- MatchIt::matchit(f, data = d, method = "nearest", distance = "glm", link = "linear.logit",
                                       caliper = 0.2)
                 md <- MatchIt::match.data(m)
                 fit <- stats::lm(y ~ t, data = md, weights = weights)
                 co <- lmtest::coeftest(fit, vcov. = sandwich::vcovCL(fit, cluster = ~subclass))
                 list(effect = co["t", 1], `standard error` = co["t", 2])
             """), r_packages=("MatchIt", "sandwich", "lmtest"), r_tolerance=1e-9),
        # ---------------------------------------------------------------- S03: attributable fractions
        Case("table.compare_risks", 'show="attributable fractions": dry cat food and urinary disease (Willeberg 1977)',
             "dry cat food and FLUTD", "real data",
             ours="""
                 import pandas as pd
                 rows = [{"food": f, "flutd": "yes"} for f, e in zip(data["food"], data["flutd"]) for _ in range(e)]
                 rows += [{"food": f, "flutd": "no"} for f, e, n in zip(data["food"], data["flutd"], data["cats"])
                          for _ in range(n - e)]
                 r = sdata.table(pd.DataFrame(rows)).compare_risks("flutd", for_each_group_in="food",
                                                                   against="other food",
                                                                   show="attributable fractions").as_pandas()
                 {"AF among the exposed": r["estimate"][0], "AF low": r["estimate 95 % CI low"][0],
                  "AF high": r["estimate 95 % CI high"][0], "PAF": r["estimate"][1]}
             """,
             r="""
                 r <- epiR::epi.2by2(as.table(matrix(c(flutd[1], cats[1] - flutd[1], flutd[2], cats[2] - flutd[2]),
                                                     nrow = 2, byrow = TRUE)), method = "cohort.count")$massoc.detail
                 list(`AF among the exposed` = r$AFRisk.strata.wald$est, `AF low` = r$AFRisk.strata.wald$lower,
                      `AF high` = r$AFRisk.strata.wald$upper, PAF = r$PAFRisk.strata.wald$est)
             """, r_packages=("epiR",), r_tolerance=1e-9,
             note="epiR's help prints 75.05 % (32.91 to 90.72) among the exposed and 54.20 % in the population."),
        Case("table.compare_risks",
             'show="attributable fractions": the preventable fraction is 1 minus the risk ratio (groups swapped)',
             "dry cat food and FLUTD", "real data",
             ours="""
                 import pandas as pd
                 rows = [{"food": f, "flutd": "yes"} for f, e in zip(data["food"], data["flutd"]) for _ in range(e)]
                 rows += [{"food": f, "flutd": "no"} for f, e, n in zip(data["food"], data["flutd"], data["cats"])
                          for _ in range(n - e)]
                 r = sdata.table(pd.DataFrame(rows)).compare_risks("flutd", for_each_group_in="food",
                                                                   against="dry cat food",
                                                                   show="attributable fractions").as_pandas()
                 {"preventable fraction": float(r.loc[r["measure"] == "preventable fraction among the exposed",
                                                      "estimate"].iloc[0])}
             """,
             r="""
                 rr <- (flutd[2] / cats[2]) / (flutd[1] / cats[1])
                 list(`preventable fraction` = 1 - rr)
             """, r_tolerance=1e-9,
             note="The definition 1 - risk ratio (Rothman, Greenland & Lash 2008), in base R."),
        # ---------------------------------------------------------------- S07: standardisation
        Case("table.rate_of", "standard_population=: Down syndrome by birth order, adjusted for the mother's age",
             "Down syndrome by birth order", "real data",
             ours="""
                 r = sdata.table(data).rate_of("cases", time="births", for_each_group_in="birth_order",
                                               allowing_for="mother_age", standard_population="whole table",
                                               per=100000).as_pandas().set_index("group")
                 {"adjusted, first born": r.loc["1", "adjusted rate"],
                  "low, first born": r.loc["1", "adjusted rate 95 % CI low"],
                  "high, first born": r.loc["1", "adjusted rate 95 % CI high"],
                  "adjusted, fifth or later": r.loc["5+", "adjusted rate"],
                  "crude, fifth or later": r.loc["5+", "crude rate"]}
             """,
             r="""
                 k <- function(o) { s <- tapply(births, mother_age, sum)
                   a <- epitools::ageadjust.direct(cases[birth_order == o], births[birth_order == o],
                                                   stdpop = s[mother_age[birth_order == o]]) * 1e5; a }
                 one <- k("1"); five <- k("5+")
                 list(`adjusted, first born` = one[["adj.rate"]], `low, first born` = one[["lci"]],
                      `high, first born` = one[["uci"]], `adjusted, fifth or later` = five[["adj.rate"]],
                      `crude, fifth or later` = five[["crude.rate"]])
             """, r_packages=("epitools",), r_tolerance=1e-9,
             note="R epitools::ageadjust.direct is a separate package from epiR, which simplydata runs; the epitools "
                  "help gives 92.3 (80.4 to 105.8) per 100,000 for the first born."),
        Case("table.compare_rates", "standard_rates=: Down syndrome by birth order against the pooled rates (SMR)",
             "Down syndrome by birth order", "real data",
             ours="""
                 pooled = data.groupby("mother_age")[["cases", "births"]].sum()
                 rates = (pooled["cases"] / pooled["births"] * 100000).to_dict()
                 r = sdata.table(data).compare_rates("cases", time="births", for_each_group_in="birth_order",
                                                     allowing_for="mother_age", standard_rates=rates,
                                                     per=100000).as_pandas().set_index("group")
                 {"observed / expected, first born": r.loc["1", "observed / expected"],
                  "expected, first born": r.loc["1", "expected"],
                  "low, first born": r.loc["1", "observed / expected 95 % CI low"],
                  "p, first born": r.loc["1", "p-value"],
                  "observed / expected, fifth or later": r.loc["5+", "observed / expected"]}
             """,
             r="""
                 s <- tapply(cases, mother_age, sum); p <- tapply(births, mother_age, sum)
                 k <- function(o) epitools::ageadjust.indirect(cases[birth_order == o], births[birth_order == o],
                                                               stdcount = s[mother_age[birth_order == o]],
                                                               stdpop = p[mother_age[birth_order == o]])$sir
                 one <- k("1"); five <- k("5+")
                 pt <- stats::poisson.test(one[["observed"]], one[["exp"]])
                 list(`observed / expected, first born` = one[["sir"]], `expected, first born` = one[["exp"]],
                      `low, first born` = pt$conf.int[1], `p, first born` = pt$p.value,
                      `observed / expected, fifth or later` = five[["sir"]])
             """, r_packages=("epitools",), r_tolerance=1e-9,
             note="The ratio and the expected count from R epitools::ageadjust.indirect (a separate package from epiR); "
                  "its log-normal interval differs, so the exact interval and p-value come from R poisson.test(). "
                  "The standard rates are the table's own pooled rates, worked out in the case code."),
        # ---------------------------------------------------------------- AD07: mediation
        Case("table.explain", "through=: JOBS II, the workshop, job-search confidence and depression", "JOBS II",
             "real data",
             ours="""
                 r = sdata.table(data).explain("depress2", using="treat", through="job_seek",
                                               allowing_for=["econ_hard", "sex", "age"]).as_pandas().set_index("term")
                 {"indirect effect": r.loc["indirect effect (through job_seek)", "estimate"],
                  "indirect low": r.loc["indirect effect (through job_seek)", "95 % CI low"],
                  "total effect": r.loc["total effect", "estimate"]}
             """,
             parent="""
                 import statsmodels.formula.api as smf
                 from statsmodels.stats.mediation import Mediation
                 med = smf.ols("job_seek ~ treat + econ_hard + sex + age", data=data)
                 out = smf.ols("depress2 ~ treat + job_seek + econ_hard + sex + age", data=data)
                 s = Mediation(out, med, "treat", "job_seek").fit(n_rep=1000, rng=1).summary()
                 {"indirect effect": s.loc["ACME (average)", "Estimate"],
                  "indirect low": s.loc["ACME (average)", "Lower CI bound"], "total effect": s.loc["Total effect", "Estimate"]}
             """, parent_label="statsmodels Mediation (with_seed=1)",
             r="""
                 a <- coef(lm(job_seek ~ treat + econ_hard + sex + age))[["treat"]]
                 b <- coef(lm(depress2 ~ treat + job_seek + econ_hard + sex + age))[["job_seek"]]
                 total <- coef(lm(depress2 ~ treat + econ_hard + sex + age))[["treat"]]
                 list(`indirect effect` = a * b, `total effect` = total)
             """, r_tolerance=0.05,
             note="For two linear models without an interaction the indirect effect is the product of the two "
                  "coefficients and the total effect the coefficient of treat without job_seek (base R lm); "
                  "the simulation (1000 draws) estimates them within a few percent. R mediation::mediate(sims = "
                  "1000) gave -0.0159 (-0.0422 to 0.0105) here; Tingley et al. (2014) analyse the same data."),
        # ---------------------------------------------------------------- I05: 2 x 2 crossover
        *[Case("table.compare_averages_of", f"period=: bioequivalence reference dataset {name} ({what})",
               "bioequivalence reference datasets", "published",
               ours=f"""
                   r = sdata.table(data[data["dataset"] == "{name}"]).compare_averages_of(
                       "auc", for_each_group_in="formulation", matched_by="subject", period="period",
                       same_within=[0.8, 1.25]).as_pandas().iloc[0]
                   {{"ratio": r["estimate"], "90 % CI low": r["90 % CI low"], "90 % CI high": r["90 % CI high"],
                     "within-subject CV": r["within-subject CV"]}}
               """,
               published={"ratio": (ratio, 0.00005, SCHUTZ), "90 % CI low": (low, 0.00005, SCHUTZ),
                          "90 % CI high": (high, 0.00005, SCHUTZ)},
               r=f"""
                   k <- dataset == "{name}"
                   s <- factor(subject[k]); p <- factor(period[k]); f <- factor(formulation[k])
                   first <- tapply(as.character(f), list(s, p), function(v) v)[, 1]
                   q <- factor(first[as.character(s)])
                   m <- stats::lm(log(auc[k]) ~ q + s + p + f)
                   ci <- stats::confint(m, level = 0.90)["ftest", ]
                   list(ratio = exp(coef(m)[["ftest"]]), `90 % CI low` = exp(ci[[1]]), `90 % CI high` = exp(ci[[2]]),
                        `within-subject CV` = sqrt(exp(summary(m)$sigma^2) - 1))
               """, r_tolerance=1e-9,
               note="R lm() gives NA for the sequence (subject lies within it), as the EMA model expects.")
          for name, what, ratio, low, high in (("A", "18 subjects, balanced", 0.9509, 0.9076, 0.9962),
                                               ("B", "18 subjects, a large CV", 0.7110, 0.5145, 0.9826),
                                               ("C", "13 subjects, unbalanced", 0.5856, 0.3941, 0.8703))],
        # ---------------------------------------------------------------- X05: multiple imputation for other words
        Case("table.find_correlation_between",
             'empty_cells="multiple imputation": airquality, ozone and temperature (37 empty ozone cells)',
             "airquality (R datasets)", "real data",
             ours="""
                 t = sdata.table(data).find_correlation_between("Ozone", "Temp", "Solar.R", "Wind",
                                                                empty_cells="multiple imputation").as_pandas()
                 {"r": t[(t["column 1"] == "Ozone") & (t["column 2"] == "Temp")]["r"].iloc[0]}
             """,
             r="""
                 d <- data.frame(Ozone = Ozone, Solar.R = Solar.R, Temp = Temp, Wind = Wind)
                 imp <- mice::mice(d, m = 20, method = "pmm", seed = 1, printFlag = FALSE)
                 r <- miceadds::micombine.cor(imp, variables = c("Ozone", "Temp"))
                 list(r = r$r[1])
             """, r_packages=("mice", "miceadds"), r_tolerance=0.03,
             note="R mice fills in with its own random draws, so the two pooled correlations agree to the "
                  "simulation error, not to many digits; the pooling itself is checked exactly in the same "
                  "underneath."),
        Case("table.explain_survival",
             'empty_cells="multiple imputation": lung cancer survival, with empty Karnofsky and weight-loss cells',
             "lung with weight loss (survival)", "real data",
             ours="""
                 r = sdata.table(data).explain_survival(time="time", event="status", value=2,
                                                        using=["age", "sex", "ph.karno", "wt.loss"],
                                                        empty_cells="multiple imputation").as_pandas().set_index("term")
                 {"hazard ratio sex": r.loc["sex", "hazard ratio"], "hazard ratio ph.karno": r.loc["ph.karno", "hazard ratio"]}
             """,
             r="""
                 d <- data.frame(time = time, status = as.numeric(status == 2), age = age, sex = sex, ph.karno = ph.karno,
                                 wt.loss = wt.loss)
                 d$hazard <- mice::nelsonaalen(d, time, status)
                 pred <- mice::make.predictorMatrix(d); pred[, "time"] <- 0
                 imp <- mice::mice(d, m = 20, method = "pmm", predictorMatrix = pred, seed = 1, printFlag = FALSE)
                 fit <- with(imp, survival::coxph(survival::Surv(time, status) ~ age + sex + ph.karno + wt.loss))
                 s <- summary(mice::pool(fit), exponentiate = TRUE)
                 list(`hazard ratio sex` = s$estimate[2], `hazard ratio ph.karno` = s$estimate[3])
             """, r_packages=("mice", "survival"), r_tolerance=0.02,
             note="R mice with the event and the Nelson-Aalen hazard as predictors (White & Royston 2009) and its "
                  "own random draws: the pooled hazard ratios agree to the simulation error."),
    ]


def add_to(namespace) -> None:
    """Add the S3d-2 datasets and cases to cases.py, and teach its load() the datasets read from R."""
    import dataclasses

    import numpy as np
    import pandas as pd

    Dataset, Case = namespace["Dataset"], namespace["Case"]
    for d in _datasets(Dataset):
        namespace["DATASETS"][d.name] = d
    cases = []
    for c in _cases(Case):
        head = c.title.split(":")[0]
        option = head if "=" in head else ""
        cases.append(dataclasses.replace(c, ours_r=OURS_R.get(c.word), option=option))
    namespace["CASES"].extend(cases)
    namespace.setdefault("R_DATA", {}).update({name: packages for name, (packages, _) in R_DATA_CAUSAL.items()})
    plain_load = namespace["load"]

    def load(name: str) -> pd.DataFrame:
        if name in R_DATA_CAUSAL:
            from simplydata._r import need_r, r_call

            packages, code = R_DATA_CAUSAL[name]
            need_r(packages, f"the {name} data")
            found = r_call(code, what=f"the {name} data")
            return pd.DataFrame({k: np.asarray(v, dtype=float) for k, v in found.items()})
        return plain_load(name)

    namespace["load"] = load
