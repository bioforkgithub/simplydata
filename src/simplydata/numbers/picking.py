"""Words for a list of numbers: picking, keeping, ordering and filling.

The names follow tables, with "numbers" in place of "rows", so they can be guessed:

    table.keep_rows_where("marks", is_above=50)    ->  numbers.keep_each_number_that(is_above=50)
    table.keep_first_rows(10)             ->  numbers.keep_first_numbers(10)
    table.show_first_rows(5)              ->  numbers.show_first_numbers(5)
    table.remove_rows_with_empty_cells_in()  ->  numbers.remove_empty_numbers()
    table.count_empty_cells_in()             ->  numbers.count_empty_numbers()
    table.fill_empty_cells_in("marks", with_the="average")  ->  numbers.fill_empty_numbers(with_the="average")

Conditions are the same as keep_rows_where (without the text ones), and empty values never
match a condition except is_empty=True.

Positions count from 1: numbers.get_number_at(1) is the first number.
"""

from __future__ import annotations

from .._typing import _Same

import sys

import numpy as np

from .._errors import SimplydataError, choice_error, friendly, option_error
from .._positions import read_positions
from ._base import NOT_GIVEN, amount, check_seed, check_whole, is_number, plain, say

CONDITIONS = ("above", "below", "at_least", "at_most", "equal_to", "not_equal_to", "between", "one_of",
              "is_empty")
FILL_CHOICES = ("average", "median", "value above", "value below", "line between neighbours")



def _is(key: str) -> str:
    """The condition option as it is written now: above -> is_above (the old names still work)."""
    return key if key.startswith("is_") or key in ("contains", "starts_with", "ends_with") else f"is_{key}"

