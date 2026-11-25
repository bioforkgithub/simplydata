"""More chart words (charts phase, batch 2; approved by Manish on 2026-11-25).

New words: a chart inside a chart, a second x scale, an arrow, the frame and ticks, the colour bar, the shape of
the plot area, a description of what was drawn, rug lines, a wind rose and the 3D words. The draw helpers of the
new options on older words (y= on draw_histogram and draw_density, show= on draw_dots, stacked="percent",
hole=, as_wires=, with_height_lines=, between= on the reference lines, formula= on add_second_y) live here too;
the older words call them.

Everything is passed through to matplotlib, seaborn, NumPy, pandas or SciPy (PLAN.md section 7): the counts of a
wind rose are NumPy's histogram2d, the averages of draw_dots(show=) are seaborn's pointplot, the inverse of a
second scale is SciPy's brentq. simplydata only chooses the starting values and checks the input.
"""

from __future__ import annotations

from .._typing import _Same

import numbers

import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns

from .._core import PHASES, Context
from .._data import is_listlike
from .._errors import SimplydataError, column_error, friendly
from . import second_cues as cues
from ._helpers import check, check_thickness, check_transparency, colour_role, default_colour, opacity

INSIDE_PLACES = ("top left", "top right", "bottom left", "bottom right")
INSIDE_GAP = 0.03  # the space between a chart inside and the edge of the chart it sits in (a share of its width)
COLOUR_BAR_PLACES = ("bottom", "top", "left")  # right is matplotlib's own place
STACKED_CHOICES = (False, True, "percent")
WIND_ROSE_SPEED_BANDS = 5  # about this many speed bands, at round numbers (matplotlib MaxNLocator)
SECOND_X_KINDS = ("lines", "dots")
THREE_D = "3d"


# ====================================================================== shared checks
def _need_3d(ctx, word):
    if ctx.ax.name != THREE_D:
        raise SimplydataError(
            f".{word}() works on 3D charts, such as chart.draw_surface(x=\"east\", y=\"north\", z=\"height\") or "
            "chart.draw_dots_3d(...).\nThis chart is flat; use the _x and _y words on it instead.")


def _need_flat(ctx, word):
    if ctx.ax.name != "rectilinear":
        raise SimplydataError(f".{word}() works on flat charts with an x and a y axis, not on round (polar) or "
                              "3D charts.")


def _is_number(value) -> bool:
    return not isinstance(value, bool) and isinstance(value, numbers.Real) and np.isfinite(value)


def check_stacked(word, stacked):
    """stacked= is True, False or "percent" (each stack makes 100 %)."""
    if isinstance(stacked, str):
        if stacked.strip().lower() == "percent":
            return "percent"
        raise SimplydataError(f'.{word}() does not know stacked="{stacked}".\n'
                              'Use stacked=True (groups on top of each other) or stacked="percent" (each stack '
                              "makes 100 %).")
    if not isinstance(stacked, bool):
        raise SimplydataError(f'stacked= in .{word}() should be True, False or "percent", not {stacked!r}.')
    return stacked


def check_between(word, between, example):
    """between=[low, high] of a reference line: two numbers (or dates), low first."""
    if between is None:
        return None
    if isinstance(between, (str, bytes)) or not is_listlike(between) or len(between) != 2:
        raise SimplydataError(f".{word}() needs two numbers in between=[low, high], not {between!r}.\n"
                              f"For example chart.{example}")
    low, high = between
    for v in (low, high):
        if isinstance(v, bool) or not (_is_number(v) or hasattr(v, "year") or isinstance(v, np.datetime64)):
            raise SimplydataError(f".{word}() needs numbers in between=, not {v!r}.\nFor example chart.{example}")
    try:
        wrong = not (low < high)
    except TypeError:
        raise SimplydataError(f".{word}() needs both ends of between= of the same kind (two numbers or two "
                              "dates).") from None
    if wrong:
        raise SimplydataError(f".{word}(between=[{low!r}, {high!r}]): the low end comes first, and the two must "
                              f"differ.\nWrite between=[{high!r}, {low!r}].")
    return [low, high]


# ====================================================================== options of older words
def check_no_negatives(data, word, y):
    """stacked="percent" shows shares of a whole, which a value below 0 cannot be part of: refuse at once."""
    if not isinstance(y, str) or y not in getattr(data, "columns", ()):
        return
    values = pd.to_numeric(data[y], errors="coerce")
    below = values[values < 0]
    if len(below):
        raise SimplydataError(
            f'.{word}(stacked="percent") shows each stack as shares of 100 %, so it cannot show values below 0, '
            f'and "{y}" has {len(below)} of them (smallest: {below.min():g}).\n'
            "Remove those rows first, or use stacked=True to show the values themselves.")


def as_percent_of_each_row(wide: pd.DataFrame, word: str) -> pd.DataFrame:
    """stacked="percent": each row's values as a percent of the row's total (pandas div and sum).

    A group with no rows at an x is an empty cell of `wide`: it counts as 0 there (it adds nothing to the stack),
    and a note says how many cells that was. A stack whose total is 0 has no shares: it is drawn empty, with a
    note naming it. Values below 0 are refused before drawing (check_no_negatives)."""
    from .._core import chart_note

    empty = int(wide.isna().sum().sum())
    if empty:
        line = (f'Note: .{word}(stacked="percent"): {empty} place{"s" if empty != 1 else ""} where a group has no '
                "value counted as 0 % of the stack.")
        chart_note(("percent empty", word), lambda _n, line=line: line)
    totals = wide.sum(axis=1)  # pandas leaves the empty cells out of the sum, the same as counting them as 0
    if (totals < 0).any():
        raise SimplydataError(f'.{word}(stacked="percent") cannot show stacks whose total is below 0.')
    zero = [str(i) for i in totals.index[totals == 0]]
    if zero:
        line = (f'Note: .{word}(stacked="percent"): the total of {", ".join(zero)} is 0, so '
                f'{"its stack is" if len(zero) == 1 else "their stacks are"} drawn empty.')
        chart_note(("percent zero", word), lambda _n, line=line: line)
    shares = wide.div(totals.where(totals != 0), axis=0).mul(100)
    return shares.where(wide.notna() | totals.eq(0).to_numpy()[:, None], 0.0)


def draw_histogram_2d(ctx, x, y, bins, colour, show, transparency=None):
    """draw_histogram(x=, y=): seaborn's two-way histogram (histplot with x and y)."""
    from . import _colour_scale as scales
    from .charts import _frame, _hue, _remember, _colour_bar
    from ._helpers import palette_for

    group, fixed = colour_role(ctx.data, colour)
    table, n = _frame(ctx, x=x, y=y, colour=group)
    kw = dict(data=table, x=n["x"], y=n["y"], **_hue(table, n), ax=ctx.ax, stat=show,
              bins=10 if bins is None else bins)
    if n["colour"]:
        kw["palette"] = palette_for(table, n["colour"], ctx.settings)
    else:  # the colour map of chart.use_colour_scale(...), else viridis as on heatmaps
        kw["cmap"] = ((ctx.settings["colour_scale"]["map"] if scales.wanted(ctx.settings) else None)
                      or cues.colour_map(ctx))  # greys in black and white
    if transparency is not None:
        kw["alpha"] = opacity(transparency)
    before = set(ctx.ax.collections)
    sns.histplot(**kw)
    if not n["colour"]:
        mesh = [c for c in ctx.ax.collections if c not in before]
        if mesh:
            _colour_bar(ctx, mesh[-1], show)
    _remember(ctx, "histogram_2d", table, n)


