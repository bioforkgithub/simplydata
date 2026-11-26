"""Numbers phase, batch 3: the new words on numbers and grids, each against NumPy or SciPy doing the same."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import fft, linalg, ndimage, signal

import simplydata as sdata
from simplydata._other_names import OTHER_NAMES

PLATE = [[1, 8, 9, 2], [0, 7, 1, 1], [6, 0, 0, 9]]


def test_take_cube_root_is_numpy_cbrt_on_numbers_and_grids():
    values = [27, -8, 1000, 2, 0.001]
    nums = sdata.numbers(values)
    nums.take_cube_root()
    np.testing.assert_array_equal(nums.as_numpy(), np.cbrt(np.array(values, dtype=float)))
    assert nums.get_number_at(2) == -2.0  # raise_to_power(1/3) would give an empty value here
    grid = sdata.number_grid([[8, -27], [1, 64]])
    grid.take_cube_root()
    np.testing.assert_array_equal(grid.as_numpy(), np.cbrt(np.array([[8, -27], [1, 64]], dtype=float)))
    grid.undo()
    np.testing.assert_array_equal(grid.as_numpy(), [[8, -27], [1, 64]])


def test_take_cosine_transform_is_scipy_dct_ortho():
    values = [1.0, 2, 3, 4, 7, 1]
    nums = sdata.numbers(values)
    nums.take_cosine_transform()
    np.testing.assert_array_equal(nums.as_numpy(), fft.dct(values, type=2, norm="ortho"))
    assert (nums.as_numpy() ** 2).sum() == pytest.approx(sum(v * v for v in values), rel=1e-14)
    with pytest.raises(sdata.SimplydataError, match="fill the empty"):
        sdata.numbers([1, None]).take_cosine_transform()


def test_find_coherence_with_is_scipy_coherence():
    t = 0.01 * np.arange(2000)
    a = np.sin(2 * np.pi * 5 * t) + 0.3 * np.cos(2 * np.pi * 17 * t)
    b = np.sin(2 * np.pi * 5 * t + 1) + np.cos(2 * np.pi * 13 * t)
    table = sdata.numbers(a).find_coherence_with(b, time_step=0.01).as_pandas()
    f, c = signal.coherence(a, b, fs=100, nperseg=256)  # long enough for SciPy's own segments
    np.testing.assert_array_equal(table["frequency"], f)
    np.testing.assert_allclose(table["coherence"], c, rtol=1e-13)
    short = sdata.numbers(a[:300]).find_coherence_with(b[:300], time_step=0.01).as_pandas()
    f2, c2 = signal.coherence(a[:300], b[:300], fs=100, nperseg=int(300 // 4.5))  # eight half-overlapping segments
    np.testing.assert_allclose(short["coherence"], c2, rtol=1e-13)
    with pytest.raises(sdata.SimplydataError, match="same length"):
        sdata.numbers(a).find_coherence_with(b[:10])


def test_get_numbers_at_pairs_counts_from_1():
    g = np.array(PLATE)
    found = sdata.number_grid(PLATE).get_numbers_at_pairs(rows=[1, 2, 3], columns=[2, 2, 4])
    np.testing.assert_array_equal(found.as_numpy(), g[[0, 1, 2], [1, 1, 3]])
    with pytest.raises(sdata.SimplydataError, match="as many rows as columns"):
        sdata.number_grid(PLATE).get_numbers_at_pairs(rows=[1, 2], columns=[1])
    with pytest.raises(sdata.SimplydataError, match="from 1 to 3"):
        sdata.number_grid(PLATE).get_numbers_at_pairs(rows=[0], columns=[1])


def test_get_numbers_from_each_row_at_is_take_along_axis():
    g = np.array(PLATE)
    positions = [[4, 1], [2, 2], [1, 3]]
    found = sdata.number_grid(PLATE).get_numbers_from_each_row_at(columns=positions)
    np.testing.assert_array_equal(found.as_numpy(), np.take_along_axis(g, np.array(positions) - 1, axis=1))
    one = sdata.number_grid(PLATE).get_numbers_from_each_row_at(columns=[3, 2, 4])
    np.testing.assert_array_equal(one.as_numpy(), [9, 7, 9])
    with pytest.raises(sdata.SimplydataError, match="each of the 3 rows"):
        sdata.number_grid(PLATE).get_numbers_from_each_row_at(columns=[1, 2])


@pytest.mark.parametrize("touching, connect", [("sides", 1), ("corners", 2)])
def test_find_each_patch_that_is_ndimage_label(touching, connect):
    g = np.array([[1, 8, 9, 2], [0, 0, 1, 7], [6, 0, 6, 9]], dtype=float)
    table = sdata.number_grid(g.tolist()).find_each_patch_that(is_above=5, touching=touching).as_pandas()
    labels, n = ndimage.label(g > 5, structure=ndimage.generate_binary_structure(2, connect))
    index = np.arange(1, n + 1)
    assert len(table) == n
    np.testing.assert_array_equal(table["total"], ndimage.sum_labels(g, labels, index))
    np.testing.assert_allclose(table["average"], ndimage.mean(g, labels, index), rtol=1e-15)
    centres = np.array(ndimage.center_of_mass(g > 5, labels, index))
    np.testing.assert_allclose(table[["centre row", "centre column"]].to_numpy(), centres + 1, rtol=1e-15)
    assert n == (3 if touching == "sides" else 2)


def test_find_each_patch_that_leaves_out_empty_cells_and_finds_none():
    grid = sdata.number_grid([[9, None], [None, 9]])
    assert len(grid.find_each_patch_that(is_above=5).as_pandas()) == 2
    assert len(sdata.number_grid(PLATE).find_each_patch_that(is_above=100).as_pandas()) == 0


@pytest.mark.parametrize("method, order", [("linear", 1), ("nearest", 0), ("cubic", 3)])
def test_change_size_to_is_ndimage_zoom(method, order):
    g = np.array(PLATE, dtype=float)
    grid = sdata.number_grid(PLATE)
    grid.change_size_to(rows=6, columns=10, test_method=method)
    np.testing.assert_array_equal(grid.as_numpy(), ndimage.zoom(g, (6 / 3, 10 / 4), order=order))
    assert grid.find_shape() == (6, 10)


def test_rotate_is_ndimage_rotate_with_empty_outside():
    g = np.array(PLATE, dtype=float)
    grid = sdata.number_grid(PLATE)
    grid.rotate(by_degrees=30)
    np.testing.assert_array_equal(grid.as_numpy(), ndimage.rotate(g, 30, reshape=False, order=1, mode="constant",
                                                                  cval=np.nan))
    square = sdata.number_grid([[1, 2], [3, 4]])
    square.rotate(by_degrees=90)
    np.testing.assert_allclose(square.as_numpy(), np.rot90([[1, 2], [3, 4]]), atol=1e-12)  # anticlockwise


def test_take_matrix_exp_is_scipy_expm_and_not_take_exp():
    rates = [[-0.5, 0.5], [0.2, -0.2]]
    grid = sdata.number_grid(rates)
    grid.take_matrix_exp()
    np.testing.assert_array_equal(grid.as_numpy(), linalg.expm(np.array(rates)))
    # a closed form: exp of [[0, t], [-t, 0]] is a rotation by t radians
    turn = sdata.number_grid([[0, 1], [-1, 0]])
    turn.take_matrix_exp()
    np.testing.assert_allclose(turn.as_numpy(), [[np.cos(1), np.sin(1)], [-np.sin(1), np.cos(1)]], rtol=1e-14)
    with pytest.raises(sdata.SimplydataError, match="square"):
        sdata.number_grid(PLATE).take_matrix_exp()


def test_find_null_space_is_scipy_null_space():
    a = np.array([[1, 2, 3], [2, 4, 6]], dtype=float)
    found = sdata.number_grid(a.tolist()).find_null_space().as_numpy()
    np.testing.assert_array_equal(found, linalg.null_space(a))
    assert found.shape == (3, 2) and np.abs(a @ found).max() < 1e-12
    assert sdata.number_grid([[1, 0], [0, 1]]).find_null_space().find_shape() == (2, 0)


def test_grid_and_number_other_names_point_to_the_new_words():
    grid = sdata.number_grid(PLATE)
    for name, word in [("expm", "take_matrix_exp"), ("null_space", "find_null_space"), ("zoom", "change_size_to"),
                       ("take_along_axis", "get_numbers_from_each_row_at"), ("label", "find_each_patch_that")]:
        with pytest.raises(AttributeError, match=word):
            getattr(grid, name)
    nums = sdata.numbers([1, 2])
    for name in ("cbrt", "dct", "coherence", "cumulative_trapezoid", "nsimplify"):
        assert name in OTHER_NAMES["numbers"]
        with pytest.raises(AttributeError):
            getattr(nums, name)
