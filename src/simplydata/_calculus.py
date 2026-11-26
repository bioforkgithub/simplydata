"""Areas, volumes and paths over time from a formula: sdata.find_area_under, find_volume_under, find_path_over_time.

Every number comes from SciPy (and SymPy for exactly=True):

* find_area_under: integrate.quad (QUADPACK, as R integrate()); test_method="gauss" is integrate.fixed_quad (5-point
  Gauss-Legendre); exactly=True: sympy.integrate;
* find_volume_under: integrate.dblquad (two letters), tplquad (three), nquad (more), the letters in the order of
  between= (the first is the outer one) and handed to SciPy in its own reversed order;
* find_path_over_time: integrate.solve_ivp (RK45 by default; LSODA, Radau, BDF, DOP853, RK23), with the relative and
  absolute tolerances of R deSolve (1e-6), t_eval from time_step= and a stopping event from stop_when=;
  exactly=True: sympy.dsolve;
* numbers phase, batch 4 (approved by Manish 2026-11-26): find_volume_under(exactly=True): sympy.integrate over each
  letter in turn; find_path_over_time(exactly=True) without at_start= gives the general solution (dsolve with its
  free constants C1, C2), and a second-order equation "d2x/dt2 = ..." is solved exactly (dsolve) or in numbers
  (solve_ivp, with dx/dt as a second changing value); find_sum_of_series: sympy.summation, with Sum.is_convergent
  and evalf when there is no closed form.

The formulas are read by the same safe reader as fit_formula and find_where_smallest (Python's ast; never run), so
the same text works everywhere, and a formula made with sdata.formula() is accepted too. Own code is glue only.
"""

from __future__ import annotations

import math
import re
import warnings

import numpy as np

from ._errors import SimplydataError, choice_error, friendly
from ._maths_formula import read_formula, split_equation
from ._time_limit import one_deadline

AREA_METHODS = {"quad": "SciPy integrate.quad (adaptive Gauss-Kronrod, QUADPACK), as R integrate()",
                "gauss": "SciPy integrate.fixed_quad (Gauss-Legendre with 5 points)"}
AREA_SPELLINGS = {"adaptive": "quad", "quadpack": "quad", "fixed_quad": "gauss", "gauss-legendre": "gauss",
                  "gaussian": "gauss"}
PATH_METHODS = {"RK45": "RK45 (Dormand-Prince, explicit Runge-Kutta 5(4))",
                "LSODA": "LSODA (switches between Adams and BDF when the problem turns stiff, as R deSolve's default)",
                "stiff": "Radau (implicit Runge-Kutta of order 5, for stiff problems)",
                "BDF": "BDF (backward differentiation, for stiff problems)",
                "DOP853": "DOP853 (explicit Runge-Kutta of order 8)",
                "RK23": "RK23 (Bogacki-Shampine, explicit Runge-Kutta 3(2))"}
PATH_SCIPY = {"RK45": "RK45", "LSODA": "LSODA", "stiff": "Radau", "BDF": "BDF", "DOP853": "DOP853", "RK23": "RK23"}
PATH_SPELLINGS = {"rk45": "RK45", "lsoda": "LSODA", "stiff": "stiff", "radau": "stiff", "bdf": "BDF",
                  "dop853": "DOP853", "rk23": "RK23", "ode45": "RK45", "ode23": "RK23", "ode15s": "BDF"}
RTOL = 1e-6  # as R deSolve::ode (rtol = 1e-6, atol = 1e-6)
ATOL = 1e-6
_DERIVATIVE = re.compile(r"^\s*d\s*([A-Za-z]\w*)\s*/\s*d\s*([A-Za-z]\w*)\s*$")
# "d2x/dt2" (also written d^2x/dt^2): the slope of the slope (numbers phase, batch 4)
_SECOND = re.compile(r"^\s*d\s*\^?\s*2\s*([A-Za-z]\w*)\s*/\s*d\s*([A-Za-z]\w*?)\s*\^?\s*2\s*$")
MAX_SUM_TERMS = 10_000  # a finite sum with no closed form is added term by term only up to this many terms
_INFINITY = {"infinity": math.inf, "inf": math.inf, "+infinity": math.inf, "-infinity": -math.inf,
             "-inf": -math.inf, "minus infinity": -math.inf}


def _show(x) -> str:
    x = float(x)
    if math.isinf(x):
        return "infinity" if x > 0 else "-infinity"
    return f"{x:.6g}"


def _text_of(formula, step: str) -> str:
    if hasattr(formula, "_formula_text"):
        return formula._formula_text()
    if not isinstance(formula, str):
        raise SimplydataError(f'{step}() needs a formula in quotes, for example '
                              f'sdata.{step}("exp(-x**2)", between=[0, "infinity"]).')
    return formula


def _end(value, step: str, name: str) -> float:
    """One end of a range: a number, "infinity" or "-infinity"."""
    if isinstance(value, str) and value.strip().lower() in _INFINITY:
        return _INFINITY[value.strip().lower()]
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)) or math.isnan(value):
        raise SimplydataError(f'{step}() needs between= numbers (or "infinity", "-infinity") for {name}; '
                              f"it got {value!r}.")
    return float(value)


