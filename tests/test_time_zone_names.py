"""Time zone names with "_", "-", "+" or digits (America/New_York, America/Port-au-Prince, Etc/GMT+5) on a pandas
and a Polars table.

narwhals 2.27 to 2.29 reads such a pandas column as Unknown (its pattern for the written dtype
"datetime64[us, America/New_York]" takes only letters and "/" in the zone), so every date word on a pandas table
stopped or called the column "other values"; simplydata._narwhals_mend widens that pattern. Every word here must give
the same values and the same zone on both engines, and a few values are written out by hand (worked out from the
standard time zone rules, not from either engine).
"""

import datetime as dt

import narwhals as nw
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table

pl = pytest.importorskip("polars")
ENGINES = ["pandas", "polars"]
ZONES = ["Europe/Oslo", "America/New_York", "America/Port-au-Prince", "Etc/GMT+5", "America/Argentina/Buenos_Aires",
         "UTC"]
TIMES = ["1959-07-01 00:00", "2024-01-15 12:30", "2024-07-01 23:45", "2024-03-02 06:10", None, "2024-11-30 18:00"]


@pytest.fixture(params=ENGINES)
def engine(request):
    return request.param


def build(data, engine):
    data = pd.DataFrame(data)
    return make_table(data, fast=True) if engine == "polars" else make_table(data)


def zoned(zone, times=TIMES):
    return pd.to_datetime(times).as_unit("us").tz_localize(zone)


def sample(zone):
    t = zoned(zone)
    return pd.DataFrame({"t": t, "u": t + pd.Timedelta(days=3, hours=5), "g": list("aabbab"),
                         "v": [1.0, 2, 3, 4, 5, 6], "naive": pd.to_datetime(TIMES).as_unit("us")})


def as_polars(result):
    """The result as a Polars table, to compare both engines cell by cell and kind by kind."""
    return result._frame.to_polars() if hasattr(result, "_frame") else result


def both(zone, word, capsys=None):
    """Run one word on a pandas table and on a Polars table of the same values."""
    data = sample(zone)
    got = [as_polars(word(build(data, engine))) for engine in ENGINES]
    if capsys is not None:
        capsys.readouterr()
    return got


def assert_same(pandas_result, polars_result):
    """Same columns, same cells; a date column also has the same time zone. Whole-number widths may differ
    (pandas int32 or float with an empty cell, Polars int8), as on every other word."""
    assert pandas_result.columns == polars_result.columns
    for name in pandas_result.columns:
        a, b = pandas_result.schema[name], polars_result.schema[name]
        if a.is_temporal() or b.is_temporal():
            assert a == b, f"{name}: {a} on pandas, {b} on Polars"
        assert pandas_result[name].to_list() == polars_result[name].to_list(), name


# ---------------------------------------------------------------- the mend itself
@pytest.mark.parametrize("zone", ZONES)
def test_pandas_zone_names_are_read_as_dates(zone):
    frame = nw.from_native(pd.DataFrame({"t": zoned(zone, ["2024-01-01"])}), eager_only=True)
    assert frame.schema["t"] == nw.Datetime("us", zone)
    assert make_table(pd.DataFrame({"t": zoned(zone, ["2024-01-01"])}))._kind("t") == "date"


def test_mend_is_kept_only_while_narwhals_needs_it():
    from narwhals._pandas_like import utils

    from simplydata import _narwhals_mend

    assert _narwhals_mend._reads_every_zone(utils.PATTERN_PD_DATETIME)
    assert _narwhals_mend.mend_pandas_time_zones() is False  # reads every name already: nothing changed again
    for written in ("datetime64[ns]", "datetime64[us, UTC]", "datetime64[ms, Europe/Oslo]",
                    "datetime64[ns, UTC+01:00]", "datetime64[ns, pytz.FixedOffset(60)]"):
        assert utils.PATTERN_PD_DATETIME.match(written), written


