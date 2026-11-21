"""Multiple imputation for other words (phase S3d-2): empty_cells="multiple imputation" on explain_survival and
find_correlation_between, as explain() has had since S2.

The empty cells of number columns are filled in 20 times by chained equations with predictive mean matching
(statsmodels MICEData, 5 donors, as R mice(); the same filling as explain()), then:

* explain_survival: R survival::coxph() on each filled-in table (Efron's ties) and the results pooled with Rubin's
  rules by R mice::pool() (Barnard-Rubin degrees of freedom; for a Cox model mice counts the events, minus the
  number of terms, as the complete-data degrees of freedom), read with summary(conf.int = TRUE, exponentiate =
  TRUE). The filling of each column uses the event and the Nelson-Aalen estimate of the cumulative hazard at each
  row's time (R mice::nelsonaalen()), as White & Royston (2009) recommend, not the time itself.
* find_correlation_between: R miceadds::micombine.cor() on the filled-in tables: Fisher's z of each table pooled
  with Rubin's rules and taken back to r (van Buuren 2018, section 5.2), with its interval and p-value.

simplydata prepares the columns and words the answer; every number comes from statsmodels and R.
"""

from __future__ import annotations

import math
import warnings

import numpy as np

from .._errors import SimplydataError
from .stat_tests import _list_words

MULTIPLE = "multiple imputation"


def read_empty_cells(step, empty_cells, example):
    """"leave out" (the default) or "multiple imputation"."""
    if isinstance(empty_cells, str) and empty_cells.strip().lower() in ("leave out", "leave them out", "skip"):
        return "leave out"
    if isinstance(empty_cells, str) and empty_cells.strip().lower() in (MULTIPLE, "mice", "impute"):
        return MULTIPLE
    raise SimplydataError(f'empty_cells= takes "leave out" (the default) or "multiple imputation".\nFor example, '
                          f'{example.rstrip(")")}, empty_cells="multiple imputation")')


def fill_in(columns, seed, what):
    """The filled-in tables (a list of pandas DataFrames with the keys of columns), statsmodels MICEData as
    explain() uses it. R (mice) is started first, as explain() does (table/models.py says why)."""
    import pandas as pd
    from statsmodels.imputation.mice import MICEData

    from .._r import need_r
    from .models import BETWEEN, BURN_IN, IMPUTATIONS, PMM_DONORS

    need_r(("mice",), what, "statsmodels MICE pools with Rubin's rules but without the Barnard-Rubin degrees of "
                            "freedom, so its p-values differ")
    imputer = MICEData(pd.DataFrame(columns), k_pmm=PMM_DONORS, rng=seed)
    filled = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        imputer.update_all(BURN_IN)
        for _ in range(IMPUTATIONS):
            imputer.update_all(BETWEEN)
            filled.append(imputer.data.copy())
    return filled


def _method_line(seed, analysis):
    from .models import IMPUTATIONS, PMM_DONORS

    return (f"Method: multiple imputation by chained equations (statsmodels MICEData, predictive mean matching with "
            f"{PMM_DONORS} donors, with_seed={seed}): the empty cells were filled in {IMPUTATIONS} times, {analysis}.")


# ---------------------------------------------------------------- find_correlation_between
_R_COR = ("colnames(X) <- vn; dl <- lapply(seq_len(m), function(i) as.data.frame(X[((i - 1) * n + 1):(i * n), , drop = FALSE])); "
          "r <- miceadds::micombine.cor(dl, method = meth, conf.level = level); "
          "list(a = as.character(r$variable1), b = as.character(r$variable2), r = r$r, p = r$p, "
          "low = r[[paste0(\"lower\", round(100 * level))]], high = r[[paste0(\"upper\", round(100 * level))]], "
          "fmi = r$fmi)")


