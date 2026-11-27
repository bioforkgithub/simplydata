"""Name completion in editors (2026-11-23, Manish: "autocomplete should be our savior").

VS Code's Pylance and Jupyter's Jedi complete t.keep... only when they know what t is. That needs return type
hints on sdata.table(), sdata.get_example(), start_chart() and every step that gives back the same table or chart,
a py.typed marker, and words that are real class attributes. Hints only: no behaviour changes.
"""

import inspect
import pathlib

import pytest

import simplydata as sdata
from simplydata.chart import Chart
from simplydata.numbers.numbers import NumberGrid, Numbers
from simplydata.table.table import Table

SRC = pathlib.Path(sdata.__file__).resolve().parent.parent


def _return_hint(func):
    return inspect.unwrap(func).__annotations__.get("return")


def test_the_package_says_it_has_type_hints():
    assert (pathlib.Path(sdata.__file__).parent / "py.typed").is_file()


def test_starting_words_say_what_they_give_back():
    assert _return_hint(sdata.table) == "Table"
    assert _return_hint(sdata.chart) == "Chart"
    assert _return_hint(sdata.number_list) == "Numbers"
    assert _return_hint(sdata.number_grid) == "NumberGrid"
    assert _return_hint(sdata.distribution) == "Distribution"
    assert _return_hint(Table.start_chart) == "Chart"
    assert _return_hint(Numbers.start_chart) == "Chart"
    assert _return_hint(NumberGrid.turn_into_table) == "Table"


@pytest.mark.parametrize("cls, words", [
    (Table, ["keep_rows_where", "remove_rows_where", "sort_by", "keep_columns", "add_column", "rename_column",
             "fill_empty_cells_in", "spread_into_columns", "join_with", "undo", "make_copy"]),
    (Chart, ["draw_dots", "draw_bars", "draw_lines", "draw_boxes", "write_title_on_top", "label_x", "fit_line"]),
    (Numbers, ["sort", "take_log", "keep_first_numbers", "smooth"]),
])
def test_steps_give_back_the_same_kind_of_thing(cls, words):
    for word in words:
        assert _return_hint(getattr(cls, word)) == "_Same", word
        first = next(iter(inspect.signature(inspect.unwrap(getattr(cls, word))).parameters.values()))
        assert first.name == "self" and first.annotation == "_Same", word


def test_words_are_real_class_attributes_and_listed():
    table = sdata.get_example("marks")
    listed = dir(table)
    for word in ("keep_rows_where", "compare_averages_of", "start_chart", "make_copy", "count_empty_cells_in"):
        assert word in vars(Table) or any(word in vars(base) for base in Table.__mro__), word
        assert word in listed, word
    assert "draw_dots" in dir(sdata.chart(table))
    for word in ("table", "get_example", "chart", "number_list", "number_grid", "distribution"):
        assert word in sdata.__all__ and word in dir(sdata), word


def _complete(code: str) -> list[str]:
    jedi = pytest.importorskip("jedi")
    import sys

    project = jedi.Project(path=str(SRC), sys_path=[str(SRC)] + [p for p in sys.path if p], smart_sys_path=False)
    script = jedi.Script(code, path=str(SRC / "editor_check.py"), project=project)
    lines = code.split("\n")
    return [c.name for c in script.complete(len(lines), len(lines[-1]))]


@pytest.mark.parametrize("code, expected", [
    ("import simplydata as sdata\nt = sdata.table('my_file.csv')\nt.keep", "keep_rows_where"),
    ("import simplydata as sdata\nt = sdata.get_example('marks')\nt.compare_av", "compare_averages_of"),
    ("import simplydata as sdata\nt = sdata.table('my_file.csv')\nt.keep_rows_where('a', is_above=1).sort", "sort_by"),
    ("import simplydata as sdata\nc = sdata.chart(sdata.table('my_file.csv'))\nc.draw_b", "draw_bars"),
    ("import simplydata as sdata\nc = sdata.table('my_file.csv').start_chart()\nc.draw_d", "draw_dots"),
    ("import simplydata as sdata\nc = sdata.chart(sdata.table('my_file.csv'))\nc.draw_dots(x='a', y='b').write_t",
     "write_title_on_top"),
    ("import simplydata as sdata\nn = sdata.number_list([1, 2, 3])\nn.find_av", "find_average"),
])
def test_static_completion_in_a_script(code, expected):
    """jedi.Script reads the code without running it, as an editor does."""
    assert expected in _complete(code)
