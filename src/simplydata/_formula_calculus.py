"""Calculus checks, series, transforms and code on a formula (families for 100 %, batches 24-26, plan section 2.10,
approved by Manish 2026-11-28, G15): formula.take_transform("laplace"), find_area_along_path, check_if_always,
find_turning_points, find_where_undefined, find_period, find_fourier_series, find_residue_at, list_terms,
find_hessian, find_wronskian, show_as_code("r") and show_as_tree.

Every answer comes from SymPy, each call under simplydata's one time limit (_time_limit.py), with the SymPy function
named in what is printed:

* take_transform: laplace_transform, fourier_transform, mellin_transform, sine_transform, cosine_transform,
  hankel_transform and their inverses (noconds=True: the transform itself, without SymPy's conditions);
* find_area_along_path: line_integrate along SymPy's Curve; check_if_always: is_increasing, is_decreasing,
  is_strictly_increasing, is_strictly_decreasing, is_monotonic, is_convex; find_turning_points: stationary_points;
  find_where_undefined: singularities; find_period: periodicity;
* find_fourier_series: fourier_series, then truncate; find_residue_at: residue; list_terms: sequence;
* find_hessian: hessian (an exact grid); find_wronskian: wronskian (casoratian with whole_numbers_only=True);
* show_as_code: SymPy's code printers (ccode, rcode, julia_code, mathml ...); show_as_tree: SymPy's tree printer
  (dotprint for Graphviz).

Own code is glue only: reading the options, naming the letters, and writing SymPy's answers back as formulas,
numbers and tables. The words are on the formula (Formula takes them from _CalculusWords).
"""

from __future__ import annotations

import math
import re

from ._errors import friendly
from ._time_limit import one_deadline

# ------------------------------------------------------------------------------------------------ take_transform
# plain name -> (SymPy function, letter it comes from, letter it goes to, what it is)
TRANSFORMS = {
    "laplace": ("laplace_transform", "t", "s", "the integral of f(t)*exp(-s*t) from 0 to infinity"),
    "inverse laplace": ("inverse_laplace_transform", "s", "t", "the f(t) whose Laplace transform is the formula"),
    "fourier": ("fourier_transform", "x", "k", "the integral of f(x)*exp(-2*pi*I*x*k) over all x (SymPy's "
                "convention, with 2*pi in the power)"),
    "inverse fourier": ("inverse_fourier_transform", "k", "x", "the integral of F(k)*exp(2*pi*I*x*k) over all k"),
    "mellin": ("mellin_transform", "x", "s", "the integral of x**(s - 1)*f(x) from 0 to infinity"),
    "inverse mellin": ("inverse_mellin_transform", "s", "x", "the f(x) whose Mellin transform is the formula, in the "
                       "strip of s given with between="),
    "sine": ("sine_transform", "x", "k", "sqrt(2/pi) times the integral of f(x)*sin(k*x) from 0 to infinity"),
    "inverse sine": ("inverse_sine_transform", "k", "x", "the sine transform back (it is its own inverse)"),
    "cosine": ("cosine_transform", "x", "k", "sqrt(2/pi) times the integral of f(x)*cos(k*x) from 0 to infinity"),
    "inverse cosine": ("inverse_cosine_transform", "k", "x", "the cosine transform back (it is its own inverse)"),
    "hankel": ("hankel_transform", "r", "k", "the integral of f(r)*besselj(order, k*r)*r from 0 to infinity"),
    "inverse hankel": ("inverse_hankel_transform", "k", "r", "the Hankel transform back (it is its own inverse)"),
}
TRANSFORM_SPELLINGS = {}
for _key, (_function, *_rest) in TRANSFORMS.items():
    _class = "".join(part.capitalize() for part in _function.split("_"))  # LaplaceTransform ...
    TRANSFORM_SPELLINGS.update({_function: _key, _function.replace("_", " "): _key, _class.lower(): _key,
                                f"{_key} transform": _key})
TRANSFORM_SPELLINGS.update({"inverse_laplace": "inverse laplace", "inverse_fourier": "inverse fourier",
                            "fourier sine": "sine", "fourier cosine": "cosine"})
del _key, _function, _rest, _class

