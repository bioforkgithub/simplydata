"""NumPy + SciPy phase, batch 1: blocks of numbers (n directions), compared with plain NumPy doing the same.

Exact equality for whole-number results, tight tolerances for decimals; shapes are compared too. Every word is run
next to the NumPy call it names, never against itself.
"""

from __future__ import annotations

import numpy as np
import pytest

import simplydata as sdata
from simplydata._errors import MissingWordError
from simplydata.numbers import _directions
from simplydata.numbers.blocks import NumberBlock

RNG = np.random.default_rng(11)
PLATE = RNG.normal(0.5, 0.2, size=(24, 8, 12))  # OD600 readings: 24 hours x 8 rows x 12 columns
WHOLE = np.arange(2 * 3 * 4 * 5).reshape(2, 3, 4, 5)


@pytest.fixture(autouse=True)
def _stretching_notes_on():
    """A help example may have turned the notes off (sdata.hide_stretching_notes()); these tests read them."""
    from simplydata.numbers._directions import SETTINGS

    SETTINGS["stretching_notes"] = True
    yield
    SETTINGS["stretching_notes"] = True


def plate(named=True):
    return sdata.number_block(PLATE.copy(), directions_named=["hour", "row", "column"] if named else None)


# ---------------------------------------------------------------------- making and looking
def test_number_block_from_lists_arrays_and_shapes():
    block = sdata.number_block([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
    assert isinstance(block, NumberBlock)
    np.testing.assert_array_equal(block.as_numpy(), np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]]))
    assert block.as_numpy().dtype == np.int64
    filled = sdata.number_block(of_shape=(24, 8, 12), filled_with=0)
    np.testing.assert_array_equal(filled.as_numpy(), np.zeros((24, 8, 12)))
    empty = sdata.number_block(of_shape=(2, 3), filled_with=None)
    assert np.isnan(empty.as_numpy()).all()
    like = sdata.number_block(like=plate(), filled_with=1)
    np.testing.assert_array_equal(like.as_numpy(), np.ones_like(PLATE))
    assert like.find_direction_names() == ["hour", "row", "column"]


def test_default_names_page_book_and_letters(capsys):
    assert sdata.number_block(of_shape=(2, 3, 4)).find_direction_names() == ["page", "row", "column"]
    assert sdata.number_block(WHOLE).find_direction_names() == ["book", "page", "row", "column"]
    six = sdata.number_block(of_shape=(1, 2, 1, 2, 3, 4)).find_direction_names()
    assert six == ["direction a", "direction b", "book", "page", "row", "column"]
    print(sdata.number_block(of_shape=(24, 8, 12)))
    out = capsys.readouterr().out
    assert "24 pages x 8 rows x 12 columns (NumPy: array, PyTorch: tensor)" in out
    assert "page 1 of 24 (8 rows x 12 columns)" in out
    assert "... and 21 more" in out


def test_shape_words_and_numpy_shape(capsys):
    block = plate()
    assert block.find_shape() == PLATE.shape
    assert "24 hours x 8 rows x 12 columns (NumPy shape (24, 8, 12))" in capsys.readouterr().out
    assert block.count_directions() == PLATE.ndim
    assert block.count() == PLATE.size


def test_get_number_at_counts_from_one():
    block = plate()
    assert block.get_number_at(hour=3, row=2, column=5) == PLATE[2, 1, 4]
    assert block.get_number_at(3, 2, 5) == PLATE[2, 1, 4]
    assert block.get_number_at(hour="last", row=1, column=1) == PLATE[-1, 0, 0]
    with pytest.raises(sdata.SimplydataError, match="from 1 to 24"):
        block.get_number_at(hour=0, row=1, column=1)
    np.testing.assert_array_equal(block.get_all_numbers().as_numpy(), PLATE.ravel())


# ---------------------------------------------------------------------- summaries over directions
@pytest.mark.parametrize("word, func", [
    ("find_average", np.nanmean), ("find_median", np.nanmedian), ("find_total", np.nansum),
    ("find_smallest", np.nanmin), ("find_biggest", np.nanmax)])
def test_summaries_over_and_in_each_equal_numpy(word, func):
    block = plate()
    result = getattr(block, word)(over="hour")
    np.testing.assert_allclose(result.as_numpy(), func(PLATE, axis=0), rtol=1e-12)
    assert result.find_direction_names() == ["row", "column"]
    kept = getattr(block, word)(in_each="column")
    np.testing.assert_allclose(kept.as_numpy(), func(PLATE, axis=(0, 1)), rtol=1e-12)
    assert getattr(block, word)() == pytest.approx(func(PLATE), rel=1e-12)


