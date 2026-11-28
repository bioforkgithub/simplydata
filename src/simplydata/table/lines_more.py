"""Lines and curves (phase S3a-2): more ways to fit a line or a curve, dose-response curves, the best power
of a column, percentile lines and lines that change at a known point.

Every number comes from a package; nothing is calculated here but the arithmetic of printing:

* fit_line(test_method="theil-sen" / "siegel"): SciPy stats.theilslopes(alpha=0.95, method="separate") and
  stats.siegelslopes(method="hierarchical").
* fit_line(test_method="standardised major axis" / "major axis"): R smatr::sma(); "deming" / "passing-bablok":
  R mcr::mcreg(method.ci = "analytical"). y_error_over_x_error= is the error variance of y over that of x;
  mcr's error.ratio is the other way round (x over y), so it gets 1 / y_error_over_x_error.
* fit_line(with_bends=1): R segmented::segmented(), confint(), slope(), davies.test().
* fit_line(changes_at=37) and explain(..., changes_at={"month": 37}): statsmodels OLS (explain: its usual
  model) with two more columns, "after" (0 before, 1 from the change on) and the time since the change; the
  lag-1 autocorrelation of the leftovers by statsmodels acf().
* fit_curve(of_kind="logistic growth" ...): the formula of R's self-starting model, fitted by the fit_formula
  engine (SciPy least_squares, Levenberg-Marquardt, as R nls()); start values from R stats::getInitial() when R
  is there, else a search of the whole range (SciPy differential evolution, seed 1) within limits taken from
  the data. The least-squares answer is the same either way.
* fit_dose_response: R drc::drm(), drc::ED(interval = "delta"), drc::EDcomp() and drc::noEffect().
* find_best_power_of: one column, SciPy stats.boxcox(alpha=0.05) (power and its 95 % profile-likelihood
  interval) or stats.yeojohnson (power only); with using=, R car::powerTransform() of the model.
* explain(..., for_percentile=90): R quantreg::rq() with summary(se = "nid").
"""

from __future__ import annotations

import contextlib
import io
import math

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, choice_error, friendly


def _st():
    from . import stat_tests

    return stat_tests


def _num(x) -> str:
    return _st()._num(x)


def _p_sentence(*args, **kwargs) -> str:
    from .summaries import _p_sentence as sentence

    return sentence(*args, **kwargs)


def _p_clause(*args, **kwargs) -> str:
    from .summaries import _p_clause as clause

    return clause(*args, **kwargs)


# ---------------------------------------------------------------------------- fit_line(method=)
LINE_METHODS = ("least squares", "standardised major axis", "major axis", "deming", "passing-bablok", "theil-sen",
                "siegel")
LINE_SPELLINGS = {"standardized major axis": "standardised major axis", "sma": "standardised major axis",
                  "reduced major axis": "standardised major axis", "rma": "standardised major axis",
                  "ma": "major axis", "ols": "least squares", "ordinary least squares": "least squares",
                  "passing bablok": "passing-bablok", "paba": "passing-bablok", "theil sen": "theil-sen",
                  "theilsen": "theil-sen", "sen": "theil-sen", "repeated medians": "siegel",
                  "siegel repeated medians": "siegel"}
# the question each line answers (rule S3a-L9)
LINE_QUESTION = {
    "least squares": "it predicts y from x (x is taken as measured without error)",
    "standardised major axis": "it describes how the two measures change together, when both carry error (it "
                               "does not predict one from the other)",
    "major axis": "it describes how the two measures change together, when both carry error and are on the same "
                  "scale (it does not predict one from the other)",
    "deming": "it compares two measurement methods that both carry error, with a known ratio of their error "
              "variances",
    "passing-bablok": "it compares two measurement methods without assuming a shape for their errors, and outliers "
                      "pull it little",
    "theil-sen": "it predicts y from x like least squares, but outliers pull it little (the median of the slopes "
                 "between every pair of points)",
    "siegel": "it predicts y from x like least squares, but outliers pull it even less (repeated medians)",
}


def read_line_method(method) -> str:
    key = method.strip().lower() if isinstance(method, str) else method
    key = LINE_SPELLINGS.get(key, key)
    if key not in LINE_METHODS:
        raise choice_error("fit_line", "test_method", method, list(LINE_METHODS))
    return key


def _line_row(test, x, y, slope, slope_low, slope_high, intercept, intercept_low, intercept_high, n,
              slope_se=math.nan, intercept_se=math.nan, r2=math.nan, p=math.nan, more=None):
    row = {"test": test, "what it compares": f'"{y}" against "{x}"', "slope": float(slope),
           "slope 95 % CI low": float(slope_low), "slope 95 % CI high": float(slope_high),
           "slope standard error": float(slope_se), "intercept": float(intercept),
           "intercept 95 % CI low": float(intercept_low), "intercept 95 % CI high": float(intercept_high),
           "intercept standard error": float(intercept_se), "p-value": float(p), "R squared": float(r2), "rows": n}
    row.update(more or {})
    return row


def _plus(value) -> str:
    """+ 0.372 or - 0.0141: the intercept in a written line."""
    return f"{'-' if value < 0 else '+'} {_num(abs(value))}"


def _ci(low, high) -> str:
    if not (math.isfinite(low) and math.isfinite(high)):
        return "no interval"
    return f"95 % CI {_num(low)} to {_num(high)}"