def correlation_imputed(table, step, names, method, seed):
    """find_correlation_between(empty_cells="multiple imputation"): r for two columns, a table for more."""
    import narwhals as nw

    if method not in ("pearson", "spearman"):
        raise SimplydataError('empty_cells="multiple imputation" works with method="pearson" or "spearman" '
                              "(R miceadds::micombine.cor()).")
    frame = table._number_frame(step, names)
    values = {nm: np.array([math.nan if v is None else float(v) for v in frame[nm].to_list()]) for nm in names}
    all_empty = np.all([np.isnan(values[nm]) for nm in names], axis=0)
    if all_empty.any():
        print(f"Note: {int(all_empty.sum())} rows with every column empty were left out.")
    values = {nm: v[~all_empty] for nm, v in values.items()}
    gaps = np.any([np.isnan(v) for v in values.values()], axis=0)
    if not gaps.any():
        print("There are no empty cells to fill in, so this is the ordinary correlation.")
        return None
    keys = {nm: f"v{i}" for i, nm in enumerate(names)}
    filled = fill_in({keys[nm]: values[nm] for nm in names}, seed,
                     "Pooling the correlations of the filled-in tables (R miceadds::micombine.cor())")
    from .._r import r_call

    stacked = np.vstack([f[[keys[nm] for nm in names]].to_numpy(dtype=float) for f in filled])
    found = r_call(_R_COR, packages=("miceadds",), what="Pooling correlations (R miceadds::micombine.cor())",
                   python_note="leave out empty_cells= to skip the rows with an empty cell", source="miceadds",
                   X=stacked, vn=[keys[nm] for nm in names], m=float(len(filled)), n=float(len(values[names[0]])), meth=method, level=0.95)
    back = {v: k for k, v in keys.items()}
    pairs = {}
    for a, b, r, p, low, high, fmi in zip(*(np.atleast_1d(found[k]) for k in ("a", "b", "r", "p", "low", "high",
                                                                                "fmi"))):
        pairs[(back[str(a)], back[str(b)])] = tuple(float(x) for x in (r, p, low, high, fmi))
    from .stat_tests import _num
    from .summaries import _p_sentence

    kind = "Pearson's r" if method == "pearson" else "Spearman's rho"
    n = len(values[names[0]])
    print(f"{kind} from {n} rows, {int(gaps.sum())} of them with empty cells filled in:")
    rows = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            r, p, low, high, fmi = pairs[(a, b)]
            print(f'  "{a}" and "{b}": {_num(r)} (95 % CI {_num(low)} to {_num(high)}).')
            if len(names) == 2:
                print("  " + _p_sentence(p, if_none="there were truly no link", this="a link this strong or stronger",
                                         not_shown="that there is no link"))
            rows.append({"column 1": a, "column 2": b, "r": r, "95 % CI low": low, "95 % CI high": high,
                         "p-value": p, "share of variance from empty cells": fmi})
    print(_method_line(seed, "the correlation was found in each filled-in table, and Fisher's z values were pooled "
                             "with Rubin's rules and taken back to r, as R miceadds::micombine.cor()"))
    print("A correlation does not show that one thing causes the other.")
    if len(names) == 2:
        return rows[0]["r"]
    return table._new_table(nw.from_dict({k: [r[k] for r in rows] for k in rows[0]},
                                         backend=table._frame.implementation))


# ---------------------------------------------------------------- explain_survival
_R_COX = ("dl <- lapply(seq_len(m), function(i) X[((i - 1) * n + 1):(i * n), , drop = FALSE]); "
          "fits <- lapply(dl, function(x) survival::coxph(survival::Surv(time, status) ~ x, ties = \"efron\")); "
          "pooled <- mice::pool(mice::as.mira(fits)); "
          "s <- summary(pooled, conf.int = TRUE, exponentiate = TRUE); "
          "list(hr = s$estimate, low = s[[\"2.5 %\"]], high = s[[\"97.5 %\"]], p = s$p.value, df = s$df, "
          "beta = pooled$pooled$estimate, se = s$std.error, lambda = pooled$pooled$lambda)")
_R_HAZARD = "mice::nelsonaalen(data.frame(time = time, status = status), time, status)"


