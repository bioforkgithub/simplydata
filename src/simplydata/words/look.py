"""Colours, legends and the overall look."""

from __future__ import annotations

from .._typing import _Same

from matplotlib import colors as mcolors
from matplotlib.patches import Rectangle

from .._data import is_listlike
from .._errors import SimplydataError, friendly, suggest
from .._style import STYLES
from .._units import PER_INCH, SCREEN_RESOLUTION, check_number, check_unit
from ._colour_scale import check_options, check_used, resolve_map
from .charts import set_order

# Colour names we suggest from when a name is misspelt ("bleu" -> "blue").
_COLOUR_NAMES = sorted(mcolors.CSS4_COLORS)


def check_colour(value, step: str):
    """Return `value` if matplotlib can use it as a colour, else raise a friendly error."""
    if not isinstance(value, bool) and mcolors.is_color_like(value):
        return value
    lines = [f".{step}() does not know the colour {value!r}."]
    if isinstance(value, str):
        guess = suggest(value.lower().replace(" ", ""), _COLOUR_NAMES, n=1)
        if guess:
            lines.append(f'Did you mean "{guess[0]}"?')
    lines.append('Use a colour name such as "blue", "orange" or "darkgreen", or a code such as "#0072B2".')
    raise SimplydataError("\n".join(lines))


# ---------------------------------------------------------------- legends
def _twins(ctx) -> list:
    """Extra y-axes (chart.add_second_y) that may carry legend entries."""
    found = []
    stored = ctx.store.get("second_y")
    if isinstance(stored, dict):
        stored = list(stored.values())
    for item in stored if isinstance(stored, (list, tuple)) else [stored]:
        if hasattr(item, "get_legend_handles_labels"):
            found.append(item)
    for ax in ctx.axes:  # twins of every panel, not just the last one drawn
        siblings = getattr(ax, "_twinned_axes", None)
        if siblings is not None:
            found.extend(siblings.get_siblings(ax))
    unique = []
    for ax in found:
        if ax not in unique and ax not in ctx.axes:
            unique.append(ax)
    return unique


def _blank():
    return Rectangle((0, 0), 1, 1, fill=False, edgecolor="none", visible=False)


def _collect_entries(ctx):
    """Take every legend entry from all panels (and twin axes) and remove their legends."""
    handles, labels, group_title = [], [], ""
    for ax in list(ctx.axes) + _twins(ctx):
        found_h, found_l = [], []
        leg = ax.get_legend()
        if leg is not None:
            found_h = list(leg.legend_handles)
            found_l = [t.get_text() for t in leg.get_texts()]
            group_title = group_title or leg.get_title().get_text()
            leg.remove()
        more_h, more_l = ax.get_legend_handles_labels()
        for h, label in zip(found_h + more_h, found_l + more_l):
            if not label or label.startswith("_") or label in labels:
                continue
            handles.append(h if h is not None else _blank())
            labels.append(label)
    return handles, labels, group_title


def _take_text(artist):
    """Hide a figure title/label so the legend can show it instead. Returns (text, font)."""
    font = dict(size=artist.get_fontsize(), weight=artist.get_fontweight())
    artist.set_visible(False)
    artist.set_in_layout(False)
    return artist.get_text(), font


def _visible_fig_text(fig, attr):
    artist = getattr(fig, attr, None)
    if artist is not None and artist.get_visible() and artist.get_text():
        return artist
    return None


_LEGEND_PLACES = {
    "top": "outside upper center",
    "bottom": "outside lower center",
    "left": "outside center left",
    "right": "outside center right",
}


