"""Reading data and turning what the user gives us into a pandas table.

Charts always draw from pandas. Polars tables and big files are read with Polars
(fast mode) and handed over as pandas.

Files can be read one at a time, several at once (a folder, or a pattern such as
"data/*.csv", stacked with a "file" column), or from a web address.
"""

from __future__ import annotations

import codecs
import csv
import glob
import io
import keyword
import os
import re
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from ._errors import SimplydataError, column_error, suggest

BIG_FILE_BYTES = 100 * 1024 * 1024  # 100 MB: above this, fast mode is used automatically
WEB_TIMEOUT_SECONDS = 30

_READERS = {
    ".csv": "csv",
    ".txt": "csv",
    ".tsv": "tsv",
    ".xlsx": "excel",
    ".xlsm": "excel",
    ".xls": "excel",
    ".parquet": "parquet",
    ".json": "json",
    ".docx": "word",   # optional extra: python-docx
    ".sav": "spss",    # optional extra: pyreadstat
    ".zsav": "spss",
    ".dta": "stata",
    # tables phase, batch 3 (P38): more file types by name, each read by pandas itself
    ".csv.gz": "csv",   # pandas read_csv(compression="gzip")
    ".tsv.gz": "tsv",
    ".txt.gz": "csv",
    ".zip": "csv",      # one CSV file inside: pandas read_csv(compression="zip")
    ".feather": "feather",  # pandas read_feather (pyarrow)
    ".arrow": "feather",
    ".jsonl": "jsonl",  # pandas read_json(lines=True)
    ".ndjson": "jsonl",
    ".xml": "xml",      # pandas read_xml(parser="etree"), Python's own XML reader
    ".sas7bdat": "sas",  # pandas read_sas
    ".sqlite": "sqlite",  # Python's sqlite3 and pandas read_sql_query
    ".sqlite3": "sqlite",
    ".db": "sqlite",
    ".duckdb": "duckdb",  # DuckDB (simplydata[sql]), opened read-only, with no extensions and no files
}
# file endings of two parts: the compressed text files
_TWO_PART_ENDINGS = (".csv.gz", ".tsv.gz", ".txt.gz")

_KIND_NAMES = {
    "csv": "CSV and text", "tsv": "TSV", "excel": "Excel", "parquet": "Parquet", "json": "JSON",
    "word": "Word", "spss": "SPSS", "stata": "Stata",
    "feather": "Feather (Arrow)", "jsonl": "JSON lines", "xml": "XML", "sas": "SAS", "sqlite": "SQLite",
    "duckdb": "DuckDB",
}

# Which reading options make sense for which kind of file.
_OPTIONS_FOR = {
    "separator": ("csv", "tsv"),
    "encoding": ("csv", "tsv"),
    "decimal_mark": ("csv", "tsv", "excel", "word"),
    "thousands_mark": ("csv", "tsv", "excel", "word"),
    "empty_values": ("csv", "tsv", "excel", "word"),
    "skip_rows": ("csv", "tsv", "excel", "word"),
    "table_number": ("word",),
    "read_as_text": ("csv", "tsv", "excel", "word"),
    # tables phase, batch 2 (approved by Manish 2026-11-25)
    "columns": ("csv", "tsv", "excel", "parquet"),
    "column_names": ("csv", "tsv", "excel"),
    "skip_lines_starting_with": ("csv", "tsv"),
    "table_name": ("sqlite", "duckdb"),  # tables phase, batch 3 (P38)
}

READING_OPTIONS = tuple(_OPTIONS_FOR)

_FILES_HINT = "Install it with:  pip install simplydata[files]"


def _is_polars(obj) -> bool:
    return type(obj).__module__.split(".")[0] == "polars"


def _polars_to_pandas(obj) -> pd.DataFrame:
    if hasattr(obj, "collect"):  # LazyFrame
        obj = obj.collect()
    if hasattr(obj, "to_frame") and not hasattr(obj, "columns"):  # Series
        obj = obj.to_frame()
    return obj.to_pandas()


def _missing_file_error(path: Path) -> SimplydataError:
    lines = [f'File "{path}" not found.']
    folder = path.parent if str(path.parent) not in ("", ".") else Path(".")
    try:
        nearby = [p.name for p in folder.iterdir() if p.is_file()]
    except OSError:
        nearby = []
    guess = suggest(path.name, nearby, n=1)
    if guess:
        lines.append(f'Did you mean "{folder / guess[0]}"?')
    lines.append(f"simplydata is looking in: {Path(folder).resolve()}")
    return SimplydataError("\n".join(lines))


# ---------------------------------------------------------------- reading options
# read_as_text= also takes pandas' dtype={"sample": str} and Polars' schema_overrides={"sample": pl.String} when every
# type in it is a text type; these are the ways of writing "text" that are accepted
_TEXT_TYPES = ("str", "string", "text", "object", "utf8", "character")


def _is_text_type(value) -> bool:
    if value is str:
        return True
    name = getattr(value, "__name__", None) or str(value)
    return name.strip().lower().replace("pl.", "") in _TEXT_TYPES


def _read_as_text_names(value) -> list:
    """read_as_text= as a list of column names (one name, a list, or a {name: str} mapping from pandas or Polars)."""
    example = 'For example:  sdata.table("lab.csv", read_as_text=["sample_id"])'
    if isinstance(value, dict):
        not_text = [str(k) for k, v in value.items() if not _is_text_type(v)]
        if not_text:
            raise SimplydataError(
                "read_as_text= keeps columns as text, exactly as typed. Other kinds are set after reading: "
                "table.turn_into_numbers(...) or table.turn_into_dates(...).\n"
                f"Not text here: {', '.join(not_text)}.\n{example}"
            )
        value = list(value)
    if isinstance(value, str):
        value = [value]
    if (not isinstance(value, (list, tuple)) or not value
            or not all(isinstance(v, str) and v.strip() for v in value)):
        raise SimplydataError(
            "read_as_text= is a list of the column names to keep as text, so that 007 stays 007 and 3-12 "
            f"stays 3-12.\n{example}"
        )
    return list(dict.fromkeys(value))


def _names_option(option, value, example) -> list:
    """columns= / column_names=: one name or a list of names, each once."""
    if isinstance(value, str):
        value = [value]
    if (not isinstance(value, (list, tuple)) or not value
            or not all(isinstance(v, str) and v.strip() for v in value)):
        raise SimplydataError(f"{option}= is a list of column names in quotes.\nFor example:  {example}")
    twice = sorted({v for v in value if list(value).count(v) > 1})
    if twice:
        raise SimplydataError(f"{option}= has {', '.join(twice)} more than once; give each name once.\n"
                              f"For example:  {example}")
    return list(value)


