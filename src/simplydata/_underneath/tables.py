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
