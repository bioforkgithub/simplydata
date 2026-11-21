"""The reliability study for the "same underneath" entries added in phases U1 to U3: each word that got a box in the
manual is also run on real, published data and compared with the package underneath (pandas, Polars, NumPy, SciPy,
statsmodels, seaborn) and, where it is plain base R, with R.

cases.py loads this file at its end and calls add_to(), which adds the cases below to its own CASES. The datasets
are the study's own (validation/data, README.md): Fisher's iris, mtcars, warpbreaks, birthwt, NHANES (mice), the
AirPassengers series, NIST's Michelson and Norris data, Student's sleep data and the BCG trials (read from R
metadat, as the combining-studies cases do). Words that show something and give nothing back (show_first_rows,
describe_columns, show_rows_with_outliers) are checked on what they print: the printed numbers are read back.
"""

from __future__ import annotations

import textwrap

PRINTED = """
    import contextlib
    import io
    shown = io.StringIO()
    with contextlib.redirect_stdout(shown):
        {call}
    lines = [line for line in shown.getvalue().splitlines() if line.strip()]
"""


def _printed(call: str, then: str) -> str:
    """Code that runs a word that prints, keeping what it printed in `lines`, then the code `then`."""
    return textwrap.dedent(PRINTED).format(call=call) + textwrap.dedent(then)


