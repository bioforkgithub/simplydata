"""Words and labels on a chart."""

from __future__ import annotations

from .._typing import _Same

from .._typing import _Same

import numbers

import matplotlib as mpl
import numpy as np
from matplotlib.colors import to_rgb
from matplotlib.text import Annotation

from .._core import PHASES, chart_note
from .._data import is_listlike
from .._errors import SimplydataError, column_error, friendly, suggest
from .axes import tick_position

FONT_KINDS = ("serif", "sans-serif", "monospace", "cursive", "fantasy")


def installed_font(name):
    """The installed font's own name for `name` (any capitals), or a friendly error with close names."""
    from matplotlib import font_manager

    if name.lower() in FONT_KINDS:
        return name.lower()
    fonts = sorted({f.name for f in font_manager.fontManager.ttflist})
    by_lower = {f.lower(): f for f in fonts}
    if name.lower() in by_lower:
        return by_lower[name.lower()]
    lower = name.lower()
    close = [f for f in fonts if lower in f.lower() or f.lower() in lower]
    close += [by_lower[g] for g in suggest(lower, list(by_lower), n=5, cutoff=0.5) if by_lower[g] not in close]
    lines = [f'.use_font() cannot find the font "{name}" on this computer.']
    if close:
        lines.append("Installed fonts with a similar name: " + ", ".join(f'"{f}"' for f in close[:8]))
    else:
        lines.append("Some installed fonts: " + ", ".join(f'"{f}"' for f in fonts[:8]))
    lines.append('Or use a kind of font: "serif", "sans-serif" or "monospace". '
                 "After installing a new font, restart Python.")
    raise SimplydataError("\n".join(lines))


ARROW_OFFSET = 40  # points between a note and the place its arrow points at


def _title_top(ctx, text):
    if len(ctx.axes) == 1:
        ctx.ax.set_title(text)
    else:
        ctx.fig.suptitle(text, fontweight="bold")


def _label_x(ctx, text):
    if len(ctx.axes) == 1:
        ctx.ax.set_xlabel(text)
    else:
        for ax in ctx.axes:
            ax.set_xlabel("")
        ctx.fig.supxlabel(text, fontweight="bold")


def _label_y(ctx, text):
    if len(ctx.axes) == 1:
        ctx.ax.set_ylabel(text)
    else:
        for ax in ctx.axes:
            ax.set_ylabel("")
        ctx.fig.supylabel(text, fontweight="bold")


# ---------------------------------------------------------------- caption
def _caption_bottom(ctx, text):
    style = dict(fontsize=0.8 * mpl.rcParams["font.size"], fontweight="normal", alpha=0.8)
    if len(ctx.axes) == 1:
        # Hang the caption under the x-axis label. It belongs to the axes, so constrained
        # layout makes room for it, and it moves down when labels are turned or get bigger.
        caption = ctx.ax.annotate(text, xy=(0.5, 0), xycoords=ctx.ax.xaxis.label, xytext=(0, -4),
                                  textcoords="offset points", ha="center", va="top",
                                  annotation_clip=False, **style)
        caption.simplydata_part = "caption"
        return
    # Several panels: the figure's bottom line (supxlabel) is the only text that constrained
    # layout keeps below every panel.
    shared = ctx.fig.get_supxlabel()
    if not shared:
        ctx.fig.supxlabel(text, **style).simplydata_part = "caption"
        return
    # Both a shared x label and a caption: the label gets an empty second line and the
    # caption sits in it, so layout has made room for both.
    label = ctx.fig.supxlabel(shared + "\n", fontweight="bold")
    caption = Annotation(text, xy=(0.5, 0), xycoords=label, ha="center", va="bottom", annotation_clip=False,
                         **style)
    caption.simplydata_part = "caption"
    ctx.fig.add_artist(caption)


# ---------------------------------------------------------------- note
# Fixed places for write_note(where=): (x, y) as parts of the plot area, and how the text is aligned there
NOTE_PLACES = {"top left": (0.02, 0.98, "left", "top"), "top right": (0.98, 0.98, "right", "top"),
               "bottom left": (0.02, 0.02, "left", "bottom"), "bottom right": (0.98, 0.02, "right", "bottom"),
               "top": (0.5, 0.98, "center", "top"), "bottom": (0.5, 0.02, "center", "bottom"),
               "left": (0.02, 0.5, "left", "center"), "right": (0.98, 0.5, "right", "center"),
               "middle": (0.5, 0.5, "center", "center")}


