"""A panel letter on one chart, and the legend inside the chart (charts phase, batch 1, approved by Manish 2026-11-25).

    chart.write_letter("B")                  B in bold at the top left, as with_letters=True writes it on pages
    chart.put_legend_inside("top left")      the legend in a corner of the plot (matplotlib's loc="upper left")
"""

from __future__ import annotations

import matplotlib

from .._errors import SimplydataError, friendly
from .._typing import _Same
from .look import _collect_entries

# Places inside the plot, in simplydata's words, and matplotlib's name for each (Legend loc=)
INSIDE_PLACES = {"top left": "upper left", "top right": "upper right", "bottom left": "lower left",
                 "bottom right": "lower right", "top": "upper center", "bottom": "lower center",
                 "left": "center left", "right": "center right", "middle": "center",
                 "best": "best"}
LETTER_PLACES = ("top left", "top right")


def _legend_inside(ctx, where):
    import seaborn as sns

    loc = INSIDE_PLACES[where]
    if len(ctx.axes) > 1:  # several panels: each keeps its own legend, moved inside it
        for ax in ctx.axes:
            if ax.get_legend() is not None:
                sns.move_legend(ax, loc)
        return
    handles, labels, group_title = _collect_entries(ctx)  # also the entries of a second y-axis
    if ctx.settings.get("legend_title") is not None:  # chart.label_legend("Class")
        group_title = ctx.settings["legend_title"]
    if handles:
        ctx.ax.legend(handles, labels, loc=loc, title=group_title or None)


def _letter_size():
    return matplotlib.rcParams["axes.titlesize"] * 1.2


def _write_letter(ctx, text, where):
    from .layout import _put_letter

    side = "left" if where == "top left" else "right"
    if len(ctx.axes) == 1:
        title = ctx.ax.set_title(text, loc=side, fontweight="bold", fontsize=_letter_size())
        title.simplydata_part = "panel letter"
        return
    if side == "left":  # a chart in several panels: on its own line above them, as pages do
        _put_letter(ctx.fig, ctx.axes, text)
        return
    letter = ctx.fig.suptitle(text, x=0.99, ha="right", fontweight="bold", fontsize=_letter_size())
    letter.simplydata_part = "panel letter"


class LetterLegendWords:
    @friendly
    def write_letter(self: _Same, text, where="top left") -> _Same:
        """A bold letter at the top left of the chart, as figures in papers have. chart.write_letter("B")

        For a figure made of separate pictures. On a page of charts, with_letters=True writes A, B, C ... by
        itself. where="top right" puts it at the other corner.
        """
        if text is None or isinstance(text, bool) or not str(text).strip():
            raise SimplydataError('.write_letter() needs a letter, for example chart.write_letter("B").')
        self._check_choice("write_letter", "where", where, LETTER_PLACES)
        return self._replace("write_letter", "text", _write_letter, scope="figure", text=str(text).strip(),
                             where=where)

    @friendly
    def put_legend_inside(self: _Same, where="best") -> _Same:
        """The legend inside the chart, in a corner. chart.put_legend_inside("top left")
        (with chart.draw_lines(x="month", y="temperature", colour="city") on sdata.get_example("weather"))

        where= is "top left", "top right", "bottom left", "bottom right", "top", "bottom", "left", "right",
        "middle", or "best" (normal): the place where it covers the fewest lines, dots and bars.
        """
        self._check_choice("put_legend_inside", "where", where, list(INSIDE_PLACES))
        return self._legend_step_inside(where)

    def _legend_step_inside(self, where):
        # the same step as put_legend_at_top ...: the last of them wins, and show_legend() takes it away
        return self._replace("legend", "finish", _legend_inside, scope="figure", where=where)