def reading_options(separator=None, decimal_mark=None, thousands_mark=None, empty_values=None,
                    skip_rows=None, encoding=None, table_number=None, read_as_text=None, columns=None,
                    column_names=None, skip_lines_starting_with=None, table_name=None) -> dict:
    """Check the reading options at once and give back only the ones that were given.

    sdata.table(...) and sdata.chart(...) pass their options through here, so every
    reading word checks them the same way.
    """
    options = {}
    if separator is not None:
        if not isinstance(separator, str) or separator == "":
            raise SimplydataError(
                "separator= is the character between the values on each line.\n"
                'For example:  sdata.table("lab.csv", separator=";")   or   separator="tab"'
            )
        options["separator"] = {"tab": "\t", "space": " "}.get(separator.lower(), separator)
    if decimal_mark is not None:
        if decimal_mark not in (".", ","):
            raise SimplydataError(
                f'decimal_mark= should be "." or ",", not {decimal_mark!r}.\n'
                'For example, when 3,5 means three and a half:  sdata.table("lab.csv", decimal_mark=",")'
            )
        options["decimal_mark"] = decimal_mark
    if thousands_mark is not None:
        if not isinstance(thousands_mark, str) or len(thousands_mark) != 1:
            raise SimplydataError(
                "thousands_mark= is the one character that groups thousands, as in 1.000.000 or 1 000 000.\n"
                'For example:  sdata.table("lab.csv", decimal_mark=",", thousands_mark=".")'
            )
        if thousands_mark == (decimal_mark or "."):
            raise SimplydataError(
                f'thousands_mark="{thousands_mark}" is the same as the decimal mark, so simplydata cannot '
                "tell 1.500 (one and a half) from 1.500 (fifteen hundred).\n"
                'Give both, for example:  sdata.table("lab.csv", decimal_mark=",", thousands_mark=".")'
            )
        options["thousands_mark"] = thousands_mark
    if empty_values is not None:
        if isinstance(empty_values, (str, int, float)) and not isinstance(empty_values, bool):
            empty_values = [empty_values]
        if (not isinstance(empty_values, (list, tuple, set))
                or not all(isinstance(v, (str, int, float)) and not isinstance(v, bool) for v in empty_values)):
            raise SimplydataError(
                'empty_values= is a list of the markers that mean "no value" in your file.\n'
                'For example:  sdata.table("lab.csv", empty_values=["NA", "-", "n/a"])'
            )
        options["empty_values"] = [str(v) for v in empty_values]
    if skip_rows is not None:
        if isinstance(skip_rows, bool) or not isinstance(skip_rows, (int, np.integer)) or skip_rows < 0:
            raise SimplydataError(
                "skip_rows= is how many lines to skip at the top, before the column names: a whole number.\n"
                'For example:  sdata.table("lab.csv", skip_rows=2)'
            )
        options["skip_rows"] = int(skip_rows)
    if encoding is not None:
        try:
            codecs.lookup(str(encoding))
        except LookupError:
            raise SimplydataError(
                f'simplydata does not know the encoding "{encoding}".\n'
                'Common ones: "utf-8" (most files), "latin-1" or "cp1252" (older Excel on Windows), "utf-16".\n'
                'For example:  sdata.table("lab.csv", encoding="latin-1")'
            ) from None
        options["encoding"] = str(encoding)
    if table_number is not None:
        good = table_number == "all" or (
            isinstance(table_number, (int, np.integer)) and not isinstance(table_number, bool) and table_number >= 1)
        if not good:
            raise SimplydataError(
                "table_number= picks a table in a Word file: 1 for the first, 2 for the second, "
                'or "all" to stack them.\nFor example:  sdata.table("report.docx", table_number=2)'
            )
        options["table_number"] = table_number if table_number == "all" else int(table_number)
    if read_as_text is not None:
        options["read_as_text"] = _read_as_text_names(read_as_text)
    if columns is not None:  # pandas read_csv(usecols=), Polars read_csv(columns=)
        options["columns"] = _names_option("columns", columns, 'sdata.table("weather.csv", columns=["month", "city", '
                                                               '"rain"])')
    if column_names is not None:  # pandas read_csv(header=None, names=), Polars read_csv(has_header=False, new_columns=)
        options["column_names"] = _names_option("column_names", column_names,
                                                'sdata.table("logger.csv", column_names=["time", "temperature"])')
    if skip_lines_starting_with is not None:  # pandas read_csv(comment=), Polars read_csv(comment_prefix=)
        mark = skip_lines_starting_with
        if not isinstance(mark, str) or len(mark) != 1 or mark.isalnum() or mark in ",;\t\"' \n":
            raise SimplydataError(
                "skip_lines_starting_with= is the one sign that starts a note line in the file, such as \"#\" "
                "(not a letter, a digit, a quote or a separator).\n"
                'For example:  sdata.table("logger.csv", skip_lines_starting_with="#")')
        options["skip_lines_starting_with"] = mark
    if "columns" in options and "column_names" in options:
        missing = [c for c in options["columns"] if c not in options["column_names"]]
        if missing:
            raise SimplydataError(f'columns= names "{missing[0]}", which is not in column_names=. With column_names= '
                                  "the names in columns= are the new names.")
    if table_name is not None:  # tables phase, batch 3 (P38): one table of a database file
        if not isinstance(table_name, str) or not table_name.strip():
            raise SimplydataError(
                "table_name= is the name of one table in a database file, in quotes.\n"
                'For example:  sdata.table("lab.sqlite", table_name="samples")'
            )
        options["table_name"] = table_name
    return options


def _check_options_fit(kind: str, options: dict, label: str) -> None:
    for option in options:
        kinds = _OPTIONS_FOR[option]
        if kind not in kinds:
            works = ", ".join(_KIND_NAMES[k] for k in kinds)
            raise SimplydataError(
                f'{option}= is for {works} files, so it cannot be used for "{label}" '
                f"({_KIND_NAMES[kind]}).\nLeave {option}= out for this file."
            )


def _check_reading_source(source, options) -> None:
    if options and not isinstance(source, (str, os.PathLike)):
        names = ", ".join(f"{k}=" for k in options)
        raise SimplydataError(
            f"{names} {'is' if len(options) == 1 else 'are'} for reading files, "
            "and this data is already a table.\n"
            'Use it with a file name, for example:  sdata.table("lab.csv", decimal_mark=",")'
        )


