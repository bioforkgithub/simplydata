"""Numbers phase, batch 3 (approved by Manish 2026-11-25): words on numbers and on grids of numbers.

On numbers: turn_into_running_area (SciPy integrate.cumulative_trapezoid / cumulative_simpson), find_coherence_with
(SciPy signal.coherence), take_cosine_transform (SciPy fft.dct). On numbers and grids: take_cube_root (NumPy cbrt) and
show_as_fraction (SymPy nsimplify). On grids: get_numbers_at_pairs (NumPy indexing with pairs),
get_numbers_from_each_row_at (NumPy take_along_axis), find_each_patch_that (SciPy ndimage.label, sum_labels, mean,
center_of_mass), change_size_to (SciPy ndimage.zoom), rotate(by_degrees=) (SciPy ndimage.rotate), take_matrix_exp
(SciPy linalg.expm) and find_null_space (SciPy linalg.null_space). Positions count from 1, as everywhere in
simplydata; the sentence also gives NumPy's own positions (from 0). Own code is glue only.
"""

from __future__ import annotations

from .._typing import _Same

import math

import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from .._time_axis import read_time_step
from ._base import NOT_GIVEN, amount, is_number, say

RUNNING_AREA_METHODS = {"trapezoid": ("the trapezoid rule", "SciPy integrate.cumulative_trapezoid"),
                        "simpson": ("Simpson's rule", "SciPy integrate.cumulative_simpson")}
ZOOM_ORDERS = {"nearest": (0, "the nearest cell"), "linear": (1, "straight lines between neighbouring cells"),
               "cubic": (3, "smooth cubic curves (splines) through the cells")}
TOUCHING = {"sides": 1, "corners": 2}
COHERENCE_SEGMENT = 256  # SciPy signal.coherence's own segment length (nperseg)
COHERENCE_PIECES = 4.5   # shorter recordings: eight half-overlapping segments, as MATLAB mscohere (n / 4.5 each)


def _no_empty(values, step: str):
    if values.dtype.kind == "f" and np.isnan(values).any():
        raise SimplydataError(f"{step}() needs a value in every place; fill the empty ones first "
                              "(fill_empty_numbers or replace_each_number_that(is_empty=True, with_value=0)).")


# find_each_patch_that(show=): families for 100 %, batch 21 (approved by Manish 2026-11-28, plan section 2.9)
PATCH_SHOW = ("biggest", "smallest", "where biggest", "where smallest", "median", "standard deviation", "variance",
              "range", "positions", "counts in bins")


def _patch_show(show, bins) -> list[str]:
    """The show= values of find_each_patch_that, checked: one value or a list."""
    if show is None:
        if bins is not None:
            raise SimplydataError('bins= goes with show="counts in bins".')
        return []
    shown = [show] if isinstance(show, str) else show
    if not isinstance(shown, (list, tuple)) or not shown:
        raise SimplydataError('show= takes one value or a list, such as show=["biggest", "where biggest"].')
    for value in shown:
        if value not in PATCH_SHOW:
            raise choice_error("find_each_patch_that", "show", value, list(PATCH_SHOW))
    if ("counts in bins" in shown) != (bins is not None):
        raise SimplydataError('show="counts in bins" needs bins=, the number of equal bins (such as bins=4), and '
                              "bins= goes with it only.")
    if bins is not None and (not isinstance(bins, (int, np.integer)) or isinstance(bins, bool) or bins < 1):
        raise SimplydataError("bins= needs a whole number of bins, 1 or more.")
    return list(dict.fromkeys(shown))


