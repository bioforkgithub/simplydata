"""Patterns across many columns: principal components, clusters, distances, NMDS and PERMANOVA.

These words look at many number columns at once (for example the counts of ten plant species
in each plot of sdata.example("meadow")). columns=None uses every number column; give a list
to choose. Rows with an empty cell in the columns used are left out with a printed note, and
an add_ word gives them empty cells. PCA, distances and hierarchical clusters come from
statsmodels and SciPy; k-means, NMDS and PERMANOVA from R itself (simplydata[r]).

* add_principal_components / principal_components_of: principal component analysis by
  singular value decomposition of the centred (and, with same_scale=True, scaled) columns,
  exactly as R prcomp(x, scale. = TRUE). The sign of a component is arbitrary (flipping it
  changes nothing) and differs between maths libraries, so each component is turned so that
  its biggest weight is positive: the same answer on every computer, equal to R up to sign.
* add_clusters, method="k-means": R stats::kmeans(x, k, nstart = 25) itself (Hartigan-Wong),
  run through rpy2 after set.seed(seed), so the clusters are R's. Needs simplydata[r] and R.
  method="hierarchical": SciPy's agglomerative clustering on Euclidean distances, cut into
  how_many clusters; linkage="ward" is R hclust(method = "ward.D2"), and "average",
  "complete" and "single" are the R methods of the same name. Clusters are numbered 1, 2, 3
  in the order they first appear in the table, so the numbers do not jump between runs.
* distances_between_rows: "bray-curtis" (the R vegan::vegdist default), "euclidean",
  "manhattan", and "jaccard", which is vegan::vegdist(binary = TRUE): the share of the
  species present in either row that are present in only one of them (counts above 0 are
  "present").
* add_nmds: non-metric multidimensional scaling, R vegan::metaMDS() itself on vegdist
  distances (autotransform = FALSE, try = tries=, trymax = 100: R stops as soon as its best
  map repeats), run through rpy2 after
  set.seed(seed). Kruskal stress-1 as metaMDS reports it; the map is centred and turned so
  that NMDS1 holds the most spread (metaMDS default); rotation and signs are arbitrary.
  Clarke's (1993) rule of thumb reads the stress. Needs simplydata[r], R and vegan.
* compare_profiles: PERMANOVA, R vegan::adonis2(distances ~ group) itself, then the spread
  check vegan::betadisper() with vegan::permutest(), run through rpy2 after set.seed(seed),
  so pseudo-F, R squared and both permutation p-values are R's for the same seed. A note is
  printed when the spreads differ. Needs simplydata[r], R and vegan.
"""

from __future__ import annotations

import math
import re

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, friendly
from .stat_tests import _list_words, _num, _p_sentence, _p_shown, _skipped_note

CLUSTER_METHODS = ("k-means", "hierarchical")
LINKAGES = {"ward": "ward.D2", "average": "average", "complete": "complete", "single": "single"}
MEASURES = {"bray-curtis": "Bray-Curtis", "euclidean": "Euclidean", "jaccard": "Jaccard",
            "manhattan": "Manhattan"}
MEASURE_R = {"bray-curtis": 'vegdist(x, "bray")', "euclidean": 'vegdist(x, "euclidean")',
             "jaccard": 'vegdist(x, "jaccard", binary = TRUE)', "manhattan": 'vegdist(x, "manhattan")'}
KMEANS_STARTS = 25
R_SEED_MAX = 2 ** 31 - 1  # the largest seed R set.seed() takes
NMDS_TRIES_UP_TO = 100  # metaMDS trymax: more starts, until the best map repeats
MADE_HERE = re.compile(r"^(PC|NMDS)\d+$")  # columns these words add; columns=None leaves them out


# ---------------------------------------------------------------------------- small helpers
def _pct(share: float) -> str:
    return f"{share * 100:.1f} %"


def _quoted_list(names) -> str:
    return _list_words(f'"{n}"' for n in names)


def _distances(x, measure):
    """Condensed distances between the rows of x, as R vegan::vegdist()."""
    from scipy.spatial.distance import pdist

    if measure == "euclidean":
        return pdist(x, "euclidean")
    if measure == "manhattan":
        return pdist(x, "cityblock")
    if measure == "bray-curtis":
        return pdist(x, "braycurtis")
    return pdist(x > 0, "jaccard")  # vegan binary = TRUE: decostand(x, "pa")