def _file_suffix(name) -> str:
    """The file type by the end of the name: ".csv", or ".csv.gz" for the compressed text files."""
    lowered = str(name).lower()
    for ending in _TWO_PART_ENDINGS:
        if lowered.endswith(ending):
            return ending
    return Path(lowered).suffix


def _compression(label) -> str | None:
    """pandas read_csv(compression=) for a compressed text file, by its name."""
    lowered = str(label).lower()
    return "gzip" if lowered.endswith(".gz") else "zip" if lowered.endswith(".zip") else None


def _kind_of(suffix: str, label: str) -> str:
    kind = _READERS.get(suffix.lower())
    if kind is None:
        raise SimplydataError(
            f'simplydata cannot read "{suffix or label}" files yet.\n'
            "It can read: " + ", ".join(sorted(_READERS))
        )
    return kind


SEPARATORS = ",;\t|"  # the only characters ever guessed as the separator: never a letter, digit or other sign
_SEPARATOR_WORDS = {",": '","', ";": '";"', "\t": "a tab", "|": '"|"'}
_SEPARATOR_OPTION = {",": '","', ";": '";"', "\t": '"tab"', "|": '"|"'}
_guesses: list | None = None  # while a folder is read, the guesses are collected and said once


def _guess_separator(source, encoding="utf-8", skip_rows=0, compression=None) -> str:
    """The character between values in a text file: Python's csv.Sniffer, allowed to choose only a comma,
    semicolon, tab or bar. Anything else it might find (a letter such as the "e" of "species", a digit, a
    space or another sign) is refused. A file with one column has none of the four, so the sniffer fails and
    "," is used: the file is read as one column."""
    try:
        if compression is not None:  # a .csv.gz or .zip file: the guess reads the start of the text inside
            sample = _start_of_compressed(source, compression)
        elif isinstance(source, io.BytesIO):
            sample = source.getvalue()[:65536]
        else:
            with open(source, "rb") as fh:
                sample = fh.read(65536)
        lines = sample.decode(encoding, errors="ignore").splitlines()
    except (OSError, LookupError):
        return ","
    lines = lines[skip_rows or 0:]  # the lines above the column names (skip_rows=) are not part of the table
    if len(sample) == 65536 and len(lines) > 1:
        lines = lines[:-1]  # the sample ends in the middle of a line
    if not lines:
        return ","
    try:
        found = csv.Sniffer().sniff("\n".join(lines), delimiters=SEPARATORS).delimiter
    except csv.Error:
        # rows of different lengths, or very wide rows: the column names alone decide; the separator is the one
        # of the four that turns up most often in them (none of them: one column)
        header = lines[0]
        counts = {sep: header.count(sep) for sep in SEPARATORS}
        found = max(counts, key=counts.get) if max(counts.values()) else ","
    return found if found in SEPARATORS else ","


def _start_of_compressed(source, compression) -> bytes:
    """The first 64 KB of the text in a .gz file (Python's gzip) or in the one file of a .zip (zipfile)."""
    import gzip
    import zipfile

    if isinstance(source, io.BytesIO):
        source = io.BytesIO(source.getvalue())
    if compression == "gzip":
        with gzip.open(source, "rb") as fh:
            return fh.read(65536)
    with zipfile.ZipFile(source) as archive:
        names = [n for n in archive.namelist() if not n.endswith("/")]
        if len(names) != 1:
            return b""
        with archive.open(names[0]) as fh:
            return fh.read(65536)


def _say_guess(label, sep) -> None:
    """One plain line when simplydata guessed the separator (none when separator= was given)."""
    if _guesses is not None:
        _guesses.append(sep)
        return
    print(f'Read "{label}" with {_SEPARATOR_WORDS[sep]} between the columns (guessed). '
          f"To be sure, give separator={_SEPARATOR_OPTION[sep]}.")


def _separator_for(source, kind, label, options) -> str:
    """separator= when given, a tab for .tsv files, otherwise the guess (said in one line)."""
    if options.get("separator"):
        return options["separator"]
    if kind == "tsv":
        return "\t"
    sep = _guess_separator(_rewind(source), options.get("encoding", "utf-8"), options.get("skip_rows", 0),
                           _compression(label))
    _say_guess(label, sep)
    return sep


def _rewind(source):
    if isinstance(source, io.BytesIO):
        source.seek(0)
    return source


# ---------------------------------------------------------------- one file
def read_file(path, sheet=None, fast: bool = False, keep_fast: bool = False, options: dict | None = None):
    """Read a file, a folder of files, a file pattern such as "data/*.csv", or a web address.

    Big files use the fast engine; keep_fast=True keeps its Polars table.
    """
    options = options or {}
    text = str(path)
    if _is_web_address(text):
        return _read_web(text, sheet=sheet, fast=fast, keep_fast=keep_fast, options=options)
    path = Path(path)
    if path.is_dir():
        return _read_many(_files_in_folder(path), sheet=sheet, fast=fast, keep_fast=keep_fast,
                          options=options, asked_for=text)
    if not path.exists() and _has_wildcards(text):
        return _read_many(_files_matching(text), sheet=sheet, fast=fast, keep_fast=keep_fast,
                          options=options, asked_for=text)
    if not path.exists():
        raise _missing_file_error(path)
    kind = _kind_of(_file_suffix(path.name), path.name)
    return _read_one(path, kind, path.stat().st_size, path.name, sheet=sheet, fast=fast,
                     keep_fast=keep_fast, options=options)


def _read_one(source, kind, size, label, sheet=None, fast=False, keep_fast=False, options=None):
    """Read one file (a path, or the bytes of a downloaded file)."""
    options = options or {}
    if "column_names" in options and kind in ("csv", "tsv", "excel"):
        _check_column_names(source, kind, label, options)
    if "skip_lines_starting_with" in options and kind in ("csv", "tsv"):
        _check_note_mark(source, label, options)
    try:
        found = _read_one_file(source, kind, size, label, sheet, fast, keep_fast, options)
    except SimplydataError:
        raise
    except Exception:
        if "columns" in options:  # the parent's refusal of a missing column, said in words
            _check_columns_wanted(source, kind, label, options)
        raise
    if "read_as_text" in options:
        _check_read_as_text(found, options["read_as_text"], label)
    if "columns" in options:  # in the order given (pandas usecols= and Polars columns= keep the file's order)
        wanted = options["columns"]
        found = found.select(wanted) if _is_polars(found) else found[wanted]
    return found


