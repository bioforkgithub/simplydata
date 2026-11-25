"""Run an underneath entry next to its simplydata word and compare the two results.

Used by tests/test_underneath.py and by the reliability report (validation/make_report.py), so the
manual's boxes, the tests and the report check the same thing in the same way.

    check_entry(entry)                  -> [Outcome, ...]   one per library block (and table engine)
    chart_facts(ax)                     -> {fact: value}    what a chart shows, as data
    compare_charts(a, b, check, tol)    -> [difference, ...]
"""

from __future__ import annotations

import ast
import contextlib
import io
import math
import textwrap
from dataclasses import dataclass, field

import numpy as np

from . import CHART_FACTS, Entry

OLD_NAME_NOTE = "is now called"


@dataclass
class Outcome:
    """One comparison: the word against one library block (on one table engine)."""

    word: str
    library: str
    engine: str
    compare: str
    tolerance: float
    passed: bool
    differences: list = field(default_factory=list)
    skipped: str = ""  # why it did not run (R missing), else ""

    @property
    def status(self) -> str:
        return "skipped" if self.skipped else ("pass" if self.passed else "FAIL")


# ---------------------------------------------------------------- running code
def run_python(source: str, namespace: dict | None = None):
    """Run Python code; give back (value of the last line if it is an expression, what it printed, namespace)."""
    import simplydata

    ns = {"sdata": simplydata, "__name__": "__underneath__"} if namespace is None else namespace
    ns.setdefault("sdata", simplydata)
    tree = ast.parse(textwrap.dedent(source))
    last = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
    printed = io.StringIO()
    value = None
    with contextlib.redirect_stdout(printed):
        exec(compile(tree, "<underneath>", "exec"), ns)  # noqa: S102 - our own code, from the registry
        if last is not None:
            value = eval(compile(ast.Expression(last.value), "<underneath>", "eval"), ns)  # noqa: S307
    return value, printed.getvalue(), ns


@contextlib.contextmanager
def practice_files():
    """While the library code runs, the folder of the practice tables is the working folder, so the code reads a
    practice table from its file as anyone would: pd.read_csv("marks.csv"). (sdata.get_example("marks") gives a
    simplydata table, which the library code does not use: it reads the same file with the library itself.)"""
    import os
    from importlib.resources import as_file, files

    with as_file(files("simplydata.data")) as folder:
        before = os.getcwd()
        os.chdir(folder)
        try:
            yield
        finally:
            os.chdir(before)


@contextlib.contextmanager
def _practice_tables_as(engine: str):
    """While ours runs, sdata.get_example gives tables held by Polars (engine="polars") instead of pandas."""
    import simplydata

    if engine == "pandas":
        yield
        return
    original = simplydata.get_example

    def as_polars(name=None, **options):
        found = original(name, **options)
        if options:  # from_r_package= gives a pandas-held simplydata table, as a user gets it
            return found
        return None if found is None else simplydata.table(found, fast=True)

    simplydata.get_example = as_polars
    try:
        yield
    finally:
        simplydata.get_example = original


def run_ours(entry: Entry, engine: str = "pandas"):
    """Run the simplydata side; give back (result, printed)."""
    with _practice_tables_as(engine):
        value, printed, _ = run_python(entry.ours_code())
    return value, printed


def engines(entry: Entry) -> list[str]:
    """Table words run on a pandas and on a Polars table; other words on pandas."""
    if entry.word.startswith("table."):
        return ["pandas", "polars"]
    return ["pandas"]


# ---------------------------------------------------------------- what a chart shows
def _axes_of(value, library_side: bool = False):
    """The Axes a result stands for: a simplydata chart, a Figure or an Axes. Only the library side may
    fall back to the current figure (seaborn and matplotlib draw on it); a simplydata word that gives
    back anything else is an error, so a chart is never compared with itself."""
    import matplotlib.pyplot as plt
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    if isinstance(value, Axes):
        return value
    if isinstance(value, Figure):
        return value.axes[0]
    if hasattr(value, "_render"):
        return value._render().axes[0]
    if not library_side:
        raise TypeError(f"the simplydata code gave back {type(value).__name__}, not a chart: end ours= with the "
                        "chart (chart.draw_bars(...) gives it back)")
    if not plt.get_fignums():
        raise TypeError("the library code drew no chart")
    return plt.gcf().axes[0]


