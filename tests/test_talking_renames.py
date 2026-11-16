"""The talking-syntax renames (2026-11-16): every old word and old option still works for one release,
prints its note once per session, and is never listed among the words.

The lists below are the renames themselves (CHANGELOG, Unreleased), written out so that a rename that is
lost or undone shows up here.
"""

import re

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import learn

NOTE_END = "The old name will stop working in a later version."

CHART = {
    "bars": "draw_bars", "lines": "draw_lines", "dots": "draw_dots", "area": "draw_area",
    "histogram": "draw_histogram", "boxes": "draw_boxes", "violins": "draw_violins", "heatmap": "draw_heatmap",
    "pie": "draw_pie", "polar": "draw_polar", "contour": "draw_contour", "surface": "draw_surface",
    "dots_3d": "draw_dots_3d", "band": "draw_band", "empty_cells": "draw_map_of_empty_cells",
    "error_bars": "draw_error_bars", "curve": "draw_curve", "smooth_line": "draw_smooth_line",
    "density": "draw_density", "count_bars": "draw_count_bars", "all_dots": "draw_all_dots",
    "side_histograms": "draw_side_histograms", "qq_dots": "draw_qq_dots", "cumulative_share": "draw_cumulative_share",
    "title_top": "write_title_on_top", "caption_bottom": "write_caption_at_bottom", "note": "write_note",
    "numbers_on_bars": "write_numbers_on_bars", "names_on_dots": "write_names_on_dots",
    "font_size": "use_font_size", "font_name": "use_font", "range_x": "set_range_x", "range_y": "set_range_y",
    "log_scale_x": "use_log_scale_x", "log_scale_y": "use_log_scale_y", "ticks_x": "put_ticks_x",
    "ticks_y": "put_ticks_y", "tick_format_x": "write_ticks_x_as", "tick_format_y": "write_ticks_y_as",
    "second_y": "add_second_y", "colour": "use_colour", "colours": "use_colours", "colour_scale": "use_colour_scale",
    "style": "use_style", "size": "set_size", "legend_top": "put_legend_at_top",
    "legend_bottom": "put_legend_at_bottom", "legend_left": "put_legend_on_left", "legend_right": "put_legend_on_right",
    "one_chart_per": "draw_one_chart_for_each_group_in", "zoom_box": "add_zoom_box",
    "survival_curves": "draw_survival_curves", "line_at_x": "draw_line_at_x", "line_at_y": "draw_line_at_y",
    "line_with_slope": "draw_line_with_slope",
    # American spellings and other names that were the same word
    "color": "use_color", "colors": "use_colors", "color_scale": "use_color_scale", "scatter": "draw_dots",
    "bar": "draw_bars", "line": "draw_lines", "box": "draw_boxes", "violin": "draw_violins",
}
TABLE = {
    "column_names": "get_column_names", "column": "get_column", "row": "get_row", "cell_at": "get_cell_at",
    "keep_rows": "keep_rows_where", "remove_rows": "remove_rows_where", "count_empty_cells": "count_empty_cells_in",
    "remove_rows_with_empty_cells": "remove_rows_with_empty_cells_in", "fill_empty_cells": "fill_empty_cells_in",
    "remove_extra_spaces": "remove_extra_spaces_in", "replace_values": "replace_values_in",
    "add_date_part_column": "add_column_with_part_of_date", "add_text_part_column": "add_column_with_part_of_text",
    "replace_text": "replace_text_in", "average_of": "find_average_of", "median_of": "find_median_of",
    "total_of": "find_total_of", "smallest_of": "find_smallest_of", "biggest_of": "find_biggest_of",
    "standard_deviation_of": "find_standard_deviation_of", "summary_of": "find_summary_of",
    "percent_of": "find_percent_of_rows_where", "count_different_values": "count_different_values_in",
    "percentile_of": "find_percentile_of", "most_common_of": "find_most_common_of",
    "correlation_between": "find_correlation_between", "interval_of": "find_interval_of", "chart": "start_chart",
    "compare_averages": "compare_averages_of", "compare_each_pair": "compare_each_pair_of",
    "compare_before_after": "compare_before_and_after", "compare_counts": "compare_counts_of",
    "compare_spreads": "compare_spreads_of", "compare_shapes": "compare_shapes_of",
    "check_random_order": "check_if_random_order", "compare_matched": "compare_matched_columns",
    "model_averages_of": "find_model_averages_of", "check_model": "check_model_of",
    "show_rows_that_pull": "show_rows_that_pull_model", "principal_components_of": "find_principal_components_of",
    "distances_between_rows": "find_distances_between_rows", "compare_profiles": "compare_profiles_of",
    "survival_over_time": "find_survival_over_time", "spectrum_of": "find_spectrum_of",
    "check_steady": "check_steady_over_time", "autocorrelation_of": "find_autocorrelation_of",
    "trend_of": "find_trend_of", "compare_forecasts": "compare_forecasts_for",
    "find_change_points": "find_change_points_in", "find_peaks": "find_each_peak_that", "find_dips": "find_each_dip_that",
    "map_of": "make_map_of", "fit_distribution": "fit_distribution_to", "compare_distributions": "compare_distributions_for",
    "make_numbers": "turn_into_numbers", "make_text": "turn_into_text", "make_dates": "turn_into_dates",
    "make_lowercase": "turn_into_lowercase", "make_uppercase": "turn_into_uppercase", "round_to": "round_numbers_in",
    "steps": "show_steps",
}
NUMS = {
    "number_at": "get_number_at", "power": "raise_to_power", "square_root": "take_square_root",
    "absolute_value": "take_absolute_value", "log": "take_log", "exp": "take_exp",
    "running_total": "turn_into_running_total", "keep_numbers": "keep_each_number_that",
    "remove_numbers": "remove_each_number_that", "replace_numbers": "replace_each_number_that",
    "average": "find_average", "median": "find_median", "total": "find_total", "smallest": "find_smallest",
    "biggest": "find_biggest", "standard_deviation": "find_standard_deviation", "percentile": "find_percentile",
    "number_grid": "make_number_grid", "table": "turn_into_table", "chart": "start_chart",
    "spectrum_of": "find_spectrum", "autocorrelation_of": "find_autocorrelation",
    "keep_frequencies": "keep_each_frequency_that", "remove_frequencies": "remove_each_frequency_that",
    "find_peaks": "find_each_peak_that", "find_dips": "find_each_dip_that",
    "fourier_transform": "take_fourier_transform", "envelope": "find_envelope", "steps": "show_steps",
}
GRID = {"shape": "find_shape", "number_at": "get_number_at", "row": "get_row", "column": "get_column",
        "numbers": "get_all_numbers", "replace_numbers": "replace_each_number_that", "steps": "show_steps",
        "average": "find_average", "total": "find_total", "table": "turn_into_table"}
