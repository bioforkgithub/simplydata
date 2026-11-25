"""Tables phase, batch 1 (approved by Manish 2026-11-25): every new word and option on a pandas and a Polars table,
checked against plain pandas and plain Polars, plus the fjord practice tables and the pointers from other tools."""

from importlib.resources import files

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata._errors import MissingWordError
from simplydata.data import DATE_COLUMNS, TEXT_COLUMNS
from simplydata.table import table as make_table
from simplydata.table.more_table_words import clean_name

pl = pytest.importorskip("polars")
ENGINES = ["pandas", "polars"]


def raw(name):
    """A practice table read straight from its file by pandas (the reference side)."""
    with (files("simplydata.data") / f"{name}.csv").open("r", encoding="utf-8") as fh:
        text = {c: str for c in TEXT_COLUMNS.get(name, [])}
        return pd.read_csv(fh, parse_dates=DATE_COLUMNS.get(name, False), dtype=text or None)


def build(data, engine):
    data = pd.DataFrame(data)
    return make_table(data, fast=True) if engine == "polars" else make_table(data)


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


# ---------------------------------------------------------------- P01 read_as_text=
def test_read_as_text_keeps_ids_as_typed(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    raw("fjord_lab").to_csv("lab.csv", index=False)
    assert pd.read_csv("lab.csv")["sample_id"].iloc[0] == 1  # what pandas does without being told: 001 is 1
    for fast in (False, True):
        lab = sdata.table("lab.csv", read_as_text=["sample_id", "lab_code"], fast=fast)
        expected = pd.read_csv("lab.csv", dtype={"sample_id": str, "lab_code": str})["sample_id"]
        got = plain(lab)["sample_id"]
        assert got.iloc[0] == "001" and list(got.fillna("")) == list(expected.fillna(""))
        if fast:  # Polars read_csv(schema_overrides={"sample_id": pl.String})
            polars = pl.read_csv("lab.csv", schema_overrides={"sample_id": pl.String})["sample_id"].to_list()
            assert [None if pd.isna(v) else v for v in got] == polars
    one = sdata.table("lab.csv", read_as_text="sample_id")
    assert one.get_cell_at(row=1, column="sample_id") == "001"
    with pytest.raises(SimplydataError, match='Did you mean "sample_id"'):
        sdata.table("lab.csv", read_as_text=["sampleid"])
    with pytest.raises(SimplydataError, match="list of the column names"):
        sdata.table("lab.csv", read_as_text=[1])
    with pytest.raises(SimplydataError, match="for reading files"):
        sdata.table(raw("marks"), read_as_text=["name"])


def test_read_as_text_from_other_tools(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    raw("fjord_lab").to_csv("lab.csv", index=False)
    lab = sdata.table("lab.csv", dtype={"sample_id": str})
    assert "Note: dtype= is read_as_text= in simplydata." in capsys.readouterr().out
    assert lab.get_cell_at(row=1, column="sample_id") == "001"
    assert sdata.table("lab.csv", schema_overrides={"sample_id": pl.String}).get_cell_at(row=1, column="sample_id") == "001"
    with pytest.raises(SimplydataError, match="turn_into_numbers"):
        sdata.table("lab.csv", dtype={"ct": float})


# ---------------------------------------------------------------- P14 join_with options
PEOPLE = {"student": ["Asha", "Ben", "Zoe"], "age": [12, 13, 11]}


def test_join_using_two_names_matches_pandas(engine, capsys):
    marks = raw("marks")
    t = build(marks, engine)
    t.join_with(PEOPLE, using={"name": "student"})
    expected = marks.merge(pd.DataFrame(PEOPLE), left_on="name", right_on="student").drop(columns="student")
    same(plain(t), expected)
    assert "using name = student" in t._history[-1][0]


@pytest.mark.parametrize("engine_", ENGINES)
def test_join_keeps_all_rows_from_the_other_table(engine_, capsys):
    marks = raw("marks")
    other = pd.DataFrame({"name": ["Zoe", "Asha", "Ben"], "age": [11, 12, 13], "height": [1, 2, 3]})
    t = build(marks, engine_)
    t.join_with(other, using="name", keep="all rows from the other table")
    out = capsys.readouterr().out
    assert "2 of 3 rows in the other table found a match in this table." in out
    expected = marks.merge(other, on="name", how="right", suffixes=("", "_other"))
    same(plain(t), expected)
    if engine_ == "polars":  # Polars join(how="right") gives the same rows; simplydata puts the columns in pandas' order
        native = pl.from_pandas(marks).join(pl.from_pandas(other), on="name", how="right", suffix="_other",
                                            maintain_order="right_left")
        same(plain(t), native.select(list(expected.columns)).to_pandas())


def test_join_how_runs_as_keep(engine, capsys):
    t = build(raw("marks"), engine)
    t.join_with(PEOPLE, using={"name": "student"}, how="left")
    out = capsys.readouterr().out
    assert 'Note: how="left" is keep="all rows from this table" in simplydata.' in out
    assert len(t) == 54


def test_join_check_that(engine, capsys):
    t = build(raw("marks"), engine)
    repeated = {"name": ["Asha", "Asha", "Ben"], "pet": ["cat", "dog", "fish"]}
    with pytest.raises(SimplydataError, match=r'check_that="each row has one match" failed: 1 value of name appear '
                                              r'more than once in the other table: "Asha"'):
        t.join_with(repeated, using="name", check_that="each row has one match")
    assert len(t) == 54 and not t._history  # nothing joined
    with pytest.raises(SimplydataError, match="more than once in this table"):
        t.join_with({"name": ["Asha"], "pet": ["cat"]}, using="name", check_that="each key appears once here")
    t.join_with({"name": ["Asha"], "pet": ["cat"]}, using="name", check_that="each row has one match")
    assert len(t) == 3
    # the same check in pandas itself
    with pytest.raises(pd.errors.MergeError):
        raw("marks").merge(pd.DataFrame(repeated), on="name", validate="many_to_one")
    with pytest.raises(SimplydataError, match='Did you mean check_that="each row has one match"'):
        t.join_with(repeated, using="name", check_that="each row has a match")


def test_join_with_match_column_matches_pandas_indicator(engine, capsys):
    marks = raw("marks")[["name", "subject", "marks"]]
    t = build(marks, engine)
    t.join_with(PEOPLE, using={"name": "student"}, keep="all rows from both", with_match_column=True)
    expected = marks.merge(pd.DataFrame(PEOPLE).rename(columns={"student": "name"}), on="name", how="outer",
                           indicator="found in")
    expected["found in"] = expected["found in"].map({"both": "both", "left_only": "this table only",
                                                     "right_only": "other table only"}).astype(object)
    got = plain(t)
    assert sorted(map(tuple, got.astype(str).values)) == sorted(map(tuple, expected.astype(str).values))
    assert "other table only 1 row" in capsys.readouterr().out


def test_join_pointers_never_run(engine):
    t = build(raw("marks"), engine)
    for option in ("left_on", "right_on", "validate", "indicator"):
        with pytest.raises(SimplydataError, match="In simplydata this is"):
            t.join_with(PEOPLE, **{option: "name"})
    assert not t._history


def test_join_text_and_numbers_say_how_to_fix(capsys):
    samples, lab = sdata.get_example("fjord_samples"), sdata.get_example("fjord_lab")
    with pytest.raises(SimplydataError, match="turn_into_numbers"):
        samples.join_with(lab, using="sample_id")


def test_join_whole_numbers_with_decimals_on_polars(capsys):
    samples = sdata.table(sdata.get_example("fjord_samples").as_polars())
    lab = sdata.table(sdata.get_example("fjord_lab").as_polars())
    lab.turn_into_numbers("sample_id")
    lab.change_column("sample_id", "sample_id / 1")  # whole numbers kept as decimals (7.0)
    samples.keep_rows_found_in(lab, using="sample_id")
    assert len(samples) == 59
    lab.change_column("sample_id", "sample_id / 2")
    with pytest.raises(SimplydataError, match="numbers with decimals"):
        samples.keep_rows_found_in(lab, using="sample_id")


# ---------------------------------------------------------------- P02 keep_rows_found_in / remove_rows_found_in
def test_rows_found_in_match_pandas_and_polars(engine, capsys):
    marks = raw("marks")
    other = pd.DataFrame({"name": ["Asha", "Ben", "Asha"]})  # a repeated key never repeats a row
    t = build(marks, engine)
    t.keep_rows_found_in(other, using="name")
    same(plain(t), marks[marks["name"].isin(other["name"])])
    assert "Kept 6 of 54 rows" in capsys.readouterr().out
    t.undo()
    t.remove_rows_found_in(other, using="name")
    same(plain(t), marks[~marks["name"].isin(other["name"])])
    semi = pl.from_pandas(marks).join(pl.from_pandas(other).unique(), on="name", how="semi", maintain_order="left")
    anti = pl.from_pandas(marks).join(pl.from_pandas(other), on="name", how="anti", maintain_order="left")
    t.undo()
    t.keep_rows_found_in(other, using="name")
    same(plain(t), semi.to_pandas())
    t.undo()
    t.remove_rows_found_in(other, using="name")
    same(plain(t), anti.to_pandas())


def test_rows_found_in_with_two_names_and_empty_keys(engine, capsys):
    t = build({"id": [1, 2, None, 4], "x": [1, 2, 3, 4]}, engine)
    t.keep_rows_found_in({"sample": [2, 4, 9]}, using={"id": "sample"})
    assert plain(t)["x"].tolist() == [2, 4]
    t.undo()
    t.remove_rows_found_in({"sample": [2, 4]}, using={"id": "sample"})
    assert plain(t)["x"].tolist() == [1, 3]
    assert "an empty id = sample, which is never found" in capsys.readouterr().out


def test_fjord_samples_without_a_lab_result(capsys):
    samples, lab = sdata.get_example("fjord_samples"), sdata.get_example("fjord_lab")
    lab.turn_into_numbers("sample_id")
    samples.remove_rows_found_in(lab, using="sample_id")
    assert plain(samples)["sample_id"].tolist() == [23]


# ---------------------------------------------------------------- P03 for_each_group_in= on the position words
def test_first_and_last_rows_of_each_group(engine, capsys):
    marks = raw("marks").sort_values("marks", ascending=False, kind="stable").reset_index(drop=True)
    t = build(marks, engine)
    t.keep_first_rows(2, for_each_group_in="subject")
    same(plain(t), marks.groupby("subject", sort=False).head(2))
    polars = pl.from_pandas(marks).filter(pl.int_range(pl.len()).over("subject") < 2).to_pandas()
    same(plain(t), polars)
    t.undo()
    t.keep_last_rows(1, for_each_group_in=["name"])
    same(plain(t), marks.groupby("name", sort=False).tail(1))
    t.undo()
    t.keep_rows_by_position([1, 3], for_each_group_in="name")
    same(plain(t), marks.groupby("name", sort=False).nth([0, 2]))
    t.undo()
    t.keep_rows_by_position(2, to="last", for_each_group_in="name")
    same(plain(t), marks.groupby("name", sort=False).nth(slice(1, None)))
    with pytest.raises(SimplydataError, match="keep_last_rows"):
        t.keep_rows_by_position("last", for_each_group_in="name")
    t.keep_first_rows(how_many=1)
    assert len(t) == 1


# ---------------------------------------------------------------- P04 clean_column_names
@pytest.mark.parametrize("name, clean", [
    ("Max Temp (°C)", "max_temp_c"), ("Sample ID ", "sample_id"), ("pH", "ph"), ("% cover", "percent_cover"),
    ("# of eggs", "number_of_eggs"), ("Fjørd", "fjord"), ("Unnamed: 0", "unnamed_0"), ("2026", "x2026"),
    ("µg/L", "ug_l"), ("Distance to outfall (km)", "distance_to_outfall_km"), ("(°)", "x"), ("Råvika", "ravika"),
])
def test_clean_name_follows_the_janitor_rule(name, clean):
    assert clean_name(name) == clean


def test_clean_column_names(engine, capsys):
    t = build({"Max Temp (°C)": [1], "max temp (C)": [2], "pH": [7.1]}, engine)
    t.clean_column_names()
    assert t.get_column_names() == ["max_temp_c", "max_temp_c_2", "ph"]
    out = capsys.readouterr().out
    assert '"Max Temp (°C)" -> max_temp_c' in out and "Cleaned 3 of 3" in out
    t.clean_column_names()
    assert "already clean" in capsys.readouterr().out
    stations = sdata.get_example("fjord_stations").clean_column_names()
    assert stations.get_column_names() == ["station", "fjord", "latitude_n", "longitude_e", "distance_to_outfall_km"]


# ---------------------------------------------------------------- P05 empty rows and columns
def test_all_empty_rows_and_columns_match_pandas(engine, capsys):
    lab = raw("fjord_lab")
    t = build(lab, engine)
    t.remove_rows_that_are_all_empty()
    same(plain(t), lab.dropna(how="all"))
    assert "Removed 2 of 244 rows" in capsys.readouterr().out
    t.remove_columns_that_are_all_empty()
    same(plain(t), lab.dropna(how="all").dropna(axis=1, how="all"))
    polars = pl.from_pandas(lab).filter(~pl.all_horizontal(pl.all().is_null()))
    polars = polars.select([c for c in polars.columns if polars[c].null_count() < polars.height])
    same(plain(t), polars.to_pandas())


def test_text_of_only_spaces_counts_as_empty(engine, capsys):
    t = build({"a": ["x", "  ", None], "b": [1.0, None, None], "c": [" ", "", None]}, engine)
    t.remove_rows_that_are_all_empty()
    assert len(t) == 1
    t.remove_columns_that_are_all_empty()
    assert t.get_column_names() == ["a", "b"]


# ---------------------------------------------------------------- P06 show_duplicate_rows and keep=
def test_show_duplicate_rows_matches_pandas(engine, capsys):
    lab = raw("fjord_lab").dropna(how="all").reset_index(drop=True)
    t = build(lab, engine)
    t.show_duplicate_rows()
    out = capsys.readouterr().out
    shown = lab[lab.duplicated(keep=False)]
    assert f"{len(shown)} rows repeat another row" in out
    for position in shown.index:
        assert f"\n{position + 1} " in out
    assert len(t) == len(lab) and not t._history  # the table does not change
    t.show_duplicate_rows(columns=["sample_id", "gene", "lab_code", "copies_per_ml", "ct"])
    t.remove_duplicate_rows()
    t.show_duplicate_rows(columns=["sample_id", "gene"])
    assert "0 rows repeat another row in sample_id, gene" in capsys.readouterr().out


@pytest.mark.parametrize("keep", ["first", "last", "none"])
def test_remove_duplicate_rows_keep(engine, keep, capsys):
    marks = raw("marks")
    t = build(marks, engine)
    t.remove_duplicate_rows(columns=["name"], keep=keep)
    same(plain(t), marks.drop_duplicates(subset=["name"], keep=False if keep == "none" else keep))
    polars = pl.from_pandas(marks).unique(subset=["name"], keep=keep, maintain_order=True)
    same(plain(t), polars.to_pandas())


def test_remove_duplicate_rows_keep_false_points_to_none(engine):
    with pytest.raises(SimplydataError, match='keep="none"'):
        build(raw("marks"), engine).remove_duplicate_rows(keep=False)


# ---------------------------------------------------------------- P07 add_row_summary_column
COLUMNS = ["a", "b", "c"]
ROWS = {"a": [1.0, None, None, 4.0], "b": [2.0, 3.0, None, 4.0], "c": [6.0, 5.0, None, 1.0]}


@pytest.mark.parametrize("show, pandas_way, polars_way", [
    ("average", lambda d: d.mean(axis=1), pl.mean_horizontal(COLUMNS)),
    ("total", lambda d: d.sum(axis=1, min_count=1), None),
    ("median", lambda d: d.median(axis=1), pl.concat_list(COLUMNS).list.median()),
    ("smallest", lambda d: d.min(axis=1), pl.min_horizontal(COLUMNS)),
    ("biggest", lambda d: d.max(axis=1), pl.max_horizontal(COLUMNS)),
    ("standard deviation", lambda d: d.std(axis=1), pl.concat_list(COLUMNS).list.std()),
    ("count", lambda d: d.count(axis=1), pl.sum_horizontal(pl.col(COLUMNS).is_not_null())),
])
def test_row_summary_matches_pandas_and_polars(engine, show, pandas_way, polars_way, capsys):
    data = pd.DataFrame(ROWS)
    t = build(data, engine)
    t.add_row_summary_column("s", columns=COLUMNS, show=show)
    got = plain(t)["s"].astype(float)
    np.testing.assert_allclose(got, pandas_way(data[COLUMNS]).astype(float), rtol=1e-12)
    if polars_way is not None:
        expected = pl.from_pandas(data).select(polars_way.alias("s"))["s"].cast(pl.Float64).to_numpy()
        if show != "total":
            np.testing.assert_allclose(got, expected, rtol=1e-12)
    assert "2 rows had an empty cell, which was left out" in capsys.readouterr().out


def test_row_summary_on_the_clinic_table(engine, capsys):
    clinic = raw("clinic")
    weeks = ["pain_week_0", "pain_week_4", "pain_week_8"]
    t = build(clinic, engine)
    t.add_row_summary_column("pain_average", columns=weeks, show="mean")
    assert 'show="mean" is show="average"' in capsys.readouterr().out
    np.testing.assert_allclose(plain(t)["pain_average"], clinic[weeks].mean(axis=1), rtol=1e-12)
    with pytest.raises(SimplydataError, match="two or more column names"):
        t.add_row_summary_column("x", columns=["pain_week_0"])
    with pytest.raises(SimplydataError, match="holds text"):
        t.add_row_summary_column("x", columns=["ward", "pain_week_0"])


# ---------------------------------------------------------------- P08 spread_into_columns(show=)
@pytest.mark.parametrize("show, aggfunc", [("total", "sum"), ("average", "mean"), ("median", "median"),
                                           ("smallest", "min"), ("biggest", "max"), ("count", "size")])
def test_spread_show_matches_pivot_table(engine, show, aggfunc, capsys):
    fruit = raw("fruit")[["day", "fruit", "count"]]
    t = build(fruit, engine)
    t.spread_into_columns(names_from="fruit", values_from="count", show=show)
    expected = fruit.pivot_table(index="day", columns="fruit", values="count", aggfunc=aggfunc).reset_index()
    expected.columns.name = None
    got = plain(t)
    expected = expected.set_index("day").loc[list(got["day"]), list(got.columns[1:])].reset_index()
    same(got.astype({c: float for c in got.columns[1:]}), expected.astype({c: float for c in expected.columns[1:]}))
    if show in ("total", "count"):  # Polars pivot gives 0 for a pair that never appears; simplydata an empty cell
        polars = pl.from_pandas(fruit).pivot(on="fruit", index="day", values="count",
                                             aggregate_function="sum" if show == "total" else "len")
        assert (polars.select(pl.exclude("day")).to_pandas() == 0).to_numpy().any()
        assert got.isna().to_numpy().any()


def test_spread_without_show_names_the_repeats(engine):
    t = build(raw("fruit")[["day", "fruit", "count"]], engine)
    with pytest.raises(SimplydataError) as err:
        t.spread_into_columns(names_from="fruit", values_from="count")
    text = str(err.value)
    assert "combinations appear more than once" in text and 'show="average"' in text


def test_spread_show_from_other_tools(engine, capsys):
    t = build(raw("fruit")[["day", "fruit", "count"]], engine)
    t.spread_into_columns(names_from="fruit", values_from="count", aggfunc="sum")
    out = capsys.readouterr().out
    assert "Note: aggfunc= is show= in simplydata." in out and 'Note: "sum" is show="total" in simplydata.' in out


# ---------------------------------------------------------------- P09 turn_into_categories
def test_categories_match_pandas_and_polars(engine, capsys):
    clinic = raw("clinic")
    order = ["mild", "moderate", "severe"]
    t = build(clinic, engine)
    t.turn_into_categories("nurse_rating", in_order=order)
    t.sort_by("nurse_rating")
    expected = clinic.assign(nurse_rating=pd.Categorical(clinic["nurse_rating"], categories=order, ordered=True))
    expected = expected.sort_values("nurse_rating", kind="stable")
    assert plain(t)["patient"].tolist() == expected["patient"].tolist()
    polars = pl.from_pandas(clinic).with_columns(pl.col("nurse_rating").cast(pl.Enum(order)))
    polars = polars.with_row_index().sort(["nurse_rating", "index"])
    assert plain(t)["patient"].tolist() == polars["patient"].to_list()
    averages = plain(t.find_average_of("pain_week_0", for_each_group_in="nurse_rating"))
    assert averages["nurse_rating"].astype(str).tolist() == order


def test_categories_refuse_a_value_not_in_the_list(engine):
    t = build({"r": ["mild", "Severe", "severe", None]}, engine)
    with pytest.raises(SimplydataError, match=r'1 value that is not in in_order=: "Severe" \(1 row\)'):
        t.turn_into_categories("r", in_order=["mild", "moderate", "severe"])
    with pytest.raises(pl.exceptions.InvalidOperationError):  # Polars refuses it too
        pl.DataFrame({"r": ["mild", "Severe"]}).with_columns(pl.col("r").cast(pl.Enum(["mild", "severe"])))
    with pytest.raises(SimplydataError, match="turn_into_text"):
        build({"n": [1, 2]}, engine).turn_into_categories("n")


def test_categories_without_an_order_keep_the_first_appearance(engine, capsys):
    t = build({"r": ["b", "a", "b", "c"]}, engine)
    t.turn_into_categories("r")
    assert "in this order: b < a < c" in capsys.readouterr().out
    t.sort_by("r")
    assert plain(t)["r"].astype(str).tolist() == ["b", "b", "a", "c"]


# ---------------------------------------------------------------- P10 split_into_rows
def test_split_into_rows_matches_explode(engine, capsys):
    data = pd.DataFrame({"sample": ["S1", "S2", "S3", "S4"], "genes": ["sul1;tetM", "blaOXA48", None, "a; b"]})
    t = build(data, engine)
    t.split_into_rows("genes", separator=";")
    expected = data.assign(genes=data["genes"].str.split(";")).explode("genes", ignore_index=True)
    same(plain(t), expected)
    polars = pl.from_pandas(data).with_columns(pl.col("genes").str.split(";")).explode("genes")
    same(plain(t), polars.to_pandas())
    out = capsys.readouterr().out
    assert "4 rows became 6 rows" in out and "remove_extra_spaces_in" in out
    with pytest.raises(SimplydataError, match="separator="):
        build(data, engine).split_into_rows("genes")


def test_split_into_rows_of_a_list_column():
    t = sdata.table(pl.DataFrame({"s": ["S1", "S2"], "genes": [["sul1", "tetM"], ["intI1"]]}))
    t.split_into_rows("genes")
    assert plain(t)["genes"].tolist() == ["sul1", "tetM", "intI1"]


def test_split_the_fjord_crew(capsys):
    samples = sdata.get_example("fjord_samples")
    crew = raw("fjord_samples")["crew"].str.split(";").explode()
    samples.split_into_rows("crew", separator=";")
    assert plain(samples)["crew"].tolist() == crew.tolist()


# ---------------------------------------------------------------- P11 add_running_column
@pytest.mark.parametrize("show, pandas_way", [
    ("total", "cumsum"), ("biggest", "cummax"), ("smallest", "cummin"), ("product", "cumprod"),
])
def test_running_matches_pandas_groupby(engine, show, pandas_way, capsys):
    shop = raw("shop").sort_values("date").reset_index(drop=True)
    shop["sales"] = shop["sales"] / 100
    t = build(shop, engine)
    t.add_running_column("so_far", from_column="sales", show=show, for_each_group_in="shop", sorted_by="date")
    expected = getattr(shop.groupby("shop")["sales"], pandas_way)()
    np.testing.assert_allclose(plain(t)["so_far"].astype(float), expected.astype(float), rtol=1e-12)
    method = {"total": "cum_sum", "biggest": "cum_max", "smallest": "cum_min", "product": "cum_prod"}[show]
    polars = pl.from_pandas(shop).select(getattr(pl.col("sales"), method)().over("shop"))["sales"].to_numpy()
    np.testing.assert_allclose(plain(t)["so_far"].astype(float), polars.astype(float), rtol=1e-12)


def test_running_average_and_count(engine, capsys):
    shop = raw("shop")
    t = build(shop, engine)
    t.add_running_column("average", from_column="sales", show="average", for_each_group_in="shop", sorted_by="date")
    t.add_running_column("count", from_column="sales", show="count", for_each_group_in="shop", sorted_by="date")
    expected = shop.groupby("shop")["sales"].expanding().mean().reset_index(level=0, drop=True).sort_index()
    expected[shop["sales"].isna()] = np.nan  # an empty cell stays empty
    np.testing.assert_allclose(plain(t)["average"], expected, rtol=1e-12)
    counted = pl.from_pandas(shop).select(pl.col("sales").cum_count().over("shop"))["sales"].to_numpy()
    np.testing.assert_array_equal(plain(t)["count"].to_numpy(), counted)


def test_running_keeps_the_rows_in_place(engine, capsys):
    t = build({"d": [3, 1, 2], "x": [30, 10, 20]}, engine)
    t.add_running_column("total", from_column="x", sorted_by="d")
    assert plain(t)["total"].tolist() == [60, 10, 30]


# ---------------------------------------------------------------- P12 add_row_number_column
def test_row_numbers_match_cumcount(engine, capsys):
    river = raw("river").sample(frac=1, random_state=1).reset_index(drop=True)
    t = build(river, engine)
    t.add_row_number_column("day_number", for_each_group_in="station", sorted_by="date")
    ordered = river.sort_values(["date"], kind="stable")
    expected = (ordered.groupby("station").cumcount() + 1).sort_index()
    assert plain(t)["day_number"].tolist() == expected.tolist()
    polars = (pl.from_pandas(river).with_row_index().sort("date")
              .with_columns(pl.int_range(1, pl.len() + 1).over("station").alias("n")).sort("index"))
    assert plain(t)["day_number"].tolist() == polars["n"].to_list()
    t.add_row_number_column("row")
    assert plain(t)["row"].tolist() == list(range(1, len(river) + 1))


# ---------------------------------------------------------------- P13 keep_groups_where / remove_groups_where
def test_keep_groups_where_matches_groupby_filter(engine, capsys):
    school = raw("school")
    t = build(school, engine)
    t.keep_groups_where("average(marks) >= 50", for_each_group_in="school")
    same(plain(t), school.groupby("school").filter(lambda g: g["marks"].mean() >= 50))
    polars = pl.from_pandas(school).filter(pl.col("marks").mean().over("school") >= 50).to_pandas()
    same(plain(t), polars)
    assert "groups of \"school\"" in capsys.readouterr().out
    t.undo()
    t.remove_groups_where("count() >= 15 and average(sleep) > 7", for_each_group_in="school")
    same(plain(t), school.groupby("school").filter(lambda g: not (len(g) >= 15 and g["sleep"].mean() > 7)))


def test_keep_groups_where_needs_a_summary(engine):
    t = build(raw("school"), engine)
    with pytest.raises(SimplydataError, match="needs a summary of each group"):
        t.keep_groups_where("marks >= 50", for_each_group_in="school")
    with pytest.raises(SimplydataError, match='"hours" on its own'):
        t.keep_groups_where("average(marks) >= hours", for_each_group_in="school")
    with pytest.raises(SimplydataError, match="needs for_each_group_in="):
        t.keep_groups_where("average(marks) >= 50")
    with pytest.raises(SimplydataError, match="average"):
        t.keep_groups_where("mean(marks) >= 50", for_each_group_in="school")


# ---------------------------------------------------------------- P16 in_rows_where=
def test_change_column_in_rows_where_matches_loc(engine, capsys):
    school = raw("school")
    t = build(school, engine)
    t.change_column("passed", value="yes", in_rows_where="marks >= 45")
    expected = school.copy()
    expected.loc[expected["marks"] >= 45, "passed"] = "yes"
    same(plain(t), expected)
    polars = pl.from_pandas(school).with_columns(
        pl.when(pl.col("marks") >= 45).then(pl.lit("yes")).otherwise(pl.col("passed")).alias("passed"))
    same(plain(t), polars.to_pandas())
    assert "only in the 108 rows where marks >= 45" in capsys.readouterr().out
    t.undo()
    assert plain(t)["passed"].tolist() == school["passed"].tolist()
    with pytest.raises(SimplydataError, match="one column cannot hold both"):
        t.change_column("passed", value=1, in_rows_where="marks >= 45")


def test_in_rows_where_keeps_rows_it_cannot_check(engine, capsys):
    school = raw("school")
    t = build(school, engine)
    t.change_column("hours", "hours * 2", in_rows_where="sleep < 7")
    expected = school.copy()
    expected.loc[expected["sleep"] < 7, "hours"] = expected["hours"] * 2
    same(plain(t), expected)
    assert "keep their value" in capsys.readouterr().out


def test_replace_and_fill_in_rows_where(engine, capsys):
    shop = raw("shop")
    t = build(shop, engine)
    t.fill_empty_cells_in("customers", with_value=0, in_rows_where="shop == 'Northgate'")
    expected = shop.copy()
    rows = (expected["shop"] == "Northgate") & expected["customers"].isna()
    expected.loc[rows, "customers"] = 0
    same(plain(t), expected)
    marks = raw("marks")
    m = build(marks, engine)
    m.replace_values_in("subject", "Maths", with_value="Math", in_rows_where="class == 'A'")
    expected = marks.copy()
    expected.loc[(expected["class"] == "A") & (expected["subject"] == "Maths"), "subject"] = "Math"
    same(plain(m), expected)
    m.undo()
    m.replace_values_in("marks", is_above=90, with_value=90, in_rows_where="class == 'B'")
    expected = marks.copy()
    expected.loc[(expected["class"] == "B") & (expected["marks"] > 90), "marks"] = 90
    same(plain(m), expected)


# ---------------------------------------------------------------- the practice data and the pointers
def test_fjord_tables_are_messy_on_purpose():
    samples = raw("fjord_samples")
    assert {"St.3 ", "st.3"} <= set(samples["station"]) and "Råvika" in set(samples["station"])
    lab = raw("fjord_lab")
    assert lab["sample_id"].iloc[0] == "001" and "141" in set(lab["sample_id"])
    assert {"<LOD", "n.d."} <= set(lab["copies_per_ml"]) and {"3-12", "2/4"} <= set(lab["lab_code"])
    assert lab.isna().all(axis=1).sum() == 2 and lab["checked_by"].isna().all()
    assert lab.dropna(how="all").duplicated().sum() == 6
    assert "23" not in set(lab["sample_id"].dropna().str.lstrip("0"))


@pytest.mark.parametrize("name, word", [
    ("semi_join", "keep_rows_found_in"), ("isin", "keep_rows_found_in"), ("anti_join", "remove_rows_found_in"),
    ("clean_names", "clean_column_names"), ("remove_empty", "remove_rows_that_are_all_empty"),
    ("duplicated", "show_duplicate_rows"), ("get_dupes", "show_duplicate_rows"), ("rowMeans", "add_row_summary_column"),
    ("mean_horizontal", "add_row_summary_column"), ("factor", "turn_into_categories"),
    ("Categorical", "turn_into_categories"), ("explode", "split_into_rows"), ("separate_rows", "split_into_rows"),
    ("cumsum", "add_running_column"), ("cum_sum", "add_running_column"), ("cumcount", "add_row_number_column"),
    ("row_number", "add_row_number_column"), ("having", "keep_groups_where"), ("right_join", "join_with"),
])
def test_other_names_point_to_the_new_words(name, word):
    table = sdata.get_example("marks")
    with pytest.raises(MissingWordError) as info:
        getattr(table, name)
    assert f"In simplydata this is table.{word}(" in str(info.value)
