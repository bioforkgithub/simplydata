"""Families for 100 %, batch 19 (approved by Manish 2026-11-28): the matrices of scipy.linalg (plan section 2.8):
take_matrix_function with each of its names, check_if_grid_is, find_best_rotation_to, find_angles_to,
solve_matrix_equation, the new test_method= values of break_down, solve_for(structure=), find_eigenvalues(structure=)
and make_pair_table_with(column_by_column=True), each next to the SciPy code that does the same job."""

from . import Entry

GRID = "[[4, 2, 1], [2, 3, 0.5], [1, 0.5, 2]]"
NOT_EACH = "simplydata also says it is the matrix function, not the function of each number, and refuses a grid that " \
           "is not square or an answer with complex numbers."


def _matrix_function(name: str, scipy_name: str, word_entry: bool = False) -> Entry:
    return Entry(
        word="grid.take_matrix_function",
        option="" if word_entry else f'function="{name}"',
        ours=f"""
            grid = sdata.number_grid({GRID})
            grid.take_matrix_function("{name}")
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import linalg
            g = np.array({GRID})
            # take_matrix_function("{name}")
            linalg.{scipy_name}(g)
        """},
        compare="value",
        tolerance=1e-10,
        also=NOT_EACH,
    )


def _grid_kind(kind: str, line: str, grid: str = "[[4, 1, 0], [1, 4, 1], [0, 1, 4]]", word_entry=False) -> Entry:
    return Entry(
        word="grid.check_if_grid_is",
        option="" if word_entry else f'kind="{kind}"',
        ours=f"""
            grid = sdata.number_grid({grid})
            grid.check_if_grid_is("{kind}")
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import linalg
            g = np.array({grid}, dtype=float)
            # check_if_grid_is("{kind}")
            {line}
        """},
        compare="value",
        also="simplydata also prints how many diagonals below and above the main one hold numbers.",
    )


def _equation(kind: str, call: str, given: str, line: str, word_entry=False) -> Entry:
    return Entry(
        word="sdata.solve_matrix_equation",
        option="" if word_entry else f'kind="{kind}"',
        ours=f"""
            sdata.solve_matrix_equation("{kind}", {call})
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import linalg
            {given}
            # solve_matrix_equation("{kind}", {call})
            {line}
        """},
        compare="value",
        tolerance=1e-10,
        also="simplydata also writes the equation in words and how far X is from fitting it.",
    )


A2 = "a, q = np.array([[-1, 0.5], [0, -2]]), np.eye(2)"
RICCATI = "a, b, q, r = np.array([[0, 1], [0, 0]]), np.array([[0], [1]]), np.eye(2), np.array([[1]])"
TRI = "[[4, 1, 0, 0], [1, 4, 1, 0], [0, 1, 4, 1], [0, 0, 1, 4]]"

