"""Numbers finishing (approved by Manish, P41 and the designed matrix words): solve a grid's equations, and break a
grid down into the parts of a matrix decomposition.

grid.solve_for(b) solves grid times x = b: SciPy linalg.solve for a square grid, linalg.lstsq (least squares) for a
grid that is not square or with with_best_fit=True, optimize.nnls for between=[0, None] and optimize.lsq_linear
(bounded least squares, method="bvls") for other limits; exactly=True gives SymPy's exact answer (LUsolve, or
solve_least_squares). grid.break_down(test_method=) gives the parts of a decomposition from SciPy linalg: svd, qr,
lu, cholesky, schur, polar, ldl, hessenberg and qz. Own code is glue only: checks, sentences and the parts in a dict.
"""

from __future__ import annotations

import math
import warnings

import numpy as np

from .._errors import SimplydataError, choice_error, friendly
from .._time_limit import one_deadline
from ._base import amount, is_number, say
from .numbers_3 import _no_empty
from .numbers_4 import _is_symmetric

# test_method= of break_down: what the parts are and how they multiply back to the grid
BREAK_DOWN = {
    "svd": ("the singular value decomposition", "SciPy linalg.svd, full_matrices=False",
            "grid = U times (the singular values on a diagonal) times Vt"),
    "qr": ("the QR decomposition", "SciPy linalg.qr, mode=\"economic\"", "grid = Q times R"),
    "lu": ("the LU decomposition", "SciPy linalg.lu", "grid = P times L times U"),
    "cholesky": ("the Cholesky decomposition", "SciPy linalg.cholesky", "grid = U turned (Ut) times U"),
    "schur": ("the Schur decomposition", "SciPy linalg.schur, output=\"real\"", "grid = Z times T times Zt"),
    "polar": ("the polar decomposition", "SciPy linalg.polar", "grid = U times P"),
    "ldl": ("the LDL decomposition", "SciPy linalg.ldl", "grid = L times D times Lt"),
    "hessenberg": ("the Hessenberg form", "SciPy linalg.hessenberg, calc_q=True", "grid = Q times H times Qt"),
    "qz": ("the QZ (generalised Schur) decomposition of two grids", "SciPy linalg.qz, output=\"real\"",
           "grid = Q times AA times Zt, and the other grid = Q times BB times Zt"),
    # families for 100 %, batch 19 (approved by Manish 2026-11-28, plan section 2.8)
    "rq": ("the RQ decomposition", "SciPy linalg.rq, mode=\"economic\"", "grid = R times Q"),
    "cs": ("the CS (cosine-sine) decomposition of a grid with columns of length 1 at right angles",
           "SciPy linalg.cossin", "grid = U times CS times Vt"),
    "real eigen blocks": ("the eigen decomposition in real numbers (each pair of complex eigenvalues as a 2 x 2 "
                          "block)", "SciPy linalg.eig, then linalg.cdf2rdf",
                          "grid = V times (the eigenvalue blocks) times (V's inverse)"),
    "jordan": ("the Jordan form, exactly", "SymPy Matrix.jordan_form, the numbers as fractions",
               "grid = P times J times (P's inverse)"),
}
JORDAN_HINT = ('The exact Jordan form is slow when the eigenvalues are not simple numbers (roots of a cubic ...); '
               'test_method="schur" or "real eigen blocks" give the decimals.')
# "real eigen blocks": eigenvectors with a condition number above this (NumPy linalg.cond) do not rebuild the grid
EIGENVECTORS_CONDITION = 1e8
# other spellings of test_method= of break_down: SciPy's and SymPy's names
BREAK_DOWN_SPELLINGS = {"cossin": "cs", "cosine-sine": "cs", "cosine sine": "cs", "cdf2rdf": "real eigen blocks",
                        "jordan_form": "jordan", "jordan form": "jordan"}

