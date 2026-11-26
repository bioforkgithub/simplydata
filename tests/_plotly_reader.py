"""Reading a web page back: the plotly figure of chart.save("x.html") as the three tables of get_numbers_drawn(),
get_text_drawn() and get_scales_drawn() (charts phase, batch 3).

The tests compare these tables with the ones read from the matplotlib picture, so this reader reads plotly's own
data wherever plotly has a field for it:
  * the numbers: the x, y, base, z, values and customdata arrays of each mark, its line, fill and marker colours,
    the heights of contour lines from their hover text, and layout shapes;
  * the panels: from the subplots' domains (the place of each set of axes on the page): marks whose axes sit in
    the same place are on one panel, numbered in the order of the subplots (a second axis overlays its panel);
  * the scales: each axis's range, type ("log", "date"), tick values and tick words; a scale of groups is an axis
    whose tick words are names; a shared axis's name is the name of the axis it matches;
  * the words: the title, the annotations, the axis titles, the legend entries (marks shown in a legend) and
    the colour bars' titles.
Only labels plotly has no field for are read from the figure's meta: which layer of the chart a mark is and the
kind of row it shows (plotly's mark type and mode are checked to agree with it), which panel a legend belongs to,
what a piece of text is (a title, a panel letter, a note), and the name and kind of a colour scale.
"""

from __future__ import annotations

import math
import re

import numpy as np
import pandas as pd

from simplydata._web import colour_code_of

NUMBER_COLUMNS = ("panel", "layer", "kind", "series", "x", "y", "low", "high", "value", "colour")
# the plotly mark that draws each kind of row: what the meta says must agree with plotly's own type and mode
_POINTS = {"scatter:markers", "scatter:lines+markers", "scatter:lines"}
FAMILIES = {"line": {"scatter:lines", "scatter:lines+markers", "scatter:markers", "scatterpolar:lines",
                     "scatter3d:lines"},
            "dot": {"scatter:markers", "scatter:lines+markers", "scatterpolar:markers", "scatter3d:markers"},
            "bar": {"bar:", "barpolar:", "mesh3d:"}, "band": {"scatter:lines"},
            "shape": {"scatter:lines", "scatterpolar:lines"}, "contour": {"scatter:lines"},
            "hexagon": {"scatter:lines"}, "cell": {"heatmap:"}, "slice": {"pie:"}, "surface": {"surface:"},
            "stem": _POINTS, "error bar": _POINTS, "segment": _POINTS, "stem base": _POINTS,
            "error bar cap": _POINTS, "stem top": _POINTS}


def _gaps(values):
    """Split a list at its gaps (None): plotly draws each part apart."""
    parts, part = [], []
    for v in values:
        if v is None:
            parts.append(part)
            part = []
        else:
            part.append(v)
    parts.append(part)
    return [p for p in parts if p]


def _num(v):
    if v is None:
        return math.nan
    if isinstance(v, str):
        try:
            return pd.Timestamp(v)
        except ValueError:
            return v
    if hasattr(v, "year"):
        return pd.Timestamp(v)
    return float(v)


def _is_number_text(text) -> bool:
    text = str(text).replace("−", "-").replace(",", "").rstrip("%").strip()
    try:
        float(text)
        return True
    except ValueError:
        return bool(re.fullmatch(r"[-0-9.]*(×)?10\S*", text))  # 10², 3×10¹ on a log axis


def _axis_layout(fig, name):
    """The layout of axis "x2" (xaxis2)."""
    return fig.layout[{"x": "xaxis", "y": "yaxis"}[name[0]] + name[1:]]


def _drawn_as_groups(fig, name) -> bool:
    """Whether an axis holds groups (names at 0, 1, 2 ...). plotly has no field for it: the web page draws groups
    on a number axis with the names as tick words, as matplotlib does, so the figure's meta says which axes they
    are."""
    meta = (fig.layout.meta or {}).get("simplydata", {}).get("axes", {})
    return meta.get(name, {}).get("kind") == "group"


