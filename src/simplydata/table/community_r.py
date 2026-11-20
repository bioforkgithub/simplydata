"""The R calls of the community words (S3c-1), through rpy2 (simplydata[r]).

Each function runs R's own code (vegan, zCompositions, compositions, cluster, MASS, ca, stats) and gives back
plain NumPy values; the words in communities.py and patterns.py check the input and say the result in words.
Packages that would mask base R functions when attached (compositions masks var, cor, dist ...) are never
attached: they are checked with need_r() and called as pkg::fun. vegan is attached as patterns.py always did.
"""

from __future__ import annotations

import numpy as np

from .._errors import SimplydataError

# measure= -> the vegan::vegdist() arguments
VEGDIST = {"bray-curtis": 'method = "bray"', "euclidean": 'method = "euclidean"',
           "manhattan": 'method = "manhattan"', "jaccard": 'method = "jaccard", binary = TRUE',
           "aitchison": 'method = "aitchison"', "robust aitchison": 'method = "robust.aitchison"',
           "hellinger": 'method = "hellinger"'}
GBM = ('as.matrix(zCompositions::cmultRepl({x}, method = "GBM", output = "p-counts", z.delete = FALSE, '
       "suppress.print = TRUE))")
R_ONLY_MEASURES = ("aitchison", "robust aitchison", "hellinger")


def packages_for(measure) -> tuple:
    return ("vegan", "zCompositions") if measure == "aitchison" else ("vegan",)


def replaced(x, measure) -> bool:
    """True when the measure replaces zeros first (Aitchison distances on a table with zeros)."""
    return measure == "aitchison" and bool((x == 0).any())


def distance_code(measure, x, name="x", out="d") -> str:
    """R code that makes `out`, the measure= distances between the rows of `name`; for "aitchison" the zeros are
    replaced by estimated small values first (zCompositions GBM), as vegdist() refuses zeros."""
    prepare = f"{name} <- {GBM.format(x=name)}; " if replaced(x, measure) else ""
    return f"{prepare}{out} <- vegan::vegdist({name}, {VEGDIST[measure]}); "


def _need(packages, what):
    from .._r import need_r

    need_r(tuple(packages), what)


def _call(code, what, packages=("vegan",), source=None, **values):
    from .._r import r_call

    _need(packages, what)
    attach = ("vegan",) if "vegan" in packages else ()
    return r_call(code, packages=attach, what=what, source=source, **values)


# ---------------------------------------------------------------- distances
def r_distances(x, measure):
    """Condensed distances (SciPy's order, which is R dist's order) for the measures only R gives."""
    found = _call(distance_code(measure, x) + "as.numeric(d)", f'{measure.capitalize()} distances (R vegan::vegdist())',
                  packages_for(measure), source="vegan::vegdist", x=x)
    return np.asarray(found, dtype=float)


# ---------------------------------------------------------------- diversity
def diversity(x, at_total_count=None, chao=False):
    """vegan's richness, Shannon, Simpson, inverse Simpson, Hill numbers (renyi(hill = TRUE)), and on request
    Chao1 (estimateR) and the expected richness at a total count (rarefy)."""
    code = ("list(richness = vegan::specnumber(x), shannon = vegan::diversity(x, index = \"shannon\"), "
            "simpson = vegan::diversity(x, index = \"simpson\"), "
            "invsimpson = vegan::diversity(x, index = \"invsimpson\"), "
            "hill = as.matrix(vegan::renyi(x, scales = c(0, 1, 2), hill = TRUE)), "
            f"chao = {'vegan::estimateR(x)' if chao else 'NULL'}, "
            f"rarefied = {f'suppressWarnings(vegan::rarefy(x, sample = {int(at_total_count)}))' if at_total_count else 'NULL'})")
    found = _call(code, "Diversity (R vegan::diversity(), specnumber(), renyi())", source="vegan", x=x)
    out = {k: (None if v is None else np.asarray(v, dtype=float)) for k, v in found.items()}
    if out["hill"] is not None and out["hill"].ndim == 1:
        out["hill"] = out["hill"].reshape(len(x), 3, order="F")
    if out["chao"] is not None and out["chao"].ndim == 1:
        out["chao"] = out["chao"].reshape(5, len(x), order="F")
    return out


