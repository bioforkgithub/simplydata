"""Charts phase, batch 2: new options on older chart words (approved by Manish on 2026-11-25).

y= on draw_histogram and draw_density, drawn_as= on draw_histogram (was steps=), in_halves= on draw_violins,
show= and error= on draw_dots, stacked="percent" on bars and areas, hole=, x= and y= on draw_pie, as_wires= and
with_height_lines= on draw_surface, value= / z= as one option, between= on the reference lines, title= and ticks= on
use_font_size, per_row= on the legend words and formula= on add_second_y. Each is compared with plain
matplotlib, seaborn or pandas doing the same, reading what was drawn."""

import io

import matplotlib.pyplot as plt
import numpy as np
import pytest
import seaborn as sns

import simplydata as sdata
from simplydata import SimplydataError
from conftest import example_frame


@pytest.fixture(autouse=True)
def _close():
    yield
    plt.close("all")


def axes_of(chart):
    return chart._render().axes[0]


def _mesh(ax):
    return [c for c in ax.collections if c.__class__.__name__ == "QuadMesh"]


def _paths(ax):
    return [p.vertices for c in ax.collections if hasattr(c, "get_paths") and c.__class__.__name__ != "PathCollection"
            for p in c.get_paths()]


# ---------------------------------------------------------------- two-way histogram and density
def test_histogram_with_y_is_seaborn_two_way_histplot_with_a_colour_bar():
    marks = example_frame("marks")
    chart = sdata.chart(marks).draw_histogram(x="hours", y="marks")
    ax = axes_of(chart)
    fig, plain = plt.subplots()
    sns.histplot(marks, x="hours", y="marks", bins=10, ax=plain)
    ours, theirs = _mesh(ax)[0].get_array(), _mesh(plain)[0].get_array()
    assert np.array_equal(np.ma.filled(ours, 0), np.ma.filled(theirs, 0))
    bar, = [a for a in chart._render().axes if a.get_label() == "<colorbar>"]
    assert bar.get_ylabel() == "count"


def test_histogram_with_y_refuses_the_one_way_options():
    marks = example_frame("marks")
    for options in ({"cumulative": True}, {"bin_width": 2}, {"drawn_as": "outline"}, {"with_bins": [0, 5, 10]}):
        with pytest.raises(SimplydataError, match="draw_histogram"):
            sdata.chart(marks).draw_histogram(x="hours", y="marks", **options)


def test_histogram_outline_is_the_new_name_of_steps(capsys):
    marks = example_frame("marks")
    new = axes_of(sdata.chart(marks).draw_histogram(x="marks", drawn_as="outline"))
    old = axes_of(sdata.chart(marks).draw_histogram(x="marks", steps=True))
    assert "drawn_as=" in capsys.readouterr().out
    assert np.allclose(new.lines[0].get_xydata(), old.lines[0].get_xydata())
    with pytest.raises(SimplydataError, match="drawn_as"):
        sdata.chart(marks).draw_histogram(x="marks", drawn_as="steps")


def test_density_with_y_is_seaborn_two_way_kdeplot():
    marks = example_frame("marks")
    ax = axes_of(sdata.chart(marks).draw_density(x="hours", y="marks"))
    fig, plain = plt.subplots()
    sns.kdeplot(marks, x="hours", y="marks", common_norm=False, ax=plain)
    ours, theirs = _paths(ax), _paths(plain)
    assert len(ours) == len(theirs) and all(np.allclose(a, b) for a, b in zip(ours, theirs))


# ---------------------------------------------------------------- violins in halves
def test_violins_in_halves_are_seaborn_split_violins():
    school = example_frame("school")
    ax = axes_of(sdata.chart(school).draw_violins(x="class", y="marks", colour="breakfast", in_halves=True))
    fig, plain = plt.subplots()
    sns.violinplot(school, x="class", y="marks", hue="breakfast", split=True, cut=0, gap=0.1, ax=plain)
    ours, theirs = _paths(ax), _paths(plain)
    assert len(ours) == len(theirs) and all(np.allclose(a, b) for a, b in zip(ours, theirs))


def test_violins_in_halves_need_groups_and_split_points_to_it(capsys):
    school = example_frame("school")
    with pytest.raises(SimplydataError, match="colour= a column with two groups"):
        sdata.chart(school).draw_violins(x="class", y="marks", in_halves=True)
    sdata.chart(school).draw_violins(x="class", y="marks", colour="breakfast", split=True)
    assert "in_halves=" in capsys.readouterr().out


