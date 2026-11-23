"""The talking-syntax renames (2026-11-16): every old word and old option still works for one release,
prints its note once per session, and is never listed among the words.

The lists below are the renames themselves (CHANGELOG, Unreleased), written out so that a rename that is
lost or undone shows up here.
"""

import re
from pathlib import Path

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
    # the old American spellings (the new words have American twins for good: use_color ...)
    "color": "use_color", "colors": "use_colors", "color_scale": "use_color_scale",
}
# Names from other tools that were the same word as a chart type: now pointers, never run, never expire.
POINTERS = {"scatter": "draw_dots", "bar": "draw_bars", "line": "draw_lines", "box": "draw_boxes",
            "violin": "draw_violins"}
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
    # between= stays for spans, after=/before= stay for two columns
    sdata.chart(marks).draw_dots(x="height", y="marks").draw_curve("y = x / 2", between=[130, 170])
    wide = pd.DataFrame({"before": [1.0, 2, 3, 4, 5], "after": [2.0, 3, 5, 4, 7]})
    sdata.table(wide).compare_before_and_after(before="before", after="after")


def test_legend_words_take_both_spellings(marks):
    for written, other in (("put_legend_at_top", "put_legend_on_top"), ("put_legend_at_bottom", "put_legend_on_bottom"),
                           ("put_legend_on_left", "put_legend_at_left"), ("put_legend_on_right", "put_legend_at_right")):
        assert getattr(sdata.Chart, written) is getattr(sdata.Chart, other)
        assert other in learn._aliases()[written]


# ---------------------------------------------------------------- what a learner reads
def _listed_words(out: str) -> set[str]:
    """Every word sdata.show_all_words() lists: the first name on each line ("  draw_bars   chart.draw_bars(...)"),
    with the object in front when it has one, and the words of its examples."""
    listed = set()
    for line in out.splitlines():
        first = line.strip().split(" ")[0] if line.startswith("  ") else ""
        if re.fullmatch(r"[\w.]+", first):
            listed.add(first.rpartition(".")[2])
        listed |= set(re.findall(r"(?<![\w.])(?:chart|table|nums|grid|dist|sdata|system)\.(\w+)\(", line))
    return listed


def test_show_all_words_lists_no_old_name(capsys):
    sdata.show_all_words()
    listed = _listed_words(capsys.readouterr().out)
    current = set()
    for cls in (sdata.Chart, sdata.Table, sdata.Numbers, sdata.NumberGrid, type(sdata.distribution("normal"))):
        current |= set(cls._word_names())
    current |= set(sdata.__all__)
    for kind, old, new in [*[("chart", o, n) for o, n in CHART.items()], *ALL[len(CHART):],
                           *[("sdata", o, n) for o, n in SDATA.items()]]:
        twins = {a for names in learn._aliases().values() for a in names}  # use_color: listed with use_colour
        assert new in listed or new in twins, new  # exact names, not parts of longer ones
        if old not in current:  # an old name that is no word of any object now
            assert old not in listed, f"{kind}.{old}"
    for old in CHART:  # the bare chart keys: draw_bars is listed as "draw_bars", never as "bars"
        assert old not in learn._all_keys()
    for kind, old, new in ALL:
        assert f"{kind}.{old}" not in learn._all_keys() and f"{'nums' if kind == 'grid' else kind}.{old}" \
            not in learn._all_keys()
    for old in SDATA:
        assert f"sdata.{old}" not in learn._all_keys()
    keys = {learn._word(k) for k in learn._all_keys()}
    assert "draw_bars" in keys and "bars" not in keys


@pytest.mark.parametrize("old, new", [("bars", "chart.draw_bars"), ("keep_rows", "table.keep_rows_where"),
                                      ("lesson", "sdata.show_lesson"), ("average_of", "table.find_average_of")])
def test_help_for_an_old_name_points_to_the_new_one(old, new, capsys):
    sdata.help(old)
    where = new.split(".")[0]
    assert capsys.readouterr().out.startswith(f'"{where}.{old}" is now called "{new}".')


def test_help_for_an_old_option_lists_its_words_on_one_line(capsys):
    sdata.help("for_each=")
    out = capsys.readouterr().out
    lines = [line for line in out.splitlines() if line.startswith('"for_each=" is now called')]
    assert len(lines) == 2  # for_each_group_in= on tables and charts, in_each= on grids
    assert lines[0].startswith('"for_each=" is now called "for_each_group_in=" in ') and "more." in lines[0]
    assert lines[1].startswith('"for_each=" is now called "in_each=" in grid.find_average()')
    assert len(out.splitlines()) < 10  # not every word explained in full


