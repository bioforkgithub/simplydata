"""Charts finishing PR (approved by Manish 2026-11-27): chart.as_matplotlib(), the door to matplotlib.

It gives the chart's matplotlib Figure (its charts are the Axes in fig.axes), as table.as_pandas() gives a pandas
table: a copy, so changing the Figure never changes the chart, and later words on the chart never change the Figure.
Each check compares with matplotlib itself: what the Figure holds is what matplotlib draws for the same data.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pytest  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

import simplydata as sdata  # noqa: E402
from simplydata import learn  # noqa: E402


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")


def _marks():
    return sdata.get_example("marks")


def test_as_matplotlib_gives_a_figure_with_the_dots_matplotlib_draws():
    table = _marks()
    chart = sdata.chart(table).draw_dots(x="hours", y="marks")
    fig = chart.as_matplotlib()
    assert isinstance(fig, Figure) and isinstance(fig.axes[0], Axes)
    ours = np.asarray(fig.axes[0].collections[0].get_offsets(), dtype=float)
    frame = table.as_pandas()
    theirs_fig, theirs_ax = plt.subplots()
    theirs = np.asarray(theirs_ax.scatter(frame["hours"], frame["marks"]).get_offsets(), dtype=float)
    np.testing.assert_array_equal(ours, theirs)
    assert fig.axes[0].get_xlabel() == "hours" and fig.axes[0].get_ylabel() == "marks"


def test_any_matplotlib_method_works_on_it_and_savefig_writes_the_picture(tmp_path):
    chart = sdata.chart(_marks()).draw_dots(x="hours", y="marks")
    fig = chart.as_matplotlib()
    ax = fig.axes[0]
    ax.annotate("most hours", xy=(9, 80), xytext=(6, 95), arrowprops={"arrowstyle": "->"})
    ax.set_title("Changed in matplotlib")
    fig.savefig(tmp_path / "chart.png", dpi=50)
    assert (tmp_path / "chart.png").stat().st_size > 1000
    assert [t.get_text() for t in ax.texts] == ["most hours"]


def test_it_is_a_copy_changing_it_never_changes_the_chart(tmp_path, capsys):
    chart = sdata.chart(_marks()).draw_dots(x="hours", y="marks")
    fig = chart.as_matplotlib()
    fig.axes[0].set_title("Only in matplotlib")
    fig.axes[0].annotate("a note", xy=(5, 50))
    text = chart.get_text_drawn()
    assert text.keep_rows_where("part", is_equal_to="title").count_rows() == 0
    assert chart.as_matplotlib() is not fig  # a new Figure each time
    assert chart.as_matplotlib().axes[0].get_title() == ""
    chart.save(tmp_path / "chart.png")
    assert chart._render() is not fig


def test_later_words_on_the_chart_never_change_the_figure():
    chart = sdata.chart(_marks()).draw_dots(x="hours", y="marks")
    fig = chart.as_matplotlib()
    chart.write_title_on_top("Added later")
    assert fig.axes[0].get_title() == ""
    assert chart.as_matplotlib().axes[0].get_title() == "Added later"


def test_a_second_y_axis_and_a_colour_bar_come_after_the_chart_in_fig_axes():
    lines = sdata.chart(sdata.get_example("weather")).draw_lines(x="month", y="temperature").add_second_y("rain")
    fig = lines.as_matplotlib()
    assert [ax.get_ylabel() for ax in fig.axes] == ["temperature", "rain"]
    heat = sdata.chart(sdata.get_example("weather")).draw_heatmap(x="month", y="city", value="rain")
    fig = heat.as_matplotlib()
    assert len(fig.axes) == 2 and fig.axes[1].get_label() == "<colorbar>"


def test_a_page_of_charts_gives_one_figure_with_every_chart():
    a = sdata.chart(_marks()).draw_dots(x="hours", y="marks")
    b = sdata.chart(_marks()).draw_bars(x="class", y="marks")
    page = sdata.put_side_by_side([a, b])
    fig = page.as_matplotlib()
    assert isinstance(fig, Figure) and len(fig.axes) == 2 and len(fig.subfigs) == 2


def test_a_chart_for_a_web_page_still_gives_the_matplotlib_figure():
    chart = sdata.chart(_marks()).draw_dots(x="hours", y="marks").show_when_pointing("name")
    fig = chart.as_matplotlib()
    assert isinstance(fig, Figure)
    assert len(fig.axes[0].collections[0].get_offsets()) == len(_marks().as_pandas())


def test_an_animation_gives_its_last_frame():
    growth = sdata.get_example("growth")
    chart = sdata.chart(growth).draw_bars(x="country", y="population").animate(over="year")
    fig = chart.as_matplotlib()
    last = growth.as_pandas()["year"].max()
    assert str(last) in " ".join(t.get_text() for t in fig.texts + fig.axes[0].texts + [fig.axes[0].title])


def test_as_matplotlib_is_a_word_with_help_an_example_and_its_group(capsys):
    assert "as_matplotlib" in dict(learn.GROUPS)["Start, show and save"]
    sdata.help("as_matplotlib")
    out = capsys.readouterr().out
    assert out.startswith("chart.as_matplotlib()")
    assert "fig.axes" in out and "copy" in out and "web page" in out
    assert "fig = chart.as_matplotlib()" in learn.HELP_EXAMPLES["as_matplotlib"]


def test_a_pairs_chart_has_the_door_too():
    """sdata.draw_all_pairs(...) gives a pairs chart; as_matplotlib gives its Figure, a copy as on a chart (it raised
    MissingWordError)."""
    pairs = sdata.draw_all_pairs(_marks(), columns=["hours", "marks"])
    fig = pairs.as_matplotlib()
    assert isinstance(fig, Figure) and len(fig.axes) >= 4  # 2 x 2 panels (and the twins of the histograms)
    dots = [np.asarray(c.get_offsets(), dtype=float) for ax in fig.axes for c in ax.collections if len(c.get_offsets())]
    frame = _marks().as_pandas()
    assert any(len(d) == len(frame) and sorted(d[:, 0]) == sorted(frame["marks"]) for d in dots)
    fig.suptitle("Only in matplotlib")
    assert pairs.as_matplotlib() is not fig
    assert pairs.as_matplotlib().get_suptitle() == ""