def test_standard_deviation_and_percentile_with_empty_values():
    values = PLATE.copy()
    values[0, 0, 0] = np.nan
    block = sdata.number_block(values, directions_named=["hour", "row", "column"])
    np.testing.assert_allclose(block.find_standard_deviation(over="hour").as_numpy(),
                               np.nanstd(values, axis=0, ddof=1), rtol=1e-12)
    np.testing.assert_allclose(block.find_percentile(90, over=["row", "column"]).as_numpy(),
                               np.nanpercentile(values, 90, axis=(1, 2)), rtol=1e-12)


def test_whole_number_totals_are_exact():
    block = sdata.number_block(WHOLE)
    np.testing.assert_array_equal(block.find_total(over="page").as_numpy(), WHOLE.sum(axis=1))
    np.testing.assert_array_equal(block.turn_into_running_total(over="column").as_numpy(), np.cumsum(WHOLE, axis=3))


def test_only_show_new_shape_changes_nothing(capsys):
    block = plate()
    assert block.find_average(over="hour", only_show_new_shape=True) is None
    assert "-> 8 rows x 12 columns (nothing changed). NumPy: np.nanmean(block, axis=0)" in capsys.readouterr().out
    block.change_shape_to(24, "rest", only_show_new_shape=True)
    assert "24 hours x 8 rows x 12 columns -> 24 rows x 96 columns (nothing changed)" in capsys.readouterr().out
    np.testing.assert_array_equal(block.as_numpy(), PLATE)


# ---------------------------------------------------------------------- shape and directions
def test_change_shape_to_equals_reshape(capsys):
    block = plate()
    block.change_shape_to(one_row_per="hour")
    np.testing.assert_array_equal(block.as_numpy(), PLATE.reshape(24, -1))
    assert "24 hours x 8 rows x 12 columns -> 24 rows x 96 columns. NumPy: block.reshape(24, -1)" in capsys.readouterr().out
    block.undo()
    np.testing.assert_array_equal(block.as_numpy(), PLATE)
    assert block.find_direction_names() == ["hour", "row", "column"]
    block.change_shape_to(8, "rest")
    np.testing.assert_array_equal(block.as_numpy(), PLATE.reshape(8, -1))
    block.start_again()
    block.change_shape_to(5, 7, fill="repeat")
    np.testing.assert_array_equal(block.as_numpy(), np.resize(PLATE, (5, 7)))
    with pytest.raises(sdata.SimplydataError, match="move_direction"):
        plate().change_shape_to(one_row_per="column")


def test_direction_words_equal_numpy():
    block = plate()
    block.add_direction("plate", at_position=1)
    np.testing.assert_array_equal(block.as_numpy(), np.expand_dims(PLATE, 0))
    block.remove_directions_of_size_one()
    np.testing.assert_array_equal(block.as_numpy(), PLATE)
    block.swap_directions("row", "column")
    np.testing.assert_array_equal(block.as_numpy(), np.swapaxes(PLATE, 1, 2))
    assert block.find_direction_names() == ["hour", "column", "row"]
    block.move_direction("hour", to_position=3)
    np.testing.assert_array_equal(block.as_numpy(), np.moveaxis(np.swapaxes(PLATE, 1, 2), 0, 2))


def test_order_words_equal_numpy():
    whole = sdata.number_block(WHOLE)
    np.testing.assert_array_equal(whole.reverse(over="row").as_numpy(), np.flip(WHOLE, axis=2))
    whole.undo()
    np.testing.assert_array_equal(whole.reverse().as_numpy(), np.flip(WHOLE))
    whole.undo()
    np.testing.assert_array_equal(whole.rotate(by_quarter_turns=1).as_numpy(), np.rot90(WHOLE, 1, axes=(2, 3)))
    whole.undo()
    np.testing.assert_array_equal(whole.rotate(by_quarter_turns=-1, over=["page", "row"]).as_numpy(),
                                  np.rot90(WHOLE, -1, axes=(1, 2)))
    whole.undo()
    np.testing.assert_array_equal(whole.move_round_by(3, over="column").as_numpy(), np.roll(WHOLE, 3, axis=3))
    whole.undo()
    np.testing.assert_array_equal(whole.insert_numbers(0, at_position=2, over="page").as_numpy(),
                                  np.insert(WHOLE, 1, 0, axis=1))


