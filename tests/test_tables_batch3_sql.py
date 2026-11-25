"""Tables phase, batch 3 (approved by Manish 2026-11-25): SQL through DuckDB (table.run_sql, sdata.run_sql), the
database files (table_name=, in_table=) and the file types by name, checked against DuckDB, sqlite3 and pandas
themselves. DuckDB is an optional extra: its tests skip without it.

Privacy: no query and no database file can reach the network. DuckDB is opened with extensions neither installed
nor loaded on their own (so httpfs never comes in), the settings locked, one SELECT only, and a web or cloud address
is refused before DuckDB sees it. The tests below prove each of these."""

import gzip
import sqlite3
import zipfile
from importlib.resources import files

import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.data import DATE_COLUMNS
from simplydata.table import table as make_table

pl = pytest.importorskip("polars")
ENGINES = ["pandas", "polars"]
QUERY = "SELECT station, avg(nitrate) AS nitrate, count(*) AS days FROM data GROUP BY station ORDER BY station"


def raw(name):
    with (files("simplydata.data") / f"{name}.csv").open("r", encoding="utf-8") as fh:
        return pd.read_csv(fh, parse_dates=DATE_COLUMNS.get(name, False))


def build(data, engine):
    data = pd.DataFrame(data)
    return make_table(data, fast=True) if engine == "polars" else make_table(data)


def plain(t):
    native = t._done()
    if not isinstance(native, pd.DataFrame):
        native = native.to_pandas()
    return native.reset_index(drop=True)


def same(got, expected):
    got, expected = got.reset_index(drop=True), expected.reset_index(drop=True)
    assert list(got.columns) == list(expected.columns)
    pd.testing.assert_frame_equal(got.astype(object).where(got.notna(), None),
                                  expected.astype(object).where(expected.notna(), None), check_dtype=False)


@pytest.fixture(params=ENGINES)
def engine(request):
    return request.param


@pytest.fixture
def duckdb():
    return pytest.importorskip("duckdb")


# ---------------------------------------------------------------- P37 table.run_sql
def test_table_run_sql_matches_duckdb(engine, duckdb, capsys):
    river = build(raw("river"), engine)
    answer = river.run_sql(QUERY)
    con = duckdb.connect()
    con.register("data", raw("river"))
    same(plain(answer), con.sql(QUERY).df())
    assert type(answer._done()).__module__.split(".")[0] == ("polars" if engine == "polars" else "pandas")
    out = capsys.readouterr().out
    assert "Ran the query with DuckDB on this table (called data in the query): 2 rows, 3 columns." in out
    assert len(river) == len(raw("river"))  # the table does not change
    assert not river._history


def test_table_run_sql_without_duckdb_uses_polars_sql(engine, monkeypatch, capsys):
    import importlib.util

    real = importlib.util.find_spec
    monkeypatch.setattr(importlib.util, "find_spec", lambda name, *a: None if name == "duckdb" else real(name, *a))
    answer = build(raw("river"), engine).run_sql(QUERY)
    expected = pl.SQLContext(data=pl.from_pandas(raw("river"))).execute(QUERY, eager=True).to_pandas()
    same(plain(answer), expected)
    assert "Polars SQL (DuckDB is not installed)" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="only reads"):
        build(raw("river"), engine).run_sql("DROP TABLE data")
    with pytest.raises(SimplydataError, match="web or cloud address"):
        build(raw("river"), engine).run_sql("SELECT * FROM read_csv('https://example.invalid/x.csv')")


def test_run_sql_needs_a_query_and_explains_duckdb_errors(duckdb):
    river = sdata.get_example("river")
    with pytest.raises(SimplydataError, match="needs the query as text"):
        river.run_sql()
    with pytest.raises(SimplydataError, match="DuckDB could not run the query"):
        river.run_sql("SELECT no_such_column FROM data")
    with pytest.raises(SimplydataError, match="one query at a time"):
        river.run_sql("SELECT 1 FROM data; SELECT 2 FROM data")


def test_sdata_run_sql_on_files(duckdb, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    raw("river").to_csv("river_a.csv", index=False)
    raw("river").to_csv("river_b.csv", index=False)
    query = "SELECT station, max(level) AS level FROM 'river_*.csv' GROUP BY station ORDER BY station"
    answer = sdata.run_sql(query)
    same(plain(answer), duckdb.sql(query).df())
    assert "Ran the query with DuckDB: 2 rows, 2 columns." in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="DuckDB could not run the query"):
        sdata.run_sql("SELECT * FROM 'no_such_file.csv'")


def test_missing_duckdb_says_how_to_install_it(monkeypatch):
    import builtins

    real = builtins.__import__

    def without_duckdb(name, *args, **kwargs):
        if name == "duckdb":
            raise ImportError("no duckdb")
        return real(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_duckdb)
    with pytest.raises(SimplydataError, match=r'pip install "simplydata\[sql\]"'):
        sdata.run_sql("SELECT 1")


