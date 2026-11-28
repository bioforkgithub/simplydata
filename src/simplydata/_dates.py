"""sdata.make_run_of_dates(...): a table of regular dates, and the date steps that add_missing_dates uses.

Glue on pandas dates: pandas Timestamp and DateOffset make each date. Month steps are counted from
the first date, so a run from the 31st stays on the 31st, or the month's last day when the month is
shorter (2026-01-31, 2026-02-28, 2026-03-31), as Polars date_range(interval="1mo") does. R's
seq(as.Date("2026-01-31"), by = "month", length.out = 3) overflows into March instead (2026-03-03).
"""

from __future__ import annotations

import re

from ._errors import SimplydataError, choice_error, friendly

UNITS = {"second": "seconds", "minute": "minutes", "hour": "hours", "day": "days", "week": "weeks",
         "month": "months", "quarter": "quarters", "year": "years"}
PLURALS = {plural: single for single, plural in UNITS.items()}
EXAMPLE = 'sdata.make_run_of_dates("2026-01-01", to="2026-12-31", every="day")'
MAX_DATES = 10_000_000


def read_every(every, step_name="dates"):
    """every="day", "2 weeks", "15 minutes" -> (count, unit) with unit one of UNITS."""
    if not isinstance(every, str) or not every.strip():
        raise SimplydataError(f'{step_name}() needs every= as a word such as "day", "month" or "15 minutes".')
    text = every.strip().lower()
    found = re.fullmatch(r"(\d+)\s*([a-z]+)", text)
    count, word = (int(found.group(1)), found.group(2)) if found else (1, text)
    word = PLURALS.get(word, word)
    if word not in UNITS or count < 1:
        raise choice_error(step_name, "every", every, list(UNITS) + ["15 minutes", "2 weeks"])
    return count, word


def every_words(count, unit) -> str:
    return unit if count == 1 else f"{count} {UNITS[unit]}"


def step_after(start, count, unit, k, month_end=False):
    """The k-th date after start (k = 0 gives start), counting calendar months from start. month_end=True
    keeps to the last day of each month (pandas MonthEnd: 2023-04-30, 2023-05-31, 2023-06-30), for runs of
    month-end dates; days and weeks are steps on the calendar (pandas DateOffset), so a date with a time
    zone keeps its clock time across a summer-time change."""
    import pandas as pd

    if unit in ("month", "quarter", "year"):
        months = count * k * {"month": 1, "quarter": 3, "year": 12}[unit]
        if month_end and months:
            return start + pd.offsets.MonthEnd(months)
        return start + pd.DateOffset(months=months)
    if unit in ("day", "week"):
        return start + pd.DateOffset(days=count * k * (7 if unit == "week" else 1))
    size = {"second": pd.Timedelta(seconds=1), "minute": pd.Timedelta(minutes=1), "hour": pd.Timedelta(hours=1)}[unit]
    return start + size * (count * k)


def all_month_ends(stamps) -> bool:
    """True when every date is the last day of its month (2023-02-28, 2023-03-31, ...)."""
    import pandas as pd

    return bool(len(stamps)) and bool(pd.DatetimeIndex(stamps).is_month_end.all())


def date_steps(start, count, unit, how_many=None, to=None, month_end=False):
    """A list of pandas Timestamps from start, every `count unit`, how_many of them or up to `to`."""
    if how_many is not None:
        return [step_after(start, count, unit, k, month_end) for k in range(how_many)]
    out, k = [], 0
    while True:
        value = step_after(start, count, unit, k, month_end)
        if value > to:
            return out
        out.append(value)
        k += 1
        if k > MAX_DATES:
            raise SimplydataError(f"That would be more than {MAX_DATES:,} dates; choose a longer step.")


def read_date(value, name, step_name="dates"):
    import pandas as pd

    try:
        stamp = pd.Timestamp(value)
    except (ValueError, TypeError):
        stamp = None
    if stamp is None or pd.isna(stamp):
        raise SimplydataError(f'{step_name}() needs {name}= as a date such as "2026-01-01" (year-month-day).\n'
                              f"For example, {EXAMPLE}")
    return stamp


def _shown(stamp) -> str:
    return str(stamp.date()) if (stamp.hour, stamp.minute, stamp.second) == (0, 0, 0) else str(stamp)


WORKING_DAY_WORDS = ("working day", "working days", "business day", "business days", "weekday", "weekdays")