def richness_curves(x, step):
    """vegan::rarecurve(tidy = TRUE): the expected richness of each row at total counts step apart."""
    found = _call(f"rownames(x) <- seq_len(nrow(x)); colnames(x) <- seq_len(ncol(x)); "
                  f"r <- vegan::rarecurve(x, step = {int(step)}, tidy = TRUE); "
                  "list(row = as.integer(r$Site), at = r$Sample, richness = r$Species)",
                  "Richness curves (R vegan::rarecurve())", source="vegan::rarecurve", x=x)
    return {k: np.asarray(v, dtype=float) for k, v in found.items()}


# ---------------------------------------------------------------- log ratios
def log_ratios(x, method, how, reference=None, zeros=True):
    """clr, alr (against the column at position reference, counted from 1) or ilr, after the zeros are handled:
    zCompositions GBM then compositions::clr / alr / ilr, or vegan::decostand(pseudocount = 1) for "adding 1"."""
    from ._compositions import ADDING_ONE

    if zeros and how == ADDING_ONE:
        extra = f", reference = {int(reference)}" if method == "alr" else ""
        code = f'm <- vegan::decostand(x, method = "{method}", pseudocount = 1{extra}); unname(as.matrix(m))'
        packages = ("vegan",)
    else:
        prepare = f"x <- {GBM.format(x='x')}; " if zeros else ""
        call = {"clr": "compositions::clr(x)", "ilr": "compositions::ilr(x)",
                "alr": f"compositions::alr(x, ivar = {int(reference or 0)})"}[method]
        code = f"{prepare}m <- {call}; unname(matrix(as.numeric(unclass(m)), nrow = nrow(x)))"
        packages = ("zCompositions", "compositions") if zeros else ("compositions",)
    found = _call(code, "Log ratios (R zCompositions and compositions)", packages=packages,
                  source="compositions" if packages != ("vegan",) else "vegan::decostand", x=x)
    return np.asarray(found, dtype=float).reshape(len(x), -1)


# ---------------------------------------------------------------- PCoA
def principal_coordinates(x, measure, k):
    """stats::cmdscale(d, k, eig = TRUE): the coordinates, the eigenvalues and cmdscale's goodness of fit for
    1 ... k axes (GOF[2]: the share of the positive eigenvalues); vegan's proportion for axis 1 (all eigenvalues,
    negative ones included, as ape::pcoa) for the sentence that reconciles the two."""
    code = (distance_code(measure, x) + f"p <- stats::cmdscale(d, k = {int(k)}, eig = TRUE); "
            f"list(points = unname(p$points), eig = p$eig, "
            f"gof = sapply(seq_len({int(k)}), function(j) stats::cmdscale(d, k = j, eig = TRUE)$GOF[2]), "
            "vegan_first = summary(vegan::eigenvals(vegan::wcmdscale(d, eig = TRUE)))[2, 1])")
    found = _call(code, "Principal coordinates (R stats::cmdscale())", packages_for(measure),
                  source="stats::cmdscale", x=x)
    points = np.asarray(found["points"], dtype=float).reshape(len(x), k, order="F") if np.ndim(
        found["points"]) == 1 else np.asarray(found["points"], dtype=float)
    return {"points": points, "eig": np.asarray(found["eig"], dtype=float),
            "gof": np.atleast_1d(np.asarray(found["gof"], dtype=float)), "vegan_first": float(found["vegan_first"][0])}


# ---------------------------------------------------------------- constrained ordination
def _env_code(env_names):
    """R code that builds env, a data frame of the using= and allowing_for= columns (v1, v2 ... come in)."""
    parts = ", ".join(f"v{i}" for i in range(1, len(env_names) + 1))
    return (f"env <- data.frame({parts}, stringsAsFactors = TRUE); "
            "names(env) <- simplydata_env_names; ")


