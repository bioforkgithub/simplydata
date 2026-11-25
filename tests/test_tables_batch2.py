"""Tables phase, batch 2 (approved by Manish 2026-11-25): every new word and option on a pandas and a Polars table,
checked against plain pandas and plain Polars, plus the pointers from other tools."""

from importlib.resources import files

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.data import DATE_COLUMNS, TEXT_COLUMNS
from simplydata.table import table as make_table
from simplydata.table.rows import format_from_example

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
    native = t._done() if hasattr(t, "_done") else t
    if not isinstance(native, pd.DataFrame):
        native = native.to_pandas()
    return native.reset_index(drop=True)


def same(got, expected):
    """Same columns, same values (empty cells in the same places), whatever the integer or float kinds."""
    got, expected = got.reset_index(drop=True), expected.reset_index(drop=True)
    assert list(got.columns) == list(expected.columns)
    pd.testing.assert_frame_equal(got.astype(object).where(got.notna(), None),
                                  expected.astype(object).where(expected.notna(), None), check_dtype=False)


def when(values):
    """Dates and times written in ISO 8601, some with a time of day and some without."""
    return pd.to_datetime(values, format="ISO8601")


@pytest.fixture(params=ENGINES)
def engine(request):
    return request.param


# ---------------------------------------------------------------- P17 reading options
LOGGER = "# logger 7, serial 2231\n# times in local time\n2026-05-12 08:00,8.3,9.1\n2026-05-12 08:10,8.4,9.0\n"


@pytest.mark.parametrize("fast", [False, True])
def test_reading_columns_in_the_order_given(tmp_path, monkeypatch, capsys, fast):
    monkeypatch.chdir(tmp_path)
    raw("weather").to_csv("weather.csv", index=False)
    t = sdata.table("weather.csv", columns=["rain", "month", "city"], separator=",", fast=fast)
    expected = pd.read_csv("weather.csv", usecols=["rain", "month", "city"])[["rain", "month", "city"]]
    same(plain(t), expected)
    if fast:  # Polars read_csv(columns=[...])
        same(plain(t), pl.read_csv("weather.csv", columns=["rain", "month", "city"]).select(
            "rain", "month", "city").to_pandas())
    with pytest.raises(SimplydataError, match=r'(?s)columns= names "rainfall".*Did you mean "rain"'):
        sdata.table("weather.csv", columns=["rainfall"], separator=",", fast=fast)


@pytest.mark.parametrize("fast", [False, True])
def test_reading_column_names_and_note_lines(tmp_path, monkeypatch, capsys, fast):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "logger.csv").write_text(LOGGER, encoding="utf-8")
    t = sdata.table("logger.csv", column_names=["time", "temperature", "oxygen"], skip_lines_starting_with="#",
                    separator=",", fast=fast)
    expected = pd.read_csv("logger.csv", header=None, names=["time", "temperature", "oxygen"], comment="#")
    same(plain(t), expected)
    if fast:  # Polars read_csv(has_header=False, new_columns=, comment_prefix=)
        native = pl.read_csv("logger.csv", has_header=False, new_columns=["time", "temperature", "oxygen"],
                             comment_prefix="#")
        same(plain(t), native.to_pandas())
    only = sdata.table("logger.csv", column_names=["time", "temperature", "oxygen"], columns=["oxygen", "time"],
                       skip_lines_starting_with="#", separator=",", fast=fast)
    assert only.get_column_names() == ["oxygen", "time"]
    with pytest.raises(SimplydataError, match="has 3 columns, but column_names= gives 2 names"):
        sdata.table("logger.csv", column_names=["time", "temperature"], skip_lines_starting_with="#", separator=",")


def test_reading_note_sign_inside_a_line_is_refused(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "lab.csv").write_text("# run 4\nsample,code\n1,A#2\n", encoding="utf-8")
    with pytest.raises(SimplydataError, match="Line 3 .* has \"#\" inside it"):
        sdata.table("lab.csv", skip_lines_starting_with="#")
    with pytest.raises(SimplydataError, match="one sign"):
        sdata.table("lab.csv", skip_lines_starting_with="##")


