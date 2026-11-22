"""Risks, rates and diagnostic accuracy from given numbers: sdata.compare_risks, sdata.compare_rates and
sdata.compare_to_truth.

For when only the counts of a paper or a report are at hand, not the rows. The same engines as the table
words (table/risk_words.py, table/accuracy_words.py), so the same packages and the same sentences:

* sdata.compare_risks(events=[20, 30], out_of=[60, 60], names=["new medicine", "usual care"],
  against="usual care");
* sdata.compare_rates(events=[15, 30], time=[1200, 1100]);
* sdata.compare_to_truth(found=45, missed=5, false_alarms=30, correct_negatives=920), or, without
  counts, sdata.compare_to_truth(sensitivity=90, specificity=95, prevalence=1): only the natural-frequency
  sentences (display arithmetic; there are no counts, so no intervals). This is the calculator for the
  base-rate question: how many positive results are real when the condition is rare?
"""

from __future__ import annotations

import math

import numpy as np

from ._errors import SimplydataError, friendly


def _table():
    from .table import table

    return table({"group": ["-"]})


def _rows(rows):
    import narwhals as nw

    from .table.risk_words import _rows_table

    base = _table()
    backend = base._frame.implementation
    return _rows_table(lambda d: base._new_table(nw.from_dict(d, backend=backend)), rows)


def _counts(step, option, values, example, whole=True, above_zero=False):
    if isinstance(values, (str, bytes)) or not hasattr(values, "__len__"):
        raise SimplydataError(f"{step}() needs {option} as a list of numbers, one per group.\nFor example, {example}")
    out = []
    for v in values:
        if isinstance(v, bool) or not isinstance(v, (int, float, np.integer, np.floating)) or not math.isfinite(v) \
                or v < 0 or (whole and v != int(v)) or (above_zero and v <= 0):
            kind = "whole numbers of 0 or more" if whole else "numbers above 0"
            raise SimplydataError(f"{step}() needs {option} as {kind}; {v!r} is not one.\nFor example, {example}")
        out.append(float(v))
    return out


def _group_names(step, names, n, example):
    if names is None:
        return [f"group {i}" for i in range(1, n + 1)]
    if isinstance(names, (str, bytes)) or not hasattr(names, "__len__"):
        raise SimplydataError(f'names= needs a list of {n} names, one per group, like names=["A", "B"].\n'
                              f"For example, {example}")
    if len(names) != n or len({str(g) for g in names}) != n:
        raise SimplydataError(f"names= needs {n} different names, one per number.\nFor example, {example}")
    return [str(g) for g in names]


def _sides(step, groups, against, sides, higher, lower, alternative, example, same_within, not_lower=None,
           not_higher=None):
    from .table.risk_words import check_sides

    return check_sides(step, sides, higher, lower, alternative, against, groups, example, same_within, not_lower,
                       not_higher)


@friendly(renamed={"groups": "names"})
def compare_risks(events=None, out_of=None, names=None, against=None, interval=95, p_value_by="formula",
                  same_within=None, not_lower=None, not_higher=None, sides=2, higher=None, lower=None,
                  alternative=None):
    """How much more (or less) often does something happen in one group than another? From counts.

    sdata.compare_risks(events=[20, 30], out_of=[60, 60], names=["new", "usual"], against="usual")
    events: how many had the event in each group; out_of: how many there were; names: the groups
    (default "group 1", "group 2", ...). Prints the same answer as table.compare_risks (risks,
    risk difference, number needed for one event fewer or more, risk ratio, odds ratio, p-value;
    same_within= for equivalence, with not_lower= or not_higher= for non-inferiority). Gives back
    one row per measure.
    """
    from .table.risk_words import _level, pick_against, risk_engine

    step = "compare_risks"
    example = 'sdata.compare_risks(events=[20, 30], out_of=[60, 60], names=["new medicine", "usual care"])'
    ev = _counts(step, "events=", events, example)
    tot = _counts(step, "out_of=", out_of, example)
    if len(ev) != len(tot) or len(ev) < 2:
        raise SimplydataError(f"{step}() needs events= and out_of= of the same length, 2 or more groups.\n"
                              f"For example, {example}")
    if any(e > t or t == 0 for e, t in zip(ev, tot)):
        raise SimplydataError(f"Each of events= must be at most its out_of= (and out_of= above 0).\nFor example, {example}")
    level = _level(step, interval, example)
    if p_value_by not in ("formula", "exact"):
        from ._errors import choice_error

        raise choice_error(step, "p_value_by", p_value_by, ["formula", "exact"])
    names = _group_names(step, names, len(ev), example)
    ref = pick_against(step, names, against, example, order="given")
    alt, up, claim = _sides(step, names, ref, sides, higher, lower, alternative, example, same_within, not_lower,
                            not_higher)
    if same_within is not None and len(names) != 2:
        raise SimplydataError("same_within= compares two groups.")
    order = [g for g in names if g != ref] + [ref]
    counts = {g: (int(ev[names.index(g)]), int(tot[names.index(g)])) for g in order}
    return _rows(risk_engine(counts, ref, level, "With the event", p_value_by, None, same_within, up, alt,
                             claim=claim))


