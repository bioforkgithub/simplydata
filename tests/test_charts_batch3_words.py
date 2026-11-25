"""Charts phase, batch 3: the priority-3 words (approved by Manish on 2026-11-25).

Each word is checked against plain matplotlib or seaborn doing the same job, by reading what was drawn
(get_numbers_drawn(), get_scales_drawn() and the matplotlib objects), never by comparing pixels. Then the checks of
the input, undo, black and white, say_what_it_shows() and the read-back words on each new word."""

from __future__ import annotations

import contextlib
import io

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
import seaborn as sns
from matplotlib.figure import Figure

import simplydata as sdata
from simplydata import SimplydataError
from simplydata._numbers_drawn import numbers_drawn
from conftest import example_frame


@pytest.fixture(autouse=True)
def _close():
    yield
    plt.close("all")


def quiet(make):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        result = make()
    return result, out.getvalue()


def numbers(chart):
    return quiet(lambda: chart.get_numbers_drawn().as_pandas())[0]


def scales(chart):
    return quiet(lambda: chart.get_scales_drawn().as_pandas())[0]


def drawn_by_hand(draw, projection=None):
    fig = Figure()
    ax = fig.add_subplot(projection=projection)
    draw(ax)
    return fig, ax


# ---------------------------------------------------------------- broken y-axis
def test_break_between_y_is_the_gallery_layout_two_panels_sharing_x():
    marks = example_frame("marks")
    chart = sdata.chart(marks).draw_bars(x="class", y="marks")
    chart.break_between_y(5, 50)
    fig, out = quiet(chart._render)
    top, bottom = fig.axes
    assert top.get_shared_x_axes().joined(top, bottom)
    assert bottom.get_ylim()[1] == 5 and top.get_ylim()[0] == 50
    assert not top.spines["bottom"].get_visible() and not bottom.spines["top"].get_visible()
    by_hand = Figure()
    hand_top, hand_bottom = by_hand.subplots(2, 1, sharex=True)
    for ax in (hand_top, hand_bottom):
        sns.barplot(marks, x="class", y="marks", errorbar=None, ax=ax)
    hand_bottom.set_ylim(hand_bottom.get_ylim()[0], 5)
    hand_top.set_ylim(50, hand_top.get_ylim()[1])
    ours = numbers_drawn(fig)[["panel", "kind", "x", "y", "low", "high"]]
    theirs = numbers_drawn(by_hand)[["panel", "kind", "x", "y", "low", "high"]]
    pd.testing.assert_frame_equal(ours, theirs)
    assert "say in the caption" in out
    assert not (numbers_drawn(fig)["kind"] == "dot").any()  # the slanted break marks are not data


def test_break_between_y_checks_its_numbers():
    chart = sdata.chart(example_frame("marks")).draw_bars(x="class", y="marks")
    with pytest.raises(SimplydataError, match="low end comes first"):
        chart.break_between_y(50, 5)
    with pytest.raises(SimplydataError, match="two numbers"):
        chart.break_between_y("a", 5)
    chart.break_between_y(5, 500)
    with pytest.raises(SimplydataError, match="nothing is drawn above 500"):
        quiet(chart._render)
    with pytest.raises(SimplydataError, match="flat chart"):
        sdata.chart(example_frame("island")).draw_surface(x="east", y="north", z="height").break_between_y(1, 2)


# ---------------------------------------------------------------- other scales
def test_use_scale_y_square_root_is_matplotlibs_function_scale():
    marks = example_frame("marks")
    chart = sdata.chart(marks).draw_dots(x="hours", y="marks").use_scale_y("square root")
    ax = chart._render().axes[0]
    assert ax.get_yscale() == "function"
    fig, hand = drawn_by_hand(lambda a: sns.scatterplot(marks, x="hours", y="marks", ax=a))
    low, high = hand.get_ylim()
    hand.set_yscale("function", functions=(lambda v: np.sqrt(np.clip(v, 0, None)), np.square))
    hand.set_ylim(max(low, 0), high)
    assert ax.get_ylim() == pytest.approx(hand.get_ylim())
    assert np.allclose(ax.transData.transform([[5, 64]]), ax.transData.transform([[5, 64]]))
    table = scales(chart)
    assert table.loc[table["scale"] == "y", "kind"].item() == "square root"