def test_reading_options_from_other_tools(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    raw("weather").to_csv("weather.csv", index=False)
    t = sdata.table("weather.csv", usecols=["month", "rain"], separator=",")
    assert "usecols= is columns= in simplydata" in capsys.readouterr().out
    assert t.get_column_names() == ["month", "rain"]
    with pytest.raises(SimplydataError, match="In simplydata this is column_names="):
        sdata.table("weather.csv", header=None)
    with pytest.raises(SimplydataError, match="for reading files"):
        sdata.table(raw("marks"), columns=["name"])


# ---------------------------------------------------------------- P15 capitals_matter=, matches_pattern=
def test_capitals_matter_false_matches_pandas_lower(engine, capsys):
    marks = raw("marks")
    t = build(marks, engine)
    t.keep_rows_where("subject", is_equal_to="MATHS", capitals_matter=False)
    same(plain(t), marks[marks["subject"].str.lower() == "maths"])
    t = build(marks, engine)
    t.remove_rows_where("subject", is_one_of=["maths", "ENGLISH"], capitals_matter=False)
    same(plain(t), marks[~marks["subject"].str.lower().isin(["maths", "english"])])
    t = build(marks, engine)
    t.keep_rows_where("name", contains="AN", capitals_matter=False)
    same(plain(t), marks[marks["name"].str.contains("an", case=False, regex=False)])
    t = build(marks, engine)
    t.keep_rows_where("subject", is_equal_to="maths")  # capitals matter by default
    assert len(t) == 0


def test_matches_pattern_on_rows_matches_pandas_and_polars(engine, capsys):
    marks = raw("marks")
    t = build(marks, engine)
    t.keep_rows_where("name", matches_pattern=r"^[AB]")
    same(plain(t), marks[marks["name"].str.contains(r"^[AB]")])
    if engine == "polars":
        same(plain(t), pl.from_pandas(marks).filter(pl.col("name").str.contains(r"^[AB]")).to_pandas())
    t = build(marks, engine)
    t.remove_rows_where("name", matches_pattern=r"^a", capitals_matter=False)
    same(plain(t), marks[~marks["name"].str.contains(r"^a", case=False)])
    with pytest.raises(SimplydataError, match="not a pattern simplydata can use"):
        build(marks, engine).keep_rows_where("name", matches_pattern="(")


def test_capitals_matter_on_the_other_text_words(engine, capsys):
    marks = raw("marks")
    t = build(marks, engine)
    t.replace_values_in("subject", "maths", with_value="Mathematics", capitals_matter=False)
    assert (plain(t)["subject"] == "Mathematics").sum() == (marks["subject"] == "Maths").sum()
    fruit = raw("fruit")
    t = build(fruit, engine)
    t.replace_text_in("shop", " SHOP", with_value="", capitals_matter=False)
    same(plain(t), fruit.assign(shop=fruit["shop"].str.replace(" SHOP", "", case=False, regex=True)))
    weather = raw("weather")
    t = build(weather, engine)
    t.keep_columns(starts_with="WIND", capitals_matter=False)
    assert t.get_column_names() == [c for c in weather.columns if c.lower().startswith("wind")]
    capsys.readouterr()
    share = build(marks, engine).find_percent_of_rows_where("subject", is_equal_to="MATHS", capitals_matter=False)
    assert share == pytest.approx(100 * (marks["subject"] == "Maths").mean())


def test_capitals_matter_is_for_text_only_and_other_names_point(engine):
    t = build(raw("marks"), engine)
    with pytest.raises(SimplydataError, match="capitals_matter=False is for conditions on text"):
        t.keep_rows_where("marks", is_above=50, capitals_matter=False)
    with pytest.raises(SimplydataError, match="In simplydata this is capitals_matter=False"):
        t.keep_rows_where("subject", is_equal_to="maths", ignore_case=True)
    with pytest.raises(SimplydataError, match="In simplydata this is matches_pattern="):
        t.keep_rows_where("name", regex="^A")


# ---------------------------------------------------------------- P22 durations and counted_in=
@pytest.mark.parametrize("amount, offset", [("1 month", pd.DateOffset(months=1)), ("2 weeks", pd.DateOffset(weeks=2)),
                                            ("30 days", pd.DateOffset(days=30)), ("1 year", pd.DateOffset(years=1))])
def test_plus_a_duration_matches_pandas_dateoffset(engine, amount, offset, capsys):
    data = pd.DataFrame({"date": when(["2026-01-31", "2024-02-29", None, "2026-03-15"])})
    t = build(data, engine)
    t.add_column("later", from_column="date", plus=amount)
    same(plain(t), data.assign(later=data["date"] + offset))
    t = build(data, engine)
    t.add_column("earlier", from_column="date", minus=amount)
    same(plain(t), data.assign(earlier=data["date"] - offset))


def test_plus_a_duration_on_polars_is_offset_by(capsys):
    data = pd.DataFrame({"date": when(["2026-01-31", "2026-03-15 12:00"])})
    t = build(data, "polars")
    t.add_column("later", from_column="date", plus="1 month")
    native = pl.from_pandas(data).with_columns(pl.col("date").dt.offset_by("1mo").alias("later"))
    same(plain(t), native.to_pandas())


def test_counted_in_hours_minutes_and_weeks(engine, capsys):
    data = pd.DataFrame({"start": when(["2026-01-01 08:00", "2026-01-03 10:30", "2026-01-01"]),
                         "end": when(["2026-01-02 09:59", "2026-01-01 10:00", None])})
    for unit, size in (("hours", "h"), ("minutes", "min"), ("weeks", "W")):
        t = build(data, engine)
        t.add_column("between", by_subtracting=["end", "start"], counted_in=unit)
        expected = np.trunc((data["end"] - data["start"]) / pd.Timedelta(1, unit=size))
        assert plain(t)["between"].tolist()[:2] == expected.tolist()[:2]
        assert pd.isna(plain(t)["between"].iloc[2])
    if engine == "polars":
        t = build(data, engine)
        t.add_column("between", by_subtracting=["end", "start"], counted_in="hours")
        native = pl.from_pandas(data).select((pl.col("end") - pl.col("start")).dt.total_hours())
        assert plain(t)["between"].tolist()[:2] == native.to_series().to_list()[:2]
    with pytest.raises(SimplydataError, match="counted_in= says the unit"):
        build(data, engine).add_column("x", from_column="start", plus="1 day", counted_in="hours")
    with pytest.raises(SimplydataError, match='number and a unit'):
        build(data, engine).add_column("x", from_column="start", plus="a month")


# ---------------------------------------------------------------- P23 written_like=
@pytest.mark.parametrize("example, layout", [("31.12.2026", "%d.%m.%Y"), ("03/15/2026", "%m/%d/%Y"),
                                             ("2026-12-31 14:30", "%Y-%m-%d %H:%M"),
                                             ("March 31, 2026", "%B %d, %Y"), ("31 Dec 2026", "%d %b %Y"),
                                             ("%d/%m/%y", "%d/%m/%y")])
def test_written_like_becomes_the_percent_codes(example, layout):
    assert format_from_example(example) == layout


@pytest.mark.parametrize("bad, said", [("03/04/2026", "cannot tell the day from the month"),
                                       ("31.12.26", "four digits"), ("31.02.2026", "not a date that exists")])
def test_written_like_refuses_an_unclear_example(bad, said):
    with pytest.raises(SimplydataError, match=said):
        format_from_example(bad)


def test_written_like_matches_strftime_and_to_datetime(engine, capsys):
    shop = raw("shop")
    t = build(shop, engine)
    t.turn_into_text("date", written_like="31.12.2026")
    same(plain(t), shop.assign(date=shop["date"].dt.strftime("%d.%m.%Y")))
    if engine == "polars":
        same(plain(t), pl.from_pandas(shop).with_columns(pl.col("date").dt.to_string("%d.%m.%Y")).to_pandas())
    data = pd.DataFrame({"when": ["03/15/2026", "12/01/2026", "15/03/2026", None]})
    t = build(data, engine)
    t.turn_into_dates("when", written_like="03/15/2026")
    expected = pd.to_datetime(data["when"], format="%m/%d/%Y", errors="coerce")
    assert plain(t)["when"].tolist()[:2] == expected.tolist()[:2]
    assert plain(t)["when"].isna().tolist() == [False, False, True, True]
    assert "1 cell could not become dates" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="order= or written_like="):
        build(data, engine).turn_into_dates("when", order="month day year", written_like="03/15/2026")