# ---------------------------------------------------------------- dots of averages
def test_dots_with_show_are_seaborn_pointplot_without_a_line(capsys):
    marks = example_frame("marks")
    ax = axes_of(sdata.chart(marks).draw_dots(x="class", y="marks", show="average", error="standard error"))
    assert "standard error" in capsys.readouterr().out
    fig, plain = plt.subplots()
    sns.pointplot(marks, x="class", y="marks", estimator="mean", errorbar="se", linestyle="none", capsize=0.1,
                  ax=plain)
    assert len(ax.lines) == len(plain.lines)
    for a, b in zip(ax.lines, plain.lines):
        assert np.allclose(a.get_xydata(), b.get_xydata(), equal_nan=True)
    means = marks.groupby("class")["marks"].mean()
    assert ax.lines[0].get_ydata() == pytest.approx(means.to_numpy())


def test_dots_with_show_refuse_size_shape_and_count():
    marks = example_frame("marks")
    with pytest.raises(SimplydataError, match="size= and shape="):
        sdata.chart(marks).draw_dots(x="class", y="marks", show="median", size=5)
    with pytest.raises(SimplydataError, match='show="count"'):
        sdata.chart(marks).draw_dots(x="class", y="marks", show="count")


# ---------------------------------------------------------------- shares
def test_bars_stacked_percent_are_pandas_shares_of_each_stack():
    marks = example_frame("marks")
    chart = sdata.chart(marks).draw_bars(x="class", y="marks", colour="subject", stacked="percent")
    ax = axes_of(chart)
    wide = marks.groupby(["class", "subject"])["marks"].mean().unstack("subject")[["Maths", "Science", "English"]]
    shares = wide.div(wide.sum(axis=1), axis=0) * 100
    drawn = np.array([[p.get_height() for p in c.patches] for c in ax.containers]).T
    assert drawn == pytest.approx(shares.to_numpy())
    assert ax.get_ylabel() == "percent of marks"
    tops = chart.get_numbers_drawn().as_pandas().groupby("x")["high"].max()
    assert tops.to_numpy() == pytest.approx([100, 100, 100])


def test_area_stacked_percent_makes_each_x_100():
    growth = example_frame("growth")
    chart = sdata.chart(growth).draw_area(x="year", y="population", colour="country", stacked="percent")
    wide = growth.pivot_table(index="year", columns="country", values="population", aggfunc="mean")
    shares = wide.div(wide.sum(axis=1), axis=0) * 100
    drawn = chart.get_numbers_drawn().as_pandas()
    first = drawn[drawn["layer"] == 1]
    assert first["high"].to_numpy() == pytest.approx(shares[first["series"].iloc[0]].to_numpy())
    last = drawn[drawn["layer"] == drawn["layer"].max()]
    assert last["high"].to_numpy() == pytest.approx(np.full(len(shares), 100.0))
    assert axes_of(chart).get_ylabel() == "percent of population"


@pytest.mark.parametrize("stacked", ["half", 1, None])
def test_stacked_is_true_false_or_percent(stacked):
    with pytest.raises(SimplydataError, match="stacked="):
        sdata.chart(example_frame("marks")).draw_bars(x="class", y="marks", colour="subject", stacked=stacked)


# ---------------------------------------------------------------- pie
def test_pie_hole_is_a_ring_of_matplotlib_wedges():
    fruit = example_frame("fruit")
    ax = axes_of(sdata.chart(fruit).draw_pie(x="fruit", y="count", hole=0.4))
    sizes = fruit.groupby("fruit", sort=False)["count"].sum()
    fig, plain = plt.subplots()
    plain.pie(sizes, labels=sizes.index, autopct="%1.0f%%", startangle=90, counterclock=False,
              wedgeprops=dict(width=0.6), pctdistance=0.7)
    assert [w.width for w in ax.patches] == pytest.approx([0.6] * len(sizes))
    for a, b in zip(ax.patches, plain.patches):
        assert np.allclose(a.get_path().vertices, b.get_path().vertices)
    assert np.allclose(sorted(t.get_position() for t in ax.texts), sorted(t.get_position() for t in plain.texts))


def test_pie_x_and_y_are_labels_and_values():
    fruit = example_frame("fruit")
    new = axes_of(sdata.chart(fruit).draw_pie(x="fruit", y="count"))
    old = axes_of(sdata.chart(fruit).draw_pie(labels="fruit", values="count"))
    assert [w.theta2 for w in new.patches] == pytest.approx([w.theta2 for w in old.patches])
    with pytest.raises(SimplydataError, match="not both"):
        sdata.chart(fruit).draw_pie(labels="fruit", x="fruit")
    with pytest.raises(SimplydataError, match="hole="):
        sdata.chart(fruit).draw_pie(x="fruit", hole=1.2)