def _note(ctx, text, x, y, arrow, where=None, box=False, curved=False):
    ax = ctx.ax
    # a soft background in the chart's own colour keeps the words readable over lines and bars
    back = dict(boxstyle="round,pad=0.2", fc=mpl.rcParams["axes.facecolor"], ec="none", alpha=0.85)
    if box:  # with_box=True: a frame round the note
        back = dict(boxstyle="round,pad=0.3", fc=mpl.rcParams["axes.facecolor"], ec=mpl.rcParams["text.color"],
                    lw=0.8)
    if where is not None:  # a fixed place in the plot area, whatever the data (matplotlib's transAxes)
        fx, fy, ha, va = NOTE_PLACES[where]
        note = ax.text(fx, fy, text, transform=ax.transAxes, ha=ha, va=va, bbox=back, zorder=5)
        note.simplydata_part, note.simplydata_where = "note", where
        return
    px, py = tick_position(ax, "x", x), tick_position(ax, "y", y)
    if not arrow:
        note = ax.annotate(text, xy=(px, py), xytext=(0, 4), textcoords="offset points",
                           ha="center", va="bottom", bbox=back)
        note.simplydata_part = "note"
        return
    # Put the text on the side that points into the chart, so it stays inside.
    data = (ax.xaxis.convert_units(px), ax.yaxis.convert_units(py))
    fx, fy = ax.transAxes.inverted().transform(ax.transData.transform(data))
    dx = -ARROW_OFFSET if fx > 0.6 else ARROW_OFFSET
    dy = -ARROW_OFFSET if fy > 0.6 else ARROW_OFFSET
    arrow_look = dict(arrowstyle="->", color=mpl.rcParams["text.color"], lw=1.2, shrinkA=2, shrinkB=3)
    if curved:  # with_curved_arrow=True: the arrow bends on its way (matplotlib's connectionstyle arc3)
        arrow_look["connectionstyle"] = "arc3,rad=0.3"
    note = ax.annotate(text, xy=(px, py), xytext=(dx, dy), textcoords="offset points",
                       ha="right" if dx < 0 else "left", va="top" if dy < 0 else "bottom", bbox=back,
                       arrowprops=arrow_look)
    note.simplydata_part = "note"


# ---------------------------------------------------------------- numbers on bars
def _text_colour_on(face):
    r, g, b = to_rgb(face)
    return "black" if 0.299 * r + 0.587 * g + 0.114 * b > 0.55 else "white"


def _numbers_on_bars(ctx, decimals):
    ax = ctx.ax
    bars = [c for c in ax.containers if isinstance(c, mpl.container.BarContainer)]
    if not bars:
        raise SimplydataError(
            ".write_numbers_on_bars() writes the value on each bar, but this chart has no bars.\n"
            'Add some first, for example chart.draw_bars(x="name", y="marks").'
        )
    sideways = getattr(bars[0], "orientation", "vertical") == "horizontal"

    def where(patch):  # middle of a bar along the category axis
        if sideways:
            return round(patch.get_y() + patch.get_height() / 2, 6)
        return round(patch.get_x() + patch.get_width() / 2, 6)

    # Stacked bars share their places; bars side by side (colour=) do not.
    places = [{where(p) for p in c.patches} for c in bars]
    stacked = len(bars) > 1 and all(p == places[0] for p in places[1:])

    def text(v):
        if v is None or np.isnan(v) or (stacked and v == 0):
            return ""
        return f"{v:,.{decimals}f}"

    if stacked:
        for c in bars:
            labels = [text(v) for v in np.ravel(c.datavalues)]
            colour = _text_colour_on(c.patches[0].get_facecolor())
            for t in ax.bar_label(c, labels=labels, label_type="center"):
                t.set_color(colour)
                t.simplydata_part = "number on bar"
        return

    # Error bars: write the number just past the end of the error bar, not across it.
    # (seaborn draws each error bar, caps included, as one line that stays within its bar)
    spans = []
    for line in ax.lines:
        xd, yd = np.asarray(line.get_xdata(), float), np.asarray(line.get_ydata(), float)
        along, value = (yd, xd) if sideways else (xd, yd)
        if len(along) and not np.all(np.isnan(along)):
            spans.append((np.nanmin(along), np.nanmax(along), value))

    def error_ends(patch):
        start = patch.get_y() if sideways else patch.get_x()
        size = patch.get_height() if sideways else patch.get_width()
        lo, hi = sorted((start, start + size))
        found = [val for a, b, val in spans if a >= lo - 1e-9 and b <= hi + 1e-9]
        return np.concatenate(found) if found else None

    for c in bars:
        plain = []
        for patch, v in zip(c.patches, np.ravel(c.datavalues)):
            lab = text(v)
            span = error_ends(patch)
            if span is None or not lab:
                plain.append(lab)
                continue
            plain.append("")
            up = v >= 0
            end = np.nanmax(span) if up else np.nanmin(span)
            if sideways:
                number = ax.annotate(lab, xy=(end, where(patch)), xytext=(3 if up else -3, 0),
                                     textcoords="offset points", ha="left" if up else "right", va="center")
            else:
                number = ax.annotate(lab, xy=(where(patch), end), xytext=(0, 3 if up else -3),
                                     textcoords="offset points", ha="center", va="bottom" if up else "top")
            number.simplydata_part = "number on bar"
        for t in ax.bar_label(c, labels=plain, padding=3):
            t.simplydata_part = "number on bar"
    # a little more room at the end of the bars, so the numbers stay inside the chart
    ax.margins(**({"x": 0.12} if sideways else {"y": 0.12}))
    ax.autoscale_view()


