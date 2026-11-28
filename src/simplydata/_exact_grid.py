"""Exact grids (families for 100 %, batch 26, plan section 2.10, approved by Manish 2026-11-28): sdata.number_grid(
..., exactly=True) keeps every cell exact (fractions, square roots, pi) and may hold letters ("a", "x**2"), as a SymPy
Matrix; and the grid words find_permanent and make_columns_orthogonal (on a grid of numbers and on an exact grid).

Every answer comes from SymPy's Matrix, each call under simplydata's one time limit (_time_limit.py): det,
inv, eigenvals, nullspace, LUsolve, transpose, per (the permanent), GramSchmidt, subs and evalf. Own code is glue
only: reading the cells and writing SymPy's answers back.
"""

from __future__ import annotations

import math

import numpy as np

from ._errors import SimplydataError, friendly
from ._time_limit import one_deadline

EXACT_WORDS = ("count_rows", "count_columns", "find_shape", "swap_rows_and_columns", "find_determinant",
               "take_inverse", "find_eigenvalues", "find_null_space", "solve_for", "find_permanent",
               "make_columns_orthogonal", "find_value_at", "show_as_latex", "as_sympy", "undo")
MAX_EXACT_CELLS = 12  # rows and columns of an exact grid (as MAX_EXACT_GRID for exactly=True on a grid)


def _cell(sp, value, row: int, column: int):
    """One cell of an exact grid: a number (as the exact fraction it stands for), or formula text."""
    from ._formula import Formula, exact_number, parse

    if isinstance(value, Formula):
        return value._expr
    if isinstance(value, str):
        return parse(value, f"sdata.number_grid(exactly=True), row {row}, column {column}")
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)) or not math.isfinite(
            float(value)):
        raise SimplydataError(f"sdata.number_grid(exactly=True) takes numbers and formula text in quotes; row {row}, "
                              f"column {column} is {value!r}.")
    return exact_number(sp, value)


def exact_grid(values):
    """sdata.number_grid(values, exactly=True): the rows as a SymPy Matrix of exact cells."""
    from ._formula import need_sympy

    sp = need_sympy("sdata.number_grid(exactly=True)")
    example = 'sdata.number_grid([[1, "1/3"], ["a", 2]], exactly=True)'
    if hasattr(values, "_values") and getattr(values, "_values").ndim == 2:
        values = values._values.tolist()
    if not isinstance(values, (list, tuple)) or not values or not all(isinstance(r, (list, tuple)) and r
                                                                      for r in values):
        raise SimplydataError(f"sdata.number_grid(exactly=True) needs rows of numbers or formula text.\n"
                              f"For example:  {example}")
    width = len(values[0])
    if any(len(r) != width for r in values):
        raise SimplydataError("Every row of the grid needs the same number of cells.")
    if max(len(values), width) > MAX_EXACT_CELLS:
        raise SimplydataError(f"An exact grid has up to {MAX_EXACT_CELLS} rows and {MAX_EXACT_CELLS} columns; this one "
                              f"is {len(values)} x {width}. Leave out exactly=True for a grid of decimals.")
    matrix = sp.Matrix([[_cell(sp, v, i + 1, j + 1) for j, v in enumerate(r)] for i, r in enumerate(values)])
    return ExactGrid(matrix)


def _rows_text(matrix) -> list[str]:
    from ._formula import _show

    return ["[" + ", ".join(_show(v) for v in matrix.row(i)) + "]" for i in range(matrix.rows)]


def _run(call, *values, what: str, **named):
    from ._formula import run_exactly

    return run_exactly(call, *values, what=what, **named)