PARTS = {
    "svd": {"U": "columns of length 1 at right angles (the directions in the rows' space)",
            "singular values": "how much the grid stretches along each direction, biggest first",
            "Vt": "rows of length 1 at right angles (the directions in the columns' space)"},
    "qr": {"Q": "columns of length 1 at right angles", "R": "an upper triangle (zeros below the diagonal)"},
    "lu": {"P": "a grid of 0s and 1s that puts the rows back in their order (the row swaps)",
           "L": "a lower triangle with 1 on the diagonal", "U": "an upper triangle"},
    "cholesky": {"U": "an upper triangle with positive numbers on the diagonal"},
    "schur": {"T": "almost an upper triangle: the eigenvalues on the diagonal (a 2 x 2 square for each pair of "
                   "complex eigenvalues)",
              "Z": "columns of length 1 at right angles"},
    "polar": {"U": "columns of length 1 at right angles (the turn)",
              "P": "a symmetric grid with no negative eigenvalues (the stretch)"},
    "ldl": {"L": "a lower triangle with its rows in another order (row order puts it back)",
            "D": "a diagonal grid, with a 2 x 2 square where needed",
            "row order": "the order of L's rows that makes it a lower triangle (positions from 1)"},
    "hessenberg": {"H": "zeros below the first diagonal under the main one",
                   "Q": "columns of length 1 at right angles"},
    "qz": {"AA": "almost an upper triangle, from the grid", "BB": "an upper triangle, from the other grid",
           "Q": "columns of length 1 at right angles", "Z": "columns of length 1 at right angles"},
    "rq": {"R": "an upper triangle (zeros below the diagonal)", "Q": "rows of length 1 at right angles"},
    "cs": {"U": "a block diagonal grid of two blocks, each with columns of length 1 at right angles",
           "CS": "the cosines and sines of the angles, in four blocks", "Vt": "a block diagonal grid of two blocks, "
                                                                            "each with rows of length 1 at right "
                                                                            "angles"},
    "real eigen blocks": {"eigenvalue blocks": "the real eigenvalues on the diagonal, and a 2 x 2 block [[a, b], "
                                               "[-b, a]] for each pair a +- bi",
                          "V": "the eigenvectors as real columns (the real and imaginary parts of each complex pair)"},
    "jordan": {"P": "the columns that make the change of basis", "J": "the Jordan form: the eigenvalues on the "
                                                                    "diagonal, with 1 just above it inside a block "
                                                                    "for each repeated eigenvalue without enough "
                                                                    "eigenvectors"},
}

SQUARE_ONLY = ("cholesky", "schur", "polar", "ldl", "hessenberg", "qz", "cs", "real eigen blocks", "jordan")
# solve_for(structure=): a banded grid is solved from its band only (families for 100 %, batch 19)
STRUCTURES = ("banded",)


def _values_of(b, step: str, example: str):
    """The right side b as a NumPy array of decimals: numbers (1-D) or a grid (2-D, one right side in each column)."""
    from ._base import BaseNumbers

    if isinstance(b, BaseNumbers):
        values = np.asarray(b._values)
    elif is_number(b):
        values = np.asarray([b])
    else:
        try:
            values = np.asarray(b)
        except (TypeError, ValueError):
            values = np.asarray([object()])
    if values.dtype.kind not in "iuf" or values.ndim not in (1, 2) or values.size == 0:
        raise SimplydataError(f"{step}() needs the right side b as numbers, for example {example}.")
    values = values.astype(float)
    if not np.isfinite(values).all():
        raise SimplydataError(f"{step}() needs a number in every place of b (no empty or infinite ones).")
    return values


