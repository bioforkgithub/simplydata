"""Small additions to known words (phase S3c-4): one entry for each new option or value that changes what a word calls
(keyed by word and option): weighted percentiles and medians, the covariance table, the automatic ARIMA order,
Storey's q-values and the local false discovery rate, Nemenyi's and Conover's tests after Friedman's, and pairwise
comparisons of percents. Practice tables: "fruit", "marks", "visitors", "many_tests" (made up), "clinic".
"""

from . import Entry

PAIN = """
    df = sdata.get_example("clinic").melt(id_vars="patient", value_vars=["pain_week_0", "pain_week_4", "pain_week_8"],
                                          var_name="week", value_name="pain")
    y = df["pain"].to_numpy(dtype=float)
    g = df["week"].to_numpy(dtype=str)
    b = df["patient"].to_numpy(dtype=str)
"""
PAIN_OURS = """
    table = sdata.table(sdata.get_example("clinic"))
    table.turn_columns_into_rows(["pain_week_0", "pain_week_4", "pain_week_8"], names_to="week", values_to="pain")
"""
PAIN_PAIRS = '    table.compare_each_pair_of("pain", for_each_group_in="week", matched_by="patient", test_method="{test}")\n'
MANY = """
    df = sdata.get_example("many_tests")
    p = df["p-value"].to_numpy(dtype=float)
"""
QVALUE_NOTE = ("No Python package gives Storey's pi0 with qvalue's smoother (statsmodels fdrcorrection_twostage is "
               "another estimator), so the numbers come from R qvalue (Bioconductor).")
PMCMR_NOTE = ("scikit-posthocs gives Nemenyi's and Conover's tests in Python, but it is not a simplydata dependency, so "
              "the numbers come from R PMCMRplus.")

