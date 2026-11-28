"""Which input of a formula matters most: Sobol' sensitivity indices (families for 100 %, batches 3-4).

sdata.find_sensitivity_of("a * x**2 + b", ranges={"a": [0, 1], "b": [0, 5], "x": [0, 2]}) lets every name of the
formula vary over its range at the same time (evenly, each on its own) and splits the spread of the formula's
values into the parts each input causes: the first-order index is the share an input causes on its own, the total
index the share it causes with its interactions. SciPy stats.sobol_indices (Saltelli et al. 2010) does the work, on
a quasi-random Sobol' sample of how_many=1024 points (a power of 2) for each of the two base samples, with_seed=1.
Approved by Manish 2026-11-28 (plan section 2.2).
"""

from __future__ import annotations

import math
import numbers

import numpy as np

from ._errors import SimplydataError, friendly

SEED = 1
HOW_MANY = 1024  # points in each of the two base samples (a power of 2, as SciPy's Sobol' sample needs)
SHOWN = 8  # inputs written out in the sentence; the table has them all


@friendly(renamed={"seed": "with_seed", "n": "how_many"}, others={"bounds": "ranges", "dists": "ranges"})
def find_sensitivity_of(formula=None, ranges=None, how_many=HOW_MANY, with_seed=SEED):
    """Which input of a formula matters most. answer = sdata.find_sensitivity_of("a + b", ranges={"a": [0, 1], "b": [0, 5]})

    answer = sdata.find_sensitivity_of("a * x**2 + b", ranges={"a": [0, 1], "b": [0, 5], "x": [0, 2]})
    Which input of a formula matters most? Every name in the formula varies evenly over its range in ranges=, all
    at the same time, and the spread of the formula's values is shared out among them (Sobol' indices): the
    first-order index is the share an input causes on its own, the total index the share it causes with its
    interactions (total minus first order is what it does together with others). Indices near 0 mean the input
    hardly matters over these ranges. SciPy stats.sobol_indices (Saltelli et al. 2010) on a Sobol' sample of
    how_many=1024 points (a power of 2; more points, steadier indices), with_seed=1 (the same seed gives the same
    indices). Gives back a table with one row per input. As R sensitivity::soboljansen() (another estimator, so its
    numbers differ a little).
    """
    from scipy import stats

    from ._maths_formula import read_formula
    from .numbers._base import check_seed

    example = 'sdata.find_sensitivity_of("a * x**2 + b", ranges={"a": [0, 1], "b": [0, 5], "x": [0, 2]})'
    if formula is None:
        raise SimplydataError(f"find_sensitivity_of() needs a formula in quotes and the range of each name in it.\n"
                              f"For example:  {example}")
    read = read_formula(formula)
    names = list(read.names)
    if len(names) < 2:
        raise SimplydataError("find_sensitivity_of() shares the spread among the names of the formula, so it needs at "
                              f"least 2 names; the formula has {len(names)}.\nFor example:  {example}")
    if not isinstance(ranges, dict):
        raise SimplydataError(f"ranges= needs the lowest and highest value of each name, as a dict.\nFor example:  "
                              f"{example}")
    missing = [n for n in names if n not in ranges]
    if missing:
        raise SimplydataError(f"ranges= needs a range for {', '.join(missing)} too (each name in the formula varies)."
                              f"\nFor example:  {example}")
    extra = [n for n in ranges if n not in names]
    if extra:
        raise SimplydataError(f"ranges= has {', '.join(map(str, extra))}, which the formula does not use. The names "
                              f"in the formula: {', '.join(names)}.")
    limits = []
    for name in names:
        pair = ranges[name]
        ok = isinstance(pair, (list, tuple)) and len(pair) == 2 and all(
            isinstance(v, numbers.Real) and not isinstance(v, (bool, np.bool_)) and math.isfinite(v) for v in pair)
        if not ok or not pair[0] < pair[1]:
            raise SimplydataError(f"The range of {name} needs the lowest value, then a higher one, like [0, 1].\n"
                                  f"For example:  {example}")
        limits.append((float(pair[0]), float(pair[1])))
    if isinstance(how_many, bool) or not isinstance(how_many, (int, np.integer)) or how_many < 64 or (
            int(how_many) & (int(how_many) - 1)):
        raise SimplydataError("how_many= is a power of 2 of at least 64 (the Sobol' sample needs it), like 1024 or "
                              "4096.")
    with_seed = check_seed(with_seed, example)

    def values_of(points):
        found = read({name: points[i] for i, name in enumerate(names)})
        found = np.array(np.broadcast_to(np.asarray(found, dtype=float), points.shape[1:]))  # a copy SciPy may change
        return found.reshape(1, -1)

    dists = [stats.uniform(loc=low, scale=high - low) for low, high in limits]
    with np.errstate(all="ignore"):
        result = stats.sobol_indices(func=values_of, n=int(how_many), dists=dists,
                                     rng=np.random.default_rng(with_seed))
    first = np.asarray(result.first_order, dtype=float).reshape(-1)
    total = np.asarray(result.total_order, dtype=float).reshape(-1)
    if not (np.all(np.isfinite(first)) and np.all(np.isfinite(total))):
        raise SimplydataError("The formula does not vary over these ranges (or gives empty values there), so its "
                              "spread cannot be shared out.")
    order = sorted(range(len(names)), key=lambda i: -total[i])
    parts = [f"{names[i]} {total[i]:.2f} ({first[i]:.2f} on its own)" for i in order[:SHOWN]]
    more = f" ... and {len(names) - SHOWN} more" if len(names) > SHOWN else ""
    print(f'Which input of "{read.text}" matters most over these ranges (total index, first order in brackets): '
          f"{', '.join(parts)}{more}.")
    print(f"{names[order[0]]} matters most: about {round(max(total[order[0]], 0) * 100)} % of the spread of the "
          "formula's values comes from it, with what it does together with the others.")
    print(f"Method: Sobol' indices (SciPy stats.sobol_indices, Saltelli et al. 2010), each name varied evenly over its "
          f"range on a Sobol' sample of {int(how_many)} points (seed {with_seed}; the same seed gives the same "
          "indices). Small negative indices are noise of the sample: read them as 0.")
    import pandas as pd

    from .table import Table

    frame = pd.DataFrame({"input": names, "lowest": [lo for lo, _ in limits], "highest": [hi for _, hi in limits],
                          "first-order index": first, "total index": total,
                          "with others": total - first})
    return Table(frame)
