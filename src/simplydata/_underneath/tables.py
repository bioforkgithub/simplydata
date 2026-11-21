"""Table words: the same step in pandas, then in Polars.

simplydata runs each table step through narwhals, which passes it to pandas or Polars (whichever holds
the table). narwhals is plumbing and is not shown; the test runs each word on a pandas and on a Polars
table.
"""

from . import Entry

ENTRIES = [
    Entry(
        word="table.keep_rows_where",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.keep_rows_where("marks", is_above=50)
        """,
        code={
            "pandas": """
                df = sdata.get_example("marks")
                # keep_rows_where("marks", is_above=50)
                df[df["marks"] > 50]                 # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.from_pandas(sdata.get_example("marks"))
                # keep_rows_where("marks", is_above=50)
                df.filter(pl.col("marks") > 50)      # (1)
            """,
        },
        compare="table",
        choices=("is_above= means strictly above (>); use is_at_least= for >=. Rows with an empty cell in "
                 "\"marks\" are left out, as in pandas and Polars.",),
        also="simplydata also says how many rows it kept, and keeps the table before the step (undo).",
    ),
    Entry(
        word="table.find_average_of",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.find_average_of("marks", for_each_group_in="class")
        """,
        code={
            "pandas": """
                df = sdata.get_example("marks")
                # find_average_of("marks", for_each_group_in="class")
                df.groupby("class", sort=False)["marks"].mean().reset_index()   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.from_pandas(sdata.get_example("marks"))
                # find_average_of("marks", for_each_group_in="class")
                df.group_by("class", maintain_order=True).agg(pl.col("marks").mean())   # (1)
            """,
        },
        compare="table",
        names={"average of marks": "marks"},
        choices=("groups stay in the order they first appear (sort=False, maintain_order=True); empty cells are "
                 "skipped, as pandas and Polars do (NumPy's mean would give nan).",),
        also="simplydata also names the column \"average of marks\" and writes the averages in a sentence.",
    ),
]


# ---------------------------------------------------------------- U1: the table words of the 30 days
SAID = "simplydata also says in a sentence what changed, and keeps the table before the step (undo)."