def _named_cells(axis) -> bool:
    """A heat map's axis: names written in the middle of each cell (at 0.5, 1.5 ...)."""
    values = [float(v) for v in axis.tickvals or ()]
    return bool(values) and all(abs(v - math.floor(v) - 0.5) < 1e-9 for v in values) and any(
        not _is_number_text(t) for t in axis.ticktext or ())


def _group_reader(axis):
    """The names of a groups axis at their places (plotly holds the places as numbers and the names as tick
    words)."""
    names = dict(zip([float(v) for v in axis.tickvals or ()], axis.ticktext or ()))

    def read(v):
        if isinstance(v, float) and not math.isnan(v) and abs(v - round(v)) < 1e-9 and float(round(v)) in names:
            return names[float(round(v))]
        return v
    return read


def _has_data(trace) -> bool:
    for name in ("x", "y", "z", "values", "theta"):
        values = getattr(trace, name, None)
        if values is not None and any(v is not None for v in np.ravel(np.asarray(values, dtype=object))):
            return True
    return False


def _domain(fig, x_name, y_name):
    x_axis = _axis_layout(fig, x_name)
    y_axis = _axis_layout(fig, y_name)
    x_axis = _axis_layout(fig, x_axis.overlaying) if x_axis.overlaying else x_axis
    y_axis = _axis_layout(fig, y_axis.overlaying) if y_axis.overlaying else y_axis
    return tuple(np.round(x_axis.domain, 6)), tuple(np.round(y_axis.domain, 6))


def _number_of(name) -> int:
    return int(re.sub(r"\D", "", name) or 1)


def _place_of(fig, trace):
    """(order, domain) of the subplot a mark is drawn on: its axes, round chart, 3D scene or pie place."""
    t = trace.type
    if t == "pie":
        d = trace.domain
        return 10 ** 6, (tuple(np.round(d.x, 6)), tuple(np.round(d.y, 6)))
    if t in ("scatterpolar", "barpolar"):
        name = trace.subplot or "polar"
    elif t in ("scatter3d", "surface", "mesh3d"):
        name = trace.scene or "scene"
    else:
        x_name = trace.xaxis or "x"
        return _number_of(x_name), _domain(fig, x_name, trace.yaxis or "y")
    d = fig.layout[name].domain
    return _number_of(name), (tuple(np.round(d.x, 6)), tuple(np.round(d.y, 6)))


def panels_from_domains(fig) -> dict:
    """{domain: panel number}: the places on the page that hold marks, numbered in the order of the subplots."""
    places = {}
    for trace in fig.data:
        if _has_data(trace):
            order, domain = _place_of(fig, trace)
            places[domain] = min(places.get(domain, order), order)
    for shape in fig.layout.shapes or ():
        x_name, y_name = str(shape.xref).replace(" domain", ""), str(shape.yref).replace(" domain", "")
        if x_name.startswith("x"):
            domain = _domain(fig, x_name, y_name)
            places[domain] = min(places.get(domain, _number_of(x_name)), _number_of(x_name))
    ordered = sorted(places, key=lambda d: places[d])
    return {d: i for i, d in enumerate(ordered, start=1)}


def _meta(trace):
    return trace.meta if isinstance(trace.meta, dict) else {}


def _colour_of(trace, i=None):
    """A mark's colour from plotly's own fields: the fill, the marker's colour (one each, or one for all) or the
    line."""
    mode = getattr(trace, "mode", None) or ""
    if trace.type == "scatter" and trace.fill:
        return colour_code_of(trace.fillcolor)
    if trace.type in ("scatter", "scatterpolar", "scatter3d") and "lines" in mode:
        colour = trace.line.color
    else:
        colour = trace.marker.color
    if isinstance(colour, (list, tuple)):
        colour = colour[i] if i is not None and i < len(colour) else colour[0]
    return colour_code_of(colour)


