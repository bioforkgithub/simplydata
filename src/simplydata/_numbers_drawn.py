"""What a chart drew, as numbers: chart.get_numbers_drawn() and the chart facts of the tests.

matplotlib keeps every number it drew on the chart's axes: the x and y of each line (Line2D), the
positions of the dots (PathCollection offsets), the bars (Rectangle patches in a BarContainer), the
segments of stems and error bars (LineCollection), the low and high ends of bands (fill_between's
FillBetweenPolyCollection), the cells of heat maps (QuadMesh, AxesImage) and the slices of pies
(Wedge). This module reads them back from the drawn figure; it computes nothing new.

The readers below (lines_of, dots_of, rectangles_of) are shared with
simplydata._underneath.check.chart_facts, so the tests and chart.get_numbers_drawn() read a chart
in the same way.
"""

from __future__ import annotations

import math

import numpy as np

COLUMNS = ("panel", "layer", "kind", "series", "x", "y", "low", "high", "value", "colour", "colour name")


# ---------------------------------------------------------------- shared readers (chart_facts uses these)
def lines_of(ax) -> list:
    """Every line on the axes, as drawn: [(line, x values, y values)].

    A line drawn at named places (seaborn's error bars on an axis of groups) keeps the names as its data;
    then the numbers matplotlib turned them into (Line2D.get_xydata) are read instead."""
    found = []
    for line in ax.get_lines():
        try:
            xs, ys = np.asarray(line.get_xdata(), dtype=float), np.asarray(line.get_ydata(), dtype=float)
        except (TypeError, ValueError):
            xy = np.asarray(line.get_xydata(), dtype=float).reshape(-1, 2)
            xs, ys = xy[:, 0], xy[:, 1]
        found.append((line, xs, ys))
    return found


def dots_of(ax) -> list:
    """Every group of dots (a PathCollection with positions): [(collection, positions as an n x 2 array)]."""
    found = []
    for coll in ax.collections:
        offsets = np.asarray(coll.get_offsets(), dtype=float)
        if offsets.ndim != 2 or len(offsets) == 0 or coll.__class__.__name__ != "PathCollection":
            continue
        found.append((coll, offsets))
    return found


def rectangles_of(ax) -> list:
    """Every Rectangle patch on the axes (bars, histogram bars, boxes drawn as rectangles)."""
    from matplotlib.patches import Rectangle

    return [p for p in ax.patches if isinstance(p, Rectangle)]


# ---------------------------------------------------------------- the table of chart.get_numbers_drawn()
def _label(artist) -> str:
    """The artist's legend label; matplotlib's own names for unlabelled artists ("_child3") count as none."""
    text = artist.get_label() if hasattr(artist, "get_label") else ""
    text = "" if text is None else str(text)
    return "" if text.startswith("_") else text


# ---------------------------------------------------------------- colours (the colour column)
def _colour_names() -> dict:
    """Named colours by their code ("#0000ff" -> "blue"); where two names share a code, the plainer one."""
    from matplotlib import colors as mcolors

    names = {}
    for name in sorted(mcolors.CSS4_COLORS, key=lambda n: ("gray" in n, len(n), n)):
        names.setdefault(mcolors.CSS4_COLORS[name].lower(), name)
    for plain in ("cyan", "magenta"):  # rather than aqua and fuchsia
        names[mcolors.CSS4_COLORS[plain].lower()] = plain
    return names


_NAMES_BY_CODE: dict = {}


def colour_code(colour) -> str:
    """A drawn colour as matplotlib keeps it, written as a code: "#0072b2" ("#0072b280" when see-through).
    Empty when there is none (a dot with no fill and no edge)."""
    from matplotlib.colors import to_hex, to_rgba

    if colour is None:
        return ""
    try:
        if not isinstance(colour, str):
            array = np.asarray(colour, dtype=float)
            if array.ndim == 2:
                if not len(array):
                    return ""
                array = array[0]
            colour = tuple(array)
        rgba = to_rgba(colour)
    except (TypeError, ValueError):
        return ""
    if rgba[3] == 0:
        return ""
    return to_hex(rgba, keep_alpha=rgba[3] < 1)