def _term(name):
    return "`" + str(name).replace("`", "") + "`"


def model_call(kind, measure, using, allowing_for):
    """The vegan call as R code (shown in the printout): kind "rda", "dbrda" or "cca"."""
    rhs = " + ".join(_term(u) for u in using)
    if allowing_for:
        rhs += " + Condition(" + " + ".join(_term(a) for a in allowing_for) + ")"
    if kind == "cca":
        return f"vegan::cca(y ~ {rhs}, data = env)"
    if kind == "rda":
        return f"vegan::rda(y ~ {rhs}, data = env)"
    return f"vegan::dbrda(d ~ {rhs}, data = env)"


def constrained(x, kind, measure, using, allowing_for, env, permutations, seed):
    """vegan rda / dbrda / cca with RsquareAdj, the overall test, each column tested after the others
    (anova(by = "margin")) and vif.cca."""
    names = [*using, *allowing_for]
    values = {f"v{i}": v for i, v in enumerate(env, 1)}
    if kind == "rda" and measure == "hellinger":
        prepare = 'y <- vegan::decostand(x, "hellinger"); '
    elif kind == "rda" and measure == "aitchison":
        prepare = (f"y <- {GBM.format(x='x')}; " if replaced(x, measure) else "y <- x; ") + \
            "y <- unclass(compositions::clr(y)); "
    elif kind == "dbrda":
        prepare = distance_code(measure, x)
    else:
        prepare = "y <- x; "
    fit = model_call(kind, measure, using, allowing_for)
    adjusted = (f"set.seed({int(seed)}); r2 <- vegan::RsquareAdj(m, permutations = {int(permutations)}); "
                if kind == "cca" else "r2 <- vegan::RsquareAdj(m); ")
    code = (prepare + _env_code(names) + f"m <- {fit}; " + adjusted +
            f"set.seed({int(seed)}); all <- anova(m, permutations = {int(permutations)}); "
            f"set.seed({int(seed)}); each <- anova(m, by = \"margin\", permutations = {int(permutations)}); "
            "v <- tryCatch(vegan::vif.cca(m), error = function(e) NULL); "
            "list(r2 = r2$r.squared, adj = r2$adj.r.squared, all_f = all$F[1], all_p = all[[\"Pr(>F)\"]][1], "
            "all_df = all$Df[1], resid_df = all$Df[2], "
            "terms = rownames(each)[seq_len(nrow(each) - 1)], f = each$F[seq_len(nrow(each) - 1)], "
            "p = each[[\"Pr(>F)\"]][seq_len(nrow(each) - 1)], df = each$Df[seq_len(nrow(each) - 1)], "
            "vif = if (is.null(v)) NULL else v, vif_names = if (is.null(v)) NULL else names(v))")
    packages = ("vegan", "zCompositions", "compositions") if measure == "aitchison" else ("vegan",)
    found = _call(code, "Constrained ordination (R vegan)", packages, source="vegan", x=x,
                  simplydata_env_names=np.array(names, dtype=object), **values)
    return {"r2": float(np.asarray(found["r2"]).reshape(-1)[0]),
            "adj": float(np.asarray(found["adj"], dtype=float).reshape(-1)[0]),
            "all_f": float(found["all_f"][0]), "all_p": float(found["all_p"][0]),
            "all_df": float(found["all_df"][0]), "resid_df": float(found["resid_df"][0]),
            "terms": [str(t) for t in np.atleast_1d(found["terms"])],
            "f": np.atleast_1d(np.asarray(found["f"], dtype=float)),
            "p": np.atleast_1d(np.asarray(found["p"], dtype=float)),
            "df": np.atleast_1d(np.asarray(found["df"], dtype=float)),
            "vif": None if found.get("vif") is None else np.atleast_1d(np.asarray(found["vif"], dtype=float)),
            "vif_names": None if found.get("vif_names") is None else [str(n) for n in np.atleast_1d(found["vif_names"])]}


