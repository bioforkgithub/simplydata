"""Epidemiology and cause and effect (phase S3d-2): compare_balanced_groups_of and its matching option, and one
entry for each new option that changes what a word calls (keyed by word and option): attributable fractions on
compare_risks, direct standardisation on rate_of, observed / expected on compare_rates, mediation on explain, the 2 x 2
crossover on compare_averages_of, and multiple imputation on find_correlation_between and explain_survival.
Practice tables: "job_training", "job_search", "drug_levels" (real), "deaths_by_age", "clinic", "school", "trial"
(made up).
"""

from . import Entry

LALONDE = """
    df = sdata.get_example("job_training")
    t = df["treat"].to_numpy(dtype=float)
    y = df["re78"].to_numpy(dtype=float)
    age, educ, married, nodegree = (df[c].to_numpy(dtype=float) for c in ("age", "educ", "married", "nodegree"))
    re74, re75 = df["re74"].to_numpy(dtype=float), df["re75"].to_numpy(dtype=float)
    race = df["race"].to_numpy(dtype=object)
"""
COLUMNS = '["age", "educ", "race", "married", "nodegree", "re74", "re75"]'
FRAME_R = ("d <- data.frame(t = t, y = y, age = age, educ = educ, race = race, married = married, nodegree = nodegree,\n"
           "                re74 = re74, re75 = re75)\n"
           "f <- t ~ age + educ + race + married + nodegree + re74 + re75")
DEATHS = """
    import numpy as np
    df = sdata.get_example("deaths_by_age")
    obs = df.pivot(index="county", columns="age_band", values="deaths")
    tar = df.pivot(index="county", columns="age_band", values="person_years")
    o, t = obs.to_numpy(dtype=float), tar.to_numpy(dtype=float)
    g, b = obs.index.to_numpy(dtype=object), obs.columns.to_numpy(dtype=object)
"""
NATIONAL = '{"0-19": 0.3, "20-39": 1.0, "40-59": 4.0, "60-69": 12.0, "70-79": 30.0, "80+": 90.0}'
FILL_IN = """
    import numpy as np
    import pandas as pd
    from statsmodels.imputation.mice import MICEData
    import simplydata._r as r
    r.need_r(("mice",), "mice")                                     # R first, as simplydata does
    df = sdata.get_example("school")
    imputer = MICEData(pd.DataFrame({"v0": df["sleep"], "v1": df["marks"].astype(float)}), k_pmm=5, rng=1)
    imputer.update_all(10)                                          # 10 cycles before the first table
    tables = []
    for _ in range(20):                                             # 20 tables, 3 cycles apart
        imputer.update_all(3)
        tables.append(imputer.data[["v0", "v1"]].to_numpy(dtype=float))
    X = np.vstack(tables)
"""
EPIR_NOTE = ("No Python package gives attributable fractions, Fay-Feuer intervals or indirect standardisation as R "
             "epiR does, so the numbers come from R.")

