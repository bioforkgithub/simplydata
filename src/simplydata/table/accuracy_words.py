"""How good is a test at finding what is really there? compare_to_truth and compare_accuracy.

The test column is compared with the truth (a reference standard, such as a slow lab test).
Every number comes from statsmodels or from R (simplydata[r]); simplydata counts the rows, calls
the package and words the answer, with natural frequencies ("of 1000 people like these") because
people reason far better with counts than with conditional percents (Gigerenzer and Hoffrage 1995).

* A yes/no test column: sensitivity, specificity and the two predictive values with exact
  Clopper-Pearson intervals (statsmodels proportion_confint "beta", as R epiR::epi.tests(method =
  "exact")); the likelihood ratios and the diagnostic odds ratio with their intervals from R
  epiR::epi.tests() (Python has none; without R a note says how to add them).
* A column of numbers (a score): the ROC curve from R pROC (Python's stack has no DeLong
  interval): pROC::roc(direction = "<"), the AUC with its DeLong interval (ci.auc(method =
  "delong")) and the best cut-off by Youden's index (coords("best", best.method = "youden")), then
  the yes/no answer at that cut-off. Higher scores count as positive (pROC's default "auto" picks
  the direction from the data, which can hide a test that works the wrong way round);
  positive_when="lower" turns it round. cut_off= gives the answer at a chosen cut-off.
* compare_accuracy("crp", "procalcitonin", truth="infected"): DeLong's test of two AUCs measured on
  the same rows (pROC::roc.test(method = "delong", paired = TRUE)), with the interval of the difference.

Display arithmetic, allowed by the owner and marked [D]: the counts "of 1000 people" (each share times
1000, rounded), and the predictive values at another prevalence= (Bayes' rule on the sensitivity and
specificity).
"""

from __future__ import annotations

import math

import numpy as np

from .._errors import SimplydataError, friendly
from .risk_words import _ci, _event_value, _level, _num
from .summaries import _p_sentence

PER = 1000  # natural frequencies: "of 1000 people like these"
WHEN = ("higher", "lower")


def _pct(share) -> str:
    return f"{_num(share * 100)} %"


def _per_1000(prevalence, se, sp):
    """[D] the four counts of 1000 people: (have it, found, missed, without it, true negatives, false alarms)."""
    have = prevalence * PER
    found = se * have
    without = PER - have
    negatives = sp * without
    return (round(have), round(found), round(have) - round(found), round(without), round(negatives),
            round(without) - round(negatives))


def _natural_sentence(prevalence, se, sp, intervals=None, own=True):
    """The natural-frequency sentences (W8). intervals: {measure: (low, high)} as shares, or None."""
    have, found, missed, without, negatives, alarms = _per_1000(prevalence, se, sp)
    positives, negs = found + alarms, missed + negatives
    ci = intervals or {}

    def with_ci(name, value, label):
        if math.isnan(value):
            return f"{label} cannot be worked out".strip()
        if name in ci:
            low, high = ci[name]
            return f"{label} {_pct(value)}, {ci['_label']} {_num(low * 100)} to {_num(high * 100)} %"
        return f"{label} {_pct(value)}"

    where = f"{_pct(prevalence)} have it in this table" if own else f"{_pct(prevalence)} have it"
    ppv = found / positives if positives else math.nan  # [D] shares of the rounded counts, words only
    npv = negatives / negs if negs else math.nan
    lines = [f"Of {PER} people like these ({where}), {have} {'has' if have == 1 else 'have'} it: the test finds {found} "
             f"({with_ci('sensitivity', se, 'sensitivity')}) and misses {missed}. Of the {without} without it, "
             f"{negatives} test negative ({with_ci('specificity', sp, 'specificity')}) and {alarms} test positive "
             "by mistake."]
    if intervals is not None:
        ppv_words, npv_words = (with_ci(k, intervals[f"_{k}"], "")[1:] if not math.isnan(intervals[f"_{k}"]) else ""
                                for k in ("ppv", "npv"))
    else:
        ppv_words, npv_words = (_pct(ppv) if positives else "", _pct(npv) if negs else "")
    if ppv_words:
        first = f"So of the {positives} positive results, {found} ({ppv_words}) really have it"
    else:
        first = "So no one tests positive, and the share of positive results that are real cannot be worked out"
    if npv_words:
        second = f"of the {negs} negative results, {negatives} ({npv_words}) really do not"
    else:
        second = "no one tests negative, so the share of negative results that are right cannot be worked out"
    lines.append(f"{first}; {second}.")
    return lines