def _limits(between):
    """between=[low, high] of solve_for: two numbers or None (no limit), low below high."""
    if not isinstance(between, (list, tuple)) or len(between) != 2:
        raise SimplydataError("between= needs two values in square brackets: [low, high]. None means no limit, "
                              "for example between=[0, None] for answers that are not negative.")
    low, high = between
    for end in (low, high):
        if end is not None and not (is_number(end) and not math.isnan(end)):
            raise SimplydataError("between= takes numbers or None (no limit), for example between=[0, None].")
    low = -math.inf if low is None else float(low)
    high = math.inf if high is None else float(high)
    if not low < high:
        raise SimplydataError(f"between= needs the low end first and below the high end; got [{say(low)}, "
                              f"{say(high)}].")
    if low == -math.inf and high == math.inf:
        raise SimplydataError("between=[None, None] sets no limit; leave it out (with_best_fit=True gives the "
                              "least-squares answer).")
    return low, high


def _shown(x) -> str:
    flat = np.ravel(x)
    return ", ".join(f"{v:.6g}" for v in flat[:8]) + (" ..." if flat.size > 8 else "")


def _limit_words(low: float, high: float) -> str:
    if high == math.inf:
        return f"every x at least {say(low)}"
    if low == -math.inf:
        return f"every x at most {say(high)}"
    return f"every x between {say(low)} and {say(high)}"


@one_deadline
def _exact_solve(values, right, least_squares: bool):
    """solve_for(exactly=True): SymPy LUsolve on a square grid, else solve_least_squares, under one time limit."""
    from .._formula import MAX_EXACT_GRID, exact_matrix, run_exactly

    matrix = exact_matrix(values, "solve_for", MAX_EXACT_GRID)
    if right.ndim == 2 and right.shape[1] > MAX_EXACT_GRID:
        raise SimplydataError(f"solve_for(exactly=True) works with up to {MAX_EXACT_GRID} right sides; b has "
                              f"{right.shape[1]} columns. Leave out exactly=True for the decimal answer.")
    side = exact_matrix(right.reshape(len(right), -1), "solve_for", max(MAX_EXACT_GRID, right.shape[0]))
    if least_squares:
        if run_exactly(matrix.rank, what="SymPy rank") < matrix.cols:
            raise SimplydataError("solve_for(exactly=True) with least squares (a grid that is not square, or "
                                  "with_best_fit=True) needs columns that are independent (no column made of the "
                                  "others): many answers would fit equally well. Leave out exactly=True for the "
                                  "shortest one (SciPy linalg.lstsq).")
        found = run_exactly(matrix.solve_least_squares, side, what="SymPy solve_least_squares")
    else:
        if run_exactly(matrix.det, what="SymPy det") == 0:
            raise SimplydataError(f"The {matrix.rows} x {matrix.rows} grid has no single answer: its determinant is "
                                  "exactly 0. with_best_fit=True gives the least-squares answer.")
        found = run_exactly(matrix.LUsolve, side, what="SymPy LUsolve")
    return found, np.array(run_exactly(found.evalf, what="SymPy evalf"), dtype=float)


def _split_at(split_at, n: int) -> tuple[int, int]:
    """split_at=[rows, columns] of break_down(test_method="cs"): where the grid is cut into four blocks."""
    if split_at is None:
        return n // 2, n // 2
    if not isinstance(split_at, (list, tuple)) or len(split_at) != 2 or not all(
            isinstance(v, (int, np.integer)) and not isinstance(v, bool) and 1 <= v < n for v in split_at):
        raise SimplydataError(f"split_at= needs two whole numbers from 1 to {n - 1}: the rows and columns of the "
                              "first block, such as split_at=[2, 2].")
    return int(split_at[0]), int(split_at[1])