def _working_days_run(first, to, how_many, fast):
    """make_run_of_dates(every="working day"): Monday to Friday, as pandas bdate_range (a first date on a weekend
    starts on the Monday after)."""
    import pandas as pd

    from .table import Table

    if (to is None) == (how_many is None):
        raise SimplydataError("make_run_of_dates() needs either to= (the last date) or how_many= (how many dates), not "
                              f"{'both' if to is not None else 'neither'}.\nFor example, {EXAMPLE}")
    if how_many is not None:
        if isinstance(how_many, bool) or not isinstance(how_many, int) or not 1 <= how_many <= MAX_DATES:
            raise SimplydataError("make_run_of_dates() needs how_many= as a whole number of at least 1, such as "
                                  "how_many=24.")
        made = pd.bdate_range(start=first, periods=how_many)  # pandas bdate_range
    else:
        last = read_date(to, "to")
        if last < first:
            raise SimplydataError(f"to= ({_shown(last)}) comes before the first date ({_shown(first)}).")
        made = pd.bdate_range(start=first, end=last)  # pandas bdate_range: Monday to Friday
    if not len(made):
        raise SimplydataError("There is no working day (Monday to Friday) between those dates.")
    frame = pd.DataFrame({"date": pd.DatetimeIndex(made)})
    print(f"{len(made)} working day{'s' if len(made) != 1 else ''} (Monday to Friday) from {_shown(made[0])} to "
          f"{_shown(made[-1])}.")
    if fast:
        import polars as pl

        return Table(pl.from_pandas(frame))
    return Table(frame)


@friendly
def make_run_of_dates(start=None, to=None, every="day", how_many=None, fast=False):
    """A table with one column, "date": regular dates from start, every day (or week, month ...).

    sdata.make_run_of_dates("2026-01-01", to="2026-12-31", every="day")
    Give to= (the last date, included when a step lands on it) or how_many= (how many dates):
    sdata.make_run_of_dates("2026-01", how_many=24, every="month"). every= is "second", "minute", "hour", "day",
    "week", "month", "quarter" or "year", or a count and a unit such as "15 minutes" or "2 weeks".
    Month steps are counted from the first date: from the 31st the dates stay on the 31st, or on the
    month's last day when the month is shorter (2026-01-31, 2026-02-28, 2026-03-31), as pandas
    DateOffset and Polars "1mo"; R's seq(by = "month") overflows into the next month instead. For
    other steps the dates are those of R seq(as.Date(start), as.Date(to), by = "day"). fast=True gives a
    Polars table. The table joins with others (join_with) and charts like any table.
    every="working day" gives the days from Monday to Friday only (pandas bdate_range, NumPy busday_offset;
    no public holidays are left out):
    sdata.make_run_of_dates("2026-12-01", to="2026-12-31", every="working day")
    """
    import pandas as pd

    from .table import Table

    if start is None:
        raise SimplydataError(f"make_run_of_dates() needs a first date.\nFor example, {EXAMPLE}")
    first = read_date(start, "start")
    if isinstance(every, str) and every.strip().lower() in WORKING_DAY_WORDS:  # families for 100 %, batches 1-2
        return _working_days_run(first, to, how_many, fast)
    count, unit = read_every(every)
    if (to is None) == (how_many is None):
        raise SimplydataError(f"make_run_of_dates() needs either to= (the last date) or how_many= (how many dates), not "
                              f"{'both' if to is not None else 'neither'}.\nFor example, {EXAMPLE}")
    if how_many is not None:
        if isinstance(how_many, bool) or not isinstance(how_many, int) or not 1 <= how_many <= MAX_DATES:
            raise SimplydataError("make_run_of_dates() needs how_many= as a whole number of at least 1, such as how_many=24.")
        made = date_steps(first, count, unit, how_many=how_many)
    else:
        last = read_date(to, "to")
        if last < first:
            raise SimplydataError(f"to= ({_shown(last)}) comes before the first date ({_shown(first)}).")
        made = date_steps(first, count, unit, to=last)
    frame = pd.DataFrame({"date": pd.DatetimeIndex(made)})
    print(f"{len(made)} date{'s' if len(made) != 1 else ''} from {_shown(made[0])} to {_shown(made[-1])}, one every "
          f"{every_words(count, unit)}.")
    if fast:
        import polars as pl

        return Table(pl.from_pandas(frame))
    return Table(frame)
