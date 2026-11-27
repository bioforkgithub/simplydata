"""NumPy + SciPy phase, batch 2: random picks (P10), random blocks (P39), log-odds and chances (P24) and counting
ways (P23), each compared with the NumPy or SciPy call it names; random words never touch NumPy's global seed."""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy import special

import simplydata as sdata
from simplydata.numbers.blocks import NumberBlock

MARKS = [52.0, 61.5, 70.0, 48.5, 66.0, 59.0, 73.5, 55.0]


def test_make_random_picks_equals_generator_choice(capsys):
    nums = sdata.number_list(MARKS)
    picks = nums.make_random_picks(how_many=40, with_seed=1)
    expected = np.random.default_rng(1).choice(np.array(MARKS), size=40, replace=True)
    np.testing.assert_array_equal(picks.as_numpy(), expected)
    assert "seed 1" in capsys.readouterr().out
    np.testing.assert_array_equal(nums.as_numpy(), MARKS)  # the numbers themselves do not change


def test_make_random_picks_without_putting_back_and_with_chances():
    nums = sdata.number_list([1, 2, 3])
    got = nums.make_random_picks(how_many=1000, with_chances=[0.5, 0.3, 0.2], with_seed=4)
    expected = np.random.default_rng(4).choice(np.array([1, 2, 3]), size=1000, replace=True, p=[0.5, 0.3, 0.2])
    np.testing.assert_array_equal(got.as_numpy(), expected)
    got = sdata.number_list(MARKS).make_random_picks(how_many=8, putting_back=False, with_seed=2)
    np.testing.assert_array_equal(got.as_numpy(),
                                  np.random.default_rng(2).choice(np.array(MARKS), size=8, replace=False))


def test_make_random_picks_is_reproducible_and_leaves_the_global_seed_alone(capsys):
    np.random.seed(123)
    before = np.random.get_state()[1].copy()
    a = sdata.number_list(MARKS).make_random_picks(how_many=5, with_seed=9)
    b = sdata.number_list(MARKS).make_random_picks(how_many=5, with_seed=9)
    np.testing.assert_array_equal(a.as_numpy(), b.as_numpy())
    sdata.number_list(MARKS).make_random_picks(how_many=5)
    assert "no seed: different each run" in capsys.readouterr().out
    np.testing.assert_array_equal(np.random.get_state()[1], before)


def test_make_random_picks_refusals():
    nums = sdata.number_list([1, 2, 3])
    with pytest.raises(sdata.SimplydataError, match="add up to 1"):
        nums.make_random_picks(how_many=3, with_chances=[2, 3, 5])
    with pytest.raises(sdata.SimplydataError, match="one chance for each number: 3"):
        nums.make_random_picks(how_many=3, with_chances=[0.5, 0.5])
    with pytest.raises(sdata.SimplydataError, match="at most 3 picks"):
        nums.make_random_picks(how_many=4, putting_back=False)


def test_make_random_numbers_of_shape_gives_a_block():
    block = sdata.make_random_numbers(of_shape=(24, 8, 12), with_seed=1)
    assert isinstance(block, NumberBlock)
    np.testing.assert_array_equal(block.as_numpy(), np.random.default_rng(1).uniform(0, 1, (24, 8, 12)))
    bell = sdata.make_random_numbers(of_shape=(2, 3), average=5, standard_deviation=2, with_seed=3)
    np.testing.assert_array_equal(bell.as_numpy(), np.random.default_rng(3).normal(5, 2, (2, 3)))
    assert block.find_direction_names() == ["page", "row", "column"]
    with pytest.raises(sdata.SimplydataError, match="one of them"):
        sdata.make_random_numbers(of_shape=(2, 3), how_many=6)


def test_take_log_odds_equals_logit_and_empties_0_and_1(capsys):
    values = np.array([0.1, 0.5, 0.8, 0.999, 0.0, 1.0, 1.2])
    nums = sdata.number_list(values.tolist())
    nums.take_log_odds()
    with np.errstate(all="ignore"):
        expected = np.where((values <= 0) | (values >= 1), np.nan, special.logit(values))
    np.testing.assert_allclose(nums.as_numpy(), expected, rtol=1e-15, equal_nan=True)
    assert "3 numbers are now empty" in capsys.readouterr().out
    nums.turn_into_chances()
    np.testing.assert_allclose(nums.as_numpy()[:4], values[:4], rtol=1e-14)


def test_turn_into_chances_equals_expit_on_grids_and_blocks():
    scores = np.array([[-2.2, 0.0], [1.386, 30.0]])
    grid = sdata.number_grid(scores.tolist())
    grid.turn_into_chances()
    np.testing.assert_allclose(grid.as_numpy(), special.expit(scores), rtol=1e-15)
    block = sdata.number_block(scores[None, :, :])
    block.turn_into_chances()
    np.testing.assert_allclose(block.as_numpy(), special.expit(scores)[None], rtol=1e-15)


@pytest.mark.parametrize("k, n", [(3, 10), (0, 5), (5, 5), (7, 3), (25, 60)])
def test_counting_ways_equals_scipy_and_math(k, n):
    assert sdata.count_ways_to_choose(k, out_of=n) == special.comb(n, k, exact=True) == math.comb(n, k)
    assert sdata.count_ways_to_order(k, out_of=n) == special.perm(n, k, exact=True) == math.perm(n, k)


def test_counting_ways_refuses_other_values():
    with pytest.raises(sdata.SimplydataError, match="whole number"):
        sdata.count_ways_to_choose(2.5, out_of=10)
    with pytest.raises(sdata.SimplydataError, match="out_of="):
        sdata.count_ways_to_order(3, out_of=-1)


def test_numpy_names_point_to_the_new_words():
    from simplydata._errors import MissingWordError

    with pytest.raises(MissingWordError, match="make_random_picks"):
        sdata.number_list([1, 2]).choice
    with pytest.raises(MissingWordError, match="take_log_odds"):
        sdata.number_list([0.5]).logit
    with pytest.raises(MissingWordError, match="count_ways_to_choose"):
        sdata.comb
    with pytest.raises(MissingWordError, match="find_values_at"):
        sdata.number_block([[1.0]]).interp
    with pytest.raises(MissingWordError, match="in_groups_of"):
        sdata.number_block([[1.0]]).coarsen