# ---------------------------------------------------------------- hand-written values
@pytest.mark.parametrize(("zone", "local", "utc"), [
    ("America/New_York", "1959-07-01 00:00", "1959-07-01 04:00"),        # summer time (EDT, -4)
    ("America/New_York", "2024-01-15 12:30", "2024-01-15 17:30"),        # winter time (EST, -5)
    ("America/New_York", "2024-07-01 23:45", "2024-07-02 03:45"),        # the next day on the UTC clock
    ("America/Port-au-Prince", "2024-01-15 12:30", "2024-01-15 17:30"),  # winter time (-5)
    ("Etc/GMT+5", "2024-07-01 23:45", "2024-07-02 04:45"),               # always -5 (the sign is reversed in Etc/)
    ("Europe/Oslo", "2024-07-01 23:45", "2024-07-01 21:45"),             # summer time (CEST, +2)
    ("Europe/Oslo", "2024-01-15 12:30", "2024-01-15 11:30"),             # winter time (CET, +1)
])
def test_recorded_in_a_zone_to_utc_by_hand(engine, zone, local, utc, capsys):
    t = build({"t": pd.to_datetime([local]).as_unit("us")}, engine)
    t.change_time_zone_in("t", to="UTC", recorded_in=zone)
    got = as_polars(t)
    assert got.schema["t"] == pl.Datetime("us", "UTC")
    assert got["t"].dt.replace_time_zone(None).to_list() == [dt.datetime.fromisoformat(utc)]
    # and back: the same moment on the zone's clock, with the zone written in the column
    t.change_time_zone_in("t", to=zone)
    back = as_polars(t)
    assert back.schema["t"] == pl.Datetime("us", zone)
    assert back["t"].dt.replace_time_zone(None).to_list() == [dt.datetime.fromisoformat(local)]


def test_utc_to_new_york_by_hand(engine, capsys):
    t = build({"t": pd.to_datetime(["1959-07-01 04:00", "2024-01-15 17:30"]).as_unit("us")}, engine)
    t.change_time_zone_in("t", to="America/New_York", recorded_in="UTC")
    got = as_polars(t)["t"]
    assert [v.isoformat() for v in got.to_list()] == ["1959-07-01T00:00:00-04:00", "2024-01-15T12:30:00-05:00"]


def test_parts_of_a_new_york_date_by_hand(engine, capsys):
    t = build({"t": zoned("America/New_York", ["2024-07-01 23:45", "2024-12-31 23:00"])}, engine)
    t.add_column_with_part_of_date("day", from_column="t", part="day")
    t.add_column_with_part_of_date("hour", from_column="t", part="hour")
    t.add_column_with_part_of_date("year", from_column="t", part="year")
    got = as_polars(t)
    assert got["day"].to_list() == [1, 31] and got["hour"].to_list() == [23, 23]
    assert got["year"].to_list() == [2024, 2024]  # on the UTC clock the second would already be 2025


def test_hours_between_across_the_spring_change_by_hand(engine, capsys):
    # New York moved its clocks on 10 March 2024 at 02:00: noon to noon is 23 hours, so no whole day
    start = zoned("America/New_York", ["2024-03-09 12:00"])
    t = build({"start": start, "end": zoned("America/New_York", ["2024-03-10 12:00"])}, engine)
    t.add_column("hours", by_subtracting=["end", "start"], counted_in="hours")
    t.add_column("days", by_subtracting=["end", "start"])
    got = as_polars(t)
    assert got["hours"].to_list() == [23] and got["days"].to_list() == [0]


def test_every_month_uses_the_columns_own_clock_by_hand(engine, capsys):
    # 1 July 00:00 in Oslo is 30 June 22:00 UTC: it is counted in July, as on the Oslo clock
    t = build({"t": zoned("Europe/Oslo", ["2024-07-01 00:00", "2024-06-30 23:00", "2024-07-15 12:00"])}, engine)
    got = as_polars(t.count_rows(for_each_group_in="t", every="month"))
    months = [v.isoformat() for v in got["t"].to_list()]
    assert months == ["2024-06-01T00:00:00+02:00", "2024-07-01T00:00:00+02:00"]
    assert got[got.columns[-1]].to_list() == [1, 2]


