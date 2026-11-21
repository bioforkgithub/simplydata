"""The R calls of phase S3c-4 (small additions): Storey's q-values and the local false discovery rate (R qvalue, from
Bioconductor), and the pair tests after Friedman's test (R PMCMRplus). simplydata puts the numbers in and words the
answer; every number comes from the R package.

* add_adjusted_p_value_column(method="storey" | "local fdr"): R qvalue::qvalue(p) with its defaults (pi0 by the
  smoother over lambda = 0.05, 0.10, ..., 0.95; Storey & Tibshirani 2003), giving $qvalues, $lfdr and $pi0. No Python
  package gives Storey's pi0 with qvalue's smoother (statsmodels fdrcorrection_twostage is another estimator).
* compare_each_pair_of(matched_by=, test="nemenyi" | "conover"): R PMCMRplus::frdAllPairsNemenyiTest(y, groups,
  blocks) (the studentized range, which allows for all pairs itself: no further adjustment) and
  frdAllPairsConoverTest(y, groups, blocks, p.adjust.method = "holm"). scikit-posthocs gives the same Nemenyi
  p-values, but it is not a simplydata dependency, and its Conover test is not adjusted by default.
"""

from __future__ import annotations

import numpy as np

from .._errors import SimplydataError

# test= after Friedman -> (name in sentences, R function, how the p-values are adjusted)
FRIEDMAN_PAIR_TESTS = {
    "nemenyi": ("Nemenyi's test", "PMCMRplus::frdAllPairsNemenyiTest()",
                "Nemenyi's test allows for all the pairs itself (the studentized range), so there is no further "
                "adjustment: do not adjust these p-values again"),
    "conover": ("Conover's test for matched rows", 'PMCMRplus::frdAllPairsConoverTest(p.adjust.method = "holm")',
                "the p-values are adjusted with Holm's method, so the chance of any false alarm stays at 5 %. "
                "scikit-posthocs gives unadjusted p-values and PMCMRplus single-step ones by default, so their "
                "numbers differ"),
}

_FRIEDMAN_OUT = ("list(p = r$p.value[lower.tri(r$p.value, diag = TRUE)], "
                 "stat = r$statistic[lower.tri(r$statistic, diag = TRUE)], dist = r$dist, "
                 "df = if (is.null(r$parameter)) NA_real_ else unname(r$parameter), "
                 # each group's mean rank within the matched rows, R base rank(), for the direction in the printout
                 "ranks = colMeans(t(apply(matrix(y, ncol = length(lv)), 1, rank))))")
_R_FRIEDMAN = {
    "nemenyi": "r <- PMCMRplus::frdAllPairsNemenyiTest(y, factor(g, levels = lv), factor(b)); " + _FRIEDMAN_OUT,
    "conover": 'r <- PMCMRplus::frdAllPairsConoverTest(y, factor(g, levels = lv), factor(b), p.adjust.method = "holm"); '
               + _FRIEDMAN_OUT,
}

_R_QVALUE = "q <- qvalue::qvalue(p); list(q = q$qvalues, lfdr = q$lfdr, pi0 = q$pi0)"


def storey(p, method):
    """{q, lfdr, pi0} from R qvalue::qvalue(p); a friendly error when qvalue cannot estimate pi0."""
    from .._r import RMissing, r_call

    try:
        found = r_call(_R_QVALUE, packages=("qvalue",),
                       what="Storey's q-values and the local false discovery rate (R qvalue::qvalue())",
                       python_note=('without R, method="benjamini-hochberg" gives the false discovery rate with '
                                    "pi0 = 1 (statsmodels)"),
                       source="qvalue::qvalue", p=np.asarray(p, dtype=float))
    except RMissing:
        raise
    except SimplydataError as error:
        raise SimplydataError(
            f"R qvalue could not estimate the share of true nulls (pi0) from these {len(p)} p-value{"" if len(p) == 1 else "s"} "
            f"({' '.join(str(error).removeprefix('R stopped with: ').split())[:200]}). This happens with few p-values, "
            'or when none lies near 1. Use method="benjamini-hochberg", the same idea with pi0 = 1.') from None
    return {"q": np.asarray(found["q"], dtype=float), "lfdr": np.asarray(found["lfdr"], dtype=float),
            "pi0": float(np.asarray(found["pi0"], dtype=float).ravel()[0])}


def friedman_pairs(test, names, blocks, data):
    """[{group 1, group 2, statistic, p-value (adjusted)}] in R's combn() order, from PMCMRplus.

    names: the groups in order; blocks: the matched rows (each measured in every group); data: {group: values in the
    order of blocks}."""
    from .._r import r_call

    title, r_name, _ = FRIEDMAN_PAIR_TESTS[test]
    y = np.concatenate([data[g] for g in names]).astype(float)
    g = np.repeat(np.array([str(n) for n in names], dtype=object), len(blocks))
    b = np.tile(np.array([str(w) for w in blocks], dtype=object), len(names))
    found = r_call(_R_FRIEDMAN[test], packages=("PMCMRplus",), what=f"{title} (R {r_name})",
                   python_note="without R, leave out test= for Wilcoxon signed-rank tests with Holm's correction",
                   y=y, g=g, b=b, lv=np.array([str(n) for n in names], dtype=object))
    # lower triangle of R's matrix, column by column: (2, 1), (3, 1), ..., (3, 2), ... -> pairs (1, 2), (1, 3), (2, 3)
    order = [(j, i) for i in range(len(names) - 1) for j in range(i + 1, len(names))]
    p = dict(zip(order, np.asarray(found["p"], dtype=float).ravel()))
    stat = dict(zip(order, np.asarray(found["stat"], dtype=float).ravel()))
    dist = str(np.atleast_1d(found["dist"])[0])
    df = float(np.asarray(found["df"], dtype=float).ravel()[0])
    ranks = np.asarray(found["ranks"], dtype=float).ravel()
    return [{"i": i, "j": j, "statistic": stat[(j, i)], "p": p[(j, i)], "dist": dist, "df": df,
             "rank 1": float(ranks[i]), "rank 2": float(ranks[j])}
            for i in range(len(names)) for j in range(i + 1, len(names))]