@pytest.mark.parametrize("typed, line, not_said", [
    ("dist.chart", '"dist.chart" is now called "dist.draw_chart".', "start_chart"),
    ("table.chart", '"table.chart" is now called "table.start_chart".', "draw_chart"),
    ("nums.chart", '"nums.chart" is now called "nums.start_chart".', "draw_chart"),
    ("nums.average", '"nums.average" is now called "nums.find_average".', "dist."),
    ("grid.average", '"grid.average" is now called "grid.find_average".', "dist."),
    ("table.spectrum_of", '"table.spectrum_of" is now called "table.find_spectrum_of".', "nums."),
])
def test_help_honours_the_object_written_in_front(typed, line, not_said, capsys):
    sdata.help(typed)
    out = capsys.readouterr().out
    notes_ = [x for x in out.splitlines() if "is now called" in x]
    assert notes_ == [line]  # one line, for that object only, no options with the same name
    assert not_said not in " ".join(notes_)


def test_help_without_an_object_names_each_object_once(capsys):
    sdata.help("chart")  # sdata.chart is a word: it is explained, with no old-name lines
    assert "is now called" not in capsys.readouterr().out
    sdata.help("average")
    out = capsys.readouterr().out
    said = [x for x in out.splitlines() if "is now called" in x]
    assert said == ['"nums.average" is now called "nums.find_average".',
                    '"dist.average" is now called "dist.find_average".']


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


def test_same_old_name_on_two_objects_gets_a_note_for_each(marks, capsys):
    # conftest clears the remembered notes before each test, so both objects are used in this one test
    table, dist, nums = sdata.table(marks), sdata.distribution("normal"), sdata.numbers([1.0, 2, 3, 4, 5, 6, 7, 8])
    assert table.chart == table.start_chart and dist.chart == dist.draw_chart
    nums.chart  # the same new name as table.chart: no second note
    table.keep_rows_where("marks", above=50)
    dist.find_cut_off(above=0.05)
    table.compare_averages_of("marks", between="class")
    table.keep_rows_where("marks", between=[40, 60])
    nums.spectrum_of
    table.spectrum_of
    said = notes(capsys.readouterr().out)
    for old, new in (("chart", "start_chart"), ("chart", "draw_chart"), ("above=", "is_above="),
                     ("above=", "with_chance_above="), ("between=", "for_each_group_in="), ("between=", "is_between="),
                     ("spectrum_of", "find_spectrum"), ("spectrum_of", "find_spectrum_of")):
        assert said.count(note(old, new)) == 1, (old, new)
    assert len([n for n in said if "is now called" in n]) == 8


def test_grid_summaries_take_in_each(capsys):
    grid = sdata.number_grid([[1, 2], [3, 4]])
    assert grid.find_total(in_each="row").as_numpy().tolist() == [3, 7]
    assert grid.find_average(in_each="column").as_numpy().tolist() == [2, 3]
    assert grid.find_percentile(50, in_each="row").as_numpy().tolist() == [1.5, 3.5]
    assert grid.find_total(for_each="row").as_numpy().tolist() == [3, 7]  # the old spelling, with a note
    assert notes(capsys.readouterr().out) == [note("for_each=", "in_each=")]
    with pytest.raises(sdata.SimplydataError, match='find_total\\(\\) does not know in_each="rows"'):
        grid.find_total(in_each="rows")


def test_agreement_between_takes_checking_for(capsys):
    import inspect

    params = inspect.signature(sdata.Table.agreement_between).parameters
    assert "checking_for" in params and "kind" not in params
    assert sdata.Table.agreement_between._renamed_options["kind"] == "checking_for"
    with pytest.raises(sdata.SimplydataError, match='checking_for='):
        sdata.table(pd.DataFrame({"a": [1.0, 2, 3, 4], "b": [1.0, 2, 4, 4]})).agreement_between(
            "a", "b", checking_for="same")


@pytest.mark.parametrize("name, new", list(POINTERS.items()))
def test_other_tool_chart_names_point_and_never_run(name, new, marks, capsys):
    from simplydata._errors import MissingWordError

    with pytest.raises(MissingWordError, match=rf"In simplydata this is chart\.{new}\("):
        getattr(sdata.chart(marks), name)
    assert "will stop working" not in capsys.readouterr().out
    assert name not in sdata.Chart._OLD_WORDS
    sdata.help(name)
    out = capsys.readouterr().out
    assert "a name from other tools" in out and f"chart.{new}(" in out and "stop working" not in out


def test_american_spellings_of_the_new_words_stay(marks, capsys):
    chart = sdata.chart(marks)
    for american, british in (("use_color", "use_colour"), ("use_colors", "use_colours"),
                              ("use_color_scale", "use_colour_scale"), ("label_color_bar", "label_colour_bar")):
        assert getattr(sdata.Chart, american) is getattr(sdata.Chart, british)
        getattr(chart, american)
        assert american in learn._aliases()[british]
    assert "Note" not in capsys.readouterr().out  # a spelling, not an old name: no note, no end date


