"""Chart words for time series and signals: sticks, autocorrelation_bars, cross_correlation_bars, lag_dots,
trend_and_season, forecast, spectrum, spectrum_over_time, peak_dots.

The numbers come from the table words (find_autocorrelation_of, find_correlation_between, add_trend_and_season,
forecast, find_spectrum_of, find_each_peak_that), worked out when the word is called, so the chart shows exactly what
the table word gives back and prints the same sentences. The drawing is matplotlib.
"""

from __future__ import annotations

import numpy as np
from matplotlib import rcParams

from .._errors import SimplydataError, friendly, option_error, renamed_note
from ._helpers import check, check_thickness, check_transparency, colour_role, default_colour, palette_for, single_list


def _table_of(chart, columns=None):
    from ..table import Table

    if chart._data is None or not len(chart._data.columns):
        raise SimplydataError("This chart word needs a table: start with sdata.chart(table) or table.start_chart().")
    return Table((chart._data if columns is None else chart._data[columns]).copy())


def _frame(table):
    native = table._frame.to_native()
    return native.to_pandas() if hasattr(native, "to_pandas") else native


def _colours(ctx, frame, group, fixed=None):
    """[(name, part, colour)] for each group of the result table (one item without groups)."""
    if group is None or group not in frame.columns:
        return [(None, frame, default_colour(ctx.settings, fixed))]
    levels = list(dict.fromkeys(frame[group].tolist()))
    colours = palette_for(frame, group, ctx.settings)
    return [(level, frame[frame[group] == level], fixed or colour) for level, colour in zip(levels, colours)]


def _sticks_on(ax, xs, ys, colour, thickness, label=None):
    ax.vlines(xs, 0, ys, color=colour, linewidth=1.5 if thickness is None else thickness, zorder=2)
    ax.plot(xs, ys, "o", color=colour, markersize=5, zorder=3, label=label)


def _remember(ctx, kind, table, x, y, colour=None):
    ctx.last = dict(kind=kind, table=table, x=x, y=y, colour=colour, row_order=None)


def _draw_sticks(ctx, x, y, colour, thickness=None):
    from .charts import _frame as frame_for_chart

    group, fixed = colour_role(ctx.data, colour)
    table, n = frame_for_chart(ctx, x=x, y=y, colour=group)
    ax = ctx.ax
    parts = _colours(ctx, table, n["colour"], fixed)
    for name, part, col in parts:
        _sticks_on(ax, part[n["x"]].to_numpy(), part[n["y"]].to_numpy(dtype=float), col, thickness,
                   None if name is None else str(name))
    ax.axhline(0, color=rcParams["text.color"], linewidth=0.8, zorder=1)
    ax.set_xlabel(n["x"])
    ax.set_ylabel(n["y"])
    if len(parts) > 1:
        ax.legend(title=n["colour"])
    _remember(ctx, "sticks", table, n["x"], n["y"], n["colour"])


def _draw_result_sticks(ctx, frame, x, y, group, low=None, high=None, label_x=None, label_y=None, word="sticks"):
    ax = ctx.ax
    parts = _colours(ctx, frame, group)
    width = 0.6 / max(len(parts), 1)
    for i, (name, part, col) in enumerate(parts):
        shift = (i - (len(parts) - 1) / 2) * width if len(parts) > 1 else 0.0
        _sticks_on(ax, part[x].to_numpy(dtype=float) + shift, part[y].to_numpy(dtype=float), col, None,
                   None if name is None else str(name))
        if low is not None:
            xs = part[x].to_numpy(dtype=float)
            order = np.argsort(xs)
            for edge in (low, high):
                ax.step(xs[order], part[edge].to_numpy(dtype=float)[order], where="mid", linestyle="--", color=col,
                        linewidth=1, zorder=1.5)
    ax.axhline(0, color=rcParams["text.color"], linewidth=0.8, zorder=1)
    ax.set_xlabel(label_x or x)
    ax.set_ylabel(label_y or y)
    if len(parts) > 1:
        ax.legend(title=group)
    _remember(ctx, word, frame, x, y, group)