def test_keep_and_remove_by_position_in():
    block = plate()
    block.keep_by_position_in("hour", [1, 3])
    np.testing.assert_array_equal(block.as_numpy(), np.take(PLATE, [0, 2], axis=0))
    block = plate().remove_by_position_in("column", 1, to=3)
    np.testing.assert_array_equal(block.as_numpy(), np.delete(PLATE, [0, 1, 2], axis=2))
    with pytest.raises(sdata.SimplydataError, match="count from 1"):
        plate().keep_by_position_in("hour", 0)


def test_repeat_stack_join_and_split_equal_numpy():
    small = np.arange(6).reshape(2, 3)
    block = sdata.number_block(small)
    np.testing.assert_array_equal(block.repeat_each_number(2, over="row").as_numpy(), np.repeat(small, 2, axis=0))
    block.undo()
    np.testing.assert_array_equal(block.repeat_whole_block(3, over="column").as_numpy(), np.tile(small, (1, 3)))
    block.undo()
    block.repeat_whole_block(4, over="hour")
    np.testing.assert_array_equal(block.as_numpy(), np.tile(small, (4, 1, 1)))
    assert block.find_direction_names() == ["hour", "row", "column"]
    stacked = sdata.stack_up([small, small * 2, small * 3], as_new_direction="image")
    np.testing.assert_array_equal(stacked.as_numpy(), np.stack([small, small * 2, small * 3]))
    joined = sdata.number_block(small).add_numbers_from(small + 10, over="row")
    np.testing.assert_array_equal(joined.as_numpy(), np.concatenate([small, small + 10], axis=0))
    pieces = plate().split_into_pieces(5, over="hour")
    for ours, theirs in zip(pieces, np.array_split(PLATE, 5, axis=0)):
        np.testing.assert_array_equal(ours.as_numpy(), theirs)
    each = plate().split_into_one_block_per("row")
    assert len(each) == 8
    np.testing.assert_array_equal(each[2].as_numpy(), PLATE[:, 2, :])


# ---------------------------------------------------------------------- stretching (P04, P05, P07, P48)
def test_words_stretch_and_say_so(capsys):
    blank = RNG.normal(0.05, 0.01, size=(8, 12))
    block = plate()
    block.subtract(sdata.number_block(blank))
    np.testing.assert_allclose(block.as_numpy(), PLATE - blank, rtol=0, atol=0)
    assert "were used again for each of the 24 hours" in capsys.readouterr().out
    block.undo()
    block.subtract(blank[:, 0], over="row")
    np.testing.assert_array_equal(block.as_numpy(), PLATE - blank[:, 0][np.newaxis, :, np.newaxis])


def test_symbols_follow_numpy_broadcasting_for_random_shapes():
    rng = np.random.default_rng(3)
    for _ in range(60):
        ndim_a, ndim_b = rng.integers(1, 5, size=2)
        a = rng.integers(-5, 5, size=tuple(rng.choice([1, 2, 3], size=ndim_a)))
        b = rng.integers(-5, 5, size=tuple(rng.choice([1, 2, 3], size=ndim_b)))
        try:
            expected = a + b
        except ValueError:
            with pytest.raises(sdata.SimplydataError, match="Cannot combine"):
                sdata.number_block(a) + sdata.number_block(b)
            continue
        got = sdata.number_block(a) + sdata.number_block(b)
        np.testing.assert_array_equal(got.as_numpy(), expected)


def test_clash_message_lines_up_from_the_right():
    with pytest.raises(sdata.SimplydataError) as info:
        plate(named=False) - sdata.number_list(list(range(8)))
    text = str(info.value)
    assert text.startswith("Cannot combine 24 pages x 8 rows x 12 columns with 8 numbers.")
    assert "<- needs 12, or 1" in text
    assert 'For one number per row:  block.subtract(other, over="row")' in text
    assert len(text.splitlines()) <= 5