def draw_average_dots(ctx, x, y, colour, show, error, transparency=None):
    """draw_dots(show=, error=): one dot for each group's average (or median ...), with error bars: seaborn
    pointplot with the line between the dots left out."""
    from .._stats import SHOW, check_error
    from .charts import _frame, _hue, _remember, _seaborn_colours

    group, fixed = colour_role(ctx.data, colour)
    table, n = _frame(ctx, measure=SHOW[show], size_role="y", x=x, y=y, colour=group)
    kw = dict(data=table, x=n["x"], y=n["y"], **_hue(table, n), ax=ctx.ax, estimator=SHOW[show],
              errorbar=check_error("draw_dots", error, show), linestyle="none")
    _seaborn_colours(kw, table, n, ctx, fixed)
    if n["colour"] and n["colour"] not in (n["x"], n["y"]):
        kw["dodge"] = True  # the groups side by side, so their error bars do not cover each other
    if error:
        kw["capsize"] = 0.1
    if transparency is not None:
        kw["alpha"] = opacity(transparency)
    if n["colour"] and (ctx.settings.get("shapes") or cues.in_black_and_white(ctx)):
        # each group its own shape: use_shapes(), and the style "black and white" (charts phase, batch 1)
        how_many = table[n["colour"]].nunique()
        kw["markers"] = cues.markers_for(ctx.settings, how_many) or [
            list(cues.SHAPES.values())[i % len(cues.SHAPES)] for i in range(how_many)]
    elif ctx.settings.get("shapes"):
        kw["markers"] = cues.shape_codes(ctx.settings["shapes"])[0]
    x_values = table[n["x"]]
    if pd.api.types.is_numeric_dtype(x_values) and not pd.api.types.is_bool_dtype(x_values):
        kw["native_scale"] = True  # numbers keep their spacing (1, 2, 10); words and groups sit at 0, 1, 2 ...
    sns.pointplot(**kw)
    _remember(ctx, "dots_average", table, n, show=show)


def draw_wires(ctx, gx, gy, gz, transparency=None):
    """draw_surface(as_wires=True): matplotlib's wire frame of the same grid."""
    ctx.ax.plot_wireframe(gx, gy, gz, color=default_colour(ctx.settings), linewidth=0.8,
                          alpha=opacity(transparency))


def draw_height_lines(ctx, gx, gy, gz, colours):
    """draw_surface(with_height_lines=True): matplotlib's contour lines on the floor of the 3D box."""
    ctx.ax.contour(gx, gy, gz, zdir="z", offset=np.nanmin(gz), levels=10, **colours)


def draw_line_between(ctx, axis, value, low, high, style, label, size):
    """draw_line_at_y(..., between=[low, high]): matplotlib hlines (vlines for x) from low to high only."""
    ax = ctx.ax
    kw = dict(colors=style["color"], linestyles=style["linestyle"], linewidths=style["linewidth"],
              zorder=style["zorder"])
    if axis == "y":
        ax.hlines(value, low, high, **kw)
        if label:
            ax.text(high, value, f" {label}", ha="left", va="center", color=style["color"], fontsize=size)
    else:
        ax.vlines(value, low, high, **kw)
        if label:
            ax.text(value, high, f" {label} ", ha="center", va="bottom", color=style["color"], fontsize=size)


def pie_hole(hole):
    """draw_pie(hole=0.4): the ring's width for matplotlib (wedgeprops width) and where the percents go."""
    if hole is None:
        return {}, {}
    return {"width": 1 - hole}, {"pctdistance": 1 - (1 - hole) / 2}


def check_hole(hole):
    if hole is None:
        return None
    if isinstance(hole, bool) or not isinstance(hole, numbers.Real) or not 0 < hole < 1:
        raise SimplydataError(f"hole= in .draw_pie() is the share of the circle left empty in the middle, a number "
                              f"between 0 and 1 such as hole=0.4, not {hole!r}.")
    if hole > 0.9:
        raise SimplydataError(f"hole={hole} in .draw_pie() leaves almost no ring to see. Try 0.3 to 0.7.")
    return float(hole)


# ====================================================================== second scales
def _second_scale(ctx, axis, formula_text, label):
    """A second x or y scale in other units over the same data: matplotlib secondary_xaxis / secondary_yaxis with
    the formula (simplydata's formula reader) one way and SciPy's brentq the other way, on the drawn range."""
    from scipy.optimize import brentq

    from .axes import _has_group_names, _is_date_axis
    from .curves import read_curve_formula

    word = f"add_second_{axis}"
    _need_flat(ctx, word)
    formula, _, name, _ = read_curve_formula(word, formula_text)
    ax = ctx.ax
    axis_obj = ax.xaxis if axis == "x" else ax.yaxis
    if _is_date_axis(axis_obj) or _has_group_names(axis_obj):
        raise SimplydataError(f".{word}(formula=...) needs numbers on the {axis}-axis, but it shows dates or "
                              "groups (names).")
    if axis_obj.get_scale() != "linear":
        raise SimplydataError(f".{word}(formula=...) works on an ordinary {axis}-axis, not on a log scale.")
    low, high = sorted(ax.get_xlim() if axis == "x" else ax.get_ylim())

    def forward(values):
        values = np.asarray(values, dtype=float)
        with np.errstate(all="ignore"):
            return np.asarray(formula({name: values}), dtype=float) * np.ones_like(values)

    with np.errstate(invalid="ignore"):
        steps = np.diff(forward(np.linspace(low, high, 201)))
    if not (np.all(steps > 0) or np.all(steps < 0)):
        raise SimplydataError(
            f'.{word}(formula="{formula_text}") needs a formula that only goes up (or only down) over the chart, '
            f"from {low:g} to {high:g}, so each place on the {axis}-axis has one value on the second scale.")
    span = high - low
    brackets = [(low - span, high + span), (low, high)]

    def inverse(values):
        values = np.asarray(values, dtype=float)
        out = np.full(values.shape, np.nan)
        for place, target in np.ndenumerate(values):
            if not np.isfinite(target):
                continue
            for a, b in brackets:
                try:
                    out[place] = brentq(lambda t: float(forward(t)) - target, a, b)
                    break
                except (ValueError, RuntimeError):
                    continue
        return out

    if axis == "x":
        second = ax.secondary_xaxis("top", functions=(forward, inverse))
        if label:
            second.set_xlabel(label)
    else:
        second = ax.secondary_yaxis("right", functions=(forward, inverse))
        if label:
            second.set_ylabel(label)
    ctx.store[f"second_{axis}_scale"] = second


def _draw_second_x_column(ctx, x, drawn_as, label, colour):
    """add_second_x("column"): the same y drawn against another column on a second x-axis at the top (twiny),
    by seaborn lineplot (the average at each x) or scatterplot."""
    from .axes import _free_colour

    last = ctx.last
    if last is None or last.get("kind") not in ("lines", "dots") or last.get("y") is None:
        raise SimplydataError(
            ".add_second_x() draws the y of a lines or dots chart against a second column at the top, so it needs "
            'one to sit on.\nFor example:\n  chart.draw_lines(x="month_number", y="temperature")\n'
            '  chart.add_second_x("rain", labelled="Rain (mm)")')
    table, y = last["table"], last["y"]
    if x not in table.columns:
        raise column_error(x, table.columns)
    ax = ctx.ax
    colour = colour or _free_colour(ax, ctx.settings)
    twin = ax.twiny()
    ctx.store["second_x"] = twin
    twin.grid(False)
    if drawn_as == "lines":
        sns.lineplot(data=table, x=x, y=y, estimator="mean", errorbar=None, color=colour, ax=twin)
    else:
        sns.scatterplot(data=table, x=x, y=y, color=colour, ax=twin)
    twin.set_ylabel("")
    twin.set_xlabel(label or x, color=colour)
    twin.tick_params(axis="x", colors=colour)
    twin.spines["top"].set_visible(True)
    twin.spines["top"].set_color(colour)