def at_prevalence(se, sp, prevalence):
    """[D] PPV and NPV where prevalence (a share) have it: Bayes' rule on the sensitivity and specificity. A share
    with no one in it (such as the PPV of a test that is never positive) is NaN, as R gives 0 / 0."""
    positive = se * prevalence + (1 - sp) * (1 - prevalence)
    negative = sp * (1 - prevalence) + (1 - se) * prevalence
    ppv = se * prevalence / positive if positive > 0 else math.nan
    npv = sp * (1 - prevalence) / negative if negative > 0 else math.nan
    return ppv, npv


def _likelihood_sentence(est, low, high, ci):
    """The likelihood ratios in words; one below 1 is "less common", 0 / 0 "cannot be worked out"."""
    def ends(i, label):
        if math.isnan(low[i]) or math.isnan(high[i]):
            return f"{label}its interval cannot be worked out"
        return f"{label}{_num(low[i])} to {_num(high[i])}"

    lr_pos, lr_neg = float(est[0]), float(est[1])
    if math.isnan(lr_pos):
        pos = "The positive likelihood ratio cannot be worked out (0 / 0: no positive results)"
    elif lr_pos > 1:
        pos = (f"A positive result is {_num(lr_pos)} times more common in people who have it than in people who do not "
               f"(positive likelihood ratio, {ends(0, ci + ' ')})")
    elif lr_pos == 1:
        pos = (f"A positive result is just as common in people who have it as in people who do not (positive "
               f"likelihood ratio 1, {ends(0, ci + ' ')}): the test tells nothing")
    else:
        pos = (f"A positive result is less common in people who have it than in people who do not: only "
               f"{_num(lr_pos)} times as common (positive likelihood ratio below 1, {ends(0, ci + ' ')}), so the test "
               "works the wrong way round")
    if math.isnan(lr_neg):
        neg = "the negative likelihood ratio cannot be worked out (0 / 0: no negative results)"
    else:
        neg = f"a negative result is {_num(lr_neg)} times as common (negative likelihood ratio, {ends(1, '')})"
    return f"{pos}; {neg}."


def _check_prevalence(step, prevalence, example):
    if prevalence is None:
        return None
    if isinstance(prevalence, bool) or not isinstance(prevalence, (int, float)) or not 0 < prevalence < 100:
        raise SimplydataError(f"prevalence= is how common the condition is, in percent (above 0 and below 100), such "
                              f"as prevalence=1.\nFor example, {example}")
    return float(prevalence) / 100