# ------------------------------------------------------------------------------------------------ check_if_always
# plain kind -> (SymPy function, what it means)
ALWAYS = {
    "rising": ("is_increasing", "never goes down (it may stay level for a while)"),
    "falling": ("is_decreasing", "never goes up (it may stay level for a while)"),
    "strictly rising": ("is_strictly_increasing", "always goes up"),
    "strictly falling": ("is_strictly_decreasing", "always goes down"),
    "one way only": ("is_monotonic", "always goes up, or always goes down (strictly monotonic)"),
    "bending up": ("is_convex", "bends upwards everywhere (convex: a straight line between two points lies on or "
                   "above it)"),
}
ALWAYS_SPELLINGS = {"increasing": "rising", "is_increasing": "rising", "decreasing": "falling",
                    "is_decreasing": "falling", "strictly increasing": "strictly rising",
                    "is_strictly_increasing": "strictly rising", "strictly decreasing": "strictly falling",
                    "is_strictly_decreasing": "strictly falling", "monotonic": "one way only",
                    "is_monotonic": "one way only", "convex": "bending up", "is_convex": "bending up",
                    "going up": "rising", "going down": "falling"}

# ------------------------------------------------------------------------------------------------ show_as_code
# plain language -> (SymPy printer, what it writes)
LANGUAGES = {
    "c": ("ccode", "C (C99)"), "c++": ("cxxcode", "C++"), "fortran": ("fcode", "Fortran"),
    "glsl": ("glsl_code", "OpenGL Shading Language (GLSL)"), "javascript": ("jscode", "JavaScript"),
    "julia": ("julia_code", "Julia"), "maple": ("maple_code", "Maple"),
    "mathematica": ("mathematica_code", "Mathematica (Wolfram Language)"), "mathml": ("mathml", "MathML (content)"),
    "octave": ("octave_code", "Octave and MATLAB"), "python": ("pycode", "Python with its math module"),
    "r": ("rcode", "R"), "rust": ("rust_code", "Rust"), "smt-lib": ("smtlib_code", "SMT-LIB (for SMT solvers)"),
    "sympy": ("python", "SymPy code that makes the formula again"), "text": ("sstr", "plain text, as SymPy writes it"),
    "sympy tree": ("srepr", "SymPy's full form, every part named (srepr)"),
}
LANGUAGE_SPELLINGS = {"cpp": "c++", "cxx": "c++", "matlab": "octave", "js": "javascript", "smtlib": "smt-lib",
                      "smt": "smt-lib", "wolfram": "mathematica", "srepr": "sympy tree", "repr": "sympy tree",
                      "str": "text", "string": "text", "py": "python", "f90": "fortran", "f95": "fortran"}
for _language, (_printer, _) in LANGUAGES.items():
    if _printer not in LANGUAGES:  # "python" is a language here, and the name of the printer of "sympy"
        LANGUAGE_SPELLINGS.setdefault(_printer, _language)
del _language, _printer

MAX_TERMS = 10_000  # list_terms: at most this many terms
MAX_FOURIER_TERMS = 100  # find_fourier_series(how_many_terms=)
_PATH_PART = re.compile(r"^\s*([A-Za-z]\w*)\s*=\s*(.+?)\s*$", re.S)


def _value(table: dict, spellings: dict, value, step: str, option: str):
    from ._formula_algebra import _value as checked

    return checked(table, spellings, value, step, option)


def _end_value(sp, value, what: str):
    """An end of a range: a number, "infinity" or "-infinity", or a formula without letters ("pi", "2*pi")."""
    from ._errors import SimplydataError
    from ._formula import INFINITY, MINUS_INFINITY, _limit_value, parse

    if isinstance(value, str) and value.strip().lower() not in INFINITY + MINUS_INFINITY:
        found = parse(value, what)
        if found.free_symbols:
            raise SimplydataError(f'{what} takes numbers, "infinity", or a formula of numbers such as "2*pi"; '
                                  f'"{value}" has letters.')
        return found
    return _limit_value(sp, value, what)


def _range(sp, between, what: str, example: str, default=None):
    """between=[low, high] as SymPy numbers (low below high), or the default when between= is left out."""
    from ._errors import SimplydataError

    if between is None:
        return default
    if isinstance(between, (str, bytes)) or not isinstance(between, (list, tuple)) or len(between) != 2:
        raise SimplydataError(f"between= needs two values, the low end and the high end.\nFor example:  {example}")
    low, high = (_end_value(sp, v, "between=") for v in between)
    if (low - high).is_nonnegative:
        raise SimplydataError(f"between= must go from the low end to the high end; it was "
                              f"[{between[0]}, {between[1]}].")
    return low, high


def _domain(sp, ends):
    """The real numbers between two ends (SymPy Interval; an endless end is open), or all real numbers."""
    return sp.S.Reals if ends is None else sp.Interval(*ends)


