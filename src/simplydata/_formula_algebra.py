"""Polynomial algebra on a formula (families for 100 %, batches 22-23, plan section 2.10, approved by Manish
2026-11-28, G14): formula.find_roots, find_degree, divide_by, find_common_factor_with, find_common_multiple_with,
turn_into_one_fraction, split_into_top_and_bottom, find_repeated_parts and the family find_fact("discriminant"),
and the by= values of make_simpler, turn_into_sum and turn_into_product.

Every answer comes from SymPy, each call under simplydata's one time limit (_time_limit.py), with the SymPy function
named in what is printed:

* find_roots: all_roots (real_roots with real_only=True, ground_roots with fractions_only=True, nroots with
  exactly=False, count_roots with show="count", intervals with show="intervals" and within=);
* find_degree: degree (total_degree for a formula of several letters, degree_list for a list of letters);
* divide_by: div, quo, rem (pdiv, pquo, prem with without_fractions=True; exquo and pexquo with
  with_no_remainder=True);
* find_common_factor_with: gcd (gcd_list for a list; cofactors, gcdex, half_gcdex with show=);
  find_common_multiple_with: lcm (lcm_list for a list);
* turn_into_one_fraction: together; split_into_top_and_bottom: fraction; find_repeated_parts: cse;
* find_fact(name): one SymPy function for each fact (FACTS below);
* make_simpler(by=), turn_into_sum(by=), turn_into_product(by=): one SymPy function for each value (SIMPLER, SUM,
  PRODUCT below).

Own code is glue only: reading the options, naming the letters, and writing SymPy's answers back as formulas,
numbers and tables. The words are on the formula (Formula takes them from _AlgebraWords).
"""

from __future__ import annotations

import math

from ._errors import friendly
from ._time_limit import one_deadline

# ------------------------------------------------------------------------------------------------ by= values
# make_simpler(by=): plain value -> (SymPy function, what it does). None (the default) is SymPy simplify.
SIMPLER = {
    "trig functions": ("trigsimp", "sin, cos, tan ... with the trigonometric identities"),
    "exponentials and trig": ("exptrigsimp", "exp(I*x) and cosh, sinh into each other"),
    "trig rules": ("fu", "Fu's trigonometric rules, step by step (Fu et al. 2006)"),
    "powers": ("powsimp", "powers with the same base or the same power put together"),
    "powers of powers": ("powdenest", "(x**a)**b written as one power, as the letters allow"),
    "logs": ("logcombine", "log(a) + log(b) as log(a*b), where the letters allow it"),
    "fractions": ("ratsimp", "one fraction, with common factors cancelled"),
    "common factors": ("cancel", "top and bottom as polynomials with their common factors cancelled"),
    "roots in the bottom": ("radsimp", "square roots taken out of the bottom of a fraction"),
    "nested roots": ("sqrtdenest", "sqrt(5 + 2*sqrt(6)) as sqrt(2) + sqrt(3)"),
    "gamma functions": ("gammasimp", "gamma functions put together"),
    "factorials": ("combsimp", "factorials and binomials put together"),
    "bessel functions": ("besselsimp", "Bessel functions put together"),
    "hypergeometric functions": ("hyperexpand", "hyper and meijerg written with ordinary functions"),
    "kronecker deltas": ("kroneckersimp", "KroneckerDelta put together"),
    "signs": ("signsimp", "minus signs taken out in front"),
    "letters apart": ("separatevars", "a product of parts that each have one letter, where it is one"),
    "conditions": ("piecewise_fold", "a formula with Piecewise in it written as one Piecewise"),
    "decimals as fractions": ("nsimplify", "decimals written as the exact numbers they stand for"),
}
SIMPLER_SPELLINGS = {"trig": "trig functions", "trigonometry": "trig functions", "trigsimp": "trig functions",
                     "angles": "trig functions", "exptrigsimp": "exponentials and trig", "fu": "trig rules",
                     "powsimp": "powers", "power": "powers", "powdenest": "powers of powers", "log": "logs",
                     "logcombine": "logs", "logarithms": "logs", "ratsimp": "fractions", "fraction": "fractions",
                     "cancel": "common factors", "radsimp": "roots in the bottom", "sqrtdenest": "nested roots",
                     "gammasimp": "gamma functions", "gamma": "gamma functions", "combsimp": "factorials",
                     "factorial": "factorials", "binomials": "factorials", "besselsimp": "bessel functions",
                     "bessel": "bessel functions", "hyperexpand": "hypergeometric functions",
                     "hypergeometric": "hypergeometric functions", "kroneckersimp": "kronecker deltas",
                     "signsimp": "signs", "separatevars": "letters apart",
                     "piecewise_fold": "conditions", "piecewise": "conditions", "nsimplify": "decimals as fractions",
                     "decimals": "decimals as fractions"}
# turn_into_sum(by=): plain value -> (SymPy function, what it does). None (the default) is SymPy expand.
SUM = {
    "logs": ("expand_log", "log(a*b) as log(a) + log(b), where the letters allow it"),
    "trig functions": ("expand_trig", "sin(a + b) and cos(2*x) multiplied out"),
    "powers": ("expand_power_exp", "x**(a + b) as x**a * x**b"),
    "power of a product": ("expand_power_base", "(x*y)**a as x**a * y**a, where the letters allow it"),
    "products": ("expand_mul", "products multiplied out, powers of sums kept"),
    "powers of sums": ("expand_multinomial", "(x + y)**2 multiplied out, other products kept"),
    "real and imaginary parts": ("expand_complex", "the real part plus I times the imaginary part"),
    "special functions": ("expand_func", "special functions written with simpler ones (gamma(x + 1) as x*gamma(x))"),
}
SUM_SPELLINGS = {"log": "logs", "expand_log": "logs", "logarithms": "logs", "trig": "trig functions",
                 "expand_trig": "trig functions", "trigonometry": "trig functions", "expand_power_exp": "powers",
                 "expand_power_base": "power of a product", "expand_mul": "products",
                 "expand_multinomial": "powers of sums", "multinomial": "powers of sums",
                 "expand_complex": "real and imaginary parts", "complex": "real and imaginary parts",
                 "expand_func": "special functions", "functions": "special functions"}
