"""Families for 100 %, batch 10 (approved by Manish 2026-11-28, plan section 2.4): NumPy words for lists of numbers.

find_product (NumPy nanprod), turn_into_changes (diff), turn_into_slopes (gradient), count_in_bins (histogram,
histogram_bin_edges, histogram2d), find_bin_of_each (digitize), the set words keep_numbers_also_in (intersect1d),
remove_numbers_also_in (setdiff1d), keep_numbers_in_only_one (setxor1d) and join_numbers_with (union1d),
find_dot_product_with (dot), find_cross_product_with (cross), find_positions_where (flatnonzero, argwhere) and
find_size (linalg.vector_norm / matrix_norm). The new options of existing words (show="product" of
turn_into_running_total, show="positions" and then_by= of sort, show= of remove_duplicate_numbers, spacing="log" of
sdata.number_list, remove_jumps= of change_angles_to) call the helpers below. Every calculation is one NumPy call,
named in the sentence the word prints; positions count from 1, as everywhere in simplydata.
"""

from __future__ import annotations

import numbers as _nb

import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from .._typing import _Same
from ._base import NOT_GIVEN, amount, is_number, say, to_array

# bins_include= of find_bin_of_each: which edge belongs to a bin -> NumPy digitize(right=)
BIN_EDGES = {"left edge": False, "right edge": True}
# edges= by a rule name -> NumPy histogram_bin_edges(bins=)
EDGE_RULES = {"auto": "auto", "freedman-diaconis": "fd", "doane": "doane", "scott": "scott", "stone": "stone",
              "rice": "rice", "sturges": "sturges", "square root": "sqrt", "fd": "fd", "sqrt": "sqrt"}
# find_size(kind=) on numbers -> NumPy linalg.vector_norm(ord=)
VECTOR_SIZES = {"length": 2, "total size": 1, "biggest size": np.inf, "smallest size": -np.inf,
                "count not zero": 0}
# find_size(kind=) on a grid -> NumPy linalg.matrix_norm(ord=)
GRID_SIZES = {"frobenius": "fro", "biggest column total": 1, "biggest row total": np.inf, "biggest stretch": 2,
              "nuclear": "nuc", "smallest column total": -1, "smallest row total": -np.inf, "smallest stretch": -2}
DUPLICATE_SHOWS = ("positions", "which number")
SORT_SHOWS = ("numbers", "positions")
RUNNING_SHOWS = ("total", "product")


def _other(other, step: str, example: str) -> np.ndarray:
    """The other numbers of a word that takes two lists, as one NumPy list."""
    if other is None:
        raise SimplydataError(f"{step}() needs other numbers.\nFor example:  {example}")
    values = to_array(other, f"{step}()", example)
    return values.ravel() if values.ndim != 1 else values


def _filled(values: np.ndarray) -> tuple[np.ndarray, int]:
    """The numbers without the empty ones, and how many were empty."""
    if values.dtype.kind != "f":
        return values, 0
    empty = np.isnan(values)
    return values[~empty], int(empty.sum())


def _note_left_out(n: int, step: str) -> None:
    if n:
        print(f"Note: {amount(n, 'empty value')} {'was' if n == 1 else 'were'} left out ({step} works on numbers).")


def _show_numbers(values, most: int = 8) -> str:
    shown = ", ".join(say(v) if float(v).is_integer() else f"{float(v):.6g}" for v in np.asarray(values).ravel()[:most])
    return shown + (" ..." if np.size(values) > most else "")


