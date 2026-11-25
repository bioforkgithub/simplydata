"""Blocks of numbers: numbers with any number of directions (NumPy's n-D arrays), each direction with a name.

    plate = sdata.number_block(of_shape=(24, 8, 12), filled_with=0, directions_named=["hour", "row", "column"])
    plate.find_average(over="hour")       # one average for each row and column: 8 rows x 12 columns remain
    plate.subtract(blank)                 # blank (8 rows x 12 columns) is used again for each of the 24 hours

The words are the words of numbers and grids (decision 2 of the NumPy review, approved by Manish 2026-11-25):
find_shape, get_number_at, get_all_numbers, find_average(over=, in_each=) ... and the block words of the NumPy brief
(change_shape_to, add_direction, keep_by_position_in, stretch_to, repeat_each_number, split_into_pieces ...).

Every calculation is one NumPy call (named in the sentence each word prints); xarray lines up named directions when
the extra simplydata[xarray] is installed. Positions count from 1, both ends included.
"""

from __future__ import annotations

from .._typing import _Same

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..chart import Chart
    from ..table import Table

import numbers as _nb
import sys

import numpy as np

from .._errors import SimplydataError, choice_error, friendly, suggest
from .._positions import read_positions
from ._base import (HISTORY_LIMIT, BaseNumbers, amount, calculate, check_whole, is_number, note_empty, plain,
                    to_array)
from ._directions import (SETTINGS, check_names, default_names, line_up, numpy_shape, plural, say_shape, say_size,
                          xarray_or_none)
from .maths import MathsWords
from .more_number_words import MoreNumberWords
from .picking import ReplacingWords
from .summaries import SUMMARIES, _ordinal, _quiet
from ..table.summaries import _say_number

PAGES_SHOWN = 3  # print(block) shows this many pages; block.show() shows them all
_EXAMPLE = ('sdata.number_block(of_shape=(24, 8, 12), filled_with=0, directions_named=["hour", "row", "column"])')


def _is_block(value) -> bool:
    return getattr(value, "_is_simplydata_block", False)


def _say_numpy_axis(axes) -> str:
    axes = tuple(int(a) for a in axes)
    return str(axes[0]) if len(axes) == 1 else str(axes)


