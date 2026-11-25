"""Areas, volumes and paths over time from a formula: sdata.find_area_under, find_volume_under, find_path_over_time.

Every number comes from SciPy (and SymPy for exactly=True):

* find_area_under: integrate.quad (QUADPACK, as R integrate()); test_method="gauss" is integrate.fixed_quad (5-point
  Gauss-Legendre); exactly=True: sympy.integrate;
* find_volume_under: integrate.dblquad (two letters), tplquad (three), nquad (more), the letters in the order of
  between= (the first is the outer one) and handed to SciPy in its own reversed order;
* find_path_over_time: integrate.solve_ivp (RK45 by default; LSODA, Radau, BDF, DOP853, RK23), with the relative and
  absolute tolerances of R deSolve (1e-6), t_eval from time_step= and a stopping event from stop_when=;
  exactly=True: sympy.dsolve.

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
        (value, error), notes = _quiet(integrate.quad, curve, low, high)
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


def _area_exactly(text, name, low, high, known):
    from ._formula import Formula, need_sympy, parse

    sp = need_sympy("find_area_under(exactly=True)")
    from ._maths_formula import _known_values

    values = {k: sp.nsimplify(v, rational=True) for k, v in _known_values(known).items()}
    expr = parse(text, "find_area_under()", values)
    x = sp.Symbol(name)

    def end(v):
        return sp.oo if v == math.inf else (-sp.oo if v == -math.inf else sp.nsimplify(v, rational=True))

    found = sp.integrate(expr, (x, end(low), end(high)))
    if found.has(sp.Integral):
        raise SimplydataError(f"SymPy found no exact area under {text}; without exactly=True simplydata gives it as "
                              "a decimal.")
    decimal = sp.N(found)
    print(f"The area under {text} for {name} from {_show(low)} to {_show(high)}: {found} (about {decimal}).")
    print("Method: SymPy integrate, exact.")
    return Formula(found)


@friendly
def find_volume_under(formula=None, between=None, known=None):
    """The volume under a formula of two or more letters, over a range of each (a double or triple integral).

    sdata.find_volume_under("x * y", between={"x": [0, 1], "y": [0, 2]})   (1)
    between= gives a range for each letter; the first letter is the outer one. Two letters: SciPy
    integrate.dblquad; three: tplquad; more: nquad (the total under the surface). Ends can be "infinity".
    """
    from scipy import integrate

    step = "find_volume_under"
    example = 'sdata.find_volume_under("x * y", between={"x": [0, 1], "y": [0, 2]})'
    if formula is None:
        raise SimplydataError(f"find_volume_under() needs a formula in quotes.\nFor example:  {example}")
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
    ranges = ", ".join(f"{n} from {_show(lo)} to {_show(hi)}" for n, (lo, hi) in zip(order, spans))
    print(f"The volume under {text} for {ranges}: {_show(value)} (error below {error:.2g}).")
    print(f"Method: {how}; {order[0]} is the outer letter.")
    for note in notes:
        print(f"Note from SciPy: {note}")
    return float(value)


# ---------------------------------------------------------------- paths over time
def _read_changes(equations, known, example):
    if isinstance(equations, str):
        texts = [equations]
    elif isinstance(equations, (list, tuple)) and equations and all(isinstance(e, str) for e in equations):
        texts = list(equations)
    else:
        raise SimplydataError(f"find_path_over_time() needs an equation such as \"dN/dt = r * N\" in quotes, or a "
                              f"list of them.\nFor example:  {example}")
    names, rights, time = [], [], None
    for text in texts:
        left, sign, right = split_equation(text)
        found = _DERIVATIVE.match(left)
        if sign != "=" or not found:
            raise SimplydataError(f'"{text}" should say how fast something changes, such as "dN/dt = r * N": the '
                                  f"left side is d, a letter, /d and the time letter.\nFor example:  {example}")
        name, letter = found.groups()
        if time is not None and letter != time:
            raise SimplydataError(f"Every equation needs the same time letter; one uses d{time} and one d{letter}.")
        if name == letter:
            raise SimplydataError(f'"{text}": what changes and the time letter cannot be the same letter.')
        if name in names:
            raise SimplydataError(f"{name} has two equations; give one for each letter that changes.")
        time = letter
        names.append(name)
        rights.append(right)
    formulas = [read_formula(r, known=known) for r in rights]
    allowed = set(names) | {time}
    for text, f in zip(texts, formulas):
        other = [n for n in f.names if n not in allowed]
        if other:
            raise SimplydataError(f"{text} uses {', '.join(other)}, which {'is' if len(other) == 1 else 'are'} not "
                                  f"changing and has no value. Give {'it' if len(other) == 1 else 'them'} with "
                                  f"known=, for example known={{{', '.join(repr(n) + ': 0.3' for n in other)}}}.")
    return texts, names, rights, formulas, time


@friendly(renamed={"method": "test_method"})
def find_path_over_time(equations=None, at_start=None, between=None, known=None, time_step=None, stop_when=None,
                        test_method="RK45", exactly=False):
    """The values over time from how fast they change (an ordinary differential equation). sdata.find_path_over_time("dN/dt = r * N * (1 - N / K)", at_start={"N": 10}, between=[0, 50], known={"r": 0.3, "K": 1000}, time_step=0.5)

    Gives back a table: time, then each value that changes. Write each equation as "dN/dt = ..."; several
    equations in a list change together (predator and prey). at_start= gives each value at the first time,
    between= the first and last time, known= the fixed values, time_step= the times in the table (else the
    solver's own steps). stop_when="N >= 900" stops when that comes true. SciPy integrate.solve_ivp,
    test_method="RK45" (the default), "LSODA", "stiff" (Radau), "BDF", "DOP853" or "RK23", with the tolerances
    of R deSolve (1e-6). exactly=True gives the formula from SymPy dsolve (one equation; simplydata[exact]).
    """
    from scipy import integrate

    step = "find_path_over_time"
    example = ('sdata.find_path_over_time("dN/dt = r * N * (1 - N / K)", at_start={"N": 10}, between=[0, 50], '
               'known={"r": 0.3, "K": 1000}, time_step=0.5)')
    texts, names, rights, formulas, time = _read_changes(equations, known, example)
    if not isinstance(at_start, dict):
        raise SimplydataError(f"find_path_over_time() needs at_start= with the first value of "
                              f"{', '.join(names)}.\nFor example:  {example}")
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
    if between is None:
        raise SimplydataError(f"find_path_over_time() needs between=[first time, last time].\nFor example:  {example}")
    t0, t1 = _span(between, step, time, example)
    if math.isinf(t0) or math.isinf(t1):
        raise SimplydataError("between= needs two numbers for the times (not infinity).")
    if not isinstance(exactly, bool):
        raise SimplydataError("exactly= should be True or False.")
    if exactly:
        return _path_exactly(texts, names, rights, time, at_start, t0, known)
    key = PATH_SPELLINGS.get(str(test_method).strip().lower())
    if key is None:
        raise choice_error(step, "test_method", test_method, list(PATH_METHODS))
    times = None
    if time_step is not None:
        if isinstance(time_step, bool) or not isinstance(time_step, (int, float, np.integer, np.floating)) or \
                not time_step > 0:
            raise SimplydataError("time_step= needs a number above 0, such as time_step=0.5.")
        count = int(math.floor((t1 - t0) / time_step + 1e-9))
        times = t0 + time_step * np.arange(count + 1)

    def change(t, y):
        values = dict(zip(names, y))
        values[time] = t
        return [float(f({k: values[k] for k in f.names})) for f in formulas]

    events, stop_text = None, None
    if stop_when is not None:
        events, stop_text = _stop_event(stop_when, names, time, known)
    start = [float(at_start[n]) for n in names]
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
    event.direction = {">=": 1, ">": 1, "<=": -1, "<": -1, "=": 0}[sign]
    return [event], stop_when.strip()


def _path_exactly(texts, names, rights, time, at_start, t0, known):
    from ._formula import Formula, need_sympy, parse
    from ._maths_formula import _known_values

    sp = need_sympy("find_path_over_time(exactly=True)")
    if len(names) != 1:
        raise SimplydataError("exactly=True works with one equation; for several, leave it out and simplydata "
                              "finds the path in numbers.")
    values = {k: sp.nsimplify(v, rational=True) for k, v in _known_values(known).items()}
    t = sp.Symbol(time)
    y = sp.Function(names[0])
    rhs = parse(rights[0], "find_path_over_time()", values).subs(sp.Symbol(names[0]), y(t))
    start = sp.nsimplify(at_start[names[0]], rational=True)
    try:
        solved = sp.dsolve(sp.Eq(y(t).diff(t), rhs), y(t), ics={y(sp.nsimplify(t0, rational=True)): start})
    except (NotImplementedError, ValueError) as error:
        raise SimplydataError(f"SymPy found no formula for {texts[0]} ({error}). Leave out exactly=True for the "
                              "path in numbers.") from None
    if isinstance(solved, list):
        raise SimplydataError(f"{texts[0]} has more than one formula that starts at {names[0]} = {start}; leave out "
                              "exactly=True for the path in numbers.")
    if solved.lhs != y(t) or solved.rhs.has(y(t)):
        raise SimplydataError(f"SymPy could write the answer to {texts[0]} only as an equation, not as a formula for "
                              f"{names[0]}: {solved.lhs} = {solved.rhs}. Leave out exactly=True for the path in "
                              "numbers.")
    answer = sp.simplify(solved.rhs)
    print(f"{texts[0]} with {names[0]} = {start} at {time} = {_show(t0)}: {names[0]} = {answer}   (SymPy dsolve)")
    return Formula(answer)