def colour_name(code: str) -> str:
    """The name of a colour code when a named colour has exactly that code ("#0000ff" -> "blue"), else empty."""
    if not _NAMES_BY_CODE:
        _NAMES_BY_CODE.update(_colour_names())
    return _NAMES_BY_CODE.get((code or "").lower(), "")


def _each_colour(colours, n) -> list:
    """n colour codes from matplotlib's list of colours of a collection (one for all, or one each)."""
    try:
        array = np.asarray(colours, dtype=float)
    except (TypeError, ValueError):
        return [colour_code(colours)] * n
    if array.ndim == 1 and array.size in (3, 4):
        array = array[None, :]
    if array.ndim != 2 or not len(array):
        return [""] * n
    if len(array) == n:
        return [colour_code(c) for c in array]
    if len(array) == 1:
        return [colour_code(array[0])] * n
    return [""] * n  # colours that cannot be matched to the points: none rather than a wrong one


def _mapped(coll):
    """A collection coloured by numbers (a colour scale) gets its colours the way drawing gives them."""
    if hasattr(coll, "get_array") and coll.get_array() is not None:
        coll.update_scalarmappable()
    return coll


def _colour_key(artist):
    """The artist's main colour as a rounded RGBA tuple, or None."""
    from matplotlib.colors import to_rgba

    for getter in ("get_color", "get_facecolor", "get_edgecolor"):
        if not hasattr(artist, getter):
            continue
        try:
            colour = getattr(artist, getter)()
            if not isinstance(colour, str):
                array = np.asarray(colour, dtype=float)
                if array.ndim == 2:
                    if not len(array):
                        continue
                    array = array[0]
                colour = tuple(array)
            return tuple(round(float(v), 4) for v in to_rgba(colour))
        except (TypeError, ValueError):
            continue
    return None


def _legend_names(ax) -> dict:
    """The legend's names by colour, so a line drawn in a group's colour without its own label (a fitted
    line per group) gets the group's name."""
    legend = ax.get_legend()
    if legend is None:
        return {}
    names = {}
    for handle, text in zip(getattr(legend, "legend_handles", []), legend.get_texts()):
        key = _colour_key(handle) if handle is not None else None
        if key is not None and text.get_text():
            names.setdefault(key, text.get_text())
    return names


def _data_axes(artist, ax) -> tuple[bool, bool]:
    """Whether the artist's x and y are data values (False for a line at x= drawn across the whole height,
    whose y runs over the axes from 0 to 1, not over the data)."""
    try:
        return tuple(bool(v) for v in artist.get_transform().contains_branch_seperately(ax.transData))
    except (AttributeError, ValueError):
        return True, True


def _axis_reader(axis):
    """A function that turns the axis's drawn numbers back into what was plotted: dates for a date axis,
    the group names for an axis of named groups (matplotlib's category axis), numbers otherwise."""
    converter = axis.get_converter() if hasattr(axis, "get_converter") else getattr(axis, "converter", None)
    if converter is not None and type(converter).__module__ == "matplotlib.dates":
        from matplotlib import dates as mdates

        def as_date(v):
            if v is None or not np.isfinite(v):
                return None
            try:
                return mdates.num2date(v).replace(tzinfo=None)
            except (OverflowError, ValueError):  # a point far outside the dates (a band drawn to the edge)
                return None

        return as_date, "date"
    if converter is not None and type(converter).__name__ == "StrCategoryConverter":
        units = axis.get_units()
        mapping = {int(i): str(name) for name, i in getattr(units, "_mapping", {}).items()}

        def as_name(v):
            if v is None or not np.isfinite(v):
                return None
            whole = int(round(v))
            return mapping.get(whole, v) if abs(v - whole) < 1e-9 else v

        return as_name, "group"
    return (lambda v: v), "number"


def _num(v):
    if v is None:
        return math.nan
    try:
        v = float(v)
    except (TypeError, ValueError):
        return math.nan
    return v


