"""Charts as web pages: chart.save("marks.html") and chart.show_in_web_page() (charts phase, batch 3; approved by
Manish on 2026-11-25, decisions D2 to D5 and D10 of the charts proposal).

How a web page is made (decision D3): the chart is drawn once by matplotlib and seaborn, exactly as for a picture,
and what was drawn is then copied into a plotly figure. The numbers come from the same readers as
chart.get_numbers_drawn() (simplydata._numbers_drawn), the words and scales from those of chart.get_text_drawn() and
chart.get_scales_drawn() (simplydata._read_back), the places of the panels, legends, notes and colour bars from
where matplotlib put them. plotly computes nothing: no bins, densities, boxes or fitted lines are worked out again,
so the web page shows the same numbers as the picture.

Each kind of drawn row becomes one kind of plotly mark: lines and dots go.Scatter, bars go.Bar (go.Barpolar on a
round chart), bands, shapes, contour lines and hexagons filled go.Scatter outlines, heat map cells go.Heatmap, pie
slices go.Pie, rectangles and lines across the plot area layout shapes, 3D lines and dots go.Scatter3d, surfaces
go.Surface and 3D bars go.Mesh3d. Each plotly mark keeps in its meta which panel, layer and kind of row it shows,
so a test can read the web page back and compare it with the picture.

What plotly cannot draw is refused with one sentence (decision D5): a broken axis (break_between_y), a square-root,
logit or asinh scale (use_scale_y) and a log scale through zero (use_log_scale_y(through_zero=True)).

Privacy (the "no leaks" rule, proposal section 3.4): plotly.js is written into the file (include_plotlyjs=True),
never loaded from the web; MathJax is not loaded; the page names no web fonts; plotly's links to its online
services are switched off and the picture button is taken away (pictures come from matplotlib, decision D4). A page
opened by show_in_web_page() is a file on this computer opened by the browser: no server is started. The page
holds the numbers drawn and only the columns named in show_when_pointing(), and saving it says so once.
"""

from __future__ import annotations

import contextlib
import html as html_text
import io
import math
import re

import numpy as np

from ._errors import SimplydataError

INSTALL = 'pip install "simplydata[web]"'
PIXELS_PER_INCH = 96  # a web page's pixels: plotly sizes are in these
WIDEST_PAGE = 1100  # pixels: a wider chart (a page of several) is drawn smaller, text and marks with it, to fit
WEB_CONFIG = {
    "displaylogo": False,  # no plotly logo linking to plotly's website
    "showSendToCloud": False,
    "plotlyServerURL": "",
    "modeBarButtonsToRemove": ["toImage", "sendDataToCloud"],  # pictures come from matplotlib: chart.save("x.png")
    "responsive": False,
}
SAVED_NOTE = ("Note: the web page holds the numbers drawn and the columns shown when pointing; share it as you would "
              "share the table.")
PICTURE_NOTE = ("Note: pointing and range bars only show in web pages (.html); this picture leaves them out. "
                'Use chart.save("chart.html") or chart.show_in_web_page().')
FONT_NOTE = ("Note: a web page names the font of chart.use_font(); the reader's browser shows it only if that "
             "computer has it, else a font like it. The page loads no fonts from the web.")
_NOTE_KEYS = {"saved": "web page holds the numbers", "picture": "pointing only in web pages",
              "font": "web page font"}

# matplotlib marker -> plotly marker symbol
SYMBOLS = {"o": "circle", "s": "square", "^": "triangle-up", "v": "triangle-down", "<": "triangle-left",
           ">": "triangle-right", "D": "diamond", "d": "diamond-tall", "X": "x", "x": "x-thin", "P": "cross",
           "+": "cross-thin", "*": "star", "p": "pentagon", "h": "hexagon", "H": "hexagon2", "8": "octagon",
           ".": "circle", ",": "square", "_": "line-ew", "|": "line-ns", "1": "y-down", "2": "y-up",
           "3": "y-left", "4": "y-right"}
# matplotlib hatch -> plotly bar pattern
PATTERNS = {"/": "/", "\\": "\\", "x": "x", "-": "-", "|": "|", "+": "+", ".": ".", "o": ".", "O": ".", "*": "x"}
# matplotlib dashes -> plotly dash
DASHES = {"-": "solid", "solid": "solid", "--": "dash", "dashed": "dash", ":": "dot", "dotted": "dot",
          "-.": "dashdot", "dashdot": "dashdot"}
MOVE_TO, CLOSE = 1, 79  # matplotlib Path codes


# ---------------------------------------------------------------- plotly and the notes
def need_plotly():
    """plotly.graph_objects, or a plain SimplydataError with the install line."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        raise SimplydataError(
            "A web page (.html) or chart.show_in_web_page() needs plotly, which is not installed.\n"
            f"Install it with:  {INSTALL}\n"
            "Pictures (.png, .pdf, .svg) work without it.") from None
    return go


def _note_once(key, line):
    from ._errors import _NOTED

    if _NOTE_KEYS[key] in _NOTED:
        return
    _NOTED.add(_NOTE_KEYS[key])
    print(line)


def picture_note(chart):
    """A picture of a chart with show_when_pointing() or add_range_bar_x(): one note, once."""
    settings = chart.__dict__.get("_settings") or {}
    if settings.get("pointing") or settings.get("range_bar_x"):
        _note_once("picture", PICTURE_NOTE)


# ---------------------------------------------------------------- what plotly cannot draw (decision D5)
_SCALE_WORDS = {"symlog": "a log scale through zero (use_log_scale_{a}(through_zero=True))",
                "logit": 'a logit scale (use_scale_{a}("logit"))', "asinh": 'an asinh scale (use_scale_{a}("asinh"))',
                "function": 'a square-root scale (use_scale_{a}("square root"))',
                "functionlog": "a scale of its own"}


def refuse_what_plotly_cannot_draw(chart, fig):
    from ._numbers_drawn import panels_of

    if (chart.__dict__.get("_settings") or {}).get("y_break"):
        raise SimplydataError("plotly cannot draw a broken axis (chart.break_between_y), so a web page cannot show "
                              "this chart; save a picture (.png, .pdf) instead.")
    for ax in panels_of(fig):
        if type(ax).__name__ == "SecondaryAxis":  # add_second_x(formula=): its own scale is drawn by its tick words
            continue
        for name in ("x", "y"):
            scale = getattr(ax, f"get_{name}scale")()
            if scale in _SCALE_WORDS:
                raise SimplydataError(f"plotly cannot draw {_SCALE_WORDS[scale].format(a=name)}, so a web page cannot "
                                      "show this chart; save a picture (.png, .pdf) instead.")


# ---------------------------------------------------------------- colours and sizes
def css(code, alpha=None):
    """A colour code ("#0072b2", "#0072b280") or any matplotlib colour as plotly's rgba() text."""
    from matplotlib.colors import to_rgba

    if code is None or (isinstance(code, str) and code in ("", "none")):
        return "rgba(0,0,0,0)"
    try:
        r, g, b, a = to_rgba(code)
    except (TypeError, ValueError):
        return "rgba(0,0,0,0)"
    a = a if alpha is None else alpha
    return f"rgba({round(r * 255)},{round(g * 255)},{round(b * 255)},{round(a, 4):g})"


def colour_code_of(text) -> str:
    """plotly's rgba() text back to a colour code, as get_numbers_drawn() writes it ("" for none)."""
    from matplotlib.colors import to_hex

    if not text or not isinstance(text, str):
        return ""
    if text.startswith("rgba(") or text.startswith("rgb("):
        parts = [float(v) for v in text[text.index("(") + 1:-1].split(",")]
        r, g, b = (v / 255 for v in parts[:3])
        a = parts[3] if len(parts) > 3 else 1.0
        if a == 0:
            return ""
        return to_hex((r, g, b, a), keep_alpha=a < 1)
    return to_hex(text, keep_alpha=False)


class _Page:
    """Where things are on the drawn figure, in plotly's units: paper fractions and web pixels."""

    def __init__(self, fig):
        self.fig = fig
        self.width, self.height = fig.bbox.width, fig.bbox.height  # display pixels at fig.dpi
        # the whole chart, text and marks too, is made smaller when it would be wider than a usual window
        self.shrink = min(1.0, WIDEST_PAGE / (fig.get_figwidth() * PIXELS_PER_INCH))
        self.scale = PIXELS_PER_INCH / fig.dpi * self.shrink

    def box(self, bbox):
        return (bbox.x0 / self.width, bbox.x1 / self.width, bbox.y0 / self.height, bbox.y1 / self.height)

    def point(self, x, y):
        return x / self.width, y / self.height

    def px(self, display_pixels):
        return float(display_pixels) * self.scale

    def points(self, size):
        return float(size) * PIXELS_PER_INCH / 72 * self.shrink


def _clip(v):
    return min(max(float(v), 0.0), 1.0)


def _font(text, page, colour=True):
    font = {"size": page.points(text.get_fontsize())}
    if colour:
        font["color"] = css(text.get_color())
    if str(text.get_fontweight()) in ("bold", "heavy", "700", "800", "900") or text.get_fontweight() in (700, 800,
                                                                                                         900):
        font["weight"] = "bold"
    return font


# ---------------------------------------------------------------- reading what is drawn, for each set of axes
def _axis_kind(axis) -> str:
    from ._numbers_drawn import _axis_reader

    return _axis_reader(axis)[1]


