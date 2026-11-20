"""Checking and comparing (phase S3a-3): the new words find_columns_that_predict, find_group_levels_of and
draw_interaction_lines (ENTRIES), and one entry for each new option of explain, compare_models,
find_model_averages_of and compare_averages_of (OPTION_ENTRIES, keyed by word and option).
"""

from . import Entry

SENTENCE = "simplydata also writes the result as sentences, with the p-value in words, and names the method."
SCHOOL = """
    df = sdata.get_example("school").dropna(subset=["marks", "hours", "breakfast", "sleep"])
    marks = df["marks"].to_numpy(dtype=float)
    hours = df["hours"].to_numpy(dtype=float)
    sleep = df["sleep"].to_numpy(dtype=float)
    breakfast = df["breakfast"].to_numpy(dtype=object)
    school = df["school"].to_numpy(dtype=object)
    group = df["class"].to_numpy(dtype=object)
"""
RATS = """
    import numpy as np
    treatment = np.array(["control"] * 12 + ["glucose"] * 12 + ["glucose and fructose"] * 12, dtype=object)
    rat = np.array([f"rat {i // 6 + 1}" for i in range(36)], dtype=object)
    glycogen = np.array([131, 130, 131, 125, 136, 142, 150, 148, 140, 143, 160, 150, 157, 145, 154, 142, 147, 153,
                         151, 155, 147, 147, 162, 152, 134, 125, 138, 138, 135, 136, 138, 140, 139, 138, 134, 127],
                        dtype=float)
"""

ENTRIES = [
    Entry(
        word="table.find_columns_that_predict",
        data="school",
        ours="""
            table = sdata.table(sdata.get_example("school"))
            result = table.find_columns_that_predict("marks", using=["hours", "sleep"])
            result.as_pandas().query("term == 'hours'")
        """,
        code={
            "R": """
                # find_columns_that_predict("marks", using=["hours", "sleep"])
                # marks, hours, sleep: the rows of sdata.get_example("school") with every cell given
                set.seed(1)                                                         # (1)
                fit <- glmnet::cv.glmnet(cbind(hours, sleep), marks, alpha = 1, nfolds = 10)  # (2)
                b <- as.numeric(coef(fit, s = "lambda.1se"))                         # (3)
                list(hours = b[2])
            """,
            "Python": """
                {"effect": hours}
            """,
        },
        r_inputs=SCHOOL,
        r_packages=("glmnet",),
        compare="result",
        fields=("effect",),
        tolerance=1e-9,
        choices=("the random split into 10 parts is made in R itself (with_seed=1 is set.seed(1)), so R's own random "
                 "numbers give the same parts.",
                 "the lasso (alpha = 1) with 10 parts; method=\"elastic net\" is alpha = 0.5.",
                 "the penalty is lambda.1se, the largest within one standard error of the best (fewer columns, "
                 "steadier); simplydata names it, so a change of glmnet's default cannot change the answer."),
        python_note="Python has no cross-validated lasso for these models outside scikit-learn, which simplydata "
                    "leaves out, so the numbers come from R glmnet.",
        also="simplydata also turns text columns into 0/1 columns, prints the cross-validated error and says why there "
             "are no p-values.",
    ),
    Entry(
        word="table.find_group_levels_of",
        data="school",
        ours="""
            table = sdata.table(sdata.get_example("school"))
            result = table.find_group_levels_of("marks", using=["hours"], grouped_by="school")
            result.as_pandas().query("term == 'School A'")
        """,
        code={
            "R": """
                # find_group_levels_of("marks", using=["hours"], grouped_by="school")
                m <- lme4::lmer(marks ~ hours + (1 | school), REML = TRUE)
                re <- lme4::ranef(m, condVar = TRUE)$school                    # (1)
                sd <- sqrt(attr(re, "postVar")[1, 1, ])
                a <- rownames(re) == "School A"
                list(level = re[a, 1], low = re[a, 1] - 1.959964 * sd[a],      # (2)
                     own = coef(m)$school[a, 1])
            """,
            "Python": """
                {"starting level (distance from the average)": level,
                 "starting level 95 % interval low": low, "own starting level": own}
            """,
        },
        r_inputs=SCHOOL.replace('"breakfast", "sleep"', '"school"'),
        r_packages=("lme4",),
        compare="result",
        fields=("starting level (distance from the average)", "starting level 95 % interval low",
                "own starting level"),
        tolerance=1e-6,
        choices=("condVar = TRUE: each level comes with its conditional variance; without it ranef() gives no "
                 "uncertainty.",
                 "the 95 % interval is the level plus and minus 1.96 conditional standard deviations, as "
                 "lattice::dotplot(ranef(m, condVar = TRUE)) draws it."),
        python_note="statsmodels MixedLM gives the same levels for random intercepts (random_effects), but its "
                    "conditional variances differ from lme4's, so the intervals come from R.",
        also="simplydata also sorts the groups, adds own slopes with own_slope_for=, and prints and stores the warning "
             "that the levels are not data for later tests.",
    ),
    Entry(
        word="draw_interaction_lines",
        data="school",
        ours="""
            chart = sdata.chart(sdata.get_example("school"))
            chart.draw_interaction_lines(x="class", y="marks", colour="breakfast")
        """,
        code={"seaborn": """
            import seaborn as sns
            from scipy import stats
            df = sdata.get_example("school")
            # draw_interaction_lines(x="class", y="marks", colour="breakfast")
            def t95(v):                                                       # (1)
                return stats.t.interval(0.95, len(v) - 1, loc=v.mean(), scale=stats.sem(v))
            sns.pointplot(data=df, x="class", y="marks", hue="breakfast",
                          errorbar=t95, dodge=0.15, capsize=0.1)               # (2)
        """},
        compare="chart",
        check=("labels", "legend", "dots"),
        choices=("95 % t intervals of each average, as R t.test(); seaborn's own default is a bootstrap interval, "
                 "which changes from run to run.",
                 "the groups are moved a little apart (dodged) so their bars do not hide each other."),
        also="simplydata also prints how to read the picture (parallel lines or not) and the explain() call that tests "
             "the interaction. Its averages and intervals are checked against pandas and SciPy in the tests.",
    ),
]