def survival_imputed(table, step, time, event, using, value, seed, example):
    """explain_survival(empty_cells="multiple imputation"): pooled hazard ratios; None when nothing is empty."""
    import narwhals as nw

    from .._r import r_call
    from .survival import is_empty

    numbers = [u for u in using if table._frame.schema[u].is_numeric()]
    texts = [u for u in using if u not in numbers]
    times, events, kept, yes, _ = table._survival_data(step, time, event, texts, example, value)
    used_rows = [i for i in range(len(table._frame))
                 if not any(is_empty(table._frame[c].to_list()[i]) for c in [time, event] + texts)]
    raw = {c: [table._frame[c].to_list()[i] for i in used_rows] for c in numbers}
    values = {c: np.array([math.nan if is_empty(v) else float(v) for v in raw[c]]) for c in numbers}
    gaps = np.any([np.isnan(v) for v in values.values()], axis=0) if numbers else np.zeros(len(times), dtype=bool)
    if not gaps.any():
        print("There are no empty cells in the number columns to fill in, so this is the ordinary Cox model.")
        return None
    status = events.astype(float)
    hazard = np.asarray(r_call(_R_HAZARD, packages=("mice",), what="The Nelson-Aalen estimate (R mice::nelsonaalen())",
                               source="mice::nelsonaalen", time=times, status=status), dtype=float).ravel()
    columns = {"event": status, "hazard": hazard}
    for j, c in enumerate(texts):
        levels = sorted(set(str(v) for v in kept[c]))
        for k, level in enumerate(levels[1:]):
            columns[f"t{j}_{k}"] = np.array([1.0 if str(v) == level else 0.0 for v in kept[c]])
    keys = {c: f"v{i}" for i, c in enumerate(numbers)}
    for c in numbers:
        columns[keys[c]] = values[c]
    filled = fill_in(columns, seed, "Pooling the Cox models of the filled-in tables (R mice::pool())")
    designs, names = [], None
    for f in filled:
        rows = dict(kept)
        for c in numbers:
            rows[c] = f[keys[c]].to_numpy(dtype=float).tolist()
        x, names, _ = table._cox_columns(using, rows, len(times))
        designs.append(x)
    found = r_call(_R_COX, packages=("survival", "mice"), what="Pooling the Cox models (R mice::pool())",
                   python_note="leave out empty_cells= to skip the rows with an empty cell", source="mice::pool",
                   X=np.vstack(designs), m=float(len(filled)), n=float(len(times)), time=times, status=status)
    out = {k: np.asarray(v, dtype=float).ravel() for k, v in found.items()}
    from .summaries import _p_clause
    from .survival import _num

    print(table._event_sentence(event, yes, events, time))
    print(f"Hazard ratios from {len(times)} rows with {int(events.sum())} events, {int(gaps.sum())} rows with empty "
          "cells filled in (above 1: a higher risk of the event at any moment; below 1: a lower risk):")
    result = []
    for i, (column, level, base) in enumerate(names):
        what = f'each 1 more "{column}"' if level is None else f'"{column}" {level} vs {base}'
        print(f"  {what}: hazard ratio {_num(out['hr'][i])} (95 % CI {_num(out['low'][i])} to {_num(out['high'][i])}); "
              f"{_p_clause(float(out['p'][i]))}.")
        result.append({"term": column if level is None else f"{column}: {level} vs {base}",
                       "hazard ratio": float(out["hr"][i]), "95 % CI low": float(out["low"][i]),
                       "95 % CI high": float(out["high"][i]), "coefficient": float(out["beta"][i]),
                       "standard error": float(out["se"][i]), "degrees of freedom": float(out["df"][i]),
                       "p-value": float(out["p"][i]),
                       "share of variance from empty cells": float(out["lambda"][i])})
    print(_method_line(seed, "each column filled in from the event, the Nelson-Aalen cumulative hazard (R "
                             "mice::nelsonaalen(); White & Royston 2009) and the other columns; R survival::coxph() "
                             "(Efron's ties) was fitted to each table, and the results pooled with Rubin's rules "
                             "(Barnard-Rubin degrees of freedom), as R pool(with(mice(...), coxph(...)))"))
    print(f"The filling-in adds uncertainty: up to {round(float(np.max(out['lambda'])) * 100)} % of the variance of a "
          "hazard ratio comes from the differences between the filled-in tables. The proportional-hazards check and "
          "Harrell's C are not pooled here.")
    return table._new_table(nw.from_dict({k: [r[k] for r in result] for k in result[0]},
                                         backend=table._frame.implementation))