class ExactGrid:
    """A grid whose cells are exact (fractions, square roots, pi) or formulas with letters, as a SymPy Matrix. Make
    one with sdata.number_grid([[1, "1/3"], ["a", 2]], exactly=True).

    Words: count_rows, count_columns, find_shape, swap_rows_and_columns, find_determinant, take_inverse,
    find_eigenvalues, find_null_space, solve_for, find_permanent, make_columns_orthogonal, find_value_at,
    show_as_latex, as_sympy, undo. They work as on a grid of numbers, and every answer is exact.
    """

    def __init__(self, matrix):
        object.__setattr__(self, "_matrix", matrix)
        object.__setattr__(self, "_history", [])

    def __setattr__(self, name, value):
        raise SimplydataError("An exact grid is changed with its words, such as grid.take_inverse(); grid.undo() takes "
                              "a step back.")

    def __dir__(self):
        return list(EXACT_WORDS)

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        from ._errors import MissingWordError

        raise MissingWordError(f"An exact grid has no word called .{name}(). Its words: {', '.join(EXACT_WORDS)}. "
                               "For the other grid words, give the letters numbers first: "
                               "grid.find_value_at(a=2) gives a grid of decimals.")

    def __repr__(self):
        rows, columns = self._matrix.shape
        return (f"simplydata exact grid: {rows} rows, {columns} columns\n" + "\n".join(_rows_text(self._matrix)))

    def _repr_latex_(self):
        import sympy as sp

        return f"$\\displaystyle {sp.latex(self._matrix)}$"

    def _change(self, what: str, new):
        self._history.append((what, self._matrix))
        object.__setattr__(self, "_matrix", new)
        return self

    def _square(self, step: str):
        rows, columns = self._matrix.shape
        if rows != columns:
            raise SimplydataError(f"grid.{step}() needs a square grid (as many rows as columns); this one is "
                                  f"{rows} x {columns}.")
        return rows

    # ------------------------------------------------------------------------------------------- looking
    @friendly
    def count_rows(self) -> int:
        """How many rows the exact grid has. grid.count_rows()"""
        return int(self._matrix.rows)

    @friendly
    def count_columns(self) -> int:
        """How many columns the exact grid has. grid.count_columns()"""
        return int(self._matrix.cols)

    @friendly
    def find_shape(self) -> tuple:
        """The rows and columns of the exact grid. grid.find_shape()"""
        return tuple(int(n) for n in self._matrix.shape)

    @friendly
    def as_sympy(self):
        """The SymPy Matrix underneath, to carry on in SymPy itself. matrix = grid.as_sympy()"""
        print(f"The SymPy Matrix underneath ({self._matrix.rows} x {self._matrix.cols}; carry on in SymPy with it)")
        return self._matrix.copy()

    @friendly
    def show_as_latex(self) -> str:
        """The exact grid as LaTeX, to paste into a paper; also gives the text back. grid.show_as_latex()"""
        from ._formula import need_sympy

        sp = need_sympy("grid.show_as_latex()")
        text = sp.latex(self._matrix)
        print(text)
        return text

    @friendly
    def undo(self):
        """Take back the last step that changed the exact grid. grid.undo()"""
        if not self._history:
            raise SimplydataError("There is no step to undo.")
        what, old = self._history.pop()
        object.__setattr__(self, "_matrix", old)
        print(f"Took back: {what}.")
        return self

    # ------------------------------------------------------------------------------------------- changing
    @friendly
    def swap_rows_and_columns(self):
        """Rows become columns (the transpose), exactly. grid.swap_rows_and_columns()"""
        new = _run(self._matrix.transpose, what="SymPy transpose")
        print(f"Rows and columns swapped: a {new.rows} x {new.cols} grid   (SymPy transpose)")
        return self._change("swap rows and columns", new)

    @friendly
    @one_deadline
    def take_inverse(self):
        """Turn a square exact grid into its inverse, exactly. grid.take_inverse()"""
        n = self._square("take_inverse")
        if _run(self._matrix.det, what="SymPy det") == 0:
            raise SimplydataError(f"The {n} x {n} grid has no inverse: its determinant is exactly 0 (SymPy det).")
        new = _run(self._matrix.inv, what="SymPy inv")
        print(f"The inverse of the {n} x {n} grid, exactly (SymPy inv):")
        for line in _rows_text(new):
            print("  " + line)
        return self._change("inverse", new)

    @friendly
    @one_deadline
    def make_columns_orthogonal(self, of_length_1=False):
        """Make the columns at right angles to each other (Gram-Schmidt), exactly. grid.make_columns_orthogonal()"""
        new = _gram_schmidt(self._matrix, of_length_1)
        return self._change("columns made orthogonal", new)

    # ------------------------------------------------------------------------------------------- answers
    @friendly
    def find_determinant(self):
        """The determinant of a square exact grid, as a formula. grid.find_determinant()"""
        from ._formula import Formula, _show

        n = self._square("find_determinant")
        found = _run(self._matrix.det, what="SymPy det")
        print(f"The determinant of the {n} x {n} grid, exactly: {_show(found)}   (SymPy det)")
        return Formula(found)

    @friendly
    def find_permanent(self):
        """The permanent of a square exact grid (the determinant with every sign +). grid.find_permanent()"""
        from ._formula import Formula, _show

        n = self._square("find_permanent")
        found = _run(self._matrix.per, what="SymPy per")
        print(f"The permanent of the {n} x {n} grid, exactly: {_show(found)}   (SymPy per)")
        return Formula(found)

    @friendly
    def find_eigenvalues(self, fast=False):
        """The eigenvalues of a square exact grid, with how many times each comes. grid.find_eigenvalues()"""
        from ._formula import _result_rows, _show
        from ._formula_algebra import _back

        n = self._square("find_eigenvalues")
        from ._formula import MAX_EXACT_EIGEN

        if n > MAX_EXACT_EIGEN:
            raise SimplydataError(f"Exact eigenvalues work on grids up to {MAX_EXACT_EIGEN} x {MAX_EXACT_EIGEN}.")
        found = _run(self._matrix.eigenvals, what="SymPy eigenvals")
        rows = []
        for value, times in found.items():
            back = _back(__import__("sympy"), value)
            rows.append({"eigenvalue": back if isinstance(back, float) else math.nan,
                         "eigenvalue exactly": _show(value), "times": int(times)})
        print(f"The eigenvalues of the {n} x {n} grid: " + ", ".join(r["eigenvalue exactly"] for r in rows)
              + "   (SymPy eigenvals)")
        return _result_rows(rows, fast)

    @friendly
    def find_null_space(self):
        """The directions the exact grid turns into 0, each as an exact column. directions = grid.find_null_space()"""
        found = _run(self._matrix.nullspace, what="SymPy nullspace")
        print(f"The null space has {len(found)} direction{'s' if len(found) != 1 else ''}, exactly: "
              + ("; ".join(_rows_text(v.T)[0] for v in found) or "none") + "   (SymPy nullspace)")
        return [ExactGrid(v) for v in found]

    @friendly
    def solve_for(self, right_side=None):
        """The x with grid times x = right_side, exactly. x = grid.solve_for([5, 10])"""
        from ._formula import need_sympy

        sp = need_sympy("grid.solve_for()")
        n = self._square("solve_for")
        if not isinstance(right_side, (list, tuple)) or len(right_side) != n:
            raise SimplydataError(f"grid.solve_for() needs the right side: a list of {n} numbers or formula texts, "
                                  "such as grid.solve_for([5, 10]).")
        b = sp.Matrix([_cell(sp, v, i + 1, 1) for i, v in enumerate(right_side)])
        if _run(self._matrix.det, what="SymPy det") == 0:
            raise SimplydataError(f"The {n} x {n} grid has determinant 0, so grid times x = right side has no single "
                                  "answer (SymPy det).")
        found = _run(self._matrix.LUsolve, b, what="SymPy LUsolve")
        print("x, exactly: " + _rows_text(found.T)[0] + "   (SymPy LUsolve)")
        return ExactGrid(found)

    @friendly
    def find_value_at(self, **values):
        """A grid of decimals, with a number in place of each letter. decimals = grid.find_value_at(a=2)"""
        from ._formula import exact_number, need_sympy
        from .numbers.numbers import NumberGrid

        sp = need_sympy("grid.find_value_at()")
        letters = {str(s): s for s in self._matrix.free_symbols}
        unknown = [k for k in values if k not in letters]
        if unknown or set(letters) - set(values):
            raise SimplydataError(f"grid.find_value_at() needs a number for each letter of the grid "
                                  f"({', '.join(sorted(letters)) or 'none'}), such as grid.find_value_at("
                                  + ", ".join(f"{n}=2" for n in sorted(letters)) + ").")
        swaps = {letters[k]: exact_number(sp, v) for k, v in values.items()}
        new = _run(self._matrix.subs, swaps, what="SymPy subs") if swaps else self._matrix
        decimals = _run(new.evalf, what="SymPy evalf")
        try:
            out = np.array(decimals.tolist(), dtype=float)
        except TypeError:
            raise SimplydataError("Some cells are not ordinary (real) numbers, so the grid has no decimals.") from None
        print(f"The grid with {', '.join(f'{k} = {v}' for k, v in values.items()) or 'no letters'}, in decimals.")
        return NumberGrid(out)


