"""Risks and rates in plain words: compare_risks, compare_rates and rate_of.

Like the other tests, these words never change the table: they print the answer in words and give
back a result table, one row per measure. Every number comes from statsmodels or SciPy, and the
few that Python does not give come from R (simplydata[r]); simplydata only counts the rows,
calls the package and words the answer.

* compare_risks("died", for_each_group_in="treatment", against="usual care"): the risk (share with the
  event) in each group with its exact Clopper-Pearson interval (statsmodels proportion_confint
  "beta", as R binom.test()); the risk difference with Newcombe's score interval (statsmodels
  confint_proportions_2indep(method="newcomb"), as R DescTools::BinomDiffCI(method = "score"));
  the risk ratio and odds ratio with Wald intervals on the log scale (statsmodels Table2x2, as R
  epitools::riskratio() / oddsratio(method = "wald") and epiR::epi.2by2()); the p-value of the
  chi-square test with Yates' correction (SciPy chi2_contingency, as R prop.test()).
  p_value_by="exact": Fisher's exact test and the conditional odds ratio (SciPy fisher_exact and
  contingency.odds_ratio(kind="conditional"), as R fisher.test()).
  allowing_for="age_group": Mantel-Haenszel (statsmodels StratifiedTable: pooled odds ratio and
  its interval, the test with continuity correction as R mantelhaen.test(), Breslow-Day as R
  DescTools::BreslowDayTest(), the pooled risk ratio as R epiR::epi.2by2(); the interval of the
  pooled risk ratio comes from R epiR, which Python lacks).
  same_within=10 (percentage points): two one-sided tests (statsmodels tost_proportions_2indep,
  Wald, as R TOSTER::twoprop_test()); with not_lower= or not_higher=, non-inferiority.
* compare_rates("infections", time="patient_days", for_each_group_in="ward"): events per time. Each rate
  with its exact interval (statsmodels confint_poisson "exact-c", as R poisson.test()); the rate
  ratio with the exact conditional test (statsmodels test_poisson_2indep "exact-cond", as R
  poisson.test(c(x1, x2), c(t1, t2))) and R's exact interval of the ratio (poisson.test; Python
  has only other intervals). same_within= takes a ratio margin ([0.8, 1.25], or 1.25 for the same):
  statsmodels tost_poisson_2indep("exact-cond"), as two one-sided R poisson.test(r =).
* rate_of("infections", time="patient_days", for_each_group_in="ward"): the rates and their intervals.

Display arithmetic, allowed by the owner and marked [D]: "out of 100" (the difference times 100),
the number needed for one event fewer or more (1 / the difference, its interval from the
difference's interval) and rates per 1000 (rate times 1000).
"""

from __future__ import annotations

import math

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, friendly
from .stat_tests import _direction, _label, _list_words, _non_inferiority, _one_sided_sentence, _skipped_note, _whole
from .stat_tests import _num as _num_plain
from .summaries import _check_percent, _p_sentence

# value pairs read as (event, no event) without asking
EVENT_PAIRS = (("yes", "no"), ("true", "false"), ("1", "0"), ("1.0", "0.0"), ("y", "n"), ("positive", "negative"),
               ("died", "alive"), ("dead", "alive"))
COMMON = 0.10  # the odds ratio note: an outcome this common makes the odds ratio drift from the risk ratio


def _num(x) -> str:
    """_num after rounding away float noise (0.1 * 100 = 10.000000000000002 is shown as 10.0); a NaN (such as
    0 / 0) is shown as "cannot be worked out", never "nan"."""
    x = float(x)
    if math.isnan(x):
        return "cannot be worked out"
    return _num_plain(round(x, 9) if math.isfinite(x) else x)


def _level(step, interval, example):
    level = _check_percent(step, interval, "interval", example)
    if not 50 <= level < 100:
        raise SimplydataError(f"interval= is the level of the intervals in percent, such as interval=95 (it is "
                              f"{level:g}).\nFor example, {example}")
    return level


def _ci(level) -> str:
    return f"{level:g} % CI"


def _event_value(step, column, values, positive, what="the event", option="positive"):
    """(event value, words) for a column with 2 values; positive= (value= on compare_risks) chooses, else
    yes/no-like pairs, else the second value in sorted order (as R takes the second factor level)."""
    distinct = sorted(set(values), key=lambda v: (str(type(v)), v))
    if len(distinct) != 2:
        found = _list_words(f'"{_label(v)}"' for v in distinct[:6])
        raise SimplydataError(f'{step}() needs "{column}" to hold two values ({what} or not); it holds '
                              f"{len(distinct)}: {found}.")
    if positive is not None:
        for v in distinct:
            if v == positive or str(v) == str(positive):
                return v, f'"{_label(v)}" (chosen with {option}=)'
        raise SimplydataError(f'{option}="{positive}" is not a value of "{column}"; its values are '
                              + _list_words(f'"{_label(v)}"' for v in distinct) + ".")
    lowered = {str(v).strip().lower(): v for v in distinct}
    for yes, no in EVENT_PAIRS:
        if set(lowered) == {yes, no}:
            return lowered[yes], f'"{_label(lowered[yes])}"'
    return distinct[1], (f'"{_label(distinct[1])}" (the second value in sorted order, as R; choose with '
                         f"{option}=)")


def _ratio_words(estimate, low, high, ci) -> str:
    """'2.00 (95 % CI 1.08 to 3.72)', 'infinite (its interval cannot be worked out)' or 'cannot be worked out (0 / 0)'."""
    if math.isnan(estimate):
        return "cannot be worked out (0 / 0)"
    if math.isnan(low) or math.isnan(high):
        return f"{_num(estimate)} (its interval cannot be worked out)"
    return f"{_num(estimate)} ({ci} {_num(low)} to {_num(high)})"


def _rows_table(make, rows):
    """A result table with one row per dict (missing keys left empty)."""
    keys = list(dict.fromkeys(k for r in rows for k in r))
    return make({k: [r.get(k) for r in rows] for k in keys})


def _say_pct(share) -> str:
    return f"{_num(share * 100)} %"


