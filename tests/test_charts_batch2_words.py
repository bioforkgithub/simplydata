"""Charts phase, batch 2: the new chart words (approved by Manish on 2026-11-25).

Each word is checked against plain matplotlib, seaborn or NumPy doing the same job, by reading what was drawn
(chart.get_numbers_drawn() and the matplotlib objects), never by comparing pixels."""

import io

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator, NullLocator

import simplydata as sdata
from simplydata import SimplydataError
from simplydata._errors import MissingWordError
from conftest import example_frame


@pytest.fixture(autouse=True)
def _close():
    yield
    plt.close("all")


def axes_of(chart):
    return chart._render().axes[0]


def numbers(chart):
    return chart.get_numbers_drawn().as_pandas()


# ---------------------------------------------------------------- wind rose
def test_wind_rose_counts_are_numpy_histogram2d_of_the_drawn_sectors_and_bands():
    weather = example_frame("weather")
    ax = axes_of(sdata.chart(weather).draw_wind_rose(direction="wind_direction", speed="wind_speed"))
    turned = np.mod(weather["wind_direction"].to_numpy(float) + 15, 360)
    edges = MaxNLocator(nbins=5).tick_values(weather["wind_speed"].min(), weather["wind_speed"].max())
    counts, _, _ = np.histogram2d(turned, weather["wind_speed"], bins=[np.arange(0, 361, 30), edges])
    counts = counts[:, counts.any(axis=0)]
    drawn = np.array([[p.get_height() for p in c.patches] for c in ax.containers]).T
    assert np.array_equal(drawn, counts)
    bottoms = np.array([[p.get_y() for p in c.patches] for c in ax.containers]).T
    assert np.allclose(bottoms[:, 1:], np.cumsum(counts, axis=1)[:, :-1])  # stacked from the slowest band out
    assert ax.get_theta_offset() == pytest.approx(np.pi / 2) and ax.get_theta_direction() == -1
    assert [t.get_text() for t in ax.get_legend().get_texts()][0] == f"{edges[0]:g} to {edges[1]:g}"


def test_wind_rose_without_speed_is_one_count_per_sector():
    weather = example_frame("weather")
    ax = axes_of(sdata.chart(weather).draw_wind_rose(direction="wind_direction", every=45))
    turned = np.mod(weather["wind_direction"].to_numpy(float) + 22.5, 360)
    counts, _ = np.histogram(turned, bins=np.arange(0, 361, 45))
    heights = [p.get_height() for p in ax.containers[0].patches]
    assert heights == list(counts) and sum(heights) == len(weather)
    assert [p.get_x() + p.get_width() / 2 for p in ax.containers[0].patches] == pytest.approx(
        np.deg2rad(np.arange(0, 360, 45)))


@pytest.mark.parametrize("every", [7, 0, 100, "30", True])
def test_wind_rose_every_must_go_into_360(every):
    with pytest.raises(SimplydataError, match="every="):
        sdata.chart(example_frame("weather")).draw_wind_rose(direction="wind_direction", every=every)


def test_wind_rose_needs_numbers_and_a_round_chart():
    weather = example_frame("weather")
    with pytest.raises(SimplydataError, match="needs numbers"):
        sdata.chart(weather).draw_wind_rose(direction="city")
    with pytest.raises(SimplydataError, match="cannot share one chart"):
        sdata.chart(weather).draw_lines(x="month", y="rain").draw_wind_rose(direction="wind_direction")


# ---------------------------------------------------------------- rug lines
def test_rug_lines_are_seaborn_rugplot():
    marks = example_frame("marks")
    ax = axes_of(sdata.chart(marks).draw_density(x="marks").draw_rug_lines(x="marks"))
    fig, plain = plt.subplots()
    sns.rugplot(marks, x="marks", ax=plain)
    ours = [c for c in ax.collections if c.__class__.__name__ == "LineCollection"]
    theirs = [c for c in plain.collections if c.__class__.__name__ == "LineCollection"]
    assert len(ours) == len(theirs) == 1
    assert np.allclose(np.concatenate(ours[0].get_segments()), np.concatenate(theirs[0].get_segments()))
    assert sorted(numbers(sdata.chart(marks).draw_rug_lines(x="marks")).query("kind == 'segment'")["x"].unique()) \
        == pytest.approx(sorted(marks["marks"].unique()))


