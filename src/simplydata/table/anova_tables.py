"""explain(..., test_type=): a table with one test for each column (an ANOVA table).

* test_type="type 2" (the usual choice): each column tested after the others it does not
  belong with (R car::Anova(type = 2)); "type 3": each column tested after all the others,
  with sum-to-zero coding done for the user (R car::Anova(type = 3) with contr.sum); "in order":
  each column after the ones before it in using= (R anova(), type 1), so the order matters.
* Numbers: statsmodels anova_lm(typ=1/2/3) on the same model (F tests, sums of squares), = R.
  Partial eta-squared, the share of the variation a column explains once the others are set
  aside, from R effectsize::eta_squared(partial = TRUE) itself; without R it is left out with
  a note.
* Yes/no and counts: likelihood-ratio tests from R car::Anova(type = 2/3, test = "LR") or
  anova(test = "Chisq") itself.
"""

from __future__ import annotations

import math
import warnings

import numpy as np

from .._errors import SimplydataError
from .stat_tests import _num, _whole
from .summaries import _p_words

TEST_TYPES = ("type 2", "type 3", "in order")
TEST_TYPE_SPELLINGS = {"type ii": "type 2", "ii": "type 2", "2": "type 2", "type iii": "type 3", "iii": "type 3",
                       "3": "type 3", "type 1": "in order", "type i": "in order", "1": "in order",
                       "sequential": "in order"}
R_FAMILY = {"binomial": "binomial", "poisson": "poisson", "negbin": None, "gamma": 'Gamma(link = "log")',
            "quasipoisson": "quasipoisson"}


def read_test_type(value):
    text = str(value).strip().lower()
    text = TEST_TYPE_SPELLINGS.get(text, text)
    if text not in TEST_TYPES:
        raise SimplydataError(f'test_type= is "type 2" (the usual choice), "type 3" or "in order", not {value!r}.')
    return text


def _frame_and_formula(model, coding):
    """A data frame with safe names and an R/patsy formula for the model's terms."""
    import pandas as pd

    names = {v: f"v{i}" for i, v in enumerate(model["variables"])}
    data = {"y": model["y"]}
    for v in model["variables"]:
        data[names[v]] = model["data"][v]
    frame = pd.DataFrame(data)
    pieces = []
    for term in model["terms"]:
        parts = []
        for v in term:
            if model["kinds"][v] == "group":
                frame[names[v]] = frame[names[v]].astype(str)
                parts.append(f"C({names[v]}, {coding})")
            else:
                parts.append(names[v])
        pieces.append(":".join(parts))
    model["_pieces"] = dict(zip(pieces, (_label(t) for t in model["terms"])))
    return frame, "y ~ " + " + ".join(pieces), names


def _label(term):
    return " : ".join(term)


def anova_numbers(model, test_type):
    """statsmodels anova_lm on the lm model: rows (term, sum of squares, df, F, p) and the residual row."""
    if test_type == "in order":
        return _sequential_numbers(model)
    import statsmodels.formula.api as smf
    from statsmodels.stats.anova import anova_lm

    coding = "Sum" if test_type == "type 3" else "Treatment"
    frame, formula, _ = _frame_and_formula(model, coding)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit = smf.ols(formula, data=frame).fit()
        table = anova_lm(fit, typ={"type 2": 2, "type 3": 3}[test_type])
    # rows by name: patsy puts group terms before number terms, so the order is not using='s order
    names = dict(model["_pieces"], Intercept="(intercept)", Residual="residual")
    by_name = {names.get(str(index), str(index)): r for index, r in table.iterrows()}
    order = (["(intercept)"] if test_type == "type 3" else []) + [_label(t) for t in model["terms"]] + ["residual"]
    rows = []
    for label in order:
        r = by_name[label]
        rows.append(dict(term=label, ss=float(r["sum_sq"]), df=float(r["df"]),
                         stat=float(r["F"]) if not math.isnan(r["F"]) else math.nan,
                         p=float(r["PR(>F)"]) if not math.isnan(r["PR(>F)"]) else math.nan))
    return rows


