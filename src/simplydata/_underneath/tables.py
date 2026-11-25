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
    # 2026-11-23 (branch save-in-sheet)
    Entry(
        word="table.save",
        option="in_sheet=",
        data="marks",
        ours="""
            import os
            import tempfile
            table = sdata.get_example("marks")
            with tempfile.TemporaryDirectory() as folder:
                results = os.path.join(folder, "results.xlsx")
                table.save(results, in_sheet="2025")
                table.save(results, in_sheet="2026")
                both = sdata.table(results, sheet="all")
            both
        """,
        code={
            "pandas": """
                import os
                import tempfile
                import pandas as pd
                df = pd.read_csv("marks.csv")
                with tempfile.TemporaryDirectory() as folder:
                    results = os.path.join(folder, "results.xlsx")
                    df.to_excel(results, sheet_name="2025", index=False)
                    # save as results.xlsx with in_sheet="2026", to a file that exists
                    with pd.ExcelWriter(results, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:  # (1)
                        df.to_excel(writer, sheet_name="2026", index=False)
                    sheets = pd.read_excel(results, sheet_name=None)
                both = pd.concat([s.assign(sheet=n)[["sheet", *df.columns]] for n, s in sheets.items()], ignore_index=True)
                both
            """,
        },
        compare="table",
        choices=('mode="a" adds the sheet to the Excel file that is there and keeps its other sheets; '
                 'if_sheet_exists="replace" replaces a sheet of the same name (simplydata prints that it did). A '
                 "file that does not exist yet is made with pandas ExcelWriter and that one sheet.",),
        also="simplydata checks the sheet name first with Excel's rules as openpyxl states them (at most 31 characters, "
             "none of : \\ / ? * [ ]) and refuses a name Excel would count as the same in other capitals, so a "
             "refused name leaves the file as it was. Polars tables go through pandas too. The test reads the "
             'workbook back with sheet="all" (pandas read_excel(sheet_name=None)).',
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
            table.keep_rows_where("subject", is_equal_to="Maths")
            table.show_rows_with_outliers("marks", for_each_group_in="class")
        """,
        code={"pandas": """
            import pandas as pd
            df = pd.read_csv("marks.csv")
            df = df[df["subject"] == "Maths"].reset_index(drop=True)   # one row per child
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
            table.keep_rows_where("subject", is_equal_to="Maths")
            table.find_interval_of("marks", "average")
        """,
        code={"SciPy": """
            import numpy as np
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("marks.csv")
            df = df[df["subject"] == "Maths"].reset_index(drop=True)   # one row per child
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


# ---------------------------------------------------------------- tables phase, batch 1 (approved by Manish 2026-11-25)
ENTRIES += [
    Entry(
        word="table.keep_rows_found_in",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_rows_found_in({"name": ["Asha", "Ben", "Asha"]}, using="name")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                other = pd.DataFrame({"name": ["Asha", "Ben", "Asha"]})
                # keep_rows_found_in(other, using="name")
                df[df["name"].isin(other["name"])]                                   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                other = pl.DataFrame({"name": ["Asha", "Ben", "Asha"]})
                # keep_rows_found_in(other, using="name")
                df.join(other.unique(), on="name", how="semi", maintain_order="left")  # (1)
            """,
        },
        compare="table",
        choices=("a semi join: no column comes in from the other table and no row is repeated, however often a name "
                 "appears there; the rows keep their order, and an empty key is never found.",),
        also="using= also pairs columns with different names, using={\"sample_id\": \"sample\"}. " + SAID,
    ),
    Entry(
        word="table.remove_rows_found_in",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.remove_rows_found_in({"name": ["Asha", "Ben"]}, using="name")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                other = pd.DataFrame({"name": ["Asha", "Ben"]})
                # remove_rows_found_in(other, using="name")
                df[~df["name"].isin(other["name"])]                                  # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                other = pl.DataFrame({"name": ["Asha", "Ben"]})
                # remove_rows_found_in(other, using="name")
                df.join(other, on="name", how="anti", maintain_order="left")         # (1)
            """,
        },
        compare="table",
        choices=("an anti join: the rows whose name is not in the other table stay, in their order; a row with an "
                 "empty key is never found, so it stays.",),
        also=SAID,
    ),
    Entry(
        word="table.clean_column_names",
        data="fjord_stations",
        ours="""
            table = sdata.get_example("fjord_stations")
            table.clean_column_names()
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("fjord_stations.csv")
                # clean_column_names()
                names = (df.columns.str.replace("%", "_percent_").str.normalize("NFKD")
                         .str.encode("ascii", "ignore").str.decode("ascii")
                         .str.replace(r"[^0-9A-Za-z]+", "_", regex=True)
                         .str.strip("_").str.lower())                                 # (1)
                df.set_axis(names, axis=1)
            """,
            "Polars": """
                import polars as pl, re, unicodedata
                df = pl.read_csv("fjord_stations.csv")
                # clean_column_names()
                ascii_ = [unicodedata.normalize("NFKD", c).encode("ascii", "ignore").decode() for c in df.columns]
                df.rename({c: re.sub(r"[^0-9A-Za-z]+", "_", a).strip("_").lower()
                           for c, a in zip(df.columns, ascii_)})                     # (1)
            """,
        },
        compare="table",
        choices=("the rule of R janitor::clean_names(): % becomes percent and # number, letters such as ø and é "
                 "become plain letters, every run of other signs one \"_\", small letters; a name that starts with a "
                 "digit gets an x in front and a repeated name _2. Unlike janitor, pH becomes ph, not p_h.",),
        also="simplydata also prints each change, old -> new. " + SAID,
    ),
    Entry(
        word="table.remove_rows_that_are_all_empty",
        data="fjord_lab",
        ours="""
            table = sdata.get_example("fjord_lab")
            table.remove_rows_that_are_all_empty()
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("fjord_lab.csv", dtype={"sample_id": str})
                # remove_rows_that_are_all_empty()
                df.dropna(how="all")                                                 # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("fjord_lab.csv", schema_overrides={"sample_id": pl.String})
                # remove_rows_that_are_all_empty()
                df.filter(~pl.all_horizontal(pl.all().is_null()))                    # (1)
            """,
        },
        compare="table",
        choices=("a row goes only when every cell is empty; an empty cell is a missing value or text of only spaces "
                 "(pandas and Polars count \"   \" as filled).",),
        also="remove_rows_with_empty_cells_in() is the word that removes a row for one empty cell. " + SAID,
    ),
    Entry(
        word="table.remove_columns_that_are_all_empty",
        data="fjord_lab",
        ours="""
            table = sdata.get_example("fjord_lab")
            table.remove_columns_that_are_all_empty()
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("fjord_lab.csv", dtype={"sample_id": str})
                # remove_columns_that_are_all_empty()
                df.dropna(axis=1, how="all")                                         # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("fjord_lab.csv", schema_overrides={"sample_id": pl.String})
                # remove_columns_that_are_all_empty()
                df.select([c for c in df.columns if df[c].null_count() < df.height])  # (1)
            """,
        },
        compare="table",
        choices=("a column goes only when every cell is empty (a missing value or text of only spaces); a table "
                 "whose every cell is empty is refused rather than left with no columns.",),
        also="simplydata also names the columns it removed. " + SAID,
    ),
    Entry(
        word="table.show_duplicate_rows",
        data="fjord_lab",
        ours="""
            table = sdata.get_example("fjord_lab")
            table.remove_rows_that_are_all_empty()
            table.show_duplicate_rows()
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("fjord_lab.csv", dtype={"sample_id": str}).dropna(how="all")
                # show_duplicate_rows()
                repeats = df[df.duplicated(keep=False)]                              # (1)
                n, kinds = len(repeats), len(repeats.drop_duplicates())
                print(f"{n} rows repeat another row: {kinds} different rows are there more than once "
                      f"({n - kinds} extra copies).")
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("fjord_lab.csv", schema_overrides={"sample_id": pl.String})
                df = df.filter(~pl.all_horizontal(pl.all().is_null()))
                # show_duplicate_rows()
                repeats = df.filter(df.is_duplicated())                              # (1)
                n, kinds = repeats.height, repeats.unique().height
                print(f"{n} rows repeat another row: {kinds} different rows are there more than once "
                      f"({n - kinds} extra copies).")
            """,
        },
        compare="printed",
        choices=("every copy is shown, the first one too (keep=False), each with its row number counted from 1, and "
                 "two empty cells count as the same; the table does not change.",),
        also="simplydata also prints the rows themselves and the remove_duplicate_rows() line that would remove them.",
    ),
    Entry(
        word="table.add_row_summary_column",
        data="clinic",
        ours="""
            table = sdata.get_example("clinic")
            table.add_row_summary_column("pain_average", columns=["pain_week_0", "pain_week_4", "pain_week_8"],
                                         show="average")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("clinic.csv")
                weeks = ["pain_week_0", "pain_week_4", "pain_week_8"]
                # add_row_summary_column("pain_average", columns=weeks, show="average")
                df.assign(pain_average=df[weeks].mean(axis=1))                      # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("clinic.csv")
                weeks = ["pain_week_0", "pain_week_4", "pain_week_8"]
                # add_row_summary_column("pain_average", columns=weeks, show="average")
                df.with_columns(pl.mean_horizontal(weeks).alias("pain_average"))     # (1)
            """,
        },
        compare="table",
        choices=("empty cells are left out of each row's summary, as pandas (skipna) and Polars do; a row with every "
                 "cell empty gets an empty cell, also for show=\"total\" (pandas sum(min_count=1); Polars "
                 "sum_horizontal alone would give 0).",),
        also="show= also gives the total, median, smallest, biggest, standard deviation or count of each row. " + SAID,
    ),
    Entry(
        word="table.turn_into_categories",
        data="clinic",
        ours="""
            table = sdata.get_example("clinic")
            table.turn_into_categories("nurse_rating", in_order=["mild", "moderate", "severe"])
            table.sort_by("nurse_rating")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("clinic.csv")
                # turn_into_categories("nurse_rating", in_order=["mild", "moderate", "severe"])
                df["nurse_rating"] = pd.Categorical(df["nurse_rating"], ordered=True,
                                                    categories=["mild", "moderate", "severe"])   # (1)
                df.sort_values("nurse_rating", kind="stable")
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("clinic.csv")
                # turn_into_categories("nurse_rating", in_order=["mild", "moderate", "severe"])
                order = pl.Enum(["mild", "moderate", "severe"])
                df = df.with_columns(pl.col("nurse_rating").cast(order))             # (1)
                df.with_row_index().sort("nurse_rating", "index").drop("index")
            """,
        },
        compare="table",
        choices=("a value that is not in in_order= stops the word with its name (pandas Categorical would turn it "
                 "into an empty cell without a word; Polars Enum refuses it too); without in_order= the order is the "
                 "one in which the values first appear.",),
        also="simplydata also says the order in a sentence and names the listed values the column does not hold yet. "
             + SAID,
    ),
    Entry(
        word="table.split_into_rows",
        data="fjord_samples",
        ours="""
            table = sdata.get_example("fjord_samples")
            table.keep_columns("sample_id", "station", "crew")
            table.split_into_rows("crew", separator=";")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("fjord_samples.csv")[["sample_id", "station", "crew"]]
                # split_into_rows("crew", separator=";")
                df.assign(crew=df["crew"].str.split(";")).explode("crew", ignore_index=True)   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("fjord_samples.csv").select("sample_id", "station", "crew")
                # split_into_rows("crew", separator=";")
                df.with_columns(pl.col("crew").str.split(";")).explode("crew")       # (1)
            """,
        },
        compare="table",
        choices=("the separator is plain text, not a pattern; a cell without it stays one row, and an empty cell "
                 "stays one row with an empty cell.",),
        also="A column that already holds lists is split without separator=, and a note says when new cells start "
             "or end with a space. " + SAID,
    ),
    Entry(
        word="table.add_running_column",
        data="shop",
        ours="""
            table = sdata.get_example("shop")
            table.add_running_column("sales_so_far", from_column="sales", show="total",
                                     for_each_group_in="shop", sorted_by="date")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("shop.csv", parse_dates=["date"])
                # add_running_column("sales_so_far", from_column="sales", show="total", ...)
                ordered = df.sort_values("date", kind="stable")                      # (1)
                so_far = ordered.groupby("shop", dropna=False)["sales"].cumsum()     # (2)
                df.assign(sales_so_far=so_far.sort_index())
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("shop.csv", try_parse_dates=True)
                # add_running_column("sales_so_far", from_column="sales", show="total", ...)
                so_far = pl.col("sales").cum_sum().over("shop", order_by="date")     # (1) (2)
                df.with_columns(so_far.alias("sales_so_far"))
            """,
        },
        compare="table",
        choices=("the sum follows sorted_by= (here the date) while the rows keep their place in the table;",
                 "an empty cell stays empty and is left out of the rows after it (for show=\"average\" too, whose "
                 "pandas expanding().mean() would carry the average on).",),
        also="show= also gives the running average, smallest, biggest, count or product. " + SAID,
    ),
    Entry(
        word="table.add_row_number_column",
        data="river",
        ours="""
            table = sdata.get_example("river")
            table.add_row_number_column("day_number", for_each_group_in="station", sorted_by="date")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("river.csv", parse_dates=["date"])
                # add_row_number_column("day_number", for_each_group_in="station", sorted_by="date")
                ordered = df.sort_values("date", kind="stable")
                number = ordered.groupby("station", dropna=False).cumcount() + 1     # (1)
                df.assign(day_number=number.sort_index())
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("river.csv", try_parse_dates=True)
                # add_row_number_column("day_number", for_each_group_in="station", sorted_by="date")
                number = pl.int_range(1, pl.len() + 1).over("station", order_by="date")   # (1)
                df.with_columns(number.alias("day_number"))
            """,
        },
        compare="table",
        choices=("numbers start at 1, as table.show() counts (pandas cumcount() starts at 0), in the order of "
                 "sorted_by=, while the rows keep their place.",),
        also=SAID,
    ),
    Entry(
        word="table.keep_groups_where",
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.keep_groups_where("average(marks) >= 50", for_each_group_in="school")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("school.csv")
                # keep_groups_where("average(marks) >= 50", for_each_group_in="school")
                df.groupby("school").filter(lambda group: group["marks"].mean() >= 50)   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("school.csv")
                # keep_groups_where("average(marks) >= 50", for_each_group_in="school")
                df.filter(pl.col("marks").mean().over("school") >= 50)               # (1)
            """,
        },
        compare="table",
        choices=("whole groups stay or go, in their places; empty cells are left out of each summary, and a group "
                 "whose summary cannot be worked out (every cell empty) is left out.",),
        also="count() alone counts the rows of each group, and the condition can join summaries with and / or. "
             "simplydata also says how many groups and rows stayed. " + SAID,
    ),
    Entry(
        word="table.remove_groups_where",
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.remove_groups_where("average(marks) < 50", for_each_group_in="school")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("school.csv")
                # remove_groups_where("average(marks) < 50", for_each_group_in="school")
                df.groupby("school").filter(lambda group: not group["marks"].mean() < 50)   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("school.csv")
                # remove_groups_where("average(marks) < 50", for_each_group_in="school")
                df.filter(~(pl.col("marks").mean().over("school") < 50))             # (1)
            """,
        },
        compare="table",
        choices=("whole groups go, the others stay in their places; a group whose summary cannot be worked out is "
                 "never removed.",),
        also=SAID,
    ),
    # options of existing words
    Entry(
        word="table.join_with",
        option="using=",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.join_with({"student": ["Asha", "Ben"], "age": [12, 13]}, using={"name": "student"},
                            check_that="each row has one match")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                ages = pd.DataFrame({"student": ["Asha", "Ben"], "age": [12, 13]})
                # join_with(ages, using={"name": "student"}, check_that="each row has one match")
                joined = df.merge(ages, left_on="name", right_on="student",
                                  validate="many_to_one")                            # (1)
                joined.drop(columns="student")                                       # (2)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                ages = pl.DataFrame({"student": ["Asha", "Ben"], "age": [12, 13]})
                # join_with(ages, using={"name": "student"}, check_that="each row has one match")
                df.join(ages, left_on="name", right_on="student", validate="m:1",
                        maintain_order="left_right")                                 # (1) (2)
            """,
        },
        compare="table",
        choices=("check_that= runs pandas' and Polars' own validate= and, when a key repeats, says which values "
                 "repeat and in which table, before anything is joined;",
                 "the key keeps this table's name only (pandas keeps both columns; Polars drops the other's).",),
        also="keep=\"all rows from the other table\" is the right join, and with_match_column=True adds a column "
             "\"found in\" (pandas merge(indicator=True)). " + SAID,
    ),
    Entry(
        word="table.spread_into_columns",
        option="show=",
        data="fruit",
        ours="""
            table = sdata.get_example("fruit")
            table.keep_columns("day", "fruit", "count")
            table.spread_into_columns(names_from="fruit", values_from="count", show="total")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("fruit.csv")
                # spread_into_columns(names_from="fruit", values_from="count", show="total")
                wide = df.pivot_table(index="day", columns="fruit", values="count", aggfunc="sum")
                wide = wide.loc[df["day"].unique(), df["fruit"].unique()]              # (1)
                wide.reset_index().rename_axis(columns=None)                           # (2)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("fruit.csv")
                # spread_into_columns(names_from="fruit", values_from="count", show="total")
                wide = df.pivot(on="fruit", index="day", values="count", aggregate_function="sum")   # (1)
                pairs = df.pivot(on="fruit", index="day", values="count", aggregate_function="len")
                wide.with_columns(pl.when(pairs[c] > 0).then(pl.col(c)).alias(c)
                                  for c in wide.columns[1:])                           # (2)
            """,
        },
        compare="table",
        choices=("rows and new columns stay in the order they first appear (pandas pivot_table sorts them);",
                 "a day and fruit that never appear together stay an empty cell for every show= (Polars gives 0 for "
                 "a total or count of no rows).",),
        also="Without show= simplydata stops when two rows would fill one cell, names them and suggests show=, so "
             "nothing is combined without your word. " + SAID,
    ),
    Entry(
        word="table.change_column",
        option="in_rows_where=",
        data="school",
        ours="""
            table = sdata.get_example("school")
            table.change_column("passed", value="yes", in_rows_where="marks >= 45")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("school.csv")
                # change_column("passed", value="yes", in_rows_where="marks >= 45")
                df.loc[df["marks"] >= 45, "passed"] = "yes"                          # (1)
                df
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("school.csv")
                # change_column("passed", value="yes", in_rows_where="marks >= 45")
                df.with_columns(pl.when(pl.col("marks") >= 45).then(pl.lit("yes"))
                                .otherwise(pl.col("passed")).alias("passed"))        # (1)
            """,
        },
        compare="table",
        choices=("the condition is read on the values before the change, and a row it cannot check (an empty cell) "
                 "keeps its value, with a note.",),
        also="replace_values_in and fill_empty_cells_in take in_rows_where= too. simplydata also says how many cells "
             "changed. " + SAID,
    ),
    Entry(
        word="table.keep_first_rows",
        option="for_each_group_in=",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.sort_by("marks", biggest_first=True)
            table.keep_first_rows(2, for_each_group_in="subject")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv").sort_values("marks", ascending=False, kind="stable")
                # keep_first_rows(2, for_each_group_in="subject")
                df.groupby("subject", sort=False, dropna=False).head(2)              # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv").sort("marks", descending=True, maintain_order=True)
                # keep_first_rows(2, for_each_group_in="subject")
                df.filter(pl.int_range(pl.len()).over("subject") < 2)                # (1)
            """,
        },
        compare="table",
        choices=("the rows keep their order in the table (Polars group_by().head() would put each group's rows "
                 "together), and an empty group cell is a group of its own.",),
        also="keep_last_rows and keep_rows_by_position take for_each_group_in= too. " + SAID,
    ),
]


