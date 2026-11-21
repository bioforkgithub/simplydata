"""2 x 2 crossover (bioequivalence) in plain words (phase S3d-2): compare_averages_of(period=).

table.compare_averages_of("auc", for_each_group_in="formulation", matched_by="subject", period="visit",
same_within=[0.8, 1.25]): each subject had both formulations, one in each of two periods. The analysis is the EMA
guideline's (2010) "all effects fixed" model on the log scale: statsmodels OLS of log(auc) on sequence, subject
(within sequence), period and formulation, as R lm(log(auc) ~ sequence + subject + period + formulation). The
ratio of the geometric means (test / reference) and its 90 % interval are the formulation effect and its interval
taken back from logs; same_within= says whether that interval lies inside the margin (two one-sided tests at 5 %
each, the same as the 90 % interval).

simplydata finds each subject's sequence from the order of the formulations, refuses designs that are not 2 x 2,
leaves out (and names) subjects without both periods, and words the answer. Display arithmetic, marked [D] and
listed for the owner's approval: the ratio and its interval as exp() of statsmodels' log-scale estimate and
interval, and the within-subject CV sqrt(exp(residual variance) - 1) (as R PowerTOST::se2CV()).
"""

from __future__ import annotations

import math
import warnings

import numpy as np

from .._errors import SimplydataError
from .stat_tests import _label, _list_words

EXAMPLE = ('table.compare_averages_of("auc", for_each_group_in="formulation", matched_by="subject", period="period", '
           "same_within=[0.8, 1.25])")


def ratio_margin(same_within):
    """same_within=1.25 -> (0.8, 1.25); [0.8, 1.25] -> (0.8, 1.25): a margin on the ratio, around 1."""
    if same_within is None:
        return None
    if isinstance(same_within, (int, float, np.integer, np.floating)) and not isinstance(same_within, bool):
        if same_within <= 1:
            raise SimplydataError("With period=, same_within= is a margin on the ratio of geometric means, such as "
                                  "same_within=[0.8, 1.25] (the usual bioequivalence limits), or 1.25 for the same.\n"
                                  f"For example, {EXAMPLE}")
        return 1 / float(same_within), float(same_within)  # [D] the margin 1.25 read as 0.8 to 1.25
    if (isinstance(same_within, (list, tuple)) and len(same_within) == 2
            and all(isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, bool)
                    for v in same_within) and 0 < same_within[0] < 1 < same_within[1]):
        return float(same_within[0]), float(same_within[1])
    raise SimplydataError("With period=, same_within= takes the ratio limits [low, high] around 1, such as "
                          f"[0.8, 1.25].\nFor example, {EXAMPLE}")