class _Rows:
    def __init__(self):
        self.rows = []

    def add(self, panel, layer, kind, series, x=math.nan, y=math.nan, low=math.nan, high=math.nan, value=math.nan,
            colour=""):
        colour = colour if isinstance(colour, str) else colour_code(colour)
        self.rows.append(dict(panel=panel, layer=layer, kind=kind, series=series, x=_num(x), y=_num(y),
                              low=_num(low), high=_num(high), value=_num(value), colour=colour,
                              **{"colour name": colour_name(colour)}))


def _containers(ax):
    """Which artists belong to bars, stems and error bars (matplotlib keeps them in ax.containers)."""
    from matplotlib.container import BarContainer, ErrorbarContainer, StemContainer

    bars, roles = [], {}
    for c in ax.containers:
        if isinstance(c, BarContainer):
            bars.append(c)
        elif isinstance(c, StemContainer):
            roles[id(c.stemlines)] = ("stem", _label(c))
            roles[id(c.markerline)] = ("stem top", _label(c))
            roles[id(c.baseline)] = ("stem base", _label(c))
        elif isinstance(c, ErrorbarContainer):
            for part in c.lines[2] if len(c.lines) > 2 else ():
                roles[id(part)] = ("error bar", _label(c))
            for cap in c.lines[1] if len(c.lines) > 1 else ():  # the little caps at the ends of the error bars
                roles[id(cap)] = ("error bar cap", _label(c))
    return bars, roles


def _band_rows(rows, panel, layer, coll, series):
    """fill_between: per path, the forward edge and the backward edge share their x values."""
    sideways = getattr(coll, "t_direction", "x") == "y"
    colour = _each_colour(coll.get_facecolor(), 1)[0]
    for path in coll.get_paths():
        v = np.asarray(path.vertices, dtype=float)
        n = (len(v) - 3) // 2
        if n < 1 or len(v) != 2 * n + 3:
            continue
        first, second = v[1:n + 1], v[n + 2:2 * n + 2][::-1]
        for (t, a), (_, b) in zip(first, second):
            if sideways:  # fill_betweenx (violins): the position is y, the band runs along x
                rows.add(panel, layer, "band", series, y=t, low=min(a, b), high=max(a, b), colour=colour)
            else:
                rows.add(panel, layer, "band", series, x=t, low=min(a, b), high=max(a, b), colour=colour)


def _segment_rows(rows, panel, layer, coll, kind, series):
    """Stems, error bars and other line segments: an upright segment gives its x, its end (y) and its
    low and high ends; a level one its y and its left and right ends (low, high)."""
    segments = coll.get_segments()
    colours = _each_colour(coll.get_colors(), len(segments))
    for seg, colour in zip(segments, colours):
        seg = np.asarray(seg, dtype=float)
        if len(seg) < 2:
            continue
        (x0, y0), (x1, y1) = seg[0], seg[-1]
        if x0 == x1:
            rows.add(panel, layer, kind, series, x=x0, y=y1, low=min(y0, y1), high=max(y0, y1), colour=colour)
        elif y0 == y1:
            rows.add(panel, layer, kind, series, x=x1, y=y0, low=min(x0, x1), high=max(x0, x1), colour=colour)
        else:
            for x, y in seg:
                rows.add(panel, layer, kind, series, x=x, y=y, colour=colour)


