"""Bayesian answers (phase S3d-3): one entry for each word that takes test_method="bayesian" (keyed by word and option). The
light route is R BayesFactor (ttestBF, correlationBF, contingencyTableBF, then posterior() after set.seed()); the heavy
route is R rstanarm (stan_glm, stan_glmer) with the posterior package's convergence measures. Practice tables: "clinic"
and "school" (made up).
"""

from . import Entry

CLINIC = """
    import pandas as pd
    df = pd.read_csv("clinic.csv")
"""
SEED = 'set.seed(1, kind = "Mersenne-Twister", normal.kind = "Inversion", sample.kind = "Rejection")'
QUANTILES = 'c("2.5%", "50%", "97.5%")'
BF_NOTE = ("No Python package gives the JZS Bayes factors with their posterior (pingouin's bayesfactor_ttest gives the "
           "Bayes factor only), so the numbers come from R BayesFactor (Morey & Rouder).")
STAN_NOTE = ("PyMC and Bambi fit the same kind of model in Python, but they compile each model and are not simplydata "
             "dependencies, so the numbers come from R rstanarm, whose models are compiled when it is installed.")
SEED_CHOICE = ("with_seed=1: R's set.seed() before BayesFactor::posterior() (10,000 draws), so the interval is the same "
               "on every run; the Bayes factor itself is worked out without random draws.")
STAN_CHOICES = ("rstanarm's defaults written out: 4 chains of 2000 iterations (1000 warm-up), its weakly informative "
                "priors scaled to the data (printed from prior_summary()), seed = with_seed and cores = 1 (no worker "
                "processes).",
                "the posterior median and the central 95 % interval (posterior_interval()); R-hat, bulk and tail "
                "effective sample sizes from the posterior package (rank-normalised, Vehtari et al. 2021), not the "
                "older Rhat and n_eff of rstanarm's summary().")


def _bf(word, option, ours, r_code, r_inputs, fields, choices, also):
    return Entry(word=word, option=option, data="clinic", ours=ours,
                 code={"R": r_code, "Python": "{" + ", ".join(f'"{k}": {v}' for k, v in fields.items()) + "}\n"},
                 r_inputs=r_inputs, r_packages=("BayesFactor",), compare="result", fields=tuple(fields),
                 tolerance=1e-9, choices=choices, python_note=BF_NOTE, also=also)


