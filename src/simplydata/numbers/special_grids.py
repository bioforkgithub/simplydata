"""Families for 100 %, batch 11 (approved by Manish 2026-11-28, plan section 2.4): special grids and coordinate grids.

sdata.number_grid(kind=...) makes the special grids of NumPy (eye, diag, tri, vander, block), scipy.linalg (toeplitz,
hankel, circulant, companion, hadamard, hilbert, invhilbert, pascal, invpascal, leslie, helmert, fiedler,
fiedler_companion, block_diag, convolution_matrix) and SymPy (rot_axis1-3, under simplydata's one time limit for
SymPy); sdata.number_grid(from_formula=...) fills a grid from a formula of row and column (NumPy fromfunction, rows and
columns from 1); sdata.make_coordinate_grids(x=, y=) gives the grids of x and y at every point (NumPy meshgrid), or
of the row and column numbers (NumPy indices, from 1). Own code is glue only.
"""

from __future__ import annotations

import numbers as _nb

import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from ._base import amount, is_number, say, to_array

# kind= -> (what it needs, the library call shown in the sentence)
KINDS = {
    "identity": ("size= (or rows= and columns=), shifted_by=", "NumPy eye"),
    "diagonal": ("the numbers of the diagonal, shifted_by=", "NumPy diag"),
    "ones below diagonal": ("rows=, columns=, shifted_by=", "NumPy tri"),
    "vandermonde": ("the numbers, columns=", "NumPy vander"),
    "blocks": ("of=[[first, second], [third, fourth]]", "NumPy block"),
    "block diagonal": ("of=[first, second]", "SciPy linalg.block_diag"),
    "toeplitz": ("first_column= (and first_row=)", "SciPy linalg.toeplitz"),
    "hankel": ("first_column= (and last_row=)", "SciPy linalg.hankel"),
    "circulant": ("first_column=", "SciPy linalg.circulant"),
    "companion": ("the polynomial's numbers, highest power first", "SciPy linalg.companion"),
    "fiedler companion": ("the polynomial's numbers, highest power first", "SciPy linalg.fiedler_companion"),
    "fiedler": ("the numbers", "SciPy linalg.fiedler"),
    "convolution": ("the numbers to convolve with, size=", "SciPy linalg.convolution_matrix"),
    "hadamard": ("size= (a power of 2)", "SciPy linalg.hadamard"),
    "hilbert": ("size=", "SciPy linalg.hilbert"),
    "inverse hilbert": ("size=", "SciPy linalg.invhilbert"),
    "pascal": ("size=", "SciPy linalg.pascal"),
    "lower pascal": ("size=", "SciPy linalg.pascal(kind=\"lower\")"),
    "upper pascal": ("size=", "SciPy linalg.pascal(kind=\"upper\")"),
    "inverse pascal": ("size=", "SciPy linalg.invpascal"),
    "leslie": ("first_row= (births), survival=", "SciPy linalg.leslie"),
    "helmert": ("size=", "SciPy linalg.helmert"),
    "rotation": ("axis= (\"x\", \"y\" or \"z\"), by_degrees=", "SymPy rot_axis1, rot_axis2, rot_axis3"),
}
AXES = {"x": 1, "y": 2, "z": 3}
EXAMPLE = 'sdata.number_grid(kind="toeplitz", first_column=[1, 2, 3])'


def _whole(value, option: str, smallest: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, _nb.Integral) or value < smallest:
        raise SimplydataError(f"{option}= needs a whole number from {smallest} up.\nFor example:  {EXAMPLE}")
    return int(value)


def _list(value, option: str) -> np.ndarray:
    if value is None:
        raise SimplydataError(f"This kind of grid needs {option}.\nFor example:  {EXAMPLE}")
    found = to_array(value, option, EXAMPLE)
    if found.ndim != 1 or not found.size:
        raise SimplydataError(f"{option} needs a list of numbers, such as [1, 2, 3].")
    return found


def _grids(of) -> list[np.ndarray]:
    if not isinstance(of, (list, tuple)) or not of:
        raise SimplydataError("of= needs a list of grids.\nFor example:  "
                              'sdata.number_grid(kind="block diagonal", of=[first, second])')
    return [np.atleast_2d(to_array(g, "of=", "of=[first, second]")) for g in of]


