"""The reliability study for the families for 100 % plan, batches 1-2 (approved by Manish 2026-11-28): the table words
and options for the pandas and Polars gaps, and the seaborn.objects marks and moves, each run on real, published data.

cases_underneath.py loads this file and adds the cases. Each word is compared with the library its box names: pandas,
and Polars in a second case (simplydata then gets a Polars table, so the Polars side of the word is checked as well),
seaborn for the chart words, and base R where R does the same thing in a few plain lines. The datasets are the
study's own (validation/README.md): mtcars, iris, warpbreaks, AirPassengers, Seatbelts and Lake Huron.

The simplydata side reads its results only with simplydata words (get_column, get_cell_at, count_rows ...). Text
results are counted (how many values, the position of a value), so a value that differs is a count that differs.
"""

from __future__ import annotations

import textwrap


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(p).strip("\n") for p in parts if p and p.strip())


def _both(Case, word, title, dataset, kind, *, ours, pandas, pandas_label, polars, polars_label, setup="",
          r="", r_tolerance=0.0, tolerance=0.0, option="", note=""):
    """Two cases: simplydata on a pandas table against pandas (and R), and on a Polars table against Polars.

    setup (pandas) prepares the input for both sides; then `source` is the table simplydata gets: the pandas table
    itself, or the same table as Polars (pl.from_pandas). The Polars side starts from the same Polars table."""
    pandas_case = Case(word, title, dataset, kind, ours=_code(setup, "source = data", ours),
                       parent=_code(setup, pandas), parent_label=pandas_label, parent_tolerance=tolerance,
                       r=r, r_tolerance=r_tolerance, option=option, note=note)
    polars_case = Case(word, title + " (a Polars table)", dataset, kind,
                       ours=_code(setup, "import polars as pl", "source = pl.from_pandas(data)", ours),
                       parent=_code(setup, "import polars as pl", "df = pl.from_pandas(data)", polars),
                       parent_label=polars_label, parent_tolerance=tolerance, option=option)
    return [pandas_case, polars_case]


