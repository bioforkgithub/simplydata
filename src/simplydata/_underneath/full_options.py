"""Families for 100 %, batches 1-2 (approved by Manish 2026-11-28): the new options and values of existing words for the
pandas and Polars gaps (plan section 2.1), and the seaborn.objects mark and moves (section 2.5)."""

from . import Entry

SAID = "simplydata also says in a sentence what changed, and keeps the table before the step (undo)."
LOOK = "simplydata also sets its own look (colours, fonts, frame)."

ENTRIES = [
    # ---------------------------------------------------------------- find_summary_of
    Entry(
        word="table.find_summary_of",
        option='show="product"',
        data="weather",
        ours="""
            table = sdata.get_example("weather")
            table.find_summary_of("rain", show=["product"], for_each_group_in="city")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("weather.csv")
                # find_summary_of("rain", show=["product"], for_each_group_in="city")
                found = df.groupby("city")["rain"].apply(lambda r: r.astype(float).prod())   # (1)
                found = found.rename("product").reset_index()
                found.insert(0, "column", "rain")
                found
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("weather.csv")
                # find_summary_of("rain", show=["product"], for_each_group_in="city")
                df.group_by("city").agg(pl.lit("rain").alias("column"),
                                        pl.col("rain").cast(pl.Float64).product().alias("product")).sort(
                    "city").select("column", "city", "product")                              # (1)
            """,
        },
        compare="table",
        tolerance=1e-12,
        choices=("in decimals, so a product of whole numbers never wraps round (pandas prod() of int64 would); empty "
                 "cells are left out (pandas prod() and Polars product() skip them).",),
        also="The product of many values gets big fast: entropy= and the geometric mean are often what is wanted.",
    ),
    Entry(
        word="table.find_summary_of",
        option='show="entropy"',
        data="weather",
        ours="""
            table = sdata.get_example("weather")
            table.find_summary_of("rain", show=["entropy"], for_each_group_in="city")
        """,
        code={
            "Polars": """
                import polars as pl
                df = pl.read_csv("weather.csv")
                # find_summary_of("rain", show=["entropy"], for_each_group_in="city")
                df.group_by("city").agg(pl.lit("rain").alias("column"),
                                        pl.col("rain").drop_nulls().entropy().alias("entropy")).sort(
                    "city").select("column", "city", "entropy")                              # (1)
            """,
        },
        compare="table",
        tolerance=1e-12,
        choices=("the values are shared out to 1 (each value over the total) and the log is the natural log: Polars "
                 "entropy(base=e, normalize=True) and SciPy entropy, which simplydata calls.",),
        also="Negative values give an empty cell, with a note (a share cannot be below 0).",
    ),
    Entry(
        word="table.find_summary_of",
        option='show="joined text"',
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_rows_where("subject", is_equal_to="Maths")
            table.find_summary_of("name", show=["joined text"], separator=", ", for_each_group_in="class")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                df = df[df["subject"] == "Maths"]
                # find_summary_of("name", show=["joined text"], separator=", ", for_each_group_in="class")
                found = df.groupby("class")["name"].agg(lambda s: ", ".join(s.dropna().astype(str)))   # (1)
                found = found.rename("joined text").reset_index()
                found.insert(0, "column", "name")
                found
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv").filter(pl.col("subject") == "Maths")
                # find_summary_of("name", show=["joined text"], separator=", ", for_each_group_in="class")
                df.group_by("class", maintain_order=True).agg(
                    pl.col("name").drop_nulls().str.join(", ").alias("joined text")).sort("class").select(
                    pl.lit("name").alias("column"), "class", "joined text")                   # (1)
            """,
        },
        compare="table",
        choices=("the texts of each group in the order of the rows, empty cells left out, \"; \" between them unless "
                 "separator= says otherwise.",),
        also="It is the mirror of split_into_rows, which makes one row for each piece again.",
    ),
    Entry(
        word="table.find_summary_of",
        option="show={column: measures}",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.find_summary_of(show={"marks": ["average", "count"], "hours": ["total"]}, for_each_group_in="class")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # find_summary_of(show={"marks": ["average", "count"], "hours": ["total"]}, for_each_group_in="class")
                df.groupby("class").agg(**{"marks average": ("marks", "mean"), "marks count": ("marks", "count"),
                                           "hours total": ("hours", "sum")}).reset_index()   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("marks.csv")
                # find_summary_of(show={"marks": ["average", "count"], "hours": ["total"]}, for_each_group_in="class")
                df.group_by("class").agg(pl.col("marks").mean().alias("marks average"),
                                         pl.col("marks").count().alias("marks count"),
                                         pl.col("hours").sum().alias("hours total")).sort("class")   # (1)
            """,
        },
        compare="table",
        tolerance=1e-12,
        choices=("one row for each group, the columns named column then measure (pandas named aggregation).",),
        also="Every measure of find_summary_of works here, the percentiles and your own functions too.",
    ),
    # ---------------------------------------------------------------- row after row, rounding, text, dates
    Entry(
        word="table.add_previous_value_column",
        option="rows_ahead=",
        data="weather",
        ours="""
            table = sdata.get_example("weather")
            table.add_previous_value_column("next_month", from_column="temperature", rows_ahead=1,
                                            for_each_group_in="city", sorted_by="month_number")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("weather.csv")
                # add_previous_value_column("next_month", from_column="temperature", rows_ahead=1, ...)
                ordered = df.sort_values("month_number", kind="stable")
                after = ordered.groupby("city")["temperature"].shift(-1)                  # (1)
                df.assign(next_month=after)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("weather.csv")
                # add_previous_value_column("next_month", from_column="temperature", rows_ahead=1, ...)
                after = pl.col("temperature").shift(-1).over("city", order_by="month_number")   # (1)
                df.with_columns(after.alias("next_month"))
            """,
        },
        compare="table",
        choices=("the next value (a lead, R dplyr lead()): the last month of each city has no row after it and stays "
                 "empty.",),
        also=SAID,
    ),
    Entry(
        word="table.round_numbers_in",
        option="significant_figures=",
        data="river",
        ours="""
            table = sdata.get_example("river")
            table.round_numbers_in("nitrate", significant_figures=2)
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("river.csv", parse_dates=["date"])
                # round_numbers_in("nitrate", significant_figures=2)
                from decimal import ROUND_HALF_EVEN, Decimal
                def signif(v):
                    d = Decimal(repr(v))
                    return float(d.quantize(Decimal(1).scaleb(d.adjusted() - 1), rounding=ROUND_HALF_EVEN))
                df.assign(nitrate=[signif(v) if v == v else v for v in df["nitrate"]])   # (1)
            """,
        },
        compare="table",
        choices=("each number as it is written, a half to the even digit, as R signif() (Polars round_sig_figs takes "
                 "a half away from 0: 5.25 would be 5.3).",),
        also=SAID,
    ),
    Entry(
        word="table.keep_rows_where",
        option="time_of_day_between=",
        data="fjord_samples",
        ours="""
            table = sdata.get_example("fjord_samples")
            table.turn_into_dates("sampled_local")
            table.keep_rows_where("sampled_local", time_of_day_between=["09:00", "12:00"])
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("fjord_samples.csv")
                df["sampled_local"] = pd.to_datetime(df["sampled_local"])
                # keep_rows_where("sampled_local", time_of_day_between=["09:00", "12:00"])
                kept = df.set_index("sampled_local", drop=False).between_time("09:00", "12:00")   # (1)
                kept.reset_index(drop=True)
            """,
            "Polars": """
                import datetime
                import polars as pl
                df = pl.read_csv("fjord_samples.csv").with_columns(pl.col("sampled_local").str.to_datetime())
                # keep_rows_where("sampled_local", time_of_day_between=["09:00", "12:00"])
                clock = pl.col("sampled_local").dt.time()
                df.filter(clock.is_between(datetime.time(9), datetime.time(12)))          # (1)
            """,
        },
        compare="table",
        choices=("both clock times included, on any day; a start after the end goes past midnight, as pandas "
                 "between_time.",),
        also="[\"08:00\", \"08:00\"] keeps one clock time (pandas at_time). " + SAID,
    ),
    Entry(
        word="table.add_column_with_part_of_text",
        option="every_match=",
        data="fjord_samples",
        ours="""
            table = sdata.get_example("fjord_samples")
            table.add_column_with_part_of_text("people", from_column="crew", matches_pattern="[A-Z]{2}",
                                               every_match=True)
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("fjord_samples.csv", parse_dates=["sampled_local"])
                # add_column_with_part_of_text("people", from_column="crew", matches_pattern=..., every_match=True)
                found = df["crew"].str.findall("[A-Z]{2}")                                 # (1)
                df.assign(people=found.map(lambda v: ";".join(v) if isinstance(v, list) and v else None))
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("fjord_samples.csv", try_parse_dates=True)
                # add_column_with_part_of_text("people", from_column="crew", matches_pattern=..., every_match=True)
                found = pl.col("crew").str.extract_all("[A-Z]{2}").list.join(";")           # (1)
                df.with_columns(pl.when(found != "").then(found).alias("people"))
            """,
        },
        compare="table",
        choices=("every piece that fits, joined with \";\" (separator= for another mark); a text with none gives an "
                 "empty cell.",),
        also="split_into_rows then gives one row for each piece. " + SAID,
    ),
    Entry(
        word="table.add_column_with_part_of_text",
        option="position_of=",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.add_column_with_part_of_text("where_a", from_column="name", position_of="a")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("marks.csv")
                # add_column_with_part_of_text("where_a", from_column="name", position_of="a")
                found = df["name"].str.find("a")                                          # (1)
                df.assign(where_a=(found + 1).where(found >= 0))
            """,
        },
        compare="table",
        choices=("counted from 1, and an empty cell where it is not found (pandas find() gives -1); characters are "
                 "counted on both engines (Polars str.find counts bytes).",),
        also=SAID,
    ),
    Entry(
        word="table.add_column_with_part_of_date",
        option='part="is month start"',
        data="shop",
        ours="""
            table = sdata.get_example("shop")
            table.turn_into_dates("date")
            table.add_column_with_part_of_date("first_day", from_column="date", part="is month start")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("shop.csv", parse_dates=["date"])
                # add_column_with_part_of_date("first_day", from_column="date", part="is month start")
                df.assign(first_day=df["date"].dt.is_month_start)                        # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("shop.csv", try_parse_dates=True)
                # add_column_with_part_of_date("first_day", from_column="date", part="is month start")
                df.with_columns((pl.col("date").dt.day() == 1).alias("first_day"))       # (1)
            """,
        },
        compare="table",
        choices=("worked out by Polars on both engines; an empty date gives an empty cell (pandas gives False).",),
        also="\"is quarter start\", \"is quarter end\", \"is year start\", \"is year end\" and \"month end\" (the date "
             "of the month's last day, Polars dt.month_end()) work the same way. " + SAID,
    ),
    Entry(
        word="table.add_column_with_part_of_date",
        option='part="is working day"',
        data="shop",
        ours="""
            table = sdata.get_example("shop")
            table.turn_into_dates("date")
            table.add_column_with_part_of_date("working", from_column="date", part="is working day")
        """,
        code={
            "NumPy": """
                import numpy as np
                import pandas as pd
                df = pd.read_csv("shop.csv", parse_dates=["date"])
                # add_column_with_part_of_date("working", from_column="date", part="is working day")
                df.assign(working=np.is_busday(df["date"].values.astype("datetime64[D]")))   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("shop.csv", try_parse_dates=True)
                # add_column_with_part_of_date("working", from_column="date", part="is working day")
                df.with_columns(pl.col("date").dt.is_business_day().alias("working"))      # (1)
            """,
        },
        compare="table",
        choices=("Monday to Friday; no public holidays are left out.",),
        also=SAID,
    ),
    Entry(
        word="table.add_column_with_part_of_date",
        option='part="unix time"',
        data="shop",
        ours="""
            table = sdata.get_example("shop")
            table.turn_into_dates("date")
            table.add_column_with_part_of_date("seconds", from_column="date", part="unix time")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("shop.csv", parse_dates=["date"])
                # add_column_with_part_of_date("seconds", from_column="date", part="unix time")
                seconds = (df["date"] - pd.Timestamp("1970-01-01")) // pd.Timedelta(seconds=1)   # (1)
                df.assign(seconds=seconds)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("shop.csv", try_parse_dates=True)
                # add_column_with_part_of_date("seconds", from_column="date", part="unix time")
                df.with_columns(pl.col("date").dt.epoch("s").alias("seconds"))            # (1)
            """,
        },
        compare="table",
        choices=("whole seconds since 1 January 1970 on the UTC clock (Polars dt.epoch(\"s\")).",),
        also="turn_into_dates(from_unix_seconds=True) turns such seconds back into dates. " + SAID,
    ),
    Entry(
        word="table.turn_into_dates",
        option="from_unix_seconds=",
        ours="""
            table = sdata.table({"logged": [1764288000, 1764291600.5, 0]})
            table.turn_into_dates("logged", from_unix_seconds=True)
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.DataFrame({"logged": [1764288000, 1764291600.5, 0]})
                # turn_into_dates("logged", from_unix_seconds=True)
                df.assign(logged=pd.to_datetime(df["logged"], unit="s").dt.as_unit("us"))   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.DataFrame({"logged": [1764288000, 1764291600.5, 0]})
                # turn_into_dates("logged", from_unix_seconds=True)
                micro = (pl.col("logged") * 1_000_000).round(0).cast(pl.Int64)
                df.with_columns(pl.from_epoch(micro, time_unit="us").alias("logged"))      # (1)
            """,
        },
        compare="table",
        choices=("dates and times on the UTC clock, to the microsecond (Polars from_epoch).",),
        also=SAID,
    ),
    Entry(
        word="table.add_column",
        option="floor() ceil() log10() log1p() sign() cbrt()",
        data="weather",
        ours="""
            table = sdata.get_example("weather")
            table.add_column("tens", "floor(rain / 10)")
            table.add_column("log_rain", "log1p(rain)")
        """,
        code={
            "NumPy": """
                import numpy as np
                import pandas as pd
                df = pd.read_csv("weather.csv")
                # add_column("tens", "floor(rain / 10)"); add_column("log_rain", "log1p(rain)")
                df.assign(tens=np.floor(df["rain"] / 10), log_rain=np.log1p(df["rain"]))   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("weather.csv")
                # add_column("tens", "floor(rain / 10)"); add_column("log_rain", "log1p(rain)")
                df.with_columns((pl.col("rain") / 10).floor().alias("tens"),
                                pl.col("rain").log1p().alias("log_rain"))                 # (1)
            """,
        },
        compare="table",
        tolerance=1e-12,
        choices=("worked out with NumPy on both engines; an answer that is not a number gives an empty cell.",),
        also="log10, sign, cbrt and ceil work the same way. " + SAID,
    ),
    Entry(
        word="table.add_column",
        option="add_working_days() count_working_days()",
        data="shop",
        ours="""
            table = sdata.get_example("shop")
            table.turn_into_dates("date")
            table.add_column("reply_by", "add_working_days(date, 10)")
        """,
        code={
            "NumPy": """
                import numpy as np
                import pandas as pd
                df = pd.read_csv("shop.csv", parse_dates=["date"])
                # add_column("reply_by", "add_working_days(date, 10)")
                days = df["date"].values.astype("datetime64[D]")
                df.assign(reply_by=np.busday_offset(days, 10, roll="forward").astype("datetime64[us]"))   # (1)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("shop.csv", try_parse_dates=True)
                # add_column("reply_by", "add_working_days(date, 10)")
                df.with_columns(pl.col("date").dt.add_business_days(10, roll="forward").alias("reply_by"))   # (1)
            """,
        },
        compare="table",
        choices=("a date on a weekend first moves to the Monday (roll=\"forward\"); Monday to Friday, no holidays.",),
        also="count_working_days(start, end) counts them, the end date not counted (NumPy busday_count, Polars "
             "business_day_count). " + SAID,
    ),
    Entry(
        word="sdata.make_run_of_dates",
        option='every="working day"',
        ours="""
            sdata.make_run_of_dates("2026-12-01", to="2026-12-31", every="working day")
        """,
        code={
            "pandas": """
                import pandas as pd
                # make_run_of_dates("2026-12-01", to="2026-12-31", every="working day")
                pd.DataFrame({"date": pd.bdate_range("2026-12-01", "2026-12-31")})        # (1)
            """,
        },
        compare="table",
        choices=("Monday to Friday; no public holidays are left out.",),
        also="how_many= gives that many working days instead of to=.",
    ),
    Entry(
        word="table.add_rolling_column",
        option="with_column=",
        data="weather",
        ours="""
            table = sdata.get_example("weather")
            table.add_rolling_column("link", from_column="temperature", with_column="rain", show="correlation",
                                     window=4, for_each_group_in="city", sorted_by="month_number")
        """,
        code={
            "pandas": """
                import pandas as pd
                df = pd.read_csv("weather.csv")
                # add_rolling_column("link", from_column="temperature", with_column="rain", show="correlation", ...)
                ordered = df.sort_values("month_number", kind="stable")
                link = ordered.groupby("city", group_keys=False).apply(
                    lambda g: g["temperature"].rolling(4).corr(g["rain"]))                # (1)
                df.assign(link=link)
            """,
            "Polars": """
                import polars as pl
                df = pl.read_csv("weather.csv").with_row_index("row")
                # add_rolling_column("link", from_column="temperature", with_column="rain", show="correlation", ...)
                link = pl.rolling_corr("temperature", "rain", window_size=4).over("city", order_by="month_number")
                df.with_columns(link.alias("link")).drop("row")                           # (1)
            """,
        },
        compare="table",
        tolerance=1e-9,
        choices=("the same as from_column=[\"temperature\", \"rain\"]; the first rows of each group are empty until "
                 "the window is full.",),
        also="show=\"covariance\" works the same way (pandas rolling().cov(), Polars rolling_cov). " + SAID,
    ),
    Entry(
        word="table.join_with",
        option="where=",
        data="river",
        ours="""
            table = sdata.get_example("river")
            table.turn_into_dates("date")
            periods = sdata.table({"start": ["2024-01-01", "2024-04-01"], "end": ["2024-02-01", "2024-05-01"],
                                   "period": ["winter", "spring"]})
            periods.turn_into_dates("start")
            periods.turn_into_dates("end")
            table.join_with(periods, where="date >= start and date < end")
        """,
        code={
            "Polars": """
                import polars as pl
                df = pl.read_csv("river.csv", try_parse_dates=True)
                periods = pl.DataFrame({"start": ["2024-01-01", "2024-04-01"], "end": ["2024-02-01", "2024-05-01"],
                                        "period": ["winter", "spring"]}).with_columns(
                    pl.col("start", "end").str.to_datetime())
                # join_with(periods, where="date >= start and date < end")
                pairs = df.join_where(periods, pl.col("date") >= pl.col("start"), pl.col("date") < pl.col("end"))
                pairs.sort(["station", "date"]).select(df.columns + periods.columns)       # (1)
            """,
            "pandas": """
                import pandas as pd
                df = pd.read_csv("river.csv", parse_dates=["date"])
                periods = pd.DataFrame({"start": pd.to_datetime(["2024-01-01", "2024-04-01"]),
                                        "end": pd.to_datetime(["2024-02-01", "2024-05-01"]),
                                        "period": ["winter", "spring"]})
                # join_with(periods, where="date >= start and date < end")
                pairs = df.merge(periods, how="cross")
                pairs[(pairs["date"] >= pairs["start"]) & (pairs["date"] < pairs["end"])].reset_index(drop=True)   # (1)
            """,
        },
        compare="table",
        choices=("the rows keep this table's order, each followed by its partners (Polars join_where gives no order "
                 "of its own, so the Polars box sorts); a row without a partner is left out.",),
        also=SAID,
    ),
    Entry(
        word="table.turn_into_numbers",
        option="show_problems=",
        ours="""
            table = sdata.table({"dose": ["1.5", "<0.5", "n.d.", "2"]})
            table.turn_into_numbers("dose", show_problems=True)
        """,
        compare="none",
        note="simplydata's own look before a step: the filled cells that turn_into_numbers would make empty (what "
             "pandas str.isnumeric() or to_numeric(errors=\"coerce\").isna() find), named with their rows; the table "
             "does not change.",
    ),
    # ---------------------------------------------------------------- seaborn.objects: Path, Shift, Dash
    Entry(
        word="draw_lines",
        option="in_row_order=",
        data="weather",
        ours="""
            chart = sdata.chart(sdata.get_example("weather"))
            chart.draw_lines(x="temperature", y="rain", in_row_order=True)
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import pandas as pd
            import seaborn as sns
            df = pd.read_csv("weather.csv")
            fig, ax = plt.subplots()
            # draw_lines(x="temperature", y="rain", in_row_order=True): seaborn so.Path
            sns.lineplot(df, x="temperature", y="rain", sort=False, estimator=None, errorbar=None, ax=ax)   # (1)
            fig
        """},
        compare="chart",
        check=("lines",),
        choices=("every row, joined in the order of the rows (no average, no sorting by x).",),
        also=LOOK,
    ),
    Entry(
        word="draw_dots",
        option="move_layer_by=",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dots(x="hours", y="marks", move_layer_by=0.5)
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import pandas as pd
            import seaborn as sns
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            # draw_dots(x="hours", y="marks", move_layer_by=0.5): seaborn so.Shift(x=0.5)
            sns.scatterplot(df.assign(hours=df["hours"] + 0.5), x="hours", y="marks", ax=ax)   # (1)
            fig
        """},
        compare="chart",
        check=("dots",),
        choices=("the dots move 0.5 along x; on a group axis each group is 1 wide.",),
        also="draw_lines, draw_all_dots and draw_dashes take move_layer_by= too. " + LOOK,
    ),
    Entry(
        word="draw_dashes",
        data="marks",
        ours="""
            chart = sdata.chart(sdata.get_example("marks"))
            chart.draw_dashes(x="class", y="marks")
        """,
        code={"seaborn": """
            import matplotlib.pyplot as plt
            import pandas as pd
            import seaborn as sns
            from matplotlib.collections import LineCollection
            df = pd.read_csv("marks.csv")
            fig, ax = plt.subplots()
            # draw_dashes(x="class", y="marks"): seaborn so.Dash, each value at its group's place
            sns.stripplot(df, x="class", y="marks", jitter=False, ax=ax)                 # (1)
            dots = list(ax.collections)  # one set of dots for each class, each dot made a dash
            dashes = [[(x - 0.4, y), (x + 0.4, y)] for d in dots for x, y in d.get_offsets()]
            [d.remove() for d in dots]
            ax.add_collection(LineCollection(dashes, linewidths=2))
            fig
        """},
        compare="chart",
        check=("segments",),
        choices=("each dash is 0.8 wide (width=), centred on its group, as so.Dash(width=0.8).",),
        also=LOOK,
    ),
]