ENTRIES = [
    # ------------------------------------------------------------------ Z01-Z02: Bayes factors and posteriors
    _bf("table.compare_averages_of", "test_method=\"bayesian\"",
        """
            table = sdata.get_example("clinic")
            table.compare_averages_of("crp", for_each_group_in="ward", test_method="bayesian")
        """,
        f"""
            # compare_averages_of("crp", for_each_group_in="ward", test_method="bayesian")
            b <- BayesFactor::ttestBF(x = a, y = b, rscale = "medium")       # (1)
            {SEED}
            p <- BayesFactor::posterior(b, iterations = 10000, progress = FALSE)                 # (2)
            q <- summary(p)$quantiles["beta (x - y)", {QUANTILES}]
            list(bf = BayesFactor::extractBF(b)$bf, low = q[[1]], mid = q[[2]], high = q[[3]])
        """,
        CLINIC + """    a = df.loc[df["ward"] == "ward A", "crp"].to_numpy(dtype=float)
    b = df.loc[df["ward"] == "ward B", "crp"].to_numpy(dtype=float)
""",
        {"Bayes factor": "bf", "difference": "mid", "difference 95 % credible interval low": "low",
         "difference 95 % credible interval high": "high"},
        ("the JZS prior of medium width (a Cauchy prior on the effect size, r = 0.707; Rouder et al. 2009), "
         "BayesFactor's default; prior_width= changes it.", SEED_CHOICE),
        "simplydata also says the Bayes factor in words both ways round, prints the prior and what a credible "
        "interval means, gives the effect size's interval, refuses three or more groups, and prints no p-value."),
    _bf("table.compare_before_and_after", "test_method=\"bayesian\"",
        """
            table = sdata.get_example("clinic")
            table.compare_before_and_after("pain_week_0", "pain_week_4", test_method="bayesian")
        """,
        f"""
            # compare_before_and_after("pain_week_0", "pain_week_4", test_method="bayesian")
            b <- BayesFactor::ttestBF(x = after, y = before, paired = TRUE, rscale = "medium")   # (1)
            {SEED}
            p <- BayesFactor::posterior(b, iterations = 10000, progress = FALSE)   # (2)
            q <- summary(p)$quantiles["mu", {QUANTILES}]
            list(bf = BayesFactor::extractBF(b)$bf, low = q[[1]], mid = q[[2]], high = q[[3]])
        """,
        CLINIC + """    before = df["pain_week_0"].to_numpy(dtype=float)
    after = df["pain_week_4"].to_numpy(dtype=float)
""",
        {"Bayes factor": "bf", "average change": "mid", "average change 95 % credible interval low": "low",
         "average change 95 % credible interval high": "high"},
        ("the change is after minus before (x = after, y = before), with the JZS prior of medium width.",
         SEED_CHOICE),
        "simplydata also skips rows with an empty cell (with a note), refuses columns that are not numbers, and "
        "prints the prior and no p-value."),
    _bf("table.compare_average_to", "test_method=\"bayesian\"",
        """
            table = sdata.get_example("clinic")
            table.compare_average_to("crp", 5, test_method="bayesian")
        """,
        f"""
            # compare_average_to("crp", 5, test_method="bayesian")
            b <- BayesFactor::ttestBF(x = x - 5, rscale = "medium")           # (1)
            {SEED}
            p <- BayesFactor::posterior(b, iterations = 10000, progress = FALSE)   # (2)
            q <- summary(p)$quantiles["mu", {QUANTILES}]
            list(bf = BayesFactor::extractBF(b)$bf, low = q[[1]], mid = q[[2]], high = q[[3]])
        """,
        CLINIC + """    x = df["crp"].to_numpy(dtype=float)
""",
        {"Bayes factor": "bf", "difference": "mid", "difference 95 % credible interval low": "low",
         "difference 95 % credible interval high": "high"},
        ("x - 5 rather than mu = 5: BayesFactor's posterior() leaves mu = out (its draws are those of mu = 0), while "
         "its Bayes factor takes mu away inside; so the Bayes factor is the same and the posterior is that of the "
         "average minus 5.", SEED_CHOICE),
        "simplydata also prints the prior and what a credible interval means, and no p-value."),
    _bf("table.find_correlation_between", "test_method=\"bayesian\"",
        """
            table = sdata.get_example("clinic")
            table.find_correlation_between("crp", "procalcitonin", test_method="bayesian")
        """,
        f"""
            # find_correlation_between("crp", "procalcitonin", test_method="bayesian")
            b <- BayesFactor::correlationBF(y = a, x = b, rscale = "medium")  # (1)
            {SEED}
            p <- BayesFactor::posterior(b, iterations = 10000, progress = FALSE)   # (2)
            q <- summary(p)$quantiles["rho", {QUANTILES}]
            list(bf = BayesFactor::extractBF(b)$bf, low = q[[1]], mid = q[[2]], high = q[[3]])
        """,
        CLINIC + """    a = df["crp"].to_numpy(dtype=float)
    b = df["procalcitonin"].to_numpy(dtype=float)
""",
        {"Bayes factor": "bf", "r": "mid", "r 95 % credible interval low": "low", "r 95 % credible interval high": "high"},
        ("the stretched beta prior of medium width 1/3 (BayesFactor's default; JASP's default of 1 gives other Bayes "
         "factors).", SEED_CHOICE),
        "simplydata also refuses more than two columns and every option of the usual correlation, and prints no "
        "p-value."),
    _bf("table.compare_counts_of", "test_method=\"bayesian\"",
        """
            table = sdata.get_example("clinic")
            table.compare_counts_of("infected", for_each_group_in="ward", test_method="bayesian")
        """,
        f"""
            # compare_counts_of("infected", for_each_group_in="ward", test_method="bayesian")
            tab <- table(g, v)
            b <- BayesFactor::contingencyTableBF(tab, sampleType = "indepMulti",
                                                 fixedMargin = "rows")         # (1)
            {SEED}
            p <- BayesFactor::posterior(b, iterations = 10000, progress = FALSE)   # (2)
            q <- summary(p)$quantiles["omega[1,2]", {QUANTILES}]
            list(bf = BayesFactor::extractBF(b)$bf, low = q[[1]], mid = q[[2]], high = q[[3]])
        """,
        CLINIC + """    g = df["ward"].to_numpy(dtype=str)
    v = df["infected"].to_numpy(dtype=str)
""",
        {"Bayes factor": "bf", "share yes in ward A": "mid", "share yes in ward A 95 % credible interval low": "low",
         "share yes in ward A 95 % credible interval high": "high"},
        ("independent multinomial sampling with each group's total fixed: the groups are the rows (fixedMargin = "
         "\"rows\"), with the Gunel-Dickey prior of concentration 1 (BayesFactor's default).", SEED_CHOICE),
        "simplydata also gives every group's share of every value with its interval, and prints no p-value."),
    # ------------------------------------------------------------------ Z03-Z06: Bayesian models
    Entry(
        word="table.explain", option="test_method=\"bayesian\"",
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.explain("marks", using=["hours", "breakfast"], test_method="bayesian")
        """,
        code={
            "R": """
                # explain("marks", using=["hours", "breakfast"], test_method="bayesian")
                d <- data.frame(marks, hours, breakfast = factor(breakfast))
                m <- rstanarm::stan_glm(marks ~ hours + breakfast, data = d, chains = 4,
                                        iter = 2000, seed = 1, refresh = 0, cores = 1)   # (1)
                ci <- rstanarm::posterior_interval(m, prob = 0.95)                        # (2)
                s <- posterior::summarise_draws(posterior::as_draws_array(as.array(m)),
                                                "rhat", "ess_bulk", "ess_tail")
                list(est = unname(coef(m)[2]), low = ci[2, 1], high = ci[2, 2], rhat = s$rhat[2],
                     bulk = s$ess_bulk[2], tail = s$ess_tail[2])
            """,
            "Python": """
                {"effect": est, "95 % credible interval low": low, "95 % credible interval high": high,
                 "R-hat": rhat, "effective draws (middle)": bulk, "effective draws (tails)": tail}
            """,
        },
        r_inputs="""
            import pandas as pd
            df = pd.read_csv("school.csv")
            marks = df["marks"].to_numpy(dtype=float)
            hours = df["hours"].to_numpy(dtype=float)
            breakfast = df["breakfast"].to_numpy(dtype=str)
        """,
        r_packages=("rstanarm", "rstan", "posterior"), compare="result", row="hours",
        fields=("effect", "95 % credible interval low", "95 % credible interval high", "R-hat",
                "effective draws (middle)", "effective draws (tails)"), tolerance=1e-9,
        choices=STAN_CHOICES, python_note=STAN_NOTE,
        also="simplydata also prints the prior, warns before any estimate when R-hat is above 1.01, there are fewer "
             "than 400 effective draws or any divergent transition (with what to do), gives odds or rate ratios for "
             "yes/no and counts, and prints no p-value.",
    ),
    Entry(
        word="table.explain", option="test_method=\"bayesian\", grouped_by=",
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.explain("marks", using=["hours"], grouped_by="school", test_method="bayesian")
        """,
        code={
            "R": """
                # explain("marks", using=["hours"], grouped_by="school", test_method="bayesian")
                d <- data.frame(marks, hours, school = factor(school))
                m <- rstanarm::stan_glmer(marks ~ hours + (1 | school), data = d, chains = 4,
                                          iter = 2000, seed = 1, refresh = 0, cores = 1)  # (1)
                ci <- rstanarm::posterior_interval(m, prob = 0.95, pars = "hours")
                list(est = unname(rstanarm::fixef(m)[2]), low = ci[1, 1], high = ci[1, 2])
            """,
            "Python": """
                {"effect": est, "95 % credible interval low": low, "95 % credible interval high": high}
            """,
        },
        r_inputs="""
            import pandas as pd
            df = pd.read_csv("school.csv")
            marks = df["marks"].to_numpy(dtype=float)
            hours = df["hours"].to_numpy(dtype=float)
            school = df["school"].to_numpy(dtype=str)
        """,
        r_packages=("rstanarm", "rstan", "posterior"), compare="result", row="hours",
        fields=("effect", "95 % credible interval low", "95 % credible interval high"), tolerance=1e-9,
        choices=("a mixed model with its own starting level for each school, (1 | school), rstanarm's decov prior "
                 "for the group spread; otherwise as explain(test_method=\"bayesian\").",),
        python_note=STAN_NOTE,
        also="simplydata also prints the spread between the groups (rstanarm VarCorr()) and checks every group "
             "parameter for convergence, not only the effects.",
    ),
    Entry(
        word="table.check_model_of", option="test_method=\"bayesian\"",
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.check_model_of("marks", using=["hours", "breakfast"], test_method="bayesian")._check_numbers["observed"]
        """,
        code={
            "R": """
                # check_model_of("marks", using=["hours", "breakfast"], test_method="bayesian")
                d <- data.frame(marks, hours, breakfast = factor(breakfast))
                m <- rstanarm::stan_glm(marks ~ hours + breakfast, data = d, chains = 4,
                                        iter = 2000, seed = 1, refresh = 0, cores = 1)
                yrep <- rstanarm::posterior_predict(m, draws = 50, seed = 1)       # (1)
                r <- range(c(marks, yrep))
                list(observed = stats::density(marks, from = r[1], to = r[2], n = 256)$y)   # (2)
            """,
            "Python": """
                observed
            """,
        },
        r_inputs="""
            import pandas as pd
            df = pd.read_csv("school.csv")
            marks = df["marks"].to_numpy(dtype=float)
            hours = df["hours"].to_numpy(dtype=float)
            breakfast = df["breakfast"].to_numpy(dtype=str)
        """,
        r_packages=("rstanarm", "rstan", "posterior"), compare="value", tolerance=1e-9,
        choices=("50 sets of made-up values from the fitted model (posterior_predict(draws = 50)), as bayesplot's "
                 "pp_check() shows by default.",
                 "each set and the data as a density on one grid from the smallest to the largest value, R "
                 "stats::density() with its bw.nrd0 bandwidth, the rule bayesplot::ppc_dens_overlay uses through "
                 "ggplot2; the lines are drawn with matplotlib."),
        python_note=STAN_NOTE,
        also="simplydata also draws bars with the median and 90 % interval of the made-up counts for yes/no and "
             "counts (as bayesplot::ppc_bars), prints R-hat and effective draws, and with show=\"prior check\" draws "
             "the sets made up from the prior alone (prior_PD = TRUE).",
    ),
]
