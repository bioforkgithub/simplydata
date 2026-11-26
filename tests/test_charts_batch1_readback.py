"""Charts phase, batch 1: reading a chart back (approved by Manish 2026-11-25).

get_numbers_drawn's two reader fixes (lines at named x positions, 3D surfaces), its colour columns, and the new
words get_text_drawn, get_scales_drawn and get_size. Every check compares what simplydata read back with plain
matplotlib or seaborn doing the same (Agg backend, no windows, no pixels).
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
import seaborn as sns
from matplotlib.colors import to_hex

import simplydata as sdata
from conftest import example_frame


@pytest.fixture(autouse=True)
def _close():
    yield
    plt.close("all")


def _rows(table, column, value):
    """The rows with that value, on a copy (table steps change the table itself)."""
    return table.make_copy().keep_rows_where(column, is_equal_to=value)


# ---------------------------------------------------------------- the two reader fixes
def test_lines_at_named_x_positions_are_read(capsys):
    """Error bars on dots at named groups used to stop get_numbers_drawn (the names could not become numbers).
    The bars read back are each class's average plus and minus its standard error (pandas, from the file)."""
    df = example_frame("marks")
    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="class", y="marks").draw_error_bars("standard error")
    bars = _rows(chart.get_numbers_drawn(), "kind", "error bar")
    groups = df.groupby("class", sort=False)["marks"]
    average, error = groups.mean(), groups.sem()
    assert list(bars.get_column("x")) == ["A", "B", "C"]
    assert list(bars.get_column("low")) == pytest.approx(list(average - error), rel=1e-9)
    assert list(bars.get_column("high")) == pytest.approx(list(average + error), rel=1e-9)


def test_a_surface_is_read_as_its_grid_of_points(capsys):
    df = example_frame("island")
    chart = sdata.chart(sdata.get_example("island")).draw_surface(x="east", y="north", z="height")
    drawn = _rows(chart.get_numbers_drawn(), "kind", "surface")
    # plain matplotlib: the same grid as plot_surface gets it
    wide = df.groupby(["north", "east"])["height"].mean().unstack()
    gx, gy = np.meshgrid(wide.columns, wide.index)
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    ax.plot_surface(gx, gy, wide.to_numpy(dtype=float))
    expected = pd.DataFrame({"x": gx.ravel(), "y": gy.ravel(), "z": wide.to_numpy(dtype=float).ravel()})
    expected = expected.sort_values(["y", "x"]).reset_index(drop=True)
    assert drawn.count_rows() == len(expected) == len(df)  # each grid point once
    assert drawn.get_column("x") == pytest.approx(expected["x"].to_numpy(dtype=float))
    assert drawn.get_column("y") == pytest.approx(expected["y"].to_numpy(dtype=float))
    assert drawn.get_column("value") == pytest.approx(expected["z"].to_numpy(dtype=float))


def test_a_second_y_axis_belongs_to_its_panel(capsys):
    chart = sdata.chart(sdata.get_example("weather")).draw_lines(x="month_number", y="temperature")
    chart.add_second_y("rain")
    drawn = chart.get_numbers_drawn()
    assert set(drawn.get_column("panel")) == {1}
    assert len(set(drawn.get_column("layer"))) == 2


# ---------------------------------------------------------------- the colour column
def test_bar_colours_are_the_drawn_colours(capsys):
    df = example_frame("marks")
    chart = sdata.chart(sdata.get_example("marks")).draw_bars(x="class", y="marks", colour="subject")
    drawn = chart.get_numbers_drawn()
    fig, ax = plt.subplots()
    order = list(pd.unique(df["subject"]))
    sns.barplot(df, x="class", y="marks", hue="subject", hue_order=order, errorbar=None, saturation=1,
                palette=sdata._style.COLOURS[:3], ax=ax)
    theirs = [to_hex(p.get_facecolor()) for c in ax.containers for p in c.patches]
    assert drawn.get_column("colour") == theirs


def test_a_named_colour_gets_its_name(capsys):
    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks", colour="blue")
    drawn = chart.get_numbers_drawn()
    assert set(drawn.get_column("colour")) == {"#0000ff"}
    assert set(drawn.get_column("colour name")) == {"blue"}


def test_heat_map_cells_get_their_colour_map_colours(capsys):
    chart = sdata.chart(sdata.get_example("weather")).draw_heatmap(x="month", y="city", value="rain")
    cells = _rows(chart.get_numbers_drawn(), "kind", "cell")
    values = np.asarray(cells.get_column("value"), dtype=float)
    cmap = plt.get_cmap("viridis")
    low, high = np.nanmin(values), np.nanmax(values)
    expected = [to_hex(cmap((v - low) / (high - low))) for v in values]
    assert cells.get_column("colour") == expected


# ---------------------------------------------------------------- get_text_drawn
def test_text_drawn_is_what_seaborn_writes(capsys):
    df = example_frame("marks")
    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks", colour="class")
    chart.write_title_on_top("More study, higher marks")
    text = chart.get_text_drawn()
    assert "Read" in capsys.readouterr().out
    fig, ax = plt.subplots()
    sns.scatterplot(df, x="hours", y="marks", hue="class", ax=ax)
    ax.set_title("More study, higher marks")
    assert _rows(text, "part", "title").get_column("text") == [ax.get_title()]
    assert _rows(text, "part", "x label").get_column("text") == [ax.get_xlabel()]
    assert _rows(text, "part", "y label").get_column("text") == [ax.get_ylabel()]
    assert _rows(text, "part", "legend entry").get_column("text") == [t.get_text() for t in ax.get_legend().get_texts()]
    assert _rows(text, "part", "legend title").get_column("text") == ["class"]
    assert text.get_column_names() == ["panel", "part", "text", "where"]