def test_keep_rows_after_a_day_on_the_columns_clock_by_hand(engine, capsys):
    # "after 1 July" starts at midnight on 2 July in New York (04:00 UTC)
    t = build({"t": zoned("America/New_York", ["2024-07-01 23:45", "2024-07-02 00:30"])}, engine)
    t.keep_rows_where("t", is_after="2024-07-01")
    assert [v.isoformat() for v in as_polars(t)["t"].to_list()] == ["2024-07-02T00:30:00-04:00"]
    t.undo()
    t.keep_rows_where("t < '2024-07-02 00:00'")
    assert [v.isoformat() for v in as_polars(t)["t"].to_list()] == ["2024-07-01T23:45:00-04:00"]


def test_a_time_that_never_happens_is_refused_in_a_condition(engine):
    t = build({"t": zoned("America/New_York", ["2024-03-10 01:00"])}, engine)
    with pytest.raises(SimplydataError, match="never happens or happens twice"):
        t.keep_rows_where("t", is_after="2024-03-10 02:30")


def test_round_dates_counts_only_changed_filled_cells(engine, capsys):
    t = build({"t": zoned("America/New_York", ["2024-01-15 12:30", None, "2024-01-01 00:00"])}, engine)
    capsys.readouterr()
    t.round_dates_in("t", down_to="month")
    assert "1 of 3 rows changed" in capsys.readouterr().out


# ---------------------------------------------------------------- every date word: pandas = Polars, for every zone
PARTS = ["year", "quarter", "month", "month name", "week", "day", "weekday", "weekday name", "day of year", "hour",
         "minute", "date", "time", "second", "is weekend", "days in month", "is month end", "is leap year",
         "year and month"]


def other_table(t, zone):
    data = pd.DataFrame({"t": zoned(zone, ["1959-06-30 22:00", "2024-01-15 00:00", "2024-07-01 00:00"]),
                         "w": [10.0, 20, 30]})
    return data if t._engine == "pandas" else pl.from_pandas(data)


WORDS = {
    **{f"part {p}": (lambda t, z, p=p: t.add_column_with_part_of_date("p", from_column="t", part=p)) for p in PARTS},
    "turn_into_text": lambda t, z: t.turn_into_text("t"),
    "turn_into_text written_like": lambda t, z: t.turn_into_text("t", written_like="2026-03-15 14:30"),
    "turn_into_dates": lambda t, z: t.turn_into_dates("t"),
    "days between": lambda t, z: t.add_column("d", by_subtracting=["u", "t"]),
    "hours between": lambda t, z: t.add_column("d", by_subtracting=["u", "t"], counted_in="hours"),
    "plus 1 month": lambda t, z: t.add_column("d", from_column="t", plus="1 month"),
    "plus 30 days": lambda t, z: t.add_column("d", from_column="t", plus="30 days"),
    "minus 12 hours": lambda t, z: t.add_column("d", from_column="t", minus="12 hours"),
    "round down month": lambda t, z: t.round_dates_in("t", down_to="month"),
    "round down week": lambda t, z: t.round_dates_in("t", down_to="week"),
    "round up day": lambda t, z: t.round_dates_in("t", up_to="day"),
    "round to hour": lambda t, z: t.round_dates_in("t", to_the="hour"),
    "to UTC": lambda t, z: t.change_time_zone_in("t", to="UTC"),
    "UTC and back": lambda t, z: t.change_time_zone_in("t", to="UTC").change_time_zone_in("t", to=z),
    "recorded_in to UTC": lambda t, z: t.change_time_zone_in("naive", to="UTC", recorded_in=z),
    "recorded_in UTC to zone": lambda t, z: t.change_time_zone_in("naive", to=z, recorded_in="UTC"),
    "recorded_in only": lambda t, z: t.change_time_zone_in("naive", recorded_in=z),
    "keep is_after": lambda t, z: t.keep_rows_where("t", is_after="2024-01-01"),
    "keep is_before": lambda t, z: t.keep_rows_where("t", is_before="2024-03-01 12:00"),
    "keep is_between": lambda t, z: t.keep_rows_where("t", is_between=["2024-01-01", "2024-07-01"]),
    "keep written": lambda t, z: t.keep_rows_where("t > '2024-01-01'"),
    "sort_by": lambda t, z: t.sort_by("t", biggest_first=True),
    "join exact": lambda t, z: t.join_with(other_table(t, z), using="t"),
    "join nearest before": lambda t, z: t.remove_rows_with_empty_cells_in("t").join_with(
        other_table(t, z), using="t", match="nearest before", within="2 days"),
    "join nearest": lambda t, z: t.remove_rows_with_empty_cells_in("t").join_with(
        other_table(t, z), using="t", match="nearest"),
    "average every month": lambda t, z: t.find_average_of("v", for_each_group_in="t", every="month"),
    "total every year": lambda t, z: t.find_total_of("v", for_each_group_in="t", every="year"),
    "biggest every day": lambda t, z: t.find_biggest_of("v", for_each_group_in="t", every="day"),
    "smallest every week": lambda t, z: t.find_smallest_of("v", for_each_group_in="t", every="week"),
    "median every quarter": lambda t, z: t.find_median_of("v", for_each_group_in="t", every="quarter"),
    "summary every month": lambda t, z: t.find_summary_of("v", for_each_group_in="t", every="month"),
    "count every month": lambda t, z: t.count_rows(for_each_group_in="t", every="month"),
    "count across": lambda t, z: t.count_rows(for_each_group_in="g", across="t"),
    "count across every year": lambda t, z: t.count_rows(for_each_group_in="t", across="g", every="year"),
    "add_missing_dates month": lambda t, z: t.keep_rows_where("t", is_after="2000-01-01").round_dates_in(
        "t", down_to="month").add_missing_dates("t", every="month"),
    "add_missing_dates day": lambda t, z: t.keep_rows_where("t", is_after="2024-06-28").round_dates_in(
        "t", down_to="day").add_missing_dates("t", every="day", for_each_group_in="g"),
}


