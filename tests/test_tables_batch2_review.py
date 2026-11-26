"""Tables phase, batch 2: fixes from the independent review (2026-11-25). Where pandas and Polars disagree, the step
runs through one parent library for both engines, so a pandas table and a Polars table give the very same result;
each test compares the two engines strictly."""

import datetime as dt

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table

pl = pytest.importorskip("polars")
ENGINES = ["pandas", "polars"]


def build(data, engine):
    """The same data as a pandas and as a Polars table (Polars built from Python values, not from pandas)."""
    if engine == "polars":
        return make_table(pl.DataFrame(data, strict=False))
    return make_table(pd.DataFrame(data))


def values(t):
    """A table as {column: [values]}, with every empty cell as None and every number as a Python number."""
    native = t._frame.to_native()
    data = native.to_dict(as_series=False) if isinstance(native, pl.DataFrame) else native.to_dict(orient="list")
    out = {}
    for k, column in data.items():
        out[k] = [None if v is None or v is pd.NA or v is pd.NaT or (isinstance(v, float) and np.isnan(v))
                  else v.to_pydatetime() if isinstance(v, pd.Timestamp)
                  else v.item() if isinstance(v, np.generic) else v for v in column]
    return out


def on_both(data, step, capsys=None):
    """(the pandas result, the Polars result, what each printed), or the error each gave."""
    results, printed = [], []
    for engine in ENGINES:
        t = build(data, engine)
        try:
            results.append(values(step(t)))
        except SimplydataError as error:
            results.append(f"refused: {error}")
        if capsys is not None:
            printed.append(capsys.readouterr().out)
    return results, printed


# ---------------------------------------------------------------- 1 into_equal_groups=: pandas qcut for both
def test_equal_groups_with_tied_cut_points_are_refused_on_both(capsys):
    (a, b), _ = on_both({"x": [1, 1, 1, 1, 2, 3, 4, 5]},
                        lambda t: t.add_group_column("q", from_column="x", into_equal_groups=4))
    assert a == b and a.startswith("refused") and "into_equal_groups=3" in a


def test_equal_groups_and_cut_points_are_the_same_on_both(capsys):
    rng = np.random.default_rng(0)
    for _ in range(60):
        x = [float(v) for v in rng.integers(0, int(rng.integers(3, 30)), int(rng.integers(8, 40)))] + [None]
        k = int(rng.integers(2, 6))
        (a, b), (pa, pb) = on_both({"x": x}, lambda t: t.add_group_column("q", from_column="x", into_equal_groups=k),
                                   capsys)
        assert a == b, (k, x)
        assert pa == pb
        if not isinstance(a, str):
            series = pd.Series(x, dtype="float64")
            expected = pd.qcut(series, k, labels=False) + 1
            assert a["q"] == [None if pd.isna(v) else int(v) for v in expected]


# ---------------------------------------------------------------- 2 skip_rows= counts the lines of the file
def test_skip_rows_with_note_lines_counts_raw_lines_on_both(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "log.csv").write_text("# logger v1\na,b,c\n1,2,3\n#note\n4,5,6\n", encoding="utf-8")
    slow = sdata.table("log.csv", skip_lines_starting_with="#", skip_rows=1, separator=",")
    fast = sdata.table("log.csv", skip_lines_starting_with="#", skip_rows=1, separator=",", fast=True)
    assert values(slow) == values(fast) == {"a": [1, 4], "b": [2, 5], "c": [3, 6]}
    assert values(slow) == pd.read_csv("log.csv", skiprows=1, comment="#").to_dict(orient="list")


# ---------------------------------------------------------------- 3 round_dates_in: Polars for both, at summer time
OSLO_CHANGES = ["2026-03-29 01:40", "2026-03-28 23:30", "2026-10-25 01:50", "2026-10-25 02:40", "2026-10-25 03:20"]


@pytest.mark.parametrize("how", [dict(to_the="hour"), dict(up_to="hour"), dict(down_to="hour"), dict(to_the="day"),
                                 dict(up_to="day"), dict(down_to="week"), dict(up_to="month"),
                                 dict(to_the="15 minutes")])