def _colour_groups(colours) -> list[int]:
    """Each item's colour as the number of its colour in order of first appearance: [0, 0, 1, 2, 1].
    Which items share a colour is compared, not the colours themselves (simplydata has its own palette)."""
    seen: dict = {}
    out = []
    for c in colours:
        key = tuple(np.round(np.asarray(c, dtype=float), 6))
        out.append(seen.setdefault(key, len(seen)))
    return out


def chart_facts(ax) -> dict:
    """What a chart shows, as data: compare these, not pixels.

    bars              sorted (x, y, width, height) of every bar (Rectangle) on the axes
    bar_colour_groups which bars share a colour, in the sorted order of bars
    dots              every dot's (x, y), group by group as drawn
    dot_size_shares   each dot's size as a share of the biggest (simplydata's look scales all sizes)
    dot_colour_groups which dots share a colour
    lines             (x values, y values) of every line (names on a category axis read as their places 0, 1,
                      2 ...; straight lines right across the chart are in ax_lines instead)
    labels            (x label, y label, title)
    ticks             the words under the x axis and beside the y axis
    legend            the legend's title and entries
    limits            (x limits, y limits)
    scales            ("linear" or "log", for x and y)
    panels            the number of charts in the figure
    texts             the other words on the figure (titles above several panels, notes, captions, numbers on
                      bars), sorted: (words on the figure, words on the chart)
    font_sizes        the font sizes of the title, the x and y labels, the x and y tick labels and the legend
    size              the figure's width and height in inches
    legend_place      each legend: on the chart or on the figure, matplotlib's place code, the side outside the
                      chart (empty inside it), its number of columns, its title and entries
    colours           the colours themselves (as #rrggbbaa): of the bars (sorted as in bars), the dots and the lines
    tick_angles       the angle, the alignment and the rotation mode of each tick label, under the x axis and
                      beside the y axis
    shapes            the corners of every filled shape that is not a bar (violins, boxes, bands)
    cells             the numbers behind each grid of coloured cells (a heatmap), its colour map and the two
                      numbers at the ends of the colour scale
    line_styles       the dash pattern, the width (none for a line of markers only), the zorder (drawing order)
                      and the marker of every line
    text_places       each word on the chart (sorted): where it points (annotations), where it sits, its angle and
                      alignment, and the box behind it (or none)
    shape_colours     the fill colour of every filled shape that is not a bar (as #rrggbbaa)
    panel_styles      for each set of axes in the figure: the sizes, rim widths and colours of its dots, the
                      colours of its bars, its drawing order and whether its background is drawn
    every_panel       for each set of axes shown in the figure (second y-axes too): its labels, title, dots,
                      bars, lines, filled shapes and axis ranges
    grid              whether grid lines are shown across the x axis and across the y axis
    fonts             the font each of the title, the x label and the y label is written in
    polar_start       on a round (polar) chart: where 0 sits (the angle from the right, in radians) and the
                      direction angles go (1 anticlockwise, -1 clockwise); empty on a flat chart
    in_3d             on a 3D chart: the z label, the z range, every 3D dot's (x, y, z) and the height behind the
                      colour of each piece of a surface; empty on a flat chart
    segments          the short lines drawn as one set (vlines, hlines, error bars): their ends and their widths
    insets            each small chart inside the chart (side histograms, zoom boxes): its place inside the chart
                      and what it shows (as every_panel)
    colour_bars       each colour bar beside the chart: its label and the range of its scale
    ax_lines          each straight line drawn right across the chart (axline): a point on it, a second point or
                      its slope
    tick_places       where the ticks are, along the x axis and along the y axis (in the axis's own numbers: names
                      under bars sit at 0, 1, 2 ...)
    """
    from .._numbers_drawn import dots_of, rectangles_of  # the readers of chart.get_numbers_drawn()

    bars = sorted(((float(r.get_x()), float(r.get_y()), float(r.get_width()), float(r.get_height()), r.get_facecolor())
                   for r in rectangles_of(ax)), key=lambda b: b[:4])
    dots, sizes, dot_colours = [], [], []
    for coll, offsets in dots_of(ax):
        dots.extend(map(tuple, offsets))
        s = np.asarray(coll.get_sizes(), dtype=float)
        if len(s) == len(offsets):
            sizes.extend(s)
        else:  # one size for every dot, or none
            sizes.extend([s[0] if len(s) else np.nan] * len(offsets))
        fc = coll.get_facecolors()
        dot_colours.extend(fc if len(fc) == len(offsets) else [fc[0] if len(fc) else (0, 0, 0, 0)] * len(offsets))
    sizes = np.asarray(sizes, dtype=float)
    biggest = np.nanmax(sizes) if sizes.size and not np.all(np.isnan(sizes)) else 1.0
    legend = ax.get_legend()
    fig = ax.get_figure()
    return {
        "bars": [b[:4] for b in bars],
        "bar_colour_groups": _colour_groups([b[4] for b in bars]),
        "dots": dots,
        "dot_size_shares": list(sizes / biggest) if sizes.size else [],
        "dot_colour_groups": _colour_groups(dot_colours),
        "lines": [_line_xy(line) for line in ax.get_lines() if not _is_ax_line(line)],
        "labels": (ax.get_xlabel(), ax.get_ylabel(), ax.get_title()),
        "ticks": ([t.get_text() for t in ax.get_xticklabels()], [t.get_text() for t in ax.get_yticklabels()]),
        "legend": (([legend.get_title().get_text()] + [t.get_text() for t in legend.get_texts()])
                   if legend is not None else []),
        "limits": (tuple(map(float, ax.get_xlim())), tuple(map(float, ax.get_ylim()))),
        "scales": (ax.get_xscale(), ax.get_yscale()),
        "panels": len([a for a in fig.axes if a.get_label() != "<colorbar>"]) if fig is not None else 1,
        "texts": _texts(ax),
        "font_sizes": _font_sizes(ax),
        "size": tuple(map(float, _root(ax).get_size_inches())) if _root(ax) is not None else (),
        "legend_place": _legend_places(ax),
        "colours": ([_hex(b[4]) for b in bars], [_hex(c) for c in dot_colours],
                    [_hex(line.get_color()) for line in ax.get_lines()]),
        "tick_angles": ([(float(t.get_rotation()), t.get_ha(), t.get_rotation_mode()) for t in ax.get_xticklabels()],
                        [(float(t.get_rotation()), t.get_ha(), t.get_rotation_mode()) for t in ax.get_yticklabels()]),
        "shapes": _shapes(ax),
        "cells": _cells(ax),
        "every_panel": [_panel(a) for a in _panels(ax)],
        # a line drawn only as markers (linestyle "None") has no width to see, so its width is left out (nan)
        "line_styles": [(str(line.get_linestyle()),
                         float(line.get_linewidth()) if str(line.get_linestyle()) != "None" else math.nan,
                         float(line.get_zorder()), str(line.get_marker()))
                        for line in ax.get_lines()],
        "text_places": sorted((_text_place(t) for t in ax.texts if _shown(t)), key=repr),
        "shape_colours": _shape_colours(ax),
        "panel_styles": [_panel_style(a) for a in _panels(ax)],
        "grid": tuple(any(g.get_visible() for g in axis.get_gridlines()) for axis in (ax.xaxis, ax.yaxis)),
        "fonts": tuple(t.get_fontname() for t in (ax.title, ax.xaxis.label, ax.yaxis.label)),
        "polar_start": ((float(ax.get_theta_offset()), float(ax.get_theta_direction())) if ax.name == "polar"
                        else ()),
        "in_3d": _in_3d(ax),
        "segments": [(_sized(np.concatenate(c.get_segments()) if c.get_segments() else []),
                      list(np.asarray(c.get_linewidths(), dtype=float)))
                     for c in ax.collections if c.__class__.__name__ == "LineCollection"],
        "insets": [(_inset_place(ax, a), _panel(a)) for a in ax.child_axes if a.get_visible() and _is_panel(a)],
        "colour_bars": [(a.get_ylabel() or a.get_xlabel(),
                         tuple(map(float, a.get_ylim() if a.get_ylabel() or not a.get_xlabel() else a.get_xlim())))
                        for a in (fig.axes if fig is not None else []) if a.get_label() == "<colorbar>"],
        "ax_lines": [_ax_line(line) for line in ax.get_lines() if _is_ax_line(line)],
        "tick_places": ([float(v) for v in ax.get_xticks()], [float(v) for v in ax.get_yticks()]),
    }