def _cases(Case):
    return [
        # ---- tables: start and look
        Case("table.show_first_rows", "the first 3 of Fisher's 150 iris flowers, numbered from 1", "iris", "real data",
             ours=_printed('sdata.table(data).show_first_rows(3)', """
                 rows = [line.split() for line in lines[1:]]
                 {"rows shown": len(rows), "first row number": int(rows[0][0]),
                  "sepal length total": sum(float(r[1]) for r in rows)}
             """),
             parent="""
                 first = data.head(3)
                 {"rows shown": len(first), "first row number": 1, "sepal length total": first["Sepal.Length"].sum()}
             """, parent_label="pandas head", parent_tolerance=1e-12),
        Case("table.describe_columns", "the columns of Fisher's iris data: averages and kinds", "iris", "real data",
             ours=_printed('sdata.table(data).describe_columns()', """
                 cells = {line.split()[0]: line.split() for line in lines[2:]}
                 {"average sepal length": float(cells["Sepal.Length"][-1]),
                  "average petal width": float(cells["Petal.Width"][-1]),
                  "species": float(cells["Species"][-1]), "columns": len(cells)}
             """),
             parent="""
                 {"average sepal length": round(data["Sepal.Length"].mean(), 2),
                  "average petal width": round(data["Petal.Width"].mean(), 2),
                  "species": data["Species"].nunique(), "columns": data.shape[1]}
             """, parent_label="pandas mean (rounded to 2 decimals, as printed) and nunique", parent_tolerance=1e-12,
             r="""
                 list(`average sepal length` = round(mean(Sepal.Length), 2), species = length(unique(Species)))
             """, r_tolerance=1e-12),
        Case("table.keep_columns", "two of the 11 columns of mtcars", "mtcars", "real data",
             ours="""
                 kept = sdata.table(data).keep_columns("mpg", "hp")
                 {"columns": len(kept.get_column_names()), "total mpg": kept.get_column("mpg").find_total(),
                  "total hp": kept.get_column("hp").find_total()}
             """,
             parent="""
                 kept = data[["mpg", "hp"]]
                 {"columns": kept.shape[1], "total mpg": kept["mpg"].sum(), "total hp": kept["hp"].sum()}
             """, parent_label="pandas column selection", parent_tolerance=0.0),
        Case("table.rename_column", "mpg renamed in mtcars", "mtcars", "real data",
             ours="""
                 renamed = sdata.table(data).rename_column("mpg", to="miles_per_gallon")
                 {"total": renamed.get_column("miles_per_gallon").find_total(), "columns": len(renamed.get_column_names())}
             """,
             parent="""
                 renamed = data.rename(columns={"mpg": "miles_per_gallon"})
                 {"total": renamed["miles_per_gallon"].sum(), "columns": renamed.shape[1]}
             """, parent_label="pandas rename", parent_tolerance=0.0),
        Case("table.sort_by", "NHANES body mass index, biggest first, empty cells last", "nhanes (mice)", "real data",
             ours="""
                 s = sdata.table(data).sort_by("bmi", biggest_first=True)
                 bmi = s.get_column("bmi")
                 {"first bmi": s.get_cell_at(row=1, column="bmi"), "first empty row": bmi.count() - bmi.count_empty_numbers(),
                  "age of the first row": s.get_cell_at(row=1, column="age")}
             """,
             parent="""
                 s = data.sort_values("bmi", ascending=False, kind="stable", na_position="last")
                 {"first bmi": s["bmi"].iloc[0], "first empty row": int(s["bmi"].isna().to_numpy().argmax()),
                  "age of the first row": s["age"].iloc[0]}
             """, parent_label="pandas sort_values (stable)", parent_tolerance=0.0),
        Case("table.keep_rows_by_position", "rows 10 to 20 of mtcars", "mtcars", "real data",
             ours="""
                 mpg = sdata.table(data).keep_rows_by_position(10, to=20).get_column("mpg")
                 {"rows": mpg.count(), "total mpg": mpg.find_total()}
             """,
             parent="""
                 kept = data.iloc[9:20]
                 {"rows": len(kept), "total mpg": kept["mpg"].sum()}
             """, parent_label="pandas iloc", parent_tolerance=1e-12,
             r="""
                 list(rows = length(mpg[10:20]), `total mpg` = sum(mpg[10:20]))
             """, r_tolerance=1e-12),
        Case("table.fill_empty_cells_in", "NHANES body mass index: the 9 empty cells filled with the median",
             "nhanes (mice)", "real data",
             ours="""
                 bmi = sdata.table(data).fill_empty_cells_in("bmi", with_the="median").get_column("bmi")
                 {"total": bmi.find_total(), "empty cells left": bmi.count_empty_numbers()}
             """,
             parent="""
                 filled = data["bmi"].fillna(data["bmi"].median())
                 {"total": filled.sum(), "empty cells left": int(filled.isna().sum())}
             """, parent_label="pandas fillna with the median", parent_tolerance=1e-12,
             r="""
                 b <- bmi; b[is.na(b)] <- median(bmi, na.rm = TRUE)
                 list(total = sum(b))
             """, r_tolerance=1e-12),
        Case("table.turn_into_numbers", "mtcars miles per gallon written with decimal commas, read back as numbers",
             "mtcars", "real data",
             ours="""
                 text = data.assign(mpg=data["mpg"].map(lambda v: f"{v:.1f}".replace(".", ",")))
                 mpg = sdata.table(text).turn_into_numbers("mpg").get_column("mpg")
                 {"total": mpg.find_total(), "empty cells": mpg.count_empty_numbers()}
             """,
             parent="""
                 {"total": data["mpg"].sum(), "empty cells": 0}
             """, parent_label="the published numbers themselves", parent_tolerance=1e-12),
        Case("table.add_column", "mtcars horsepower per 1000 lb", "mtcars", "real data",
             ours="""
                 t = sdata.table(data).add_column("hp_per_wt", "hp / wt")
                 {"total": t.get_column("hp_per_wt").find_total(), "first": t.get_cell_at(row=1, column="hp_per_wt")}
             """,
             parent="""
                 x = data["hp"] / data["wt"]
                 {"total": x.sum(), "first": x.iloc[0]}
             """, parent_label="pandas division", parent_tolerance=1e-12,
             r="""
                 x <- hp / wt
                 list(total = sum(x), first = x[1])
             """, r_tolerance=1e-12),
        Case("table.add_group_column", "mtcars cars put into four fuel-use groups (cut at 15, 20 and 25 mpg)", "mtcars",
             "real data",
             ours="""
                 t = sdata.table(data).add_group_column("group", from_column="mpg", cut_at=[15, 20, 25],
                                                        names=["D", "C", "B", "A"])
                 groups = t.get_column("group")
                 {g: groups.count(g) for g in "ABCD"}
             """,
             parent="""
                 g = pd.cut(data["mpg"], [-np.inf, 15, 20, 25, np.inf], labels=["D", "C", "B", "A"], right=False)
                 {k: int((g == k).sum()) for k in "ABCD"}
             """, parent_label="pandas cut(right=False)", parent_tolerance=0.0,
             r="""
                 g <- cut(mpg, c(-Inf, 15, 20, 25, Inf), labels = c("D", "C", "B", "A"), right = FALSE)
                 list(A = sum(g == "A"), B = sum(g == "B"), C = sum(g == "C"), D = sum(g == "D"))
             """, r_tolerance=0.0),
        Case("table.find_summary_of", "sepal length of each iris species: average, standard deviation, count", "iris",
             "real data",
             ours="""
                 s = sdata.table(data).find_summary_of("Sepal.Length", for_each_group_in="Species",
                                                       show=["average", "standard deviation", "count"])
                 rows = {s.get_cell_at(row=i, column="Species"): i for i in (1, 2, 3)}
                 {f"{k} {sp}": s.get_cell_at(row=rows[sp], column=m) for sp in ("setosa", "virginica")
                  for k, m in (("average", "average"), ("sd", "standard deviation"), ("count", "count"))}
             """,
             parent="""
                 g = data.groupby("Species")["Sepal.Length"].agg(["mean", "std", "count"])
                 {f"{k} {sp}": g.loc[sp, m] for sp in ("setosa", "virginica")
                  for k, m in (("average", "mean"), ("sd", "std"), ("count", "count"))}
             """, parent_label="pandas groupby().agg()", parent_tolerance=1e-12,
             r="""
                 m <- tapply(Sepal.Length, Species, mean); s <- tapply(Sepal.Length, Species, sd)
                 list(`average setosa` = m[["setosa"]], `sd setosa` = s[["setosa"]],
                      `average virginica` = m[["virginica"]], `sd virginica` = s[["virginica"]])
             """, r_tolerance=1e-12),
        Case("table.join_with", "mtcars joined with a small table of cylinder labels (all rows of mtcars kept)",
             "mtcars", "real data",
             ours="""
                 t = sdata.table(data).join_with({"cyl": [4, 6], "size": [1, 2]}, using="cyl",
                                                 keep="all rows from this table")
                 size = t.get_column("size")
                 {"rows": size.count(), "empty sizes": size.count_empty_numbers(), "total size": size.find_total()}
             """,
             parent="""
                 t = data.merge(pd.DataFrame({"cyl": [4, 6], "size": [1, 2]}), on="cyl", how="left")
                 {"rows": len(t), "empty sizes": int(t["size"].isna().sum()), "total size": t["size"].sum()}
             """, parent_label="pandas merge(how=\"left\")", parent_tolerance=0.0),
        Case("table.add_z_score_column", "z-scores of iris sepal length within each species", "iris", "real data",
             ours="""
                 t = sdata.table(data).add_z_score_column("z", from_column="Sepal.Length",
                                                          for_each_group_in="Species")
                 {"first": t.get_cell_at(row=1, column="z"), "last": t.get_cell_at(row=150, column="z"),
                  "sum of squares": t.get_column("z").raise_to_power(2).find_total()}
             """,
             parent="""
                 from scipy import stats
                 z = data.groupby("Species")["Sepal.Length"].transform(stats.zscore, ddof=1)
                 {"first": z.iloc[0], "last": z.iloc[-1], "sum of squares": (z ** 2).sum()}
             """, parent_label="SciPy zscore(ddof=1)", parent_tolerance=1e-10,
             r="""
                 z <- ave(Sepal.Length, Species, FUN = function(v) as.numeric(scale(v)))
                 list(first = z[1], last = z[length(z)], `sum of squares` = sum(z^2))
             """, r_tolerance=1e-10),
        Case("table.save", "iris saved as CSV and read back", "iris", "real data",
             ours="""
                 import os
                 import tempfile
                 with tempfile.TemporaryDirectory() as folder:
                     sdata.table(data).save(os.path.join(folder, "iris.csv"))
                     back = sdata.table(os.path.join(folder, "iris.csv"))
                 petals = back.get_column("Petal.Length")
                 {"rows": petals.count(), "total petal length": petals.find_total(), "columns": len(back.get_column_names())}
             """,
             parent="""
                 import os
                 import tempfile
                 with tempfile.TemporaryDirectory() as folder:
                     data.to_csv(os.path.join(folder, "iris.csv"), index=False)
                     back = pd.read_csv(os.path.join(folder, "iris.csv"))
                 {"rows": len(back), "total petal length": back["Petal.Length"].sum(), "columns": back.shape[1]}
             """, parent_label="pandas to_csv(index=False)", parent_tolerance=1e-12),
        Case("table.as_pandas", "iris given back as pandas, from a Polars table", "iris", "real data",
             ours="""
                 import polars as pl
                 back = sdata.table(pl.from_pandas(data)).as_pandas()
                 {"rows": len(back), "total sepal width": back["Sepal.Width"].sum()}
             """,
             parent="""
                 import polars as pl
                 back = pl.from_pandas(data).to_pandas()
                 {"rows": len(back), "total sepal width": back["Sepal.Width"].sum()}
             """, parent_label="Polars to_pandas", parent_tolerance=1e-12),
        Case("table.as_polars", "iris given back as Polars, from a pandas table", "iris", "real data",
             ours="""
                 back = sdata.table(data).as_polars()
                 {"rows": back.height, "total sepal width": back["Sepal.Width"].sum()}
             """,
             parent="""
                 import polars as pl
                 back = pl.from_pandas(data)
                 {"rows": back.height, "total sepal width": back["Sepal.Width"].sum()}
             """, parent_label="Polars from_pandas", parent_tolerance=1e-12),
        Case("table.remove_extra_spaces_in", "the names of the 32 mtcars cars with extra spaces put in, cleaned",
             "mtcars", "real data",
             ours="""
                 spaced = data.assign(model="  " + data["model"].str.replace(" ", "   ") + " ")
                 back = sdata.table(spaced).remove_extra_spaces_in("model").get_column("model")
                 {"names as published": sum(a == b for a, b in zip(back, data["model"]))}
             """,
             parent="""
                 {"names as published": len(data)}
             """, parent_label="the published names themselves", parent_tolerance=0.0),
        Case("table.replace_values_in", "warpbreaks: wool A renamed", "warpbreaks", "real data",
             ours="""
                 wool = sdata.table(data).replace_values_in("wool", "A", with_value="wool A").get_column("wool")
                 {"wool A": wool.count("wool A"), "B": wool.count("B")}
             """,
             parent="""
                 w = data["wool"].mask(data["wool"] == "A", "wool A")
                 {"wool A": int((w == "wool A").sum()), "B": int((w == "B").sum())}
             """, parent_label="pandas mask", parent_tolerance=0.0),
        Case("table.add_missing_dates", "AirPassengers with three months taken out: the months put back", "AirPassengers",
             "real data",
             ours="""
                 gappy = data.assign(month=pd.to_datetime(data["month"])).drop(index=[10, 11, 50]).reset_index(drop=True)
                 passengers = sdata.table(gappy).add_missing_dates("month", every="month").get_column("passengers")
                 {"rows": passengers.count(), "empty cells": passengers.count_empty_numbers(), "total": passengers.find_total()}
             """,
             parent="""
                 gappy = data.assign(month=pd.to_datetime(data["month"])).drop(index=[10, 11, 50])
                 months = pd.date_range(gappy["month"].min(), gappy["month"].max(), freq="MS")
                 back = gappy.set_index("month").reindex(months)
                 {"rows": len(back), "empty cells": int(back["passengers"].isna().sum()),
                  "total": back["passengers"].sum()}
             """, parent_label="pandas date_range and reindex", parent_tolerance=1e-12),
        Case("table.add_rolling_column", "AirPassengers: the total of the last 12 months", "AirPassengers", "real data",
             ours="""
                 t = sdata.table(data).add_rolling_column("year_total", from_column="passengers", window=12,
                                                          show="total")
                 {"last": t.get_cell_at(row=144, column="year_total"), "first full": t.get_cell_at(row=12, column="year_total"),
                  "empty": t.get_column("year_total").count_empty_numbers()}
             """,
             parent="""
                 r = data["passengers"].rolling(12).sum()
                 {"last": r.iloc[-1], "first full": r.iloc[11], "empty": int(r.isna().sum())}
             """, parent_label="pandas rolling(12).sum()", parent_tolerance=1e-12,
             r="""
                 r <- stats::filter(passengers, rep(1, 12), sides = 1)
                 list(last = r[length(r)], `first full` = r[12], empty = sum(is.na(r)))
             """, r_tolerance=1e-12),
        Case("table.show_rows_with_outliers", "mtcars horsepower: outliers within each number of cylinders (Tukey)",
             "mtcars", "real data",
             ours=_printed('sdata.table(data).show_rows_with_outliers("hp", for_each_group_in="cyl")', """
                 start = next(i for i, line in enumerate(lines) if line.lstrip().startswith("model"))
                 rows = [int(line.split()[0]) for line in lines[start + 1:] if line.split()[0].isdigit()]
                 {"rows found": len(rows), "sum of row numbers": sum(rows)}
             """),
             parent="""
                 g = data.groupby("cyl")["hp"]
                 q1, q3 = g.transform("quantile", 0.25), g.transform("quantile", 0.75)
                 found = data[(data["hp"] < q1 - 1.5 * (q3 - q1)) | (data["hp"] > q3 + 1.5 * (q3 - q1))]
                 {"rows found": len(found), "sum of row numbers": int(np.sum(np.asarray(found.index) + 1))}
             """, parent_label="pandas quantile (linear) and Tukey's rule", parent_tolerance=0.0),
        # ---- starting words
        Case("sdata.table", "Fisher's iris data read from a CSV file", "iris", "real data",
             ours="""
                 import os
                 import tempfile
                 with tempfile.TemporaryDirectory() as folder:
                     data.to_csv(os.path.join(folder, "iris.csv"), index=False)
                     width = sdata.table(os.path.join(folder, "iris.csv")).get_column("Petal.Width")
                 {"rows": width.count(), "total petal width": width.find_total()}
             """,
             parent="""
                 {"rows": len(data), "total petal width": data["Petal.Width"].sum()}
             """, parent_label="pandas read_csv", parent_tolerance=1e-12),
        Case("sdata.get_example", "the practice table bcg against the published trials in R metadat (dat.bcg)",
             "BCG trials (metadat)", "real data",
             ours="""
                 bcg = sdata.table(sdata.get_example("bcg"))
                 {"trials": bcg.get_column("vaccinated").count(), "cases vaccinated": bcg.get_column("tb_vaccinated").find_total(),
                  "vaccinated": bcg.get_column("vaccinated").find_total(),
                  "cases unvaccinated": bcg.get_column("tb_unvaccinated").find_total(),
                  "latitudes": bcg.get_column("latitude").find_total()}
             """,
             parent="""
                 {"trials": len(data), "cases vaccinated": data["tpos"].sum(), "vaccinated": data["vaccinated"].sum(),
                  "cases unvaccinated": data["cpos"].sum(), "latitudes": data["ablat"].sum()}
             """, parent_label="R metadat dat.bcg (the published counts)", parent_tolerance=0.0),
        Case("sdata.chart", "the 36 Norris calibration points on a new chart", "NIST Norris", "real data",
             ours="""
                 from simplydata._underneath.check import chart_facts
                 ax = sdata.chart(data).draw_dots(x="x", y="y")._render().axes[0]
                 dots = chart_facts(ax)["dots"]
                 {"dots": len(dots), "sum of y": sum(d[1] for d in dots)}
             """,
             parent="""
                 import matplotlib.pyplot as plt
                 import seaborn as sns
                 from simplydata._underneath.check import chart_facts
                 fig, ax = plt.subplots()
                 sns.scatterplot(data, x="x", y="y", ax=ax)
                 dots = chart_facts(ax)["dots"]
                 {"dots": len(dots), "sum of y": sum(d[1] for d in dots)}
             """, parent_label="seaborn scatterplot", parent_tolerance=1e-12),
        Case("table.start_chart", "Student's sleep data: a chart of drug 2 only, started from the table",
             "Student's sleep data", "published",
             ours="""
                 from simplydata._underneath.check import chart_facts
                 t = sdata.table(data).keep_rows_where("group", is_equal_to="drug 2")
                 ax = t.start_chart().draw_bars(x="group", y="extra")._render().axes[0]
                 {"bar": chart_facts(ax)["bars"][0][3], "bars": len(chart_facts(ax)["bars"])}
             """,
             published={"bar": (2.33, 0.005, "Student (1908)")},
             parent="""
                 import matplotlib.pyplot as plt
                 import seaborn as sns
                 from simplydata._underneath.check import chart_facts
                 fig, ax = plt.subplots()
                 sns.barplot(data[data["group"] == "drug 2"], x="group", y="extra", errorbar=None, ax=ax)
                 {"bar": chart_facts(ax)["bars"][0][3], "bars": len(chart_facts(ax)["bars"])}
             """, parent_label="seaborn barplot"),
        Case("sdata.numbers", "Michelson's 100 measurements as numbers", "NIST Michelso", "published",
             ours="""
                 nums = sdata.numbers(data["y"].tolist())
                 {"mean": nums.find_total() / nums.count(), "count": nums.count()}
             """,
             published={"mean": (299.8524, 1e-9, "NIST certified")},
             parent="""
                 {"mean": float(np.mean(np.array(data["y"].tolist()))), "count": len(data)}
             """, parent_label="NumPy array", parent_tolerance=0.0),
        Case("sdata.number_grid", "the 600 iris measurements as a grid of 150 rows and 4 columns", "iris", "real data",
             ours="""
                 values = data[["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]].to_numpy().ravel()
                 grid = sdata.number_grid(values.tolist(), columns=4)
                 {"rows": grid.count_rows(), "total of column 3": grid.get_column(3).find_total(),
                  "row 2 column 1": grid.get_number_at(row=2, column=1)}
             """,
             parent="""
                 grid = data[["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]].to_numpy()
                 {"rows": grid.shape[0], "total of column 3": grid[:, 2].sum(), "row 2 column 1": grid[1, 0]}
             """, parent_label="NumPy reshape (row after row)", parent_tolerance=1e-12),
        Case("sdata.distribution", "chance of at most 1.96 in the standard normal distribution",
             "standard normal table", "published",
             ours="""
                 {"chance at most 1.96": sdata.distribution("normal", average=0, standard_deviation=1)
                                         .find_chance_that_value(is_at_most=1.96)}
             """,
             # NIST/SEMATECH e-Handbook 1.3.6.7.1: the area from 0 to 1.96 is 0.47500, so below 1.96 is 0.5 + 0.47500
             published={"chance at most 1.96": (0.975, 0.000005, "NIST/SEMATECH e-Handbook, table 1.3.6.7.1")},
             parent="""
                 from scipy import stats
                 {"chance at most 1.96": stats.norm(loc=0, scale=1).cdf(1.96)}
             """, parent_label="SciPy stats.norm.cdf", parent_tolerance=1e-14,
             r="""
                 list(`chance at most 1.96` = pnorm(1.96))
             """, r_tolerance=1e-14,
             note="No data: the published value is the standard normal table (5 decimals)."),
        Case("sdata.make_random_numbers", "random numbers shaped like Michelson's measurements (their average and "
                                          "standard deviation), seed 1", "NIST Michelso", "real data",
             ours="""
                 m, s = data["y"].mean(), data["y"].std()
                 nums = sdata.make_random_numbers(how_many=100, average=m, standard_deviation=s, with_seed=1)
                 {"first": nums.get_number_at(1), "total": nums.find_total()}
             """,
             parent="""
                 m, s = data["y"].mean(), data["y"].std()
                 x = np.random.default_rng(1).normal(m, s, 100)
                 {"first": x[0], "total": x.sum()}
             """, parent_label="NumPy default_rng(1).normal", parent_tolerance=1e-12,
             note="Random numbers have no published answer; the check is that the same seed gives NumPy's numbers."),
        Case("sdata.make_run_of_dates", "the 144 months of the AirPassengers series", "AirPassengers", "real data",
             ours="""
                 dates = sdata.make_run_of_dates("1949-01-01", how_many=144, every="month").get_column("date")
                 {"dates": len(dates), "same as the series": sum(a == b for a, b in zip(dates, pd.to_datetime(data["month"])))}
             """,
             parent="""
                 {"dates": len(data), "same as the series": len(data)}
             """, parent_label="the dates of the published series", parent_tolerance=0.0),
        # ---- numbers and distributions
        Case("nums.find_average", "average of Michelson's 100 speed-of-light measurements", "NIST Michelso",
             "published",
             ours="""
                 {"mean": sdata.numbers(data["y"].tolist()).find_average()}
             """,
             published={"mean": (299.8524, "lre", "NIST certified")},
             parent="""
                 {"mean": np.nanmean(data["y"].to_numpy())}
             """, parent_label="NumPy nanmean", parent_tolerance=1e-15,
             r="""
                 list(mean = mean(y))
             """, r_tolerance=1e-14),
        Case("nums.find_percentile", "90th percentile of Michelson's measurements", "NIST Michelso", "real data",
             ours="""
                 {"percentile 90": sdata.numbers(data["y"].tolist()).find_percentile(90)}
             """,
             parent="""
                 {"percentile 90": np.nanpercentile(data["y"].to_numpy(), 90)}
             """, parent_label="NumPy nanpercentile (linear)", parent_tolerance=1e-15,
             r="""
                 list(`percentile 90` = unname(quantile(y, 0.9, type = 7)))
             """, r_tolerance=1e-14),
        Case("nums.keep_each_number_that", "Michelson's measurements above 299.9", "NIST Michelso", "real data",
             ours="""
                 kept = sdata.numbers(data["y"].tolist()).keep_each_number_that(is_above=299.9)
                 {"kept": kept.count(), "total": kept.find_total()}
             """,
             parent="""
                 y = data["y"].to_numpy()
                 {"kept": len(y[y > 299.9]), "total": y[y > 299.9].sum()}
             """, parent_label="NumPy boolean indexing", parent_tolerance=1e-12,
             r="""
                 list(kept = sum(y > 299.9), total = sum(y[y > 299.9]))
             """, r_tolerance=1e-12),
        Case("dist.find_percentile", "the 97.5th percentile of the standard normal distribution",
             "standard normal table", "published",
             ours="""
                 {"percentile 97.5": sdata.distribution("normal", average=0, standard_deviation=1)
                                     .find_percentile(97.5)}
             """,
             # the table gives 0.47500 for z = 1.96: 97.5 % lies below 1.96, printed to 2 decimals
             published={"percentile 97.5": (1.96, 0.005, "NIST/SEMATECH e-Handbook, table 1.3.6.7.1")},
             parent="""
                 from scipy import stats
                 {"percentile 97.5": stats.norm.ppf(0.975)}
             """, parent_label="SciPy stats.norm.ppf", parent_tolerance=1e-14,
             r="""
                 list(`percentile 97.5` = qnorm(0.975))
             """, r_tolerance=1e-14,
             note="No data: the published value is the standard normal table."),
        # ---- statistics
        Case("table.compare_spreads_of", "warpbreaks: do the breaks spread differently at the three tensions?",
             "warpbreaks", "real data",
             ours="""
                 r = sdata.table(data).compare_spreads_of("breaks", for_each_group_in="tension")
                 {"F": r.get_cell_at(row=1, column="statistic"), "p-value": r.get_cell_at(row=1, column="p-value"),
                  "df 2": r.get_cell_at(row=1, column="degrees of freedom 2")}
             """,
             parent="""
                 from scipy import stats
                 groups = [g["breaks"] for _, g in data.groupby("tension")]
                 res = stats.levene(*groups, center="median")
                 {"F": res.statistic, "p-value": res.pvalue, "df 2": len(data) - 3}
             """, parent_label="SciPy levene(center=\"median\")", parent_tolerance=1e-10,
             r="""
                 d <- abs(breaks - ave(breaks, tension, FUN = median))
                 a <- anova(lm(d ~ factor(tension)))
                 list(F = a$`F value`[1], `p-value` = a$`Pr(>F)`[1], `df 2` = a$Df[2])
             """, r_tolerance=1e-10,
             note="R's check is the Brown-Forsythe test written out: a one-way ANOVA of the distances from each "
                  "group's median, which is what car::leveneTest() computes."),
        Case("table.compare_percent_to", "birthwt: is the percent of low birth weights 30 %?", "birthwt", "real data",
             ours="""
                 t = data.assign(low=data["low"].map({1: "yes", 0: "no"}))
                 r = sdata.table(t).compare_percent_to("low", value="yes", percent=30)
                 {name: r.get_cell_at(row=1, column=column) for name, column in (
                     ("low births", "statistic"), ("p-value", "p-value"), ("CI low", "percent 95 % CI low"),
                     ("CI high", "percent 95 % CI high"))}
             """,
             parent="""
                 from scipy import stats
                 res = stats.binomtest(int(data["low"].sum()), len(data), 0.3)
                 ci = res.proportion_ci(confidence_level=0.95, method="exact")
                 {"low births": data["low"].sum(), "p-value": res.pvalue, "CI low": ci.low * 100,
                  "CI high": ci.high * 100}
             """, parent_label="SciPy binomtest (Clopper-Pearson interval)", parent_tolerance=1e-10,
             r="""
                 b <- binom.test(sum(low), length(low), p = 0.3)
                 list(`p-value` = b$p.value, `CI low` = b$conf.int[1] * 100, `CI high` = b$conf.int[2] * 100)
             """, r_tolerance=1e-8),
        Case("table.add_principal_components", "principal components of Fisher's four iris measurements", "iris",
             "real data",
             ours="""
                 t = sdata.table(data).add_principal_components(how_many=2)
                 {"PC1 of row 1": t.get_cell_at(row=1, column="PC1"), "PC2 of row 1": t.get_cell_at(row=1, column="PC2"),
                  "PC1 of row 150": t.get_cell_at(row=150, column="PC1")}
             """,
             parent="""
                 from statsmodels.multivariate.pca import PCA
                 x = data.select_dtypes("number")
                 z = (x - x.mean()) / x.std()
                 w = np.asarray(PCA(z, ncomp=2, standardize=False, demean=False, normalize=False, method="svd").loadings)
                 w = w * np.sign(w[np.abs(w).argmax(axis=0), [0, 1]])
                 s = z.to_numpy() @ w
                 {"PC1 of row 1": s[0, 0], "PC2 of row 1": s[0, 1], "PC1 of row 150": s[-1, 0]}
             """, parent_label="statsmodels PCA (SVD)", parent_tolerance=1e-9,
             r="""
                 p <- prcomp(cbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width), scale. = TRUE)
                 w <- p$rotation
                 s <- sign(w[cbind(apply(abs(w), 2, which.max), seq_len(ncol(w)))])
                 x <- p$x %*% diag(s)
                 list(`PC1 of row 1` = x[1, 1], `PC2 of row 1` = x[1, 2], `PC1 of row 150` = x[nrow(x), 1])
             """, r_tolerance=1e-9),
        Case("table.add_predicted_column", "mtcars: fuel use predicted from weight and horsepower", "mtcars",
             "real data",
             ours="""
                 t = sdata.table(data).add_predicted_column("mpg", using=["wt", "hp"])
                 {"first": t.get_cell_at(row=1, column="predicted mpg"), "last": t.get_cell_at(row=32, column="predicted mpg")}
             """,
             parent="""
                 import statsmodels.formula.api as smf
                 f = smf.ols("mpg ~ wt + hp", data=data).fit().fittedvalues
                 {"first": f.iloc[0], "last": f.iloc[-1]}
             """, parent_label="statsmodels OLS fittedvalues", parent_tolerance=1e-10,
             r="""
                 f <- fitted(lm(mpg ~ wt + hp))
                 list(first = f[[1]], last = f[[length(f)]])
             """, r_tolerance=1e-10),
    ] + _cases_batch_2(Case)


