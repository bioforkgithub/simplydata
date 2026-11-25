"""Charts phase, batch 3: two leftovers of the review of charts-3, on web pages.

1. A log axis writes some small ticks (20, 30, 40 between 10 and 100) but draws grid lines only at its big ticks;
   plotly draws a grid line at every tick it writes, so the page drew grid lines the picture has not.
2. A legend that only just misses an error bar in the picture covered it on a page in a narrow window (plotly writes
   the legend in the page's pixels); such a legend now goes outside the chart, on the right.
3. Found by the reliability study (validation/cases_underneath_charts_2.py, draw_side_histograms): a band drawn
   sideways (fill_betweenx: violins, the density on the right edge) was read back with its x and y swapped, in
   get_numbers_drawn() and so on the web page.

Each test reads plotly's own layout (grid flags, shapes, legend place, margins), not the translator's meta.
"""

from __future__ import annotations

import contextlib
import io

import matplotlib.pyplot as plt
import pytest

import simplydata as sdata


@pytest.fixture(autouse=True)
def _plotly(needs_plotly):
    yield


@pytest.fixture(autouse=True)
def _close():
    yield
    plt.close("all")


def web(chart):
    from simplydata import _web

    with contextlib.redirect_stdout(io.StringIO()):
        return _web.web_figure(chart)


def grid_shapes(figure, letter):
    """The places of the grid lines drawn as shapes across the chart along one axis ("y": lines across)."""
    lines = [s for s in figure.layout.shapes or () if s.type == "line" and not s.name]
    if letter == "y":
        return sorted(float(s.y0) for s in lines if str(s.xref).endswith("domain") and s.y0 == s.y1)
    return sorted(float(s.x0) for s in lines if str(s.yref).endswith("domain") and s.x0 == s.x1)


def test_a_log_axis_draws_grid_lines_only_where_the_picture_does():
    growth = sdata.get_example("growth")
    chart = sdata.chart(growth).draw_lines(x="year", y="population", colour="country").use_log_scale_y()
    figure = web(chart)
    ax = chart._render().axes[0]
    low, high = ax.get_ylim()
    pictured = sorted(float(loc) for loc, tick in zip(ax.yaxis.get_majorticklocs(), ax.yaxis.get_major_ticks())
                      if tick.gridline.get_visible() and low <= loc <= high)
    assert pictured == [10.0]  # the picture: one grid line, at 10
    written = list(figure.layout.yaxis.tickvals)
    assert {20.0, 30.0, 40.0} <= set(written)  # small ticks with words, as in the picture
    assert not figure.layout.yaxis.showgrid  # plotly would draw a grid line at each of them
    assert grid_shapes(figure, "y") == pictured
    assert figure.layout.yaxis.minor.showgrid is False


def test_an_axis_with_grid_lines_at_every_tick_word_keeps_plotlys_own_grid():
    marks = sdata.get_example("marks")
    figure = web(sdata.chart(marks).draw_dots(x="hours", y="marks").show_grid())
    assert figure.layout.yaxis.showgrid and figure.layout.xaxis.showgrid
    assert grid_shapes(figure, "y") == [] and grid_shapes(figure, "x") == []


def test_a_legend_that_only_just_misses_an_error_bar_goes_outside_on_the_web_page():
    marks = sdata.get_example("marks")
    chart = sdata.chart(marks).draw_bars(x="class", y="marks", colour="subject", error="standard deviation",
                                         hatched=True)
    figure = web(chart)
    right_edge = figure.layout.xaxis.domain[1]
    legend = figure.layout.legend
    assert legend.x > right_edge and legend.xanchor == "left" and legend.yanchor == "top"
    assert figure.layout.margin.r > 0  # the page is made wider for it
    paper = figure.layout.width - figure.layout.margin.r
    assert paper == pytest.approx(chart._render().get_figwidth() * 96, abs=1)  # the chart itself keeps its size
    # the picture is unchanged: matplotlib's legend stays inside the chart
    ax = chart._render().axes[0]
    box, area = ax.get_legend().get_window_extent(), ax.get_window_extent()
    assert area.x0 <= box.x0 and box.x1 <= area.x1


def test_a_legend_with_room_stays_where_matplotlib_put_it():
    marks = sdata.get_example("marks")
    chart = sdata.chart(marks).draw_lines(x="subject", y="marks", colour="class").draw_error_bars("standard error")
    figure = web(chart)
    assert figure.layout.legend.x <= figure.layout.xaxis.domain[1]
    assert figure.layout.margin.r == 0


def test_a_sideways_band_is_read_back_with_its_position_on_y():
    import pandas as pd

    table = pd.DataFrame({"group": ["a"] * 5, "value": [1.0, 2.0, 2.5, 3.0, 4.0]})
    chart = sdata.chart(table).draw_violins(x="group", y="value")
    with contextlib.redirect_stdout(io.StringIO()):
        drawn = chart.get_numbers_drawn().as_pandas()
    band = drawn[drawn["kind"] == "band"]
    # cut=0: the violin runs from the smallest to the largest value, along y, round its group (x = 0)
    assert band["y"].min() == pytest.approx(1.0) and band["y"].max() == pytest.approx(4.0)
    assert (band["low"] <= 0).all() and (band["high"] >= 0).all() and band["x"].isna().all()
    # the web page draws the same outline: along y from 1 to 4, round x = 0
    figure = web(chart)
    trace = [t for t in figure.data if (t.meta or {}).get("kind") == "band"][0]
    ys = [v for v in trace.y if v is not None]
    xs = [v for v in trace.x if v is not None]
    assert min(ys) == pytest.approx(1.0) and max(ys) == pytest.approx(4.0)
    assert min(xs) < 0 < max(xs) and max(abs(v) for v in xs) < 0.5


def test_a_sideways_band_matches_fill_betweenx():
    from simplydata._numbers_drawn import numbers_drawn

    fig, ax = plt.subplots()
    ax.fill_betweenx([1.0, 2.0, 3.0], 0.0, [5.0, 6.0, 7.0])
    rows = numbers_drawn(fig)
    band = rows[rows["kind"] == "band"]
    assert list(band["y"]) == [1.0, 2.0, 3.0]
    assert list(band["low"]) == [0.0, 0.0, 0.0] and list(band["high"]) == [5.0, 6.0, 7.0]


def test_a_violins_box_is_drawn_over_its_body_on_the_web_page_as_in_the_picture():
    marks = sdata.get_example("marks")
    figure = web(sdata.chart(marks).draw_violins(x="class", y="marks"))
    kinds = [(t.meta or {}).get("kind") for t in figure.data]
    bodies = [i for i, k in enumerate(kinds) if k == "band"]
    boxes = [i for i, k in enumerate(kinds) if k == "line"]
    assert bodies and boxes and max(bodies) < min(boxes)  # plotly draws later marks on top
