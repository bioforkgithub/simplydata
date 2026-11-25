"""Charts phase, batch 1: fixes after the independent review of charts-1 (2026-11-25).

Each test failed before its fix. Expected values are written by hand or read independently: from plain matplotlib,
from pandas on the practice file, or from the saved file itself (Agg backend, no windows, no pixel comparisons).
"""

import struct

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.colors import to_hex, to_rgb

import simplydata as sdata
from conftest import example_frame
from simplydata.words.second_cues import HATCHES


@pytest.fixture(autouse=True)
def _close():
    yield
    plt.close("all")


def _rows(table, column, value):
    return table.make_copy().keep_rows_where(column, is_equal_to=value)


def _marks():
    return sdata.chart(sdata.get_example("marks"))


def _lightness(colour):
    r, g, b = to_rgb(colour)
    return 0.299 * r + 0.587 * g + 0.114 * b


# ---------------------------------------------------------------- 1. 3D dots coloured by a number
def test_3d_dots_coloured_by_a_number_keep_each_dots_colour(capsys):
    df = example_frame("marks")
    chart = _marks().draw_dots_3d(x="hours", y="height", z="marks", colour="marks")
    drawn = chart.get_numbers_drawn()
    values = np.asarray(drawn.get_column("value"), dtype=float)
    colours = list(drawn.get_column("colour"))
    assert colours[int(np.argmax(values))] == "#fde725"  # the top of viridis, written by hand
    assert colours[int(np.argmin(values))] == "#440154"  # the bottom of viridis
    viridis = plt.get_cmap("viridis")
    low, high = df["marks"].min(), df["marks"].max()
    assert colours == [to_hex(viridis((v - low) / (high - low))) for v in values]


def test_colours_that_cannot_be_matched_are_left_empty():
    from simplydata._numbers_drawn import _each_colour

    assert _each_colour([[0, 0, 1, 1], [1, 0, 0, 1]], 3) == ["", "", ""]
    assert _each_colour([[0, 0, 1, 1]], 2) == ["#0000ff", "#0000ff"]


def test_hollow_dots_coloured_by_a_number_keep_each_dots_colour(capsys):
    df = example_frame("marks")
    chart = _marks().draw_dots(x="hours", y="marks", colour="height", hollow=True).use_colour_scale("magma")
    colours = list(chart.get_numbers_drawn().get_column("colour"))
    magma = plt.get_cmap("magma")
    low, high = df["height"].min(), df["height"].max()
    assert colours == [to_hex(magma((v - low) / (high - low))) for v in df["height"]]


# ---------------------------------------------------------------- 2. one legend for a page
def test_one_legend_needs_the_same_legend_on_every_chart(capsys):
    a = _marks().draw_dots(x="hours", y="marks", colour="class")
    other_colours = _marks().draw_dots(x="height", y="marks", colour="class").use_colours("red", "green", "blue")
    with pytest.raises(sdata.SimplydataError, match="chart 2 shows its groups drawn another way"):
        sdata.put_side_by_side(a, other_colours, with_one_legend=True).save("never.png")
    cities = sdata.chart(sdata.get_example("weather")).draw_lines(x="month", y="temperature", colour="city")
    with pytest.raises(sdata.SimplydataError, match='chart 2 shows another legend name \\("city" against "class"\\)'):
        sdata.put_side_by_side(a, cities, with_one_legend=True).get_text_drawn()
    bars = _marks().draw_bars(x="subject", y="marks", colour="class")
    with pytest.raises(sdata.SimplydataError, match="drawn another way"):  # boxes are not dots
        sdata.put_side_by_side(a, bars, with_one_legend=True).get_text_drawn()


def test_one_legend_is_exactly_the_charts_legend(capsys):
    a = _marks().draw_dots(x="hours", y="marks", colour="class")
    b = _marks().draw_dots(x="height", y="marks", colour="class")
    fig = sdata.put_side_by_side(a, b, with_one_legend=True)._render()
    legend = fig.legends[0]
    assert legend.get_title().get_text() == "class"
    assert [t.get_text() for t in legend.get_texts()] == ["A", "B", "C"]
    shown = [to_hex(h.get_markerfacecolor() if hasattr(h, "get_markerfacecolor") else h.get_facecolors()[0])
             for h in legend.legend_handles]
    assert shown == ["#0072b2", "#e69f00", "#009e73"]  # Okabe-Ito, simplydata's first three colours