def test_round_dates_at_both_summer_time_changes_are_the_same_on_both(how, capsys):
    local = pd.Series(pd.to_datetime(OSLO_CHANGES)).dt.tz_localize("Europe/Oslo", ambiguous=[True] * 5)
    results = []
    for native in (pd.DataFrame({"t": local}), pl.DataFrame({"t": pl.from_pandas(local)})):
        t = make_table(native)
        t.round_dates_in("t", **how)  # pandas' own dt.round/dt.ceil stop here ("Cannot infer dst time")
        results.append([v.isoformat() for v in values(t)["t"]])
    assert results[0] == results[1]
    if how == dict(to_the="hour"):
        expected = pl.from_pandas(local).dt.round("1h").to_list()
        assert results[1] == [v.isoformat() for v in expected]


def test_round_dates_half_way_goes_up_on_both(capsys):
    (a, b), _ = on_both({"t": [dt.datetime(2026, 1, 1, 10, 30), dt.datetime(2026, 1, 1, 11, 30), None]},
                        lambda t: t.round_dates_in("t", to_the="hour"))
    assert a == b and a["t"][:2] == [dt.datetime(2026, 1, 1, 11), dt.datetime(2026, 1, 1, 12)]


# ---------------------------------------------------------------- 4 with_totals=: "(total)", empty cells kept
def test_totals_are_called_total_in_brackets_and_a_value_total_stays(capsys):
    (a, b), _ = on_both({"shop": ["total", "N"], "fruit": ["a", "b"]},
                        lambda t: t.count_rows(for_each_group_in="shop", across="fruit", with_totals=True))
    assert a == b == {"shop": ["N", "total", "(total)"], "a": [0, 1, 1], "b": [1, 0, 1], "(total)": [1, 1, 2]}
    (a, b), _ = on_both({"shop": ["(total)", "N"], "fruit": ["a", "b"]},
                        lambda t: t.count_rows(for_each_group_in="shop", across="fruit", with_totals=True))
    assert a == b and a.startswith("refused") and 'already holds the value "(total)"' in a


def test_totals_keep_rows_with_empty_cells_on_both(capsys):
    data = {"shop": ["N", "N", "N", "S", None, "S"], "fruit": ["a", "a", "b", "a", "b", None],
            "x": [1.0, 3.0, 10.0, None, 4.0, 6.0]}
    for step in (lambda t: t.count_rows(for_each_group_in="shop", across="fruit", with_totals=True),
                 lambda t: t.find_total_of("x", for_each_group_in="shop", across="fruit", with_totals=True),
                 lambda t: t.find_average_of("x", for_each_group_in="shop", across="fruit", with_totals=True)):
        (a, b), _ = on_both(data, step)
        assert a == b
    counts = on_both(data, lambda t: t.count_rows(for_each_group_in="shop", across="fruit", with_totals=True))[0][0]
    assert counts["(total)"][-1] == 6  # every row counts, the ones with an empty shop or fruit too
    assert pd.crosstab(pd.Series(data["shop"]), pd.Series(data["fruit"]), margins=True).iloc[-1, -1] == 4


# ---------------------------------------------------------------- 5 add_missing_combinations_of keeps whole numbers
def test_missing_combinations_keep_whole_numbers_on_both(capsys):
    big = 2 ** 60 + 1
    (a, b), _ = on_both({"s": ["A", "A", "B", None], "depth": [1, 2, 1, 1], "n": [10, big, 30, 40]},
                        lambda t: t.add_missing_combinations_of("s", "depth"))
    assert a == b == {"s": ["A", "A", "B", "B", None], "depth": [1, 2, 1, 2, 1], "n": [10, big, 30, None, 40]}


# ---------------------------------------------------------------- 6 capitals_matter=False: one rule (casefold)
WORDS = {"s": ["STRASSE", "Straße", "İstanbul", "ISTANBUL", "ΟΔΟΣ", "οδος", "Øl", "øl", None]}


@pytest.mark.parametrize("condition, kept", [
    (dict(is_equal_to="straße"), ["STRASSE", "Straße"]), (dict(is_equal_to="istanbul"), ["ISTANBUL"]),
    (dict(is_equal_to="ΟΔΟΣ"), ["ΟΔΟΣ", "οδος"]), (dict(is_one_of=["øl"]), ["Øl", "øl"]),
    (dict(contains="SS"), ["STRASSE", "Straße"]), (dict(starts_with="i̇"), ["İstanbul"])])
