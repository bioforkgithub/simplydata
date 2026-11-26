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
from .._typing import _Same


def _exact_rows(sp, matrix) -> list[str]:
    return ["[" + ", ".join(str(v) for v in matrix.row(i)) + "]" for i in range(matrix.rows)]


class GridWords4:
    @friendly
    def find_determinant(self, exactly=False):
        """The determinant of a square grid: one number that is 0 when the grid has no inverse. grid.find_determinant()

        sdata.number_grid([[2, 1], [1, 2]]).find_determinant() gives 3. SciPy linalg.det (from the LU
        decomposition, LAPACK), as R det() and MATLAB det. exactly=True gives the exact answer from SymPy (the
        numbers as fractions), as a formula: f.find_value_at() gives its decimal. Nothing changes in the grid.
        """
        from scipy import linalg

        if not isinstance(exactly, bool):
            raise SimplydataError("exactly= should be True or False.")
        values = self._square("find_determinant")
        n = values.shape[0]
        if exactly:
            from .._formula import Formula, exact_matrix, run_exactly

            import sympy as sp

            matrix = exact_matrix(values, "find_determinant", _max_exact())
            found = run_exactly(matrix.det, what="SymPy det")
            print(f"The determinant of the {n} x {n} grid, exactly: {found} (about {float(sp.N(found)):.10g})   "
                  "(SymPy det, exact)")
            return Formula(found)
        found = float(linalg.det(values))
        print(f"The determinant of the {n} x {n} grid: {found:.10g}   (SciPy linalg.det, from the LU decomposition)"
              + (". It is 0, so the grid has no inverse." if found == 0 else ""))
        return found

    @friendly
    def take_inverse(self: _Same, exactly=False) -> _Same:
        """Turn a square grid into its inverse: the grid that multiplies it to give the identity. grid.take_inverse()

        sdata.number_grid([[2, 1], [1, 2]]).take_inverse() gives [[2/3, -1/3], [-1/3, 2/3]] as decimals. SciPy
        linalg.inv (LAPACK), as R solve(a) and MATLAB inv. A grid whose determinant is 0 has no inverse, and
        simplydata says so. exactly=True works it out exactly with SymPy (the numbers as fractions), prints the
        fractions and keeps their decimals. Undo with grid.undo(). To solve equations, sdata.solve is better than an
        inverse.
        """
        from scipy import linalg

        if not isinstance(exactly, bool):
            raise SimplydataError("exactly= should be True or False.")
        values = self._square("take_inverse")
        n = values.shape[0]
        if exactly:
            from .._formula import exact_matrix, run_exactly

            import sympy as sp

            matrix = exact_matrix(values, "take_inverse", _max_exact())
            if run_exactly(matrix.det, what="SymPy det") == 0:
                raise SimplydataError(f"The {n} x {n} grid has no inverse: its determinant is exactly 0 (SymPy det).")
            inverse = run_exactly(matrix.inv, what="SymPy inv")
            print(f"The inverse of the {n} x {n} grid, exactly (SymPy inv):")
            for line in _exact_rows(sp, inverse):
                print("  " + line)
            print("The grid now holds these as decimals.")
            out = np.array(inverse.evalf(), dtype=float)
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
    def find_eigenvalues(self, exactly=False):
        """The eigenvalues of a square grid, biggest first, as a table. grid.find_eigenvalues()

        sdata.number_grid([[2, 1], [1, 2]]).find_eigenvalues() gives 3 and 1. Gives back a table: eigenvalue,
        imaginary part (0 unless the grid turns things round). A symmetric grid (as a correlation grid) uses SciPy
        linalg.eigvalsh, whose eigenvalues are always real; any other grid uses linalg.eigvals. exactly=True gives
        the exact eigenvalues from SymPy (eigenvals, the numbers as fractions), with how many times each comes, for
        grids up to 6 x 6. As R eigen()$values, MATLAB eig.
        """
        import pandas as pd
        from scipy import linalg

        from ..table import Table

        if not isinstance(exactly, bool):
            raise SimplydataError("exactly= should be True or False.")
        values = self._square("find_eigenvalues")
        n = values.shape[0]
        if exactly:
            from .._formula import MAX_EXACT_EIGEN, exact_matrix, run_exactly

            import sympy as sp

            matrix = exact_matrix(values, "find_eigenvalues", MAX_EXACT_EIGEN)
            found = run_exactly(matrix.eigenvals, what="SymPy eigenvals")
            rows = []
            for value, times in found.items():
                number = complex(sp.N(value))
                rows.append({"eigenvalue": number.real, "imaginary part": number.imag, "eigenvalue exactly": str(value),
                             "times": int(times)})
            rows.sort(key=lambda r: (-r["eigenvalue"], -r["imaginary part"]))
            said = " and ".join(r["eigenvalue exactly"] for r in rows)
            each = "each once" if all(r["times"] == 1 for r in rows) else \
                "; ".join(f"{r['eigenvalue exactly']} comes {r['times']} times" for r in rows if r["times"] > 1)
            print(f"The eigenvalues of the {n} x {n} grid: {said} ({each})   (SymPy eigenvals, exact)")
            return Table(pd.DataFrame(rows))
        symmetric = bool(np.array_equal(values, values.T))
        if symmetric:
            found = linalg.eigvalsh(values)[::-1].astype(complex)
            how = "SciPy linalg.eigvalsh, for a symmetric grid"
        else:
            found = linalg.eigvals(values)
            found = found[np.lexsort((-found.imag, -found.real))]
            how = "SciPy linalg.eigvals"
        table = pd.DataFrame({"eigenvalue": found.real, "imaginary part": found.imag})
        shown = ", ".join(f"{v.real:.6g}" + (f" {'+' if v.imag > 0 else '-'} {abs(v.imag):.6g}i" if v.imag else "")
                          for v in found[:8]) + (" ..." if n > 8 else "")
        print(f"The eigenvalues of the {n} x {n} grid, biggest first: {shown}   ({how})")
        return Table(table)


def _max_exact() -> int:
    from .._formula import MAX_EXACT_GRID

    return MAX_EXACT_GRID
