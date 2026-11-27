"""Numbers and number grids: every word checked against NumPy."""

import re

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata._data import frame_for, is_listlike, load
from simplydata.numbers import NumberGrid, Numbers, number_grid, number_list, make_random_numbers

NAN = np.nan


def same(a, b):
    np.testing.assert_allclose(np.asarray(a, dtype=float), np.asarray(b, dtype=float), equal_nan=True)


# ====================================================================== making numbers
def test_from_list_and_from_several_numbers():
    assert isinstance(number_list([3, 5, 2, 8]), Numbers)
    same(number_list([3, 5, 2, 8]), [3, 5, 2, 8])
    same(number_list(3, 5, 2, 8), [3, 5, 2, 8])
    assert number_list([3, 5]).as_numpy().dtype.kind == "i"  # whole numbers stay whole
    same(number_list([1, None, 3]), [1, NAN, 3])
    same(number_list(np.array([1.5, 2.5])), [1.5, 2.5])
    same(number_list(pd.Series([1, 2])), [1, 2])
    same(number_list(range(3)), [0, 1, 2])
    assert number_list([]).count() == 0


def test_counting_includes_the_end():
    same(number_list(1, to=10), np.arange(1, 11))
    same(number_list(0, to=100, step=25), [0, 25, 50, 75, 100])
    same(number_list(10, to=1), np.arange(10, 0, -1))
    same(number_list(0, to=1, step=0.1), np.linspace(0, 1, 11))
    same(number_list(0, to=1, how_many=5), np.linspace(0, 1, 5))
    same(number_list(1, to=10, step=4), [1, 5, 9])
    assert number_list(1, to=10).as_numpy().dtype.kind == "i"


def test_making_numbers_errors():
    with pytest.raises(SimplydataError, match="sdata.number_list\\(1, to=5\\)"):
        number_list(5)
    with pytest.raises(SimplydataError, match="text"):
        number_list(["a", 2])
    with pytest.raises(SimplydataError, match="without quotes"):
        number_list(["3", "4"])
    with pytest.raises(SimplydataError, match="True/False"):
        number_list([True, False])
    with pytest.raises(SimplydataError, match="number_grid"):
        number_list([[1, 2], [3, 4]])
    with pytest.raises(SimplydataError, match="never gets there"):
        number_list(1, to=10, step=-1)
    with pytest.raises(SimplydataError, match="not both"):
        number_list(0, to=1, step=0.1, how_many=3)
    with pytest.raises(SimplydataError, match="not 0"):
        number_list(0, to=1, step=0)
    with pytest.raises(SimplydataError, match="has no option called start="):
        number_list(start=1, to=10)


def test_random_numbers_match_numpy():
    same(make_random_numbers(how_many=5, with_seed=1), np.random.default_rng(1).uniform(0, 1, 5))
    same(make_random_numbers(how_many=5, between=[10, 2], with_seed=2), np.random.default_rng(2).uniform(2, 10, 5))
    dice = make_random_numbers(how_many=500, between=[1, 6], whole_numbers=True, with_seed=3)
    same(dice, np.random.default_rng(3).integers(1, 6, 500, endpoint=True))
    assert dice.find_smallest() == 1 and dice.find_biggest() == 6
    same(make_random_numbers(how_many=4, average=50, standard_deviation=10, with_seed=4),
         np.random.default_rng(4).normal(50, 10, 4))
    grid = make_random_numbers(rows=2, columns=3, with_seed=5)
    assert isinstance(grid, NumberGrid) and grid.find_shape() == (2, 3)
    same(make_random_numbers(how_many=3, with_seed=9), make_random_numbers(how_many=3, with_seed=9))