def numbers_from_web(fig) -> pd.DataFrame:
    panels = panels_from_domains(fig)
    rows = []
    now = {"x": None, "y": None, "panel": 0, "meta": {}}

    def same(v):
        return v

    def add(x=math.nan, y=math.nan, low=math.nan, high=math.nan, value=math.nan, colour=""):
        meta = now["meta"]
        # on an axis of groups, x and y are the group names (as get_numbers_drawn() gives them)
        rows.append(dict(panel=now["panel"], layer=meta["layer"], kind=meta["kind"], series=meta.get("series", ""),
                         x=now["x"](x), y=now["y"](y), low=low, high=high, value=value, colour=colour))

    for trace in fig.data:
        meta = _meta(trace)
        kind = meta.get("kind")
        if kind is None or "layer" not in meta or not _has_data(trace):
            continue
        t = trace.type
        family = f"{t}:{trace.mode or ''}" if t in ("scatter", "scatterpolar", "scatter3d") else f"{t}:"
        assert family in FAMILIES.get(kind, ()), f"a {kind} drawn as {family}"
        now["meta"], now["panel"] = meta, panels[_place_of(fig, trace)[1]]
        now["x"] = now["y"] = same
        if t in ("scatter", "bar", "heatmap"):
            x_axis, y_axis = _axis_layout(fig, trace.xaxis or "x"), _axis_layout(fig, trace.yaxis or "y")
            now["x"] = _group_reader(x_axis) if _drawn_as_groups(fig, trace.xaxis or "x") else same
            now["y"] = _group_reader(y_axis) if _drawn_as_groups(fig, trace.yaxis or "y") else same
        if t == "scatter":
            xs, ys = list(trace.x), list(trace.y)
            if kind in ("line", "dot", "stem base", "stem top", "error bar cap"):
                for i, (x, y) in enumerate(zip(xs, ys)):
                    add(x=_num(x), y=_num(y), colour=_colour_of(trace, i))
            elif kind == "band":
                sideways = trace.orientation == "h"
                for part_x, part_y in zip(_gaps(xs), _gaps(ys)):
                    n = len(part_x) // 2
                    for i in range(n):
                        if sideways:
                            a, b = _num(part_x[i]), _num(part_x[2 * n - 1 - i])
                            add(y=_num(part_y[i]), low=min(a, b), high=max(a, b), colour=_colour_of(trace))
                        else:
                            a, b = _num(part_y[i]), _num(part_y[2 * n - 1 - i])
                            add(x=_num(part_x[i]), low=min(a, b), high=max(a, b), colour=_colour_of(trace))
            elif kind in ("stem", "error bar", "segment"):
                for part_x, part_y in zip(_gaps(xs), _gaps(ys)):
                    (x0, y0), (x1, y1) = (_num(part_x[0]), _num(part_y[0])), (_num(part_x[-1]), _num(part_y[-1]))
                    colour = _colour_of(trace)
                    if len(part_x) == 2 and x0 == x1:
                        add(x=x0, y=y1, low=min(y0, y1), high=max(y0, y1), colour=colour)
                    elif len(part_x) == 2 and y0 == y1:
                        add(x=x1, y=y0, low=min(x0, x1), high=max(x0, x1), colour=colour)
                    else:
                        for x, y in zip(part_x, part_y):
                            add(x=_num(x), y=_num(y), colour=colour)
            elif kind in ("shape", "contour"):
                level = math.nan
                if kind == "contour":  # the height of a contour line is its hover text
                    level = float(next(text for text in trace.text if text))
                colour = colour_code_of(trace.fillcolor) if trace.fill else colour_code_of(trace.line.color)
                for x, y in zip(xs, ys):
                    if x is not None:
                        add(x=_num(x), y=_num(y), value=level, colour=colour)
            elif kind == "hexagon":
                seen = set()
                for data in trace.customdata:
                    if data[0] is None or data[3] in seen:
                        continue
                    seen.add(data[3])
                    add(x=float(data[0]), y=float(data[1]), value=float(data[2]), colour=_colour_of(trace))
        elif t == "bar":
            upright = trace.orientation != "h"
            places = list(trace.x if upright else trace.y)
            lengths = list(trace.y if upright else trace.x)
            for i, (place, length, base) in enumerate(zip(places, lengths, trace.base)):
                base, length = _num(base), float(length)
                if isinstance(base, pd.Timestamp):  # bars on a date axis: lengths in milliseconds
                    end = base + pd.Timedelta(milliseconds=length)
                    low, high = min(base, end), max(base, end)
                else:
                    low, high = min(base, base + length), max(base, base + length)
                if upright:
                    add(x=_num(place), y=length, low=low, high=high, colour=_colour_of(trace, i))
                else:
                    add(x=length, y=_num(place), low=low, high=high, colour=_colour_of(trace, i))
        elif t == "heatmap":
            for y, row in zip(trace.y, trace.z):
                for x, v in zip(trace.x, row):
                    add(x=_num(x), y=_num(y), value=math.nan if v is None else float(v))
        elif t == "pie":
            at = 90 - (trace.rotation or 0)
            sign = 1 if trace.direction == "counterclockwise" else -1
            for v, colour in zip(trace.values, trace.marker.colors):
                end = at + sign * 360 * float(v)
                add(low=min(at, end), high=max(at, end), value=float(v), colour=colour_code_of(colour))
                at = end
        elif t == "scatterpolar":
            for i, (theta, r) in enumerate(zip(trace.theta, trace.r)):
                add(x=math.radians(theta), y=float(r), colour=_colour_of(trace, i))
        elif t == "barpolar":
            for i, (theta, r, base) in enumerate(zip(trace.theta, trace.r, trace.base)):
                add(x=math.radians(theta), y=float(r), low=min(base, base + r), high=max(base, base + r),
                    colour=_colour_of(trace, i))
        elif t == "scatter3d":
            for i, (x, y, z) in enumerate(zip(trace.x, trace.y, trace.z)):
                add(x=float(x), y=float(y), value=float(z), colour=_colour_of(trace, i))
        elif t == "surface":
            for y, row in zip(trace.y, trace.z):
                for x, z in zip(trace.x, row):
                    if z is not None:
                        add(x=float(x), y=float(y), value=float(z))
        elif t == "mesh3d":
            points = np.column_stack([trace.x, trace.y, trace.z]).reshape(-1, 8, 3)
            faces = list(trace.facecolor or ())
            for i, box in enumerate(points):
                (x0, y0, z0), (x1, y1, z1) = box.min(axis=0), box.max(axis=0)
                colour = colour_code_of(faces[12 * i]) if len(faces) > 12 * i else ""  # 12 triangles per bar
                add(x=(x0 + x1) / 2, y=(y0 + y1) / 2, low=z0, high=z1, value=z1 - z0, colour=colour)
    for shape in fig.layout.shapes or ():
        kind, _, layer, series = (shape.name or "|||").split("|", 3)  # plotly has no "kind" or "layer" field
        if not kind:
            continue
        x_name, y_name = str(shape.xref).replace(" domain", ""), str(shape.yref).replace(" domain", "")
        now["meta"] = dict(layer=int(layer), kind=kind, series=series)
        now["panel"], now["x"], now["y"] = panels[_domain(fig, x_name, y_name)], same, same
        x_data = not str(shape.xref).endswith("domain")
        y_data = not str(shape.yref).endswith("domain")
        if kind == "rectangle":
            y0, y1 = _num(shape.y0), _num(shape.y1)
            add(x=(_num(shape.x0) + _num(shape.x1)) / 2 if x_data else math.nan,
                y=(y1 - y0) if y_data else math.nan, low=min(y0, y1) if y_data else math.nan,
                high=max(y0, y1) if y_data else math.nan, colour=colour_code_of(shape.fillcolor))
        else:
            for x, y in ((shape.x0, shape.y0), (shape.x1, shape.y1)):
                add(x=_num(x) if x_data else math.nan, y=_num(y) if y_data else math.nan,
                    colour=colour_code_of(shape.line.color))
    return pd.DataFrame(rows, columns=list(NUMBER_COLUMNS))