# ---------------------------------------------------------------- tables phase, batch 3 (approved by Manish 2026-11-25)
ENTRIES += [
    Entry(
        word="table.add_zeros_in_front_of",
        data="fjord_samples",
        ours="""
            table = sdata.get_example("fjord_samples")
            table.keep_columns("sample_id", "station")
            table.turn_into_text("sample_id")
            table.add_zeros_in_front_of("sample_id", to_length=3)
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("fjord_samples.csv")[["sample_id", "station"]]
                # add_zeros_in_front_of("sample_id", to_length=3)
                df["sample_id"] = df["sample_id"].astype(str).str.zfill(3)          # (1)
                df
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("fjord_samples.csv").select("sample_id", "station")
                # add_zeros_in_front_of("sample_id", to_length=3)
                df.with_columns(pl.col("sample_id").cast(pl.String).str.zfill(3))     # (1)
            """,
        },
        compare="table",
        choices=("zeros go in front until the text has to_length= characters; a longer text is never cut, a minus or "
                 "plus sign stays in front, and an empty cell stays empty (str.zfill in pandas and Polars).",),
        also="simplydata also says how many values changed and how many were already longer. " + SAID,
    ),
    Entry(
        word="table.move_columns",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.move_columns("marks", "hours", to="start")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # move_columns("marks", "hours", to="start")
                moved = ["marks", "hours"]
                df[moved + [c for c in df.columns if c not in moved]]
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # move_columns("marks", "hours", to="start")
                moved = ["marks", "hours"]
                df.select(moved + [c for c in df.columns if c not in moved])
            """,
        },
        compare="table",
        also="to=\"end\" puts them last and after=\"name\" just after that column; the other columns keep their order. "
             + SAID,
    ),
    Entry(
        word="table.show_rows_with_empty_cells_in",
        data="shop",
        ours="""
            table = sdata.get_example("shop")
            table.show_rows_with_empty_cells_in()
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("shop.csv")
                # show_rows_with_empty_cells_in()
                holes = df[df.isna().any(axis=1)]                                    # (1)
                print(f"{len(holes)} rows of {len(df)} have an empty cell:")
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("shop.csv")
                # show_rows_with_empty_cells_in()
                holes = df.filter(pl.any_horizontal(pl.all().is_null()))              # (1)
                print(f"{holes.height} rows of {df.height} have an empty cell:")
            """,
        },
        compare="printed",
        choices=("a row is shown when any of its cells (or of the columns= named) is empty, with its row number counted "
                 "from 1; text of only spaces counts as empty too, and the table does not change.",),
        also="simplydata also prints the rows themselves and the remove_rows_with_empty_cells_in() line that would "
             "remove them.",
    ),
    Entry(
        word="table.show_differences_from",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.replace_values_in("marks", is_above=90, with_value=90)
            table.show_differences_from(sdata.get_example("marks"))
        """,
        code={
            "pandas": """
                import pandas as pd
                original = pd.read_csv("marks.csv")
                df = original.copy()
                df.loc[df["marks"] > 90, "marks"] = 90
                # show_differences_from(original)
                cells = df.compare(original, result_names=("this", "other"))         # (1)
                n = int(cells.xs("this", axis=1, level=1).notna().sum().sum())
                print(f"{n} cells differ, in {len(cells)} rows (rows counted from 1; empty cells shown as None):")
            """,
        },
        compare="printed",
        choices=("rows are compared in order (row 3 with row 3), and two empty cells count as the same (pandas "
                 "compare); tables with other columns or another number of rows are not compared cell by cell, and "
                 "simplydata says how they differ. Polars tables go through pandas compare.",),
        also="simplydata also shows the differing cells as row, column, this, other, with rows counted from 1.",
    ),
    Entry(
        word="table.check_if_same_as",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.round_numbers_in("hours", 0)
            table.check_if_same_as(sdata.get_example("marks"))
        """,
        code={
            "pandas": """
                import pandas as pd
                original = pd.read_csv("marks.csv")
                df = original.round({"hours": 0})
                # check_if_same_as(original)
                df.equals(original)                                                  # (1)
            """,
            "Polars": """
                import polars as pl
                original = pl.read_csv("marks.csv")
                df = original.with_columns(pl.col("hours").round(0))
                # check_if_same_as(original)
                df.equals(original)                                                  # (1)
            """,
        },
        compare="value",
        choices=("the same means the same columns in the same order, the same rows, the same values and the same kinds "
                 "(pandas and Polars equals); two empty cells count as the same.",),
        also="simplydata also names the first difference: a column, a row and the two values, or the kinds.",
    ),
    Entry(
        word="table.run_sql",
        data="river",
        ours="""
            table = sdata.get_example("river")
            table.run_sql("SELECT station, avg(nitrate) AS nitrate FROM data GROUP BY station ORDER BY station")
        """,
        code={
            "DuckDB": """
                import duckdb
                import pandas as pd
                df = pd.read_csv("river.csv")
                # run_sql("SELECT station, avg(nitrate) AS nitrate FROM data GROUP BY station ORDER BY station")
                con = duckdb.connect(config={"autoload_known_extensions": False,
                                             "enable_external_access": False})       # (1)
                con.register("data", df)                                             # (2)
                con.sql("SELECT station, avg(nitrate) AS nitrate FROM data GROUP BY station ORDER BY station").df()
            """,
        },
        compare="table",
        choices=("DuckDB runs with no extensions loaded or installed on their own and no access to files or the web, "
                 "the settings locked, and only one SELECT is run: a query can never fetch, install or write anything;",
                 "inside the query the table is called data; a Polars table comes back as Polars (.pl()), and without "
                 "DuckDB, Polars SQL runs the query (pl.SQLContext).",),
        also="simplydata also says which engine ran and the size of the answer; the table itself does not change.",
    ),
    Entry(
        word="sdata.run_sql",
        data="river",
        ours="""
            import os
            import tempfile
            with tempfile.TemporaryDirectory() as folder:
                river = os.path.join(folder, "river.csv").replace(os.sep, "/")
                sdata.get_example("river").save(river)
                answer = sdata.run_sql(f"SELECT station, max(level) AS level FROM '{river}' GROUP BY station "
                                       "ORDER BY station")
            answer
        """,
        code={
            "DuckDB": """
                import duckdb
                # run_sql("SELECT station, max(level) AS level FROM 'river.csv' GROUP BY station ORDER BY station")
                con = duckdb.connect(config={"autoload_known_extensions": False,
                                             "autoinstall_known_extensions": False})  # (1)
                con.sql("SELECT station, max(level) AS level FROM 'river.csv' GROUP BY station "
                        "ORDER BY station").df()
            """,
        },
        compare="table",
        choices=("DuckDB reads the files on this computer, with no extensions loaded or installed on their own (so no "
                 "web or cloud address can be read), the settings locked, and only one SELECT is run; an address "
                 "such as https:// or s3:// is refused before DuckDB sees it.",),
        also="The file is read by DuckDB itself: only the rows and columns the query needs. The test saves the "
             "practice table in a folder that is deleted afterwards.",
    ),
    Entry(
        word="table.make_one_table_for_each_group_in",
        data="river",
        ours="""
            table = sdata.get_example("river")
            tables = table.make_one_table_for_each_group_in("station")
            tables["Station B"]
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("river.csv", parse_dates=["date"])
                # make_one_table_for_each_group_in("station")
                tables = {name: part for name, part in df.groupby("station", sort=False, dropna=False)}  # (1)
                tables["Station B"]
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("river.csv", try_parse_dates=True)
                # make_one_table_for_each_group_in("station")
                tables = df.partition_by("station", maintain_order=True, as_dict=True)  # (1)
                tables[("Station B",)]
            """,
        },
        compare="table",
        choices=("the groups come in the order they are first seen and the rows keep their order; rows with an empty "
                 "cell in the column make a group of their own (dropna=False), and with one column each table is "
                 "found by the value itself: tables[\"Station B\"].",),
        also="simplydata also says how many tables there are, their sizes and how to get one.",
    ),
    Entry(
        word="table.as_list",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.as_list()
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # as_list()
                df.to_dict("records")
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # as_list()
                df.to_dicts()
            """,
        },
        compare="value",
        also="It is a copy: changing the list does not change the table.",
    ),
    # options of existing words
    Entry(
        word="table.find_summary_of",
        option="show=",
        data="river",
        ours="""
            table = sdata.get_example("river")
            table.find_summary_of("level", show=["first", "biggest", "smallest", "last"], for_each_group_in="station")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("river.csv")
                # find_summary_of("level", show=["first", "biggest", "smallest", "last"], for_each_group_in="station")
                found = df.groupby("station")["level"].agg(["first", "max", "min", "last"])   # (1)
                found = found.rename(columns={"max": "biggest", "min": "smallest"}).reset_index()
                found.insert(0, "column", "level")
                found
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("river.csv")
                # find_summary_of("level", show=["first", "biggest", "smallest", "last"], for_each_group_in="station")
                level = pl.col("level").drop_nulls()
                df.group_by("station", maintain_order=True).agg(
                    pl.lit("level").alias("column"), level.first().alias("first"),
                    level.max().alias("biggest"), level.min().alias("smallest"),
                    level.last().alias("last")).select("column", "station", "first", "biggest", "smallest", "last")  # (1)
            """,
        },
        compare="table",
        choices=("\"first\" and \"last\" are the first and last filled value in the order of the rows (pandas "
                 "groupby first() and last() skip empty cells; Polars drop_nulls() then first() and last()): sort "
                 "first with sort_by for another order.",),
        also="With every=\"month\" the same four give each month's open, high, low and close (pandas resample().ohlc()).",
    ),
    Entry(
        word="table.sort_by",
        option="biggest_first=",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.sort_by("class", "marks", biggest_first=[False, True])
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # sort_by("class", "marks", biggest_first=[False, True])
                df.sort_values(["class", "marks"], ascending=[True, False], kind="stable")   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # sort_by("class", "marks", biggest_first=[False, True])
                df.sort(["class", "marks"], descending=[False, True], maintain_order=True)   # (1)
            """,
        },
        compare="table",
        choices=("a list gives each column its own direction, one True or False for each; pandas' ascending= is the "
                 "opposite (ascending=[True, False]), Polars' descending= the same; rows that tie keep their order.",),
        also=SAID,
    ),
    Entry(
        word="table.gather_into_rows",
        option="starts_with=",
        data="clinic",
        ours="""
            table = sdata.get_example("clinic")
            table.keep_columns("patient", "pain_week_0", "pain_week_4", "pain_week_8")
            table.gather_into_rows(starts_with="pain_week_", names_to="week", values_to="pain")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("clinic.csv")[["patient", "pain_week_0", "pain_week_4", "pain_week_8"]]
                # gather_into_rows(starts_with="pain_week_", names_to="week", values_to="pain")
                weeks = [c for c in df.columns if c.startswith("pain_week_")]        # (1)
                df.melt(id_vars=["patient"], value_vars=weeks, var_name="week", value_name="pain")
            """,
            "Polars": """
                import polars as pl
                import polars.selectors as cs
                df = pl.read_csv("clinic.csv").select("patient", "pain_week_0", "pain_week_4", "pain_week_8")
                # gather_into_rows(starts_with="pain_week_", names_to="week", values_to="pain")
                df.unpivot(on=cs.starts_with("pain_week_"), index="patient",
                           variable_name="week", value_name="pain")                  # (1)
            """,
        },
        compare="table",
        choices=("starts_with=, ends_with= and matches_pattern= choose the columns by their names exactly as "
                 "keep_columns does (capital letters matter), in table order; one way at a time.",),
        also=SAID,
    ),
    Entry(
        word="table.join_with",
        option="match=",
        data="river",
        ours="""
            table = sdata.get_example("river")
            rain = sdata.table({"date": ["2024-01-01", "2024-01-08", "2024-01-15"], "rain_mm": [12.0, 3.5, 20.1]})
            rain.turn_into_dates("date")
            table.join_with(rain, using="date", match="nearest before", within="3 days",
                            keep="all rows from this table")
            table.keep_columns("date", "station", "rain_mm")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("river.csv", parse_dates=["date"])[["date", "station"]]
                rain = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-01-08", "2024-01-15"]),
                                     "rain_mm": [12.0, 3.5, 20.1]})
                # join_with(rain, using="date", match="nearest before", within="3 days")
                df = df.reset_index().sort_values("date", kind="stable")             # (1)
                joined = pd.merge_asof(df, rain, on="date", direction="backward",
                                       tolerance=pd.Timedelta(days=3))               # (2)
                joined.sort_values("index").drop(columns="index")
            """,
            "Polars": """
                import datetime
                import polars as pl
                df = pl.read_csv("river.csv", try_parse_dates=True).select("date", "station").with_row_index()
                rain = pl.DataFrame({"date": [datetime.date(2024, 1, d) for d in (1, 8, 15)], "rain_mm": [12.0, 3.5, 20.1]})
                # join_with(rain, using="date", match="nearest before", within="3 days")
                joined = df.sort("date").join_asof(rain.sort("date"), on="date", strategy="backward",
                                                   tolerance=datetime.timedelta(days=3))  # (1) (2)
                joined.sort("index").drop("index")
            """,
        },
        compare="table",
        choices=("both tables are sorted by the date first, as merge_asof and join_asof need, and the rows go back to "
                 "this table's order afterwards;",
                 "\"nearest before\" takes the last row at or before each date (backward), \"nearest after\" the first "
                 "at or after (forward), \"nearest\" either; within= is the furthest it looks (tolerance), and "
                 "keep=\"matching rows\" leaves out the rows with nothing near enough.",),
        also="simplydata also brings the other table's date in as \"date_other\" and says how many rows found a match. "
             + SAID,
    ),
    Entry(
        word="table.join_with",
        option='keep="every combination"',
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_columns("name", "subject")
            table.join_with({"term": ["autumn", "spring"]}, keep="every combination")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")[["name", "subject"]]
                terms = pd.DataFrame({"term": ["autumn", "spring"]})
                # join_with(terms, keep="every combination")
                df.merge(terms, how="cross")
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv").select("name", "subject")
                terms = pl.DataFrame({"term": ["autumn", "spring"]})
                # join_with(terms, keep="every combination")
                df.join(terms, how="cross")
            """,
        },
        compare="table",
        also="simplydata also says how many rows came out: 54 x 2 = 108. " + SAID,
    ),
    Entry(
        word="table.save",
        option="in_table=",
        data="marks",
        ours="""
            import os
            import tempfile
            table = sdata.get_example("marks")
            with tempfile.TemporaryDirectory() as folder:
                results = os.path.join(folder, "results.sqlite")
                table.save(results, in_table="marks")
                table.save(results, in_table="marks_again")
                back = sdata.table(results, table_name="marks_again")
            back
        """,
        code={
            "pandas": """
                import os
                import sqlite3
                import tempfile
                import pandas as pd
                df = pd.read_csv("marks.csv")
                with tempfile.TemporaryDirectory() as folder:
                    con = sqlite3.connect(os.path.join(folder, "results.sqlite"))
                    # save as results.sqlite with in_table="marks_again"
                    df.to_sql("marks_again", con, if_exists="replace", index=False)  # (1)
                    back = pd.read_sql_query('SELECT * FROM "marks_again"', con)
                    con.close()
                back
            """,
        },
        compare="table",
        choices=("in_table= replaces that one table and keeps the other tables of the file (if_exists=\"replace\"), "
                 "with no row labels (index=False); a .duckdb file is written by DuckDB, with no extensions.",),
        also="simplydata says when it replaced a table. Read it back with sdata.table(\"results.sqlite\", "
             "table_name=\"marks_again\"). The test writes in a folder that is deleted afterwards.",
    ),
]