def _draw_lag_dots(ctx, x, y, rows_back, transparency=None):
    import pandas as pd

    data = ctx.data
    values = data.sort_values(x, kind="stable")[y] if x is not None else data[y]
    values = pd.to_numeric(values, errors="coerce").reset_index(drop=True)
    ax = ctx.ax
    colours = rcParams["axes.prop_cycle"].by_key()["color"]
    shown = []
    for i, k in enumerate(rows_back):
        earlier = values.shift(k)
        keep = earlier.notna() & values.notna()
        ax.scatter(earlier[keep], values[keep], s=18, color=colours[i % len(colours)], alpha=1 - (transparency or 0),
                   label=f"{k} row{'s' if k != 1 else ''} back", zorder=2)
        shown.append(np.concatenate([earlier[keep].to_numpy(dtype=float), values[keep].to_numpy(dtype=float)]))
    allv = np.concatenate(shown) if shown else np.array([0.0, 1.0])
    low, high = float(np.nanmin(allv)), float(np.nanmax(allv))
    ax.plot([low, high], [low, high], linestyle="--", color="grey", linewidth=1, zorder=1)
    ax.set_xlabel(f"{y}, rows back")
    ax.set_ylabel(y)
    if len(rows_back) > 1:
        ax.legend()
    table = pd.DataFrame({"earlier": values.shift(rows_back[0]), y: values})
    _remember(ctx, "lag_dots", table, "earlier", y)


def _draw_trend_and_season(ctx, frame, x, y):
    ax = ctx.ax
    ax.set_axis_off()
    colour = default_colour(ctx.settings)
    names = [(y, y), (f"{y}_trend", "trend"), (f"{y}_season", "season"), (f"{y}_rest", "rest")]
    panels = []
    for i, (column, title) in enumerate(names):
        inner = ax.inset_axes([0, 1 - (i + 1) * 0.25 + 0.02, 1, 0.21], sharex=panels[0] if panels else None)
        xs = frame[x] if x is not None else np.arange(1, len(frame) + 1)
        if i == 3:
            inner.vlines(xs, 0, frame[column].to_numpy(dtype=float), color=colour, linewidth=1)
            inner.axhline(0, color="grey", linewidth=0.8)
        else:
            inner.plot(xs, frame[column].to_numpy(dtype=float), color=colour, linewidth=1.5)
        inner.set_ylabel(title)
        if i < 3:
            inner.tick_params(labelbottom=False)
        panels.append(inner)
    panels[-1].set_xlabel(x or "row")
    _remember(ctx, "trend_and_season", frame, x, y)


def _draw_forecast(ctx, frame, x, group, interval):
    ax = ctx.ax
    for name, part, col in _colours(ctx, frame, group):
        xs = part[x]
        ax.plot(xs, part["forecast"].to_numpy(dtype=float), linestyle="--", color=col, linewidth=2, zorder=3,
                label=None)
        low = [c for c in part.columns if c.endswith("% prediction low")][0]
        high = [c for c in part.columns if c.endswith("% prediction high")][0]
        ax.fill_between(xs, part[low].to_numpy(dtype=float), part[high].to_numpy(dtype=float), color=col,
                        alpha=0.2, linewidth=0, zorder=2.5)


def _draw_spectrum(ctx, frame, column, group, log_scale, peaks):
    ax = ctx.ax
    parts = _colours(ctx, frame, group)
    for name, part, col in parts:
        part = part[part["frequency"] > 0]
        ax.plot(part["frequency"].to_numpy(dtype=float), part[column].to_numpy(dtype=float), color=col,
                linewidth=1.5, label=None if name is None else str(name))
    for f, value, period, col in peaks:
        ax.annotate(f"repeats every {period:.3g}", (f, value), textcoords="offset points", xytext=(4, 4),
                    fontsize=rcParams["legend.fontsize"], color=col)
    if log_scale:
        ax.set_yscale("log")
    ax.set_xlabel("frequency")
    ax.set_ylabel(column)
    if len(parts) > 1:
        ax.legend(title=group)
    _remember(ctx, "spectrum", frame, "frequency", column, group)


