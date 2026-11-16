"""Numbers and NumberGrid, and the words that make them: numbers(), number_grid(), make_random_numbers()."""

from __future__ import annotations

import math
import numbers as _nb
import sys

import numpy as np

from .._errors import SimplydataError, friendly, option_error
from .._positions import read_positions
from ._base import BaseNumbers, amount, check_seed, check_whole, is_number, plain, to_array
from .distribution_words import DistributionNumberWords
from .maths import MathsWords
from .picking import PickingWords, ReplacingWords
from .signal_words import SignalNumberWords, TimeSeriesNumberWords
from .smoothing_words import SmoothingNumberWords
from .filter_words import FilterNumberWords
from .fourier_words import FourierNumberWords
from .peak_words import PeakNumberWords
from .summaries import GridSummaryWords, SummaryWords


class Numbers(PickingWords, MathsWords, SummaryWords, DistributionNumberWords, SignalNumberWords,
              TimeSeriesNumberWords, SmoothingNumberWords, FilterNumberWords, PeakNumberWords,
              FourierNumberWords, BaseNumbers):
    """A list of numbers. Make one with sdata.numbers([3, 5, 2, 8]), then add steps: nums.add(5)."""

    _is_simplydata_numbers = True
    _name = "nums"
    _noun = "numbers"
    _OLD_WORDS = {**BaseNumbers._OLD_WORDS, "fill_empty": "fill_empty_numbers",
                  "show_first": "show_first_numbers", "show_last": "show_last_numbers",
                  "running_total": "turn_into_running_total", "keep_numbers": "keep_each_number_that",
                  "remove_numbers": "remove_each_number_that", "number_grid": "make_number_grid",
                  "spectrum_of": "find_spectrum", "autocorrelation_of": "find_autocorrelation",
                  "keep_frequencies": "keep_each_frequency_that",
                  "remove_frequencies": "remove_each_frequency_that", "find_peaks": "find_each_peak_that",
                  "find_dips": "find_each_dip_that", "fourier_transform": "take_fourier_transform",
                  "envelope": "find_envelope",}

    def _as_pandas(self, name="value", for_chart=False):
        import pandas as pd

        if not isinstance(name, str) or not name.strip():
            raise SimplydataError('name= needs a column name in quotes, like nums.turn_into_table(name="marks").')
        return pd.DataFrame({name: self._values})

    def _picking_help(self) -> str:
        return (
            "Numbers are picked with words, and positions count from 1:\n"
            "    nums.get_number_at(1)              the first number\n"
            '    nums.get_number_at("last")         the last number\n'
            "    nums.keep_first_numbers(3)     keep only the first 3\n"
            "    nums.keep_numbers_by_position(3, to=8)   the numbers at positions 3 to 8\n"
            "Python's [ ] counts from 0, so simplydata does not use it. "
            "For a NumPy array, use nums.as_numpy()."
        )

    def __repr__(self):
        body = np.array2string(self._values, separator=", ", threshold=60)
        return f"simplydata numbers: {amount(self._values.size)}\n{body}"


_GRID_KEEP_NUMBERS = (
    "A grid keeps its rows and columns, so it cannot drop single numbers (the rows would end up with "
    "different lengths; that is why NumPy's g[g > 5] gives a flat list).\n"
    "For the numbers above 5 as a list:  grid.get_all_numbers().keep_each_number_that(is_above=5)\n"
    "To change them where they are:      grid.replace_each_number_that(is_above=5, with_value=0)\n"
    "To keep whole rows or columns:      grid.keep_rows_by_position(1, to=2)"
)


