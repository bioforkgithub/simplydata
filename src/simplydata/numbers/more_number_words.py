"""Words for numbers, grids and blocks alike (the NumPy + SciPy phase, batch 1; approved by Manish 2026-11-25).

* rounding: round_down, round_up, take_whole_part (round_to, on main, rounds to the nearest)
* angles: take_sin, take_cos, take_tan (radians, as NumPy; degrees=True for degrees), change_angles_to
* yes or no: turn_into_yes_or_no, keep_numbers_where, remove_numbers_where, replace_numbers_where, & | ~,
  count_numbers_that, check_if_any_number, check_if_all_numbers
* comparing and positions: check_if_same_as, find_where_biggest, find_where_smallest
* every pair: make_pair_table_with

Each word is one NumPy call, named in the sentence it prints.
"""

from __future__ import annotations

from .._typing import _Same

import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from ._base import NOT_GIVEN, BaseNumbers, amount, is_number, note_empty, plain, say, to_array

_CONDITION_OPTIONS = ("is_above", "is_below", "is_at_least", "is_at_most", "is_equal_to", "is_not_equal_to",
                      "is_between", "is_one_of", "is_empty")
ANGLE_UNITS = ("degrees", "radians")


def _short(option: str) -> str:
    return option if option == "is_empty" else option[3:]


def _bool_array(value):
    """True/False values given as numbers, grids, blocks, lists or NumPy arrays: a NumPy bool array, or None."""
    if isinstance(value, BaseNumbers):
        arr = value._values
    elif isinstance(value, (list, tuple, np.ndarray)) or isinstance(value, (bool, np.bool_)):
        try:
            arr = np.asarray(value)
        except (ValueError, TypeError):
            return None
    else:
        return None
    return arr if arr.dtype.kind == "b" else None