# ---------------------------------------------------------------------------- risks engine
def risk_engine(counts, against, level, what, p_value_by="formula", strata=None, same_within=None, up=None,
                alternative="two-sided", group_word="in", claim=None):
    """compare_risks on counts: counts = {group: (events, total)} in the order to show; against = the
    reference group. strata = (name, {stratum: {group: (events, total)}}) for Mantel-Haenszel. claim: None or
    "not_higher" (from not_higher=, see stat_tests._non_inferiority). Prints the sentences and gives back the
    list of result rows."""
    from scipy import stats
    from statsmodels.stats import contingency_tables as ct
    from statsmodels.stats.proportion import confint_proportions_2indep, proportion_confint

    alpha = 1 - level / 100
    ci = _ci(level)
    rows = []
    shares = {}
    for group, (events, total) in counts.items():
        low, high = proportion_confint(events, total, alpha=alpha, method="beta")
        shares[group] = events / total  # [D] the share the interval belongs to
        rows.append({"measure": "risk", "group": group, "against": None, "estimate": shares[group],
                     f"estimate {ci} low": float(low), f"estimate {ci} high": float(high), "events": int(events),
                     "out of": int(total), "p-value": None,
                     "method": "exact Clopper-Pearson interval (statsmodels proportion_confint, as R binom.test())"})
    listed = _list_words(f"{e} of {t} ({_say_pct(e / t)}) {group_word} {g}" for g, (e, t) in counts.items())
    print(f"{what}: {listed}.")
    ref_events, ref_total = counts[against]
    others = [g for g in counts if g != against]
    if same_within is not None:
        return rows + _risk_equivalence(others[0], against, counts, level, same_within, up, claim)
    for group in others:
        events, total = counts[group]
        tab = np.array([[events, total - events], [ref_events, ref_total - ref_events]], dtype=float)
        diff = shares[group] - shares[against]
        d_low, d_high = (float(v) for v in confint_proportions_2indep(
            events, total, ref_events, ref_total, method="newcomb", compare="diff", alpha=alpha))
        # a copy without the 0.5 added to empty cells (statsmodels shift_zeros=True changes the array it is given):
        # the ratios as R epitools::riskratio() / oddsratio(method = "wald") give them, 0 or infinite with a 0
        zero = bool((tab == 0).any())
        no_events = events == 0 or ref_events == 0  # the risk ratio is 0, infinite or 0/0, without an interval
        with np.errstate(divide="ignore", invalid="ignore"):
            table = ct.Table2x2(tab.copy(), shift_zeros=False)
            rr, (rr_low, rr_high) = float(table.riskratio), (float(v) for v in table.riskratio_confint(alpha=alpha))
            odds, (or_low, or_high) = float(table.oddsratio), (float(v) for v in table.oddsratio_confint(alpha=alpha))
        if no_events:
            rr = math.nan if events == 0 and ref_events == 0 else rr
            rr_low = rr_high = math.nan
        if zero:
            or_low = or_high = math.nan
        # no events in either group, or events in every row: R prop.test() gives NaN (an expected count of 0)
        empty_column = bool((tab.sum(axis=0) == 0).any())
        if p_value_by == "exact":
            fisher = stats.fisher_exact(tab.astype(int), alternative={"two-sided": "two-sided", "greater": "greater",
                                                                       "less": "less"}[alternative])
            p = float(fisher.pvalue)
            cond = stats.contingency.odds_ratio(tab.astype(int), kind="conditional")
            c_ci = cond.confidence_interval(confidence_level=level / 100)
            odds, or_low, or_high = float(cond.statistic), float(c_ci.low), float(c_ci.high)
            test_words = "Fisher's exact test (SciPy fisher_exact, as R fisher.test())"
            or_words = "conditional maximum-likelihood odds ratio with its exact interval (SciPy, as R fisher.test())"
        else:
            if empty_column:
                p = math.nan  # as R prop.test(): NaN (SciPy refuses an expected count of 0)
                test_words = "the chi-square test with Yates' correction (SciPy, as R prop.test())"
            elif alternative == "two-sided":
                p = float(stats.chi2_contingency(tab, correction=True).pvalue)
                test_words = "the chi-square test with Yates' correction (SciPy, as R prop.test())"
            else:
                # one-sided: R prop.test(alternative =) with Yates' correction; statsmodels has only the
                # uncorrected test, so this p-value comes from R
                p = _prop_test_one_sided(events, total, ref_events, ref_total, alternative)
                test_words = f'R prop.test(alternative = "{alternative}") (with Yates\' correction)'
            or_words = "Wald interval on the log scale (statsmodels Table2x2, as R epitools::oddsratio(method = \"wald\"))"
        per_100 = abs(diff) * 100  # [D]
        more = "fewer" if diff < 0 else "more"
        print(f"Out of 100, about {round(per_100)} {more} {group_word} {group} than {group_word} {against} (risk "
              f"difference {_num(diff * 100)} percentage points, {ci} {_num(d_low * 100)} to {_num(d_high * 100)}).")
        rr_line = "Risk ratio " + _ratio_words(rr, rr_low, rr_high, ci)
        if math.isfinite(rr) and rr > 0:
            rr_line += f": the risk {group_word} {group} is {_num(rr)} times the risk {group_word} {against}."
        elif not math.isnan(rr):  # 0 or infinite
            rr_line += f": there are no events {group_word} {group if rr == 0 else against}."
        else:
            rr_line += "."
        or_line = "Odds ratio " + _ratio_words(odds, or_low, or_high, ci)
        if not (math.isfinite(odds) and odds > 0):
            or_line += "."
        elif max(shares[group], shares[against]) > COMMON:
            or_line += ("; odds are not risks: with an outcome this common (over 10 %) the odds ratio lies further "
                        "from 1 than the risk ratio.")
        else:
            or_line += "; with a rare outcome (10 % or less) it is close to the risk ratio."
        print(rr_line + " " + or_line)
        nnt_row = _nnt(diff, d_low, d_high, group, against, ci, group_word)
        if zero:
            exact = (" The conditional odds ratio of the exact test has its interval." if p_value_by == "exact" else
                     ' p_value_by="exact" gives the exact test and the conditional odds ratio with its interval.')
            print("Note: a count of 0 in the 2 x 2 table makes a ratio 0 or infinite (or 0 / 0, which cannot be worked "
                  "out), and its Wald interval cannot be worked out, as in R epitools::riskratio() and oddsratio(); "
                  "simplydata does not add 0.5 to the empty cells." + exact)
        rows += [
            {"measure": "risk difference", "group": group, "against": against, "estimate": diff,
             f"estimate {ci} low": d_low, f"estimate {ci} high": d_high, "p-value": p,
             "method": "Newcombe's score interval (statsmodels, as R DescTools::BinomDiffCI(method = \"score\"))"},
            nnt_row,
            {"measure": "risk ratio", "group": group, "against": against, "estimate": rr,
             f"estimate {ci} low": rr_low, f"estimate {ci} high": rr_high, "p-value": p,
             "method": "Wald interval on the log scale (statsmodels Table2x2, as R epitools::riskratio(method = "
                       "\"wald\"))"},
            {"measure": "odds ratio", "group": group, "against": against, "estimate": odds,
             f"estimate {ci} low": or_low, f"estimate {ci} high": or_high, "p-value": p, "method": or_words},
        ]
        if alternative == "two-sided":
            if_none = "the risks were truly the same"
        else:
            other = against if up == group else group
            if_none = f"the risk {group_word} {up} were truly not higher than {group_word} {other}"
        print(_p_sentence(p, if_none, "a difference this big or bigger", "that the risks are the same"))
        if math.isnan(p):
            print("Note: with " + ("no events in either group" if events + ref_events == 0 else "the event in every row")
                  + ", the chi-square test has an expected count of 0, so R prop.test() gives NaN too.")
        print(f"Method: {test_words} for the p-value; exact intervals for each risk, Newcombe's score interval for "
              "the difference (as R DescTools::BinomDiffCI(method = \"score\")), Wald intervals on the log scale "
              "for the ratios (statsmodels Table2x2, as R epitools::riskratio())" +
              ("; the odds ratio and its interval as R fisher.test()." if p_value_by == "exact" else "."))
    if strata is not None:
        rows += _mantel_haenszel(strata, others[0], against, level, rows)
    return rows


def _prop_test_one_sided(x1, n1, x2, n2, alternative):
    from .._r import r_call

    return float(np.asarray(r_call("prop.test(c(x1, x2), c(n1, n2), alternative = side)$p.value", packages=(),
                                   what="the one-sided test of two risks (R prop.test())",
                                   python_note="statsmodels test_proportions_2indep gives the test without Yates' "
                                               "correction, so its p-value differs from R's; without R, "
                                               "p_value_by=\"exact\" gives the one-sided Fisher test",
                                   x1=float(x1), n1=float(n1), x2=float(x2), n2=float(n2),
                                   side=alternative))[0])


NNT_FEWER, NNT_MORE = "number needed for one event fewer", "number needed for one event more"


