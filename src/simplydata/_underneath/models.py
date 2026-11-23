"""Model options (S3a): explain() with an option that changes what it calls underneath.

Each entry is one option of table.explain, keyed "table.explain weights=" and so on: the box shows the call
in statsmodels, SciPy, patsy or R that gives the numbers of one row of explain()'s result table. Where no
practice table fits (yes counts out of tries, matched sets), the box makes its own small table with pandas.
"""

from . import Entry

SENTENCE = "simplydata also writes each effect as a sentence with its interval and p-value, and names the method."
SEEDS = """\
seeds = pd.DataFrame({"extract": ["bean"] * 5 + ["cucumber"] * 6,
                      "germinated": [10, 23, 23, 26, 17, 5, 53, 55, 32, 46, 10],
                      "seeds": [39, 62, 81, 51, 39, 6, 74, 72, 51, 79, 13]})"""
PAIRS = """\
pairs = pd.DataFrame({"pair": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8],
                      "case": [1, 0] * 8,
                      "smoker": [1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0]})"""


MEADOW = """
    import pandas as pd
    df = pd.read_csv("meadow.csv")
    thistle = df["thistle"].to_numpy(dtype=float)
    grazed = df["grazed"].to_numpy(dtype=object)
    nettle = df["nettle"].to_numpy(dtype=float)
"""


def _indent(text: str, by: str = "            ") -> str:
    return "\n".join(by + line for line in text.splitlines())