def accuracy_engine(tp, fn, fp, tn, level, prevalence=None, test_words="the test", truth_words="the truth"):
    """Sensitivity, specificity, PPV, NPV (exact intervals, statsmodels), likelihood ratios and the diagnostic
    odds ratio (R epiR); prints the natural-frequency sentences and gives back the rows."""
    from statsmodels.stats.proportion import proportion_confint

    from .._r import RMissing, r_call

    alpha = 1 - level / 100
    ci = _ci(level)
    have, without = tp + fn, fp + tn
    if have == 0 or without == 0:
        raise SimplydataError("To judge a test, the truth needs rows that have the condition and rows that do not; "
                              f"here {'none have it' if have == 0 else 'all have it'}.")
    method_ci = "exact Clopper-Pearson interval (statsmodels proportion_confint, as R epiR::epi.tests(method = \"exact\"))"
    measures = [("sensitivity", tp, have, "of those who have it, the share the test finds"),
                ("specificity", tn, without, "of those without it, the share that test negative"),
                ("positive predictive value", tp, tp + fp, "of the positive results, the share that really have it"),
                ("negative predictive value", tn, tn + fn, "of the negative results, the share that really do not")]
    rows, shares, cis = [], {}, {"_label": ci}
    for name, count, total, meaning in measures:
        if total == 0:
            low = high = value = math.nan
        else:
            value = count / total
            low, high = (float(v) for v in proportion_confint(count, total, alpha=alpha, method="beta"))
        shares[name] = value
        rows.append({"measure": name, "estimate": value, f"estimate {ci} low": low, f"estimate {ci} high": high,
                     "count": int(count), "out of": int(total), "what it means": meaning, "method": method_ci})
        key = {"sensitivity": "sensitivity", "specificity": "specificity", "positive predictive value": "ppv",
               "negative predictive value": "npv"}[name]
        cis[key] = (low, high)
    cis["_ppv"], cis["_npv"] = shares["positive predictive value"], shares["negative predictive value"]
    prev_here = have / (have + without)
    se, sp = shares["sensitivity"], shares["specificity"]
    # the sentence with the table's own counts scaled to 1000 [D], and the intervals of the real counts
    lines = _natural_sentence(prev_here, se, sp, cis)
    try:
        found = r_call("t <- as.table(matrix(c(tp, fn, fp, tn), nrow = 2)); "
                       "d <- epiR::epi.tests(t, method = 'exact', conf.level = level)$detail; "
                       "k <- match(c('lr.pos', 'lr.neg', 'diag.or'), d$statistic); "
                       "list(est = d$est[k], low = d$lower[k], high = d$upper[k])",
                       packages=("epiR",), what="likelihood ratios with their intervals (R epiR::epi.tests())",
                       tp=float(tp), fn=float(fn), fp=float(fp), tn=float(tn), level=level / 100)
        est, low, high = (np.asarray(found[k], dtype=float) for k in ("est", "low", "high"))
        lr_note = ""
    except RMissing:
        est = low = high = np.full(3, math.nan)
        lr_note = ('Note: the likelihood ratios and the diagnostic odds ratio with their intervals come from the R '
                   'package epiR, which is not ready here; to add them: pip install "simplydata[r]", install R, then in '
                   'R install.packages("epiR").')
    for i, (name, meaning) in enumerate((
            ("positive likelihood ratio", "how many times more common a positive result is in those who have it"),
            ("negative likelihood ratio", "how many times as common a negative result is in those who have it"),
            ("diagnostic odds ratio", "the odds of a positive result in those who have it over those who do not"))):
        rows.append({"measure": name, "estimate": float(est[i]), f"estimate {ci} low": float(low[i]),
                     f"estimate {ci} high": float(high[i]), "what it means": meaning,
                     "method": "R epiR::epi.tests(method = \"exact\")"})
    if not lr_note:
        lines.append(_likelihood_sentence(est, low, high, ci))
    if prevalence is None:
        lines.append("The share of positives that are real depends on how common the condition is: give prevalence=1 "
                     "to see it for a group where 1 % have it.")
    else:
        ppv, npv = at_prevalence(se, sp, prevalence)
        lines += _natural_sentence(prevalence, se, sp, None, own=False)
        rows += [{"measure": f"positive predictive value where {prevalence * 100:g} % have it", "estimate": ppv,
                  "method": "Bayes' rule on the sensitivity and specificity (display arithmetic, no interval)"},
                 {"measure": f"negative predictive value where {prevalence * 100:g} % have it", "estimate": npv,
                  "method": "Bayes' rule on the sensitivity and specificity (display arithmetic, no interval)"}]
    for line in lines:
        print(line)
    print(f"Method: exact Clopper-Pearson intervals (statsmodels proportion_confint), likelihood ratios from R "
          f"epiR::epi.tests(method = \"exact\"); {test_words} against {truth_words}. The counts of {PER} are the shares "
          "written as numbers of people.")
    if lr_note:
        print(lr_note)
    return rows