# turn_into_product(by=): plain value -> (SymPy function, what it does). None (the default) is SymPy factor.
PRODUCT = {
    "common factors": ("factor_terms", "the factor common to all terms taken out, without factoring further"),
    "common factors over one fraction": ("gcd_terms", "the terms over one fraction, their common factor taken out"),
    "common power of letters": ("terms_gcd", "the power of each letter common to all terms taken out"),
    "repeated factors": ("sqf", "factors grouped by how often they repeat (square-free factoring)"),
    "nested": ("horner", "Horner's nested form x*(x*(a*x + b) + c) + d, the quickest to work out"),
}
PRODUCT_SPELLINGS = {"factor_terms": "common factors", "common factor": "common factors",
                     "gcd_terms": "common factors over one fraction", "terms_gcd": "common power of letters",
                     "sqf": "repeated factors", "square-free": "repeated factors", "square free": "repeated factors",
                     "horner": "nested", "horner form": "nested"}

# ------------------------------------------------------------------------------------------------ find_fact
# plain name -> (SymPy function, what it needs, what it gives, about). Needs: None, "other" (a formula),
# "others" (a list of formulas), "number", "power", "letter" (the letter that counts).
FACTS = {
    "discriminant": ("discriminant", None, "number or formula", "b**2 - 4*a*c for a*x**2 + b*x + c, and the like "
                     "for every degree: 0 when two roots are the same"),
    "resultant": ("resultant", "other", "number or formula", "0 exactly when the two polynomials have a root in "
                  "common"),
    "subresultants": ("subresultants", "other", "formulas", "the subresultant sequence of the two polynomials"),
    "groebner basis": ("groebner", "others", "formulas", "the reduced Groebner basis of the polynomials (lex order)"),
    "minimal polynomial": ("minimal_polynomial", None, "formula", "the smallest polynomial with whole-number "
                           "coefficients that the number is a root of"),
    "galois group": ("galois_group", None, "text", "the Galois group of a polynomial of degree 6 at most"),
    "sturm sequence": ("sturm", None, "formulas", "the Sturm sequence (it counts the real roots between two values)"),
    "viete formulas": ("viete", None, "text", "the sums and products of the roots r1, r2 ... from the coefficients"),
    "leading coefficient": ("LC", None, "number or formula", "the number in front of the highest power"),
    "leading term": ("LT", None, "formula", "the term with the highest power"),
    "symmetric form": ("symmetrize", None, "formulas", "the formula in the elementary symmetric polynomials s1, s2 "
                       "..., and what is left over"),
    "number factor": ("content", None, "number", "the greatest common divisor of the coefficients"),
    "without number factor": ("primitive", None, "formula", "the polynomial divided by the number factor"),
    "factors": ("factor_list", None, "factors", "each factor with how many times it repeats"),
    "repeated factors": ("sqf_list", None, "factors", "the square-free factors with how many times each repeats"),
    "square-free part": ("sqf_part", None, "formula", "the product of the different factors, each once"),
    "factorial factors": ("gff_list", None, "factors", "the falling-factorial factors with their powers"),
    "divided by leading coefficient": ("monic", None, "formula", "the polynomial divided by its leading "
                                       "coefficient (monic)"),
    "parts it is made of": ("decompose", None, "formulas", "polynomials f1, f2 ... with f1(f2(...)) the formula"),
    "put into": ("compose", "other", "formula", "the formula with the other formula put in for its letter"),
    "inverse modulo": ("invert", "other", "formula", "the polynomial that times the formula leaves 1 after "
                       "division by the other"),
    "coefficients modulo": ("trunc", "number", "formula", "each coefficient as its remainder after division by "
                            "the number"),
    "powers of roots": ("nth_power_roots_poly", "power", "formula", "the polynomial whose roots are the roots of "
                        "the formula to the power"),
    "term ratio": ("hypersimp", "letter", "formula", "the ratio of one term to the one before, f(k + 1)/f(k), "
                   "written simply"),
    "remainder by several": ("reduced", "others", "formula", "the remainder after division by several polynomials "
                             "(lex order)"),
    "coefficients": ("Poly.all_coeffs", None, "numbers or formulas", "the coefficients from the highest power down"),
}
FACT_SPELLINGS = {"discriminant": "discriminant", "resultant": "resultant", "subresultants": "subresultants",
                  "groebner": "groebner basis", "groebner_basis": "groebner basis",
                  "minimal_polynomial": "minimal polynomial", "minpoly": "minimal polynomial",
                  "galois_group": "galois group", "sturm": "sturm sequence", "viete": "viete formulas",
                  "vieta formulas": "viete formulas", "vieta": "viete formulas", "lc": "leading coefficient",
                  "lt": "leading term", "symmetrize": "symmetric form", "content": "number factor",
                  "primitive": "without number factor", "primitive part": "without number factor",
                  "factor_list": "factors", "sqf_list": "repeated factors", "square-free factors": "repeated factors",
                  "sqf_part": "square-free part", "gff_list": "factorial factors", "monic": "divided by leading "
                  "coefficient", "decompose": "parts it is made of", "compose": "put into", "invert": "inverse modulo",
                  "trunc": "coefficients modulo", "nth_power_roots_poly": "powers of roots", "hypersimp": "term ratio",
                  "reduced": "remainder by several", "all_coeffs": "coefficients", "coeffs": "coefficients"}