class NumberBlock(MoreNumberWords, ReplacingWords, MathsWords, BaseNumbers):
    """Numbers in any number of directions, each with a name. Make one with sdata.number_block(...)."""

    _is_simplydata_block = True
    _name = "block"
    _noun = "block"
    _OTHER_KIND = "block"
    _OLD_WORDS: dict = {}  # blocks were never released, so they have no old names
    _HINTS = {"reshape": "change_shape_to", "flatten": "get_all_numbers", "ravel": "get_all_numbers",
              "shape": "find_shape", "ndim": "count_directions", "transpose": "swap_directions",
              "T": "swap_directions", "squeeze": "remove_directions_of_size_one", "expand_dims": "add_direction",
              "flip": "reverse", "roll": "move_round_by", "rot90": "rotate", "insert": "insert_numbers",
              "repeat": "repeat_each_number", "tile": "repeat_whole_block", "concatenate": "add_numbers_from",
              "split": "split_into_pieces", "broadcast_to": "stretch_to", "take": "keep_by_position_in",
              "delete": "remove_by_position_in", "sel": "keep_where", "isel": "keep_by_position_in",
              "mean": "find_average", "sum": "find_total"}

    def __init__(self, values, names=None, named=None, labels=None):
        values = np.asarray(values)
        names = list(names) if names is not None else default_names(values.ndim)
        named = list(named) if named is not None else [False] * values.ndim
        super().__init__(values)
        object.__setattr__(self, "_names", names)
        object.__setattr__(self, "_named", named)
        object.__setattr__(self, "_labels", dict(labels or {}))
        object.__setattr__(self, "_original_state", (names, named, dict(labels or {})))

    # ------------------------------------------------------------------ history (the names go with the numbers)
    def _change(self, what: str, values, names=None, named=None, labels=None):
        values = np.asarray(values)
        if names is None:
            names, named = self._names, self._named
            labels = self._labels if labels is None else labels
        if named is None:
            named = [n in self._names and self._named[self._names.index(n)] for n in names]
        if labels is None:
            labels = {n: lab for n, lab in self._labels.items() if n in names}
        self._history.append((what, self._values, None, (self._names, self._named, self._labels)))
        if len(self._history) > HISTORY_LIMIT:
            self._history.pop(0)
        object.__setattr__(self, "_values", values)
        object.__setattr__(self, "_names", list(names))
        object.__setattr__(self, "_named", list(named))
        object.__setattr__(self, "_labels", dict(labels))
        return self

    @friendly
    def undo(self: _Same) -> _Same:
        """Take the last step back; the directions come back with the numbers. block.undo()"""
        if not self._history:
            print("Nothing to undo: this block has no steps yet.")
            return self
        what, before, _, (names, named, labels) = self._history.pop()
        object.__setattr__(self, "_values", before)
        object.__setattr__(self, "_names", list(names))
        object.__setattr__(self, "_named", list(named))
        object.__setattr__(self, "_labels", dict(labels))
        print(f"Undone: {what}")
        return self

    @friendly
    def start_again(self: _Same) -> _Same:
        """Go back to the block as it was at the start. block.start_again()"""
        names, named, labels = self._original_state
        return self._change("start again", self._original, names, named, labels)

    def _new(self, values, names=None, named=None, labels=None):
        """A new block (for symbols and the words that make new things)."""
        values = np.asarray(values)
        if names is None and values.ndim == self._values.ndim:
            names, named, labels = self._names, self._named, self._labels
        return NumberBlock(values, names, named, labels)

    def _like(self, values):
        return NumberBlock(values, self._names, self._named, self._labels)

    def _wrap(self, values):
        return self._new(values)

    # ------------------------------------------------------------------ directions
    def _shape_words(self, shape=None, names=None) -> str:
        return say_shape(self._values.shape if shape is None else shape, self._names if names is None else names)

    def _axis(self, step: str, direction, option: str = "over") -> int:
        """The NumPy axis of a direction given by name (or by its position, counting from 1)."""
        names = self._names
        if isinstance(direction, str):
            if direction in names:
                return names.index(direction)
            guesses = suggest(direction, names)
            hint = f' Did you mean "{guesses[0]}"?' if guesses else ""
            raise SimplydataError(
                f'This block has no direction called "{direction}".{hint} Its directions are: '
                + ", ".join(f'"{n}"' for n in names) + f".\nFor example:  {self._name}.{step}({option}=\"{names[0]}\")")
        if isinstance(direction, _nb.Integral) and not isinstance(direction, bool) and 1 <= direction <= len(names):
            axis = int(direction) - 1
            print(f"Note: direction {direction} is {names[axis]} (NumPy axis {axis}).")
            return axis
        raise SimplydataError(
            f"{option}= needs the name of a direction in quotes: " + ", ".join(f'"{n}"' for n in names)
            + f" (or its position, from 1 to {len(names)}).\nFor example:  {self._name}.{step}({option}=\"{names[0]}\")")

    def _axes(self, step: str, directions, option: str = "over") -> list[int]:
        if isinstance(directions, (list, tuple)):
            if not directions:
                raise SimplydataError(f"{option}= needs at least one direction.")
            axes = [self._axis(step, d, option) for d in directions]
            if len(set(axes)) != len(axes):
                raise SimplydataError(f"{option}= names a direction twice.")
            return axes
        return [self._axis(step, directions, option)]

    def _summary_axes(self, step: str, over, in_each) -> list[int] | None:
        """over= names the directions a summary runs through (they go); in_each= the ones kept."""
        if over is not None and in_each is not None:
            raise SimplydataError(
                f".{step}() takes over= (the directions that go) or in_each= (the directions kept), not both."
                f'\nFor example:  {self._name}.{step}(over="{self._names[0]}")')
        if over is not None:
            return sorted(self._axes(step, over))
        if in_each is not None:
            kept = self._axes(step, in_each, "in_each")
            return [i for i in range(self._values.ndim) if i not in kept]
        return None

    def _empty(self):
        if self._values.dtype.kind == "f":
            return np.isnan(self._values)
        return np.zeros(self._values.shape, dtype=bool)

    def _note_stretch(self, text: str):
        if SETTINGS["stretching_notes"] and text:
            print(text)

    # ------------------------------------------------------------------ looking
    def _pages(self, limit=None) -> list[str]:
        values, names = self._values, self._names
        if values.ndim <= 2:
            return [np.array2string(values, separator=", ", threshold=sys.maxsize if limit is None else 200)]
        lead_shape = values.shape[:-2]
        out = []
        total = int(np.prod(lead_shape)) if lead_shape else 1
        for count, index in enumerate(np.ndindex(*lead_shape)):
            if limit is not None and count >= limit:
                out.append(f"... and {total - limit} more (block.show() shows every one)")
                break
            where = ", ".join(f"{name} {i + 1} of {size}" for name, i, size in zip(names, index, lead_shape))
            out.append(f"{where} ({say_shape(values.shape[-2:], names[-2:])})")
            out.append(np.array2string(values[index], separator=", ", threshold=sys.maxsize))
        return out

    def __repr__(self):
        head = f"simplydata number block: {self._shape_words()} (NumPy: array, PyTorch: tensor)"
        if self._values.dtype.kind == "b":
            head += f"; yes or no values: {int(np.count_nonzero(self._values))} yes"
        return "\n".join([head, *self._pages(limit=PAGES_SHOWN)])

    @friendly
    def show(self):
        """Show every number, page by page. block.show()"""
        print(f"{self._shape_words()}:")
        print("\n".join(self._pages()))
        return None

    def _picking_help(self) -> str:
        args = ", ".join(f"{n}=1" for n in self._names if n.isidentifier())
        return (
            "Numbers in a block are picked with words, and positions count from 1:\n"
            f"    block.get_number_at({args})   one number\n"
            f'    block.keep_by_position_in("{self._names[0]}", 1, to=3)   keep part of one direction\n'
            "    block.get_all_numbers()             every number in one list\n"
            "Python's [ ] counts from 0, so simplydata does not use it. For a NumPy array, use block.as_numpy()."
        )

    @friendly
    def find_shape(self):
        """The size of each direction, in words and as NumPy's shape: (24, 8, 12). block.find_shape()"""
        print(f"{self._shape_words()} (NumPy shape {numpy_shape(self._values.shape)}).")
        return tuple(int(n) for n in self._values.shape)

    @friendly
    def count_directions(self):
        """How many directions the block has (NumPy ndim). block.count_directions()"""
        n = self._values.ndim
        print(f"{n} direction{'' if n == 1 else 's'}: {', '.join(self._names)} (NumPy ndim {n}).")
        return n

    @friendly
    def find_direction_names(self):
        """The names of the directions, in order. block.find_direction_names()"""
        given = [n for n, real in zip(self._names, self._named) if real]
        print("Directions: " + ", ".join(self._names)
              + ("" if given else " (the names simplydata gives; directions_named= gives your own)") + ".")
        return list(self._names)

    @friendly
    def get_number_at(self, *positions, **by_name):
        """The number at one position in every direction, counting from 1. block.get_number_at(hour=1, row=2, column=3)

        Give a position for each direction, by name (hour=1) or in order (block.get_number_at(1, 2, 3)); "last" is
        the last one. As NumPy block[0, 1, 2].
        """
        names, shape = self._names, self._values.shape
        example = f"{self._name}.get_number_at(" + ", ".join(f"{n}=1" for n in names if n.isidentifier()) + ")"
        if positions and by_name:
            raise SimplydataError(f"Give the positions by name or in order, not both.\nFor example:  {example}")
        if by_name:
            unknown = [k for k in by_name if k not in names]
            if unknown:
                raise SimplydataError(f'This block has no direction called "{unknown[0]}". Its directions are: '
                                      + ", ".join(names) + f".\nFor example:  {example}")
            missing = [n for n in names if n not in by_name]
            if missing:
                raise SimplydataError(f"get_number_at() needs a position for every direction; {', '.join(missing)} "
                                      f"{'is' if len(missing) == 1 else 'are'} missing.\nFor example:  {example}")
            positions = tuple(by_name[n] for n in names)
        if len(positions) != len(names):
            raise SimplydataError(f"get_number_at() needs {len(names)} positions, one for each direction "
                                  f"({', '.join(names)}).\nFor example:  {example}")
        index = []
        for value, name, size in zip(positions, names, shape):
            if isinstance(value, str) and value.strip().lower() == "last":
                index.append(size - 1)
                continue
            if not isinstance(value, _nb.Integral) or isinstance(value, bool) or not 1 <= value <= size:
                raise SimplydataError(
                    f"{name} needs a whole number from 1 to {size}, or \"last\"; positions count from 1."
                    f"\nFor example:  {example}")
            index.append(int(value) - 1)
        return plain(self._values[tuple(index)])

    @friendly
    def get_all_numbers(self):
        """Every number of the block in one list, the last direction fastest (NumPy ravel). nums = block.get_all_numbers()"""
        from .numbers import Numbers

        return Numbers(self._values.ravel().copy())

    @friendly
    def turn_into_table(self) -> Table:
        """The block as a long table: one column per direction (positions from 1) and a column "value". block.turn_into_table()"""
        import pandas as pd

        from ..table import Table

        index = pd.MultiIndex.from_product([range(1, n + 1) for n in self._values.shape], names=self._names)
        frame = pd.DataFrame({"value": self._values.ravel()}, index=index).reset_index()
        for name, labels in self._labels.items():
            frame[name] = np.asarray(labels)[frame[name].to_numpy() - 1]
        return Table(frame)

    @friendly
    def start_chart(self) -> Chart:
        """Start a chart from a block with one or two directions (a grid gives a heatmap). block.start_chart()"""
        from ..chart import chart
        from .numbers import NumberGrid, Numbers

        if self._values.ndim == 1:
            return chart(Numbers(self._values.copy()))
        if self._values.ndim == 2:
            return chart(NumberGrid(self._values.copy()))
        raise SimplydataError(
            f"A chart is drawn from one or two directions, and this block has {self._values.ndim} "
            f"({self._shape_words()}). Keep one page first:  "
            f'block.keep_by_position_in("{self._names[0]}", 1).remove_directions_of_size_one().start_chart()')

    # ------------------------------------------------------------------ lining up and sums
    def _other_parts(self, other, step: str):
        """values, names and real-name flags of the other side of a sum."""
        if _is_block(other):
            return other._values, other._names, other._named
        if is_number(other):
            return np.asarray(other), [], []
        if other is None or isinstance(other, (str, bytes, bool, np.bool_)):
            raise SimplydataError(f".{step}() needs a number, a block or a list of numbers."
                                  + self._example(f"{step}(5)"))
        values = other._values if isinstance(other, BaseNumbers) else to_array(other, f".{step}()", f"{self._name}.{step}(5)")
        return values, default_names(values.ndim), [False] * values.ndim

    def _lined_up(self, other, step: str, over=None):
        b, b_names, b_named = self._other_parts(other, step)
        over_axes = self._axes(step, over) if over is not None else None
        return line_up(self._values, self._names, self._named, b, b_names, b_named, over_axes=over_axes, step=step,
                       owner=self._name), b, b_names

    def _used_again(self, lined, b, b_names, result_shape) -> list[str]:
        """The directions along which the other side's numbers were used again."""
        if lined.how == "by name":
            return [say_size(int(s), n) for s, n in zip(result_shape, lined.names) if n not in b_names and s != 1]
        shape_b = np.shape(lined.b)
        offset = len(result_shape) - len(shape_b)
        return [say_size(int(s), n) for i, (s, n) in enumerate(zip(result_shape, lined.names))
                if s != 1 and (i < offset or shape_b[i - offset] == 1)]

    def _sum_word(self, op: str, other, over=None):
        lined, b, b_names = self._lined_up(other, op, over)
        result, n, why = calculate(op, lined.a, lined.b)
        if result.shape != self._values.shape:
            raise SimplydataError(
                f"{self._name}.{op}() would change the shape of your block ({self._shape_words()} -> "
                f"{say_shape(result.shape, lined.names)}). Use the symbol instead to make a new block, for example:  "
                f"new = {self._name} {'+-*/'['add subtract times divide_by'.split().index(op)] if op != 'power' else '**'} other")
        note_empty(n, why)
        again = self._used_again(lined, b, b_names, self._values.shape) if np.ndim(b) else []
        if again:
            self._note_stretch(f"The other numbers ({say_shape(np.shape(b), b_names)}) were used again for each of "
                               f"the {' and '.join(again)} (lined up {lined.how}; NumPy: broadcasting).")
        word = op.replace("_", " ")
        return self._change(f"{word} {'a number' if not np.ndim(b) else 'other numbers'}", result)

    def _sum_symbol(self, op: str, other, reverse: bool = False):
        if not (is_number(other) or isinstance(other, (BaseNumbers, list, tuple, np.ndarray, range))):
            return NotImplemented
        lined, b, b_names = self._lined_up(other, op)
        result, n, why = calculate(op, lined.b, lined.a) if reverse else calculate(op, lined.a, lined.b)
        note_empty(n, why)
        if np.ndim(b):
            if lined.how == "by name":
                mine_again = [n for n in lined.names if n not in self._names]
            else:
                mine_again = _again(self._values.shape, result.shape)
            theirs_again = self._used_again(lined, b, b_names, result.shape)
            if mine_again and theirs_again and result.size > max(self._values.size, np.size(b)):
                self._note_stretch(
                    f"Note: both sides were stretched: {self._shape_words()} and {say_shape(np.shape(b), b_names)} "
                    f"gave {say_shape(result.shape, lined.names)}. If you meant one number per "
                    f"{self._names[0]}, use {self._name}.{op}(other, over=\"{self._names[0]}\"). If you meant "
                    f"every pair, use {self._name}.make_pair_table_with(other, by_{_BY.get(op, 'multiplying')}=True).")
        return NumberBlock(result, lined.names, lined.named)

    # the maths words take over= on blocks: plate.subtract(blank, over="row")
    @friendly
    def add(self: _Same, number=None, over=None) -> _Same:
        """Add a number, or a block that lines up, to every number. block.add(5)

        over="row" says which direction the other numbers belong to (one number per row). Named directions line up
        by name. For a new block write bigger = block + 5.
        """
        return self._sum_word("add", number, over)

    @friendly
    def subtract(self: _Same, number=None, over=None) -> _Same:
        """Take a number, or a block that lines up, away from every number. block.subtract(2)

        block.subtract(blank) takes a blank of 8 rows x 12 columns from each of the 24 hours; over="row" gives one
        number per row (plate.subtract(blank, over="row")). For a new block write smaller = block - 2.
        """
        return self._sum_word("subtract", number, over)

    @friendly
    def times(self: _Same, number=None, over=None) -> _Same:
        """Multiply every number by a number, or by a block that lines up. block.times(2)

        block.times(weights, over="colour") gives one weight for each colour of a photo.
        """
        return self._sum_word("times", number, over)

    @friendly
    def divide_by(self: _Same, number=None, rounding_down=False, over=None) -> _Same:
        """Divide every number by a number, or by a block that lines up. block.divide_by(4)

        rounding_down=True keeps the whole part, rounded down (NumPy floor_divide). Dividing by 0 has no answer, so
        those values become empty and a note says how many.
        """
        if rounding_down is True:
            return self._floor_divide(number, over)
        if rounding_down is not False:
            raise SimplydataError("rounding_down= needs True or False (no quotes).")
        return self._sum_word("divide_by", number, over)

    @friendly
    def raise_to_power(self: _Same, number=None, over=None) -> _Same:
        """Raise every number to a power. block.raise_to_power(2)"""
        return self._sum_word("power", number, over)

    def __and__(self, other):
        return self._yes_no_symbol("and", other)

    def __rand__(self, other):
        return self._yes_no_symbol("and", other)

    def __or__(self, other):
        return self._yes_no_symbol("or", other)

    def __ror__(self, other):
        return self._yes_no_symbol("or", other)

    def _yes_no_symbol(self, how, other):
        if not isinstance(other, (BaseNumbers, list, tuple, np.ndarray, bool, np.bool_)):
            return NotImplemented
        b = other._values if isinstance(other, BaseNumbers) else np.asarray(other)
        b_names = other._names if _is_block(other) else default_names(b.ndim)
        b_named = other._named if _is_block(other) else [False] * b.ndim
        self._need_yes_no("&" if how == "and" else "|", b)
        lined = line_up(self._values, self._names, self._named, b, b_names, b_named, step=how, owner=self._name)
        result = (np.logical_and if how == "and" else np.logical_or)(lined.a, lined.b)
        return NumberBlock(result, lined.names, lined.named)

    # ------------------------------------------------------------------ stretching (P04, B2-B6)
    @friendly
    def show_how_it_lines_up_with(self, other=None):
        """Show how this block and another line up before combining them; nothing changes. block.show_how_it_lines_up_with(other)

        Shapes line up from the right; a direction of size 1, or one the other side lacks, is used again (NumPy:
        broadcasting). Blocks whose directions all have names line up by name. NumPy np.broadcast_shapes.
        """
        b, b_names, b_named = self._other_parts(other, "show_how_it_lines_up_with")
        a, names = self._values, self._names
        mine = f"this block: {self._shape_words()}"
        theirs = f"other:      {say_shape(np.shape(b), b_names)}"
        by_name = all(self._named) and all(b_named) and np.ndim(b) > 0
        lines = [mine, theirs]
        if by_name:
            lines.append("lined up by name (both blocks name every direction):")
            sizes_b = dict(zip(b_names, np.shape(b)))
            result = []
            for name in [n for n in b_names if n not in names] + list(names):
                size_a = dict(zip(names, a.shape)).get(name)
                size_b = sizes_b.get(name)
                if size_a is None:
                    lines.append(f"  {name:<10} {size_b:>4}   (this block has no {name}: its numbers are used again "
                                 f"for each of the {say_size(size_b, name)})")
                    result.append((size_b, name))
                elif size_b is None:
                    lines.append(f"  {name:<10} {size_a:>4}   (the other has no {name}: its numbers are used again "
                                 f"for each of the {say_size(size_a, name)})")
                    result.append((size_a, name))
                elif size_a == size_b:
                    lines.append(f"  {name:<10} {size_a:>4} = {size_b}")
                    result.append((size_a, name))
                else:
                    lines.append(f"  {name:<10} {size_a:>4} against {size_b}   <- clash: the same name needs the "
                                 "same size")
                    result = None
                    break
            if result is None:
                lines.append("These do not fit.")
            else:
                lines.append(f"result: {say_shape([s for s, _ in result], [n for _, n in result])}. Nothing is "
                             "copied; the numbers are only read again.")
            lines.append("xarray lines up by name the same way (xarray.broadcast).")
            print("\n".join(lines))
            return None
        lines.append("lined up from the right:")
        width = max(a.ndim, np.ndim(b))
        sa = (None,) * (width - a.ndim) + tuple(a.shape)
        sb = (None,) * (width - np.ndim(b)) + tuple(np.shape(b))
        na = [None] * (width - a.ndim) + list(names)
        nb = [None] * (width - np.ndim(b)) + list(b_names)
        clash = False
        for x, y, n1, n2 in zip(sa, sb, na, nb):
            name = n1 or n2
            if x is None or y is None:
                size = x if y is None else y
                lacking = "the other" if y is None else "this block"
                lines.append(f"  {name:<10} {size:>4}   ({lacking} has no {name}: its numbers are used again for "
                             f"each of the {say_size(size, name)})")
            elif x == y:
                lines.append(f"  {name:<10} {x:>4} = {y}")
            elif 1 in (x, y):
                size = max(x, y)
                which = "the other" if y == 1 else "this block"
                lines.append(f"  {name:<10} {x:>4} and {y}   ({which} has 1: it is used again for each of the "
                             f"{say_size(size, name)})")
            else:
                lines.append(f"  {name:<10} {x:>4} against {y}   <- clash: neither is 1")
                clash = True
        try:
            shape = np.broadcast_shapes(a.shape, np.shape(b))
        except ValueError:
            shape = None
        if clash or shape is None:
            lines.append("These do not fit." + (f' For one number per {names[list(a.shape).index(np.shape(b)[0])]}: '
                                                 f'{self._name}.subtract(other, over="'
                                                 f'{names[list(a.shape).index(np.shape(b)[0])]}")'
                                                 if np.ndim(b) == 1 and np.shape(b)[0] in a.shape else ""))
            lines.append(f"NumPy: np.broadcast_shapes({numpy_shape(a.shape)}, {numpy_shape(np.shape(b))}) raises "
                         "\"shape mismatch\"")
        else:
            result_names = (default_names(len(shape))[: len(shape) - a.ndim] if len(shape) > a.ndim else []) + list(names)
            lines.append(f"result: {say_shape(shape, result_names)}. Nothing is copied; the numbers are only read "
                         "again.")
            lines.append(f"NumPy: np.broadcast_shapes({numpy_shape(a.shape)}, {numpy_shape(np.shape(b))})")
        print("\n".join(lines))
        return None

    @friendly
    def stretch_to(self: _Same, shape=None) -> _Same:
        """Stretch the block to a bigger shape by using its numbers again (NumPy broadcast_to). block.stretch_to((2, 24, 8, 12))

        shape= is a shape such as (24, 8, 12), or another block (its shape and names). Directions line up from the
        right, or by name when both blocks name every direction.
        """
        example = f"{self._name}.stretch_to((24, 8, 12))"
        if _is_block(shape):
            target, t_names, t_named = shape._values.shape, shape._names, shape._named
            if all(self._named) and all(t_named):
                lined = line_up(np.broadcast_to(0, target), t_names, t_named, self._values, self._names, self._named,
                                step="stretch_to", owner=self._name)
                if list(lined.names) != list(t_names):
                    raise SimplydataError(f"The block has directions the other one lacks, so it cannot be stretched "
                                          f"to {say_shape(target, t_names)}.")
                new = np.broadcast_to(lined.b, target).copy()
                call = f"np.broadcast_to(block, {numpy_shape(target)}) after lining up by name"
                return self._stretched(new, t_names, t_named, call)
        elif isinstance(shape, (tuple, list)) and shape and all(isinstance(n, _nb.Integral) and not isinstance(n, bool)
                                                                and n >= 0 for n in shape):
            target = tuple(int(n) for n in shape)
            t_names = default_names(len(target))[: len(target) - self._values.ndim] + list(self._names) \
                if len(target) >= self._values.ndim else default_names(len(target))
            t_named = [False] * (len(target) - self._values.ndim) + list(self._named) \
                if len(target) >= self._values.ndim else [False] * len(target)
        else:
            raise SimplydataError(f"stretch_to() needs a shape in brackets, such as (24, 8, 12), or another block."
                                  f"\nFor example:  {example}")
        try:
            new = np.broadcast_to(self._values, target).copy()
        except ValueError:
            raise SimplydataError(
                f"{self._shape_words()} cannot be stretched to {say_shape(target, t_names)}: lined up from the right, "
                "each size must be the same or 1 (NumPy np.broadcast_to raised \"shape mismatch\").") from None
        return self._stretched(new, t_names, t_named, f"np.broadcast_to(block, {numpy_shape(target)})")

    def _stretched(self, new, names, named, call):
        before = self._shape_words()
        after = say_shape(new.shape, names)
        print(f"{before} -> {after}: the same numbers used again, nothing resized. NumPy: {call}")
        return self._change(f"stretch to {after}", new, names, named, {})

    # ------------------------------------------------------------------ the shape (B6: only_show_new_shape=)
    def _preview(self, new_shape, new_names, call) -> None:
        print(f"{self._shape_words()} -> {say_shape(new_shape, new_names)} (nothing changed). NumPy: {call}")

    def _stand_in(self):
        """A zero-memory stand-in with the block's shape: the NumPy call runs on it to give the new shape."""
        return np.broadcast_to(0, self._values.shape)

    @friendly
    def change_shape_to(self: _Same, *sizes, one_row_per=None, fill=None, only_show_new_shape=False) -> _Same:
        """Give the numbers a new shape, row by row (NumPy reshape). block.change_shape_to(one_row_per="hour")

        block.change_shape_to(8, "rest") makes 8 rows and as many columns as the numbers fill. one_row_per="image"
        keeps one row for each hour (the first direction) and puts the rest of its numbers in that row, as
        scikit-learn needs. fill="repeat" fills a new shape of any size by repeating the numbers (NumPy resize).
        only_show_new_shape=True only says what the shape would be.
        """
        example = f'{self._name}.change_shape_to(8, "rest")'
        a = self._values
        if one_row_per is not None:
            if sizes:
                raise SimplydataError(f"Give sizes or one_row_per=, not both.\nFor example:  {example}")
            axis = self._axis("change_shape_to", one_row_per, "one_row_per")
            if axis != 0:
                raise SimplydataError(
                    f'{one_row_per} is not the first direction, so a new shape would mix it up with the others. Move it '
                    f'first:  {self._name}.move_direction("{one_row_per}", to_position=1)')
            target = (a.shape[0], -1)
            call = f"block.reshape({a.shape[0]}, -1)"
        else:
            if not sizes:
                raise SimplydataError(f"change_shape_to() needs the new sizes.\nFor example:  {example}")
            target = []
            for size in sizes:
                if isinstance(size, str) and size.strip().lower() == "rest":
                    target.append(-1)
                elif isinstance(size, _nb.Integral) and not isinstance(size, bool) and size >= 0:
                    target.append(int(size))
                else:
                    raise SimplydataError(f'Sizes are whole numbers, or "rest" once for the size that fits '
                                          f"(you gave {size!r}).\nFor example:  {example}")
            if target.count(-1) > 1:
                raise SimplydataError(f'"rest" can be used once.\nFor example:  {example}')
            target = tuple(target)
            call = f"block.reshape{target}" if len(target) > 1 else f"block.reshape({target[0]})"
        if fill is not None:
            if fill != "repeat":
                raise choice_error("change_shape_to", "fill", fill, ["repeat"])
            if -1 in target:
                raise SimplydataError('fill="repeat" needs every size; "rest" cannot be worked out.')
            new_shape = np.resize(self._stand_in(), target).shape
            call = f"np.resize(block, {numpy_shape(target)})"
            if only_show_new_shape:
                self._preview(new_shape, default_names(len(new_shape)), call)
                return self
            new = np.resize(a, target)
        else:
            try:
                new_shape = np.reshape(self._stand_in(), target).shape
            except ValueError:
                fits = [d for d in range(1, a.size + 1) if a.size % d == 0][:12]
                raise SimplydataError(
                    f"{amount(a.size)} cannot fill that shape exactly: the sizes multiplied together must be "
                    f"{a.size}. Sizes that divide {a.size}: {', '.join(map(str, fits))} ...\n"
                    f'For example:  {example}   ("rest" works out the last size)') from None
            if only_show_new_shape:
                self._preview(new_shape, default_names(len(new_shape)), call)
                return self
            new = np.reshape(a, target).copy()
        names = default_names(new.ndim)
        print(f"{self._shape_words()} -> {say_shape(new.shape, names)}. NumPy: {call}")
        return self._change(f"change shape to {say_shape(new.shape, names)}", new, names, [False] * new.ndim, {})

    @friendly
    def add_direction(self: _Same, name=None, at_position=1, only_show_new_shape=False) -> _Same:
        """Add a direction of size 1, with a name (NumPy expand_dims). block.add_direction("plate", at_position=1)

        at_position=1 puts it first (the default); a direction of size 1 is used again along it when combining.
        """
        example = f'{self._name}.add_direction("image", at_position=1)'
        if not isinstance(name, str) or not name.strip():
            raise SimplydataError(f"add_direction() needs a name for the new direction, in quotes.\nFor example:  {example}")
        if name in self._names:
            raise SimplydataError(f'The block already has a direction called "{name}".\nFor example:  {example}')
        n = self._values.ndim
        if not isinstance(at_position, _nb.Integral) or isinstance(at_position, bool) or not 1 <= at_position <= n + 1:
            raise SimplydataError(f"at_position= needs a whole number from 1 to {n + 1}.\nFor example:  {example}")
        axis = int(at_position) - 1
        names = self._names[:axis] + [name] + self._names[axis:]
        named = self._named[:axis] + [True] + self._named[axis:]
        call = f"np.expand_dims(block, axis={axis})"
        if only_show_new_shape:
            self._preview(np.expand_dims(self._stand_in(), axis).shape, names, call)
            return self
        new = np.expand_dims(self._values, axis).copy()
        print(f"{self._shape_words()} -> {say_shape(new.shape, names)}. NumPy: {call}")
        return self._change(f'add direction "{name}"', new, names, named)

    @friendly
    def remove_directions_of_size_one(self: _Same, only_show_new_shape=False) -> _Same:
        """Remove every direction that has size 1 (NumPy squeeze). block.remove_directions_of_size_one()"""
        a = self._values
        keep = [i for i, s in enumerate(a.shape) if s != 1]
        if len(keep) == a.ndim:
            print(f"No direction has size 1 ({self._shape_words()}); nothing to remove.")
            return self
        if not keep:
            raise SimplydataError("Every direction has size 1, so the block holds one number: "
                                  f"{self._name}.get_all_numbers() gives it.")
        names = [self._names[i] for i in keep]
        if only_show_new_shape:
            self._preview(np.squeeze(self._stand_in()).shape, names, "np.squeeze(block)")
            return self
        new = np.squeeze(a).copy()
        print(f"{self._shape_words()} -> {say_shape(new.shape, names)}. NumPy: np.squeeze(block)")
        return self._change("remove directions of size one", new, names, [self._named[i] for i in keep])

    @friendly
    def swap_directions(self: _Same, first=None, second=None, only_show_new_shape=False) -> _Same:
        """Swap two directions (NumPy swapaxes). block.swap_directions("row", "column")"""
        i = self._axis("swap_directions", first, "first")
        j = self._axis("swap_directions", second, "second")
        order = list(range(self._values.ndim))
        order[i], order[j] = order[j], order[i]
        names = [self._names[k] for k in order]
        named = [self._named[k] for k in order]
        call = f"np.swapaxes(block, {i}, {j})"
        if only_show_new_shape:
            self._preview(np.swapaxes(self._stand_in(), i, j).shape, names, call)
            return self
        new = np.swapaxes(self._values, i, j).copy()
        print(f"{self._shape_words()} -> {say_shape(new.shape, names)}. NumPy: {call}")
        return self._change(f"swap directions {first} and {second}", new, names, named)

    @friendly
    def move_direction(self: _Same, name=None, to_position=None, only_show_new_shape=False) -> _Same:
        """Move one direction to another place (NumPy moveaxis). block.move_direction("column", to_position=1)"""
        i = self._axis("move_direction", name, "name")
        n = self._values.ndim
        if not isinstance(to_position, _nb.Integral) or isinstance(to_position, bool) or not 1 <= to_position <= n:
            raise SimplydataError(f"to_position= needs a whole number from 1 to {n}.\nFor example:  "
                                  f'{self._name}.move_direction("{self._names[-1]}", to_position=1)')
        j = int(to_position) - 1
        order = [k for k in range(n) if k != i]
        order.insert(j, i)
        names = [self._names[k] for k in order]
        named = [self._named[k] for k in order]
        call = f"np.moveaxis(block, {i}, {j})"
        if only_show_new_shape:
            self._preview(np.moveaxis(self._stand_in(), i, j).shape, names, call)
            return self
        new = np.moveaxis(self._values, i, j).copy()
        print(f"{self._shape_words()} -> {say_shape(new.shape, names)}. NumPy: {call}")
        return self._change(f"move direction {self._names[i]} to position {to_position}", new, names, named)

    # ------------------------------------------------------------------ order along a direction
    def _labels_after(self, axis, how, index=None):
        name = self._names[axis]
        labels = dict(self._labels)
        if name in labels:
            if how == "flip":
                labels[name] = np.flip(labels[name])
            elif how == "take":
                labels[name] = np.take(labels[name], index)
            else:
                labels.pop(name)
                print(f"Note: the labels of {name} were left out (the positions moved).")
        return labels

    @friendly
    def reverse(self: _Same, over=None) -> _Same:
        """Turn the order round along a direction, or along every direction (NumPy flip). block.reverse(over="row")"""
        if over is None:
            axes = list(range(self._values.ndim))
        else:
            axes = self._axes("reverse", over)
        new = np.flip(self._values, axis=tuple(axes)).copy()
        labels = dict(self._labels)
        for axis in axes:
            if self._names[axis] in labels:
                labels[self._names[axis]] = np.flip(labels[self._names[axis]])
        said = "every direction" if over is None else ", ".join(self._names[a] for a in axes)
        print(f"Reversed along {said}. NumPy: np.flip(block, axis={_say_numpy_axis(axes)})")
        return self._change(f"reverse along {said}", new, labels=labels)

    @friendly
    def rotate(self: _Same, by_quarter_turns=1, over=None) -> _Same:
        """Turn the block a quarter turn (or more) anticlockwise, as a picture (NumPy rot90). block.rotate(by_quarter_turns=1)

        It turns the last two directions (rows and columns), or the two named in over=["row", "column"];
        by_quarter_turns=-1 turns clockwise.
        """
        if not isinstance(by_quarter_turns, _nb.Integral) or isinstance(by_quarter_turns, bool):
            raise SimplydataError(f"by_quarter_turns= needs a whole number, such as 1 or -1.\nFor example:  "
                                  f"{self._name}.rotate(by_quarter_turns=1)")
        if self._values.ndim < 2:
            raise SimplydataError("rotate() turns two directions, and this block has one.")
        axes = (self._values.ndim - 2, self._values.ndim - 1) if over is None else tuple(self._axes("rotate", over))
        if len(axes) != 2:
            raise SimplydataError('over= names the two directions to turn, such as over=["row", "column"].')
        new = np.rot90(self._values, k=int(by_quarter_turns), axes=axes).copy()
        names = list(self._names)
        print(f"Turned {by_quarter_turns} quarter turn{'' if abs(by_quarter_turns) == 1 else 's'} "
              f"{'anticlockwise' if by_quarter_turns >= 0 else 'clockwise'}: {self._shape_words()} -> "
              f"{say_shape(new.shape, names)}. NumPy: np.rot90(block, k={by_quarter_turns}, axes={axes})")
        labels = {n: v for n, v in self._labels.items() if n not in (names[axes[0]], names[axes[1]])}
        return self._change(f"rotate by {by_quarter_turns} quarter turns", new, names, self._named, labels)

    @friendly
    def move_round_by(self: _Same, steps=None, over=None) -> _Same:
        """Move every number along a direction by some steps; the ones that fall off the end come round to the start (NumPy roll).

        block.move_round_by(3, over="hour")
        """
        if not isinstance(steps, _nb.Integral) or isinstance(steps, bool):
            raise SimplydataError(f'move_round_by() needs a whole number of steps.\nFor example:  '
                                  f'{self._name}.move_round_by(3, over="{self._names[0]}")')
        if over is None and self._values.ndim > 1:
            raise SimplydataError(f'move_round_by() needs over=, the direction to move along.\nFor example:  '
                                  f'{self._name}.move_round_by(3, over="{self._names[0]}")')
        axis = 0 if over is None else self._axis("move_round_by", over)
        new = np.roll(self._values, int(steps), axis=axis)
        labels = self._labels_after(axis, "drop")
        print(f"Moved round by {steps} along {self._names[axis]}. NumPy: np.roll(block, {steps}, axis={axis})")
        return self._change(f"move round by {steps} over {self._names[axis]}", new, labels=labels)

    @friendly
    def insert_numbers(self: _Same, values=None, at_position=None, over=None) -> _Same:
        """Put new numbers in before a position along a direction (NumPy insert). block.insert_numbers(0, at_position=2, over="row")

        at_position counts from 1; one more than the size adds them at the end. The numbers are one number, or one
        for each position of the other directions.
        """
        example = f'{self._name}.insert_numbers(0, at_position=2, over="{self._names[0]}")'
        if over is None and self._values.ndim > 1:
            raise SimplydataError(f"insert_numbers() needs over=, the direction to insert along.\nFor example:  {example}")
        axis = 0 if over is None else self._axis("insert_numbers", over)
        size = self._values.shape[axis]
        if not isinstance(at_position, _nb.Integral) or isinstance(at_position, bool) or not 1 <= at_position <= size + 1:
            raise SimplydataError(f"at_position= needs a whole number from 1 to {size + 1}.\nFor example:  {example}")
        if values is None:
            raise SimplydataError(f"insert_numbers() needs the numbers to put in.\nFor example:  {example}")
        new_values = np.asarray(values) if is_number(values) else to_array(values, ".insert_numbers()", example)
        try:
            new = np.insert(self._values, int(at_position) - 1, new_values, axis=axis)
        except ValueError:
            raise SimplydataError(f"The numbers to insert do not fit: give one number, or one for each position of "
                                  f"the other directions.\nFor example:  {example}") from None
        labels = self._labels_after(axis, "drop")
        print(f"{self._shape_words()} -> {say_shape(new.shape, self._names)}. "
              f"NumPy: np.insert(block, {int(at_position) - 1}, values, axis={axis})")
        return self._change(f"insert numbers at position {at_position} over {self._names[axis]}", new, labels=labels)

    def _by_position(self, step, direction, positions, to, step_size, keep):
        axis = self._axis(step, direction, "direction")
        name = self._names[axis]
        total = self._values.shape[axis]
        picked = read_positions(step, positions, to, step_size, total, noun=name, count_noun=plural(name),
                                owner="The block has", example=f'{self._name}.{step}("{name}", 1, to=2)',
                                last_hint=f'{self._name}.{step}("{name}", "last")', name=self._name)
        if keep:
            index = picked.array()
        else:
            if len(picked) == total:
                raise SimplydataError(f"That would remove every {name}. Keep at least one.")
            index = picked.kept_positions(total)
        new = np.take(self._values, index, axis=axis)
        labels = self._labels_after(axis, "take", index)
        verb = "Kept" if keep else "Removed"
        count = len(index) if keep else len(picked)
        print(f"{verb} {picked.words()} ({count} of {say_size(total, name)}); the block is now "
              f"{say_shape(new.shape, self._names)}. NumPy: "
              + (f"np.take(block, positions, axis={axis})" if keep else f"np.delete(block, positions, axis={axis})"))
        return self._change(f"{'keep' if keep else 'remove'} {picked.short_words()}", new, labels=labels)

    @friendly
    def keep_by_position_in(self: _Same, direction=None, positions=None, to=None, step=None) -> _Same:
        """Keep some positions along one direction, counting from 1, both ends included. block.keep_by_position_in("hour", [1, 3])

        As keep_rows_by_position: a run (to=), every n-th (step=) or a list. NumPy np.take(block, ..., axis=).
        """
        return self._by_position("keep_by_position_in", direction, positions, to, step, keep=True)

    @friendly
    def remove_by_position_in(self: _Same, direction=None, positions=None, to=None, step=None) -> _Same:
        """Remove some positions along one direction, counting from 1. block.remove_by_position_in("hour", 24)"""
        return self._by_position("remove_by_position_in", direction, positions, to, step, keep=False)

    # ------------------------------------------------------------------ labels (P25)
    def _label_positions(self, step, direction, is_between, is_one_of):
        axis = self._axis(step, direction, "direction")
        name = self._names[axis]
        if name not in self._labels:
            raise SimplydataError(
                f'{name} has no labels (only positions), so {step}() has nothing to compare. By position:  '
                f'{self._name}.keep_by_position_in("{name}", 1, to=3)')
        given = [x for x in (is_between, is_one_of) if x is not None]
        if len(given) != 1:
            raise SimplydataError(f'.{step}() needs is_between=[low, high] or is_one_of=[...].\nFor example:  '
                                  f'{self._name}.{step}("{name}", is_between=[60, 80])')
        labels = np.asarray(self._labels[name])
        xr = xarray_or_none()
        if xr is not None:
            # xarray chooses the positions itself (sel), from a block of positions labelled like this one
            places = xr.DataArray(np.arange(labels.size), dims=[name], coords={name: labels})
            if is_between is not None:
                low, high = sorted(self._two_bounds(step, name, is_between))  # either order
                if places.indexes[name].is_monotonic_decreasing:
                    low, high = high, low
                chosen = places.sel({name: slice(low, high)}).values
                said = f"between {low} and {high}"
            else:
                try:
                    chosen = places.sel({name: list(is_one_of)}).values
                except KeyError as error:
                    raise SimplydataError(f"{name} has no label {error.args[0]!r}.") from None
                said = "one of " + ", ".join(str(x) for x in is_one_of)
            return axis, name, np.asarray(chosen, dtype=int), said, "xarray sel"
        if labels.dtype.kind not in "iuf":
            raise SimplydataError(f'Choosing by date or text labels needs xarray: pip install "simplydata[xarray]".')
        if is_between is not None:
            low, high = sorted(self._two_bounds(step, name, is_between))
            chosen = np.flatnonzero(np.logical_and(labels >= low, labels <= high))
            said = f"between {low} and {high}"
        else:
            chosen = np.flatnonzero(np.isin(labels, list(is_one_of)))
            said = "one of " + ", ".join(str(x) for x in is_one_of)
        return axis, name, chosen, said, "NumPy flatnonzero on the labels"

    def _two_bounds(self, step, name, value):
        if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)) or len(value) != 2:
            raise SimplydataError(f'is_between= needs two values in square brackets.\nFor example:  '
                                  f'{self._name}.{step}("{name}", is_between=[60, 80])')
        return value[0], value[1]

    @friendly
    def keep_where(self: _Same, direction=None, is_between=None, is_one_of=None) -> _Same:
        """Keep the part of a labelled direction whose labels pass (xarray sel). block.keep_where("east", is_between=[2, 5])

        The range can be written in either order, also when the labels run downward. is_one_of=[0, 10, 50] keeps
        those labels. A direction without labels is chosen by position: keep_by_position_in.
        """
        axis, name, chosen, said, how = self._label_positions("keep_where", direction, is_between, is_one_of)
        if chosen.size == 0:
            raise SimplydataError(f"No {name} is {said}, so nothing would be left.")
        new = np.take(self._values, chosen, axis=axis)
        labels = self._labels_after(axis, "take", chosen)
        print(f"Kept {chosen.size} of {say_size(self._values.shape[axis], name)} ({name} {said}); the block is now "
              f"{say_shape(new.shape, self._names)}. Chosen by {how}.")
        return self._change(f"keep where {name} is {said}", new, labels=labels)

    @friendly
    def remove_where(self: _Same, direction=None, is_between=None, is_one_of=None) -> _Same:
        """Remove the part of a labelled direction whose labels pass. block.remove_where("north", is_one_of=[0, 1])"""
        axis, name, chosen, said, how = self._label_positions("remove_where", direction, is_between, is_one_of)
        if chosen.size == self._values.shape[axis]:
            raise SimplydataError(f"Every {name} is {said}, so nothing would be left.")
        new = np.delete(self._values, chosen, axis=axis)
        kept = np.delete(np.arange(self._values.shape[axis]), chosen)
        labels = self._labels_after(axis, "take", kept)
        print(f"Removed {chosen.size} of {say_size(self._values.shape[axis], name)} ({name} {said}); the block is now "
              f"{say_shape(new.shape, self._names)}. Chosen by {how}.")
        return self._change(f"remove where {name} is {said}", new, labels=labels)

    # ------------------------------------------------------------------ repeating, joining, splitting
    @friendly
    def repeat_each_number(self: _Same, how_many=None, over=None, only_show_new_shape=False) -> _Same:
        """Repeat each number along a direction: 1, 2 becomes 1, 1, 2, 2 (NumPy repeat). block.repeat_each_number(3, over="hour")"""
        n = check_whole("repeat_each_number", "repeat_each_number()", how_many,
                        f'{self._name}.repeat_each_number(3, over="{self._names[0]}")', smallest=1)
        if over is None and self._values.ndim > 1:
            raise SimplydataError(f'repeat_each_number() needs over=, the direction to repeat along.\nFor example:  '
                                  f'{self._name}.repeat_each_number(3, over="{self._names[0]}")')
        axis = 0 if over is None else self._axis("repeat_each_number", over)
        call = f"np.repeat(block, {n}, axis={axis})"
        if only_show_new_shape:
            self._preview(np.repeat(self._stand_in(), n, axis=axis).shape, self._names, call)
            return self
        new = np.repeat(self._values, n, axis=axis)
        labels = self._labels_after(axis, "drop")
        print(f"{self._shape_words()} -> {say_shape(new.shape, self._names)}. NumPy: {call}")
        return self._change(f"repeat each number {n} times over {self._names[axis]}", new, labels=labels)

    @friendly
    def repeat_whole_block(self: _Same, how_many=None, over=None, only_show_new_shape=False) -> _Same:
        """Repeat the whole block along a direction: 1, 2 becomes 1, 2, 1, 2 (NumPy tile). block.repeat_whole_block(2, over="hour")

        over= a name the block does not have adds that direction in front, with the block repeated along it.
        """
        example = f'{self._name}.repeat_whole_block(24, over="hour")'
        n = check_whole("repeat_whole_block", "repeat_whole_block()", how_many, example, smallest=1)
        if not isinstance(over, str) and over is not None:
            axis = self._axis("repeat_whole_block", over)
        elif over is None:
            if self._values.ndim > 1:
                raise SimplydataError(f"repeat_whole_block() needs over=, the direction to repeat along.\nFor example:  {example}")
            axis = 0
        elif over in self._names:
            axis = self._names.index(over)
        else:
            reps = (n,) + (1,) * self._values.ndim
            names, named = [over] + list(self._names), [True] + list(self._named)
            call = f"np.tile(block, {reps})"
            if only_show_new_shape:
                self._preview(np.tile(self._stand_in(), reps).shape, names, call)
                return self
            new = np.tile(self._values, reps)
            print(f"{self._shape_words()} -> {say_shape(new.shape, names)}: the block used again for each "
                  f"{over}. NumPy: {call}")
            return self._change(f"repeat whole block {n} times over new direction {over}", new, names, named)
        reps = tuple(n if i == axis else 1 for i in range(self._values.ndim))
        call = f"np.tile(block, {reps})"
        if only_show_new_shape:
            self._preview(np.tile(self._stand_in(), reps).shape, self._names, call)
            return self
        new = np.tile(self._values, reps)
        labels = self._labels_after(axis, "drop")
        print(f"{self._shape_words()} -> {say_shape(new.shape, self._names)}. NumPy: {call}")
        return self._change(f"repeat whole block {n} times over {self._names[axis]}", new, labels=labels)

    @friendly
    def add_numbers_from(self: _Same, other=None, over=None, only_show_new_shape=False) -> _Same:
        """Add another block's numbers at the end of one direction (NumPy concatenate). block.add_numbers_from(other, over="hour")

        The other directions must have the same sizes; blocks that name every direction are lined up by name first.
        """
        example = f'{self._name}.add_numbers_from(other, over="{self._names[0]}")'
        if over is None:
            raise SimplydataError(f"add_numbers_from() needs over=, the direction to add along.\nFor example:  {example}")
        axis = self._axis("add_numbers_from", over)
        b, b_names, b_named = self._other_parts(other, "add_numbers_from")
        if np.ndim(b) != self._values.ndim:
            raise SimplydataError(f"The other numbers have {np.ndim(b)} directions and this block {self._values.ndim}; "
                                  f"they need the same directions.\nFor example:  {example}")
        if all(self._named) and all(b_named) and sorted(b_names) == sorted(self._names) and b_names != self._names:
            b = np.transpose(b, [b_names.index(n) for n in self._names])
        call = f"np.concatenate([block, other], axis={axis})"
        try:
            if only_show_new_shape:
                shape = np.concatenate([self._stand_in(), np.broadcast_to(0, np.shape(b))], axis=axis).shape
                self._preview(shape, self._names, call)
                return self
            new = np.concatenate([self._values, b], axis=axis)
        except ValueError:
            raise SimplydataError(
                f"The other numbers ({say_shape(np.shape(b), b_names)}) do not fit {self._shape_words()}: every "
                f"direction except {self._names[axis]} needs the same size.\nFor example:  {example}") from None
        labels = self._labels_after(axis, "drop")
        print(f"{self._shape_words()} -> {say_shape(new.shape, self._names)}. NumPy: {call}")
        return self._change(f"add numbers from other over {self._names[axis]}", new, labels=labels)

    @friendly
    def split_into_pieces(self, how_many=None, over=None, only_show_new_shape=False) -> list:
        """Split the block into pieces along a direction; gives back a list of new blocks (NumPy array_split).

        block.split_into_pieces(3, over="hour")
        Pieces are as equal as they can be: 10 hours in 3 pieces gives 4, 3 and 3. The block itself does not change.
        """
        example = f'{self._name}.split_into_pieces(3, over="{self._names[0]}")'
        n = check_whole("split_into_pieces", "split_into_pieces()", how_many, example, smallest=1)
        if over is None and self._values.ndim > 1:
            raise SimplydataError(f"split_into_pieces() needs over=, the direction to split along.\nFor example:  {example}")
        axis = 0 if over is None else self._axis("split_into_pieces", over)
        call = f"np.array_split(block, {n}, axis={axis})"
        if only_show_new_shape:
            shapes = [p.shape for p in np.array_split(self._stand_in(), n, axis=axis)]
            print(f"{self._shape_words()} -> {n} pieces: " + "; ".join(say_shape(s, self._names) for s in shapes)
                  + f" (nothing changed). NumPy: {call}")
            return None
        pieces = np.array_split(self._values, n, axis=axis)
        print(f"{n} pieces along {self._names[axis]}: " + "; ".join(say_shape(p.shape, self._names) for p in pieces)
              + f". NumPy: {call}")
        return [NumberBlock(p.copy(), self._names, self._named) for p in pieces]

    @friendly
    def split_into_one_block_per(self, direction=None) -> list:
        """One new block for each position of a direction, without that direction (NumPy unstack). block.split_into_one_block_per("hour")"""
        axis = self._axis("split_into_one_block_per", direction, "direction")
        names = [n for i, n in enumerate(self._names) if i != axis]
        named = [r for i, r in enumerate(self._named) if i != axis]
        parts = np.unstack(self._values, axis=axis) if hasattr(np, "unstack") else \
            [np.take(self._values, i, axis=axis) for i in range(self._values.shape[axis])]
        print(f"{len(parts)} blocks of {say_shape(self._values.shape[:axis] + self._values.shape[axis + 1:], names)}, "
              f"one for each {self._names[axis]}. NumPy: np.unstack(block, axis={axis})")
        return [NumberBlock(np.asarray(p).copy(), names, named) for p in parts]

    # ------------------------------------------------------------------ summaries over directions
    def _block_summary(self, step: str, func, over, in_each, only_show_new_shape, **more):
        what = f"the {_ordinal(more['q'])} percentile" if step == "percentile" else f"the {step.replace('_', ' ')}"
        np_name = {"average": "nanmean", "median": "nanmedian", "total": "nansum", "smallest": "nanmin",
                   "biggest": "nanmax", "standard_deviation": "nanstd(..., ddof=1)", "percentile": "nanpercentile"}[step]
        axes = self._summary_axes(f"find_{step}", over, in_each)
        a = self._values
        empty = int(self._empty().sum())
        if axes is None or len(axes) == a.ndim:
            if only_show_new_shape:
                print(f"{self._shape_words()} -> one number (nothing changed). NumPy: np.{np_name}(block)")
                return None
            filled = a[~self._empty()]
            if filled.size == 0:
                print(f"Note: there are no numbers here, so {what} is empty (nan).")
                return float("nan")
            if empty:
                print(f"Note: {amount(empty, 'empty value')} {'was' if empty == 1 else 'were'} skipped.")
            answer = plain(_quiet(func, filled, **more))
            print(f"{what[0].upper()}{what[1:]} of the block is {_say_number(answer)} ({amount(filled.size)}). "
                  f"NumPy: np.{np_name}(block)")
            return answer
        kept = [i for i in range(a.ndim) if i not in axes]
        names = [self._names[i] for i in kept]
        gone = " and ".join(say_size(a.shape[i], self._names[i]) for i in axes)
        call = f"np.{np_name.split('(')[0]}(block, axis={_say_numpy_axis(axes)}" + (", ddof=1)" if "ddof" in np_name else ")")
        if only_show_new_shape:
            shape = tuple(a.shape[i] for i in kept)
            print(f"{self._shape_words()} -> {say_shape(shape, names)} (nothing changed). NumPy: {call}")
            return None
        result = _quiet(func, a, axis=tuple(axes), **more)
        if empty:
            print(f"Note: {amount(empty, 'empty value')} {'was' if empty == 1 else 'were'} skipped.")
        verb = {"average": "Averaged", "total": "Added up", "median": "The median taken"}.get(step, f"{what[0].upper()}{what[1:]} taken")
        print(f"{verb} over the {gone}; {say_shape(np.shape(result), names)} remain. NumPy: {call}")
        labels = {n: v for n, v in self._labels.items() if n in names}
        return NumberBlock(np.asarray(result), names, [self._named[i] for i in kept], labels)

    @friendly
    def find_percentile(self, percent=None, over=None, in_each=None, only_show_new_shape=False):
        """The number that this percent of the numbers are below, over some directions. block.find_percentile(90, over="hour")

        NumPy nanpercentile (the usual "linear" method, as pandas and R). Empty values are skipped.
        """
        if not is_number(percent) or not 0 <= percent <= 100:
            raise SimplydataError(".find_percentile() needs a number from 0 to 100." + self._example("find_percentile(90)"))
        return self._block_summary("percentile", np.nanpercentile, over, in_each, only_show_new_shape,
                                   q=float(percent))

    @friendly
    def turn_into_running_total(self: _Same, over=None) -> _Same:
        """Each number becomes the total so far along a direction (NumPy cumsum). block.turn_into_running_total(over="hour")

        Empty values stay empty and are skipped in the total, as pandas cumsum().
        """
        if over is None and self._values.ndim > 1:
            raise SimplydataError(f'turn_into_running_total() needs over=, the direction to run along.\nFor example:  '
                                  f'{self._name}.turn_into_running_total(over="{self._names[0]}")')
        axis = 0 if over is None else self._axis("turn_into_running_total", over)
        empty = self._empty()
        totals = np.cumsum(np.where(empty, 0, self._values), axis=axis)
        if empty.any():
            totals = np.where(empty, np.nan, totals)
        print(f"A running total along {self._names[axis]}. NumPy: np.cumsum(block, axis={axis})")
        return self._change(f"running total over {self._names[axis]}", totals)


