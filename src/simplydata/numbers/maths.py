"""Maths words. They CHANGE the numbers you have, and undo() takes them back.

For NEW numbers use the symbols instead: numbers + 5, numbers * 2, numbers ** 2. Both give the
same answer, because they share one calculation (see _base.calculate).
"""

from __future__ import annotations

from .._typing import _Same

import numbers as _nb

import numpy as np

from .._errors import SimplydataError, friendly
from ._base import is_number, note_empty, say
from .function_words import FunctionWords


class MathsWords(FunctionWords):  # take_function and work_on_bits: families for 100 % (function_words.py)
    # ------------------------------------------------------------------ the four sums and power
    @friendly
    def add(self: _Same, number=None) -> _Same:
        """Add a number to every number (or add numbers one by one). numbers.add(5)

        For new numbers, write bigger = numbers + 5 instead.
        """
        return self._sum_word("add", number)

    @friendly
    def subtract(self: _Same, number=None) -> _Same:
        """Take a number away from every number. numbers.subtract(2)

        For new numbers, write smaller = numbers - 2 instead.
        """
        return self._sum_word("subtract", number)

    @friendly
    def times(self: _Same, number=None) -> _Same:
        """Multiply every number by a number. numbers.times(2)

        For new numbers, write double = numbers * 2 instead.
        """
        return self._sum_word("times", number)

    @friendly
    def divide_by(self: _Same, number=None, rounding_down=False) -> _Same:
        """Divide every number by a number. numbers.divide_by(4)

        Dividing by 0 has no answer, so those values become empty and a note says how many.
        rounding_down=True keeps the whole part, rounded down, also for minus numbers: -7 divided by 2 gives -4
        (NumPy floor_divide, Python's //). For new numbers, write quarter = numbers / 4 instead.
        """
        if rounding_down is True:
            return self._floor_divide(number)
        if rounding_down is not False:
            raise SimplydataError("rounding_down= needs True or False (no quotes)." + self._example("divide_by(7, rounding_down=True)"))
        return self._sum_word("divide_by", number)

    @friendly
    def raise_to_power(self: _Same, number=None) -> _Same:
        """Raise every number to a power: raise_to_power(2) squares, raise_to_power(3) cubes. numbers.raise_to_power(2)

        raise_to_power(0.5) is the same as the square root. For new numbers, write squares = numbers ** 2.
        """
        return self._sum_word("power", number)

    # ------------------------------------------------------------------ one number at a time
    def _each(self, what: str, values, n_empty: int = 0, why: str = ""):
        note_empty(n_empty, why)
        return self._change(what, values)

    @friendly
    def take_square_root(self: _Same) -> _Same:
        """The square root of every number: 9 becomes 3. numbers.take_square_root()

        Negative numbers have no square root among ordinary numbers, so they become empty.
        """
        v = self._values
        negative = v < 0
        with np.errstate(all="ignore"):
            result = np.where(negative, np.nan, np.sqrt(v.astype(float)))
        return self._each("square root", result, int(negative.sum()),
                          "a negative number has no square root")

    @friendly
    def take_absolute_value(self: _Same) -> _Same:
        """Every number without its minus sign: -3 becomes 3. numbers.take_absolute_value()"""
        return self._each("absolute value", np.abs(self._values))

    @friendly(renamed={"decimals": "with_decimals"})
    def round_to(self: _Same, with_decimals=0) -> _Same:
        """Round every number to this many decimal places. numbers.round_to(2)

        A number exactly halfway goes to the even neighbour (2.5 becomes 2, 3.5 becomes 4),
        like R and NumPy; this stops a run of halves from always pushing totals up.
        round_to(0) gives whole numbers; round_to(-1) rounds to tens.
        """
        if not isinstance(with_decimals, _nb.Integral) or isinstance(with_decimals, bool):
            raise SimplydataError(
                ".round_to() needs a whole number of decimal places, like 2." + self._example("round_to(2)")
            )
        with_decimals = int(with_decimals)
        places = "decimal place" if with_decimals == 1 else "decimal places"
        return self._each(f"round to {with_decimals} {places}", np.round(self._values, with_decimals))

    @friendly
    def take_log(self: _Same, base="e") -> _Same:
        """The logarithm of every number: natural (base e) unless you give base=10 or base=2.

        numbers.take_log()  numbers.take_log(base=10)  numbers.take_log(base=2)
        take_log(base=10) of 1000 is 3, because 10 x 10 x 10 = 1000. The log only exists for
        numbers above 0, so 0 and negative numbers become empty.
        """
        if not (base == "e" or (is_number(base) and base > 0 and base != 1)):
            raise SimplydataError(
                '.take_log() needs base= as a number above 0 (but not 1), such as base=10 or base=2, or base="e" '
                "(the natural log, the default)." + self._example("take_log(base=10)")
            )
        v = self._values.astype(float)
        bad = v <= 0
        with np.errstate(all="ignore"):
            if base == "e":
                result, what = np.log(v), "natural log"
            elif base == 10:
                result, what = np.log10(v), "log base 10"
            elif base == 2:
                result, what = np.log2(v), "log base 2"
            else:
                result, what = np.log(v) / np.log(float(base)), f"log base {say(base)}"
        result = np.where(bad, np.nan, result)
        return self._each(what, result, int(bad.sum()), "the log only exists for numbers above 0")

    @friendly
    def take_exp(self: _Same) -> _Same:
        """e (about 2.718) to the power of every number; it undoes take_log(). numbers.take_exp()"""
        with np.errstate(all="ignore"):
            result = np.exp(self._values.astype(float))
        too_big = int((np.isinf(result) & np.isfinite(self._values)).sum())
        if too_big:
            print(f"Note: {too_big} {'answer is' if too_big == 1 else 'answers are'} too big to hold "
                  "and shown as inf (infinity).")
        return self._each("exp", result)