def roc_engine(truth01, score, level, positive_when, score_name, truth_words, cut_off=None, prevalence=None):
    """ROC analysis by R pROC; prints the AUC, the cut-off and the yes/no answer there; gives back rows."""
    from .._r import r_call

    direction = "<" if positive_when == "higher" else ">"
    found = r_call(
        "r <- pROC::roc(truth, score, levels = c(0, 1), direction = dir, quiet = TRUE); "
        "a <- pROC::ci.auc(r, method = 'delong', conf.level = level); "
        "b <- pROC::coords(r, 'best', best.method = 'youden', ret = c('threshold', 'sensitivity', 'specificity'), "
        "transpose = FALSE); "
        "list(auc = as.numeric(a[2]), low = as.numeric(a[1]), high = as.numeric(a[3]), "
        "threshold = b$threshold, se = b$sensitivity, sp = b$specificity)",
        packages=("pROC",), what="the ROC curve and its AUC (R pROC)",
        python_note="Python's stack (SciPy, statsmodels) has no ROC analysis with DeLong's interval",
        truth=truth01, score=score, dir=direction, level=level / 100)
    auc, low, high = (float(np.asarray(found[k])[0]) for k in ("auc", "low", "high"))
    thresholds = np.asarray(found["threshold"], dtype=float)
    ci = _ci(level)
    word = "higher" if positive_when == "higher" else "lower"
    print(f"AUC {_num(auc)} ({ci} {_num(low)} to {_num(high)}): a person who has it scores {word} than one who does "
          f"not in {round(auc * 100)} of 100 such pairs (0.5 is no better than tossing a coin, 1 is perfect).")
    if auc < 0.5:
        print(f"Note: the AUC is below 0.5, so {score_name} works the other way round: "
              + ("lower" if positive_when == "higher" else "higher") + " scores go with having it. "
              f'Give positive_when="{"lower" if positive_when == "higher" else "higher"}" if that was expected.')
    rows = [{"measure": "area under the ROC curve (AUC)", "estimate": auc, f"estimate {ci} low": low,
             f"estimate {ci} high": high, "what it means": f"the chance that a person who has it scores {word}",
             "method": "R pROC::ci.auc(method = \"delong\")"}]
    sign = ">=" if positive_when == "higher" else "<="
    or_more = "or more" if positive_when == "higher" else "or less"
    if cut_off is None:
        if len(thresholds) > 1:
            print(f"Note: {len(thresholds)} cut-offs share the best Youden's index; the first is used.")
        cut = float(thresholds[0])
        se_r, sp_r = float(np.asarray(found["se"])[0]), float(np.asarray(found["sp"])[0])
        print(f"Best cut-off by Youden's index (sensitivity + specificity - 1): {score_name} {_num(cut)} {or_more} counts "
              f"as positive (sensitivity {_pct(se_r)}, specificity {_pct(sp_r)}). A cut-off chosen on these data looks "
              "better here than it will on new data.")
        rows.append({"measure": "best cut-off (Youden's index)", "estimate": cut,
                     "method": "R pROC::coords(\"best\", best.method = \"youden\")"})
    else:
        cut = float(cut_off)
        print(f"Cut-off chosen with cut_off=: {score_name} {_num(cut)} {or_more} counts as positive.")
        rows.append({"measure": "chosen cut-off", "estimate": cut, "method": "cut_off="})
    positive = score >= cut if sign == ">=" else score <= cut
    has = truth01 == 1
    tp, fn = int((positive & has).sum()), int((~positive & has).sum())
    fp, tn = int((positive & ~has).sum()), int((~positive & ~has).sum())
    rows += accuracy_engine(tp, fn, fp, tn, level, prevalence, f"{score_name} {_num(cut)} {or_more} as positive",
                            truth_words)
    print(f'Method: R pROC::roc(direction = "{direction}") ({word} scores count as positive; positive_when= turns it '
          'round), ci.auc(method = "delong"), coords("best", best.method = "youden").')
    return rows


