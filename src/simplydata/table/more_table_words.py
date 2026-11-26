"""Tables phase, batch 1: words for the jobs a messy table needs most (approved by Manish 2026-11-25).

  keep_rows_found_in / remove_rows_found_in   rows whose key is (or is not) in another table: semi and anti joins
  clean_column_names                          headers such as "Max Temp (°C)" become max_temp_c
  remove_rows_that_are_all_empty              rows (and columns) in which every cell is empty
  remove_columns_that_are_all_empty
  show_duplicate_rows                         look at the repeats before removing them
  add_row_summary_column                      a summary across several columns of each row (axis=1)
  turn_into_categories                        a fixed list of values, in an order (mild < moderate < severe)
  split_into_rows                             "sul1;tetM" becomes two rows
  add_running_column                          the total (or biggest, average ...) from the first row up to this one
  add_row_number_column                       1, 2, 3 ... in each group
  keep_groups_where / remove_groups_where     whole groups, by a summary of the group

Every word passes straight through to pandas or Polars (PLAN.md section 7); the comment at each call names it.
clean_column_names follows a fixed published rule (R janitor::make_clean_names(), see its docstring) and computes no
number. Each word works on pandas and Polars tables alike, keeps a step for undo(), and says what it did.
"""

from __future__ import annotations

import ast
import re
import unicodedata

import narwhals as nw

from .._errors import SimplydataError, choice_error, friendly
from .._typing import _Same
from ._base import numbered_at
from ._base import show as _show_native
from .columns import SUMMARY_WORDS, _as_list, _plain, _roll_with_pandas
from .conditions import _ConditionReader, _condition_error, _count_in, _kind, _rows, empty_cells_note

# add_row_summary_column(show=): the house measure names
ROW_SHOWS = ("average", "total", "median", "smallest", "biggest", "standard deviation", "count")
# add_running_column(show=): the house measure names and the narwhals cumulative method of each
# (pandas cumsum / cummax / cummin / cumprod, Polars cum_sum / cum_max / cum_min / cum_prod / cum_count);
# the average comes from pandas expanding().mean()
RUNNING_SHOWS = {"total": "cum_sum", "average": None, "smallest": "cum_min", "biggest": "cum_max",
                 "count": "cum_count", "product": "cum_prod"}
# names from other tools for show=, run with a note once
_OTHER_SHOWS = {"mean": "average", "sum": "total", "min": "smallest", "max": "biggest", "std": "standard deviation",
                "sd": "standard deviation", "prod": "product", "n": "count"}

# clean_column_names(): R janitor::make_clean_names() replaces these first (its replace= default) ...
_JANITOR_REPLACE = (("'", ""), ('"', ""), ("%", "_percent_"), ("#", "_number_"))
# ... and turns every letter into plain ASCII (ICU "Latin-ASCII"); these letters have no Unicode decomposition,
# so they are written out here, as ICU writes them (µ is "u", as janitor's replace= says)
_LATIN_ASCII = {"ø": "o", "Ø": "O", "æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE", "ß": "ss", "đ": "d", "Đ": "D",
                "ł": "l", "Ł": "L", "þ": "th", "Þ": "TH", "ð": "d", "Ð": "D", "ı": "i", "µ": "u", "μ": "u"}


def clean_name(name) -> str:
    """One column name made clean: plain ASCII letters, small letters, words joined by "_" (snake case).

    The rule of R janitor::make_clean_names(): "%" becomes "percent" and "#" "number", quotes go, accents and
    letters such as ø become plain letters (Latin-ASCII), every run of other characters becomes one "_", and a
    name that starts with a digit gets an "x" in front (as R make.names()). Unlike janitor, capitals inside a word
    do not split it: pH becomes ph (janitor makes p_h)."""
    text = str(name)
    for old, new in _JANITOR_REPLACE:
        text = text.replace(old, new)
    text = "".join(_LATIN_ASCII.get(c, c) for c in text)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^0-9A-Za-z]+", "_", text).strip("_").lower()
    if not text:
        return "x"
    return "x" + text if text[0].isdigit() else text


def _unique_names(names) -> list:
    """A repeated name gets _2, _3 ... at the end, as janitor gives it."""
    out, used = [], set()
    for name in names:
        new, n = name, 1
        while new in used:
            n += 1
            new = f"{name}_{n}"
        used.add(new)
        out.append(new)
    return out