ENTRIES = [
    # ------------------------------------------------------------------ AD01-AD03: balancing groups
    Entry(
        word="table.compare_balanced_groups_of",
        data="job_training",
        ours=f"""
            table = sdata.table(sdata.get_example("job_training"))
            table.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for={COLUMNS})
        """,
        code={
            "R": f"""
                # compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for=[...])
                {FRAME_R.replace(chr(10), chr(10) + '                ')}
                W <- WeightIt::weightit(f, data = d, method = "glm", estimand = "ATE")   # (1)
                m <- WeightIt::glm_weightit(y ~ t, data = d, weightit = W,              # (2)
                                          family = stats::gaussian())
                co <- summary(m)$coefficients; ci <- stats::confint(m)
                b <- cobalt::bal.tab(W, un = TRUE, binary = "std", continuous = "std")   # (3)
                list(estimate = co["t", 1], se = co["t", 2], p = co["t", 4], low = ci["t", 1], high = ci["t", 2])
            """,
            "Python": """
                {"estimate": estimate, "standard error": se, "p-value": p, "estimate 95 % CI low": low,
                 "estimate 95 % CI high": high}
            """,
        },
        r_inputs=LALONDE, r_packages=("WeightIt", "cobalt"), compare="result",
        fields=("estimate", "standard error", "p-value", "estimate 95 % CI low", "estimate 95 % CI high"),
        tolerance=1e-9,
        choices=("weighting by the inverse of the propensity score from logistic regression, for everyone (ATE), "
                 "unless effect_for= names a group (ATT).",
                 "the effect from WeightIt's lm_weightit(), whose M-estimation standard errors allow for the "
                 "estimated weights (statsmodels TreatmentEffect.ipw gives the same estimate with a larger error).",
                 "standardised differences for every column, text columns too (binary = \"std\"), with the guide 0.1; "
                 "never p-values for balance (Austin 2009)."),
        python_note="statsmodels TreatmentEffect.ipw gives the same estimate, but its standard error ignores how the "
                    "weights were estimated in WeightIt's way, so the numbers come from R WeightIt.",
        also="simplydata also prints the overlap of the scores (rows outside the other group's range), the balance "
             "table, notes on columns still apart after weighting and on weights above 20, and the assumptions the "
             "effect rests on.",
    ),
    Entry(
        word="table.compare_balanced_groups_of", option='test_method="matching"',
        data="job_training",
        ours=f"""
            table = sdata.table(sdata.get_example("job_training"))
            table.compare_balanced_groups_of("re78", for_each_group_in="treat", allowing_for={COLUMNS},
                                             test_method="matching", effect_for=1)
        """,
        code={
            "R": f"""
                # compare_balanced_groups_of(..., test_method="matching", effect_for=1)
                {FRAME_R.replace(chr(10), chr(10) + '                ')}
                mm <- MatchIt::matchit(f, data = d, method = "nearest", distance = "glm")   # (1)
                md <- MatchIt::match.data(mm)
                m <- stats::lm(y ~ t, data = md, weights = weights)
                V <- sandwich::vcovCL(m, cluster = ~subclass)                               # (2)
                co <- lmtest::coeftest(m, vcov. = V); ci <- lmtest::coefci(m, vcov. = V)
                list(estimate = co["t", 1], se = co["t", 2], p = co["t", 4], low = ci["t", 1], high = ci["t", 2])
            """,
            "Python": """
                {"estimate": estimate, "standard error": se, "p-value": p, "estimate 95 % CI low": low,
                 "estimate 95 % CI high": high}
            """,
        },
        r_inputs=LALONDE, r_packages=("MatchIt", "sandwich", "lmtest"), compare="result",
        fields=("estimate", "standard error", "p-value", "estimate 95 % CI low", "estimate 95 % CI high"),
        tolerance=1e-9,
        choices=("1:1 nearest-neighbour matching on the propensity score without replacement, MatchIt's default; "
                 "match_within= adds a caliper in standard deviations of the logit of the score (Austin 2011).",
                 "standard errors clustered on the matched pairs, as the MatchIt vignette does."),
        python_note="No Python package in simplydata's dependencies matches on the propensity score as MatchIt does, "
                    "so the numbers come from R.",
        also="simplydata also asks which group the effect is for (effect_for=; matching gives the effect among one "
             "group), counts the rows left without a match, prints the balance table and the assumptions.",
    ),
    # ------------------------------------------------------------------ S03: attributable fractions
    Entry(
        word="table.compare_risks", option='show="attributable fractions"',
        data="clinic",
        ours="""
            table = sdata.table(sdata.get_example("clinic"))
            table.compare_risks("infected", for_each_group_in="ward", against="ward A", show="attributable fractions")
        """,
        code={
            "R": """
                # compare_risks("infected", for_each_group_in="ward", against="ward A", show="attributable fractions")
                r <- epiR::epi.2by2(as.table(matrix(n, nrow = 2, byrow = TRUE)),   # (1)
                                    method = "cohort.count")
                af <- r$massoc.detail$AFRisk.strata.wald
                list(af = af$est, low = af$lower, high = af$upper)
            """,
            "Python": """
                {"estimate": af, "estimate 95 % CI low": low, "estimate 95 % CI high": high}
            """,
        },
        r_inputs="""
            import numpy as np
            df = sdata.get_example("clinic")
            b, a = df[df["ward"] == "ward B"], df[df["ward"] == "ward A"]
            e1, e0 = (b["infected"] == "yes").sum(), (a["infected"] == "yes").sum()
            n = np.array([e1, len(b) - e1, e0, len(a) - e0], dtype=float)   # exposed first, events first
        """,
        r_packages=("epiR",), compare="result", fields=("estimate", "estimate 95 % CI low", "estimate 95 % CI high"),
        tolerance=1e-9,
        choices=("the risk-based fractions of a cohort (method = \"cohort.count\"), with Wald intervals from the risk "
                 "ratio; crude, not adjusted for other columns.",),
        python_note=EPIR_NOTE,
        also="simplydata also gives the population attributable fraction, the preventable fraction among the exposed "
             "when the exposure goes with fewer events, and says that the fractions are causal only if the exposure "
             "causes the events.",
    ),
    # ------------------------------------------------------------------ S07: standardisation
    Entry(
        word="table.rate_of", option="standard_population=",
        data="deaths_by_age",
        ours="""
            table = sdata.table(sdata.get_example("deaths_by_age"))
            table.rate_of("deaths", time="person_years", for_each_group_in="county", allowing_for="age_band",
                          standard_population="whole table")
        """,
        code={
            "R": """
                # rate_of(..., allowing_for="age_band", standard_population="whole table")
                obs <- matrix(o, nrow = length(g), dimnames = list(g, b))
                tar <- matrix(t, nrow = length(g), dimnames = list(g, b))
                std <- matrix(colSums(tar), nrow = 1, dimnames = list("", b))   # (1)
                r <- epiR::epi.directadj(obs, tar, std, units = 1000)          # (2)
                a <- r$adj.strata
                list(adj = a$est[1], low = a$lower[1], high = a$upper[1])
            """,
            "Python": """
                {"adjusted rate": adj, "adjusted rate 95 % CI low": low, "adjusted rate 95 % CI high": high}
            """,
        },
        r_inputs=DEATHS, r_packages=("epiR",), compare="result",
        fields=("adjusted rate", "adjusted rate 95 % CI low", "adjusted rate 95 % CI high"), tolerance=1e-9,
        choices=("\"whole table\": the standard population is the person-time of all rows in each band.",
                 "direct standardisation with Fay & Feuer's gamma interval (epiR, the same as epitools::ageadjust."
                 "direct())."),
        python_note=EPIR_NOTE,
        also="simplydata also takes a standard population table, refuses bands missing on either side and groups "
             "with no person-time in a band, and prints the crude rate beside the adjusted one.",
    ),
    Entry(
        word="table.compare_rates", option="standard_rates=",
        data="deaths_by_age",
        ours=f"""
            table = sdata.table(sdata.get_example("deaths_by_age"))
            table.compare_rates("deaths", time="person_years", for_each_group_in="county", allowing_for="age_band",
                                standard_rates={NATIONAL})
        """,
        code={
            "R": """
                # compare_rates(..., allowing_for="age_band", standard_rates={...})   (per 1000 person-years)
                obs <- matrix(rowSums(matrix(o, nrow = length(g))), ncol = 1, dimnames = list(g, ""))
                pop <- matrix(t, nrow = length(g), dimnames = list(g, b))
                std <- matrix(c(s / 1000, NA), nrow = 1, dimnames = list("", c(b, "Total")))   # (1)
                r <- epiR::epi.indirectadj(obs, pop, std, units = 1000)                        # (2)
                sm <- r$smr.strata["Eastmere", ]                                               # by name
                list(smr = sm$est, low = sm$lower, high = sm$upper, e = sm$exp,
                     p = stats::poisson.test(sm$obs, sm$exp)$p.value)
            """,
            "Python": """
                {"observed / expected": smr, "observed / expected 95 % CI low": low,
                 "observed / expected 95 % CI high": high, "expected": e, "p-value": p}
            """,
        },
        r_inputs=DEATHS + "    s = np.array([0.3, 1.0, 4.0, 12.0, 30.0, 90.0])\n",
        r_packages=("epiR",), compare="result",
        fields=("observed / expected", "observed / expected 95 % CI low", "observed / expected 95 % CI high",
                "expected", "p-value"), tolerance=1e-9,
        choices=("the standard rates are read per per= units of time (1000 here) and divided by it for epiR, which "
                 "wants rates per one unit.",
                 "observed / expected with the exact Poisson interval; the p-value from R poisson.test(observed, "
                 "expected)."),
        python_note=EPIR_NOTE,
        also="simplydata also refuses bands without a standard rate and groups without person-time, and says that "
             "two groups' ratios are each against the standard, not against each other.",
    ),
    # ------------------------------------------------------------------ AD07: mediation
    Entry(
        word="table.explain", option="through=",
        data="job_search",
        ours="""
            table = sdata.table(sdata.get_example("job_search"))
            table.explain("depress2", using="treat", through="job_seek", allowing_for=["econ_hard", "sex", "age"])
        """,
        code={"statsmodels": """
            import statsmodels.formula.api as smf
            from statsmodels.stats.mediation import Mediation
            df = sdata.get_example("job_search")
            # explain("depress2", using="treat", through="job_seek", allowing_for=["econ_hard", "sex", "age"])
            mediator = smf.ols("job_seek ~ treat + econ_hard + sex + age", data=df)            # (1)
            outcome = smf.ols("depress2 ~ treat + job_seek + econ_hard + sex + age", data=df)
            summary = Mediation(outcome, mediator, "treat", "job_seek").fit(n_rep=1000, rng=1).summary   # (2)
            s = summary()
            {"estimate": s.loc["ACME (average)", "Estimate"], "95 % CI low": s.loc["ACME (average)", "Lower CI bound"],
             "95 % CI high": s.loc["ACME (average)", "Upper CI bound"], "p-value": s.loc["ACME (average)", "P-value"]}
        """},
        compare="result", row="indirect effect (through job_seek)",
        fields=("estimate", "95 % CI low", "95 % CI high", "p-value"), tolerance=1e-9,
        choices=("least squares for a column of numbers, logistic regression for yes or no; the exposure coded 0 and "
                 "1 (against= is 0).",
                 "1000 quasi-Bayesian simulations, as R mediation::mediate(sims = 1000), with_seed=1; effects averaged "
                 "over the two exposure levels."),
        also="simplydata also prints the direct and total effects and the share that goes through, and always the "
             "assumptions (nothing unmeasured affects both the mediator and the outcome).",
    ),
    # ------------------------------------------------------------------ I05: 2 x 2 crossover
    Entry(
        word="table.compare_averages_of", option="period=",
        data="drug_levels",
        ours="""
            table = sdata.table(sdata.get_example("drug_levels"))
            table.compare_averages_of("auc", for_each_group_in="formulation", matched_by="subject", period="period",
                                      same_within=[0.8, 1.25])
        """,
        code={"statsmodels": """
            import numpy as np
            import statsmodels.formula.api as smf
            df = sdata.get_example("drug_levels")
            first = df[df["period"] == 1].set_index("subject")["formulation"]
            df["sequence"] = df["subject"].map(first)                                          # (1)
            # compare_averages_of("auc", ..., matched_by="subject", period="period", same_within=[0.8, 1.25])
            m = smf.ols("np.log(auc) ~ C(sequence) + C(subject) + C(period) + C(formulation)", data=df).fit()   # (2)
            term = "C(formulation)[T.test]"
            low, high = m.conf_int(alpha=0.10).loc[term]                                       # (3)
            {"estimate": np.exp(m.params[term]), "90 % CI low": np.exp(low), "90 % CI high": np.exp(high),
             "within-subject CV": np.sqrt(np.exp(m.mse_resid) - 1)}
        """},
        compare="result", fields=("estimate", "90 % CI low", "90 % CI high", "within-subject CV"), tolerance=1e-9,
        choices=("the sequence is each subject's formulation in the first period.",
                 "the EMA (2010) model with all effects fixed, on the log scale.",
                 "the 90 % interval, the same as two one-sided tests at 5 % each; the ratio and its interval taken "
                 "back from logs."),
        also="simplydata also leaves out (and names) subjects without both periods, refuses designs that are not "
             "2 x 2, says whether the interval lies inside same_within=, and gives the within-subject CV.",
    ),
    # ------------------------------------------------------------------ X05: multiple imputation for other words
    Entry(
        word="table.find_correlation_between", option='empty_cells="multiple imputation"',
        data="school",
        ours="""
            table = sdata.table(sdata.get_example("school"))
            table.find_correlation_between("sleep", "marks", empty_cells="multiple imputation")
        """,
        code={
            "R": """
                # find_correlation_between("sleep", "marks", empty_cells="multiple imputation")
                colnames(X) <- c("v0", "v1")
                tables <- lapply(1:20, function(i) as.data.frame(X[((i - 1) * 180 + 1):(i * 180), ]))
                r <- miceadds::micombine.cor(tables)   # (1)
                list(r = r$r[1])
            """,
            "Python": """
                r
            """,
        },
        r_inputs=FILL_IN, r_packages=("miceadds", "mice"), compare="value", tolerance=1e-9,
        choices=("Fisher's z of each filled-in table pooled with Rubin's rules and taken back to r (van Buuren 2018, "
                 "section 5.2).",),
        python_note="statsmodels fills in the empty cells; no Python package pools correlations with Rubin's rules, "
                    "so the pooling comes from R miceadds.",
        also="simplydata also leaves out rows where every column is empty, gives the interval and the p-value, and a "
             "table for three or more columns.",
    ),
]