def _square(condensed):
    from scipy.spatial.distance import squareform

    return squareform(condensed, checks=False)


def _first_appearance(labels):
    """Number the groups 1, 2, 3 ... in the order they first appear."""
    values, first = np.unique(labels, return_index=True)
    renumber = {old: new for new, old in enumerate(values[np.argsort(first)], 1)}
    return np.array([renumber[v] for v in labels], dtype=int)


def _sum_squares(x, labels):
    """(within-cluster, total) sums of squares."""
    total = float(((x - x.mean(axis=0)) ** 2).sum())
    within = 0.0
    for g in np.unique(labels):
        part = x[labels == g]
        within += float(((part - part.mean(axis=0)) ** 2).sum())
    return within, total


# ---------------------------------------------------------------------------- R (simplydata[r])
R_DISTANCE = {"bray-curtis": 'method = "bray"', "euclidean": 'method = "euclidean"',
              "manhattan": 'method = "manhattan"', "jaccard": 'method = "jaccard", binary = TRUE'}


def _r_kmeans(z, k, seed):
    """R stats::kmeans(z, k, nstart = 25) after set.seed(seed): (labels 1..k, between_SS / total_SS)."""
    from .._r import r_call

    out = r_call(f"set.seed({int(seed)}); fit <- stats::kmeans(z, centers = {int(k)}, nstart = {KMEANS_STARTS}); "
                 "list(cluster = fit$cluster, between = fit$betweenss, total = fit$totss)",
                 what="k-means (R stats::kmeans())", source="stats::kmeans",
                 python_note="scikit-learn KMeans is similar but finds other clusters; or use "
                             'method="hierarchical", which needs no R', z=z)
    total = float(out["total"][0])
    return out["cluster"].astype(int), (float(out["between"][0]) / total if total > 0 else 0.0)


def _nmds_tries(tries):
    """(try, trymax) for metaMDS: at least tries= random starts, then more up to 100 until the best repeats."""
    first = max(int(tries), 1)
    return first, max(first, NMDS_TRIES_UP_TO)


def _r_nmds(x, measure, dimensions, tries, seed):
    """R vegan::metaMDS on vegdist distances, set.seed(seed): (points, stress, best repeated?)."""
    from .._r import r_call

    out = r_call(f"set.seed({int(seed)}); d <- vegan::vegdist(x, {R_DISTANCE[measure]}); "
                 f"fit <- vegan::metaMDS(d, k = {int(dimensions)}, try = {_nmds_tries(tries)[0]}, "
                 f"trymax = {_nmds_tries(tries)[1]}, "
                 "autotransform = FALSE, trace = 0); "
                 "list(points = unclass(fit$points), stress = fit$stress, "
                 "converged = isTRUE(as.numeric(fit$converged) > 0))",
                 packages=("vegan",), what="NMDS (R vegan::metaMDS())", source="vegan::metaMDS",
                 python_note="scikit-learn MDS(metric=False) is similar but gives a different stress", x=x)
    points = np.asarray(out["points"], dtype=float)
    if points.ndim == 1:
        points = points.reshape(len(x), dimensions, order="F")
    return points, float(out["stress"][0]), bool(out["converged"][0])


def _r_permanova(x, measure, groups, permutations, seed):
    """R vegan::adonis2, then betadisper and permutest, after set.seed(seed), as an R user runs them."""
    from .._r import r_call

    out = r_call(f"set.seed({int(seed)}); d <- vegan::vegdist(x, {R_DISTANCE[measure]}); g <- factor(g); "
                 f"a <- vegan::adonis2(d ~ g, permutations = {int(permutations)}); "
                 f"b <- vegan::betadisper(d, g); t <- vegan::permutest(b, permutations = {int(permutations)}); "
                 "list(f = a$F[1], r2 = a$R2[1], p = a[['Pr(>F)']][1], spread_f = t$tab$F[1], "
                 "spread_p = t$tab[['Pr(>F)']][1], distances = as.numeric(b$distances))",
                 packages=("vegan",), source="vegan",
                 what="PERMANOVA (R vegan::adonis2()) and its spread check (vegan::betadisper())",
                 python_note="scikit-bio permanova gives the same F with another random p-value, but its spread "
                             "check (permdisp) gives different numbers", x=x, g=groups)
    return {k: (float(v[0]) if k != "distances" else np.asarray(v, dtype=float)) for k, v in out.items()}


