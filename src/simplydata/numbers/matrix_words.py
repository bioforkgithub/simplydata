"""Families for 100 %, batch 19 (approved by Manish 2026-11-28, plan section 2.8, G7): the words of scipy.linalg on a
grid that the numbers phase left open.

grid.take_matrix_function(name) is one family word for the matrix functions of SciPy linalg: logm, sqrtm, cosm,
sinm, tanm, coshm, sinhm, tanhm, signm, expm (take_matrix_exp stays), fractional_matrix_power (NumPy
linalg.matrix_power for a whole power) and funm for a formula of x. grid.check_if_grid_is(kind) asks SciPy
linalg.issymmetric, ishermitian and bandwidth. grid.find_best_rotation_to(other) is SciPy
linalg.orthogonal_procrustes and grid.find_angles_to(other) linalg.subspace_angles. Own code is glue only: checks,
sentences and the answer as a grid.
"""

from __future__ import annotations

import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from .._typing import _Same
from ._base import amount, is_number, say
from .numbers_3 import _no_empty

# name -> (SciPy function, what it is)
MATRIX_FUNCTIONS = {
    "log": ("logm", "the grid whose matrix exponential is this grid"),
    "square root": ("sqrtm", "the grid that, multiplied as a matrix by itself, gives this grid"),
    "exp": ("expm", "1 + A + A**2/2! + ... with matrix products, as take_matrix_exp"),
    "cos": ("cosm", "1 - A**2/2! + A**4/4! - ... with matrix products"),
    "sin": ("sinm", "A - A**3/3! + A**5/5! - ... with matrix products"),
    "tan": ("tanm", "the matrix sine times the inverse of the matrix cosine"),
    "cosh": ("coshm", "1 + A**2/2! + A**4/4! + ... with matrix products"),
    "sinh": ("sinhm", "A + A**3/3! + A**5/5! + ... with matrix products"),
    "tanh": ("tanhm", "the matrix sinh times the inverse of the matrix cosh"),
    "sign": ("signm", "each eigenvalue becomes +1 or -1 by the sign of its real part"),
    "power": ("fractional_matrix_power", "the grid multiplied as a matrix by itself"),
}
# other spellings: SciPy's own names and everyday ones
MATRIX_SPELLINGS = {"logm": "log", "logarithm": "log", "ln": "log", "sqrtm": "square root", "sqrt": "square root",
                    "square_root": "square root", "expm": "exp", "exponential": "exp", "cosm": "cos",
                    "cosine": "cos", "sinm": "sin", "sine": "sin", "tanm": "tan", "tangent": "tan", "coshm": "cosh",
                    "sinhm": "sinh", "tanhm": "tanh", "signm": "sign", "fractional_matrix_power": "power",
                    "matrix_power": "power", "fractional power": "power"}
# check_if_grid_is(kind): SciPy linalg.issymmetric, ishermitian, and bandwidth for the shapes
GRID_KINDS = ("symmetric", "hermitian", "diagonal", "upper triangle", "lower triangle", "banded")
GRID_KIND_SPELLINGS = {"issymmetric": "symmetric", "ishermitian": "hermitian", "bandwidth": "banded",
                       "upper triangular": "upper triangle", "lower triangular": "lower triangle",
                       "triangular upper": "upper triangle", "triangular lower": "lower triangle", "band": "banded"}
# an answer whose imaginary parts are only rounding (about the size of the machine epsilon) is real
IMAGINARY_ROUNDING = 1e-12


def _real_answer(out, step: str, what: str):
    """SciPy's answer as real numbers: complex only by rounding is real; truly complex is refused, with the reason."""
    out = np.asarray(out)
    if np.iscomplexobj(out):
        size = max(1.0, float(np.max(np.abs(out.real)))) if out.size else 1.0
        if out.size and float(np.max(np.abs(out.imag))) > IMAGINARY_ROUNDING * size:
            raise SimplydataError(f"{step}(): {what} of this grid has complex numbers (the grid has a negative or "
                                  "complex eigenvalue), and a grid holds real numbers only. Hand it to SciPy for the "
                                  "complex answer: grid.as_numpy(), then scipy.linalg.")
        out = out.real
    return np.asarray(out, dtype=float)