class LinesMoreWords:
    """fit_dose_response and find_best_power_of, and the new options of fit_line, fit_curve and explain."""

    # ------------------------------------------------------------------ fit_line(method=)
    def _fit_line_other(self, x, y, method, ratio):
        """fit_line with a method other than least squares."""
        step = "fit_line"
        xs, ys = self._number_values(step, [x, y])
        n = len(xs)
        if np.ptp(xs) == 0:
            raise SimplydataError(f'Every number in "{x}" is the same, so no line can be fitted.')
        if method in ("theil-sen", "siegel"):
            return self._theil_sen(x, y, xs, ys, method)
        if method == "passing-bablok":
            if n < 10:
                raise SimplydataError(f'test_method="passing-bablok" needs at least 10 pairs; there are {n}.')
            if np.any(xs < 0) or np.any(ys < 0):
                raise SimplydataError(f'test_method="passing-bablok" works on values of 0 or more (R mcr), and "{x}" or '
                                      f'"{y}" has negative values.')
        elif n < 3:
            raise SimplydataError(f'{step}() needs at least 3 rows with a number in both "{x}" and "{y}".')
        from .lines_r import two_error_line

        out = two_error_line(xs, ys, method, ratio)
        get = {k: float(np.atleast_1d(v)[0]) for k, v in out.items() if k not in ("n",)}
        names = {"standardised major axis": "standardised major axis line (R smatr)",
                 "major axis": "major axis line (R smatr)",
                 "deming": "Deming line (R mcr)", "passing-bablok": "Passing-Bablok line (R mcr)"}
        more = {}
        if method == "deming":
            more = {"y error over x error": float(ratio)}
        row = _line_row(names[method], x, y, get["slope"], get["slope_low"], get["slope_high"], get["intercept"],
                        get["intercept_low"], get["intercept_high"], n, get.get("slope_se", math.nan),
                        get.get("intercept_se", math.nan), get.get("r2", math.nan), get.get("p", math.nan), more)
        direction = "up" if row["slope"] >= 0 else "down"
        print(f'"{y}" goes {direction} by {_num(abs(row["slope"]))} for each 1 more "{x}" ({_ci(row["slope 95 % CI low"], row["slope 95 % CI high"])}), '
              f'by the {method} line.')
        print(f"Line: {y} = {_num(row['slope'])} * {x} {_plus(row['intercept'])} "
              f"(intercept {_ci(row['intercept 95 % CI low'], row['intercept 95 % CI high'])}), over {n} rows.")
        print(f"This line answers another question than least squares: {LINE_QUESTION[method]}.")
        if method in ("standardised major axis", "major axis"):
            r2, p = row["R squared"], row["p-value"]
            print(f"R squared = {r2:.2f} (how closely the two measures go together). "
                  + _p_sentence(p, "the two measures were truly uncorrelated", "a correlation this strong or stronger",
                                "that they are uncorrelated"))
            r_method = "SMA" if method == "standardised major axis" else "MA"
            print(f'Method: R smatr::sma({y} ~ {x}, method = "{r_method}") (Warton et al. 2006); its 95 % intervals. '
                  "Fit both columns on a log scale first (table.add_column) for allometry.")
            if p >= 0.05:
                print("Note: the two measures are hardly correlated, so the slope's size and even its sign are not "
                      f'well pinned down (a {method} slope takes its sign from the correlation).')
        elif method == "deming":
            print(f"Method: R mcr::mcreg(x, y, method.reg = \"Deming\", error.ratio = {_num(1 / ratio)}, "
                  f'method.ci = "analytical"): the variance of the errors in "{y}" is taken as {_num(ratio)} times that '
                  f'in "{x}" (y_error_over_x_error={_num(ratio)}; mcr\'s error.ratio is x over y, so it gets '
                  f"1 / {_num(ratio)}). Intervals by mcr's analytical method.")
        else:
            print('Method: R mcr::mcreg(x, y, method.reg = "PaBa", method.ci = "analytical") (Passing & Bablok 1983); '
                  "the intervals are Passing and Bablok's own, from the ranks of the slopes (no standard errors).")
            if n < 30:
                print(f"Note: Passing-Bablok intervals are wide and rough with fewer than 30 pairs (here {n}).")
        return self._result_table(row)

    def _theil_sen(self, x, y, xs, ys, method):
        from scipy import stats

        n = len(xs)
        if n < 3:
            raise SimplydataError(f'fit_line() needs at least 3 rows with a number in both "{x}" and "{y}".')
        if method == "theil-sen":
            fit = stats.theilslopes(ys, xs, alpha=0.95, method="separate")
            low, high = float(fit.low_slope), float(fit.high_slope)
            test = "Theil-Sen line (SciPy theilslopes)"
        else:
            fit = stats.siegelslopes(ys, xs, method="hierarchical")
            low = high = math.nan
            test = "Siegel repeated-medians line (SciPy siegelslopes)"
        slope, intercept = float(fit.slope), float(fit.intercept)
        row = _line_row(test, x, y, slope, low, high, intercept, math.nan, math.nan, n)
        direction = "up" if slope >= 0 else "down"
        interval = f" ({_ci(low, high)})" if method == "theil-sen" else " (SciPy gives no interval for Siegel's line)"
        print(f'"{y}" goes {direction} by {_num(abs(slope))} for each 1 more "{x}"{interval}, by the {method} line.')
        print(f"Line: {y} = {_num(slope)} * {x} {_plus(intercept)}, over {n} rows. "
              "A link does not show that one thing causes the other.")
        print(f"This line answers the same question as least squares in a way outliers pull little: "
              f"{LINE_QUESTION[method]}.")
        if method == "theil-sen":
            print('Method: SciPy stats.theilslopes(y, x, alpha=0.95, method="separate"): the slope is the median of '
                  "the slopes between every pair of points (pairs with the same x are left out, as R does); its 95 % "
                  "interval by Sen's method; the intercept is median(y) - slope * median(x) (Conover; SciPy's default; "
                  "R mblm takes the median of y - slope * x instead, so its intercept can differ a little). No "
                  "p-value.")
        else:
            print('Method: SciPy stats.siegelslopes(y, x, method="hierarchical"): for each point the median of its '
                  "slopes to the others, then the median of those; no interval and no p-value.")
        return self._result_table(row)

    # ------------------------------------------------------------------ fit_line(with_bends=)
    def _fit_line_bends(self, x, y, how_many):
        step = "fit_line"
        if isinstance(how_many, bool) or not isinstance(how_many, (int, np.integer)) or not 1 <= how_many <= 3:
            raise SimplydataError(f"with_bends= is how many bends the line may have: 1, 2 or 3, not {how_many!r}.\n"
                                  f'For example table.fit_line(x="{x}", y="{y}", with_bends=1)')
        how_many = int(how_many)
        xs, ys = self._number_values(step, [x, y])
        n = len(xs)
        need = 5 * (how_many + 1)
        if n < need:
            raise SimplydataError(f"A line with {how_many} bend{'s' if how_many > 1 else ''} has {how_many + 1} pieces "
                                  f"and needs at least 5 rows for each, so {need} rows; there are {n}.")
        if np.ptp(xs) == 0:
            raise SimplydataError(f'Every number in "{x}" is the same, so no line can be fitted.')
        from .lines_r import SEGMENTED_SEED, bends

        out = bends(xs, ys, how_many)
        davies_p = float(np.atleast_1d(out["davies_p"])[0])
        if not bool(np.atleast_1d(out["found"])[0]):
            print(f"R segmented found no bend in the line of \"{y}\" against \"{x}\"; here is the straight line.")
            print(_p_sentence(davies_p, "the line truly had no bend", "a change of slope this big",
                              "that there is no bend") + " (Davies' test: no bend against at least one)")
            return self.fit_line(x=x, y=y)
        psi = np.atleast_1d(out["psi"]).astype(float)
        psi_low, psi_high = np.atleast_1d(out["psi_low"]).astype(float), np.atleast_1d(out["psi_high"]).astype(float)
        slopes = np.atleast_1d(out["slope"]).astype(float)
        s_low, s_high = np.atleast_1d(out["slope_low"]).astype(float), np.atleast_1d(out["slope_high"]).astype(float)
        s_se = np.atleast_1d(out["slope_se"]).astype(float)
        intercepts = np.atleast_1d(out["intercept"]).astype(float)
        r2 = float(np.atleast_1d(out["r2"])[0])
        row = {"test": "line with bends (R segmented)", "what it compares": f'"{y}" against "{x}"'}
        for i in range(len(psi)):
            row.update({f"bend {i + 1}": psi[i], f"bend {i + 1} 95 % CI low": psi_low[i],
                        f"bend {i + 1} 95 % CI high": psi_high[i]})
        for i in range(len(slopes)):
            row.update({f"slope {i + 1}": slopes[i], f"slope {i + 1} standard error": s_se[i],
                        f"slope {i + 1} 95 % CI low": s_low[i], f"slope {i + 1} 95 % CI high": s_high[i]})
        row.update({"intercept": intercepts[0], "Davies p-value": davies_p,
                    "residual standard error": float(np.atleast_1d(out["sigma"])[0]), "R squared": r2, "rows": n})
        if len(psi) == 1:
            print(f'The line of "{y}" bends at "{x}" = {_num(psi[0])} ({_ci(psi_low[0], psi_high[0])}): slope '
                  f"{_num(slopes[0])} ({_ci(s_low[0], s_high[0])}) before, {_num(slopes[1])} "
                  f"({_ci(s_low[1], s_high[1])}) after.")
        else:
            where = ", ".join(f"{_num(p)} ({_ci(lo, hi)})" for p, lo, hi in zip(psi, psi_low, psi_high))
            print(f'The line of "{y}" bends at "{x}" = {where}.')
            print("Slopes, piece by piece: " + "; ".join(f"{_num(s)} ({_ci(lo, hi)})"
                                                          for s, lo, hi in zip(slopes, s_low, s_high)) + ".")
        print(f"R squared = {r2:.2f}. The line is continuous: it bends, it does not jump (for a jump at a point you "
              "know, use changes_at=).")
        print(_p_sentence(davies_p, "the line truly had no bend", "a change of slope this big",
                          "that there is no bend") + " (Davies' test: no bend against at least one)")
        print(f"Method: R segmented::segmented(lm({y} ~ {x}), seg.Z = ~ {x}, npsi = {how_many}, control = "
              f"seg.control(seed = {SEGMENTED_SEED})) (the seed fixes segmented's random restarts); the bend's 95 % "
              "interval by the delta method (confint), the slopes by segmented::slope(). The data chose where the "
              "bend is, so the ordinary p-value of the bend is not valid; Davies' test (segmented::davies.test) asks "
              "whether there is a bend at all (no bend against at least one).")
        return self._result_table(row)

    # ------------------------------------------------------------------ fit_line(changes_at=)
    def _change_column(self, step, column, at, example):
        """The values of column as numbers (dates as days since the first one), at on the same scale, the words
        saying how dates were turned into numbers, and the first date (None for a column of numbers)."""
        import pandas as pd

        self._need_columns(column)
        dtype = self._frame.schema[column]
        if dtype.is_temporal():
            when = pd.to_datetime(pd.Series(self._frame[column].to_list()))
            first = when.min()
            try:
                at_time = pd.Timestamp(at)
            except (TypeError, ValueError):
                raise SimplydataError(f'changes_at= should be a date like "2005-01-01" when "{column}" holds dates.\n'
                                      f"For example, {example}") from None
            days = ((when - first).dt.total_seconds() / 86400).to_numpy(dtype=float)
            return (days, float((at_time - first).total_seconds() / 86400), f" (dates as days since {first.date()})",
                    first.date())
        if not dtype.is_numeric():
            raise SimplydataError(f'changes_at= needs "{column}" to hold numbers or dates (the time of each row).')
        st = _st()
        if not st._is_number(at) or isinstance(at, bool):
            raise SimplydataError(f'changes_at= is the value of "{column}" where the change happens, a number.\n'
                                  f"For example, {example}")
        values = self._frame[column].cast(nw.Float64).to_numpy().astype(float)
        return values, float(at), "", None

    def _fit_line_changes(self, x, y, at):
        from statsmodels.regression.linear_model import OLS
        from statsmodels.tsa.stattools import acf

        step = "fit_line"
        example = f'table.fit_line(x="{x}", y="{y}", changes_at=37)'
        self._need_columns(x, y)
        xs_all, at_value, how, _ = self._change_column(step, x, at, example)
        frame = self._number_frame(step, [y])
        ys_all = np.array([math.nan if v is None else float(v) for v in frame[y].to_list()])
        keep = np.isfinite(xs_all) & np.isfinite(ys_all)
        _st()._skipped_note(int((~keep).sum()), [x, y])
        order = np.argsort(xs_all[keep], kind="stable")
        xs, ys = xs_all[keep][order], ys_all[keep][order]
        before, after = int((xs < at_value).sum()), int((xs >= at_value).sum())
        if before < 3 or after < 3:
            raise SimplydataError(f"changes_at={at!r} leaves {before} rows before and {after} from the change on; "
                                  "each side needs at least 3.")
        after_col = (xs >= at_value).astype(float)
        since = after_col * (xs - at_value)
        X = np.column_stack([np.ones(len(xs)), xs, after_col, since])
        fit = OLS(ys, X).fit()
        low, high = np.asarray(fit.conf_int(0.05)).T
        b, se, p = np.asarray(fit.params), np.asarray(fit.bse), np.asarray(fit.pvalues)
        lag1 = float(acf(ys - np.asarray(fit.fittedvalues), nlags=1, fft=False)[1])
        later = fit.t_test(np.array([[0.0, 1.0, 0.0, 1.0]]))  # the slope after: slope before + slope change
        after_slope = float(np.asarray(later.effect).ravel()[0])
        after_low, after_high = (float(v) for v in np.asarray(later.conf_int(0.05)).ravel())
        n = len(xs)
        names = ["intercept", "slope before", "level change", "slope change"]
        row = {"test": "line that changes at a known point (least squares)", "what it compares": f'"{y}" against "{x}"',
               "changes at": at if not isinstance(at, (np.generic,)) else at.item()}
        for j, name in enumerate(names):
            row.update({name: float(b[j]), f"{name} standard error": float(se[j]), f"{name} 95 % CI low": float(low[j]),
                        f"{name} 95 % CI high": float(high[j]), f"{name} p-value": float(p[j])})
        row.update({"slope after": after_slope, "slope after 95 % CI low": after_low,
                    "slope after 95 % CI high": after_high, "lag-1 autocorrelation of the leftovers": lag1,
                    "R squared": float(fit.rsquared), "rows": n})
        print(f'Before {at}: "{y}" goes {"up" if b[1] >= 0 else "down"} by {_num(abs(b[1]))} for each 1 more "{x}"'
              f"{how} ({_ci(low[1], high[1])}).")
        print(f"At {at} the level jumps by {_num(b[2])} ({_ci(low[2], high[2])}) and the slope changes by "
              f"{_num(b[3])} ({_ci(low[3], high[3])}), to {_num(after_slope)} after ({_ci(after_low, after_high)}).")
        print("Level change: " + _p_sentence(p[2], "there were truly no jump", "a jump this big or bigger",
                                             "that there is no jump"))
        print("Slope change: " + _p_sentence(p[3], "the slope truly stayed the same", "a change of slope this big",
                                             "that the slope stays the same"))
        print(f"Method: least squares (statsmodels OLS, as R lm({y} ~ {x} + after + since)) with two more columns: "
              f"after (0 before {at}, 1 from it on) and since (how far past {at}, 0 before); an interrupted time "
              f"series over {n} rows ({before} before, {after} after).")
        print(f"Lag-1 autocorrelation of the leftovers (statsmodels acf): {lag1:.2f}. Near 0 is what the intervals "
              "assume; if it is well away from 0, neighbouring rows are alike and the intervals are too narrow "
              f'(look with table.find_autocorrelation_of(...), Bernal et al. 2017).')
        return self._result_table(row)

    # ------------------------------------------------------------------ fit_curve(of_kind=)
    def _fit_curve_kind(self, x, y, kind, weights, for_each):
        from .fitting import fit_formula_core, read_fit_formula
        from .lines_r import SELF_START

        st = _st()
        step = "fit_curve"
        model, names = SELF_START[kind]
        clash = [k for k in names if k in self._columns]
        if clash:
            raise SimplydataError(f'of_kind="{kind}" uses the value names {", ".join(names)}; the table has a column '
                                  f'called "{clash[0]}". Rename it first: table.rename_column("{clash[0]}", ...).')
        xq, yq = (f"`{c}`" if not c.isidentifier() else c for c in (x, y))
        formula = CURVE_FORMULAS[kind].format(x=xq, y=yq if yq == y else y)
        example = f'table.fit_curve(x="{x}", y="{y}", of_kind="{kind}")'
        try:
            parsed = read_fit_formula(formula, self._columns, step)
        except SimplydataError as error:
            raise SimplydataError(f'of_kind="{kind}" could not be written for these columns: {error}') from None
        groups = self._fit_data(step, [x, y], for_each, weights, example)
        from .._r import r_ready

        with_r = r_ready(())
        rows, done, failed = [], [], []
        for label, key, arrays in groups:
            xs, ys = arrays[x], arrays[y]
            w = arrays[weights] if weights is not None else None
            where = f' in group "{label}"' if label is not None else ""
            try:
                if len(xs) < len(names) + 1:
                    raise SimplydataError(f'A {kind} curve has {len(names)} values to find and needs at least '
                                          f"{len(names) + 1} rows{where}; there are {len(xs)}.")
                fit, how = self._kind_fit(kind, parsed, xs, ys, w, weights, with_r, x)
            except SimplydataError as error:
                if label is None:
                    raise
                failed.append((label, str(error).split("\n")[0]))
                continue
            low, high = fit.intervals
            for j, name in enumerate(fit.names):
                row = {} if label is None else {for_each: key}
                row.update({"term": name, "meaning": CURVE_MEANINGS[kind][name], "estimate": float(fit.values[j]),
                            "standard error": float(fit.standard_errors[j]), "statistic name": "t",
                            "statistic": float(fit.t[j]), "degrees of freedom": float(fit.df),
                            "p-value": float(fit.p_values[j]), "95 % CI low": float(low[j]),
                            "95 % CI high": float(high[j]), "residual standard error": fit.sigma, "AIC": fit.aic,
                            "R squared": fit.r2, "rows": fit.n})
                rows.append(row)
            done.append((label, fit, how))
        if not done:
            raise SimplydataError(f"{step}() could not fit a {kind} curve in any group: {failed[0][1]}")

        def values_text(fit):
            low, high = fit.intervals
            return "; ".join(f"{k} = {_num(v)} ({_ci(lo, hi)}): {CURVE_MEANINGS[kind][k]}"
                             for k, v, lo, hi in zip(fit.names, fit.values, low, high))

        if for_each is None:
            fit = done[0][1]
            print(f'Fitted a {kind} curve, {parsed.text}, to {fit.n} rows:')
            print(f"  {values_text(fit)}.")
            print(f"Residual standard error {_num(fit.sigma)} on {fit.df} degrees of freedom; AIC {_num(fit.aic)}; "
                  f"R squared = {fit.r2:.2f} (only a rough guide for a curve).")
        else:
            print(f'Fitted a {kind} curve, {parsed.text}, for each "{for_each}":')
            for label, fit, _ in done[:st.GROUPS_SHOWN]:
                print(f"  {label} ({fit.n} rows): {values_text(fit)}.")
            if len(done) > st.GROUPS_SHOWN:
                print(f"  ... and {len(done) - st.GROUPS_SHOWN} more groups (the table has them all)")
        weighted = f', weights = {weights}' if weights is not None else ""
        print(f"Method: nonlinear least squares, as R nls({y} ~ {model}({x}, {', '.join(names)}){weighted}); "
              f"{done[0][2]}. Intervals are estimate +/- t x standard error.")
        for label, problem in failed:
            print(f'Note: group "{label}" was not fitted: {problem}')
        for label, fit, _ in done:
            where = "" if label is None else f'In group "{label}": '
            for note in fit.notes:
                print(note if not where else note.replace("Note: ", f"Note: {where}", 1))
        return self._rows_table(rows)

    @classmethod
    def _kind_fit(cls, kind, parsed, xs, ys, w, weights_name, with_r, x):
        """One fit of a self-starting curve; for "two exponentials" the fast part comes first (lrc1 > lrc2), as
        R's SSbiexp names them, so the two parts are always reported the same way round."""
        fit, how = cls._kind_fit_once(kind, parsed, xs, ys, w, weights_name, with_r, x)
        if kind == "two exponentials" and fit.value_dict["lrc1"] < fit.value_dict["lrc2"]:
            from .fitting import fit_formula_core

            v = fit.value_dict
            start = {"A1": v["A2"], "lrc1": v["lrc2"], "A2": v["A1"], "lrc2": v["lrc1"]}
            data = {x: xs, parsed.left: ys}
            if weights_name is not None:
                data[weights_name] = w
            fit = fit_formula_core(parsed, data, list(data), start=start, weights=w, step="fit_curve",
                                   weights_name=weights_name)
        return fit, how

    @staticmethod
    def _kind_fit_once(kind, parsed, xs, ys, w, weights_name, with_r, x):
        """One fit of a self-starting curve: from R's start values, or a search of the whole range without R."""
        from .fitting import fit_formula_core
        from .lines_r import SELF_START, self_start

        model = SELF_START[kind][0]
        data = {x: xs, parsed.left: ys}
        if weights_name is not None:
            data[weights_name] = w
        start = self_start(kind, xs, ys) if with_r else None
        if start is not None:
            try:
                fit = fit_formula_core(parsed, data, list(data), start=start, weights=w, step="fit_curve",
                                       weights_name=weights_name)
                return fit, (f"start values from R's self-starting model {model} (stats::getInitial()), then "
                             f"Levenberg-Marquardt (SciPy least_squares), as R nls() would")
            except SimplydataError:
                pass  # R's start did not lead to a fit: search the whole range instead
        between = _search_limits(kind, xs, ys)
        try:
            fit = fit_formula_core(parsed, data, list(data), between=between, weights=w, search="whole range",
                                   step="fit_curve", weights_name=weights_name)
        except SimplydataError:
            raise SimplydataError(
                f"simplydata could not fit a {kind} curve to these data: the search did not settle. Check that the "
                f"data have this shape (draw them first), or fit the formula yourself with start values: "
                f'table.fit_formula("{parsed.text}", start={{...}}).') from None
        return fit, ("start found by a search of the whole range (SciPy differential evolution, seed 1, within limits "
                     "taken from the data, as R is not there to give start values), then trust region least squares")

    # ------------------------------------------------------------------ fit_dose_response
    @friendly
    def fit_dose_response(self, x=None, y=None, doses_for_effect=None, of_kind=None, outcome="numbers", out_of=None,
                          for_each_group_in=None):
        """Fit a dose-response curve and find the dose for 50 % of the effect (ED50, EC50, LD50).

        table.fit_dose_response(x="concentration", y="root_length")   (with sdata.get_example("toxicity"))
        Fits a 4 parameter log-logistic curve (R drc::drm(fct = LL.4()), the usual curve in
        ecotoxicology) and prints the ED50 with its 95 % interval (delta method, R drc::ED()), the
        upper and lower limits and the steepness. doses_for_effect=[10, 50, 90] gives ED10, ED50
        and ED90: the doses where the response has moved 10, 50 and 90 % of the way from the upper
        limit to the lower one. of_kind= "4 parameter log-logistic" (the default), "3 parameter
        log-logistic" (lower limit 0), "5 parameter log-logistic" (not symmetric) or "weibull".
        outcome="yes or no", out_of="exposed": y holds how many died (or answered yes) out of
        out_of in each row: LD50, with a 2 parameter log-logistic curve from 0 to 100 % (R drm(type
        = "binomial")). for_each_group_in="chemical" fits one curve per group in one model and
        compares their ED50s (relative potency, R drc::EDcomp()). Needs R with drc
        (pip install "simplydata[r]"; in R: install.packages("drc")). Gives back one row per
        value of the curve and per ED. The same curve on a chart: chart.fit_dose_response().
        """
        return dose_response_word(self, x, y, doses_for_effect, of_kind, outcome, out_of, for_each_group_in)

    # ------------------------------------------------------------------ find_best_power_of
    @friendly(renamed={"method": "test_method"})
    def find_best_power_of(self, column=None, using=None, test_method="box-cox", show="power"):
        """Find the power to raise a column to that brings it closest to a normal shape (Box-Cox).

        table.find_best_power_of("days")   (with sdata.get_example("trial"))
        Box-Cox finds the power by maximum likelihood (SciPy stats.boxcox), with its 95 %
        interval: power 1 is no change, 0.5 the square root, 0 the log, -1 one over the value.
        It names the simple power inside the interval nearest to the best one, and says whether
        log (0) and no change (1) are inside it. using=["treatment"] finds the power that brings
        the leftovers of the model explain(column, using=) closest to a normal shape (R
        car::powerTransform(), needs R), with likelihood-ratio tests of power 0 and 1.
        test_method="yeo-johnson" (SciPy stats.yeojohnson) works with zeros and negative values too.
        Box-Cox needs values above 0. For counts or shares, a model made for them
        (explain(..., outcome=)) is usually better than a power. Gives back one row.
        show="log-likelihood" gives a table of the log-likelihood of each power from -2 to 2 (SciPy boxcox_llf,
        yeojohnson_llf), show="normal plot correlation" how straight the normal probability plot is for each
        (boxcox_normplot, yeojohnson_normplot), and show="best by normal plot" the Box-Cox power with the
        straightest plot (boxcox_normmax(method="pearsonr")). test_method="tukey lambda" finds the Tukey lambda
        shape with the straightest probability plot (SciPy ppcc_max: lambda 0.14 is about normal, 0 logistic, -1
        Cauchy), and with show="normal plot correlation" the table of each lambda (ppcc_plot).
        """
        return best_power_word(self, column, using, test_method, show)