_BY = {"add": "adding", "subtract": "subtracting", "times": "multiplying", "divide_by": "dividing"}


def _again(shape, result_shape) -> list:
    """The positions (from the right) where a side of this shape was used again in the result."""
    offset = len(result_shape) - len(shape)
    return [i for i, size in enumerate(result_shape) if size != 1 and (i < offset or shape[i - offset] == 1)]


def _summary_word(step: str):
    func, doc = SUMMARIES[step]

    def word(self, over=None, in_each=None, only_show_new_shape=False):
        return self._block_summary(step, func, over, in_each, only_show_new_shape)

    word.__doc__ = (f"{doc.split(chr(10))[0]}\n\n        block.find_{step}(over=\"hour\")   over= the directions that go;"
                    f" in_each= the directions kept;\n        no option: one number for the whole block. "
                    f"only_show_new_shape=True only says the shape.\n        ")
    word.__name__ = word.__qualname__ = f"find_{step}"
    return friendly(word)


for _step in ("average", "median", "total", "smallest", "biggest", "standard_deviation"):
    setattr(NumberBlock, f"find_{_step}", _summary_word(_step))


# ====================================================================== making blocks
def _from_xarray(values):
    names = [str(d) for d in values.dims]
    labels = {}
    for name in names:
        if name in values.coords and values.coords[name].ndim == 1:
            labels[name] = np.asarray(values.coords[name].values)
    return np.asarray(values.values), names, labels


