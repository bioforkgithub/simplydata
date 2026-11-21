"""Mediation in plain words (phase S3d-2): explain(column, using="treatment", through="job_seeking").

How much of the effect of one column on another goes through a third? statsmodels stats.mediation.Mediation fits
two models, the mediator from the exposure (and allowing_for=), and the outcome from the exposure, the mediator
(and allowing_for=), and simulates from them (Imai, Keele & Tingley 2010, the quasi-Bayesian algorithm of R
mediation::mediate()): the indirect effect (through the mediator, ACME), the direct effect (ADE), the total effect
and the share that goes through, each averaged over the two exposure levels, with percentile intervals and
simulation p-values. Numbers: least squares (R lm()); yes or no: logistic regression (R glm(family = binomial)),
effects on the chance of yes. The simulation is random: with_seed= fixes it.

simplydata codes the exposure as 0 and 1 (against= is 0), checks the columns and words the answer; every number
comes from statsmodels. The printout always says what the answer rests on.
"""

from __future__ import annotations

import math

import numpy as np

from .._errors import SimplydataError
from .stat_tests import _label, _list_words
from .summaries import _p_sentence

EXAMPLE = ('table.explain("depression", using="treatment", through="job_seeking", allowing_for=["age", "sex"])   '
           '(with sdata.get_example("job_search"): explain("depress2", using="treat", through="job_seek", '
           'allowing_for=["econ_hard", "sex", "age"]))')
SIMULATIONS = 1000  # as R mediation::mediate(sims = 1000)
ASSUMPTIONS = ("These are effects of {x} only if nothing that was not measured affects both {x} and {y}, nor both "
               "{m} and {y} (allowing_for= takes the measured ones into account), {x} came before {m}, and {m} came "
               "before {y}. A randomised {x} makes the first true for {x}, never for {m}.")


def _values(table, name, kept):
    return kept[name].to_list()


def _two_values(name, values):
    distinct = sorted(set(values), key=lambda v: (str(type(v)), v))
    return distinct