DIST = {
    "chance": "find_chance_that_value", "density_at": "find_density_at", "percentile": "find_percentile",
    "cut_off": "find_cut_off", "middle_range": "find_middle_range", "average": "find_average", "median": "find_median",
    "standard_deviation": "find_standard_deviation", "variance": "find_variance", "summary": "show_summary",
    "random_numbers": "make_random_numbers", "chart": "draw_chart", "table": "turn_into_table",
    "parameters": "show_parameters",
}
SDATA = {
    "example": "get_example", "pairs": "draw_all_pairs", "side_by_side": "put_side_by_side",
    "one_above_other": "put_one_above_other", "grid": "put_in_rows_and_columns", "random_numbers": "make_random_numbers",
    "how_many_needed": "find_how_many_needed", "chance_to_find": "find_chance_of_finding",
    "dates": "make_run_of_dates", "inverse_fourier_transform": "find_inverse_fourier_transform", "wave": "make_wave",
    "window_shape": "make_window_shape", "find_smallest": "find_where_smallest", "find_biggest": "find_where_biggest",
    "words": "show_all_words", "lesson": "show_lesson", "today": "show_today", "day": "show_day",
    "answers": "show_answers", "next_day": "go_to_next_day",
}


def notes(out):
    return [line for line in out.splitlines() if line.startswith("Note:")]


def note(old, new):
    return f'Note: "{old}" is now called "{new}". {NOTE_END}'


@pytest.fixture
def objects(marks):
    return {"chart": sdata.chart(marks), "table": sdata.table(marks), "nums": sdata.numbers([3, 1, 2]),
            "grid": sdata.number_grid([[1, 2], [3, 4]]), "dist": sdata.distribution("normal")}


ALL = [("chart", o, n) for o, n in CHART.items()] + [("table", o, n) for o, n in TABLE.items()] + \
      [("nums", o, n) for o, n in NUMS.items()] + [("grid", o, n) for o, n in GRID.items()] + \
      [("dist", o, n) for o, n in DIST.items()]