def _from_table(table, directions, values):
    """A long table (one row per number) as a block: pandas reindex on every combination of the labels, NumPy reshape."""
    import pandas as pd

    example = 'sdata.number_block(sdata.get_example("island"), directions_named=["east", "north"], values="height")'
    frame = table.as_pandas() if hasattr(table, "as_pandas") else (table.to_pandas() if hasattr(table, "to_pandas")
                                                                    else table)
    if directions is None or values is None:
        raise SimplydataError("A block from a table needs directions_named= (the columns that place each number) and "
                          f"values= (the column of numbers).\nFor example:  {example}")
    names = check_names(directions, len(directions) if isinstance(directions, (list, tuple)) else -1,
                        "number_block", example)
    missing = [c for c in [*names, values] if c not in frame.columns]
    if missing:
        raise SimplydataError(f'The table has no column called "{missing[0]}".\nFor example:  {example}')
    keyed = frame.set_index(names)[values]
    if keyed.index.duplicated().any():
        raise SimplydataError(f"Some rows have the same {', '.join(names)}, so one place would hold two numbers. "
                              f"Find the average for each place first.\nFor example:  {example}")
    labels = [np.sort(frame[n].dropna().unique()) for n in names]
    every = pd.MultiIndex.from_product(labels, names=names)
    column = keyed.reindex(every).to_numpy()
    arr = to_array(column, "sdata.number_block()", example).reshape([len(lab) for lab in labels])
    gaps = int(np.isnan(arr).sum()) if arr.dtype.kind == "f" else 0
    print(f"{say_shape(arr.shape, names)} from the column {values}"
          + (f"; {gaps} places have no row and are empty" if gaps else "")
          + ". pandas reindex on every combination, then NumPy reshape.")
    return arr, list(names), {n: lab for n, lab in zip(names, labels)}


