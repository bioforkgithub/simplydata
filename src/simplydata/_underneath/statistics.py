"""Statistics words: the call in SciPy or statsmodels that gives the main numbers.

For words that do a long job (choose the test, check the spreads, effect size, a sentence), the code
shows the core of it: the call that gives the numbers in simplydata's result table.
"""

from . import Entry

SENTENCE = "simplydata also writes the result as a sentence and names the test."

ENTRIES = [
    Entry(
        word="table.compare_averages_of",
        data="trial",
        ours="""
            table = sdata.get_example("trial")
            table.compare_averages_of("days", for_each_group_in="treatment")
        """,
        code={"SciPy": """
            from scipy import stats
            import pandas as pd
            df = pd.read_csv("trial.csv")
            # the core of compare_averages_of("days", for_each_group_in="treatment")
            a, b = [rows["days"] for _, rows in df.groupby("treatment", sort=False)]
            res = stats.ttest_ind(a, b, equal_var=False)       # (1)
            {"statistic": res.statistic, "degrees of freedom": res.df,
             "p-value": res.pvalue, "difference": a.mean() - b.mean()}
        """},
        compare="result",
        fields=("statistic", "degrees of freedom", "p-value", "difference"),
        tolerance=1e-9,
        choices=("Welch's t-test, which does not assume both groups have the same spread; SciPy's own default "
                 "(equal_var=True) is Student's t-test, which does.",),
        also="With three or more groups simplydata uses Welch's one-way ANOVA (statsmodels anova_oneway, whose "
             "own default is Welch too). simplydata also chooses the test from the number of groups, adds an "
             "effect size (R effectsize, when R is there) and the averages of the groups. " + SENTENCE,
    ),
    Entry(
        word="table.fit_line",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_rows_where("subject", is_equal_to="Maths")
            table.fit_line(x="hours", y="marks")
        """,
        code={"SciPy": """
            from scipy import stats
            import pandas as pd
            df = pd.read_csv("marks.csv")
            df = df[df["subject"] == "Maths"].reset_index(drop=True)   # one row per child
            # fit_line(x="hours", y="marks")
            fit = stats.linregress(df["hours"], df["marks"])
            t = stats.t.ppf(0.975, len(df) - 2)                 # (1)
            {"slope": fit.slope, "intercept": fit.intercept,
             "slope standard error": fit.stderr, "intercept standard error": fit.intercept_stderr,
             "slope 95 % CI low": fit.slope - t * fit.stderr,
             "R squared": fit.rvalue ** 2, "p-value": fit.pvalue}
        """},
        compare="result",
        fields=("slope", "intercept", "slope standard error", "intercept standard error", "slope 95 % CI low",
                "R squared", "p-value"),
        tolerance=1e-9,
        choices=("the 95 % interval of the slope uses the t distribution with n - 2 degrees of freedom, as R's "
                 "confint(lm(...)).",),
        also="Rows with an empty cell in x or y are left out first. " + SENTENCE,
    ),
    Entry(
        word="dist.find_chance_that_value",
        ours="""
            distribution = sdata.distribution("normal", average=50, standard_deviation=10)
            distribution.find_chance_that_value(is_above=80)
        """,
        code={"SciPy": """
            from scipy import stats
            dist = stats.norm(loc=50, scale=10)
            # find_chance_that_value(is_above=80)
            dist.sf(80)                     # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the chance above a value is the survival function sf(), not 1 - cdf(): it stays accurate far "
                 "out in the tail.",),
        also="simplydata also says the chance in a sentence, with the same call in R "
             "(pnorm(80, mean = 50, sd = 10, lower.tail = FALSE)).",
    ),
    Entry(
        word="dist.find_percentile",
        ours="""
            distribution = sdata.distribution("normal", average=50, standard_deviation=10)
            distribution.find_percentile(95)
        """,
        code={"SciPy": """
            from scipy import stats
            dist = stats.norm(loc=50, scale=10)
            # find_percentile(percent=95)
            dist.isf(1 - 0.95)              # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the percent is turned into a share (95 % is 0.95). Above the middle simplydata asks for the value "
                 "with 5 % above it (isf), which stays accurate far out in the upper tail; below the middle it uses "
                 "ppf(). For counts it is the smallest count with at least that share at or below it, as R "
                 "qbinom().",),
        also="simplydata also says the value in a sentence, with the same call in R (qnorm(0.95, mean = 50, "
             "sd = 10)). A list of percents gives one value for each.",
    ),
    Entry(
        word="table.compare_spreads_of",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_rows_where("subject", is_equal_to="Maths")
            table.compare_spreads_of("marks", for_each_group_in="class")
        """,
        code={"SciPy": """
            from scipy import stats
            import pandas as pd
            df = pd.read_csv("marks.csv")
            df = df[df["subject"] == "Maths"].reset_index(drop=True)   # one row per child
            # compare_spreads_of("marks", for_each_group_in="class")
            groups = [rows["marks"].dropna() for _, rows in df.groupby("class")]
            res = stats.levene(*groups, center="median")                  # (1)
            {"statistic": res.statistic, "p-value": res.pvalue,
             "degrees of freedom 1": len(groups) - 1,
             "degrees of freedom 2": sum(len(g) for g in groups) - len(groups)}
        """},
        compare="result",
        fields=("statistic", "p-value", "degrees of freedom 1", "degrees of freedom 2"),
        tolerance=1e-10,
        choices=("Levene's test centred on each group's median (the Brown-Forsythe test), the default of SciPy "
                 "and of R car::leveneTest(); it copes well with values that are not bell-shaped.",),
        also="test_method= takes \"bartlett\", \"fligner\" and, for two groups, \"ansari\", \"mood\" and \"f\" "
             "(R var.test()). simplydata also gives each group's standard deviation. " + SENTENCE,
    ),
    Entry(
        word="table.compare_percent_to",
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.compare_percent_to("passed", value="yes", percent=50)
        """,
        code={"SciPy": """
            from scipy import stats
            from statsmodels.stats.proportion import proportion_effectsize
            import pandas as pd
            df = pd.read_csv("school.csv")
            # compare_percent_to("passed", value="yes", percent=50)
            passed = df["passed"].dropna()
            hits, n = int((passed == "yes").sum()), len(passed)
            res = stats.binomtest(hits, n, 0.5)                               # (1)
            ci = res.proportion_ci(confidence_level=0.95, method="exact")     # (2)
            {"statistic": hits, "p-value": res.pvalue, "percent 95 % CI low": ci.low * 100,
             "percent 95 % CI high": ci.high * 100,
             "effect size": proportion_effectsize(hits / n, 0.5)}             # (3)
        """},
        compare="result",
        fields=("statistic", "p-value", "percent 95 % CI low", "percent 95 % CI high", "effect size"),
        tolerance=1e-10,
        choices=("the exact binomial test, as R binom.test(); empty cells are left out first.",
                 "the exact (Clopper-Pearson) 95 % interval of the percent; interval_by= takes \"wilson\" or "
                 "\"agresti-coull\".",
                 "the effect size is Cohen's h, the difference between the two shares on the arcsine scale.",),
        also="percent= is above 0 and below 100 (SciPy takes shares from 0 to 1). sides=1 with higher=\"percent\" "
             "or lower=\"percent\" tests one direction. " + SENTENCE,
    ),
    Entry(
        word="table.add_principal_components",
        data="meadow",
        ours="""
            table = sdata.get_example("meadow")
            table.add_principal_components(how_many=2)
        """,
        code={"statsmodels": """
            import numpy as np
            import pandas as pd
            from statsmodels.multivariate.pca import PCA
            df = pd.read_csv("meadow.csv")
            # add_principal_components(how_many=2)
            x = df.select_dtypes("number").dropna()                          # (1)
            z = (x - x.mean()) / x.std()                                     # (2)
            pca = PCA(z, ncomp=2, standardize=False, demean=False, normalize=False, method="svd")
            w = np.asarray(pca.loadings)
            w = w * np.sign(w[np.abs(w).argmax(axis=0), [0, 1]])             # (3)
            df.join(pd.DataFrame(z.to_numpy() @ w, index=x.index, columns=["PC1", "PC2"]))
        """},
        compare="table",
        tolerance=1e-9,
        choices=("only rows with a number in every column are used; the other rows get empty PC cells.",
                 "every number column is put on the same scale first (mean 0, standard deviation with n - 1), "
                 "as R prcomp(scale. = TRUE); same_scale=False only centres them (mean 0), as prcomp(scale. = FALSE).",
                 "the sign of a component is arbitrary and differs between computers, so each one is turned so its "
                 "biggest weight is positive: the same scores on every computer.",),
        also="simplydata also prints how much of the spread each component holds and the columns it weighs most "
             "on.",
    ),
    Entry(
        word="table.add_predicted_column",
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.add_predicted_column("marks", using=["hours", "sleep"])
        """,
        code={"statsmodels": """
            import statsmodels.formula.api as smf
            import pandas as pd
            df = pd.read_csv("school.csv")
            # add_predicted_column("marks", using=["hours", "sleep"])
            fit = smf.ols("marks ~ hours + sleep", data=df).fit()            # (1)
            df.assign(**{"predicted marks": fit.fittedvalues})               # (2)
        """},
        compare="table",
        tolerance=1e-9,
        choices=("the same model as explain(): least squares for numbers (R fitted(lm(...))); outcome= chooses "
                 "the others (logistic for yes or no; Poisson, quasi-Poisson or negative binomial for counts; Gamma for "
                 "positive numbers).",
                 "rows with an empty cell in a column the model uses are left out of the fit and stay empty "
                 "(assign lines the fitted values up by row).",),
        also="interval=95 adds the ends of the 95 % confidence interval (for_new_rows=True: the prediction "
             "interval), from statsmodels get_prediction(). simplydata also says which model it fitted on how many "
             "rows.",
    ),
]