def _header_of(source, kind, options, header="infer"):
    """The first lines of a file, read by pandas with the file's reading options (for the checks below)."""
    if kind == "excel":
        return pd.read_excel(_rewind(source), nrows=1, header=0 if header == "infer" else None,
                             skiprows=options.get("skip_rows"))
    if kind == "parquet":
        return pd.read_parquet(_rewind(source)).head(1)
    sep = options.get("separator") or ("\t" if kind == "tsv" else _guess_separator(
        _rewind(source), options.get("encoding", "utf-8"), options.get("skip_rows", 0)))
    return pd.read_csv(_rewind(source), sep=sep, nrows=1, header=header, skiprows=options.get("skip_rows"),
                       comment=options.get("skip_lines_starting_with"), encoding=options.get("encoding"),
                       engine=None if len(sep) == 1 else "python")


def _check_columns_wanted(source, kind, label, options) -> None:
    """Every column named in columns= must be in the file; the refusal names the file's columns."""
    try:
        names = (options["column_names"] if "column_names" in options
                 else [str(c) for c in _header_of(source, kind, options).columns])
    except Exception:  # noqa: BLE001 - the original error is raised instead
        return
    missing = [c for c in options["columns"] if c not in names]
    if missing:
        lines = [f'columns= names "{missing[0]}", but "{label}" has no column called that.']
        guess = suggest(missing[0], names, n=1)
        if guess:
            lines.append(f'Did you mean "{guess[0]}"?')
        lines.append("Its columns: " + ", ".join(names))
        raise SimplydataError("\n".join(lines))


def _check_column_names(source, kind, label, options) -> None:
    """column_names= gives one name for each column of the file (pandas would put extra columns in the row labels,
    Polars would keep the extra columns' own names)."""
    width = _header_of(source, kind, options, header=None).shape[1]
    given = len(options["column_names"])
    if given != width:
        raise SimplydataError(
            f'"{label}" has {width} column{"s" if width != 1 else ""}, but column_names= gives {given} '
            f'name{"s" if given != 1 else ""}. Give one name for each column, in order; to keep only some of them, '
            "add columns= with the ones you want.")


def _check_note_mark(source, label, options) -> None:
    """skip_lines_starting_with= skips whole lines. pandas comment= also cuts a line where the sign appears later in
    it, so a file in which it does is refused, with the line, rather than cut without a word."""
    mark = options["skip_lines_starting_with"]
    encoding = options.get("encoding", "utf-8")
    if isinstance(source, io.BytesIO):
        text = source.getvalue().decode(encoding, errors="ignore")
    else:
        with open(source, encoding=encoding, errors="ignore") as fh:
            text = fh.read()
    for number, line in enumerate(text.splitlines(), 1):
        if mark in line[1:] and not line.startswith(mark):
            raise SimplydataError(
                f'Line {number} of "{label}" has "{mark}" inside it, not at its start: {line.strip()[:60]!r}.\n'
                f'skip_lines_starting_with="{mark}" skips whole lines that start with it, and pandas would cut this '
                "line at the sign. Choose a sign that starts only the note lines.")
    _rewind(source)


def _check_read_as_text(found, names, label) -> None:
    """Every column named in read_as_text= must be in the file (pandas and Polars pass over a missing one)."""
    columns = [str(c) for c in found.columns]
    missing = [n for n in names if n not in columns]
    if not missing:
        return
    lines = [f'read_as_text= names "{missing[0]}", but "{label}" has no column called that.']
    guess = suggest(missing[0], columns, n=1)
    if guess:
        lines.append(f'Did you mean "{guess[0]}"?')
    lines.append("Its columns: " + ", ".join(columns))
    raise SimplydataError("\n".join(lines))


def _read_one_file(source, kind, size, label, sheet, fast, keep_fast, options):
    _check_options_fit(kind, options, label)

    asked = fast
    fast = asked or size > BIG_FILE_BYTES
    polars_can = ("thousands_mark" not in options and _compression(label) is None
                  and str(options.get("encoding", "utf-8")).lower().replace("_", "-") in ("utf-8", "utf8"))
    if fast and kind in ("csv", "tsv", "parquet") and polars_can:
        import polars as pl

        if not asked:
            print("This file is large, so simplydata is using its fast mode.")
        if kind == "parquet":  # Polars read_parquet(columns=[...])
            fast_table = pl.read_parquet(_rewind(source), columns=options.get("columns"))
        else:
            sep = _separator_for(source, kind, label, options)
            extra = {}
            if options.get("decimal_mark") == ",":
                extra["decimal_comma"] = True
            if "empty_values" in options:
                extra["null_values"] = options["empty_values"]
            if "skip_rows" in options:
                extra["skip_rows"] = options["skip_rows"]
            if "read_as_text" in options:  # Polars read_csv(schema_overrides={"sample_id": pl.String})
                extra["schema_overrides"] = {name: pl.String for name in options["read_as_text"]}
            if "column_names" in options:  # Polars read_csv(has_header=False, new_columns=[...])
                extra["has_header"] = False
                extra["new_columns"] = options["column_names"]
            elif "columns" in options:  # Polars read_csv(columns=[...])
                extra["columns"] = options["columns"]
            if "skip_lines_starting_with" in options:  # Polars read_csv(comment_prefix="#")
                extra["comment_prefix"] = options["skip_lines_starting_with"]
                if "skip_rows" in options:
                    # Polars skip_rows= counts the rows left after the note lines are taken out; pandas
                    # skiprows= counts the lines as they are in the file. Polars skip_lines= counts those too.
                    extra["skip_lines"] = extra.pop("skip_rows")
            fast_table = pl.read_csv(_rewind(source), separator=sep, infer_schema_length=10000, **extra)
        # A blank line: pandas read_csv skips it (skip_blank_lines=True), Polars read_csv makes it a row of empty
        # cells, the same row as a line of empty fields (",,"), which both keep. Polars has no option to skip blank
        # lines and its result cannot tell the two apart, so a file with a row of only empty cells is read by
        # pandas instead (as for thousands_mark= above): one answer on both engines, nothing guessed.
        if kind == "parquet" or not fast_table.height or not fast_table.width or not fast_table.select(
                pl.all_horizontal(pl.all().is_null()).any()).item():
            return fast_table if keep_fast else fast_table.to_pandas()

    if kind in ("csv", "tsv"):
        return _read_text(source, kind, label, options)
    if kind == "excel":
        return _read_excel(source, label, sheet, options)
    if kind == "parquet":  # pandas read_parquet(columns=[...])
        return pd.read_parquet(_rewind(source), columns=options.get("columns"))
    if kind == "json":
        return pd.read_json(_rewind(source))
    if kind == "word":
        return _read_word(source, label, options)
    if kind == "spss":
        return _read_spss(source)
    if kind in _MORE_KINDS:  # tables phase, batch 3 (P38)
        return _read_more(source, kind, label, options)
    return pd.read_stata(_rewind(source))