# ---------------------------------------------------------------------------- fit_curve(of_kind=)
CURVE_KINDS = ("logistic growth", "4 parameter logistic", "michaelis-menten", "rise to a limit",
               "rise or fall to a limit", "gompertz growth", "weibull growth", "two exponentials")
CURVE_SPELLINGS = {"logistic": "logistic growth", "sslogis": "logistic growth", "gompertz": "gompertz growth",
                   "ssgompertz": "gompertz growth", "weibull": "weibull growth", "ssweibull": "weibull growth",
                   "michaelis menten": "michaelis-menten", "ssmicmen": "michaelis-menten",
                   "four parameter logistic": "4 parameter logistic", "ssfpl": "4 parameter logistic",
                   "ssasymporig": "rise to a limit", "ssasymp": "rise or fall to a limit",
                   "biexponential": "two exponentials", "ssbiexp": "two exponentials"}
CURVE_FORMULAS = {
    "logistic growth": "{y} = Asym / (1 + exp((xmid - {x}) / scal))",
    "4 parameter logistic": "{y} = A + (B - A) / (1 + exp((xmid - {x}) / scal))",
    "michaelis-menten": "{y} = Vm * {x} / (K + {x})",
    "rise to a limit": "{y} = Asym * (1 - exp(-exp(lrc) * {x}))",
    "rise or fall to a limit": "{y} = Asym + (R0 - Asym) * exp(-exp(lrc) * {x})",
    "gompertz growth": "{y} = Asym * exp(-b2 * b3 ** {x})",
    "weibull growth": "{y} = Asym - Drop * exp(-exp(lrc) * {x} ** pwr)",
    "two exponentials": "{y} = A1 * exp(-exp(lrc1) * {x}) + A2 * exp(-exp(lrc2) * {x})",
}
CURVE_MEANINGS = {
    "logistic growth": {"Asym": "the level the curve levels off at", "xmid": "the x where it is half way up",
                        "scal": "the x it takes to go from half way to 73 % of the way (smaller is steeper)"},
    "4 parameter logistic": {"A": "the level at the far left", "B": "the level at the far right",
                             "xmid": "the x half way between them", "scal": "the x it takes to go from half way to "
                                                                            "73 % of the way (smaller is steeper)"},
    "michaelis-menten": {"Vm": "the highest rate, reached at very high x", "K": "the x at half the highest rate"},
    "rise to a limit": {"Asym": "the level the curve rises to", "lrc": "the log of the rate it rises at"},
    "rise or fall to a limit": {"Asym": "the level the curve goes to", "R0": "the value at x = 0",
                                "lrc": "the log of the rate it gets there"},
    "gompertz growth": {"Asym": "the level the curve levels off at", "b2": "how far below the level it starts",
                        "b3": "how slowly it grows (between 0 and 1; smaller is faster)"},
    "weibull growth": {"Asym": "the level the curve rises to", "Drop": "how far below that level it starts",
                       "lrc": "the log of the rate it rises at", "pwr": "the power of x (the shape of the rise)"},
    "two exponentials": {"A1": "the size of the fast part", "lrc1": "the log of the fast rate",
                         "A2": "the size of the slow part", "lrc2": "the log of the slow rate"},
}