@pytest.mark.parametrize("scale", ["logit", "asinh"])
def test_use_scale_x_logit_and_asinh_are_matplotlibs_own(scale):
    frame = pd.DataFrame({"share": [0.1, 0.4, 0.9], "y": [1, 2, 3]})
    chart = sdata.chart(frame).draw_dots(x="share", y="y").use_scale_x(scale)
    assert chart._render().axes[0].get_xscale() == scale
    assert scales(chart).loc[lambda t: t["scale"] == "x", "kind"].item() == scale


def test_use_scale_refuses_values_it_cannot_show_and_points_to_the_log_word():
    frame = pd.DataFrame({"x": [1, 2, 3], "y": [-1, 2, 3]})
    chart = sdata.chart(frame).draw_dots(x="x", y="y").use_scale_y("square root")
    with pytest.raises(SimplydataError, match="below 0"):
        quiet(chart._render)
    with pytest.raises(SimplydataError, match="use_log_scale_y"):
        sdata.chart(frame).use_scale_y("log")
    with pytest.raises(SimplydataError):
        sdata.chart(frame).use_scale_y("cube")


def test_one_scale_for_an_axis_the_later_word_wins():
    chart = sdata.chart(example_frame("marks")).draw_dots(x="hours", y="marks")
    chart.use_log_scale_y()
    chart.use_scale_y("square root")
    assert chart._render().axes[0].get_yscale() == "function"
    chart.use_log_scale_y()
    chart._cache = None
    assert chart._render().axes[0].get_yscale() == "log"


def test_log_scale_through_zero_is_symlog_and_allows_zero_and_below():
    frame = pd.DataFrame({"x": [1, 2, 3, 4], "y": [-100, 0, 10, 1000]})
    chart = sdata.chart(frame).draw_dots(x="x", y="y").use_log_scale_y(through_zero=True)
    chart.set_range_y(-1000, 2000)
    ax = chart._render().axes[0]
    assert ax.get_yscale() == "symlog"
    fig, hand = drawn_by_hand(lambda a: (a.set_yscale("symlog"), sns.scatterplot(frame, x="x", y="y", ax=a)))
    assert numbers(chart)[["x", "y"]].to_numpy().tolist() == numbers_drawn(fig)[["x", "y"]].to_numpy().tolist()
    assert scales(chart).loc[lambda t: t["scale"] == "y", "kind"].item() == "log through zero"
    with pytest.raises(SimplydataError, match="through_zero=True or"):
        chart.use_log_scale_x(through_zero="yes")
    with pytest.raises(SimplydataError, match="zero or negative"):  # a plain log scale still checks
        quiet(sdata.chart(frame).draw_dots(x="x", y="y").use_log_scale_y()._render)


def test_use_background_colour_is_set_facecolor():
    chart = sdata.chart(example_frame("marks")).draw_dots(x="hours", y="marks")
    chart.use_background_colour("ivory")
    assert matplotlib.colors.to_hex(chart._render().axes[0].get_facecolor()) == matplotlib.colors.to_hex("ivory")
    assert sdata.Chart.use_background_color is sdata.Chart.use_background_colour
    with pytest.raises(SimplydataError, match="colour name"):
        chart.use_background_colour("not a colour")


