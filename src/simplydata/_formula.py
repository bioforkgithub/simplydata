"""Exact maths with SymPy: sdata.formula("(x + 2)**2 - 4") and its words, solve(exactly=True) and show_as_fraction.

SymPy is the optional extra simplydata[exact] (pip install "simplydata[exact]"); without it these words stop with a
plain sentence that says how to install it. Every answer comes from SymPy:

* the formula text is checked with Python's ast first (numbers, letters, + - * / ** ^, brackets and the functions of
  fit_formula only; never run), then read by SymPy's parse_expr with every letter given as a SymPy Symbol, so that
  letters such as E, I, N, S or beta stay letters and never become SymPy's own constants or functions. SymPy reads
  it unevaluated first (parse_expr(evaluate=False)): the numbers inside gamma, lgamma, digamma, beta and besselJ and
  the numbers of powers are worked out under the time limit and checked for size, and a formula with any of them is
  then worked out (SymPy doit) under the time limit too, never while the text is read;
* make_simpler: simplify; turn_into_sum: expand; turn_into_product: factor;
* find_slope_formula: diff; find_area_formula: integrate; find_value_at: subs + evalf (one value) or lambdify with
  NumPy and SciPy (many values); put_in: subs; show_as_latex: latex; find_limit_as: limit; find_taylor_series:
  series; solve(exactly=True): solve; nums.show_as_fraction: nsimplify(rational=True).
* numbers phase, batch 4 (approved by Manish 2026-11-26): find_slope_formula(how_many_times=) and mixed slopes: diff;
  find_limit_as(from_side=): limit(dir="+" or "-"); show_as_decimal: N; group_by_powers_of: expand then collect;
  turn_into_partial_fractions: apart; letters_are=: Symbols with SymPy's assumptions (positive, integer ...);
  solve(for_letter=, exactly=True): solve for some letters; rules (<, >, <=, >=) with exactly=True: solveset over
  the real numbers (reduce_inequalities for several); a formula object in solve means formula = 0; as_sympy: the
  SymPy expression itself. The heavy SymPy calls run under one time limit (_time_limit.py).

Own code is glue only: checking the text, naming the letters, and writing SymPy's answer back as formula text that
the other simplydata words read (abs, lgamma, besselJ(x, nu) and sinc as fit_formula writes them).
"""

from __future__ import annotations

import ast
import math

import numpy as np

from ._errors import MissingWordError, SimplydataError, choice_error, friendly, suggest
from ._time_limit import EXACTLY_HINT, FORMULA_HINT, one_deadline

INSTALL_EXACT = 'pip install "simplydata[exact]"   (or: conda install -c conda-forge sympy)'
FORMULA_EXAMPLE = 'f = sdata.formula("(x + 2)**2 - 4")'

# the functions a formula may use: name -> (fewest, most arguments); the same as fit_formula's
FUNCTIONS = {"exp": (1, 1), "log": (1, 2), "sqrt": (1, 1), "abs": (1, 1), "sin": (1, 1), "cos": (1, 1),
             "tan": (1, 1), "arcsin": (1, 1), "arccos": (1, 1), "arctan": (1, 1), "arctan2": (2, 2), "erf": (1, 1),
             "erfc": (1, 1), "gamma": (1, 1), "lgamma": (1, 1), "digamma": (1, 1), "beta": (2, 2),
             "besselJ": (2, 2), "sinc": (1, 1)}
SPELLINGS = {"atan": "arctan", "asin": "arcsin", "acos": "arccos", "atan2": "arctan2"}
FREE_NAMES = ("gamma", "beta")  # without brackets they are letters, as in fit_formula
INFINITY = ("infinity", "inf", "oo", "+infinity")
MINUS_INFINITY = ("-infinity", "-inf", "-oo", "minus infinity")

# Words of a formula (sdata.help, the dictionary and the tests read this)
WORDS = ("make_simpler", "turn_into_sum", "turn_into_product", "find_slope_formula", "find_area_formula",
         "find_value_at", "put_in", "show_as_latex", "find_limit_as", "find_taylor_series", "undo",
         # numbers phase, batch 4 (approved by Manish 2026-11-26)
         "show_as_decimal", "group_by_powers_of", "turn_into_partial_fractions", "as_sympy")
# names from SymPy, MATLAB and R -> the formula word (they never run)
HINTS = {"simplify": "make_simpler()", "expand": "turn_into_sum() (multiplied out)",
         "factor": "turn_into_product()", "factorise": "turn_into_product()", "factorize": "turn_into_product()",
         "diff": 'find_slope_formula(for_letter="x")', "derivative": "find_slope_formula()",
         "Derivative": "find_slope_formula()", "deriv": "find_slope_formula()", "D": "find_slope_formula()",
         "integrate": "find_area_formula() (sdata.find_area_under for a number)",
         "Integral": "find_area_formula()", "int": "find_area_formula()",
         "subs": 'put_in(x="y + 1") (find_value_at(x=2) for a number)', "substitute": 'put_in(x="y + 1")',
         "evalf": "find_value_at(x=2) for a number, or show_as_decimal(digits=50) for many digits",
         "N": "find_value_at(x=2) for a number, or show_as_decimal(digits=50) for many digits", "lambdify": "find_value_at(x=numbers)",
         "matlabFunction": "find_value_at(x=numbers)", "latex": "show_as_latex()",
         "limit": 'find_limit_as("x", goes_to=0)', "series": "find_taylor_series(around=0, up_to_power=4)",
         "taylor": "find_taylor_series(around=0, up_to_power=4)",
         # numbers phase, batch 4
         "apart": "turn_into_partial_fractions()", "partial_fractions": "turn_into_partial_fractions()",
         "collect": 'group_by_powers_of("x")', "coeff": 'group_by_powers_of("x")',
         "vpa": "show_as_decimal(digits=50)",
         "digits": "show_as_decimal(digits=50)", "refine": 'sdata.formula("...", letters_are={"x": "positive"})',
         "assumptions": 'sdata.formula("...", letters_are={"x": "positive"})',
         "expr": "as_sympy() (the SymPy expression)", "sympy": "as_sympy() (the SymPy expression)",
         "to_sympy": "as_sympy() (the SymPy expression)",
         "summation": 'sdata.find_sum_of_series("1/k**2", between=[1, "infinity"])',
         "Sum": 'sdata.find_sum_of_series("1/k**2", between=[1, "infinity"])',
         "pretty": "show_as_latex() (in Jupyter a formula is shown typeset by itself)",
         "pprint": "show_as_latex() (in Jupyter a formula is shown typeset by itself)"}

# letters_are= (batch 4): what a letter is -> SymPy's assumptions on its Symbol
LETTER_KINDS = {"positive": {"positive": True}, "zero or more": {"nonnegative": True},
                "negative": {"negative": True}, "real": {"real": True}, "whole number": {"integer": True},
                "positive whole number": {"integer": True, "positive": True}}
LETTER_KIND_SPELLINGS = {"above zero": "positive", "above 0": "positive", "nonnegative": "zero or more",
                         "non-negative": "zero or more", "zero or above": "zero or more", "0 or more": "zero or more",
                         "below zero": "negative", "below 0": "negative", "integer": "whole number",
                         "whole": "whole number", "positive integer": "positive whole number",
                         "natural number": "positive whole number", "real number": "real"}
FROM_SIDES = {"both": "+-", "above": "+", "below": "-"}
FROM_SIDE_SPELLINGS = {"right": "above", "+": "above", "from above": "above", "from the right": "above",
                       "left": "below", "-": "below", "from below": "below", "from the left": "below",
                       "two-sided": "both", "+-": "both", "both sides": "both"}
MAX_SLOPE_TIMES = 20  # how_many_times= (a slope of a big product grows quickly)
MAX_DECIMAL_DIGITS = 10_000  # show_as_decimal(digits=)
MAX_LETTER_POWER = 100  # a sum with letters raised to a higher whole power is not multiplied out


def need_sympy(what: str):
    """The sympy module, or a plain error that says how to install it."""
    try:
        import sympy
    except ImportError:
        raise SimplydataError(f"{what} needs SymPy, an optional extra for exact maths.\n"
                              f"Install it with:  {INSTALL_EXACT}") from None
    return sympy


# ---------------------------------------------------------------- reading the text
def _formula_error(problem: str) -> SimplydataError:
    return SimplydataError(
        f"{problem}\nA formula uses numbers, letters (x, y, rate), + - * / and ** (or ^) for a power, brackets, pi, "
        "and the functions exp log sqrt abs sin cos tan arcsin arccos arctan arctan2 erf erfc gamma lgamma digamma "
        f"beta besselJ sinc.\nFor example:  {FORMULA_EXAMPLE}")


MAX_DIGITS = 1000  # a whole number made by powers of numbers may have at most this many digits
# gamma(10**7) is a whole number of 65 million digits and digamma(10**6) a fraction of millions: SymPy works them
# out exactly while it reads the text. A number inside these functions may be at most this big (gamma(1000) has
# 2565 digits).
MAX_SPECIAL_ARGUMENT = 1000
SPECIAL_FUNCTIONS = ("gamma", "lgamma", "digamma", "beta", "besselJ")
# names SymPy's reader writes into the text it runs (Integer(2), Symbol('x'), and Add, Mul and Pow when it reads
# unevaluated): never letters of a formula
RESERVED = ("Integer", "Float", "Rational", "Symbol", "Function", "Lambda", "Add", "Mul", "Pow")