def _as_shown(value, read, kind):
    """A drawn number as the web page holds it: a date on a date axis, else the number itself."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if kind == "date":
        return read(value)
    return float(value)


def _hover_value(value, read, kind) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    shown = read(value) if kind in ("date", "group") else value
    if hasattr(shown, "year"):
        return str(shown.date()) if not (shown.hour or shown.minute or shown.second) else str(shown)
    if isinstance(shown, str):
        return shown
    return f"{float(shown):.4g}"


class _Axes:
    """One matplotlib Axes and the plotly axes it becomes."""

    def __init__(self, ax, number, panel, role, rows, page):
        self.ax, self.number, self.panel, self.role, self.rows, self.page = ax, number, panel, role, rows, page
        self.kind = {"polar": "polar", "3d": "3d"}.get(getattr(ax, "name", ""), "flat")
        suffix = "" if number == 1 else str(number)
        self.x, self.y = f"x{suffix}", f"y{suffix}"
        self.x_layout, self.y_layout = f"xaxis{suffix}", f"yaxis{suffix}"
        self.polar, self.scene = f"polar{suffix}", f"scene{suffix}"
        self.domain = page.box(ax.get_window_extent())
        if self.kind == "flat":
            self.read_x, self.x_kind = _reader(ax.xaxis)
            self.read_y, self.y_kind = _reader(ax.yaxis)
        else:
            self.read_x, self.x_kind = (lambda v: v), "number"
            self.read_y, self.y_kind = (lambda v: v), "number"

    def place(self, trace):
        if self.kind == "polar":
            trace["subplot"] = self.polar
        elif self.kind == "3d":
            trace["scene"] = self.scene
        else:
            trace["xaxis"], trace["yaxis"] = self.x, self.y
        return trace

    def name_x(self):
        return self.ax.get_xlabel() or "x"

    def name_y(self):
        return self.ax.get_ylabel() or "y"


def _shown_kind(a, axis, letter) -> str:
    """What get_scales_drawn() calls the scale ("numbers", "groups", "dates", "log" ...), read the same way."""
    from ._read_back import _axis_row

    try:
        return _axis_row(a.panel, letter, a.ax, axis, "", letter)["kind"]
    except (TypeError, ValueError, AttributeError):
        return ""


def _reader(axis):
    from ._numbers_drawn import _axis_reader

    return _axis_reader(axis)


# ---------------------------------------------------------------- the translator
class Translator:
    """Copies one drawn matplotlib figure into plotly traces and a plotly layout."""

    def __init__(self, chart, fig, see_through=False):
        from ._numbers_drawn import numbered_panels
        from ._read_back import drawn

        self.chart, self.fig = chart, fig
        drawn(fig)
        self.page = _Page(fig)
        self.see_through = see_through
        self.traces: list = []
        self.layout: dict = {"annotations": [], "shapes": []}
        self.meta_axes: dict = {}
        self.axes: list[_Axes] = []
        self.left_out: list = []
        self.title_part = None
        self.meta_legends: dict = {}
        self.extra_right = 0.0  # web pixels added on the right for a legend moved outside its chart
        last_layer: dict = {}
        for number, (ax, panel, role, (rows, _, _)) in enumerate(numbered_panels(fig), start=1):
            axes = _Axes(ax, number, panel, role, rows, self.page)
            # layers are numbered as get_numbers_drawn() numbers them: a second axis's after its panel's own
            axes.layer_offset = last_layer.get(panel, 0) if panel else 0
            last_layer[panel] = axes.layer_offset + max([r["layer"] for r in rows] or [0])
            self.axes.append(axes)
        self.by_ax = {id(a.ax): a for a in self.axes}
        self.pointing = _Pointing(chart)

    # ------------------------------------------------------------ the whole figure
    def translate(self):
        from matplotlib import rcParams

        for axes in self.axes:
            self._axes_layout(axes)
            self._traces_of(axes)
        self._colour_scales()
        self._legends()
        self._texts()
        page = self.page
        face = self.fig.get_facecolor()
        plot_face = self.axes[0].ax.get_facecolor() if self.axes else face
        family = rcParams["font.family"]
        family = family if isinstance(family, str) else ", ".join(family)
        names = rcParams.get(f"font.{family}", []) if family in ("sans-serif", "serif", "monospace") else []
        extra = math.ceil(self.extra_right) if self.extra_right > 0 else 0
        self.layout.update(
            width=round(self.fig.get_figwidth() * PIXELS_PER_INCH * page.shrink) + extra,
            height=round(self.fig.get_figheight() * PIXELS_PER_INCH * page.shrink),
            autosize=False,
            margin=dict(l=0, r=extra, t=0, b=0, pad=0, autoexpand=False),
            paper_bgcolor="rgba(0,0,0,0)" if self.see_through else css(face),
            plot_bgcolor="rgba(0,0,0,0)" if self.see_through else css(plot_face),
            font=dict(family=", ".join(list(names)[:3] + [family]), size=page.points(rcParams["font.size"]),
                      color=css(rcParams["text.color"])),
            hovermode="closest",
            showlegend=any(t.get("showlegend") for t in self.traces),
            meta={"simplydata": {"axes": self.meta_axes, "left out": sorted(set(self.left_out)),
                                 "legends": self.meta_legends,
                                 "title": dict(zip(("part", "panel"), self.title_part)) if self.title_part
                                 else None}},
        )
        self.pointing.note()
        if self.left_out:
            from ._core import chart_note

            kinds = ", ".join(sorted(set(self.left_out)))
            line = (f"Note: the web page leaves out what it cannot draw from this chart ({kinds}); the picture "
                    "(.png, .pdf) shows everything.")
            chart_note(("web left out", line), lambda _n, line=line: line)
        if self.pointing.all_lines:
            self.layout["hovermode"] = "x unified"
        if (self.chart.__dict__.get("_settings") or {}).get("range_bar_x"):
            self._range_bar()
        return self.traces, self.layout

    # ------------------------------------------------------------ axes
    def _axes_layout(self, a: _Axes):
        from ._read_back import _ticks

        ax, page = a.ax, self.page
        domain_x = [_clip(a.domain[0]), _clip(a.domain[1])]
        domain_y = [_clip(a.domain[2]), _clip(a.domain[3])]
        if a.kind == "polar":
            self._polar_layout(a, domain_x, domain_y)
            return
        if a.kind == "3d":
            self._scene_layout(a, domain_x, domain_y)
            return
        main = self._main_of(a)
        # A second axis (add_second_y, add_second_x: a column or formula=) is drawn over its panel: its own scale
        # overlays the panel's axis and is anchored to the panel's other axis; its marks use the panel's other axis.
        shared_letter = {"second y": "x", "second x": "y"}.get(a.role) if main is not None else None
        if shared_letter == "x":
            a.x, a.x_layout = main.x, main.x_layout
        elif shared_letter == "y":
            a.y, a.y_layout = main.y, main.y_layout
        for letter, axis, kind, read in (("x", ax.xaxis, a.x_kind, a.read_x), ("y", ax.yaxis, a.y_kind, a.read_y)):
            if letter == shared_letter:
                continue
            name = a.x_layout if letter == "x" else a.y_layout
            other = a.y if letter == "x" else a.x
            scale = axis.get_scale()
            low, high = ax.get_xlim() if letter == "x" else ax.get_ylim()
            ticks = _ticks(axis, ax)
            second = type(ax).__name__ == "SecondaryAxis"
            if second:  # add_second_x(formula=): the ticks of the other units, placed on the main axis's scale
                ticks, low, high = self._second_scale_ticks(ax, axis, ticks, main)
            layout = dict(domain=domain_x if letter == "x" else domain_y, anchor=other, automargin=False,
                          zeroline=False, showgrid=False, tickmode="array")
            if scale == "log" and not second:
                layout["type"] = "log"
                layout["range"] = [math.log10(low), math.log10(high)]
            elif kind == "date":
                layout["type"] = "date"
                layout["range"] = [read(low), read(high)]
            else:
                layout["type"] = "linear"
                layout["range"] = [float(low), float(high)]
            if kind == "date":
                layout["tickvals"] = [read(loc) for loc, _ in ticks]
            else:
                layout["tickvals"] = [float(loc) for loc, _ in ticks]
            layout["ticktext"] = [words for _, words in ticks]
            layout["showticklabels"] = bool(ticks)
            layout["ticks"] = "outside" if ticks else ""
            labels = axis.get_majorticklabels()
            if labels:
                layout["tickfont"] = dict(size=page.points(labels[0].get_fontsize()), color=css(labels[0].get_color()))
                if labels[0].get_rotation():
                    layout["tickangle"] = -float(labels[0].get_rotation())
            label = axis.get_label()
            if label.get_visible() and label.get_text():
                layout["title"] = dict(text=label.get_text(), font=_font(label, page))
            hidden_name = label.get_text() if not label.get_visible() else ""
            grid_at, grid_line = _grid_lines(axis, low, high)
            # plotly draws a grid line at every tick word; matplotlib only where its grid lines are (the big ticks:
            # a log axis also writes some small ticks, 20, 30 ..., with no grid line), so where they differ the grid
            # lines are drawn as lines of their own at matplotlib's places
            if grid_line is not None and ax.axison and axis.get_visible():  # a hidden axis draws no grid lines
                grid_style = dict(color=css(grid_line.get_color()), width=page.points(grid_line.get_linewidth()))
                if set(grid_at) == {float(loc) for loc, _ in ticks}:
                    layout.update(showgrid=True, gridcolor=grid_style["color"], gridwidth=grid_style["width"])
                else:
                    for place in grid_at:
                        value = read(place) if kind == "date" else float(place)  # a shape on a log axis: data
                        across = (dict(xref=f"{other} domain", x0=0, x1=1, yref=a.y, y0=value, y1=value)
                                  if letter == "y" else
                                  dict(yref=f"{other} domain", y0=0, y1=1, xref=a.x, x0=value, x1=value))
                        self.layout["shapes"].append(dict(type="line", layer="below", line=grid_style, **across))
            minor = [m for m in axis.get_minorticklocs() if min(low, high) <= m <= max(low, high)]
            if minor and axis.get_minor_ticks() and axis.get_minor_ticks()[0].tick1line.get_visible():
                layout["minor"] = dict(ticks="outside", showgrid=False,
                                       tickvals=[read(m) if kind == "date" else float(m) for m in minor])
            side_spines = ("bottom", "top") if letter == "x" else ("left", "right")
            spines = [ax.spines[s] for s in side_spines if s in ax.spines]
            shown = [s for s in spines if s.get_visible()]
            if shown:
                layout.update(showline=True, linecolor=css(shown[0].get_edgecolor()),
                              linewidth=page.points(shown[0].get_linewidth()), mirror=len(shown) == 2)
            if letter == "x" and axis.get_label_position() == "top":
                layout["side"] = "top"
            if letter == "y" and axis.get_label_position() == "right":
                layout["side"] = "right"
            if not ax.axison:
                layout["visible"] = False
            if main is not None:  # the second axis itself: over the panel's axis, on the far side
                layout["overlaying"] = main.x if letter == "x" else main.y
                layout["anchor"] = main.y if letter == "x" else main.x
                layout["side"] = "top" if letter == "x" else "right"
                layout["visible"] = True
                if second:  # its ticks are placed in the main axis's numbers: the same range and kind of scale
                    under = self.layout[main.x_layout if letter == "x" else main.y_layout]
                    layout["range"], layout["type"] = list(under["range"]), under["type"]
                    # plotly draws an axis only for a mark on it: a mark with no points holds the scale
                    holder = dict(type="scatter", x=[None], y=[None], mode="markers", hoverinfo="skip",
                                  showlegend=False, name="", meta={"panel": a.panel, "kind": "second scale"})
                    holder["xaxis"], holder["yaxis"] = (a.x, main.y) if letter == "x" else (main.x, a.y)
                    self.traces.append(holder)
            else:
                shared = self._shared_with(a, letter)
                if shared is not None:  # same_x / same_y panels zoom together, as matplotlib shares them
                    layout["matches"] = shared.x if letter == "x" else shared.y
                if hidden_name:
                    layout["title"] = dict(text=hidden_name, font=dict(color="rgba(0,0,0,0)"))
            self.layout[name] = layout
            self.meta_axes[(a.x if letter == "x" else a.y)] = {"panel": a.panel, "role": a.role, "kind": kind}

    def _shared_with(self, a, letter):
        """An earlier panel whose x (or y) matplotlib shares with this one, or None."""
        for b in self.axes:
            if b is a:
                return None
            if b.kind != "flat" or b.role:
                continue
            group = a.ax.get_shared_x_axes() if letter == "x" else a.ax.get_shared_y_axes()
            if group.joined(a.ax, b.ax):
                return b
        return None

    def _main_of(self, a):
        from ._numbers_drawn import main_of

        if not a.role:
            return None
        main, _ = main_of(a.ax, [b.ax for b in self.axes])
        return self.by_ax.get(id(main))

    def _second_scale_ticks(self, ax, axis, ticks, main):
        """A secondary axis (add_second_x(formula=)): its tick words, placed at the main axis's numbers through
        matplotlib's own way back (the functions the secondary axis keeps)."""
        functions = getattr(ax, "_functions", None)
        parent = main.ax if main is not None else getattr(ax, "_parent", ax)
        low, high = parent.get_xlim() if axis is ax.xaxis else parent.get_ylim()
        if not functions:
            return ticks, low, high
        back = functions[1]
        with np.errstate(all="ignore"):
            placed = [(float(np.asarray(back(np.array([loc])))[0]), words) for loc, words in ticks]
        return [(loc, words) for loc, words in placed if np.isfinite(loc)], low, high

    def _polar_layout(self, a, domain_x, domain_y):
        from ._read_back import _ticks

        ax, page = a.ax, self.page
        angular_ticks = _ticks(ax.xaxis, ax)
        radial_ticks = _ticks(ax.yaxis, ax)
        low, high = ax.get_ylim()
        self.layout[a.polar] = dict(
            domain=dict(x=domain_x, y=domain_y),
            bgcolor=css(ax.get_facecolor()),
            angularaxis=dict(rotation=math.degrees(ax.get_theta_offset()),
                             direction="counterclockwise" if ax.get_theta_direction() == 1 else "clockwise",
                             tickmode="array", tickvals=[math.degrees(v) for v, _ in angular_ticks],
                             ticktext=[w for _, w in angular_ticks], showgrid=True),
            radialaxis=dict(range=[float(low), float(high)], tickmode="array",
                            tickvals=[float(v) for v, _ in radial_ticks], ticktext=[w for _, w in radial_ticks],
                            angle=math.degrees(ax.get_rlabel_position() * math.pi / 180) if hasattr(
                                ax, "get_rlabel_position") else 0),
        )
        if ax.title.get_text():
            pass  # the title is written as a note above the panel (_texts)
        self.meta_axes[a.polar] = {"panel": a.panel, "role": a.role, "kind": "polar"}
        del page

    def _scene_layout(self, a, domain_x, domain_y):
        from ._read_back import _ticks

        ax = a.ax
        scene = dict(domain=dict(x=domain_x, y=domain_y))
        for letter, axis, limits, label in (("x", ax.xaxis, ax.get_xlim(), ax.get_xlabel()),
                                            ("y", ax.yaxis, ax.get_ylim(), ax.get_ylabel()),
                                            ("z", ax.zaxis, ax.get_zlim(), ax.get_zlabel())):
            ticks = _ticks(axis, ax)
            scene[f"{letter}axis"] = dict(range=[float(limits[0]), float(limits[1])], title=dict(text=label or ""),
                                          tickmode="array", tickvals=[float(v) for v, _ in ticks],
                                          ticktext=[w for _, w in ticks])
        elev, azim = math.radians(ax.elev), math.radians(ax.azim)
        distance = 2.5  # far enough for the tick words and axis names to stay inside the scene
        scene["camera"] = dict(eye=dict(x=distance * math.cos(elev) * math.cos(azim),
                                        y=distance * math.cos(elev) * math.sin(azim),
                                        z=distance * math.sin(elev)))
        scene["aspectmode"] = "cube"
        self.layout[a.scene] = scene
        self.meta_axes[a.scene] = {"panel": a.panel, "role": a.role, "kind": "3d"}

    def _range_bar(self):
        flat = [a for a in self.axes if a.kind == "flat" and not a.role]
        if not flat:
            return
        bottom = min(flat, key=lambda a: a.domain[2])
        self.layout[bottom.x_layout]["rangeslider"] = dict(visible=True, thickness=0.08)
        self.layout["margin"]["b"] = round(0.12 * self.layout["height"])
        self.layout["height"] = round(self.layout["height"] * 1.12)

    # ------------------------------------------------------------ marks
    def _traces_of(self, a: _Axes):
        layers: dict = {}
        for row in a.rows:
            layers.setdefault(row["layer"], []).append(row)
        # plotly draws marks in the order they are given: give them in matplotlib's drawing order (zorder), so a
        # violin's box stays on top of its body as in the picture (sorted() keeps the order of equal zorders)
        for layer, rows in sorted(layers.items(), key=lambda item: _zorder(item[1][0]["_artist"])):
            kind = rows[0]["kind"]
            make = getattr(self, "_" + kind.replace(" ", "_"), None)
            if a.kind == "polar":
                make = {"line": self._polar_line, "dot": self._polar_line, "bar": self._polar_bar,
                        "shape": self._polar_line, "stem": self._polar_line}.get(kind)
            elif a.kind == "3d":
                make = {"line": self._line_3d, "dot": self._dot_3d, "surface": self._surface,
                        "bar": self._bars_3d}.get(kind)
            if make is None:
                self.left_out.append(kind)
                continue
            make(a, layer, rows)

    def _meta(self, a, layer, rows, **more):
        meta = {"panel": a.panel, "layer": layer + a.layer_offset, "kind": rows[0]["kind"],
                "series": rows[0]["series"]}
        meta.update(more)
        return meta

    def _add(self, a, trace, name=""):
        trace["name"] = name
        trace.setdefault("showlegend", False)
        self.traces.append(a.place(trace))
        return trace

    def _hover(self, a, xs, ys, extra=None, rows=None):
        texts = []
        for i, (x, y) in enumerate(zip(xs, ys)):
            parts = []
            if x is not None and not (isinstance(x, float) and math.isnan(x)):
                parts.append(f"{a.name_x()}: {_hover_value(x, a.read_x, a.x_kind)}")
            if y is not None and not (isinstance(y, float) and math.isnan(y)):
                parts.append(f"{a.name_y()}: {_hover_value(y, a.read_y, a.y_kind)}")
            if extra:
                parts.append(extra[i] if isinstance(extra, list) else extra)
            texts.append("<br>".join(p for p in parts if p))
        return texts

    def _x(self, a, v):
        return _as_shown(v, a.read_x, a.x_kind)

    def _y(self, a, v):
        return _as_shown(v, a.read_y, a.y_kind)

    def _data_axes(self, a, artist):
        from ._numbers_drawn import _data_axes

        return _data_axes(artist, a.ax) if artist is not None else (True, True)

    # lines ------------------------------------------------------------------------------------------------
    def _line(self, a, layer, rows, kind_meta=None):
        line = rows[0]["_artist"]
        xs_data, ys_data = self._data_axes(a, line)
        if not (xs_data and ys_data):  # a line across the plot area (draw_line_at_y): a layout shape
            self._line_across(a, layer, rows, line, xs_data, ys_data)
            return
        only_markers = str(line.get_linestyle()).lower() in ("none", "", " ")
        mode = "markers" if only_markers else ("lines+markers" if str(line.get_marker()).lower()
                                               not in ("none", "", " ") else "lines")
        xs = [self._x(a, r["x"]) for r in rows]
        ys = [self._y(a, r["y"]) for r in rows]
        trace = dict(type="scatter", x=xs, y=ys, mode=mode, meta=self._meta(a, layer, rows),
                     opacity=1.0 if line.get_alpha() is None else float(line.get_alpha()))
        if "lines" in mode:
            trace["line"] = dict(color=css(line.get_color()), width=self.page.points(line.get_linewidth()),
                                 dash=_dash(line.get_linestyle()))
            drawstyle = line.get_drawstyle()
            if drawstyle.startswith("steps"):
                trace["line"]["shape"] = {"steps-pre": "vh", "steps": "vh", "steps-post": "hv",
                                          "steps-mid": "hvh"}.get(drawstyle, "linear")
        if "markers" in mode:
            face = line.get_markerfacecolor()
            symbol = SYMBOLS.get(str(line.get_marker()), "circle")
            hollow = str(face).lower() == "none"
            trace["marker"] = dict(symbol=symbol + ("-open" if hollow and "line" not in symbol else ""),
                                   size=self.page.points(line.get_markersize()),
                                   color=css(line.get_markeredgecolor() if hollow else face),
                                   line=dict(color=css(line.get_markeredgecolor()),
                                             width=self.page.points(line.get_markeredgewidth())))
        trace["text"] = self.pointing.texts(a, rows, self._hover(a, [r["x"] for r in rows], [r["y"] for r in rows]))
        trace["hovertemplate"] = "%{text}<extra></extra>"
        self._add(a, trace, rows[0]["series"])

    _stem_base = _line

    def _line_across(self, a, layer, rows, line, xs_data, ys_data):
        xd, yd = line.get_xdata(), line.get_ydata()
        x0, x1 = (float(np.asarray(xd, dtype=float)[0]), float(np.asarray(xd, dtype=float)[-1])) if not xs_data else (
            self._x(a, rows[0]["x"]), self._x(a, rows[-1]["x"]))
        y0, y1 = (float(np.asarray(yd, dtype=float)[0]), float(np.asarray(yd, dtype=float)[-1])) if not ys_data else (
            self._y(a, rows[0]["y"]), self._y(a, rows[-1]["y"]))
        self.layout["shapes"].append(dict(
            type="line", xref=a.x if xs_data else f"{a.x} domain", yref=a.y if ys_data else f"{a.y} domain",
            x0=x0, x1=x1, y0=y0, y1=y1, layer="above",
            line=dict(color=css(line.get_color()), width=self.page.points(line.get_linewidth()),
                      dash=_dash(line.get_linestyle())),
            name=_shape_name(a, layer, rows)))

    # dots -------------------------------------------------------------------------------------------------
    def _dot(self, a, layer, rows):
        artist = rows[0]["_artist"]
        if artist is None or hasattr(artist, "get_xdata"):  # dots drawn by plot(): a Line2D
            self._line(a, layer, rows)
            return
        coll = artist
        sizes = np.asarray(coll.get_sizes(), dtype=float)
        symbols = _symbols_of(coll, len(rows))
        faces = np.asarray(_rgba_list(coll.get_facecolors(), len(rows)))
        edges = np.asarray(_rgba_list(coll.get_edgecolors(), len(rows)))
        alpha = coll.get_alpha()
        hover = self.pointing.texts(a, rows, self._hover(a, [r["x"] for r in rows], [r["y"] for r in rows]))
        groups: dict = {}
        legend = _legend_names(a.ax)
        for i, r in enumerate(rows):
            groups.setdefault((r["colour"], symbols[i]), []).append(i)
        for (colour, symbol), members in groups.items():
            hollow = faces[members[0]][3] == 0
            size = sizes[members[0] % len(sizes)] if len(sizes) else 36.0
            name = legend.get(colour, "") or rows[0]["series"]
            trace = dict(
                type="scatter", mode="markers", x=[self._x(a, rows[i]["x"]) for i in members],
                y=[self._y(a, rows[i]["y"]) for i in members],
                marker=dict(symbol=symbol + ("-open" if hollow and "line" not in symbol else ""),
                            size=[self.page.points(math.sqrt(sizes[i % len(sizes)] if len(sizes) else size))
                                  for i in members],
                            color=[css(_hex(edges[i] if hollow else faces[i])) for i in members],
                            line=dict(color=[css(_hex(edges[i])) for i in members],
                                      width=self.page.points(np.ravel(coll.get_linewidths())[0]
                                                             if len(np.ravel(coll.get_linewidths())) else 0))),
                customdata=[[rows[i]["_piece"]] for i in members],
                text=[hover[i] for i in members], hovertemplate="%{text}<extra></extra>",
                meta=self._meta(a, layer, rows),
                opacity=1.0 if alpha is None else float(np.min(alpha)))
            self._add(a, trace, name)

    # bars -------------------------------------------------------------------------------------------------
    def _bar(self, a, layer, rows):
        patches = [r["_artist"] for r in rows]
        upright = rows[0]["_code"] == "upright"
        values, bases, widths, places = [], [], [], []
        for r, p in zip(rows, patches):
            if upright:
                places.append(self._x(a, r["x"]))
                values.append(float(p.get_height()))
                bases.append(float(p.get_y()))
                widths.append(float(p.get_width()))
            else:
                places.append(self._y(a, r["y"]))
                values.append(float(p.get_width()))
                bases.append(float(p.get_x()))
                widths.append(float(p.get_height()))
        if (upright and a.y_kind == "date") or (not upright and a.x_kind == "date"):
            # time bars: plotly's bars on a date axis take their length in milliseconds and their base as a date
            read = a.read_y if upright else a.read_x
            ends = [read(b + v) for b, v in zip(bases, values)]
            bases = [read(b) for b in bases]
            values = [(e - b).total_seconds() * 1000 for e, b in zip(ends, bases)]
        if (upright and a.x_kind == "date") or (not upright and a.y_kind == "date"):
            widths = [w * 86_400_000 for w in widths]  # matplotlib's dates count days; plotly's, milliseconds
        trace = dict(type="bar", orientation="v" if upright else "h", base=bases, width=widths,
                     meta=self._meta(a, layer, rows))
        trace["x" if upright else "y"] = places
        trace["y" if upright else "x"] = values
        faces = [css(_hex(p.get_facecolor())) for p in patches]
        edge = patches[0].get_edgecolor()
        marker = dict(color=faces[0] if len(set(faces)) == 1 else faces, line=dict(color=css(_hex(edge)), width=self.page.points(patches[0].get_linewidth())))
        hatches = [p.get_hatch() or "" for p in patches]
        if any(hatches):
            shapes = [PATTERNS.get(h[:1], "") for h in hatches]
            # one pattern for the whole set: plotly then shows it in the legend too
            marker["pattern"] = dict(shape=shapes[0] if len(set(shapes)) == 1 else shapes,
                                     fgcolor=_pattern(patches[0])["fgcolor"], solidity=0.3)
        trace["marker"] = marker
        lows = [r["low"] for r in rows]
        highs = [r["high"] for r in rows]
        extra = [f"from {_hover_value(lo, a.read_y if upright else a.read_x, a.y_kind if upright else a.x_kind)} "
                 f"to {_hover_value(hi, a.read_y if upright else a.read_x, a.y_kind if upright else a.x_kind)}"
                 if (upright and a.y_kind == "date") or (not upright and a.x_kind == "date") else ""
                 for lo, hi in zip(lows, highs)]
        trace["text"] = self.pointing.texts(a, rows, self._hover(a, [r["x"] for r in rows], [r["y"] for r in rows],
                                                                 extra=extra))
        trace["textposition"] = "none"
        trace["hovertemplate"] = "%{text}<extra></extra>"
        self._add(a, trace, rows[0]["series"])

    def _rectangle(self, a, layer, rows):
        p = rows[0]["_artist"]
        xs_data, ys_data = self._data_axes(a, p)
        x0, y0, w, h = float(p.get_x()), float(p.get_y()), float(p.get_width()), float(p.get_height())
        x_read = (lambda v: self._x(a, v)) if xs_data else (lambda v: v)
        y_read = (lambda v: self._y(a, v)) if ys_data else (lambda v: v)
        face = p.get_facecolor()
        self.layout["shapes"].append(dict(
            type="rect", xref=a.x if xs_data else f"{a.x} domain", yref=a.y if ys_data else f"{a.y} domain",
            x0=x_read(x0), x1=x_read(x0 + w), y0=y_read(y0), y1=y_read(y0 + h), layer="below" if p.get_zorder() < 2
            else "above", fillcolor=css(_hex(face)) if p.get_fill() else "rgba(0,0,0,0)",
            line=dict(color=css(_hex(p.get_edgecolor())), width=self.page.points(p.get_linewidth())),
            name=_shape_name(a, layer, rows)))

    # bands, shapes, contours -------------------------------------------------------------------------------
    def _band(self, a, layer, rows):
        coll = rows[0]["_artist"]
        sideways = rows[0]["_code"] == "sideways"
        pieces: dict = {}
        for r in rows:
            pieces.setdefault(r["_piece"], []).append(r)
        xs, ys = [], []
        for part in pieces.values():
            if sideways:
                ys += [self._y(a, r["y"]) for r in part] + [self._y(a, r["y"]) for r in reversed(part)] + [None]
                xs += [self._x(a, r["high"]) for r in part] + [self._x(a, r["low"]) for r in reversed(part)] + [None]
            else:
                xs += [self._x(a, r["x"]) for r in part] + [self._x(a, r["x"]) for r in reversed(part)] + [None]
                ys += [self._y(a, r["high"]) for r in part] + [self._y(a, r["low"]) for r in reversed(part)] + [None]
        face = _first_rgba(coll.get_facecolor())
        edge = _first_rgba(coll.get_edgecolor())
        trace = dict(type="scatter", mode="lines", x=xs[:-1], y=ys[:-1], fill="toself", fillcolor=css(_hex(face)),
                     line=dict(color=css(_hex(edge)) if edge is not None and edge[3] > 0 else "rgba(0,0,0,0)",
                               width=self.page.points(np.ravel(coll.get_linewidths())[0])
                               if len(np.ravel(coll.get_linewidths())) else 0),
                     hoverinfo="skip", meta=self._meta(a, layer, rows),
                     orientation="h" if sideways else "v")  # a band along y (violins) lies sideways
        pattern = _pattern(coll)
        if pattern:  # an area with a pattern (hatched=True, black and white)
            trace["fillpattern"] = pattern
        self._add(a, trace, rows[0]["series"])

    def _outline(self, a, layer, rows, kind_name):
        """Shapes and contours: each path as an outline, filled when matplotlib filled it. A point that only
        closes a path (matplotlib's CLOSEPOLY) is kept apart, so it is not drawn as a line."""
        artist = rows[0]["_artist"]
        xs_data, ys_data = self._data_axes(a, artist)
        by_colour: dict = {}
        for r in rows:
            key = (r["colour"], r["_piece"]) if kind_name == "contour" else (r["colour"],)
            by_colour.setdefault(key, {}).setdefault(r["_piece"], []).append(r)
        filled = _is_filled(artist)
        for (colour, *_), pieces in by_colour.items():
            xs, ys = [], []
            for part in pieces.values():
                for r in part:
                    if r["_code"] in (MOVE_TO,) and xs and xs[-1] is not None:
                        xs.append(None)
                        ys.append(None)
                    if r["_code"] == CLOSE:  # alone, between gaps: plotly closes a filled outline itself
                        xs += [None, self._x(a, r["x"]) if xs_data else r["x"], None]
                        ys += [None, self._y(a, r["y"]) if ys_data else r["y"], None]
                        continue
                    xs.append(self._x(a, r["x"]) if xs_data else r["x"])
                    ys.append(self._y(a, r["y"]) if ys_data else r["y"])
                xs.append(None)
                ys.append(None)
            edge = _first_rgba(artist.get_edgecolor()) if hasattr(artist, "get_edgecolor") else None
            line_colour = (css(_hex(edge)) if edge is not None and edge[3] > 0 else
                           ("rgba(0,0,0,0)" if filled else css(colour)))
            widths = np.ravel(artist.get_linewidth()) if hasattr(artist, "get_linewidth") else [1.0]
            trace = dict(type="scatter", mode="lines", x=xs[:-1], y=ys[:-1],
                         line=dict(color=line_colour, width=self.page.points(widths[0]) if len(widths) else 1),
                         meta=self._meta(a, layer, rows, colour=colour, filled=filled,
                                         value=pieces[next(iter(pieces))][0]["value"]),
                         hoverinfo="skip" if kind_name != "contour" else "text",
                         connectgaps=False)
            if filled:
                trace["fill"] = "toself"
                trace["fillcolor"] = css(colour)
                pattern = _pattern(artist)
                if pattern:  # boxes and violins in black and white
                    trace["fillpattern"] = pattern
            if kind_name == "contour":
                level = pieces[next(iter(pieces))][0]["value"]
                trace["text"] = [f"{level:.10g}" if x is not None else "" for x in xs[:-1]]
                trace["hovertemplate"] = "height %{text}<extra></extra>"
            self._add(a, trace, rows[0]["series"])

    def _shape(self, a, layer, rows):
        self._outline(a, layer, rows, "shape")

    def _contour(self, a, layer, rows):
        self._outline(a, layer, rows, "contour")

    def _hexagon(self, a, layer, rows):
        coll = rows[0]["_artist"]
        template = np.asarray(coll.get_paths()[0].vertices, dtype=float)
        codes = coll.get_paths()[0].codes
        if codes is not None:
            template = template[np.asarray(codes) != CLOSE]
        by_colour: dict = {}
        for r in rows:
            by_colour.setdefault(r["colour"], []).append(r)
        for colour, members in by_colour.items():
            xs, ys, data, texts = [], [], [], []
            for r in members:
                for vx, vy in template:
                    xs.append(r["x"] + vx)
                    ys.append(r["y"] + vy)
                    data.append([r["x"], r["y"], r["value"], r["_piece"]])
                    texts.append(f"count: {r['value']:g}")
                xs.append(None)
                ys.append(None)
                data.append([None, None, None, None])
                texts.append("")
            self._add(a, dict(type="scatter", mode="lines", x=xs[:-1], y=ys[:-1], fill="toself",
                              fillcolor=css(colour), line=dict(color=css(colour), width=0.5),
                              customdata=data[:-1], text=texts[:-1], hovertemplate="%{text}<extra></extra>",
                              meta=self._meta(a, layer, rows)), rows[0]["series"])

    # segments ---------------------------------------------------------------------------------------------
    def _segments(self, a, layer, rows):
        artist = rows[0]["_artist"]
        if hasattr(artist, "get_xdata"):  # error bar caps, stem tops: markers drawn by plot()
            self._line(a, layer, rows)
            return
        by_colour: dict = {}
        for r in rows:
            by_colour.setdefault(r["colour"], {}).setdefault(r["_piece"], []).append(r)
        widths = np.ravel(artist.get_linewidths()) if hasattr(artist, "get_linewidths") else [1.0]
        styles = artist.get_linestyles() if hasattr(artist, "get_linestyles") else []
        dash = "solid" if not len(styles) or styles[0][1] is None else "dash"
        for colour, pieces in by_colour.items():
            xs, ys = [], []
            for part in pieces.values():
                r = part[0]
                code = r["_code"]
                if code in ("upright", "upright down"):
                    y0, y1 = (r["low"], r["high"]) if code == "upright" else (r["high"], r["low"])
                    xs += [self._x(a, r["x"]), self._x(a, r["x"]), None]
                    ys += [self._y(a, y0), self._y(a, y1), None]
                elif code in ("level", "level back"):
                    x0, x1 = (r["low"], r["high"]) if code == "level" else (r["high"], r["low"])
                    xs += [self._x(a, x0), self._x(a, x1), None]
                    ys += [self._y(a, r["y"]), self._y(a, r["y"]), None]
                else:
                    xs += [self._x(a, p["x"]) for p in part] + [None]
                    ys += [self._y(a, p["y"]) for p in part] + [None]
            self._add(a, dict(type="scatter", mode="lines", x=xs[:-1], y=ys[:-1], connectgaps=False,
                              line=dict(color=css(colour), width=self.page.points(widths[0]) if len(widths) else 1,
                                        dash=dash),
                              hoverinfo="skip", meta=self._meta(a, layer, rows, colour=colour)), rows[0]["series"])

    _stem = _segments
    _error_bar = _segments
    _error_bar_cap = _segments
    _segment = _segments
    _stem_top = _segments

    # cells and slices -------------------------------------------------------------------------------------
    def _cell(self, a, layer, rows):
        artist = rows[0]["_artist"]
        values = np.array([r["value"] for r in rows], dtype=float)
        if type(artist).__name__ == "QuadMesh":
            corners = np.asarray(artist.get_coordinates(), dtype=float)
            if rows[0]["_code"] == "gouraud":
                ny, nx = corners.shape[:2]
                xs, ys = corners[0, :, 0], corners[:, 0, 1]
            else:
                ny, nx = corners.shape[0] - 1, corners.shape[1] - 1
                centres = (corners[:-1, :-1] + corners[1:, 1:]) / 2
                xs, ys = centres[0, :, 0], centres[:, 0, 1]
            grid = values.reshape(ny, nx)
        else:  # an image: one value per pixel, rows from the top when the image's origin is "upper"
            image_values = np.ma.filled(np.ma.asarray(artist.get_array(), dtype=float), np.nan)
            ny, nx = image_values.shape
            left, right, bottom, top = artist.get_extent()
            xs = np.array([left + (j + 0.5) * (right - left) / nx for j in range(nx)])
            if artist.origin == "upper":
                ys = np.array([top + (i + 0.5) * (bottom - top) / ny for i in range(ny)])
            else:
                ys = np.array([bottom + (i + 0.5) * (top - bottom) / ny for i in range(ny)])
            grid = values.reshape(ny, nx)
        norm = artist.norm
        low = float(norm.vmin) if norm.vmin is not None else float(np.nanmin(values))
        high = float(norm.vmax) if norm.vmax is not None else float(np.nanmax(values))
        texts = [[f"{a.name_x()}: {_hover_value(x, a.read_x, a.x_kind)}<br>{a.name_y()}: "
                  f"{_hover_value(y, a.read_y, a.y_kind)}<br>{_number(v)}" for x, v in zip(xs, row)]
                 for y, row in zip(ys, grid)]
        trace = dict(type="heatmap", x=[self._x(a, v) for v in xs], y=[self._y(a, v) for v in ys],
                     z=[[None if not np.isfinite(v) else float(v) for v in row] for row in grid],
                     colorscale=colour_scale(artist, low, high), zmin=low, zmax=high, showscale=False,
                     text=texts, hovertemplate="%{text}<extra></extra>",
                     meta=self._meta(a, layer, rows, colours=artist.get_cmap().name))
        if rows[0]["_code"] == "gouraud":
            trace["zsmooth"] = "best"
        self._add(a, trace, rows[0]["series"])

    def _slice(self, a, layer, rows):
        wedges = [r["_artist"] for r in rows]
        counter = len(rows) < 2 or abs(rows[1]["low"] - rows[0]["high"]) < 1e-9 or abs(
            (rows[1]["low"] - rows[0]["high"]) % 360) < 1e-9
        start = rows[0]["low"] if counter else rows[0]["high"]
        legend = a.ax.get_legend()
        names = [t.get_text() for t in legend.get_texts()] if legend is not None else []
        labels = [names[i] if i < len(names) else (r["series"] or f"slice {i + 1}") for i, r in enumerate(rows)]
        width = getattr(wedges[0], "width", None)
        trace = dict(type="pie", values=[r["value"] for r in rows], labels=labels, sort=False,
                     direction="counterclockwise" if counter else "clockwise", rotation=90 - start,
                     textinfo="none", marker=dict(colors=[css(r["colour"]) for r in rows],
                                                  line=dict(color=css(_hex(wedges[0].get_edgecolor())),
                                                            width=self.page.points(wedges[0].get_linewidth()))),
                     domain=dict(x=[_clip(a.domain[0]), _clip(a.domain[1])], y=[_clip(a.domain[2]),
                                                                                 _clip(a.domain[3])]),
                     hovertemplate="%{label}: %{percent}<extra></extra>",
                     meta=self._meta(a, layer, rows), showlegend=bool(names))
        if width:
            trace["hole"] = max(0.0, 1 - width / wedges[0].r)
        self.traces.append(trace)  # a pie has no axes: it sits in its panel's place

    # round (polar) charts ---------------------------------------------------------------------------------
    def _polar_line(self, a, layer, rows):
        artist = rows[0]["_artist"]
        theta = [math.degrees(r["x"]) for r in rows]
        r_values = [r["y"] for r in rows]
        trace = dict(type="scatterpolar", theta=theta, r=r_values, meta=self._meta(a, layer, rows))
        if rows[0]["kind"] == "dot" or (hasattr(artist, "get_linestyle") and str(artist.get_linestyle()).lower()
                                        in ("none", "", " ")):
            trace.update(mode="markers", marker=dict(color=[css(r["colour"]) for r in rows]))
        else:
            colour = artist.get_color() if hasattr(artist, "get_color") else rows[0]["colour"]
            trace.update(mode="lines", line=dict(color=css(_hex(_first_rgba(colour)))))
            if rows[0]["kind"] == "shape":
                trace.update(fill="toself", fillcolor=css(rows[0]["colour"]))
        self._add(a, trace, rows[0]["series"])

    def _polar_bar(self, a, layer, rows):
        patches = [r["_artist"] for r in rows]
        trace = dict(type="barpolar", theta=[math.degrees(r["x"]) for r in rows],
                     r=[float(p.get_height()) for p in patches], base=[float(p.get_y()) for p in patches],
                     width=[math.degrees(float(p.get_width())) for p in patches],
                     marker=dict(color=[css(r["colour"]) for r in rows],
                                 line=dict(color=css(_hex(patches[0].get_edgecolor())),
                                           width=self.page.points(patches[0].get_linewidth()))),
                     meta=self._meta(a, layer, rows),
                     hovertemplate="%{theta:.0f}°: %{r:.4g}<extra></extra>")
        self._add(a, trace, rows[0]["series"])

    # 3D ---------------------------------------------------------------------------------------------------
    def _line_3d(self, a, layer, rows):
        artist = rows[0]["_artist"]
        self._add(a, dict(type="scatter3d", mode="lines", x=[r["x"] for r in rows], y=[r["y"] for r in rows],
                          z=[r["value"] for r in rows],
                          line=dict(color=css(_hex(_first_rgba(artist.get_color()))),
                                    width=self.page.points(artist.get_linewidth())),
                          meta=self._meta(a, layer, rows)), rows[0]["series"])

    def _dot_3d(self, a, layer, rows):
        self._add(a, dict(type="scatter3d", mode="markers", x=[r["x"] for r in rows], y=[r["y"] for r in rows],
                          z=[r["value"] for r in rows],
                          marker=dict(color=[css(r["colour"]) for r in rows], size=4),
                          customdata=[[r["_piece"]] for r in rows], meta=self._meta(a, layer, rows)),
                  rows[0]["series"])

    def _surface(self, a, layer, rows):
        artist = rows[0]["_artist"]
        xs = sorted({r["x"] for r in rows})
        ys = sorted({r["y"] for r in rows})
        where = {(r["x"], r["y"]): r["value"] for r in rows}
        grid = [[where.get((x, y)) for x in xs] for y in ys]
        if artist.get_array() is not None:
            values = np.asarray([v for row in grid for v in row if v is not None], dtype=float)
            colours = colour_scale(artist, float(values.min()), float(values.max()))
        else:
            face = css(_hex(_first_rgba(artist.get_facecolor())))
            colours = [[0, face], [1, face]]
        self._add(a, dict(type="surface", x=xs, y=ys, z=grid, colorscale=colours, showscale=False,
                          meta=self._meta(a, layer, rows)), rows[0]["series"])

    def _bars_3d(self, a, layer, rows):
        coll = rows[0]["_artist"]
        faces = np.asarray(coll._faces, dtype=float).reshape(int(coll.simplydata_bars_3d), -1, 3)
        xs, ys, zs, i_list, j_list, k_list, colours = [], [], [], [], [], [], []
        for box, r in zip(faces, rows):
            (x0, y0, z0), (x1, y1, z1) = box.min(axis=0), box.max(axis=0)
            start = len(xs)
            for cx, cy, cz in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                               (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)):
                xs.append(float(cx))
                ys.append(float(cy))
                zs.append(float(cz))
            for tri in ((0, 1, 2), (0, 2, 3), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
                        (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)):
                i_list.append(start + tri[0])
                j_list.append(start + tri[1])
                k_list.append(start + tri[2])
                colours.append(css(r["colour"]))
        self._add(a, dict(type="mesh3d", x=xs, y=ys, z=zs, i=i_list, j=j_list, k=k_list, facecolor=colours,
                          flatshading=True, meta=self._meta(a, layer, rows)), rows[0]["series"])

    # ------------------------------------------------------------ colour bars and colour scales
    def _colour_scales(self):
        from ._read_back import _colour_bar_axes, _mappables, _norm_kind, _ticks

        with_bar = set()
        for cax in _colour_bar_axes(self.fig):
            bar = cax._colorbar
            mappable = bar.mappable
            low, high = float(mappable.norm.vmin), float(mappable.norm.vmax)
            vertical = bar.orientation == "vertical"
            label = cax.get_ylabel() if vertical else cax.get_xlabel()
            ticks = _ticks(bar.long_axis, cax)
            box = self.page.box(cax.get_window_extent())
            kind, middle = _norm_kind(mappable.norm)
            colorbar = dict(tickmode="array", tickvals=[float(v) for v, _ in ticks], ticktext=[w for _, w in ticks],
                            thicknessmode="pixels", lenmode="fraction", outlinewidth=0.5)
            if vertical:
                colorbar.update(orientation="v", x=_clip(box[0]), xanchor="left", y=(box[2] + box[3]) / 2,
                                yanchor="middle", len=box[3] - box[2],
                                thickness=self.page.px(cax.get_window_extent().width))
            else:
                colorbar.update(orientation="h", y=_clip(box[2]), yanchor="bottom", x=(box[0] + box[1]) / 2,
                                xanchor="center", len=box[1] - box[0],
                                thickness=self.page.px(cax.get_window_extent().height))
            if label:
                colorbar["title"] = dict(text=label, side="right" if vertical else "bottom")
            owner = self._owner_of(mappable, bar)
            with_bar.add(owner.panel if owner else 0)
            self._scale_trace(owner, mappable, low, high, kind, middle, colorbar=colorbar)
        for a in self.axes:
            if not a.panel or a.panel in with_bar:
                continue
            seen = []
            for artist in _mappables(a.ax):
                key = (id(artist.norm), id(artist.get_cmap()))
                if key in seen:
                    continue
                seen.append(key)
                kind, middle = _norm_kind(artist.norm)
                vmin = artist.norm.vmin
                vmax = artist.norm.vmax
                if vmin is None or vmax is None:
                    continue
                self._scale_trace(a, artist, float(vmin), float(vmax), kind, middle, colorbar=None)

    def _owner_of(self, mappable, bar):
        ax = getattr(mappable, "axes", None)
        if ax is not None and id(ax) in self.by_ax:
            return self.by_ax[id(ax)]
        for parent in (getattr(bar.ax, "_colorbar_info", None) or {}).get("parents", []):
            if id(parent) in self.by_ax:
                return self.by_ax[id(parent)]
        return self.axes[0] if self.axes else None

    def _scale_trace(self, owner, mappable, low, high, kind, middle, colorbar):
        """A colour scale as a mark that draws nothing but its colour bar (plotly shows a colour bar for a mark)."""
        marker = dict(colorscale=colour_scale(mappable, low, high), cmin=low, cmax=high, color=[low, high],
                      showscale=colorbar is not None, size=0.001)
        if colorbar is not None:
            marker["colorbar"] = colorbar
        trace = dict(type="scatter", mode="markers", x=[None, None], y=[None, None], marker=marker,
                     hoverinfo="skip", showlegend=False, name="",
                     meta={"panel": owner.panel if owner else 0, "kind": "colour scale",
                           "colours": mappable.get_cmap().name, "middle": None if math.isnan(middle) else middle,
                           "scale kind": kind})
        if owner is not None and owner.kind == "flat":
            owner.place(trace)
        self.traces.append(trace)

    # ------------------------------------------------------------ legends
    def _legends(self):
        legends = []
        for a in self.axes:
            legend = a.ax.get_legend()
            if legend is not None and legend.get_visible():
                legends.append((legend, [a], a.panel))
        from ._numbers_drawn import _all_axes

        for figure in [self.fig] + list(_subfigures(self.fig)):
            inside = [a for a in self.axes if any(a.ax is b for b in _all_axes(figure))]
            # a legend of the whole chart (put_legend_at_top ...) or of one chart on a page
            panel = 0 if figure is self.fig else min([a.panel for a in inside if a.panel] or [0])
            for legend in figure.legends:
                if legend.get_visible():
                    legends.append((legend, inside or list(self.axes), panel))
        for n, (legend, owners, panel) in enumerate(legends, start=1):
            key = "legend" if n == 1 else f"legend{n}"
            self.meta_legends[key] = panel
            names = [t.get_text() for t in legend.get_texts()]
            title = legend.get_title().get_text() if legend.get_title().get_visible() else ""
            box = self.page.box(legend.get_window_extent())
            # The legend sits where matplotlib put it, held at its corner nearest the edge of its panel, so a
            # legend that is a little bigger on the web page grows away from that edge (inside, or outside)
            area = owners[0].domain if len(owners) == 1 else (0.0, 1.0, 0.0, 1.0)
            right = (box[0] + box[1]) / 2 > (area[0] + area[1]) / 2
            top = (box[2] + box[3]) / 2 > (area[2] + area[3]) / 2
            place = dict(x=_clip(box[1] if right else box[0]), y=_clip(box[3] if top else box[2]),
                         xanchor="right" if right else "left", yanchor="top" if top else "bottom")
            if len(owners) == 1 and legend is owners[0].ax.get_legend() and _legend_crowds_marks(legend, owners[0].ax):
                # matplotlib's legend only just misses the marks: on the page, where it can be a little bigger, it
                # goes outside the chart, at the top on the right, and the page is made wider for it if need be
                place = dict(x=area[1] + 0.01, y=area[3], xanchor="left", yanchor="top")
                needed = self.page.px(legend.get_window_extent().width) * 1.15 + 10
                room = (1 - area[1] - 0.01) * self.layout_width()
                self.extra_right = max(self.extra_right, needed - room)
            self.layout[key] = dict(**place,
                                    itemwidth=30, tracegroupgap=0,
                                    bgcolor=css(_hex(legend.get_frame().get_facecolor()))
                                    if legend.get_frame_on() else "rgba(0,0,0,0)",
                                    bordercolor=css(_hex(legend.get_frame().get_edgecolor()))
                                    if legend.get_frame_on() else "rgba(0,0,0,0)",
                                    borderwidth=1 if legend.get_frame_on() else 0,
                                    font=dict(size=self.page.points(legend.get_texts()[0].get_fontsize()))
                                    if legend.get_texts() else {},
                                    orientation="h" if getattr(legend, "_ncols", 1) > 1 else "v",
                                    title=dict(text=title))
            panels = {o.panel for o in owners}
            shown = set()
            handles = getattr(legend, "legend_handles", [])
            for rank, (name, handle) in enumerate(zip(names, handles)):
                if not name:
                    continue
                trace = next((t for t in self.traces if t.get("name") == name and t.get("meta", {}).get("panel")
                              in panels and t["type"] not in ("pie",) and not t.get("showlegend")
                              and t.get("legend", key) == key), None)
                if trace is None:  # seaborn's legends name no mark: the marks of the entry's colour are that group
                    trace = self._marks_of_colour(handle, panels, name)
                if trace is not None and name not in shown:
                    for t in self.traces:  # every mark of that group hides and shows together
                        if t.get("name") == name and t.get("meta", {}).get("panel") in panels and t["type"] != "pie":
                            t["legendgroup"] = f"{key}:{name}"
                            t["legend"] = key
                    trace.update(showlegend=True, legendrank=1000 + rank)
                else:
                    self._legend_only(owners[0], key, name, handle, rank)
                shown.add(name)
            for t in self.traces:
                if t["type"] == "pie" and t.get("meta", {}).get("panel") in panels and t.get("showlegend"):
                    t["legend"] = key

    def _marks_of_colour(self, handle, panels, name):
        """The bars or dots drawn in a legend entry's colour, named after the entry (or None)."""
        colour = _first_rgba(handle.get_facecolor()) if hasattr(handle, "get_facecolor") else None
        if colour is None or colour[3] == 0:
            return None
        wanted = css(_hex(colour))
        found = [t for t in self.traces if t["type"] in ("bar", "scatter") and not t.get("name")
                 and t.get("meta", {}).get("panel") in panels and _first_colour(t) == wanted]
        for t in found:
            t["name"] = name
        return found[0] if found else None

    def _legend_only(self, a, key, name, handle, rank):
        """A legend entry with no mark of its own name (seaborn's legends): a mark that draws nothing, in the
        entry's look."""
        trace = dict(type="scatter", x=[None], y=[None], name=name, showlegend=True, legend=key,
                     legendgroup=f"{key}:{name}", legendrank=1000 + rank, hoverinfo="skip",
                     meta={"panel": a.panel, "kind": "legend entry"})
        if hasattr(handle, "get_linestyle") and hasattr(handle, "get_marker"):
            marker = str(handle.get_marker())
            lined = str(handle.get_linestyle()).lower() not in ("none", "", " ")
            trace["mode"] = ("lines" if lined else "") + ("+markers" if marker not in ("none", "", " ", "None")
                                                          else "")
            trace["mode"] = trace["mode"].strip("+") or "lines"
            trace["line"] = dict(color=css(handle.get_color()), dash=_dash(handle.get_linestyle()))
            trace["marker"] = dict(color=css(handle.get_markerfacecolor()), symbol=SYMBOLS.get(marker, "circle"))
        elif hasattr(handle, "get_facecolor") and (handle.get_hatch() if hasattr(handle, "get_hatch") else None):
            # a patterned entry: a bar that draws nothing, so the legend shows the colour and the pattern
            colour = _first_rgba(handle.get_facecolor())
            trace.update(type="bar", x=[None], y=[None],
                         marker=dict(color=css(_hex(colour)), pattern=_pattern(handle),
                                     line=dict(color=css(_hex(_first_rgba(handle.get_edgecolor()))), width=1)))
        elif hasattr(handle, "get_facecolor"):
            colour = _first_rgba(handle.get_facecolor())
            edge = _first_rgba(handle.get_edgecolor()) if hasattr(handle, "get_edgecolor") else None
            hollow = colour is None or colour[3] == 0
            trace["mode"] = "markers"
            trace["marker"] = dict(symbol="square" if type(handle).__name__ in ("Rectangle", "Patch") else "circle"
                                   + ("-open" if hollow else ""),
                                   color=css(_hex(edge if hollow else colour)), size=10)
        else:
            trace["mode"] = "markers"
        if a.kind == "flat":
            a.place(trace)
        self.traces.append(trace)

    # ------------------------------------------------------------ text
    def _texts(self):
        from ._numbers_drawn import _all_axes

        fig, page = self.fig, self.page
        renderer = fig.canvas.get_renderer() if hasattr(fig.canvas, "get_renderer") else fig._get_renderer()
        numbers = {id(a.ax): a.panel for a in self.axes}
        for figure in [fig] + list(_subfigures(fig)):
            top = figure is fig
            panel = 0 if top else min([numbers.get(id(ax), 0) for ax in _all_axes(figure) if numbers.get(id(ax))]
                                      or [0])
            sup = getattr(figure, "_suptitle", None)
            if sup is not None and sup.get_visible() and sup.get_text():
                part = getattr(sup, "simplydata_part", "") or ("page title" if top and figure.subfigs else "title")
                if top:
                    x, y = self._centre(sup, renderer)
                    self.layout["title"] = dict(text=sup.get_text(), x=x, y=y, xanchor="center", yanchor="middle",
                                                xref="paper", yref="paper", font=_font(sup, page))
                    self.title_part = (part, panel)
                else:
                    self._note(sup, renderer, part, panel)
            for attr, part in (("_supxlabel", "x label"), ("_supylabel", "y label")):
                text = getattr(figure, attr, None)
                if text is not None and text.get_visible() and text.get_text():
                    self._note(text, renderer, getattr(text, "simplydata_part", "") or part, panel)
            own = {id(getattr(figure, a, None)) for a in ("_suptitle", "_supxlabel", "_supylabel")}
            for text in list(figure.texts) + [t for t in figure.artists if hasattr(t, "get_text")]:
                if id(text) not in own and text.get_visible() and text.get_text():
                    self._note(text, renderer, getattr(text, "simplydata_part", "") or "note", panel,
                               where=getattr(text, "simplydata_where", "") or "")
        for a in self.axes:
            ax = a.ax
            for title, part in ((ax.title, "title"), (ax._left_title, "panel letter"), (ax._right_title, "title")):
                if title.get_visible() and title.get_text():
                    self._note(title, renderer, getattr(title, "simplydata_part", "") or part, a.panel)
            if a.kind != "flat":
                if a.kind == "polar" and ax.get_ylabel():
                    pass
            for text in ax.texts:
                if text.get_visible() and text.get_text():
                    self._note(text, renderer, getattr(text, "simplydata_part", "") or "note", a.panel, owner=a)

    def _centre(self, text, renderer):
        box = text.get_window_extent(renderer)
        return self.page.point((box.x0 + box.x1) / 2, (box.y0 + box.y1) / 2)

    def _note(self, text, renderer, part, panel, owner=None, where=""):
        x, y = self._centre(text, renderer)
        note = dict(text=html_text.escape(text.get_text()).replace("\n", "<br>"), x=x, y=y, xref="paper",
                    yref="paper", xanchor="center", yanchor="middle", showarrow=False, font=_font(text, self.page),
                    textangle=-float(text.get_rotation() or 0), name=f"{part}|{panel}")
        box = text.get_bbox_patch()
        if box is not None and box.get_visible():
            note["bgcolor"] = css(_hex(box.get_facecolor()))
            edge = _first_rgba(box.get_edgecolor())
            if edge is not None and edge[3] > 0:
                note.update(bordercolor=css(_hex(edge)), borderwidth=self.page.points(box.get_linewidth()))
        arrow = getattr(text, "arrow_patch", None)
        if arrow is not None and arrow.get_visible() and owner is not None:
            # a note with an arrow (write_note(arrow=), draw_arrow): plotly's arrow from the words to the place
            head = text.xy
            try:
                hx, hy = owner.ax.transData.transform((owner.ax.xaxis.convert_units(head[0]),
                                                       owner.ax.yaxis.convert_units(head[1])))
            except (TypeError, ValueError):
                hx, hy = None, None
            if hx is not None:
                px, py = self.page.point(hx, hy)
                note.update(x=px, y=py, showarrow=True, arrowhead=2, arrowcolor=css(_hex(_first_rgba(
                    arrow.get_edgecolor()))), arrowwidth=self.page.points(arrow.get_linewidth()),
                    ax=(x - px) * self.layout_width(), ay=-(y - py) * self.layout_height(), axref="pixel",
                    ayref="pixel", standoff=0)
                if not text.get_text().strip():
                    note["text"] = ""
        self.layout["annotations"].append(note)

    def layout_width(self):
        return self.fig.get_figwidth() * PIXELS_PER_INCH * self.page.shrink

    def layout_height(self):
        return self.fig.get_figheight() * PIXELS_PER_INCH * self.page.shrink