# ---------------------------------------------------------------- P24 new parts of a date
@pytest.mark.parametrize("part, pandas_way", [
    ("date", lambda d: d.dt.normalize()), ("second", lambda d: d.dt.second),
    ("is weekend", lambda d: (d.dt.day_of_week >= 5).where(d.notna(), None)),
    ("days in month", lambda d: d.dt.days_in_month), ("is month end", lambda d: d.dt.is_month_end.where(d.notna(), None)),
    ("is leap year", lambda d: d.dt.is_leap_year.where(d.notna(), None)), ("year and month", lambda d: d.dt.strftime("%Y-%m")),
    ("time", lambda d: d.dt.time)])
def test_new_date_parts_match_pandas(engine, part, pandas_way, capsys):
    data = pd.DataFrame({"d": when(["2024-02-29 13:45:07", "2026-03-14 00:00:59", None, "2026-01-31 23:00"])})
    t = build(data, engine)
    t.add_column_with_part_of_date("p", from_column="d", part=part)
    got, expected = plain(t)["p"], pandas_way(data["d"])
    assert [None if pd.isna(v) else v for v in got] == [None if pd.isna(v) else v for v in expected]


def test_new_date_parts_match_polars(capsys):
    data = pd.DataFrame({"d": when(["2024-02-29 13:45:07", "2026-03-14 00:00:59", "2026-01-31 23:00"])})
    d = pl.col("d")
    for part, expr in (("is weekend", d.dt.weekday() >= 6), ("days in month", d.dt.days_in_month()),
                       ("is leap year", d.dt.is_leap_year()), ("time", d.dt.time()),
                       ("is month end", d.dt.month_end().dt.day() == d.dt.day())):
        t = build(data, "polars")
        t.add_column_with_part_of_date("p", from_column="d", part=part)
        assert plain(t)["p"].tolist() == pl.from_pandas(data).select(expr.alias("p")).to_series().to_list(), part