def _span(pair, step: str, name: str, example: str) -> tuple[float, float]:
    if isinstance(pair, (str, bytes)) or not isinstance(pair, (list, tuple)) or len(pair) != 2:
        raise SimplydataError(f"{step}() needs between= two ends for {name}, the lowest and the highest.\n"
                              f"For example:  {example}")
    low, high = _end(pair[0], step, name), _end(pair[1], step, name)
    if not low < high:
        raise SimplydataError(f"between= for {name} must go from a lower value to a higher one; it was "
                              f"[{_show(low)}, {_show(high)}].")
    return low, high


def _quiet(call, *args, **kwargs):
    """Run a SciPy integrator; its warnings come back as notes."""
    from scipy.integrate import IntegrationWarning

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", IntegrationWarning)
        out = call(*args, **kwargs)
    notes = [str(w.message).strip().splitlines()[0] for w in caught if issubclass(w.category, IntegrationWarning)]
    return out, notes


@friendly(renamed={"method": "test_method"})
def find_area_under(formula=None, between=None, test_method="quad", exactly=False, known=None):
    """The area under a formula's curve between two values (the definite integral). sdata.find_area_under("x**2", between=[0, 3])

    sdata.find_area_under("exp(-x**2)", between=[0, "infinity"]) gives 0.886227 (half the square root of pi).
    The formula has one letter (known= fixes others, as in sdata.solve). The area below 0 counts as minus.
    test_method="quad" (the default: SciPy integrate.quad, adaptive, as R integrate()) or "gauss" (fixed_quad,
    5 points; ends must be numbers). exactly=True gives the exact answer from SymPy integrate (simplydata[exact]),
    as a formula. For a list of readings use nums.turn_into_running_area().
    """
    from scipy import integrate

    step = "find_area_under"
    example = 'sdata.find_area_under("x**2", between=[0, 3])'
    if formula is None:
        raise SimplydataError(f"find_area_under() needs a formula in quotes.\nFor example:  {example}")
    if not isinstance(exactly, bool):
        raise SimplydataError("exactly= should be True or False.")
    text = _text_of(formula, step)
    read = read_formula(text, known=known)
    if len(read.names) != 1:
        raise SimplydataError(f"find_area_under() needs a formula with one letter; {text} has {len(read.names)} "
                              f"({', '.join(read.names) or 'none'}). Fix the others with known={{...}}, or use "
                              "sdata.find_volume_under for two or more.")
    name = read.names[0]
    if between is None:
        raise SimplydataError(f"find_area_under() needs between=[low, high].\nFor example:  {example}")
    low, high = _span(between, step, name, example)
    from ._formula import check_range_fits

    check_range_fits(formula, name, low, high, step)
    if exactly:
        return _area_exactly(text, name, low, high, known)
    key = AREA_SPELLINGS.get(str(test_method).strip().lower(), str(test_method).strip().lower())
    if key == "romberg":
        raise SimplydataError('test_method="romberg" is gone: SciPy removed integrate.romberg in version 1.15. Use '
                              'test_method="quad" (the default) or "gauss".')
    if key not in AREA_METHODS:
        raise choice_error(step, "test_method", test_method, list(AREA_METHODS))

    def curve(x):
        return float(read({name: x}))

    if key == "quad":
        try:
            (value, error), notes = _quiet(integrate.quad, curve, low, high)
        except (ZeroDivisionError, OverflowError):
            raise SimplydataError(
                f"{text} cannot be worked out at some {name} between {_show(low)} and {_show(high)} (such as a "
                f"division by 0), so the area there may not exist. Split the range at that point, for example "
                f"between=[{_show(low)}, 0] and between=[0, {_show(high)}], or check the formula.") from None
        said = f"error below {error:.2g}"
    else:
        if math.isinf(low) or math.isinf(high):
            raise SimplydataError('test_method="gauss" needs two numbers for between=; for "infinity" use '
                                  'test_method="quad".')

        def curve_many(xs):
            return np.asarray(read({name: np.asarray(xs, dtype=float)}), dtype=float) * np.ones_like(xs)

        (value, _), notes = _quiet(integrate.fixed_quad, curve_many, low, high, n=5)
        said = "5 points; no error estimate"
    print(f"The area under {text} for {name} from {_show(low)} to {_show(high)}: {_show(value)} ({said}).")
    print(f"Method: {AREA_METHODS[key]}.")
    for note in notes:
        print(f"Note from SciPy: {note}")
    return float(value)


def _exact_end(sp, v):
    return sp.oo if v == math.inf else (-sp.oo if v == -math.inf else sp.nsimplify(v, rational=True))


def _exact_answer(sp, found, what: str):
    """Refuse an exact area or volume that does not settle on a number, or that SymPy could not work out."""
    if found in (sp.oo, -sp.oo):
        raise SimplydataError(f"{what} is {'infinite' if found == sp.oo else 'minus infinite'}: it does not settle "
                              "on a number (SymPy integrate).")
    if found is sp.nan or found.has(sp.nan) or found.has(sp.zoo):
        raise SimplydataError(f"{what} does not settle on a number (the integral does not converge; SymPy integrate "
                              "gives no value).")
    if found.has(sp.Integral):
        raise SimplydataError(f"SymPy found no exact answer for {what[0].lower() + what[1:]}; without exactly=True "
                              "simplydata gives it as a decimal.")


def _exact_values(sp, known) -> dict:
    """known= as exact numbers (exact_number: 0.3 is 3/10), the same rule as the typed numbers of a formula."""
    from ._formula import exact_number
    from ._maths_formula import _known_values

    return {k: exact_number(sp, v) for k, v in _known_values(known).items()}


