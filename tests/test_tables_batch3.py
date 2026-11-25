"""Tables phase, batch 3 (ranks 31-44, approved by Manish 2026-11-25): every new word and option on a pandas and a
Polars table, checked against plain pandas and plain Polars. SQL, databases and the file types are in
test_tables_batch3_sql.py."""

import datetime
from importlib.resources import files

import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.data import DATE_COLUMNS, TEXT_COLUMNS
from simplydata.table import table as make_table

pl = pytest.importorskip("polars")
ENGINES = ["pandas", "polars"]


def raw(name, dates=True):
    """A practice table read straight from its file by pandas (the reference side)."""
    with (files("simplydata.data") / f"{name}.csv").open("r", encoding="utf-8") as fh:
        text = {c: str for c in TEXT_COLUMNS.get(name, [])}
        return pd.read_csv(fh, parse_dates=DATE_COLUMNS.get(name, False) if dates else False, dtype=text or None)


def build(data, engine):
    data = pd.DataFrame(data)
    return make_table(data, fast=True) if engine == "polars" else make_table(data)


def example(name, engine):
    return build(raw(name), engine)


def plain(t):
    native = t._done()
    if not isinstance(native, pd.DataFrame):
        native = native.to_pandas()
    return native.reset_index(drop=True)


def same(got, expected):
    """Same columns, same values (empty cells in the same places), whatever the integer or float kinds."""
    got, expected = got.reset_index(drop=True), expected.reset_index(drop=True)
    assert list(got.columns) == list(expected.columns)
    pd.testing.assert_frame_equal(got.astype(object).where(got.notna(), None),
                                  expected.astype(object).where(expected.notna(), None), check_dtype=False)


@pytest.fixture(params=ENGINES)
def engine(request):
    return request.param


# ---------------------------------------------------------------- P25 add_zeros_in_front_of
def test_add_zeros_in_front_of_matches_zfill(engine, capsys):
    codes = ["7", "42", "1234", None, "-7", "007"]
    t = build({"code": codes}, engine)
    t.add_zeros_in_front_of("code", to_length=3)
    expected_pandas = pd.Series(codes, dtype=object).str.zfill(3)
    expected_polars = pl.Series(codes).str.zfill(3).to_list()
    got = list(plain(t)["code"].astype(object).where(plain(t)["code"].notna(), None))
    assert got == [None if pd.isna(v) else v for v in expected_pandas] == expected_polars
    assert got == ["007", "042", "1234", None, "-07", "007"]
    out = capsys.readouterr().out
    assert "3 values changed" in out and "1 value has more than 3 characters and was not cut" in out
    t.undo()
    assert plain(t)["code"].iloc[0] == "7"


def test_add_zeros_in_front_of_wants_text_and_a_length(engine):
    t = example("fjord_samples", engine)
    with pytest.raises(SimplydataError, match=r'turn_into_text\("sample_id"\)'):
        t.add_zeros_in_front_of("sample_id", to_length=3)
    t.turn_into_text("sample_id")
    for bad in (0, 2.5, True, None, "3"):
        with pytest.raises(SimplydataError, match="to_length="):
            t.add_zeros_in_front_of("sample_id", to_length=bad)
    t.add_zeros_in_front_of("sample_id", width=3)  # pandas' name runs as to_length= with a note
    assert plain(t)["sample_id"].iloc[0] == "001"