# ---------------------------------------------------------------- P18 add_missing_combinations_of
def test_missing_combinations_match_pandas_reindex(engine, capsys):
    growth = raw("growth").iloc[[0, 1, 2, 5, 30, 31]].reset_index(drop=True)
    t = build(growth, engine)
    t.add_missing_combinations_of("year", "country")
    grid = pd.MultiIndex.from_product([sorted(growth["year"].unique()), sorted(growth["country"].unique())],
                                      names=["year", "country"])
    expected = growth.set_index(["year", "country"]).reindex(grid).reset_index()
    same(plain(t), expected)
    added = len(expected) - len(growth)
    assert f"Added {added} rows" in capsys.readouterr().out


def test_missing_combinations_keep_empty_keys_and_repeats(engine, capsys):
    t = build({"a": ["x", "x", "y", None], "b": [1, 1, 2, 3], "v": [1.0, 2.0, 3.0, 4.0]}, engine)
    t.add_missing_combinations_of("a", "b")
    got = plain(t)
    assert len(got) == 4 + 4  # x-2, x-3, y-1, y-3 added; the repeated x-1 stays twice; the empty key stays
    assert got["a"].iloc[-1] is None or pd.isna(got["a"].iloc[-1])
    with pytest.raises(SimplydataError, match="two or more column names"):
        t.add_missing_combinations_of("a")


# ---------------------------------------------------------------- P30 with_totals=
def test_count_rows_with_totals_matches_crosstab_margins(engine, capsys):
    fruit = raw("fruit")
    result = plain(build(fruit, engine).count_rows(for_each_group_in="shop", across="fruit", with_totals=True))
    expected = pd.crosstab(fruit["shop"], fruit["fruit"], margins=True, margins_name="(total)").reset_index()
    expected.columns.name = None
    same(result, expected)