def _nnt(diff, low, high, group, against, ci, group_word):
    """The number needed for one event fewer (or more): 1 / the risk difference, rounded up [D] (Altman 1998).

    The labels do not say "treat", "benefit" or "harm": simplydata does not know whether the event is good
    (cured) or bad (died). The sentence names NNTB/NNTH once, for a harmful event."""
    row = {"measure": NNT_FEWER, "group": group, "against": against, "p-value": None,
           "method": "1 / risk difference; its interval from the difference's interval (Altman 1998)"}
    if diff == 0:
        print("The risks are the same, so no number of people gives one event fewer or more.")
        return {**row, "estimate": math.inf, f"estimate {ci} low": math.nan, f"estimate {ci} high": math.nan}
    nnt = 1 / abs(diff)  # [D]
    shown = math.ceil(round(nnt, 9))
    fewer = "fewer" if diff < 0 else "more"
    short = "NNTB" if diff < 0 else "NNTH"
    head = f"Number needed for one event {fewer}: {shown} (1 / {_num(abs(diff))}, rounded up"
    meaning = (f"for every {shown} {group_word} {group} instead of {against}, one event {fewer} (the {short}, if "
               "the event is harmful, such as death)")
    row["measure"] = NNT_FEWER if diff < 0 else NNT_MORE
    if low < 0 < high:
        benefit, harm = 1 / abs(low), 1 / abs(high)  # [D] one event fewer from the lower end, more from the upper
        print(f"{head}): {meaning}. The interval of the difference includes 0, so the interval runs from "
              f"{_num(benefit)} for one event fewer through infinity to {_num(harm)} for one event more.")
        return {**row, "estimate": nnt, f"estimate {ci} low": math.nan, f"estimate {ci} high": math.nan,
                f"{ci} end, one event fewer": benefit, f"{ci} end, one event more": harm}
    ends = sorted((1 / abs(low) if low else math.inf, 1 / abs(high) if high else math.inf))  # [D]
    print(f"{head}; {ci} {_num(ends[0])} to {_num(ends[1])}): {meaning}.")
    return {**row, "estimate": nnt, f"estimate {ci} low": ends[0], f"estimate {ci} high": ends[1]}


def _mantel_haenszel(strata, group, against, level, rows):
    from statsmodels.stats import contingency_tables as ct

    from .._r import RMissing, r_call

    name, tables = strata
    alpha = 1 - level / 100
    ci = _ci(level)
    used, left_out = [], []
    for key, counts in tables.items():
        (e1, t1), (e0, t0) = counts.get(group, (0, 0)), counts.get(against, (0, 0))
        if t1 == 0 or t0 == 0:
            left_out.append(key)
            continue
        used.append((key, np.array([[e1, t1 - e1], [e0, t0 - e0]], dtype=float)))
    if left_out:
        print(f'Note: {_list_words(chr(34) + _label(k) + chr(34) for k in left_out)} in "{name}" has rows of only one '
              "group, so it cannot be compared and was left out of the Mantel-Haenszel analysis.")
    if len(used) < 2:
        raise SimplydataError(f'allowing_for="{name}" needs at least 2 groups in "{name}" with rows of both '
                              f"{group} and {against}.")
    st = ct.StratifiedTable([t for _, t in used])
    odds = float(st.oddsratio_pooled)
    or_low, or_high = (float(v) for v in st.oddsratio_pooled_confint(alpha=alpha))
    p = float(st.test_null_odds(correction=True).pvalue)
    bd = float(st.test_equal_odds(adjust=False).pvalue)
    rr = float(st.riskratio_pooled)
    crude_or = next(r["estimate"] for r in rows if r["measure"] == "odds ratio")
    crude_rr = next(r["estimate"] for r in rows if r["measure"] == "risk ratio")
    try:
        stacked = np.stack([t for _, t in used], axis=2)
        found = r_call("x <- array(v, dim = d); e <- epiR::epi.2by2(as.table(x), method = 'cohort.count', "
                       "conf.level = level); m <- e$massoc.detail$RR.mh.wald; "
                       "list(est = m$est, low = m$lower, high = m$upper)",
                       packages=("epiR",), what="the interval of the Mantel-Haenszel risk ratio (R epiR::epi.2by2())",
                       v=stacked.ravel(order="F"), d=[float(n) for n in stacked.shape], level=level / 100)
        rr_low, rr_high = float(np.asarray(found["low"])[0]), float(np.asarray(found["high"])[0])
        rr_text = f"risk ratio {_num(rr)} ({ci} {_num(rr_low)} to {_num(rr_high)}"
        rr_note = ""
    except RMissing:
        rr_low = rr_high = math.nan
        rr_text = f"risk ratio {_num(rr)} (the interval needs R"
        rr_note = ('Note: the interval of the Mantel-Haenszel risk ratio comes from the R package epiR, which is not '
                   'ready here; to add it: pip install "simplydata[r]", install R, then in R install.packages("epiR").')
    print(f'Allowing for "{name}" (Mantel-Haenszel, {len(used)} groups): odds ratio {_num(odds)} ({ci} {_num(or_low)} '
          f"to {_num(or_high)}; {_num(crude_or)} without allowing for it), {rr_text}; {_num(crude_rr)} without).")
    print(_p_sentence(p, f'the risks were truly the same within each "{name}"', "a difference this big or bigger",
                      "that the risks are the same"))
    same = bd >= 0.05
    print(f'The odds ratio is {"about the same in every" if same else "different between the groups of"} "{name}" '
          f"(Breslow-Day test, p = {_num(bd)})" + (": report each group's odds ratio." if not same else ".")
          + " Method: statsmodels StratifiedTable, the test with continuity correction as R mantelhaen.test(), "
            "Breslow-Day as R DescTools::BreslowDayTest(), the risk ratio as R epiR::epi.2by2().")
    if rr_note:
        print(rr_note)
    method = "Mantel-Haenszel (statsmodels StratifiedTable, as R mantelhaen.test())"
    return [
        {"measure": f"odds ratio allowing for {name}", "group": group, "against": against, "estimate": odds,
         f"estimate {ci} low": or_low, f"estimate {ci} high": or_high, "p-value": p, "method": method},
        {"measure": f"risk ratio allowing for {name}", "group": group, "against": against, "estimate": rr,
         f"estimate {ci} low": rr_low, f"estimate {ci} high": rr_high, "p-value": p,
         "method": "Mantel-Haenszel (statsmodels StratifiedTable; interval from R epiR::epi.2by2())"},
        {"measure": f"same odds ratio in each {name} (Breslow-Day)", "group": group, "against": against,
         "estimate": None, "p-value": bd, "method": "Breslow-Day test (statsmodels, as R DescTools::BreslowDayTest())"},
    ]


def _say_margin(same_within, low, high, scale):
    """The line that says what same_within= means (always printed): "same_within=10 on risks means ..."."""
    given = (f"[{float(same_within[0]):g}, {float(same_within[1]):g}]" if isinstance(same_within, (list, tuple))
             else f"{float(same_within):g}")
    print(f"same_within={given} on {scale[0]} means {scale[1]} from {round(low, 4):g} to {round(high, 4):g}"
          f"{scale[2]}.")


def _risk_margin_note(same_within):
    """compare_risks takes percentage points; a single number below 1 is probably a share (0.1 for 10)."""
    if isinstance(same_within, (int, float, np.integer, np.floating)) and not isinstance(same_within, bool) \
            and 0 < same_within < 1:
        print(f"Note: same_within= is in percentage points: {float(same_within):g} means {float(same_within):g} "
              f"points. Did you mean {round(same_within * 100, 6):g}?")