# ---------------------------------------------------------------- old words on objects
@pytest.mark.parametrize("kind, old, new", ALL)
def test_old_word_is_the_new_word_with_a_note_once(kind, old, new, objects, capsys):
    thing = objects[kind]
    got = getattr(thing, old)
    assert got == getattr(thing, new)  # the same bound word, so it does exactly what the new word does
    getattr(thing, old)
    assert notes(capsys.readouterr().out) == [note(old, new)]  # once per session


@pytest.mark.parametrize("kind, old, new", ALL)
def test_old_word_is_not_a_listed_word(kind, old, new):
    cls = {"chart": sdata.Chart, "table": sdata.Table, "nums": sdata.Numbers, "grid": sdata.NumberGrid,
           "dist": type(sdata.distribution("normal"))}[kind]
    assert old not in cls._word_names()
    assert new in cls._word_names()


@pytest.mark.parametrize("old, new", list(SDATA.items()))
def test_old_sdata_word_works_with_a_note_once(old, new, capsys):
    if old == "words":  # a function of its own: sdata.words is also the name of a subpackage
        assert callable(sdata.words)
    else:
        assert getattr(sdata, old) is getattr(sdata, new)
        getattr(sdata, old)
        assert notes(capsys.readouterr().out) == [note(old, new)]
    assert old not in sdata.__all__ and new in sdata.__all__


def test_old_names_really_run(marks, capsys):
    table = sdata.table(marks)
    assert table.average_of("marks") == table.find_average_of("marks")
    sdata.words()
    out = capsys.readouterr().out
    assert note("words", "show_all_words") in out and "chart.draw_bars(" in out
    chart = sdata.chart(marks).bars(x="name", y="marks").title_top("Marks").legend_bottom()
    assert [s.name for s in chart._steps] == [s.name for s in sdata.chart(marks).draw_bars(x="name", y="marks")
                                               .write_title_on_top("Marks").put_legend_at_bottom()._steps]
    assert repr(chart).startswith("<simplydata chart: draw_bars")  # shown with the word as it is written now
    assert sdata.numbers([1, 4, 9]).square_root().as_numpy().tolist() == [1, 2, 3]
    assert sdata.distribution("normal").chance(is_below=0) == pytest.approx(0.5)


def test_from_import_of_an_old_sdata_word():
    from simplydata import grid, example  # noqa: F401  (old names, kept for one release)

    assert grid is sdata.put_in_rows_and_columns and example is sdata.get_example


# ---------------------------------------------------------------- old options
OPTIONS = [
    (lambda t: t.keep_rows_where("marks", above=50), "above=", "is_above="),
    (lambda t: t.keep_rows_where("marks", below=50), "below=", "is_below="),
    (lambda t: t.keep_rows_where("marks", at_least=50), "at_least=", "is_at_least="),
    (lambda t: t.keep_rows_where("marks", at_most=50), "at_most=", "is_at_most="),
    (lambda t: t.keep_rows_where("class", equal_to="A"), "equal_to=", "is_equal_to="),
    (lambda t: t.keep_rows_where("class", not_equal_to="A"), "not_equal_to=", "is_not_equal_to="),
    (lambda t: t.keep_rows_where("class", one_of=["A"]), "one_of=", "is_one_of="),
    (lambda t: t.remove_rows_where("marks", between=[40, 60]), "between=", "is_between="),
    (lambda t: t.find_average_of("marks", for_each="class"), "for_each=", "for_each_group_in="),
    (lambda t: t.keep_random_rows(3, seed=1), "seed=", "with_seed="),
    (lambda t: t.keep_columns(kind="number"), "kind=", "of_kind="),
    (lambda t: t.keep_columns(pattern="^m"), "pattern=", "matches_pattern="),
    (lambda t: t.round_numbers_in("marks", decimals=1), "decimals=", "with_decimals="),
    (lambda t: t.fit_curve(x="height", y="marks", degree=2), "degree=", "of_degree="),
]


@pytest.mark.parametrize("call, old, new", OPTIONS)
def test_old_option_works_with_a_note_once(call, old, new, marks, capsys):
    call(sdata.table(marks))
    call(sdata.table(marks))
    assert notes(capsys.readouterr().out).count(note(old, new)) == 1


def test_old_and_new_conditions_give_the_same_rows(marks):
    a = sdata.table(marks).keep_rows_where("marks", above=50).as_pandas()
    b = sdata.table(marks).keep_rows_where("marks", is_above=50).as_pandas()
    pd.testing.assert_frame_equal(a, b)
    old = sdata.numbers([1, 5, 9]).keep_numbers(between=[2, 9]).as_numpy()
    assert np.array_equal(old, sdata.numbers([1, 5, 9]).keep_each_number_that(is_between=[2, 9]).as_numpy())