def _exact_floats(sp, expr):
    """Typed decimals of a formula (0.3) as the exact numbers they stand for (3/10), as known= values are."""
    from ._formula import exact_number

    floats = expr.atoms(sp.Float)
    return expr.xreplace({f: exact_number(sp, float(f)) for f in floats}) if floats else expr


def _about(sp, found) -> str:
    """" (about 1.234)" for an exact real number, worked out under the time limit; "" otherwise."""
    from ._formula import EXACTLY_HINT, float_of

    if found.free_symbols or not found.is_real:
        return ""
    return f" (about {float_of(found, 'SymPy N', EXACTLY_HINT):.10g})"


def _area_exactly(text, name, low, high, known):
    from ._formula import EXACTLY_HINT, Formula, _guarded, _show as said, need_sympy, parse

    sp = need_sympy("find_area_under(exactly=True)")
    expr = _exact_floats(sp, parse(text, "find_area_under()", _exact_values(sp, known)))
    x = next((s for s in expr.free_symbols if str(s) == name), sp.Symbol(name))
    found = _guarded(sp.integrate, expr, (x, _exact_end(sp, low), _exact_end(sp, high)), what="SymPy integrate",
                     hint=EXACTLY_HINT)
    _exact_answer(sp, found, f"The area under {text} for {name} from {_show(low)} to {_show(high)}")
    print(f"The area under {text} for {name} from {_show(low)} to {_show(high)}: {said(found)}{_about(sp, found)}.")
    print("Method: SymPy integrate, exact.")
    return Formula(found)


@friendly
def find_volume_under(formula=None, between=None, known=None, exactly=False):
    """The volume under a formula of two or more letters, over a range of each (a double or triple integral).

    sdata.find_volume_under("x * y", between={"x": [0, 1], "y": [0, 2]})   (1)
    between= gives a range for each letter; the first letter is the outer one. Two letters: SciPy
    integrate.dblquad; three: tplquad; more: nquad (the total under the surface). Ends can be "infinity".
    exactly=True gives the exact answer from SymPy integrate (one letter after the other, the last letter of
    between= first), as a formula (simplydata[exact]).
    """
    from scipy import integrate

    step = "find_volume_under"
    example = 'sdata.find_volume_under("x * y", between={"x": [0, 1], "y": [0, 2]})'
    if formula is None:
        raise SimplydataError(f"find_volume_under() needs a formula in quotes.\nFor example:  {example}")
    if not isinstance(exactly, bool):
        raise SimplydataError("exactly= should be True or False.")
    text = _text_of(formula, step)
    read = read_formula(text, known=known)
    if len(read.names) < 2:
        raise SimplydataError(f"find_volume_under() needs a formula with two or more letters; {text} has "
                              f"{len(read.names)}. For one letter use sdata.find_area_under.")
    if not isinstance(between, dict):
        raise SimplydataError(f"find_volume_under() needs between= with a range for each letter "
                              f"({', '.join(read.names)}).\nFor example:  {example}")
    missing = [n for n in read.names if n not in between]
    extra = [n for n in between if n not in read.names]
    if missing or extra:
        raise SimplydataError(f"between= needs a range for each letter of {text} ({', '.join(read.names)}) and no "
                              f"other; {'missing: ' + ', '.join(missing) if missing else 'not in the formula: ' + ', '.join(map(str, extra))}."
                              f"\nFor example:  {example}")
    order = list(between)
    spans = [_span(between[n], step, n, example) for n in order]
    from ._formula import check_range_fits

    for n, (lo, hi) in zip(order, spans):
        check_range_fits(formula, n, lo, hi, step)
    ranges = ", ".join(f"{n} from {_show(lo)} to {_show(hi)}" for n, (lo, hi) in zip(order, spans))
    if exactly:
        return _volume_exactly(text, order, spans, ranges, known)

    def value_at(*inner_first):
        values = dict(zip(reversed(order), inner_first))  # SciPy gives the innermost letter first
        return float(read(values))

    if len(order) == 2:
        (a, b), (c, d) = spans
        (value, error), notes = _quiet(integrate.dblquad, value_at, a, b, c, d)
        how = "SciPy integrate.dblquad (QUADPACK, one letter inside the other)"
    elif len(order) == 3:
        (a, b), (c, d), (e, f) = spans
        (value, error), notes = _quiet(integrate.tplquad, value_at, a, b, c, d, e, f)
        how = "SciPy integrate.tplquad (QUADPACK, one letter inside the other)"
    else:
        (value, error), notes = _quiet(integrate.nquad, value_at, list(reversed(spans)))
        how = f"SciPy integrate.nquad over {len(order)} letters (the total under the surface)"
    print(f"The volume under {text} for {ranges}: {_show(value)} (error below {error:.2g}).")
    print(f"Method: {how}; {order[0]} is the outer letter.")
    for note in notes:
        print(f"Note from SciPy: {note}")
    return float(value)