# ---------------------------------------------------------------- names on dots
# Each name goes into the first free place around its dot: right, left, above, below, then
# the four corners. A place is free when the name covers no other name and no other dot and
# stays inside the chart. A name with no free place is left out (and a line says how many).
_PLACES = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
NAME_GAP = 2.0  # points between a dot's edge and its name
NAME_ROOM = 2.0  # free points kept around each name, so names never touch


def _text_size(text, size):
    """Width and height of a text in points."""
    from matplotlib.font_manager import FontProperties
    from matplotlib.textpath import text_to_path

    width, height, _ = text_to_path.get_text_width_height_descent(
        text, FontProperties(size=size), ismath=False)
    return width, max(height, 0.75 * size) * 1.15


def _overlaps(box, boxes):
    x0, y0, x1, y1 = box
    return any(x0 < b[2] and b[0] < x1 and y0 < b[3] and b[1] < y1 for b in boxes)


def _dots_drawn(ax):
    """The dot collections on the chart: (centres in data units, radius in points)."""
    found = []
    for coll in ax.collections:
        offsets = np.asarray(coll.get_offsets(), float)
        if offsets.ndim != 2 or not len(offsets) or coll.get_offset_transform() != ax.transData:
            continue
        sizes = np.asarray(coll.get_sizes(), float)
        radius = float(np.sqrt(sizes.max()) / 2) if len(sizes) else 3.0
        found.append((offsets, radius))
    return found


def _names_on_dots(ctx, column, colour):
    last = ctx.last
    if not last or last.get("kind") != "dots":
        found = last.get("kind") if last else None
        raise SimplydataError(
            ".write_names_on_dots() writes a name next to each dot, but "
            + (f"the last chart type is {found}." if found else "your chart has no dots yet.")
            + '\nUse it after chart.draw_dots(x="hours", y="marks").'
        )
    ax, table = ctx.ax, last["table"]
    if is_listlike(column):
        names = list(column)
        if len(names) != len(table):
            raise SimplydataError(
                f".write_names_on_dots() got {len(names)} names, but the chart has {len(table)} rows of dots.\n"
                "Give one name for each dot.")
        order = last.get("row_order")
        if order is not None and len(order) == len(names):
            names = [names[i] for i in order]  # the rows were put in order (order_x, months)
    else:
        if column not in table.columns:
            raise column_error(column, table.columns)
        names = list(table[column])

    ax.get_xlim(), ax.get_ylim()  # let matplotlib finish its automatic ranges first
    scale = 72.0 / ctx.fig.dpi  # pixels -> points

    def to_points(xy):
        return ax.transData.transform(xy) * scale

    dots = _dots_drawn(ax)
    centres = np.column_stack([ax.xaxis.convert_units(table[last["x"]].to_numpy()),
                               ax.yaxis.convert_units(table[last["y"]].to_numpy())]).astype(float)
    radius = max([r for _, r in dots] + [mpl.rcParams["lines.markersize"] / 2])
    taken = [(px - r, py - r, px + r, py + r) for offsets, r in dots for px, py in to_points(offsets)]
    frame = ax.get_window_extent()
    inside = (frame.x0 * scale, frame.y0 * scale, frame.x1 * scale, frame.y1 * scale)
    size = 0.85 * mpl.rcParams["font.size"]
    gap = radius + NAME_GAP
    back = dict(boxstyle="round,pad=0.1", fc=mpl.rcParams["axes.facecolor"], ec="none", alpha=0.7)
    left_out = 0
    for (px, py), name in zip(centres, names):
        if name is None or (isinstance(name, float) and np.isnan(name)) or not np.isfinite([px, py]).all():
            continue
        text = str(name)
        w, h = _text_size(text, size)
        cx, cy = to_points(np.array([[px, py]]))[0]
        others = [b for b in taken if not (abs((b[0] + b[2]) / 2 - cx) < 1e-6 and abs((b[1] + b[3]) / 2 - cy) < 1e-6)]
        for dx, dy in _PLACES:
            ox, oy = dx * gap, dy * gap
            left = cx + ox - (0 if dx > 0 else w if dx < 0 else w / 2)
            bottom = cy + oy - (0 if dy > 0 else h if dy < 0 else h / 2)
            box = (left, bottom, left + w, bottom + h)
            if left < inside[0] or box[2] > inside[2] or bottom < inside[1] or box[3] > inside[3]:
                continue
            if _overlaps(box, others):
                continue
            name = ax.annotate(text, xy=(px, py), xytext=(ox, oy), textcoords="offset points",
                               ha="left" if dx > 0 else "right" if dx < 0 else "center",
                               va="bottom" if dy > 0 else "top" if dy < 0 else "center",
                               fontsize=size, color=colour or mpl.rcParams["text.color"], zorder=4, bbox=back)
            name.simplydata_part = "name on dot"
            taken.append((box[0] - NAME_ROOM, box[1] - NAME_ROOM, box[2] + NAME_ROOM, box[3] + NAME_ROOM))
            break
        else:
            left_out += 1
    ctx.store["names_left_out"] = ctx.store.get("names_left_out", 0) + left_out
    if left_out:  # one note for the whole picture, however many panels it has
        chart_note("names_on_dots", _names_left_out, left_out)