# ---------------------------------------------------------------- P42 find_summary_of(show=["first", "last"])
def test_first_and_last_skip_empty_cells_like_pandas(engine):
    data = {"g": ["a", "a", "a", "b", "b", "c"], "x": [None, 2.0, 3.0, 4.0, None, None]}
    t = build(data, engine)
    got = plain(t.find_summary_of("x", show=["first", "last", "biggest"], for_each_group_in="g"))
    expected = pd.DataFrame(data).groupby("g")["x"].agg(["first", "last", "max"]).reset_index()
    assert list(got["first"].fillna(-1)) == list(expected["first"].fillna(-1)) == [2.0, 4.0, -1]
    assert list(got["last"].fillna(-1)) == list(expected["last"].fillna(-1)) == [3.0, 4.0, -1]
    polars = (pl.DataFrame(data).group_by("g", maintain_order=True)
              .agg(pl.col("x").drop_nulls().first().alias("first"), pl.col("x").drop_nulls().last().alias("last")))
    assert polars["first"].to_list() == [2.0, 4.0, None]
    whole = plain(t.find_summary_of("x", show=["first", "last"]))
    assert whole["first"].iloc[0] == 2.0 and whole["last"].iloc[0] == 4.0


def test_open_high_low_close_by_month(engine):
    river = example("river", engine)
    got = plain(river.find_summary_of("level", show=["first", "biggest", "smallest", "last"],
                                      for_each_group_in=["station", "date"], every="month"))
    df = raw("river")
    expected = (df.groupby(["station", df["date"].dt.to_period("M")])["level"].agg(["first", "max", "min", "last"])
                .reset_index())
    assert len(got) == len(expected)
    for ours, theirs in (("first", "first"), ("biggest", "max"), ("smallest", "min"), ("last", "last")):
        assert list(got[ours].round(9)) == list(expected[theirs].round(9))


def test_first_and_last_keep_the_columns_own_kind(engine):
    """Review fix: a whole number above 2**53 stays exact (no conversion to decimals), on both engines."""
    big = 2 ** 60 + 1
    data = pd.DataFrame({"g": ["a", "a", "b", "c"], "x": pd.array([big, 3, big + 2, None], dtype="Int64")})
    t = make_table(data, fast=True) if engine == "polars" else make_table(data)
    rows = t.find_summary_of("x", for_each_group_in="g", show=["first", "last"]).as_list()
    assert [(r["first"], r["last"]) for r in rows] == [(big, 3), (big + 2, big + 2), (None, None)]
    assert all(isinstance(r["first"], int) for r in rows[:2])
    whole = build({"x": [big, 5]}, engine).find_summary_of("x", show=["first", "last"]).as_list()[0]
    assert (whole["first"], whole["last"]) == (big, 5)
    decimals = build({"x": [0.5, None, 2.5]}, engine).find_summary_of("x", show=["first", "last"]).as_list()[0]
    assert (decimals["first"], decimals["last"]) == (0.5, 2.5)


# ---------------------------------------------------------------- P43 sort_by(biggest_first=[...])
def test_sort_by_with_a_direction_for_each_column(engine, capsys):
    t = example("marks", engine)
    t.sort_by("class", "marks", biggest_first=[False, True])
    expected = raw("marks").sort_values(["class", "marks"], ascending=[True, False], kind="stable")
    same(plain(t), expected)
    polars = pl.from_pandas(raw("marks")).sort(["class", "marks"], descending=[False, True], maintain_order=True)
    same(plain(t), polars.to_pandas())
    t.show_steps()
    assert "sort by class (smallest first), marks (biggest first)" in capsys.readouterr().out


def test_sort_by_list_is_checked_and_ascending_points(engine, capsys):
    t = example("marks", engine)
    with pytest.raises(SimplydataError, match="one True or False for each column: 2 here"):
        t.sort_by("class", "marks", biggest_first=[True])
    with pytest.raises(SimplydataError, match="one True or False"):
        t.sort_by("class", "marks", biggest_first=[1, 0])
    with pytest.raises(SimplydataError, match="ascending=False is biggest_first=True"):
        t.sort_by("marks", ascending=False)
    t.sort_by("marks", descending=True)  # Polars' name, same meaning: runs with a note
    assert "descending= is biggest_first=" in capsys.readouterr().out
    assert plain(t)["marks"].iloc[0] == raw("marks")["marks"].max()