def test_capitals_do_not_matter_by_one_rule_on_both(condition, kept, capsys):
    (a, b), _ = on_both(WORDS, lambda t: t.keep_rows_where("s", capitals_matter=False, **condition))
    assert a == b
    assert a["s"] == kept
    folded = pd.Series(WORDS["s"][:-1]).str.casefold()
    if "is_equal_to" in condition:
        assert kept == [w for w, f in zip(WORDS["s"], folded) if f == condition["is_equal_to"].casefold()]


def test_replace_text_any_capitals_is_the_same_on_both(capsys):
    (a, b), _ = on_both({"s": ["ΟΔΟΣ x", "οδος y", "A.B", "axb", None]},
                        lambda t: t.replace_text_in("s", "οδος", with_value="road", capitals_matter=False))
    assert a == b and a["s"][:2] == ["road x", "road y"]


# ---------------------------------------------------------------- (a) matches_pattern=: Polars rules on both
def test_patterns_follow_one_set_of_rules_on_both(capsys):
    (a, b), _ = on_both({"s": ["ab", "AB"]}, lambda t: t.keep_rows_where("s", matches_pattern="(?=a)b|ab"))
    assert a == b and a.startswith("refused") and "look-ahead" in a
    (a, b), _ = on_both({"s": ["ab\n", "AB", "xb"]}, lambda t: t.keep_rows_where("s", matches_pattern="b$"))
    assert a == b == {"s": ["xb"]}  # "$" is the very end of the text: "ab\n" does not end with b


# ---------------------------------------------------------------- (b) fill_empty_cells_from
@pytest.mark.parametrize("here, other, expected", [
    ({"k": [1, 2, 3, None], "v": [None, "  ", "x", None]}, {"k": [1, 2, None], "v": ["a", None, "z"]},
     ["a", "  ", "x", None]),  # "  " with nothing to take stays as it is
    ({"k": [1, 2], "v": [None, None]}, {"k": [1, None, None], "v": ["a", "b", "c"]}, ["a", None]),  # empty keys
    ({"k": [1, 2], "v": [None, None]}, {"k": [1, 2], "v": ["  ", "b"]}, [None, "b"]),  # "  " fills nothing
    ({"k": [1, 2], "v": ["x", None]}, {"k": [1, 2], "v": [None, None]}, ["x", None]),  # an all-empty column
])
def test_fill_from_another_table_edge_cases_on_both(here, other, expected, capsys):
    (a, b), _ = on_both(here, lambda t: t.fill_empty_cells_from(other, using="k"))
    assert not isinstance(a, str) and not isinstance(b, str), (a, b)
    assert a["v"] == b["v"] == expected


# ---------------------------------------------------------------- (c) written_like= with month names
def test_written_like_reads_full_and_short_month_names_on_both(capsys):
    for example in ("31 May 2026", "31 Dec 2026", "31 December 2026"):
        (a, b), _ = on_both({"d": ["5 May 2026", "15 Sep 2026", "15 September 2026", None]},
                            lambda t: t.turn_into_dates("d", written_like=example))
        assert a == b
        assert a["d"][:3] == [dt.datetime(2026, 5, 5), dt.datetime(2026, 9, 15), dt.datetime(2026, 9, 15)]


def test_fill_from_a_polars_table_with_a_column_of_only_empty_cells(capsys):
    here = make_table(pl.DataFrame({"k": [1, 2], "v": ["x", None]}))
    here.fill_empty_cells_from(pl.DataFrame({"k": [1, 2], "v": [None, None]}), using="k")  # v has no kind (Null)
    empty_here = make_table(pl.DataFrame({"k": [1, 2], "v": [None, None]}))
    empty_here.fill_empty_cells_from(pl.DataFrame({"k": [1, 2], "v": ["a", "b"]}), using="k")
    pandas_side = make_table(pd.DataFrame({"k": [1, 2], "v": [None, None]}))
    pandas_side.fill_empty_cells_from(pd.DataFrame({"k": [1, 2], "v": ["a", "b"]}), using="k")
    assert values(here)["v"] == ["x", None]
    assert values(empty_here)["v"] == values(pandas_side)["v"] == ["a", "b"]