# ---------------------------------------------------------------- surfaces, contours, heatmaps
def test_surface_as_wires_is_plot_wireframe_without_a_colour_bar():
    island = example_frame("island")
    chart = sdata.chart(island).draw_surface(x="east", y="north", z="height", as_wires=True)
    ax = axes_of(chart)
    wide = island.pivot(index="north", columns="east", values="height")
    gx, gy = np.meshgrid(wide.columns, wide.index)
    fig = plt.figure()
    plain = fig.add_subplot(projection="3d")
    plain.plot_wireframe(gx, gy, wide.to_numpy())
    ours, = [c for c in ax.collections if c.__class__.__name__ == "Line3DCollection"]
    theirs, = plain.collections
    assert len(ours._segments3d) == len(theirs._segments3d)
    assert all(np.allclose(a, b) for a, b in zip(ours._segments3d, theirs._segments3d))
    assert not [a for a in chart._render().axes if a.get_label() == "<colorbar>"]


def test_surface_height_lines_are_contours_on_the_floor():
    island = example_frame("island")
    ax = axes_of(sdata.chart(island).draw_surface(x="east", y="north", z="height", with_height_lines=True))
    lines, = [c for c in ax.collections if "Contour" in c.__class__.__name__]
    assert len(lines.levels) >= 5
    # matplotlib keeps the 3D places of contour lines only in the private _3dverts_codes
    zs = np.concatenate([np.asarray(verts)[:, 2] for verts, _ in lines._3dverts_codes if len(verts)])
    assert np.allclose(zs, island["height"].min())


def test_value_and_z_are_one_option():
    island, weather = example_frame("island"), example_frame("weather")
    a = axes_of(sdata.chart(island).draw_contour(x="east", y="north", value="height"))
    b = axes_of(sdata.chart(island).draw_contour(x="east", y="north", z="height"))
    assert np.allclose(_paths(a)[0], _paths(b)[0])
    a = axes_of(sdata.chart(weather).draw_heatmap(x="month", y="city", z="rain"))
    b = axes_of(sdata.chart(weather).draw_heatmap(x="month", y="city", value="rain"))
    assert np.array_equal(_mesh(a)[0].get_array(), _mesh(b)[0].get_array())
    with pytest.raises(SimplydataError, match="not both"):
        sdata.chart(island).draw_surface(x="east", y="north", z="height", value="height")


# ---------------------------------------------------------------- reference lines between two values
def test_line_at_y_between_is_matplotlib_hlines():
    marks = example_frame("marks")
    ax = axes_of(sdata.chart(marks).draw_dots(x="hours", y="marks").draw_line_at_y(50, between=[2, 6], labelled="pass")
                 .draw_line_at_x(4, between=[20, 60]))
    segments = [np.asarray(c.get_segments()) for c in ax.collections if c.__class__.__name__ == "LineCollection"]
    assert np.allclose(segments[0], [[[2, 50], [6, 50]]]) and np.allclose(segments[1], [[[4, 20], [4, 60]]])
    assert [t.get_text().strip() for t in ax.texts] == ["pass"]


@pytest.mark.parametrize("between", [[6, 2], [2], "2, 6", [2, "x"]])
def test_between_is_low_then_high(between):
    with pytest.raises(SimplydataError, match="between="):
        sdata.chart().draw_line_at_y(50, between=between)


# ---------------------------------------------------------------- font sizes, legends, second y scale
def test_font_size_title_and_ticks():
    marks = example_frame("marks")
    ax = axes_of(sdata.chart(marks).draw_bars(x="class", y="marks").write_title_on_top("T")
                 .use_font_size(12, title=20, ticks=8))
    assert ax.title.get_fontsize() == 20
    assert ax.get_xticklabels()[0].get_fontsize() == 8 and ax.get_yticklabels()[0].get_fontsize() == 8
    assert ax.xaxis.label.get_fontsize() == 13  # the axis names keep the paper look's size
    with pytest.raises(SimplydataError, match="needs a size"):
        sdata.chart().use_font_size()
    with pytest.raises(SimplydataError, match="for title="):
        sdata.chart().use_font_size(title=-3)


@pytest.mark.parametrize("word", ["put_legend_at_bottom", "put_legend_at_top"])
def test_legend_per_row_is_ncols(word):
    weather = example_frame("weather")
    chart = sdata.chart(weather).draw_lines(x="month", y="temperature", colour="city")
    getattr(chart, word)(per_row=2)
    legend, = chart._render().legends
    assert legend._ncols == 2
    with pytest.raises(SimplydataError, match="per_row="):
        getattr(chart, word)(per_row=0)


def test_second_y_formula_is_a_secondary_y_axis():
    weather = example_frame("weather")
    ax = axes_of(sdata.chart(weather).draw_dots(x="rain", y="temperature")
                 .add_second_y(formula="y * 9 / 5 + 32", labelled="Temperature (°F)"))
    ax.figure.savefig(io.BytesIO(), format="png")
    right, = ax.child_axes
    low, high = ax.get_ylim()
    assert right.get_ylim() == pytest.approx((low * 9 / 5 + 32, high * 9 / 5 + 32))
    assert right.get_ylabel() == "Temperature (°F)"
    with pytest.raises(SimplydataError, match="not both"):
        sdata.chart(weather).add_second_y("rain", formula="y + 1")
