"""The reliability study for the tables phase (batches 1 to 3, PR #59): the table words and options that got their
"same underneath" box there, each run on real, published data.

cases_underneath.py loads this file and adds the cases. Each word is compared with the library its box names:
pandas, and Polars in a second case where the box shows Polars too (simplydata then gets a Polars table, so the Polars
side of the word is checked as well), DuckDB for SQL, and base R where R does the same thing in a few plain lines (as
in cases_underneath_tables.py). The datasets are the study's own (validation/README.md): Fisher's iris, mtcars,
warpbreaks, NHANES (mice), AirPassengers, Seatbelts, the ICU arrival times (circular) and Hackshaw's passive smoking
studies (metadat).

The simplydata side reads its results only with simplydata words (get_column, get_cell_at, get_column_names,
count_rows ...); the words that print and give nothing back (show_differences_from, show_duplicate_rows,
show_rows_with_empty_cells_in) are checked on what they print. Text results (column names, the order of rows, dates
written as text) are compared one by one: each value is part of a name ("row 3: Datsun 710"), so a value that differs
is a name missing on one side, and the check fails.
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


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(p).strip("\n") for p in parts if p and p.strip())


def _both(Case, word, title, dataset, kind, *, ours, pandas, pandas_label, polars, polars_label, setup="",
          r="", r_tolerance=0.0, tolerance=0.0, option="", published=None, note=""):
    """Two cases: simplydata on a pandas table against pandas (and R), and on a Polars table against Polars.

    setup (pandas) prepares the input for both sides; then `source` is the table simplydata gets: the pandas table
    itself, or the same table as Polars (pl.from_pandas). The Polars side starts from the same Polars table."""
    pandas_case = Case(word, title, dataset, kind,
                       ours=_code(setup, "source = data", ours), published=published or {},
                       parent=_code(setup, pandas), parent_label=pandas_label, parent_tolerance=tolerance,
                       r=r, r_tolerance=r_tolerance, option=option, note=note)
    polars_case = Case(word, title + " (a Polars table)", dataset, kind,
                       ours=_code(setup, "import polars as pl", "source = pl.from_pandas(data)", ours),
                       parent=_code(setup, "import polars as pl", "df = pl.from_pandas(data)", polars),
                       parent_label=polars_label, parent_tolerance=tolerance, option=option)
    return [pandas_case, polars_case]


def cases(Case):
    out = []

    def both(*args, **kwargs):
        out.extend(_both(Case, *args, **kwargs))

    # ---------------------------------------------------------------- SQL (DuckDB)
    out.append(Case(
        "sdata.run_sql", "mtcars saved as a CSV file and summed up by DuckDB: cars, average mpg and the most "
        "horsepower for each number of cylinders", "mtcars", "real data",
        ours="""
            import os
            import tempfile
            with tempfile.TemporaryDirectory() as folder:
                cars = os.path.join(folder, "mtcars.csv").replace(os.sep, "/")
                data.to_csv(cars, index=False)
                t = sdata.run_sql(f"SELECT cyl, count(*) AS cars, avg(mpg) AS mpg, max(hp) AS hp FROM '{cars}' "
                                  "GROUP BY cyl ORDER BY cyl")
            found = {}
            for i in range(1, t.count_rows() + 1):
                c = t.get_cell_at(row=i, column="cyl")
                found.update({f"{c} cylinders: cars": t.get_cell_at(row=i, column="cars"),
                              f"{c} cylinders: average mpg": t.get_cell_at(row=i, column="mpg"),
                              f"{c} cylinders: most hp": t.get_cell_at(row=i, column="hp")})
            found
        """,
        parent="""
            import os
            import tempfile
            import duckdb
            with tempfile.TemporaryDirectory() as folder:
                cars = os.path.join(folder, "mtcars.csv").replace(os.sep, "/")
                data.to_csv(cars, index=False)
                con = duckdb.connect(config={"autoload_known_extensions": False,
                                             "autoinstall_known_extensions": False})
                t = con.sql(f"SELECT cyl, count(*) AS cars, avg(mpg) AS mpg, max(hp) AS hp FROM '{cars}' "
                            "GROUP BY cyl ORDER BY cyl").df()
                con.close()
            found = {}
            for _, row in t.iterrows():
                c = int(row["cyl"])
                found.update({f"{c} cylinders: cars": row["cars"], f"{c} cylinders: average mpg": row["mpg"],
                              f"{c} cylinders: most hp": row["hp"]})
            found
        """, parent_label="DuckDB (the same SELECT on the same file)", parent_tolerance=1e-12,
        r="""
            n <- table(cyl); m <- tapply(mpg, cyl, mean); h <- tapply(hp, cyl, max)
            list(`4 cylinders: cars` = n[["4"]], `6 cylinders: cars` = n[["6"]], `8 cylinders: cars` = n[["8"]],
                 `4 cylinders: average mpg` = m[["4"]], `6 cylinders: average mpg` = m[["6"]],
                 `8 cylinders: average mpg` = m[["8"]], `4 cylinders: most hp` = h[["4"]],
                 `6 cylinders: most hp` = h[["6"]], `8 cylinders: most hp` = h[["8"]])
        """, r_tolerance=1e-12))
    for polars in (False, True):
        out.append(Case(
            "table.run_sql", "iris: the average sepal length and the flowers of each species, by SQL"
            + (" (a Polars table)" if polars else ""), "iris", "real data",
            ours=_code("import polars as pl" if polars else "",
                       "source = pl.from_pandas(data)" if polars else "source = data", """
                t = sdata.table(source).run_sql('SELECT Species, avg("Sepal.Length") AS sepal, count(*) AS n '
                                                'FROM data GROUP BY Species ORDER BY Species')
                found = {}
                for i in range(1, t.count_rows() + 1):
                    s = t.get_cell_at(row=i, column="Species")
                    found.update({f"{s}: average sepal length": t.get_cell_at(row=i, column="sepal"),
                                  f"{s}: flowers": t.get_cell_at(row=i, column="n")})
                found
            """),
            parent=_code("import polars as pl" if polars else "",
                         "df = pl.from_pandas(data)" if polars else "df = data", """
                import duckdb
                con = duckdb.connect(config={"autoload_known_extensions": False, "enable_external_access": False})
                con.register("data", df)
                t = con.sql('SELECT Species, avg("Sepal.Length") AS sepal, count(*) AS n '
                            'FROM data GROUP BY Species ORDER BY Species').df()
                con.close()
                found = {}
                for _, row in t.iterrows():
                    found.update({f"{row['Species']}: average sepal length": row["sepal"],
                                  f"{row['Species']}: flowers": row["n"]})
                found
            """), parent_label="DuckDB (register, then the same SELECT)", parent_tolerance=1e-12,
            r="" if polars else """
                m <- tapply(Sepal.Length, Species, mean); n <- table(Species)
                list(`setosa: average sepal length` = m[["setosa"]], `versicolor: average sepal length` = m[["versicolor"]],
                     `virginica: average sepal length` = m[["virginica"]], `setosa: flowers` = n[["setosa"]],
                     `versicolor: flowers` = n[["versicolor"]], `virginica: flowers` = n[["virginica"]])
            """, r_tolerance=1e-12))

    # ---------------------------------------------------------------- new columns
    both("table.add_column", "AirPassengers: whole weeks from January 1949 to the start of each month",
         "AirPassengers", "real data", option="counted_in=",
         setup='data = data.assign(start="1949-01-01")',
         ours="""
             t = sdata.table(source)
             t.turn_into_dates("month")
             t.turn_into_dates("start")
             t.add_column("weeks", by_subtracting=["month", "start"], counted_in="weeks")
             w = t.get_column("weeks")
             {"total weeks": w.find_total(), "February": w.get_number_at(2), "last month": w.get_number_at(144)}
         """,
         pandas="""
             w = np.trunc((pd.to_datetime(data["month"]) - pd.to_datetime(data["start"])) / pd.Timedelta(weeks=1))
             {"total weeks": w.sum(), "February": w.iloc[1], "last month": w.iloc[-1]}
         """, pandas_label="pandas (end - start) / pd.Timedelta(weeks=1), whole weeks",
         polars="""
             d = df.with_columns(pl.col("month", "start").str.to_date())
             w = d.select(((pl.col("month") - pl.col("start")).dt.total_days() // 7).alias("w"))["w"]
             {"total weeks": w.sum(), "February": w[1], "last month": w[-1]}
         """, polars_label="Polars (end - start).dt.total_days() // 7",
         r="""
             w <- trunc(as.numeric(difftime(as.Date(month), as.Date("1949-01-01"), units = "weeks")))
             list(`total weeks` = sum(w), February = w[2], `last month` = w[144])
         """)
    both("table.add_group_column", "mtcars miles per gallon in four equal groups (quarters)", "mtcars", "real data",
         option="into_equal_groups=",
         ours="""
             t = sdata.table(source).add_group_column("quarter", from_column="mpg", into_equal_groups=4)
             q = [int(v) for v in t.get_column("quarter")]
             {**{f"cars in quarter {k}": q.count(k) for k in (1, 2, 3, 4)},
              "quarter of each car (sum of row x quarter)": sum(i * v for i, v in enumerate(q, 1))}
         """,
         pandas="""
             q = [int(v) for v in pd.qcut(data["mpg"], 4, labels=False) + 1]
             {**{f"cars in quarter {k}": q.count(k) for k in (1, 2, 3, 4)},
              "quarter of each car (sum of row x quarter)": sum(i * v for i, v in enumerate(q, 1))}
         """, pandas_label="pandas qcut(4)",
         polars="""
             q = df.select(pl.col("mpg").qcut(4, labels=["1", "2", "3", "4"]).cast(pl.String).cast(pl.Int64))["mpg"]
             q = q.to_list()
             {**{f"cars in quarter {k}": q.count(k) for k in (1, 2, 3, 4)},
              "quarter of each car (sum of row x quarter)": sum(i * v for i, v in enumerate(q, 1))}
         """, polars_label="Polars qcut(4)",
         r="""
             q <- cut(mpg, quantile(mpg, 0:4 / 4), include.lowest = TRUE, labels = FALSE)
             list(`cars in quarter 1` = sum(q == 1), `cars in quarter 2` = sum(q == 2), `cars in quarter 3` = sum(q == 3),
                  `cars in quarter 4` = sum(q == 4),
                  `quarter of each car (sum of row x quarter)` = sum(seq_along(q) * q))
         """)
    both("table.add_missing_combinations_of", "mtcars: the one missing pair of cylinders and gears (8 cylinders, 4 "
         "gears) added as a row", "mtcars", "real data",
         ours="""
             t = sdata.table(source).add_missing_combinations_of("cyl", "gear")
             mpg = t.get_column("mpg")
             empty_row = [i for i in range(1, t.count_rows() + 1) if t.get_cell_at(row=i, column="mpg") is None][0]
             {"rows": t.count_rows(), "empty mpg": mpg.count_empty_numbers(), "row of the new pair": empty_row,
              "its cylinders": t.get_cell_at(row=empty_row, column="cyl"),
              "its gears": t.get_cell_at(row=empty_row, column="gear")}
         """,
         pandas="""
             keys = ["cyl", "gear"]
             grid = pd.MultiIndex.from_product([data[k].dropna().unique() for k in keys], names=keys)
             found = grid.to_frame(index=False).merge(data[keys].drop_duplicates(), how="left", indicator=True)
             missing = found[found["_merge"] == "left_only"].drop(columns="_merge")
             t = pd.concat([data, missing]).sort_values(keys, kind="stable", na_position="last")
             at = int(np.flatnonzero(t["mpg"].isna().to_numpy())[0])
             {"rows": len(t), "empty mpg": int(t["mpg"].isna().sum()), "row of the new pair": at + 1,
              "its cylinders": t["cyl"].iloc[at], "its gears": t["gear"].iloc[at]}
         """, pandas_label="pandas MultiIndex.from_product, merge(indicator=True), concat, sort_values (stable)",
         polars="""
             keys = ["cyl", "gear"]
             grid = df.select(keys[0]).drop_nulls().unique().join(df.select(keys[1]).drop_nulls().unique(), how="cross")
             missing = grid.join(df.select(keys).unique(), on=keys, how="anti")
             t = pl.concat([df, missing], how="diagonal").sort(keys, maintain_order=True, nulls_last=True)
             at = t.with_row_index().filter(pl.col("mpg").is_null())["index"][0]
             {"rows": t.height, "empty mpg": t["mpg"].null_count(), "row of the new pair": at + 1,
              "its cylinders": t["cyl"][at], "its gears": t["gear"][at]}
         """, polars_label="Polars join(how=\"cross\"), join(how=\"anti\"), concat, sort",
         r="""
             grid <- expand.grid(cyl = unique(cyl), gear = unique(gear))
             have <- paste(cyl, gear)
             new <- grid[!paste(grid$cyl, grid$gear) %in% have, ]
             all_cyl <- c(cyl, new$cyl); all_gear <- c(gear, new$gear); all_mpg <- c(mpg, rep(NA, nrow(new)))
             o <- order(all_cyl, all_gear)
             at <- which(is.na(all_mpg[o]))
             list(rows = length(o), `empty mpg` = sum(is.na(all_mpg)), `row of the new pair` = at,
                  `its cylinders` = all_cyl[o][at], `its gears` = all_gear[o][at])
         """)
    both("table.add_rank_column", "mtcars: each car's place for fuel use within its number of cylinders, ties "
         "sharing the average place", "mtcars", "real data", option="when_tied=",
         ours="""
             t = sdata.table(source).add_rank_column("place", from_column="mpg", for_each_group_in="cyl",
                                                     when_tied="share the average place")
             p = t.get_column("place")
             {"sum of places": p.find_total(), "Mazda RX4": p.get_number_at(1), "Mazda RX4 Wag": p.get_number_at(2),
              "sum of row x place": sum(i * p.get_number_at(i) for i in range(1, 33))}
         """,
         pandas="""
             p = data.groupby("cyl")["mpg"].rank(method="average", ascending=False)
             {"sum of places": p.sum(), "Mazda RX4": p.iloc[0], "Mazda RX4 Wag": p.iloc[1],
              "sum of row x place": sum(i * v for i, v in enumerate(p, 1))}
         """, pandas_label="pandas groupby().rank(method=\"average\")",
         polars="""
             p = df.select(pl.col("mpg").rank("average", descending=True).over("cyl"))["mpg"]
             {"sum of places": p.sum(), "Mazda RX4": p[0], "Mazda RX4 Wag": p[1],
              "sum of row x place": sum(i * v for i, v in enumerate(p, 1))}
         """, polars_label="Polars rank(\"average\").over()",
         r="""
             p <- ave(-mpg, cyl, FUN = rank)
             list(`sum of places` = sum(p), `Mazda RX4` = p[1], `Mazda RX4 Wag` = p[2],
                  `sum of row x place` = sum(seq_along(p) * p))
         """)
    both("table.add_row_number_column", "mtcars: the cars numbered from the least powerful within each number of "
         "cylinders (ties keep the table's order)", "mtcars", "real data",
         ours="""
             t = sdata.table(source).add_row_number_column("number", for_each_group_in="cyl", sorted_by="hp")
             n = t.get_column("number")
             {"biggest number": n.find_biggest(), "sum of row x number": sum(i * n.get_number_at(i) for i in range(1, 33))}
         """,
         pandas="""
             ordered = data.sort_values("hp", kind="stable")
             n = (ordered.groupby("cyl", dropna=False).cumcount() + 1).sort_index()
             {"biggest number": n.max(), "sum of row x number": sum(i * v for i, v in enumerate(n, 1))}
         """, pandas_label="pandas sort_values (stable), groupby().cumcount() + 1",
         polars="""
             n = df.select(pl.int_range(1, pl.len() + 1).over("cyl", order_by="hp").alias("n"))["n"]
             {"biggest number": n.max(), "sum of row x number": sum(i * v for i, v in enumerate(n, 1))}
         """, polars_label="Polars int_range(1, len() + 1).over(order_by=)",
         r="""
             n <- integer(length(hp))
             for (g in unique(cyl)) { i <- which(cyl == g); i <- i[order(hp[i])]; n[i] <- seq_along(i) }
             list(`biggest number` = max(n), `sum of row x number` = sum(seq_along(n) * n))
         """)
    both("table.add_row_summary_column", "iris: the average of the four measurements of each flower", "iris",
         "real data",
         ours="""
             columns = ["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]
             a = sdata.table(source).add_row_summary_column("average", columns=columns, show="average").get_column("average")
             {"total": a.find_total(), "first flower": a.get_number_at(1), "last flower": a.get_number_at(150)}
         """,
         pandas="""
             a = data[["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]].mean(axis=1)
             {"total": a.sum(), "first flower": a.iloc[0], "last flower": a.iloc[-1]}
         """, pandas_label="pandas mean(axis=1)", tolerance=1e-12,
         polars="""
             a = df.select(pl.mean_horizontal("Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"))
             a = a.to_series()
             {"total": a.sum(), "first flower": a[0], "last flower": a[-1]}
         """, polars_label="Polars mean_horizontal",
         r="""
             a <- rowMeans(cbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width))
             list(total = sum(a), `first flower` = a[1], `last flower` = a[150])
         """, r_tolerance=1e-12)
    both("table.add_running_column", "Seatbelts: drivers killed in Great Britain so far each year, month by month",
         "Seatbelts", "real data",
         ours="""
             s = sdata.table(source).add_running_column("so_far", from_column="DriversKilled", show="total",
                                                        for_each_group_in="year", sorted_by="month").get_column("so_far")
             {"total": s.find_total(), "December 1969": s.get_number_at(12), "December 1984": s.get_number_at(192),
              "January 1970": s.get_number_at(13)}
         """,
         pandas="""
             ordered = data.sort_values("month", kind="stable")
             s = ordered.groupby("year", dropna=False)["DriversKilled"].cumsum().sort_index()
             {"total": s.sum(), "December 1969": s.iloc[11], "December 1984": s.iloc[191], "January 1970": s.iloc[12]}
         """, pandas_label="pandas sort_values (stable), groupby().cumsum()",
         polars="""
             s = df.select(pl.col("DriversKilled").cum_sum().over("year", order_by="month"))["DriversKilled"]
             {"total": s.sum(), "December 1969": s[11], "December 1984": s[191], "January 1970": s[12]}
         """, polars_label="Polars cum_sum().over(order_by=)",
         r="""
             s <- ave(DriversKilled, year, FUN = cumsum)
             list(total = sum(s), `December 1969` = s[12], `December 1984` = s[192], `January 1970` = s[13])
         """)
    both("table.add_zeros_in_front_of", "Seatbelts: the month of the year written with two digits (01 to 12)",
         "Seatbelts", "real data",
         ours="""
             t = sdata.table(source)
             t.turn_into_text("month_of_year")
             t.add_zeros_in_front_of("month_of_year", to_length=2)
             m = t.get_column("month_of_year")
             {**{f"cells reading {k}": m.count(k) for k in ("01", "09", "10", "12")},
              "cells two long": sum(len(v) == 2 for v in m)}
         """,
         pandas="""
             m = list(data["month_of_year"].astype(str).str.zfill(2))
             {**{f"cells reading {k}": m.count(k) for k in ("01", "09", "10", "12")},
              "cells two long": sum(len(v) == 2 for v in m)}
         """, pandas_label="pandas astype(str).str.zfill(2)",
         polars="""
             m = df.select(pl.col("month_of_year").cast(pl.String).str.zfill(2)).to_series().to_list()
             {**{f"cells reading {k}": m.count(k) for k in ("01", "09", "10", "12")},
              "cells two long": sum(len(v) == 2 for v in m)}
         """, polars_label="Polars cast(pl.String).str.zfill(2)",
         r="""
             m <- sprintf("%02d", month_of_year)
             list(`cells reading 01` = sum(m == "01"), `cells reading 09` = sum(m == "09"),
                  `cells reading 10` = sum(m == "10"), `cells reading 12` = sum(m == "12"),
                  `cells two long` = sum(nchar(m) == 2))
         """)
    both("table.change_column", "warpbreaks: the tension written as \"high breakage\" in the rows with 40 breaks "
         "or more", "warpbreaks", "real data", option="in_rows_where=",
         ours="""
             t = sdata.table(source).change_column("tension", value="high breakage", in_rows_where="breaks >= 40")
             v = t.get_column("tension")
             {"high breakage": v.count("high breakage"), "L": v.count("L"), "M": v.count("M"), "H": v.count("H")}
         """,
         pandas="""
             d = data.copy()
             d.loc[d["breaks"] >= 40, "tension"] = "high breakage"
             v = d["tension"]
             {k: int((v == k).sum()) for k in ("high breakage", "L", "M", "H")}
         """, pandas_label="pandas loc[condition, column] = value",
         polars="""
             v = df.select(pl.when(pl.col("breaks") >= 40).then(pl.lit("high breakage"))
                           .otherwise(pl.col("tension")).alias("tension"))["tension"]
             {k: int((v == k).sum()) for k in ("high breakage", "L", "M", "H")}
         """, polars_label="Polars when().then().otherwise()",
         r="""
             v <- ifelse(breaks >= 40, "high breakage", tension)
             list(`high breakage` = sum(v == "high breakage"), L = sum(v == "L"), M = sum(v == "M"), H = sum(v == "H"))
         """)
    both("table.change_time_zone_in", "AirPassengers: midnight at the start of each month on the Oslo clock, 1949-1960, "
         "on the UTC clock (Norway kept summer time in 1959 and 1960; the IANA time zone database)", "AirPassengers", "real data",
         setup='data = data.assign(month=pd.to_datetime(data["month"]))',
         ours="""
             t = sdata.table(source).change_time_zone_in("month", to="UTC", recorded_in="Europe/Oslo")
             hours = [t.get_cell_at(row=i, column="month").hour for i in range(1, 145)]
             {"months at 22:00 UTC (summer time)": hours.count(22), "months at 23:00 UTC": hours.count(23),
              "sum of row x hour": sum(i * h for i, h in enumerate(hours, 1))}
         """,
         pandas="""
             local = data["month"].dt.tz_localize("Europe/Oslo", nonexistent="NaT", ambiguous="NaT")
             hours = list(local.dt.tz_convert("UTC").dt.hour)
             {"months at 22:00 UTC (summer time)": hours.count(22), "months at 23:00 UTC": hours.count(23),
              "sum of row x hour": sum(i * h for i, h in enumerate(hours, 1))}
         """, pandas_label="pandas dt.tz_localize(\"Europe/Oslo\").dt.tz_convert(\"UTC\")",
         polars="""
             local = pl.col("month").dt.replace_time_zone("Europe/Oslo", non_existent="null", ambiguous="null")
             hours = df.select(local.dt.convert_time_zone("UTC").dt.hour())["month"].to_list()
             {"months at 22:00 UTC (summer time)": hours.count(22), "months at 23:00 UTC": hours.count(23),
              "sum of row x hour": sum(i * h for i, h in enumerate(hours, 1))}
         """, polars_label="Polars dt.replace_time_zone().dt.convert_time_zone(\"UTC\")",
         r="""
             x <- as.POSIXct(substr(as.character(month), 1, 10), tz = "Europe/Oslo")
             h <- as.integer(format(x, "%H", tz = "UTC"))
             list(`months at 22:00 UTC (summer time)` = sum(h == 22), `months at 23:00 UTC` = sum(h == 23),
                  `sum of row x hour` = sum(seq_along(h) * h))
         """)
    # America/New_York: a zone name with "_", which narwhals 2.27 to 2.29 did not read on a pandas table (the column was
    # "Unknown"); simplydata._narwhals_mend lets it read the name (tests/test_time_zone_names.py)
    both("table.change_time_zone_in", "AirPassengers: midnight at the start of each month on the New York clock, "
         "1949-1960, on the UTC clock (US summer time; the IANA time zone database)", "AirPassengers", "real data",
         setup='data = data.assign(month=pd.to_datetime(data["month"]))',
         ours="""
             t = sdata.table(source).change_time_zone_in("month", to="UTC", recorded_in="America/New_York")
             hours = [t.get_cell_at(row=i, column="month").hour for i in range(1, 145)]
             {"months at 04:00 UTC (summer time)": hours.count(4), "months at 05:00 UTC": hours.count(5),
              "sum of row x hour": sum(i * h for i, h in enumerate(hours, 1))}
         """,
         pandas="""
             local = data["month"].dt.tz_localize("America/New_York", nonexistent="NaT", ambiguous="NaT")
             hours = list(local.dt.tz_convert("UTC").dt.hour)
             {"months at 04:00 UTC (summer time)": hours.count(4), "months at 05:00 UTC": hours.count(5),
              "sum of row x hour": sum(i * h for i, h in enumerate(hours, 1))}
         """, pandas_label="pandas dt.tz_localize(\"America/New_York\").dt.tz_convert(\"UTC\")",
         polars="""
             local = pl.col("month").dt.replace_time_zone("America/New_York", non_existent="null", ambiguous="null")
             hours = df.select(local.dt.convert_time_zone("UTC").dt.hour())["month"].to_list()
             {"months at 04:00 UTC (summer time)": hours.count(4), "months at 05:00 UTC": hours.count(5),
              "sum of row x hour": sum(i * h for i, h in enumerate(hours, 1))}
         """, polars_label="Polars dt.replace_time_zone(\"America/New_York\").dt.convert_time_zone(\"UTC\")",
         r="""
             x <- as.POSIXct(substr(as.character(month), 1, 10), tz = "America/New_York")
             h <- as.integer(format(x, "%H", tz = "UTC"))
             list(`months at 04:00 UTC (summer time)` = sum(h == 4), `months at 05:00 UTC` = sum(h == 5),
                  `sum of row x hour` = sum(seq_along(h) * h))
         """)
    both("table.change_time_zone_in", "AirPassengers: a column that already carries the America/New_York zone "
         "(midnight at the start of each month, 1949-1960), its day of the month, then the same moments on the "
         "UTC clock", "AirPassengers", "real data",
         setup='data = data.assign(month=pd.to_datetime(data["month"]).dt.tz_localize("America/New_York"))',
         ours="""
             t = sdata.table(source)
             t.add_column_with_part_of_date("day", from_column="month", part="day")
             t.change_time_zone_in("month", to="UTC")
             hours = [t.get_cell_at(row=i, column="month").hour for i in range(1, 145)]
             {"first of the month in New York": sum(d == 1 for d in t.get_column("day")),
              "months at 04:00 UTC (summer time)": hours.count(4), "months at 05:00 UTC": hours.count(5),
              "sum of row x hour": sum(i * h for i, h in enumerate(hours, 1))}
         """,
         pandas="""
             hours = list(data["month"].dt.tz_convert("UTC").dt.hour)
             {"first of the month in New York": int((data["month"].dt.day == 1).sum()),
              "months at 04:00 UTC (summer time)": hours.count(4), "months at 05:00 UTC": hours.count(5),
              "sum of row x hour": sum(i * h for i, h in enumerate(hours, 1))}
         """, pandas_label="pandas dt.day and dt.tz_convert(\"UTC\")",
         polars="""
             hours = df.select(pl.col("month").dt.convert_time_zone("UTC").dt.hour())["month"].to_list()
             {"first of the month in New York": int((df["month"].dt.day() == 1).sum()),
              "months at 04:00 UTC (summer time)": hours.count(4), "months at 05:00 UTC": hours.count(5),
              "sum of row x hour": sum(i * h for i, h in enumerate(hours, 1))}
         """, polars_label="Polars dt.day() and dt.convert_time_zone(\"UTC\")",
         r="""
             x <- as.POSIXct(substr(as.character(month), 1, 10), tz = "America/New_York")
             h <- as.integer(format(x, "%H", tz = "UTC"))
             list(`first of the month in New York` = sum(as.integer(format(x, "%d")) == 1),
                  `months at 04:00 UTC (summer time)` = sum(h == 4), `months at 05:00 UTC` = sum(h == 5),
                  `sum of row x hour` = sum(seq_along(h) * h))
         """)
    both("table.round_dates_in", "AirPassengers: the first day of each month taken back to the Monday of its week",
         "AirPassengers", "real data",
         ours="""
             t = sdata.table(source)
             t.turn_into_dates("month")
             t.round_dates_in("month", down_to="week")
             days = [t.get_cell_at(row=i, column="month") for i in range(1, 145)]
             {"still the first of the month": sum(d.day == 1 for d in days),
              "all Mondays": float(all(d.weekday() == 0 for d in days)),
              **{f"row {i}: {str(d)[:10]}": 1.0 for i, d in enumerate(days, 1)}}
         """,
         pandas="""
             m = pd.to_datetime(data["month"])
             days = list(m - pd.to_timedelta(m.dt.dayofweek, unit="D"))
             {"still the first of the month": sum(d.day == 1 for d in days),
              "all Mondays": float(all(d.weekday() == 0 for d in days)),
              **{f"row {i}: {str(d)[:10]}": 1.0 for i, d in enumerate(days, 1)}}
         """, pandas_label="pandas: the date minus its dt.dayofweek in days",
         polars="""
             days = df.select(pl.col("month").str.to_date().dt.truncate("1w"))["month"].to_list()
             {"still the first of the month": sum(d.day == 1 for d in days),
              "all Mondays": float(all(d.weekday() == 0 for d in days)),
              **{f"row {i}: {str(d)[:10]}": 1.0 for i, d in enumerate(days, 1)}}
         """, polars_label="Polars dt.truncate(\"1w\")",
         r="""
             d <- as.Date(month)
             w <- d - (as.POSIXlt(d)$wday + 6) %% 7
             found <- setNames(as.list(rep(1, length(w))), paste0("row ", seq_along(w), ": ", format(w, "%Y-%m-%d")))
             c(list(`still the first of the month` = sum(as.POSIXlt(w)$mday == 1)), found)
         """)
    both("table.round_dates_in", "ICU arrivals: 254 arrival times rounded to the nearest hour (59 are exactly half "
         "past, which go up)", "ICU arrivals (circular)", "real data", option="to_the=",
         setup='data = data.assign(arrived=pd.Timestamp("1966-01-01") + '
               'pd.to_timedelta((data["hour"] * 60).round(), unit="min"))',
         ours="""
             t = sdata.table(source).round_dates_in("arrived", to_the="hour")
             times = [t.get_cell_at(row=i, column="arrived") for i in range(1, 255)]
             {"sum of hours": sum(x.hour for x in times), "next day": sum(x.day == 2 for x in times),
              "sum of row x hour": sum(i * x.hour for i, x in enumerate(times, 1)),
              "on the hour": float(all(x.minute == 0 and x.second == 0 for x in times))}
         """,
         pandas="""
             times = list((data["arrived"] + pd.Timedelta("30min")).dt.floor("h"))
             {"sum of hours": sum(x.hour for x in times), "next day": sum(x.day == 2 for x in times),
              "sum of row x hour": sum(i * x.hour for i, x in enumerate(times, 1)),
              "on the hour": float(all(x.minute == 0 and x.second == 0 for x in times))}
         """, pandas_label="pandas (time + 30 minutes).dt.floor(\"h\") (half way up)",
         polars="""
             times = df.select(pl.col("arrived").dt.round("1h"))["arrived"].to_list()
             {"sum of hours": sum(x.hour for x in times), "next day": sum(x.day == 2 for x in times),
              "sum of row x hour": sum(i * x.hour for i, x in enumerate(times, 1)),
              "on the hour": float(all(x.minute == 0 and x.second == 0 for x in times))}
         """, polars_label="Polars dt.round(\"1h\")",
         r="""
             x <- as.POSIXct("1966-01-01", tz = "UTC") + round(hour * 60) * 60
             r <- as.POSIXlt(round(x, "hours"))
             list(`sum of hours` = sum(r$hour), `next day` = sum(r$mday == 2), `sum of row x hour` = sum(seq_along(r$hour) * r$hour),
                  `on the hour` = as.numeric(all(r$min == 0 & r$sec == 0)))
         """, note="R round.POSIXt(x, \"hours\") also sends a time exactly half way up.")
    both("table.turn_into_text", "AirPassengers: the 144 months written as day.month.year", "AirPassengers",
         "real data", option="written_like=",
         ours="""
             t = sdata.table(source)
             t.turn_into_dates("month")
             t.turn_into_text("month", written_like="31.12.2026")
             v = t.get_column("month")
             {"cells": len(v), **{f"row {i}: {x}": 1.0 for i, x in enumerate(v, 1)}}
         """,
         pandas="""
             v = list(pd.to_datetime(data["month"]).dt.strftime("%d.%m.%Y"))
             {"cells": len(v), **{f"row {i}: {x}": 1.0 for i, x in enumerate(v, 1)}}
         """, pandas_label="pandas dt.strftime(\"%d.%m.%Y\")",
         polars="""
             v = df.select(pl.col("month").str.to_date().dt.to_string("%d.%m.%Y"))["month"].to_list()
             {"cells": len(v), **{f"row {i}: {x}": 1.0 for i, x in enumerate(v, 1)}}
         """, polars_label="Polars dt.to_string(\"%d.%m.%Y\")",
         r="""
             v <- format(as.Date(month), "%d.%m.%Y")
             c(list(cells = length(v)), setNames(as.list(rep(1, length(v))), paste0("row ", seq_along(v), ": ", v)))
         """)
    both("table.turn_into_categories", "warpbreaks: tension put in the order high, medium, low, then sorted by it",
         "warpbreaks", "real data",
         ours="""
             t = sdata.table(source)
             t.turn_into_categories("tension", in_order=["H", "M", "L"])
             t.sort_by("tension")
             b = t.get_column("breaks")
             {"first tension is H": float(t.get_cell_at(row=1, column="tension") == "H"),
              "sum of row x breaks": sum(i * b.get_number_at(i) for i in range(1, 55))}
         """,
         pandas="""
             d = data.copy()
             d["tension"] = pd.Categorical(d["tension"], ordered=True, categories=["H", "M", "L"])
             d = d.sort_values("tension", kind="stable")
             {"first tension is H": float(d["tension"].iloc[0] == "H"),
              "sum of row x breaks": sum(i * v for i, v in enumerate(d["breaks"], 1))}
         """, pandas_label="pandas Categorical(ordered=True), sort_values (stable)",
         polars="""
             d = df.with_columns(pl.col("tension").cast(pl.Enum(["H", "M", "L"])))
             d = d.with_row_index().sort("tension", "index").drop("index")
             {"first tension is H": float(d["tension"][0] == "H"),
              "sum of row x breaks": sum(i * v for i, v in enumerate(d["breaks"], 1))}
         """, polars_label="Polars pl.Enum, sort",
         r="""
             o <- order(factor(tension, levels = c("H", "M", "L")))
             list(`first tension is H` = as.numeric(tension[o][1] == "H"), `sum of row x breaks` = sum(seq_along(o) * breaks[o]))
         """)
    both("table.clean_column_names", "Hackshaw's passive smoking studies: \"odds ratio 95 % CI low\" and the other "
         "names made plain", "passive smoking (metadat)", "real data",
         ours="""
             names = sdata.table(source).clean_column_names().get_column_names()
             {"columns": len(names), **{f"column {i}: {n}": 1.0 for i, n in enumerate(names, 1)}}
         """,
         pandas="""
             names = list(data.columns.str.replace("%", "_percent_").str.normalize("NFKD")
                          .str.encode("ascii", "ignore").str.decode("ascii")
                          .str.replace(r"[^0-9A-Za-z]+", "_", regex=True).str.strip("_").str.lower())
             {"columns": len(names), **{f"column {i}: {n}": 1.0 for i, n in enumerate(names, 1)}}
         """, pandas_label="pandas str.replace, str.normalize(\"NFKD\"), str.lower on the column names",
         polars="""
             import re
             import unicodedata
             plain = [unicodedata.normalize("NFKD", c.replace("%", "_percent_")).encode("ascii", "ignore").decode()
                      for c in df.columns]
             names = df.rename({c: re.sub(r"[^0-9A-Za-z]+", "_", a).strip("_").lower()
                                for c, a in zip(df.columns, plain)}).columns
             {"columns": len(names), **{f"column {i}: {n}": 1.0 for i, n in enumerate(names, 1)}}
         """, polars_label="Polars rename (re.sub, unicodedata)",
         r="""
             n <- c("study", "odds ratio", "odds ratio 95 % CI low", "odds ratio 95 % CI high")
             n <- tolower(gsub("^_+|_+$", "", gsub("[^0-9A-Za-z]+", "_", gsub("%", "_percent_", n, fixed = TRUE))))
             c(list(columns = length(n)), setNames(as.list(rep(1, length(n))), paste0("column ", seq_along(n), ": ", n)))
         """)

    # ---------------------------------------------------------------- choosing rows and columns
    both("table.keep_first_rows", "mtcars: the two cars with the best fuel use for each number of cylinders",
         "mtcars", "real data", option="for_each_group_in=",
         ours="""
             t = sdata.table(source)
             t.sort_by("mpg", biggest_first=True)
             t.keep_first_rows(2, for_each_group_in="cyl")
             models = t.get_column("model")
             {"rows": t.count_rows(), **{f"row {i}: {m}": 1.0 for i, m in enumerate(models, 1)}}
         """,
         pandas="""
             d = data.sort_values("mpg", ascending=False, kind="stable").groupby("cyl", sort=False, dropna=False).head(2)
             {"rows": len(d), **{f"row {i}: {m}": 1.0 for i, m in enumerate(d["model"], 1)}}
         """, pandas_label="pandas sort_values (stable), groupby().head(2)",
         polars="""
             d = df.sort("mpg", descending=True, maintain_order=True)
             d = d.filter(pl.int_range(pl.len()).over("cyl") < 2)
             {"rows": d.height, **{f"row {i}: {m}": 1.0 for i, m in enumerate(d["model"], 1)}}
         """, polars_label="Polars sort, filter(int_range(len()).over() < 2)",
         r="""
             o <- order(-mpg)
             keep <- ave(seq_along(o), cyl[o], FUN = seq_along) <= 2
             m <- model[o][keep]
             c(list(rows = length(m)), setNames(as.list(rep(1, length(m))), paste0("row ", seq_along(m), ": ", m)))
         """)
    both("table.keep_groups_where", "mtcars: only the numbers of cylinders whose cars average 19 mpg or more",
         "mtcars", "real data",
         ours="""
             t = sdata.table(source).keep_groups_where("average(mpg) >= 19", for_each_group_in="cyl")
             {"rows": t.count_rows(), "total mpg": t.get_column("mpg").find_total()}
         """,
         pandas="""
             d = data.groupby("cyl").filter(lambda group: group["mpg"].mean() >= 19)
             {"rows": len(d), "total mpg": d["mpg"].sum()}
         """, pandas_label="pandas groupby().filter()", tolerance=1e-12,
         polars="""
             d = df.filter(pl.col("mpg").mean().over("cyl") >= 19)
             {"rows": d.height, "total mpg": d["mpg"].sum()}
         """, polars_label="Polars filter(mean().over() >= 19)",
         r="""
             keep <- ave(mpg, cyl) >= 19
             list(rows = sum(keep), `total mpg` = sum(mpg[keep]))
         """, r_tolerance=1e-12)
    both("table.remove_groups_where", "mtcars: the numbers of cylinders whose cars average under 19 mpg removed",
         "mtcars", "real data",
         ours="""
             t = sdata.table(source).remove_groups_where("average(mpg) < 19", for_each_group_in="cyl")
             {"rows": t.count_rows(), "total mpg": t.get_column("mpg").find_total()}
         """,
         pandas="""
             d = data.groupby("cyl").filter(lambda group: not group["mpg"].mean() < 19)
             {"rows": len(d), "total mpg": d["mpg"].sum()}
         """, pandas_label="pandas groupby().filter()", tolerance=1e-12,
         polars="""
             d = df.filter(~(pl.col("mpg").mean().over("cyl") < 19))
             {"rows": d.height, "total mpg": d["mpg"].sum()}
         """, polars_label="Polars filter(~(mean().over() < 19))",
         r="""
             keep <- !(ave(mpg, cyl) < 19)
             list(rows = sum(keep), `total mpg` = sum(mpg[keep]))
         """, r_tolerance=1e-12)
    both("table.keep_rows_found_in", "warpbreaks: the looms run at low or high tension (a list with a repeat)",
         "warpbreaks", "real data",
         ours="""
             t = sdata.table(source).keep_rows_found_in({"tension": ["L", "H", "L"]}, using="tension")
             b = t.get_column("breaks")
             {"rows": t.count_rows(), "total breaks": b.find_total(),
              "sum of row x breaks": sum(i * b.get_number_at(i) for i in range(1, t.count_rows() + 1))}
         """,
         pandas="""
             d = data[data["tension"].isin(pd.DataFrame({"tension": ["L", "H", "L"]})["tension"])]
             {"rows": len(d), "total breaks": d["breaks"].sum(),
              "sum of row x breaks": sum(i * v for i, v in enumerate(d["breaks"], 1))}
         """, pandas_label="pandas isin",
         polars="""
             d = df.join(pl.DataFrame({"tension": ["L", "H", "L"]}).unique(), on="tension", how="semi",
                         maintain_order="left")
             {"rows": d.height, "total breaks": d["breaks"].sum(),
              "sum of row x breaks": sum(i * v for i, v in enumerate(d["breaks"], 1))}
         """, polars_label="Polars join(how=\"semi\")",
         r="""
             keep <- tension %in% c("L", "H", "L")
             b <- breaks[keep]
             list(rows = sum(keep), `total breaks` = sum(b), `sum of row x breaks` = sum(seq_along(b) * b))
         """)
    both("table.remove_rows_found_in", "warpbreaks: the looms run at low tension removed", "warpbreaks", "real data",
         ours="""
             t = sdata.table(source).remove_rows_found_in({"tension": ["L"]}, using="tension")
             b = t.get_column("breaks")
             {"rows": t.count_rows(), "total breaks": b.find_total(),
              "sum of row x breaks": sum(i * b.get_number_at(i) for i in range(1, t.count_rows() + 1))}
         """,
         pandas="""
             d = data[~data["tension"].isin(pd.DataFrame({"tension": ["L"]})["tension"])]
             {"rows": len(d), "total breaks": d["breaks"].sum(),
              "sum of row x breaks": sum(i * v for i, v in enumerate(d["breaks"], 1))}
         """, pandas_label="pandas ~isin",
         polars="""
             d = df.join(pl.DataFrame({"tension": ["L"]}), on="tension", how="anti", maintain_order="left")
             {"rows": d.height, "total breaks": d["breaks"].sum(),
              "sum of row x breaks": sum(i * v for i, v in enumerate(d["breaks"], 1))}
         """, polars_label="Polars join(how=\"anti\")",
         r="""
             keep <- !(tension %in% "L")
             b <- breaks[keep]
             list(rows = sum(keep), `total breaks` = sum(b), `sum of row x breaks` = sum(seq_along(b) * b))
         """)
    both("table.keep_rows_where", "iris: the flowers whose species is SETOSA, capitals not mattering", "iris",
         "real data", option="capitals_matter=",
         ours="""
             t = sdata.table(source).keep_rows_where("Species", is_equal_to="SETOSA", capitals_matter=False)
             {"rows": t.count_rows(), "total sepal length": t.get_column("Sepal.Length").find_total()}
         """,
         pandas="""
             d = data[data["Species"].str.lower() == "setosa"]
             {"rows": len(d), "total sepal length": d["Sepal.Length"].sum()}
         """, pandas_label="pandas str.lower() ==", tolerance=1e-12,
         polars="""
             d = df.filter(pl.col("Species").str.to_lowercase() == "setosa")
             {"rows": d.height, "total sepal length": d["Sepal.Length"].sum()}
         """, polars_label="Polars str.to_lowercase() ==",
         r="""
             keep <- tolower(Species) == tolower("SETOSA")
             list(rows = sum(keep), `total sepal length` = sum(Sepal.Length[keep]))
         """, r_tolerance=1e-12)
    both("table.make_one_table_for_each_group_in", "iris: one table for each of the three species", "iris",
         "real data",
         ours="""
             tables = sdata.table(source).make_one_table_for_each_group_in("Species")
             {"tables": len(tables), **{f"{k}: flowers": v.count_rows() for k, v in tables.items()},
              **{f"{k}: total petal length": v.get_column("Petal.Length").find_total() for k, v in tables.items()}}
         """,
         pandas="""
             tables = {k: part for k, part in data.groupby("Species", sort=False, dropna=False)}
             {"tables": len(tables), **{f"{k}: flowers": len(v) for k, v in tables.items()},
              **{f"{k}: total petal length": v["Petal.Length"].sum() for k, v in tables.items()}}
         """, pandas_label="pandas groupby(sort=False)", tolerance=1e-12,
         polars="""
             tables = {k[0]: v for k, v in df.partition_by("Species", maintain_order=True, as_dict=True).items()}
             {"tables": len(tables), **{f"{k}: flowers": v.height for k, v in tables.items()},
              **{f"{k}: total petal length": v["Petal.Length"].sum() for k, v in tables.items()}}
         """, polars_label="Polars partition_by(as_dict=True)",
         r="""
             s <- split(Petal.Length, Species)
             list(tables = length(s), `setosa: flowers` = length(s$setosa), `versicolor: flowers` = length(s$versicolor),
                  `virginica: flowers` = length(s$virginica), `setosa: total petal length` = sum(s$setosa),
                  `versicolor: total petal length` = sum(s$versicolor), `virginica: total petal length` = sum(s$virginica))
         """, r_tolerance=1e-12)
    both("table.move_columns", "mtcars: horsepower and weight moved to the front", "mtcars", "real data",
         ours="""
             names = sdata.table(source).move_columns("hp", "wt", to="start").get_column_names()
             {"columns": len(names), **{f"column {i}: {n}": 1.0 for i, n in enumerate(names, 1)}}
         """,
         pandas="""
             moved = ["hp", "wt"]
             names = list(data[moved + [c for c in data.columns if c not in moved]].columns)
             {"columns": len(names), **{f"column {i}: {n}": 1.0 for i, n in enumerate(names, 1)}}
         """, pandas_label="pandas df[columns in the new order]",
         polars="""
             moved = ["hp", "wt"]
             names = df.select(moved + [c for c in df.columns if c not in moved]).columns
             {"columns": len(names), **{f"column {i}: {n}": 1.0 for i, n in enumerate(names, 1)}}
         """, polars_label="Polars select(columns in the new order)")
    both("table.rename_columns", "mtcars: mpg and hp given longer names", "mtcars", "real data",
         ours="""
             t = sdata.table(source).rename_columns({"mpg": "miles_per_gallon", "hp": "horsepower"})
             names = t.get_column_names()
             {"columns": len(names), "total horsepower": t.get_column("horsepower").find_total(),
              **{f"column {i}: {n}": 1.0 for i, n in enumerate(names, 1)}}
         """,
         pandas="""
             d = data.rename(columns={"mpg": "miles_per_gallon", "hp": "horsepower"})
             {"columns": d.shape[1], "total horsepower": d["horsepower"].sum(),
              **{f"column {i}: {n}": 1.0 for i, n in enumerate(d.columns, 1)}}
         """, pandas_label="pandas rename(columns=)",
         polars="""
             d = df.rename({"mpg": "miles_per_gallon", "hp": "horsepower"})
             {"columns": d.width, "total horsepower": d["horsepower"].sum(),
              **{f"column {i}: {n}": 1.0 for i, n in enumerate(d.columns, 1)}}
         """, polars_label="Polars rename")
    both("table.count_columns", "the 12 columns of mtcars (the car names and 11 measurements)", "mtcars", "real data",
         ours="""
             {"columns": sdata.table(source).count_columns()}
         """,
         pandas="""
             {"columns": data.shape[1]}
         """, pandas_label="pandas shape[1]",
         polars="""
             {"columns": df.width}
         """, polars_label="Polars width",
         published={"columns": (12, 0.0, "Henderson & Velleman (1981): 11 variables, with the car names")})
    both("table.remove_columns_that_are_all_empty", "NHANES: the 9 people without a body mass index; their bmi "
         "column, all empty, removed", "nhanes (mice)", "real data",
         setup='data = data[data["bmi"].isna()].reset_index(drop=True)',
         ours="""
             names = sdata.table(source).remove_columns_that_are_all_empty().get_column_names()
             {"columns": len(names), **{f"column {i}: {n}": 1.0 for i, n in enumerate(names, 1)}}
         """,
         pandas="""
             names = list(data.dropna(axis=1, how="all").columns)
             {"columns": len(names), **{f"column {i}: {n}": 1.0 for i, n in enumerate(names, 1)}}
         """, pandas_label="pandas dropna(axis=1, how=\"all\")",
         polars="""
             names = df.select([c for c in df.columns if df[c].null_count() < df.height]).columns
             {"columns": len(names), **{f"column {i}: {n}": 1.0 for i, n in enumerate(names, 1)}}
         """, polars_label="Polars select(columns with null_count() < height)",
         r="""
             gone <- is.na(bmi)
             kept <- c("age", "bmi", "hyp", "chl")[c(!all(is.na(age[gone])), !all(is.na(bmi[gone])),
                                                     !all(is.na(hyp[gone])), !all(is.na(chl[gone])))]
             c(list(columns = length(kept)), setNames(as.list(rep(1, length(kept))), paste0("column ", seq_along(kept), ": ", kept)))
         """)
    both("table.remove_rows_that_are_all_empty", "NHANES body mass index, hypertension and cholesterol: the 7 "
         "people with none of the three removed", "nhanes (mice)", "real data",
         setup='data = data[["bmi", "hyp", "chl"]]',
         ours="""
             t = sdata.table(source).remove_rows_that_are_all_empty()
             {"rows left": t.count_rows(), "total cholesterol": t.get_column("chl").find_total(),
              "empty bmi left": t.get_column("bmi").count_empty_numbers()}
         """,
         pandas="""
             d = data.dropna(how="all")
             {"rows left": len(d), "total cholesterol": d["chl"].sum(), "empty bmi left": int(d["bmi"].isna().sum())}
         """, pandas_label="pandas dropna(how=\"all\")",
         polars="""
             d = df.filter(~pl.all_horizontal(pl.all().is_null()))
             {"rows left": d.height, "total cholesterol": d["chl"].sum(), "empty bmi left": d["bmi"].null_count()}
         """, polars_label="Polars filter(~all_horizontal(is_null()))",
         r="""
             keep <- !(is.na(bmi) & is.na(hyp) & is.na(chl))
             list(`rows left` = sum(keep), `total cholesterol` = sum(chl[keep], na.rm = TRUE),
                  `empty bmi left` = sum(is.na(bmi[keep])))
         """)
    both("table.sort_by", "mtcars sorted by cylinders (fewest first), then by miles per gallon (most first)",
         "mtcars", "real data", option="biggest_first=",
         ours="""
             t = sdata.table(source).sort_by("cyl", "mpg", biggest_first=[False, True])
             {"rows": t.count_rows(), **{f"row {i}: {m}": 1.0 for i, m in enumerate(t.get_column("model"), 1)}}
         """,
         pandas="""
             d = data.sort_values(["cyl", "mpg"], ascending=[True, False], kind="stable")
             {"rows": len(d), **{f"row {i}: {m}": 1.0 for i, m in enumerate(d["model"], 1)}}
         """, pandas_label="pandas sort_values(ascending=[True, False], kind=\"stable\")",
         polars="""
             d = df.sort(["cyl", "mpg"], descending=[False, True], maintain_order=True)
             {"rows": d.height, **{f"row {i}: {m}": 1.0 for i, m in enumerate(d["model"], 1)}}
         """, polars_label="Polars sort(descending=[False, True], maintain_order=True)",
         r="""
             m <- model[order(cyl, -mpg)]
             c(list(rows = length(m)), setNames(as.list(rep(1, length(m))), paste0("row ", seq_along(m), ": ", m)))
         """)

    # ---------------------------------------------------------------- reshaping and joining
    both("table.split_into_rows", "mtcars: each word of a car's name on its own row", "mtcars", "real data",
         ours="""
             t = sdata.table(source)
             t.keep_columns("model", "mpg")
             t.split_into_rows("model", separator=" ")
             words = t.get_column("model")
             {"rows": t.count_rows(), "Merc": words.count("Merc"), "total mpg": t.get_column("mpg").find_total(),
              **{f"row {i}: {w}": 1.0 for i, w in enumerate(words, 1)}}
         """,
         pandas="""
             d = data[["model", "mpg"]]
             d = d.assign(model=d["model"].str.split(" ")).explode("model", ignore_index=True)
             {"rows": len(d), "Merc": int((d["model"] == "Merc").sum()), "total mpg": d["mpg"].sum(),
              **{f"row {i}: {w}": 1.0 for i, w in enumerate(d["model"], 1)}}
         """, pandas_label="pandas str.split, explode", tolerance=1e-12,
         polars="""
             d = df.select("model", "mpg").with_columns(pl.col("model").str.split(" ")).explode("model")
             {"rows": d.height, "Merc": int((d["model"] == "Merc").sum()), "total mpg": d["mpg"].sum(),
              **{f"row {i}: {w}": 1.0 for i, w in enumerate(d["model"], 1)}}
         """, polars_label="Polars str.split, explode",
         r="""
             parts <- strsplit(model, " ", fixed = TRUE)
             w <- unlist(parts)
             c(list(rows = length(w), Merc = sum(w == "Merc"), `total mpg` = sum(rep(mpg, lengths(parts)))),
               setNames(as.list(rep(1, length(w))), paste0("row ", seq_along(w), ": ", w)))
         """, r_tolerance=1e-12)
    both("table.gather_into_rows", "iris: the two sepal columns (names starting with \"Sepal.\") turned into rows",
         "iris", "real data", option="starts_with=",
         ours="""
             t = sdata.table(source).gather_into_rows(starts_with="Sepal.", names_to="part", values_to="cm")
             cm = t.get_column("cm")
             part = t.get_column("part")
             {"rows": t.count_rows(), "columns": len(t.get_column_names()), "total cm": cm.find_total(),
              "Sepal.Width rows": part.count("Sepal.Width"), "row 151": cm.get_number_at(151)}
         """,
         pandas="""
             names = [c for c in data.columns if c.startswith("Sepal.")]
             d = data.melt(id_vars=[c for c in data.columns if c not in names], value_vars=names, var_name="part",
                           value_name="cm")
             {"rows": len(d), "columns": d.shape[1], "total cm": d["cm"].sum(),
              "Sepal.Width rows": int((d["part"] == "Sepal.Width").sum()), "row 151": d["cm"].iloc[150]}
         """, pandas_label="pandas melt", tolerance=1e-12,
         polars="""
             import polars.selectors as cs
             d = df.unpivot(on=cs.starts_with("Sepal."), index=[c for c in df.columns if not c.startswith("Sepal.")],
                            variable_name="part", value_name="cm")
             {"rows": d.height, "columns": d.width, "total cm": d["cm"].sum(),
              "Sepal.Width rows": int((d["part"] == "Sepal.Width").sum()), "row 151": d["cm"][150]}
         """, polars_label="Polars unpivot(on=cs.starts_with())",
         r="""
             long <- stack(list(Sepal.Length = Sepal.Length, Sepal.Width = Sepal.Width))
             list(rows = nrow(long), `total cm` = sum(long$values), `Sepal.Width rows` = sum(long$ind == "Sepal.Width"),
                  `row 151` = long$values[151])
         """, r_tolerance=1e-12)
    both("table.spread_into_columns", "warpbreaks: the total breaks for each wool (rows) and tension (columns)",
         "warpbreaks", "real data", option="show=",
         ours="""
             t = sdata.table(source)
             t.keep_columns("wool", "tension", "breaks")
             t.spread_into_columns(names_from="tension", values_from="breaks", show="total")
             found = {"columns": len(t.get_column_names())}
             for i in range(1, t.count_rows() + 1):
                 w = t.get_cell_at(row=i, column="wool")
                 found.update({f"wool {w}, tension {k}": t.get_cell_at(row=i, column=k) for k in ("L", "M", "H")})
             found
         """,
         pandas="""
             wide = data.pivot_table(index="wool", columns="tension", values="breaks", aggfunc="sum")
             wide = wide.loc[data["wool"].unique(), data["tension"].unique()].reset_index().rename_axis(columns=None)
             found = {"columns": wide.shape[1]}
             for _, row in wide.iterrows():
                 found.update({f"wool {row['wool']}, tension {k}": row[k] for k in ("L", "M", "H")})
             found
         """, pandas_label="pandas pivot_table(aggfunc=\"sum\")",
         polars="""
             wide = df.pivot(on="tension", index="wool", values="breaks", aggregate_function="sum")
             found = {"columns": wide.width}
             for row in wide.iter_rows(named=True):
                 found.update({f"wool {row['wool']}, tension {k}": row[k] for k in ("L", "M", "H")})
             found
         """, polars_label="Polars pivot(aggregate_function=\"sum\")",
         r="""
             s <- tapply(breaks, list(wool, tension), sum)
             list(`wool A, tension L` = s["A", "L"], `wool A, tension M` = s["A", "M"], `wool A, tension H` = s["A", "H"],
                  `wool B, tension L` = s["B", "L"], `wool B, tension M` = s["B", "M"], `wool B, tension H` = s["B", "H"])
         """)
    both("table.spread_into_yes_no_columns", "iris: a yes/no column for each species", "iris", "real data",
         ours="""
             t = sdata.table(source).spread_into_yes_no_columns("Species")
             names = t.get_column_names()
             {"columns": len(names), **{f"yes in {n}": sum(bool(v) for v in t.get_column(n)) for n in names[5:]},
              "row 51 is versicolor": float(bool(t.get_cell_at(row=51, column="Species: versicolor")))}
         """,
         pandas="""
             yes_no = pd.get_dummies(data["Species"], prefix="Species", prefix_sep=": ")
             d = pd.concat([data, yes_no], axis=1)
             {"columns": d.shape[1], **{f"yes in {n}": int(yes_no[n].sum()) for n in yes_no.columns},
              "row 51 is versicolor": float(bool(d["Species: versicolor"].iloc[50]))}
         """, pandas_label="pandas get_dummies(prefix_sep=\": \")",
         polars="""
             yes_no = df["Species"].to_dummies(separator=": ").cast(pl.Boolean)
             d = pl.concat([df, yes_no], how="horizontal")
             {"columns": d.width, **{f"yes in {n}": int(yes_no[n].sum()) for n in yes_no.columns},
              "row 51 is versicolor": float(bool(d["Species: versicolor"][50]))}
         """, polars_label="Polars to_dummies(separator=\": \")",
         r="""
             n <- table(Species)
             list(`yes in Species: setosa` = n[["setosa"]], `yes in Species: versicolor` = n[["versicolor"]],
                  `yes in Species: virginica` = n[["virginica"]], `row 51 is versicolor` = as.numeric(Species[51] == "versicolor"))
         """)
    both("table.join_with", "mtcars: every car paired with both kinds of gearbox (64 rows)", "mtcars", "real data",
         option='keep="every combination"',
         ours="""
             t = sdata.table(source)
             t.keep_columns("model", "mpg")
             t.join_with({"gearbox": ["automatic", "manual"]}, keep="every combination")
             rows = [f"{t.get_cell_at(row=i, column='model')} / {t.get_cell_at(row=i, column='gearbox')}"
                     for i in range(1, t.count_rows() + 1)]
             {"rows": t.count_rows(), "total mpg": t.get_column("mpg").find_total(),
              **{f"row {i}: {r}": 1.0 for i, r in enumerate(rows, 1)}}
         """,
         pandas="""
             d = data[["model", "mpg"]].merge(pd.DataFrame({"gearbox": ["automatic", "manual"]}), how="cross")
             {"rows": len(d), "total mpg": d["mpg"].sum(),
              **{f"row {i}: {m} / {g}": 1.0 for i, (m, g) in enumerate(zip(d["model"], d["gearbox"]), 1)}}
         """, pandas_label="pandas merge(how=\"cross\")", tolerance=1e-12,
         polars="""
             d = df.select("model", "mpg").join(pl.DataFrame({"gearbox": ["automatic", "manual"]}), how="cross")
             {"rows": d.height, "total mpg": d["mpg"].sum(),
              **{f"row {i}: {m} / {g}": 1.0 for i, (m, g) in enumerate(zip(d["model"], d["gearbox"]), 1)}}
         """, polars_label="Polars join(how=\"cross\")",
         r="""
             g <- c("automatic", "manual")
             r <- paste(rep(model, each = 2), "/", rep(g, times = length(model)))
             c(list(rows = length(r), `total mpg` = 2 * sum(mpg)),
               setNames(as.list(rep(1, length(r))), paste0("row ", seq_along(r), ": ", r)))
         """, r_tolerance=1e-12)
    both("table.join_with", "AirPassengers: each month joined to the start of its quarter (January, April, July, "
         "October) when that is at most 40 days before", "AirPassengers", "real data", option="match=",
         setup="""
             data = data.assign(month=pd.to_datetime(data["month"]))
             quarters = data[data["month"].dt.month.isin([1, 4, 7, 10])].rename(columns={"passengers": "quarter_start"})
         """,
         ours="""
             t = sdata.table(source).join_with(quarters, using="month", match="nearest before", within="40 days",
                                               keep="all rows from this table")
             q = t.get_column("quarter_start")
             {"rows": t.count_rows(), "empty": q.count_empty_numbers(), "total": q.find_total(),
              "February 1949": q.get_number_at(2), "sum of row x value": sum(i * v for i, v in enumerate(q, 1) if v == v)}
         """,
         pandas="""
             d = data.reset_index().sort_values("month", kind="stable")
             j = pd.merge_asof(d, quarters, on="month", direction="backward", tolerance=pd.Timedelta(days=40))
             q = j.sort_values("index")["quarter_start"].reset_index(drop=True)
             {"rows": len(q), "empty": int(q.isna().sum()), "total": q.sum(), "February 1949": q.iloc[1],
              "sum of row x value": sum(i * v for i, v in enumerate(q, 1) if v == v)}
         """, pandas_label="pandas merge_asof(direction=\"backward\", tolerance=40 days)",
         polars="""
             import datetime
             right = pl.from_pandas(quarters).sort("month")
             j = df.with_row_index().sort("month").join_asof(right, on="month", strategy="backward",
                                                             tolerance=datetime.timedelta(days=40))
             q = j.sort("index")["quarter_start"].to_list()
             {"rows": len(q), "empty": sum(v is None for v in q), "total": sum(v for v in q if v is not None),
              "February 1949": q[1], "sum of row x value": sum(i * v for i, v in enumerate(q, 1) if v is not None)}
         """, polars_label="Polars join_asof(strategy=\"backward\", tolerance=40 days)",
         r="""
             d <- as.Date(substr(as.character(month), 1, 10))
             starts <- which(as.POSIXlt(d)$mon %in% c(0, 3, 6, 9))
             q <- sapply(seq_along(d), function(i) {
               j <- starts[d[starts] <= d[i]]; j <- j[length(j)]
               if (length(j) && as.numeric(d[i] - d[j]) <= 40) passengers[j] else NA })
             list(rows = length(q), empty = sum(is.na(q)), total = sum(q, na.rm = TRUE), `February 1949` = q[2],
                  `sum of row x value` = sum((seq_along(q) * q)[!is.na(q)]))
         """)
    both("table.join_with", "iris joined to a table of the species' average petal length, named \"kind\" there",
         "iris", "real data", option="using=",
         setup="""
             kinds = (data.groupby("Species", as_index=False)["Petal.Length"].mean()
                      .rename(columns={"Species": "kind", "Petal.Length": "species_petal_length"}))
         """,
         ours="""
             t = sdata.table(source).join_with(kinds, using={"Species": "kind"}, check_that="each row has one match")
             names = t.get_column_names()
             s = t.get_column("species_petal_length")
             {"rows": t.count_rows(), "columns": len(names), "total": s.find_total(), "row 150": s.get_number_at(150),
              **{f"column {i}: {n}": 1.0 for i, n in enumerate(names, 1)}}
         """,
         pandas="""
             d = data.merge(kinds, left_on="Species", right_on="kind", validate="many_to_one").drop(columns="kind")
             {"rows": len(d), "columns": d.shape[1], "total": d["species_petal_length"].sum(),
              "row 150": d["species_petal_length"].iloc[149], **{f"column {i}: {n}": 1.0 for i, n in enumerate(d.columns, 1)}}
         """, pandas_label="pandas merge(left_on=, right_on=, validate=\"many_to_one\")", tolerance=1e-12,
         polars="""
             d = df.join(pl.from_pandas(kinds), left_on="Species", right_on="kind", validate="m:1",
                         maintain_order="left_right")
             {"rows": d.height, "columns": d.width, "total": d["species_petal_length"].sum(),
              "row 150": d["species_petal_length"][149], **{f"column {i}: {n}": 1.0 for i, n in enumerate(d.columns, 1)}}
         """, polars_label="Polars join(left_on=, right_on=, validate=\"m:1\")",
         r="""
             s <- ave(Petal.Length, Species)
             list(rows = length(s), total = sum(s), `row 150` = s[150])
         """, r_tolerance=1e-12)
    both("table.fill_empty_cells_from", "NHANES: the 9 empty body mass index cells filled with the average of the "
         "person's age group", "nhanes (mice)", "real data",
         setup='averages = data.groupby("age", as_index=False)["bmi"].mean()',
         ours="""
             t = sdata.table(source).fill_empty_cells_from(averages, using="age")
             b = t.get_column("bmi")
             {"empty left": b.count_empty_numbers(), "total": b.find_total(), "first person": b.get_number_at(1),
              "sum of row x bmi": sum(i * b.get_number_at(i) for i in range(1, 26))}
         """,
         pandas="""
             keyed = data.set_index("age")
             b = keyed["bmi"].fillna(averages.set_index("age")["bmi"].reindex(keyed.index)).reset_index(drop=True)
             {"empty left": int(b.isna().sum()), "total": b.sum(), "first person": b.iloc[0],
              "sum of row x bmi": sum(i * v for i, v in enumerate(b, 1))}
         """, pandas_label="pandas fillna from the other table's matching row (set_index, reindex)", tolerance=1e-12,
         polars="""
             j = df.join(pl.from_pandas(averages), on="age", how="left", suffix="_other", maintain_order="left")
             b = j.select(pl.coalesce("bmi", "bmi_other"))["bmi"]
             {"empty left": b.null_count(), "total": b.sum(), "first person": b[0],
              "sum of row x bmi": sum(i * v for i, v in enumerate(b, 1))}
         """, polars_label="Polars join(how=\"left\"), coalesce",
         r="""
             m <- ave(bmi, age, FUN = function(v) mean(v, na.rm = TRUE))
             b <- ifelse(is.na(bmi), m, bmi)
             list(`empty left` = sum(is.na(b)), total = sum(b), `first person` = b[1], `sum of row x bmi` = sum(seq_along(b) * b))
         """, r_tolerance=1e-12)

    # ---------------------------------------------------------------- summaries and lists
    both("table.find_summary_of", "NHANES body mass index by age group: the first and last filled values, the "
         "biggest and the smallest", "nhanes (mice)", "real data", option="show=",
         ours="""
             s = sdata.table(source).find_summary_of("bmi", show=["first", "biggest", "smallest", "last"],
                                                     for_each_group_in="age")
             found = {}
             for i in range(1, s.count_rows() + 1):
                 a = s.get_cell_at(row=i, column="age")
                 found.update({f"age group {a}: {k}": s.get_cell_at(row=i, column=k)
                               for k in ("first", "biggest", "smallest", "last")})
             found
         """,
         pandas="""
             f = data.groupby("age")["bmi"].agg(["first", "max", "min", "last"]).rename(columns={"max": "biggest",
                                                                                              "min": "smallest"})
             {f"age group {a}: {k}": f.loc[a, k] for a in f.index for k in ("first", "biggest", "smallest", "last")}
         """, pandas_label="pandas groupby().agg([\"first\", \"max\", \"min\", \"last\"]) (empty cells skipped)",
         polars="""
             b = pl.col("bmi").drop_nulls()
             f = df.group_by("age", maintain_order=True).agg(b.first().alias("first"), b.max().alias("biggest"),
                                                             b.min().alias("smallest"), b.last().alias("last"))
             {f"age group {row['age']}: {k}": row[k] for row in f.iter_rows(named=True)
              for k in ("first", "biggest", "smallest", "last")}
         """, polars_label="Polars group_by().agg(drop_nulls().first(), max(), min(), last())",
         r="""
             s <- split(bmi, age)
             out <- list()
             for (a in names(s)) {
               v <- s[[a]][!is.na(s[[a]])]
               out[[paste0("age group ", a, ": first")]] <- v[1]
               out[[paste0("age group ", a, ": biggest")]] <- max(v)
               out[[paste0("age group ", a, ": smallest")]] <- min(v)
               out[[paste0("age group ", a, ": last")]] <- v[length(v)]
             }
             out
         """)
    both("table.as_list", "mtcars given back as a list of 32 rows, one dict for each car", "mtcars", "real data",
         ours="""
             rows = sdata.table(source).as_list()
             {"rows": len(rows), "keys in a row": len(rows[0]), "total hp": sum(r["hp"] for r in rows),
              "total wt": sum(r["wt"] for r in rows), **{f"row {i}: {r['model']}": 1.0 for i, r in enumerate(rows, 1)}}
         """,
         pandas="""
             rows = data.to_dict("records")
             {"rows": len(rows), "keys in a row": len(rows[0]), "total hp": sum(r["hp"] for r in rows),
              "total wt": sum(r["wt"] for r in rows), **{f"row {i}: {r['model']}": 1.0 for i, r in enumerate(rows, 1)}}
         """, pandas_label="pandas to_dict(\"records\")",
         polars="""
             rows = df.to_dicts()
             {"rows": len(rows), "keys in a row": len(rows[0]), "total hp": sum(r["hp"] for r in rows),
              "total wt": sum(r["wt"] for r in rows), **{f"row {i}: {r['model']}": 1.0 for i, r in enumerate(rows, 1)}}
         """, polars_label="Polars to_dicts()")
    both("table.check_if_same_as", "mtcars against itself, and against mtcars with the weights rounded to 1 decimal",
         "mtcars", "real data",
         ours="""
             same = sdata.table(source).check_if_same_as(sdata.table(source))
             rounded = sdata.table(source).round_numbers_in("wt", 1)
             {"same as itself": float(same), "same after rounding wt": float(rounded.check_if_same_as(sdata.table(source)))}
         """,
         pandas="""
             {"same as itself": float(data.equals(data.copy())),
              "same after rounding wt": float(data.round({"wt": 1}).equals(data))}
         """, pandas_label="pandas equals",
         polars="""
             {"same as itself": float(df.equals(df.clone())),
              "same after rounding wt": float(df.with_columns(pl.col("wt").round(1)).equals(df))}
         """, polars_label="Polars equals",
         r="""
             list(`same as itself` = as.numeric(identical(wt, wt)), `same after rounding wt` = as.numeric(identical(round(wt, 1), wt)))
         """)
    both("table.show_duplicate_rows", "iris: flower 143 repeats flower 102 exactly", "iris", "real data",
         ours=_printed("sdata.table(source).show_duplicate_rows()", """
             import re
             n = [int(x) for x in re.findall(r"\\d+", lines[0])[:3]]
             {"rows that repeat": n[0], "different rows": n[1], "extra copies": n[2]}
         """),
         pandas="""
             repeats = data[data.duplicated(keep=False)]
             n, kinds = len(repeats), len(repeats.drop_duplicates())
             {"rows that repeat": n, "different rows": kinds, "extra copies": n - kinds}
         """, pandas_label="pandas duplicated(keep=False)",
         polars="""
             repeats = df.filter(df.is_duplicated())
             n, kinds = repeats.height, repeats.unique().height
             {"rows that repeat": n, "different rows": kinds, "extra copies": n - kinds}
         """, polars_label="Polars is_duplicated()",
         r="""
             d <- data.frame(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width, Species)
             n <- sum(duplicated(d) | duplicated(d, fromLast = TRUE))
             list(`rows that repeat` = n, `extra copies` = sum(duplicated(d)), `different rows` = n - sum(duplicated(d)))
         """)
    both("table.show_rows_with_empty_cells_in", "NHANES: the people with at least one empty cell", "nhanes (mice)",
         "real data",
         ours=_printed("sdata.table(source).show_rows_with_empty_cells_in()", """
             import re
             n = [int(x) for x in re.findall(r"\\d+", lines[0])[:2]]
             {"rows with an empty cell": n[0], "rows": n[1]}
         """),
         pandas="""
             holes = data[data.isna().any(axis=1)]
             {"rows with an empty cell": len(holes), "rows": len(data)}
         """, pandas_label="pandas isna().any(axis=1)",
         polars="""
             holes = df.filter(pl.any_horizontal(pl.all().is_null()))
             {"rows with an empty cell": holes.height, "rows": df.height}
         """, polars_label="Polars any_horizontal(is_null())",
         r="""
             list(`rows with an empty cell` = sum(!complete.cases(data.frame(age, bmi, hyp, chl))), rows = length(age))
         """)

    # ---------------------------------------------------------------- pandas only (the box shows pandas alone)
    out.append(Case(
        "table.count_rows", "warpbreaks: looms for each wool and tension, with the totals", "warpbreaks", "real data",
        option="with_totals=",
        ours="""
            t = sdata.table(data).count_rows(for_each_group_in="wool", across="tension", with_totals=True)
            found = {"columns": len(t.get_column_names())}
            for i in range(1, t.count_rows() + 1):
                w = t.get_cell_at(row=i, column="wool")
                found.update({f"{w}, {k}": t.get_cell_at(row=i, column=k) for k in ("L", "M", "H", "(total)")})
            found
        """,
        parent="""
            c = pd.crosstab(data["wool"], data["tension"], margins=True, margins_name="(total)").reset_index()
            found = {"columns": c.shape[1]}
            for _, row in c.iterrows():
                found.update({f"{row['wool']}, {k}": row[k] for k in ("L", "M", "H", "(total)")})
            found
        """, parent_label="pandas crosstab(margins=True, margins_name=\"(total)\")", parent_tolerance=0.0,
        r="""
            m <- addmargins(table(wool, tension))
            out <- list()
            for (w in rownames(m)) for (k in colnames(m)) {
              out[[paste0(ifelse(w == "Sum", "(total)", w), ", ", ifelse(k == "Sum", "(total)", k))]] <- m[w, k]
            }
            out
        """, r_tolerance=0.0,
        note="R addmargins() names its totals \"Sum\"; simplydata and pandas (margins_name) call them \"(total)\". "
             "The R names are changed to \"(total)\" before the numbers are compared."))
    out.append(Case(
        "table.save", "mtcars saved twice into an SQLite file (two tables) and read back", "mtcars", "real data",
        option="in_table=",
        ours="""
            import os
            import tempfile
            with tempfile.TemporaryDirectory() as folder:
                results = os.path.join(folder, "results.sqlite")
                t = sdata.table(data)
                t.save(results, in_table="cars")
                t.save(results, in_table="cars_again")
                back = sdata.table(results, table_name="cars_again")
                found = {"rows": back.count_rows(), "columns": len(back.get_column_names()),
                         "total hp": back.get_column("hp").find_total(), "total wt": back.get_column("wt").find_total(),
                         "row 3": float(back.get_cell_at(row=3, column="model") == "Datsun 710")}
            found
        """,
        parent="""
            import os
            import sqlite3
            import tempfile
            with tempfile.TemporaryDirectory() as folder:
                con = sqlite3.connect(os.path.join(folder, "results.sqlite"))
                data.to_sql("cars", con, if_exists="replace", index=False)
                data.to_sql("cars_again", con, if_exists="replace", index=False)
                back = pd.read_sql_query('SELECT * FROM "cars_again"', con)
                con.close()
            {"rows": len(back), "columns": back.shape[1], "total hp": back["hp"].sum(), "total wt": back["wt"].sum(),
             "row 3": float(back["model"].iloc[2] == "Datsun 710")}
        """, parent_label="pandas to_sql, read_sql_query (sqlite3)", parent_tolerance=1e-12))
    out.append(Case(
        "table.show_differences_from", "mtcars with horsepower capped at 200, against mtcars", "mtcars", "real data",
        ours=_printed('t.show_differences_from(sdata.table(data))', """
            import re
            n = [int(x) for x in re.findall(r"\\d+", lines[0])[:2]]
            {"cells that differ": n[0], "rows that differ": n[1]}
        """).replace("import contextlib", 't = sdata.table(data).replace_values_in("hp", is_above=200, '
                                          'with_value=200)\nimport contextlib', 1),
        parent="""
            d = data.copy()
            d.loc[d["hp"] > 200, "hp"] = 200
            cells = d.compare(data, result_names=("this", "other"))
            {"cells that differ": int(cells.xs("this", axis=1, level=1).notna().sum().sum()), "rows that differ": len(cells)}
        """, parent_label="pandas compare", parent_tolerance=0.0,
        r="""
            list(`cells that differ` = sum(hp > 200), `rows that differ` = sum(hp > 200))
        """, r_tolerance=0.0))
    return out
