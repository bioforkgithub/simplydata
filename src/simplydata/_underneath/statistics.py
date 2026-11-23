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
            table = sdata.table(sdata.get_example("trial"))
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
            table = sdata.table(sdata.get_example("marks"))
            table.fit_line(x="hours", y="marks")
        """,
        code={"SciPy": """
            from scipy import stats
            import pandas as pd
            df = pd.read_csv("marks.csv")
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
            table = sdata.table(sdata.get_example("marks"))
            table.compare_spreads_of("marks", for_each_group_in="class")
        """,
        code={"SciPy": """
            from scipy import stats
            import pandas as pd
            df = pd.read_csv("marks.csv")
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
            table = sdata.table(sdata.get_example("school"))
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
            table = sdata.table(sdata.get_example("meadow"))
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
            table = sdata.table(sdata.get_example("school"))
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
