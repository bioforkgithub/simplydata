"""Charts for communities and resistomes (S3c-1): richness curves and the cluster tree.

* draw_richness_curves(columns=[...]): one curve per row, the expected richness (kinds present) against the total
  count, from R vegan::rarecurve(tidy = TRUE) (the numbers of vegan::rarefy at steps of the total), drawn with
  matplotlib. A dotted line marks the smallest row total: richness can be compared at or below it
  (table.add_diversity_columns(at_total_count=)).
* draw_cluster_tree(columns=[...]): the tree of hierarchical clustering (a dendrogram), SciPy
  cluster.hierarchy.linkage and dendrogram(no_plot=True) for the links, drawn with matplotlib. The measure and the
  linkage follow table.add_clusters(test_method="hierarchical"): "ward" for straight-line distances, "average" for the
  others, so the tree matches the clusters. The cophenetic correlation (SciPy cophenet, as R
  cor(cophenetic(h), d)) says how well the tree keeps the distances.
"""

from __future__ import annotations

from .._typing import _Same

import numpy as np
import pandas as pd

from .._errors import SimplydataError, friendly
from ._helpers import check, colour_role, default_colour, palette_for
from .charts import _remember

STEPS_PER_ROW = 50  # at least about 50 points on the shortest richness curve (vegan rarecurve's step)
MANY_ROWS = 50  # above this, thin lines and a note
X_LABEL = "Total count (reads, individuals)"
Y_LABEL = "Expected kinds present (richness)"


def _count_matrix(word, data, columns):
    if isinstance(columns, str):
        columns = [columns]
    if not isinstance(columns, (list, tuple)) or not columns or not all(isinstance(c, str) for c in columns):
        numbers = [c for c in data.columns if pd.api.types.is_numeric_dtype(data[c])]
        ready = "[" + ", ".join(f'"{c}"' for c in numbers) + "]"
        raise SimplydataError(
            f".{word}() needs columns=: the columns that hold the counts of each kind (species, genes ...). "
            "simplydata does not take every number column here, because temperature or the read total would be "
            f"counted as a kind.\nThe number columns are {ready}; copy the ones that are counts:\n"
            f'  chart.{word}(columns=["blaTEM", "blaCTXM", "sul1"])')
    missing = [c for c in columns if c not in data.columns]
    if missing:
        check(data, x=missing[0])
    text = [c for c in columns if not pd.api.types.is_numeric_dtype(data[c])]
    if text:
        raise SimplydataError(f'.{word}() needs columns of counts; "{text[0]}" holds text.')
    return list(dict.fromkeys(columns))


def _counts(data, columns):
    frame = data[columns].apply(pd.to_numeric, errors="coerce")
    keep = ~frame.isna().any(axis=1)
    return frame[keep].to_numpy(dtype=float), keep.to_numpy()