@friendly(renamed={"groups": "names"})
def compare_rates(events=None, time=None, names=None, against=None, per=1000, interval=95, same_within=None,
                  not_lower=None, not_higher=None, sides=2, higher=None, lower=None, alternative=None):
    """Do events happen more often per unit of time in one group than another? From counts and times.

    sdata.compare_rates(events=[15, 30], time=[1200, 1100], names=["ward A", "ward B"])
    events: the number of events in each group; time: the time followed (such as patient-days);
    names: the groups. Prints the same answer as table.compare_rates (same_within=[0.8, 1.25] for
    equivalence of the rate ratio, with not_lower= or not_higher= for non-inferiority). Gives back
    one row per measure.
    """
    from .table.risk_words import _level, pick_against, rate_engine

    step = "compare_rates"
    example = "sdata.compare_rates(events=[15, 30], time=[1200, 1100])"
    ev = _counts(step, "events=", events, example)
    tm = _counts(step, "time=", time, example, whole=False, above_zero=True)
    if len(ev) != len(tm) or len(ev) < 2:
        raise SimplydataError(f"{step}() needs events= and time= of the same length, 2 or more groups.\n"
                              f"For example, {example}")
    level = _level(step, interval, example)
    if isinstance(per, bool) or not isinstance(per, (int, float)) or per <= 0:
        raise SimplydataError(f"per= is the amount of time the rate is given for, such as per=1000.\nFor example, {example}")
    names = _group_names(step, names, len(ev), example)
    ref = pick_against(step, names, against, example, order="given")
    alt, up, claim = _sides(step, names, ref, sides, higher, lower, alternative, example, same_within, not_lower,
                            not_higher)
    if same_within is not None and len(names) != 2:
        raise SimplydataError("same_within= compares two groups.")
    order = [g for g in names if g != ref] + [ref]
    counts = {g: (ev[names.index(g)], tm[names.index(g)]) for g in order}
    return _rows(rate_engine(counts, ref, level, per, "units of time", "Events", same_within, up, alt, claim=claim))


# Other names for the four counts (other tools and papers): accepted, with a pointer once per session.
COUNT_OTHERS = {"tp": "found", "fn": "missed", "fp": "false_alarms", "tn": "correct_negatives",
                "true_positives": "found", "false_negatives": "missed", "false_positives": "false_alarms",
                "true_negatives": "correct_negatives"}


@friendly(others=COUNT_OTHERS)
def compare_to_truth(found=None, missed=None, false_alarms=None, correct_negatives=None, sensitivity=None,
                     specificity=None, prevalence=None, interval=95):
    """How well does a test find what is really there? From the four counts, or from percents.

    sdata.compare_to_truth(found=45, missed=5, false_alarms=30, correct_negatives=920)
    found: positive and has it; missed: negative but has it; false_alarms: positive but does not
    have it; correct_negatives: negative and does not have it (tp=, fn=, fp=, tn= and
    true_positives= ... true_negatives= are accepted too). Prints the same answer as
    table.compare_to_truth (sensitivity, specificity, predictive values, likelihood ratios).
    sdata.compare_to_truth(sensitivity=90, specificity=95, prevalence=1): no counts, so no
    intervals; it prints how many of 1000 people like these test positive, and how many of those
    really have it (display arithmetic). Gives back one row per measure.
    """
    from .table.accuracy_words import _check_prevalence, _natural_sentence, accuracy_engine, at_prevalence
    from .table.risk_words import _level

    step = "compare_to_truth"
    example = "sdata.compare_to_truth(found=45, missed=5, false_alarms=30, correct_negatives=920)"
    counts = (found, missed, false_alarms, correct_negatives)
    shares = (sensitivity, specificity)
    if all(c is None for c in counts):
        if any(s is None for s in shares) or prevalence is None:
            raise SimplydataError(f"{step}() needs the four counts, or sensitivity=, specificity= and prevalence= "
                                  f"(all in percent).\nFor example, {example}\n"
                                  "or sdata.compare_to_truth(sensitivity=90, specificity=95, prevalence=1)")
        for name, value in (("sensitivity", sensitivity), ("specificity", specificity)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 100:
                raise SimplydataError(f"{name}= is a percent from 0 to 100, such as {name}=90.")
        prev = _check_prevalence(step, prevalence, "sdata.compare_to_truth(sensitivity=90, specificity=95, prevalence=1)")
        se, sp = sensitivity / 100, specificity / 100
        for line in _natural_sentence(prev, se, sp, None, own=False):
            print(line)
        print("Method: display arithmetic on the given percents (Bayes' rule); no intervals, because there are no "
              "counts.")
        ppv, npv = at_prevalence(se, sp, prev)
        return _rows([{"measure": "positive predictive value", "estimate": ppv},
                      {"measure": "negative predictive value", "estimate": npv}])
    if any(c is None for c in counts):
        raise SimplydataError(f"{step}() needs all four counts: found=, missed=, false_alarms=, correct_negatives=.\n"
                              f"For example, {example}")
    tp, fn, fp, tn = (int(v) for v in _counts(step, "the counts", list(counts), example))
    level = _level(step, interval, example)
    prev = _check_prevalence(step, prevalence, example)
    return _rows(accuracy_engine(tp, fn, fp, tn, level, prev, "the test", "the truth"))