# ---------------------------------------------------------------- ANOSIM and SIMPER
def anosim(x, measure, groups, permutations, seed):
    """vegan::anosim on vegdist distances, then betadisper and permutest (the spread check), after set.seed."""
    code = (f"set.seed({int(seed)}); " + distance_code(measure, x) + "g <- factor(g); "
            f"a <- vegan::anosim(d, g, permutations = {int(permutations)}); "
            f"b <- vegan::betadisper(d, g); t <- vegan::permutest(b, permutations = {int(permutations)}); "
            "list(r = a$statistic, p = a$signif, spread_f = t$tab$F[1], spread_p = t$tab[['Pr(>F)']][1], "
            "distances = as.numeric(b$distances))")
    found = _call(code, "ANOSIM (R vegan::anosim())", packages_for(measure), source="vegan", x=x, g=groups)
    return {k: (float(v[0]) if k != "distances" else np.asarray(v, dtype=float)) for k, v in found.items()}


def simper(x, groups, columns):
    """vegan::simper(permutations = 0) and its summary: one table per pair of groups."""
    code = ("colnames(x) <- simplydata_columns; g <- factor(g); s <- summary(vegan::simper(x, g, permutations = 0)); "
            "lapply(s, function(t) list(column = rownames(t), average = t$average, sd = t$sd, ratio = t$ratio, "
            "ava = t$ava, avb = t$avb, cumsum = t$cumsum))")
    found = _call(code, "SIMPER (R vegan::simper())", source="vegan::simper", x=x, g=groups,
                  simplydata_columns=np.array([str(c) for c in columns], dtype=object))
    return {pair: {k: (np.asarray(v, dtype=float) if k != "column" else [str(c) for c in v]) for k, v in t.items()}
            for pair, t in found.items()}


# ---------------------------------------------------------------- Mantel and Procrustes
def profile_correlation(x, y, measure_x, measure_y, method, permutations, seed):
    """vegan::mantel (Pearson) or vegan::protest on the first two principal coordinates of each set."""
    second = (distance_code(measure_y, y, name="y", out="e") if measure_y != "scaled euclidean"
              else "e <- stats::dist(scale(y)); ")
    if method == "mantel":
        test = (f"t <- vegan::mantel(d, e, method = \"pearson\", permutations = {int(permutations)}); "
                "list(r = t$statistic, p = t$signif)")
    else:
        test = (f"t <- vegan::protest(stats::cmdscale(d, k = 2), stats::cmdscale(e, k = 2), "
                f"permutations = {int(permutations)}); list(r = t$t0, p = t$signif, ss = t$ss)")
    code = f"set.seed({int(seed)}); " + distance_code(measure_x, x) + second + test
    packages = tuple(dict.fromkeys(packages_for(measure_x) + (packages_for(measure_y) if measure_y != "scaled euclidean"
                                                              else ())))
    found = _call(code, f"{method.capitalize()} (R vegan::{'mantel' if method == 'mantel' else 'protest'}())",
                  packages, source="vegan", x=x, y=y)
    return {k: float(np.asarray(v).reshape(-1)[0]) for k, v in found.items()}


# ---------------------------------------------------------------- clusters
def silhouettes(labels, x, measure):
    """cluster::silhouette(labels, d): each row's width and next best cluster, and the average width. measure None:
    straight-line distances between the rows of x as given (the columns already on the same scale)."""
    d = "d <- stats::dist(x); " if measure is None else distance_code(measure, x)
    code = (d + "s <- cluster::silhouette(as.integer(k), d); "
            "list(width = s[, \"sil_width\"], neighbour = s[, \"neighbor\"], average = summary(s)$avg.width)")
    found = _call(code, "Silhouette widths (R cluster::silhouette())",
                  ("cluster",) + (packages_for(measure) if measure else ()),
                  source="cluster::silhouette", x=x, k=np.asarray(labels, dtype=float))
    return {"width": np.asarray(found["width"], dtype=float), "neighbour": np.asarray(found["neighbour"], dtype=int),
            "average": float(found["average"][0])}