# ---------------------------------------------------------------- small helpers of the translator
def _subfigures(fig):
    for sub in getattr(fig, "subfigs", []):
        yield sub
        yield from _subfigures(sub)


def _zorder(artist) -> float:
    try:
        return float(artist.get_zorder())
    except (AttributeError, TypeError, ValueError):
        return 0.0


def _grid_lines(axis, low, high):
    """Where matplotlib drew grid lines along an axis (big ticks and small ticks whose grid line is shown, inside the
    range shown), and one of those lines for its colour and width (None: no grid lines)."""
    room = abs(high - low) * 1e-9
    places, first = [], None
    for locs, ticks in ((axis.get_majorticklocs(), axis.get_major_ticks()),
                        (axis.get_minorticklocs(), axis.get_minor_ticks())):
        for loc, tick in zip(locs, ticks):
            if tick.gridline.get_visible() and min(low, high) - room <= loc <= max(low, high) + room:
                places.append(float(loc))
                first = first or tick.gridline
    return sorted(set(places)), first


def _legend_crowds_marks(legend, ax, grow=0.3) -> bool:
    """True when a legend inside a chart covers a mark, or comes within `grow` of its own width and height of one on
    the sides away from its corner. A web page writes the legend in the page's own pixels, so beside a chart drawn a
    little smaller (a narrow window) it is a little bigger than in the picture: a legend that only just misses the
    marks in the picture would cover them on the page."""
    box, area = legend.get_window_extent(), ax.get_window_extent()  # the figure is drawn: its own renderer
    if not (area.x0 <= (box.x0 + box.x1) / 2 <= area.x1 and area.y0 <= (box.y0 + box.y1) / 2 <= area.y1):
        return False  # a legend outside the chart covers nothing
    right = (box.x0 + box.x1) / 2 > (area.x0 + area.x1) / 2
    top = (box.y0 + box.y1) / 2 > (area.y0 + area.y1) / 2
    width, height = box.width * grow, box.height * grow
    x0, x1 = (box.x0 - width, box.x1) if right else (box.x0, box.x1 + width)
    y0, y1 = (box.y0 - height, box.y1) if top else (box.y0, box.y1 + height)

    def inside(points):
        points = np.asarray(points, dtype=float).reshape(-1, 2)
        points = points[np.all(np.isfinite(points), axis=1)]
        return bool(np.any((points[:, 0] >= x0) & (points[:, 0] <= x1) & (points[:, 1] >= y0) & (points[:, 1] <= y1)))

    def along(points):  # points along each straight piece, so a line passing under the legend counts
        points = np.asarray(points, dtype=float).reshape(-1, 2)
        points = points[np.all(np.isfinite(points), axis=1)]  # a step line to the edge (draw_cumulative_share)
        if len(points) < 2:
            return points
        steps = np.linspace(0, 1, 25)[:, None, None]
        return (points[:-1] + steps * (points[1:] - points[:-1])).reshape(-1, 2)

    for line in ax.get_lines():
        if not line.get_visible() or _is_line_across(line) or not len(line.get_xydata()):
            continue
        points = line.get_transform().transform(np.asarray(line.get_xydata(), dtype=float))
        if inside(points if str(line.get_linestyle()).strip().lower() in ("none", "") else along(points)):
            return True  # a line, or the markers alone (the caps of error bars: nothing is drawn between them)
    for coll in ax.collections:
        if not coll.get_visible():
            continue
        if hasattr(coll, "get_segments"):  # error bars, sticks, rug lines
            if any(inside(along(coll.get_transform().transform(np.asarray(s, dtype=float))))
                   for s in coll.get_segments() if len(s)):
                return True
        elif coll.__class__.__name__ == "PathCollection" and len(coll.get_offsets()):  # dots
            if inside(coll.get_offset_transform().transform(np.asarray(coll.get_offsets(), dtype=float))):
                return True
    for patch in ax.patches:  # bars
        if patch.get_visible() and patch.__class__.__name__ == "Rectangle":
            b = patch.get_window_extent()
            if b.x0 < x1 and b.x1 > x0 and b.y0 < y1 and b.y1 > y0:
                return True
    return False