# ====================================================================== a chart inside a chart
def _chart_inside(ctx, other, where, size):
    """matplotlib inset_axes, then the other chart's steps drawn on it (as add_zoom_box draws its own steps)."""
    _need_flat(ctx, "put_chart_inside")
    ax = ctx.ax
    left = INSIDE_GAP if "left" in where else 1 - INSIDE_GAP - size
    bottom = 1 - INSIDE_GAP - size if "top" in where else INSIDE_GAP
    inset = ax.inset_axes([left, bottom, size, size])
    sub = Context(fig=ctx.fig, ax=inset, data=other._data, settings=other._settings, axes=[inset])
    sub.store["whole_table"] = other._data
    # its own panel steps, and its title and axis names (which go on the small chart when it has one panel)
    steps = [s for s in other._steps if s.scope == "axes" or s.name in ("title_top", "label_x", "label_y")]
    other._run(steps, sub)
    inset.tick_params(labelsize="small")
    for text in (inset.title, inset.xaxis.label, inset.yaxis.label):
        text.set_fontsize("small")
    inset.set_facecolor(matplotlib.rcParams["axes.facecolor"])
    inset.set_zorder(5)  # above the main chart's marks and legend
    ctx.store.setdefault("charts_inside", []).append(inset)


# ====================================================================== arrows
def _draw_arrow(ctx, start, end, colour, label, thickness):
    """One arrow from start to end: matplotlib annotate with an arrow and no words (or the words at the start)."""
    from .axes import tick_position

    ax = ctx.ax
    colour = colour or matplotlib.rcParams["text.color"]
    begin = (tick_position(ax, "x", start[0]), tick_position(ax, "y", start[1]))
    finish = (tick_position(ax, "x", end[0]), tick_position(ax, "y", end[1]))
    ax.annotate(label or "", xy=finish, xytext=begin, xycoords="data", textcoords="data",
                ha="center", va="center", color=colour, fontsize=matplotlib.rcParams["legend.fontsize"],
                arrowprops=dict(arrowstyle="->", color=colour, linewidth=1.5 if thickness is None else thickness,
                                shrinkA=4 if label else 0, shrinkB=0),
                zorder=4)


# ====================================================================== frame, ticks and shape
def _hide_frame(ctx):
    ctx.ax.set_axis_off()


def _hide_ticks(ctx, axis):
    if axis == "x":
        ctx.ax.tick_params(axis="x", which="both", length=0, labelbottom=False, labeltop=False)
    else:
        ctx.ax.tick_params(axis="y", which="both", length=0, labelleft=False, labelright=False)


def _small_ticks(ctx, axis):
    (ctx.ax.xaxis if axis == "x" else ctx.ax.yaxis).minorticks_on()


def _true_shape(ctx):
    ctx.ax.set_aspect("equal")


def _make_square(ctx):
    ax = ctx.ax
    ax.set_box_aspect((1, 1, 1) if ax.name == THREE_D else 1)


# ====================================================================== colour bar
def _bars_of(ctx, word):
    bar = ctx.store.get("colour_bar")
    if bar is None:
        raise SimplydataError(
            f".{word}() needs a chart with a colour bar,\n"
            'for example chart.draw_heatmap() or chart.draw_contour(x="east", y="north", z="height").')
    return bar if isinstance(bar, (list, tuple)) else [bar]


def _check_colour_bar_place(ctx):
    _bars_of(ctx, f"put_colour_bar_at_{ctx.settings.get('colour_bar_place')}")


def _hide_colour_bar(ctx):
    bar = ctx.store.pop("colour_bar", None)
    for one in bar if isinstance(bar, (list, tuple)) else ([bar] if bar is not None else []):
        one.remove()


def _ticks_colour_bar(ctx, values, labels):
    for bar in _bars_of(ctx, "put_ticks_colour_bar"):
        bar.set_ticks(values, labels=labels)


# ====================================================================== rug lines
def _draw_rug_lines(ctx, x, y, colour, transparency=None, thickness=None):
    """seaborn rugplot: a short line at each value along the axis."""
    from .charts import _frame, _hue, _remember, _seaborn_colours

    group, fixed = colour_role(ctx.data, colour)
    table, n = _frame(ctx, on_x="x" if x is not None else None, on_y="y" if y is not None else None,
                      x=x, y=y, colour=group)
    kw = dict(data=table, x=n["x"], y=n["y"], **_hue(table, n), ax=ctx.ax)
    _seaborn_colours(kw, table, n, ctx, fixed)
    if transparency is not None:
        kw["alpha"] = opacity(transparency)
    if thickness is not None:
        kw["linewidth"] = thickness
    sns.rugplot(**kw)
    if ctx.last is None:  # alone, the rug is the chart; on top of dots or a density it leaves them in charge
        _remember(ctx, "rug_lines", table, n)


# ====================================================================== wind rose
def _speed_edges(values):
    """Round numbers that cover the speeds, about WIND_ROSE_SPEED_BANDS bands (matplotlib's MaxNLocator)."""
    from matplotlib import ticker

    locator = ticker.MaxNLocator(nbins=WIND_ROSE_SPEED_BANDS)
    return locator.tick_values(*locator.nonsingular(float(np.min(values)), float(np.max(values))))


def _draw_wind_rose(ctx, angle, distance, every, transparency=None):
    """NumPy counts how many rows fall in each direction sector (and speed band) with histogram2d; matplotlib draws
    the counts as bars round a compass (0 at the top, clockwise), stacked from the slowest band outwards."""
    from .charts import _frame, _remember

    table, n = _frame(ctx, on_x=None, on_y=None, angle=angle, distance=distance)
    ax = ctx.ax
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    used = [n["angle"]] + ([n["distance"]] if n["distance"] else [])
    rows = table[used].apply(pd.to_numeric, errors="coerce").dropna()
    if not len(rows):
        raise SimplydataError(".draw_wind_rose() found no rows with a direction" +
                              (" and a speed" if n["distance"] else "") + " to count.")
    # each sector is centred on its direction (0 = north): turning every direction on by half a sector puts the
    # sector from -15 to 15 degrees (with every=30) into NumPy's first bin, 0 to 30
    turned = np.mod(rows[n["angle"]].to_numpy(dtype=float) + every / 2, 360)
    sector_edges = np.linspace(0, 360, int(round(360 / every)) + 1)
    centres = np.deg2rad(sector_edges[:-1])
    width = np.deg2rad(every)
    alpha = opacity(transparency)
    if n["distance"] is None:
        counts, _ = np.histogram(turned, bins=sector_edges)
        ax.bar(centres, counts, width=width, color=default_colour(ctx.settings), edgecolor="white",
               linewidth=0.8, alpha=alpha)
    else:
        speeds = rows[n["distance"]].to_numpy(dtype=float)
        speed_edges = _speed_edges(speeds)
        counts, _, _ = np.histogram2d(turned, speeds, bins=[sector_edges, speed_edges])
        bands = [j for j in range(counts.shape[1]) if counts[:, j].any()]
        if cues.in_black_and_white(ctx):  # greys from light (slow) to dark (fast), between 25 % and 75 %
            colours = [matplotlib.colors.to_hex(str(v)) for v in np.linspace(0.75, 0.25, len(bands))]
        else:
            colours = sns.color_palette("viridis", n_colors=len(bands))
        before = set(ax.patches)
        bottom = np.zeros(len(centres))
        for colour, j in zip(colours, bands):
            ax.bar(centres, counts[:, j], width=width, bottom=bottom, color=colour, edgecolor="white",
                   linewidth=0.8, alpha=alpha, label=f"{speed_edges[j]:g} to {speed_edges[j + 1]:g}")
            bottom = np.add(bottom, counts[:, j])
        ax.legend(title=n["distance"], loc="upper left", bbox_to_anchor=(1.08, 1))
        if cues.in_black_and_white(ctx):  # each speed band its own pattern, in the legend too
            cues.patterns_by_colour(ax, before)
    ax.set_xticks(np.deg2rad([0, 90, 180, 270]), labels=["N", "E", "S", "W"])
    ax.grid(True)
    ctx.store["wind_rose_sectors"] = sector_edges - every / 2  # the drawn sectors' edges, in degrees
    _remember(ctx, "wind_rose", table, {"x": n["angle"], "y": n["distance"], "colour": None})


