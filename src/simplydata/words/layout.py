"""Several charts together, small multiples, zoom boxes and animation.

How the hard tricks work underneath (users never see this):
* draw_one_chart_for_each_group_in  sets settings["split"]; BaseChart._render_split draws one panel per group.
* put_side_by_side,  a Page gives every chart its own matplotlib SubFigure, so each chart keeps
  put_one_above_other, its own title, labels and legend, and figure-wide steps of one chart
  grid             (labels, legends) cannot land on another chart.
* add_zoom_box       draws the chart's data steps again into an inset axes.
* animate        draws the chart once per value of a column and saves the frames as a GIF.
"""

from __future__ import annotations

from .._typing import _Same

import math
import numbers

import matplotlib
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec

from .. import _style
from .._core import PHASES, BaseChart, Context, chart_notes
from .._data import is_listlike
from .._errors import SimplydataError, column_error, friendly, option_error, renamed_note
from .look import LookWords
from .read_back import ReadBackWords

# Inset positions inside the main plot: [left, bottom, width, height] as parts of the plot.
_ZOOM_PLACES = {
    "top right": [0.58, 0.56, 0.39, 0.4],
    "top left": [0.03, 0.56, 0.39, 0.4],
    "bottom right": [0.58, 0.05, 0.39, 0.4],
    "bottom left": [0.03, 0.05, 0.39, 0.4],
}
# Old place names (matplotlib's words), still understood for one release.
_OLD_PLACES = {"upper right": "top right", "upper left": "top left",
               "lower right": "bottom right", "lower left": "bottom left"}
# Steps that must not be drawn again inside a zoom box.
_NOT_IN_ZOOM = {"zoom_box", "second_y"}


def _draw_chart(chart, fig):
    """Draw every step of `chart` into `fig` (a Figure or a SubFigure). Returns the panels."""
    split = chart._settings["split"]
    if not split:
        ax = fig.add_subplot(projection=chart._settings["projection"])
        axes, ctx = [ax], chart._draw_panel(fig, ax)
    else:
        axes, ctx = chart._render_split(fig, split)
    chart._draw_figure_steps(fig, axes, ctx)
    return axes


def _check_bool(step, name, value):
    if not isinstance(value, bool):
        raise SimplydataError(f".{step}() needs {name}=True or {name}=False, not {value!r}.")


# ---------------------------------------------------------------- zoom box
def _zoom_box(ctx, chart, x_between, y_between, where):
    ax = ctx.ax
    if ax.name != "rectilinear":
        raise SimplydataError(".add_zoom_box() works on flat charts with an x and a y axis, not on polar or 3D charts.")
    inset = ax.inset_axes(_ZOOM_PLACES[where])
    sub = Context(fig=ctx.fig, ax=inset, data=ctx.data, settings=ctx.settings, axes=[inset])
    again = [s for s in chart._steps
             if s.scope == "axes" and s.phase in (PHASES["draw"], PHASES["extra"], PHASES["axes"])
             and s.name not in _NOT_IN_ZOOM]
    chart._run(again, sub)
    if inset.get_legend() is not None:
        inset.get_legend().remove()
    inset.set_xlim(*x_between)
    inset.set_ylim(*y_between)
    inset.set_xlabel("")
    inset.set_ylabel("")
    inset.set_title("")
    inset.tick_params(labelsize="small")
    inset.set_facecolor(matplotlib.rcParams["axes.facecolor"])
    inset.set_zorder(5)  # above the main plot's lines and legend
    ax.indicate_inset_zoom(inset, edgecolor=matplotlib.rcParams["axes.edgecolor"])


# ---------------------------------------------------------------- animation helpers
def _label_frame(fig, axes, over, value):
    text = f"{over}: {value}"
    sup = getattr(fig, "_suptitle", None)
    if len(axes) == 1:
        title = axes[0].get_title()
        axes[0].set_title(f"{title}  ({text})" if title else text)
    elif sup is not None and sup.get_visible() and sup.get_text():
        sup.set_text(f"{sup.get_text()}  ({text})")
    else:
        fig.suptitle(text, fontweight="bold")