@pytest.mark.parametrize("word, aggfunc", [("find_total_of", "sum"), ("find_average_of", "mean")])
def test_summaries_with_totals_match_pivot_table_margins(engine, word, aggfunc, capsys):
    marks = raw("marks")
    result = plain(getattr(build(marks, engine), word)("marks", for_each_group_in="class", across="subject",
                                                        with_totals=True))
    expected = pd.pivot_table(marks, index="class", columns="subject", values="marks", aggfunc=aggfunc,
                              margins=True, margins_name="(total)").reset_index()
    expected.columns.name = None
    pd.testing.assert_frame_equal(result.astype({c: float for c in result.columns[1:]}),
                                  expected.astype({c: float for c in expected.columns[1:]}), check_dtype=False)


def test_with_totals_needs_across(engine):
    with pytest.raises(SimplydataError, match="goes with across="):
        build(raw("fruit"), engine).count_rows(for_each_group_in="shop", with_totals=True)


# ---------------------------------------------------------------- P31 filling from a column and another table
def test_fill_from_a_column_matches_fillna_and_coalesce(engine, capsys):
    data = pd.DataFrame({"phone": ["1", None, None, "4"], "mobile": ["9", "8", None, "7"]})
    t = build(data, engine)
    t.fill_empty_cells_in("phone", from_column="mobile")
    same(plain(t), data.assign(phone=data["phone"].fillna(data["mobile"])))
    if engine == "polars":
        native = pl.from_pandas(data).with_columns(pl.coalesce("phone", "mobile").alias("phone"))
        same(plain(t), native.to_pandas())
    with pytest.raises(SimplydataError, match="holds number values"):
        build({"a": [1.0, None], "b": ["x", "y"]}, engine).fill_empty_cells_in("a", from_column="b")


def test_fill_empty_cells_from_another_table_matches_combine_first(engine, capsys):
    samples = raw("fjord_samples")
    backup = pd.DataFrame({"sample_id": [1, 2, 12, 99], "notes": ["calm sea", "rain", "other", "no such"],
                           "salinity": [99.0, None, 99.0, 1.0]})
    t = build(samples, engine)
    t.fill_empty_cells_from(backup, using="sample_id")
    keyed = samples.set_index("sample_id")
    expected = keyed.combine_first(backup.set_index("sample_id")).loc[keyed.index, list(keyed.columns)].reset_index()
    same(plain(t), expected)
    assert plain(t)["notes"].iloc[11] == "bottle cracked, refilled"  # a filled cell never changes
    with pytest.raises(SimplydataError, match="more than once"):
        build(samples, engine).fill_empty_cells_from({"sample_id": [1, 1], "notes": ["a", "b"]}, using="sample_id")


# ---------------------------------------------------------------- P33 rename_columns, P19 count_columns
def test_rename_columns_matches_rename_and_add_prefix(engine, capsys):
    weather = raw("weather")
    t = build(weather, engine)
    t.rename_columns({"temperature": "temp", "rain": "rain_mm"})
    same(plain(t), weather.rename(columns={"temperature": "temp", "rain": "rain_mm"}))
    t = build(weather, engine)
    t.rename_columns(add_in_front="w_")
    same(plain(t), weather.add_prefix("w_"))
    t = build(weather, engine)
    t.rename_columns(add_at_end="_2026")
    same(plain(t), weather.add_suffix("_2026"))
    with pytest.raises(SimplydataError, match="more than one column"):
        build(weather, engine).rename_columns({"temperature": "rain"})
    t = build(weather, engine)
    t.rename_columns(prefix="w_")
    assert "prefix= is add_in_front= in simplydata" in capsys.readouterr().out


def test_count_columns(engine, capsys):
    weather = raw("weather")
    assert build(weather, engine).count_columns() == weather.shape[1]
    assert f"The table has {weather.shape[1]} columns." in capsys.readouterr().out


# ---------------------------------------------------------------- P20 round_dates_in
@pytest.mark.parametrize("how, unit, pandas_way", [
    ("down_to", "month", lambda d: d.dt.to_period("M").dt.to_timestamp()), ("down_to", "hour", lambda d: d.dt.floor("h")),
    ("down_to", "week", lambda d: d.dt.to_period("W").dt.start_time), ("up_to", "day", lambda d: d.dt.ceil("D")),
    ("up_to", "15 minutes", lambda d: d.dt.ceil("15min")), ("down_to", "year", lambda d: d.dt.to_period("Y").dt.to_timestamp())])