class ReplacingWords:
    """Shared by numbers and grids: one condition on the numbers, and replace_each_number_that()."""

    def _condition(self, step: str, options: dict, extra: tuple):
        """Which numbers match one condition. Gives (True/False for each number, words)."""
        example = f"{step}(is_above=50)"
        if extra:
            raise SimplydataError(
                f".{step}() needs one plain word saying which numbers, like is_above=50 or is_between=[40, 60]."
                + self._example(example)
            )
        given = {k: v for k, v in options.items() if v is not NOT_GIVEN}
        if not given:
            raise SimplydataError(
                f".{step}() needs one condition saying which numbers. You can use: "
                + ", ".join(f"{_is(c)}=" for c in CONDITIONS) + self._example(example)
            )
        if len(given) > 1:
            names = " and ".join(f"{c}=" for c in given)
            raise SimplydataError(
                f".{step}() takes one condition at a time, but you gave {names}. "
                "Write one step per condition, or use is_between=[low, high]."
                + self._example(f"{step}(is_at_least=40)   then   numbers.{step}(is_at_most=80)")
            )
        option, value = next(iter(given.items()))
        v = self._values
        empty = self._empty_mask()
        if option == "is_empty":
            if not isinstance(value, bool):
                raise SimplydataError("is_empty= needs True or False (no quotes)." + self._example(f"{step}(is_empty=True)"))
            return (empty if value else ~empty), ("are empty" if value else "are not empty")

        def number(x, example_code=example):
            if is_number(x):
                return x
            hint = ""
            if isinstance(x, str):
                try:
                    float(x)
                    hint = f" Write the number without quotes: {_is(option)}={x.strip()}."
                except ValueError:
                    pass
            raise SimplydataError(f"{_is(option)}= needs a number (you gave {x!r}).{hint}" + self._example(example_code))

        with np.errstate(invalid="ignore"):
            if option in ("above", "below", "at_least", "at_most"):
                x = number(value)
                cond = {"above": v > x, "below": v < x, "at_least": v >= x, "at_most": v <= x}[option]
                words = f"{option.replace('_', ' ')} {say(x)}"
            elif option == "between":
                ex = f"{step}(is_between=[40, 60])"
                if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)) or len(value) != 2:
                    raise SimplydataError(
                        "is_between= needs two numbers in square brackets: the lowest and the highest."
                        + self._example(ex)
                    )
                low, high = sorted(number(x, ex) for x in value)
                cond, words = (v >= low) & (v <= high), f"between {say(low)} and {say(high)}"
            elif option == "one_of":
                ex = f"{step}(is_one_of=[1, 2, 3])"
                if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple, set)) or not value:
                    raise SimplydataError(
                        "is_one_of= needs a list of numbers in square brackets. For a single number use is_equal_to="
                        + self._example(ex)
                    )
                values = [number(x, ex) for x in value]
                cond, words = np.isin(v, values), "one of " + ", ".join(say(x) for x in values)
            else:  # equal_to, not_equal_to
                x = number(value, f"{step}(is_equal_to=5)")
                if option == "equal_to":
                    cond, words = v == x, f"equal to {say(x)}"
                else:
                    cond, words = v != x, f"not equal to {say(x)}"
        return cond & ~empty, words

    @friendly(renamed={"above": "is_above", "below": "is_below", "at_least": "is_at_least", "at_most": "is_at_most",
                       "equal_to": "is_equal_to", "not_equal_to": "is_not_equal_to", "between": "is_between",
                       "one_of": "is_one_of"})
    def replace_each_number_that(self, old=NOT_GIVEN, with_value=NOT_GIVEN, *, is_above=NOT_GIVEN, is_below=NOT_GIVEN,
                                 is_at_least=NOT_GIVEN, is_at_most=NOT_GIVEN, is_equal_to=NOT_GIVEN, is_not_equal_to=NOT_GIVEN,
                                 is_between=NOT_GIVEN, is_one_of=NOT_GIVEN, is_empty=NOT_GIVEN):
        """Replace a number, or every number that meets one condition; with_value="empty" (or None) makes them empty.

        numbers.replace_each_number_that(-999, with_value=None)   a code for "missing" becomes empty
        numbers.replace_each_number_that(is_above=100, with_value=100)   every number above 100 becomes 100
        The conditions are those of keep_each_number_that (one at a time): is_above, is_below,
        is_at_least, is_at_most, is_equal_to, is_not_equal_to, is_between, is_one_of, is_empty. A grid keeps its rows and columns.
        As NumPy np.where(a > 100, 100, a) and pandas s.mask(s > 100, 100).
        """
        name = self._name
        example = f"{name}.replace_each_number_that(is_above=100, with_value=100)"
        options = dict(above=is_above, below=is_below, at_least=is_at_least, at_most=is_at_most, equal_to=is_equal_to,
                       not_equal_to=is_not_equal_to, between=is_between, one_of=is_one_of, is_empty=is_empty)
        given = [k for k, v in options.items() if v is not NOT_GIVEN]
        if old is NOT_GIVEN and not given:
            raise SimplydataError(
                ".replace_each_number_that() needs the number to replace, or one condition saying which numbers ("
                + ", ".join(f"{_is(c)}=" for c in CONDITIONS) + "), and with_value= the new number."
                + f"\nFor example:  {name}.replace_each_number_that(-999, with_value=None)\nFor example:  {example}"
            )
        if old is not NOT_GIVEN and given:
            raise SimplydataError(
                f".replace_each_number_that() takes either the old number or one condition ({_is(given[0])}=), not both."
                + f"\nFor example:  {name}.replace_each_number_that(-999, with_value=None)\nFor example:  {example}"
            )
        if with_value is NOT_GIVEN:
            raise SimplydataError(
                ".replace_each_number_that() needs with_value=, the new number (None makes them empty)."
                + f"\nFor example:  {example}"
            )
        if isinstance(with_value, str) and with_value.strip().lower() == "empty":
            with_value = None  # P37: "empty" says the same as None
        if with_value is not None and not is_number(with_value):
            raise SimplydataError(
                f"with_value= needs a number, or None to make the numbers empty (you gave {with_value!r})."
                + f"\nFor example:  {example}"
            )
        if old is not NOT_GIVEN:
            if old is None or (is_number(old) and old != old):
                raise SimplydataError(
                    f"For the empty numbers write {name}.replace_each_number_that(is_empty=True, with_value=0) "
                    f"or {name}.fill_empty_numbers(with_value=0)." if name == "numbers" else
                    f"For the empty numbers write {name}.replace_each_number_that(is_empty=True, with_value=0)."
                )
            olds = list(old) if isinstance(old, (list, tuple, set, np.ndarray)) else [old]
            for x in olds:
                if not is_number(x):
                    raise SimplydataError(f"The old value needs to be a number (you gave {x!r})."
                                          + f"\nFor example:  {name}.replace_each_number_that(-999, with_value=None)")
            options = {"one_of": olds} if len(olds) > 1 else {"equal_to": olds[0]}
        cond, words = self._condition("replace_each_number_that", options, ())
        n, total = int(cond.sum()), self._values.size
        if words.startswith("are "):
            words = "that were " + words[4:]
        values = self._values
        if with_value is None:
            new, said = np.where(cond, np.nan, values.astype(float)), "empty"
        else:
            new, said = np.where(cond, with_value, values), say(with_value)
        if with_value is None:
            print(f"Made {n} of {amount(total)} empty: the numbers {words}.")
        else:
            print(f"Replaced {n} of {amount(total)} {words} with {said}.")
        return self._change(f"replace numbers {words} with {said}", new)


