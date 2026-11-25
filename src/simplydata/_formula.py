"""Exact maths with SymPy: sdata.formula("(x + 2)**2 - 4") and its words, solve(exactly=True) and show_as_fraction.

SymPy is the optional extra simplydata[exact] (pip install "simplydata[exact]"); without it these words stop with a
plain sentence that says how to install it. Every answer comes from SymPy:

* the formula text is checked with Python's ast first (numbers, letters, + - * / ** ^, brackets and the functions of
  fit_formula only; never run), then read by SymPy's parse_expr with every letter given as a SymPy Symbol, so that
  letters such as E, I, N, S or beta stay letters and never become SymPy's own constants or functions;
* make_simpler: simplify; turn_into_sum: expand; turn_into_product: factor;
* find_slope_formula: diff; find_area_formula: integrate; find_value_at: subs + evalf (one value) or lambdify with
  NumPy and SciPy (many values); put_in: subs; show_as_latex: latex; find_limit_as: limit; find_taylor_series:
  series; solve(exactly=True): solve; nums.show_as_fraction: nsimplify(rational=True).

Own code is glue only: checking the text, naming the letters, and writing SymPy's answer back as formula text that
the other simplydata words read (abs, lgamma, besselJ(x, nu) and sinc as fit_formula writes them).
"""

from __future__ import annotations

import ast
import math

import numpy as np

from ._errors import MissingWordError, SimplydataError, friendly, suggest

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
         "find_value_at", "put_in", "show_as_latex", "find_limit_as", "find_taylor_series", "undo")
# names from SymPy, MATLAB and R -> the formula word (they never run)
HINTS = {"simplify": "make_simpler()", "expand": "turn_into_sum() (multiplied out)",
         "factor": "turn_into_product()", "factorise": "turn_into_product()", "factorize": "turn_into_product()",
         "diff": 'find_slope_formula(for_letter="x")', "derivative": "find_slope_formula()",
         "Derivative": "find_slope_formula()", "deriv": "find_slope_formula()", "D": "find_slope_formula()",
         "integrate": "find_area_formula() (sdata.find_area_under for a number)",
         "Integral": "find_area_formula()", "int": "find_area_formula()",
         "subs": 'put_in(x="y + 1") (find_value_at(x=2) for a number)', "substitute": 'put_in(x="y + 1")',
         "evalf": "find_value_at(x=2)", "N": "find_value_at(x=2)", "lambdify": "find_value_at(x=numbers)",
         "matlabFunction": "find_value_at(x=numbers)", "latex": "show_as_latex()",
         "limit": 'find_limit_as("x", goes_to=0)', "series": "find_taylor_series(around=0, up_to_power=4)",
         "taylor": "find_taylor_series(around=0, up_to_power=4)"}


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
        if name != "pi" and name not in letters:
            letters.append(name)
        return
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        return _check_node(node.operand, text, letters, functions)
    if isinstance(node, ast.BinOp):
        if not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.BitXor)):
            raise _formula_error(f'The sign in "{ast.get_source_segment(text, node)}" is not allowed in a formula.')
        _check_node(node.left, text, letters, functions)
        return _check_node(node.right, text, letters, functions)
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


def parse(text, what: str = "sdata.formula()", letters_known=None):
    """Formula text (or a formula) -> a SymPy expression. The text is checked with ast before SymPy reads it."""
    sp = need_sympy(what)
    if isinstance(text, Formula):
        return text._expr
    if isinstance(text, bool) or not isinstance(text, (str, int, float, np.integer, np.floating)):
        raise _formula_error(f"{what} needs the formula as text in quotes (or a number); it got {text!r}.")
    if not isinstance(text, str):
        if isinstance(text, (int, np.integer)):
            return sp.Integer(int(text))
        return sp.nsimplify(float(text), rational=True) if math.isfinite(float(text)) else sp.Float(float(text))
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
    local = {name: known.get(name, sp.Symbol(name)) for name in letters}
    named = _sympy_functions(sp)
    for name in functions:
        local[name] = named[SPELLINGS.get(name, name)]
    local["pi"] = sp.pi
    safe = {"Integer": sp.Integer, "Float": sp.Float, "Rational": sp.Rational, "Symbol": sp.Symbol,
            "__builtins__": {}}
    return parse_expr(text.strip(), local_dict=local, global_dict=safe,
                      transformations=standard_transformations + (convert_xor,))


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
    """How an answer is printed: SymPy's own text (sqrt(2), pi, x**2 + 4*x)."""
    return str(expr)


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
    return sp.nsimplify(value, rational=True) if not float(value).is_integer() else sp.Integer(int(value))


