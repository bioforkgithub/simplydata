"""Charts phase, batch 3: fixes after the independent review of charts-3.

Each test fails without its fix. They read plotly's own data and layout (the hover text, the axes of the layout,
the colour scale, the legend and slider places) and the page's HTML, not the translator's meta.
"""

from __future__ import annotations

import contextlib
import io
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError, learn
from conftest import example_frame


@pytest.fixture(autouse=True)
def _plotly(needs_plotly):
    yield


@pytest.fixture(autouse=True)
def _close():
    yield
    plt.close("all")


def web(chart):
    from simplydata import _web

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        figure = _web.web_figure(chart)
    return figure, out.getvalue()


def hover_texts(figure):
    return [str(t) for trace in figure.data if getattr(trace, "text", None) is not None
            for t in np.ravel(np.asarray(trace.text, dtype=object))]


# ---------------------------------------------------------------- 1. pointing never names a row on a summary
PATIENTS = pd.DataFrame({"month": [1, 1, 1, 2, 2, 2], "y": [10, 20, 30, 5, 5, 20],
                         "patient": ["Ann", "Bob", "Cat", "Dan", "Eve", "Fay"]})


def test_a_line_of_averages_never_shows_a_persons_name():
    # the average of month 1 is 20, Bob's own value: matching by value would name Bob
    figure, out = web(sdata.chart(PATIENTS).draw_lines(x="month", y="y").show_when_pointing("patient"))
    texts = hover_texts(figure)
    assert texts and not any(name in t for t in texts for name in PATIENTS["patient"])
    assert all("the average of several rows" in t for t in texts)
    assert "summaries of several rows" in out


@pytest.mark.parametrize("make", [
    lambda c: c.draw_bars(x="month", y="y"),
    lambda c: c.draw_dots(x="month", y="y", show="average"),
    lambda c: c.draw_histogram(x="y"),
    lambda c: c.draw_dots(x="month", y="y").fit_line(),
])
def test_summary_marks_show_no_row(make):
    chart = make(sdata.chart(PATIENTS)).show_when_pointing("patient")
    figure, _ = web(chart)
    for trace in figure.data:
        kind = (trace.meta or {}).get("kind") if isinstance(trace.meta, dict) else None
        texts = [] if getattr(trace, "text", None) is None else [str(t) for t in np.ravel(trace.text)]
        if trace.type == "scatter" and trace.mode == "markers" and kind == "dot" and "show" not in str(make):
            continue  # the raw dots under a fitted line are rows
        assert not any(name in t for t in texts for name in PATIENTS["patient"]), (trace.type, texts)


def test_raw_dots_and_a_line_with_one_row_at_each_point_show_the_row():
    figure, _ = web(sdata.chart(PATIENTS).draw_dots(x="month", y="y").show_when_pointing("patient"))
    assert sorted(re.search(r"patient: (\w+)", t).group(1) for t in hover_texts(figure)) == sorted(PATIENTS["patient"])
    series = pd.DataFrame({"day": [1, 2, 3], "v": [3, 4, 5], "patient": ["Ann", "Bob", "Cat"]})
    figure, _ = web(sdata.chart(series).draw_lines(x="day", y="v").show_when_pointing("patient"))
    assert [re.search(r"patient: (\w+)", t).group(1) for t in hover_texts(figure)] == ["Ann", "Bob", "Cat"]


def test_two_groups_with_the_same_x_and_y_keep_their_own_rows():
    frame = pd.DataFrame({"x": [1, 2, 1, 3], "y": [5, 6, 5, 7], "group": ["A", "A", "B", "B"],
                          "patient": ["p1", "p2", "p3", "p4"]})
    figure, _ = web(sdata.chart(frame).draw_dots(x="x", y="y", colour="group").show_when_pointing("patient"))
    by_group = {t.name: [re.search(r"patient: (\w+)", s).group(1) for s in t.text] for t in figure.data if t.text}
    assert sorted(by_group["A"]) == ["p1", "p2"] and sorted(by_group["B"]) == ["p3", "p4"]


# ---------------------------------------------------------------- 2. second axes are drawn on the page
def _axes(figure):
    layout = figure.layout.to_plotly_json()
    return {key[0] + key[5:]: value for key, value in layout.items() if re.fullmatch(r"[xy]axis\d*", key)}


def _holding(figure):
    """The axes some mark is on (plotly draws an axis only for a mark on it)."""
    held = set()
    for trace in figure.data:
        if trace.type in ("scatter", "bar", "heatmap"):
            held.update({trace.xaxis or "x", trace.yaxis or "y"})
    return held