# ---------------------------------------------------------------- more file types (tables phase, batch 3, P38)
_MORE_KINDS = ("feather", "jsonl", "xml", "sas", "sqlite", "duckdb")


def _read_more(source, kind, label, options):
    """Feather, JSON lines, XML, SAS and database files, each read by pandas (or DuckDB) itself."""
    if kind == "feather":
        return pd.read_feather(_rewind(source))  # pandas read_feather
    if kind == "jsonl":
        return pd.read_json(_rewind(source), lines=True)  # pandas read_json(lines=True): one row per line
    if kind == "xml":
        return pd.read_xml(_rewind(source), parser="etree")  # pandas read_xml, with Python's own XML reader
    if kind == "sas":
        return pd.read_sas(_rewind(source), format="sas7bdat", encoding="infer")  # pandas read_sas
    if isinstance(source, io.BytesIO):
        raise SimplydataError(f'"{label}" is a database file. simplydata reads databases from this computer only: '
                              "download it, then read it by its file name.")
    if kind == "sqlite":
        return _read_sqlite(Path(source), label, options.get("table_name"))
    return _read_duckdb(Path(source), label, options.get("table_name"))


def _which_table(names, wanted, label) -> str:
    """The database table to read: the one named by table_name=, or the only one there is."""
    example = f'sdata.table("{label}", table_name="{names[0] if names else "samples"}")'
    if not names:
        raise SimplydataError(f'"{label}" has no tables in it.')
    if wanted is None:
        if len(names) == 1:
            print(f'"{label}" holds one table, "{names[0]}"; reading it.')
            return names[0]
        raise SimplydataError(f'"{label}" holds {len(names)} tables: ' + ", ".join(f'"{n}"' for n in names)
                              + f".\nSay which one with table_name=, for example:  {example}")
    if wanted not in names:
        lines = [f'"{label}" has no table called "{wanted}".']
        guess = suggest(wanted, names, n=1)
        if guess:
            lines.append(f'Did you mean table_name="{guess[0]}"?')
        lines.append("Its tables: " + ", ".join(f'"{n}"' for n in names))
        raise SimplydataError("\n".join(lines))
    return wanted


def _read_sqlite(path, label, wanted):
    """One table of an SQLite file: Python's sqlite3 (read-only) and pandas read_sql_query."""
    import sqlite3

    from ._sql import quoted

    try:
        con = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    except sqlite3.Error as problem:
        raise SimplydataError(f'simplydata could not open "{label}" as an SQLite database ({problem}).') from None
    try:
        names = [row[0] for row in con.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name")]
        name = _which_table(names, wanted, label)
        return pd.read_sql_query(f"SELECT * FROM {quoted(name)}", con)  # pandas read_sql_query
    except sqlite3.DatabaseError as problem:
        raise SimplydataError(f'"{label}" is not an SQLite database that simplydata can read ({problem}).') from None
    finally:
        con.close()


def _read_duckdb(path, label, wanted):
    """One table of a DuckDB file, opened read-only with no extensions and no other files (simplydata._sql)."""
    from . import _sql

    con = _sql.connect(f'Reading "{label}"', database=str(path), read_only=True)
    try:
        names = [row[0] for row in con.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main' ORDER BY table_name"
        ).fetchall()]
        name = _which_table(names, wanted, label)
        return con.sql(f"SELECT * FROM {_sql.quoted(name)}").df()  # DuckDB con.sql(...).df()
    finally:
        con.close()


def _pandas_text_options(options: dict) -> dict:
    extra = {}
    if "decimal_mark" in options:
        extra["decimal"] = options["decimal_mark"]
    if "thousands_mark" in options:
        extra["thousands"] = options["thousands_mark"]
    if "empty_values" in options:
        extra["na_values"] = options["empty_values"]
    if "skip_rows" in options:
        extra["skiprows"] = options["skip_rows"]
    if "read_as_text" in options:  # pandas read_csv(dtype={"sample_id": str}); empty cells stay empty
        extra["dtype"] = {name: str for name in options["read_as_text"]}
    if "column_names" in options:  # pandas read_csv(header=None, names=[...])
        extra["header"] = None
        extra["names"] = options["column_names"]
    if "columns" in options:  # pandas read_csv(usecols=[...])
        extra["usecols"] = options["columns"]
    if "skip_lines_starting_with" in options:  # pandas read_csv(comment="#")
        extra["comment"] = options["skip_lines_starting_with"]
    return extra


def _read_text(source, kind, label, options):
    extra = _pandas_text_options(options)
    if "encoding" in options:
        extra["encoding"] = options["encoding"]
    sep = _separator_for(source, kind, label, options)
    try:
        engine = {} if len(sep) == 1 else {"engine": "python"}
        if _compression(label) is not None:  # .csv.gz, .zip: pandas read_csv(compression=)
            extra["compression"] = _compression(label)
        return pd.read_csv(_rewind(source), sep=sep, **engine, **extra)
    except UnicodeDecodeError:
        raise SimplydataError(
            f'"{label}" is not saved as {options.get("encoding", "utf-8")} text.\n'
            "Tell simplydata how it is saved, for example:  "
            f'sdata.table("{label}", encoding="latin-1")\n'
            '"latin-1" or "cp1252" fit most files from older Excel on Windows.'
        ) from None
    except (pd.errors.ParserError, csv.Error) as problem:
        first_line = (str(problem).strip().splitlines() or [""])[0]
        raise SimplydataError(
            f'simplydata could not split "{label}" into columns ({first_line}).\n'
            "Tell it the character between the values, for example:  "
            f'sdata.table("{label}", separator=";")\n'
            "If there are notes above the column names, skip them:  "
            f'sdata.table("{label}", skip_rows=2)'
        ) from None
    except ValueError as problem:  # a .zip with more than one file in it
        if _compression(label) != "zip":
            raise
        raise SimplydataError(f'simplydata reads a .zip file that holds one CSV or TSV file; "{label}" could not be '
                              f"read that way ({str(problem).strip()}).\nUnzip it and read the files, for example "
                              'sdata.table("folder/*.csv").') from None