# ====================================================================== 3D
def _draw_lines_3d(ctx, x, y, z, colour, transparency=None, thickness=None):
    """matplotlib Axes3D.plot: one line through the points in the order of the table, one per group."""
    from .charts import _frame, _group_colours, _groups, _remember

    group, fixed = colour_role(ctx.data, colour)
    table, n = _frame(ctx, on_x=None, on_y=None, x=x, y=y, z=z, colour=group)
    ax = ctx.ax
    before = list(ax.get_lines())
    for (name, rows), c in zip(_groups(table, n["colour"]), _group_colours(table, n["colour"], ctx, fixed)):
        ax.plot(rows[n["x"]].to_numpy(dtype=float), rows[n["y"]].to_numpy(dtype=float),
                rows[n["z"]].to_numpy(dtype=float), color=c, label=None if name is None else str(name),
                alpha=opacity(transparency), linewidth=thickness)
    if n["colour"]:
        ax.legend(title=n["colour"])
    if cues.in_black_and_white(ctx):  # each group its own dashes, in the legend too
        cues.dashes_by_colour(ax, before)
    ax.set_xlabel(n["x"])
    ax.set_ylabel(n["y"])
    ax.set_zlabel(n["z"])
    _remember(ctx, "lines_3d", table, n, z=n["z"])


def _label_z(ctx, text):
    _need_3d(ctx, "label_z")
    ctx.ax.set_zlabel(text)


def _range_z(ctx, low, high):
    _need_3d(ctx, "set_range_z")
    cur_low, cur_high = sorted(ctx.ax.get_zlim())
    low = cur_low if low is None else low
    high = cur_high if high is None else high
    if low >= high:
        raise SimplydataError(f".set_range_z(): the range would be empty (from {low:g} to {high:g}).\n"
                              "Give both ends, for example chart.set_range_z(0, 100).")
    ctx.ax.set_zlim(low, high)


def _ticks_z(ctx, values, labels):
    _need_3d(ctx, "put_ticks_z")
    ctx.ax.set_zticks(values, labels=labels)


def _look_from(ctx, height, around):
    _need_3d(ctx, "look_from")
    ctx.ax.view_init(elev=height, azim=around)


# ====================================================================== what it shows
# say_what_it_shows() describes each drawing step the user wrote (the chart word and the columns it was given, as
# recorded in the chart's steps) and reads everything else from the drawn figure: the group names from the legend,
# the axis names, their ranges or the names along them, the title and the colour bar. It never counts the pieces
# matplotlib draws with (a line of 12 points is one line, not 12; an error bar is not a line of data).
_WHAT_IS_DRAWN = {
    "draw_bars": "bars", "draw_count_bars": "bars that count the rows", "draw_lines": "lines", "draw_dots": "dots",
    "draw_area": "coloured areas under lines", "draw_histogram": "a histogram: bars that count the values in ranges",
    "draw_boxes": "boxes (the line is the median, the box the middle half of the values)",
    "draw_violins": "violins (shapes that are wide where many values are)", "draw_all_dots": "every value as a dot",
    "draw_density": "smooth density curves", "draw_heatmap": "a grid of coloured squares",
    "draw_pie": "a pie, one slice per group", "draw_polar": "dots on a round chart",
    "draw_contour": "a contour map (each colour band is one height)", "draw_surface": "a 3D surface",
    "draw_dots_3d": "dots in a 3D box", "draw_lines_3d": "lines in a 3D box", "draw_band": "a shaded band",
    "draw_rug_lines": "a short line at each value along the axis", "draw_cumulative_share":
        "lines that climb from 0 to 1: the share of values at or below each x",
    "draw_wind_rose": "bars round a compass (north at the top): how many rows come from each direction",
    # charts phase, batch 3
    "draw_hexagon_bins": "hexagons coloured by how many dots fall in each (a colour bar gives the counts)",
    "draw_time_bars": "a bar from the start to the end of each row, the first row at the top",
    "draw_residual_dots": "what is left of y after a straight line on x, as dots round a line at 0",
    "draw_event_lines": "a short upright line at each value", "draw_bars_3d": "bars standing in a 3D box",
}
_ONE_PER_GROUP = {"draw_lines": ("line", "lines"), "draw_area": ("area", "areas"),
                  "draw_density": ("curve", "curves"), "draw_cumulative_share": ("line", "lines"),
                  "draw_lines_3d": ("line", "lines")}
_OPTION_NAMES = {"draw_wind_rose": {"angle": "direction", "distance": "speed"}}
_COLUMN_KEYS = ("x", "y", "z", "value", "colour", "size", "shape", "labels", "values", "angle", "distance", "low",
                "high", "column", "start", "end")


def _is_number_text(text):
    try:
        float(text.replace("−", "-").replace(",", "").rstrip("%").strip())
        return True
    except ValueError:
        return False


def _axis_words(ax, axis):
    """An axis in words, read from the drawn axes: its name, then the names written along it (a category axis,
    a heatmap) or the range of its numbers or dates; a log scale and a flipped axis are said."""
    from matplotlib import dates as mdates

    from .axes import _is_date_axis

    obj = {"x": ax.xaxis, "y": ax.yaxis}.get(axis) or ax.zaxis
    name = obj.get_label().get_text() or "no name"
    labels = [t.get_text() for t in obj.get_ticklabels() if t.get_text()]
    flipped = axis in "xy" and (ax.xaxis_inverted() if axis == "x" else ax.yaxis_inverted())
    if _is_date_axis(obj):
        low, high = (mdates.num2date(v).strftime("%Y-%m-%d") for v in sorted(obj.get_view_interval()))
        span = f"from {low} to {high}"
    elif labels and not all(_is_number_text(t) for t in labels):
        return f'{axis}-axis "{name}", with the names ' + ", ".join(labels)  # their order says the direction
    else:
        low, high = sorted(obj.get_view_interval())
        span = f"from {low:.4g} to {high:.4g}"
    scale = {"log": " (log scale)", "symlog": " (log scale through zero)", "logit": " (logit scale)",
             "asinh": " (asinh scale)"}.get(obj.get_scale(), "")
    if obj.get_scale() == "function" and getattr(obj, "simplydata_scale", None):
        scale = f" ({obj.simplydata_scale} scale)"  # use_scale_y("square root") (charts phase, batch 3)
    return f'{axis}-axis "{name}", {span}{scale}' + (" (flipped)" if flipped else "")


