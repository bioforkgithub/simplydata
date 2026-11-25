"""Words and options added on 2026-11-21 (PR words-and-fixes): chart.get_numbers_drawn(), table.repeat_each_row_by(),
the table that show_rows_that_pull_model() gives back, check_model_of(show="numbers"),
sdata.get_example(from_r_package=) and find_correlation_between(show="result table"); 2026-11-23 (branch three-words):
find_correlation_between(allowing_for=, show="result table") and the best cut-off of trade_off_curve read with
get_numbers_drawn().
"""

from . import Entry

ENTRIES = [
    Entry(
        word="get_numbers_drawn",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
            drawn = chart.get_numbers_drawn()
            drawn.keep_columns("x", "y")
        """,
        code={"matplotlib": """
            import matplotlib.pyplot as plt
            import pandas as pd
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            ax.scatter(df["hours"], df["marks"])
            # get_numbers_drawn(): what matplotlib keeps of the drawn dots
            xy = ax.collections[0].get_offsets()
            pd.DataFrame({"x": xy[:, 0], "y": xy[:, 1]})
        """},
        compare="table",
        also="simplydata reads every layer the same way (Line2D.get_xydata for lines, the bars of each "
             "BarContainer, the segments of stems and error bars, the edges of fill_between bands, heat map cells, "
             "pie slices), gives dates and group names back on date and group axes, numbers the layers and panels, "
             "and names each layer after its legend entry.",
    ),
    Entry(
        word="table.repeat_each_row_by",
        ours="""
            table = sdata.table({"answer": ["yes", "no", "maybe"], "count": [3, 2, 0]})
            table.repeat_each_row_by("count")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.DataFrame({"answer": ["yes", "no", "maybe"], "count": [3, 2, 0]})
                # repeat_each_row_by("count")
                df.loc[df.index.repeat(df["count"])].drop(columns="count").reset_index(drop=True)
            """,
            "Polars": """
                import polars as pl
                df = pl.DataFrame({"answer": ["yes", "no", "maybe"], "count": [3, 2, 0]})
                # repeat_each_row_by("count")
                rows = pl.int_range(pl.len()).repeat_by("count").explode().drop_nulls()
                df.select(pl.exclude("count").gather(rows))
            """,
        },
        compare="table",
        also="simplydata also refuses counts that are not whole numbers, are below 0 or are empty, says how many rows "
             "it made, and keeps the table before the step (undo).",
    ),
    Entry(
        word="table.show_rows_that_pull_model",
        data="school",
        ours="""
            table = sdata.get_example("school")
            found = table.show_rows_that_pull_model("marks", using=["hours", "sleep"])
            found.keep_columns("row", "Cook's distance", "leverage")
        """,
        code={"statsmodels": """
            import numpy as np
            import pandas as pd
            import statsmodels.api as sm
            from statsmodels.stats.outliers_influence import OLSInfluence
            df = pd.read_csv("school.csv").dropna(subset=["marks", "hours", "sleep"])
            # show_rows_that_pull_model("marks", using=["hours", "sleep"])
            fit = sm.OLS(df["marks"], sm.add_constant(df[["hours", "sleep"]])).fit()
            influence = OLSInfluence(fit)
            cooks, hat = np.asarray(influence.cooks_distance[0]), np.asarray(influence.hat_matrix_diag)
            above = [i for i in np.argsort(-cooks, kind="stable") if cooks[i] > 4 / len(df)]   # (1)
            pd.DataFrame({"row": df.index.to_numpy()[above] + 1, "Cook's distance": cooks[above],
                          "leverage": hat[above]})
        """},
        compare="table",
        choices=("rows with a Cook's distance above 4 / (number of rows), a rule of thumb (Bollen & Jackman 1985), "
                 "biggest first, numbered from 1 in the whole table (empty cells included).",),
        also="simplydata also prints the ten biggest with their values and studentised residual (rstudent), says "
             "which rows pull very strongly (Cook's distance above 1), and with grouped_by= checks whole groups "
             "(R lme4 influence()).",
    ),
    Entry(
        word="sdata.get_example",
        option="from_r_package=",
        ours="""
            lung = sdata.get_example("lung", from_r_package="survival")
            lung
        """,
        code={
            "R": """
                # get_example("lung", from_r_package="survival")
                e <- new.env()
                utils::data(list = "cancer", package = "survival", envir = e)   # (1)
                lung <- e$lung
                list(time = lung$time[1], status = lung$status[1], age = lung$age[1], loss = lung$wt.loss[1])
            """,
            "Python": """
                {"time": time, "status": status, "age": age, "wt.loss": loss}
            """,
        },
        compare="result",
        fields=("time", "status", "age", "wt.loss"),
        r_inputs="pass  # nothing from Python: R loads the dataset itself",
        r_packages=("survival",),
        ours_r=("survival",),
        choices=("R itself loads the dataset (utils::data, from the data file that holds it: lung is kept in "
                 "\"cancer\"); groups (factors) become text and R's NA empty cells; row names that carry information "
                 "become a first column \"row name\".",),
        also="simplydata also checks that the package is installed and has that dataset (suggesting the nearest "
             "name), never downloads or installs anything, and lists the R package for sdata.show_packages_used().",
        python_note="Python has no copy of the R packages' datasets; statsmodels.datasets.get_rdataset() downloads "
                    "them from the internet, which simplydata never does.",
    ),
    Entry(
        word="table.check_model_of",
        option='show="numbers"',
        data="school",
        ours="""
            table = sdata.get_example("school")
            numbers = table.check_model_of("marks", using=["hours", "sleep"], show="numbers")
            numbers.keep_rows_where("check", is_equal_to="Breusch-Pagan test (chi-square)")
        """,
        code={"statsmodels": """
            import statsmodels.api as sm
            from statsmodels.stats.diagnostic import het_breuschpagan
            import pandas as pd
            df = pd.read_csv("school.csv").dropna(subset=["marks", "hours", "sleep"])
            # check_model_of("marks", using=["hours", "sleep"], show="numbers"): the Breusch-Pagan row
            X = sm.add_constant(df[["hours", "sleep"]])
            fit = sm.OLS(df["marks"], X).fit()
            bp, p, _, _ = het_breuschpagan(fit.resid, X, robust=True)     # (1)
            {"value": bp, "df": X.shape[1] - 1, "p-value": p}
        """},
        compare="result",
        fields=("value", "df", "p-value"),
        tolerance=1e-9,
        choices=("Koenker's studentised Breusch-Pagan test (robust=True, as R lmtest::bptest's default), which does "
                 "not assume bell-shaped errors.",),
        also="The table holds every number check_model_of prints: the variance inflation factors (statsmodels, or "
             "R car::vif), White's test, the Brier score and Hosmer-Lemeshow test for yes or no, and the rows with a "
             "Cook's distance above 0.5; with test_method=\"bayesian\", R-hat and effective draws and the posterior "
             "predictive check from R.",
    ),
    Entry(
        word="table.find_correlation_between",
        option='show="result table"',
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_rows_where("subject", is_equal_to="Maths")
            table.find_correlation_between("hours", "marks", show="result table")
        """,
        code={"SciPy": """
            from scipy import stats
            import pandas as pd
            df = pd.read_csv("marks.csv")
            df = df[df["subject"] == "Maths"].reset_index(drop=True)   # one row per child
            # find_correlation_between("hours", "marks", show="result table")
            res = stats.pearsonr(df["hours"], df["marks"])
            ci = res.confidence_interval(0.95)                 # (1)
            {"r": res.statistic, "95 % CI low": ci.low, "95 % CI high": ci.high, "p-value": res.pvalue,
             "rows": len(df)}
        """},
        compare="result",
        fields=("r", "95 % CI low", "95 % CI high", "p-value", "rows"),
        tolerance=1e-9,
        choices=("the 95 % interval of Pearson's r from Fisher's z, as SciPy pearsonr and R cor.test.",),
        also="With p_value_by=\"shuffling\" or interval_by=\"bootstrap\" the table holds those (SciPy "
             "permutation_test, bootstrap) and says so; Spearman's and Kendall's intervals come from R DescTools. "
             "With three or more columns the result table is the table of show=\"each pair\".",
    ),
    # 2026-11-23 (branch three-words)
    Entry(
        word="table.find_correlation_between",
        option='allowing_for=, show="result table"',
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_rows_where("subject", is_equal_to="Maths")
            table.find_correlation_between("hours", "marks", allowing_for="height", show="result table")
        """,
        code={
            "R": """
                # find_correlation_between("hours", "marks", allowing_for="height", show="result table")
                p <- ppcor::pcor.test(hours, marks, height, method = "pearson")      # (1)
                list(r = p$estimate, statistic = p$statistic, p = p$p.value, rows = p$n)
            """,
            "Python": """
                {"r": r, "statistic": statistic, "p-value": p, "rows": rows}
            """,
        },
        r_inputs="""
            import pandas as pd
            df = pd.read_csv("marks.csv").dropna(subset=["hours", "marks", "height"])
            df = df[df["subject"] == "Maths"].reset_index(drop=True)   # one row per child
            hours = df["hours"].to_numpy(dtype=float)
            marks = df["marks"].to_numpy(dtype=float)
            height = df["height"].to_numpy(dtype=float)
        """,
        r_packages=("ppcor",), compare="result", fields=("r", "statistic", "p-value", "rows"), tolerance=1e-9,
        choices=("the partial correlation of R ppcor::pcor.test(): the link left after taking out what both columns "
                 "share with the third; its statistic is t (z for Kendall) and it gives no interval.",),
        python_note="SciPy and statsmodels have no partial correlation test, so the numbers come from R ppcor.",
        also="simplydata also prints the correlation without allowing for the third column, on the same rows, and "
             "says the strength in words.",
    ),
    Entry(
        word="draw_trade_off_curve",
        option="get_numbers_drawn()",
        data="clinic",
        ours="""
            chart = sdata.chart(sdata.get_example("clinic"))
            chart.draw_trade_off_curve(score="crp", truth="infected")
            drawn = chart.get_numbers_drawn()
            drawn.keep_rows_where("kind", is_equal_to="dot")
        """,
        code={
            "R": """
                # draw_trade_off_curve(score="crp", truth="infected"), then get_numbers_drawn():
                # the marked dot's row
                r <- pROC::roc(infected, crp, levels = c(0, 1),
                               direction = "<", quiet = TRUE)
                b <- pROC::coords(r, "best", best.method = "youden",         # (1)
                                  ret = c("threshold", "sensitivity"), transpose = FALSE)
                list(cut = b$threshold[1], se = b$sensitivity[1])
            """,
            "Python": """
                {"value": cut, "y": se}
            """,
        },
        r_inputs="""
            import pandas as pd
            clinic = pd.read_csv("clinic.csv").dropna(subset=["crp", "infected"])
            infected = (clinic["infected"] == "yes").to_numpy(dtype=float)
            crp = clinic["crp"].to_numpy(dtype=float)
        """,
        r_packages=("pROC",), compare="result", fields=("value", "y"), tolerance=1e-12,
        choices=("the best cut-off by Youden's index, R pROC::coords(\"best\", best.method = \"youden\"); "
                 "its threshold is the value of the marked dot, its sensitivity the dot's y.",),
        python_note="Python's stack (SciPy, statsmodels) has no ROC analysis with DeLong's interval, so the "
                    "numbers come from R.",
        also="The dot's x is the false alarms there (1 - specificity), as drawn; table.compare_to_truth gives the "
             "same cut-off with its sensitivity and specificity as a result table.",
    ),
]