# ---------------------------------------------------------------- U-batch 2: chart words read back as data
# simplydata has no word that reads back what a chart drew, so the simplydata side reads its own chart with the same
# chart_facts() the tests use (bars, dots, lines, labels, texts, sizes ...), as the sdata.chart case above does. The
# library side draws the same chart with seaborn or matplotlib and reads it the same way; R gives the numbers the
# chart should show (averages, medians, sums), where it is plain base R.
CHART_FACTS_OF = "from simplydata._underneath.check import chart_facts\n"
LIBRARY_CHART = ("import matplotlib.pyplot as plt\nimport seaborn as sns\n"
                 "from simplydata._underneath.check import chart_facts\n")


def _ours_chart(build: str, then: str, axes: str = "chart._render().axes[0]") -> str:
    """simplydata code that builds a chart (ending in `chart`), reads its facts into f, then the code `then`."""
    return (CHART_FACTS_OF + textwrap.dedent(build).strip("\n") + f"\nf = chart_facts({axes})\n"
            + textwrap.dedent(then).strip("\n"))


def _library_chart(build: str, then: str, axes: str = "ax") -> str:
    """seaborn / matplotlib code that draws on `ax`, reads its facts into f, then the code `then`."""
    return (LIBRARY_CHART + textwrap.dedent(build).strip("\n") + f"\nf = chart_facts({axes})\n"
            + textwrap.dedent(then).strip("\n"))


