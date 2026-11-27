"""NumPy + SciPy phase, batch 1: fixes after the independent review (direction bookkeeping).

Each test failed before its fix. Results are compared with plain NumPy (or xarray) doing the same, and the words
that line blocks up by name are run with xarray and without it (the NumPy path), which must agree exactly.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata.numbers import _directions, blocks


@pytest.fixture(autouse=True)
def _notes_on():
    _directions.SETTINGS["stretching_notes"] = True
    yield
    _directions.SETTINGS["stretching_notes"] = True
    _directions.UNDERNEATH["named"] = "auto"


@pytest.fixture(params=["xarray", "numpy"])
def path(request, monkeypatch):
    """Run a test with xarray underneath (when installed) and with NumPy only."""
    if request.param == "xarray":
        pytest.importorskip("xarray")
    else:
        monkeypatch.setattr(blocks, "xarray_or_none", lambda: None)
        _directions.UNDERNEATH["named"] = "numpy"
    return request.param


def _labelled():
    frame = pd.DataFrame({"x": np.repeat([0, 10, 50], 4), "y": np.tile([1, 2, 3, 4], 3), "v": np.arange(12.0)})
    return sdata.number_block(frame, directions_named=["x", "y"], values="v")


# 1 ---------------------------------------------------------------- stack_up lines up by name
def test_stack_up_lines_up_names_given_in_another_order(capsys):
    a = np.array([[1, 2], [3, 4]])
    first = sdata.number_block(a, directions_named=["hour", "depth"])
    turned = sdata.number_block(a.T.copy(), directions_named=["depth", "hour"])
    stacked = sdata.stack_up([first, turned], as_new_direction="site")
    np.testing.assert_array_equal(stacked.as_numpy(), np.stack([a, a]))
    assert stacked.find_direction_names() == ["site", "hour", "depth"]
    assert "lined up by name" in capsys.readouterr().out


# 2 ---------------------------------------------------------------- over= uses the other block's names
def test_over_uses_the_other_blocks_names(path):
    values = np.arange(9.0).reshape(3, 3)
    weights = np.array([[0, 1, 2], [0, 0, 0], [0, 0, 0.0]])  # named column x row
    a = sdata.number_block(values, directions_named=["r", "c"])
    a.subtract(sdata.number_block(weights, directions_named=["c", "r"]), over=["r", "c"])
    np.testing.assert_array_equal(a.as_numpy(), values - weights.T)
    with pytest.raises(sdata.SimplydataError, match="directions are called"):
        sdata.number_block(values, directions_named=["r", "c"]).subtract(
            sdata.number_block(weights, directions_named=["c", "s"]), over=["r", "c"])


# 3 ---------------------------------------------------------------- rotate moves names and labels with the numbers
@pytest.mark.parametrize("turns", [1, 2, 3, -1])
def test_rotate_moves_names_and_labels_like_xarray(turns, capsys):
    xr = pytest.importorskip("xarray")
    da = xr.DataArray(np.arange(6.0).reshape(2, 3), dims=["hour", "depth"],
                      coords={"hour": [0, 1], "depth": [5, 10, 20]})
    block = sdata.number_block(da).rotate(by_quarter_turns=turns)
    np.testing.assert_array_equal(block.as_numpy(), np.rot90(da.values, turns))
    # each number keeps its own hour and depth: compare with xarray, read label by label
    names = block.find_direction_names()
    for i, first in enumerate(block._labels[names[0]]):
        for j, second in enumerate(block._labels[names[1]]):
            assert block.as_numpy()[i, j] == da.sel({names[0]: first, names[1]: second}).item()
    if turns % 2:
        assert names == ["depth", "hour"]
        assert "2 hours x 3 depths -> 3 depths x 2 hours" in capsys.readouterr().out


# 4 ---------------------------------------------------------------- keep_where(is_one_of=): one rule on both paths
def test_keep_where_one_of_keeps_the_order_given(path):
    kept = _labelled().keep_where("x", is_one_of=[50, 0])
    np.testing.assert_array_equal(kept.as_numpy(), np.arange(12.0).reshape(3, 4)[[2, 0]])
    np.testing.assert_array_equal(kept._labels["x"], [50, 0])


def test_keep_where_one_of_refuses_missing_labels(path):
    with pytest.raises(sdata.SimplydataError, match="x has no label 99"):
        _labelled().keep_where("x", is_one_of=[0, 99])


def test_a_direction_called_x_is_not_read_as_times(capsys):
    _labelled().keep_where("x", is_one_of=[0])
    out = capsys.readouterr().out
    assert "1 in x by 4 in y" in out and "x x" not in out


# 5 ---------------------------------------------------------------- named size-1 directions stretch
def test_named_size_one_direction_stretches(path, capsys):
    plate_values = np.arange(24 * 8 * 12, dtype=float).reshape(24, 8, 12)
    blank_values = np.random.default_rng(1).normal(size=(8, 12))
    plate = sdata.number_block(plate_values, directions_named=["hour", "row", "column"])
    blank = sdata.number_block(blank_values, directions_named=["row", "column"]).add_direction("hour")
    plate.subtract(blank)
    np.testing.assert_array_equal(plate.as_numpy(), plate_values - blank_values[np.newaxis])
    assert "were used again for each of the 24 hours" in capsys.readouterr().out
    turned = sdata.number_block(blank_values.T[:, np.newaxis, :].copy(), directions_named=["column", "hour", "row"])
    total = sdata.number_block(plate_values, directions_named=["hour", "row", "column"]) + turned
    np.testing.assert_array_equal(total.as_numpy(), plate_values + blank_values[np.newaxis])
    stretched = sdata.number_block(blank_values[np.newaxis], directions_named=["hour", "row", "column"])
    stretched.stretch_to(sdata.number_block(plate_values, directions_named=["hour", "row", "column"]))
    np.testing.assert_array_equal(stretched.as_numpy(), np.broadcast_to(blank_values, (24, 8, 12)))


# 6 ---------------------------------------------------------------- Fourier: the biggest away from frequency 0
def test_fourier_biggest_size_skips_frequency_zero_by_value(capsys):
    signal = [5, 5.1, 4.9, 5, 5.2, 4.8, 5, 5.1]
    sdata.number_list(signal).take_fourier_transform(time_step=1, with_zero_in_middle=True)
    out = capsys.readouterr().out
    assert "the biggest size (after frequency 0) is at -0.375" in out or "is at 0.375" in out


# 7 ---------------------------------------------------------------- smaller ones
def test_stretch_to_on_an_unnamed_block_gives_one_set_of_names():
    block = sdata.number_block(np.arange(3)).stretch_to((2, 3))
    np.testing.assert_array_equal(block.as_numpy(), np.broadcast_to(np.arange(3), (2, 3)))
    assert block.find_direction_names() == ["row", "column"]


def test_the_note_names_unnamed_numbers_by_what_they_line_up_with(capsys):
    plate = sdata.number_block(of_shape=(24, 8, 12), filled_with=5.0, directions_named=["hour", "row", "column"])
    plate.subtract(sdata.number_block(np.ones((1, 8, 12))))
    out = capsys.readouterr().out
    assert "(1 hour x 8 rows x 12 columns)" in out and "page" not in out


def test_keep_numbers_where_says_whole_numbers_became_decimals(capsys):
    values = np.arange(24).reshape(2, 3, 4)
    block = sdata.number_block(values)
    yes = block.turn_into_yes_or_no(is_above=10)
    capsys.readouterr()
    block.keep_numbers_where(yes)
    np.testing.assert_array_equal(block.as_numpy(), np.where(values > 10, values, np.nan))
    assert "whole numbers became decimal numbers" in capsys.readouterr().out


def test_rows_without_a_place_are_counted_in_a_note(capsys):
    frame = pd.DataFrame({"site": ["a", "a", None, "b"], "day": [1, 2, 1, 1], "v": [1.0, 2.0, 3.0, 4.0]})
    block = sdata.number_block(frame, directions_named=["site", "day"], values="v")
    assert "1 row with an empty site or day cell was left out" in capsys.readouterr().out
    expected = frame.dropna().pivot(index="site", columns="day", values="v").to_numpy()
    np.testing.assert_array_equal(block.as_numpy(), expected)
