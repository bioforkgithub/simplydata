"""Charts phase, batch 1 (approved by Manish 2026-11-25): the new chart words and options, checked against plain
matplotlib and seaborn by reading back what was drawn (Agg backend, no windows, no pixel comparisons).

put_legend_inside, put_in_rows_and_columns with rows as lists (widths=, heights=), with_one_legend=, write_letter,
write_note(where=, with_box=, with_curved_arrow=), hatched=, hollow=, dashed=, dotted=, use_shapes,
use_style("black and white"), use_colours sets, save(see_through=True), .eps, fonts kept as text, undo, and the
draw_ names of the twelve chart words (decision D11).
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
import seaborn as sns
from matplotlib.colors import to_hex

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


def _drawn(chart):
    """The matplotlib figure the chart draws, to read its artists."""
    return chart._render()


# ---------------------------------------------------------------- legends
@pytest.mark.parametrize("where, loc", [("top left", "upper left"), ("bottom right", "lower right"),
                                        ("middle", "center"), ("best", "best")])
def test_put_legend_inside_is_seaborns_move_legend(where, loc, capsys):
    df = example_frame("weather")
    chart = sdata.chart(sdata.get_example("weather")).draw_lines(x="month", y="temperature", colour="city")
    chart.put_legend_inside(where)
    ours = _drawn(chart).axes[0].get_legend()
    fig, ax = plt.subplots()
    sns.lineplot(df, x="month", y="temperature", hue="city", ax=ax)
    sns.move_legend(ax, loc)
    theirs = ax.get_legend()
    assert ours._loc == theirs._loc
    assert [t.get_text() for t in ours.get_texts()] == [t.get_text() for t in theirs.get_texts()]
    assert ours.get_title().get_text() == theirs.get_title().get_text()
    assert not _drawn(chart).legends  # inside the chart, not beside it
    text = chart.get_text_drawn()
    assert set(_rows(text, "part", "legend entry").get_column("where")) == {f"inside {where}"}


def test_put_legend_inside_takes_the_place_of_put_legend_at_bottom(capsys):
    chart = _marks().draw_dots(x="hours", y="marks", colour="class").put_legend_at_bottom()
    chart.put_legend_inside("top left")
    assert _drawn(chart).axes[0].get_legend()._loc == 2
    chart.show_legend()  # back to the usual place
    assert _drawn(chart).axes[0].get_legend()._loc == 0
    with pytest.raises(sdata.SimplydataError, match="top left"):
        chart.put_legend_inside("upper left")


def test_with_one_legend_shows_each_group_once(capsys):
    a = _marks().draw_dots(x="hours", y="marks", colour="class")
    b = _marks().draw_dots(x="height", y="marks", colour="class")
    page = sdata.put_side_by_side(a, b, with_one_legend=True)
    fig = page._render()
    assert len(fig.legends) == 1
    assert [t.get_text() for t in fig.legends[0].get_texts()] == ["A", "B", "C"]
    assert all(ax.get_legend() is None for sub in fig.subfigs for ax in sub.axes)
    text = page.get_text_drawn()
    assert _rows(text, "part", "legend entry").get_column("text") == ["A", "B", "C"]
    assert set(_rows(text, "part", "legend entry").get_column("panel")) == {0}


# ---------------------------------------------------------------- pages with rows as lists
def _plain_layout(widths=None, heights=None):
    """Plain matplotlib: chart a across the top row, b and c under it (GridSpec slices of sub-figures)."""
    from matplotlib.figure import Figure
    from matplotlib.gridspec import GridSpec

    fig = Figure(figsize=(12, 9), layout="constrained")
    grid = GridSpec(2, 2, figure=fig, width_ratios=widths, height_ratios=heights, left=0, right=1, bottom=0, top=1)
    subs = [fig.add_subfigure(grid[0, :]), fig.add_subfigure(grid[1, 0]), fig.add_subfigure(grid[1, 1])]
    for sub in subs:
        sub.add_subplot()
    fig.draw_without_rendering()
    return [tuple(np.round(sub.bbox.bounds, 3)) for sub in subs]


def test_rows_as_lists_span_cells(capsys):
    a = _marks().draw_dots(x="hours", y="marks")
    b = _marks().draw_bars(x="class", y="marks")
    c = _marks().draw_boxes(x="class", y="marks")
    page = sdata.put_in_rows_and_columns([[a, a], [b, c]], heights=[2, 1], widths=[2, 1])
    page.set_size(width=12, height=9)
    fig = page._render()
    fig.draw_without_rendering()
    ours = [tuple(np.round(sub.bbox.bounds, 3)) for sub in fig.subfigs]
    assert ours == _plain_layout(widths=[2, 1], heights=[2, 1])
    assert page.get_numbers_drawn().get_column("panel").find_biggest() == 3


def test_rows_as_lists_are_checked(capsys):
    a, b, c = (_marks().draw_dots(x="hours", y="marks") for _ in range(3))
    with pytest.raises(sdata.SimplydataError, match="per_row"):
        sdata.put_in_rows_and_columns([[a, a], [b, c]], per_row=2)
    with pytest.raises(sdata.SimplydataError, match="rectangle"):
        sdata.put_in_rows_and_columns([[a, b], [c, a]])
    with pytest.raises(sdata.SimplydataError, match="same number"):
        sdata.put_in_rows_and_columns([[a, b], [c]])
    with pytest.raises(sdata.SimplydataError, match="heights="):
        sdata.put_in_rows_and_columns([[a, b], [c, None]], heights=[1])
    page = sdata.put_in_rows_and_columns([a, b], [c, None])  # rows given one by one; None leaves a place empty
    assert len(page._render().subfigs) == 3


def test_plain_grids_take_widths_too(capsys):
    a, b = _marks().draw_dots(x="hours", y="marks"), _marks().draw_bars(x="class", y="marks")
    fig = sdata.put_in_rows_and_columns(a, b, widths=[3, 1])._render()
    fig.draw_without_rendering()
    first, second = (sub.bbox.width for sub in fig.subfigs)
    assert first / second == pytest.approx(3, rel=1e-6)


# ---------------------------------------------------------------- letters and notes
def test_write_letter_is_a_bold_left_title(capsys):
    chart = _marks().draw_dots(x="hours", y="marks").write_title_on_top("Marks").write_letter("B")
    ax = _drawn(chart).axes[0]
    fig, plain = plt.subplots()
    plain.set_title("B", loc="left", fontweight="bold")
    assert ax._left_title.get_text() == plain._left_title.get_text() == "B"
    assert ax._left_title.get_fontweight() == "bold"
    assert ax.get_title() == "Marks"
    right = _marks().draw_dots(x="hours", y="marks").write_letter("C", where="top right")
    assert _drawn(right).axes[0]._right_title.get_text() == "C"


def test_write_note_at_a_fixed_place_with_a_box(capsys):
    chart = _marks().draw_dots(x="hours", y="marks").write_note("n = 54", where="bottom right", with_box=True)
    ax = _drawn(chart).axes[0]
    note = ax.texts[0]
    fig, plain = plt.subplots()
    theirs = plain.text(0.98, 0.02, "n = 54", transform=plain.transAxes, ha="right", va="bottom")
    assert note.get_position() == theirs.get_position()
    assert note.get_transform() == ax.transAxes
    assert (note.get_ha(), note.get_va()) == (theirs.get_ha(), theirs.get_va())
    assert note.get_bbox_patch().get_edgecolor()[3] == 1  # a frame is drawn
    with pytest.raises(sdata.SimplydataError, match="not both"):
        _marks().write_note("n", x=1, y=2, where="top left")
    with pytest.raises(sdata.SimplydataError, match="arrow"):
        _marks().write_note("n", where="top left", with_arrow=True)


def test_write_note_with_a_curved_arrow(capsys):
    chart = _marks().draw_dots(x="hours", y="marks").write_note("Top", x=9, y=95, with_curved_arrow=True)
    note = _drawn(chart).axes[0].texts[0]
    assert note.arrow_patch is not None
    assert "rad=0.3" in str(note.arrowprops.get("connectionstyle"))
    straight = _marks().draw_dots(x="hours", y="marks").write_note("Top", x=9, y=95, with_arrow=True)
    assert "connectionstyle" not in _drawn(straight).axes[0].texts[0].arrowprops


# ---------------------------------------------------------------- second cues
def test_hatched_bars_get_one_pattern_per_group(capsys):
    chart = _marks().draw_bars(x="class", y="marks", colour="subject", hatched=True)
    ax = _drawn(chart).axes[0]
    patterns = [[p.get_hatch() for p in c.patches] for c in ax.containers]
    assert patterns == [[HATCHES[i]] * 3 for i in range(3)]
    assert [h.get_hatch() for h in ax.get_legend().legend_handles] == HATCHES[:3]
    # the numbers stay what seaborn draws
    plain = _marks().draw_bars(x="class", y="marks", colour="subject")
    assert list(chart.get_numbers_drawn().get_column("y")) == list(plain.get_numbers_drawn().get_column("y"))


def test_hatched_on_histograms_areas_and_pies(capsys):
    hist = _marks().draw_histogram(x="marks", colour="class", hatched=True)
    assert {c.patches[0].get_hatch() for c in _drawn(hist).axes[0].containers} == set(HATCHES[:3])
    area = sdata.chart(sdata.get_example("growth")).draw_area(x="year", y="population", colour="country",
                                                               hatched=True)
    ax = _drawn(area).axes[0]
    filled = [c.get_hatch() for c in ax.collections if c.get_hatch()]
    assert filled == HATCHES[:len(filled)] and len(filled) >= 2
    assert [h.get_hatch() for h in ax.get_legend().legend_handles] == filled
    pie = sdata.chart(sdata.get_example("fruit")).draw_pie(labels="fruit", values="count", hatched=True)
    wedges = [p for p in _drawn(pie).axes[0].patches if p.get_hatch()]
    assert [w.get_hatch() for w in wedges] == HATCHES[:len(wedges)]
    with pytest.raises(sdata.SimplydataError, match="steps=True"):
        _marks().draw_histogram(x="marks", hatched=True, steps=True)


def test_hollow_dots_keep_seaborns_colours_as_outlines(capsys):
    df = example_frame("marks")
    chart = _marks().draw_dots(x="hours", y="marks", colour="class", hollow=True)
    coll = _drawn(chart).axes[0].collections[0]
    fig, ax = plt.subplots()
    order = list(pd.unique(df["class"]))
    sns.scatterplot(df, x="hours", y="marks", hue="class", hue_order=order, palette=sdata._style.COLOURS[:3], ax=ax)
    theirs = ax.collections[0].get_facecolors()
    assert len(coll.get_facecolors()) == 0 or coll.get_facecolors()[:, 3].max() == 0
    assert [to_hex(c) for c in coll.get_edgecolors()] == [to_hex(c) for c in theirs]
    drawn = chart.get_numbers_drawn()  # the colour column gives the outline's colour
    assert drawn.get_column("colour") == [to_hex(c) for c in theirs]


def test_dashed_by_a_column_is_seaborns_style(capsys):
    df = example_frame("weather")
    chart = sdata.chart(sdata.get_example("weather"))
    chart.draw_lines(x="month_number", y="temperature", colour="city", dashed="city")
    ours = [tuple(line.get_dashes() if hasattr(line, "get_dashes") else ()) for line in _drawn(chart).axes[0].lines]
    fig, ax = plt.subplots()
    order = list(pd.unique(df["city"]))
    sns.lineplot(df, x="month_number", y="temperature", hue="city", hue_order=order, style="city",
                 style_order=order, ax=ax)
    assert [line.get_linestyle() for line in _drawn(chart).axes[0].lines][:3] == \
        [line.get_linestyle() for line in ax.lines][:3]
    assert len({line.get_linestyle() for line in _drawn(chart).axes[0].lines[:3]}) >= 2
    assert ours


def test_dotted_and_dashed(capsys):
    dotted = sdata.chart(sdata.get_example("weather")).draw_lines(x="month_number", y="temperature", dotted=True)
    assert _drawn(dotted).axes[0].lines[0].get_linestyle() == ":"
    with pytest.raises(sdata.SimplydataError, match="not both"):
        sdata.chart(sdata.get_example("weather")).draw_lines(x="month_number", y="temperature", dotted=True,
                                                             dashed=True)
    with pytest.raises(sdata.SimplydataError):
        sdata.chart(sdata.get_example("weather")).draw_lines(x="month_number", y="temperature", dashed="town")


def test_use_shapes_is_seaborns_markers(capsys):
    df = example_frame("marks")
    chart = _marks().draw_dots(x="hours", y="marks", colour="class").use_shapes("circle", "square", "triangle")
    ours = _drawn(chart).axes[0].collections[0]
    fig, ax = plt.subplots()
    order = list(pd.unique(df["class"]))
    sns.scatterplot(df, x="hours", y="marks", hue="class", hue_order=order, style="class", style_order=order,
                    markers=["o", "s", "^"], ax=ax)
    theirs = ax.collections[0]
    assert [p.vertices.tolist() for p in ours.get_paths()] == [p.vertices.tolist() for p in theirs.get_paths()]
    with pytest.raises(sdata.SimplydataError, match="circle"):
        _marks().use_shapes("blob")


def test_black_and_white_style(capsys):
    for name in ("black and white", "greyscale", "grayscale"):
        chart = _marks().draw_bars(x="class", y="marks", colour="subject").use_style(name)
        assert chart._settings["style"] == "black and white"
    colours = set(chart.get_numbers_drawn().get_column("colour"))
    assert all(c[1:3] == c[3:5] == c[5:7] for c in colours)  # greys
    assert {c.patches[0].get_hatch() for c in _drawn(chart).axes[0].containers} == set(HATCHES[:3])
    lines = sdata.chart(sdata.get_example("weather")).draw_lines(x="month_number", y="temperature", colour="city")
    lines.use_style("black and white")
    assert len({line.get_linestyle() for line in _drawn(lines).axes[0].lines[:3]}) >= 2


def test_use_colours_named_sets(capsys):
    chart = _marks().draw_bars(x="class", y="marks", colour="subject").use_colours("Set2")
    expected = [to_hex(c) for c in sns.color_palette("Set2")]
    assert chart._settings["colours"] == expected
    assert sorted(set(chart.get_numbers_drawn().get_column("colour"))) == sorted(expected[:3])
    five = _marks().use_colours("viridis", how_many=5)
    assert five._settings["colours"] == [to_hex(c) for c in sns.color_palette("viridis", n_colors=5)]
    safe = _marks().use_colours("colour-blind safe")
    assert safe._settings["colours"] == list(sdata._style.COLOURS)
    with pytest.raises(sdata.SimplydataError, match="how_many"):
        _marks().use_colours("blue", "red", how_many=2)
    with pytest.raises(sdata.SimplydataError, match="Set2"):
        _marks().use_colours("set 2")


# ---------------------------------------------------------------- saving
def test_save_eps_and_fonts_kept_as_text(tmp_path, capsys):
    chart = _marks().draw_dots(x="hours", y="marks").write_title_on_top("Marks")
    chart.save(tmp_path / "marks.pdf")
    chart.save(tmp_path / "marks.svg")
    chart.save(tmp_path / "marks.eps")
    pdf = (tmp_path / "marks.pdf").read_bytes()
    assert b"/FontFile2" in pdf and b"/Type3" not in pdf  # TrueType (Type 42), not Type 3
    assert "<text" in (tmp_path / "marks.svg").read_text(encoding="utf-8")
    assert (tmp_path / "marks.eps").read_bytes().startswith(b"%!PS-Adobe")
    see = _marks().draw_dots(x="hours", y="marks", transparency=0.5)
    see.save(tmp_path / "see.eps")
    assert "cannot hold see-through" in capsys.readouterr().out


def test_save_see_through(tmp_path, capsys):
    from PIL import Image

    chart = _marks().draw_dots(x="hours", y="marks")
    chart.save(tmp_path / "clear.png", see_through=True)
    chart.save(tmp_path / "white.png")
    with Image.open(tmp_path / "clear.png") as clear, Image.open(tmp_path / "white.png") as white:
        assert clear.convert("RGBA").getpixel((0, 0))[3] == 0
        assert white.convert("RGBA").getpixel((0, 0))[3] == 255
    with pytest.raises(sdata.SimplydataError, match="see_through"):
        chart.save(tmp_path / "x.png", see_through="yes")


# ---------------------------------------------------------------- undo
def test_undo_takes_the_last_word_back(capsys):
    chart = _marks().draw_dots(x="hours", y="marks").use_log_scale_y().use_style("dark")
    chart.undo()
    assert chart._settings["style"] == "paper"
    assert "Undone: chart.use_style()" in capsys.readouterr().out
    chart.undo()
    assert chart.get_scales_drawn().get_cell_at(row=2, column="kind") == "numbers"
    chart.undo()
    assert chart.get_numbers_drawn().count_rows() == 0
    chart.undo()
    assert "Nothing to undo" in capsys.readouterr().out


def test_undo_takes_back_a_word_that_changes_two_things(capsys):
    chart = _marks().draw_dots(x="hours", y="marks", colour="class").label_legend("Class")
    chart.undo()
    assert chart._settings.get("legend_title") is None
    assert not [s for s in chart._steps if s.name == "label_legend"]
    assert len(chart._steps) == 1


# ---------------------------------------------------------------- D11: draw_ names
OLD_TO_NEW = {"sticks": "draw_sticks", "spectrum": "draw_spectrum", "spectrum_over_time": "draw_spectrum_over_time",
              "lag_dots": "draw_lag_dots", "peak_dots": "draw_peak_dots", "difference_dots": "draw_difference_dots",
              "forecast": "draw_forecast", "trend_and_season": "draw_trend_and_season",
              "autocorrelation_bars": "draw_autocorrelation_bars",
              "cross_correlation_bars": "draw_cross_correlation_bars", "trade_off_curve": "draw_trade_off_curve",
              "forest_plot": "draw_forest_plot"}


@pytest.mark.parametrize("old, new", OLD_TO_NEW.items())
def test_the_chart_types_start_with_draw(old, new):
    words = sdata.Chart._word_names()
    assert new in words and old not in words
    assert getattr(sdata.chart(), old).__name__ == new or callable(getattr(sdata.chart(), old))


def test_an_old_name_still_draws_with_a_note(capsys):
    old = sdata.chart(sdata.get_example("weather")).sticks(x="month_number", y="rain", colour="city")
    assert 'Note: "sticks" is now called "draw_sticks"' in capsys.readouterr().out
    new = sdata.chart(sdata.get_example("weather")).draw_sticks(x="month_number", y="rain", colour="city")
    assert list(old.get_numbers_drawn().get_column("y")) == list(new.get_numbers_drawn().get_column("y"))
