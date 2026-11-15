"""Table words for regular time steps: table.add_missing_dates(...) and table.add_smoothed_column(...).

add_missing_dates is glue on pandas dates (simplydata._dates): it lists the dates a regular run
would have and adds a row for each one that is not there (as pandas reindex / Polars upsample).
add_smoothed_column hands each series to simplydata._smoothing (SciPy, statsmodels, pandas, or R
runmed for the running median).
"""

from __future__ import annotations

import narwhals as nw
import numpy as np

from .. import _dates
from .._errors import SimplydataError, friendly

STEP_NAMES = ((1 / 86400, "second"), (1 / 1440, "minute"), (1 / 24, "hour"), (1, "day"), (7, "week"))


def _common_every(days: np.ndarray):
    """The most common step between dates, as (count, unit)."""
    steps = np.round(days, 9)
    values, counts = np.unique(steps[steps > 0], return_counts=True)
    if not len(values):
        raise SimplydataError("add_missing_dates() needs at least two different dates to see the step; give every=.")
    step = float(values[np.argmax(counts)])
    if 28 <= step <= 31:
        return 1, "month"
    if 89 <= step <= 92:
        return 1, "quarter"
    if 365 <= step <= 366:
        return 1, "year"
    for size, unit in reversed(STEP_NAMES):
        count = step / size
        if count >= 1 and abs(count - round(count)) < 1e-6:
            return int(round(count)), unit
    raise SimplydataError("The dates have no regular step that simplydata can name; give every=, such as "
                          'every="day".')