def _draw_spectrum_over_time(ctx, times, frequencies, decibels):
    ax = ctx.ax
    mesh = ax.pcolormesh(times, frequencies, decibels, shading="nearest", cmap="viridis")
    bar = ctx.fig.colorbar(mesh, ax=ax)
    bar.set_label("power (decibels)")
    ax.set_xlabel("time")
    ax.set_ylabel("frequency")
    import pandas as pd

    _remember(ctx, "spectrum_over_time", pd.DataFrame(), None, None)


def _draw_peak_dots(ctx, frame, x, y, group, dips):
    ax = ctx.ax
    for name, part, col in _colours(ctx, frame, group):
        ax.scatter(part[x], part["value"].to_numpy(dtype=float), marker="v" if dips else "^", s=60, color=col,
                   edgecolors=rcParams["axes.facecolor"], zorder=4)


class TimeChartWords:
    """Chart words for time series and signals (mixed into Chart)."""

    def _last_layer(self, word, kinds=("lines", "dots", "area", "sticks")):
        from .._core import PHASES

        draws = [s for s in self._steps if s.phase == PHASES["draw"] and s.name in kinds]
        return draws[-1].kwargs if draws else {}

    def _xy(self, word, x, y, example):
        last = self._last_layer(word)
        x = last.get("x") if x is None else x
        y = last.get("y") if y is None else y
        if y is None:
            raise SimplydataError(f".{word}() needs y= (the column), for example {example}.")
        check(self._data, x=x, y=y)
        return x, y, last.get("colour")

    def _column_first(self, word, column, sorted_by, example):
        """(column, sorted_by) of a chart word that takes the column first, as its table word does; a lines
        layer before it gives them when left out."""
        last = self._last_layer(word)
        column = last.get("y") if column is None else column
        sorted_by = last.get("x") if sorted_by is None else sorted_by
        if column is None:
            raise SimplydataError(f".{word}() needs the column first, for example {example}.")
        check(self._data, x=sorted_by, y=column)
        return column, sorted_by

    @friendly
    def sticks(self, x=None, y=None, colour=None, thickness=None):
        """A thin line from 0 up (or down) to each value, with a dot on top (a stem chart).

        chart.sticks(x="month_number", y="rain", colour="city")   (with sdata.get_example("weather"))
        Good for values at separate places, such as correlations for each number of rows back.
        colour="group" draws each group in its own colour. thickness=3 draws thicker sticks (normal is 1.5).
        """
        thickness = check_thickness("sticks", thickness)
        x, y = single_list(x, y)
        if x is None or y is None:
            raise SimplydataError('.sticks() needs x= and y=, for example chart.sticks(x="rows back", y="correlation").')
        group, _ = colour_role(self._data, colour)
        check(self._data, x=x, y=y, colour=group)
        self._need_axes("sticks")
        return self._add("sticks", "draw", _draw_sticks, x=x, y=y, colour=colour, thickness=thickness)

    @friendly(renamed={"y": "column", "x": "sorted_by"})
    def autocorrelation_bars(self, column=None, sorted_by=None, rows_back=None, show="correlation",
                             band="white noise"):
        """Sticks for the correlation of a column with itself 1, 2, ... rows back, with the noise band.

        chart.autocorrelation_bars("visitors", sorted_by="month")   (with one museum of sdata.get_example("visitors"))
        The column first, sorted_by= the time column (the order), as table.find_autocorrelation_of: the heights
        are its numbers (rows_back=, show="correlation" or "partial", band="white noise" or "bartlett"); the
        dashed lines are the band, as R plot(acf(x)). colour= groups are not used: keep one series first.
        """
        y, x = self._column_first("autocorrelation_bars", column, sorted_by,
                                  'chart.autocorrelation_bars("visitors", sorted_by="month")')
        got = _frame(_table_of(self).find_autocorrelation_of(y, sorted_by=x, rows_back=rows_back, show=show, band=band))
        value = [c for c in got.columns if c not in ("rows back", "band low", "band high", "outside band",
                                                     "Ljung-Box statistic", "Ljung-Box p-value")][-1]
        self._need_axes("autocorrelation_bars")
        return self._add("autocorrelation_bars", "draw", _draw_result_sticks, frame=got, x="rows back", y=value,
                         group=None, low="band low", high="band high", word="autocorrelation_bars")

    @friendly(renamed={"x": "sorted_by"})
    def cross_correlation_bars(self, *columns, sorted_by=None, rows_back=None, **other_names):
        """Sticks for the correlation of two columns when the second is shifted by -k to k rows.

        chart.cross_correlation_bars("signal", "vibration", sorted_by="time", rows_back=20)   (with sdata.get_example("sensor"))
        The two columns first, sorted_by= the time column, as table.find_correlation_between: the heights are
        its numbers. A high stick at shift 6 means the second column follows the first 6 rows later.
        """
        example = 'chart.cross_correlation_bars("signal", "vibration", sorted_by="time")'
        columns = list(columns)
        for old, place in (("y", 0), ("against", 1)):  # the spellings before 0.6 was released
            if old in other_names:
                renamed_note(f"{old}=", "the first column" if place == 0 else "the second column")
                value = other_names.pop(old)
                if len(columns) > place:
                    raise SimplydataError(f"Give the {'first' if place == 0 else 'second'} column once ({old}= is "
                                          f"its old name). For example, {example}.")
                columns.insert(place, value)
        if other_names:
            raise option_error("cross_correlation_bars", next(iter(other_names)), ["sorted_by", "rows_back"])
        if len(columns) != 2:
            raise SimplydataError(f".cross_correlation_bars() needs two columns, for example {example}.")
        y, against = columns
        x = sorted_by if sorted_by is not None else self._last_layer("cross_correlation_bars").get("x")
        check(self._data, x=x, y=y)
        check(self._data, y=against)
        rows_back = 10 if rows_back is None else rows_back
        got = _frame(_table_of(self).find_correlation_between(y, against, rows_back=rows_back, sorted_by=x))
        shift = [c for c in got.columns if c.startswith("shift")][0]
        value = [c for c in got.columns if c not in (shift,) and got[c].dtype.kind == "f"][0]
        low = high = None
        if "band low" in got.columns:
            low, high = "band low", "band high"
        self._need_axes("cross_correlation_bars")
        return self._add("cross_correlation_bars", "draw", _draw_result_sticks, frame=got, x=shift, y=value,
                         group=None, low=low, high=high, word="cross_correlation_bars")

    @friendly(renamed={"y": "column", "x": "sorted_by"})
    def lag_dots(self, column=None, sorted_by=None, rows_back=1, transparency=None):
        """Dots of each value against the value some rows back, with the 1:1 line (as R lag.plot).

        chart.lag_dots("visitors", sorted_by="month", rows_back=[1, 12])   (with one museum of sdata.get_example("visitors"))
        The column first, sorted_by= the time column (the order; table order without it). rows_back= one
        number or a list: each gets its own colour. Dots near the dashed 1:1 line mean the value is like
        the one rows_back earlier. transparency=0.5 makes the dots half see-through where many overlap.
        """
        if column is None:
            raise SimplydataError('.lag_dots() needs the column first, for example chart.lag_dots("visitors", '
                                  'sorted_by="month").')
        y, x = column, sorted_by
        check(self._data, x=x, y=y)
        transparency = check_transparency("lag_dots", transparency)
        ks = rows_back if isinstance(rows_back, (list, tuple)) else [rows_back]
        if not ks or any(isinstance(k, bool) or not isinstance(k, int) or k < 1 for k in ks):
            raise SimplydataError("rows_back= needs whole numbers of 1 or more, such as rows_back=[1, 12].")
        self._need_axes("lag_dots")
        return self._add("lag_dots", "draw", _draw_lag_dots, x=x, y=y, rows_back=list(ks), transparency=transparency)

    @friendly
    def trend_and_season(self, x=None, y=None, repeats_every=None, method="loess"):
        """Four panels sharing x: the column itself, its trend, its season and the rest (as R plot(stl(...)),
        which labels the first panel "data").

        chart.trend_and_season(x="month", y="visitors", repeats_every="year")   (with one museum of sdata.get_example("visitors"))
        The parts are those of table.add_trend_and_season (repeats_every=, method="loess", "moving
        averages" or "straight line"); the first panel is named after the column.
        """
        if y is None:
            raise SimplydataError('.trend_and_season() needs y=, for example chart.trend_and_season(x="month", '
                                  'y="visitors", repeats_every="year").')
        check(self._data, x=x, y=y)
        table = _table_of(self, [c for c in (x, y) if c is not None])
        table.add_trend_and_season(y, sorted_by=x, repeats_every=repeats_every, method=method)
        got = _frame(table)
        if x is not None:
            got = got.sort_values(x, kind="stable")
        self._need_axes("trend_and_season")
        return self._add("trend_and_season", "draw", _draw_trend_and_season, frame=got, x=x, y=y)

    @friendly
    def forecast(self, x=None, y=None, steps_ahead=12, method="exponential smoothing", repeats_every=None, trend=True,
                 season="added", order=None, seasonal_order=None, interval=95):
        """The forecast after the data: a dashed line and its interval band, per colour group.

        chart.forecast(steps_ahead=12, repeats_every="year")   (after chart.draw_lines(x="month", y="visitors",
        colour="museum") with sdata.get_example("visitors")). x= and y= come from the lines before it (or give them). The numbers and the printed sentence are
        those of table.forecast (method=, repeats_every=, interval= ...); the colour groups of the lines
        are forecast one by one.
        """
        x, y, colour = self._xy("forecast", x, y, 'chart.draw_lines(x="month", y="visitors").forecast(steps_ahead=12)')
        group = colour if isinstance(colour, str) and colour in self._data.columns else None
        got = _frame(_table_of(self).forecast(y, sorted_by=x, steps_ahead=steps_ahead, method=method,
                                               repeats_every=repeats_every, trend=trend, season=season, order=order,
                                               seasonal_order=seasonal_order, interval=interval, for_each_group_in=group))
        return self._add("forecast", "extra", _draw_forecast, frame=got, x=x, group=group, interval=interval)

    @friendly(renamed={"y": "column", "x": "sorted_by"})
    def spectrum(self, column=None, sorted_by=None, method="periodogram", show="power", window=None, log_scale=True):
        """Power against frequency: which cycles a column holds, the 3 strongest labelled with their period.

        chart.spectrum("signal", sorted_by="time")   (with sdata.get_example("sensor"))
        The column first, sorted_by= the time column, as table.find_spectrum_of: the numbers are its numbers
        (method="periodogram", "welch" or "lomb-scargle"; show="power", "decibels" or "amplitude").
        log_scale=True puts the power on a log scale (not for decibels). colour= groups each get a line.
        """
        if column is None:
            raise SimplydataError('.spectrum() needs the column first, for example chart.spectrum("signal", '
                                  'sorted_by="time").')
        y, x = column, sorted_by
        check(self._data, x=x, y=y)
        last = self._last_layer("spectrum")
        colour = last.get("colour") if last.get("y") == y else None
        group = colour if isinstance(colour, str) and colour in self._data.columns else None
        got = _frame(_table_of(self).find_spectrum_of(y, sorted_by=x, method=method, show=show, window=window,
                                                 for_each_group_in=group))
        column = [c for c in got.columns if c not in ("frequency", "repeats every", "share of variance (%)")
                  and c != group][-1]
        peaks = []
        for name, part in ([(None, got)] if group is None else list(got.groupby(group, sort=False))):
            part = part[part["frequency"] > 0]
            for _, row in part.nlargest(3, "share of variance (%)").iterrows():
                peaks.append((row["frequency"], row[column], row["repeats every"], rcParams["text.color"]))
        if self._steps and any(s.name == "spectrum" for s in self._steps):
            raise SimplydataError(".spectrum() is already on this chart.")
        self._need_axes("spectrum")
        return self._add("spectrum", "draw", _draw_spectrum, frame=got, column=column, group=group,
                         log_scale=bool(log_scale) and show != "decibels", peaks=peaks)

    @friendly(renamed={"y": "column", "x": "sorted_by"})
    def spectrum_over_time(self, column=None, sorted_by=None, window=256, window_shape="hann"):
        """How the cycles in a column change over time: a heat map of time, frequency and power (decibels).

        chart.spectrum_over_time("signal", sorted_by="time", window=100)   (with sdata.get_example("sensor"))
        The column first, sorted_by= the time column. The column is cut into pieces of window= readings
        that overlap by half; each piece gets its periodogram (window_shape= weights, the mean of each piece
        removed), as SciPy signal.spectrogram; the time of each piece is its middle. The readings must be
        evenly spaced (sorted_by=) and filled in.
        """
        from .._time_axis import need_filled, need_regular, series_of

        example = 'chart.spectrum_over_time("signal", sorted_by="time")'
        if column is None:
            raise SimplydataError(f".spectrum_over_time() needs the column first, for example {example}.")
        y, x = column, sorted_by
        check(self._data, x=x, y=y)
        table = _table_of(self)
        one = series_of(table, y, x, None, "spectrum_over_time", example)[0]
        need_filled(one, y, "spectrum_over_time", x)
        if x is not None:
            need_regular(one, "spectrum_over_time", x)
        if isinstance(window, bool) or not isinstance(window, int) or not 4 <= window <= len(one.values):
            raise SimplydataError(f"window= needs a whole number of readings from 4 to {len(one.values)}.")
        frequencies, times, power = spectrum_over_time(one.values, one.step, window, window_shape)
        start = one.times[0] if one.times is not None else 0.0
        with np.errstate(divide="ignore"):
            decibels = 10 * np.log10(power)
        print(f'Spectrum over time of "{y}": {len(times)} pieces of {window} readings (half overlap, {window_shape} '
              f"weights), frequencies 0 to {frequencies[-1]:.4g}. Method: SciPy signal.spectrogram.")
        self._need_axes("spectrum_over_time")
        return self._add("spectrum_over_time", "draw", _draw_spectrum_over_time, times=times + start,
                         frequencies=frequencies, decibels=decibels)

    @friendly(renamed={"at_least": "is_at_least", "at_most": "is_at_most"})
    def peak_dots(self, x=None, y=None, is_at_least=None, apart=None, stands_out_by=None, dips=False, is_at_most=None):
        """Dots on the peaks of the line (and on the dips with dips=True).

        chart.peak_dots(is_at_least=1, apart=0.05)   (after chart.draw_lines(x="time", y="signal") with sdata.get_example("sensor"))
        The peaks are those of table.find_each_peak_that (is_at_least=, apart=, stands_out_by=); dips=True marks the
        dips of table.find_each_dip_that instead (is_at_most=). x= and y= come from the lines before it.
        """
        x, y, colour = self._xy("peak_dots", x, y, 'chart.draw_lines(x="time", y="signal").peak_dots(is_at_least=1)')
        group = colour if isinstance(colour, str) and colour in self._data.columns else None
        table = _table_of(self)
        if dips:
            got = table.find_each_dip_that(y, sorted_by=x, is_at_most=is_at_most, apart=apart, stands_out_by=stands_out_by,
                                  for_each_group_in=group)
        else:
            if is_at_most is not None:
                raise SimplydataError("is_at_most= goes with dips=True.")
            got = table.find_each_peak_that(y, sorted_by=x, is_at_least=is_at_least, apart=apart, stands_out_by=stands_out_by,
                                   for_each_group_in=group)
        frame = _frame(got)
        where = x if x is not None else "position"
        return self._add("peak_dots", "extra", _draw_peak_dots, frame=frame, x=where,
                         y=y, group=group if group in frame.columns else None, dips=bool(dips))


def spectrum_over_time(values, step, window, window_shape="hann"):
    """(frequencies, times, power) from SciPy signal.spectrogram: pieces of window readings, half overlap,
    window_shape= weights (periodic), each piece's mean removed, one-sided density."""
    from scipy import signal

    return signal.spectrogram(np.asarray(values, dtype=float), fs=1 / step, window=window_shape, nperseg=int(window),
                              noverlap=int(window) // 2, detrend="constant", scaling="density", mode="psd")
