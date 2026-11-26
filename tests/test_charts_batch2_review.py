"""Charts phase, batch 2: fixes after the independent review of 2026-11-25.

Every expected value here is written out by hand (from the small tables in the tests, or from the practice tables'
known groups), not worked out again with the steps the chart words use."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from conftest import example_frame


@pytest.fixture(autouse=True)
def _close():
    yield
    plt.close("all")


def axes_of(chart):
    return chart._render().axes[0]


def heights(ax):
    """Bar heights, stack by stack (rows: x places, columns: groups)."""
    return np.array([[p.get_height() for p in c.patches] for c in ax.containers]).T


# ---------------------------------------------------------------- 1. say_what_it_shows describes the steps
def test_lines_with_groups_are_three_lines_not_their_points():
    text = sdata.chart(example_frame("weather")).draw_lines(x="month_number", y="temperature",
                                                            colour="city").say_what_it_shows()
    assert "3 lines, one for each city: Sunnyvale, Rainbridge, Frostby" in text
    assert "36" not in text and "12 lines" not in text


def test_bars_with_error_bars_name_the_error_and_count_no_lines():
    text = sdata.chart(example_frame("marks")).draw_bars(x="class", y="marks", error="standard error") \
        .say_what_it_shows()
    assert 'draw_bars(x="class", y="marks")' in text
    assert 'each bar is the average of "marks"' in text
    assert "error bars show the standard error of the average" in text
    assert "lines" not in text and "3 bars" not in text
    assert 'x-axis "class", with the names A, B, C' in text


@pytest.mark.parametrize("word, said, never", [
    ("draw_boxes", "boxes (the line is the median", ("shapes", "dot", "lines")),
    ("draw_violins", "violins (shapes that are wide", ("bands", "lines", "15")),
])
def test_boxes_and_violins_are_one_step_not_their_pieces(word, said, never):
    text = getattr(sdata.chart(example_frame("marks")), word)(x="class", y="marks").say_what_it_shows()
    assert f'{word}(x="class", y="marks"): {said}' in text
    for piece in never:
        assert piece not in text


def test_heatmap_axes_are_the_names_along_them():
    text = sdata.chart(example_frame("weather")).draw_heatmap(x="month", y="city", value="rain").say_what_it_shows()
    assert 'x-axis "month", with the names Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec' in text
    assert 'y-axis "city", with the names Sunnyvale, Rainbridge, Frostby' in text
    assert "from 0 to 12" not in text
    assert 'Colour bar "rain": from 9 to 155.' in text  # the driest and the wettest month in the weather table


def test_wind_rose_is_one_step_with_its_bands_and_no_bar_count():
    table = pd.DataFrame({"d": [0, 90, 90, 180], "s": [1, 2, 3, 4]})
    text = sdata.chart(table).draw_wind_rose(direction="d", speed="s").say_what_it_shows()
    assert text.startswith('draw_wind_rose(direction="d", speed="s"): bars round a compass')
    assert "one bar for every 30 degrees" in text
    assert 'stacked by bands of "s"' in text
    assert "12" not in text and "bars," not in text


def test_scatter_with_colour_and_histogram():
    marks = example_frame("marks")
    text = sdata.chart(marks).draw_dots(x="hours", y="marks", colour="class").say_what_it_shows()
    assert "dots; one colour for each class: A, B, C." in text
    text = sdata.chart(marks).draw_histogram(x="marks").say_what_it_shows()
    assert "a histogram: bars that count the values in ranges; the height of a bar is the count." in text
    assert "10 bars" not in text


def test_lines_on_top_are_said_once():
    text = (sdata.chart(example_frame("marks")).draw_dots(x="hours", y="marks").draw_line_at_y(50, between=[2, 6])
            .say_what_it_shows())
    assert "draw_line_at_y(50): a straight line at y = 50 from 2 to 6." in text


# ---------------------------------------------------------------- 2. stacked="percent"
def test_percent_stacks_refuse_values_below_zero():
    table = pd.DataFrame({"g": ["a", "a", "b", "b"], "s": ["p", "q", "p", "q"], "v": [-5, 10, 3, 3]})
    with pytest.raises(SimplydataError, match=r'"v" has 1 of them \(smallest: -5\)'):
        sdata.chart(table).draw_bars(x="g", y="v", colour="s", stacked="percent")
    with pytest.raises(SimplydataError, match="below 0"):
        sdata.chart(table).draw_area(x="g", y="v", colour="s", stacked="percent")


def test_percent_stack_with_a_total_of_zero_is_drawn_empty_with_a_note(capsys):
    table = pd.DataFrame({"g": ["a", "a", "b", "b"], "s": ["p", "q", "p", "q"], "v": [10, 30, 0, 0]})
    ax = axes_of(sdata.chart(table).draw_bars(x="g", y="v", colour="s", stacked="percent"))
    assert "the total of b is 0, so its stack is drawn empty" in capsys.readouterr().out
    drawn = heights(ax)
    assert drawn[0] == pytest.approx([25, 75])  # 10 and 30 of 40
    assert not np.nansum(drawn[1])


def test_percent_stack_counts_a_missing_group_as_zero_and_says_so(capsys):
    table = pd.DataFrame({"g": ["a", "a", "b"], "s": ["p", "q", "p"], "v": [30, 10, 5]})
    ax = axes_of(sdata.chart(table).draw_bars(x="g", y="v", colour="s", stacked="percent"))
    assert "1 place where a group has no value counted as 0 %" in capsys.readouterr().out
    assert heights(ax) == pytest.approx(np.array([[75, 25], [100, 0]]))


def test_percent_area_counts_a_missing_group_as_zero_and_says_so(capsys):
    table = pd.DataFrame({"g": [1, 1, 2, 3, 3], "s": ["p", "q", "p", "p", "q"], "v": [30, 10, 5, 20, 20]})
    chart = sdata.chart(table).draw_area(x="g", y="v", colour="s", stacked="percent")
    drawn = chart.get_numbers_drawn().as_pandas()
    assert "1 place where a group has no value counted as 0 %" in capsys.readouterr().out
    p = drawn[drawn["series"] == "p"]
    assert p["high"].to_numpy() == pytest.approx([75, 100, 50])
    assert axes_of(chart).get_ylabel() == "percent of total v"


def test_percent_bars_are_shares_of_totals_unless_averages_are_asked_for(capsys):
    # group p has three rows of 10 (total 30, average 10); group q one row of 30 (total 30, average 30)
    table = pd.DataFrame({"g": ["a"] * 4, "s": ["p", "p", "p", "q"], "v": [10, 10, 10, 30]})
    ax = axes_of(sdata.chart(table).draw_bars(x="g", y="v", colour="s", stacked="percent"))
    assert heights(ax)[0] == pytest.approx([50, 50])
    assert ax.get_ylabel() == "percent of total v"
    assert "shares of the" not in capsys.readouterr().out
    ax = axes_of(sdata.chart(table).draw_bars(x="g", y="v", colour="s", stacked="percent", show="average"))
    assert "shares of the averages" in capsys.readouterr().out
    assert heights(ax)[0] == pytest.approx([25, 75])
    assert ax.get_ylabel() == "percent of average v"


# ---------------------------------------------------------------- 3. violins in halves need two groups
def test_violins_in_halves_need_exactly_two_groups():
    table = pd.DataFrame({"c": ["A"] * 6, "g": ["x", "y", "z"] * 2, "v": [1, 2, 3, 4, 5, 6]})
    with pytest.raises(SimplydataError, match='"g" has 3: x, y, z'):
        sdata.chart(table).draw_violins(x="c", y="v", colour="g", in_halves=True)
    one = pd.DataFrame({"c": ["A"] * 4, "g": ["x"] * 4, "v": [1, 2, 3, 4]})
    with pytest.raises(SimplydataError, match='"g" has 1: x'):
        sdata.chart(one).draw_violins(x="c", y="v", colour="g", in_halves=True)


# ---------------------------------------------------------------- 4. dots of averages keep number spacing
def test_dots_of_averages_keep_the_spacing_of_number_x():
    table = pd.DataFrame({"h": [1, 1, 2, 2, 10, 10], "m": [1, 3, 3, 5, 5, 7]})
    ax = axes_of(sdata.chart(table).draw_dots(x="h", y="m", show="average"))
    assert list(ax.lines[0].get_xdata()) == [1, 2, 10]
    assert list(ax.lines[0].get_ydata()) == [2, 4, 6]
    words = pd.DataFrame({"h": ["one", "one", "two", "ten"], "m": [1, 3, 4, 6]})
    ax = axes_of(sdata.chart(words).draw_dots(x="h", y="m", show="average"))
    assert list(ax.lines[0].get_xdata()) == [0, 1, 2]  # names stay groups, side by side


# ---------------------------------------------------------------- 5. wind rose edges and speeds
def test_wind_rose_sectors_at_their_edges():
    # every=30: the north bar holds 345 up to (not including) 15 degrees; 15 starts the 30-degree bar
    table = pd.DataFrame({"d": [0, 14.9, 15, 344.9, 345, 360]})
    ax = axes_of(sdata.chart(table).draw_wind_rose(direction="d"))
    found = {round(np.rad2deg(p.get_x() + p.get_width() / 2)) % 360: p.get_height() for p in ax.patches}
    assert found == {0: 4, 30: 1, 60: 0, 90: 0, 120: 0, 150: 0, 180: 0, 210: 0, 240: 0, 270: 0, 300: 0, 330: 1}


def test_wind_rose_refuses_negative_speeds_and_notes_empty_rows(capsys):
    with pytest.raises(SimplydataError, match=r'speeds of 0 or more, but "s" has 1 below 0 \(smallest: -50\)'):
        sdata.chart(pd.DataFrame({"d": [0, 90], "s": [3, -50]})).draw_wind_rose(direction="d", speed="s")
    table = pd.DataFrame({"d": [0, 90, np.nan, 200], "s": [1, 2, 3, np.nan]})
    sdata.chart(table).draw_wind_rose(direction="d", speed="s")._render()
    assert '2 rows with empty "d" or "s" were left out' in capsys.readouterr().out