def test_line_up_by_name_xarray_and_numpy_agree():
    pytest.importorskip("xarray")
    block = plate()
    turned = sdata.number_block(PLATE.mean(axis=0).T.copy(), directions_named=["column", "row"])
    by_xarray = (block - turned).as_numpy()
    _directions.UNDERNEATH["named"] = "numpy"
    try:
        by_numpy = (block - turned).as_numpy()
    finally:
        _directions.UNDERNEATH["named"] = "auto"
    np.testing.assert_array_equal(by_xarray, by_numpy)
    np.testing.assert_array_equal(by_numpy, PLATE - PLATE.mean(axis=0))


def test_named_blocks_line_up_without_keepdims():
    block = plate()
    centred = block - block.find_average(over="hour")
    np.testing.assert_allclose(centred.as_numpy(), PLATE - PLATE.mean(axis=0, keepdims=True), rtol=1e-12, atol=1e-15)
    per_row = block - block.find_average(in_each="row")
    np.testing.assert_allclose(per_row.as_numpy(), PLATE - PLATE.mean(axis=(0, 2))[np.newaxis, :, np.newaxis],
                               rtol=1e-12, atol=1e-15)


def test_show_how_it_lines_up_prints_the_picture(capsys):
    plate(named=False).show_how_it_lines_up_with(sdata.number_block(np.ones((8, 12))))
    out = capsys.readouterr().out
    assert "lined up from the right:" in out
    assert "NumPy: np.broadcast_shapes((24, 8, 12), (8, 12))" in out
    assert "result: 24 pages x 8 rows x 12 columns" in out


def test_both_sides_stretching_note_and_hiding_it(capsys):
    column = sdata.number_block(np.arange(100).reshape(100, 1))
    row = sdata.number_list(list(range(100)))
    result = column - row
    np.testing.assert_array_equal(result.as_numpy(), np.arange(100).reshape(100, 1) - np.arange(100))
    assert "both sides were stretched" in capsys.readouterr().out
    sdata.hide_stretching_notes()
    try:
        column - row
        assert "both sides" not in capsys.readouterr().out
    finally:
        sdata.show_stretching_notes()


def test_stretch_to_and_stretch_to_same_shape():
    blank = sdata.number_block(np.arange(12).reshape(1, 12))
    blank.stretch_to((8, 12))
    np.testing.assert_array_equal(blank.as_numpy(), np.broadcast_to(np.arange(12).reshape(1, 12), (8, 12)))
    a, b = sdata.stretch_to_same_shape(np.arange(3).reshape(3, 1), np.arange(4))
    x, y = np.broadcast_arrays(np.arange(3).reshape(3, 1), np.arange(4))
    np.testing.assert_array_equal(a.as_numpy(), x)
    np.testing.assert_array_equal(b.as_numpy(), y)


# ---------------------------------------------------------------------- labels (P25)
def test_keep_where_on_labels_runs_either_way():
    xr = pytest.importorskip("xarray")
    lat = np.arange(89.5, 50, -1.0)  # runs downward, as many files do
    data = xr.DataArray(RNG.normal(size=(3, lat.size)), dims=["time", "latitude"], coords={"latitude": lat})
    sst = sdata.number_block(data)
    sst.keep_where("latitude", is_between=[60, 80])
    expected = data.sel(latitude=slice(80, 60)).values
    np.testing.assert_array_equal(sst.as_numpy(), expected)
    np.testing.assert_array_equal(sst._labels["latitude"], data.sel(latitude=slice(80, 60)).latitude.values)
    again = sdata.number_block(data).remove_where("latitude", is_one_of=[89.5, 88.5])
    np.testing.assert_array_equal(again.as_numpy(), data.drop_sel(latitude=[89.5, 88.5]).values)


def test_keep_where_without_labels_points_to_positions():
    with pytest.raises(sdata.SimplydataError, match="keep_by_position_in"):
        plate().keep_where("hour", is_between=[1, 3])


# ---------------------------------------------------------------------- other names, tables, undo
def test_numpy_names_point_to_block_words():
    with pytest.raises(MissingWordError, match="change_shape_to"):
        plate().reshape
    with pytest.raises(MissingWordError, match="remove_directions_of_size_one"):
        plate().squeeze


def test_long_table_has_one_column_per_direction():
    table = sdata.number_block(np.arange(6).reshape(2, 3), directions_named=["site", "day"]).turn_into_table()
    frame = table.as_pandas()
    assert list(frame.columns) == ["site", "day", "value"]
    np.testing.assert_array_equal(frame["value"].to_numpy(), np.arange(6))
    np.testing.assert_array_equal(frame["day"].to_numpy(), [1, 2, 3, 1, 2, 3])