def test_random_numbers_errors():
    with pytest.raises(SimplydataError, match="how_many"):
        make_random_numbers(with_seed=1)
    with pytest.raises(SimplydataError, match="not both"):
        make_random_numbers(how_many=3, between=[0, 1], average=2, standard_deviation=1)
    with pytest.raises(SimplydataError, match="seed="):
        make_random_numbers(how_many=3, with_seed=-1)
    with pytest.raises(SimplydataError, match="both average= and standard_deviation="):
        make_random_numbers(how_many=3, average=5)
    with pytest.raises(SimplydataError, match="whole numbers in between"):
        make_random_numbers(how_many=3, between=[0.5, 2], whole_numbers=True)


def test_making_grids():
    grid = number_grid([[1, 2, 3], [4, 5, 6]])
    assert isinstance(grid, NumberGrid)
    assert grid.find_shape() == (2, 3) and grid.count_rows() == 2 and grid.count_columns() == 3
    assert grid.count() == 6 and len(grid) == 2
    same(number_grid(rows=2, columns=3), np.zeros((2, 3)))
    same(number_grid(rows=2, columns=2, filled_with=1), np.ones((2, 2)))
    same(number_grid(rows=1, columns=2, filled_with=None), [[NAN, NAN]])
    same(number_grid([1, 2, 3, 4, 5, 6], columns=3), np.arange(1, 7).reshape(2, 3))
    same(number_grid([1, 2, 3, 4, 5, 6], rows=3), np.arange(1, 7).reshape(3, 2))
    same(number_list(1, to=6).make_number_grid(columns=2), np.arange(1, 7).reshape(3, 2))
    with pytest.raises(SimplydataError, match="same length"):
        number_grid([[1, 2], [3]])
    with pytest.raises(SimplydataError, match="cannot fill"):
        number_grid([1, 2, 3, 4, 5], columns=2)
    with pytest.raises(SimplydataError, match="rows= and columns="):
        number_grid()


# ====================================================================== looking and picking
def test_positions_count_from_one():
    nums = number_list([3, 5, 2, 8])
    assert nums.get_number_at(1) == 3 and nums.get_number_at(4) == 8
    assert isinstance(nums.get_number_at(1), int)
    with pytest.raises(SimplydataError, match="from 1 to 4"):
        nums.get_number_at(0)
    with pytest.raises(SimplydataError, match="count from 1"):
        nums[0]
    grid = number_grid([[1, 2, 3], [4, 5, 6]])
    assert grid.get_number_at(row=2, column=3) == 6
    same(grid.get_row(1), [1, 2, 3])
    same(grid.get_column(2), [2, 5])
    same(grid.get_all_numbers(), [1, 2, 3, 4, 5, 6])
    with pytest.raises(SimplydataError, match="from 1 to 2"):
        grid.get_row(3)
    with pytest.raises(SimplydataError, match="number_at"):
        grid[0, 0]


def test_show_words(capsys):
    nums = number_list(1, to=10)
    nums.show_first_numbers(3)
    nums.show_last_numbers(2)
    nums.show()
    out = capsys.readouterr().out.splitlines()
    assert out[0] == "[1, 2, 3]" and out[1] == "[ 9, 10]"
    assert "simplydata numbers: 10 numbers" in repr(nums)
    assert "2 rows, 3 columns" in repr(number_grid(rows=2, columns=3))


def test_keep_and_remove_use_table_conditions(capsys):
    values = np.array([3, 50, 70, NAN, 51, 40])
    nums = number_list(values)
    nums.keep_each_number_that(is_above=50)
    same(nums, [70, 51])
    assert "Kept 2 of 6 numbers." in capsys.readouterr().out
    nums.undo()
    nums.remove_each_number_that(is_between=[40, 60])
    same(nums, [3, 70, NAN])
    assert "Removed 3 of 6 numbers. 3 left." in capsys.readouterr().out
    for option, expected in [
        (dict(is_below=40), [3]), (dict(is_at_least=50), [50, 70, 51]), (dict(is_at_most=40), [3, 40]),
        (dict(is_equal_to=70), [70]), (dict(is_not_equal_to=70), [3, 50, 51, 40]),
        (dict(is_one_of=[3, 40]), [3, 40]), (dict(is_empty=True), [NAN]),
        (dict(is_empty=False), [3, 50, 70, 51, 40]), (dict(is_between=[60, 40]), [50, 51, 40]),
    ]:
        nums = number_list(values)
        nums.keep_each_number_that(**option)
        same(nums, expected)