@pytest.mark.parametrize("make", [
    lambda: sdata.chart(example_frame("weather")).draw_dots(x="temperature", y="rain").add_second_x(
        formula="x * 9 / 5 + 32", labelled="Temperature (F)"),
    lambda: sdata.chart(example_frame("weather")).draw_dots(x="rain", y="temperature").add_second_y(
        formula="y * 9 / 5 + 32", labelled="Temperature (F)"),
    lambda: sdata.chart(example_frame("weather")).draw_lines(x="month", y="temperature").add_second_y(
        "rain", drawn_as="bars"),
    lambda: sdata.chart(example_frame("weather")).draw_lines(x="month_number", y="temperature").add_second_x(
        "wind_speed"),
])
def test_every_axis_with_tick_words_is_drawn(make):
    figure, _ = web(make())
    axes, held = _axes(figure), _holding(figure)
    with_words = [name for name, axis in axes.items() if axis.get("ticktext") and axis.get("visible") is not False]
    assert len(with_words) == 3  # x, y and the second scale
    for name in with_words:
        axis = axes[name]
        assert name in held, f"{name} has no mark on it, so plotly does not draw it"
        if axis.get("overlaying"):
            under = axes[axis["overlaying"]]
            assert axis["overlaying"] in held and under.get("visible") is not False
            assert axis["anchor"] in held and axes[axis["anchor"]].get("visible") is not False
            assert axis["domain"] == pytest.approx(under["domain"])


@pytest.mark.parametrize("letter", ["x", "y"])
def test_the_second_scales_ticks_are_the_formula_of_their_places(letter):
    weather = example_frame("weather")
    chart = sdata.chart(weather).draw_dots(x="temperature", y="temperature")
    getattr(chart, f"add_second_{letter}")(formula=f"{letter} * 9 / 5 + 32")
    figure, _ = web(chart)
    second = next(a for a in _axes(figure).values() if a.get("overlaying"))
    places = np.asarray(second["tickvals"], dtype=float)
    words = np.asarray([float(w.replace("−", "-")) for w in second["ticktext"]])
    assert np.allclose(places * 9 / 5 + 32, words)
    assert second["side"] == ("top" if letter == "x" else "right")


# ---------------------------------------------------------------- 3. break_between_y hides no data
BROKEN = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [10, 12, 30, 95, 100]})


def test_a_break_that_would_hide_values_is_refused():
    chart = sdata.chart(BROKEN).draw_dots(x="x", y="y").break_between_y(20, 80)
    with pytest.raises(SimplydataError, match=r"would hide 1 drawn value between 20 and 80 \(from 30 to 30\)"):
        web(chart)
    with pytest.raises(SimplydataError, match="would hide"):
        quiet = io.StringIO()
        with contextlib.redirect_stdout(quiet):
            chart.get_numbers_drawn()


def test_a_break_with_an_empty_part_is_refused_on_the_data():
    for low, high, words in ((5, 9, "lower part would be empty"), (100, 120, "upper part would be empty")):
        chart = sdata.chart(BROKEN).draw_dots(x="x", y="y").break_between_y(low, high)
        with pytest.raises(SimplydataError, match=words):
            with contextlib.redirect_stdout(io.StringIO()):
                chart.get_numbers_drawn()


def test_a_broken_chart_reads_each_point_once_on_its_part():
    chart = sdata.chart(BROKEN).draw_dots(x="x", y="y").break_between_y(35, 80)
    with contextlib.redirect_stdout(io.StringIO()):
        table = chart.get_numbers_drawn().as_pandas()
    assert sorted(table["y"]) == sorted(BROKEN["y"])  # once each
    assert set(table.loc[table["panel"] == 1, "y"]) == {95, 100}  # the upper part
    assert set(table.loc[table["panel"] == 2, "y"]) == {10, 12, 30}  # the lower part


# ---------------------------------------------------------------- 4. nothing is left out without a word
def _chart_examples():
    from simplydata.chart import Chart

    words = set(Chart._word_names())
    return [k for k in learn.HELP_EXAMPLES if k in words and k not in
            ("break_between_y", "use_scale_x", "use_scale_y", "animate")]


@pytest.mark.parametrize("key", _chart_examples())
def test_every_chart_word_leaves_nothing_out_of_the_web_page(key, tmp_path, monkeypatch):
    from test_charts_batch3_web import _example_chart

    chart = _example_chart(key, tmp_path, monkeypatch)
    figure, out = web(chart)
    assert figure.layout.meta["simplydata"]["left out"] == []
    assert "leaves out" not in out


def test_what_is_left_out_is_said_in_a_note(monkeypatch):
    from simplydata import _web

    monkeypatch.delattr(_web.Translator, "_bar")  # as if bars could not be drawn on a web page
    figure, out = web(sdata.chart(example_frame("marks")).draw_bars(x="class", y="marks"))
    assert "the web page leaves out what it cannot draw from this chart (bar)" in out