def _is_line_across(line) -> bool:
    return line.__class__.__name__ in ("AxLine", "_AxLine")


def _dash(style) -> str:
    if isinstance(style, tuple):
        return "solid" if style[1] is None else "dash"
    return DASHES.get(str(style), "solid")


def _hex(colour) -> str:
    from ._numbers_drawn import colour_code

    return colour_code(colour)


def _first_rgba(colours):
    from matplotlib.colors import to_rgba_array

    try:
        array = to_rgba_array(colours)
    except (TypeError, ValueError):
        return None
    return tuple(array[0]) if len(array) else None


def _rgba_list(colours, n):
    from matplotlib.colors import to_rgba_array

    try:
        array = to_rgba_array(colours)
    except (TypeError, ValueError):
        return [(0, 0, 0, 0)] * n
    if len(array) == n:
        return [tuple(c) for c in array]
    if len(array) >= 1:
        return [tuple(array[0])] * n
    return [(0, 0, 0, 0)] * n


def _pattern(artist):
    """plotly's fill pattern for a matplotlib hatch (hatched=True, black and white), or None."""
    hatch = artist.get_hatch() if hasattr(artist, "get_hatch") else None
    shape = PATTERNS.get((hatch or "")[:1], "")
    if not shape:
        return None
    colour = None
    for getter in ("get_hatchcolor", "get_edgecolor"):
        if hasattr(artist, getter):
            colour = _first_rgba(getattr(artist, getter)())
            if colour is not None and colour[3] > 0:
                break
    if colour is None or colour[3] == 0:  # no colour of its own: black or white, whichever shows on the fill
        from .words.second_cues import contrasting

        colour = contrasting(_first_rgba(artist.get_facecolor()))
    return dict(shape=shape, fgcolor=css(_hex(colour)), solidity=0.3)


