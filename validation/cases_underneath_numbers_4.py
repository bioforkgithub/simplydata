"""Numbers phase, batch 4 (the SymPy words): the new words and options against answers worked out by hand and on
real data.

cases_underneath.py loads this file and adds cases(Case) to the study. The formula words, sums of series, exact
volumes and paths over time have no data by nature (a formula is the input): their cases are checked against the
answer worked out by hand from the formula (a closed form), against SymPy or SciPy directly, and against base R
where it does the same (D(), integrate(), polyroot(), sums). The matrix words of a grid run on the study's real data
(the correlations of Fisher's iris measurements, AirPassengers as 12 years x 12 months, the first iris flowers)
against SciPy or SymPy and base R (det(), solve(), eigen(); MASS::Null).
"""

from __future__ import annotations

import math
import textwrap

CLOSED_FORM = "exact: worked out by hand from the formula"
IRIS = '["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"]'
IRIS_R = "cor(cbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width))"
AIR_GRID = "grid = sdata.number_grid(np.asarray(data['passengers'], dtype=float).reshape(12, 12).tolist())\n"
AIR_NUMPY = "g = np.asarray(data['passengers'], dtype=float).reshape(12, 12)\n"
AIR_R = "g <- matrix(as.numeric(passengers), nrow = 12, byrow = TRUE)\n"
# sqrt(2) to 50 significant digits (OEIS A002193)
ROOT_2 = "1.4142135623730950488016887242096980785696718753769"


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(p).strip("\n") for p in parts if p)


def _damped(t: float, k: float = 4.0, c: float = 0.5) -> tuple[float, float]:
    """x and dx/dt of d2x/dt2 = -k x - c dx/dt from x = 1, dx/dt = 0 (an underdamped spring), worked out by hand."""
    w = math.sqrt(k - c * c / 4)
    a = c / (2 * w)
    e = math.exp(-c * t / 2)
    x = e * (math.cos(w * t) + a * math.sin(w * t))
    speed = e * (-(c / 2) * (math.cos(w * t) + a * math.sin(w * t)) + (-w * math.sin(w * t) + a * w * math.cos(w * t)))
    return x, speed


def _log_series(power: int, last: int = 10**7) -> float:
    """1/(k log(k)**power) from 2 on, worked out by hand: the terms up to last, then the integral of the rest
    (1/((power - 1) log(last)**(power - 1))) less half the last term, as the Euler-Maclaurin rule gives."""
    import numpy as np

    k = np.arange(2, last + 1, dtype=float)
    return float(np.sum(1 / (k * np.log(k) ** power)) + 1 / ((power - 1) * math.log(last) ** (power - 1))
                 - 1 / (2 * last * math.log(last) ** power))