class LayoutWords:
    # ------------------------------------------------------------ small multiples
    @friendly(renamed={"row": "down", "column": "across", "columns": "per_row"})
    def draw_one_chart_for_each_group_in(self: _Same, by=None, down=None, across=None, per_row=None, same_x=True, same_y=True) -> _Same:
        """One small chart for each group. chart.draw_one_chart_for_each_group_in("class", per_row=3) (with sdata.get_example("marks"))

        per_row=3 puts 3 small charts in each row.
        down="class", across="subject" makes a table of charts: the classes go down (one
        row of charts each) and the subjects go across (one column of charts each).
        same_x=False / same_y=False lets each small chart choose its own axis range.
        """
        row, column, columns = down, across, per_row
        if by is None and row is None and column is None:
            raise SimplydataError(
                '.draw_one_chart_for_each_group_in() needs a column to split by, for example chart.draw_one_chart_for_each_group_in("class")\n'
                'or chart.draw_one_chart_for_each_group_in(down="class", across="subject").'
            )
        if by is not None and (row is not None or column is not None):
            raise SimplydataError(
                '.draw_one_chart_for_each_group_in() takes either one column (chart.draw_one_chart_for_each_group_in("class"))\n'
                'or down= and across= (chart.draw_one_chart_for_each_group_in(down="class", across="subject")), not both.'
            )
        if columns is not None:
            if by is None:
                raise SimplydataError(
                    'per_row= only works with one column, for example chart.draw_one_chart_for_each_group_in("class", per_row=3).')
            if isinstance(columns, bool) or not isinstance(columns, int) or columns < 1:
                raise SimplydataError(f"per_row= should be a whole number such as 2 or 3, not {columns!r}.")
        _check_bool("draw_one_chart_for_each_group_in", "same_x", same_x)
        _check_bool("draw_one_chart_for_each_group_in", "same_y", same_y)
        data = self._data
        if data is None or len(data.columns) == 0:
            raise SimplydataError(
                '.draw_one_chart_for_each_group_in() needs a table, for example sdata.chart(sdata.get_example("marks")).draw_one_chart_for_each_group_in("class").')
        for name in (by, row, column):
            if name is not None and name not in data.columns:
                raise column_error(name, data.columns)

        if by is not None:
            n = data[by].nunique(dropna=True)
            ncols = min(columns or min(n, 3), max(n, 1))
            nrows = math.ceil(n / ncols) if n else 1
        else:
            nrows = data[row].nunique(dropna=True) if row else 1
            ncols = data[column].nunique(dropna=True) if column else 1
        self._set(split=dict(by=by, row=row, column=column, columns=columns, same_x=same_x, same_y=same_y))
        if not self._settings.get("size_set"):  # about 4 x 3.3 inches for each small chart
            self._set(width=max(6.0, 4.0 * ncols + 1.0), height=max(4.5, 3.3 * nrows + 1.2))
        return self

    # ------------------------------------------------------------ zoom box
    @friendly
    def add_zoom_box(self: _Same, x_between=None, y_between=None, where="top right", **old) -> _Same:
        """A small box showing part of the chart close up.

        chart.add_zoom_box(x_between=[2, 4], y_between=[40, 60]) (with sdata.get_example("marks"))
        x_between= and y_between= are the part to show: [low, high] on each axis.
        where="top right" (default), "top left", "bottom right" or "bottom left".
        """
        example = "chart.add_zoom_box(x_between=[2, 4], y_between=[40, 60])"
        spans = {"x": x_between, "y": y_between}
        for key in old:  # x_from=, x_to=, y_from=, y_to= are the old way of writing the spans
            if key not in ("x_from", "x_to", "y_from", "y_to"):
                raise option_error("add_zoom_box", key, ["x_between", "y_between", "where"])
        for axis in "xy":
            low, high = old.get(f"{axis}_from"), old.get(f"{axis}_to")
            if low is None and high is None:
                continue
            renamed_note(f"{axis}_from= and {axis}_to=", f"{axis}_between=")
            if spans[axis] is not None:
                raise SimplydataError(f"Give {axis}_between= only ({axis}_from= and {axis}_to= are its old names).")
            spans[axis] = [low, high]
        if isinstance(where, str) and where.strip().lower() in _OLD_PLACES:
            new = _OLD_PLACES[where.strip().lower()]
            renamed_note(f'where="{where}"', f'where="{new}"')
            where = new
        self._check_choice("add_zoom_box", "where", where, list(_ZOOM_PLACES))
        for axis, span in spans.items():
            name = f"{axis}_between"
            if span is None:
                raise SimplydataError(f".add_zoom_box() needs {name}=[low, high].\nFor example {example}")
            if isinstance(span, (str, bytes)) or not is_listlike(span) or len(span) != 2:
                raise SimplydataError(f".add_zoom_box() needs two numbers in {name}=[low, high], not {span!r}.\n"
                                      f"For example {example}")
            for value in span:
                if isinstance(value, bool) or not isinstance(value, numbers.Real):
                    raise SimplydataError(f".add_zoom_box() needs numbers in {name}=, not {value!r}.\n"
                                          f"For example {example}")
            low, high = sorted(float(v) for v in span)
            if low == high:
                raise SimplydataError(f".add_zoom_box() needs two different numbers in {name}=.\nFor example {example}")
            spans[axis] = (low, high)
        return self._replace("zoom_box", "finish", _zoom_box, chart=self, x_between=spans["x"],
                             y_between=spans["y"], where=where)

    # ------------------------------------------------------------ animation
    @friendly
    def animate(self: _Same, over, seconds_per_frame=0.8, keep=False) -> _Same:
        """A moving chart with one picture for each value of a column.

        chart.animate(over="year") (with sdata.get_example("growth")), then chart.save("growth.gif")
        keep=True builds the chart up: each picture also keeps the values before it.
        """
        data = self._data
        if data is None or len(data.columns) == 0:
            raise SimplydataError('.animate() needs a table, for example sdata.chart(sdata.get_example("growth")).animate(over="year").')
        if is_listlike(over) or over not in data.columns:
            raise column_error(over, data.columns)
        if isinstance(seconds_per_frame, bool) or not isinstance(seconds_per_frame, numbers.Real) \
                or seconds_per_frame <= 0:
            raise SimplydataError(f"seconds_per_frame= should be a number bigger than 0, such as 0.8, not {seconds_per_frame!r}.")
        _check_bool("animate", "keep", keep)
        if data[over].nunique(dropna=True) < 2:
            raise SimplydataError(f'Column "{over}" has fewer than 2 different values, so there is nothing to animate.')
        return self._set(animate=dict(over=over, seconds=float(seconds_per_frame), keep=keep))

    def _frames(self):
        anim = self._settings["animate"]
        data, over = self._data, anim["over"]
        values = self._panel_groups(over, words="sorted")  # calendar months, order_x ... else small to big
        for i, value in enumerate(values):
            shown = values[: i + 1] if anim["keep"] else [value]
            yield value, data[data[over].isin(shown)]

    def _fixed_limits(self):
        """Axis ranges of the chart with all the data, so frames do not jump about."""
        fig = Figure(figsize=(self._settings["width"], self._settings["height"]), layout="constrained")
        return [(ax.get_xlim(), ax.get_ylim()) for ax in _draw_chart(self, fig)]

    def _draw_frame(self, fig, value, table, limits):
        fig.clear()
        full = self._data
        self._data = table
        try:
            axes = _draw_chart(self, fig)
        finally:
            self._data = full
        for ax, (xlim, ylim) in zip(axes, limits):
            if ax.name == "rectilinear":
                ax.set_xlim(xlim)
                ax.set_ylim(ylim)
        _label_frame(fig, axes, self._settings["animate"]["over"], value)

    def _render(self):
        """An animated chart shown as a still picture (in Jupyter or as .png) shows its last frame."""
        if not self._settings.get("animate"):
            return super()._render()
        if self._cache is not None:
            return self._cache
        s = self._settings
        with chart_notes(), _style.context(s):
            self._left_out_rows()
            limits = self._fixed_limits()
            fig = Figure(figsize=(s["width"], s["height"]), layout="constrained")
            *_, (value, table) = self._frames()
            self._draw_frame(fig, value, table, limits)
        self._cache = fig
        return fig

    def _save_animation(self, path, resolution=100):
        if not self._settings.get("animate"):
            return super()._save_animation(path, resolution)
        from matplotlib.animation import PillowWriter

        s = self._settings
        seconds = s["animate"]["seconds"]
        with chart_notes(), _style.context(s), matplotlib.rc_context({"savefig.bbox": None}):  # same size frames
            self._left_out_rows()
            limits = self._fixed_limits()
            fig = Figure(figsize=(s["width"], s["height"]), layout="constrained")
            writer = PillowWriter(fps=1.0 / seconds)
            with writer.saving(fig, str(path), dpi=resolution):
                for value, table in self._frames():
                    self._draw_frame(fig, value, table, limits)
                    writer.grab_frame()
        return self