def test_keep_errors():
    nums = number_list([1, 2, 3])
    with pytest.raises(SimplydataError, match="one condition"):
        nums.keep_each_number_that()
    with pytest.raises(SimplydataError, match="one condition at a time"):
        nums.keep_each_number_that(is_above=1, is_below=3)
    with pytest.raises(SimplydataError, match="without quotes"):
        nums.keep_each_number_that(is_above="2")
    with pytest.raises(SimplydataError, match="two numbers"):
        nums.keep_each_number_that(is_between=5)
    with pytest.raises(SimplydataError, match="no option called contains="):
        nums.keep_each_number_that(contains="1")
    with pytest.raises(SimplydataError, match="above=50"):
        nums.keep_each_number_that(50)


def test_first_last_random_empty_duplicate():
    nums = number_list([4, 1, 4, NAN, 2, 1])
    nums.keep_first_numbers(3)
    same(nums, [4, 1, 4])
    nums.start_again()
    nums.keep_last_numbers(2)
    same(nums, [2, 1])
    nums.start_again()
    nums.remove_empty_numbers()
    same(nums, [4, 1, 4, 2, 1])
    nums.remove_duplicate_numbers()
    same(nums, [4, 1, 2])
    picked = number_list(1, to=20)
    picked.keep_random_numbers(5, with_seed=1)
    expected = np.sort(np.random.default_rng(1).choice(20, 5, replace=False)) + 1
    same(picked, expected)


def test_fill_empty_numbers(capsys):
    values = [1, NAN, 3, NAN]
    for kw, expected in [
        (dict(with_value=0), [1, 0, 3, 0]), (dict(with_the="average"), [1, 2, 3, 2]),
        (dict(with_the="median"), [1, 2, 3, 2]), (dict(with_the="value above"), [1, 1, 3, 3]),
        (dict(with_the="value below"), [1, 3, 3, NAN]),
    ]:
        nums = number_list(values)
        nums.fill_empty_numbers(**kw)
        same(nums, expected)
    assert "1 value stayed empty" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="exactly one"):
        number_list(values).fill_empty_numbers()
    with pytest.raises(SimplydataError, match="with_the"):
        number_list(values).fill_empty_numbers(with_the="mode")


# ====================================================================== maths words and symbols
@pytest.mark.parametrize("word, symbol, other", [
    ("add", lambda a, b: a + b, 5), ("subtract", lambda a, b: a - b, 2),
    ("times", lambda a, b: a * b, 3), ("divide_by", lambda a, b: a / b, 4),
    ("raise_to_power", lambda a, b: a ** b, 2), ("add", lambda a, b: a + b, [1, 2, 3, 4]),
    ("times", lambda a, b: a * b, [0.5, 1, 2, 3]),
])
def test_words_change_and_symbols_make_new(word, symbol, other):
    base = np.array([3.0, 5.0, 2.0, 8.0])
    nums = number_list(base)
    new = symbol(nums, other)
    assert isinstance(new, Numbers)
    same(nums, base)  # symbols leave the numbers alone
    same(new, symbol(base, np.asarray(other)))
    getattr(nums, word)(other)
    same(nums, new)  # the word gives the same answer
    nums.undo()
    same(nums, base)