def _volume_exactly(text, order, spans, ranges, known):
    from ._formula import EXACTLY_HINT, Formula, _guarded, _show as said, need_sympy, parse

    sp = need_sympy("find_volume_under(exactly=True)")
    expr = _exact_floats(sp, parse(text, "find_volume_under()", _exact_values(sp, known)))
    # a letter SymPy cancelled while reading (x*y/y is x) is still integrated over: it multiplies by its range
    symbols = {n: next((s for s in expr.free_symbols if str(s) == n), sp.Symbol(n)) for n in order}
    # SymPy integrates over the first range it is given first: the inner letter (the last of between=) goes first
    limits = [(symbols[n], _exact_end(sp, lo), _exact_end(sp, hi)) for n, (lo, hi) in reversed(list(zip(order,
                                                                                                         spans)))]
    found = _guarded(sp.integrate, expr, *limits, what="SymPy integrate", hint=EXACTLY_HINT)
    _exact_answer(sp, found, f"The volume under {text} for {ranges}")
    print(f"The volume under {text} for {ranges}: {said(found)}{_about(sp, found)}.")
    print(f"Method: SymPy integrate, exact; {order[-1]} first (the inner letter), {order[0]} last.")
    return Formula(found)


# ---------------------------------------------------------------- paths over time
def _velocity_letter(name: str, time: str) -> str:
    """The letter that stands for dx/dt inside a second-order equation."""
    return f"d{name}_d{time}"


def _read_changes(equations, known, example, other_letters_allowed=False):
    """(texts, names, letters, rights, formulas, time, order): names are what the table shows (x, dx/dt), letters
    what the formulas use (x, dx_dt); order is 2 for one equation "d2x/dt2 = ...", else 1."""
    if isinstance(equations, str):
        texts = [equations]
    elif isinstance(equations, (list, tuple)) and equations and all(isinstance(e, str) for e in equations):
        texts = list(equations)
    else:
        raise SimplydataError(f"find_path_over_time() needs an equation such as \"dN/dt = r * N\" in quotes, or a "
                              f"list of them.\nFor example:  {example}")
    names, rights, time, order = [], [], None, 1
    for text in texts:
        left, sign, right = split_equation(text)
        found = _DERIVATIVE.match(left)
        second = _SECOND.match(left) if not found else None
        if sign != "=" or not (found or second):
            raise SimplydataError(f'"{text}" should say how fast something changes, such as "dN/dt = r * N": the '
                                  f"left side is d, a letter, /d and the time letter (or d2x/dt2 for the slope of "
                                  f"the slope).\nFor example:  {example}")
        name, letter = (found or second).groups()
        if second:
            if len(texts) != 1:
                raise SimplydataError("A second-order equation (d2x/dt2 = ...) works on its own: give it alone, not in "
                                      "a list with others.")
            order = 2
        if time is not None and letter != time:
            raise SimplydataError(f"Every equation needs the same time letter; one uses d{time} and one d{letter}.")
        if name == letter:
            raise SimplydataError(f'"{text}": what changes and the time letter cannot be the same letter.')
        if name in names:
            raise SimplydataError(f"{name} has two equations; give one for each letter that changes.")
        time = letter
        names.append(name)
        rights.append(right)
    letters = list(names)
    if order == 2:
        name = names[0]
        speed = _velocity_letter(name, time)
        if re.search(rf"\b{re.escape(speed)}\b", rights[0]):
            raise SimplydataError(f"{speed} is the name simplydata gives to d{name}/d{time}; use another letter.")
        # d x / d t on the right is the speed: written as one letter before the safe reader reads the text
        rights = [speed, re.sub(rf"\bd\s*{re.escape(name)}\s*/\s*d\s*{re.escape(time)}\b", speed, rights[0])]
        names = [name, f"d{name}/d{time}"]
        letters = [name, speed]
    formulas = [read_formula(r, known=known) for r in rights]
    allowed = set(letters) | {time}
    for text, f in zip(texts * len(formulas), formulas):
        other = [n for n in f.names if n not in allowed]
        if other and not other_letters_allowed:  # exactly=True keeps them as letters
            raise SimplydataError(f"{text} uses {', '.join(other)}, which {'is' if len(other) == 1 else 'are'} not "
                                  f"changing and has no value. Give {'it' if len(other) == 1 else 'them'} with "
                                  f"known=, for example known={{{', '.join(repr(n) + ': 0.3' for n in other)}}}.")
    return texts, names, letters, rights, formulas, time, order