def _legend_of(ax, fig):
    legend = ax.get_legend() or next(iter(fig.legends), None)
    if legend is None or not legend.get_visible():
        return None, []
    return legend.get_title().get_text(), [t.get_text() for t in legend.get_texts() if t.get_text()]


def _step_words(chart, step, ax, fig):
    """One drawing step in words: the word and its columns as written, what it draws, and its groups (read from
    the drawn legend)."""
    from .._stats import ERROR_MEANING

    word = chart._public_name(step.name)
    kw = step.kwargs
    rename = _OPTION_NAMES.get(word, {})
    written = ", ".join(f'{rename.get(k, k)}="{v}"' for k, v in kw.items() if k in _COLUMN_KEYS and isinstance(v, str))
    parts = ["" if word in _ONE_PER_GROUP else _WHAT_IS_DRAWN.get(word, "")]  # those say "3 lines ..." below
    group = kw.get("colour")
    data = chart._data
    if isinstance(group, str) and group in getattr(data, "columns", ()):
        title, names = _legend_of(ax, fig)
        if word in _ONE_PER_GROUP:
            one, many = _ONE_PER_GROUP[word]
            noun = one if len(names) == 1 else many
            parts.append(f"{len(names)} {noun}, one for each {group}: " + ", ".join(names) if names
                         else f"one {_ONE_PER_GROUP[word][0]} for each {group}")
        else:
            parts.append(f"one colour for each {group}" + (": " + ", ".join(names) if names else ""))
    elif word in _ONE_PER_GROUP:
        parts.append(f"one {_ONE_PER_GROUP[word][0]}")
    show = kw.get("show")
    if show and word in ("draw_bars", "draw_lines", "draw_dots"):
        mark = {"draw_bars": "bar", "draw_lines": "point of a line", "draw_dots": "dot"}[word]
        y = kw.get("y")
        parts.append(f"each {mark} counts rows" if show == "count" else
                     f'each {mark} is the {show} of "{y}"' if isinstance(y, str) else f"each {mark} is the {show}")
    if word == "draw_histogram":
        parts.append(f'the height of a bar is the {kw.get("show", "count")}')
    if kw.get("stacked") == "percent":
        parts.append("stacked, each stack making 100 %")
    elif kw.get("stacked") is True:
        parts.append("stacked on top of each other")
    if word == "draw_wind_rose":
        parts[0] += f', one bar for every {kw.get("every", 30):g} degrees'
        if kw.get("distance"):
            title, names = _legend_of(ax, fig)
            parts.append(f'stacked by bands of "{kw["distance"]}": ' + ", ".join(names))
    error = kw.get("error")
    if error in ERROR_MEANING:
        parts.append(("a shaded band shows " if word == "draw_lines" else "error bars show ") + ERROR_MEANING[error])
    # second cues besides colour, as asked (charts phase, batch 1)
    if kw.get("hatched") is True:
        parts.append("each " + (f"{group} " if isinstance(group, str) else "") + "has its own pattern")
    if kw.get("hollow") is True:
        parts.append("hollow dots (outlines only)")
    if isinstance(kw.get("dashed"), str):
        parts.append(f'each {kw["dashed"]} has its own dashes')
    elif kw.get("dashed") is True:
        parts.append("dashed")
    elif kw.get("dotted") is True:
        parts.append("dotted")
    return f"{word}({written}): " + "; ".join(p for p in parts if p) + "."


def _extra_words(chart, step):
    """A step drawn on top of the chart types (a reference line, a fitted line, error bars ...), in words."""
    from .._stats import ERROR_MEANING, ERRORS

    word = chart._public_name(step.name)
    if not (word.startswith(("draw_", "fit_", "shade_", "write_note", "put_chart_inside", "add_"))):
        return None
    kw = step.kwargs
    if word in ("draw_line_at_x", "draw_line_at_y"):
        between = kw.get("between")
        where = f" from {between[0]} to {between[1]}" if between else ""
        return f"{word}({kw['value']}): a straight line at {word[-1]} = {kw['value']}{where}."
    if word == "draw_error_bars":
        code = ERRORS.get(str(kw.get("kind")).lower(), kw.get("kind"))
        return f"{word}(): error bars showing {ERROR_MEANING.get(code, kw.get('kind'))}."
    if word == "put_chart_inside":
        return "put_chart_inside(): a small chart drawn inside this one."
    if word == "draw_rectangle":  # charts phase, batch 3
        return (f"draw_rectangle(): a rectangle from x = {kw['x_between'][0]} to {kw['x_between'][1]} and "
                f"y = {kw['y_between'][0]} to {kw['y_between'][1]}" + (", outline only." if kw.get("hollow") else "."))
    if word == "draw_circle":
        return (f"draw_circle(): a circle round x = {kw['centre'][0]:g}, y = {kw['centre'][1]:g} with radius "
                f"{kw['radius']:g}" + (", outline only." if kw.get("hollow") else "."))
    if word == "draw_side_histograms" and kw.get("drawn_as") == "density":
        return "draw_side_histograms(drawn_as=\"density\"): density curves of x and y along the top and right edges."
    if word == "write_note":
        place = (f' at the {kw["where"]} of the chart' if kw.get("where") else
                 f' at x = {kw.get("x")}, y = {kw.get("y")}' + (" with an arrow" if kw.get("arrow") else ""))
        return f'write_note("{kw.get("text")}"): a note{place}' + (", in a box." if kw.get("box") else ".")
    return f"{word}(): drawn on top."


def _legend_place(chart):
    """Where the legend was put by a word (put_legend_inside("top left"), put_legend_at_bottom() ...), in words."""
    from .letters_and_legends import _legend_inside

    step = next((s for s in chart._steps if s.name == "legend"), None)
    where = step.kwargs.get("where") if step is not None else None
    if where is None or where == "hide":
        return ""
    if step.func is _legend_inside:
        return " inside the chart" if where == "best" else f" inside the chart, {where}"
    return {"top": " above the chart", "bottom": " below the chart"}.get(where, f" on the {where}")


def _look_words(chart):
    """The second cues set for the whole chart: use_shapes(...) and the style "black and white"."""
    settings = chart._settings
    lines = []
    if settings.get("shapes"):
        lines.append("Dot shapes for the groups: " + ", ".join(settings["shapes"]) + ".")
    if settings.get("style") == cues.BLACK_AND_WHITE:
        lines.append('Style "black and white": greys; the groups also differ by pattern, dashes or dot shape.')
    return lines