class AccuracyWords:
    def _truth_and_test(self, step, columns, truth, positive, example):
        names = list(columns) + [truth]
        if len(set(names)) != len(names):
            raise SimplydataError(f"{step}() needs the test column and truth= to be different columns.\n"
                                  f"For example, {example}")
        self._need_columns(*names)
        kept = self._two_columns_frame(step, names, example)
        truth_values = kept[truth].to_list()
        has, has_words = _event_value(step, truth, truth_values, positive, what="has it")
        truth01 = np.array([v == has for v in truth_values], dtype=float)
        return kept, truth01, f'"{truth}" = {has_words}'

    @friendly
    def compare_to_truth(self, test_column=None, truth=None, positive=None, prevalence=None, interval=95,
                         cut_off=None, positive_when="higher"):
        """How well does a test find what is really there (sensitivity, specificity, predictive values)?

        table.compare_to_truth("rapid_test", truth="infected")   (with sdata.get_example("clinic"))
        truth= is the column with the real answer (a reference standard). A yes/no test column
        gives, of 1000 people like these, how many the test finds and misses, with sensitivity,
        specificity and the share of positive and negative results that are right (exact
        intervals, statsmodels), and the likelihood ratios from R epiR (simplydata[r]).
        positive= says which value of the truth (and test) column means "has it" when it is not
        clear. prevalence=1 also shows the predictive values where 1 % have it.
        A column of numbers (such as "crp") gives the ROC analysis from R pROC: the AUC with its
        DeLong interval, the best cut-off by Youden's index and the answer at that cut-off;
        cut_off=3 gives the answer at a chosen cut-off. Higher scores count as positive;
        positive_when="lower" turns it round. Gives back one row per measure.
        """
        step = "compare_to_truth"
        example = 'table.compare_to_truth("rapid_test", truth="infected")'
        self._need_name(step, "the test column", test_column, example)
        self._need_name(step, "truth=", truth, example)
        level = _level(step, interval, example)
        prev = _check_prevalence(step, prevalence, example)
        self._check_choice(step, "positive_when", positive_when, WHEN)
        kept, truth01, truth_words = self._truth_and_test(step, [test_column], truth, positive, example)
        schema = self._frame.schema[test_column]
        values = kept[test_column].to_list()
        if schema.is_numeric() and len(set(values)) > 2:
            if cut_off is not None and (isinstance(cut_off, bool) or not isinstance(cut_off, (int, float))):
                raise SimplydataError("cut_off= needs a number on the scale of the test column, such as cut_off=3.")
            score = kept[test_column].to_numpy().astype(float)
            rows = roc_engine(truth01, score, level, positive_when, f'"{test_column}"', truth_words, cut_off, prev)
        else:
            if cut_off is not None:
                raise SimplydataError(f'cut_off= is for a column of numbers (a score); "{test_column}" has two values.')
            if positive_when != "higher":
                raise SimplydataError("positive_when= is for a column of numbers (a score); for a yes/no test column "
                                      "give positive= instead.")
            hit, hit_words = _event_value(step, test_column, values, positive, what="a positive result")
            pos = np.array([v == hit for v in values])
            has = truth01 == 1
            tp, fn = int((pos & has).sum()), int((~pos & has).sum())
            fp, tn = int((pos & ~has).sum()), int((~pos & ~has).sum())
            print(f'Counted as positive: "{test_column}" = {hit_words}; as having it: {truth_words}.')
            rows = accuracy_engine(tp, fn, fp, tn, level, prev, f'"{test_column}"', truth_words)
        return self._many_rows_table(rows)

    @friendly
    def compare_accuracy(self, *scores, truth=None, positive=None, interval=95, positive_when="higher"):
        """Which of two scores tells better who has it? DeLong's test of two AUCs on the same rows.

        table.compare_accuracy("crp", "procalcitonin", truth="infected")   (with sdata.get_example("clinic"))
        Both scores were measured on the same people, so their ROC curves are compared as a pair
        (R pROC::roc.test(method = "delong", paired = TRUE), simplydata[r]). Prints each AUC with
        its DeLong interval, the difference with its interval, and the p-value. Higher scores
        count as positive; positive_when="lower" turns it round. Gives back one row per AUC and
        one for the difference.
        """
        from .._r import r_call

        step = "compare_accuracy"
        example = 'table.compare_accuracy("crp", "procalcitonin", truth="infected")'
        names = []
        for s in scores:
            names.extend(s if isinstance(s, (list, tuple)) else [s])
        if len(names) != 2:
            raise SimplydataError(f"{step}() compares two score columns.\nFor example, {example}")
        for n in names:
            self._need_name(step, "each score column", n, example)
        self._need_name(step, "truth=", truth, example)
        level = _level(step, interval, example)
        self._check_choice(step, "positive_when", positive_when, WHEN)
        kept, truth01, truth_words = self._truth_and_test(step, names, truth, positive, example)
        for n in names:
            if not self._frame.schema[n].is_numeric():
                raise SimplydataError(f'{step}() needs scores (numbers); "{n}" is not a column of numbers.')
        a, b = (kept[n].to_numpy().astype(float) for n in names)
        direction = "<" if positive_when == "higher" else ">"
        found = r_call(
            "r1 <- pROC::roc(truth, a, levels = c(0, 1), direction = dir, quiet = TRUE); "
            "r2 <- pROC::roc(truth, b, levels = c(0, 1), direction = dir, quiet = TRUE); "
            "c1 <- pROC::ci.auc(r1, method = 'delong', conf.level = level); "
            "c2 <- pROC::ci.auc(r2, method = 'delong', conf.level = level); "
            "t <- pROC::roc.test(r1, r2, method = 'delong', paired = TRUE, conf.level = level); "
            "list(auc = c(as.numeric(c1[2]), as.numeric(c2[2])), low = c(as.numeric(c1[1]), as.numeric(c2[1])), "
            "high = c(as.numeric(c1[3]), as.numeric(c2[3])), z = unname(t$statistic), p = t$p.value, "
            "ci = as.numeric(t$conf.int))",
            packages=("pROC",), what="DeLong's test of two ROC curves (R pROC::roc.test())",
            python_note="Python's stack (SciPy, statsmodels) has no DeLong test",
            truth=truth01, a=a, b=b, dir=direction, level=level / 100)
        auc, low, high = (np.asarray(found[k], dtype=float) for k in ("auc", "low", "high"))
        z, p = float(np.asarray(found["z"])[0]), float(np.asarray(found["p"])[0])
        d_low, d_high = (float(v) for v in np.asarray(found["ci"]))
        ci = _ci(level)
        diff = float(auc[0] - auc[1])  # [D] the difference the interval belongs to
        print(f'AUC {_num(auc[0])} for "{names[0]}" ({ci} {_num(low[0])} to {_num(high[0])}) and {_num(auc[1])} for '
              f'"{names[1]}" ({_num(low[1])} to {_num(high[1])}): a difference of {_num(diff)} ({ci} {_num(d_low)} to '
              f"{_num(d_high)}), measured on the same {len(a)} people ({truth_words} counts as having it).")
        print(_p_sentence(p, "the two scores were truly equally good", "a difference this big or bigger",
                          "that the scores are equally good"))
        print(f'Test: DeLong\'s test for two ROC curves on the same rows (z = {_num(z)}), as R pROC::roc.test(method = '
              f'"delong", paired = TRUE); {"higher" if positive_when == "higher" else "lower"} scores count as positive.')
        rows = [{"measure": f"AUC of {n}", "estimate": float(auc[i]), f"estimate {ci} low": float(low[i]),
                 f"estimate {ci} high": float(high[i]), "method": "R pROC::ci.auc(method = \"delong\")"}
                for i, n in enumerate(names)]
        rows.append({"measure": f"difference in AUC ({names[0]} minus {names[1]})", "estimate": diff,
                     f"estimate {ci} low": d_low, f"estimate {ci} high": d_high, "statistic": z, "p-value": p,
                     "method": "DeLong's test, R pROC::roc.test(method = \"delong\", paired = TRUE)"})
        return self._many_rows_table(rows)
