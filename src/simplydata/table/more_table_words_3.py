"""Tables phase, batch 3: the less frequent table jobs (ranks 31-44, approved by Manish 2026-11-25).

  add_zeros_in_front_of              "7" becomes "007" (pandas and Polars str.zfill)
  move_columns                       put columns at the start, at the end or after another column
  show_rows_with_empty_cells_in      look at the rows with a hole before removing or filling them
  show_differences_from              the cells that differ between two tables (pandas compare)
  check_if_same_as                   are two tables the same? (pandas equals, Polars equals)
  run_sql                            an SQL query on the table, which the query calls data (DuckDB)
  make_one_table_for_each_group_in   one table for each group (pandas groupby, Polars partition_by)
  as_list                            one dict per row, for plain Python (to_dict("records"), to_dicts())

and the join_with options match= / within= (pandas merge_asof, Polars join_asof) and keep="every combination"
(a cross join), which join_with hands to this file.

Every word passes straight through to pandas, Polars or DuckDB (PLAN.md section 7); the comment at each call names
it. Each word works on pandas and Polars tables alike, and says what it did.
"""

from __future__ import annotations

import datetime
import re
from typing import TYPE_CHECKING

import narwhals as nw

from .._errors import SimplydataError, choice_error, friendly
from .._typing import _Same
from ._base import SHOW_LIMIT, counted, numbered_at
from ._base import show as _show_native
from .columns import JOIN_SUFFIX, _as_list
from .conditions import _rows

if TYPE_CHECKING:
    from .table import Table

MOVE_TO = ("start", "end")
# join_with(match=): pandas merge_asof(direction=) and Polars join_asof(strategy=)
MATCH_CHOICES = {"nearest before": "backward", "nearest after": "forward", "nearest": "nearest"}
# join_with(within="2 days"): the units of a time limit, as Python's datetime.timedelta takes them
_WITHIN_UNITS = ("second", "minute", "hour", "day", "week")
DIFFERENCES_SHOWN = 50  # show_differences_from shows at most this many cells; the sentence gives the count


def _example(code: str, name: str | None = None) -> str:
    table = f'   (with sdata.get_example("{name}"))' if name else ""
    return f"\nFor example:  {code}{table}"


def _names_list(names) -> str:
    names = [str(n) for n in names]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def _within_limit(within, numbers: bool, example: str):
    """within= as the parent packages take it: a datetime.timedelta for dates ("2 days"), a number for numbers."""
    if numbers:
        if isinstance(within, bool) or not isinstance(within, (int, float)) or within < 0:
            raise SimplydataError("within= is the biggest distance allowed between the two values: a number of 0 or "
                                  f"more, as the column holds numbers.{example}")
        return within
    found = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(" + "|".join(_WITHIN_UNITS) + r")s?\s*", str(within).lower()) \
        if isinstance(within, str) else None
    if not found:
        raise SimplydataError(
            f'within= is the longest time allowed between the two dates, as text: "2 days", "12 hours", '
            f'"30 minutes" or "1 week" (not {within!r}).{example}'
        )
    return datetime.timedelta(**{found.group(2) + "s": float(found.group(1))})


def _common_kind(pl, here, there, key):
    """One Polars kind for a key in both tables: decimals when either holds decimals, a time when either holds a
    time (both in UTC when both say a time zone), or the kind they share. Other mixes are refused."""
    def temporal(t):
        return t == pl.Date or isinstance(t, pl.Datetime)

    if here == there:
        return here
    if here.is_numeric() and there.is_numeric():
        return pl.Float64 if (here.is_float() or there.is_float()) else pl.Int64
    if temporal(here) and temporal(there):
        zones = {t.time_zone if isinstance(t, pl.Datetime) else None for t in (here, there)}
        if len(zones) > 1 and None in zones:
            raise SimplydataError(f'"{key}" has a time zone in one table and none in the other, so the times cannot be '
                                  "matched. Give both the same time zone first.")
        return pl.Datetime("us", "UTC" if zones - {None} else None)
    raise SimplydataError(f'"{key}" holds {here} values in this table and {there} values in the other table, so no '
                          "rows can match. Make them the same kind first (turn_into_numbers, turn_into_text or "
                          "turn_into_dates).")