class NumberGrid(ReplacingWords, GridSummaryWords, MathsWords, BaseNumbers):
    """A grid of numbers in rows and columns. Make one with sdata.number_grid([[1, 2], [3, 4]])."""

    _is_simplydata_grid = True
    _name = "grid"
    _noun = "grid"
    _OLD_WORDS = {**BaseNumbers._OLD_WORDS, "show_first": "show_first_rows", "show_last": "show_last_rows",
                  "shape": "find_shape", "row": "get_row", "column": "get_column", "numbers": "get_all_numbers",}
    # Names people may try on a grid -> the grid word (they never run).
    _HINTS = {"keep_rows": "keep_rows_by_position", "remove_rows": "remove_rows_by_position",
              "keep_rows_where": "keep_rows_by_position", "remove_rows_where": "remove_rows_by_position",
              "keep_columns": "keep_columns_by_position", "remove_columns": "remove_columns_by_position",
              "where": "replace_each_number_that", "clip": "replace_each_number_that", "replace": "replace_each_number_that",
              "replace_values": "replace_each_number_that", "putmask": "replace_each_number_that", "delete": "remove_rows_by_position",
              "take": "keep_rows_by_position", "slice": "keep_rows_by_position",
              "keep_first_rows": "keep_rows_by_position", "keep_last_rows": "keep_rows_by_position"}
    # Words that cannot work on a grid, with the reason and what to write instead.
    _POINTERS = {"keep_each_number_that": _GRID_KEEP_NUMBERS, "remove_each_number_that": _GRID_KEEP_NUMBERS,
                 "keep_numbers": _GRID_KEEP_NUMBERS, "remove_numbers": _GRID_KEEP_NUMBERS}

    def _as_pandas(self, name=None, for_chart=False):
        """A table with columns called "1", "2", ...; for charts the rows are numbered from 1 too."""
        import pandas as pd

        rows, columns = self._values.shape
        frame = pd.DataFrame(self._values, columns=[str(i) for i in range(1, columns + 1)])
        if for_chart:
            frame.index = pd.RangeIndex(1, rows + 1)
        return frame

    def _picking_help(self) -> str:
        return (
            "Numbers in a grid are picked with words, and positions count from 1:\n"
            "    grid.get_number_at(row=1, column=2)   one number\n"
            "    grid.get_row(1)                       the first row, as numbers\n"
            "    grid.get_column(2)                    the second column, as numbers\n"
            "    grid.keep_rows_by_position(2, to=5).keep_columns_by_position(1, to=3)   a block\n"
            "Python's [ ] counts from 0, so simplydata does not use it. "
            "For a NumPy array, use grid.as_numpy()."
        )

    def __repr__(self):
        rows, columns = self._values.shape
        body = np.array2string(self._values, separator=", ", threshold=200)
        return f"simplydata number grid: {amount(rows, 'row')}, {amount(columns, 'column')}\n{body}"

    def __iter__(self):
        return iter(self._values.tolist())  # one list per row

    # ------------------------------------------------------------------ looking
    @friendly
    def count_rows(self):
        """How many rows the grid has. grid.count_rows()"""
        return int(self._values.shape[0])

    @friendly
    def count_columns(self):
        """How many columns the grid has. grid.count_columns()"""
        return int(self._values.shape[1])

    @friendly
    def find_shape(self):
        """How many rows and columns, as (rows, columns). grid.find_shape()"""
        return tuple(int(n) for n in self._values.shape)

    @friendly
    def show_first_rows(self, rows=5):
        """Show the first rows. grid.show_first_rows(5)"""
        n = check_whole("show_first_rows", "show_first_rows()", rows, "grid.show_first_rows(5)")
        print(np.array2string(self._values[:n], threshold=sys.maxsize, separator=", "))
        return None

    @friendly
    def show_last_rows(self, rows=5):
        """Show the last rows. grid.show_last_rows(5)"""
        n = check_whole("show_last_rows", "show_last_rows()", rows, "grid.show_last_rows(5)")
        size = self._values.shape[0]
        print(np.array2string(self._values[size - min(n, size):], threshold=sys.maxsize, separator=", "))
        return None

    def _position(self, step, value, option):
        n = self._values.shape[0 if option == "row" else 1]
        example = f"{step}(row=1, column=2)" if step == "get_number_at" else f"{step}(1)"
        if isinstance(value, str) and value.strip().lower() == "last" and n:
            return n - 1
        if not isinstance(value, (int, np.integer)) or isinstance(value, bool) or not 1 <= value <= n:
            raise SimplydataError(
                f"{option}= needs a whole number from 1 to {n}, or \"last\" (this grid has {amount(n, option)}); "
                f"positions count from 1, so 1 is the first and {n} is the last." + self._example(example)
            )
        return int(value) - 1

    @friendly
    def get_number_at(self, row=None, column=None):
        """The number at a row and column, counting from 1. grid.get_number_at(row=1, column=2)

        "last" is the last row or column: grid.get_number_at(row="last", column="last").
        """
        return plain(self._values[self._position("get_number_at", row, "row"),
                                  self._position("get_number_at", column, "column")])

    @friendly
    def get_row(self, position=None):
        """One row of the grid as new numbers, counting from 1: row(1) is the top row. grid.get_row(1)

        grid.get_row("last") is the bottom row.
        """
        return Numbers(self._values[self._position("row", position, "row")].copy())

    @friendly
    def get_column(self, position=None):
        """One column of the grid as new numbers, counting from 1: column(1) is the left one. grid.get_column(1)

        grid.get_column("last") is the right one.
        """
        return Numbers(self._values[:, self._position("column", position, "column")].copy())

    @friendly
    def get_all_numbers(self):
        """All the numbers of the grid as a list, row by row (flatten). nums = grid.get_all_numbers()"""
        return Numbers(self._values.ravel().copy())

    # ------------------------------------------------------------------ rows and columns by position
    def _grid_picked(self, step: str, positions, to, step_size, conditions: dict, axis: int):
        noun = "row" if axis == 0 else "column"
        example = f"grid.{step}(1, to=2)"
        if conditions:
            key = next(iter(conditions))
            if key in ("above", "below", "at_least", "at_most", "equal_to", "not_equal_to", "between",
                       "one_of", "is_empty"):
                raise SimplydataError(f".{step}() chooses {noun}s by their place, not by their values.\n"
                                      + _GRID_KEEP_NUMBERS)
            raise option_error(step, key, ["positions", "to", "step"])
        return read_positions(
            step, positions, to, step_size, self._values.shape[axis], noun=noun, count_noun=f"{noun}s",
            owner="The grid has", example=example, last_hint=f'grid.{step}("last")',
            after_hint=f"for another order list them, like [3, 2, 1]", name="grid",
        )

    def _grid_step(self, step: str, picked, axis: int, keep: bool):
        noun = "row" if axis == 0 else "column"
        total = self._values.shape[axis]
        if keep:
            chosen = picked.array()
        else:
            if len(picked) == total:
                raise SimplydataError(f"That would remove every {noun}. Keep at least one.\n"
                                      f"For example:  grid.{step}(1)")
            chosen = picked.kept_positions(total)
        new = np.take(self._values, chosen, axis=axis).copy()
        rows, columns = new.shape
        size = f"the grid is now {amount(rows, 'row')} by {amount(columns, 'column')}"
        if keep:
            said = f"Kept {picked.words()}{picked.in_order()} ({len(chosen)} of {amount(total, noun)}); {size}."
        else:
            said = f"Removed {picked.words()} ({len(picked)} of {amount(total, noun)}); {size}."
        print(said)
        if picked.note:
            print(picked.note.format(verb="kept" if keep else "removed"))
        if new.shape[axis] == 1:
            print(f"One {noun} is left, so this is still a grid; grid.get_{noun}(1) gives it as numbers.")
        verb = "keep" if keep else "remove"
        return self._change(f"{verb} {picked.short_words()}", new)

    @friendly
    def keep_rows_by_position(self, positions=None, to=None, step=None, **conditions):
        """Keep rows of the grid by their position, counting from 1: a run, every n-th row, or a list.

        grid.keep_rows_by_position(1, to=2)
        Both ends are included; to="last" goes to the bottom; step=2 keeps every 2nd row; a list
        such as [2, 1] keeps those rows in that order. A block is two steps:
        grid.keep_rows_by_position(2, to=5).keep_columns_by_position(1, to=3), as NumPy g[1:5, 0:3].
        """
        picked = self._grid_picked("keep_rows_by_position", positions, to, step, conditions, 0)
        return self._grid_step("keep_rows_by_position", picked, 0, keep=True)

    @friendly
    def remove_rows_by_position(self, positions=None, to=None, step=None, **conditions):
        """Remove rows of the grid by their position, counting from 1. grid.remove_rows_by_position(1)

        The same positions as keep_rows_by_position. As NumPy np.delete(g, 0, axis=0).
        """
        picked = self._grid_picked("remove_rows_by_position", positions, to, step, conditions, 0)
        return self._grid_step("remove_rows_by_position", picked, 0, keep=False)

    @friendly
    def keep_columns_by_position(self, positions=None, to=None, step=None, **conditions):
        """Keep columns of the grid by their position, counting from 1 at the left. grid.keep_columns_by_position(2, to=3)

        The same positions as keep_rows_by_position: a run (to=), every n-th (step=) or a list.
        As NumPy g[:, 1:3].
        """
        picked = self._grid_picked("keep_columns_by_position", positions, to, step, conditions, 1)
        return self._grid_step("keep_columns_by_position", picked, 1, keep=True)

    @friendly
    def remove_columns_by_position(self, positions=None, to=None, step=None, **conditions):
        """Remove columns of the grid by their position, counting from 1 at the left. grid.remove_columns_by_position(1)

        The same positions as keep_columns_by_position. As NumPy np.delete(g, 0, axis=1).
        """
        picked = self._grid_picked("remove_columns_by_position", positions, to, step, conditions, 1)
        return self._grid_step("remove_columns_by_position", picked, 1, keep=False)

    # ------------------------------------------------------------------ changing the grid
    def replace_each_number_that(self, *args, **kwargs):
        """Replace a number, or every number that meets one condition; the grid keeps its rows and columns.

        grid.replace_each_number_that(is_below=4, with_value=0)
        The conditions are those of keep_each_number_that (one at a time): is_above, is_below,
        is_at_least, is_at_most, is_equal_to, is_not_equal_to, is_between, is_one_of, is_empty; with_value=None makes the numbers empty.
        As NumPy np.where(g < 4, 0, g) or g[g < 4] = 0.
        """
        return ReplacingWords.replace_each_number_that(self, *args, **kwargs)

    replace_each_number_that.__wrapped__ = ReplacingWords.replace_each_number_that  # the same options in sdata.help()

    @friendly
    def swap_rows_and_columns(self):
        """Turn rows into columns and columns into rows (the transpose in maths).

        grid.swap_rows_and_columns()
        A grid of 2 rows and 3 columns becomes 3 rows and 2 columns.
        Matrix multiplication and other linear algebra are planned for simplydata v0.7.
        """
        return self._change("swap rows and columns", self._values.T.copy())

    @friendly
    def turn_into_table(self):
        """Turn the grid into a simplydata table with columns "1", "2", ... grid.turn_into_table()"""
        from ..table import Table

        return Table(self._as_pandas())

    @friendly
    def start_chart(self):
        """Start a chart from this grid, for example a heatmap. grid.start_chart().heatmap(with_numbers=True)"""
        from ..chart import chart

        return chart(self)