def test_rug_lines_need_a_column():
    with pytest.raises(SimplydataError, match="needs x="):
        sdata.chart(example_frame("marks")).draw_rug_lines()


# ---------------------------------------------------------------- arrow
def test_arrow_is_one_matplotlib_annotation_from_start_to_end():
    marks = example_frame("marks")
    chart = sdata.chart(marks).draw_dots(x="hours", y="marks").draw_arrow(start=[2, 40], end=[4, 60],
                                                                         labelled="more", colour="red")
    note, = axes_of(chart).texts
    assert note.xy == (4, 60) and note.xyann == (2, 40) and note.get_text() == "more"
    assert note.arrow_patch is not None and matplotlib.colors.same_color(note.arrow_patch.get_edgecolor(), "red")


@pytest.mark.parametrize("start, end", [([1, 2], [1, 2]), ([1], [2, 3]), ("1, 2", [2, 3]), ([1, None], [2, 3])])
def test_arrow_needs_two_different_places(start, end):
    with pytest.raises(SimplydataError, match="draw_arrow"):
        sdata.chart(example_frame("marks")).draw_arrow(start=start, end=end)


# ---------------------------------------------------------------- a chart inside
def test_chart_inside_is_an_inset_with_the_other_charts_bars():
    weather = example_frame("weather")
    detail = sdata.chart(weather).draw_bars(x="city", y="rain").write_title_on_top("Rain")
    ax = axes_of(sdata.chart(weather).draw_lines(x="month_number", y="temperature")
                 .put_chart_inside(detail, where="bottom right", size=0.35))
    inset, = ax.child_axes
    fig, plain = plt.subplots()
    sns.barplot(weather, x="city", y="rain", errorbar=None, ax=plain)
    assert [p.get_height() for p in inset.patches] == pytest.approx([p.get_height() for p in plain.patches])
    assert inset.get_title() == "Rain"
    assert inset.get_axes_locator()._bounds == pytest.approx([1 - 0.03 - 0.35, 0.03, 0.35, 0.35])


def test_chart_inside_refuses_itself_pages_round_charts_and_bad_places():
    weather = example_frame("weather")
    chart = sdata.chart(weather).draw_lines(x="month_number", y="temperature")
    with pytest.raises(SimplydataError, match="not the chart itself"):
        chart.put_chart_inside(chart)
    with pytest.raises(SimplydataError, match="needs a chart"):
        chart.put_chart_inside(sdata.put_side_by_side(sdata.chart(weather), sdata.chart(weather)))
    with pytest.raises(SimplydataError, match="round, 3D"):
        chart.put_chart_inside(sdata.chart(weather).draw_wind_rose(direction="wind_direction"))
    with pytest.raises(SimplydataError, match="where"):
        chart.put_chart_inside(sdata.chart(weather), where="middle")
    with pytest.raises(SimplydataError, match="size="):
        chart.put_chart_inside(sdata.chart(weather), size=0.9)


# ---------------------------------------------------------------- second x scale
def test_second_x_formula_is_a_secondary_axis_whose_way_back_is_brentq():
    weather = example_frame("weather")
    ax = axes_of(sdata.chart(weather).draw_dots(x="temperature", y="rain")
                 .add_second_x(formula="x * 9 / 5 + 32", labelled="Temperature (°F)"))
    ax.figure.savefig(io.BytesIO(), format="png")  # a second scale works out its range when it is drawn
    top, = ax.child_axes
    forward, back = top._functions
    low, high = ax.get_xlim()
    assert top.get_xlim() == pytest.approx((low * 9 / 5 + 32, high * 9 / 5 + 32))
    assert back(np.array([50.0, 68.0])) == pytest.approx([10.0, 20.0])
    assert top.get_xlabel() == "Temperature (°F)"


