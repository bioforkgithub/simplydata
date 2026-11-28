"""Families for 100 %, batches 24-26 (plan section 2.10): calculus checks, series, transforms and code on a formula,
check_solution, products, ways, the new kinds of sdata.solve(exactly=True), number theory and exact grids, against
answers worked out by hand and published values.

cases_underneath.py loads this file and adds cases(Case) to the study. A formula or a few whole numbers are the
input of these words, so they have no data by nature: each case is checked against the answer worked out by hand (a
closed form, such as the Laplace transform tables of Abramowitz and Stegun 1964, chapter 29), against published
values (the OEIS sequences), against SymPy directly, and against R where R does the same (pracma's isprime, factors,
primes, gcd, Lcm and contfrac; base R's choose and factorial; gmp's factorize and isprime).
"""

from __future__ import annotations

import math
import textwrap

CLOSED_FORM = "exact: worked out by hand from the formula"
TABLES = "Abramowitz and Stegun (1964), Handbook of Mathematical Functions, table 29.3 (Laplace transforms)"
OEIS = "OEIS (the On-Line Encyclopedia of Integer Sequences)"


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(p).strip("\n") for p in parts if p)


def cases(Case):
    def closed(word, title, ours, published, parent="", label="", r="", option="", tolerance=1e-12,
               r_tolerance=1e-9, r_packages=()):
        return Case(word, title, "closed form (no data)", "closed form", ours=_code(ours), published=published,
                    parent=_code(parent), parent_label=label, parent_tolerance=tolerance, r=_code(r),
                    r_tolerance=r_tolerance, option=option, r_packages=r_packages)

    return [
        # ---------------------------------------------------------------- transforms
        closed("f.take_transform", "Laplace transform of exp(-2t) is 1/(s + 2); at s = 1 it is 1/3",
               """
                   found = sdata.formula("exp(-2*t)").take_transform("laplace")
                   {"at s = 1": found.find_value_at(s=1), "at s = 3": found.find_value_at(s=3)}
               """, {"at s = 1": (1 / 3, 1e-15, TABLES + ": 1/(s + a)"), "at s = 3": (0.2, 1e-15, TABLES)},
               """
                   import sympy as sp
                   t, s = sp.symbols("t s")
                   F = sp.laplace_transform(sp.exp(-2*t), t, s, noconds=True)
                   {"at s = 1": float(F.subs(s, 1)), "at s = 3": float(F.subs(s, 3))}
               """, "SymPy laplace_transform"),
        closed("f.take_transform", "Laplace transform of t^3 is 3!/s^4 = 6/s^4",
               """
                   found = sdata.formula("t**3").take_transform("laplace")
                   {"at s = 2": found.find_value_at(s=2)}
               """, {"at s = 2": (6 / 16, 1e-15, TABLES + ": n!/s^(n+1)")},
               """
                   import sympy as sp
                   t, s = sp.symbols("t s")
                   {"at s = 2": float(sp.laplace_transform(t**3, t, s, noconds=True).subs(s, 2))}
               """, "SymPy laplace_transform"),
        closed("f.take_transform", "Fourier transform of exp(-pi x^2) is exp(-pi k^2) (the Gaussian is its own "
               "transform with 2*pi in the power)",
               """
                   found = sdata.formula("exp(-pi*x**2)").take_transform("fourier")
                   {"at k = 1": found.find_value_at(k=1)}
               """, {"at k = 1": (math.exp(-math.pi), 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   x, k = sp.symbols("x k")
                   {"at k = 1": float(sp.fourier_transform(sp.exp(-sp.pi*x**2), x, k).subs(k, 1))}
               """, "SymPy fourier_transform"),
        closed("f.take_transform", "from_letter= and to_letter=: Laplace transform of sin(3u) is 3/(p^2 + 9)",
               """
                   found = sdata.formula("sin(3*u)").take_transform("laplace", from_letter="u", to_letter="p")
                   {"at p = 1": found.find_value_at(p=1)}
               """, {"at p = 1": (0.3, 1e-15, TABLES + ": w/(s^2 + w^2)")},
               """
                   import sympy as sp
                   u, p = sp.symbols("u p")
                   {"at p = 1": float(sp.laplace_transform(sp.sin(3*u), u, p, noconds=True).subs(p, 1))}
               """, "SymPy laplace_transform", option="from_letter="),
        closed("f.take_transform", "order=: Hankel transform of order 0 of exp(-r) is (k^2 + 1)^(-3/2)",
               """
                   found = sdata.formula("exp(-r)").take_transform("hankel", order=0)
                   {"at k = 1": found.find_value_at(k=1)}
               """, {"at k = 1": (2 ** -1.5, 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   r, k = sp.symbols("r k")
                   {"at k = 1": float(sp.hankel_transform(sp.exp(-r), r, k, 0).subs(k, 1))}
               """, "SymPy hankel_transform", option="order="),
        closed("f.take_transform", "between=: the inverse Mellin transform of gamma(s) on (0, infinity) is exp(-x)",
               """
                   found = sdata.formula("gamma(s)").take_transform("inverse mellin", between=[0, "infinity"])
                   {"at x = 1": found.find_value_at(x=1)}
               """, {"at x = 1": (math.exp(-1), 1e-15, "Euler's integral: gamma(s) is the Mellin transform of "
                                                       "exp(-x)")},
               """
                   import sympy as sp
                   s, x = sp.symbols("s x")
                   {"at x = 1": float(sp.inverse_mellin_transform(sp.gamma(s), s, x, (0, sp.oo)).subs(x, 1))}
               """, "SymPy inverse_mellin_transform", option="between="),
        closed("f.find_area_along_path", "x^2 + y^2 along the unit circle is 1 times its length, 2*pi",
               """
                   area = sdata.formula("x**2 + y**2").find_area_along_path(path="x = cos(t), y = sin(t)",
                                                                            between=[0, "2*pi"])
                   {"area": area}
               """, {"area": (2 * math.pi, 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   x, y, t = sp.symbols("x y t")
                   C = sp.Curve([sp.cos(t), sp.sin(t)], (t, 0, 2*sp.pi))
                   {"area": float(sp.line_integrate(x**2 + y**2, C, [x, y]))}
               """, "SymPy line_integrate"),
        # ---------------------------------------------------------------- calculus checks
        closed("f.check_if_always", "x^2 rises on [0, 5] and not on [-1, 5]; x^3 rises on [-1, 1]",
               """
                   f = sdata.formula("x**2")
                   {"x^2 on [0, 5]": float(f.check_if_always("rising", between=[0, 5])),
                    "x^2 on [-1, 5]": float(f.check_if_always("rising", between=[-1, 5])),
                    "x^3 on [-1, 1]": float(sdata.formula("x**3").check_if_always("rising", between=[-1, 1]))}
               """, {"x^2 on [0, 5]": (1.0, 0.0, CLOSED_FORM + ": the slope 2x is at least 0"),
                     "x^2 on [-1, 5]": (0.0, 0.0, CLOSED_FORM + ": the slope is below 0 for x < 0"),
                     "x^3 on [-1, 1]": (1.0, 0.0, CLOSED_FORM + ": the slope 3x^2 is at least 0")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"x^2 on [0, 5]": float(sp.is_increasing(x**2, sp.Interval(0, 5), x)),
                    "x^2 on [-1, 5]": float(sp.is_increasing(x**2, sp.Interval(-1, 5), x)),
                    "x^3 on [-1, 1]": float(sp.is_increasing(x**3, sp.Interval(-1, 1), x))}
               """, "SymPy is_increasing"),
        closed("f.check_if_always", "between=: x^2 bends up on [-1, 1]; sin(x) does not on [0, pi]",
               """
                   {"x^2": float(sdata.formula("x**2").check_if_always("bending up", between=[-1, 1])),
                    "sin": float(sdata.formula("sin(x)").check_if_always("bending up", between=[0, "pi"]))}
               """, {"x^2": (1.0, 0.0, CLOSED_FORM + ": the second slope is 2"),
                     "sin": (0.0, 0.0, CLOSED_FORM + ": the second slope -sin(x) is below 0 inside")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"x^2": float(sp.is_convex(x**2, x, domain=sp.Interval(-1, 1))),
                    "sin": float(sp.is_convex(sp.sin(x), x, domain=sp.Interval(0, sp.pi)))}
               """, "SymPy is_convex", option="between="),
        closed("f.find_turning_points", "x^3 - 3x turns at -1 (value 2) and 1 (value -2)",
               """
                   points = sdata.formula("x**3 - 3*x").find_turning_points()
                   at = points.get_column("at").as_numpy()
                   value = points.get_column("value").as_numpy()
                   {"first": float(at[0]), "second": float(at[1]), "value at first": float(value[0])}
               """, {"first": (-1.0, 0.0, CLOSED_FORM + ": 3x^2 - 3 = 0"), "second": (1.0, 0.0, CLOSED_FORM),
                     "value at first": (2.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   p = sorted(sp.stationary_points(x**3 - 3*x, x, sp.S.Reals))
                   {"first": float(p[0]), "second": float(p[1]), "value at first": float((x**3 - 3*x).subs(x, p[0]))}
               """, "SymPy stationary_points"),
        closed("f.find_turning_points", "between=: sin(x) turns at pi/2 and 3*pi/2 between 0 and 7",
               """
                   points = sdata.formula("sin(x)").find_turning_points(between=[0, 7])
                   at = points.get_column("at").as_numpy()
                   {"first": float(at[0]), "second": float(at[1])}
               """, {"first": (math.pi / 2, 1e-15, CLOSED_FORM + ": cos(x) = 0"),
                     "second": (3 * math.pi / 2, 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   p = sorted(sp.stationary_points(sp.sin(x), x, sp.Interval(0, 7)), key=float)
                   {"first": float(p[0]), "second": float(p[1])}
               """, "SymPy stationary_points", option="between="),
        closed("f.find_where_undefined", "1/(x^2 - 1) is undefined at -1 and 1",
               """
                   points = sdata.formula("1/(x**2 - 1)").find_where_undefined()
                   at = points.get_column("at").as_numpy()
                   {"first": float(at[0]), "second": float(at[1])}
               """, {"first": (-1.0, 0.0, CLOSED_FORM + ": x^2 - 1 = 0"), "second": (1.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   p = sorted(sp.singularities(1/(x**2 - 1), x, sp.S.Reals))
                   {"first": float(p[0]), "second": float(p[1])}
               """, "SymPy singularities"),
        closed("f.find_period", "sin(2x) repeats every pi; cos(x/3) every 6*pi",
               """
                   {"sin(2x)": sdata.formula("sin(2*x)").find_period(),
                    "cos(x/3)": sdata.formula("cos(x/3)").find_period()}
               """, {"sin(2x)": (math.pi, 1e-15, CLOSED_FORM + ": 2*pi/2"),
                     "cos(x/3)": (6 * math.pi, 1e-15, CLOSED_FORM + ": 2*pi*3")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"sin(2x)": float(sp.periodicity(sp.sin(2*x), x)),
                    "cos(x/3)": float(sp.periodicity(sp.cos(x/3), x))}
               """, "SymPy periodicity"),
        # ---------------------------------------------------------------- series
        closed("f.find_fourier_series", "x on (-pi, pi) is 2 sin x - sin 2x + (2/3) sin 3x - ...",
               """
                   series = sdata.formula("x").find_fourier_series(between=["-pi", "pi"])
                   {"at 1": series.find_value_at(x=1)}
               """, {"at 1": (2 * math.sin(1) - math.sin(2) + 2 / 3 * math.sin(3), 1e-15,
                              CLOSED_FORM + ": b_n = 2(-1)^(n+1)/n")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   s = sp.fourier_series(x, (x, -sp.pi, sp.pi)).truncate(3)
                   {"at 1": float(s.subs(x, 1))}
               """, "SymPy fourier_series"),
        closed("f.find_fourier_series", "how_many_terms=: x^2 on (-pi, pi) is pi^2/3 - 4 cos x + cos 2x - (4/9) cos 3x",
               """
                   series = sdata.formula("x**2").find_fourier_series(between=["-pi", "pi"], how_many_terms=4)
                   {"at 0": series.find_value_at(x=0)}
               """, {"at 0": (math.pi ** 2 / 3 - 4 + 1 - 4 / 9, 1e-14, CLOSED_FORM + ": a_n = 4(-1)^n/n^2")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"at 0": float(sp.fourier_series(x**2, (x, -sp.pi, sp.pi)).truncate(4).subs(x, 0))}
               """, "SymPy fourier_series", option="how_many_terms="),
        closed("f.find_residue_at", "the residue of exp(x)/x^3 at 0 is 1/2!; of 1/(x^2 + 1) at pi it is 0",
               """
                   {"exp(x)/x^3": sdata.formula("exp(x)/x**3").find_residue_at(0),
                    "1/(x^2 + 1)": sdata.formula("1/(x**2 + 1)").find_residue_at("pi")}
               """, {"exp(x)/x^3": (0.5, 0.0, CLOSED_FORM + ": the x^2 term of exp(x) is x^2/2"),
                     "1/(x^2 + 1)": (0.0, 0.0, CLOSED_FORM + ": no pole at pi")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"exp(x)/x^3": float(sp.residue(sp.exp(x)/x**3, x, 0)),
                    "1/(x^2 + 1)": float(sp.residue(1/(x**2 + 1), x, sp.pi))}
               """, "SymPy residue"),
        closed("f.list_terms", "the squares 1, 4, 9, 16, 25 (OEIS A000290)",
               """
                   terms = sdata.formula("n**2").list_terms(between=[1, 5]).get_column("term").as_numpy()
                   {"5th": float(terms[4]), "total": float(terms.sum())}
               """, {"5th": (25.0, 0.0, OEIS + " A000290"), "total": (55.0, 0.0, CLOSED_FORM + ": n(n+1)(2n+1)/6")},
               """
                   import sympy as sp
                   n = sp.Symbol("n")
                   t = [float(v) for v in sp.sequence(n**2, (n, 1, 5))]
                   {"5th": t[4], "total": sum(t)}
               """, "SymPy sequence"),
        closed("f.find_taylor_series", "all_terms=: every term of exp(x) is x^k/k!; the sum to 10 terms at 1 is e",
               """
                   every = sdata.formula("exp(x)").find_taylor_series(all_terms=True)
                   {"terms": float("factorial" in str(every))}
               """, {"terms": (1.0, 0.0, CLOSED_FORM + ": the k-th term is x^k/k!")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"terms": float("factorial" in str(sp.fps(sp.exp(x), x, 0).infinite))}
               """, "SymPy fps", option="all_terms="),
        closed("f.find_limit_as", "whole_numbers_only=: (-1)^n/n goes to 0; n/(n + 1) to 1",
               """
                   {"(-1)^n/n": sdata.formula("(-1)**n/n").find_limit_as("n", goes_to="infinity",
                                                                          whole_numbers_only=True),
                    "n/(n + 1)": sdata.formula("n/(n + 1)").find_limit_as("n", goes_to="infinity",
                                                                           whole_numbers_only=True)}
               """, {"(-1)^n/n": (0.0, 0.0, CLOSED_FORM), "n/(n + 1)": (1.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   n = sp.Symbol("n")
                   {"(-1)^n/n": float(sp.limit_seq((-1)**n/n, n)), "n/(n + 1)": float(sp.limit_seq(n/(n + 1), n))}
               """, "SymPy limit_seq", option="whole_numbers_only="),
        closed("f.find_slope_formula", "step=: the forward difference of x^2 over h is 2x + h",
               """
                   slope = sdata.formula("x**2").find_slope_formula(step="h")
                   {"at x = 3, h = 0.5": slope.find_value_at(x=3, h=0.5)}
               """, {"at x = 3, h = 0.5": (6.5, 1e-15, CLOSED_FORM + ": ((x + h)^2 - x^2)/h = 2x + h")},
               """
                   import sympy as sp
                   x, h = sp.symbols("x h")
                   d = sp.differentiate_finite(x**2, x, points=[x, x + h])
                   {"at x = 3, h = 0.5": float(d.subs({x: 3, h: sp.Rational(1, 2)}))}
               """, "SymPy differentiate_finite", option="step="),
        closed("f.find_hessian", "the Hessian of x^2 y + y^3 is [[2y, 2x], [2x, 6y]]; its determinant at (1, 1) is 8",
               """
                   grid = sdata.formula("x**2*y + y**3").find_hessian()
                   {"determinant at (1, 1)": grid.find_determinant().find_value_at(x=1, y=1)}
               """, {"determinant at (1, 1)": (8.0, 0.0, CLOSED_FORM + ": 12y^2 - 4x^2")},
               """
                   import sympy as sp
                   x, y = sp.symbols("x y")
                   {"determinant at (1, 1)": float(sp.hessian(x**2*y + y**3, [x, y]).det().subs({x: 1, y: 1}))}
               """, "SymPy hessian"),
        closed("f.find_wronskian", "the Wronskian of exp(x) and exp(2x) is exp(3x)",
               """
                   {"at 0": sdata.formula("exp(x)").find_wronskian(["exp(2*x)"]).find_value_at(x=0)}
               """, {"at 0": (1.0, 0.0, CLOSED_FORM + ": e^x 2e^(2x) - e^(2x) e^x")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"at 0": float(sp.wronskian([sp.exp(x), sp.exp(2*x)], x).subs(x, 0))}
               """, "SymPy wronskian"),
        closed("f.find_wronskian", "whole_numbers_only=: the Casoratian of 2^n and 3^n is 6^n",
               """
                   found = sdata.formula("2**n").find_wronskian(["3**n"], whole_numbers_only=True)
                   {"at n = 2": found.find_value_at(n=2)}
               """, {"at n = 2": (36.0, 0.0, CLOSED_FORM + ": 2^n 3^(n+1) - 3^n 2^(n+1) = 6^n")},
               """
                   import sympy as sp
                   n = sp.Symbol("n")
                   {"at n = 2": float(sp.casoratian([2**n, 3**n], n, zero=False).subs(n, 2))}
               """, "SymPy casoratian", option="whole_numbers_only="),
        closed("f.find_wronskian", "for_letter=: the Wronskian of exp(a x) and exp(2x) in x is (2 - a) exp((a + 2) x)",
               """
                   found = sdata.formula("exp(a*x)").find_wronskian(["exp(2*x)"], for_letter="x")
                   {"at a = 1, x = 0": found.find_value_at(a=1, x=0)}
               """, {"at a = 1, x = 0": (1.0, 1e-15, CLOSED_FORM + ": 2 e^(ax) e^(2x) - a e^(ax) e^(2x)")},
               """
                   import sympy as sp
                   a, x = sp.symbols("a x")
                   w = sp.wronskian([sp.exp(a*x), sp.exp(2*x)], x)
                   {"at a = 1, x = 0": float(w.subs({a: 1, x: 0}))}
               """, "SymPy wronskian", option="for_letter="),
        closed("f.show_as_code", "sin(x)^2 + exp(-x) in R, as R itself writes it",
               """
                   {"same": float(sdata.formula("sin(x)**2 + exp(-x)").show_as_code("r") == "sin(x)^2 + exp(-x)")}
               """, {"same": (1.0, 0.0, "R's own syntax: ^ for powers")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"same": float(sp.rcode(sp.sin(x)**2 + sp.exp(-x)) == "sin(x)^2 + exp(-x)")}
               """, "SymPy rcode",
               r="""
                   x <- 0.7
                   list(same = as.numeric(abs(eval(parse(text = "sin(x)^2 + exp(-x)")) - (sin(0.7)^2 + exp(-0.7)))
                                          < 1e-15))
               """),
        closed("f.show_as_tree", "x^2 + 1: an Add with the parts 1 and x^2, 5 lines",
               """
                   {"lines": float(len(sdata.formula("x**2 + 1").show_as_tree().splitlines()))}
               """, {"lines": (5.0, 0.0, CLOSED_FORM + ": Add, One, Pow, Symbol, Integer")},
               """
                   import sympy as sp
                   from sympy.printing.tree import tree
                   x = sp.Symbol("x")
                   {"lines": float(len(tree(x**2 + 1, assumptions=False).rstrip().splitlines()))}
               """, "SymPy print_tree"),
        closed("f.show_as_tree", "as_graphviz=: the dot text of x + 1 starts a digraph",
               """
                   {"digraph": float(sdata.formula("x + 1").show_as_tree(as_graphviz=True).startswith("digraph"))}
               """, {"digraph": (1.0, 0.0, "the Graphviz dot language")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"digraph": float(sp.dotprint(x + 1).startswith("digraph"))}
               """, "SymPy dotprint", option="as_graphviz="),
        closed("f.show_as_latex", "left_side=: y = x^{2}",
               """
                   {"same": float(sdata.formula("x**2").show_as_latex(left_side="y") == "y = x^{2}")}
               """, {"same": (1.0, 0.0, "LaTeX")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"same": float(sp.latex(sp.Eq(sp.Symbol("y"), x**2)) == "y = x^{2}")}
               """, "SymPy latex", option="left_side="),
        closed("f.show_as_latex", "over_lines=: one line for each of the 3 terms of x^2 + 2x + 1",
               """
                   text = sdata.formula("x**2 + 2*x + 1").show_as_latex(over_lines=True)
                   {"lines": float(text.count("\\\\\\\\") + 1)}
               """, {"lines": (3.0, 0.0, CLOSED_FORM + ": three terms")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"lines": float(sp.multiline_latex(sp.Symbol("y"), x**2 + 2*x + 1).count("\\\\\\\\") + 1)}
               """, "SymPy multiline_latex", option="over_lines="),
        # ---------------------------------------------------------------- solving
        closed("sdata.check_solution", "y = 3 exp(x) solves dy/dx = y; y = sin(x) solves y'' = -y; x = -2 solves "
               "x^2 = 4",
               """
                   {"ode": float(sdata.check_solution("dy/dx = y", "y = 3*exp(x)")),
                    "second": float(sdata.check_solution("d2y/dx2 = -y", "y = sin(x)")),
                    "wrong": float(sdata.check_solution("dy/dx = y", "y = exp(2*x)")),
                    "algebra": float(sdata.check_solution("x**2 = 4", "x = -2"))}
               """, {"ode": (1.0, 0.0, CLOSED_FORM), "second": (1.0, 0.0, CLOSED_FORM),
                     "wrong": (0.0, 0.0, CLOSED_FORM + ": 2e^(2x) is not e^(2x)"), "algebra": (1.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   y = sp.Function("y")
                   {"ode": float(sp.checkodesol(sp.Eq(y(x).diff(x), y(x)), sp.Eq(y(x), 3*sp.exp(x)))[0]),
                    "second": float(sp.checkodesol(sp.Eq(y(x).diff(x, 2), -y(x)), sp.Eq(y(x), sp.sin(x)))[0]),
                    "wrong": float(sp.checkodesol(sp.Eq(y(x).diff(x), y(x)), sp.Eq(y(x), sp.exp(2*x)))[0]),
                    "algebra": float(sp.checksol(sp.Eq(x**2, 4), {x: -2}))}
               """, "SymPy checkodesol and checksol"),
        closed("sdata.find_product_of_series", "(1/2)(2/3)...(n/(n + 1)) = 1/(n + 1); 1 x 2 x ... x 10 = 10!",
               """
                   product = sdata.find_product_of_series("k/(k + 1)", between=[1, "n"])
                   {"at n = 9": product.find_value_at(n=9),
                    "10!": sdata.find_product_of_series("k", between=[1, 10]).find_value_at()}
               """, {"at n = 9": (0.1, 1e-15, CLOSED_FORM + ": the product telescopes"),
                     "10!": (3628800.0, 0.0, OEIS + " A000142")},
               """
                   import sympy as sp
                   k, n = sp.symbols("k n", integer=True)
                   {"at n = 9": float(sp.product(k/(k + 1), (k, 1, n)).subs(n, 9)),
                    "10!": float(sp.product(k, (k, 1, 10)))}
               """, "SymPy product",
               r="""
                   list(`10!` = factorial(10))
               """),
        closed("sdata.solve", "whole_numbers_only=: x^2 + y^2 = 25 has 12 whole-number solutions (r2(25), OEIS "
               "A004018)",
               """
                   {"solutions": float(sdata.solve("x**2 + y**2 = 25", exactly=True,
                                                   whole_numbers_only=True).count_rows())}
               """, {"solutions": (12.0, 0.0, OEIS + " A004018: r2(25) = 12")},
               """
                   import sympy as sp
                   x, y = sp.symbols("x y")
                   {"solutions": float(len(sp.diophantine(x**2 + y**2 - 25, syms=(x, y), permute=True)))}
               """, "SymPy diophantine", option="whole_numbers_only="),
        closed("sdata.solve", "at_start=: a(n + 2) = a(n + 1) + a(n), a(0) = 0, a(1) = 1 gives the Fibonacci numbers "
               "(F(20) = 6765, OEIS A000045)",
               """
                   a = sdata.solve("a(n + 2) = a(n + 1) + a(n)", exactly=True, at_start={0: 0, 1: 1})
                   {"F(20)": a.find_value_at(n=20)}
               """, {"F(20)": (6765.0, 1e-12, OEIS + " A000045")},
               """
                   import sympy as sp
                   n = sp.Symbol("n", integer=True)
                   a = sp.Function("a")
                   f = sp.rsolve(a(n + 2) - a(n + 1) - a(n), a(n), {a(0): 0, a(1): 1})
                   {"F(20)": float(f.subs(n, 20))}
               """, "SymPy rsolve", option="at_start="),
        closed("sdata.list_ways_to_choose", "2 out of 4 can be chosen in 4 choose 2 = 6 ways",
               """
                   {"ways": float(sdata.list_ways_to_choose(2, out_of=["A", "B", "C", "D"]).count_rows())}
               """, {"ways": (6.0, 0.0, CLOSED_FORM + ": 4!/(2! 2!)")},
               """
                   import sympy as sp
                   {"ways": float(len(list(sp.subsets(["A", "B", "C", "D"], 2))))}
               """, "SymPy subsets",
               r="""
                   list(ways = ncol(combn(4, 2)))
               """),
        closed("sdata.list_ways_to_choose", "one_from_each=: 2 colours and 3 sizes make 6 combinations",
               """
                   ways = sdata.list_ways_to_choose(one_from_each=[["red", "blue"], ["S", "M", "L"]])
                   {"ways": float(ways.count_rows())}
               """, {"ways": (6.0, 0.0, CLOSED_FORM + ": 2 x 3")},
               """
                   import sympy as sp
                   {"ways": float(len(list(sp.cartes(["red", "blue"], ["S", "M", "L"]))))}
               """, "SymPy cartes",
               r="""
                   list(ways = nrow(expand.grid(c("red", "blue"), c("S", "M", "L"))))
               """, option="one_from_each="),
        closed("sdata.list_ways_to_choose", "with_repeats=: 2 out of 3 with repeats: (3 + 2 - 1) choose 2 = 6",
               """
                   {"ways": float(sdata.list_ways_to_choose(2, out_of=3, with_repeats=True).count_rows())}
               """, {"ways": (6.0, 0.0, CLOSED_FORM + ": (n + k - 1) choose k")},
               """
                   import sympy as sp
                   {"ways": float(len(list(sp.subsets([1, 2, 3], 2, repetition=True))))}
               """, "SymPy subsets",
               r="""
                   list(ways = choose(3 + 2 - 1, 2))
               """, option="with_repeats="),
        closed("sdata.list_ways_to_order", "2 out of 5 in order: 5 x 4 = 20 ways",
               """
                   {"ways": float(sdata.list_ways_to_order(2, out_of=5).count_rows())}
               """, {"ways": (20.0, 0.0, CLOSED_FORM + ": 5!/3!")},
               """
                   import sympy as sp
                   {"ways": float(len(list(sp.variations([1, 2, 3, 4, 5], 2))))}
               """, "SymPy variations",
               r="""
                   list(ways = factorial(5) / factorial(3))
               """),
        # ---------------------------------------------------------------- number theory
        closed("nums.check_if_prime", "of 1 to 100, 25 are prime (pi(100) = 25, OEIS A000720); 561 is not",
               """
                   answer = sdata.number_list(list(range(1, 101))).check_if_prime()
                   {"primes": float(answer.as_numpy().sum()),
                    "561": float(sdata.number_list([561]).check_if_prime().as_numpy()[0])}
               """, {"primes": (25.0, 0.0, OEIS + " A000720: pi(100) = 25"),
                     "561": (0.0, 0.0, CLOSED_FORM + ": 3 x 11 x 17")},
               """
                   import sympy as sp
                   {"primes": float(sum(sp.isprime(n) for n in range(1, 101))), "561": float(sp.isprime(561))}
               """, "SymPy isprime",
               r="""
                   list(primes = sum(pracma::isprime(1:100)), `561` = pracma::isprime(561))
               """, r_packages=("pracma",)),
        closed("nums.find_prime_factors", "360 = 2^3 x 3^2 x 5",
               """
                   factors = sdata.number_list([360]).find_prime_factors()
                   times = factors.get_column("times").as_numpy()
                   {"2": float(times[0]), "3": float(times[1]), "5": float(times[2])}
               """, {"2": (3.0, 0.0, CLOSED_FORM), "3": (2.0, 0.0, CLOSED_FORM), "5": (1.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   f = sp.factorint(360)
                   {"2": float(f[2]), "3": float(f[3]), "5": float(f[5])}
               """, "SymPy factorint",
               r="""
                   f <- pracma::factors(360)
                   list(`2` = sum(f == 2), `3` = sum(f == 3), `5` = sum(f == 5))
               """, r_packages=("pracma",)),
        closed("nums.find_prime_factors", 'show="different primes": the primes of 2310 are 2, 3, 5, 7, 11 (the '
               "primorial 11#)",
               """
                   found = sdata.number_list([2310]).find_prime_factors(show="different primes")
                   primes = found.get_column("prime").as_numpy()
                   {"how many": float(len(primes)), "biggest": float(primes[-1])}
               """, {"how many": (5.0, 0.0, OEIS + " A002110: 2310 = 2 x 3 x 5 x 7 x 11"),
                     "biggest": (11.0, 0.0, OEIS + " A002110")},
               """
                   import sympy as sp
                   p = sp.primefactors(2310)
                   {"how many": float(len(p)), "biggest": float(p[-1])}
               """, "SymPy primefactors",
               r="""
                   p <- unique(pracma::factors(2310))
                   list(`how many` = length(p), biggest = max(p))
               """, option="show=", r_packages=("pracma",)),
        closed("nums.find_number_fact", "the divisors of 28 add to 56 (a perfect number, OEIS A000396); 100 has 9 "
               "divisors (OEIS A000005)",
               """
                   divisors = sdata.number_list([28]).find_number_fact("divisors").get_column("answer").as_numpy()
                   {"sum": float(divisors.sum()),
                    "count of 100": float(sdata.number_list([100]).find_number_fact("number of divisors")
                                          .as_numpy()[0]),
                    "partitions of 100": float(sdata.number_list([100]).find_number_fact("partitions")
                                               .as_numpy()[0])}
               """, {"sum": (56.0, 0.0, OEIS + " A000396: 28 is perfect"),
                     "count of 100": (9.0, 0.0, OEIS + " A000005"),
                     "partitions of 100": (190569292.0, 0.0, OEIS + " A000041: p(100) = 190569292 (Hardy and "
                                                             "Ramanujan 1918)")},
               """
                   import sympy as sp
                   {"sum": float(sum(sp.divisors(28))), "count of 100": float(sp.divisor_count(100)),
                    "partitions of 100": float(sp.npartitions(100))}
               """, "SymPy divisors, divisor_count, npartitions",
               r="""
                   d <- (1:28)[28 %% (1:28) == 0]
                   list(sum = sum(d), `count of 100` = sum(100 %% (1:100) == 0))
               """),
        closed("nums.find_number_fact", "other=: 220 and 284 are amicable (OEIS A063990)",
               """
                   {"amicable": float(sdata.number_list([220]).find_number_fact("amicable with", other=284)
                                      .as_numpy()[0])}
               """, {"amicable": (1.0, 0.0, OEIS + " A063990: the smallest amicable pair")},
               """
                   import sympy as sp
                   {"amicable": float(sp.is_amicable(220, 284))}
               """, "SymPy is_amicable", option="other="),
        closed("nums.find_number_fact", "modulo=: 3 x 5 = 15 = 1 modulo 7, so the inverse of 3 is 5",
               """
                   {"inverse": float(sdata.number_list([3]).find_number_fact("inverse modulo", modulo=7)
                                     .as_numpy()[0])}
               """, {"inverse": (5.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   {"inverse": float(sp.mod_inverse(3, 7))}
               """, "SymPy mod_inverse",
               r="""
                   list(inverse = which((3 * 1:6) %% 7 == 1))
               """, option="modulo="),
        closed("nums.find_number_fact", "power=: the whole square root of 17 is 4, not exact",
               """
                   root = sdata.number_list([17]).find_number_fact("whole nth root", power=2)
                   {"root": float(root.get_column("root").as_numpy()[0])}
               """, {"root": (4.0, 0.0, CLOSED_FORM + ": 16 <= 17 < 25")},
               """
                   import sympy as sp
                   {"root": float(sp.integer_nthroot(17, 2)[0])}
               """, "SymPy integer_nthroot",
               r="""
                   list(root = floor(sqrt(17)))
               """, option="power="),
        closed("nums.find_number_fact", "base=: 7^k = 12 modulo 41 for k = 13 (the discrete log)",
               """
                   k = sdata.number_list([12]).find_number_fact("discrete log", modulo=41, base=7).as_numpy()[0]
                   {"k": float(k), "check": float(pow(7, int(k), 41))}
               """, {"check": (12.0, 0.0, CLOSED_FORM + ": 7^k modulo 41 is 12")},
               """
                   import sympy as sp
                   k = sp.discrete_log(41, 12, 7)
                   {"k": float(k), "check": float(pow(7, int(k), 41))}
               """, "SymPy discrete_log", option="base="),
        # ---------------------------------------------------------------- grids
        closed("sdata.number_grid", "exactly=: the determinant of [[1, 1/3], [a, 2]] is 2 - a/3; at a = 6 it is 0",
               """
                   grid = sdata.number_grid([[1, "1/3"], ["a", 2]], exactly=True)
                   {"at a = 6": grid.find_determinant().find_value_at(a=6)}
               """, {"at a = 6": (0.0, 0.0, CLOSED_FORM + ": 1 x 2 - a/3")},
               """
                   import sympy as sp
                   a = sp.Symbol("a")
                   {"at a = 6": float(sp.Matrix([[1, sp.Rational(1, 3)], [a, 2]]).det().subs(a, 6))}
               """, "SymPy Matrix.det", option="exactly="),
        closed("grid.find_permanent", "the permanent of the 6 x 6 grid of 1s is 6! = 720 (OEIS A000142); of [[1, 2], "
               "[3, 4]] it is 10",
               """
                   {"ones": sdata.number_grid([[1] * 6] * 6).find_permanent(),
                    "small": sdata.number_grid([[1, 2], [3, 4]]).find_permanent()}
               """, {"ones": (720.0, 0.0, OEIS + " A000142: per(J_n) = n!"), "small": (10.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   {"ones": float(sp.ones(6, 6).per()), "small": float(sp.Matrix([[1, 2], [3, 4]]).per())}
               """, "SymPy per"),
        closed("grid.find_permanent", "exactly=: the permanent of [[1/2, 1], [1, 2]] is 1/2 x 2 + 1 x 1 = 2",
               """
                   {"permanent": sdata.number_grid([[0.5, 1], [1, 2]]).find_permanent(exactly=True).find_value_at()}
               """, {"permanent": (2.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   {"permanent": float(sp.Matrix([[sp.Rational(1, 2), 1], [1, 2]]).per())}
               """, "SymPy per", option="exactly="),
        closed("grid.make_columns_orthogonal", "Gram-Schmidt on (1, 1) and (1, 0) gives (1, 1) and (1/2, -1/2), at "
               "right angles",
               """
                   grid = sdata.number_grid([[1, 1], [1, 0]])
                   grid.make_columns_orthogonal()
                   v = grid.as_numpy()
                   {"dot": float(v[:, 0] @ v[:, 1]), "second top": float(v[0, 1])}
               """, {"dot": (0.0, 0.0, CLOSED_FORM), "second top": (0.5, 0.0, CLOSED_FORM + ": (1, 0) - (1/2)(1, 1)")},
               """
                   import sympy as sp
                   c = sp.GramSchmidt([sp.Matrix([1, 1]), sp.Matrix([1, 0])])
                   {"dot": float(c[0].dot(c[1])), "second top": float(c[1][0])}
               """, "SymPy GramSchmidt"),
        closed("grid.make_columns_orthogonal", "of_length_1=: each column then has length 1",
               """
                   grid = sdata.number_grid([[3, 1], [4, 2]])
                   grid.make_columns_orthogonal(of_length_1=True)
                   v = grid.as_numpy()
                   {"first length": float((v[:, 0] ** 2).sum()), "second length": float((v[:, 1] ** 2).sum())}
               """, {"first length": (1.0, 1e-15, CLOSED_FORM), "second length": (1.0, 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   c = sp.GramSchmidt([sp.Matrix([3, 4]), sp.Matrix([1, 2])], True)
                   {"first length": float(c[0].dot(c[0])), "second length": float(c[1].dot(c[1]))}
               """, "SymPy GramSchmidt", option="of_length_1="),
    ]
