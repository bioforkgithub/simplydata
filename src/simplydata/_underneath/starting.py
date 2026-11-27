"""Starting words (U1): making a table, a chart, numbers, a grid, a distribution, random numbers and a run of
dates, and the help and 30-day words, which run no library at all (compare="none", with a note).
"""

from . import Entry

ENTRIES = [
    Entry(
        word="sdata.table",
        data="marks",
        ours="""
            from importlib.resources import files
            path = str(files("simplydata.data") / "marks.csv")
            sdata.table(path)
        """,
        code={"pandas": """
            from importlib.resources import files
            import pandas as pd
            path = str(files("simplydata.data") / "marks.csv")   # the practice file inside simplydata
            # table(path)
            pd.read_csv(path, sep=None, engine="python")         # (1)
        """},
        compare="table",
        choices=("the separator is guessed from the file (sep=None), so a file with ; or tabs between the values "
                 "is read too; separator= sets it yourself.",),
        also="simplydata reads the file with pandas (fast=True: with Polars), finds the type from the end of the "
             "name (.xlsx, .csv, .tsv, .parquet, .json, Word, SPSS, Stata) and keeps it ready for table words. A "
             "pandas or Polars table you already have is used as it is.",
    ),
    Entry(
        word="sdata.get_example",
        data="shop",
        ours="""
            sdata.get_example("shop")
        """,
        code={"pandas": """
            from importlib.resources import files
            import pandas as pd
            # get_example("shop")
            pd.read_csv(files("simplydata.data") / "shop.csv", parse_dates=["date"])   # (1)
        """},
        compare="table",
        choices=("a column of dates is read as dates (parse_dates=), so date words work on it at once.",),
        also="sdata.get_example() with no name lists every practice table and its columns.",
    ),
    Entry(
        word="sdata.chart",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            import pandas as pd
            df = pd.read_csv("marks.csv")
            # chart(df): the figure and its axes
            fig, ax = plt.subplots()
            sns.scatterplot(df, x="hours", y="marks", ax=ax)
        """},
        compare="chart",
        check=("dots", "labels", "limits"),
        also="sdata.chart() keeps the table (or reads a file with pandas) and makes the figure when the first "
             "chart word draws on it. simplydata's paper look (fonts, colours, no top and right lines) is left out "
             "here.",
    ),
    Entry(
        word="table.start_chart",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_rows_where("subject", is_equal_to="Maths")
            chart = table.start_chart()
            chart.draw_bars(x="name", y="marks")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import seaborn as sns
            import pandas as pd
            df = pd.read_csv("marks.csv")
            maths = df[df["subject"] == "Maths"]
            # start_chart(): the figure and its axes, from the table as it is now
            fig, ax = plt.subplots()
            sns.barplot(maths, x="name", y="marks", errorbar=None, ax=ax)
        """},
        compare="chart",
        check=("bars", "labels", "ticks"),
        also="The chart uses the table after all the steps so far (here only the Maths rows). simplydata's paper "
             "look is left out here.",
    ),
    Entry(
        word="sdata.number_list",
        ours="""
            sdata.number_list(0, to=100, step=25)
        """,
        code={"NumPy": """
            import numpy as np
            # number_list(0, to=100, step=25)
            n = int(np.floor((100 - 0) / 25 + 1e-9)) + 1     # (1)
            0 + 25 * np.arange(n)
        """},
        compare="value",
        tolerance=0.0,
        choices=("the end you give is included (0, 25, 50, 75, 100): simplydata counts how many steps fit (with a "
                 "little room for rounding) and multiplies. np.arange(0, 125, 25) gives the same here, but with a "
                 "decimal step np.arange can overshoot the end: np.arange(1, 1.4, 0.1) has 1.4 in it.",),
        also="sdata.number_list([3, 5, 2, 8]) is np.array([3, 5, 2, 8]), and how_many= is np.linspace(0, 1, 5). "
             "None in a list becomes an empty value (nan).",
    ),
    Entry(
        word="sdata.number_grid",
        ours="""
            sdata.number_grid([1, 2, 3, 4, 5, 6], columns=3)
        """,
        code={"NumPy": """
            import numpy as np
            # number_grid([1, 2, 3, 4, 5, 6], columns=3)
            np.array([1, 2, 3, 4, 5, 6]).reshape(-1, 3)    # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("the list is cut into rows, row after row (NumPy's order \"C\"): 1 2 3, then 4 5 6.",),
        also="sdata.number_grid([[1, 2, 3], [4, 5, 6]]) is np.array([[1, 2, 3], [4, 5, 6]]), and rows= with "
             "columns= and filled_with= is np.full(). simplydata stops with a message when the numbers cannot "
             "fill the grid exactly.",
    ),
    Entry(
        word="sdata.distribution",
        ours="""
            coins = sdata.distribution("binomial", tries=10, chance=0.5)
            coins.find_chance_that_value(is_at_most=3)
        """,
        code={"SciPy": """
            from scipy import stats
            # distribution("binomial", tries=10, chance=0.5)
            coins = stats.binom(n=10, p=0.5)        # (1)
            coins.cdf(3)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the parameters have plain names (tries=, chance=), turned into SciPy's (n, p); R's names "
                 "(size=, prob=) work too.",),
        also="Any other SciPy distribution works by its SciPy name and parameters. simplydata also writes each "
             "answer in a sentence with the same call in R (pbinom(3, size = 10, prob = 0.5)).",
    ),
    Entry(
        word="sdata.make_random_numbers",
        ours="""
            sdata.make_random_numbers(how_many=10, between=[1, 6], whole_numbers=True, with_seed=1)
        """,
        code={"NumPy": """
            import numpy as np
            # make_random_numbers(how_many=10, between=[1, 6], whole_numbers=True, with_seed=1)
            rng = np.random.default_rng(1)                 # (1)
            rng.integers(1, 6, 10, endpoint=True)          # (2)
        """},
        compare="value",
        tolerance=0.0,
        choices=("NumPy's random generator (default_rng) with the seed you give, the way NumPy recommends; "
                 "the old np.random.seed() gives other numbers.",
                 "both ends are included, like rolling a dice (endpoint=True); NumPy's own default leaves out 6.",),
        also="average= with standard_deviation= is rng.normal(), and between= without whole_numbers= is "
             "rng.uniform(). Without with_seed= the numbers change every time.",
    ),
    Entry(
        word="sdata.make_run_of_dates",
        ours="""
            sdata.make_run_of_dates("2026-01-30", how_many=4, every="month")
        """,
        code={"pandas": """
            import pandas as pd
            first = pd.Timestamp("2026-01-30")
            # make_run_of_dates("2026-01-30", how_many=4, every="month")
            dates = [first + pd.DateOffset(months=k) for k in range(4)]      # (1)
            pd.DataFrame({"date": dates})
        """},
        compare="table",
        choices=("each month is counted from the first date, so the dates stay on the 30th, or on the month's last "
                 "day when it is shorter (30 January, 28 February, 30 March, 30 April). pandas' "
                 "date_range(freq=DateOffset(months=1)) steps from the date before instead and stays on the 28th; "
                 "R's seq(by = \"month\") runs over into March.",),
        also="simplydata also says how many dates it made. to= gives the last date instead of how_many=, and "
             "fast=True gives a Polars table.",
    ),
    Entry(word="sdata.help", ours='sdata.help("draw_bars")', compare="none",
          note="simplydata's own: it reads its own word list and the words' docstrings, in plain Python. Python's "
               "help() shows a function's docstring too."),
    Entry(word="sdata.show_all_words", ours="sdata.show_all_words()", compare="none",
          note="simplydata's own: it prints its own word list, group by group, with a short example of each."),
    Entry(word="sdata.show_day", ours="sdata.show_day(5)", compare="none",
          note="simplydata's own: the 30 days are written in simplydata (learn_days.py) and printed in plain "
               "Python; nothing is computed."),
]