def _sequential_numbers(model):
    """Type 1 ("in order"), as R anova(lm()): each term after the ones before it in the model's own term order
    (using= order, main effects before interactions, as R's formula). statsmodels anova_lm() on nested OLS fits
    that add the terms one at a time, each fit using the columns of the model matrix (R model.matrix()) that the
    terms so far own, as R's sequential sums of squares do; patsy's own order (group terms first) is not used."""
    import statsmodels.api as sm
    from statsmodels.stats.anova import anova_lm

    X, y, owner = np.asarray(model["X"], dtype=float), np.asarray(model["y"], dtype=float), np.asarray(model["owner"])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fits = [sm.OLS(y, X[:, owner < k]).fit() for k in range(len(model["terms"]) + 1)]
        table = anova_lm(*fits)
    rows = []
    for term, (_, r) in zip(model["terms"], list(table.iterrows())[1:]):
        rows.append(dict(term=_label(term), ss=float(r["ss_diff"]), df=float(r["df_diff"]), stat=float(r["F"]),
                         p=float(r["Pr(>F)"])))
    last = fits[-1]
    rows.append(dict(term="residual", ss=float(last.ssr), df=float(last.df_resid), stat=math.nan, p=math.nan))
    return rows


def _r_pieces(model, names):
    """The R formula pieces of the model's terms (factor() for group columns), with the label of each."""
    pieces = {}
    for term in model["terms"]:
        parts = [f"factor({names[v]})" if model["kinds"][v] == "group" else names[v] for v in term]
        pieces[":".join(parts)] = _label(term)
    return pieces


def _in_r_with_coding(test_type, code):
    """R code run inside a function that sets sum-to-zero coding for type 3 and puts R's own coding back on the
    way out, also when the code stops (on.exit), so a failure never leaves R with contr.sum."""
    if test_type != "type 3":
        return code
    return ("(function() { op <- options(contrasts = c('contr.sum', 'contr.poly')); on.exit(options(op)); "
            + code + " })()")


def eta_squared(model, test_type):
    """Partial eta-squared for each term, R effectsize::eta_squared(partial = TRUE) on the same table, as a dict
    term label -> value (R's terms in the formula's order, which is the model's term order)."""
    from .._r import r_call

    frame, _, names = _frame_and_formula(model, "Treatment")
    pieces = _r_pieces(model, names)
    values = {col: frame[col].to_numpy() for col in frame.columns}
    code = (f"d <- data.frame({', '.join(values)}); "
            + _in_r_with_coding(test_type, f"m <- stats::lm(y ~ {' + '.join(pieces)}, data = d); "
                                + ("a <- stats::anova(m); " if test_type == "in order" else
                                   f"a <- car::Anova(m, type = {3 if test_type == 'type 3' else 2}); ")
                                + "e <- effectsize::eta_squared(a, partial = TRUE, verbose = FALSE); "
                                + "list(term = as.character(e$Parameter), eta = e$Eta2_partial)"))
    out = r_call(code, packages=("car", "effectsize"), what="Partial eta-squared (R effectsize::eta_squared())",
                 python_note="statsmodels has no eta-squared", **values)
    # R may write an interaction's parts in another order (b:a as a:b), so match the parts, not the text
    by_parts = {frozenset(piece.split(":")): label for piece, label in pieces.items()}
    return {by_parts.get(frozenset(str(t).split(":")), str(t)): float(e)
            for t, e in zip(np.atleast_1d(out["term"]), np.atleast_1d(out["eta"]))}