def test_old_chart_options(marks, capsys):
    chart = sdata.chart(marks).draw_lines(x="test", y="marks", dots=True).draw_line_at_y(50, label="pass")
    chart.draw_histogram(x="marks", bins=5)
    sdata.chart(marks).draw_dots(x="height", y="marks").write_note("top", x=150, y=90, arrow=True)._render()
    out = capsys.readouterr().out
    for old, new in (("dots=", "with_dots="), ("label=", "labelled="), ("bins=", "with_bins="),
                     ("arrow=", "with_arrow=")):
        assert note(old, new) in out
    assert chart._steps[0].kwargs["dots"] is True  # the inner names are unchanged


def test_labeled_is_the_same_as_labelled(marks, capsys):
    a = sdata.chart(marks).draw_dots(x="height", y="marks").draw_line_at_y(50, labeled="pass")
    b = sdata.chart(marks).draw_dots(x="height", y="marks").draw_line_at_y(50, labelled="pass")
    assert a._steps[-1].kwargs == b._steps[-1].kwargs
    assert "Note" not in capsys.readouterr().out  # a spelling, not an old name


def test_cut_off_options_say_chance(capsys):
    dist = sdata.distribution("normal", average=50, standard_deviation=10)
    new = dist.find_cut_off(with_chance_above=0.025)
    assert dist.find_cut_off(above=0.025) == pytest.approx(new)
    assert dist.find_cut_off(with_chance_below=0.05) == pytest.approx(dist.find_cut_off(below=0.05))
    out = capsys.readouterr().out
    assert note("above=", "with_chance_above=") in out and note("below=", "with_chance_below=") in out


def test_kept_options_keep_their_old_meaning(marks):
    # between= stays for spans, after=/before= stay for two columns, a grid keeps for_each="row"
    sdata.chart(marks).draw_dots(x="height", y="marks").draw_curve("y = x / 2", between=[130, 170])
    assert sdata.number_grid([[1, 2], [3, 4]]).find_total(for_each="row").as_numpy().tolist() == [3, 7]
    wide = pd.DataFrame({"before": [1.0, 2, 3, 4, 5], "after": [2.0, 3, 5, 4, 7]})
    sdata.table(wide).compare_before_and_after(before="before", after="after")


def test_legend_words_take_both_spellings(marks):
    for written, other in (("put_legend_at_top", "put_legend_on_top"), ("put_legend_at_bottom", "put_legend_on_bottom"),
                           ("put_legend_on_left", "put_legend_at_left"), ("put_legend_on_right", "put_legend_at_right")):
        assert getattr(sdata.Chart, written) is getattr(sdata.Chart, other)
        assert other in learn._aliases()[written]


# ---------------------------------------------------------------- what a learner reads
def test_show_all_words_lists_no_old_name(capsys):
    sdata.show_all_words()
    out = capsys.readouterr().out
    listed = set(re.findall(r"(?:chart|table|nums|grid|dist|sdata)\.(\w+)\(", out))
    for old, new in [*CHART.items(), *TABLE.items(), *NUMS.items(), *GRID.items(), *DIST.items(), *SDATA.items()]:
        assert new in listed or new in out, new
    keys = {learn._word(k) for k in learn._all_keys()}
    for kind, old, new in ALL:
        assert f"{kind}.{old}" not in learn._all_keys()
    for old in SDATA:
        assert f"sdata.{old}" not in learn._all_keys()
    assert "draw_bars" in keys and "bars" not in keys


@pytest.mark.parametrize("old, new", [("bars", "draw_bars"), ("keep_rows", "keep_rows_where"), ("lesson", "show_lesson"),
                                      ("average_of", "find_average_of"), ("for_each=", "for_each_group_in=")])
def test_help_for_an_old_name_points_to_the_new_one(old, new, capsys):
    sdata.help(old)
    assert capsys.readouterr().out.startswith(f'"{old}" is now called "{new}"')


def test_lessons_and_help_examples_use_no_old_name():
    texts = list(learn.HELP_EXAMPLES.values())
    texts += [code for les in learn.LESSONS for _, steps in les["parts"] for code, _ in steps]
    for text in texts:
        for prefix, name in re.findall(r"\b(chart|table|nums|grid|dist|sdata)\.(\w+)\(", text):
            if prefix == "sdata":
                assert name not in SDATA, (name, text)
            else:
                kinds = {"chart": CHART, "table": TABLE, "nums": NUMS, "grid": {**NUMS, **GRID}, "dist": DIST}
                assert name not in kinds[prefix], (prefix, name, text)