ENTRIES = [
    _matrix_function("square root", "sqrtm", word_entry=True),
    *[_matrix_function(name, scipy_name) for name, scipy_name in (
        ("log", "logm"), ("exp", "expm"), ("cos", "cosm"), ("sin", "sinm"), ("tan", "tanm"), ("cosh", "coshm"),
        ("sinh", "sinhm"), ("tanh", "tanhm"), ("sign", "signm"))],
    Entry(
        word="grid.take_matrix_function", option="power=",
        ours=f"""
            grid = sdata.number_grid({GRID})
            grid.take_matrix_function("power", power=0.5)
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import linalg
            g = np.array({GRID})
            # take_matrix_function("power", power=0.5)
            linalg.fractional_matrix_power(g, 0.5)   # (1)
        """},
        compare="value",
        tolerance=1e-10,
        choices=("a whole power uses NumPy linalg.matrix_power (repeated matrix products); any other power SciPy "
                 "linalg.fractional_matrix_power.",),
        also=NOT_EACH,
    ),
    Entry(
        word="grid.take_matrix_function", option='function="a formula of x"',
        ours=f"""
            grid = sdata.number_grid({GRID})
            grid.take_matrix_function("1 / (1 + x)")
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import linalg
            g = np.array({GRID})
            # take_matrix_function("1 / (1 + x)")
            linalg.funm(g, lambda x: 1 / (1 + x), disp=False)[0]   # (1)
        """},
        compare="value",
        tolerance=1e-10,
        choices=("any formula of x, read safely by simplydata's formula reader, goes to SciPy linalg.funm "
                 "(the Schur-Parlett method).",),
        also=NOT_EACH,
    ),
    _grid_kind("symmetric", "linalg.issymmetric(g)", word_entry=True),
    _grid_kind("hermitian", "linalg.ishermitian(g)"),
    _grid_kind("banded", "lower, upper = linalg.bandwidth(g)\n            lower < 2 or upper < 2"),
    _grid_kind("diagonal", "linalg.bandwidth(g) == (0, 0)"),
    _grid_kind("upper triangle", "linalg.bandwidth(g)[0] == 0", "[[1, 2, 3], [0, 4, 5], [0, 0, 6]]"),
    _grid_kind("lower triangle", "linalg.bandwidth(g)[1] == 0", "[[1, 2, 3], [0, 4, 5], [0, 0, 6]]"),
    Entry(
        word="grid.check_if_grid_is", option="within=",
        ours="""
            grid = sdata.number_grid([[1, 2], [2.0000000001, 1]])
            grid.check_if_grid_is("symmetric", within=1e-6)
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import linalg
            g = np.array([[1, 2], [2.0000000001, 1]])
            # check_if_grid_is("symmetric", within=1e-6)
            linalg.issymmetric(g, atol=1e-6, rtol=0)   # (1)
        """},
        compare="value",
        choices=("within= is an absolute tolerance; without it the grid must be exactly symmetric, as SciPy.",),
        also="simplydata also says how close it had to be.",
    ),
    Entry(
        word="grid.find_best_rotation_to",
        ours="""
            grid = sdata.number_grid([[1, 0], [0, 1], [1, 1]])
            grid.find_best_rotation_to(sdata.number_grid([[0, 1], [-1, 0], [-1, 1]]))
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import linalg
            a, b = np.array([[1, 0], [0, 1], [1, 1]]), np.array([[0, 1], [-1, 0], [-1, 1]])
            # find_best_rotation_to(other_grid)
            linalg.orthogonal_procrustes(a, b)[0]
        """},
        compare="value",
        tolerance=1e-10,
        also="simplydata also says how far the rotated grid is from the other grid, and the scale.",
    ),
    Entry(
        word="grid.find_angles_to",
        ours="""
            grid = sdata.number_grid([[1, 0], [0, 1], [0, 0]])
            grid.find_angles_to(sdata.number_grid([[1, 0], [0, 1], [0, 1]]))
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import linalg
            a, b = np.array([[1, 0], [0, 1], [0, 0]]), np.array([[1, 0], [0, 1], [0, 1]])
            # find_angles_to(other_grid)
            np.degrees(linalg.subspace_angles(a, b))   # (1)
        """},
        compare="value",
        tolerance=1e-10,
        choices=("the angles in degrees, biggest first; in_radians=True keeps SciPy's radians.",),
        also="simplydata also prints the angles.",
    ),
    _equation("lyapunov", "a=[[-1, 0.5], [0, -2]], q=[[1, 0], [0, 1]]", A2, "linalg.solve_continuous_lyapunov(a, q)",
              word_entry=True),
    _equation("discrete lyapunov", "a=[[0.5, 0.1], [0, 0.3]], q=[[1, 0], [0, 1]]",
              "a, q = np.array([[0.5, 0.1], [0, 0.3]]), np.eye(2)", "linalg.solve_discrete_lyapunov(a, q)"),
    _equation("sylvester", "a=[[-1, 0.5], [0, -2]], b=[[-3]], q=[[1], [2]]",
              "a, b, q = np.array([[-1, 0.5], [0, -2]]), np.array([[-3]]), np.array([[1], [2]])",
              "linalg.solve_sylvester(a, b, q)"),
    _equation("riccati", "a=[[0, 1], [0, 0]], b=[[0], [1]], q=[[1, 0], [0, 1]], r=[[1]]", RICCATI,
              "linalg.solve_continuous_are(a, b, q, r)"),
    _equation("discrete riccati", "a=[[0, 1], [0, 0]], b=[[0], [1]], q=[[1, 0], [0, 1]], r=[[1]]", RICCATI,
              "linalg.solve_discrete_are(a, b, q, r)"),
    Entry(
        word="grid.break_down", option='test_method="rq"',
        ours=f"""
            grid = sdata.number_grid({GRID})
            [part.as_numpy() for part in grid.break_down(test_method="rq").values()]
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import linalg
            g = np.array({GRID})
            # break_down(test_method="rq")
            list(linalg.rq(g, mode="economic"))   # (1) R, Q
        """},
        compare="value",
        tolerance=1e-10,
        choices=("the short (economic) form, as for qr.",),
        also="simplydata also prints what each part is and how they multiply back to the grid.",
    ),
    Entry(
        word="grid.break_down", option='test_method="cs"',
        ours="""
            grid = sdata.number_grid([[0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 1, 0, 0]])
            [part.as_numpy() for part in grid.break_down(test_method="cs").values()]
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import linalg
            g = np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 1, 0, 0]], dtype=float)
            # break_down(test_method="cs")
            list(linalg.cossin(g, p=2, q=2))   # (1) U, CS, Vt
        """},
        compare="value",
        tolerance=1e-10,
        choices=("the four blocks are cut after half the rows and half the columns unless split_at= says where.",),
        also="simplydata also checks that the grid's columns have length 1 and are at right angles.",
    ),
    Entry(
        word="grid.break_down", option='test_method="real eigen blocks"',
        ours="""
            grid = sdata.number_grid([[0, -2, 0], [1, 0, 0], [0, 0, 3]])
            [part.as_numpy() for part in grid.break_down(test_method="real eigen blocks").values()]
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import linalg
            g = np.array([[0, -2, 0], [1, 0, 0], [0, 0, 3]], dtype=float)
            # break_down(test_method="real eigen blocks")
            list(linalg.cdf2rdf(*linalg.eig(g)))   # (1) the eigenvalue blocks, V
        """},
        compare="value",
        tolerance=1e-10,
        choices=("the eigenvalues and eigenvectors of linalg.eig, turned into real 2 x 2 blocks by linalg.cdf2rdf.",),
        also="simplydata also prints what each part is.",
    ),
    Entry(
        word="grid.break_down", option='test_method="jordan"',
        ours="""
            grid = sdata.number_grid([[2, 1, 0], [0, 2, 0], [0, 0, 3]])
            [part.as_numpy() for part in grid.break_down(test_method="jordan").values()]
        """,
        code={"SymPy": """
            import numpy as np
            import sympy as sp
            m = sp.Matrix([[2, 1, 0], [0, 2, 0], [0, 0, 3]])
            # break_down(test_method="jordan")
            p, j = m.jordan_form()   # (1)
            [np.array(p.evalf(), dtype=float), np.array(j.evalf(), dtype=float)]
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the numbers as exact fractions (SymPy nsimplify), so the Jordan form is exact.",),
        also="simplydata also prints J exactly and refuses complex eigenvalues (\"real eigen blocks\" keeps them).",
    ),
    Entry(
        word="grid.solve_for", option="structure=",
        ours=f"""
            grid = sdata.number_grid({TRI})
            grid.solve_for([1, 2, 3, 4], structure="banded")
        """,
        code={"SciPy": f"""
            import numpy as np
            from scipy import linalg
            band = np.array([[0, 1, 1, 1], [4, 4, 4, 4]], dtype=float)   # (1) the band, above the diagonal
            # solve_for([1, 2, 3, 4], structure="banded")
            factor = linalg.cholesky_banded(band)   # (2)
            linalg.cho_solve_banded((factor, False), [1, 2, 3, 4])
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the band is read from the grid with SciPy linalg.bandwidth and put in LAPACK's banded storage.",
                 "a symmetric grid with positive eigenvalues uses Cholesky on the band; any other banded grid "
                 "linalg.solve_banded."),
        also="simplydata also says which band it used.",
    ),
    Entry(
        word="grid.find_eigenvalues", option="structure=",
        ours=f"""
            grid = sdata.number_grid({TRI})
            grid.find_eigenvalues(structure="tridiagonal").get_column("eigenvalue")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import linalg
            # find_eigenvalues(structure="tridiagonal")
            found = linalg.eigvalsh_tridiagonal([4, 4, 4, 4], [1, 1, 1])   # (1)
            found[::-1]
        """},
        compare="value",
        tolerance=1e-12,
        choices=("biggest first, as R eigen() for a symmetric grid; structure=\"banded\" uses linalg.eigvals_banded.",),
        also="simplydata also checks the grid is symmetric and banded.",
    ),
    Entry(
        word="nums.make_pair_table_with", option="column_by_column=",
        ours="""
            grid = sdata.number_grid([[1, 2], [3, 4]])
            grid.make_pair_table_with(sdata.number_grid([[5, 6], [7, 8], [9, 10]]), as_blocks=True,
                                      column_by_column=True)
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import linalg
            a, b = np.array([[1, 2], [3, 4]]), np.array([[5, 6], [7, 8], [9, 10]])
            # make_pair_table_with(other_grid, as_blocks=True, column_by_column=True)
            linalg.khatri_rao(a, b)
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also checks the two grids have the same number of columns.",
    ),
]