def anova_glm(model, test_type):
    """R car::Anova(type = 2/3, test = "LR") or anova(test = "Chisq") on the same GLM: rows (term, chi, df, p)."""
    from .._r import r_call

    kind = model["kind"]
    family = R_FAMILY.get(kind)
    coding = "Treatment"
    frame, formula, names = _frame_and_formula(model, coding)
    r_formula = formula
    for v, safe in names.items():
        r_formula = r_formula.replace(f"C({safe}, Treatment)", f"factor({safe})")
    values = {col: frame[col].to_numpy() for col in frame.columns}
    fit = (f"m <- MASS::glm.nb({r_formula}, data = d); " if kind == "negbin" else
           f"m <- stats::glm({r_formula}, data = d, family = {family}); ")
    test = "F" if kind in ("quasipoisson", "gamma") else "LR"
    if test_type == "in order":
        table = f"a <- stats::anova(m, test = '{'F' if test == 'F' else 'Chisq'}'); a <- a[-1, , drop = FALSE]; "
        stat = "if ('F' %in% names(a)) a$F else a$Deviance"
        p = "a[[ncol(a)]]"
    else:
        table = f"a <- car::Anova(m, type = {3 if test_type == 'type 3' else 2}, test.statistic = '{test}'); "
        stat = "if ('F values' %in% names(a) || 'F' %in% names(a)) a[[grep('^F', names(a))[1]]] else a[[1]]"
        p = "a[[ncol(a)]]"
    code = (f"d <- data.frame({', '.join(values)}); "
            + _in_r_with_coding(test_type, fit + table + f"list(term = rownames(a), stat = as.numeric({stat}), "
                                f"df = as.numeric(a$Df), p = as.numeric({p}))"))
    out = r_call(code, packages=("car", "MASS"), what=GLM_WHAT, python_note=GLM_NOTE, **values)
    labels = [_label(t) for t in model["terms"]]
    terms = [str(t) for t in np.atleast_1d(out["term"])]
    rows = []
    for r_term, stat, df, p in zip(terms, np.atleast_1d(out["stat"]), np.atleast_1d(out["df"]),
                                   np.atleast_1d(out["p"])):
        if r_term in ("Residuals", "(Intercept)") or r_term.startswith("Residual"):
            continue
        rows.append(dict(term=labels[len(rows)] if len(rows) < len(labels) else r_term, ss=math.nan,
                         df=float(df), stat=float(stat), p=float(p)))
    return rows, ("F" if test == "F" else "chi-square")


GLM_WHAT = "Tests for each column of this model (R car::Anova())"
GLM_NOTE = "statsmodels gives these tests only for least-squares models"


def need_r_for(model):
    """Before anything is printed: the tests for yes/no and counts come from R car::Anova(), so say what to
    install now rather than after the model has been printed."""
    from .._r import need_r

    if model["kind"] != "lm":
        need_r(("car", "MASS"), GLM_WHAT, GLM_NOTE)


WHAT = {"type 2": 'type 2: each column after the others it does not belong with, as R car::Anova(type = 2)',
        "type 3": 'type 3: each column after all the others, with sum-to-zero coding, as R car::Anova(type = 3)',
        "in order": "in order: each column after the ones before it in using=, as R anova(); the order matters"}


def report(model, test_type):
    """Print the table of tests; gives back the rows for the result table."""
    from .._r import RMissing

    if model["kind"] in ("mixed", "glmm", "gee"):
        raise SimplydataError("test_type= is not available with grouped_by= yet; the whole-column Wald tests are "
                              "printed instead.")
    out_rows = []
    if model["kind"] == "lm":
        rows = anova_numbers(model, test_type)
        terms = [r for r in rows if r["term"] not in ("residual", "(intercept)")]
        try:
            etas = eta_squared(model, test_type)
        except RMissing:
            etas = None
        print(f"Tests for each column ({WHAT[test_type]}):")
        residual = rows[-1]
        for r in terms:
            value = math.nan if etas is None else etas.get(r["term"], math.nan)
            eta = "" if math.isnan(value) else f", partial eta-squared {_num(value)}"
            print(f"  {r['term']}: F = {_num(r['stat'])}, df = {_whole(r['df'])} and {_whole(residual['df'])}"
                  f"{eta}; {_p_words(r['p'])}.")
            out_rows.append({"term": f"{r['term']} (test, {test_type})", "statistic name": "F",
                             "statistic": r["stat"], "degrees of freedom": r["df"], "p-value": r["p"],
                             "sum of squares": r["ss"],
                             "partial eta-squared": value})
        if etas is None:
            print("Note: partial eta-squared needs R (pip install \"simplydata[r]\" and R with the effectsize "
                  "package); the tests above do not.")
        else:
            print("Partial eta-squared: the share of the variation in the outcome that a column explains once the "
                  "other columns are set aside (R effectsize::eta_squared(partial = TRUE)).")
        return out_rows
    rows, name = anova_glm(model, test_type)
    print(f"Tests for each column ({WHAT[test_type]}, likelihood-ratio tests run in R):")
    for r in rows:
        print(f"  {r['term']}: {name} = {_num(r['stat'])}, df = {_whole(r['df'])}; {_p_words(r['p'])}.")
        out_rows.append({"term": f"{r['term']} (test, {test_type})", "statistic name": name,
                         "statistic": r["stat"], "degrees of freedom": r["df"], "p-value": r["p"]})
    return out_rows