def read_curve_kind(of_kind) -> str:
    key = of_kind.strip().lower() if isinstance(of_kind, str) else of_kind
    key = CURVE_SPELLINGS.get(key, key)
    if key not in CURVE_KINDS:
        raise choice_error("fit_curve", "of_kind", of_kind, list(CURVE_KINDS))
    return key


def _search_limits(kind, xs, ys) -> dict:
    """Wide limits for the whole-range search, taken from the data (used only when R is not there)."""
    xr = float(np.ptp(xs)) or 1.0
    top = 10 * float(np.max(np.abs(ys))) or 10.0
    xlo, xhi = float(np.min(xs)) - xr, float(np.max(xs)) + xr
    rate = math.log(1e4 / xr)  # rates up to 10 000 per range of x
    slow = math.log(1e-4 / xr)
    limits = {
        "logistic growth": {"Asym": [-top, top], "xmid": [xlo, xhi], "scal": [xr / 1e4, 10 * xr]},
        "4 parameter logistic": {"A": [-top, top], "B": [-top, top], "xmid": [xlo, xhi], "scal": [xr / 1e4, 10 * xr]},
        "michaelis-menten": {"Vm": [-top, top], "K": [-10 * float(np.max(np.abs(xs))) - xr, 10 * float(np.max(np.abs(xs))) + xr]},
        "rise to a limit": {"Asym": [-top, top], "lrc": [slow, rate]},
        "rise or fall to a limit": {"Asym": [-top, top], "R0": [-top, top], "lrc": [slow, rate]},
        "gompertz growth": {"Asym": [-top, top], "b2": [1e-4, 1e4], "b3": [1e-6, 1 - 1e-9]},
        "weibull growth": {"Asym": [-top, top], "Drop": [-top, top], "lrc": [slow - 5, rate + 5], "pwr": [0.05, 20]},
        "two exponentials": {"A1": [-top, top], "lrc1": [slow, rate], "A2": [-top, top], "lrc2": [slow, rate]},
    }
    return limits[kind]