def describe_chart(chart) -> str:
    """The text of say_what_it_shows(): the drawing steps as written, and the title, axes, legend and colour bar
    as drawn. Nothing is counted or worked out from the data."""
    import io

    fig = chart._render()
    fig.savefig(io.BytesIO(), format="png")  # tick names and second scales are only set when a chart is drawn
    panels = [a for a in fig.axes if a.get_label() != "<colorbar>" and a.get_visible()
              and a.__class__.__name__ != "SecondaryAxis"]
    ax = panels[0]
    lines = []
    sup = getattr(fig, "_suptitle", None)
    letters = [t.get_text() for t in [sup, ax._left_title, ax._right_title]
               if t is not None and t.get_visible() and getattr(t, "simplydata_part", None) == "panel letter"]
    title = next((t.get_text() for t in [sup, ax.title, ax._left_title]
                  if t is not None and t.get_visible() and t.get_text()
                  and getattr(t, "simplydata_part", None) != "panel letter"), "")
    if title:
        lines.append(f'Title: "{title}".')
    if letters:
        lines.append(f'Panel letter: "{letters[0]}".')
    draws = [s for s in chart._steps if s.phase == PHASES["draw"]]
    if not draws:
        lines.append("Nothing is drawn yet.")
    lines += [_step_words(chart, s, ax, fig) for s in draws]
    extras = [_extra_words(chart, s) for s in chart._steps if s.phase != PHASES["draw"]]
    lines += [e for e in extras if e]
    split = chart._settings.get("split") or {}
    if len(panels) > 1 and split:
        by = [c for c in (split.get("by"), split.get("down"), split.get("row"), split.get("column")) if c]
        lines.append(f"It is drawn as {len(panels)} small charts, one for each group of " + " and ".join(by) + ".")
    if ax.name == "polar":
        lines.append("It is a round chart: directions go round, counts or distances go out from the middle.")
    elif ax.name == THREE_D or ax.axison:
        axes = ["x", "y"] + (["z"] if ax.name == THREE_D else [])
        lines.append("; ".join(_axis_words(ax, a) for a in axes) + ".")
    for second in (c for c in ax.child_axes if c.__class__.__name__ == "SecondaryAxis"):
        name = second.xaxis.get_label().get_text() or second.yaxis.get_label().get_text()
        lines.append("A second scale shows the same places in other units" + (f': "{name}".' if name else "."))
    legend_title, entries = _legend_of(ax, fig)
    if entries:
        lines.append(f"Legend{f' ({legend_title})' if legend_title else ''}{_legend_place(chart)}: "
                     + ", ".join(entries) + ".")
    lines += _look_words(chart)
    y_break = chart._settings.get("y_break")
    if y_break:  # break_between_y (charts phase, batch 3)
        lines.append(f"The y-axis is broken: the part from {y_break[0]:g} to {y_break[1]:g} is left out, so the chart "
                     "is drawn twice, below and above the break.")
    background = next((s for s in chart._steps if s.name == "background_colour"), None)
    if background is not None:
        lines.append(f'The plot area is coloured "{background.kwargs["colour"]}".')
    for bar_ax in (a for a in fig.axes if a.get_label() == "<colorbar>"):
        horizontal = bool(bar_ax.get_xlabel()) and not bar_ax.get_ylabel()
        name = bar_ax.get_xlabel() if horizontal else bar_ax.get_ylabel()
        low, high = sorted(bar_ax.get_xlim() if horizontal else bar_ax.get_ylim())
        lines.append(f'Colour bar{f" {chr(34)}{name}{chr(34)}" if name else ""}: from {low:.4g} to {high:.4g}.')
    return "\n".join(lines)