# ---------------------------------------------------------------- U3 batch 3: the lessons, the 30 days and the packages used
DAYS_NOTE = ("simplydata's own: the 30 days are written in simplydata (learn_days.py) and printed in plain Python; "
             "the day you reached is kept in a small JSON file on this computer (json, pathlib), and nothing is "
             "computed or sent anywhere.")

ENTRIES += [
    Entry(word="sdata.show_lesson", ours="sdata.show_lesson(1)", compare="none",
          note="simplydata's own: the lessons are written in simplydata (learn.py) and printed in plain Python; "
               "nothing is computed."),
    Entry(word="sdata.show_packages_used", ours="""
              table = sdata.get_example("marks")
              table.find_average_of("marks", for_each_group_in="class")
              sdata.show_packages_used()
          """, compare="none",
          note="simplydata's own: it notes which packages its words called, reads their versions from the installed "
               "metadata (Python's importlib.metadata; R's packageVersion() and citation() through rpy2 for R "
               "packages) and prints each reference with a sentence for your methods. No data are worked on; "
               "importlib.metadata.version(\"pandas\") gives one version yourself."),
    Entry(word="sdata.start_30_days", ours="""
              import os
              import tempfile
              before = os.environ.get("SIMPLYDATA_PROGRESS_FILE")   # the test keeps the progress in a
              with tempfile.TemporaryDirectory() as folder:          # folder deleted afterwards
                  os.environ["SIMPLYDATA_PROGRESS_FILE"] = os.path.join(folder, "progress.json")
                  try:
                      sdata.start_30_days()
                  finally:
                      os.environ.pop("SIMPLYDATA_PROGRESS_FILE")
                      if before is not None:
                          os.environ["SIMPLYDATA_PROGRESS_FILE"] = before
          """, compare="none",
          note=DAYS_NOTE),
    Entry(word="sdata.show_today", ours="""
              import os
              import tempfile
              before = os.environ.get("SIMPLYDATA_PROGRESS_FILE")   # the test keeps the progress in a
              with tempfile.TemporaryDirectory() as folder:          # folder deleted afterwards
                  os.environ["SIMPLYDATA_PROGRESS_FILE"] = os.path.join(folder, "progress.json")
                  try:
                      sdata.start_30_days()
                      sdata.show_today()
                  finally:
                      os.environ.pop("SIMPLYDATA_PROGRESS_FILE")
                      if before is not None:
                          os.environ["SIMPLYDATA_PROGRESS_FILE"] = before
          """,
          compare="none", note=DAYS_NOTE),
    Entry(word="sdata.show_answers", ours="sdata.show_answers(5)", compare="none",
          note="simplydata's own: the answers are written in simplydata (learn_days.py) and printed in plain "
               "Python; nothing is computed."),
    Entry(word="sdata.go_to_next_day", ours="""
              import os
              import tempfile
              before = os.environ.get("SIMPLYDATA_PROGRESS_FILE")   # the test keeps the progress in a
              with tempfile.TemporaryDirectory() as folder:          # folder deleted afterwards
                  os.environ["SIMPLYDATA_PROGRESS_FILE"] = os.path.join(folder, "progress.json")
                  try:
                      sdata.start_30_days()
                      sdata.go_to_next_day()
                  finally:
                      os.environ.pop("SIMPLYDATA_PROGRESS_FILE")
                      if before is not None:
                          os.environ["SIMPLYDATA_PROGRESS_FILE"] = before
          """,
          compare="none", note=DAYS_NOTE),
]
