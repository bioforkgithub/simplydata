"""The reliability study for phase U3, batch 3: the table words that got their "same underneath" box, each run on
real, published data and compared with pandas (or SciPy) and, where it is plain base R, with R.

cases_underneath.py loads this file and adds the cases. The datasets are the study's own (validation/data,
README.md): Fisher's iris, mtcars, warpbreaks, NHANES (mice), the AirPassengers series and Student's sleep data.
The simplydata side reads its results only with simplydata words (get_column, get_cell_at, get_row, count_rows ...);
the words that show something and give nothing back (show, show_last_rows) are checked on what they print.
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


def cases(Case):
    return [
        # ---- looking at a table
        Case("table.show_last_rows", "the last 3 of Fisher's 150 iris flowers, numbered 148 to 150", "iris",
             "real data",
             ours=_printed('sdata.table(data).show_last_rows(3)', """
                 rows = [line.split() for line in lines[1:]]
                 {"rows shown": len(rows), "first row number": int(rows[0][0]),
                  "sepal length total": sum(float(r[1]) for r in rows)}
             """),
             parent="""
                 last = data.tail(3)
                 {"rows shown": len(last), "first row number": len(data) - 2,
                  "sepal length total": last["Sepal.Length"].sum()}
             """, parent_label="pandas tail", parent_tolerance=1e-12,
             r="""
                 n <- length(Sepal.Length)
                 list(`rows shown` = 3, `first row number` = n - 2, `sepal length total` = sum(tail(Sepal.Length, 3)))
             """, r_tolerance=1e-12),
        Case("table.show", "all 144 months of AirPassengers shown, numbered from 1", "AirPassengers", "real data",
             ours=_printed('sdata.table(data).show()', """
                 rows = [line.split() for line in lines[1:] if line.split()[0].isdigit()]
                 {"rows shown": len(rows), "last row number": int(rows[-1][0]),
                  "total passengers": sum(int(r[2]) for r in rows)}
             """),
             parent="""
                 {"rows shown": len(data), "last row number": len(data), "total passengers": data["passengers"].sum()}
             """, parent_label="pandas (every row)", parent_tolerance=0.0,
             r="""
                 list(`rows shown` = length(passengers), `total passengers` = sum(passengers))
             """, r_tolerance=0.0),
        Case("table.get_column_names", "the 12 column names of mtcars", "mtcars", "real data",
             ours="""
                 names = sdata.table(data).get_column_names()
                 {"columns": len(names), "mpg is second": float(names[1] == "mpg")}
             """,
             parent="""
                 {"columns": data.shape[1], "mpg is second": float(list(data.columns)[1] == "mpg")}
             """, parent_label="pandas columns", parent_tolerance=0.0),
        Case("table.get_column", "NHANES body mass index taken out as numbers, with its 9 empty cells",
             "nhanes (mice)", "real data",
             ours="""
                 bmi = sdata.table(data).get_column("bmi")
                 {"values": bmi.count(), "empty": bmi.count_empty_numbers(), "total": bmi.find_total()}
             """,
             parent="""
                 x = data["bmi"].to_numpy(dtype=float)
                 {"values": len(x), "empty": int(np.isnan(x).sum()), "total": np.nansum(x)}
             """, parent_label="pandas to_numpy", parent_tolerance=1e-12,
             r="""
                 list(values = length(bmi), empty = sum(is.na(bmi)), total = sum(bmi, na.rm = TRUE))
             """, r_tolerance=1e-12),
        Case("table.get_row", "the first NHANES person: an age and three empty cells", "nhanes (mice)", "real data",
             ours="""
                 row = sdata.table(data).get_row(1)
                 {"age group": row["age"], "empty cells": sum(v is None for v in row.values())}
             """,
             parent="""
                 row = data.iloc[0]
                 {"age group": row["age"], "empty cells": int(row.isna().sum())}
             """, parent_label="pandas iloc[0]", parent_tolerance=0.0,
             r="""
                 list(`age group` = age[1], `empty cells` = sum(is.na(c(bmi[1], hyp[1], chl[1]))))
             """, r_tolerance=0.0),
        Case("table.get_cell_at", "the horsepower of the third car in mtcars (Datsun 710)", "mtcars", "published",
             ours="""
                 {"hp": sdata.table(data).get_cell_at(row=3, column="hp")}
             """,
             published={"hp": (93, 0.0, "Henderson & Velleman (1981)")},
             parent="""
                 {"hp": data["hp"].iloc[2]}
             """, parent_label="pandas iloc[2]", parent_tolerance=0.0,
             r="""
                 list(hp = hp[3])
             """, r_tolerance=0.0),
        # ---- choosing columns and rows
        Case("table.remove_columns", "mtcars without the car names", "mtcars", "real data",
             ours="""
                 t = sdata.table(data).remove_columns("model")
                 {"columns": len(t.get_column_names()), "total mpg": t.get_column("mpg").find_total()}
             """,
             parent="""
                 t = data.drop(columns=["model"])
                 {"columns": t.shape[1], "total mpg": t["mpg"].sum()}
             """, parent_label="pandas drop(columns=)", parent_tolerance=1e-12),
        Case("table.keep_columns_by_position", "columns 2 to 4 of mtcars (mpg, cyl, disp)", "mtcars", "real data",
             ours="""
                 t = sdata.table(data).keep_columns_by_position(2, to=4)
                 {"columns": len(t.get_column_names()), "total disp": t.get_column("disp").find_total()}
             """,
             parent="""
                 t = data.iloc[:, 1:4]
                 {"columns": t.shape[1], "total disp": t["disp"].sum()}
             """, parent_label="pandas iloc[:, 1:4]", parent_tolerance=1e-12,
             r="""
                 list(columns = 3, `total disp` = sum(disp))
             """, r_tolerance=1e-12),
        Case("table.remove_columns_by_position", "mtcars without its first column (the car names)", "mtcars",
             "real data",
             ours="""
                 names = sdata.table(data).remove_columns_by_position(1).get_column_names()
                 {"columns": len(names), "mpg is first": float(names[0] == "mpg")}
             """,
             parent="""
                 t = data.drop(columns=data.columns[0])
                 {"columns": t.shape[1], "mpg is first": float(t.columns[0] == "mpg")}
             """, parent_label="pandas drop(columns=)", parent_tolerance=0.0),
        Case("table.remove_rows_where", "NHANES: people with a body mass index below 25 removed (empty cells stay)",
             "nhanes (mice)", "real data",
             ours="""
                 bmi = sdata.table(data).remove_rows_where("bmi", is_below=25).get_column("bmi")
                 {"rows left": bmi.count(), "empty left": bmi.count_empty_numbers(), "total": bmi.find_total()}
             """,
             parent="""
                 left = data[~(data["bmi"] < 25)]
                 {"rows left": len(left), "empty left": int(left["bmi"].isna().sum()), "total": left["bmi"].sum()}
             """, parent_label="pandas boolean indexing", parent_tolerance=1e-12,
             r="""
                 keep <- is.na(bmi) | bmi >= 25
                 list(`rows left` = sum(keep), `empty left` = sum(is.na(bmi)), total = sum(bmi[keep], na.rm = TRUE))
             """, r_tolerance=1e-12),
        Case("table.keep_first_rows", "the first 10 cars of mtcars", "mtcars", "real data",
             ours="""
                 mpg = sdata.table(data).keep_first_rows(10).get_column("mpg")
                 {"rows": mpg.count(), "total mpg": mpg.find_total()}
             """,
             parent="""
                 {"rows": len(data.head(10)), "total mpg": data["mpg"].head(10).sum()}
             """, parent_label="pandas head", parent_tolerance=1e-12,
             r="""
                 list(rows = 10, `total mpg` = sum(head(mpg, 10)))
             """, r_tolerance=1e-12),
        Case("table.keep_last_rows", "the last 10 cars of mtcars", "mtcars", "real data",
             ours="""
                 mpg = sdata.table(data).keep_last_rows(10).get_column("mpg")
                 {"rows": mpg.count(), "total mpg": mpg.find_total()}
             """,
             parent="""
                 {"rows": len(data.tail(10)), "total mpg": data["mpg"].tail(10).sum()}
             """, parent_label="pandas tail", parent_tolerance=1e-12,
             r="""
                 list(rows = 10, `total mpg` = sum(tail(mpg, 10)))
             """, r_tolerance=1e-12),
        Case("table.remove_rows_by_position", "mtcars without its first and last car", "mtcars", "real data",
             ours="""
                 mpg = sdata.table(data).remove_rows_by_position([1, 32]).get_column("mpg")
                 {"rows": mpg.count(), "total mpg": mpg.find_total()}
             """,
             parent="""
                 left = data.drop(index=data.index[[0, 31]])
                 {"rows": len(left), "total mpg": left["mpg"].sum()}
             """, parent_label="pandas drop(index=)", parent_tolerance=1e-12,
             r="""
                 list(rows = length(mpg[-c(1, 32)]), `total mpg` = sum(mpg[-c(1, 32)]))
             """, r_tolerance=1e-12),
        Case("table.reverse_rows", "AirPassengers turned upside down: the last month first", "AirPassengers",
             "real data",
             ours="""
                 t = sdata.table(data).reverse_rows()
                 {"first": t.get_cell_at(row=1, column="passengers"), "last": t.get_cell_at(row=144, column="passengers")}
             """,
             parent="""
                 back = data.iloc[::-1]
                 {"first": back["passengers"].iloc[0], "last": back["passengers"].iloc[-1]}
             """, parent_label="pandas iloc[::-1]", parent_tolerance=0.0,
             r="""
                 list(first = rev(passengers)[1], last = rev(passengers)[144])
             """, r_tolerance=0.0),
        Case("table.remove_duplicate_rows", "mtcars: the first car of each number of cylinders", "mtcars", "real data",
             ours="""
                 mpg = sdata.table(data).remove_duplicate_rows(columns=["cyl"]).get_column("mpg")
                 {"rows": mpg.count(), "total mpg": mpg.find_total()}
             """,
             parent="""
                 kept = data.drop_duplicates(subset=["cyl"], keep="first")
                 {"rows": len(kept), "total mpg": kept["mpg"].sum()}
             """, parent_label="pandas drop_duplicates", parent_tolerance=1e-12,
             r="""
                 list(rows = sum(!duplicated(cyl)), `total mpg` = sum(mpg[!duplicated(cyl)]))
             """, r_tolerance=1e-12),
        Case("table.keep_biggest_rows", "mtcars: the 3 most powerful cars for each number of cylinders", "mtcars",
             "real data",
             ours="""
                 t = sdata.table(data).keep_biggest_rows(3, by="hp", for_each_group_in="cyl")
                 {"rows": t.count_rows(), "total hp": t.get_column("hp").find_total(),
                  "first hp": t.get_cell_at(row=1, column="hp")}
             """,
             parent="""
                 top = data.sort_values("hp", ascending=False, kind="stable").groupby("cyl").head(3)
                 top = top.sort_values("cyl", kind="stable")
                 {"rows": len(top), "total hp": top["hp"].sum(), "first hp": top["hp"].iloc[0]}
             """, parent_label="pandas sort_values (stable) and groupby().head()", parent_tolerance=0.0,
             r="""
                 top <- tapply(hp, cyl, function(v) head(sort(v, decreasing = TRUE), 3))
                 list(`total hp` = sum(unlist(top)), `first hp` = top[["4"]][1])
             """, r_tolerance=0.0),
        Case("table.keep_smallest_rows", "mtcars: the 3 thirstiest cars for each number of cylinders", "mtcars",
             "real data",
             ours="""
                 t = sdata.table(data).keep_smallest_rows(3, by="mpg", for_each_group_in="cyl")
                 {"rows": t.count_rows(), "total mpg": t.get_column("mpg").find_total(),
                  "first mpg": t.get_cell_at(row=1, column="mpg")}
             """,
             parent="""
                 low = data.sort_values("mpg", kind="stable").groupby("cyl").head(3)
                 low = low.sort_values("cyl", kind="stable")
                 {"rows": len(low), "total mpg": low["mpg"].sum(), "first mpg": low["mpg"].iloc[0]}
             """, parent_label="pandas sort_values (stable) and groupby().head()", parent_tolerance=1e-12,
             r="""
                 low <- tapply(mpg, cyl, function(v) head(sort(v), 3))
                 list(`total mpg` = sum(unlist(low)), `first mpg` = low[["4"]][1])
             """, r_tolerance=1e-12),
        Case("table.remove_rows_with_outliers", "mtcars horsepower: Tukey's outliers within each number of cylinders "
             "removed", "mtcars", "real data",
             ours="""
                 hp = sdata.table(data).remove_rows_with_outliers("hp", for_each_group_in="cyl").get_column("hp")
                 {"rows left": hp.count(), "total hp": hp.find_total()}
             """,
             parent="""
                 g = data.groupby("cyl")["hp"]
                 q1, q3 = g.transform("quantile", 0.25), g.transform("quantile", 0.75)
                 left = data[~((data["hp"] < q1 - 1.5 * (q3 - q1)) | (data["hp"] > q3 + 1.5 * (q3 - q1)))]
                 {"rows left": len(left), "total hp": left["hp"].sum()}
             """, parent_label="pandas quantile (linear) and Tukey's rule", parent_tolerance=0.0,
             r="""
                 keep <- ave(hp, cyl, FUN = function(v) {
                   q <- quantile(v, c(0.25, 0.75)); f <- 1.5 * diff(q)
                   as.numeric(v >= q[1] - f & v <= q[2] + f)
                 })
                 list(`rows left` = sum(keep == 1), `total hp` = sum(hp[keep == 1]))
             """, r_tolerance=0.0),
        Case("table.remove_rows_with_empty_cells_in", "NHANES: the people without a body mass index removed",
             "nhanes (mice)", "real data",
             ours="""
                 bmi = sdata.table(data).remove_rows_with_empty_cells_in("bmi").get_column("bmi")
                 {"rows left": bmi.count(), "total": bmi.find_total()}
             """,
             parent="""
                 left = data.dropna(subset=["bmi"])
                 {"rows left": len(left), "total": left["bmi"].sum()}
             """, parent_label="pandas dropna(subset=)", parent_tolerance=1e-12,
             r="""
                 list(`rows left` = sum(!is.na(bmi)), total = sum(bmi, na.rm = TRUE))
             """, r_tolerance=1e-12),
        Case("table.add_is_empty_column", "NHANES: which people have no cholesterol value", "nhanes (mice)",
             "real data",
             ours="""
                 flags = sdata.table(data).add_is_empty_column("chl_was_empty", from_column="chl").get_column("chl_was_empty")
                 {"empty": sum(bool(v) for v in flags), "rows": len(flags)}
             """,
             parent="""
                 {"empty": int(data["chl"].isna().sum()), "rows": len(data)}
             """, parent_label="pandas isna", parent_tolerance=0.0,
             r="""
                 list(empty = sum(is.na(chl)), rows = length(chl))
             """, r_tolerance=0.0),
        # ---- changing what is in a column
        Case("table.turn_into_text", "mtcars miles per gallon written as text", "mtcars", "real data",
             ours="""
                 text = sdata.table(data).turn_into_text("mpg").get_column("mpg")
                 {"cells reading 21.0": text.count("21.0"), "cells reading 10.4": text.count("10.4")}
             """,
             parent="""
                 text = data["mpg"].astype(str)
                 {"cells reading 21.0": int((text == "21.0").sum()), "cells reading 10.4": int((text == "10.4").sum())}
             """, parent_label="pandas astype(str)", parent_tolerance=0.0),
        Case("table.turn_into_dates", "the 144 months of AirPassengers read as dates", "AirPassengers", "real data",
             ours="""
                 t = sdata.table(data).turn_into_dates("month")
                 first, last = t.get_cell_at(row=1, column="month"), t.get_cell_at(row=144, column="month")
                 {"first year": first.year, "last year": last.year, "last month": last.month}
             """,
             parent="""
                 d = pd.to_datetime(data["month"], format="%Y-%m-%d")
                 {"first year": d.iloc[0].year, "last year": d.iloc[-1].year, "last month": d.iloc[-1].month}
             """, parent_label="pandas to_datetime", parent_tolerance=0.0,
             r="""
                 d <- as.POSIXlt(as.Date(month))
                 list(`first year` = d$year[1] + 1900, `last year` = d$year[144] + 1900, `last month` = d$mon[144] + 1)
             """, r_tolerance=0.0),
        Case("table.turn_into_lowercase", "warpbreaks: the wool types written in small letters", "warpbreaks",
             "real data",
             ours="""
                 wool = sdata.table(data).turn_into_lowercase("wool").get_column("wool")
                 {"a": wool.count("a"), "b": wool.count("b")}
             """,
             parent="""
                 w = data["wool"].str.lower()
                 {"a": int((w == "a").sum()), "b": int((w == "b").sum())}
             """, parent_label="pandas str.lower", parent_tolerance=0.0,
             r="""
                 w <- tolower(wool)
                 list(a = sum(w == "a"), b = sum(w == "b"))
             """, r_tolerance=0.0),
        Case("table.turn_into_uppercase", "iris: the species written in capital letters", "iris", "real data",
             ours="""
                 species = sdata.table(data).turn_into_uppercase("Species").get_column("Species")
                 {"SETOSA": species.count("SETOSA"), "VIRGINICA": species.count("VIRGINICA")}
             """,
             parent="""
                 s = data["Species"].str.upper()
                 {"SETOSA": int((s == "SETOSA").sum()), "VIRGINICA": int((s == "VIRGINICA").sum())}
             """, parent_label="pandas str.upper", parent_tolerance=0.0,
             r="""
                 s <- toupper(Species)
                 list(SETOSA = sum(s == "SETOSA"), VIRGINICA = sum(s == "VIRGINICA"))
             """, r_tolerance=0.0),
        Case("table.round_numbers_in", "mtcars weights rounded to 1 decimal", "mtcars", "real data",
             ours="""
                 wt = sdata.table(data).round_numbers_in("wt", 1).get_column("wt")
                 {"total": wt.find_total(), "first": wt.get_number_at(1)}
             """,
             parent="""
                 r = data["wt"].round(1)
                 {"total": r.sum(), "first": r.iloc[0]}
             """, parent_label="pandas round", parent_tolerance=1e-12),
        Case("table.change_column", "mtcars miles per gallon changed into kilometres per litre", "mtcars",
             "real data",
             ours="""
                 kml = sdata.table(data).change_column("mpg", "mpg * 0.425144").get_column("mpg")
                 {"total": kml.find_total(), "cars": kml.count()}
             """,
             parent="""
                 {"total": (data["mpg"] * 0.425144).sum(), "cars": len(data)}
             """, parent_label="pandas multiplication", parent_tolerance=1e-12,
             r="""
                 list(total = sum(mpg * 0.425144))
             """, r_tolerance=1e-12),
        Case("table.add_rank_column", "mtcars cars ranked by fuel use, ties sharing the best place", "mtcars",
             "real data",
             ours="""
                 place = sdata.table(data).add_rank_column("place", from_column="mpg").get_column("place")
                 {"first car": place.get_number_at(1), "sum of places": place.find_total()}
             """,
             parent="""
                 r = data["mpg"].rank(method="min", ascending=False)
                 {"first car": r.iloc[0], "sum of places": r.sum()}
             """, parent_label="pandas rank(method=\"min\")", parent_tolerance=0.0,
             r="""
                 r <- rank(-mpg, ties.method = "min")
                 list(`first car` = r[1], `sum of places` = sum(r))
             """, r_tolerance=0.0),
        Case("table.add_column_with_part_of_date", "AirPassengers: the weekday of the first day of each month (1 is "
             "Monday)", "AirPassengers", "real data",
             ours="""
                 t = sdata.table(data).turn_into_dates("month")
                 day = t.add_column_with_part_of_date("weekday", from_column="month", part="weekday").get_column("weekday")
                 {"total": day.find_total(), "first": day.get_number_at(1)}
             """,
             parent="""
                 d = pd.to_datetime(data["month"]).dt.dayofweek + 1
                 {"total": d.sum(), "first": d.iloc[0]}
             """, parent_label="pandas dt.dayofweek + 1", parent_tolerance=0.0,
             r="""
                 w <- (as.POSIXlt(as.Date(month))$wday + 6) %% 7 + 1
                 list(total = sum(w), first = w[1])
             """, r_tolerance=0.0),
        Case("table.add_column_with_part_of_text", "mtcars: the make of each car, the text before the first space",
             "mtcars", "real data",
             ours="""
                 make = sdata.table(data).add_column_with_part_of_text("make", from_column="model", before=" ").get_column("make")
                 {"Merc": make.count("Merc"), "Toyota": make.count("Toyota"), "empty": make.count(None)}
             """,
             parent="""
                 make = data["model"].str.extract(r"(?s)^(.*?) ", expand=False).str.strip()
                 {"Merc": int((make == "Merc").sum()), "Toyota": int((make == "Toyota").sum()),
                  "empty": int(make.isna().sum())}
             """, parent_label="pandas str.extract", parent_tolerance=0.0,
             r="""
                 has <- grepl(" ", model); make <- ifelse(has, sub(" .*$", "", model), NA)
                 list(Merc = sum(make == "Merc", na.rm = TRUE), Toyota = sum(make == "Toyota", na.rm = TRUE),
                      empty = sum(is.na(make)))
             """, r_tolerance=0.0),
        Case("table.split_column", "mtcars car names split into the make and the rest", "mtcars", "real data",
             ours="""
                 t = sdata.table(data).split_column("model", separator=" ", into=["make", "type"])
                 make, kind = t.get_column("make"), t.get_column("type")
                 {"Merc": make.count("Merc"), "no type": kind.count(None), "columns": len(t.get_column_names())}
             """,
             parent="""
                 parts = data["model"].str.split(" ", n=1, expand=True)
                 {"Merc": int((parts[0] == "Merc").sum()), "no type": int(parts[1].isna().sum()),
                  "columns": data.shape[1] + 1}
             """, parent_label="pandas str.split(n=1)", parent_tolerance=0.0),
        Case("table.replace_text_in", "mtcars: Merc written out as Mercedes in the car names", "mtcars", "real data",
             ours="""
                 names = sdata.table(data).replace_text_in("model", "Merc", with_value="Mercedes").get_column("model")
                 {"with Mercedes": sum("Mercedes" in n for n in names), "Mercedes 240D": names.count("Mercedes 240D")}
             """,
             parent="""
                 n = data["model"].str.replace("Merc", "Mercedes", regex=False)
                 {"with Mercedes": int(n.str.contains("Mercedes", regex=False).sum()),
                  "Mercedes 240D": int((n == "Mercedes 240D").sum())}
             """, parent_label="pandas str.replace(regex=False)", parent_tolerance=0.0,
             r="""
                 n <- gsub("Merc", "Mercedes", model, fixed = TRUE)
                 list(`with Mercedes` = sum(grepl("Mercedes", n, fixed = TRUE)), `Mercedes 240D` = sum(n == "Mercedes 240D"))
             """, r_tolerance=0.0),
        # ---- working along the rows
        Case("table.add_previous_value_column", "AirPassengers: each month beside the month before", "AirPassengers",
             "real data",
             ours="""
                 before = sdata.table(data).add_previous_value_column("last_month", from_column="passengers",
                                                                      sorted_by="month").get_column("last_month")
                 {"empty": before.count_empty_numbers(), "total": before.find_total(), "row 2": before.get_number_at(2)}
             """,
             parent="""
                 b = data.sort_values("month", kind="stable")["passengers"].shift(1)
                 {"empty": int(b.isna().sum()), "total": b.sum(), "row 2": b.iloc[1]}
             """, parent_label="pandas shift(1)", parent_tolerance=0.0,
             r="""
                 list(empty = 1, total = sum(head(passengers, -1)), `row 2` = passengers[1])
             """, r_tolerance=0.0),
        Case("table.add_change_column", "AirPassengers: the change from the month before, in percent",
             "AirPassengers", "real data",
             ours="""
                 g = sdata.table(data).add_change_column("growth", from_column="passengers", in_percent=True,
                                                         sorted_by="month").get_column("growth")
                 {"last": g.get_number_at(144), "total": g.find_total(), "empty": g.count_empty_numbers()}
             """,
             parent="""
                 p = data.sort_values("month", kind="stable")["passengers"]
                 g = (p - p.shift(1)) / p.shift(1) * 100
                 {"last": g.iloc[-1], "total": g.sum(), "empty": int(g.isna().sum())}
             """, parent_label="pandas shift(1)", parent_tolerance=1e-12,
             r="""
                 g <- diff(passengers) / head(passengers, -1) * 100
                 list(last = g[length(g)], total = sum(g), empty = 1)
             """, r_tolerance=1e-12),
        # ---- summaries
        Case("table.find_smallest_of", "the shortest sepal of each iris species", "iris", "real data",
             ours="""
                 s = sdata.table(data).find_smallest_of("Sepal.Length", for_each_group_in="Species")
                 {s.get_cell_at(row=i, column="Species"): s.get_cell_at(row=i, column="smallest of Sepal.Length")
                  for i in (1, 2, 3)}
             """,
             parent="""
                 m = data.groupby("Species")["Sepal.Length"].min()
                 {k: m[k] for k in m.index}
             """, parent_label="pandas groupby().min()", parent_tolerance=0.0,
             r="""
                 m <- tapply(Sepal.Length, Species, min)
                 list(setosa = m[["setosa"]], versicolor = m[["versicolor"]], virginica = m[["virginica"]])
             """, r_tolerance=0.0),
        Case("table.find_biggest_of", "the most powerful car in mtcars (Maserati Bora, 335 hp)", "mtcars", "published",
             ours="""
                 {"hp": sdata.table(data).find_biggest_of("hp")}
             """,
             published={"hp": (335, 0.0, "Henderson & Velleman (1981)")},
             parent="""
                 {"hp": data["hp"].max()}
             """, parent_label="pandas max", parent_tolerance=0.0,
             r="""
                 list(hp = max(hp))
             """, r_tolerance=0.0),
        Case("table.find_standard_deviation_of", "the spread of petal length in each iris species (n - 1)", "iris",
             "real data",
             ours="""
                 s = sdata.table(data).find_standard_deviation_of("Petal.Length", for_each_group_in="Species")
                 {s.get_cell_at(row=i, column="Species"): s.get_cell_at(row=i, column="standard deviation of Petal.Length")
                  for i in (1, 2, 3)}
             """,
             parent="""
                 sd = data.groupby("Species")["Petal.Length"].std(ddof=1)
                 {k: sd[k] for k in sd.index}
             """, parent_label="pandas groupby().std(ddof=1)", parent_tolerance=1e-12,
             r="""
                 s <- tapply(Petal.Length, Species, sd)
                 list(setosa = s[["setosa"]], versicolor = s[["versicolor"]], virginica = s[["virginica"]])
             """, r_tolerance=1e-12),
        Case("table.count_different_values_in", "NHANES: how many different body mass index values (empty cells not "
             "counted)", "nhanes (mice)", "real data",
             ours="""
                 {"different values": sdata.table(data).count_different_values_in("bmi")}
             """,
             parent="""
                 {"different values": data["bmi"].nunique()}
             """, parent_label="pandas nunique", parent_tolerance=0.0,
             r="""
                 list(`different values` = length(unique(na.omit(bmi))))
             """, r_tolerance=0.0),
        Case("table.find_most_common_of", "the most common number of cylinders in mtcars", "mtcars", "real data",
             ours="""
                 {"most common": sdata.table(data).find_most_common_of("cyl")}
             """,
             parent="""
                 {"most common": data["cyl"].mode().iloc[0]}
             """, parent_label="pandas mode", parent_tolerance=0.0,
             r="""
                 counts <- table(cyl)
                 list(`most common` = as.numeric(names(counts)[which.max(counts)]))
             """, r_tolerance=0.0),
        Case("table.find_interval_of", "mtcars miles per gallon: the average with a 95 % BCa bootstrap interval",
             "mtcars", "real data",
             ours="""
                 s = sdata.table(data).find_interval_of("mpg", "average")
                 {"average": s.get_cell_at(row=1, column="average of mpg"),
                  "low": s.get_cell_at(row=1, column="average of mpg 95 % CI low"),
                  "high": s.get_cell_at(row=1, column="average of mpg 95 % CI high")}
             """,
             parent="""
                 from scipy import stats
                 x = data["mpg"].to_numpy(dtype=float)
                 ci = stats.bootstrap((x,), np.mean, n_resamples=9999, method="BCa", vectorized=False,
                                      rng=np.random.default_rng(1)).confidence_interval
                 {"average": x.mean(), "low": ci.low, "high": ci.high}
             """, parent_label="SciPy stats.bootstrap (BCa, 9999 resamples, seed 1)", parent_tolerance=1e-12,
             note="R boot::boot.ci() draws other random rows, so only SciPy, with the same seed, gives the same "
                  "interval."),
        # ---- stacking and reshaping
        Case("table.add_rows_from", "Fisher's iris data put under itself", "iris", "real data",
             ours="""
                 width = sdata.table(data).add_rows_from(data).get_column("Petal.Width")
                 {"rows": width.count(), "total petal width": width.find_total()}
             """,
             parent="""
                 both = pd.concat([data, data], ignore_index=True)
                 {"rows": len(both), "total petal width": both["Petal.Width"].sum()}
             """, parent_label="pandas concat", parent_tolerance=1e-12,
             r="""
                 both <- rbind(data.frame(w = Petal.Width), data.frame(w = Petal.Width))
                 list(rows = nrow(both), `total petal width` = sum(both$w))
             """, r_tolerance=1e-12),
        Case("table.turn_columns_into_rows", "iris sepal length and width turned into rows", "iris", "real data",
             ours="""
                 t = sdata.table(data).turn_columns_into_rows(["Sepal.Length", "Sepal.Width"])
                 value = t.get_column("value")
                 {"rows": value.count(), "total": value.find_total(), "columns": len(t.get_column_names())}
             """,
             parent="""
                 long = data.melt(id_vars=["Petal.Length", "Petal.Width", "Species"],
                                  value_vars=["Sepal.Length", "Sepal.Width"], var_name="column", value_name="value")
                 {"rows": len(long), "total": long["value"].sum(), "columns": long.shape[1]}
             """, parent_label="pandas melt", parent_tolerance=1e-12,
             r="""
                 list(rows = 2 * length(Sepal.Length), total = sum(Sepal.Length) + sum(Sepal.Width))
             """, r_tolerance=1e-12),
        Case("table.turn_rows_into_columns", "Student's sleep data: one row for each patient, a column for each drug",
             "Student's sleep data", "published",
             ours="""
                 t = sdata.table(data).turn_rows_into_columns(names_from="group", values_from="extra")
                 {"patients": t.count_rows(), "average drug 2": t.get_column("drug 2").find_total() / t.count_rows(),
                  "patient 1 drug 1": t.get_cell_at(row=1, column="drug 1")}
             """,
             published={"average drug 2": (2.33, 0.005, "Student (1908)")},
             parent="""
                 wide = data.pivot(index="ID", columns="group", values="extra")
                 {"patients": len(wide), "average drug 2": wide["drug 2"].mean(), "patient 1 drug 1": wide["drug 1"].iloc[0]}
             """, parent_label="pandas pivot", parent_tolerance=1e-12,
             r="""
                 list(`average drug 2` = mean(extra[group == "drug 2"]), `patient 1 drug 1` = extra[group == "drug 1"][1])
             """, r_tolerance=1e-12),
    ]