ROOTS_SHOW = ("roots", "count", "intervals")
_ROOTS_HINT = (" find_roots() works exactly on whole-number and fraction coefficients; exactly=False gives the roots "
               "of any polynomial in decimals.")
# the facts of a polynomial in one letter: with several letters, for_letter= says which
ONE_LETTER = ("discriminant", "resultant", "subresultants", "sturm sequence", "parts it is made of", "put into",
              "inverse modulo", "powers of roots", "coefficients")
DIVIDE_SHOW = ("quotient and remainder", "quotient", "remainder")
FACTOR_SHOW = ("common factor", "common factor and the rest", "combination", "half combination")
DIVIDE_SHOW_SPELLINGS = {"both": "quotient and remainder", "div": "quotient and remainder", "quo": "quotient",
                         "rem": "remainder", "answer": "quotient"}
FACTOR_SHOW_SPELLINGS = {"gcd": "common factor", "cofactors": "common factor and the rest", "gcdex": "combination",
                         "half_gcdex": "half combination", "factor": "common factor"}
MAX_ROOT_POWER = 100  # powers of roots: up to this power
MAX_FACT_DEGREE = 6  # galois_group: SymPy works up to degree 6


def _value(table: dict, spellings: dict, value, step: str, option: str):
    """A plain value of an option (any capitals; SymPy's name works too), checked."""
    from ._errors import choice_error

    key = value.strip().lower() if isinstance(value, str) else value
    key = spellings.get(key, key)
    if key not in table:
        raise choice_error(step, option, value, list(table))
    return key


def by_value(table: dict, spellings: dict, by, step: str) -> str:
    return _value(table, spellings, by, step, "by")


def _polynomial_error(step: str, shown: str, problem, hint: str = "") -> Exception:
    from ._errors import SimplydataError

    return SimplydataError(f"formula.{step}() works on polynomials (sums of whole powers of letters, such as "
                           f"x**3 - 2*x + 1); SymPy could not use {shown} as one ({type(problem).__name__}: "
                           f"{problem}).{hint}")


def _poly_errors():
    """SymPy's errors that say the formula is not a polynomial it can work with."""
    from sympy.polys.polyerrors import BasePolynomialError

    return (BasePolynomialError, NotImplementedError)


