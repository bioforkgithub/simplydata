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
            df = sdata.get_example("trial")
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
            df = sdata.get_example("marks")
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
]
