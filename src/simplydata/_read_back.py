"""What a chart wrote and what scales it drew: chart.get_text_drawn() and chart.get_scales_drawn().

Charts phase, batch 1 (approved by Manish 2026-11-25). Like chart.get_numbers_drawn() (simplydata._numbers_drawn),
these read the drawn matplotlib figure back and work nothing out again: the titles, axis names, legend entries,
notes and tick words are matplotlib's Text artists; the ranges, scales and ticks are what the Axes keep
(get_xlim, get_xscale, xaxis_inverted, the major tick locations and labels); a colour scale is the colour map and
the limits of the drawn ScalarMappable (cmap.name, norm.vmin, norm.vmax, a TwoSlopeNorm's vcenter). The panels are
numbered as get_numbers_drawn() numbers them (simplydata._numbers_drawn.numbered_panels), so the three tables
can be read side by side.

Where simplydata writes a piece of text itself (a note, a panel letter, a number on a bar, a name next to a dot,
a caption), it marks the Text with what it is (simplydata_part) and, for a note at a fixed place, where it is
(simplydata_where); text that other code wrote on a chart counts as a note.
"""

from __future__ import annotations

import math

import numpy as np

from ._numbers_drawn import _all_axes, _axis_reader, numbered_panels

TEXT_COLUMNS = ("panel", "part", "text", "where")
SCALE_COLUMNS = ("panel", "scale", "name", "low", "high", "kind", "flipped", "ticks", "tick words", "shared with",
                 "colours", "middle")

# matplotlib's legend places (Legend.codes) in simplydata's words
_PLACE_WORDS = {0: "best", 1: "top right", 2: "top left", 3: "bottom left", 4: "bottom right", 5: "right",
                6: "left", 7: "right", 8: "bottom", 9: "top", 10: "middle"}
# a legend outside the panels (put_legend_at_top ...) is on that side of the chart
_OUTSIDE_WORDS = {9: "top", 8: "bottom", 6: "left", 7: "right"}
_SCALE_KINDS = {"linear": "numbers", "log": "log", "symlog": "log through zero", "logit": "logit",
                "asinh": "asinh", "function": "function", "functionlog": "function"}


# ---------------------------------------------------------------- shared
def drawn(fig):
    """Let matplotlib finish the figure (tick words, layout) without making a picture."""
    fig.draw_without_rendering()
    return fig


def _number_text(v) -> str:
    if v is None:
        return ""
    if hasattr(v, "year"):
        return str(v.date()) if hasattr(v, "date") and not (v.hour or v.minute or v.second) else str(v)
    if isinstance(v, str):
        return v
    v = float(v)
    if not math.isfinite(v):
        return ""
    return f"{v:g}"