def test_text_drawn_names_notes_letters_captions_and_numbers(capsys):
    chart = sdata.chart(sdata.get_example("marks")).draw_bars(x="class", y="marks")
    chart.write_note("n = 54", where="top right").write_note("Best", x="A", y=70).write_letter("B")
    chart.write_caption_at_bottom("Made-up marks").write_numbers_on_bars()
    text = chart.get_text_drawn()
    notes = _rows(text, "part", "note")
    assert notes.get_column("text") == ["n = 54", "Best"]
    assert notes.get_column("where") == ["top right", "A, 70"]
    assert _rows(text, "part", "panel letter").get_column("text") == ["B"]
    assert _rows(text, "part", "caption").get_column("text") == ["Made-up marks"]
    assert _rows(text, "part", "number on bar").count_rows() == 3


def test_text_drawn_reads_the_ticks_shown(capsys):
    df = example_frame("marks")
    chart = sdata.chart(sdata.get_example("marks")).draw_bars(x="class", y="marks")
    text = chart.get_text_drawn()
    assert _rows(text, "part", "tick x").get_column("text") == list(pd.unique(df["class"]))


def test_text_drawn_reads_a_second_y_label_and_a_colour_bar(capsys):
    chart = sdata.chart(sdata.get_example("weather")).draw_lines(x="month_number", y="temperature")
    chart.add_second_y("rain")
    assert _rows(chart.get_text_drawn(), "part", "second y label").get_column("text") == ["rain"]
    heat = sdata.chart(sdata.get_example("island")).draw_contour(x="east", y="north", z="height")
    heat.label_colour_bar("Height (m)")
    assert _rows(heat.get_text_drawn(), "part", "colour bar label").get_column("text") == ["Height (m)"]


# ---------------------------------------------------------------- get_scales_drawn
def test_scales_drawn_are_matplotlibs_ranges(capsys):
    df = example_frame("marks")
    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks")
    scales = chart.get_scales_drawn()
    out = capsys.readouterr().out
    assert out.startswith("Read 2 scales on 1 chart: x ")
    fig, ax = plt.subplots()
    ax.scatter(df["hours"], df["marks"])
    assert scales.get_column("scale") == ["x", "y"]
    assert scales.get_column("low") == pytest.approx([ax.get_xlim()[0], ax.get_ylim()[0]])
    assert scales.get_column("high") == pytest.approx([ax.get_xlim()[1], ax.get_ylim()[1]])
    assert scales.get_column("kind") == ["numbers", "numbers"]
    assert scales.get_column("name") == ["hours", "marks"]


def test_scales_drawn_say_log_flipped_groups_and_dates(capsys):
    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks").use_log_scale_y().flip_x()
    scales = chart.get_scales_drawn()
    assert scales.get_cell_at(row=2, column="kind") == "log"
    assert scales.get_column("flipped") == [True, False]
    bars = sdata.chart(sdata.get_example("marks")).draw_bars(x="class", y="marks").get_scales_drawn()
    assert bars.get_cell_at(row=1, column="kind") == "groups"
    assert bars.get_cell_at(row=1, column="tick words") == "A, B, C"
    dates = sdata.chart(sdata.get_example("shop")).draw_lines(x="date", y="sales").get_scales_drawn()
    assert dates.get_cell_at(row=1, column="kind") == "dates"
    assert hasattr(dates.get_cell_at(row=1, column="low"), "year")


def test_scales_drawn_read_the_colour_scale(capsys):
    df = example_frame("island")
    chart = sdata.chart(sdata.get_example("island")).draw_contour(x="east", y="north", z="height")
    colour = _rows(chart.get_scales_drawn(), "scale", "colour")
    assert colour.count_rows() == 1
    assert colour.get_cell_at(row=1, column="colours") == "viridis"
    low, high = colour.get_cell_at(row=1, column="low"), colour.get_cell_at(row=1, column="high")
    assert low <= df["height"].min() and high >= df["height"].max()
    middle = sdata.chart(sdata.get_example("island")).draw_contour(x="east", y="north", z="height")
    middle.use_colour_scale("blue to red", middle=0, between=[-10, 140])  # a TwoSlopeNorm keeps its middle
    assert _rows(middle.get_scales_drawn(), "scale", "colour").get_cell_at(row=1, column="middle") == 0


def test_shared_ranges_on_split_charts(capsys):
    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks")
    chart.draw_one_chart_for_each_group_in("class")
    scales = chart.get_scales_drawn()
    first_y = _rows(_rows(scales, "panel", 1), "scale", "y")
    assert first_y.get_cell_at(row=1, column="shared with") == "2, 3"


# ---------------------------------------------------------------- get_size
def test_get_size_is_the_set_size(capsys):
    chart = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks")
    chart.set_size(width=17, height=12, unit="cm")
    # matplotlib writes whole pixels: 17 cm at 300 dots per inch is 2007.87, so 2007 pixels
    assert chart.get_size(unit="pixels") == (int(17 / 2.54 * 300), int(12 / 2.54 * 300))
    assert chart.get_size(unit="cm") == pytest.approx((17, 12), abs=0.01)
    assert "The chart is" in capsys.readouterr().out


def test_get_size_of_a_page(tmp_path, capsys):
    a = sdata.chart(sdata.get_example("marks")).draw_dots(x="hours", y="marks")
    b = sdata.chart(sdata.get_example("marks")).draw_bars(x="class", y="marks")
    page = sdata.put_side_by_side(a, b).set_size(width=12, height=4.5)
    assert page.get_size() == pytest.approx((12, 4.5), abs=0.01)
    assert "The page is" in capsys.readouterr().out