def _risk_equivalence(group, against, counts, level, same_within, up, claim=None):
    """same_within= in percentage points: TOST, or with not_lower= / not_higher= non-inferiority, on the
    difference of risks."""
    from statsmodels.stats.proportion import (confint_proportions_2indep, test_proportions_2indep,
                                              tost_proportions_2indep)

    from .equivalence import margin

    low, high = margin("compare_risks", same_within)
    _say_margin(same_within, low, high, ("risks", "risk differences", " percentage points"))
    _risk_margin_note(same_within)
    (e1, t1), (e0, t0) = counts[group], counts[against]
    diff = e1 / t1 - e0 / t0
    first, second = group, against
    if up is None:
        result = tost_proportions_2indep(e1, t1, e0, t0, low / 100, high / 100, method="wald")
        p_low, p_high = float(result.results_larger.pvalue), float(result.results_smaller.pvalue)
        p = max(p_low, p_high)
        lo90, hi90 = (float(v) * 100 for v in confint_proportions_2indep(e1, t1, e0, t0, method="wald", compare="diff",
                                                                           alpha=0.10))
        lo95, hi95 = (float(v) * 100 for v in confint_proportions_2indep(e1, t1, e0, t0, method="wald", compare="diff",
                                                                           alpha=0.05))
        span = f"{low:g} to {high:g}"
        within = f"{high:g}" if low == -high else span
        if p < 0.05:
            verdict, answer = "the same within the margin", f"so the risks are the same within {within} percentage points"
        elif lo95 > 0 or hi95 < 0:
            verdict = "different"
            answer = f"and the 95 % interval, {_num(lo95)} to {_num(hi95)}, leaves out 0, so the risks differ"
        else:
            verdict = "the data cannot tell"
            answer = (f"so the data cannot tell whether the risks are the same within {within} percentage points: "
                      f"values from {_num(lo95)} to {_num(hi95)} fit the data (95 % CI). More data would narrow it")
        inside = "lies inside" if low < lo90 and hi90 < high else "does not lie inside"
        print(f"The risk difference ({first} minus {second}) is {_num(diff * 100)} percentage points; the 90 % "
              f"interval, {_num(lo90)} to {_num(hi90)}, {inside} {span}, {answer}.")
        print(_p_sentence(p, f"the difference were truly outside {span} percentage points",
                          "a difference this far inside the margin", "that they differ by more than the margin"))
        print(f"Method: two one-sided tests (TOST, Wald z-tests of two percents, statsmodels tost_proportions_2indep), "
              f"as R TOSTER::twoprop_test(alternative = \"equivalence\"); the larger p counts (p = {_num(p_low)} against "
              f"{low:g}, p = {_num(p_high)} against {high:g}). The 90 % interval goes with the two 5 % tests.")
        return [{"measure": "risk difference (percentage points), equivalence", "group": group, "against": against,
                 "estimate": diff * 100, "estimate 90 % CI low": lo90, "estimate 90 % CI high": hi90,
                 "p-value against the low margin": p_low, "p-value against the high margin": p_high, "p-value": p,
                 "margin low": low, "margin high": high, "answer": verdict,
                 "method": "TOST, Wald (statsmodels tost_proportions_2indep, as R TOSTER::twoprop_test())"}]
    looks_up = up == first
    edge = low if looks_up else high
    side = "larger" if looks_up else "smaller"
    named, other = (up, second if looks_up else first)
    worse = "lower"  # not_lower="B": the risk in B is not lower than in the other group by more than the margin
    if claim == "not_higher":  # not_higher="A": the risk in A is not higher than in the other by more than it
        named, other, worse = other, named, "higher"
    p = float(test_proportions_2indep(e1, t1, e0, t0, value=edge / 100, method="wald", alternative=side).pvalue)
    lo, hi = (float(v) * 100 for v in confint_proportions_2indep(e1, t1, e0, t0, method="wald", compare="diff",
                                                                   alpha=0.10))
    ends = f"at least {_num(lo)}" if looks_up else f"at most {_num(hi)}"
    amount = f"{abs(edge):g}"
    verdict = "not worse than the margin" if p < 0.05 else "the data cannot tell"
    answer = (f"so the risk in {named} is not {worse} than in {other} by more than {amount} percentage "
              "points" if p < 0.05 else f"so the data cannot show that the risk in {named} is not {worse} than in "
              f"{other} by more than {amount} percentage points")
    print(f"The risk difference ({first} minus {second}) is {_num(diff * 100)} percentage points; the one-sided 95 % "
          f"interval is {ends}, {answer}.")
    print(_p_sentence(p, f"the risk in {named} were truly {worse} than in {other} by {amount} points or more",
                      "a difference this far from that", f"that it is {worse} by more than {amount} points"))
    print("Method: one one-sided Wald z-test against the margin (non-inferiority, statsmodels test_proportions_2indep),"
          " as R TOSTER::twoprop_test(); one-sided, as you asked before seeing the data.")
    return [{"measure": "risk difference (percentage points), non-inferiority", "group": group, "against": against,
             "estimate": diff * 100, "estimate one-sided 95 % CI low": lo if looks_up else -math.inf,
             "estimate one-sided 95 % CI high": math.inf if looks_up else hi, "p-value": p, "margin": edge,
             "answer": verdict, "sides": f"one-sided: {named} not {worse} by more than {amount}",
             "method": "non-inferiority, Wald (statsmodels test_proportions_2indep, as R TOSTER::twoprop_test())"}]


# ---------------------------------------------------------------------------- rates engine
def _rate_ci(events, time, level):
    from statsmodels.stats.rates import confint_poisson

    low, high = confint_poisson(events, time, method="exact-c", alpha=1 - level / 100)
    return float(low), float(high)


def rate_rows(counts, level, per, unit):
    """One row per group: events, time, the rate per `per` with its exact interval, and a column "per" that says
    per what ("1000 patient_days"): one column name for every rate word, so forest_plot(x="rate") finds
    "rate 95 % CI low"."""
    ci = _ci(level)
    rows = []
    for group, (events, time) in counts.items():
        low, high = _rate_ci(events, time, level)
        rows.append({"group": group, "events": float(events), "time": float(time),
                     "rate": events / time * per,  # [D] per 1000
                     f"rate {ci} low": low * per, f"rate {ci} high": high * per, "per": f"{per:g} {unit}"})
    listed = _list_words(f"{_num(r['rate'])} in {r['group']} ({ci} {_num(r[f'rate {ci} low'])} to "
                         f"{_num(r[f'rate {ci} high'])}; {_whole(r['events'])} events in {_whole(r['time'])})"
                         for r in rows)
    return rows, listed



def _whole_events(counts):
    """Event counts as whole numbers where they are whole: older SciPy's binomtest (under statsmodels'
    exact conditional Poisson test) refuses 12.0 and asks for 12."""
    return {g: (int(e) if float(e).is_integer() else e, t) for g, (e, t) in counts.items()}


