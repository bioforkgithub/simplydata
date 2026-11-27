"""Tables finishing PR: one column said as "1 column", the same .csv file from both engines for times without a time
zone, and the sentences of spread_into_columns."""

import datetime as dt
import gzip

import pytest

import simplydata as sdata

pl = pytest.importorskip("polars")

TIMES = {
    "station": ["A", "B", "C", "D"],
    "whole_seconds": [dt.datetime(2024, 7, 1, 23, 45), dt.datetime(2024, 7, 2, 1, 0, 5), None,
                      dt.datetime(1969, 12, 31, 6)],
    "midnight": [dt.datetime(2024, 7, 1), dt.datetime(2024, 7, 2), dt.datetime(2024, 7, 3), None],
    "milliseconds": [dt.datetime(2024, 7, 1, 23, 45, 0, 500000), dt.datetime(2024, 7, 2), None,
                     dt.datetime(2024, 7, 2, 8, 0, 0, 120000)],
    "microseconds": [dt.datetime(2024, 7, 1, 23, 45, 0, 123456), dt.datetime(2024, 7, 2), None, None],
    "day": [dt.date(2024, 7, 1), dt.date(2024, 7, 2), None, dt.date(2024, 7, 4)],
    "level": [1.5, 2.0, None, 3.25],
}


# ---------------------------------------------------------------- one column, one row: no "1 columns"
def test_one_column_is_said_in_the_singular(capsys):
    table = sdata.table({"marks": [61]})
    assert repr(table).startswith("simplydata table: 1 row, 1 column\n")
    table.describe_columns()
    assert "The table has 1 row and 1 column." in capsys.readouterr().out
    table.check_if_same_as(sdata.table({"marks": [61]}))
    assert "The tables are the same: 1 row, 1 column, every cell equal." in capsys.readouterr().out
    table.show_differences_from(sdata.table({"marks": [61]}))
    assert "both tables have the same 1 row and 1 column," in capsys.readouterr().out
    two = sdata.table({"marks": [61, 70], "class": ["A", "B"]})
    assert repr(two).startswith("simplydata table: 2 rows, 2 columns\n")


def test_a_count_table_with_one_column_is_said_in_the_singular(capsys):
    fruit = sdata.get_example("fruit")
    fruit.keep_rows_where("fruit", is_equal_to="apple")
    fruit.find_total_of("count", for_each_group_in="day", across="fruit")
    assert "1 column of numbers" in capsys.readouterr().out


# ---------------------------------------------------------------- times without a time zone in a .csv file
@pytest.mark.parametrize("kind", ["csv", "tsv", "csv.gz", "tsv.gz"])
def test_both_engines_write_the_same_text_file(kind, tmp_path):
    """The same table saved on pandas and on Polars (fast=True) gives the same bytes, times without a zone included."""
    files = []
    for fast in (False, True):
        path = tmp_path / f"times_{fast}.{kind}"
        sdata.table(TIMES, fast=fast).save(str(path))
        files.append(gzip.decompress(path.read_bytes()) if kind.endswith(".gz") else path.read_bytes())
    assert files[0] == files[1]
    assert b"\r\n" not in files[0]  # one line end on every computer


def test_times_without_a_zone_are_written_as_pandas_writes_them(tmp_path):
    path = tmp_path / "times.csv"
    sdata.table(TIMES, fast=True).save(str(path))
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[1] == ("A,2024-07-01 23:45:00,2024-07-01,2024-07-01 23:45:00.500,2024-07-01 23:45:00.123456,"
                        "2024-07-01,1.5")
    assert lines[4] == "D,1969-12-31 06:00:00,,2024-07-02 08:00:00.120,,2024-07-04,3.25"
    back = sdata.table(str(path), fast=True, separator=",")
    back.turn_into_dates("whole_seconds")  # Polars' own text, 2024-07-01T23:45:00.000000, did not become a date
    assert back.get_cell_at(row=1, column="whole_seconds") == dt.datetime(2024, 7, 1, 23, 45)


def test_times_with_a_zone_and_without_one_in_one_csv_file(tmp_path, capsys):
    """A zone column still gets its UTC offset; the plain column next to it gets pandas' text, on both engines."""
    data = {"utc": [dt.datetime(2024, 7, 1, 12, tzinfo=dt.timezone.utc)], "local": [dt.datetime(2024, 7, 1, 14)]}
    texts = []
    for fast in (False, True):
        path = tmp_path / f"zone_{fast}.csv"
        sdata.table(data, fast=fast).save(str(path))
        texts.append(path.read_bytes())
    assert texts[0] == texts[1] == b"utc,local\n2024-07-01 12:00:00+00:00,2024-07-01 14:00:00\n"
    assert "UTC offset" in capsys.readouterr().out


# ---------------------------------------------------------------- spread_into_columns says what it did
def test_spread_with_show_names_the_columns_that_share_a_cell(capsys):
    fruit = sdata.get_example("fruit")
    fruit.keep_columns("day", "fruit", "count")
    fruit.spread_into_columns(names_from="fruit", values_from="count", show="total")
    out = capsys.readouterr().out
    assert ('Each new cell is the total of "count" over the rows with the same "fruit" and "day"; '
            "10 cells combine more than one row.") in out


def test_spread_with_several_columns_that_differ_has_a_note(capsys):
    """Rain and wind differ from city to city, so no row merges: a note says why the new columns are mostly empty."""
    weather = sdata.get_example("weather")
    weather.spread_into_columns(names_from="city", values_from="temperature")
    out = capsys.readouterr().out
    assert "Note: 72 cells of the new columns are empty because the rows did not merge" in out
    assert 'table.undo(), then table.keep_columns(...)' in out


def test_spread_with_a_pair_that_never_appears_has_no_note(capsys):
    """A child without a Maths mark leaves one empty cell; the rows did merge, so no note."""
    marks = sdata.get_example("marks")
    marks.keep_columns("name", "subject", "marks")
    marks.keep_rows_by_position(2, to=54)
    capsys.readouterr()
    marks.spread_into_columns(names_from="subject", values_from="marks")
    assert "Note" not in capsys.readouterr().out
    assert marks.count_rows() == 18


def test_spread_docstring_says_to_keep_the_needed_columns_first():
    from simplydata.table import Table

    doc = " ".join(Table.spread_into_columns.__doc__.split())
    assert 'table.keep_columns("month", "city", "temperature") before spreading gives one row for each month' in doc
    assert 'The values of rows with an empty cell in names_from go into a new column called "(empty)"' in doc
