"""The reliability study for the words and options added on 2026-11-21 (PR words-and-fixes): chart.get_numbers_drawn(),
table.repeat_each_row_by(), the table that show_rows_that_pull_model() gives back, check_model_of(show="numbers"),
sdata.get_example(from_r_package=) and find_correlation_between(show="result table").

cases.py loads this file at its end and calls add_to(), which adds the cases below to its CASES. The datasets are
already in the study: Anscombe's quartet, stackloss, mtcars, Down syndrome by birth order and lung (R survival).
Each simplydata side uses simplydata words only; the references are the parent package, R and the published counts.
"""

from __future__ import annotations


def _cases(Case):
    return [
        Case("get_numbers_drawn", "Anscombe's first set: the drawn fitted line is the least-squares line",
             "Anscombe's quartet", "published",
             ours="""
                 chart = sdata.chart(data).draw_dots(x="x1", y="y1").fit_line()
                 drawn = chart.get_numbers_drawn()
                 line = sdata.table(drawn).keep_rows_where("kind", is_equal_to="line")
                 xs, ys = list(line.get_column("x")), list(line.get_column("y"))
                 {"slope of the drawn line": (ys[-1] - ys[0]) / (xs[-1] - xs[0]),
                  "dots drawn": len(sdata.table(drawn).keep_rows_where("kind", is_equal_to="dot"))}
             """,
             published={"slope of the drawn line": (0.5001, 0.0001, "Anscombe (1973)"),
                        "dots drawn": (11, 0, "Anscombe (1973)")},
             parent="""
                 import statsmodels.api as sm
                 fit = sm.OLS(data["y1"], sm.add_constant(data["x1"])).fit()
                 {"slope of the drawn line": fit.params["x1"], "dots drawn": len(data)}
             """, parent_label="statsmodels OLS", parent_tolerance=1e-9,
             note="The numbers come back from what matplotlib drew; Anscombe prints the slope 0.500 (0.5001)."),
        Case("table.repeat_each_row_by", "Down syndrome cases in Michigan: one row per case",
             "Down syndrome by birth order", "real data",
             ours="""
                 table = sdata.table(data)
                 table.repeat_each_row_by("cases")
                 {"rows": len(table), "first birth order rows": len(sdata.table(table).keep_rows_where(
                     "birth_order", is_equal_to="1"))}
             """,
             parent="""
                 long = data.loc[data.index.repeat(data["cases"])]
                 {"rows": len(long), "first birth order rows": int((long["birth_order"].astype(str) == "1").sum())}
             """, parent_label="pandas index.repeat", parent_tolerance=0),
        Case("table.show_rows_that_pull_model", "stackloss: the rows with a Cook's distance above 4/n",
             "stackloss", "published",
             ours="""
                 found = sdata.table(data).show_rows_that_pull_model("stack_loss",
                                                                    using=["air_flow", "water_temp", "acid_conc"])
                 {"first row": found.get_cell_at(row=1, column="row"),
                  "its Cook's distance": found.get_cell_at(row=1, column="Cook's distance"), "rows found": len(found)}
             """,
             published={"first row": (21, 0, "Daniel & Wood (1980): observation 21 is the most influential")},
             r="""
                 m <- lm(stack_loss ~ air_flow + water_temp + acid_conc)
                 d <- cooks.distance(m)
                 list(`first row` = which.max(d), `its Cook's distance` = max(d), `rows found` = sum(d > 4 / length(d)))
             """, r_tolerance=1e-9),
        Case("sdata.get_example", "lung from R survival: the dataset as R ships it", "lung with weight loss (survival)",
             "real data", option="from_r_package=", ours_r=("survival",),
             ours="""
                 lung = sdata.get_example("lung", from_r_package="survival")
                 first = lung.get_row(1)
                 {"rows": len(lung), "time of the first row": first["time"], "age of the first row": first["age"]}
             """,
             r="""
                 list(rows = length(time), `time of the first row` = time[1], `age of the first row` = age[1])
             """, r_packages=("survival",), r_tolerance=0),
        Case("table.check_model_of", 'show="numbers": mtcars mpg ~ wt + hp, the Breusch-Pagan test', "mtcars",
             "real data", option='show="numbers"',
             ours="""
                 numbers = sdata.table(data).check_model_of("mpg", using=["wt", "hp"], show="numbers")
                 bp = sdata.table(numbers).keep_rows_where("check", is_equal_to="Breusch-Pagan test (chi-square)")
                 {"BP": bp.get_cell_at(row=1, column="value"), "p": bp.get_cell_at(row=1, column="p-value")}
             """,
             r="""
                 b <- lmtest::bptest(lm(mpg ~ wt + hp))
                 list(BP = unname(b$statistic), p = unname(b$p.value))
             """, r_packages=("lmtest",), r_tolerance=1e-9),
        Case("table.find_correlation_between", 'show="result table": mtcars mpg and wt', "mtcars", "real data",
             option='show="result table"',
             ours="""
                 row = sdata.table(data).find_correlation_between("mpg", "wt", show="result table").get_row(1)
                 {"r": row["r"], "low": row["95 % CI low"], "high": row["95 % CI high"], "p": row["p-value"]}
             """,
             r="""
                 t <- cor.test(mpg, wt)
                 list(r = unname(t$estimate), low = t$conf.int[1], high = t$conf.int[2], p = t$p.value)
             """, r_tolerance=1e-9),
    ]


def add_to(namespace) -> None:
    """Add the cases to cases.py."""
    namespace["CASES"].extend(_cases(namespace["Case"]))