def _is_ax_line(line) -> bool:
    return line.__class__.__name__ in ("AxLine", "_AxLine")


def _ax_line(line) -> tuple:
    """(a point, a second point or None, the slope or None) of a straight line drawn with axline. matplotlib before
    3.9 has no get_xy1/get_xy2/get_slope, only the private _xy1, _xy2, _slope."""
    def read(name):
        getter = getattr(line, f"get_{name}", None)
        return getter() if getter is not None else getattr(line, f"_{name}", None)

    xy1, xy2, slope = read("xy1"), read("xy2"), read("slope")
    return (tuple(map(float, xy1)), None if xy2 is None else tuple(map(float, xy2)),
            None if slope is None else float(slope))


def _line_xy(line) -> tuple:
    """(x values, y values) of a line as numbers; names on a category axis (an error bar at "A") as the places
    matplotlib puts them (0, 1, 2 ...)."""
    try:
        return np.asarray(line.get_xdata(), dtype=float), np.asarray(line.get_ydata(), dtype=float)
    except (TypeError, ValueError):
        return (np.asarray(line.get_xdata(orig=False), dtype=float),
                np.asarray(line.get_ydata(orig=False), dtype=float))


def _in_3d(ax) -> tuple:
    """(z label, z range, each 3D dot set's (x, y, z), each surface's heights): empty on a flat chart."""
    if ax.name != "3d":
        return ()
    # matplotlib keeps the z of 3D dots only in the private _offsets3d; tests/test_underneath.py pins it
    dots = [_sized(np.column_stack([np.ma.filled(np.ma.asarray(v, dtype=float), np.nan) for v in c._offsets3d]))
            for c in ax.collections if c.__class__.__name__ == "Path3DCollection"]
    heights = [_sized(np.ma.filled(np.ma.asarray(c.get_array(), dtype=float), np.nan))
               for c in ax.collections if c.__class__.__name__ == "Poly3DCollection" and c.get_array() is not None]
    return (ax.get_zlabel(), tuple(map(float, ax.get_zlim())), dots, heights)