@one_deadline
def _gram_schmidt(matrix, of_length_1: bool):
    """SymPy GramSchmidt on the columns of a SymPy Matrix; the columns side by side again."""
    import sympy as sp

    if not isinstance(of_length_1, bool):
        raise SimplydataError("of_length_1= is True or False.")
    columns = [matrix.col(j) for j in range(matrix.cols)]
    if _run(matrix.rank, what="SymPy rank") < len(columns):
        raise SimplydataError("The columns of the grid depend on each other (its rank is less than its number of "
                              "columns), so they cannot all be made orthogonal (SymPy rank).")
    found = _run(sp.GramSchmidt, columns, of_length_1, what="SymPy GramSchmidt")
    new = sp.Matrix.hstack(*found)
    print(f"The columns made orthogonal{' and of length 1' if of_length_1 else ''} (Gram-Schmidt, SymPy "
          "GramSchmidt):")
    for line in _rows_text(new):
        print("  " + line)
    return new


class GridWords26:
    """Batch 26 words of a grid of numbers: the permanent and orthogonal columns, from SymPy."""

    @friendly
    def find_permanent(self, exactly=False):
        """The permanent of a square grid: the determinant with every sign +. grid.find_permanent()

        sdata.number_grid([[1, 2], [3, 4]]).find_permanent() gives 10 (1*4 + 2*3; the determinant is 1*4 - 2*3). SymPy
        per on the numbers as exact fractions (SciPy and NumPy have no permanent), for grids up to 12 x 12; it counts
        the ways to pair rows with columns, such as the perfect matchings of a network. exactly=True gives the exact
        answer as a formula. Nothing changes in the grid. As SymPy per; R permanent::permanent.
        """
        from ._formula import EXACTLY_HINT, MAX_EXACT_GRID, Formula, _show, exact_matrix, float_of

        if not isinstance(exactly, bool):
            raise SimplydataError("exactly= should be True or False.")
        values = self._square("find_permanent")
        n = values.shape[0]
        matrix = exact_matrix(values, "find_permanent", MAX_EXACT_GRID)
        found = _run(matrix.per, what="SymPy per")
        if exactly:
            print(f"The permanent of the {n} x {n} grid, exactly: {_show(found)}   (SymPy per)")
            return Formula(found)
        about = float_of(found, "SymPy N", EXACTLY_HINT)
        print(f"The permanent of the {n} x {n} grid: {about:.10g}   (SymPy per, on the numbers as exact fractions)")
        return about

    @friendly
    def make_columns_orthogonal(self, of_length_1=False):
        """Make the columns of the grid at right angles to each other (Gram-Schmidt). grid.make_columns_orthogonal()

        sdata.number_grid([[1, 1], [1, 0]]).make_columns_orthogonal() turns the columns (1, 1) and (1, 0) into (1, 1)
        and (1/2, -1/2): each column has the parts along the columns before it taken away (Gram-Schmidt, SymPy
        GramSchmidt on the numbers as exact fractions). of_length_1=True also makes each column of length 1
        (orthonormal). The columns must not depend on each other. The exact columns are printed; the grid keeps
        their decimals. Undo with grid.undo(). As SymPy GramSchmidt; R pracma::gramSchmidt.
        """
        from ._formula import MAX_EXACT_GRID, exact_matrix

        matrix = exact_matrix(self._values, "make_columns_orthogonal", MAX_EXACT_GRID)
        new = _gram_schmidt(matrix, of_length_1)
        out = np.array(_run(new.evalf, what="SymPy evalf").tolist(), dtype=float)
        print("The grid now holds these columns as decimals.")
        return self._change("columns made orthogonal", out)
