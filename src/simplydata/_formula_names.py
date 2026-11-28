"""More SymPy names inside the text of sdata.formula (families for 100 %, batches 22-23, plan section 2.10, approved by
Manish 2026-11-28).

sdata.formula("Max(x, 0) + fibonacci(n)") reads SymPy's own functions by their SymPy names: the other trigonometric
and hyperbolic functions (cot, sec, csc and their inverses), parts of numbers (floor, ceiling, frac, sign, re, im,
arg, Max, Min, Mod), counting functions (factorial, fibonacci, bell, catalan, harmonic, partition, totient ...),
more special functions (trigamma, lerchphi, hankel1, mathieuc, appellf1, hyper, meijerg, Ynm ...), steps and deltas
(DiracDelta, KroneckerDelta, LeviCivita, SingularityFunction), Piecewise, and SymPy's constants Catalan, EulerGamma,
GoldenRatio and TribonacciConstant.

Each name is SymPy's function itself, so every exact word of a formula (slopes, areas, limits, series, simpler)
knows it. These names are for sdata.formula only: the formulas of a table (add_column, fit_formula) and the
decimal words (find_where_smallest, solve) work with NumPy and SciPy, where most of them have no function. Without
brackets a name stays a letter (re, ln, sec and bell are letters in "re + ln"), as gamma and beta are.

The counting functions are worked out exactly by SymPy, so the number inside them may be at most 1000, as for gamma
(factorial(1000) has 2568 digits): factorial(5000) is refused while the text is read. Every formula with one of
these names is worked out by SymPy under simplydata's one time limit (_time_limit.py), never while the text is read.

Piecewise takes pairs (value, condition) with one comparison each, (0, True) for "otherwise":
Piecewise((x, x > 0), (0, True)). hyper takes two lists in brackets and a value, hyper((1, 2), (3,), x); meijerg
takes SymPy's lists of lists, meijerg(((1,), ()), ((), (0,)), x).

The names SymPy calls by the same name as a scipy.special or NumPy function (besseli, erfinv, LambertW, Si,
legendre ...) are those of the maths family (_maths_functions.py, plan section 2.3); they are not repeated here.

An exact answer can still be very big or slow within that limit (bell(1000) has about 1,900 digits); every such step
stops at the time limit. Every name is tested against SymPy directly (tests/test_formula_algebra.py).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from ._time_limit import one_deadline

TRIG = "other angle and hyperbolic functions"
PARTS = "parts of numbers"
COUNTING = "counting functions (worked out exactly; the number inside at most 1000)"
SPECIAL = "more special functions"
STEPS = "steps, deltas and pieces"
GROUP_ORDER = (TRIG, PARTS, COUNTING, SPECIAL, STEPS)


@dataclass(frozen=True)
class FormulaName:
    """One SymPy name of formula text.

    name:    how it is written in formula text (SymPy's name)
    sympy:   the SymPy function it is (sympy.<sympy>)
    fewest, most: how many values it takes
    about:   one line on what it is
    group:   where sdata.help lists it
    sample:  the values of the example (and of its test against SymPy), as formula text
    capped:  the numbers inside may be at most 1000 (SymPy works the answer out exactly)
    """

    name: str
    sympy: str
    fewest: int
    most: int
    about: str
    group: str
    sample: str
    capped: bool = False


def _n(name, fewest, most, about, group, sample, sympy=None, capped=False) -> FormulaName:
    return FormulaName(name, sympy or name, fewest, most, about, group, sample, capped)


NAMES = (
    # ------------------------------------------------------------------------- other angle and hyperbolic functions
    _n("cot", 1, 1, "cotangent, 1/tan(x)", TRIG, "pi/4"),
    _n("sec", 1, 1, "secant, 1/cos(x)", TRIG, "pi/3"),
    _n("csc", 1, 1, "cosecant, 1/sin(x)", TRIG, "pi/6"),
    _n("acot", 1, 1, "inverse cotangent", TRIG, "1"),
    _n("asec", 1, 1, "inverse secant", TRIG, "2"),
    _n("acsc", 1, 1, "inverse cosecant", TRIG, "2"),
    _n("coth", 1, 1, "hyperbolic cotangent", TRIG, "1"),
    _n("sech", 1, 1, "hyperbolic secant", TRIG, "0"),
    _n("csch", 1, 1, "hyperbolic cosecant", TRIG, "1"),
    _n("acoth", 1, 1, "inverse hyperbolic cotangent", TRIG, "2"),
    _n("asech", 1, 1, "inverse hyperbolic secant", TRIG, "1"),
    _n("acsch", 1, 1, "inverse hyperbolic cosecant", TRIG, "1"),
    # ------------------------------------------------------------------------- parts of numbers
    _n("floor", 1, 1, "rounded down to a whole number", PARTS, "7/2"),
    _n("ceiling", 1, 1, "rounded up to a whole number", PARTS, "7/2"),
    _n("ceil", 1, 1, "rounded up to a whole number (the same as ceiling)", PARTS, "7/2", sympy="ceiling"),
    _n("frac", 1, 1, "the part after the point, x - floor(x)", PARTS, "7/2"),
    _n("sign", 1, 1, "-1 below 0, 0 at 0, 1 above 0", PARTS, "-3"),
    _n("Max", 1, 50, "the biggest of the values", PARTS, "2, 7, 3"),
    _n("Min", 1, 50, "the smallest of the values", PARTS, "2, 7, 3"),
    _n("re", 1, 1, "the real part of a complex number", PARTS, "3 + sqrt(-16)"),
    _n("im", 1, 1, "the imaginary part of a complex number", PARTS, "3 + sqrt(-16)"),
    _n("arg", 1, 1, "the angle of a complex number (radians)", PARTS, "1 + sqrt(-1)"),
    _n("conjugate", 1, 1, "the complex conjugate (the sign of the imaginary part turned)", PARTS, "3 + sqrt(-16)"),
    _n("Mod", 2, 2, "the remainder of x divided by y, with the sign of y", PARTS, "17, 5"),
    _n("Rem", 2, 2, "the remainder of x divided by y, with the sign of x", PARTS, "-17, 5"),
    _n("ln", 1, 1, "the natural log (the same as log)", PARTS, "exp(2)"),
    # ------------------------------------------------------------------------- counting functions
    _n("factorial", 1, 1, "n! = 1*2*...*n", COUNTING, "10", capped=True),
    _n("ff", 2, 2, "falling factorial x(x-1)...(x-k+1)", COUNTING, "10, 3", capped=True),
    _n("FallingFactorial", 2, 2, "falling factorial (the same as ff)", COUNTING, "10, 3", capped=True),
    _n("rf", 2, 2, "rising factorial x(x+1)...(x+k-1)", COUNTING, "10, 3", capped=True),
    _n("fibonacci", 1, 2, "the nth Fibonacci number (1, 1, 2, 3, 5 ...), or polynomial", COUNTING, "30",
       capped=True),
    _n("lucas", 1, 1, "the nth Lucas number (2, 1, 3, 4, 7 ...)", COUNTING, "20", capped=True),
    _n("tribonacci", 1, 2, "the nth tribonacci number (0, 1, 1, 2, 4, 7 ...)", COUNTING, "20", capped=True),
    _n("bell", 1, 3, "the nth Bell number: the ways to split n things into groups", COUNTING, "10", capped=True),
    _n("catalan", 1, 1, "the nth Catalan number (1, 1, 2, 5, 14 ...)", COUNTING, "10", capped=True),
    _n("genocchi", 1, 2, "the nth Genocchi number", COUNTING, "10", capped=True),
    _n("andre", 1, 1, "the nth Andre (up-down) number", COUNTING, "10", capped=True),
    _n("harmonic", 1, 2, "the nth harmonic number 1 + 1/2 + ... + 1/n", COUNTING, "10", capped=True),
    _n("partition", 1, 1, "the number of ways to write n as a sum of whole numbers", COUNTING, "50", capped=True),
    _n("motzkin", 1, 1, "the nth Motzkin number", COUNTING, "10", capped=True),
    _n("subfactorial", 1, 1, "the ways to reorder n things with none in its place (derangements)", COUNTING, "10",
       capped=True),
    _n("primepi", 1, 1, "how many prime numbers are at most n", COUNTING, "100", capped=True),
    _n("totient", 1, 1, "Euler's totient: the whole numbers up to n with no factor in common with n", COUNTING,
       "36", capped=True),
    _n("reduced_totient", 1, 1, "Carmichael's reduced totient", COUNTING, "36", capped=True),
    _n("divisor_sigma", 1, 2, "the sum of the divisors of n (to the power k)", COUNTING, "12", capped=True),
    _n("primenu", 1, 1, "how many different prime factors n has", COUNTING, "360", capped=True),
    _n("primeomega", 1, 1, "how many prime factors n has, counted with repeats", COUNTING, "360", capped=True),
    _n("mobius", 1, 1, "the Moebius function: 0, 1 or -1", COUNTING, "30", capped=True),
    _n("jacobi_symbol", 2, 2, "the Jacobi symbol (m / n)", COUNTING, "2, 15", capped=True),
    _n("kronecker_symbol", 2, 2, "the Kronecker symbol (a / n)", COUNTING, "2, 15", capped=True),
    _n("legendre_symbol", 2, 2, "the Legendre symbol (a / p), p a prime", COUNTING, "2, 7", capped=True),
    _n("stieltjes", 1, 2, "the nth Stieltjes constant", COUNTING, "1", capped=True),
    _n("multigamma", 2, 2, "the multivariate gamma function of x in p dimensions", COUNTING, "3, 2", capped=True),
    _n("chebyshevt_root", 2, 2, "the kth root (from 0) of the Chebyshev polynomial T_n", COUNTING, "3, 0",
       capped=True),
    _n("chebyshevu_root", 2, 2, "the kth root (from 0) of the Chebyshev polynomial U_n", COUNTING, "3, 0",
       capped=True),
    # ------------------------------------------------------------------------- more special functions
    _n("trigamma", 1, 1, "the trigamma function, the slope of digamma", SPECIAL, "1"),
    _n("dirichlet_eta", 1, 2, "the Dirichlet eta function", SPECIAL, "2"),
    _n("riemann_xi", 1, 1, "the Riemann xi function", SPECIAL, "2"),
    _n("lerchphi", 3, 3, "the Lerch transcendent Phi(z, s, a)", SPECIAL, "1/2, 2, 1"),
    _n("li", 1, 1, "the logarithmic integral", SPECIAL, "2"),
    _n("Li", 1, 1, "the offset logarithmic integral li(x) - li(2)", SPECIAL, "2"),
    _n("betainc_regularized", 4, 4, "the regularized incomplete beta function I(a, b; x1, x2)", SPECIAL,
       "1, 2, 0, 1/2"),
    _n("elliptic_pi", 2, 3, "the elliptic integral of the third kind", SPECIAL, "1/2, 1/3"),
    _n("erf2", 2, 2, "the two-value error function erf(y) - erf(x)", SPECIAL, "0, 1"),
    _n("erf2inv", 2, 2, "the inverse of erf2", SPECIAL, "0, 1/2"),
    _n("hankel1", 2, 2, "the Hankel function of the first kind H1(nu, z)", SPECIAL, "1, 2"),
    _n("hankel2", 2, 2, "the Hankel function of the second kind H2(nu, z)", SPECIAL, "1, 2"),
    _n("hn1", 2, 2, "the spherical Hankel function of the first kind", SPECIAL, "1, 2"),
    _n("hn2", 2, 2, "the spherical Hankel function of the second kind", SPECIAL, "1, 2"),
    _n("marcumq", 3, 3, "the Marcum Q-function Q(m, a, b)", SPECIAL, "1, 1, 2"),
    _n("mathieuc", 3, 3, "the Mathieu cosine function C(a, q, z)", SPECIAL, "1, 0, x"),
    _n("mathieucprime", 3, 3, "the slope of the Mathieu cosine function", SPECIAL, "1, 0, x"),
    _n("mathieus", 3, 3, "the Mathieu sine function S(a, q, z)", SPECIAL, "1, 0, x"),
    _n("mathieusprime", 3, 3, "the slope of the Mathieu sine function", SPECIAL, "1, 0, x"),
    _n("appellf1", 6, 6, "the Appell hypergeometric function F1(a, b1, b2, c, x, y)", SPECIAL,
       "1, 1, 1, 2, x, y"),
    _n("hyper", 3, 3, "the generalized hypergeometric function pFq((a ...), (b ...), z)", SPECIAL,
       "(1, 1), (2,), x"),
    _n("meijerg", 3, 5, "the Meijer G-function", SPECIAL, "((1,), ()), ((), (0,)), x"),
    _n("Ynm", 4, 4, "the spherical harmonic Y(n, m, theta, phi)", SPECIAL, "1, 0, theta, phi"),
    _n("Ynm_c", 4, 4, "the complex conjugate of the spherical harmonic Ynm", SPECIAL, "1, 0, theta, phi"),
    _n("Znm", 4, 4, "the real spherical harmonic Z(n, m, theta, phi)", SPECIAL, "1, 0, theta, phi"),
    # ------------------------------------------------------------------------- steps, deltas and pieces
    _n("DiracDelta", 1, 2, "the Dirac delta (an area of 1 at 0); a second value takes its slope", STEPS, "x"),
    _n("KroneckerDelta", 2, 3, "1 when the two values are the same, else 0", STEPS, "3, 3"),
    _n("LeviCivita", 2, 10, "the Levi-Civita symbol: 1, -1 or 0 by the order of the values", STEPS, "1, 2, 3"),
    _n("Eijk", 2, 10, "the Levi-Civita symbol (the same as LeviCivita)", STEPS, "2, 1, 3"),
    _n("SingularityFunction", 3, 3, "the singularity function <x - a>^n of beam formulas", STEPS, "x, 2, 1"),
    _n("Piecewise", 1, 20, "a formula in pieces: (value, condition) pairs, (value, True) for otherwise", STEPS,
       "(x, x > 0), (0, True)"),
)
BY_NAME = {entry.name: entry for entry in NAMES}
# names whose values may be lists in brackets (hyper, meijerg) or (value, condition) pairs (Piecewise)
LIST_FUNCTIONS = ("hyper", "meijerg", "Piecewise")
CAPPED = tuple(entry.name for entry in NAMES if entry.capped)
NO_EVALUATE = ("betainc_regularized",)  # SymPy's own class takes no evaluate= (and works nothing out when made)
# SymPy's constants, by their SymPy names (pi is already one): Catalan's constant, the Euler-Mascheroni constant,
# the golden ratio and the tribonacci constant
CONSTANTS = ("Catalan", "EulerGamma", "GoldenRatio", "TribonacciConstant")
CONSTANTS_ABOUT = {"Catalan": "Catalan's constant 0.9159...", "EulerGamma": "the Euler-Mascheroni constant 0.5772...",
                   "GoldenRatio": "the golden ratio (1 + sqrt(5))/2", "TribonacciConstant": "the tribonacci constant "
                   "1.8393..."}
COMPARISONS = {ast.Lt: "<", ast.Gt: ">", ast.LtE: "<=", ast.GtE: ">="}


def sizes() -> dict:
    """name -> (fewest, most values), for the formula reader's FUNCTIONS."""
    return {entry.name: (entry.fewest, entry.most) for entry in NAMES}


def sympy_functions(evaluate: bool) -> dict:
    """name -> the SymPy function (evaluate=False: it keeps its values unevaluated, so SymPy doit works them out
    under the time limit)."""
    import sympy as sp

    def made(entry):
        function = getattr(sp, entry.sympy)
        if entry.name == "Ynm_c":  # SymPy's Ynm_c is conjugate(Ynm(...)), written out so it can stay unevaluated
            return lambda *values, **_: sp.conjugate(sp.Ynm(*values, evaluate=evaluate), evaluate=evaluate)
        if entry.name == "Eijk":  # SymPy's Eijk is LeviCivita
            return lambda *values, **_: sp.LeviCivita(*values, evaluate=evaluate)
        if evaluate or entry.name in NO_EVALUATE:  # SymPy leaves these unevaluated by themselves
            return function
        return lambda *values, **_: function(*values, evaluate=False)

    return {entry.name: made(entry) for entry in NAMES}


def sympy_classes() -> tuple:
    """The SymPy functions of this table: a formula with any of them is worked out under the time limit."""
    import sympy as sp

    return tuple({getattr(sp, entry.sympy) for entry in NAMES if entry.name not in ("Ynm_c", "Eijk", "ln")})


# names that SymPy lambdify gives to NumPy and SciPy with the same values SymPy gives; a formula with any other name
# of this table is worked out value by value by SymPy (factorial is SciPy's 0 below 0 but SymPy's gamma(x + 1), and
# NumPy has no totient or fibonacci)
LAMBDIFY_SAFE = ("cot", "sec", "csc", "acot", "asec", "acsc", "coth", "sech", "csch", "acoth", "asech", "acsch",
                 "floor", "ceiling", "ceil", "sign", "Max", "Min", "re", "im", "arg", "conjugate", "Mod", "ln",
                 "hankel1", "hankel2", "trigamma")


def by_value_classes() -> tuple:
    """The SymPy functions find_value_at works out value by value for many values (not LAMBDIFY_SAFE)."""
    import sympy as sp

    return tuple({getattr(sp, entry.sympy) for entry in NAMES if entry.name not in LAMBDIFY_SAFE + ("Ynm_c", "Eijk")})


def capped_classes() -> tuple:
    """The SymPy functions whose numbers may be at most 1000 (the counting functions)."""
    import sympy as sp

    return tuple({getattr(sp, entry.sympy) for entry in NAMES if entry.capped})


def constants() -> dict:
    """SymPy's constants by name."""
    import sympy as sp

    return {name: getattr(sp, name) for name in CONSTANTS}


def relations() -> dict:
    """The comparisons SymPy's reader writes for the conditions of Piecewise (x > 0 is Gt(x, 0) when it reads the
    text unevaluated)."""
    import sympy as sp

    return {"Lt": sp.Lt, "Gt": sp.Gt, "Le": sp.Le, "Ge": sp.Ge}


def check_list_call(node, name: str, text: str, check, error) -> None:
    """Check the values of hyper, meijerg and Piecewise (ast, never run): lists in brackets of formula pieces, and
    for Piecewise (value, condition) pairs whose condition is one comparison (x > 0) or True. check(piece) checks a
    formula piece; error(problem) is the formula reader's error."""
    def piece_or_list(value, depth):
        if isinstance(value, ast.Tuple):
            if depth == 0:
                raise error(f'"{ast.get_source_segment(text, value)}": {name}() takes lists in brackets only this '
                            "deep.")
            for part in value.elts:
                piece_or_list(part, depth - 1)
        else:
            check(value)

    if name == "Piecewise":
        for pair in node.args:
            if not (isinstance(pair, ast.Tuple) and len(pair.elts) == 2):
                raise error(f'"{ast.get_source_segment(text, pair)}": Piecewise() takes (value, condition) pairs, '
                            "such as Piecewise((x, x > 0), (0, True)).")
            value, condition = pair.elts
            check(value)
            if isinstance(condition, ast.Constant) and condition.value is True:
                continue
            if not (isinstance(condition, ast.Compare) and len(condition.ops) == 1
                    and type(condition.ops[0]) in COMPARISONS):
                raise error(f'"{ast.get_source_segment(text, condition)}": a condition of Piecewise() is one '
                            "comparison with <, >, <= or >= (such as x > 0), or True for otherwise.")
            check(condition.left)
            check(condition.comparators[0])
        return
    depth = 1 if name == "hyper" else 2
    for value in node.args:
        piece_or_list(value, depth)


def pointer_groups() -> list:
    """The help pointers of SymPy's names in formula text: [(how the simplydata word is written, the names)]."""
    out = []
    for entry in NAMES:
        if entry.name == "ceil":  # a spelling of ceiling, not a SymPy name
            continue
        out.append((f'sdata.formula("{entry.name}({entry.sample})"): SymPy\'s {entry.name} inside formula text '
                    f"({entry.about})", entry.name))
    for name in CONSTANTS:
        out.append((f'sdata.formula("{name}"): SymPy\'s constant {name} inside formula text '
                    f"({CONSTANTS_ABOUT[name]})", name))
    return out


# SymPy functions that NumPy and SciPy cannot work out (lambdify writes their name, which NumPy does not know):
# find_value_at works them out value by value with SymPy evalf instead, each under the time limit
NO_VALUE = (TypeError, ValueError, KeyError, ZeroDivisionError, ArithmeticError)  # SymPy's ways of saying "no value"
MAX_BY_VALUE = 10_000  # values worked out one at a time at most
# SymPy functions that SymPy's evalf leaves as they are (no decimal): said plainly instead of an empty answer
NO_DECIMAL = ("mathieuc", "mathieus", "mathieucprime", "mathieusprime", "marcumq", "stieltjes")


@one_deadline
def value_by_value(expr, symbols: list, arrays: list):
    """The values of expr at each combination of the arrays (broadcast), each from SymPy evalf with subs, all under
    one time limit: complex numbers, NaN where SymPy gives no number (a pole). A whole number goes in as a whole
    number (totient(36.0) has no value, totient(36) has). A function SymPy has no decimal for is said plainly."""
    import numpy as np
    import sympy as sp

    from ._errors import SimplydataError
    from ._formula import _guarded, _show

    columns = np.broadcast_arrays(*[np.asarray(a, dtype=float) for a in arrays])
    shape = columns[0].shape
    if columns[0].size > MAX_BY_VALUE:
        raise SimplydataError(f"This formula has a SymPy function that NumPy and SciPy do not have, so each value is "
                              f"worked out by SymPy on its own; give at most {MAX_BY_VALUE:,} values.")
    out = np.empty(shape, dtype=complex)
    for at in np.ndindex(shape):
        swaps = {s: c[at] for s, c in zip(symbols, columns)}
        if any(np.isnan(v) for v in swaps.values()):
            out[at] = np.nan
            continue
        put = {s: sp.Integer(int(v)) if float(v).is_integer() else float(v) for s, v in swaps.items()}
        try:
            found = _guarded(expr.evalf, 15, subs=put, what="SymPy evalf")
        except NO_VALUE:  # a pole (zeta(1)): no number there
            out[at] = np.nan
            continue
        left = [f for f in found.atoms(sp.Function) if type(f).__name__ in NO_DECIMAL] if not found.is_Number else []
        if left:
            raise SimplydataError(f"SymPy has no decimal for {_show(left[0])} (at "
                                  + ", ".join(f"{k} = {v}" for k, v in put.items()) + "), so these values cannot be "
                                  "worked out. Try other values, or one value at a time.")
        try:
            out[at] = complex(found)
        except (TypeError, ValueError):  # zoo or nan: no number there
            out[at] = np.nan
    return out


def check_values(node, text: str, error) -> None:
    """The values of a counting function, checked by SymPy as it makes it (under the time limit): motzkin(n) and
    chebyshevt_root(n, 0) take whole numbers only, legendre_symbol(2, 9) needs a prime. error(problem) is the formula
    reader's error."""
    from ._formula import _guarded

    name = type(node).__name__
    try:
        _guarded(type(node), *node.args, what="SymPy " + name)
    except (ValueError, TypeError, NotImplementedError, AttributeError) as problem:
        if node.free_symbols:
            raise error(f'"{text}": the SymPy function {name}() takes whole numbers here, not letters '
                        f"({problem}). Put a number in its place.") from None
        raise error(f'"{text}": SymPy has no value of {name}() for these numbers ({problem}).') from None
