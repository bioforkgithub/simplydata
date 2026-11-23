"""New-user fixes (2026-11-23, Manish: "We want other than experienced users to accept it completely"): the note when
rows repeat one person, table.make_copy(), as_pandas() as a copy, for_each_group_in= on charts, and option names
from other tools (on=, by=, groupby=, hue=, random_state=)."""

import copy

import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata._errors import _NOTED
from simplydata.table._independence import _is_id_name, repeated_rows_note

REPEAT_NOTE = ('Note: "name" repeats (each value appears 3 times), so these rows may not be independent. If the same '
               "person was measured more than once, use matched_by=, grouped_by=, compare_matched_columns, or one row "
               "per person (see lesson 14).")


@pytest.fixture(autouse=True)
def fresh_notes():
    _NOTED.clear()
    yield
    _NOTED.clear()


@pytest.fixture
def marks():
    return sdata.get_example("marks")


# ---------------------------------------------------------------- the note when rows repeat
def test_lesson_14_old_analysis_gets_the_note_once_after_the_result(marks, capsys):
    marks.compare_averages_of("marks", for_each_group_in="class")
    out = capsys.readouterr().out
    assert out.count("may not be independent") == 1
    assert REPEAT_NOTE in out
    assert out.rstrip().endswith("(see lesson 14).")  # after the result, never before it


def test_lesson_14_old_subjects_analysis_gets_the_note(marks, capsys):
    marks.compare_averages_of("marks", for_each_group_in="subject")
    assert REPEAT_NOTE in capsys.readouterr().out


def test_lesson_14_new_per_child_analysis_has_no_note(marks, capsys):
    per_child = marks.find_average_of("marks", for_each_group_in=["class", "name"])
    per_child.compare_averages_of("average of marks", for_each_group_in="class")
    assert "may not be independent" not in capsys.readouterr().out


def test_one_subject_and_matched_columns_have_no_note(marks, capsys):
    marks.keep_rows_where("subject", is_equal_to="Maths")
    marks.compare_averages_of("marks", for_each_group_in="class")
    marks.find_correlation_between("hours", "marks")
    wide = sdata.get_example("marks")
    wide.keep_columns("name", "class", "subject", "marks")
    wide.spread_into_columns(names_from="subject", values_from="marks")
    wide.compare_matched_columns(["Maths", "Science", "English"])
    assert "may not be independent" not in capsys.readouterr().out


def test_the_note_names_only_the_options_the_word_has(marks, capsys):
    marks.find_correlation_between("hours", "marks")
    out = capsys.readouterr().out
    assert ('Note: "name" repeats (each value appears 3 times), so these rows may not be independent. If the same '
            "person was measured more than once, use one row per person (see lesson 14).") in out


def test_matched_by_or_grouped_by_or_the_id_in_the_call_means_no_note(marks):
    frame = marks._frame
    params = ["column", "for_each_group_in", "matched_by", "grouped_by"]
    assert repeated_rows_note(frame, "compare_averages_of", params, ("marks",), {"for_each_group_in": "class"})
    assert not repeated_rows_note(frame, "compare_averages_of", params, ("marks",),
                                  {"for_each_group_in": "subject", "matched_by": "name"})
    assert not repeated_rows_note(frame, "explain", params, ("marks",), {"using": ["class"], "grouped_by": "name"})
    assert not repeated_rows_note(frame, "explain", params, ("marks ~ class + (1 | name)",), {})
    assert not repeated_rows_note(frame, "find_average_of", params, ("marks",), {"for_each_group_in": "class"})


def test_ordinary_grouping_columns_never_get_the_note(capsys):
    rows = 60
    table = sdata.table(pd.DataFrame({
        "class": ["A", "B", "C"] * 20,
        "site": [f"site {chr(65 + i % 6)}" for i in range(rows)],
        "month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"] * 5,
        "patient_days": [i % 7 for i in range(rows)], "cases": [i % 5 for i in range(rows)],
        "value": [float(i % 11) for i in range(rows)]}))
    table.compare_averages_of("value", for_each_group_in="class")
    assert "may not be independent" not in capsys.readouterr().out


def test_codes_without_an_id_name_get_the_note(capsys):
    table = sdata.table(pd.DataFrame({"tube": [f"T{i:02d}" for i in range(12)] * 2,
                                      "day": [1] * 12 + [2] * 12, "od": [0.1 * (i % 7) for i in range(24)]}))
    table.compare_averages_of("od", for_each_group_in="day")
    out = capsys.readouterr().out
    assert 'Note: "tube" repeats (each value appears 2 times)' in out


@pytest.mark.parametrize("name, is_id", [
    ("name", True), ("Subject", True), ("patient_id", True), ("Sample ID", True), ("animalNumber", True),
    ("id", True), ("patient_days", False), ("person_years", False), ("cases", False), ("pupils", False),
    ("class", False), ("valid", False)])
def test_id_names(name, is_id):
    assert _is_id_name(name) is is_id