ENTRIES += [
    Entry(
        word="table.show_first_rows",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.show_first_rows(3)
        """,
        code={"pandas": """
            df = sdata.get_example("marks")
            # show_first_rows(rows=3)
            first = df.head(3)
            first.index = range(1, 4)        # (1)
            print(first)
        """},
        compare="printed",
        choices=("the rows are numbered from 1, the way people count; pandas numbers them from 0. Only what is "
                 "shown changes: as_pandas() still gives the table with pandas' own row labels.",),
        also="A Polars table has no row labels, so simplydata shows it through pandas with the same numbers. In "
             "Jupyter or VS Code the rows are shown as a table instead of text.",
    ),
    Entry(
        word="table.describe_columns",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.describe_columns()
        """,
        code={"pandas": """
            import pandas as pd
            df = sdata.get_example("marks")
            # describe_columns()
            print(f"The table has {len(df)} rows and {df.shape[1]} columns.\\n")
            numbers = [c in df.select_dtypes("number") for c in df.columns]
            nice = lambda v: str(round(v, 2)).removesuffix(".0")      # (1)
            rows = [{"column": c, "kind": "number" if n else "text", "empty cells": df[c].isna().sum(),
                     "smallest": nice(df[c].min()) if n else "", "biggest": nice(df[c].max()) if n else "",
                     "average": nice(df[c].mean()) if n else "",
                     "different values": "" if n else str(df[c].nunique())}           # (2)
                    for c, n in zip(df.columns, numbers)]
            print(pd.DataFrame(rows).to_string(index=False))
        """},
        compare="printed",
        choices=("numbers are written for people: whole numbers without .0, others rounded to 2 decimals.",
                 "text columns get the number of different values (empty cells left out), number columns the "
                 "smallest, biggest and average (empty cells left out, as pandas does).",),
        also="Date columns get their first and last date, and true/false columns their number of different "
             "values; this table has neither. pandas' own df.describe() gives the numbers in another layout.",
    ),
    Entry(
        word="table.keep_columns",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.keep_columns("name", "marks")
        """,
        code={
            "pandas": """
                df = sdata.get_example("marks")
                # keep_columns("name", "marks")
                df[["name", "marks"]]
            """,
            "Polars": """
                import polars as pl
                df = pl.from_pandas(sdata.get_example("marks"))
                # keep_columns("name", "marks")
                df.select("name", "marks")
            """,
        },
        compare="table",
        also="The columns come in the order you list them. to=, of_kind=, starts_with= and the others choose "
             "columns by a run, a kind or their names. " + SAID,
    ),
    Entry(
        word="table.rename_column",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.rename_column("marks", to="score")
        """,
        code={
            "pandas": """
                df = sdata.get_example("marks")
                # rename_column("marks", to="score")
                df.rename(columns={"marks": "score"})
            """,
            "Polars": """
                import polars as pl
                df = pl.from_pandas(sdata.get_example("marks"))
                # rename_column("marks", to="score")
                df.rename({"marks": "score"})
            """,
        },
        compare="table",
        also="simplydata stops with a message when the new name is already a column (pandas would give two "
             "columns with one name). " + SAID,
    ),
    Entry(
        word="table.sort_by",
        data="shop",
        ours="""
            table = sdata.table(sdata.get_example("shop"))
            table.sort_by("sales", biggest_first=True)
        """,
        code={
            "pandas": """
                df = sdata.get_example("shop")
                # sort_by("sales", biggest_first=True)
                df.sort_values("sales", ascending=False, kind="stable",    # (1)
                               na_position="last")                         # (2)
            """,
            "Polars": """
                import polars as pl
                df = pl.from_pandas(sdata.get_example("shop"))
                # sort_by("sales", biggest_first=True)
                df.sort("sales", descending=True, maintain_order=True,     # (1)
                        nulls_last=True)                                   # (2)
            """,
        },
        compare="table",
        choices=("rows that tie keep the order they had (a stable sort); pandas' own default sort (quicksort) "
                 "does not promise that.",
                 "empty cells go last, also when the biggest come first (Polars' own default puts them first).",),
        also=SAID,
    ),
    Entry(
        word="table.keep_rows_by_position",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.keep_rows_by_position(10, to=20)
        """,
        code={
            "pandas": """
                df = sdata.get_example("marks")
                # keep_rows_by_position(10, to=20)
                df.iloc[9:20]                    # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.from_pandas(sdata.get_example("marks"))
                # keep_rows_by_position(10, to=20)
                df.slice(9, 11)                  # (1)
            """,
        },
        compare="table",
        choices=("rows are counted from 1 and both ends are kept, so rows 10 to 20 are 11 rows: Python's 9:20 "
                 "(it counts from 0 and leaves out the end); in Polars, 11 rows from row 9.",),
        also="step= keeps every n-th row and a list keeps those rows in that order. " + SAID,
    ),
    Entry(
        word="table.fill_empty_cells_in",
        data="shop",
        ours="""
            table = sdata.table(sdata.get_example("shop"))
            table.fill_empty_cells_in("customers", with_the="median")
        """,
        code={
            "pandas": """
                df = sdata.get_example("shop")
                # fill_empty_cells_in("customers", with_the="median")
                df.assign(customers=df["customers"].fillna(df["customers"].median()))   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.from_pandas(sdata.get_example("shop"))
                # fill_empty_cells_in("customers", with_the="median")
                df.with_columns(pl.col("customers").fill_null(pl.col("customers").median()))   # (1)
            """,
        },
        compare="table",
        choices=("the median of the filled cells of the whole column (the empty cells left out).",),
        also="with_the=\"value above\" and \"value below\" copy a neighbour (ffill, bfill), and \"line between "
             "neighbours\" draws a straight line across each gap. simplydata also says how many cells it filled.",
    ),
    Entry(
        word="table.turn_into_numbers",
        ours="""
            table = sdata.table({"price": ["12.5", "1,200", " 3 ", "n/a", None]})
            table.turn_into_numbers("price")
        """,
        code={"pandas": """
            import pandas as pd
            df = pd.DataFrame({"price": ["12.5", "1,200", " 3 ", "n/a", None]})
            # turn_into_numbers("price")
            text = df["price"].str.replace(r"\\s", "", regex=True)
            thousands = text.str.fullmatch(r"[+-]?\\d{1,3}(,\\d{3})+(\\.\\d+)?", na=False)   # (1)
            comma = text.str.fullmatch(r"[+-]?\\d*,\\d+", na=False) & ~thousands          # (2)
            text = text.where(~thousands, text.str.replace(",", ""))
            text = text.where(~comma, text.str.replace(",", "."))
            number = text.str.fullmatch(r"[+-]?(\\d+(\\.\\d*)?|\\.\\d+)([eE][+-]?\\d+)?", na=False)
            df.assign(price=text.where(number).astype(float))                          # (3)
        """},
        compare="table",
        choices=("a comma between groups of three digits is a thousands mark: 1,200 is twelve hundred.",
                 "any other single comma is a decimal comma: 12,5 is twelve and a half.",
                 "a cell that is not a number after that becomes empty, as pd.to_numeric(errors=\"coerce\"); "
                 "simplydata says how many and shows one.",),
        also="Spaces inside a number are left out first (1 200). A true/false column becomes 1 and 0, and a "
             "column that is already numbers is left as it is.",
    ),
    Entry(
        word="table.add_column",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.add_column("marks_per_hour", "marks / hours")
        """,
        code={
            "pandas": """
                df = sdata.get_example("marks")
                # add_column("marks_per_hour", "marks / hours")
                df.assign(marks_per_hour=df["marks"] / df["hours"])
            """,
            "Polars": """
                import polars as pl
                df = pl.from_pandas(sdata.get_example("marks"))
                # add_column("marks_per_hour", "marks / hours")
                df.with_columns((pl.col("marks") / pl.col("hours")).alias("marks_per_hour"))
            """,
        },
        compare="table",
        also="Dividing by zero gives an empty cell in simplydata (pandas gives inf); no hour is 0 here. The "
             "formula is read by simplydata itself, never run as Python code. " + SAID,
    ),
    Entry(
        word="table.add_group_column",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.add_group_column("grade", from_column="marks", cut_at=[40, 60, 80], names=["D", "C", "B", "A"])
        """,
        code={
            "pandas": """
                import numpy as np
                import pandas as pd
                df = sdata.get_example("marks")
                # add_group_column("grade", from_column="marks", cut_at=[40, 60, 80], names=[...])
                grade = pd.cut(df["marks"], [-np.inf, 40, 60, 80, np.inf],
                               labels=["D", "C", "B", "A"], right=False)       # (1)
                df.assign(grade=grade)
            """,
            "Polars": """
                import polars as pl
                df = pl.from_pandas(sdata.get_example("marks"))
                # add_group_column("grade", from_column="marks", cut_at=[40, 60, 80], names=[...])
                df.with_columns(pl.col("marks").cut([40, 60, 80], labels=["D", "C", "B", "A"],
                                                    left_closed=True).alias("grade"))   # (1)
            """,
        },
        compare="table",
        choices=("a value exactly on a cut goes into the higher group: a mark of 60 is a B (right=False, "
                 "left_closed=True); pandas and Polars put it in the lower group by default.",),
        also="simplydata makes a text column; pandas and Polars make a category column with the same values. "
             "Empty cells stay empty. " + SAID,
    ),
    Entry(
        word="table.find_summary_of",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.find_summary_of("marks", for_each_group_in="class", show=["average", "standard deviation", "count"])
        """,
        code={
            "pandas": """
                df = sdata.get_example("marks")
                # find_summary_of("marks", for_each_group_in="class", show=[...])
                out = df.groupby("class")["marks"].agg(["mean", "std", "count"])   # (1) (2)
                out.reset_index().assign(column="marks")[["column", "class", "mean", "std", "count"]]
            """,
            "Polars": """
                import polars as pl
                df = pl.from_pandas(sdata.get_example("marks"))
                # find_summary_of("marks", for_each_group_in="class", show=[...])
                m = pl.col("marks")
                out = df.group_by("class").agg(m.mean().alias("mean"), m.std().alias("std"),   # (2)
                                               m.count().alias("count")).sort("class")         # (1)
                out.select(pl.lit("marks").alias("column"), pl.all())
            """,
        },
        compare="table",
        names={"average": "mean", "standard deviation": "std"},
        choices=("one row for each group, the groups sorted (A, B, C).",
                 "the standard deviation of a sample (n - 1), as pandas, Polars and R sd(); NumPy's own default "
                 "is n.",),
        also="simplydata also writes the summary in a sentence; the result is a new table you can save or chart.",
    ),
    Entry(
        word="table.join_with",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.join_with({"name": ["Asha", "Ben"], "age": [12, 13]}, using="name", keep="all rows from this table")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = sdata.get_example("marks")
                ages = pd.DataFrame({"name": ["Asha", "Ben"], "age": [12, 13]})
                # join_with(ages, using="name", keep="all rows from this table")
                df.merge(ages, on="name", how="left", suffixes=("", "_other"))   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.from_pandas(sdata.get_example("marks"))
                ages = pl.DataFrame({"name": ["Asha", "Ben"], "age": [12, 13]})
                # join_with(ages, using="name", keep="all rows from this table")
                df.join(ages, on="name", how="left", suffix="_other", maintain_order="left")   # (1)
            """,
        },
        compare="table",
        choices=("a column found in both tables (other than using=) keeps its name in this table and gets "
                 "\"_other\" in the other table's copy.",),
        also="keep=\"matching rows\" (the default) is an inner join and \"all rows from both\" a full join. "
             "simplydata also says how many rows found a match, and warns when a name appears twice in the "
             "other table (rows would be repeated).",
    ),
    Entry(
        word="table.add_z_score_column",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.add_z_score_column("marks_z", from_column="marks", for_each_group_in="subject")
        """,
        code={
            "pandas": """
                from scipy import stats
                df = sdata.get_example("marks")
                # add_z_score_column("marks_z", from_column="marks", for_each_group_in="subject")
                z = df.groupby("subject")["marks"].transform(stats.zscore, ddof=1)   # (1)
                df.assign(marks_z=z)
            """,
            "Polars": """
                import polars as pl
                df = pl.from_pandas(sdata.get_example("marks"))
                # add_z_score_column("marks_z", from_column="marks", for_each_group_in="subject")
                m = pl.col("marks")
                df.with_columns(((m - m.mean()) / m.std()).over("subject").alias("marks_z"))   # (1)
            """,
        },
        compare="table",
        tolerance=1e-12,
        choices=("the standard deviation of a sample (n - 1, ddof=1), as R scale(); SciPy's zscore uses n "
                 "unless told ddof=1.",),
        also="Empty cells stay empty, and a group with fewer than 2 numbers gets empty cells. " + SAID,
    ),
    Entry(word="table.undo", ours="""
              table = sdata.table(sdata.get_example("marks"))
              table.undo()
          """, compare="none",
          note="simplydata's own: it keeps the table as it was before each step and puts back the last one. In "
               "pandas or Polars you keep a copy yourself before a step (before = df.copy()) and go back to it."),
    Entry(word="table.show_steps", ours="""
              table = sdata.table(sdata.get_example("marks"))
              table.show_steps()
          """, compare="none",
          note="simplydata's own: it writes down each step as you do it and lists them. pandas and Polars keep no "
               "list of steps; your script is the record."),
    Entry(
        word="table.save",
        data="marks",
        ours="""
            import os
            import tempfile
            import pandas as pd
            table = sdata.table(sdata.get_example("marks"))
            with tempfile.TemporaryDirectory() as folder:
                table.save(os.path.join(folder, "marks.csv"))
                saved = pd.read_csv(os.path.join(folder, "marks.csv"))
            saved
        """,
        code={
            "pandas": """
                import os
                import tempfile
                import pandas as pd
                df = sdata.get_example("marks")
                with tempfile.TemporaryDirectory() as folder:
                    # save("marks.csv")
                    df.to_csv(os.path.join(folder, "marks.csv"), index=False)   # (1)
                    saved = pd.read_csv(os.path.join(folder, "marks.csv"))
                saved
            """,
            "Polars": """
                import os
                import tempfile
                import pandas as pd
                import polars as pl
                df = pl.from_pandas(sdata.get_example("marks"))
                with tempfile.TemporaryDirectory() as folder:
                    # save("marks.csv")
                    df.write_csv(os.path.join(folder, "marks.csv"))
                    saved = pd.read_csv(os.path.join(folder, "marks.csv"))
                saved
            """,
        },
        compare="table",
        choices=("no row labels are written (index=False): the file holds only your columns.",),
        also="The end of the file name chooses the type: .xlsx (pandas to_excel), .tsv, .parquet and .json too. "
             "The test saves both files in a folder that is deleted afterwards and reads them back.",
    ),
    Entry(
        word="table.as_pandas",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.as_pandas()
        """,
        code={"Polars": """
            import polars as pl
            df = pl.from_pandas(sdata.get_example("marks"))
            # as_pandas()
            df.to_pandas()
        """},
        compare="table",
        also="A table that is already pandas comes back as it is; a Polars table is turned into pandas.",
    ),
    Entry(
        word="table.as_polars",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.as_polars()
        """,
        code={"pandas": """
            import polars as pl
            df = sdata.get_example("marks")
            # as_polars()
            pl.from_pandas(df)
        """},
        compare="table",
        also="A table that is already Polars comes back as it is; a pandas table is turned into Polars.",
    ),
    Entry(
        word="table.remove_extra_spaces_in",
        ours="""
            table = sdata.table({"name": ["  Asha ", "Ben   Lee", "Cara"]})
            table.remove_extra_spaces_in("name")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.DataFrame({"name": ["  Asha ", "Ben   Lee", "Cara"]})
                # remove_extra_spaces_in("name")
                df.assign(name=df["name"].str.replace(r"\\s+", " ", regex=True).str.strip())
            """,
            "Polars": """
                import polars as pl
                df = pl.DataFrame({"name": ["  Asha ", "Ben   Lee", "Cara"]})
                # remove_extra_spaces_in("name")
                df.with_columns(pl.col("name").str.replace_all(r"\\s+", " ").str.strip_chars())
            """,
        },
        compare="table",
        also="Any run of spaces, tabs or line breaks inside the text becomes one space. " + SAID,
    ),
    Entry(
        word="table.replace_values_in",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.replace_values_in("subject", "Maths", with_value="Math")
        """,
        code={
            "pandas": """
                df = sdata.get_example("marks")
                # replace_values_in("subject", "Maths", with_value="Math")
                df.assign(subject=df["subject"].mask(df["subject"] == "Maths", "Math"))
            """,
            "Polars": """
                import polars as pl
                df = pl.from_pandas(sdata.get_example("marks"))
                # replace_values_in("subject", "Maths", with_value="Math")
                subject = pl.col("subject")
                df.with_columns(pl.when(subject == "Maths").then(pl.lit("Math")).otherwise(subject).alias("subject"))
            """,
        },
        compare="table",
        also="A dictionary {old: new} replaces several values at once, each cell looked up in the original "
             "column (so {\"A\": \"B\", \"B\": \"A\"} swaps them); is_above= and the other conditions replace every "
             "value that meets one. Empty cells never match. " + SAID,
    ),
    Entry(
        word="table.add_missing_dates",
        data="river",
        ours="""
            table = sdata.table(sdata.get_example("river"))
            table.add_missing_dates("date", every="day", for_each_group_in="station")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = sdata.get_example("river")
                # add_missing_dates("date", every="day", for_each_group_in="station")
                parts = []
                for station, rows in df.groupby("station", sort=True):                    # (1)
                    days = pd.date_range(rows["date"].min(), rows["date"].max(), freq="D")  # (2)
                    full = rows.set_index("date").reindex(days).rename_axis("date").reset_index()
                    parts.append(full.assign(station=station))
                pd.concat(parts, ignore_index=True)
            """,
            "Polars": """
                import polars as pl
                df = pl.from_pandas(sdata.get_example("river"))
                # add_missing_dates("date", every="day", for_each_group_in="station")
                df.sort("station", "date").upsample("date", every="1d", group_by="station",   # (1) (2)
                                                    maintain_order=True)
            """,
        },
        compare="table",
        choices=("the table comes back sorted by the groups, then the dates; the group's name is copied into "
                 "the new rows.",
                 "each group's own run, from its first to its last date: no rows are added before or after "
                 "(between= adds them).",),
        also="Without every= simplydata uses the most common step between the dates and says so. It stops with "
             "a message when a date is repeated or does not fall on the steps. " + SAID,
    ),
    Entry(
        word="table.add_rolling_column",
        data="weather",
        ours="""
            table = sdata.table(sdata.get_example("weather"))
            table.add_rolling_column("rain_3_months", from_column="rain", window=3, show="total",
                                     for_each_group_in="city", sorted_by="month_number")
        """,
        code={
            "pandas": """
                df = sdata.get_example("weather")
                # add_rolling_column("rain_3_months", from_column="rain", window=3, show="total", ...)
                ordered = df.sort_values("month_number", kind="stable")                    # (1)
                total = ordered.groupby("city")["rain"].transform(lambda s: s.rolling(3).sum())  # (2)
                df.assign(rain_3_months=total)
            """,
            "Polars": """
                import polars as pl
                df = pl.from_pandas(sdata.get_example("weather"))
                # add_rolling_column("rain_3_months", from_column="rain", window=3, show="total", ...)
                total = pl.col("rain").rolling_sum(3).over("city", order_by="month_number")   # (1) (2)
                df.with_columns(total.alias("rain_3_months"))
            """,
        },
        compare="table",
        choices=("the window follows sorted_by=, but the rows keep their place in the table (assign lines the "
                 "values up by row).",
                 "the window is this row and the 2 rows before it, within each city; the first 2 rows of each city "
                 "stay empty until the window is full.",),
        also="centre=True centres the window, window=\"7 days\" makes it a span of time, and show= takes the "
             "median, standard deviation, a percentile and more. " + SAID,
    ),
    Entry(
        word="table.show_rows_with_outliers",
        data="marks",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.show_rows_with_outliers("marks", for_each_group_in="class")
        """,
        code={"pandas": """
            df = sdata.get_example("marks")
            # show_rows_with_outliers("marks", for_each_group_in="class")
            marks = df.groupby("class")["marks"]
            q1, q3 = marks.transform("quantile", 0.25), marks.transform("quantile", 0.75)   # (1)
            far = 1.5 * (q3 - q1)
            found = df[(df["marks"] < q1 - far) | (df["marks"] > q3 + far)]                  # (2)
            found.index = found.index + 1                                                   # (3)
            print(found)
        """},
        compare="printed",
        choices=("the quartiles of each class by pandas' (and R's type 7) linear method.",
                 "Tukey's rule, the one box plots use: below Q1 - 1.5 x IQR or above Q3 + 1.5 x IQR.",
                 "each row is shown with its place in the whole table, counted from 1, so "
                 "remove_rows_by_position() can follow.",),
        also="simplydata also prints the limits of each group and how many rows it found; the table does not "
             "change. test_method= takes \"3 IQR\", \"3 standard deviations\" or a test run in R (Grubbs, Dixon, "
             "Rosner).",
    ),
]