def test_round_dates_down_and_up_match_pandas(engine, how, unit, pandas_way, capsys):
    data = pd.DataFrame({"t": when(["2026-03-15 10:29:59", "2026-03-01 00:00", None, "2026-12-31 23:50"])})
    t = build(data, engine)
    t.round_dates_in("t", **{how: unit})
    same(plain(t), data.assign(t=pandas_way(data["t"]).astype(data["t"].dtype)))


def test_round_dates_to_the_nearest_goes_half_way_up_as_polars(engine, capsys):
    data = pd.DataFrame({"t": when(["2026-01-01 10:30", "2026-01-01 11:30", "2026-01-01 11:29", None])})
    t = build(data, engine)
    t.round_dates_in("t", to_the="hour")
    expected = pl.from_pandas(data).select(pl.col("t").dt.round("1h")).to_pandas()
    same(plain(t), expected)
    with pytest.raises(SimplydataError, match="has no one length"):
        build(data, engine).round_dates_in("t", to_the="month")


def test_round_dates_up_to_the_month_on_polars(capsys):
    data = pd.DataFrame({"t": when(["2026-03-15 10:29", "2026-03-01 00:00"])})
    t = build(data, "polars")
    t.round_dates_in("t", up_to="month")
    assert plain(t)["t"].tolist() == [pd.Timestamp("2026-04-01"), pd.Timestamp("2026-03-01")]


# ---------------------------------------------------------------- P21 change_time_zone_in
def test_change_time_zone_matches_tz_localize_and_convert(engine, capsys):
    samples = raw("fjord_samples")
    t = build(samples, engine)
    t.change_time_zone_in("sampled_local", to="UTC", recorded_in="Europe/Oslo")
    expected = samples["sampled_local"].dt.tz_localize("Europe/Oslo").dt.tz_convert("UTC")
    got = plain(t)["sampled_local"]
    assert [v.isoformat() for v in got] == [v.isoformat() for v in expected]
    if engine == "polars":
        native = pl.from_pandas(samples).select(
            pl.col("sampled_local").dt.replace_time_zone("Europe/Oslo").dt.convert_time_zone("UTC")).to_series()
        assert [v.isoformat() for v in got] == [v.isoformat() for v in native.to_pandas()]


def test_change_time_zone_summer_time_gap_becomes_empty(engine, capsys):
    data = pd.DataFrame({"t": when(["2026-03-29 01:30", "2026-03-29 02:30", "2026-10-25 02:30"])})
    t = build(data, engine)
    t.change_time_zone_in("t", to="UTC", recorded_in="Europe/Oslo")
    assert plain(t)["t"].isna().tolist() == [False, True, True]
    assert "2 clock times never happened or happened twice" in capsys.readouterr().out


def test_change_time_zone_asks_where_times_were_written(engine):
    data = pd.DataFrame({"t": when(["2026-05-12 08:00"])})
    with pytest.raises(SimplydataError, match="recorded_in="):
        build(data, engine).change_time_zone_in("t", to="UTC")
    with pytest.raises(SimplydataError, match='Did you mean "Europe/Oslo"'):
        build(data, engine).change_time_zone_in("t", to="UTC", recorded_in="Europe/Olso")


# ---------------------------------------------------------------- P27 spread_into_yes_no_columns
def test_yes_no_columns_match_get_dummies_and_to_dummies(engine, capsys):
    fruit = raw("fruit")
    t = build(fruit, engine)
    t.spread_into_yes_no_columns("fruit")
    dummies = pd.get_dummies(fruit["fruit"], prefix="fruit", prefix_sep=": ")
    same(plain(t), pd.concat([fruit, dummies], axis=1))
    if engine == "polars":
        native = pl.from_pandas(fruit)["fruit"].to_dummies(separator=": ").cast(pl.Boolean).to_pandas()
        same(plain(t)[list(native.columns)], native)


def test_yes_no_columns_with_a_separator_and_empty_cells(engine, capsys):
    data = pd.DataFrame({"genes": ["sul1;tetM", "tetM", None, "blaCTX;;sul1"]})
    t = build(data, engine)
    t.spread_into_yes_no_columns("genes", separator=";")
    dummies = data["genes"].str.get_dummies(sep=";").drop(columns="").add_prefix("genes: ").astype(bool)
    got = plain(t)
    assert list(got.columns) == ["genes", *sorted(dummies.columns), "genes: (empty)"]
    for c in dummies.columns:
        assert got[c].tolist() == dummies[c].tolist()
    assert got["genes: (empty)"].tolist() == [False, False, True, False]
    assert 'the column "genes: (empty)" is True there' in capsys.readouterr().out


