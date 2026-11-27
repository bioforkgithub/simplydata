"""NumPy + SciPy phase, batch 1: words for numbers, grids and blocks alike, compared with plain NumPy.

Rounding, angles, yes or no values, counting and checking, where the biggest is, every pair, whole division, the
Fourier option with_zero_in_middle=, grid.keep_rows_where and the renamed table.find_values_at.
"""

from __future__ import annotations

import numpy as np
import pytest

import simplydata as sdata
from simplydata._errors import MissingWordError

VALUES = np.array([2.7, -2.3, -2.7, 0.5, 3.0, -0.5, 1.5])
ANGLES = np.array([0.0, 30.0, 45.0, 60.0, 90.0, 180.0, 270.0])
GRID = np.array([[3.0, 8.0, 1.0], [7.0, 2.0, 9.0], [4.0, 6.0, 5.0], [0.5, 0.25, 11.0]])
BLOCK = np.random.default_rng(5).normal(20, 4, size=(6, 4, 5))


@pytest.fixture(autouse=True)
def _stretching_notes_on():
    """A help example may have turned the notes off (sdata.hide_stretching_notes()); these tests read them."""
    from simplydata.numbers._directions import SETTINGS

    SETTINGS["stretching_notes"] = True
    yield
    SETTINGS["stretching_notes"] = True


def _three(values):
    """The same numbers as numbers (1-D), a grid (2-D) and a block (3-D)."""
    values = np.asarray(values)
    out = []
    if values.ndim == 1:
        out.append(sdata.number_list(values.tolist()))
    if values.ndim == 2:
        out.append(sdata.number_grid(values.tolist()))
    out.append(sdata.number_block(values))
    return out


# ---------------------------------------------------------------------- rounding
@pytest.mark.parametrize("word, func", [("round_down", np.floor), ("round_up", np.ceil),
                                        ("take_whole_part", np.trunc)])
@pytest.mark.parametrize("values", [VALUES, GRID - 5.5, BLOCK])
def test_rounding_words_equal_numpy(word, func, values):
    for obj in _three(values):
        getattr(obj, word)()
        np.testing.assert_array_equal(obj.as_numpy(), func(values))
        obj.undo()
        np.testing.assert_array_equal(obj.as_numpy(), values)


def test_rounding_whole_numbers_changes_nothing(capsys):
    nums = sdata.number_list([1, -2, 3])
    nums.round_down()
    np.testing.assert_array_equal(nums.as_numpy(), np.array([1, -2, 3]))
    assert "whole numbers already" in capsys.readouterr().out


# ---------------------------------------------------------------------- angles (radians by default, as NumPy)
@pytest.mark.parametrize("word, func", [("take_sin", np.sin), ("take_cos", np.cos), ("take_tan", np.tan)])
def test_trigonometry_radians_and_degrees(word, func):
    radians = sdata.number_list(ANGLES.tolist())
    getattr(radians, word)()
    np.testing.assert_allclose(radians.as_numpy(), func(ANGLES), rtol=1e-14, atol=1e-15)
    degrees = sdata.number_list(ANGLES.tolist())
    getattr(degrees, word)(degrees=True)
    np.testing.assert_allclose(degrees.as_numpy(), func(np.deg2rad(ANGLES)), rtol=1e-14, atol=1e-15)
    block = sdata.number_block(BLOCK)
    getattr(block, word)(degrees=True)
    np.testing.assert_allclose(block.as_numpy(), func(np.deg2rad(BLOCK)), rtol=1e-14)


def test_change_angles_to():
    nums = sdata.number_list(ANGLES.tolist())
    nums.change_angles_to("radians")
    np.testing.assert_allclose(nums.as_numpy(), np.deg2rad(ANGLES), rtol=1e-15)
    nums.change_angles_to("degrees")
    np.testing.assert_allclose(nums.as_numpy(), np.rad2deg(np.deg2rad(ANGLES)), rtol=1e-15)
    with pytest.raises(sdata.SimplydataError, match="degrees"):
        nums.change_angles_to("degree")


