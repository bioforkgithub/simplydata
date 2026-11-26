"""Words for charts as web pages (charts phase, batch 3; approved by Manish on 2026-11-25).

chart.save("marks.html") makes a web page (the end of the file name decides, as for every file), and
chart.show_in_web_page() shows one; chart.show_when_pointing(...) chooses the columns shown when the pointer rests
on a mark and chart.add_range_bar_x() adds a small bar under the x-axis to choose the range shown. The web page is
drawn by plotly from what matplotlib drew (simplydata._web): the same numbers as the picture, nothing worked out
again. plotly is the optional extra simplydata[web].

Decision D2 (Manish, 2026-11-25): a chart becomes a web page where it goes (save(".html"), show_in_web_page()), so
there is no option on sdata.chart() for it; interactive=True there points here.
"""

from __future__ import annotations

from .._typing import _Same

from .._data import is_listlike
from .._errors import SimplydataError, column_error, friendly

# sdata.chart(..., interactive=True) and table.start_chart(interactive=True): an other name that points here
WEB_POINTERS = {"interactive": 'chart.show_in_web_page(), or chart.save("marks.html") for a web page file: a chart '
                               "becomes a web page where it goes"}


class WebWords:
    """Words for web pages (simplydata[web])."""

    @friendly(pointers={"renderer": "chart.show_in_web_page() (a notebook shows it inside, a script opens the "
                                    "browser)"})
    def show_in_web_page(self: _Same) -> _Same:
        """Show the chart as a web page: point at marks to read them, zoom, click the legend.
        chart.show_in_web_page() (with chart.draw_dots(x="hours", y="marks") on sdata.get_example("marks"))

        In Jupyter and VS Code the page shows below the cell; from a script it opens in your web
        browser from a file on this computer (nothing goes on the internet). The numbers are those of
        the picture: matplotlib draws the chart and plotly shows what it drew. Needs simplydata[web].
        """
        from .._web import need_plotly, show_page

        need_plotly()
        return show_page(self)

    @friendly(pointers={"hover_data": 'chart.show_when_pointing("name", "class")',
                        "hover_name": 'chart.show_when_pointing("name")'})
    def show_when_pointing(self: _Same, *columns, all_lines=False) -> _Same:
        """The columns shown when the pointer rests on a dot or a line in a web page.
        chart.show_when_pointing("name", "class") (with chart.draw_dots(x="hours", y="marks") on
        sdata.get_example("marks"))

        Only the columns you name are shown, never the whole row. all_lines=True shows one box with
        every line at that x. A picture (.png, .pdf) cannot point: it leaves this out, with a note.
        """
        if len(columns) == 1 and is_listlike(columns[0]) and not isinstance(columns[0], str):
            columns = tuple(columns[0])
        if not isinstance(all_lines, bool):
            raise SimplydataError(f".show_when_pointing() needs all_lines=True or all_lines=False, not {all_lines!r}.")
        if not columns and not all_lines:
            raise SimplydataError('.show_when_pointing() needs the columns to show, for example '
                                  'chart.show_when_pointing("name", "class").')
        data = self._data
        for column in columns:
            if not isinstance(column, str) or data is None or column not in data.columns:
                raise column_error(column, [] if data is None else data.columns)
        return self._set(pointing=dict(columns=list(dict.fromkeys(columns)), all_lines=all_lines))

    @friendly
    def add_range_bar_x(self: _Same) -> _Same:
        """A small bar under the x-axis of a web page, to choose the part of the x-axis shown.
        chart.add_range_bar_x() (with chart.draw_lines(x="month", y="visitors", colour="museum") on
        sdata.get_example("visitors"))

        Drag its ends to zoom in on a time; good for long series. Web pages only: a picture leaves it
        out, with a note.
        """
        if self._settings.get("projection") is not None:
            raise SimplydataError(".add_range_bar_x() works on flat charts with an x-axis, not on round or 3D charts.")
        return self._set(range_bar_x=True)
