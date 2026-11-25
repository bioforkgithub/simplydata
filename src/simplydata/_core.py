"""The heart of simplydata: a chart records steps and draws them when needed.

Why record instead of drawing straight away?
* the order of a user's lines does not matter (legend before bars still works)
* style and size can be changed at any time
* the same steps can be drawn again on many panels (draw_one_chart_for_each_group_in, put_side_by_side)

Every public step:
1. checks its input straight away, so mistakes are reported on the line that made them
2. records a Step (what to draw, in which phase)
3. returns the chart, so steps can also be chained on one line
"""

from __future__ import annotations

from ._typing import _Same

import io
import math
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import pandas as pd
from matplotlib.figure import Figure

from . import _style
from ._data import load
from ._errors import (SimplydataError, choice_error, missing_word_error, old_word, other_name_error, public_words,
                      suggest)
from ._units import check_number

# Phases decide drawing order, whatever order the user wrote the steps in.
PHASES = {
    "setup": 0,   # things that must exist before drawing
    "draw": 1,    # bars, lines, dots ... (kept in the user's order, so later layers sit on top)
    "extra": 2,   # fit lines, error bars, reference lines, shading, notes
    "axes": 3,    # ranges, log scales, ticks
    "text": 4,    # titles and labels
    "finish": 5,  # legend and other last touches
}

def _tidy_dates(fig):
    """Dates on an axis get short labels that don't overlap ("Jan", "Feb" ... with the year once)."""
    from matplotlib.dates import AutoDateFormatter, ConciseDateFormatter

    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            if isinstance(axis.get_major_formatter(), AutoDateFormatter):
                axis.set_major_formatter(ConciseDateFormatter(axis.get_major_locator()))


# ---------------------------------------------------------------- notes while drawing
# A chart can be drawn several times for one picture (each panel of draw_one_chart_for_each_group_in, each frame
# of an animation, the zoom box ...). Notes made while drawing are collected and printed once,
# when the whole picture is done, so the same note never shows up again and again.
_NOTES = {"depth": 0, "lines": {}}
# matplotlib backends that draw no window: after chart.show() on them, the figure pyplot opened is closed
_NO_WINDOW_BACKENDS = {"agg", "pdf", "ps", "svg", "pgf", "cairo", "template"}

# The options of a chart type that name the columns it draws (the rest are settings).
COLUMN_OPTIONS = ("x", "y", "z", "colour", "size", "shape", "value", "labels", "values", "angle", "distance",
                  "low", "high")
# Chart types that show empty cells on purpose, so they leave nothing out.
SHOWS_EMPTY_CELLS = {"empty_cells"}


@contextmanager
def chart_notes():
    """Collect notes while a picture is drawn; print each once at the end (also when nested)."""
    _NOTES["depth"] += 1
    try:
        yield
    except BaseException:
        if _NOTES["depth"] == 1:
            _NOTES["lines"] = {}
        raise
    finally:
        _NOTES["depth"] -= 1
    if _NOTES["depth"] == 0:
        lines, _NOTES["lines"] = _NOTES["lines"], {}
        for count, make in lines.values():
            print(make(count))


def chart_note(key, make, count=0):
    """Add a note: make(total count) gives its line. Notes with the same key are one note,
    and their counts add up (names left out on each panel ...)."""
    if _NOTES["depth"] == 0:
        print(make(count))
        return
    old = _NOTES["lines"].get(key)
    _NOTES["lines"][key] = ((old[0] if old else 0) + count, make)


def _quoted(names):
    names = [f'"{n}"' for n in names]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " or " + names[-1]


SAVE_FORMATS = ("png", "pdf", "svg", "eps", "jpg", "jpeg", "tif", "tiff", "gif")
WEB_FORMATS = ("html",)  # a web page drawn by plotly from what matplotlib drew (simplydata._web; simplydata[web])