def _is_table(value) -> bool:
    return getattr(value, "_is_simplydata_table", False) or type(value).__module__.split(".")[0] in ("pandas",
                                                                                                    "polars")


@friendly
def number_block(source=None, of_shape=None, filled_with=0, like=None, directions_named=None,
                 values=None) -> NumberBlock:
    """Make a block of numbers with any number of directions (NumPy's n-D array, PyTorch's tensor).

    sdata.number_block(of_shape=(24, 8, 12), filled_with=0, directions_named=["hour", "row", "column"])
    sdata.number_block([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])   from lists inside lists (2 pages x 2 rows x 2 columns)
    sdata.number_block(array)                                  from a NumPy array (or an xarray DataArray: its names and labels come too)
    sdata.number_block(table, directions_named=["east", "north"], values="height")   from a long table: the
        directions' labels are the values of those columns
    sdata.number_block(like=plate, filled_with=1)              the shape and names of another block
    Without names the directions are called row and column (the last two), page, book, then direction a, b ...
    filled_with=None makes every number empty.
    """
    sources = [x is not None for x in (source, of_shape, like)]
    if sum(sources) != 1:
        raise SimplydataError(f"sdata.number_block() needs your numbers, or of_shape=, or like= (one of them).\n"
                              f"For example:  {_EXAMPLE}")
    if filled_with is not None and not is_number(filled_with):
        raise SimplydataError(f"filled_with= needs a number, like filled_with=0 (or None for empty values).\n"
                              f"For example:  {_EXAMPLE}")
    if values is not None and not _is_table(source):
        raise SimplydataError("values= names the column of numbers when the block comes from a table.")
    names = labels = None
    named = None
    if like is not None:
        if not _is_block(like):
            raise SimplydataError("like= needs another block.\nFor example:  sdata.number_block(like=plate, filled_with=0)")
        arr = np.full(like._values.shape, np.nan if filled_with is None else filled_with)
        names, named = list(like._names), list(like._named)
    elif of_shape is not None:
        if isinstance(of_shape, _nb.Integral) and not isinstance(of_shape, bool):
            of_shape = (of_shape,)
        if (not isinstance(of_shape, (tuple, list)) or not of_shape
                or not all(isinstance(n, _nb.Integral) and not isinstance(n, bool) and n >= 1 for n in of_shape)):
            raise SimplydataError(f"of_shape= needs the size of each direction in brackets, such as (24, 8, 12).\n"
                                  f"For example:  {_EXAMPLE}")
        arr = np.full(tuple(int(n) for n in of_shape), np.nan if filled_with is None else filled_with)
    elif _is_table(source):
        arr, names, labels = _from_table(source, directions_named, values)
        return NumberBlock(arr, names, [True] * len(names), labels)
    else:
        if type(source).__module__.split(".")[0] == "xarray":
            arr, names, labels = _from_xarray(source)
            named = [True] * len(names)
        elif _is_block(source):
            arr, names, named, labels = (source._values.copy(), list(source._names), list(source._named),
                                         dict(source._labels))
        else:
            raw = np.asarray(source._values if isinstance(source, BaseNumbers) else source)                 if not isinstance(source, (list, tuple)) else None
            if raw is not None and raw.dtype.kind == "b":
                arr = raw.copy()
            else:
                arr = to_array(source, "sdata.number_block()", _EXAMPLE)
        if arr.ndim == 0:
            raise SimplydataError(f"sdata.number_block() needs a list of numbers (one number has no directions).\n"
                                  f"For example:  {_EXAMPLE}")
    if directions_named is not None:
        new_names = check_names(directions_named, arr.ndim, "number_block", _EXAMPLE)
        old = names or []
        labels = {new: labels[o] for o, new in zip(old, new_names) if labels and o in labels}
        names, named = new_names, [True] * arr.ndim
    return NumberBlock(arr, names, named, labels)