def _first_colour(trace) -> str:
    marker = trace.get("marker") or {}
    colour = marker.get("color") if trace["type"] == "bar" or trace.get("mode") == "markers" else None
    if isinstance(colour, (list, tuple)):
        colour = colour[0] if colour else None
    return colour or ""


def _number(v) -> str:
    return "" if v is None or not np.isfinite(v) else f"{v:.4g}"


def _is_filled(artist) -> bool:
    if artist is None:
        return False
    if hasattr(artist, "filled"):  # a contour set
        return bool(artist.filled)
    if hasattr(artist, "get_fill") and not artist.get_fill():
        return False
    face = _first_rgba(artist.get_facecolor()) if hasattr(artist, "get_facecolor") else None
    return face is not None and face[3] > 0


def _shape_name(a, layer, rows) -> str:
    return f"{rows[0]['kind']}|{a.panel}|{layer}|{rows[0]['series']}"


def _legend_names(ax) -> dict:
    from ._numbers_drawn import _legend_names as by_key

    names = {}
    for key, name in by_key(ax).items():
        from matplotlib.colors import to_hex

        names[to_hex(key, keep_alpha=key[3] < 1)] = name
    return names


def _symbols_of(coll, n) -> list:
    """The plotly symbol of each dot: matplotlib keeps each dot's shape as a path, compared with its markers."""
    from matplotlib.markers import MarkerStyle

    paths = coll.get_paths()
    if not paths:
        return ["circle"] * n
    known = []
    for code, symbol in (("o", "circle"), ("s", "square"), ("^", "triangle-up"), ("v", "triangle-down"),
                         ("D", "diamond"), ("X", "x"), ("P", "cross"), ("*", "star"), ("p", "pentagon"),
                         ("h", "hexagon"), ("<", "triangle-left"), (">", "triangle-right"), ("d", "diamond-tall")):
        style = MarkerStyle(code)
        vertices = style.get_path().transformed(style.get_transform()).vertices
        known.append((symbol, vertices / max(np.abs(vertices).max(), 1e-12)))

    def match(path):
        vertices = np.asarray(path.vertices, dtype=float)
        scale = max(np.abs(vertices).max(), 1e-12)
        for symbol, shape in known:
            if shape.shape == vertices.shape and np.allclose(shape, vertices / scale, atol=1e-6):
                return symbol
        return "circle"

    shapes = [match(p) for p in paths]
    return [shapes[i % len(shapes)] for i in range(n)]