def running_product(values: np.ndarray) -> tuple[np.ndarray, str]:
    """turn_into_running_total(show="product"): NumPy nancumprod for decimals, with the empty values left empty again
    (as the running total leaves them). Whole numbers are multiplied as Python's whole numbers (NumPy
    multiply.accumulate on objects), so they never wrap round; products too big for a whole number of 64 bits come
    back as decimals, with a note."""
    if values.dtype.kind == "f":
        out = np.nancumprod(values)
        return np.where(np.isnan(values), np.nan, out), "NumPy nancumprod"
    exact = np.multiply.accumulate(values.astype(object)) if values.size else values
    if values.size and max(abs(int(v)) for v in exact) >= 2 ** 63:
        return exact.astype(float), ("NumPy multiply.accumulate on Python's whole numbers; the products are too big "
                                     "for whole numbers of 64 bits, so they are given as decimals")
    return np.asarray(exact, dtype=np.int64), "NumPy multiply.accumulate on Python's whole numbers, so none wraps round"


def sort_positions(values: np.ndarray, biggest_first: bool, then_by=None) -> np.ndarray:
    """sort(show="positions"): NumPy argsort (stable) or lexsort with then_by=, empty values last; from 1."""
    key = values.astype(float)
    empty = np.isnan(key)
    if then_by is None:
        filled = np.flatnonzero(~empty)
        order = filled[np.argsort(-key[filled] if biggest_first else key[filled], kind="stable")]
    else:
        second = then_by.astype(float)
        filled = np.flatnonzero(~empty)
        main = -key[filled] if biggest_first else key[filled]
        sub = -second[filled] if biggest_first else second[filled]
        order = filled[np.lexsort((sub, main))]
    return np.concatenate([order, np.flatnonzero(empty)])


def log_spaced(start, to, how_many) -> np.ndarray:
    """number_list(..., spacing="log"): NumPy geomspace, each number the same times bigger than the one before."""
    if not how_many:
        raise SimplydataError('spacing="log" needs how_many=, such as sdata.number_list(1, to=1000, how_many=4, '
                              'spacing="log").')
    if start == 0 or to == 0 or (start < 0) != (to < 0):
        raise SimplydataError('spacing="log" needs a start and an end of the same sign, neither of them 0 (each number '
                              "is the one before times the same factor).")
    return np.geomspace(start, to, int(how_many))