# ---------------------------------------------------------------- pages of several charts
class Page(ReadBackWords, BaseChart):
    """Several charts on one page. Make one with sdata.put_side_by_side, sdata.put_one_above_other or sdata.put_in_rows_and_columns."""

    def __init__(self, charts, rows, columns, same_x=False, same_y=False, how="grid", letters=False, cells=None,
                 widths=None, heights=None, one_legend=False):
        self._charts = list(charts)
        self._letters = letters
        self._rows, self._columns, self._how = rows, columns, how
        self._same_x, self._same_y = same_x, same_y
        # charts phase, batch 1: where each chart goes, [(chart, first row, last row + 1, first column, last
        # column + 1)] (a chart can span cells), the relative widths of the columns and heights of the rows, and
        # one legend for the whole page
        if cells is None:
            cells = [(chart, i // columns, i // columns + 1, i % columns, i % columns + 1)
                     for i, chart in enumerate(self._charts)]
        self._cells = cells
        self._widths, self._heights, self._one_legend = widths, heights, one_legend
        self._data = pd.DataFrame()
        self._steps = []
        styles = {c._settings["style"] for c in self._charts}
        self._settings = {
            "style": styles.pop() if len(styles) == 1 else "paper",
            "style_set": False,  # True after page.use_style(...): then every chart uses it
            "font_size": None,
            "grid": None,
            "title": None,
            "size_set": False,
            "width": None,
            "height": None,
        }
        self._cache = None

    set_size = LookWords.set_size

    @friendly
    def use_style(self: _Same, name) -> _Same:
        """One look for every chart on the page: "paper", "school", "presentation" or "dark"."""
        LookWords.use_style(self, name)
        return self._set(style_set=True)

    @friendly
    def write_title_on_top(self: _Same, text) -> _Same:
        """A title above the whole page. page.write_title_on_top("Marks in both classes")"""
        return self._set(title=str(text))

    @friendly
    def say_what_it_shows(self) -> str:
        """Say in words what each chart on the page shows. page.say_what_it_shows()

        The page title, how the charts are placed, then each chart (by its letter with with_letters=True) as
        chart.say_what_it_shows() says it. Read from the steps and from the charts as drawn: nothing is worked out.
        """
        from .more_charts import describe_chart

        s = self._settings
        with chart_notes():
            lines = [f'Title: "{s["title"]}".'] if s["title"] else []
            lines.append(f"A page of {len(self._cells)} charts, {self._how}"
                         + (", with one legend for the whole page." if self._one_legend else "."))
            if s["style_set"] and s["style"] == "black and white":
                lines.append('Style "black and white": greys; the groups also differ by pattern, dashes or dot shape.')
            for number, (chart, r0, r1, c0, c1) in enumerate(self._cells):
                rows = f"row {r0 + 1}" if r1 - r0 == 1 else f"rows {r0 + 1} to {r1}"
                columns = f"column {c0 + 1}" if c1 - c0 == 1 else f"columns {c0 + 1} to {c1}"
                name = f"Chart {_letter(number)}" if self._letters else f"Chart {number + 1}"
                lines.append(f"{name} ({rows}, {columns}):")
                lines += ["  " + line for line in describe_chart(chart).splitlines()]
        text = "\n".join(lines)
        print(text)
        return text

    def _page_size(self):
        s = self._settings
        if s["size_set"]:
            return s["width"], s["height"]
        # each cell gets about 3/4 of its chart's own size (8 x 6 -> 6 x 4.5)
        w = max(c._settings["width"] for c in self._charts) * 0.75
        h = max(c._settings["height"] for c in self._charts) * 0.75
        return min(w * self._columns, 20.0), min(h * self._rows + (0.5 if s["title"] else 0), 20.0)

    def _render(self):
        s = self._settings
        with chart_notes(), _style.context(s):
            for chart in self._charts:
                chart._left_out_rows()
            fig = Figure(figsize=self._page_size(), layout="constrained")
            # each chart gets its own sub-figure on a grid (Figure.subfigures does the same for equal cells); a
            # chart in several cells spans them (GridSpec slices), widths= and heights= are the grid's ratios
            grid = GridSpec(self._rows, self._columns, figure=fig, width_ratios=self._widths,
                            height_ratios=self._heights, left=0, right=1, bottom=0, top=1)
            panels = []
            for number, (chart, r0, r1, c0, c1) in enumerate(self._cells):
                cell = fig.add_subfigure(grid[r0:r1, c0:c1])
                look = dict(chart._settings)
                if s["style_set"]:
                    look["style"] = s["style"]
                own_style = chart._settings.get("style")
                chart._settings["style"] = look["style"]  # the page's style is drawn as the chart's own (patterns)
                try:
                    with _style.context(look):
                        cell.set_facecolor(matplotlib.rcParams["figure.facecolor"])
                        drawn = _draw_chart(chart, cell)
                finally:
                    chart._settings["style"] = own_style
                with _style.context(look):
                    if self._letters and drawn:  # A, B, C ... at the top left, as in papers
                        _put_letter(cell, drawn, _letter(number))
                    panels.extend(ax for ax in drawn if ax.name == "rectilinear")
            if self._same_x:
                _share(panels, "x")
            if self._same_y:
                _share(panels, "y")
            if self._one_legend:
                _one_legend(fig, [cell[0] for cell in self._cells])
            if s["title"]:
                fig.suptitle(s["title"], fontweight="bold", fontsize=matplotlib.rcParams["axes.titlesize"] * 1.15)
        return fig  # not cached: the charts on the page may still change

    def _save_animation(self, path, resolution=100):
        raise SimplydataError("A page of charts cannot be saved as .gif. Save it as .png or .pdf instead.")

    def __repr__(self):
        return f"<simplydata page: {len(self._charts)} charts, {self._how}>"


def _handle_look(handle) -> tuple:
    """What a legend entry shows: the kind of mark, its colours, line style, dot shape and pattern."""
    from matplotlib.colors import to_hex

    def hexed(colour):
        try:
            import numpy as np

            array = np.asarray(colour, dtype=float)
            if array.ndim == 2:
                array = array[0] if len(array) else None
            return "" if array is None else to_hex(array, keep_alpha=True)
        except (TypeError, ValueError):
            return str(colour)

    if handle is None:
        return ("none",)
    if hasattr(handle, "get_marker") and hasattr(handle, "get_linestyle"):  # a line, or a dot drawn as a line
        return ("line", hexed(handle.get_color()), str(handle.get_linestyle()), str(handle.get_marker()),
                hexed(handle.get_markerfacecolor()), hexed(handle.get_markeredgecolor()))
    if hasattr(handle, "get_paths") and hasattr(handle, "get_offsets"):  # a dot (scatter)
        paths = handle.get_paths()
        shape = tuple(map(tuple, paths[0].vertices.round(3))) if len(paths) else ()
        return ("dot", hexed(handle.get_facecolors()), hexed(handle.get_edgecolors()), shape,
                str(handle.get_hatch()))
    return ("box", hexed(handle.get_facecolor()), str(getattr(handle, "get_hatch", lambda: None)()),
            str(getattr(handle, "get_linestyle", lambda: None)()))


def _one_legend(fig, charts):
    """with_one_legend=True: one legend for the page (matplotlib Figure.legend) at its right; the charts' own
    legends are taken away. Only when every chart with a legend shows the same one: the same name, the same
    groups in the same order, drawn the same way (colour, shape, dashes, pattern). Otherwise it stops and says
    which chart differs, so a shared legend can never be wrong for one of the charts."""
    from .._numbers_drawn import _all_axes

    found = []
    for number, sub in enumerate(fig.subfigs, start=1):
        legends = list(sub.legends) + [ax.get_legend() for ax in _all_axes(sub) if ax.get_legend() is not None]
        handles, labels, title = [], [], ""
        for legend in legends:
            title = title or legend.get_title().get_text()
            for h, text in zip(legend.legend_handles, legend.get_texts()):
                label = text.get_text()
                if label.endswith(":") and not title:  # "class:" in front of a one-row legend is its name
                    title = label[:-1]
                elif label and not label.startswith("_") and label not in labels:
                    handles.append(h)
                    labels.append(label)
        if labels:
            found.append((number, title, labels, [_handle_look(h) for h in handles], handles, legends))
    if not found:
        return
    first = found[0]
    for number, title, labels, looks, _, _ in found[1:]:
        if title != first[1]:
            what = f'another legend name ("{title}" against "{first[1]}")'
        elif labels != first[2]:
            what = f"other groups ({', '.join(labels)} against {', '.join(first[2])})"
        elif looks != first[3]:
            what = "its groups drawn another way (colour, kind of mark, shape, dashes or pattern)"
        else:
            continue
        raise SimplydataError(
            f"with_one_legend=True needs the same legend on every chart, but chart {number} shows {what} "
            f"than chart {first[0]}.\nLeave out with_one_legend=True to keep each chart's own legend.")
    for *_, legends in found:
        for legend in legends:
            legend.remove()
    fig.legend(first[4], first[2], loc="outside center right", title=first[1] or None)


def _share(axes, which):
    """Give all panels the same x or y range, wide enough for every panel's data."""
    if len(axes) < 2:
        return
    lims = [a.get_xlim() if which == "x" else a.get_ylim() for a in axes]
    low, high = min(min(lim) for lim in lims), max(max(lim) for lim in lims)
    for ax, lim in zip(axes, lims):  # a flipped axis stays flipped
        (ax.set_xlim if which == "x" else ax.set_ylim)(*((low, high) if lim[0] <= lim[1] else (high, low)))


def _put_letter(cell, panels, letter):
    """Write the panel letter at the top left of one chart on a page.

    A chart with one panel gets it as the panel's left title. A chart split into panels
    (draw_one_chart_for_each_group_in) already has a title centred on each panel, so the letter goes on its own
    line above the panels, at the left of the chart, where it cannot cover a panel title.
    """
    size = matplotlib.rcParams["axes.titlesize"] * 1.2
    if len(panels) == 1:
        panels[0].set_title(letter, loc="left", fontweight="bold", fontsize=size).simplydata_part = "panel letter"
        return
    sup = getattr(cell, "_suptitle", None)
    if sup is not None and sup.get_visible() and sup.get_text():  # write_title_on_top of the chart: same line
        x, y = sup.get_position()
        written = cell.text(0.01, y, letter, ha="left", va=sup.get_va(), fontweight="bold", fontsize=size,
                            transform=cell.transSubfigure)
    else:
        written = cell.suptitle(letter, x=0.01, ha="left", fontweight="bold", fontsize=size)
    written.simplydata_part = "panel letter"


def _letter(number):
    """A, B, C ... Z, then AA, AB ... for very big pages."""
    letters = ""
    number += 1
    while number:
        number, rest = divmod(number - 1, 26)
        letters = chr(ord("A") + rest) + letters
    return letters


def _page_charts(step, charts):
    if len(charts) == 1 and isinstance(charts[0], (list, tuple)):
        charts = tuple(charts[0])
    if not charts:
        raise SimplydataError(f"sdata.{step}() needs some charts, for example sdata.{step}(chart_a, chart_b).")
    for i, c in enumerate(charts, start=1):
        if isinstance(c, Page):
            raise SimplydataError(
                f"Chart {i} given to sdata.{step}() is already a page of charts.\n"
                "Give the single charts instead, for example sdata.put_in_rows_and_columns(a, b, c, d, per_row=2)."
            )
        if not isinstance(c, BaseChart):
            raise SimplydataError(
                f"sdata.{step}() needs charts made with sdata.chart(...), but number {i} is {type(c).__name__}."
            )
    return charts


def _check_page_options(step, same_x, same_y, letters=False, one_legend=False):
    _check_bool(step, "same_x", same_x)
    _check_bool(step, "same_y", same_y)
    _check_bool(step, "letters", letters)
    _check_bool(step, "with_one_legend", one_legend)


@friendly(renamed={"letters": "with_letters"})
def put_side_by_side(*charts, same_x=False, same_y=False, with_letters=False, with_one_legend=False):
    """Charts next to each other. sdata.put_side_by_side(a, b).save("both.png")

    same_y=True gives them all the same y range, so heights can be compared.
    with_letters=True writes A, B, C ... at the top left of each chart, as in papers.
    with_one_legend=True shows one legend for the whole page, when the charts have the same groups.
    """
    charts = _page_charts("put_side_by_side", charts)
    _check_page_options("put_side_by_side", same_x, same_y, with_letters, with_one_legend)
    return Page(charts, 1, len(charts), same_x, same_y, how="side by side", letters=with_letters,
                one_legend=with_one_legend)


@friendly(renamed={"letters": "with_letters"})
def put_one_above_other(*charts, same_x=False, same_y=False, with_letters=False, with_one_legend=False):
    """Charts on top of each other. sdata.put_one_above_other(a, b).save("both.png")

    same_x=True gives them all the same x range, which suits time series.
    with_letters=True writes A, B, C ... at the top left of each chart, as in papers.
    with_one_legend=True shows one legend for the whole page, when the charts have the same groups.
    """
    charts = _page_charts("put_one_above_other", charts)
    _check_page_options("put_one_above_other", same_x, same_y, with_letters, with_one_legend)
    return Page(charts, len(charts), 1, same_x, same_y, how="one above the other", letters=with_letters,
                one_legend=with_one_legend)


def _is_layout(charts) -> bool:
    """put_in_rows_and_columns([[a, a], [b, c]]): a list of rows, each a list of charts."""
    rows = charts[0] if len(charts) == 1 and isinstance(charts[0], (list, tuple)) else charts
    return bool(rows) and all(isinstance(row, (list, tuple)) for row in rows)


def _cells_of(rows):
    """The cells of each chart in a list of rows: [(chart, first row, last row + 1, first column, last column + 1)]
    in the order the charts first appear. A chart in several cells spans them; None leaves a cell empty."""
    example = "for example sdata.put_in_rows_and_columns([[a, a], [b, c]])"
    rows = [list(row) for row in rows]
    columns = len(rows[0])
    if not columns or any(len(row) != columns for row in rows):
        raise SimplydataError(f"Each row needs the same number of places (use None for an empty place), {example}.")
    places = {}
    for r, row in enumerate(rows):
        for c, chart in enumerate(row):
            if chart is None:
                continue
            _page_charts("put_in_rows_and_columns", (chart,))
            places.setdefault(id(chart), (chart, []))[1].append((r, c))
    if not places:
        raise SimplydataError(f"sdata.put_in_rows_and_columns() needs some charts in the rows, {example}.")
    cells = []
    for chart, spots in places.values():
        found_rows = sorted({r for r, _ in spots})
        found_columns = sorted({c for _, c in spots})
        r0, r1, c0, c1 = found_rows[0], found_rows[-1] + 1, found_columns[0], found_columns[-1] + 1
        if len(spots) != (r1 - r0) * (c1 - c0):
            raise SimplydataError(
                "A chart that spans several places needs a full rectangle of them (side by side, or one under "
                f"the other, or both), {example}: chart a fills the whole first row.")
        cells.append((chart, r0, r1, c0, c1))
    return cells, len(rows), columns


def _check_ratios(name, values, count, what):
    if values is None:
        return None
    if isinstance(values, (str, bytes)) or not is_listlike(values) or len(values) != count:
        raise SimplydataError(f"{name}= needs one number for each {what} ({count}), for example "
                              f"{name}=[{', '.join(['2'] + ['1'] * (count - 1))}].")
    for v in values:
        if isinstance(v, bool) or not isinstance(v, numbers.Real) or not v > 0:
            raise SimplydataError(f"{name}= needs numbers bigger than 0, not {v!r}.")
    return [float(v) for v in values]


@friendly(renamed={"columns": "per_row", "letters": "with_letters"})
def put_in_rows_and_columns(*charts, per_row=None, same_x=False, same_y=False, with_letters=False, widths=None,
                            heights=None, with_one_legend=False):
    """Charts in rows and columns. sdata.put_in_rows_and_columns(a, b, c, d, per_row=2)

    per_row=2 (normal) puts 2 charts in each row.
    Or give the rows as lists: sdata.put_in_rows_and_columns([[a, a], [b, c]]) puts chart a across the
    whole first row and b and c under it; a chart named in several places spans them, and None leaves a
    place empty.
    widths=[2, 1] makes the first column twice as wide as the second; heights=[2, 1] does the same for rows.
    with_letters=True writes A, B, C ... at the top left of each chart, as figures in papers do.
    with_one_legend=True shows one legend for the whole page, when the charts have the same groups.
    """
    _check_page_options("put_in_rows_and_columns", same_x, same_y, with_letters, with_one_legend)
    if _is_layout(charts):
        if per_row is not None:
            raise SimplydataError("The rows you give already say how many charts go in each row; leave out "
                                  "per_row=, for example sdata.put_in_rows_and_columns([[a, a], [b, c]]).")
        rows = charts[0] if len(charts) == 1 and isinstance(charts[0], (list, tuple)) and \
            all(isinstance(r, (list, tuple)) for r in charts[0]) else charts
        cells, n_rows, n_columns = _cells_of(rows)
        return Page([cell[0] for cell in cells], n_rows, n_columns, same_x, same_y,
                    how=f"{n_rows} rows and {n_columns} columns", letters=with_letters, cells=cells,
                    widths=_check_ratios("widths", widths, n_columns, "column"),
                    heights=_check_ratios("heights", heights, n_rows, "row"), one_legend=with_one_legend)
    charts = _page_charts("grid", charts)
    per_row = 2 if per_row is None else per_row
    if isinstance(per_row, bool) or not isinstance(per_row, int) or per_row < 1:
        raise SimplydataError(f"per_row= should be a whole number such as 2 or 3, not {per_row!r}.")
    columns = min(per_row, len(charts))
    rows = math.ceil(len(charts) / columns)
    return Page(charts, rows, columns, same_x, same_y,
                how=f"grid of {columns} columns", letters=with_letters,
                widths=_check_ratios("widths", widths, columns, "column"),
                heights=_check_ratios("heights", heights, rows, "row"), one_legend=with_one_legend)