def colour_scale(mappable, low, high, steps=65):
    """plotly's colour scale for a matplotlib colour map and norm: the colours matplotlib gives at evenly spaced
    values from low to high (so a two-sided middle, a log norm and steps are kept as drawn)."""
    if not (np.isfinite(low) and np.isfinite(high)) or high <= low:
        colour = css(_hex(mappable.to_rgba(np.array([low]))[0])) if np.isfinite(low) else "rgba(0,0,0,0)"
        return [[0, colour], [1, colour]]
    bands = _bands(mappable)
    if bands is not None:  # a filled contour map or a colour scale cut into steps: one colour for each band
        edges, colours = bands
        scale = []
        for i, colour in enumerate(colours):
            start = 0.0 if i == 0 else min(max((edges[i] - low) / (high - low), 0.0), 1.0)
            end = 1.0 if i == len(colours) - 1 else min(max((edges[i + 1] - low) / (high - low), 0.0), 1.0)
            scale += [[start, css(_hex(colour))], [end, css(_hex(colour))]]
        return scale
    values = np.linspace(low, high, steps)
    colours = mappable.to_rgba(values)
    return [[float(i / (steps - 1)), css(_hex(c))] for i, c in enumerate(colours)]


def _bands(mappable):
    """(edges, the colour of each band) of a filled contour set or a stepped colour scale (BoundaryNorm), as
    matplotlib colours them; None for a smooth colour scale."""
    from matplotlib.colors import BoundaryNorm

    if getattr(mappable, "filled", False) and getattr(mappable, "levels", None) is not None:
        edges = np.asarray(mappable.levels, dtype=float)
        return edges, mappable.to_rgba(np.asarray(mappable.layers, dtype=float))
    norm = getattr(mappable, "norm", None)
    if isinstance(norm, BoundaryNorm):
        edges = np.asarray(norm.boundaries, dtype=float)
        return edges, mappable.to_rgba((edges[:-1] + edges[1:]) / 2)
    return None


