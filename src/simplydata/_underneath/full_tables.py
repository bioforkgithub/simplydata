"""Families for 100 %, batches 1-2 (approved by Manish 2026-11-28): the table words and options for the pandas and
Polars gaps (section 2.1 of the plan) and the seaborn.objects marks and moves (section 2.5)."""

from . import Entry

SAID = "simplydata also says in a sentence what changed, and keeps the table before the step (undo)."
TOLD = "simplydata also says the answer in a sentence."

ENTRIES = [
    # ---------------------------------------------------------------- new table words
    Entry(
        word="table.get_different_values_in",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.get_different_values_in("class")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # get_different_values_in("class")
                list(df["class"].dropna().unique())                                   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # get_different_values_in("class")
                df["class"].drop_nulls().unique(maintain_order=True).to_list()        # (1)
            """,
        },
        compare="value",
        tolerance=0.0,
        choices=("the values in the order they first turn up, empty cells left out (pandas unique() keeps an empty "
                 "value; Polars unique() needs maintain_order=True for this order).",),
        also="A column of numbers comes back as sdata.number_list, any other as a plain list, as get_column does. "
             + TOLD,
    ),
    Entry(
        word="table.check_if_all_values_in",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.check_if_all_values_in("marks", is_above=40)
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # check_if_all_values_in("marks", is_above=40)
                marks = df["marks"].dropna()                                          # (1)
                bool((marks > 40).all())
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # check_if_all_values_in("marks", is_above=40)
                df.select((pl.col("marks").drop_nulls() > 40).all()).item()           # (1)
            """,
        },
        compare="value",
        tolerance=0.0,
        choices=("empty cells are left out, as pandas all() and Polars all() leave them out.",),
        also="It says how many values fail and the first row that does; a list of columns checks them all (Polars "
             "all_horizontal), and for_each_group_in= gives the answer for each group (pandas groupby().all()).",
    ),
    Entry(
        word="table.check_if_any_value_in",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.check_if_any_value_in("marks", is_above=90)
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # check_if_any_value_in("marks", is_above=90)
                bool((df["marks"].dropna() > 90).any())                               # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # check_if_any_value_in("marks", is_above=90)
                df.select((pl.col("marks").drop_nulls() > 90).any()).item()           # (1)
            """,
        },
        compare="value",
        tolerance=0.0,
        choices=("empty cells are left out, as pandas any() and Polars any() leave them out.",),
        also="It says how many values meet the condition and the first row that does (Polars any_horizontal for a "
             "list of columns, pandas groupby().any() with for_each_group_in=).",
    ),
    Entry(
        word="table.check_if_sorted_by",
        data="weather",
        ours="""
            table = sdata.get_example("weather")
            table.sort_by("city", "month_number")
            table.check_if_sorted_by("city")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("weather.csv").sort_values(["city", "month_number"], kind="stable")
                # check_if_sorted_by("city")
                bool(df["city"].dropna().is_monotonic_increasing)                     # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("weather.csv").sort(["city", "month_number"], maintain_order=True)
                # check_if_sorted_by("city")
                df["city"].drop_nulls().is_sorted()                                   # (1)
            """,
        },
        compare="value",
        tolerance=0.0,
        choices=("values that tie may follow each other, and empty cells are left out (pandas is_monotonic_increasing "
                 "says False for a column with an empty cell).",),
        also="biggest_first=True checks the other direction (is_monotonic_decreasing, is_sorted(descending=True)); "
             "it names the first row that is out of order. " + TOLD,
    ),
    Entry(
        word="table.add_run_number_column",
        data="river",
        ours="""
            table = sdata.get_example("river")
            table.add_group_column("band", from_column="level", cut_at=[2.5], names=["low", "high"])
            table.add_run_number_column("spell", from_column="band", for_each_group_in="station", sorted_by="date")
        """,
        code={
            "pandas": """
                import numpy as np
                import pandas as pd
                df = pd.read_csv("river.csv", parse_dates=["date"])
                df["band"] = np.select([df["level"] >= 2.5, df["level"] < 2.5], ["high", "low"], default=None)
                # add_run_number_column("spell", from_column="band", for_each_group_in="station", sorted_by="date")
                ordered = df.sort_values("date", kind="stable")                      # (1)
                spell = ordered.groupby("station")["band"].transform(
                    lambda s: (s.fillna("") != s.fillna("").shift()).cumsum())        # (2)
                df.assign(spell=spell)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("river.csv", try_parse_dates=True)
                band = pl.when(pl.col("level") >= 2.5).then(pl.lit("high")).when(pl.col("level") < 2.5).then(
                    pl.lit("low"))
                df = df.with_columns(band.alias("band"))
                # add_run_number_column("spell", from_column="band", for_each_group_in="station", sorted_by="date")
                spell = (pl.col("band").rle_id() + 1).over("station", order_by="date")   # (1) (2)
                df.with_columns(spell.alias("spell"))
            """,
        },
        compare="table",
        choices=("the runs follow sorted_by=, but the rows keep their place in the table.",
                 "within each station, counted from 1 (Polars rle_id() counts from 0); empty cells next to each other "
                 "are one run, as Polars counts them.",),
        also="count_rows(for_each_group_in=[\"station\", \"spell\"]) then gives the length of each run (Polars "
             "rle()). " + SAID,
    ),
    Entry(
        word="table.turn_into_title_case",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.turn_into_lowercase("name")
            table.turn_into_title_case("name")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                df["name"] = df["name"].str.lower()
                # turn_into_title_case("name")
                df.assign(name=df["name"].str.title())                                # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv").with_columns(pl.col("name").str.to_lowercase())
                # turn_into_title_case("name")
                df.with_columns(pl.col("name").str.to_titlecase())                    # (1)
            """,
        },
        compare="table",
        choices=("a new word starts after anything that is not a letter (\"o'neil\" becomes \"O'Neil\"): pandas "
                 "str.title() and Polars str.to_titlecase() agree on this.",),
        also=SAID,
    ),
]