# ---------------------------------------------------------------- P44 gather_into_rows(starts_with= ...)
def test_gather_into_rows_by_name(engine):
    t = example("clinic", engine)
    t.keep_columns("patient", "ward", "pain_week_0", "pain_week_4", "pain_week_8")
    t.gather_into_rows(starts_with="pain_week_", names_to="week", values_to="pain")
    df = raw("clinic")[["patient", "ward", "pain_week_0", "pain_week_4", "pain_week_8"]]
    weeks = [c for c in df.columns if c.startswith("pain_week_")]
    expected = df.melt(id_vars=["patient", "ward"], value_vars=weeks, var_name="week", value_name="pain")
    same(plain(t), expected)
    import polars.selectors as cs

    polars = pl.from_pandas(df).unpivot(on=cs.starts_with("pain_week_"), index=["patient", "ward"],
                                        variable_name="week", value_name="pain")
    same(plain(t), polars.to_pandas())
    t2 = example("clinic", engine)
    t2.keep_columns("patient", "pain_week_0", "pain_week_4")
    t2.gather_into_rows(ends_with="_4")
    assert set(plain(t2)["column"]) == {"pain_week_4"}
    t2.undo()
    t2.gather_into_rows(matches_pattern=r"week_\d$")
    assert set(plain(t2)["column"]) == {"pain_week_0", "pain_week_4"}


def test_gather_into_rows_one_way_at_a_time(engine):
    t = example("clinic", engine)
    with pytest.raises(SimplydataError, match="one way at a time"):
        t.gather_into_rows(["pain_week_0"], starts_with="pain_week_")
    with pytest.raises(SimplydataError, match="one way at a time"):
        t.gather_into_rows(starts_with="pain", ends_with="0")
    with pytest.raises(SimplydataError, match="No column name starts with"):
        t.gather_into_rows(starts_with="nothing_")


# ---------------------------------------------------------------- P32 move_columns
def test_move_columns(engine, capsys):
    t = example("marks", engine)
    cols = list(raw("marks").columns)
    t.move_columns("marks", "hours", to="start")
    assert list(plain(t).columns) == ["marks", "hours"] + [c for c in cols if c not in ("marks", "hours")]
    same(plain(t), raw("marks")[["marks", "hours"] + [c for c in cols if c not in ("marks", "hours")]])
    t.move_columns("marks", to="end")
    assert list(plain(t).columns)[-1] == "marks"
    t.move_columns("height", after="name")
    order = list(plain(t).columns)
    assert order[order.index("name") + 1] == "height"
    t.move_columns("subject")  # without to=: the start
    assert list(plain(t).columns)[0] == "subject"
    assert "Moved \"subject\" to the start" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="to= or after=, not both"):
        t.move_columns("marks", to="start", after="name")
    with pytest.raises(SimplydataError, match="being moved"):
        t.move_columns("marks", after="marks")
    with pytest.raises(SimplydataError, match='"middle"'):
        t.move_columns("marks", to="middle")
    with pytest.raises(SimplydataError):
        t.move_columns("nope")


# ---------------------------------------------------------------- P34 show_rows_with_empty_cells_in
def test_show_rows_with_empty_cells_in(engine, capsys):
    t = example("shop", engine)
    before = plain(t)
    assert t.show_rows_with_empty_cells_in() is None
    out = capsys.readouterr().out
    df = raw("shop")
    holes = df[df.isna().any(axis=1)]
    polars = pl.from_pandas(df).filter(pl.any_horizontal(pl.all().is_null()))
    assert len(holes) == polars.height
    assert f"{len(holes)} rows of {len(df)} have an empty cell:" in out
    first = int(holes.index[0]) + 1
    assert f"\n{first} " in out or f"\n{first}  " in out
    t.show_rows_with_empty_cells_in(columns=["sales"])
    out = capsys.readouterr().out
    assert f"{int(df['sales'].isna().sum())} rows of {len(df)} have an empty cell in sales:" in out
    same(plain(t), before)  # the table does not change
    full = example("marks", engine)
    full.show_rows_with_empty_cells_in()
    assert "No row has an empty cell" in capsys.readouterr().out


