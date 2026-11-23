"""Hidden factors (phase S3c-2): find_hidden_factors_behind (R psych, with GPArotation) and check_hidden_factors
(R lavaan), each with one entry for every option that changes what it calls in R (keyed by word and option).
"""

from . import Entry

TESTS = """
    import pandas as pd
    tests = pd.read_csv("ability_tests.csv")
    x = tests[["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"]].to_numpy(dtype=float)
"""
COLUMNS = '["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"]'
EXPLORE = """
    table = sdata.get_example("ability_tests")
    table.find_hidden_factors_behind({columns}{more})
"""
LOADINGS = ("factor 1", "factor 2", "factor 3", "shared part")
LOADINGS_PYTHON = """
    {"factor 1": f1, "factor 2": f2, "factor 3": f3, "shared part": h2}
"""
EXPLORE_NOTE = ("statsmodels Factor has principal-axis and maximum-likelihood factor analysis with varimax or promax, "
                "but no minres, no oblimin and no parallel analysis, so the numbers come from R psych.")
EXPLORE_ALSO = ("simplydata also says why it chose that many factors, leaves loadings below 0.3 blank in the printout, "
                "gives each column's shared and own part, and adds notes on the KMO, the rows per column and the "
                "columns that go with no factor or with two.")
MEASURED_BY = '{"visual": ["x1", "x2", "x3"], "textual": ["x4", "x5", "x6"], "speed": ["x7", "x8", "x9"]}'
CONFIRM_NOTE = ("statsmodels has no confirmatory factor analysis and Python's semopy is not on conda-forge, so the "
                "numbers come from R lavaan.")
CONFIRM_ALSO = ("simplydata also gives the chi-square test as a count of studies, says what CFI, TLI, RMSEA and SRMR "
                "mean with the commonly used guides (as guides, not pass marks), and names the largest modification "
                "indices with a warning against changing the model only to fit these data.")


def _explore_entry(option, more, fit, choices):
    return Entry(
        word="table.find_hidden_factors_behind",
        option=option,
        data="ability_tests",
        ours=EXPLORE.format(columns=COLUMNS, more=more),
        code={"R": fit, "Python": LOADINGS_PYTHON},
        r_inputs=TESTS,
        r_packages=("psych", "GPArotation"),
        compare="result",
        fields=LOADINGS,
        tolerance=1e-6,
        choices=choices,
        python_note=EXPLORE_NOTE,
        also=EXPLORE_ALSO,
    )