def _inset_place(ax, inset) -> tuple:
    """[left, bottom, width, height] of a small chart inside ax, as parts of ax (rounded to 6 decimals)."""
    locator = inset.get_axes_locator()
    if locator is None:
        return ()
    try:
        holder = inset.get_figure(root=False)
    except TypeError:  # pragma: no cover - matplotlib before 3.10
        holder = inset.get_figure()
    box = locator(inset, None).transformed(holder.transSubfigure)
    box = box.transformed(ax.transAxes.inverted())
    return tuple(round(float(v), 6) for v in box.bounds)


def _root(ax):
    """The whole figure an Axes is on (not the part of a page it sits in)."""
    try:
        return ax.get_figure(root=True)
    except TypeError:  # pragma: no cover - matplotlib before 3.10
        return ax.get_figure()


def _hex(colour) -> str:
    from matplotlib.colors import to_hex

    return to_hex(colour, keep_alpha=True)


def _shown(text) -> str:
    return text.get_text().strip() if text is not None and text.get_visible() else ""


def _texts(ax) -> tuple:
    """(words on the figure and the parts of a page, words on the chart): each sorted, empty ones left out."""
    from matplotlib.text import Text

    root = _root(ax)
    on_figure = []
    figures = [root] if root is not None else []
    while figures:
        f = figures.pop(0)
        figures.extend(getattr(f, "subfigs", []))
        found = [getattr(f, name, None) for name in ("_suptitle", "_supxlabel", "_supylabel")]
        found += list(f.texts) + [a for a in f.artists if isinstance(a, Text)]
        on_figure += found
    on_figure = [_shown(t) for t in dict.fromkeys(t for t in on_figure if t is not None)]  # a title is in texts too
    on_chart = [_shown(t) for t in ax.texts]
    return sorted(t for t in on_figure if t), sorted(t for t in on_chart if t)