def _example(code: str, name: str) -> str:
    return f'\nFor example:  {code}   (with sdata.get_example("{name}"))'


def _show_choice(step: str, show, choices) -> str:
    """show= checked; a name from another tool (mean, sum, max ...) runs with a note once."""
    from .columns import _value_note

    if isinstance(show, str) and show not in choices and show.strip().lower() in _OTHER_SHOWS:
        new = _OTHER_SHOWS[show.strip().lower()]
        if new in choices:
            _value_note(f"{step} show={show}", f'Note: show="{show}" is show="{new}" in simplydata.')
            return new
    if show not in choices:
        raise choice_error(step, "show", show, list(choices))
    return show


def _words_list(names) -> str:
    names = [str(n) for n in names]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


class MoreTableWords:
    # ================================================================== rows found in another table
    def _found_in(self, step, other, using, keep):
        example = f'table.{step}({{"name": ["Asha", "Ben"]}}, using="name")'
        right, keys, said = self._matched_other(other, using, step, example + '   (with sdata.get_example("marks"))')
        found = right.select(keys).unique()
        index = "_simplydata_row_"
        # pandas df[df["name"].isin(other["name"])] / ~isin; Polars join(how="semi") / join(how="anti")
        new = (self._frame.with_row_index(index).join(found, on=keys, how="semi" if keep else "anti")
               .sort(index).drop(index))
        before = len(self._frame)
        if keep:
            print(f"Kept {len(new)} of {_rows(before)}: those whose {said} is found in the other table.")
        else:
            print(f"Removed {before - len(new)} of {_rows(before)}: those whose {said} is found in the other table. "
                  f"{_rows(len(new))} left.")
        empty = _count_in(self._frame, nw.any_horizontal(*[nw.col(k).is_null() for k in keys], ignore_nulls=True))
        if empty:
            print(f"Note: {_rows(empty)} {'has' if empty == 1 else 'have'} an empty {said}, which is never found "
                  f"in another table, so {'it was' if empty == 1 else 'they were'} "
                  f"{'left out' if keep else 'not removed'}.")
        verb = "keep" if keep else "remove"
        return self._change(f"{verb} rows whose {said} is found in another table", new)

    @friendly(others={"on": "using", "by": "using"})
    def keep_rows_found_in(self: _Same, other=None, using=None) -> _Same:
        """Keep only the rows whose key (a name, a sample ID) is found in another table; no columns are added.

        table.keep_rows_found_in({"name": ["Asha", "Ben"]}, using="name")   (with sdata.get_example("marks"))
        Only Asha's and Ben's rows stay. Unlike join_with, nothing comes in from the other table, and a
        row never appears twice, however often its key appears there (a semi join: pandas
        df[df["name"].isin(other["name"])], Polars join(how="semi")). using= pairs differently named
        columns as in join_with: using={"sample_id": "sample"}. An empty key is never found.
        other can be a simplydata table, a pandas or Polars table, a file name or a dict.
        """
        return self._found_in("keep_rows_found_in", other, using, keep=True)

    @friendly(others={"on": "using", "by": "using"})
    def remove_rows_found_in(self: _Same, other=None, using=None) -> _Same:
        """Remove the rows whose key is found in another table: what is left is what the other table lacks.

        table.remove_rows_found_in({"name": ["Asha", "Ben"]}, using="name")   (with sdata.get_example("marks"))
        The opposite of keep_rows_found_in (an anti join: pandas df[~df["name"].isin(other["name"])],
        Polars join(how="anti")). It finds, for example, the samples that have no lab result:
          samples.remove_rows_found_in(lab, using="sample_id")
        A row with an empty key is never found, so it stays.
        """
        return self._found_in("remove_rows_found_in", other, using, keep=False)

    # ================================================================== column names
    @friendly
    def clean_column_names(self: _Same) -> _Same:
        """Make every column name plain: small letters, no spaces or signs, words joined by "_".

        table.clean_column_names()   (with sdata.get_example("fjord_stations"))
        "Distance to outfall (km)" becomes distance_to_outfall_km, "Latitude (°N)" latitude_n,
        "Sample ID " sample_id and "pH" ph; one line per change is printed. Clean names can be typed
        without quotes in a formula (add_column("ratio", "salinity / depth_m")). The rule is R
        janitor::clean_names(): "%" becomes percent and "#" number, letters such as ø and é become o
        and e, a name that starts with a digit gets an x in front, and a name that would repeat
        gets _2 at the end. Unlike janitor, capitals inside a word do not split it (janitor makes
        pH into p_h). Undo with table.undo().
        """
        old = self._columns
        new = _unique_names([clean_name(c) for c in old])
        changes = {o: n for o, n in zip(old, new) if o != n}
        if not changes:
            print("The column names are already clean, so nothing changed.")
            return self._change("clean the column names (nothing to change)", self._frame)
        print(f"Cleaned {len(changes)} of {len(old)} column name{'s' if len(old) != 1 else ''} (the R janitor rule):")
        for o, n in changes.items():
            print(f'  "{o}" -> {n}')
        return self._change(f"clean the column names ({len(changes)} changed)", self._frame.rename(changes))

    # ================================================================== empty rows and columns
    @friendly
    def remove_rows_that_are_all_empty(self: _Same) -> _Same:
        """Remove the rows in which every cell is empty, as a spreadsheet leaves between blocks of data.

        table.remove_rows_that_are_all_empty()   (with sdata.get_example("fjord_lab"))
        A row with some cells filled stays: remove_rows_with_empty_cells_in() is the word that removes
        a row for one empty cell. An empty cell is a missing value or text of only spaces, as
        everywhere in simplydata (pandas dropna(how="all"), Polars
        filter(~pl.all_horizontal(pl.all().is_null())); pandas counts "   " as filled, simplydata does not).
        """
        if not self._columns:
            raise SimplydataError("The table has no columns, so there is nothing to look at.")
        every = nw.all_horizontal(*[self._empty(c) for c in self._columns], ignore_nulls=True)
        new = self._frame.filter(~every)
        before, gone = len(self._frame), len(self._frame) - len(new)
        if gone:
            print(f"Removed {gone} of {_rows(before)}: every cell in {'it' if gone == 1 else 'them'} was empty. "
                  f"{_rows(len(new))} left.")
        else:
            print(f"No row has every cell empty, so nothing was removed ({_rows(before)}).")
        return self._change(f"remove rows that are all empty ({gone})", new)

    @friendly
    def remove_columns_that_are_all_empty(self: _Same) -> _Same:
        """Remove the columns in which every cell is empty, such as a column nobody filled in.

        table.remove_columns_that_are_all_empty()   (with sdata.get_example("fjord_lab"))
        It says which columns went. A column with one filled cell stays. An empty cell is a missing
        value or text of only spaces (pandas dropna(axis=1, how="all"), Polars select() of the
        columns whose null_count() is below the number of rows).
        """
        rows = len(self._frame)
        if not rows:
            raise SimplydataError("The table has no rows, so every column is empty: nothing was removed.")
        empty = [c for c in self._columns if self._count(self._empty(c)) == rows]
        if len(empty) == len(self._columns):
            raise SimplydataError("Every cell of the table is empty, so removing the empty columns would leave "
                                  "nothing. Check that the right file was read.")
        if empty:
            names = ", ".join(f'"{c}"' for c in empty)
            print(f"Removed {len(empty)} column{'s' if len(empty) != 1 else ''} in which every cell is empty: {names}.")
        else:
            print("No column has every cell empty, so nothing was removed.")
        return self._change(f"remove columns that are all empty ({', '.join(map(str, empty)) or 'none'})",
                            self._frame.drop(empty))

    # ================================================================== repeats
    @friendly(others={"subset": "columns"})
    def show_duplicate_rows(self, columns=None):
        """Show the rows that repeat another row, each with its row number (the table does not change).

        table.show_duplicate_rows()   (with sdata.get_example("fjord_lab"))
        Without columns= a row repeats when every cell is the same; with columns= when those cells
        are: table.show_duplicate_rows(columns=["sample_id", "gene"]). Every copy is shown, the first one too (pandas df[df.duplicated(keep=False)], Polars
        df.filter(df.is_duplicated())), so you can see which copy to keep before
        remove_duplicate_rows(keep=...). Two empty cells count as the same.
        """
        if columns is None:
            subset = list(self._columns)
        else:
            subset = [columns] if isinstance(columns, str) else _as_list([columns])
            if not subset or not all(isinstance(c, str) for c in subset):
                raise SimplydataError("columns= needs one or more column names."
                                      + _example('table.show_duplicate_rows(columns=["name", "subject"])', "marks"))
            self._need_columns(*subset)
        within = "" if columns is None else f" in {', '.join(subset)}"
        repeats = self._frame.select(subset).is_duplicated()
        place = "_simplydata_place_"
        found = self._frame.with_row_index(place).filter(repeats)
        if not len(found):
            print(f"0 rows repeat another row{within}, so there is nothing to remove.")
            return None
        positions = found[place].to_list()
        found = found.drop(place)
        groups = len(found.select(subset).unique())
        extra = len(found) - groups
        print(f"{_rows(len(found))} repeat another row{within}: {groups} different "
              f"{'row is' if groups == 1 else 'rows are'} there more than once ({extra} extra "
              f"cop{'y' if extra == 1 else 'ies'}).")
        _show_native(numbered_at(nw.maybe_reset_index(found), positions))
        code = "" if columns is None else f"columns={subset!r}".replace("'", '"')
        print(f"table.remove_duplicate_rows({code}) keeps the first copy of each; keep=\"last\" keeps the last.")
        return None

    # ================================================================== across the columns of a row
    @friendly(others={"cols": "columns", "of": "columns"})
    def add_row_summary_column(self: _Same, name=None, columns=None, show="average") -> _Same:
        """Add a column with a summary of several columns in each row, such as the average of three visits.

        table.add_row_summary_column("pain_average", columns=["pain_week_0", "pain_week_4", "pain_week_8"], show="average")   (with sdata.get_example("clinic"))
        show= can be "average", "total", "median", "smallest", "biggest", "standard deviation" or
        "count" (the filled cells). Empty cells are left out, and the sentence says how many rows had
        one; a row with every cell empty gets an empty cell (a count of 0). As pandas
        df[columns].mean(axis=1) and Polars pl.mean_horizontal(columns) (sum_horizontal, min_horizontal,
        max_horizontal; the median and standard deviation of pl.concat_list(columns)).
        A summary down a column, for each group, is find_summary_of; this one goes across a row.
        """
        step = "add_row_summary_column"
        example = _example(f'table.{step}("pain_average", columns=["pain_week_0", "pain_week_4", "pain_week_8"])',
                           "clinic")
        self._check_new_name(name, step)
        cols = [columns] if isinstance(columns, str) else _as_list([columns]) if columns is not None else []
        if len(cols) < 2 or not all(isinstance(c, str) for c in cols):
            raise SimplydataError(f"{step}() needs columns= with two or more column names." + example)
        self._need_columns(*cols)
        show = _show_choice(step, show, ROW_SHOWS)
        if show != "count":
            self._need_numbers(*cols, step=step)
        native = self._frame.to_native()
        if self._frame.implementation.is_polars():
            import polars as pl

            filled = pl.sum_horizontal(pl.col(cols).is_not_null())
            expr = {"average": pl.mean_horizontal(cols), "total": pl.sum_horizontal(cols),
                    "smallest": pl.min_horizontal(cols), "biggest": pl.max_horizontal(cols),
                    "median": pl.concat_list(cols).list.median(), "standard deviation": pl.concat_list(cols).list.std(),
                    "count": filled}[show]
            if show == "total":  # Polars sum_horizontal gives 0 for a row with no filled cell; pandas min_count=1
                expr = pl.when(filled > 0).then(expr)
            native = native.with_columns(expr.alias(name))
        else:
            part = native[cols]
            values = {"average": lambda: part.mean(axis=1), "total": lambda: part.sum(axis=1, min_count=1),
                      "median": lambda: part.median(axis=1), "smallest": lambda: part.min(axis=1),
                      "biggest": lambda: part.max(axis=1), "standard deviation": lambda: part.std(axis=1),
                      "count": lambda: part.count(axis=1)}[show]()
            native = native.assign(**{name: values})
        frame = nw.from_native(native, eager_only=True)
        some_empty = _count_in(self._frame, nw.any_horizontal(*[self._empty(c) for c in cols], ignore_nulls=True))
        said = f"; {_rows(some_empty)} had an empty cell, which was left out" if some_empty else ""
        print(f'Each "{name}" is the {show} of {_words_list(cols)} in its row{said}.')
        return self._finish(name, frame, f'add row summary column "{name}" = {show} of {", ".join(cols)}')

    # ================================================================== categories
    @friendly(others={"levels": "in_order", "categories": "in_order", "order": "in_order"})
    def turn_into_categories(self: _Same, column=None, in_order=None) -> _Same:
        """Turn a text column into categories: a fixed list of values, in an order you give.

        table.turn_into_categories("nurse_rating", in_order=["mild", "moderate", "severe"])   (with sdata.get_example("clinic"))
        Sorting, summaries for each group and charts then follow mild < moderate < severe instead of
        A to Z (count_each still lists the most common first; its in_order= gives this order). A value
        that is not in the list stops the word with its name, so a typing mistake such as "Severe"
        is never turned silently into an empty cell. Without in_order= the order is the one in
        which the values first appear. As pandas pd.Categorical(values, categories=[...],
        ordered=True) and Polars cast(pl.Enum([...])). Undo with table.undo().
        """
        step = "turn_into_categories"
        example = _example(f'table.{step}("nurse_rating", in_order=["mild", "moderate", "severe"])', "clinic")
        if not isinstance(column, str):
            raise SimplydataError(f".{step}() needs the column name in quotes first." + example)
        self._need_columns(column)
        kind = _kind(self._frame.schema[column])
        if kind != "text":
            raise SimplydataError(f'.{step}() works on text, but "{column}" holds {kind} values. To use numbers '
                                  f'as categories, first write table.turn_into_text("{column}").' + example)
        empty = self._empty(column)
        spaces = _count_in(self._frame, empty & ~nw.col(column).is_null())
        present = (self._frame.filter(~empty).select(nw.col(column).cast(nw.String))[column]
                   .unique(maintain_order=True).to_list())
        if in_order is None:
            order = present
        else:
            if isinstance(in_order, str) or not isinstance(in_order, (list, tuple)) or not in_order:
                raise SimplydataError("in_order= is the list of values, in order, in square brackets." + example)
            order = list(in_order)
            if not all(isinstance(v, str) for v in order):
                raise SimplydataError("in_order= holds text values in quotes, like in_order=[\"mild\", \"moderate\"]."
                                      + example)
            twice = sorted({v for v in order if order.count(v) > 1})
            if twice:
                raise SimplydataError(f"in_order= has {', '.join(map(repr, twice))} more than once; give each value "
                                      "once.")
            missing = [v for v in present if v not in order]
            if missing:
                counts = [_count_in(self._frame, nw.col(column) == v) for v in missing[:5]]
                shown = ", ".join(f'"{v}" ({_rows(n)})' for v, n in zip(missing, counts))
                raise SimplydataError(
                    f'"{column}" holds {len(missing)} value{"s" if len(missing) != 1 else ""} that '
                    f'{"is" if len(missing) == 1 else "are"} not in in_order=: {shown}'
                    f'{" ..." if len(missing) > 5 else ""}.\nAdd {"it" if len(missing) == 1 else "them"} to the list, '
                    f'or fix {"it" if len(missing) == 1 else "them"} first, for example '
                    f'table.replace_values_in("{column}", "{missing[0]}", with_value="...").'
                )
        native = self._frame.with_columns(nw.when(~empty).then(nw.col(column)).alias(column)).to_native()
        if self._frame.implementation.is_polars():
            import polars as pl

            native = native.with_columns(pl.col(column).cast(pl.Enum(order)))  # Polars cast(pl.Enum([...]))
        else:
            import pandas as pd

            native = native.assign(**{column: pd.Categorical(native[column], categories=order, ordered=True)})
        unused = [v for v in order if v not in present]
        print(f'"{column}" is now categories, in this order: {" < ".join(order)}. Sorting, summaries for each group '
              "and charts follow it." + (f" Not in the column yet: {', '.join(unused)}." if unused else ""))
        if spaces:
            print(f"Note: {_rows(spaces)} held only spaces; {'it is' if spaces == 1 else 'they are'} an empty cell now.")
        return self._change(f'turn "{column}" into categories ({" < ".join(order)})',
                            nw.from_native(native, eager_only=True))

    # ================================================================== one value per cell
    @friendly(others={"sep": "separator", "delimiter": "separator", "by": "separator"})
    def split_into_rows(self: _Same, column=None, separator=None) -> _Same:
        """Split the cells of a column into rows: "sul1;tetM" becomes two rows, one value each.

        table.split_into_rows("crew", separator=";")   (with sdata.get_example("fjord_samples"))
        The other columns are copied into each new row. A cell without the separator stays one row;
        an empty cell stays one row with an empty cell. A column that already holds lists (from a
        Polars or Parquet table) is split without separator=. As pandas
        df.assign(crew=df["crew"].str.split(";")).explode("crew") and Polars
        df.with_columns(pl.col("crew").str.split(";")).explode("crew"). To split a cell into
        columns instead, use split_column(). Undo with table.undo().
        """
        step = "split_into_rows"
        example = _example(f'table.{step}("crew", separator=";")', "fjord_samples")
        if not isinstance(column, str):
            raise SimplydataError(f".{step}() needs the column name in quotes first." + example)
        self._need_columns(column)
        dtype = self._frame.schema[column]
        native = self._frame.to_native()
        polars = self._frame.implementation.is_polars()
        holds_lists = dtype == nw.List or (not polars and dtype == nw.Object and any(
            isinstance(v, (list, tuple)) for v in native[column].dropna().head(20)))
        if not holds_lists:
            if _kind(dtype) != "text":
                raise SimplydataError(f'.{step}() splits text, but "{column}" holds {_kind(dtype)} values.' + example)
            if not isinstance(separator, str) or not separator:
                raise SimplydataError(f".{step}() needs separator=, the character between the values in a cell, "
                                      'such as separator=";" or separator=",".' + example)
        elif separator is not None:
            raise SimplydataError(f'"{column}" already holds lists, so leave out separator=.')
        before = len(self._frame)
        if polars:
            import polars as pl

            if not holds_lists:
                native = native.with_columns(pl.col(column).str.split(separator))
            native = native.explode(column)
        else:
            if not holds_lists:
                native = native.assign(**{column: native[column].str.split(separator, regex=False)})
            native = native.explode(column, ignore_index=True)
        frame = nw.from_native(native, eager_only=True)
        at = f' at "{separator}"' if separator is not None else ""
        print(f'Split "{column}"{at} into rows: {_rows(before)} became {_rows(len(frame))}.')
        if frame.schema[column] == nw.String:
            text = nw.col(column)
            loose = _count_in(frame, (text != text.str.strip_chars()).fill_null(False) & ~text.is_null())
            if loose:
                print(f"Note: {loose} of the new cells start or end with a space; "
                      f'table.remove_extra_spaces_in("{column}") takes the spaces away.')
        return self._change(f'split "{column}"{at} into rows', frame)

    # ================================================================== row after row
    @friendly(renamed={"for_each": "for_each_group_in"})
    def add_running_column(self: _Same, name=None, from_column=None, show="total", for_each_group_in=None,
                           sorted_by=None) -> _Same:
        """Add a running summary: for each row, the total (or average, biggest ...) from the first row up to this one.

        table.add_running_column("sales_so_far", from_column="sales", show="total", for_each_group_in="shop", sorted_by="date")   (with sdata.get_example("shop"))
        show= can be "total" (a cumulative sum), "average", "smallest", "biggest", "count" (the filled
        cells so far) or "product". for_each_group_in= starts again in each group; sorted_by= works it
        out in the order of a column such as a date (the rows themselves keep their place).
        An empty cell is left out of the rows after it, and its own row stays empty, except with
        show="count", which gives the count of filled cells so far there too. Running: from the first row
        to this one; rolling (add_rolling_column): a window of the last few rows that moves.
        As pandas groupby().cumsum() (cummax, cummin, cumprod, and expanding().mean() for the
        average) and Polars cum_sum().over() (cum_max, cum_min, cum_prod, cum_count).
        """
        step = "add_running_column"
        example = (f'For example: table.{step}("sales_so_far", from_column="sales", show="total", '
                   'for_each_group_in="shop", sorted_by="date")   (with sdata.get_example("shop"))')
        show = _show_choice(step, show, RUNNING_SHOWS)
        keys, order = self._sequence_checks(step, name, from_column, for_each_group_in, sorted_by, example,
                                            numbers_only=show != "count")
        method = RUNNING_SHOWS[show]

        def make(frame, over):
            if method is None:  # the average so far: pandas expanding().mean(), group by group
                values = _roll_with_pandas(frame.to_pandas(), keys, [from_column], "all", None, None, order,
                                           "average", False, None)
                frame = frame.with_columns(nw.new_series(name, values, nw.Float64, backend=frame.implementation))
                return frame.with_columns(nw.when(~nw.col(from_column).is_null()).then(nw.col(name)).alias(name))
            return frame.with_columns(over(getattr(nw.col(from_column), method)()).alias(name))

        group, how = self._order_words(keys, order)
        print(f'Each "{name}" is the {show} of {from_column} from the first row up to this one{group}, {how}.')
        return self._row_after_row(name, keys, order, make, f'add running column "{name}" = {show} of {from_column}'
                                   f"{group}")

    @friendly(renamed={"for_each": "for_each_group_in"})
    def add_row_number_column(self: _Same, name=None, for_each_group_in=None, sorted_by=None) -> _Same:
        """Add a column that numbers the rows 1, 2, 3 ..., starting again at 1 in each group.

        table.add_row_number_column("day_number", for_each_group_in="station", sorted_by="date")   (with sdata.get_example("river"))
        Without for_each_group_in= the whole table is numbered from 1. sorted_by= numbers the rows in
        the order of a column such as a date (the rows themselves keep their place). Numbers start at
        1, as table.show() counts, not at 0 as pandas does. As pandas groupby().cumcount() + 1 and
        Polars pl.int_range(1, pl.len() + 1).over(...).
        """
        step = "add_row_number_column"
        example = (f'For example: table.{step}("day_number", for_each_group_in="station", sorted_by="date")'
                   '   (with sdata.get_example("river"))')
        self._check_new_name(name, step)
        keys, order = self._group_keys(for_each_group_in, example), self._order_columns(sorted_by, example)

        def make(frame, over):
            native = frame.to_native()
            if frame.implementation.is_polars():
                import polars as pl

                number = pl.int_range(1, pl.len() + 1)
                values = native.select((number.over(keys) if keys else number).alias("n"))["n"].to_numpy()
            elif keys:
                values = (native.groupby(keys, sort=False, dropna=False).cumcount() + 1).to_numpy()
            else:
                values = range(1, len(native) + 1)
            return frame.with_columns(nw.new_series(name, list(values), nw.Int64, backend=frame.implementation))

        group, how = self._order_words(keys, order)
        print(f'"{name}" numbers the rows from 1{group}, {how}.')
        return self._row_after_row(name, keys, order, make, f'add row number column "{name}"{group}')

    # ================================================================== whole groups
    def _group_summaries(self, step, condition, keys, frame, example):
        """The summaries in a group condition, average(marks) or count(), as columns worked out for each group
        (pandas groupby().transform("mean"), Polars pl.col("marks").mean().over(...)); gives the condition with each
        summary replaced by its column, the frame with those columns, and {column: the summary as written}."""
        text = " ".join(condition.split())
        names = {}

        def backtick(match):
            key = f"_simplydata_name_{len(names)}_"
            names[key] = match.group(1)
            return key

        plain = re.sub(r"`([^`]*)`", backtick, text)
        try:
            tree = ast.parse(plain, mode="eval")
        except SyntaxError:
            raise _condition_error(f'simplydata cannot read the condition "{condition}". Check the brackets and signs.'
                                   + example) from None
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id in SUMMARY_WORDS]
        if not calls:
            raise SimplydataError(
                f".{step}() looks at whole groups, so the condition needs a summary of each group, such as "
                "average(marks) >= 50, count() >= 10 or total(sales) > 1000. For single rows use keep_rows_where."
                + example)
        row_id = "_simplydata_row_"
        frame = frame.with_row_index(row_id)
        made, said = [], {}
        for i, call in enumerate(sorted(calls, key=lambda c: c.col_offset, reverse=True)):
            word = call.func.id
            if call.keywords or len(call.args) > 1 or (call.args and not isinstance(call.args[0], ast.Name)):
                raise _condition_error(f"Write {word}() with one column name inside, like {word}(marks)"
                                       + (", or count() for the rows of each group." if word == "count" else ".")
                                       + example)
            if not call.args:
                if word != "count":
                    raise _condition_error(f"{word}() needs a column inside, like {word}(marks)." + example)
                expr = nw.col(row_id).count()
            else:
                column = names.get(call.args[0].id, call.args[0].id)
                self._need_columns(column)
                if word != "count":
                    self._need_numbers(column, step=step)
                expr = getattr(nw.col(column), SUMMARY_WORDS[word])()
            key = f"_simplydata_group_{i}_"
            made.append(expr.over(*keys).alias(key))
            code = plain.encode("utf-8")  # ast gives the places in bytes
            written = code[call.col_offset:call.end_col_offset].decode("utf-8")
            for k, n in names.items():
                written = written.replace(k, f"`{n}`")
            said[key] = written
            plain = (code[:call.col_offset] + key.encode("utf-8") + code[call.end_col_offset:]).decode("utf-8")
        for k, n in names.items():
            plain = plain.replace(k, f"`{n}`")
        return plain, frame.with_columns(made).drop(row_id), said

    def _groups_where(self, step, condition, for_each, keep):
        example = _example(f'table.{step}("average(marks) >= 50", for_each_group_in="school")', "school")
        if not isinstance(condition, str) or not condition.strip():
            raise SimplydataError(f'.{step}() needs a condition in quotes, like "average(marks) >= 50".' + example)
        if for_each is None:
            raise SimplydataError(f".{step}() needs for_each_group_in=, the column that makes the groups." + example)
        keys = self._group_keys(for_each, example)
        text, frame, said = self._group_summaries(step, condition, keys, self._frame, example)
        reader = _ConditionReader(text, frame, where=f"{step}()")
        try:
            true, false = reader.read()
        except SimplydataError as error:
            message = str(error)
            for key, written in said.items():
                message = message.replace(f"`{key}`", written).replace(key, written)
            raise SimplydataError(message) from None
        single = [c for c in reader.used if c not in said and c not in keys]
        if single:
            raise SimplydataError(
                f'"{single[0]}" on its own is a value of single rows, but .{step}() keeps or removes whole groups. '
                f"Name a summary of it, such as average({single[0]}), or use keep_rows_where for single rows."
                + example)
        meets = frame.select(true.fill_null(False).alias("_simplydata_meets_"))["_simplydata_meets_"]
        new = self._frame.filter(meets if keep else ~meets)
        label = ", ".join(f'"{k}"' for k in keys)
        groups_before = len(self._frame.select(keys).unique())
        groups_after = len(new.select(keys).unique())
        rows_before = len(self._frame)
        if keep:
            print(f"Kept {groups_after} of {groups_before} groups of {label}: those where {condition} "
                  f"({len(new)} of {_rows(rows_before)}).")
        else:
            print(f"Removed {groups_before - groups_after} of {groups_before} groups of {label}: those where "
                  f"{condition} ({rows_before - len(new)} of {_rows(rows_before)}; {_rows(len(new))} left).")
        unknown, _ = empty_cells_note(frame, true, false, list(said))
        if unknown:
            print(f"Note: in {_rows(unknown)} the summary is empty (a group with no filled cell), so the condition "
                  f"cannot be checked there; {'they were left out' if keep else 'they were not removed'}.")
        verb = "keep" if keep else "remove"
        return self._change(f"{verb} groups of {', '.join(keys)} where {condition}", new)

    @friendly(others={"by": "for_each_group_in", "groupby": "for_each_group_in"})
    def keep_groups_where(self: _Same, condition=None, for_each_group_in=None) -> _Same:
        """Keep only the whole groups that meet a condition on a summary of the group.

        table.keep_groups_where("average(marks) >= 50", for_each_group_in="school")   (with sdata.get_example("school"))
        The condition uses the summary words of add_column: average(), median(), total(), smallest(),
        biggest() and count() (count() alone is the number of rows in the group), with the
        keep_rows_where signs and and / or:
          table.keep_groups_where("count() >= 10 and average(sleep) > 7", for_each_group_in="school")
        Every row of a group that meets it stays; the sentence says how many groups and rows. Empty
        cells are left out of each summary. As pandas groupby("school").filter(lambda g:
        g["marks"].mean() >= 50) and Polars filter(pl.col("marks").mean().over("school") >= 50).
        """
        return self._groups_where("keep_groups_where", condition, for_each_group_in, keep=True)

    @friendly(others={"by": "for_each_group_in", "groupby": "for_each_group_in"})
    def remove_groups_where(self: _Same, condition=None, for_each_group_in=None) -> _Same:
        """Remove the whole groups that meet a condition on a summary of the group (the opposite of keep_groups_where).

        table.remove_groups_where("average(marks) < 50", for_each_group_in="school")   (with sdata.get_example("school"))
        Same conditions as keep_groups_where. A group whose summary cannot be worked out (every cell
        empty) is never removed.
        """
        return self._groups_where("remove_groups_where", condition, for_each_group_in, keep=False)
