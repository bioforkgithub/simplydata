"""Statistics words: the call in SciPy or statsmodels that gives the main numbers.

For words that do a long job (choose the test, check the spreads, effect size, a sentence), the code
shows the core of it: the call that gives the numbers in simplydata's result table.
"""

from . import Entry

SENTENCE = "simplydata also writes the result as a sentence and names the test."

ENTRIES = [
    Entry(
        word="table.compare_averages_of",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.compare_averages_of("marks", for_each_group_in="class")
        """,
        code={"statsmodels": """
            from statsmodels.stats.oneway import anova_oneway
            df = sdata.get_example("marks")
            # the core of compare_averages_of("marks", for_each_group_in="class")
            groups = [rows["marks"] for _, rows in df.groupby("class", sort=False)]
            res = anova_oneway(groups, use_var="unequal")      # (1)
            {"statistic": res.statistic, "degrees of freedom 1": res.df_num,
             "degrees of freedom 2": res.df_denom, "p-value": res.pvalue}
        """},
        compare="result",
        fields=("statistic", "degrees of freedom 1", "degrees of freedom 2", "p-value"),
        tolerance=1e-9,
        choices=("Welch's one-way ANOVA, which does not assume the groups have the same spread; with two groups "
                 "simplydata uses Welch's t-test (SciPy stats.ttest_ind with equal_var=False). SciPy's and "
                 "statsmodels' own defaults assume equal spreads.",),
        also="simplydata also chooses the test from the number of groups, adds an effect size (R effectsize, "
             "when R is there) and the averages of the groups. " + SENTENCE,
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
        choices=("the chance above a value is the survival function sf(), not 1 - cdf(): it stays exact far "
                 "out in the tail.",),
        also="simplydata also says the chance in a sentence, with the same call in R "
             "(pnorm(80, mean = 50, sd = 10, lower.tail = FALSE)).",
    ),
]
