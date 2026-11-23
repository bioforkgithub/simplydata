"""The heart of simplydata tables.

A table holds its data in a narwhals frame, so every word is written once and runs on
both pandas (normal files) and Polars (big files, Polars tables, fast=True).

Every step that changes the table goes through self._change(...), which remembers the
table as it was before. That gives undo(), show_steps() and start_again() for free.
Summaries never change the table; they return a new, small table.
"""

from __future__ import annotations

from pathlib import Path

import narwhals as nw

from .._data import load_native
from .._errors import (MissingWordError, SimplydataError, choice_error, column_error, friendly, missing_word_error,
                       old_word, other_name_error, suggest)

HISTORY_LIMIT = 30  # how many steps undo() can take back
SHOW_LIMIT = 1000  # table.show() with no rows= shows at most this many rows
REPR_WHOLE_LIMIT = 10_000  # a Polars table up to this size is shown whole in notebooks
REPR_ENDS = 30  # a bigger one shows this many rows from the start and the end
SAVE_TYPES = ("csv", "tsv", "xlsx", "parquet", "json")


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
    }

    def __init__(self, data=None, sheet=None, fast: bool = False, _frame=None, _reading=None):
        if _frame is None:
            native = load_native(data, sheet=sheet, fast=fast, options=_reading)
            if fast and type(native).__module__.split(".")[0] == "pandas":
                try:
                    import polars as pl
                except ImportError:
                    raise SimplydataError(
                        "fast=True needs the fast engine.\nInstall it with:  pip install simplydata[fast]"
                    ) from None
                native = pl.from_pandas(native)
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
    def undo(self):
        """Take the last step back. table.undo()"""
        if not self._history:
            print("Nothing to undo: this table has no steps yet.")
            return self
        what, before = self._history.pop()
        object.__setattr__(self, "_frame", before)
        print(f"Undone: {what}")
        return self

    @friendly
    def show_steps(self):
        """List every step you did to this table, in order. table.show_steps()"""
        if not self._history:
            print("No steps yet.")
        else:
            for i, (what, _) in enumerate(self._history, 1):
                print(f"{i}. {what}")
        return self

    @friendly
    def start_again(self):
        """Go back to the table as it was at the start. table.start_again()"""
        return self._change("start again", self._original)

    # ------------------------------------------------------------------ finishing words
    @friendly
    def as_pandas(self):
        """Give back the table as a plain pandas table, for other Python tools. df = table.as_pandas()

        Only needed when another library wants pandas: simplydata words never need it.
        """
        return self._frame.to_pandas()

    @friendly
    def as_polars(self):
        """Give back the table as a plain Polars table, for other Python tools. df = table.as_polars()

        Needs Polars (pip install simplydata[fast]). simplydata words never need it.
        """
        try:
            import polars  # noqa: F401
        except ImportError:
            raise SimplydataError(
                "as_polars() needs Polars, the fast engine.\n"
                "Install it with:  pip install simplydata[fast]\n"
                "Or use table.as_pandas() to get a pandas table instead."
            ) from None
        return self._frame.to_polars()

    def _done(self):
        """The old done(): the table as it is stored (pandas, or Polars for Polars tables)."""
        return self._frame.to_native()

    @friendly
    def start_chart(self):
        """Start a chart from this table. chart = table.start_chart()"""
        from ..chart import chart

        return chart(self)

    @friendly(others={"sheet_name": "in_sheet", "sheetName": "in_sheet"})
    def save(self, file_name, in_sheet=None):
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
        : \\ / ? * [ ], and Excel counts "Cleaned" and "cleaned" as the same name.

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
        """
        path = Path(file_name)
        kind = path.suffix.lower().lstrip(".")
        if not kind:
            raise SimplydataError(
                f'Add a file type to the name, for example "{path.name}.xlsx" or "{path.name}.csv".'
            )
        if kind not in SAVE_TYPES:
            raise choice_error("save", "file type", kind, SAVE_TYPES)
        if in_sheet is not None and kind != "xlsx":
            raise SimplydataError(
                f"in_sheet= saves the table as one sheet of an Excel file. Only .xlsx files have sheets; "
                f"a .{kind} file holds one table.\n"
                f'For example:  table.save("{path.stem}.xlsx", in_sheet={in_sheet!r}), '
                f'or table.save("{path.name}") without in_sheet=.'
            )
        if path.parent and not path.parent.exists():
            raise SimplydataError(f'The folder "{path.parent}" does not exist. Create it first.')
        if in_sheet is not None:
            self._save_in_sheet(path, in_sheet)
            return self
        if kind == "csv":
            self._frame.write_csv(str(path))
        elif kind == "parquet":
            self._frame.write_parquet(str(path))
        else:
            pandas_table = self._frame.to_pandas()
            if kind == "tsv":
                pandas_table.to_csv(path, sep="\t", index=False)
            elif kind == "xlsx":
                pandas_table.to_excel(path, index=False)
            else:
                pandas_table.to_json(path, orient="records", indent=2)
        return self

    def _save_in_sheet(self, path, in_sheet):
        """table.save("x.xlsx", in_sheet=...): pandas ExcelWriter with openpyxl, adding to the file if it exists.

        The sheet name is checked first with Excel's rules as openpyxl states them (its INVALID_TITLE_REGEX, its
        31-character warning, a name of at least one character), so a bad name never leaves a half-written file.
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
        if not path.exists():
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                self._frame.to_pandas().to_excel(writer, sheet_name=in_sheet, index=False)
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
            self._frame.to_pandas().to_excel(writer, sheet_name=in_sheet, index=False)
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
            print(f"Showing {rows} of {total} rows, {len(self._columns)} columns.")
        else:
            print(f"{total} rows, {len(self._columns)} columns.")
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
        return f"simplydata table: {rows} rows, {cols} columns{mode}\n{numbered(self._frame.head(10))!r}"

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
            guess = suggest(key, columns, n=1)
            lines.append(f'There is no column "{key}".' + (f' Did you mean table.get_column("{guess[0]}")?' if guess else ""))
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