# ---------------------------------------------------------------------------- fit_dose_response
DOSE_KINDS = ("4 parameter log-logistic", "3 parameter log-logistic", "5 parameter log-logistic", "weibull",
              "2 parameter log-logistic")
DOSE_SPELLINGS = {"ll.4": "4 parameter log-logistic", "ll4": "4 parameter log-logistic",
                  "ll.3": "3 parameter log-logistic", "ll3": "3 parameter log-logistic",
                  "ll.5": "5 parameter log-logistic", "ll5": "5 parameter log-logistic",
                  "ll.2": "2 parameter log-logistic", "ll2": "2 parameter log-logistic",
                  "log-logistic": "4 parameter log-logistic", "log logistic": "4 parameter log-logistic",
                  "w1.4": "weibull", "weibull 4 parameters": "weibull",
                  "logit": "2 parameter log-logistic", "logistic regression on log dose": "2 parameter log-logistic"}
DOSE_VALUES = {"4 parameter log-logistic": 4, "3 parameter log-logistic": 3, "5 parameter log-logistic": 5,
               "weibull": 4, "2 parameter log-logistic": 2}
DOSE_OUTCOMES = ("numbers", "yes or no")
PARAMETER_WORDS = {"b": "steepness", "c": "lower limit", "d": "upper limit", "e": "ED50", "f": "asymmetry"}


def read_dose_kind(of_kind, outcome) -> str:
    if of_kind is None:
        return "2 parameter log-logistic" if outcome == "yes or no" else "4 parameter log-logistic"
    key = of_kind.strip().lower() if isinstance(of_kind, str) else of_kind
    key = DOSE_SPELLINGS.get(key, key)
    if key not in DOSE_KINDS:
        raise choice_error("fit_dose_response", "of_kind", of_kind, list(DOSE_KINDS))
    if key == "2 parameter log-logistic" and outcome != "yes or no":
        raise SimplydataError('of_kind="2 parameter log-logistic" (limits fixed at 0 and 1) goes with outcome="yes or '
                              'no". For numbers use "4 parameter log-logistic" or "3 parameter log-logistic".')
    return key


def _read_percents(doses_for_effect) -> list[float]:
    if doses_for_effect is None:
        return [50.0]
    st = _st()
    items = doses_for_effect if isinstance(doses_for_effect, (list, tuple)) else [doses_for_effect]
    if not items or not all(st._is_number(p) and not isinstance(p, bool) and 0 < p < 100 for p in items):
        raise SimplydataError("doses_for_effect= gives the percents of the effect, between 0 and 100, for example "
                              "doses_for_effect=[10, 50, 90] for ED10, ED50 and ED90.")
    return [float(p) for p in dict.fromkeys(items)]


def _p_word(p) -> str:
    return f"{p:g}"


def dose_response_word(table, x, y, doses_for_effect, of_kind, outcome, out_of, for_each):
    from .lines_r import dose_response

    st = _st()
    step = "fit_dose_response"
    example = ('with sdata.get_example("toxicity"): table.fit_dose_response(x="concentration", y="root_length")')
    table._need_name(step, "x= (the doses)", x, example)
    table._need_name(step, "y= (the response)", y, example)
    if x == y:
        raise SimplydataError(f"{step}() needs two different columns, for example {example}.")
    table._check_choice(step, "outcome", outcome, DOSE_OUTCOMES)
    kind = read_dose_kind(of_kind, outcome)
    percents = _read_percents(doses_for_effect)
    if outcome == "yes or no" and out_of is None:
        raise SimplydataError(f'outcome="yes or no" needs out_of= the column with how many were exposed in each row; '
                              f'"{y}" then holds how many died (or answered yes).\nFor example, '
                              f'table.fit_dose_response(x="concentration", y="dead", outcome="yes or no", '
                              f'out_of="seedlings")')
    if out_of is not None and outcome != "yes or no":
        raise SimplydataError('out_of= (how many were exposed in each row) goes with outcome="yes or no".')
    columns = [x, y] + ([out_of] if out_of is not None else [])
    if out_of is not None:
        table._need_name(step, "out_of=", out_of, example)
    groups = table._fit_data(step, columns, for_each, None, example)
    dose = np.concatenate([a[x] for _, _, a in groups])
    response = np.concatenate([a[y] for _, _, a in groups])
    trials = np.concatenate([a[out_of] for _, _, a in groups]) if out_of is not None else None
    labels = np.concatenate([[str(label)] * len(a[x]) for label, _, a in groups]) if for_each is not None else None
    if np.any(dose < 0):
        raise SimplydataError(f'"{x}" has negative doses; a dose-response curve needs doses of 0 or more.')
    values = DOSE_VALUES[kind]
    for label, _, a in groups:
        where = f' in group "{label}"' if label is not None else ""
        different = len(np.unique(a[x]))
        if different < values + 1:
            raise SimplydataError(f"A {kind} curve has {values} values to estimate and needs at least {values + 1} "
                                  f"different doses{where}; there are {different}.")
    if trials is not None:
        if np.any(trials <= 0) or np.any(response < 0) or np.any(response > trials) or \
                np.any(response != np.round(response)) or np.any(trials != np.round(trials)):
            raise SimplydataError(f'outcome="yes or no": "{y}" should hold whole numbers from 0 up to the number in '
                                  f'"{out_of}" (how many were exposed, above 0) in every row.')
    try:
        out = dose_response(dose, response, kind, percents, trials=trials, groups=labels)
    except SimplydataError as error:
        if "R stopped" in str(error):
            raise SimplydataError(f'R drc could not fit a {kind} curve: the response does not seem to change with '
                                  f'the dose, so there is no ED50 to find. Draw the data first: sdata.chart(...)'
                                  f'.draw_dots(x="{x}", y="{y}").\n({str(error).splitlines()[0]})') from None
        raise
    arr = {k: np.atleast_1d(v) for k, v in out.items()}
    binomial = trials is not None

    rows = []
    shown = {}
    for name, est, se, t, p, lo, hi in zip(arr["names"], arr["estimate"], arr["se"], arr["t"], arr["p"], arr["low"],
                                          arr["high"]):
        letter, _, group = str(name).partition(":")
        group = None if group == "(Intercept)" else group
        word = PARAMETER_WORDS.get(letter, letter)
        if letter == "e" and kind in ("5 parameter log-logistic", "weibull"):
            word = "a location value (not the ED50 for this curve)"
        row = {} if for_each is None else {for_each: group}
        row.update({"term": f"{letter} ({word})", "estimate": float(est), "standard error": float(se),
                    "statistic": float(t), "p-value": float(p), "95 % CI low": float(lo), "95 % CI high": float(hi)})
        rows.append(row)
        shown[(group, letter)] = (float(est), float(lo), float(hi))
    eds = {}
    below_zero = []
    for name, est, se, lo, hi in zip(arr["ed_names"], arr["ed"], arr["ed_se"], arr["ed_low"], arr["ed_high"]):
        parts = str(name).split(":")
        group = None if for_each is None else parts[1]
        percent = float(parts[-1])
        row = {} if for_each is None else {for_each: group}
        row.update({"term": f"ED{_p_word(percent)}", "estimate": float(est), "standard error": float(se),
                    "statistic": math.nan, "p-value": math.nan, "95 % CI low": float(lo), "95 % CI high": float(hi)})
        rows.append(row)
        eds[(group, percent)] = (float(est), float(lo), float(hi))
        if lo < 0:
            below_zero.append(f"ED{_p_word(percent)}" + ("" if group is None else f" of {group}"))
    n = int(arr["n"][0])
    for row in rows:
        row["rows"] = n
    what = {"4 parameter log-logistic": "4 parameter log-logistic (R LL.4)",
            "3 parameter log-logistic": "3 parameter log-logistic, lower limit 0 (R LL.3)",
            "5 parameter log-logistic": "5 parameter log-logistic (R LL.5)", "weibull": "4 parameter Weibull (R W1.4)",
            "2 parameter log-logistic": "2 parameter log-logistic, from 0 to 100 % (R LL.2)"}[kind]
    group_names = [str(g) for g in dict.fromkeys(labels.tolist())] if for_each is not None else [None]
    print(f'Fitted a {what} dose-response curve of "{y}"' + (f' out of "{out_of}"' if binomial else "")
          + f' against the dose "{x}" ({n} rows' + (f', one curve for each "{for_each}"' if for_each else "") + ").")
    effect = "answer yes" if binomial else "of the effect"
    tested = (float(np.min(dose[dose > 0])) if np.any(dose > 0) else 0.0, float(np.max(dose)))
    outside = []
    for g in group_names:
        lead = f"  {g}: " if g is not None else ""
        parts = []
        for percent in percents:
            est, lo, hi = eds[(g, percent)]
            name = f"ED{_p_word(percent)}"
            if binomial:
                parts.append(f"the dose at which {_p_word(percent)} % answer yes ({name}; LD{_p_word(percent)} when yes "
                             f"is death) is {_num(est)} ({_ci(lo, hi)})")
            else:
                parts.append(f"the dose for {_p_word(percent)} % of the effect ({name}) is {_num(est)} ({_ci(lo, hi)})")
            if est > tested[1] or est < tested[0]:
                outside.append(f"{name}{'' if g is None else ' of ' + g} ({_num(est)})")
        text = "; ".join(parts)
        print(lead + text[0].upper() + text[1:] + ".")
        limits = []
        if (g, "d") in shown:
            limits.append(f"upper limit {_num(shown[(g, 'd')][0])} ({_ci(*shown[(g, 'd')][1:])})")
        if (g, "c") in shown:
            limits.append(f"lower limit {_num(shown[(g, 'c')][0])} ({_ci(*shown[(g, 'c')][1:])})")
        elif kind == "3 parameter log-logistic":
            limits.append("lower limit fixed at 0")
        if (g, "b") in shown:
            limits.append(f"steepness b = {_num(shown[(g, 'b')][0])}")
        if not binomial:
            print(("    " if g is not None else "") + "The curve: " + ", ".join(limits) + ".")
    if not binomial:
        b_values = [v[0] for (g, letter), v in shown.items() if letter == "b"]
        if b_values and all(b > 0 for b in b_values):
            way = "the response falls with dose: from the upper limit (no dose) to the lower limit (very high doses)"
        elif b_values and all(b < 0 for b in b_values):
            way = "the response rises with dose: from the lower limit (no dose) to the upper limit (very high doses)"
        else:
            way = "from the level at no dose to the level at very high doses (the curves run different ways)"
        print(f'"Effect" is the share of the way {way}; b is drc\'s steepness (how fast the response changes around '
              "the ED50 on a log dose scale; above 0 it falls, below 0 it rises).")
    if "ratio" in arr:
        for name, ratio, lo, hi, p, rse in zip(arr["ratio_names"], arr["ratio"], arr["ratio_low"], arr["ratio_high"],
                                                arr["ratio_p"], arr["ratio_se"]):
            pair = str(name).split(":")[0]
            a, _, b = pair.partition("/")
            print(f"ED50 of {a} / ED50 of {b} = {_num(ratio)} ({_ci(lo, hi)}): {a} needs {_num(ratio)} times the dose "
                  f"of {b} for the same effect (relative potency).")
            print("  " + _p_sentence(float(p), "the two ED50s were truly equal", "a ratio this far from 1",
                                     "that they are equal"))
            rows.append({for_each: pair, "term": "ED50 ratio", "estimate": float(ratio),
                         "standard error": float(rse), "statistic": math.nan, "p-value": float(p),
                         "95 % CI low": float(lo), "95 % CI high": float(hi), "rows": n})
    print("Dose effect: " + _p_sentence(float(arr["no_effect_p"][0]), "the dose truly had no effect",
                                        "a change with dose this big", "that the dose has no effect")
          + " (drc::noEffect, a likelihood-ratio test)")
    r_options = (f", weights = {out_of}, type = \"binomial\"" if binomial else "") + \
                (f", curveid = {for_each}" if for_each else "")
    left = f"{y} / {out_of}" if binomial else y
    percent_text = ", ".join(_p_word(p) for p in percents)
    print(f"Method: R drc::drm({left} ~ {x}{r_options}, fct = {DRC_FCT[kind]}(), control = drc::drmc(relTol = "
          "1e-15, maxIt = 10000)) (Ritz et al. 2015); "
          f"drc::ED(m, c({percent_text}), interval = \"delta\"). simplydata chooses the "
          f"{'2 parameter log-logistic curve (from 0 to 100 %)' if binomial and kind == '2 parameter log-logistic' else kind + ' curve'} "
          "and delta-method intervals (drc's ED() gives none unless asked)"
          + ("; one model for all groups, with one residual spread" if for_each and not binomial else "") + ".")
    if below_zero:
        print(f"Note: the 95 % interval of {st._list_words(below_zero)} reaches below 0, which no dose can be: the "
              "delta-method interval is symmetric and only a rough guide here (more doses near it would help).")
    if outside:
        print(f"Note: {st._list_words(outside)} {'is' if len(outside) == 1 else 'are'} outside the doses tested "
              f"({_num(tested[0])} to {_num(tested[1])}): an extrapolation.")
    return table._rows_table(rows)