def test_spaces_only_count_as_empty(engine, capsys):
    t = build({"a": ["x", "   ", "y"], "b": [1, 2, 3]}, engine)
    t.show_rows_with_empty_cells_in()
    assert "1 row of 3 has an empty cell:" in capsys.readouterr().out


# ---------------------------------------------------------------- P35 show_differences_from, check_if_same_as
def test_check_if_same_as_and_show_differences_from(engine, capsys):
    t = example("marks", engine)
    original = raw("marks")
    assert t.check_if_same_as(original) is True
    assert t.check_if_same_as(original) == bool(original.equals(raw("marks")))
    t.replace_values_in("marks", is_above=90, with_value=90)
    capsys.readouterr()
    assert t.check_if_same_as(original) is False
    out = capsys.readouterr().out
    changed = original.copy()
    changed.loc[changed["marks"] > 90, "marks"] = 90
    cells = changed.compare(original, result_names=("this", "other"))
    first = int(cells.index[0]) + 1
    assert f"the first difference is in row {first}, column \"marks\"" in out
    t.show_differences_from(original)
    out = capsys.readouterr().out
    assert f"{len(cells)} cells differ, in {len(cells)} rows" in out
    assert t.show_differences_from(changed) is None
    assert "No cell differs" in capsys.readouterr().out


def test_two_empty_cells_are_the_same_and_shapes_are_explained(engine, capsys):
    a = build({"x": [1.0, None], "y": ["a", None]}, engine)
    assert a.check_if_same_as({"x": [1.0, None], "y": ["a", None]}) is True
    assert a.check_if_same_as({"x": [1.0, 2.0], "y": ["a", None]}) is False
    assert "row 2, column \"x\": None here, 2.0 in the other table" in capsys.readouterr().out
    assert a.check_if_same_as({"y": ["a", None], "x": [1.0, None]}) is False
    assert "another order" in capsys.readouterr().out
    a.show_differences_from({"x": [1.0, None, 3.0], "y": ["a", None, "c"]})
    assert "this table has 2 rows and the other 3 rows" in capsys.readouterr().out
    a.show_differences_from({"x": [1.0, None], "z": ["a", None]})
    out = capsys.readouterr().out
    assert 'only this table has "y"' in out and 'only the other table has "z"' in out


def test_check_if_same_as_names_a_change_of_kind(engine, capsys):
    a = build({"x": [1, 2]}, engine)
    assert a.check_if_same_as({"x": [1.0, 2.0]}) is False
    assert "the values are equal, but \"x\" holds" in capsys.readouterr().out


# ---------------------------------------------------------------- P36 join_with(match=, within=), every combination
def _rain():
    rain = sdata.table({"date": ["2024-01-01", "2024-01-08", "2024-01-15"], "rain_mm": [12.0, 3.5, 20.1]})
    rain.turn_into_dates("date")
    return rain


@pytest.mark.parametrize("match, direction", [("nearest before", "backward"), ("nearest after", "forward"),
                                              ("nearest", "nearest")])