def numbers_of_panel(ax, panel: int):
    """The rows of one set of axes, and whether its x and y are dates or named groups."""
    from matplotlib import collections as mcollections
    from matplotlib.collections import LineCollection, PolyCollection, QuadMesh
    from matplotlib.contour import ContourSet
    from matplotlib.image import AxesImage
    from matplotlib.patches import PathPatch, Polygon, Wedge

    rows = _Rows()
    layer = 0
    bars, roles = _containers(ax)
    by_colour = _legend_names(ax)

    def name_of(artist, label=None):
        label = _label(artist) if label is None else label
        return label or by_colour.get(_colour_key(artist), "")

    if getattr(ax, "name", "") == "3d":
        return _numbers_of_3d(ax, panel, name_of), _axis_reader(ax.xaxis), _axis_reader(ax.yaxis)
    # fill_between's own collection (matplotlib 3.10 and later); older versions draw bands as plain polygons
    fill_between = getattr(mcollections, "FillBetweenPolyCollection", ())

    in_bars = set()
    for c in bars:
        layer += 1
        series = _label(c) or (name_of(c.patches[0]) if len(c.patches) else "")
        upright = getattr(c, "orientation", "vertical") != "horizontal"
        for p in c.patches:
            in_bars.add(id(p))
            if not p.get_visible():
                continue
            x, y, w, h = (float(p.get_x()), float(p.get_y()), float(p.get_width()), float(p.get_height()))
            colour = colour_code(p.get_facecolor())
            if upright:
                rows.add(panel, layer, "bar", series, x=x + w / 2, y=h, low=min(y, y + h), high=max(y, y + h),
                         colour=colour)
            else:
                rows.add(panel, layer, "bar", series, x=w, y=y + h / 2, low=min(x, x + w), high=max(x, x + w),
                         colour=colour)
    for p in rectangles_of(ax):
        if id(p) in in_bars or not p.get_visible() or (p.get_width() == 0 and p.get_height() == 0):
            continue  # an empty rectangle is a stand-in for a legend entry (seaborn), not drawn data
        layer += 1
        x, y, w, h = (float(p.get_x()), float(p.get_y()), float(p.get_width()), float(p.get_height()))
        xs, ys = _data_axes(p, ax)
        rows.add(panel, layer, "rectangle", name_of(p), x=x + w / 2 if xs else math.nan, y=h if ys else math.nan,
                 low=min(y, y + h) if ys else math.nan, high=max(y, y + h) if ys else math.nan,
                 colour=colour_code(p.get_facecolor()))
    for line, _, _ in lines_of(ax):
        # get_xydata: the numbers drawn, after matplotlib turned dates or group names into numbers
        xy = np.asarray(line.get_xydata(), dtype=float).reshape(-1, 2)
        xv, yv = xy[:, 0], xy[:, 1]
        if not line.get_visible() or len(xv) == 0:
            continue
        layer += 1
        only_markers = (str(line.get_linestyle()).lower() in ("none", "", " ")
                        and str(line.get_marker()).lower() not in ("none", "", " "))  # dots drawn by plot()
        kind, series = roles.get(id(line), ("dot" if only_markers else "line", name_of(line)))
        xs, ys = _data_axes(line, ax)
        # a number simplydata wrote next to a point (the best cut-off of trade_off_curve), kept on the line
        value = getattr(line, "simplydata_value", math.nan)
        colour = colour_code(line.get_markerfacecolor() if only_markers else line.get_color())
        if only_markers and not colour:  # hollow dots: the edge is the colour
            colour = colour_code(line.get_markeredgecolor())
        for x, y in zip(xv, yv):
            rows.add(panel, layer, kind, series, x=x if xs else math.nan, y=y if ys else math.nan, value=value,
                     colour=colour)
    dot_ids = set()
    for coll, offsets in dots_of(ax):
        if not coll.get_visible():
            continue
        dot_ids.add(id(coll))
        layer += 1
        series = name_of(coll)
        _mapped(coll)
        colours = _each_colour(coll.get_facecolors(), len(offsets))
        if not any(colours):  # hollow dots: the edge is the colour
            colours = _each_colour(coll.get_edgecolors(), len(offsets))
        for (x, y), colour in zip(offsets, colours):
            rows.add(panel, layer, "dot", series, x=x, y=y, colour=colour)
    for coll in ax.collections:
        if id(coll) in dot_ids or not coll.get_visible():
            continue
        if isinstance(coll, ContourSet):
            layer += 1
            paths = coll.get_paths()
            _mapped(coll)
            colours = _each_colour(coll.get_facecolor() if coll.filled else coll.get_edgecolor(), len(paths))
            for level, path, colour in zip(np.atleast_1d(coll.layers), paths, colours):
                for x, y in np.asarray(path.vertices, dtype=float):
                    rows.add(panel, layer, "contour", name_of(coll), x=x, y=y, value=level, colour=colour)
        elif isinstance(coll, fill_between):
            layer += 1
            _band_rows(rows, panel, layer, coll, name_of(coll))
        elif isinstance(coll, LineCollection):
            layer += 1
            kind, series = roles.get(id(coll), ("segment", name_of(coll)))
            _segment_rows(rows, panel, layer, coll, kind, series)
        elif isinstance(coll, QuadMesh):
            layer += 1
            values = np.ma.filled(np.ma.asarray(coll.get_array(), dtype=float), np.nan).ravel()
            corners = np.asarray(coll.get_coordinates(), dtype=float)
            centres = (corners[:-1, :-1] + corners[1:, 1:]) / 2
            gouraud = values.size != centres.size // 2
            if gouraud:  # shading="gouraud": one value at each corner, coloured in between
                centres = corners
            _mapped(coll)
            colours = [""] * values.size if gouraud else _each_colour(coll.get_facecolors(), values.size)
            for (x, y), v, colour in zip(centres.reshape(-1, 2), values, colours):
                rows.add(panel, layer, "cell", _label(coll), x=x, y=y, value=v, colour=colour)
        elif isinstance(coll, PolyCollection):
            layer += 1
            paths = coll.get_paths()
            colours = _each_colour(_mapped(coll).get_facecolors(), len(paths))
            for path, colour in zip(paths, colours):
                for x, y in np.asarray(path.vertices, dtype=float):
                    rows.add(panel, layer, "shape", _label(coll), x=x, y=y, colour=colour)
    for image in ax.get_images():
        if not isinstance(image, AxesImage) or not image.get_visible():
            continue
        values = np.ma.filled(np.ma.asarray(image.get_array(), dtype=float), np.nan)
        if values.ndim != 2:
            continue  # a picture (RGB), not a heat map
        layer += 1
        left, right, bottom, top = image.get_extent()
        n_rows, n_cols = values.shape
        colours = image.to_rgba(values)  # the colour matplotlib gives each cell
        for i in range(n_rows):
            for j in range(n_cols):
                x = left + (j + 0.5) * (right - left) / n_cols
                y = (top + (i + 0.5) * (bottom - top) / n_rows) if image.origin == "upper" else \
                    (bottom + (i + 0.5) * (top - bottom) / n_rows)
                rows.add(panel, layer, "cell", _label(image), x=x, y=y, value=values[i, j],
                         colour=colour_code(colours[i, j]) if np.isfinite(values[i, j]) else "")
    for p in ax.patches:  # outlines: step histograms (Polygon), filled boxes (PathPatch)
        if not p.get_visible() or not isinstance(p, (Polygon, PathPatch)) or id(p) in in_bars:
            continue
        xs, ys = _data_axes(p, ax)
        if not (xs or ys):
            continue
        layer += 1
        corners = p.get_xy() if isinstance(p, Polygon) else p.get_path().vertices
        colour = colour_code(p.get_facecolor()) or colour_code(p.get_edgecolor())  # an outline has no fill
        for x, y in np.asarray(corners, dtype=float):
            rows.add(panel, layer, "shape", name_of(p), x=x if xs else math.nan, y=y if ys else math.nan,
                     colour=colour)
    wedges = [p for p in ax.patches if isinstance(p, Wedge) and p.get_visible()]
    if wedges:
        layer += 1
        for p in wedges:
            rows.add(panel, layer, "slice", _label(p), low=p.theta1, high=p.theta2,
                     value=(p.theta2 - p.theta1) / 360.0, colour=colour_code(p.get_facecolor()))
    return rows.rows, _axis_reader(ax.xaxis), _axis_reader(ax.yaxis)


