"""Numbers phase, batch 4 (approved by Manish 2026-11-26): the matrix words of a square grid, in decimals and exactly.

find_determinant (SciPy linalg.det), take_inverse (SciPy linalg.inv) and find_eigenvalues (SciPy linalg.eigvalsh for
a symmetric grid, linalg.eigvals otherwise); exactly=True on each gives SymPy's exact answer from the grid's numbers
as fractions (SymPy Matrix: det, inv, eigenvals), under simplydata's one time limit for SymPy. grid.find_null_space
(numbers_3.py) takes exactly=True too (SymPy nullspace). Own code is glue only.
"""

from __future__ import annotations

import warnings

import numpy as np

from .._errors import SimplydataError, friendly
from .._time_limit import one_deadline
from .._typing import _Same


def _exact_rows(sp, matrix) -> list[str]:
    from .._formula import _show

    return ["[" + ", ".join(_show(v) for v in matrix.row(i)) + "]" for i in range(matrix.rows)]


SYMMETRIC_TOLERANCE = 100 * np.finfo(float).eps  # as R isSymmetric(): all.equal(a, t(a), tolerance = 100 * eps)


def _is_symmetric(values) -> bool:
    """R isSymmetric(): the mean absolute difference from the transposed grid, relative to the mean size of the
    numbers (all.equal's own measure), is at most 100 times the machine epsilon."""
    gap = float(np.mean(np.abs(values - values.T)))
    size = float(np.mean(np.abs(values)))
    return (gap / size if size > SYMMETRIC_TOLERANCE else gap) <= SYMMETRIC_TOLERANCE


def _order_like_r(real, imaginary, symmetric: bool):
    """The order of R eigen(): a symmetric grid's eigenvalues biggest first, any other grid's by their size (the
    modulus, Mod) biggest first; equal ones keep LAPACK's order."""
    keys = -np.asarray(real, dtype=float) if symmetric else -np.hypot(real, imaginary)
    return np.argsort(keys, kind="stable")


def _in_order_of(decimals, rows):
    """The exact eigenvalues (rows, each with how many times it comes) in the order of the decimal ones (R's order,
    ties of the same size included): each decimal eigenvalue in turn takes the nearest exact one not yet used up."""
    left = [r["times"] for r in rows]
    order = []
    for value in decimals:
        best = min((i for i in range(len(rows)) if left[i] > 0),
                   key=lambda i: abs(complex(rows[i]["eigenvalue"], rows[i]["imaginary part"]) - value))
        left[best] -= 1
        if best not in order:
            order.append(best)
    return [rows[i] for i in order]


@one_deadline
def _exact_eigenvalues(matrix, decimals):
    """find_eigenvalues(exactly=True): SymPy eigenvals and the decimal of each value, under one time limit for the
    whole word, in the order of the decimal eigenvalues (R's order)."""
    from .._formula import EXACTLY_HINT, _show, decimal_of, run_exactly

    found = run_exactly(matrix.eigenvals, what="SymPy eigenvals")
    rows = []
    for value, times in found.items():
        number = complex(decimal_of(value, "SymPy N", EXACTLY_HINT))
        # a real eigenvalue written with I (the roots of a cubic) has no imaginary part, only SymPy's
        # rounding remainder of about 1e-20 at 15 digits: SymPy says it is real, or the part is that small
        if value.is_real or (value.is_real is None and abs(number.imag) <= 1e-12 * max(1.0, abs(number.real))):
            number = complex(number.real, 0.0)
        rows.append({"eigenvalue": number.real, "imaginary part": number.imag,
                     "eigenvalue exactly": _show(value), "times": int(times)})
    return _in_order_of(decimals, rows)


@one_deadline
def _exact_determinant(values):
    from .._formula import EXACTLY_HINT, exact_matrix, float_of, run_exactly

    matrix = exact_matrix(values, "find_determinant", _max_exact())
    found = run_exactly(matrix.det, what="SymPy det")
    return found, float_of(found, "SymPy N", EXACTLY_HINT)


@one_deadline
def _exact_inverse(values, n):
    from .._formula import exact_matrix, run_exactly

    matrix = exact_matrix(values, "take_inverse", _max_exact())
    if run_exactly(matrix.det, what="SymPy det") == 0:
        raise SimplydataError(f"The {n} x {n} grid has no inverse: its determinant is exactly 0 (SymPy det).")
    inverse = run_exactly(matrix.inv, what="SymPy inv")
    return inverse, np.array(run_exactly(inverse.evalf, what="SymPy evalf"), dtype=float)