@friendly
def stack_up(blocks=None, as_new_direction=None, only_show_new_shape=False) -> NumberBlock:
    """Stack blocks of the same shape into one, along a new first direction (NumPy stack). sdata.stack_up([a, b, c], as_new_direction="image")

    Lists of numbers, grids and blocks all work; they keep their direction names.
    """
    example = 'sdata.stack_up([a, b, c], as_new_direction="image")'
    if not isinstance(blocks, (list, tuple)) or len(blocks) < 2:
        raise SimplydataError(f"sdata.stack_up() needs a list of two or more blocks in square brackets.\nFor example:  {example}")
    if not isinstance(as_new_direction, str) or not as_new_direction.strip():
        raise SimplydataError(f"as_new_direction= needs a name for the new direction, in quotes.\nFor example:  {example}")
    arrays, first = [], blocks[0]
    for block in blocks:
        arrays.append(block._values if isinstance(block, BaseNumbers) else to_array(block, "sdata.stack_up()", example))
    names = list(first._names) if _is_block(first) else default_names(arrays[0].ndim)
    named = list(first._named) if _is_block(first) else [False] * arrays[0].ndim
    if as_new_direction in names:
        raise SimplydataError(f'The blocks already have a direction called "{as_new_direction}".')
    for block, arr in zip(blocks, arrays):
        if _is_block(block) and all(block._named) and all(named) and block._names != names:
            if sorted(block._names) != sorted(names):
                raise SimplydataError("The blocks have different direction names, so they cannot be stacked.")
    shapes = {a.shape for a in arrays}
    if len(shapes) != 1:
        raise SimplydataError("Every block needs the same shape to be stacked: " + "; ".join(
            say_shape(a.shape, default_names(a.ndim)) for a in arrays) + f".\nFor example:  {example}")
    new_names = [as_new_direction] + names
    call = f"np.stack([...], axis=0)"
    if only_show_new_shape:
        shape = np.stack([np.broadcast_to(0, a.shape) for a in arrays]).shape
        print(f"{len(arrays)} blocks of {say_shape(arrays[0].shape, names)} -> {say_shape(shape, new_names)} "
              f"(nothing changed). NumPy: {call}")
        return None
    new = np.stack(arrays, axis=0)
    print(f"{len(arrays)} blocks of {say_shape(arrays[0].shape, names)} -> {say_shape(new.shape, new_names)}. "
          f"NumPy: {call}")
    return NumberBlock(new, new_names, [True] + named)


