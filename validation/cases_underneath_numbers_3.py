"""Numbers phase, batch 3: the new words on real data and their formulas against answers worked out by hand.

cases_underneath.py loads this file and adds cases(Case) to the study. The words on numbers, grids and tables run on
the study's own real data: AirPassengers (a 12 x 12 grid of years by months), NIST's Michelson measurements, the
Seatbelts series, the level of Lake Huron, Fisher's iris data and the meuse soil samples (places in metres). Each is
compared with the parent package (NumPy, SciPy) and, where base R or R's Matrix package does the same, with R.

The formula words (SymPy), areas, volumes and paths over time have no data by nature: a formula is the input. Their
cases are checked against the answer worked out by hand from the formula (a closed form), against SymPy or SciPy
directly, and against R where base R does the same (D(), integrate(), polyroot()).
"""

from __future__ import annotations

import math
import textwrap

CLOSED_FORM = "exact: worked out by hand from the formula"
AIR_GRID = "grid = sdata.number_grid(np.asarray(data['passengers'], dtype=float).reshape(12, 12).tolist())\n"
AIR_NUMPY = "g = np.asarray(data['passengers'], dtype=float).reshape(12, 12)\n"
AIR_R = "g <- matrix(as.numeric(passengers), nrow = 12, byrow = TRUE)\n"
IRIS = '["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]'
PRINTED = """
    import contextlib
    import io
    from fractions import Fraction
    shown = io.StringIO()
    with contextlib.redirect_stdout(shown):
        {call}
    printed = [float(Fraction(t)) for t in shown.getvalue().split("]")[0].strip("[ \\n").split(", ")]
"""


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(p).strip("\n") for p in parts if p)


def _logistic(t: float, n0: float = 10.0, r: float = 0.3, k: float = 1000.0) -> float:
    """The closed form of dN/dt = r N (1 - N / K): N(t) = K / (1 + (K - N0) / N0 * exp(-r t))."""
    return k / (1 + (k - n0) / n0 * math.exp(-r * t))