class NumPyListWords:
    """The NumPy words of plan section 2.4 on a list of numbers."""

    @friendly
    def find_product(self):
        """The product of the numbers: all of them multiplied together. product = numbers.find_product()

        Empty values are left out, as in find_total (NumPy nanprod). Whole numbers give a whole number that never
        wraps round, however big (NumPy prod with Python's whole numbers); decimals give a decimal. Nothing changes.
        """
        values, empty = _filled(np.asarray(self._values).ravel())
        if values.dtype.kind in "iu":
            found = int(np.prod(values.astype(object))) if values.size else 1
        else:
            found = float(np.nanprod(values))
        print(f"The product of {amount(values.size)}: {say(found)}   (NumPy prod"
              + (f"; {amount(empty, 'empty value')} left out)" if empty else ")"))
        return found

    @friendly
    def turn_into_changes(self: _Same, rows_back=1, how_many_times=1) -> _Same:
        """Each number becomes its change from the number before: 3, 5, 9 becomes 2, 4. numbers.turn_into_changes()

        The list gets one number shorter (NumPy diff, as R diff(x)). rows_back=12 takes the change from 12 numbers
        before (a change from the same month last year; R diff(x, lag = 12)); how_many_times=2 takes the changes of
        the changes (R diff(x, differences = 2)). An empty value gives empty changes next to it. Undo with
        numbers.undo().
        """
        for option, value in (("rows_back", rows_back), ("how_many_times", how_many_times)):
            if isinstance(value, bool) or not isinstance(value, _nb.Integral) or value < 1:
                raise SimplydataError(f"{option}= needs a whole number from 1 up, such as {option}=1."
                                      + self._example("turn_into_changes(rows_back=1)"))
        values = np.asarray(self._values)
        if values.size <= rows_back * how_many_times:
            raise SimplydataError(f"turn_into_changes() needs more than {rows_back * how_many_times} numbers for "
                                  f"rows_back={rows_back} and how_many_times={how_many_times}; there are "
                                  f"{values.size}.")
        if rows_back == 1:
            out = np.diff(values, n=int(how_many_times))
            how = "NumPy diff"
        else:
            import pandas as pd

            out = pd.Series(values)
            for _ in range(int(how_many_times)):
                out = out.diff(periods=int(rows_back)).iloc[int(rows_back):]
            out = out.to_numpy()
            if values.dtype.kind in "iu" and not np.isnan(out).any():
                out = out.astype(np.int64)
            how = f"pandas Series.diff(periods={rows_back}), as R diff(x, lag = {rows_back})"
        print(f"{amount(out.size)} left: the change{'s of the changes' if how_many_times > 1 else ''} from "
              f"{'the number before' if rows_back == 1 else f'{rows_back} numbers before'} ({how}"
              + (f", n={how_many_times})" if how_many_times > 1 else ")"))
        return self._change("changes" if how_many_times == 1 else f"changes, {how_many_times} times", out)

    @friendly
    def turn_into_slopes(self: _Same, time_step=None, at_times=None) -> _Same:
        """Each number becomes the slope at that point (how fast they change). numbers.turn_into_slopes(time_step=0.5)

        Central differences inside and one-sided ones at the two ends, so the list keeps its length (NumPy
        gradient). time_step= is the time between the numbers (1 when not given, or the numbers' own time step);
        at_times= gives the time of each number when they are not evenly spaced. Undo with numbers.undo().
        """
        values = np.asarray(self._values, dtype=float)
        if values.size < 2:
            raise SimplydataError("turn_into_slopes() needs at least 2 numbers.")
        if time_step is not None and at_times is not None:
            raise SimplydataError("Give time_step= (evenly spaced) or at_times= (the time of each number), not both.")
        if at_times is not None:
            times = to_array(at_times, "at_times=", "numbers.turn_into_slopes(at_times=[0, 1, 3, 7])").ravel()
            if times.size != values.size:
                raise SimplydataError(f"at_times= needs one time for each number ({values.size}); it has {times.size}.")
            out = np.gradient(values, times.astype(float))
            said = "at the times given"
        else:
            step = time_step if time_step is not None else (getattr(self, "_time_step", None) or 1)
            if not is_number(step) or step <= 0:
                raise SimplydataError("time_step= needs a number above 0, such as time_step=0.5."
                                      + self._example("turn_into_slopes(time_step=0.5)"))
            out = np.gradient(values, float(step))
            said = f"with a time step of {say(step)}"
        print(f"The slope at each of the {values.size} numbers, {said} (NumPy gradient: central differences, one-sided "
              "at the ends).")
        return self._change("slopes", out)

    @friendly
    def count_in_bins(self, edges=None, how_many_bins=None, between=None, together_with=None, other_edges=None):
        """How many numbers fall in each bin. counts = numbers.count_in_bins(edges=[0, 10, 20, 50])

        Each bin holds its left edge, and the last bin its right edge too (NumPy histogram, as R hist(x, right =
        FALSE, include.lowest = TRUE)). Give edges= (a list of edges, or a rule: "auto", "sturges",
        "freedman-diaconis", "scott", "doane", "rice", "square root", "stone"; NumPy histogram_bin_edges), or
        how_many_bins= (10 when nothing is given) with between=[low, high]. together_with= other numbers (one for
        each) counts the pairs in a grid of bins: rows for these numbers, columns for the other ones (NumPy
        histogram2d; other_edges= their bins). Empty values are left out. Nothing changes.
        """
        import pandas as pd

        from ..table import Table

        if together_with is not None:
            other = _other(together_with, "count_in_bins", "numbers.count_in_bins(edges=5, together_with=other)")
            mine = np.asarray(self._values, dtype=float).ravel()
            if other.size != mine.size:
                raise SimplydataError(f"together_with= needs one number for each of yours ({mine.size}); it has "
                                      f"{other.size}.")
            keep = ~np.isnan(mine) & ~np.isnan(other.astype(float))
            if (~keep).any():
                print(f"Note: {amount(int((~keep).sum()), 'pair')} with an empty value "
                      f"{'was' if (~keep).sum() == 1 else 'were'} left out (count_in_bins counts pairs of numbers).")
            bins, _ = self._bins(mine[keep], edges, how_many_bins, between, "count_in_bins")
            other_bins, _ = self._bins(other.astype(float)[keep], other_edges, None, None, "count_in_bins")
            counts, row_edges, column_edges = np.histogram2d(mine[keep], other.astype(float)[keep],
                                                             bins=[bins, other_bins])
            print(f"Counted {int(counts.sum())} of {int(keep.sum())} pairs in {counts.shape[0]} x {counts.shape[1]} "
                  f"bins (NumPy histogram2d): row edges {_show_numbers(row_edges)}; column edges "
                  f"{_show_numbers(column_edges)}.")
            return self._wrap(counts.astype(np.int64))
        if other_edges is not None:
            raise SimplydataError("other_edges= goes with together_with=, the bins of the other numbers.")
        values, empty = _filled(np.asarray(self._values, dtype=float).ravel())
        bins, said = self._bins(values, edges, how_many_bins, between, "count_in_bins")
        counts, found = np.histogram(values, bins=bins)
        _note_left_out(empty, "count_in_bins")
        inside = int(counts.sum())
        outside = values.size - inside
        print(f"{amount(inside)} counted in {counts.size} bins {said}"
              + (f"; {amount(outside)} outside the edges {'was' if outside == 1 else 'were'} not counted"
                 if outside else "")
              + "; each bin holds its left edge, the last one its right edge too (NumPy histogram).")
        return Table(pd.DataFrame({"from": found[:-1], "to": found[1:], "count": counts.astype(np.int64)}))

    def _bins(self, values, edges, how_many_bins, between, step):
        """The bins= of NumPy histogram from edges=, how_many_bins= and between=, and the words for them."""
        if edges is not None and (how_many_bins is not None or between is not None):
            raise SimplydataError(f"{step}() takes edges=, or how_many_bins= with between=, not both.")
        if isinstance(edges, str):
            rule = edges.strip().lower()
            if rule not in EDGE_RULES:
                raise choice_error(step, "edges", edges, [r for r in EDGE_RULES if r not in ("fd", "sqrt")])
            found = np.histogram_bin_edges(values, bins=EDGE_RULES[rule])
            return found, f'(edges by the "{rule}" rule, NumPy histogram_bin_edges)'
        if edges is not None:
            if is_number(edges) and not isinstance(edges, bool) and float(edges).is_integer() and edges >= 1:
                return int(edges), f"({int(edges)} equal bins)"
            found = to_array(edges, "edges=", "numbers.count_in_bins(edges=[0, 10, 20, 50])").ravel().astype(float)
            if found.size < 2 or np.any(np.diff(found) <= 0):
                raise SimplydataError("edges= needs at least 2 edges, each bigger than the one before, such as "
                                      "edges=[0, 10, 20, 50].")
            return found, f"with the edges {_show_numbers(found)}"
        n = 10 if how_many_bins is None else how_many_bins
        if isinstance(n, bool) or not isinstance(n, _nb.Integral) or n < 1:
            raise SimplydataError("how_many_bins= needs a whole number from 1 up, such as how_many_bins=10.")
        if between is not None:
            low, high = _pair(between, step)
            return np.linspace(low, high, int(n) + 1), f"({n} equal bins from {say(low)} to {say(high)})"
        return int(n), f"({n} equal bins from the smallest to the biggest number)"

    @friendly
    def find_bin_of_each(self, edges=None, bins_include="left edge"):
        """For each number, the bin it falls in, counting from 1. bins = numbers.find_bin_of_each(edges=[0, 10, 20, 50])

        Bin 1 is from the first edge to the second, and so on (NumPy digitize, as R findInterval). bins_include="left
        edge" puts a number on an edge in the bin that starts there; "right edge" in the bin that ends there. The
        outer edge on the other side belongs to the bin next to it, as in count_in_bins (R findInterval with
        rightmost.closed = TRUE). Numbers outside the edges, and empty ones, get an empty bin. Gives new numbers;
        these stay as they are.
        """
        if edges is None:
            raise SimplydataError("find_bin_of_each() needs edges=, such as edges=[0, 10, 20, 50].")
        if bins_include not in BIN_EDGES:
            raise choice_error("find_bin_of_each", "bins_include", bins_include, list(BIN_EDGES))
        found = to_array(edges, "edges=", "numbers.find_bin_of_each(edges=[0, 10, 20, 50])").ravel().astype(float)
        if found.size < 2 or np.any(np.diff(found) <= 0):
            raise SimplydataError("edges= needs at least 2 edges, each bigger than the one before.")
        values = np.asarray(self._values, dtype=float).ravel()
        index = np.digitize(values, found, right=BIN_EDGES[bins_include])
        if BIN_EDGES[bins_include]:  # the first edge closes the first bin
            index = np.where(values == found[0], 1, index)
        else:  # the last edge closes the last bin, as count_in_bins (NumPy histogram) does
            index = np.where(values == found[-1], found.size - 1, index)
        outside = (index == 0) | (index == found.size) | np.isnan(values)
        out = np.where(outside, np.nan, index.astype(float))
        n_out = int(np.count_nonzero(outside & ~np.isnan(values)))
        print(f"The bin of each of the {values.size} numbers among {found.size - 1} bins, counting from 1 (NumPy "
              f"digitize, right={BIN_EDGES[bins_include]}, with the outer edge in the bin next to it)"
              + (f"; {amount(n_out)} outside the edges {'has' if n_out == 1 else 'have'} an empty bin." if n_out
                 else "."))
        return self._wrap(out if np.isnan(out).any() else out.astype(np.int64))

    # ------------------------------------------------------------------ sets of numbers
    def _set_step(self, other, step, func, what, example):
        mine, empty = _filled(np.asarray(self._values).ravel())
        theirs, their_empty = _filled(_other(other, step, example))
        out = func(mine, theirs)
        _note_left_out(empty + their_empty, step)
        print(f"{amount(out.size)} {what}, each once, smallest first (NumPy {func.__name__}): {_show_numbers(out)}")
        return self._change(step.replace("_", " "), out)

    @friendly
    def keep_numbers_also_in(self: _Same, other=None) -> _Same:
        """Keep the numbers that are in the other numbers too, each once. numbers.keep_numbers_also_in(other_numbers)

        The numbers in both lists, smallest first (NumPy intersect1d, as R intersect then sort). Empty values are left
        out. Undo with numbers.undo().
        """
        return self._set_step(other, "keep_numbers_also_in", np.intersect1d, "in both lists",
                              "numbers.keep_numbers_also_in(other_numbers)")

    @friendly
    def remove_numbers_also_in(self: _Same, other=None) -> _Same:
        """Remove the numbers the other list has too; each left once. numbers.remove_numbers_also_in(other_numbers)

        The numbers of this list that the other list does not have, smallest first (NumPy setdiff1d, as R setdiff
        then sort). Undo with numbers.undo().
        """
        return self._set_step(other, "remove_numbers_also_in", np.setdiff1d, "not in the other list",
                              "numbers.remove_numbers_also_in(other_numbers)")

    @friendly
    def keep_numbers_in_only_one(self: _Same, other=None) -> _Same:
        """Keep the numbers in only one of the two lists, each once. numbers.keep_numbers_in_only_one(other_numbers)

        The numbers in this list or the other but not in both, smallest first (NumPy setxor1d). Undo with
        numbers.undo().
        """
        return self._set_step(other, "keep_numbers_in_only_one", np.setxor1d, "in only one of the lists",
                              "numbers.keep_numbers_in_only_one(other_numbers)")

    @friendly
    def join_numbers_with(self: _Same, other=None) -> _Same:
        """Every different number of both lists, each once, smallest first. numbers.join_numbers_with(other_numbers)

        NumPy union1d, as R union then sort. Undo with numbers.undo().
        """
        return self._set_step(other, "join_numbers_with", np.union1d, "in either list",
                              "numbers.join_numbers_with(other_numbers)")

    # ------------------------------------------------------------------ two lists as vectors
    @friendly
    def find_dot_product_with(self, other=None):
        """The dot product: the total of the products. answer = numbers.find_dot_product_with(other_numbers)

        [1, 2, 3] with [4, 5, 6] gives 1*4 + 2*5 + 3*6 = 32 (NumPy dot, as R sum(x * y) or crossprod). Both lists need
        the same length and no empty values. Nothing changes.
        """
        example = "numbers.find_dot_product_with(other_numbers)"
        mine = np.asarray(self._values).ravel()
        theirs = _other(other, "find_dot_product_with", example)
        if mine.size != theirs.size:
            raise SimplydataError(f"find_dot_product_with() needs two lists of the same length; these have "
                                  f"{mine.size} and {theirs.size} numbers.")
        if np.isnan(mine.astype(float)).any() or np.isnan(theirs.astype(float)).any():
            raise SimplydataError("find_dot_product_with() needs no empty values; fill or remove them first.")
        found = np.dot(mine, theirs)
        print(f"The dot product of the two lists of {mine.size} numbers: {say(found)}   (NumPy dot)")
        return found.item()

    @friendly
    def find_cross_product_with(self, other=None):
        """The cross product, for 3 numbers each. answer = numbers.find_cross_product_with(other_numbers)

        [1, 0, 0] with [0, 1, 0] gives [0, 0, 1]: the direction at right angles to both (NumPy cross, as R
        pracma::cross). Gives new numbers; these stay as they are. Two numbers each (directions on a flat page)
        give the one number of the turn between them.
        """
        example = "numbers.find_cross_product_with(other_numbers)"
        mine = np.asarray(self._values).ravel()
        theirs = _other(other, "find_cross_product_with", example)
        if mine.size != theirs.size or mine.size not in (2, 3):
            raise SimplydataError("find_cross_product_with() needs 3 numbers in each list (or 2 in each); these have "
                                  f"{mine.size} and {theirs.size}.")
        if mine.size == 2:
            # NumPy 2 refuses 2-number lists in np.cross: each gets a third number 0, and the z part is the answer
            found = np.cross(np.append(mine, 0), np.append(theirs, 0))[2]
            print(f"The cross product of two directions on a flat page: {say(found)}   (the z part of NumPy cross, "
                  "with 0 as the third number)")
            return found.item()
        found = np.cross(mine, theirs)
        print(f"The cross product: {_show_numbers(found)}   (NumPy cross: at right angles to both)")
        return self._wrap(found)