def test_second_scale_formula_must_only_go_up_or_down():
    chart = sdata.chart(example_frame("weather")).draw_dots(x="temperature", y="rain").add_second_x(formula="x ** 2")
    with pytest.raises(SimplydataError, match="only goes up"):
        chart._render()


def test_second_x_column_is_seaborn_lineplot_on_a_twin_axis():
    weather = example_frame("weather")
    ax = axes_of(sdata.chart(weather).draw_lines(x="month_number", y="temperature").add_second_x("wind_speed"))
    fig, plain = plt.subplots()
    sns.lineplot(weather, x="wind_speed", y="temperature", estimator="mean", errorbar=None, ax=plain)
    twin = [a for a in ax.figure.axes if a is not ax][0]
    assert np.allclose(twin.lines[0].get_xydata(), plain.lines[0].get_xydata())
    assert twin.get_xlabel() == "wind_speed"


def test_second_x_needs_a_column_or_a_formula():
    chart = sdata.chart(example_frame("weather"))
    with pytest.raises(SimplydataError, match="column name or formula="):
        chart.add_second_x()
    with pytest.raises(SimplydataError, match="not both"):
        chart.add_second_x("rain", formula="x + 1")


# ---------------------------------------------------------------- frame and ticks
def test_frame_and_tick_words_are_matplotlib_settings():
    marks = example_frame("marks")
    assert not axes_of(sdata.chart(marks).draw_dots(x="hours", y="marks").hide_frame()).axison
    ax = axes_of(sdata.chart(marks).draw_dots(x="hours", y="marks").hide_ticks_x())
    assert not any(t.label1.get_visible() for t in ax.xaxis.get_major_ticks())
    assert all(t.tick1line.get_markersize() == 0 for t in ax.xaxis.get_major_ticks())
    assert any(t.label1.get_visible() for t in ax.yaxis.get_major_ticks())
    ax = axes_of(sdata.chart(marks).draw_dots(x="hours", y="marks").hide_ticks_y())
    assert not any(t.label1.get_visible() for t in ax.yaxis.get_major_ticks())
    ax = axes_of(sdata.chart(marks).draw_dots(x="hours", y="marks").show_small_ticks_x().show_small_ticks_y())
    assert not isinstance(ax.xaxis.get_minor_locator(), NullLocator)
    assert not isinstance(ax.yaxis.get_minor_locator(), NullLocator)


def test_true_shape_and_square_are_set_aspect_and_set_box_aspect():
    island = example_frame("island")
    ax = axes_of(sdata.chart(island).draw_contour(x="east", y="north", z="height").use_true_shape())
    assert ax.get_aspect() == 1.0
    ax = axes_of(sdata.chart(example_frame("marks")).draw_dots(x="hours", y="marks").make_square())
    assert ax.get_box_aspect() == 1.0


# ---------------------------------------------------------------- colour bar
def _bars(chart):
    return [a for a in chart._render().axes if a.get_label() == "<colorbar>"]


@pytest.mark.parametrize("word, place", [("put_colour_bar_at_bottom", "bottom"), ("put_colour_bar_at_top", "top"),
                                         ("put_colour_bar_at_left", "left")])
def test_colour_bar_places_are_matplotlib_locations(word, place):
    chart = sdata.chart(example_frame("weather")).draw_heatmap(x="month", y="city", value="rain")
    getattr(chart, word)()
    bar, = _bars(chart)
    heat = chart._render().axes[0]
    box, main = bar.get_position(), heat.get_position()
    where = {"bottom": box.y1 <= main.y0, "top": box.y0 >= main.y1, "left": box.x1 <= main.x0}
    assert where[place]
    assert (bar.get_xlabel() if place in ("bottom", "top") else bar.get_ylabel()) == "rain"


