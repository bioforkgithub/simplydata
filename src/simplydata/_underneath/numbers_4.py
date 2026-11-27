"""Numbers phase, batch 4 (approved by Manish 2026-11-26): the SymPy words. New formula words (show_as_decimal,
group_by_powers_of, turn_into_partial_fractions, as_sympy), sdata.find_sum_of_series, the options how_many_times=,
for_letter= (a list), from_side=, letters_are=, solve(for_letter=) and rules, exactly= on find_volume_under and the
general and second-order paths over time, and the matrix words of a grid (find_determinant, take_inverse,
find_eigenvalues; exactly= on each and on find_null_space). Exact answers are compared as SymPy writes them (text),
numbers to a tight tolerance.
"""

from . import Entry

SYMPY = """
            import sympy as sp
            x = sp.Symbol("x")"""

ENTRIES = [
    # ------------------------------------------------------------------ formula words and options (SymPy)
    Entry(
        word="f.find_slope_formula", option="how_many_times=",
        ours="""
            f = sdata.formula("sin(x)")
            str(f.find_slope_formula(how_many_times=3))
        """,
        code={"SymPy": SYMPY + """
            # f.find_slope_formula(how_many_times=3)
            str(sp.diff(sp.sin(x), x, 3))
        """},
        compare="value",
        also="simplydata also names the derivative (the 3rd) and refuses more than 20 times.",
    ),
    Entry(
        word="f.find_slope_formula", option="for_letter=",
        ours="""
            f = sdata.formula("x**2 * y**3")
            str(f.find_slope_formula(for_letter=["x", "y"]))
        """,
        code={"SymPy": """
            import sympy as sp
            x, y = sp.symbols("x y")
            # f.find_slope_formula(for_letter=["x", "y"])
            str(sp.diff(x**2 * y**3, x, y))
        """},
        compare="value",
        also="simplydata also checks that each letter is a letter of the formula.",
    ),
    Entry(
        word="f.find_limit_as", option="from_side=",
        ours="""
            f = sdata.formula("abs(x) / x")
            f.find_limit_as("x", goes_to=0, from_side="below")
        """,
        code={"SymPy": SYMPY + """
            # f.find_limit_as("x", goes_to=0, from_side="below")
            float(sp.limit(sp.Abs(x) / x, x, 0, dir="-"))
        """},
        compare="value",
        tolerance=0.0,
        also="simplydata also takes \"left\" and \"right\" as other spellings, and refuses a side at infinity.",
    ),
    Entry(
        word="f.show_as_decimal",
        ours="""
            f = sdata.formula("sqrt(2)")
            f.show_as_decimal(digits=50)
        """,
        code={"SymPy": """
            import sympy as sp
            # f.show_as_decimal(digits=50)
            str(sp.N(sp.sqrt(2), 50))
        """},
        compare="value",
        also="simplydata also refuses a formula that still has letters, and digits= above 10,000.",
    ),
    Entry(
        word="f.group_by_powers_of",
        ours="""
            f = sdata.formula("(a + x)*(b + x) - x")
            str(f.group_by_powers_of("x"))
        """,
        code={"SymPy": """
            import sympy as sp
            a, b, x = sp.symbols("a b x")
            # f.group_by_powers_of("x")
            str(sp.collect(sp.expand((a + x)*(b + x) - x), x))   # (1)
        """},
        compare="value",
        choices=("the formula is multiplied out first (expand), so the terms inside brackets are gathered too; SymPy "
                 "collect alone leaves (a + x)*(b + x) as it is.",),
        also="simplydata also refuses a sum with letters raised to a whole power above 100, and f.undo() takes the "
             "step back.",
    ),
    Entry(
        word="f.turn_into_partial_fractions",
        ours="""
            f = sdata.formula("(3*x + 5) / ((x + 1)*(x + 2))")
            str(f.turn_into_partial_fractions())
        """,
        code={"SymPy": SYMPY + """
            # f.turn_into_partial_fractions()
            str(sp.apart((3*x + 5) / ((x + 1)*(x + 2)), x))
        """},
        compare="value",
        also="simplydata also says when the formula is not a fraction of polynomials, and f.undo() takes the step back.",
    ),
    Entry(
        word="f.as_sympy",
        ours="""
            f = sdata.formula("(x + 2)**2 - 4")
            str(f.as_sympy())
        """,
        code={"SymPy": """
            import sympy as sp
            from sympy.parsing.sympy_parser import parse_expr
            # f.as_sympy()
            str(parse_expr("(x + 2)**2 - 4", local_dict={"x": sp.Symbol("x")}))
        """},
        compare="value",
        also="simplydata also prints what kind of SymPy expression it is.",
    ),
    Entry(
        word="sdata.formula", option="letters_are=",
        ours="""
            f = sdata.formula("sqrt(k**2) + log(k*t)", letters_are={"k": "positive", "t": "positive"})
            str(f.turn_into_sum())
        """,
        code={"SymPy": """
            import sympy as sp
            k, t = sp.symbols("k t", positive=True)
            # formula("sqrt(k**2) + log(k*t)", letters_are={"k": "positive", "t": "positive"})
            str(sp.expand(sp.sqrt(k**2) + sp.log(k*t)))
        """},
        compare="value",
        also="simplydata also names each letter with what it is, and takes \"zero or more\", \"negative\", \"real\", "
             "\"whole number\" and \"positive whole number\".",
    ),
    Entry(
        word="sdata.solve", option="for_letter=",
        ours="""
            found = sdata.solve("p*V = n*R*T", for_letter="T", exactly=True)
            found.get_column("T exactly")
        """,
        code={"SymPy": """
            import sympy as sp
            p, V, n, R, T = sp.symbols("p V n R T")
            # solve("p*V = n*R*T", for_letter="T", exactly=True)
            [str(s[T]) for s in sp.solve([sp.Eq(p*V, n*R*T)], [T], dict=True)]
        """},
        compare="value",
        also="simplydata also says which letters stay letters and leaves their decimal empty.",
    ),
    Entry(
        word="sdata.solve", option="letters_are=",
        ours="""
            found = sdata.solve("c**2 = 4", exactly=True, letters_are={"c": "positive"})
            found.get_column("c exactly")
        """,
        code={"SymPy": """
            import sympy as sp
            c = sp.Symbol("c", positive=True)
            # solve("c**2 = 4", exactly=True, letters_are={"c": "positive"})
            [str(s[c]) for s in sp.solve([sp.Eq(c**2, 4)], [c], dict=True)]
        """},
        compare="value",
        also="simplydata also checks with SymPy solveset that these are all the solutions of that kind.",
    ),
    Entry(
        word="sdata.solve", option="exactly=True with a rule",
        ours="""
            found = sdata.solve("x**2 - 4 > 0", exactly=True)
            found.get_column("to exactly")
        """,
        code={"SymPy": SYMPY + """
            # solve("x**2 - 4 > 0", exactly=True)
            ranges = sp.solveset(x**2 - 4 > 0, x, sp.S.Reals)   # (1)
            [str(piece.end).replace("oo", "infinity") for piece in ranges.args]   # (2)
        """},
        compare="value",
        choices=("over the real numbers (domain S.Reals): SymPy solveset's own default is the complex numbers, where "
                 "< and > have no meaning; with letters_are= the numbers the letter may be (positive: 0 to infinity).",
                 "infinity is written as the word, not as SymPy's oo.",),
        also="simplydata also says the answer in words (x < -2 or x > 2) and uses reduce_inequalities for several "
             "rules.",
    ),
    Entry(
        word="sdata.find_sum_of_series",
        ours="""
            str(sdata.find_sum_of_series("1/k**2", between=[1, "infinity"]))
        """,
        code={"SymPy": """
            import sympy as sp
            k = sp.Symbol("k", integer=True)   # (1)
            # find_sum_of_series("1/k**2", between=[1, "infinity"])
            str(sp.summation(1/k**2, (k, 1, sp.oo)))
        """},
        compare="value",
        choices=("the letter that counts is a whole number (integer=True), as it is in a sum; SymPy can then simplify "
                 "terms such as (-1)**(2*k).",),
        also="simplydata also says when the sum grows without end or does not settle (SymPy is_convergent), and "
             "gives the decimal when there is no exact formula.",
    ),
    Entry(
        word="sdata.find_volume_under", option="exactly=",
        ours="""
            str(sdata.find_volume_under("x * y**2", between={"x": [0, 1], "y": [0, 2]}, exactly=True))
        """,
        code={"SymPy": """
            import sympy as sp
            x, y = sp.symbols("x y")
            # find_volume_under("x * y**2", between={"x": [0, 1], "y": [0, 2]}, exactly=True)
            str(sp.integrate(x * y**2, (y, 0, 2), (x, 0, 1)))   # (1)
        """},
        compare="value",
        choices=("the first letter of between= is the outer one, as without exactly=True; SymPy integrates over the "
                 "first range it is given first, so the ranges are handed over in reverse.",),
        also="simplydata also prints the decimal next to the exact answer.",
    ),
    Entry(
        word="sdata.find_path_over_time", option="exactly= without at_start=",
        ours="""
            str(sdata.find_path_over_time("dN/dt = r * N", exactly=True))
        """,
        code={"SymPy": """
            import sympy as sp
            t, r, N = sp.Symbol("t"), sp.Symbol("r"), sp.Function("N")
            # find_path_over_time("dN/dt = r * N", exactly=True)
            s = sp.dsolve(sp.Eq(N(t).diff(t), r * N(t)), N(t))
            str(sp.simplify(s.rhs))
        """},
        compare="value",
        also="simplydata also says that C1 is a free constant that at_start= would fix.",
    ),
    Entry(
        word="sdata.find_path_over_time", option='equations="d2x/dt2 = ..."',
        ours="""
            sdata.find_path_over_time("d2x/dt2 = -k*x - c*dx/dt", at_start={"x": 1, "dx/dt": 0},
                                      between=[0, 10], known={"k": 4, "c": 0.5}, time_step=0.5)
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy.integrate import solve_ivp
            # find_path_over_time("d2x/dt2 = -k*x - c*dx/dt", ...)
            def change(t, y):   # y = [x, dx/dt]   (1)
                return [y[1], -4 * y[0] - 0.5 * y[1]]
            s = solve_ivp(change, (0, 10), [1, 0], t_eval=np.linspace(0, 10, 21),
                          method="RK45", rtol=1e-6, atol=1e-6)
            pd.DataFrame({"time": s.t, "x": s.y[0], "dx/dt": s.y[1]})
        """},
        compare="table",
        tolerance=1e-12,
        choices=("the second-order equation becomes two first-order ones, with the speed dx/dt as a second changing "
                 "value (the standard way for solve_ivp, as in R deSolve).",),
        also="simplydata also reads dx/dt on the right side, and the table shows the speed too.",
    ),
    Entry(
        word="sdata.find_path_over_time", option='equations="d2x/dt2 = ...", exactly=',
        ours="""
            str(sdata.find_path_over_time("d2x/dt2 = -k*x", at_start={"x": 1, "dx/dt": 0}, known={"k": 4},
                                          exactly=True))
        """,
        code={"SymPy": """
            import sympy as sp
            t, x = sp.Symbol("t"), sp.Function("x")
            # find_path_over_time("d2x/dt2 = -k*x", at_start={"x": 1, "dx/dt": 0}, ..., exactly=True)
            ics = {x(0): 1, x(t).diff(t).subs(t, 0): 0}
            s = sp.dsolve(sp.Eq(x(t).diff(t, 2), -4 * x(t)), x(t), ics=ics)
            str(sp.simplify(s.rhs))
        """},
        compare="value",
        also="simplydata also gives the general formula with C1 and C2 when at_start= is left out.",
    ),
    # ------------------------------------------------------------------ the matrix words of a grid
    Entry(
        word="grid.find_determinant",
        ours="""
            grid = sdata.number_grid([[4, 3, 2], [3, 5, 1], [2, 1, 6]])
            grid.find_determinant()
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import linalg
            g = np.array([[4, 3, 2], [3, 5, 1], [2, 1, 6]], dtype=float)
            # find_determinant()
            float(linalg.det(g))
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also says when the determinant is 0 (no inverse), and refuses a grid that is not square.",
    ),
    Entry(
        word="grid.find_determinant", option="exactly=",
        ours="""
            grid = sdata.number_grid([[0.5, 0.25], [0.2, 0.4]])
            str(grid.find_determinant(exactly=True))
        """,
        code={"SymPy": """
            import sympy as sp
            g = [[0.5, 0.25], [0.2, 0.4]]
            # find_determinant(exactly=True)
            m = sp.Matrix([[sp.nsimplify(v, rational=True) for v in row] for row in g])   # (1)
            str(m.det())
        """},
        compare="value",
        choices=("each number becomes the fraction it stands for (SymPy nsimplify, rational=True): 0.2 is 1/5; a "
                 "number no such fraction gives back exactly keeps its exact binary value.",),
        also="simplydata also prints the decimal, and refuses grids bigger than 12 x 12.",
    ),
    Entry(
        word="grid.take_inverse",
        ours="""
            grid = sdata.number_grid([[4, 3, 2], [3, 5, 1], [2, 1, 6]])
            grid.take_inverse()
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import linalg
            g = np.array([[4, 3, 2], [3, 5, 1], [2, 1, 6]], dtype=float)
            # take_inverse()
            linalg.inv(g)
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also says plainly when the grid has no inverse, and undo() gives the grid back.",
    ),
    Entry(
        word="grid.take_inverse", option="exactly=",
        ours="""
            grid = sdata.number_grid([[2, 1], [1, 2]])
            grid.take_inverse(exactly=True)
        """,
        code={"SymPy": """
            import numpy as np
            import sympy as sp
            # take_inverse(exactly=True)
            m = sp.Matrix([[2, 1], [1, 2]]).inv()   # (1)
            np.array(m.evalf(), dtype=float)
        """},
        compare="value",
        tolerance=1e-15,
        choices=("the grid keeps the decimals of the exact inverse; the fractions themselves are printed.",),
        also="simplydata also prints each row as fractions (2/3, -1/3).",
    ),
    Entry(
        word="grid.find_eigenvalues",
        ours="""
            grid = sdata.number_grid([[4, 3, 2], [3, 5, 1], [2, 1, 6]])
            grid.find_eigenvalues()
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import linalg
            g = np.array([[4, 3, 2], [3, 5, 1], [2, 1, 6]], dtype=float)
            # find_eigenvalues()
            values = linalg.eigvalsh(g)[::-1]   # (1) (2)
            pd.DataFrame({"eigenvalue": values, "imaginary part": 0.0})
        """},
        compare="table",
        tolerance=1e-12,
        choices=("a symmetric grid uses eigvalsh, whose eigenvalues are always real; any other grid uses eigvals.",
                 "biggest first, as R eigen() gives them; SciPy gives eigvalsh's smallest first.",),
        also="simplydata also gives an imaginary part, 0 unless the grid turns things round.",
    ),
    Entry(
        word="grid.find_eigenvalues", option="exactly=",
        ours="""
            grid = sdata.number_grid([[2, 1], [1, 2]])
            grid.find_eigenvalues(exactly=True)
        """,
        code={"SymPy": """
            import pandas as pd
            import sympy as sp
            # find_eigenvalues(exactly=True)
            found = sp.Matrix([[2, 1], [1, 2]]).eigenvals()   # {3: 1, 1: 1}
            rows = sorted(found.items(), key=lambda item: -float(item[0]))   # (1)
            pd.DataFrame({"eigenvalue": [float(v) for v, _ in rows], "imaginary part": 0.0,
                          "eigenvalue exactly": [str(v) for v, _ in rows], "times": [n for _, n in rows]})
        """},
        compare="table",
        tolerance=1e-15,
        choices=("biggest first, as without exactly=True; SymPy's dict has no order to rely on.",),
        also="simplydata also says how many times each eigenvalue comes, and refuses grids bigger than 6 x 6.",
    ),
    Entry(
        word="grid.find_null_space", option="exactly=",
        ours="""
            grid = sdata.number_grid([[1, 2, 3], [2, 4, 6]])
            grid.find_null_space(exactly=True)
        """,
        code={"SymPy": """
            import numpy as np
            import sympy as sp
            # find_null_space(exactly=True)
            vectors = sp.Matrix([[1, 2, 3], [2, 4, 6]]).nullspace()
            np.array([[float(v) for v in vec] for vec in vectors]).T   # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("each of SymPy's directions is one column, as without exactly=True (SciPy's columns are of length 1; "
                 "SymPy's are its simplest whole numbers).",),
        also="simplydata also prints the directions exactly and says they are not of length 1.",
    ),
]
