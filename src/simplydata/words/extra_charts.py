"""More chart words (charts phase, batch 3; approved by Manish on 2026-11-25).

A broken y-axis, other axis scales (square root, logit, asinh; a log scale through zero is an option of
use_log_scale_y), the colour behind the plot area, hexagon bins, time bars, rectangles and circles, residual dots,
event lines and 3D bars. The side histograms can be drawn as density curves (drawn_as="density").

Everything is passed through to matplotlib or seaborn (PLAN.md section 7): hexagons are matplotlib's hexbin,
residuals seaborn's residplot, a broken axis is the "broken axis" layout of the matplotlib gallery (two panels
sharing x), time bars are matplotlib's barh with left=. simplydata only chooses the starting values and checks the
input. A web page (chart.save("x.html")) cannot show a broken axis or the other scales: those are refused there
with one sentence (simplydata._web).
"""

from __future__ import annotations

from .._typing import _Same

import numbers

import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns

from .._core import chart_note
from .._data import is_listlike
from .._errors import SimplydataError, friendly
from . import second_cues as cues
from ._helpers import check, check_thickness, check_transparency, colour_role, default_colour, opacity, palette_for

OTHER_SCALES = ("square root", "logit", "asinh")
SIDE_KINDS = ("bars", "density")
HEXAGONS_ACROSS = 20  # draw_hexagon_bins(with_bins=20): about 20 hexagons across the x range
TIME_BAR_HEIGHT = 0.8  # the height of a time bar, as a share of the space for its row
EVENT_LINE_LENGTH = 0.8
BAR_3D_WIDTH = 0.8  # a 3D bar is this share of the smallest gap between two places
RECTANGLE_SEE_THROUGH = 0.75  # a rectangle or circle is filled see-through, so the marks under it still show


def _is_number(value) -> bool:
    return not isinstance(value, bool) and isinstance(value, numbers.Real) and np.isfinite(value)


def _is_place(value) -> bool:
    """A number or a date: a place on an axis."""
    return _is_number(value) or hasattr(value, "year") or isinstance(value, np.datetime64)


def _check_colour_name(word, colour):
    if colour is not None and not (isinstance(colour, str) and matplotlib.colors.is_color_like(colour)):
        raise SimplydataError(f'.{word}() needs one colour name for colour=, such as "red", not {colour!r}.')


# ====================================================================== broken y-axis
def render_broken(chart, fig):
    """break_between_y(low, high): the matplotlib gallery's "broken axis" layout. The chart is drawn twice, on two
    panels that share x: the lower one shows up to `low`, the upper one from `high`; the edges between them are
    hidden and marked with short slanted lines. Nothing is worked out: each panel is the same drawing, cut."""
    low, high = chart._settings["y_break"]
    top, bottom = fig.subplots(2, 1, sharex=True)
    for ax in (top, bottom):
        ctx = chart._draw_panel(fig, ax, axes=[top, bottom])
    below, above = bottom.get_ylim(), top.get_ylim()
    if min(below) >= low:
        raise SimplydataError(f".break_between_y({low:g}, {high:g}): nothing is drawn below {low:g}, so the lower part "
                              "would be empty. Choose a lower first number.")
    if max(above) <= high:
        raise SimplydataError(f".break_between_y({low:g}, {high:g}): nothing is drawn above {high:g}, so the upper part "
                              "would be empty. Choose a smaller second number.")
    bottom.set_ylim(min(below), low)
    top.set_ylim(high, max(above))
    top.spines["bottom"].set_visible(False)
    bottom.spines["top"].set_visible(False)
    top.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
    top.set_xlabel("")
    bottom.set_title("")
    top.set_ylabel("")
    if top.get_legend() is not None and bottom.get_legend() is not None:
        bottom.get_legend().remove()
    slant = dict(marker=[(-1, -0.5), (1, 0.5)], markersize=12, linestyle="none",
                 color=matplotlib.rcParams["axes.edgecolor"], mec=matplotlib.rcParams["axes.edgecolor"], mew=1,
                 clip_on=False)
    for ax, y in ((top, 0), (bottom, 1)):
        (mark,) = ax.plot([0, 1], [y, y], transform=ax.transAxes, **slant)
        mark.simplydata_decoration = True  # not data: get_numbers_drawn() leaves it out
    line = ("Note: a broken y-axis makes values on the two sides look closer than they are; say in the caption that "
            f"the part from {low:g} to {high:g} is left out.")
    chart_note(line, lambda _count, line=line: line)
    return [top, bottom], ctx