def _new_table_words(Case):
    out = []

    def both(*args, **kwargs):
        out.extend(_both(Case, *args, **kwargs))

    both("table.get_different_values_in", "iris: the three species, each once, in the order they first turn up",
         "iris", "real data",
         ours="""
             v = sdata.table(source).get_different_values_in("Species")
             {"different species": len(v), "place of setosa": v.index("setosa") + 1,
              "place of versicolor": v.index("versicolor") + 1, "place of virginica": v.index("virginica") + 1}
         """,
         pandas="""
             v = list(data["Species"].dropna().unique())
             {"different species": len(v), "place of setosa": v.index("setosa") + 1,
              "place of versicolor": v.index("versicolor") + 1, "place of virginica": v.index("virginica") + 1}
         """, pandas_label="pandas Series.unique()",
         polars="""
             v = df["Species"].drop_nulls().unique(maintain_order=True).to_list()
             {"different species": len(v), "place of setosa": v.index("setosa") + 1,
              "place of versicolor": v.index("versicolor") + 1, "place of virginica": v.index("virginica") + 1}
         """, polars_label="Polars Series.unique(maintain_order=True)",
         r="""
             v <- unique(as.character(Species))
             list(`different species` = length(v), `place of setosa` = match("setosa", v),
                  `place of versicolor` = match("versicolor", v), `place of virginica` = match("virginica", v))
         """)
    both("table.get_different_values_in", "mtcars: the different numbers of cylinders, as numbers, in the order they "
         "first turn up", "mtcars", "real data",
         ours="""
             v = sdata.table(source).get_different_values_in("cyl")
             {"different values": v.count(), "first": v.get_number_at(1), "second": v.get_number_at(2),
              "third": v.get_number_at(3)}
         """,
         pandas="""
             v = data["cyl"].dropna().unique()
             {"different values": len(v), "first": v[0], "second": v[1], "third": v[2]}
         """, pandas_label="pandas Series.unique()",
         polars="""
             v = df["cyl"].drop_nulls().unique(maintain_order=True)
             {"different values": len(v), "first": v[0], "second": v[1], "third": v[2]}
         """, polars_label="Polars Series.unique(maintain_order=True)",
         r="""
             v <- unique(cyl)
             list(`different values` = length(v), first = v[1], second = v[2], third = v[3])
         """)
    both("table.check_if_all_values_in", "mtcars: does every car do more than 10 miles per gallon, and more than 15?",
         "mtcars", "real data",
         ours="""
             t = sdata.table(source)
             {"every car above 10 mpg": float(t.check_if_all_values_in("mpg", is_above=10)),
              "every car above 15 mpg": float(t.check_if_all_values_in("mpg", is_above=15))}
         """,
         pandas="""
             {"every car above 10 mpg": float((data["mpg"].dropna() > 10).all()),
              "every car above 15 mpg": float((data["mpg"].dropna() > 15).all())}
         """, pandas_label="pandas Series.all()",
         polars="""
             {"every car above 10 mpg": float(df.select((pl.col("mpg") > 10).all()).item()),
              "every car above 15 mpg": float(df.select((pl.col("mpg") > 15).all()).item())}
         """, polars_label="Polars Expr.all()",
         r="""
             list(`every car above 10 mpg` = as.numeric(all(mpg > 10)), `every car above 15 mpg` = as.numeric(all(mpg > 15)))
         """)
    both("table.check_if_any_value_in", "mtcars: is any car above 300 horsepower, or above 400?", "mtcars",
         "real data",
         ours="""
             t = sdata.table(source)
             {"a car above 300 hp": float(t.check_if_any_value_in("hp", is_above=300)),
              "a car above 400 hp": float(t.check_if_any_value_in("hp", is_above=400))}
         """,
         pandas="""
             {"a car above 300 hp": float((data["hp"].dropna() > 300).any()),
              "a car above 400 hp": float((data["hp"].dropna() > 400).any())}
         """, pandas_label="pandas Series.any()",
         polars="""
             {"a car above 300 hp": float(df.select((pl.col("hp") > 300).any()).item()),
              "a car above 400 hp": float(df.select((pl.col("hp") > 400).any()).item())}
         """, polars_label="Polars Expr.any()",
         r="""
             list(`a car above 300 hp` = as.numeric(any(hp > 300)), `a car above 400 hp` = as.numeric(any(hp > 400)))
         """)
    both("table.check_if_sorted_by", "AirPassengers: the months are in order; the passenger counts are not",
         "AirPassengers", "real data",
         ours="""
             t = sdata.table(source)
             t.turn_into_dates("month")
             {"months in order": float(t.check_if_sorted_by("month")),
              "passengers in order": float(t.check_if_sorted_by("passengers")),
              "passengers in order, biggest first": float(t.check_if_sorted_by("passengers", biggest_first=True))}
         """,
         pandas="""
             months = pd.to_datetime(data["month"])
             {"months in order": float(months.is_monotonic_increasing),
              "passengers in order": float(data["passengers"].is_monotonic_increasing),
              "passengers in order, biggest first": float(data["passengers"].is_monotonic_decreasing)}
         """, pandas_label="pandas is_monotonic_increasing / is_monotonic_decreasing",
         polars="""
             months = df["month"].str.to_date()
             {"months in order": float(months.is_sorted()),
              "passengers in order": float(df["passengers"].is_sorted()),
              "passengers in order, biggest first": float(df["passengers"].is_sorted(descending=True))}
         """, polars_label="Polars Series.is_sorted()",
         r="""
             list(`months in order` = as.numeric(!is.unsorted(as.Date(month))),
                  `passengers in order` = as.numeric(!is.unsorted(passengers)),
                  `passengers in order, biggest first` = as.numeric(!is.unsorted(rev(passengers))))
         """)
    both("table.add_run_number_column", "mtcars: the runs of automatic and manual cars in the order of the table",
         "mtcars", "real data",
         ours="""
             t = sdata.table(source).add_run_number_column("run", from_column="am")
             run = t.get_column("run")
             {"runs": run.find_biggest(), "sum of row x run": sum(i * run.get_number_at(i) for i in range(1, 33))}
         """,
         pandas="""
             run = (data["am"] != data["am"].shift()).cumsum()
             {"runs": run.max(), "sum of row x run": sum(i * v for i, v in enumerate(run, 1))}
         """, pandas_label="pandas (s != s.shift()).cumsum()",
         polars="""
             run = df.select(pl.col("am").rle_id() + 1)["am"]
             {"runs": run.max(), "sum of row x run": sum(i * v for i, v in enumerate(run, 1))}
         """, polars_label="Polars rle_id() + 1",
         r="""
             r <- rle(am)
             run <- rep(seq_along(r$lengths), r$lengths)
             list(runs = max(run), `sum of row x run` = sum(seq_along(run) * run))
         """)
    both("table.turn_into_title_case", "mtcars: the 32 car names in small letters, then in Title Case", "mtcars",
         "real data",
         ours="""
             t = sdata.table(source)
             t.turn_into_lowercase("model")
             t.turn_into_title_case("model")
             names = t.get_column("model")
             {"names as before": sum(a == b for a, b in zip(names, list(data["model"]))),
              "capital letters": sum(c.isupper() for n in names for c in n),
              "Merc 450Slc": float("Merc 450Slc" in names), "Mazda Rx4": float("Mazda Rx4" in names)}
         """,
         pandas="""
             names = list(data["model"].str.lower().str.title())
             {"names as before": sum(a == b for a, b in zip(names, list(data["model"]))),
              "capital letters": sum(c.isupper() for n in names for c in n),
              "Merc 450Slc": float("Merc 450Slc" in names), "Mazda Rx4": float("Mazda Rx4" in names)}
         """, pandas_label="pandas str.title()",
         polars="""
             names = df["model"].str.to_lowercase().str.to_titlecase().to_list()
             {"names as before": sum(a == b for a, b in zip(names, list(data["model"]))),
              "capital letters": sum(c.isupper() for n in names for c in n),
              "Merc 450Slc": float("Merc 450Slc" in names), "Mazda Rx4": float("Mazda Rx4" in names)}
         """, polars_label="Polars str.to_titlecase()")
    return out