_SUPERSCRIPTS = str.maketrans("0123456789-+.", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺·")


def plain_text(words: str) -> str:
    """matplotlib's maths text as it is shown: "$\\mathdefault{10^{2}}$" is "10²", "$\\mathdefault{3\\times10^{1}}$"
    is "3×10¹"; other text is kept."""
    import re

    if "$" not in words:
        return words
    text = words.replace("$", "")
    while "\\mathdefault{" in text:
        text = re.sub(r"\\mathdefault\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", r"\1", text)
    text = text.replace("\\times", "×").replace("\\cdot", "·").replace("\\minus", "−").replace("\\,", " ")
    text = re.sub(r"\^\{([^{}]*)\}", lambda m: m.group(1).translate(_SUPERSCRIPTS), text)
    text = re.sub(r"\^(\S)", lambda m: m.group(1).translate(_SUPERSCRIPTS), text)
    return text.replace("{", "").replace("}", "").replace("\\", "")


def _visible_text(artist) -> str:
    if artist is None or not artist.get_visible():
        return ""
    return artist.get_text() or ""


def _figures(fig) -> list:
    """The figure and its sub-figures (the charts of a page), outermost first."""
    found = [fig]
    for sub in getattr(fig, "subfigs", []):
        found.extend(_figures(sub))
    return found


def _first_panel(figure, numbers) -> int:
    """The first panel drawn in a sub-figure (0 for the whole figure)."""
    found = [numbers[id(ax)] for ax in _all_axes(figure) if numbers.get(id(ax))]
    return min(found) if found else 0


# ---------------------------------------------------------------- text
def _legend_rows(rows, legend, panel, where):
    title = _visible_text(legend.get_title())
    if title:
        rows.append((panel, "legend title", title, where))
    for text in legend.get_texts():
        words = _visible_text(text)
        if words and not words.endswith(":"):  # "class:" in front of a one-row legend is its title, moved
            rows.append((panel, "legend entry", words, where))
        elif words:
            rows.append((panel, "legend title", words[:-1], where))


def _where_of(text, ax) -> str:
    where = getattr(text, "simplydata_where", None)
    if where:
        return where
    if ax is None:
        return ""
    xy = getattr(text, "xy", None)
    coords = getattr(text, "xycoords", None) if xy is not None else None
    if xy is None:
        if text.get_transform() is not ax.transData:
            return ""
        xy = text.get_position()
    elif coords != "data":
        return ""
    (read_x, _), (read_y, _) = _axis_reader(ax.xaxis), _axis_reader(ax.yaxis)
    try:
        x, y = ax.xaxis.convert_units(xy[0]), ax.yaxis.convert_units(xy[1])
        return f"{_number_text(read_x(float(x)))}, {_number_text(read_y(float(y)))}"
    except (TypeError, ValueError):
        return ""


def _ticks(axis, ax) -> list:
    """The tick words drawn on an axis, big and small ticks (a log axis writes 30, 40 ... between 10 and 100),
    in order along the axis: inside the shown range, visible and not empty, as plain text."""
    low, high = sorted(axis.get_view_interval())
    room = (high - low) * 1e-9
    words = []
    for locs, labels in ((axis.get_majorticklocs(), axis.get_majorticklabels()),
                         (axis.get_minorticklocs(), axis.get_minorticklabels())):
        for loc, label in zip(locs, labels):
            if low - room <= loc <= high + room and label.get_visible() and label.get_text():
                words.append((loc, plain_text(label.get_text())))
    return sorted(words, key=lambda pair: pair[0])


def text_drawn(fig):
    """A pandas table of every piece of text on the drawn figure: TEXT_COLUMNS."""
    import pandas as pd

    drawn(fig)
    panels = numbered_panels(fig)
    numbers = {id(ax): number for ax, number, _, _ in panels}
    rows = []
    for figure in _figures(fig):
        top = figure is fig
        panel = 0 if top else _first_panel(figure, numbers)
        sup = getattr(figure, "_suptitle", None)
        if _visible_text(sup):
            part = getattr(sup, "simplydata_part", "") or ("page title" if top and figure.subfigs else "title")
            rows.append((panel, part, sup.get_text(), ""))
        for attr, part in (("_supxlabel", "x label"), ("_supylabel", "y label")):
            artist = getattr(figure, attr, None)
            if _visible_text(artist):
                rows.append((panel, getattr(artist, "simplydata_part", "") or part, artist.get_text(), ""))
        for legend in figure.legends:
            _legend_rows(rows, legend, panel, _OUTSIDE_WORDS.get(legend._loc, _PLACE_WORDS.get(legend._loc, "")))
        own = {id(getattr(figure, a, None)) for a in ("_suptitle", "_supxlabel", "_supylabel")}
        for text in list(figure.texts) + [a for a in figure.artists if hasattr(a, "get_text")]:
            if id(text) in own:  # the title and shared axis names, read above
                continue
            if _visible_text(text):
                rows.append((panel, getattr(text, "simplydata_part", "") or "note", text.get_text(),
                             getattr(text, "simplydata_where", "") or ""))
    for ax, panel, role, _ in panels:
        if ax.get_label() == "<colorbar>":
            continue
        for title, part in ((ax.title, "title"), (ax._left_title, "panel letter"), (ax._right_title, "title")):
            if _visible_text(title):
                rows.append((panel, getattr(title, "simplydata_part", "") or part, title.get_text(), ""))
        x_part = "second x" if role == "second x" else "x"
        y_part = "second y" if role == "second y" else "y"
        if role in ("", "second x") and _visible_text(ax.xaxis.label):
            rows.append((panel, f"{x_part} label", ax.xaxis.label.get_text(), ""))
        if role in ("", "second y") and _visible_text(ax.yaxis.label):
            rows.append((panel, f"{y_part} label", ax.yaxis.label.get_text(), ""))
        if getattr(ax, "name", "") == "3d" and ax.get_zlabel():
            rows.append((panel, "z label", ax.get_zlabel(), ""))
        legend = ax.get_legend()
        if legend is not None and legend.get_visible():
            _legend_rows(rows, legend, panel, "inside " + _PLACE_WORDS.get(legend._loc, "best"))
        for text in ax.texts:
            if _visible_text(text):
                rows.append((panel, getattr(text, "simplydata_part", "") or "note", text.get_text(),
                             _where_of(text, ax)))
        if role in ("", "second x"):
            for _, words in _ticks(ax.xaxis, ax):
                rows.append((panel, "tick " + x_part, words, ""))
        if role in ("", "second y"):
            for _, words in _ticks(ax.yaxis, ax):
                rows.append((panel, "tick " + y_part, words, ""))
    for cax in _colour_bar_axes(fig):
        bar = cax._colorbar
        label = cax.get_ylabel() if bar.orientation == "vertical" else cax.get_xlabel()
        if label:
            rows.append((_colour_bar_panel(bar, numbers), "colour bar label", label, ""))
    frame = pd.DataFrame(rows, columns=list(TEXT_COLUMNS))
    frame["panel"] = frame["panel"].astype(int)
    return frame


def _plural(n, one, many=None) -> str:
    return f"{n} {one if n == 1 else (many or one + 's')}"


def text_summary(frame) -> str:
    """One line: "Read 23 pieces of text on 1 chart: title, 2 axis names, legend with 3 entries, 17 tick words."."""
    if len(frame) == 0:
        return "The chart has no text yet: add a step such as chart.write_title_on_top(\"...\")."
    parts = frame["part"]
    said = []
    titles = int(parts.isin(["title", "page title"]).sum())
    if titles:
        said.append("title" if titles == 1 else f"{titles} titles")
    names = int(parts.str.endswith(" label").sum() - (parts == "colour bar label").sum())
    if names:
        said.append(_plural(names, "axis name"))
    entries = int((parts == "legend entry").sum())
    legends = len(frame[parts.isin(["legend entry", "legend title"])][["panel", "where"]].drop_duplicates())
    if entries:
        said.append(f"legend with {_plural(entries, 'entry', 'entries')}" if legends == 1
                    else f"{legends} legends with {_plural(entries, 'entry', 'entries')}")
    for part, one, many in (("colour bar label", "colour bar name", None), ("note", "note", None),
                            ("caption", "caption", None), ("panel letter", "panel letter", None),
                            ("number on bar", "number on bars", "numbers on bars"),
                            ("name on dot", "name next to dots", "names next to dots")):
        n = int((parts == part).sum())
        if n:
            said.append(_plural(n, one, many))
    ticks = int(parts.str.startswith("tick ").sum())
    if ticks:
        said.append(_plural(ticks, "tick word"))
    charts = frame.loc[frame["panel"] > 0, "panel"].nunique()
    where = _plural(max(charts, 1), "chart")
    return f"Read {_plural(len(frame), 'piece of text', 'pieces of text')} on {where}: {', '.join(said)}."


# ---------------------------------------------------------------- scales
def _colour_bar_axes(fig) -> list:
    return [a for a in _all_axes(fig) if a.get_label() == "<colorbar>" and hasattr(a, "_colorbar")
            and a.get_visible()]


def _colour_bar_panel(bar, numbers) -> int:
    ax = getattr(bar.mappable, "axes", None)
    if ax is not None and numbers.get(id(ax)):
        return numbers[id(ax)]
    for parent in (getattr(bar.ax, "_colorbar_info", None) or {}).get("parents", []):
        if numbers.get(id(parent)):
            return numbers[id(parent)]
    return 0


def _axis_row(panel, scale, ax, axis, name, which):
    read, kind = _axis_reader(axis)
    limits = axis.get_view_interval()
    flipped = bool(limits[0] > limits[1])
    if which == "x":
        flipped = bool(ax.xaxis_inverted())
    elif which == "y":
        flipped = bool(ax.yaxis_inverted())
    elif which == "z":
        flipped = bool(ax.zaxis_inverted())
    low, high = sorted(float(v) for v in limits)
    shown = {"date": "dates", "group": "groups"}.get(kind) or _SCALE_KINDS.get(axis.get_scale(), axis.get_scale())
    if axis.get_scale() == "function" and getattr(axis, "simplydata_scale", None):
        shown = axis.simplydata_scale  # use_scale_y("square root"): matplotlib calls it a "function" scale
    ticks = _ticks(axis, ax)
    if kind == "number":
        low_v, high_v = low, high
    else:
        low_v, high_v = read(low), read(high)
    if kind == "number" and _named_ticks(axis, ticks):  # a heat map: rows and columns of named groups
        shown = "groups"
        return dict(panel=panel, scale=scale, name=name, low=low_v, high=high_v, kind=shown, flipped=flipped,
                    ticks=", ".join(words for _, words in ticks),
                    **{"tick words": ", ".join(words for _, words in ticks), "shared with": "", "colours": "",
                       "middle": math.nan})
    return dict(panel=panel, scale=scale, name=name, low=low_v, high=high_v, kind=shown, flipped=flipped,
                ticks=", ".join(_number_text(read(float(loc))) for loc, _ in ticks),
                **{"tick words": ", ".join(words for _, words in ticks), "shared with": "", "colours": "",
                   "middle": math.nan})


def _named_ticks(axis, ticks) -> bool:
    """Whether the axis is numbered but writes names in the middle of each cell (seaborn's heat maps: names at
    0.5, 1.5 ...): its ticks are groups."""
    from matplotlib.ticker import FixedLocator

    if not ticks or not isinstance(axis.get_major_locator(), FixedLocator) or axis.get_scale() != "linear":
        return False
    if any(abs(loc - round(loc - 0.5) - 0.5) > 1e-9 for loc, _ in ticks):
        return False
    for _, words in ticks:
        try:
            float(words.replace("−", "-"))
        except ValueError:
            return True
    return False


def _norm_kind(norm) -> tuple[str, float]:
    from matplotlib import colors as mcolors

    middle = float(getattr(norm, "simplydata_middle", math.nan))  # use_colour_scale(middle=): what was asked
    if math.isnan(middle) and isinstance(norm, (mcolors.TwoSlopeNorm, mcolors.CenteredNorm)):
        middle = float(norm.vcenter)
    if isinstance(norm, mcolors.BoundaryNorm):
        return "steps", middle
    if isinstance(norm, mcolors.SymLogNorm):
        return "log through zero", middle
    if isinstance(norm, mcolors.LogNorm):
        return "log", middle
    return "numbers", middle


def _colour_row(panel, mappable, name, bar=None):
    norm = mappable.norm
    kind, middle = _norm_kind(norm)
    low, high = norm.vmin, norm.vmax
    if bar is not None:
        axis = bar.long_axis
        ticks = _ticks(axis, bar.ax)
        locs, words = [_number_text(loc) for loc, _ in ticks], [w for _, w in ticks]
    else:
        locs, words = [], []
    return dict(panel=panel, scale="colour", name=name, low=math.nan if low is None else float(low),
                high=math.nan if high is None else float(high), kind=kind, flipped=False, ticks=", ".join(locs),
                **{"tick words": ", ".join(words), "shared with": "", "colours": mappable.get_cmap().name,
                   "middle": middle})


def _mappables(ax) -> list:
    """The drawn things on a panel coloured through a colour map (heat maps, contour maps, dots by a number)."""
    found = []
    for artist in list(ax.collections) + list(ax.get_images()):
        if artist.get_visible() and getattr(artist, "get_array", None) is not None and artist.get_array() is not None:
            found.append(artist)
    return found


def scales_drawn(fig):
    """A pandas table of every scale on the drawn figure: SCALE_COLUMNS."""
    import pandas as pd

    drawn(fig)
    panels = numbered_panels(fig)
    numbers = {id(ax): number for ax, number, _, _ in panels}
    figure_names = {}
    for figure in _figures(fig):
        for ax in _all_axes(figure):
            figure_names.setdefault(id(ax), (_visible_text(getattr(figure, "_supxlabel", None)),
                                             _visible_text(getattr(figure, "_supylabel", None))))
    rows = []
    for ax, panel, role, _ in panels:
        if ax.get_label() == "<colorbar>" or (not panel and not role):
            continue
        shared_x, shared_y = figure_names.get(id(ax), ("", ""))
        if role:
            axis = ax.xaxis if role == "second x" else ax.yaxis
            rows.append(_axis_row(panel, role, ax, axis, axis.label.get_text(), role[-1]))
            continue
        rows.append(_axis_row(panel, "x", ax, ax.xaxis, ax.get_xlabel() or shared_x, "x"))
        rows.append(_axis_row(panel, "y", ax, ax.yaxis, ax.get_ylabel() or shared_y, "y"))
        if getattr(ax, "name", "") == "3d":
            rows.append(_axis_row(panel, "z", ax, ax.zaxis, ax.get_zlabel(), "z"))
    with_bar = set()
    for cax in _colour_bar_axes(fig):
        bar = cax._colorbar
        label = cax.get_ylabel() if bar.orientation == "vertical" else cax.get_xlabel()
        panel = _colour_bar_panel(bar, numbers)
        rows.append(_colour_row(panel, bar.mappable, label, bar))
        with_bar.add(panel)
    seen = []
    for ax, panel, _, _ in panels:  # a colour scale without a colour bar (its colour bar was hidden)
        if not panel or panel in with_bar:
            continue
        for artist in _mappables(ax):
            key = (id(artist.norm), id(artist.get_cmap()))
            if key not in seen:
                seen.append(key)
                rows.append(_colour_row(panel, artist, ""))
    frame = pd.DataFrame(rows, columns=list(SCALE_COLUMNS))
    for i, row in frame.iterrows():  # the other panels with the same scale over the same range
        same = frame[(frame["scale"] == row["scale"]) & (frame["panel"] != row["panel"])]
        same = same.loc[[_same_value(a, row["low"]) and _same_value(b, row["high"])
                         for a, b in zip(same["low"], same["high"])]]
        frame.at[i, "shared with"] = ", ".join(str(p) for p in sorted(set(same["panel"])))
    frame["panel"] = frame["panel"].astype(int)
    frame["flipped"] = frame["flipped"].astype(bool)
    frame["middle"] = frame["middle"].astype(float)
    return frame


def _same_value(a, b) -> bool:
    if isinstance(a, float) and isinstance(b, float):
        return a == b or (np.isnan(a) and np.isnan(b))
    return a == b


def scales_summary(frame) -> str:
    """One line: "Read 2 scales on 1 chart: x 0 to 12.5 (numbers), y 30 to 100 (numbers)."."""
    if len(frame) == 0:
        return "The chart has no scales yet: add a step such as chart.draw_dots(x=..., y=...)."
    charts = max(frame["panel"].nunique(), 1)
    several = charts > 1
    said = []
    for _, row in frame.iterrows():
        what = f"{row['scale']} {_number_text(row['low'])} to {_number_text(row['high'])} ({row['kind']}"
        what += ", flipped)" if row["flipped"] else ")"
        said.append(f"chart {row['panel']} {what}" if several else what)
    if len(said) > 6:
        said = said[:4] + [f"and {len(said) - 4} more"]
    return (f"Read {_plural(len(frame), 'scale')} on {_plural(charts, 'chart')}: " + ", ".join(said) + ".")