@pytest.mark.parametrize("zone", ZONES)
@pytest.mark.parametrize("word", list(WORDS))
def test_every_date_word_is_the_same_on_both_engines(zone, word, capsys):
    pandas_result, polars_result = both(zone, lambda t: WORDS[word](t, zone), capsys)
    assert_same(pandas_result, polars_result)


def test_oslo_before_1970_is_the_same_moment_on_both_engines(capsys):
    """Oslo in 1959: the moment is the one the pandas column holds, on both engines."""
    data = pd.DataFrame({"t": zoned("Europe/Oslo", ["1959-07-01 00:00", "1965-01-15 12:00"])})
    expected = pl.from_pandas(data["t"].dt.tz_convert("UTC")).to_list()
    for engine in ENGINES:
        t = build(data, engine)
        assert as_polars(t).schema["t"] == pl.Datetime("us", "Europe/Oslo")
        t.change_time_zone_in("t", to="UTC")
        assert as_polars(t)["t"].to_list() == expected, engine


@pytest.mark.parametrize("zone", ZONES)
def test_column_kind_and_description_are_the_same(zone, capsys):
    data = sample(zone)
    for engine in ENGINES:
        assert build(data, engine)._kind("t") == "date"
    outputs = []
    for engine in ENGINES:
        build(data, engine).describe_columns()
        outputs.append(capsys.readouterr().out)
    assert outputs[0] == outputs[1]
    assert "other" not in outputs[0]


@pytest.mark.parametrize("zone", ZONES)
@pytest.mark.parametrize("kind", ["parquet", "json"])
def test_saved_and_read_back_keeps_the_zone(zone, kind, tmp_path, capsys):
    results = []
    for engine in ENGINES:
        path = tmp_path / f"{engine}.{kind}"
        build(sample(zone), engine).save(str(path))
        results.append(as_polars(sdata.table(str(path))))
    assert_same(*results)
    if kind == "parquet":
        assert results[0].schema["t"] == pl.Datetime("us", zone)