DRC_FCT = {"4 parameter log-logistic": "LL.4", "3 parameter log-logistic": "LL.3", "5 parameter log-logistic": "LL.5",
           "2 parameter log-logistic": "LL.2", "weibull": "W1.4"}


# ---------------------------------------------------------------------------- find_best_power_of
POWER_METHODS = ("box-cox", "yeo-johnson",
                 # families for 100 %, batches 3-4 (approved by Manish 2026-11-28): SciPy ppcc_max / ppcc_plot
                 "tukey lambda")
POWER_SPELLINGS = {"boxcox": "box-cox", "box cox": "box-cox", "yeojohnson": "yeo-johnson",
                   "yeo johnson": "yeo-johnson", "boxcox_normmax": "box-cox", "yeojohnson_normmax": "yeo-johnson",
                   "ppcc": "tukey lambda", "ppcc_max": "tukey lambda", "tukeylambda": "tukey lambda"}
# find_best_power_of(show=): families for 100 %, batches 3-4; the tables are for the powers -2 to 2 in steps of 0.1
POWER_SHOWS = ("power", "log-likelihood", "normal plot correlation", "best by normal plot")
POWER_SHOW_SPELLINGS = {"llf": "log-likelihood", "boxcox_llf": "log-likelihood", "yeojohnson_llf": "log-likelihood",
                        "normplot": "normal plot correlation", "boxcox_normplot": "normal plot correlation",
                        "yeojohnson_normplot": "normal plot correlation", "ppcc_plot": "normal plot correlation",
                        "probability plot correlation": "normal plot correlation", "pearsonr": "best by normal plot"}
POWER_GRID = (-2.0, 2.0, 41)
SIMPLE_POWERS = (1.0, 0.0, -1.0, 0.5, -0.5, 2.0, -2.0)


def _power_words(power, column) -> str:
    return {1.0: "no change", 0.5: f"the square root of {column}", 0.0: f"log({column})", -0.5: f"1 / square root of "
            f"{column}", -1.0: f"1 / {column}", 2.0: f"{column} squared", -2.0: f"1 / {column} squared"}.get(
        float(power), f"{column} ** {_num(power)}")


