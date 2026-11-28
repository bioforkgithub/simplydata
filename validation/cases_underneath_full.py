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
    return _new_table_words(Case)