def _font_sizes(ax) -> tuple:
    def first(labels):
        return float(labels[0].get_fontsize()) if labels else math.nan

    root = _root(ax)
    legend = ax.get_legend() or next(iter(root.legends if root is not None else []), None)
    return (float(ax.title.get_fontsize()), float(ax.xaxis.label.get_fontsize()), float(ax.yaxis.label.get_fontsize()),
            first(ax.get_xticklabels()), first(ax.get_yticklabels()),
            first(legend.get_texts()) if legend is not None else math.nan)


def _legend_places(ax) -> list:
    # matplotlib keeps a legend's place, its outside side and its columns only in private attributes (_loc,
    # _outside_loc, _ncols); tests/test_underneath.py pins them, so a matplotlib change shows up there
    root = _root(ax)
    found = [("chart", ax.get_legend())] + [("figure", leg) for leg in (root.legends if root is not None else [])]
    return [(owner, int(leg._loc), getattr(leg, "_outside_loc", None) or "", int(leg._ncols),
             [leg.get_title().get_text()] + [t.get_text() for t in leg.get_texts()])
            for owner, leg in found if leg is not None and leg.get_visible()]


def _sized(points) -> tuple:
    """(how many, the array): arrays of different lengths are then compared by their length first."""
    points = np.asarray(points, dtype=float)
    return (len(points), points)


def _shapes(ax) -> list:
    from matplotlib.patches import Rectangle

    found = []
    for coll in ax.collections:
        if coll.__class__.__name__ in ("PathCollection", "QuadMesh", "LineCollection") or not hasattr(coll, "get_paths"):
            continue
        found += [_sized(path.vertices) for path in coll.get_paths()]
    found += [_sized(p.get_path().vertices) for p in ax.patches if not isinstance(p, Rectangle)]
    return found


def _cells(ax) -> list:
    grids = [c for c in ax.collections if c.__class__.__name__ == "QuadMesh"] + list(ax.images)
    return [_sized(np.ma.filled(np.ma.asarray(g.get_array(), dtype=float), np.nan).ravel())
            + (g.get_cmap().name, float(g.norm.vmin), float(g.norm.vmax)) for g in grids]


def _panels(ax) -> list:
    """Every set of axes in the whole figure that is shown (second y-axes too, colour bars left out), each followed by
    the axes drawn inside it (inset axes, as trend_and_season's four panels)."""
    root = _root(ax)
    if root is None:
        return []
    found = []
    for a in root.axes:
        if a.get_label() != "<colorbar>" and a.get_visible():
            found.append(a)
            found += [c for c in getattr(a, "child_axes", []) if c.get_visible() and c not in found and _is_panel(c)]
    return found


def _is_panel(ax) -> bool:
    """A second scale drawn with secondary_xaxis / secondary_yaxis (add_second_x(formula=)) is a child of the axes
    but not a panel: it has no title and no marks of its own."""
    return ax.__class__.__name__ != "SecondaryAxis"