# ---------------------------------------------------------------- hexagons
def test_hexagon_bins_are_matplotlibs_hexbin_counts():
    marks = example_frame("marks")
    chart = sdata.chart(marks).draw_hexagon_bins(x="hours", y="height", with_bins=8)
    fig, hand = drawn_by_hand(lambda a: a.hexbin(marks["hours"], marks["height"], gridsize=8, mincnt=1))
    theirs = hand.collections[0]
    table = numbers(chart)
    assert (table["kind"] == "hexagon").all()
    assert np.allclose(table[["x", "y"]].to_numpy(float), theirs.get_offsets())
    assert table["value"].tolist() == list(theirs.get_array())
    assert table["value"].sum() == len(marks)
    text = quiet(lambda: chart.get_text_drawn().as_pandas())[0]
    assert "count" in text.loc[text["part"] == "colour bar label", "text"].tolist()
    with pytest.raises(SimplydataError, match="whole number from 3 to 200"):
        sdata.chart(marks).draw_hexagon_bins(x="hours", y="height", with_bins=1)
    bw = sdata.chart(marks).draw_hexagon_bins(x="hours", y="height").use_style("black and white")
    assert bw._render().axes[0].collections[0].get_cmap().name == "Greys"


# ---------------------------------------------------------------- side densities
def test_side_density_curves_are_seaborns_kdeplot():
    marks = example_frame("marks")
    chart = sdata.chart(marks).draw_dots(x="hours", y="marks").draw_side_histograms(drawn_as="density")
    ax = chart._render().axes[0]
    top, right = ax.child_axes
    hand = Figure().add_subplot()
    sns.kdeplot(x=marks["hours"].to_numpy(float), ax=hand, fill=True)
    ours = top.collections[0].get_paths()[0].vertices
    theirs = hand.collections[0].get_paths()[0].vertices
    assert np.allclose(ours, theirs)
    grouped = sdata.chart(marks).draw_dots(x="hours", y="marks", colour="class")
    grouped.draw_side_histograms(drawn_as="density")
    top = grouped._render().axes[0].child_axes[0]
    assert len(top.get_lines()) == marks["class"].nunique()  # one outline per group
    with pytest.raises(SimplydataError, match="drawn_as"):
        sdata.chart(marks).draw_dots(x="hours", y="marks").draw_side_histograms(drawn_as="violins")


# ---------------------------------------------------------------- time bars
def test_time_bars_go_from_start_to_end_first_row_at_the_top():
    frame = pd.DataFrame({"task": ["plan", "build", "test", "plan"],
                          "start": pd.to_datetime(["2026-01-05", "2026-02-01", "2026-03-01", "2026-04-01"]),
                          "end": pd.to_datetime(["2026-01-30", "2026-03-10", "2026-03-20", "2026-04-15"]),
                          "ship": ["Kronprins", "Kronprins", "Polarstern", "Polarstern"]})
    chart = sdata.chart(frame).draw_time_bars(start="start", end="end", y="task", colour="ship")
    ax = chart._render().axes[0]
    assert ax.yaxis_inverted()
    table = numbers(chart)
    assert sorted(zip(table["low"], table["high"])) == sorted(
        zip(matplotlib.dates.date2num(frame["start"]), matplotlib.dates.date2num(frame["end"])))
    assert [t.get_text() for t in ax.get_yticklabels()] == ["plan", "build", "test"]
    assert [t.get_text() for t in ax.get_legend().get_texts()] == ["Kronprins", "Polarstern"]
    scale = scales(chart)
    assert scale.loc[scale["scale"] == "x", "kind"].item() == "dates"
    hand = Figure().add_subplot()
    hand.barh(["plan", "build", "test"], [3, 4, 3], left=[1, 3, 6], height=0.8)
    lists = sdata.chart().draw_time_bars(start=[1, 3, 6], end=[4, 7, 9], y=["plan", "build", "test"])
    ours = [(p.get_x(), p.get_y(), p.get_width(), p.get_height()) for p in lists._render().axes[0].patches]
    assert ours == [(p.get_x(), p.get_y(), p.get_width(), p.get_height()) for p in hand.patches]


def test_time_bars_check_their_columns():
    frame = pd.DataFrame({"task": ["a", "b"], "start": [5, 1], "end": [2, 3], "when": ["x", "y"]})
    with pytest.raises(SimplydataError, match="end before"):
        sdata.chart(frame).draw_time_bars(start="start", end="end", y="task")
    with pytest.raises(SimplydataError, match="both dates or both numbers"):
        sdata.chart(frame).draw_time_bars(start="start", end="when", y="task")
    with pytest.raises(SimplydataError, match="needs start=, end= and y="):
        sdata.chart(frame).draw_time_bars(start="start")


