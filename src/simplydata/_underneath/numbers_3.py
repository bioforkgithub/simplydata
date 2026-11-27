"""Numbers phase, batch 3 (approved by Manish 2026-11-25): formulas with SymPy (simplydata[exact]), areas, volumes
and paths over time (SciPy integrate), the new words on numbers and grids (NumPy, SciPy fft, signal, ndimage and
linalg) and on tables (SciPy spatial), and one entry for each option that changes what a word calls (exactly=,
test_method=). Exact answers are compared as SymPy writes them (text), numbers to a tight tolerance.
"""

from . import Entry

SYMPY = """
            import sympy as sp
            x = sp.Symbol("x")"""

ENTRIES = [
    # ------------------------------------------------------------------ formulas (SymPy)
    Entry(
        word="sdata.formula",
        ours="""
            formula = sdata.formula("(x + 2)**2 - 4")
            str(formula)
        """,
        code={"SymPy": """
            import sympy as sp
            from sympy.parsing.sympy_parser import parse_expr
            # formula("(x + 2)**2 - 4")
            letters = {"x": sp.Symbol("x")}                          # (1)
            str(parse_expr("(x + 2)**2 - 4", local_dict=letters))
        """},
        compare="value",
        choices=("every letter is handed to SymPy as a Symbol of its own, so letters such as E, I, N and S stay "
                 "letters (SymPy alone reads them as its constant e, the imaginary unit and its own functions).",),
        also="simplydata also checks the text first with Python's ast (numbers, letters, + - * / ** ^, brackets and "
             "the functions of fit_formula only) and names the letters it found.",
    ),
    Entry(
        word="f.make_simpler",
        ours="""
            formula = sdata.formula("(x**2 - 1) / (x - 1)")
            str(formula.make_simpler())
        """,
        code={"SymPy": SYMPY + """
            # formula.make_simpler()
            str(sp.simplify((x**2 - 1) / (x - 1)))
        """},
        compare="value",
        also="simplydata also prints the formula before and after, and formula.undo() takes the step back.",
    ),
    Entry(
        word="f.turn_into_sum",
        ours="""
            formula = sdata.formula("(x + 2)**2 - 4")
            str(formula.turn_into_sum())
        """,
        code={"SymPy": SYMPY + """
            # formula.turn_into_sum()
            str(sp.expand((x + 2)**2 - 4))
        """},
        compare="value",
        also="simplydata also prints the formula before and after, and formula.undo() takes the step back.",
    ),
    Entry(
        word="f.turn_into_product",
        ours="""
            formula = sdata.formula("x**2 + 4*x")
            str(formula.turn_into_product())
        """,
        code={"SymPy": SYMPY + """
            # formula.turn_into_product()
            str(sp.factor(x**2 + 4*x))
        """},
        compare="value",
        also="simplydata also prints the formula before and after, and formula.undo() takes the step back.",
    ),
    Entry(
        word="f.find_slope_formula",
        ours="""
            formula = sdata.formula("x**3 - 2*x")
            str(formula.find_slope_formula())
        """,
        code={"SymPy": SYMPY + """
            # formula.find_slope_formula()
            str(sp.diff(x**3 - 2*x, x))
        """},
        compare="value",
        also="simplydata also finds the letter itself when the formula has only one (for_letter= otherwise).",
    ),
    Entry(
        word="f.find_area_formula",
        ours="""
            formula = sdata.formula("x**3 - 2*x")
            str(formula.find_area_formula())
        """,
        code={"SymPy": SYMPY + """
            # formula.find_area_formula()
            str(sp.integrate(x**3 - 2*x, x))
        """},
        compare="value",
        also="simplydata also says \"plus any constant\", and stops with a sentence when SymPy finds no formula.",
    ),
    Entry(
        word="f.find_value_at",
        ours="""
            formula = sdata.formula("x**3 - 2*x")
            formula.find_value_at(x=2.5)
        """,
        code={"SymPy": SYMPY + """
            # formula.find_value_at(x=2.5)
            float((x**3 - 2*x).subs(x, sp.Rational(5, 2)).evalf())   # (1)
        """},
        compare="value",
        tolerance=1e-15,
        choices=("a decimal such as 2.5 is put in as the fraction it stands for (5/2, SymPy nsimplify), so the "
                 "answer is worked out exactly before it is turned into a decimal.",),
        also="simplydata also takes a list of values (SymPy lambdify, then NumPy) and gives numbers back.",
    ),
    Entry(
        word="f.put_in",
        ours="""
            formula = sdata.formula("x**2")
            str(formula.put_in(x="y + 1"))
        """,
        code={"SymPy": SYMPY + """
            y = sp.Symbol("y")
            # formula.put_in(x="y + 1")
            str((x**2).subs(x, y + 1))
        """},
        compare="value",
        also="simplydata also reads the text \"y + 1\" with the same safe reader as the formula.",
    ),
    Entry(
        word="f.show_as_latex",
        ours="""
            formula = sdata.formula("x**3 - 2*x")
            formula.show_as_latex()
        """,
        code={"SymPy": SYMPY + """
            # formula.show_as_latex()
            sp.latex(x**3 - 2*x)
        """},
        compare="value",
        also="simplydata also prints the text; it writes no file.",
    ),
    Entry(
        word="f.find_limit_as",
        ours="""
            formula = sdata.formula("sin(x) / x")
            formula.find_limit_as("x", goes_to=0)
        """,
        code={"SymPy": SYMPY + """
            # formula.find_limit_as("x", goes_to=0)
            float(sp.limit(sp.sin(x) / x, x, 0, dir="+-"))   # (1)
        """},
        compare="value",
        tolerance=1e-15,
        choices=("at a number the limit is taken from both sides (dir=\"+-\"), as in school maths; SymPy's own "
                 "default looks from above only.",),
        also="simplydata also says when the two sides differ, with the value from each.",
    ),
    Entry(
        word="f.find_taylor_series",
        ours="""
            formula = sdata.formula("exp(x)")
            str(formula.find_taylor_series(around=0, up_to_power=4))
        """,
        code={"SymPy": SYMPY + """
            # formula.find_taylor_series(around=0, up_to_power=4)
            str(sp.series(sp.exp(x), x, 0, n=5).removeO())   # (1)
        """},
        compare="value",
        choices=("up_to_power=4 keeps the powers up to 4: SymPy's n= counts the order of the term left out, so it "
                 "is up_to_power + 1.",),
        also="simplydata also gives back a formula, so its words work on the series.",
    ),
    Entry(word="f.undo", ours="""
            formula = sdata.formula("(x + 2)**2 - 4")
            formula.turn_into_sum()
            formula.undo()
        """, compare="none",
          note="simplydata's own: a formula keeps its earlier forms. A SymPy expression never changes, so in SymPy "
               "you keep the old one in a variable yourself."),
    Entry(
        word="sdata.solve", option="exactly=",
        ours="""
            found = sdata.solve("x**2 = 2", exactly=True)
            found.get_column("x exactly")
        """,
        code={"SymPy": SYMPY + """
            # solve("x**2 = 2", exactly=True)
            [str(s[x]) for s in sp.solve([sp.Eq(x**2, 2)], [x], dict=True)]
        """},
        compare="value",
        also="simplydata also gives the decimal of each solution and says when one is not an ordinary number.",
    ),
    # ------------------------------------------------------------------ areas, volumes, paths (SciPy integrate)
    Entry(
        word="sdata.find_area_under",
        ours="""
            sdata.find_area_under("exp(-x**2)", between=[0, "infinity"])
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import integrate
            # find_area_under("exp(-x**2)", between=[0, "infinity"])
            integrate.quad(lambda x: np.exp(-x**2), 0, np.inf)[0]   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("SciPy quad's own tolerances (1.49e-8, relative and absolute); R integrate() stops sooner, at a "
                 "relative error of about 1.2e-4.",),
        also="simplydata also prints the error estimate and passes on SciPy's warnings as notes.",
    ),
    Entry(
        word="sdata.find_area_under", option="test_method=",
        ours="""
            sdata.find_area_under("x**4", between=[0, 2], test_method="gauss")
        """,
        code={"SciPy": """
            from scipy import integrate
            # find_area_under("x**4", between=[0, 2], test_method="gauss")
            integrate.fixed_quad(lambda x: x**4, 0, 2, n=5)[0]   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("5 points (SciPy fixed_quad's own default): exact for polynomials up to the power 9.",),
        also="simplydata also refuses \"infinity\" as an end for this method.",
    ),
    Entry(
        word="sdata.find_area_under", option="exactly=",
        ours="""
            str(sdata.find_area_under("exp(-x**2)", between=[0, "infinity"], exactly=True))
        """,
        code={"SymPy": SYMPY + """
            # find_area_under("exp(-x**2)", between=[0, "infinity"], exactly=True)
            str(sp.integrate(sp.exp(-x**2), (x, 0, sp.oo)))
        """},
        compare="value",
        also="simplydata also prints the decimal next to the exact answer.",
    ),
    Entry(
        word="sdata.find_volume_under",
        ours="""
            sdata.find_volume_under("x * y**2", between={"x": [0, 1], "y": [0, 2]})
        """,
        code={"SciPy": """
            from scipy import integrate
            # find_volume_under("x * y**2", between={"x": [0, 1], "y": [0, 2]})
            integrate.dblquad(lambda y, x: x * y**2, 0, 1, 0, 2)[0]   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the first letter of between= is the outer one; SciPy wants the inner letter first in the "
                 "function, so the letters are handed over in reverse.",),
        also="simplydata also picks tplquad for three letters and nquad for more.",
    ),
    Entry(
        word="sdata.find_path_over_time",
        ours="""
            sdata.find_path_over_time("dN/dt = r * N * (1 - N / K)", at_start={"N": 10}, between=[0, 50],
                                      known={"r": 0.3, "K": 1000}, time_step=0.5)
        """,
        code={"SciPy": """
            import numpy as np
            import pandas as pd
            from scipy.integrate import solve_ivp
            # find_path_over_time("dN/dt = r * N * (1 - N / K)", ...)
            r, K = 0.3, 1000
            t = np.linspace(0, 50, 101)                                   # (1)
            s = solve_ivp(lambda t, N: r * N * (1 - N / K), (0, 50), [10],
                          method="RK45", t_eval=t, rtol=1e-6, atol=1e-6)   # (2)
            pd.DataFrame({"time": s.t, "N": s.y[0]})
        """},
        compare="table",
        tolerance=1e-12,
        choices=("time_step=0.5 gives the times in the table, from the first time on (t_eval).",
                 "RK45 (SciPy's default method) with the tolerances of R deSolve (1e-6, relative and absolute); "
                 "SciPy's own are looser (1e-3 and 1e-6).",),
        also="simplydata also reads the equations as text, stops at stop_when= (an event) and says when it did.",
    ),
    Entry(
        word="sdata.find_path_over_time", option="exactly=",
        ours="""
            str(sdata.find_path_over_time("dN/dt = r * N", at_start={"N": 10}, between=[0, 5], known={"r": 0.3},
                                          exactly=True))
        """,
        code={"SymPy": """
            import sympy as sp
            t, N = sp.Symbol("t"), sp.Function("N")
            # find_path_over_time("dN/dt = r * N", ..., exactly=True)
            s = sp.dsolve(sp.Eq(N(t).diff(t), sp.Rational(3, 10) * N(t)), N(t), ics={N(0): 10})
            str(sp.simplify(s.rhs))   # (1)
        """},
        compare="value",
        choices=("the answer is written as simply as SymPy can (simplify).",),
        also="simplydata also refuses an answer SymPy can give only as an equation, and says so.",
    ),
    Entry(
        word="nums.turn_into_running_area",
        ours="""
            numbers = sdata.number_list([2, 4, 4, 3, 1])
            numbers.turn_into_running_area(time_step=60)
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import integrate
            values = np.array([2, 4, 4, 3, 1], dtype=float)
            # turn_into_running_area(time_step=60)
            integrate.cumulative_trapezoid(values, dx=60, initial=0)   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("initial=0: the first number becomes 0, so the result is as long as the readings.",),
        also="simplydata also refuses empty values and remembers the time step of the numbers.",
    ),
    Entry(
        word="nums.turn_into_running_area", option="test_method=",
        ours="""
            numbers = sdata.number_list([2, 4, 4, 3, 1])
            numbers.turn_into_running_area(time_step=60, test_method="simpson")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import integrate
            values = np.array([2, 4, 4, 3, 1], dtype=float)
            # turn_into_running_area(time_step=60, test_method="simpson")
            integrate.cumulative_simpson(values, dx=60, initial=0)
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also refuses empty values.",
    ),
    # ------------------------------------------------------------------ numbers
    Entry(
        word="nums.take_cube_root",
        ours="""
            numbers = sdata.number_list([27, -8, 1000, 2])
            numbers.take_cube_root()
        """,
        code={"NumPy": """
            import numpy as np
            values = np.array([27, -8, 1000, 2], dtype=float)
            # take_cube_root()
            np.cbrt(values)
        """},
        compare="value",
        tolerance=1e-15,
        also="simplydata also says that a negative number keeps its minus sign.",
    ),
    Entry(
        word="nums.show_as_fraction",
        ours="""
            numbers = sdata.number_list([0.5, 0.25, 0.3333333333333333, 1.75])
            numbers.show_as_fraction()
        """,
        code={"SymPy": """
            import sympy as sp
            values = [0.5, 0.25, 0.3333333333333333, 1.75]
            # show_as_fraction()
            print("[" + ", ".join(str(sp.nsimplify(v, rational=True)) for v in values) + "]")
        """},
        compare="printed",
        also="simplydata also prints each row of a grid on its own line, and \"empty\" for an empty value.",
    ),
    Entry(
        word="nums.find_coherence_with",
        ours="""
            import numpy as np
            t = 0.01 * np.arange(500)
            numbers = sdata.number_list(np.sin(2 * np.pi * 5 * t))
            numbers.find_coherence_with(np.sin(2 * np.pi * 5 * t + 1) + np.cos(2 * np.pi * 13 * t), time_step=0.01)
        """,
        code={"SciPy": """
            import numpy as np
            import pandas as pd
            from scipy import signal
            t = 0.01 * np.arange(500)
            a, b = np.sin(2 * np.pi * 5 * t), np.sin(2 * np.pi * 5 * t + 1) + np.cos(2 * np.pi * 13 * t)
            # find_coherence_with(other, time_step=0.01)
            f, c = signal.coherence(a, b, fs=100, nperseg=int(500 // 4.5))   # (1)
            pd.DataFrame({"frequency": f, "coherence": c})
        """},
        compare="table",
        tolerance=1e-12,
        choices=("segments of 256 readings (SciPy's default), or, for a recording shorter than 1152 readings, eight "
                 "half-overlapping segments of n / 4.5 readings (as MATLAB mscohere), so the coherence is always an "
                 "average over several segments (with one segment it is 1 at every frequency).",),
        also="simplydata also names the frequency where the two follow each other most closely.",
    ),
    Entry(
        word="nums.take_cosine_transform",
        ours="""
            numbers = sdata.number_list([1, 2, 3, 4])
            numbers.take_cosine_transform()
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import fft
            values = np.array([1, 2, 3, 4], dtype=float)
            # take_cosine_transform()
            fft.dct(values, type=2, norm="ortho")   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("type 2 (the usual DCT) with orthonormal scaling, so the sum of squares stays the same; SciPy's own "
                 "default has no scaling.",),
        also="simplydata also refuses empty values, and undo() gives the numbers back.",
    ),
    # ------------------------------------------------------------------ grids
    Entry(
        word="grid.get_numbers_at_pairs",
        ours="""
            grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])
            grid.get_numbers_at_pairs(rows=[1, 2, 2], columns=[3, 3, 1])
        """,
        code={"NumPy": """
            import numpy as np
            g = np.array([[3, 5, 2], [8, 6, 4]])
            # get_numbers_at_pairs(rows=[1, 2, 2], columns=[3, 3, 1])
            g[np.array([1, 2, 2]) - 1, np.array([3, 3, 1]) - 1]   # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("positions count from 1, so 1 is taken off before NumPy's indexing (which counts from 0).",),
        also="simplydata also says which words give the rectangle of those rows and columns instead.",
    ),
    Entry(
        word="grid.get_numbers_from_each_row_at",
        ours="""
            grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])
            grid.get_numbers_from_each_row_at(columns=[[2, 1], [3, 3]])
        """,
        code={"NumPy": """
            import numpy as np
            g = np.array([[3, 5, 2], [8, 6, 4]])
            # get_numbers_from_each_row_at(columns=[[2, 1], [3, 3]])
            np.take_along_axis(g, np.array([[2, 1], [3, 3]]) - 1, axis=1)   # (1)
        """},
        compare="value",
        tolerance=0.0,
        choices=("positions count from 1, so 1 is taken off before NumPy's take_along_axis.",),
        also="simplydata also takes one position for each row as a plain list and gives numbers back.",
    ),
    Entry(
        word="grid.find_each_patch_that",
        ours="""
            grid = sdata.number_grid([[1, 8, 9, 2], [0, 7, 1, 1], [6, 0, 0, 9]])
            grid.find_each_patch_that(is_above=5)
        """,
        code={"SciPy": """
            import numpy as np, pandas as pd
            from scipy import ndimage
            g = np.array([[1, 8, 9, 2], [0, 7, 1, 1], [6, 0, 0, 9]], dtype=float)
            # find_each_patch_that(is_above=5)
            labels, n = ndimage.label(g > 5)                                  # (1)
            i = np.arange(1, n + 1)
            c = np.array(ndimage.center_of_mass(g > 5, labels, i))           # (2)
            pd.DataFrame({"patch": i, "cells": ndimage.sum_labels(np.ones_like(g), labels, i).astype(int),
                          "total": ndimage.sum_labels(g, labels, i), "average": ndimage.mean(g, labels, i),
                          "centre row": c[:, 0] + 1, "centre column": c[:, 1] + 1})
        """},
        compare="table",
        tolerance=1e-12,
        choices=("cells that share a side touch (SciPy label's own default); touching=\"corners\" lets a shared "
                 "corner count too.",
                 "the centre of the cells, each counting the same, from 1 (not weighted by the values).",),
        also="simplydata also says how many cells meet the condition, and empty cells are never in a patch.",
    ),
    Entry(
        word="grid.change_size_to",
        ours="""
            grid = sdata.number_grid([[3, 5, 2], [8, 6, 4]])
            grid.change_size_to(rows=4, columns=6)
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import ndimage
            g = np.array([[3, 5, 2], [8, 6, 4]], dtype=float)
            # change_size_to(rows=4, columns=6)
            ndimage.zoom(g, (4 / 2, 6 / 3), order=1)   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("straight lines between neighbouring cells (order=1); SciPy zoom's own default is a cubic spline "
                 "(order=3), which can overshoot the numbers.",),
        also="simplydata also prints the size before and after, and refuses empty cells.",
    ),
    Entry(
        word="grid.rotate",
        ours="""
            grid = sdata.number_grid([[3, 5, 2, 1], [8, 6, 4, 7], [1, 1, 2, 3], [9, 0, 5, 2]])
            grid.rotate(by_degrees=30)
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import ndimage
            g = np.array([[3, 5, 2, 1], [8, 6, 4, 7], [1, 1, 2, 3], [9, 0, 5, 2]], dtype=float)
            # rotate(by_degrees=30)
            ndimage.rotate(g, 30, reshape=False, order=1, mode="constant", cval=np.nan)   # (1) (2)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the grid keeps its size (reshape=False) and straight lines between neighbouring cells (order=1).",
                 "cells that come from outside the old grid are empty (cval=nan), not 0 as in SciPy's default.",),
        also="simplydata also says how many cells became empty.",
    ),
    Entry(
        word="grid.take_matrix_exp",
        ours="""
            grid = sdata.number_grid([[-0.5, 0.5], [0.2, -0.2]])
            grid.take_matrix_exp()
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import linalg
            g = np.array([[-0.5, 0.5], [0.2, -0.2]])
            # take_matrix_exp()
            linalg.expm(g)
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also says why this is not take_exp, and refuses a grid that is not square.",
    ),
    Entry(
        word="grid.find_null_space",
        ours="""
            grid = sdata.number_grid([[1, 2, 3], [2, 4, 6]])
            grid.find_null_space()
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import linalg
            g = np.array([[1, 2, 3], [2, 4, 6]], dtype=float)
            # find_null_space()
            linalg.null_space(g)
        """},
        compare="value",
        tolerance=1e-12,
        also="simplydata also says how many directions there are, or that only zero goes to zero.",
    ),
    # ------------------------------------------------------------------ tables (SciPy spatial)
    Entry(
        word="table.find_nearest_rows_to",
        data="stations",
        ours="""
            table = sdata.get_example("stations")
            table.find_nearest_rows_to({"east": 4000, "north": 1000}, how_many=3)
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy.spatial import KDTree
            df = pd.read_csv("stations.csv")
            # find_nearest_rows_to({"east": 4000, "north": 1000}, how_many=3)
            gaps, rows = KDTree(df[["east", "north"]].to_numpy()).query([4000, 1000], k=3)   # (1)
            df.iloc[rows].assign(distance=gaps)
        """},
        compare="table",
        tolerance=1e-12,
        choices=("the straight-line (Euclidean) distance in the columns given, nearest first.",),
        also="simplydata also leaves out rows with an empty cell in those columns, with a note, and within= gives "
             "every row up to a distance.",
    ),
    Entry(
        word="table.find_distances_to_rows_of",
        data="stations",
        ours="""
            table = sdata.get_example("stations")
            other = sdata.get_example("stations")
            table.keep_first_rows(3)
            other.keep_last_rows(2)
            table.find_distances_to_rows_of(other, using=["east", "north"], names="station")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy.spatial import distance
            df = pd.read_csv("stations.csv")
            a, b = df.head(3), df.tail(2)
            # find_distances_to_rows_of(other, using=["east", "north"], names="station")
            d = distance.cdist(a[["east", "north"]], b[["east", "north"]], metric="euclidean")   # (1)
            out = pd.DataFrame(d, columns=b["station"].tolist())
            out.insert(0, "station", a["station"].tolist())
            out
        """},
        compare="table",
        tolerance=1e-12,
        choices=("the straight-line (Euclidean) distance; test_method= takes \"manhattan\", \"chebyshev\", "
                 "\"bray-curtis\", \"canberra\" and \"cosine\".",),
        also="simplydata also labels the rows and columns with names= and leaves out rows with empty cells.",
    ),
    Entry(
        word="table.find_fence_around",
        data="stations",
        ours="""
            table = sdata.get_example("stations")
            table.find_fence_around(x="east", y="north")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy.spatial import ConvexHull
            df = pd.read_csv("stations.csv")
            # find_fence_around(x="east", y="north")
            hull = ConvexHull(df[["east", "north"]].to_numpy())   # (1)
            df.iloc[hull.vertices]
        """},
        compare="table",
        tolerance=1e-12,
        choices=("the corners in SciPy's (Qhull's) order, going round anticlockwise; R chull() goes round clockwise.",),
        also="simplydata also prints the number of corners, the area inside (hull.volume) and the length of the "
             "fence (hull.area) under their plain names.",
    ),
]