def _other_grid(other, step: str, example: str):
    """The other grid of a word that compares two grids, as decimals."""
    if other is None:
        raise SimplydataError(f"{step}() needs the other grid.\nFor example:  {example}")
    values = other._values if hasattr(other, "_values") else other
    try:
        values = np.asarray(values, dtype=float)
    except (TypeError, ValueError):
        raise SimplydataError(f"{step}() needs the other grid as numbers in rows (a grid made with "
                              f"sdata.number_grid).\nFor example:  {example}") from None
    if values.ndim != 2 or values.size == 0:
        raise SimplydataError(f"{step}() needs the other grid as rows of numbers (a grid made with "
                              f"sdata.number_grid).\nFor example:  {example}")
    if not np.isfinite(values).all():
        raise SimplydataError(f"{step}() needs a number in every cell of the other grid (no empty or infinite ones).")
    return values


def _formula_function(text: str, step: str):
    """A formula of one name (as "1 / (1 + x)") as a NumPy function that also takes complex numbers (for funm)."""
    from .._maths_formula import read_formula

    formula = read_formula(text)
    if len(formula.names) != 1 or formula.columns_used:
        raise SimplydataError(f'{step}() takes a formula of one name, such as "1 / (1 + x)"; "{text}" has '
                              f"{amount(len(formula.names), 'name')}.")
    name = formula.names[0]

    def worked_out(values):
        with np.errstate(all="ignore"):
            return np.asarray(formula._function({name: values}, {}))

    return worked_out, name


