"""Checking and comparing models (phase S3a-3): two new words and new options of known words.

New words (CheckingMoreWords):
* find_columns_that_predict("y", using=[...]): the lasso (or elastic net) with a cross-validated penalty, R
  glmnet::cv.glmnet() and the "one standard error" penalty; no p-values (the columns were chosen by the data).
* find_group_levels_of("y", using=[...], grouped_by="g"): each group's own starting level (and own slope) of a
  mixed model, R lme4::ranef(condVar = TRUE) and coef(), with the warning that they are not data for later tests.

New options of known words (each word calls the function here when the option is given):
* explain(spread_changes_with=, neighbours_alike_in_order_of=): generalised least squares, R nlme::gls().
* compare_models(using=[[...], [...], ...]): an AICc table with Akaike weights; check_on_left_out_rows=True: R
  boot::cv.glm(K = 10).
* check_model_of: the Breusch-Pagan and White tests as notes under the scale-location picture (statsmodels
  het_breuschpagan, het_white); for yes/no a calibration picture, the Hosmer-Lemeshow test (R performance) and the
  Brier score.
* find_model_averages_of(comparing=, within_each_group_in=, over_range_of=): R emmeans contrast(), joint_tests()
  and at=.
* compare_averages_of(grouped_by=): a nested ANOVA, R aov(y ~ group + Error(unit)); compare_averages_of([...]): a
  MANOVA, statsmodels MANOVA (Pillai's trace, as R summary.manova()).
"""

from __future__ import annotations

import math

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, friendly
from .models import _design, _exp, _label, _list_words, _quoted, _r_name, _sort_key
from .stat_tests import _num, _skipped_note, _whole
from .summaries import _p_clause, _p_shown

LEVELS_WARNING = ("these levels are shrunk towards the average and carry uncertainty; do not use them as data in a "
                  "later test (Houslay & Wilson 2017)")
NO_P_VALUES = ("No p-values or confidence intervals: the columns were chosen by the data, so ordinary p-values would "
               "be too small. To test effects, use explain() on rows that were not used to choose the columns.")
GELMAN_STERN = ("Compare the groups with the interaction test, not by which of the tests below have small p-values "
                "(Gelman & Stern 2006).")
LASSO_METHODS = {"lasso": 1.0, "elastic net": 0.5}
LASSO_SPELLINGS = {"elastic-net": "elastic net", "elasticnet": "elastic net", "elastic_net": "elastic net"}
LASSO_OUTCOMES = {"numbers": "gaussian", "yes or no": "binomial", "counts": "poisson"}
CV_OUTCOMES = ("numbers", "yes or no", "counts")
COMPARING = ("each pair", "each with the first", "each with the next", "each with the average of the ones before",
             "each with the average", "trend")
COMPARING_OTHERS = {"pairwise": "each pair", "trt.vs.ctrl": "each with the first", "dunnett": "each with the first",
                    "consec": "each with the next", "helmert": "each with the average of the ones before",
                    "eff": "each with the average", "poly": "trend", "polynomial": "trend"}
ADJUST_WORDS = {"tukey": "Tukey's adjustment", "dunnettx": "Dunnett's adjustment (emmeans' close form, dunnettx)",
                "mvt": "the multivariate t adjustment (mvt)", "fdr": "the false discovery rate adjustment (fdr)",
                "sidak": "Sidak's adjustment", "bonferroni": "Bonferroni's adjustment", "holm": "Holm's adjustment",
                "none": "no adjustment"}
TREND_WORDS = {"linear": "straight (linear)", "quadratic": "curved (quadratic)", "cubic": "S-shaped (cubic)",
               "quartic": "degree 4"}
LEFT_OUT_PARTS = 10
LEAST_ROWS = 20
AICC_LIMIT = 40  # Burnham & Anderson (2002): AICc when rows per value estimated are fewer than 40
RANGE_POINTS = 50


def _default_given(step, others):
    """others: [(option name, value, default)]; refuse the ones given that do not go with this option yet."""
    given = [name for name, value, default in others if not (value is default or value == default)]
    if given:
        raise SimplydataError(f"{_list_words(given)} cannot be used with {step} yet.")