def rate_engine(counts, against, level, per, unit, what, same_within=None, up=None, alternative="two-sided",
                claim=None, unit_words=None):
    """compare_rates on counts = {group: (events, time)}; prints the sentences, gives back the rows. unit is the
    time column's name (for the "per" column), unit_words how the sentence writes it (default: unit)."""
    from statsmodels.stats.rates import test_poisson_2indep

    from .._r import RMissing, r_call

    counts = _whole_events(counts)
    ci = _ci(level)
    rows, listed = rate_rows(counts, level, per, unit)
    for r in rows:
        r["measure"] = "rate"
    print(f"{what} per {per:g} {unit_words or unit}: {listed}.")
    others = [g for g in counts if g != against]
    (e0, t0) = counts[against]
    if same_within is not None:
        return rows + _rate_equivalence(others[0], against, counts, same_within, up, claim)
    side = {"two-sided": "two-sided", "greater": "larger", "less": "smaller"}[alternative]
    r_side = {"two-sided": "two.sided", "greater": "greater", "less": "less"}[alternative]
    for group in others:
        e1, t1 = counts[group]
        if e1 + e0 == 0:
            print(f"No events in {group} or in {against}: the rate ratio is 0 / 0, which cannot be worked out (R "
                  "poisson.test() gives NaN), so there is nothing to test.")
            rows.append({"measure": "rate ratio", "group": group, "against": against, "estimate": math.nan,
                         f"estimate {ci} low": math.nan, f"estimate {ci} high": math.nan, "p-value": math.nan,
                         "method": "no events in either group: the rate ratio cannot be worked out"})
            continue
        with np.errstate(divide="ignore", invalid="ignore"):  # a group with no events: the ratio is 0 or infinite
            test = test_poisson_2indep(e1, t1, e0, t0, method="exact-cond", alternative=side)
        ratio, p = float(test.ratio), float(test.pvalue)
        try:
            found = r_call("stats::poisson.test(c(x1, x0), c(t1, t0), conf.level = level, alternative = side)$conf.int",
                           packages=(), what="the exact interval of a rate ratio (R poisson.test())",
                           python_note="statsmodels confint_poisson_2indep gives score and other intervals, which "
                                       "differ from R's exact one",
                           x1=float(e1), x0=float(e0), t1=float(t1), t0=float(t0), level=level / 100, side=r_side)
            low, high = (float(v) for v in np.asarray(found))
            interval = f" ({ci} {_num(low)} to {_num(high)})" if alternative == "two-sided" else (
                f" (one-sided {ci} {'at least ' + _num(low) if alternative == 'greater' else 'at most ' + _num(high)})")
            note = ""
        except RMissing:
            low = high = math.nan
            interval = ""
            note = ("Note: the exact interval of the rate ratio comes from R (poisson.test()), which is not ready "
                    'here; to add it: pip install "simplydata[r]" and install R.')
        if 0 < ratio < math.inf:
            meaning = f": the rate in {group} is {_num(ratio)} times the rate in {against}."
        else:  # 0 or infinite: one group has no events
            meaning = f": there are no events in {group if ratio == 0 else against}."
        print(f"Rate ratio {_num(ratio)}{interval}{meaning}")
        if alternative == "two-sided":
            if_none = "the rates were truly the same"
        else:
            other = against if up == group else group
            if_none = f"the rate in {up} were truly not higher than in {other}"
        print(_p_sentence(p, if_none, "a difference this big or bigger", "that the rates are the same"))
        print(f"Method: exact intervals for each rate (statsmodels confint_poisson, as R poisson.test()); the exact "
              f"conditional test of the rate ratio (statsmodels test_poisson_2indep), with its exact interval from R, "
              f"as R poisson.test(c({_whole(e1)}, {_whole(e0)}), c({_whole(t1)}, {_whole(t0)})).")
        if note:
            print(note)
        rows.append({"measure": "rate ratio", "group": group, "against": against, "estimate": ratio,
                     f"estimate {ci} low": low, f"estimate {ci} high": high, "p-value": p,
                     "method": "exact conditional test (statsmodels test_poisson_2indep); interval from R poisson.test()"})
    return rows


def ratio_margin(step, same_within):
    """same_within=1.25 -> (0.8, 1.25); same_within=[0.8, 1.25] as given."""
    example = f"table.{step}(..., same_within=1.25)   (rate ratios from 0.8 to 1.25 count as the same)"
    if isinstance(same_within, (int, float, np.integer, np.floating)) and not isinstance(same_within, bool):
        if same_within <= 1:
            raise SimplydataError("same_within= for rates is a rate ratio above 1, such as 1.25 (then 1/1.25 = 0.8 to "
                                  f"1.25 counts as the same).\nFor example, {example}")
        return 1 / float(same_within), float(same_within)
    if isinstance(same_within, (list, tuple)) and len(same_within) == 2 and all(
            isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, bool) for v in same_within):
        low, high = (float(v) for v in same_within)
        if not 0 < low < 1 < high:
            raise SimplydataError(f"same_within=[low, high] for rates needs 0 < low < 1 < high, such as [0.8, 1.25].\n"
                                  f"For example, {example}")
        return low, high
    raise SimplydataError(f"same_within= needs a rate ratio, or two of them [low, high].\nFor example, {example}")


def _rate_equivalence(group, against, counts, same_within, up, claim=None):
    from statsmodels.stats.rates import test_poisson_2indep, tost_poisson_2indep

    from .._r import RMissing, r_call

    low, high = ratio_margin("compare_rates", same_within)
    _say_margin(same_within, low, high, ("rates", "rate ratios", ""))
    if not isinstance(same_within, (list, tuple)) and same_within >= 2:
        print(f"Note: a ratio margin of {float(same_within):g} means {round(1 / same_within, 4):g} to "
              f"{float(same_within):g}, a very wide margin. compare_rates works on the ratio of the rates; for 20 % "
              "either way give same_within=[0.8, 1.25].")
    counts = _whole_events(counts)
    (e1, t1), (e0, t0) = counts[group], counts[against]
    ratio = float(test_poisson_2indep(e1, t1, e0, t0, method="exact-cond").ratio)
    span = f"{_num(low)} to {_num(high)}"
    level = 0.90 if up is None else 0.95
    side = "two.sided" if up is None else ("greater" if up == group else "less")
    try:
        found = np.asarray(r_call("stats::poisson.test(c(x1, x0), c(t1, t0), conf.level = level, alternative = side)"
                                  "$conf.int", packages=(), what="the exact interval of a rate ratio (R poisson.test())",
                                  x1=float(e1), x0=float(e0), t1=float(t1), t0=float(t0), level=level, side=side))
        ci_low, ci_high = float(found[0]), float(found[1])
    except RMissing:
        ci_low = ci_high = math.nan
    if up is None:
        result = tost_poisson_2indep(e1, t1, e0, t0, low, high, method="exact-cond")
        p_low, p_high = float(result.results_larger.pvalue), float(result.results_smaller.pvalue)
        p = max(p_low, p_high)
        verdict = "the same within the margin" if p < 0.05 else (
            "different" if float(test_poisson_2indep(e1, t1, e0, t0, method="exact-cond").pvalue) < 0.05
            else "the data cannot tell")
        answer = {"the same within the margin": f"so the rates are the same within {span}",
                  "different": "and the rates differ (the usual test gives p < 0.05)",
                  "the data cannot tell": f"so the data cannot tell whether the rates are the same within {span}"}[verdict]
        shown = "" if math.isnan(ci_low) else f"; the 90 % interval is {_num(ci_low)} to {_num(ci_high)}"
        print(f"The rate ratio ({group} against {against}) is {_num(ratio)}{shown}, {answer}.")
        print(_p_sentence(p, f"the rate ratio were truly outside {span}", "a ratio this far inside the margin",
                          "that they differ by more than the margin"))
        print(f"Method: two one-sided exact conditional tests (TOST, statsmodels tost_poisson_2indep), as two R "
              f"poisson.test(r = ) one-sided tests (p = {_num(p_low)} against {_num(low)}, p = {_num(p_high)} against "
              f"{_num(high)}); the 90 % interval from R poisson.test().")
        return [{"measure": "rate ratio, equivalence", "group": group, "against": against, "estimate": ratio,
                 "estimate 90 % CI low": ci_low, "estimate 90 % CI high": ci_high, "p-value against the low margin": p_low,
                 "p-value against the high margin": p_high, "p-value": p, "margin low": low, "margin high": high,
                 "answer": verdict, "method": "TOST, exact conditional (statsmodels tost_poisson_2indep)"}]
    looks_up = up == group
    edge = low if looks_up else high
    named, other = up, (against if looks_up else group)
    worse = "lower"  # not_lower="B": the rate in B is not lower than in the other group by more than the margin
    if claim == "not_higher":  # not_higher="A": the rate in A is not higher than in the other by more than it
        named, other, worse = other, named, "higher"
    beyond = "below" if looks_up else "above"
    p = float(test_poisson_2indep(e1, t1, e0, t0, method="exact-cond", value=edge,
                                  alternative="larger" if looks_up else "smaller").pvalue)
    verdict = "not worse than the margin" if p < 0.05 else "the data cannot tell"
    claim_words = f"the rate ratio is not {beyond} {_num(edge)}: the rate in {named} is not {worse} than in {other} " \
                  "by more than the margin"
    print(f"The rate ratio ({group} against {against}) is {_num(ratio)}; "
          + ("" if math.isnan(ci_low) else f"the one-sided 95 % interval is "
             f"{'at least ' + _num(ci_low) if looks_up else 'at most ' + _num(ci_high)}; ")
          + (f"so {claim_words}." if p < 0.05 else f"so the data cannot show that {claim_words}."))
    print(_p_sentence(p, f"the rate ratio were truly {beyond} {_num(edge)}", "a ratio this far from that",
                      f"that it is {beyond} {_num(edge)}"))
    print(f"Method: one one-sided exact conditional test against the margin (non-inferiority, statsmodels "
          f'test_poisson_2indep), as R poisson.test(r = {_num(edge)}, alternative = "{side}"); one-sided, as you asked '
          "before seeing the data.")
    return [{"measure": "rate ratio, non-inferiority", "group": group, "against": against, "estimate": ratio,
             "estimate one-sided 95 % CI low": ci_low if looks_up else 0.0,
             "estimate one-sided 95 % CI high": math.inf if looks_up else ci_high, "p-value": p, "margin": edge,
             "answer": verdict, "sides": f"one-sided: rate ratio not {beyond} {_num(edge)}",
             "method": "non-inferiority, exact conditional (statsmodels test_poisson_2indep)"}]