class PickingWords(ReplacingWords):
    # ================================================================== helpers
    def _keep(self, what: str, keep_mask, kept_word: bool = True):
        before = self._values.size
        new = self._values[keep_mask]
        if kept_word:
            print(f"Kept {new.size} of {amount(before)}.")
        else:
            print(f"Removed {before - new.size} of {amount(before)}. {new.size} left.")
        return self._change(what, new)

    def _check_position(self, step, position, option="position"):
        example = f"{step}(1)" if option == "position" else f"{step}(row=1, column=2)"
        n = self._values.size if option == "position" else self._values.shape[0 if option == "row" else 1]
        if isinstance(position, str) and position.strip().lower() == "last" and n:
            return n - 1
        if not isinstance(position, (int, np.integer)) or isinstance(position, bool) or not 1 <= position <= n:
            if n == 0:
                raise SimplydataError(f"There are no {option}s to pick from: these {self._noun} are empty.")
            raise SimplydataError(
                f"{option} needs a whole number from 1 to {n}, or \"last\": positions count from 1, so 1 is "
                f"the first and {n} is the last." + self._example(example)
            )
        return int(position) - 1

    # ================================================================== looking
    @friendly
    def get_number_at(self, position=None):
        """The number at a position, counting from 1: get_number_at(1) is the first number.

        numbers.get_number_at(1)
        Positions count from 1, the way people count and the way charts number the x axis.
        get_number_at("last") is the last number.
        """
        return plain(self._values[self._check_position("get_number_at", position)])

    @friendly
    def show_first_numbers(self, how_many=5):
        """Show the first numbers. numbers.show_first_numbers(5)"""
        n = check_whole("show_first_numbers", "show_first_numbers()", how_many, "numbers.show_first_numbers(5)")
        print(np.array2string(self._values[:n], threshold=sys.maxsize, separator=", "))
        return None

    @friendly
    def show_last_numbers(self, how_many=5):
        """Show the last numbers. numbers.show_last_numbers(5)"""
        n = check_whole("show_last_numbers", "show_last_numbers()", how_many, "numbers.show_last_numbers(5)")
        print(np.array2string(self._values[self._values.size - min(n, self._values.size):],
                              threshold=sys.maxsize, separator=", "))
        return None

    # ================================================================== by position
    def _positions_picked(self, step: str, positions, to, step_size, example: str):
        return read_positions(
            step, positions, to, step_size, self._values.size, noun="position", count_noun="numbers",
            owner="There are", example=example, last_hint="numbers.keep_last_numbers(3)",
            after_hint="to turn the order round use numbers.reverse()", name="numbers",
            other_hint=lambda v: ("To keep numbers by their values use numbers.keep_each_number_that(is_above=50)."
                                  if isinstance(v, str) else None),
        )

    def _no_value_conditions(self, step: str, conditions: dict):
        if not conditions:
            return
        key = next(iter(conditions))
        if key in CONDITIONS or key[3:] in CONDITIONS:
            verb = step.split("_")[0]
            raise SimplydataError(
                f".{step}() chooses numbers by their place in the list, not by their values.\n"
                f"For numbers whose values meet a condition write numbers.{verb}_each_number_that({_is(key)}=...).\n"
                "For example:  numbers.keep_each_number_that(is_above=50)"
            )
        raise option_error(step, key, ["positions", "to", "step"])

    @friendly
    def keep_numbers_by_position(self: _Same, positions=None, to=None, step=None, **conditions) -> _Same:
        """Keep numbers by their position, counting from 1: a run, every n-th number, or a list.

        numbers.keep_numbers_by_position(2, to=4)
        Both ends are included. to="last" goes to the end; step=2 keeps every 2nd number; a list
        such as [1, 4] keeps those numbers in that order. As NumPy a[1:4] (positions, not values:
        keep_each_number_that(is_between=[2, 4]) keeps the values from 2 to 4).
        """
        example = "numbers.keep_numbers_by_position(3, to=8)"
        self._no_value_conditions("keep_numbers_by_position", conditions)
        picked = self._positions_picked("keep_numbers_by_position", positions, to, step, example)
        total = self._values.size
        new = self._values[picked.array()].copy()
        what = "the number at" if len(picked) == 1 else "the numbers at"
        print(f"Kept {what} {picked.words()}{picked.in_order()} ({new.size} of {amount(total)}).")
        if picked.note:
            print(picked.note.format(verb="kept"))
        return self._change(f"keep {what} {picked.short_words()}", new)

    @friendly
    def remove_numbers_by_position(self: _Same, positions=None, to=None, step=None, **conditions) -> _Same:
        """Remove numbers by their position, counting from 1: a run, every n-th number, or a list.

        numbers.remove_numbers_by_position("last")
        The opposite of keep_numbers_by_position, with the same positions. As NumPy np.delete(a, -1).
        """
        example = 'numbers.remove_numbers_by_position("last")'
        self._no_value_conditions("remove_numbers_by_position", conditions)
        picked = self._positions_picked("remove_numbers_by_position", positions, to, step, example)
        total = self._values.size
        if len(picked) == total:
            raise SimplydataError("That would remove every number. Keep at least one.\nFor example:  " + example)
        new = self._values[picked.kept_positions(total)].copy()
        what = "the number at" if len(picked) == 1 else "the numbers at"
        print(f"Removed {what} {picked.words()} ({len(picked)} of {amount(total)}). {new.size} left.")
        if picked.note:
            print(picked.note.format(verb="removed"))
        return self._change(f"remove {what} {picked.short_words()}", new)

    # ================================================================== keeping and removing
    @friendly(renamed={"above": "is_above", "below": "is_below", "at_least": "is_at_least", "at_most": "is_at_most",
                       "equal_to": "is_equal_to", "not_equal_to": "is_not_equal_to", "between": "is_between",
                       "one_of": "is_one_of"})
    def keep_each_number_that(self: _Same, *extra, is_above=NOT_GIVEN, is_below=NOT_GIVEN, is_at_least=NOT_GIVEN, is_at_most=NOT_GIVEN,
                              is_equal_to=NOT_GIVEN, is_not_equal_to=NOT_GIVEN, is_between=NOT_GIVEN, is_one_of=NOT_GIVEN,
                              is_empty=NOT_GIVEN) -> _Same:
        """Keep only the numbers that match one condition. numbers.keep_each_number_that(is_above=50)

        Conditions (the same as table.keep_rows_where): is_above, is_below, is_at_least, is_at_most, is_equal_to,
        is_not_equal_to, is_between=[low, high] (both ends included), is_one_of=[...], is_empty=True.
        Empty values only match is_empty.
        """
        options = dict(above=is_above, below=is_below, at_least=is_at_least, at_most=is_at_most, equal_to=is_equal_to,
                       not_equal_to=is_not_equal_to, between=is_between, one_of=is_one_of, is_empty=is_empty)
        cond, words = self._condition("keep_each_number_that", options, extra)
        return self._keep(f"keep numbers {words}", cond)

    @friendly(renamed={"above": "is_above", "below": "is_below", "at_least": "is_at_least", "at_most": "is_at_most",
                       "equal_to": "is_equal_to", "not_equal_to": "is_not_equal_to", "between": "is_between",
                       "one_of": "is_one_of"})
    def remove_each_number_that(self: _Same, *extra, is_above=NOT_GIVEN, is_below=NOT_GIVEN, is_at_least=NOT_GIVEN, is_at_most=NOT_GIVEN,
                                is_equal_to=NOT_GIVEN, is_not_equal_to=NOT_GIVEN, is_between=NOT_GIVEN, is_one_of=NOT_GIVEN,
                                is_empty=NOT_GIVEN) -> _Same:
        """Remove the numbers that match one condition (the opposite of keep_each_number_that).

        numbers.remove_each_number_that(is_below=0)
        Same conditions as keep_each_number_that; is_between=[low, high] includes both ends.
        """
        options = dict(above=is_above, below=is_below, at_least=is_at_least, at_most=is_at_most, equal_to=is_equal_to,
                       not_equal_to=is_not_equal_to, between=is_between, one_of=is_one_of, is_empty=is_empty)
        cond, words = self._condition("remove_each_number_that", options, extra)
        return self._keep(f"remove numbers {words}", ~cond, kept_word=False)

    @friendly
    def keep_first_numbers(self: _Same, how_many=5) -> _Same:
        """Keep only the first numbers. numbers.keep_first_numbers(10)"""
        n = check_whole("keep_first_numbers", "keep_first_numbers()", how_many, "numbers.keep_first_numbers(10)")
        mask = np.arange(self._values.size) < n
        return self._keep(f"keep the first {amount(n)}", mask)

    @friendly
    def keep_last_numbers(self: _Same, how_many=5) -> _Same:
        """Keep only the last numbers. numbers.keep_last_numbers(10)"""
        n = check_whole("keep_last_numbers", "keep_last_numbers()", how_many, "numbers.keep_last_numbers(10)")
        mask = np.arange(self._values.size) >= self._values.size - n
        return self._keep(f"keep the last {amount(n)}", mask)

    @friendly(renamed={"seed": "with_seed"})
    def keep_random_numbers(self: _Same, how_many=5, with_seed=None) -> _Same:
        """Keep some numbers picked at random (they keep their order); a seed gives the same pick every time.

        numbers.keep_random_numbers(10, with_seed=1)
        """
        example = "numbers.keep_random_numbers(10, with_seed=1)"
        n = check_whole("keep_random_numbers", "keep_random_numbers()", how_many, example)
        with_seed = check_seed(with_seed, example)
        size = self._values.size
        if n > size:
            print(f"There are only {amount(size)}, so all of them are kept.")
            n = size
        picked = np.random.default_rng(with_seed).choice(size, size=n, replace=False)
        mask = np.zeros(size, dtype=bool)
        mask[picked] = True
        what = f"keep {n} random numbers" + (f" (seed {with_seed})" if with_seed is not None else "")
        return self._keep(what, mask)

    @friendly
    def remove_empty_numbers(self: _Same) -> _Same:
        """Remove the empty (missing) values. numbers.remove_empty_numbers()"""
        return self._keep("remove empty values", ~self._empty_mask(), kept_word=False)

    @friendly
    def remove_duplicate_numbers(self: _Same) -> _Same:
        """Remove numbers that repeat an earlier number, so each number is left once, in its first place.

        numbers.remove_duplicate_numbers()
        """
        import pandas as pd

        mask = ~pd.Series(self._values).duplicated().to_numpy()
        return self._keep("remove duplicate numbers", mask, kept_word=False)

    @friendly
    def fill_empty_numbers(self: _Same, with_value=None, with_the=None) -> _Same:
        """Fill the empty values with a number, or with the average, median, value above or value below.

        numbers.fill_empty_numbers(with_value=0)   or   numbers.fill_empty_numbers(with_the="average")
        with_the="line between neighbours" fills each gap on the straight line between the
        values just before and just after it; empty values at the start or end stay empty.
        """
        if (with_value is None) == (with_the is None):
            raise SimplydataError(
                ".fill_empty_numbers() needs exactly one of with_value= or with_the=."
                + self._example("fill_empty_numbers(with_value=0)")
                + self._example('fill_empty_numbers(with_the="average")')
            )
        if with_value is not None and not is_number(with_value):
            raise SimplydataError("with_value= needs a number, like with_value=0." + self._example("fill_empty_numbers(with_value=0)"))
        choice = None if with_the is None else str(with_the).strip().lower().replace("_", " ")
        if choice is not None:
            choice = choice.replace("neighbors", "neighbours")
        if choice is not None and choice not in FILL_CHOICES:
            raise choice_error("fill_empty_numbers", "with_the", with_the, FILL_CHOICES)
        empty = self._empty_mask()
        if not empty.any():
            print("There are no empty values to fill.")
            return self
        v = self._values.astype(float)
        if choice is None:
            new, how = np.where(empty, float(with_value), v), say(with_value)
        else:
            if choice in ("average", "median"):
                if empty.all():
                    raise SimplydataError(f"There are no numbers at all, so there is no {choice} to fill with.")
                value = np.nanmean(v) if choice == "average" else np.nanmedian(v)
                new = np.where(empty, value, v)
            elif choice == "line between neighbours":
                from .._stats import line_between_neighbours

                new = line_between_neighbours(np.where(empty, np.nan, v))
            else:
                import pandas as pd

                series = pd.Series(v)
                new = (series.ffill() if choice == "value above" else series.bfill()).to_numpy()
            how = f"the {choice}"
        left = int(np.isnan(new).sum())
        filled = int(empty.sum()) - left
        why = ("at the start or end, with a neighbour on one side only" if choice == "line between neighbours"
               else "nothing to copy from")
        print(f"Filled {amount(filled, 'empty value')}."
              + (f" {amount(left, 'value')} stayed empty ({why})." if left else ""))
        return self._change(f"fill empty values with {how}", new)

    # ================================================================== order
    @friendly
    def sort(self: _Same, biggest_first=False) -> _Same:
        """Put the numbers in order, smallest first; empty values go last. numbers.sort(biggest_first=True)"""
        if not isinstance(biggest_first, bool):
            raise SimplydataError("biggest_first= needs True or False (no quotes)." + self._example("sort(biggest_first=True)"))
        empty = self._empty_mask()
        filled = np.sort(self._values[~empty], kind="stable")
        if biggest_first:
            filled = filled[::-1]
        new = np.concatenate([filled, self._values[empty]])
        return self._change("sort, biggest first" if biggest_first else "sort, smallest first", new)

    @friendly
    def reverse(self: _Same) -> _Same:
        """Turn the order round: the last number comes first. numbers.reverse()"""
        return self._change("reverse", self._values[::-1].copy())

    @friendly
    def turn_into_running_total(self: _Same) -> _Same:
        """Each number becomes the total so far (the cumulative sum): 1, 2, 3 becomes 1, 3, 6.

        numbers.turn_into_running_total()
        Empty values stay empty and are skipped in the total, like pandas cumsum().
        """
        empty = self._empty_mask()
        totals = np.cumsum(np.where(empty, 0, self._values))
        if empty.any():
            totals = np.where(empty, np.nan, totals)
        return self._change("running total", totals)

    # ================================================================== into a grid
    @friendly
    def make_number_grid(self, rows=None, columns=None):
        """Make a NEW grid from these numbers, filled row by row. grid = numbers.make_number_grid(columns=3)

        Give rows= or columns= (or both); the numbers must fill the grid exactly.
        """
        from .numbers import number_grid

        return number_grid(self, rows=rows, columns=columns)