@friendly(renamed={"method": "test_method"})
def find_path_over_time(equations=None, at_start=None, between=None, known=None, time_step=None, stop_when=None,
                        test_method="RK45", exactly=False):
    """The values over time from how fast they change (an ordinary differential equation). sdata.find_path_over_time("dN/dt = r * N * (1 - N / K)", at_start={"N": 10}, between=[0, 50], known={"r": 0.3, "K": 1000}, time_step=0.5)

    Gives back a table: time, then each value that changes. Write each equation as "dN/dt = ..."; several
    equations in a list change together (predator and prey). at_start= gives each value at the first time,
    between= the first and last time, known= the fixed values, time_step= the times in the table (else the
    solver's own steps). stop_when="N >= 900" stops when that comes true. SciPy integrate.solve_ivp,
    test_method="RK45" (the default), "LSODA", "stiff" (Radau), "BDF", "DOP853" or "RK23", with the tolerances
    of R deSolve (1e-6). One second-order equation, "d2x/dt2 = -k*x - c*dx/dt", needs at_start={"x": 1,
    "dx/dt": 0}; the table then has dx/dt too. exactly=True gives the formula from SymPy dsolve (one equation;
    simplydata[exact]); without at_start= it gives the general formula, with free constants C1 (and C2).
    """
    from scipy import integrate

    step = "find_path_over_time"
    example = ('sdata.find_path_over_time("dN/dt = r * N * (1 - N / K)", at_start={"N": 10}, between=[0, 50], '
               'known={"r": 0.3, "K": 1000}, time_step=0.5)')
    if not isinstance(exactly, bool):
        raise SimplydataError("exactly= should be True or False.")
    texts, names, letters, rights, formulas, time, order = _read_changes(equations, known, example,
                                                                         other_letters_allowed=exactly)
    if exactly and at_start is None:
        t0 = _span(between, step, time, example)[0] if between is not None else 0.0
        return _path_exactly(texts, names, letters, rights, time, None, t0, known, order)
    if not isinstance(at_start, dict):
        raise SimplydataError(f"find_path_over_time() needs at_start= with the first value of "
                              f"{', '.join(names)}.\nFor example:  {example}"
                              + ("\n(With exactly=True and no at_start=, SymPy gives the general formula.)"
                                 if not exactly else ""))
    missing = [n for n in names if n not in at_start]
    extra = [n for n in at_start if n not in names]
    if missing or extra:
        raise SimplydataError(f"at_start= needs a value for {', '.join(names)} and nothing else"
                              + (f"; missing: {', '.join(missing)}" if missing else
                                 f"; {', '.join(map(str, extra))} does not change") + f".\nFor example:  {example}")
    for n in names:
        v = at_start[n]
        if isinstance(v, bool) or not isinstance(v, (int, float, np.integer, np.floating)) or not math.isfinite(v):
            raise SimplydataError(f"at_start= needs a number for {n}; it got {v!r}.")
    if exactly:
        t0 = _span(between, step, time, example)[0] if between is not None else 0.0
        if math.isinf(t0):
            raise SimplydataError("between= needs two numbers for the times (not infinity).")
        return _path_exactly(texts, names, letters, rights, time, at_start, t0, known, order)
    if between is None:
        raise SimplydataError(f"find_path_over_time() needs between=[first time, last time].\nFor example:  {example}")
    t0, t1 = _span(between, step, time, example)
    if math.isinf(t0) or math.isinf(t1):
        raise SimplydataError("between= needs two numbers for the times (not infinity).")
    key = PATH_SPELLINGS.get(str(test_method).strip().lower())
    if key is None:
        raise choice_error(step, "test_method", test_method, list(PATH_METHODS))
    times = None
    if time_step is not None:
        if isinstance(time_step, bool) or not isinstance(time_step, (int, float, np.integer, np.floating)) or \
                not time_step > 0:
            raise SimplydataError("time_step= needs a number above 0, such as time_step=0.5.")
        steps = (t1 - t0) / time_step
        if abs(steps - round(steps)) <= 1e-9 * max(1.0, steps):
            # the step fits the span: evenly spaced times that end exactly at the last time (never past it)
            times = np.linspace(t0, t1, int(round(steps)) + 1)
        else:
            times = t0 + time_step * np.arange(int(math.floor(steps)) + 1)
            times = times[times <= t1]
            print(f"Note: time_step={_show(time_step)} does not fit {_show(t0)} to {_show(t1)} a whole number of "
                  f"times, so the last time in the table is {_show(times[-1])}.")

    def change(t, y):
        values = dict(zip(letters, y))
        values[time] = t
        return [float(f({k: values[k] for k in f.names})) for f in formulas]

    events, stop_text = None, None
    start = [float(at_start[n]) for n in names]
    if stop_when is not None:
        rule_text = stop_when
        if order == 2 and isinstance(stop_when, str):  # dx/dt in the rule is the speed, as on the right side
            rule_text = re.sub(rf"\bd\s*{re.escape(names[0])}\s*/\s*d\s*{re.escape(time)}\b", letters[1],
                               stop_when)
        events, stop_text, holds = _stop_event(rule_text, letters, time, known)
        stop_text = stop_when.strip() if isinstance(stop_when, str) else stop_text
        if holds(t0, start):
            import pandas as pd

            from .table import Table

            print(f"{stop_text} is already true at the start ({time} = {_show(t0)}, "
                  + ", ".join(f"{n} = {_show(at_start[n])}" for n in names) + "), so the path stops there at once.")
            return Table(pd.DataFrame({"time": [t0], **{n: [float(at_start[n])] for n in names}}))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        found = integrate.solve_ivp(change, (t0, t1), start, method=PATH_SCIPY[key], t_eval=times, events=events,
                                    rtol=RTOL, atol=ATOL)
    if found.status < 0:
        raise SimplydataError(f"The solver stopped early: {found.message} Try test_method=\"stiff\", or a shorter "
                              "between=.")
    import pandas as pd

    from .table import Table

    data = {"time": found.t}
    for i, n in enumerate(names):
        data[n] = found.y[i]
    print(f"{'; '.join(texts)}: from {time} = {_show(t0)} to {_show(t1)}, starting at "
          + ", ".join(f"{n} = {_show(at_start[n])}" for n in names) + f"; {len(found.t)} times in the table"
          + (f" (every {_show(time_step)})" if time_step is not None else " (the solver's own steps; time_step= "
                                                                          "gives even ones)") + ".")
    if order == 2:
        print(f"The second-order equation was solved as two first-order ones, with the speed {names[1]} as a "
              "second changing value (it is in the table too).")
    if stop_text is not None:
        hit = found.t_events[0]
        if len(hit):
            print(f"Stopped when {stop_text}: at {time} = {_show(hit[0])}.")
        else:
            print(f"{stop_text} never came true before {time} = {_show(t1)}.")
    print(f"Method: SciPy integrate.solve_ivp, {PATH_METHODS[key]}, relative and absolute tolerance {RTOL:g} "
          "(as R deSolve::ode).")
    return Table(pd.DataFrame(data))