# ---------------------------------------------------------------- 3. black and white
def test_black_and_white_greys_are_readable_and_patterns_show(capsys):
    chart = _marks().draw_bars(x="subject", y="marks", colour="class").use_style("black and white")
    ax = chart._render().axes[0]
    bars = [p for c in ax.containers for p in c.patches]
    assert all(0.24 <= _lightness(p.get_facecolor()) <= 0.76 for p in bars)
    assert {to_hex(p.get_edgecolor()) for p in bars} == {"#000000"}
    for p in bars:  # the pattern is white on dark grey, black on light grey
        if hasattr(p, "get_hatchcolor"):
            expected = "#ffffff" if _lightness(p.get_facecolor()) < 0.5 else "#000000"
            assert to_hex(p.get_hatchcolor()) == expected
    assert len({p.get_hatch() for p in bars}) == 3
    lines = sdata.chart(sdata.get_example("weather")).draw_lines(x="month", y="temperature", colour="city")
    lines.use_style("black and white")
    assert all(0.24 <= _lightness(line.get_color()) <= 0.76 for line in lines._render().axes[0].lines[:3])


def test_black_and_white_boxes_violins_and_density_get_a_second_cue(capsys):
    boxes = _marks().draw_boxes(x="subject", y="marks", colour="class").use_style("black and white")
    ax = boxes._render().axes[0]
    filled = [p for p in ax.patches if p.get_hatch()]
    assert len({p.get_hatch() for p in filled}) == 3
    medians = [line for line in ax.lines if to_hex(line.get_color()) == "#ffffff"]
    assert len(medians) == 9 and all(line.get_path_effects() for line in medians)  # white with a black rim
    assert [h.get_hatch() for h in ax.get_legend().legend_handles] == HATCHES[:3]
    violins = _marks().draw_violins(x="subject", y="marks", colour="class").use_style("black and white")
    hatched = {c.get_hatch() for c in violins._render().axes[0].collections if c.get_hatch()}
    assert hatched == set(HATCHES[:3])
    density = _marks().draw_density(x="marks", colour="class").use_style("black and white")
    styles = {tuple(line._unscaled_dash_pattern[1] or ()) for line in density._render().axes[0].lines}
    assert len(styles) == 3


def test_black_and_white_colour_maps_are_grey(capsys):
    heat = sdata.chart(sdata.get_example("weather")).draw_heatmap(x="month", y="city", value="rain")
    heat.use_style("black and white")
    assert _rows(heat.get_scales_drawn(), "scale", "colour").get_cell_at(row=1, column="colours") == "Greys"
    contour = sdata.chart(sdata.get_example("island")).draw_contour(x="east", y="north", z="height")
    contour.use_style("greyscale")
    assert _rows(contour.get_scales_drawn(), "scale", "colour").get_cell_at(row=1, column="colours") == "Greys"
    surface = sdata.chart(sdata.get_example("island")).draw_surface(x="east", y="north", z="height")
    surface.use_style("black and white")
    assert surface._render().axes[0].collections[0].get_cmap().name == "Greys"
    two_sided = sdata.chart(sdata.get_example("island")).draw_contour(x="east", y="north", z="height")
    two_sided.use_colour_scale(middle=0).use_style("black and white")
    two_sided.get_numbers_drawn()
    assert "cannot show which side of the middle" in capsys.readouterr().out


def test_a_page_in_black_and_white_gets_the_patterns(capsys):
    a = _marks().draw_bars(x="subject", y="marks", colour="class")
    b = _marks().draw_dots(x="hours", y="marks")
    page = sdata.put_side_by_side(a, b).use_style("black and white")
    bars = [p for c in page._render().subfigs[0].axes[0].containers for p in c.patches]
    assert len({p.get_hatch() for p in bars}) == 3
    assert a._settings["style"] == "paper"  # the chart itself keeps its own style