def _patch_columns(shown, bins, values, labels, index) -> dict:
    """The extra columns of find_each_patch_that(show=), each from SciPy ndimage on the patch labels."""
    from scipy import ndimage

    count = len(index)
    columns = {}
    if not count:
        names = [c for v in shown for c in (["row of biggest", "column of biggest"] if v == "where biggest" else
                                            ["row of smallest", "column of smallest"] if v == "where smallest" else
                                            [f"bin {i}" for i in range(1, bins + 1)] if v == "counts in bins" else
                                            [v])]
        return {name: [] for name in names}
    if {"biggest", "smallest", "where biggest", "where smallest"} & set(shown):
        smallest, biggest, where_small, where_big = ndimage.extrema(values, labels, index)
        where_small, where_big = np.asarray(where_small).reshape(-1, 2), np.asarray(where_big).reshape(-1, 2)
    for value in shown:
        if value == "biggest":
            columns["biggest"] = np.asarray(biggest, dtype=float)
        elif value == "smallest":
            columns["smallest"] = np.asarray(smallest, dtype=float)
        elif value == "where biggest":
            columns["row of biggest"], columns["column of biggest"] = where_big[:, 0] + 1, where_big[:, 1] + 1
        elif value == "where smallest":
            columns["row of smallest"], columns["column of smallest"] = where_small[:, 0] + 1, where_small[:, 1] + 1
        elif value in ("median", "standard deviation", "variance"):
            function = {"median": ndimage.median, "standard deviation": ndimage.standard_deviation,
                        "variance": ndimage.variance}[value]
            columns[value] = np.asarray(function(values, labels, index), dtype=float)
        elif value == "range":
            columns["range"] = ndimage.labeled_comprehension(values, labels, index, np.ptp, float, np.nan)
        elif value == "positions":
            found = ndimage.value_indices(labels, ignore_value=0)
            columns["positions"] = [" ".join(f"({r + 1}, {c + 1})" for r, c in zip(*found[i])) for i in index]
        else:  # the bins run over the cells of the patches (never empty: an empty cell is in no patch)
            inside = values[labels > 0]
            low, high = float(np.nanmin(inside)), float(np.nanmax(inside))
            if low == high:
                if bins != 1:
                    raise SimplydataError(f'show="counts in bins": every cell of the patches is {low:.6g}, so there '
                                          "is only one bin; use bins=1.")
                columns["bin 1"] = [int(v) for v in ndimage.sum_labels(np.ones_like(values), labels, index)]
                print(f"Every cell of the patches is {low:.6g}, so bin 1 holds them all (SciPy ndimage.sum_labels).")
                continue
            counts = ndimage.histogram(values, low, high, bins, labels, index)
            for b in range(bins):
                columns[f"bin {b + 1}"] = [int(np.asarray(c)[b]) for c in counts]
            print(f"The bins run from {low:.6g} to {high:.6g} (the smallest and biggest cell of the patches) in "
                  f"{bins} equal steps (SciPy ndimage.histogram(grid, {low:.6g}, {high:.6g}, {bins}, labels, "
                  "patches)).")
    return columns


# ---------------------------------------------------------------- numbers and grids
class SharedWords3:
    @friendly
    def take_cube_root(self: _Same) -> _Same:
        """The cube root of every number: 27 becomes 3, and -8 becomes -2. numbers.take_cube_root()

        Unlike raise_to_power(1/3), a negative number keeps its real cube root. NumPy cbrt.
        """
        with np.errstate(all="ignore"):
            result = np.cbrt(self._values.astype(float))
        print(f"The cube root of each of the {self._values.size} numbers (NumPy cbrt; a negative number keeps its "
              "minus sign).")
        return self._change("cube root", result)

    @friendly
    def show_as_fraction(self) -> None:
        """Show each number as a fraction, such as 0.25 as 1/4; the numbers do not change. numbers.show_as_fraction()

        Each number is written with all the digits Python keeps (about 16), and SymPy nsimplify(rational=True) gives
        the fraction of exactly those digits: 1/3 worked out as a decimal (0.3333333333333333) shows as 1/3, but
        0.333333 typed with six digits shows as 333333/1000000, and a number that is no simple fraction shows its
        digits over a power of 10. Needs the extra simplydata[exact] (SymPy).
        """
        from .._formula import fraction_text

        values = np.asarray(self._values, dtype=float)
        if values.ndim == 1:
            print("[" + ", ".join(fraction_text(v) for v in values) + "]")
        else:
            for row in values:
                print("[" + ", ".join(fraction_text(v) for v in row) + "]")
        print("(As fractions by SymPy nsimplify; the numbers themselves do not change.)")
        return None