def cases(Case):
    def closed(word, title, ours, published, parent="", label="", r="", option="", tolerance=1e-12,
               r_tolerance=1e-9):
        return Case(word, title, "closed form (no data)", "closed form", ours=_code(ours), published=published,
                    parent=_code(parent), parent_label=label, parent_tolerance=tolerance, r=_code(r),
                    r_tolerance=r_tolerance, option=option)

    return [
        # ---------------------------------------------------------------- formula words and options (SymPy)
        closed("f.find_slope_formula", "how_many_times=3: the third slope of sin(x) is -cos(x)",
               """
                   s = sdata.formula("sin(x)").find_slope_formula(how_many_times=3)
                   {"at 1": s.find_value_at(x=1), "at 0": s.find_value_at(x=0)}
               """, {"at 1": (-math.cos(1), 1e-15, CLOSED_FORM), "at 0": (-1.0, 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   d = sp.diff(sp.sin(x), x, 3)
                   {"at 1": float(d.subs(x, 1)), "at 0": float(d.subs(x, 0))}
               """, "SymPy diff",
               r="""
                   d <- D(D(D(expression(sin(x)), "x"), "x"), "x")
                   list(`at 1` = eval(d, list(x = 1)), `at 0` = eval(d, list(x = 0)))
               """, option="how_many_times="),
        closed("f.find_slope_formula", "for_letter=[\"x\", \"y\"]: the mixed slope of x^2 y^3 is 6 x y^2",
               """
                   s = sdata.formula("x**2 * y**3").find_slope_formula(for_letter=["x", "y"])
                   {"at (2, 1)": s.find_value_at(x=2, y=1), "at (1, 3)": s.find_value_at(x=1, y=3)}
               """, {"at (2, 1)": (12.0, 1e-15, CLOSED_FORM), "at (1, 3)": (54.0, 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   x, y = sp.symbols("x y")
                   d = sp.diff(x**2 * y**3, x, y)
                   {"at (2, 1)": float(d.subs({x: 2, y: 1})), "at (1, 3)": float(d.subs({x: 1, y: 3}))}
               """, "SymPy diff",
               r="""
                   d <- D(D(expression(x^2 * y^3), "x"), "y")
                   list(`at (2, 1)` = eval(d, list(x = 2, y = 1)), `at (1, 3)` = eval(d, list(x = 1, y = 3)))
               """, option="for_letter="),
        closed("f.find_limit_as", "from_side=: |x| / x comes to -1 from below and 1 from above at 0",
               """
                   formula = sdata.formula("abs(x) / x")
                   {"below": formula.find_limit_as("x", goes_to=0, from_side="below"),
                    "above": formula.find_limit_as("x", goes_to=0, from_side="right")}
               """, {"below": (-1.0, 0.0, CLOSED_FORM), "above": (1.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"below": float(sp.limit(sp.Abs(x) / x, x, 0, dir="-")),
                    "above": float(sp.limit(sp.Abs(x) / x, x, 0, dir="+"))}
               """, "SymPy limit (dir)", option="from_side="),
        closed("f.show_as_decimal", "sqrt(2) to 50 digits, as published (OEIS A002193)",
               f"""
                   import contextlib, io
                   with contextlib.redirect_stdout(io.StringIO()):
                       text = sdata.formula("sqrt(2)").show_as_decimal(digits=50)
                   {{"the 50 digits": float(text == "{ROOT_2}"), "digits": len(text.replace(".", ""))}}
               """, {"the 50 digits": (1.0, 0.0, "OEIS A002193: " + ROOT_2),
                     "digits": (50.0, 0.0, "digits=50")},
               f"""
                   import sympy as sp
                   text = str(sp.N(sp.sqrt(2), 50))
                   {{"the 50 digits": float(text == "{ROOT_2}"), "digits": len(text.replace(".", ""))}}
               """, "SymPy N", tolerance=0.0),
        closed("f.group_by_powers_of", "(a + x)(b + x) - x grouped by x: x^2 + x (a + b - 1) + a b",
               """
                   formula = sdata.formula("(a + x)*(b + x) - x")
                   formula.group_by_powers_of("x")
                   {"terms": len(formula.as_sympy().args), "at a=2, b=3, x=5": formula.find_value_at(a=2, b=3, x=5)}
               """, {"terms": (3.0, 0.0, CLOSED_FORM + ": x**2, x*(a + b - 1) and a*b"),
                     "at a=2, b=3, x=5": (51.0, 1e-15, CLOSED_FORM + ": 7 * 8 - 5")},
               """
                   import sympy as sp
                   a, b, x = sp.symbols("a b x")
                   g = sp.collect(sp.expand((a + x)*(b + x) - x), x)
                   {"terms": len(g.args), "at a=2, b=3, x=5": float(g.subs({a: 2, b: 3, x: 5}))}
               """, "SymPy expand and collect",
               r="""
                   list(`at a=2, b=3, x=5` = eval(expression((a + x) * (b + x) - x), list(a = 2, b = 3, x = 5)))
               """),
        closed("f.turn_into_partial_fractions", "(3x + 5) / ((x + 1)(x + 2)) is 2/(x + 1) + 1/(x + 2)",
               """
                   formula = sdata.formula("(3*x + 5) / ((x + 1)*(x + 2))")
                   formula.turn_into_partial_fractions()
                   {"fractions": len(formula.as_sympy().args), "at 3": formula.find_value_at(x=3)}
               """, {"fractions": (2.0, 0.0, CLOSED_FORM), "at 3": (0.7, 1e-15, CLOSED_FORM + ": 2/4 + 1/5")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   g = sp.apart((3*x + 5) / ((x + 1)*(x + 2)), x)
                   {"fractions": len(g.args), "at 3": float(g.subs(x, 3))}
               """, "SymPy apart",
               r="""
                   list(`at 3` = eval(expression((3 * x + 5) / ((x + 1) * (x + 2))), list(x = 3)))
               """),
        closed("f.as_sympy", "the SymPy expression of (x + 2)^2 - 4 is SymPy's own, at x = 1.5",
               """
                   expr = sdata.formula("(x + 2)**2 - 4").as_sympy()
                   {"at 1.5": float(expr.subs("x", 1.5)), "letters": len(expr.free_symbols)}
               """, {"at 1.5": (8.25, 1e-15, CLOSED_FORM), "letters": (1.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   from sympy.parsing.sympy_parser import parse_expr
                   e = parse_expr("(x + 2)**2 - 4", local_dict={"x": sp.Symbol("x")})
                   {"at 1.5": float(e.subs("x", 1.5)), "letters": len(e.free_symbols)}
               """, "SymPy parse_expr"),
        closed("sdata.formula", "letters_are=: with k and t positive, sqrt(k^2) + log(k t) is k + log(k) + log(t)",
               """
                   formula = sdata.formula("sqrt(k**2) + log(k*t)", letters_are={"k": "positive", "t": "positive"})
                   formula.turn_into_sum()
                   {"terms": len(formula.as_sympy().args), "at k=2, t=3": formula.find_value_at(k=2, t=3)}
               """, {"terms": (3.0, 0.0, CLOSED_FORM), "at k=2, t=3": (2 + math.log(6), 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   k, t = sp.symbols("k t", positive=True)
                   g = sp.expand(sp.sqrt(k**2) + sp.log(k*t))
                   {"terms": len(g.args), "at k=2, t=3": float(g.subs({k: 2, t: 3}))}
               """, "SymPy expand with positive Symbols",
               r="""
                   list(`at k=2, t=3` = sqrt(2^2) + log(2 * 3))
               """, option="letters_are="),
        closed("sdata.solve", "for_letter=\"T\": p V = n R T gives T = p V / (n R); one mole at 101325 Pa in 22.4 L",
               """
                   found = sdata.solve("p*V = n*R*T", for_letter="T", exactly=True)
                   T = sdata.formula(found.get_cell_at(row=1, column="T exactly"))
                   {"T": T.find_value_at(p=101325, V=0.0224, n=1, R=8.314)}
               """, {"T": (101325 * 0.0224 / 8.314, 1e-12, CLOSED_FORM)},
               """
                   import sympy as sp
                   p, V, n, R, T = sp.symbols("p V n R T")
                   s = sp.solve(sp.Eq(p*V, n*R*T), T, dict=True)[0][T]
                   {"T": float(s.subs({p: 101325, V: sp.Rational(224, 10000), n: 1, R: sp.Rational(8314, 1000)}))}
               """, "SymPy solve",
               r="""
                   list(T = 101325 * 0.0224 / (1 * 8.314))
               """, option="for_letter="),
        closed("sdata.solve", "letters_are=: c^2 = 4 with c positive has the one solution c = 2",
               """
                   found = sdata.solve("c**2 = 4", exactly=True, letters_are={"c": "positive"})
                   {"solutions": found.count_rows(), "c": found.get_cell_at(row=1, column="c")}
               """, {"solutions": (1.0, 0.0, CLOSED_FORM), "c": (2.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   c = sp.Symbol("c", positive=True)
                   s = sp.solve(sp.Eq(c**2, 4), c, dict=True)
                   {"solutions": len(s), "c": float(s[0][c])}
               """, "SymPy solve with a positive Symbol", option="letters_are="),
        closed("sdata.solve", "a rule: x^2 - 4 > 0 holds for x < -2 and x > 2 (the roots of x^2 - 4)",
               """
                   found = sdata.solve("x**2 - 4 > 0", exactly=True)
                   {"pieces": found.count_rows(), "first ends at": found.get_cell_at(row=1, column="to"),
                    "second starts at": found.get_cell_at(row=2, column="from")}
               """, {"pieces": (2.0, 0.0, CLOSED_FORM), "first ends at": (-2.0, 0.0, CLOSED_FORM),
                     "second starts at": (2.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   s = sp.solveset(x**2 - 4 > 0, x, sp.S.Reals)
                   {"pieces": len(s.args), "first ends at": float(s.args[0].end), "second starts at": float(s.args[1].start)}
               """, "SymPy solveset over the real numbers",
               r="""
                   z <- sort(Re(polyroot(c(-4, 0, 1))))
                   list(`first ends at` = z[1], `second starts at` = z[2])
               """, option="exactly=True with a rule"),
        closed("sdata.find_sum_of_series", "1 / k^2 from 1 to infinity is pi^2 / 6 (Euler, the Basel problem)",
               """
                   {"sum": sdata.find_sum_of_series("1/k**2", between=[1, "infinity"]).find_value_at(),
                    "no closed form": sdata.find_sum_of_series("1/(k**3 + k + 1)", between=[1, "infinity"])}
               """, {"sum": (math.pi ** 2 / 6, 1e-15, CLOSED_FORM + ": pi^2 / 6")},
               """
                   import sympy as sp
                   k = sp.Symbol("k", integer=True)
                   {"sum": float(sp.summation(1/k**2, (k, 1, sp.oo))),
                    "no closed form": float(sp.Sum(1/(k**3 + k + 1), (k, 1, sp.oo)).evalf())}
               """, "SymPy summation and Sum.evalf",
               r="""
                   k <- 1:1e6
                   list(sum = sum(1 / k^2) + 1 / 1e6, `no closed form` = sum(1 / (k^3 + k + 1)))
               """, r_tolerance=1e-9),
        closed("sdata.find_sum_of_series", "k from 1 to n is n (n + 1) / 2 (Gauss); at n = 100 it is 5050",
               """
                   s = sdata.find_sum_of_series("k", between=[1, "n"])
                   {"at 100": s.find_value_at(n=100), "big": sdata.find_sum_of_series("k**2", between=[1, 10**6])
                    .find_value_at()}
               """, {"at 100": (5050.0, 0.0, CLOSED_FORM + ": n (n + 1) / 2"),
                     "big": (10**6 * (10**6 + 1) * (2 * 10**6 + 1) / 6, 1e-15, CLOSED_FORM + ": n (n + 1)(2n + 1) / 6")},
               """
                   import sympy as sp
                   k, n = sp.symbols("k n", integer=True)
                   {"at 100": float(sp.summation(k, (k, 1, n)).subs(n, 100)),
                    "big": float(sp.summation(k**2, (k, 1, 10**6)))}
               """, "SymPy summation",
               r="""
                   list(`at 100` = sum(1:100), big = sum(as.numeric(1:1e6)^2))
               """),
        closed("sdata.find_sum_of_series", "1 / (k log(k)^3) from 2 settles slowly: only the sure digits",
               """
                   {"sum": sdata.find_sum_of_series("1/(k*log(k)**3)", between=[2, "infinity"])}
               """, {"sum": (_log_series(3), 1e-9, "worked out by hand: the terms up to 10^7 and the integral of the "
                                                    "rest (Euler-Maclaurin)")},
               """
                   import sympy as sp
                   x = sp.Symbol("x", positive=True)
                   f = 1 / (x * sp.log(x)**3)
                   first = sp.Add(*[f.subs(x, i) for i in range(2, 1001)]).evalf(40)
                   high = sp.integrate(f, (x, sp.Rational(2001, 2), sp.oo))
                   low = sp.integrate(f, (x, 1000, sp.oo)) - f.subs(x, 1000) / 2
                   {"sum": float(first + ((low + high) / 2).evalf(40))}
               """, "SymPy: the first 1,000 terms (evalf), the rest between the trapezoid and midpoint bounds "
                    "(integrate)", tolerance=1e-12,
               r="""
                   N <- 1e7; k <- 2:N
                   list(sum = sum(1/(k*log(k)^3)) + 1/(2*log(N)^2) - 1/(2*N*log(N)^3))
               """, r_tolerance=1e-9),
        closed("sdata.find_volume_under", "exactly=True: the volume under x y^2 over 0..1 by 0..2 is 4 / 3",
               """
                   v = sdata.find_volume_under("x * y**2", between={"x": [0, 1], "y": [0, 2]}, exactly=True)
                   {"volume": v.find_value_at()}
               """, {"volume": (4 / 3, 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   x, y = sp.symbols("x y")
                   {"volume": float(sp.integrate(x * y**2, (y, 0, 2), (x, 0, 1)))}
               """, "SymPy integrate",
               r="""
                   inner <- function(x) sapply(x, function(a) integrate(function(y) a * y^2, 0, 2, rel.tol = 1e-12)$value)
                   list(volume = integrate(inner, 0, 1, rel.tol = 1e-12)$value)
               """, option="exactly="),
        closed("sdata.find_path_over_time", "exactly=True without at_start=: dN/dt = r N is N = C1 exp(r t)",
               """
                   path = sdata.find_path_over_time("dN/dt = r * N", exactly=True)
                   {"C1 = 10, r = 0.3, t = 5": path.find_value_at(C1=10, r=0.3, t=5)}
               """, {"C1 = 10, r = 0.3, t = 5": (10 * math.exp(1.5), 1e-14, CLOSED_FORM)},
               """
                   import sympy as sp
                   t, r, C1, N = sp.Symbol("t"), sp.Symbol("r"), sp.Symbol("C1"), sp.Function("N")
                   s = sp.dsolve(sp.Eq(N(t).diff(t), r * N(t)), N(t))
                   {"C1 = 10, r = 0.3, t = 5": float(s.rhs.subs({C1: 10, r: sp.Rational(3, 10), t: 5}))}
               """, "SymPy dsolve", option="exactly= without at_start="),
        closed("sdata.find_path_over_time", "d2x/dt2 = -4x - 0.5 dx/dt from x = 1 at rest: a damped spring",
               """
                   p = sdata.find_path_over_time("d2x/dt2 = -k*x - c*dx/dt", at_start={"x": 1, "dx/dt": 0},
                                                 between=[0, 10], known={"k": 4, "c": 0.5}, time_step=0.5)
                   {"x at 5": p.get_cell_at(row=11, column="x"), "x at 10": p.get_cell_at(row=21, column="x"),
                    "dx/dt at 5": p.get_cell_at(row=11, column="dx/dt")}
               """, {"x at 5": (_damped(5)[0], 1e-4, CLOSED_FORM + ": exp(-c t / 2) (cos w t + c / (2 w) sin w t), "
                                                   "within the solver's tolerance"),
                     "x at 10": (_damped(10)[0], 1e-4, CLOSED_FORM),
                     "dx/dt at 5": (_damped(5)[1], 1e-4, CLOSED_FORM)},
               """
                   from scipy.integrate import solve_ivp
                   s = solve_ivp(lambda t, y: [y[1], -4 * y[0] - 0.5 * y[1]], (0, 10), [1, 0],
                                 t_eval=np.linspace(0, 10, 21), rtol=1e-6, atol=1e-6)
                   {"x at 5": s.y[0][10], "x at 10": s.y[0][20], "dx/dt at 5": s.y[1][10]}
               """, "SciPy integrate.solve_ivp (RK45), as two first-order equations",
               option='equations="d2x/dt2 = ..."'),
        closed("sdata.find_path_over_time", "exactly=True: d2x/dt2 = -4x from x = 1 at rest is x = cos(2t)",
               """
                   path = sdata.find_path_over_time("d2x/dt2 = -k*x", at_start={"x": 1, "dx/dt": 0}, known={"k": 4},
                                                    exactly=True)
                   {"at 1": path.find_value_at(t=1), "at 2.5": path.find_value_at(t=2.5)}
               """, {"at 1": (math.cos(2), 1e-15, CLOSED_FORM), "at 2.5": (math.cos(5), 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   t, x = sp.Symbol("t"), sp.Function("x")
                   s = sp.dsolve(sp.Eq(x(t).diff(t, 2), -4 * x(t)), x(t), ics={x(0): 1, x(t).diff(t).subs(t, 0): 0})
                   {"at 1": float(s.rhs.subs(t, 1)), "at 2.5": float(s.rhs.subs(t, sp.Rational(5, 2)))}
               """, "SymPy dsolve",
               r="""
                   list(`at 1` = cos(2), `at 2.5` = cos(5))
               """, option='equations="d2x/dt2 = ...", exactly='),
        # ---------------------------------------------------------------- grids on real data
        Case("grid.find_determinant", "the determinant of the correlations of Fisher's iris measurements",
             "iris", "real data",
             ours=f"""
                 grid = sdata.number_grid(data[{IRIS}].corr().to_numpy().tolist())
                 {{"determinant": grid.find_determinant()}}
             """,
             parent=f"""
                 from scipy import linalg
                 {{"determinant": float(linalg.det(data[{IRIS}].corr().to_numpy()))}}
             """, parent_label="SciPy linalg.det", parent_tolerance=1e-12,
             r=f"""
                 list(determinant = det({IRIS_R}))
             """, r_tolerance=1e-9),
        Case("grid.find_determinant", "exactly=True: AirPassengers as 12 years x 12 months, a whole-number determinant",
             "AirPassengers", "real data", option="exactly=",
             ours=_code(AIR_GRID, """
                 exact = grid.find_determinant(exactly=True)
                 {"determinant": exact.find_value_at(), "whole number": float(exact.as_sympy().is_Integer)}
             """),
             parent=_code(AIR_NUMPY, """
                 import sympy as sp
                 d = sp.Matrix(g.astype(int).tolist()).det()
                 {"determinant": float(d), "whole number": float(d.is_Integer)}
             """), parent_label="SymPy Matrix.det", parent_tolerance=1e-15,
             r=_code(AIR_R, """
                 list(determinant = det(g))
             """), r_tolerance=1e-9),
        Case("grid.take_inverse", "the inverse of the correlations of Fisher's iris measurements",
             "iris", "real data",
             ours=f"""
                 grid = sdata.number_grid(data[{IRIS}].corr().to_numpy().tolist())
                 grid.take_inverse()
                 {{"first": grid.get_number_at(row=1, column=1), "corner": grid.get_number_at(row=1, column=4),
                  "total": grid.find_total()}}
             """,
             parent=f"""
                 from scipy import linalg
                 i = linalg.inv(data[{IRIS}].corr().to_numpy())
                 {{"first": i[0, 0], "corner": i[0, 3], "total": i.sum()}}
             """, parent_label="SciPy linalg.inv", parent_tolerance=1e-12,
             r=f"""
                 i <- solve({IRIS_R})
                 list(first = i[1, 1], corner = i[1, 4], total = sum(i))
             """, r_tolerance=1e-9),
        Case("grid.take_inverse", "exactly=True: the first 3 years x 3 months of AirPassengers, inverted exactly",
             "AirPassengers", "real data", option="exactly=",
             ours=_code(AIR_GRID, """
                 grid.keep_rows_by_position(1, to=3)
                 grid.keep_columns_by_position(1, to=3)
                 grid.take_inverse(exactly=True)
                 {"first": grid.get_number_at(row=1, column=1), "total": grid.find_total()}
             """),
             parent=_code(AIR_NUMPY, """
                 import sympy as sp
                 i = np.array(sp.Matrix(g[:3, :3].astype(int).tolist()).inv().evalf(), dtype=float)
                 {"first": i[0, 0], "total": i.sum()}
             """), parent_label="SymPy Matrix.inv", parent_tolerance=1e-15,
             r=_code(AIR_R, """
                 i <- solve(g[1:3, 1:3])
                 list(first = i[1, 1], total = sum(i))
             """), r_tolerance=1e-9),
        Case("grid.find_eigenvalues", "the eigenvalues of the correlations of Fisher's iris measurements",
             "iris", "real data",
             ours=f"""
                 grid = sdata.number_grid(data[{IRIS}].corr().to_numpy().tolist())
                 e = grid.find_eigenvalues()
                 {{"biggest": e.get_cell_at(row=1, column="eigenvalue"),
                  "smallest": e.get_cell_at(row=4, column="eigenvalue"),
                  "total": e.get_column("eigenvalue").find_total()}}
             """,
             parent=f"""
                 from scipy import linalg
                 v = linalg.eigvalsh(data[{IRIS}].corr().to_numpy())
                 {{"biggest": v[-1], "smallest": v[0], "total": v.sum()}}
             """, parent_label="SciPy linalg.eigvalsh", parent_tolerance=1e-12,
             published={"total": (4.0, 1e-12, "the eigenvalues of a correlation grid add up to its size")},
             r=f"""
                 v <- eigen({IRIS_R})$values
                 list(biggest = v[1], smallest = v[4], total = sum(v))
             """, r_tolerance=1e-9),
        Case("grid.find_eigenvalues", "AirPassengers, first 4 years x 4 months (not symmetric): in R eigen()'s order",
             "AirPassengers", "real data",
             ours=_code(AIR_GRID, """
                 grid.keep_rows_by_position(1, to=4)
                 grid.keep_columns_by_position(1, to=4)
                 e = grid.find_eigenvalues()
                 {"first": e.get_cell_at(row=1, column="eigenvalue"),
                  "second": e.get_cell_at(row=2, column="eigenvalue"),
                  "third": e.get_cell_at(row=3, column="eigenvalue"),
                  "third, imaginary": e.get_cell_at(row=3, column="imaginary part"),
                  "fourth, imaginary": e.get_cell_at(row=4, column="imaginary part")}
             """),
             parent=_code(AIR_NUMPY, """
                 from scipy import linalg
                 v = linalg.eigvals(g[:4, :4])
                 v = v[np.argsort(-np.abs(v), kind="stable")]
                 {"first": v[0].real, "second": v[1].real, "third": v[2].real, "third, imaginary": v[2].imag,
                  "fourth, imaginary": v[3].imag}
             """), parent_label="SciPy linalg.eigvals, by size", parent_tolerance=1e-12,
             r=_code(AIR_R, """
                 v <- eigen(g[1:4, 1:4])$values
                 list(first = Re(v[1]), second = Re(v[2]), third = Re(v[3]), `third, imaginary` = Im(v[3]),
                      `fourth, imaginary` = Im(v[4]))
             """), r_tolerance=1e-9),
        Case("grid.find_eigenvalues", "exactly=True: January and February of 1949 and 1950 (AirPassengers), exactly",
             "AirPassengers", "real data", option="exactly=",
             ours=_code(AIR_GRID, """
                 grid.keep_rows_by_position(1, to=2)
                 grid.keep_columns_by_position(1, to=2)
                 e = grid.find_eigenvalues(exactly=True)
                 {"biggest": e.get_cell_at(row=1, column="eigenvalue"),
                  "smallest": e.get_cell_at(row=2, column="eigenvalue")}
             """),
             parent=_code(AIR_NUMPY, """
                 import sympy as sp
                 found = sorted((float(v) for v in sp.Matrix(g[:2, :2].astype(int).tolist()).eigenvals()), reverse=True)
                 {"biggest": found[0], "smallest": found[1]}
             """), parent_label="SymPy Matrix.eigenvals", parent_tolerance=1e-15,
             r=_code(AIR_R, """
                 v <- eigen(g[1:2, 1:2])$values
                 list(biggest = v[1], smallest = v[2])
             """), r_tolerance=1e-12),
        Case("grid.find_null_space", "exactly=True: the 2 directions the first 6 iris flowers (4 x 6) send to zero",
             "iris", "real data", option="exactly=",
             ours=f"""
                 grid = sdata.number_grid(data[{IRIS}].head(6).to_numpy().T.tolist())
                 n = grid.find_null_space(exactly=True).as_numpy()
                 {{"directions": n.shape[1], "biggest left over": float(np.abs(grid.as_numpy() @ n).max() < 1e-12),
                  "total": n.sum()}}
             """,
             parent=f"""
                 import sympy as sp
                 a = data[{IRIS}].head(6).to_numpy().T
                 m = sp.Matrix([[sp.nsimplify(v, rational=True) for v in row] for row in a])
                 n = np.array([[float(v) for v in vec] for vec in m.nullspace()]).T
                 {{"directions": n.shape[1], "biggest left over": float(np.abs(a @ n).max() < 1e-12), "total": n.sum()}}
             """, parent_label="SymPy Matrix.nullspace", parent_tolerance=1e-15,
             r="""
                 a <- rbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width)[, 1:6]
                 n <- MASS::Null(t(a))
                 list(directions = ncol(n), `biggest left over` = as.numeric(max(abs(a %*% n)) < 1e-12))
             """, r_packages=("MASS",), r_tolerance=1e-12),
    ]