class MoreNumberWords:
    """Shared by Numbers, NumberGrid and NumberBlock."""

    # ------------------------------------------------------------------ what each kind of object provides
    def _like(self, values):
        """New numbers of the same kind (and, for a block, the same directions)."""
        return type(self)(np.asarray(values))

    def _direction_names(self) -> list[str]:
        if getattr(self, "_names", None) is not None:
            return list(self._names)
        return ["number"] if self._values.ndim == 1 else ["row", "column"]

    def _reduce_axes(self, step: str, over, in_each) -> list[int] | None:
        """The NumPy axes a word runs through: over= the directions that go, in_each= the ones kept."""
        if over is None and in_each is None:
            return None
        if hasattr(self, "_summary_axes"):
            return self._summary_axes(step, over, in_each)
        names = self._direction_names()
        if self._values.ndim == 1:
            raise SimplydataError(f".{step}() on numbers has no over= or in_each=: numbers have one direction.")
        if over is not None and in_each is not None:
            raise SimplydataError(f".{step}() takes over= or in_each=, not both.")
        given, option = (over, "over") if over is not None else (in_each, "in_each")
        if given not in names:
            raise choice_error(step, option, given, names)
        axis = names.index(given)
        return [axis] if option == "over" else [1 - axis]

    def _after_reducing(self, result, axes):
        """A result with these axes gone: a block keeps the other names; a grid gives numbers."""
        from .numbers import Numbers

        result = np.asarray(result)
        if hasattr(self, "_summary_axes"):
            from .blocks import NumberBlock

            kept = [i for i in range(self._values.ndim) if i not in axes]
            return NumberBlock(result, [self._names[i] for i in kept], [self._named[i] for i in kept],
                               {n: v for n, v in self._labels.items() if n in [self._names[i] for i in kept]})
        return Numbers(result)

    def _mask_from(self, yes_no, step: str):
        """Yes/no values that line up with these numbers (same shape, or stretchable)."""
        mask = _bool_array(yes_no)
        if mask is None:
            raise SimplydataError(
                f".{step}() needs yes or no values (True/False), one for each number. Make them with a test:\n"
                f"For example:  deep = depth.turn_into_yes_or_no(is_above=100)   then   "
                f"{self._name}.{step}(deep)")
        if hasattr(self, "_summary_axes"):
            from ._directions import line_up

            other_names = yes_no._names if getattr(yes_no, "_is_simplydata_block", False) else None
            other_named = yes_no._named if other_names else [False] * mask.ndim
            from ._directions import default_names

            lined = line_up(self._values, self._names, self._named, mask, other_names or default_names(mask.ndim),
                            other_named, step=step, owner=self._name)
            full = np.broadcast_to(lined.b, np.broadcast_shapes(np.shape(lined.a), np.shape(lined.b)))
            if full.shape != self._values.shape:
                raise SimplydataError(f"The yes or no values would change the shape of the block; give one for each "
                                      f"number.\nFor example:  {self._name}.{step}(yes_no)")
            return np.array(full)
        try:
            return np.broadcast_to(mask, self._values.shape)
        except ValueError:
            raise SimplydataError(
                f"There are {amount(mask.size, 'yes or no value')} but {amount(self._values.size)}: they need to "
                f"line up (the same shape).\nFor example:  {self._name}.{step}(yes_no)") from None

    def _condition_from(self, step: str, given: dict, allow_none_for_yes_no=True):
        """The numbers that pass one condition (is_above=, is_between= ...), and the words for it."""
        conditions = {k: v for k, v in given.items() if v is not NOT_GIVEN}
        if not conditions and allow_none_for_yes_no and self._values.dtype.kind == "b":
            return self._values.copy(), "are yes"
        if self._values.dtype.kind == "b":
            if len(conditions) == 1 and next(iter(conditions)) == "is_equal_to" \
                    and isinstance(conditions["is_equal_to"], (bool, np.bool_)):
                value = bool(conditions["is_equal_to"])
                return np.equal(self._values, value), f"are {'yes' if value else 'no'}"
        options = {_short(k): v for k, v in conditions.items()}
        options.update({_short(k): NOT_GIVEN for k in _CONDITION_OPTIONS if k not in conditions})
        cond, words = self._condition(step, options, ())
        return cond, (words if words.startswith("are ") else "are " + words)

    def _need_yes_no(self, symbol, other_values=None):
        if self._values.dtype.kind != "b" or (other_values is not None and np.asarray(other_values).dtype.kind != "b"):
            raise SimplydataError(
                f"{symbol} joins yes or no values. Make them first with a test, such as:\n"
                f"warm = sst.turn_into_yes_or_no(is_above=20); salty = salt.turn_into_yes_or_no(is_above=35); "
                f"both = warm {symbol} salty")

    # ------------------------------------------------------------------ rounding (decision 4)
    def _whole(self, step, func, what):
        if self._values.dtype.kind in "iub":
            print(f"The numbers are whole numbers already, so {what} changes nothing.")
            return self._change(what, self._values.copy())
        with np.errstate(all="ignore"):
            new = func(self._values)
        print(f"{what[0].upper()}{what[1:]}. NumPy: np.{func.__name__}({self._name})")
        return self._change(what, new)

    @friendly
    def round_down(self: _Same) -> _Same:
        """Round every number down to a whole number: 2.7 becomes 2 and -2.3 becomes -3 (NumPy floor). numbers.round_down()"""
        return self._whole("round_down", np.floor, "round down to whole numbers")

    @friendly
    def round_up(self: _Same) -> _Same:
        """Round every number up to a whole number: 2.1 becomes 3, -2.7 becomes -2 (NumPy ceil). numbers.round_up()"""
        return self._whole("round_up", np.ceil, "round up to whole numbers")

    @friendly
    def take_whole_part(self: _Same) -> _Same:
        """Keep the whole part of every number, dropping the decimals: 2.7 becomes 2 and -2.7 becomes -2 (NumPy trunc).

        numbers.take_whole_part()
        round_down goes down (-2.7 becomes -3); take_whole_part goes towards 0.
        """
        return self._whole("take_whole_part", np.trunc, "take the whole part")

    # ------------------------------------------------------------------ angles (decision 5: radians, as NumPy)
    def _trig(self, func, degrees):
        if not isinstance(degrees, bool):
            raise SimplydataError(f"degrees= needs True or False (no quotes).{self._example(f'take_{func.__name__}(degrees=True)')}")
        values = self._values.astype(float)
        with np.errstate(all="ignore"):
            new = func(np.deg2rad(values)) if degrees else func(values)
        unit = "degrees" if degrees else "radians (degrees=True for degrees)"
        call = f"np.{func.__name__}(np.deg2rad({self._name}))" if degrees else f"np.{func.__name__}({self._name})"
        print(f"The {func.__name__} of every number; angles in {unit}. NumPy: {call}")
        return self._change(f"take {func.__name__}" + (" (degrees)" if degrees else ""), new)

    @friendly
    def take_sin(self: _Same, degrees=False) -> _Same:
        """The sine of every number; angles in radians, as NumPy, or degrees=True. numbers.take_sin(degrees=True)"""
        return self._trig(np.sin, degrees)

    @friendly
    def take_cos(self: _Same, degrees=False) -> _Same:
        """The cosine of every number; angles in radians, as NumPy, or degrees=True. numbers.take_cos(degrees=True)"""
        return self._trig(np.cos, degrees)

    @friendly
    def take_tan(self: _Same, degrees=False) -> _Same:
        """The tangent of every number; angles in radians, as NumPy, or degrees=True. numbers.take_tan(degrees=True)

        At 90 degrees the tangent has no finite value; NumPy gives a very big number there.
        """
        return self._trig(np.tan, degrees)

    @friendly
    def change_angles_to(self: _Same, unit=None, remove_jumps=False) -> _Same:
        """Change angles between radians and degrees (NumPy rad2deg, deg2rad). numbers.change_angles_to("degrees")

        remove_jumps=True: the angles are already in unit=, and each jump of a whole turn (from 359 to 1 degree, say)
        is taken out, so they run on smoothly (NumPy unwrap, period 2 pi or 360).
        """
        if unit not in ANGLE_UNITS:
            raise choice_error("change_angles_to", "unit", unit, list(ANGLE_UNITS))
        if not isinstance(remove_jumps, bool):
            raise SimplydataError("remove_jumps= needs True or False (no quotes).")
        if remove_jumps:
            period = 360.0 if unit == "degrees" else 2 * np.pi
            new = np.unwrap(self._values.astype(float), period=period)
            print(f"Jumps of a whole turn taken out of the angles in {unit} (NumPy unwrap, period "
                  f"{'360' if unit == 'degrees' else '2 pi'}).")
            return self._change(f"remove jumps in angles ({unit})", new)
        func = np.rad2deg if unit == "degrees" else np.deg2rad
        other = "radians" if unit == "degrees" else "degrees"
        new = func(self._values.astype(float))
        print(f"Angles changed from {other} to {unit}. NumPy: np.{func.__name__}({self._name})")
        return self._change(f"change angles to {unit}", new)

    def _floor_divide(self, number, over=None):
        if hasattr(self, "_lined_up"):
            lined, b, _ = self._lined_up(number, "divide_by", over)
            a, b = lined.a, lined.b
        else:
            a, b = self._values, self._operand(number, "divide_by")
        with np.errstate(all="ignore"):
            result = np.floor_divide(a, b)
        zero = np.broadcast_to(np.equal(b, 0), np.shape(result))
        filled = ~np.isnan(np.broadcast_to(np.asarray(a, dtype=float), np.shape(result)))
        n = int(np.count_nonzero(zero & filled))
        if zero.any():
            result = np.where(zero, np.nan, result)
        if np.shape(result) != self._values.shape:
            raise SimplydataError(f"{self._name}.divide_by() would change the shape of your numbers. Use // to make "
                                  f"new ones:  new = {self._name}.as_numpy() // other")
        note_empty(n, "dividing by 0 has no answer")
        print(f"Divided and rounded down to whole numbers. NumPy: np.floor_divide({self._name}, other)")
        return self._change("divide, rounding down", result)

    # ------------------------------------------------------------------ yes or no (P01, P02, P08, P09, P37)
    @friendly
    def turn_into_yes_or_no(self, *extra, is_above=NOT_GIVEN, is_below=NOT_GIVEN, is_at_least=NOT_GIVEN,
                            is_at_most=NOT_GIVEN, is_equal_to=NOT_GIVEN, is_not_equal_to=NOT_GIVEN,
                            is_between=NOT_GIVEN, is_one_of=NOT_GIVEN, is_empty=NOT_GIVEN):
        """New yes or no values, one for each number: yes where the number passes the test. warm = numbers.turn_into_yes_or_no(is_above=20)

        The same conditions as keep_each_number_that; empty numbers are no (except is_empty=True). Join tests with
        & (both), | (either) and ~ (not): warm & ~salty. The numbers themselves do not change.
        NumPy: numbers > 20 (a bool array).
        """
        if extra:
            raise SimplydataError("turn_into_yes_or_no() needs one condition, like is_above=20."
                                  + self._example("turn_into_yes_or_no(is_above=20)"))
        given = dict(is_above=is_above, is_below=is_below, is_at_least=is_at_least, is_at_most=is_at_most,
                     is_equal_to=is_equal_to, is_not_equal_to=is_not_equal_to, is_between=is_between,
                     is_one_of=is_one_of, is_empty=is_empty)
        cond, words = self._condition_from("turn_into_yes_or_no", given, allow_none_for_yes_no=False)
        cond = np.asarray(cond, dtype=bool)
        print(f"{amount(cond.size, 'yes or no value')} (NumPy bool): {int(np.count_nonzero(cond))} yes "
              f"(the numbers that {words}).")
        return self._like(cond)

    def __invert__(self):
        self._need_yes_no("~")
        return self._like(np.logical_not(self._values))

    def _yes_no_join(self, how, other):
        """& and | on yes or no values: NumPy logical_and / logical_or (a block on the other side lines them up)."""
        if getattr(other, "_is_simplydata_block", False):
            return NotImplemented
        b = _bool_array(other)
        symbol = "&" if how == "and" else "|"
        if b is None:
            if isinstance(other, (BaseNumbers, list, tuple, np.ndarray)):
                self._need_yes_no(symbol, np.asarray(getattr(other, "_values", other)))
            return NotImplemented
        self._need_yes_no(symbol, b)
        try:
            result = (np.logical_and if how == "and" else np.logical_or)(self._values, b)
        except ValueError:
            raise SimplydataError(f"{symbol} needs yes or no values of the same shape on both sides "
                                  f"({self._values.shape} against {b.shape}).") from None
        return self._like(result) if result.shape == self._values.shape else self._wrap(result)

    def __and__(self, other):
        return self._yes_no_join("and", other)

    def __rand__(self, other):
        return self._yes_no_join("and", other)

    def __or__(self, other):
        return self._yes_no_join("or", other)

    def __ror__(self, other):
        return self._yes_no_join("or", other)

    @friendly
    def keep_numbers_where(self: _Same, yes_no=None) -> _Same:
        """Keep the numbers where the yes or no values say yes. numbers.keep_numbers_where(deep)

        deep = depth.turn_into_yes_or_no(is_above=100) makes the yes or no values. Numbers drop the others (NumPy
        numbers[deep]); a grid or block keeps its shape and the others become empty (NumPy np.where(deep, numbers, nan);
        xarray's where does the same).
        """
        return self._where("keep_numbers_where", yes_no, keep=True)

    @friendly
    def remove_numbers_where(self: _Same, yes_no=None) -> _Same:
        """Remove the numbers where the yes or no values say yes. numbers.remove_numbers_where(land)

        Numbers drop them (NumPy numbers[~land]); a grid or block keeps its shape and they become empty.
        """
        return self._where("remove_numbers_where", yes_no, keep=False)

    def _where(self, step, yes_no, keep):
        mask = self._mask_from(yes_no, step)
        chosen = mask if keep else np.logical_not(mask)
        total = self._values.size
        n = int(np.count_nonzero(chosen))
        if self._values.ndim == 1 and not hasattr(self, "_summary_axes"):
            new = self._values[chosen]
            print(f"{'Kept' if keep else 'Removed'} {n if keep else total - n} of {amount(total)}"
                  f"{'' if keep else f'; {n} left'}. NumPy: {self._name}[{'' if keep else '~'}yes_no]")
            return self._change(f"{'keep' if keep else 'remove'} numbers where yes", new)
        new = np.where(chosen, self._values, np.nan)
        kind = {"b": "yes or no values", "i": "whole numbers", "u": "whole numbers"}.get(self._values.dtype.kind)
        made_decimal = (f" The {kind} became decimal numbers (1 for yes, 0 for no)" if kind == "yes or no values" else
                        f" The {kind} became decimal numbers" if kind else "")
        made_decimal += ", because NumPy whole numbers cannot be empty." if kind else ""
        print(f"{'Kept' if keep else 'Removed'} {n if keep else total - n} of {amount(total)}; the others are now "
              f"empty, so the shape stays.{made_decimal} NumPy: np.where({'' if keep else '~'}yes_no, {self._name}, "
              "np.nan). "
              f"As a list:  {self._name}.get_all_numbers().keep_numbers_where(yes_no.get_all_numbers())")
        return self._change(f"{'keep' if keep else 'remove'} numbers where yes", new)

    @friendly
    def replace_numbers_where(self: _Same, yes_no=None, with_value=NOT_GIVEN, at_positions=None,
                              rules=None) -> _Same:
        """Replace the numbers where yes or no values say yes. numbers.replace_numbers_where(land, with_value="empty")

        with_value= a number, "empty" (None works too), or other numbers of the same size (each taken from its own
        place: NumPy copyto). NumPy np.where(land, value, numbers). at_positions= replaces the numbers at these
        positions instead (from 1; on a grid, the table find_positions_where gives, or (row, column) pairs; NumPy
        put). rules=[(cold, -1), (warm, 1)] gives each number the value of the first rule whose yes or no values say
        yes, and leaves the others as they are, or gives them with_value= (NumPy select).
        """
        from .numpy_grid_words import replace_at_positions, replace_by_rules

        if at_positions is not None or rules is not None:
            if sum(v is not None for v in (yes_no, at_positions, rules)) > 1:
                raise SimplydataError("replace_numbers_where() takes yes or no values, at_positions= or rules=: one "
                                      "of them.")
            if at_positions is not None:
                return replace_at_positions(self, at_positions, with_value)
            return replace_by_rules(self, rules, with_value)
        mask = self._mask_from(yes_no, "replace_numbers_where")
        if with_value is NOT_GIVEN:
            raise SimplydataError('replace_numbers_where() needs with_value=, a number or "empty".'
                                  + self._example('replace_numbers_where(land, with_value="empty")'))
        if with_value is None or (isinstance(with_value, str) and with_value == "empty"):
            new, said = np.where(mask, np.nan, self._values.astype(float)), "empty"
        elif is_number(with_value):
            new, said = np.where(mask, with_value, self._values), say(with_value)
        elif isinstance(with_value, (list, tuple, np.ndarray)) or hasattr(with_value, "_values"):
            from ._base import to_array

            other = to_array(with_value, "with_value=", "numbers.replace_numbers_where(land, with_value=other)")
            if other.shape != self._values.shape:
                raise SimplydataError(f"with_value= needs a number, or numbers of the same size as yours "
                                      f"({self._values.size}); it has {other.size}.")
            new = self._values.astype(np.result_type(self._values, other), copy=True)
            np.copyto(new, other, where=mask)
            n = int(np.count_nonzero(mask))
            print(f"Replaced {n} of {amount(self._values.size)} with the other numbers at the same places. NumPy: "
                  f"np.copyto({self._name}, other, where=yes_no)")
            return self._change("replace numbers where yes with other numbers", new)
        else:
            raise SimplydataError(f'with_value= needs a number or "empty" (you gave {with_value!r}).'
                                  + self._example('replace_numbers_where(land, with_value="empty")'))
        n = int(np.count_nonzero(mask))
        print(f"Replaced {n} of {amount(self._values.size)} with {said}. NumPy: np.where(yes_no, "
              f"{'np.nan' if said == 'empty' else said}, {self._name})")
        return self._change(f"replace numbers where yes with {said}", new)

    @friendly
    def count_numbers_that(self, *extra, is_above=NOT_GIVEN, is_below=NOT_GIVEN, is_at_least=NOT_GIVEN,
                           is_at_most=NOT_GIVEN, is_equal_to=NOT_GIVEN, is_not_equal_to=NOT_GIVEN, is_between=NOT_GIVEN,
                           is_one_of=NOT_GIVEN, is_empty=NOT_GIVEN, over=None, in_each=None):
        """How many numbers pass a test, for all of them or along a direction. numbers.count_numbers_that(is_above=25)

        On yes or no values without a test, it counts the yes. Grids and blocks take over= (sst.count_numbers_that(
        is_above=25, over="time") gives warm days per grid cell) or in_each=. NumPy
        np.count_nonzero(numbers > 25, axis=).
        """
        if extra:
            raise SimplydataError("count_numbers_that() needs one condition, like is_above=25."
                                  + self._example("count_numbers_that(is_above=25)"))
        given = dict(is_above=is_above, is_below=is_below, is_at_least=is_at_least, is_at_most=is_at_most,
                     is_equal_to=is_equal_to, is_not_equal_to=is_not_equal_to, is_between=is_between,
                     is_one_of=is_one_of, is_empty=is_empty)
        cond, words = self._condition_from("count_numbers_that", given)
        axes = self._reduce_axes("count_numbers_that", over, in_each)
        if axes is None:
            n = int(np.count_nonzero(cond))
            print(f"{n} of {amount(cond.size)} {words.replace('are ', 'are ', 1) if n != 1 else words.replace('are ', 'is ', 1)}. "
                  f"NumPy: np.count_nonzero(test)")
            return n
        counts = np.count_nonzero(cond, axis=tuple(axes))
        print(f"The count of numbers that {words}, along {self._say_axes(axes)}. "
              f"NumPy: np.count_nonzero(test, axis={axes[0] if len(axes) == 1 else tuple(axes)})")
        return self._after_reducing(counts, axes)

    def _say_axes(self, axes) -> str:
        names = self._direction_names()
        return " and ".join(names[i] for i in axes)

    def _check_all_or_any(self, step, which, given, over):
        cond, words = self._condition_from(step, given)
        empty = self._empty_mask() if hasattr(self, "_empty_mask") else np.zeros(self._values.shape, dtype=bool)
        axes = self._reduce_axes(step, over, None)
        func = np.all if which == "all" else np.any
        # empty numbers are skipped: for "all" they count as passing, for "any" as not passing
        test = np.logical_or(cond, empty) if which == "all" else np.logical_and(cond, np.logical_not(empty))
        if axes is None:
            answer = bool(func(test))
            filled = int(np.count_nonzero(np.logical_not(empty)))
            passing = int(np.count_nonzero(np.logical_and(cond, np.logical_not(empty))))
            what = words[4:] if words.startswith("are ") else words
            if which == "all":
                said = (f"Yes: all {amount(filled)} {words}" if answer else
                        f"No: {filled - passing} of {amount(filled)} {'is' if filled - passing == 1 else 'are'} not {what}")
            else:
                said = (f"Yes: {passing} of {amount(filled)} {'is' if passing == 1 else 'are'} {what}" if answer else
                        f"No: none of the {amount(filled)} {words}")
            skipped = int(np.count_nonzero(empty))
            print(said + (f" ({amount(skipped, 'empty value')} skipped)" if skipped else "")
                  + f". NumPy: np.{which}(test)")
            return answer
        result = func(test, axis=tuple(axes))
        print(f"One answer for each position of the other directions: does {which} along "
              f"{self._say_axes(axes)} pass? NumPy: np.{which}(test, axis={axes[0] if len(axes) == 1 else tuple(axes)})")
        return self._after_reducing(result, axes)

    @friendly
    def check_if_all_numbers(self, *extra, is_above=NOT_GIVEN, is_below=NOT_GIVEN, is_at_least=NOT_GIVEN,
                             is_at_most=NOT_GIVEN, is_equal_to=NOT_GIVEN, is_not_equal_to=NOT_GIVEN,
                             is_between=NOT_GIVEN, is_one_of=NOT_GIVEN, over=None):
        """Check whether every number passes a test: it says so and gives back True or False. numbers.check_if_all_numbers(is_at_least=0)

        Empty numbers are skipped. over= gives one answer for each position of the other directions. NumPy np.all.
        """
        if extra:
            raise SimplydataError("check_if_all_numbers() needs one condition, like is_at_least=0.")
        given = dict(is_above=is_above, is_below=is_below, is_at_least=is_at_least, is_at_most=is_at_most,
                     is_equal_to=is_equal_to, is_not_equal_to=is_not_equal_to, is_between=is_between, is_one_of=is_one_of)
        return self._check_all_or_any("check_if_all_numbers", "all", given, over)

    @friendly
    def check_if_any_number(self, *extra, is_above=NOT_GIVEN, is_below=NOT_GIVEN, is_at_least=NOT_GIVEN,
                            is_at_most=NOT_GIVEN, is_equal_to=NOT_GIVEN, is_not_equal_to=NOT_GIVEN,
                            is_between=NOT_GIVEN, is_one_of=NOT_GIVEN, over=None):
        """Check whether at least one number passes a test: it says so and gives back True or False. numbers.check_if_any_number(is_above=30)

        Empty numbers are skipped. over= gives one answer for each position of the other directions. NumPy np.any.
        """
        if extra:
            raise SimplydataError("check_if_any_number() needs one condition, like is_above=30.")
        given = dict(is_above=is_above, is_below=is_below, is_at_least=is_at_least, is_at_most=is_at_most,
                     is_equal_to=is_equal_to, is_not_equal_to=is_not_equal_to, is_between=is_between, is_one_of=is_one_of)
        return self._check_all_or_any("check_if_any_number", "any", given, over)

    # ------------------------------------------------------------------ comparing (decision 11)
    @friendly
    def check_if_same_as(self, other=None, within=None) -> bool:
        """Check whether these numbers and others are the same: it says so and gives back True or False. numbers.check_if_same_as(other, within=0.001)

        The same shape and the same numbers; two empty values count as the same. within= allows a difference up to
        that much (0.1 + 0.2 is not exactly 0.3 in a computer). NumPy np.array_equal, or np.allclose(rtol=0, atol=within).
        """
        example = f"{self._name}.check_if_same_as(other, within=0.001)"
        if other is None:
            raise SimplydataError(f"check_if_same_as() needs the other numbers.\nFor example:  {example}")
        b = other._values if isinstance(other, BaseNumbers) else to_array(other, ".check_if_same_as()", example)
        if within is not None and (not is_number(within) or within < 0):
            raise SimplydataError(f"within= needs a number from 0 up, the biggest difference allowed.\nFor example:  {example}")
        a = self._values
        if a.shape != b.shape:
            print(f"No: the shapes differ ({tuple(a.shape)} against {tuple(b.shape)}). NumPy: a.shape == b.shape")
            return False
        float_kind = a.dtype.kind == "f" or b.dtype.kind == "f"
        if within is None:
            same = bool(np.array_equal(a, b, equal_nan=float_kind))
            close = np.equal(a, b) | (np.isnan(a.astype(float)) & np.isnan(b.astype(float)))
            call = "np.array_equal(a, b, equal_nan=True)"
        else:
            same = bool(np.allclose(a, b, rtol=0, atol=within, equal_nan=True))
            close = np.isclose(a, b, rtol=0, atol=within, equal_nan=True)
            call = f"np.allclose(a, b, rtol=0, atol={say(within)})"
        if same:
            print(f"Yes: the same {amount(a.size)}" + (f" (within {say(within)})" if within is not None else "")
                  + f". NumPy: {call}")
            return True
        differ = int(np.count_nonzero(np.logical_not(close)))
        first = np.argwhere(np.logical_not(close))[0]
        where = ", ".join(str(int(i) + 1) for i in first)
        print(f"No: {differ} of {amount(a.size)} differ" + (f" by more than {say(within)}" if within is not None else "")
              + f"; the first at position {where}. NumPy: {call}")
        return False

    # ------------------------------------------------------------------ where the biggest is (decision 7)
    def _where_most(self, step, func, over):
        a = self._values
        word = "biggest" if func is np.nanargmax else "smallest"
        if a.size == 0 or (a.dtype.kind == "f" and np.isnan(a).all()):
            raise SimplydataError(f"There are no numbers, so there is no {word} one.")
        names = self._direction_names()
        if over is None:
            with np.errstate(all="ignore"):
                flat = int(func(a))
            index = np.unravel_index(flat, a.shape)
            value = plain(a[index])
            if a.ndim == 1:
                print(f"The {word} number, {say(value)}, is at position {flat + 1} (NumPy index {flat}). "
                      f"NumPy: np.{func.__name__}({self._name})")
                return flat + 1
            where = ", ".join(f"{n} {int(i) + 1}" for n, i in zip(names, index))
            print(f"The {word} number, {say(value)}, is at {where} (NumPy index {tuple(int(i) for i in index)}). "
                  f"NumPy: np.unravel_index(np.{func.__name__}({self._name}), shape)")
            return tuple(int(i) + 1 for i in index)
        axes = self._reduce_axes(step, over, None)
        if len(axes) != 1:
            raise SimplydataError(f"over= names one direction for {step}().")
        try:
            positions = func(a, axis=axes[0])
        except ValueError:
            raise SimplydataError(f"Some {self._say_axes(axes)} has only empty values, so it has no {word} number.") from None
        print(f"The position (from 1) of the {word} number along {self._say_axes(axes)}, for each position of the "
              f"other directions. NumPy: np.{func.__name__}({self._name}, axis={axes[0]}) + 1")
        return self._after_reducing(np.asarray(positions) + 1, axes)

    @friendly
    def find_where_biggest(self, over=None):
        """Where the biggest number is, counting from 1 (NumPy argmax + 1). numbers.find_where_biggest()

        Numbers give its position; grids and blocks its position in every direction, said with names. over= gives
        one position for each position of the other directions: scores.find_where_biggest(over="class"). Empty values are skipped; on a tie, the first.
        """
        return self._where_most("find_where_biggest", np.nanargmax, over)

    @friendly
    def find_where_smallest(self, over=None):
        """Where the smallest number is, counting from 1 (NumPy argmin + 1). numbers.find_where_smallest()

        As find_where_biggest: a position for numbers, one in every direction for grids and blocks, over= for one
        position along a direction.
        """
        return self._where_most("find_where_smallest", np.nanargmin, over)

    # ------------------------------------------------------------------ every pair (P06)
    @friendly
    def make_pair_table_with(self, other=None, by_adding=False, by_subtracting=False, by_multiplying=False,
                             by_dividing=False, as_blocks=False):
        """A new table of every pair: each number with each of the other numbers (NumPy outer). numbers.make_pair_table_with(depths, by_subtracting=True)

        Multiplying is the default (the times table); by_adding=, by_subtracting= or by_dividing=True for the others.
        as_blocks=True puts a copy of the other numbers, times each number, in its place (NumPy kron).
        """
        from .blocks import NumberBlock
        from .numbers import NumberGrid

        example = f"{self._name}.make_pair_table_with(other, by_subtracting=True)"
        if other is None:
            raise SimplydataError(f"make_pair_table_with() needs the other numbers.\nFor example:  {example}")
        switches = {"adding": by_adding, "subtracting": by_subtracting, "multiplying": by_multiplying,
                    "dividing": by_dividing}
        for key, value in [*switches.items(), ("as_blocks", as_blocks)]:
            if not isinstance(value, bool):
                raise SimplydataError(f"{'by_' + key if key != 'as_blocks' else key}= needs True or False (no quotes).")
        chosen = [k for k, v in switches.items() if v]
        if len(chosen) > 1:
            raise SimplydataError(f"Give one of by_adding=, by_subtracting=, by_multiplying=, by_dividing=.\nFor example:  {example}")
        how = chosen[0] if chosen else "multiplying"
        b = other._values if isinstance(other, BaseNumbers) else to_array(other, ".make_pair_table_with()", example)
        a = self._values
        if as_blocks:
            if how != "multiplying":
                raise SimplydataError("as_blocks=True goes with multiplying (the Kronecker product).")
            result = np.kron(a, b)
            call = "np.kron(a, b)"
            names = getattr(self, "_names", None) if result.ndim == a.ndim else None
        else:
            func = {"adding": np.add, "subtracting": np.subtract, "multiplying": np.multiply,
                    "dividing": np.true_divide}[how]
            with np.errstate(all="ignore"):
                result = func.outer(a, b)
            call = f"np.{func.__name__}.outer(a, b)"
            n = 0
            if how == "dividing":
                zero = np.broadcast_to(np.equal(b, 0), result.shape)
                n = int(np.count_nonzero(zero))
                result = np.where(zero, np.nan, result)
            note_empty(n, "dividing by 0 has no answer")
            mine = self._direction_names()
            theirs = list(other._names) if getattr(other, "_is_simplydata_block", False) else \
                (["number"] if b.ndim == 1 else ["row", "column"][-b.ndim:] if b.ndim <= 2 else None)
            if theirs is None:
                from ._directions import default_names
                theirs = default_names(b.ndim)
            names = mine + [f"{t} of other" if t in mine else t for t in theirs]
        print(f"A table of every pair ({how}): {a.size} x {b.size} gives {amount(result.size)}, shape "
              f"{tuple(result.shape)}. NumPy: {call}")
        if result.ndim == 2 and not getattr(self, "_is_simplydata_block", False) \
                and not getattr(other, "_is_simplydata_block", False):
            return NumberGrid(result)
        return NumberBlock(result, names, None)