def _numbers_of_3d(ax, panel, name_of):
    """A 3D chart: lines (Line3D.get_data_3d), dots and surfaces with their height (z) in the value column.
    The 2D positions matplotlib keeps for these are the projection on the screen, so the 3D data are read.

    A surface (Poly3DCollection) keeps its pieces as four or more corners each, in the data's own x, y and z, so
    every grid point is a corner of up to four pieces. Each drawn grid point is given once (kind "surface"), in
    the order of y and then x: the grid matplotlib drew. (matplotlib draws at most 50 x 50 pieces, so a finer
    grid is drawn, and read, at every second or third point.)"""
    rows = _Rows()
    layer = 0
    for line in ax.get_lines():
        if not line.get_visible() or not hasattr(line, "get_data_3d"):
            continue
        layer += 1
        xs, ys, zs = (np.asarray(v, dtype=float) for v in line.get_data_3d())
        colour = colour_code(line.get_color())
        for x, y, z in zip(xs, ys, zs):
            rows.add(panel, layer, "line", name_of(line), x=x, y=y, value=z, colour=colour)
    for coll in ax.collections:
        if not coll.get_visible():
            continue
        dots = getattr(coll, "_offsets3d", None)  # Path3DCollection (ax.scatter on 3D axes)
        faces = getattr(coll, "_faces", None)  # Poly3DCollection (ax.plot_surface)
        if dots is not None:
            layer += 1
            xs, ys, zs = (np.ma.filled(np.ma.asarray(v, dtype=float), np.nan).ravel() for v in dots)
            colours = _colours_3d(coll, len(xs))
            for x, y, z, colour in zip(xs, ys, zs, colours):
                rows.add(panel, layer, "dot", name_of(coll), x=x, y=y, value=z, colour=colour)
        elif faces is not None:
            layer += 1
            corners = np.asarray(faces, dtype=float).reshape(-1, 3)
            corners = corners[np.isfinite(corners).all(axis=1)]
            corners = np.unique(corners, axis=0)  # each drawn grid point once
            corners = corners[np.lexsort((corners[:, 0], corners[:, 1]))]
            for x, y, z in corners:
                rows.add(panel, layer, "surface", name_of(coll), x=x, y=y, value=z)
    return rows.rows


