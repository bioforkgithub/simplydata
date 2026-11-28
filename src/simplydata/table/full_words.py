"""Families for 100 %, batches 1-2 (approved by Manish 2026-11-28): the table words for the pandas and Polars gaps.

  get_different_values_in   the different values of a column (pandas Series.unique, Polars unique(maintain_order=True))
  check_if_all_values_in    is every value above 0, or True? (pandas Series.all, Polars all / all_horizontal)
  check_if_any_value_in     is at least one value above 100? (pandas Series.any, Polars any / any_horizontal)
  check_if_sorted_by        are the rows in order of a column? (pandas is_monotonic_increasing, Polars is_sorted)
  add_run_number_column     number each run of the same value (Polars rle_id, pandas (s != s.shift()).cumsum())
  turn_into_title_case      "asha ali" becomes "Asha Ali" (pandas str.title, Polars str.to_titlecase)

Every word passes straight through to pandas or Polars; the comment at each call names it. Each word works on pandas
and Polars tables alike, gives one answer on both, and says what it did.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import narwhals as nw

from .._errors import SimplydataError, friendly
from .._typing import _Same
from .rows import _NOT_GIVEN

if TYPE_CHECKING:
    from ..numbers import Numbers

VALUES_IN_SENTENCE = 10  # a sentence names at most this many values; the list has them all
# the condition words of check_if_all_values_in / check_if_any_value_in, as keep_rows_where writes them
_CONDITION_NAMES = {"is_above": "above", "is_below": "below", "is_at_least": "at_least", "is_at_most": "at_most",
                    "is_equal_to": "equal_to", "is_not_equal_to": "not_equal_to", "is_between": "between",
                    "is_one_of": "one_of", "contains": "contains", "starts_with": "starts_with",
                    "ends_with": "ends_with", "is_after": "after", "is_before": "before",
                    "matches_pattern": "matches_pattern"}
_CHECK_RENAMED = {"above": "is_above", "below": "is_below", "at_least": "is_at_least", "at_most": "is_at_most",
                  "equal_to": "is_equal_to", "not_equal_to": "is_not_equal_to", "between": "is_between",
                  "one_of": "is_one_of", "after": "is_after", "before": "is_before"}


def _say_value(value) -> str:
    from .summaries import _say_number

    if isinstance(value, str):
        return f'"{value}"'
    if hasattr(value, "isoformat"):
        return str(value)[:19] if str(value).endswith(":00") is False else str(value)
    return _say_number(value)


def _values_said(values) -> str:
    shown = ", ".join(_say_value(v) for v in values[:VALUES_IN_SENTENCE])
    return shown + (f" ... ({len(values) - VALUES_IN_SENTENCE} more)" if len(values) > VALUES_IN_SENTENCE else "")


class FullWords:
    """The table words of the families for 100 % plan, batches 1-2 (section 2.1)."""

    # ------------------------------------------------------------------ the different values of a column
    @friendly
    def get_different_values_in(self, column=None) -> Numbers | list:
        """The different values of a column, each once. classes = table.get_different_values_in("class")

        classes = table.get_different_values_in("class")   (with sdata.get_example("marks"))
        The values come in the order they first turn up in the table (pandas Series.unique(), Polars
        unique(maintain_order=True)), so sort the table first (sort_by) for another order. Empty cells are left
        out, with a note, as count_different_values_in leaves them out. A column of numbers gives
        sdata.number_list, any other column a plain list, as get_column does. Capital letters matter: "Apple" and
        "apple" are two values. The table does not change.
        """
        from ..numbers import number_list
        from .models import _missing
        from .summaries import _plain

        step = "get_different_values_in"
        example = 'classes = table.get_different_values_in("class")   (with sdata.get_example("marks"))'
        if not isinstance(column, str):
            raise SimplydataError(f"{step}() needs one column name in quotes.\nFor example:  {example}")
        self._need_columns(column)
        series = self._frame[column]
        empty = int(series.is_null().sum())
        if self._frame.schema[column].is_float():  # NaN is an empty cell too (pandas reads it so)
            empty = int((series.is_null() | series.is_nan()).sum())
            series = series.filter(~series.is_nan().fill_null(True))
        else:
            series = series.drop_nulls()
        # pandas Series.unique() and Polars Series.unique(maintain_order=True): the order of first appearance
        different = series.unique(maintain_order=True)
        values = [_plain(v) for v in different.to_list() if not _missing(v)]
        if empty:
            print(f'Note: {empty} empty cell{"" if empty == 1 else "s"} in "{column}" '
                  f'{"was" if empty == 1 else "were"} left out.')
        print(f'"{column}" has {len(values)} different value{"" if len(values) == 1 else "s"}, in the order they '
              f"first turn up: {_values_said(values)}.")
        dtype = self._frame.schema[column]
        if dtype.is_numeric():
            return number_list(values)
        return values

    # ------------------------------------------------------------------ every value, or any value
    def _check_values(self, step, column, options, capitals_matter, for_each_group_in, every_value):
        """check_if_all_values_in and check_if_any_value_in: (answer, sentence) on the rows with a value."""
        from .summaries import _say_label

        word = "every value" if every_value else "any value"
        example = (f'table.{step}("marks", is_above=0)   (with sdata.get_example("marks"))' if every_value else
                   f'table.{step}("marks", is_above=90)   (with sdata.get_example("marks"))')
        columns = [column] if isinstance(column, str) else column
        if (not isinstance(columns, (list, tuple)) or not columns
                or not all(isinstance(c, str) for c in columns)):
            raise SimplydataError(f"{step}() needs a column name in quotes, or a list of them.\n"
                                  f"For example:  {example}")
        self._need_columns(*columns)
        given = {k: v for k, v in options.items() if v is not _NOT_GIVEN}
        if len(given) > 1:
            names = " and ".join(f"{_CHECK_NAMES[k]}=" for k in given)
            raise SimplydataError(f"{step}() takes one condition at a time, but you gave {names}. Use "
                                  f"is_between=[low, high] for a range.\nFor example:  {example}")
        conditions, words = [], ""
        for name in columns:
            if given:
                cond, words = self._condition(step, name, options, (), capitals_matter)
            else:
                if self._kind_of(name) != "true/false":
                    raise SimplydataError(
                        f'{step}() needs a condition, such as is_above=0, unless "{name}" holds True and False.\n'
                        f"For example:  {example}")
                cond, words = nw.col(name) == nw.lit(True), "is True"
            conditions.append((name, cond.fill_null(False), ~self._empty(name)))
        flags = [nw.when(filled).then(cond.cast(nw.Int64)).alias(f"__hit {i}")
                 for i, (_, cond, filled) in enumerate(conditions)]
        filled = [filled.cast(nw.Int64).alias(f"__filled {i}") for i, (_, _, filled) in enumerate(conditions)]
        frame = self._frame.with_columns(*flags, *filled)
        hits = nw.sum_horizontal(*(nw.col(f"__hit {i}").fill_null(0) for i in range(len(columns))))
        counted = nw.sum_horizontal(*(nw.col(f"__filled {i}") for i in range(len(columns))))
        frame = frame.with_columns(hits.alias("__hits"), counted.alias("__counted"))
        named = " and ".join(f'"{c}"' for c in columns)
        what = f"in {named}"
        phrase = words  # "is above 0", "contains 'bla'", "is True"
        empties = len(frame) * len(columns) - int(frame.select(nw.col("__counted").sum()).item())
        if empties:
            print(f'Note: {empties} empty cell{"" if empties == 1 else "s"} {what} '
                  f'{"was" if empties == 1 else "were"} left out (pandas all() and any(), Polars all() and any() '
                  "leave them out too).")
        if for_each_group_in is not None:
            groups = self._group_columns(step, for_each_group_in, columns)
            sums = frame.group_by(groups, drop_null_keys=False).agg(
                nw.col("__hits").sum().alias("__h"), nw.col("__counted").sum().alias("__c")).sort(groups,
                                                                                                 nulls_last=True)
            answer_name = "every value" if every_value else "any value"
            answer = (nw.col("__h") == nw.col("__c")) if every_value else (nw.col("__h") > 0)
            result = sums.with_columns(answer.alias(answer_name)).select(*groups, answer_name)
            table = self._new_table(nw.maybe_reset_index(result))
            rows = result.rows(named=True)
            said = "; ".join(f"{' / '.join(_say_label(r[g]) for g in groups)}: {'yes' if r[answer_name] else 'no'}"
                             for r in rows[:8])
            more = " ..." if len(rows) > 8 else ""
            ask = "Does every value" if every_value else "Does any value"
            print(f'{ask} {what} meet "{phrase}", for each {", ".join(groups)}? {said}{more}.')
            return table
        hits = int(frame.select(nw.col("__hits").sum()).item())
        total = int(frame.select(nw.col("__counted").sum()).item())
        index = frame.with_row_index("__row")
        values = "value" if total == 1 else "values"
        if every_value:
            answer = hits == total
            if total == 0:
                print(f"There are no values {what} to check, so the answer is True (as pandas all() of an empty "
                      "column).")
            elif answer:
                print(f'Yes: every value {what} meets "{phrase}" ({total} {values}).')
            else:
                first = index.filter(nw.col("__hits") < nw.col("__counted"))["__row"].item(0) + 1
                print(f'No: {total - hits} of the {total} {values} {what} do not meet "{phrase}" (the first in row '
                      f"{first}).")
        else:
            answer = hits > 0
            if answer:
                first = index.filter(nw.col("__hits") > 0)["__row"].item(0) + 1
                print(f'Yes: {hits} of the {total} {values} {what} meet "{phrase}" (the first in row {first}).')
            else:
                print(f'No: none of the {total} {values} {what} meets "{phrase}".')
        return bool(answer)

    @friendly(renamed=_CHECK_RENAMED)
    def check_if_all_values_in(self, column=None, *, is_above=_NOT_GIVEN, is_below=_NOT_GIVEN, is_at_least=_NOT_GIVEN,
                               is_at_most=_NOT_GIVEN, is_equal_to=_NOT_GIVEN, is_not_equal_to=_NOT_GIVEN,
                               is_between=_NOT_GIVEN, is_one_of=_NOT_GIVEN, contains=_NOT_GIVEN, starts_with=_NOT_GIVEN,
                               ends_with=_NOT_GIVEN, is_after=_NOT_GIVEN, is_before=_NOT_GIVEN,
                               matches_pattern=_NOT_GIVEN, capitals_matter=True, for_each_group_in=None):
        """Check whether every value of a column meets a condition. table.check_if_all_values_in("marks", is_above=0)

        answer = table.check_if_all_values_in("marks", is_above=0)   (with sdata.get_example("marks"))
        The conditions are the keep_rows_where ones, one at a time: is_above, is_below, is_at_least, is_at_most,
        is_equal_to, is_not_equal_to, is_between=[low, high], is_one_of=[...], contains, starts_with, ends_with,
        matches_pattern, is_after and is_before; a column of True and False needs none. Gives back True or False,
        so it also works in an if, and says how many values fail, and the first row that does. Empty cells are left
        out, with a note (pandas Series.all() and Polars all() leave them out too). A list of columns checks every
        value of all of them (Polars all_horizontal, then all): table.check_if_all_values_in(["hours", "marks"],
        is_above=0). for_each_group_in="class" gives a table with the answer for each group (pandas
        groupby().all()). capitals_matter=False makes the text conditions read any capitals alike.
        """
        options = dict(above=is_above, below=is_below, at_least=is_at_least, at_most=is_at_most, equal_to=is_equal_to,
                       not_equal_to=is_not_equal_to, between=is_between, one_of=is_one_of, contains=contains,
                       starts_with=starts_with, ends_with=ends_with, after=is_after, before=is_before,
                       matches_pattern=matches_pattern)
        return self._check_values("check_if_all_values_in", column, options, capitals_matter, for_each_group_in, True)

    @friendly(renamed=_CHECK_RENAMED)
    def check_if_any_value_in(self, column=None, *, is_above=_NOT_GIVEN, is_below=_NOT_GIVEN, is_at_least=_NOT_GIVEN,
                              is_at_most=_NOT_GIVEN, is_equal_to=_NOT_GIVEN, is_not_equal_to=_NOT_GIVEN,
                              is_between=_NOT_GIVEN, is_one_of=_NOT_GIVEN, contains=_NOT_GIVEN, starts_with=_NOT_GIVEN,
                              ends_with=_NOT_GIVEN, is_after=_NOT_GIVEN, is_before=_NOT_GIVEN,
                              matches_pattern=_NOT_GIVEN, capitals_matter=True, for_each_group_in=None):
        """Check whether any value of a column meets a condition. table.check_if_any_value_in("marks", is_above=90)

        answer = table.check_if_any_value_in("marks", is_above=90)   (with sdata.get_example("marks"))
        The conditions are the keep_rows_where ones, as in check_if_all_values_in; a column of True and False needs
        none. Gives back True or False, and says how many values meet it and the first row that does. Empty cells
        are left out, with a note (pandas Series.any() and Polars any() leave them out too). A list of columns
        checks the values of all of them (Polars any_horizontal, then any). for_each_group_in="class" gives a table
        with the answer for each group (pandas groupby().any()).
        """
        options = dict(above=is_above, below=is_below, at_least=is_at_least, at_most=is_at_most, equal_to=is_equal_to,
                       not_equal_to=is_not_equal_to, between=is_between, one_of=is_one_of, contains=contains,
                       starts_with=starts_with, ends_with=ends_with, after=is_after, before=is_before,
                       matches_pattern=matches_pattern)
        return self._check_values("check_if_any_value_in", column, options, capitals_matter, for_each_group_in, False)

    # ------------------------------------------------------------------ in order?
    @friendly(others={"descending": "biggest_first"})
    def check_if_sorted_by(self, column=None, biggest_first=False) -> bool:
        """Check whether the rows are in order of a column, smallest first. table.check_if_sorted_by("month_number")

        answer = table.check_if_sorted_by("month_number")   (with sdata.get_example("weather"))
        Values that tie may follow each other (pandas is_monotonic_increasing, Polars is_sorted()).
        biggest_first=True checks the other direction (pandas is_monotonic_decreasing, Polars
        is_sorted(descending=True)). Gives back True or False, and names the first row that is out of order.
        Empty cells are left out, with a note. Text is in the order of its letters (capitals before small
        letters, as sort_by puts them); dates and times from the earliest.
        """
        step = "check_if_sorted_by"
        example = 'answer = table.check_if_sorted_by("month_number")   (with sdata.get_example("weather"))'
        if not isinstance(column, str):
            raise SimplydataError(f"{step}() needs one column name in quotes.\nFor example:  {example}")
        self._need_columns(column)
        if not isinstance(biggest_first, bool):
            raise SimplydataError("biggest_first= should be True or False.")
        frame = self._frame.with_row_index("__row").filter(~self._empty(column))
        empty = len(self._frame) - len(frame)
        if empty:
            print(f'Note: {empty} empty cell{"" if empty == 1 else "s"} in "{column}" '
                  f'{"was" if empty == 1 else "were"} left out.')
        values = frame[column]
        native = values.to_native()
        # pandas Series.is_monotonic_increasing / _decreasing, Polars Series.is_sorted(descending=)
        if frame.implementation.is_polars():
            answer = bool(native.is_sorted(descending=biggest_first))
        else:
            answer = bool(native.is_monotonic_decreasing if biggest_first else native.is_monotonic_increasing)
        order = "biggest first" if biggest_first else "smallest first"
        if answer:
            print(f'Yes: the rows are in order of "{column}", {order} (values that tie may follow each other).')
            return True
        before = values.shift(1)
        wrong = (values > before) if biggest_first else (values < before)
        positions = frame.with_columns(wrong.alias("__wrong")).filter(nw.col("__wrong").fill_null(False))
        at = int(positions["__row"].item(0))
        previous = frame.filter(nw.col("__row") < at)[column].to_list()[-1]
        print(f'No: the rows are not in order of "{column}", {order}: row {at + 1} '
              f"({_say_value(positions[column].item(0))}) comes after {_say_value(previous)}.")
        return False

    # ------------------------------------------------------------------ runs of the same value
    @friendly(renamed={"for_each": "for_each_group_in"})
    def add_run_number_column(self: _Same, name=None, from_column=None, for_each_group_in=None,
                              sorted_by=None) -> _Same:
        """Number each run of the same value. table.add_run_number_column("spell", from_column="level_band")

        table.add_run_number_column("spell", from_column="level_band", for_each_group_in="station", sorted_by="date")
        (with sdata.get_example("river"), after table.add_group_column("level_band", from_column="level",
        cut_at=[2.5], names=["low", "high"]): each spell of low or high water at each station)
        A run is a stretch of rows in a row with the same value; the number goes up by one each time the value
        changes, as Polars rle_id() (plus 1, to count from 1) and pandas (s != s.shift()).cumsum(). Empty cells
        next to each other are one run (as Polars counts them). sorted_by= works in the order of a column such as
        a date (the rows keep their place); for_each_group_in= starts again at 1 in each group. Then
        table.count_rows(for_each_group_in=["station", "spell"]) gives the length of each run (Polars rle()).
        """
        step = "add_run_number_column"
        example = ('For example: table.add_run_number_column("spell", from_column="level_band", '
                   'for_each_group_in="station", sorted_by="date")')
        keys, order = self._sequence_checks(step, name, from_column, for_each_group_in, sorted_by, example,
                                            numbers_only=False)

        def make(frame, over):
            import polars as pl

            polars = frame.to_polars()
            ids = pl.col(from_column).rle_id() + 1  # Polars rle_id(): 0, 0, 1, 2, 2 ... counted from 1 here
            polars = polars.with_columns((ids.over(keys) if keys else ids).cast(pl.Int64).alias(name))
            column = polars[name]
            if not frame.implementation.is_polars():
                column = column.to_pandas()
                column.index = frame.to_native().index
            return frame.with_columns(nw.from_native(column, series_only=True).alias(name))

        group, how = self._order_words(keys, order)
        print(f'Each "{name}" numbers the runs of the same {from_column} from 1{group}, {how}: the number goes up '
              "each time the value changes.")
        return self._row_after_row(name, keys, order, make,
                                   f'add run number column "{name}" = runs of {from_column}{group}')

    # ------------------------------------------------------------------ Title Case
    @friendly
    def turn_into_title_case(self: _Same, column=None) -> _Same:
        """Start each word with a capital letter ("asha ali" becomes "Asha Ali"). table.turn_into_title_case("name")

        table.turn_into_title_case("name")   (with sdata.get_example("marks"))
        The other letters of each word become small ("McDONALD" becomes "Mcdonald"). A new word starts after
        anything that is not a letter, so "o'neil" becomes "O'Neil" and "2nd" becomes "2Nd" (pandas str.title(),
        Polars str.to_titlecase(): the same answer on both).
        """
        step = "turn_into_title_case"
        text = self._need_text(step, column, f'table.{step}("name")')
        changed = self._frame.with_columns(text.str.to_titlecase().alias(column))  # pandas title, Polars to_titlecase
        before = self._frame[column].drop_nulls()
        after = changed[column].drop_nulls()
        example = ""
        for old, new in zip(before.to_list(), after.to_list()):
            if old != new:
                example = f': "{old}" became "{new}"'
                break
        print(f'Each word in "{column}" now starts with a capital letter{example}.')
        return self._change(f"turn {column} into title case", changed)


_CHECK_NAMES = {v: k for k, v in _CONDITION_NAMES.items()}