# ---------------------------------------------------------------- rectangles and circles
def test_rectangle_and_circle_are_matplotlib_patches():
    chart = sdata.chart(example_frame("marks")).draw_dots(x="hours", y="marks")
    chart.draw_rectangle(x_between=[4, 6], y_between=[60, 80]).draw_circle(centre=[5, 70], radius=1, hollow=True)
    table = numbers(chart)
    box = table[table["kind"] == "rectangle"].iloc[0]
    assert (box["x"], box["low"], box["high"], box["y"]) == (5, 60, 80, 20)
    circle = table[table["kind"] == "shape"][["x", "y"]].to_numpy(float)
    assert np.allclose(np.hypot(circle[:, 0] - 5, circle[:, 1] - 70), 1, atol=1e-3)
    ax = chart._render().axes[0]
    from matplotlib.patches import Circle, Rectangle

    rect = next(p for p in ax.patches if isinstance(p, Rectangle))
    ring = next(p for p in ax.patches if isinstance(p, Circle))
    assert rect.get_facecolor()[3] == pytest.approx(0.25) and ring.get_facecolor()[3] == 0
    with pytest.raises(SimplydataError, match="low end comes first"):
        chart.draw_rectangle(x_between=[6, 4], y_between=[60, 80])
    with pytest.raises(SimplydataError, match="radius="):
        chart.draw_circle(centre=[5, 70], radius=-1)
    with pytest.raises(SimplydataError, match="centre="):
        chart.draw_circle(centre=5, radius=1)


# ---------------------------------------------------------------- residual dots, event lines, 3D bars
def test_residual_dots_are_seaborns_residplot():
    marks = example_frame("marks")
    chart = sdata.chart(marks).draw_residual_dots(x="hours", y="marks")
    fig, hand = drawn_by_hand(lambda a: sns.residplot(marks, x="hours", y="marks", ax=a))
    ours = numbers(chart)
    theirs = numbers_drawn(fig)
    pd.testing.assert_frame_equal(ours[["kind", "x", "y"]], theirs[["kind", "x", "y"]])
    assert chart._render().axes[0].get_ylabel() == "residual of marks"


def test_event_lines_are_matplotlibs_eventplot():
    marks = example_frame("marks")
    chart = sdata.chart(marks).draw_event_lines(x="hours", y="class")
    groups = list(pd.unique(marks["class"]))
    fig, hand = drawn_by_hand(lambda a: a.eventplot([marks.loc[marks["class"] == g, "hours"] for g in groups],
                                                    lineoffsets=range(len(groups)), linelengths=0.8))
    ours = numbers(chart)
    pd.testing.assert_frame_equal(ours[["x", "y", "low", "high"]], numbers_drawn(fig)[["x", "y", "low", "high"]])
    ax = chart._render().axes[0]
    assert [t.get_text() for t in ax.get_yticklabels()] == groups
    with pytest.raises(SimplydataError, match="needs x="):
        sdata.chart(marks).draw_event_lines()


def test_bars_3d_are_matplotlibs_bar3d_one_per_row():
    weather = example_frame("weather")
    chart = sdata.chart(weather).draw_bars_3d(x="month", y="city", z="rain")
    table, out = quiet(lambda: chart.get_numbers_drawn().as_pandas())
    assert (table["kind"] == "bar").all() and len(table) == len(weather)
    assert sorted(table["high"]) == sorted(weather["rain"].astype(float))
    assert np.allclose(table["value"], table["high"] - table["low"])
    assert "heat map" in quiet(chart._render)[1] or "heat map" in out
    ax = chart._render().axes[0]
    assert [t.get_text() for t in ax.get_yticklabels()] == list(pd.unique(weather["city"]))
    twice = pd.concat([weather, weather])
    with pytest.raises(SimplydataError, match="more than one row"):
        quiet(sdata.chart(twice).draw_bars_3d(x="month", y="city", z="rain")._render)