# ====================================================================== other scales
def _set_other_scale(ctx, axis, scale):
    """use_scale_y("square root" / "logit" / "asinh"): matplotlib's function, logit and asinh scales."""
    from .axes import _values_on

    ax = ctx.ax
    axis_obj = ax.xaxis if axis == "x" else ax.yaxis
    values, name = _values_on(ctx, axis)
    if values is not None:
        values = values[~np.isnan(values)]
        if scale == "square root" and (values < 0).any():
            raise SimplydataError(f'.use_scale_{axis}("square root") cannot show numbers below 0, and "{name}" has '
                                  f"{int((values < 0).sum())} of them. Remove them first, or use "
                                  f"use_log_scale_{axis}(through_zero=True).")
        if scale == "logit" and ((values <= 0) | (values >= 1)).any():
            raise SimplydataError(f'.use_scale_{axis}("logit") shows shares between 0 and 1 (not 0 or 1 '
                                  f'themselves), and "{name}" has values outside that.')
    setter = ax.set_xscale if axis == "x" else ax.set_yscale
    if scale == "square root":
        low, high = sorted(ax.get_xlim() if axis == "x" else ax.get_ylim())
        setter("function", functions=(lambda v: np.sqrt(np.clip(v, 0, None)), np.square))
        (ax.set_xlim if axis == "x" else ax.set_ylim)(max(low, 0), high)
    else:
        setter(scale)
    axis_obj.simplydata_scale = scale  # read back by get_scales_drawn() as "square root" rather than "function"


# ====================================================================== background
def _background(ctx, colour):
    ctx.ax.set_facecolor(colour)


# ====================================================================== hexagon bins
def _draw_hexagon_bins(ctx, x, y, bins, transparency=None):
    """matplotlib hexbin: the dots counted in hexagons; hexagons with no dots are not drawn (mincnt=1)."""
    from . import _colour_scale as scales
    from .charts import _colour_bar, _frame, _remember

    table, n = _frame(ctx, x=x, y=y)
    rows = table[[n["x"], n["y"]]].apply(pd.to_numeric, errors="coerce").dropna()
    if not len(rows):
        raise SimplydataError(".draw_hexagon_bins() found no rows with numbers in both columns.")
    cmap = ((ctx.settings["colour_scale"]["map"] if scales.wanted(ctx.settings) else None)
            or cues.colour_map(ctx))
    hexagons = ctx.ax.hexbin(rows[n["x"]].to_numpy(float), rows[n["y"]].to_numpy(float), gridsize=bins, mincnt=1,
                             cmap=cmap, linewidths=0.2, edgecolors="face", alpha=opacity(transparency))
    ctx.ax.set_xlabel(n["x"])
    ctx.ax.set_ylabel(n["y"])
    _colour_bar(ctx, hexagons, "count")
    _remember(ctx, "hexagon_bins", table, n)


# ====================================================================== side densities
def side_densities(ctx, top, right, groups, x, y, many):
    """draw_side_histograms(drawn_as="density"): seaborn kdeplot on the two edges, one curve per group."""
    for _, part, colour in groups:
        kw = (dict(color=colour, fill=False, linewidth=1.5) if many
              else dict(color=colour, fill=True, alpha=0.8, linewidth=0))
        values_x = part[x].dropna().to_numpy(dtype=float)
        values_y = part[y].dropna().to_numpy(dtype=float)
        if len(np.unique(values_x)) > 1:
            sns.kdeplot(x=values_x, ax=top, **kw)
        if len(np.unique(values_y)) > 1:
            sns.kdeplot(y=values_y, ax=right, **kw)
    for side in (top, right):
        side.set_xlabel("")
        side.set_ylabel("")