def crossover(table, column, for_each_group_in, matched_by, period, same_within, against):
    """The EMA 2 x 2 crossover analysis; gives back a one-row result table."""
    import pandas as pd
    import statsmodels.formula.api as smf

    step = "compare_averages_of"
    for option, value in (("the column", column), ("for_each_group_in=", for_each_group_in),
                          ("matched_by=", matched_by), ("period=", period)):
        table._need_name(step, option, value, EXAMPLE)
    names = [column, for_each_group_in, matched_by, period]
    if len(set(names)) != 4:
        raise SimplydataError(f"{step}() with period= needs four different columns: the measurement, "
                              f"for_each_group_in= (the formulation), matched_by= (the subject) and period=.\n"
                              f"For example, {EXAMPLE}")
    table._need_columns(*names)
    if not table._frame.schema[column].is_numeric():
        raise SimplydataError(f'{step}() needs numbers in "{column}".\nFor example, {EXAMPLE}')
    margin = ratio_margin(same_within)
    kept = table._two_columns_frame(step, names, EXAMPLE)
    y = kept[column].to_numpy().astype(float)
    if (y <= 0).any():
        raise SimplydataError(f'The crossover analysis works on the log scale, so "{column}" needs values above 0 '
                              f"(it has {int((y <= 0).sum())} of 0 or less).")
    treatments = [_label(v) for v in kept[for_each_group_in].to_list()]
    periods = [_label(v) for v in kept[period].to_list()]
    subjects = [_label(v) for v in kept[matched_by].to_list()]
    kinds = sorted(set(treatments))
    period_kinds = [_label(v) for v in sorted(set(kept[period].to_list()), key=lambda v: (str(type(v)), v))]
    if len(kinds) != 2 or len(period_kinds) != 2:
        found = len(kinds) if len(kinds) != 2 else len(period_kinds)
        what = f'"{for_each_group_in}" (formulations)' if len(kinds) != 2 else f'"{period}" (periods)'
        raise SimplydataError(f"period= is for the 2 x 2 crossover: two formulations in two periods. {what} has "
                              f"{found}. Replicate and higher-order designs are not offered.")
    ref = kinds[0]
    if against is not None:
        if str(against) not in kinds:
            raise SimplydataError(f'against="{against}" is not one of the formulations '
                                  f"({_list_words(chr(34) + k + chr(34) for k in kinds)}).")
        ref = str(against)
    test = next(k for k in kinds if k != ref)
    frame = pd.DataFrame({"y": y, "trt": treatments, "per": periods, "subj": subjects})
    # each subject needs both formulations, one in each period
    complete, left_out = [], []
    for subject, rows in frame.groupby("subj", sort=False):
        if len(rows) == 2 and set(rows["trt"]) == set(kinds) and set(rows["per"]) == set(period_kinds):
            complete.append(subject)
        else:
            left_out.append(subject)
    if left_out:
        print(f"Note: {len(left_out)} subject{'' if len(left_out) == 1 else 's'} without both formulations in the "
              f"two periods {'was' if len(left_out) == 1 else 'were'} left out: "
              f"{_list_words(left_out[:10])}{' ...' if len(left_out) > 10 else ''}.")
    frame = frame[frame["subj"].isin(complete)].copy()
    if len(complete) < 3:
        raise SimplydataError(f"{step}() with period= needs at least 3 subjects with both periods; it found "
                              f"{len(complete)}.")
    first = frame[frame["per"] == period_kinds[0]].set_index("subj")["trt"]
    second = frame[frame["per"] == period_kinds[1]].set_index("subj")["trt"]
    sequence = {s: f"{first[s]} then {second[s]}" for s in complete}
    frame["seq"] = frame["subj"].map(sequence)
    counts = frame.drop_duplicates("subj")["seq"].value_counts()
    if len(counts) != 2:
        raise SimplydataError(f"Every subject had the formulations in the same order ({counts.index[0]}), so the "
                              "formulation cannot be told apart from the period. A crossover needs both orders.")
    frame["logy"] = np.log(frame["y"])  # the analysis is on the log scale (EMA 2010)
    frame["arm"] = np.where(frame["trt"] == test, "test", "reference")
    with warnings.catch_warnings():  # subject lies within sequence, so one column repeats others (R lm gives NA)
        warnings.simplefilter("ignore")
        fit = smf.ols("logy ~ C(seq) + C(subj) + C(per) + C(arm, Treatment(reference='reference'))", data=frame).fit()
    term = "C(arm, Treatment(reference='reference'))[T.test]"
    estimate, (low, high) = float(fit.params[term]), (float(v) for v in fit.conf_int(alpha=0.10).loc[term])
    ratio, ratio_low, ratio_high = math.exp(estimate), math.exp(low), math.exp(high)  # [D] back from logs
    cv = math.sqrt(math.exp(float(fit.mse_resid)) - 1)  # [D] within-subject CV (R PowerTOST::se2CV)
    df = float(fit.df_resid)

    def pct(v):
        return f"{v * 100:.2f} %"  # [D] the ratio as a percent, 2 decimals as in bioequivalence reports

    print(f'"{column}": {len(complete)} subjects in a 2 x 2 crossover ({_list_words(f"{n} {s}" for s, n in counts.items())}).')
    named = "" if (test, ref) == ("test", "reference") else f" ({test} / {ref})"
    print(f"Ratio of the geometric means, test / reference{named}: {pct(ratio)} (90 % CI {pct(ratio_low)} to "
          f"{pct(ratio_high)}). Within-subject CV {pct(cv)}.")
    verdict = None
    if margin is not None:
        lo, hi = margin
        span = f"{pct(lo)} to {pct(hi)}"
        if lo <= ratio_low and ratio_high <= hi:
            verdict = "same within the margin"
            print(f"The 90 % interval lies inside {span}, so {test} and {ref} are bioequivalent for \"{column}\" "
                  "(two one-sided tests at 5 % each).")
        elif ratio_high < lo or ratio_low > hi:
            verdict = "different"
            print(f"The 90 % interval lies wholly outside {span}, so {test} and {ref} differ by more than the margin "
                  f'for "{column}".')
        else:
            verdict = "the data cannot tell"
            print(f"The 90 % interval reaches outside {span}, so bioequivalence is not shown for \"{column}\" (the "
                  "data cannot tell; this does not show that they differ).")
    print("Method: the EMA (2010) model with all effects fixed: statsmodels OLS of log(" + column + ") on sequence, "
          "subject (within sequence), period and formulation, as R lm(log(" + column + ") ~ sequence + subject + "
          "period + formulation); the 90 % interval taken back from logs; within-subject CV sqrt(exp(MSE) - 1), as R "
          "PowerTOST::se2CV().")
    print("simplydata does not test for carry-over first: that two-stage procedure biases the result (Freeman 1989), "
          "and a washout long enough to rule it out is part of the design.")
    row = {"term": f"ratio of geometric means ({test} / {ref})", "estimate": ratio, "90 % CI low": ratio_low,
           "90 % CI high": ratio_high, "within-subject CV": cv, "subjects": len(complete),
           "degrees of freedom": df}
    if margin is not None:
        row.update({"margin low": margin[0], "margin high": margin[1], "answer": verdict})
    row["method"] = "EMA 2 x 2 crossover, all effects fixed, log scale (statsmodels OLS)"
    return [row]