# ---------------------------------------------------------------- undo, read-back, words, black and white
NEW_WORDS = [
    ("break_between_y", lambda c: c.draw_bars(x="class", y="marks").break_between_y(5, 50)),
    ("use_scale_y", lambda c: c.draw_dots(x="hours", y="marks").use_scale_y("square root")),
    ("use_scale_x", lambda c: c.draw_dots(x="hours", y="marks").use_scale_x("asinh")),
    ("use_background_colour", lambda c: c.draw_dots(x="hours", y="marks").use_background_colour("ivory")),
    ("draw_hexagon_bins", lambda c: c.draw_hexagon_bins(x="hours", y="height")),
    ("draw_rectangle", lambda c: c.draw_dots(x="hours", y="marks").draw_rectangle(x_between=[4, 6],
                                                                                  y_between=[60, 80])),
    ("draw_circle", lambda c: c.draw_dots(x="hours", y="marks").draw_circle(centre=[5, 70], radius=1)),
    ("draw_residual_dots", lambda c: c.draw_residual_dots(x="hours", y="marks")),
    ("draw_event_lines", lambda c: c.draw_event_lines(x="hours", y="class")),
    ("show_when_pointing", lambda c: c.draw_dots(x="hours", y="marks").show_when_pointing("name")),
    ("add_range_bar_x", lambda c: c.draw_dots(x="hours", y="marks").add_range_bar_x()),
]


@pytest.mark.parametrize("word, make", NEW_WORDS)
def test_every_new_word_can_be_undone_and_read_back(word, make):
    chart = make(sdata.chart(example_frame("marks")))
    _, out = quiet(lambda: (chart.get_numbers_drawn(), chart.get_text_drawn(), chart.get_scales_drawn(),
                            chart.say_what_it_shows()))
    assert "Read" in out
    before = len(chart._history)
    _, said = quiet(chart.undo)
    assert f"chart.{word}()" in said and len(chart._history) == before - 1


def test_say_what_it_shows_names_the_new_marks_and_scales():
    chart = sdata.chart(example_frame("marks")).draw_hexagon_bins(x="hours", y="height")
    chart.draw_rectangle(x_between=[4, 6], y_between=[145, 155]).use_scale_y("square root")
    chart.use_background_colour("ivory")
    text, _ = quiet(chart.say_what_it_shows)
    assert "hexagons coloured by how many dots" in text
    assert "draw_rectangle(): a rectangle from x = 4 to 6" in text
    assert "(square root scale)" in text and 'coloured "ivory"' in text
    broken = sdata.chart(example_frame("marks")).draw_bars(x="class", y="marks").break_between_y(5, 50)
    assert "the part from 5 to 50 is left out" in quiet(broken.say_what_it_shows)[0]


def test_time_bars_in_black_and_white_get_greys_and_patterns():
    frame = pd.DataFrame({"task": ["a", "b"], "start": [1, 2], "end": [3, 5], "ship": ["x", "y"]})
    chart = sdata.chart(frame).draw_time_bars(start="start", end="end", y="task", colour="ship")
    chart.use_style("black and white")
    patches = chart._render().axes[0].patches
    assert [p.get_hatch() for p in patches] == ["//", "\\\\"]
    for p in patches:
        r, g, b, _ = p.get_facecolor()
        assert r == g == b  # grey


@pytest.mark.parametrize("name, word", [("hexbin", "draw_hexagon_bins"), ("broken_barh", "draw_time_bars"),
                                        ("residplot", "draw_residual_dots"), ("eventplot", "draw_event_lines"),
                                        ("bar3d", "draw_bars_3d"), ("set_facecolor", "use_background_colour"),
                                        ("symlog", "through_zero=True"), ("brokenaxes", "break_between_y")])
def test_other_tools_names_point_to_the_new_words(name, word):
    with pytest.raises(SimplydataError, match=word.replace("(", r"\(")):
        getattr(sdata.chart(example_frame("marks")), name)
