"""Families for 100 %, batch 19 (approved by Manish 2026-11-28, plan section 2.8): sdata.solve_matrix_equation, one
family word for the matrix equations of SciPy linalg (Lyapunov, Sylvester and Riccati), whose answer is a grid X.

Every number comes from SciPy linalg: solve_continuous_lyapunov (solve_lyapunov), solve_discrete_lyapunov,
solve_sylvester, solve_continuous_are and solve_discrete_are. Own code is glue only: checks, the equation in words and
how far the answer is from fitting it (NumPy matrix products).
"""

from __future__ import annotations

import numpy as np

from ._errors import SimplydataError, choice_error, friendly

# kind -> (SciPy function, the grids it needs, the equation in words)
EQUATIONS = {
    "lyapunov": ("solve_continuous_lyapunov", ("a", "q"), "a X + X at = q"),
    "discrete lyapunov": ("solve_discrete_lyapunov", ("a", "q"), "a X at - X + q = 0"),
    "sylvester": ("solve_sylvester", ("a", "b", "q"), "a X + X b = q"),
    "riccati": ("solve_continuous_are", ("a", "b", "q", "r"),
                "at X + X a - X b (r's inverse) bt X + q = 0"),
    "discrete riccati": ("solve_discrete_are", ("a", "b", "q", "r"),
                         "at X a - X - (at X b) (r + bt X b)'s inverse (bt X a) + q = 0"),
}
SPELLINGS = {"continuous lyapunov": "lyapunov", "solve_lyapunov": "lyapunov", "solve_continuous_lyapunov": "lyapunov",
             "lyap": "lyapunov", "solve_discrete_lyapunov": "discrete lyapunov", "dlyap": "discrete lyapunov",
             "solve_sylvester": "sylvester", "continuous riccati": "riccati", "solve_continuous_are": "riccati",
             "care": "riccati", "are": "riccati", "solve_discrete_are": "discrete riccati", "dare": "discrete riccati"}
EXAMPLE = 'sdata.solve_matrix_equation("lyapunov", a=grid, q=other_grid)'


def _grid_values(value, name: str):
    """One of the grids a=, b=, q=, r= as decimals (a grid made with sdata.number_grid, or rows of numbers)."""
    values = value._values if hasattr(value, "_values") else value
    try:
        values = np.asarray(values, dtype=float)
    except (TypeError, ValueError):
        values = np.asarray([[np.nan]])
    if values.ndim != 2 or values.size == 0 or not np.isfinite(values).all():
        raise SimplydataError(f"{name}= needs a grid of numbers with a number in every cell (made with "
                              f"sdata.number_grid).\nFor example:  {EXAMPLE}")
    return values


@friendly(renamed={"equation": "kind"})
def solve_matrix_equation(kind=None, a=None, b=None, q=None, r=None):
    """Solve a matrix equation for the grid X: Lyapunov, Sylvester or Riccati. sdata.solve_matrix_equation("lyapunov", a=grid, q=other_grid)

    kind= "lyapunov" (a X + X at = q, at is a with rows and columns swapped; SciPy linalg.solve_continuous_lyapunov),
    "discrete lyapunov" (a X at - X + q = 0; solve_discrete_lyapunov), "sylvester" (a X + X b = q;
    solve_sylvester), "riccati" (the continuous algebraic Riccati equation of control, with b, q and r;
    solve_continuous_are) or "discrete riccati" (solve_discrete_are). Give the grids with a=, b=, q= and r=. Gives
    back X as a grid and says how far it is from fitting the equation. Lyapunov equations give the variance of a
    system driven by noise and Riccati equations the best feedback of a controller (R control::lyap, dlyap, care;
    MATLAB lyap, dlyap, sylvester, icare, idare). SciPy's names (solve_lyapunov ...) work too.
    """
    from scipy import linalg

    from .numbers.numbers import NumberGrid

    step = "solve_matrix_equation"
    if not isinstance(kind, str):
        raise SimplydataError(f"{step}() needs the kind of equation, one of: "
                              + ", ".join(f'"{k}"' for k in EQUATIONS) + f".\nFor example:  {EXAMPLE}")
    chosen = SPELLINGS.get(kind.strip().lower(), kind.strip().lower())
    if chosen not in EQUATIONS:
        raise choice_error(step, "kind", kind, list(EQUATIONS))
    scipy_name, needed, words = EQUATIONS[chosen]
    given = {"a": a, "b": b, "q": q, "r": r}
    missing = [name for name in needed if given[name] is None]
    if missing:
        raise SimplydataError(f'kind="{chosen}" ({words}) needs ' + ", ".join(f"{m}=" for m in needed)
                              + "; " + ", ".join(f"{m}=" for m in missing) + " " + ("is" if len(missing) == 1 else
                                                                                   "are") + " missing.")
    extra = [name for name, value in given.items() if value is not None and name not in needed]
    if extra:
        raise SimplydataError(f'kind="{chosen}" ({words}) takes ' + ", ".join(f"{m}=" for m in needed)
                              + " only; leave out " + ", ".join(f"{m}=" for m in extra) + ".")
    grids = {name: _grid_values(given[name], name) for name in needed}
    for name in ("a", "b") if chosen == "sylvester" else ("a", "q", "r"):  # Sylvester's q may be any shape
        if name in grids and grids[name].shape[0] != grids[name].shape[1]:
            raise SimplydataError(f"{name}= needs a square grid; it is {grids[name].shape[0]} x "
                                  f"{grids[name].shape[1]}.")
    try:
        found = getattr(linalg, scipy_name)(*(grids[name] for name in needed))
    except (ValueError, linalg.LinAlgError) as problem:
        raise SimplydataError(f"SciPy linalg.{scipy_name} found no answer: {str(problem).splitlines()[0]}") from None
    found = np.real_if_close(np.asarray(found))
    if np.iscomplexobj(found):
        raise SimplydataError(f"The answer of SciPy linalg.{scipy_name} has complex numbers; a grid holds real "
                              "numbers only.")
    a_, q_ = grids["a"], grids["q"]
    left = {"lyapunov": lambda x: a_ @ x + x @ a_.T - q_,
            "discrete lyapunov": lambda x: a_ @ x @ a_.T - x + q_,
            "sylvester": lambda x: a_ @ x + x @ grids["b"] - q_}.get(chosen)
    print(f"X solves {words} (SciPy linalg.{scipy_name}): a {found.shape[0]} x {found.shape[1]} grid."
          + (f" The size left over (the biggest difference between the two sides) is "
             f"{float(np.max(np.abs(left(found)))):.3g}." if left is not None else ""))
    return NumberGrid(np.asarray(found, dtype=float))