# ---------------------------------------------------------------- U-batch 2: trends, peaks, NMDS, formulas, matched columns
HARBOUR = """
    import pandas as pd
    visitors_table = pd.read_csv("visitors.csv", parse_dates=["month"])
    harbour = visitors_table[visitors_table["museum"] == "Harbour Museum"].sort_values("month")
    visitors = harbour["visitors"].to_numpy(dtype=float)
"""

ENTRIES += [
    Entry(
        word="table.find_trend_of",
        data="visitors",
        ours="""
            table = sdata.get_example("visitors")
            table.keep_rows_where("museum", is_equal_to="Harbour Museum")
            table.find_trend_of("visitors", sorted_by="month")
        """,
        code={
            "R": """
                # find_trend_of("visitors", sorted_by="month"), for one museum
                # visitors: the monthly counts of the Harbour Museum, in time order
                m <- trend::mk.test(visitors)                                   # (1)
                list(z = unname(m$statistic), p = m$p.value,
                     S = unname(m$estimates["S"]), tau = unname(m$estimates["tau"]))
            """,
            "SciPy": """
                import pandas as pd
                from scipy import stats
                df = pd.read_csv("visitors.csv", parse_dates=["month"])
                harbour = df[df["museum"] == "Harbour Museum"].sort_values("month")
                sen = stats.theilslopes(harbour["visitors"], alpha=0.95)        # (2)
                {"slope": sen.slope, "95 % CI low": sen.low_slope, "95 % CI high": sen.high_slope,
                 "slope per year": 12 * sen.slope,                               # (3)
                 "z": z, "p-value": p, "S": S, "Kendall's tau": tau}
            """,
        },
        r_inputs=HARBOUR,
        r_packages=("trend",),
        compare="result",
        fields=("slope", "95 % CI low", "95 % CI high", "slope per year", "z", "p-value", "S", "Kendall's tau"),
        tolerance=1e-9,
        choices=("the Mann-Kendall test with its continuity correction, run in R itself (trend::mk.test).",
                 "Sen's slope is the median of the slopes between every pair of readings, with its 95 % interval "
                 "(SciPy theilslopes gives the same numbers as R trend::sens.slope).",
                 "readings one calendar month apart give the slope per month, and 12 times it per year.",),
        python_note="SciPy kendalltau gives a similar test, but without R's continuity correction its p-value "
                    "differs, so the test comes from R.",
        also="simplydata also checks the readings left after Sen's line for lag-1 autocorrelation (statsmodels acf "
             "and the Ljung-Box test) and warns when the p-value is then too small. repeats_every=12 runs the "
             "seasonal test (trend::smk.test, sea.sens.slope). " + SENTENCE,
    ),
    Entry(
        word="table.find_each_peak_that",
        data="sensor",
        ours="""
            table = sdata.get_example("sensor")
            table.find_each_peak_that("signal", sorted_by="time", is_at_least=1, apart=0.05)
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import signal
            df = pd.read_csv("sensor.csv").sort_values("time")
            # find_each_peak_that("signal", sorted_by="time", is_at_least=1, apart=0.05)
            y, step = df["signal"].to_numpy(), 0.005                 # readings 0.005 apart
            peaks, _ = signal.find_peaks(y, height=1, distance=round(0.05 / step, 9))  # (1)
            prom, left, right = signal.peak_prominences(y, peaks)
            width = signal.peak_widths(y, peaks, rel_height=0.5,
                                       prominence_data=(prom, left, right))[0]  # (2)
            pd.DataFrame({"position": peaks + 1, "time": df["time"].to_numpy()[peaks],
                          "value": y[peaks], "stands out by": prom, "width": width * step,
                          "left base": left + 1, "right base": right + 1})     # (3)
        """},
        compare="table",
        tolerance=1e-9,
        choices=("apart= is in units of sorted_by, so it becomes a number of readings (0.05 / 0.005 = 10) for "
                 "SciPy's distance=. simplydata rounds that number to 9 decimals first: 0.05 / 0.005 is "
                 "10.000000000000002 in floating point, and SciPy rounds distance= up, to 11 readings, which can "
                 "lose a peak.",
                 "each peak's width is measured halfway down its prominence (as R pracma::findpeaks), and written in "
                 "units of sorted_by.",
                 "positions and bases count from 1, as the rows do.",),
        also="Empty cells are never peaks and split their neighbours. stands_out_by= and wide_at_least= are SciPy's "
             "prominence= and width=. simplydata also says how many peaks it found and which is highest.",
    ),
    Entry(
        word="table.add_nmds",
        data="meadow",
        ours="""
            table = sdata.get_example("meadow")
            table.add_nmds(measure="bray-curtis")
        """,
        code={
            "R": """
                # add_nmds(measure="bray-curtis")
                # x: the plant counts of sdata.get_example("meadow"), one row per plot
                set.seed(1)                                                     # (1)
                d <- vegan::vegdist(x, method = "bray")
                fit <- vegan::metaMDS(d, k = 2, try = 20, trymax = 100,         # (2)
                                      autotransform = FALSE, trace = 0)         # (3)
                list(points = unclass(fit$points))
            """,
            "pandas": """
                import pandas as pd
                import numpy as np
                df = pd.read_csv("meadow.csv")
                p = np.asarray(points).reshape(len(df), 2, order="F")
                df.assign(NMDS1=p[:, 0], NMDS2=p[:, 1])
            """,
        },
        r_inputs="""
            import pandas as pd
            meadow = pd.read_csv("meadow.csv")
            x = meadow.select_dtypes("number").to_numpy(dtype=float)
        """,
        r_packages=("vegan",),
        compare="table",
        tolerance=1e-9,
        choices=("with_seed=1 is R's own set.seed(1), so the random starts are the same every time.",
                 "at least 20 random starts, and more (up to 100) until the best map has been found twice.",
                 "the counts are used as they are (autotransform = FALSE); vegan's own default may take square "
                 "roots first, which changes the map without saying so.",),
        python_note="scikit-learn MDS(metric=False) is similar but finds another map with another stress, and "
                    "simplydata leaves scikit-learn out, so the map comes from R vegan.",
        also="vegan also centres the map, turns it to its main axes and scales it (metaMDS's own steps after the "
             "search). simplydata prints the stress with Clarke's rule of thumb and says when the best map was found "
             "only once. Rows with an empty cell get empty NMDS cells.",
    ),
    Entry(
        word="table.fit_formula",
        data="growth",
        ours="""
            table = sdata.get_example("growth")
            table.keep_rows_where("country", is_equal_to="Applia")
            table.fit_formula("population = a * exp(b * (year - 2000))")
        """,
        code={"SciPy": """
            import pandas as pd
            import numpy as np
            from scipy import optimize, stats
            df = pd.read_csv("growth.csv")
            rows = df[df["country"] == "Applia"]
            # fit_formula("population = a * exp(b * (year - 2000))")
            f = lambda year, a, b: a * np.exp(b * (year - 2000))
            (a, b), cov = optimize.curve_fit(f, rows["year"], rows["population"], p0=[1, 1],  # (1)
                                             method="lm", maxfev=20000, xtol=1e-12, ftol=1e-12)  # (2)
            se, df_left = np.sqrt(np.diag(cov)), len(rows) - 2
            t = stats.t.ppf(0.975, df_left)                                      # (3)
            {"a": a, "b": b, "standard error of a": se[0], "standard error of b": se[1],
             "95 % CI low of b": b - t * se[1], "95 % CI high of b": b + t * se[1],
             "residual standard error": np.sqrt(np.sum((rows["population"] - f(rows["year"], a, b)) ** 2) / df_left)}
        """},
        compare="result",
        fields=("a", "b", "standard error of a", "standard error of b", "95 % CI low of b", "95 % CI high of b",
                "residual standard error"),
        tolerance=1e-7,
        choices=("names that are not columns (a, b) are the values to find, and each starts at 1 unless start= "
                 "says otherwise.",
                 "Levenberg-Marquardt with tight stopping rules, as R nls(); between= limits switch to SciPy's trust "
                 "region method (method=\"trf\").",
                 "each interval is the value plus and minus t (n - 2 degrees of freedom here) standard errors; R's "
                 "confint() on nls profiles the likelihood and can differ a little.",),
        also="The numbers agree to 7 digits: the search stops at a tolerance, not at an exact answer. simplydata also "
             "gives t, p-values, R squared, AIC and whether the fit converged, and says plainly when the data do not "
             "pin a value down. " + SENTENCE,
    ),
    Entry(
        word="table.compare_matched_columns",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_columns("name", "subject", "marks")
            table.spread_into_columns(names_from="subject", values_from="marks")
            table.compare_matched_columns("Maths", "Science", "English")
        """,
        code={
            "R": """
                # compare_matched_columns("Maths", "Science", "English")
                # y: one row per student, one column per subject, in that order
                set.seed(1)                                                     # (1)
                es <- as.data.frame(effectsize::kendalls_w(y, ci = 0.95,
                                                           alternative = "two.sided"))  # (2)
                list(w = es$Kendalls_W, low = es$CI_low, high = es$CI_high)
            """,
            "SciPy": """
                import pandas as pd
                from scipy import stats
                df = pd.read_csv("marks.csv")
                wide = df.pivot(index="name", columns="subject", values="marks")
                res = stats.friedmanchisquare(wide["Maths"], wide["Science"], wide["English"])  # (3)
                {"statistic": res.statistic, "degrees of freedom": 2, "p-value": res.pvalue,
                 "effect size": w, "effect size 95 % CI low": low, "effect size 95 % CI high": high}
            """,
        },
        r_inputs="""
            import pandas as pd
            marks = pd.read_csv("marks.csv")
            wide = marks.pivot(index="name", columns="subject", values="marks").loc[marks["name"].unique()]
            y = wide[["Maths", "Science", "English"]].dropna().to_numpy(dtype=float)
        """,
        r_packages=("effectsize",),
        compare="result",
        fields=("statistic", "degrees of freedom", "p-value", "effect size", "effect size 95 % CI low",
                "effect size 95 % CI high"),
        tolerance=1e-9,
        choices=("the bootstrap interval of Kendall's W uses R's own random numbers after set.seed(1), so it is the "
                 "same every time.",
                 "Kendall's W: how alike the rows rank the columns, from 0 (no common order) to 1 (every row the "
                 "same), with a two-sided 95 % interval.",
                 "the Friedman test, which compares the ranks within each row, so it needs no bell shape (as R "
                 "friedman.test()); rows with an empty cell are skipped first.",),
        python_note="Python has no Kendall's W with a bootstrap interval, so the effect size comes from R effectsize; "
                    "the test itself is SciPy's.",
        also="Yes/no columns get Cochran's Q test (statsmodels cochrans_q); test_method=\"quade\" (R quade.test()) and "
             "\"page\" (SciPy page_trend_test) are the other tests. simplydata also gives the median of each "
             "column. " + SENTENCE,
    ),
]

# ---------------------------------------------------------------- U3 batch 6: statistics and distribution words
CLINIC_TRUTH = """
    import pandas as pd
    import numpy as np
    df = pd.read_csv("clinic.csv")
    truth = (df["infected"] == "yes").to_numpy(dtype=float)
    crp = df["crp"].to_numpy(dtype=float)
    pct = df["procalcitonin"].to_numpy(dtype=float)
"""
DEVICES = """
    import pandas as pd
    df = pd.read_csv("clinic.csv")
    a = df["device_a"].to_numpy(dtype=float)
    b = df["device_b"].to_numpy(dtype=float)
"""
NO_DATA = """
    import numpy as np
    unused = np.zeros(1)
"""

ENTRIES += [
    Entry(
        word="table.compare_counts_to",
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.compare_counts_to("breakfast", expected={"yes": 0.6, "no": 0.4})
        """,
        code={"SciPy": """
            import pandas as pd
            import numpy as np
            from scipy import stats
            from statsmodels.stats.gof import chisquare_effectsize
            df = pd.read_csv("school.csv")
            # compare_counts_to("breakfast", expected={"yes": 0.6, "no": 0.4})
            observed = df["breakfast"].dropna().value_counts()[["yes", "no"]].to_numpy(dtype=float)
            shares = np.array([0.6, 0.4])
            res = stats.chisquare(observed, shares * observed.sum())                 # (1)
            w = chisquare_effectsize(shares, observed / observed.sum())               # (2)
            {"statistic": res.statistic, "degrees of freedom": len(observed) - 1, "p-value": res.pvalue,
             "effect size": w, "smallest expected count": (shares * observed.sum()).min()}
        """},
        compare="result",
        fields=("statistic", "degrees of freedom", "p-value", "effect size", "smallest expected count"),
        tolerance=1e-10,
        choices=("each share of expected= is matched to its value by name and turned into an expected count (share "
                 "times the rows with a value); SciPy's own default, without expected counts, is the same count for "
                 "every value.",
                 "the effect size is Cohen's w, the distance between the counted and the expected shares (statsmodels "
                 "chisquare_effectsize)."),
        also="Without expected= every value is expected equally often (R chisq.test(table(x))). Empty cells are left "
             "out first. simplydata also gives Cohen's w its 95 % interval (R effectsize, when R is there), the count "
             "and expected count of each value, and a note when an expected count is below 5. " + SENTENCE,
    ),
    Entry(
        word="table.compare_shapes_of",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.compare_shapes_of("marks", for_each_group_in="class")
        """,
        code={"SciPy": """
            import pandas as pd
            import numpy as np
            from scipy import stats
            df = pd.read_csv("marks.csv")
            # compare_shapes_of("marks", for_each_group_in="class"), three classes
            groups = [rows["marks"].dropna().to_numpy(dtype=float) for _, rows in df.groupby("class")]
            res = stats.anderson_ksamp(groups, midrank=True,                          # (1)
                                       method=stats.PermutationMethod(
                                           n_resamples=9999, rng=np.random.default_rng(1)))  # (2)
            {"statistic": res.statistic, "p-value": res.pvalue}
        """},
        compare="result",
        fields=("statistic", "p-value"),
        tolerance=1e-12,
        choices=("three or more groups get the Anderson-Darling k-sample test in its midrank version, which allows "
                 "for tied values, as R kSamples::ad.test() version 2.",
                 "the p-value comes from shuffling the group labels 9999 times with NumPy's generator seeded with 1 "
                 "(with_seed=1), so the same seed gives the same p-value; SciPy's own default reads it from a table "
                 "and caps it at 0.001 and 0.25."),
        also="Two groups get the two-sample Kolmogorov-Smirnov test (the next box). Empty cells are left out first. "
             "simplydata also gives each group's median and count. " + SENTENCE,
    ),
    Entry(
        word="table.compare_shapes_of",
        option="two groups",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_rows_where("class", is_one_of=["A", "B"])
            table.compare_shapes_of("marks", for_each_group_in="class")
        """,
        code={
            "R": """
                # compare_shapes_of("marks", for_each_group_in="class"), classes A and B
                # a, b: the marks of class A and of class B (some marks are tied)
                list(p = ks.test(a, b)$p.value)                                 # (1)
            """,
            "SciPy": """
                import pandas as pd
                from scipy import stats
                df = pd.read_csv("marks.csv")
                a, b = (df.loc[df["class"] == c, "marks"] for c in ("A", "B"))
                res = stats.ks_2samp(a, b, method="exact")                     # (2)
                {"statistic": res.statistic, "biggest gap at": res.statistic_location, "p-value": p}
            """,
        },
        r_inputs="""
            import pandas as pd
            df = pd.read_csv("marks.csv")
            a = df.loc[df["class"] == "A", "marks"].to_numpy(dtype=float)
            b = df.loc[df["class"] == "B", "marks"].to_numpy(dtype=float)
        """,
        r_packages=(),  # base R (stats) only
        compare="result",
        fields=("statistic", "biggest gap at", "p-value"),
        tolerance=1e-9,
        choices=("with tied values the exact p-value comes from R ks.test(), which allows for the ties; SciPy's exact "
                 "p-value assumes there are none.",
                 "the exact distribution while the two groups make fewer than 10000 pairs of values, as R ks.test(); "
                 "larger groups use the normal approximation."),
        python_note="SciPy ks_2samp gives the same D, but its exact p-value ignores tied values, so with ties the "
                    "p-value comes from R.",
        also="simplydata also gives the share of each group at or below the biggest gap, and the count of each "
             "group. " + SENTENCE,
    ),
    Entry(
        word="table.check_if_random_order",
        data="growth",
        ours="""
            table = sdata.get_example("growth")
            table.keep_rows_where("country", is_equal_to="Applia")
            table.check_if_random_order("forest")
        """,
        code={"statsmodels": """
            import pandas as pd
            import numpy as np
            from statsmodels.sandbox.stats.runs import Runs
            df = pd.read_csv("growth.csv")
            # check_if_random_order("forest"), Applia's 13 rows in table order
            x = df.loc[df["country"] == "Applia", "forest"].dropna().to_numpy(dtype=float)
            middle = np.median(x)
            above = x[x != middle] > middle                       # (1)
            runs = Runs(above.astype(int))
            z, p = runs.runs_test(correction=False)               # (2)
            {"statistic": z, "p-value": p, "runs": runs.n_runs, "median": middle,
             "values equal to the median (left out)": int((x == middle).sum())}
        """},
        compare="result",
        fields=("statistic", "p-value", "runs", "median", "values equal to the median (left out)"),
        tolerance=1e-12,
        choices=("each value is above or below the median; values equal to the median (one here) are left out, as R "
                 "randtests::runs.test() does.",
                 "the normal approximation without a continuity correction, the same numbers as R "
                 "randtests::runs.test(); statsmodels' own default adds one below 50 values, as here."),
        also="sorted_by= sorts the rows by another column first. Empty cells are left out. simplydata also counts the "
             "values above and below the median and says whether the values clump or flip. " + SENTENCE,
    ),
    Entry(
        word="table.compare_correlations",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_rows_where("class", is_one_of=["A", "B"])
            table.compare_correlations("hours", "marks", for_each_group_in="class")
        """,
        code={
            "R": """
                # compare_correlations("hours", "marks", for_each_group_in="class"), classes A and B
                a <- group == "A"
                b <- group == "B"
                r1 <- cor(hours[a], marks[a])
                r2 <- cor(hours[b], marks[b])
                t <- cocor::cocor.indep.groups(r1, r2, sum(a), sum(b),
                                               test = c("fisher1925", "zou2007"))   # (1)
                list(r1 = r1, r2 = r2, z = t@fisher1925$statistic, p = t@fisher1925$p.value,
                     ci = t@zou2007$conf.int)
            """,
            "Python": """
                {"r in A": r1, "r in B": r2, "statistic": z, "p-value": p,
                 "difference 95 % CI low": ci[0], "difference 95 % CI high": ci[1]}
            """,
        },
        r_inputs="""
            import pandas as pd
            df = pd.read_csv("marks.csv")
            df = df[df["class"].isin(["A", "B"])]
            hours = df["hours"].to_numpy(dtype=float)
            marks = df["marks"].to_numpy(dtype=float)
            group = df["class"].to_numpy(dtype=str)
        """,
        r_packages=("cocor",),
        compare="result",
        fields=("r in A", "r in B", "statistic", "p-value", "difference 95 % CI low", "difference 95 % CI high"),
        tolerance=1e-9,
        choices=("Fisher's z test for the p-value and Zou's interval for the difference; cocor's own default runs "
                 "every test it knows.",),
        python_note="SciPy and statsmodels have no test of two correlations, so the test comes from R cocor; the "
                    "correlations are SciPy's pearsonr (the same as R cor()).",
        also="Two pairs of columns that share one column, in the same rows, get Steiger's z test (R "
             "cocor::cocor.dep.groups.overlap()). Rows with an empty cell are left out. " + SENTENCE,
    ),
    Entry(
        word="sdata.compare_averages",
        ours="""
            sdata.compare_averages(averages=[63.2, 68.9], standard_deviations=[8.1, 9.0], counts=[20, 22])
        """,
        code={
            "R": """
                # compare_averages(averages=[63.2, 68.9], standard_deviations=[8.1, 9.0], counts=[20, 22])
                r <- BSDA::tsum.test(63.2, 8.1, 20, 68.9, 9.0, 22, var.equal = FALSE)   # (1)
                list(low = r$conf.int[1], high = r$conf.int[2], df = unname(r$parameter))
            """,
            "SciPy": """
                from scipy import stats
                res = stats.ttest_ind_from_stats(63.2, 8.1, 20, 68.9, 9.0, 22, equal_var=False)  # (1)
                {"statistic": res.statistic, "p-value": res.pvalue, "degrees of freedom": df,
                 "difference": 63.2 - 68.9, "difference 95 % CI low": low, "difference 95 % CI high": high}
            """,
        },
        r_inputs=NO_DATA,
        r_packages=("BSDA",),
        compare="result",
        fields=("statistic", "p-value", "degrees of freedom", "difference", "difference 95 % CI low",
                "difference 95 % CI high"),
        tolerance=1e-9,
        choices=("Welch's t-test, which does not assume both groups have the same spread; test_method=\"student\" "
                 "assumes they do (equal_var=True, var.equal = TRUE).",),
        python_note="SciPy gives the t-test from summary numbers but not the interval of the difference, which comes "
                    "from R BSDA::tsum.test().",
        also="Three or more groups get Welch's one-way ANOVA from the summary numbers (statsmodels anova_generic, "
             "the same numbers as R oneway.test() on the rows). " + SENTENCE,
    ),
    Entry(
        word="sdata.compare_counts",
        ours="""
            sdata.compare_counts([[20, 40], [30, 30]])
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import stats
            # compare_counts([[20, 40], [30, 30]])
            observed = np.array([[20, 40], [30, 30]])
            chi = stats.chi2_contingency(observed, correction=True)                   # (1)
            v = stats.contingency.association(observed, method="cramer", correction=False)  # (2)
            {"statistic": chi.statistic, "degrees of freedom": chi.dof, "p-value": chi.pvalue,
             "effect size": v, "smallest expected count": chi.expected_freq.min()}
        """},
        compare="result",
        fields=("statistic", "degrees of freedom", "p-value", "effect size", "smallest expected count"),
        tolerance=1e-10,
        choices=("the chi-square test of independence with Yates' continuity correction for a 2 x 2 table, as R "
                 "chisq.test().",
                 "Cramer's V from the counts without the continuity correction, so it does not shrink with Yates' "
                 "correction."),
        also="test_method= takes \"fisher\", \"g\", \"barnard\" and \"boschloo\", as table.compare_counts_of(). "
             "simplydata also gives Cramer's V its 95 % interval (R effectsize, when R is there) and a note when an "
             "expected count is below 5. " + SENTENCE,
    ),
    Entry(
        word="sdata.compare_risks",
        ours="""
            result = sdata.compare_risks(events=[20, 30], out_of=[60, 60], names=["new", "usual"], against="usual")
            result.keep_rows_where("measure", is_equal_to="risk difference")
            result
        """,
        code={"statsmodels": """
            from scipy import stats
            from statsmodels.stats.proportion import confint_proportions_2indep
            # compare_risks(events=[20, 30], out_of=[60, 60], names=["new", "usual"], against="usual")
            low, high = confint_proportions_2indep(20, 60, 30, 60, compare="diff",
                                                   method="newcomb")                  # (1)
            p = stats.chi2_contingency([[20, 40], [30, 30]], correction=True).pvalue   # (2)
            {"estimate": 20 / 60 - 30 / 60, "estimate 95 % CI low": low, "estimate 95 % CI high": high,
             "p-value": p}
        """},
        compare="result",
        fields=("estimate", "estimate 95 % CI low", "estimate 95 % CI high", "p-value"),
        tolerance=1e-10,
        choices=("the interval of the risk difference is Newcombe's score interval, as R DescTools::BinomDiffCI("
                 "method = \"score\"); statsmodels' own default is another interval (Agresti-Caffo).",
                 "the p-value is the chi-square test with Yates' correction, as R prop.test(); p_value_by=\"exact\" "
                 "gives Fisher's exact test."),
        also="The other rows hold each risk with its exact interval (statsmodels proportion_confint(method=\"beta\")), "
             "the number needed for one event fewer, and the risk ratio and odds ratio with Wald intervals on the log "
             "scale (statsmodels Table2x2, as R epitools). simplydata prints the same answer as table.compare_risks.",
    ),
    Entry(
        word="sdata.compare_rates",
        ours="""
            result = sdata.compare_rates(events=[30, 15], time=[1100, 1200], names=["ward B", "ward A"])
            result.keep_rows_where("measure", is_equal_to="rate ratio")
            result
        """,
        code={
            "R": """
                # compare_rates(events=[30, 15], time=[1100, 1200], names=["ward B", "ward A"])
                t <- poisson.test(c(15, 30), c(1200, 1100))                    # (1)
                list(low = t$conf.int[1], high = t$conf.int[2])
            """,
            "statsmodels": """
                from statsmodels.stats.rates import test_poisson_2indep
                test = test_poisson_2indep(15, 1200, 30, 1100, method="exact-cond")    # (2)
                {"estimate": test.ratio, "estimate 95 % CI low": low, "estimate 95 % CI high": high,
                 "p-value": test.pvalue}
            """,
        },
        r_inputs=NO_DATA,
        r_packages=(),  # base R (stats) only
        compare="result",
        fields=("estimate", "estimate 95 % CI low", "estimate 95 % CI high", "p-value"),
        tolerance=1e-9,
        choices=("without against=, the first group given in names= (here ward B) is the one compared against; the "
                 "ratio is ward A's rate over ward B's, with R poisson.test()'s exact interval.",
                 "the exact conditional test of the rate ratio, as R poisson.test(); statsmodels' own default is a "
                 "score test."),
        python_note="statsmodels gives the exact test but its intervals of a rate ratio are score and other "
                    "intervals, so the exact interval comes from R poisson.test().",
        also="The first rows hold each rate per 1000 units of time with its exact interval (statsmodels "
             "confint_poisson). same_within= tests equivalence of the rate ratio. simplydata prints the same answer "
             "as table.compare_rates.",
    ),
]

ENTRIES += [
    Entry(
        word="table.compare_to_truth",
        data="clinic",
        ours="""
            table = sdata.get_example("clinic")
            result = table.compare_to_truth("rapid_test", truth="infected")
            result.keep_rows_where("measure", is_equal_to="sensitivity")
            result
        """,
        code={"statsmodels": """
            import pandas as pd
            from statsmodels.stats.proportion import proportion_confint
            df = pd.read_csv("clinic.csv")
            # compare_to_truth("rapid_test", truth="infected"): the sensitivity
            has = df[df["infected"] == "yes"]                                   # (1)
            found = int((has["rapid_test"] == "positive").sum())
            low, high = proportion_confint(found, len(has), method="beta")       # (2)
            {"estimate": found / len(has), "estimate 95 % CI low": low, "estimate 95 % CI high": high,
             "count": found, "out of": len(has)}
        """},
        compare="result",
        fields=("estimate", "estimate 95 % CI low", "estimate 95 % CI high", "count", "out of"),
        tolerance=1e-10,
        choices=("\"yes\" in the truth column and \"positive\" in the test column count as having it and as a "
                 "positive result; without such words the second value in sorted order counts, as R takes the second "
                 "level; positive= chooses.",
                 "each share gets the exact Clopper-Pearson interval, as R epiR::epi.tests(method = \"exact\"); "
                 "statsmodels' own default is the normal-curve interval."),
        also="The other rows hold the specificity and the predictive values (the same exact intervals) and the "
             "likelihood ratios and diagnostic odds ratio from R epiR::epi.tests() (simplydata[r]). prevalence=1 adds "
             "the predictive values where 1 % have it. simplydata also writes the answer as people out of 1000.",
    ),
    Entry(
        word="table.compare_to_truth",
        option="a column of numbers",
        data="clinic",
        ours="""
            table = sdata.get_example("clinic")
            table.compare_to_truth("crp", truth="infected")
        """,
        code={
            "R": """
                # compare_to_truth("crp", truth="infected"): the area under the ROC curve
                # truth: 1 for infected, 0 for not; crp: the scores
                r <- pROC::roc(truth, crp, levels = c(0, 1), direction = "<", quiet = TRUE)  # (1)
                a <- pROC::ci.auc(r, method = "delong")                                  # (2)
                list(auc = as.numeric(a[2]), low = as.numeric(a[1]), high = as.numeric(a[3]))
            """,
            "Python": """
                {"estimate": auc, "estimate 95 % CI low": low, "estimate 95 % CI high": high}
            """,
        },
        r_inputs=CLINIC_TRUTH,
        r_packages=("pROC",),
        compare="result",
        fields=("estimate", "estimate 95 % CI low", "estimate 95 % CI high"),
        tolerance=1e-9,
        choices=("higher scores count as positive (direction = \"<\"), said before the curve is made; pROC's own "
                 "default guesses the direction from the data, which flatters a score that works the wrong way round. "
                 "positive_when=\"lower\" turns it round.",
                 "DeLong's interval of the AUC."),
        python_note="Python's stack (SciPy, statsmodels) has no ROC analysis with DeLong's interval, so it comes from "
                    "R pROC.",
        also="The next rows hold the best cut-off by Youden's index (pROC::coords(\"best\", best.method = "
             "\"youden\")) and the sensitivity, specificity and predictive values at that cut-off; cut_off=3 gives "
             "them at a chosen cut-off.",
    ),
    Entry(
        word="table.compare_accuracy",
        data="clinic",
        ours="""
            table = sdata.get_example("clinic")
            result = table.compare_accuracy("crp", "procalcitonin", truth="infected")
            result.keep_rows_where("measure", is_equal_to="difference in AUC (crp minus procalcitonin)")
            result
        """,
        code={
            "R": """
                # compare_accuracy("crp", "procalcitonin", truth="infected")
                r1 <- pROC::roc(truth, crp, levels = c(0, 1), direction = "<", quiet = TRUE)  # (1)
                r2 <- pROC::roc(truth, pct, levels = c(0, 1), direction = "<", quiet = TRUE)
                t <- pROC::roc.test(r1, r2, method = "delong", paired = TRUE)            # (2)
                list(d = unname(t$estimate[1] - t$estimate[2]), z = unname(t$statistic), p = t$p.value,
                     ci = as.numeric(t$conf.int))
            """,
            "Python": """
                {"estimate": d, "estimate 95 % CI low": ci[0], "estimate 95 % CI high": ci[1],
                 "statistic": z, "p-value": p}
            """,
        },
        r_inputs=CLINIC_TRUTH,
        r_packages=("pROC",),
        compare="result",
        fields=("estimate", "estimate 95 % CI low", "estimate 95 % CI high", "statistic", "p-value"),
        tolerance=1e-9,
        choices=("higher scores count as positive for both scores (direction = \"<\"), said before the curves are "
                 "made, so neither curve is turned round on its own.",
                 "DeLong's test for two curves on the same people (paired = TRUE)."),
        python_note="Python's stack (SciPy, statsmodels) has no DeLong test, so it comes from R pROC.",
        also="The first two rows hold each AUC with its DeLong interval (pROC::ci.auc()). positive_when=\"lower\" "
             "turns both round. " + SENTENCE,
    ),
    Entry(
        word="sdata.compare_to_truth",
        ours="""
            result = sdata.compare_to_truth(found=45, missed=5, false_alarms=30, correct_negatives=920)
            result.keep_rows_where("measure", is_equal_to="positive likelihood ratio")
            result
        """,
        code={
            "R": """
                # compare_to_truth(found=45, missed=5, false_alarms=30, correct_negatives=920)
                t <- as.table(matrix(c(45, 5, 30, 920), nrow = 2))                 # (1)
                d <- epiR::epi.tests(t, method = "exact")$detail                     # (2)
                k <- d$statistic == "lr.pos"
                list(est = d$est[k], low = d$lower[k], high = d$upper[k])
            """,
            "Python": """
                {"estimate": est, "estimate 95 % CI low": low, "estimate 95 % CI high": high}
            """,
        },
        r_inputs=NO_DATA,
        r_packages=("epiR",),
        compare="result",
        fields=("estimate", "estimate 95 % CI low", "estimate 95 % CI high"),
        tolerance=1e-9,
        choices=("the four counts are laid out as epiR reads them: the test result in the rows (positive first) and "
                 "the truth in the columns (has it first).",
                 "method = \"exact\": the shares get exact intervals; the likelihood ratios get epiR's intervals on "
                 "the log scale."),
        python_note="statsmodels gives the shares with exact intervals (the first rows of the result), but no "
                    "likelihood ratios with intervals, so those come from R epiR.",
        also="The first rows hold sensitivity, specificity and the predictive values with exact intervals "
             "(statsmodels proportion_confint(method=\"beta\")). sensitivity=, specificity= and prevalence= in percent "
             "give the predictive values by Bayes' rule, without intervals.",
    ),
    Entry(
        word="table.agreement_between",
        data="made-up",
        ours="""
            ratings = {"nurse": ["mild", "mild", "moderate", "moderate", "severe", "severe", "mild", "moderate"],
                       "doctor": ["mild", "moderate", "moderate", "moderate", "moderate", "moderate", "mild", "mild"]}
            table = sdata.table(ratings)
            table.agreement_between("nurse", "doctor")
        """,
        code={"statsmodels": """
            import numpy as np
            import pandas as pd
            from statsmodels.stats.inter_rater import cohens_kappa
            nurse = pd.Series(["mild", "mild", "moderate", "moderate", "severe", "severe", "mild", "moderate"])
            doctor = pd.Series(["mild", "moderate", "moderate", "moderate", "moderate", "moderate", "mild", "mild"])
            # agreement_between("nurse", "doctor"): the doctor never says "severe"
            seen = sorted(set(nurse) | set(doctor))
            counts = pd.crosstab(nurse, doctor).reindex(index=seen, columns=seen, fill_value=0).to_numpy()  # (1)
            res = cohens_kappa(counts, wt=None)                                   # (2)
            {"estimate": res["kappa"], "estimate 95 % CI low": res["kappa_low"],
             "estimate 95 % CI high": res["kappa_upp"], "statistic": res["z_value"],
             "raw agreement": np.trace(counts) / counts.sum()}
        """},
        compare="result",
        fields=("estimate", "estimate 95 % CI low", "estimate 95 % CI high", "statistic", "raw agreement"),
        tolerance=1e-10,
        choices=("a square table of counts with every category either rater used, in sorted order, so a category "
                 "only one rater used (\"severe\" here) still counts.",
                 "Cohen's kappa without weights, as R irr::kappa2(); near_misses=\"linear\" or \"quadratic\" counts "
                 "near misses as partly right (wt=\"linear\", \"quadratic\")."),
        also="Three or more columns get Fleiss' kappa (statsmodels fleiss_kappa, its p-value from R irr), columns of "
             "numbers the intraclass correlation (the next box). simplydata also gives the agreement chance alone "
             "would give, and says that agreement is not correlation.",
    ),
    Entry(
        word="table.agreement_between",
        option="columns of numbers",
        data="clinic",
        ours="""
            table = sdata.get_example("clinic")
            table.agreement_between("device_a", "device_b")
        """,
        code={
            "R": """
                # agreement_between("device_a", "device_b")
                i <- irr::icc(cbind(a, b), model = "twoway", type = "agreement",     # (1)
                              unit = "single")                                       # (2)
                list(value = i$value, low = i$lbound, high = i$ubound, f = i$Fvalue, p = i$p.value)
            """,
            "Python": """
                {"estimate": value, "estimate 95 % CI low": low, "estimate 95 % CI high": high,
                 "statistic": f, "p-value": p}
            """,
        },
        r_inputs=DEVICES,
        r_packages=("irr",),
        compare="result",
        fields=("estimate", "estimate 95 % CI low", "estimate 95 % CI high", "statistic", "p-value"),
        tolerance=1e-9,
        choices=("two-way, absolute agreement: the raters are a sample of many possible raters, and a rater who always "
                 "reads higher counts against agreement (ICC(A,1), Shrout and Fleiss ICC(2,1)); irr's own default is "
                 "the one-way model with consistency.",
                 "the agreement of one rater, not of the average of the raters (of=\"average of raters\")."),
        python_note="Python's stack (SciPy, statsmodels) has no intraclass correlation, so it comes from R irr.",
        also="raters=\"these only\" or \"different per row\" and checking_for=\"consistency\" choose another form, and "
             "the form is always named. test_method=\"lin\" gives Lin's concordance correlation (R DescTools::CCC()).",
    ),
    Entry(
        word="table.limits_of_agreement",
        data="clinic",
        ours="""
            table = sdata.get_example("clinic")
            table.limits_of_agreement("device_a", "device_b")
        """,
        code={
            "R": """
                # limits_of_agreement("device_a", "device_b")
                s <- BlandAltmanLeh::bland.altman.stats(a, b, conf.int = 0.95)       # (1)
                k <- DescTools::CCC(a, b, conf.level = 0.95)$rho.c                    # (2)
                list(mean = s$mean.diffs, lower = s$lower.limit, upper = s$upper.limit,
                     ci = unname(s$CI.lines), ccc = k$est, ccc_low = k$lwr.ci)
            """,
            "Python": """
                {"average difference": mean, "average difference 95 % CI low": ci[2],
                 "lower limit": lower, "lower limit 95 % CI low": ci[0], "upper limit": upper,
                 "upper limit 95 % CI high": ci[5], "concordance correlation": ccc,
                 "concordance correlation 95 % CI low": ccc_low}
            """,
        },
        r_inputs=DEVICES,
        r_packages=("BlandAltmanLeh", "DescTools"),
        compare="result",
        fields=("average difference", "average difference 95 % CI low", "lower limit", "lower limit 95 % CI low",
                "upper limit", "upper limit 95 % CI high", "concordance correlation",
                "concordance correlation 95 % CI low"),
        tolerance=1e-9,
        choices=("the difference is the first column minus the second; the limits are the average difference plus and "
                 "minus 1.96 standard deviations (with n - 1), each with its t interval.",
                 "Lin's concordance correlation beside the limits, with its interval on Fisher's z scale."),
        python_note="statsmodels mean_diff_plot draws the limits but gives no intervals (and uses n in the standard "
                    "deviation), so the numbers come from R.",
        also="simplydata also says how much the first reads higher or lower in words, and that whether the limits are "
             "close enough is a question for the field. chart.draw_difference_dots() draws it.",
    ),
    Entry(
        word="table.reliability_of",
        data="clinic",
        ours="""
            table = sdata.get_example("clinic")
            table.reliability_of(["item_1", "item_2", "item_3", "item_4", "item_5"])
        """,
        code={
            "R": """
                # reliability_of(["item_1", "item_2", "item_3", "item_4", "item_5"])
                # x: the five item columns, one row per person
                a <- psych::alpha(as.data.frame(x), check.keys = FALSE)               # (1)
                f <- psych::alpha.ci(a$total$raw_alpha, n.obs = nrow(x), n.var = ncol(x),
                                     p.val = 0.05)                                    # (2)
                list(alpha = a$total$raw_alpha, low = f$lower.ci, high = f$upper.ci)
            """,
            "Python": """
                {"estimate": alpha, "estimate 95 % CI low": low, "estimate 95 % CI high": high}
            """,
        },
        r_inputs="""
            import pandas as pd
            df = pd.read_csv("clinic.csv")
            x = df[["item_1", "item_2", "item_3", "item_4", "item_5"]].to_numpy(dtype=float)
        """,
        r_packages=("psych",),
        compare="result",
        fields=("estimate", "estimate 95 % CI low", "estimate 95 % CI high"),
        tolerance=1e-9,
        choices=("raw alpha with the items as they are (check.keys = FALSE): an item scored the other way round is "
                 "not turned round without saying so.",
                 "Feldt's 95 % interval (psych::alpha.ci())."),
        python_note="Python's stack (SciPy, statsmodels) has no Cronbach's alpha with Feldt's interval, so it comes "
                    "from R psych.",
        also="The next rows hold alpha without each item (psych::alpha()$alpha.drop). Rows with an empty cell are "
             "left out. simplydata also names the item whose removal would raise alpha, and says that alpha does not "
             "show that the items measure one thing.",
    ),
    Entry(
        word="draw_difference_dots",
        data="clinic",
        ours="""
            chart = sdata.chart(sdata.get_example("clinic"))
            chart.draw_difference_dots(first="device_a", second="device_b")
        """,
        code={
            "R": """
                # draw_difference_dots(first="device_a", second="device_b"): the limits of agreement
                s <- BlandAltmanLeh::bland.altman.stats(a, b)                    # (1)
                list(lower = s$lower.limit, upper = s$upper.limit)
            """,
            "statsmodels": """
                import pandas as pd
                import matplotlib.pyplot as plt
                from statsmodels.graphics.agreement import mean_diff_plot
                df = pd.read_csv("clinic.csv")
                fig, ax = plt.subplots()
                mean_diff_plot(df["device_a"], df["device_b"], ax=ax, sd_limit=0)   # (2)
                for limit in (lower, upper):
                    ax.axhline(limit, linestyle="--")
                ax.set_xlabel("Average of device_a and device_b")
                ax.set_ylabel("device_a minus device_b")
                ax.set_title("")
            """,
        },
        r_inputs=DEVICES,
        r_packages=("BlandAltmanLeh",),
        compare="chart",
        check=("dots", "lines", "labels"),
        choices=("the limits of agreement come from R, with the standard deviation on n - 1, as "
                 "table.limits_of_agreement() gives them.",
                 "statsmodels draws the dots and the average difference; sd_limit=0 leaves out its own limits, whose "
                 "standard deviation uses n."),
        python_note="statsmodels mean_diff_plot draws the dots, but its limits use n in the standard deviation and "
                    "come without intervals, so the limits come from R BlandAltmanLeh.",
        also="simplydata also shades the 95 % interval of each limit and writes each limit's value beside its line.",
    ),
]

ENTRIES += [
    Entry(
        word="sdata.find_where_smallest",
        ours="""
            sdata.find_where_smallest("x**4 - 3*x", between=[0, 2])
        """,
        code={"SciPy": """
            from scipy import optimize
            # find_where_smallest("x**4 - 3*x", between=[0, 2])
            found = optimize.minimize_scalar(lambda x: x**4 - 3*x, bounds=(0, 2),
                                             method="bounded",                      # (1)
                                             options={"xatol": 1e-10, "maxiter": 10000})  # (2)
            {"x": found.x, "smallest value": found.fun}
        """},
        compare="result",
        fields=("x", "smallest value"),
        tolerance=1e-12,
        choices=("one name with a range: Brent's method on the range, as R optimize(); the method is decided by what "
                 "you give (start=, rules=, search=) and printed.",
                 "a tolerance of 1e-10, as R optimize(tol = 1e-10); SciPy's own default stops at 1e-5."),
        also="simplydata also checks 200 evenly spaced points and the two ends of the range, and says when the curve "
             "has several dips. Several names use Nelder-Mead from start= (R optim()) or L-BFGS-B with between=; "
             "rules= use SLSQP or, for straight-line formulas, linear programming.",
    ),
    Entry(
        word="sdata.find_where_biggest",
        ours="""
            sdata.find_where_biggest("3*x + 2*y", rules=["x + y <= 4", "x + 3*y <= 6", "y >= -1"])
        """,
        code={"SciPy": """
            from scipy import optimize
            # find_where_biggest("3*x + 2*y", rules=["x + y <= 4", "x + 3*y <= 6", "y >= -1"])
            res = optimize.linprog(c=[-3, -2], A_ub=[[1, 1], [1, 3], [0, -1]], b_ub=[4, 6, 1],  # (1)
                                   bounds=[(None, None), (None, None)], method="highs")       # (2)
            {"x": res.x[0], "y": res.x[1], "biggest value": -res.fun,
             "value of one more: x + y <= 4": -res.ineqlin.marginals[0],
             "value of one more: y >= -1": res.ineqlin.marginals[2]}
        """},
        compare="result",
        fields=("x", "y", "biggest value", "value of one more: x + y <= 4", "value of one more: y >= -1"),
        tolerance=1e-12,
        choices=("a straight-line formula with straight-line rules is a linear program, solved exactly (HiGHS, as R "
                 "lpSolve::lp(), except that lp() takes every name to be 0 or more, see (2)); the biggest value is the "
                 "smallest value of minus the formula, and a rule with >= is turned into <= by changing its signs.",
                 "the names may be any number unless a rule or between= limits them: simplydata passes bounds=(None, "
                 "None), while SciPy linprog's own default (0, None) and R lp() take every name to be 0 or more; here "
                 "y may go down to -1, which gives 13 instead of 12."),
        also="The \"value of one more\" of each rule is its shadow price: how much the biggest value grows when the "
             "right side of the rule grows by 1 (R lp(compute.sens = TRUE)$duals). whole_numbers=True gives mixed-"
             "integer linear programming (SciPy milp). simplydata also says which rules are reached exactly.",
    ),
    Entry(
        word="sdata.solve",
        ours="""
            result = sdata.solve("x**3 - 2*x = 0.5", between=[-2, 2])
            result.keep_columns("x")
            result
        """,
        code={"SciPy": """
            import numpy as np
            import pandas as pd
            from scipy import optimize
            # solve("x**3 - 2*x = 0.5", between=[-2, 2])
            gap = lambda x: x**3 - 2*x - 0.5                    # left minus right
            xs = np.linspace(-2, 2, 1001)                       # (1)
            ys = gap(xs)
            roots = [optimize.brentq(gap, a, b, xtol=1e-12, maxiter=1000)          # (2)
                     for a, b, ya, yb in zip(xs[:-1], xs[1:], ys[:-1], ys[1:]) if ya * yb < 0]
            pd.DataFrame({"x": roots})
        """},
        compare="table",
        tolerance=1e-12,
        choices=("the range is cut into 1000 steps and every step where the two sides cross is searched, so every "
                 "solution that crosses is found (as R rootSolve::uniroot.all()), not only one.",
                 "Brent's method in each step with a tolerance of 1e-12, as R uniroot(tol = 1e-12); SciPy's own "
                 "default (2e-12) gives the same roots here."),
        also="start= finds one solution with the secant method; a polynomial without between= or start= gives all its "
             "solutions, complex ones too (NumPy polyroots, as R polyroot()); several equations use SciPy root "
             "(Powell's hybrid method, as R nleqslv). The result also holds \"left minus right\" at each solution, the "
             "check that it is close to 0.",
    ),
    Entry(
        word="table.find_values_at",
        data="made-up",
        ours="""
            growth = {"year": [2000, 2002, 2002, 2004, 2000, 2002, 2004],
                      "country": ["A", "A", "A", "A", "B", "B", "B"], "population": [10, 11, 13, 14, 20, 22, 23]}
            table = sdata.table(growth)
            table.find_values_at("population", at={"year": [1999, 2001, 2003]}, for_each_group_in="country")
        """,
        code={"pandas": """
            import numpy as np
            import pandas as pd
            df = pd.DataFrame({"year": [2000, 2002, 2002, 2004, 2000, 2002, 2004],
                               "country": ["A", "A", "A", "A", "B", "B", "B"], "population": [10, 11, 13, 14, 20, 22, 23]})
            # find_values_at("population", at={"year": [1999, 2001, 2003]}, for_each_group_in="country")
            at, parts = np.array([1999, 2001, 2003]), []
            for country, rows in df.groupby("country"):
                known = rows.groupby("year")["population"].mean()                     # (1)
                found = np.interp(at, known.index, known.to_numpy(),
                                  left=np.nan, right=np.nan)                          # (2)
                parts.append(pd.DataFrame({"year": at, "country": country, "population": found}))
            pd.concat(parts, ignore_index=True)
        """},
        compare="table",
        tolerance=1e-12,
        choices=("several values at the same place (country A in 2002) are averaged first, as R approx(ties = mean).",
                 "straight lines between neighbours (NumPy interp, as R approx()), and places outside the known points "
                 "stay empty, as R approx(rule = 1); NumPy's own default carries the end value on, which "
                 "outside=\"nearest end\" gives."),
        also="joined_by= takes \"smooth curve\" (natural cubic spline, SciPy CubicSpline), \"curve without "
             "overshoot\" (PCHIP), \"steps\" and \"nearest\"; smoothness= gives a smoothing spline. Two or more at= "
             "columns join across a surface (SciPy RegularGridInterpolator, griddata). simplydata also counts the "
             "places left empty.",
    ),
    Entry(
        word="table.make_map_of",
        data="island",
        ours="""
            table = sdata.get_example("island")
            table.make_map_of("height", across=["east", "north"], steps=4)
        """,
        code={"SciPy": """
            import numpy as np
            import pandas as pd
            from scipy import interpolate
            df = pd.read_csv("island.csv")
            # make_map_of("height", across=["east", "north"], steps=4)
            grid = df.groupby(["east", "north"])["height"].mean().unstack()           # (1)
            east, north = grid.index.to_numpy(dtype=float), grid.columns.to_numpy(dtype=float)
            reader = interpolate.RegularGridInterpolator((east, north), grid.to_numpy(dtype=float),
                                                         bounds_error=False, fill_value=np.nan)  # (2)
            e, n = np.meshgrid(np.linspace(east.min(), east.max(), 4),
                               np.linspace(north.min(), north.max(), 4), indexing="ij")         # (3)
            pd.DataFrame({"east": e.ravel(), "north": n.ravel(),
                          "height": reader(np.column_stack([e.ravel(), n.ravel()]))})
        """},
        compare="table",
        tolerance=1e-12,
        choices=("the known points form a full grid (every east with every north), so they are read as a grid; "
                 "scattered points are joined by flat triangles instead (SciPy griddata, as R interp::interp()).",
                 "straight lines along each direction (bilinear interpolation, RegularGridInterpolator's "
                 "method=\"linear\").",
                 "steps= evenly spaced places from the smallest to the biggest known value of each column, every "
                 "combination, the first column changing slowest."),
        also="joined_by=\"smooth surface\" gives a thin-plate spline (SciPy RBFInterpolator). simplydata also says how "
             "the points were joined and how many places are empty. The long table is ready for draw_contour() or "
             "draw_heatmap().",
    ),
    Entry(
        word="table.compare_distributions_for",
        data="shop",
        ours="""
            table = sdata.get_example("shop")
            table.compare_distributions_for("sales")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import stats
            x = pd.read_csv("shop.csv", parse_dates=["date"])["sales"].dropna().to_numpy(dtype=float)
            # compare_distributions_for("sales")
            fits = {"normal": stats.norm, "lognormal": stats.lognorm, "gamma": stats.gamma,
                    "weibull": stats.weibull_min}
            aic, params = {}, {}
            for name, family in fits.items():
                held = {} if name == "normal" else {"floc": 0}                        # (1)
                params[name] = p = family.fit(x, **held)
                aic[name] = 2 * (len(p) - len(held)) - 2 * family.logpdf(x, *p).sum()   # (2)
            best = min(aic, key=aic.get)
            {"distribution": best, "AIC": aic[best], "AIC difference": 0.0,
             "Kolmogorov-Smirnov statistic": stats.kstest(x, fits[best].cdf, args=params[best]).statistic}
        """},
        compare="result",
        fields=("distribution", "AIC", "AIC difference", "Kolmogorov-Smirnov statistic"),
        tolerance=1e-7,
        choices=("each distribution is fitted by maximum likelihood; the families for positive values start at 0 "
                 "(floc=0), as R MASS::fitdistr() and fitdistrplus fit them, not with SciPy's own extra location.",
                 "AIC counts only the parameters that were fitted, and the rows are sorted by it, smallest (best) "
                 "first."),
        also="simplydata fits the normal and lognormal in closed form, the gamma with SciPy gamma.fit(floc=0) and the "
             "Weibull by solving its score equation for the shape itself (brentq), the same answer as "
             "weibull_min.fit(floc=0); the numbers agree to 7 digits because the Weibull shape is a search. Each row also holds the "
             "log-likelihood, BIC and the Anderson-Darling and Cramer-von Mises statistics, as R "
             "fitdistrplus::gofstat(). simplydata says that an AIC difference below 2 is too small to choose by.",
    ),
    Entry(
        word="nums.fit_distribution",
        ours="""
            numbers = sdata.numbers([12, 15, 9, 20, 14])
            fit = numbers.fit_distribution("gamma")
            fit.turn_into_table()
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import stats
            x = np.array([12, 15, 9, 20, 14], dtype=float)
            # fit_distribution("gamma")
            shape, _, scale = stats.gamma.fit(x, floc=0)                # (1)
            {"shape": shape, "rate": 1 / scale,                         # (2)
             "log-likelihood": stats.gamma.logpdf(x, shape, scale=scale).sum()}
        """},
        compare="result",
        fields=("shape", "rate", "log-likelihood"),
        tolerance=1e-10,
        choices=("maximum likelihood with the gamma starting at 0 (floc=0), as R MASS::fitdistr(x, \"gamma\"); SciPy's "
                 "own fit also moves the start.",
                 "the second parameter is the rate (1 / SciPy's scale), as R's dgamma(shape, rate)."),
        also="Empty values are left out. A fitted distribution answers the distribution words (find_chance_that_value, "
             "find_percentile ...); turn_into_table() also gives the standard errors, AIC and BIC.",
    ),
    Entry(
        word="dist.find_density_at",
        ours="""
            distribution = sdata.distribution("gamma", shape=2, rate=0.5)
            distribution.find_density_at(3)
        """,
        code={"SciPy": """
            from scipy import stats
            dist = stats.gamma(a=2, scale=1 / 0.5)       # (1)
            # find_density_at(value=3)
            dist.pdf(3)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the parameters have R's names (shape, rate), turned into SciPy's (a, scale = 1 / rate).",),
        also="A list of values gives Numbers. simplydata also says that a density is not a chance, with the same call "
             "in R (dgamma(3, shape = 2, rate = 0.5)).",
    ),
    Entry(
        word="dist.find_cut_off",
        ours="""
            distribution = sdata.distribution("normal", average=50, standard_deviation=10)
            distribution.find_cut_off(with_chance_above=1e-9)
        """,
        code={"SciPy": """
            from scipy import stats
            dist = stats.norm(loc=50, scale=10)
            # find_cut_off(with_chance_above=1e-9), a chance of one in a billion
            dist.isf(1e-9)                  # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the value with a chance above it is the inverse survival function isf(), not ppf(1 - chance): it "
                 "stays accurate far out in the tail (1 - 1e-9 cannot be stored exactly). with_chance_below= "
                 "uses ppf().",),
        also="Chances are shares from 0 to 1; a list gives Numbers. For counts it is the smallest count with at most "
             "that chance above it, as R qbinom(lower.tail = FALSE). simplydata also gives the same call in R "
             "(qnorm(1e-09, mean = 50, sd = 10, lower.tail = FALSE)).",
    ),
    Entry(
        word="dist.find_middle_range",
        ours="""
            distribution = sdata.distribution("normal", average=50, standard_deviation=10)
            distribution.find_middle_range(95)
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import stats
            dist = stats.norm(loc=50, scale=10)
            # find_middle_range(percent=95)
            tail = (1 - 0.95) / 2                                  # (1)
            high = 1 - tail
            np.array([dist.ppf(tail), dist.isf(1 - high)])       # a share above 0.5 goes through isf()
        """},
        compare="value",
        tolerance=1e-12,
        choices=("equal tails: half of what is left (2.5 % here) is cut off at each end, not the shortest range.",),
        also="The upper end is the share 1 - tail, read through isf() of what lies above it, as simplydata's "
             "percentiles do for shares above 0.5; because the share is formed first, this gains nothing over ppf() "
             "when the percent is very close to 100. simplydata gives back Numbers [low, high] and the same call in "
             "R (qnorm(c(0.025, 0.975), mean = 50, sd = 10)); for counts each end holds at least that share.",
    ),
    Entry(
        word="dist.find_average",
        ours="""
            distribution = sdata.distribution("gamma", shape=2, rate=0.5)
            distribution.find_average()
        """,
        code={"SciPy": """
            from scipy import stats
            dist = stats.gamma(a=2, scale=1 / 0.5)       # (1)
            # find_average()
            dist.mean()
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the parameters have R's names (shape, rate), turned into SciPy's (a, scale = 1 / rate).",),
        also="A distribution with tails too heavy for an average (Cauchy) gets a sentence that says so.",
    ),
    Entry(
        word="dist.find_median",
        ours="""
            distribution = sdata.distribution("gamma", shape=2, rate=0.5)
            distribution.find_median()
        """,
        code={"SciPy": """
            from scipy import stats
            curve = stats.gamma(a=2, scale=1 / 0.5)       # (1)
            # find_median()
            curve.median()
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the parameters have R's names (shape, rate), turned into SciPy's (a, scale = 1 / rate).",),
        also="The median is the 50 % point, the same as distribution.find_percentile(50) and R qgamma(0.5, shape = 2, "
             "rate = 0.5).",
    ),
    Entry(
        word="dist.find_standard_deviation",
        ours="""
            distribution = sdata.distribution("gamma", shape=2, rate=0.5)
            distribution.find_standard_deviation()
        """,
        code={"SciPy": """
            from scipy import stats
            dist = stats.gamma(a=2, scale=1 / 0.5)       # (1)
            # find_standard_deviation()
            dist.std()
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the parameters have R's names (shape, rate), turned into SciPy's (a, scale = 1 / rate).",),
        also="This is the spread of the distribution itself, not of a sample, so there is no n - 1.",
    ),
    Entry(
        word="dist.find_variance",
        ours="""
            distribution = sdata.distribution("gamma", shape=2, rate=0.5)
            distribution.find_variance()
        """,
        code={"SciPy": """
            from scipy import stats
            dist = stats.gamma(a=2, scale=1 / 0.5)       # (1)
            # find_variance()
            dist.var()
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the parameters have R's names (shape, rate), turned into SciPy's (a, scale = 1 / rate).",),
        also="The variance is the standard deviation squared.",
    ),
    Entry(
        word="dist.show_summary",
        ours="""
            distribution = sdata.distribution("gamma", shape=2, rate=0.5)
            distribution.show_summary()
        """,
        code={"SciPy": """
            import math
            from scipy import stats
            curve = stats.gamma(a=2, scale=1 / 0.5)
            # show_summary()
            mean, var, skew, kurt = curve.stats(moments="mvsk")      # (1)
            low, high = curve.support()
            {"average": mean, "median": curve.median(), "standard deviation": math.sqrt(var), "variance": var,
             "skewness": skew, "excess kurtosis": kurt, "entropy": curve.entropy(),
             "lowest possible": low, "highest possible": high}
        """},
        compare="result",
        fields=("average", "median", "standard deviation", "variance", "skewness", "excess kurtosis", "entropy",
                "lowest possible", "highest possible"),
        tolerance=1e-12,
        choices=("the kurtosis is the excess kurtosis (0 for the normal distribution), as SciPy gives it.",),
        also="The entropy is in nats (natural logarithms). simplydata also writes the parameters in words and the "
             "summary in a sentence.",
    ),
    Entry(
        word="dist.make_random_numbers",
        ours="""
            distribution = sdata.distribution("normal", average=50, standard_deviation=10)
            distribution.make_random_numbers(how_many=5, with_seed=1)
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import stats
            dist = stats.norm(loc=50, scale=10)
            # make_random_numbers(how_many=5, with_seed=1)
            dist.rvs(size=5, random_state=np.random.default_rng(1))      # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("NumPy's generator (PCG64) seeded with with_seed=1, so the same seed gives the same numbers; R's "
                 "rnorm() uses another generator, so its numbers differ.",),
        also="rows= and columns= give a grid. with_seed=None gives different numbers each time.",
    ),
    Entry(
        word="dist.draw_chart",
        ours="""
            distribution = sdata.distribution("normal", average=50, standard_deviation=10)
            distribution.draw_chart()
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import numpy as np
            from scipy import stats
            dist = stats.norm(loc=50, scale=10)
            # draw_chart()
            fig, ax = plt.subplots()
            xs = np.linspace(dist.ppf(0.001), dist.ppf(0.999), 200)     # (1)
            ax.plot(xs, dist.pdf(xs))
            ax.set_xlabel("value")
            ax.set_ylabel("density")
        """},
        compare="chart",
        check=("lines", "labels"),
        choices=("the curve runs from the 0.1 % point to the 99.9 % point (the ends of the possible values where they "
                 "are closer), at 200 evenly spaced places.",),
        also="show=\"cumulative\" draws the chance at or below each value (cdf); counts (binomial, Poisson ...) get "
             "bars of the chance of each value (pmf). between= sets the range.",
    ),
    Entry(
        word="dist.turn_into_table",
        ours="""
            distribution = sdata.distribution("gamma", shape=2, rate=0.5)
            distribution.turn_into_table()
        """,
        code={"pandas": """
            import pandas as pd
            # turn_into_table() of distribution("gamma", shape=2, rate=0.5)
            pd.DataFrame({"distribution": ["gamma"], "shape": [2.0], "rate": [0.5]})   # (1)
        """},
        compare="table",
        tolerance=1e-12,
        choices=("one row with the parameters under their plain names (R's names, shape and rate; underscores become "
                 "spaces), not SciPy's (a, scale); parameters not given are left out.",),
        also="A fitted distribution (fit_distribution) also gives the standard errors, log-likelihood, AIC and BIC.",
    ),
    Entry(
        word="dist.show_parameters",
        ours="""
            distribution = sdata.distribution("normal", average=50, standard_deviation=10)
            distribution.show_parameters()
        """,
        compare="none",
        note="simplydata's own: it gives back the parameters as a Python dictionary of plain names, "
             "{\"average\": 50.0, \"standard_deviation\": 10.0}; SciPy keeps them as args and kwds (loc, scale).",
    ),
    Entry(
        word="table.find_principal_components_of",
        data="meadow",
        ours="""
            table = sdata.get_example("meadow")
            table.find_principal_components_of()
        """,
        code={"statsmodels": """
            import numpy as np
            import pandas as pd
            from statsmodels.multivariate.pca import PCA
            x = pd.read_csv("meadow.csv").select_dtypes("number")
            # find_principal_components_of()
            z = (x - x.mean()) / x.std()                                           # (1)
            pca = PCA(z, standardize=False, demean=False, normalize=False, method="svd")
            sd = np.sqrt(np.asarray(pca.eigenvals) / (len(z) - 1))                 # (2)
            w = np.asarray(pca.loadings)
            w = w * np.sign(w[np.abs(w).argmax(axis=0), np.arange(w.shape[1])])     # (3)
            share = sd**2 / (sd**2).sum() * 100
            out = pd.DataFrame({"component": [f"PC{i + 1}" for i in range(len(sd))], "standard deviation": sd,
                                "spread explained (%)": share, "cumulative (%)": share.cumsum()})
            pd.concat([out, pd.DataFrame(w.T, columns=["weight of " + c for c in x.columns])], axis=1)
        """},
        compare="table",
        tolerance=1e-9,
        choices=("every number column is put on the same scale first (mean 0, standard deviation with n - 1), as R "
                 "prcomp(scale. = TRUE); same_scale=False leaves the columns as they are.",
                 "the standard deviation of each component divides by n - 1, as R prcomp()$sdev.",
                 "the sign of a component is arbitrary and differs between computers, so each one is turned so its "
                 "biggest weight is positive."),
        also="The weights are R prcomp()$rotation. simplydata also says how much of the spread the first two "
             "components hold. table.add_principal_components() adds the scores as columns.",
    ),
    Entry(
        word="table.use_survey_design",
        data="sampled_schools",
        ours="""
            table = sdata.get_example("sampled_schools")
            table.use_survey_design(weights="weight", strata="school_type", clusters="district")
            table.find_average_of("score_2000")
        """,
        code={
            "R": """
                # use_survey_design(weights="weight", strata="school_type", clusters="district")
                op <- options(survey.lonely.psu = "adjust")                       # (1)
                d <- survey::svydesign(ids = ~cl, strata = ~s, weights = ~w, nest = TRUE,   # (2)
                                       data = data.frame(cl, s, w, y))
                m <- survey::svymean(~y, d)                    # then find_average_of("score_2000")
                ci <- confint(m, df = survey::degf(d))                            # (3)
                options(op)
                list(est = coef(m), se = survey::SE(m), low = ci[1], df = survey::degf(d))
            """,
            "Python": """
                {"average of score_2000": est, "standard error": se, "average of score_2000 95 % CI low": low,
                 "degrees of freedom": df}
            """,
        },
        r_inputs="""
            import pandas as pd
            df = pd.read_csv("sampled_schools.csv")
            cl = df["district"].to_numpy(dtype=str)
            s = df["school_type"].to_numpy(dtype=str)
            w = df["weight"].to_numpy(dtype=float)
            y = df["score_2000"].to_numpy(dtype=float)
        """,
        r_packages=("survey",),
        compare="result",
        fields=("average of score_2000", "standard error", "average of score_2000 95 % CI low", "degrees of freedom"),
        tolerance=1e-9,
        choices=("a stratum with only one cluster is centred at the overall average (survey.lonely.psu = \"adjust\"); "
                 "survey's own default stops with an error.",
                 "clusters are counted within their stratum (nest = TRUE): a district that turns up in two school "
                 "types is two clusters; without it survey refuses these data.",
                 "the intervals use t on the design's degrees of freedom (degf(design), here 159), not survey's own "
                 "normal-curve confint()."),
        python_note="statsmodels has weights but no strata, clusters or population sizes, so the design and every "
                    "number after it come from R survey (Lumley).",
        also="The word itself only sets the design up and prints its strata, clusters and degrees of freedom; the "
             "survey words after it (find_average_of, find_total_of, explain ...) give the design-based answers. "
             "population_sizes= is survey's fpc=. table.use_survey_design() with no options turns it off.",
    ),
]
