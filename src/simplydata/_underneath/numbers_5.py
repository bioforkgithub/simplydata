"""Numbers finishing (P41 and the designed matrix words, approved by Manish 2026-11-25): grid.solve_for (SciPy
linalg.solve; least squares with linalg.lstsq; limits with optimize.nnls and optimize.lsq_linear; exactly with SymPy)
and grid.break_down (the decompositions of SciPy linalg). The parts of a decomposition are compared as NumPy arrays,
in the order the dict gives them.
"""

from . import Entry

ENTRIES = [
    Entry(
        word="grid.solve_for",
        ours="""
            grid = sdata.number_grid([[4, 3, 2], [3, 5, 1], [2, 1, 6]])
            grid.solve_for([1, 2, 3])
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import linalg
            g = np.array([[4, 3, 2], [3, 5, 1], [2, 1, 6]], dtype=float)
            # solve_for([1, 2, 3])
            linalg.solve(g, [1, 2, 3])   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("a square grid uses linalg.solve (the LU decomposition, LAPACK gesv); a grid that is not square has "
                 "no exact answer, so it uses least squares (linalg.lstsq), and the sentence says so.",),
        also="simplydata also says plainly when the grid has no single answer (determinant 0) and what to write "
             "instead.",
    ),
    Entry(
        word="grid.solve_for", option="with_best_fit=",
        ours="""
            grid = sdata.number_grid([[1, 2], [2, 4]])
            grid.solve_for([1, 2], with_best_fit=True)
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import linalg
            g = np.array([[1, 2], [2, 4]], dtype=float)
            # solve_for([1, 2], with_best_fit=True)
            x, leftover, rank, singular_values = linalg.lstsq(g, [1, 2])
            x
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also says that the columns depend on each other (rank 1 of 2), so this answer is the "
             "shortest of many that fit equally well.",
    ),
    Entry(
        word="grid.solve_for", option="between=",
        ours="""
            grid = sdata.number_grid([[2, 0, 1], [1, 1, 0], [0, 3, 1], [1, 0, 2]])
            grid.solve_for([4, 1, 2, 5], between=[0, None])
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import optimize
            g = np.array([[2, 0, 1], [1, 1, 0], [0, 3, 1], [1, 0, 2]], dtype=float)
            # solve_for([4, 1, 2, 5], between=[0, None])
            x, leftover = optimize.nnls(g, [4, 1, 2, 5])   # (1)
            x
        """},
        compare="value",
        tolerance=1e-9,
        choices=("between=[0, None] is non-negative least squares, SciPy optimize.nnls (Lawson and Hanson's active set "
                 "method); any other limits use optimize.lsq_linear with method=\"bvls\" (bounded-variable least "
                 "squares), whose active-set answer is exact, not iterative.",),
        also="simplydata also prints the leftover size and how many of the answers sit at a limit.",
    ),
    Entry(
        word="grid.solve_for", option="exactly=",
        ours="""
            grid = sdata.number_grid([[2, 1], [1, 3]])
            grid.solve_for([1, 1], exactly=True)
        """,
        code={"SymPy": """
            import numpy as np
            import sympy as sp
            # solve_for([1, 1], exactly=True)
            x = sp.Matrix([[2, 1], [1, 3]]).LUsolve(sp.Matrix([1, 1]))   # (1)
            np.array(x.evalf(), dtype=float).ravel()
        """},
        compare="value",
        tolerance=1e-15,
        choices=("the numbers become the fractions they stand for (0.2 is 1/5), then SymPy LUsolve works exactly; a "
                 "grid that is not square uses SymPy solve_least_squares. The answer keeps the decimals of the exact "
                 "fractions, which are printed.",),
        also="simplydata also prints x as fractions (2/5, 1/5).",
    ),
    Entry(
        word="grid.break_down",
        ours="""
            grid = sdata.number_grid([[4, 3, 2], [3, 5, 1], [2, 1, 6], [1, 0, 2]])
            [part.as_numpy() for part in grid.break_down().values()]
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import linalg
            g = np.array([[4, 3, 2], [3, 5, 1], [2, 1, 6], [1, 0, 2]], dtype=float)
            # break_down()
            list(linalg.svd(g, full_matrices=False))   # (1) U, singular values, Vt
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the singular value decomposition by default, the one every grid has (square or not); its short "
                 "(economic) form, as R svd(): U has as many columns as the grid.",),
        also="simplydata also prints what each part is and how the parts multiply back to the grid.",
    ),
    Entry(
        word="grid.break_down", option="test_method=",
        ours="""
            grid = sdata.number_grid([[4, 3, 2], [3, 5, 1], [2, 1, 6]])
            [part.as_numpy() for part in grid.break_down(test_method="lu").values()]
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import linalg
            g = np.array([[4, 3, 2], [3, 5, 1], [2, 1, 6]], dtype=float)
            # break_down(test_method="lu")
            list(linalg.lu(g))   # (1) P, L, U
        """},
        compare="value",
        tolerance=1e-12,
        choices=("each test_method= is SciPy linalg's own call with its own defaults (lu gives grid = P L U, cholesky "
                 "the upper triangle, schur the real form); qr is the short (economic) form, as R qr(); ldl's row "
                 "order counts from 1.",),
        also="simplydata also refuses a grid that does not fit the method (cholesky and ldl need a symmetric grid).",
    ),
    Entry(
        word="grid.break_down", option="together_with=",
        ours="""
            grid = sdata.number_grid([[4, 2], [2, 3]])
            [part.as_numpy() for part in grid.break_down(test_method="qz", together_with=[[1, 0], [0, 2]]).values()]
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import linalg
            a = np.array([[4, 2], [2, 3]], dtype=float)
            b = np.array([[1, 0], [0, 2]], dtype=float)
            # break_down(test_method="qz", together_with=b)
            list(linalg.qz(a, b, output="real"))   # AA, BB, Q, Z
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also checks that the two grids are square and of the same size.",
    ),
]