def _names_left_out(n):
    return (f"Note: {n} name{'s were' if n != 1 else ' was'} left out of this chart (write_names_on_dots), because "
            "there was no free space next to the dot. A bigger chart (chart.set_size(...)) makes room.")


# ---------------------------------------------------------------- the words
def _check_text(step, text, example):
    if text is None or (isinstance(text, str) and not text.strip()):
        raise SimplydataError(f".{step}() needs some words, for example {example}")
    return str(text)


class TextWords:
    @friendly
    def write_title_on_top(self: _Same, text) -> _Same:
        """A title above the chart. chart.write_title_on_top("My class marks")"""
        return self._replace("title_top", "text", _title_top, scope="figure", text=str(text))

    @friendly
    def label_x(self: _Same, text) -> _Same:
        """The name under the x-axis. chart.label_x("Student")"""
        return self._replace("label_x", "text", _label_x, scope="figure", text=str(text))

    @friendly
    def label_y(self: _Same, text) -> _Same:
        """The name beside the y-axis. chart.label_y("Marks")"""
        return self._replace("label_y", "text", _label_y, scope="figure", text=str(text))

    @friendly
    def write_caption_at_bottom(self: _Same, text) -> _Same:
        """A small line of text under the whole chart. chart.write_caption_at_bottom("Data from 2026")"""
        text = _check_text("write_caption_at_bottom", text, 'chart.write_caption_at_bottom("Data from 2026")')
        # "finish": runs after label_x, so it knows whether there is a shared x label to go under
        return self._replace("caption_bottom", "finish", _caption_bottom, scope="figure", text=text)

    @friendly(renamed={"arrow": "with_arrow"})
    def write_note(self: _Same, text, x=None, y=None, with_arrow=False, where=None, with_box=False,
                   with_curved_arrow=False) -> _Same:
        """A note on the chart at a place x, y. chart.write_note("Biggest", x=2024, y=49)

        with_arrow=True puts the note a little away, with an arrow pointing at x, y;
        with_curved_arrow=True makes the arrow bend.
        On bar charts x can be a name: chart.write_note("Best", x="Ben", y=90) on bars of names.
        where="top left" puts the note at a fixed place in the chart instead of at x, y: "top left",
        "top right", "bottom left", "bottom right", "top", "bottom", "left", "right" or "middle",
        for example chart.write_note("n = 30", where="top left").
        with_box=True draws a frame round the note.
        """
        text = _check_text("write_note", text, 'chart.write_note("Highest!", x=5, y=98)')
        for name, value in (("with_box", with_box), ("with_curved_arrow", with_curved_arrow)):
            if not isinstance(value, bool):
                raise SimplydataError(f".write_note() needs {name}=True or {name}=False, not {value!r}.")
        if where is not None:
            if x is not None or y is not None:
                raise SimplydataError('.write_note() takes a place by x= and y=, or by where=, not both. For example '
                                      'chart.write_note("n = 30", where="top left").')
            if with_arrow or with_curved_arrow:
                raise SimplydataError(".write_note() draws an arrow to a point x, y; a note at where= has no point "
                                      "to point at. Give x= and y= for an arrow.")
            self._check_choice("write_note", "where", where, list(NOTE_PLACES))
            return self._add("note", "extra", _note, text=text, x=None, y=None, arrow=False, where=where,
                             box=with_box)
        if x is None or y is None:
            raise SimplydataError(
                '.write_note() needs a place: x= and y=, for example chart.write_note("Highest!", x=5, y=98).')
        for name, v in (("x", x), ("y", y)):
            ok = isinstance(v, (numbers.Real, str)) or hasattr(v, "year")  # numbers, names, dates
            if isinstance(v, bool) or not ok:
                raise SimplydataError(
                    f'.write_note() needs a number for {name}=, not {v!r}. For example chart.write_note("Highest!", x=5, y=98).')
        if not isinstance(with_arrow, bool):
            raise SimplydataError(".write_note() needs with_arrow=True or with_arrow=False.")
        return self._add("note", "extra", _note, text=text, x=x, y=y, arrow=with_arrow or with_curved_arrow,
                         box=with_box, curved=with_curved_arrow)

    @friendly(renamed={"decimals": "with_decimals"})
    def write_numbers_on_bars(self: _Same, with_decimals=0) -> _Same:
        """Write the value of each bar on it. chart.write_numbers_on_bars() · with_decimals=1 shows 12.5"""
        if isinstance(with_decimals, bool) or not isinstance(with_decimals, numbers.Integral) or not 0 <= with_decimals <= 6:
            raise SimplydataError(
                ".write_numbers_on_bars() needs a whole number from 0 to 6 for with_decimals=, "
                "for example chart.write_numbers_on_bars(with_decimals=1).")
        return self._replace("numbers_on_bars", "extra", _numbers_on_bars, decimals=int(with_decimals))

    @friendly
    def write_names_on_dots(self: _Same, column, colour=None) -> _Same:
        """Write a name next to each dot. chart.write_names_on_dots("name")
        (with chart.draw_dots(x="hours", y="marks") on sdata.get_example("marks"))

        column is the column whose words are written (or a list: one name for each dot).
        Each name goes where it covers no other name or dot: right of its dot, else left,
        above, below or in a corner. A name with no free place is left out, and a line says
        how many; a bigger chart (chart.set_size(...)) makes room.
        colour="grey" writes the names in that colour.
        """
        if column is None or isinstance(column, bool) or not (isinstance(column, str) or is_listlike(column)):
            raise SimplydataError(
                f'.write_names_on_dots() needs a column of names, for example chart.write_names_on_dots("name"), not {column!r}.')
        if isinstance(column, str) and column not in self._data.columns:
            raise column_error(column, self._data.columns)
        if colour is not None and not (isinstance(colour, str) and mpl.colors.is_color_like(colour)):
            raise SimplydataError(
                f'.write_names_on_dots() does not know the colour {colour!r}. Use a name such as "grey" or "black".')
        draws = [s for s in self._steps if s.phase == PHASES["draw"] and s.name != "band"]
        if draws and draws[-1].name != "dots":
            raise SimplydataError(
                f".write_names_on_dots() writes a name next to each dot, but the last chart type is {draws[-1].name}.\n"
                'Use it after chart.draw_dots(x="hours", y="marks").')
        # "text" phase: after set_range_x/set_range_y, so free places are found on the final axes
        return self._replace("names_on_dots", "text", _names_on_dots, column=column, colour=colour)

    @friendly
    def use_font_size(self: _Same, size) -> _Same:
        """Make all the text bigger or smaller. chart.use_font_size(14) (normal is 12)"""
        if isinstance(size, bool) or not isinstance(size, numbers.Real) or size <= 0:
            raise SimplydataError(
                f".use_font_size() needs a number bigger than 0, not {size!r}. For example chart.use_font_size(14).")
        if not 4 <= size <= 60:
            raise SimplydataError(
                f"Font size {size} is very {'small' if size < 4 else 'big'}. "
                "Try a number between 8 and 24, for example chart.use_font_size(14).")
        return self._set(font_size=float(size))

    @friendly
    def use_font(self: _Same, name) -> _Same:
        """The font for all the text on the chart. chart.use_font("DejaVu Serif")

        Any font installed on your computer, such as "Arial" or "Times New Roman", or a
        kind of font: "serif", "sans-serif" (normal) or "monospace". If the font is not
        installed, the message lists the installed fonts with a similar name.
        """
        if not isinstance(name, str) or not name.strip():
            raise SimplydataError(
                f'.use_font() needs the name of a font, for example chart.use_font("Arial"), not {name!r}.')
        return self._set(font_name=installed_font(name.strip()))