class _AlgebraWords:
    """The polynomial words of a formula (Formula takes them from here)."""

    # ------------------------------------------------------------------------------------------- helpers
    def _poly(self, step: str, call, *values, what: str, hint: str = "", **named):
        """A SymPy polynomial call under the time limit, its 'not a polynomial' errors said plainly."""
        from ._formula import _guarded, _show

        try:
            return _guarded(call, *values, what=what, **named)
        except _poly_errors() as problem:
            raise _polynomial_error(step, _show(self._expr), problem, hint) from None

    def _other(self, other, step: str, example: str):
        """Another formula (text, a formula or a number) as SymPy, with this formula's letters."""
        from ._errors import SimplydataError
        from ._formula import Formula, parse

        if other is None:
            raise SimplydataError(f"formula.{step}() needs the other formula, such as formula.{example}.")
        if isinstance(other, Formula):
            return other._expr
        return parse(other, f"formula.{step}()", symbols=self._symbols())

    def _others(self, other, step: str, example: str) -> list:
        if isinstance(other, (list, tuple)):
            from ._errors import SimplydataError

            if not other:
                raise SimplydataError(f"formula.{step}() needs at least one other formula, such as "
                                      f"formula.{example}.")
            return [self._other(item, step, example) for item in other]
        return [self._other(other, step, example)]

    def _letters_for(self, step: str, for_letter, example: str, also=()) -> list:
        """The letters a polynomial is in: for_letter= (one or a list), else every letter of the formula (and of the
        other formulas), in SymPy's order."""
        from ._errors import SimplydataError

        if for_letter is None:
            found = set(self._expr.free_symbols)
            for item in also:
                found |= item.free_symbols
            return sorted(found, key=str)
        names = list(for_letter) if isinstance(for_letter, (list, tuple)) else [for_letter]
        letters = sorted({str(s) for s in self._expr.free_symbols} | {str(s) for e in also for s in e.free_symbols})
        symbols = {str(s): s for e in (self._expr, *also) for s in e.free_symbols}
        out = []
        for name in names:
            if not isinstance(name, str) or name not in letters:
                raise SimplydataError(f"for_letter= needs letters of the formula in quotes: "
                                      f"{', '.join(repr(n) for n in letters) or 'none'}.\nFor example:  "
                                      f"formula.{example}")
            out.append(symbols[name])
        return out

    # ------------------------------------------------------------------------------------------- roots
    @friendly
    @one_deadline
    def find_roots(self, real_only=False, fractions_only=False, between=None, exactly=True, show="roots",
                   within=None, fast=False):
        """The roots of a polynomial in one letter, with how many times each repeats. roots = formula.find_roots()

        formula = sdata.formula("x**3 - 2*x**2 - x + 2"), then formula.find_roots() gives the table of the roots -1,
        1 and 2, exactly and as decimals, with how many times each root repeats (SymPy all_roots; a root SymPy
        cannot write with roots is SymPy's CRootOf, worked out to any number of digits). real_only=True keeps the
        real roots (real_roots); fractions_only=True the whole-number and fraction roots (ground_roots);
        between=[0, 3] the real roots between two values. exactly=False gives decimals (nroots, 15 digits).
        show="count" counts the different real roots (count_roots); show="intervals" gives an interval around each
        real root (intervals), as narrow as within=0.001. The formula must be a polynomial in one letter with
        number coefficients; sdata.solve(..., exactly=True) solves other equations. As SymPy all_roots; R polyroot.
        """
        from ._errors import SimplydataError
        from ._formula import _guarded, _result_rows, _show, float_of, need_sympy

        sp = need_sympy("formula.find_roots()")
        key = _value({k: k for k in ROOTS_SHOW}, {"number": "count", "how many": "count"}, show, "find_roots",
                     "show")
        letters = self._letters()
        if len(letters) != 1:
            raise SimplydataError(f"formula.find_roots() works on a polynomial in one letter with number "
                                  f"coefficients; {_show(self._expr)} has "
                                  f"{len(letters) or 'no'} letter{'s' if len(letters) != 1 else ''}. For an "
                                  "equation with other letters in it, use sdata.solve(\"...\", for_letter=\"x\", "
                                  "exactly=True).")
        x = self._symbol(letters[0])
        if not self._expr.is_polynomial(x):
            raise SimplydataError(f"formula.find_roots() works on a polynomial in {x}; {_show(self._expr)} is not "
                                  "one. For the roots of a fraction, find those of its top: "
                                  "top, bottom = formula.split_into_top_and_bottom(), then top.find_roots().")
        for flag, name in ((real_only, "real_only"), (fractions_only, "fractions_only"), (exactly, "exactly"),
                           (fast, "fast")):
            if not isinstance(flag, bool):
                raise SimplydataError(f"{name}= is True or False.")
        low = high = None
        if between is not None:
            from ._formula import _limit_value

            if not isinstance(between, (list, tuple)) or len(between) != 2:
                raise SimplydataError("between= needs two values, such as between=[0, 3].")
            low, high = (_limit_value(sp, v, "between=") for v in between)
        if within is not None and key != "intervals":
            raise SimplydataError('within= is for show="intervals": how narrow each interval is.')
        if within is not None and (isinstance(within, bool) or not isinstance(within, (int, float))
                                   or not 0 < within < math.inf):
            raise SimplydataError("within= needs a number above 0, such as within=0.001.")
        shown = _show(self._expr)
        if key == "count":
            count = self._poly("find_roots", sp.count_roots, self._expr, low, high, what="SymPy count_roots")
            where = f" between {_show(low)} and {_show(high)}" if between is not None else ""
            print(f"{shown} has {count} different real root{'s' if count != 1 else ''}{where}   (SymPy count_roots)")
            return int(count)
        if key == "intervals":
            eps = None if within is None else _exact(sp, within)
            found = self._poly("find_roots", sp.intervals, self._expr, inf=low, sup=high, eps=eps,
                               what="SymPy intervals")
            rows = [{"from": float(a), "to": float(b), "from exactly": _show(a), "to exactly": _show(b),
                     "times": int(k)} for (a, b), k in found]
            print(f"The real roots of {shown} lie in: " + (", ".join(f"[{_show(a)}, {_show(b)}]"
                                                                      for (a, b), _ in found) or "none")
                  + "   (SymPy intervals)")
            return _result_rows(rows, fast) if rows else _empty_roots(fast, "intervals")
        if not exactly:
            if real_only or fractions_only:
                raise SimplydataError("exactly=False gives every root in decimals; real_only= and fractions_only= "
                                      "go with exact roots.")
            found = self._poly("find_roots", sp.nroots, self._expr, n=15, what="SymPy nroots")
            rows = []
            for root in found:
                value = complex(root)
                rows.append({"root": value.real if value.imag == 0 else math.nan, "root as text": str(root)})
            if between is not None:
                rows = [r for r in rows if not math.isnan(r["root"]) and float(low) <= r["root"] <= float(high)]
            print(f"The roots of {shown} in decimals: " + (", ".join(r["root as text"] for r in rows) or "none")
                  + "   (SymPy nroots)")
            return _result_rows(rows, fast) if rows else _empty_roots(fast, "decimals")
        if fractions_only:
            found = self._poly("find_roots", sp.ground_roots, self._expr, what="SymPy ground_roots", hint=_ROOTS_HINT)
            pairs = sorted(found.items(), key=lambda item: float(item[0]))
            how = "SymPy ground_roots"
        else:
            listed = self._poly("find_roots", sp.real_roots if real_only or between is not None else sp.all_roots,
                                self._expr, what="SymPy real_roots" if real_only or between is not None
                                else "SymPy all_roots", hint=_ROOTS_HINT)
            pairs = []
            for root in listed:  # SymPy lists a root that repeats once for each time, side by side
                if pairs and pairs[-1][0] == root:
                    pairs[-1] = (root, pairs[-1][1] + 1)
                else:
                    pairs.append((root, 1))
            how = "SymPy real_roots" if real_only or between is not None else "SymPy all_roots"
        if between is not None:
            pairs = [(r, k) for r, k in pairs if _guarded(sp.Le, low, r, what="SymPy Le") == sp.true
                     and _guarded(sp.Le, r, high, what="SymPy Le") == sp.true]
        rows = []
        for root, times in pairs:
            value = float_of(root)
            rows.append({"root": value, "root exactly": _show(root), "times": int(times)})
        said = ", ".join(f"{r['root exactly']}" + (f" ({r['times']} times)" if r["times"] > 1 else "") for r in rows)
        print(f"The roots of {shown}: {said or 'none'}   ({how})")
        if any(math.isnan(r["root"]) for r in rows):
            print("A root that is not an ordinary (real) number has an empty decimal; its exact form is in the "
                  "table.")
        return _result_rows(rows, fast) if rows else _empty_roots(fast, "exact")

    # ------------------------------------------------------------------------------------------- degree
    @friendly
    def find_degree(self, for_letter=None):
        """The degree of a polynomial: its highest power. degree = formula.find_degree()

        formula = sdata.formula("x**3*y + x*y**2 + 1"), then formula.find_degree(for_letter="x") gives 3, the highest
        power of x (SymPy degree). Without for_letter=, a formula of one letter gives its highest power and one of
        several letters its total degree, the highest sum of powers in one term (4 here; SymPy total_degree).
        for_letter=["x", "y"] gives the degree in each letter (SymPy degree_list). 0 has no degree: SymPy gives
        minus infinity. As SymPy degree; MATLAB polynomialDegree.
        """
        from ._errors import SimplydataError
        from ._formula import _show, need_sympy

        sp = need_sympy("formula.find_degree()")
        example = 'find_degree(for_letter="x")'
        letters = self._letters_for("find_degree", for_letter, example)
        if not self._expr.is_polynomial(*letters):
            raise SimplydataError(f"formula.find_degree() works on a polynomial (whole powers of letters); "
                                  f"{_show(self._expr)} is not one.")
        shown = _show(self._expr)
        if isinstance(for_letter, (list, tuple)):
            found = self._poly("find_degree", sp.degree_list, self._expr, *letters, what="SymPy degree_list")
            answer = {str(s): _whole_or_minus_infinity(d) for s, d in zip(letters, found)}
            print(f"The degree of {shown} in " + ", ".join(f"{n}: {d}" for n, d in answer.items())
                  + "   (SymPy degree_list)")
            return answer
        if for_letter is None and len(letters) > 1:
            found = self._poly("find_degree", sp.total_degree, self._expr, *letters, what="SymPy total_degree")
            print(f"The total degree of {shown}: {_show(found)}, the highest sum of powers in one term   "
                  "(SymPy total_degree)")
            return _whole_or_minus_infinity(found)
        if letters:
            found = self._poly("find_degree", sp.degree, self._expr, letters[0], what="SymPy degree")
            print(f"The degree of {shown} in {letters[0]}: {_show(found)}   (SymPy degree)")
        else:
            found = self._poly("find_degree", sp.degree, self._expr, what="SymPy degree")
            print(f"The degree of {shown}: {_show(found)}   (SymPy degree)")
        if found == -sp.oo:
            print("0 has no degree; SymPy writes minus infinity.")
        return _whole_or_minus_infinity(found)

    # ------------------------------------------------------------------------------------------- division
    @friendly
    @one_deadline
    def divide_by(self, other=None, show="quotient and remainder", without_fractions=False, with_no_remainder=False,
                  for_letter=None):
        """Divide a polynomial by another: the quotient and the remainder. answer = formula.divide_by("x - 1")

        formula = sdata.formula("x**3 - 2*x + 5"), then quotient, remainder = formula.divide_by("x - 1") gives
        x**2 + x - 1 and 4: x**3 - 2*x + 5 = (x - 1)*(x**2 + x - 1) + 4 (SymPy div). show="quotient" or
        show="remainder" gives one of them (quo, rem). without_fractions=True multiplies the formula by a power of
        the other's leading coefficient first, so no fractions appear (pseudo-division: pdiv, pquo, prem).
        with_no_remainder=True gives the quotient and stops when the division leaves a remainder (exquo, pexquo).
        for_letter= says which letter when there are several. The formula itself does not change. As SymPy div;
        MATLAB deconv; R polynom's division.
        """
        from ._errors import SimplydataError
        from ._formula import Formula, _show, need_sympy

        sp = need_sympy("formula.divide_by()")
        example = 'divide_by("x - 1")'
        g = self._other(other, "divide_by", example)
        key = _value({k: k for k in DIVIDE_SHOW}, DIVIDE_SHOW_SPELLINGS, show, "divide_by", "show")
        for flag, name in ((without_fractions, "without_fractions"), (with_no_remainder, "with_no_remainder")):
            if not isinstance(flag, bool):
                raise SimplydataError(f"{name}= is True or False.")
        if with_no_remainder and key == "remainder":
            raise SimplydataError('with_no_remainder=True gives the quotient: leave out show="remainder".')
        letters = self._letters_for("divide_by", for_letter, 'divide_by("x - 1", for_letter="x")', also=(g,))
        if g == 0:
            raise SimplydataError("A polynomial cannot be divided by 0.")
        shown, by = _show(self._expr), _show(g)
        if with_no_remainder:
            call, name = (sp.pexquo, "pexquo") if without_fractions else (sp.exquo, "exquo")
            try:
                found = self._poly("divide_by", call, self._expr, g, *letters, what=f"SymPy {name}")
            except SimplydataError as problem:
                if "ExactQuotientFailed" in str(problem):
                    raise SimplydataError(f"{shown} does not divide by {by} without a remainder (SymPy {name}); "
                                          "leave out with_no_remainder=True to see the remainder.") from None
                raise
            print(f"{shown} divided by {by}: {_show(found)}, with no remainder   (SymPy {name})")
            return Formula(found)
        if key == "quotient and remainder":
            call, name = (sp.pdiv, "pdiv") if without_fractions else (sp.div, "div")
            quotient, remainder = self._poly("divide_by", call, self._expr, g, *letters, what=f"SymPy {name}")
            print(f"{shown} divided by {by}: the quotient {_show(quotient)} and the remainder {_show(remainder)}   "
                  f"(SymPy {name})")
            return Formula(quotient), Formula(remainder)
        if key == "quotient":
            call, name = (sp.pquo, "pquo") if without_fractions else (sp.quo, "quo")
        else:
            call, name = (sp.prem, "prem") if without_fractions else (sp.rem, "rem")
        found = self._poly("divide_by", call, self._expr, g, *letters, what=f"SymPy {name}")
        print(f"{shown} divided by {by}: the {key} {_show(found)}   (SymPy {name})")
        return Formula(found)

    # ------------------------------------------------------------------------------------------- gcd and lcm
    @friendly
    def find_common_factor_with(self, other=None, show="common factor", for_letter=None):
        """The greatest common factor with another polynomial. answer = formula.find_common_factor_with("x**2 - 1")

        formula = sdata.formula("x**2 + 2*x + 1"), then formula.find_common_factor_with("x**2 - 1") gives x + 1
        (SymPy gcd; a list of formulas uses gcd_list). show="common factor and the rest" also gives what is left of
        each after dividing by it (cofactors); show="combination" gives s, t and the factor h with
        s*formula + t*other = h (gcdex, one letter); show="half combination" gives s and h (half_gcdex). The formula
        itself does not change. As SymPy gcd; MATLAB gcd.
        """
        from ._errors import SimplydataError
        from ._formula import Formula, _show, need_sympy

        sp = need_sympy("formula.find_common_factor_with()")
        example = 'find_common_factor_with("x**2 - 1")'
        key = _value({k: k for k in FACTOR_SHOW}, FACTOR_SHOW_SPELLINGS, show, "find_common_factor_with", "show")
        others = self._others(other, "find_common_factor_with", example)
        letters = self._letters_for("find_common_factor_with", for_letter, example, also=others)
        shown = _show(self._expr)
        if len(others) > 1 or isinstance(other, (list, tuple)):
            if key != "common factor":
                raise SimplydataError(f'show="{key}" works with one other formula, not a list.')
            found = self._poly("find_common_factor_with", sp.gcd_list, [self._expr, *others], *letters,
                               what="SymPy gcd_list")
            print(f"The greatest common factor of {shown} and {', '.join(_show(o) for o in others)}: {_show(found)}"
                  "   (SymPy gcd_list)")
            return Formula(found)
        g = others[0]
        if key == "common factor":
            found = self._poly("find_common_factor_with", sp.gcd, self._expr, g, *letters, what="SymPy gcd")
            print(f"The greatest common factor of {shown} and {_show(g)}: {_show(found)}   (SymPy gcd)")
            return Formula(found)
        if key == "common factor and the rest":
            h, rest_f, rest_g = self._poly("find_common_factor_with", sp.cofactors, self._expr, g, *letters,
                                           what="SymPy cofactors")
            print(f"The greatest common factor of {shown} and {_show(g)}: {_show(h)}; what is left: {_show(rest_f)} "
                  f"and {_show(rest_g)}   (SymPy cofactors)")
            return Formula(h), Formula(rest_f), Formula(rest_g)
        if len(letters) != 1:
            raise SimplydataError(f'show="{key}" works on polynomials in one letter; say which with for_letter=.')
        if key == "combination":
            s, t, h = self._poly("find_common_factor_with", sp.gcdex, self._expr, g, *letters, what="SymPy gcdex")
            print(f"({_show(s)})*({shown}) + ({_show(t)})*({_show(g)}) = {_show(h)}, the greatest common factor   "
                  "(SymPy gcdex)")
            return Formula(s), Formula(t), Formula(h)
        s, h = self._poly("find_common_factor_with", sp.half_gcdex, self._expr, g, *letters, what="SymPy half_gcdex")
        print(f"({_show(s)})*({shown}) = {_show(h)} after division by {_show(g)}: h = {_show(h)} is the greatest "
              "common factor   (SymPy half_gcdex)")
        return Formula(s), Formula(h)

    @friendly
    def find_common_multiple_with(self, other=None, for_letter=None):
        """The least common multiple with another polynomial. answer = formula.find_common_multiple_with("x**2 - 1")

        formula = sdata.formula("x**2 + 2*x + 1"), then formula.find_common_multiple_with("x**2 - 1") gives
        (x - 1)*(x + 1)**2 multiplied out (SymPy lcm; a list of formulas uses lcm_list). The formula itself does not
        change. As SymPy lcm; MATLAB lcm.
        """
        from ._formula import Formula, _show, need_sympy

        sp = need_sympy("formula.find_common_multiple_with()")
        example = 'find_common_multiple_with("x**2 - 1")'
        others = self._others(other, "find_common_multiple_with", example)
        letters = self._letters_for("find_common_multiple_with", for_letter, example, also=others)
        shown = _show(self._expr)
        if len(others) > 1 or isinstance(other, (list, tuple)):
            found = self._poly("find_common_multiple_with", sp.lcm_list, [self._expr, *others], *letters,
                               what="SymPy lcm_list")
            how = "SymPy lcm_list"
        else:
            found = self._poly("find_common_multiple_with", sp.lcm, self._expr, others[0], *letters,
                               what="SymPy lcm")
            how = "SymPy lcm"
        print(f"The least common multiple of {shown} and {', '.join(_show(o) for o in others)}: {_show(found)}   "
              f"({how})")
        return Formula(found)

    # ------------------------------------------------------------------------------------------- fractions
    @friendly
    def turn_into_one_fraction(self):
        """Write a sum of fractions as one fraction (SymPy together). formula.turn_into_one_fraction()

        formula = sdata.formula("1/x + 1/(x + 1)"), then formula.turn_into_one_fraction() gives
        (2*x + 1)/(x*(x + 1)). The formula changes; formula.undo() takes the step back.
        turn_into_partial_fractions() goes the other way. As SymPy together.
        """
        from ._formula import _guarded, _show, need_sympy

        sp = need_sympy("formula.turn_into_one_fraction()")
        new = _guarded(sp.together, self._expr, what="SymPy together")
        print(f"{_show(self._expr)} as one fraction: {_show(new)}   (SymPy together)")
        return self._change("turn into one fraction", new)

    @friendly
    def split_into_top_and_bottom(self):
        """The top and the bottom of a fraction, as two formulas. top, bottom = formula.split_into_top_and_bottom()

        formula = sdata.formula("(x + 1)/(x - 2)"), then top, bottom = formula.split_into_top_and_bottom() gives
        x + 1 and x - 2 (SymPy fraction). A formula that is not a fraction has 1 at the bottom. Put it over one
        fraction first with formula.turn_into_one_fraction(). The formula itself does not change. As SymPy
        fraction (numer, denom); MATLAB numden.
        """
        from ._formula import Formula, _guarded, _show, need_sympy

        sp = need_sympy("formula.split_into_top_and_bottom()")
        top, bottom = _guarded(sp.fraction, self._expr, what="SymPy fraction")
        print(f"{_show(self._expr)}: the top is {_show(top)} and the bottom {_show(bottom)}   (SymPy fraction)")
        return Formula(top), Formula(bottom)

    @friendly
    def find_repeated_parts(self):
        """The parts a formula repeats, each with a short name. parts, shorter = formula.find_repeated_parts()

        formula = sdata.formula("(x + 1)**2 + sin(x + 1)"), then parts, shorter = formula.find_repeated_parts()
        gives {"x0": x + 1} and x0**2 + sin(x0) (SymPy cse, common subexpression elimination): work out each
        part once, then the shorter formula. The names x0, x1 ... are never letters of the formula. The formula
        itself does not change. As SymPy cse.
        """
        from ._formula import Formula, _guarded, _show, need_sympy

        sp = need_sympy("formula.find_repeated_parts()")
        replacements, reduced = _guarded(sp.cse, self._expr, what="SymPy cse")
        parts = {str(name): Formula(part) for name, part in replacements}
        shorter = reduced[0]
        if parts:
            print(f"{_show(self._expr)} repeats " + ", ".join(f"{n} = {_show(p._expr)}" for n, p in parts.items())
                  + f"; with them it is {_show(shorter)}   (SymPy cse)")
        else:
            print(f"{_show(self._expr)} has no repeated part   (SymPy cse)")
        return parts, Formula(shorter)

    # ------------------------------------------------------------------------------------------- the family
    @friendly
    @one_deadline
    def find_fact(self, name=None, other=None, power=None, for_letter=None):
        """A rarer fact of a polynomial, by name (SymPy's polynomial tools). answer = formula.find_fact("discriminant")

        formula = sdata.formula("x**2 - 3*x + 1"), then formula.find_fact("discriminant") gives 5 (SymPy
        discriminant). Names: "discriminant", "resultant" and "subresultants" (with other=), "groebner basis" and
        "remainder by several" (other= a list of formulas), "minimal polynomial" (of a number such as
        sqrt(2) + sqrt(3), in the letter for_letter=, x by itself), "galois group", "sturm sequence", "viete
        formulas", "leading coefficient", "leading term", "symmetric form", "number factor", "without number
        factor", "factors", "repeated factors", "square-free part", "factorial factors", "divided by leading
        coefficient", "parts it is made of", "put into" (other=), "inverse modulo" (other=), "coefficients modulo"
        (other= a whole number), "powers of roots" (power=), "term ratio" (for_letter= the letter that counts) and
        "coefficients". SymPy's names work too ("LC", "groebner", "sqf_list"). The formula itself does not change.
        """
        from ._errors import SimplydataError
        from ._formula import Formula, _show, need_sympy

        sp = need_sympy("formula.find_fact()")
        if name is None:
            raise SimplydataError('formula.find_fact() needs the name of a fact, such as '
                                  'formula.find_fact("discriminant"). Names: ' + ", ".join(f'"{n}"' for n in FACTS))
        key = _value(FACTS, FACT_SPELLINGS, name, "find_fact", "name")
        function_name, needs, gives, _ = FACTS[key]
        shown = _show(self._expr)
        values: list = []
        named: dict = {}
        if needs in ("other", "others"):
            items = (self._others(other, "find_fact", f'find_fact("{key}", other="x - 1")') if needs == "others"
                     else [self._other(other, "find_fact", f'find_fact("{key}", other="x - 1")')])
            if needs == "others":
                values = [[self._expr, *items]] if function_name == "groebner" else [self._expr, items]
            else:
                values = [self._expr, items[0]]
            also = items
        else:
            if other is not None and needs != "number":
                raise SimplydataError(f'find_fact("{key}") takes no other formula; leave out other=.')
            values, also = [self._expr], []
        if needs == "number":
            if isinstance(other, bool) or not isinstance(other, int) or other < 2:
                raise SimplydataError(f'find_fact("{key}") needs a whole number of 2 or more in other=, such as '
                                      f'find_fact("{key}", other=3).')
            values.append(sp.Integer(other))
        if needs == "power":
            if isinstance(power, bool) or not isinstance(power, int) or not 1 <= power <= MAX_ROOT_POWER:
                raise SimplydataError(f'find_fact("{key}") needs a whole power from 1 to {MAX_ROOT_POWER} in power=, '
                                      f'such as find_fact("{key}", power=2).')
            values.append(power)
        elif power is not None:
            raise SimplydataError(f'power= goes with find_fact("powers of roots"); leave it out for "{key}".')
        if key == "minimal polynomial":
            if self._expr.free_symbols:
                raise SimplydataError(f'find_fact("minimal polynomial") works on a number without letters, such as '
                                      f'sqrt(2) + sqrt(3); {shown} has letters.')
            letter = "x" if for_letter is None else for_letter
            if not isinstance(letter, str) or not letter.isidentifier():
                raise SimplydataError('for_letter= is the letter of the minimal polynomial, such as for_letter="x".')
            values.append(sp.Symbol(letter))
        elif key == "term ratio":
            values += self._letters_for("find_fact", for_letter, 'find_fact("term ratio", for_letter="k")')[:1] \
                if for_letter is not None else [self._letter("find_fact", None, 'find_fact("term ratio", '
                                                                                'for_letter="k")')]
        else:
            letters = self._letters_for("find_fact", for_letter, f'find_fact("{key}", for_letter="x")', also=also)
            if not letters:
                raise SimplydataError(f'find_fact("{key}") works on a polynomial with a letter; {shown} has none.')
            if key == "galois group":
                if len(letters) != 1:
                    raise SimplydataError('find_fact("galois group") works on a polynomial in one letter.')
                named["by_name"] = True
            elif key in ("groebner basis", "remainder by several"):
                values += letters
                named["order"] = "lex"
            elif key == "symmetric form":
                values += letters
                named["formal"] = True
            elif key == "coefficients":
                pass
            elif key not in ("viete formulas",):
                values += letters
            if key in ONE_LETTER and len(letters) > 1:
                raise SimplydataError(f'find_fact("{key}") works on a polynomial in one letter; {shown} has '
                                      f'{len(letters)} ({", ".join(str(s) for s in letters)}): say which with '
                                      f'for_letter=, such as find_fact("{key}", for_letter="x").')
        if key == "coefficients":
            letters = self._letters_for("find_fact", for_letter, 'find_fact("coefficients", for_letter="x")')
            poly = self._poly("find_fact", sp.Poly, self._expr, letters[0], what="SymPy Poly")
            found = self._poly("find_fact", sp.Poly.all_coeffs, poly, what="SymPy Poly.all_coeffs")
        else:
            found = self._poly("find_fact", getattr(sp, function_name), *values, what=f"SymPy {function_name}",
                               **named)
        how = f"SymPy {function_name}"
        with_said = f" with {', '.join(_show(o) for o in also)}" if also else (f" and {other}" if needs == "number"
                                                                               else "")
        if key == "galois group":
            group, alternating = found
            text = group.name
            print(f"The Galois group of {shown}: {text} ({group.value}; inside the alternating group: "
                  f"{'yes' if alternating else 'no'})   ({how})")
            return text
        if key == "viete formulas":
            lines = [f"{_show(left)} = {_show(right)}" for left, right in found]
            print(f"The Viete formulas of {shown} (r1, r2 ... are its roots): " + "; ".join(lines) + f"   ({how})")
            return lines
        if key == "symmetric form":
            symmetric, rest, names = found
            print(f"{shown} in the elementary symmetric polynomials "
                  + ", ".join(f"{_show(s)} = {_show(v)}" for s, v in names)
                  + f": {_show(symmetric)}, with {_show(rest)} left over   ({how})")
            return Formula(symmetric), Formula(rest)
        if key == "remainder by several":
            quotients, rest = found
            print(f"{shown} divided by {', '.join(_show(o) for o in also)}: the quotients "
                  f"{', '.join(_show(q) for q in quotients)} and the remainder {_show(rest)}   ({how})")
            return Formula(rest)
        if gives == "factors":
            number, pairs = (1, found) if function_name == "gff_list" else found  # gff_list has no number factor
            rows = [{"factor": _show(f), "times": int(k)} for f, k in pairs]
            if number != 1:
                rows.insert(0, {"factor": _show(number), "times": 1})
            written = [f"({r['factor']})" + (f"**{r['times']}" if r["times"] > 1 else "") for r in rows]
            print(f'find_fact("{key}") of {shown}: ' + " * ".join(written) + f"   ({how})")
            from ._formula import _result_rows

            return _result_rows(rows, False)
        if key == "without number factor":
            number, found = found
            print(f"{shown} is {_show(number)} times {_show(found)}   ({how})")
            return Formula(found)
        if gives in ("formulas", "numbers or formulas") or key == "groebner basis":
            items = list(found.exprs) if key == "groebner basis" else list(found)
            print(f'find_fact("{key}") of {shown}{with_said}: {", ".join(_show(i) for i in items)}   ({how})')
            return [_back(sp, i) for i in items]
        print(f'find_fact("{key}") of {shown}{with_said}: {_show(found)}   ({how})')
        return _back(sp, found) if gives in ("number", "number or formula") else Formula(found)


# ------------------------------------------------------------------------------------------------ small helpers
def _exact(sp, value):
    from ._formula import exact_number

    return exact_number(sp, value)


def _whole_or_minus_infinity(value):
    """A degree: a whole number, or minus infinity for 0 (SymPy -oo)."""
    import sympy as sp

    return -math.inf if value == -sp.oo else int(value)


def _back(sp, value):
    """A SymPy answer as simplydata gives it back: a number (float, or complex) when it has no letters, else a
    formula (as find_limit_as does)."""
    from ._formula import Formula, decimal_of, float_of

    if getattr(value, "free_symbols", None):
        return Formula(value)
    if value.is_real:
        return float_of(value)
    found = complex(decimal_of(value))
    return found.real if found.imag == 0 else found


def _empty_roots(fast, kind: str):
    """The table of no roots, with the columns of the kind of roots asked for."""
    import pandas as pd

    from .table import table

    columns = {"exact": ["root", "root exactly", "times"], "decimals": ["root", "root as text"],
               "intervals": ["from", "to", "from exactly", "to exactly", "times"]}[kind]
    return table(pd.DataFrame(columns=columns), fast=fast)