@pytest.mark.parametrize("separator", [None, ";"])
def test_yes_no_column_of_empty_cells_has_one_name_on_both_engines(separator, capsys):
    data = pd.DataFrame({"fruit": ["pear", None, "apple", "  "]})
    names = []
    for engine in ENGINES:
        t = build(data, engine)
        t.spread_into_yes_no_columns("fruit", separator=separator)
        names.append(t.get_column_names())
        assert plain(t)["fruit: (empty)"].tolist() == [False, True, False, True]
    assert names[0] == names[1] == ["fruit", "fruit: apple", "fruit: pear", "fruit: (empty)"]
    expected = pd.get_dummies(data["fruit"].str.strip().replace("", None), prefix="fruit", prefix_sep=": ",
                              dummy_na=True)  # pandas names it "fruit: nan"
    assert plain(t)["fruit: apple"].tolist() == expected["fruit: apple"].tolist()


@pytest.mark.parametrize("engine_", ENGINES)
def test_yes_no_value_empty_next_to_empty_cells_is_refused(engine_):
    t = build({"fruit": ["(empty)", None, "pear"]}, engine_)
    with pytest.raises(SimplydataError, match=r'fill_empty_cells_in\("fruit", with_value="not recorded"\)'):
        t.spread_into_yes_no_columns("fruit")


# ---------------------------------------------------------------- P28 add_rank_column options
@pytest.mark.parametrize("when_tied, method", [("share the best place", "min"), ("share the average place", "average"),
                                               ("no gaps", "dense"), ("in table order", "first")])
def test_rank_in_groups_matches_pandas_rank(engine, when_tied, method, capsys):
    marks = raw("marks")
    t = build(marks, engine)
    t.add_rank_column("place", from_column="marks", for_each_group_in="subject", when_tied=when_tied)
    expected = marks.groupby("subject")["marks"].rank(method=method, ascending=False)
    assert plain(t)["place"].tolist() == expected.tolist()
    if engine == "polars":
        polars_method = "ordinal" if method == "first" else method
        native = pl.from_pandas(marks).select(pl.col("marks").rank(polars_method, descending=True).over("subject"))
        assert plain(t)["place"].tolist() == native.to_series().cast(pl.Float64).to_list()


def test_rank_method_points_to_when_tied(engine):
    with pytest.raises(SimplydataError, match="In simplydata this is when_tied="):
        build(raw("marks"), engine).add_rank_column("place", from_column="marks", method="dense")


# ---------------------------------------------------------------- P29 into_equal_groups=
def test_equal_groups_match_qcut(engine, capsys):
    marks = raw("marks")
    t = build(marks, engine)
    t.add_group_column("quarter", from_column="marks", into_equal_groups=4)
    expected = pd.qcut(marks["marks"], 4, labels=False) + 1
    assert plain(t)["quarter"].tolist() == expected.tolist()
    if engine == "polars":
        native = pl.from_pandas(marks)["marks"].qcut(4, labels=["1", "2", "3", "4"]).cast(pl.String).cast(pl.Int64)
        assert plain(t)["quarter"].tolist() == native.to_list()
    cuts = pd.qcut(marks["marks"], 4, retbins=True)[1][1:-1]
    assert "cut at " + ", ".join(f"{c:g}" for c in cuts) in capsys.readouterr().out
    t = build(marks, engine)
    t.add_group_column("half", from_column="marks", into_equal_groups=2, names=["lower", "upper"])
    assert plain(t)["half"].tolist() == pd.qcut(marks["marks"], 2, labels=["lower", "upper"]).astype(str).tolist()


def test_equal_groups_with_too_many_ties_say_so(engine):
    with pytest.raises(SimplydataError, match="too many equal values"):
        build({"x": [1, 1, 1, 1, 1, 2]}, engine).add_group_column("g", from_column="x", into_equal_groups=4)