def _visible_title(axis) -> str:
    title = axis.title
    if not title.text:
        return ""
    colour = title.font.color if title.font else None
    if isinstance(colour, str) and colour.replace(" ", "").endswith(",0)"):
        return ""  # a name kept on the axis but not shown
    return title.text


def _axis_name(fig, name) -> str:
    """An axis's name: its title, or the title of the axis it matches (the inner panels of a shared chart)."""
    return _axis_layout(fig, name).title.text or ""


def _cartesian_axes(fig):
    """[(axis name "x2", panel, second)] for every axis in the layout that holds marks or overlays an axis that
    does (second: it overlays its panel's axis, a second scale)."""
    panels = panels_from_domains(fig)
    used = {}
    for trace in fig.data:
        if trace.type in ("scatter", "bar", "heatmap") and _has_data(trace):
            for name in (trace.xaxis or "x", trace.yaxis or "y"):
                used.setdefault(name, panels[_place_of(fig, trace)[1]])
    for shape in fig.layout.shapes or ():
        x_name, y_name = str(shape.xref).replace(" domain", ""), str(shape.yref).replace(" domain", "")
        for name in (x_name, y_name):
            used.setdefault(name, panels[_domain(fig, x_name, y_name)])
    found = []
    for key in fig.layout.to_plotly_json():
        if not re.fullmatch(r"[xy]axis\d*", key):
            continue
        name = key[0] + key[5:]
        axis = fig.layout[key]
        if name in used:
            found.append((name, used[name], bool(axis.overlaying)))
        elif axis.overlaying in used:
            found.append((name, used[axis.overlaying], True))
        elif not axis.overlaying:
            other = _axis_layout(fig, axis.anchor) if axis.anchor and axis.anchor != "free" else None
            domain = (tuple(np.round(axis.domain, 6)), tuple(np.round(other.domain, 6))) if name[0] == "x" and other                 else (tuple(np.round(other.domain, 6)), tuple(np.round(axis.domain, 6))) if other else None
            if domain in panels:  # the axes of a pie: the pie sits in the same place
                found.append((name, panels[domain], False))
            elif axis.visible is not False:
                found.append((name, 0, False))  # an empty frame (the base of a chart drawn in parts)
    return found