def _new_rows_table(words, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    data = {key: [r.get(key, math.nan) for r in rows] for key in keys}
    return words._new_table(nw.from_dict(data, backend=words._frame.implementation))


# ---------------------------------------------------------------- explain(spread_changes_with=, neighbours_...)
def _order_values(words, name):
    """The values of neighbours_alike_in_order_of= as numbers (dates as days), with their empty cells."""
    frame = words._frame
    dtype = frame.schema[name]
    if dtype.is_temporal():
        import pandas as pd

        values = pd.to_datetime(frame[name].to_pandas())
        empty = values.isna().to_numpy()
        days = ((values - values.min()) / pd.Timedelta(days=1)).to_numpy(dtype=float)
        return days, empty, "days"
    if not dtype.is_numeric():
        raise SimplydataError(f'neighbours_alike_in_order_of="{name}" needs numbers or dates (the order of the rows, '
                              "such as a year or a date); it holds text.")
    values = frame[name].cast(nw.Float64).to_numpy().astype(float)
    return values, np.isnan(values), None


def explain_gls(words, column, using, spread, order, others):
    """explain(..., spread_changes_with=, neighbours_alike_in_order_of=): R nlme::gls()."""
    from .checking_r import gls

    step = "explain(spread_changes_with=, neighbours_alike_in_order_of=)"
    outcome = dict((n, v) for n, v, _ in others).get("outcome=", "numbers")
    if outcome != "numbers":
        raise SimplydataError('spread_changes_with= and neighbours_alike_in_order_of= are for outcome="numbers" (a '
                              "linear model whose spread changes or whose neighbouring rows are alike).")
    grouped = dict((n, v) for n, v, _ in others).get("grouped_by=")
    if grouped is not None:
        raise SimplydataError("spread_changes_with= and neighbours_alike_in_order_of= cannot be used with grouped_by= "
                              "yet (that would be a mixed model with these parts, R nlme::lme()). Leave out "
                              "grouped_by=, or leave out these options for the mixed model.")
    _default_given(step, [o for o in others if o[0] not in ("outcome=", "grouped_by=")])
    terms, pieces, variables, raw, missing, kinds = words._model_parts("explain", column, using, "numbers", None,
                                                                       "leave out")
    names = [column] + variables
    spread_values = order_values = None
    spread_kind = order_kind = None
    for option, value in (("spread_changes_with=", spread), ("neighbours_alike_in_order_of=", order)):
        if value is None:
            continue
        if not isinstance(value, str):
            raise SimplydataError(f'{option} is one column name, for example {option}"site".')
        words._need_columns(value)
        if value == column:
            raise SimplydataError(f'"{value}" cannot be explained and also be {option}')
    if spread is not None:
        frame = words._frame
        if frame.schema[spread].is_numeric():
            spread_values = frame[spread].cast(nw.Float64).to_numpy().astype(float)
            spread_kind = "number"
            missing_spread = np.isnan(spread_values)
        else:
            spread_values = np.array(frame[spread].to_list(), dtype=object)
            spread_kind = "group"
            missing_spread = np.array([v is None or (isinstance(v, float) and math.isnan(v)) for v in spread_values])
        missing[f"spread:{spread}"] = missing_spread
        names.append(f"spread:{spread}")
    if order is not None:
        order_values, missing_order, unit = _order_values(words, order)
        missing[f"order:{order}"] = missing_order
        names.append(f"order:{order}")
    keep = ~np.any([missing[nm] for nm in names], axis=0)
    _skipped_note(int((~keep).sum()), [column] + variables + [v for v in (spread, order) if v is not None])
    model = words._fit_model("explain", column, "numbers", None, terms, variables, raw, kinds, keep)
    s = o = None
    if spread is not None:
        s = spread_values[keep]
        if spread_kind == "number" and np.any(s == 0):
            raise SimplydataError(f'spread_changes_with="{spread}" holds 0 in {int((s == 0).sum())} rows; a spread that '
                                  "grows as a power of a column needs values that are not 0 (R nlme::varPower()).")
        if spread_kind == "group":
            s = np.array([_label(v) for v in s], dtype=object)
            counts = {g: int(np.sum(s == g)) for g in set(s.tolist())}
            if len(counts) < 2:
                raise SimplydataError(f'spread_changes_with="{spread}" needs at least 2 groups.')
            if min(counts.values()) < 2:
                raise SimplydataError(f'Each group of "{spread}" needs at least 2 rows to have a spread of its own.')
    if order is not None:
        o = order_values[keep]
        if len(set(o.tolist())) < len(o):
            raise SimplydataError(f'neighbours_alike_in_order_of="{order}" has repeated values, so the rows have no '
                                  "single order (each row needs its own time). Use a column with one value per row.")
        steps = np.diff(np.sort(o))
        even = bool(len(steps) and np.allclose(steps, steps[0], rtol=1e-9, atol=0))
        if even:
            o = np.round((o - o.min()) / steps[0]) + 1
            order_kind = "even"
        else:
            order_kind = "uneven"
    out = gls(model, s, spread_kind, o, order_kind)
    coef = dict(beta=out["beta"], se=out["se"], stat=out["t"], p=out["p"], low=out["low"], high=out["high"],
                name="t", df=np.full(len(out["beta"]), float(out["df"][0])))
    parts = []
    if spread is not None:
        parts.append(f'the spread changing with "{spread}"')
    if order is not None:
        parts.append(f'neighbouring rows in "{order}" order alike')
    words._print_terms(model, coef, f"{model['n']} rows, with {' and '.join(parts)}")
    more = []
    if spread is not None and spread_kind == "group":
        names_v = [str(n) for n in out["spread_names"]]
        ratios = dict(zip(names_v, out["spread"].astype(float)))
        reference = next((n for n, r in ratios.items() if abs(r - 1) < 1e-12), names_v[0])
        ci = {str(n): (float(lo), float(hi)) for n, lo, hi in
              zip(out["spread_ci_names"], out["spread_low"], out["spread_high"])} if len(out["spread_ci_names"]) else {}
        pieces_text = []
        for name in sorted(ratios, key=lambda n: (n != reference, n)):
            if name == reference:
                continue
            lo, hi = ci.get(name, (math.nan, math.nan))
            pieces_text.append(f"{name} {_num(ratios[name])} times (95 % CI {_num(lo)} to {_num(hi)})")
            more.append({"term": f'spread of "{name}" against "{reference}"', "effect": ratios[name],
                         "95 % CI low": lo, "95 % CI high": hi})
        print(f'Spread (standard deviation) of each "{spread}" group against "{reference}": '
              + "; ".join(pieces_text) + ".")
    elif spread is not None:
        power = float(out["spread"][0])
        lo, hi = (float(out["spread_low"][0]), float(out["spread_high"][0])) if len(out["spread_low"]) else (
            math.nan, math.nan)
        print(f'Spread: the standard deviation grows as "{spread}" to the power {_num(power)} (95 % CI {_num(lo)} to '
              f"{_num(hi)}); 0 would mean the same spread everywhere.")
        more.append({"term": f'power of "{spread}" for the spread', "effect": power, "95 % CI low": lo,
                     "95 % CI high": hi})
    if order is not None:
        phi = float(out["phi"][0])
        lo, hi = float(out["phi_low"][0]), float(out["phi_high"][0])
        if order_kind == "even":
            print(f'Neighbours: rows next to each other in "{order}" order have a correlation of {_num(phi)} (95 % CI '
                  f"{_num(lo)} to {_num(hi)}); rows two steps apart {_num(phi ** 2)}, and so on (AR(1)).")
        else:
            unit = "day" if (order is not None and words._frame.schema[order].is_temporal()) else f'unit of "{order}"'
            print(f'Neighbours: rows 1 {unit} apart in "{order}" have a correlation of {_num(phi)} (95 % CI {_num(lo)} '
                  f"to {_num(hi)}); further apart it falls as that number to the power of the distance (continuous-"
                  "time AR(1), for rows that are not evenly spaced).")
        more.append({"term": f'correlation of neighbours in "{order}" order', "effect": phi, "95 % CI low": lo,
                     "95 % CI high": hi})
        if phi > 0.99:
            print("Note: the correlation of neighbours is about 1, so the values wander rather than vary around the "
                  "line (a trend or a random walk). Explaining the trend itself (a column for time in using=) or the "
                  "changes from row to row may fit better.")
    aic, aic0 = float(out["aic"][0]), float(out["aic0"][0])
    lr, lr_df, lr_p = float(out["lr"][0]), float(out["lr_df"][0]), float(out["lr_p"][0])
    null = " and ".join((["the spread were truly the same everywhere"] if spread is not None else [])
                        + (["neighbouring rows were truly not alike"] if order is not None else []))
    print(f"Against the same model without {'these parts' if len(parts) > 1 else 'this part'}: AIC {_num(aic)} against "
          f"{_num(aic0)} (lower is better; a difference under 2 means little). Likelihood-ratio test (chi-square = "
          f"{_num(lr)}, df = {_whole(lr_df)}): {_p_clause(lr_p, null)}.")
    rhs = " + ".join(pieces)
    struct = []
    if spread is not None:
        struct.append(f"weights = varIdent(form = ~ 1 | {_r_name(spread)})" if spread_kind == "group" else
                      f"weights = varPower(form = ~ {_r_name(spread)})")
    if order is not None:
        struct.append(f"correlation = corAR1(form = ~ {_r_name(order)})" if order_kind == "even" else
                      f"correlation = corCAR1(form = ~ {_r_name(order)})")
    print(f"Method: generalised least squares, as R nlme::gls({_r_name(column)} ~ {rhs}, {', '.join(struct)}, method "
          '= "REML"); t-tests and 95 % intervals as R summary() and intervals(); the comparison as R anova(m0, m) of '
          "the two REML fits (they have the same effects, so their REML fits can be compared).")
    if order is not None and order_kind == "even":
        print(f'"{order}" is evenly spaced, so each step is one step of the AR(1) (corAR1); with uneven gaps simplydata '
              "would use corCAR1, which allows for the size of each gap.")
    more.append({"term": "AIC of this model", "effect": aic})
    more.append({"term": "AIC without these parts", "effect": aic0})
    more.append({"term": "test: with these parts against without", "statistic name": "chi-square", "statistic": lr,
                 "degrees of freedom": lr_df, "p-value": lr_p})
    words._closing(coef["p"][1:])
    return words._term_table(model, coef, [], more_rows=more)


# ---------------------------------------------------------------- compare_models: many models, left-out rows
def _model_lists(step, using, against, example):
    """using= as a list of models (each a list of columns), with against= added as one more."""
    if isinstance(using, (list, tuple)) and using and all(isinstance(u, (list, tuple)) for u in using):
        models = [list(u) for u in using]
    elif isinstance(using, (list, tuple, str)) and using:
        models = [[using] if isinstance(using, str) else list(using)]
    else:
        raise SimplydataError(f"{step}() needs using= with the columns of each model.\nFor example, {example}")
    if against is not None:
        models.append([against] if isinstance(against, str) else list(against))
    for m in models:
        if not m or not all(isinstance(c, str) for c in m):
            raise SimplydataError(f"Each model in using= is a list of column names.\nFor example, {example}")
    return models


def _fit_on_same_rows(words, step, column, models, outcome, grouped_by, in_order, inner=None):
    """Fit every model on the rows with a value in every column of all of them (as compare_models does)."""
    from .model_tools import MORE_OUTCOMES

    parts = [words._model_parts(step, column, m, outcome, grouped_by, "leave out") for m in models]
    seen = set()
    for p in parts:
        key = frozenset(frozenset(t) for t in p[0])
        if key in seen:
            raise SimplydataError("Two of the models in using= are the same; give each model other columns.")
        seen.add(key)
    names = list(dict.fromkeys([column] + [v for p in parts for v in p[2]] + ([grouped_by] if grouped_by else [])))
    missing, kinds, raw = {}, {}, {}
    for p in parts:
        missing.update(p[4])
        kinds.update(p[5])
        raw.update(p[3])
    if inner is not None:
        words._model_parts(step, column, models[0], outcome, inner, "leave out")
        raw[inner], missing[inner], kinds[inner] = words._inner_column(inner)
        names.append(inner)
    keep = ~np.any([missing[nm] for nm in names], axis=0)
    _skipped_note(int((~keep).sum()), names)
    if outcome not in MORE_OUTCOMES and in_order is not None:
        raise SimplydataError('in_order= gives the order of the groups for outcome="ordered groups".')
    fitted = []
    for terms, pieces, variables, *_ in parts:
        fit_more = None
        if outcome in MORE_OUTCOMES:
            from . import models_more

            model = words._more_model(step, column, outcome, terms, variables, raw, kinds, keep, in_order)
            fit_more = {"ordered": models_more.fit_ordered, "multinom": models_more.fit_groups,
                        "shares": models_more.fit_shares, "zeros": models_more.fit_zeros}[model["kind"]](
                model["X"], model["y"])
        else:
            model = words._fit_model(step, column, outcome, grouped_by, terms, variables, raw, kinds, keep,
                                     grouping={"inner": inner} if inner is not None else None)
        fitted.append((model, pieces, fit_more))
    return fitted


def _model_call(model, pieces, grouped_by):
    from .model_tools import model_call

    return model_call(model, pieces, grouped_by)


def compare_many(words, column, using, against, outcome, grouped_by, in_order, left_out, with_seed):
    """compare_models with a list of models (AICc table) or check_on_left_out_rows=True (R boot::cv.glm)."""
    import statsmodels.tools.eval_measures as measures

    step = "compare_models"
    example = ('with sdata.get_example("school"): table.compare_models("marks", using=[["hours"], ["hours", '
               '"breakfast"]])')
    if not isinstance(left_out, bool):
        raise SimplydataError("check_on_left_out_rows= is True or False.")
    models = _model_lists(step, using, against, example)
    grouped_by, inner = words._groups_inside(step, grouped_by)
    if left_out:
        return _left_out_check(words, column, models, outcome, grouped_by, with_seed)
    if len(models) < 2:
        raise SimplydataError(f"{step}() needs at least two models to compare: using=[[...], [...]].\n"
                              f"For example, {example}")
    if outcome == "counts (overdispersed)":
        raise SimplydataError('Quasi-Poisson (outcome="counts (overdispersed)") has no likelihood, so there is no AIC '
                              'to compare (as R). Compare two models with against= (an F test), or use outcome='
                              '"counts that vary a lot".')
    fitted = _fit_on_same_rows(words, step, column, models, outcome, grouped_by, in_order, inner)
    n = fitted[0][0]["n"]
    found = []
    for model, pieces, fit_more in fitted:
        llf, k = words._likelihood(model, fit_more)
        formula = f"{_r_name(column)} ~ " + " + ".join(pieces)
        found.append(dict(formula=formula, llf=llf, k=k, aic=float(measures.aic(llf, n, k)),
                          aicc=float(measures.aicc(llf, n, k)) if n - k - 1 > 0 else math.inf))
    biggest = max(f["k"] for f in found)
    use_aicc = n / biggest < AICC_LIMIT
    key = "aicc" if use_aicc else "aic"
    best = min(f[key] for f in found)
    for f in found:
        f["delta"] = f[key] - best
    total = sum(math.exp(-f["delta"] / 2) for f in found)
    for f in found:
        f["weight"] = math.exp(-f["delta"] / 2) / total
    found.sort(key=lambda f: f[key])
    where = f' in "{grouped_by}" groups' if grouped_by is not None else ""
    name = "AICc" if use_aicc else "AIC"
    why = (f"AIC corrected for few rows: {n} rows for up to {biggest} values estimated, fewer than {AICC_LIMIT} per "
           "value (Burnham & Anderson 2002)" if use_aicc else
           f"{n} rows for up to {biggest} values estimated, at least {AICC_LIMIT} per value, so AIC needs no small-"
           "sample correction (Burnham & Anderson 2002)")
    print(f'Comparing {len(found)} models of "{column}" on the same {n} rows{where}, by {name} ({why}):')
    for i, f in enumerate(found, start=1):
        print(f"  {i}. {f['formula']}: {name} {_num(f[key])}, difference {_num(f['delta'])}, weight {f['weight']:.2f} "
              f"({f['k']} values estimated)")
    print(f"A difference under 2 means the models fit about equally well. The weight (Akaike weight) is how strongly "
          "the data favour each model among these; it is not the chance that a model is true.")
    if grouped_by is not None:
        print("The mixed models are fitted by maximum likelihood for this, as R anova() refits them.")
    print(f"Method: each model fitted on the same rows as {_model_call(fitted[0][0], fitted[0][1], grouped_by)} "
          "and the others; AIC as R AIC() (every value estimated counts, the spread of a least-squares model too), "
          "AICc = AIC + 2k(k + 1) / (n - k - 1) (statsmodels eval_measures.aicc), Akaike weights exp(-difference / 2) "
          "scaled to add up to 1, as R AICcmodavg::aictab().")
    if len(found) == 2:
        print(f'For a test of two models where one holds every column of the other: table.compare_models("{column}", '
              "using=[...], against=[...]).")
    rows = [{"term": f["formula"], "AIC": f["aic"], "AICc": f["aicc"], f"difference in {name}": f["delta"],
             "Akaike weight": f["weight"], "values estimated": float(f["k"]), "log-likelihood": f["llf"]}
            for f in found]
    return _new_rows_table(words, rows)


def _left_out_check(words, column, models, outcome, grouped_by, with_seed):
    from .checking_r import left_out_rows

    step = "compare_models"
    if outcome not in CV_OUTCOMES:
        raise SimplydataError(f'check_on_left_out_rows=True works with outcome="numbers", "yes or no" or "counts", not '
                              f'"{outcome}".')
    if grouped_by is not None:
        raise SimplydataError("check_on_left_out_rows=True cannot be used with grouped_by= yet: the rows of a group "
                              "would have to be left out together. Leave out grouped_by=.")
    if isinstance(with_seed, bool) or not isinstance(with_seed, int):
        raise SimplydataError("with_seed= is a whole number that fixes the random split, for example with_seed=1.")
    fitted = _fit_on_same_rows(words, step, column, models, outcome, None, None)
    n = fitted[0][0]["n"]
    if n < LEAST_ROWS:
        raise SimplydataError(f"check_on_left_out_rows=True needs at least {LEAST_ROWS} rows (here {n}): each of the "
                              f"{LEFT_OUT_PARTS} parts must hold enough rows to predict.")
    if any(m[0].get("out_of") or m[0].get("time") for m in fitted):
        raise SimplydataError("check_on_left_out_rows=True cannot be used with time= or out_of= yet.")
    out = left_out_rows([m[0] for m in fitted], with_seed, LEFT_OUT_PARTS)
    error = {"numbers": "mean squared error", "yes or no": "Brier score", "counts": "mean squared error"}[outcome]
    what = {"numbers": "the average squared distance between the value and the prediction",
            "yes or no": "the average squared distance between the predicted chance and what happened (0 or 1)",
            "counts": "the average squared distance between the count and the prediction"}[outcome]
    how_many = f"{len(fitted)} models" if len(fitted) > 1 else "the model"
    print(f'Checking {how_many} of "{column}" on rows {"they" if len(fitted) > 1 else "it"} did not see ({n} rows): the '
          f"rows were split into {LEFT_OUT_PARTS} parts at random (with_seed={with_seed}); each part was left out once "
          f"and predicted by a model fitted to the other {LEFT_OUT_PARTS - 1}.")
    rows = []
    for i, (model, pieces, _) in enumerate(fitted):
        formula = f"{_r_name(column)} ~ " + " + ".join(pieces)
        d1, d2, inside = float(out["delta1"][i]), float(out["delta2"][i]), float(out["inside"][i])
        print(f"  {formula}: {error} {_num(d1)} on the left-out rows (adjusted {_num(d2)}), {_num(inside)} on the rows "
              "it was fitted to")
        rows.append({"term": formula, f"{error} on left-out rows": d1, f"{error} on left-out rows (adjusted)": d2,
                     f"{error} on the rows fitted": inside})
    print(f"{error.capitalize()}: {what}; lower is better. A model that does much better on its own rows than on the "
          "left-out rows follows chance details of these rows (overfitting).")
    if len(fitted) > 1:
        best = min(range(len(rows)), key=lambda i: float(out["delta1"][i]))
        print(f"Lowest error on the left-out rows: {rows[best]['term']}. The split is random, so small differences can "
              "change with another with_seed=.")
    family = {"numbers": "gaussian", "yes or no": "binomial", "counts": "poisson"}[outcome]
    print(f"Method: R boot::cv.glm(d, glm(..., family = {family}), K = {LEFT_OUT_PARTS}) after set.seed({with_seed}) "
          "for each model (the same split for every model): delta[1] is the error on the left-out rows, delta[2] that "
          f"error adjusted for fitting to {LEFT_OUT_PARTS - 1} parts of the rows instead of all (Davison & Hinkley "
          f"1997). cv.glm's own default leaves out one row at a time; simplydata sets K = {LEFT_OUT_PARTS}.")
    return _new_rows_table(words, rows)


# ---------------------------------------------------------------- check_model_of: notes and the calibration picture
def spread_tests(model, numbers):
    """Breusch-Pagan (Koenker's studentised form) and White tests of equal spread: notes under picture 3."""
    from statsmodels.stats.diagnostic import het_breuschpagan, het_white

    residual = np.asarray(model["y"], dtype=float) - np.asarray(model["fit"]["fitted"], dtype=float)
    X = np.asarray(model["X"], dtype=float)
    if X.shape[1] < 2:
        return {}
    bp, bp_p, _, _ = het_breuschpagan(residual, X, robust=True)
    bp_df = X.shape[1] - 1
    found = {"breusch_pagan": (float(bp), float(bp_df), float(bp_p))}
    print("Under picture 3, two tests of equal spread (notes only: with many rows they flag even small, harmless "
          "differences, so judge by the picture):")
    print(f"  Breusch-Pagan test (Koenker's studentised form, as R lmtest::bptest()): chi-square = {_num(bp)}, df = "
          f"{_whole(bp_df)}; {_p_clause(float(bp_p), 'the spread were truly the same everywhere')}.")
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            white, white_p, _, _ = het_white(residual, X)
        i0, i1 = np.triu_indices(X.shape[1])
        products = X[:, i0] * X[:, i1]
        white_df = float(np.linalg.matrix_rank(products) - 1)
        found["white"] = (float(white), white_df, float(white_p))
        print(f"  White's test (the columns, their squares and products, as R lmtest::bptest(m, ~ the same)): "
              f"chi-square = {_num(white)}, df = {_whole(white_df)}; "
              f"{_p_clause(float(white_p), 'the spread were truly the same everywhere')}.")
    except (ValueError, np.linalg.LinAlgError, AssertionError):
        print("  White's test is left out: there are too few rows for the squares and products of the columns.")
    return found


def calibration(model):
    """The calibration picture of a yes/no model (the share of yes against the predicted chance in 10 groups of
    rows, with the diagonal), the Hosmer-Lemeshow test (R performance) and the Brier score."""
    import pandas as pd

    from .._r import RMissing
    from ..chart import chart as make_chart
    from .checking_r import hosmer

    y = np.asarray(model["y"], dtype=float)
    p = np.asarray(model["fit"]["fitted"], dtype=float)
    groups = pd.qcut(p, 10, duplicates="drop")
    frame = pd.DataFrame({"chance": p, "yes": y, "group": groups})
    table = frame.groupby("group", observed=True).agg(predicted=("chance", "mean"), observed=("yes", "mean"),
                                                      rows=("yes", "size")).reset_index(drop=True)
    picture = pd.DataFrame({"predicted chance": table["predicted"], "share of yes": table["observed"]})
    chart = (make_chart(picture).draw_dots(x="predicted chance", y="share of yes").draw_line_with_slope(1, intercept=0)
             .set_range_x(0, 1).set_range_y(0, 1).write_title_on_top("Calibration"))
    brier = float(np.mean((p - y) ** 2))
    share = float(np.mean(y))
    found = {"calibration_predicted": table["predicted"].to_numpy(), "calibration_observed": table["observed"].to_numpy(),
             "calibration_rows": table["rows"].to_numpy(), "brier": brier}
    bins = len(table)
    print(f"  5. calibration: the share of yes in {bins} groups of rows (from the lowest predicted chances to the "
          "highest) against their average predicted chance; dots near the diagonal mean the chances can be trusted.")
    print(f"Brier score {_num(brier)}: the average squared distance between the predicted chance and what happened (0 "
          f"is perfect; always predicting the share of yes, {_num(share)}, would give {_num(share * (1 - share))}).")
    try:
        out = hosmer(model["X"], y, 10)
        chi, df, hp = float(out["chisq"][0]), float(out["df"][0]), float(out["p"][0])
        found["hosmer"] = (chi, df, hp)
        print(f"Hosmer-Lemeshow test with 10 groups (a note: its answer depends on the number of groups and it misses "
              f"much; the picture says more): chi-square = {_num(chi)}, df = {_whole(df)}; "
              f"{_p_clause(hp, 'the predicted chances truly matched what happened')}.")
    except RMissing:
        print('The Hosmer-Lemeshow test comes from R performance::performance_hosmer() (needs R: pip install '
              '"simplydata[r]"); left out here.')
    print("Calibration numbers: the groups are the tenths of the predicted chances (pandas qcut, as R "
          "performance::performance_hosmer() cuts them); Brier score as R DescTools::BrierScore().")
    return chart, found


# ---------------------------------------------------------------- find_model_averages_of(comparing=, ...)
def _comparing_choice(comparing, levels):
    """comparing= checked: (name, emmeans method or None, weights dict or None)."""
    from .._errors import other_value_note
    from .checking_r import EMMEANS_METHODS

    if isinstance(comparing, dict):
        if not comparing:
            raise SimplydataError('comparing= as a dict needs at least one comparison, such as {"A against B and C": '
                                  "[1, -0.5, -0.5]}.")
        weights = {}
        for name, w in comparing.items():
            if not isinstance(name, str) or not isinstance(w, (list, tuple)) or len(w) != len(levels) or not all(
                    isinstance(v, (int, float)) and not isinstance(v, bool) for v in w):
                raise SimplydataError(f"Each comparison in comparing= is a name and one weight for each group, in the "
                                      f"order {_list_words(_quoted(g) for g in levels)}: for example "
                                      f'{{"{levels[0]} against the rest": [1'
                                      + ", " * (len(levels) > 1) + ", ".join(
                                          _num(-1 / (len(levels) - 1)) for _ in levels[1:]) + "]}.")
            weights[name] = [float(v) for v in w]
        return "own weights", None, weights
    text = comparing.strip().lower() if isinstance(comparing, str) else comparing
    if text in COMPARING_OTHERS:
        other_value_note("comparing", comparing, COMPARING_OTHERS[text])
        text = COMPARING_OTHERS[text]
    if text not in COMPARING:
        from .._errors import choice_error

        raise choice_error("find_model_averages_of", "comparing", comparing, list(COMPARING))
    if text == "each with the average of the ones before":
        if len(levels) < 2:
            raise SimplydataError("comparing= needs at least 2 groups.")
        weights = {}
        for k in range(1, len(levels)):
            before = levels[:k]
            name = (f"{levels[k]} against {before[0]}" if k == 1 else
                    f"{levels[k]} against the average of {_list_words(before)}")
            weights[name] = [-1 / k] * k + [1.0] + [0.0] * (len(levels) - k - 1)
        return text, None, weights
    if text == "trend" and len(levels) < 3:
        raise SimplydataError('comparing="trend" needs at least 3 groups in order (a straight trend and a curve).')
    return text, EMMEANS_METHODS[text], None


def averages_compared(words, column, for_each, using, outcome, grouped_by, in_order, comparing, within, over_range):
    """find_model_averages_of with comparing=, within_each_group_in= or over_range_of=: R emmeans."""
    from .checking_r import model_contrasts
    from .model_tools import AVERAGE_OUTCOMES, AVERAGE_WORDS, RATIO_PAIRS, model_call

    step = "find_model_averages_of"
    example = ('with sdata.get_example("school"): table.find_model_averages_of("marks", for_each_group_in="school", '
               'using=["hours", "breakfast"], comparing="each with the first")')
    grouped_by, inner = words._groups_inside(step, grouped_by)
    words._need_name(step, "the column to explain", column, example)
    if outcome not in AVERAGE_OUTCOMES:
        words._check_choice(step, "outcome", outcome, AVERAGE_OUTCOMES)
    if outcome in ("ordered groups", "groups"):
        raise SimplydataError(f'comparing=, within_each_group_in= and over_range_of= cannot be used with outcome='
                              f'"{outcome}" yet.')
    if over_range is not None and (within is not None or comparing != "each pair"):
        raise SimplydataError("over_range_of= gives the model's averages along a number column; leave out comparing= "
                              "and within_each_group_in= with it.")
    if over_range is None:
        words._need_name(step, "for_each_group_in=", for_each, example)
    if within is not None:
        words._need_name(step, "within_each_group_in=", within, example)
        if within == for_each:
            raise SimplydataError('within_each_group_in= is another group column than for_each_group_in=: '
                                  'for_each_group_in= names the groups that are compared, within_each_group_in= the groups '
                                  'inside which they are compared, for example for_each_group_in="diet", '
                                  'within_each_group_in="sex".')
    for name in (for_each, within, over_range):
        if name is not None:
            words._need_columns(name)
    words._need_columns(column)
    if using is None:
        using = [v for v in (for_each, within, over_range) if v is not None]
    using = [using] if isinstance(using, str) else list(using) if isinstance(using, (list, tuple)) else using
    if not isinstance(using, list):
        raise SimplydataError(f"{step}() needs using= as a list of column names.\nFor example, {example}")

    def mentioned(name):
        return any(name in [p.strip().strip("`") for p in item.replace("*", ":").split(":")]
                   for item in using if isinstance(item, str))

    added = [v for v in (for_each, within, over_range) if v is not None and not mentioned(v)]
    using = using + added
    model, pieces = words._one_model(step, column, using, outcome, grouped_by, None, inner=inner)
    held_out = {for_each, within, over_range}
    held = [v for v in model["variables"] if v not in held_out and model["kinds"][v] == "number"]
    others = [v for v in model["variables"] if v not in held_out and model["kinds"][v] == "group"]
    how = []
    if held:
        how.append(_list_words(f'"{v}" held at its average ({_num(float(np.mean(model["data"][v])))})' for v in held))
    if others:
        how.append(f"the groups of {_list_words(_quoted(v) for v in others)} counted equally")
    how_text = f", with {' and '.join(how)}" if how else ""
    call = model_call(model, pieces, grouped_by)
    what = AVERAGE_WORDS[outcome]
    for name in added:
        print(f'Note: "{name}" was not in using=, so it was added to the model.')
    if over_range is not None:
        return _averages_over_range(words, model, column, for_each, over_range, how_text, call, what)
    for name, role in ((for_each, "for_each_group_in="), (within, "within_each_group_in=")):
        if name is not None and model["kinds"][name] != "group":
            raise SimplydataError(f'{role}"{name}" holds numbers; it needs a group (text) column. For a number column, '
                                  'over_range_of= gives the model averages along it.')
    levels = [str(v) for v in model["levels"][for_each]]
    if in_order is not None:
        given = [str(v) for v in in_order] if isinstance(in_order, (list, tuple)) else None
        if given is None or sorted(given) != sorted(levels):
            raise SimplydataError(f'in_order= gives the groups of "{for_each}" in the order to compare them, each once: '
                                  f"in_order={[*levels]}.")
        levels = given
    name, method, weights = _comparing_choice(comparing, levels)
    out = model_contrasts(model, for_each, levels, method, weights, by=within)
    ratio = bool(np.atleast_1d(out["ratio"])[0])
    pair_what = RATIO_PAIRS.get(outcome, "ratio") if ratio else "difference"
    adjust_raw = str(np.atleast_1d(out["adjust"])[0])
    adjust_key = adjust_raw.split()[0].lower() if adjust_raw.strip() else "none"
    adjust = ADJUST_WORDS.get(adjust_key, adjust_raw)
    contrasts = [str(c) for c in out["contrast"]]
    n_contrasts = len(contrasts) // (len(set(out["contrast_by"])) if within is not None else 1)
    rows = []
    print(f'Model {what}s of "{column}" for each "{for_each}" ({model["n"]} rows){how_text}'
          + (f', within each "{within}"' if within is not None else "") + ":")
    if within is not None:
        _print_within(words, model, out, for_each, within, rows)
    else:
        for i, level in enumerate(out["level"]):
            print(f"  {level}: {what} {_num(out['average'][i])} (95 % CI {_num(out['low'][i])} to {_num(out['high'][i])})")
    heading = {"each pair": "Each pair of groups", "each with the first": f'Each group against the first, "{levels[0]}"',
               "each with the next": "Each group against the next one",
               "each with the average of the ones before": "Each group against the average of the groups before it "
                                                           "(Helmert contrasts)",
               "each with the average": "Each group against the average of all the groups",
               "trend": "The trend across the groups in order",
               "own weights": "Your comparisons"}[name]
    print(f"{heading} ({pair_what}, {adjust}" + (f" for {n_contrasts} comparisons" if n_contrasts > 1 and
                                                 adjust_key != "none" else "") + "):")
    by_list = [str(b) for b in out["contrast_by"]] if within is not None else [None] * len(contrasts)
    for i, label in enumerate(contrasts):
        shown = _contrast_label(label, name)
        where = f"{by_list[i]}: " if within is not None else ""
        p = float(out["p"][i])
        if adjust_key != "none" and n_contrasts > 1:
            words_p = f"{ADJUST_WORDS.get(adjust_key, adjust_key).split(chr(39))[0].strip()}-adjusted {_p_shown(p)}" \
                if adjust_key in ("tukey", "sidak", "bonferroni", "holm") else f"adjusted {_p_shown(p)} ({adjust_key})"
        else:
            words_p = _p_clause(p, "the groups truly did not differ" if name != "trend" else "there were truly no trend")
        print(f"  {where}{shown}: {pair_what} {_num(out['difference'][i])} (95 % CI {_num(out['plow'][i])} to "
              f"{_num(out['phigh'][i])}); {words_p}.")
        row = {"term": shown + (f" (within {by_list[i]})" if within is not None else ""), pair_what:
               float(out["difference"][i]), "95 % CI low": float(out["plow"][i]), "95 % CI high": float(out["phigh"][i]),
               "standard error": float(out["pse"][i]), "degrees of freedom": float(out["pdf"][i]),
               "statistic": float(out["stat"][i]), f"p-value ({adjust_key})": p}
        rows.append(row)
    spec = f"~ {_r_name(for_each)}" + (f" | {_r_name(within)}" if within is not None else "")
    scale = "" if outcome == "numbers" else ', type = "response"'
    method_words = method if method else "list(...) of the weights"
    print(f"Method: the model {call}, then R emmeans::emmeans(m, {spec}{scale}) and contrast(e, method = "
          f'{chr(34) + method_words + chr(34) if method else method_words}), with emmeans\' own adjustment for this '
          f"method ({adjust_key})" + ("; joint_tests(m) and joint_tests(m, by = " + chr(34) + within + chr(34) +
                                       ") for the F tests" if within is not None else "") + ".")
    if name == "each with the first" and in_order is None:
        rest = [g for g in levels if g != levels[0]]
        print(f'The first group is "{levels[0]}" (in sorted order). To compare each group with another one, put it '
              f"first: in_order={[rest[0], levels[0], *rest[1:]]}.")
    if name == "trend" and in_order is None:
        print(f"The trend follows the groups in the order {_list_words(_quoted(g) for g in levels)}; give in_order=[...] "
              "when that is not their natural order.")
    if ratio:
        print(f"The comparisons are ratios: 1 means no difference ({pair_what}).")
    if adjust_key != "none" and n_contrasts > 1:
        print(f"Adjusted p-values allow for making {n_contrasts} comparisons: each says how often a difference this "
              "big would turn up among all of them if the groups truly did not differ.")
    if any(float(p) >= 0.05 for p in out["p"]):
        print("A large p-value does not show that there is no difference, only that the data cannot tell.")
    for i, level in enumerate(out["level"]):
        rows.insert(i, {"term": str(level) + (f" (within {out['level_by'][i]})" if within is not None else ""),
                        f"model {what}": float(out["average"][i]), "95 % CI low": float(out["low"][i]),
                        "95 % CI high": float(out["high"][i]), "standard error": float(out["se"][i]),
                        "degrees of freedom": float(out["df"][i])})
    return _new_rows_table(words, rows)


def _contrast_label(label, name):
    if name == "trend":
        return TREND_WORDS.get(label, label.replace("degree ", "degree "))
    return label.replace(" - ", " minus ").replace(" / ", " against ")


def _print_within(words, model, out, for_each, within, rows):
    """The interaction test first, then the test of for_each= within each group of within= and its averages."""
    safe = out["safe"]
    back = {v: k for k, v in safe.items()}

    def name(term):
        return " : ".join(back.get(p, p) for p in str(term).split(":"))

    joint = {name(t): i for i, t in enumerate(out["joint_term"])}
    wanted = {f"{for_each} : {within}", f"{within} : {for_each}"}
    key = next((t for t in joint if t in wanted), None)
    if key is None:
        print(f'Note: the model has no interaction of "{for_each}" and "{within}", so the differences between the '
              f'"{for_each}" groups are the same in every "{within}" group. Add "{for_each} * {within}" to using= to let '
              "them differ.")
    else:
        i = joint[key]
        f, d1, d2, p = (float(out["joint_f"][i]), float(out["joint_df1"][i]), float(out["joint_df2"][i]),
                        float(out["joint_p"][i]))
        df2 = "infinite" if not math.isfinite(d2) else _whole(d2)
        print(f'Does the effect of "{for_each}" depend on "{within}"? The interaction {for_each} : {within}: F = '
              f"{_num(f)}, df = {_whole(d1)} and {df2}; "
              f"{_p_clause(p, 'the effect were truly the same in every group')}.")
        print(GELMAN_STERN)
        rows.append({"term": f"interaction {for_each} : {within}", "statistic name": "F", "statistic": f,
                     "degrees of freedom 1": d1, "degrees of freedom 2": d2, "p-value": p})
    levels_by = [str(b) for b in out["level_by"]]
    for b_index, b in enumerate(str(x) for x in out["within_by"]):
        f, d1, d2, p = (float(out["within_f"][b_index]), float(out["within_df1"][b_index]),
                        float(out["within_df2"][b_index]), float(out["within_p"][b_index]))
        df2 = "infinite" if not math.isfinite(d2) else _whole(d2)
        print(f'  within "{within}" {b}: "{for_each}" F = {_num(f)}, df = {_whole(d1)} and {df2}; '
              f"{_p_clause(p, 'the averages truly did not differ there')}.")
        shown = [f"{out['level'][i]} {_num(out['average'][i])} (95 % CI {_num(out['low'][i])} to {_num(out['high'][i])})"
                 for i in range(len(levels_by)) if levels_by[i] == b]
        print("    averages: " + ", ".join(shown))
        rows.append({"term": f"{for_each} within {within} {b}", "statistic name": "F", "statistic": f,
                     "degrees of freedom 1": d1, "degrees of freedom 2": d2, "p-value": p})


def _averages_over_range(words, model, column, for_each, over_range, how_text, call, what):
    from .checking_r import model_contrasts

    if model["kinds"][over_range] != "number":
        raise SimplydataError(f'over_range_of="{over_range}" holds groups; it needs a number column (the model averages '
                              "are given at evenly spaced values of it). For groups, use for_each_group_in=.")
    if for_each is not None and model["kinds"][for_each] != "group":
        raise SimplydataError(f'for_each_group_in="{for_each}" holds numbers; with over_range_of= it names a group '
                              "column, one line for each group.")
    values = np.asarray(model["data"][over_range], dtype=float)
    grid = np.linspace(float(values.min()), float(values.max()), RANGE_POINTS)
    out = model_contrasts(model, for_each, [str(v) for v in model["levels"][for_each]] if for_each else None,
                          at=(over_range, grid))
    x = np.asarray(out["x"], dtype=float)
    groups = [str(g) for g in out["group"]] if for_each is not None else [None] * len(x)
    lines = f', one line for each "{for_each}"' if for_each is not None else ""
    print(f'Model {what}s of "{column}" across "{over_range}" ({RANGE_POINTS} values from {_num(grid[0])} to '
          f'{_num(grid[-1])}; {model["n"]} rows){how_text}{lines}:')
    for g in dict.fromkeys(groups):
        idx = [i for i in range(len(x)) if groups[i] == g]
        if g is not None:
            print(f"  {g}:")
        for i in (idx[0], idx[len(idx) // 2], idx[-1]):
            print(f"{'    ' if g is not None else '  '}{over_range} {_num(x[i])}: {what} {_num(out['average'][i])} "
                  f"(95 % CI {_num(out['low'][i])} to {_num(out['high'][i])})")
    print(f"  (all {len(x)} rows are in the table that comes back)")
    colour = f', colour="{for_each}"' if for_each is not None else ""
    print(f'To draw them: chart = sdata.chart(result), then chart.draw_lines(x="{over_range}", y="model {what}"{colour}) '
          f'and chart.draw_band(x="{over_range}", between=["95 % CI low", "95 % CI high"]{colour}).')
    spec = f"~ {_r_name(over_range)}" + (f" | {_r_name(for_each)}" if for_each is not None else "")
    print(f"Method: the model {call}, then R emmeans::emmeans(m, {spec}, at = list({_r_name(over_range)} = "
          f"{RANGE_POINTS} evenly spaced values)" + ("" if model["outcome"] == "numbers" else ', type = "response"')
          + ").")
    rows = []
    for i in range(len(x)):
        row = {over_range: float(x[i])}
        if for_each is not None:
            row[for_each] = groups[i]
        row.update({f"model {what}": float(out["average"][i]), "95 % CI low": float(out["low"][i]),
                    "95 % CI high": float(out["high"][i]), "standard error": float(out["se"][i]),
                    "degrees of freedom": float(out["df"][i])})
        rows.append(row)
    return _new_rows_table(words, rows)


# ---------------------------------------------------------------- compare_averages_of(grouped_by=) and a list
def nested_averages(words, column, for_each, grouped_by):
    """compare_averages_of(..., grouped_by=): a nested ANOVA, R aov(y ~ group + Error(unit))."""
    from .checking_r import nested_anova

    step = "compare_averages_of"
    example = ('table.compare_averages_of("length", for_each_group_in="diet", grouped_by="tank") (several fish in each '
               "tank, each tank on one diet)")
    words._need_name(step, "the column", column, example)
    if not isinstance(for_each, str):
        raise SimplydataError(f"With grouped_by=, for_each_group_in= is one group column.\nFor example, {example}")
    words._need_name(step, "grouped_by=", grouped_by, example)
    words._need_columns(column, for_each, grouped_by)
    if len({column, for_each, grouped_by}) < 3:
        raise SimplydataError("The column, for_each_group_in= and grouped_by= must be different columns.")
    frame = words._frame
    if not frame.schema[column].is_numeric():
        raise SimplydataError(f'compare_averages_of() needs numbers in "{column}".')
    y = frame[column].cast(nw.Float64).to_numpy().astype(float)
    groups = frame[for_each].to_list()
    units = frame[grouped_by].to_list()
    empty = np.isnan(y) | np.array([g is None or (isinstance(g, float) and math.isnan(g)) for g in groups]) | \
        np.array([u is None or (isinstance(u, float) and math.isnan(u)) for u in units])
    _skipped_note(int(empty.sum()), [column, for_each, grouped_by])
    keep = ~empty
    y = y[keep]
    groups = [_label(g) for g, k in zip(groups, keep) if k]
    units = [_label(u) for u, k in zip(units, keep) if k]
    seen = {}
    for g, u in zip(groups, units):
        seen.setdefault(u, set()).add(g)
    shared = [u for u, gs in seen.items() if len(gs) > 1]
    if shared:
        raise SimplydataError(
            f'Some "{grouped_by}" groups hold more than one "{for_each}" group (for example "{shared[0]}"), so they are '
            f'not inside the "{for_each}" groups. If every "{grouped_by}" was measured in every "{for_each}" group '
            f'(crossed, not nested), use matched_by=: table.compare_averages_of("{column}", for_each_group_in='
            f'"{for_each}", matched_by="{grouped_by}"). If the "{grouped_by}" names start again in each "{for_each}" '
            f'group (tank 1, 2, 3 in each diet), make the names unique first, for example with table.add_column().')
    size = {u: units.count(u) for u in seen}
    if max(size.values()) < 2:
        raise SimplydataError(f'Each "{grouped_by}" has only one row, so there is nothing nested: compare the groups '
                              f'without grouped_by=: table.compare_averages_of("{column}", for_each_group_in="{for_each}").')
    order = sorted(set(groups), key=_sort_key)
    per_group = {g: sorted({u for u, gs in seen.items() if g in gs}) for g in order}
    if len(order) < 2:
        raise SimplydataError(f'"{for_each}" needs at least 2 groups.')
    if min(len(v) for v in per_group.values()) < 2 and len(seen) - len(order) < 1:
        raise SimplydataError(f'Each "{for_each}" group needs at least 2 "{grouped_by}" groups, so the differences '
                              f'between "{grouped_by}" groups can be measured.')
    out = nested_anova(y, groups, units)
    f, d1, d2, p = (float(out["f"][0]), float(out["df1"][0]), float(out["df2"][0]), float(out["p"][0]))
    v_units, v_within = float(out["var_units"][0]), float(out["var_within"][0])
    balanced = len(set(size.values())) == 1 and len({len(v) for v in per_group.values()}) == 1
    averages = ", ".join(f"{g} {_num(float(np.mean(y[np.array(groups) == g])))}" for g in order)
    print(f'Comparing the average "{column}" for each "{for_each}", with several rows from each "{grouped_by}" '
          f'({len(seen)} "{grouped_by}" groups inside {len(order)} "{for_each}" groups, {len(y)} rows): a nested ANOVA, '
          f'so "{for_each}" is tested against the differences between "{grouped_by}" groups, not between rows.')
    print(f"  averages: {averages}")
    print(f'  "{for_each}": F = {_num(f)}, df = {_whole(d1)} and {_whole(d2)}; '
          f"{_p_clause(p, 'the averages truly did not differ')}.")
    share = v_units / (v_units + v_within) if v_units + v_within > 0 else math.nan
    print(f'  Variances (R lme4::lmer(), REML): between "{grouped_by}" groups {_num(v_units)}, between rows of a '
          f'"{grouped_by}" {_num(v_within)}: about {round(share * 100) if math.isfinite(share) else "?"} % of the '
          f'differences the groups do not explain lies between "{grouped_by}" groups.')
    print(f"Method: R aov({_r_name(column)} ~ {_r_name(for_each)} + Error({_r_name(grouped_by)})), the classical nested "
          f'table: "{for_each}" tested against the mean square between "{grouped_by}" groups ({_num(float(out["ms_units"][0]))} '
          f"on {_whole(d2)} df); the variances from R lme4::lmer({_r_name(column)} ~ {_r_name(for_each)} + (1 | "
          f"{_r_name(grouped_by)})).")
    if not balanced:
        print(f'Note: the "{grouped_by}" groups are not all the same size (an unbalanced design), so the classical table '
              f'is only approximate. A mixed model gives a safer test: table.explain("{column}", using=["{for_each}"], '
              f'grouped_by="{grouped_by}", p_value_by="satterthwaite").')
    if p >= 0.05:
        print("A large p-value does not show that there is no difference, only that the data cannot tell.")
    rows = [{"term": for_each, "statistic name": "F", "statistic": f, "degrees of freedom 1": d1,
             "degrees of freedom 2": d2, "p-value": p, "sum of squares": float(out["ss_group"][0]),
             "mean square": float(out["ms_group"][0])},
            {"term": f"between {grouped_by} groups", "degrees of freedom 1": d2,
             "sum of squares": float(out["ss_units"][0]), "mean square": float(out["ms_units"][0]),
             "variance": v_units},
            {"term": "within", "degrees of freedom 1": float(out["df_within"][0]),
             "sum of squares": float(out["ss_within"][0]), "mean square": float(out["ms_within"][0]),
             "variance": v_within}]
    return _new_rows_table(words, rows)


def manova(words, columns, for_each):
    """compare_averages_of(["a", "b"], for_each_group_in="g"): statsmodels MANOVA, Pillai's trace first."""
    import pandas as pd
    from statsmodels.multivariate.manova import MANOVA

    step = "compare_averages_of"
    example = ('with sdata.get_example("iris"): table.compare_averages_of(["sepal_length", "petal_length"], '
               'for_each_group_in="species")')
    if len(columns) < 2 or not all(isinstance(c, str) for c in columns) or len(set(columns)) < len(columns):
        raise SimplydataError(f"A list in the first place compares two or more different number columns at once (a "
                              f"MANOVA).\nFor example, {example}")
    if isinstance(for_each, (list, tuple)):
        raise SimplydataError("A MANOVA with more than one group column is not in simplydata yet; give "
                              "for_each_group_in= one group column.")
    words._need_name(step, "for_each_group_in=", for_each, example)
    words._need_columns(*columns, for_each)
    if for_each in columns:
        raise SimplydataError(f'"{for_each}" cannot be compared and also be for_each_group_in=.')
    frame = words._frame
    for c in columns:
        if not frame.schema[c].is_numeric():
            raise SimplydataError(f'compare_averages_of() needs numbers in "{c}".')
    Y = np.column_stack([frame[c].cast(nw.Float64).to_numpy().astype(float) for c in columns])
    groups = frame[for_each].to_list()
    empty = np.isnan(Y).any(axis=1) | np.array([g is None or (isinstance(g, float) and math.isnan(g)) for g in groups])
    _skipped_note(int(empty.sum()), [*columns, for_each])
    Y = Y[~empty]
    groups = [_label(g) for g, e in zip(groups, empty) if not e]
    order = sorted(set(groups), key=_sort_key)
    if len(order) < 2:
        raise SimplydataError(f'"{for_each}" needs at least 2 groups.')
    counts = {g: groups.count(g) for g in order}
    small = [g for g in order if counts[g] <= len(columns)]
    if small:
        raise SimplydataError(f'The group "{small[0]}" has {counts[small[0]]} rows for {len(columns)} columns; a MANOVA '
                              "needs more rows than columns in every group.")
    centred = Y - np.array([Y[np.array(groups) == g].mean(axis=0) for g in groups])
    if np.linalg.matrix_rank(centred) < len(columns):
        raise SimplydataError("Some of the columns can be made exactly from the others (the same thing measured twice), "
                              "so they cannot be compared together. Leave one out.")
    safe = {c: f"y{i}" for i, c in enumerate(columns)}
    data = pd.DataFrame({safe[c]: Y[:, i] for i, c in enumerate(columns)})
    data["g"] = pd.Categorical(groups, categories=order)
    result = MANOVA.from_formula(" + ".join(safe.values()) + " ~ g", data=data).mv_test()
    table = result.results["g"]["stat"]
    stats_names = {"Pillai's trace": "Pillai's trace", "Wilks' lambda": "Wilks' lambda",
                   "Hotelling-Lawley trace": "Hotelling-Lawley trace", "Roy's greatest root": "Roy's greatest root"}
    pillai = table.loc["Pillai's trace"]
    value, f, d1, d2, p = (float(pillai["Value"]), float(pillai["F Value"]), float(pillai["Num DF"]),
                           float(pillai["Den DF"]), float(pillai["Pr > F"]))
    named = _list_words(_quoted(c) for c in columns)
    print(f'Comparing the averages of {named} together for each "{for_each}" ({len(Y)} rows, {len(order)} groups): a '
          "MANOVA, one test for all the columns at once.")
    for g in order:
        means = Y[np.array(groups) == g].mean(axis=0)
        print(f"  {g}: " + ", ".join(f"{c} {_num(m)}" for c, m in zip(columns, means)))
    print(f"  Pillai's trace = {_num(value)}, approximate F = {_num(f)}, df = {_whole(d1)} and {_whole(d2)}; "
          f"{_p_clause(p, 'the averages truly did not differ in any of the columns')}.")
    formula = " + ".join(_r_name(c) for c in columns)
    print(f'Method: statsmodels MANOVA.from_formula("{formula} ~ {for_each}").mv_test(); Pillai\'s trace, the one R '
          f"summary(manova(cbind({', '.join(_r_name(c) for c in columns)}) ~ {_r_name(for_each)})) prints by default "
          "and the safest when groups differ in size or spread; Wilks, Hotelling-Lawley and Roy are in the table that "
          "comes back.")
    print(f"To see which columns differ: compare_averages_of() for each column, then "
          "table.add_adjusted_p_value_column() on the p-values.")
    if p >= 0.05:
        print("A large p-value does not show that there is no difference, only that the data cannot tell.")
    rows = [{"term": f"{for_each} ({stats_names[name]})", "statistic name": name, "statistic": float(table.loc[name, "Value"]),
             "F": float(table.loc[name, "F Value"]), "degrees of freedom 1": float(table.loc[name, "Num DF"]),
             "degrees of freedom 2": float(table.loc[name, "Den DF"]), "p-value": float(table.loc[name, "Pr > F"])}
            for name in ("Pillai's trace", "Wilks' lambda", "Hotelling-Lawley trace", "Roy's greatest root")]
    return _new_rows_table(words, rows)


# ---------------------------------------------------------------- the two new words
class CheckingMoreWords:
    @friendly
    def find_columns_that_predict(self, column=None, using=None, method="lasso", outcome="numbers", with_seed=1):
        """Choose the columns that predict a column, with the lasso and a penalty checked on left-out rows.

        table.find_columns_that_predict("Fertility", using=["Agriculture", "Examination", "Education", "Catholic",
        "Infant.Mortality"])   (with a table of the Swiss provinces)
        The lasso shrinks every effect towards 0 and sets the weakest to exactly 0, so only some
        columns are kept. How strongly it shrinks (the penalty) is chosen by cross-validation: the
        rows are split into 10 parts at random (with_seed=1 fixes the split), each part is left out
        once and predicted by models fitted to the other nine, and simplydata takes the largest
        penalty within one standard error of the best (fewer columns, steadier). method="elastic
        net" is half lasso, half ridge (it keeps groups of linked columns together). outcome="yes or
        no" and "counts" work too. Text columns are turned into 0/1 columns. No p-values: the
        columns were chosen by the data. Done by R glmnet::cv.glmnet() (needs R: pip install
        "simplydata[r]"). Gives back a table with one row per column: its shrunk effect, and whether
        it was kept. Other names: lasso, glmnet, elastic net.
        """
        from .checking_r import lasso

        step = "find_columns_that_predict"
        example = ('table.find_columns_that_predict("marks", using=["hours", "breakfast", "sleep"])   (with a table '
                   "of several columns)")
        self._need_name(step, "the column to predict", column, example)
        method_text = method.strip().lower() if isinstance(method, str) else method
        method_text = LASSO_SPELLINGS.get(method_text, method_text)
        if method_text == "ridge":
            raise SimplydataError('method="ridge" keeps every column (it shrinks effects but never sets one to 0), so it '
                                  'does not find columns. Use method="lasso" (the default) or method="elastic net".')
        if method_text not in LASSO_METHODS:
            self._check_choice(step, "method", method, tuple(LASSO_METHODS))
        if outcome not in LASSO_OUTCOMES:
            self._check_choice(step, "outcome", outcome, tuple(LASSO_OUTCOMES))
        if isinstance(with_seed, bool) or not isinstance(with_seed, int):
            raise SimplydataError("with_seed= is a whole number that fixes the random split, for example with_seed=1.")
        terms, pieces, variables, raw, missing, kinds = self._model_parts(step, column, using, outcome, None,
                                                                          "leave out")
        if len(variables) < 2:
            raise SimplydataError(f"{step}() chooses among several columns: give using= at least two.\n"
                                  f"For example, {example}")
        names = [column] + variables
        keep = ~np.any([missing[nm] for nm in names], axis=0)
        _skipped_note(int((~keep).sum()), names)
        n = int(keep.sum())
        if n < LEAST_ROWS:
            raise SimplydataError(f"{step}() needs at least {LEAST_ROWS} rows with a value in every column (here {n}): "
                                  f"the penalty is checked on {LEFT_OUT_PARTS} parts of the rows.")
        y, yes_words = self._outcome_values(column, outcome, raw[column][keep], kinds[column])
        data = {v: raw[v][keep] for v in variables}
        levels = {}
        for v in variables:
            if kinds[v] == "group":
                found = sorted(set(data[v].tolist()), key=_sort_key)
                if len(found) < 2:
                    raise SimplydataError(f'The group column "{v}" has only one group in the rows used; leave it out.')
                levels[v] = found
        X, labels, owner, parts_of = _design(data, kinds, levels, terms)
        out = lasso(X[:, 1:], y, LASSO_OUTCOMES[outcome], LASSO_METHODS[method_text], with_seed)
        beta = np.asarray(out["beta"], dtype=float)
        kept = [j for j in range(1, len(labels)) if beta[j] != 0]
        dropped = [j for j in range(1, len(labels)) if beta[j] == 0]
        ratio = {"yes or no": "odds ratio", "counts": "rate ratio"}.get(outcome)
        what = "the lasso" if method_text == "lasso" else "the elastic net (half lasso, half ridge)"
        print(f'Choosing the columns that predict "{column}" with {what} ({n} rows, {len(labels) - 1} columns to choose '
              "from):")

        def effect_words(j):
            b = float(beta[j])
            return f'"{labels[j]}" {_num(_exp(b))}' if ratio else f'"{labels[j]}" {_num(b)}'

        if kept:
            unit = f" ({ratio}s, shrunk towards 1)" if ratio else " (effects shrunk towards 0)"
            print(f"  kept {len(kept)} of {len(labels) - 1}: {_list_words(effect_words(j) for j in kept)}{unit}")
        else:
            print(f"  kept none of the {len(labels) - 1} columns: at the penalty chosen, the average alone predicts "
                  "as well as any of them.")
        if dropped:
            print(f"  left out (effect 0): {_list_words(_quoted(labels[j]) for j in dropped)}")
        grouped = [v for v in variables if kinds[v] == "group"]
        if grouped:
            print(f"  text columns turned into 0/1 columns (each group against the first): "
                  f"{_list_words(_quoted(v) for v in grouped)}")
        lam, lam_min = float(out["lambda"][0]), float(out["lambda_min"][0])
        measure = str(np.atleast_1d(out["measure"])[0])
        print(f"How: the rows were split into {LEFT_OUT_PARTS} parts at random (with_seed={with_seed}); each part was "
              f"left out once and predicted by models fitted to the other {LEFT_OUT_PARTS - 1}, for "
              f"{int(out['lambdas'][0])} penalties. The penalty chosen is the largest within one standard error of the "
              f"best (lambda = {_num(lam)}; the best was {_num(lam_min)}): it keeps fewer columns and is steadier.")
        print(f"Cross-validated {measure.lower()} at that penalty: {_num(float(out['cvm'][0]))} (at the best: "
              f"{_num(float(out['cvm_min'][0]))}).")
        print(NO_P_VALUES)
        family = LASSO_OUTCOMES[outcome]
        yes = f" ({yes_words})" if yes_words else ""
        print(f'Method: R glmnet::cv.glmnet(x, y, family = "{family}", alpha = {_num(LASSO_METHODS[method_text])}, '
              f"nfolds = {LEFT_OUT_PARTS}) after set.seed({with_seed}), effects from coef(fit, s = \"lambda.1se\"){yes}; "
              "glmnet puts every column on the same scale before shrinking (standardize = TRUE) and gives the effects "
              "in each column's own units.")
        rows = []
        for j, label in enumerate(labels):
            row = {"term": label, "effect": float(beta[j])}
            if ratio:
                row[ratio] = _exp(float(beta[j]))
            row["kept"] = bool(j == 0 or beta[j] != 0)
            rows.append(row)
        rows.append({"term": "penalty chosen (lambda.1se)", "value": lam})
        rows.append({"term": f"cross-validated {measure.lower()}", "value": float(out["cvm"][0])})
        return _new_rows_table(self, rows)

    @friendly
    def find_group_levels_of(self, column=None, using=None, grouped_by=None, outcome="numbers", own_slope_for=None):
        """Each group's own starting level (and own slope) in a mixed model.

        table.find_group_levels_of("marks", using=["hours"], grouped_by="school")   (with sdata.get_example("school"))
        The mixed model of explain(..., grouped_by="school") gives each school its own
        starting level around the average one. This word shows each school's level (its
        distance from the average starting level, a BLUP: best linear unbiased prediction) with a
        95 % interval, and the school's own line. own_slope_for="hours" adds each school's own
        slope. The levels are shrunk towards the average and carry uncertainty: they are for
        pictures and reports, not data for a later test (Houslay & Wilson 2017); the table that
        comes back says so in its "warning" column. Done by R lme4::ranef(condVar = TRUE) and
        coef() (needs R: pip install "simplydata[r]"). Other names: ranef, BLUP, random effects.
        """
        from .checking_r import group_levels
        from .model_tools import model_call

        step = "find_group_levels_of"
        example = 'with sdata.get_example("school"): table.find_group_levels_of("marks", using=["hours"], grouped_by="school")'
        self._need_name(step, "the column to explain", column, example)
        if grouped_by is None:
            raise SimplydataError(f"{step}() needs grouped_by= with the group column whose levels it shows.\n"
                                  f"For example, {example}")
        if isinstance(grouped_by, (list, tuple)):
            raise SimplydataError(f"{step}() takes one group column in grouped_by= for now (groups inside groups come "
                                  "later).")
        if outcome not in ("numbers", "yes or no", "counts"):
            self._check_choice(step, "outcome", outcome, ("numbers", "yes or no", "counts"))
        slopes = [own_slope_for] if isinstance(own_slope_for, str) else list(own_slope_for or [])
        model, pieces = self._one_model(step, column, using, outcome, grouped_by)
        for s in slopes:
            if s not in model["variables"] or model["kinds"][s] != "number":
                raise SimplydataError(f'own_slope_for="{s}" needs "{s}" in using= as a number column: each group then '
                                      "gets its own slope for it.")
        out = group_levels(model, slopes)
        groups = [str(g) for g in out["groups"]]
        names = out["names"]
        level, sd, own = out["level"], out["sd"], out["own"]
        scale = "" if outcome == "numbers" else (" (on the log-odds scale)" if outcome == "yes or no" else
                                                 " (on the log scale)")
        order = np.argsort(level[:, 0], kind="stable")
        what = 'own starting level' + (f" and own slope for {_list_words(_quoted(s) for s in slopes)}" if slopes else "")
        print(f'Each "{grouped_by}"\'s {what}, from the mixed model of "{column}" ({model["n"]} rows, {len(groups)} '
              f"groups){scale}:")
        fixed = np.asarray(out["fixed"], dtype=float)
        start = "the starting level is where every number column in using= is 0" + (
            " and every group column at its first group" if any(model["kinds"][v] == "group"
                                                                 for v in model["variables"]) else "")
        print(f"  ({start}; the average starting level is {_num(fixed[0])}. Each line: the group's distance from the "
              "average, with its 95 % interval, then the group's own value.)")
        for i in order:
            pieces_text = []
            for k, name in enumerate(names):
                lo, hi = level[i, k] - 1.959963984540054 * sd[i, k], level[i, k] + 1.959963984540054 * sd[i, k]
                label = "starting level" if name == "(Intercept)" else f'slope for "{name}"'
                pieces_text.append(f"{label} {level[i, k]:+.3g} (95 % interval {_num(lo)} to {_num(hi)}), own "
                                   f"{_num(own[i, k])}")
            print(f"  {groups[i]}: " + "; ".join(pieces_text))
        print(f"Note: {LEVELS_WARNING}. The table that comes back says this too, in its \"warning\" column.")
        if bool(np.atleast_1d(out["singular"])[0]):
            print("Note: R calls this a singular fit (a variance of about 0, or a correlation of about 1 or -1 between "
                  "the starting levels and the slopes): the data cannot tell all these levels apart, so a simpler model "
                  "(without own_slope_for=) may be enough.")
        call = model_call(model, pieces, grouped_by)
        if slopes:
            call = call.replace("(1 | ", f"(1 + {' + '.join(_r_name(s) for s in slopes)} | ")
        print(f"Method: the mixed model R {call}, then lme4::ranef(m, condVar = TRUE) (each level with its conditional "
              "standard deviation; the 95 % interval is the level plus and minus 1.96 of them, as "
              "lattice::dotplot(ranef(m, condVar = TRUE)) draws it) and coef(m) (the group's own line).")
        rows = []
        for i in order:
            row = {"term": groups[i]}
            for k, name in enumerate(names):
                label = "starting level" if name == "(Intercept)" else f"slope for {name}"
                row.update({f"{label} (distance from the average)": float(level[i, k]),
                            f"{label} 95 % interval low": float(level[i, k] - 1.959963984540054 * sd[i, k]),
                            f"{label} 95 % interval high": float(level[i, k] + 1.959963984540054 * sd[i, k]),
                            f"{label} conditional standard deviation": float(sd[i, k]),
                            f"own {label}": float(own[i, k])})
            row["warning"] = LEVELS_WARNING
            rows.append(row)
        return _new_rows_table(self, rows)
