"""SQL through DuckDB, kept on this computer (tables phase, batch 3; approved by Manish 2026-11-25).

table.run_sql, sdata.run_sql and the .duckdb files of sdata.table / table.save open DuckDB here, always the same way:

  * no extension is installed or loaded on its own (DuckDB's autoinstall_known_extensions and
    autoload_known_extensions are off, community extensions are not allowed), so httpfs, the extension that reads
    web and cloud addresses, never comes in; and the settings are locked, so a query cannot switch them back on;
  * a query or file name with a web or cloud address in it (http://, https://, s3://, gs:// ...) is refused before
    DuckDB sees it;
  * a query may only read: one SELECT (or WITH ... SELECT). INSTALL, LOAD, ATTACH, COPY, SET, CREATE ... are
    refused, so a query never writes a file or changes a setting;
  * a query on a table (table.run_sql) cannot open files at all (enable_external_access is off).

DuckDB is an optional extra: pip install "simplydata[sql]". Nothing here reaches the network (tests/test_privacy.py,
tests/test_tables_batch3_sql.py).
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ._errors import SimplydataError, friendly

if TYPE_CHECKING:
    from .table import Table

INSTALL_SQL = 'pip install "simplydata[sql]"   (or: conda install -c conda-forge python-duckdb)'
# web and cloud addresses DuckDB (with httpfs and friends) or Polars could otherwise read
_REMOTE = re.compile(r"\b(?:https?|s3a?|s3n|gcs|gs|r2|az|azure|abfss?|hf|ftp|sftp|ssh)://", re.IGNORECASE)
# a query only reads: the DuckDB statement types that do
_READING_STATEMENTS = ("SELECT",)


def refuse_remote(text, what="The query") -> None:
    """Stop at once if text names a web or cloud address: simplydata never fetches data for a query."""
    found = _REMOTE.search(str(text))
    if found:
        raise SimplydataError(
            f'{what} names a web or cloud address ("{found.group(0)}..."). simplydata never reads data from the '
            "internet in SQL, so that your data and your queries stay on this computer.\n"
            "Download the file yourself, then use its name on this computer, for example "
            "sdata.run_sql(\"SELECT * FROM 'river.parquet'\")."
        )


def need_duckdb(what: str):
    """The duckdb module, or a plain error that says how to install it."""
    try:
        import duckdb
    except ImportError:
        raise SimplydataError(f"{what} needs DuckDB, an optional extra.\nInstall it with:  {INSTALL_SQL}") from None
    return duckdb


def connect(what: str, database=":memory:", read_only=False, files=False):
    """A DuckDB connection that cannot reach the network or load extensions; files=False: no files either.

    DuckDB's own settings (duckdb.org/docs, "Configuration"): autoinstall_known_extensions and
    autoload_known_extensions off, allow_community_extensions off, enable_external_access off unless files are
    wanted, then lock_configuration on."""
    duckdb = need_duckdb(what)
    config = {"autoinstall_known_extensions": False, "autoload_known_extensions": False,
              "allow_community_extensions": False}
    if not files:
        config["enable_external_access"] = False
    con = duckdb.connect(database, read_only=read_only, config=config)
    con.execute("SET lock_configuration = true")
    return con


def check_query(con, query: str, example: str) -> None:
    """One statement, and one that only reads (SELECT or WITH ... SELECT), with no web address in it."""
    if not isinstance(query, str) or not query.strip():
        raise SimplydataError(f"run_sql() needs the query as text in quotes.\nFor example:  {example}")
    refuse_remote(query)
    try:
        statements = con.extract_statements(query)
    except Exception as problem:  # noqa: BLE001 - DuckDB's own words, given back plainly
        raise SimplydataError(f"DuckDB could not read the query: {_first_line(problem)}\nFor example:  {example}") \
            from None
    if len(statements) != 1:
        raise SimplydataError(f"run_sql() runs one query at a time, but this text has {len(statements)} (separated "
                              f"by ;). Run them one by one.\nFor example:  {example}")
    kind = str(statements[0].type).rsplit(".", 1)[-1]
    if kind not in _READING_STATEMENTS:
        raise SimplydataError(
            f"run_sql() only reads: the query must be a SELECT (or WITH ... SELECT), and this one is {kind}. "
            "simplydata never lets a query install or load extensions, change settings, attach databases or write "
            f"files.\nTo save the result, use table.save(...) on it.\nFor example:  {example}"
        )


def _first_line(problem) -> str:
    return (str(problem).strip().splitlines() or [""])[0]


def run(con, query: str, example: str, polars: bool):
    """The query's answer as a pandas table (or a Polars table); a DuckDB refusal said in one plain line."""
    try:
        answer = con.sql(query)
        if answer is None:
            raise SimplydataError("The query gave no table back. A query that reads starts with SELECT.")
        return answer.pl() if polars else answer.df()
    except SimplydataError:
        raise
    except Exception as problem:  # noqa: BLE001 - DuckDB's own message, given back plainly
        raise SimplydataError(f"DuckDB could not run the query: {_first_line(problem)}\nFor example:  {example}") \
            from None


def quoted(name: str) -> str:
    """An SQL name in double quotes, a " inside written twice (the SQL standard)."""
    return '"' + str(name).replace('"', '""') + '"'


@friendly(others={"sql": "query"})
def run_sql(query=None) -> Table:
    """Run an SQL query on files, without reading them first, and give back its answer as a table.

    sdata.run_sql("SELECT station, avg(nitrate) AS nitrate FROM 'river.csv' GROUP BY station")
    A file name goes in single quotes after FROM, and a pattern reads many files at once:
    FROM 'river/*.parquet'. CSV, Parquet and JSON files work, on this computer only. Only the
    rows and columns the query asks for are read, so big files are quick. The query runs in DuckDB
    (pip install "simplydata[sql]"; duckdb.sql(query).df()). It may only read (one SELECT): it can
    never read a web address, install or load an extension, or write a file, so the data stay on
    this computer. A table you already have: table.run_sql("SELECT ... FROM data").
    """
    from .table import Table

    example = "sdata.run_sql(\"SELECT station, avg(nitrate) AS nitrate FROM 'river.csv' GROUP BY station\")"
    con = connect("sdata.run_sql()", files=True)
    try:
        check_query(con, query, example)
        answer = run(con, query, example, polars=False)  # DuckDB con.sql(query).df()
    finally:
        con.close()
    result = Table(answer)
    rows, cols = answer.shape
    print(f"Ran the query with DuckDB: {rows} row{'s' if rows != 1 else ''}, {cols} column{'s' if cols != 1 else ''}.")
    return result