def _as_kind(pl, name, kind_now, kind):
    """The column as the common kind (Polars cast; a time with a zone is changed to UTC first)."""
    col = pl.col(name)
    if kind_now == kind:
        return col
    if isinstance(kind, pl.Datetime) and kind.time_zone == "UTC" and isinstance(kind_now, pl.Datetime):
        return col.dt.convert_time_zone("UTC").cast(kind)
    return col.cast(kind)


def _cell(value):
    """A cell as Python gives it, with an empty cell as None (bookkeeping for the printed tables)."""
    if value is None:
        return None
    try:
        if value != value:  # NaN, NaT
            return None
    except (TypeError, ValueError):
        pass
    return value.item() if hasattr(value, "item") else value


class MoreTableWordsThree:
    # ================================================================== text
    @friendly(others={"width": "to_length", "length": "to_length"})
    def add_zeros_in_front_of(self: _Same, column=None, to_length=None) -> _Same:
        """Add zeros in front of the text in a column until it has a length: "7" becomes "007".

        table.add_zeros_in_front_of("sample_id", to_length=3)   (with sdata.get_example("fjord_samples"))
        Sample IDs typed as 7 in one file and 007 in another then match in a join. A longer text
        is never cut ("1234" stays "1234"), the sentence says how many there were, and an empty
        cell stays empty. A minus or plus sign stays in front ("-7" becomes "-07"). It works on
        text: a column of numbers is first made text with turn_into_text("sample_id"). As pandas
        str.zfill(3) and Polars str.zfill(3); other filling characters: pandas str.pad.
        """
        step = "add_zeros_in_front_of"
        example = _example(f'table.{step}("sample_id", to_length=3)', "fjord_samples")
        if not isinstance(column, str):
            raise SimplydataError(f".{step}() needs the column name in quotes first." + example)
        self._need_columns(column)
        if isinstance(to_length, bool) or not isinstance(to_length, int) or to_length < 1:
            raise SimplydataError(f"to_length= is how many characters each value should have at least: a whole "
                                  f"number such as 3 (not {to_length!r})." + example)
        kind = self._kind_of(column)
        if kind != "text":
            hint = (f' Make it text first: table.turn_into_text("{column}"), then add the zeros.'
                    if kind == "number" else "")
            raise SimplydataError(f'.{step}() works on text, but "{column}" holds {kind} values.{hint}' + example)
        text = nw.col(column).cast(nw.String)
        length = text.str.len_chars()
        shorter = self._count(length < to_length)
        longer = self._count(length > to_length)
        # pandas Series.str.zfill(3), Polars Expr.str.zfill(3)
        frame = self._frame.with_columns(text.str.zfill(to_length).alias(column))
        said = f" {longer} {'value has' if longer == 1 else 'values have'} more than {to_length} characters and " \
               f"{'was' if longer == 1 else 'were'} not cut." if longer else ""
        print(f'Added zeros in front of "{column}" so that each value has at least {to_length} characters: '
              f"{shorter} {'value' if shorter == 1 else 'values'} changed.{said}")
        return self._change(f'add zeros in front of "{column}" (to length {to_length})', frame)

    # ================================================================== columns
    @friendly
    def move_columns(self: _Same, *names, to=None, after=None) -> _Same:
        """Move columns to the start or the end of the table, or after another column.

        table.move_columns("marks", to="start")   (with sdata.get_example("marks"))
        to="start" (also without to=) puts them first, in the order you list them; to="end" puts
        them last; after="name" puts them just after that column. The other columns keep their
        order, and no value changes. As pandas df[[...new order...]] and Polars df.select([...]);
        R dplyr relocate().
        """
        step = "move_columns"
        example = _example(f'table.{step}("marks", to="start")', "marks")
        chosen = list(dict.fromkeys(_as_list(list(names))))
        if not chosen or not all(isinstance(n, str) for n in chosen):
            raise SimplydataError(f".{step}() needs the names of the columns to move, in quotes." + example)
        self._need_columns(*chosen)
        if to is not None and after is not None:
            raise SimplydataError(f".{step}() takes to= or after=, not both." + example)
        rest = [c for c in self._columns if c not in chosen]
        if after is not None:
            if not isinstance(after, str):
                raise SimplydataError("after= is the name of the column the moved columns go after, in quotes."
                                      + _example(f'table.{step}("marks", after="name")', "marks"))
            self._need_columns(after)
            if after in chosen:
                raise SimplydataError(f'"{after}" is one of the columns being moved, so they cannot go after it.')
            at = rest.index(after) + 1
            order, where = rest[:at] + chosen + rest[at:], f'after "{after}"'
        else:
            to = "start" if to is None else to
            if to not in MOVE_TO:
                raise choice_error(step, "to", to, list(MOVE_TO))
            order = chosen + rest if to == "start" else rest + chosen
            where = f"to the {to}"
        # pandas df[order], Polars df.select(order)
        frame = self._frame.select(order)
        moved = ", ".join(f'"{c}"' for c in chosen)
        print(f"Moved {moved} {where}. The columns are now: {', '.join(map(str, order))}.")
        return self._change(f"move {', '.join(map(str, chosen))} {where}", frame)

    # ================================================================== looking at empty cells
    @friendly(others={"subset": "columns", "column": "columns"})
    def show_rows_with_empty_cells_in(self, columns=None):
        """Show the rows that have an empty cell, each with its row number (the table does not change).

        table.show_rows_with_empty_cells_in()   (with sdata.get_example("shop"))
        Without columns= a row is shown when any of its cells is empty; with columns= only an empty
        cell in those columns counts: table.show_rows_with_empty_cells_in(columns=["sales"]). An empty
        cell is a missing value or text of only spaces, as everywhere in simplydata (pandas
        df[df.isna().any(axis=1)], Polars df.filter(pl.any_horizontal(pl.all().is_null()))). Look
        first, then remove (remove_rows_with_empty_cells_in) or fill (fill_empty_cells_in).
        """
        step = "show_rows_with_empty_cells_in"
        if columns is None:
            names = list(self._columns)
        else:
            names = [columns] if isinstance(columns, str) else _as_list([columns])
            if not names or not all(isinstance(c, str) for c in names):
                raise SimplydataError("columns= needs one or more column names."
                                      + _example(f'table.{step}(columns=["sales"])', "shop"))
            self._need_columns(*names)
        within = "" if columns is None else f" in {', '.join(map(str, names))}"
        any_empty = nw.any_horizontal(*[self._empty(c) for c in names], ignore_nulls=True).fill_null(False)
        place = "_simplydata_place_"
        found = self._frame.with_row_index(place).filter(any_empty)
        if not len(found):
            print(f"No row has an empty cell{within} ({_rows(len(self._frame))}).")
            return None
        positions = found[place].to_list()
        found = found.drop(place)
        print(f"{_rows(len(found))} of {len(self._frame)} {'has' if len(found) == 1 else 'have'} an empty "
              f"cell{within}:")
        shown = min(len(found), SHOW_LIMIT)
        _show_native(numbered_at(nw.maybe_reset_index(found.head(shown)), positions[:shown]))
        if shown < len(found):
            print(f"Showing the first {shown}.")
        code = "" if columns is None else f"columns={names!r}".replace("'", '"')
        print(f"table.remove_rows_with_empty_cells_in({code}) removes them; fill_empty_cells_in fills a column.")
        return None

    # ================================================================== two tables side by side
    def _two_pandas(self, other, step):
        """This table and the other one as pandas tables (the other in this table's engine first)."""
        there = self._other_frame(other, step)
        return self._frame.to_pandas(), there.to_pandas(), there

    @staticmethod
    def _shape_difference(here, there) -> str:
        """The first way two tables differ in their shape (columns, their order, rows); empty when the same."""
        cols, others = [str(c) for c in here.columns], [str(c) for c in there.columns]
        if cols != others:
            only_here = [c for c in cols if c not in others]
            only_there = [c for c in others if c not in cols]
            if not only_here and not only_there:
                return ("they have the same columns in another order. This table: " + ", ".join(cols)
                        + "; the other: " + ", ".join(others) + ". move_columns puts them in order.")
            parts = []
            if only_here:
                parts.append("only this table has " + ", ".join(f'"{c}"' for c in only_here))
            if only_there:
                parts.append("only the other table has " + ", ".join(f'"{c}"' for c in only_there))
            return "they have different columns: " + "; ".join(parts) + "."
        if len(here) != len(there):
            return f"this table has {_rows(len(here))} and the other {_rows(len(there))}."
        return ""

    @staticmethod
    def _cell_differences(here, there):
        """pandas compare(): every cell that differs, as (row from 1, column, this value, other value)."""
        # pandas DataFrame.compare(other, result_names=("this", "other")): differing cells only; two empty cells
        # are the same
        found = here.reset_index(drop=True).compare(there.reset_index(drop=True), result_names=("this", "other"))
        cells = []
        if found.empty:
            return cells
        columns = [c for c in here.columns if c in set(found.columns.get_level_values(0))]
        for row in found.index:
            for column in columns:
                this, that = _cell(found.at[row, (column, "this")]), _cell(found.at[row, (column, "other")])
                if this is not None or that is not None:
                    cells.append((int(row) + 1, column, this, that))
        return cells

    @friendly(others={"other_table": "other"})
    def show_differences_from(self, other=None):
        """Show the cells that differ between this table and another one, as row, column, this, other.

        table.show_differences_from(sdata.get_example("marks"))   (with sdata.get_example("marks"))
        Handy after cleaning: cleaned.show_differences_from(original) lists every cell that a step
        changed, and nothing else. Rows are compared in order (row 3 with row 3), so both tables
        need the same columns and the same number of rows; when they differ, simplydata says how.
        Two empty cells count as the same. As pandas this.compare(other) (Polars tables go through
        pandas compare). The table does not change. check_if_same_as() only answers same or not.
        """
        step = "show_differences_from"
        here, there, _ = self._two_pandas(other, step)
        shape = self._shape_difference(here, there)
        if shape:
            print(f"The tables cannot be compared cell by cell: {shape}")
            return None
        cells = self._cell_differences(here, there)
        if not cells:
            print(f"No cell differs: both tables have the same {_rows(len(here))} and "
                  f"{counted(len(here.columns), 'column')}, "
                  "with the same values.")
            return None
        import pandas as pd

        rows = len({c[0] for c in cells})
        print(f"{len(cells)} {'cell differs' if len(cells) == 1 else 'cells differ'}, in {_rows(rows)} "
              f"(rows counted from 1; empty cells shown as None):")
        shown = pd.DataFrame(cells[:DIFFERENCES_SHOWN], columns=["row", "column", "this", "other"], dtype=object)
        _show_native(shown.set_index("row"))
        if len(cells) > DIFFERENCES_SHOWN:
            print(f"Showing the first {DIFFERENCES_SHOWN} of {len(cells)}.")
        return None

    @friendly(others={"other_table": "other"})
    def check_if_same_as(self, other=None) -> bool:
        """Check whether this table and another one are the same: it says so, or names the first difference.

        table.check_if_same_as(sdata.get_example("marks"))   (with sdata.get_example("marks"))
        Gives back True or False, so it also works in an if. The same means the same columns in
        the same order, the same rows in the same order, the same values (two empty cells count as
        the same) and the same kinds (whole numbers and decimals are different kinds). As pandas
        df.equals(other) and Polars df.equals(other). show_differences_from() lists every
        differing cell.
        """
        step = "check_if_same_as"
        there = self._other_frame(other, step)
        here_native, there_native = self._frame.to_native(), there.to_native()
        # pandas DataFrame.equals, Polars DataFrame.equals (two empty cells are equal in both); the kinds of the
        # columns are compared too, as pandas equals does (Polars equals leaves them out)
        same = bool(here_native.equals(there_native)) and self._frame.schema == there.schema
        if same:
            print(f"The tables are the same: {_rows(len(self._frame))}, {counted(len(self._columns), 'column')}, "
                  "every cell "
                  "equal.")
            return True
        here, other_pandas = self._frame.to_pandas(), there.to_pandas()
        shape = self._shape_difference(here, other_pandas)
        if shape:
            print(f"The tables are not the same: {shape}")
            return False
        cells = self._cell_differences(here, other_pandas)
        if cells:
            row, column, this, that = cells[0]
            more = f" ({len(cells)} cells differ; show_differences_from lists them)" if len(cells) > 1 else ""
            print(f'The tables are not the same: the first difference is in row {row}, column "{column}": {this!r} '
                  f"here, {that!r} in the other table{more}.")
            return False
        kinds = [str(c) for c in self._columns if self._frame.schema[c] != there.schema[c]]
        if kinds:
            column = kinds[0]
            print(f'The tables are not the same: the values are equal, but "{column}" holds '
                  f"{self._frame.schema[column]} values here and {there.schema[column]} values in the other table "
                  "(for example whole numbers and decimals).")
        else:
            print("The tables are not the same, although every cell is equal (the row labels of the pandas tables "
                  "differ).")
        return False

    # ================================================================== SQL
    @friendly(others={"sql": "query"})
    def run_sql(self, query=None) -> Table:
        """Run an SQL query on the table, which the query calls data, and give back its answer as a new table.

        table.run_sql("SELECT station, avg(nitrate) AS nitrate FROM data GROUP BY station")   (with sdata.get_example("river"))
        Inside the query the table is called data; a column with spaces goes in double quotes
        ("max temp"). The table itself does not change. The query runs in DuckDB, an optional extra
        (pip install "simplydata[sql]", or conda install -c conda-forge python-duckdb): DuckDB
        con.register("data", df) and con.sql(query).df(), or .pl() for a Polars table. The query may
        only read (one SELECT); it can never open a file or a web address, install anything or
        write a file, so the data stay on this computer.
        Files, without a table first: sdata.run_sql("SELECT ... FROM 'river.csv'").
        """
        from .. import _sql

        example = 'table.run_sql("SELECT station, avg(nitrate) AS nitrate FROM data GROUP BY station")'
        polars = self._frame.implementation.is_polars()
        native = self._frame.to_native()
        con = _sql.connect("table.run_sql()")  # a plain error with the install line when DuckDB is missing
        try:
            _sql.check_query(con, query, example)
            con.register("data", native)  # DuckDB con.register("data", df)
            answer = _sql.run(con, query, example, polars)  # con.sql(query).df() / .pl()
        finally:
            con.close()
        result = self._new_table(nw.from_native(answer, eager_only=True))
        rows, cols = result._frame.shape
        print(f"Ran the query with DuckDB on this table (called data in the query): {_rows(rows)}, "
              f"{cols} column{'s' if cols != 1 else ''}.")
        return result

    # ================================================================== one table for each group
    @friendly(others={"by": "column", "for_each_group_in": "column"})
    def make_one_table_for_each_group_in(self, column=None) -> dict:
        """Make one table for each group of a column, and give them back together: tables["Station A"].

        tables = table.make_one_table_for_each_group_in("station")   (with sdata.get_example("river"))
        Each table has the rows of one group, in their order, and every column; the first table
        is the group seen first. Get one with tables["Station A"], and go through them with
        for name, part in tables.items(). With two columns, make_one_table_for_each_group_in(
        ["station", "year"]), each key is a pair: tables[("Station A", 2024)]. Rows with an empty
        cell in the column make a group of their own, tables[None]. As pandas
        {name: part for name, part in df.groupby("station", sort=False, dropna=False)} and Polars
        df.partition_by("station", maintain_order=True, as_dict=True). The table itself does not change.
        """
        step = "make_one_table_for_each_group_in"
        example = _example(f'tables = table.{step}("station")', "river")
        names = [column] if isinstance(column, str) else _as_list([column]) if column is not None else []
        if not names or not all(isinstance(c, str) for c in names):
            raise SimplydataError(f".{step}() needs the column whose groups make the tables, in quotes." + example)
        self._need_columns(*names)
        native = self._frame.to_native()
        parts = {}
        if self._frame.implementation.is_polars():
            # Polars df.partition_by(columns, maintain_order=True, as_dict=True)
            for key, part in native.partition_by(names, maintain_order=True, as_dict=True).items():
                parts[key[0] if len(names) == 1 else tuple(key)] = part
        else:
            # pandas df.groupby(columns, sort=False, dropna=False): groups in the order they are first seen
            by = names[0] if len(names) == 1 else names
            for key, part in native.groupby(by, sort=False, dropna=False):
                key = _cell(key) if len(names) == 1 else tuple(_cell(k) for k in key)
                parts[key] = part.reset_index(drop=True)
        tables = {key: self._new_table(nw.from_native(part, eager_only=True)) for key, part in parts.items()}
        what = " and ".join(map(str, names))
        listed = [f"{key} ({_rows(len(t))})" for key, t in list(tables.items())[:10]]
        more = f" ... and {len(tables) - 10} more" if len(tables) > 10 else ""
        first = next(iter(tables), None)
        get = f"tables[{first!r}]".replace("'", '"')
        print(f"{len(tables)} table{'s' if len(tables) != 1 else ''}, one for each {what}: {', '.join(listed)}{more}. "
              f"Get one with {get}.")
        return tables

    # ================================================================== hand-off
    @friendly
    def as_list(self) -> list:
        """Give back the table as a list with one dict per row, for plain Python. rows = table.as_list()

        rows[0] is the first row, as {"name": "Asha", "class": "A", ...}; rows[0]["marks"] is one
        cell. Only needed for code outside simplydata: simplydata words never need it. It is a
        copy, as as_pandas() is. As pandas df.to_dict("records") and Polars df.to_dicts().
        Empty cells are None in a Polars table and nan (or None) in a pandas table.
        """
        native = self._frame.to_native()
        if self._frame.implementation.is_polars():
            return native.to_dicts()  # Polars DataFrame.to_dicts()
        return native.to_dict("records")  # pandas DataFrame.to_dict("records")

    # ================================================================== join_with: nearest rows and every combination
    def _join_every_combination(self, other, using):
        """join_with(keep="every combination"): pandas merge(how="cross"), Polars join(how="cross")."""
        if using is not None:
            raise SimplydataError('keep="every combination" pairs every row with every row, so it takes no using=.'
                                  + _example('table.join_with(other, keep="every combination")'))
        right = self._other_frame(other, "join_with")
        # pandas merge(how="cross", suffixes=("", "_other")), Polars join(how="cross", suffix="_other")
        frame = self._frame.join(right, how="cross", suffix=JOIN_SUFFIX)
        print(f"Every row with every row: {len(self._frame)} x {len(right)} = {_rows(len(frame))}.")
        return self._change("join with another table (keep every combination)", frame)

    def _join_nearest(self, other, using, keep, match, within, check_that, with_match_column):
        """join_with(match="nearest before", within="2 days"): Polars join_asof, for pandas and Polars tables alike.

        A pandas table goes through Polars and comes back as pandas (as show_differences_from goes through pandas
        compare), so both engines give the same rows: pandas merge_asof breaks ties and pairs empty keys in other
        ways. Both tables are sorted stably by the key first, and the rows go back to this table's order."""
        step = "join_with"
        example = _example('river.join_with(rain, using="date", match="nearest before", within="2 days")')
        if match not in MATCH_CHOICES:
            raise choice_error(step, "match", match, list(MATCH_CHOICES))
        if keep not in ("matching rows", "all rows from this table"):
            raise SimplydataError(f'match="{match}" keeps the rows of this table: keep="all rows from this table" '
                                  f'(every row, empty cells when nothing is near enough) or keep="matching rows" (the '
                                  f'normal choice).' + example)
        if check_that is not None or with_match_column:
            raise SimplydataError(f'match="{match}" finds one row for each row, so check_that= and '
                                  "with_match_column= are not needed with it." + example)
        import polars as pl

        right, keys, said = self._nearest_other(other, using, step)
        on, by = keys[-1], keys[:-1]
        kind_here, kind_there = self._frame.schema[on], right.schema[on]
        numbers = kind_here.is_numeric() and kind_there.is_numeric()
        dates = all(k == nw.Date or isinstance(k, nw.Datetime) for k in (kind_here, kind_there))
        if not (dates or numbers):
            raise SimplydataError(f'match="{match}" looks for the nearest value, so "{on}" must hold dates or numbers '
                                  "in both tables (turn_into_dates makes text into dates)." + example)
        tolerance = None if within is None else _within_limit(within, numbers, example)
        for side, frame in (("this table", self._frame), ("the other table", right)):
            empty = self._count_rows_where(frame, nw.col(on).is_null())
            if empty:
                raise SimplydataError(f'{_rows(empty).capitalize()} of {side} {"has" if empty == 1 else "have"} an '
                                      f'empty "{on}", which has no nearest value. Remove '
                                      f'{"it" if empty == 1 else "them"} first: '
                                      f'remove_rows_with_empty_cells_in("{on}").')
        index, mark = "_simplydata_row_", "_simplydata_found_"
        other_on = f"{on}{JOIN_SUFFIX}"
        if other_on in self._columns:
            raise SimplydataError(f'The table already has a column "{other_on}". Rename it first (rename_column).')
        pandas_table = not self._frame.implementation.is_polars()
        here = pl.from_pandas(self._frame.to_pandas()) if pandas_table else self._frame.to_native()
        there = right.to_native() if right.implementation.is_polars() else pl.from_pandas(right.to_pandas())
        # the keys as one kind in both tables (whole numbers and decimals as decimals; dates and times as times), in
        # helper columns, so the columns themselves keep their kind
        key_names = [f"_simplydata_key_{i}_" for i in range(len(keys))]
        here_keys, there_keys = [], []
        for name, key in zip(key_names, keys):
            kind = _common_kind(pl, here.schema[key], there.schema[key], key)
            here_keys.append(_as_kind(pl, key, here.schema[key], kind).alias(name))
            there_keys.append(_as_kind(pl, key, there.schema[key], kind).alias(name))
        here = here.with_row_index(index).with_columns(here_keys)
        there = there.with_columns(pl.col(on).alias(other_on), pl.lit(True).alias(mark), *there_keys).drop(keys)
        if by:  # an empty key never matches, as in every simplydata join
            there = there.filter(pl.all_horizontal(pl.col(key_names[:-1]).is_not_null()))
        try:
            import warnings

            # Polars join_asof(on=, by=, strategy="backward", tolerance=timedelta(days=2)), both sorted stably by the
            # key (the sort is done here, so the Polars note that it cannot check it with by= is not shown)
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="Sortedness of columns cannot be checked")
                joined = here.sort(key_names[-1], maintain_order=True).join_asof(
                    there.sort(key_names[-1], maintain_order=True), on=key_names[-1], by=key_names[:-1] or None,
                    strategy=MATCH_CHOICES[match], tolerance=tolerance, suffix=JOIN_SUFFIX)
        except Exception as problem:  # noqa: BLE001 - the parent's own message, given back plainly
            first = (str(problem).strip().splitlines() or [""])[0]
            raise SimplydataError(f"The tables could not be joined on the nearest {on}: {first}") from None
        joined = joined.sort(index).drop([c for c in joined.columns if c.startswith("_simplydata_key_")])
        frame = nw.from_native(joined.to_pandas() if pandas_table else joined, eager_only=True)
        found = nw.col(mark).fill_null(False)
        matched = self._count_rows_where(frame, found)
        limit = "" if within is None else f" within {within}"
        nearest = {"nearest before": f"the nearest {on} before or at their own", "nearest after":
                   f"the nearest {on} after or at their own", "nearest": f"the nearest {on}"}[match]
        print(f"{matched} of {_rows(len(self._frame))} in this table found a row of the other table with {nearest}"
              f"{limit} (its {on} is in \"{other_on}\").")
        if keep == "matching rows":
            frame = frame.filter(found)
            if matched < len(self._frame):
                print(f'{_rows(len(self._frame) - matched)} without one {"was" if len(self._frame) - matched == 1 else "were"}'
                      ' left out; keep="all rows from this table" keeps them, with empty cells.')
        frame = frame.drop([index, mark])
        what = f"join with another table using the {match} {said}{limit} (keep {keep})"
        return self._change(what, frame)

    def _nearest_other(self, other, using, step):
        """The other table, its key columns named as here: (other frame, this table's key names, the keys in words).
        As _matched_other, but whole numbers and decimals are left for _common_kind to bring together."""
        right = self._other_frame(other, step)
        example = _example('table.join_with(other, using="date", match="nearest before")')
        if isinstance(using, dict) and using and all(isinstance(k, str) and isinstance(v, str)
                                                     for k, v in using.items()):
            keys, other_keys = list(using), list(using.values())
        else:
            keys = [using] if isinstance(using, str) else _as_list([using]) if using is not None else []
            if not keys or not all(isinstance(k, str) for k in keys):
                raise SimplydataError("using= names the column to match on (the last one is matched to the nearest "
                                      "value, the others exactly)." + example)
            other_keys = list(keys)
        self._need_columns(*keys)
        for o in other_keys:
            if o not in right.columns:
                raise SimplydataError(f'The other table has no column "{o}". Its columns: '
                                      + ", ".join(map(str, right.columns)))
        rename = {o: k for k, o in zip(keys, other_keys) if o != k}
        if rename:
            right = right.rename(rename)
        said = ", ".join(k if k == o else f"{k} = {o}" for k, o in zip(keys, other_keys))
        return right, keys, said

    @staticmethod
    def _count_rows_where(frame, expr) -> int:
        if len(frame) == 0:
            return 0
        return int(frame.select(expr.fill_null(False).cast(nw.Int64).sum()).item() or 0)

