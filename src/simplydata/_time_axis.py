"""The time axis of a series: order, spacing, gaps and the time between readings.

Glue for the words on things that change over time (spectrum_of, check_steady, ...). It sorts a
column by sorted_by=, splits it with for_each=, works out the step between readings (numbers, or
dates in days, with calendar months, quarters and years counted as regular), and gives friendly
errors for gaps and empty cells. It computes no statistics.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import narwhals as nw
import numpy as np

from ._errors import SimplydataError

CALENDAR = (("month", 28, 31), ("quarter", 89, 92), ("year", 365, 366))  # step name, shortest, longest (days)
DAY_SECONDS = 86400.0


@dataclass
class TimeSeries:
    """One series: its group label, values in time order, times and the step between readings."""

    label: str | None
    values: np.ndarray
    times: np.ndarray | None  # floats in `unit`, or None when the rows are taken in table order
    step: float  # the time between readings, in `unit` (1 for table order and calendar steps)
    unit: str  # "rows", "days", "seconds", "months", "quarters", "years", or the sorted_by column's name
    regular: bool
    gaps: list = field(default_factory=list)  # (time before, time after) for each gap
    shown_times: list | None = None  # the sorted_by values as written, for sentences
    rows: np.ndarray | None = None  # the table rows these values come from, in time order

    def describe(self) -> str:
        n = len(self.values)
        if self.times is None:
            return f"{n} readings in table order"
        if self.unit in ("months", "quarters", "years"):
            return f"one reading every {self.unit[:-1]} ({n} readings)"
        if self.unit in ("days", "seconds"):
            return f"one reading every {_num(self.step)} {self.unit} ({n} readings)"
        return f'one reading every {_num(self.step)} in "{self.unit}" ({n} readings)'


def _num(x) -> str:
    x = float(x)
    return f"{x:g}" if abs(x) >= 1e-4 or x == 0 else f"{x:.3g}"


def _calendar_step(days: np.ndarray):
    """'month', 'quarter' or 'year' when every step is one calendar step long, else None."""
    for name, low, high in CALENDAR:
        if len(days) and np.all((days >= low) & (days <= high)):
            return name
    return None


def series_of(table, column, sorted_by=None, for_each=None, step_name="this step", example=""):
    """The column as one TimeSeries per group, sorted by sorted_by (empty cells kept as NaN)."""
    frame = table._frame
    table._need_columns(column)
    if not frame.schema[column].is_numeric():
        raise SimplydataError(f'{step_name}() needs "{column}" to hold numbers.\nFor example, {example}')
    groups = table._group_columns(step_name, for_each, [column]) if for_each is not None else []
    if sorted_by is not None:
        if not isinstance(sorted_by, str):
            raise SimplydataError(f"{step_name}() needs sorted_by= as one column name in quotes.\nFor example, {example}")
        table._need_columns(sorted_by)
        if sorted_by == column or sorted_by in groups:
            raise SimplydataError(f'"{sorted_by}" cannot be both sorted_by= and the column or for_each=.')
    values = frame[column].cast(nw.Float64).to_numpy().astype(float)
    keys = [tuple(r) for r in frame.select(groups).rows()] if groups else [()] * len(values)
    times, kind = None, None
    if sorted_by is not None:
        dtype = frame.schema[sorted_by]
        raw = frame[sorted_by].to_numpy()
        if dtype.is_temporal():
            kind = "dates"
            times = np.asarray(raw, dtype="datetime64[ns]")
        elif dtype.is_numeric():
            kind = "numbers"
            times = np.asarray(raw, dtype=float)
        else:
            raise SimplydataError(f'sorted_by="{sorted_by}" should hold numbers or dates (make dates first: '
                                  f'table.make_dates("{sorted_by}")).')
        if np.any(np.isnat(times) if kind == "dates" else np.isnan(times)):
            raise SimplydataError(f'"{sorted_by}" has empty cells, so the order of those rows is not known. '
                                  "Fill or remove them first.")
    order: dict = {}
    for i, key in enumerate(keys):
        order.setdefault(key, []).append(i)
    out = []
    for key in sorted(order, key=lambda k: tuple((str(type(v)), v) for v in k)):
        rows = np.asarray(order[key])
        label = " / ".join(str(v) for v in key) if groups else None
        if times is None:
            out.append(TimeSeries(label, values[rows], None, 1.0, "rows", True, rows=rows))
            continue
        t = times[rows]
        sort = np.argsort(t, kind="stable")
        rows, t = rows[sort], t[sort]
        shown = [str(v)[:10] if kind == "dates" else _num(v) for v in t]
        if (np.diff(t.astype("int64") if kind == "dates" else t) == 0).any():
            where = f" for {label}" if label else ""
            raise SimplydataError(f'Some rows have the same "{sorted_by}"{where}, so the order is not clear. '
                                  "Summarise them first, for example with table.average_of(..., for_each=...).")
        if kind == "dates":
            days = (t - t[0]).astype("timedelta64[ns]").astype(np.int64) / (DAY_SECONDS * 1e9)
            gaps_days = np.diff(days)
            calendar = _calendar_step(gaps_days)
            if calendar:
                out.append(TimeSeries(label, values[rows], np.arange(len(t), dtype=float), 1.0, calendar + "s", True,
                                      shown_times=shown, rows=rows))
                continue
            unit, scale = ("days", 1.0) if np.min(gaps_days, initial=1) >= 1 else ("seconds", DAY_SECONDS)
            numbers = days * scale
        else:
            unit, numbers = sorted_by, t
        diffs = np.diff(numbers)
        step = float(np.median(diffs)) if len(diffs) else 1.0
        regular = bool(len(diffs) == 0 or np.allclose(diffs, step, rtol=1e-6, atol=0))
        gaps = [(shown[i], shown[i + 1]) for i in np.flatnonzero(~np.isclose(diffs, step, rtol=1e-6, atol=0))]
        out.append(TimeSeries(label, values[rows], numbers, step, unit, regular, gaps, shown, rows=rows))
    return out


def need_regular(series: TimeSeries, step_name: str, sorted_by: str | None = None) -> None:
    """Friendly error when the readings are not evenly spaced."""
    if series.regular:
        return
    where = f" for {series.label}" if series.label else ""
    first = series.gaps[0] if series.gaps else ("?", "?")
    raise SimplydataError(
        f'{step_name}() needs evenly spaced readings, but "{sorted_by}" has {len(series.gaps)} uneven step'
        f'{"" if len(series.gaps) == 1 else "s"}{where} (the first between {first[0]} and {first[1]}). '
        "Add the missing times and fill them first, or (for spectra) use method=\"lomb-scargle\", which is made "
        "for uneven times.")


def need_filled(series: TimeSeries, column: str, step_name: str, sorted_by: str | None = None) -> None:
    """Friendly error when the series has empty cells (they break the even steps)."""
    empty = int(np.isnan(series.values).sum())
    if not empty:
        return
    where = f" for {series.label}" if series.label else ""
    order = f', sorted_by="{sorted_by}"' if sorted_by else ""
    raise SimplydataError(
        f'{step_name}() needs a value at every step, but "{column}" has {empty} empty cell'
        f'{"" if empty == 1 else "s"}{where}. Fill them first, for example: '
        f'table.fill_empty_cells("{column}", with_the="line between neighbours"{order}).')


def read_time_step(time_step=None, sampling_rate=None, fs=None, remembered=None, step_name="this step"):
    """(time step, words) from time_step=, or sampling_rate= / fs= (readings per unit of time)."""
    given = [(n, v) for n, v in (("time_step", time_step), ("sampling_rate", sampling_rate), ("fs", fs))
             if v is not None]
    if len(given) > 1:
        raise SimplydataError(f"{step_name}() needs only one of time_step=, sampling_rate= or fs=.")
    if not given:
        if remembered is not None:
            return float(remembered), f"time step {_num(remembered)} (remembered from the numbers)"
        return 1.0, "time step 1 (frequencies in cycles per reading)"
    name, value = given[0]
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)) or not \
            math.isfinite(value) or value <= 0:
        raise SimplydataError(f"{step_name}() needs {name}= as a number above 0, such as time_step=0.01.")
    step = float(value) if name == "time_step" else 1.0 / float(value)
    return step, f"time step {_num(step)} ({_num(1 / step)} readings per unit of time)"


def future_times(table, series: TimeSeries, sorted_by, steps: int, start_after: int | None = None) -> list:
    """The sorted_by column carried on for `steps` readings after the last one (or after reading number
    start_after): months stay months (the same day of the month, or the month's last day), days and
    numbers go on by the step. Plain glue on pandas dates."""
    import pandas as pd

    position = len(series.values) - 1 if start_after is None else start_after - 1
    raw = table._frame[sorted_by].to_numpy()[series.rows[position]]
    ahead = range(1, steps + 1)
    if series.unit in ("months", "quarters", "years"):
        months = {"months": 1, "quarters": 3, "years": 12}[series.unit]
        last = pd.Timestamp(raw)
        return [(last + pd.DateOffset(months=months * k)).to_pydatetime() for k in ahead]
    if series.unit in ("days", "seconds"):
        last = pd.Timestamp(raw)
        size = pd.Timedelta(days=series.step) if series.unit == "days" else pd.Timedelta(seconds=series.step)
        return [(last + size * k).to_pydatetime() for k in ahead]
    return [float(raw) + series.step * k for k in ahead]