# ---------------------------------------------------------------- files without a place for the zone name
@pytest.mark.parametrize("zone", ZONES)
@pytest.mark.parametrize("kind", ["csv", "tsv", "csv.gz", "tsv.gz"])
def test_text_files_keep_the_moments_on_both_engines(zone, kind, tmp_path, capsys):
    data = sample(zone)
    results, files = [], []
    for engine in ENGINES:
        path = tmp_path / f"{engine}.{kind}"
        build(data, engine).save(str(path))
        assert f"the zone name {zone} is not stored" in capsys.readouterr().out
        results.append(as_polars(sdata.table(str(path))).select("t", "u"))
        assert 'Read "t", "u" in' in capsys.readouterr().out
        if not kind.endswith(".gz"):
            files.append(path.read_text(encoding="utf-8").replace("\t", ","))
    assert_same(*results)
    for got in results:  # the same moments as the table saved, now on the UTC clock
        assert got.schema["t"] == pl.Datetime("us", "UTC")
        expected = pl.from_pandas(data["t"].dt.tz_convert("UTC")).to_list()
        assert got["t"].to_list() == expected
    if files:  # one text on both engines (the zone-free "naive" column aside)
        assert [line.split(",")[:2] for line in files[0].splitlines()] == \
               [line.split(",")[:2] for line in files[1].splitlines()]


def test_csv_text_and_moments_by_hand(engine, tmp_path, capsys):
    t = build({"t": zoned("America/New_York", ["1959-07-01 00:00", "2024-01-15 12:30", None]), "v": [1, 2, 3]},
              engine)
    path = tmp_path / "times.csv"
    t.save(str(path))
    assert path.read_text(encoding="utf-8").splitlines() == ["t,v", "1959-07-01 00:00:00-04:00,1",
                                                             "2024-01-15 12:30:00-05:00,2", ",3"]
    back = sdata.table(str(path), fast=engine == "polars")
    got = as_polars(back)["t"].to_list()
    assert [v.isoformat() if v else None for v in got] == ["1959-07-01T04:00:00+00:00", "2024-01-15T17:30:00+00:00",
                                                           None]
    back.change_time_zone_in("t", to="America/New_York")
    assert as_polars(back)["t"].to_list()[0].isoformat() == "1959-07-01T00:00:00-04:00"


def test_text_that_only_looks_like_times_stays_text(engine, tmp_path, capsys):
    path = tmp_path / "mixed.csv"
    path.write_text("a,b,c\n2024-01-15 12:30:00-05:00,2024-01-15 12:30:00,2024-01-15 12:30:00+01:00\n"
                    "not a time,2024-01-16 08:00:00,2024-01-16 08:00:00Z\n", encoding="utf-8")
    got = as_polars(sdata.table(str(path), fast=engine == "polars"))
    assert got.schema["a"] == pl.String and got.schema["b"] == pl.String
    assert got.schema["c"] == pl.Datetime("us", "UTC")
    assert [v.isoformat() for v in got["c"].to_list()] == ["2024-01-15T11:30:00+00:00", "2024-01-16T08:00:00+00:00"]
    kept = as_polars(sdata.table(str(path), read_as_text=["c"]))
    assert kept.schema["c"] == pl.String


@pytest.mark.parametrize("kind", ["xlsx", "dta"])
def test_excel_and_stata_get_the_clock_times_with_a_note(engine, kind, tmp_path, capsys):
    t = build({"t": zoned("America/New_York", ["2024-01-15 12:30", "2024-07-01 23:45", None]), "v": [1, 2, 3]},
              engine)
    path = tmp_path / f"times.{kind}"
    t.save(str(path))
    said = capsys.readouterr().out
    assert "has no time zones" in said and "on the America/New_York clock" in said
    assert 'table.change_time_zone_in("t", to="UTC")' in said
    got = as_polars(sdata.table(str(path)))["t"].to_list()
    assert got[:2] == [dt.datetime(2024, 1, 15, 12, 30), dt.datetime(2024, 7, 1, 23, 45)] and got[2] is None
    assert as_polars(t)["t"].dtype == pl.Datetime("us", "America/New_York")  # the table itself keeps its zone


def test_excel_sheet_gets_the_clock_times(engine, tmp_path, capsys):
    t = build({"t": zoned("Etc/GMT+5", ["2024-07-01 23:45"])}, engine)
    path = tmp_path / "book.xlsx"
    t.save(str(path), in_sheet="times")
    t.save(str(path), in_sheet="again")
    assert "on the Etc/GMT+5 clock" in capsys.readouterr().out
    got = as_polars(sdata.table(str(path), sheet="again"))["t"].to_list()
    assert got == [dt.datetime(2024, 7, 1, 23, 45)]
