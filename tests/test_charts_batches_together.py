"""Charts phase: the words of batch 2 with the features of batch 1 (undo, black and white, read-back words,
say_what_it_shows), merged 2026-11-25."""

import re

import matplotlib
import pytest
from matplotlib.colors import to_hex

import simplydata as sdata
from simplydata.words.second_cues import HATCHES

matplotlib.use("Agg")


def _marks():
    return sdata.chart(sdata.get_example("marks"))


def _weather():
    return sdata.chart(sdata.get_example("weather"))


def _state(chart):
    return ([(s.name, repr(sorted(s.kwargs.items(), key=str))) for s in chart._steps],
            repr(sorted(chart._settings.items(), key=str)))


# ---------------------------------------------------------------- undo after batch-2 words
@pytest.mark.parametrize("make, word, name", [
    (lambda: _marks().draw_dots(x="hours", y="marks"), lambda c: c.add_second_x(formula="x * 60"), "add_second_x"),
    (lambda: _marks().draw_dots(x="hours", y="marks"), lambda c: c.draw_arrow(start=[1, 50], end=[3, 70]),
     "draw_arrow"),
    (lambda: _marks().draw_histogram(x="hours", y="marks"), lambda c: c.put_colour_bar_at_bottom(),
     "put_colour_bar_at_bottom"),
    (lambda: _marks().draw_histogram(x="hours", y="marks").put_ticks_colour_bar(0, 5),
     lambda c: c.put_ticks_colour_bar(0, 2, 4), "put_ticks_colour_bar"),
    (lambda: _weather(), lambda c: c.draw_wind_rose(direction="wind_direction", speed="wind_speed"),
     "draw_wind_rose"),
    (lambda: _marks(), lambda c: c.draw_lines_3d(x="hours", y="marks", z="height"), "draw_lines_3d"),
    (lambda: _marks().draw_lines_3d(x="hours", y="marks", z="height"), lambda c: c.look_from(20, 30), "look_from"),
    (lambda: _marks().draw_dots(x="hours", y="marks", colour="class"),
     lambda c: c.put_legend_at_bottom(per_row=2), "put_legend_at_bottom"),
    (lambda: _marks(), lambda c: c.draw_bars(x="class", y="marks", colour="subject", stacked="percent"),
     "draw_bars"),
])
def test_undo_takes_back_each_batch_2_word_and_names_it(make, word, name, capsys):
    chart = make()
    chart._render()
    before = _state(chart)
    word(chart)
    chart._render()
    capsys.readouterr()
    chart.undo()
    assert f"Undone: chart.{name}()" in capsys.readouterr().out
    assert _state(chart) == before
    chart._render()


# ---------------------------------------------------------------- black and white
def _bw(chart):
    return chart.use_style("black and white")._render().axes[0]


def test_black_and_white_wind_rose_bands_get_greys_and_patterns(capsys):
    ax = _bw(_weather().draw_wind_rose(direction="wind_direction", speed="wind_speed"))
    faces = {to_hex(p.get_facecolor()) for p in ax.patches}
    assert all(r == g == b for r, g, b in (matplotlib.colors.to_rgb(f) for f in faces))
    hatches = {p.get_hatch() for p in ax.patches}
    assert len(hatches) == len(faces) and None not in hatches
    assert all(h.get_hatch() for h in ax.get_legend().legend_handles)


def test_black_and_white_3d_lines_get_dashes_and_two_way_histogram_greys(capsys):
    ax = _bw(_marks().draw_lines_3d(x="hours", y="marks", z="height", colour="class"))
    styles = [line._dash_pattern for line in ax.get_lines()]
    assert len({repr(s) for s in styles}) == 3
    ax = _bw(_marks().draw_histogram(x="hours", y="marks"))
    assert ax.collections[0].get_cmap().name == "Greys"


def test_black_and_white_average_dots_get_shapes_and_use_shapes_works_on_them(capsys):
    ax = _bw(_marks().draw_dots(x="subject", y="marks", colour="class", show="average"))
    markers = {line.get_marker() for line in ax.get_lines() if line.get_marker() not in (None, "None", "")}
    assert len(markers) == 3
    ax = _marks().draw_dots(x="subject", y="marks", colour="class", show="average").use_shapes(
        "square", "diamond", "star")._render().axes[0]
    assert {line.get_marker() for line in ax.get_lines()} >= {"s", "D", "*"}


def test_black_and_white_percent_stacks_halves_and_donut_keep_patterns(capsys):
    ax = _bw(_marks().draw_bars(x="subject", y="marks", colour="class", stacked="percent"))
    assert {p.get_hatch() for p in ax.patches} == set(HATCHES[:3])
    table = sdata.get_example("marks").keep_rows_where("class", is_not_equal_to="C")
    ax = _bw(sdata.chart(table).draw_violins(x="subject", y="marks", colour="class", in_halves=True))
    assert {c.get_hatch() for c in ax.collections if c.get_hatch()} == set(HATCHES[:2])
    ax = _bw(sdata.chart(sdata.get_example("fruit")).draw_pie(labels="fruit", values="count", hole=0.4))
    assert all(p.get_hatch() for p in ax.patches)