def _stop_event(stop_when, names, time, known):
    if not isinstance(stop_when, str):
        raise SimplydataError('stop_when= needs a rule in quotes, such as stop_when="N >= 900".')
    left, sign, right = split_equation(stop_when)
    rule = read_formula(f"({left}) - ({right})", known=known)
    other = [n for n in rule.names if n not in names and n != time]
    if other:
        raise SimplydataError(f"stop_when= uses {', '.join(other)}, which is not a changing value or the time.")

    def event(t, y):
        values = dict(zip(names, y))
        values[time] = t
        return float(rule({k: values[k] for k in rule.names}))

    event.terminal = True
    # >= and > come true when the difference rises through 0, <= and < when it falls through 0, = either way
    event.direction = {">=": 1, ">": 1, "<=": -1, "<": -1, "=": 0}[sign]

    def holds(t, y):
        gap = event(t, y)
        return {">=": gap >= 0, ">": gap > 0, "<=": gap <= 0, "<": gap < 0, "=": gap == 0}[sign]

    return [event], stop_when.strip(), holds


@one_deadline
def _path_exactly(texts, names, letters, rights, time, at_start, t0, known, order=1):
    from ._formula import EXACTLY_HINT, Formula, _guarded, exact_number, need_sympy, parse

    sp = need_sympy("find_path_over_time(exactly=True)")
    if len(texts) != 1:
        raise SimplydataError("exactly=True works with one equation; for several, leave it out and simplydata "
                              "finds the path in numbers.")
    values = _exact_values(sp, known)
    t = sp.Symbol(time)
    name = names[0]
    y = sp.Function(name)
    swaps = {sp.Symbol(name): y(t)}
    if order == 2:
        swaps[sp.Symbol(letters[1])] = y(t).diff(t)
    rhs = _exact_floats(sp, parse(rights[-1], "find_path_over_time()", values)).subs(swaps)
    start_time = exact_number(sp, t0)
    ics = None
    if at_start is not None:
        ics = {y(start_time): exact_number(sp, at_start[name])}
        if order == 2:
            ics[y(t).diff(t).subs(t, start_time)] = exact_number(sp, at_start[names[1]])
    equation = sp.Eq(y(t).diff(t, order), rhs)
    try:
        solved = _guarded(sp.dsolve, equation, y(t), ics=ics, what="SymPy dsolve", hint=EXACTLY_HINT)
    except (NotImplementedError, ValueError) as error:
        raise SimplydataError(f"SymPy found no formula for {texts[0]} ({error}). Leave out exactly=True for the "
                              "path in numbers.") from None
    if isinstance(solved, list):
        where = f"that starts at {name} = {at_start[name]}" if at_start is not None else "for it"
        raise SimplydataError(f"{texts[0]} has more than one formula {where}; leave out exactly=True for the path in "
                              "numbers.")
    if solved.lhs != y(t) or solved.rhs.has(y(t)):
        raise SimplydataError(f"SymPy could write the answer to {texts[0]} only as an equation, not as a formula for "
                              f"{name}: {solved.lhs} = {solved.rhs}. Leave out exactly=True for the path in numbers.")
    answer = _guarded(sp.simplify, solved.rhs, what="SymPy simplify", hint=EXACTLY_HINT)
    if at_start is None:
        constants = sorted((str(s) for s in answer.free_symbols if str(s).startswith("C") and str(s)[1:].isdigit()))
        print(f"{texts[0]}: {name} = {answer}   (SymPy dsolve, the general formula)")
        if constants:
            print(f"{' and '.join(constants)} {'is a constant' if len(constants) == 1 else 'are constants'} that any "
                  f"number fits; at_start= fixes {'it' if len(constants) == 1 else 'them'}.")
        return Formula(answer)
    starts = ", ".join(f"{n} = {exact_number(sp, at_start[n])}" for n in names)
    print(f"{texts[0]} with {starts} at {time} = {_show(t0)}: {name} = {answer}   (SymPy dsolve)")
    return Formula(answer)


# ---------------------------------------------------------------- sums of series (numbers phase, batch 4)
SUM_HINT = ("For the decimal of a finite sum, put the terms in numbers and add them: sdata.numbers(...) then "
            "find_total(). For the formula of the sum up to a letter, use between=[1, \"n\"].")
MAX_SUM_DIGITS = 100_000  # a finite sum whose terms have more digits than this is refused before SymPy adds them


def _sum_end(sp, value, own: dict, example: str):
    """One end of a sum: a whole number, "infinity" / "-infinity", or a letter (a sum up to n). A letter that is
    also a letter of the formula is that same letter (the formula's own SymPy Symbol)."""
    from ._formula import INFINITY, MINUS_INFINITY, parse

    words = f'between= takes whole numbers, "infinity" or a letter such as "n" for the ends'
    if isinstance(value, str):
        key = value.strip().lower()
        if key in INFINITY:
            return sp.oo
        if key in MINUS_INFINITY:
            return -sp.oo
        end = parse(value, "find_sum_of_series()")
        if not isinstance(end, sp.Symbol):
            raise SimplydataError(f'{words}; it got "{value}".\nFor example:  {example}')
        return own.get(str(end), sp.Symbol(str(end), integer=True))
    if isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool) and \
            math.isinf(float(value)):
        return sp.oo if value > 0 else -sp.oo
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)) or \
            not math.isfinite(float(value)) or float(value) != int(value):
        raise SimplydataError(f"{words}; it got {value!r}.\nFor example:  {example}")
    return sp.Integer(int(value))


