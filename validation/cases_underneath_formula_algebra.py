"""Families for 100 %, batches 22-23 (plan section 2.10): polynomial algebra on a formula and SymPy's names in formula
text, against answers worked out by hand and published values.

cases_underneath.py loads this file and adds cases(Case) to the study. A formula is the input of these words, so
they have no data by nature: each case is checked against the answer worked out by hand from the formula (a closed
form, such as the remainder theorem or b^2 - 4ac), against published values (the OEIS sequences and constants),
against SymPy directly, and against R where R does the same (base R polyroot() for roots, factorial(), pracma's
deconv() for the division of polynomials).
"""

from __future__ import annotations

import math
import textwrap

CLOSED_FORM = "exact: worked out by hand from the formula"
OEIS = "OEIS (the On-Line Encyclopedia of Integer Sequences)"
# the cube root of 2 (OEIS A002580)
CUBE_ROOT_2 = 1.2599210498948731648


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(p).strip("\n") for p in parts if p)


def cases(Case):
    def closed(word, title, ours, published, parent="", label="", r="", option="", tolerance=1e-12,
               r_tolerance=1e-9, r_packages=()):
        return Case(word, title, "closed form (no data)", "closed form", ours=_code(ours), published=published,
                    parent=_code(parent), parent_label=label, parent_tolerance=tolerance, r=_code(r),
                    r_tolerance=r_tolerance, option=option, r_packages=r_packages)

    return [
        # ---------------------------------------------------------------- find_roots
        closed("f.find_roots", "x^3 - 2x^2 - x + 2 = (x + 1)(x - 1)(x - 2) has the roots -1, 1 and 2",
               """
                   roots = sdata.formula("x**3 - 2*x**2 - x + 2").find_roots()
                   values = roots.get_column("root").as_numpy()
                   {"smallest": float(values[0]), "middle": float(values[1]), "biggest": float(values[2])}
               """, {"smallest": (-1.0, 0.0, CLOSED_FORM), "middle": (1.0, 0.0, CLOSED_FORM),
                     "biggest": (2.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   r = [float(v) for v in sp.all_roots(x**3 - 2*x**2 - x + 2)]
                   {"smallest": r[0], "middle": r[1], "biggest": r[2]}
               """, "SymPy all_roots",
               r="""
                   z <- sort(Re(polyroot(c(2, -1, -2, 1))))
                   list(smallest = z[1], middle = z[2], biggest = z[3])
               """),
        closed("f.find_roots", "(x - 1)^2 (x^2 + 1): the root 1 twice, and the complex roots -i and i",
               """
                   roots = sdata.formula("(x - 1)**2*(x**2 + 1)").find_roots()
                   {"rows": roots.count_rows(), "times of 1": float(roots.get_column("times").as_numpy()[0])}
               """, {"rows": (3.0, 0.0, CLOSED_FORM + ": 1, -i and i"), "times of 1": (2.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   found = sp.all_roots((x - 1)**2*(x**2 + 1))
                   {"rows": len(set(found)), "times of 1": found.count(1)}
               """, "SymPy all_roots"),
        closed("f.find_roots", "the one real root of x^5 - x + 1, which has no formula in roots (Abel-Ruffini)",
               """
                   roots = sdata.formula("x**5 - x + 1").find_roots(real_only=True)
                   r = float(roots.get_column("root").as_numpy()[0])
                   {"root": r, "f(root)": r**5 - r + 1, "real roots": roots.count_rows()}
               """, {"f(root)": (0.0, 1e-14, CLOSED_FORM + ": the formula is 0 at its root"),
                     "real roots": (1.0, 0.0, CLOSED_FORM + ": x^5 - x + 1 rises everywhere but on (-0.67, 0.67), "
                                    "where it stays above 0")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   r = float(sp.real_roots(x**5 - x + 1)[0])
                   {"root": r, "f(root)": r**5 - r + 1, "real roots": len(sp.real_roots(x**5 - x + 1))}
               """, "SymPy real_roots",
               r="""
                   z <- polyroot(c(1, -1, 0, 0, 0, 1))
                   list(root = Re(z[abs(Im(z)) < 1e-9]))
               """, option="real_only="),
        closed("f.find_roots", "2x^3 - 3x^2 - 2x + 3 = (2x - 3)(x^2 - 1): the fraction roots -1, 1 and 3/2",
               """
                   roots = sdata.formula("2*x**3 - 3*x**2 - 2*x + 3").find_roots(fractions_only=True)
                   values = roots.get_column("root").as_numpy()
                   {"smallest": float(values[0]), "biggest": float(values[2])}
               """, {"smallest": (-1.0, 0.0, CLOSED_FORM), "biggest": (1.5, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   r = sorted(float(v) for v in sp.ground_roots(2*x**3 - 3*x**2 - 2*x + 3))
                   {"smallest": r[0], "biggest": r[2]}
               """, "SymPy ground_roots", option="fractions_only="),
        closed("f.find_roots", "exactly=False: the real root of x^3 - 2 is the cube root of 2 (OEIS A002580)",
               """
                   roots = sdata.formula("x**3 - 2").find_roots(exactly=False)
                   {"real root": float(roots.get_column("root").as_numpy()[0])}
               """, {"real root": (CUBE_ROOT_2, 1e-14, "OEIS A002580: 1.25992104989487316476...")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"real root": float(sp.nroots(x**3 - 2, n=15)[0])}
               """, "SymPy nroots",
               r="""
                   z <- polyroot(c(-2, 0, 0, 1))
                   list(`real root` = Re(z[abs(Im(z)) < 1e-9]))
               """, option="exactly="),
        closed("f.find_roots", 'show="count": x^3 - 2x^2 - x + 2 has 3 different real roots (Sturm)',
               """
                   {"count": sdata.formula("x**3 - 2*x**2 - x + 2").find_roots(show="count"),
                    "between 0 and 3": len(sdata.formula("x**3 - 2*x**2 - x + 2").find_roots(between=[0, 3])
                                           .get_column("root").as_numpy())}
               """, {"count": (3.0, 0.0, CLOSED_FORM), "between 0 and 3": (2.0, 0.0, CLOSED_FORM + ": 1 and 2")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"count": sp.count_roots(x**3 - 2*x**2 - x + 2),
                    "between 0 and 3": sp.count_roots(x**3 - 2*x**2 - x + 2, 0, 3)}
               """, "SymPy count_roots", option="show="),
        closed("f.find_roots", 'show="intervals", within=0.001: an interval narrower than 0.001 around sqrt(2)',
               """
                   found = sdata.formula("x**2 - 2").find_roots(show="intervals", within=0.001)
                   low, high = found.get_column("from").as_numpy()[1], found.get_column("to").as_numpy()[1]
                   {"sqrt(2) inside": float(low <= math.sqrt(2) <= high), "narrow": float(high - low <= 0.001)}
               """, {"sqrt(2) inside": (1.0, 0.0, CLOSED_FORM), "narrow": (1.0, 0.0, "within=0.001")},
               """
                   import math
                   import sympy as sp
                   x = sp.Symbol("x")
                   (low, high), _ = sp.intervals(x**2 - 2, eps=sp.Rational(1, 1000))[1]
                   {"sqrt(2) inside": float(low <= math.sqrt(2) <= high), "narrow": float(high - low <= 0.001)}
               """, "SymPy intervals", option="within="),
        # ---------------------------------------------------------------- find_degree
        closed("f.find_degree", "x^3 y + x y^2 + 1: total degree 4, degree 3 in x and 2 in y",
               """
                   formula = sdata.formula("x**3*y + x*y**2 + 1")
                   each = formula.find_degree(for_letter=["x", "y"])
                   {"total": formula.find_degree(), "in x": each["x"], "in y": each["y"]}
               """, {"total": (4.0, 0.0, CLOSED_FORM), "in x": (3.0, 0.0, CLOSED_FORM),
                     "in y": (2.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   x, y = sp.symbols("x y")
                   f = x**3*y + x*y**2 + 1
                   {"total": sp.total_degree(f), "in x": sp.degree(f, x), "in y": sp.degree(f, y)}
               """, "SymPy total_degree and degree"),
        # ---------------------------------------------------------------- divide_by
        closed("f.divide_by", "(x^3 - 2x + 5) / (x - 1): quotient x^2 + x - 1, remainder f(1) = 4",
               """
                   quotient, remainder = sdata.formula("x**3 - 2*x + 5").divide_by("x - 1")
                   {"quotient at 2": quotient.find_value_at(x=2), "remainder": remainder.find_value_at()}
               """, {"quotient at 2": (5.0, 0.0, CLOSED_FORM + ": 4 + 2 - 1"),
                     "remainder": (4.0, 0.0, "the remainder theorem: f(1) = 1 - 2 + 5")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   q, r = sp.div(x**3 - 2*x + 5, x - 1, x)
                   {"quotient at 2": float(q.subs(x, 2)), "remainder": float(r)}
               """, "SymPy div",
               r="""
                   d <- pracma::deconv(c(1, 0, -2, 5), c(1, -1))
                   list(`quotient at 2` = sum(d$q * 2^(2:0)), remainder = d$r[length(d$r)])
               """, r_packages=("pracma",)),
        closed("f.divide_by", "without_fractions=True: 8(x^3 - 2x + 5) = (2x - 1)(4x^2 + 2x - 7) + 33",
               """
                   quotient, remainder = sdata.formula("x**3 - 2*x + 5").divide_by("2*x - 1", without_fractions=True)
                   {"quotient at 1": quotient.find_value_at(x=1), "remainder": remainder.find_value_at()}
               """, {"quotient at 1": (-1.0, 0.0, CLOSED_FORM + ": 4 + 2 - 7"),
                     "remainder": (33.0, 0.0, CLOSED_FORM + ": 2^3 f(1/2) = 8 * 33/8")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   q, r = sp.pdiv(x**3 - 2*x + 5, 2*x - 1, x)
                   {"quotient at 1": float(q.subs(x, 1)), "remainder": float(r)}
               """, "SymPy pdiv", option="without_fractions="),
        # ---------------------------------------------------------------- common factor and multiple
        closed("f.find_common_factor_with", "gcd((x + 1)^2, (x - 1)(x + 1)) = x + 1 and lcm = (x - 1)(x + 1)^2",
               """
                   formula = sdata.formula("x**2 + 2*x + 1")
                   factor = formula.find_common_factor_with("x**2 - 1")
                   multiple = formula.find_common_multiple_with("x**2 - 1")
                   {"factor at 2": factor.find_value_at(x=2), "multiple at 2": multiple.find_value_at(x=2)}
               """, {"factor at 2": (3.0, 0.0, CLOSED_FORM + ": x + 1"),
                     "multiple at 2": (9.0, 0.0, CLOSED_FORM + ": (x - 1)(x + 1)^2")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   f, g = x**2 + 2*x + 1, x**2 - 1
                   {"factor at 2": float(sp.gcd(f, g).subs(x, 2)), "multiple at 2": float(sp.lcm(f, g).subs(x, 2))}
               """, "SymPy gcd and lcm"),
        closed("f.find_common_factor_with", 'show="combination": s f + t g = gcd(f, g) (Bezout\'s identity)',
               """
                   f = sdata.formula("x**2 - 1")
                   s, t, h = f.find_common_factor_with("x**2 + 3*x + 2", show="combination")
                   both = sdata.formula(f"({s})*(x**2 - 1) + ({t})*(x**2 + 3*x + 2) - ({h})")
                   both.make_simpler()
                   {"s f + t g - h": both.find_value_at(), "h at 0": h.find_value_at(x=0)}
               """, {"s f + t g - h": (0.0, 0.0, "Bezout's identity"), "h at 0": (1.0, 0.0, CLOSED_FORM + ": x + 1")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   s, t, h = sp.gcdex(x**2 - 1, x**2 + 3*x + 2, x)
                   {"s f + t g - h": float(sp.simplify(s*(x**2 - 1) + t*(x**2 + 3*x + 2) - h)),
                    "h at 0": float(h.subs(x, 0))}
               """, "SymPy gcdex", option="show="),
        # ---------------------------------------------------------------- fractions and parts
        closed("f.turn_into_one_fraction", "1/x + 1/(x + 1) = (2x + 1) / (x (x + 1)); top and bottom",
               """
                   formula = sdata.formula("1/x + 1/(x + 1)")
                   formula.turn_into_one_fraction()
                   top, bottom = formula.split_into_top_and_bottom()
                   {"top at 2": top.find_value_at(x=2), "bottom at 2": bottom.find_value_at(x=2)}
               """, {"top at 2": (5.0, 0.0, CLOSED_FORM + ": 2x + 1"), "bottom at 2": (6.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   top, bottom = sp.fraction(sp.together(1/x + 1/(x + 1)))
                   {"top at 2": float(top.subs(x, 2)), "bottom at 2": float(bottom.subs(x, 2))}
               """, "SymPy together and fraction"),
        closed("f.find_repeated_parts", "(x + 1)^2 + sin(x + 1): the repeated part x + 1, worked out once",
               """
                   parts, shorter = sdata.formula("(x + 1)**2 + sin(x + 1)").find_repeated_parts()
                   {"parts": len(parts), "part at 2": parts["x0"].find_value_at(x=2),
                    "shorter at x0 = 3": shorter.find_value_at(x0=3)}
               """, {"parts": (1.0, 0.0, CLOSED_FORM), "part at 2": (3.0, 0.0, CLOSED_FORM),
                     "shorter at x0 = 3": (9 + math.sin(3), 1e-15, CLOSED_FORM + ": 9 + sin(3)")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   parts, shorter = sp.cse((x + 1)**2 + sp.sin(x + 1))
                   x0 = parts[0][0]
                   {"parts": len(parts), "part at 2": float(parts[0][1].subs(x, 2)),
                    "shorter at x0 = 3": float(shorter[0].subs(x0, 3))}
               """, "SymPy cse"),
        # ---------------------------------------------------------------- find_fact
        closed("f.find_fact", "discriminants: b^2 - 4ac = 5 for x^2 - 3x + 1, -4p^3 - 27q^2 = -23 for x^3 - x + 1",
               """
                   {"quadratic": sdata.formula("x**2 - 3*x + 1").find_fact("discriminant"),
                    "cubic": sdata.formula("x**3 - x + 1").find_fact("discriminant")}
               """, {"quadratic": (5.0, 0.0, CLOSED_FORM + ": 9 - 4"),
                     "cubic": (-23.0, 0.0, CLOSED_FORM + ": -4(-1)^3 - 27(1)^2")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"quadratic": float(sp.discriminant(x**2 - 3*x + 1)), "cubic": float(sp.discriminant(x**3 - x + 1))}
               """, "SymPy discriminant"),
        closed("f.find_fact", "the minimal polynomial of sqrt(2) + sqrt(3) is x^4 - 10x^2 + 1",
               """
                   found = sdata.formula("sqrt(2) + sqrt(3)").find_fact("minimal polynomial")
                   {"at 0": found.find_value_at(x=0), "at 1": found.find_value_at(x=1)}
               """, {"at 0": (1.0, 0.0, CLOSED_FORM), "at 1": (-8.0, 0.0, CLOSED_FORM + ": 1 - 10 + 1")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   m = sp.minimal_polynomial(sp.sqrt(2) + sp.sqrt(3), x)
                   {"at 0": float(m.subs(x, 0)), "at 1": float(m.subs(x, 1))}
               """, "SymPy minimal_polynomial"),
        closed("f.find_fact", "resultant(x^2 - 3x + 1, x - 1) = f(1) = -1 (other=)",
               """
                   {"resultant": sdata.formula("x**2 - 3*x + 1").find_fact("resultant", other="x - 1")}
               """, {"resultant": (-1.0, 0.0, CLOSED_FORM + ": the resultant with x - a is f(a) for degree 2")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"resultant": float(sp.resultant(x**2 - 3*x + 1, x - 1, x))}
               """, "SymPy resultant", option="other="),
        closed("f.find_fact", "power=2: the squares of the roots of x^2 - 3x + 1 are the roots of x^2 - 7x + 1",
               """
                   found = sdata.formula("x**2 - 3*x + 1").find_fact("powers of roots", power=2)
                   {"at 0": found.find_value_at(x=0), "at 1": found.find_value_at(x=1)}
               """, {"at 0": (1.0, 0.0, CLOSED_FORM + ": r1^2 r2^2 = 1"),
                     "at 1": (-5.0, 0.0, CLOSED_FORM + ": r1^2 + r2^2 = 9 - 2 = 7")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   p = sp.nth_power_roots_poly(x**2 - 3*x + 1, 2, x)
                   {"at 0": float(p.subs(x, 0)), "at 1": float(p.subs(x, 1))}
               """, "SymPy nth_power_roots_poly", option="power="),
        # ---------------------------------------------------------------- by= values
        closed("f.make_simpler", 'by="trig functions": sin^2 x + cos^2 x = 1; by="powers": x^a x^b = x^(a + b)',
               """
                   one = sdata.formula("sin(x)**2 + cos(x)**2")
                   one.make_simpler(by="trig functions")
                   powers = sdata.formula("x**a * x**b")
                   powers.make_simpler(by="powers")
                   {"trig": one.find_value_at(), "powers at x=2, a=1, b=2": powers.find_value_at(x=2, a=1, b=2),
                    "one power": float(len(powers.as_sympy().args))}
               """, {"trig": (1.0, 0.0, CLOSED_FORM), "powers at x=2, a=1, b=2": (8.0, 0.0, CLOSED_FORM),
                     "one power": (2.0, 0.0, CLOSED_FORM + ": x**(a + b) has a base and a power")},
               """
                   import sympy as sp
                   a, b, x = sp.symbols("a b x")
                   p = sp.powsimp(x**a * x**b)
                   {"trig": float(sp.trigsimp(sp.sin(x)**2 + sp.cos(x)**2)),
                    "powers at x=2, a=1, b=2": float(p.subs({x: 2, a: 1, b: 2})), "one power": float(len(p.args))}
               """, "SymPy trigsimp and powsimp", option="by="),
        closed("f.turn_into_sum", 'by="trig functions": sin(a + b) = sin a cos b + cos a sin b',
               """
                   formula = sdata.formula("sin(a + b)")
                   formula.turn_into_sum(by="trig functions")
                   {"terms": float(len(formula.as_sympy().args)), "at a=0.3, b=0.5": formula.find_value_at(a=0.3, b=0.5)}
               """, {"terms": (2.0, 0.0, CLOSED_FORM), "at a=0.3, b=0.5": (math.sin(0.8), 1e-15, CLOSED_FORM)},
               """
                   import sympy as sp
                   a, b = sp.symbols("a b")
                   g = sp.expand_trig(sp.sin(a + b))
                   {"terms": float(len(g.args)), "at a=0.3, b=0.5": float(g.subs({a: 0.3, b: 0.5}))}
               """, "SymPy expand_trig", option="by="),
        closed("f.turn_into_product", 'by="nested": Horner\'s form of x^3 + 2x + 1 is x (x^2 + 2) + 1',
               """
                   formula = sdata.formula("x**3 + 2*x + 1")
                   formula.turn_into_product(by="nested")
                   {"at 2": formula.find_value_at(x=2), "outer terms": float(len(formula.as_sympy().args))}
               """, {"at 2": (13.0, 0.0, CLOSED_FORM), "outer terms": (2.0, 0.0, CLOSED_FORM + ": x*(...) and 1")},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   h = sp.horner(x**3 + 2*x + 1)
                   {"at 2": float(h.subs(x, 2)), "outer terms": float(len(h.args))}
               """, "SymPy horner", option="by="),
        # ---------------------------------------------------------------- SymPy's names in formula text
        closed("sdata.formula", "SymPy counting names in formula text: fibonacci(30), catalan(10), bell(10), "
                                "partition(50), factorial(10) (OEIS)",
               """
                   {name: sdata.formula(f"{name}({n})").find_value_at()
                    for name, n in [("fibonacci", 30), ("catalan", 10), ("bell", 10), ("partition", 50),
                                    ("factorial", 10), ("subfactorial", 10), ("lucas", 20), ("totient", 36),
                                    ("primepi", 100)]}
               """, {"fibonacci": (832040.0, 0.0, OEIS + " A000045"), "catalan": (16796.0, 0.0, OEIS + " A000108"),
                     "bell": (115975.0, 0.0, OEIS + " A000110"), "partition": (204226.0, 0.0, OEIS + " A000041"),
                     "factorial": (3628800.0, 0.0, OEIS + " A000142"),
                     "subfactorial": (1334961.0, 0.0, OEIS + " A000166"), "lucas": (15127.0, 0.0, OEIS + " A000032"),
                     "totient": (12.0, 0.0, OEIS + " A000010"), "primepi": (25.0, 0.0, OEIS + " A000720")},
               """
                   import sympy as sp
                   {name: float(getattr(sp, name)(n))
                    for name, n in [("fibonacci", 30), ("catalan", 10), ("bell", 10), ("partition", 50),
                                    ("factorial", 10), ("subfactorial", 10), ("lucas", 20), ("totient", 36),
                                    ("primepi", 100)]}
               """, "SymPy's functions",
               r="""
                   list(factorial = factorial(10), catalan = choose(20, 10) / 11)
               """),
        closed("sdata.formula", "SymPy constants in formula text: Catalan, EulerGamma and GoldenRatio",
               """
                   {name: sdata.formula(name).find_value_at() for name in ("Catalan", "EulerGamma", "GoldenRatio")}
               """, {"Catalan": (0.91596559417721901505, 1e-15, OEIS + " A006752"),
                     "EulerGamma": (0.57721566490153286061, 1e-15, OEIS + " A001620"),
                     "GoldenRatio": ((1 + math.sqrt(5)) / 2, 1e-15, CLOSED_FORM + ": (1 + sqrt(5))/2")},
               """
                   import sympy as sp
                   {name: float(getattr(sp, name)) for name in ("Catalan", "EulerGamma", "GoldenRatio")}
               """, "SymPy's constants",
               r="""
                   list(GoldenRatio = (1 + sqrt(5)) / 2, EulerGamma = -digamma(1))
               """),
        closed("sdata.formula", "SymPy functions in formula text: cot, sec, csc, Max, floor, harmonic, Piecewise",
               """
                   {"cot(pi/4)": sdata.formula("cot(pi/4)").find_value_at(),
                    "sec(pi/3)": sdata.formula("sec(pi/3)").find_value_at(),
                    "csc(pi/6)": sdata.formula("csc(pi/6)").find_value_at(),
                    "Max(2, 7, 3)": sdata.formula("Max(2, 7, 3)").find_value_at(),
                    "floor(-7/2)": sdata.formula("floor(-7/2)").find_value_at(),
                    "harmonic(10)": sdata.formula("harmonic(10)").find_value_at(),
                    "Piecewise at -2": sdata.formula("Piecewise((x, x > 0), (0, True))").find_value_at(x=-2)}
               """, {"cot(pi/4)": (1.0, 1e-15, CLOSED_FORM), "sec(pi/3)": (2.0, 1e-15, CLOSED_FORM),
                     "csc(pi/6)": (2.0, 1e-15, CLOSED_FORM), "Max(2, 7, 3)": (7.0, 0.0, CLOSED_FORM),
                     "floor(-7/2)": (-4.0, 0.0, CLOSED_FORM), "harmonic(10)": (7381 / 2520, 1e-15, OEIS + " A001008 "
                                                                               "/ A002805: 7381/2520"),
                     "Piecewise at -2": (0.0, 0.0, CLOSED_FORM)},
               """
                   import sympy as sp
                   x = sp.Symbol("x")
                   {"cot(pi/4)": float(sp.cot(sp.pi/4)), "sec(pi/3)": float(sp.sec(sp.pi/3)),
                    "csc(pi/6)": float(sp.csc(sp.pi/6)), "Max(2, 7, 3)": float(sp.Max(2, 7, 3)),
                    "floor(-7/2)": float(sp.floor(sp.Rational(-7, 2))), "harmonic(10)": float(sp.harmonic(10)),
                    "Piecewise at -2": float(sp.Piecewise((x, x > 0), (0, True)).subs(x, -2))}
               """, "SymPy's functions",
               r="""
                   list(`cot(pi/4)` = 1 / tan(pi / 4), `sec(pi/3)` = 1 / cos(pi / 3), `csc(pi/6)` = 1 / sin(pi / 6),
                        `Max(2, 7, 3)` = max(2, 7, 3), `floor(-7/2)` = floor(-7 / 2), `harmonic(10)` = sum(1 / (1:10)))
               """),
    ]