# ---------------------------------------------------------------- numbers only
class NumberWords3:
    @friendly(renamed={"method": "test_method"})
    def turn_into_running_area(self: _Same, time_step=None, test_method="trapezoid", sampling_rate=None,
                               fs=None) -> _Same:
        """Turn readings into the area so far under their curve (a running integral). numbers.turn_into_running_area(time_step=60)

        A flow per second read every 60 seconds becomes the volume so far. The first number becomes 0 and the
        last is the whole area. test_method="trapezoid" (the default; SciPy integrate.cumulative_trapezoid,
        straight lines between readings) or "simpson" (cumulative_simpson). Undo with numbers.undo().
        """
        from scipy import integrate

        key = str(test_method).strip().lower()
        if key not in RUNNING_AREA_METHODS:
            raise choice_error("turn_into_running_area", "test_method", test_method, list(RUNNING_AREA_METHODS))
        x = np.asarray(self._values, dtype=float).ravel()
        _no_empty(x, "turn_into_running_area")
        if x.size < 2:
            raise SimplydataError("turn_into_running_area() needs at least 2 readings.")
        step, words = read_time_step(time_step, sampling_rate, fs, getattr(self, "_time_step", None),
                                     "turn_into_running_area")
        if time_step is None and sampling_rate is None and fs is None and getattr(self, "_time_step", None) is None:
            words = "time step 1 between readings (give time_step= for another)"
        if key == "trapezoid":
            out = integrate.cumulative_trapezoid(x, dx=step, initial=0)
        else:
            out = integrate.cumulative_simpson(x, dx=step, initial=0)
        how, call = RUNNING_AREA_METHODS[key]
        print(f"The area so far under {x.size} readings ({words}), by {how} ({call}). The whole area is "
              f"{out[-1]:.6g}.")
        return self._change("running area", out)

    @friendly
    def find_coherence_with(self, other=None, time_step=None, sampling_rate=None, fs=None):
        """How closely two recordings follow each other at each frequency, from 0 to 1 (the coherence).

        numbers.find_coherence_with(other, time_step=0.01)
        Gives back a table: frequency, coherence. 1 means the two always move together at that frequency
        (with a fixed delay), 0 that they are unrelated there. Welch's method: SciPy signal.coherence with its own
        settings (Hann window, segments half overlapping, no padding). The segments are SciPy's 256 readings for a
        recording of 1152 readings or more; a shorter one is cut into eight half-overlapping segments of n / 4.5
        readings (only this rule follows MATLAB mscohere), so the coherence is always an average.
        """
        import pandas as pd
        from scipy import signal

        from ..table import Table
        from ._base import to_array

        if other is None:
            raise SimplydataError("find_coherence_with() needs the other recording, as numbers of the same length."
                                  + self._example("find_coherence_with(other, time_step=0.01)"))
        x = np.asarray(self._values, dtype=float).ravel()
        y = np.asarray(to_array(other, "find_coherence_with()", "numbers.find_coherence_with([1, 2, 3])"),
                       dtype=float).ravel()
        if x.size != y.size:
            raise SimplydataError(f"find_coherence_with() needs two recordings of the same length; these have "
                                  f"{x.size} and {y.size} readings.")
        _no_empty(x, "find_coherence_with")
        _no_empty(y, "find_coherence_with")
        if x.size < 16:
            raise SimplydataError("find_coherence_with() needs at least 16 readings in each recording.")
        step, words = read_time_step(time_step, sampling_rate, fs, getattr(self, "_time_step", None),
                                     "find_coherence_with")
        segment = COHERENCE_SEGMENT if x.size >= COHERENCE_SEGMENT * COHERENCE_PIECES else \
            int(x.size // COHERENCE_PIECES)
        frequency, together = signal.coherence(x, y, fs=1.0 / step, nperseg=segment)
        best = int(np.argmax(together[1:])) + 1 if together.size > 1 else 0
        print(f"Coherence of two recordings of {x.size} readings ({words}): at each frequency, 0 = unrelated, "
              f"1 = always moving together. The highest after frequency 0 is {together[best]:.3f}, at frequency "
              f"{frequency[best]:.6g}.")
        print(f"Method: Welch's method, SciPy signal.coherence (Hann window, segments of {segment} readings, half "
              "overlapping).")
        return Table(pd.DataFrame({"frequency": frequency, "coherence": together}))

    @friendly
    def take_cosine_transform(self: _Same, kind="cosine", inverse=False, log_step=None, order=0) -> _Same:
        """The numbers as a sum of cosine waves: the size of each (the discrete cosine transform). numbers.take_cosine_transform()

        The type-2 transform with orthonormal scaling (SciPy fft.dct(type=2, norm="ortho")), so the sum of
        squares stays the same; the first numbers hold the slow changes. kind="sine" gives the sine transform (dst);
        inverse=True turns transformed numbers back (idct, idst). kind="hankel" is the fast Hankel transform of
        numbers spaced evenly on a log scale (SciPy fft.fht, inverse ifht): log_step= is the step of the natural log
        between them and order= the order of the Bessel function. Undo with numbers.undo().
        """
        from scipy import fft

        if kind not in ("cosine", "sine", "hankel"):
            raise choice_error("take_cosine_transform", "kind", kind, ["cosine", "sine", "hankel"])
        if not isinstance(inverse, bool):
            raise SimplydataError("inverse= needs True or False (no quotes).")
        x = np.asarray(self._values, dtype=float).ravel()
        _no_empty(x, "take_cosine_transform")
        if kind == "hankel":
            if not is_number(log_step) or log_step <= 0 or not is_number(order):
                raise SimplydataError('kind="hankel" needs log_step= (the step of the natural log between the numbers, '
                                      "above 0) and order= (a number), such as log_step=0.1, order=0.")
            func = fft.ifht if inverse else fft.fht
            out = func(x, dln=float(log_step), mu=float(order))
            print(f"The {'inverse ' if inverse else ''}fast Hankel transform of {x.size} numbers (SciPy "
                  f"fft.{func.__name__}, dln={say(log_step)}, mu={say(order)}).")
            return self._change(f"{'inverse ' if inverse else ''}hankel transform", out)
        if log_step is not None or order != 0:
            raise SimplydataError('log_step= and order= go with kind="hankel".')
        func = {("cosine", False): fft.dct, ("sine", False): fft.dst, ("cosine", True): fft.idct,
                ("sine", True): fft.idst}[(kind, inverse)]
        out = func(x, type=2, norm="ortho")
        if kind == "cosine" and not inverse:
            print(f"The cosine transform of {x.size} numbers (SciPy fft.dct, type 2, orthonormal): number 1 is the "
                  "average level, the next ones ever faster cosine waves.")
            return self._change("cosine transform", out)
        print(f"The {'inverse ' if inverse else ''}{kind} transform of {x.size} numbers (SciPy fft.{func.__name__}, "
              "type 2, orthonormal).")
        return self._change(f"{'inverse ' if inverse else ''}{kind} transform", out)


# ---------------------------------------------------------------- grids only
class GridWords3:
    def _positions_of(self, step: str, values, option: str, size: int, example: str) -> list[int]:
        if is_number(values):
            values = [values]
        if hasattr(values, "_values"):
            values = np.asarray(values._values).ravel().tolist()
        if isinstance(values, (str, bytes)) or not isinstance(values, (list, tuple, np.ndarray, range)):
            raise SimplydataError(f"{option}= needs a list of whole numbers from 1 to {size}.\nFor example:  {example}")
        found = []
        for v in values:
            if isinstance(v, (bool, np.bool_)) or not is_number(v) or float(v) != int(v) or not 1 <= v <= size:
                raise SimplydataError(f"{option}= needs whole numbers from 1 to {size} (positions count from 1; this "
                                      f"grid has {amount(size, option[:-1])}); it has {v!r}.\nFor example:  {example}")
            found.append(int(v))
        return found

    @friendly
    def get_numbers_at_pairs(self, rows=None, columns=None):
        """The numbers at pairs of a row and a column, counting from 1. grid.get_numbers_at_pairs(rows=[1, 2], columns=[3, 3])

        rows=[1, 2, 3] with columns=[4, 4, 5] gives three numbers: at (1, 4), (2, 4) and (3, 5). For the
        rectangle of those rows and columns, use keep_rows_by_position then keep_columns_by_position. As NumPy
        g[[0, 1, 2], [3, 3, 4]] (from 0).
        """
        from .numbers import Numbers

        example = "grid.get_numbers_at_pairs(rows=[1, 2], columns=[3, 3])"
        n_rows, n_columns = self._values.shape
        if rows is None or columns is None:
            raise SimplydataError(f"get_numbers_at_pairs() needs rows= and columns=, one of each for every pair.\n"
                                  f"For example:  {example}")
        r = self._positions_of("get_numbers_at_pairs", rows, "rows=", n_rows, example)
        c = self._positions_of("get_numbers_at_pairs", columns, "columns=", n_columns, example)
        if len(r) != len(c):
            raise SimplydataError(f"get_numbers_at_pairs() needs as many rows as columns, one of each for every "
                                  f"pair; it got {len(r)} rows and {len(c)} columns.\nFor the rectangle of these rows "
                                  "and columns, use keep_rows_by_position then keep_columns_by_position.")
        picked = self._values[np.array(r) - 1, np.array(c) - 1]
        pairs = ", ".join(f"({a}, {b})" for a, b in zip(r[:6], c[:6])) + (" ..." if len(r) > 6 else "")
        print(f"{amount(len(r))} at the pairs (row, column) {pairs}. NumPy: g[{[a - 1 for a in r][:6]}, "
              f"{[b - 1 for b in c][:6]}] (from 0). For the rectangle of these rows and columns, use "
              "keep_rows_by_position then keep_columns_by_position.")
        return Numbers(np.array(picked).copy())

    @friendly
    def get_numbers_from_each_row_at(self, columns=None):
        """From each row, the numbers at its own columns, counting from 1. grid.get_numbers_from_each_row_at(columns=[2, 1])

        columns= has one position for each row (a list), or a grid with one row of positions for each row. As
        NumPy take_along_axis(g, positions - 1, axis=1).
        """
        from .numbers import NumberGrid, Numbers
        from ._base import to_array

        example = "grid.get_numbers_from_each_row_at(columns=[2, 1])"
        n_rows, n_columns = self._values.shape
        if columns is None:
            raise SimplydataError(f"get_numbers_from_each_row_at() needs columns=, the positions to take from each "
                                  f"row.\nFor example:  {example}")
        positions = to_array(columns, "get_numbers_from_each_row_at()", example)
        one_each = positions.ndim == 1
        if one_each:
            positions = positions.reshape(-1, 1)
        if positions.ndim != 2 or positions.shape[0] != n_rows:
            raise SimplydataError(f"columns= needs one position (or one row of positions) for each of the {n_rows} "
                                  f"rows; it has {positions.shape[0]}.\nFor example:  {example}")
        if positions.dtype.kind == "f" and (np.isnan(positions).any() or (positions != np.round(positions)).any()):
            raise SimplydataError("columns= needs whole numbers (positions count from 1).")
        positions = positions.astype(np.int64)
        if positions.min() < 1 or positions.max() > n_columns:
            raise SimplydataError(f"columns= needs positions from 1 to {n_columns} (this grid has "
                                  f"{amount(n_columns, 'column')}).")
        picked = np.take_along_axis(self._values, positions - 1, axis=1)
        print(f"From each of the {n_rows} rows, {amount(positions.shape[1])} at its own columns (NumPy "
              "take_along_axis, positions - 1, axis=1).")
        return Numbers(picked.ravel().copy()) if one_each else NumberGrid(picked.copy())

    @friendly(renamed={"above": "is_above", "below": "is_below", "at_least": "is_at_least", "at_most": "is_at_most",
                       "equal_to": "is_equal_to", "between": "is_between"})
    def find_each_patch_that(self, is_above=NOT_GIVEN, is_below=NOT_GIVEN, is_at_least=NOT_GIVEN,
                             is_at_most=NOT_GIVEN, is_equal_to=NOT_GIVEN, is_not_equal_to=NOT_GIVEN,
                             is_between=NOT_GIVEN, is_one_of=NOT_GIVEN, touching="sides", show=None, bins=None):
        """Find each patch of touching cells that meet a condition. grid.find_each_patch_that(is_above=5)

        Gives back a table: patch, cells, total, average, centre row, centre column (counting from 1; each cell
        counts the same). touching="sides" (the default: cells that share a side) or "corners" (a shared corner
        is enough). Empty cells are never in a patch. SciPy ndimage.label, sum_labels, mean and center_of_mass.
        show= adds columns, one value or a list: "biggest", "smallest" and "where biggest", "where smallest" (the
        row and column, from 1; SciPy ndimage.extrema), "median", "standard deviation", "variance" (SciPy ndimage's
        own, with n in the bottom, as NumPy), "range" (biggest minus smallest;
        labeled_comprehension with NumPy ptp), "positions" (every cell of the patch, from 1; value_indices) and
        "counts in bins" with bins= a number of equal bins from the smallest to the biggest cell of the patches
        (ndimage.histogram).
        """
        import pandas as pd
        from scipy import ndimage

        from ..table import Table

        if touching not in TOUCHING:
            raise choice_error("find_each_patch_that", "touching", touching, list(TOUCHING))
        shown = _patch_show(show, bins)
        options = dict(above=is_above, below=is_below, at_least=is_at_least, at_most=is_at_most,
                       equal_to=is_equal_to, not_equal_to=is_not_equal_to, between=is_between, one_of=is_one_of)
        mask, words = self._condition("find_each_patch_that", options, ())
        structure = ndimage.generate_binary_structure(2, TOUCHING[touching])
        labels, count = ndimage.label(mask, structure=structure)
        values = np.asarray(self._values, dtype=float)
        index = np.arange(1, count + 1)
        if count:
            cells = ndimage.sum_labels(np.ones_like(values), labels, index)
            totals = ndimage.sum_labels(values, labels, index)
            averages = ndimage.mean(values, labels, index)
            centres = np.array(ndimage.center_of_mass(mask.astype(float), labels, index), dtype=float).reshape(-1, 2)
        else:
            cells = totals = averages = np.array([], dtype=float)
            centres = np.empty((0, 2))
        table = pd.DataFrame({"patch": index, "cells": np.asarray(cells, dtype=np.int64), "total": totals,
                              "average": averages, "centre row": centres[:, 0] + 1,
                              "centre column": centres[:, 1] + 1})
        print(f"{count} {'patch' if count == 1 else 'patches'} of cells {words.replace('are ', '')}, "
              f"touching by their {touching} ({int(mask.sum())} of {values.size} cells). SciPy ndimage.label; the "
              "centres count from 1.")
        if shown:
            for name, column in _patch_columns(shown, bins, values, labels, index).items():
                table[name] = column
        return Table(table)

    def _new_grid_values(self, step: str, what: str, values, before):
        rows, columns = before
        new_rows, new_columns = values.shape
        print(f"{what}: {amount(rows, 'row')} x {amount(columns, 'column')} -> {amount(new_rows, 'row')} x "
              f"{amount(new_columns, 'column')}.")
        return self._change(step, values)

    @friendly(renamed={"method": "test_method"})
    def change_size_to(self: _Same, rows=None, columns=None, test_method="linear") -> _Same:
        """Make the grid bigger or smaller, filling in between the cells (resampling). grid.change_size_to(rows=4, columns=6)

        test_method="linear" (the default: straight lines between neighbouring cells), "nearest" (the nearest
        cell) or "cubic" (smooth spline curves). SciPy ndimage.zoom. NumPy's resize only repeats numbers; this
        works out new ones. Undo with grid.undo().
        """
        from scipy import ndimage

        example = "grid.change_size_to(rows=4, columns=6)"
        if test_method not in ZOOM_ORDERS:
            raise choice_error("change_size_to", "test_method", test_method, list(ZOOM_ORDERS))
        before = self._values.shape
        for name, value in (("rows", rows), ("columns", columns)):
            if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < 1:
                raise SimplydataError(f"change_size_to() needs {name}= as a whole number of at least 1.\n"
                                      f"For example:  {example}")
        values = np.asarray(self._values, dtype=float)
        _no_empty(values, "change_size_to")
        order, how = ZOOM_ORDERS[test_method]
        out = ndimage.zoom(values, (rows / before[0], columns / before[1]), order=order)
        if out.shape != (rows, columns):  # pragma: no cover - SciPy rounds the size it is given
            raise SimplydataError(f"SciPy made a grid of {out.shape}, not {(rows, columns)}.")
        return self._new_grid_values("change size", f"New size by {how} (SciPy ndimage.zoom, order {order})", out,
                                     before)

    @friendly(renamed={"method": "test_method"})
    def rotate(self: _Same, by_degrees=None, test_method="linear") -> _Same:
        """Turn the picture of the grid round its centre, anticlockwise, by some degrees. grid.rotate(by_degrees=15)

        The grid keeps its size; cells that come from outside the old grid are empty. test_method="linear" (the
        default), "nearest" or "cubic", as change_size_to. SciPy ndimage.rotate(reshape=False). Undo with
        grid.undo().
        """
        from scipy import ndimage

        if by_degrees is None or not is_number(by_degrees) or not math.isfinite(by_degrees):
            raise SimplydataError("rotate() needs by_degrees= as a number: positive turns anticlockwise."
                                  + self._example("rotate(by_degrees=15)"))
        if test_method not in ZOOM_ORDERS:
            raise choice_error("rotate", "test_method", test_method, list(ZOOM_ORDERS))
        values = np.asarray(self._values, dtype=float)
        _no_empty(values, "rotate")
        order, how = ZOOM_ORDERS[test_method]
        out = ndimage.rotate(values, float(by_degrees), reshape=False, order=order, mode="constant", cval=np.nan)
        empty = int(np.isnan(out).sum())
        print(f"Turned by {say(by_degrees)} degrees anticlockwise round the centre, by {how} (SciPy ndimage.rotate, "
              f"order {order}); {amount(empty, 'cell')} came from outside the old grid and "
              f"{'is' if empty == 1 else 'are'} empty.")
        return self._change(f"rotate by {say(by_degrees)} degrees", out)

    def _square(self, step: str):
        rows, columns = self._values.shape
        if rows != columns:
            raise SimplydataError(f"{step}() needs a square grid (as many rows as columns); this one has "
                                  f"{amount(rows, 'row')} and {amount(columns, 'column')}.")
        values = np.asarray(self._values, dtype=float)
        _no_empty(values, step)
        return values

    @friendly
    def take_matrix_exp(self: _Same) -> _Same:
        """The matrix exponential of a square grid (as used for rates of change between states). grid.take_matrix_exp()

        Not e to the power of each number (that is take_exp): the sum 1 + A + A**2/2! + A**3/3! + ... with
        matrix products, as SciPy linalg.expm (Pade approximation, Al-Mohy and Higham), R Matrix::expm.
        Undo with grid.undo().
        """
        from scipy import linalg

        values = self._square("take_matrix_exp")
        out = linalg.expm(values)
        print(f"The matrix exponential of the {values.shape[0]} x {values.shape[0]} grid (SciPy linalg.expm; not e to "
              "the power of each number, which is take_exp).")
        return self._change("matrix exp", out)

    @friendly
    def find_null_space(self, exactly=False):
        """The directions the grid turns into zeros (its null space), one in each column of a new grid. grid.find_null_space()

        Each column x of the answer gives the grid times x = 0, and the columns are at right angles and of length
        1. No column means only zero goes to zero. SciPy linalg.null_space (from the singular value
        decomposition). exactly=True gives SymPy's exact directions (nullspace, the numbers as fractions): simple
        whole numbers and fractions, such as [-2, 1], which are not of length 1 and need not be at right angles
        (numbers phase, batch 4).
        """
        from scipy import linalg

        from .numbers import NumberGrid

        if not isinstance(exactly, bool):
            raise SimplydataError("exactly= should be True or False.")
        values = np.asarray(self._values, dtype=float)
        _no_empty(values, "find_null_space")
        if exactly:
            from .._formula import MAX_EXACT_GRID, exact_matrix, run_exactly

            matrix = exact_matrix(values, "find_null_space", MAX_EXACT_GRID)
            vectors = run_exactly(matrix.nullspace, what="SymPy nullspace")
            if not vectors:
                print("The null space is empty: only zero is sent to zero (SymPy nullspace, exact). The new grid has "
                      "no columns.")
                return NumberGrid(np.zeros((values.shape[1], 0)))
            said = "; ".join("[" + ", ".join(str(v) for v in vector) + "]" for vector in vectors)
            print(f"The null space has {amount(len(vectors), 'direction')}, exactly: {said}   (SymPy nullspace, exact). "
                  "These are SymPy's simplest whole-number directions, not of length 1 as without exactly=True.")
            return NumberGrid(np.array([[float(v) for v in vector] for vector in vectors], dtype=float).T)
        out = linalg.null_space(values)
        if out.shape[1]:
            print(f"The null space has {amount(out.shape[1], 'direction')}: each column of the new grid is sent to 0 "
                  "(SciPy linalg.null_space).")
        else:
            print("The null space is empty: only zero is sent to zero (SciPy linalg.null_space). The new grid has "
                  "no columns.")
        return NumberGrid(out)