def test_divide_rounding_down_and_by_zero(capsys):
    nums = sdata.number_list([7, -7, 9, 4])
    nums.divide_by(2, rounding_down=True)
    np.testing.assert_array_equal(nums.as_numpy(), np.floor_divide(np.array([7, -7, 9, 4]), 2))
    nums = sdata.number_list([7.0, -7.0, 9.0])
    nums.divide_by([2, 0, 4], rounding_down=True)
    got = nums.as_numpy()
    expected = np.floor_divide(np.array([7.0, -7.0, 9.0]), np.array([2.0, 1.0, 4.0]))
    assert np.isnan(got[1]) and got[0] == expected[0] and got[2] == expected[2]
    assert "1 number is now empty" in capsys.readouterr().out
    block = sdata.number_block(np.arange(24).reshape(2, 3, 4))
    block.divide_by(5, rounding_down=True)
    np.testing.assert_array_equal(block.as_numpy(), np.arange(24).reshape(2, 3, 4) // 5)


# ---------------------------------------------------------------------- yes or no (P01, P02, P08, P09, P37)
def test_turn_into_yes_or_no_and_the_symbols():
    sst = sdata.number_list([18.0, 21.5, np.nan, 25.0, 19.0])
    warm = sst.turn_into_yes_or_no(is_above=20)
    np.testing.assert_array_equal(warm.as_numpy(), np.array([18.0, 21.5, np.nan, 25.0, 19.0]) > 20)
    np.testing.assert_array_equal(sst.as_numpy(), [18.0, 21.5, np.nan, 25.0, 19.0], err_msg="unchanged")
    cool = sst.turn_into_yes_or_no(is_below=24)
    raw = np.array([18.0, 21.5, np.nan, 25.0, 19.0])
    np.testing.assert_array_equal((warm & cool).as_numpy(), np.logical_and(raw > 20, raw < 24))
    np.testing.assert_array_equal((warm | cool).as_numpy(), np.logical_or(raw > 20, raw < 24))
    np.testing.assert_array_equal((~warm).as_numpy(), np.logical_not(raw > 20))
    assert "yes or no" in repr(warm)
    with pytest.raises(sdata.SimplydataError, match="yes or no"):
        ~sst


def test_keep_remove_and_replace_numbers_where():
    depth = np.array([5, 150, 80, 300, 20])
    nitrate = np.array([1.1, 9.5, 4.2, 12.0, 2.0])
    deep = sdata.number_list(depth.tolist()).turn_into_yes_or_no(is_above=100)
    kept = sdata.number_list(nitrate.tolist()).keep_numbers_where(deep)
    np.testing.assert_array_equal(kept.as_numpy(), nitrate[depth > 100])
    removed = sdata.number_list(nitrate.tolist()).remove_numbers_where(deep)
    np.testing.assert_array_equal(removed.as_numpy(), nitrate[~(depth > 100)])
    replaced = sdata.number_list(nitrate.tolist()).replace_numbers_where(deep, with_value="empty")
    np.testing.assert_array_equal(replaced.as_numpy(), np.where(depth > 100, np.nan, nitrate))
    replaced = sdata.number_list(nitrate.tolist()).replace_numbers_where(deep, with_value=0)
    np.testing.assert_array_equal(replaced.as_numpy(), np.where(depth > 100, 0, nitrate))


def test_keep_numbers_where_on_grids_and_blocks_keeps_the_shape():
    land = sdata.number_block(BLOCK).turn_into_yes_or_no(is_below=18)
    kept = sdata.number_block(BLOCK).keep_numbers_where(~land)
    np.testing.assert_array_equal(kept.as_numpy(), np.where(~(BLOCK < 18), BLOCK, np.nan))
    grid = sdata.number_grid(GRID.tolist())
    big = grid.turn_into_yes_or_no(is_at_least=5)
    grid.remove_numbers_where(big)
    np.testing.assert_array_equal(grid.as_numpy(), np.where(GRID >= 5, np.nan, GRID))


def test_replace_each_number_that_takes_empty():
    nums = sdata.number_list([1.0, -3.0, 4.0])
    nums.replace_each_number_that(is_below=0, with_value="empty")
    np.testing.assert_array_equal(nums.as_numpy(), np.where(np.array([1.0, -3.0, 4.0]) < 0, np.nan, [1.0, -3.0, 4.0]))


@pytest.mark.parametrize("values", [VALUES, GRID, BLOCK])
def test_count_numbers_that_equals_count_nonzero(values):
    for obj in _three(values):
        assert obj.count_numbers_that(is_above=1) == np.count_nonzero(values > 1)
    block = sdata.number_block(BLOCK, directions_named=["day", "row", "column"])
    np.testing.assert_array_equal(block.count_numbers_that(is_above=20, over="day").as_numpy(),
                                  np.count_nonzero(BLOCK > 20, axis=0))
    grid = sdata.number_grid(GRID.tolist())
    np.testing.assert_array_equal(grid.count_numbers_that(is_above=4, in_each="row").as_numpy(),
                                  np.count_nonzero(GRID > 4, axis=1))


def test_check_if_any_and_all(capsys):
    counts = sdata.number_grid(GRID.tolist())
    assert counts.check_if_all_numbers(is_at_least=0) is bool(np.all(GRID >= 0))
    assert "Yes: all 12 numbers are at least 0" in capsys.readouterr().out
    assert counts.check_if_any_number(is_above=10) is bool(np.any(GRID > 10))
    assert counts.check_if_all_numbers(is_above=1) is bool(np.all(GRID > 1))
    block = sdata.number_block(BLOCK, directions_named=["day", "row", "column"])
    np.testing.assert_array_equal(block.check_if_any_number(is_above=25, over="day").as_numpy(),
                                  np.any(BLOCK > 25, axis=0))
    with_empty = sdata.number_list([1.0, np.nan, 3.0])
    assert with_empty.check_if_all_numbers(is_above=0) is True  # empty values are skipped


def test_yes_or_no_counts_the_yes():
    warm = sdata.number_block(BLOCK).turn_into_yes_or_no(is_above=22)
    assert warm.count_numbers_that() == np.count_nonzero(BLOCK > 22)
    assert warm.count_numbers_that(is_equal_to=False) == np.count_nonzero(~(BLOCK > 22))


# ---------------------------------------------------------------------- comparing and positions
def test_check_if_same_as():
    a = sdata.number_list([0.1 + 0.2, 1.0])
    assert a.check_if_same_as([0.3, 1.0]) is bool(np.array_equal([0.1 + 0.2, 1.0], [0.3, 1.0]))
    assert a.check_if_same_as([0.3, 1.0], within=1e-12) is bool(np.allclose([0.1 + 0.2, 1.0], [0.3, 1.0], rtol=0,
                                                                            atol=1e-12))
    grid = sdata.number_grid([[1.0, np.nan], [2.0, 3.0]])
    assert grid.check_if_same_as(sdata.number_grid([[1.0, np.nan], [2.0, 3.0]])) is True
    assert sdata.number_block(BLOCK).check_if_same_as(BLOCK[:, :, :4]) is False
    with pytest.raises(MissingWordError, match="check_if_same_as"):
        sdata.number_list([1, 2]).allclose


def test_find_where_biggest_and_smallest_count_from_one(capsys):
    nums = sdata.number_list([12, 15, 9, 20, 14])
    assert nums.find_where_biggest() == int(np.argmax([12, 15, 9, 20, 14])) + 1
    assert "is at position 4 (NumPy index 3)" in capsys.readouterr().out
    assert nums.find_where_smallest() == int(np.argmin([12, 15, 9, 20, 14])) + 1
    grid = sdata.number_grid(GRID.tolist())
    expected = tuple(int(i) + 1 for i in np.unravel_index(np.argmax(GRID), GRID.shape))
    assert grid.find_where_biggest() == expected
    np.testing.assert_array_equal(grid.find_where_biggest(over="column").as_numpy(), np.argmax(GRID, axis=1) + 1)
    block = sdata.number_block(BLOCK, directions_named=["image", "row", "column"])
    np.testing.assert_array_equal(block.find_where_smallest(over="image").as_numpy(), np.argmin(BLOCK, axis=0) + 1)
    assert block.find_where_biggest() == tuple(int(i) + 1 for i in np.unravel_index(np.argmax(BLOCK), BLOCK.shape))
    gaps = sdata.number_list([np.nan, 3.0, 7.0])
    assert gaps.find_where_biggest() == int(np.nanargmax([np.nan, 3.0, 7.0])) + 1


def test_make_pair_table_with_equals_outer():
    depths = np.array([0.0, 10.0, 50.0, 200.0])
    table = sdata.number_list(depths.tolist()).make_pair_table_with(depths.tolist(), by_subtracting=True)
    np.testing.assert_array_equal(table.as_numpy(), np.subtract.outer(depths, depths))
    times = sdata.number_list([1, 2, 3]).make_pair_table_with([4, 5])
    np.testing.assert_array_equal(times.as_numpy(), np.multiply.outer([1, 2, 3], [4, 5]))
    added = sdata.number_grid([[1, 2], [3, 4]]).make_pair_table_with([10, 20, 30], by_adding=True)
    np.testing.assert_array_equal(added.as_numpy(), np.add.outer(np.array([[1, 2], [3, 4]]), [10, 20, 30]))
    kron = sdata.number_grid([[1, 2], [3, 4]]).make_pair_table_with(sdata.number_grid([[0, 1], [1, 0]]), as_blocks=True)
    np.testing.assert_array_equal(kron.as_numpy(), np.kron([[1, 2], [3, 4]], [[0, 1], [1, 0]]))
    divided = sdata.number_list([1.0, 2.0]).make_pair_table_with([2.0, 0.0], by_dividing=True)
    expected = np.divide.outer([1.0, 2.0], [2.0, 1.0])
    np.testing.assert_array_equal(divided.as_numpy()[:, 0], expected[:, 0])
    assert np.isnan(divided.as_numpy()[:, 1]).all()
    with pytest.raises(MissingWordError, match="make_pair_table_with"):
        sdata.number_list([1, 2]).times_table_with


# ---------------------------------------------------------------------- grids: rows by a test on one column (P03)
def test_grid_keep_and_remove_rows_where():
    grid = sdata.number_grid(GRID.tolist())
    grid.keep_rows_where(column=3, is_above=4.5)
    np.testing.assert_array_equal(grid.as_numpy(), GRID[GRID[:, 2] > 4.5])
    grid = sdata.number_grid(GRID.tolist())
    grid.remove_rows_where(column=1, is_between=[3, 5])
    np.testing.assert_array_equal(grid.as_numpy(), GRID[~((GRID[:, 0] >= 3) & (GRID[:, 0] <= 5))])
    with pytest.raises(sdata.SimplydataError, match="column="):
        sdata.number_grid(GRID.tolist()).keep_rows_where(column="a", is_above=1)


# ---------------------------------------------------------------------- Fourier with zero in the middle
def test_fourier_with_zero_in_middle_and_back():
    from scipy import fft

    x = np.sin(np.linspace(0, 8 * np.pi, 64, endpoint=False)) + 0.25
    table = sdata.number_list(x.tolist()).take_fourier_transform(time_step=0.1, with_zero_in_middle=True)
    frame = table.as_pandas()
    np.testing.assert_array_equal(frame["frequency"].to_numpy(), fft.fftshift(fft.fftfreq(64, d=0.1)))
    np.testing.assert_allclose(frame["size"].to_numpy(), np.abs(fft.fftshift(fft.fft(x))), rtol=1e-12)
    back = sdata.find_inverse_fourier_transform(table)
    np.testing.assert_allclose(back.as_numpy(), x, atol=1e-12)


# ---------------------------------------------------------------------- renamed: table.find_values_at
def test_find_values_at_and_the_old_name(capsys):
    growth = sdata.get_example("growth")
    new = growth.find_values_at("population", at={"year": [2001, 2003]}, for_each_group_in="country")
    old = sdata.get_example("growth").values_at("population", at={"year": [2001, 2003]}, for_each_group_in="country")
    assert "is now called" in capsys.readouterr().out
    assert new.as_pandas().equals(old.as_pandas())
