"""compare_each_pair(test=...) beyond Welch, Mann-Whitney and Tukey: the usual follow-up tests.

Each comes from the package that defines it; simplydata only puts the pairs in order and words them:

* "games-howell" (averages, groups with different spreads): R rstatix::games_howell_test(), the
  same numbers as PMCMRplus::gamesHowellTest(), with simultaneous 95 % intervals.
* "scheffe" and "lsd" (averages): R DescTools::ScheffeTest() and PostHocTest(method = "lsd");
  Fisher's LSD does not adjust for the number of pairs, and the sentence says so.
* "dunn" (ranks, after Kruskal-Wallis): R FSA::dunnTest(method = "holm"), the same numbers as
  dunn.test(altp = TRUE) and PMCMRplus::kwAllPairsDunnTest().
* "conover" (ranks): R PMCMRplus::kwAllPairsConoverTest(p.adjust.method = "holm").
* against="A" (every group against one control group): Dunnett's test, SciPy stats.dunnett (as R
  multcomp::glht(mcp(group = "Dunnett"))); SciPy and multcomp both integrate the multivariate t
  distribution with random numbers, so simplydata seeds SciPy's (with_seed=1, printed) and the last digit
  can differ from R's.

All pairs come in the order of R's combn(): (1, 2), (1, 3), ..., (2, 3), ... as in R's output.
"""

from __future__ import annotations

import numpy as np

from .._errors import SimplydataError

# test= -> (name in sentences, based_on, R function, how the p-values are adjusted)
R_PAIR_TESTS = {
    "games-howell": ("Games-Howell test", "averages", "rstatix::games_howell_test()",
                     "the p-values and 95 % intervals hold for all pairs at once (Tukey's studentized range "
                     "with Welch's degrees of freedom), so the chance of any false alarm stays at 5 %"),
    "scheffe": ("Scheffe's test", "averages", "DescTools::ScheffeTest()",
                "the p-values and 95 % intervals hold for all pairs at once (and for any other comparison of the "
                "averages), so the chance of any false alarm stays at 5 %"),
    "lsd": ("Fisher's least significant difference", "averages", 'DescTools::PostHocTest(method = "lsd")',
            "the p-values are NOT adjusted for the number of pairs, so with many pairs a false alarm is more likely"),
    "dunn": ("Dunn's test", "ranks", 'FSA::dunnTest(method = "holm")',
             "the p-values are adjusted with Holm's method, so the chance of any false alarm stays at 5 %"),
    "conover": ("Conover's test", "ranks", 'PMCMRplus::kwAllPairsConoverTest(p.adjust.method = "holm")',
                "the p-values are adjusted with Holm's method, so the chance of any false alarm stays at 5 %"),
}

_R_CODE = {
    "games-howell": ('r <- rstatix::games_howell_test(data.frame(y = y, g = factor(g, levels = lv)), y ~ g); '
                     "list(d = -r$estimate, low = -r$conf.high, high = -r$conf.low, p = r$p.adj)", ("rstatix",)),
    "scheffe": ("r <- DescTools::ScheffeTest(stats::aov(y ~ factor(g, levels = lv)))[[1]]; "
                'list(d = -r[, "diff"], low = -r[, "upr.ci"], high = -r[, "lwr.ci"], p = r[, "pval"])', ("DescTools",)),
    "lsd": ('r <- DescTools::PostHocTest(stats::aov(y ~ factor(g, levels = lv)), method = "lsd")[[1]]; '
            'list(d = -r[, "diff"], low = -r[, "upr.ci"], high = -r[, "lwr.ci"], p = r[, "pval"])', ("DescTools",)),
    "dunn": ('r <- FSA::dunnTest(y ~ factor(g, levels = lv), method = "holm")$res; '
             "list(z = r$Z, p_raw = r$P.unadj, p = r$P.adj)", ("FSA",)),
    "conover": ('r <- PMCMRplus::kwAllPairsConoverTest(y, factor(g, levels = lv), p.adjust.method = "holm"); '
                "list(p = r$p.value[lower.tri(r$p.value, diag = TRUE)], "
                "stat = r$statistic[lower.tri(r$statistic, diag = TRUE)])", ("PMCMRplus",)),
}