def text_from_web(fig) -> pd.DataFrame:
    """(panel, part, text) of every piece of text on the web page."""
    meta = (fig.layout.meta or {}).get("simplydata", {})
    legends = meta.get("legends", {})  # plotly's legends belong to no panel
    rows = []
    title = meta.get("title")
    if title and fig.layout.title.text:
        rows.append((title["panel"], title["part"], fig.layout.title.text))
    for note in fig.layout.annotations or ():
        part, panel = (note.name or "note|0").split("|")  # plotly has no field for what a note is
        if note.text:
            rows.append((int(panel), part, _plain(note.text)))
    panels = panels_from_domains(fig)
    for name, panel, second in _cartesian_axes(fig):
        letter = name[0]
        axis = _axis_layout(fig, name)
        prefix = f"second {letter}" if second else letter
        if _visible_title(axis):
            rows.append((panel, f"{prefix} label", axis.title.text))
        rows += [(panel, f"tick {prefix}", w) for w in axis.ticktext or ()]
    for key in fig.layout.to_plotly_json():
        if re.fullmatch(r"(polar|scene)\d*", key):
            layout = fig.layout[key]
            domain = (tuple(np.round(layout.domain.x, 6)), tuple(np.round(layout.domain.y, 6)))
            if domain not in panels:
                continue
            panel = panels[domain]
            if key.startswith("scene"):
                for letter in ("x", "y", "z"):
                    axis = layout[f"{letter}axis"]
                    if axis.title.text:
                        rows.append((panel, f"{letter} label", axis.title.text))
                for letter in ("x", "y"):
                    rows += [(panel, f"tick {letter}", w) for w in layout[f"{letter}axis"].ticktext or ()]
            else:
                rows += [(panel, "tick x", w) for w in layout.angularaxis.ticktext or ()]
                rows += [(panel, "tick y", w) for w in layout.radialaxis.ticktext or ()]
    for trace in fig.data:
        if trace.showlegend and trace.name and trace.type != "pie":
            rows.append((legends.get(trace.legend or "legend", 0), "legend entry", trace.name))
        if trace.type == "pie" and trace.showlegend:
            rows += [(legends.get(trace.legend or "legend", 0), "legend entry", label) for label in trace.labels]
        bar = getattr(getattr(trace, "marker", None), "colorbar", None)
        if bar is not None and getattr(trace.marker, "showscale", False) and bar.title.text:
            rows.append((_colour_panel(fig, trace, panels), "colour bar label", bar.title.text))
    for key, panel in legends.items():
        title = fig.layout[key].title.text
        if title:
            rows.append((panel, "legend title", title))
    return pd.DataFrame(rows, columns=["panel", "part", "text"])