def _agreeing(first: float, second: float) -> int:
    """How many leading significant digits two decimals share (0 when their signs or sizes differ)."""
    if first == second:
        return 17
    a, b = f"{first:.16e}", f"{second:.16e}"
    if a[0] != b[0] or a.split("e")[1] != b.split("e")[1]:
        return 0
    digits_a, digits_b = a.split("e")[0].replace("-", "").replace(".", ""), b.split("e")[0].replace("-", "").replace(".", "")
    count = 0
    for x, y in zip(digits_a, digits_b):
        if x != y:
            break
        count += 1
    return count


def _settled_decimal(sp, series, said: str):
    """The decimal of a series with no exact formula: SymPy evalf at 15 and at 30 digits of precision, and only the
    digits both give (less the last of them, which may still be on its way). A slowly settling series such as
    1/(k log(k)**2) gets only a few digits, or none."""
    from ._formula import _guarded

    first = _guarded(sp.N, series, 15, what="SymPy evalf", hint=SUM_HINT)
    second = _guarded(sp.N, series, 30, what="SymPy evalf", hint=SUM_HINT)
    if not (first.is_real and second.is_real):
        raise SimplydataError(f"{said}: SymPy found no exact formula, and its decimal is not an ordinary (real) "
                              f"number ({first}).")
    a, b = float(first), float(second)
    own = min(int(getattr(x, "_prec", 53) * math.log10(2)) for x in (first, second))
    kept = min(_agreeing(a, b), own) - 1
    if kept < 2:
        raise SimplydataError(f"{said}: SymPy found no exact formula, and its decimal does not settle to even two "
                              f"digits (it gives {a:.6g} at 15 digits of precision and {b:.6g} at 30). The series "
                              "settles too slowly for SymPy's evalf.")
    shown = min(kept, 10)
    value = float(f"{b:.{kept - 1}e}") if kept < 13 else b
    note = "" if kept >= 10 else (f"; only {kept} digits are sure: SymPy's evalf gives the same first digits at 15 "
                                  "and 30 digits of precision, and no more")
    print(f"{said}: SymPy found no exact formula; it settles at about {value:.{shown}g}{note}   (SymPy "
          "is_convergent and evalf)")
    return value


@friendly
@one_deadline
def find_sum_of_series(formula=None, between=None, for_letter=None, known=None):
    """The sum of a formula for every whole number from one end to the other (a series). sdata.find_sum_of_series("1/k**2", between=[1, "infinity"])

    sdata.find_sum_of_series("1/k**2", between=[1, "infinity"]) gives pi**2/6 (about 1.644934067). The ends are
    whole numbers, "infinity", or a letter: between=[1, "n"] gives the formula of the sum up to n. When the sum grows
    without end, or does not settle, simplydata says so. When SymPy finds no exact formula but the sum settles, the
    decimal is given, with only the digits SymPy is sure of. A sum that holds only under a condition (r**k, for
    |r| < 1) keeps the condition in its formula. for_letter= says which letter counts when there are several;
    known= fixes others. As SymPy summation(); MATLAB symsum. Gives a formula (or a number when only the decimal is
    known).
    """
    from ._formula import Formula, _guarded, _show as show, float_of, need_sympy, parse

    sp = need_sympy("sdata.find_sum_of_series()")
    example = 'sdata.find_sum_of_series("1/k**2", between=[1, "infinity"])'
    if formula is None:
        raise SimplydataError(f"find_sum_of_series() needs a formula in quotes.\nFor example:  {example}")
    values = _exact_values(sp, known)
    expr = _exact_floats(sp, parse(formula, "find_sum_of_series()", values))
    if hasattr(formula, "_expr") and values:
        named = {str(s): s for s in expr.free_symbols}
        expr = expr.subs({named[k]: v for k, v in values.items() if k in named})
    letters = sorted(str(s) for s in expr.free_symbols)
    if for_letter is None:
        if len(letters) != 1:
            raise SimplydataError(f"{show(expr)} has {len(letters)} letters ({', '.join(letters) or 'none'}): say "
                                  "which one counts with for_letter=, and fix the others with known= if they are "
                                  f'numbers.\nFor example:  sdata.find_sum_of_series("r**k", between=[0, "infinity"], '
                                  'for_letter="k")')
        for_letter = letters[0]
    if not isinstance(for_letter, str) or for_letter not in letters:
        raise SimplydataError(f"for_letter= needs one of the letters of {show(expr)} in quotes: "
                              f"{', '.join(repr(n) for n in letters) or 'none'}.")
    if isinstance(between, (str, bytes)) or not isinstance(between, (list, tuple)) or len(between) != 2:
        raise SimplydataError(f"find_sum_of_series() needs between= the first and the last whole number.\n"
                              f"For example:  {example}")
    own = {str(s): s for s in expr.free_symbols}
    low, high = (_sum_end(sp, v, own, example) for v in between)
    if for_letter in (str(low), str(high)):
        raise SimplydataError(f"between= cannot end at {for_letter}: that is the letter that counts.")
    if low.is_number and high.is_number and low > high:
        raise SimplydataError(f"between= must go from the smaller end to the bigger one; it was "
                              f"[{show(low)}, {show(high)}].")
    k = sp.Symbol(for_letter, integer=True)
    term = expr.subs(own[for_letter], k)
    said = (f"The sum of {formula.strip() if isinstance(formula, str) else show(expr)} for {k} from {show(low)} to "
            f"{show(high)}")
    finite = low.is_Integer and high.is_Integer
    if finite:
        _check_term_sizes(sp, term, k, (low, high), said)
    if finite and int(high) - int(low) + 1 > MAX_SUM_TERMS:
        return _long_sum(sp, term, k, low, high, said)
    found = _guarded(sp.summation, term, (k, low, high), what="SymPy summation", hint=SUM_HINT)
    if found == sp.oo or found == -sp.oo:
        print(f"{said} grows without end: the series does not settle on a number   (SymPy summation)")
        return math.inf if found == sp.oo else -math.inf
    if found is sp.nan or found.has(sp.nan, sp.zoo):
        print(f"{said} does not settle on a number   (SymPy summation)")
        return math.nan
    if isinstance(found, sp.Piecewise):
        pieces = [(e, c) for e, c in found.args if not e.has(sp.Sum)]
        if pieces:
            words = "; ".join(f"{show(e)} when {show(c)}" if c is not sp.true else show(e) for e, c in pieces)
            print(f"{said}: {words}; otherwise it does not settle   (SymPy summation)")
            print("The formula keeps the condition: f.find_value_at() gives no number where it does not hold.")
            return Formula(sp.Piecewise(*pieces, (sp.nan, True)))
    if found.has(sp.Sum):
        series = sp.Sum(term, (k, low, high))
        if high.is_infinite or low.is_infinite:
            try:
                settles = _guarded(series.is_convergent, what="SymPy is_convergent", hint=SUM_HINT)
            except NotImplementedError:
                settles = None
            if settles is False or settles == sp.false:
                print(f"{said} does not settle on a number   (SymPy is_convergent)")
                return math.nan
            if settles is not True and settles != sp.true:
                raise SimplydataError(f"{said}: SymPy found no exact formula and cannot tell whether the series "
                                      "settles.")
        if series.free_symbols:
            raise SimplydataError(f"{said}: SymPy found no exact formula. Give the other letters numbers with known= "
                                  "for a decimal.")
        return _settled_decimal(sp, series, said)
    about = f" (about {float_of(found, 'SymPy N', SUM_HINT):.10g})" if not found.free_symbols and found.is_real else ""
    print(f"{said}: {show(found)}{about}   (SymPy summation)")
    return Formula(found)