def test_reflected_symbols_and_numbers_with_numbers():
    nums = number_list([1, 2, 4])
    same(10 - nums, [9, 8, 6])
    same(8 / nums, [8, 4, 2])
    same(2 ** nums, [2, 4, 16])
    same([1, 1, 1] + nums, [2, 3, 5])
    same(nums + number_list([1, 1, 1]), [2, 3, 5])
    same(-nums, [-1, -2, -4])
    same(abs(number_list([-1, 2])), [1, 2])
    same(np.array([1, 1, 1]) * nums, [1, 2, 4])
    assert isinstance(np.float64(2) * nums, Numbers)
    with pytest.raises(SimplydataError, match="3 numbers"):
        nums + [1, 2]
    with pytest.raises(SimplydataError, match="without quotes"):
        nums.add("5")
    with pytest.raises(SimplydataError, match="v0.7"):
        nums @ nums


def test_division_by_zero_becomes_empty(capsys):
    nums = number_list([4, 0, NAN])
    same(nums / 0, [NAN, NAN, NAN])
    assert "dividing by 0 has no answer, so 2 numbers are now empty" in capsys.readouterr().out
    nums.divide_by([2, 0, 1])
    same(nums, [2, NAN, NAN])
    assert "1 number is now empty" in capsys.readouterr().out
    same(1 / number_list([0, 2]), [NAN, 0.5])


def test_power_edge_cases(capsys):
    same(number_list([2, 3]) ** -1, [0.5, 1 / 3])
    same(number_list([0, 4]) ** -1, [NAN, 0.25])
    assert "minus power" in capsys.readouterr().out
    same(number_list([-4, 4]) ** 0.5, [NAN, 2])
    assert "power with decimals" in capsys.readouterr().out
    big = number_list([10]) ** 30
    assert big.get_number_at(1) == pytest.approx(1e30)  # no silent whole-number overflow
    assert (number_list([2, 3]) ** 2).as_numpy().dtype.kind == "i"


def test_one_at_a_time_words(capsys):
    v = np.array([1.0, 4.0, -9.0, 100.0, 0.0])
    checks = [
        ("take_square_root", {}, np.where(v < 0, NAN, np.sqrt(np.abs(v)))),
        ("take_absolute_value", {}, np.abs(v)),
        ("take_log", {}, np.where(v <= 0, NAN, np.log(np.abs(v) + (v == 0)))),
        ("take_log", {"base": 10}, np.where(v <= 0, NAN, np.log10(np.abs(v) + (v == 0)))),
        ("take_log", {"base": 2}, np.where(v <= 0, NAN, np.log2(np.abs(v) + (v == 0)))),
        ("take_log", {"base": 5}, np.where(v <= 0, NAN, np.log(np.abs(v) + (v == 0)) / np.log(5))),
        ("take_exp", {}, np.exp(v)),
    ]
    for word, kw, expected in checks:
        nums = number_list(v)
        getattr(nums, word)(**kw)
        same(nums, expected)
    out = capsys.readouterr().out
    assert "a negative number has no square root, so 1 number is now empty" in out
    assert "the log only exists for numbers above 0, so 2 numbers are now empty" in out
    with pytest.raises(SimplydataError, match="base="):
        number_list(v).take_log(base=1)


def test_round_half_to_even():
    nums = number_list([0.5, 1.5, 2.5, 3.5, 2.675, 1234])
    nums.round_to(0)
    same(nums, np.round([0.5, 1.5, 2.5, 3.5, 2.675, 1234]))
    same(nums.as_numpy()[:4], [0, 2, 2, 4])
    nums.undo()
    nums.round_to(2)
    same(nums, np.round([0.5, 1.5, 2.5, 3.5, 2.675, 1234], 2))
    nums.round_to(-2)
    assert nums.get_number_at(6) == 1200
    with pytest.raises(SimplydataError, match="whole number"):
        nums.round_to(1.5)


def test_order_words():
    nums = number_list([3, NAN, 1, 2])
    nums.sort()
    same(nums, [1, 2, 3, NAN])
    nums.sort(biggest_first=True)
    same(nums, [3, 2, 1, NAN])
    nums.reverse()
    same(nums, [NAN, 1, 2, 3])
    nums = number_list([1, 2, NAN, 3])
    nums.turn_into_running_total()
    same(nums, pd.Series([1, 2, NAN, 3]).cumsum())
    with pytest.raises(SimplydataError, match="True or False"):
        nums.sort(biggest_first="yes")


