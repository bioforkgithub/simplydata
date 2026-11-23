"""Fixes from the simulated user study (2026-11-23): clear messages, the reshaping words spread_into_columns,
gather_into_rows and swap_rows_and_columns, and the old names that keep working."""

import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata._errors import MissingWordError

NOTE_END = "The old name will stop working in a later version."


@pytest.fixture
def marks():
    return sdata.table(sdata.get_example("marks"))


# ---------------------------------------------------------------- table["marks"] after a step took it away
def test_brackets_say_which_step_took_the_column_away(marks):
    marks.spread_into_columns(names_from="subject", values_from="marks")
    with pytest.raises(SimplydataError) as error:
        marks["marks"]
    text = str(error.value)
    assert text.startswith('The table has no column "marks" now: the step "turn rows into columns (subject becomes '
                           'columns, filled from marks)" changed the table')
    assert "table.undo() takes the last step back" in text
    assert "Columns you have now: name, class, hours, height, Maths, Science, English" in text


def test_brackets_for_a_column_never_there_list_the_columns(marks):
    with pytest.raises(SimplydataError, match=r'There is no column "mraks"\. Did you mean table\.get_column\("marks"\)\?'
                                              r'\nColumns you have: name, class, subject, hours, marks, height'):
        marks["mraks"]


# ---------------------------------------------------------------- count_empty_cells_in("OD600")
def test_count_empty_cells_in_with_a_column_says_how_to_use_it(marks):
    with pytest.raises(SimplydataError) as error:
        marks.count_empty_cells_in("hours")
    text = str(error.value)
    assert "takes no column name" in text and "does not know" not in text
    assert "table.count_empty_cells_in() with nothing in the brackets" in text
    assert 'table.keep_rows_where("hours", is_empty=True)' in text
    assert 'table.remove_rows_with_empty_cells_in("hours")' in text


def test_count_empty_cells_in_with_a_near_column_name(marks):
    with pytest.raises(SimplydataError, match='show="patterns"') as error:
        marks.count_empty_cells_in("hour")
    assert 'Did you mean the column "hours"?' in str(error.value)


def test_count_empty_cells_in_patterns_still_works(marks, capsys):
    assert marks.count_empty_cells_in(show="patterns") is not None


# ---------------------------------------------------------------- remove_duplicate_rows() that removes nothing
def test_no_exact_duplicates_names_the_column_that_differs(capsys):
    table = sdata.table(pd.DataFrame({"sample": ["T1", "T2", "T5", "T5"], "od": [0.31, 0.35, 0.30, 0.30],
                                      "notes": [None, None, "dup", None]}))
    table.remove_duplicate_rows()
    out = capsys.readouterr().out
    assert "Removed 0 of 4 rows." in out
    assert ('Note: no row repeats an earlier row exactly, but some rows repeat an earlier row in every column except '
            'one: "notes" (1 row).') in out
    assert 'table.remove_duplicate_rows(columns=["sample", "od"])' in out


def test_no_duplicates_at_all_says_so(capsys):
    sdata.table(pd.DataFrame({"a": [1, 2], "b": [3, 4]})).remove_duplicate_rows()
    assert "No row repeats an earlier row exactly, so nothing was removed." in capsys.readouterr().out


def test_duplicates_removed_print_no_note(capsys):
    sdata.table(pd.DataFrame({"a": [1, 1], "b": [3, 3]})).remove_duplicate_rows()
    out = capsys.readouterr().out
    assert "Removed 1 of 2 rows." in out and "Note" not in out and "No row" not in out


# ---------------------------------------------------------------- spread_into_columns: the staircase note
def test_spread_with_a_column_that_differs_says_why_cells_are_empty(marks, capsys):
    marks.spread_into_columns(names_from="subject", values_from="marks")
    out = capsys.readouterr().out
    assert 'of the new columns are empty because "hours" differs between rows that are otherwise the same' in out
    assert 'table.keep_columns("name", "class", "height", "subject", "marks")' in out


def test_spread_of_the_needed_columns_gives_one_row_each_and_no_note(marks, capsys):
    marks.keep_columns("name", "class", "subject", "marks")
    marks.spread_into_columns(names_from="subject", values_from="marks")
    assert "Note" not in capsys.readouterr().out
    assert marks._frame.shape == (18, 5)