@one_deadline
def _jordan_parts(values) -> dict:
    """break_down(test_method="jordan"): SymPy jordan_form on the numbers as fractions, under one time limit."""
    from .._formula import MAX_EXACT_EIGEN, _guarded, _show, exact_matrix, run_exactly

    if values.shape[0] > MAX_EXACT_EIGEN:
        raise SimplydataError(f'test_method="jordan" works exactly, on grids of up to {MAX_EXACT_EIGEN} x '
                              f"{MAX_EXACT_EIGEN}; this one is {values.shape[0]} x {values.shape[0]}. "
                              'test_method="schur" or "real eigen blocks" give the decimals.')
    matrix = exact_matrix(values, "break_down", MAX_EXACT_EIGEN)
    p, j = _guarded(matrix.jordan_form, what="SymPy jordan_form", hint=JORDAN_HINT)
    if not all(v.is_real for v in list(p) + list(j)):
        raise SimplydataError('test_method="jordan" works when every eigenvalue is real; this grid has complex ones '
                              '(test_method="real eigen blocks" keeps them as real 2 x 2 blocks).')
    print("The Jordan form J, exactly: " + "; ".join(
        "[" + ", ".join(_show(v) for v in j.row(i)) + "]" for i in range(j.rows)) + "   (SymPy jordan_form)")
    return {"P": np.array(run_exactly(p.evalf, what="SymPy evalf"), dtype=float),
            "J": np.array(run_exactly(j.evalf, what="SymPy evalf"), dtype=float)}


def _band_storage(values, below: int, above: int):
    """The band of a square grid in LAPACK's banded storage (row above + i - j holds the cell i, j), as SciPy
    solve_banded and cholesky_banded take it."""
    n = values.shape[0]
    band = np.zeros((below + above + 1, n))
    for k in range(-below, above + 1):
        band[above - k, max(0, k):n + min(0, k)] = np.diagonal(values, k)
    return band


def _solve_banded(values, right):
    """solve_for(structure="banded"): Cholesky on the band for a symmetric grid with positive eigenvalues (SciPy
    cholesky_banded and cho_solve_banded), else solve_banded (LAPACK gbsv)."""
    from scipy import linalg

    below, above = linalg.bandwidth(values)
    if linalg.issymmetric(values):
        try:
            factor = linalg.cholesky_banded(_band_storage(values, 0, above))
        except linalg.LinAlgError:
            pass
        else:
            return (linalg.cho_solve_banded((factor, False), right),
                    f"SciPy linalg.cholesky_banded and cho_solve_banded, on the band of {above} diagonal"
                    f"{'' if above == 1 else 's'} each side (a symmetric grid with positive eigenvalues)")
    found = linalg.solve_banded((below, above), _band_storage(values, below, above), right)
    return found, (f"SciPy linalg.solve_banded, on the band of {below} diagonal{'' if below == 1 else 's'} below "
                   f"and {above} above")