ENTRIES = [
    # ------------------------------------------------------------------ A14: weighted percentiles
    Entry(
        word="table.find_percentile_of", option="weights=",
        data="fruit",
        ours="""
            table = sdata.table(sdata.get_example("fruit"))
            table.find_percentile_of("price", 90, weights="count")
        """,
        code={"NumPy": """
            import numpy as np
            df = sdata.get_example("fruit")
            # find_percentile_of("price", 90, weights="count")
            rows = np.repeat(df["price"].to_numpy(), df["count"].to_numpy())   # (1)
            np.percentile(rows, 90)                                           # (2)
        """},
        compare="value", tolerance=1e-12,
        choices=("frequency weights: each row repeated as often as its weight, so weights of 1 change nothing (as R "
                 "quantile(rep(x, w)) and Hmisc::wtd.quantile).",
                 "the linear rule (R type 7), the same test_method= as without weights."),
        also="simplydata also refuses weights that are not whole numbers (and points to weight_kind=\"analytic\"), "
             "negative weights and more than 10 million repeated rows, and skips rows with an empty cell, with a note.",
    ),
    Entry(
        word="table.find_percentile_of", option='weight_kind="analytic"',
        data="fruit",
        ours="""
            table = sdata.table(sdata.get_example("fruit"))
            table.find_percentile_of("price", 90, weights="count", weight_kind="analytic")
        """,
        code={"NumPy": """
            import numpy as np
            df = sdata.get_example("fruit")
            # find_percentile_of("price", 90, weights="count", weight_kind="analytic")
            np.percentile(df["price"], 90, weights=df["count"],
                          method="inverted_cdf")                              # (1)
        """},
        compare="value", tolerance=1e-12,
        choices=("the weighted inverted CDF, the only NumPy rule with weights (as R survey::svyquantile(qrule = "
                 "\"math\")): a step, not a line between values.",),
        also="simplydata also refuses test_method= with analytic weights (no other rule takes weights) and NumPy older "
             "than 2.0.",
    ),
    Entry(
        word="table.find_median_of", option="weights=",
        data="fruit",
        ours="""
            table = sdata.table(sdata.get_example("fruit"))
            table.find_median_of("price", weights="count")
        """,
        code={"NumPy": """
            import numpy as np
            df = sdata.get_example("fruit")
            # find_median_of("price", weights="count")
            rows = np.repeat(df["price"].to_numpy(), df["count"].to_numpy())   # (1)
            np.median(rows)
        """},
        compare="value", tolerance=1e-12,
        choices=("frequency weights: each row repeated as often as its weight (weight_kind=\"analytic\" gives the "
                 "weighted inverted CDF instead).",),
        also="As find_percentile_of(weights=).",
    ),
    # ------------------------------------------------------------------ A25: covariance matrix
    Entry(
        word="table.find_correlation_between", option='show="covariance"',
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.find_correlation_between("hours", "marks", "height", show="covariance")
        """,
        code={"pandas": """
            df = sdata.get_example("marks")
            # find_correlation_between("hours", "marks", "height", show="covariance")
            cov = df[["hours", "marks", "height"]].cov(ddof=1)   # (1)
            cov.rename_axis("column").reset_index()
        """},
        compare="table", tolerance=1e-12,
        choices=("divide by n - 1, each pair on the rows where both columns have a number (as R cov(use = "
                 "\"pairwise.complete.obs\"); R's default gives NA with an empty cell, and NumPy cov reads rows as "
                 "the variables).",),
        also="simplydata also says that a covariance is in the units of the two columns multiplied and that the "
             "correlation is the same link without units.",
    ),
    # ------------------------------------------------------------------ AA11: automatic ARIMA order
    Entry(
        word="table.forecast", option='order="automatic"',
        data="visitors",
        ours="""
            table = sdata.table(sdata.get_example("visitors"))
            table.forecast("visitors", sorted_by="month", test_method="arima", order="automatic", repeats_every=12,
                           for_each_group_in="museum")
        """,
        code={
            "R": """
                # forecast("visitors", test_method="arima", order="automatic", repeats_every=12), first museum
                fit <- forecast::auto.arima(stats::ts(x, frequency = 12),
                                            stepwise = FALSE, approximation = FALSE)   # (1)
                f <- forecast::forecast(fit, h = 12, level = 95)
                list(mean = f$mean[1], low = f$lower[1], high = f$upper[1])
            """,
            "Python": """
                {"forecast": mean, "forecast 95 % prediction low": low, "forecast 95 % prediction high": high}
            """,
        },
        r_inputs="""
            df = sdata.get_example("visitors").sort_values("month")
            x = df[df["museum"] == "Harbour Museum"]["visitors"].to_numpy(dtype=float)
        """,
        r_packages=("forecast",), compare="result",
        fields=("forecast", "forecast 95 % prediction low", "forecast 95 % prediction high"), tolerance=1e-9,
        choices=("every order is tried (stepwise = FALSE, approximation = FALSE) for series of up to 1,000 readings; "
                 "auto.arima's own quicker defaults can choose another order on long or seasonal series.",),
        python_note="statsmodels has no automatic order search (pmdarima, which has one, is not a simplydata "
                    "dependency), so the order and the numbers come from R forecast::auto.arima (Hyndman & "
                    "Khandakar 2008).",
        also="simplydata also prints the order chosen (and both orders with a season), says the intervals are a "
             "little too narrow because the order was chosen from the data, refuses seasonal_order= with "
             "order=\"automatic\", and checks the leftover errors (Ljung-Box).",
    ),
    # ------------------------------------------------------------------ G03: q-values and local FDR
    Entry(
        word="table.add_adjusted_p_value_column", option='test_method="storey"',
        data="many_tests",
        ours="""
            table = sdata.table(sdata.get_example("many_tests"))
            table.add_adjusted_p_value_column(test_method="storey")
        """,
        code={
            "R": """
                # add_adjusted_p_value_column(test_method="storey")
                q <- qvalue::qvalue(p)   # (1)
                list(q = q$qvalues)
            """,
            "Python": """
                df = sdata.get_example("many_tests")
                df["p-value (Storey q-value)"] = q
                df
            """,
        },
        r_inputs=MANY, r_packages=("qvalue",), compare="table", tolerance=1e-9,
        choices=("qvalue's own defaults: the share of true nulls (pi0) estimated by the smoother over lambda = 0.05 "
                 "to 0.95 (Storey & Tibshirani 2003), not set to 1 as in Benjamini-Hochberg.",),
        python_note=QVALUE_NOTE,
        also="simplydata also prints pi0 in words, names Benjamini-Hochberg as the same idea with pi0 = 1, notes "
             "fewer than 100 p-values, and refuses with a sentence when qvalue cannot estimate pi0.",
    ),
    Entry(
        word="table.add_adjusted_p_value_column", option='test_method="local fdr"',
        data="many_tests",
        ours="""
            table = sdata.table(sdata.get_example("many_tests"))
            table.add_adjusted_p_value_column(test_method="local fdr")
        """,
        code={
            "R": """
                # add_adjusted_p_value_column(test_method="local fdr")
                q <- qvalue::qvalue(p)   # (1)
                list(lfdr = q$lfdr)
            """,
            "Python": """
                df = sdata.get_example("many_tests")
                df["local false discovery rate"] = lfdr
                df
            """,
        },
        r_inputs=MANY, r_packages=("qvalue",), compare="table", tolerance=1e-9,
        choices=("qvalue's local false discovery rate with its defaults (pi0 from the smoother), in a column named "
                 "\"local false discovery rate\", not \"adjusted p\": it belongs to one test.",),
        python_note=QVALUE_NOTE,
        also="As test_method=\"storey\".",
    ),
    # ------------------------------------------------------------------ G09: Nemenyi and Conover after Friedman
    Entry(
        word="table.compare_each_pair_of", option='matched_by=, test_method="nemenyi"',
        data="clinic",
        ours=PAIN_OURS + PAIN_PAIRS.format(test="nemenyi"),
        code={
            "R": """
                # compare_each_pair_of("pain", for_each_group_in="week", matched_by="patient", test_method="nemenyi")
                r <- PMCMRplus::frdAllPairsNemenyiTest(y, factor(g), factor(b))   # (1)
                list(p = r$p.value[1, 1], q = r$statistic[1, 1])
            """,
            "Python": """
                {"statistic": q, "p-value (adjusted)": p}
            """,
        },
        r_inputs=PAIN, r_packages=("PMCMRplus",), compare="result", fields=("statistic", "p-value (adjusted)"),
        tolerance=1e-9,
        choices=("Nemenyi's test allows for all the pairs itself (the studentized range): no Holm on top, and the "
                 "printout says not to adjust again.",),
        python_note=PMCMR_NOTE,
        also="simplydata also keeps only the patients measured in every week (with a note), refuses fewer than 3 "
             "groups, and notes that mean-rank tests depend on the other groups in the study (Benavoli et al. 2016).",
    ),
    Entry(
        word="table.compare_each_pair_of", option='matched_by=, test_method="conover"',
        data="clinic",
        ours=PAIN_OURS + PAIN_PAIRS.format(test="conover"),
        code={
            "R": """
                # compare_each_pair_of("pain", for_each_group_in="week", matched_by="patient", test_method="conover")
                r <- PMCMRplus::frdAllPairsConoverTest(y, factor(g), factor(b),
                                                      p.adjust.method = "holm")    # (1)
                list(p = r$p.value[1, 1], q = r$statistic[1, 1])
            """,
            "Python": """
                {"statistic": q, "p-value (adjusted)": p}
            """,
        },
        r_inputs=PAIN, r_packages=("PMCMRplus",), compare="result", fields=("statistic", "p-value (adjusted)"),
        tolerance=1e-9,
        choices=("Holm's adjustment, as for Conover's test after Kruskal-Wallis; PMCMRplus's own default is "
                 "\"single-step\" and scikit-posthocs adjusts nothing, so their numbers differ.",),
        python_note=PMCMR_NOTE,
        also="As test_method=\"nemenyi\".",
    ),
    # ------------------------------------------------------------------ D13: pairwise comparisons of percents
    Entry(
        word="table.compare_each_pair_of", option='based_on="percents"',
        data="clinic",
        ours="""
            table = sdata.table(sdata.get_example("clinic"))
            table.compare_each_pair_of("infected", for_each_group_in="age_group", based_on="percents", value="yes")
        """,
        code={"SciPy and statsmodels": """
            import pandas as pd
            from scipy import stats
            from statsmodels.stats.multitest import multipletests
            df = sdata.get_example("clinic")
            # compare_each_pair_of("infected", for_each_group_in="age_group", based_on="percents", value="yes")
            t = pd.crosstab(df["age_group"], df["infected"] == "yes").to_numpy()
            pairs = [(i, j) for i in range(len(t)) for j in range(i + 1, len(t))]
            p = [stats.chi2_contingency(t[[i, j]], correction=True).pvalue      # (1)
                 for i, j in pairs]
            {"p-value": p[0], "p-value (Holm)": multipletests(p, method="holm")[1][0]}   # (2)
        """},
        compare="result", fields=("p-value", "p-value (Holm)"), tolerance=1e-9,
        choices=("each pair gets the 2 x 2 chi-square test with Yates' correction that compare_counts_of uses (the "
                 "default of R prop.test and pairwise.prop.test); test_method=\"fisher\" gives Fisher's exact test.",
                 "Holm's adjustment for the number of pairs, as R pairwise.prop.test()."),
        also="simplydata also gives each pair's difference in percentage points with Newcombe's interval "
             "(statsmodels, as compare_risks), notes expected counts below 5, and leaves a pair with no p-value out "
             "of Holm's adjustment.",
    ),
]