def _text_place(t) -> tuple:
    """(words, the place an annotation points at or None, where the words sit, angle, alignment, its box or None)."""
    box = t.get_bbox_patch()
    return (_shown(t), tuple(map(float, t.xy)) if hasattr(t, "xy") else None, tuple(map(float, t.get_position())),
            float(t.get_rotation()), t.get_ha(), t.get_va(), None if box is None else _hex(box.get_facecolor()))


def _filled(ax) -> list:
    from matplotlib.patches import Rectangle

    found = [c for c in ax.collections
             if c.__class__.__name__ not in ("PathCollection", "QuadMesh", "LineCollection") and hasattr(c, "get_paths")]
    return found + [p for p in ax.patches if not isinstance(p, Rectangle)]


def _shape_colours(ax) -> list:
    out = []
    for artist in _filled(ax):
        faces = np.atleast_2d(artist.get_facecolor())
        out += [_hex(c) for c in faces] if len(faces) else ["none"]
    return out


def _panel_style(ax) -> tuple:
    from matplotlib.patches import Rectangle

    dots = [c for c in ax.collections if c.__class__.__name__ == "PathCollection"]
    return ([list(np.asarray(c.get_sizes(), dtype=float)) for c in dots],
            [list(np.asarray(c.get_linewidths(), dtype=float)) for c in dots],
            [[_hex(f) for f in c.get_facecolors()] for c in dots],
            [_hex(r.get_facecolor()) for r in sorted((r for r in ax.patches if isinstance(r, Rectangle)),
                                                    key=lambda r: (r.get_x(), r.get_y()))],
            float(ax.get_zorder()), bool(ax.patch.get_visible()))


def _panel(ax) -> tuple:
    """What one set of axes shows: labels, title, dots, bars, lines and filled shapes (for figures with several)."""
    from matplotlib.patches import Rectangle

    dots = [tuple(o) for c in ax.collections if c.__class__.__name__ == "PathCollection"
            for o in np.asarray(c.get_offsets(), dtype=float).reshape(-1, 2)]
    bars = sorted((float(r.get_x()), float(r.get_y()), float(r.get_width()), float(r.get_height()))
                  for r in ax.patches if isinstance(r, Rectangle))
    # lines with no points (seaborn adds them for legend entries) show nothing, so they are left out
    lines = [tuple(_sized(v) for v in _line_xy(line)) for line in ax.get_lines()
             if len(line.get_xdata()) and not _is_ax_line(line)]
    return (ax.get_xlabel(), ax.get_ylabel(), ax.get_title(), ax.get_title(loc="left"),
            _sized(dots) if dots else (0,), _sized(bars) if bars else (0,), lines, _shapes(ax),
            tuple(map(float, ax.get_xlim())), tuple(map(float, ax.get_ylim())))


def _same(a, b, tol: float) -> bool:
    """Equal, with numbers compared to a relative tolerance (and 1e-12 absolute, for zeros)."""
    if isinstance(a, str) or isinstance(b, str):
        return a == b
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)) or isinstance(a, np.ndarray):
        try:
            if len(a) != len(b):
                return False
        except TypeError:
            return False
        if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
            a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
            if a.shape != b.shape:  # a grid and a list, or (n, 1) and (n,), are not the same result
                return False
            return bool(np.allclose(a, b, rtol=tol, atol=1e-12, equal_nan=True))
        return all(_same(x, y, tol) for x, y in zip(a, b))
    if a is None or b is None:
        return a is b
    try:
        x, y = float(a), float(b)
    except (TypeError, ValueError):
        return a == b
    if math.isnan(x) or math.isnan(y):
        return math.isnan(x) and math.isnan(y)
    return math.isclose(x, y, rel_tol=tol, abs_tol=1e-12)


def compare_charts(ours: dict, theirs: dict, check, tol: float) -> list[str]:
    out = []
    for name in check:
        if name not in CHART_FACTS:
            raise ValueError(f"{name} is not a chart fact; use one of {', '.join(CHART_FACTS)}")
        if not _same(ours[name], theirs[name], tol):
            out.append(f"{name}: simplydata {_short(ours[name])} | library {_short(theirs[name])}")
    return out


