"""The path between two ends: values given at both ends of a range (families for 100 %, batch 15).

sdata.find_path_between_ends("d2y/dx2 = -y", at_ends={"y": [0, 1]}, between=[0, 1.5]) finds the path of y whose
slope of the slope is -y, starting at y = 0 and ending at y = 1 (a boundary value problem). Unlike
find_path_over_time, which starts from every value at the first time, some values here are known only at the last
end: a beam fixed at both walls, a temperature held at both ends of a rod, a shot that must land on a target.
SciPy integrate.solve_bvp does the work (4th-order collocation with control of the residual, Kierzenka and Shampine
2001, as MATLAB bvp4c and R bvpSolve::bvpcol()), to a tolerance of 1e-8. Approved by Manish 2026-11-28 (plan
section 2.6).
"""

from __future__ import annotations

import math
import warnings

import numpy as np

from ._calculus import _read_changes, _show, _span
from ._errors import SimplydataError, friendly

POINTS = 101  # places in the table when step= is not given
TOLERANCE = 1e-8
MAX_NODES = 100_000


@friendly(others={"bc": "at_ends", "boundary": "at_ends", "x": "between"})
def find_path_between_ends(equations=None, at_ends=None, between=None, known=None, step=None):
    """Path between two ends. sdata.find_path_between_ends("d2y/dx2 = -y", at_ends={"y": [0, 1]}, between=[0, 1])

    path = sdata.find_path_between_ends("d2y/dx2 = -y", at_ends={"y": [0, 1]}, between=[0, 1.5])

    The equations say how fast each value changes, as in find_path_over_time ("dy/dx = ..." in a list, or one
    "d2y/dx2 = ..." for the slope of the slope). at_ends= gives the known values at the two ends: {"y": [0, 1]}
    is y = 0 at the first end and y = 1 at the last; None leaves an end free ({"y": [0, None], "dy/dx": [None,
    2]}). There must be as many known values as values that change (two for one d2y/dx2 equation). between= is the
    first and last place, known= fixes other letters, step= the gap between the places in the table (else 101
    evenly spaced places). SciPy integrate.solve_bvp (collocation, tolerance 1e-8, as MATLAB bvp4c and R
    bvpSolve::bvpcol()); the sentence says whether it settled, after how many steps and on how many points.
    Gives back a table: the place, then each value that changes.
    """
    from scipy import integrate

    word = "find_path_between_ends"
    example = 'path = sdata.find_path_between_ends("d2y/dx2 = -y", at_ends={"y": [0, 1]}, between=[0, 1.5])'
    if not (isinstance(equations, str) or (isinstance(equations, (list, tuple)) and equations and
                                           all(isinstance(e, str) for e in equations))):
        raise SimplydataError(f"{word}() needs an equation such as \"d2y/dx2 = -y\" in quotes, or a list of them "
                              f"(\"dy/dx = ...\").\nFor example:  {example}")
    texts, names, letters, rights, formulas, place, order = _read_changes(equations, known, example)
    if between is None:
        raise SimplydataError(f"{word}() needs between=[first, last]: the two ends.\nFor example:  {example}")
    low, high = _span(between, word, place, example)
    if math.isinf(low) or math.isinf(high):
        raise SimplydataError("between= needs two numbers for the ends (not infinity).")
    if not isinstance(at_ends, dict) or not at_ends:
        raise SimplydataError(f"{word}() needs at_ends= with the known values at the two ends, such as "
                              f'at_ends={{"{names[0]}": [0, 1]}}.\nFor example:  {example}')
    extra = [k for k in at_ends if k not in names]
    if extra:
        raise SimplydataError(f"at_ends= has {', '.join(map(str, extra))}, which does not change; the values that "
                              f"change: {', '.join(names)}.")
    given = []  # (index of the value, 0 for the first end or 1 for the last, the value)
    for name, pair in at_ends.items():
        if isinstance(pair, (str, bytes)) or not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise SimplydataError(f'at_ends= needs two values for {name}, at the first and the last end (None for a '
                                  f'free end), such as at_ends={{"{name}": [0, 1]}}.')
        for end, value in enumerate(pair):
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)) or \
                    not math.isfinite(value):
                raise SimplydataError(f"at_ends= needs numbers (or None for a free end); {name} has {value!r}.")
            given.append((names.index(name), end, float(value)))
    if len(given) != len(names):
        raise SimplydataError(
            f"at_ends= needs as many known values as values that change ({len(names)}: {', '.join(names)}); it has "
            f"{len(given)}. " + ("A d2y/dx2 equation needs two, such as one value at each end."
                                 if order == 2 else "Give one known value for each equation."))
    if step is not None:
        if isinstance(step, bool) or not isinstance(step, (int, float, np.integer, np.floating)) or not step > 0:
            raise SimplydataError("step= needs a number above 0, such as step=0.1.")
        count = (high - low) / step
        if abs(count - round(count)) > 1e-9 * max(1.0, count):
            raise SimplydataError(f"step={_show(step)} does not fit {_show(low)} to {_show(high)} a whole number of "
                                  "times; choose a step that does, so that both ends are in the table.")
        places = np.linspace(low, high, int(round(count)) + 1)
    else:
        places = np.linspace(low, high, POINTS)
    calls = [0]

    def change(x, values):
        calls[0] += 1
        found = dict(zip(letters, values))
        found[place] = x
        return np.vstack([np.broadcast_to(np.asarray(f({k: found[k] for k in f.names}), dtype=float), x.shape)
                          for f in formulas])

    def ends(first, last):
        return np.array([(first if end == 0 else last)[i] - value for i, end, value in given])

    guess = np.zeros((len(names), places.size))  # a straight line between known ends, else level
    for i in range(len(names)):
        at = {end: value for j, end, value in given if j == i}
        if 0 in at and 1 in at:
            guess[i] = at[0] + (at[1] - at[0]) * (places - low) / (high - low)
            if order == 2 and i == 0:
                guess[1] = (at[1] - at[0]) / (high - low)
        elif at:
            guess[i] = next(iter(at.values()))
    with warnings.catch_warnings(), np.errstate(all="ignore"):
        warnings.simplefilter("ignore")
        found = integrate.solve_bvp(change, ends, places, guess, tol=TOLERANCE, max_nodes=MAX_NODES)
    if not found.success:
        raise SimplydataError(f"The path between the ends did not settle: {found.message} Check that the ends can be "
                              "reached (some problems have no path, or several), or try a shorter between=.")
    values = found.sol(places)
    import pandas as pd

    from .table import Table

    data = {place: places}
    for i, n in enumerate(names):
        data[n] = values[i]
    known_words = "; ".join(f"{names[i]} = {_show(v)} at the {'first' if end == 0 else 'last'} end"
                            for i, end, v in sorted(given, key=lambda g: (g[1], g[0])))
    print(f"{'; '.join(texts)}: from {place} = {_show(low)} to {_show(high)}, with {known_words}; {places.size} places "
          "in the table.")
    if order == 2:
        print(f"The second-order equation was solved as two first-order ones, with the slope {names[1]} as a second "
              "changing value (it is in the table too).")
    print(f"Method: SciPy integrate.solve_bvp (4th-order collocation with control of the residual, Kierzenka and "
          f"Shampine 2001), tolerance {TOLERANCE:g}, as MATLAB bvp4c and R bvpSolve::bvpcol().")
    print(f"Search: collocation; it settled (converged) after {int(found.niter):,} steps on {found.x.size:,} points "
          f"(largest residual {float(np.max(found.rms_residuals)):.2g}), and the equations were worked out "
          f"{calls[0]:,} times.")
    return Table(pd.DataFrame(data))