def _rgb(colour: str) -> str:
    """Code for a dict of the red, green and blue (0 to 255) of a colour written as #rrggbbaa."""
    return f'{{"red": int({colour}[1:3], 16), "green": int({colour}[3:5], 16), "blue": int({colour}[5:7], 16)}}'


def _cases_batch_2(Case):
    bars_cyl = 'sns.barplot(data, x="cyl", y="mpg", errorbar=None, ax=ax)'
    lines_wool = 'sns.lineplot(data, x="tension", y="breaks", hue="wool", errorbar=None, ax=ax)'
    return [
        Case("save", "mtcars: average fuel use for 4, 6 and 8 cylinders, saved as a picture", "mtcars", "real data",
             ours=_ours_chart("""
                 import os
                 import tempfile
                 chart = sdata.chart(data).draw_bars(x="cyl", y="mpg")
                 chart.save(os.path.join(tempfile.gettempdir(), "mtcars_save.png"))
             """, """
                 {"width (inches)": f["size"][0], "height (inches)": f["size"][1], "4 cylinders": f["bars"][0][3]}
             """),
             parent=_library_chart(f"""
                 import os
                 import tempfile
                 fig, ax = plt.subplots(figsize=(8, 6))
                 {bars_cyl}
                 fig.savefig(os.path.join(tempfile.gettempdir(), "mtcars_save_mpl.png"), dpi=300, bbox_inches="tight")
             """, """
                 {"width (inches)": f["size"][0], "height (inches)": f["size"][1], "4 cylinders": f["bars"][0][3]}
             """), parent_label="matplotlib savefig", parent_tolerance=1e-12,
             r="""
                 list(`4 cylinders` = mean(mpg[cyl == 4]))
             """, r_tolerance=1e-12),
        Case("write_title_on_top", "Fisher's iris: the average sepal length of each species, with a title", "iris",
             "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_bars(x="Species", y="Sepal.Length")
                 chart.write_title_on_top("Sepal length of three irises")
             """, """
                 {"title as written": float(f["labels"][2] == "Sepal length of three irises"), "setosa": f["bars"][0][3]}
             """),
             parent=_library_chart("""
                 fig, ax = plt.subplots()
                 sns.barplot(data, x="Species", y="Sepal.Length", errorbar=None, ax=ax)
                 ax.set_title("Sepal length of three irises")
             """, """
                 {"title as written": float(f["labels"][2] == "Sepal length of three irises"), "setosa": f["bars"][0][3]}
             """), parent_label="matplotlib set_title", parent_tolerance=1e-12,
             r="""
                 list(setosa = mean(Sepal.Length[Species == "setosa"]))
             """, r_tolerance=1e-12),
        *[Case(word, f"mtcars: fuel use against weight, the {axis} axis named", "mtcars", "real data",
               ours=_ours_chart(f"""
                   chart = sdata.chart(data).draw_dots(x="wt", y="mpg")
                   chart.{word}("{text}")
               """, f"""
                   {{"label as written": float(f["labels"][{place}] == "{text}"), "dots": len(f["dots"])}}
               """),
               parent=_library_chart(f"""
                   fig, ax = plt.subplots()
                   sns.scatterplot(data, x="wt", y="mpg", ax=ax)
                   ax.set_{axis}label("{text}")
               """, f"""
                   {{"label as written": float(f["labels"][{place}] == "{text}"), "dots": len(f["dots"])}}
               """), parent_label=f"matplotlib set_{axis}label", parent_tolerance=0.0)
          for word, axis, place, text in (("label_x", "x", 0, "Weight (1000 lb)"),
                                          ("label_y", "y", 1, "Miles per gallon"))],
        Case("rotate_labels_x", "mtcars: the 32 car names under their bars, stood up", "mtcars", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_bars(x="model", y="mpg").rotate_labels_x(90)
             """, """
                 {"angle of the first name": f["tick_angles"][0][0][0], "names": len(f["ticks"][0]),
                  "names lined up by their right end": sum(a[1] == "right" for a in f["tick_angles"][0])}
             """),
             parent=_library_chart("""
                 fig, ax = plt.subplots()
                 sns.barplot(data, x="model", y="mpg", errorbar=None, ax=ax)
                 for label in ax.get_xticklabels():
                     label.set_rotation(90)
                     label.set_horizontalalignment("right")
                     label.set_verticalalignment("center")
                     label.set_rotation_mode("anchor")
             """, """
                 {"angle of the first name": f["tick_angles"][0][0][0], "names": len(f["ticks"][0]),
                  "names lined up by their right end": sum(a[1] == "right" for a in f["tick_angles"][0])}
             """), parent_label="matplotlib set_rotation", parent_tolerance=0.0),
        Case("write_caption_at_bottom", "Fisher's iris: bars with the source written under them", "iris", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_bars(x="Species", y="Petal.Length")
                 chart.write_caption_at_bottom("Data: Fisher (1936)")
             """, """
                 {"caption written": float("Data: Fisher (1936)" in f["texts"][1]), "virginica": f["bars"][2][3]}
             """),
             parent=_library_chart("""
                 fig, ax = plt.subplots(layout="constrained")
                 sns.barplot(data, x="Species", y="Petal.Length", errorbar=None, ax=ax)
                 ax.annotate("Data: Fisher (1936)", xy=(0.5, 0), xycoords=ax.xaxis.label, xytext=(0, -4),
                             textcoords="offset points", ha="center", va="top")
             """, """
                 {"caption written": float("Data: Fisher (1936)" in f["texts"][1]), "virginica": f["bars"][2][3]}
             """), parent_label="matplotlib annotate", parent_tolerance=1e-12,
             r="""
                 list(virginica = mean(Petal.Length[Species == "virginica"]))
             """, r_tolerance=1e-12),
        Case("use_font_size", "Fisher's iris: bars with all their words in size 16", "iris", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_bars(x="Species", y="Sepal.Width")
                 chart.write_title_on_top("Sepal width").use_font_size(16)
             """, """
                 {"title": f["font_sizes"][0], "x label": f["font_sizes"][1], "tick labels": f["font_sizes"][3]}
             """),
             published={"title": (14 * 16 / 12, 1e-9, "exact"), "x label": (13 * 16 / 12, 1e-9, "exact"),
                        "tick labels": (11 * 16 / 12, 1e-9, "exact")},
             parent=_library_chart("""
                 scale = 16 / 12
                 sizes = {"font.size": 16, "axes.titlesize": 14 * scale, "axes.labelsize": 13 * scale,
                          "xtick.labelsize": 11 * scale, "ytick.labelsize": 11 * scale, "legend.fontsize": 11 * scale}
                 with plt.rc_context(sizes):
                     fig, ax = plt.subplots()
                     sns.barplot(data, x="Species", y="Sepal.Width", errorbar=None, ax=ax)
                     ax.set_title("Sepal width")
             """, """
                 {"title": f["font_sizes"][0], "x label": f["font_sizes"][1], "tick labels": f["font_sizes"][3]}
             """), parent_label="matplotlib rc_context", parent_tolerance=1e-12,
             note="simplydata's normal sizes are 12 (text), 14 (title), 13 (axis labels) and 11 (tick labels); "
                  "use_font_size(16) multiplies each by 16 / 12."),
        Case("use_colour", "Fisher's iris: every bar dark green", "iris", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_bars(x="Species", y="Petal.Width").use_colour("darkgreen")
             """, _rgb('f["colours"][0][0]')),
             published={"red": (0, 0, "exact"), "green": (100, 0, "exact"), "blue": (0, 0, "exact")},
             parent=_library_chart("""
                 fig, ax = plt.subplots()
                 sns.barplot(data, x="Species", y="Petal.Width", errorbar=None, color="darkgreen", saturation=1,
                             ax=ax)
             """, _rgb('f["colours"][0][0]')), parent_label="seaborn barplot(color=, saturation=1)",
             parent_tolerance=0.0,
             note="darkgreen is #006400 in the CSS colour names matplotlib uses."),
        Case("use_colours", "warpbreaks: the two wools in navy and orange", "warpbreaks", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_bars(x="tension", y="breaks", colour="wool")
                 chart.use_colours("navy", "orange")
             """, """
                 {"navy bars": f["colours"][0].count("#000080ff"), "orange bars": f["colours"][0].count("#ffa500ff"),
                  "first bar navy": float(f["colours"][0][0] == "#000080ff")}
             """),
             parent=_library_chart("""
                 fig, ax = plt.subplots()
                 sns.barplot(data, x="tension", y="breaks", hue="wool", palette=["navy", "orange"], errorbar=None,
                             saturation=1, ax=ax)
             """, """
                 {"navy bars": f["colours"][0].count("#000080ff"), "orange bars": f["colours"][0].count("#ffa500ff"),
                  "first bar navy": float(f["colours"][0][0] == "#000080ff")}
             """), parent_label="seaborn barplot(palette=)", parent_tolerance=0.0),
        *[Case(word, f"warpbreaks: lines of the two wools, the legend {where}", "warpbreaks", "real data",
               ours=_ours_chart(f"""
                   chart = sdata.chart(data).draw_lines(x="tension", y="breaks", colour="wool").{word}()
               """, """
                   {"legends on the figure": sum(p[0] == "figure" for p in f["legend_place"]),
                    "legends on the chart": sum(p[0] == "chart" for p in f["legend_place"]),
                    "place": f["legend_place"][0][1], "entries": len(f["legend_place"][0][4]) - 1}
               """),
               parent=_library_chart(f"""
                   fig, ax = plt.subplots(layout="constrained")
                   {lines_wool}
                   handles, labels = ax.get_legend_handles_labels()
                   ax.get_legend().remove()
                   fig.legend(handles, labels, title="wool", loc="{loc}"{columns})
               """, """
                   {"legends on the figure": sum(p[0] == "figure" for p in f["legend_place"]),
                    "legends on the chart": sum(p[0] == "chart" for p in f["legend_place"]),
                    "place": f["legend_place"][0][1], "entries": len(f["legend_place"][0][4]) - 1}
               """), parent_label="matplotlib fig.legend", parent_tolerance=0.0)
          for word, (where, loc, columns) in {"put_legend_at_bottom": ["below", "outside lower center", ", ncols=2"],
                                              "put_legend_on_left": ["on the left", "outside center left", ""]}.items()],
        Case("order_x", "warpbreaks: the tensions in the order high, medium, low", "warpbreaks", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_bars(x="tension", y="breaks").order_x("H", "M", "L")
             """, """
                 {"first bar (H)": f["bars"][0][3], "last bar (L)": f["bars"][2][3],
                  "first name": float(f["ticks"][0][0] == "H")}
             """),
             parent=_library_chart("""
                 fig, ax = plt.subplots()
                 sns.barplot(data, x="tension", y="breaks", order=["H", "M", "L"], errorbar=None, ax=ax)
             """, """
                 {"first bar (H)": f["bars"][0][3], "last bar (L)": f["bars"][2][3],
                  "first name": float(f["ticks"][0][0] == "H")}
             """), parent_label="seaborn barplot(order=)", parent_tolerance=1e-12,
             r="""
                 list(`first bar (H)` = mean(breaks[tension == "H"]), `last bar (L)` = mean(breaks[tension == "L"]))
             """, r_tolerance=1e-12),
        Case("use_style", "Fisher's iris: bars in the presentation style", "iris", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_bars(x="Species", y="Sepal.Length").use_style("presentation")
             """, """
                 {"title": f["font_sizes"][0], "x label": f["font_sizes"][1], "tick labels": f["font_sizes"][3]}
             """),
             published={"title": (20, 0, "exact"), "x label": (18, 0, "exact"), "tick labels": (15, 0, "exact")},
             parent=_library_chart("""
                 look = {"font.size": 16, "axes.titlesize": 20, "axes.labelsize": 18, "xtick.labelsize": 15,
                         "ytick.labelsize": 15, "legend.fontsize": 15, "lines.linewidth": 3.0}
                 with plt.rc_context(look):
                     fig, ax = plt.subplots()
                     sns.barplot(data, x="Species", y="Sepal.Length", errorbar=None, ax=ax)
             """, """
                 {"title": f["font_sizes"][0], "x label": f["font_sizes"][1], "tick labels": f["font_sizes"][3]}
             """), parent_label="matplotlib rc_context", parent_tolerance=0.0,
             note="The sizes of simplydata's presentation style: 20 for titles, 18 for axis labels, 15 for tick "
                  "labels."),
        Case("hide_legend", "warpbreaks: lines of the two wools, without a legend", "warpbreaks", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_lines(x="tension", y="breaks", colour="wool").hide_legend()
             """, """
                 {"legends": len(f["legend_place"]), "lines with points": sum(len(x) > 0 for x, _ in f["lines"])}
             """),
             parent=_library_chart(f"""
                 fig, ax = plt.subplots()
                 {lines_wool}
                 ax.get_legend().remove()
             """, """
                 {"legends": len(f["legend_place"]), "lines with points": sum(len(x) > 0 for x, _ in f["lines"])}
             """), parent_label="matplotlib Legend.remove", parent_tolerance=0.0),
        Case("draw_lines", "warpbreaks: the average breaks at each tension, one line for each wool", "warpbreaks",
             "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_lines(x="tension", y="breaks", colour="wool")
             """, """
                 {"wool A at L": f["lines"][0][1][0], "wool A at H": f["lines"][0][1][2], "wool B at M": f["lines"][1][1][1]}
             """),
             parent=_library_chart(f"""
                 fig, ax = plt.subplots()
                 {lines_wool}
             """, """
                 {"wool A at L": f["lines"][0][1][0], "wool A at H": f["lines"][0][1][2], "wool B at M": f["lines"][1][1][1]}
             """), parent_label="seaborn lineplot(errorbar=None)", parent_tolerance=1e-12,
             r="""
                 m <- tapply(breaks, list(wool, tension), mean)
                 list(`wool A at L` = m["A", "L"], `wool A at H` = m["A", "H"], `wool B at M` = m["B", "M"])
             """, r_tolerance=1e-12),
        Case("draw_boxes", "Fisher's iris: the sepal lengths of each species as boxes", "iris", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_boxes(x="Species", y="Sepal.Length")
             """, """
                 {"boxes": len(f["shapes"]), "setosa median": f["lines"][4][1][0], "virginica median": f["lines"][16][1][0]}
             """),
             parent=_library_chart("""
                 fig, ax = plt.subplots()
                 sns.boxplot(data, x="Species", y="Sepal.Length", saturation=1, ax=ax)
             """, """
                 {"boxes": len(f["shapes"]), "setosa median": f["lines"][4][1][0], "virginica median": f["lines"][16][1][0]}
             """), parent_label="seaborn boxplot", parent_tolerance=1e-12,
             r="""
                 list(boxes = 3, `setosa median` = median(Sepal.Length[Species == "setosa"]),
                      `virginica median` = median(Sepal.Length[Species == "virginica"]))
             """, r_tolerance=1e-12,
             note="Each box is drawn as two whiskers, two caps, the median line and the far values, in that order, so "
                  "the 5th line is the first median."),
        Case("draw_all_dots", "Fisher's iris: all 150 petal lengths as dots over boxes", "iris", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_boxes(x="Species", y="Petal.Length")
                 chart.draw_all_dots(x="Species", y="Petal.Length")
             """, """
                 {"dots": len(f["dots"]), "total of the values": sum(y for _, y in f["dots"]),
                  "dark grey dots": f["colours"][1].count("#333333ff")}
             """),
             parent=_library_chart("""
                 from matplotlib.figure import Figure
                 fig = Figure(figsize=(8, 6), layout="constrained")
                 ax = fig.subplots()
                 sns.boxplot(data, x="Species", y="Petal.Length", saturation=1, ax=ax)
                 sns.swarmplot(data, x="Species", y="Petal.Length", color="#333333", ax=ax)
             """, """
                 {"dots": len(f["dots"]), "total of the values": sum(y for _, y in f["dots"]),
                  "dark grey dots": f["colours"][1].count("#333333ff")}
             """), parent_label="seaborn swarmplot", parent_tolerance=1e-12,
             r="""
                 list(dots = length(Petal.Length), `total of the values` = sum(Petal.Length))
             """, r_tolerance=1e-12),
        Case("draw_violins", "Fisher's iris: each violin stops at the longest sepal of its species", "iris", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_violins(x="Species", y="Sepal.Length")
             """, """
                 {f"top of the {name} violin": max(v[1][:, 1]) for name, v in zip(["setosa", "versicolor", "virginica"],
                                                                                 f["shapes"])}
             """),
             published={"top of the setosa violin": (5.8, 1e-12, "exact"),
                        "top of the versicolor violin": (7.0, 1e-12, "exact"),
                        "top of the virginica violin": (7.9, 1e-12, "exact")},
             parent=_library_chart("""
                 fig, ax = plt.subplots()
                 sns.violinplot(data, x="Species", y="Sepal.Length", cut=0, saturation=1, ax=ax)
             """, """
                 {f"top of the {name} violin": max(v[1][:, 1]) for name, v in zip(["setosa", "versicolor", "virginica"],
                                                                                 f["shapes"])}
             """), parent_label="seaborn violinplot(cut=0)", parent_tolerance=1e-12,
             r="""
                 m <- tapply(Sepal.Length, Species, max)
                 list(`top of the setosa violin` = m[["setosa"]], `top of the versicolor violin` = m[["versicolor"]],
                      `top of the virginica violin` = m[["virginica"]])
             """, r_tolerance=1e-12,
             note="The longest sepals in Fisher's table are 5.8, 7.0 and 7.9 cm."),
        Case("show=", "mtcars: the median fuel use for 4, 6 and 8 cylinders", "mtcars", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_bars(x="cyl", y="mpg", show="median")
             """, """
                 {"4 cylinders": f["bars"][0][3], "6 cylinders": f["bars"][1][3], "8 cylinders": f["bars"][2][3]}
             """),
             parent=_library_chart("""
                 fig, ax = plt.subplots()
                 sns.barplot(data, x="cyl", y="mpg", estimator="median", errorbar=None, ax=ax)
             """, """
                 {"4 cylinders": f["bars"][0][3], "6 cylinders": f["bars"][1][3], "8 cylinders": f["bars"][2][3]}
             """), parent_label="seaborn barplot(estimator=\"median\")", parent_tolerance=1e-12,
             r="""
                 m <- tapply(mpg, cyl, median)
                 list(`4 cylinders` = m[["4"]], `6 cylinders` = m[["6"]], `8 cylinders` = m[["8"]])
             """, r_tolerance=1e-12),
        Case("error=", "mtcars: average fuel use with standard deviation bars", "mtcars", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_bars(x="cyl", y="mpg", error="standard deviation")
             """, """
                 {"top of the 4-cylinder bar": max(f["lines"][0][1]), "bottom of it": min(f["lines"][0][1])}
             """),
             parent=_library_chart("""
                 fig, ax = plt.subplots()
                 sns.barplot(data, x="cyl", y="mpg", errorbar="sd", capsize=0.1, ax=ax)
             """, """
                 {"top of the 4-cylinder bar": max(f["lines"][0][1]), "bottom of it": min(f["lines"][0][1])}
             """), parent_label="seaborn barplot(errorbar=\"sd\")", parent_tolerance=1e-12,
             r="""
                 m <- mpg[cyl == 4]
                 list(`top of the 4-cylinder bar` = mean(m) + sd(m), `bottom of it` = mean(m) - sd(m))
             """, r_tolerance=1e-12),
        Case("write_numbers_on_bars", "warpbreaks: the total breaks at each tension written on the bars", "warpbreaks",
             "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_bars(x="tension", y="breaks", show="total").write_numbers_on_bars()
             """, """
                 shown = [float(t.replace(",", "")) for t in f["texts"][1]]
                 {"numbers written": len(shown), "biggest": max(shown), "smallest": min(shown)}
             """),
             parent=_library_chart("""
                 fig, ax = plt.subplots()
                 sns.barplot(data, x="tension", y="breaks", estimator="sum", errorbar=None, ax=ax)
                 ax.bar_label(ax.containers[0], labels=[f"{v:,.0f}" for v in ax.containers[0].datavalues], padding=3)
             """, """
                 shown = [float(t.replace(",", "")) for t in f["texts"][1]]
                 {"numbers written": len(shown), "biggest": max(shown), "smallest": min(shown)}
             """), parent_label="matplotlib bar_label", parent_tolerance=0.0,
             r="""
                 s <- tapply(breaks, tension, sum)
                 list(`numbers written` = length(s), biggest = max(s), smallest = min(s))
             """, r_tolerance=0.0),
        Case("fit_line", "mtcars: the straight line of fuel use on weight", "mtcars", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_dots(x="wt", y="mpg").fit_line()
             """, """
                 {"line at the lightest car": f["lines"][0][1][0], "line at the heaviest car": f["lines"][0][1][-1]}
             """),
             parent=_library_chart("""
                 from scipy import stats
                 fig, ax = plt.subplots()
                 sns.scatterplot(data, x="wt", y="mpg", ax=ax)
                 fit = stats.linregress(data["wt"], data["mpg"])
                 xs = np.linspace(data["wt"].min(), data["wt"].max(), 200)
                 ax.plot(xs, fit.intercept + fit.slope * xs)
             """, """
                 {"line at the lightest car": f["lines"][0][1][0], "line at the heaviest car": f["lines"][0][1][-1]}
             """), parent_label="SciPy linregress", parent_tolerance=1e-12,
             r="""
                 p <- predict(lm(mpg ~ wt), data.frame(wt = range(wt)))
                 list(`line at the lightest car` = p[[1]], `line at the heaviest car` = p[[2]])
             """, r_tolerance=1e-10),
        Case("draw_qq_dots", "Michelson's 100 measurements of the speed of light against the normal curve",
             "NIST Michelso", "published",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_qq_dots("y")
             """, """
                 (x0, x1), (y0, y1) = f["lines"][0]
                 {"dots": len(f["dots"]), "slope of the line": (y1 - y0) / (x1 - x0), "smallest value": f["dots"][0][1]}
             """),
             parent=_library_chart("""
                 from scipy import stats
                 (theory, ordered), (slope, intercept, r) = stats.probplot(data["y"], dist="norm")
                 fig, ax = plt.subplots()
             """, """
                 {"dots": len(ordered), "slope of the line": slope, "smallest value": ordered[0]}
             """), parent_label="SciPy probplot", parent_tolerance=1e-12,
             r="""
                 list(dots = length(y), `smallest value` = min(y))
             """, r_tolerance=1e-12,
             note="R's qqnorm() puts the dots at slightly different places (Blom's, not Filliben's), so only the count "
                  "and the values themselves are checked against R."),
        Case("set_range_y", "mtcars: average fuel use on an axis from 0 to 40", "mtcars", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_bars(x="cyl", y="mpg").set_range_y(0, 40)
             """, """
                 {"bottom of the y axis": f["limits"][1][0], "top of the y axis": f["limits"][1][1]}
             """),
             published={"bottom of the y axis": (0, 0, "exact"), "top of the y axis": (40, 0, "exact")},
             parent=_library_chart(f"""
                 fig, ax = plt.subplots()
                 {bars_cyl}
                 ax.set_ylim(0, 40)
             """, """
                 {"bottom of the y axis": f["limits"][1][0], "top of the y axis": f["limits"][1][1]}
             """), parent_label="matplotlib set_ylim", parent_tolerance=0.0),
        Case("draw_line_at_y", "mtcars: a line at the average fuel use, 20.09 miles per gallon", "mtcars",
             "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_dots(x="wt", y="mpg")
                 chart.draw_line_at_y(20.090625, labelled="average")
             """, """
                 {"line at": f["lines"][0][1][0], "label written": float("average" in f["texts"][1])}
             """),
             parent=_library_chart("""
                 fig, ax = plt.subplots()
                 sns.scatterplot(data, x="wt", y="mpg", ax=ax)
                 ax.axhline(20.090625, color="grey", linestyle="--", linewidth=1.5)
                 ax.text(1.01, 20.090625, "average", transform=ax.get_yaxis_transform())
             """, """
                 {"line at": f["lines"][0][1][0], "label written": float("average" in f["texts"][1])}
             """), parent_label="matplotlib axhline", parent_tolerance=0.0,
             r="""
                 list(`line at` = mean(mpg))
             """, r_tolerance=1e-12),
        Case("shade_between_y", "mtcars: the middle half of the fuel use shaded (the quartiles 15.425 and 22.8)",
             "mtcars", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_dots(x="wt", y="mpg").shade_between_y(15.425, 22.8)
             """, """
                 {"bottom of the band": f["bars"][0][1], "height of the band": f["bars"][0][3],
                  "width (share of the chart)": f["bars"][0][2]}
             """),
             parent=_library_chart("""
                 fig, ax = plt.subplots()
                 sns.scatterplot(data, x="wt", y="mpg", ax=ax)
                 ax.axhspan(15.425, 22.8, color="grey", alpha=0.2, linewidth=0, zorder=0)
             """, """
                 {"bottom of the band": f["bars"][0][1], "height of the band": f["bars"][0][3],
                  "width (share of the chart)": f["bars"][0][2]}
             """), parent_label="matplotlib axhspan", parent_tolerance=1e-12,
             r="""
                 q <- quantile(mpg, c(0.25, 0.75))
                 list(`bottom of the band` = q[[1]], `height of the band` = q[[2]] - q[[1]])
             """, r_tolerance=1e-12),
        Case("use_log_scale_y", "warpbreaks: lines of the two wools on a log scale", "warpbreaks", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_lines(x="tension", y="breaks", colour="wool").use_log_scale_y()
             """, """
                 {"log scale": float(f["scales"][1] == "log"), "bottom of the y axis": f["limits"][1][0],
                  "top of the y axis": f["limits"][1][1]}
             """),
             parent=_library_chart(f"""
                 fig, ax = plt.subplots()
                 ax.set_yscale("log")
                 {lines_wool}
             """, """
                 {"log scale": float(f["scales"][1] == "log"), "bottom of the y axis": f["limits"][1][0],
                  "top of the y axis": f["limits"][1][1]}
             """), parent_label="matplotlib set_yscale(\"log\")", parent_tolerance=1e-12),
        Case("draw_line_at_x", "mtcars: a line at a weight of 3,500 lb", "mtcars", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_dots(x="wt", y="mpg").draw_line_at_x(3.5, labelled="3,500 lb")
             """, """
                 {"line at": f["lines"][0][0][0], "label written": float("3,500 lb" in f["texts"][1])}
             """),
             published={"line at": (3.5, 0, "exact")},
             parent=_library_chart("""
                 fig, ax = plt.subplots()
                 sns.scatterplot(data, x="wt", y="mpg", ax=ax)
                 ax.axvline(3.5, color="grey", linestyle="--", linewidth=1.5)
                 ax.text(3.5, 0.98, " 3,500 lb ", transform=ax.get_xaxis_transform(), rotation=90)
             """, """
                 {"line at": f["lines"][0][0][0], "label written": float("3,500 lb" in f["texts"][1])}
             """), parent_label="matplotlib axvline", parent_tolerance=0.0),
        Case("write_ticks_y_as", "birthwt: the share of low birth weights for each race, written as percents",
             "birthwt", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_bars(x="race", y="low").write_ticks_y_as("percent", out_of=1)
             """, """
                 shown = [t for t in f["ticks"][1] if t]
                 {"labels with %": sum(t.endswith("%") for t in shown), "labels": len(shown),
                  "race 1": f["bars"][0][3]}
             """),
             parent=_library_chart("""
                 from matplotlib import ticker
                 fig, ax = plt.subplots()
                 sns.barplot(data, x="race", y="low", errorbar=None, ax=ax)
                 ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))
             """, """
                 shown = [t for t in f["ticks"][1] if t]
                 {"labels with %": sum(t.endswith("%") for t in shown), "labels": len(shown),
                  "race 1": f["bars"][0][3]}
             """), parent_label="matplotlib PercentFormatter", parent_tolerance=1e-12,
             r="""
                 list(`race 1` = mean(low[race == 1]))
             """, r_tolerance=1e-12),
        Case("set_size", "mtcars: a chart 12 cm wide and 9 cm high", "mtcars", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_dots(x="wt", y="mpg").set_size(width=12, height=9, unit="cm")
             """, """
                 {"width (inches)": f["size"][0], "height (inches)": f["size"][1]}
             """),
             published={"width (inches)": (12 / 2.54, 1e-12, "exact"), "height (inches)": (9 / 2.54, 1e-12, "exact")},
             parent=_library_chart("""
                 fig, ax = plt.subplots(figsize=(12 / 2.54, 9 / 2.54))
                 sns.scatterplot(data, x="wt", y="mpg", ax=ax)
             """, """
                 {"width (inches)": f["size"][0], "height (inches)": f["size"][1]}
             """), parent_label="matplotlib figsize", parent_tolerance=1e-12,
             note="An inch is 2.54 cm."),
        Case("write_note", "mtcars: the lightest car named on the chart", "mtcars", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_dots(x="wt", y="mpg").write_note("Lotus Europa", x=1.513, y=30.4)
             """, """
                 {"note written": float("Lotus Europa" in f["texts"][1]), "dots": len(f["dots"])}
             """),
             parent=_library_chart("""
                 fig, ax = plt.subplots()
                 sns.scatterplot(data, x="wt", y="mpg", ax=ax)
                 ax.annotate("Lotus Europa", xy=(1.513, 30.4), xytext=(0, 4), textcoords="offset points")
             """, """
                 {"note written": float("Lotus Europa" in f["texts"][1]), "dots": len(f["dots"])}
             """), parent_label="matplotlib annotate", parent_tolerance=0.0),
        Case("draw_heatmap", "warpbreaks: the average breaks for each wool and tension as coloured cells",
             "warpbreaks", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_heatmap(x="tension", y="wool", value="breaks", with_numbers=True)
             """, """
                 cells = f["cells"][0][1]
                 {"cells": len(cells), "wool A, tension L": cells[0], "wool B, tension H": cells[5],
                  "numbers written": len(f["texts"][1])}
             """),
             parent=_library_chart("""
                 wide = data.pivot_table(index="wool", columns="tension", values="breaks", aggfunc="mean", sort=False)
                 fig, ax = plt.subplots()
                 sns.heatmap(wide, cmap="viridis", cbar=False, annot=True, fmt=".3g", ax=ax)
             """, """
                 cells = f["cells"][0][1]
                 {"cells": len(cells), "wool A, tension L": cells[0], "wool B, tension H": cells[5],
                  "numbers written": len(f["texts"][1])}
             """), parent_label="seaborn heatmap", parent_tolerance=1e-12,
             r="""
                 m <- tapply(breaks, list(wool, tension), mean)
                 list(cells = length(m), `wool A, tension L` = m["A", "L"], `wool B, tension H` = m["B", "H"])
             """, r_tolerance=1e-12),
        Case("draw_one_chart_for_each_group_in", "Fisher's iris: one small chart of petal against sepal length for "
             "each species", "iris", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_dots(x="Sepal.Length", y="Petal.Length")
                 chart.draw_one_chart_for_each_group_in("Species")
             """, """
                 {"panels": f["panels"], "dots in the first": f["every_panel"][0][4][0],
                  "dots in the last": f["every_panel"][2][4][0], "width (inches)": f["size"][0]}
             """),
             published={"panels": (3, 0, "exact"), "dots in the first": (50, 0, "exact"),
                        "dots in the last": (50, 0, "exact")},
             parent=_library_chart("""
                 fig = plt.figure(figsize=(13, 4.5), layout="constrained")
                 axes = fig.subplots(1, 3, sharex=True, sharey=True)
                 for ax, (name, rows) in zip(axes, data.groupby("Species", sort=False)):
                     sns.scatterplot(rows, x="Sepal.Length", y="Petal.Length", ax=ax)
             """, """
                 {"panels": f["panels"], "dots in the first": f["every_panel"][0][4][0],
                  "dots in the last": f["every_panel"][2][4][0], "width (inches)": f["size"][0]}
             """, axes="axes[0]"), parent_label="matplotlib subplots(sharex, sharey)", parent_tolerance=0.0),
        Case("sdata.put_side_by_side", "mtcars: bars and boxes of fuel use side by side, on the same y range",
             "mtcars", "real data",
             ours=_ours_chart("""
                 a = sdata.chart(data).draw_bars(x="cyl", y="mpg")
                 b = sdata.chart(data).draw_boxes(x="cyl", y="mpg")
                 chart = sdata.put_side_by_side(a, b, same_y=True)
             """, """
                 {"panels": len(f["every_panel"]), "width (inches)": f["size"][0], "top of the y axis": f["limits"][1][1],
                  "4 cylinders": f["every_panel"][0][5][1][0][3]}
             """),
             parent=_library_chart(f"""
                 fig = plt.figure(figsize=(12, 4.5), layout="constrained")
                 ax, ax2 = (cell.add_subplot() for cell in fig.subfigures(1, 2))
                 {bars_cyl}
                 sns.boxplot(data, x="cyl", y="mpg", saturation=1, ax=ax2)
                 ends = ax.get_ylim() + ax2.get_ylim()
                 for one in (ax, ax2):
                     one.set_ylim(min(ends), max(ends))
             """, """
                 {"panels": len(f["every_panel"]), "width (inches)": f["size"][0], "top of the y axis": f["limits"][1][1],
                  "4 cylinders": f["every_panel"][0][5][1][0][3]}
             """), parent_label="matplotlib subfigures", parent_tolerance=1e-12,
             r="""
                 list(`4 cylinders` = mean(mpg[cyl == 4]))
             """, r_tolerance=1e-12),
        Case("sdata.put_one_above_other", "Fisher's iris: dots above a histogram", "iris", "real data",
             ours=_ours_chart("""
                 a = sdata.chart(data).draw_dots(x="Sepal.Length", y="Petal.Length")
                 b = sdata.chart(data).draw_histogram(x="Sepal.Length")
                 chart = sdata.put_one_above_other(a, b)
             """, """
                 {"panels": len(f["every_panel"]), "height (inches)": f["size"][1], "dots": f["every_panel"][0][4][0],
                  "bars": f["every_panel"][1][5][0]}
             """),
             parent=_library_chart("""
                 fig = plt.figure(figsize=(6, 9), layout="constrained")
                 ax, ax2 = (cell.add_subplot() for cell in fig.subfigures(2, 1))
                 sns.scatterplot(data, x="Sepal.Length", y="Petal.Length", ax=ax)
                 sns.histplot(data, x="Sepal.Length", bins=10, ax=ax2)
             """, """
                 {"panels": len(f["every_panel"]), "height (inches)": f["size"][1], "dots": f["every_panel"][0][4][0],
                  "bars": f["every_panel"][1][5][0]}
             """), parent_label="matplotlib subfigures", parent_tolerance=0.0),
        Case("sdata.put_in_rows_and_columns", "Fisher's iris: histograms of the four measurements, two in a row",
             "iris", "real data",
             ours=_ours_chart("""
                 names = ["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]
                 charts = [sdata.chart(data).draw_histogram(x=name) for name in names]
                 chart = sdata.put_in_rows_and_columns(*charts, per_row=2)
             """, """
                 {"panels": len(f["every_panel"]), "width (inches)": f["size"][0], "height (inches)": f["size"][1],
                  "flowers in the last histogram": sum(b[3] for b in f["every_panel"][3][5][1])}
             """),
             published={"panels": (4, 0, "exact"), "flowers in the last histogram": (150, 0, "exact")},
             parent=_library_chart("""
                 names = ["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]
                 fig = plt.figure(figsize=(12, 9), layout="constrained")
                 axes = [cell.add_subplot() for cell in fig.subfigures(2, 2).flat]
                 for one, name in zip(axes, names):
                     sns.histplot(data, x=name, bins=10, ax=one)
             """, """
                 {"panels": len(f["every_panel"]), "width (inches)": f["size"][0], "height (inches)": f["size"][1],
                  "flowers in the last histogram": sum(b[3] for b in f["every_panel"][3][5][1])}
             """, axes="axes[0]"), parent_label="matplotlib subfigures", parent_tolerance=0.0),
        Case("sdata.draw_all_pairs", "Fisher's iris: every measurement against every other, by species", "iris",
             "real data",
             ours=_ours_chart("""
                 chart = sdata.draw_all_pairs(data, colour="Species")
             """, """
                 {"panels and diagonal axes": f["panels"], "dots in the second panel": f["every_panel"][1][4][0],
                  "panels with dots": sum(p[4][0] > 0 for p in f["every_panel"])}
             """),
             published={"panels and diagonal axes": (20, 0, "exact"), "dots in the second panel": (150, 0, "exact"),
                        "panels with dots": (12, 0, "exact")},
             parent=_library_chart("""
                 cols = ["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]
                 fig, axes = plt.subplots(4, 4, sharex="col", sharey="row")
                 for i, y in enumerate(cols):
                     for j, x in enumerate(cols):
                         if i == j:
                             sns.kdeplot(data, x=x, hue="Species", fill=True, common_norm=False, legend=False,
                                         ax=axes[i, j].twinx())
                         else:
                             sns.scatterplot(data, x=x, y=y, hue="Species", legend=False, ax=axes[i, j])
             """, """
                 {"panels and diagonal axes": f["panels"], "dots in the second panel": f["every_panel"][1][4][0],
                  "panels with dots": sum(p[4][0] > 0 for p in f["every_panel"])}
             """, axes="axes[0, 0]"), parent_label="seaborn scatterplot and kdeplot", parent_tolerance=0.0,
             note="4 columns make 16 panels; each of the 4 on the diagonal also has a second y-axis for its curves."),
        Case("add_second_y", "mtcars: fuel use as a line and horsepower as bars on a second y-axis", "mtcars",
             "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_lines(x="cyl", y="mpg").add_second_y("hp", drawn_as="bars")
             """, """
                 bars = f["every_panel"][1][5][1]
                 {"4 cylinders": bars[0][3], "6 cylinders": bars[1][3], "8 cylinders": bars[2][3]}
             """),
             parent=_library_chart("""
                 fig, ax = plt.subplots()
                 sns.lineplot(data, x="cyl", y="mpg", errorbar=None, ax=ax)
                 hp = data.groupby("cyl")["hp"].mean()
                 ax.twinx().bar(hp.index, hp, width=0.8 * 2, alpha=0.6)
             """, """
                 bars = f["every_panel"][1][5][1]
                 {"4 cylinders": bars[0][3], "6 cylinders": bars[1][3], "8 cylinders": bars[2][3]}
             """), parent_label="matplotlib twinx and bar", parent_tolerance=1e-12,
             r="""
                 m <- tapply(hp, cyl, mean)
                 list(`4 cylinders` = m[["4"]], `6 cylinders` = m[["6"]], `8 cylinders` = m[["8"]])
             """, r_tolerance=1e-12),
        Case("animate", "mtcars: average fuel use by cylinders, one picture for each number of gears (the last: 5)",
             "mtcars", "real data",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_bars(x="cyl", y="mpg").animate(over="gear")
             """, """
                 {"4 cylinders": f["bars"][0][3], "8 cylinders": f["bars"][2][3],
                  "named by its gear": float(f["labels"][2] == "gear: 5")}
             """),
             parent=_library_chart("""
                 fig, ax = plt.subplots()
                 sns.barplot(data[data["gear"] == 5], x="cyl", y="mpg", errorbar=None, ax=ax)
                 ax.set_title("gear: 5")
             """, """
                 {"4 cylinders": f["bars"][0][3], "8 cylinders": f["bars"][2][3],
                  "named by its gear": float(f["labels"][2] == "gear: 5")}
             """), parent_label="seaborn barplot of the last frame", parent_tolerance=1e-12,
             r="""
                 five <- gear == 5
                 list(`4 cylinders` = mean(mpg[five & cyl == 4]), `8 cylinders` = mean(mpg[five & cyl == 8]))
             """, r_tolerance=1e-12,
             note="Shown as a still picture, an animated chart is its last frame."),
        Case("fit_formula", "Puromycin (treated): the Michaelis-Menten curve through the dots", "Puromycin (treated)",
             "published",
             ours=_ours_chart("""
                 chart = sdata.chart(data).draw_dots(x="conc", y="rate")
                 chart.fit_formula("rate = Vm * conc / (K + conc)", start={"Vm": 200, "K": 0.1})
             """, """
                 xs, ys = f["lines"][0]
                 {"curve at the highest concentration": ys[-1], "curve at the lowest": ys[0]}
             """),
             parent=_library_chart("""
                 from scipy import optimize
                 (vm, k), _ = optimize.curve_fit(lambda c, vm, k: vm * c / (k + c), data["conc"], data["rate"],
                                                 p0=[200, 0.1], method="lm", maxfev=20000, xtol=1e-12, ftol=1e-12)
                 fig, ax = plt.subplots()
                 xs = np.linspace(data["conc"].min(), data["conc"].max(), 200)
                 ax.plot(xs, vm * xs / (k + xs))
             """, """
                 xs, ys = f["lines"][0]
                 {"curve at the highest concentration": ys[-1], "curve at the lowest": ys[0]}
             """), parent_label="SciPy curve_fit", parent_tolerance=1e-7,
             r="""
                 m <- nls(rate ~ Vm * conc / (K + conc), start = list(Vm = 200, K = 0.1), control = list(tol = 1e-8))
                 p <- predict(m, data.frame(conc = range(conc)))
                 list(`curve at the highest concentration` = p[[2]], `curve at the lowest` = p[[1]])
             """, r_tolerance=1e-6),
        # ---- statistics words of U-batch 2
        Case("table.find_trend_of", "the level of Lake Huron, 1875-1972: Mann-Kendall test and Sen's slope",
             "Lake Huron", "real data",
             ours="""
                 r = sdata.table(data).find_trend_of("level", sorted_by="year")
                 {"slope per year": r.get_cell_at(row=1, column="slope"),
                  "slope 95 % CI low": r.get_cell_at(row=1, column="95 % CI low"),
                  "z": r.get_cell_at(row=1, column="z"), "p-value": r.get_cell_at(row=1, column="p-value")}
             """,
             parent="""
                 from scipy import stats
                 s = stats.theilslopes(data["level"], data["year"], alpha=0.95)
                 {"slope per year": s.slope, "slope 95 % CI low": s.low_slope}
             """, parent_label="SciPy theilslopes", parent_tolerance=1e-10,
             r="""
                 m <- trend::mk.test(level)
                 s <- trend::sens.slope(level)
                 list(`slope per year` = unname(s$estimates), `slope 95 % CI low` = s$conf.int[1],
                      z = unname(m$statistic), `p-value` = m$p.value)
             """, r_packages=("trend",), r_tolerance=1e-9, ours_r=("trend",),
             note="The years run 1875 to 1972 without a gap, so the slope per year equals R's slope per reading."),
        Case("table.find_each_peak_that", "the air passengers, 1949-1960: the peaks at least 6 months apart",
             "AirPassengers", "real data",
             ours="""
                 r = sdata.table(data).find_each_peak_that("passengers", apart=6)
                 {"peaks": r.count_rows(), "first peak (row)": r.get_cell_at(row=1, column="position"),
                  "highest peak": r.get_column("value").find_biggest()}
             """,
             parent="""
                 from scipy import signal
                 peaks, _ = signal.find_peaks(data["passengers"].to_numpy(dtype=float), distance=6)
                 {"peaks": len(peaks), "first peak (row)": peaks[0] + 1,
                  "highest peak": data["passengers"].to_numpy()[peaks].max()}
             """, parent_label="SciPy find_peaks(distance=6)", parent_tolerance=0.0,
             published={"highest peak": (622, 0, "Box & Jenkins (1976): July 1960")}),
        Case("table.add_nmds", "the dune meadows (vegan): an NMDS map of the 20 plots", "dune (vegan)", "real data",
             ours="""
                 species = [c for c in data.columns if c not in ("Management", "A1")]
                 t = sdata.table(data).add_nmds(columns=species)
                 {"NMDS1 of plot 1": t.get_cell_at(row=1, column="NMDS1"),
                  "NMDS2 of plot 1": t.get_cell_at(row=1, column="NMDS2"),
                  "NMDS1 of plot 20": t.get_cell_at(row=20, column="NMDS1")}
             """,
             r="""
                 e <- new.env(); utils::data("dune", package = "vegan", envir = e)
                 set.seed(1)
                 fit <- vegan::metaMDS(vegan::vegdist(e$dune, method = "bray"), k = 2, try = 20, trymax = 100,
                                       autotransform = FALSE, trace = 0)
                 list(`NMDS1 of plot 1` = fit$points[1, 1], `NMDS2 of plot 1` = fit$points[1, 2],
                      `NMDS1 of plot 20` = fit$points[20, 1])
             """, r_packages=("vegan",), r_tolerance=1e-9, ours_r=("vegan",)),
        Case("table.fit_formula", "Puromycin (treated): Vm and K of the Michaelis-Menten formula", "Puromycin (treated)",
             "published",
             ours="""
                 r = sdata.table(data).fit_formula("rate = Vm * conc / (K + conc)", start={"Vm": 200, "K": 0.1})
                 {"Vm": r.get_cell_at(row=1, column="Vm"), "K": r.get_cell_at(row=1, column="K"),
                  "standard error of K": r.get_cell_at(row=1, column="standard error of K")}
             """,
             published={"Vm": (212.7, 0.05, "Bates & Watts (1988)"), "K": (0.06412, 0.000005, "Bates & Watts (1988)")},
             parent="""
                 from scipy import optimize
                 (vm, k), cov = optimize.curve_fit(lambda c, vm, k: vm * c / (k + c), data["conc"], data["rate"],
                                                   p0=[200, 0.1], method="lm", maxfev=20000, xtol=1e-12, ftol=1e-12)
                 {"Vm": vm, "K": k, "standard error of K": np.sqrt(cov[1, 1])}
             """, parent_label="SciPy curve_fit (Levenberg-Marquardt)", parent_tolerance=1e-7,
             r="""
                 m <- summary(nls(rate ~ Vm * conc / (K + conc), start = list(Vm = 200, K = 0.1), control = list(tol = 1e-8)))$coefficients
                 list(Vm = m["Vm", 1], K = m["K", 1], `standard error of K` = m["K", 2])
             """, r_tolerance=1e-6),
        Case("table.compare_matched_columns", "rounding first base: 22 players, three routes (Friedman test)",
             "rounding first base", "published",
             ours="""
                 r = sdata.table(data).compare_matched_columns("round_out", "narrow_angle", "wide_angle")
                 {"chi-square": r.get_cell_at(row=1, column="statistic"),
                  "degrees of freedom": r.get_cell_at(row=1, column="degrees of freedom"),
                  "p-value": r.get_cell_at(row=1, column="p-value")}
             """,
             published={"chi-square": (11.143, 0.0005, "R friedman.test help (Hollander & Wolfe 1973)"),
                        "p-value": (0.003805, 0.0000005, "R friedman.test help (Hollander & Wolfe 1973)")},
             parent="""
                 from scipy import stats
                 res = stats.friedmanchisquare(data["round_out"], data["narrow_angle"], data["wide_angle"])
                 {"chi-square": res.statistic, "degrees of freedom": 2, "p-value": res.pvalue}
             """, parent_label="SciPy friedmanchisquare", parent_tolerance=1e-12,
             r="""
                 f <- friedman.test(cbind(round_out, narrow_angle, wide_angle))
                 list(`chi-square` = unname(f$statistic), `degrees of freedom` = unname(f$parameter),
                      `p-value` = f$p.value)
             """, r_tolerance=1e-10),
        Case("table.show_rows_that_pull_model", "mtcars: the cars that pull the line of fuel use on weight and "
             "horsepower the most", "mtcars", "real data",
             ours=_printed('sdata.table(data).show_rows_that_pull_model("mpg", using=["wt", "hp"])', """
                 first = lines[0].split()
                 {"rows above 4 / n": int(first[1]), "the row that pulls most": int(lines[1].split()[1].rstrip(":")),
                  "its Cook's distance": float(lines[1].split("Cook's distance ")[1].split(",")[0])}
             """),
             parent="""
                 import statsmodels.formula.api as smf
                 s = smf.ols("mpg ~ wt + hp", data=data).fit().get_influence().summary_frame()
                 {"rows above 4 / n": int((s["cooks_d"] > 4 / len(data)).sum()),
                  "the row that pulls most": int(s["cooks_d"].to_numpy().argmax()) + 1,
                  "its Cook's distance": float(f'{s["cooks_d"].max():.3g}')}
             """, parent_label="statsmodels OLSInfluence (Cook's distance to the 3 digits printed)",
             parent_tolerance=0.0,
             r="""
                 d <- cooks.distance(lm(mpg ~ wt + hp))
                 list(`rows above 4 / n` = sum(d > 4 / length(d)), `the row that pulls most` = which.max(d)[[1]],
                      `its Cook's distance` = signif(max(d), 3))
             """, r_tolerance=0.0),
    ]


def add_to(namespace) -> None:
    """Add the underneath-phase cases to cases.py."""
    namespace["CASES"].extend(_cases(namespace["Case"]))