# ====================================================================== making numbers
_NUMBERS_EXAMPLE = "sdata.numbers([3, 5, 2, 8])   or   sdata.numbers(1, to=10)"


@friendly
def numbers(*values, to=None, step=None, how_many=None, channel=None) -> Numbers:
    """Make a list of numbers.

    sdata.numbers([3, 5, 2, 8])              these numbers (or sdata.numbers(3, 5, 2, 8))
    sdata.numbers(1, to=10)                  1, 2, 3 ... 10 (the end is included)
    sdata.numbers(0, to=100, step=25)        0, 25, 50, 75, 100
    sdata.numbers(0, to=1, how_many=5)       5 numbers evenly spaced: 0, 0.25, 0.5, 0.75, 1
    sdata.numbers(10, to=1)                  counting down: 10, 9 ... 1
    sdata.numbers("call.wav", channel=1)      the readings of a sound file, scaled to -1 to 1 (they remember their time step)
    None or NaN in a list is an empty (missing) value.
    """
    if len(values) == 1 and isinstance(values[0], str) and values[0].lower().endswith(".wav"):
        return _read_wav(values[0], channel)
    if channel is not None:
        raise SimplydataError('channel= goes with a .wav file, such as sdata.numbers("call.wav", channel=1).')
    if len(values) == 1 and not is_number(values[0]):
        if to is not None or step is not None or how_many is not None:
            raise SimplydataError(
                "to=, step= and how_many= go with a starting number, like sdata.numbers(1, to=10).\n"
                "For a list of your own numbers, write just the list: sdata.numbers([3, 5, 2, 8])"
            )
        arr = to_array(values[0], "sdata.numbers()", _NUMBERS_EXAMPLE)
        if arr.ndim != 1:
            raise SimplydataError(
                "sdata.numbers() makes one list of numbers. For rows and columns, use "
                "sdata.number_grid([[1, 2], [3, 4]])."
            )
        return Numbers(arr)
    if not values:
        raise SimplydataError(f"sdata.numbers() needs some numbers.\nFor example:  {_NUMBERS_EXAMPLE}")
    if len(values) == 1 and to is not None:
        return Numbers(_counting(values[0], to, step, how_many))
    if to is not None or step is not None or how_many is not None:
        raise SimplydataError(
            "to=, step= and how_many= go with one starting number, like sdata.numbers(1, to=10)."
        )
    if len(values) == 1:
        n = say_number(values[0])
        raise SimplydataError(
            f"sdata.numbers({n}) is only one number. For a list with just that number write sdata.numbers([{n}]);\n"
            f"to count up to it write sdata.numbers(1, to={n})."
        )
    return Numbers(to_array(list(values), "sdata.numbers()", _NUMBERS_EXAMPLE))