ENTRIES = [
    _explore_entry("", "", """
        # find_hidden_factors_behind(["x1", ..., "x9"])
        x <- as.data.frame(x)
        set.seed(1)                                                   # (1)
        pa <- psych::fa.parallel(x, fm = "minres", fa = "fa",
                                 plot = FALSE)                        # (2)
        f <- psych::fa(x, nfactors = pa$nfact, fm = "minres",         # (3)
                       rotate = "oblimin")                            # (4)
        L <- unclass(f$loadings)
        list(f1 = L[1, 1], f2 = L[1, 2], f3 = L[1, 3], h2 = f$communality[1])
    """, ("with_seed=1: parallel analysis compares the data with random data, and the oblimin rotation starts from "
          "random numbers too, so R's random numbers are seeded and the answer repeats.",
          "how_many=\"automatic\": parallel analysis (Horn 1965) keeps the factors that stand out more than in random "
          "data of the same size; the 'eigenvalue above 1' rule finds too many (Zwick & Velicer 1986).",
          "test_method=\"minres\", psych's default: it gives an answer where maximum likelihood can fail (base R factanal "
          "uses maximum likelihood).",
          "rotation=\"oblimin\" (through GPArotation): the factors may correlate, as they usually do in real data "
          "(base R factanal uses varimax, which keeps them uncorrelated).")),
    _explore_entry("how_many=", ", how_many=3", """
        # find_hidden_factors_behind([...], how_many=3)
        x <- as.data.frame(x)
        set.seed(1)
        f <- psych::fa(x, nfactors = 3, fm = "minres",                # (1)
                       rotate = "oblimin")
        L <- unclass(f$loadings)
        list(f1 = L[1, 1], f2 = L[1, 2], f3 = L[1, 3], h2 = f$communality[1])
    """, ("a number of factors chosen by you: no parallel analysis (the seed is still set, for the oblimin rotation).",)),
    _explore_entry("test_method=", ', how_many=3, test_method="maximum likelihood"', """
        # find_hidden_factors_behind([...], how_many=3, test_method="maximum likelihood")
        x <- as.data.frame(x)
        set.seed(1)
        f <- psych::fa(x, nfactors = 3, fm = "ml",                    # (1)
                       rotate = "oblimin")
        L <- unclass(f$loadings)
        list(f1 = L[1, 1], f2 = L[1, 2], f3 = L[1, 3], h2 = f$communality[1])
    """, ("maximum likelihood, as base R factanal fits; \"principal axis\" is psych's fm = \"pa\".",)),
    _explore_entry("rotation=", ', how_many=3, rotation="varimax"', """
        # find_hidden_factors_behind([...], how_many=3, rotation="varimax")
        x <- as.data.frame(x)
        set.seed(1)
        f <- psych::fa(x, nfactors = 3, fm = "minres",
                       rotate = "varimax")                            # (1)
        L <- unclass(f$loadings)
        list(f1 = L[1, 1], f2 = L[1, 2], f3 = L[1, 3], h2 = f$communality[1])
    """, ("varimax (stats::varimax, as R factanal uses) keeps the factors uncorrelated; \"promax\" lets them "
          "correlate, \"none\" leaves them unrotated.",)),
    Entry(
        word="table.check_hidden_factors",
        data="ability_tests",
        ours=f"""
            table = sdata.get_example("ability_tests")
            table.check_hidden_factors(measured_by={MEASURED_BY})
        """,
        code={
            "R": """
                # check_hidden_factors(measured_by={"visual": [...], ...})
                d <- as.data.frame(x)
                colnames(d) <- paste0("x", 1:9)
                model <- "visual =~ x1 + x2 + x3
                          textual =~ x4 + x5 + x6
                          speed =~ x7 + x8 + x9"
                f <- lavaan::cfa(model, data = d, estimator = "ML")      # (1)
                m <- lavaan::fitMeasures(f)
                list(chisq = m[["chisq"]], df = m[["df"]], p = m[["pvalue"]])
            """,
            "Python": """
                {"estimate": chisq, "degrees of freedom": df, "p-value": p}
            """,
        },
        r_inputs=TESTS,
        r_packages=("lavaan",),
        compare="result",
        row="chi-square",
        fields=("estimate", "degrees of freedom", "p-value"),
        tolerance=1e-6,
        choices=("maximum likelihood; with empty cells simplydata adds missing = \"ml\", which uses every value "
                 "given, where lavaan's own default (\"listwise\") would leave those rows out without a word.",),
        python_note=CONFIRM_NOTE,
        also=CONFIRM_ALSO,
    ),
    Entry(
        word="table.check_hidden_factors",
        option="formula=",
        data="ability_tests",
        ours="""
            table = sdata.get_example("ability_tests")
            table.check_hidden_factors(formula="visual =~ x1 + x2 + x3; "
                                       "speed =~ x7 + x8 + x9; speed ~ visual")
        """,
        code={
            "R": """
                # check_hidden_factors(formula="visual =~ ...; speed ~ visual")
                d <- as.data.frame(x)
                colnames(d) <- paste0("x", 1:9)
                model <- "visual =~ x1 + x2 + x3
                          speed =~ x7 + x8 + x9
                          speed ~ visual"
                f <- lavaan::sem(model, data = d, estimator = "ML")      # (1)
                s <- lavaan::standardizedSolution(f)
                r <- s[s$op == "~", ]                                       # (2)
                list(b = r$est.std, se = r$se, p = r$pvalue)
            """,
            "Python": """
                {"estimate": b, "standard error": se, "p-value": p}
            """,
        },
        r_inputs=TESTS,
        r_packages=("lavaan",),
        compare="result",
        row="speed explained by visual",
        fields=("estimate", "standard error", "p-value"),
        tolerance=1e-6,
        choices=("formula= takes the model in lavaan's own syntax and runs lavaan::sem(), so hidden factors can "
                 "explain each other (a structural equation model).",
                 "the paths are shown standardised (both sides on a scale of standard deviations), as the loadings "
                 "are."),
        python_note=CONFIRM_NOTE,
        also=CONFIRM_ALSO,
    ),
]