# The word that changes each setting, for the line chart.undo() prints (charts phase, batch 1)
_SETTING_WORDS = {"style": "use_style", "width": "set_size", "height": "set_size", "pixels": "set_size",
                  "size_set": "set_size", "colour": "use_colour", "colours": "use_colours",
                  "colour_scale": "use_colour_scale", "grid": "show_grid", "font_size": "use_font_size",
                  "font_name": "use_font", "legend_title": "label_legend", "split": "draw_one_chart_for_each_group_in",
                  "animate": "animate", "shapes": "use_shapes", "title": "write_title_on_top",
                  # charts phase, batch 3
                  "y_break": "break_between_y", "pointing": "show_when_pointing", "range_bar_x": "add_range_bar_x"}


@dataclass
class Step:
    name: str
    phase: int
    func: Callable
    kwargs: dict
    scope: str = "axes"  # "axes": once per panel; "figure": once per figure
    order: int = 0


@dataclass
class Context:
    """Everything a step needs while drawing."""

    fig: Figure
    ax: object
    data: pd.DataFrame
    settings: dict
    axes: list = field(default_factory=list)  # all panels (figure-scope steps use this)
    panel_title: str | None = None
    last: dict | None = None  # the most recent data layer: kind, table, x, y, colour
    store: dict = field(default_factory=dict)  # free space for steps (e.g. second y-axis)