def _colours_3d(coll, n) -> list:
    """The colour of each 3D dot in the order of the data. matplotlib sorts the colours it draws by depth, so they
    are read from what it keeps in the data's order: the numbers coloured through the colour map
    (ScalarMappable.to_rgba of the array), or the colours given (_facecolor3d)."""
    values = coll.get_array()
    if values is not None:
        values = np.ma.asarray(values, dtype=float).ravel()
        if len(values) == n:
            return [colour_code(c) for c in coll.to_rgba(values, alpha=coll.get_alpha())]
        return [""] * n
    return _each_colour(getattr(coll, "_facecolor3d", None), n)


def _all_axes(fig) -> list:
    """The figure's axes, with the axes drawn inside them (the parts of trend_and_season, side histograms, a
    zoom box) and those of its sub-figures (pages of charts)."""
    found = []

    def with_children(ax):
        if any(ax is seen for seen in found):
            return
        found.append(ax)
        for child in getattr(ax, "child_axes", []):
            with_children(child)

    for ax in fig.axes:
        with_children(ax)
    for sub in getattr(fig, "subfigs", []):
        for ax in _all_axes(sub):
            with_children(ax)
    return found


def panels_of(fig) -> list:
    """The chart's panels (sets of axes), without colour bars and hidden axes."""
    return [a for a in _all_axes(fig) if a.get_label() != "<colorbar>" and a.get_visible()]


def main_of(ax, axes) -> tuple:
    """(the panel's own axes, the role) of a set of axes: a second y-axis (chart.add_second_y, twinx), a second
    x-axis (twiny) and a secondary axis belong to the panel they are drawn on; other axes are their own ("")."""
    if type(ax).__name__ == "SecondaryAxis":
        return getattr(ax, "_parent", ax), "second " + getattr(ax, "_orientation", "y")
    twins = getattr(ax, "_twinned_axes", None)
    siblings = twins.get_siblings(ax) if twins is not None else [ax]
    if len(siblings) > 1:
        first = next((a for a in axes if any(a is s for s in siblings)), ax)
        if first is not ax:
            return first, "second y" if ax.get_shared_x_axes().joined(ax, first) else "second x"
    return ax, ""


