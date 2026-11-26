"""One set of time zone rules for both engines: Polars' own copy of the world time zone data (IANA).

pandas reads the clock of a column with a time zone through Python's zoneinfo, which uses the computer's copy of the
time zone data; Polars carries its own (chrono-tz, the main IANA data). The copies can differ before 1970: Debian and
Ubuntu build Europe/Oslo with Norway's summer time of 1959 to 1965, while the main data (and the tzdata package that
Python uses on Windows) follow Europe/Berlin there. So on Linux the same moment of 1 July 1959 was 00:00 on a pandas
table and 23:00 the day before on a Polars table.

Every date step that reads or writes the clock of a column with a time zone therefore runs on Polars for a pandas
table too (pass-through: pandas -> Polars for that step -> pandas, as round_dates_in did first): local clock times
follow the main world time zone data (IANA), the same on every computer. A moment itself (the instant) never
changes on the way. simplydata does no clock arithmetic of its own (PLAN.md section 7).
"""

from __future__ import annotations

import narwhals as nw

TIME_WITH_OFFSET = "%Y-%m-%d %H:%M:%S%.f%:z"  # Polars dt.to_string: 2024-07-01 23:45:00-04:00


def zone_of(frame, column):
    """The time zone of a column of clock times, or None."""
    dtype = frame.schema[column]
    return dtype.time_zone if dtype == nw.Datetime else None


def on_pandas_with_zone(frame, columns) -> bool:
    """True for a pandas table where one of these columns holds clock times with a time zone."""
    return not frame.implementation.is_polars() and any(zone_of(frame, c) for c in columns)


def as_polars(frame, column):
    """The column as a Polars Series (the same moments)."""
    native = frame[column].to_native()
    if frame.implementation.is_polars():
        return native
    import polars as pl

    return pl.from_pandas(native)


def _back_to_pandas(series, index):
    """A Polars Series as a pandas Series on the table's row index; text stays the table's kind of text."""
    import pandas as pd
    import polars as pl

    out = series.to_pandas()
    if series.dtype == pl.String:
        out = pd.Series(series.to_list(), dtype=pd.Series([""]).dtype, name=series.name)
    out.index = index
    return out


def with_columns(frame, exprs, columns):
    """frame.with_columns(*exprs) for expressions that read the clock of these columns.

    On a pandas table with a time zone in one of the columns, Polars works the expressions out on those columns
    (pass-through) and the results come back as pandas columns; otherwise narwhals runs them on the table's own
    engine."""
    exprs = list(exprs)
    columns = list(dict.fromkeys(columns))
    if not on_pandas_with_zone(frame, columns):
        return frame.with_columns(*exprs)
    import polars as pl

    native = frame.select(*columns).to_native()
    worked = nw.from_native(pl.from_pandas(native), eager_only=True).select(*exprs).to_native()
    return frame.with_columns(*(nw.from_native(_back_to_pandas(worked[name], native.index), series_only=True)
                                .alias(name) for name in worked.columns))


def select(frame, exprs, columns):
    """frame.select(*exprs), with the same rule as with_columns (a small frame, such as a minimum and a maximum)."""
    exprs = list(exprs)
    columns = list(dict.fromkeys(columns))
    if not on_pandas_with_zone(frame, columns):
        return frame.select(*exprs)
    import polars as pl

    native = frame.select(*columns).to_native()
    return nw.from_native(pl.from_pandas(native), eager_only=True).select(*exprs)


def values(frame, column) -> list:
    """The cells of a column as Python values, read on Polars' clock for a column with a time zone."""
    if zone_of(frame, column) and not frame.implementation.is_polars():
        return as_polars(frame, column).to_list()
    return frame[column].to_list()


def texts(frame, column) -> list:
    """The cells of a column with a time zone as text with their UTC offset (2024-07-01 23:45:00-04:00), written by
    Polars dt.to_string on both engines; empty cells are None."""
    return as_polars(frame, column).dt.to_string(TIME_WITH_OFFSET).to_list()


def text_of(frame, column, row: int) -> str:
    """One cell as text, as values() and texts() read it."""
    if zone_of(frame, column):
        return texts(frame, column)[row]
    return str(frame[column].item(row))


def wall_clock(frame, column):
    """A column with a time zone as clock times without the zone (Polars dt.replace_time_zone(None)), as pandas."""
    series = as_polars(frame, column).dt.replace_time_zone(None)
    native = frame[column].to_native()
    if frame.implementation.is_polars():
        return series.to_pandas()
    out = series.to_pandas()
    out.index = native.index
    return out


def place_on_clock(series, zone, ambiguous="raise", non_existent="raise"):
    """Clock times without a zone (a pandas Series) placed in a time zone by Polars dt.replace_time_zone, as pandas
    (the same index)."""
    import polars as pl

    placed = pl.from_pandas(series).dt.replace_time_zone(zone, ambiguous=ambiguous, non_existent=non_existent)
    out = placed.to_pandas()
    out.index = series.index
    return out


def say(series) -> list:
    """Clock times with a time zone written for people, as show_steps() and describe_columns() write a date: the day
    alone at midnight (2024-07-01), otherwise the time with its UTC offset (2024-07-01 23:45:00-04:00); written by
    Polars dt.to_string on the column's own clock. series is a Polars Series; empty cells give None."""
    import polars as pl

    d = pl.col("d")
    midnight = (d.dt.hour() == 0) & (d.dt.minute() == 0) & (d.dt.second() == 0)
    text = pl.when(midnight).then(d.dt.to_string("%Y-%m-%d")).otherwise(d.dt.to_string(TIME_WITH_OFFSET))
    return pl.DataFrame({"d": series}).select(text.alias("d"))["d"].to_list()


def between_on_clock(between, zone, utc: bool):
    """between= dates (pandas Timestamps) for a column with a time zone: as clock times of the zone without the zone
    (utc=False), or as moments on the UTC clock (utc=True); placed by Polars. None stays None."""
    if between is None:
        return None
    import pandas as pd
    import polars as pl

    out = []
    for stamp in between:
        if stamp.tzinfo is not None:  # a moment, written with its own offset
            moment = pl.Series([stamp.tz_convert("UTC").tz_localize(None).to_pydatetime()]).dt.replace_time_zone("UTC")
            placed = moment if utc else moment.dt.convert_time_zone(zone).dt.replace_time_zone(None)
        elif utc:
            placed = pl.Series([stamp.to_pydatetime()]).dt.replace_time_zone(
                zone, ambiguous="earliest", non_existent="null").dt.convert_time_zone("UTC")
        else:
            out.append(stamp)
            continue
        out.append(pd.Timestamp(placed.to_pandas().iloc[0]))
    return out
