"""The reliability study for phase S3a-3, checking and comparing: explain(spread_changes_with=,
neighbours_alike_in_order_of=), find_columns_that_predict, compare_models(using=[[...], ...],
check_on_left_out_rows=True), the notes of check_model_of, find_model_averages_of(comparing=, within_each_group_in=,
over_range_of=), find_group_levels_of, compare_averages_of(grouped_by=) and with a list of columns, and
draw_interaction_lines.

cases.py loads this file at its end and calls add_to(), which adds the datasets and cases below to its own
DATASETS and CASES and teaches load() the datasets read from R packages (not stored here: their licence is the
package's, GPL, so they are read where they are published).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# datasets read from an R package at run time: name -> (R packages, R code giving a named list of columns)
R_DATA_CHECKING = {
    "Dialyzer (nlme)": (("nlme",), "d <- nlme::Dialyzer; list(rate = d$rate, pressure = d$pressure, "
                                   "QB = as.character(d$QB))"),
    "sleepstudy (lme4)": (("lme4",), "d <- lme4::sleepstudy; list(Reaction = d$Reaction, Days = d$Days, "
                                     "Subject = paste0('s', as.character(d$Subject)))"),
    "birthwt (MASS)": (("MASS",), "d <- MASS::birthwt; list(low = ifelse(d$low == 1, 'yes', 'no'), age = d$age, "
                                  "lwt = d$lwt, smoke = ifelse(d$smoke == 1, 'yes', 'no'))"),
}


def _datasets(Dataset):
    r_copy = "The copy in R's datasets package is GPL-2 | GPL-3."
    return [
        Dataset("swiss", "swiss.csv",
                "fertility and five social measures of 47 French-speaking provinces of Switzerland in about 1888",
                "Mosteller, F. & Tukey, J. W. (1977). Data Analysis and Regression. Addison-Wesley, pp. 549-551 "
                "(from the Office of Population Research, Princeton, 1976). Copy from R's datasets package (swiss).",
                "Official 1888 statistics (public domain). " + r_copy,
                "https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/swiss.html"),
        Dataset("iris", "iris.csv",
                "sepal and petal length and width of 50 flowers of each of three iris species",
                "Anderson, E. (1935). The irises of the Gaspe Peninsula. Bulletin of the American Iris Society 59, "
                "2-5; Fisher, R. A. (1936). The use of multiple measurements in taxonomic problems. Annals of "
                "Eugenics 7, 179-188. Copy from R's datasets package (iris).",
                "Published 1935 (public domain). " + r_copy,
                "https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/iris.html"),
        Dataset("warpbreaks", "warpbreaks.csv",
                "the number of warp breaks per loom for two wools (A, B) at three tensions (L, M, H), 9 looms each",
                "Tippett, L. H. C. (1950). Technological Applications of Statistics. Wiley, p. 106. Copy from R's "
                "datasets package (warpbreaks).",
                "Published 1950 (facts). " + r_copy,
                "https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/warpbreaks.html"),
        Dataset("Lake Huron", "lake_huron.csv",
                "annual level of Lake Huron in feet, 1875-1972",
                "Brockwell, P. J. & Davis, R. A. (1991). Time Series and Forecasting Methods, 2nd ed. Springer, "
                "pp. 328-329 (from the US Army Corps of Engineers). Copy from R's datasets package (LakeHuron).",
                "US Government measurements (public domain). " + r_copy,
                "https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/LakeHuron.html"),
        Dataset("rat liver glycogen", "rat_glycogen.csv",
                "glycogen in the livers of 6 rats, 2 on each of 3 treatments (control, glucose, glucose and "
                "fructose), 3 preparations per liver and 2 readings per preparation (36 rows)",
                "Sokal, R. R. & Rohlf, F. J. (1981). Biometry, 2nd ed. Freeman, Box 10.1 (nested ANOVA: treatments "
                "SS 1557.56 on 2 df, rats within treatments SS 797.67 on 3 df, F = 2.929); the same analysis in "
                "Crawley, M. J. (2007). The R Book. Wiley, chapter 11.",
                "Facts published in the book (36 numbers), typed from it; not covered by copyright.",
                "https://www.worldcat.org/title/biometry/oclc/7203719"),
        Dataset("Dialyzer (nlme)", "",
                "ultrafiltration rate of 20 high-flux haemodialyzers at 7 transmembrane pressures, at two blood flow "
                "rates (140 rows)",
                "Vonesh, E. F. & Carter, R. L. (1992). Mixed-effects nonlinear regression for unbalanced repeated "
                "measures. Biometrics 48, 1-17. Analysed with variance functions in Pinheiro, J. C. & Bates, D. M. "
                "(2000). Mixed-Effects Models in S and S-PLUS. Springer, section 5.2. Shipped with the R package nlme.",
                "GPL (nlme). Not stored here: read from nlme, so it needs R.",
                "https://cran.r-project.org/package=nlme"),
        Dataset("sleepstudy (lme4)", "",
                "average reaction time of 18 truck drivers on each of 10 days of sleep deprivation (180 rows)",
                "Belenky, G. et al. (2003). Patterns of performance degradation and restoration during sleep "
                "restriction and subsequent recovery. Journal of Sleep Research 12, 1-12. Analysed in Bates, D., "
                "Maechler, M., Bolker, B. & Walker, S. (2015). Fitting linear mixed-effects models using lme4. "
                "Journal of Statistical Software 67(1) (CC BY). Shipped with the R package lme4.",
                "GPL (>= 2) (lme4). Not stored here: read from lme4, so it needs R.",
                "https://doi.org/10.18637/jss.v067.i01"),
        Dataset("birthwt (MASS)", "",
                "189 births at Baystate Medical Center, Springfield, Massachusetts (1986): low birth weight, the "
                "mother's age, weight and smoking",
                "Hosmer, D. W. & Lemeshow, S. (1989). Applied Logistic Regression. Wiley. Shipped with the R package "
                "MASS (Venables, W. N. & Ripley, B. D. (2002). Modern Applied Statistics with S, 4th ed.).",
                "GPL-2 | GPL-3 (MASS). Not stored here: read from MASS, so it needs R.",
                "https://cran.r-project.org/package=MASS"),
    ]


def _cases(Case):
    swiss_cols = '["Agriculture", "Examination", "Education", "Catholic", "Infant.Mortality"]'
    return [
        # ---- J14: generalised least squares
        Case("table.explain", 'spread_changes_with=: the spread of the ultrafiltration rate grows with pressure '
                              "(varPower)", "Dialyzer (nlme)", "real data",
             ours="""
                 r = sdata.table(data).explain("rate", using=["pressure"], spread_changes_with="pressure").as_pandas()
                 r = r.set_index("term")
                 {"slope": r.loc["pressure", "effect"], "standard error": r.loc["pressure", "standard error"],
                  "power": r.loc['spread grows as "pressure" to the power', "effect"]}
             """,
             r="""
                 m <- nlme::gls(rate ~ pressure, weights = nlme::varPower(form = ~ pressure))
                 list(slope = coef(m)[2], `standard error` = sqrt(vcov(m)[2, 2]),
                      power = unname(coef(m$modelStruct$varStruct, unconstrained = FALSE)))
             """, r_packages=("nlme",), r_tolerance=1e-5,
             note="R nlme::gls() is the reference: statsmodels has no variance functions. nlme's optimiser stops at "
                  "its own tolerance, so the numbers agree to about 1e-6."),
        Case("table.explain", 'spread_changes_with=: a spread of its own for each blood flow rate (varIdent), with '
                              "its interval", "Dialyzer (nlme)", "real data",
             ours="""
                 r = sdata.table(data).explain("rate", using=["pressure"], spread_changes_with="QB").as_pandas()
                 r = r.set_index("term")
                 row = r.loc['spread of "300" against "200"']
                 {"ratio": row["effect"], "ratio low": row["95 % CI low"], "ratio high": row["95 % CI high"]}
             """,
             r="""
                 m <- nlme::gls(rate ~ pressure, weights = nlme::varIdent(form = ~ 1 | QB))
                 v <- nlme::intervals(m, which = "var-cov")$varStruct
                 list(ratio = v[1, 2], `ratio low` = v[1, 1], `ratio high` = v[1, 3])
             """, r_packages=("nlme",), r_tolerance=1e-5),
        Case("table.explain", "neighbours_alike_in_order_of=: the level of Lake Huron, a linear trend with AR(1) "
                              "errors", "Lake Huron", "real data",
             ours="""
                 r = sdata.table(data).explain("level", using=["year"], neighbours_alike_in_order_of="year").as_pandas()
                 r = r.set_index("term")
                 {"trend": r.loc["year", "effect"], "standard error": r.loc["year", "standard error"],
                  "phi": r.loc['correlation of neighbours in "year" order', "effect"]}
             """,
             r="""
                 m <- nlme::gls(level ~ year, correlation = nlme::corAR1(form = ~ year))
                 list(trend = coef(m)[2], `standard error` = sqrt(vcov(m)[2, 2]),
                      phi = unname(coef(m$modelStruct$corStruct, unconstrained = FALSE)))
             """, r_packages=("nlme",), r_tolerance=1e-5),
        # ---- L10: lasso
        Case("table.find_columns_that_predict", "lasso: which social measures predict fertility (1888)", "swiss",
             "real data",
             ours=f"""
                 r = sdata.table(data).find_columns_that_predict("Fertility", using={swiss_cols}).as_pandas()
                 r = r.set_index("term")
                 {{"Education": r.loc["Education", "effect"], "Infant.Mortality": r.loc["Infant.Mortality", "effect"],
                  "penalty": r.loc["penalty chosen (lambda.1se)", "penalty"]}}
             """,
             r=f"""
                 x <- cbind(Agriculture, Examination, Education, Catholic, Infant.Mortality)
                 set.seed(1)
                 f <- glmnet::cv.glmnet(x, Fertility, alpha = 1, nfolds = 10)
                 b <- as.numeric(coef(f, s = "lambda.1se"))
                 list(Education = b[4], Infant.Mortality = b[6], penalty = f$lambda.1se)
             """, r_packages=("glmnet",), r_tolerance=1e-9,
             note="R glmnet with the same seed is the reference (the random split is made in R). No published lasso "
                  "fit of these data is used: a cross-validated penalty depends on the random split. The tests also "
                  "check the effects against statsmodels' elastic net at the same penalty (to about 0.5 %, glmnet's "
                  "convergence threshold)."),
        # ---- O10: AICc table
        Case("table.compare_models", "using=[[...], ...]: three models of fertility, AICc and Akaike weights",
             "swiss", "real data",
             ours="""
                 r = sdata.table(data).compare_models("Fertility", using=[["Education"], ["Education", "Catholic"],
                     ["Education", "Catholic", "Infant.Mortality"]]).as_pandas().set_index("term")
                 {"AICc of Fertility ~ Education": r.loc["Fertility ~ Education", "AICc"],
                  "weight of the biggest": r.loc["Fertility ~ Education + Catholic + Infant.Mortality", "Akaike weight"]}
             """,
             parent="""
                 import numpy as np
                 import statsmodels.formula.api as smf
                 from statsmodels.tools import eval_measures
                 fs = ["Fertility ~ Education", "Fertility ~ Education + Catholic",
                       "Fertility ~ Education + Catholic + Q('Infant.Mortality')"]
                 fits = [smf.ols(f, data).fit() for f in fs]
                 a = np.array([eval_measures.aicc(f.llf, f.nobs, len(f.params) + 1) for f in fits])
                 w = np.exp(-(a - a.min()) / 2)
                 {"AICc of Fertility ~ Education": a[0], "weight of the biggest": (w / w.sum())[2]}
             """, parent_label="statsmodels OLS and eval_measures.aicc",
             r="""
                 ms <- list(a = lm(Fertility ~ Education), b = lm(Fertility ~ Education + Catholic),
                            c = lm(Fertility ~ Education + Catholic + Infant.Mortality))
                 t <- AICcmodavg::aictab(ms, modnames = names(ms), sort = FALSE)
                 list(`AICc of Fertility ~ Education` = t$AICc[1], `weight of the biggest` = t$AICcWt[3])
             """, r_packages=("AICcmodavg",), r_tolerance=1e-9),
        # ---- O14: left-out rows
        Case("table.compare_models", "check_on_left_out_rows=True: low birth weight from age, weight and smoking "
                                     "(Brier score in 10 parts)", "birthwt (MASS)", "real data",
             ours="""
                 r = sdata.table(data).compare_models("low", using=["age", "lwt", "smoke"], outcome="yes or no",
                                                      check_on_left_out_rows=True).as_pandas().iloc[0]
                 {"left out": r["Brier score on left-out rows"], "bias-corrected": r["Brier score on left-out rows (bias-corrected)"]}
             """,
             r="""
                 d <- data.frame(y = as.numeric(low == "yes"), age = age, lwt = lwt, smoke = smoke)
                 m <- glm(y ~ age + lwt + smoke, data = d, family = binomial)
                 set.seed(1)
                 cv <- boot::cv.glm(d, m, K = 10)
                 list(`left out` = cv$delta[1], `bias-corrected` = cv$delta[2])
             """, r_packages=("boot",), r_tolerance=1e-10,
             note="R boot::cv.glm with the same seed is the reference: the split is made by R's own random numbers."),
        # ---- O05: Breusch-Pagan
        Case("table.check_model_of", "Breusch-Pagan and White tests of the NIST Norris line", "NIST Norris",
             "real data",
             ours="""
                 page = sdata.table(data).check_model_of("y", using=["x"])
                 n = page._check_numbers
                 {"Breusch-Pagan": n["breusch_pagan"][0], "Breusch-Pagan p": n["breusch_pagan"][2],
                  "White": n["white"][0]}
             """,
             parent="""
                 import statsmodels.api as sm
                 from statsmodels.stats.diagnostic import het_breuschpagan, het_white
                 X = sm.add_constant(data["x"])
                 res = sm.OLS(data["y"], X).fit().resid
                 bp = het_breuschpagan(res, X, robust=True)
                 {"Breusch-Pagan": bp[0], "Breusch-Pagan p": bp[1], "White": het_white(res, X)[0]}
             """, parent_label="statsmodels het_breuschpagan, het_white",
             r="""
                 m <- lm(y ~ x)
                 list(`Breusch-Pagan` = unname(lmtest::bptest(m)$statistic), `Breusch-Pagan p` = lmtest::bptest(m)$p.value,
                      White = unname(lmtest::bptest(m, ~ x + I(x^2))$statistic))
             """, r_packages=("lmtest",), r_tolerance=1e-8),
        # ---- O13 + R07: calibration
        Case("table.check_model_of", "outcome=\"yes or no\": Hosmer-Lemeshow test and Brier score, low birth weight",
             "birthwt (MASS)", "real data",
             ours="""
                 page = sdata.table(data).check_model_of("low", using=["age", "lwt", "smoke"], outcome="yes or no")
                 n = page._check_numbers
                 {"Hosmer-Lemeshow": n["hosmer"][0], "Hosmer-Lemeshow p": n["hosmer"][2], "Brier": n["brier"]}
             """,
             r="""
                 m <- glm(as.numeric(low == "yes") ~ age + lwt + smoke, family = binomial)
                 h <- performance::performance_hosmer(m, n_bins = 10)
                 list(`Hosmer-Lemeshow` = unname(h$chisq), `Hosmer-Lemeshow p` = unname(h$p.value),
                      Brier = DescTools::BrierScore(m))
             """, r_packages=("performance", "DescTools"), r_tolerance=1e-6),
        # ---- N10, N12, N13, O18
        Case("table.find_model_averages_of", 'comparing="each with the first": each tension against the low one',
             "warpbreaks", "real data",
             ours="""
                 r = sdata.table(data).find_model_averages_of("breaks", for_each_group_in="tension",
                     using=["wool * tension"], comparing="each with the first", in_order=["L", "M", "H"])
                 r = r.as_pandas().set_index("term")
                 {"M minus L": r.loc["M minus L", "difference"], "H minus L": r.loc["H minus L", "difference"],
                  "p H minus L": r.loc["H minus L", "p-value (Dunnett)"]}
             """,
             r="""
                 d <- data.frame(y = breaks, w = factor(wool), t = factor(tension, levels = c("L", "M", "H")))
                 e <- emmeans::emmeans(lm(y ~ w * t, d), ~ t)
                 s <- as.data.frame(emmeans::contrast(e, "trt.vs.ctrl"))
                 list(`M minus L` = s$estimate[1], `H minus L` = s$estimate[2], `p H minus L` = s$p.value[2])
             """, r_packages=("emmeans",), r_tolerance=1e-6,
             note="R emmeans is the reference. Dunnett's p-values (dunnettx) come from a close approximation of the "
                  "multivariate t, so they agree to about 1e-6."),
        Case("table.find_model_averages_of", "within_each_group_in=: the interaction test and tension within each "
                                             "wool", "warpbreaks", "real data",
             ours="""
                 r = sdata.table(data).find_model_averages_of("breaks", for_each_group_in="tension",
                     using=["wool * tension"], within_each_group_in="wool").as_pandas().set_index("term")
                 {"interaction F": r.loc["interaction tension : wool", "statistic"],
                  "tension within A": r.loc["tension within wool A", "statistic"]}
             """,
             r="""
                 m <- lm(breaks ~ factor(wool) * factor(tension))
                 j <- as.data.frame(emmeans::joint_tests(m))
                 jb <- as.data.frame(emmeans::joint_tests(m, by = "wool"))
                 list(`interaction F` = j$F.ratio[3], `tension within A` = jb$F.ratio[1])
             """, r_packages=("emmeans",), r_tolerance=1e-9),
        Case("table.find_model_averages_of", "over_range_of=: model fertility across education", "swiss",
             "real data",
             ours="""
                 r = sdata.table(data).find_model_averages_of("Fertility", over_range_of="Education",
                     using=["Education", "Catholic"]).as_pandas()
                 {"first": r["model average"].iloc[0], "last": r["model average"].iloc[-1],
                  "last high": r["95 % CI high"].iloc[-1]}
             """,
             r="""
                 m <- lm(Fertility ~ Education + Catholic)
                 g <- seq(min(Education), max(Education), length.out = 50)
                 a <- as.data.frame(summary(emmeans::emmeans(m, ~ Education, at = list(Education = g))))
                 list(first = a$emmean[1], last = a$emmean[50], `last high` = a$upper.CL[50])
             """, r_packages=("emmeans",), r_tolerance=1e-10),
        Case("draw_interaction_lines", "the averages of warp breaks for each wool at each tension", "warpbreaks",
             "real data",
             ours="""
                 chart = sdata.chart(data).draw_interaction_lines(x="tension", y="breaks", colour="wool")
                 lines = [l for l in chart._render().axes[0].get_lines() if len(l.get_ydata()) == 3]
                 {"A at L": lines[0].get_ydata()[0], "B at H": lines[1].get_ydata()[2],
                  "A at L, interval low": lines[2].get_ydata()[0]}
             """,
             parent="""
                 from scipy import stats
                 a = data[(data["wool"] == "A") & (data["tension"] == "L")]["breaks"]
                 {"A at L": a.mean(), "B at H": data[(data["wool"] == "B") & (data["tension"] == "H")]["breaks"].mean(),
                  "A at L, interval low": stats.t.interval(0.95, len(a) - 1, loc=a.mean(), scale=stats.sem(a))[0]}
             """, parent_label="pandas mean, SciPy t.interval",
             r="""
                 a <- breaks[wool == "A" & tension == "L"]
                 list(`A at L` = mean(a), `B at H` = mean(breaks[wool == "B" & tension == "H"]),
                      `A at L, interval low` = t.test(a)$conf.int[1])
             """, r_tolerance=1e-12),
        # ---- M12: group levels
        Case("table.find_group_levels_of", "each driver's own starting reaction time and slope over days",
             "sleepstudy (lme4)", "real data",
             ours="""
                 r = sdata.table(data).find_group_levels_of("Reaction", using=["Days"], grouped_by="Subject",
                                                            own_slope_for="Days").as_pandas().set_index("term")
                 {"level of 308": r.loc["s308", "starting level (distance from the average)"],
                  "slope of 308": r.loc["s308", "slope for Days (distance from the average)"],
                  "own slope of 308": r.loc["s308", "own slope for Days"]}
             """,
             r="""
                 m <- lme4::lmer(Reaction ~ Days + (1 + Days | Subject))
                 re <- lme4::ranef(m)$Subject
                 list(`level of 308` = re["s308", 1], `slope of 308` = re["s308", 2],
                      `own slope of 308` = coef(m)$Subject["s308", 2])
             """, r_packages=("lme4",), r_tolerance=1e-6),
        # ---- N07, N09
        Case("table.compare_averages_of", "grouped_by=: nested ANOVA of liver glycogen, rats inside treatments",
             "rat liver glycogen", "published",
             ours="""
                 r = sdata.table(data).compare_averages_of("glycogen", for_each_group_in="treatment",
                                                           grouped_by="rat").as_pandas()
                 {"F": r["statistic"].iloc[0], "treatment SS": r["sum of squares"].iloc[0],
                  "rats SS": r["sum of squares"].iloc[1]}
             """,
             published={"F": (2.929, 0.0005, "Sokal & Rohlf (1981), Box 10.1"),
                        "treatment SS": (1557.56, 0.005, "Sokal & Rohlf (1981), Box 10.1"),
                        "rats SS": (797.67, 0.005, "Sokal & Rohlf (1981), Box 10.1")},
             r="""
                 a <- summary(aov(glycogen ~ treatment + Error(rat)))[["Error: rat"]][[1]]
                 list(F = a[["F value"]][1], `treatment SS` = a[["Sum Sq"]][1], `rats SS` = a[["Sum Sq"]][2])
             """, r_tolerance=1e-10,
             note="The book's three-level table (rats, preparations, readings) tests treatments against rats with "
                  "the same F as the two-level table here, because the design is balanced."),
        Case("table.compare_averages_of", "a list of columns: MANOVA of sepal and petal length across species",
             "iris", "real data",
             ours="""
                 r = sdata.table(data).compare_averages_of(["Sepal.Length", "Petal.Length"],
                                                           for_each_group_in="Species").as_pandas()
                 {"Pillai": r["statistic"].iloc[0], "F": r["F"].iloc[0], "Wilks": r["statistic"].iloc[1]}
             """,
             parent="""
                 from statsmodels.multivariate.manova import MANOVA
                 d = data.rename(columns={"Sepal.Length": "a", "Petal.Length": "b"})
                 s = MANOVA.from_formula("a + b ~ Species", data=d).mv_test().results["Species"]["stat"]
                 {"Pillai": s.loc["Pillai's trace", "Value"], "F": s.loc["Pillai's trace", "F Value"],
                  "Wilks": s.loc["Wilks' lambda", "Value"]}
             """, parent_label="statsmodels MANOVA",
             r="""
                 m <- manova(cbind(Sepal.Length, Petal.Length) ~ Species)
                 p <- summary(m)$stats
                 list(Pillai = p[1, 2], F = p[1, 3], Wilks = summary(m, test = "Wilks")$stats[1, 2])
             """, r_tolerance=1e-10),
    ]


def add_to(namespace) -> None:
    """Add the S3a-3 datasets and cases to cases.py, and teach its load() the datasets read from R."""
    Dataset, Case = namespace["Dataset"], namespace["Case"]
    for d in _datasets(Dataset):
        namespace["DATASETS"][d.name] = d
    import dataclasses

    # the R packages simplydata's own side calls (Case.ours_r: skipped without them, failed under --require-r),
    # and the option each case checks (Case.option)
    needs = {"table.explain": ("nlme",), "table.find_columns_that_predict": ("glmnet",),
             "table.find_model_averages_of": ("emmeans",), "table.find_group_levels_of": ("lme4",)}
    cases = []
    for c in _cases(Case):
        ours_r = needs.get(c.word)
        if "check_on_left_out_rows" in c.ours:
            ours_r = ("boot",)
        if c.word == "table.compare_averages_of" and "grouped_by=" in c.ours:
            ours_r = ("lme4",)
        if c.word == "table.check_model_of" and 'outcome="yes or no"' in c.ours:
            ours_r = ("performance",)
        option = c.title.split(":")[0] if "=" in c.title.split(":")[0] else ""
        if option.startswith("using="):
            option = "using=[[...], [...]]"  # the key of the underneath entry of a list of models
        if c.word == "table.compare_averages_of" and "a list of columns" in c.title:
            option = "for_each_group_in= with a list of columns"
        cases.append(dataclasses.replace(c, ours_r=ours_r, option=option))
    namespace["CASES"].extend(cases)
    namespace.setdefault("R_DATA", {}).update({name: packages for name, (packages, _) in R_DATA_CHECKING.items()})
    plain_load = namespace["load"]

    def load(name: str) -> pd.DataFrame:
        if name in R_DATA_CHECKING:
            from simplydata._r import need_r, r_call

            packages, code = R_DATA_CHECKING[name]
            need_r(packages, f"the {name} data")  # checked, not attached: the code names its package
            found = r_call(code, what=f"the {name} data")
            return pd.DataFrame({k: (np.asarray(v, dtype=float) if np.asarray(v).dtype.kind in "iuf" else list(v))
                                 for k, v in found.items()})
        return plain_load(name)

    namespace["load"] = load
