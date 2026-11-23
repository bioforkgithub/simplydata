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
            table = sdata.get_example("marks")
            table.keep_rows_where("marks", is_above=50)
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # keep_rows_where("marks", is_above=50)
                df[df["marks"] > 50]                 # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
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
            table = sdata.get_example("marks")
            table.find_average_of("marks", for_each_group_in="subject")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # find_average_of("marks", for_each_group_in="subject")
                df.groupby("subject", dropna=False)["marks"].mean().reset_index()   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # find_average_of("marks", for_each_group_in="subject")
                df.group_by("subject").agg(pl.col("marks").mean()).sort("subject", nulls_last=True)   # (1)
            """,
        },
        compare="table",
        names={"average of marks": "marks"},
        choices=("one row for each group, the groups sorted (English, Maths, Science), with rows whose group cell is "
                 "empty as a group of their own, last; empty cells in \"marks\" are skipped, as pandas and Polars do "
                 "(NumPy's mean would give nan).",),
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
            table = sdata.get_example("marks")
            table.show_first_rows(3)
        """,
        code={"pandas": """
            import pandas as pd
            df = pd.read_csv("marks.csv")
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
            table = sdata.get_example("marks")
            table.describe_columns()
        """,
        code={"pandas": """
            import pandas as pd
            df = pd.read_csv("marks.csv")
            # describe_columns()
            print(f"The table has {len(df)} rows and {df.shape[1]} columns.\\n")
            numbers = [c in df.select_dtypes("number") for c in df.columns]
            nice = lambda v: str(int(v)) if float(v).is_integer() else str(round(v, 2))   # (1)
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
             "values; this table has neither. Text that is blank or only spaces counts as an empty cell (isna() "
             "would not count it). pandas' own df.describe() gives the numbers in another layout.",
    ),
    Entry(
        word="table.keep_columns",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_columns("name", "marks")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # keep_columns("name", "marks")
                df[["name", "marks"]]
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
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
            table = sdata.get_example("marks")
            table.rename_column("marks", to="score")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # rename_column("marks", to="score")
                df.rename(columns={"marks": "score"})
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
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
            table = sdata.get_example("shop")
            table.sort_by("sales", biggest_first=True)
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("shop.csv", parse_dates=["date"])
                # sort_by("sales", biggest_first=True)
                df.sort_values("sales", ascending=False, kind="stable",    # (1)
                               na_position="last")                         # (2)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("shop.csv", try_parse_dates=True)
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
            table = sdata.get_example("marks")
            table.keep_rows_by_position(10, to=20)
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # keep_rows_by_position(10, to=20)
                df.iloc[9:20]                    # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
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
            table = sdata.get_example("shop")
            table.fill_empty_cells_in("customers", with_the="median")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("shop.csv", parse_dates=["date"])
                # fill_empty_cells_in("customers", with_the="median")
                customers = df["customers"]
                df.assign(customers=customers.fillna(customers.median()))   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("shop.csv", try_parse_dates=True)
                # fill_empty_cells_in("customers", with_the="median")
                customers = pl.col("customers")
                df.with_columns(customers.fill_null(customers.median()))   # (1)
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
            table = sdata.table({"price": ["12.5", "1,200", "12,5", " 3 ", "n/a", None]})
            table.turn_into_numbers("price")
        """,
        code={"pandas": """
            import pandas as pd
            df = pd.DataFrame({"price": ["12.5", "1,200", "12,5", " 3 ", "n/a", None]})
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
                 "simplydata says how many and shows up to 3 of them. Blank text is simply empty.",),
        also="Spaces inside a number are left out first (1 200). A true/false column becomes 1 and 0, and a "
             "column that is already numbers is left as it is.",
    ),
    Entry(
        word="table.add_column",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.add_column("marks_per_hour", "marks / hours")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # add_column("marks_per_hour", "marks / hours")
                df.assign(marks_per_hour=df["marks"] / df["hours"])
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
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
            table = sdata.get_example("marks")
            table.add_group_column("grade", from_column="marks", cut_at=[41, 61, 81], names=["D", "C", "B", "A"])
        """,
        code={
            "pandas": """
                import numpy as np
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # add_group_column("grade", from_column="marks", cut_at=[41, 61, 81], names=[...])
                grade = pd.cut(df["marks"], [-np.inf, 41, 61, 81, np.inf],
                               labels=["D", "C", "B", "A"], right=False)       # (1)
                df.assign(grade=grade)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # add_group_column("grade", from_column="marks", cut_at=[41, 61, 81], names=[...])
                df.with_columns(pl.col("marks").cut([41, 61, 81], labels=["D", "C", "B", "A"],
                                                    left_closed=True).alias("grade"))   # (1)
            """,
        },
        compare="table",
        choices=("a value exactly on a cut goes into the higher group: a mark of 61 is a B (right=False, "
                 "left_closed=True); pandas and Polars put it in the lower group by default.",),
        also="simplydata makes a text column; pandas and Polars make a category column with the same values. "
             "Empty cells stay empty. " + SAID,
    ),
    Entry(
        word="table.find_summary_of",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.find_summary_of("marks", for_each_group_in="class", show=["average", "standard deviation", "count"])
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # find_summary_of("marks", for_each_group_in="class", show=[...])
                out = df.groupby("class", dropna=False)["marks"].agg(["mean", "std", "count"])   # (1) (2)
                out.reset_index().assign(column="marks")[["column", "class", "mean", "std", "count"]]
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # find_summary_of("marks", for_each_group_in="class", show=[...])
                m = pl.col("marks")
                out = df.group_by("class").agg(m.mean().alias("mean"), m.std().alias("std"),   # (2)
                                               m.count().alias("count")).sort("class")         # (1)
                out.select(pl.lit("marks").alias("column"), pl.all())
            """,
        },
        compare="table",
        names={"average": "mean", "standard deviation": "std"},
        choices=("one row for each group, the groups sorted (A, B, C); rows with an empty group cell form a group "
                 "of their own, shown last (dropna=False).",
                 "the standard deviation of a sample (n - 1), as pandas, Polars and R sd(); NumPy's own default "
                 "is n.",),
        also="simplydata also writes the summary in a sentence; the result is a new table you can save or chart.",
    ),
    Entry(
        word="table.join_with",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.join_with({"name": ["Asha", "Ben"], "age": [12, 13]}, using="name", keep="all rows from this table")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                ages = pd.DataFrame({"name": ["Asha", "Ben"], "age": [12, 13]})
                # join_with(ages, using="name", keep="all rows from this table")
                df.merge(ages, on="name", how="left", suffixes=("", "_other"))   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                ages = pl.DataFrame({"name": ["Asha", "Ben"], "age": [12, 13]})
                # join_with(ages, using="name", keep="all rows from this table")
                df.join(ages, on="name", how="left", suffix="_other")   # (1)
            """,
        },
        compare="table",
        choices=("a column found in both tables (other than using=) keeps its name in this table and gets "
                 "\"_other\" in the other table's copy.",),
        also="keep=\"matching rows\" (the default) is an inner join and \"all rows from both\" a full join. On a "
             "Polars table the order of the rows is Polars' own (the join is given no maintain_order=). "
             "simplydata also says how many rows found a match, and warns when a name appears twice in the "
             "other table (rows would be repeated).",
    ),
    Entry(
        word="table.add_z_score_column",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.add_z_score_column("marks_z", from_column="marks", for_each_group_in="subject")
        """,
        code={
            "pandas": """
                from scipy import stats
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # add_z_score_column("marks_z", from_column="marks", for_each_group_in="subject")
                z = df.groupby("subject")["marks"].transform(stats.zscore, ddof=1, nan_policy="omit")   # (1)
                df.assign(marks_z=z)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
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
              table = sdata.get_example("marks")
              table.undo()
          """, compare="none",
          note="simplydata's own: it keeps the table as it was before each step and puts back the last one. In "
               "pandas or Polars you keep a copy yourself before a step (before = df.copy()) and go back to it."),
    Entry(word="table.show_steps", ours="""
              table = sdata.get_example("marks")
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
            table = sdata.get_example("marks")
            with tempfile.TemporaryDirectory() as folder:
                table.save(os.path.join(folder, "marks.csv"))
                saved = sdata.table(os.path.join(folder, "marks.csv"))
            saved
        """,
        code={
            "pandas": """
                import os
                import tempfile
                import pandas as pd
                df = pd.read_csv("marks.csv")
                with tempfile.TemporaryDirectory() as folder:
                    # save as marks.csv
                    df.to_csv(os.path.join(folder, "marks.csv"), index=False)   # (1)
                    saved = pd.read_csv(os.path.join(folder, "marks.csv"))
                saved
            """,
            "Polars": """
                import os
                import tempfile
                import pandas as pd
                import polars as pl
                df = pl.read_csv("marks.csv")
                with tempfile.TemporaryDirectory() as folder:
                    # save as marks.csv
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
            table = sdata.get_example("marks")
            table.as_pandas()
        """,
        code={"Polars": """
            import polars as pl
            df = pl.read_csv("marks.csv")
            # as_pandas()
            df.to_pandas()
        """},
        compare="table",
        also="It is a copy: changing it never changes the table, and later steps on the table never change it "
             "(a pandas table is copied with df.copy(), which costs nothing until one of them changes under pandas 3; "
             "a Polars table is turned into pandas).",
    ),
    Entry(
        word="table.make_copy",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            backup = table.make_copy()
            table.keep_rows_where("class", is_equal_to="A")
            backup
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # backup = make_copy()
                backup = df.copy()                                    # (1)
                df = df[df["class"] == "A"]
                backup
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # backup = make_copy()
                backup = df.clone()
                df = df.filter(pl.col("class") == "A")
                backup
            """,
        },
        compare="table",
        choices=("the copy keeps the steps so far, so backup.undo() and backup.show_steps() work on it; pandas "
                 "df.copy() keeps only the data.",),
        also="copy.copy(table) and copy.deepcopy(table) give the same independent copy. A plain backup = table gives "
             "the same table a second name, so a step on one shows in both.",
    ),
    Entry(
        word="table.as_polars",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.as_polars()
        """,
        code={"pandas": """
            import polars as pl
            import pandas as pd
            df = pd.read_csv("marks.csv")
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
            table = sdata.get_example("marks")
            table.replace_values_in("subject", "Maths", with_value="Math")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # replace_values_in("subject", "Maths", with_value="Math")
                df.assign(subject=df["subject"].mask(df["subject"] == "Maths", "Math"))
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
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
            table = sdata.get_example("river")
            table.add_missing_dates("date", every="day", for_each_group_in="station")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("river.csv", parse_dates=["date"])
                # add_missing_dates("date", every="day", for_each_group_in="station")
                parts = []
                for station, rows in df.groupby("station", sort=True, dropna=False):      # (1)
                    days = pd.date_range(rows["date"].min(), rows["date"].max(), freq="D")  # (2)
                    full = rows.set_index("date").reindex(days).rename_axis("date").reset_index()
                    parts.append(full.assign(station=station))
                pd.concat(parts, ignore_index=True)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("river.csv", try_parse_dates=True)
                # add_missing_dates("date", every="day", for_each_group_in="station")
                df.sort("station", "date").upsample("date", every="1d", group_by="station",   # (1) (2)
                                                    maintain_order=True)
            """,
        },
        compare="table",
        choices=("the table comes back sorted by the groups, then the dates; the group's name is copied into "
                 "the new rows, and rows with an empty group cell are a group of their own (dropna=False).",
                 "each group's own run, from its first to its last date: no rows are added before or after "
                 "(between= adds them).",),
        also="Without every= simplydata uses the most common step between the dates and says so. It stops with "
             "a message when a date is repeated or does not fall on the steps. " + SAID,
    ),
    Entry(
        word="table.add_rolling_column",
        data="weather",
        ours="""
            table = sdata.get_example("weather")
            table.add_rolling_column("rain_3_months", from_column="rain", window=3, show="total",
                                     for_each_group_in="city", sorted_by="month_number")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("weather.csv")
                # add_rolling_column("rain_3_months", from_column="rain", window=3, show="total", ...)
                ordered = df.sort_values("month_number", kind="stable")                    # (1)
                total = ordered.groupby("city")["rain"].transform(lambda s: s.rolling(3).sum())  # (2)
                df.assign(rain_3_months=total)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("weather.csv")
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
            table = sdata.get_example("marks")
            table.show_rows_with_outliers("marks", for_each_group_in="class")
        """,
        code={"pandas": """
            import pandas as pd
            df = pd.read_csv("marks.csv")
            # show_rows_with_outliers("marks", for_each_group_in="class")
            marks = df.groupby("class", dropna=False)["marks"]
            q1, q3 = marks.transform("quantile", 0.25), marks.transform("quantile", 0.75)   # (1)
            far = 1.5 * (q3 - q1)
            found = df[(df["marks"] < q1 - far) | (df["marks"] > q3 + far)]                  # (2)
            found.index = found.index + 1                                                   # (3)
            print(found)
        """},
        compare="printed",
        choices=("the quartiles of each class by pandas' (and R's type 7) linear method; rows with an empty class "
                 "are a group of their own (dropna=False).",
                 "Tukey's rule, the one box plots use: below Q1 - 1.5 x IQR or above Q3 + 1.5 x IQR.",
                 "each row is shown with its place in the whole table, counted from 1, so "
                 "remove_rows_by_position() can follow.",),
        also="simplydata also prints the limits of each group and how many rows it found; the table does not "
             "change. test_method= takes \"3 IQR\", \"3 standard deviations\" or a test run in R (Grubbs, Dixon, "
             "Rosner).",
    ),
]


# ---------------------------------------------------------------- U3 batch 3: more table words
ENTRIES += [
    Entry(
        word="table.show_last_rows",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.show_last_rows(3)
        """,
        code={"pandas": """
            import pandas as pd
            df = pd.read_csv("marks.csv")
            # show_last_rows(rows=3)
            last = df.tail(3)
            last.index = range(len(df) - 2, len(df) + 1)     # (1)
            print(last)
        """},
        compare="printed",
        choices=("each row is numbered with its place in the whole table, counted from 1: the last 3 of 54 rows are "
                 "52, 53 and 54, the numbers keep_rows_by_position() takes.",),
        also="A Polars table has no row labels, so simplydata shows it through pandas with the same numbers. Only "
             "what is shown changes; the table keeps pandas' own row labels.",
    ),
    Entry(
        word="table.show",
        data="shop",
        ours="""
            table = sdata.get_example("shop")
            table.show()
        """,
        code={"pandas": """
            import pandas as pd
            df = pd.read_csv("shop.csv", parse_dates=["date"])
            # show()
            shown = df.copy()
            shown.index = range(1, len(df) + 1)                   # (1)
            with pd.option_context("display.max_rows", None, "display.max_columns", None,
                                   "display.width", None):        # (2)
                print(shown)
        """},
        compare="printed",
        choices=("the rows are numbered from 1, the way people count; pandas numbers them from 0.",
                 "every row and every column is shown (up to 1,000 rows); pandas on its own shows the first and last "
                 "5 of these 180 rows with \"...\" between.",),
        also="rows= shows only the first rows. A table of more than 1,000 rows shows its first 1,000 and says how "
             "to see them all. In Jupyter or VS Code the table is shown as a table instead of text.",
    ),
    Entry(
        word="table.get_column_names",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.get_column_names()
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # get_column_names()
                list(df.columns)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # get_column_names()
                df.columns
            """,
        },
        compare="value",
        tolerance=0.0,
        also="The names come back as a plain Python list, left to right; the table does not change.",
    ),
    Entry(
        word="table.get_column",
        data="shop",
        ours="""
            table = sdata.get_example("shop")
            table.get_column("sales")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("shop.csv", parse_dates=["date"])
                # get_column("sales")
                df["sales"].to_numpy(dtype=float)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("shop.csv", try_parse_dates=True)
                # get_column("sales")
                df["sales"].to_numpy()
            """,
        },
        compare="value",
        tolerance=0.0,
        also="A column of numbers comes back as sdata.numbers, so number words such as find_average() work on it; "
             "its empty cells become empty numbers (nan). A column of text or dates comes back as a plain list "
             "(to_list()), with a note. The table does not change.",
    ),
    Entry(
        word="table.get_row",
        data="shop",
        ours="""
            table = sdata.get_example("shop")
            table.get_row(45)
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("shop.csv", parse_dates=["date"])
                # get_row(position=45)
                row = df.iloc[44].to_dict()                                  # (1)
                {k: None if pd.isna(v) else v for k, v in row.items()}       # (2)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("shop.csv", schema_overrides={"date": pl.Datetime})   # dates with a time, as pandas
                # get_row(position=45)
                df.row(44, named=True)                                       # (1) (2)
            """,
        },
        compare="value",
        tolerance=0.0,
        choices=("rows are counted from 1, so row 45 is Python's position 44.",
                 "an empty cell becomes None, on both engines (pandas gives nan, Polars None); row 45 has no sales.",),
        also="get_row(\"last\") is the last row. Numbers and dates come back as plain Python values. The table does "
             "not change.",
    ),
    Entry(
        word="table.get_cell_at",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.get_cell_at(row=3, column="marks")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # get_cell_at(row=3, column="marks")
                df["marks"].iloc[2]              # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # get_cell_at(row=3, column="marks")
                df.item(2, "marks")              # (1)
            """,
        },
        compare="value",
        tolerance=0.0,
        choices=("rows are counted from 1, so row 3 is Python's position 2.",),
        also="row=\"last\" is the last row. An empty cell gives None and a note says so. The table does not change.",
    ),
    Entry(
        word="table.remove_columns",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.remove_columns("height")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # remove_columns("height")
                df.drop(columns=["height"])
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # remove_columns("height")
                df.drop("height")
            """,
        },
        compare="table",
        also="to=, of_kind=, starts_with= and the others remove columns by a run, a kind or their names, as in "
             "keep_columns(). simplydata stops with a message rather than remove every column. " + SAID,
    ),
    Entry(
        word="table.keep_columns_by_position",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_columns_by_position(1, to=3)
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # keep_columns_by_position(1, to=3)
                df.iloc[:, 0:3]                     # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # keep_columns_by_position(1, to=3)
                df.select(df.columns[0:3])          # (1)
            """,
        },
        compare="table",
        choices=("columns are counted from 1 at the left and both ends are kept, so columns 1 to 3 are Python's "
                 "0:3.",),
        also="\"last\" is the last column, step= keeps every n-th column and a list keeps those columns in that "
             "order. simplydata also names the columns it kept. " + SAID,
    ),
    Entry(
        word="table.remove_columns_by_position",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.remove_columns_by_position(2, to=3)
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # remove_columns_by_position(2, to=3)
                df.drop(columns=df.columns[1:3])    # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # remove_columns_by_position(2, to=3)
                df.drop(df.columns[1:3])            # (1)
            """,
        },
        compare="table",
        choices=("columns are counted from 1 at the left and both ends are removed, so columns 2 to 3 are Python's "
                 "1:3.",),
        also="Handy for the \"Unnamed: 0\" column a CSV file often brings (remove_columns_by_position(1)). "
             "simplydata names the columns it removed and stops rather than remove every column. " + SAID,
    ),
    Entry(
        word="table.remove_rows_where",
        data="shop",
        ours="""
            table = sdata.get_example("shop")
            table.remove_rows_where("sales", is_below=300)
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("shop.csv", parse_dates=["date"])
                # remove_rows_where("sales", is_below=300)
                df[~(df["sales"] < 300)]                                 # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("shop.csv", try_parse_dates=True)
                # remove_rows_where("sales", is_below=300)
                df.filter(~(pl.col("sales") < 300).fill_null(False))     # (1)
            """,
        },
        compare="table",
        choices=("a row whose cell is empty is never removed by a comparison: the 10 rows without sales stay. In "
                 "pandas an empty cell is never below 300; in Polars the comparison gives null, which is made False "
                 "first (without it Polars' filter would drop those rows too).",),
        also="The same conditions as keep_rows_where(); is_empty=True removes the empty rows. simplydata also says "
             "how many rows it removed, and keeps the table before the step (undo).",
    ),
    Entry(
        word="table.keep_first_rows",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_first_rows(10)
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # keep_first_rows(n=10)
                df.head(10)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # keep_first_rows(n=10)
                df.head(10)
            """,
        },
        compare="table",
        also="simplydata also says how many rows it kept, and keeps the table before the step (undo).",
    ),
    Entry(
        word="table.keep_last_rows",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_last_rows(10)
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # keep_last_rows(n=10)
                df.tail(10)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # keep_last_rows(n=10)
                df.tail(10)
            """,
        },
        compare="table",
        also="simplydata also says how many rows it kept, and keeps the table before the step (undo).",
    ),
    Entry(
        word="table.remove_rows_by_position",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.remove_rows_by_position([12, 40])
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # remove_rows_by_position([12, 40])
                df.drop(index=df.index[[11, 39]])                         # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # remove_rows_by_position([12, 40])
                df.filter(~pl.int_range(pl.len()).is_in([11, 39]))        # (1)
            """,
        },
        compare="table",
        choices=("rows are counted from 1, so rows 12 and 40 are Python's positions 11 and 39.",),
        also="A run (remove_rows_by_position(10, to=20)) keeps both ends, as keep_rows_by_position() does, and "
             "step= removes every n-th row. simplydata stops rather than remove every row. " + SAID,
    ),
    Entry(
        word="table.reverse_rows",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.reverse_rows()
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # reverse_rows()
                df.iloc[::-1]
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # reverse_rows()
                df.reverse()
            """,
        },
        compare="table",
        also="For an order by the values in a column use sort_by(). " + SAID,
    ),
    Entry(
        word="table.remove_duplicate_rows",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.remove_duplicate_rows(columns=["name"])
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # remove_duplicate_rows(columns=["name"])
                df.drop_duplicates(subset=["name"], keep="first")                   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # remove_duplicate_rows(columns=["name"])
                df.unique(subset=["name"], keep="first", maintain_order=True)       # (1)
            """,
        },
        compare="table",
        choices=("the first row of each name is kept and the rows stay in their order; Polars' own default keeps any "
                 "one of them, in any order.",),
        also="Without columns= a row is removed only when every cell repeats an earlier row. simplydata also says "
             "how many rows it removed, and keeps the table before the step (undo).",
    ),
    Entry(
        word="table.keep_biggest_rows",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_biggest_rows(4, by="marks", for_each_group_in="subject")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # keep_biggest_rows(4, by="marks", for_each_group_in="subject")
                ordered = df.sort_values("marks", ascending=False, kind="stable")   # (1)
                top = ordered.groupby("subject").head(4)
                top.sort_values("subject", kind="stable")                         # (2)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # keep_biggest_rows(4, by="marks", for_each_group_in="subject")
                ordered = df.sort("marks", descending=True, maintain_order=True)   # (1)
                top = ordered.filter(pl.int_range(pl.len()).over("subject") < 4)
                top.sort("subject", maintain_order=True)                          # (2)
            """,
        },
        compare="table",
        choices=("exactly 4 rows: when rows tie at the cut, the ones higher up in the table are kept (a stable "
                 "sort). Here English and Maths each have two 4th-best marks; a note says so.",
                 "the groups come in order (English, Maths, Science), biggest first within each.",),
        also="Rows with an empty cell in by= are never kept, and a note says how many. Without for_each_group_in= "
             "it keeps the 4 biggest of the whole table.",
    ),
    Entry(
        word="table.keep_smallest_rows",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_smallest_rows(3, by="marks", for_each_group_in="subject")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # keep_smallest_rows(3, by="marks", for_each_group_in="subject")
                ordered = df.sort_values("marks", kind="stable")                  # (1)
                low = ordered.groupby("subject").head(3)
                low.sort_values("subject", kind="stable")                         # (2)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # keep_smallest_rows(3, by="marks", for_each_group_in="subject")
                ordered = df.sort("marks", maintain_order=True)                   # (1)
                low = ordered.filter(pl.int_range(pl.len()).over("subject") < 3)
                low.sort("subject", maintain_order=True)                          # (2)
            """,
        },
        compare="table",
        choices=("exactly 3 rows: when rows tie at the cut, the one higher up in the table is kept (a stable sort). "
                 "Here Maths has two marks of 47 at the cut; a note says so.",
                 "the groups come in order (English, Maths, Science), smallest first within each.",),
        also="Rows with an empty cell in by= are never kept, and a note says how many. Without for_each_group_in= "
             "it keeps the 3 smallest of the whole table.",
    ),
    Entry(
        word="table.remove_rows_with_outliers",
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.remove_rows_with_outliers("sleep", for_each_group_in="school")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("school.csv")
                # remove_rows_with_outliers("sleep", for_each_group_in="school")
                sleep = df.groupby("school")["sleep"]
                q1, q3 = sleep.transform("quantile", 0.25), sleep.transform("quantile", 0.75)   # (1)
                far = 1.5 * (q3 - q1)
                out = (df["sleep"] < q1 - far) | (df["sleep"] > q3 + far)                         # (2)
                df[~out]                                                                          # (3)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("school.csv")
                # remove_rows_with_outliers("sleep", for_each_group_in="school")
                s = pl.col("sleep")
                q1, q3 = s.quantile(0.25, "linear").over("school"), s.quantile(0.75, "linear").over("school")  # (1)
                far = 1.5 * (q3 - q1)
                df.filter(~((s < q1 - far) | (s > q3 + far)).fill_null(False))                    # (2) (3)
            """,
        },
        compare="table",
        choices=("the quartiles of each school by the linear method (pandas' default, R's type 7); Polars' own "
                 "default is \"nearest\", which would remove 5 rows here instead of 4.",
                 "Tukey's rule, the one box plots use: below Q1 - 1.5 x IQR or above Q3 + 1.5 x IQR.",
                 "rows with an empty cell stay: the 19 pupils without a sleep value are not outliers.",),
        also="simplydata also prints the limits of each group and how many rows it removed (here 4). "
             "test_method= takes \"3 IQR\", \"3 standard deviations\" or a test run in R (Grubbs, Dixon, Rosner). "
             "Look first with show_rows_with_outliers().",
    ),
    Entry(
        word="table.remove_rows_with_empty_cells_in",
        ours="""
            table = sdata.table({"name": ["Asha", " ", None, "Ben"], "marks": [61, 70, 55, 80]})
            table.remove_rows_with_empty_cells_in("name")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.DataFrame({"name": ["Asha", " ", None, "Ben"], "marks": [61, 70, 55, 80]})
                # remove_rows_with_empty_cells_in("name")
                name = df["name"]
                df[~(name.isna() | (name.str.strip() == ""))]                     # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.DataFrame({"name": ["Asha", " ", None, "Ben"], "marks": [61, 70, 55, 80]})
                # remove_rows_with_empty_cells_in("name")
                name = pl.col("name")
                df.filter(~(name.is_null() | (name.str.strip_chars() == "")))      # (1)
            """,
        },
        compare="table",
        choices=("a cell of only spaces counts as empty, as a missing one does; pandas' dropna() would keep it.",),
        also="Without a column name, a row with an empty cell in any column is removed. simplydata also says how "
             "many rows it removed, and keeps the table before the step (undo).",
    ),
    Entry(
        word="table.add_is_empty_column",
        ours="""
            table = sdata.table({"note": ["ok", "", None, "  ", "late"]})
            table.add_is_empty_column("note_was_empty", from_column="note")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.DataFrame({"note": ["ok", "", None, "  ", "late"]})
                # add_is_empty_column("note_was_empty", from_column="note")
                note = df["note"]
                df.assign(note_was_empty=note.isna() | (note.str.strip() == ""))              # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.DataFrame({"note": ["ok", "", None, "  ", "late"]})
                # add_is_empty_column("note_was_empty", from_column="note")
                note = pl.col("note")
                df.with_columns((note.is_null() | (note.str.strip_chars() == "")).alias("note_was_empty"))  # (1)
            """,
        },
        compare="table",
        choices=("empty means missing, NaN or blank text (\"\" or only spaces); pandas' isna() finds only the "
                 "missing one.",),
        also="Add it before fill_empty_cells_in(), to keep track of which values were filled in. simplydata also "
             "says how many rows are True. " + SAID,
    ),
    Entry(
        word="table.turn_into_text",
        data="shop",
        ours="""
            table = sdata.get_example("shop")
            table.turn_into_text("date")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("shop.csv", parse_dates=["date"])
                # turn_into_text("date")
                df.assign(date=df["date"].dt.strftime("%Y-%m-%d"))          # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("shop.csv", try_parse_dates=True)
                # turn_into_text("date")
                df.with_columns(pl.col("date").dt.strftime("%Y-%m-%d"))     # (1)
            """,
        },
        compare="table",
        choices=("dates are written year-month-day (2026-01-01), with the time of day only when some date has one; "
                 "Polars' own cast to text would add 00:00:00.000000 to every cell.",),
        also="Numbers become their text (astype(str), cast(pl.String)); True/False become \"True\" and \"False\"; "
             "empty cells stay empty (pandas' astype(str) would write \"nan\"). " + SAID,
    ),
    Entry(
        word="table.turn_into_dates",
        ours="""
            table = sdata.table({"when": ["15/03/2026", "03/04/2026", "12/25/2026", "2026-05-01", "soon"]})
            table.turn_into_dates("when")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.DataFrame({"when": ["15/03/2026", "03/04/2026", "12/25/2026", "2026-05-01", "soon"]})
                # turn_into_dates("when")
                when = pd.Series(pd.NaT, index=df.index, dtype="datetime64[us]")
                for f in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]:                                   # (1)
                    when = when.fillna(pd.to_datetime(df["when"], format=f, errors="coerce"))     # (2)
                df.assign(when=when)
            """,
            "Polars": """
                import polars as pl
                df = pl.DataFrame({"when": ["15/03/2026", "03/04/2026", "12/25/2026", "2026-05-01", "soon"]})
                # turn_into_dates("when")
                formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]                                   # (1)
                found = [pl.col("when").str.strptime(pl.Datetime("us"), f, strict=False) for f in formats]  # (2)
                df.with_columns(pl.coalesce(found).alias("when"))
            """,
        },
        compare="table",
        choices=("each cell gets the first way of writing that fits, day first before month first: 03/04/2026 is "
                 "3 April, and 12/25/2026 can only be 25 December. simplydata's list holds 26 ways (dots, dashes, "
                 "month names, times of day); these 3 are the ones these cells need.",
                 "a cell that fits none of them becomes empty (errors=\"coerce\", strict=False); simplydata says how "
                 "many and shows one (\"soon\").",),
        also="order=\"month day year\" (or another order) uses only the ways in that order, so nothing is guessed. "
             "Whole years such as 2026 become 1 January of that year, \"2026-03\" becomes 1 March, and spaces at "
             "the ends of a cell are left out. " + SAID,
    ),
    Entry(
        word="table.turn_into_lowercase",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.turn_into_lowercase("name")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # turn_into_lowercase("name")
                df.assign(name=df["name"].str.lower())
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # turn_into_lowercase("name")
                df.with_columns(pl.col("name").str.to_lowercase())
            """,
        },
        compare="table",
        also="Empty cells stay empty; a column that is not text gets a message. " + SAID,
    ),
    Entry(
        word="table.turn_into_uppercase",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.turn_into_uppercase("name")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # turn_into_uppercase("name")
                df.assign(name=df["name"].str.upper())
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # turn_into_uppercase("name")
                df.with_columns(pl.col("name").str.to_uppercase())
            """,
        },
        compare="table",
        also="Empty cells stay empty; a column that is not text gets a message. " + SAID,
    ),
    Entry(
        word="table.round_numbers_in",
        ours="""
            table = sdata.table({"price": [0.5, 1.5, 2.5, 3.25]})
            table.round_numbers_in("price", 0)
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.DataFrame({"price": [0.5, 1.5, 2.5, 3.25]})
                # round_numbers_in("price", with_decimals=0)
                df.assign(price=df["price"].round(0))
            """,
            "Polars": """
                import polars as pl
                df = pl.DataFrame({"price": [0.5, 1.5, 2.5, 3.25]})
                # round_numbers_in("price", with_decimals=0)
                df.with_columns(pl.col("price").round(0))
            """,
        },
        compare="table",
        also="A number exactly halfway goes to the even neighbour (0.5 to 0, 1.5 and 2.5 to 2), as pandas, NumPy "
             "and R round() do, and Polars whose round() rounds halves to even by default (mode=\"half_to_even\"; "
             "older Polars releases rounded halves away from zero); this keeps a run of halves from pushing totals "
             "up. A negative number of places "
             "rounds to tens or hundreds, and round_numbers_in(1) rounds every number column. " + SAID,
    ),
    Entry(
        word="table.change_column",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.change_column("marks", "marks / 10")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # change_column("marks", "marks / 10")
                df.assign(marks=df["marks"] / 10)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # change_column("marks", "marks / 10")
                df.with_columns(pl.col("marks") / 10)
            """,
        },
        compare="table",
        also="The column keeps its name and its place. The formula is read by simplydata itself, never run as "
             "Python code, and dividing by zero gives an empty cell. The same ways as add_column() work "
             "(from_column= with plus=, for_each_group_in= ...). " + SAID,
    ),
    Entry(
        word="table.add_rank_column",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.add_rank_column("place", from_column="marks")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # add_rank_column("place", from_column="marks")
                df.assign(place=df["marks"].rank(method="min", ascending=False))     # (1) (2)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # add_rank_column("place", from_column="marks")
                df.with_columns(pl.col("marks").rank("min", descending=True).alias("place"))   # (1) (2)
            """,
        },
        compare="table",
        choices=("rows that tie share the best place and the next place is skipped, as in sports tables (1, 2, 2, "
                 "4); pandas' own default gives both 2.5.",
                 "the biggest value gets place 1 (biggest_first=False gives it to the smallest).",),
        also="Empty cells get no place. A column without empty cells gets whole numbers. " + SAID,
    ),
    Entry(
        word="table.add_column_with_part_of_date",
        data="shop",
        ours="""
            table = sdata.get_example("shop")
            table.add_column_with_part_of_date("weekday", from_column="date", part="weekday")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("shop.csv", parse_dates=["date"])
                # add_column_with_part_of_date("weekday", from_column="date", part="weekday")
                df.assign(weekday=df["date"].dt.dayofweek + 1)                # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("shop.csv", try_parse_dates=True)
                # add_column_with_part_of_date("weekday", from_column="date", part="weekday")
                df.with_columns(pl.col("date").dt.weekday().alias("weekday"))   # (1)
            """,
        },
        compare="table",
        choices=("1 is Monday and 7 is Sunday, as the ISO 8601 standard and Polars count; pandas counts Monday as "
                 "0.",),
        also="part= also takes \"year\", \"quarter\", \"month\", \"month name\", \"week\" (the ISO week), \"day\", "
             "\"weekday name\", \"day of year\", \"hour\" and \"minute\". Empty dates give empty cells. " + SAID,
    ),
    Entry(
        word="table.add_column_with_part_of_text",
        ours="""
            table = sdata.table({"place": ["Corner shop, north", "Big Market , east, 2", "Kiosk", None]})
            table.add_column_with_part_of_text("first_word", from_column="place", before=",")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.DataFrame({"place": ["Corner shop, north", "Big Market , east, 2", "Kiosk", None]})
                # add_column_with_part_of_text("first_word", from_column="place", before=",")
                part = df["place"].str.extract(r"(?s)^(.*?),", expand=False)     # (1)
                df.assign(first_word=part.str.strip())                           # (2)
            """,
            "Polars": """
                import polars as pl
                df = pl.DataFrame({"place": ["Corner shop, north", "Big Market , east, 2", "Kiosk", None]})
                # add_column_with_part_of_text("first_word", from_column="place", before=",")
                part = pl.col("place").str.extract(r"(?s)^(.*?),", 1)            # (1)
                df.with_columns(part.str.strip_chars().alias("first_word"))      # (2)
            """,
        },
        compare="table",
        choices=("the text before the first comma (\"Big Market\", not \"Big Market , east\"); a cell without a "
                 "comma gives an empty cell, and simplydata says how many.",
                 "spaces at the ends of the part are removed (\"Big Market \" becomes \"Big Market\"), and a part "
                 "that is blank becomes empty.",),
        also="first_characters=, last_characters=, characters=[2, 4], after= and matches_pattern= take other "
             "parts. " + SAID,
    ),
    Entry(
        word="table.split_column",
        ours="""
            table = sdata.table({"name": ["Asha Rao", "Ben Lee Park", "Dev   Shah", "Cara"], "age": [12, 13, 14, 12]})
            table.split_column("name", separator=" ", into=["first", "rest"])
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.DataFrame({"name": ["Asha Rao", "Ben Lee Park", "Dev   Shah", "Cara"], "age": [12, 13, 14, 12]})
                # split_column("name", separator=" ", into=["first", "rest"])
                parts = df["name"].str.split(" ", n=1, expand=True, regex=False)                # (1)
                new = pd.DataFrame({"first": parts[0].str.strip(), "rest": parts[1].str.strip()})
                pd.concat([new, df.drop(columns="name")], axis=1)                               # (2)
            """,
            "Polars": """
                import polars as pl
                df = pl.DataFrame({"name": ["Asha Rao", "Ben Lee Park", "Dev   Shah", "Cara"], "age": [12, 13, 14, 12]})
                # split_column("name", separator=" ", into=["first", "rest"])
                parts = pl.col("name").str.splitn(" ", 2)                                       # (1)
                df.select(parts.struct.field("field_0").str.strip_chars().alias("first"),       # (2)
                          parts.struct.field("field_1").str.strip_chars().alias("rest"), "age")
            """,
        },
        compare="table",
        choices=("at most as many pieces as names in into=: the last keeps the rest of the text (\"Lee Park\"), and "
                 "a cell with fewer pieces gives an empty cell (\"Cara\" has no rest). simplydata says how many of "
                 "each.",
                 "the new columns take the place of the old one; spaces at the ends of each piece are removed (\"Dev   "
                 "Shah\" gives \"Shah\", not \"  Shah\").",),
        also="The separator is plain text, not a pattern. " + SAID,
    ),
    Entry(
        word="table.replace_text_in",
        ours="""
            table = sdata.table({"code": ["A.1", "B.2.5", "C-3"]})
            table.replace_text_in("code", ".", with_value="-")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.DataFrame({"code": ["A.1", "B.2.5", "C-3"]})
                # replace_text_in("code", ".", with_value="-")
                df.assign(code=df["code"].str.replace(".", "-", regex=False))          # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.DataFrame({"code": ["A.1", "B.2.5", "C-3"]})
                # replace_text_in("code", ".", with_value="-")
                df.with_columns(pl.col("code").str.replace_all(".", "-", literal=True))   # (1)
            """,
        },
        compare="table",
        choices=("the old text is plain text, not a pattern: \".\" is a full stop, not \"any character\"; and it is "
                 "replaced everywhere it appears (Polars' replace() changes only the first).",),
        also="Capitals matter, and with_value=\"\" removes the text. matches_pattern= takes a regular expression "
             "instead. simplydata also says in how many cells it replaced the text. " + SAID,
    ),
    Entry(
        word="table.add_previous_value_column",
        data="weather",
        ours="""
            table = sdata.get_example("weather")
            table.sort_by("temperature")
            table.add_previous_value_column("last_month", from_column="temperature", for_each_group_in="city",
                                            sorted_by="month_number")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("weather.csv").sort_values("temperature", kind="stable")
                # add_previous_value_column("last_month", from_column="temperature", ...)
                ordered = df.sort_values("month_number", kind="stable")                     # (1)
                before = ordered.groupby("city")["temperature"].shift(1)                    # (2)
                df.assign(last_month=before)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("weather.csv").sort("temperature", maintain_order=True)
                # add_previous_value_column("last_month", from_column="temperature", ...)
                before = pl.col("temperature").shift(1).over("city", order_by="month_number")   # (1) (2)
                df.with_columns(before.alias("last_month"))
            """,
        },
        compare="table",
        choices=("\"the row before\" follows sorted_by=, but the rows keep their place in the table (here sorted by "
                 "temperature; assign lines the values up by row).",
                 "within each city; the first month of each city has no row before it and stays empty.",),
        also="rows_back=2 takes the value from 2 rows before. Without sorted_by= the rows are taken in the order "
             "they are in now. " + SAID,
    ),
    Entry(
        word="table.add_change_column",
        ours="""
            table = sdata.table({"year": [2021, 2020, 2022, 2020, 2021], "country": ["A", "A", "A", "B", "B"],
                                 "population": [5.0, 0.0, 6.0, 4.0, 5.0]})
            table.add_change_column("growth", from_column="population", in_percent=True, for_each_group_in="country",
                                    sorted_by="year")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.DataFrame({"year": [2021, 2020, 2022, 2020, 2021], "country": ["A", "A", "A", "B", "B"],
                                   "population": [5.0, 0.0, 6.0, 4.0, 5.0]})
                # add_change_column("growth", from_column="population", in_percent=True, ...)
                ordered = df.sort_values("year", kind="stable")
                before = ordered.groupby("country")["population"].shift(1)                  # (1)
                df.assign(growth=(df["population"] - before) / before.where(before != 0) * 100)   # (2)
            """,
            "Polars": """
                import polars as pl
                df = pl.DataFrame({"year": [2021, 2020, 2022, 2020, 2021], "country": ["A", "A", "A", "B", "B"],
                                   "population": [5.0, 0.0, 6.0, 4.0, 5.0]})
                # add_change_column("growth", from_column="population", in_percent=True, ...)
                p = pl.col("population")
                before = p.shift(1).over("country", order_by="year")                        # (1)
                df.with_columns(((p - before) / pl.when(before != 0).then(before) * 100).alias("growth"))  # (2)
            """,
        },
        compare="table",
        choices=("the previous value is the one before in order of sorted_by= (year), within each country; the rows "
                 "keep their place, and the first year of each country stays empty.",
                 "in_percent=True is (this - previous) / previous x 100, and a previous value of 0 gives an empty "
                 "cell (pandas and Polars would give inf).",),
        also="Without in_percent= it is this value minus the previous one. rows_back= compares with a row further "
             "back. " + SAID,
    ),
    Entry(
        word="table.find_smallest_of",
        data="weather",
        ours="""
            table = sdata.get_example("weather")
            table.find_smallest_of("temperature", for_each_group_in="city")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("weather.csv")
                # find_smallest_of("temperature", for_each_group_in="city")
                df.groupby("city")["temperature"].min().reset_index()                   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("weather.csv")
                # find_smallest_of("temperature", for_each_group_in="city")
                df.group_by("city").agg(pl.col("temperature").min()).sort("city")       # (1)
            """,
        },
        compare="table",
        names={"smallest of temperature": "temperature"},
        choices=("one row for each city, the cities sorted A to Z (Polars' group_by gives them in any order).",),
        also="Empty cells are skipped, as pandas and Polars do. simplydata also names the column \"smallest of "
             "temperature\" and writes the values in a sentence; without for_each_group_in= it gives one number.",
    ),
    Entry(
        word="table.find_biggest_of",
        data="weather",
        ours="""
            table = sdata.get_example("weather")
            table.find_biggest_of("temperature")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("weather.csv")
                # find_biggest_of("temperature")
                df["temperature"].max()
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("weather.csv")
                # find_biggest_of("temperature")
                df["temperature"].max()
            """,
        },
        compare="value",
        tolerance=0.0,
        also="Empty cells are skipped, as pandas and Polars do (NumPy's max would give nan). for_each_group_in= "
             "gives a table with one row for each group. simplydata also says how many values it looked at.",
    ),
    Entry(
        word="table.find_standard_deviation_of",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.find_standard_deviation_of("marks", for_each_group_in="class")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # find_standard_deviation_of("marks", for_each_group_in="class")
                df.groupby("class")["marks"].std(ddof=1).reset_index()                   # (1) (2)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # find_standard_deviation_of("marks", for_each_group_in="class")
                df.group_by("class").agg(pl.col("marks").std(ddof=1)).sort("class")      # (1) (2)
            """,
        },
        compare="table",
        tolerance=1e-12,
        names={"standard deviation of marks": "marks"},
        choices=("the standard deviation of a sample (divide by n - 1), as pandas, Polars and R sd(); NumPy's own "
                 "default divides by n.",
                 "one row for each class, the classes sorted A to Z.",),
        also="Empty cells are skipped. interval=95 adds a confidence interval (from R), and weights= gives a "
             "weighted standard deviation. simplydata also writes the values in a sentence.",
    ),
    Entry(
        word="table.count_different_values_in",
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.count_different_values_in("sleep", for_each_group_in="school")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("school.csv")
                # count_different_values_in("sleep", for_each_group_in="school")
                df.groupby("school")["sleep"].nunique().reset_index()                        # (1) (2)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("school.csv")
                # count_different_values_in("sleep", for_each_group_in="school")
                df.group_by("school").agg(pl.col("sleep").drop_nulls().n_unique()).sort("school")   # (1) (2)
            """,
        },
        compare="table",
        names={"different values": "sleep"},
        choices=("empty cells are not counted as a value (pandas' nunique() leaves them out; Polars' n_unique() "
                 "would count the empty value once); a note says how many there were (19).",
                 "one row for each school, the schools sorted A to Z.",),
        also="Capital letters matter: \"Apple\" and \"apple\" are two values. Without for_each_group_in= it gives "
             "one number.",
    ),
    Entry(
        word="table.find_most_common_of",
        ours="""
            table = sdata.table({"x": [3, 1, 3, 1, 2, None]})
            table.find_most_common_of("x")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.DataFrame({"x": [3, 1, 3, 1, 2, None]})
                # find_most_common_of("x")
                df["x"].mode().iloc[0]                          # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.DataFrame({"x": [3, 1, 3, 1, 2, None]})
                # find_most_common_of("x")
                df["x"].drop_nulls().mode().sort()[0]           # (1)
            """,
        },
        compare="value",
        tolerance=0.0,
        choices=("when values tie (1 and 3 each turn up twice), the smallest is given and a note names the others; "
                 "empty cells are skipped. pandas' mode() is sorted; Polars' mode() comes in any order.",),
        also="simplydata counts the values itself and breaks a tie with its own sort; the answer is the one pandas' "
             "mode() gives. It works for text too (the first in A to Z order on a tie). for_each_group_in= gives a "
             "table with, for "
             "each group, the most common value, its count, its percent and how many values share the top count.",
    ),
    Entry(
        word="table.find_interval_of",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.find_interval_of("marks", "average")
        """,
        code={"SciPy": """
            import numpy as np
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("marks.csv")
            # find_interval_of("marks", "average")
            x = df["marks"].dropna().to_numpy(dtype=float)
            ci = stats.bootstrap((x,), np.mean, n_resamples=9999, method="BCa",            # (1) (2)
                                 vectorized=False, rng=np.random.default_rng(1)).confidence_interval   # (3)
            pd.DataFrame({"average of marks": [x.mean()], "average of marks 95 % CI low": [ci.low],
                          "average of marks 95 % CI high": [ci.high], "count": [len(x)]})
        """},
        compare="table",
        tolerance=1e-12,
        choices=("the bias-corrected and accelerated (BCa) bootstrap interval, the usual choice; \"percentile "
                 "bootstrap\" and \"reverse percentile bootstrap\" are the others.",
                 "9999 resamples (resamples= changes it).",
                 "NumPy's random generator with seed 1 (with_seed=), printed, so the same call gives the same "
                 "interval.",),
        also="summary= takes any one-number measure (\"median\", \"standard deviation\", \"percentile 90\" ...) or a "
             "function of your own, and for_each_group_in= gives one row for each group. With fewer than 20 "
             "values a note says the interval is often too narrow. R boot::boot.ci() gives the same kinds.",
    ),
    Entry(
        word="table.add_rows_from",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.add_rows_from({"marks": [88], "name": ["Zoe"], "class": ["A"], "subject": ["Maths"],
                                 "hours": [5.0], "height": [150]})
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                other = pd.DataFrame({"marks": [88], "name": ["Zoe"], "class": ["A"], "subject": ["Maths"],
                                      "hours": [5.0], "height": [150]})
                # add_rows_from(other)
                pd.concat([df, other], ignore_index=True)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                other = pl.DataFrame({"marks": [88], "name": ["Zoe"], "class": ["A"], "subject": ["Maths"],
                                      "hours": [5.0], "height": [150]})
                # add_rows_from(other)
                pl.concat([df, other.select(df.columns)], how="vertical_relaxed")       # (1)
            """,
        },
        compare="table",
        choices=("columns are matched by their names, so the other table's columns may come in any order; pandas' "
                 "concat matches them by name itself, Polars' needs them put in the same order first "
                 "(select(df.columns)).",),
        also="simplydata stops with a message that names the columns found in only one of the two tables, or the "
             "columns that hold different kinds of values. The new rows go under, numbered on from the last. "
             + SAID,
    ),
    Entry(
        word="table.gather_into_rows",
        data="weather",
        ours="""
            table = sdata.get_example("weather")
            table.gather_into_rows(["temperature", "rain"])
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("weather.csv")
                # gather_into_rows(["temperature", "rain"])
                others = [c for c in df.columns if c not in ("temperature", "rain")]
                df.melt(id_vars=others, value_vars=["temperature", "rain"],
                        var_name="column", value_name="value")                          # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("weather.csv")
                # gather_into_rows(["temperature", "rain"])
                others = [c for c in df.columns if c not in ("temperature", "rain")]
                df.unpivot(on=["temperature", "rain"], index=others,
                           variable_name="column", value_name="value")                  # (1)
            """,
        },
        compare="table",
        choices=("every other column stays beside each value, and the new columns are called \"column\" and "
                 "\"value\" (names_to=, values_to= change them; pandas' own names are \"variable\" and \"value\").",),
        also="All temperatures come first, then all rain, as in pandas and Polars. simplydata stops with a message "
             "when text and number columns are mixed. " + SAID,
    ),
    Entry(
        word="table.spread_into_columns",
        data="weather",
        ours="""
            table = sdata.get_example("weather")
            table.keep_columns("month", "city", "temperature")
            table.spread_into_columns(names_from="city", values_from="temperature")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("weather.csv")[["month", "city", "temperature"]]
                # spread_into_columns(names_from="city", values_from="temperature")
                wide = df.pivot(index="month", columns="city", values="temperature")
                wide = wide.loc[df["month"].unique(), df["city"].unique()]              # (1)
                wide.reset_index().rename_axis(columns=None)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("weather.csv").select("month", "city", "temperature")
                # spread_into_columns(names_from="city", values_from="temperature")
                df.pivot(on="city", index="month", values="temperature")                # (1)
            """,
        },
        compare="table",
        choices=("rows and new columns stay in the order they first appear (Jan, Feb ...; Sunnyvale first), on both "
                 "engines; pandas' pivot sorts them (Apr, Aug ...; Frostby first).",),
        also="All the other columns say which row is which. When two rows would fill the same cell simplydata "
             "stops and suggests find_average_of() first, instead of choosing one. When another column differs "
             "between rows that would merge, so that the new columns get empty cells, a note names that column. "
             + SAID,
    ),
    Entry(
        word="table.swap_rows_and_columns",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_rows_where("subject", is_equal_to="Maths")
            table.keep_columns("name", "hours", "marks")
            table.swap_rows_and_columns()
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                df = df[df["subject"] == "Maths"][["name", "hours", "marks"]]
                # swap_rows_and_columns()
                flipped = df.set_index("name").T                                       # (1)
                flipped.rename_axis("column").reset_index().rename_axis(columns=None)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv").filter(pl.col("subject") == "Maths").select("name", "hours", "marks")
                # swap_rows_and_columns()
                df.drop("name").transpose(include_header=True, header_name="column",
                                          column_names=df["name"])                    # (1)
            """,
        },
        compare="table",
        choices=("the first column (here \"name\") names the new columns, because it holds text with no repeat and "
                 "no empty cell, and the old column names go in a first column called \"column\"; pandas' plain .T "
                 "and Polars' transpose() would number the columns instead.",),
        also="A first column of numbers, or one with a repeat or an empty cell, cannot name columns: then the new "
             "columns are numbered \"1\", \"2\" ... and a note says why. A Polars table goes through pandas and back. "
             + SAID,
    ),
    Entry(word="table.start_again", ours="""
              table = sdata.get_example("marks")
              table.keep_rows_where("marks", is_above=50)
              table.start_again()
          """, compare="none",
          note="simplydata's own: it keeps the table it started with and puts it back, as one more step that undo() "
               "can take back. In pandas or Polars you keep the first table yourself (start = df.copy()) and go "
               "back to it."),
]