def _constant(node):
    """The size of a piece made only of numbers (float, never exact; inf when too big), or None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        try:
            return float(node.value)
        except OverflowError:  # a whole number typed with more than 308 digits
            return math.inf if node.value > 0 else -math.inf
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        inner = _constant(node.operand)
        return None if inner is None else (-inner if isinstance(node.op, ast.USub) else inner)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
                                                            ast.BitXor)):
        a, b = _constant(node.left), _constant(node.right)
        if a is None or b is None:
            return None
        try:
            if isinstance(node.op, ast.Add):
                return a + b
            if isinstance(node.op, ast.Sub):
                return a - b
            if isinstance(node.op, ast.Mult):
                return a * b
            if isinstance(node.op, ast.Div):
                return a / b if b else math.inf
            return math.pow(abs(a), b) if a else 0.0
        except OverflowError:
            return math.inf
    return None


def _check_power(node, text: str):
    """Refuse a power of numbers too big to write down (9**9**9 has 369 million digits; SymPy would try)."""
    base, power = _constant(node.left), _constant(node.right)
    if base is None or power is None or abs(base) <= 1:
        return
    digits = power * math.log10(abs(base)) if math.isfinite(power) else math.inf
    if digits > MAX_DIGITS:
        raise _formula_error(f'"{ast.get_source_segment(text, node) or text}" is a number with more than '
                             f"{MAX_DIGITS} digits, too big to work with exactly. Use smaller numbers, or a letter "
                             "for it.")


def _check_node(node, text: str, letters: list, functions: set):
    """Check one piece of the formula (ast, never run); note the letters and functions it uses."""
    if isinstance(node, ast.Expression):
        return _check_node(node.body, text, letters, functions)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise _formula_error(f"{node.value!r} is not allowed in a formula: only numbers and letters are.")
        return
    if isinstance(node, ast.Name):
        name = node.id
        if name.startswith("_"):
            raise _formula_error(f'"{name}" cannot be a letter in a formula (it starts with _).')
        if (name in FUNCTIONS or name in SPELLINGS) and name not in FREE_NAMES:
            raise _formula_error(f"{name} needs brackets after it, for example {name}(x).")
        if name in RESERVED:
            raise _formula_error(f'"{name}" cannot be a letter in a formula: SymPy uses that name itself. Use '
                                 f'another name, such as "{name.lower()}_value".')
        if name != "pi" and name not in letters:
            letters.append(name)
        return
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        return _check_node(node.operand, text, letters, functions)
    if isinstance(node, ast.BinOp):
        if not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.BitXor)):
            raise _formula_error(f'The sign in "{ast.get_source_segment(text, node)}" is not allowed in a formula.')
        _check_node(node.left, text, letters, functions)
        _check_node(node.right, text, letters, functions)
        if isinstance(node.op, (ast.Pow, ast.BitXor)):
            _check_power(node, text)
        return
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise _formula_error(f'"{ast.get_source_segment(text, node)}" is not allowed in a formula.')
        name = SPELLINGS.get(node.func.id, node.func.id)
        if name not in FUNCTIONS:
            close = suggest(name, list(FUNCTIONS), n=1)
            hint = f" Did you mean {close[0]}()?" if close else ""
            raise _formula_error(f"{node.func.id}() is not a function a formula knows.{hint}")
        if node.keywords:
            raise _formula_error(f"{node.func.id}() takes its values without names, for example {name}(x).")
        fewest, most = FUNCTIONS[name]
        if not fewest <= len(node.args) <= most:
            wanted = str(fewest) if fewest == most else f"{fewest} or {most}"
            raise _formula_error(f"{node.func.id}() takes {wanted} value{'s' if most > 1 else ''}, "
                                 f"not {len(node.args)}.")
        functions.add(node.func.id)
        for arg in node.args:
            _check_node(arg, text, letters, functions)
        if name in SPECIAL_FUNCTIONS:
            for arg in node.args:
                size = _constant(arg)
                if size is not None and not abs(size) <= MAX_SPECIAL_ARGUMENT:
                    raise _formula_error(f'"{ast.get_source_segment(text, node)}": {name}() of a number bigger than '
                                         f"{MAX_SPECIAL_ARGUMENT} is too big to work out exactly. Use a smaller "
                                         "number, or a letter for it and find_value_at() for a decimal.")
        return
    if isinstance(node, ast.Attribute):
        raise _formula_error(f'"{ast.get_source_segment(text, node)}" is not allowed: a formula cannot use a dot '
                             "after a name.")
    raise _formula_error(f'"{ast.get_source_segment(text, node) or text}" is not allowed in a formula.')


def _sympy_functions(sp) -> dict:
    """The formula functions as SymPy functions (argument order and NumPy's sinc as fit_formula reads them)."""
    return {"exp": sp.exp, "log": lambda x, base=None: sp.log(x) if base is None else sp.log(x, base),
            "sqrt": sp.sqrt, "abs": sp.Abs, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "arcsin": sp.asin,
            "arccos": sp.acos, "arctan": sp.atan, "arctan2": sp.atan2, "erf": sp.erf, "erfc": sp.erfc,
            "gamma": sp.gamma, "lgamma": sp.loggamma, "digamma": sp.digamma, "beta": sp.beta,
            "besselJ": lambda x, nu: sp.besselj(nu, x), "sinc": lambda x: sp.sinc(sp.pi * x)}


def _unevaluated_functions(sp) -> dict:
    """The formula functions as SymPy functions that keep their values unevaluated (gamma(2000) stays gamma(2000)
    until SymPy doit works it out under the time limit)."""
    def keep(function):
        return lambda *values, **_: function(*values, evaluate=False)

    named = {name: keep(function) for name, function in
             {"exp": sp.exp, "sqrt": sp.sqrt, "abs": sp.Abs, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
              "arcsin": sp.asin, "arccos": sp.acos, "arctan": sp.atan, "arctan2": sp.atan2, "erf": sp.erf,
              "erfc": sp.erfc, "gamma": sp.gamma, "lgamma": sp.loggamma, "digamma": sp.digamma,
              "beta": sp.beta}.items()}
    named["log"] = lambda x, base=None, **_: (sp.log(x, evaluate=False) if base is None
                                               else sp.log(x, base, evaluate=False))
    named["besselJ"] = lambda x, nu, **_: sp.besselj(nu, x, evaluate=False)
    named["sinc"] = lambda x, **_: sp.sinc(sp.Mul(sp.pi, x, evaluate=False), evaluate=False)
    return named


def _too_big_special(text: str, name: str) -> SimplydataError:
    return _formula_error(f'"{text}": {name}() of a number bigger than {MAX_SPECIAL_ARGUMENT} is too big to work out '
                          "exactly. Use a smaller number, or a letter for it and find_value_at() for a decimal.")


def _specials(sp) -> tuple:
    """The special functions whose number may be at most MAX_SPECIAL_ARGUMENT (gamma(1000) is worked out exactly)."""
    return sp.gamma, sp.loggamma, sp.digamma, sp.beta, sp.besselj


def _special_name(node) -> str:
    """The name of a special function as it is written in a formula."""
    return {"loggamma": "lgamma", "besselj": "besselJ"}.get(type(node).__name__, type(node).__name__)


def _size_of_number(sp, value):
    """The size of a value that is a number (worked out by SymPy N under the time limit when it is not written as a
    plain number); None for a value that still has letters, or has no size."""
    if value.is_Symbol:
        return None
    found = value if value.is_Number else _guarded(sp.N, value, 15, what="SymPy N")
    if not found.is_number:
        return None
    try:
        return abs(complex(found))
    except (TypeError, ValueError):  # zoo, nan: no size
        return None


def _power_digits(sp, base, power) -> float:
    """About how many digits base**power has, for a number base and a fraction power: the power times the digits of
    the biggest whole number in the base (the top or the bottom of its fractions)."""
    heights = [math.log10(max(abs(int(r.p)), int(r.q), 1)) for r in base.atoms(sp.Rational)]
    return abs(float(power)) * max(heights, default=0.0)


def _too_many_digits(text: str) -> SimplydataError:
    return _formula_error(f'"{text}" has a number with more than {MAX_DIGITS} digits, too big to work with exactly. '
                          "Use smaller numbers, or a letter for it.")


def _height(number) -> float:
    """The digits of a fraction: those of the bigger of its top and its bottom."""
    return math.log10(max(abs(int(number.p)), int(number.q), 1))


def _times(power, digits: float) -> float:
    """|power| times digits, for a fraction power of any size (a power too big for a float is endless)."""
    if digits == 0:
        return 0.0  # 1**p and 0**p have no digits, however big p is
    try:
        return abs(float(power)) * digits
    except OverflowError:
        return math.inf


def _digits(sp, value) -> float:
    """At most about how many digits the biggest exact number in value has once SymPy has worked it out. A fraction
    has its own; a power is sized by _pow_digits and an exp by _exp_digits; a product or a sum has the digits of its
    parts added up (the numbers in a product are multiplied together, and a sum of fractions has the product of
    their bottoms); anything else (a function, a letter) has those of its parts."""
    if value.is_Rational:
        return _height(value)
    if value.is_Atom:
        return 0.0
    if isinstance(value, sp.exp):
        return _exp_digits(sp, value.args[0])
    if value.is_Pow:
        return _pow_digits(sp, *value.args)
    return _combined(value, [_digits(sp, part) for part in value.args])


def _combined(value, parts) -> float:
    """The digits of a product, sum or function from those of its parts (a sum may carry one more digit per ten
    parts)."""
    total = math.fsum(parts)
    return total + math.log10(len(parts)) if value.is_Add and parts else total


def _pow_digits(sp, base, power) -> float:
    """At most about how many digits base**power has once SymPy has worked it out (the power and the base worked
    out). SymPy works out a power of a fraction (999**100); multiplies out a power of a product ((999*x)**100 is
    999**100 * x**100); writes a power of a power as one power ((2**sqrt(2))**(1000*sqrt(2)) is 2**2000); and writes
    exp(c)**p as exp(c*p), so exp(2)**(1500*log(10)) is exp(3000*log(10)), which is 10**3000. A power of a sum or of
    a function is left as it is ((x + 999)**400), so it has the digits of its parts."""
    if base == sp.E:
        return _exp_digits(sp, power)
    if isinstance(base, sp.exp):
        return _exp_digits(sp, base.args[0] * power)
    if base.is_Mul:
        return math.fsum(_pow_digits(sp, factor, power) for factor in base.args)
    if base.is_Pow:
        return max(_pow_digits(sp, base.args[0], base.args[1] * power), _digits(sp, base))
    if base.is_Rational and power.is_Rational:
        return _times(power, _height(base))
    return _digits(sp, base) + _digits(sp, power)


def _exp_digits(sp, value) -> float:
    """At most about how many digits exp(value) has once SymPy has worked it out. SymPy exp writes exp(n*log(b)) as
    b**n (and exp(n*log(b) + x) as b**n * exp(x)) when n is a fraction: each such term of value counts as that
    power, and the terms together as the product of those powers (exp(log(2)*3000 + log(3)*2000) is
    2**3000 * 3**2000)."""
    total = 0.0
    for term in sp.Add.make_args(value):
        factors = sp.Mul.make_args(term)
        logs = [f for f in factors if isinstance(f, sp.log)]
        rest = sp.Mul(*[f for f in factors if not isinstance(f, sp.log)])
        if len(logs) == 1 and rest.is_Rational:
            total += _pow_digits(sp, logs[0].args[0], rest)
        else:
            total += _digits(sp, term)
    return total


def _check_exp(sp, value, text: str) -> float:
    """Refuse exp(value) when SymPy would turn it into a number with more than MAX_DIGITS digits (_exp_digits);
    else its digits."""
    digits = _exp_digits(sp, value)
    if digits > MAX_DIGITS:
        raise _too_many_digits(text)
    return digits


def _work_out(sp, tree, text: str):
    """The unevaluated formula from parse_expr(evaluate=False), worked out; None when nothing in it can be heavy.

    Every power whose base is not a plain letter or a plain number, every power with a big or worked-out exponent,
    and every exp of a log is sized first, from the inside out, so that a number with more than MAX_DIGITS digits
    is refused before SymPy makes it: (abs(999)**100)**100 (each further **100 makes it 100 times longer),
    (999*x)**100 (SymPy multiplies out the 999), exp(3000*log(10)) (SymPy writes 10**3000). Each piece is sized as
    SymPy works it out: here while nothing before it is heavy (so it is small), else by SymPy under the time limit.
    The numbers inside the special functions are checked too. Products and sums are sized from their parts (four
    999**100 multiplied together have 1,200 digits). A formula with anything heavy is then worked out by SymPy doit
    under the time limit, never here while the text is read."""
    heavy = False
    digits: dict = {}  # each part of the formula -> at most how many digits it has once worked out

    def worked_out(*values):
        return list(_guarded(sp.Tuple, *values, what="SymPy evaluate")) if heavy else [v.doit() for v in values]

    for node in sp.postorder_traversal(tree):
        if node.is_Atom:
            digits[node] = _digits(sp, node)
            continue
        if isinstance(node, _specials(sp)):
            heavy = True
            for value in node.args:
                size = _size_of_number(sp, value)
                if size is not None and not size <= MAX_SPECIAL_ARGUMENT:
                    raise _too_big_special(text, _special_name(node))
            found = _combined(node, [digits[p] if p in digits else _digits(sp, p) for p in node.args])
        elif isinstance(node, sp.exp) and node.args[0].has(sp.log):
            found = _check_exp(sp, worked_out(node.args[0])[0], text)
        elif isinstance(node, sp.Pow):
            base, power = node.args
            small = power.is_Number and (power.is_Float or (
                abs(int(power.p)) <= MAX_LETTER_POWER and int(power.q) <= MAX_LETTER_POWER))
            if not (base.is_Symbol or (base.is_Number and small)):  # else x**k, or a small power of a number
                heavy = heavy or not small
                base, power = worked_out(base, power)
                if power.is_Rational and (base.is_number or isinstance(base, (sp.Mul, sp.Pow))) and \
                        _power_digits(sp, base, power) > MAX_DIGITS:
                    raise _too_many_digits(text)  # a number, or a product SymPy multiplies out: (999*x)**100
            found = _pow_digits(sp, base, power)  # exp(2)**(1500*log(10)) is 10**3000
        else:
            found = _combined(node, [digits[p] if p in digits else _digits(sp, p) for p in node.args])
        if found > MAX_DIGITS:
            raise _too_many_digits(text)
        digits[node] = found
    if not heavy:
        return None
    return _guarded(tree.doit, what="SymPy doit")


def letters_of(text, what: str = "sdata.formula()") -> list[str]:
    """The letters of formula text (checked with ast, never run), in the order they first appear."""
    if isinstance(text, Formula):
        return text._letters()
    if not isinstance(text, str):
        return []
    try:
        tree = ast.parse(text.strip(), mode="eval")
    except SyntaxError:
        return []
    letters: list = []
    try:
        _check_node(tree, text.strip(), letters, set())
    except SimplydataError:  # parse() says what is wrong with the text, in its own words
        return []
    return letters


def letter_kind_symbols(letters_are, letters, what: str, example: str) -> dict:
    """letters_are={"k": "positive"} -> {"k": Symbol("k", positive=True)}; names and kinds are checked first."""
    if letters_are is None:
        return {}
    sp = need_sympy(what)
    if not isinstance(letters_are, dict) or not letters_are:
        raise SimplydataError(f'letters_are= needs a dict of letter -> what it is, such as {{"k": "positive"}}.\n'
                              f"For example:  {example}")
    symbols = {}
    for name, kind in letters_are.items():
        if not isinstance(name, str) or name not in letters:
            raise SimplydataError(f"letters_are= names {name!r}, which is not a letter of the formula. Its letters: "
                                  f"{', '.join(letters) or 'none'}.\nFor example:  {example}")
        key = kind.strip().lower() if isinstance(kind, str) else None
        key = LETTER_KIND_SPELLINGS.get(key, key)
        if key not in LETTER_KINDS:
            raise choice_error(what.split("(")[0].replace("sdata.", ""), f"letters_are for {name}", kind,
                               list(LETTER_KINDS))
        symbols[name] = sp.Symbol(name, **LETTER_KINDS[key])
    return symbols


def kind_of(symbol) -> str | None:
    """What a letter is, in the words of letters_are= (None for a plain letter)."""
    if symbol.is_integer and symbol.is_positive:
        return "positive whole number"
    if symbol.is_integer:
        return "whole number"
    if symbol.is_positive:
        return "positive"
    if symbol.is_nonnegative:
        return "zero or more"
    if symbol.is_negative:
        return "negative"
    if symbol.is_real:
        return "real"
    return None


def parse(text, what: str = "sdata.formula()", letters_known=None, symbols=None):
    """Formula text (or a formula) -> a SymPy expression. The text is checked with ast before SymPy reads it.

    symbols= gives some letters as ready-made SymPy Symbols (with assumptions, from letters_are=)."""
    sp = need_sympy(what)
    if isinstance(text, Formula):
        return text._expr
    if isinstance(text, bool) or not isinstance(text, (str, int, float, np.integer, np.floating)):
        raise _formula_error(f"{what} needs the formula as text in quotes (or a number); it got {text!r}.")
    if not isinstance(text, str):
        if isinstance(text, (int, np.integer)):
            return sp.Integer(int(text))
        return exact_number(sp, text) if math.isfinite(float(text)) else sp.Float(float(text))
    if not text.strip():
        raise _formula_error("The formula is empty.")
    for sign in ("<=", ">=", "==", "=", "<", ">"):
        if sign in text:
            raise _formula_error(
                f'"{text}" has {sign} in it, so it is an equation, not a formula. Give only the formula here, such as '
                '"x**2 - 2"; to solve an equation exactly use sdata.solve("x**2 = 2", exactly=True).')
    try:
        tree = ast.parse(text.strip(), mode="eval")
    except SyntaxError:
        raise _formula_error(f'"{text}" cannot be read as a formula. Check the brackets, and write 2*x for 2 times '
                             "x.") from None
    letters: list = []
    functions: set = set()
    _check_node(tree, text.strip(), letters, functions)
    from sympy.parsing.sympy_parser import convert_xor, parse_expr, standard_transformations

    known = dict(letters_known or {})
    made = dict(symbols or {})
    local = {name: known[name] if name in known else made.get(name, sp.Symbol(name)) for name in letters}
    named = _sympy_functions(sp)
    for name in functions:
        local[name] = named[SPELLINGS.get(name, name)]
    local["pi"] = sp.pi
    safe = {"Integer": sp.Integer, "Float": sp.Float, "Rational": sp.Rational, "Symbol": sp.Symbol,
            "__builtins__": {}}
    transformations = standard_transformations + (convert_xor,)
    # first unevaluated: nothing is worked out while the text is read (gamma(abs(-2000)) stays as it is)
    kept = _unevaluated_functions(sp)
    unevaluated = {**local, **{name: kept[SPELLINGS.get(name, name)] for name in functions}}
    tree = parse_expr(text.strip(), local_dict=unevaluated, transformations=transformations, evaluate=False,
                      global_dict={**safe, "Add": sp.Add, "Mul": sp.Mul, "Pow": sp.Pow})
    worked_out = _work_out(sp, tree, text.strip())
    if worked_out is not None:
        return worked_out
    return parse_expr(text.strip(), local_dict=local, global_dict=safe, transformations=transformations)


def _python_printer():
    """SymPy's StrPrinter, writing functions as the simplydata formula reader knows them."""
    from sympy.printing.str import StrPrinter

    names = {"Abs": "abs", "loggamma": "lgamma", "asin": "arcsin", "acos": "arccos", "atan": "arctan",
             "atan2": "arctan2"}

    class FormulaPrinter(StrPrinter):
        def _print_Function(self, expr):
            name = expr.func.__name__
            args = [self._print(a) for a in expr.args]
            if name == "besselj":
                return f"besselJ({args[1]}, {args[0]})"
            if name == "sinc":
                return f"sinc(({args[0]})/pi)"
            return f"{names.get(name, name)}({', '.join(args)})"

        def _print_Exp1(self, expr):
            return "exp(1)"

        def _print_Infinity(self, expr):
            return "inf"

    return FormulaPrinter()


def formula_text(expr) -> str:
    """A SymPy expression written as simplydata formula text (** for powers; abs, lgamma, besselJ(x, nu))."""
    return _python_printer().doprint(expr)


def _show(expr) -> str:
    """How an answer is printed: SymPy's own text (sqrt(2), pi, x**2 + 4*x), with oo written as infinity. A number
    with more digits than Python writes out (4300) is shown as a decimal with its number of digits."""
    import sympy as sp

    if expr == sp.oo:
        return "infinity"
    if expr == -sp.oo:
        return "-infinity"
    try:
        return str(expr)
    except ValueError:  # Python's limit on writing very long whole numbers
        return _too_long(sp, expr)


def _digit_count(sp, whole: int) -> int:
    """How many digits a whole number above 0 has: the power of ten of SymPy N(whole, 30), plus one. Only when that
    decimal reads 1.000...0 (the number is within 5e-30 of a power of ten, where rounding could cross it) does SymPy
    integer_log decide, which is exact but slow for millions of digits (it works out the power of ten itself)."""
    near = _guarded(sp.N, sp.Integer(whole), 30, what="SymPy N")
    mantissa, _, power = str(near).upper().partition("E")
    if power and mantissa.replace(".", "").rstrip("0") != "1":
        return int(power) + 1
    found, _ = _guarded(sp.integer_log, whole, 10, what="SymPy integer_log")
    return int(found) + 1


def _too_long(sp, expr) -> str:
    """A number too long to write out, as "about 6.01452E+15151335 (a whole number of 15,151,336 digits)": the first
    digits from SymPy N(expr, 6) and the number of digits from SymPy (_digit_count), all under the time limit."""
    if isinstance(expr, sp.Rational) and expr.p:
        lead = _guarded(sp.N, expr, 6, what="SymPy N")
        part = "a whole number of" if isinstance(expr, sp.Integer) else "a fraction whose top has"
        return f"about {lead} ({part} {_digit_count(sp, abs(int(expr.p))):,} digits, too long to write out)"
    return "(an exact answer with numbers of more than 4300 digits, too long to write out)"


def _decimal(value) -> str:
    x = float(value)
    if math.isinf(x):
        return "infinity" if x > 0 else "minus infinity"
    return f"{x:.10g}"


def _limit_value(sp, value, what: str):
    """A number, or "infinity" / "-infinity", as SymPy's number."""
    if isinstance(value, str):
        key = value.strip().lower()
        if key in INFINITY:
            return sp.oo
        if key in MINUS_INFINITY:
            return -sp.oo
        raise SimplydataError(f'{what} takes a number, "infinity" or "-infinity"; it got "{value}".')
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise SimplydataError(f'{what} takes a number, "infinity" or "-infinity"; it got {value!r}.')
    if math.isinf(float(value)):
        return sp.oo if value > 0 else -sp.oo
    return exact_number(sp, value)


# ---------------------------------------------------------------- the formula object
def _guarded(call, *values, what: str, hint: str = FORMULA_HINT, **named):
    """A heavy SymPy call under simplydata's one time limit (see _time_limit.py)."""
    from ._time_limit import run_with_time_limit

    return run_with_time_limit(call, *values, what=what, hint=hint, **named)


def decimal_of(expr, what: str = "SymPy N", hint: str = FORMULA_HINT, digits: int = 15):
    """The decimal of an exact number, worked out by SymPy under the time limit."""
    import sympy as sp

    return _guarded(sp.N, expr, digits, what=what, hint=hint)


def float_of(expr, what: str = "SymPy N", hint: str = FORMULA_HINT) -> float:
    """A real exact number as a float; NaN when it is not a real number."""
    value = complex(decimal_of(expr, what, hint))
    return value.real if abs(value.imag) <= 1e-12 * max(1.0, abs(value.real)) else math.nan


def kind_words(kind: str) -> str:
    """What a letter is, after "x is": "positive", "a whole number", "a positive whole number"."""
    return f"a {kind}" if kind.endswith("whole number") else kind


def _domain_words(sp, domain) -> str:
    """The real numbers a rule is solved over, in words."""
    return {sp.S.Reals: "the real numbers", sp.Interval.open(0, sp.oo): "the positive numbers",
            sp.Interval(0, sp.oo): "the numbers zero or more",
            sp.Interval.open(-sp.oo, 0): "the negative numbers"}.get(domain, str(domain))


# what a letter is -> the real numbers it may take (letters_are=)
def kind_domain(sp, symbol):
    """The set of real numbers a letter may be, from what letters_are= said (Reals for a plain letter)."""
    kind = kind_of(symbol)
    return {"positive whole number": sp.S.Naturals, "whole number": sp.S.Integers,
            "positive": sp.Interval.open(0, sp.oo), "zero or more": sp.Interval(0, sp.oo),
            "negative": sp.Interval.open(-sp.oo, 0)}.get(kind, sp.S.Reals)


def _fits_kind(value, kind: str) -> bool:
    """Whether SymPy's assumptions show that value is what letters_are= says (2*y is positive for a positive y)."""
    checks = {"positive": ("is_positive",), "zero or more": ("is_nonnegative",), "negative": ("is_negative",),
              "whole number": ("is_integer",), "positive whole number": ("is_integer", "is_positive"),
              "real": ("is_real",)}[kind]
    return all(getattr(value, check) is True for check in checks)


def check_value_fits(symbol, value, step: str) -> None:
    """Refuse a number that contradicts what letters_are= said the letter is (x positive, x = -2)."""
    kind = kind_of(symbol)
    if kind is None or kind == "real":
        return
    numbers = np.asarray(value, dtype=float).ravel()
    numbers = numbers[~np.isnan(numbers)]
    fits = {"positive": numbers > 0, "zero or more": numbers >= 0, "negative": numbers < 0,
            "whole number": numbers == np.round(numbers),
            "positive whole number": (numbers == np.round(numbers)) & (numbers > 0)}[kind]
    if not np.all(fits):
        bad = numbers[~fits][0]
        raise SimplydataError(f"{step}() was given {symbol} = {bad:g}, but the formula says {symbol} is "
                              f"{kind_words(kind)} (letters_are=). SymPy may have used that already "
                              f"({_kind_example(kind, str(symbol))}), so the answer would be wrong. Give a value that "
                              f"is {kind_words(kind)}, or make the formula without letters_are=.")


def _kind_example(kind: str, name: str) -> str:
    """What SymPy may do with a letter of this kind, for the sentences that refuse a value that is not of it."""
    return {"positive": f"sqrt({name}**2) is {name} only for a positive {name}",
            "zero or more": f"sqrt({name}**2) is {name} only for {name} zero or more",
            "negative": f"sqrt({name}**2) is -{name} only for a negative {name}",
            "real": f"abs({name})**2 is {name}**2 only for a real {name}",
            "whole number": f"cos(pi*{name})**2 is 1 only for a whole {name}",
            "positive whole number": f"cos(pi*{name})**2 is 1 only for a whole {name}"}[kind]


def _kind_expression_example(kind: str) -> str:
    """An expression SymPy can show is of this kind."""
    return {"positive": "2*y with y positive", "zero or more": "y**2 with y real", "negative": "-y with y positive",
            "real": "y + 1 with y real", "whole number": "n + 1 with n a whole number",
            "positive whole number": "n + 1 with n a positive whole number"}[kind]


def _check_one_letter_per_name(expr, swaps: dict, values: dict) -> None:
    """Refuse a put_in() that would leave two different letters with one name: SymPy tells letters apart by what
    they are as well as by name, so put_in(x="z", w="z") with x positive and w negative would make a positive z and
    a negative z, and z - z would not be 0."""
    seen: dict = {}
    for symbol in sorted((expr.free_symbols - set(swaps)).union(*[v.free_symbols for v in swaps.values()]),
                         key=lambda s: (str(s), str(kind_of(s)))):
        first = seen.setdefault(str(symbol), symbol)
        if first != symbol:
            kinds = " and one ".join(kind_words(kind_of(s)) if kind_of(s) else "plain (any number)"
                                     for s in (first, symbol))
            given = ", ".join(f"{k}={v!r}" for k, v in values.items())
            raise SimplydataError(
                f"put_in({given}) would make two different letters called {symbol}, one {kinds} (a new letter takes "
                "what the letter it replaces is, from letters_are=). SymPy keeps such letters apart, so the answer "
                "could be wrong. Give each place a new letter of its own, or write the formula again with the new "
                "letters and give them their own letters_are=.")


def _check_put_in_digits(sp, expr, symbol, value, said: str) -> None:
    """Refuse put_in() when putting value in place of symbol would make a number with more than MAX_DIGITS digits,
    before SymPy makes it (2**x with x = 10000 has 3,011 digits). Each part of the formula is sized from the inside
    out with the value in it, as _work_out sizes a formula when it is read; a part that is a power or an exp is
    sized from its base and power with the value put in (worked out by SymPy under the time limit when they are
    more than the letter itself, and already sized, so never huge). The numbers inside the special functions are
    checked as when a formula is read."""
    digits: dict = {}
    built: dict = {}

    def put_in(part):
        if part == symbol:
            return value
        if not part.has(symbol):
            return part
        if part not in built:
            built[part] = _guarded(part.xreplace, {symbol: value}, what="SymPy subs")
        return built[part]

    for node in sp.postorder_traversal(expr):
        if node == symbol:
            found = _digits(sp, value)
        elif node.is_Atom:
            found = _digits(sp, node)
        elif not node.has(symbol):
            found = _combined(node, [digits[p] if p in digits else _digits(sp, p) for p in node.args]) \
                if not (node.is_Pow or isinstance(node, sp.exp)) else _digits(sp, node)
        elif isinstance(node, sp.exp):
            found = _exp_digits(sp, put_in(node.args[0]))
        elif node.is_Pow:
            found = _pow_digits(sp, put_in(node.args[0]), put_in(node.args[1]))
        else:
            if isinstance(node, _specials(sp)):
                for part in node.args:
                    size = _size_of_number(sp, put_in(part))
                    if size is not None and not size <= MAX_SPECIAL_ARGUMENT:
                        raise SimplydataError(f"put_in() would give {_special_name(node)}() a number bigger than "
                                              f"{MAX_SPECIAL_ARGUMENT} ({said}), too big to work out exactly. Use a "
                                              "smaller number, or keep the letter and use find_value_at() for a "
                                              "decimal.")
            found = _combined(node, [digits[p] if p in digits else _digits(sp, p) for p in node.args])
        if found > MAX_DIGITS:
            raise SimplydataError(f"put_in() would make a number with more than {MAX_DIGITS} digits ({said}), too "
                                  "big to work with exactly. Put in a smaller number, or keep the letter and use "
                                  "find_value_at() for a decimal.")
        digits[node] = found


def check_range_fits(formula, name: str, low: float, high: float, step: str) -> None:
    """Refuse a range of a letter that goes outside what letters_are= said the letter is."""
    expr = getattr(formula, "_expr", None)
    if expr is None:
        return
    symbol = next((s for s in expr.free_symbols if str(s) == name), None)
    if symbol is None or kind_of(symbol) in (None, "real"):
        return
    kind = kind_of(symbol)
    if kind in ("whole number", "positive whole number"):  # a range of numbers always has numbers between them
        raise SimplydataError(f"{step}() works with every number of {name} from {low:g} to {high:g}, but the formula "
                              f"says {name} is {kind_words(kind)} (letters_are=), and SymPy may have used that already "
                              f"(cos(pi*{name})**2 is 1 only for a whole {name}), so the answer would be wrong between "
                              f"the whole numbers. Make the formula without letters_are= for {step}().")
    inside = {"positive": low >= 0, "zero or more": low >= 0, "negative": high <= 0}.get(kind, True)
    if not inside:
        raise SimplydataError(f"{step}() goes over {name} from {low:g} to {high:g}, but the formula says {name} is "
                              f"{kind_words(kind)} (letters_are=), and SymPy may have used that already "
                              f"({_kind_example(kind, name)}), so the answer would be wrong "
                              f"there. Keep between= where {name} is {kind}, or make the formula without "
                              "letters_are=.")


def _whole(value, option: str, low: int, high: int, example: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or not low <= value <= high:
        raise SimplydataError(f"{option} needs a whole number from {low} to {high:,}; it got {value!r}.\n"
                              f"For example:  {example}")
    return int(value)


def _ordinal(n: int) -> str:
    end = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{end}"


def _said_letters(symbols) -> str:
    """"k (positive), t" for the letters of a formula, with what each is when letters_are= said so."""
    parts = []
    for s in sorted(symbols, key=str):
        kind = kind_of(s)
        parts.append(f"{s} ({kind})" if kind else str(s))
    return ", ".join(parts)


def check_letter_powers(sp, expr, step: str) -> None:
    """Refuse a sum with letters raised to a whole power above MAX_LETTER_POWER before it is multiplied out:
    (x + y + z + 1)**200 has about 1.4 million terms."""
    for power in expr.atoms(sp.Pow):
        if (power.exp.is_Integer and abs(int(power.exp)) > MAX_LETTER_POWER and power.base.is_Add
                and power.base.free_symbols):
            raise SimplydataError(f"{power.base} is raised to the power {power.exp}: multiplied out it has far too "
                                  f"many terms to work with. {step}() takes powers of a sum with letters up to "
                                  f"{MAX_LETTER_POWER}; use a smaller power, or keep the brackets.")


class Formula:
    """A formula that SymPy works with exactly. Make one with sdata.formula("(x + 2)**2 - 4").

    Words: make_simpler, turn_into_sum, turn_into_product, find_slope_formula, find_area_formula, find_value_at,
    put_in, show_as_latex, find_limit_as, find_taylor_series, undo, show_as_decimal, group_by_powers_of,
    turn_into_partial_fractions, as_sympy.
    """

    _OLD_WORDS: dict = {}  # no old names (sdata.help reads this, as for tables and systems)

    def __init__(self, expr):
        object.__setattr__(self, "_expr", expr)
        object.__setattr__(self, "_history", [])

    def __setattr__(self, name, value):
        raise SimplydataError("A formula is changed with its words, such as f.make_simpler(); f.undo() takes a "
                              "step back.")

    @classmethod
    def _word_names(cls) -> list[str]:
        return list(WORDS)

    def __dir__(self):
        return list(WORDS)

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        lines = [f"A formula has no word called .{name}()."]
        if name in HINTS:
            lines.append(f"In simplydata this is f.{HINTS[name]}." if not HINTS[name].startswith("sdata.")
                         else f"In simplydata this is {HINTS[name]}.")
        else:
            guesses = suggest(name, list(WORDS))
            if guesses:
                lines.append("Did you mean " + " or ".join(f".{g}()" for g in guesses) + "?")
        lines.append("Every word for a formula: " + ", ".join(WORDS))
        raise MissingWordError("\n".join(lines))

    def __repr__(self):
        said = _said_letters(self._expr.free_symbols) or "none"
        return f"simplydata formula: {_show(self._expr)}   (letters: {said})"

    def __str__(self):
        return _show(self._expr)

    def _repr_latex_(self):
        """Jupyter shows a formula typeset, from SymPy latex (no word: the display only)."""
        import sympy as sp

        return f"$\\displaystyle {sp.latex(self._expr)}$"

    def _formula_text(self) -> str:
        """The formula as text for the other simplydata words (find_where_smallest, find_area_under ...)."""
        return formula_text(self._expr)

    def _has_conditions(self) -> bool:
        """Whether the formula holds only under conditions (a SymPy Piecewise), which formula text cannot write: the
        other words then work with the SymPy expression itself."""
        import sympy as sp

        return self._expr.has(sp.Piecewise)

    # ---------------------------------------------------------------- helpers
    def _letters(self) -> list[str]:
        return sorted(str(s) for s in self._expr.free_symbols)

    def _symbols(self) -> dict:
        """The formula's own letters as SymPy Symbols, by name (with what letters_are= said they are)."""
        return {str(s): s for s in self._expr.free_symbols}

    def _symbol(self, name: str):
        import sympy as sp

        return self._symbols().get(name, sp.Symbol(name))

    def _letter(self, step: str, for_letter, example: str):
        """The letter to work with: for_letter=, or the only letter of the formula."""
        need_sympy(f"f.{step}()")
        letters = self._letters()
        if for_letter is None:
            if len(letters) == 1:
                return self._symbol(letters[0])
            if not letters:
                raise SimplydataError(f"{_show(self._expr)} has no letter, so .{step}() has nothing to work with.")
            raise SimplydataError(f"{_show(self._expr)} has {len(letters)} letters ({', '.join(letters)}): say which "
                                  f"one with for_letter=.\nFor example:  f.{example}")
        if not isinstance(for_letter, str) or for_letter not in letters:
            raise SimplydataError(f"for_letter= needs one of the letters of the formula in quotes: "
                                  f"{', '.join(repr(n) for n in letters) or 'none'}.\nFor example:  f.{example}")
        return self._symbol(for_letter)

    def _change(self, what: str, new):
        self._history.append((what, self._expr))
        object.__setattr__(self, "_expr", new)
        return self

    # ---------------------------------------------------------------- changing the formula (with undo)
    @friendly
    def make_simpler(self):
        """Write the formula in a simpler way (SymPy simplify). f.make_simpler()

        f = sdata.formula("(x**2 - 1) / (x - 1)"), then f.make_simpler() gives x + 1. The formula changes;
        f.undo() takes the step back. As SymPy simplify(); MATLAB simplify.
        """
        sp = need_sympy("f.make_simpler()")
        new = _guarded(sp.simplify, self._expr, what="SymPy simplify")
        print(f"{_show(self._expr)} written more simply: {_show(new)}   (SymPy simplify)")
        return self._change("make simpler", new)

    @friendly
    def turn_into_sum(self):
        """Multiply out the brackets, so the formula is a sum of terms (SymPy expand). f.turn_into_sum()

        f = sdata.formula("(x + 2)**2 - 4"), then f.turn_into_sum() gives x**2 + 4*x. The formula changes;
        f.undo() takes the step back. turn_into_product() goes the other way. As SymPy expand(). A sum with letters
        raised to a whole power above 100 is refused (it would have far too many terms).
        """
        sp = need_sympy("f.turn_into_sum()")
        check_letter_powers(sp, self._expr, "turn_into_sum")
        new = _guarded(sp.expand, self._expr, what="SymPy expand")
        print(f"{_show(self._expr)} multiplied out: {_show(new)}   (SymPy expand)")
        return self._change("turn into sum", new)

    @friendly
    def turn_into_product(self):
        """Write the formula as a product of factors (SymPy factor). f.turn_into_product()

        f = sdata.formula("x**2 + 4*x"), then f.turn_into_product() gives x*(x + 4). The formula changes;
        f.undo() takes the step back. turn_into_sum() goes the other way. As SymPy factor().
        """
        sp = need_sympy("f.turn_into_product()")
        new = _guarded(sp.factor, self._expr, what="SymPy factor")
        print(f"{_show(self._expr)} as a product: {_show(new)}   (SymPy factor)")
        return self._change("turn into product", new)

    @friendly
    @one_deadline
    def group_by_powers_of(self, letter=None):
        """Multiply out, then gather the terms by the powers of one letter (SymPy collect). f.group_by_powers_of("x")

        f = sdata.formula("a*x**2 + b*x**2 + a*x - x"), then f.group_by_powers_of("x") gives
        x**2*(a + b) + x*(a - 1). The formula changes; f.undo() takes the step back. As SymPy collect(expand(...), x).
        A sum with letters raised to a whole power above 100 is refused.
        """
        sp = need_sympy("f.group_by_powers_of()")
        x = self._letter("group_by_powers_of", letter, 'group_by_powers_of("x")')
        check_letter_powers(sp, self._expr, "group_by_powers_of")
        expanded = _guarded(sp.expand, self._expr, what="SymPy expand")
        new = _guarded(sp.collect, expanded, x, what="SymPy collect")
        print(f"{_show(self._expr)} grouped by powers of {x}: {_show(new)}   (SymPy collect)")
        return self._change(f"group by powers of {x}", new)

    @friendly
    def turn_into_partial_fractions(self, for_letter=None):
        """Split a fraction of polynomials into a sum of simple fractions (SymPy apart). f.turn_into_partial_fractions()

        f = sdata.formula("(3*x + 5) / ((x + 1)*(x + 2))"), then f.turn_into_partial_fractions() gives
        1/(x + 2) + 2/(x + 1). for_letter= says which letter when there are several. The formula changes; f.undo()
        takes the step back. As SymPy apart(); MATLAB partfrac.
        """
        sp = need_sympy("f.turn_into_partial_fractions()")
        x = self._letter("turn_into_partial_fractions", for_letter, 'turn_into_partial_fractions(for_letter="x")')
        if not self._expr.is_rational_function(x):
            raise SimplydataError(f"turn_into_partial_fractions() works on a fraction of polynomials in {x}, such as "
                                  f"(3*x + 5)/((x + 1)*(x + 2)); {_show(self._expr)} is not one.")
        check_letter_powers(sp, self._expr, "turn_into_partial_fractions")
        new = _guarded(sp.apart, self._expr, x, what="SymPy apart")
        print(f"{_show(self._expr)} as partial fractions: {_show(new)}   (SymPy apart)")
        return self._change("turn into partial fractions", new)

    @friendly
    def undo(self):
        """Take the last change of the formula back. f.undo()"""
        if not self._history:
            print("Nothing to undo: this formula has not changed.")
            return self
        what, old = self._history.pop()
        object.__setattr__(self, "_expr", old)
        print(f"Undone: {what}. The formula is {_show(old)} again.")
        return self

    # ---------------------------------------------------------------- new formulas
    @friendly
    def find_slope_formula(self, for_letter=None, how_many_times=1) -> Formula:
        """The formula of the slope (the derivative), as a new formula. f.find_slope_formula()

        f = sdata.formula("x**3 - 2*x"), then f.find_slope_formula() gives 3*x**2 - 2. for_letter= says which
        letter when there are several. how_many_times=2 takes the slope of the slope (the second derivative), up to
        20 times. for_letter=["x", "y"] takes the slope for x, then for y (a mixed partial derivative). As SymPy
        diff(); MATLAB diff; R D().
        """
        sp = need_sympy("f.find_slope_formula()")
        example = 'find_slope_formula(for_letter="x")'
        times = _whole(how_many_times, "how_many_times=", 1, MAX_SLOPE_TIMES, "f.find_slope_formula(how_many_times=2)")
        if isinstance(for_letter, (list, tuple)):
            if times != 1:
                raise SimplydataError('how_many_times= works with one letter. With a list, name a letter more than '
                                      'once: for_letter=["x", "x", "y"].')
            if not 1 <= len(for_letter) <= MAX_SLOPE_TIMES:
                raise SimplydataError(f"for_letter= needs a list of 1 to {MAX_SLOPE_TIMES} letters, such as "
                                      'for_letter=["x", "y"].')
            letters = [self._letter("find_slope_formula", name, 'find_slope_formula(for_letter=["x", "y"])')
                       for name in for_letter]
            new = _guarded(sp.diff, self._expr, *letters, what="SymPy diff")
            if len(letters) > 1:
                said = ", then ".join(str(s) for s in letters)
                print(f"The slope of {_show(self._expr)} as {said} change: {_show(new)}   (a mixed partial "
                      "derivative; SymPy diff)")
                return Formula(new)
            x = letters[0]
        else:
            x = self._letter("find_slope_formula", for_letter, example)
            new = _guarded(sp.diff, self._expr, x, times, what="SymPy diff")
        if times == 1:
            print(f"The slope of {_show(self._expr)} as {x} changes: {_show(new)}   (the derivative; SymPy diff)")
        else:
            print(f"The slope of {_show(self._expr)} as {x} changes, {times} times over: {_show(new)}   (the "
                  f"{_ordinal(times)} derivative; SymPy diff)")
        return Formula(new)

    @friendly
    def find_area_formula(self, for_letter=None) -> Formula:
        """The formula of the area under the curve (the integral), as a new formula. f.find_area_formula()

        f = sdata.formula("x**3 - 2*x"), then f.find_area_formula() gives x**4/4 - x**2 (add any constant).
        for_letter= says which letter when there are several. sdata.find_area_under("...", between=[a, b]) gives
        the area as a number. As SymPy integrate(); MATLAB int.
        """
        sp = need_sympy("f.find_area_formula()")
        x = self._letter("find_area_formula", for_letter, 'find_area_formula(for_letter="x")')
        new = _guarded(sp.integrate, self._expr, x, what="SymPy integrate")
        if new.has(sp.Integral):
            raise SimplydataError(f"SymPy found no formula for the area under {_show(self._expr)}. For the area "
                                  "between two values as a number, use sdata.find_area_under(\"...\", "
                                  "between=[0, 1]).")
        print(f"The area under {_show(self._expr)} as {x} grows: {_show(new)}, plus any constant   "
              "(the integral; SymPy integrate)")
        return Formula(new)

    def _values_for(self, step: str, values: dict, example: str):
        letters = self._letters()
        if not values and letters:
            raise SimplydataError(f".{step}() needs a value for each letter ({', '.join(letters) or 'none'}).\n"
                                  f"For example:  f.{example}")
        unknown = [k for k in values if k not in letters]
        if unknown:
            raise SimplydataError(f"{', '.join(unknown)} {'is' if len(unknown) == 1 else 'are'} not a letter of "
                                  f"{_show(self._expr)}. Its letters: {', '.join(letters) or 'none'}.")
        return letters

    @friendly
    def find_value_at(self, **values):
        """The value of the formula when each letter has a value. f.find_value_at(x=2)

        f = sdata.formula("x**3 - 2*x"), then f.find_value_at(x=2) gives 4. Give every letter a value. Many
        values at once (a list or numbers) give numbers back: f.find_value_at(x=sdata.numbers(0, to=3,
        how_many=50)). One value: SymPy subs and evalf; many: SymPy lambdify with NumPy and SciPy. An empty value
        (NaN) gives an empty answer, as in a list. lgamma(x) is the log of the size of gamma(x) (SciPy gammaln, as R
        lgamma), for one value and for many.
        """
        sp = need_sympy("f.find_value_at()")
        letters = self._values_for("find_value_at", values, "find_value_at(x=2)")
        missing = [n for n in letters if n not in values]
        if missing:
            raise SimplydataError(f"find_value_at() needs a value for every letter; {', '.join(missing)} "
                                  f"{'has' if len(missing) == 1 else 'have'} none.\nFor example:  f.find_value_at("
                                  + ", ".join(f"{n}=1" for n in letters) + ")")
        many = {k: v for k, v in values.items() if not _one_number(v)}
        for name, value in values.items():
            if name not in many and (isinstance(value, bool) or not isinstance(value, (int, float, np.integer,
                                                                                         np.floating))):
                raise SimplydataError(f"{name}= needs a number or a list of numbers; it got {value!r}.")
        for name, value in values.items():
            check_value_fits(self._symbol(name), value._values if hasattr(value, "_values") else value,
                             "find_value_at")
        singles_empty = any(isinstance(v, (float, np.floating)) and math.isnan(v) for k, v in values.items()
                            if k not in many)
        by_numbers = bool(many) or singles_empty or self._expr.has(sp.loggamma)
        if not by_numbers:
            swaps = {self._symbol(k): parse(v, "find_value_at()") for k, v in values.items()}
            found = _guarded(self._expr.evalf, 15, subs=swaps, what="SymPy evalf")
            if found.is_real and found.is_finite and not math.isfinite(float(found)):
                raise SimplydataError(f"At {_places(values)} the formula is about {sp.N(found, 6)}: a number too big for a "
                                      "decimal (float). f.put_in(...).show_as_decimal() shows it.")
            if not found.is_real:
                if found.is_number:
                    raise SimplydataError(f"At {_places(values)} the formula has no value among the ordinary "
                                          f"numbers (it is {found}).")
                raise SimplydataError(f"At {_places(values)} the formula still has letters: {found}.")
            answer = float(found)
            where = f" at {_places(values)}" if values else " as a decimal"
            print(f"{_show(self._expr)}{where}: {_decimal(answer)}   (SymPy subs and evalf)")
            return answer
        from .numbers._base import to_array
        from .numbers.numbers import Numbers

        arrays = [np.asarray(to_array(values[n], "find_value_at()", "f.find_value_at(x=[0, 1, 2])"), dtype=float)
                  if n in many else float(values[n]) for n in letters]
        from scipy import special

        # lgamma is the log of the size of gamma (SciPy gammaln, as R lgamma and fit_formula), real for every x
        function = sp.lambdify([self._symbol(n) for n in letters], self._expr,
                               modules=[{"loggamma": special.gammaln}, "scipy", "numpy"])
        with np.errstate(all="ignore"):
            out = np.asarray(function(*arrays), dtype=complex)
        shape = np.broadcast_shapes(*[np.shape(a) for a in arrays])
        out = np.broadcast_to(out, shape)
        if np.any(np.abs(out.imag) > 1e-12 * np.maximum(1.0, np.abs(out.real))):
            raise SimplydataError("For some of these values the formula has no value among the ordinary numbers "
                                  "(a square root or log of a negative number).")
        result = np.array(out.real, dtype=float)
        if not many:
            answer = float(result.reshape(-1)[0])
            print(f"{_show(self._expr)} at {_places(values)}: {_decimal(answer)}   (SymPy lambdify, worked out by NumPy "
                  "and SciPy" + ("; an empty value gives an empty answer)" if singles_empty else ")"))
            return answer
        print(f"{_show(self._expr)} at {result.size} values (SymPy lambdify, worked out by NumPy and SciPy).")
        return Numbers(result.ravel())

    @friendly
    def put_in(self, **values) -> Formula:
        """Put a number or another formula in place of a letter, as a new formula. f.put_in(x="y + 1")

        f = sdata.formula("x**2"), then f.put_in(x="y + 1") gives (y + 1)**2. A number gives a formula with one
        letter fewer. As SymPy subs(); MATLAB subs.
        """
        sp = need_sympy("f.put_in()")
        self._values_for("put_in", values, 'put_in(x="y + 1")')
        own = self._symbols()
        swaps = {}
        for k, v in values.items():
            symbol, symbols = self._symbol(k), dict(own)
            kind = kind_of(symbol)
            new = v.strip() if isinstance(v, str) else None
            if kind is not None and new is not None and new.isidentifier() and new not in own:
                symbols[new] = sp.Symbol(new, **LETTER_KINDS[kind])  # put_in(x="y"): y is what x was
            value = parse(v, "put_in()", symbols=symbols)
            if kind is not None and not (value.is_number and value.is_real) and not _fits_kind(value, kind):
                said = new if new is not None else _show(value)
                raise SimplydataError(
                    f"put_in() cannot put {said} in place of {k}: the formula says {k} is {kind_words(kind)} "
                    f"(letters_are=), and SymPy may have used that already ({_kind_example(kind, k)}), so the "
                    f"answer could be wrong when {said} is not {kind_words(kind)}. Put in a real number, one new "
                    f"letter (it takes what {k} is), or an expression SymPy can show is {kind_words(kind)} "
                    f"({_kind_expression_example(kind)}); or write the formula again with the new letters, and give "
                    "them their own letters_are=.")
            swaps[symbol] = value
        _check_one_letter_per_name(self._expr, swaps, values)
        for symbol, value in swaps.items():
            if value.is_number and value.is_real:
                check_value_fits(symbol, float(value), "put_in")
        # SymPy subs puts the values in one after the other, in its order for a dict of letters (by name, with
        # infinities first); each step is sized before SymPy makes it
        order = sorted(swaps, key=sp.default_sort_key)
        endless = (sp.nan, sp.oo, -sp.oo, sp.zoo)
        order = [s for s in order if swaps[s] in endless] + [s for s in order if swaps[s] not in endless]
        new = self._expr
        for symbol in order:
            _check_put_in_digits(sp, new, symbol, swaps[symbol], f"{_show(self._expr)} with {_places(values)}")
            new = _guarded(new.subs, symbol, swaps[symbol], what="SymPy subs")
        print(f"{_show(self._expr)} with {_places(values)}: {_show(new)}   (SymPy subs)")
        return Formula(new)

    @friendly
    def show_as_latex(self) -> str:
        """Show the formula as LaTeX, to paste into a paper; also gives the text back. f.show_as_latex()

        f = sdata.formula("x**3 - 2*x"), then f.show_as_latex() prints x^{3} - 2 x. Nothing is written to a
        file. As SymPy latex(). In Jupyter a formula is shown typeset by itself.
        """
        sp = need_sympy("f.show_as_latex()")
        text = sp.latex(self._expr)
        print(text)
        return text

    @friendly
    def show_as_decimal(self, digits=15) -> str:
        """Show a formula without letters as a decimal with as many digits as you ask; also gives the text back.

        f.show_as_decimal(digits=50)
        f = sdata.formula("sqrt(2)"), then f.show_as_decimal(digits=50) prints
        1.4142135623730950488016887242096980785696718753769. A float keeps only about 16 digits, so the answer is
        text. digits= from 1 to 10,000. Put numbers in place of letters first (f.put_in(x=2)). Nothing changes.
        As SymPy N(expr, digits) (evalf); MATLAB vpa.
        """
        sp = need_sympy("f.show_as_decimal()")
        count = _whole(digits, "digits=", 1, MAX_DECIMAL_DIGITS, "f.show_as_decimal(digits=50)")
        letters = self._letters()
        if letters:
            raise SimplydataError(f"{_show(self._expr)} still has letters ({', '.join(letters)}), so it has no single "
                                  f"decimal. Put numbers in first, for example f.put_in({letters[0]}=2)"
                                  ".show_as_decimal().")
        value = _guarded(sp.N, self._expr, count, what="SymPy N")
        if value.has(sp.zoo, sp.nan, sp.oo, -sp.oo) or value is sp.nan:
            raise SimplydataError(f"{_show(self._expr)} has no value among the ordinary numbers (SymPy gives "
                                  f"{value}).")
        text = str(value)
        print(text)
        if not value.is_real and value.has(sp.I):
            print("(A complex number: the part with I is the imaginary part, I being the square root of -1.)")
        return text

    @friendly
    def as_sympy(self):
        """The SymPy expression underneath, to carry on in SymPy itself. f.as_sympy()

        f = sdata.formula("(x + 2)**2 - 4"), then expr = f.as_sympy() gives the SymPy expression (x + 2)**2 - 4,
        with the same letters (SymPy Symbols, with what letters_are= said they are). Changing it in SymPy does not
        change the formula. A SymPy expression never changes itself, so the two can be used side by side.
        """
        need_sympy("f.as_sympy()")
        print(f"The SymPy expression underneath: {_show(self._expr)}   (a SymPy {type(self._expr).__name__}; carry "
              "on in SymPy with it)")
        return self._expr

    @friendly
    @one_deadline
    def find_limit_as(self, letter=None, goes_to=0, from_side="both"):
        """The value the formula comes close to as a letter goes to a value (the limit). f.find_limit_as("x", goes_to=0)

        f = sdata.formula("sin(x) / x"), then f.find_limit_as("x", goes_to=0) gives 1. goes_to= takes a number,
        "infinity" or "-infinity". At a number the formula must come to the same value from both sides (as in
        school maths; SymPy's own limit() looks from above only); from_side="above" or "below" looks from one side
        only ("right" and "left" work too): for 1/x, f.find_limit_as("x", goes_to=0, from_side="above") gives
        infinity. Gives a number, or a formula when other letters are left. As SymPy limit().
        """
        sp = need_sympy("f.find_limit_as()")
        if letter is None:
            letters = self._letters()
            letter = letters[0] if len(letters) == 1 else None
        x = self._letter("find_limit_as", letter, 'find_limit_as("x", goes_to=0)')
        target = _limit_value(sp, goes_to, "goes_to=")
        key = from_side.strip().lower() if isinstance(from_side, str) else None
        key = FROM_SIDE_SPELLINGS.get(key, key)
        if key not in FROM_SIDES:
            raise choice_error("find_limit_as", "from_side", from_side, list(FROM_SIDES))
        if key != "both" and not target.is_finite:
            raise SimplydataError(f"from_side= is for a number: at {_show(target)} there is only one side to come "
                                  "from, so leave from_side= out.")
        if key != "both":
            side = FROM_SIDES[key]
            found = _guarded(sp.limit, self._expr, x, target, dir=side, what="SymPy limit")
        else:
            side = "+-" if target.is_finite else "+"
            try:
                found = _guarded(sp.limit, self._expr, x, target, dir=side, what="SymPy limit")
                if found.has(sp.zoo) and side == "+-":  # SymPy's "complex infinity": the sides may differ
                    raise ValueError(found)
            except ValueError:
                above = _guarded(sp.limit, self._expr, x, target, dir="+", what="SymPy limit")
                below = _guarded(sp.limit, self._expr, x, target, dir="-", what="SymPy limit")
                if above != below or above.has(sp.zoo):
                    raise SimplydataError(f"{_show(self._expr)} comes to different values from the two sides of {x} "
                                          f"= {_show(target)}: {_show(above)} from above and {_show(below)} from "
                                          "below, so it has no limit "
                                          'there. For one side, use from_side="above" or from_side="below".') from None
                found = above
        if found.has(sp.zoo):
            raise SimplydataError(f"{_show(self._expr)} grows without end as {x} goes to {_show(target)}, but not "
                                  "towards "
                                  "plus or minus infinity (SymPy calls it complex infinity), so it has no limit.")
        if found.has(sp.Limit) or isinstance(found, sp.AccumBounds):
            raise SimplydataError(f"SymPy found no limit of {_show(self._expr)} as {x} goes to {_show(target)} "
                                  f"(it gave {found}).")
        if not target.is_finite:
            how = ")"
        else:
            how = {"+-": ", from both sides)", "+": ", from above)", "-": ", from below)"}[side]
        print(f"As {x} goes to {_show(target)}{' from ' + key if key != 'both' else ''}, {_show(self._expr)} comes "
              "close to "
              f"{_show(found)}   (SymPy limit{how}")
        if found.free_symbols:
            return Formula(found)
        if found == sp.oo:  # SymPy's oo is not "positive" (is_positive is False): compare with oo itself
            return math.inf
        if found == -sp.oo:
            return -math.inf
        return float_of(found) if found.is_real else complex(decimal_of(found))

    @friendly
    def find_taylor_series(self, around=0, up_to_power=4, for_letter=None) -> Formula:
        """The formula as a sum of powers near one value (the Taylor series), as a new formula.

        f.find_taylor_series(around=0, up_to_power=4)
        f = sdata.formula("exp(x)"), then f.find_taylor_series(around=0, up_to_power=4) gives
        x**4/24 + x**3/6 + x**2/2 + x + 1: the powers of (x - around) up to up_to_power=, with the rest left
        out. As SymPy series(...).removeO().
        """
        sp = need_sympy("f.find_taylor_series()")
        x = self._letter("find_taylor_series", for_letter, 'find_taylor_series(around=0, up_to_power=4, '
                                                           'for_letter="x")')
        if isinstance(up_to_power, bool) or not isinstance(up_to_power, (int, np.integer)) or up_to_power < 0:
            raise SimplydataError("up_to_power= needs a whole number, 0 or more, such as up_to_power=4.")
        point = _limit_value(sp, around, "around=")
        if not point.is_finite:
            raise SimplydataError("around= needs a number for a Taylor series.")
        new = _guarded(sp.series, self._expr, x, point, int(up_to_power) + 1, what="SymPy series").removeO()
        print(f"{_show(self._expr)} near {x} = {point}, up to the power {up_to_power}: {_show(new)}   "
              "(SymPy series)")
        return Formula(new)


def _one_number(value) -> bool:
    return isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool)


def _places(values: dict) -> str:
    return ", ".join(f"{k} = {v}" for k, v in values.items())


@friendly
def formula(text=None, letters_are=None) -> Formula:
    """A formula to work with exactly (SymPy): simpler, multiplied out, slopes, areas, limits. sdata.formula("(x + 2)**2 - 4")

    f = sdata.formula("(x + 2)**2 - 4"), then f.turn_into_sum() gives x**2 + 4*x. Write the formula as for
    fit_formula: letters (x, y, rate), numbers, + - * / and ** (^ works too), brackets, pi and the functions exp,
    log, sqrt, abs, sin, cos, tan, erf ... The letters are found by themselves. letters_are={"k": "positive"} says
    what a letter is ("positive", "zero or more", "negative", "real", "whole number", "positive whole number"), so
    SymPy may use it: sqrt(k**2) is then k. Needs the extra simplydata[exact] (SymPy): pip install
    "simplydata[exact]". A formula can be handed to find_where_smallest, find_where_biggest, find_area_under, solve
    and chart.draw_curve. lgamma(x) is the log of the size of gamma(x), as R lgamma and SciPy gammaln (real also
    where gamma is negative). Powers of numbers with more than 1000 digits are refused. In Jupyter a formula is
    shown typeset.
    """
    if text is None:
        raise SimplydataError(f"sdata.formula() needs a formula in quotes.\nFor example:  {FORMULA_EXAMPLE}")
    if letters_are is not None and isinstance(text, Formula):
        raise SimplydataError("letters_are= goes with formula text: sdata.formula(\"sqrt(k**2)\", "
                              'letters_are={"k": "positive"}).')
    symbols = {}
    if letters_are is not None:
        parse(text, "sdata.formula()")  # a text that cannot be read is said first, in parse's own words
        symbols = letter_kind_symbols(letters_are, letters_of(text), "sdata.formula()",
                                      'sdata.formula("sqrt(k**2)", letters_are={"k": "positive"})')
    expr = parse(text, "sdata.formula()", symbols=symbols)
    made = Formula(expr)
    letters = made._letters()
    print(f"The formula {_show(expr)}, with the letter{'s' if len(letters) != 1 else ''} "
          f"{_said_letters(expr.free_symbols) if letters else '(none)'}.")
    return made


# ---------------------------------------------------------------- solve(exactly=True)
def _equation_of(sp, item, known_symbols, symbols):
    """(SymPy relation, its text, sign) of one equation, rule or formula (a formula means formula = 0)."""
    from ._maths_formula import split_equation

    if isinstance(item, Formula):
        named = item._symbols()
        expr = item._expr.subs({named[k]: v for k, v in known_symbols.items() if k in named})
        return sp.Eq(expr, 0), f"{_show(item._expr)} = 0", "="
    if not isinstance(item, str):
        raise SimplydataError('solve(exactly=True) needs equations in quotes, or a formula (meaning formula = 0), '
                              'for example sdata.solve("x**2 = 2", exactly=True).')
    left, sign, right = split_equation(item)
    a = parse(left, "solve()", known_symbols, symbols)
    b = parse(right, "solve()", known_symbols, symbols)
    relation = {"=": sp.Eq, "<": sp.StrictLessThan, ">": sp.StrictGreaterThan, "<=": sp.LessThan,
                ">=": sp.GreaterThan}[sign]
    return relation(a, b), item.strip(), sign


def _letters_to_find(names, for_letter, example):
    if for_letter is None:
        return None
    wanted = [for_letter] if isinstance(for_letter, str) else for_letter
    if not isinstance(wanted, (list, tuple)) or not wanted or not all(isinstance(n, str) for n in wanted):
        raise SimplydataError(f"for_letter= needs a letter in quotes, or a list of them.\nFor example:  {example}")
    unknown = [n for n in wanted if n not in names]
    if unknown:
        raise SimplydataError(f"for_letter= names {', '.join(unknown)}, which "
                              f"{'is' if len(unknown) == 1 else 'are'} not a letter of the equations. Their letters: "
                              f"{', '.join(names) or 'none'}.\nFor example:  {example}")
    return list(dict.fromkeys(wanted))


def _letters_of_items(texts) -> list[str]:
    from ._maths_formula import split_equation

    found: list = []
    for item in texts:
        if isinstance(item, Formula):
            found += [n for n in item._letters() if n not in found]
        elif isinstance(item, str):
            left, _, right = split_equation(item)
            for side in (left, right):
                found += [n for n in letters_of(side, "solve()") if n not in found]
    return found


def exact_number(sp, value):
    """A typed number as an exact SymPy number: the simplest fraction whose decimal is exactly that number (0.2 is
    1/5 and 1e23 is 10**23, as nsimplify writes them), or, when no short fraction gives the number back exactly, its
    exact binary value (4 + 1e-15 stays 4 + 1e-15, never 4)."""
    if isinstance(value, (int, np.integer)) and not isinstance(value, bool):
        return sp.Integer(int(value))
    x = float(value)
    simple = sp.nsimplify(x, rational=True)
    return simple if float(simple) == x else sp.Rational(x)


def _unify_letters(sp, equations, chosen_by_option):
    """Every letter the same SymPy Symbol in every equation: what letters_are= says, else what a formula made with
    letters_are= says, else a plain letter. Two different kinds for one letter are refused."""
    by_name: dict = {}
    for eq in equations:
        for s in eq.free_symbols:
            by_name.setdefault(str(s), set()).add(s)
    chosen = {}
    for name, found in by_name.items():
        kinds = {kind_of(s) for s in found} - {None}
        if name in chosen_by_option:
            wanted = kind_of(chosen_by_option[name])
            if kinds - {wanted}:
                raise SimplydataError(f"{name} is {', '.join(sorted(kinds))} in a formula but {wanted} in letters_are=; "
                                      "say one thing for each letter.")
            chosen[name] = chosen_by_option[name]
        elif len(kinds) > 1:
            raise SimplydataError(f"{name} is {' in one formula and '.join(sorted(kinds))} in another; say one thing "
                                  "for each letter (letters_are=).")
        elif kinds:
            chosen[name] = next(s for s in found if kind_of(s) is not None)
        else:
            chosen[name] = next(iter(found))
    swaps = {s: chosen[str(s)] for eq in equations for s in eq.free_symbols if s is not chosen[str(s)]}
    return [eq.xreplace(swaps) if swaps else eq for eq in equations]


@one_deadline
def solve_exactly(texts: list, known, fast: bool, for_letter=None, letters_are=None):
    """sdata.solve(..., exactly=True): SymPy solve on the equations; a table with one row per solution.

    for_letter= solves for some letters and leaves the others as letters; rules (<, >, <=, >=) go to SymPy solveset
    over the real numbers (or the numbers the letter may be, from letters_are=); a formula means formula = 0;
    letters_are= gives the letters SymPy's assumptions, in every equation and formula alike. All the SymPy calls of
    one solve share one time limit."""
    sp = need_sympy("sdata.solve(exactly=True)")
    from ._maths_formula import _known_values

    values = _known_values(known)
    known_symbols = {k: exact_number(sp, v) for k, v in values.items()}
    symbols = letter_kind_symbols(letters_are, _letters_of_items(texts), "sdata.solve()",
                                  'sdata.solve("c**2 = 4", exactly=True, letters_are={"c": "positive"})')
    equations, shown, signs = [], [], []
    for item in texts:
        eq, said, sign = _equation_of(sp, item, known_symbols, symbols)
        equations.append(eq)
        shown.append(said)
        signs.append(sign)
    equations = _unify_letters(sp, equations, symbols)
    # a typed decimal in a rule is the exact number it stands for (x < 3.5 is x < 7/2), as in the other exact words
    equations = [eq.xreplace({f: exact_number(sp, float(f)) for f in eq.atoms(sp.Float)})
                 if sign != "=" and eq.atoms(sp.Float) else eq for eq, sign in zip(equations, signs)]
    names: list = []
    for eq, said, item in zip(equations, shown, texts):
        if eq in (sp.true, sp.false):
            had = [n for n in _letters_of_items([item]) if n not in known_symbols]
            if not had:
                raise SimplydataError(f'"{said}" is always {"true" if eq == sp.true else "false"}: it has no letter '
                                      "left to find.")
            kinds = [f"{n} is {kind_words(kind_of(symbols[n]))}" for n in had if n in symbols and kind_of(symbols[n])]
            kinds += [f"{s} is {kind_words(kind_of(s))}" for s in (item._expr.free_symbols if isinstance(item, Formula)
                                                                     else ()) if kind_of(s) and str(s) not in symbols]
            when = f" when {' and '.join(kinds)} (letters_are=)" if kinds else ""
            truth = "true" if eq == sp.true else "false"
            raise SimplydataError(f'"{said}" is {truth} for every value of {", ".join(had)}{when}, as SymPy finds, '
                                  "so there is nothing to find.")
        for s in sorted(eq.free_symbols, key=str):
            if str(s) not in names:
                names.append(str(s))
    if not names:
        raise SimplydataError(f'"{shown[0]}" has no letter to find, such as x.')
    example = 'sdata.solve("p*V = n*R*T", for_letter="T", exactly=True)'
    wanted = _letters_to_find(names, for_letter, example)
    if any(sign != "=" for sign in signs):
        if any(sign == "=" for sign in signs):
            raise SimplydataError("solve(exactly=True) takes equations (=) or rules (<, >, <=, >=), not both at "
                                  "once. Solve the equations first, then put the answer into the rules.")
        return _rules_exactly(sp, equations, shown, names, wanted, fast)
    find = wanted or names
    if wanted is None and len(names) > len(equations):
        raise SimplydataError(f"There are more letters to find ({', '.join(names)}) than equations "
                              f"({len(equations)}). Give one equation for each letter, fix some with known=, or say "
                              f"which to find with for_letter= (the others stay letters).\nFor example:  {example}")
    by_name = {str(s): s for eq in equations for s in eq.free_symbols}
    symbols_found = [by_name[n] for n in find]
    found = _guarded(sp.solve, equations, symbols_found, dict=True, what="SymPy solve", hint=EXACTLY_HINT)
    joined = " and ".join(shown)
    if not found:
        print(f"{joined} has no solution SymPy can write down exactly (SymPy solve). Without exactly=True, "
              "sdata.solve looks for decimal solutions.")
        return _result_rows([{**{n: math.nan for n in find}, "method": "SymPy solve (exact)"}], fast)
    rows, said = [], []
    with_letters, any_number = False, set()
    for answer in found:
        row, parts, free = {}, [], []
        for n, s in zip(find, symbols_found):
            if s not in answer:  # SymPy leaves a letter out when every number fits it
                free.append(n)
                any_number.add(n)
                row[n] = math.nan
                row[f"{n} exactly"] = "any number"
                continue
            value = answer[s]
            parts.append(f"{n} = {_show(value)}")
            with_letters = with_letters or bool(value.free_symbols)
            row[n] = math.nan if value.free_symbols else float_of(value, "SymPy N", EXACTLY_HINT)
            row[f"{n} exactly"] = _show(value)
        row["method"] = "SymPy solve (exact)"
        rows.append(row)
        free_words = (f"{' and '.join(free)} can be any number{'s' if len(free) > 1 else ''}; " if free else "")
        said.append(free_words + ", ".join(parts))
    print(f"{joined} when " + " or ".join(said) + "   (SymPy solve, exact)")
    others = [n for n in names if n not in find]
    if with_letters and others:
        print(f"{', '.join(others)} {'stays a letter' if len(others) == 1 else 'stay letters'}, so the decimal "
              "column is empty where the answer has letters; the exact form is in the table.")
    if any_number:
        print(f"There are endless solutions: for each value of {' and '.join(sorted(any_number))} there is one "
              "solution, as written.")
    else:
        print(_completeness(sp, equations, symbols_found, len(found)))
    if not with_letters and not any_number and any(any(math.isnan(r[n]) for n in find) for r in rows):
        print("A solution that is not an ordinary (real) number has an empty decimal; its exact form is in the "
              "table.")
    return _result_rows(rows, fast)


def _result_rows(rows, fast):
    from .finding import _result

    return _result(rows, fast)


def _interval_words(sp, piece, x) -> str:
    """One piece of the answer of a rule, in words: x < -2, 1 <= x < 3, x = 0."""
    if isinstance(piece, sp.FiniteSet):
        return " or ".join(f"{x} = {_show(v)}" for v in piece)
    low, high = piece.start, piece.end
    left = "<" if piece.left_open else "<="
    right = "<" if piece.right_open else "<="
    if low == -sp.oo and high == sp.oo:
        return f"{x} is any real number"
    if low == -sp.oo:
        return f"{x} {right} {_show(high)}"
    if high == sp.oo:
        return f"{x} {'>' if piece.left_open else '>='} {_show(low)}"
    return f"{_show(low)} {left} {x} {right} {_show(high)}"


def _decimal_end(sp, value) -> float:
    if value == sp.oo:
        return math.inf
    if value == -sp.oo:
        return -math.inf
    return float_of(value, "SymPy N", EXACTLY_HINT)


def _rules_exactly(sp, rules, shown, names, wanted, fast):
    """Rules (<, >, <=, >=) in one letter: SymPy solveset over the real numbers the letter may be (from letters_are=;
    reduce_inequalities for several rules, then kept to those numbers)."""
    if len(names) != 1 or (wanted is not None and wanted != names):
        raise SimplydataError(f"solve(exactly=True) solves rules (<, >, <=, >=) in one letter; these have "
                              f"{len(names)} ({', '.join(names)}). Fix the others with known=.")
    x = next(s for r in rules for s in r.free_symbols if str(s) == names[0])
    kind = kind_of(x)
    whole_numbers = kind in ("whole number", "positive whole number")
    domain = sp.Interval.open(0, sp.oo) if kind == "positive whole number" else (
        sp.S.Reals if whole_numbers else kind_domain(sp, x))
    where = _domain_words(sp, domain)
    plain, repeating = [], []
    for rule, said in zip(rules, shown):
        period = _guarded(sp.periodicity, rule.lhs - rule.rhs, x, what="SymPy periodicity", hint=EXACTLY_HINT)
        (repeating if period is not None and period != 0 else plain).append((rule, said, period))
    if len(rules) == 1 and plain:
        whole = _guarded(sp.solveset, rules[0], x, domain, what="SymPy solveset", hint=EXACTLY_HINT)
        how = f"SymPy solveset over {where}"
    elif plain:
        try:
            reduced = _guarded(sp.reduce_inequalities, [r for r, _, _ in plain], x,
                               what="SymPy reduce_inequalities", hint=EXACTLY_HINT)
        except NotImplementedError:  # SymPy's own error, from the helper: x**x > 2 with other rules
            raise SimplydataError(f"SymPy could not solve {' and '.join(shown)} exactly (SymPy reduce_inequalities "
                                  "cannot do rules of this kind together).") from None
        whole =sp.S.Reals if reduced == sp.true else sp.S.EmptySet if reduced == sp.false else reduced.as_set()
        whole = _guarded(sp.Intersection, whole, domain, what="SymPy Intersection", hint=EXACTLY_HINT)
        how = f"SymPy reduce_inequalities over {where}"
    else:
        whole = domain
        how = f"SymPy solveset over {where}"
    for rule, said, period in repeating:
        whole = _keep_repeating(sp, rule, said, period, x, whole)
    if isinstance(whole, sp.ConditionSet):
        raise SimplydataError(f"SymPy could not solve {' and '.join(shown)} exactly ({whole}).")
    pieces = list(whole.args) if isinstance(whole, sp.Union) else ([] if whole == sp.S.EmptySet else [whole])
    if any(not isinstance(p, (sp.Interval, sp.FiniteSet)) for p in pieces):
        raise SimplydataError(f"SymPy gave the answer to {' and '.join(shown)} as {whole}, which simplydata cannot "
                              "write as ranges.")
    rows, said = [], []
    for piece in pieces:
        said.append(_interval_words(sp, piece, x))
        if isinstance(piece, sp.FiniteSet):
            ends = [(v, v, True, True) for v in piece]
        else:
            ends = [(piece.start, piece.end, not piece.left_open, not piece.right_open)]
        for low, high, low_in, high_in in ends:
            rows.append({"from": _decimal_end(sp, low), "to": _decimal_end(sp, high), "includes from": bool(low_in),
                         "includes to": bool(high_in), "from exactly": _show(low), "to exactly": _show(high),
                         "method": f"{how} (exact)"})
    joined = " and ".join(shown)
    if not rows:
        print(f"{joined} is never true for {x} among {where}   ({how})")
        return _result_rows([{"from": math.nan, "to": math.nan, "includes from": False, "includes to": False,
                              "from exactly": "", "to exactly": "", "method": f"{how} (exact)"}], fast)
    print(f"{joined} when " + " or ".join(said) + f"   ({how})")
    if whole_numbers:
        print(f"{x} is a {kind} (letters_are=), so only the {kind}s in these ranges count.")
    return _result_rows(rows, fast)


MAX_PERIODS = 1000  # a repeating rule is put together from at most this many periods


def _keep_repeating(sp, rule, said, period, x, whole):
    """The part of whole where a repeating rule (sin(x) > 0, repeating every period) holds.

    SymPy solveset gives the answer of such a rule over the real numbers for one period only, 0 <= x < period (or
    every number, or none, when the rule always or never holds). That one period is moved along by whole periods
    (SymPy imageset) over the range the other rules leave, which must be of finite length, and kept to that range
    (SymPy Intersection). Over an endless range only "always" and "never" can be given; anything else is refused."""
    if isinstance(whole, sp.ConditionSet):  # SymPy could not solve the rules before: the caller says so
        return whole
    once = _guarded(sp.solveset, rule, x, sp.S.Reals, what="SymPy solveset", hint=EXACTLY_HINT)
    if once == sp.S.EmptySet or whole == sp.S.EmptySet or isinstance(once, sp.ConditionSet):
        return once if whole != sp.S.EmptySet else whole
    one_period = sp.Interval(0, period, False, True)
    if once == sp.S.Reals or _guarded(one_period.is_subset, once, what="SymPy is_subset", hint=EXACTLY_HINT):
        return whole  # true for every number
    if whole.inf.is_finite and whole.sup.is_finite:
        first = int(_guarded(sp.floor, whole.inf / period, what="SymPy floor", hint=EXACTLY_HINT))
        last = int(_guarded(sp.ceiling, whole.sup / period, what="SymPy ceiling", hint=EXACTLY_HINT))
        if last - first <= MAX_PERIODS:
            moved = [_guarded(sp.imageset, sp.Lambda(x, x + n * period), once, what="SymPy imageset",
                              hint=EXACTLY_HINT) for n in range(first, last + 1)]
            return _guarded(sp.Intersection, sp.Union(*moved), whole, what="SymPy Intersection", hint=EXACTLY_HINT)
        raise SimplydataError(f'"{said}" repeats every {_show(period)} in {x}, and the range the other rules leave '
                              f"covers {last - first:,} repeats, more than the {MAX_PERIODS:,} simplydata puts "
                              "together. Use a shorter range, or solve where the two sides are equal instead (with = "
                              "and exactly=True, which gives the whole repeating set) and read the ranges between "
                              "those points.")
    raise SimplydataError(f'"{said}" repeats every {_show(period)} in {x}, and SymPy solveset gives the ranges of one '
                          "period only, so its answer would leave out the others. Solve where the two sides are equal "
                          "instead (with = and exactly=True, which gives the whole repeating set), and read the ranges "
                          "between those points, or keep the letter to a range of finite length with more rules (such "
                          'as "x > 0" and "x < 10").')


def _completeness(sp, equations, symbols, listed: int) -> str:
    """Whether the solutions listed are all of them: SymPy solveset gives the whole set for one equation in one
    letter (an endless, repeating set for sin(x) = 0); for several equations, a polynomial system is complete."""
    if len(equations) == 1 and len(symbols) == 1:
        whole = _guarded(sp.solveset, equations[0], symbols[0], what="SymPy solveset", hint=EXACTLY_HINT)
        if isinstance(whole, sp.FiniteSet):  # solveset leaves out what letters_are= says; keep what fits
            facts = [f for f, v in symbols[0].assumptions0.items() if v is True and f in
                     ("positive", "nonnegative", "negative", "integer", "real")]
            whole = sp.FiniteSet(*[v for v in whole if all(getattr(v, f"is_{f}") is not False for f in facts)])
        if isinstance(whole, sp.FiniteSet) and len(whole) == listed:
            return "These are all the solutions (SymPy solveset gives the same set)."
        if isinstance(whole, sp.ConditionSet):
            return "SymPy found these solutions; there may be more that it cannot write down."
        if whole.free_symbols - set(symbols):
            return "SymPy found these solutions; some hold only for some values of the other letters."
        return (f"SymPy found these solutions; there are more. The whole set (SymPy solveset) is {whole}"
                + (", which repeats without end." if whole.has(sp.ImageSet) else "."))
    if all(eq.lhs.is_polynomial(*symbols) and eq.rhs.is_polynomial(*symbols) for eq in equations):
        return "These are all the solutions (the equations are polynomials, which SymPy solves completely)."
    return "SymPy found these solutions; there may be more."


# ---------------------------------------------------------------- show_as_fraction (numbers and grids)
def fraction_text(value) -> str:
    """One number as SymPy's simplest fraction that gives it back (nsimplify(rational=True)); empty stays empty."""
    sp = need_sympy("show_as_fraction()")
    x = float(value)
    if math.isnan(x):
        return "empty"
    if math.isinf(x):
        return "infinity" if x > 0 else "-infinity"
    return str(sp.nsimplify(x, rational=True))


# ---------------------------------------------------------------- exact grids (numbers phase, batch 4)
MAX_EXACT_GRID = 12  # rows and columns of a grid for exact determinant, inverse and null space
MAX_EXACT_EIGEN = 6  # rows of a grid for exact eigenvalues (roots of a polynomial of that degree)


def exact_matrix(values, step: str, most: int):
    """A grid of numbers as a SymPy Matrix of exact numbers: each the simplest fraction whose decimal is exactly that
    number (0.2 is 1/5), else its exact binary value (4 + 1e-15 is not rounded to 4); see exact_number."""
    sp = need_sympy(f"grid.{step}(exactly=True)")
    rows, columns = values.shape
    if max(rows, columns) > most:
        raise SimplydataError(f"{step}(exactly=True) works on grids of up to {most} rows and {most} columns; this one "
                              f"is {rows} x {columns}. Leave out exactly=True for the decimal answer.")
    if not np.isfinite(values).all():
        raise SimplydataError(f"{step}(exactly=True) needs a number in every cell (no empty or infinite ones).")
    return sp.Matrix([[exact_number(sp, v) for v in row] for row in values])


def run_exactly(call, *values, what: str):
    """A SymPy call on a grid, under the same time limit as the formula words."""
    return _guarded(call, *values, what=what, hint=EXACTLY_HINT)