def _points_table(sp, points, what: str, fast: bool, value_of=None):
    """A finite set of points as a table: at, at exactly (and the value there)."""
    from ._formula import _result_rows, _show, float_of

    rows = []
    for point in sorted(points, key=lambda p: float_of(p) if p.is_real else math.inf):
        row = {"at": float_of(point), "at exactly": _show(point)}
        if value_of is not None:
            value = value_of(point)
            row["value"] = float_of(value) if not value.free_symbols else math.nan
            row["value exactly"] = _show(value)
        rows.append(row)
    if not rows:
        import pandas as pd

        from .table import table

        columns = ["at", "at exactly"] + (["value", "value exactly"] if value_of is not None else [])
        return table(pd.DataFrame(columns=columns), fast=fast)
    return _result_rows(rows, fast)


class _CalculusWords:
    """Calculus checks, series, transforms and code of a formula (Formula takes them from here)."""

    # ------------------------------------------------------------------------------------------- transforms
    @friendly
    @one_deadline
    def take_transform(self, name=None, from_letter=None, to_letter=None, order=0, between=None):
        """The Laplace, Fourier, Mellin, sine, cosine or Hankel transform. formula.take_transform("laplace")

        formula = sdata.formula("exp(-2*t)"), then formula.take_transform("laplace") gives 1/(s + 2) (SymPy
        laplace_transform). Names: "laplace", "fourier", "mellin", "sine", "cosine", "hankel", and each with
        "inverse " in front ("inverse laplace" gives exp(-2*t) back, with Heaviside(t): 0 before t = 0). from_letter=
        is the letter of the formula (t for Laplace, x for Fourier, s for an inverse Laplace, else the only letter);
        to_letter= the letter of the answer (s for Laplace, k for Fourier). The Fourier transform has SymPy's
        convention, with 2*pi in the power: the integral of f(x)*exp(-2*pi*I*x*k). order= is the order of the Bessel
        function of the Hankel transform (0 by itself); between= is the strip of s for "inverse mellin", such as
        between=[0, "infinity"]. SymPy's names work too ("laplace_transform"). Gives a new formula; this one does
        not change. As SymPy laplace_transform(noconds=True); MATLAB laplace.
        """
        from ._errors import SimplydataError
        from ._formula import Formula, _guarded, _show, exact_number, need_sympy

        sp = need_sympy("formula.take_transform()")
        if name is None:
            raise SimplydataError('formula.take_transform() needs the name of a transform, such as '
                                  'formula.take_transform("laplace"). Names: '
                                  + ", ".join(f'"{n}"' for n in TRANSFORMS))
        key = _value(TRANSFORMS, TRANSFORM_SPELLINGS, name, "take_transform", "name")
        function_name, usual_from, usual_to, about = TRANSFORMS[key]
        letters = self._letters()
        if from_letter is None:
            from_letter = usual_from if usual_from in letters or len(letters) != 1 else letters[0]
        example = f'take_transform("{key}", from_letter="{usual_from}", to_letter="{usual_to}")'
        x = self._letter("take_transform", from_letter, example)
        if to_letter is None:
            to_letter = usual_to
        if not isinstance(to_letter, str) or not to_letter.isidentifier():
            raise SimplydataError(f'to_letter= is the letter of the answer in quotes, such as '
                                  f'to_letter="{usual_to}".')
        if to_letter == str(x) or to_letter in letters:
            new = usual_to if usual_to not in letters else "w"
            raise SimplydataError(f"to_letter= must be a new letter, not one of the formula's letters "
                                  f'({", ".join(letters)}): such as to_letter="{new}".')
        y = sp.Symbol(to_letter)
        values: list = [self._expr, x, y]
        named: dict = {}
        if key in ("hankel", "inverse hankel"):
            if isinstance(order, bool) or not isinstance(order, (int, float)) or not math.isfinite(order):
                raise SimplydataError("order= is the order of the Bessel function, a number such as order=0.")
            values.append(exact_number(sp, order))
        elif order != 0:
            raise SimplydataError(f'order= goes with "hankel" and "inverse hankel"; leave it out for "{key}".')
        if key == "inverse mellin":
            ends = _range(sp, between, "between=", f'take_transform("inverse mellin", between=[0, "infinity"])')
            if ends is None:
                raise SimplydataError('take_transform("inverse mellin") needs between=, the strip of s where the '
                                      'transform holds, such as between=[0, "infinity"].')
            values.append(ends)
        elif between is not None:
            raise SimplydataError(f'between= goes with "inverse mellin" (the strip of s); leave it out for "{key}".')
        else:
            named["noconds"] = True
        found = _guarded(getattr(sp, function_name), *values, what=f"SymPy {function_name}", **named)
        from sympy.integrals.transforms import IntegralTransform

        if isinstance(found, tuple):  # (transform, strip or condition)
            found = found[0]
        if found.has(IntegralTransform):
            raise SimplydataError(f"SymPy found no formula for the {key} transform of {_show(self._expr)} (SymPy "
                                  f"{function_name} gave it back unworked). formula.as_sympy() hands the formula to "
                                  "SymPy itself.")
        print(f"The {key} transform of {_show(self._expr)} ({about}): {_show(found)}   (SymPy {function_name})")
        return Formula(found)

    # ------------------------------------------------------------------------------------------- along a path
    @friendly
    @one_deadline
    def find_area_along_path(self, path=None, between=None):
        """The area under the formula along a path: the line integral.
        area = formula.find_area_along_path(path="x = cos(t), y = sin(t)", between=[0, "2*pi"])

        formula = sdata.formula("x**2 + y**2"), then formula.find_area_along_path(path="x = cos(t), y = sin(t)",
        between=[0, "2*pi"]) gives 2*pi: the formula added up along the circle, each bit of path times its length,
        like the area of a curtain hung from the path up to the formula (SymPy line_integrate). path= gives each
        letter of the formula as a formula of one new letter (t), as text "x = cos(t), y = sin(t)" or a dict
        {"x": "cos(t)", "y": "sin(t)"}; between= is where that letter starts and ends (numbers, or formulas of
        numbers such as "2*pi"). Gives a number, or a formula when letters are left. As SymPy line_integrate.
        """
        from ._errors import SimplydataError
        from ._formula import _guarded, _show, need_sympy, parse
        from ._formula_algebra import _back

        sp = need_sympy("formula.find_area_along_path()")
        example = 'formula.find_area_along_path(path="x = cos(t), y = sin(t)", between=[0, "2*pi"])'
        pieces = self._path_pieces(path, example)
        letters = self._letters()
        missing = [n for n in letters if n not in pieces]
        extra = [n for n in pieces if n not in letters]
        if missing or extra:
            raise SimplydataError(f"path= needs a formula for each letter of {_show(self._expr)} "
                                  f"({', '.join(letters) or 'none'})" + (f"; it has none for {', '.join(missing)}"
                                                                         if missing else "")
                                  + (f"; {', '.join(extra)} is not a letter of the formula" if extra else "")
                                  + f".\nFor example:  {example}")
        made = {n: parse(text, "path=") for n, text in pieces.items()}
        along = sorted({str(s) for e in made.values() for s in e.free_symbols})
        if len(along) != 1 or along[0] in letters:
            raise SimplydataError(f"path= needs every formula in one new letter that runs along the path, such as t; "
                                  f"these have {', '.join(along) or 'none'}.\nFor example:  {example}")
        ends = _range(sp, between, "between=", example)
        if ends is None:
            raise SimplydataError(f"find_area_along_path() needs between=, where {along[0]} starts and ends.\n"
                                  f"For example:  {example}")
        t = next(iter(next(e for e in made.values() if e.free_symbols).free_symbols))
        order = [self._symbol(n) for n in letters]
        curve = sp.Curve([made[n] for n in letters], (t, *ends))
        found = _guarded(sp.line_integrate, self._expr, curve, order, what="SymPy line_integrate")
        if found.has(sp.Integral):
            raise SimplydataError(f"SymPy found no exact area of {_show(self._expr)} along this path (SymPy "
                                  "line_integrate left an integral).")
        said = ", ".join(f"{n} = {_show(made[n])}" for n in letters)
        print(f"The area under {_show(self._expr)} along the path {said}, {t} from {_show(ends[0])} to "
              f"{_show(ends[1])}: {_show(found)}   (SymPy line_integrate)")
        return _back(sp, found)

    def _path_pieces(self, path, example: str) -> dict:
        from ._errors import SimplydataError

        if isinstance(path, dict) and path and all(isinstance(k, str) and isinstance(v, str) for k, v in path.items()):
            return dict(path)
        if not isinstance(path, str) or not path.strip():
            raise SimplydataError(f"find_area_along_path() needs path=, each letter as a formula of one new letter."
                                  f"\nFor example:  {example}")
        parts, depth, start = [], 0, 0
        for i, sign in enumerate(path):  # split at the commas outside brackets
            depth += {"(": 1, ")": -1, "[": 1, "]": -1}.get(sign, 0)
            if sign == "," and depth == 0:
                parts.append(path[start:i])
                start = i + 1
        parts.append(path[start:])
        out = {}
        for part in parts:
            found = _PATH_PART.match(part)
            if not found:
                raise SimplydataError(f'path= reads "letter = formula" parts with commas between; "{part.strip()}" is '
                                      f"not one.\nFor example:  {example}")
            out[found.group(1)] = found.group(2)
        return out

    # ------------------------------------------------------------------------------------------- calculus checks
    @friendly
    @one_deadline
    def check_if_always(self, kind=None, between=None, for_letter=None):
        """Whether the formula is always rising, falling or bending up.
        answer = formula.check_if_always("rising", between=[0, 5])

        formula = sdata.formula("x**3"), then formula.check_if_always("rising", between=[-1, 1]) gives True (SymPy
        is_increasing). Kinds: "rising" (never goes down), "falling" (never goes up), "strictly rising" (always goes
        up), "strictly falling" (always goes down), "one way only" (always up or always down: strictly monotonic,
        is_monotonic) and "bending up" (convex, is_convex). between= is the range of the letter (every real number
        when left out). Gives True or False; None when SymPy cannot tell, which simplydata says. As SymPy
        is_increasing.
        """
        from ._errors import SimplydataError
        from ._formula import _guarded, _show, need_sympy

        sp = need_sympy("formula.check_if_always()")
        if kind is None:
            raise SimplydataError('formula.check_if_always() needs a kind, such as formula.check_if_always("rising"). '
                                  "Kinds: " + ", ".join(f'"{k}"' for k in ALWAYS))
        key = _value(ALWAYS, ALWAYS_SPELLINGS, kind, "check_if_always", "kind")
        function_name, meaning = ALWAYS[key]
        x = self._letter("check_if_always", for_letter, f'check_if_always("{key}", for_letter="x")')
        ends = _range(sp, between, "between=", f'formula.check_if_always("{key}", between=[0, 5])')
        domain = _domain(sp, ends)
        if function_name == "is_convex":
            found = _guarded(sp.is_convex, self._expr, x, what="SymPy is_convex", domain=domain)
        else:
            found = _guarded(getattr(sp, function_name), self._expr, domain, x, what=f"SymPy {function_name}")
        where = f"for {x} from {_show(ends[0])} to {_show(ends[1])}" if ends else f"for every real {x}"
        if found is None:
            print(f"SymPy cannot tell whether {_show(self._expr)} is always {key} {where}   (SymPy {function_name})")
            return None
        answer = bool(found)
        print(f"{_show(self._expr)} is {'' if answer else 'not '}always {key} {where}: it "
              f"{meaning if answer else 'does not: ' + meaning}   (SymPy {function_name})")
        return answer

    @friendly
    @one_deadline
    def find_turning_points(self, between=None, for_letter=None, fast=False):
        """Where the slope of the formula is 0: its turning points. points = formula.find_turning_points()

        formula = sdata.formula("x**3 - 3*x"), then formula.find_turning_points() gives -1 and 1, with the value of the
        formula at each (SymPy stationary_points). between= keeps the points in a range of the letter; a repeating
        formula (sin(x)) needs a range of finite length. Gives a table: at, at exactly, value, value exactly. As SymPy
        stationary_points.
        """
        from ._formula import _guarded, need_sympy

        sp = need_sympy("formula.find_turning_points()")
        x = self._letter("find_turning_points", for_letter, 'find_turning_points(for_letter="x")')
        ends = _range(sp, between, "between=", "formula.find_turning_points(between=[0, 7])")
        found = _guarded(sp.stationary_points, self._expr, x, _domain(sp, ends), what="SymPy stationary_points")
        return self._point_set(sp, found, x, ends, "turning points", "stationary_points", fast, with_value=True)

    @friendly
    @one_deadline
    def find_where_undefined(self, between=None, for_letter=None, fast=False):
        """Where the formula has no value: its singularities. points = formula.find_where_undefined()

        formula = sdata.formula("1/(x**2 - 1)"), then formula.find_where_undefined() gives -1 and 1, where the formula
        divides by 0 (SymPy singularities). between= keeps the points in a range of the letter; a repeating formula
        (tan(x)) needs a range of finite length. Gives a table: at, at exactly. As SymPy singularities.
        """
        from ._formula import _guarded, need_sympy

        sp = need_sympy("formula.find_where_undefined()")
        x = self._letter("find_where_undefined", for_letter, 'find_where_undefined(for_letter="x")')
        ends = _range(sp, between, "between=", "formula.find_where_undefined(between=[0, 7])")
        found = _guarded(sp.singularities, self._expr, x, _domain(sp, ends), what="SymPy singularities")
        return self._point_set(sp, found, x, ends, "points where it is undefined", "singularities", fast)

    def _point_set(self, sp, found, x, ends, what: str, function_name: str, fast: bool, with_value: bool = False):
        from ._errors import SimplydataError
        from ._formula import _guarded, _show

        where = f" for {x} from {_show(ends[0])} to {_show(ends[1])}" if ends else ""
        if not isinstance(found, sp.FiniteSet):
            raise SimplydataError(f"The {what} of {_show(self._expr)}{where} are endless: {found} (SymPy "
                                  f"{function_name}). Keep the letter to a range of finite length with between=, "
                                  "such as between=[0, 7].")

        def value_of(point):
            return _guarded(self._expr.subs, x, point, what="SymPy subs")

        points = list(found)
        said = ", ".join(_show(p) for p in sorted(points, key=lambda p: (not p.is_real, str(p)))) or "none"
        print(f"The {what} of {_show(self._expr)}{where}: {said}   (SymPy {function_name})")
        return _points_table(sp, points, what, fast, value_of if with_value else None)

    @friendly
    def find_period(self, for_letter=None):
        """How often the formula repeats: its period. period = formula.find_period()

        formula = sdata.formula("sin(2*x)"), then formula.find_period() gives pi (about 3.14159): the formula is the
        same at x and at x + pi (SymPy periodicity). A formula that does not repeat gives None, which simplydata
        says. Gives a number, or a formula when other letters are in the period (sin(a*x)). As SymPy periodicity.
        """
        from ._formula import _guarded, _show, need_sympy
        from ._formula_algebra import _back

        sp = need_sympy("formula.find_period()")
        x = self._letter("find_period", for_letter, 'find_period(for_letter="x")')
        found = _guarded(sp.periodicity, self._expr, x, what="SymPy periodicity")
        if found is None:
            print(f"{_show(self._expr)} does not repeat as {x} changes (or SymPy cannot find how often)   "
                  "(SymPy periodicity)")
            return None
        print(f"{_show(self._expr)} repeats every {_show(found)} in {x}   (SymPy periodicity)")
        return _back(sp, found)

    # ------------------------------------------------------------------------------------------- series
    @friendly
    @one_deadline
    def find_fourier_series(self, between=None, how_many_terms=3, for_letter=None):
        """The formula as a sum of sines and cosines (its Fourier series).
        series = formula.find_fourier_series(between=["-pi", "pi"])

        formula = sdata.formula("x"), then formula.find_fourier_series(between=["-pi", "pi"]) gives 2*sin(x) -
        sin(2*x) + 2*sin(3*x)/3: the first how_many_terms= terms that are not 0 (3 by itself, up to 100) of the
        series that repeats the formula over the range (SymPy fourier_series, then truncate). between= is the range
        that repeats, ["-pi", "pi"] by itself. Gives a new formula. As SymPy fourier_series.
        """
        from ._errors import SimplydataError
        from ._formula import Formula, _guarded, _show, _whole, need_sympy

        sp = need_sympy("formula.find_fourier_series()")
        x = self._letter("find_fourier_series", for_letter, 'find_fourier_series(for_letter="x")')
        count = _whole(how_many_terms, "how_many_terms=", 1, MAX_FOURIER_TERMS,
                       'formula.find_fourier_series(between=["-pi", "pi"], how_many_terms=5)')
        ends = _range(sp, between, "between=", 'formula.find_fourier_series(between=["-pi", "pi"])',
                      default=(-sp.pi, sp.pi))
        if not (ends[0].is_finite and ends[1].is_finite):
            raise SimplydataError("between= needs a range of finite length for a Fourier series, such as "
                                  'between=["-pi", "pi"].')
        series = _guarded(sp.fourier_series, self._expr, (x, *ends), what="SymPy fourier_series")
        found = _guarded(series.truncate, count, what="SymPy truncate")
        print(f"{_show(self._expr)} as a Fourier series over {x} from {_show(ends[0])} to {_show(ends[1])}, the "
              f"first {count} term{'s' if count != 1 else ''}: {_show(found)}   (SymPy fourier_series)")
        return Formula(found)

    @friendly
    @one_deadline
    def find_residue_at(self, at=0, for_letter=None):
        """The residue of the formula at a point (complex analysis). residue = formula.find_residue_at(0)

        formula = sdata.formula("exp(x)/x**3"), then formula.find_residue_at(0) gives 1/2: the number in front of
        1/x in the series of the formula around x = 0 (SymPy residue). at= is the point: a number, or a formula of
        numbers such as "pi". Gives a number, or a formula when letters are left. As SymPy residue.
        """
        from ._formula import _guarded, _show, need_sympy
        from ._formula_algebra import _back

        sp = need_sympy("formula.find_residue_at()")
        x = self._letter("find_residue_at", for_letter, 'find_residue_at(0, for_letter="x")')
        point = _end_value(sp, at, "at=")
        found = _guarded(sp.residue, self._expr, x, point, what="SymPy residue")
        print(f"The residue of {_show(self._expr)} at {x} = {_show(point)}: {_show(found)}   (SymPy residue)")
        return _back(sp, found)

    @friendly
    @one_deadline
    def list_terms(self, between=None, for_letter=None, fast=False):
        """The terms of a sequence, one for each whole number in a range. terms = formula.list_terms(between=[1, 10])

        formula = sdata.formula("n**2"), then formula.list_terms(between=[1, 5]) gives 1, 4, 9, 16 and 25 (SymPy
        sequence). between= gives the first and the last whole number (up to 10,000 terms). Gives a table: the
        letter, term, term exactly. sdata.find_sum_of_series adds the terms up. As SymPy sequence; R seq.
        """
        from ._errors import SimplydataError
        from ._formula import _guarded, _result_rows, _show, need_sympy

        sp = need_sympy("formula.list_terms()")
        x = self._letter("list_terms", for_letter, 'list_terms(between=[1, 10], for_letter="n")')
        example = "formula.list_terms(between=[1, 10])"
        if isinstance(between, (str, bytes)) or not isinstance(between, (list, tuple)) or len(between) != 2 or any(
                isinstance(v, bool) or not isinstance(v, int) for v in between):
            raise SimplydataError(f"list_terms() needs between= the first and the last whole number.\n"
                                  f"For example:  {example}")
        low, high = int(between[0]), int(between[1])
        if high < low:
            raise SimplydataError(f"between= must go from the first to the last; it was [{low}, {high}].")
        if high - low + 1 > MAX_TERMS:
            raise SimplydataError(f"list_terms() lists up to {MAX_TERMS:,} terms; [{low}, {high}] has "
                                  f"{high - low + 1:,}. Use a shorter range.")
        sequence = _guarded(sp.sequence, self._expr, (x, low, high), what="SymPy sequence")
        terms = _guarded(sequence.__getitem__, slice(None), what="SymPy sequence")
        rows = []
        name = str(x)
        for position, term in zip(range(low, high + 1), terms):
            from ._formula_algebra import _back

            value = _back(sp, term)
            rows.append({name: position, "term": value if isinstance(value, float) else math.nan,
                         "term exactly": _show(term)})
        shown = ", ".join(r["term exactly"] for r in rows[:10]) + (" ..." if len(rows) > 10 else "")
        print(f"The terms of {_show(self._expr)} for {name} from {low} to {high}: {shown}   (SymPy sequence)")
        return _result_rows(rows, fast)

    # ------------------------------------------------------------------------------------------- grids of slopes
    @friendly
    def find_hessian(self, for_letters=None):
        """The grid of every second slope of the formula (its Hessian), exactly. grid = formula.find_hessian()

        formula = sdata.formula("x**2*y + y**3"), then formula.find_hessian() gives the exact grid [[2*y, 2*x], [2*x,
        6*y]]: row i, column j is the slope for letter i of the slope for letter j (SymPy hessian). for_letters= gives
        the letters and their order (every letter, in alphabetical order, by itself). Gives an exact grid
        (sdata.number_grid(..., exactly=True)): grid.find_determinant() and grid.find_value_at(x=1, y=2) work on it.
        As SymPy hessian.
        """
        from ._errors import SimplydataError
        from ._exact_grid import ExactGrid
        from ._formula import _guarded, _show, need_sympy

        sp = need_sympy("formula.find_hessian()")
        letters = self._letters() if for_letters is None else for_letters
        if isinstance(letters, str):
            letters = [letters]
        if not isinstance(letters, (list, tuple)) or not letters:
            raise SimplydataError(f"{_show(self._expr)} has no letter, so it has no Hessian."
                                  if for_letters is None else 'for_letters= needs a list of letters, such as '
                                  'for_letters=["x", "y"].')
        symbols = [self._letter("find_hessian", n, 'find_hessian(for_letters=["x", "y"])') for n in letters]
        found = _guarded(sp.hessian, self._expr, symbols, what="SymPy hessian")
        print(f"The Hessian of {_show(self._expr)} for {', '.join(str(s) for s in symbols)}: "
              f"{_show(found.tolist())}   (SymPy hessian)")
        return ExactGrid(found)

    @friendly
    def find_wronskian(self, others=None, for_letter=None, whole_numbers_only=False):
        """The Wronskian of the formula and other formulas: 0 everywhere when they depend on each other.
        answer = formula.find_wronskian(["exp(2*x)"])

        formula = sdata.formula("exp(x)"), then formula.find_wronskian(["exp(2*x)"]) gives exp(3*x): the determinant
        of the grid of the formulas and their slopes (SymPy wronskian). Not 0 means the formulas are independent
        (the solutions of a differential equation form a basis). whole_numbers_only=True treats the letter as whole
        numbers and gives the Casoratian, the same for sequences, with steps of 1 in place of slopes (SymPy
        casoratian). SymPy's answer is not made simpler: formula.make_simpler() does that. As SymPy wronskian.
        """
        from ._errors import SimplydataError
        from ._formula import Formula, _guarded, _show, need_sympy

        sp = need_sympy("formula.find_wronskian()")
        if not isinstance(whole_numbers_only, bool):
            raise SimplydataError("whole_numbers_only= is True or False.")
        items = self._others(others, "find_wronskian", 'find_wronskian(["cos(x)"])')
        letters = sorted({str(s) for e in (self._expr, *items) for s in e.free_symbols})
        if for_letter is None:
            if len(letters) != 1:
                raise SimplydataError(f"find_wronskian() needs for_letter= when the formulas have "
                                      f"{len(letters) or 'no'} letters ({', '.join(letters) or 'none'}).")
            for_letter = letters[0]
        if for_letter not in letters:
            raise SimplydataError(f"for_letter= needs one of the letters {', '.join(letters)} in quotes.")
        x = next(s for e in (self._expr, *items) for s in e.free_symbols if str(s) == for_letter)
        functions = [self._expr, *items]
        name = "casoratian" if whole_numbers_only else "wronskian"
        found = _guarded(getattr(sp, name), functions, x, what=f"SymPy {name}")
        said = ", ".join(_show(f) for f in functions)
        print(f"The {name.capitalize()} of {said} in {x}: {_show(found)}   (SymPy {name})")
        return Formula(found)

    # ------------------------------------------------------------------------------------------- showing
    @friendly
    def show_as_code(self, language=None):
        """The formula written as code of another language; also gives the text back. formula.show_as_code("r")

        formula = sdata.formula("sin(x)**2 + exp(-x)"), then formula.show_as_code("r") prints sin(x)^2 + exp(-x)
        (SymPy rcode). Languages: "c", "c++", "fortran", "glsl", "javascript", "julia", "maple", "mathematica",
        "mathml", "octave" (MATLAB too), "python", "r", "rust", "smt-lib", "sympy" (SymPy code that makes the
        formula again), "text" and "sympy tree" (SymPy's full form, srepr). SymPy's names work too ("rcode",
        "julia_code"). Nothing is written to a file. show_as_latex() writes LaTeX. As SymPy rcode, ccode ...
        """
        from ._errors import SimplydataError
        from ._formula import _guarded, need_sympy

        sp = need_sympy("formula.show_as_code()")
        if language is None:
            raise SimplydataError('formula.show_as_code() needs a language, such as formula.show_as_code("r"). '
                                  "Languages: " + ", ".join(f'"{n}"' for n in LANGUAGES))
        key = _value(LANGUAGES, LANGUAGE_SPELLINGS, language, "show_as_code", "language")
        printer = getattr(sp, LANGUAGES[key][0])
        text = str(_guarded(printer, self._expr, what=f"SymPy {LANGUAGES[key][0]}"))
        print(text)
        return text

    @friendly
    def show_as_tree(self, as_graphviz=False):
        """The parts of the formula as a tree, one part on each line; also gives the text back. formula.show_as_tree()

        formula = sdata.formula("x**2 + 1"), then formula.show_as_tree() prints Add: x**2 + 1, then its parts One: 1 and
        Pow: x**2, and their parts below them (SymPy's tree printer, print_tree, without the assumptions).
        as_graphviz=True writes the tree in the Graphviz dot language instead (SymPy dotprint), to draw with
        Graphviz. Nothing is written to a file. As SymPy print_tree.
        """
        from ._errors import SimplydataError
        from ._formula import _guarded, need_sympy

        need_sympy("formula.show_as_tree()")
        if not isinstance(as_graphviz, bool):
            raise SimplydataError("as_graphviz= is True or False.")
        if as_graphviz:
            from sympy.printing.dot import dotprint

            text = _guarded(dotprint, self._expr, what="SymPy dotprint")
        else:
            from sympy.printing.tree import tree

            text = _guarded(tree, self._expr, what="SymPy print_tree", assumptions=False).rstrip("\n")
        print(text)
        return text
