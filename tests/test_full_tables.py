"""Families for 100 %, batches 1-2 (approved by Manish 2026-11-28): the pandas and Polars gaps (plan section 2.1) and
the seaborn.objects marks and moves (section 2.5). Each word and option is checked against pandas, Polars or seaborn
itself, on both table engines where it applies."""

from __future__ import annotations

import numpy as np
import pandas as pd
import polars as pl
import pytest

import simplydata as sdata

ENGINES = [False, True]  # pandas, then Polars (fast=True)


def _table(name, fast):
    return sdata.table(sdata.get_example(name), fast=fast)


def _frame(name):
    return sdata.get_example(name).as_pandas()


# ---------------------------------------------------------------- new table words
@pytest.mark.parametrize("fast", ENGINES)
def test_get_different_values_in_matches_pandas_unique_and_polars_unique(fast, capsys):
    df = pd.DataFrame({"site": ["b", "a", None, "b", "c", "a"], "n": [3.0, 1.0, np.nan, 3.0, 2.0, 1.0]})
    table = sdata.table(df, fast=fast)
    values = table.get_different_values_in("site")
    assert values == list(df["site"].dropna().unique())
    assert values == pl.from_pandas(df)["site"].drop_nulls().unique(maintain_order=True).to_list()
    out = capsys.readouterr().out
    assert 'Note: 1 empty cell in "site" was left out.' in out
    assert '"site" has 3 different values, in the order they first turn up: "b", "a", "c".' in out
    numbers = table.get_different_values_in("n")
    assert list(numbers.as_numpy()) == list(df["n"].dropna().unique())  # number_list, as get_column gives
    assert table.count_rows() == 6  # the table does not change


@pytest.mark.parametrize("fast", ENGINES)
def test_check_if_all_and_any_match_pandas_and_polars(fast, capsys):
    df = pd.DataFrame({"depth": [3.0, 5.0, np.nan, 8.0], "dose": [10, 120, 40, 90], "ok": pd.array([True, True, None, True], dtype="boolean"),
                       "site": ["N", "N", "S", "S"]})
    table = sdata.table(df, fast=fast)
    assert table.check_if_all_values_in("depth", is_above=0) is bool((df["depth"].dropna() > 0).all()) is True
    assert table.check_if_all_values_in("depth", is_above=4) is False
    out = capsys.readouterr().out
    assert "Note: 1 empty cell" in out and 'No: 1 of the 3 values in "depth" do not meet "is above 4" (the first in ' \
                                          "row 1)." in out
    assert table.check_if_any_value_in("dose", is_above=100) is bool((df["dose"] > 100).any()) is True
    assert table.check_if_any_value_in("dose", is_above=200) is False
    assert table.check_if_all_values_in("ok") is True  # a True/False column needs no condition; empty left out
    polars = pl.from_pandas(df)
    assert table.check_if_all_values_in(["depth", "dose"], is_above=2) == bool(
        polars.select(pl.all_horizontal(pl.col("depth", "dose").fill_null(99) > 2).all()).item())
    assert table.check_if_any_value_in(["depth", "dose"], is_above=100) == bool(
        polars.select(pl.any_horizontal(pl.col("depth", "dose") > 100).any()).item())
    grouped = table.check_if_all_values_in("dose", is_below=100, for_each_group_in="site")
    expected = df.groupby("site")["dose"].apply(lambda s: bool((s < 100).all()))
    assert grouped.get_column("every value") == list(expected.values)
    assert table.check_if_any_value_in("dose", is_above=100, for_each_group_in="site").get_column("any value") == \
        list(df.groupby("site")["dose"].apply(lambda s: bool((s > 100).any())).values)


def test_check_if_all_values_in_needs_a_condition_unless_true_false():
    table = sdata.table(sdata.get_example("marks"))
    with pytest.raises(sdata.SimplydataError, match="needs a condition"):
        table.check_if_all_values_in("marks")
    with pytest.raises(sdata.SimplydataError, match="one condition at a time"):
        table.check_if_all_values_in("marks", is_above=0, is_below=100)


@pytest.mark.parametrize("fast", ENGINES)
def test_check_if_sorted_by_matches_is_monotonic_and_is_sorted(fast, capsys):
    df = pd.DataFrame({"day": [1, 2, 2, np.nan, 5], "level": [3.0, 2.0, 2.5, 1.0, 0.5], "site": ["a", "b", "b", "c", "c"]})
    table = sdata.table(df, fast=fast)
    assert table.check_if_sorted_by("day") is bool(df["day"].dropna().is_monotonic_increasing) is True
    assert table.check_if_sorted_by("level") is pl.from_pandas(df)["level"].is_sorted() is False
    out = capsys.readouterr().out
    assert 'No: the rows are not in order of "level", smallest first: row 2 (2) comes after 3.' in out
    assert table.check_if_sorted_by("level", biggest_first=True) is bool(df["level"].is_monotonic_decreasing)
    assert table.check_if_sorted_by("site") is True


@pytest.mark.parametrize("fast", ENGINES)
def test_add_run_number_column_matches_polars_rle_id(fast):
    df = pd.DataFrame({"t": [5, 1, 2, 3, 4, 6], "g": ["x", "x", "x", "y", "y", "y"],
                       "wet": ["no", "no", "yes", None, None, "yes"]})
    table = sdata.table(df, fast=fast).add_run_number_column("run", from_column="wet")
    expected = (pl.from_pandas(df).select(pl.col("wet").rle_id() + 1)["wet"]).to_list()
    assert table.get_column("run").as_numpy().tolist() == expected == [1, 1, 2, 3, 3, 4]
    ordered = sdata.table(df, fast=fast).add_run_number_column("run", from_column="wet", for_each_group_in="g",
                                                               sorted_by="t")
    want = pl.from_pandas(df).select((pl.col("wet").rle_id() + 1).over("g", order_by="t"))["wet"].to_list()
    assert ordered.get_column("run").as_numpy().tolist() == want


@pytest.mark.parametrize("fast", ENGINES)
def test_turn_into_title_case_matches_pandas_title_and_polars_to_titlecase(fast, capsys):
    df = pd.DataFrame({"name": ["o'neil mcDONALD", "asha ali", None, "hello-world 2nd"]})
    table = sdata.table(df, fast=fast).turn_into_title_case("name")
    assert table.get_column("name") == [None if pd.isna(v) else v for v in df["name"].str.title()]
    assert table.get_column("name") == pl.from_pandas(df)["name"].str.to_titlecase().to_list()
    assert "Each word in \"name\" now starts with a capital letter: \"o'neil mcDONALD\" became \"O'Neil Mcdonald\"." \
        in capsys.readouterr().out
    table.undo()
    assert table.get_column("name")[0] == "o'neil mcDONALD"