def r_pairs(test, groups):
    """[{group 1, group 2, ...}] for a test of R_PAIR_TESTS, pairs in R's combn() order."""
    from .._r import r_call

    names = [g[0] for g in groups]
    y = np.concatenate([g[1] for g in groups])
    g = np.repeat(np.array(names, dtype=object), [len(v) for v in (x[1] for x in groups)])
    code, packages = _R_CODE[test]
    title, based_on, r_name, _ = R_PAIR_TESTS[test]
    found = r_call(code, packages=packages, what=f"{title} (R {r_name})",
                   python_note=("without R, leave out test= for Welch's t-tests (or Mann-Whitney U with "
                                'based_on="ranks") with Holm\'s correction, or use test="tukey"'),
                   y=y.astype(float), g=g, lv=np.array(names, dtype=object))
    pairs = [(i, j) for i in range(len(names)) for j in range(i + 1, len(names))]
    if test == "conover":
        # lower triangle of R's matrix, column by column: (2, 1), (3, 1), ..., (3, 2), ... -> pairs (1, 2), (1, 3), (2, 3)
        order = [(j, i) for i in range(len(names) - 1) for j in range(i + 1, len(names))]
        lookup = dict(zip(order, np.asarray(found["p"], dtype=float)))
        stat = dict(zip(order, np.asarray(found["stat"], dtype=float)))
    rows = []
    for k, (i, j) in enumerate(pairs):
        (n1, a), (n2, b) = groups[i], groups[j]
        row = {"group 1": n1, "group 2": n2, "test": title}
        if based_on == "averages":
            row.update({"difference": float(np.asarray(found["d"])[k]),
                        "difference 95 % CI low": float(np.asarray(found["low"])[k]),
                        "difference 95 % CI high": float(np.asarray(found["high"])[k]),
                        "p-value (adjusted)" if test != "lsd" else "p-value": float(np.asarray(found["p"])[k])})
        elif test == "dunn":
            row.update({"difference in medians": float(np.median(a) - np.median(b)), "statistic name": "z",
                        "statistic": float(np.asarray(found["z"])[k]), "p-value": float(np.asarray(found["p_raw"])[k]),
                        "p-value (adjusted)": float(np.asarray(found["p"])[k])})
        else:
            row.update({"difference in medians": float(np.median(a) - np.median(b)), "statistic name": "q",
                        "statistic": stat[(j, i)], "p-value (adjusted)": lookup[(j, i)]})
        row.update({"count in group 1": len(a), "count in group 2": len(b)})
        rows.append(row)
    return rows


def dunnett_pairs(groups, against, seed):
    """[{group, against, difference, CI, p}] Dunnett's test of every group against one, SciPy stats.dunnett."""
    from scipy import stats

    names = [g[0] for g in groups]
    if against not in names:
        from .._errors import choice_error

        raise choice_error("compare_each_pair_of", "against", against, names)
    control = dict(groups)[against]
    others = [(n, v) for n, v in groups if n != against]
    result = stats.dunnett(*[v for _, v in others], control=control, rng=np.random.default_rng(seed))
    interval = result.confidence_interval(0.95)
    rows = []
    for k, (n, v) in enumerate(others):
        rows.append({"group 1": n, "group 2": against, "test": "Dunnett's test",
                     "difference": float(v.mean() - control.mean()),
                     "difference 95 % CI low": float(interval.low[k]), "difference 95 % CI high": float(interval.high[k]),
                     "statistic name": "t", "statistic": float(result.statistic[k]),
                     "p-value (adjusted)": float(result.pvalue[k]), "count in group 1": len(v),
                     "count in group 2": len(control)})
    if not rows:
        raise SimplydataError("against= needs at least one other group to compare with.")
    return rows


P_COLUMNS = ("p-value (Holm)", "p-value (Tukey)", "p-value (adjusted)", "p-value")  # the one the letters use


def pair_letters(names, rows):
    """{group: letters} from the pairs' (adjusted) p-values: R multcompView::multcompLetters(), threshold 0.05.

    Groups that share a letter have a p-value of 0.05 or more between them. Gives back (letters, the
    p-value column used)."""
    from .._r import r_call

    p_name = next(c for c in P_COLUMNS if c in rows[0])
    k = len(names)
    index = {n: i for i, n in enumerate(names)}
    matrix = np.ones((k, k))
    for row in rows:
        i, j = index[row["group 1"]], index[row["group 2"]]
        matrix[i, j] = matrix[j, i] = row[p_name]
    found = r_call("dimnames(p) <- list(lv, lv); unname(multcompView::multcompLetters(p, threshold = 0.05)$Letters"
                   "[lv])", packages=("multcompView",), what="the letters (R multcompView::multcompLetters())",
                   python_note="without R, leave out show= to see each pair with its p-value",
                   p=matrix, lv=np.array(names, dtype=object))
    return dict(zip(names, (str(v) for v in np.atleast_1d(found)))), p_name