def special_grid(kind, values=None, rows=None, columns=None, size=None, first_column=None, first_row=None,
                 last_row=None, of=None, shifted_by=0, survival=None, axis=None, by_degrees=None):
    """The NumPy array of sdata.number_grid(kind=...), and the call that made it."""
    from scipy import linalg

    if kind not in KINDS:
        raise choice_error("number_grid", "kind", kind, list(KINDS))
    if isinstance(shifted_by, bool) or not isinstance(shifted_by, _nb.Integral):
        raise SimplydataError("shifted_by= needs a whole number (1 is just above the main diagonal, -1 just below).")
    k = int(shifted_by)
    how = KINDS[kind][1]
    if kind == "identity":
        n = _whole(size if size is not None else rows, "size")
        m = n if columns is None else _whole(columns, "columns")
        return np.eye(n, m, k), how
    if kind == "diagonal":
        return np.diag(_list(values, "the numbers"), k), how
    if kind == "ones below diagonal":
        return np.tri(_whole(rows, "rows"), None if columns is None else _whole(columns, "columns"), k), how
    if kind == "vandermonde":
        found = _list(values, "the numbers")
        return np.vander(found, None if columns is None else _whole(columns, "columns")), how
    if kind == "blocks":
        if not isinstance(of, (list, tuple)) or not of or not all(isinstance(row, (list, tuple)) for row in of):
            raise SimplydataError('kind="blocks" needs of= as rows of grids: of=[[first, second], [third, fourth]].')
        try:
            rows = [[np.atleast_2d(to_array(g, "of=", "of=[[a, b], [c, d]]")) for g in row] for row in of]
            return np.block(rows), how
        except ValueError as error:
            raise SimplydataError(f"The grids of of= do not fit together ({error}).") from None
    if kind == "block diagonal":
        return linalg.block_diag(*_grids(of)), how
    if kind == "toeplitz":
        column = _list(first_column, "first_column=")
        return linalg.toeplitz(column, None if first_row is None else _list(first_row, "first_row=")), how
    if kind == "hankel":
        column = _list(first_column, "first_column=")
        return linalg.hankel(column, None if last_row is None else _list(last_row, "last_row=")), how
    if kind == "circulant":
        return linalg.circulant(_list(first_column, "first_column=")), how
    if kind in ("companion", "fiedler companion"):
        found = _list(values, "the polynomial's numbers").astype(float)
        if found.size < 2 or found[0] == 0:
            raise SimplydataError("A companion grid needs at least 2 numbers, the first (highest power) not 0, such as "
                                  "[1, -6, 11, -6] for x**3 - 6x**2 + 11x - 6.")
        func = linalg.companion if kind == "companion" else linalg.fiedler_companion
        return func(found), how
    if kind == "fiedler":
        return linalg.fiedler(_list(values, "the numbers")), how
    if kind == "convolution":
        return linalg.convolution_matrix(_list(values, "the numbers"), _whole(size, "size")), how
    if kind == "hadamard":
        n = _whole(size, "size")
        if n & (n - 1):
            raise SimplydataError(f'kind="hadamard" needs size= a power of 2 (1, 2, 4, 8 ...); it got {n}.')
        return linalg.hadamard(n), how
    if kind in ("hilbert", "inverse hilbert", "helmert"):
        func = {"hilbert": linalg.hilbert, "inverse hilbert": linalg.invhilbert, "helmert": linalg.helmert}[kind]
        return func(_whole(size, "size", 2 if kind == "helmert" else 1)), how
    if kind in ("pascal", "lower pascal", "upper pascal"):
        return linalg.pascal(_whole(size, "size"), kind={"pascal": "symmetric", "lower pascal": "lower",
                                                          "upper pascal": "upper"}[kind]), how
    if kind == "inverse pascal":
        return linalg.invpascal(_whole(size, "size")), how
    if kind == "leslie":
        births, alive = _list(first_row, "first_row= (the births)"), _list(survival, "survival=")
        if alive.size != births.size - 1:
            raise SimplydataError(f"survival= needs one number fewer than first_row= ({births.size - 1}); it has "
                                  f"{alive.size}.")
        return linalg.leslie(births, alive), how
    return _rotation(axis, by_degrees), how