def cases(Case):
    def closed(word, title, ours, published, parent="", label="", r="", option="", tolerance=1e-12):
        return Case(word, title, "closed form (no data)", "closed form", ours=_code(ours), published=published,
                    parent=_code(parent), parent_label=label, parent_tolerance=tolerance, r=_code(r),
                    r_tolerance=1e-9, option=option)

    return [
        # ---------------------------------------------------------------- formulas (SymPy)
        closed("sdata.formula", "(x + 2)^2 - 4 read as a formula, at x = 1.5",
               """
                   formula = sdata.formula("(x + 2)**2 - 4")
                   {"at 1.5": formula.find_value_at(x=1.5)}
               """, {"at 1.5": (8.25, 1e-15, CLOSED_FORM + ": 3.5^2 - 4")},
               """
                   import sympy as sp
                   from sympy.parsing.sympy_parser import parse_expr
                   x = sp.Symbol("x")
                   {"at 1.5": float(parse_expr("(x + 2)**2 - 4", local_dict={"x": x}).subs(x, sp.Rational(3, 2)))}
               """, "SymPy parse_expr",
               r="""
                   list(`at 1.5` = eval(parse(text = "(x + 2)^2 - 4"), list(x = 1.5)))
               """),
        closed("f.make_simpler", "(x^2 - 1) / (x - 1) is x + 1: the simpler formula at x = 3 and x = 1",
               """
                   formula = sdata.formula("(x**2 - 1) / (x - 1)")
                   formula.make_simpler()
                   {"at 3": formula.find_value_at(x=3), "at 1": formula.find_value_at(x=1)}
               """, {"at 3": (4.0, 1e-15, CLOSED_FORM), "at 1": (2.0, 1e-15, CLOSED_FORM + ": the gap at 1 is gone")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   g = sp.simplify((x**2 - 1) / (x - 1))
                   {"at 3": float(g.subs(x, 3)), "at 1": float(g.subs(x, 1))}
               """, "SymPy simplify"),
        closed("f.turn_into_sum", "(x + 2)^2 - 4 multiplied out: x^2 + 4x has two terms",
               """
                   formula = sdata.formula("(x + 2)**2 - 4")
                   formula.turn_into_sum()
                   {"terms": str(formula).count("+") + 1, "at 2": formula.find_value_at(x=2)}
               """, {"terms": (2.0, 0.0, CLOSED_FORM + ": x^2 + 4x"), "at 2": (12.0, 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   g = sp.expand((x + 2)**2 - 4)
                   {"terms": len(g.args), "at 2": float(g.subs(x, 2))}
               """, "SymPy expand"),
        closed("f.turn_into_product", "x^2 + 4x as a product: x (x + 4), two factors",
               """
                   formula = sdata.formula("x**2 + 4*x")
                   formula.turn_into_product()
                   {"factors": str(formula).count("*") + 1, "at 3": formula.find_value_at(x=3)}
               """, {"factors": (2.0, 0.0, CLOSED_FORM + ": x (x + 4)"), "at 3": (21.0, 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   g = sp.factor(x**2 + 4*x)
                   {"factors": len(g.args), "at 3": float(g.subs(x, 3))}
               """, "SymPy factor"),
        closed("f.find_slope_formula", "the slope of x^3 - 2x is 3x^2 - 2: at x = 2 it is 10",
               """
                   slope = sdata.formula("x**3 - 2*x").find_slope_formula()
                   {"at 2": slope.find_value_at(x=2), "at -1.5": slope.find_value_at(x=-1.5)}
               """, {"at 2": (10.0, 1e-15, CLOSED_FORM), "at -1.5": (4.75, 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   d = sp.diff(x**3 - 2*x, x)
                   {"at 2": float(d.subs(x, 2)), "at -1.5": float(d.subs(x, sp.Rational(-3, 2)))}
               """, "SymPy diff",
               r="""
                   d <- D(expression(x^3 - 2 * x), "x")
                   list(`at 2` = eval(d, list(x = 2)), `at -1.5` = eval(d, list(x = -1.5)))
               """),
        closed("f.find_area_formula", "the area formula of x^3 - 2x is x^4/4 - x^2: at x = 3 it is 11.25",
               """
                   area = sdata.formula("x**3 - 2*x").find_area_formula()
                   {"at 3": area.find_value_at(x=3), "at 0": area.find_value_at(x=0)}
               """, {"at 3": (11.25, 1e-15, CLOSED_FORM), "at 0": (0.0, 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   a = sp.integrate(x**3 - 2*x, x)
                   {"at 3": float(a.subs(x, 3)), "at 0": float(a.subs(x, 0))}
               """, "SymPy integrate",
               r="""
                   list(`at 3` = integrate(function(x) x^3 - 2 * x, 0, 3)$value)
               """),
        closed("f.find_value_at", "x^3 - 2x at x = 2.5, and at four values at once",
               """
                   formula = sdata.formula("x**3 - 2*x")
                   many = formula.find_value_at(x=[0, 1, 2, 3])
                   {"at 2.5": formula.find_value_at(x=2.5), "total at 0 to 3": many.find_total()}
               """, {"at 2.5": (10.625, 1e-15, CLOSED_FORM), "total at 0 to 3": (24.0, 1e-12, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   g = sp.lambdify(x, x**3 - 2*x, "numpy")
                   {"at 2.5": float((x**3 - 2*x).subs(x, sp.Rational(5, 2))), "total at 0 to 3": g(np.arange(4)).sum()}
               """, "SymPy subs and lambdify",
               r="""
                   f <- function(x) x^3 - 2 * x
                   list(`at 2.5` = f(2.5), `total at 0 to 3` = sum(f(0:3)))
               """),
        closed("f.put_in", "x^2 with x = y + 1 is (y + 1)^2: at y = 2 it is 9",
               """
                   g = sdata.formula("x**2").put_in(x="y + 1")
                   {"at 2": g.find_value_at(y=2), "at -1": g.find_value_at(y=-1)}
               """, {"at 2": (9.0, 1e-15, CLOSED_FORM), "at -1": (0.0, 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   x, y = sp.symbols("x y")
                   g = (x**2).subs(x, y + 1)
                   {"at 2": float(g.subs(y, 2)), "at -1": float(g.subs(y, -1))}
               """, "SymPy subs"),
        closed("f.show_as_latex", "x^3 - 2x as LaTeX: x^{3} - 2 x",
               """
                   import contextlib, io
                   with contextlib.redirect_stdout(io.StringIO()):
                       text = sdata.formula("x**3 - 2*x").show_as_latex()
                   {"is x^{3} - 2 x": float(text == "x^{3} - 2 x")}
               """, {"is x^{3} - 2 x": (1.0, 0.0, CLOSED_FORM + " (the usual way to write it in LaTeX)")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"is x^{3} - 2 x": float(sp.latex(x**3 - 2*x) == "x^{3} - 2 x")}
               """, "SymPy latex", tolerance=0.0),
        closed("f.find_limit_as", "sin(x) / x as x goes to 0 is 1; (1 + 1/x)^x as x goes to infinity is e",
               """
                   {"sin(x) / x": sdata.formula("sin(x) / x").find_limit_as("x", goes_to=0),
                    "(1 + 1/x)^x": sdata.formula("(1 + 1/x)**x").find_limit_as("x", goes_to="infinity")}
               """, {"sin(x) / x": (1.0, 1e-15, CLOSED_FORM), "(1 + 1/x)^x": (math.e, 1e-15, CLOSED_FORM + ": e")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"sin(x) / x": float(sp.limit(sp.sin(x) / x, x, 0, dir="+-")),
                    "(1 + 1/x)^x": float(sp.limit((1 + 1 / x)**x, x, sp.oo))}
               """, "SymPy limit"),
        closed("f.find_taylor_series", "exp(x) near 0 up to the power 4, at x = 1: 65/24",
               """
                   s = sdata.formula("exp(x)").find_taylor_series(around=0, up_to_power=4)
                   {"at 1": s.find_value_at(x=1), "at 0.5": s.find_value_at(x=0.5)}
               """, {"at 1": (65 / 24, 1e-15, CLOSED_FORM + ": 1 + 1 + 1/2 + 1/6 + 1/24"),
                     "at 0.5": (1 + 0.5 + 0.125 + 0.5 ** 3 / 6 + 0.5 ** 4 / 24, 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   s = sp.series(sp.exp(x), x, 0, n=5).removeO()
                   {"at 1": float(s.subs(x, 1)), "at 0.5": float(s.subs(x, sp.Rational(1, 2)))}
               """, "SymPy series"),
        closed("sdata.solve", "x^2 = 2 exactly: x = -sqrt(2) and sqrt(2)",
               """
                   found = sdata.solve("x**2 = 2", exactly=True)
                   {"smaller": found.get_cell_at(row=1, column="x"), "bigger": found.get_cell_at(row=2, column="x")}
               """, {"smaller": (-math.sqrt(2), 1e-15, CLOSED_FORM), "bigger": (math.sqrt(2), 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   s = sorted(sp.solve(sp.Eq(x**2, 2), x), key=float)
                   {"smaller": float(s[0]), "bigger": float(s[1])}
               """, "SymPy solve",
               r="""
                   z <- sort(Re(polyroot(c(-2, 0, 1))))
                   list(smaller = z[1], bigger = z[2])
               """, option="exactly="),
        # ---------------------------------------------------------------- areas, volumes and paths (SciPy)
        closed("sdata.find_area_under", "the area under exp(-x^2) from 0 to infinity: sqrt(pi) / 2",
               """
                   {"area": sdata.find_area_under("exp(-x**2)", between=[0, "infinity"]),
                    "sine": sdata.find_area_under("sin(x)", between=[0, np.pi])}
               """, {"area": (math.sqrt(math.pi) / 2, 1e-12, CLOSED_FORM),
                     "sine": (2.0, 1e-12, CLOSED_FORM + ": the area under one arch of the sine is 2")},
               """
                   from scipy import integrate
                   {"area": integrate.quad(lambda x: np.exp(-x**2), 0, np.inf)[0],
                    "sine": integrate.quad(np.sin, 0, np.pi)[0]}
               """, "SciPy integrate.quad",
               r="""
                   list(area = integrate(function(x) exp(-x^2), 0, Inf, rel.tol = 1e-12)$value,
                        sine = integrate(sin, 0, pi, rel.tol = 1e-12)$value)
               """),
        closed("sdata.find_area_under", "test_method=\"gauss\": the area under x^4 from 0 to 2 is 32 / 5",
               """
                   {"area": sdata.find_area_under("x**4", between=[0, 2], test_method="gauss")}
               """, {"area": (6.4, 1e-12, CLOSED_FORM)},
               """
                   from scipy import integrate
                   {"area": integrate.fixed_quad(lambda x: x**4, 0, 2, n=5)[0]}
               """, "SciPy integrate.fixed_quad", option="test_method="),
        closed("sdata.find_area_under", "exactly=True: the area under exp(-x^2) from 0 to infinity is sqrt(pi) / 2",
               """
                   exact = sdata.find_area_under("exp(-x**2)", between=[0, "infinity"], exactly=True)
                   {"area": exact.find_value_at()}
               """, {"area": (math.sqrt(math.pi) / 2, 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"area": float(sp.integrate(sp.exp(-x**2), (x, 0, sp.oo)))}
               """, "SymPy integrate", option="exactly="),
        closed("sdata.find_volume_under", "the volume under x y^2 over 0..1 by 0..2 is 4 / 3",
               """
                   {"volume": sdata.find_volume_under("x * y**2", between={"x": [0, 1], "y": [0, 2]}),
                    "three letters": sdata.find_volume_under("x + y + z", between={"x": [0, 1], "y": [0, 1],
                                                                                    "z": [0, 1]})}
               """, {"volume": (4 / 3, 1e-12, CLOSED_FORM), "three letters": (1.5, 1e-12, CLOSED_FORM)},
               """
                   from scipy import integrate
                   {"volume": integrate.dblquad(lambda y, x: x * y**2, 0, 1, 0, 2)[0],
                    "three letters": integrate.tplquad(lambda z, y, x: x + y + z, 0, 1, 0, 1, 0, 1)[0]}
               """, "SciPy integrate.dblquad and tplquad",
               r="""
                   inner <- function(x) sapply(x, function(a) integrate(function(y) a * y^2, 0, 2, rel.tol = 1e-12)$value)
                   list(volume = integrate(inner, 0, 1, rel.tol = 1e-12)$value)
               """),
        closed("sdata.find_path_over_time", "logistic growth from 10 towards 1000 at rate 0.3, against its closed form",
               """
                   p = sdata.find_path_over_time("dN/dt = r * N * (1 - N / K)", at_start={"N": 10}, between=[0, 50],
                                                 known={"r": 0.3, "K": 1000}, time_step=0.5)
                   {"at 10": p.get_cell_at(row=21, column="N"), "at 50": p.get_cell_at(row=101, column="N")}
               """, {"at 10": (_logistic(10), 1e-3, CLOSED_FORM + ": K / (1 + (K - N0) / N0 exp(-r t)), within the "
                               "solver's tolerance"),
                     "at 50": (_logistic(50), 1e-3, CLOSED_FORM)},
               """
                   from scipy.integrate import solve_ivp
                   s = solve_ivp(lambda t, N: 0.3 * N * (1 - N / 1000), (0, 50), [10], t_eval=0.5 * np.arange(101),
                                 rtol=1e-6, atol=1e-6)
                   {"at 10": s.y[0][20], "at 50": s.y[0][100]}
               """, "SciPy integrate.solve_ivp (RK45)"),
        closed("sdata.find_path_over_time", "exactly=True: dN/dt = 0.3 N from 10 is 10 exp(0.3 t); at t = 5",
               """
                   path = sdata.find_path_over_time("dN/dt = r * N", at_start={"N": 10}, between=[0, 5],
                                                    known={"r": 0.3}, exactly=True)
                   {"at 5": path.find_value_at(t=5)}
               """, {"at 5": (10 * math.exp(1.5), 1e-12, CLOSED_FORM)},
               """
                   import sympy as sp
                   t, N = sp.Symbol("t"), sp.Function("N")
                   s = sp.dsolve(sp.Eq(N(t).diff(t), sp.Rational(3, 10) * N(t)), N(t), ics={N(0): 10})
                   {"at 5": float(s.rhs.subs(t, 5))}
               """, "SymPy dsolve", option="exactly="),
        # ---------------------------------------------------------------- numbers on real data
        Case("nums.turn_into_running_area", "AirPassengers: passengers so far, month by month (trapezoid rule)",
             "AirPassengers", "real data",
             ours="""
                 numbers = sdata.number_list(data["passengers"].tolist())
                 numbers.turn_into_running_area(time_step=1)
                 {"after a year": numbers.get_number_at(13), "whole area": numbers.get_number_at("last")}
             """,
             parent="""
                 from scipy import integrate
                 a = integrate.cumulative_trapezoid(data["passengers"].to_numpy(dtype=float), dx=1, initial=0)
                 {"after a year": a[12], "whole area": a[-1]}
             """, parent_label="SciPy integrate.cumulative_trapezoid", parent_tolerance=1e-12,
             r="""
                 x <- as.numeric(passengers); n <- length(x)
                 a <- c(0, cumsum((x[-1] + x[-n]) / 2))
                 list(`after a year` = a[13], `whole area` = a[n])
             """, r_tolerance=1e-12),
        Case("nums.turn_into_running_area", "AirPassengers: passengers so far by Simpson's rule",
             "AirPassengers", "real data", option="test_method=",
             ours="""
                 numbers = sdata.number_list(data["passengers"].tolist())
                 numbers.turn_into_running_area(time_step=1, test_method="simpson")
                 {"after a year": numbers.get_number_at(13), "whole area": numbers.get_number_at("last")}
             """,
             parent="""
                 from scipy import integrate
                 a = integrate.cumulative_simpson(data["passengers"].to_numpy(dtype=float), dx=1, initial=0)
                 {"after a year": a[12], "whole area": a[-1]}
             """, parent_label="SciPy integrate.cumulative_simpson", parent_tolerance=1e-12),
        Case("nums.take_cube_root", "the cube roots of Michelson's measurements less their average (some negative)",
             "NIST Michelso", "real data",
             ours="""
                 numbers = sdata.number_list((data["y"] - 299.85).tolist())
                 numbers.take_cube_root()
                 {"total": numbers.find_total(), "smallest": numbers.find_smallest()}
             """,
             parent="""
                 r = np.cbrt(data["y"].to_numpy() - 299.85)
                 {"total": r.sum(), "smallest": r.min()}
             """, parent_label="NumPy cbrt", parent_tolerance=1e-12,
             r="""
                 v <- y - 299.85
                 r <- sign(v) * abs(v)^(1 / 3)
                 list(total = sum(r), smallest = min(r))
             """, r_tolerance=1e-12),
        Case("nums.show_as_fraction", "Michelson's first measurements as fractions give the numbers back exactly",
             "NIST Michelso", "real data",
             ours=textwrap.dedent(PRINTED).format(
                 call='sdata.number_list(data["y"].head(10).tolist()).show_as_fraction()')
             + textwrap.dedent("""
                 {"total": sum(printed), "shown": len(printed)}
             """),
             parent="""
                 import sympy as sp
                 shown = [sp.nsimplify(v, rational=True) for v in data["y"].head(10)]
                 {"total": float(sum(shown)), "shown": len(shown)}
             """, parent_label="SymPy nsimplify", parent_tolerance=1e-15,
             r="""
                 list(total = sum(y[1:10]), shown = 10)
             """, r_tolerance=1e-12),
        Case("nums.find_coherence_with", "Seatbelts: drivers killed or injured against drivers killed, by frequency",
             "Seatbelts", "real data",
             ours="""
                 c = sdata.number_list(data["drivers"].tolist()).find_coherence_with(data["DriversKilled"].tolist(),
                                                                                    time_step=1 / 12)
                 {"rows": c.count_rows(), "at a year": c.get_cell_at(row=4, column="coherence"),
                  "average": c.get_column("coherence").find_average()}
             """,
             parent="""
                 from scipy import signal
                 f, c = signal.coherence(data["drivers"].to_numpy(dtype=float), data["DriversKilled"].to_numpy(dtype=float),
                                         fs=12, nperseg=int(len(data) // 4.5))
                 {"rows": len(f), "at a year": c[3], "average": c.mean()}
             """, parent_label="SciPy signal.coherence (eight half-overlapping segments)", parent_tolerance=1e-12),
        Case("nums.take_cosine_transform", "the level of Lake Huron, 1875-1972, as cosine waves",
             "Lake Huron", "real data",
             ours="""
                 numbers = sdata.number_list(data["level"].tolist())
                 numbers.take_cosine_transform()
                 {"first": numbers.get_number_at(1), "second": numbers.get_number_at(2),
                  "sum of squares": (numbers ** 2).find_total()}
             """,
             parent="""
                 from scipy import fft
                 d = fft.dct(data["level"].to_numpy(dtype=float), type=2, norm="ortho")
                 {"first": d[0], "second": d[1], "sum of squares": (d ** 2).sum()}
             """, parent_label="SciPy fft.dct (type 2, orthonormal)", parent_tolerance=1e-12,
             r="""
                 n <- length(level)
                 list(first = sum(level) / sqrt(n), `sum of squares` = sum(level^2))
             """, r_tolerance=1e-12),
        # ---------------------------------------------------------------- grids on real data
        Case("grid.get_numbers_at_pairs", "AirPassengers as 12 years x 12 months: July of 1949, 1955 and 1960",
             "AirPassengers", "real data",
             ours=_code(AIR_GRID, """
                 p = grid.get_numbers_at_pairs(rows=[1, 7, 12], columns=[7, 7, 7])
                 {"1949": p.get_number_at(1), "1955": p.get_number_at(2), "1960": p.get_number_at(3)}
             """),
             parent=_code(AIR_NUMPY, """
                 p = g[[0, 6, 11], [6, 6, 6]]
                 {"1949": p[0], "1955": p[1], "1960": p[2]}
             """), parent_label="NumPy indexing with pairs (from 0)", parent_tolerance=0.0,
             r=_code(AIR_R, """
                 p <- g[cbind(c(1, 7, 12), c(7, 7, 7))]
                 list(`1949` = p[1], `1955` = p[2], `1960` = p[3])
             """), r_tolerance=0.0),
        Case("grid.get_numbers_from_each_row_at", "AirPassengers: June to August of every year, row by row",
             "AirPassengers", "real data",
             ours=_code(AIR_GRID, """
                 summer = grid.get_numbers_from_each_row_at(columns=[[6, 7, 8]] * 12)
                 {"total": summer.find_total(), "1960 August": summer.get_number_at(row=12, column=3)}
             """),
             parent=_code(AIR_NUMPY, """
                 s = np.take_along_axis(g, np.array([[5, 6, 7]] * 12), axis=1)
                 {"total": s.sum(), "1960 August": s[11, 2]}
             """), parent_label="NumPy take_along_axis", parent_tolerance=0.0,
             r=_code(AIR_R, """
                 s <- g[, 6:8]
                 list(total = sum(s), `1960 August` = s[12, 3])
             """), r_tolerance=0.0),
        Case("grid.find_each_patch_that", "AirPassengers: the patches of months above 400 thousand passengers",
             "AirPassengers", "real data",
             ours=_code(AIR_GRID, """
                 p = grid.find_each_patch_that(is_above=400)
                 {"patches": p.count_rows(), "cells": p.get_column("cells").find_total(),
                  "biggest total": p.get_column("total").find_biggest(),
                  "centre rows": p.get_column("centre row").find_total(),
                  "centre columns": p.get_column("centre column").find_total()}
             """),
             parent=_code(AIR_NUMPY, """
                 from scipy import ndimage
                 labels, n = ndimage.label(g > 400)
                 totals = ndimage.sum_labels(g, labels, np.arange(1, n + 1))
                 centres = np.array(ndimage.center_of_mass(g > 400, labels, np.arange(1, n + 1))) + 1
                 {"patches": n, "cells": int((g > 400).sum()), "biggest total": totals.max(),
                  "centre rows": centres[:, 0].sum(), "centre columns": centres[:, 1].sum()}
             """), parent_label="SciPy ndimage.label, sum_labels and center_of_mass (from 1)",
             parent_tolerance=1e-12),
        Case("grid.change_size_to", "AirPassengers' 12 x 12 grid made 24 x 24 (straight lines between cells)",
             "AirPassengers", "real data",
             ours=_code(AIR_GRID, """
                 grid.change_size_to(rows=24, columns=24)
                 {"rows": grid.count_rows(), "total": grid.find_total(), "row 2 column 3": grid.get_number_at(row=2, column=3)}
             """),
             parent=_code(AIR_NUMPY, """
                 from scipy import ndimage
                 z = ndimage.zoom(g, 2, order=1)
                 {"rows": z.shape[0], "total": z.sum(), "row 2 column 3": z[1, 2]}
             """), parent_label="SciPy ndimage.zoom (order 1)", parent_tolerance=1e-12),
        Case("grid.rotate", "AirPassengers' 12 x 12 grid turned by 30 degrees",
             "AirPassengers", "real data",
             ours=_code(AIR_GRID, """
                 grid.rotate(by_degrees=30)
                 {"empty": grid.count_empty_numbers(), "total": grid.find_total()}
             """),
             parent=_code(AIR_NUMPY, """
                 from scipy import ndimage
                 r = ndimage.rotate(g, 30, reshape=False, order=1, mode="constant", cval=np.nan)
                 {"empty": int(np.isnan(r).sum()), "total": np.nansum(r)}
             """), parent_label="SciPy ndimage.rotate (order 1, empty outside)", parent_tolerance=1e-12),
        Case("grid.take_matrix_exp", "the matrix exponential of the correlations of Fisher's iris measurements",
             "iris", "real data",
             ours=f"""
                 grid = sdata.number_grid(data[{IRIS}].corr().to_numpy().tolist())
                 grid.take_matrix_exp()
                 {{"first": grid.get_number_at(row=1, column=1), "corner": grid.get_number_at(row=1, column=4),
                  "total": grid.find_total()}}
             """,
             parent=f"""
                 from scipy import linalg
                 e = linalg.expm(data[{IRIS}].corr().to_numpy())
                 {{"first": e[0, 0], "corner": e[0, 3], "total": e.sum()}}
             """, parent_label="SciPy linalg.expm", parent_tolerance=1e-12,
             r="""
                 e <- as.matrix(Matrix::expm(Matrix::Matrix(cor(cbind(Sepal.Length, Sepal.Width, Petal.Length,
                                                                     Petal.Width)))))
                 list(first = e[1, 1], corner = e[1, 4], total = sum(e))
             """, r_packages=("Matrix",), r_tolerance=1e-9),
        Case("grid.find_null_space", "the 146 directions that the iris measurements (4 x 150) send to zero",
             "iris", "real data",
             ours=f"""
                 grid = sdata.number_grid(data[{IRIS}].to_numpy().T.tolist())
                 n = grid.find_null_space().as_numpy()
                 {{"directions": n.shape[1], "length of each": float(np.mean((n ** 2).sum(axis=0))),
                  "biggest left over": float(np.abs(grid.as_numpy() @ n).max() < 1e-12)}}
             """,
             parent=f"""
                 from scipy import linalg
                 a = data[{IRIS}].to_numpy().T
                 n = linalg.null_space(a)
                 {{"directions": n.shape[1], "length of each": float(np.mean((n ** 2).sum(axis=0))),
                  "biggest left over": float(np.abs(a @ n).max() < 1e-12)}}
             """, parent_label="SciPy linalg.null_space", parent_tolerance=1e-12,
             r="""
                 a <- rbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width)
                 n <- MASS::Null(t(a))
                 list(directions = ncol(n), `length of each` = mean(colSums(n^2)),
                      `biggest left over` = as.numeric(max(abs(a %*% n)) < 1e-12))
             """, r_packages=("MASS",), r_tolerance=1e-12),
        # ---------------------------------------------------------------- tables on real data (meuse)
        Case("table.find_nearest_rows_to", "meuse: the 5 soil samples nearest to the point (179500, 331500)",
             "meuse (sp)", "real data",
             ours="""
                 near = sdata.table(data).find_nearest_rows_to({"x": 179500, "y": 331500}, how_many=5)
                 {"nearest": near.get_cell_at(row=1, column="distance"),
                  "fifth": near.get_cell_at(row=5, column="distance"), "zinc of nearest": near.get_cell_at(row=1, column="zinc")}
             """,
             parent="""
                 from scipy.spatial import KDTree
                 d, i = KDTree(data[["x", "y"]].to_numpy(dtype=float)).query([179500, 331500], k=5)
                 {"nearest": d[0], "fifth": d[4], "zinc of nearest": data["zinc"].iloc[i[0]]}
             """, parent_label="SciPy spatial.KDTree", parent_tolerance=1e-12,
             r="""
                 d <- sqrt((x - 179500)^2 + (y - 331500)^2)
                 o <- order(d)
                 list(nearest = d[o[1]], fifth = d[o[5]], `zinc of nearest` = zinc[o[1]])
             """, r_tolerance=1e-12),
        Case("table.find_distances_to_rows_of", "meuse: the first 5 samples against the last 3, in metres",
             "meuse (sp)", "real data",
             ours="""
                 first, last = sdata.table(data), sdata.table(data)
                 first.keep_first_rows(5)
                 last.keep_last_rows(3)
                 d = first.find_distances_to_rows_of(last, using=["x", "y"])
                 {"row 1 to 153": d.get_cell_at(row=1, column="1"), "row 5 to 155": d.get_cell_at(row=5, column="3"),
                  "total": sum(d.get_column(c).find_total() for c in ["1", "2", "3"])}
             """,
             parent="""
                 from scipy.spatial import distance
                 xy = data[["x", "y"]].to_numpy(dtype=float)
                 d = distance.cdist(xy[:5], xy[-3:])
                 {"row 1 to 153": d[0, 0], "row 5 to 155": d[4, 2], "total": d.sum()}
             """, parent_label="SciPy spatial.distance.cdist", parent_tolerance=1e-12,
             r="""
                 m <- as.matrix(dist(cbind(x, y)))
                 d <- m[1:5, (length(x) - 2):length(x)]
                 list(`row 1 to 153` = d[1, 1], `row 5 to 155` = d[5, 3], total = sum(d))
             """, r_tolerance=1e-12),
        Case("table.find_fence_around", "meuse: the shortest fence around the 155 soil samples (convex hull)",
             "meuse (sp)", "real data",
             ours="""
                 corners = sdata.table(data).find_fence_around(x="x", y="y")
                 {"corners": corners.count_rows(), "x total": corners.get_column("x").find_total(),
                  "zinc total": corners.get_column("zinc").find_total()}
             """,
             parent="""
                 from scipy.spatial import ConvexHull
                 hull = ConvexHull(data[["x", "y"]].to_numpy(dtype=float))
                 {"corners": len(hull.vertices), "x total": data["x"].iloc[hull.vertices].sum(),
                  "zinc total": data["zinc"].iloc[hull.vertices].sum()}
             """, parent_label="SciPy spatial.ConvexHull", parent_tolerance=1e-12,
             r="""
                 h <- chull(x, y)
                 list(corners = length(h), `x total` = sum(x[h]), `zinc total` = sum(zinc[h]))
             """, r_tolerance=1e-12),
    ]