# ---------------------------------------------------------------- show_when_pointing: the columns of each row
def _key(value):
    import pandas as pd

    if value is None:
        return None
    if hasattr(value, "year"):
        try:
            return pd.Timestamp(value).tz_localize(None)
        except (TypeError, ValueError):
            return pd.Timestamp(value)
    if isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool):
        v = float(value)
        return None if math.isnan(v) else float(f"{v:.10g}")
    return str(value)


SUMMARY_NOTE = ("Note: show_when_pointing() shows your columns only on marks that are single rows of the table (dots, "
                "and lines with one row at each point). {words} {verb} summaries of several rows, so pointing at "
                "them shows what they are, never one row's columns.")
RAW_LINE_JOINS = ("straight lines", "steps")  # a curve through the points (joined_by="smooth curve") makes new points


def raw_step(chart, step) -> bool:
    """Whether every mark a step draws is one row of the table, decided from the step as written: dots drawn from
    the rows themselves, and lines that have one row at each point (no average, total ... of several rows, no
    curve through the points). Bars, error bars, bands, fitted lines, densities, histograms and hexagons are
    summaries."""
    import pandas as pd

    kw = step.kwargs
    if step.name == "dots":
        return getattr(step.func, "__name__", "") == "_draw_dots"  # not draw_dots(show=...): averages
    if step.name != "lines" or kw.get("joined_by", "straight lines") not in RAW_LINE_JOINS or kw.get("error"):
        return False
    data = chart.__dict__.get("_data")
    columns = [kw.get(k) for k in ("x", "colour", "dashed")]
    columns = [c for c in columns if isinstance(c, str) and data is not None and c in data.columns]
    y = kw.get("y")
    if data is None or not isinstance(y, str) or y not in data.columns or not columns:
        return False
    rows = data.dropna(subset=[y] + columns)
    return bool(len(rows)) and not rows.duplicated(subset=columns).any()  # one row at each point of each line