# ====================================================================== time bars
def _draw_time_bars(ctx, start, end, y, colour, transparency=None):
    """matplotlib barh with left=: one bar from start to end on the row of each name, the first row at the top."""
    from .charts import _frame, _hue, _remember

    group, fixed = colour_role(ctx.data, colour)
    table, n = _frame(ctx, on_x=None, on_y="y", start=start, end=end, y=y, colour=group)
    rows = table.dropna(subset=[n["start"], n["end"], n["y"]])
    if not len(rows):
        raise SimplydataError(".draw_time_bars() found no rows with a start, an end and a name.")
    ax = ctx.ax
    names = [str(v) for v in pd.unique(rows[n["y"]])]
    ax.yaxis.update_units(np.array(names, dtype=object))  # the rows in the order of the table
    groups = [(None, rows)] if not n["colour"] else [(g, rows[rows[n["colour"]] == g])
                                                     for g in _hue(rows, n).get("hue_order") or
                                                     pd.unique(rows[n["colour"]].dropna())]
    colours = (palette_for(rows, n["colour"], ctx.settings) if n["colour"]
               else [default_colour(ctx.settings, fixed)])
    bw = cues.in_black_and_white(ctx)
    for i, ((name, part), shade) in enumerate(zip(groups, colours)):
        bars = ax.barh(part[n["y"]].astype(str).to_numpy(dtype=object), part[n["end"]] - part[n["start"]],
                       left=part[n["start"]], height=TIME_BAR_HEIGHT, color=shade, alpha=opacity(transparency),
                       label=None if name is None else str(name),
                       edgecolor=matplotlib.rcParams["axes.edgecolor"] if bw else None,
                       linewidth=0.6 if bw else 0)
        if bw and n["colour"]:
            for patch in bars.patches:
                cues.hatch(patch, cues.HATCHES[i % len(cues.HATCHES)])
    if not ax.yaxis_inverted():
        ax.invert_yaxis()  # the first row of the table at the top, as in a plan
    if isinstance(y, str):  # columns name the axes; lists of values leave them for label_x / label_y
        ax.set_ylabel(n["y"])
    if isinstance(start, str) and isinstance(end, str):
        ax.set_xlabel(f"{n['start']} to {n['end']}")
    if n["colour"]:
        ax.legend(title=n["colour"])
    _remember(ctx, "time_bars", rows, n, start=n["start"], end=n["end"])


# ====================================================================== rectangles and circles
def _shape_colours(ctx, colour, transparency, hollow):
    shade = colour or ("grey" if cues.in_black_and_white(ctx) else default_colour(ctx.settings))
    alpha = 1 - (RECTANGLE_SEE_THROUGH if transparency is None else transparency)
    face = "none" if hollow else matplotlib.colors.to_rgba(shade, alpha)
    return dict(facecolor=face, edgecolor=shade, linewidth=1.5, zorder=2.2)


def _axis_number(ax, axis, value):
    """A date given for a place on a date axis becomes matplotlib's number for it (the axis's own converter)."""
    axis_obj = ax.xaxis if axis == "x" else ax.yaxis
    if _is_number(value):
        return float(value)
    return float(axis_obj.convert_units(value))


def _draw_rectangle(ctx, x_between, y_between, colour, transparency, hollow):
    """matplotlib patches.Rectangle, added with add_patch."""
    from matplotlib.patches import Rectangle

    ax = ctx.ax
    x0, x1 = (_axis_number(ax, "x", v) for v in x_between)
    y0, y1 = (_axis_number(ax, "y", v) for v in y_between)
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, **_shape_colours(ctx, colour, transparency, hollow)))
    ax.autoscale_view()