def cases(Case):
    return _new_table_words(Case) + _new_options(Case) + _chart_options(Case)


def _new_options(Case):
    out = []

    def both(*args, **kwargs):
        out.extend(_both(Case, *args, **kwargs))

    growth = 'data = data.assign(ratio=data["passengers"] / data["passengers"].shift(1))'
    both("table.find_summary_of", "AirPassengers: the product of the 143 monthly growth ratios (the last month over "
         "the first)", "AirPassengers", "real data", option='show="product"', setup=growth, tolerance=1e-12,
         ours="""
             r = sdata.table(source).find_summary_of("ratio", show=["product"])
             {"product": r.get_cell_at(row=1, column="product")}
         """,
         pandas='{"product": data["ratio"].prod()}', pandas_label="pandas Series.prod()",
         polars='{"product": df["ratio"].drop_nulls().product()}', polars_label="Polars Series.product()",
         r="list(product = prod(passengers[-1] / passengers[-length(passengers)]))", r_tolerance=1e-12)
    both("table.find_summary_of", "warpbreaks: the Shannon entropy of the breaks of each wool", "warpbreaks",
         "real data", option='show="entropy"', tolerance=1e-12,
         ours="""
             r = sdata.table(source).find_summary_of("breaks", show=["entropy"], for_each_group_in="wool")
             {"wool A": r.get_cell_at(row=1, column="entropy"), "wool B": r.get_cell_at(row=2, column="entropy")}
         """,
         pandas="""
             from scipy import stats
             e = data.groupby("wool")["breaks"].apply(lambda b: stats.entropy(b))
             {"wool A": e["A"], "wool B": e["B"]}
         """, pandas_label="SciPy stats.entropy on each wool",
         polars="""
             e = df.group_by("wool").agg(pl.col("breaks").entropy()).sort("wool")["breaks"]
             {"wool A": e[0], "wool B": e[1]}
         """, polars_label="Polars Expr.entropy()",
         r="""
             h <- function(b) { p <- b / sum(b); -sum(p * log(p)) }
             list(`wool A` = h(breaks[wool == "A"]), `wool B` = h(breaks[wool == "B"]))
         """, r_tolerance=1e-12)
    both("table.find_summary_of", "mtcars: the names of the cars of each number of cylinders, joined into one text",
         "mtcars", "real data", option='show="joined text"',
         ours="""
             r = sdata.table(source).find_summary_of("model", show=["joined text"], separator=", ",
                                                     for_each_group_in="cyl")
             {f"{c} cylinders: letters": len(r.get_cell_at(row=i, column="joined text"))
              for i, c in enumerate((4, 6, 8), 1)}
         """,
         pandas="""
             j = data.groupby("cyl")["model"].agg(", ".join)
             {f"{c} cylinders: letters": len(j[c]) for c in (4, 6, 8)}
         """, pandas_label='pandas groupby().agg(", ".join)',
         polars="""
             j = df.group_by("cyl", maintain_order=True).agg(pl.col("model").str.join(", ")).sort("cyl")["model"]
             {f"{c} cylinders: letters": len(j[i]) for i, c in enumerate((4, 6, 8))}
         """, polars_label="Polars str.join",
         r="""
             n <- function(k) nchar(paste(model[cyl == k], collapse = ", "))
             list(`4 cylinders: letters` = n(4), `6 cylinders: letters` = n(6), `8 cylinders: letters` = n(8))
         """)
    both("table.find_summary_of", "mtcars: the average fuel use and the most horsepower for each number of cylinders "
         "(a measure for each column)", "mtcars", "real data", option="show={column: measures}", tolerance=1e-12,
         ours="""
             r = sdata.table(source).find_summary_of(show={"mpg": ["average"], "hp": ["biggest"]},
                                                     for_each_group_in="cyl")
             found = {}
             for i, c in enumerate((4, 6, 8), 1):
                 found[f"{c} cylinders: average mpg"] = r.get_cell_at(row=i, column="mpg average")
                 found[f"{c} cylinders: most hp"] = r.get_cell_at(row=i, column="hp biggest")
             found
         """,
         pandas="""
             g = data.groupby("cyl").agg(mpg=("mpg", "mean"), hp=("hp", "max"))
             found = {}
             for c in (4, 6, 8):
                 found[f"{c} cylinders: average mpg"] = g.loc[c, "mpg"]
                 found[f"{c} cylinders: most hp"] = g.loc[c, "hp"]
             found
         """, pandas_label="pandas named aggregation",
         polars="""
             g = df.group_by("cyl").agg(pl.col("mpg").mean(), pl.col("hp").max()).sort("cyl")
             found = {}
             for i, c in enumerate((4, 6, 8)):
                 found[f"{c} cylinders: average mpg"] = g["mpg"][i]
                 found[f"{c} cylinders: most hp"] = g["hp"][i]
             found
         """, polars_label="Polars group_by().agg()",
         r="""
             m <- tapply(mpg, cyl, mean); h <- tapply(hp, cyl, max)
             list(`4 cylinders: average mpg` = m[["4"]], `6 cylinders: average mpg` = m[["6"]],
                  `8 cylinders: average mpg` = m[["8"]], `4 cylinders: most hp` = h[["4"]],
                  `6 cylinders: most hp` = h[["6"]], `8 cylinders: most hp` = h[["8"]])
         """, r_tolerance=1e-12)
    both("table.add_previous_value_column", "AirPassengers: next month's passengers next to each month",
         "AirPassengers", "real data", option="rows_ahead=",
         ours="""
             t = sdata.table(source).add_previous_value_column("next", from_column="passengers", rows_ahead=1)
             n = t.get_column("next")
             {"empty": n.count_empty_numbers(), "first": n.get_number_at(1),
              "total of next": n.remove_empty_numbers().find_total()}
         """,
         pandas="""
             n = data["passengers"].shift(-1)
             {"total of next": n.sum(), "empty": n.isna().sum(), "first": n.iloc[0]}
         """, pandas_label="pandas shift(-1)",
         polars="""
             n = df["passengers"].shift(-1)
             {"total of next": n.sum(), "empty": n.null_count(), "first": n[0]}
         """, polars_label="Polars shift(-1)",
         r="""
             n <- c(passengers[-1], NA)
             list(`total of next` = sum(n, na.rm = TRUE), empty = sum(is.na(n)), first = n[1])
         """)
    both("table.round_numbers_in", "mtcars: the weights to 2 significant figures", "mtcars", "real data",
         option="significant_figures=", tolerance=1e-12,
         ours="""
             w = sdata.table(source).round_numbers_in("wt", significant_figures=2).get_column("wt")
             {"total": w.find_total(), "first": w.get_number_at(1), "heaviest": w.find_biggest()}
         """,
         pandas="""
             from decimal import ROUND_HALF_EVEN, Decimal
             q = [Decimal(repr(v)) for v in data["wt"]]
             w = [float(d.quantize(Decimal(1).scaleb(d.adjusted() - 1), rounding=ROUND_HALF_EVEN)) for d in q]
             {"total": sum(w), "first": w[0], "heaviest": max(w)}
         """,
         pandas_label="Python decimal, a half to the even digit (pandas has no such word)",
         polars="""
             w = df["wt"].round_sig_figs(2).to_list()
             w = [5.2 if v == 5.3 and x == 5.25 else v for v, x in zip(w, df["wt"])]
             {"total": sum(w), "first": w[0], "heaviest": max(w)}
         """, polars_label="Polars round_sig_figs(2), with its one half (5.25) taken to the even digit",
         note="Polars round_sig_figs takes a half away from 0 (5.25 becomes 5.3); simplydata and R signif() take "
              "it to the even digit (5.2), as round_numbers_in rounds every half.",
         r="""
             w <- signif(wt, 2)
             list(total = sum(w), first = w[1], heaviest = max(w))
         """, r_tolerance=1e-12)
    arrivals = 'data = data.assign(time=pd.Timestamp("2026-01-01") + pd.to_timedelta((data["hour"] * 3600).round(), unit="s"))'
    both("table.keep_rows_where", "ICU arrivals: the patients who arrived between 08:00 and 17:00",
         "ICU arrivals (circular)", "real data", option="time_of_day_between=", setup=arrivals,
         ours="""
             t = sdata.table(source).keep_rows_where("time", time_of_day_between=["08:00", "17:00"])
             {"arrivals": t.count_rows(), "total hours": t.get_column("hour").find_total()}
         """,
         pandas="""
             k = data.set_index("time", drop=False).between_time("08:00", "17:00")
             {"arrivals": len(k), "total hours": k["hour"].sum()}
         """, pandas_label="pandas between_time", tolerance=1e-12,
         polars="""
             import datetime
             k = df.filter(pl.col("time").dt.time().is_between(datetime.time(8), datetime.time(17)))
             {"arrivals": len(k), "total hours": k["hour"].sum()}
         """, polars_label="Polars dt.time().is_between()",
         r="""
             s <- round(hour * 3600) %% 86400
             k <- s >= 8 * 3600 & s <= 17 * 3600
             list(arrivals = sum(k), `total hours` = sum(hour[k]))
         """, r_tolerance=1e-12)
    both("table.add_column_with_part_of_text", "mtcars: every number in the car names", "mtcars", "real data",
         option="every_match=",
         ours="""
             t = sdata.table(source).add_column_with_part_of_text("numbers", from_column="model",
                                                                  matches_pattern="[0-9]+", every_match=True)
             v = [x for x in t.get_column("numbers") if x is not None]
             {"names with a number": len(v), "numbers": sum(len(x.split(";")) for x in v),
              "total of the numbers": sum(int(p) for x in v for p in x.split(";"))}
         """,
         pandas="""
             f = data["model"].str.findall("[0-9]+")
             v = [x for x in f if x]
             {"names with a number": len(v), "numbers": sum(len(x) for x in v),
              "total of the numbers": sum(int(p) for x in v for p in x)}
         """, pandas_label="pandas str.findall",
         polars="""
             f = df["model"].str.extract_all("[0-9]+").to_list()
             v = [x for x in f if x]
             {"names with a number": len(v), "numbers": sum(len(x) for x in v),
              "total of the numbers": sum(int(p) for x in v for p in x)}
         """, polars_label="Polars str.extract_all",
         r="""
             m <- regmatches(model, gregexpr("[0-9]+", model))
             k <- lengths(m) > 0
             list(`names with a number` = sum(k), numbers = sum(lengths(m)),
                  `total of the numbers` = sum(as.numeric(unlist(m))))
         """)
    both("table.add_column_with_part_of_text", 'mtcars: where "a" first comes in each car name', "mtcars",
         "real data", option="position_of=",
         ours="""
             t = sdata.table(source).add_column_with_part_of_text("at", from_column="model", position_of="a")
             p = t.get_column("at")
             {"names with an a": p.count() - p.count_empty_numbers(), "total of the places": p.remove_empty_numbers().find_total()}
         """,
         pandas="""
             f = data["model"].str.find("a") + 1
             {"names with an a": (f > 0).sum(), "total of the places": f[f > 0].sum()}
         """, pandas_label="pandas str.find + 1",
         polars="""
             f = df["model"].str.find("a", literal=True) + 1
             {"names with an a": f.drop_nulls().len(), "total of the places": f.sum()}
         """, polars_label="Polars str.find + 1 (the names are plain letters, so bytes are characters)",
         r="""
             f <- regexpr("a", model, fixed = TRUE)
             list(`names with an a` = sum(f > 0), `total of the places` = sum(f[f > 0]))
         """)
    months = 'data = data.assign(month=pd.to_datetime(data["month"]))'
    both("table.add_column_with_part_of_date", "AirPassengers: the months that start a month, a quarter and a year",
         "AirPassengers", "real data", option='part="is month start"', setup=months,
         ours="""
             t = sdata.table(source)
             found = {}
             for part in ("is month start", "is quarter start", "is year start", "is year end"):
                 t.add_column_with_part_of_date("x", from_column="month", part=part)
                 found[part] = sum(bool(v) for v in t.get_column("x"))
             found
         """,
         pandas="""
             d = data["month"].dt
             {"is month start": d.is_month_start.sum(), "is quarter start": d.is_quarter_start.sum(),
              "is year start": d.is_year_start.sum(), "is year end": d.is_year_end.sum()}
         """, pandas_label="pandas dt.is_month_start, is_quarter_start, is_year_start, is_year_end",
         polars="""
             d = df["month"]
             {"is month start": (d.dt.day() == 1).sum(),
              "is quarter start": ((d.dt.day() == 1) & d.dt.month().is_in([1, 4, 7, 10])).sum(),
              "is year start": ((d.dt.day() == 1) & (d.dt.month() == 1)).sum(),
              "is year end": ((d.dt.day() == 31) & (d.dt.month() == 12)).sum()}
         """, polars_label="Polars dt.day() and dt.month()",
         r="""
             d <- as.POSIXlt(as.Date(month))
             list(`is month start` = sum(d$mday == 1), `is quarter start` = sum(d$mday == 1 & d$mon %in% c(0, 3, 6, 9)),
                  `is year start` = sum(d$mday == 1 & d$mon == 0), `is year end` = sum(d$mday == 31 & d$mon == 11))
         """)
    both("table.add_column_with_part_of_date", "AirPassengers: how many months start on a working day (Monday to "
         "Friday)", "AirPassengers", "real data", option='part="is working day"', setup=months,
         ours="""
             t = sdata.table(source).add_column_with_part_of_date("w", from_column="month", part="is working day")
             {"months starting on a working day": sum(bool(v) for v in t.get_column("w"))}
         """,
         pandas='{"months starting on a working day": np.is_busday(data["month"].values.astype("datetime64[D]")).sum()}',
         pandas_label="NumPy is_busday",
         polars='{"months starting on a working day": df["month"].dt.is_business_day().sum()}',
         polars_label="Polars dt.is_business_day()",
         r="""
             w <- as.POSIXlt(as.Date(month))$wday
             list(`months starting on a working day` = sum(w %in% 1:5))
         """)
    both("table.add_column_with_part_of_date", "AirPassengers: each month as Unix seconds", "AirPassengers",
         "real data", option='part="unix time"', setup=months,
         ours="""
             s = sdata.table(source).add_column_with_part_of_date("s", from_column="month", part="unix time")
             s = s.get_column("s")
             {"first": s.get_number_at(1), "last": s.get_number_at(144), "total": s.find_total()}
         """,
         pandas="""
             s = (data["month"] - pd.Timestamp("1970-01-01")) // pd.Timedelta(seconds=1)
             {"first": s.iloc[0], "last": s.iloc[-1], "total": s.sum()}
         """, pandas_label="pandas (date - 1970-01-01) // 1 second",
         polars="""
             s = df["month"].dt.epoch("s")
             {"first": s[0], "last": s[-1], "total": s.sum()}
         """, polars_label='Polars dt.epoch("s")',
         r="""
             s <- as.numeric(as.POSIXct(as.Date(month), tz = "UTC"))
             list(first = s[1], last = s[length(s)], total = sum(s))
         """)
    seconds = ('data = data.assign(seconds=(pd.to_datetime(data["month"]) - pd.Timestamp("1970-01-01")) '
               '// pd.Timedelta(seconds=1))')
    both("table.turn_into_dates", "AirPassengers: the months written as Unix seconds, read back as dates",
         "AirPassengers", "real data", option="from_unix_seconds=", setup=seconds,
         ours="""
             t = sdata.table(source).turn_into_dates("seconds", from_unix_seconds=True)
             t.add_column_with_part_of_date("y", from_column="seconds", part="year")
             t.add_column_with_part_of_date("m", from_column="seconds", part="month")
             {"total of the years": t.get_column("y").find_total(), "total of the months": t.get_column("m").find_total()}
         """,
         pandas="""
             d = pd.to_datetime(data["seconds"], unit="s")
             {"total of the years": d.dt.year.sum(), "total of the months": d.dt.month.sum()}
         """, pandas_label='pandas to_datetime(unit="s")',
         polars="""
             d = pl.from_epoch(df["seconds"], time_unit="s")
             {"total of the years": d.dt.year().cast(pl.Int64).sum(), "total of the months": d.dt.month().cast(pl.Int64).sum()}
         """, polars_label='Polars from_epoch(time_unit="s")',
         r="""
             d <- as.POSIXlt(as.Date(month))
             list(`total of the years` = sum(d$year + 1900), `total of the months` = sum(d$mon + 1))
         """)
    both("table.add_column", "mtcars: the tens of miles per gallon (floor) and log(1 + horsepower)", "mtcars",
         "real data", option="floor() ceil() log10() log1p() sign() cbrt()", tolerance=1e-12,
         ours="""
             t = sdata.table(source)
             t.add_column("tens", "floor(mpg / 10)")
             t.add_column("log_hp", "log1p(hp)")
             t.add_column("root", "cbrt(disp)")
             {"total of tens": t.get_column("tens").find_total(), "total of log1p": t.get_column("log_hp").find_total(),
              "total of cube roots": t.get_column("root").find_total()}
         """,
         pandas="""
             {"total of tens": np.floor(data["mpg"] / 10).sum(), "total of log1p": np.log1p(data["hp"]).sum(),
              "total of cube roots": np.cbrt(data["disp"]).sum()}
         """, pandas_label="NumPy floor, log1p, cbrt",
         polars="""
             {"total of tens": (df["mpg"] / 10).floor().sum(), "total of log1p": df["hp"].log1p().sum(),
              "total of cube roots": df["disp"].cbrt().sum()}
         """, polars_label="Polars floor, log1p, cbrt",
         r="""
             list(`total of tens` = sum(floor(mpg / 10)), `total of log1p` = sum(log1p(hp)),
                  `total of cube roots` = sum(disp^(1/3)))
         """, r_tolerance=1e-12)
    both("table.add_column", "AirPassengers: the date 10 working days after the start of each month",
         "AirPassengers", "real data", option="add_working_days() count_working_days()", setup=months,
         ours="""
             t = sdata.table(source)
             t.add_column("due", "add_working_days(month, 10)")
             t.add_column("days", "count_working_days(month, due)")
             t.add_column_with_part_of_date("d", from_column="due", part="day")
             {"total of the days of the month": t.get_column("d").find_total(),
              "total working days counted": t.get_column("days").find_total()}
         """,
         pandas="""
             start = data["month"].values.astype("datetime64[D]")
             due = np.busday_offset(start, 10, roll="forward")
             {"total of the days of the month": int(pd.DatetimeIndex(due).day.to_numpy().sum()),
              "total working days counted": np.busday_count(start, due).sum()}
         """, pandas_label='NumPy busday_offset(roll="forward") and busday_count',
         polars="""
             due = df.select(pl.col("month").dt.add_business_days(10, roll="forward"))["month"]
             {"total of the days of the month": due.dt.day().cast(pl.Int64).sum(),
              "total working days counted": df.select(pl.business_day_count(pl.col("month").cast(pl.Date),
                  pl.col("month").dt.add_business_days(10, roll="forward").cast(pl.Date)))["month"].sum()}
         """, polars_label="Polars dt.add_business_days and business_day_count")
    out.append(Case("sdata.make_run_of_dates", "AirPassengers: the working days from its first to its last month",
                    "AirPassengers", "real data", option='every="working day"',
                    ours="""
                        t = sdata.make_run_of_dates(data["month"].iloc[0], to=data["month"].iloc[-1],
                                                    every="working day")
                        {"working days": t.count_rows()}
                    """,
                    parent="""
                        {"working days": len(pd.bdate_range(data["month"].iloc[0], data["month"].iloc[-1]))}
                    """, parent_label="pandas bdate_range",
                    r="""
                        d <- seq(as.Date(month[1]), as.Date(month[length(month)]), by = "day")
                        list(`working days` = sum(as.POSIXlt(d)$wday %in% 1:5))
                    """))
    both("table.add_rolling_column", "Seatbelts: the correlation of drivers and drivers killed over each 12 months",
         "Seatbelts", "real data", option="with_column=", tolerance=1e-9,
         ours="""
             t = sdata.table(source).add_rolling_column("link", from_column="drivers", with_column="DriversKilled",
                                                        show="correlation", window=12)
             r = t.get_column("link")
             {"last": r.get_number_at(192), "empty": r.count_empty_numbers(),
              "total": r.remove_empty_numbers().find_total()}
         """,
         pandas="""
             r = data["drivers"].rolling(12).corr(data["DriversKilled"])
             {"total": r.sum(), "last": r.iloc[-1], "empty": r.isna().sum()}
         """, pandas_label="pandas rolling(12).corr()",
         polars="""
             r = df.select(pl.rolling_corr("drivers", "DriversKilled", window_size=12))["drivers"]
             {"total": r.sum(), "last": r[-1], "empty": r.null_count()}
         """, polars_label="Polars rolling_corr",
         r="""
             r <- sapply(12:length(drivers), function(i) cor(drivers[(i - 11):i], DriversKilled[(i - 11):i]))
             list(total = sum(r), last = r[length(r)], empty = 11)
         """, r_tolerance=1e-9)
    periods = ('periods = pd.DataFrame({"start": pd.to_datetime(["1949-01-01", "1955-01-01"]), '
               '"end": pd.to_datetime(["1955-01-01", "1961-01-01"]), "half": [1, 2]})')
    both("table.join_with", "AirPassengers: each month paired with the half of the years it falls in", "AirPassengers",
         "real data", option="where=", setup=months + "\n" + periods,
         ours="""
             t = sdata.table(source).join_with(periods, where="month >= start and month < end")
             h = t.get_column("half")
             {"rows": t.count_rows(), "total of half": h.find_total()}
         """,
         pandas="""
             j = data.merge(periods, how="cross")
             j = j[(j["month"] >= j["start"]) & (j["month"] < j["end"])]
             {"rows": len(j), "total of half": j["half"].sum()}
         """, pandas_label='pandas merge(how="cross") then the condition',
         polars="""
             j = df.join_where(pl.from_pandas(periods), pl.col("month") >= pl.col("start"), pl.col("month") < pl.col("end"))
             {"rows": len(j), "total of half": j["half"].sum()}
         """, polars_label="Polars join_where",
         r="""
             y <- as.integer(substr(as.character(month), 1, 4))
             list(rows = length(y), `total of half` = sum(ifelse(y < 1955, 1, 2)))
         """)
    return out