def best_power_word(table, column, using, method, show="power"):
    from scipy import stats

    step = "find_best_power_of"
    example = 'with sdata.get_example("trial"): table.find_best_power_of("days")'
    table._need_name(step, "the column", column, example)
    key = method.strip().lower() if isinstance(method, str) else method
    key = POWER_SPELLINGS.get(key, key)
    if key not in POWER_METHODS:
        raise choice_error(step, "test_method", method, list(POWER_METHODS))
    shown = show.strip().lower() if isinstance(show, str) else show
    shown = POWER_SHOW_SPELLINGS.get(shown, shown)
    if shown not in POWER_SHOWS:
        raise choice_error(step, "show", show, list(POWER_SHOWS))
    if (shown != "power" or key == "tukey lambda") and using is not None:
        raise SimplydataError(f'using= finds the power for the leftovers of a model (R car); show="{shown}" and '
                              'test_method="tukey lambda" work on the column itself: leave out using=.')
    if shown != "power" or key == "tukey lambda":
        return _power_more(table, step, column, key, shown, example)
    if using is None:
        values = table._number_values(step, [column])[0]
        X = None
    else:
        values, X = _model_rows(table, step, column, using)
    n = len(values)
    if n < 10:
        raise SimplydataError(f"{step}() needs at least 10 values to find a power; there are {n}.")
    if key == "box-cox" and np.any(values <= 0):
        call = (f'table.{step}("{column}", test_method="yeo-johnson")' if using is None else
                f'table.{step}("{column}", using={using!r}, test_method="yeo-johnson")')
        raise SimplydataError(f'Box-Cox needs values above 0, and "{column}" has {int(np.sum(values <= 0))} at 0 or '
                              f"below. Yeo-Johnson works with them:\n{call}")
    p0 = p1 = math.nan
    if X is None:
        if key == "box-cox":
            _, power, (low, high) = stats.boxcox(values, alpha=0.05)
            how = ('SciPy stats.boxcox(x, alpha=0.05): the power by maximum likelihood, its 95 % interval from the '
                   "profile likelihood (as R MASS::boxcox)")
        else:
            _, power = stats.yeojohnson(values)
            low = high = math.nan
            how = ("SciPy stats.yeojohnson(x): the power by maximum likelihood (SciPy gives no interval; with R, "
                   "car::powerTransform(x ~ 1, family = \"yjPower\") gives a Wald interval)")
        power, low, high = float(power), float(low), float(high)
        simple = _simple_power(power, low, high)
        target = f'the values of "{column}"'
    else:
        from .lines_r import power_transform

        out = power_transform(X, values, "bcPower" if key == "box-cox" else "yjPower")
        got = {k: float(np.atleast_1d(v)[0]) for k, v in out.items()}
        power, low, high, simple = got["power"], got["low"], got["high"], got["rounded"]
        p0, p1 = got["p0"], got["p1"]
        family = "bcPower" if key == "box-cox" else "yjPower"
        how = (f'R car::powerTransform(lm({column} ~ {" + ".join(using if isinstance(using, list) else [using])}), '
               f'family = "{family}"): the power by maximum likelihood with its Wald 95 % interval, the rounded power '
               "car suggests, and likelihood-ratio tests of power 0 and 1 (car::testTransform)")
        target = f'the leftovers of the model explain("{column}", using={using!r})'
    name = "Box-Cox" if key == "box-cox" else "Yeo-Johnson"
    row = {"test": f"best power ({name})", "column": column, "power": power, "95 % CI low": low, "95 % CI high": high,
           "simple power": simple, "rows": n}
    if X is not None:
        row.update({"p-value for power 0 (log)": p0, "p-value for power 1 (no change)": p1})
    interval = f" ({_ci(low, high)})" if math.isfinite(low) else ""
    print(f"Best power ({name}): {_num(power)}{interval}: the power that brings {target} closest to a normal shape.")
    if math.isfinite(simple):
        words = _power_words(simple, column) if key == "box-cox" else f"power {_num(simple)} (Yeo-Johnson)"
        print(f"A nearby simple choice: {words} (power {simple:g}).")
    if math.isfinite(low):
        for p_, words in ((0.0, "log (power 0)"), (1.0, "no change (power 1)")):
            inside = low <= p_ <= high
            print(f"  {words[0].upper() + words[1:]} is {'inside' if inside else 'outside'} the interval.")
    if X is not None:
        print("Log: " + _p_sentence(p0, "the log (power 0) were truly right", "a best power this far from 0",
                                    "that the log is right"))
        print("No change: " + _p_sentence(p1, "no change (power 1) were truly right", "a best power this far from 1",
                                          "that no change is needed"))
    print(f"Method: {how}.")
    print("Note: for counts or shares, a model made for them (explain(..., outcome=\"counts\" or \"shares\")) is "
          "usually better than a power.")
    return table._result_table(row)


def _power_more(table, step, column, key, shown, example):
    """find_best_power_of(show="log-likelihood" | "normal plot correlation" | "best by normal plot") and
    test_method="tukey lambda": SciPy boxcox_llf, yeojohnson_llf, boxcox_normplot, yeojohnson_normplot,
    boxcox_normmax(method="pearsonr"), ppcc_max and ppcc_plot."""
    from scipy import stats

    values = table._number_values(step, [column])[0]
    n = len(values)
    if n < 10:
        raise SimplydataError(f"{step}() needs at least 10 values to find a power; there are {n}.")
    if key == "box-cox" and np.any(values <= 0):
        raise SimplydataError(f'Box-Cox needs values above 0, and "{column}" has {int(np.sum(values <= 0))} at 0 or '
                              f'below. Yeo-Johnson works with them: table.{step}("{column}", '
                              f'test_method="yeo-johnson", show="{shown}")')
    name = {"box-cox": "Box-Cox", "yeo-johnson": "Yeo-Johnson", "tukey lambda": "Tukey lambda"}[key]
    powers = np.linspace(*POWER_GRID)
    if shown == "log-likelihood":
        if key == "tukey lambda":
            raise SimplydataError('show="log-likelihood" is for test_method="box-cox" or "yeo-johnson".')
        function = stats.boxcox_llf if key == "box-cox" else stats.yeojohnson_llf
        found = np.asarray([float(function(p, values)) for p in powers])
        best = float(powers[int(np.argmax(found))])
        print(f'The log-likelihood of each {name} power from -2 to 2 for "{column}" ({n} values): highest at '
              f"{best:g} among them (SciPy {'boxcox_llf' if key == 'box-cox' else 'yeojohnson_llf'}); the best power "
              'itself comes from show="power".')
        data = {"power": powers.round(10).tolist(), "log-likelihood": found.tolist()}
        return table._new_table(nw.from_dict(data, backend=table._frame.implementation))
    if shown == "normal plot correlation":
        if key == "tukey lambda":
            found_powers, found = stats.ppcc_plot(values, POWER_GRID[0], POWER_GRID[1], dist="tukeylambda",
                                                  N=POWER_GRID[2])
            what = "Tukey lambda shape"
            how = "SciPy ppcc_plot(dist=\"tukeylambda\")"
        else:
            function = stats.boxcox_normplot if key == "box-cox" else stats.yeojohnson_normplot
            found_powers, found = function(values, POWER_GRID[0], POWER_GRID[1], N=POWER_GRID[2])
            what = f"{name} power"
            how = f"SciPy {'boxcox_normplot' if key == 'box-cox' else 'yeojohnson_normplot'}"
        best = float(found_powers[int(np.argmax(found))])
        print(f'How straight the normal probability plot of "{column}" is (its correlation) for each {what} from -2 '
              f"to 2: straightest at {best:g} among them ({how}).")
        data = {"power" if key != "tukey lambda" else "lambda": np.asarray(found_powers).round(10).tolist(),
                "normal plot correlation": np.asarray(found, dtype=float).tolist()}
        return table._new_table(nw.from_dict(data, backend=table._frame.implementation))
    if key == "tukey lambda":
        if shown == "best by normal plot":
            raise SimplydataError('test_method="tukey lambda" already finds the best shape by the probability plot; '
                                  'leave out show=.')
        best = float(stats.ppcc_max(values))
        kind = ("close to a Cauchy shape (very long tails)" if best < -0.5 else
                "close to a logistic shape (longer tails than a bell)" if -0.5 <= best < 0.07 else
                "close to a normal (bell) shape" if 0.07 <= best < 0.3 else
                "close to a uniform shape (short tails)" if 0.7 <= best <= 1.3 else "between the usual shapes")
        print(f'Best Tukey lambda shape for "{column}": lambda = {_num(best)}, {kind}: the shape whose probability '
              "plot is straightest (lambda -1 is about Cauchy, 0 logistic, 0.14 normal, 1 uniform).")
        print("Method: SciPy ppcc_max (the probability plot correlation coefficient, Filliben 1975, made biggest).")
        row = {"test": "best Tukey lambda shape (probability plot correlation)", "column": column, "lambda": best,
               "rows": n}
        return table._result_table(row)
    if key == "yeo-johnson":
        raise SimplydataError('show="best by normal plot" is for test_method="box-cox" (SciPy boxcox_normmax); the '
                              'Yeo-Johnson power comes from maximum likelihood (show="power").')
    best = float(stats.boxcox_normmax(values, method="pearsonr"))
    print(f'Best Box-Cox power for "{column}" by the normal plot: {_num(best)}, the power whose normal probability '
          "plot is straightest (SciPy boxcox_normmax(method=\"pearsonr\")); show=\"power\" gives the one by maximum "
          "likelihood.")
    row = {"test": "best power (Box-Cox, by the normal plot)", "column": column, "power": best, "rows": n}
    del example
    return table._result_table(row)


def _simple_power(power, low, high) -> float:
    """The simple power (1, 0, -1, 0.5, -0.5, 2, -2) inside the interval nearest to the best one; NaN if none."""
    inside = [p for p in SIMPLE_POWERS if math.isfinite(low) and low <= p <= high]
    if not inside:
        return math.nan
    return min(inside, key=lambda p: (abs(p - power), SIMPLE_POWERS.index(p)))


def _model_rows(table, step, column, using):
    """The outcome and the model matrix of explain(column, using=) (rows with an empty cell left out)."""
    from .models import _skipped_note

    with contextlib.redirect_stdout(io.StringIO()):
        terms, pieces, variables, raw, missing, kinds = table._model_parts(step, column, using, "numbers", None,
                                                                           "leave out")
    names = [column] + variables
    keep = ~np.any([missing[nm] for nm in names], axis=0)
    _skipped_note(int((~keep).sum()), names)
    if kinds[column] != "number":
        raise SimplydataError(f'"{column}" should hold numbers to find a power for it.')
    with contextlib.redirect_stdout(io.StringIO()):
        model = table._fit_model(step, column, "numbers", None, terms, variables, raw, kinds, keep)
    return np.asarray(model["y"], dtype=float), np.asarray(model["X"], dtype=float)