class GridWords4:
    @friendly
    def find_determinant(self, exactly=False, as_log=False):
        """The determinant of a square grid: one number that is 0 when the grid has no inverse. grid.find_determinant()

        sdata.number_grid([[2, 1], [1, 2]]).find_determinant() gives 3. SciPy linalg.det (from the LU
        decomposition, LAPACK), as R det() and MATLAB det. exactly=True gives the exact answer from SymPy (the
        numbers as fractions), as a formula: formula.find_value_at() gives its decimal. as_log=True gives the natural
        log of its size, which stays readable when the determinant itself is too big or too small for a decimal
        (NumPy linalg.slogdet, as R determinant(x, logarithm = TRUE)); the sentence says its sign. Nothing changes in
        the grid.
        """
        from scipy import linalg

        if not isinstance(exactly, bool):
            raise SimplydataError("exactly= should be True or False.")
        if not isinstance(as_log, bool):
            raise SimplydataError("as_log= should be True or False.")
        if exactly and as_log:
            raise SimplydataError("exactly=True and as_log=True do not go together; choose one.")
        values = self._square("find_determinant")
        n = values.shape[0]
        if as_log:
            from .numpy_grid_words import log_determinant

            sign, logged = log_determinant(values)
            sign_said = {1.0: "positive", -1.0: "negative"}.get(sign, "0")
            if sign == 0:
                print(f"The determinant of the {n} x {n} grid is 0, so its log has no value (NumPy linalg.slogdet).")
                return float("-inf")
            print(f"The natural log of the size of the determinant of the {n} x {n} grid: {logged:.10g}; the "
                  f"determinant is {sign_said}   (NumPy linalg.slogdet)")
            return logged
        if exactly:
            from .._formula import Formula, _show

            found, about = _exact_determinant(values)
            print(f"The determinant of the {n} x {n} grid, exactly: {_show(found)} (about {about:.10g})   (SymPy det, "
                  "exact)")
            return Formula(found)
        found = float(linalg.det(values))
        print(f"The determinant of the {n} x {n} grid: {found:.10g}   (SciPy linalg.det, from the LU decomposition)"
              + (". It is 0, so the grid has no inverse." if found == 0 else ""))
        return found

    @friendly
    def take_inverse(self: _Same, exactly=False, closest_possible=False) -> _Same:
        """Turn a square grid into its inverse: the grid that multiplies it to give the identity. grid.take_inverse()

        sdata.number_grid([[2, 1], [1, 2]]).take_inverse() gives [[2/3, -1/3], [-1/3, 2/3]] as decimals. SciPy
        linalg.inv (LAPACK), as R solve(a) and MATLAB inv. A grid whose determinant is 0 has no inverse, and
        simplydata says so. exactly=True works it out exactly with SymPy (the numbers as fractions), prints the
        fractions and keeps their decimals. closest_possible=True gives the closest thing to an inverse for any grid,
        also one that is not square or has no inverse (the Moore-Penrose pseudo-inverse from the SVD: SciPy
        linalg.pinv, or pinvh for a symmetric grid; R MASS::ginv gives the same, with its own cut-off for tiny
        singular values). Undo with grid.undo(). To solve equations,
        sdata.solve is better than an inverse.
        """
        from scipy import linalg

        if not isinstance(exactly, bool):
            raise SimplydataError("exactly= should be True or False.")
        if not isinstance(closest_possible, bool):
            raise SimplydataError("closest_possible= should be True or False.")
        if closest_possible:
            if exactly:
                raise SimplydataError("exactly=True and closest_possible=True do not go together; choose one.")
            from .numpy_grid_words import closest_inverse

            values = self._no_empty_cells("take_inverse")
            out, how = closest_inverse(values)
            print(f"The closest possible inverse of the {values.shape[0]} x {values.shape[1]} grid ({how}: the "
                  "Moore-Penrose pseudo-inverse); it is "
                  f"{values.shape[1]} x {values.shape[0]}.")
            return self._change("closest possible inverse", out)
        values = self._square("take_inverse")
        n = values.shape[0]
        if exactly:
            import sympy as sp

            inverse, out = _exact_inverse(values, n)
            print(f"The inverse of the {n} x {n} grid, exactly (SymPy inv):")
            for line in _exact_rows(sp, inverse):
                print("  " + line)
            print("The grid now holds these as decimals.")
            return self._change("inverse (exact)", out)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                out = linalg.inv(values)
            except linalg.LinAlgError:
                raise SimplydataError(f"The {n} x {n} grid has no inverse: its determinant is 0 (it is singular). "
                                      "SciPy linalg.inv stopped.") from None
        print(f"The inverse of the {n} x {n} grid (SciPy linalg.inv): the grid times it gives the identity.")
        for w in caught:
            if issubclass(w.category, (linalg.LinAlgWarning, RuntimeWarning)):
                print(f"Note from SciPy: {str(w.message).strip().splitlines()[0]}")
        return self._change("inverse", out)

    @friendly
    def find_eigenvalues(self, exactly=False, structure=None):
        """The eigenvalues of a square grid, biggest first, as a table. grid.find_eigenvalues()

        sdata.number_grid([[2, 1], [1, 2]]).find_eigenvalues() gives 3 and 1. Gives back a table: eigenvalue,
        imaginary part (0 unless the grid turns things round). A symmetric grid (as a correlation grid; symmetric to
        within R isSymmetric's tolerance) uses SciPy linalg.eigvalsh, whose eigenvalues are always real, biggest
        first; any other grid uses linalg.eigvals, ordered by their size (the modulus) biggest first. That is the
        order of R eigen()$values. exactly=True gives the exact eigenvalues from SymPy (eigenvals, the numbers as
        exact fractions), in the same order (R's order, also among eigenvalues of the same size), with how many
        times each comes, for grids up to 6 x 6. structure="banded" (a symmetric grid with numbers only in a band
        round the diagonal; SciPy linalg.eigvals_banded) or "tridiagonal" (only the diagonal and one each side;
        SciPy linalg.eigvalsh_tridiagonal) works from the band alone, which is much faster for big grids. MATLAB
        eig.
        """
        import pandas as pd
        from scipy import linalg

        from ..table import Table

        if not isinstance(exactly, bool):
            raise SimplydataError("exactly= should be True or False.")
        if structure is not None and structure not in EIGEN_STRUCTURES:
            from .._errors import choice_error

            raise choice_error("find_eigenvalues", "structure", structure, list(EIGEN_STRUCTURES))
        values = self._square("find_eigenvalues")
        n = values.shape[0]
        if structure is not None:
            if exactly:
                raise SimplydataError(f'structure="{structure}" works in decimals from the band; leave out '
                                      "exactly=True.")
            found, how = _banded_eigenvalues(values, structure)
            found = found[_order_like_r(found, np.zeros_like(found), True)].astype(complex)
            print(f"The eigenvalues of the {n} x {n} grid, biggest first: "
                  + ", ".join(f"{v.real:.6g}" for v in found[:8]) + (" ..." if n > 8 else "") + f"   ({how})")
            return Table(pd.DataFrame({"eigenvalue": found.real, "imaginary part": found.imag}))
        if exactly:  # the grid's size and cells are checked first
            from .._formula import MAX_EXACT_EIGEN, exact_matrix

            matrix = exact_matrix(values, "find_eigenvalues", MAX_EXACT_EIGEN)
        symmetric = _is_symmetric(values)
        if symmetric:
            found = linalg.eigvalsh(values).astype(complex)
            how = "SciPy linalg.eigvalsh, for a symmetric grid"
        else:
            found = linalg.eigvals(values)
            how = "SciPy linalg.eigvals, ordered by size (modulus) as R eigen()"
        found = found[_order_like_r(found.real, found.imag, symmetric)]
        if exactly:  # SymPy's exact eigenvalues, in the order of the decimal ones (R's order, ties included)
            rows = _exact_eigenvalues(matrix, found)
            said = " and ".join(r["eigenvalue exactly"] for r in rows)
            each = "each once" if all(r["times"] == 1 for r in rows) else \
                "; ".join(f"{r['eigenvalue exactly']} comes {r['times']} times" for r in rows if r["times"] > 1)
            print(f"The eigenvalues of the {n} x {n} grid: {said} ({each})   (SymPy eigenvals, exact)")
            return Table(pd.DataFrame(rows))
        table = pd.DataFrame({"eigenvalue": found.real, "imaginary part": found.imag})
        shown = ", ".join(f"{v.real:.6g}" + (f" {'+' if v.imag > 0 else '-'} {abs(v.imag):.6g}i" if v.imag else "")
                          for v in found[:8]) + (" ..." if n > 8 else "")
        print(f"The eigenvalues of the {n} x {n} grid, biggest first: {shown}   ({how})")
        return Table(table)


