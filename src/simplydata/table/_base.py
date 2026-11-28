"""The heart of simplydata tables.

A table holds its data in a narwhals frame, so every word is written once and runs on
both pandas (normal files) and Polars (big files, Polars tables, fast=True).

Every step that changes the table goes through self._change(...), which remembers the
table as it was before. That gives undo(), show_steps() and start_again() for free.
Summaries never change the table; they return a new, small table.
"""

from __future__ import annotations

from .._typing import _Same

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..chart import Chart

from pathlib import Path

import narwhals as nw

from .. import _zone_clock
from .._data import load_native
from .._errors import (MissingWordError, SimplydataError, choice_error, column_error, friendly, missing_word_error,
                       old_word, other_name_error, suggest)

HISTORY_LIMIT = 30  # how many steps undo() can take back
SHOW_LIMIT = 1000  # table.show() with no rows= shows at most this many rows
REPR_WHOLE_LIMIT = 10_000  # a Polars table up to this size is shown whole in notebooks
REPR_ENDS = 30  # a bigger one shows this many rows from the start and the end
SAVE_TYPES = ("csv", "tsv", "xlsx", "parquet", "json",
              # tables phase, batch 3 (P38): each written by pandas itself (DuckDB for .duckdb)
              "csv.gz", "tsv.gz", "feather", "jsonl", "dta", "html", "sqlite", "db", "duckdb",
              # families for 100 %, batches 1-2: a finished table for a paper (Polars Markdown, pandas to_latex,
              # python-docx)
              "md", "tex", "docx")
PAPER_TYPES = ("md", "tex", "docx")
DATABASE_TYPES = ("sqlite", "db", "duckdb")  # these hold tables by name: save(..., in_table="river")
# Times with a time zone in files that have no place for the zone name (see Table._file_frame)
OFFSET_TEXT_TYPES = ("csv", "tsv", "csv.gz", "tsv.gz")  # written as text with the UTC offset, read back as UTC times
NO_ZONE_TYPES = {"xlsx": "Excel", "dta": "Stata"}  # written as the clock times of their zone, without the zone
TIME_WITH_OFFSET = "%Y-%m-%d %H:%M:%S%.f%:z"  # Polars dt.to_string: 2024-07-01 23:45:00-04:00 (pandas' own CSV text)
# Text files end each line with \n on every computer, as Polars writes them (pandas would write \r\n on Windows)
LINE_END = "\n"


def _plain_time_text(native):
    """The text pandas to_csv writes for a Polars column of times without a time zone, so a .csv file is the same on
    both engines: 2024-07-01 when every time is at midnight, else 2024-07-01 23:45:00 with as many decimals of a second
    as the values need (none, 3, 6 or 9). Polars write_csv would write 2024-07-01T23:45:00.000000."""
    filled = native.drop_nulls()
    parts = [filled.dt.hour(), filled.dt.minute(), filled.dt.second(), filled.dt.nanosecond()]
    if all((part == 0).all() for part in parts):
        return native.dt.to_string("%Y-%m-%d")
    fraction = parts[3]
    digits = next((d for d, step in ((0, 10**9), (3, 10**6), (6, 10**3)) if (fraction % step == 0).all()), 9)
    return native.dt.to_string("%Y-%m-%d %H:%M:%S" + (f"%.{digits}f" if digits else ""))


def _clock_text(native):
    """The text pandas to_csv writes for a Polars column of times of day: 01:02:03, or 04:05:06.500000 when the time
    has parts of a second (Python's own text of a time). Polars write_csv would write 01:02:03.000000000."""
    whole, fine = native.dt.to_string("%H:%M:%S"), native.dt.to_string("%H:%M:%S%.6f")
    return whole.zip_with(native.dt.nanosecond() == 0, fine)


def _duration_text(native):
    """The text pandas to_csv writes for a Polars column of durations (0 days 01:00:00); Polars write_csv cannot write
    durations at all. pandas to_csv itself writes the column, so the text is that of the pandas installed (pandas
    3.0 writes 0 days 01:00:00 where a later pandas writes 0 days 01:00:00.000000 next to a value with decimals)."""
    import polars as pl

    values = native.to_pandas()
    lines = values.to_frame().to_csv(index=False, header=False, lineterminator="\n").split("\n")[:len(values)]
    texts = [None if empty else text for text, empty in zip(lines, values.isna().tolist())]
    return pl.Series(native.name, texts, dtype=pl.String)


def _true_false_text(native):
    """True and False, as pandas to_csv writes them (Polars write_csv would write true and false)."""
    import polars as pl

    return native.replace_strict({True: "True", False: "False"}, return_dtype=pl.String)


def counted(n: int, word: str) -> str:
    """1 column, 2 columns: a count with its word in the singular or the plural."""
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def show(native):
    """Show a table nicely: a real table in Jupyter/VS Code, text elsewhere."""
    try:
        from IPython import get_ipython

        if get_ipython() is not None:
            from IPython.display import display

            display(native)
            return
    except ImportError:
        pass
    print(native)


def numbered(part, first: int = 0):
    """Rows of a table ready to show, numbered from 1 the way people count (display only).

    part is a narwhals frame of rows taken from a table; first is the position (from 0) of its
    first row in the whole table, so the last 3 rows of a 54-row table are shown as 52, 53, 54.
    The stored table is never changed: pandas tables keep their own index (as_pandas() gives
    0, 1, 2 ... as pandas users expect), and Polars tables, which have no row labels, are shown
    through pandas with the same numbers.
    """
    import pandas as pd

    native = part.to_native()
    if type(native).__module__.split(".")[0] == "pandas":
        shown = native.copy(deep=False)
    else:
        shown = part.to_pandas()
    shown.index = pd.RangeIndex(first + 1, first + 1 + len(shown))
    return shown