def test_dark_patterns_are_white_after_the_black_edge(capsys):
    ax = _bw(_weather().draw_wind_rose(direction="wind_direction", speed="wind_speed"))
    for p in ax.patches:
        light = matplotlib.colors.to_rgb(p.get_facecolor())[0]
        assert to_hex(p.get_hatchcolor()) == ("#ffffff" if light < 0.5 else "#000000")
        assert to_hex(p.get_edgecolor()) == "#000000"


# ---------------------------------------------------------------- read-back words
def test_read_back_words_see_second_scales_colour_bars_and_z(capsys):
    scales = _marks().draw_dots(x="hours", y="marks").add_second_x(formula="x * 60", labelled="minutes") \
        .get_scales_drawn().as_pandas()
    second = scales[scales["scale"] == "second x"].iloc[0]
    assert second["name"] == "minutes" and second["low"] == pytest.approx(0.055 * 60, rel=0.01)
    chart = _marks().draw_histogram(x="hours", y="marks").put_colour_bar_at_bottom() \
        .put_ticks_colour_bar(0, 2, 4, labels=["none", "some", "many"])
    scales = chart.get_scales_drawn().as_pandas()
    bar = scales[scales["scale"] == "colour"].iloc[0]
    assert bar["tick words"] == "none, some, many"
    text = chart.get_text_drawn().as_pandas()
    assert "colour bar label" in set(text["part"])
    scales = _marks().draw_lines_3d(x="hours", y="marks", z="height").label_z("Height").set_range_z(100, 200) \
        .get_scales_drawn().as_pandas()
    z = scales[scales["scale"] == "z"].iloc[0]
    assert (z["name"], z["low"], z["high"]) == ("Height", 100, 200)


# ---------------------------------------------------------------- say_what_it_shows on batch-1 charts
def test_say_what_it_shows_names_letters_notes_legends_inside_and_second_cues(capsys):
    text = _marks().draw_bars(x="subject", y="marks", colour="class", hatched=True).write_letter("B") \
        .write_note("high", x=1, y=80, with_box=True).say_what_it_shows()
    assert 'Panel letter: "B".' in text and "Title" not in text
    assert "each class has its own pattern" in text
    assert 'write_note("high"): a note at x = 1, y = 80, in a box.' in text
    text = _weather().draw_lines(x="month_number", y="temperature", colour="city") \
        .put_legend_inside("top left", per_row=2).say_what_it_shows()
    assert "Legend (city) inside the chart, top left:" in text
    text = _marks().draw_dots(x="hours", y="marks", colour="class", hollow=True) \
        .use_shapes("circle", "square", "triangle").use_style("black and white").say_what_it_shows()
    assert "hollow dots" in text and "circle, square, triangle" in text and "black and white" in text


def test_say_what_it_shows_on_pages(capsys):
    a = _weather().draw_lines(x="month_number", y="temperature", colour="city")
    b = _marks().draw_bars(x="subject", y="marks", colour="class")
    c = _marks().draw_dots(x="hours", y="marks", colour="class")
    page = sdata.put_in_rows_and_columns([[a, a], [b, c]], with_letters=True)
    page.write_title_on_top("Three charts")
    text = page.say_what_it_shows()
    assert text.splitlines()[:2] == ['Title: "Three charts".', "A page of 3 charts, 2 rows and 2 columns."]
    assert "Chart A (row 1, columns 1 to 2):" in text and "Chart C (row 2, column 2):" in text
    assert re.search(r"Chart B \(row 2, column 1\):\n  draw_bars", text)
    text = sdata.put_side_by_side(b, c, with_one_legend=True).say_what_it_shows()
    assert "with one legend for the whole page" in text


# ---------------------------------------------------------------- options of both batches together
def test_put_legend_inside_per_row(capsys):
    ax = _weather().draw_lines(x="month_number", y="temperature", colour="city") \
        .put_legend_inside("top left", per_row=3)._render().axes[0]
    assert ax.get_legend()._ncols == 3
    with pytest.raises(sdata.SimplydataError, match="per_row="):
        _weather().draw_lines(x="month_number", y="temperature", colour="city").put_legend_inside(per_row=0)


def test_draw_bars_help_shows_average_and_percent_stacks_show_totals(capsys):
    sdata.help("draw_bars")
    assert re.search(r'show=\s+normally "average"', capsys.readouterr().out)
    _marks().draw_bars(x="class", y="marks", colour="subject", stacked="percent")._render()
    assert "Note" not in capsys.readouterr().out
    _marks().draw_bars(x="class", y="marks", colour="subject", stacked="percent", show="average")._render()
    assert "shares of the averages" in capsys.readouterr().out