def _colour_panel(fig, trace, panels):
    """The panel of a colour scale: the panel whose axes its mark is placed on (the colour bar sits beside it)."""
    if trace.type == "scatter" and trace.xaxis is not None:
        place = _place_of(fig, trace)[1]
        if place in panels:
            return panels[place]
    return _meta(trace).get("panel", 0)  # a scale of a 3D or round chart: plotly gives it no axes


def _plain(text):
    import html

    return html.unescape(text.replace("<br>", "\n"))


def scales_from_web(fig) -> pd.DataFrame:
    """(panel, scale, name, low, high, kind, flipped, tick words) of each flat axis and colour scale."""
    rows = []
    panels = panels_from_domains(fig)
    for name, panel, second in _cartesian_axes(fig):
        letter = name[0]
        axis = _axis_layout(fig, name)
        low, high = axis.range
        if axis.type == "log":
            low, high = 10 ** low, 10 ** high
        if not panel and not second:
            continue  # an empty frame has no scales of its own
        kind = "dates" if axis.type == "date" else "log" if axis.type == "log" else \
            "groups" if _drawn_as_groups(fig, name) or _named_cells(axis) else "numbers"
        flipped = _num(low) > _num(high)
        low, high = (_num(high), _num(low)) if flipped else (_num(low), _num(high))
        if second and axis.range == _axis_layout(fig, axis.overlaying).range and not _uses(fig, name):
            # a second scale in other units (add_second_x(formula=)) is drawn on its panel's numbers: its own
            # range is not on the page, only its tick words at their places
            low = high = math.nan
        rows.append(dict(panel=panel, scale=f"second {letter}" if second else letter, name=_axis_name(fig, name),
                         low=low, high=high, kind=kind, flipped=bool(flipped),
                         **{"tick words": ", ".join(axis.ticktext or ())}))
    for trace in fig.data:
        marker = getattr(trace, "marker", None)
        if trace.type != "scatter" or marker is None or marker.cmin is None or _has_data(trace):
            continue  # a colour scale: a mark that draws nothing but its colour bar
        bar = marker.colorbar if marker.showscale else None
        rows.append(dict(panel=_colour_panel(fig, trace, panels), scale="colour",
                         name=(bar.title.text or "") if bar else "", low=float(marker.cmin), high=float(marker.cmax),
                         kind=_meta(trace).get("scale kind", ""), flipped=False,
                         **{"tick words": ", ".join(bar.ticktext or ()) if bar else ""},
                         colours=_meta(trace).get("colours", "")))  # plotly keeps the colours, not their name
    return pd.DataFrame(rows, columns=["panel", "scale", "name", "low", "high", "kind", "flipped", "tick words",
                                       "colours"])


def _uses(fig, name) -> bool:
    return any((t.xaxis or "x") == name or (t.yaxis or "y") == name for t in fig.data
               if t.type in ("scatter", "bar", "heatmap") and _has_data(t))