class SolvingWords:
    @friendly
    def solve_for(self, b=None, between=None, with_best_fit=False, exactly=False, structure=None):
        """Find x with grid times x = b: solve a grid's straight-line equations. grid.solve_for([5, 7])

        sdata.number_grid([[2, 1], [1, 3]]).solve_for([5, 10]) gives x = [1, 3], as R solve(a, b) and MATLAB a \\ b.
        A square grid uses SciPy linalg.solve (LU decomposition). A grid that is not square (more equations than
        unknowns, or fewer) has no exact answer, so x is the least-squares answer, the one that makes the squared
        leftovers smallest (SciPy linalg.lstsq); the sentence says so. with_best_fit=True asks for least squares on
        a square grid too (one whose determinant is 0). between=[low, high] keeps every x inside limits (least
        squares with limits; None is no limit): between=[0, None] is non-negative least squares (SciPy
        optimize.nnls, as R nnls and MATLAB lsqnonneg), as for unmixing spectra or a diet mix; other limits use
        optimize.lsq_linear. exactly=True gives SymPy's exact answer (the numbers as fractions). b may be a grid:
        one right side in each column. Gives back numbers (or a grid). structure="banded" solves a square grid
        whose numbers lie in a band round the diagonal from that band only (SciPy linalg.cholesky_banded and
        cho_solve_banded for a symmetric grid with positive eigenvalues, else solve_banded), as for the equations
        of a spline or a diffusion along a line. For equations written as text, see sdata.solve. Nothing changes
        in the grid.
        """
        from scipy import linalg

        from .numbers import NumberGrid, Numbers

        for name, value in (("with_best_fit", with_best_fit), ("exactly", exactly)):
            if not isinstance(value, bool):
                raise SimplydataError(f"{name}= should be True or False.")
        if structure is not None and structure not in STRUCTURES:
            raise choice_error("solve_for", "structure", structure, list(STRUCTURES))
        if b is None:
            raise SimplydataError("solve_for() needs the right side b: one number for each row of the grid."
                                  + self._example("solve_for([5, 10])"))
        values = np.asarray(self._values, dtype=float)
        _no_empty(values, "solve_for")
        if not np.isfinite(values).all():
            raise SimplydataError("solve_for() needs a finite number in every cell of the grid; this one has an "
                                  "infinite one.")
        rows, columns = values.shape
        right = _values_of(b, "solve_for", f"{self._name}.solve_for([5, 10])")
        if right.shape[0] != rows:
            raise SimplydataError(f"b needs one number for each row of the grid: the grid has {amount(rows, 'row')} "
                                  f"and b has {amount(right.shape[0])}.")
        wrap = Numbers if right.ndim == 1 else NumberGrid
        if structure == "banded":
            if between is not None or with_best_fit or exactly:
                raise SimplydataError('structure="banded" solves a square grid exactly from its band; it does not go '
                                      "with between=, with_best_fit= or exactly=.")
            values = self._square("solve_for")
            try:
                out, how = _solve_banded(values, right)
            except linalg.LinAlgError:
                raise SimplydataError(f"The {rows} x {rows} grid has no single answer: it is singular (SciPy "
                                      "linalg.solve_banded stopped).") from None
            print(f"x solves grid times x = b, from the band of the grid: {_shown(out)}   ({how})")
            return wrap(out)
        if between is not None:
            if exactly:
                raise SimplydataError("exactly=True does not go with between=: limits are worked out in decimals "
                                      "(SciPy optimize). Leave out one of them.")
            if with_best_fit:
                raise SimplydataError("between= is least squares already; leave out with_best_fit=True.")
            if right.ndim != 1:
                raise SimplydataError("between= works with one right side: give b as numbers, not a grid.")
            return wrap(self._solve_between(values, right, *_limits(between)))
        least = with_best_fit or rows != columns
        if exactly:
            from .._formula import _show

            found, out = _exact_solve(values, right, least)
            how = "SymPy solve_least_squares, exact least squares" if least else "SymPy LUsolve, exact"
            if right.ndim == 1:
                said = "[" + ", ".join(_show(found[i, 0]) for i in range(found.rows)) + "]"
            else:
                said = "; ".join("[" + ", ".join(_show(v) for v in found.row(i)) + "]" for i in range(found.rows))
            print(f"x, exactly: {said}   ({how})")
            return wrap(out.ravel() if right.ndim == 1 else out)
        if not least:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                try:
                    out = linalg.solve(values, right)
                except linalg.LinAlgError:
                    raise SimplydataError(f"The {rows} x {rows} grid has no single answer: its determinant is 0 (it "
                                          "is singular). with_best_fit=True gives the least-squares answer (SciPy "
                                          "linalg.lstsq).") from None
            notes = [w for w in caught if issubclass(w.category, (linalg.LinAlgWarning, RuntimeWarning))]
            # a grid close to having no inverse (ill-conditioned): the answer may be far off, so not "exactly"
            print(f"x solves grid times x = b{'' if notes else ' exactly'}: {_shown(out)}   (SciPy linalg.solve, LU "
                  "decomposition)")
            for w in notes:
                print(f"Note from SciPy: {str(w.message).strip().splitlines()[0]}")
            return wrap(out)
        out, _, rank, _ = linalg.lstsq(values, right)
        if rows > columns:
            why = (f"the grid has {amount(rows, 'row')} and {amount(columns, 'column')} (more equations than "
                   "unknowns), so no x fits every equation")
        elif rows < columns:
            why = (f"the grid has {amount(rows, 'row')} and {amount(columns, 'column')} (fewer equations than "
                   "unknowns), so many x fit")
        else:
            why = "with_best_fit=True"
        print(f"x is the least-squares answer, because {why}: it makes the total of the squared leftovers (b minus "
              f"grid times x) as small as possible: {_shown(out)}   (SciPy linalg.lstsq)")
        if rank < columns:
            print(f"The grid's columns are not independent (rank {rank} of {columns}), so many answers fit equally "
                  "well; this x is the shortest of them (minimum length).")
        return wrap(out)

    def _solve_between(self, values, right, low: float, high: float):
        from scipy import optimize

        if low == 0 and high == math.inf:
            out, leftover = optimize.nnls(values, right)
            how = "SciPy optimize.nnls, non-negative least squares"
        else:
            found = optimize.lsq_linear(values, right, bounds=(low, high), method="bvls")
            if not found.success:
                raise SimplydataError(f"SciPy optimize.lsq_linear did not finish: {found.message}")
            out = found.x
            leftover = float(np.linalg.norm(values @ out - right))
            how = "SciPy optimize.lsq_linear, method bvls: bounded least squares"
        at_limit = int(np.sum(np.isclose(out, low) | np.isclose(out, high)))
        print(f"x makes grid times x as close to b as it can (least squares) with {_limit_words(low, high)}: "
              f"{_shown(out)}   ({how})")
        print(f"The leftover size (the length of b minus grid times x) is {leftover:.6g}; "
              f"{at_limit} of the {amount(out.size)} {'is' if at_limit == 1 else 'are'} at a limit.")
        return out

    @friendly
    def break_down(self, test_method="svd", together_with=None, split_at=None):
        """Break a grid down into the parts of a matrix decomposition. grid.break_down(test_method="qr")

        sdata.number_grid([[4, 2], [2, 3]]).break_down(test_method="cholesky") gives {"U": ...} with grid = Ut times
        U. Gives back a dict of the parts, each a grid (the singular values and the row order are numbers), and prints
        what each part is and how they multiply back to the grid. test_method= "svd" (the default: singular values,
        for any grid; SciPy linalg.svd), "qr", "rq", "lu", "cholesky" (a symmetric grid with positive eigenvalues),
        "schur", "polar", "ldl" (a symmetric grid), "hessenberg", "qz" (two square grids: give the other one with
        together_with=), "cs" (the cosine-sine decomposition of a grid with columns of length 1 at right angles,
        cut into four blocks after split_at=[rows, columns], half of each unless given; SciPy linalg.cossin), "real
        eigen blocks" (the eigen decomposition in real numbers; SciPy linalg.eig then cdf2rdf) or "jordan" (the
        Jordan form, exactly; SymPy jordan_form). All from SciPy linalg, as R svd(), qr(), chol() and MATLAB svd,
        qr, lu, chol, schur, ldl, hess, qz, jordan. svd, qr and rq give the short (economic) form, as R. Nothing
        changes in the grid.
        """
        from scipy import linalg

        from .numbers import NumberGrid, Numbers

        if isinstance(test_method, str):
            test_method = BREAK_DOWN_SPELLINGS.get(test_method.strip().lower(), test_method)
        if test_method not in BREAK_DOWN:
            raise choice_error("break_down", "test_method", test_method, list(BREAK_DOWN))
        if split_at is not None and test_method != "cs":
            raise SimplydataError('split_at= goes with test_method="cs" only: where the grid is cut into four blocks.')
        values = np.asarray(self._values, dtype=float)
        _no_empty(values, "break_down")
        if not np.isfinite(values).all():
            raise SimplydataError("break_down() needs finite numbers in every cell.")
        if test_method in SQUARE_ONLY:
            values = self._square("break_down")
        if (together_with is None) != (test_method != "qz"):
            raise SimplydataError('together_with= goes with test_method="qz" only, which needs it: the other square '
                                  "grid of the same size." + self._example('break_down(test_method="qz", '
                                                                           "together_with=other_grid)"))
        if test_method in ("cholesky", "ldl") and not _is_symmetric(values):
            raise SimplydataError(f'test_method="{test_method}" needs a symmetric grid (the same after '
                                  "swap_rows_and_columns), as a correlation or covariance grid.")
        if test_method == "svd":
            u, s, vt = linalg.svd(values, full_matrices=False)
            parts = {"U": u, "singular values": s, "Vt": vt}
        elif test_method == "qr":
            q, r = linalg.qr(values, mode="economic")
            parts = {"Q": q, "R": r}
        elif test_method == "lu":
            p, low, up = linalg.lu(values)
            parts = {"P": p, "L": low, "U": up}
        elif test_method == "cholesky":
            try:
                parts = {"U": linalg.cholesky(values)}
            except linalg.LinAlgError:
                raise SimplydataError('test_method="cholesky" needs a grid whose eigenvalues are all above 0 '
                                      "(positive definite); this one has an eigenvalue of 0 or below. "
                                      'test_method="ldl" works on it.') from None
        elif test_method == "schur":
            t, z = linalg.schur(values, output="real")
            parts = {"T": t, "Z": z}
        elif test_method == "polar":
            u, p = linalg.polar(values)
            parts = {"U": u, "P": p}
        elif test_method == "ldl":
            low, d, order = linalg.ldl(values)
            parts = {"L": low, "D": d, "row order": order + 1}
        elif test_method == "hessenberg":
            h, q = linalg.hessenberg(values, calc_q=True)
            parts = {"H": h, "Q": q}
        elif test_method == "rq":
            r, q = linalg.rq(values, mode="economic")
            parts = {"R": r, "Q": q}
        elif test_method == "cs":
            p, q = _split_at(split_at, values.shape[0])
            if not np.allclose(values.T @ values, np.eye(values.shape[0]), atol=1e-10):
                raise SimplydataError('test_method="cs" needs a grid whose columns have length 1 and are at right '
                                      'angles (an orthogonal grid, such as Q of break_down(test_method="qr")).')
            u, cs, vdh = linalg.cossin(values, p=p, q=q)
            parts = {"U": u, "CS": cs, "Vt": vdh}
        elif test_method == "real eigen blocks":
            w, v = linalg.eig(values)
            blocks, vectors = linalg.cdf2rdf(w, v)
            if not np.linalg.cond(vectors) < EIGENVECTORS_CONDITION:
                raise SimplydataError('test_method="real eigen blocks": this grid has a repeated eigenvalue without '
                                      "enough eigenvectors (V has almost no inverse), so grid = V times the blocks "
                                      "times the inverse of V does not hold. test_method=\"jordan\" gives its Jordan "
                                      "form.")
            parts = {"eigenvalue blocks": blocks, "V": vectors}
        elif test_method == "jordan":
            parts = _jordan_parts(values)
        else:
            other = _values_of(together_with, "break_down", f'{self._name}.break_down(test_method="qz", '
                                                            "together_with=other_grid)")
            if other.shape != values.shape:
                raise SimplydataError(f"together_with= needs a grid of the same size as this one ({values.shape[0]} "
                                      f"x {values.shape[1]}); it is {' x '.join(str(n) for n in other.shape)}.")
            aa, bb, q, z = linalg.qz(values, other, output="real")
            parts = {"AA": aa, "BB": bb, "Q": q, "Z": z}
        name, how, back = BREAK_DOWN[test_method]
        rows, columns = values.shape
        print(f"The {rows} x {columns} grid broken down by {name} ({how}): {back}.")
        for part, what in PARTS[test_method].items():
            print(f"  {part}: {what}")
        print("Each part is in the dict this gives back, for example parts[\"" + next(iter(parts)) + "\"].")
        return {part: (Numbers(np.asarray(v)) if np.ndim(v) == 1 else NumberGrid(np.asarray(v)))
                for part, v in parts.items()}