def numbered_panels(fig) -> list:
    """[(axes, panel number, role, what numbers_of_panel read)] in the order of get_numbers_drawn(). A panel is a
    set of axes on which something was drawn; a second axis (role "second y" ...) has the number of its panel.
    Axes with nothing drawn on them or their second axes (an empty frame, the base of a chart drawn in parts)
    get 0: what is written on them belongs to the whole chart."""
    axes = panels_of(fig)
    read = {id(ax): numbers_of_panel(ax, 0) for ax in axes}
    mains = {id(ax): main_of(ax, axes) for ax in axes}
    with_rows = {id(mains[id(ax)][0]) for ax in axes if read[id(ax)][0]}
    number, numbers = 0, {}
    for ax in axes:
        main = mains[id(ax)][0]
        if id(main) in with_rows and id(main) not in numbers:
            number += 1
            numbers[id(main)] = number
    return [(ax, numbers.get(id(mains[id(ax)][0]), 0), mains[id(ax)][1], read[id(ax)]) for ax in axes]


def numbers_drawn(fig):
    """A pandas table of every number drawn on the figure (COLUMNS), panel by panel. On a date axis x (or y)
    is given as dates, on an axis of named groups as the group names. What is drawn on a second y-axis
    belongs to the panel it is drawn on, its layers after the panel's own."""
    import pandas as pd

    rows = []
    last_layer = {}
    for _ax, panel, _role, (found, (read_x, x_kind), (read_y, y_kind)) in numbered_panels(fig):
        if not found or not panel:
            continue  # an empty frame (the base of a chart drawn in parts) is not a chart
        before = last_layer.get(panel, 0)
        for r in found:
            r["panel"] = panel
            r["layer"] += before
        last_layer[panel] = max([before] + [r["layer"] for r in found])
        for r in found:
            if r["kind"] == "slice":
                continue
            if x_kind != "number":
                r["x"] = read_x(r["x"])
            if y_kind != "number":
                r["y"] = read_y(r["y"])
        rows.extend(found)
    frame = pd.DataFrame(rows, columns=list(COLUMNS))
    for column in ("low", "high", "value"):
        frame[column] = frame[column].astype(float)
    for column in ("colour", "colour name"):
        frame[column] = frame[column].astype(object).fillna("")
    return frame


# what one layer of each kind is called in the printed line
LAYER_WORDS = {"line": ("line", "lines"), "dot": ("group of dots", "groups of dots"),
               "bar": ("set of bars", "sets of bars"), "band": ("band", "bands"),
               "stem": ("set of stems", "sets of stems"), "stem top": ("line of stem tops", "lines of stem tops"),
               "stem base": ("base line", "base lines"), "error bar": ("set of error bars", "sets of error bars"),
               "segment": ("set of line pieces", "sets of line pieces"), "rectangle": ("rectangle", "rectangles"),
               "cell": ("heat map", "heat maps"), "slice": ("pie", "pies"), "shape": ("shape", "shapes"),
               "contour": ("set of contour lines", "sets of contour lines"), "surface": ("surface", "surfaces"),
               "error bar cap": ("set of error bar caps", "sets of error bar caps")}


def summary(frame) -> str:
    """One line on what was read: "Read 230 drawn points in 3 layers: 1 group of dots, 2 lines."."""
    if len(frame) == 0:
        return "The chart has no drawn numbers yet: add a step such as chart.draw_dots(x=..., y=...)."
    layers = frame.drop_duplicates(["panel", "layer"])
    counts = layers["kind"].value_counts(sort=False)
    said = ", ".join(f"{n} {LAYER_WORDS[k][0 if n == 1 else 1]}" for k, n in counts.items())
    panels = frame["panel"].nunique()
    where = f" on {panels} charts" if panels > 1 else ""
    n_layers = len(layers)
    return f"Read {len(frame):,} drawn points in {n_layers} layer{'s' if n_layers != 1 else ''}{where}: {said}."