def test_history_words(capsys):
    nums = number_list([1, 2, 3])
    nums.add(1)
    nums.times(2)
    nums.show_steps()
    assert "1. add 1\n2. times 2" in capsys.readouterr().out
    nums.start_again()
    same(nums, [1, 2, 3])
    nums.undo()
    same(nums, [4, 6, 8])
    nums.undo()
    nums.undo()
    nums.undo()
    assert "Nothing to undo" in capsys.readouterr().out
    same(nums, [1, 2, 3])


# ====================================================================== summaries
def test_summaries_match_numpy(capsys):
    v = np.array([3.0, 5.0, NAN, 2.0, 8.0])
    nums = number_list(v)
    assert nums.find_average() == pytest.approx(np.nanmean(v))
    assert nums.find_median() == pytest.approx(np.nanmedian(v))
    assert nums.find_total() == pytest.approx(np.nansum(v))
    assert nums.find_smallest() == 2 and nums.find_biggest() == 8
    assert nums.find_standard_deviation() == pytest.approx(np.nanstd(v, ddof=1))
    assert nums.find_standard_deviation() == pytest.approx(pd.Series(v).std())
    assert nums.find_percentile(90) == pytest.approx(np.nanpercentile(v, 90))
    assert nums.count() == 5 and nums.count_empty_numbers() == 1 and len(nums) == 5
    assert "1 empty value was skipped" in capsys.readouterr().out
    assert isinstance(number_list([1, 2]).find_total(), int)


def test_summaries_on_nothing(capsys):
    empty = number_list([NAN, NAN])
    assert np.isnan(empty.find_average())
    assert empty.find_total() == 0
    assert np.isnan(number_list([4]).find_standard_deviation())
    assert "at least 2 numbers" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="0 to 100"):
        number_list([1, 2]).find_percentile(120)


def test_count_each():
    table = number_list([2, 1, 2, NAN, 2, 1]).count_each()
    plain = table._done()
    assert list(plain.columns) == ["number", "count", "percent"]
    assert plain["number"].tolist()[:2] == [2, 1]
    assert plain["count"].tolist() == [3, 2, 1]
    assert plain["percent"].tolist() == [50.0, 33.3, 16.7]


def test_summary_names_and_hints():
    nums = number_list([1, 2])
    with pytest.raises(SimplydataError, match=r"numbers\.find_average\(\)"):
        nums.find_average_of()
    with pytest.raises(SimplydataError, match=r"numbers\.find_average\(\)"):
        nums.mean()
    with pytest.raises(SimplydataError, match=r"keep_each_number_that"):
        nums.keep_rows_where()
    with pytest.raises(SimplydataError, match="brackets"):
        nums.find_total = 3
    assert not hasattr(nums, "dtype")  # still an AttributeError for Python tools


# ====================================================================== grids
def test_grid_summaries_in_each():
    g = np.array([[1.0, 2.0, NAN], [4.0, 5.0, 6.0]])
    grid = number_grid(g)
    assert grid.find_average() == pytest.approx(np.nanmean(g))
    same(grid.find_average(in_each="row"), np.nanmean(g, axis=1))
    same(grid.find_total(in_each="column"), np.nansum(g, axis=0))
    same(grid.find_biggest(in_each="row"), np.nanmax(g, axis=1))
    same(grid.find_standard_deviation(in_each="column"), [np.std([1, 4], ddof=1), np.std([2, 5], ddof=1), NAN])
    same(grid.find_percentile(50, in_each="row"), np.nanmedian(g, axis=1))
    assert isinstance(grid.find_median(in_each="row"), Numbers)
    with pytest.raises(SimplydataError, match='Did you mean in_each="row"'):
        grid.find_average(in_each="rows")


