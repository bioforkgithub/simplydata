"""Communities and resistomes (S3c-1): diversity, log ratios, principal coordinates, constrained ordination,
correlation between two sets of profiles, discriminant axes and correspondence axes.

A community table holds the counts of many kinds (species, genes, ASVs) in each sample, often beside a few
columns that describe the samples (site, temperature, salinity, reads). The words here read such a table:

* add_diversity_columns: R vegan specnumber() (richness), diversity() (Shannon with the natural log, Simpson as
  1 - D, inverse Simpson), renyi(hill = TRUE) (Hill numbers: the effective number of equally common kinds),
  estimateR() (bias-corrected Chao1) and rarefy() (the expected richness at a total count, Hurlbert 1971).
* add_log_ratio_columns: zeros replaced by estimated small values (R zCompositions::cmultRepl(method = "GBM",
  z.delete = FALSE)), then R compositions::clr(), alr() or ilr(); "adding 1" is vegan::decostand(pseudocount = 1).
* add_principal_coordinates: R stats::cmdscale(eig = TRUE) on vegan::vegdist() distances (PCoA).
* explain_profiles_of: R vegan dbrda() (distance-based RDA, the default on Bray-Curtis), rda() (Hellinger or
  Aitchison) or cca(); RsquareAdj(); anova(); anova(by = "margin"): each column tested after all the others.
* find_correlation_between_profiles: R vegan::mantel() (Pearson) or vegan::protest() (Procrustes).
* add_axes_that_separate_groups: R MASS::lda(), predict()$x and lda(CV = TRUE).
* add_correspondence_axes: CA with R vegan::cca(x) for counts; MCA with R ca::mjca(lambda = "adjusted") for
  text columns.

columns= is required on the words that read counts (add_diversity_columns, add_log_ratio_columns,
explain_profiles_of), so that temperature or read totals are never counted as a kind (independent review 5.1).
Every word needs R (simplydata[r]); the R calls are in community_r.py. simplydata computes no statistic itself.
"""

from __future__ import annotations

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, friendly
from . import _compositions as comp
from .patterns import (MEASURE_R, MEASURES, R_SEED_MAX, _columns_used, _depth_note, _pct, _permutation_p_sentence,
                       _quoted_list)
from .stat_tests import _list_words, _num, _p_sentence

DIVERSITY_SHOW = ("richness", "shannon", "simpson", "inverse simpson", "chao1", "hill numbers")
DIVERSITY_DEFAULT = ("richness", "shannon", "simpson")
LOG_RATIO_METHODS = {"clr": "clr", "centred log ratio": "clr", "centered log ratio": "clr", "alr": "alr",
                     "additive log ratio": "alr", "ilr": "ilr", "isometric log ratio": "ilr"}
CANONICAL = {"canonical correspondence": "cca", "cca": "cca", "canonical correspondence analysis": "cca"}
STRAIGHT_RDA = ("euclidean", "hellinger", "aitchison")
CORRELATION_METHODS = ("mantel", "procrustes")
COUNT_MEASURES = ("bray-curtis", "jaccard", "aitchison", "robust aitchison", "hellinger")
SCALED = "scaled euclidean"


def _flip(scores):
    """Turn each axis so its biggest value is positive: the sign of an axis is arbitrary, and this gives the same
    answer on every computer (as add_principal_components does)."""
    if not scores.size:
        return scores
    biggest = scores[np.abs(scores).argmax(axis=0), np.arange(scores.shape[1])]
    return scores * np.where(biggest < 0, -1.0, 1.0)


def _clean_term(term):
    return str(term).strip("`")