# ---------------------------------------------------------------- draw_richness_curves
def _draw_richness(ctx, columns, names, colour, thin):
    from ..table.community_r import richness_curves

    ax = ctx.ax
    x, keep = _counts(ctx.data, columns)
    rows = ctx.data[keep]
    totals = x.sum(axis=1)
    used = totals > 0
    x, rows, totals = x[used], rows[used], totals[used]
    step = max(1, int(totals.min() // STEPS_PER_ROW))
    curves = richness_curves(x, step)
    group, fixed = colour_role(ctx.data, colour)
    if group is not None:
        names_g = list(pd.unique(ctx.data[group].dropna()))
        colours = dict(zip(names_g, palette_for(pd.DataFrame({group: names_g}), group, ctx.settings)))
    shown = set()
    for i in range(len(x)):
        mine = curves["row"] == i + 1
        if group is not None:
            g = rows[group].iloc[i]
            c = colours.get(g, default_colour(ctx.settings))
            label = None if g in shown else str(g)
            shown.add(g)
        else:
            c, label = default_colour(ctx.settings, fixed), None
        ax.plot(curves["at"][mine], curves["richness"][mine], color=c, label=label,
                linewidth=0.6 if thin else 1.2)
        if names is not None:
            ax.annotate(str(rows[names].iloc[i]), (curves["at"][mine][-1], curves["richness"][mine][-1]),
                        fontsize=7, xytext=(2, 0), textcoords="offset points")
    ax.axvline(float(totals.min()), color="grey", linestyle=":", linewidth=1)
    if ax.get_xlabel() == "":
        ax.set_xlabel(X_LABEL)
    if ax.get_ylabel() == "":
        ax.set_ylabel(Y_LABEL)
    if group is not None:
        ax.legend(title=group)
    _remember(ctx, "draw_richness_curves", rows, {"x": None, "y": None, "colour": group})


# ---------------------------------------------------------------- draw_cluster_tree
def _draw_tree(ctx, tree, labels, colour):
    from scipy.cluster import hierarchy

    ax = ctx.ax
    found = hierarchy.dendrogram(tree, labels=labels, no_plot=True)
    c = default_colour(ctx.settings, colour)
    for xs, ys in zip(found["icoord"], found["dcoord"]):
        ax.plot(xs, ys, color=c, linewidth=1.2)
    ax.set_xticks(np.arange(5, 10 * len(labels), 10))
    ax.set_xticklabels(found["ivl"], rotation=90)
    ax.set_xlim(0, 10 * len(labels))
    if ax.get_ylabel() == "":
        ax.set_ylabel("Distance at which the groups join")
    _remember(ctx, "draw_cluster_tree", ctx.data, {"x": None, "y": None, "colour": None})


class CommunityChartWords:
    @friendly
    def draw_richness_curves(self: _Same, columns=None, names=None, colour=None) -> _Same:
        """Richness curves: how many kinds each row would show at each total count (rarefaction curves).

        chart.draw_richness_curves(columns=["blaTEM", "blaCTXM", "sul1", "sul2", "tetA", "tetM"], colour="site")   (with sdata.get_example("resistome"))
        One curve per row: the expected number of kinds present (richness) in a sample of each
        size, drawn up to the row's own total (R vegan::rarecurve, the expected values of
        vegan::rarefy). Curves that still climb at their end would find more kinds with more
        counts. The dotted line marks the smallest row total: compare richness at or below it
        (table.add_diversity_columns(at_total_count=...)). columns= is required and must hold raw
        counts (whole numbers). colour="site" gives each group its own colour; names= writes each
        row's name at the end of its curve. Needs R (vegan).
        """
        word = "draw_richness_curves"
        data = self._data
        columns = _count_matrix(word, data, columns)
        if names is not None:
            if not isinstance(names, str):
                raise SimplydataError(f".{word}() needs names= as one column name in quotes.")
            check(data, x=names)
        group, _ = colour_role(data, colour)
        if group is not None:
            if not isinstance(group, str):
                raise SimplydataError(f".{word}() needs colour= as one column name or a colour.")
            check(data, x=group)
        x, keep = _counts(data, columns)
        if not len(x):
            raise SimplydataError(f".{word}() found no rows with all of these columns filled in.")
        if (x < 0).any():
            raise SimplydataError(f".{word}() needs counts, which cannot be below 0.")
        finite = x[np.isfinite(x)]
        if not np.all(finite == np.round(finite)):
            raise SimplydataError(f".{word}() needs raw counts (whole numbers); these look normalised (per 16S, per "
                                  "million reads?). Rarefaction draws counts, so it cannot run on shares.")
        totals = x.sum(axis=1)
        if not (totals > 0).any():
            raise SimplydataError(f".{word}() found nothing above 0 in these columns.")
        from .._r import need_r

        need_r(("vegan",), "Richness curves (R vegan::rarecurve())")
        thin = len(x) > MANY_ROWS
        print(f"Richness curves of {len(x)} rows from {len(columns)} columns: the expected number of kinds present at "
              f"each total count (R vegan::rarecurve, the expected values of vegan::rarefy). The dotted line marks the "
              f"smallest total, {totals[totals > 0].min():,.0f}: compare richness at or below it "
              f"(table.add_diversity_columns(at_total_count={int(totals[totals > 0].min())})). Curves that still "
              "climb at their end would find more kinds with more counts.")
        if thin:
            print(f"Note: {len(x)} curves are drawn as thin lines; draw fewer rows to see each one.")
        if (totals == 0).any():
            print(f"Note: {int((totals == 0).sum())} rows with nothing in them are left out.")
        if not keep.all():
            print(f"Note: {int((~keep).sum())} rows with an empty cell in these columns are left out.")
        self._need_axes(word)
        return self._add("richness_curves", "draw", _draw_richness, columns=columns, names=names, colour=colour,
                         thin=thin)

    @friendly
    def draw_cluster_tree(self: _Same, columns=None, measure=None, linkage=None, same_scale=True, names=None, colour=None) -> _Same:
        """The cluster tree (a dendrogram): which rows join first, and at what distance.

        chart.draw_cluster_tree(columns=["blaTEM", "blaCTXM", "sul1", "sul2", "tetA", "tetM"], measure="bray-curtis", names="sample")
        (with sdata.get_example("resistome"))
        Hierarchical clustering joins the two closest rows (or groups of rows) step by step; the
        tree shows each join at the height of its distance. measure= takes the measures of
        table.find_distances_between_rows ("bray-curtis", "aitchison" ...); without it the
        distances are straight-line ones, with each column on the same scale first
        (same_scale=True). The linkage follows table.add_clusters: "ward" for straight-line
        distances and "average" for the others (Ward is refused with Bray-Curtis), so the tree
        matches the clusters; linkage= chooses "average", "complete", "single" or "ward". names=
        labels the leaves. Prints the cophenetic correlation: how well the heights of the tree keep
        the distances (1 = exactly). SciPy (cluster.hierarchy); measure="aitchison", "robust
        aitchison" and "hellinger" need R (vegan).
        """
        from ..table import patterns
        from ..table._compositions import whole_numbers

        word = "draw_cluster_tree"
        data = self._data
        if columns is None:
            columns = [c for c in data.columns if pd.api.types.is_numeric_dtype(data[c]) and c != names]
            if not columns:
                raise SimplydataError(f".{word}() needs columns of numbers.")
            print(f"Note: columns=None uses every number column: {', '.join(map(str, columns))}.")
        else:
            columns = _count_matrix(word, data, columns)
        if measure is not None:
            self._check_choice(word, "measure", measure, list(patterns.MEASURES))
        straight = (measure or "euclidean") in patterns.STRAIGHT
        chosen = linkage if linkage is not None else ("ward" if straight else "average")
        self._check_choice(word, "linkage", chosen, list(patterns.LINKAGES))
        if chosen == "ward" and not straight:
            raise SimplydataError(f'linkage="ward" assumes straight-line (Euclidean) distances, and '
                                  f'{patterns.MEASURES[measure]} distances are not. Use linkage="average":\n'
                                  f'  chart.draw_cluster_tree(columns=[...], measure="{measure}", linkage="average")')
        if names is not None:
            if not isinstance(names, str):
                raise SimplydataError(f".{word}() needs names= as one column name in quotes.")
            check(data, x=names)
        x, keep = _counts(data, columns)
        if len(x) < 3:
            raise SimplydataError(f".{word}() needs at least 3 rows without empty cells.")
        labels = ([str(v) for v in data[names][keep]] if names is not None
                  else [str(i + 1) for i in np.flatnonzero(keep)])
        from scipy.cluster.hierarchy import cophenet
        from scipy.cluster.hierarchy import linkage as make_tree
        from scipy.spatial.distance import pdist

        plain = measure in (None, "euclidean")
        if plain:
            z = patterns.PatternWords._scaled(x, columns, same_scale)
            d = pdist(z, "euclidean")
        else:
            patterns.PatternWords._check_measure(measure, x, columns, word)
            d = patterns._distances(x, measure)
        tree = make_tree(d, method=chosen)
        r, _ = cophenet(tree, d)
        name = patterns.MEASURES[measure or "euclidean"]
        print(f"Cluster tree of {len(x)} rows from {len(columns)} columns: {name} distances"
              f"{' (each column on the same scale first)' if plain and same_scale else ''}, {chosen} linkage. "
              f"Cophenetic correlation {r:.2f}: how well the heights of the tree keep the distances (1 = exactly).")
        if linkage is None:
            print(f'simplydata chooses linkage="{chosen}" for {name} distances (the same as table.add_clusters).')
        if measure == "bray-curtis" and whole_numbers(x):
            patterns._depth_note(measure, x)
        self._need_axes(word)
        return self._add("cluster_tree", "draw", _draw_tree, tree=tree, labels=labels, colour=colour)