def _read_excel(source, label, sheet, options):
    extra = _pandas_text_options(options)
    if sheet is None:
        return pd.read_excel(_rewind(source), **extra)
    if isinstance(sheet, str) and sheet.lower() == "all":
        sheets = pd.read_excel(_rewind(source), sheet_name=None, **extra)
        parts = []
        for name, frame in sheets.items():
            if len(frame.columns) == 0:
                print(f'Sheet "{name}" is empty, so it is left out.')
                continue
            parts.append((str(name), frame))
        if not parts:
            raise SimplydataError(f'Every sheet in "{label}" is empty.')
        return _stack(parts, column="sheet", what="sheet",
                      example=f'sdata.table("{label}", sheet="{parts[0][0]}")', keep_fast=False, file_label=label)
    try:
        return pd.read_excel(_rewind(source), sheet_name=sheet, **extra)
    except ValueError:
        sheets = pd.ExcelFile(_rewind(source)).sheet_names
        lines = [f'Sheet "{sheet}" not found in {label}.']
        guess = suggest(sheet, sheets, n=1)
        if guess:
            lines.append(f'Did you mean "{guess[0]}"?')
        lines.append("Sheets you have: " + ", ".join(sheets))
        lines.append('sheet="all" reads every sheet and stacks them.')
        raise SimplydataError("\n".join(lines)) from None


def _read_word(source, label, options):
    """The tables in a Word file (.docx). Needs python-docx (an optional extra)."""
    try:
        import docx
    except ImportError:
        raise SimplydataError(f"Reading Word files needs python-docx.\n{_FILES_HINT}") from None
    tables = docx.Document(_rewind(source)).tables
    if not tables:
        raise SimplydataError(f'"{label}" has no tables in it. simplydata reads the tables of a Word file.')
    number = options.get("table_number", 1)

    def as_frame(word_table):
        # The cells go through the CSV reader, so numbers, decimal marks and empty values
        # are understood exactly as in a CSV file.
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter="\t")
        for row in word_table.rows:
            writer.writerow([cell.text.strip() for cell in row.cells])
        buffer.seek(0)
        return pd.read_csv(buffer, sep="\t", **_pandas_text_options(options))

    if number == "all":
        parts = [(i, as_frame(t)) for i, t in enumerate(tables, 1)]
        return _stack(parts, column="table", what="table",
                      example=f'sdata.table("{label}", table_number=1)', keep_fast=False)
    if number > len(tables):
        raise SimplydataError(
            f'"{label}" has {len(tables)} table{"s" if len(tables) != 1 else ""}, so there is no table {number}.\n'
            f'For example:  sdata.table("{label}", table_number={len(tables)})'
        )
    if len(tables) > 1 and "table_number" not in options:
        print(f'"{label}" has {len(tables)} tables; reading table 1. '
              'Use table_number=2 for the next one, or table_number="all" to stack them.')
    return as_frame(tables[number - 1])


def _read_spss(source):
    """An SPSS file (.sav). pandas reads it with pyreadstat (an optional extra)."""
    try:
        import pyreadstat  # noqa: F401
    except ImportError:
        raise SimplydataError(f"Reading SPSS files needs pyreadstat.\n{_FILES_HINT}") from None
    if isinstance(source, io.BytesIO):  # pyreadstat needs a real file
        with tempfile.TemporaryDirectory() as folder:
            temporary = Path(folder) / "download.sav"
            temporary.write_bytes(source.getvalue())
            return pd.read_spss(temporary)
    return pd.read_spss(source)


# ---------------------------------------------------------------- several files
def _has_wildcards(text: str) -> bool:
    return any(c in text for c in "*?[")


def _natural_key(path: Path):
    """Sort file2 before file10."""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", str(path))]


def _readable(path: Path) -> bool:
    return path.is_file() and not path.name.startswith((".", "~$"))


def _list_some(names) -> str:
    names = sorted(names)
    return ", ".join(names[:15]) + (" ..." if len(names) > 15 else "")


def _files_in_folder(folder: Path) -> list[Path]:
    files = sorted((p for p in folder.iterdir() if _readable(p) and _file_suffix(p.name) in _READERS),
                   key=_natural_key)
    if not files:
        there = [p.name for p in folder.iterdir() if p.is_file()]
        lines = [f'The folder "{folder}" has no files simplydata can read.',
                 "It can read: " + ", ".join(sorted(_READERS))]
        lines.append("Files in the folder: " + _list_some(there) if there else "The folder is empty.")
        raise SimplydataError("\n".join(lines))
    return files


def _files_matching(pattern: str) -> list[Path]:
    files = sorted((Path(p) for p in glob.glob(pattern, recursive=True) if _readable(Path(p))), key=_natural_key)
    if not files:
        folder = Path(pattern).parent
        while _has_wildcards(str(folder)):
            folder = folder.parent
        lines = [f'No files match "{pattern}".']
        if folder.is_dir():
            there = [p.name for p in folder.iterdir() if p.is_file()]
            lines.append(f'Files in "{folder}": ' + _list_some(there) if there else f'The folder "{folder}" is empty.')
        else:
            lines.append(f'The folder "{folder}" does not exist.')
            lines.append(f"simplydata is looking in: {Path('.').resolve()}")
        raise SimplydataError("\n".join(lines))
    return files


def _labels(files: list[Path]) -> list[str]:
    """Each file's name, with its folder only when needed to tell files apart."""
    full = [p.resolve() for p in files]
    common = Path(os.path.commonpath([p.parent for p in full]))
    return [p.relative_to(common).as_posix() for p in full]


def _read_many(files, sheet, fast, keep_fast, options, asked_for):
    global _guesses
    labels = _labels(files)
    parts = []
    _guesses = []
    try:
        for path, label in zip(files, labels):
            kind = _kind_of(_file_suffix(path.name), path.name)
            parts.append((label, _read_one(path, kind, path.stat().st_size, label, sheet=sheet, fast=fast,
                                           keep_fast=keep_fast, options=options)))
        guessed = sorted(set(_guesses), key=SEPARATORS.index)
    finally:
        _guesses = None
    if guessed:
        said = " or ".join(_SEPARATOR_WORDS[g] for g in guessed)
        print(f"Read the files with {said} between the columns (guessed). "
              f"To be sure, give separator={_SEPARATOR_OPTION[guessed[0]]}.")
    is_folder = Path(asked_for).is_dir()
    folder = Path(asked_for) if is_folder else files[0].parent
    example = f'sdata.table("{(files[0].parent / files[0].name).as_posix()}")'
    if is_folder:
        example += (", or pick files with a pattern, for example "
                    f'sdata.table("{folder.as_posix()}/*{files[0].suffix}")')
    return _stack(parts, column="file", what="file", example=example, keep_fast=keep_fast)