# ---------------------------------------------------------------- the formula object
class Formula:
    """A formula that SymPy works with exactly. Make one with sdata.formula("(x + 2)**2 - 4").

    Words: make_simpler, turn_into_sum, turn_into_product, find_slope_formula, find_area_formula, find_value_at,
    put_in, show_as_latex, find_limit_as, find_taylor_series, undo.
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
            lines.append(f"In simplydata this is f.{HINTS[name]}.")
        else:
            guesses = suggest(name, list(WORDS))
            if guesses:
                lines.append("Did you mean " + " or ".join(f".{g}()" for g in guesses) + "?")
        lines.append("Every word for a formula: " + ", ".join(WORDS))
        raise MissingWordError("\n".join(lines))

    def __repr__(self):
        letters = self._letters()
        said = ", ".join(letters) if letters else "none"
        return f"simplydata formula: {_show(self._expr)}   (letters: {said})"

    def __str__(self):
        return _show(self._expr)

    def _formula_text(self) -> str:
        """The formula as text for the other simplydata words (find_where_smallest, find_area_under ...)."""
        return formula_text(self._expr)

    # ---------------------------------------------------------------- helpers
    def _letters(self) -> list[str]:
        return sorted(str(s) for s in self._expr.free_symbols)

    def _letter(self, step: str, for_letter, example: str):
        """The letter to work with: for_letter=, or the only letter of the formula."""
        sp = need_sympy(f"f.{step}()")
        letters = self._letters()
        if for_letter is None:
            if len(letters) == 1:
                return sp.Symbol(letters[0])
            if not letters:
                raise SimplydataError(f"{_show(self._expr)} has no letter, so .{step}() has nothing to work with.")
            raise SimplydataError(f"{_show(self._expr)} has {len(letters)} letters ({', '.join(letters)}): say which "
                                  f"one with for_letter=.\nFor example:  f.{example}")
        if not isinstance(for_letter, str) or for_letter not in letters:
            raise SimplydataError(f"for_letter= needs one of the letters of the formula in quotes: "
                                  f"{', '.join(repr(n) for n in letters) or 'none'}.\nFor example:  f.{example}")
        return sp.Symbol(for_letter)

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
        new = sp.simplify(self._expr)
        print(f"{_show(self._expr)} written more simply: {_show(new)}   (SymPy simplify)")
        return self._change("make simpler", new)

    @friendly
    def turn_into_sum(self):
        """Multiply out the brackets, so the formula is a sum of terms (SymPy expand). f.turn_into_sum()

        f = sdata.formula("(x + 2)**2 - 4"), then f.turn_into_sum() gives x**2 + 4*x. The formula changes;
        f.undo() takes the step back. turn_into_product() goes the other way. As SymPy expand().
        """
        sp = need_sympy("f.turn_into_sum()")
        new = sp.expand(self._expr)
        print(f"{_show(self._expr)} multiplied out: {_show(new)}   (SymPy expand)")
        return self._change("turn into sum", new)

    @friendly
    def turn_into_product(self):
        """Write the formula as a product of factors (SymPy factor). f.turn_into_product()

        f = sdata.formula("x**2 + 4*x"), then f.turn_into_product() gives x*(x + 4). The formula changes;
        f.undo() takes the step back. turn_into_sum() goes the other way. As SymPy factor().
        """
        sp = need_sympy("f.turn_into_product()")
        new = sp.factor(self._expr)
        print(f"{_show(self._expr)} as a product: {_show(new)}   (SymPy factor)")
        return self._change("turn into product", new)

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
    def find_slope_formula(self, for_letter=None) -> Formula:
        """The formula of the slope (the derivative), as a new formula. f.find_slope_formula()

        f = sdata.formula("x**3 - 2*x"), then f.find_slope_formula() gives 3*x**2 - 2. for_letter= says which
        letter when there are several. As SymPy diff(); MATLAB diff; R D().
        """
        sp = need_sympy("f.find_slope_formula()")
        x = self._letter("find_slope_formula", for_letter, 'find_slope_formula(for_letter="x")')
        new = sp.diff(self._expr, x)
        print(f"The slope of {_show(self._expr)} as {x} changes: {_show(new)}   (the derivative; SymPy diff)")
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
        new = sp.integrate(self._expr, x)
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
        how_many=50)). One value: SymPy subs and evalf; many: SymPy lambdify with NumPy and SciPy.
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
        if not many:
            found = self._expr.subs({sp.Symbol(k): parse(v, "find_value_at()") for k, v in values.items()}).evalf()
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
        function = sp.lambdify([sp.Symbol(n) for n in letters], self._expr, modules=["scipy", "numpy"])
        with np.errstate(all="ignore"):
            out = np.asarray(function(*arrays), dtype=complex)
        shape = np.broadcast_shapes(*[np.shape(a) for a in arrays])
        out = np.broadcast_to(out, shape)
        if np.any(np.abs(out.imag) > 1e-12 * np.maximum(1.0, np.abs(out.real))):
            raise SimplydataError("For some of these values the formula has no value among the ordinary numbers "
                                  "(a square root or log of a negative number).")
        result = np.array(out.real, dtype=float)
        print(f"{_show(self._expr)} at {result.size} values (SymPy lambdify, worked out by NumPy and SciPy).")
        return Numbers(result.ravel())

    @friendly
    def put_in(self, **values) -> Formula:
        """Put a number or another formula in place of a letter, as a new formula. f.put_in(x="y + 1")

        f = sdata.formula("x**2"), then f.put_in(x="y + 1") gives (y + 1)**2. A number gives a formula with one
        letter fewer. As SymPy subs(); MATLAB subs.
        """
        need_sympy("f.put_in()")
        self._values_for("put_in", values, 'put_in(x="y + 1")')
        import sympy as sp

        swaps = {sp.Symbol(k): parse(v, "put_in()") for k, v in values.items()}
        new = self._expr.subs(swaps)
        print(f"{_show(self._expr)} with {_places(values)}: {_show(new)}   (SymPy subs)")
        return Formula(new)

    @friendly
    def show_as_latex(self) -> str:
        """Show the formula as LaTeX, to paste into a paper; also gives the text back. f.show_as_latex()

        f = sdata.formula("x**3 - 2*x"), then f.show_as_latex() prints x^{3} - 2 x. Nothing is written to a
        file. As SymPy latex().
        """
        sp = need_sympy("f.show_as_latex()")
        text = sp.latex(self._expr)
        print(text)
        return text

    @friendly
    def find_limit_as(self, letter=None, goes_to=0):
        """The value the formula comes close to as a letter goes to a value (the limit). f.find_limit_as("x", goes_to=0)

        f = sdata.formula("sin(x) / x"), then f.find_limit_as("x", goes_to=0) gives 1. goes_to= takes a number,
        "infinity" or "-infinity". At a number the formula must come to the same value from both sides (as in
        school maths; SymPy's own limit() looks from above only). Gives a number, or a formula when other letters
        are left. As SymPy limit().
        """
        sp = need_sympy("f.find_limit_as()")
        if letter is None:
            letters = self._letters()
            letter = letters[0] if len(letters) == 1 else None
        x = self._letter("find_limit_as", letter, 'find_limit_as("x", goes_to=0)')
        target = _limit_value(sp, goes_to, "goes_to=")
        side = "+-" if target.is_finite else "+"
        try:
            found = sp.limit(self._expr, x, target, dir=side)
            if found.has(sp.zoo):  # SymPy's "complex infinity": the two sides go to different infinities
                raise ValueError(found)
        except ValueError:
            above = sp.limit(self._expr, x, target, dir="+")
            below = sp.limit(self._expr, x, target, dir="-")
            raise SimplydataError(f"{_show(self._expr)} comes to different values from the two sides of {x} = "
                                  f"{target}: {above} from above and {below} from below, so it has no limit "
                                  "there.") from None
        if found.has(sp.Limit) or isinstance(found, sp.AccumBounds):
            raise SimplydataError(f"SymPy found no limit of {_show(self._expr)} as {x} goes to {target} "
                                  f"(it gave {found}).")
        print(f"As {x} goes to {target}, {_show(self._expr)} comes close to {_show(found)}   (SymPy limit"
              + (", from both sides)" if side == "+-" else ")"))
        if found.free_symbols:
            return Formula(found)
        if found.is_infinite:
            return math.inf if found.is_positive else -math.inf
        return float(found) if found.is_real else complex(found)

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
        new = sp.series(self._expr, x, point, n=int(up_to_power) + 1).removeO()
        print(f"{_show(self._expr)} near {x} = {point}, up to the power {up_to_power}: {_show(new)}   "
              "(SymPy series)")
        return Formula(new)


def _one_number(value) -> bool:
    return isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool)


def _places(values: dict) -> str:
    return ", ".join(f"{k} = {v}" for k, v in values.items())


@friendly
def formula(text=None) -> Formula:
    """A formula to work with exactly (SymPy): simpler, multiplied out, slopes, areas, limits. sdata.formula("(x + 2)**2 - 4")

    f = sdata.formula("(x + 2)**2 - 4"), then f.turn_into_sum() gives x**2 + 4*x. Write the formula as for
    fit_formula: letters (x, y, rate), numbers, + - * / and ** (^ works too), brackets, pi and the functions exp,
    log, sqrt, abs, sin, cos, tan, erf ... The letters are found by themselves. Needs the extra
    simplydata[exact] (SymPy): pip install "simplydata[exact]". A formula can be handed to find_where_smallest,
    find_where_biggest and find_area_under.
    """
    if text is None:
        raise SimplydataError(f"sdata.formula() needs a formula in quotes.\nFor example:  {FORMULA_EXAMPLE}")
    expr = parse(text, "sdata.formula()")
    made = Formula(expr)
    letters = made._letters()
    print(f"The formula {_show(expr)}, with the letter{'s' if len(letters) != 1 else ''} "
          f"{', '.join(letters) if letters else '(none)'}.")
    return made


# ---------------------------------------------------------------- solve(exactly=True)
def solve_exactly(texts: list, known, fast: bool):
    """sdata.solve(..., exactly=True): SymPy solve on the equations; a table with one row per solution."""
    sp = need_sympy("sdata.solve(exactly=True)")
    from ._maths_formula import _known_values, split_equation
    from .finding import _result

    values = _known_values(known)
    known_symbols = {k: sp.nsimplify(v, rational=True) for k, v in values.items()}
    equations, names = [], []
    for text in texts:
        if not isinstance(text, str):
            raise SimplydataError('solve(exactly=True) needs equations in quotes, for example '
                                  'sdata.solve("x**2 = 2", exactly=True).')
        left, sign, right = split_equation(text)
        if sign != "=":
            raise SimplydataError(f'solve() works with = only; "{text}" is a rule.')
        eq = sp.Eq(parse(left, "solve()", known_symbols), parse(right, "solve()", known_symbols))
        equations.append(eq)
        for s in sorted(eq.free_symbols, key=str):
            if str(s) not in names:
                names.append(str(s))
    if not names:
        raise SimplydataError(f'"{texts[0]}" has no letter to find, such as x.')
    if len(names) > len(equations):
        raise SimplydataError(f"There are more letters to find ({', '.join(names)}) than equations "
                              f"({len(equations)}). Give one equation for each letter, or fix some with known=.")
    symbols = [sp.Symbol(n) for n in names]
    found = sp.solve(equations, symbols, dict=True)
    shown = " and ".join(texts)
    if not found:
        print(f"{shown} has no solution SymPy can write down exactly (SymPy solve). Without exactly=True, "
              "sdata.solve looks for decimal solutions.")
        return _result([{**{n: math.nan for n in names}, "method": "SymPy solve (exact)"}], fast)
    rows, said = [], []
    for answer in found:
        row, parts = {}, []
        for n, s in zip(names, symbols):
            value = answer.get(s, s)
            parts.append(f"{n} = {_show(value)}")
            number = complex(sp.N(value)) if not value.free_symbols else complex(math.nan)
            row[n] = number.real if abs(number.imag) <= 1e-12 * max(1.0, abs(number.real)) else math.nan
            row[f"{n} exactly"] = _show(value)
        row["method"] = "SymPy solve (exact)"
        rows.append(row)
        said.append(", ".join(parts))
    print(f"{shown} when " + " or ".join(said) + "   (SymPy solve, exact)")
    if any(any(math.isnan(r[n]) for n in names) for r in rows):
        print("A solution that is not an ordinary (real) number has an empty decimal; its exact form is in the "
              "table.")
    return _result(rows, fast)


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