def pick_against(step, groups, against, example, order="sorted"):
    """The reference group: against=, or the first group. order="sorted": the groups of a column, sorted, as R
    takes the first level of a factor; order="given": counts given as lists (sdata.compare_rates), in the order
    given, as R poisson.test(), prop.test() and epitools take the counts in the order they are given."""
    if against is None:
        how = ("the first in sorted order, as R" if order == "sorted" else
               "the first given, as R takes counts in the order they are given")
        print(f'Note: compared against "{groups[0]}" ({how}); choose another with against=.')
        return groups[0]
    for g in groups:
        if g == against or str(g) == str(against):
            return g
    from .._errors import suggest

    guess = suggest(str(against), [str(g) for g in groups], n=1)
    hint = f' Did you mean against="{guess[0]}"?' if guess else ""
    raise SimplydataError(f'against="{against}" is not one of the groups ({_list_words(chr(34) + str(g) + chr(34) for g in groups)}).'
                          f"{hint}\nFor example, {example}")


def check_sides(step, sides, higher, lower, alternative, against, groups, example, same_within, not_lower=None,
                not_higher=None):
    """sides=1 with higher=/lower= (or, with same_within=, not_lower=/not_higher=) on a word with two groups: the
    SciPy-style alternative for "group minus against", the group that is expected higher (or None) and the
    non-inferiority claim (None or "not_higher", see stat_tests._non_inferiority)."""
    words = [str(g) for g in groups]
    ni_example = example.rstrip(")") + f', same_within=10, not_lower="{words[0]}")'
    sides, higher, lower, claim = _non_inferiority(step, same_within, sides, higher, lower, not_lower, not_higher,
                                                   words, ni_example)
    if len(groups) != 2 and (sides != 2 or higher is not None or lower is not None or alternative is not None):
        raise SimplydataError(f"{step}() looks in one direction only with two groups; this has {len(groups)}.")
    if len(groups) != 2:
        return "two-sided", None, None
    group = next(g for g in groups if g != against)
    choices = {str(group): "greater", str(against): "less"}
    alt, up = _direction(step, sides, higher, lower, alternative, choices, example)
    if up is not None and same_within is None:
        print(_one_sided_sentence(f"{up} higher", f"{'a drop' if up == str(group) else 'a rise'} in {group}"))
    return alt, (group if up == str(group) else (against if up is not None else None)), claim