def _draw_circle(ctx, centre, radius, colour, transparency, hollow):
    """matplotlib patches.Circle, added with add_patch (the radius in the units of the axes)."""
    from matplotlib.patches import Circle

    ax = ctx.ax
    ax.add_patch(Circle((float(centre[0]), float(centre[1])), float(radius),
                        **_shape_colours(ctx, colour, transparency, hollow)))
    ax.autoscale_view()


# ====================================================================== residual dots, event lines
def _draw_residual_dots(ctx, x, y, colour, transparency=None):
    """seaborn residplot: what is left of y after a straight line on x, as dots, with a line at 0."""
    from .charts import _frame, _remember

    _, fixed = colour_role(ctx.data, colour)
    table, n = _frame(ctx, x=x, y=y)
    kw = dict(data=table, x=n["x"], y=n["y"], ax=ctx.ax, color=default_colour(ctx.settings, fixed))
    if transparency is not None:
        kw["scatter_kws"] = {"alpha": opacity(transparency)}
    sns.residplot(**kw)
    ctx.ax.set_ylabel(f"residual of {n['y']}")
    _remember(ctx, "residual_dots", table, n)


def _draw_event_lines(ctx, x, y, colour, thickness=None):
    """matplotlib eventplot: a short upright line at each value; with y= one row of lines for each group."""
    from .charts import _frame, _remember

    group, fixed = colour_role(ctx.data, colour)
    table, n = _frame(ctx, on_y="y", x=x, y=y, colour=group)
    ax = ctx.ax
    if n["y"] is None:
        names = [None]
        positions = [table[n["x"]].dropna().to_numpy()]
    else:
        names = [g for g in pd.unique(table[n["y"]].dropna())]
        positions = [table.loc[table[n["y"]] == g, n["x"]].dropna().to_numpy() for g in names]
    if n["colour"] and n["colour"] != n["y"]:
        raise SimplydataError(".draw_event_lines() colours the rows of y=; give colour= the same column as y=, or "
                              "one colour name.")
    if n["colour"]:
        colours = palette_for(table, n["y"], ctx.settings)
    else:
        colours = [default_colour(ctx.settings, fixed)] * len(names)
    ax.eventplot(positions, lineoffsets=list(range(len(names))), linelengths=EVENT_LINE_LENGTH, colors=colours,
                 linewidths=1.5 if thickness is None else thickness)
    if n["y"] is not None:
        ax.set_yticks(range(len(names)), labels=[str(g) for g in names])
        ax.set_ylabel(n["y"])
    else:
        ax.set_yticks([])
    ax.set_xlabel(n["x"])
    _remember(ctx, "event_lines", table, n)


# ====================================================================== 3D bars
def _places(values):
    """The places of a column along a 3D axis: numbers as they are; names at 0, 1, 2 ... (with the names)."""
    if pd.api.types.is_numeric_dtype(values) and not pd.api.types.is_bool_dtype(values):
        return values.to_numpy(dtype=float), None
    names = [str(v) for v in pd.unique(values.dropna())]
    where = {name: i for i, name in enumerate(names)}
    return values.astype(str).map(where).to_numpy(dtype=float), names


def _gap(places):
    unique = np.unique(places[np.isfinite(places)])
    return float(np.min(np.diff(unique))) if len(unique) > 1 else 1.0