# ---------------------------------------------------------------- make_copy and as_pandas
def test_make_copy_is_independent_and_keeps_the_steps(marks, capsys):
    marks.keep_rows_where("class", is_equal_to="A")
    backup = marks.make_copy()
    marks.keep_rows_where("marks", is_above=90)
    assert backup.count_rows() == 18 and marks.count_rows() < 18
    backup.show_steps()
    assert capsys.readouterr().out.rstrip().endswith('1. keep rows where class is "A"')
    backup.undo()
    assert backup.count_rows() == 54 and marks.count_rows() < 18


def test_copy_module_gives_the_same_independent_copy(marks):
    for make in (copy.copy, copy.deepcopy):
        other = make(marks)
        other.keep_rows_where("class", is_equal_to="A")
        assert marks.count_rows() == 54 and other.count_rows() == 18
        marks.show_steps()


def test_other_names_point_to_make_copy(marks):
    for name in ("copy", "clone", "deepcopy", "duplicate"):
        with pytest.raises(SimplydataError, match=r"In simplydata this is table\.make_copy\(\)"):
            getattr(marks, name)()


@pytest.mark.parametrize("engine", ["pandas", "polars"])
def test_as_pandas_and_as_polars_are_copies(engine):
    pl = pytest.importorskip("polars")
    data = {"a": [1, 2, 3], "b": ["x", "y", "z"]}
    source = pd.DataFrame(data) if engine == "pandas" else pl.DataFrame(data)
    table = sdata.table(source)
    if engine == "pandas":
        source.loc[0, "a"] = 100
    else:
        source[0, "a"] = 100
    out = table.as_pandas()
    out.loc[1, "a"] = 999
    fast = table.as_polars()
    fast[2, "a"] = 777
    assert list(table.get_column("a").as_numpy()) == [1, 2, 3]


# ---------------------------------------------------------------- for_each_group_in= on charts
def test_for_each_group_in_on_a_chart_is_colour(capsys):
    trial = sdata.get_example("trial")
    chart = sdata.chart(trial).draw_survival_curves(time="days", event="died", for_each_group_in="treatment")
    out = capsys.readouterr().out
    assert ('Note: on a chart, for_each_group_in="treatment" is the same as colour="treatment": each group gets its '
            "own colour.") in out
    same = sdata.chart(trial).draw_survival_curves(time="days", event="died", colour="treatment")
    assert chart.get_numbers_drawn().count_rows() == same.get_numbers_drawn().count_rows()


def test_for_each_group_in_on_charts_takes_only_columns(marks):
    with pytest.raises(SimplydataError, match='Column "red" not found'):
        sdata.chart(marks).draw_dots(x="hours", y="marks", for_each_group_in="red")
    with pytest.raises(SimplydataError, match="not both"):
        sdata.chart(marks).draw_dots(x="hours", y="marks", for_each_group_in="class", colour="class")
    with pytest.raises(SimplydataError, match="no option called for_each_group_in="):
        sdata.chart(marks).draw_line_at_x(3, for_each_group_in="class")


def test_hue_is_colour_on_charts(marks, capsys):
    sdata.chart(marks).draw_boxes(x="class", y="marks", hue="subject")
    assert "Note: hue= is colour= in simplydata." in capsys.readouterr().out


# ---------------------------------------------------------------- option names from other tools
def test_join_with_on_and_by(marks, capsys):
    other = {"name": ["Asha", "Ben"], "age": [12, 13]}
    marks.join_with(other, on="name")
    assert "Note: on= is using= in simplydata." in capsys.readouterr().out
    assert "age" in marks.get_column_names()
    marks.undo()
    marks.join_with(other, by="name")
    assert "Note: by= is using= in simplydata." in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="Give using= only once"):
        marks.join_with(other, on="name", using="name")


def test_by_and_groupby_are_for_each_group_in(marks, capsys):
    marks.find_average_of("marks", by="class")
    marks.find_average_of("marks", groupby="class")
    out = capsys.readouterr().out
    assert "Note: by= is for_each_group_in= in simplydata." in out
    assert "Note: groupby= is for_each_group_in= in simplydata." in out
    with pytest.raises(SimplydataError, match="Give for_each_group_in= only once"):
        marks.find_average_of("marks", by="class", for_each_group_in="class")


def test_random_state_is_with_seed(marks, capsys):
    marks.keep_random_rows(5, random_state=1)
    first = marks.get_column("marks").as_numpy().tolist()
    assert "Note: random_state= is with_seed= in simplydata." in capsys.readouterr().out
    again = sdata.get_example("marks")
    again.keep_random_rows(5, with_seed=1)
    assert again.get_column("marks").as_numpy().tolist() == first


def test_a_word_with_its_own_by_keeps_it(marks):
    marks.keep_biggest_rows(3, by="marks")
    assert marks.count_rows() >= 3


def test_subset_is_columns_on_remove_duplicate_rows(marks, capsys):
    marks.remove_duplicate_rows(subset=["name"])
    assert "Note: subset= is columns= in simplydata." in capsys.readouterr().out
    assert marks.count_rows() == 18
