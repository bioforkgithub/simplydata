"""Reading a chart back, and taking a step back (charts phase, batch 1, approved by Manish 2026-11-25).

chart.get_text_drawn(), chart.get_scales_drawn() and chart.get_size() read what matplotlib drew, as
chart.get_numbers_drawn() does (simplydata._read_back, simplydata._numbers_drawn): nothing is worked out again.
chart.undo() takes the last word back, as table.undo() does on a table. Pages of charts have these words too.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .._errors import friendly
from .._typing import _Same
from .._units import PER_INCH, check_unit

if TYPE_CHECKING:
    from ..table.table import Table

# the resolution chart.save() uses unless resolution= is given
SAVE_RESOLUTION = 300


class ReadBackWords:
    def _what_it_is(self) -> str:
        return "page" if hasattr(self, "_charts") else "chart"

    def _drawn_figure(self):
        from .. import _style

        fig = self._render()
        return fig, _style.context(self._settings)

    @friendly
    def get_text_drawn(self) -> "Table":
        """A table of every piece of text the chart drew. text = chart.get_text_drawn()
        (with chart.draw_dots(x="hours", y="marks", colour="class") on sdata.get_example("marks"))

        One row per piece of text, read back from what matplotlib drew:
          panel   the chart number, as in get_numbers_drawn() (0: the whole chart or page)
          part    "title", "page title", "x label", "y label", "second y label", "z label", "legend title",
                  "legend entry", "colour bar label", "note", "caption", "panel letter", "tick x", "tick y",
                  "tick second y", "number on bar" or "name on dot"
          text    the words as drawn
          where   for a legend, its place ("inside top left", "bottom" ...); for a note, its place
                  ("top left") or the x, y it was written at
        Read one part with table words: text.keep_rows_where("part", is_equal_to="title").
        """
        from .._read_back import text_drawn, text_summary
        from ..table.table import table

        fig, look = self._drawn_figure()
        with look:
            frame = text_drawn(fig)
        print(text_summary(frame))
        return table(frame)

    @friendly
    def get_scales_drawn(self) -> "Table":
        """A table of the scales the chart drew: x, y and colour. scales = chart.get_scales_drawn()
        (with chart.draw_dots(x="hours", y="marks") on sdata.get_example("marks"))

        One row per chart and scale, read back from what matplotlib drew:
          panel        the chart number, as in get_numbers_drawn()
          scale        "x", "y", "second y", "second x", "z" or "colour"
          name         the axis name (or the colour bar's)
          low, high    the ends of the range shown (dates on a date axis)
          kind         "numbers", "log", "dates", "groups", "log through zero", "steps" (a colour scale cut
                       into steps) ...
          flipped      True when the axis runs from high to low (flip_x, flip_y)
          ticks        where the ticks are, and tick words: what is written there
          shared with  the other charts with the same scale over the same range
          colours      the colour map of a colour scale ("viridis"), and middle: its middle (middle=0)
        After chart.use_log_scale_y(), scales.get_cell_at(row=2, column="kind") gives "log".
        """
        from .._read_back import scales_drawn, scales_summary
        from ..table.table import table

        fig, look = self._drawn_figure()
        with look:
            frame = scales_drawn(fig)
        print(scales_summary(frame))
        return table(frame)

    @friendly
    def get_size(self, unit="inches") -> tuple[float, float]:
        """The size of the chart as (width, height). chart.get_size(unit="cm")

        unit= is "inches" (normal, as set_size), "cm", "mm" or "pixels". In pixels it is the size of a saved
        picture at the normal resolution (300 dots per inch), or exactly the pixels set_size(unit="pixels")
        asked for. For a page of charts it is the size of the page.
        """
        unit = check_unit(unit, "get_size")
        fig, look = self._drawn_figure()
        width, height = (float(v) for v in fig.get_size_inches())
        pixels = self._settings.get("pixels")
        if unit == "pixels":
            width, height = pixels if pixels else (width * SAVE_RESOLUTION, height * SAVE_RESOLUTION)
        else:
            width, height = width * PER_INCH[unit], height * PER_INCH[unit]
        width, height = round(float(width), 4), round(float(height), 4)
        short = {"inches": "inches", "cm": "cm", "mm": "mm", "pixels": "pixels"}[unit]
        at = " (saved at 300 dots per inch)" if unit == "pixels" and not pixels else ""
        print(f"The {self._what_it_is()} is {width:g} x {height:g} {short}{at}.")
        return width, height

    @friendly
    def undo(self: _Same) -> _Same:
        """Take the last step back. chart.undo()

        The last word you used on the chart is taken back, whatever it changed (a layer, a title, the style,
        the size), as table.undo() does on a table. Use it again to go back further.
        """
        history = self.__dict__.get("_history") or []
        if not history:
            print(f"Nothing to undo: this {self._what_it_is()} has no steps yet.")
            return self
        _, what, steps, settings = history.pop()
        object.__setattr__(self, "_steps", steps)
        object.__setattr__(self, "_settings", settings)
        object.__setattr__(self, "_cache", None)
        shown = what if what.startswith("a ") else f"{self._what_it_is()}.{what}()"
        print(f"Undone: {shown}")
        return self