def _draw_bars_3d(ctx, x, y, z, colour, transparency=None):
    """matplotlib Axes3D.bar3d: one bar for each row, standing on 0 at its x and y."""
    from .charts import _frame, _remember

    _, fixed = colour_role(ctx.data, colour)
    table, n = _frame(ctx, x=x, y=y, z=z)
    rows = table.dropna(subset=[n["x"], n["y"], n["z"]])
    if rows.duplicated(subset=[n["x"], n["y"]]).any():
        raise SimplydataError(f'.draw_bars_3d() draws one bar for each place, but some places ({n["x"]} and '
                              f'{n["y"]}) have more than one row. Find one number for each first, for example with '
                              f'table.find_total_of("{n["z"]}", for_each_group_in=["{n["x"]}", "{n["y"]}"]).')
    xs, x_names = _places(rows[n["x"]])
    ys, y_names = _places(rows[n["y"]])
    heights = rows[n["z"]].to_numpy(dtype=float)
    width, depth = BAR_3D_WIDTH * _gap(xs), BAR_3D_WIDTH * _gap(ys)
    ax = ctx.ax
    shade = default_colour(ctx.settings, fixed)
    bars = ax.bar3d(xs - width / 2, ys - depth / 2, np.zeros(len(heights)), width, depth, heights, color=shade,
                    alpha=opacity(transparency), shade=True)
    bars.simplydata_bars_3d = len(heights)  # read back as bars by get_numbers_drawn(), six faces each
    for axis, names, label in ((ax.xaxis, x_names, n["x"]), (ax.yaxis, y_names, n["y"])):
        if names is not None:
            axis.set_ticks(range(len(names)), labels=names)
    ax.set_xlabel(n["x"])
    ax.set_ylabel(n["y"])
    ax.set_zlabel(n["z"])
    line = ("Note: 3D bars hide each other and their heights are hard to read from the side; a heat map "
            "(chart.draw_heatmap) shows the same numbers more plainly.")
    chart_note(line, lambda _count, line=line: line)
    _remember(ctx, "bars_3d", rows, n)