class _Pointing:
    """chart.show_when_pointing("name", "marks"). Only a mark that is one row of the table shows that row's named
    columns: the step that drew the mark (each drawn matplotlib artist is tagged with its step while the chart is
    drawn) must draw single rows (raw_step); the row is then found among that step's rows by its x, y (and group).
    A summary (an average, a bar, a band, a fit ...) is never matched to a row by its value: it says what it is."""

    def __init__(self, chart):
        settings = chart.__dict__.get("_settings") or {}
        wanted = settings.get("pointing") or {}
        self.chart = chart
        self.columns = list(wanted.get("columns") or [])
        self.all_lines = bool(wanted.get("all_lines"))
        self.data = chart.__dict__.get("_data")
        self.summaries: list = []

    def texts(self, a, rows, texts):
        if not self.columns or self.data is None or not rows:
            return texts
        artist = rows[0].get("_artist")
        step = getattr(artist, "simplydata_step", None)
        if step is None or not raw_step(self.chart, step):
            word = self.chart._public_name(step.name) if step is not None else "these marks"
            if word not in self.summaries:
                self.summaries.append(word)
            show = (step.kwargs.get("show") if step is not None else None) or ""
            what = (f"the {show} of several rows" if isinstance(show, str) and show and show != "count"
                    else "a summary of several rows")
            return [f"{t}<br>({what})" if t else f"({what})" for t in texts]
        kw = step.kwargs
        x, y, group = kw.get("x"), kw.get("y"), kw.get("colour")
        if not (isinstance(x, str) and isinstance(y, str) and x in self.data.columns and y in self.data.columns):
            return texts
        grouped = isinstance(group, str) and group in self.data.columns
        names = _legend_names(a.ax) if grouped else {}
        table: dict = {}
        for i, (xv, yv, gv) in enumerate(zip(self.data[x], self.data[y],
                                             self.data[group] if grouped else [None] * len(self.data))):
            table.setdefault((_key(xv), _key(yv), _key(gv) if grouped else None), []).append(i)
        out = []
        for text, r in zip(texts, rows):
            g = _key(names.get(r["colour"])) if grouped else None
            positions = table.get((_key(_shown(r["x"], a.read_x, a.x_kind)), _key(_shown(r["y"], a.read_y, a.y_kind)),
                                   g))
            if positions:
                i = positions.pop(0) if len(positions) > 1 else positions[0]
                row = self.data.iloc[i]
                extra = "<br>".join(f"{c}: {html_text.escape(_written(row[c]))}" for c in self.columns)
                text = f"{text}<br>{extra}" if text else extra
            out.append(text)
        return out

    def note(self):
        from ._core import chart_note

        if self.summaries:
            line = SUMMARY_NOTE.format(words=" and ".join(f"{w}()" for w in self.summaries),
                                       verb="shows" if len(self.summaries) == 1 else "show")
            chart_note(("pointing summaries", line), lambda _n, line=line: line)


def _shown(value, read, kind):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return read(value) if kind in ("date", "group") else value


def _written(value) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    if hasattr(value, "year") and hasattr(value, "hour") and not (value.hour or value.minute or value.second):
        return str(value.date())
    return str(value)


# ---------------------------------------------------------------- the whole web page
def web_figure(chart, see_through=False):
    """The plotly figure of a chart (or a page of charts), from what matplotlib drew."""
    from . import _style
    from ._cite import _note
    from ._core import chart_notes

    go = need_plotly()
    settings = chart._settings
    if settings.get("font_name"):
        _note_once("font", FONT_NOTE)
    with chart_notes():
        if settings.get("animate") and hasattr(chart, "_frames"):
            figure = _animated(chart, go, see_through)
        else:
            fig = chart._render()
            with _style.context(settings):
                refuse_what_plotly_cannot_draw(chart, fig)
                traces, layout = Translator(chart, fig, see_through).translate()
            figure = _figure(go, traces, layout)
    _note([("python", "plotly")])  # sdata.show_packages_used() lists plotly when a web page was made
    return figure


def _figure(go, traces, layout, frames=None):
    figure = go.Figure(layout=layout, frames=frames or [])
    for trace in traces:
        figure.add_trace(_trace(go, trace))
    return figure


def _trace(go, trace):
    trace = dict(trace)
    kind = trace.pop("type")
    makers = {"scatter": go.Scatter, "bar": go.Bar, "heatmap": go.Heatmap, "pie": go.Pie,
              "scatterpolar": go.Scatterpolar, "barpolar": go.Barpolar, "scatter3d": go.Scatter3d,
              "surface": go.Surface, "mesh3d": go.Mesh3d}
    return makers[kind](**trace)


def _animated(chart, go, see_through):
    """animate(over=...): every frame drawn by matplotlib as for a .gif, each copied into a plotly frame, with a
    play button and a slider."""
    from matplotlib.figure import Figure

    from . import _style

    s = chart._settings
    over = s["animate"]["over"]
    seconds = s["animate"]["seconds"]
    frames = []
    with _style.context(s):
        chart._left_out_rows()
        limits = chart._fixed_limits()
        for value, table in chart._frames():
            fig = Figure(figsize=(s["width"], s["height"]), layout="constrained")
            chart._draw_frame(fig, value, table, limits)
            refuse_what_plotly_cannot_draw(chart, fig)
            traces, layout = Translator(chart, fig, see_through).translate()
            frames.append((value, traces, layout))
    most = max(len(t) for _, t, _ in frames)

    def padded(traces):
        return [_trace(go, t) for t in traces] + [go.Scatter(x=[None], y=[None], showlegend=False,
                                                            hoverinfo="skip") for _ in range(most - len(traces))]

    first_value, first_traces, layout = frames[0]
    plotly_frames = [go.Frame(name=str(value), data=padded(traces),
                              layout=dict(annotations=frame_layout["annotations"],
                                          title=frame_layout.get("title")))
                     for value, traces, frame_layout in frames]
    milliseconds = int(seconds * 1000)
    layout = dict(layout)
    layout["margin"] = dict(layout["margin"], b=round(0.25 * layout["height"]))
    layout["height"] = round(layout["height"] * 1.25)
    # the Play and Pause buttons on the left, the slider beside them (not under them), its last value inside
    layout["updatemenus"] = [dict(type="buttons", direction="left", x=0, y=0, xanchor="left", yanchor="top",
                                  pad=dict(t=45, l=4), showactive=False, buttons=[
                                      dict(label="Play", method="animate",
                                           args=[None, dict(frame=dict(duration=milliseconds, redraw=True),
                                                            fromcurrent=True, transition=dict(duration=0))]),
                                      dict(label="Pause", method="animate",
                                           args=[[None], dict(mode="immediate", frame=dict(duration=0),
                                                              transition=dict(duration=0))])])]
    layout["sliders"] = [dict(active=0, x=0.22, len=0.74, y=0, yanchor="top", pad=dict(t=30, r=10, l=0),
                              currentvalue=dict(prefix=f"{over}: "),
                              steps=[dict(label=str(value), method="animate",
                                          args=[[str(value)], dict(mode="immediate", frame=dict(duration=0,
                                                                                                redraw=True))])
                                     for value, _, _ in frames])]
    figure = go.Figure(data=padded(first_traces), layout=layout, frames=plotly_frames)
    del first_value
    return figure


def page_html(chart, see_through=False, full_html=True) -> str:
    """The web page: the plotly figure with plotly.js written inside it (no internet needed to open it, nothing
    fetched), a title, and the chart's description in words for screen readers."""
    figure = web_figure(chart, see_through)
    # The page fits the window: the chart keeps its shape (width to height) and is never wider than drawn, so a page
    # of charts needs no sideways scrolling; plotly redraws it at the size of its box (responsive).
    width, height = figure.layout.width, figure.layout.height
    figure.update_layout(width=None, height=None, autosize=True)
    page = figure.to_html(include_plotlyjs=True, include_mathjax=False, full_html=full_html,
                          config=dict(WEB_CONFIG, responsive=True), validate=True, default_width="100%",
                          default_height="100%")
    # plotly's outer box is the page's first <div>: '<div style="height:100%; width:100%;">' in newer plotly, a bare
    # '<div>' in plotly 6.0 (the oldest supported); either becomes the fitted box
    fitted = (f'<div class="simplydata-chart" style="width:100%; max-width:{width}px; '
              f'aspect-ratio:{width} / {height}; margin:0 auto;">')
    page = re.sub(r'<div(?: style="height:100%; width:100%;")?>', lambda _m: fitted, page, count=1)
    description = _description(chart)
    title = _title(figure)
    if full_html:
        head = f"<title>{html_text.escape(title)}</title>"
        page = page.replace("<head>", f"<head>{head}", 1)
    if description:
        hidden = ('<div style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">'
                  + "<br>".join(html_text.escape(line) for line in description.splitlines()) + "</div>")
        page = page.replace("<body>", f"<body>{hidden}", 1) if full_html else hidden + page
    return page


def _title(figure) -> str:
    title = figure.layout.title.text if figure.layout.title and figure.layout.title.text else ""
    if not title:
        for note in figure.layout.annotations or ():
            if (note.name or "").startswith("title|"):
                title = note.text
                break
    return html_text.unescape(title) or "simplydata chart"


def _description(chart) -> str:
    """say_what_it_shows(), as the page's text for screen readers (nothing printed)."""
    words = getattr(chart, "say_what_it_shows", None)
    if words is None:
        return ""
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return words()
    except SimplydataError:
        return ""


def save_page(chart, path, see_through=False):
    text = page_html(chart, see_through)
    path.write_text(text, encoding="utf-8")
    _note_once("saved", SAVED_NOTE)
    return chart


# ---------------------------------------------------------------- show_in_web_page()
WEB_PAGE_FOLDER = {"folder": None}  # None: the computer's folder for temporary files (tests set their own)


def in_notebook() -> bool:
    try:
        from IPython import get_ipython
    except ImportError:
        return False
    shell = get_ipython()
    return shell is not None and type(shell).__name__ == "ZMQInteractiveShell"


def open_file_in_browser(address: str):
    """Open a web page that is a file on this computer. Only file addresses are opened: nothing is fetched and no
    server is started."""
    import webbrowser

    if not address.startswith("file:"):
        raise SimplydataError("simplydata only opens web pages that are files on this computer.")
    webbrowser.open(address)


def show_page(chart):
    import tempfile
    from pathlib import Path

    if in_notebook():
        from IPython.display import HTML, display

        display(HTML(page_html(chart, full_html=False)))
        _note_once("saved", SAVED_NOTE)  # the notebook keeps the page, with the numbers, in its file
        return chart
    text = page_html(chart)
    handle, name = tempfile.mkstemp(prefix="simplydata_chart_", suffix=".html", dir=WEB_PAGE_FOLDER["folder"])
    with open(handle, "w", encoding="utf-8") as file:
        file.write(text)
    path = Path(name)
    print(f"The chart opens in your web browser from a file on this computer, in the folder for temporary files:\n"
          f"    {path}\n"
          "That file holds the numbers drawn and the columns shown when pointing, as the table does; share it as "
          "you would share the table, and delete it when you no longer need it.")
    open_file_in_browser(path.resolve().as_uri())
    return chart