def test_join_nearest_matches_merge_asof_and_join_asof(engine, match, direction, capsys):
    t = example("river", engine)
    t.keep_columns("date", "station", "nitrate")
    t.join_with(_rain(), using="date", match=match, within="3 days", keep="all rows from this table")
    got = plain(t)
    df = raw("river")[["date", "station", "nitrate"]]
    rain = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-01-08", "2024-01-15"]),
                         "rain_mm": [12.0, 3.5, 20.1]})
    left = df.reset_index().sort_values("date", kind="stable")
    expected = (pd.merge_asof(left, rain, on="date", direction=direction, tolerance=pd.Timedelta(days=3))
                .sort_values("index").drop(columns="index").reset_index(drop=True))
    assert list(got.columns) == ["date", "station", "nitrate", "rain_mm", "date_other"]
    same(got.drop(columns="date_other"), expected)
    polars = (pl.from_pandas(df).with_row_index().sort("date")
              .join_asof(pl.from_pandas(rain).sort("date"), on="date", strategy=direction,
                         tolerance=datetime.timedelta(days=3)).sort("index").drop("index"))
    assert [None if pd.isna(v) else v for v in got["rain_mm"]] == polars["rain_mm"].to_list()
    found = int(expected["rain_mm"].notna().sum())
    assert f"{found} of {len(df)} rows in this table found a row of the other table" in capsys.readouterr().out
    t.undo()
    t.join_with(_rain(), using="date", match=match, within="3 days")  # keep="matching rows": the rest left out
    assert len(t) == found


def test_join_nearest_with_exact_keys_and_numbers(engine):
    left = build({"station": ["A", "A", "B"], "depth": [1.0, 9.0, 4.0]}, engine)
    right = {"station": ["A", "A", "B"], "depth": [0.0, 10.0, 5.0], "temp": [8.1, 6.0, 7.5]}
    left.join_with(right, using=["station", "depth"], match="nearest", within=2)
    expected = pd.merge_asof(pd.DataFrame({"station": ["A", "A", "B"], "depth": [1.0, 9.0, 4.0]}).sort_values("depth"),
                             pd.DataFrame(right).sort_values("depth"), on="depth", by="station", direction="nearest",
                             tolerance=2)
    got = plain(left)
    assert sorted(got["temp"]) == sorted(expected["temp"]) == [6.0, 7.5, 8.1]


def test_join_nearest_is_checked(engine):
    t = example("river", engine)
    with pytest.raises(SimplydataError, match='within= is the longest time'):
        t.join_with(_rain(), using="date", match="nearest before", within="soon")
    with pytest.raises(SimplydataError, match="within= goes with match="):
        t.join_with(_rain(), using="date", within="2 days")
    with pytest.raises(SimplydataError, match='"nearest before"'):
        t.join_with(_rain(), using="date", match="closest")
    with pytest.raises(SimplydataError, match="keeps the rows of this table"):
        t.join_with(_rain(), using="date", match="nearest", keep="all rows from both")
    with pytest.raises(SimplydataError, match="must hold dates or numbers"):
        t.join_with({"station": ["Station A"], "x": [1]}, using="station", match="nearest")
    with pytest.raises(SimplydataError, match="In simplydata this is match="):
        t.join_with(_rain(), using="date", direction="backward")
    with pytest.raises(SimplydataError, match="within="):
        t.join_with(_rain(), using="date", match="nearest", tolerance="2d")
    holes = build({"date": pd.to_datetime(["2024-01-02", None]), "x": [1, 2]}, engine)
    with pytest.raises(SimplydataError, match="empty \"date\""):
        holes.join_with(_rain(), using="date", match="nearest")


def _nearest_both(left, right, **options):
    """The join on a pandas and on a Polars table, as plain rows."""
    out = []
    for engine in ENGINES:
        t = build(left, engine)
        t.join_with(build(right, engine), **options)
        out.append([{k: (None if v is None or v != v else v) for k, v in row.items()} for row in t.as_list()])
    return out


def _plain_join_asof(left, right, on, strategy, by=None, **extra):
    """Plain Polars join_asof after a stable sort, the rows back in this table's order."""
    joined = (pl.from_pandas(pd.DataFrame(left)).with_row_index("i").sort(on, maintain_order=True)
              .join_asof(pl.from_pandas(pd.DataFrame(right)).sort(on, maintain_order=True), on=on, by=by,
                         strategy=strategy, **extra).sort("i").drop("i"))
    return joined.to_dicts()