class MatrixWords:
    @friendly(renamed={"name": "function"})
    def take_matrix_function(self: _Same, function=None, power=None) -> _Same:
        """A function of a square grid as a matrix, such as its matrix log or square root. grid.take_matrix_function("log")

        Not the function of each number (that is take_log, take_square_root ...): the matrix function, worked out
        on the grid as a whole, so that the matrix square root multiplied as a matrix by itself gives the grid back.
        function= "log" (SciPy linalg.logm), "square root" (sqrtm), "exp" (expm, as take_matrix_exp), "cos",
        "sin", "tan", "cosh", "sinh", "tanh" (cosm, sinm ...), "sign" (signm) or "power" with power= (NumPy
        linalg.matrix_power for a whole power, SciPy fractional_matrix_power for any other). Any other formula of
        one name, such as "1 / (1 + x)", is worked out by SciPy linalg.funm (Schur-Parlett). SciPy's names (logm,
        sqrtm ...) work too. R expm::logm, sqrtm and MATLAB logm, sqrtm, funm. A grid holds real numbers, so an
        answer with complex numbers (a negative eigenvalue, for the log) is refused with the reason. Undo with
        grid.undo().
        """
        from scipy import linalg

        step = "take_matrix_function"
        if not isinstance(function, str) or not function.strip():
            raise SimplydataError(f'{step}() needs the name of a function, such as "log" or "square root".'
                                  + self._example('take_matrix_function("square root")'))
        key = MATRIX_SPELLINGS.get(function.strip().lower(), function.strip().lower())
        values = self._square(step)
        if not np.isfinite(values).all():
            raise SimplydataError(f"{step}() needs a finite number in every cell.")
        n = values.shape[0]
        if key != "power" and power is not None:
            raise SimplydataError(f'power= goes with "power": take_matrix_function("power", power=0.5).')
        if key in MATRIX_FUNCTIONS:
            scipy_name, what = MATRIX_FUNCTIONS[key]
            if key == "power":
                if not is_number(power) or not np.isfinite(power):
                    raise SimplydataError('"power" needs power= as a number, such as take_matrix_function("power", '
                                          "power=0.5).")
                if float(power) == int(power):
                    out = np.linalg.matrix_power(values, int(power))
                    how = f"NumPy linalg.matrix_power(grid, {int(power)})"
                else:
                    out = linalg.fractional_matrix_power(values, float(power))
                    how = f"SciPy linalg.fractional_matrix_power(grid, {say(power)})"
                what = f"the grid multiplied as a matrix by itself, to the power {say(power)}"
            else:
                out = getattr(linalg, scipy_name)(values)
                how = f"SciPy linalg.{scipy_name}"
            out = _real_answer(out, step, f"the matrix {key}")
            print(f"The matrix {key} of the {n} x {n} grid ({how}): {what}; not the {key} of each number.")
            return self._change(f"matrix {key}" + (f" {say(power)}" if key == "power" else ""), out)
        try:
            worked_out, name = _formula_function(function, step)
        except SimplydataError:
            raise choice_error(step, "function", function, list(MATRIX_FUNCTIONS) + ["a formula of x"]) from None
        out = _real_answer(linalg.funm(values, worked_out, disp=False)[0], step, f"the matrix function {function}")
        print(f"The matrix function {function.strip()} of the {n} x {n} grid, with the grid as {name} (SciPy "
              "linalg.funm, the Schur-Parlett method).")
        return self._change(f"matrix function {function.strip()}", out)

    @friendly(renamed={"tolerance": "within"})
    def check_if_grid_is(self, kind=None, within=None):
        """Check whether a grid has a shape: symmetric, diagonal, a triangle or banded. grid.check_if_grid_is("symmetric")

        Gives back True or False. kind= "symmetric" (the same after swap_rows_and_columns; SciPy
        linalg.issymmetric), "hermitian" (SciPy linalg.ishermitian; for real numbers the same as symmetric),
        "diagonal", "upper triangle" (zeros below the diagonal), "lower triangle" or "banded" (zeros away from a
        band round the diagonal), from SciPy linalg.bandwidth, which also prints how many diagonals below and
        above the main one hold numbers. within= allows small differences from rounding for "symmetric" and
        "hermitian" (an absolute tolerance, such as within=1e-12); without it they must be exactly equal, as
        SciPy. R isSymmetric() and MATLAB issymmetric, bandwidth.
        """
        from scipy import linalg

        step = "check_if_grid_is"
        if not isinstance(kind, str):
            raise SimplydataError(f"{step}() needs a kind of grid, one of: " + ", ".join(f'"{k}"' for k in GRID_KINDS)
                                  + "." + self._example('check_if_grid_is("symmetric")'))
        chosen = GRID_KIND_SPELLINGS.get(kind.strip().lower(), kind.strip().lower())
        if chosen not in GRID_KINDS:
            raise choice_error(step, "kind", kind, list(GRID_KINDS))
        if within is not None and (not is_number(within) or not within >= 0):
            raise SimplydataError("within= needs a number of 0 or more (the biggest difference allowed).")
        values = np.asarray(self._values, dtype=float)
        _no_empty(values, step)
        rows, columns = values.shape
        if chosen in ("symmetric", "hermitian"):
            if rows != columns:
                print(f"No: a {chosen} grid is square, and this one has {amount(rows, 'row')} and "
                      f"{amount(columns, 'column')}.")
                return False
            tolerance = {} if within is None else {"atol": float(within), "rtol": 0.0}
            found = bool((linalg.issymmetric if chosen == "symmetric" else linalg.ishermitian)(values, **tolerance))
            same = "exactly" if within is None else f"to within {say(within)}"
            print(f"{'Yes' if found else 'No'}: the grid is {'' if found else 'not '}{chosen} ({same}; SciPy "
                  f"linalg.is{chosen}" + ("; for real numbers hermitian is the same as symmetric" if chosen ==
                                          "hermitian" else "") + ").")
            return found
        if within is not None:
            raise SimplydataError(f'within= goes with "symmetric" and "hermitian"; "{chosen}" counts the cells that '
                                  "are exactly 0.")
        below, above = linalg.bandwidth(values)
        found = {"diagonal": below == 0 and above == 0, "upper triangle": below == 0, "lower triangle": above == 0,
                 "banded": below < rows - 1 or above < columns - 1}[chosen]
        print(f"{'Yes' if found else 'No'}: the grid is {'' if found else 'not '}{_kind_words(chosen)}. Numbers lie "
              f"on {amount(below, 'diagonal')} below the main one and {amount(above, 'diagonal')} above it (SciPy "
              "linalg.bandwidth).")
        return bool(found)

    @friendly(renamed={"other": "other_grid"})
    def find_best_rotation_to(self, other_grid=None):
        """The rotation that turns this grid's rows closest to another grid's (orthogonal Procrustes). grid.find_best_rotation_to(other_grid)

        Gives back a square grid R (columns of length 1 at right angles) that makes grid multiplied as a matrix
        by R as close as possible to the other grid (the smallest total of squared differences), as when lining
        up two sets of landmarks or two maps of the same points. Both grids need the same size. SciPy
        linalg.orthogonal_procrustes (from the singular value decomposition), as R vegan::procrustes and MATLAB
        procrustes without the scaling. table.find_correlation_between_profiles compares two tables this way.
        Nothing changes in the grid.
        """
        from scipy import linalg

        from .numbers import NumberGrid

        step = "find_best_rotation_to"
        mine = np.asarray(self._values, dtype=float)
        _no_empty(mine, step)
        theirs = _other_grid(other_grid, step, f"{self._name}.find_best_rotation_to(other_grid)")
        if theirs.shape != mine.shape:
            raise SimplydataError(f"{step}() needs two grids of the same size: this one is {mine.shape[0]} x "
                                  f"{mine.shape[1]} and the other {theirs.shape[0]} x {theirs.shape[1]}.")
        rotation, scale = linalg.orthogonal_procrustes(mine, theirs)
        left = float(np.linalg.norm(mine @ rotation - theirs))
        print(f"The best rotation, a {rotation.shape[0]} x {rotation.shape[1]} grid with columns of length 1 at right "
              f"angles (SciPy linalg.orthogonal_procrustes): grid times it is as close as it can be to the other "
              f"grid. The size left over (the length of the differences) is {left:.6g}; the scale is {scale:.6g}.")
        return NumberGrid(rotation)

    @friendly(renamed={"other": "other_grid"})
    def find_angles_to(self, other_grid=None, in_radians=False):
        """The angles between the directions of this grid's columns and another grid's. grid.find_angles_to(other_grid)

        Each grid's columns span a set of directions (a subspace); the principal angles say how far apart the
        two sets are: 0 for a direction both share, 90 degrees for directions at right angles. Gives back the
        angles in degrees, biggest first (in_radians=True for radians), one for each column of the grid with
        fewer columns. Both grids need the same number of rows. SciPy linalg.subspace_angles, as MATLAB subspace
        (its biggest angle). Nothing changes in the grid.
        """
        from scipy import linalg

        from .numbers import Numbers

        step = "find_angles_to"
        if not isinstance(in_radians, bool):
            raise SimplydataError("in_radians= should be True or False.")
        mine = np.asarray(self._values, dtype=float)
        _no_empty(mine, step)
        theirs = _other_grid(other_grid, step, f"{self._name}.find_angles_to(other_grid)")
        if theirs.shape[0] != mine.shape[0]:
            raise SimplydataError(f"{step}() needs two grids with the same number of rows: this one has "
                                  f"{mine.shape[0]} and the other {theirs.shape[0]}.")
        angles = linalg.subspace_angles(mine, theirs)
        shown = angles if in_radians else np.degrees(angles)
        unit = "radians" if in_radians else "degrees"
        print(f"{amount(len(angles), 'angle')} between the directions of the two grids' columns, biggest first, in "
              f"{unit}: " + ", ".join(f"{v:.6g}" for v in shown[:8]) + (" ..." if len(shown) > 8 else "")
              + " (SciPy linalg.subspace_angles).")
        return Numbers(np.asarray(shown, dtype=float))


def _kind_words(kind: str) -> str:
    return {"diagonal": "diagonal (numbers on the main diagonal only)",
            "upper triangle": "an upper triangle (zeros below the diagonal)",
            "lower triangle": "a lower triangle (zeros above the diagonal)",
            "banded": "banded (zeros away from a band round the diagonal)"}[kind]