# ---------------------------------------------------------------------------- explain(for_percentile=)
def read_percentiles(for_percentile) -> list[float]:
    st = _st()
    items = for_percentile if isinstance(for_percentile, (list, tuple)) else [for_percentile]
    if not items or not all(st._is_number(p) and not isinstance(p, bool) and 1 <= p <= 99 for p in items):
        raise SimplydataError("for_percentile= is the percentile of the line, from 1 to 99, for example "
                              "for_percentile=90 (the line under which 90 % of the values fall), or a list such as "
                              "[10, 50, 90].")
    return [float(p) for p in dict.fromkeys(items)]


def explain_percentile(table, column, using, outcome, percents, others):
    """explain(column, using=, for_percentile=): R quantreg::rq() and summary(se = "nid").

    [D] The 95 % interval is estimate +/- t(n - p) x quantreg's "nid" standard error: the Wald interval that
    goes with the t-test summary.rq prints (quantreg prints no interval for se = "nid")."""
    from scipy import stats

    from .lines_r import percentile_lines
    from .models import _skipped_note

    step = "explain"
    if outcome != "numbers":
        raise SimplydataError(f'for_percentile= works with outcome="numbers", not "{outcome}".')
    busy = [name for name, value, default in others if value != default]
    if busy:
        raise SimplydataError(f"for_percentile= cannot be used with {busy[0]} yet.")
    terms, pieces, variables, raw, missing, kinds = table._model_parts(step, column, using, "numbers", None,
                                                                       "leave out")
    names = [column] + variables
    keep = ~np.any([missing[nm] for nm in names], axis=0)
    _skipped_note(int((~keep).sum()), names)
    with contextlib.redirect_stdout(io.StringIO()):
        model = table._fit_model(step, column, "numbers", None, terms, variables, raw, kinds, keep)
    X, y, labels = np.asarray(model["X"], dtype=float), np.asarray(model["y"], dtype=float), model["labels"]
    n, k = X.shape
    out = percentile_lines(X, y, [p / 100 for p in percents])
    rows = []
    others = _st()._list_words('"' + v + '"' for v in variables)
    print(f'A percentile line is the line under which a share of the values of "{column}" fall, at each value of '
          f"{others}: the 90th percentile line has 90 % of the values below it.")
    for i, percent in enumerate(percents):
        got = out[f"t{i + 1}"]
        beta, se = np.atleast_1d(got["beta"]).astype(float), np.atleast_1d(got["se"]).astype(float)
        t, p = np.atleast_1d(got["t"]).astype(float), np.atleast_1d(got["p"]).astype(float)
        df = n - k
        q = float(stats.t.ppf(0.975, df))
        print(f"At the {_ordinal(percent)} percentile of \"{column}\":")
        for j, label in enumerate(labels):
            low, high = beta[j] - q * se[j], beta[j] + q * se[j]
            rows.append({"percentile": percent, "term": label, "estimate": float(beta[j]),
                         "standard error": float(se[j]), "statistic name": "t", "statistic": float(t[j]),
                         "degrees of freedom": float(df), "p-value": float(p[j]), "95 % CI low": float(low),
                         "95 % CI high": float(high), "rows": n})
            if j == 0:
                continue
            what = "for each 1 more" if " (" not in label else "compared with the first group,"
            print(f"  {label}: {what} the line goes {'up' if beta[j] >= 0 else 'down'} by {_num(abs(beta[j]))} "
                  f"({_ci(low, high)}); {_p_clause(float(p[j]))}.")
        if not bool(np.atleast_1d(got["unique"])[0]):
            print("  Note: the line is not unique here (several lines fit equally well); R gives one of them.")
    print(f"Method: R quantreg::rq({column} ~ {' + '.join(pieces)}, tau = "
          f"{', '.join(f'{p / 100:g}' for p in percents)}) (Koenker & Bassett 1978), standard errors by summary(se = "
          "\"nid\") (Hendricks-Koenker sandwich, which allows the spread to change with the other columns). simplydata "
          "chooses \"nid\" for every number of rows so that each line has an interval and a p-value; R's own "
          "default below 1001 rows is \"rank\" (intervals only).")
    if n < 20:
        print(f"Note: with {n} rows, lines near the edges (such as the 10th or 90th percentile) rest on very few "
              "values.")
    return table._rows_table(rows)


def _ordinal(p) -> str:
    whole = int(p) if float(p).is_integer() else p
    if not isinstance(whole, int):
        return f"{whole}th"
    suffix = "th" if 10 <= whole % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(whole % 10, "th")
    return f"{whole}{suffix}"


# ---------------------------------------------------------------------------- explain(changes_at=)
def explain_changes(table, column, using, changes_at, call):
    """explain(..., changes_at={"month": 37}): the same model with two more columns, after and since."""
    from statsmodels.tsa.stattools import acf

    step = "explain"
    example = f'table.explain("{column}", using=["month"], changes_at={{"month": 37}})'
    if not isinstance(changes_at, dict) or len(changes_at) != 1:
        name = (using[0] if isinstance(using, (list, tuple)) and using else using) or "month"
        raise SimplydataError(f'changes_at= on explain names the time column and the point of change, like '
                              f'changes_at={{"{name}": {changes_at if _st()._is_number(changes_at) else 37}}}.\n'
                              f"For example, {example}")
    (time_column, at), = changes_at.items()
    unsupported = [name for name, value, default in (
        ("curve_for=", call.get("curve_for"), None), ("zero_part_using=", call.get("zero_part_using"), None),
        ("empty_cells=", call.get("empty_cells"), "leave out")) if value != default]
    if call.get("outcome") in ("ordered groups", "groups", "shares", "counts with many zeros", "counts in two steps",
                               "counts in two steps that vary a lot", "counts with many zeros that vary a lot"):
        unsupported.append(f'outcome="{call.get("outcome")}"')
    if unsupported:
        raise SimplydataError(f"changes_at= cannot be used with {unsupported[0]} yet: that model has no single set of "
                              "fitted values for the lag-1 autocorrelation of its leftovers.")
    table._need_columns(time_column)
    values, at_value, how, first = table._change_column(step, time_column, at, example)
    after_name, since_name = f"after {time_column} {at}", f"{time_column} since {at}"
    for name in (after_name, since_name):
        if name in table._columns:
            raise SimplydataError(f'The table already has a column "{name}"; rename it first.')
    after = np.where(np.isnan(values), np.nan, (values >= at_value).astype(float))
    since = after * (values - at_value)
    base = nw.maybe_reset_index(table._frame)
    frame = base.with_columns(nw.new_series(after_name, after, nw.Float64, backend=base.implementation),
                              nw.new_series(since_name, since, nw.Float64, backend=base.implementation))
    bigger = table._new_table(frame)
    items = [using] if isinstance(using, str) else list(using or [])
    if table._frame.schema[time_column].is_temporal():
        # dates cannot go into a model: the time trend is the number of days since the first date
        days_name = f"{time_column} in days since {first}"
        if days_name in table._columns:
            raise SimplydataError(f'The table already has a column "{days_name}"; rename it first.')
        frame = frame.with_columns(nw.new_series(days_name, values, nw.Float64, backend=base.implementation))
        bigger = table._new_table(frame)
        items = [days_name] + [i for i in items if i != time_column]
        print(f'"{time_column}" holds dates, so the time trend before the change is "{days_name}" (the dates as '
              "numbers of days).")
    elif time_column not in items:
        items = [time_column] + items
    items = items + [after_name, since_name]
    # the leftovers must come from the model explain() fits and prints (weighted, robust, mixed ...): the fitted
    # model is taken where explain() turns it into its result table
    captured = {}
    to_table = bigger._term_table

    def keep_the_model(model, *args, **kwargs):
        captured.setdefault("model", model)
        return to_table(model, *args, **kwargs)

    bigger._term_table = keep_the_model
    with contextlib.redirect_stdout(io.StringIO()) as quiet:
        result = bigger.explain(column, using=items, **call)
    model = captured.get("model")
    fitted = (model or {}).get("fit", {}).get("fitted") if isinstance((model or {}).get("fit"), dict) else None
    if model is None or fitted is None or model.get("keep") is None or len(np.atleast_1d(fitted)) != int(
            np.sum(model["keep"])):
        raise SimplydataError(
            "changes_at= cannot be used with these options yet: the model they fit does not give simplydata its "
            "fitted values, so the lag-1 autocorrelation of its leftovers (which an interrupted time series must "
            "check) cannot be worked out. Leave out the other options, or add the two change columns yourself.")
    print(quiet.getvalue(), end="")
    keep = np.asarray(model["keep"], dtype=bool)
    leftovers = np.asarray(model["y"], dtype=float) - np.asarray(fitted, dtype=float)
    order = np.argsort(values[keep], kind="stable")
    lag1 = float(acf(leftovers[order], nlags=1, fft=False)[1])
    print(f'Interrupted time series: "{after_name}" is the jump in level at {at} and "{since_name}" the change of '
          f'slope after it{how}. Lag-1 autocorrelation of the leftovers (observed minus fitted, in "{time_column}" '
          f"order; statsmodels acf): {lag1:.2f}. Near 0 is what the intervals assume; well away from 0, neighbouring "
          "rows are alike and the intervals are too narrow (Bernal et al. 2017).")
    return result