class NumPySharedWords:
    """The NumPy words of plan section 2.4 that numbers and grids share: positions and size."""

    @friendly
    def find_positions_where(self, *extra, is_above=NOT_GIVEN, is_below=NOT_GIVEN, is_at_least=NOT_GIVEN,
                             is_at_most=NOT_GIVEN, is_equal_to=NOT_GIVEN, is_not_equal_to=NOT_GIVEN,
                             is_between=NOT_GIVEN, is_one_of=NOT_GIVEN, is_empty=NOT_GIVEN, show="positions"):
        """The positions of the numbers that pass a test, from 1. positions = numbers.find_positions_where(is_above=30)

        The same tests as count_numbers_that (is_above=, is_between=, is_one_of= ...; on yes or no values, the yes).
        On numbers it gives the positions (NumPy flatnonzero, plus 1). On a grid, grid.find_positions_where(is_above=4)
        gives a table with a row and a column for each (NumPy argwhere, plus 1), ready for
        grid.replace_numbers_where(at_positions=...); show="position in list" gives each one's position in the
        grid's numbers read row by row instead (NumPy flatnonzero). Nothing changes.
        """
        import pandas as pd

        from ..table import Table

        if extra:
            raise SimplydataError("find_positions_where() needs one condition, like is_above=30."
                                  + self._example("find_positions_where(is_above=30)"))
        given = dict(is_above=is_above, is_below=is_below, is_at_least=is_at_least, is_at_most=is_at_most,
                     is_equal_to=is_equal_to, is_not_equal_to=is_not_equal_to, is_between=is_between,
                     is_one_of=is_one_of, is_empty=is_empty)
        if show not in ("positions", "position in list"):
            raise choice_error("find_positions_where", "show", show, ["positions", "position in list"])
        cond, words = self._condition_from("find_positions_where", given)
        if cond.ndim == 1 or show == "position in list":
            found = np.flatnonzero(cond) + 1
            print(f"{amount(found.size, 'number')} {words.replace('are ', 'is ', 1) if found.size == 1 else words}, "
                  f"at the positions {_show_numbers(found)} (NumPy flatnonzero, plus 1: positions count from 1)")
            from .numbers import Numbers

            return Numbers(found.astype(np.int64))
        found = np.argwhere(cond) + 1
        print(f"{amount(len(found), 'number')} {words.replace('are ', 'is ', 1) if len(found) == 1 else words}; "
              "their row and column (NumPy argwhere, plus 1: rows and columns count from 1)")
        return Table(pd.DataFrame({"row": found[:, 0].astype(np.int64), "column": found[:, 1].astype(np.int64)}))

    @friendly
    def find_size(self, kind=None):
        """The size of the numbers as one number (a norm). size = numbers.find_size()

        Numbers: kind="length" (the square root of the sum of squares, NumPy linalg.vector_norm, as R norm(x, "2")),
        "total size" (the total of the sizes), "biggest size", "smallest size", "count not zero", or a number p (the
        p-norm). A grid: kind="frobenius" (the same, over every number; NumPy linalg.matrix_norm), "biggest column
        total", "biggest row total", "biggest stretch" (the biggest singular value), "nuclear" (the total of the
        singular values), and "smallest ..." for the smallest: grid.find_size(kind="biggest stretch"). Nothing
        changes.
        """
        values = np.asarray(self._values, dtype=float)
        if np.isnan(values).any():
            raise SimplydataError("find_size() needs no empty values; fill or remove them first.")
        if values.ndim == 1:
            kind = "length" if kind is None else kind
            if is_number(kind) and not isinstance(kind, bool):
                order, said = float(kind), f"the {say(kind)}-norm"
            elif kind in VECTOR_SIZES:
                order, said = VECTOR_SIZES[kind], f"the {kind}"
            else:
                raise choice_error("find_size", "kind", kind, list(VECTOR_SIZES))
            found = float(np.linalg.vector_norm(values, ord=order))
            print(f"The size of the {amount(values.size)}, {said}: {found:.10g}   (NumPy linalg.vector_norm, "
                  f"ord={order!r})")
            return found
        kind = "frobenius" if kind is None else kind
        if kind not in GRID_SIZES:
            raise choice_error("find_size", "kind", kind, list(GRID_SIZES))
        found = float(np.linalg.matrix_norm(values, ord=GRID_SIZES[kind]))
        print(f"The size of the grid, the {kind}: {found:.10g}   (NumPy linalg.matrix_norm, ord={GRID_SIZES[kind]!r})")
        return found


def _pair(between, step):
    if (not isinstance(between, (list, tuple)) or len(between) != 2 or not all(is_number(v) for v in between)
            or between[0] >= between[1]):
        raise SimplydataError(f"between= needs two numbers, the low one first, such as between=[0, 100] ({step}).")
    return float(between[0]), float(between[1])