def _wav_header(file_name):
    """(bits per sample, kind) from the file's header: Python's wave module reads whole-number (PCM) files;
    a file it cannot read is taken as floating point (SciPy reads those)."""
    import wave

    try:
        with wave.open(file_name, "rb") as w:
            return w.getsampwidth() * 8, "whole"
    except (wave.Error, EOFError):
        return None, "float"


def _read_wav(file_name, channel=None):
    """A .wav file as Numbers scaled to -1 to 1 (SciPy io.wavfile), remembering its time step.

    Whole-number (PCM) files are divided by 2^(bits - 1) (8-bit files, stored from 0 to 255, have 128
    taken off first), so every file comes back on the same -1 to 1 scale, as MATLAB audioread and
    Python soundfile give. R tuneR::readWave keeps the whole numbers; the same values in R:
    w <- tuneR::readWave(file); (w@left - (w@bit == 8) * 128) / 2^(w@bit - 1).
    Floating-point files are kept as they are. SciPy reads 24-bit files into 32-bit whole numbers
    (shifted up by 8 bits), so the header (Python's wave module) tells 24-bit from 32-bit.
    """
    from scipy.io import wavfile

    try:
        rate, data = wavfile.read(file_name)
    except FileNotFoundError:
        raise SimplydataError(f'There is no file called "{file_name}".') from None
    except ValueError as error:
        raise SimplydataError(f'"{file_name}" could not be read as a .wav file ({error}).') from None
    channels = 1 if data.ndim == 1 else data.shape[1]
    chosen = 1 if channel is None else channel
    if isinstance(chosen, bool) or not isinstance(chosen, int) or not 1 <= chosen <= channels:
        raise SimplydataError(f"channel= needs a whole number from 1 to {channels} (the file has {channels}).")
    values = data if data.ndim == 1 else data[:, chosen - 1]
    bits, kind = _wav_header(file_name)
    x = np.asarray(values, dtype=float)
    if data.dtype.kind == "f":
        bits, scaling = data.dtype.itemsize * 8, "floating point, kept as they are"
    else:
        bits = bits or data.dtype.itemsize * 8
        stored = data.dtype.itemsize * 8  # SciPy's container: 24-bit samples sit in the top of 32 bits
        if data.dtype.kind == "u":
            x = x - 2.0 ** (stored - 1)
        x = x / 2.0 ** (stored - 1)
        scaling = (f"whole numbers, scaled to -1 to 1 (divided by 2^{bits - 1}"
                   + (", after taking off 128" if data.dtype.kind == "u" else "") + ")")
    nums = Numbers(x)
    nums._time_step = 1.0 / rate
    print(f"{rate:,} readings per second (time step {1 / rate:.3g} s), {len(values) / rate:.3g} seconds, "
          f"{bits}-bit {scaling}, channel {chosen} of {channels}.")
    return nums