class BaseChart:
    """A chart. Make one with sdata.chart(...)."""

    # Old names that still work for one release (with a note the first time): old -> new.
    _OLD_WORDS = {
        "bars": "draw_bars", "lines": "draw_lines", "dots": "draw_dots", "area": "draw_area",
        "histogram": "draw_histogram", "boxes": "draw_boxes", "violins": "draw_violins", "heatmap": "draw_heatmap",
        "pie": "draw_pie", "polar": "draw_polar", "contour": "draw_contour", "surface": "draw_surface",
        "dots_3d": "draw_dots_3d", "band": "draw_band", "empty_cells": "draw_map_of_empty_cells",
        "error_bars": "draw_error_bars", "curve": "draw_curve", "smooth_line": "draw_smooth_line",
        "density": "draw_density", "count_bars": "draw_count_bars", "all_dots": "draw_all_dots",
        "side_histograms": "draw_side_histograms", "qq_dots": "draw_qq_dots",
        "cumulative_share": "draw_cumulative_share", "title_top": "write_title_on_top",
        "caption_bottom": "write_caption_at_bottom", "note": "write_note",
        "numbers_on_bars": "write_numbers_on_bars", "names_on_dots": "write_names_on_dots",
        "font_size": "use_font_size", "font_name": "use_font", "range_x": "set_range_x", "range_y": "set_range_y",
        "log_scale_x": "use_log_scale_x", "log_scale_y": "use_log_scale_y", "ticks_x": "put_ticks_x",
        "ticks_y": "put_ticks_y", "tick_format_x": "write_ticks_x_as", "tick_format_y": "write_ticks_y_as",
        "second_y": "add_second_y", "colour": "use_colour", "colours": "use_colours",
        "colour_scale": "use_colour_scale", "style": "use_style", "size": "set_size",
        "legend_top": "put_legend_at_top", "legend_bottom": "put_legend_at_bottom",
        "legend_left": "put_legend_on_left", "legend_right": "put_legend_on_right",
        "one_chart_per": "draw_one_chart_for_each_group_in", "zoom_box": "add_zoom_box",
        "survival_curves": "draw_survival_curves", "line_at_x": "draw_line_at_x", "line_at_y": "draw_line_at_y",
        "line_with_slope": "draw_line_with_slope", "color": "use_color", "colors": "use_colors",
        "color_scale": "use_color_scale", "all_points": "draw_all_dots",
        "colour_bar_label": "label_colour_bar", "color_bar_label": "label_colour_bar",
        "one_per": "draw_one_chart_for_each_group_in",
        # charts phase, batch 1 (decision D11, approved by Manish 2026-11-25): every chart type starts with draw_
        "sticks": "draw_sticks", "spectrum": "draw_spectrum", "spectrum_over_time": "draw_spectrum_over_time",
        "lag_dots": "draw_lag_dots", "peak_dots": "draw_peak_dots", "difference_dots": "draw_difference_dots",
        "forecast": "draw_forecast", "trend_and_season": "draw_trend_and_season",
        "autocorrelation_bars": "draw_autocorrelation_bars", "cross_correlation_bars": "draw_cross_correlation_bars",
        "trade_off_curve": "draw_trade_off_curve", "forest_plot": "draw_forest_plot",
    }

    def __init__(self, data=None, sheet=None, fast: bool = False):
        self._data = load(data, sheet=sheet, fast=fast)
        self._steps: list[Step] = []
        self._settings = {
            "style": "paper",
            "width": 8.0,
            "height": 6.0,
            "font_size": None,
            "grid": None,
            "split": None,  # set by draw_one_chart_for_each_group_in(): dict(by=, row=, column=, columns=)
            "projection": None,  # "polar" or "3d" for charts that need special axes
        }
        self._cache: Figure | None = None
        self._history: list = []  # chart.undo(): the steps and settings before each word

    # ------------------------------------------------------------------ recording
    def _remember_for_undo(self, what: str):
        """Keep the steps and settings as they are before a word changes them, for chart.undo().

        A word that changes several things (a setting and a step) is one step back: everything changed while
        one word runs (the outermost word the user called) shares one memory."""
        from ._cite import _frames, outermost_word

        history = self.__dict__.get("_history")
        if history is None:  # a page of charts, or a chart made before undo existed
            history = []
            object.__setattr__(self, "_history", history)
        frames = _frames()
        word_running = frames[0] if frames else None
        if word_running is not None and history and history[-1][0] is word_running:
            return
        settings = {k: (dict(v) if isinstance(v, dict) else list(v) if isinstance(v, list) else v)
                    for k, v in self._settings.items()}
        what = outermost_word() or what  # the word the user called, not the step it adds ("legend")
        history.append((word_running, what, list(self._steps), settings))

    def _add(self, name: str, phase: str, func: Callable, scope: str = "axes", **kwargs):
        self._remember_for_undo(self._public_name(name))
        self._steps.append(Step(name, PHASES[phase], func, kwargs, scope, len(self._steps)))
        self._cache = None
        return self

    def _replace(self, name: str, phase: str, func: Callable, scope: str = "axes", **kwargs):
        """Like _add, but a step with this name replaces an earlier one (e.g. write_title_on_top)."""
        self._remember_for_undo(self._public_name(name))
        self._steps = [s for s in self._steps if s.name != name]
        return self._add(name, phase, func, scope, **kwargs)

    def _set(self, **settings):
        words = [_SETTING_WORDS[k] for k in settings if k in _SETTING_WORDS]
        self._remember_for_undo(words[0] if words else "a setting")
        self._settings.update(settings)
        self._cache = None
        return self

    @staticmethod
    def _check_choice(step: str, option: str, value, choices):
        if value not in choices:
            raise choice_error(step, option, value, list(choices))

    # ------------------------------------------------------------------ drawing
    def _run(self, steps, ctx: Context):
        for step in sorted(steps, key=lambda s: (s.phase, s.order)):
            try:
                step.func(ctx, **step.kwargs)
            except SimplydataError as exc:
                if exc.args and isinstance(exc.args[0], str):  # the words as they are written now
                    exc.args = (public_words(exc.args[0]), *exc.args[1:])
                raise
            except Exception as exc:  # turn library errors into a plain message
                raise SimplydataError(
                    f"Something went wrong while drawing .{self._public_name(step.name)}():\n{exc}"
                ) from exc

    def _draw_panel(self, fig, ax, data=None, panel_title=None, axes=None) -> Context:
        """Draw all panel steps on one set of axes. Used by layouts as well."""
        ctx = Context(
            fig=fig,
            ax=ax,
            data=self._data if data is None else data,
            settings=self._settings,
            axes=axes if axes is not None else [ax],
            panel_title=panel_title,
        )
        ctx.store["whole_table"] = self._data  # a panel shows part of it (draw_one_chart_for_each_group_in, animate)
        self._run([s for s in self._steps if s.scope == "axes"], ctx)
        if panel_title is not None and not ax.get_title():
            ax.set_title(str(panel_title))
        return ctx

    def _draw_figure_steps(self, fig, axes, last_ctx: Context | None = None):
        ctx = Context(
            fig=fig,
            ax=axes[0],
            data=self._data,
            settings=self._settings,
            axes=list(axes),
            last=last_ctx.last if last_ctx else None,
            store=last_ctx.store if last_ctx else {},
        )
        self._run([s for s in self._steps if s.scope == "figure"], ctx)

    def _left_out_rows(self):
        """One note per chart type for the rows it leaves out because of empty cells.

        Counted on the whole table (not on each panel or frame). The columns that split the
        chart into panels or frames count too: a row with no group is in no panel.
        """
        data = self._data
        if data is None or len(data.columns) == 0:
            return
        split = self._settings.get("split") or {}
        animate = self._settings.get("animate") or {}
        splitting = [c for c in (split.get("by"), split.get("row"), split.get("column"), animate.get("over"))
                     if isinstance(c, str)]
        for step in self._steps:
            if step.phase != PHASES["draw"] or step.name in SHOWS_EMPTY_CELLS:
                continue
            used = [v for k, v in step.kwargs.items() if k in COLUMN_OPTIONS and isinstance(v, str)]
            used = list(dict.fromkeys(c for c in used + splitting if c in data.columns))
            if not used:
                continue
            empty = data[used].isna()
            n = int(empty.any(axis=1).sum())
            if not n:
                continue
            names = [c for c in used if empty[c].any()]
            rows = "1 row" if n == 1 else f"{n} rows"
            line = f"Note: {rows} with empty {_quoted(names)} {'was' if n == 1 else 'were'} left out of this chart."
            chart_note(line, lambda _count, line=line: line)

    def _render(self) -> Figure:
        if self._cache is not None:
            return self._cache
        with chart_notes():
            self._left_out_rows()
            return self._render_now()

    def _render_now(self) -> Figure:
        s = self._settings
        with _style.context(s):
            fig = Figure(figsize=(s["width"], s["height"]), layout="constrained")
            split = s["split"]
            if s.get("y_break"):  # chart.break_between_y(...) (charts phase, batch 3)
                from .words.extra_charts import render_broken

                if split or s["projection"] is not None:
                    raise SimplydataError(".break_between_y() works on a flat chart with one panel, not on round or "
                                          "3D charts or charts split into panels.")
                axes, ctx = render_broken(self, fig)
                self._draw_figure_steps(fig, axes, ctx)
            elif not split:
                ax = fig.add_subplot(projection=s["projection"])
                ctx = self._draw_panel(fig, ax)
                self._draw_figure_steps(fig, [ax], ctx)
            else:
                axes, ctx = self._render_split(fig, split)
                self._draw_figure_steps(fig, axes, ctx)
            _tidy_dates(fig)
        self._cache = fig
        return fig

    def _panel_groups(self, column, words="appearance"):
        """A column's groups in panel order: order_x / category / calendar order (see group_values)."""
        from .words.charts import group_values  # the chart words build on this module

        return group_values(self, column, words)

    def _render_split(self, fig, split):
        data = self._data
        row, column, by = split.get("row"), split.get("column"), split.get("by")
        share = dict(sharex=split.get("same_x", True), sharey=split.get("same_y", True))
        ctx = None
        if by is not None:
            groups = self._panel_groups(by)
            ncols = split.get("columns") or min(len(groups), 3)
            nrows = math.ceil(len(groups) / ncols)
            grid = fig.subplots(nrows, ncols, squeeze=False, subplot_kw={"projection": self._settings["projection"]}, **share)
            flat = list(grid.flat)
            for ax, g in zip(flat, groups):
                ctx = self._draw_panel(fig, ax, data[data[by] == g], panel_title=f"{by} = {g}", axes=flat)
            for ax in flat[len(groups):]:
                ax.set_visible(False)
            return flat[: len(groups)], ctx
        rows = self._panel_groups(row) if row else [None]
        cols = self._panel_groups(column) if column else [None]
        grid = fig.subplots(len(rows), len(cols), squeeze=False, subplot_kw={"projection": self._settings["projection"]}, **share)
        for i, r in enumerate(rows):
            for j, c in enumerate(cols):
                mask = pd.Series(True, index=data.index)
                parts = []
                if row:
                    mask &= data[row] == r
                    parts.append(f"{row} = {r}")
                if column:
                    mask &= data[column] == c
                    parts.append(f"{column} = {c}")
                ctx = self._draw_panel(fig, grid[i][j], data[mask], panel_title=", ".join(parts), axes=list(grid.flat))
        return list(grid.flat), ctx

    # ------------------------------------------------------------------ output
    def save(self, file_name, quality: str = "normal", resolution=None, dpi=None, see_through=False):
        """Save the chart. chart.save("marks.png") or chart.save("marks.tif", resolution=600)

        The end of the file name decides the format: "marks.png", "marks.pdf", "marks.svg", "marks.eps", or
        "marks.html" for a web page in which you can point at marks, zoom and click the legend (it needs
        simplydata[web] and works with no internet; the numbers are the picture's own).
        resolution= is the sharpness in dots per inch (dpi); normally 300.
        see_through=True saves the page with no background (the marks keep their colours), for a logo or a slide
        of another colour. Text in a .pdf, .svg or .eps file stays real text that editors and journals can read.
        """
        self._check_choice("save", "quality", quality, ("normal", "high"))
        if not isinstance(see_through, bool):
            raise SimplydataError(f".save() needs see_through=True or see_through=False, not {see_through!r}.")
        path = Path(file_name)
        fmt = path.suffix.lower().lstrip(".")
        if not fmt:
            raise SimplydataError(
                f'Add a file type to the name, for example "{path.name}.png" or "{path.name}.pdf".'
            )
        if fmt not in SAVE_FORMATS + WEB_FORMATS:
            raise choice_error("save", "file type", fmt, SAVE_FORMATS + WEB_FORMATS)
        if path.parent and not path.parent.exists():
            raise SimplydataError(f'The folder "{path.parent}" does not exist. Create it first.')
        if fmt in WEB_FORMATS:  # a web page (charts phase, batch 3)
            from ._web import need_plotly, save_page

            if resolution is not None or dpi is not None or quality != "normal":
                raise SimplydataError("A web page (.html) has no resolution: it is drawn sharp at any size. Leave "
                                      "out resolution=, dpi= and quality=, or save a picture (.png, .tif) instead.")
            need_plotly()
            return save_page(self, path, see_through=see_through)
        from ._web import picture_note

        picture_note(self)
        resolution = self._save_resolution(fmt, quality, resolution, dpi)
        if fmt == "eps" and self._draws_see_through():
            print("Note: an .eps file cannot hold see-through colours, so the see-through parts of this chart "
                  "(bands, shading, marks drawn with transparency=) are saved solid. Save as .pdf or .svg to keep "
                  "them see-through.")
        s = self._settings
        self._see_through = see_through
        if not s.get("size_set"):
            return self._save_now(path, fmt, resolution)
        # chart.set_size() was used: the file is exactly that size (no trimming of the edges)
        before = (s["width"], s["height"])
        if s.get("pixels"):
            s["width"], s["height"] = s["pixels"][0] / resolution, s["pixels"][1] / resolution
            self._cache = None
        self._check_pixels(resolution)
        try:
            return self._save_now(path, fmt, resolution, exact=True)
        finally:
            if s.get("pixels"):
                s["width"], s["height"] = before
                self._cache = None

    def _save_resolution(self, fmt, quality, resolution, dpi):
        if dpi is not None:
            if resolution is not None:
                raise SimplydataError(".save() needs resolution= or dpi= (they mean the same), not both.")
            resolution = dpi
        if resolution is None:
            return 100 if fmt == "gif" else (600 if quality == "high" else 300)
        if quality != "normal":
            raise SimplydataError('.save() needs quality="high" or resolution=, not both. '
                                  'quality="high" is the same as resolution=600.')
        resolution = check_number(resolution, "resolution", "save")
        if resolution < 10:
            raise SimplydataError(f".save() needs resolution= to be at least 10 dots per inch, not {resolution:g}. "
                                  "Pictures for papers usually need 300 or 600.")
        self._check_pixels(resolution)
        return resolution

    def _check_pixels(self, resolution):
        # a page of charts works out its own size unless page.set_size() was used
        width, height = self._page_size() if hasattr(self, "_page_size") else (
            self._settings["width"], self._settings["height"])
        w, h = width * resolution, height * resolution
        if max(w, h) >= 2**16:
            raise SimplydataError(
                f"This picture would be {round(w):,} x {round(h):,} pixels, too big to save. "
                "Choose a smaller chart.set_size() or a lower resolution=."
            )

    def _draws_see_through(self) -> bool:
        """Whether anything drawn on the chart's panels is partly see-through (a band, shading, a mark drawn with
        transparency=): read from the drawn artists' colours and alpha (grid lines and words left out)."""
        import numpy as np

        from ._numbers_drawn import _all_axes

        def partly(colours) -> bool:
            try:
                array = np.asarray(colours, dtype=float).reshape(-1, 4)
            except (TypeError, ValueError):
                return False
            return bool(((array[:, 3] > 0) & (array[:, 3] < 1)).any())

        for ax in _all_axes(self._render()):
            for artist in list(ax.collections) + list(ax.patches) + list(ax.lines) + list(ax.images):
                if not artist.get_visible():
                    continue
                alpha = artist.get_alpha()
                if alpha is not None and 0 < np.min(alpha) < 1:
                    return True
                for getter in ("get_facecolor", "get_edgecolor", "get_color"):
                    if hasattr(artist, getter) and partly(getattr(artist, getter)()):
                        return True
        return False

    def _saved_pixels(self, resolution=300) -> tuple[int, int]:
        """The width and height in pixels of the picture chart.save("x.png") writes at this resolution: the same
        drawing written to memory (without set_size, matplotlib trims the page to what is drawn)."""
        import struct

        buffer = io.BytesIO()
        s = self._settings
        before = (s.get("width"), s.get("height"))
        if s.get("size_set") and s.get("pixels"):
            s["width"], s["height"] = s["pixels"][0] / resolution, s["pixels"][1] / resolution
            self._cache = None
        try:
            self._save_now(buffer, "png", resolution, exact=bool(s.get("size_set")))
        finally:
            if s.get("size_set") and s.get("pixels"):
                s["width"], s["height"] = before
                self._cache = None
        width, height = struct.unpack(">II", buffer.getvalue()[16:24])  # the PNG header
        return width, height

    def _save_now(self, path, fmt, resolution, exact=False):
        if fmt == "gif":
            return self._save_animation(path, resolution)
        fig = self._render()
        # .tif files are compressed without losing anything (LZW), as journals ask
        extra = {"pil_kwargs": {"compression": "tiff_lzw"}} if fmt in ("tif", "tiff") else {}
        if self.__dict__.get("_see_through"):
            extra["transparent"] = True  # chart.save(..., see_through=True): no page or panel background
        if exact:
            extra["bbox_inches"] = fig.bbox_inches  # the whole page, exactly the size asked for
        with _style.context(self._settings):
            fig.savefig(path, dpi=resolution, format={"jpg": "jpeg", "tif": "tiff"}.get(fmt, fmt), **extra)
        return self

    def _save_animation(self, path, resolution=100):
        raise SimplydataError('To save a .gif, first make an animation with chart.animate(over="year").')

    def show(self: _Same) -> _Same:
        """Show the chart in a window. chart.show()

        In Jupyter, VS Code and Spyder charts appear by themselves.
        """
        import matplotlib.pyplot as plt

        from ._web import picture_note

        picture_note(self)
        self._cache = None
        fig = self._render()
        holder = plt.figure()
        manager = holder.canvas.manager
        manager.canvas.figure = fig
        fig.set_canvas(manager.canvas)
        plt.show()
        # pyplot keeps every figure it opened until it is closed. A window that stays open after plt.show()
        # returns (interactive mode: notebooks with %matplotlib widget, IPython with a window backend) belongs to
        # the user, who closes it; otherwise plt.show() has finished with it (it blocked until the window was
        # closed, or the backend draws no window, as in scripts and tests), so it is closed here, and the next
        # show() or save() draws on a new figure
        if not plt.isinteractive() or str(plt.get_backend()).lower() in _NO_WINDOW_BACKENDS:
            plt.close(manager.num)  # by number: the window now shows the chart's figure, not the holder
            self._cache = None
        return self

    def get_numbers_drawn(self):
        """A table of the numbers the chart drew. chart.get_numbers_drawn()

        One row per drawn point, in layers: each line, group of dots, set of bars, band, set of
        stems or error bars is one layer. The columns:
          panel   the chart number (1 unless the chart is split into several)
          layer   the layer number on that chart
          kind    "line", "dot", "bar", "band", "stem", "error bar", "segment", "rectangle",
                  "cell" (a heat map square), "slice" (a pie slice) or "shape"
          series  the name of the layer in the legend (empty when it has none)
          x, y    where the point is (dates on a date axis, group names on an axis of groups); for a
                  bar, x is its middle and y its height (sideways bars: x is the length, y the middle)
          low, high  the two ends of a bar, a band, a stem or an error bar
          value   the number in a heat map square, a pie slice's share of the whole, or the
                  number written at a marked point (the best cut-off of trade_off_curve)
        The numbers are read back from what matplotlib drew (nothing is worked out again), so they
        are exactly what you see: the points of a fitted curve, a forecast band, the survival steps.
        """
        from ._numbers_drawn import numbers_drawn, summary
        from .table.table import table

        frame = numbers_drawn(self._render())
        print(summary(frame))
        return table(frame)

    def _repr_png_(self):
        """Lets Jupyter, VS Code and Spyder show the chart automatically."""
        fig = self._render()
        buf = io.BytesIO()
        with _style.context(self._settings):
            fig.savefig(buf, format="png", dpi=100)
        return buf.getvalue()

    def __repr__(self):
        kinds = [self._public_name(s.name) for s in self._steps if s.phase == PHASES["draw"]]
        what = ", ".join(kinds) if kinds else "empty"
        return f"<simplydata chart: {what}>"

    # ------------------------------------------------------------------ help
    @classmethod
    def _public_name(cls, step_name: str) -> str:
        """The word a step is written with: steps keep their short inner names (bars, title_top ...)."""
        new = cls._OLD_WORDS.get(step_name)
        return new if isinstance(new, str) and hasattr(cls, new) else step_name

    @classmethod
    def _word_names(cls) -> list[str]:
        return sorted(n for n in dir(cls) if not n.startswith("_") and callable(getattr(cls, n)))

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        if self._OLD_WORDS.get(name) in self._word_names():
            return old_word(self, name, self._OLD_WORDS)
        raise other_name_error("chart", name, self._word_names()) or missing_word_error(name, self._word_names())

    def __setattr__(self, name, value):
        # chart.title = "x" would silently do nothing; tell the user what to write instead.
        if not name.startswith("_"):
            words = self._word_names()
            guesses = [w for w in words if w.startswith(name) or f"_{name}_" in w] or suggest(name, words)
            hint = f'chart.{guesses[0]}({value!r})' if guesses else "a step such as chart.write_title_on_top(\"...\")"
            raise SimplydataError(
                f"Steps are written with brackets, not with =.\nInstead of chart.{name} = ..., write {hint}"
            )
        object.__setattr__(self, name, value)
