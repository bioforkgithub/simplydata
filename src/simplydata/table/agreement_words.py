"""Agreement and reliability in plain words: agreement_between, limits_of_agreement, reliability_of.

Agreement is not correlation: two raters (or devices) can rise and fall together and still disagree on
every row. These words measure agreement itself. Every number comes from statsmodels or from R
(simplydata[r]); simplydata only builds the table the package wants and words the answer.

* agreement_between("nurse_rating", "doctor_rating"): two columns of categories give Cohen's kappa with
  its interval, z and p (statsmodels cohens_kappa, as R irr::kappa2() and psych::cohen.kappa());
  near_misses="linear" / "quadratic" for ordered categories (in_order= gives the order), as R
  kappa2(weight = "equal" / "squared"). The raw agreement is shown beside kappa, because kappa can be low
  when one category is rare. Three or more columns: Fleiss' kappa (statsmodels fleiss_kappa), its z and p
  from R irr::kappam.fleiss(). Columns of numbers: the intraclass correlation, R psych::ICC() (two-way,
  absolute agreement, one rater by default; raters=, checking_for=, of= choose the form, which is always named:
  raters="a sample" (McGraw and Wong's "random"), "these only" ("fixed") or "different per row" ("different")).
  test_method="krippendorff": R icr::krippalpha(); test_method="lin": Lin's concordance correlation, R
  DescTools::CCC().
* limits_of_agreement("device_a", "device_b"): Bland-Altman: the average difference and the limits within
  which 95 % of differences lie, each with its interval (R BlandAltmanLeh::bland.altman.stats()), and
  Lin's concordance correlation (R DescTools::CCC()). Python has no function that gives the limits with
  their intervals (statsmodels mean_diff_plot only draws them).
* reliability_of(["item_1", "item_2", "item_3", "item_4", "item_5"]): Cronbach's alpha with Feldt's interval and the alpha
  without each item (R psych::alpha(), psych::alpha.ci()).

Display arithmetic, allowed by the owner and marked [D]: the raw agreement (a count of rows where the
columns agree) and the agreement expected by chance, read back from kappa and the raw agreement.
"""

from __future__ import annotations

import math

import numpy as np

from .._errors import SimplydataError, friendly, other_value_note
from .risk_words import _ci, _level, _num
from .stat_tests import _label, _list_words
from .summaries import _p_sentence

METHODS = ("kappa", "icc", "krippendorff", "lin")
WEIGHTS = {"linear": ("linear", "equal"), "quadratic": ("quadratic", "squared")}
RATERS = {"a sample": "twoway", "these only": "twoway", "different per row": "oneway"}
RATERS_OTHERS = {"random": "a sample", "fixed": "these only", "different": "different per row"}  # McGraw and Wong
DATA_WORDS = {"nominal": "categories (nominal data)", "ordinal": "ordered categories (ordinal data)",
              "interval": "numbers (interval data)"}
KINDS = ("agreement", "consistency")
OF = {"one rater": "single", "average of raters": "average"}
NOT_CORRELATION = "Agreement is not correlation: two raters can rise and fall together and still disagree."


def _koo_li(value) -> str:
    """Koo and Li (2016) guide words for an ICC (display only)."""
    if value < 0.5:
        return "poor"
    if value < 0.75:
        return "moderate"
    if value < 0.9:
        return "good"
    return "excellent"


def _r_numbers(found, key):
    return float(np.asarray(found[key], dtype=float)[0])