def _short(value, width: int = 200) -> str:
    text = repr(value)
    return text if len(text) <= width else text[: width - 3] + "..."


# ---------------------------------------------------------------- comparing results
def _as_pandas(value):
    import pandas as pd

    if hasattr(value, "as_pandas"):
        value = value.as_pandas()
    if hasattr(value, "to_pandas") and not isinstance(value, (pd.DataFrame, pd.Series)):
        value = value.to_pandas()
    if isinstance(value, pd.Series):
        value = value.reset_index()
    return value.reset_index(drop=True)


def compare_tables(ours, theirs, names: dict, tol: float) -> list[str]:
    import pandas as pd

    a = _as_pandas(ours).rename(columns=names)
    b = _as_pandas(theirs)
    if list(a.columns) != list(b.columns):
        return [f"columns: simplydata {list(a.columns)} | library {list(b.columns)}"]
    if a.shape != b.shape:
        return [f"shape: simplydata {a.shape} | library {b.shape}"]
    out = []
    for col in a.columns:
        x, y = a[col], b[col]
        if pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y):
            if not np.allclose(x.to_numpy(dtype=float), y.to_numpy(dtype=float), rtol=tol, atol=1e-12, equal_nan=True):
                out.append(f"{col}: the numbers differ")
        elif [str(v) for v in x] != [str(v) for v in y]:
            out.append(f"{col}: the values differ")
    return out


def compare_result(ours, theirs: dict, fields, tol: float, row_name: str = "") -> list[str]:
    frame = _as_pandas(ours)
    if row_name:
        found = frame[frame["term"] == row_name]
        if not len(found):
            return [f"no row {row_name!r} in simplydata's result"]
        row = found.iloc[0]
    else:
        row = frame.iloc[0]
    out = []
    for name in fields:
        if name not in theirs:
            out.append(f"{name}: the library code does not give it")
        elif not _same(row[name], theirs[name], tol):
            out.append(f"{name}: simplydata {row[name]!r} | library {theirs[name]!r}")
    return out


def compare_printed(ours: str, theirs: str) -> list[str]:
    """Every line the library code printed appears, in the same order, in what simplydata printed (simplydata may
    print more: a sentence before or after). Spaces at the ends of lines are left out."""
    mine = [line.rstrip() for line in ours.splitlines()]
    wanted = [line.rstrip() for line in theirs.splitlines() if line.strip()]
    if not wanted:
        return ["the library code printed nothing"]
    at = 0
    for line in wanted:
        while at < len(mine) and mine[at] != line:
            at += 1
        if at == len(mine):
            return [f"simplydata did not print the line {line!r} (in this order)"]
        at += 1
    return []


def compare_values(ours, theirs, tol: float) -> list[str]:
    return [] if _same(ours, theirs, tol) else [f"simplydata {ours!r} | library {theirs!r}"]


def compare(entry: Entry, ours, theirs) -> list[str]:
    if entry.compare == "chart":
        return compare_charts(chart_facts(_axes_of(ours)), chart_facts(_axes_of(theirs, library_side=True)),
                              entry.check, entry.tolerance)
    if entry.compare == "table":
        return compare_tables(ours, theirs, entry.names, entry.tolerance)
    if entry.compare == "result":
        return compare_result(ours, theirs, entry.fields, entry.tolerance, entry.row)
    if entry.compare == "value":
        if hasattr(ours, "as_numpy"):  # simplydata numbers or a grid: ours ends with the word itself
            ours = ours.as_numpy()
        return compare_values(ours, theirs, entry.tolerance)
    raise ValueError(f"{entry.word}: compare={entry.compare!r} cannot be run")


# ---------------------------------------------------------------- one entry
def _r_values(entry: Entry) -> dict:
    """The values the R block uses, made by r_inputs from the practice table."""
    with practice_files():
        _, _, ns = run_python(entry.r_inputs)
    return {k: v for k, v in ns.items() if not k.startswith("__") and k != "sdata" and isinstance(v, np.ndarray)}