def _chart_options(Case):
    def lines_of(code):
        return _code(code, """
            fig = chart.as_matplotlib()
            ax = fig.axes[0]
        """)

    return [
        Case("draw_lines", "mtcars: weight and fuel use joined in the order of the rows", "mtcars", "real data",
             option="in_row_order=",
             ours=lines_of("""
                 chart = sdata.chart(sdata.table(data))
                 chart.draw_lines(x="wt", y="mpg", in_row_order=True)
             """) + """
xy = ax.lines[0].get_xydata()
{"points": len(xy), "row x weight": float((np.arange(1, len(xy) + 1) * xy[:, 0]).sum()), "first mpg": float(xy[0, 1])}""",
             parent="""
                 import matplotlib.pyplot as plt
                 import seaborn as sns
                 fig, ax = plt.subplots()
                 sns.lineplot(data, x="wt", y="mpg", sort=False, estimator=None, errorbar=None, ax=ax)
                 xy = ax.lines[0].get_xydata()
                 plt.close(fig)
                 {"points": len(xy), "row x weight": float((np.arange(1, len(xy) + 1) * xy[:, 0]).sum()),
                  "first mpg": float(xy[0, 1])}
             """, parent_label="seaborn lineplot(sort=False, estimator=None), as so.Path", parent_tolerance=1e-12,
             r="""
                 list(points = length(wt), `row x weight` = sum(seq_along(wt) * wt), `first mpg` = mpg[1])
             """, r_tolerance=1e-12),
        Case("draw_dots", "mtcars: fuel use against weight, the dots moved 0.5 along x", "mtcars", "real data",
             option="move_layer_by=",
             ours=lines_of("""
                 chart = sdata.chart(sdata.table(data))
                 chart.draw_dots(x="wt", y="mpg", move_layer_by=0.5)
             """) + """
xy = ax.collections[0].get_offsets()
{"dots": len(xy), "sum of x": float(xy[:, 0].sum()), "sum of y": float(xy[:, 1].sum())}""",
             parent="""
                 import matplotlib.pyplot as plt
                 import seaborn as sns
                 fig, ax = plt.subplots()
                 sns.scatterplot(data.assign(wt=data["wt"] + 0.5), x="wt", y="mpg", ax=ax)
                 xy = ax.collections[0].get_offsets()
                 plt.close(fig)
                 {"dots": len(xy), "sum of x": float(xy[:, 0].sum()), "sum of y": float(xy[:, 1].sum())}
             """, parent_label="seaborn scatterplot of x + 0.5, as so.Shift(x=0.5)", parent_tolerance=1e-12,
             r="list(dots = length(wt), `sum of x` = sum(wt + 0.5), `sum of y` = sum(mpg))", r_tolerance=1e-12),
        Case("draw_dashes", "iris: a dash for the sepal length of each flower, by species", "iris", "real data",
             ours=lines_of("""
                 chart = sdata.chart(sdata.table(data))
                 chart.draw_dashes(x="Species", y="Sepal.Length")
             """) + """
segments = np.concatenate([np.asarray(s) for s in ax.collections[0].get_segments()]).reshape(-1, 2, 2)
{"dashes": len(segments), "sum of y": float(segments[:, 0, 1].sum()),
 "sum of the middles": float(segments[:, :, 0].mean(axis=1).sum()), "width": float(segments[0, 1, 0] - segments[0, 0, 0])}""",
             parent="""
                 import matplotlib.pyplot as plt
                 import seaborn as sns
                 fig, ax = plt.subplots()
                 sns.stripplot(data, x="Species", y="Sepal.Length", jitter=False, ax=ax)
                 xy = np.concatenate([c.get_offsets() for c in ax.collections])
                 plt.close(fig)
                 {"dashes": len(xy), "sum of y": float(xy[:, 1].sum()), "sum of the middles": float(xy[:, 0].sum()),
                  "width": 0.8}
             """, parent_label="seaborn stripplot(jitter=False): the places so.Dash puts its dashes",
             parent_tolerance=1e-12,
             r="""
                 list(dashes = length(Sepal.Length), `sum of y` = sum(Sepal.Length),
                      `sum of the middles` = sum(match(Species, unique(Species)) - 1), width = 0.8)
             """, r_tolerance=1e-12),
    ]