def _is_number_column(native, name):
    """True for numbers, False for text, None when the column is all empty."""
    column = native[name]
    if _is_polars(native):
        if column.null_count() == len(column):
            return None
        return column.dtype.is_numeric()
    if column.isna().all():
        return None
    return pd.api.types.is_numeric_dtype(column) and not pd.api.types.is_bool_dtype(column)


def _variable_name(sheet_name, taken):
    """A name to copy for a sheet: plain text cleaning only. Lowercase, anything but letters and digits becomes "_",
    and a name that starts with a digit (or is a Python keyword) gets "sheet_" in front; a repeat gets _2, _3 ..."""
    name = re.sub(r"_+", "_", re.sub(r"\W", "_", sheet_name.lower())).strip("_") or "sheet"
    if name[0].isdigit() or keyword.iskeyword(name):
        name = f"sheet_{name}"
    base, n = name, 2
    while name in taken:
        name, n = f"{base}_{n}", n + 1
    taken.add(name)
    return name


def _read_each_sheet(labels, file_label, shown=10):
    """Ready-to-copy lines that read each sheet on its own; past about ten sheets the rest are named only."""
    taken = set()
    names = [_variable_name(label, taken) for label in labels[:shown]]
    width = max(map(len, names))
    def quoted(text):  # Excel allows " in a sheet name; then the line uses Python's own quotes
        return repr(text) if '"' in text else f'"{text}"'

    lines = [f'  {name.ljust(width)} = sdata.table({quoted(file_label)}, sheet={quoted(label)})'
             for name, label in zip(names, labels)]
    if len(labels) > shown:
        lines.append("  and the same for the sheets " + ", ".join(f'"{label}"' for label in labels[shown:]))
    return lines


def _stack(parts, column, what, example, keep_fast, file_label=None):
    """Stack tables with the same columns, with a column saying where each row came from.

    parts is a list of (label, table); what is "file", "sheet" or "table". For sheets, file_label is the Excel file's
    name, and a refusal ends with a line to copy for each sheet.
    """
    def called(label):
        return {"file": f"{label}", "sheet": f'sheet "{label}"', "table": f"table {label}"}[what]

    first_label, first = parts[0]
    reference = list(first.columns)
    problems = []
    for label, frame in parts[1:]:
        names = list(frame.columns)
        problems += [f'  {called(label)} has no column "{n}"' for n in reference if n not in names]
        problems += [f'  {called(label)} has an extra column "{n}"' for n in names if n not in reference]
    if problems:
        shown = problems[:12] + ([f"  ... and {len(problems) - 12} more differences"] if len(problems) > 12 else [])
        if what == "sheet" and file_label is not None:
            raise SimplydataError(
                f'The sheets in "{file_label}" do not have the same columns, so they cannot be joined into one table:\n'
                + "\n".join(shown)
                + f"\nColumns in {called(first_label)}: " + ", ".join(map(str, reference))
                + "\nRead each sheet on its own:\n"
                + "\n".join(_read_each_sheet([label for label, _ in parts], file_label))
                + '\nOr make the columns match, and sheet="all" stacks them.'
            )
        raise SimplydataError(
            f"These {what}s do not all have the same columns, so simplydata cannot stack them:\n"
            + "\n".join(shown)
            + f"\nColumns in {called(first_label)}: " + ", ".join(map(str, reference))
            + f"\nMake the columns match, or read one {what} at a time, for example {example}."
        )

    name = column
    if name in reference:
        name = f"from_{column}"
        print(f'Your {what}s already have a column called "{column}", so the {what} names go in "{name}".')

    # A column with numbers in some parts and text in others becomes text everywhere.
    mixed = [col for col in reference
             if len({_is_number_column(frame, col) for _, frame in parts} - {None}) > 1]

    if keep_fast and any(_is_polars(frame) for _, frame in parts):
        import polars as pl

        frames = []
        for label, frame in parts:
            if not _is_polars(frame):
                frame = pl.from_pandas(frame)
            if mixed:
                frame = frame.with_columns([pl.col(c).cast(pl.String) for c in mixed])
            frames.append(frame.select(reference).with_columns(pl.lit(label).alias(name)).select([name, *reference]))
        stacked = pl.concat(frames, how="vertical_relaxed")
    else:
        frames = []
        for label, frame in parts:
            frame = (frame.to_pandas() if _is_polars(frame) else frame)[reference].copy()
            for col in mixed:
                values = frame[col]
                frame[col] = values.astype(object).where(values.isna(), values.astype(str))
            frame.insert(0, name, label)
            frames.append(frame)
        stacked = pd.concat(frames, ignore_index=True)

    for col in mixed:
        print(f'Note: column "{col}" holds numbers in some {what}s and text in others, so it is kept as text.')
    print(f"Read {len(parts)} {what}{'s' if len(parts) != 1 else ''} and stacked them: {len(stacked)} rows. "
          f'The column "{name}" says which {what} each row came from.')
    return stacked


# ---------------------------------------------------------------- web addresses
def _is_web_address(text: str) -> bool:
    return text.lower().startswith(("http://", "https://"))


def _redirect_allowed(old_url: str, new_url: str) -> bool:
    """A web address may send you on to another http(s) address, never from https down to http (which would show
    the address, and any key in it, to everyone on the way) and never to ftp or a file."""
    old, new = urllib.parse.urlparse(old_url).scheme.lower(), urllib.parse.urlparse(new_url).scheme.lower()
    return new == "https" or (new == "http" and old == "http")