def _check_term_sizes(sp, term, k, ends, said: str) -> None:
    """Refuse a finite sum whose terms at its ends have more than MAX_SUM_DIGITS digits (2**(2**k) up to 36), before
    SymPy adds them: worked out as decimals by SymPy evalf, which keeps only the size of such a number."""
    from ._formula import _guarded

    for end in ends:
        try:
            size = _guarded(term.evalf, 15, subs={k: end}, what="SymPy evalf", hint=SUM_HINT)
        except (ValueError, TypeError, ZeroDivisionError):
            continue
        if size.is_number and size.is_finite and size != 0:
            digits = _guarded(sp.log, sp.Abs(size), 10, what="SymPy log", hint=SUM_HINT)
            if digits.is_real and digits > MAX_SUM_DIGITS:
                raise SimplydataError(f"{said}: the term at {k} = {end} has about {int(digits):,} digits, too big to "
                                      f"add up exactly (simplydata takes terms of up to {MAX_SUM_DIGITS} digits).")


def _long_sum(sp, term, k, low, high, said: str):
    """A finite sum of more than MAX_SUM_TERMS terms: SymPy's formula of the sum up to a letter, never term by term.
    A polynomial formula is worked out exactly; any other (harmonic numbers, zeta) only as a decimal, with the end
    put in as a decimal number, since its exact fraction would have millions of digits."""
    from ._formula import Formula, _guarded, _show as show, float_of

    last = sp.Dummy("last", integer=True)
    general = _guarded(sp.summation, term, (k, low, last), what="SymPy summation", hint=SUM_HINT)
    if general.has(sp.Sum):
        raise SimplydataError(f"{said}: SymPy found no exact formula, and simplydata does not add more than "
                              f"{MAX_SUM_TERMS:,} terms one by one. Use a shorter range, or numbers words: "
                              "sdata.numbers(...) then find_total().")
    if general.is_polynomial(last):
        found = _guarded(general.subs, last, high, what="SymPy subs", hint=SUM_HINT)
        about = f" (about {float_of(found, 'SymPy N', SUM_HINT):.10g})" if found.is_real else ""
        print(f"{said}: {show(found)}{about}   (SymPy summation, the formula of the sum up to {k} = {high})")
        return Formula(found)
    decimal = _guarded(general.subs, last, sp.Float(int(high), 30), what="SymPy subs", hint=SUM_HINT)
    value = float_of(decimal, "SymPy N", SUM_HINT)
    print(f"{said}: about {value:.10g}   (SymPy summation gives the formula {show(general.subs(last, sp.Symbol('n')))} "
          f"for the sum up to n; at n = {high} its exact fraction is too long to write, so the decimal is given)")
    return value