# ---------------------------------------------------------------------------- the words
class PatternWords:
    # ------------------------------------------------------------------ helpers
    def _pattern_columns(self, step, columns, example, at_least=1, leave_out=()):
        """The columns to use: a list, one name, or None for every number column."""
        if columns is None:
            numbers = [c for c, d in self._frame.schema.items() if d.is_numeric() and c not in leave_out]
            earlier = getattr(self, "_pattern_made", set())
            made = [c for c in numbers if MADE_HERE.match(str(c)) or c in earlier]
            columns = [c for c in numbers if c not in made]
            if made:
                print(f"Note: left out {_list_words(made)} (made by an earlier pattern word); "
                      "give columns= to use them.")
            if not columns:
                raise SimplydataError(f"{step}() needs columns of numbers, and this table has none.\n"
                                      f"For example, {example}")
        elif isinstance(columns, str):
            columns = [columns]
        elif not isinstance(columns, (list, tuple)) or not all(isinstance(c, str) for c in columns):
            raise SimplydataError(f"{step}() needs columns= as a list of column names in quotes, or nothing "
                                  f"to use every number column.\nFor example, {example}")
        columns = list(dict.fromkeys(columns))
        if len(columns) < at_least:
            raise SimplydataError(f"{step}() needs at least {at_least} columns of numbers; it got "
                                  f"{len(columns)}.\nFor example, {example}")
        self._number_frame(step, columns)
        return columns

    def _pattern_matrix(self, step, columns, extra=(), least_rows=3):
        """(numbers of the complete rows, which rows were kept); skipped rows get a note."""
        frame = self._number_frame(step, columns)
        for name in extra:
            if frame.schema[name].is_float():
                frame = frame.with_columns(nw.col(name).fill_nan(None))
        keep = np.ones(len(frame), dtype=bool)
        for name in [*columns, *extra]:
            keep &= ~np.asarray(frame[name].is_null().to_numpy(), dtype=bool)
        _skipped_note(int((~keep).sum()), [*columns, *extra])
        values = np.column_stack([frame[c].to_numpy().astype(float) for c in columns])[keep]
        if len(values) < least_rows:
            raise SimplydataError(f"{step}() needs at least {least_rows} rows without empty cells; "
                                  f"it found {len(values)}.")
        return values, keep

    @staticmethod
    def _scaled(x, columns, same_scale):
        centred = x - x.mean(axis=0)
        if not same_scale:
            return centred
        spread = x.std(axis=0, ddof=1)
        flat = [c for c, s in zip(columns, spread) if not s > 0]
        if flat:
            raise SimplydataError(
                f"{_quoted_list(flat)} has the same value in every row, so it cannot be put on the same scale "
                "as the others (its standard deviation is 0).\nLeave it out with columns=[...]."
            )
        return centred / spread

    def _with_new_columns(self, what, named_values, keep, dtype=nw.Float64):
        """Add columns (values for the kept rows, empty cells for the others) as one undoable step."""
        base = nw.maybe_reset_index(self._frame)
        rows = np.flatnonzero(keep)
        series = []
        for name, values in named_values:
            full = [None] * len(keep)
            for i, v in zip(rows, values):
                full[i] = int(v) if dtype == nw.Int64 else float(v)
            if dtype == nw.Int64 and not keep.all() and base.implementation.is_pandas():
                import pandas as pd  # whole numbers with empty cells need pandas' own "Int64"

                series.append(nw.from_native(pd.Series(full, name=name, dtype="Int64"), series_only=True))
            else:
                series.append(nw.new_series(name, full, dtype, backend=base.implementation))
        made = getattr(self, "_pattern_made", set()) | {name for name, _ in named_values}
        object.__setattr__(self, "_pattern_made", made)
        return self._change(what, base.with_columns(*series))

    @staticmethod
    def _check_measure(measure, x, columns):
        if measure not in ("bray-curtis", "jaccard"):
            return
        if (x < 0).any():
            bad = [c for c, has in zip(columns, (x < 0).any(axis=0)) if has]
            raise SimplydataError(
                f'measure="{measure}" is for counts or amounts, which cannot be below 0, but '
                f"{_quoted_list(bad)} has values below 0.\nUse measure=\"euclidean\" for values that can be negative."
            )
        empty = int(((x > 0).sum(axis=1) == 0).sum())
        if empty:
            raise SimplydataError(
                f'measure="{measure}" cannot compare a row with nothing in it (every value 0), and '
                f"{empty} row{'s are' if empty > 1 else ' is'} like that. "
                "Remove them first, for example with table.remove_rows(...)."
            )

    @staticmethod
    def _check_whole(step, option, value, low, high=None, example=""):
        if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < low or (
                high is not None and value > high):
            span = f"from {low} to {high}" if high is not None else f"{low} or more"
            raise SimplydataError(f"{step}() needs {option} as a whole number {span}, not {value!r}.\n"
                                  f"For example, {example}")

    def _pca(self, step, columns, same_scale, example):
        columns = self._pattern_columns(step, columns, example, at_least=2)
        x, keep = self._pattern_matrix(step, columns)
        z = self._scaled(x, columns, same_scale)
        from statsmodels.multivariate.pca import PCA

        found = PCA(z, ncomp=min(z.shape), standardize=False, demean=False, normalize=False, method="svd")
        sdev = np.sqrt(np.asarray(found.eigenvals, dtype=float) / (len(z) - 1))  # as R prcomp() sdev
        share = sdev ** 2 / (sdev ** 2).sum()
        rotation = np.asarray(found.loadings, dtype=float)
        # the sign of a component is arbitrary and differs between maths libraries (macOS, Linux,
        # Windows): turn each one so its biggest weight is positive, the same on every computer
        biggest = rotation[np.abs(rotation).argmax(axis=0), np.arange(rotation.shape[1])]
        rotation = rotation * np.where(biggest < 0, -1.0, 1.0)
        return columns, keep, sdev, share, rotation, z @ rotation

    # ------------------------------------------------------------------ principal components
    @friendly
    def add_principal_components(self, columns=None, how_many=2, same_scale=True):
        """Add principal components: a few new columns that hold most of the spread of many columns.

        table.add_principal_components(how_many=2)   (with sdata.example("meadow"))
        Principal component analysis turns many related columns into new columns PC1, PC2 ...
        that do not overlap: PC1 holds the most spread, PC2 the most of what is left, and so
        on. The new columns are the scores of each row. columns=None uses every number
        column; same_scale=True (the default, as R prcomp(scale. = TRUE)) first puts each
        column on the same scale (mean 0, standard deviation 1) so that big numbers do not
        dominate; same_scale=False keeps the columns as they are (use it when all columns are
        the same kind of measure on the same scale). Prints how much of the spread each
        component explains and the 3 columns with the largest weights in each. The sign of a
        component is arbitrary: flipping it changes nothing. Rows with an empty cell get
        empty PC cells. table.principal_components_of() gives all the weights as a table.
        Method: singular value decomposition (statsmodels PCA), as R prcomp().
        """
        step = "add_principal_components"
        example = 'with sdata.example("meadow"): table.add_principal_components(how_many=2)'
        columns, keep, sdev, share, rotation, scores = self._pca(step, columns, same_scale, example)
        most = len(sdev)
        self._check_whole(step, "how_many=", how_many, 1, most, example)
        cumulative = np.cumsum(share)
        names = [f"PC{i}" for i in range(1, how_many + 1)]
        scale_words = ("each put on the same scale first (mean 0, standard deviation 1)" if same_scale
                       else "as they are (not rescaled)")
        parts = [f"{n} {_pct(share[i])}" for i, n in enumerate(names)]
        together = f" ({_pct(cumulative[how_many - 1])} together)" if how_many > 1 else ""
        print(f"Principal components of {len(columns)} columns ({', '.join(map(str, columns))}), {scale_words}: "
              f"{_list_words(parts)} of the spread{together}.")
        for i, n in enumerate(names):
            top = np.argsort(-np.abs(rotation[:, i]), kind="stable")[:3]
            print(f"  {n} weighs most on " + _list_words(f'"{columns[j]}" ({rotation[j, i]:.2f})' for j in top) + ".")
        print(f"Method: principal component analysis by singular value decomposition, as R prcomp(scale. = "
              f"{'TRUE' if same_scale else 'FALSE'}). Added {_list_words(names)} (the scores of each row). "
              "The sign of each component is arbitrary: flipping it changes nothing.")
        if how_many < most:
            print(f"There are {most} components in all; table.principal_components_of() shows them all.")
        return self._with_new_columns(
            f"add principal components {', '.join(names)} of {', '.join(map(str, columns))}",
            [(n, scores[:, i]) for i, n in enumerate(names)], keep)

    @friendly
    def principal_components_of(self, columns=None, same_scale=True):
        """A table of the principal components: how much spread each explains and the weight of each column.

        table.principal_components_of()   (with sdata.example("meadow"))
        One row per component (PC1, PC2 ...) with its standard deviation, the share of the
        spread it explains, the cumulative share, and one column of weights per original
        column, "weight of hours" and so on (the loadings, R prcomp()$rotation). A large
        weight, plus or minus, means the column counts a lot in that component. The sign of a
        component is arbitrary. same_scale=True puts each column on the same scale first, as
        R prcomp(scale. = TRUE).
        """
        step = "principal_components_of"
        example = 'with sdata.example("meadow"): table.principal_components_of()'
        columns, _, sdev, share, rotation, _ = self._pca(step, columns, same_scale, example)
        cumulative = np.cumsum(share)
        data = {"component": [f"PC{i}" for i in range(1, len(sdev) + 1)],
                "standard deviation": [float(v) for v in sdev],
                "spread explained (%)": [float(v * 100) for v in share],
                "cumulative (%)": [float(v * 100) for v in cumulative]}
        for j, c in enumerate(columns):
            data[f"weight of {c}"] = [float(v) for v in rotation[j]]
        print(f"Principal components of {len(columns)} columns: PC1 explains {_pct(share[0])} of the spread, "
              f"PC2 {_pct(share[1])} ({_pct(cumulative[1])} together). Method: singular value decomposition, as "
              f"R prcomp(scale. = {'TRUE' if same_scale else 'FALSE'}). The sign of each component is arbitrary.")
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    # ------------------------------------------------------------------ clusters
    @friendly
    def add_clusters(self, columns=None, how_many=3, method="k-means", same_scale=True, seed=1, name="cluster",
                     linkage="ward"):
        """Sort the rows into groups of similar rows (clusters), in a new column.

        table.add_clusters(how_many=3)   (with sdata.example("meadow"))
        method="k-means" (the default) finds how_many clusters whose rows are as close as
        possible to their cluster's average, from 25 random starts (as R kmeans(nstart = 25));
        seed= makes the result the same every time. method="hierarchical" joins the closest
        rows step by step and cuts the tree into how_many clusters; linkage="ward" (the
        default, R hclust(method = "ward.D2")), "average", "complete" or "single".
        same_scale=True (the default) puts each column on the same scale first (R scale()).
        The clusters are numbered 1, 2, 3 in the order they first appear in the table. Prints
        the size of each cluster and the share of the spread that lies between clusters (R
        kmeans: between_SS / total_SS). Rows with an empty cell get an empty cluster cell.
        """
        step = "add_clusters"
        example = 'with sdata.example("meadow"): table.add_clusters(how_many=3)'
        self._check_choice(step, "method", method, CLUSTER_METHODS)
        if method == "hierarchical":
            self._check_choice(step, "linkage", linkage, list(LINKAGES))
        if not isinstance(name, str) or not name.strip():
            raise SimplydataError(f"{step}() needs name= as the new column's name in quotes.\nFor example, {example}")
        columns = self._pattern_columns(step, columns, example, leave_out=(name,))
        x, keep = self._pattern_matrix(step, columns)
        self._check_whole(step, "how_many=", how_many, 2, len(x) - 1, example)
        z = self._scaled(x, columns, same_scale)
        if method == "k-means":
            self._check_whole(step, "seed=", seed, 0, R_SEED_MAX, example)
            if len(np.unique(z, axis=0)) < how_many:
                raise SimplydataError(f"There are only {len(np.unique(z, axis=0))} different rows, so they cannot "
                                      f"make {how_many} clusters.")
            labels, between = _r_kmeans(z, how_many, seed)
            how = (f"k-means (Hartigan-Wong) with {KMEANS_STARTS} random starts, run in R: set.seed({seed}); "
                   f"kmeans(x, {how_many}, nstart = {KMEANS_STARTS})")
        else:
            from scipy.cluster.hierarchy import fcluster
            from scipy.cluster.hierarchy import linkage as make_tree

            labels = fcluster(make_tree(z, method=linkage, metric="euclidean"), how_many, criterion="maxclust")
            how = (f"hierarchical clustering on Euclidean distances with {linkage} linkage, as R "
                   f'hclust(dist(x), method = "{LINKAGES[linkage]}") and cutree(k = {how_many})')
        labels = _first_appearance(labels)
        found = int(labels.max())
        if method != "k-means":
            within, total = _sum_squares(z, labels)
            between = 1 - within / total if total > 0 else 0.0
        sizes = np.bincount(labels)[1:]
        scale_words = " (each put on the same scale first)" if same_scale else ""
        print(f"Made {found} clusters of {len(x)} rows from {len(columns)} columns{scale_words}: sizes "
              f"{_list_words(str(s) for s in sizes)} (clusters {_list_words(str(i) for i in range(1, found + 1))}, "
              f"numbered in the order they first appear). {_pct(between)} of the spread lies between the clusters "
              "(between-cluster / total sum of squares); the rest is within them.")
        if found < how_many:
            print(f"Note: the tree could only be cut into {found} clusters, not {how_many}, because of tied heights.")
        print(f'Method: {how}. Added the column "{name}".')
        return self._with_new_columns(f'add clusters "{name}" ({method}, {found}) of {", ".join(map(str, columns))}',
                                      [(name, labels)], keep, dtype=nw.Int64)

    # ------------------------------------------------------------------ distances
    def _labels(self, step, names, keep, example):
        if names is None:
            return "row", [str(i) for i in np.flatnonzero(keep) + 1]
        if not isinstance(names, str):
            raise SimplydataError(f"{step}() needs names= as one column name in quotes.\nFor example, {example}")
        self._need_columns(names)
        values = self._frame[names].to_list()
        labels = ["" if values[i] is None else str(values[i]) for i in np.flatnonzero(keep)]
        if len(set(labels)) < len(labels):
            twice = sorted({lab for lab in labels if labels.count(lab) > 1})[:3]
            raise SimplydataError(f'names= needs a different name in each row, but "{names}" has '
                                  f"{_quoted_list(twice)} more than once.")
        if names in labels:
            raise SimplydataError(f'names= cannot use "{names}": one of its rows is also called "{names}".')
        return names, labels

    @friendly
    def distances_between_rows(self, columns=None, measure="bray-curtis", names=None):
        """How different each row is from every other row: a square table of distances.

        table.distances_between_rows(names="plot")   (with sdata.example("meadow"))
        measure="bray-curtis" (the default, as R vegan::vegdist()) is the usual measure for
        counts of species: 0 when two rows have the same counts, 1 when they share nothing.
        "jaccard" uses only present / absent (a count above 0 is present), as
        vegan::vegdist(binary = TRUE): the share of the species found in either row that are
        found in only one. "euclidean" is the straight-line distance and "manhattan" the sum
        of the differences. names= is a column whose values label the rows and columns.
        """
        step = "distances_between_rows"
        example = 'with sdata.example("meadow"): table.distances_between_rows(names="plot")'
        self._check_choice(step, "measure", measure, list(MEASURES))
        columns = self._pattern_columns(step, columns, example,
                                        leave_out=(names,) if isinstance(names, str) else ())
        x, keep = self._pattern_matrix(step, columns, least_rows=2)
        self._check_measure(measure, x, columns)
        first, labels = self._labels(step, names, keep, example)
        square = _square(_distances(x, measure))
        data = {first: labels}
        for j, lab in enumerate(labels):
            data[lab] = [float(v) for v in square[:, j]]
        print(f"{MEASURES[measure]} distances between {len(x)} rows from {len(columns)} columns, as R vegan::"
              f"{MEASURE_R[measure]}. 0 means the same; the bigger, the more different.")
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    # ------------------------------------------------------------------ NMDS
    @friendly
    def add_nmds(self, columns=None, measure="bray-curtis", dimensions=2, tries=20, seed=1):
        """Draw the rows as points on a map where close points are similar rows (NMDS), in new columns.

        table.add_nmds()   (with sdata.example("meadow"))
        Non-metric multidimensional scaling puts each row on a map with dimensions= axes
        (NMDS1, NMDS2) so that the order of the distances on the map follows the order of
        the distances between the rows (measure="bray-curtis", as R vegan::metaMDS). It tries
        at least tries= random starts (seed= makes them the same every time), and more, up to
        100, until the best map has been found twice; it keeps the map with the lowest stress
        (Kruskal's stress-1: how badly the map fits). Clarke's (1993) rule of thumb: below 0.05
        excellent, below 0.1 good, below 0.2 usable, above 0.2 hard to trust. The axes have no units; their rotation and signs are
        arbitrary. Rows with an empty cell get empty NMDS cells.
        """
        step = "add_nmds"
        example = 'with sdata.example("meadow"): table.add_nmds()'
        self._check_choice(step, "measure", measure, list(MEASURES))
        self._check_whole(step, "dimensions=", dimensions, 1, 10, example)
        self._check_whole(step, "tries=", tries, 0, None, example)
        self._check_whole(step, "seed=", seed, 0, R_SEED_MAX, example)
        columns = self._pattern_columns(step, columns, example)
        x, keep = self._pattern_matrix(step, columns, least_rows=dimensions + 3)
        self._check_measure(measure, x, columns)
        delta = _distances(x, measure)
        if not (delta > 0).any():
            raise SimplydataError("Every row is the same in these columns, so there is nothing to draw.")
        points, stress, repeated = _r_nmds(x, measure, dimensions, tries, seed)
        first, most = _nmds_tries(tries)
        if stress < 0.05:
            reading = "excellent"
        elif stress < 0.1:
            reading = "good"
        elif stress < 0.2:
            reading = "usable, but do not read too much into small details"
        else:
            reading = f"hard to trust; try dimensions={dimensions + 1}"
        names = [f"NMDS{i}" for i in range(1, dimensions + 1)]
        print(f"NMDS map of {len(x)} rows from {len(columns)} columns ({MEASURES[measure]} distances, {dimensions} "
              f"dimensions): stress = {stress:.3f}, {reading} (Clarke's rule of thumb: below 0.05 excellent, below 0.1 "
              "good, below 0.2 usable, above 0.2 hard to trust).")
        print(f"Method: non-metric multidimensional scaling, run in R: set.seed({seed}); vegan::metaMDS("
              f"vegdist(x, {R_DISTANCE[measure]}), k = {dimensions}, try = {first}, trymax = {most}, "
              f"autotransform = FALSE) (Kruskal's stress-1). Added {_list_words(names)}; the axes have no units and "
              "their rotation and signs are arbitrary.")
        if not repeated:
            print('Note: the best map was found only once (R: "Best solution was not repeated"), so a better map '
                  f"may exist even after {most} starts.")
        return self._with_new_columns(f"add NMDS {', '.join(names)} of {', '.join(map(str, columns))} ({measure})",
                                      [(n, points[:, i]) for i, n in enumerate(names)], keep)

    # ------------------------------------------------------------------ PERMANOVA
    @friendly
    def compare_profiles(self, columns=None, for_each=None, measure="bray-curtis", permutations=999, seed=1):
        """Do the groups differ in their make-up across many columns (PERMANOVA), or could it be chance?

        table.compare_profiles(for_each="grazed")   (with sdata.example("meadow"))
        Compares whole profiles, such as the counts of all plant species in a plot, between
        the groups in for_each=. PERMANOVA, as R vegan::adonis2(distances ~ group): R squared
        is the share of the differences between rows (measure= distances, Bray-Curtis by
        default) that the groups explain, and pseudo-F compares the differences between
        groups with those within groups. The p-value comes from shuffling the rows
        permutations= times (seed= makes it the same every time). It also checks whether the
        groups differ in spread (vegan::betadisper and permutest), because PERMANOVA can then
        mistake a difference in spread for a difference in make-up. Gives back a one-row table.
        """
        step = "compare_profiles"
        example = 'with sdata.example("meadow"): table.compare_profiles(for_each="grazed")'
        self._check_choice(step, "measure", measure, list(MEASURES))
        self._need_name(step, "for_each=", for_each, example)
        self._need_columns(for_each)
        self._check_whole(step, "permutations=", permutations, 1, None, example)
        self._check_whole(step, "seed=", seed, 0, R_SEED_MAX, example)
        columns = self._pattern_columns(step, columns, example, leave_out=(for_each,))
        if for_each in columns:
            raise SimplydataError(f'"{for_each}" cannot be both a column to compare and the for_each= column.\n'
                                  f"For example, {example}")
        x, keep = self._pattern_matrix(step, columns, extra=(for_each,), least_rows=3)
        self._check_measure(measure, x, columns)
        every = self._frame[for_each].to_list()
        keys = [every[i] for i in np.flatnonzero(keep)]
        order = sorted(set(keys), key=lambda k: (str(type(k)), k))
        a = len(order)
        if a < 2:
            raise SimplydataError(f'{step}() needs at least 2 groups in "{for_each}"; it found {a}.')
        codes = np.array([order.index(k) for k in keys])
        sizes = np.bincount(codes, minlength=a)
        group_names = [str(k) for k in order]
        if (sizes < 2).any():
            small = [g for g, s in zip(group_names, sizes) if s < 2]
            raise SimplydataError(f"{step}() needs at least 2 rows in each group; "
                                  f'{_quoted_list(small)} in "{for_each}" has fewer.')
        n = len(x)
        if n <= a:
            raise SimplydataError(f"{step}() needs more rows than groups.")
        result = _r_permanova(x, measure, np.array(group_names, dtype=object)[codes], permutations, seed)
        f, r2, p = result["f"], result["r2"], result["p"]
        spread_f, spread_p, z = result["spread_f"], result["spread_p"], result["distances"]
        spreads = [float(z[codes == g].mean()) for g in range(a)]
        groups_text = ", ".join(group_names)
        what = (f'the make-up of {len(columns)} columns ({", ".join(map(str, columns))}) in each "{for_each}" '
                f"({groups_text})")
        print(f'The groups of "{for_each}" ({groups_text}) explain {_pct(r2)} of the differences between the rows '
              f"(R squared = {_num(r2)}; {MEASURES[measure]} distances over {len(columns)} columns; pseudo-F = "
              f"{_num(f)}, from {permutations} permutations).")
        print(_p_sentence(p, "the groups truly had the same make-up", "a difference in make-up this big or bigger",
                          "that the groups have the same make-up"))
        print(f"Test: PERMANOVA (permutational analysis of variance on distances), run in R: set.seed({seed}); "
              f"vegan::adonis2(distances ~ {for_each}, permutations = {permutations}) with distances = "
              f"vegan::{MEASURE_R[measure]}.")
        print("Spread check: the average distance to the group centre is "
              f"{_list_words(f'{_num(s)} in {g}' for g, s in zip(group_names, spreads))} (as vegan::betadisper and "
              f"permutest: F = {_num(spread_f)}, {_p_shown(spread_p)}).")
        if spread_p < 0.05:
            print("Note: the groups differ in spread, and PERMANOVA can then mistake a difference in spread for a "
                  "difference in make-up. Look at a picture (table.add_nmds()) before reading the result.")
        row = {"test": "PERMANOVA", "what it compares": what, "distance": MEASURES[measure],
               "statistic name": "pseudo-F", "statistic": float(f), "degrees of freedom 1": float(a - 1),
               "degrees of freedom 2": float(n - a), "R squared": float(r2), "p-value": float(p),
               "permutations": int(permutations), "spread check F": float(spread_f),
               "spread check p-value": float(spread_p)}
        for g, s, size in zip(group_names, spreads, sizes):
            row[f"count in {g}"] = int(size)
            row[f"distance to centre in {g}"] = s
        return self._result_table(row)