def say_number(value) -> str:
    from ._base import say

    return say(value)


def _counting(start, to, step, how_many) -> np.ndarray:
    example = "sdata.numbers(1, to=10)   or   sdata.numbers(0, to=1, how_many=5)"
    for name, value in (("the starting number", start), ("to=", to)):
        if not is_number(value) or not math.isfinite(value):
            raise SimplydataError(f"{name} needs to be a number.\nFor example:  {example}")
    if step is not None and how_many is not None:
        raise SimplydataError(
            "Give step= (the gap between numbers) or how_many= (how many numbers), not both.\n"
            "For example:  sdata.numbers(0, to=100, step=25)   or   sdata.numbers(0, to=1, how_many=5)"
        )
    if how_many is not None:
        n = check_whole("numbers", "how_many=", how_many, "sdata.numbers(0, to=1, how_many=5)")
        return np.linspace(start, to, n)
    if step is None:
        step = 1 if to >= start else -1
    if not is_number(step) or step == 0 or not math.isfinite(step):
        raise SimplydataError(f"step= needs a number that is not 0, like step=2.\nFor example:  sdata.numbers(0, to=100, step=25)")
    if (to - start) * step < 0:
        raise SimplydataError(
            f"Going from {say_number(start)} to {say_number(to)} with step={say_number(step)} never gets there.\n"
            f"To count {'down' if to < start else 'up'}, use step={say_number(-step)}."
        )
    n = int(math.floor((to - start) / step + 1e-9)) + 1
    if all(isinstance(v, _nb.Integral) for v in (start, step)):
        return start + step * np.arange(n, dtype=np.int64)
    return start + step * np.arange(n, dtype=np.float64)