def _legend(ctx, where):
    handles, labels, group_title = _collect_entries(ctx)
    if ctx.settings.get("legend_title") is not None:  # chart.label_legend("Class")
        group_title = ctx.settings["legend_title"]
    if where == "hide":
        ctx.store["legend_hidden"] = True
    if where == "hide" or not handles:
        return
    fig = ctx.fig

    # Matplotlib puts a figure legend and a figure title/label in the same margin, on top
    # of each other. So the text that would share the legend's side becomes its heading.
    heading = None
    if where == "top":
        sup = _visible_fig_text(fig, "_suptitle")
        if sup is not None:
            heading = _take_text(sup)
        elif len(ctx.axes) == 1 and ctx.ax.get_title():  # keep the title above the legend
            title = ctx.ax.title
            heading = (title.get_text(), dict(size=title.get_fontsize(), weight=title.get_fontweight()))
            ctx.ax.set_title("")
    elif where == "bottom":
        sup = _visible_fig_text(fig, "_supxlabel")
        if sup is not None:
            heading = _take_text(sup)
    elif where == "left":
        sup = _visible_fig_text(fig, "_supylabel")
        if sup is not None:  # give the y name back to the left-hand panels instead
            text, _ = _take_text(sup)
            for ax in ctx.axes:
                spec = ax.get_subplotspec()
                if spec is None or spec.is_first_col():
                    ax.set_ylabel(text)

    kw = dict(loc=_LEGEND_PLACES[where])
    if heading is not None:
        kw["title"], kw["title_fontproperties"] = heading
        if group_title:  # the group name moves to the front of the row
            handles = [_blank()] + handles
            labels = [f"{group_title}:"] + labels
    elif group_title:
        kw["title"] = group_title
    if where in ("top", "bottom"):
        kw["ncols"] = min(len(handles), 6)  # one row; wraps only when there are many entries
    fig.legend(handles, labels, **kw)


def _label_legend(ctx, text):
    """Put the name above the legend of every panel (and of a second y-axis)."""
    found = False
    for ax in list(ctx.axes) + _twins(ctx):
        leg = ax.get_legend()
        if leg is not None:
            leg.set_title(text or None)
            found = True
    if not found and not ctx.fig.legends and not ctx.store.get("legend_hidden"):
        raise SimplydataError(
            ".label_legend() names the legend, but this chart has no legend.\n"
            'A legend appears when colour= makes groups, for example chart.draw_dots(x="hours", y="marks", colour="class").'
        )


def _label_colour_bar(ctx, text):
    bar = ctx.store.get("colour_bar")
    if bar is None:
        raise SimplydataError(
            ".label_colour_bar() needs a chart with a colour bar,\n"
            'for example chart.draw_heatmap() or chart.draw_contour(x="east", y="north", z="height").'
        )
    for one in bar if isinstance(bar, (list, tuple)) else [bar]:
        one.set_label(text)