# ---------------------------------------------------------------- 6. the page's layout
def test_a_wide_page_fits_a_window_and_keeps_its_shape(tmp_path):
    marks = example_frame("marks")
    charts = [sdata.chart(marks).draw_bars(x="class", y="marks"), sdata.chart(marks).draw_boxes(x="class", y="marks"),
              sdata.chart(marks).draw_dots(x="hours", y="marks")]
    page = sdata.put_side_by_side(*charts)
    with contextlib.redirect_stdout(io.StringIO()):
        page.save(str(tmp_path / "page.html"))
    text = (tmp_path / "page.html").read_text(encoding="utf-8")
    box = re.search(r'class="simplydata-chart" style="width:100%; max-width:(\d+)px; aspect-ratio:(\d+) / (\d+);',
                    text)
    assert box and int(box.group(1)) <= 1100  # no sideways scrolling in a 1200 px window
    figure, _ = web(page)
    fonts = [a["tickfont"]["size"] for a in _axes(figure).values() if "tickfont" in a]
    with contextlib.redirect_stdout(io.StringIO()):
        single, _ = web(charts[0])
    assert max(fonts) < max(a["tickfont"]["size"] for a in _axes(single).values() if "tickfont" in a)


def test_the_animation_buttons_do_not_cover_the_slider():
    figure, _ = web(sdata.chart(example_frame("growth")).draw_bars(x="country", y="population").animate(over="year"))
    slider, buttons = figure.layout.sliders[0], figure.layout.updatemenus[0]
    assert slider.active == 0 and figure.frames[0].name == slider.steps[0].label
    assert buttons.x == 0 and slider.x * figure.layout.width >= 140  # Play and Pause (about 130 px) end first
    assert slider.x + slider.len <= 1 and slider.pad.r > 0  # the last year is not cut


def test_a_filled_contour_maps_colour_bar_is_banded():
    figure, _ = web(sdata.chart(example_frame("island")).draw_contour(x="east", y="north", z="height"))
    scale = next(t.marker.colorscale for t in figure.data if t.type == "scatter" and t.marker.showscale)
    positions = [p for p, _ in scale]
    assert len(positions) != len(set(positions))  # each band starts where the last ends: steps, not a blend
    for (p1, c1), (p2, c2) in zip(scale[::2], scale[1::2]):
        assert c1 == c2  # one colour across each band


def test_patterned_bars_show_their_pattern_in_the_legend():
    chart = sdata.chart(example_frame("marks")).draw_bars(x="class", y="marks", colour="subject", hatched=True)
    figure, _ = web(chart)
    shown = [t for t in figure.data if t.showlegend]
    assert len(shown) == 3 and all(t.type == "bar" and isinstance(t.marker.pattern.shape, str) for t in shown)
    for t in shown:
        assert isinstance(t.marker.color, str)  # one colour for the set, as the legend draws it
        assert not t.marker.pattern.fgcolor.replace(" ", "").endswith(",0)")  # a pattern colour that shows


def test_a_legend_is_held_at_the_corner_matplotlib_put_it():
    chart = sdata.chart(example_frame("growth")).draw_lines(x="year", y="population", colour="country")
    chart.use_log_scale_y()
    ax = chart._render().axes[0]
    figure, _ = web(chart)
    legend = figure.layout.legend
    box = ax.get_legend().get_window_extent()
    width, height = chart._render().bbox.width, chart._render().bbox.height
    assert legend.xanchor == "right" and legend.yanchor == "bottom"  # matplotlib put it at the bottom right
    assert legend.x == pytest.approx(box.x1 / width) and legend.y == pytest.approx(box.y0 / height)


# ---------------------------------------------------------------- 7. privacy notes
def test_a_notebook_page_says_it_holds_the_numbers(monkeypatch):
    import sys
    import types

    from simplydata import _web

    monkeypatch.setattr(_web, "in_notebook", lambda: True)
    display = types.ModuleType("IPython.display")
    display.HTML, display.display = (lambda data: data), (lambda thing: None)
    monkeypatch.setitem(sys.modules, "IPython", types.ModuleType("IPython"))
    monkeypatch.setitem(sys.modules, "IPython.display", display)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        sdata.chart(example_frame("marks")).draw_dots(x="hours", y="marks").show_in_web_page()
    assert "the web page holds the numbers drawn" in out.getvalue()


def test_the_temporary_page_says_where_it_is_and_what_it_holds(tmp_path):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        sdata.chart(example_frame("marks")).draw_dots(x="hours", y="marks").show_in_web_page()
    said = out.getvalue()
    page = next(tmp_path.glob("simplydata_chart_*.html"))
    assert str(page) in said and "folder for temporary files" in said
    assert "holds the numbers drawn" in said and "delete it" in said