def numbered_at(part, positions):
    """Rows of a table ready to show, each numbered with its own position (from 0) in the whole table."""
    import pandas as pd

    shown = numbered(part)
    shown.index = pd.Index([int(p) + 1 for p in positions])
    return shown


def _show_whole(native):
    """Show a table without hiding any rows or columns behind "..."."""
    import pandas as pd

    with pd.option_context("display.max_rows", None, "display.max_columns", None, "display.width", None):
        show(native)


class PickingError(SimplydataError, TypeError):
    """table[...] and loops over a table: a friendly error that is still the TypeError Python tools expect."""


def _slice_text(key: slice) -> str:
    return f"{'' if key.start is None else key.start}:{'' if key.stop is None else key.stop}"


class BaseTable:
    """A table. Make one with sdata.table(...)."""

    _is_simplydata_table = True

    # Old names that still work for one release (with a note the first time): old -> new.
    _OLD_WORDS = {
        "done": ("as_pandas", "_done"),  # done() gave back Polars for Polars tables, so it still does
        # renamed 2026-11-15 (fit_straight_line, compare_to_random_order) and 2026-11-16 (talking rewrite)
        # NumPy + SciPy phase, batch 1 (decision 7, approved by Manish 2026-11-25): a verb, as find_value_at
        "values_at": "find_values_at",
        "show_first": "show_first_rows", "show_last": "show_last_rows", "count_empty": "count_empty_cells_in",
        "remove_empty_rows": "remove_rows_with_empty_cells_in", "fill_empty": "fill_empty_cells_in",
        "fit_straight_line": "fit_line", "compare_to_random_order": "check_if_random_order",
        "column_names": "get_column_names", "column": "get_column", "row": "get_row", "cell_at": "get_cell_at",
        "keep_rows": "keep_rows_where", "remove_rows": "remove_rows_where",
        "count_empty_cells": "count_empty_cells_in",
        "remove_rows_with_empty_cells": "remove_rows_with_empty_cells_in",
        "fill_empty_cells": "fill_empty_cells_in", "remove_extra_spaces": "remove_extra_spaces_in",
        "replace_values": "replace_values_in", "add_date_part_column": "add_column_with_part_of_date",
        "add_text_part_column": "add_column_with_part_of_text", "replace_text": "replace_text_in",
        "average_of": "find_average_of", "median_of": "find_median_of", "total_of": "find_total_of",
        "smallest_of": "find_smallest_of", "biggest_of": "find_biggest_of",
        "standard_deviation_of": "find_standard_deviation_of", "summary_of": "find_summary_of",
        "percent_of": "find_percent_of_rows_where", "count_different_values": "count_different_values_in",
        "percentile_of": "find_percentile_of", "most_common_of": "find_most_common_of",
        "correlation_between": "find_correlation_between", "interval_of": "find_interval_of",
        "chart": "start_chart", "compare_averages": "compare_averages_of",
        "compare_each_pair": "compare_each_pair_of", "compare_before_after": "compare_before_and_after",
        "compare_counts": "compare_counts_of", "compare_spreads": "compare_spreads_of",
        "compare_shapes": "compare_shapes_of", "check_random_order": "check_if_random_order",
        "compare_matched": "compare_matched_columns", "model_averages_of": "find_model_averages_of",
        "check_model": "check_model_of", "show_rows_that_pull": "show_rows_that_pull_model",
        "principal_components_of": "find_principal_components_of",
        "distances_between_rows": "find_distances_between_rows", "compare_profiles": "compare_profiles_of",
        "survival_over_time": "find_survival_over_time", "spectrum_of": "find_spectrum_of",
        "check_steady": "check_steady_over_time", "autocorrelation_of": "find_autocorrelation_of",
        "trend_of": "find_trend_of", "compare_forecasts": "compare_forecasts_for",
        "find_change_points": "find_change_points_in", "find_peaks": "find_each_peak_that",
        "find_dips": "find_each_dip_that", "map_of": "make_map_of", "fit_distribution": "fit_distribution_to",
        "compare_distributions": "compare_distributions_for", "make_numbers": "turn_into_numbers",
        "make_text": "turn_into_text", "make_dates": "turn_into_dates", "make_lowercase": "turn_into_lowercase",
        "make_uppercase": "turn_into_uppercase", "round_to": "round_numbers_in", "steps": "show_steps",
        # 2026-11-23 (Manish: "spread and gather would be nice")
        "turn_rows_into_columns": "spread_into_columns", "turn_columns_into_rows": "gather_into_rows",
    }

    def __init__(self, data=None, sheet=None, fast: bool = False, _frame=None, _reading=None):
        if _frame is None:
            native = load_native(data, sheet=sheet, fast=fast, options=_reading)
            if fast and type(native).__module__.split(".")[0] == "pandas":
                import polars as pl

                native = pl.from_pandas(native)
            if native is data:  # the user's own pandas or Polars table: later changes to it must not reach this one
                native = _independent_native(native)
            _frame = nw.from_native(native, eager_only=True)
        object.__setattr__(self, "_frame", _frame)
        object.__setattr__(self, "_original", _frame)
        object.__setattr__(self, "_history", [])  # list of (what was done, table before)

    # ------------------------------------------------------------------ helpers for words
    @property
    def _columns(self) -> list[str]:
        return list(self._frame.columns)

    def _need_columns(self, *names):
        """Friendly error at once if a column does not exist."""
        for name in names:
            if name not in self._frame.columns:
                raise column_error(name, self._frame.columns)

    @staticmethod
    def _check_choice(step: str, option: str, value, choices):
        if value not in choices:
            raise choice_error(step, option, value, list(choices))

    def _change(self, what: str, frame):
        """Replace the table with a changed one and remember the old one for undo().

        pandas tables are numbered again 0, 1, 2 ... after every step, so a filtered table
        never shows gaps such as 0, 3, 5. (Polars tables have no row numbers.) This is the
        only place that does it, and undo() gives back a table that was numbered the same way.
        """
        frame = nw.maybe_reset_index(frame)
        self._history.append((what, self._frame))
        if len(self._history) > HISTORY_LIMIT:
            self._history.pop(0)
        object.__setattr__(self, "_frame", frame)
        return self

    def _new_table(self, frame):
        """A new table (for summaries), using the same engine."""
        return type(self)(_frame=frame)

    @property
    def _engine(self) -> str:
        return "Polars" if self._frame.implementation.is_polars() else "pandas"

    # ------------------------------------------------------------------ history words
    @friendly
    def undo(self: _Same) -> _Same:
        """Take the last step back. table.undo()"""
        if not self._history:
            print("Nothing to undo: this table has no steps yet.")
            return self
        what, before = self._history.pop()
        object.__setattr__(self, "_frame", before)
        print(f"Undone: {what}")
        return self

    @friendly
    def show_steps(self: _Same) -> _Same:
        """List every step you did to this table, in order. table.show_steps()"""
        if not self._history:
            print("No steps yet.")
        else:
            for i, (what, _) in enumerate(self._history, 1):
                print(f"{i}. {what}")
        return self

    @friendly
    def start_again(self: _Same) -> _Same:
        """Go back to the table as it was at the start. table.start_again()"""
        return self._change("start again", self._original)

    @friendly
    def make_copy(self: _Same) -> _Same:
        """Give back an independent copy of the table. backup = table.make_copy()

        Steps on one table never change the other: after backup = table.make_copy(), table.keep_rows_where(...)
        leaves backup as it was. The copy keeps the steps so far (backup.show_steps(), backup.undo()).
        A plain backup = table gives the same table a second name, not a copy (pandas df.copy(), Polars
        df.clone(), R copies on change).
        """
        return self.__copy__()

    def __copy__(self):
        """copy.copy(table) and copy.deepcopy(table) give the same independent copy as table.make_copy()."""
        copied = type(self)(_frame=_independent(self._frame))
        object.__setattr__(copied, "_original", self._original)
        object.__setattr__(copied, "_history", list(self._history))
        return copied

    def __deepcopy__(self, memo):
        return self.__copy__()

    # ------------------------------------------------------------------ finishing words
    @friendly
    def as_pandas(self):
        """Give back the table as a plain pandas table, for other Python tools. df = table.as_pandas()

        Only needed when another library wants pandas: simplydata words never need it. It is a copy: changing df
        does not change the table, and later steps on the table do not change df (as as_polars() and
        numbers.as_numpy()).
        """
        return _independent_native(self._frame.to_pandas())

    @friendly
    def as_polars(self):
        """Give back the table as a plain Polars table, for other Python tools. df = table.as_polars()

        It is a copy, as as_pandas().
        """
        return _independent_native(self._frame.to_polars())

    def _done(self):
        """The old done(): the table as it is stored (pandas, or Polars for Polars tables)."""
        return self._frame.to_native()

    @friendly(pointers={"interactive": 'chart.show_in_web_page(), or chart.save("marks.html") for a web page '
                                       "file: a chart becomes a web page where it goes"})
    def start_chart(self) -> Chart:
        """Start a chart from this table. chart = table.start_chart()"""
        from ..chart import chart

        return chart(self)

    @friendly(others={"sheet_name": "in_sheet", "sheetName": "in_sheet", "name": "in_table"},
              pointers={"if_exists": 'in_table="river", which replaces that table and keeps the others'})
    def save(self: _Same, file_name, in_sheet=None, in_table=None) -> _Same:
        """Save the table; the end of the file name decides the type. table.save("clean.xlsx")

        File types: .xlsx (Excel), .csv, .tsv, .parquet and .json. Without in_sheet=, saving to an
        Excel file that already exists replaces the whole file, every sheet in it.

        in_sheet="2026" saves the table as one sheet of an Excel file and keeps the sheets already
        in it, so several tables go into one workbook:
            marks_2025.save("results.xlsx", in_sheet="2025")
            marks_2026.save("results.xlsx", in_sheet="2026")
        If the file does not exist yet, it is made with that sheet. If it already has a sheet of that
        name, that sheet is replaced (simplydata says so) and the other sheets are kept. Only .xlsx
        files have sheets. Sheet names follow Excel's rules: at most 31 characters, none of
        : \\ / ? * [ ], no apostrophe at the start or end, not "History" (Excel keeps it), and Excel
        counts "Cleaned" and "cleaned" as the same name.

        Mind the two names: sheet= reads a sheet, in_sheet= saves one. To read the workbook back:
            sdata.table("results.xlsx", sheet="2026")               one sheet
            everything = sdata.table("results.xlsx", sheet="all")   every sheet, stacked
        sheet="all" makes one table with a "sheet" column naming the sheet each row came from, so
        simplydata words work sheet by sheet:
            everything.count_rows(for_each_group_in="sheet")                how many rows came from each sheet
            everything.find_average_of("marks", for_each_group_in="sheet")  a summary per sheet
            everything.keep_rows_where("sheet", is_equal_to="2026")         just one sheet's rows
        (keep_rows_where changes everything; everything.undo() brings the other sheets back.)
        sheet="all" stacks the sheets only when they have the same columns. Sheets that hold different
        data are read by name, each on its own: simplydata says which columns differ and prints a line
        to copy for each sheet, such as  patients = sdata.table("study.xlsx", sheet="patients").

        A .csv file is written the way pandas writes it, on both engines: times without a time zone
        as 2024-07-01 23:45:00 (with decimals of a second only when the times have them, or just
        2024-07-01 when every time is at midnight), times of day as 01:02:03, durations as
        0 days 01:00:00, True and False with capitals, and an empty cell of a one-column table as ""
        (an empty line would be skipped when the file is read). One difference is left: an empty
        text ("") is "" on Polars and nothing on pandas. Text files (.csv, .tsv) end each line the
        same way on every computer (a line feed, as on Linux and macOS).

        Times with a time zone: .parquet and .feather keep the zone. A .csv or .tsv file has no place
        for it, so the times are written with their UTC offset (2024-07-01 23:45:00-04:00, on both
        engines) and sdata.table() reads them back as the same moments on the UTC clock; a note
        names the zone, to put back with table.change_time_zone_in("t", to="America/New_York").
        Excel and Stata have no time zones, so the clock times of the zone are saved (Polars
        dt.replace_time_zone(None), on both engines), with a note naming the zone. Polars reads the
        clock of a time zone for every date word, on both engines: local clock times before 1970 follow
        the main world time-zone data (IANA), the same on every computer.

        More file types: .csv.gz and .tsv.gz (compressed), .feather (Arrow), .jsonl
        (one JSON row per line), .dta (Stata) and .html (a web page table), each written by pandas.
        A database file (.sqlite, .db, .duckdb) holds tables by name, so it needs in_table=, the
        mirror of in_sheet=: table.save("results.sqlite", in_table="river") replaces that table
        and keeps the others (pandas to_sql(if_exists="replace"); DuckDB CREATE OR REPLACE TABLE).
        Read it back with sdata.table("results.sqlite", table_name="river").

        A finished table for a paper: .md (a Markdown table, as Polars writes one), .tex (a LaTeX
        tabular, pandas to_latex) and .docx (a Word table, python-docx: pip install "simplydata[files]").
        Each writes every row and column as it is; round the numbers first with round_numbers_in.
        table.save("clipboard") copies the table, to paste into Excel or a document (pandas
        to_clipboard; nothing leaves this computer).
        """
        from .._data import CLIPBOARD, _file_suffix

        if isinstance(file_name, str) and file_name.strip().lower() == CLIPBOARD:
            return self._save_to_clipboard()
        path = Path(file_name)
        kind = _file_suffix(path.name).lstrip(".")
        if not kind:
            raise SimplydataError(
                f'Add a file type to the name, for example "{path.name}.xlsx" or "{path.name}.csv".'
            )
        if kind not in SAVE_TYPES:
            raise choice_error("save", "file type", kind, SAVE_TYPES)
        if in_table is not None or kind in DATABASE_TYPES:  # tables phase, batch 3 (P38)
            if in_sheet is not None:
                raise SimplydataError("in_sheet= is for Excel files and in_table= for databases; give one of them.")
            self._save_in_table(path, kind, in_table)
            return self
        if in_sheet is not None and kind != "xlsx":
            raise SimplydataError(
                f"in_sheet= saves the table as one sheet of an Excel file. Only .xlsx files have sheets; "
                f"a .{kind} file holds one table.\n"
                f'For example:  table.save("{path.stem}.xlsx", in_sheet={in_sheet!r}), '
                f'or table.save("{path.name}") without in_sheet=.'
            )
        if path.parent and not path.parent.exists():
            raise SimplydataError(f'The folder "{path.parent}" does not exist. Create it first.')
        frame = self._file_frame(kind, path.name)
        if in_sheet is not None:
            self._save_in_sheet(path, in_sheet, frame)
            return self
        if kind == "csv" and frame.implementation.is_polars():
            native = frame.to_native()
            if native.width == 1 and native.null_count().item():
                # one column: an empty cell would be an empty line, which a reader skips; pandas writes "" there
                native.write_csv(str(path), null_value='""')
            else:
                frame.write_csv(str(path))  # Polars write_csv (lines end in \n on every computer)
        elif kind == "csv":
            frame.to_native().to_csv(path, index=False, lineterminator=LINE_END)  # pandas to_csv
        elif kind == "parquet":
            frame.write_parquet(str(path))
        elif kind in ("csv.gz", "tsv.gz", "feather", "jsonl", "dta", "html"):  # tables phase, batch 3 (P38)
            self._save_more(path, kind, frame)
        elif kind in PAPER_TYPES:  # families for 100 %, batches 1-2
            self._save_for_paper(path, kind, frame)
        else:
            pandas_table = frame.to_pandas()
            if kind == "tsv":
                pandas_table.to_csv(path, sep="\t", index=False, lineterminator=LINE_END)
            elif kind == "xlsx":
                pandas_table.to_excel(path, index=False)
            else:
                pandas_table.to_json(path, orient="records", indent=2)
        return self

    def _file_frame(self, kind, file_name):
        """The table as it goes into a file of this kind: columns with a time zone made to fit the file.

        A CSV or TSV file has no place for a zone name, so each such column is written as text with its UTC offset,
        in one layout on both engines (Polars dt.to_string("%Y-%m-%d %H:%M:%S%.f%:z"), the text pandas to_csv
        writes: 2024-07-01 23:45:00-04:00), and sdata.table() reads it back as the same moments on the UTC clock.
        Excel and Stata have no time zones at all (pandas refuses them), so the clock times of the zone are saved
        (pandas dt.tz_localize(None), Polars dt.replace_time_zone(None)). Either way a note names the zone.
        Times without a zone, times of day, durations and True/False go into a .csv file as the text pandas writes,
        on both engines (_plain_time_text, _clock_text, _duration_text, _true_false_text).
        """
        frame = self._frame
        if kind == "csv" and frame.implementation.is_polars():  # pandas' text on both engines
            texts = {nw.Time: _clock_text, nw.Duration: _duration_text, nw.Boolean: _true_false_text}
            changed = []
            for name, kind_ in frame.schema.items():
                if kind_ == nw.Datetime and not kind_.time_zone:
                    changed.append(_plain_time_text(frame[name].to_native()))
                elif any(kind_ == dtype for dtype in texts):
                    make = next(make for dtype, make in texts.items() if kind_ == dtype)
                    changed.append(make(frame[name].to_native()))
            if changed:
                frame = frame.with_columns(*(nw.from_native(text, series_only=True) for text in changed))
        zoned = {name: kind_.time_zone for name, kind_ in self._frame.schema.items()
                 if kind_ == nw.Datetime and kind_.time_zone}
        if not zoned or (kind not in OFFSET_TEXT_TYPES and kind not in NO_ZONE_TYPES):
            return frame
        names = ", ".join(f'"{name}"' for name in zoned)
        verb = "is" if len(zoned) == 1 else "are"
        zones = ", ".join(dict.fromkeys(zoned.values()))
        first, zone = next(iter(zoned.items()))
        if kind in NO_ZONE_TYPES:
            print(f"Note: {NO_ZONE_TYPES[kind]} has no time zones, so {names} {verb} saved in {file_name} as clock "
                  f"times on the {zones} clock, without the zone name. To save UTC times instead, first write "
                  f'table.change_time_zone_in("{first}", to="UTC").')
            # the clock times of the zone, read by Polars on both engines (simplydata._zone_clock)
            return _zone_clock.with_columns(self._frame, [nw.col(name).dt.replace_time_zone(None) for name in zoned],
                                            list(zoned))
        import polars as pl

        polars = frame.implementation.is_polars()
        for name in zoned:
            native = frame[name].to_native()
            text = (native if polars else pl.from_pandas(native)).dt.to_string(TIME_WITH_OFFSET)
            if not polars:
                text = text.to_pandas()
                text.index = native.index
            frame = frame.with_columns(nw.from_native(text, series_only=True).alias(name))
        example = frame.filter(~nw.col(first).is_null())[first]
        shown = f" ({example.item(0)})" if len(example) else ""
        print(f"Note: {names} {verb} saved in {file_name} as times with their UTC offset{shown}; the zone name "
              f"{zones} is not stored in a .{kind} file. sdata.table() reads them back as the same moments on the "
              f'UTC clock; table.change_time_zone_in("{first}", to="{zone}") puts them back on the {zone} clock.')
        return frame

    def _save_more(self, path, kind, frame):
        """The file types of the tables phase (P38), each written by pandas itself."""
        pandas_table = frame.to_pandas()
        try:
            if kind in ("csv.gz", "tsv.gz"):  # pandas to_csv: the .gz ending compresses it (gzip)
                pandas_table.to_csv(path, sep="\t" if kind == "tsv.gz" else ",", index=False, lineterminator=LINE_END)
            elif kind == "feather":
                pandas_table.to_feather(path)  # pandas to_feather
            elif kind == "jsonl":
                pandas_table.to_json(path, orient="records", lines=True)  # pandas to_json(lines=True)
            elif kind == "dta":
                import warnings

                with warnings.catch_warnings(record=True) as said:
                    warnings.simplefilter("always")
                    pandas_table.to_stata(path, write_index=False)  # pandas to_stata
                renamed = [line.strip() for w in said for line in str(w.message).splitlines() if "->" in line]
                if renamed:  # pandas' InvalidColumnName warning, said plainly
                    print("Note: Stata does not allow some of the column names, so pandas changed them in the file: "
                          + "; ".join(" ".join(line.split()) for line in renamed) + ".")
            else:
                pandas_table.to_html(path, index=False)  # pandas to_html
        except SimplydataError:
            raise
        except (ValueError, TypeError) as problem:  # Stata's rules on names and kinds, said plainly
            first = (str(problem).strip().splitlines() or [""])[0]
            raise SimplydataError(f'The table could not be saved as "{path.name}": {first}') from None

    def _save_for_paper(self, path, kind, frame):
        """.md (Polars' Markdown table), .tex (pandas to_latex) and .docx (python-docx): a finished table. Every cell
        is written as Polars writes it as text (30.5, 2026-03-01), and an empty cell is left blank."""
        import polars as pl

        native = frame.to_polars()
        numbers = [name for name, kind_ in native.schema.items() if kind_.is_numeric()]
        text = native.with_columns(pl.all().cast(pl.String).fill_null(""))  # one text for every cell, in every file
        if kind == "md":
            with pl.Config(tbl_formatting="MARKDOWN", tbl_hide_column_data_types=True, tbl_hide_dataframe_shape=True,
                           tbl_rows=-1, tbl_cols=-1, fmt_str_lengths=10_000, tbl_width_chars=-1):
                written = str(text)  # Polars writes the table in Markdown
            path.write_text(written + "\n", encoding="utf-8", newline="\n")
        elif kind == "tex":
            try:
                import jinja2  # noqa: F401 - pandas to_latex needs it
            except ImportError:
                raise SimplydataError('Saving a LaTeX table needs jinja2. Install it with:  pip install '
                                      '"simplydata[files]"') from None
            places = "".join("r" if name in numbers else "l" for name in native.columns)
            # pandas to_latex: a LaTeX tabular, numbers on the right, LaTeX's special signs escaped
            text.to_pandas().to_latex(path, index=False, column_format=places, escape=True)
        else:
            try:
                import docx
            except ImportError:
                raise SimplydataError('Saving a Word table needs python-docx. Install it with:  pip install '
                                      '"simplydata[files]"') from None
            document = docx.Document()
            table = document.add_table(rows=len(text) + 1, cols=len(text.columns))
            table.style = "Table Grid"
            for j, name in enumerate(text.columns):
                table.cell(0, j).text = str(name)
            for i, row in enumerate(text.iter_rows(), 1):
                for j, value in enumerate(row):
                    table.cell(i, j).text = value
            document.save(str(path))  # python-docx: one Word table, the column names in the first row
        print(f"Saved the table as {path.name}: {len(frame)} rows and {len(frame.columns)} columns (empty cells "
              "left blank).")

    def _save_to_clipboard(self):
        """table.save("clipboard"): pandas to_clipboard(excel=True), tabs between the values, to paste into Excel."""
        try:
            self._frame.to_pandas().to_clipboard(index=False, excel=True)  # pandas to_clipboard
        except Exception as problem:  # noqa: BLE001 - no clipboard program (a server, a Linux without xclip)
            raise SimplydataError("simplydata could not copy to the clipboard on this computer "
                                  f"({type(problem).__name__}). Save the table as a file instead, such as "
                                  'table.save("results.xlsx").') from None
        print(f"Copied the table to the clipboard: {len(self._frame)} rows and {len(self._frame.columns)} columns, "
              "ready to paste into Excel.")
        return self

    def _save_in_table(self, path, kind, in_table):
        """table.save("x.sqlite", in_table="river"): one table of a database file; the other tables are kept.

        SQLite: Python's sqlite3 and pandas to_sql(if_exists="replace"). DuckDB: CREATE OR REPLACE TABLE from the
        table, in a connection with no extensions and no other files (simplydata._sql)."""
        example = f'table.save("{path.name}", in_table="river")'
        if kind not in DATABASE_TYPES:
            raise SimplydataError(f"in_table= saves the table as one table of a database file (.sqlite, .db or "
                                  f".duckdb); a .{kind} file holds one table.\nFor example:  "
                                  f'table.save("{path.stem}.sqlite", in_table={in_table!r}), or '
                                  f'table.save("{path.name}") without in_table=.')
        if in_table is None:
            raise SimplydataError(f'"{path.name}" is a database, which holds tables by name. Say which with '
                                  f"in_table=.\nFor example:  {example}")
        if not isinstance(in_table, str) or not in_table.strip():
            raise SimplydataError(f"in_table= is the name of a table, in quotes.\nFor example:  {example}")
        if path.parent and not path.parent.exists():
            raise SimplydataError(f'The folder "{path.parent}" does not exist. Create it first.')
        pandas_table = self._frame.to_pandas()
        if kind == "duckdb":
            from .. import _sql

            con = _sql.connect(f'Saving "{path.name}"', database=str(path))
            try:
                there = [row[0] for row in con.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'").fetchall()]
                _same_but_capitals(path, in_table, there)
                con.register("_simplydata_table_", pandas_table)
                con.execute(f"CREATE OR REPLACE TABLE {_sql.quoted(in_table)} AS SELECT * FROM _simplydata_table_")
            finally:
                con.close()
        else:
            import sqlite3

            con = sqlite3.connect(path)
            try:
                try:
                    there = [row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
                except sqlite3.DatabaseError as problem:
                    raise SimplydataError(f'"{path.name}" exists but is not an SQLite database ({problem}), so '
                                          "simplydata cannot add a table to it. Save to a new file name.") from None
                _same_but_capitals(path, in_table, there)
                pandas_table.to_sql(in_table, con, if_exists="replace", index=False)  # pandas to_sql
                con.commit()
            finally:
                con.close()
        if in_table in there:
            print(f'Replaced the table "{in_table}" in {path.name}; the other tables are kept.')

    def _save_in_sheet(self, path, in_sheet, frame):
        """table.save("x.xlsx", in_sheet=...): pandas ExcelWriter with openpyxl, adding to the file if it exists.

        The sheet name is checked first with Excel's rules as openpyxl states them (its INVALID_TITLE_REGEX, its
        31-character warning, a name of at least one character) and Excel's own two (the reserved name "History" in any
        capitals, no apostrophe at the start or end), so a bad name never leaves a half-written file.
        """
        import pandas as pd
        from openpyxl.workbook.child import INVALID_TITLE_REGEX

        example = f'table.save("{path.name}", in_sheet="cleaned")'
        if not isinstance(in_sheet, str):
            raise SimplydataError(f"in_sheet= is the name of a sheet, in quotes: in_sheet=\"{in_sheet}\", "
                                  f"not {in_sheet!r}.\nFor example:  {example}")
        if not in_sheet.strip():
            raise SimplydataError(f"in_sheet= needs a name with at least one letter or digit.\nFor example:  {example}")
        bad = INVALID_TITLE_REGEX.search(in_sheet)
        if bad:
            raise SimplydataError(f'Excel does not allow "{bad.group(0)}" in a sheet name, and none of : \\ / ? * [ ]. '
                                  f'Try in_sheet="{INVALID_TITLE_REGEX.sub(" ", in_sheet).strip()}".')
        if len(in_sheet) > 31:
            raise SimplydataError(f'Excel allows at most 31 characters in a sheet name; "{in_sheet}" has '
                                  f'{len(in_sheet)}. Try in_sheet="{in_sheet[:31].strip()}".')
        if in_sheet.startswith("'") or in_sheet.endswith("'"):
            raise SimplydataError(f"Excel does not allow an apostrophe (') at the start or the end of a sheet name. "
                                  f"Try in_sheet=\"{in_sheet.strip(chr(39)).strip() or 'cleaned'}\".")
        if in_sheet.lower() == "history":
            raise SimplydataError(f'Excel keeps the sheet name "History" for itself (in any capitals), so '
                                  f'in_sheet="{in_sheet}" cannot be used. Try in_sheet="history of changes".')
        if not path.exists():
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                frame.to_pandas().to_excel(writer, sheet_name=in_sheet, index=False)
            return
        try:
            with pd.ExcelFile(path, engine="openpyxl") as book:
                sheets = [str(name) for name in book.sheet_names]
        except Exception:
            raise SimplydataError(f'"{path.name}" exists but simplydata cannot open it as an Excel file, so it cannot '
                                  f"add a sheet to it.\nSave to a new file name, or without in_sheet= to replace "
                                  f'the file:  table.save("{path.name}")') from None
        same_but_case = [name for name in sheets if name.lower() == in_sheet.lower() and name != in_sheet]
        if same_but_case:
            raise SimplydataError(f'"{path.name}" already has a sheet "{same_but_case[0]}", and Excel counts '
                                  f'"{in_sheet}" as the same name.\nTo replace that sheet: '
                                  f'table.save("{path.name}", in_sheet="{same_but_case[0]}"); or choose another name.')
        with pd.ExcelWriter(path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            frame.to_pandas().to_excel(writer, sheet_name=in_sheet, index=False)
        if in_sheet in sheets:
            print(f'Replaced the sheet "{in_sheet}" in {path.name}; the other sheets are kept.')

    # ------------------------------------------------------------------ looking words
    @friendly
    def show(self, rows=None):
        """Show the whole table, every row and column. table.show()

        rows=10 shows only the first 10 rows. A table with more than 1000 rows shows its
        first 1000; give rows= to see more. Try it: sdata.table(sdata.get_example("marks")).show()
        """
        total = len(self._frame)
        if rows is not None and (isinstance(rows, bool) or not isinstance(rows, int) or rows < 0):
            raise SimplydataError(
                f"rows= is how many rows to show: a whole number, not {rows!r}.\n"
                'For example:  sdata.table(sdata.get_example("marks")).show(rows=10)'
            )
        if rows is None:
            rows = min(total, SHOW_LIMIT)
            if total > SHOW_LIMIT:
                print(f"This table has {total} rows; showing the first {SHOW_LIMIT}. "
                      f"table.show(rows={total}) shows them all.")
        rows = min(rows, total)
        _show_whole(numbered(self._frame.head(rows)))
        if rows < total:
            print(f"Showing {rows} of {counted(total, 'row')}, {counted(len(self._columns), 'column')}.")
        else:
            print(f"{counted(total, 'row')}, {counted(len(self._columns), 'column')}.")
        return None

    @friendly
    def show_first_rows(self, rows=5):
        """Show the first rows, numbered from 1. table.show_first_rows(5)"""
        show(numbered(self._frame.head(int(rows))))
        return None

    @friendly
    def show_last_rows(self, rows=5):
        """Show the last rows, with their row numbers in the whole table. table.show_last_rows(5)

        The last 3 rows of a table of 54 rows are numbered 52, 53 and 54, the numbers that
        table.keep_rows_by_position(52, to=54) takes.
        """
        part = self._frame.tail(int(rows))
        show(numbered(part, len(self._frame) - len(part)))
        return None

    @friendly
    def get_column_names(self):
        """The names of all columns. table.get_column_names()"""
        return self._columns

    # ------------------------------------------------------------------ Python details
    def __len__(self):
        return len(self._frame)

    def __repr__(self):
        rows, cols = self._frame.shape
        survey = self.__dict__.get("_survey")
        mode = f" (a survey: {survey['said']})" if survey else ""
        return (f"simplydata table: {counted(rows, 'row')}, {counted(cols, 'column')}{mode}\n"
                f"{numbered(self._frame.head(10))!r}")

    def _repr_html_(self):
        """The table in Jupyter and VS Code, with rows numbered from 1 (as everywhere in simplydata)."""
        import pandas as pd

        total = len(self._frame)
        if self._frame.implementation.is_pandas() or total <= REPR_WHOLE_LIMIT:
            shown = numbered(self._frame)
        else:  # a big Polars table: only the rows a notebook shows are turned into pandas
            k = REPR_ENDS
            shown = pd.concat([numbered(self._frame.head(k)), numbered(self._frame.tail(k), total - k)])
        return shown._repr_html_()

    def __getitem__(self, key):
        raise PickingError(self._picking_help(key))

    def __iter__(self):
        raise PickingError(
            "A table is not gone through row by row with a loop: simplydata words work on every row at once.\n"
            "To look at one row write table.get_row(3) (rows count from 1); for one column, table.get_column(\"marks\")."
        )

    def _picking_help(self, key) -> str:
        """Why table[...] does not work, and the words that do (with the user's own column or rows)."""
        columns = self._columns
        lines = []
        if isinstance(key, str) and key in columns:
            lines.append(f'For the column "{key}" on its own write table.get_column("{key}").')
        elif isinstance(key, str):
            lines.append(self._gone_column_help(key))
        elif isinstance(key, (list, tuple)) and key and all(isinstance(k, str) for k in key):
            lines.append("To keep these columns write table.keep_columns("
                         + ", ".join(f'"{k}"' for k in key) + ").")
        elif isinstance(key, int) and not isinstance(key, bool) and key >= 0:
            lines.append(f"In Python [{key}] is row {key + 1} counting from 1: table.get_row({key + 1}) shows it.")
        elif isinstance(key, int) and key == -1:
            lines.append('In Python [-1] is the last row: table.get_row("last") shows it.')
        elif isinstance(key, slice) and key.step in (None, 1) and all(
                v is None or (isinstance(v, int) and not isinstance(v, bool) and v >= 0) for v in (key.start, key.stop)):
            first = (key.start or 0) + 1
            last = "last" if key.stop is None else key.stop
            if last == "last" or last >= first:
                shown = '"last"' if last == "last" else last
                lines.append(f"In Python [{_slice_text(key)}] means rows {first} to {last} counting from 1: "
                             f"table.keep_rows_by_position({first}, to={shown}).")
        lines.append(
            'Parts of a table are chosen with words, and positions count from 1:\n'
            '    table.get_column("marks")                     one column, as numbers\n'
            '    table.keep_columns("name", "marks")       some columns\n'
            '    table.keep_rows_where("marks > 50")             rows that meet a condition\n'
            '    table.keep_rows_by_position(10, to=20)    rows 10 to 20\n'
            '    table.get_cell_at(row=3, column="marks")      one cell\n'
            "Python's [ ] counts from 0, so simplydata does not use it. For a pandas table, use table.as_pandas()."
        )
        return "\n".join(lines)

    def _gone_column_help(self, key: str) -> str:
        """table["marks"] for a column the table does not have now: which step took it away (each step changes the
        table itself), how to get it back, and the columns there are now."""
        columns = self._columns
        now = ", ".join(map(str, columns))
        later = list(columns)
        for what, before in reversed(self._history):
            if key in before.columns and key not in later:
                return (f'The table has no column "{key}" now: the step "{what}" changed the table and "{key}" is '
                        "not in it any more (each step changes the table itself).\n"
                        "table.undo() takes the last step back, and table.show_steps() lists the steps. "
                        f'Then the column on its own is table.get_column("{key}").\n'
                        f"Columns you have now: {now}")
            later = list(before.columns)
        guess = suggest(key, columns, n=1)
        return (f'There is no column "{key}".' + (f' Did you mean table.get_column("{guess[0]}")?' if guess else "")
                + f"\nColumns you have: {now}")

    def _repeated_rows_note(self, word, params, args, kwargs) -> str:
        """The note when an ID column repeats in a test that takes rows as independent (table/_independence.py)."""
        from ._independence import repeated_rows_note

        return repeated_rows_note(self._frame, word, params, args, kwargs)

    @classmethod
    def _word_names(cls) -> list[str]:
        return sorted(n for n in dir(cls) if not n.startswith("_") and callable(getattr(cls, n)))

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        if name in self._OLD_WORDS:
            return old_word(self, name, self._OLD_WORDS)
        frame = self.__dict__.get("_frame")
        if frame is not None and name in frame.columns:
            if frame.schema[name].is_numeric():
                what, rows = "its numbers", f'table.keep_rows_where("{name} > 50")'
            else:
                what, rows = "its values", f'table.keep_rows_where("{name}", is_equal_to="...")'
            raise MissingWordError(
                f'{name} is a column. For {what} write table.get_column("{name}"); to choose rows write {rows}.\n'
                "Columns are named in quotes inside a word, never after a dot."
            )
        raise other_name_error("table", name, self._word_names()) or missing_word_error(name, self._word_names())

    def __setattr__(self, name, value):
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        guesses = suggest(name, self._word_names())
        hint = f"table.{guesses[0]}(...)" if guesses else 'a step such as table.rename_column("old", to="new")'
        raise SimplydataError(f"Steps are written with brackets, not with =.\nInstead of table.{name} = ..., write {hint}")


def _same_but_capitals(path, in_table, there) -> None:
    """SQLite and DuckDB take "River" and "river" as the same table: replacing it under other capitals is refused,
    so that a table is never replaced without the note that says so."""
    found = [name for name in there if name.lower() == in_table.lower() and name != in_table]
    if found:
        raise SimplydataError(
            f'"{path.name}" already has a table "{found[0]}", and the database counts "{in_table}" as the same name '
            f"(capital letters do not matter in table names).\nTo replace that table:  "
            f'table.save("{path.name}", in_table="{found[0]}"); or choose another name.')


def _independent_native(native):
    """A pandas or Polars table that shares nothing a later change could reach (bookkeeping, no computation).

    pandas 3 copies on change (copy-on-write), so a shallow copy is independent and costs nothing; pandas 2
    needs a deep copy. Polars clone() shares the column data, which Polars never changes in place."""
    module = type(native).__module__.split(".")[0]
    if module == "pandas":
        import pandas as pd

        return native.copy(deep=int(pd.__version__.split(".")[0]) < 3)
    if module == "polars" and hasattr(native, "clone"):
        return native.clone()
    return native


def _independent(frame):
    """_independent_native() for a narwhals frame."""
    return nw.from_native(_independent_native(frame.to_native()), eager_only=True)
