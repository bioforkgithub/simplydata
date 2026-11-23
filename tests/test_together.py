"""Words built separately must work together."""

import pytest

import simplydata as sdata
from conftest import example_frame


def test_second_y_with_legend_bottom_keeps_both_series(marks):
    chart = sdata.chart(marks)
    chart.draw_lines(x="test", y="marks", colour="class")
    chart.add_second_y("height", drawn_as="lines", labelled="Height (cm)")
    chart.put_legend_at_bottom()
    fig = chart._render()
    labels = [t.get_text() for leg in fig.legends for t in leg.get_texts()]
    assert "A" in labels and "B" in labels
    assert any("height" in l.lower() for l in labels)
    assert all(ax.get_legend() is None for ax in fig.axes)


def test_full_sentence_renders(marks, tmp_path):
    chart = sdata.chart(marks)
    chart.draw_bars(x="name", y="marks", colour="class", error="sd")
    chart.write_title_on_top("My class marks")
    chart.label_x("Student")
    chart.label_y("Marks")
    chart.draw_line_at_y(50)
    chart.shade_between_y(40, 60)
    chart.set_range_y(0, 110)
    chart.write_numbers_on_bars()
    chart.write_caption_at_bottom("Made-up data")
    chart.put_legend_on_right()
    chart.use_style("school")
    chart.save(tmp_path / "all.png")
    assert (tmp_path / "all.png").stat().st_size > 0


def test_page_of_different_charts(marks, tmp_path):
    a = sdata.chart(marks).draw_bars(x="name", y="marks").write_title_on_top("Bars")
    b = sdata.chart(marks).draw_dots(x="height", y="marks").fit_line(with_confidence_band=True).write_title_on_top("Fit")
    c = sdata.chart(marks).draw_histogram(x="marks").write_title_on_top("Spread")
    d = sdata.chart(marks).draw_heatmap(x="name", y="test", value="marks", with_numbers=True)
    sdata.put_in_rows_and_columns(a, b, c, d, per_row=2).write_title_on_top("Everything").save(tmp_path / "page.png")
    assert (tmp_path / "page.png").stat().st_size > 0


def test_grid_with_letters_labels_each_chart(tmp_path):
    marks, weather = example_frame("marks"), example_frame("weather")
    a = sdata.chart(marks).draw_bars(x="class", y="marks")
    b = sdata.chart(weather).draw_lines(x="month", y="rain")
    c = sdata.chart(marks).draw_histogram(x="marks")
    page = sdata.put_in_rows_and_columns(a, b, c, per_row=2, with_letters=True)
    fig = page._render()
    assert [ax.get_title(loc="left") for ax in fig.axes if ax.get_title(loc="left")] == ["A", "B", "C"]
    page.save(tmp_path / "grid.png")
    assert (tmp_path / "grid.png").stat().st_size > 0
    fig = sdata.put_side_by_side(a, b)._render()
    assert not [ax for ax in fig.axes if ax.get_title(loc="left")]  # no letters unless asked


def test_one_above_other_with_letters(tmp_path):
    marks = example_frame("marks")
    a = sdata.chart(marks).draw_boxes(x="class", y="marks")
    b = sdata.chart(marks).draw_dots(x="hours", y="marks")
    fig = sdata.put_one_above_other(a, b, with_letters=True)._render()
    assert [ax.get_title(loc="left") for ax in fig.axes if ax.get_title(loc="left")] == ["A", "B"]


def test_page_letters_must_be_true_or_false():
    a = sdata.chart(sdata.get_example("marks")).draw_bars(x="class", y="marks")
    with pytest.raises(sdata.SimplydataError, match="letters=True or letters=False"):
        sdata.put_side_by_side(a, a, with_letters="yes")
    with pytest.raises(sdata.SimplydataError, match="letters=True or letters=False"):
        sdata.put_in_rows_and_columns(a, a, with_letters=1)


def _overlaps(a, b):
    return not (a.x1 <= b.x0 or b.x1 <= a.x0 or a.y1 <= b.y0 or b.y1 <= a.y0)


@pytest.mark.parametrize("title", [None, "Marks per class"])
def test_letter_does_not_cover_the_panel_titles_of_a_split_chart(title):
    marks = example_frame("marks")
    split = sdata.chart(marks).draw_bars(x="name", y="marks").draw_one_chart_for_each_group_in("class")
    if title:
        split.write_title_on_top(title)
    single = sdata.chart(marks).draw_dots(x="hours", y="marks")
    page = sdata.put_side_by_side(split, single, with_letters=True).set_size(8, 3)
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    fig = page._render()
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    letters = {id(t): t for sub in fig.subfigs for t in [*sub.texts, getattr(sub, "_suptitle", None)]
               if t is not None and t.get_text() == "A"}  # a suptitle is also one of the texts
    letters = list(letters.values())
    assert len(letters) == 1
    box = letters[0].get_window_extent(renderer)
    panel_titles = [ax.title.get_window_extent(renderer) for ax in fig.axes if ax.get_title()]
    assert panel_titles and not any(_overlaps(box, t) for t in panel_titles)
    assert [ax.get_title(loc="left") for ax in fig.axes if ax.get_title(loc="left")] == ["B"]


def test_page_cannot_be_saved_as_gif(tmp_path):
    marks = example_frame("marks")
    a = sdata.chart(marks).draw_bars(x="class", y="marks")
    with pytest.raises(sdata.SimplydataError, match="cannot be saved as .gif"):
        sdata.put_side_by_side(a, a).save(tmp_path / "page.gif")