# find_eigenvalues(structure=): families for 100 %, batch 19 (approved by Manish 2026-11-28, plan section 2.8)
EIGEN_STRUCTURES = ("banded", "tridiagonal")


def _banded_eigenvalues(values, structure: str):
    """The eigenvalues of a symmetric banded grid from its band (SciPy eigvals_banded or eigvalsh_tridiagonal)."""
    from scipy import linalg

    if not linalg.issymmetric(values):
        raise SimplydataError(f'structure="{structure}" needs a symmetric grid (the same after '
                              "swap_rows_and_columns); leave out structure= for any other grid.")
    below, above = linalg.bandwidth(values)
    if structure == "tridiagonal":
        if above > 1:
            raise SimplydataError(f'structure="tridiagonal" needs numbers only on the diagonal and one diagonal each '
                                  f'side; this grid has {above} each side (structure="banded" works on it).')
        return (linalg.eigvalsh_tridiagonal(np.diagonal(values).copy(), np.diagonal(values, 1).copy()),
                "SciPy linalg.eigvalsh_tridiagonal, from the diagonal and the one beside it")
    n = values.shape[0]
    band = np.zeros((above + 1, n))  # LAPACK's upper banded storage: row above + i - j holds the cell i, j
    for k in range(above + 1):
        band[above - k, k:] = np.diagonal(values, k)
    return (linalg.eigvals_banded(band), f"SciPy linalg.eigvals_banded, from the band of {above} diagonal"
                                         f"{'' if above == 1 else 's'} each side")


def _max_exact() -> int:
    from .._formula import MAX_EXACT_GRID

    return MAX_EXACT_GRID