@friendly
def stretch_to_same_shape(first=None, second=None) -> tuple:
    """Two blocks stretched to one shape, as a sum would line them up; gives back two new blocks (NumPy broadcast_arrays).

    a2, b2 = sdata.stretch_to_same_shape(a, b)
    """
    example = "a2, b2 = sdata.stretch_to_same_shape(a, b)"
    if first is None or second is None:
        raise SimplydataError(f"sdata.stretch_to_same_shape() needs two blocks.\nFor example:  {example}")
    a = first if _is_block(first) else NumberBlock(first._values if isinstance(first, BaseNumbers)
                                                  else to_array(first, "stretch_to_same_shape()", example))
    b, b_names, b_named = a._other_parts(second, "stretch_to_same_shape")
    lined = line_up(a._values, a._names, a._named, b, b_names, b_named, step="add", owner="a")
    if lined.how == "by name":
        x, y = np.broadcast_arrays(lined.a, lined.b)
    else:
        x, y = np.broadcast_arrays(a._values, b)
    print(f"Both are now {say_shape(x.shape, lined.names)} (lined up {lined.how}). NumPy: np.broadcast_arrays(a, b)")
    return (NumberBlock(np.array(x), lined.names, lined.named), NumberBlock(np.array(y), lined.names, lined.named))


@friendly
def hide_stretching_notes() -> None:
    """Stop the notes that say which numbers were used again when blocks are combined. sdata.hide_stretching_notes()"""
    SETTINGS["stretching_notes"] = False
    print("Stretching notes are off; sdata.show_stretching_notes() turns them on again.")


@friendly
def show_stretching_notes() -> None:
    """Print the notes that say which numbers were used again when blocks are combined (the default). sdata.show_stretching_notes()"""
    SETTINGS["stretching_notes"] = True
    print("Stretching notes are on.")
