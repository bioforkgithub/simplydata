"""The reliability study for the "same underneath" entries added in phases U1 to U3: each word that got a box in the
manual is also run on real, published data and compared with the package underneath (pandas, Polars, NumPy, SciPy,
statsmodels, seaborn) and, where it is plain base R, with R.

cases.py loads this file at its end and calls add_to(), which adds the cases below to its own CASES. The datasets
are the study's own (validation/data, README.md): Fisher's iris, mtcars, warpbreaks, birthwt, NHANES (mice), the
AirPassengers series, NIST's Michelson and Norris data, Student's sleep data and the BCG trials (read from R
metadat, as the combining-studies cases do). Words that show something and give nothing back (show_first_rows,
describe_columns, show_rows_with_outliers) are checked on what they print: the printed numbers are read back.

The chart cases read what a chart drew with chart.get_numbers_drawn(), and show_rows_that_pull_model's case reads the
table the word gives back. A survey design's degrees of freedom have no word yet (its name waits for approval).
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
                  for k, m in {"average": "average", "sd": "standard deviation", "count": "count"}.items()}
             """,
             parent="""
                 g = data.groupby("Species")["Sepal.Length"].agg(["mean", "std", "count"])
                 {f"{k} {sp}": g.loc[sp, m] for sp in ("setosa", "virginica")
                  for k, m in {"average": "mean", "sd": "std", "count": "count"}.items()}
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
                 z = data.groupby("Species")["Sepal.Length"].transform(stats.zscore, ddof=1, nan_policy="omit")
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
                 import os
                 import tempfile
                 with tempfile.TemporaryDirectory() as folder:
                     data.to_csv(os.path.join(folder, "iris.csv"), index=False)
                     t = pd.read_csv(os.path.join(folder, "iris.csv"), sep=None, engine="python")
                 {"rows": len(t), "total petal width": t["Petal.Width"].sum()}
             """, parent_label="pandas read_csv(sep=None)", parent_tolerance=1e-12),
        Case("sdata.get_example", "the practice table bcg has the shape of the published trials in R metadat (dat.bcg)",
             "BCG trials (metadat)", "real data",
             ours="""
                 bcg = sdata.table(sdata.get_example("bcg"))
                 {"trials": bcg.get_column("vaccinated").count(),
                  "kinds of allocation": len(set(bcg.get_column("allocation"))),
                  "earliest year": bcg.get_column("year").find_smallest(),
                  "latest year": bcg.get_column("year").find_biggest()}
             """,
             parent="""
                 {"trials": len(data), "kinds of allocation": data["alloc"].nunique(),
                  "earliest year": data["year"].min(), "latest year": data["year"].max()}
             """, parent_label="R metadat dat.bcg (the published trials)", parent_tolerance=0.0,
             note="Since 2026-11-22 the practice table bcg is made up (DATA_LICENSES.md): it keeps the published "
                  "trials' columns, number of trials, kinds of allocation and span of years, but not their counts. "
                  "The counts themselves are checked against metadat in the combine_studies cases."),
        Case("sdata.chart", "the 36 Norris calibration points on a new chart", "NIST Norris", "real data",
             ours="""
                 drawn = sdata.chart(data).draw_dots(x="x", y="y").get_numbers_drawn()
                 {"dots": drawn.get_column("y").count(), "sum of y": drawn.get_column("y").find_total()}
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
                 t = sdata.table(data).keep_rows_where("group", is_equal_to="drug 2")
                 drawn = t.start_chart().draw_bars(x="group", y="extra").get_numbers_drawn()
                 {"bar": drawn.get_cell_at(row=1, column="y"), "bars": drawn.get_column("y").count()}
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
    ]


def add_to(namespace) -> None:
    """Add the underneath-phase cases to cases.py."""
    namespace["CASES"].extend(_cases(namespace["Case"]))