# ====================================================================== the words
class ExtraChartWords:
    """Chart words of the charts phase, batch 3."""

    # -------------------------------------------------------------- axes
    @friendly
    def break_between_y(self: _Same, low, high) -> _Same:
        """Leave out the part of the y-axis between two values, with break marks.
        chart.break_between_y(5, 50) (with chart.draw_bars(x="class", y="marks") on sdata.get_example("marks"))

        The chart is drawn on two panels that share the x-axis: the lower one up to low, the upper one
        from high. Use it when one value is far above the others; say in the caption what is left out.
        Pictures only: a web page (.html) cannot break an axis.
        """
        example = "chart.break_between_y(50, 500)"
        for name, value in (("low", low), ("high", high)):
            if not _is_number(value):
                raise SimplydataError(f".break_between_y() needs two numbers, but {name} is {value!r}.\n"
                                      f"For example {example}")
        if not low < high:
            raise SimplydataError(f".break_between_y({low!r}, {high!r}): the low end comes first, and the two must "
                                  f"differ.\nWrite chart.break_between_y({high!r}, {low!r}).")
        if self._settings.get("projection") is not None or self._settings.get("split"):
            raise SimplydataError(".break_between_y() works on a flat chart with one panel, not on round or 3D charts "
                                  "or charts split into panels.")
        return self._set(y_break=(float(low), float(high)))

    def _scale_word(self, axis, scale):
        word = f"use_scale_{axis}"
        if isinstance(scale, str) and scale.strip().lower() in OTHER_SCALES:
            scale = scale.strip().lower()
        elif isinstance(scale, str) and scale.strip().lower() in ("log", "logarithmic"):
            raise SimplydataError(f"For a log scale, use chart.use_log_scale_{axis}() (and through_zero=True for "
                                  "a log scale that also shows 0 and numbers below it).")
        self._check_choice(word, "scale", scale, OTHER_SCALES)
        self._remember_for_undo(word)
        # one scale for an axis: this one replaces a log scale
        self._steps = [s for s in self._steps if s.name not in (f"log_scale_{axis}", f"log_scale_{axis}_check")]
        return self._replace(f"scale_{axis}", "axes", _set_other_scale, axis=axis, scale=scale)

    @friendly
    def use_scale_x(self: _Same, scale) -> _Same:
        """Another scale on the x-axis: "square root", "logit" or "asinh". chart.use_scale_x("square root")
        (with chart.draw_dots(x="hours", y="marks") on sdata.get_example("marks"))

        "square root" spreads out small numbers (counts); "logit" spreads out shares near 0 and 1;
        "asinh" is like a log scale that also shows 0 and numbers below it. Pictures only.
        """
        return self._scale_word("x", scale)

    @friendly
    def use_scale_y(self: _Same, scale) -> _Same:
        """Another scale on the y-axis: "square root", "logit" or "asinh". chart.use_scale_y("square root")
        (with chart.draw_dots(x="hours", y="marks") on sdata.get_example("marks"))

        "square root" spreads out small numbers (counts); "logit" spreads out shares near 0 and 1;
        "asinh" is like a log scale that also shows 0 and numbers below it. Pictures only.
        """
        return self._scale_word("y", scale)

    @friendly
    def use_background_colour(self: _Same, colour) -> _Same:
        """The colour behind the plot area. chart.use_background_colour("ivory")
        (with chart.draw_dots(x="hours", y="marks") on sdata.get_example("marks"))

        Any colour name or code ("#f5f5f0"); the page around the chart stays white. A web page uses it too.
        """
        if not (isinstance(colour, str) and matplotlib.colors.is_color_like(colour)):
            raise SimplydataError(f'.use_background_colour() needs a colour name, such as "ivory" or "#f5f5f0", not '
                                  f"{colour!r}.")
        return self._replace("background_colour", "axes", _background, colour=colour)

    use_background_color = use_background_colour  # American spelling, same word

    # -------------------------------------------------------------- chart types
    @friendly(others={"gridsize": "with_bins"})
    def draw_hexagon_bins(self: _Same, x=None, y=None, with_bins=HEXAGONS_ACROSS, transparency=None) -> _Same:
        """Many dots counted in hexagons: the darker, the more dots. chart.draw_hexagon_bins(x="hours", y="height")
        (with sdata.get_example("marks"))

        with_bins=20 makes about 20 hexagons across; hexagons with no dots are left out. A colour bar
        says how many dots each colour stands for. Use it when dots would cover each other.
        """
        transparency = check_transparency("draw_hexagon_bins", transparency)
        if x is None or y is None:
            raise SimplydataError('.draw_hexagon_bins() needs x= and y=, for example '
                                  'chart.draw_hexagon_bins(x="hours", y="height").')
        if isinstance(with_bins, bool) or not isinstance(with_bins, (int, np.integer)) or not 3 <= with_bins <= 200:
            raise SimplydataError(f"with_bins= in .draw_hexagon_bins() is how many hexagons go across, a whole number "
                                  f"from 3 to 200 such as with_bins=20, not {with_bins!r}.")
        check(self._data, x=x, y=y)
        from .charts import _check_numbers

        _check_numbers(self._data, "draw_hexagon_bins", x=x, y=y)
        self._need_axes("draw_hexagon_bins")
        return self._add("draw_hexagon_bins", "draw", _draw_hexagon_bins, x=x, y=y, bins=int(with_bins),
                         transparency=transparency)

    @friendly(others={"begin": "start", "finish": "end", "stop": "end"})
    def draw_time_bars(self: _Same, start=None, end=None, y=None, colour=None, transparency=None) -> _Same:
        """A bar from a start to an end on each row, as in a plan or a timeline.
        chart.draw_time_bars(start=[1, 3, 6], end=[4, 7, 9], y=["plan", "build", "test"])

        start= and end= are columns of dates (or numbers), or lists; y= names the row each bar goes on
        (the first row of the table at the top). Several bars can share a row. colour="ship" gives each
        group its own colour, or colour="teal" one colour.
        """
        transparency = check_transparency("draw_time_bars", transparency)
        if start is None or end is None or y is None:
            raise SimplydataError('.draw_time_bars() needs start=, end= and y=, for example '
                                  'chart.draw_time_bars(start="start", end="end", y="task").')
        group, _ = colour_role(self._data, colour)
        check(self._data, start=start, end=end, y=y, colour=group)
        data = self._data
        if isinstance(start, str) and isinstance(end, str):
            first, last = data[start], data[end]
            dates = [pd.api.types.is_datetime64_any_dtype(c) for c in (first, last)]
            numbers_ = [pd.api.types.is_numeric_dtype(c) and not pd.api.types.is_bool_dtype(c) for c in (first, last)]
            if not (all(dates) or all(numbers_)):
                raise SimplydataError(f'.draw_time_bars() needs start= and end= both dates or both numbers, but "{start}" '
                                      f'and "{end}" are not. Turn text into dates first with '
                                      f'table.turn_into_dates("{start}").')
            backwards = int((last < first).sum())
            if backwards:
                raise SimplydataError(f'.draw_time_bars(): {backwards} row{"s" if backwards != 1 else ""} end before '
                                      f'{"they start" if backwards != 1 else "it starts"} ("{end}" is before '
                                      f'"{start}"). Fix or remove those rows first.')
        self._need_axes("draw_time_bars")
        return self._add("draw_time_bars", "draw", _draw_time_bars, start=start, end=end, y=y, colour=colour,
                         transparency=transparency)

    def _between(self, word, name, between, example):
        if between is None or isinstance(between, (str, bytes)) or not is_listlike(between) or len(between) != 2:
            raise SimplydataError(f".{word}() needs {name}=[low, high], two numbers, not {between!r}.\n"
                                  f"For example chart.{example}")
        low, high = between
        if not (_is_place(low) and _is_place(high)):
            raise SimplydataError(f".{word}() needs numbers (or dates) in {name}=, not {between!r}.\n"
                                  f"For example chart.{example}")
        try:
            wrong = not low < high
        except TypeError:
            raise SimplydataError(f".{word}() needs both ends of {name}= of the same kind.") from None
        if wrong:
            raise SimplydataError(f".{word}({name}=[{low!r}, {high!r}]): the low end comes first, and the two must "
                                  "differ.")
        return [low, high]

    @friendly
    def draw_rectangle(self: _Same, x_between=None, y_between=None, colour=None, transparency=None,
                       hollow=False) -> _Same:
        """A rectangle on the chart, to mark an area. chart.draw_rectangle(x_between=[4, 6], y_between=[60, 80])
        (with chart.draw_dots(x="hours", y="marks") on sdata.get_example("marks"))

        It is filled see-through, so the marks under it still show; hollow=True draws only its outline.
        colour= one colour name; transparency= from 0 (solid) to 1.
        """
        example = "draw_rectangle(x_between=[4, 6], y_between=[60, 80])"
        x_between = self._between("draw_rectangle", "x_between", x_between, example)
        y_between = self._between("draw_rectangle", "y_between", y_between, example)
        _check_colour_name("draw_rectangle", colour)
        transparency = check_transparency("draw_rectangle", transparency)
        cues.check_switch("draw_rectangle", "hollow", hollow)
        return self._add("draw_rectangle", "extra", _draw_rectangle, x_between=x_between, y_between=y_between,
                         colour=colour, transparency=transparency, hollow=hollow)

    @friendly(others={"center": "centre", "r": "radius"})
    def draw_circle(self: _Same, centre=None, radius=None, colour=None, transparency=None, hollow=False) -> _Same:
        """A circle on the chart, to mark a place. chart.draw_circle(centre=[5, 70], radius=1)
        (with chart.draw_dots(x="hours", y="marks") on sdata.get_example("marks"))

        centre=[x, y] and radius= are in the units of the axes, so the circle looks round only when one
        unit is as long on both axes (chart.use_true_shape()). hollow=True draws only its outline.
        """
        example = "draw_circle(centre=[5, 70], radius=1)"
        if (centre is None or isinstance(centre, (str, bytes)) or not is_listlike(centre) or len(centre) != 2
                or not all(_is_number(v) for v in centre)):
            raise SimplydataError(f".draw_circle() needs centre=[x, y], two numbers, not {centre!r}.\n"
                                  f"For example chart.{example}")
        if not _is_number(radius) or radius <= 0:
            raise SimplydataError(f".draw_circle() needs radius=, a number bigger than 0, not {radius!r}.\n"
                                  f"For example chart.{example}")
        _check_colour_name("draw_circle", colour)
        transparency = check_transparency("draw_circle", transparency)
        cues.check_switch("draw_circle", "hollow", hollow)
        return self._add("draw_circle", "extra", _draw_circle, centre=[float(v) for v in centre],
                         radius=float(radius), colour=colour, transparency=transparency, hollow=hollow)

    @friendly
    def draw_residual_dots(self: _Same, x=None, y=None, colour=None, transparency=None) -> _Same:
        """What is left of y after a straight line on x, as dots round a line at 0.
        chart.draw_residual_dots(x="hours", y="marks") (with sdata.get_example("marks"))

        If the dots show a pattern (a curve, a fan), a straight line does not fit well. colour= one
        colour name.
        """
        transparency = check_transparency("draw_residual_dots", transparency)
        if x is None or y is None:
            raise SimplydataError('.draw_residual_dots() needs x= and y=, for example '
                                  'chart.draw_residual_dots(x="hours", y="marks").')
        _check_colour_name("draw_residual_dots", colour)
        check(self._data, x=x, y=y)
        from .charts import _check_numbers

        _check_numbers(self._data, "draw_residual_dots", x=x, y=y)
        self._need_axes("draw_residual_dots")
        return self._add("draw_residual_dots", "draw", _draw_residual_dots, x=x, y=y, colour=colour,
                         transparency=transparency)

    @friendly
    def draw_event_lines(self: _Same, x=None, y=None, colour=None, thickness=None) -> _Same:
        """A short upright line at each value, so every time something happened shows.
        chart.draw_event_lines(x="hours", y="class") (with sdata.get_example("marks"))

        y="class" draws one row of lines for each group; without y= all lines are on one row.
        colour= the same column as y= (each row its own colour) or one colour name.
        """
        thickness = check_thickness("draw_event_lines", thickness)
        if x is None:
            raise SimplydataError('.draw_event_lines() needs x=, for example chart.draw_event_lines(x="hours").')
        group, _ = colour_role(self._data, colour)
        check(self._data, x=x, y=y, colour=group)
        self._need_axes("draw_event_lines")
        return self._add("draw_event_lines", "draw", _draw_event_lines, x=x, y=y, colour=colour, thickness=thickness)

    @friendly
    def draw_bars_3d(self: _Same, x=None, y=None, z=None, colour=None, transparency=None) -> _Same:
        """Bars standing in a 3D box: one bar for each row, as high as z.
        chart.draw_bars_3d(x="month", y="city", z="rain") (with sdata.get_example("weather"))

        x= and y= are where each bar stands (numbers, or names along the axis), z= its height. Each
        place needs one row. 3D bars hide each other: a heat map is often clearer.
        """
        transparency = check_transparency("draw_bars_3d", transparency)
        if x is None or y is None or z is None:
            raise SimplydataError('.draw_bars_3d() needs x=, y= and z=, for example '
                                  'chart.draw_bars_3d(x="class", y="subject", z="marks").')
        _check_colour_name("draw_bars_3d", colour)
        check(self._data, x=x, y=y, z=z)
        from .charts import _check_numbers

        _check_numbers(self._data, "draw_bars_3d", z=z)
        self._need_axes("draw_bars_3d", "3d")
        return self._add("draw_bars_3d", "draw", _draw_bars_3d, x=x, y=y, z=z, colour=colour,
                         transparency=transparency)