@pytest.mark.parametrize("match, strategy", [("nearest before", "backward"), ("nearest after", "forward"),
                                             ("nearest", "nearest")])
def test_nearest_joins_agree_on_repeats_ties_and_empty_keys(match, strategy):
    """Review fix: one rule on both engines (Polars join_asof after a stable sort), never pandas merge_asof's."""
    left = {"t": [1, 5, 10, 5], "x": ["p", "q", "r", "s"]}
    right = {"t": [3, 7, 7, 3], "v": ["a", "b", "c", "d"]}
    on_pandas, on_polars = _nearest_both(left, right, using="t", match=match, keep="all rows from this table")
    assert on_pandas == on_polars
    expected = _plain_join_asof(left, right, "t", strategy)
    assert [r["v"] for r in on_pandas] == [r["v"] for r in expected]
    # the tie (5 is as near to 3 as to 7) and the repeated keys are broken as Polars does, on both engines
    assert on_pandas[1]["v"] == {"backward": "d", "forward": "b", "nearest": expected[1]["v"]}[strategy]
    # empty exact-match keys never pair
    left2 = {"s": ["A", None, "B"], "t": [5, 5, 1]}
    right2 = {"s": ["A", None, "B"], "t": [4, 4, 0], "v": [1, 2, 3]}
    on_pandas, on_polars = _nearest_both(left2, right2, using=["s", "t"], match=match,
                                         keep="all rows from this table")
    assert on_pandas == on_polars
    assert on_pandas[1]["v"] is None
    if strategy != "forward":
        assert on_pandas[0]["v"] == 1 and on_pandas[2]["v"] == 3


def test_nearest_joins_take_whole_numbers_and_decimals():
    left, right = {"t": [2, 4]}, {"t": [1.0, 3.5], "v": [1, 2]}
    on_pandas, on_polars = _nearest_both(left, right, using="t", match="nearest before")
    assert on_pandas == on_polars == [{"t": 2, "v": 1, "t_other": 1.0}, {"t": 4, "v": 2, "t_other": 3.5}]
    on_pandas, on_polars = _nearest_both(right, left, using="t", match="nearest after",
                                         keep="all rows from this table")
    assert on_pandas == on_polars and [r["t_other"] for r in on_pandas] == [2, 4]


def test_nearest_join_keeps_the_pandas_table_pandas():
    t = build({"t": [1, 2]}, "pandas")
    t.join_with({"t": [1], "v": [5]}, using="t", match="nearest before", keep="all rows from this table")
    assert isinstance(t._done(), pd.DataFrame)


def test_join_every_combination(engine, capsys):
    t = example("marks", engine)
    t.keep_columns("name", "subject")
    t.join_with({"term": ["autumn", "spring"]}, keep="every combination")
    expected = raw("marks")[["name", "subject"]].merge(pd.DataFrame({"term": ["autumn", "spring"]}), how="cross")
    same(plain(t), expected)
    polars = pl.from_pandas(raw("marks")[["name", "subject"]]).join(pl.DataFrame({"term": ["autumn", "spring"]}),
                                                                     how="cross")
    same(plain(t), polars.to_pandas())
    assert "Every row with every row: 54 x 2 = 108 rows." in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="takes no using="):
        t.join_with({"term": ["x"]}, using="name", keep="every combination")
    t.join_with({"year": [2025]}, how="cross")  # pandas' how= runs as keep= with a note
    assert len(t) == 108


# ---------------------------------------------------------------- P39 make_one_table_for_each_group_in
def test_make_one_table_for_each_group_in(engine, capsys):
    t = example("river", engine)
    tables = t.make_one_table_for_each_group_in("station")
    df = raw("river")
    expected = {k: g for k, g in df.groupby("station", sort=False, dropna=False)}
    polars = pl.from_pandas(df).partition_by("station", maintain_order=True, as_dict=True)
    assert list(tables) == list(expected) == [k[0] for k in polars]
    for key, part in tables.items():
        same(plain(part), expected[key])
        same(plain(part), polars[(key,)].to_pandas())
    out = capsys.readouterr().out
    assert '2 tables, one for each station' in out and 'tables["Station A"]' in out
    assert len(t) == len(df)  # the table does not change
    pairs = example("marks", engine).make_one_table_for_each_group_in(["class", "subject"])
    assert ("A", "Maths") in pairs and len(pairs) == raw("marks").groupby(["class", "subject"]).ngroups