# ---------------------------------------------------------------- 4. the middle of a colour scale
@pytest.mark.parametrize("between", [None, [0, 160]])
def test_the_middle_asked_for_is_read_back(between, capsys):
    chart = sdata.chart(sdata.get_example("weather")).draw_heatmap(x="month", y="city", value="rain")
    chart.use_colour_scale("blue to red", middle=50, between=between)
    colour = _rows(chart.get_scales_drawn(), "scale", "colour")
    assert colour.get_cell_at(row=1, column="middle") == 50


# ---------------------------------------------------------------- 5. log axes: the words as shown
def test_log_tick_words_are_plain_text_with_the_small_ticks(capsys):
    chart = _marks().draw_dots(x="hours", y="marks").use_log_scale_y()
    y = _rows(chart.get_scales_drawn(), "scale", "y")
    words = y.get_cell_at(row=1, column="tick words").split(", ")
    assert "$" not in ", ".join(words)
    assert "10²" in words
    assert {"30", "40", "60"} <= set(words) or {"3×10¹", "4×10¹", "6×10¹"} <= set(words)
    text = _rows(chart.get_text_drawn(), "part", "tick y")
    assert list(text.get_column("text")) == words


# ---------------------------------------------------------------- 6. a page title once
def test_a_page_title_is_read_once(capsys):
    a = _marks().draw_dots(x="hours", y="marks")
    b = _marks().draw_bars(x="class", y="marks")
    page = sdata.put_side_by_side(a, b).write_title_on_top("Page")
    text = page.get_text_drawn()
    assert list(_rows(text, "text", "Page").get_column("part")) == ["page title"]


# ---------------------------------------------------------------- 7. get_size is what save writes
def _png_size(path):
    data = path.read_bytes()
    return struct.unpack(">II", data[16:24])


def test_get_size_is_the_saved_files_size(tmp_path, capsys):
    chart = _marks().draw_dots(x="hours", y="marks", colour="class")
    chart.save(tmp_path / "plain.png")
    assert chart.get_size(unit="pixels") == _png_size(tmp_path / "plain.png")
    chart.set_size(800, 600, unit="pixels")
    chart.save(tmp_path / "pixels.png")
    assert _png_size(tmp_path / "pixels.png") == (800, 600)
    assert chart.get_size(unit="pixels") == (800, 600)
    assert chart.get_size(unit="inches") == pytest.approx((800 / 300, 600 / 300), abs=1e-4)
    chart.set_size(8, 6, unit="cm")
    chart.save(tmp_path / "cm.png")
    width, height = _png_size(tmp_path / "cm.png")
    assert chart.get_size(unit="cm") == pytest.approx((width / 300 * 2.54, height / 300 * 2.54), abs=1e-4)
    assert "(saved at 300 dots per inch)" in capsys.readouterr().out


# ---------------------------------------------------------------- 8. .eps and see-through parts
def test_eps_note_for_any_see_through_part(tmp_path, capsys):
    band = sdata.chart(sdata.get_example("weather"))
    band.draw_lines(x="month", y="temperature", colour="city", error="standard deviation")  # seaborn's bands
    band.save(tmp_path / "band.eps")
    assert "cannot hold see-through colours" in capsys.readouterr().out
    solid = _marks().draw_bars(x="class", y="marks")
    solid.save(tmp_path / "solid.eps")
    assert "see-through" not in capsys.readouterr().out


# ---------------------------------------------------------------- 9. heat map axes are groups
def test_heat_map_axes_are_groups(capsys):
    df = example_frame("weather")
    chart = sdata.chart(sdata.get_example("weather")).draw_heatmap(x="month", y="city", value="rain")
    scales = chart.get_scales_drawn()
    x, y = _rows(scales, "scale", "x"), _rows(scales, "scale", "y")
    assert x.get_cell_at(row=1, column="kind") == "groups"
    assert x.get_cell_at(row=1, column="tick words") == ", ".join(df["month"].unique())
    assert y.get_cell_at(row=1, column="kind") == "groups"
    assert y.get_cell_at(row=1, column="tick words") == ", ".join(df["city"].unique())