OPTION_ENTRIES = [
    Entry(
        word="table.explain",
        option='spread_changes_with="school"',
        data="school",
        ours="""
            table = sdata.table(sdata.get_example("school"))
            result = table.explain("marks", using=["hours"], spread_changes_with="school")
            result.as_pandas().query("term == 'hours'")
        """,
        code={
            "R": """
                # explain("marks", using=["hours"], spread_changes_with="school")
                m <- nlme::gls(marks ~ hours, method = "REML",                      # (1)
                               weights = nlme::varIdent(form = ~ 1 | school))     # (2)
                t <- summary(m)$tTable
                list(effect = t[2, 1], se = t[2, 2], p = t[2, 4])
            """,
            "Python": """
                {"effect": effect, "standard error": se, "p-value": p}
            """,
        },
        r_inputs=SCHOOL.replace('"breakfast", "sleep"', '"school"'),
        r_packages=("nlme",),
        compare="result",
        fields=("effect", "standard error", "p-value"),
        tolerance=1e-5,
        choices=("REML, nlme's default, for the effects.",
                 "a group column gives each group its own spread (varIdent); a number column would give a spread "
                 "that grows as a power of it (varPower)."),
        python_note="statsmodels has GLSAR (iterated, not likelihood) and no variance functions, so the model comes "
                    "from R nlme.",
        also="simplydata also prints each group's spread against the first, the AIC with and without the spread part "
             "and the likelihood-ratio test between them. " + SENTENCE,
    ),
    Entry(
        word="table.explain",
        option='neighbours_alike_in_order_of="year"',
        data="made-up",
        ours="""
            years = list(range(1, 41))
            level = [10 + 0.1 * t + (1.5 if t % 7 < 3 else -1.0) + (0.5 if t % 3 else -0.4) for t in years]
            table = sdata.table({"year": years, "level": level})
            result = table.explain("level", using=["year"], neighbours_alike_in_order_of="year")
            result.as_pandas().query("term == 'year'")
        """,
        code={
            "R": """
                # explain("level", using=["year"], neighbours_alike_in_order_of="year")
                year <- 1:40
                level <- 10 + 0.1 * year + ifelse(year %% 7 < 3, 1.5, -1) + ifelse(year %% 3 != 0, 0.5, -0.4)
                m <- nlme::gls(level ~ year, method = "REML",
                               correlation = nlme::corAR1(form = ~ year))         # (1)
                list(effect = coef(m)[2], se = sqrt(vcov(m)[2, 2]))
            """,
            "Python": """
                {"effect": effect, "standard error": se}
            """,
        },
        r_inputs="""
            import numpy as np
            unused = np.zeros(1)
        """,
        r_packages=("nlme",),
        compare="result",
        fields=("effect", "standard error"),
        tolerance=1e-5,
        choices=("evenly spaced values give the AR(1) correlation (corAR1), each step one step apart; uneven gaps "
                 "give corCAR1, which allows for the size of each gap.",),
        python_note="statsmodels GLSAR iterates instead of maximising the likelihood, so the model comes from R nlme.",
        also="simplydata also prints the correlation of neighbours with its interval and the comparison with the model "
             "without it. " + SENTENCE,
    ),
    Entry(
        word="table.compare_models",
        option="using=[[...], [...]]",
        data="school",
        ours="""
            table = sdata.table(sdata.get_example("school"))
            result = table.compare_models("marks", using=[["hours"], ["hours", "breakfast"]])
            result.as_pandas().query("term == 'marks ~ hours'")
        """,
        code={"statsmodels": """
            import numpy as np
            import statsmodels.formula.api as smf
            from statsmodels.tools import eval_measures
            df = sdata.get_example("school").dropna(subset=["marks", "hours", "breakfast"])
            # compare_models("marks", using=[["hours"], ["hours", "breakfast"]])
            fits = [smf.ols(f, df).fit() for f in ("marks ~ hours", "marks ~ hours + breakfast")]
            k = [len(f.params) + 1 for f in fits]                                 # (1)
            aic = [eval_measures.aic(f.llf, f.nobs, kk) for f, kk in zip(fits, k)]
            aicc = [eval_measures.aicc(f.llf, f.nobs, kk) for f, kk in zip(fits, k)]
            use = aicc if len(df) / max(k) < 40 else aic                          # (2)
            w = np.exp(-(np.array(use) - min(use)) / 2)
            {"AICc": aicc[0], "Akaike weight": (w / w.sum())[0]}
        """},
        compare="result",
        fields=("AICc", "Akaike weight"),
        tolerance=1e-9,
        choices=("every value estimated counts, the residual spread too, as R logLik(); statsmodels' own aic leaves "
                 "it out (a difference of 2).",
                 "AICc when there are fewer than 40 rows per value estimated (Burnham & Anderson 2002), else AIC."),
        also="simplydata also fits every model on the same rows, sorts them and prints the differences and weights in "
             "words.",
    ),
    Entry(
        word="table.compare_models",
        option="check_on_left_out_rows=True",
        data="school",
        ours="""
            table = sdata.table(sdata.get_example("school"))
            result = table.compare_models("marks", using=["hours"], check_on_left_out_rows=True)
            result.as_pandas()
        """,
        code={
            "R": """
                # compare_models("marks", using=["hours"], check_on_left_out_rows=True)
                d <- data.frame(marks = marks, hours = hours)
                m <- glm(marks ~ hours, data = d)
                set.seed(1)                                                   # (1)
                cv <- boot::cv.glm(d, m, K = 10)                              # (2)
                list(left_out = cv$delta[1], adjusted = cv$delta[2])
            """,
            "Python": """
                {"mean squared error on left-out rows": left_out,
                 "mean squared error on left-out rows (adjusted)": adjusted}
            """,
        },
        r_inputs=SCHOOL.replace('"breakfast", "sleep"', '"hours"'),
        r_packages=("boot",),
        compare="result",
        fields=("mean squared error on left-out rows", "mean squared error on left-out rows (adjusted)"),
        tolerance=1e-9,
        choices=("with_seed=1 is set.seed(1) in R, so R's own random numbers make the parts.",
                 "K = 10 parts: cv.glm's own default leaves out one row at a time."),
        python_note="statsmodels has no k-fold cross-validation, so it comes from R boot.",
        also="simplydata also prints the error on the rows the model was fitted to, for comparison.",
    ),
    Entry(
        word="table.find_model_averages_of",
        option='comparing="each with the first"',
        data="school",
        ours="""
            table = sdata.table(sdata.get_example("school"))
            result = table.find_model_averages_of("marks", for_each_group_in="class", using=["hours", "class"],
                                                  comparing="each with the first")
            result.as_pandas().query("term == 'green minus blue'")
        """,
        code={
            "R": """
                # find_model_averages_of(..., comparing="each with the first")
                m <- lm(marks ~ hours + group)
                e <- emmeans::emmeans(m, ~ group)
                s <- summary(emmeans::contrast(e, method = "trt.vs.ctrl"),       # (1)
                             infer = c(TRUE, TRUE))
                list(d = s$estimate[1], p = s$p.value[1])                         # (2)
            """,
            "Python": """
                {"difference": d, "p-value (dunnettx)": p}
            """,
        },
        r_inputs=SCHOOL.replace('"breakfast", "sleep"', '"class"'),
        r_packages=("emmeans",),
        compare="result",
        fields=("difference", "p-value (dunnettx)"),
        tolerance=1e-6,
        choices=("each group against the first group (in sorted order, or the first of in_order=).",
                 "emmeans' own adjustment for this method (dunnettx), printed by simplydata."),
        python_note="no Python package gives emmeans' averages over a reference grid.",
        also="simplydata also prints the model averages, which adjustment was used, and how to put another group first. "
             + SENTENCE,
    ),
    Entry(
        word="table.find_model_averages_of",
        option='within_each_group_in="breakfast"',
        data="school",
        ours="""
            table = sdata.table(sdata.get_example("school"))
            result = table.find_model_averages_of("marks", for_each_group_in="class", using=["class * breakfast"],
                                                  within_each_group_in="breakfast")
            result.as_pandas().query("term == 'interaction class : breakfast'")
        """,
        code={
            "R": """
                # find_model_averages_of(..., within_each_group_in="breakfast")
                m <- lm(marks ~ group * breakfast)
                j <- as.data.frame(emmeans::joint_tests(m))                  # (1)
                i <- j[[1]] == "group:breakfast"
                list(f = j$F.ratio[i], p = j$p.value[i])
            """,
            "Python": """
                {"statistic": f, "p-value": p}
            """,
        },
        r_inputs=SCHOOL.replace('"breakfast", "sleep"', '"breakfast", "class"'),
        r_packages=("emmeans",),
        compare="result",
        fields=("statistic", "p-value"),
        tolerance=1e-8,
        choices=("the interaction test comes first (emmeans joint_tests()), and the comparisons within each group "
                 "after it: compare the groups with the interaction test, not by which simple effects have small "
                 "p-values (Gelman & Stern 2006).",),
        python_note="no Python package gives emmeans' joint tests and simple effects.",
        also="simplydata also prints the F test of class within each breakfast group (joint_tests(m, by =)) and each "
             "pair of classes there. " + SENTENCE,
    ),
    Entry(
        word="table.find_model_averages_of",
        option='over_range_of="hours"',
        data="school",
        ours="""
            table = sdata.table(sdata.get_example("school"))
            result = table.find_model_averages_of("marks", over_range_of="hours", using=["hours", "breakfast"])
            result.as_pandas()
        """,
        code={
            "R": """
                # find_model_averages_of("marks", over_range_of="hours", using=["hours", "breakfast"])
                m <- lm(marks ~ hours + breakfast)
                grid <- seq(min(hours), max(hours), length.out = 50)            # (1)
                e <- emmeans::emmeans(m, ~ hours, at = list(hours = grid))      # (2)
                a <- as.data.frame(summary(e))
                list(first = a$emmean[1], low = a$lower.CL[1])
            """,
            "Python": """
                {"model average": first, "95 % CI low": low}
            """,
        },
        r_inputs=SCHOOL.replace('"breakfast", "sleep"', '"breakfast"'),
        r_packages=("emmeans",),
        compare="result",
        fields=("model average", "95 % CI low"),
        tolerance=1e-9,
        choices=("50 evenly spaced values from the smallest to the largest hours.",
                 "the other columns as emmeans holds them: numbers at their average, groups counted equally."),
        python_note="no Python package gives emmeans' averages over a reference grid; add_predicted_column(interval=95) "
                    "gives the predictions at the rows' own values without R.",
        also="simplydata also prints the chart recipe (draw_lines and draw_band) for the table it gives back.",
    ),
    Entry(
        word="table.compare_averages_of",
        option='grouped_by="rat"',
        data="made-up",
        ours="""
            rats = {"treatment": ["control"] * 12 + ["glucose"] * 12 + ["glucose and fructose"] * 12,
                    "rat": [f"rat {i // 6 + 1}" for i in range(36)],
                    "glycogen": [131, 130, 131, 125, 136, 142, 150, 148, 140, 143, 160, 150, 157, 145, 154, 142, 147,
                                 153, 151, 155, 147, 147, 162, 152, 134, 125, 138, 138, 135, 136, 138, 140, 139, 138,
                                 134, 127]}
            sdata.table(rats).compare_averages_of("glycogen", for_each_group_in="treatment", grouped_by="rat")
        """,
        code={
            "R": """
                # compare_averages_of("glycogen", for_each_group_in="treatment", grouped_by="rat")
                # the rat liver glycogen data of Sokal & Rohlf (Box 10.1), 6 readings per rat
                a <- summary(stats::aov(glycogen ~ treatment + Error(rat)))      # (1)
                top <- a[["Error: rat"]][[1]]
                list(f = top[["F value"]][1], p = top[["Pr(>F)"]][1])
            """,
            "Python": """
                {"statistic": f, "p-value": p}
            """,
        },
        r_inputs=RATS,
        r_packages=("lme4",),
        compare="result",
        fields=("statistic", "p-value"),
        tolerance=1e-9,
        choices=("the treatment is tested against the variation between rats (Error(rat)), not between readings: "
                 "the readings of one rat are not independent.",),
        python_note="statsmodels has no Error() strata, so the table comes from R aov().",
        also="simplydata also prints the averages and the variances between and within rats (R lme4::lmer), and a "
             "note when the design is unbalanced. " + SENTENCE,
    ),
    Entry(
        word="table.compare_averages_of",
        option="for_each_group_in= with a list of columns",
        data="school",
        ours="""
            table = sdata.table(sdata.get_example("school"))
            result = table.compare_averages_of(["marks", "hours"], for_each_group_in="class")
            result.as_pandas()
        """,
        code={"statsmodels": """
            from statsmodels.multivariate.manova import MANOVA
            df = sdata.get_example("school").dropna(subset=["marks", "hours"])
            # compare_averages_of(["marks", "hours"], for_each_group_in="class")
            test = MANOVA.from_formula("marks + hours ~ C(Q('class'))", data=df).mv_test()
            row = test.results["C(Q('class'))"]["stat"].loc["Pillai's trace"]   # (1)
            {"statistic": row["Value"], "F": row["F Value"], "p-value": row["Pr > F"]}
        """},
        compare="result",
        fields=("statistic", "F", "p-value"),
        tolerance=1e-9,
        choices=("Pillai's trace first, the one R summary(manova()) prints by default and the safest when groups "
                 "differ in size or spread.",),
        also="simplydata also prints each group's averages and keeps Wilks, Hotelling-Lawley and Roy in the table. "
             + SENTENCE,
    ),
]