class CommunityWords:
    # ------------------------------------------------------------------ helpers
    def _required_columns(self, step, columns, example, at_least=2):
        """columns= must be given on the community words: every number column would count temperature or read
        totals as a kind, and nothing would fail."""
        if columns is None:
            numbers = [c for c, d in self._frame.schema.items() if d.is_numeric()]
            ready = "[" + ", ".join(f'"{c}"' for c in numbers) + "]"
            raise SimplydataError(
                f"{step}() needs columns=: the columns that hold the counts of each kind (species, genes ...). "
                "simplydata does not take every number column here, because a column such as temperature or the "
                "read total would then be counted as a kind, and nothing would fail.\n"
                f"The number columns of this table are {ready}; copy the ones that are counts:\n"
                f"  {example}")
        return self._pattern_columns(step, columns, example, at_least=at_least)

    def _row_labels(self, names, keep):
        if isinstance(names, str):
            self._need_columns(names)
            values = self._frame[names].to_list()
            return [str(values[i]) for i in np.flatnonzero(keep)]
        return [f"row {i + 1}" for i in np.flatnonzero(keep)]

    @staticmethod
    def _name_list(step, option, value, example):
        if isinstance(value, str):
            return [value]
        if isinstance(value, (list, tuple)) and value and all(isinstance(v, str) for v in value):
            return list(dict.fromkeys(value))
        raise SimplydataError(f"{step}() needs {option} as a column name in quotes, or a list of them.\n"
                              f"For example, {example}")

    @staticmethod
    def _check_seed_and_permutations(step, permutations, with_seed, example):
        for option, value, low, high in (("permutations=", permutations, 1, None),
                                         ("with_seed=", with_seed, 0, R_SEED_MAX)):
            if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < low or (
                    high is not None and value > high):
                raise SimplydataError(f"{step}() needs {option} as a whole number from {low}, not {value!r}.\n"
                                      f"For example, {example}")

    # ------------------------------------------------------------------ diversity
    @friendly
    def add_diversity_columns(self, columns=None, show=None, at_total_count=None, names=None):
        """Add diversity columns: how many kinds each row holds, and how evenly (richness, Shannon, Simpson).

        table.add_diversity_columns(columns=["blaTEM", "blaCTXM", "sul1", "sul2", "tetA", "tetM"])   (with sdata.get_example("resistome"))
        Each row is a sample and columns= the counts of each kind in it (species, genes). show= chooses:
        "richness" (the number of kinds present), "shannon" (Shannon diversity, natural log),
        "simpson" (1 - the sum of squared shares: the chance that two counts drawn at random are of
        different kinds), "inverse simpson", "chao1" (the bias-corrected estimate of how many kinds
        there would be if sampling went on, with its standard error) and "hill numbers" (q = 0, 1, 2:
        diversity as a number of equally common kinds). The default is richness, Shannon and
        Simpson. at_total_count=1000 adds the expected richness in a sample of 1000 counts
        (rarefaction: the expected value, not a random subsample), so rows sequenced to different
        depths can be compared. columns= is required, so that temperature or read totals are never
        counted as kinds. Chao1 and at_total_count= need raw counts (whole numbers); richness,
        Shannon and Simpson work on normalised values too. names= labels the rows in notes. A row
        with nothing in it gets empty cells. Needs R (vegan). Then compare the new columns between
        groups with table.compare_averages_of.
        """
        step = "add_diversity_columns"
        example = 'table.add_diversity_columns(columns=["blaTEM", "blaCTXM", "sul1", "tetM"])'
        if show is None:
            wanted = list(DIVERSITY_DEFAULT)
        else:
            wanted = [show] if isinstance(show, str) else show
            if not isinstance(wanted, (list, tuple)) or not wanted:
                raise SimplydataError(f'{step}() needs show= as one name in quotes or a list, such as '
                                      'show=["richness", "shannon"].')
            for w in wanted:
                self._check_choice(step, "show", w, DIVERSITY_SHOW)
            wanted = list(dict.fromkeys(wanted))
        if at_total_count is not None and (isinstance(at_total_count, bool) or
                                           not isinstance(at_total_count, (int, np.integer)) or at_total_count < 1):
            raise SimplydataError(f"{step}() needs at_total_count= as a whole number of counts, such as "
                                  f"at_total_count=1000, not {at_total_count!r}.")
        columns = self._required_columns(step, columns, example, at_least=1)
        if isinstance(names, str) and names in columns:
            raise SimplydataError(f'"{names}" cannot be both a column to count and names=.')
        x, keep = self._pattern_matrix(step, columns, least_rows=2)
        comp.check_not_negative(step, x, columns, "")
        whole = comp.whole_numbers(x)
        if not whole and ("chao1" in wanted or at_total_count):
            needs = _list_words([w for w in ("Chao1" if "chao1" in wanted else "",
                                              "at_total_count=" if at_total_count else "") if w])
            raise SimplydataError(
                f"{needs} need{'s' if ' and ' not in needs else ''} raw counts (whole numbers), and these columns "
                "hold numbers that are not whole: they look normalised (per 16S, per million reads?). Chao1 leans on "
                "the kinds seen once or twice, and rarefaction on drawing counts. Richness, Shannon and Simpson still "
                f'work:\n  table.add_diversity_columns(columns=[...], show=["richness", "shannon", "simpson"])')
        labels = self._row_labels(names, keep)
        filled = (x > 0).sum(axis=1) > 0
        if at_total_count and not (x.sum(axis=1) >= at_total_count).any():
            raise SimplydataError(f"at_total_count={at_total_count} is above every row's total count (the largest is "
                                  f"{x.sum(axis=1).max():,.0f}), so no row can be compared there. Use a total at or "
                                  f"below the smallest row total, {x[filled].sum(axis=1).min():,.0f}.")
        if not filled.any():
            raise SimplydataError(f"{step}() found nothing above 0 in any row of these columns.")
        used = x[filled]
        from .community_r import diversity

        found = diversity(used, at_total_count, chao="chao1" in wanted)
        new = []

        def column(name, values):
            full = np.full(len(x), np.nan)
            full[filled] = values
            new.append((name, full))

        lines = []
        avg = lambda v: float(np.nanmean(v))  # noqa: E731 - the average of a new column, for the printout
        hill = found["hill"]
        for w in wanted:
            if w == "richness":
                column("richness", found["richness"])
                lines.append(f"Richness (the number of kinds present) averages {avg(found['richness']):.1f} "
                             f"(from {np.min(found['richness']):.0f} to {np.max(found['richness']):.0f}).")
            elif w == "shannon":
                column("shannon", found["shannon"])
                lines.append(f"Shannon diversity averages {avg(found['shannon']):.2f} (natural log): as diverse as a "
                             f"sample of {avg(hill[:, 1]):.1f} equally common kinds, on average (its effective number, "
                             "Hill number q = 1).")
            elif w == "simpson":
                column("simpson", found["simpson"])
                lines.append(f"Simpson's index averages {avg(found['simpson']):.2f}: the chance that two counts drawn "
                             "at random are of different kinds (1 - the sum of squared shares); as diverse as "
                             f"{avg(found['invsimpson']):.1f} equally common kinds (inverse Simpson, Hill number q = 2).")
            elif w == "inverse simpson":
                column("inverse simpson", found["invsimpson"])
                lines.append(f"Inverse Simpson averages {avg(found['invsimpson']):.1f}: as diverse as that many equally "
                             "common kinds (Hill number q = 2, which weighs the common kinds most).")
            elif w == "chao1":
                chao = found["chao"]
                column("chao1", chao[1])
                column("chao1 standard error", chao[2])
                lines.append(f"Chao1 averages {avg(chao[1]):.1f} kinds: the number there would be if sampling went on "
                             "(bias-corrected; it leans on the kinds seen once or twice), against "
                             f"{avg(chao[0]):.1f} seen.")
            elif w == "hill numbers":
                for q in range(3):
                    column(f"hill number {q}", hill[:, q])
                lines.append(f"Hill numbers average {avg(hill[:, 0]):.1f} (q = 0, richness), {avg(hill[:, 1]):.1f} "
                             f"(q = 1, from Shannon) and {avg(hill[:, 2]):.1f} (q = 2, from Simpson): each is a number "
                             "of equally common kinds, so they can be compared directly.")
        totals = used.sum(axis=1)
        short = []
        if at_total_count:
            rare = found["rarefied"].copy()
            used_labels = [lab for lab, f in zip(labels, filled) if f]
            short = [lab for lab, t in zip(used_labels, totals) if t < at_total_count]
            rare[totals < at_total_count] = np.nan
            name = f"expected richness at {at_total_count}"
            column(name, rare)
            lines.append(f"Expected richness in a sample of {at_total_count:,} counts averages {avg(rare):.1f} "
                         "(rarefaction: the expected value, Hurlbert 1971; not a random subsample).")
        print(f"Diversity of {int(filled.sum())} rows from {_columns_used(columns)}:")
        for line in lines:
            print("  " + line)
        if short:
            print(f"Note: {len(short)} row{'s have' if len(short) > 1 else ' has'} fewer than {at_total_count:,} counts "
                  f"in all ({', '.join(short[:6])}{' ...' if len(short) > 6 else ''}), so "
                  f"{'their' if len(short) > 1 else 'its'} expected richness at that total is left empty.")
        if not filled.all():
            empty = [lab for lab, f in zip(labels, filled) if not f]
            print(f"Note: {len(empty)} row{'s have' if len(empty) > 1 else ' has'} nothing above 0 in these columns "
                  f"({', '.join(empty[:6])}); {'they get' if len(empty) > 1 else 'it gets'} empty cells.")
        if not whole:
            print("Note: these numbers are not whole (normalised values?). Richness still counts the kinds present, "
                  "but it depends on how deeply each sample was sequenced; Chao1 and at_total_count= need raw counts.")
        elif not at_total_count and {"richness", "chao1", "hill numbers"} & set(wanted) and \
                totals.max() > 2 * totals.min():
            print(f"Note: richness depends on how many counts each row has (from {totals.min():,.0f} to "
                  f"{totals.max():,.0f} here); compare richness at the same total count: "
                  f"at_total_count={int(totals.min())}.")
        calls = ["specnumber(x)" if "richness" in wanted else "",
                 'diversity(x, "shannon")' if "shannon" in wanted else "",
                 'diversity(x, "simpson")' if "simpson" in wanted else "",
                 'diversity(x, "invsimpson")' if "inverse simpson" in wanted else "",
                 "estimateR(x)" if "chao1" in wanted else "",
                 "renyi(x, scales = c(0, 1, 2), hill = TRUE)" if {"shannon", "simpson", "hill numbers"} & set(wanted) else "",
                 f"rarefy(x, sample = {at_total_count})" if at_total_count else ""]
        print("Method: R vegan::" + ", ".join(c for c in calls if c) + ". simplydata chooses the natural log for "
              "Shannon, Simpson as 1 - D (the Gini-Simpson index), Chao1 bias-corrected and rarefaction as an "
              f"expected value. Added {_list_words(n for n, _ in new)}.")
        return self._with_new_columns(f"add diversity columns of {', '.join(map(str, columns))}", new, keep)

    # ------------------------------------------------------------------ log ratios
    @friendly(renamed={"method": "test_method"})
    def add_log_ratio_columns(self, columns=None, test_method="clr", zeros_replaced_by="estimated small values",
                              against=None):
        """Add log ratio columns: counts that are parts of a whole, turned into logs of ratios (clr, alr, ilr).

        table.add_log_ratio_columns(columns=["blaTEM", "blaCTXM", "sul1", "sul2", "tetA", "tetM"])   (with sdata.get_example("resistome"))
        Resistome and microbiome counts are compositional: each row's total is set by how deeply the
        sample was sequenced, so raw counts and percentages give false correlations. Log ratios
        fix this (Aitchison 1986; Gloor et al. 2017). test_method="clr" (the default, the centred log
        ratio) adds clr_<column>: the log of each value over the row's geometric mean (above 0:
        more than the row's typical kind). test_method="alr" with against="16S" adds alr_<column>: the
        log of each column over the one named in against= (the reference). test_method="ilr" adds
        ilr1, ilr2 ...: isometric log ratios on the default basis of R compositions::ilr().
        Logs need values above 0, so zeros are first replaced: zeros_replaced_by="estimated small
        values" (the default; "multiplicative" accepted) is R zCompositions::cmultRepl(method =
        "GBM"), which estimates each from the data and needs raw counts; no column is deleted (a
        column with fewer than 2 values above 0 is refused, with the line that merges rare
        columns). zeros_replaced_by="adding 1" adds 1 to every count (vegan::decostand(pseudocount =
        1)): the answer then depends on the 1. columns= is required. The original columns are
        kept. Needs R (zCompositions, compositions).
        """
        step = "add_log_ratio_columns"
        example = 'table.add_log_ratio_columns(columns=["blaTEM", "blaCTXM", "sul1", "tetM"])'
        if not isinstance(test_method, str) or test_method.strip().lower() not in LOG_RATIO_METHODS:
            self._check_choice(step, "test_method", test_method, ["clr", "alr", "ilr"])
        kind = LOG_RATIO_METHODS[test_method.strip().lower()]
        how = comp.ZERO_WAYS.get(zeros_replaced_by.strip().lower() if isinstance(zeros_replaced_by, str) else None)
        if how is None:
            self._check_choice(step, "zeros_replaced_by", zeros_replaced_by, [comp.ESTIMATED, comp.ADDING_ONE])
        columns = self._required_columns(step, columns, example, at_least=2)
        if kind == "alr":
            if not isinstance(against, str) or against not in columns:
                raise SimplydataError(f'test_method="alr" needs against= as the name of one of the columns, the reference '
                                      'that every other column is divided by:\n'
                                      f'  table.add_log_ratio_columns(columns=[...], test_method="alr", against="{columns[-1]}")')
        elif against is not None:
            raise SimplydataError(f'against= names the reference of test_method="alr"; test_method="{kind}" has none. Leave '
                                  "against= out, or use test_method=\"alr\".")
        x, keep = self._pattern_matrix(step, columns, least_rows=1)
        zeros = comp.check_zeros(step, x, columns, how, "", measure_hint=False)
        if zeros and how == comp.ADDING_ONE and kind == "ilr":
            raise SimplydataError('test_method="ilr" with zeros_replaced_by="adding 1" is not offered; use the default '
                                  'zeros_replaced_by="estimated small values", or test_method="clr".')
        from .community_r import log_ratios

        reference = columns.index(against) + 1 if kind == "alr" else None
        found = log_ratios(x, kind, how, reference, zeros=bool(zeros))
        if kind == "clr":
            new = [(f"clr_{c}", found[:, j]) for j, c in enumerate(columns)]
            print(f"Each value is now the log of its share over the row's geometric mean (clr, the centred log ratio), "
                  f"for {_columns_used(columns)}. A clr value above 0 means more than the row's typical kind; below 0, "
                  "less.")
        elif kind == "alr":
            others = [c for c in columns if c != against]
            new = [(f"alr_{c}", found[:, j]) for j, c in enumerate(others)]
            print(f'Each value is now the log of the column over "{against}" (alr, the additive log ratio, with '
                  f'"{against}" as the reference), for {len(others)} columns. Above 0 means more than "{against}".')
        else:
            new = [(f"ilr{j + 1}", found[:, j]) for j in range(found.shape[1])]
            print(f"{len(new)} isometric log ratios (ilr1 to ilr{len(new)}) of {_columns_used(columns)}, on the default "
                  "basis of R compositions::ilr(); another basis (such as scikit-bio's) gives other numbers but the "
                  "same distances between rows. For reading single columns, use clr.")
        if zeros and how == comp.ADDING_ONE:
            call = (f'vegan::decostand(x, "{kind}"{", reference = " + str(reference) if kind == "alr" else ""}, '
                    "pseudocount = 1)")
        else:
            first = ('x <- zCompositions::cmultRepl(x, method = "GBM", output = "p-counts", z.delete = FALSE); '
                     if zeros else "")
            call = first + {"clr": "compositions::clr(x)", "ilr": "compositions::ilr(x)",
                            "alr": f"compositions::alr(x, ivar = {reference})"}[kind]
        print(f"Method: run in R: {call}. Added {comp.short_list([n for n, _ in new], 4)}; the counts are kept.")
        if kind == "clr":
            print('Next: measure="aitchison" on find_distances_between_rows, add_principal_coordinates, '
                  "compare_profiles_of and explain_profiles_of works on these log ratios itself.")
        return self._with_new_columns(f"add {kind} log ratio columns of {', '.join(map(str, columns))}", new, keep)

    # ------------------------------------------------------------------ principal coordinates
    @friendly
    def add_principal_coordinates(self, columns=None, measure="bray-curtis", how_many=2):
        """Add principal coordinates (PCoA): a map of the rows from their distances, in new columns PCo1, PCo2.

        table.add_principal_coordinates(columns=["blaTEM", "blaCTXM", "sul1", "sul2", "tetA", "tetM"])   (with sdata.get_example("resistome"))
        Principal coordinate analysis draws the rows as points so that the straight-line distances
        on the map follow the measure= distances between the rows as closely as possible (R
        stats::cmdscale on vegan::vegdist). It is the twin of add_nmds, and with straight-line
        distances the same as principal components. measure= takes the measures of
        find_distances_between_rows: "bray-curtis" (the default), "aitchison" (for counts that are
        parts of a whole; then no eigenvalue is negative), "jaccard", "hellinger" ... columns= is
        required (the columns of counts). how_many= axes are added. Prints the share of the differences each axis shows (of the positive
        eigenvalues) and how many eigenvalues are negative: Bray-Curtis distances cannot be drawn
        exactly on a flat map. Signs are arbitrary. Rows with an empty cell get empty cells. Needs
        R (vegan).
        """
        step = "add_principal_coordinates"
        example = 'with sdata.get_example("resistome"): table.add_principal_coordinates(columns=["blaTEM", ...])'
        self._check_choice(step, "measure", measure, list(MEASURES))
        columns = self._required_columns(step, columns, example, at_least=1)
        x, keep = self._pattern_matrix(step, columns, least_rows=3)
        self._check_whole(step, "how_many=", how_many, 1, len(x) - 1, example)
        self._check_measure(measure, x, columns, step)
        from .community_r import principal_coordinates

        found = principal_coordinates(x, measure, how_many)
        eig = found["eig"]
        tiny = 1e-8 * np.abs(eig).max()
        positive = int((eig > tiny).sum())
        negative = int((eig < -tiny).sum())
        if positive < how_many:
            raise SimplydataError(f"Only {positive} eigenvalues are above 0, so {step}() can add at most {positive} "
                                  f"axes; use how_many={positive}.")
        points = _flip(found["points"])
        names = [f"PCo{i}" for i in range(1, how_many + 1)]
        gof = found["gof"]
        line = (f"Principal coordinates (PCoA) of the {MEASURES[measure]} distances between {len(x)} rows from "
                f"{_columns_used(columns)}: PCo1 shows {_pct(gof[0])} of the differences between rows")
        if how_many > 1:
            line += f", PCo1 to PCo{how_many} together {_pct(gof[how_many - 1])}"
        print(line + " (shares of the positive eigenvalues, R cmdscale's goodness of fit).")
        if negative:
            print(f"{negative} of {positive + negative} eigenvalues are negative, because {MEASURES[measure]} distances "
                  "cannot be drawn exactly on a flat map. vegan's summary(eigenvals()) and ape::pcoa() report "
                  f"{_pct(found['vegan_first'])} for PCo1 because they divide by the sum of all the eigenvalues, the "
                  "negative ones included.")
        elif measure == "aitchison":
            print("No eigenvalue is negative: Aitchison distances are straight-line distances between the clr log "
                  "ratios, so this map is the principal components of those columns (add_log_ratio_columns, then "
                  "add_principal_components(same_scale=False)).")
        print(f"Method: R stats::cmdscale(vegan::{MEASURE_R[measure]}, k = {how_many}, eig = TRUE). Added "
              f"{_list_words(names)}; the axes have the units of the distances, and their signs are arbitrary (each "
              "is turned so its biggest value is positive).")
        _depth_note(measure, x)
        return self._with_new_columns(f"add principal coordinates {', '.join(names)} of "
                                      f"{', '.join(map(str, columns))} ({measure})",
                                      [(n, points[:, i]) for i, n in enumerate(names)], keep)

    # ------------------------------------------------------------------ constrained ordination
    @friendly(renamed={"method": "test_method", "seed": "with_seed"})
    def explain_profiles_of(self, columns=None, using=None, measure=None, test_method=None, allowing_for=None,
                            permutations=999, with_seed=1):
        """How much of the differences in make-up between rows do other columns explain (RDA, db-RDA, CCA)?

        table.explain_profiles_of(["blaTEM", "blaCTXM", "sul1", "sul2", "tetA", "tetM"], using=["temperature", "salinity"])   (with sdata.get_example("resistome"))
        The twin of compare_profiles_of for columns of numbers: it explains the profiles in
        columns= (the counts of each kind) with the columns in using=. measure="bray-curtis"
        (the default) gives distance-based redundancy analysis (R vegan::dbrda), the same
        distance as compare_profiles_of; "hellinger" or "aitchison" give redundancy analysis on
        the transformed counts (vegan::rda); "jaccard", "manhattan" and "robust aitchison" go
        through dbrda too. measure="euclidean" on raw counts is refused (Legendre & Gallagher
        2001: use "hellinger"). test_method="canonical correspondence" ("cca" accepted) gives CCA
        (vegan::cca, chi-square distances, no measure=). allowing_for= takes columns into account
        first, without testing them (a partial analysis, vegan Condition()). Prints the share of
        the differences explained (adjusted R squared first), the test of all the columns
        together and each column tested after all the others (vegan anova(by = "margin"), so the
        order of using= does not matter), from permutations= shuffles (with_seed= makes them the
        same every time). Gives back one row for all the columns together and one per column
        (a test, like compare_profiles_of; for a map of the rows use add_principal_coordinates or
        add_nmds). columns= is required. Needs R (vegan).
        """
        step = "explain_profiles_of"
        example = 'table.explain_profiles_of(["blaTEM", "blaCTXM", "sul1", "tetM"], using=["temperature", "salinity"])'
        if using is None:
            raise SimplydataError(f"{step}() needs using=: the columns that might explain the make-up, such as "
                                  f"temperature and salinity.\nFor example, {example}")
        using = self._name_list(step, "using=", using, example)
        allowing = [] if allowing_for is None else self._name_list(step, "allowing_for=", allowing_for, example)
        self._need_columns(*using, *allowing)
        kind_cca = False
        if test_method is not None:
            if not isinstance(test_method, str) or test_method.strip().lower() not in CANONICAL:
                self._check_choice(step, "test_method", test_method, ["canonical correspondence"])
            kind_cca = True
            if measure is not None:
                raise SimplydataError('test_method="canonical correspondence" uses chi-square distances itself, so it '
                                      "takes no measure=. Leave measure= out, or leave test_method= out for "
                                      "distance-based RDA with that measure.")
        chosen_measure = measure is None and not kind_cca
        measure = "bray-curtis" if measure is None else measure
        if not kind_cca:
            self._check_choice(step, "measure", measure, list(MEASURES))
        self._check_seed_and_permutations(step, permutations, with_seed, example)
        columns = self._required_columns(step, columns, example, at_least=2)
        clash = [c for c in [*using, *allowing] if c in columns]
        if clash:
            raise SimplydataError(f"{_quoted_list(clash)} cannot be both a column of the profiles (columns=) and a "
                                  "column that explains them (using= or allowing_for=).")
        twice = [c for c in allowing if c in using]
        if twice:
            raise SimplydataError(f"{_quoted_list(twice)} cannot be in both using= and allowing_for=.")
        x, keep = self._pattern_matrix(step, columns, extra=(*using, *allowing), least_rows=4)
        if kind_cca:
            comp.check_not_negative(step, x, columns, 'with test_method="canonical correspondence"')
            comp.check_no_empty_rows(step, x, 'with test_method="canonical correspondence"')
            kind = "cca"
        else:
            if measure == "euclidean" and (x >= 0).all() and comp.whole_numbers(x):
                raise SimplydataError(
                    'measure="euclidean" on raw counts lets the most common kinds and the deepest samples decide '
                    "everything (Legendre & Gallagher 2001). Use the Hellinger distance, Euclidean on the square roots "
                    "of the shares:\n"
                    f'  table.explain_profiles_of(columns=[...], using={using!r}, measure="hellinger")'.replace("'", '"'))
            self._check_measure(measure, x, columns, step)
            kind = "rda" if measure in STRAIGHT_RDA else "dbrda"
        env = []
        terms = 0
        for name in [*using, *allowing]:
            values = [self._frame[name].to_list()[i] for i in np.flatnonzero(keep)]
            if self._frame.schema[name].is_numeric():
                env.append(np.asarray(values, dtype=float))
                terms += 1 if name in using else 0
            else:
                env.append(np.asarray([str(v) for v in values], dtype=object))
                terms += (len(set(values)) - 1) if name in using else 0
        if terms + len(allowing) > len(x) - 2:
            raise SimplydataError(f"{step}() needs more rows than explaining columns: {len(x)} rows cannot test "
                                  f"{terms} using= terms. Use fewer columns in using=.")
        from .community_r import constrained, model_call

        found = constrained(x, kind, measure, using, allowing, env, permutations, with_seed)
        said = _list_words(f'"{u}"' for u in using)
        beyond = f", beyond what {_list_words(chr(34) + a + chr(34) for a in allowing)} explains" if allowing else ""
        together = "together explain" if len(using) > 1 else "explains"
        share_of = "of all the differences" if allowing else "of the differences"
        print(f"{said} {together} {_pct(found['adj'])} {share_of} in make-up between the rows{beyond} "
              f"(adjusted R squared; {_pct(found['r2'])} before adjustment).")
        print(_permutation_p_sentence(found["all_p"], permutations,
                                      f"{'these columns' if len(using) > 1 else said} had no link with the make-up",
                                      "a link at least this strong",
                                      f"that {'these columns have' if len(using) > 1 else said + ' has'} no link with "
                                      "the make-up"))
        if len(found["terms"]) > 1:
            print("Each column tested after all the others (so the order of using= does not matter):")
        rows = [{"term": "all together", "pseudo-F": found["all_f"], "degrees of freedom": found["all_df"],
                 "p-value": found["all_p"], "R squared": found["r2"], "adjusted R squared": found["adj"]}]
        for t, f, p, df in zip(found["terms"], found["f"], found["p"], found["df"]):
            t = _clean_term(t)
            if len(found["terms"]) > 1:
                print(f'  "{t}": pseudo-F = {_num(f)}. ' + _permutation_p_sentence(
                    p, permutations, f'"{t}" had no link with the make-up once the other columns are allowed for',
                    "a link at least this strong", f'that "{t}" has no link with the make-up'))
            rows.append({"term": t, "pseudo-F": float(f), "degrees of freedom": float(df), "p-value": float(p),
                         "R squared": float("nan"), "adjusted R squared": float("nan")})
        names = {"rda": "redundancy analysis (RDA)", "dbrda": "distance-based redundancy analysis (db-RDA)",
                 "cca": "canonical correspondence analysis (CCA)"}
        prepare = {"hellinger": 'y <- vegan::decostand(x, "hellinger"); ',
                   "aitchison": 'y <- compositions::clr(zCompositions::cmultRepl(x, method = "GBM", '
                                'z.delete = FALSE)); ',
                   "euclidean": "y <- x; "}.get(measure, "") if kind == "rda" else (
            f"d <- vegan::{MEASURE_R[measure]}; " if kind == "dbrda" else "y <- x; ")
        adjusted = (f"set.seed({with_seed}); vegan::RsquareAdj(m, permutations = {permutations}) (for CCA the "
                    "adjusted R squared comes from permutations)" if kind == "cca" else "vegan::RsquareAdj(m)")
        print(f"Test: {names[kind]}, run in R: {prepare}m <- {model_call(kind, measure, using, allowing)}; "
              f"{adjusted}; set.seed({with_seed}); anova(m, permutations = {permutations}); "
              f'set.seed({with_seed}); anova(m, by = "margin", permutations = {permutations}).')
        if chosen_measure:
            print("simplydata chooses distance-based RDA on Bray-Curtis distances (the distance of compare_profiles_of), "
                  "each column tested after the others and the adjusted R squared first.")
        if found["vif"] is not None:
            high = [_clean_term(n) for n, v in zip(found["vif_names"], found["vif"]) if v > 10]
            if high:
                print(f"Note: {_quoted_list(high)} overlap{'s' if len(high) == 1 else ''} strongly with the other "
                      "using= columns (variance inflation above 10, vegan::vif.cca), so each one's own test is weak.")
        print("A link is not proof that a column changes the make-up: the data are observational.")
        if not kind_cca:
            _depth_note(measure, x)
        method_name = {"rda": "RDA", "dbrda": "db-RDA", "cca": "CCA"}[kind]
        for row in rows:
            row.update({"method": method_name, "distance": "chi-square" if kind_cca else MEASURES[measure],
                        "permutations": int(permutations)})
        data = {k: [r[k] for r in rows] for k in rows[0]}
        return self._new_table(nw.from_dict(data, backend=self._frame.implementation))

    # ------------------------------------------------------------------ Mantel and Procrustes
    @friendly(renamed={"method": "test_method", "seed": "with_seed"})
    def find_correlation_between_profiles(self, first=None, second=None, measure="bray-curtis", test_method="mantel",
                                          permutations=999, with_seed=1):
        """Do rows that differ in one set of columns also differ in another (Mantel, Procrustes)?

        table.find_correlation_between_profiles(first=["blaTEM", "blaCTXM", "sul1", "sul2", "tetA", "tetM"], second=["temperature", "salinity"])   (with sdata.get_example("resistome"))
        Compares two sets of columns measured on the same rows, such as the resistome and the
        bacteria, or the genes and the water chemistry. test_method="mantel" (the default) correlates
        the distances between rows in first= with those in second= (R vegan::mantel, Pearson);
        test_method="procrustes" fits the two maps of the rows (their first two principal coordinates)
        onto each other and gives their correlation (vegan::protest). measure= is used for first=,
        and for second= too when it also holds counts (whole numbers from 0); other number columns
        get straight-line distances after each column is put on the same scale. The p-value comes
        from shuffling the rows permutations= times (with_seed= makes it the same every time).
        Mantel answers a question about distances, not about the columns themselves. Needs R
        (vegan).
        """
        step = "find_correlation_between_profiles"
        example = ('table.find_correlation_between_profiles(first=["blaTEM", "blaCTXM", "sul1"], '
                   'second=["temperature", "salinity"])')
        self._check_choice(step, "test_method", test_method, CORRELATION_METHODS)
        self._check_choice(step, "measure", measure, list(MEASURES))
        self._check_seed_and_permutations(step, permutations, with_seed, example)
        if first is None or second is None:
            raise SimplydataError(f"{step}() needs first= and second=: two sets of columns measured on the same rows.\n"
                                  f"For example, {example}")
        first = self._pattern_columns(step, self._name_list(step, "first=", first, example), example)
        second = self._pattern_columns(step, self._name_list(step, "second=", second, example), example)
        both = [c for c in first if c in second]
        if both:
            raise SimplydataError(f"{_quoted_list(both)} cannot be in both first= and second=.")
        x, keep = self._pattern_matrix(step, first, extra=second, least_rows=5)
        y = np.column_stack([self._frame[c].to_numpy().astype(float) for c in second])[keep]
        self._check_measure(measure, x, first, step)
        # second= is read as counts only when it looks like a community table too: 3 or more columns of whole
        # numbers from 0 (two columns such as depth and year are measurements); the choice is printed first
        counts = (len(second) >= 3 and (y >= 0).all() and comp.whole_numbers(y) and measure in COUNT_MEASURES)
        if len(second) < 2 and test_method == "procrustes":
            raise SimplydataError("test_method=\"procrustes\" fits two maps with two axes each, so second= needs at "
                                  "least 2 columns; for one column use test_method=\"mantel\".")
        if counts:
            self._check_measure(measure, y, second, step)
            second_measure = measure
        else:
            flat = [c for c, s in zip(second, y.std(axis=0)) if not s > 0]
            if flat:
                raise SimplydataError(f"{_quoted_list(flat)} has the same value in every row, so it cannot tell the "
                                      "rows apart; leave it out of second=.")
            second_measure = SCALED
        if second_measure == SCALED:
            print("second= is read as measurements: straight-line distances after putting each column on the same "
                  "scale (R dist(scale(y))).")
        else:
            print(f"second= holds 3 or more columns of whole numbers from 0, so it is read as counts too, with "
                  f"{MEASURES[measure]} distances. If they are measurements, they need other distances: compare them "
                  "one at a time with find_correlation_between.")
        from .community_r import profile_correlation

        found = profile_correlation(x, y, measure, second_measure, test_method, permutations, with_seed)
        r, p = found["r"], found["p"]
        a, b = f"first= ({comp.short_list(first, 4)})", f"second= ({comp.short_list(second, 4)})"
        how_second = (f"{MEASURES[measure]} distances" if second_measure != SCALED else
                      "straight-line distances after each column is put on the same scale")
        if test_method == "mantel":
            if r > 0 and p < 0.05:
                print(f"Rows that differ in {a} also tend to differ in {b}: Mantel r = {_num(r)}.")
            else:
                print(f"Mantel r = {_num(r)} between the differences of the rows in {a} and in {b}.")
            null = f"the differences between rows in first= were unrelated to their differences in second="
            print(_permutation_p_sentence(p, permutations, null, "a correlation this big or bigger",
                                          "that the two sets are unrelated"))
            print(f"Test: Mantel test, run in R: set.seed({with_seed}); vegan::mantel(d1, d2, method = \"pearson\", "
                  f"permutations = {permutations}), with d1 = {MEASURES[measure]} distances of first= and d2 = "
                  f"{how_second} of second=.")
            print("Note: Mantel answers a question about distances, not about the columns themselves; it does not show "
                  "that any single column of one set follows any single column of the other (Legendre, Fortin & "
                  "Borcard 2015).")
            name = "Mantel r"
        else:
            print(f"The maps of the rows from {a} and from {b} match with a Procrustes correlation of {_num(r)} (0 = "
                  "unrelated, 1 = the same map after turning and scaling).")
            print(_permutation_p_sentence(p, permutations, "the two maps of the rows were unrelated",
                                          "a match this close or closer", "that the two sets are unrelated"))
            print(f"Test: Procrustes (PROTEST), run in R: set.seed({with_seed}); vegan::protest(cmdscale(d1, k = 2), "
                  f"cmdscale(d2, k = 2), permutations = {permutations}), with d1 = {MEASURES[measure]} distances of "
                  f"first= and d2 = {how_second} of second=.")
            name = "Procrustes correlation"
        row = {"test": "Mantel" if test_method == "mantel" else "Procrustes (PROTEST)", "first": ", ".join(first),
               "second": ", ".join(second), "distance of first": MEASURES[measure],
               "distance of second": MEASURES.get(second_measure, "Euclidean, scaled"), "statistic name": name,
               "statistic": float(r), "p-value": float(p), "permutations": int(permutations), "rows": int(len(x))}
        return self._result_table(row)

    # ------------------------------------------------------------------ discriminant axes
    @friendly(renamed={"for_each": "for_each_group_in"})
    def add_axes_that_separate_groups(self, columns=None, for_each_group_in=None, how_many=2):
        """Add the axes that separate groups most (linear discriminant analysis), in new columns LD1, LD2.

        table.add_axes_that_separate_groups(columns=["temperature", "salinity"], for_each_group_in="site")   (with sdata.get_example("resistome"))
        Linear discriminant analysis finds the combinations of columns= that separate the groups
        in for_each_group_in= best: LD1 separates them most, LD2 next. New columns LD1, LD2 ... are
        the axes that separate the groups most (not chart axes). Prints each axis's share of the
        separation, and how many rows a rule made without them classifies correctly
        (leave-one-out), next to the share found by always guessing the largest group. The prior
        chances are the group shares in the data (R MASS's default). columns=None uses every
        number column. Needs R (MASS, which comes with R).
        """
        step = "add_axes_that_separate_groups"
        example = 'table.add_axes_that_separate_groups(columns=["temperature", "salinity"], for_each_group_in="site")'
        self._need_name(step, "for_each_group_in=", for_each_group_in, example)
        self._need_columns(for_each_group_in)
        columns = self._pattern_columns(step, columns, example, leave_out=(for_each_group_in,))
        if for_each_group_in in columns:
            raise SimplydataError(f'"{for_each_group_in}" cannot be both a column and the for_each_group_in= column.')
        x, keep = self._pattern_matrix(step, columns, extra=(for_each_group_in,), least_rows=3)
        every = self._frame[for_each_group_in].to_list()
        groups = np.array([str(every[i]) for i in np.flatnonzero(keep)], dtype=object)
        kinds, sizes = np.unique(groups, return_counts=True)
        if len(kinds) < 2:
            raise SimplydataError(f'{step}() needs at least 2 groups in "{for_each_group_in}"; it found {len(kinds)}.')
        small = [str(k) for k, s in zip(kinds, sizes) if s < 2]
        if small:
            raise SimplydataError(f'{step}() needs at least 2 rows in each group; {_quoted_list(small)} in '
                                  f'"{for_each_group_in}" has fewer.')
        # the groups' spreads are pooled into one covariance of the columns, which needs more rows (less one
        # per group) than columns; MASS::lda cannot work it out otherwise
        if len(groups) - len(kinds) <= len(columns):
            raise SimplydataError(
                f"{step}() pools the spread within the groups, and that needs more rows than columns once one row "
                f"per group is set aside: {len(groups)} rows - {len(kinds)} groups = {len(groups) - len(kinds)}, "
                f"with {len(columns)} columns. Use fewer columns (columns=[...]) or more rows.")
        thin = [f'"{k}" ({s} rows)' for k, s in zip(kinds, sizes) if s <= len(columns)]
        most = min(len(kinds) - 1, len(columns))
        self._check_whole(step, "how_many=", how_many, 1, most, example)
        from .community_r import discriminant

        found = discriminant(x, groups)
        scores = _flip(found["scores"][:, :how_many])
        names = [f"LD{i}" for i in range(1, how_many + 1)]
        trace = found["trace"]
        if found["scores"].shape[1] == 1:
            print(f"Axis that separates the {len(kinds)} groups of \"{for_each_group_in}\" from "
                  f"{_columns_used(columns)}: with two groups LD1 is the only axis.")
        else:
            parts = [f"{n} {_pct(trace[i])}" for i, n in enumerate(names) if i < len(trace)]
            print(f"Axes that separate the {len(kinds)} groups of \"{for_each_group_in}\" from "
                  f"{_columns_used(columns)}: {_list_words(parts)} of the separation (the proportion of trace, as R "
                  "MASS prints it).")
        import pandas as pd

        actual = pd.Series(groups, name="group")
        guessed = pd.Series(found["loo"], name="classified as")
        correct = float(np.mean(found["loo"] == groups))
        if thin:
            print(f"Note: {_list_words(thin)} in \"{for_each_group_in}\" {'has' if len(thin) == 1 else 'have'} no "
                  f"more rows than there are columns ({len(columns)}): the axes can follow the chance spread of so few "
                  "rows, so trust the leave-one-out share more than the picture. Fewer columns or more rows help.")
        chance = float(actual.value_counts(normalize=True).max())
        print(f"Each row was classified by a rule made without it (leave-one-out): {_pct(correct)} classified "
              f"correctly; by always guessing the largest group: {_pct(chance)}.")
        table = pd.crosstab(actual, guessed)
        print("  " + table.to_string().replace("\n", "\n  "))
        shares = ", ".join(f"{k} {p:.2f}" for k, p in zip(found["levels"], found["prior"]))
        print(f"Method: R MASS::lda(x, {for_each_group_in}), predict()$x, and lda(CV = TRUE) for the leave-one-out "
              f"classes. The prior chances are the group shares in the data (MASS's default): {shares}. Added "
              f"{_list_words(names)}, the axes that separate the groups most; their signs are arbitrary.")
        return self._with_new_columns(f"add axes that separate groups {', '.join(names)} of "
                                      f"{', '.join(map(str, columns))} by {for_each_group_in}",
                                      [(n, scores[:, i]) for i, n in enumerate(names)], keep)

    # ------------------------------------------------------------------ correspondence axes
    @friendly
    def add_correspondence_axes(self, columns=None, how_many=2, show=None):
        """Add correspondence axes (CA for counts, MCA for text columns), in new columns CA1, CA2.

        table.add_correspondence_axes(columns=["blaTEM", "blaCTXM", "sul1", "sul2", "tetA", "tetM"])   (with sdata.get_example("resistome"))
        Correspondence analysis draws the rows of a table of counts as points, so that rows with
        similar profiles (shares of each column) lie close: R vegan::cca(x) with no explaining
        columns (ter Braak's CA, the ecologists' engine). With text columns (answers such as
        "agree", "disagree") it runs multiple correspondence analysis instead: R
        ca::mjca(lambda = "adjusted"), with Greenacre's adjusted inertia. The first line printed
        says which ran. how_many= axes are added; the share of the inertia (the chi-square
        differences) each shows is printed. columns= is required. Rows with an empty cell get
        empty cells. Signs are arbitrary. Needs R (vegan; ca for text columns).
        show="numbers" gives back the axes as a table instead of adding columns: each row's number in the
        table, its coordinates, the eigenvalue of each axis ("CA1 eigenvalue"), its share of the inertia
        ("CA1 share of the inertia") and the total inertia, as R gives them (vegan: summary(eigenvals()) and
        tot.chi). For text columns (MCA) the table holds the shares and the total of the adjusted inertia
        (ca::mjca inertia.e and inertia.t); ca gives the adjusted eigenvalues only rounded to 6 decimals, so they
        are left out.
        """
        step = "add_correspondence_axes"
        if show is not None:
            self._check_choice(step, "show", show, ("numbers",))
        example = 'with sdata.get_example("resistome"): table.add_correspondence_axes(columns=["blaTEM", ...])'
        if columns is not None:
            listed = self._name_list(step, "columns=", columns, example)
            self._need_columns(*listed)
            text = [c for c in listed if not self._frame.schema[c].is_numeric()]
            if text and len(text) < len(listed):
                raise SimplydataError(f"{step}() takes columns of counts (correspondence analysis) or text columns "
                                      "(multiple correspondence analysis), not both at once: "
                                      f"{_quoted_list(text)} {'is' if len(text) == 1 else 'are'} text.")
            if text:
                return self._mca(step, listed, how_many, example, show)
        columns = self._required_columns(step, columns, example, at_least=2)
        x, keep = self._pattern_matrix(step, columns, least_rows=3)
        comp.check_not_negative(step, x, columns, "")
        comp.check_no_empty_rows(step, x, "")
        empty = [c for c, s in zip(columns, x.sum(axis=0)) if not s > 0]
        if empty:
            raise SimplydataError(f"{_quoted_list(empty)} {'is' if len(empty) == 1 else 'are'} 0 in every row, so "
                                  "correspondence analysis cannot use it; leave it out with columns=[...].")
        self._check_whole(step, "how_many=", how_many, 1, min(len(x), len(columns)) - 1, example)
        from .community_r import correspondence

        found = correspondence(x, how_many)
        names = [f"CA{i}" for i in range(1, how_many + 1)]
        scores = _flip(found["scores"][:, :how_many])
        parts = [f"{n} {_pct(found['share'][i])} (eigenvalue {_num(found['eig'][i])})" for i, n in enumerate(names)]
        print(f"Correspondence analysis (CA) of {_columns_used(columns)} in {len(x)} rows: {_list_words(parts)} of the "
              f"total inertia {_num(found['total'])} (the chi-square differences between the rows' profiles).")
        print(f"Method: R vegan::cca(x) with no explaining columns, summary(eigenvals()), tot.chi, and the row scores "
              f'with scaling = "sites". Added {_list_words(names)}; their signs are arbitrary.')
        if show == "numbers":
            return self._numbers_table([(n, scores[:, i]) for i, n in enumerate(names)], keep,
                                       [(f"{n} eigenvalue", found["eig"][i]) for i, n in enumerate(names)]
                                       + [(f"{n} share of the inertia", found["share"][i]) for i, n in enumerate(names)]
                                       + [("total inertia", found["total"])])
        return self._with_new_columns(f"add correspondence axes {', '.join(names)} of {', '.join(map(str, columns))}",
                                      [(n, scores[:, i]) for i, n in enumerate(names)], keep)

    def _mca(self, step, columns, how_many, example, show=None):
        if len(columns) < 2:
            raise SimplydataError(f"{step}() needs at least 2 text columns for multiple correspondence analysis; for "
                                  f'one, count its answers with table.count_each("{columns[0]}").')
        rows = len(self._frame)
        values = [self._frame[c].to_list() for c in columns]
        keep = np.array([all(v[i] is not None and v[i] == v[i] for v in values) for i in range(rows)], dtype=bool)
        from .stat_tests import _skipped_note

        _skipped_note(int((~keep).sum()), columns)
        if keep.sum() < 3:
            raise SimplydataError(f"{step}() needs at least 3 rows without empty cells.")
        used = [np.asarray([str(v[i]) for i in np.flatnonzero(keep)], dtype=object) for v in values]
        single = [c for c, v in zip(columns, used) if len(set(v)) < 2]
        if single:
            raise SimplydataError(f"{_quoted_list(single)} has only one answer in every row, so it cannot separate "
                                  "the rows; leave it out.")
        from .community_r import multiple_correspondence

        found = multiple_correspondence(columns, used, how_many)
        if found["scores"].shape[1] < how_many:
            raise SimplydataError(f"Only {found['scores'].shape[1]} axes have adjusted inertia above 0; use "
                                  f"how_many={found['scores'].shape[1]}.")
        names = [f"CA{i}" for i in range(1, how_many + 1)]
        scores = _flip(found["scores"][:, :how_many])
        parts = [f"axis {i + 1} {_pct(found['share'][i])}" for i in range(how_many)]
        print(f"Multiple correspondence analysis (MCA) of {len(columns)} text columns ({comp.short_list(columns)}) in "
              f"{int(keep.sum())} rows: {_list_words(parts)} of the total adjusted inertia {_num(found['total'])} "
              "(Greenacre's adjustment).")
        print('Method: R ca::mjca(x, lambda = "adjusted"), inertia.e and inertia.t, and the rows\' principal '
              "coordinates. FactoMineR's MCA() "
              "reports the unadjusted inertia, which looks much smaller for the same axes. Added "
              f"{_list_words(names)}; their signs are arbitrary.")
        if show == "numbers":
            return self._numbers_table([(n, scores[:, i]) for i, n in enumerate(names)], keep,
                                       [(f"{n} share of the inertia", found["share"][i]) for i, n in enumerate(names)]
                                       + [("total inertia", found["total"])])
        return self._with_new_columns(f"add correspondence axes {', '.join(names)} of {', '.join(columns)} (MCA)",
                                      [(n, scores[:, i]) for i, n in enumerate(names)], keep)