def test_make_one_table_keeps_empty_keys(engine):
    t = build({"g": ["a", None, "a"], "x": [1, 2, 3]}, engine)
    tables = t.make_one_table_for_each_group_in("g")
    assert list(tables) == ["a", None]
    assert len(tables["a"]) == 2 and len(tables[None]) == 1


# ---------------------------------------------------------------- P40 length() and count_text() in formulas
def test_length_and_count_text(engine):
    t = build({"genes": ["sul1;tetM", "blaTEM", None, "a;b;c"]}, engine)
    t.add_column("name_length", "length(genes)")
    t.add_column("semicolons", "count_text(genes, ';')")
    got = plain(t)
    s = pd.Series(["sul1;tetM", "blaTEM", None, "a;b;c"])
    assert [None if pd.isna(v) else int(v) for v in got["name_length"]] == [None if pd.isna(v) else int(v)
                                                                           for v in s.str.len()]
    assert [None if pd.isna(v) else int(v) for v in got["semicolons"]] == [1, 0, None, 2]
    polars = pl.Series(["sul1;tetM", "blaTEM", None, "a;b;c"])
    assert polars.str.len_chars().to_list() == [9, 6, None, 5]
    assert polars.str.count_matches(";", literal=True).to_list() == [1, 0, None, 2]
    t.add_column("dots", "count_text(genes, '.')")  # a plain piece, never a pattern
    assert list(plain(t)["dots"].fillna(-1)) == [0, 0, -1, 0]


def test_length_in_a_condition_and_errors(engine, capsys):
    t = example("marks", engine)
    t.keep_rows_where("length(name) > 4")
    assert set(plain(t)["name"]) == {n for n in raw("marks")["name"] if len(n) > 4}
    with pytest.raises(SimplydataError, match="work on text"):
        t.add_column("x", "length(marks)")
    with pytest.raises(SimplydataError, match="column of text"):
        t.add_column("x", "length('abc')")
    with pytest.raises(SimplydataError, match="piece of text to count"):
        t.add_column("x", "count_text(name, 1)")
    with pytest.raises(SimplydataError, match="In simplydata it is called length"):
        t.add_column("x", "len(name)")
    with pytest.raises(SimplydataError, match="add it as a column first|Add it as a column first"):
        t.keep_rows_where("count_text(name, 'a') > 1")


# ---------------------------------------------------------------- P41 as_list
def test_as_list(engine):
    t = example("marks", engine)
    rows = t.as_list()
    assert rows == raw("marks").to_dict("records") == pl.from_pandas(raw("marks")).to_dicts()
    rows[0]["marks"] = -1
    assert plain(t)["marks"].iloc[0] != -1  # a copy


# ---------------------------------------------------------------- other names
@pytest.mark.parametrize("name, word", [
    ("zfill", "add_zeros_in_front_of"), ("relocate", "move_columns"), ("compare", "show_differences_from"),
    ("equals", "check_if_same_as"), ("merge_asof", "join_with"), ("partition_by", "make_one_table_for_each_group_in"),
    ("to_dicts", "as_list"), ("to_sql", "save"), ("sql", "run_sql"), ("ohlc", "find_summary_of"),
])
def test_other_names_point_to_batch3_words(name, word):
    from simplydata._errors import MissingWordError

    with pytest.raises(MissingWordError, match=rf"In simplydata this is table\.{word}\("):
        getattr(sdata.get_example("marks"), name)
