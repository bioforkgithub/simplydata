"""The best way to pair the rows of a grid of costs with its columns (families for 100 %, batch 14).

sdata.find_best_pairing(costs) pairs each row (a worker, a ship, a sample) with one column (a job, a berth, a
machine) so that the total cost of the pairs is as small as possible, each row and each column used at most once:
the linear assignment problem, solved exactly by SciPy optimize.linear_sum_assignment (the shortest augmenting path
of Crouse 2016), as R lpSolve::lp.assign() and clue::solve_LSAP(). aim_for="biggest total" pairs for the biggest
total instead (scores rather than costs). An empty cell (None or NaN) is a pair that is not allowed.

with_distances= gives the quadratic assignment problem instead: costs= is then the flow between each pair of items
(how much goes from one to the other) and with_distances= the distance between each pair of places, and each item
gets a place so that the total of flow times distance is smallest (SciPy optimize.quadratic_assignment, the Fast
Approximate QAP method of Vogelstein et al. 2015, or test_method="2-opt"). That problem is hard: the answer is a
good one, not one proven to be the best. Approved by Manish 2026-11-28 (plan section 2.6).
"""

from __future__ import annotations

import numpy as np

from ._errors import SimplydataError, choice_error, friendly

AIMS = {"smallest total": False, "biggest total": True, "smallest": False, "biggest": True, "lowest total": False,
        "highest total": True, "minimum": False, "maximum": True, "min": False, "max": True}
QAP_METHODS = {"faq": ("faq", "the Fast Approximate QAP method (Vogelstein et al. 2015)"),
               "2-opt": ("2opt", "the 2-opt method (swaps of two places until no swap helps)")}
QAP_SPELLINGS = {"fast approximate": "faq", "fast approximate qap": "faq", "2opt": "2-opt", "two-opt": "2-opt",
                 "2 opt": "2-opt"}
SEED = 1
SHOWN = 10  # pairs written out in the sentence; the table has them all


def _show(x) -> str:
    return f"{float(x):.6g}"


def _grid_of(values, what: str, example: str):
    """(numbers as a 2-D float array, row names, column names) from a grid, a table, a list of lists or a NumPy
    array. A table's first column of text names the rows; its number columns are the columns."""
    rows = columns = None
    if hasattr(values, "as_pandas") and hasattr(values, "_frame"):  # a simplydata table
        frame = values.as_pandas()
        text = [c for c in frame.columns if frame[c].dtype.kind not in "iufb"]
        if text:
            rows = [str(v) for v in frame[text[0]]]
            frame = frame.drop(columns=text[0])
        if any(frame[c].dtype.kind not in "iuf" for c in frame.columns):
            raise SimplydataError(f"{what} needs number columns (and at most one column of names first).\n"
                                  f"For example:  {example}")
        columns = [str(c) for c in frame.columns]
        numbers = frame.to_numpy(dtype=float)
    else:
        if hasattr(values, "as_numpy"):
            values = values.as_numpy()
        try:
            numbers = np.array([[np.nan if v is None else v for v in row] for row in values], dtype=float)
        except (TypeError, ValueError):
            raise SimplydataError(f"{what} needs a grid of numbers: sdata.number_grid([[...], [...]]), a list of "
                                  f"rows, or a table.\nFor example:  {example}") from None
    if numbers.ndim != 2 or numbers.size == 0:
        raise SimplydataError(f"{what} needs a grid of numbers with rows and columns.\nFor example:  {example}")
    if np.isinf(numbers).any():
        raise SimplydataError(f"{what} has an infinite number; leave a pair that is not allowed empty (None).")
    rows = rows or [str(i + 1) for i in range(numbers.shape[0])]
    columns = columns or [str(j + 1) for j in range(numbers.shape[1])]
    return numbers, rows, columns


@friendly(renamed={"method": "test_method"}, pointers={"maximize": 'aim_for="biggest total"'},
          others={"cost_matrix": "costs"})