def _run_with_r(entry: Entry):
    """Blocks as one program: R gets its values, the Python block after R carries on with R's answer."""
    from .._r import need_r, r_call

    namespace: dict = {}
    value = None
    seen_r = False
    for library, language, source in entry.blocks():
        if language == "r":
            # checked, not attached: the boxes call R packages by name (pROC::roc, drc::drm), and an attached
            # package can hide base R functions from later calls (drc's gaussian(), SparseM's matrix functions)
            need_r(entry.r_packages, f"the underneath code of {entry.word}")
            found = r_call(source, what=f"the underneath code of {entry.word}",
                           **_r_values(entry))
            for k, v in (found or {}).items():
                arr = np.asarray(v, dtype=float)
                namespace[k] = arr if arr.size != 1 else float(arr.reshape(-1)[0])
            seen_r = True
        elif seen_r:
            with practice_files():
                value, _, namespace = run_python(source, namespace)
    return value, namespace


def compare_legend_numbers(entry: Entry, ours, found: dict) -> list[str]:
    """The numbers simplydata writes in its legend (such as the AUC and its interval) against what R gave,
    to the digits printed (half a unit of the last printed digit)."""
    import re

    if not entry.legend_numbers:
        return []
    texts = chart_facts(_axes_of(ours))["legend"][1:]
    m = next((re.search(entry.legend_pattern, t) for t in texts if re.search(entry.legend_pattern, t)), None)
    if m is None:
        return [f"legend: no text matching {entry.legend_pattern!r} in {texts!r}"]
    out = []
    for name, shown in zip(entry.legend_numbers, m.groups()):
        decimals = len(shown.split(".")[1]) if "." in shown else 0
        if name not in found:
            out.append(f"legend: R gave no {name}")
        elif abs(float(shown) - float(found[name])) > 0.5 * 10 ** -decimals + 1e-12:
            out.append(f"legend {name}: simplydata shows {shown} | R {found[name]!r}")
    return out


def check_entry(entry: Entry) -> list[Outcome]:
    """Run the word and each library block, and compare them. R words that cannot run (no R) are skipped."""
    import matplotlib.pyplot as plt

    outcomes = []
    if entry.compare == "none":
        return [Outcome(entry.key, "-", "-", "none", 0.0, bool(entry.note.strip()),
                        [] if entry.note.strip() else ["a word with nothing underneath needs a note="])]
    for engine in engines(entry):
        try:
            if entry.uses_r:
                from .._r import r_ready

                needed = tuple(dict.fromkeys(entry.r_packages + entry.ours_r))
                if not r_ready(needed):
                    outcomes.append(Outcome(entry.key, "R", engine, entry.compare, entry.tolerance, False,
                                            skipped="R, rpy2 or the R packages " + ", ".join(needed)
                                                    + " are not installed"))
                    continue
                ours, printed = run_ours(entry, engine)
                theirs, found = _run_with_r(entry)
                differences = compare(entry, ours, theirs) + compare_legend_numbers(entry, ours, found)
                if OLD_NAME_NOTE in printed:
                    differences.append("the simplydata code uses an old name: " + printed.strip())
                library = " + ".join(lib for lib, _, _ in entry.blocks())
                outcomes.append(Outcome(entry.key, library, engine, entry.compare, entry.tolerance,
                                        not differences, differences))
                continue
            for library, _, source in entry.blocks():
                ours, printed = run_ours(entry, engine)
                with practice_files():
                    theirs, their_print, _ = run_python(source)
                if entry.compare == "printed":
                    differences = compare_printed(printed, their_print)
                else:
                    differences = compare(entry, ours, theirs)
                if OLD_NAME_NOTE in printed:
                    differences.append("the simplydata code uses an old name: " + printed.strip())
                outcomes.append(Outcome(entry.key, library, engine, entry.compare, entry.tolerance,
                                        not differences, differences))
                plt.close("all")
        finally:
            plt.close("all")
    return outcomes