def test_hide_colour_bar_removes_it_and_ticks_go_where_asked():
    weather = example_frame("weather")
    assert _bars(sdata.chart(weather).draw_heatmap(x="month", y="city", value="rain").hide_colour_bar()) == []
    chart = sdata.chart(weather).draw_heatmap(x="month", y="city", value="rain").put_ticks_colour_bar(
        0, 50, 100, labels=["dry", "wet", "very wet"])
    bar, = _bars(chart)
    assert list(bar.get_yticks()) == [0, 50, 100]
    assert [t.get_text() for t in bar.get_yticklabels()] == ["dry", "wet", "very wet"]


def test_colour_bar_words_need_a_colour_bar():
    chart = sdata.chart(example_frame("marks")).draw_dots(x="hours", y="marks").put_colour_bar_at_bottom()
    with pytest.raises(SimplydataError, match="needs a chart with a colour bar"):
        chart._render()
    with pytest.raises(SimplydataError, match="labels="):
        sdata.chart().put_ticks_colour_bar(0, 1, labels=["a"])


# ---------------------------------------------------------------- 3D
def test_lines_3d_are_axes3d_plot_through_the_rows_in_order():
    island = example_frame("island")
    ax = axes_of(sdata.chart(island).draw_lines_3d(x="east", y="north", z="height"))
    fig = Figure()
    plain = fig.add_subplot(projection="3d")
    plain.plot(island["east"], island["north"], island["height"])
    assert np.allclose(np.array(ax.lines[0].get_data_3d()), np.array(plain.lines[0].get_data_3d()))
    assert ax.get_zlabel() == "height"


def test_z_words_and_the_view_are_matplotlib_3d_settings():
    island = example_frame("island")
    chart = (sdata.chart(island).draw_surface(x="east", y="north", z="height").label_z("Height (m)")
             .set_range_z(-10, 150).put_ticks_z(0, 50, 100, labels=["sea", "hill", "top"])
             .look_from(height=20, around=45))
    ax = axes_of(chart)
    assert ax.get_zlabel() == "Height (m)" and ax.get_zlim() == (-10, 150)
    assert list(ax.get_zticks()) == [0, 50, 100]
    assert [t.get_text() for t in ax.get_zticklabels()] == ["sea", "hill", "top"]
    assert (ax.elev, ax.azim) == (20, 45)
    view = axes_of(sdata.chart(island).draw_surface(x="east", y="north", z="height").view_from(height=10, around=5))
    assert (view.elev, view.azim) == (10, 5)


def test_z_words_need_a_3d_chart():
    chart = sdata.chart(example_frame("marks")).draw_dots(x="hours", y="marks").label_z("z")
    with pytest.raises(SimplydataError, match="3D charts"):
        chart._render()
    with pytest.raises(SimplydataError, match="from -90 to 90"):
        sdata.chart().look_from(height=120)
    with pytest.raises(SimplydataError, match="low end must be smaller"):
        sdata.chart().set_range_z(5, 1)


# ---------------------------------------------------------------- what it shows
def test_say_what_it_shows_reads_the_drawn_chart(capsys):
    marks = example_frame("marks")
    chart = sdata.chart(marks).draw_bars(x="class", y="marks", colour="subject").write_title_on_top("Marks")
    text = chart.say_what_it_shows()
    assert text in capsys.readouterr().out
    ax = axes_of(chart)
    low, high = ax.get_ylim()
    assert '"Marks". It draws 9 bars.' in text
    assert 'x-axis "class", with the groups A, B, C' in text
    assert f'y-axis "marks", from {low:.4g} to {high:.4g}' in text
    assert "Legend (subject): Maths, Science, English." in text


def test_say_what_it_shows_names_the_colour_bar_and_z_axis():
    island = example_frame("island")
    text = sdata.chart(island).draw_surface(x="east", y="north", z="height").say_what_it_shows()
    assert 'z-axis "height"' in text and 'Colour bar "height": from -6 to 133.' in text


def test_describe_is_an_other_name_that_points_to_say_what_it_shows():
    with pytest.raises(MissingWordError, match=r"In simplydata this is chart\.say_what_it_shows\("):
        sdata.chart().describe
    with pytest.raises(MissingWordError, match=r"In simplydata this is chart\.draw_wind_rose\("):
        sdata.chart().windrose