def find_best_pairing(costs=None, aim_for="smallest total", with_distances=None, test_method=None, fast=False):
    """Pair each row with one column for the smallest total. pairs = sdata.find_best_pairing([[4, 1], [2, 3]])

    pairs = sdata.find_best_pairing(sdata.number_grid([[4, 1, 3], [2, 0, 5], [3, 2, 2]]))
    costs= is a grid of numbers (sdata.number_grid, a list of rows, or a table whose first column of text names the
    rows): the cost of pairing each row (a worker) with each column (a job). Each row gets at most one column and
    each column at most one row; with more columns than rows some columns stay free. An empty cell (None) is a pair
    that is not allowed. The answer is exact: SciPy optimize.linear_sum_assignment, as R lpSolve::lp.assign().
    aim_for="biggest total" makes the total as big as possible (scores instead of costs). Gives back a table with
    one row per pair (row, column, cost) and prints the pairs and the total.
    with_distances=grid pairs items with places instead (the quadratic assignment problem): costs= is then the flow
    between each two items and with_distances= the distance between each two places, and the total of flow times
    distance is made smallest (SciPy optimize.quadratic_assignment, test_method="faq", the default, or "2-opt";
    a good answer, not one proven to be the best). fast=True gives a Polars table.
    """
    from scipy import optimize

    example = "pairs = sdata.find_best_pairing(sdata.number_grid([[4, 1, 3], [2, 0, 5], [3, 2, 2]]))"
    if costs is None:
        raise SimplydataError(f"find_best_pairing() needs a grid of costs: one row for each thing to pair, one "
                              f"column for each thing to pair it with.\nFor example:  {example}")
    if not isinstance(aim_for, str) or aim_for.strip().lower() not in AIMS:
        raise choice_error("find_best_pairing", "aim_for", aim_for, ["smallest total", "biggest total"])
    biggest = AIMS[aim_for.strip().lower()]
    if not isinstance(fast, bool):
        raise SimplydataError("fast= should be True or False.")
    numbers, rows, columns = _grid_of(costs, "costs=", example)
    if with_distances is not None:
        return _quadratic(numbers, rows, with_distances, biggest, test_method, fast)
    if test_method is not None:
        raise SimplydataError("test_method= chooses the method for with_distances= (the quadratic assignment "
                              "problem); the pairing of costs alone is always solved exactly.")
    allowed = np.isfinite(numbers)
    work = np.where(allowed, numbers, -np.inf if biggest else np.inf)
    try:
        row_at, column_at = optimize.linear_sum_assignment(work, maximize=biggest)
    except ValueError:
        raise SimplydataError("No pairing uses only allowed pairs (the empty cells leave some row or column with no "
                              "partner). Allow more pairs, or remove that row.") from None
    picked = numbers[row_at, column_at]
    total = float(picked.sum())
    pairs = [f"{rows[i]} with {columns[j]} ({_show(c)})" for i, j, c in zip(row_at, column_at, picked)]
    more = f" ... and {len(pairs) - SHOWN} more pairs (all in the table)" if len(pairs) > SHOWN else ""
    word = "biggest" if biggest else "smallest"
    print(f"The best pairing ({word} total): " + "; ".join(pairs[:SHOWN]) + more + f". Total {_show(total)}.")
    free = numbers.shape[1] - len(column_at) if numbers.shape[1] > numbers.shape[0] else 0
    if free:
        print(f"{free} column{'s stay' if free > 1 else ' stays'} free: there are more columns than rows.")
    elif numbers.shape[0] > numbers.shape[1]:
        left = numbers.shape[0] - len(row_at)
        print(f"{left} row{'s stay' if left > 1 else ' stays'} without a partner: there are more rows than columns.")
    print(f"Method: the linear assignment problem, solved exactly (SciPy optimize.linear_sum_assignment, shortest "
          f"augmenting path), as R lpSolve::lp.assign(costs{', direction = \"max\"' if biggest else ''}).")
    import pandas as pd

    from .table import table

    frame = pd.DataFrame({"row": [rows[i] for i in row_at], "column": [columns[j] for j in column_at],
                          "cost": picked.astype(float)})
    return table(frame, fast=fast)


def _quadratic(flows, items, with_distances, biggest, test_method, fast):
    from scipy import optimize

    example = ("sdata.find_best_pairing(flows, with_distances=distances), both square grids of the same size, such "
               "as sdata.number_grid([[0, 5, 2], [5, 0, 3], [2, 3, 0]])")
    distances, places, _ = _grid_of(with_distances, "with_distances=", example)
    n = flows.shape[0]
    if flows.shape != (n, n) or distances.shape != (n, n):
        raise SimplydataError(f"With with_distances=, costs= (the flow between each two items) and with_distances= "
                              f"(the distance between each two places) must be square grids of the same size; they "
                              f"are {flows.shape[0]} by {flows.shape[1]} and {distances.shape[0]} by "
                              f"{distances.shape[1]}.\nFor example:  {example}")
    if not (np.isfinite(flows).all() and np.isfinite(distances).all()):
        raise SimplydataError("With with_distances= every cell needs a number (no empty cells).")
    key = "faq" if test_method is None else str(test_method).strip().lower().replace("_", " ")
    key = QAP_SPELLINGS.get(key, key)
    if key not in QAP_METHODS:
        raise choice_error("find_best_pairing", "test_method", test_method, list(QAP_METHODS))
    scipy_name, words = QAP_METHODS[key]
    options = {"maximize": biggest}
    if scipy_name == "2opt":
        options["rng"] = np.random.default_rng(SEED)
    found = optimize.quadratic_assignment(flows, distances, method=scipy_name, options=options)
    place_of = np.asarray(found.col_ind)
    total = float(found.fun)
    pairs = [f"{items[i]} at {places[place_of[i]]}" for i in range(n)]
    more = f" ... and {n - SHOWN} more (all in the table)" if n > SHOWN else ""
    word = "biggest" if biggest else "smallest"
    print(f"A good placing ({word} total of flow times distance): " + "; ".join(pairs[:SHOWN]) + more +
          f". Total {_show(total)}.")
    seed_words = f", with_seed={SEED}" if scipy_name == "2opt" else ""
    print(f"Method: the quadratic assignment problem by {words} (SciPy optimize.quadratic_assignment"
          f"{seed_words}), {int(found.nit)} steps. The problem is hard, so this is a good answer, not one proven to "
          "be the best; R has no common equivalent.")
    import pandas as pd

    from .table import table

    frame = pd.DataFrame({"item": items, "place": [places[p] for p in place_of]})
    return table(frame, fast=fast)