class LookWords:
    @friendly
    def use_style(self: _Same, name) -> _Same:
        """The overall look. chart.use_style("school")

        "paper" (default), "school", "presentation" or "dark".
        """
        self._check_choice("use_style", "name", name, list(STYLES))
        return self._set(style=name)

    @friendly
    def set_size(self: _Same, width=8, height=6, unit="inches") -> _Same:
        """The size of the chart. chart.set_size(width=17, height=12, unit="cm")

        unit= is "inches" (normal), "cm", "mm" or "pixels". A saved file is exactly this size.
        In pixels, the saved picture has exactly that many pixels at any resolution=.
        """
        unit = check_unit(unit, "set_size")
        width = check_number(width, "width", "set_size")
        height = check_number(height, "height", "set_size")
        if unit == "pixels":
            # kept in pixels: the inches depend on the resolution the chart is saved at
            pixels = (width, height)
            width, height = width / SCREEN_RESOLUTION, height / SCREEN_RESOLUTION
        else:
            pixels = None
            width, height = width / PER_INCH[unit], height / PER_INCH[unit]
        # size_set tells draw_one_chart_for_each_group_in() and pages not to choose a size themselves
        return self._set(width=width, height=height, pixels=pixels, size_set=True)

    # ------------------------------------------------------------ colours
    @friendly
    def use_colour(self: _Same, name) -> _Same:
        """One colour for the whole chart. chart.use_colour("blue") or chart.use_colour("#0072B2")"""
        return self._set(colour=check_colour(name, "use_colour"))

    use_color = use_colour  # American spelling, same word

    @friendly
    def use_colours(self: _Same, *names) -> _Same:
        """Your own colours for the groups, in order. chart.use_colours("blue", "orange", "green")"""
        if len(names) == 1 and is_listlike(names[0]):
            names = tuple(names[0])
        if not names:
            raise SimplydataError('.use_colours() needs at least one colour, for example chart.use_colours("blue", "orange").')
        return self._set(colours=[check_colour(n, "use_colours") for n in names])

    use_colors = use_colours  # American spelling, same word

    @friendly
    def use_colour_scale(self: _Same, *names, middle=None, log=False, steps=None, between=None) -> _Same:
        """The colours for numbers on a heatmap, contour map, surface or dots coloured by a number column.
        chart.use_colour_scale("magma") (with chart.draw_heatmap(x="month", y="city", value="rain") on sdata.get_example("weather"))

        A name: "viridis" (normal), "cividis", "magma", "blues", "greens" ..., "blue to red"
        or "purple to orange" for numbers on both sides of a middle; these are all safe
        for colour-blind readers. Any matplotlib colour map name works too ("Blues", "plasma",
        "rocket"), and two or more colours make your own: chart.use_colour_scale("white", "navy").
        middle=0 puts the middle colour of a two-sided scale at 0 (or middle=1 for ratios);
        the scale goes equally far on both sides, so a step of 1 is the same change of colour.
        log=True spreads the colours on a log scale (1, 10, 100 ... evenly), for counts
        that span many sizes. steps=5 cuts the scale into 5 colours, or steps=[0, 5, 10, 20]
        sets where each colour starts. between=[0, 30] fixes the ends of the scale, so
        several charts can share it; values beyond them get the end colour (the colour bar
        shows an arrow).
        """
        cmap, shown = resolve_map(names)
        middle, log, steps, between = check_options(middle, log, steps, between)
        self._set(colour_scale=dict(map=cmap, name=shown, middle=middle, log=log, steps=steps, between=between))
        return self._replace("colour_scale_check", "finish", check_used)

    use_color_scale = use_colour_scale  # American spelling, same word

    # ------------------------------------------------------------ grid
    @friendly
    def show_grid(self: _Same) -> _Same:
        """Grid lines across the chart in both directions. chart.show_grid()"""
        return self._set(grid=True)

    @friendly
    def hide_grid(self: _Same) -> _Same:
        """No grid lines. chart.hide_grid()"""
        return self._set(grid=False)

    # ------------------------------------------------------------ legend
    def _legend_step(self, where):
        return self._replace("legend", "finish", _legend, scope="figure", where=where)

    @friendly
    def put_legend_at_top(self: _Same) -> _Same:
        """The legend above the chart, in one row. chart.put_legend_at_top()"""
        return self._legend_step("top")

    put_legend_on_top = put_legend_at_top  # the other spelling, same word

    @friendly
    def put_legend_at_bottom(self: _Same) -> _Same:
        """The legend below the chart, in one row under the x-axis name. chart.put_legend_at_bottom()"""
        return self._legend_step("bottom")

    put_legend_on_bottom = put_legend_at_bottom  # the other spelling, same word

    @friendly
    def put_legend_on_left(self: _Same) -> _Same:
        """The legend to the left of the chart. chart.put_legend_on_left()"""
        return self._legend_step("left")

    put_legend_at_left = put_legend_on_left  # the other spelling, same word

    @friendly
    def put_legend_on_right(self: _Same) -> _Same:
        """The legend to the right of the chart, outside the plot. chart.put_legend_on_right()"""
        return self._legend_step("right")

    put_legend_at_right = put_legend_on_right  # the other spelling, same word

    @friendly
    def hide_legend(self: _Same) -> _Same:
        """No legend. chart.hide_legend()"""
        return self._legend_step("hide")

    @friendly
    def label_legend(self: _Same, text) -> _Same:
        """The name above the legend. chart.label_legend("Class")
        (with chart.draw_dots(x="hours", y="marks", colour="class") on sdata.get_example("marks"))

        Without it the legend is named after the colour= column. label_legend("") leaves
        the name out.
        """
        if text is None or isinstance(text, bool):
            raise SimplydataError('.label_legend() needs some words, for example chart.label_legend("Class").')
        text = str(text)
        self._set(legend_title=text)
        return self._replace("label_legend", "finish", _label_legend, scope="figure", text=text)

    @friendly
    def order_legend(self, *names):
        """Put the colour groups in your order: in the legend, the colours and side by side.
        chart.order_legend("Science", "Maths", "English")
        (with chart.draw_bars(x="class", y="marks", colour="subject") on sdata.get_example("marks"))

        Groups you leave out come after the ones you name. The slices of a pie follow it too.
        The first group gets the first colour.
        """
        return set_order(self, "colour", names, None)

    @friendly
    def show_legend(self: _Same) -> _Same:
        """The legend in its usual place, for example after hide_legend(). chart.show_legend()

        A legend only appears when colour= (or shape=) makes groups.
        """
        self._steps = [s for s in self._steps if s.name != "legend"]
        self._cache = None
        return self

    # ------------------------------------------------------------ colour bar
    @friendly
    def label_colour_bar(self: _Same, text) -> _Same:
        """The name beside the colour bar of a heatmap or contour. chart.label_colour_bar("Height (m)")"""
        return self._replace("label_colour_bar", "text", _label_colour_bar, text=str(text))

    label_color_bar = label_colour_bar  # American spelling, same word