def explain_through(table, column, using, through, allowing_for, outcome, with_seed, against, others):
    """explain(through=): one row per effect (indirect, direct, total, share through)."""
    import pandas as pd
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.stats.mediation import Mediation

    step = "explain"
    given = [name for name, value, default in others if value != default]
    if given:
        raise SimplydataError(f"through= gives a mediation analysis with two simple models; leave out "
                              f"{_list_words(given)}.\nFor example, {EXAMPLE}")
    if isinstance(using, (list, tuple)):
        if len(using) != 1:
            raise SimplydataError("With through=, using= takes the one column whose effect is split (the exposure); "
                                  f"put the other columns in allowing_for=.\nFor example, {EXAMPLE}")
        using = using[0]
    for option, value in (("the column", column), ("using=", using), ("through=", through)):
        table._need_name(step, option, value, EXAMPLE)
    allowing = [allowing_for] if isinstance(allowing_for, str) else list(allowing_for or [])
    if not all(isinstance(a, str) for a in allowing):
        raise SimplydataError(f"allowing_for= takes column names.\nFor example, {EXAMPLE}")
    names = [column, using, through] + allowing
    if len(set(names)) != len(names):
        raise SimplydataError("The column, using=, through= and allowing_for= must be different columns (a column "
                              f"cannot be the mediator and the exposure at once).\nFor example, {EXAMPLE}")
    if outcome not in ("numbers", "yes or no"):
        raise SimplydataError('With through=, outcome= is "numbers" (least squares) or "yes or no" (logistic '
                              "regression).")
    table._need_columns(*names)
    kept = table._two_columns_frame(step, names, EXAMPLE)
    if len(kept) < len(names) + 10:
        raise SimplydataError(f"{step}() with through= needs more rows: {len(kept)} rows for {len(names)} columns.")
    exposure = _values(table, using, kept)
    levels = _two_values(using, exposure)
    if len(levels) != 2:
        raise SimplydataError(f'With through=, "{using}" needs two values (such as treated or not): the effect of '
                              f"going from one to the other is split. It has {len(levels)}.")
    zero = levels[0]
    if against is not None:
        if not any(str(v) == str(against) for v in levels):
            raise SimplydataError(f'against="{against}" is not a value of "{using}" '
                                  f"({_list_words(chr(34) + _label(v) + chr(34) for v in levels)}).")
        zero = next(v for v in levels if str(v) == str(against))
    one = next(v for v in levels if v is not zero and str(v) != str(zero))
    data = {"x": np.array([0.0 if str(v) == str(zero) else 1.0 for v in exposure])}

    def read(name, kind_word):
        values = kept[name].to_list()
        if table._frame.schema[name].is_numeric() and not set(values) <= {0, 1}:
            return np.asarray(values, dtype=float), "numbers", None
        distinct = _two_values(name, values)
        if len(distinct) != 2:
            raise SimplydataError(f'"{name}" ({kind_word}) needs numbers or two values (yes or no); it has '
                                  f"{len(distinct)} values.")
        from .risk_words import _event_value

        event, words = _event_value(step, name, values, None, what="yes")
        words = words.replace("; choose with positive=", "")
        return np.array([1.0 if v == event else 0.0 for v in values]), "yes or no", words

    m, m_kind, m_words = read(through, "the mediator, through=")
    y, y_kind, y_words = read(column, "the outcome")
    if outcome == "numbers" and y_kind == "yes or no":
        if not table._frame.schema[column].is_numeric():
            raise SimplydataError(f'"{column}" holds two values (yes or no), so it needs outcome="yes or no" (logistic '
                                  f'regression).\nFor example, table.explain("{column}", using="{using}", '
                                  f'through="{through}", outcome="yes or no")')
        y_kind = "numbers"  # a 0/1 number column explained as numbers: as the user said
    if outcome == "yes or no" and y_kind != "yes or no":
        raise SimplydataError(f'outcome="yes or no" needs "{column}" to hold two values.')
    data["m"], data["y"] = m, y
    terms = []
    for i, name in enumerate(allowing):
        key = f"c{i}"
        if table._frame.schema[name].is_numeric():
            data[key] = np.asarray(kept[name].to_list(), dtype=float)
            terms.append(key)
        else:
            data[key] = [_label(v) for v in kept[name].to_list()]
            terms.append(f"C({key})")
    frame = pd.DataFrame(data)
    extra = "".join(" + " + t for t in terms)

    def model(formula, kind):
        if kind == "numbers":
            return smf.ols(formula, data=frame)
        return smf.glm(formula, data=frame, family=sm.families.Binomial())

    mediator_model = model("m ~ x" + extra, m_kind)
    outcome_model = model("y ~ x + m" + extra, y_kind)
    mediation = Mediation(outcome_model, mediator_model, "x", "m")
    try:
        result = mediation.fit(method="parametric", n_rep=SIMULATIONS, rng=with_seed)
    except TypeError:  # statsmodels before 0.15 has no rng=: it draws from NumPy's global generator, seeded here
        np.random.seed(with_seed)
        result = mediation.fit(method="parametric", n_rep=SIMULATIONS)
    summary = result.summary(alpha=0.05)

    def row(label):
        r = summary.loc[label]
        return (float(r["Estimate"]), float(r["Lower CI bound"]), float(r["Upper CI bound"]), float(r["P-value"]))

    effects = [(f"indirect effect (through {through})", row("ACME (average)")),
               ("direct effect", row("ADE (average)")), ("total effect", row("Total effect")),
               (f"share through {through}", row("Prop. mediated (average)"))]
    scale = ("the chance of yes" if y_kind == "yes or no" else f'"{column}"')
    if m_kind == "yes or no":
        print(f'Note: "{through}" holds two values, so the mediator model is logistic regression (its chance of yes).')
    print(f'How much of the effect of "{using}" ({_label(one)} against {_label(zero)}) on {scale} goes through '
          f'"{through}"' + (f", allowing for {_list_words(allowing)}" if allowing else "") + f" ({len(kept)} rows):")
    for label, (est, low, high, p) in effects[:3]:
        print(f"  {label}: {_num(est)} (95 % interval {_num(low)} to {_num(high)})")
    share = effects[3][1]
    total_p = effects[2][1][3]
    if total_p >= 0.05:
        print(f"  share through {through}: {_num(share[0])} (95 % interval {_num(share[1])} to {_num(share[2])}); "
              "the total effect is not clear here, so this share says little.")
    else:
        print(f"  share through {through}: {_num(share[0])} (95 % interval {_num(share[1])} to {_num(share[2])}).")
    p_indirect = effects[0][1][3]
    print(_p_sentence(p_indirect, if_none=f'nothing went through "{through}"',
                      this="an indirect effect this far from 0", not_shown=f'that nothing goes through "{through}"',
                      shown=f"p < {1 / SIMULATIONS:g}, from {SIMULATIONS} simulations" if p_indirect == 0 else None))
    for words, name in ((m_words, through), (y_words, column)):
        if words:
            print(f'"{name}" is yes or no: {words} counts as yes (1).')
    print(ASSUMPTIONS.format(x=f'"{using}"', m=f'"{through}"', y=f'"{column}"'))
    kinds = {"numbers": "least squares (R lm())", "yes or no": "logistic regression (R glm(family = binomial))"}
    print(f"Method: causal mediation analysis (Imai, Keele & Tingley 2010), statsmodels Mediation with "
          f"{SIMULATIONS} quasi-Bayesian simulations (with_seed={with_seed}), as R mediation::mediate(sims = "
          f"{SIMULATIONS}): the mediator by {kinds[m_kind]}, the outcome by {kinds[y_kind]}; effects averaged over "
          "the two exposure levels, percentile intervals and simulation p-values. Not the Baron-Kenny steps.")
    return [{"term": label, "estimate": est, "95 % CI low": low, "95 % CI high": high, "p-value": p}
            for label, (est, low, high, p) in effects]


def _num(x) -> str:
    from .risk_words import _num as num

    return num(x) if not (isinstance(x, float) and math.isnan(x)) else "cannot be worked out"