def test_grid_maths_and_swap():
    g = np.arange(1, 7).reshape(2, 3)
    grid = number_grid(g)
    same(grid * 2, g * 2)
    same(grid + grid, g + g)
    same(grid + [10, 20, 30], g + [10, 20, 30])  # one number per column
    same(number_list([1, 1, 1]) + grid, g + 1)
    assert isinstance(grid ** 2, NumberGrid)
    grid.take_square_root()
    same(grid, np.sqrt(g))
    grid.undo()
    grid.swap_rows_and_columns()
    same(grid, g.T)
    assert grid.find_shape() == (3, 2)
    grid.undo()
    same(grid, g)
    with pytest.raises(SimplydataError, match="one for each column"):
        grid + [1, 2]
    same(np.sin(grid), np.sin(g))
    assert list(grid) == [[1, 2, 3], [4, 5, 6]]


# ====================================================================== finishing and charts
def test_done_table_save(tmp_path):
    nums = number_list([1, 2, 3])
    plain = nums.as_numpy()
    assert isinstance(plain, np.ndarray)
    plain[0] = 99
    assert nums.get_number_at(1) == 1  # as_numpy() gives a copy
    assert nums.turn_into_table(name="marks").get_column_names() == ["marks"]
    nums.save(tmp_path / "nums.csv")
    assert pd.read_csv(tmp_path / "nums.csv")["value"].tolist() == [1, 2, 3]
    grid = number_grid([[1, 2], [3, 4]])
    assert grid.turn_into_table().get_column_names() == ["1", "2"]
    grid.save(tmp_path / "grid.csv")
    assert pd.read_csv(tmp_path / "grid.csv").values.tolist() == [[1, 2], [3, 4]]
    with pytest.raises(SimplydataError, match="file type"):
        nums.save(tmp_path / "nums")
    same(np.asarray(nums), [1, 2, 3])


def test_charts_and_tables_accept_numbers():
    nums = number_list([3, 5, 2])
    assert is_listlike(nums)
    assert load(nums)["value"].tolist() == [3, 5, 2]
    grid = number_grid([[1, 2], [3, 4]])
    assert not is_listlike(grid)
    frame = load(grid)
    assert list(frame.columns) == ["1", "2"] and list(frame.index) == [1, 2]
    table, names = frame_for(pd.DataFrame(), y=nums)
    assert table[names["y"]].tolist() == [3, 5, 2]
    sdata.chart().draw_lines(nums).draw_dots(x=nums, y=nums * 2).draw_histogram(x=nums)._render()
    sdata.chart(grid).draw_heatmap(with_numbers=True)._render()
    grid.start_chart().draw_heatmap()._render()
    nums.start_chart().draw_bars(x=number_list(1, to=3), y="value")._render()
    assert sdata.table(nums).get_column_names() == ["value"]
    assert sdata.table(grid).count_rows() == 2


def test_every_word_has_a_docstring_with_an_example():
    # words shared by lists and grids (add, log, undo ...) show the list example
    for cls, name in ((Numbers, "numbers"), (NumberGrid, "grid")):
        for word in cls._word_names():
            doc = getattr(cls, word).__doc__ or ""
            assert doc.strip(), word
            assert re.search(rf"(?<![\w.])({name}|numbers)\.\w+\(", doc), f"{cls.__name__}.{word} has no example"


def test_fill_empty_numbers_with_the_line_between_neighbours(capsys):
    values = [np.nan, 1.0, np.nan, np.nan, 7.0, 8.0, np.nan]
    nums = number_list(values)
    nums.fill_empty_numbers(with_the="line between neighbours")
    expected = pd.Series(values).interpolate(limit_area="inside")
    same(nums.as_numpy(), expected.to_numpy())
    out = capsys.readouterr().out
    assert "Filled 2 empty values. 2 values stayed empty (at the start or end" in out
    number_list([1.0, np.nan, 3.0]).fill_empty_numbers(with_the="line between neighbors")  # US spelling too