_GRID_EXAMPLE = "sdata.number_grid([[1, 2], [3, 4]])   or   sdata.number_grid(rows=3, columns=4, filled_with=0)"


@friendly
def number_grid(values=None, rows=None, columns=None, filled_with=0) -> NumberGrid:
    """Make a grid of numbers in rows and columns.

    sdata.number_grid([[1, 2, 3], [4, 5, 6]])            from rows of numbers (2 rows, 3 columns)
    sdata.number_grid(rows=3, columns=4, filled_with=0)  a grid of 0s (filled_with=1 for 1s, or any number)
    sdata.number_grid([1, 2, 3, 4, 5, 6], columns=3)     a list cut into rows of 3
    """
    for option, value in (("rows=", rows), ("columns=", columns)):
        if value is not None:
            check_whole("make_number_grid", option, value, _GRID_EXAMPLE, smallest=1)
    if values is None:
        if rows is None or columns is None:
            raise SimplydataError(f"sdata.number_grid() needs your numbers, or rows= and columns=.\nFor example:  {_GRID_EXAMPLE}")
        if filled_with is not None and not is_number(filled_with):
            raise SimplydataError(
                "filled_with= needs a number, like filled_with=0 (or None for empty values).\n"
                f"For example:  {_GRID_EXAMPLE}"
            )
        fill = np.nan if filled_with is None else filled_with
        return NumberGrid(np.full((int(rows), int(columns)), fill))
    arr = to_array(values, "sdata.number_grid()", _GRID_EXAMPLE)
    if arr.ndim == 2:
        if rows is not None or columns is not None:
            raise SimplydataError(
                "Your numbers already have rows, so leave out rows= and columns=.\n"
                "For example:  sdata.number_grid([[1, 2, 3], [4, 5, 6]])"
            )
        return NumberGrid(arr)
    if arr.ndim != 1:
        raise SimplydataError(f"sdata.number_grid() needs rows of numbers.\nFor example:  {_GRID_EXAMPLE}")
    if rows is None and columns is None:
        raise SimplydataError(
            "To make a grid from one list, say how many columns (or rows) it should have.\n"
            "For example:  sdata.number_grid([1, 2, 3, 4, 5, 6], columns=3)"
        )
    size = arr.size
    rows = rows if rows is not None else (size // columns if size % columns == 0 else None)
    columns = columns if columns is not None else (size // rows if rows and size % rows == 0 else None)
    if rows is None or columns is None or rows * columns != size:
        raise SimplydataError(
            f"{amount(size)} cannot fill that grid exactly. "
            "The number of rows times the number of columns must equal how many numbers you have.\n"
            "For example, 6 numbers make 2 rows of 3:  sdata.number_grid([1, 2, 3, 4, 5, 6], columns=3)"
        )
    return NumberGrid(arr.reshape(int(rows), int(columns)))


@friendly(renamed={"seed": "with_seed"})
def make_random_numbers(how_many=None, between=None, average=None, standard_deviation=None,
                        whole_numbers=False, with_seed=None, rows=None, columns=None):
    """Make random numbers; give with_seed= to get the same numbers every time.

    sdata.make_random_numbers(how_many=10, between=[0, 1], with_seed=1)
        any number from 0 up to 1, each equally likely (a uniform distribution)
    sdata.make_random_numbers(how_many=10, between=[1, 6], whole_numbers=True, with_seed=1)
        whole numbers from 1 to 6, both ends included, like rolling a dice
    sdata.make_random_numbers(how_many=100, average=50, standard_deviation=10, with_seed=1)
        numbers that bunch around the average in a bell shape (a normal distribution);
        about 2 in 3 land within one standard deviation of the average
    rows= and columns= in place of how_many= give a grid.
    """
    example = "sdata.make_random_numbers(how_many=10, between=[0, 1], with_seed=1)"
    with_seed = check_seed(with_seed, example)
    if not isinstance(whole_numbers, bool):
        raise SimplydataError(f"whole_numbers= needs True or False (no quotes).\nFor example:  {example}")
    if how_many is not None and (rows is not None or columns is not None):
        raise SimplydataError(
            "Give how_many= for a list, or rows= and columns= for a grid, not both.\n"
            f"For example:  {example}"
        )
    if how_many is not None:
        size = check_whole("random_numbers", "how_many=", how_many, example)
    elif rows is not None and columns is not None:
        size = (check_whole("random_numbers", "rows=", rows, example, smallest=1),
                check_whole("random_numbers", "columns=", columns, example, smallest=1))
    else:
        raise SimplydataError(
            "sdata.make_random_numbers() needs how_many= (or rows= and columns= for a grid).\n"
            f"For example:  {example}"
        )
    bell = average is not None or standard_deviation is not None
    if bell and between is not None:
        raise SimplydataError(
            "Give between=[low, high] for numbers spread evenly, or average= and standard_deviation= for a "
            "bell shape (normal distribution), not both.\n"
            "For example:  sdata.make_random_numbers(how_many=100, average=50, standard_deviation=10, with_seed=1)"
        )
    rng = np.random.default_rng(with_seed)
    if bell:
        bell_example = "sdata.make_random_numbers(how_many=100, average=50, standard_deviation=10, with_seed=1)"
        if not is_number(average) or not is_number(standard_deviation) or standard_deviation < 0:
            raise SimplydataError(
                "A bell shape needs both average= and standard_deviation= as numbers "
                f"(the standard deviation cannot be below 0).\nFor example:  {bell_example}"
            )
        if whole_numbers:
            raise SimplydataError(
                "whole_numbers=True goes with between=[low, high]. For a bell shape, round afterwards: "
                "nums.round_to(0)."
            )
        values = rng.normal(average, standard_deviation, size)
    else:
        low, high = _two_numbers(between if between is not None else [0, 1], example)
        if whole_numbers:
            if not all(float(v).is_integer() for v in (low, high)):
                raise SimplydataError(
                    "whole_numbers=True needs whole numbers in between=, like between=[1, 6]."
                )
            values = rng.integers(int(low), int(high), size, endpoint=True)
        else:
            values = rng.uniform(low, high, size)
    return NumberGrid(values) if isinstance(size, tuple) else Numbers(values)


def _two_numbers(between, example):
    if (isinstance(between, (str, bytes)) or not isinstance(between, (list, tuple)) or len(between) != 2
            or not all(is_number(v) and math.isfinite(v) for v in between)):
        raise SimplydataError(f"between= needs two numbers in square brackets: the lowest and the highest.\nFor example:  {example}")
    return sorted(between)