# ---------------------------------------------------------------- discriminant axes
def discriminant(x, groups):
    """MASS::lda (prior = the group shares, MASS's default), predict()$x, leave-one-out classes (CV = TRUE), and
    the proportion of trace as MASS prints it."""
    code = ("f <- MASS::lda(x, g); s <- predict(f)$x; cv <- MASS::lda(x, g, CV = TRUE)$class; "
            "o <- local({ op <- options(width = 200, digits = 7); on.exit(options(op)); utils::capture.output(MASS:::print.lda(f)) }); i <- grep(\"Proportion of trace\", o, fixed = TRUE); "
            "v <- if (length(i)) o[(i[1] + 1):length(o)] else character(0); v <- v[!grepl(\"LD\", v)]; "
            "trace <- suppressWarnings(as.numeric(unlist(strsplit(trimws(paste(v, collapse = \" \")), \"\\\\s+\")))); "
            "list(scores = unname(as.matrix(s)), loo = as.character(cv), prior = unname(f$prior), "
            "levels = names(f$prior), trace = trace)")
    from .._r import r_call

    _need(("MASS",), "Discriminant axes (R MASS::lda())")
    try:
        found = r_call(code, what="Discriminant axes (R MASS::lda())", source="MASS::lda", x=x,
                       g=np.asarray(groups, dtype=object))
    except SimplydataError as error:
        if "constant within groups" in str(error):
            raise SimplydataError("A column has the same value in every row of a group, so it cannot help to "
                                  "separate the groups (R MASS::lda() stops: \"variable appears to be constant "
                                  "within groups\"). Leave it out with columns=[...].") from None
        raise
    scores = np.asarray(found["scores"], dtype=float)
    if scores.ndim == 1:
        scores = scores.reshape(len(x), -1)
    return {"scores": scores, "loo": np.asarray(found["loo"], dtype=object),
            "prior": np.asarray(found["prior"], dtype=float), "levels": [str(v) for v in found["levels"]],
            "trace": np.atleast_1d(np.asarray(found["trace"], dtype=float))}


# ---------------------------------------------------------------- correspondence analysis
def correspondence(x, k):
    """CA: vegan::cca(x) without constraints; the share of the inertia of each axis (summary(eigenvals())) and
    the row scores with scaling = "sites"."""
    code = (f"m <- vegan::cca(x); e <- summary(vegan::eigenvals(m)); "
            f"list(share = e[2, ], eig = e[1, ], scores = unname(as.matrix(vegan::scores(m, display = \"sites\", "
            f"scaling = \"sites\", choices = seq_len({int(k)})))))")
    found = _call(code, "Correspondence analysis (R vegan::cca())", source="vegan::cca", x=x)
    scores = np.asarray(found["scores"], dtype=float)
    if scores.ndim == 1:
        scores = scores.reshape(len(x), -1, order="F")
    return {"share": np.asarray(found["share"], dtype=float), "eig": np.asarray(found["eig"], dtype=float),
            "scores": scores}


def multiple_correspondence(columns, values, k):
    """MCA: ca::mjca(lambda = "adjusted"): the adjusted inertia of each axis (Greenacre) and the rows' principal
    coordinates."""
    parts = ", ".join(f"v{i}" for i in range(1, len(values) + 1))
    code = (f"df <- data.frame({parts}, stringsAsFactors = TRUE); names(df) <- simplydata_names; "
            "m <- ca::mjca(df, lambda = \"adjusted\"); "
            f"list(share = m$inertia.e, scores = unname(as.matrix(m$rowpcoord[, seq_len({int(k)}), drop = FALSE])))")
    from .._r import r_call

    _need(("ca",), "Multiple correspondence analysis (R ca::mjca())")
    found = r_call(code, what="Multiple correspondence analysis (R ca::mjca())", source="ca::mjca",
                   simplydata_names=np.array(columns, dtype=object),
                   **{f"v{i}": np.asarray(v, dtype=object) for i, v in enumerate(values, 1)})
    scores = np.asarray(found["scores"], dtype=float)
    if scores.ndim == 1:
        scores = scores.reshape(len(values[0]), -1, order="F")
    return {"share": np.asarray(found["share"], dtype=float), "scores": scores}