class _SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _redirect_allowed(req.full_url, newurl):
            raise SimplydataError(
                f"The web address sent simplydata on to another address that is not safe to follow:\n  {newurl}\n"
                "simplydata follows https addresses only (and http only from an http address). "
                "Download the file yourself and read it from your computer.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _download(url: str) -> bytes:
    """The file at a web address the user gave: one GET request with the address and the User-Agent
    "simplydata", nothing else of yours (privacy: README, SECURITY.md, tests/test_privacy.py)."""
    request = urllib.request.Request(url, headers={"User-Agent": "simplydata"})
    opener = urllib.request.build_opener(_SafeRedirect)
    try:
        with opener.open(request, timeout=WEB_TIMEOUT_SECONDS) as answer:
            return answer.read()
    except urllib.error.HTTPError as problem:
        meaning = {401: "a login is needed", 403: "not allowed", 404: "not found",
                   500: "the website had a problem"}.get(problem.code, "an error")
        raise SimplydataError(
            f"The web address answered {problem.code} ({meaning}):\n  {url}\n"
            "Check the address: open it in a web browser and see if the file downloads."
        ) from None
    except (urllib.error.URLError, OSError, ValueError) as problem:
        reason = getattr(problem, "reason", problem)
        raise SimplydataError(
            f"simplydata could not reach this web address ({reason}):\n  {url}\n"
            "Check that you are online and that the address is right.\n"
            'Or download the file and read it from your computer, for example sdata.table("data.csv").'
        ) from None


def _size_in_words(size: int) -> str:
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    if size >= 1024:
        return f"{size / 1024:.0f} KB"
    return f"{size} bytes"


def _read_web(url, sheet, fast, keep_fast, options):
    parts = urllib.parse.urlparse(url)
    name = Path(urllib.parse.unquote(parts.path)).name or parts.netloc
    suffix = _file_suffix(name)
    if suffix not in _READERS:
        wanted = urllib.parse.parse_qs(parts.query).get("format", [""])[0].lower()  # such as ?format=csv
        suffix = "." + wanted if wanted and "." + wanted in _READERS else ""
    if not suffix:
        print("The web address does not say what kind of file it is, so simplydata reads it as CSV text.")
        suffix = ".csv"
    data = _download(url)
    print(f"Downloaded {name} ({_size_in_words(len(data))}).")
    return _read_one(io.BytesIO(data), _READERS[suffix], len(data), name, sheet=sheet, fast=fast,
                     keep_fast=keep_fast, options=options)


# ---------------------------------------------------------------- anything into a table
def load(source=None, sheet=None, fast: bool = False, options: dict | None = None) -> pd.DataFrame:
    """Turn anything a beginner might give us into a pandas table.

    options are the checked reading options from reading_options(...); they are for files only.
    """
    _check_reading_source(source, options)
    if source is None:
        return pd.DataFrame()
    if getattr(source, "_is_simplydata_table", False):
        return load(source._frame.to_native())
    if _is_simplydata_numbers(source):
        return source._as_pandas(for_chart=True)
    if isinstance(source, (str, os.PathLike)):
        return read_file(source, sheet=sheet, fast=fast, options=options)
    if isinstance(source, pd.DataFrame):
        return source
    if isinstance(source, pd.Series):
        return source.to_frame()
    if _is_polars(source):
        return _polars_to_pandas(source)
    if isinstance(source, dict):
        try:
            return pd.DataFrame(source)
        except ValueError:
            raise SimplydataError(
                "The lists in your table have different lengths.\n"
                + ", ".join(f"{k}: {len(v)}" for k, v in source.items() if hasattr(v, "__len__"))
            ) from None
    if isinstance(source, (list, tuple, np.ndarray)):
        arr = np.asarray(source)
        if arr.ndim == 1:
            return pd.DataFrame({"value": arr})
        if arr.ndim == 2:
            return pd.DataFrame(arr)
    raise SimplydataError(
        f"simplydata does not know how to use a {type(source).__name__}.\n"
        "Give it a file name, a table, or a list of numbers."
    )


def _is_simplydata_numbers(obj) -> bool:
    """sdata.numbers(...) or sdata.number_grid(...)."""
    return bool(getattr(obj, "_is_simplydata_numbers", False) or getattr(obj, "_is_simplydata_grid", False))


def is_listlike(value) -> bool:
    return (isinstance(value, (list, tuple, np.ndarray, pd.Series, range)) or _is_polars(value)
            or bool(getattr(value, "_is_simplydata_numbers", False)))


def check_columns(data: pd.DataFrame, **roles) -> None:
    """Check at call time that every named column exists (friendly error if not)."""
    for value in roles.values():
        if isinstance(value, str) and len(data.columns) and value not in data.columns:
            raise column_error(value, data.columns)
        if isinstance(value, str) and not len(data.columns):
            raise column_error(value, data.columns)


def frame_for(data: pd.DataFrame, **roles):
    """Build the table a drawing step will use.

    Each role (x=, y=, colour=, ...) can be a column name, a list of values, or None.
    Lists become new columns named after the role. Returns (table, names) where
    names maps each role to the column to use (or None).
    """
    lists = {k: v for k, v in roles.items() if v is not None and is_listlike(v)}
    names = {}
    if lists:
        lengths = {k: len(v) for k, v in lists.items()}
        if len(set(lengths.values())) > 1:
            raise SimplydataError(
                "Your lists have different lengths: "
                + ", ".join(f"{k} has {n}" for k, n in lengths.items())
            )
        n = next(iter(lengths.values()))
        if len(data.columns) and len(data) == n:
            table = data.copy()
        elif len(data.columns) and any(isinstance(v, str) for v in roles.values() if v is not None):
            raise SimplydataError(
                f"Your list has {n} values but your table has {len(data)} rows.\n"
                "Use column names, or lists of the same length as the table."
            )
        else:
            table = pd.DataFrame(index=range(n))
        for role, values in lists.items():
            if _is_polars(values):
                values = values.to_list()
            table[role] = list(values)
            names[role] = role
    else:
        table = data
    for role, value in roles.items():
        if role in names:
            continue
        if value is None:
            names[role] = None
        elif isinstance(value, str):
            if value not in table.columns:
                raise column_error(value, table.columns)
            names[role] = value
        else:
            raise SimplydataError(
                f"{role}= should be a column name or a list of values, not {value!r}."
            )
    return table, names


def load_native(source=None, sheet=None, fast: bool = False, options: dict | None = None):
    """Like load(), but Polars tables (and big files) stay in Polars. Used by tables."""
    _check_reading_source(source, options)
    if getattr(source, "_is_simplydata_table", False):
        return source._frame.to_native()
    if _is_simplydata_numbers(source):
        return source._as_pandas()
    if _is_polars(source):
        if hasattr(source, "collect"):  # LazyFrame
            source = source.collect()
        if not hasattr(source, "columns"):  # Series
            source = source.to_frame()
        return source
    if isinstance(source, (str, os.PathLike)):
        return read_file(source, sheet=sheet, fast=fast, keep_fast=True, options=options)
    return load(source, sheet=sheet, fast=fast)