# ====================================================================== the words
class MoreChartWords:
    """Chart words of the charts phase, batch 2."""

    # -------------------------------------------------------------- a chart inside a chart
    @friendly
    def put_chart_inside(self: _Same, other_chart, where="top left", size=0.4) -> _Same:
        """Draw another chart small, inside this one. chart.put_chart_inside(detail, where="top right")
        (with sdata.get_example("weather"))

        other_chart is a chart made with sdata.chart(...), such as a close-up or an overview.
        where= is "top left" (normal), "top right", "bottom left" or "bottom right"; size=0.4 makes the
        small chart 0.4 of this chart's width and height. Its own title and axis names come along, smaller.
        """
        from .._core import BaseChart

        if not isinstance(other_chart, BaseChart) or not hasattr(other_chart, "_draw_panel") \
                or hasattr(other_chart, "_charts"):
            raise SimplydataError(
                ".put_chart_inside() needs a chart made with sdata.chart(...), for example\n"
                '    detail = sdata.chart(table).draw_lines(x="month", y="rain")\n'
                '    chart.put_chart_inside(detail, where="top right")')
        if other_chart is self:
            raise SimplydataError(".put_chart_inside() needs another chart, not the chart itself. "
                                  "For a close-up of this chart, use chart.add_zoom_box(...).")
        if other_chart._settings.get("projection") is not None or other_chart._settings.get("split"):
            raise SimplydataError(".put_chart_inside() draws a flat chart with one panel inside this one; the other "
                                  "chart is round, 3D or split into panels.")
        if any(s.name == "put_chart_inside" for s in other_chart._steps):
            raise SimplydataError(".put_chart_inside(): the other chart already holds a chart inside it. Put both "
                                  "small charts inside this one instead.")
        if isinstance(where, str) and where.strip().lower() in INSIDE_PLACES:
            where = where.strip().lower()
        self._check_choice("put_chart_inside", "where", where, INSIDE_PLACES)
        if isinstance(size, bool) or not isinstance(size, numbers.Real) or not 0.1 <= size <= 0.6:
            raise SimplydataError(f"size= in .put_chart_inside() is the share of this chart the small one takes, "
                                  f"from 0.1 to 0.6, such as size=0.4, not {size!r}.")
        return self._add("put_chart_inside", "finish", _chart_inside, other=other_chart, where=where, size=float(size))

    # -------------------------------------------------------------- second x scale
    @friendly
    def add_second_x(self: _Same, x=None, drawn_as="lines", labelled=None, colour=None, formula=None) -> _Same:
        """A second x-axis at the top. chart.add_second_x(formula="x * 9 / 5 + 32", labelled="Temperature (°F)")
        (with chart.draw_dots(x="temperature", y="rain") on sdata.get_example("weather"))

        formula= writes the same places in other units: the formula turns a number on the x-axis into
        the number on the top scale (any one name, such as x). It must only go up (or only down).
        A column instead, chart.add_second_x("wind_speed"), draws the y of the chart against that
        column on the top axis: drawn_as="lines" (the average at each x) or "dots".
        labelled= names the top axis; colour= colours a column's line or dots.
        """
        if formula is not None:
            if x is not None:
                raise SimplydataError(".add_second_x() takes a column or formula=, not both.")
            return self._second_scale_step("x", formula, labelled)
        if x is None or not isinstance(x, str):
            raise SimplydataError(
                '.add_second_x() needs a column name or formula=, for example chart.add_second_x("wind_speed") or\n'
                'chart.add_second_x(formula="x * 9 / 5 + 32", labelled="Temperature (°F)").')
        self._check_choice("add_second_x", "drawn_as", drawn_as, SECOND_X_KINDS)
        check(self._data, x=x)
        if colour is not None and not (isinstance(colour, str) and matplotlib.colors.is_color_like(colour)):
            raise SimplydataError(f'.add_second_x() needs one colour name for colour=, such as "red", not {colour!r}.')
        return self._replace("add_second_x", "extra", _draw_second_x_column, x=x, drawn_as=drawn_as,
                             label=None if labelled is None else str(labelled), colour=colour)

    def _second_scale_step(self, axis, formula, labelled):
        """formula= on add_second_x and add_second_y: checked now (the formula is read), drawn on the final range."""
        from .curves import read_curve_formula

        read_curve_formula(f"add_second_{axis}", formula)
        return self._replace(f"second_{axis}_scale", "text", _second_scale, axis=axis, formula_text=formula,
                             label=None if labelled is None else str(labelled))

    # -------------------------------------------------------------- arrow
    @friendly
    def draw_arrow(self: _Same, start=None, end=None, colour=None, labelled=None, thickness=None) -> _Same:
        """An arrow from one place to another. chart.draw_arrow(start=[2, 40], end=[4, 60])
        (with chart.draw_dots(x="hours", y="marks") on sdata.get_example("marks"))

        start= and end= are [x, y] places on the chart; on bar charts x can be a name.
        labelled="Fastest" writes words at the start of the arrow. colour= and thickness= as on lines.
        """
        example = "draw_arrow(start=[2, 40], end=[4, 60])"
        for name, place in (("start", start), ("end", end)):
            if place is None or isinstance(place, (str, bytes)) or not is_listlike(place) or len(place) != 2:
                raise SimplydataError(f".draw_arrow() needs {name}=[x, y], two numbers, not {place!r}.\n"
                                      f"For example chart.{example}")
            for v in place:
                if not (_is_number(v) or isinstance(v, str) or hasattr(v, "year")):
                    raise SimplydataError(f".draw_arrow() needs numbers in {name}=, not {v!r}.\n"
                                          f"For example chart.{example}")
        if list(start) == list(end):
            raise SimplydataError(".draw_arrow() needs two different places for start= and end=.")
        if colour is not None and not (isinstance(colour, str) and matplotlib.colors.is_color_like(colour)):
            raise SimplydataError(f'.draw_arrow() does not know the colour {colour!r}. Use a name such as "black".')
        thickness = check_thickness("draw_arrow", thickness)
        return self._add("draw_arrow", "extra", _draw_arrow, start=list(start), end=list(end), colour=colour,
                         label=None if labelled is None else str(labelled), thickness=thickness)

    # -------------------------------------------------------------- frame and ticks
    @friendly
    def hide_frame(self: _Same) -> _Same:
        """Only the marks: no axes, ticks, numbers or frame. chart.hide_frame()

        Good for a small picture or an icon; the axis names go too.
        """
        return self._replace("hide_frame", "axes", _hide_frame)

    @friendly
    def hide_ticks_x(self: _Same) -> _Same:
        """No tick marks and no numbers (or names) under the x-axis. chart.hide_ticks_x()"""
        return self._replace("hide_ticks_x", "text", _hide_ticks, axis="x")

    @friendly
    def hide_ticks_y(self: _Same) -> _Same:
        """No tick marks and no numbers beside the y-axis. chart.hide_ticks_y()"""
        return self._replace("hide_ticks_y", "text", _hide_ticks, axis="y")

    @friendly
    def show_small_ticks_x(self: _Same) -> _Same:
        """Small ticks between the numbered ticks of the x-axis. chart.show_small_ticks_x()"""
        return self._replace("show_small_ticks_x", "axes", _small_ticks, axis="x")

    @friendly
    def show_small_ticks_y(self: _Same) -> _Same:
        """Small ticks between the numbered ticks of the y-axis. chart.show_small_ticks_y()"""
        return self._replace("show_small_ticks_y", "axes", _small_ticks, axis="y")

    # -------------------------------------------------------------- shape of the plot area
    @friendly
    def use_true_shape(self: _Same) -> _Same:
        """One unit along x is as long as one unit along y, so maps and shapes are not stretched.
        chart.use_true_shape() (with chart.draw_contour(x="east", y="north", z="height") on sdata.get_example("island"))
        """
        return self._replace("use_true_shape", "axes", _true_shape)

    @friendly
    def make_square(self: _Same) -> _Same:
        """A square plot area, whatever the numbers on the axes. chart.make_square()"""
        return self._replace("make_square", "axes", _make_square)

    # -------------------------------------------------------------- colour bar
    def _colour_bar_place(self, place):
        self._set(colour_bar_place=place)
        return self._replace("colour_bar_place", "finish", _check_colour_bar_place)

    @friendly
    def put_colour_bar_at_bottom(self: _Same) -> _Same:
        """The colour bar under the chart, lying down. chart.put_colour_bar_at_bottom()
        (with chart.draw_heatmap(x="month", y="city", value="rain") on sdata.get_example("weather"))
        """
        return self._colour_bar_place("bottom")

    @friendly
    def put_colour_bar_at_top(self: _Same) -> _Same:
        """The colour bar above the chart, lying down. chart.put_colour_bar_at_top()
        (with chart.draw_heatmap(x="month", y="city", value="rain") on sdata.get_example("weather"))
        """
        return self._colour_bar_place("top")

    @friendly
    def put_colour_bar_at_left(self: _Same) -> _Same:
        """The colour bar on the left of the chart. chart.put_colour_bar_at_left()
        (with chart.draw_heatmap(x="month", y="city", value="rain") on sdata.get_example("weather"))
        """
        return self._colour_bar_place("left")

    put_color_bar_at_bottom = put_colour_bar_at_bottom  # American spelling, same word
    put_color_bar_at_top = put_colour_bar_at_top  # American spelling, same word
    put_color_bar_at_left = put_colour_bar_at_left  # American spelling, same word

    @friendly
    def hide_colour_bar(self: _Same) -> _Same:
        """No colour bar beside a heatmap, contour map or surface. chart.hide_colour_bar()

        The colours stay; only the bar that explains them goes, so say in words what they mean.
        """
        return self._replace("hide_colour_bar", "finish", _hide_colour_bar)

    hide_color_bar = hide_colour_bar  # American spelling, same word

    @friendly
    def put_ticks_colour_bar(self: _Same, *values, labels=None) -> _Same:
        """Where the marks on the colour bar go. chart.put_ticks_colour_bar(0, 10, 20, 30)
        (with chart.draw_heatmap(x="month", y="city", value="rain") on sdata.get_example("weather"))

        labels=["dry", "wet"] writes your own words at those places (one for each mark).
        """
        if len(values) == 1 and is_listlike(values[0]):
            values = tuple(values[0])
        if not values:
            raise SimplydataError(".put_ticks_colour_bar() needs the places of the marks, for example "
                                  "chart.put_ticks_colour_bar(0, 10, 20).")
        for v in values:
            if not _is_number(v):
                raise SimplydataError(f".put_ticks_colour_bar() needs numbers, not {v!r}.\n"
                                      "For example chart.put_ticks_colour_bar(0, 10, 20).")
        if labels is not None:
            if isinstance(labels, str) or not is_listlike(labels) or len(labels) != len(values):
                raise SimplydataError(f".put_ticks_colour_bar() got {len(values)} places, so labels= needs "
                                      f"{len(values)} words in a list, such as labels=[\"low\", ...].")
            labels = [str(t) for t in labels]
        return self._replace("put_ticks_colour_bar", "text", _ticks_colour_bar, values=[float(v) for v in values],
                             labels=labels)

    put_ticks_color_bar = put_ticks_colour_bar  # American spelling, same word

    # -------------------------------------------------------------- what it shows
    @friendly
    def say_what_it_shows(self) -> str:
        """Say in words what the chart shows, for a caption or for readers who cannot see it.
        chart.say_what_it_shows() (with chart.draw_bars(x="class", y="marks") on sdata.get_example("marks"))

        Prints and gives back the title, each chart type you drew with its columns and groups (3 lines,
        one for each city ...), error bars and lines on top, the name and range of each axis (or the
        names along it), the legend and the colour bar. It is read from your steps and from the chart
        as drawn: nothing is worked out. Add what the chart means in your own words.
        """
        from .._core import chart_notes

        with chart_notes():
            text = describe_chart(self)
        print(text)
        return text

    # -------------------------------------------------------------- rug lines
    @friendly
    def draw_rug_lines(self: _Same, x=None, y=None, colour=None, transparency=None, thickness=None) -> _Same:
        """A short line at each value along the axis, so every value shows. chart.draw_rug_lines(x="marks")
        (with chart.draw_density(x="marks") on sdata.get_example("marks"))

        Good under a density curve or beside dots. y="marks" puts them up the y-axis instead (both: x= and
        y=). colour="class" gives each group its own colour; transparency= and thickness= as on lines.
        """
        transparency = check_transparency("draw_rug_lines", transparency)
        thickness = check_thickness("draw_rug_lines", thickness)
        if x is None and y is None:
            raise SimplydataError('.draw_rug_lines() needs x= (or y=), for example chart.draw_rug_lines(x="marks").')
        group, _ = colour_role(self._data, colour)
        check(self._data, x=x, y=y, colour=group)
        from .charts import _check_numbers

        _check_numbers(self._data, "draw_rug_lines", x=x, y=y)
        self._need_axes("draw_rug_lines")
        return self._add("draw_rug_lines", "draw", _draw_rug_lines, x=x, y=y, colour=colour, transparency=transparency,
                         thickness=thickness)

    # -------------------------------------------------------------- wind rose
    @friendly
    def draw_wind_rose(self: _Same, direction=None, speed=None, every=30, transparency=None) -> _Same:
        """Bars round a compass: how often each direction (and speed) occurs.
        chart.draw_wind_rose(direction="wind_direction", speed="wind_speed") (with sdata.get_example("weather"))

        direction= holds compass degrees (0 north, 90 east); every=30 makes a bar for every 30 degrees,
        centred on north. speed= stacks the counts in speed bands at round numbers, slowest at the
        middle; without it each bar is one count. Works for currents and waves as well as wind.
        """
        transparency = check_transparency("draw_wind_rose", transparency)
        if direction is None:
            raise SimplydataError('.draw_wind_rose() needs direction=, for example '
                                  'chart.draw_wind_rose(direction="wind_direction", speed="wind_speed").')
        if not _is_number(every) or not 1 <= every <= 90 or abs(360 / every - round(360 / every)) > 1e-9:
            raise SimplydataError(f"every= in .draw_wind_rose() is the width of each bar in degrees, a number that "
                                  f"goes into 360 evenly (such as 10, 22.5, 30 or 45), not {every!r}.")
        check(self._data, angle=direction, distance=speed)
        from .charts import _check_numbers

        _check_numbers(self._data, "draw_wind_rose", direction=direction, speed=speed)
        if isinstance(speed, str):
            speeds = pd.to_numeric(self._data[speed], errors="coerce")
            below = speeds[speeds < 0]
            if len(below):
                raise SimplydataError(
                    f'.draw_wind_rose() needs speeds of 0 or more, but "{speed}" has {len(below)} below 0 (smallest: '
                    f"{below.min():g}). Fix or remove those rows first.")
        self._need_axes("draw_wind_rose", "polar")
        return self._add("draw_wind_rose", "draw", _draw_wind_rose, angle=direction, distance=speed, every=float(every),
                         transparency=transparency)

    # -------------------------------------------------------------- 3D
    @friendly
    def draw_lines_3d(self: _Same, x=None, y=None, z=None, colour=None, transparency=None, thickness=None) -> _Same:
        """Lines in a 3D box, through the points in the order of the table.
        chart.draw_lines_3d(x="east", y="north", z="height") (with sdata.get_example("island"))

        colour="track" draws one line per group. transparency= and thickness= as on draw_lines.
        """
        transparency = check_transparency("draw_lines_3d", transparency)
        thickness = check_thickness("draw_lines_3d", thickness)
        group, _ = colour_role(self._data, colour)
        self._xyz("draw_lines_3d", x, y, z, colour=group)
        self._need_axes("draw_lines_3d", "3d")
        return self._add("draw_lines_3d", "draw", _draw_lines_3d, x=x, y=y, z=z, colour=colour,
                         transparency=transparency, thickness=thickness)

    @friendly
    def label_z(self: _Same, text) -> _Same:
        """The name of the z-axis (the height) of a 3D chart. chart.label_z("Height (m)")
        (with chart.draw_surface(x="east", y="north", z="height") on sdata.get_example("island"))
        """
        if text is None or isinstance(text, bool):
            raise SimplydataError('.label_z() needs some words, for example chart.label_z("Height (m)").')
        return self._replace("label_z", "text", _label_z, text=str(text))

    @friendly
    def set_range_z(self: _Same, low=None, high=None) -> _Same:
        """From where to where the z-axis of a 3D chart goes. chart.set_range_z(-10, 20)
        (with chart.draw_surface(x="east", y="north", z="height") on sdata.get_example("island"))

        Use None to fix only one end: chart.set_range_z(0, None).
        """
        example = "chart.set_range_z(0, 100), or chart.set_range_z(0, None) to fix only the low end"
        if low is None and high is None:
            raise SimplydataError(f".set_range_z() needs at least one end.\nFor example: {example}")
        for name, v in (("low", low), ("high", high)):
            if v is not None and not _is_number(v):
                raise SimplydataError(f".set_range_z() needs numbers, but {name} is {v!r}.\nFor example: {example}")
        if low is not None and high is not None and not low < high:
            raise SimplydataError(f".set_range_z({low!r}, {high!r}): the low end must be smaller than the high end.")
        return self._replace("set_range_z", "axes", _range_z, low=low, high=high)

    @friendly
    def put_ticks_z(self: _Same, *values, labels=None) -> _Same:
        """Where the marks on the z-axis of a 3D chart go. chart.put_ticks_z(-10, 0, 10, 20)
        (with chart.draw_surface(x="east", y="north", z="height") on sdata.get_example("island"))

        labels=["deep", "sea level", "hill", "top"] writes your own words at those places.
        """
        if len(values) == 1 and is_listlike(values[0]):
            values = tuple(values[0])
        if not values:
            raise SimplydataError(".put_ticks_z() needs the places of the ticks, for example "
                                  "chart.put_ticks_z(0, 10, 20).")
        for v in values:
            if not _is_number(v):
                raise SimplydataError(f".put_ticks_z() needs numbers, not {v!r}.\nFor example chart.put_ticks_z(0, 10, 20)")
        if labels is not None:
            if isinstance(labels, str) or not is_listlike(labels) or len(labels) != len(values):
                raise SimplydataError(f".put_ticks_z() got {len(values)} ticks, so labels= needs {len(values)} words "
                                      "in a list.")
            labels = [str(t) for t in labels]
        return self._replace("put_ticks_z", "axes", _ticks_z, values=[float(v) for v in values], labels=labels)

    @friendly(others={"elev": "height", "elevation": "height", "azim": "around", "azimuth": "around"})
    def look_from(self: _Same, height=30, around=-60) -> _Same:
        """The angle a 3D chart is seen from. chart.look_from(height=20, around=45)
        (with chart.draw_surface(x="east", y="north", z="height") on sdata.get_example("island"))

        height= is how many degrees above the ground you look from (90 is straight down, 0 is
        from the side); around= is how many degrees you walk round it. Normal is height=30, around=-60.
        """
        if not _is_number(height) or not -90 <= height <= 90:
            raise SimplydataError(f"height= in .look_from() is degrees above the ground, from -90 to 90, such as "
                                  f"height=30, not {height!r}.")
        if not _is_number(around):
            raise SimplydataError(f"around= in .look_from() is degrees round the chart, such as around=45, "
                                  f"not {around!r}.")
        return self._replace("look_from", "axes", _look_from, height=float(height), around=float(around))

    view_from = look_from  # the name approved first (charts_design, 2026-11-15), same word