class AgreementWords:
    # ------------------------------------------------------------------ helpers
    def _agreement_columns(self, step, columns, example, at_least=2):
        names = []
        for value in columns:
            names.extend(value if isinstance(value, (list, tuple)) else [value])
        if len(names) < at_least:
            raise SimplydataError(f"{step}() needs at least {at_least} columns.\nFor example, {example}")
        for n in names:
            self._need_name(step, "each column", n, example)
        if len(set(names)) != len(names):
            raise SimplydataError(f"{step}() was given the same column twice.\nFor example, {example}")
        kept = self._two_columns_frame(step, names, example)
        if len(kept) < 2:
            raise SimplydataError(f"{step}() needs at least 2 rows with a value in every column.")
        return names, kept

    # ------------------------------------------------------------------ agreement_between
    @friendly(renamed={"method": "test_method", "weights": "near_misses", "kind": "checking_for"},
              others={"weight": "near_misses", "wt": "near_misses"})
    def agreement_between(self, *columns, test_method=None, near_misses=None, in_order=None, interval=95,
                          raters="a sample", checking_for="agreement", of="one rater"):
        """How well do two or more raters (or devices) agree on the same rows?

        table.agreement_between("nurse_rating", "doctor_rating")   (with sdata.get_example("clinic"))
        Each column holds one rater's answers for the same rows. The kind of column decides, and
        the sentence says which:
        categories, 2 columns: Cohen's kappa (statsmodels, as R irr::kappa2()), with the raw
        agreement beside it; near_misses="linear" or "quadratic" counts near misses as partly
        right (ordered categories: give in_order=["mild", "moderate", "severe"]);
        categories, 3 or more columns: Fleiss' kappa (statsmodels; its p-value from R irr);
        numbers: the intraclass correlation (ICC) from R psych::ICC(): by default two-way, absolute
        agreement, one rater, the raters a sample of many possible raters (raters="these only" or
        "different per row", checking_for="consistency", of="average of raters" choose another form, and
        the form is always named).
        test_method="krippendorff": Krippendorff's alpha (R icr::krippalpha()); test_method="lin": Lin's
        concordance correlation for two columns of numbers (R DescTools::CCC()).
        Rows with an empty cell are skipped. Gives back a one-row table.
        """
        step = "agreement_between"
        example = 'table.agreement_between("nurse_rating", "doctor_rating")'
        names, kept = self._agreement_columns(step, columns, example)
        level = _level(step, interval, example)
        if test_method is not None:
            self._check_choice(step, "test_method", test_method, METHODS)
        weights = near_misses
        if weights is not None:
            self._check_choice(step, "near_misses", weights, tuple(WEIGHTS))
        if raters in RATERS_OTHERS:
            other_value_note("raters", raters, RATERS_OTHERS[raters])
            raters = RATERS_OTHERS[raters]
        self._check_choice(step, "raters", raters, tuple(RATERS))
        self._check_choice(step, "checking_for", checking_for, KINDS)
        self._check_choice(step, "of", of, tuple(OF))
        numeric = all(self._frame.schema[n].is_numeric() for n in names)
        if test_method is None:
            test_method = "icc" if numeric else "kappa"
        if test_method in ("icc", "lin") and not numeric:
            text = next(n for n in names if not self._frame.schema[n].is_numeric())
            raise SimplydataError(f'test_method="{test_method}" needs columns of numbers; "{text}" is not. For categories leave '
                                  "out test_method= (Cohen's or Fleiss' kappa).")
        if weights is not None and (test_method != "kappa" or len(names) != 2):
            raise SimplydataError("near_misses= is for Cohen's kappa: two columns of categories.")
        if test_method == "lin":
            if len(names) != 2:
                raise SimplydataError('test_method="lin" compares two columns of numbers.')
            return self._lin(names, kept, level)
        if test_method == "icc":
            return self._icc(names, kept, level, raters, checking_for, of)
        values = {n: kept[n].to_list() for n in names}
        order = self._category_order(step, names, values, in_order, weights is not None or test_method == "krippendorff")
        codes = np.column_stack([[order.index(v) for v in values[n]] for n in names]).astype(float)
        if test_method == "krippendorff":
            if numeric and in_order is None:  # numbers: the values themselves, interval data
                raw = np.column_stack([kept[n].to_numpy().astype(float) for n in names])
                return self._krippendorff(names, raw, "interval")
            return self._krippendorff(names, codes, "ordinal" if in_order is not None else "nominal")
        if len(names) == 2:
            return self._cohen(names, codes, order, level, weights, in_order)
        return self._fleiss(names, codes, order)

    def _category_order(self, step, names, values, in_order, need_order):
        seen = sorted({v for n in names for v in values[n]}, key=lambda v: (str(type(v)), v))
        if in_order is None:
            numeric = all(self._frame.schema[n].is_numeric() for n in names)
            if need_order and not numeric:
                return seen  # nominal codes for Krippendorff's alpha; near_misses= is checked below
            return seen
        if isinstance(in_order, str) or not hasattr(in_order, "__iter__"):
            raise SimplydataError(f'in_order= is a list of the categories from lowest to highest, such as '
                                  f'in_order=["mild", "moderate", "severe"].')
        order = list(in_order)
        missing = [v for v in seen if v not in order and str(v) not in [str(o) for o in order]]
        if missing:
            raise SimplydataError(f"in_order= leaves out {_list_words(chr(34) + _label(v) + chr(34) for v in missing)}; "
                                  "list every category once, from lowest to highest.")
        return [next(v for v in seen if v == o or str(v) == str(o)) if any(v == o or str(v) == str(o) for v in seen)
                else o for o in order]

    def _cohen(self, names, codes, order, level, weights, in_order=None):
        from statsmodels.stats.inter_rater import cohens_kappa

        if weights is not None and in_order is None and order == sorted(order, key=str) and not all(
                self._frame.schema[n].is_numeric() for n in names):
            print("Note: the categories are weighted in sorted order ("
                  + ", ".join(f'"{_label(v)}"' for v in order) + '); give in_order=[...] if their order is another.')
        k = len(order)
        table = np.zeros((k, k))
        for a, b in codes.astype(int):
            table[a, b] += 1
        result = cohens_kappa(table, wt=None if weights is None else WEIGHTS[weights][0])
        kappa = float(result["kappa"])
        # statsmodels gives the 95 % interval; for another level, the normal distribution it returns for kappa
        low, high = ((float(result["kappa_low"]), float(result["kappa_upp"])) if level == 95 else
                     (float(v) for v in result["distribution_kappa"].interval(level / 100)))
        z, p = float(result["z_value"]), float(result["pvalue_two_sided"])
        n = int(table.sum())
        same = int(np.trace(table))
        raw = same / n  # [D] share of rows where the two agree
        # [D] the agreement chance would give, read back from the unweighted kappa: kappa = (raw - chance) / (1 -
        # chance). Not for weighted kappa (its observed and chance agreement are weighted, and statsmodels does not
        # give them), nor for kappa = 1 (then raw = 1 and the chance agreement drops out).
        chance = (raw - kappa) / (1 - kappa) if weights is None and kappa < 1 else None
        ci = _ci(level)
        name = "Cohen's kappa" if weights is None else f"weighted kappa ({weights} weights)"
        r_call = "irr::kappa2()" if weights is None else f'irr::kappa2(weight = "{WEIGHTS[weights][1]}")'
        by_chance = "" if chance is None else f"; by chance alone they would agree on about {_num(chance * 100)} %"
        exact = "exactly " if weights is not None else ""
        print(f'"{names[0]}" and "{names[1]}" agree {exact}on {same} of {n} rows ({_num(raw * 100)} %){by_chance}. '
              f"{name[0].upper() + name[1:]} = {_num(kappa)} ({ci} {_num(low)} to {_num(high)}): "
              f"they agree {round(kappa * 100)} % of the way from chance to perfect.")
        print(_p_sentence(p, "the two agreed only by chance", "agreement this far above chance",
                          "that they agree only by chance"))
        weighted = "" if weights is None else (" Near misses count as partly right (" + weights + " weights, in the "
                                               "order " + ", ".join(f'"{_label(v)}"' for v in order) + ").")
        print(f"Method: {name} (statsmodels cohens_kappa), as R {r_call} and psych::cohen.kappa().{weighted} Kappa "
              f"can be low even when the raw agreement is high, if one category is rare, so both are shown. "
              f"{NOT_CORRELATION}")
        row = {"test": name, "what it compares": f'"{names[0]}" and "{names[1]}"', "rows": n,
               "raw agreement": raw, **({} if chance is None else {"agreement by chance": chance}), "estimate": kappa,
               f"estimate {ci} low": low, f"estimate {ci} high": high, "statistic name": "z", "statistic": z,
               "p-value": p,
               "method": f"statsmodels cohens_kappa, as R {r_call}"}
        return self._result_table(row)

    def _fleiss(self, names, codes, order):
        from statsmodels.stats.inter_rater import aggregate_raters, fleiss_kappa

        from .._r import RMissing, r_call

        counts = aggregate_raters(codes.astype(int), n_cat=len(order))[0]
        kappa = float(fleiss_kappa(counts))
        n = len(codes)
        all_same = int((codes == codes[:, :1]).all(axis=1).sum())  # [D] a count
        try:
            found = r_call("k <- irr::kappam.fleiss(x); list(z = unname(k$statistic), p = k$p.value)", packages=("irr",),
                           what="the p-value of Fleiss' kappa (R irr::kappam.fleiss())",
                           python_note="statsmodels fleiss_kappa gives the kappa but no z or p-value", x=codes + 1)
            z, p = _r_numbers(found, "z"), _r_numbers(found, "p")
            note = ""
        except RMissing:
            z = p = math.nan
            note = ('Note: the p-value of Fleiss\' kappa comes from the R package irr, which is not ready here; to add '
                    'it: pip install "simplydata[r]", install R, then in R install.packages("irr").')
        listed = _list_words(f'"{c}"' for c in names)
        print(f"All {len(names)} columns ({listed}) agree on {all_same} of {n} rows ({_num(all_same / n * 100)} %). "
              f"Fleiss' kappa = {_num(kappa)}: 0 is the agreement chance would give, 1 is perfect.")
        if not note:
            print(_p_sentence(p, "the raters agreed only by chance", "agreement this far above chance",
                              "that they agree only by chance"))
        print(f"Method: Fleiss' kappa for {len(names)} raters (statsmodels fleiss_kappa), as R irr::kappam.fleiss(); "
              f"z and p from R. {NOT_CORRELATION}")
        if note:
            print(note)
        return self._result_table({"test": "Fleiss' kappa", "what it compares": listed, "rows": n,
                                   "rows where all agree": all_same, "estimate": kappa,
                                   "statistic name": "z", "statistic": z, "p-value": p, "method": "statsmodels fleiss_kappa; z and p from R "
                                                                   "irr::kappam.fleiss()"})

    def _icc(self, names, kept, level, raters, kind, of):
        from .._r import r_call

        matrix = np.column_stack([kept[n].to_numpy().astype(float) for n in names])
        model, unit = RATERS[raters], OF[of]
        # psych::ICC's rows: ICC1 one-way; ICC2 two-way, absolute agreement (McGraw and Wong's ICC(A,1), the same
        # numbers for random and fixed raters); ICC3 two-way, consistency (ICC(C,1)); a k for the average of raters.
        # psych rather than irr::icc, whose interval for ICC(A,k) does not follow McGraw and Wong (1996).
        psych_row = ("ICC1" if model == "oneway" else "ICC2" if kind == "agreement" else "ICC3")
        psych_row += "k" if unit == "average" else ""
        found = r_call("r <- psych::ICC(x, alpha = 1 - level, lmer = FALSE)$results; i <- r[r$type == row, ]; "
                       "list(value = i$ICC, low = i[['lower bound']], high = i[['upper bound']], f = i$F, "
                       "df1 = i$df1, df2 = i$df2, p = i$p)", packages=("psych",),
                       what="the intraclass correlation (R psych::ICC())",
                       python_note="Python's stack (SciPy, statsmodels) has no ICC", x=matrix, row=psych_row,
                       level=level / 100)
        value, low, high = (_r_numbers(found, k) for k in ("value", "low", "high"))
        f, p = _r_numbers(found, "f"), _r_numbers(found, "p")
        k = "1" if unit == "single" else "k"
        if model == "oneway":
            form = f"ICC(1,{k}), one-way random"
            words = (f"{'one rater' if unit == 'single' else 'the average of the raters'}; each row may have different "
                     f"raters (Shrout and Fleiss ICC(1,{k}))")
        else:
            letter = "A" if kind == "agreement" else "C"
            design = "two-way random" if raters == "a sample" else "two-way mixed"
            sf = {("a sample", "agreement"): f"; Shrout and Fleiss ICC(2,{k})",
                  ("these only", "consistency"): f"; Shrout and Fleiss ICC(3,{k})"}.get((raters, kind), "")
            form = f"ICC({letter},{k}), {design}"
            how = ("absolute agreement" if kind == "agreement" else
                   "consistency (a rater who is always higher by the same amount still counts as agreeing)")
            who = "one rater" if unit == "single" else "the average of the raters"
            words = f"{how}, {who} (McGraw and Wong{sf})"
        ci = _ci(level)
        spread = _koo_li(low), _koo_li(high)
        guide = (f"by Koo and Li's guide it is {spread[0]}" if spread[0] == spread[1] else
                 f"by Koo and Li's guide the interval runs from {spread[0]} to {spread[1]}")
        print(f"{form} = {_num(value)} ({ci} {_num(low)} to {_num(high)}) for {len(names)} columns and {len(matrix)} "
              f"rows: {guide} (below 0.5 poor, 0.5 to 0.75 moderate, 0.75 to 0.9 good, above 0.9 excellent).")
        print(_p_sentence(p, "there were truly no agreement (ICC = 0)", "agreement this high", None))
        print(f"Method: {form}: {words}; R psych::ICC(lmer = FALSE), its row {psych_row} (F = {_num(f)}). "
              f"{NOT_CORRELATION}")
        return self._result_table({"test": "intraclass correlation", "form": form,
                                   "what it compares": _list_words(f'"{c}"' for c in names), "rows": len(matrix),
                                   "estimate": value, f"estimate {ci} low": low,
                                   f"estimate {ci} high": high, "statistic name": "F", "statistic": f, "p-value": p,
                                   "method": f"R psych::ICC(lmer = FALSE), row {psych_row}"})

    def _krippendorff(self, names, codes, level_name):
        from .._r import r_call

        # icr rather than irr::kripp.alpha, which weights the pairs within a row by 1 instead of 1 / (m - 1) when no
        # cell is empty, so it is wrong for 3 or more raters (icr gives Krippendorff's published examples)
        found = r_call("icr::krippalpha(t(x), metric = m)$alpha", packages=("icr",),
                       what="Krippendorff's alpha (R icr::krippalpha())",
                       python_note="Python's stack (SciPy, statsmodels) has no Krippendorff's alpha", x=codes,
                       m=level_name)
        value = float(np.asarray(found, dtype=float)[0])
        listed = _list_words(f'"{c}"' for c in names)
        print(f"Krippendorff's alpha = {_num(value)} for {listed} ({DATA_WORDS[level_name]}), {len(codes)} rows: 1 is "
              "perfect agreement, 0 the agreement chance would give.")
        print("Method: Krippendorff's alpha from its coincidence matrix (Hayes and Krippendorff 2007), R "
              f'icr::krippalpha(metric = "{level_name}"). {NOT_CORRELATION}')
        return self._result_table({"test": "Krippendorff's alpha", "what it compares": listed, "rows": len(codes),
                                   "kind of data": DATA_WORDS[level_name], "estimate": value,
                                   "method": f'R icr::krippalpha(metric = "{level_name}")'})

    def _ccc(self, a, b, level):
        from .._r import r_call

        found = r_call("c <- DescTools::CCC(a, b, conf.level = level)$rho.c; list(est = c$est, low = c$lwr.ci, "
                       "high = c$upr.ci)", packages=("DescTools",), what="Lin's concordance correlation (R DescTools::CCC())",
                       python_note="Python's stack (SciPy, statsmodels) has no concordance correlation with an interval",
                       a=a, b=b, level=level / 100)
        return tuple(_r_numbers(found, k) for k in ("est", "low", "high"))

    def _lin(self, names, kept, level):
        a, b = (kept[n].to_numpy().astype(float) for n in names)
        value, low, high = self._ccc(a, b, level)
        ci = _ci(level)
        print(f'Lin\'s concordance correlation between "{names[0]}" and "{names[1]}" = {_num(value)} ({ci} {_num(low)} '
              f"to {_num(high)}), {len(a)} rows: how close the pairs lie to the line of equal values (1 = all on it).")
        print(f"Method: R DescTools::CCC() (Fisher's z interval). Unlike the ordinary correlation, it drops when one "
              f"column reads higher than the other. {NOT_CORRELATION}")
        return self._result_table({"test": "Lin's concordance correlation", "what it compares":
                                   f'"{names[0]}" and "{names[1]}"', "rows": len(a), "estimate": value,
                                   f"estimate {ci} low": low, f"estimate {ci} high": high,
                                   "method": "R DescTools::CCC()"})

    # ------------------------------------------------------------------ limits_of_agreement
    @friendly
    def limits_of_agreement(self, first=None, second=None, interval=95):
        """How far apart are two ways of measuring the same thing (Bland-Altman limits of agreement)?

        table.limits_of_agreement("device_a", "device_b")   (with sdata.get_example("clinic"))
        Each row is one thing measured both ways. Prints how much the first reads higher or lower
        on average, and the limits within which 95 % of the differences lie (average difference
        plus and minus 1.96 standard deviations), each with its interval (R
        BlandAltmanLeh::bland.altman.stats(), simplydata[r]), and Lin's concordance correlation (R
        DescTools::CCC()). Whether the limits are close enough is a question for the field, not
        for statistics. chart.difference_dots(first=..., second=...) draws it. Gives back a one-row
        table.
        """
        from .._r import r_call

        step = "limits_of_agreement"
        example = 'table.limits_of_agreement("device_a", "device_b")'
        names, kept = self._agreement_columns(step, [first, second], example)
        for n in names:
            if not self._frame.schema[n].is_numeric():
                raise SimplydataError(f'{step}() needs two columns of numbers; "{n}" is not.\nFor example, {example}')
        level = _level(step, interval, example)
        a, b = (kept[n].to_numpy().astype(float) for n in names)
        found = r_call("s <- BlandAltmanLeh::bland.altman.stats(a, b, conf.int = level); "
                       "list(mean = s$mean.diffs, lower = s$lower.limit, upper = s$upper.limit, ci = unname(s$CI.lines), "
                       "sd = s$critical.diff / 1.96)", packages=("BlandAltmanLeh",),
                       what="the limits of agreement with their intervals (R BlandAltmanLeh::bland.altman.stats())",
                       python_note="statsmodels graphics.agreement.mean_diff_plot draws the limits but gives no "
                                   "intervals", a=a, b=b, level=level / 100)
        mean, lower, upper = (_r_numbers(found, k) for k in ("mean", "lower", "upper"))
        ll_low, ll_high, m_low, m_high, ul_low, ul_high = (float(v) for v in np.asarray(found["ci"], dtype=float))
        ccc, c_low, c_high = self._ccc(a, b, level)
        ci = _ci(level)
        way = "higher" if mean > 0 else "lower"
        print(f'"{names[0]}" reads on average {_num(abs(mean))} {way} than "{names[1]}" ({ci} of the difference '
              f"{_num(m_low)} to {_num(m_high)}). For 95 % of rows the difference lies between {_num(lower)} and "
              f"{_num(upper)} (limits of agreement; {ci} of the lower limit {_num(ll_low)} to {_num(ll_high)}, of the "
              f"upper {_num(ul_low)} to {_num(ul_high)}). Whether that is close enough is a question for the field, "
              "not for statistics.")
        print(f"Agreement is not correlation: two ways of measuring can correlate perfectly and still disagree (Bland "
              f"and Altman 1986). Lin's concordance correlation = {_num(ccc)} ({ci} {_num(c_low)} to {_num(c_high)}).")
        print(f'Method: R BlandAltmanLeh::bland.altman.stats() (difference = "{names[0]}" minus "{names[1]}"; limits = '
              f"average difference plus and minus 1.96 standard deviations, {len(a)} rows), DescTools::CCC().")
        return self._result_table({
            "test": "limits of agreement (Bland-Altman)", "what it compares": f'"{names[0]}" minus "{names[1]}"',
            "rows": len(a), "average difference": mean, f"average difference {ci} low": m_low,
            f"average difference {ci} high": m_high, "lower limit": lower, f"lower limit {ci} low": ll_low,
            f"lower limit {ci} high": ll_high, "upper limit": upper, f"upper limit {ci} low": ul_low,
            f"upper limit {ci} high": ul_high, "concordance correlation": ccc,
            f"concordance correlation {ci} low": c_low, f"concordance correlation {ci} high": c_high,
            "method": "R BlandAltmanLeh::bland.altman.stats(), DescTools::CCC()"})

    # ------------------------------------------------------------------ reliability_of
    @friendly
    def reliability_of(self, *columns, interval=95):
        """Do the items of a questionnaire hang together (Cronbach's alpha)?

        table.reliability_of(["item_1", "item_2", "item_3", "item_4", "item_5"])   (with sdata.get_example("clinic"))
        Each column is one item (question), each row one person. Prints Cronbach's alpha with
        Feldt's interval and what alpha would be without each item (R psych::alpha() and
        psych::alpha.ci(), simplydata[r]). Alpha rises with the number of items and does not
        show that the items measure one thing. Gives back one row for alpha and one per item.
        """
        from .._r import r_call

        step = "reliability_of"
        example = 'table.reliability_of(["item_1", "item_2", "item_3", "item_4", "item_5"])'
        names, kept = self._agreement_columns(step, columns, example, at_least=2)
        for n in names:
            if not self._frame.schema[n].is_numeric():
                raise SimplydataError(f'{step}() needs columns of numbers (scores); "{n}" is not.\nFor example, {example}')
        level = _level(step, interval, example)
        matrix = np.column_stack([kept[n].to_numpy().astype(float) for n in names])
        found = r_call("a <- psych::alpha(as.data.frame(x), check.keys = FALSE); "
                       "f <- psych::alpha.ci(a$total$raw_alpha, n.obs = nrow(x), n.var = ncol(x), p.val = 1 - level); "
                       "list(alpha = a$total$raw_alpha, low = f$lower.ci, high = f$upper.ci, drop = a$alpha.drop$raw_alpha)",
                       packages=("psych",), what="Cronbach's alpha (R psych::alpha())",
                       python_note="Python's stack (SciPy, statsmodels) has no Cronbach's alpha with Feldt's interval",
                       x=matrix, level=level / 100)
        alpha, low, high = (_r_numbers(found, k) for k in ("alpha", "low", "high"))
        drop = np.asarray(found["drop"], dtype=float)
        ci = _ci(level)
        best = int(np.argmax(drop))
        print(f"Cronbach's alpha = {_num(alpha)} ({ci} {_num(low)} to {_num(high)}, Feldt) for {len(names)} items and "
              f"{len(matrix)} rows.")
        if drop[best] > alpha:
            print(f'Leaving out "{names[best]}" would raise it to {_num(drop[best])}; check whether that item fits.')
        else:
            print(f"No single item raises alpha when it is left out (the highest without one item is {_num(drop[best])}, "
                  f'without "{names[best]}").')
        print("Alpha rises with the number of items and does not show that the items measure one thing. Method: R "
              "psych::alpha() (raw alpha) and psych::alpha.ci() (Feldt's interval).")
        rows = [{"measure": "Cronbach's alpha", "estimate": alpha, f"estimate {ci} low": low,
                 f"estimate {ci} high": high, "items": len(names), "rows": len(matrix),
                 "method": "R psych::alpha(), psych::alpha.ci() (Feldt)"}]
        rows += [{"measure": f"alpha without {n}", "estimate": float(d), "items": len(names) - 1, "rows": len(matrix),
                  "method": "R psych::alpha() alpha.drop"} for n, d in zip(names, drop)]
        return self._many_rows_table(rows)