# ---------------------------------------------------------------- the renames keep the old names working
@pytest.mark.parametrize("old, new, call", [
    ("turn_rows_into_columns", "spread_into_columns",
     lambda t: t.turn_rows_into_columns(names_from="subject", values_from="marks")),
    ("turn_columns_into_rows", "gather_into_rows", lambda t: t.turn_columns_into_rows(["marks"])),
])
def test_old_reshaping_names_work_and_note_once(old, new, call, capsys):
    a, b, c = (sdata.table(sdata.get_example("marks")) for _ in range(3))
    for t in (a, b, c):
        t.keep_columns("name", "subject", "marks")
    call(a)
    call(b)
    notes = [line for line in capsys.readouterr().out.splitlines() if line.endswith(NOTE_END)]
    assert notes == [f'Note: "{old}" is now called "{new}". {NOTE_END}']
    if new == "spread_into_columns":
        c.spread_into_columns(names_from="subject", values_from="marks")
    else:
        c.gather_into_rows(["marks"])
    assert a._frame.to_pandas().equals(c._frame.to_pandas())


@pytest.mark.parametrize("name, word", [
    ("pivot", "spread_into_columns"), ("pivot_wider", "spread_into_columns"), ("spread", "spread_into_columns"),
    ("melt", "gather_into_rows"), ("pivot_longer", "gather_into_rows"), ("gather", "gather_into_rows"),
    ("stack", "gather_into_rows"), ("unpivot", "gather_into_rows"),
    ("transpose", "swap_rows_and_columns"), ("T", "swap_rows_and_columns"), ("t", "swap_rows_and_columns"),
])
def test_other_tools_names_point_to_the_reshaping_words(marks, name, word):
    with pytest.raises(MissingWordError, match=f"table.{word}"):
        getattr(marks, name)


# ---------------------------------------------------------------- swap_rows_and_columns
@pytest.mark.parametrize("fast", [False, True])
def test_swap_uses_the_first_text_column_as_names(fast):
    if fast:
        pytest.importorskip("polars")
    table = sdata.table(pd.DataFrame({"name": ["Asha", "Ben"], "maths": [61, 73], "science": [66, 98]}), fast=fast)
    table.swap_rows_and_columns()
    got = table._frame.to_pandas()
    expected = (pd.DataFrame({"name": ["Asha", "Ben"], "maths": [61, 73], "science": [66, 98]})
                .set_index("name").T.rename_axis("column").reset_index().rename_axis(columns=None))
    assert list(got.columns) == ["column", "Asha", "Ben"]
    assert got["column"].tolist() == ["maths", "science"]
    assert got["Asha"].tolist() == expected["Asha"].tolist() and got["Ben"].tolist() == [73, 98]
    assert table._frame.implementation.is_polars() == fast
    table.undo()
    assert table._columns == ["name", "maths", "science"]


def test_swap_numbers_the_columns_when_the_first_column_cannot_name_them(capsys):
    table = sdata.table(pd.DataFrame({"x": [1, 2], "y": [3, 4]}))
    table.swap_rows_and_columns()
    assert 'Note: the first column "x" holds numbers' in capsys.readouterr().out
    got = table._frame.to_pandas()
    assert list(got.columns) == ["column", "1", "2"]
    assert got["1"].tolist() == [1, 3] and got["2"].tolist() == [2, 4]


def test_swap_with_a_repeated_name_numbers_the_columns(capsys):
    table = sdata.table(pd.DataFrame({"city": ["A", "A"], "rain": [1.5, 2.0]}))
    table.swap_rows_and_columns()
    assert 'has a value that repeats or an empty cell' in capsys.readouterr().out
    assert table._columns == ["column", "1", "2"]


def test_swap_of_an_empty_table_is_refused():
    with pytest.raises(SimplydataError, match="nothing to swap"):
        sdata.table(pd.DataFrame({"a": []})).swap_rows_and_columns()


def test_spread_and_swap_say_how_they_differ():
    from simplydata.table import Table

    for word in (Table.spread_into_columns, Table.swap_rows_and_columns):
        assert "swap flips the whole table; spread turns one column's values into new columns" in " ".join(
            word.__doc__.split())


# ---------------------------------------------------------------- compare_to_truth without R
def test_compare_to_truth_method_line_says_what_was_computed(capsys, monkeypatch):
    from simplydata import _r

    monkeypatch.setattr(_r, "_STATE", {"error": "no R here", "missing": "R"})
    result = sdata.compare_to_truth(found=40, missed=10, false_alarms=5, correct_negatives=45)
    out = capsys.readouterr().out
    method = next(line for line in out.splitlines() if line.startswith("Method:"))
    assert "epi.tests" not in method and "the likelihood ratios were not computed (they need R epiR)" in method
    rows = result._frame.to_pandas()
    assert set(rows.loc[rows["measure"].str.contains("likelihood|odds"), "method"]) == {
        "not computed: R epiR is not ready here"}


def test_help_for_swap_shows_the_table_and_the_grid_word(capsys):
    sdata.help("swap_rows_and_columns")
    out = capsys.readouterr().out
    assert out.startswith("table.swap_rows_and_columns()") and "\ngrid.swap_rows_and_columns()\n" in out