def test_step_descriptions_use_the_new_words(marks, capsys):
    table = sdata.table(marks)
    table.turn_into_text("marks")
    table.turn_into_numbers("marks")
    table.turn_into_uppercase("name")
    table.turn_into_lowercase("name")
    capsys.readouterr()
    table.show_steps()
    out = capsys.readouterr().out
    assert "turn marks into text" in out and "turn marks into numbers" in out
    assert "turn name into uppercase" in out and "turn name into lowercase" in out
    assert "make marks" not in out and "make name" not in out


# ---------------------------------------------------------------- no old name anywhere a learner reads
_CURRENT = {"chart": set(sdata.Chart._word_names()), "table": set(sdata.Table._word_names()),
            "nums": set(sdata.Numbers._word_names()), "grid": set(sdata.NumberGrid._word_names()),
            "dist": set(type(sdata.distribution("normal"))._word_names()), "sdata": set(sdata.__all__),
            "system": set(n for n in dir(sdata.System) if not n.startswith("_"))}
_CURRENT["page"] = _CURRENT["chart"]
_ANY_CURRENT = set().union(*_CURRENT.values())
_OLDS = {"chart": CHART, "page": CHART, "table": TABLE, "nums": NUMS, "grid": {**NUMS, **GRID}, "dist": DIST,
         "sdata": SDATA}
_ANY_OLD = {o for olds in _OLDS.values() for o in olds} - _ANY_CURRENT
_WITH_OBJECT = re.compile(r"(?<![\w.])(chart|page|table|nums|grid|dist|sdata)\.(\w+)\(")
_AFTER_DOT = re.compile(r"(?<![\w.])\.(\w+)\(")
_LONG = sorted((o for o in _ANY_OLD if "_" in o), key=len, reverse=True)
_UNDERSCORED = re.compile(r"(?<![\w.=\"'/-])(%s)(?![\w=]|\.\w)" % "|".join(map(re.escape, _LONG)))
_SHORT_CALLS = re.compile(r"(?<![\w.])(steps|lesson|today|answers|words|example|wave|dates|envelope|chance)\(\)")


def _old_names_in(text: str, prose: bool = True) -> list[str]:
    """Old names written as code in a text: obj.old(...), .old(...), and in prose old_name or old()."""
    found = [m.group(0) for m in _WITH_OBJECT.finditer(text)
             if m.group(2) in _OLDS[m.group(1)] and m.group(2) not in _CURRENT[m.group(1)]]
    found += [m.group(0) for m in _AFTER_DOT.finditer(text) if m.group(1) in _ANY_OLD]
    if prose:
        found += [m.group(0) for m in _UNDERSCORED.finditer(text)]
        found += [m.group(0) for m in _SHORT_CALLS.finditer(text)]
    return found


def _strings_in(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _strings_in(v)
    elif isinstance(value, (list, tuple, set)):
        for v in value:
            yield from _strings_in(v)


def test_no_old_name_in_the_lessons_and_the_30_days():
    from simplydata import learn_days

    texts = list(_strings_in(learn.LESSONS)) + list(_strings_in(learn.HELP_EXAMPLES))
    texts += [s for name, value in vars(learn_days).items() if name.isupper() for s in _strings_in(value)]
    hits = [(hit, text[:80]) for text in texts for hit in _old_names_in(text)]
    assert not hits, hits[:10]


def _src_strings():
    """(file, line, text, is a docstring) for every string in src/simplydata."""
    import ast

    root = Path(sdata.__file__).parent
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        docs = {id(node.body[0].value) for node in ast.walk(tree)
                if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                and node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)}
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                yield path.relative_to(root), node.lineno, node.value, id(node) in docs


# Strings that name old names on purpose: the notes and help for old names, and how chart steps keep
# their inner names.
_ON_PURPOSE = ("is now called", "old name", "Old name", "inner name", "The old done()")


def test_no_old_name_in_docstrings_and_messages():
    hits = []
    for path, line, text, is_doc in _src_strings():
        if any(mark in text for mark in _ON_PURPOSE):
            continue
        for hit in _old_names_in(text, prose=is_doc):
            hits.append(f"{path}:{line}: {hit}")
    assert not hits, hits[:15]


def test_no_old_name_in_the_built_documents():
    manual = Path(__file__).resolve().parents[1] / "docs" / "manual"
    hits = []
    for name in ("simplydata_manual.tex", "simplydata_30_days.tex", "simplydataDictionary.tex"):
        text = (manual / name).read_text(encoding="utf-8")
        if name == "simplydataDictionary.tex":  # the list of old names is there on purpose
            start = text.index(r"\section*{Old names}")
            text = text[:start] + text[text.index(r"\end{dictcolumns}", start):]
        plain = text.replace(r"\allowbreak{}", "").replace(r"\_", "_").replace(r"\textquotedbl{}", '"')
        for number, line in enumerate(plain.splitlines(), 1):
            if any(mark in line for mark in _ON_PURPOSE):
                continue
            if r"{Underneath}{" in line:  # the calls of the package underneath (SciPy find_peaks), never simplydata words
                continue
            hits += [f"{name}:{number}: {hit}" for hit in _old_names_in(line)]
    assert not hits, hits[:15]