class RiskWords:
    # ------------------------------------------------------------------ helpers
    def _two_columns_frame(self, step, names, example):
        self._need_columns(*names)
        frame = self._frame
        floats = [c for c in names if frame.schema[c].is_float()]
        if floats:
            frame = frame.with_columns(nw.col(c).fill_nan(None) for c in floats)
        kept = frame.select(*names).drop_nulls()
        _skipped_note(len(frame) - len(kept), names)
        return kept

    def _many_rows_table(self, rows):
        backend = self._frame.implementation
        return _rows_table(lambda d: self._new_table(nw.from_dict(d, backend=backend)), rows)

    # ------------------------------------------------------------------ compare_risks
    @friendly(renamed={"outcome": "column", "for_each": "for_each_group_in"}, others={"positive": "value"})
    def compare_risks(self, column=None, for_each_group_in=None, against=None, value=None, allowing_for=None, interval=95,
                      p_value_by="formula", same_within=None, not_lower=None, not_higher=None, sides=2, higher=None,
                      lower=None, alternative=None, show=None):
        """How much more (or less) often does something happen in one group than in another?

        table.compare_risks("died", for_each_group_in="treatment", against="usual care")   (with sdata.get_example("trial"))
        column: a column with two values (an event or not, such as "yes"/"no"); value= says
        which value is the event when it is not clear (positive= is accepted too). against= is the
        group the others are compared with (default: the first in sorted order, as R).
        Prints the risk in each group, then the risk difference with its interval and what it
        means out of 100 people, the number needed for one event fewer (or more), the risk ratio
        and the odds ratio, then the p-value (chi-square test with Yates' correction, as R
        prop.test()).
        p_value_by="exact": Fisher's exact test and the conditional odds ratio (as R fisher.test()).
        allowing_for="age_group": the Mantel-Haenszel odds ratio and risk ratio, which allow for
        a third column, with the Breslow-Day check that the odds ratio is the same in each group.
        same_within=10: are the risks the same within 10 percentage points (two one-sided tests)?
        same_within=10, not_lower="new medicine": non-inferiority (the risk in "new medicine" is
        not lower by more than 10 points; not_higher= for an event that is bad, such as "died").
        interval=95 sets the level of every interval. Gives back one row per measure (estimate,
        interval, p-value, method).
        show="attributable fractions" (two groups; against= is the group without the exposure): the share
        of the events among the exposed, and in the whole population, that goes with the exposure, with
        their intervals (R epiR::epi.2by2(); crude, not adjusted for other columns); for an exposure
        that goes with fewer events, the preventable fraction among the exposed.
        Routes: statsmodels proportion_confint, confint_proportions_2indep (Newcombe), Table2x2,
        StratifiedTable, tost_proportions_2indep; SciPy chi2_contingency, fisher_exact; R epiR for
        the interval of the Mantel-Haenszel risk ratio.
        """
        step = "compare_risks"
        example = 'table.compare_risks("died", for_each_group_in="treatment", against="usual care")'
        outcome = column
        for option, value_given in (("the column", outcome), ("for_each_group_in=", for_each_group_in)):
            self._need_name(step, option, value_given, example)
        if allowing_for is not None:
            self._need_name(step, "allowing_for=", allowing_for, example)
        level = _level(step, interval, example)
        self._check_choice(step, "p_value_by", p_value_by, ("formula", "exact"))
        from .epi_words import read_show

        show = read_show(step, show, example)
        if show is not None and (allowing_for is not None or p_value_by != "formula" or same_within is not None
                                 or sides != 2 or higher is not None or lower is not None
                                 or alternative not in (None, "two-sided") or not_lower is not None
                                 or not_higher is not None):
            raise SimplydataError('show="attributable fractions" gives the crude fractions of two groups; leave out '
                                  "allowing_for=, p_value_by=, same_within=, not_lower=, not_higher=, sides=, higher= "
                                  "and lower=.\nFor example, "
                                  f'{example.rstrip(")")}, show="attributable fractions")')
        if show is not None and against is None:
            raise SimplydataError('show="attributable fractions" needs against=, the group without the exposure: the '
                                  "fractions are about the other group, so simplydata does not guess it.\nFor example, "
                                  f'{example.rstrip(")")}, show="attributable fractions")')
        names = [outcome, for_each_group_in] + ([allowing_for] if allowing_for else [])
        if len(set(names)) != len(names):
            raise SimplydataError(f"{step}() needs different columns for the outcome, for_each_group_in= and allowing_for=.\n"
                                  f"For example, {example}")
        kept = self._two_columns_frame(step, names, example)
        outcomes = kept[outcome].to_list()
        event, event_words = _event_value(step, outcome, outcomes, value, option="value")
        keys = kept[for_each_group_in].to_list()
        groups = sorted(set(keys), key=lambda k: (str(type(k)), k))
        if len(groups) < 2:
            raise SimplydataError(f'{step}() needs at least 2 groups in "{for_each_group_in}".')
        if show is not None and len(groups) != 2:
            raise SimplydataError(f'show="attributable fractions" compares two groups (exposed or not); '
                                  f'"{for_each_group_in}" has {len(groups)}. Keep two groups first, for example with '
                                  "table.keep_rows_where(...).")
        ref = pick_against(step, groups, against, example)
        alt, up, claim = check_sides(step, sides, higher, lower, alternative, ref, groups, example, same_within,
                                     not_lower, not_higher)
        if same_within is not None and len(groups) != 2:
            raise SimplydataError(f"same_within= compares two groups; \"{for_each_group_in}\" has {len(groups)}. Keep two "
                                  "groups first, for example with table.keep_rows_where(...).")
        if same_within is not None and (allowing_for or p_value_by != "formula"):
            raise SimplydataError("same_within= works on its own; leave out allowing_for= and p_value_by=.")
        if allowing_for is not None and len(groups) != 2:
            raise SimplydataError(f'allowing_for= works with two groups; "{for_each_group_in}" has {len(groups)}.')
        if alt != "two-sided" and allowing_for is not None:
            raise SimplydataError("allowing_for= gives a two-sided analysis; leave out sides=/higher=/lower=.")
        is_event = np.array([v == event for v in outcomes])
        keys_arr = np.asarray(keys, dtype=object)
        order = [g for g in groups if g != ref] + [ref]
        counts = {_label(g): (int(is_event[keys_arr == g].sum()), int((keys_arr == g).sum())) for g in order}
        strata = None
        if allowing_for is not None:
            levels = kept[allowing_for].to_list()
            lev_arr = np.asarray(levels, dtype=object)
            tables = {}
            for lev in sorted(set(levels), key=lambda k: (str(type(k)), k)):
                inside = lev_arr == lev
                tables[_label(lev)] = {_label(g): (int(is_event[inside & (keys_arr == g)].sum()),
                                                   int((inside & (keys_arr == g)).sum())) for g in order}
            strata = (allowing_for, tables)
        what = f'"{outcome}" = {event_words}'
        if show is not None:
            from .epi_words import attributable_rows

            return self._many_rows_table(attributable_rows(counts, _label(ref), level, what, for_each_group_in))
        rows = risk_engine(counts, _label(ref), level, what, p_value_by, strata, same_within,
                           None if up is None else _label(up), alt, claim=claim)
        return self._many_rows_table(rows)

    # ------------------------------------------------------------------ rates
    def _rate_counts(self, step, events, time, for_each, example):
        self._need_name(step, "the events column", events, example)
        self._need_name(step, "time=", time, example)
        names = [events, time] + ([for_each] if for_each is not None else [])
        if for_each is not None:
            self._need_name(step, "for_each_group_in=", for_each, example)
        if len(set(names)) != len(names):
            raise SimplydataError(f"{step}() needs different columns for the events, time= and for_each_group_in=.\n"
                                  f"For example, {example}")
        self._need_columns(*names)
        for c in (events, time):
            if not self._frame.schema[c].is_numeric():
                raise SimplydataError(f'{step}() needs numbers in "{c}".\nFor example, {example}')
        kept = self._two_columns_frame(step, names, example)
        ev = kept[events].to_numpy().astype(float)
        tm = kept[time].to_numpy().astype(float)
        if (ev < 0).any() or (ev != np.round(ev)).any():
            raise SimplydataError(f'"{events}" should hold counts of events: whole numbers of 0 or more.')
        if (tm < 0).any():
            raise SimplydataError(f'"{time}" should hold times of 0 or more (such as days or years of follow-up).')
        if for_each is None:
            return {"all rows": (float(ev.sum()), float(tm.sum()))}, ["all rows"]
        keys = np.asarray(kept[for_each].to_list(), dtype=object)
        groups = sorted(set(keys.tolist()), key=lambda k: (str(type(k)), k))
        return {_label(g): (float(ev[keys == g].sum()), float(tm[keys == g].sum())) for g in groups}, groups

    @friendly(renamed={"for_each": "for_each_group_in"})
    def rate_of(self, events=None, time=None, for_each_group_in=None, per=1000, interval=95, allowing_for=None,
                standard_population=None):
        """How often do events happen per unit of time, such as infections per 1000 patient-days?

        table.rate_of("infections", time="patient_days", for_each_group_in="ward")   (with sdata.get_example("clinic"))
        Adds up the events and the time (in each group), and gives the rate per 1000 units of
        time (per= changes it) with its exact 95 % interval (statsmodels confint_poisson
        "exact-c", as R poisson.test()). Gives back one row per group, with the columns "rate",
        "rate 95 % CI low/high" and "per" (such as "1000 patient_days").
        allowing_for="age_band", standard_population="whole table" (or a table with "age_band" and
        one column of population sizes): directly standardised rates, the rate each group would have
        with the standard population's make-up in age_band, with Fay & Feuer's interval, beside the
        crude rate (R epiR::epi.directadj(), as epitools::ageadjust.direct()).
        """
        step = "rate_of"
        example = 'table.rate_of("infections", time="patient_days", for_each_group_in="ward")'
        level = _level(step, interval, example)
        if isinstance(per, bool) or not isinstance(per, (int, float)) or per <= 0:
            raise SimplydataError(f"per= is the amount of time the rate is given for, such as per=1000.\n"
                                  f"For example, {example}")
        if (allowing_for is None) != (standard_population is None):
            raise SimplydataError("allowing_for= and standard_population= go together: the rates are standardised "
                                  "for the column of allowing_for= to the standard population.\nFor example, "
                                  'table.rate_of("deaths", time="person_years", for_each_group_in="county", '
                                  'allowing_for="age_band", standard_population="whole table")')
        if allowing_for is not None:
            from .epi_words import standardised_rates

            self._need_name(step, "allowing_for=", allowing_for, example)
            return self._many_rows_table(standardised_rates(self, events, time, for_each_group_in, allowing_for,
                                                            standard_population, per, level))
        counts, _ = self._rate_counts(step, events, time, for_each_group_in, example)
        rows, listed = rate_rows(counts, level, per, time)
        print(f'"{events}" per {per:g} "{time}": {listed}.')
        print("Method: exact Poisson intervals (statsmodels confint_poisson, as R poisson.test()).")
        return self._many_rows_table(rows)

    @friendly(renamed={"for_each": "for_each_group_in", "method": "test_method", "test": "test_method"})
    def compare_rates(self, events=None, time=None, for_each_group_in=None, against=None, per=1000, interval=95,
                      same_within=None, not_lower=None, not_higher=None, sides=2, higher=None, lower=None,
                      alternative=None, allowing_for=None, standard_rates=None, test_method=None):
        """Do events happen more often per unit of time in one group than in another?

        table.compare_rates("infections", time="patient_days", for_each_group_in="ward", against="ward A")
        (with sdata.get_example("clinic")). events: a column of counts; time=: the time each row was
        followed (days, years). Adds them up per group and prints each rate per 1000 units of time
        (per=) with its exact interval, then the rate ratio with the exact conditional test
        (statsmodels test_poisson_2indep, as R poisson.test()) and R's exact interval of the ratio
        (simplydata[r]; without R the interval is left out with a note). same_within=[0.8, 1.25]:
        are the rates the same within a rate ratio of 0.8 to 1.25 (two one-sided exact tests)?
        same_within=1.25 means the same. With not_lower="ward B" (or not_higher=): non-inferiority,
        the rate ratio not below (or above) the margin. Gives back one row per measure: each rate
        (columns "rate", its interval, and "per"), then the rate ratio.
        allowing_for="age_band", standard_rates=national (a table with "age_band" and one column of
        rates per 1000 units of time, as per=): observed / expected, the standardised ratio (SMR) of each
        group (for_each_group_in= is optional here) with its exact Poisson interval (R
        epiR::epi.indirectadj(); p-value from R poisson.test()).
        test_method="e-test" (families for 100 %, 2 groups): Krishnamoorthy and Thomson's E-test of two Poisson
        rates (SciPy poisson_means_test), often more powerful than the exact conditional test; gives back one row.
        """
        step = "compare_rates"
        if test_method is not None:
            chosen = str(test_method).strip().lower()
            chosen = {"poisson_means_test": "e-test", "e test": "e-test", "etest": "e-test"}.get(chosen, chosen)
            self._check_choice(step, "test_method", chosen, ("e-test",))
            given = [o for o, v in (("same_within=", same_within), ("not_lower=", not_lower),
                                    ("not_higher=", not_higher), ("allowing_for=", allowing_for),
                                    ("standard_rates=", standard_rates)) if v is not None]
            if given:
                raise SimplydataError(f'test_method="e-test" compares the rates of 2 groups; leave out '
                                      f"{_list_words(given)}.")
        example = 'table.compare_rates("infections", time="patient_days", for_each_group_in="ward", against="ward A")'
        level = _level(step, interval, example)
        if isinstance(per, bool) or not isinstance(per, (int, float)) or per <= 0:
            raise SimplydataError(f"per= is the amount of time the rate is given for, such as per=1000.\n"
                                  f"For example, {example}")
        if (allowing_for is None) != (standard_rates is None):
            raise SimplydataError("allowing_for= and standard_rates= go together on compare_rates(): the events are "
                                  "compared with those the standard rates give for each band of allowing_for= "
                                  "(observed / expected).\nFor example, table.compare_rates(\"deaths\", "
                                  'time="person_years", allowing_for="age_band", standard_rates=national_rates)')
        if standard_rates is not None:
            given = [o for o, v, d in (("against=", against, None), ("same_within=", same_within, None),
                                       ("not_lower=", not_lower, None), ("not_higher=", not_higher, None),
                                       ("sides=", sides, 2), ("higher=", higher, None), ("lower=", lower, None),
                                       ("alternative=", alternative, None)) if v != d]
            if given:
                raise SimplydataError(f"standard_rates= compares each group with the standard rates, not with each "
                                      f"other; leave out {_list_words(given)}.")
            from .epi_words import standardised_ratios

            self._need_name(step, "allowing_for=", allowing_for, example)
            return self._many_rows_table(standardised_ratios(self, events, time, for_each_group_in, allowing_for,
                                                             standard_rates, per, level))
        if for_each_group_in is None:
            raise SimplydataError(f"{step}() compares groups, so it needs for_each_group_in=; for one rate use rate_of().\n"
                                  f"For example, {example}")
        counts, groups = self._rate_counts(step, events, time, for_each_group_in, example)
        if len(groups) < 2:
            raise SimplydataError(f'{step}() needs at least 2 groups in "{for_each_group_in}".')
        ref = pick_against(step, groups, against, example)
        if same_within is not None and len(groups) != 2:
            raise SimplydataError(f'same_within= compares two groups; "{for_each_group_in}" has {len(groups)}.')
        alt, up, claim = check_sides(step, sides, higher, lower, alternative, ref, groups, example, same_within,
                                     not_lower, not_higher)
        order = [_label(g) for g in groups if g != ref] + [_label(ref)]
        counts = {g: counts[g] for g in order}
        if test_method is not None:
            return self._e_test(counts, _label(ref), alt, per, events, time, for_each_group_in)
        rows = rate_engine(counts, _label(ref), level, per, time, f'"{events}"', same_within,
                           None if up is None else _label(up), alt, claim=claim, unit_words=f'"{time}"')
        return self._many_rows_table(rows)

    def _e_test(self, counts, ref, alt, per, events, time, for_each):
        """compare_rates(test_method="e-test"): SciPy poisson_means_test (Krishnamoorthy and Thomson 2004), the group
        against against= (the first group by default)."""
        from scipy import stats

        from .stat_tests import _num
        from .summaries import _p_sentence

        if len(counts) != 2:
            raise SimplydataError(f'test_method="e-test" compares 2 groups; "{for_each}" has {len(counts)}.')
        (other, (k1, n1)), (_, (k2, n2)) = list(counts.items())
        if n1 <= 0 or n2 <= 0:
            raise SimplydataError(f'Each group needs some time in "{time}" to give a rate.')
        result = stats.poisson_means_test(int(k1), n1, int(k2), n2, alternative=alt)
        stat, p = float(result.statistic), float(result.pvalue)
        rate1, rate2 = k1 / n1 * per, k2 / n2 * per
        ratio = (k1 / n1) / (k2 / n2) if k2 > 0 else math.inf
        row = {"test": "E-test of two Poisson rates", "what it compares":
               f'the rate of "{events}" per {per:g} "{time}" in {other} against {ref}', "statistic name": "z",
               "statistic": stat, "p-value": p, f"rate in {other}": rate1, f"rate in {ref}": rate2,
               "rate ratio": ratio, f"events in {other}": k1, f"events in {ref}": k2, f"time in {other}": n1,
               f"time in {ref}": n2, "per": per}
        print(f'The rate of "{events}" is {_num(rate1)} per {per:g} "{time}" in {other} and {_num(rate2)} in {ref}: '
              f"a rate ratio of {_num(ratio)}.")
        print(_p_sentence(p, "the two rates were truly the same", "a difference this big or bigger"))
        print(f"Test: E-test of two Poisson rates (z = {_num(stat)}; Krishnamoorthy and Thomson 2004, SciPy "
              "poisson_means_test), chosen with test_method=; the usual test here is the exact conditional one (as R "
              "poisson.test()).")
        return self._many_rows_table([row])
