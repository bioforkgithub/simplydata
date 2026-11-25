"""Reading a web page back: the plotly figure of chart.save("x.html") as the three tables of get_numbers_drawn(),
get_text_drawn() and get_scales_drawn() (charts phase, batch 3).

The tests compare these tables with the ones read from the matplotlib picture. Everything is read from the plotly
figure's own data: the x, y, base, z and values arrays of each mark, the axis ranges, types, tick values and tick
words, the titles, notes, legend entries and colour bars. Which panel, layer and kind of row a mark shows is kept
in the mark's meta (plotly has no panels and no "kinds"), so the rows can be put side by side.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from simplydata._web import colour_code_of

NUMBER_COLUMNS = ("panel", "layer", "kind", "series", "x", "y", "low", "high", "value", "colour")


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


def _axes_meta(fig):
    return (fig.layout.meta or {}).get("simplydata", {}).get("axes", {})


def _group_reader(fig, axis_name):
    """The names of a groups axis at their places (plotly holds the places as numbers and the names as tick
    words)."""
    layout_name = {"x": "xaxis", "y": "yaxis"}[axis_name[0]] + axis_name[1:]
    axis = fig.layout[layout_name]
    names = dict(zip([float(v) for v in axis.tickvals or ()], axis.ticktext or ()))

    def read(v):
        if isinstance(v, float) and not math.isnan(v) and abs(v - round(v)) < 1e-9 and float(round(v)) in names:
            return names[float(round(v))]
        return v
    return read


def numbers_from_web(fig) -> pd.DataFrame:
    meta_axes = _axes_meta(fig)
    rows = []

    current = {"x": lambda v: v, "y": lambda v: v}

    def add(meta, x=math.nan, y=math.nan, low=math.nan, high=math.nan, value=math.nan, colour=""):
        # on an axis of groups, x and y are the group names (as get_numbers_drawn() gives them)
        rows.append(dict(panel=meta["panel"], layer=meta["layer"], kind=meta["kind"], series=meta.get("series", ""),
                         x=current["x"](x), y=current["y"](y), low=low, high=high, value=value, colour=colour))

    def readers(trace):
        out = []
        for letter in ("x", "y"):
            name = getattr(trace, f"{letter}axis", None) or letter
            if meta_axes.get(name, {}).get("kind") == "group":
                out.append(_group_reader(fig, name))
            else:
                out.append(lambda v: v)
        return out

    for trace in fig.data:
        meta = trace.meta if isinstance(trace.meta, dict) else {}
        kind = meta.get("kind")
        if kind is None or "layer" not in meta:
            continue
        t = trace.type
        if t in ("scatter", "bar", "heatmap"):
            current["x"], current["y"] = readers(trace)
        else:
            current["x"], current["y"] = (lambda v: v), (lambda v: v)
        if t in ("scatter",):
            rx, ry = readers(trace)
            xs, ys = list(trace.x), list(trace.y)
            if kind in ("line", "dot", "stem base", "stem top", "error bar cap"):
                colours = trace.marker.color if trace.mode == "markers" or (
                    "markers" in (trace.mode or "") and "lines" not in trace.mode) else trace.line.color
                for i, (x, y) in enumerate(zip(xs, ys)):
                    colour = colours[i] if isinstance(colours, (list, tuple)) else colours
                    add(meta, x=rx(_num(x)), y=ry(_num(y)), colour=colour_code_of(colour))
            elif kind == "band":
                for part_x, part_y in zip(_gaps(xs), _gaps(ys)):
                    n = len(part_x) // 2
                    for i in range(n):
                        if meta.get("sideways"):
                            a, b = _num(part_x[i]), _num(part_x[2 * n - 1 - i])
                            add(meta, y=_num(part_y[i]), low=min(a, b), high=max(a, b),
                                colour=colour_code_of(trace.fillcolor))
                        else:
                            a, b = _num(part_y[i]), _num(part_y[2 * n - 1 - i])
                            add(meta, x=_num(part_x[i]), low=min(a, b), high=max(a, b),
                                colour=colour_code_of(trace.fillcolor))
            elif kind in ("stem", "error bar", "segment"):
                for part_x, part_y in zip(_gaps(xs), _gaps(ys)):
                    (x0, y0), (x1, y1) = (_num(part_x[0]), _num(part_y[0])), (_num(part_x[-1]), _num(part_y[-1]))
                    colour = colour_code_of(trace.line.color)
                    if len(part_x) == 2 and x0 == x1:
                        add(meta, x=x0, y=y1, low=min(y0, y1), high=max(y0, y1), colour=colour)
                    elif len(part_x) == 2 and y0 == y1:
                        add(meta, x=x1, y=y0, low=min(x0, x1), high=max(x0, x1), colour=colour)
                    else:
                        for x, y in zip(part_x, part_y):
                            add(meta, x=_num(x), y=_num(y), colour=colour)
            elif kind in ("shape", "contour"):
                for x, y in zip(xs, ys):
                    if x is None:
                        continue
                    add(meta, x=_num(x), y=_num(y), value=meta.get("value", math.nan) if kind == "contour" else
                        math.nan, colour=meta.get("colour", ""))
            elif kind == "hexagon":
                seen = set()
                for data in trace.customdata:
                    if data[0] is None or data[3] in seen:
                        continue
                    seen.add(data[3])
                    add(meta, x=float(data[0]), y=float(data[1]), value=float(data[2]),
                        colour=colour_code_of(trace.fillcolor))
        elif t == "bar":
            rx, ry = readers(trace)
            upright = trace.orientation != "h"
            places = list(trace.x if upright else trace.y)
            lengths = list(trace.y if upright else trace.x)
            colours = trace.marker.color
            for i, (place, length, base) in enumerate(zip(places, lengths, trace.base)):
                base, length = _num(base), float(length)
                if isinstance(base, pd.Timestamp):  # bars on a date axis: lengths in milliseconds
                    end = base + pd.Timedelta(milliseconds=length)
                    low, high = min(base, end), max(base, end)
                else:
                    low, high = min(base, base + length), max(base, base + length)
                colour = colour_code_of(colours[i] if isinstance(colours, (list, tuple)) else colours)
                if upright:
                    add(meta, x=rx(_num(place)), y=length, low=low, high=high, colour=colour)
                else:
                    add(meta, x=length, y=ry(_num(place)), low=low, high=high, colour=colour)
        elif t == "heatmap":
            for y, row in zip(trace.y, trace.z):
                for x, v in zip(trace.x, row):
                    add(meta, x=_num(x), y=_num(y), value=math.nan if v is None else float(v))
        elif t == "pie":
            start = 90 - (trace.rotation or 0)
            sign = 1 if trace.direction == "counterclockwise" else -1
            at = start
            for v, colour in zip(trace.values, trace.marker.colors):
                end = at + sign * 360 * float(v)
                add(meta, low=min(at, end), high=max(at, end), value=float(v), colour=colour_code_of(colour))
                at = end
        elif t == "scatterpolar":
            colours = trace.marker.color if trace.mode == "markers" else trace.line.color
            for i, (theta, r) in enumerate(zip(trace.theta, trace.r)):
                colour = colours[i] if isinstance(colours, (list, tuple)) else colours
                add(meta, x=math.radians(theta), y=float(r), colour=colour_code_of(colour))
        elif t == "barpolar":
            for theta, r, base in zip(trace.theta, trace.r, trace.base):
                add(meta, x=math.radians(theta), y=float(r), low=min(base, base + r), high=max(base, base + r),
                    colour=colour_code_of(trace.marker.color[0] if isinstance(trace.marker.color, (list, tuple))
                                          else trace.marker.color))
        elif t == "scatter3d":
            colours = trace.marker.color if trace.mode == "markers" else trace.line.color
            for i, (x, y, z) in enumerate(zip(trace.x, trace.y, trace.z)):
                colour = colours[i] if isinstance(colours, (list, tuple)) else colours
                add(meta, x=float(x), y=float(y), value=float(z), colour=colour_code_of(colour))
        elif t == "surface":
            for y, row in zip(trace.y, trace.z):
                for x, z in zip(trace.x, row):
                    if z is not None:
                        add(meta, x=float(x), y=float(y), value=float(z))
        elif t == "mesh3d":
            points = np.column_stack([trace.x, trace.y, trace.z]).reshape(-1, 8, 3)
            faces = list(trace.facecolor or ())
            for i, box in enumerate(points):
                (x0, y0, z0), (x1, y1, z1) = box.min(axis=0), box.max(axis=0)
                colour = colour_code_of(faces[12 * i]) if len(faces) > 12 * i else ""  # 12 triangles per bar
                add(meta, x=(x0 + x1) / 2, y=(y0 + y1) / 2, low=z0, high=z1, value=z1 - z0, colour=colour)
    for shape in fig.layout.shapes or ():
        kind, panel, layer, series = (shape.name or "|||").split("|", 3)
        if not kind:
            continue
        meta = dict(panel=int(panel), layer=int(layer), kind=kind, series=series)
        x_data = not str(shape.xref).endswith("domain")
        y_data = not str(shape.yref).endswith("domain")
        if kind == "rectangle":
            y0, y1 = _num(shape.y0), _num(shape.y1)
            add(meta, x=(_num(shape.x0) + _num(shape.x1)) / 2 if x_data else math.nan,
                y=(y1 - y0) if y_data else math.nan, low=min(y0, y1) if y_data else math.nan,
                high=max(y0, y1) if y_data else math.nan, colour=colour_code_of(shape.fillcolor))
        else:
            for x, y in ((shape.x0, shape.y0), (shape.x1, shape.y1)):
                add(meta, x=_num(x) if x_data else math.nan, y=_num(y) if y_data else math.nan,
                    colour=colour_code_of(shape.line.color))
    return pd.DataFrame(rows, columns=list(NUMBER_COLUMNS))


def text_from_web(fig) -> pd.DataFrame:
    """(panel, part, text) of every piece of text on the web page."""
    meta = (fig.layout.meta or {}).get("simplydata", {})
    meta_axes, legends = meta.get("axes", {}), meta.get("legends", {})
    rows = []
    title = meta.get("title")
    if title and fig.layout.title.text:
        rows.append((title["panel"], title["part"], fig.layout.title.text))
    for note in fig.layout.annotations or ():
        part, panel = (note.name or "note|0").split("|")
        if note.text:
            rows.append((int(panel), part, _plain(note.text)))
    for name, facts in meta_axes.items():
        panel, role, kind = facts["panel"], facts["role"], facts["kind"]
        if kind in ("polar", "3d"):
            layout = fig.layout[name]
            if kind == "3d":
                for letter in ("x", "y", "z"):
                    axis = layout[f"{letter}axis"]
                    if axis.title.text:
                        rows.append((panel, f"{letter} label", axis.title.text))
                for letter in ("x", "y"):
                    rows += [(panel, f"tick {letter}", w) for w in layout[f"{letter}axis"].ticktext or ()]
            else:
                rows += [(panel, "tick x", w) for w in layout.angularaxis.ticktext or ()]
                rows += [(panel, "tick y", w) for w in layout.radialaxis.ticktext or ()]
            continue
        letter = name[0]
        axis = fig.layout[{"x": "xaxis", "y": "yaxis"}[letter] + name[1:]]
        if axis.visible is False and role and (role != f"second {letter}"):
            continue
        prefix = role if role == f"second {letter}" else ("" if not role else None)
        if prefix is None:
            continue
        part = f"{prefix} label".strip() if prefix else f"{letter} label"
        if axis.title.text:
            rows.append((panel, part, axis.title.text))
        tick = f"tick {prefix}" if prefix else f"tick {letter}"
        rows += [(panel, tick, w) for w in axis.ticktext or ()]
    for trace in fig.data:
        if trace.showlegend and trace.name:
            rows.append((legends.get(trace.legend or "legend", 0), "legend entry", trace.name))
        if trace.type == "pie" and trace.showlegend:
            rows += [(legends.get(trace.legend or "legend", 0), "legend entry", label) for label in trace.labels]
        bar = getattr(getattr(trace, "marker", None), "colorbar", None)
        if bar is not None and getattr(trace.marker, "showscale", False) and bar.title.text:
            rows.append((trace.meta.get("panel", 0), "colour bar label", bar.title.text))
    for key, panel in legends.items():
        title = fig.layout[key].title.text
        if title:
            rows.append((panel, "legend title", title))
    return pd.DataFrame(rows, columns=["panel", "part", "text"])


def _plain(text):
    import html

    return html.unescape(text.replace("<br>", "\n"))


def scales_from_web(fig) -> pd.DataFrame:
    """(panel, scale, name, low, high, kind, flipped, tick words) of each flat axis and colour scale."""
    meta_axes = _axes_meta(fig)
    rows = []
    for name, facts in meta_axes.items():
        if facts["kind"] in ("polar", "3d") or not (facts["panel"] or facts["role"]):
            continue  # an empty frame (the base of a chart drawn in parts) has no scales of its own
        letter = name[0]
        axis = fig.layout[{"x": "xaxis", "y": "yaxis"}[letter] + name[1:]]
        role = facts["role"]
        if role and role != f"second {letter}":
            continue
        scale = role or letter
        low, high = facts.get("own range") or axis.range
        if axis.type == "log" and not facts.get("own range"):
            low, high = 10 ** low, 10 ** high
        kind = facts.get("shown as") or {"date": "dates", "group": "groups"}.get(
            facts["kind"], "log" if axis.type == "log" else "numbers")
        flipped = _num(low) > _num(high)
        low, high = (_num(high), _num(low)) if flipped else (_num(low), _num(high))
        rows.append(dict(panel=facts["panel"], scale=scale, name=axis.title.text or facts.get("name") or "",
                         low=low, high=high,
                         kind=kind, flipped=bool(flipped), **{"tick words": ", ".join(axis.ticktext or ())}))
    for trace in fig.data:
        meta = trace.meta if isinstance(trace.meta, dict) else {}
        if meta.get("kind") != "colour scale":
            continue
        bar = trace.marker.colorbar if trace.marker.showscale else None
        rows.append(dict(panel=meta["panel"], scale="colour", name=(bar.title.text or "") if bar else "",
                         low=float(trace.marker.cmin), high=float(trace.marker.cmax), kind=meta["scale kind"],
                         flipped=False, **{"tick words": ", ".join(bar.ticktext or ()) if bar else ""},
                         colours=meta["colours"]))
    return pd.DataFrame(rows)