def _rotation(axis, by_degrees):
    """kind="rotation": SymPy rot_axis1, rot_axis2 or rot_axis3 at the angle in radians, as decimals."""
    from .._formula import need_sympy, run_exactly

    sp = need_sympy('sdata.number_grid(kind="rotation")')
    if axis not in AXES:
        raise choice_error("number_grid", "axis", axis, list(AXES))
    if not is_number(by_degrees):
        raise SimplydataError('kind="rotation" needs by_degrees=, such as by_degrees=30.')
    func = getattr(sp, f"rot_axis{AXES[axis]}")
    angle = sp.pi * sp.nsimplify(by_degrees) / 180
    matrix = run_exactly(func, angle, what=f"SymPy rot_axis{AXES[axis]}")
    return np.array(run_exactly(matrix.evalf, what="SymPy evalf"), dtype=float)


def grid_from_formula(text, rows, columns) -> np.ndarray:
    """number_grid(from_formula=, rows=, columns=): the formula of row and column (from 1) at every cell, as NumPy
    fromfunction with the positions plus 1, worked out with SymPy lambdify (Formula.find_value_at)."""
    import contextlib
    import io

    from .._formula import formula

    if not isinstance(text, str) or not text.strip():
        raise SimplydataError('from_formula= needs a formula of row and column in quotes, such as "row * column".')
    n, m = _whole(rows, "rows"), _whole(columns, "columns")
    with contextlib.redirect_stdout(io.StringIO()):
        made = formula(text)
    letters = set(made._letters())
    if not letters <= {"row", "column"}:
        raise SimplydataError("from_formula= uses the letters row and column only; it has "
                              f"{', '.join(sorted(letters))}.")
    row, column = np.indices((n, m)) + 1
    given = {name: (row if name == "row" else column).ravel().astype(float) for name in letters}
    with contextlib.redirect_stdout(io.StringIO()):
        found = made.find_value_at(**given) if given else None
    if found is None:
        return np.full((n, m), float(made.find_value_at()))
    return np.asarray(found._values, dtype=float).reshape(n, m)


@friendly
def make_coordinate_grids(x=None, y=None, rows=None, columns=None):
    """The x and the y at every point. x_grid, y_grid = sdata.make_coordinate_grids(x=[0, 1, 2], y=[10, 20])

    Each row of x_grid is the x values and each column of y_grid the y values, so a grid has a row for each y and a
    column for each x (NumPy meshgrid, as R expand.grid and MATLAB meshgrid). rows= and columns= in place of x= and
    y= give the row number and the column number of every cell, counting from 1 (NumPy indices, plus 1). Then a
    formula works on both at once: distance = (x_grid ** 2 + y_grid ** 2) ** 0.5.
    """
    from .numbers import NumberGrid

    if (x is None) != (y is None) or (rows is None) != (columns is None) or (x is None) == (rows is None):
        raise SimplydataError("make_coordinate_grids() needs x= and y= (the values along each side), or rows= and "
                              "columns= (the size).\nFor example:  "
                              "sdata.make_coordinate_grids(x=[0, 1, 2], y=[10, 20])")
    if rows is not None:
        n, m = _whole(rows, "rows"), _whole(columns, "columns")
        row, column = np.indices((n, m)) + 1
        print(f"The row number and the column number of every cell of a {n} x {m} grid, counting from 1 (NumPy "
              "indices, plus 1).")
        return NumberGrid(row), NumberGrid(column)
    xs = to_array(x, "x=", "x=[0, 1, 2]").ravel()
    ys = to_array(y, "y=", "y=[10, 20]").ravel()
    x_grid, y_grid = np.meshgrid(xs, ys)
    print(f"Two grids of {ys.size} rows (one for each y) and {xs.size} columns (one for each x): x and y at every "
          "point (NumPy meshgrid).")
    return NumberGrid(x_grid), NumberGrid(y_grid)


def say_kind(kind, found, how) -> str:
    rows, columns = found.shape
    article = "An" if kind[0] in "aeiou" else "A"
    return f'{article} {kind} grid of {amount(rows, "row")} and {amount(columns, "column")} ({how}).'


__all__ = ["KINDS", "grid_from_formula", "make_coordinate_grids", "say", "special_grid", "say_kind"]