ENTRIES = [
    Entry(
        word="table.explain", option="weights=",
        data="fruit",
        ours="""
            table = sdata.get_example("fruit")
            table.explain("price", using=["shop"], weights="count")
        """,
        code={"statsmodels": """
            import statsmodels.api as sm
            import pandas as pd
            df = pd.read_csv("fruit.csv")
            # explain("price", using=["shop"], weights="count")
            X = sm.add_constant((df["shop"] == "Market stall").astype(float))
            fit = sm.WLS(df["price"], X, weights=df["count"]).fit()     # (1)
            {"effect": fit.params.iloc[1], "standard error": fit.bse.iloc[1],
             "p-value": fit.pvalues.iloc[1]}
        """},
        compare="result", row="shop (Market stall)", fields=("effect", "standard error", "p-value"),
        tolerance=1e-9,
        choices=("precision weights, as R lm(weights =): statsmodels WLS; for the other outcomes GLM(var_weights=). "
                 "Not freq_weights, which would change the degrees of freedom.",),
        python_note="simplydata's standard errors of a least-squares fit are R's method, summary.lm()'s chol2inv() of "
                    "the QR factor, done with NumPy's QR and LAPACK's dpotri (approved by Manish 2026-11-22); "
                    "statsmodels' WLS above gives the same numbers here, to 1e-9.",
        also="Rows with weight 0 are left out first, as R does (statsmodels would count them in the degrees of "
             "freedom); negative weights are refused. " + SENTENCE,
    ),
    Entry(
        word="table.explain", option='outcome="yes or no (overdispersed)"',
        ours=f"""
            import pandas as pd
{_indent(SEEDS)}
            table = sdata.table(seeds)
            table.explain("germinated", using=["extract"], outcome="yes or no (overdispersed)", out_of="seeds")
        """,
        code={"statsmodels": f"""
            import pandas as pd
            import statsmodels.api as sm
{_indent(SEEDS)}
            # explain("germinated", using=["extract"], outcome="yes or no (overdispersed)", out_of="seeds")
            X = sm.add_constant((seeds["extract"] == "cucumber").astype(float))
            share = seeds["germinated"] / seeds["seeds"]
            fit = sm.GLM(share, X, family=sm.families.Binomial(),
                         var_weights=seeds["seeds"]).fit(scale="X2")   # (1)
            {{"log odds ratio": fit.params.iloc[1], "standard error": fit.bse.iloc[1]}}
        """},
        compare="result", row="extract (cucumber)", fields=("log odds ratio", "standard error"), tolerance=1e-8,
        choices=("quasi-binomial as R glm(family = quasibinomial): the shares, with the tries as var_weights and the "
                 "Pearson dispersion (scale=\"X2\"). A two-column endog would give statsmodels another dispersion.",),
        also="simplydata also gives t-based p-values with the residual degrees of freedom, as R summary(), and says "
             "that quasi-binomial has no AIC. The 11 plates are Crowder's (1978) Orobanche seeds. " + SENTENCE,
    ),
    Entry(
        word="table.explain", option="matched_by=",
        ours=f"""
            import pandas as pd
{_indent(PAIRS)}
            table = sdata.table(pairs)
            table.explain("case", using=["smoker"], outcome="yes or no", matched_by="pair")
        """,
        code={"statsmodels": f"""
            import pandas as pd
            from statsmodels.discrete.conditional_models import ConditionalLogit
{_indent(PAIRS)}
            # explain("case", using=["smoker"], outcome="yes or no", matched_by="pair")
            model = ConditionalLogit(pairs["case"], pairs[["smoker"]],
                                     groups=pairs["pair"])          # (1)
            fit = model.fit(method="newton", disp=0)                  # (2)
            {{"log odds ratio": fit.params.iloc[0], "standard error": fit.bse.iloc[0]}}
        """},
        compare="result", row="smoker", fields=("log odds ratio", "standard error"), tolerance=1e-6,
        choices=("conditional logistic regression with the exact conditional likelihood, as R survival::clogit() "
                 "(its default method = \"exact\"); no intercept, each pair compared only with itself.",
                 "fitted by Newton's method to the end; statsmodels' default (BFGS) stops a little short of the "
                 "best estimates.",),
        also="Pairs with no case or no control are left out first and counted (they add nothing); a column that "
             "does not change within any pair is refused. " + SENTENCE,
    ),
    Entry(
        word="table.explain", option='show="risk ratios"',
        data="clinic",
        ours="""
            table = sdata.get_example("clinic")
            table.explain("caught_infection", using=["ward", "patient_days"], outcome="yes or no",
                          show="risk ratios")
        """,
        code={"statsmodels": """
            import statsmodels.api as sm
            import pandas as pd
            df = pd.read_csv("clinic.csv")
            # explain("caught_infection", using=["ward", "patient_days"], outcome="yes or no", show="risk ratios")
            X = sm.add_constant(df[["patient_days"]].assign(b=(df["ward"] == "ward B") * 1.0))
            y = (df["caught_infection"] == "yes").astype(float)
            fit = sm.GLM(y, X, family=sm.families.Poisson()).fit(cov_type="HC0")   # (1)
            {"log risk ratio": fit.params.iloc[2], "standard error": fit.bse.iloc[2]}
        """},
        compare="result", row="ward (ward B)", fields=("log risk ratio", "standard error"), tolerance=1e-6,
        choices=("modified Poisson regression (Zou 2004): a Poisson model for the 0/1 column with robust (HC0) "
                 "standard errors, as R glm(family = poisson) with sandwich::vcovHC(type = \"HC0\"); it always "
                 "converges, where log-binomial (test_method=\"log-binomial\") often does not.",),
        also="simplydata also prints the risk ratios (exp of the effects) and their intervals, and leaves out the "
             "AIC: the Poisson model is used only for its ratios. " + SENTENCE,
    ),
    Entry(
        word="table.explain", option='test_method="log-binomial"',
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.explain("passed", using=["breakfast"], outcome="yes or no", show="risk ratios",
                          test_method="log-binomial")
        """,
        code={"statsmodels": """
            import statsmodels.api as sm
            import pandas as pd
            df = pd.read_csv("school.csv")
            # explain("passed", using=["breakfast"], outcome="yes or no", show="risk ratios", test_method="log-binomial")
            X = sm.add_constant((df["breakfast"] == "yes").astype(float))
            y = (df["passed"] == "yes").astype(float)
            log = sm.families.links.Log()
            fit = sm.GLM(y, X, family=sm.families.Binomial(link=log)).fit()   # (1)
            {"log risk ratio": fit.params.iloc[1], "standard error": fit.bse.iloc[1]}
        """},
        compare="result", row="breakfast (yes)", fields=("log risk ratio", "standard error"), tolerance=1e-6,
        choices=("a binomial model with a log link, as R glm(family = binomial(link = \"log\")); when it does not "
                 "converge (a predicted chance reaches 1), simplydata says so and points to the default modified "
                 "Poisson regression.",),
        also=SENTENCE,
    ),
    Entry(
        word="table.explain", option="giving_outliers_less_weight=",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.explain("marks", using=["hours"], giving_outliers_less_weight=True)
        """,
        code={"statsmodels": """
            import statsmodels.api as sm
            import pandas as pd
            df = pd.read_csv("marks.csv")
            # explain("marks", using=["hours"], giving_outliers_less_weight=True)
            X = sm.add_constant(df["hours"])
            huber = sm.robust.norms.HuberT()                          # (1)
            fit = sm.RLM(df["marks"], X, M=huber).fit(scale_est="mad", cov="H1",
                                                       maxiter=200, tol=1e-10)   # (2)
            {"effect": fit.params.iloc[1], "standard error": fit.bse.iloc[1],
             "p-value": fit.pvalues.iloc[1]}
        """},
        compare="result", row="hours", fields=("effect", "standard error", "p-value"), tolerance=1e-9,
        choices=("Huber's weights with k = 1.345, the default of statsmodels and of R MASS::rlm().",
                 "the scale by the median absolute deviation and Huber's H1 covariance; R's summary(rlm) uses a "
                 "slightly different small-sample correction, so its standard errors differ in the third digit.",),
        also="simplydata also lists the rows given less weight, by their row number, and names "
             "show_rows_that_pull_model() for unusual values in the using= columns, which Huber's method does not "
             "resist. " + SENTENCE,
    ),
    Entry(
        word="table.explain", option="with_knots=",
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.explain("marks", using=["hours", "breakfast"], curve_for="hours", with_knots=3)
        """,
        code={"patsy and statsmodels": """
            import numpy as np
            import statsmodels.api as sm
            from patsy import dmatrix
            import pandas as pd
            df = pd.read_csv("school.csv")
            # explain("marks", using=["hours", "breakfast"], curve_for="hours", with_knots=3)
            knots = np.quantile(df["hours"], [0.25, 0.5, 0.75])               # (1)
            curve = dmatrix("cr(hours, knots=knots, constraints='center') - 1", df)   # (2)
            X = sm.add_constant(np.column_stack([curve, df["breakfast"] == "yes"]))
            fit = sm.OLS(df["marks"], X.astype(float)).fit()
            {"effect": fit.params.iloc[-1], "standard error": fit.bse.iloc[-1]}
        """},
        compare="result", row="breakfast (yes)", fields=("effect", "standard error"), tolerance=1e-9,
        choices=("the knots at the quantiles of all the values, as R splines::ns() places them; patsy's own df= "
                 "would take the quantiles of the distinct values (mgcv's rule) and give another curve.",
                 "a natural cubic spline without its constant (constraints=\"center\"): the same curves as R "
                 "lm(marks ~ splines::ns(hours, df = 4) + breakfast), so the fitted values and the other effects "
                 "are R's.",),
        also="simplydata also tests the whole curve (is it flat?) with an F test, and leaves the spline's own "
             "numbers out of the printout: they depend on the basis and mean little. " + SENTENCE,
    ),
    Entry(
        word="table.explain", option='show="standardised effects"',
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.explain("marks", using=["hours", "breakfast"], show="standardised effects")
        """,
        code={"statsmodels": """
            import statsmodels.api as sm
            import pandas as pd
            df = pd.read_csv("school.csv")
            # explain("marks", using=["hours", "breakfast"], show="standardised effects")
            def z(v):
                return (v - v.mean()) / v.std()                       # (1)
            X = sm.add_constant(df[["hours"]].apply(z).assign(b=(df["breakfast"] == "yes") * 1.0))
            fit = sm.OLS(z(df["marks"]), X).fit()                     # (2)
            {"effect": fit.params.iloc[1], "standard error": fit.bse.iloc[1]}
        """},
        compare="result", row="hours", fields=("effect", "standard error"), tolerance=1e-9,
        choices=("z-scores with the standard deviation of n - 1 (pandas' std(), R's sd()), on the rows the model "
                 "uses.",
                 "the model fitted again on the z-scores, as R effectsize::standardize_parameters(method = "
                 "\"refit\"); group columns stay as they are, and the outcome is standardised only for numbers.",),
        also="simplydata also prints what one standard deviation is in each column and the warning that "
             "standardised effects depend on the sample's spread (Greenland et al. 1986). " + SENTENCE,
    ),
    Entry(
        word="table.explain", option='interval_by="bootstrap"',
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.explain("marks", using=["hours"], interval_by="bootstrap", resamples=999, with_seed=1)
        """,
        code={"SciPy and statsmodels": """
            import numpy as np
            import statsmodels.api as sm
            from scipy import stats
            import pandas as pd
            df = pd.read_csv("marks.csv")
            # explain("marks", using=["hours"], interval_by="bootstrap", resamples=999, with_seed=1)
            X, y = sm.add_constant(df["hours"]).to_numpy(), df["marks"].to_numpy()
            def refit(rows):                                          # (1)
                return sm.OLS(y[rows], X[rows]).fit().params
            res = stats.bootstrap((np.arange(len(y)),), refit, n_resamples=999, method="BCa",
                                  vectorized=False, rng=np.random.default_rng(1))   # (2)
            {"95 % CI low": res.confidence_interval.low[1], "95 % CI high": res.confidence_interval.high[1]}
        """},
        compare="result", row="hours", fields=("95 % CI low", "95 % CI high"), tolerance=1e-9,
        choices=("the rows are drawn again whole (case resampling), and the same model is fitted to each new "
                 "table.",
                 "BCa intervals (bias-corrected and accelerated), as R boot::boot.ci(type = \"bca\"); with_seed= "
                 "fixes the random draws.",),
        also="The p-values stay the model's usual ones; simplydata says so, and how many times the rows were "
             "drawn. " + SENTENCE,
    ),
    Entry(
        word="table.explain", option='interval_by="profile"',
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.explain("passed", using=["hours"], outcome="yes or no", interval_by="profile")
        """,
        code={
            "R": """
                # explain("passed", using=["hours"], outcome="yes or no", interval_by="profile")
                # passed (1 = yes) and hours: two columns of sdata.get_example("school")
                m <- stats::glm(passed ~ hours, family = stats::binomial)
                ci <- stats::confint(m)                             # (1)
                list(low = ci[2, 1], high = ci[2, 2])
            """,
            "Python": """
                import math
                {"95 % CI low": math.exp(low), "95 % CI high": math.exp(high)}   # odds ratios
            """,
        },
        r_inputs="""
            import pandas as pd
            school = pd.read_csv("school.csv")
            passed = (school["passed"] == "yes").to_numpy(dtype=float)
            hours = school["hours"].to_numpy(dtype=float)
        """,
        r_packages=(),  # base R (stats) only
        compare="result", row="hours", fields=("95 % CI low", "95 % CI high"), tolerance=1e-7,
        choices=("profile-likelihood intervals, R's confint() of a glm (in stats since R 4.4; before, in MASS); "
                 "safer than Wald intervals with few rows or effects far from 1.",),
        python_note="statsmodels gives Wald intervals only, so the profile intervals come from R.",
        also="The p-values stay the usual ones. " + SENTENCE,
    ),
    Entry(
        word="table.explain", option='p_value_by="likelihood ratio"',
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.explain("passed", using=["hours", "breakfast"], outcome="yes or no",
                          p_value_by="likelihood ratio")
        """,
        code={"statsmodels and SciPy": """
            import statsmodels.api as sm
            from scipy import stats
            import pandas as pd
            df = pd.read_csv("school.csv")
            # explain("passed", using=["hours", "breakfast"], outcome="yes or no", p_value_by="likelihood ratio")
            y = (df["passed"] == "yes").astype(float)
            X = sm.add_constant(df[["hours"]].assign(b=(df["breakfast"] == "yes") * 1.0))
            full = sm.GLM(y, X, family=sm.families.Binomial()).fit()
            small = sm.GLM(y, X.drop(columns="hours"), family=sm.families.Binomial()).fit()   # (1)
            {"p-value": stats.chi2.sf(small.deviance - full.deviance, 1)}
        """},
        compare="result", row="hours", fields=("p-value",), tolerance=1e-8,
        choices=("each column left out in turn and the deviances compared (chi-square, 1 df), as R drop1(m, test = "
                 "\"LRT\"); a group column is tested whole, and a column inside an interaction is not tested alone.",),
        also=SENTENCE,
    ),
    Entry(
        word="table.explain", option="crossed_with=",
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.explain("marks", using=["hours"], grouped_by="school", crossed_with="class")
        """,
        code={
            "R": """
                # explain("marks", using=["hours"], grouped_by="school", crossed_with="class")
                # marks, hours, school and class: four columns of sdata.get_example("school")
                m <- lme4::lmer(marks ~ hours + (1 | school) + (1 | class_))   # (1)
                list(b = lme4::fixef(m)[2], se = sqrt(diag(as.matrix(vcov(m))))[2])
            """,
            "Python": """
                {"effect": b, "standard error": se}
            """,
        },
        r_inputs="""
            import pandas as pd
            df = pd.read_csv("school.csv")
            marks = df["marks"].to_numpy(dtype=float)
            hours = df["hours"].to_numpy(dtype=float)
            school = df["school"].to_numpy(dtype=object)
            class_ = df["class"].to_numpy(dtype=object)  # "class" is a word R keeps for itself
        """,
        r_packages=("lme4",),
        compare="result", row="hours", fields=("effect", "standard error"), tolerance=1e-6,
        choices=("two groupings crossed with each other, (1 | school) + (1 | class), fitted by REML as lme4's "
                 "default; statsmodels MixedLM takes one grouping (or groups inside groups), so R fits it.",),
        python_note="statsmodels MixedLM fits one grouping or groups inside groups, not two crossed ones.",
        also="simplydata also prints the variance of each grouping and of the rows, the share of each, and a note "
             "for a grouping with fewer than 5 groups. " + SENTENCE,
    ),
    Entry(
        word="table.explain", option='outcome="counts with many zeros that vary a lot"',
        data="meadow",
        ours="""
            table = sdata.get_example("meadow")
            table.explain("thistle", using=["grazed", "nettle"], outcome="counts with many zeros that vary a lot")
        """,
        code={
            "R": """
                # explain("thistle", using=["grazed", "nettle"], outcome="counts with many zeros that vary a lot")
                # thistle, grazed and nettle: three columns of sdata.get_example("meadow")
                z <- pscl::zeroinfl(thistle ~ grazed + nettle, dist = "negbin")   # (1)
                list(b = coef(z, model = "count")[2], se = sqrt(diag(vcov(z)))[2])
            """,
            "Python": """
                {"log ratio": b, "standard error": se}
            """,
        },
        r_inputs=MEADOW,
        r_packages=("pscl",),
        compare="result", row="grazed (yes)", fields=("log ratio", "standard error"), tolerance=1e-9,
        choices=("zero-inflated negative binomial regression with a logistic zero part and the same columns in "
                 "both parts, pscl::zeroinfl(dist = \"negbin\")'s defaults.",),
        python_note="statsmodels ZeroInflatedNegativeBinomialP gives the same estimates but other standard errors.",
        also="The row compared is the count part; simplydata prints both parts in two blocks, and theta in words. "
             + SENTENCE,
    ),
    Entry(
        word="table.explain", option='outcome="counts in two steps"',
        data="meadow",
        ours="""
            table = sdata.get_example("meadow")
            table.explain("thistle", using=["grazed", "nettle"], outcome="counts in two steps")
        """,
        code={
            "R": """
                # explain("thistle", using=["grazed", "nettle"], outcome="counts in two steps")
                # thistle, grazed and nettle: three columns of sdata.get_example("meadow")
                h <- pscl::hurdle(thistle ~ grazed + nettle, dist = "poisson",
                                  zero.dist = "binomial")                 # (1)
                list(b = coef(h, model = "count")[2], se = sqrt(diag(vcov(h)))[2])
            """,
            "Python": """
                {"log ratio": b, "standard error": se}
            """,
        },
        r_inputs=MEADOW,
        r_packages=("pscl",),
        compare="result", row="grazed (yes)", fields=("log ratio", "standard error"), tolerance=1e-9,
        choices=("a hurdle model: a logistic part for zero or not (pscl's binomial zero part, the textbook form) "
                 "and a Poisson part cut off at 1 for the counts above 0.",),
        python_note="statsmodels HurdleCountModel has no logistic zero part (its default zero part is Poisson).",
        also="The row compared is the second step (how many, when not zero); simplydata prints both steps in two "
             "blocks. " + SENTENCE,
    ),
    Entry(
        word="table.explain", option="zero_part_using=",
        data="meadow",
        ours="""
            table = sdata.get_example("meadow")
            table.explain("thistle", using=["grazed", "nettle"], outcome="counts with many zeros",
                          zero_part_using=["grazed"])
        """,
        code={
            "R": """
                # explain("thistle", using=["grazed", "nettle"], outcome="counts with many zeros", zero_part_using=["grazed"])
                # thistle, grazed and nettle: three columns of sdata.get_example("meadow")
                z <- pscl::zeroinfl(thistle ~ grazed + nettle | grazed,
                                    dist = "poisson")                     # (1)
                list(b = coef(z, model = "count")[2], se = sqrt(diag(vcov(z)))[2])
            """,
            "Python": """
                {"log ratio": b, "standard error": se}
            """,
        },
        r_inputs=MEADOW,
        r_packages=("pscl",),
        compare="result", row="grazed (yes)", fields=("log ratio", "standard error"), tolerance=1e-9,
        choices=("the zero part gets its own columns, pscl's y ~ x | z; without zero_part_using= both parts use "
                 "the columns of using=.",),
        python_note="statsmodels ZeroInflatedPoisson takes exog_infl= for the zero part too, with other standard "
                    "errors.",
        also=SENTENCE,
    ),
]