class TimeStepWords:
    @friendly
    def add_missing_dates(self, column=None, every=None, for_each=None, between=None):
        """Add a row for every date that is missing from a regular run of dates (other cells empty).

        table.add_missing_dates("date", every="day", for_each="station")   (with sdata.example("river"))
        every= is the step ("day", "week", "month", "hour", "15 minutes" ...); without it, the most
        common step between the dates, printed. for_each= fills each group's own run (the group's
        value is copied into the new rows). between=["2024-01-01", "2025-12-31"] also adds rows before
        the first and after the last date. The new rows have empty cells: fill them next with
        table.fill_empty_cells(..., with_the="line between neighbours", sorted_by=..., for_each=...).
        The table comes back sorted by the groups and the dates. As pandas reindex / Polars upsample;
        R merge(data.frame(date = seq(...)), x, all.x = TRUE). Undo with table.undo().
        """
        import pandas as pd

        step_name = "add_missing_dates"
        example = 'table.add_missing_dates("date", every="day", for_each="station")'
        self._need_name(step_name, "the date column", column, example)
        self._need_columns(column)
        if not self._frame.schema[column].is_temporal():
            raise SimplydataError(f'"{column}" does not hold dates. Make dates first: table.make_dates("{column}").')
        groups = self._group_columns(step_name, for_each, [column]) if for_each is not None else []
        native = self._frame.to_pandas()
        if native[column].isna().any():
            raise SimplydataError(f'"{column}" has empty cells; remove those rows or fill them first.')
        given = None if every is None else _dates.read_every(every, step_name)
        if between is not None:
            if not (isinstance(between, (list, tuple)) and len(between) == 2):
                raise SimplydataError('between= needs the first and last date, such as between=["2024-01-01", '
                                      '"2025-12-31"].')
            low, high = (_dates.read_date(v, "between", step_name) for v in between)
            if high < low:
                raise SimplydataError("between= needs the earlier date first.")
        parts = native.groupby(groups, sort=True, dropna=False) if groups else [((), native)]
        new_rows, counts, shown_every = [], [], None
        for key, part in parts:
            key = key if isinstance(key, tuple) else (key,)
            when = pd.DatetimeIndex(part[column]).sort_values()
            label = " / ".join(map(str, key)) if groups else ""
            if when.duplicated().any():
                twice = when[when.duplicated()][0]
                where = f" for {label}" if label else ""
                raise SimplydataError(f'{int(when.duplicated().sum())} rows have the same date{where}, such as '
                                      f"{_dates._shown(twice)}. Remove the repeats (remove_duplicate_rows) or "
                                      "summarise them first.")
            count, unit = given or _common_every(np.asarray((when[1:] - when[:-1]).total_seconds(), dtype=float) / 86400)
            shown_every = (count, unit)
            first, last = (when[0], when[-1]) if between is None else (min(low, when[0]), max(high, when[-1]))
            if between is not None and low < when[0]:
                # step back from the first reading so the run keeps its rhythm
                k = 0
                while _dates.step_after(when[0], count, unit, k - 1) >= low:
                    k -= 1
                first = _dates.step_after(when[0], count, unit, k)
            run = pd.DatetimeIndex(_dates.date_steps(first, count, unit, to=last))
            if between is not None:
                run = run[(run >= low) & (run <= high)].union(when)
            off_step = when.difference(run)
            if len(off_step):
                raise SimplydataError(f'"{column}" has dates that do not fall on the every="{_dates.every_words(count, unit)}" '
                                      f"steps, such as {_dates._shown(off_step[0])}. Give another every=.")
            missing = run.difference(when)
            counts.append((label, len(missing)))
            for stamp in missing:
                row = {column: stamp}
                row.update(dict(zip(groups, key)))
                new_rows.append(row)
        total = sum(n for _, n in counts)
        unit_words = _dates.every_words(*shown_every)
        plural = (unit_words if total == 1 else (_dates.UNITS[shown_every[1]] if shown_every[0] == 1 else
                                                    f"steps of {unit_words}"))
        each = ""
        if groups and total:
            each = " (" + ", ".join(f"{n} for {label}" for label, n in counts) + ")"
        source = "" if every is not None else f" (every {unit_words}: the most common step)"
        if total:
            print(f'Added {total} missing {plural} to "{column}"{each}{source}; the new rows have empty cells. '
                  f'Fill them next: table.fill_empty_cells("<column>", with_the="line between neighbours", '
                  f'sorted_by="{column}"' + (f', for_each="{groups[0]}"' if len(groups) == 1 else "") + ").")
        else:
            print(f'No dates were missing from "{column}"{source}.')
        added = pd.DataFrame(new_rows, columns=[column, *groups]) if new_rows else None
        frame = self._frame
        if added is not None:
            if frame.implementation.is_polars():
                import polars as pl

                extra = pl.from_pandas(added).with_columns(pl.col(column).cast(frame.to_native().schema[column]))
                native_new = pl.concat([frame.to_native(), extra], how="diagonal_relaxed")
                native_new = native_new.sort([*groups, column], maintain_order=True)
            else:
                native_new = pd.concat([frame.to_native(), added], ignore_index=True)
                native_new = native_new.sort_values([*groups, column], kind="stable").reset_index(drop=True)
            frame = nw.from_native(native_new, eager_only=True)
        return self._change(f'add {total} missing dates to "{column}"', frame)

    @friendly
    def add_smoothed_column(self, name=None, from_column=None, method="moving average", window=5, sorted_by=None,
                            for_each=None, ends=None, weights=None, degree=None, newest_weight=None, width=None,
                            smoothness=None, alpha=None, span=None, half_life=None, com=None):
        """Add a smoothed copy of a column: each value becomes a summary of its neighbours in time.

        table.add_smoothed_column("signal_smooth", from_column="signal", method="savitzky-golay", window=11, sorted_by="time")
        (with sdata.example("sensor")). The methods and their options are those of
        nums.smooth: "moving average" (weights=, ends=), "median" (R runmed, needs simplydata[r]),
        "savitzky-golay" (degree=), "exponential" (newest_weight=), "gaussian" (width=), "lowess" and
        "spline" (smoothness=; these two use the sorted_by values as x and allow uneven steps and empty
        cells), "whittaker" (smoothness=) or "wiener". The other methods need evenly spaced readings
        (sorted_by=) and no empty cells. for_each= smooths each group on its own. Undo with table.undo().
        """
        from .. import _smoothing
        from .._time_axis import need_filled, need_regular, series_of

        step_name = "add_smoothed_column"
        example = 'table.add_smoothed_column("signal_smooth", from_column="signal", window=11, sorted_by="time")'
        self._need_name(step_name, "the column to smooth (from_column=)", from_column, example)
        chosen = _smoothing.read_method(method, step_name)
        if name is None:
            name = f"{from_column}_smooth"
        if not isinstance(name, str) or not name.strip():
            raise SimplydataError(f"{step_name}() needs name= as the new column's name.\nFor example, {example}")
        if name in self._columns:
            raise SimplydataError(f'"{name}" is already a column; give another name.')
        series = series_of(self, from_column, sorted_by, for_each, step_name, example)
        filled = np.full(len(self._frame), np.nan)
        got = None
        for one in series:
            if chosen not in ("lowess", "spline"):
                need_filled(one, from_column, step_name, sorted_by)
                if sorted_by is not None:
                    need_regular(one, step_name, sorted_by)
            got = _smoothing.smooth(one.values, chosen, window, ends, times=one.times, step_name=step_name,
                                    weights=weights, degree=degree, newest_weight=newest_weight, width=width,
                                    smoothness=smoothness, alpha=alpha, span=span, half_life=half_life, com=com)
            filled[one.rows] = got.values
        groups = self._group_columns(step_name, for_each, [from_column]) if for_each is not None else []
        each = f", for each {', '.join(groups)}" if groups else ""
        order = f' in order of "{sorted_by}"' if sorted_by else ""
        print(f'Smoothed "{from_column}" with {got.sentence}{each}{order}. Added "{name}".')
        print(f"Method: as R {got.r_call}.")
        base = nw.maybe_reset_index(self._frame)
        new = nw.new_series(name, [None if np.isnan(v) else float(v) for v in filled], nw.Float64,
                            backend=base.implementation)
        return self._change(f'add smoothed column "{name}"', base.with_columns(new))