# ---------------------------------------------------------------- privacy: nothing reaches the network
@pytest.mark.parametrize("address", ["https://example.invalid/river.csv", "http://example.invalid/r.parquet",
                                     "s3://bucket/river.parquet", "gs://bucket/x.csv", "HTTPS://EXAMPLE.INVALID/x",
                                     "hf://datasets/x/y.csv", "az://box/x.csv"])
def test_web_and_cloud_addresses_are_refused_before_duckdb_sees_them(address, duckdb, monkeypatch):
    from simplydata import _sql

    seen = []
    monkeypatch.setattr(_sql, "run", lambda *a, **k: seen.append(a))
    with pytest.raises(SimplydataError, match="never reads data from the internet"):
        sdata.run_sql(f"SELECT * FROM '{address}'")
    with pytest.raises(SimplydataError, match="never reads data from the internet"):
        sdata.get_example("river").run_sql(f"SELECT * FROM data, read_csv('{address}')")
    assert not seen


@pytest.mark.parametrize("statement", ["INSTALL httpfs", "LOAD httpfs", "SET autoload_known_extensions = true",
                                       "ATTACH 'other.duckdb'", "COPY (SELECT 1) TO 'out.csv'",
                                       "CREATE TABLE t AS SELECT 1", "PRAGMA enable_profiling",
                                       "SELECT 1; INSTALL httpfs"])
def test_only_one_select_runs(statement, duckdb, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SimplydataError, match="only reads|one query at a time"):
        sdata.run_sql(statement)
    with pytest.raises(SimplydataError, match="only reads|one query at a time"):
        sdata.get_example("river").run_sql(statement)
    assert not list(tmp_path.iterdir())  # nothing was written


def test_the_duckdb_connection_cannot_reach_the_network_or_load_extensions(duckdb):
    from simplydata import _sql

    for files_too in (False, True):
        con = _sql.connect("the test", files=files_too)
        try:
            settings = dict(con.sql("SELECT name, value FROM duckdb_settings() WHERE name IN "
                                    "('autoinstall_known_extensions', 'autoload_known_extensions', "
                                    "'allow_community_extensions', 'enable_external_access', "
                                    "'lock_configuration')").fetchall())
            assert settings["autoinstall_known_extensions"] == "false"
            assert settings["autoload_known_extensions"] == "false"
            assert settings["allow_community_extensions"] == "false"
            assert settings["lock_configuration"] == "true"
            assert settings["enable_external_access"] == ("true" if files_too else "false")
            # even run straight on the connection (past simplydata's checks), a web address is not read: httpfs is
            # not loaded and cannot be loaded on its own, so DuckDB stops before any connection is made
            with pytest.raises(Exception, match="httpfs|disabled|Permission"):
                con.sql("SELECT * FROM read_csv('https://example.invalid/x.csv')").fetchall()
            with pytest.raises(Exception, match="lock|Cannot change"):
                con.execute("SET autoload_known_extensions = true")
            if files_too:  # without file access DuckDB cannot even list the extension folder
                loaded = {row[0] for row in con.sql("SELECT extension_name FROM duckdb_extensions() WHERE loaded")
                          .fetchall()}
                assert "httpfs" not in loaded
        finally:
            con.close()


