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
            dist = sdata.distribution("normal", average=50, standard_deviation=10)
            dist.find_chance_that_value(is_above=80)
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
            dist = sdata.distribution("normal", average=50, standard_deviation=10)
            dist.find_percentile(95)
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