def test_a_table_query_cannot_open_files(duckdb, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    raw("marks").to_csv("secret.csv", index=False)
    with pytest.raises(SimplydataError, match="DuckDB could not run the query"):
        sdata.get_example("river").run_sql("SELECT * FROM read_csv('secret.csv')")


# ---------------------------------------------------------------- P38 databases: table_name= and in_table=
def test_sqlite_in_table_and_table_name(engine, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    marks, river = build(raw("marks"), engine), build(raw("river"), engine)
    marks.save("results.sqlite", in_table="marks")
    river.save("results.sqlite", in_table="river")
    marks.save("results.sqlite", in_table="marks")  # replaces that table and keeps the other
    assert 'Replaced the table "marks" in results.sqlite; the other tables are kept.' in capsys.readouterr().out
    con = sqlite3.connect("results.sqlite")
    tables = sorted(row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'"))
    expected = pd.read_sql_query('SELECT * FROM "marks"', con)
    con.close()
    assert tables == ["marks", "river"]
    back = sdata.table("results.sqlite", table_name="marks")
    same(plain(back), expected)
    same(plain(back), raw("marks"))
    with pytest.raises(SimplydataError, match='holds 2 tables: "marks", "river"'):
        sdata.table("results.sqlite")
    with pytest.raises(SimplydataError, match='Did you mean table_name="river"'):
        sdata.table("results.sqlite", table_name="rivers")


def test_database_options_are_checked(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    marks = sdata.get_example("marks")
    with pytest.raises(SimplydataError, match="needs|holds tables by name"):
        marks.save("results.sqlite")
    with pytest.raises(SimplydataError, match="one table of a database file"):
        marks.save("results.csv", in_table="marks")
    with pytest.raises(SimplydataError, match="give one of them"):
        marks.save("results.sqlite", in_table="marks", in_sheet="marks")
    with pytest.raises(SimplydataError, match="in quotes"):
        marks.save("results.sqlite", in_table="")
    marks.save("results.csv")
    with pytest.raises(SimplydataError, match="table_name= is for SQLite, DuckDB files"):
        sdata.table("results.csv", table_name="marks")
    with pytest.raises(SimplydataError, match="in_table=\"river\""):
        marks.save("x.sqlite", if_exists="replace")
    marks.save("one.db", in_table="only")
    assert len(sdata.table("one.db")) == 54  # one table: no table_name= needed


def test_duckdb_files(engine, duckdb, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    build(raw("marks"), engine).save("results.duckdb", in_table="marks")
    build(raw("river"), engine).save("results.duckdb", in_table="river")
    con = duckdb.connect("results.duckdb", read_only=True)
    expected = con.table("river").df()
    con.close()
    back = sdata.table("results.duckdb", table_name="river")
    same(plain(back), expected)
    assert len(sdata.table("results.duckdb", table_name="marks")) == 54


# ---------------------------------------------------------------- P38 file types by name
@pytest.mark.parametrize("name, reader", [
    ("marks.csv.gz", lambda p: pd.read_csv(p)),
    ("marks.tsv.gz", lambda p: pd.read_csv(p, sep="\t")),
    ("marks.feather", lambda p: pd.read_feather(p)),
    ("marks.jsonl", lambda p: pd.read_json(p, lines=True)),
])
def test_save_and_read_more_file_types(name, reader, engine, tmp_path, monkeypatch):
    pytest.importorskip("pyarrow")
    monkeypatch.chdir(tmp_path)
    build(raw("marks"), engine).save(name)
    same(reader(name), raw("marks"))
    same(plain(sdata.table(name)), reader(name))


def test_compressed_files_are_really_compressed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    sdata.get_example("marks").save("marks.csv.gz")
    with gzip.open("marks.csv.gz", "rt", encoding="utf-8") as fh:
        assert fh.readline().strip() == ",".join(raw("marks").columns)


def test_zip_with_one_csv(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    raw("marks").to_csv("marks.csv", index=False, sep=";")
    with zipfile.ZipFile("marks.zip", "w") as z:
        z.write("marks.csv")
    same(plain(sdata.table("marks.zip")), pd.read_csv("marks.zip", sep=";"))
    assert 'with ";" between the columns (guessed)' in capsys.readouterr().out
    with zipfile.ZipFile("two.zip", "w") as z:
        z.write("marks.csv")
        z.write("marks.csv", arcname="again.csv")
    with pytest.raises(SimplydataError, match="holds one CSV or TSV file"):
        sdata.table("two.zip")


def test_save_stata_and_html(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    marks = sdata.get_example("marks")
    marks.save("marks.dta")
    assert "class -> _class" in capsys.readouterr().out  # Stata's rule on names, said plainly
    expected = raw("marks").rename(columns={"class": "_class"})
    same(pd.read_stata("marks.dta"), expected)
    same(plain(sdata.table("marks.dta")), expected)
    marks.save("marks.html")
    same(_html_rows("marks.html"), raw("marks").astype(str))


def _html_rows(path):
    """The cells of the saved web page table, read with Python's own HTML parser (no network)."""
    from html.parser import HTMLParser

    class Cells(HTMLParser):
        def __init__(self):
            super().__init__()
            self.rows, self.cell = [], None

        def handle_starttag(self, tag, attrs):
            if tag == "tr":
                self.rows.append([])
            if tag in ("td", "th"):
                self.cell = ""

        def handle_data(self, data):
            if self.cell is not None:
                self.cell += data

        def handle_endtag(self, tag):
            if tag in ("td", "th"):
                self.rows[-1].append(self.cell.strip())
                self.cell = None

    parser = Cells()
    parser.feed(open(path, encoding="utf-8").read())
    header, *body = parser.rows
    return pd.DataFrame(body, columns=header)


def test_read_xml_and_sas_by_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    raw("marks").to_xml("marks.xml", index=False, parser="etree")
    same(plain(sdata.table("marks.xml")), pd.read_xml("marks.xml", parser="etree"))
    import simplydata._data as data

    assert data._READERS[".sas7bdat"] == "sas" and data._file_suffix("x.CSV.GZ") == ".csv.gz"


def test_a_database_is_not_read_from_the_web():
    import io

    from simplydata._data import _read_more

    with pytest.raises(SimplydataError, match="from this computer only"):
        _read_more(io.BytesIO(b"SQLite format 3"), "sqlite", "lab.sqlite", {})
