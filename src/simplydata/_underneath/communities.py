"""Communities and resistomes (phase S3c-1): the new words add_diversity_columns, draw_richness_curves,
add_log_ratio_columns, add_principal_coordinates, explain_profiles_of, find_correlation_between_profiles,
draw_cluster_tree, add_axes_that_separate_groups and add_correspondence_axes, and one entry for each new option or
value that changes what a word calls in R (keyed by word and option), on the made-up practice table "resistome".
"""

from . import Entry

GENES = ('["blaTEM", "blaCTXM", "blaOXA48", "blaNDM", "sul1", "sul2", "tetA", "tetM", "qnrS", "ermB", "aadA", '
         '"mphA", "vanA", "mcr1"]')
RESISTOME = """
    import pandas as pd
    df = pd.read_csv("resistome.csv")
    x = df.iloc[:, 5:].to_numpy(dtype=float)
    site = df["site"].to_numpy(dtype=object)
    temperature = df["temperature"].to_numpy(dtype=float)
    salinity = df["salinity"].to_numpy(dtype=float)
    reads = df["reads"].to_numpy(dtype=float)
"""
START = """
            genes = {genes}
            table = sdata.table(sdata.get_example("resistome"))
"""


def _ours(body):
    import textwrap

    lines = textwrap.dedent(body).strip("\n").splitlines()
    return START.format(genes=GENES) + "".join("            " + line + "\n" for line in lines)


VEGAN_NOTE = ("scikit-bio has some of these, but it is not a simplydata dependency and its defaults changed between "
              "versions, so the numbers come from R vegan, the community ecologists' reference.")
COMP_NOTE = ("scikit-bio has clr and a multiplicative replacement, but not zCompositions' GBM (which estimates each "
             "replacement from the data) and its ilr basis differs from R compositions, so the numbers come from R.")
FLIP = """
    import numpy as np
    import pandas as pd
    s = np.sign(points[np.abs(points).argmax(axis=0), np.arange(points.shape[1])])  # ({n})
    pd.DataFrame(points * s, columns={names})
"""
GENE_NAMES = 'names = list(pd.read_csv("resistome.csv").columns[5:])'
TESTS_ALSO = ("simplydata also tests each column after all the others, says the result in words with the W2 sentence "
              "and the permutation floor, and notes overlapping columns (vif.cca) and the sequencing-depth trap.")


def _flip(n, names):
    return FLIP.format(n=n, names=names)


ENTRIES = [
    # ------------------------------------------------------------------ diversity
    Entry(
        word="table.add_diversity_columns",
        data="resistome",
        ours=_ours("""
            table.add_diversity_columns(columns=genes)
            table.keep_columns(*["richness", "shannon", "simpson"])
        """),
        code={
            "R": """
                # add_diversity_columns(columns=genes)
                list(richness = vegan::specnumber(x),
                     shannon = vegan::diversity(x, index = "shannon"),   # (1)
                     simpson = vegan::diversity(x, index = "simpson"))   # (2)
            """,
            "Python": """
                import pandas as pd
                pd.DataFrame({"richness": richness, "shannon": shannon, "simpson": simpson})
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="table", tolerance=1e-9,
        choices=("Shannon with the natural log (vegan's base = exp(1)); scikit-bio changed its default base from 2 to e "
                 "in 0.6.1, so older numbers may be in bits.",
                 "Simpson as 1 - the sum of squared shares (the Gini-Simpson index): the chance that two counts drawn "
                 "at random are of different kinds."),
        python_note=VEGAN_NOTE,
        also="simplydata also gives each index as a number of equally common kinds (Hill numbers), notes when the "
             "rows' totals differ more than two-fold and gives empty cells to rows with nothing in them.",
    ),
    Entry(
        word="table.add_diversity_columns", option="at_total_count=",
        data="resistome",
        ours=_ours("""
            table.add_diversity_columns(columns=genes, show="richness", at_total_count=2000)
            table.keep_columns(*["richness", "expected richness at 2000"])
        """),
        code={
            "R": """
                # add_diversity_columns(columns=genes, show="richness", at_total_count=2000)
                r <- suppressWarnings(vegan::rarefy(x, sample = 2000))   # (1)
                r[rowSums(x) < 2000] <- NA                               # (2)
                list(richness = vegan::specnumber(x), rarefied = r)
            """,
            "Python": """
                import pandas as pd
                pd.DataFrame({"richness": richness, "expected richness at 2000": rarefied})
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="table", tolerance=1e-9,
        choices=("rarefaction as the expected richness in a sample of that many counts (Hurlbert 1971), not a random "
                 "subsample, so the answer is the same every time.",
                 "a row with fewer counts than that in all gets an empty cell (vegan gives its observed richness), "
                 "and the printout names it."),
        python_note=VEGAN_NOTE,
        also="simplydata also refuses at_total_count= on numbers that are not whole (normalised values).",
    ),
    Entry(
        word="table.add_diversity_columns", option='show="chao1"',
        data="resistome",
        ours=_ours("""
            table.add_diversity_columns(columns=genes, show="chao1")
            table.keep_columns(*["chao1", "chao1 standard error"])
        """),
        code={
            "R": """
                # add_diversity_columns(columns=genes, show="chao1")
                e <- vegan::estimateR(x)                                 # (1)
                list(chao1 = e["S.chao1", ], se = e["se.chao1", ])
            """,
            "Python": """
                import pandas as pd
                pd.DataFrame({"chao1": chao1, "chao1 standard error": se})
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="table", tolerance=1e-9,
        choices=("the bias-corrected Chao1 (Chao 1987) with its standard error, as vegan::estimateR gives it; it needs "
                 "raw counts, because it leans on the kinds seen once or twice.",),
        python_note=VEGAN_NOTE,
        also="simplydata also refuses Chao1 on numbers that are not whole, with the reason.",
    ),
    Entry(
        word="table.add_diversity_columns", option='show="hill numbers"',
        data="resistome",
        ours=_ours("""
            table.add_diversity_columns(columns=genes, show="hill numbers")
            table.keep_columns(*["hill number 0", "hill number 1", "hill number 2"])
        """),
        code={
            "R": """
                # add_diversity_columns(columns=genes, show="hill numbers")
                h <- vegan::renyi(x, scales = c(0, 1, 2), hill = TRUE)   # (1)
                list(hill = as.matrix(h))
            """,
            "Python": """
                import pandas as pd
                pd.DataFrame(hill, columns=["hill number 0", "hill number 1", "hill number 2"])
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="table", tolerance=1e-9,
        choices=("Hill numbers of order 0, 1 and 2 (richness, exp(Shannon), inverse Simpson): each is a number of "
                 "equally common kinds, so they can be compared directly (Jost 2006).",),
        python_note=VEGAN_NOTE,
        also="simplydata also says each average in words, as a number of equally common kinds.",
    ),
    Entry(
        word="draw_richness_curves",
        data="resistome",
        ours=_ours("""
            chart = table.start_chart()
            chart.draw_richness_curves(columns=genes)
        """),
        code={
            "R": """
                # draw_richness_curves(columns=genes)
                rownames(x) <- seq_len(nrow(x)); colnames(x) <- seq_len(ncol(x))
                step <- max(1, floor(min(rowSums(x)) / 50))                 # (1)
                r <- vegan::rarecurve(x, step = step, tidy = TRUE)          # (2)
                list(row = as.integer(r$Site), at = r$Sample, richness = r$Species)
            """,
            "matplotlib": """
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                for i in range(1, int(row.max()) + 1):
                    ax.plot(at[row == i], richness[row == i])
                ax.axvline(min(at[row == i].max() for i in range(1, int(row.max()) + 1)), linestyle=":")  # (3)
                ax.set_xlabel("Total count (reads, individuals)")
                ax.set_ylabel("Expected kinds present (richness)")
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="chart", check=("lines", "labels"), tolerance=1e-9,
        choices=("about 50 points on the shortest curve: the step is a 50th of the smallest row total.",
                 "the curves are vegan's own (rarecurve with tidy = TRUE): the expected richness of vegan::rarefy at "
                 "each step, up to each row's total.",
                 "a dotted line at the smallest row total: richness can be compared at or below it."),
        python_note="Python has no rarefaction curve in SciPy or statsmodels, so the numbers come from R vegan; "
                    "matplotlib draws them.",
        also="simplydata also refuses normalised values, colours the curves by a group column (colour=) and writes the "
             "rows' names at the ends (names=).",
    ),
    # ------------------------------------------------------------------ log ratios
    Entry(
        word="table.add_log_ratio_columns",
        data="resistome",
        ours=_ours("""
            table.add_log_ratio_columns(columns=genes)
            table.keep_columns(*["clr_" + g for g in genes])
        """),
        code={
            "R": """
                # add_log_ratio_columns(columns=genes)
                r <- zCompositions::cmultRepl(x, method = "GBM", output = "p-counts",  # (1)
                                              z.delete = FALSE, suppress.print = TRUE)  # (2)
                m <- compositions::clr(r)                                              # (3)
                list(clr = matrix(as.numeric(unclass(m)), nrow = nrow(x)))
            """,
            "Python": """
                import pandas as pd
                """ + GENE_NAMES + """
                pd.DataFrame(clr, columns=["clr_" + g for g in names])
            """,
        },
        r_inputs=RESISTOME, r_packages=("zCompositions", "compositions"), compare="table", tolerance=1e-9,
        choices=("zeros replaced by estimated small values: zCompositions' Bayesian-multiplicative replacement (GBM), "
                 "which estimates each from the data and keeps the ratios of the other parts; only when there are "
                 "zeros.",
                 "z.delete = FALSE: no column is deleted (cmultRepl's default deletes columns that are more than 80 % "
                 "zeros, with only a message); simplydata refuses columns with fewer than 2 values above 0 instead, "
                 "with the line that merges them.",
                 "clr: the log of each value over the row's geometric mean, R compositions::clr."),
        python_note=COMP_NOTE,
        also="simplydata also refuses non-whole numbers for GBM (it would run on them and give other values), prints "
             "one summary of the zeros, and keeps the counts.",
    ),
    Entry(
        word="table.add_log_ratio_columns", option='test_method="alr"',
        data="resistome",
        ours=_ours("""
            table.add_log_ratio_columns(columns=genes, test_method="alr", against="sul1")
            table.keep_columns(*["alr_" + g for g in genes if g != "sul1"])
        """),
        code={
            "R": """
                # add_log_ratio_columns(columns=genes, test_method="alr", against="sul1")
                r <- zCompositions::cmultRepl(x, method = "GBM", output = "p-counts",
                                              z.delete = FALSE, suppress.print = TRUE)
                m <- compositions::alr(r, ivar = 5)                                   # (1)
                list(alr = matrix(as.numeric(unclass(m)), nrow = nrow(x)))
            """,
            "Python": """
                import pandas as pd
                """ + GENE_NAMES + """
                pd.DataFrame(alr, columns=["alr_" + g for g in names if g != "sul1"])
            """,
        },
        r_inputs=RESISTOME, r_packages=("zCompositions", "compositions"), compare="table", tolerance=1e-9,
        choices=('the reference is the column named in against= ("sul1", the 5th), R compositions::alr(ivar =).',),
        python_note=COMP_NOTE,
        also="simplydata also names the reference in every sentence.",
    ),
    Entry(
        word="table.add_log_ratio_columns", option='test_method="ilr"',
        data="resistome",
        ours=_ours("""
            table.add_log_ratio_columns(columns=genes, test_method="ilr")
            table.keep_columns(*[f"ilr{i}" for i in range(1, 14)])
        """),
        code={
            "R": """
                # add_log_ratio_columns(columns=genes, test_method="ilr")
                r <- zCompositions::cmultRepl(x, method = "GBM", output = "p-counts",
                                              z.delete = FALSE, suppress.print = TRUE)
                m <- compositions::ilr(r)                                             # (1)
                list(ilr = matrix(as.numeric(unclass(m)), nrow = nrow(x)))
            """,
            "Python": """
                import pandas as pd
                pd.DataFrame(ilr, columns=[f"ilr{i}" for i in range(1, ilr.shape[1] + 1)])
            """,
        },
        r_inputs=RESISTOME, r_packages=("zCompositions", "compositions"), compare="table", tolerance=1e-9,
        choices=("the default basis of R compositions::ilr(); another basis (scikit-bio's) gives other numbers but the "
                 "same distances between rows, and the printout says so.",),
        python_note=COMP_NOTE,
        also="simplydata also suggests clr for reading single columns.",
    ),
    Entry(
        word="table.add_log_ratio_columns", option='zeros_replaced_by="adding 1"',
        data="resistome",
        ours=_ours("""
            table.add_log_ratio_columns(columns=genes, zeros_replaced_by="adding 1")
            table.keep_columns(*["clr_" + g for g in genes])
        """),
        code={
            "R": """
                # add_log_ratio_columns(columns=genes, zeros_replaced_by="adding 1")
                m <- vegan::decostand(x, method = "clr", pseudocount = 1)             # (1)
                list(clr = unname(as.matrix(m)))
            """,
            "Python": """
                import pandas as pd
                """ + GENE_NAMES + """
                pd.DataFrame(clr, columns=["clr_" + g for g in names])
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="table", tolerance=1e-9,
        choices=("1 added to every count before the logs (vegan's pseudocount), only when there are zeros; the "
                 "printout says the answer depends on the 1 you added.",),
        python_note=COMP_NOTE,
        also="simplydata also prints how many cells were zero.",
    ),
    # ------------------------------------------------------------------ principal coordinates
    Entry(
        word="table.add_principal_coordinates",
        data="resistome",
        ours=_ours("""
            table.add_principal_coordinates(columns=genes)
            table.keep_columns(*["PCo1", "PCo2"])
        """),
        code={
            "R": """
                # add_principal_coordinates(columns=genes)
                d <- vegan::vegdist(x, method = "bray")
                p <- stats::cmdscale(d, k = 2, eig = TRUE)                 # (1)
                list(points = p$points)
            """,
            "Python": _flip(2, '["PCo1", "PCo2"]'),
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="table", tolerance=1e-9,
        choices=("classical scaling of the Bray-Curtis distances, R stats::cmdscale with the eigenvalues, so the "
                 "printout can say how many are negative.",
                 "each axis turned so its biggest value is positive: the sign of an axis is arbitrary, and this gives "
                 "the same answer on every computer."),
        python_note="scikit-bio has pcoa, but it is not a simplydata dependency, so the numbers come from R.",
        also="simplydata also gives each axis's share of the positive eigenvalues (cmdscale's GOF), how many "
             "eigenvalues are negative, and what vegan and ape report instead.",
    ),
    Entry(
        word="table.add_principal_coordinates", option='measure="aitchison"',
        data="resistome",
        ours=_ours("""
            table.add_principal_coordinates(columns=genes, measure="aitchison")
            table.keep_columns(*["PCo1", "PCo2"])
        """),
        code={
            "R": """
                # add_principal_coordinates(columns=genes, measure="aitchison")
                r <- zCompositions::cmultRepl(x, method = "GBM", output = "p-counts",  # (1)
                                              z.delete = FALSE, suppress.print = TRUE)
                d <- vegan::vegdist(as.matrix(r), method = "aitchison")              # (2)
                list(points = stats::cmdscale(d, k = 2, eig = TRUE)$points)
            """,
            "Python": _flip(3, '["PCo1", "PCo2"]'),
        },
        r_inputs=RESISTOME, r_packages=("vegan", "zCompositions"), compare="table", tolerance=1e-9,
        choices=("zeros replaced by estimated small values first (GBM, no column deleted), as vegdist refuses zeros "
                 "for the Aitchison distance.",
                 "the Aitchison distance: the straight-line distance between the rows' clr log ratios.",
                 "each axis turned so its biggest value is positive."),
        python_note=COMP_NOTE,
        also="simplydata also says that no eigenvalue is negative and that the map equals principal components of "
             "the clr columns.",
    ),
    # ------------------------------------------------------------------ constrained ordination
    Entry(
        word="table.explain_profiles_of",
        data="resistome",
        ours=_ours("""
            table.explain_profiles_of(genes, using=["temperature", "salinity"])
        """),
        code={
            "R": """
                # explain_profiles_of(genes, using=["temperature", "salinity"])
                d <- vegan::vegdist(x, method = "bray")
                m <- vegan::dbrda(d ~ temperature + salinity,                # (1)
                                  data = data.frame(temperature, salinity))
                r2 <- vegan::RsquareAdj(m)                                   # (2)
                set.seed(1); a <- anova(m, permutations = 999)               # (3)
                list(adj = r2$adj.r.squared, r2 = r2$r.squared, f = a$F[1], p = a[["Pr(>F)"]][1])
            """,
            "Python": """
                {"adjusted R squared": adj, "R squared": r2, "pseudo-F": f, "p-value": p}
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="result",
        fields=("adjusted R squared", "R squared", "pseudo-F", "p-value"), tolerance=1e-9,
        choices=("distance-based RDA on Bray-Curtis distances, the same distance as compare_profiles_of.",
                 "the adjusted R squared first (Peres-Neto et al. 2006): the unadjusted one grows with every column.",
                 "999 permutations after set.seed(1)."),
        python_note="Python has no constrained ordination in SciPy or statsmodels, so the numbers come from R vegan.",
        also=TESTS_ALSO,
    ),
    Entry(
        word="table.explain_profiles_of", option='measure="hellinger"',
        data="resistome",
        ours=_ours("""
            result = table.explain_profiles_of(genes, using=["temperature", "salinity"], measure="hellinger")
            result
        """),
        code={
            "R": """
                # explain_profiles_of(genes, using=[...], measure="hellinger")
                y <- vegan::decostand(x, "hellinger")                        # (1)
                m <- vegan::rda(y ~ temperature + salinity, data = data.frame(temperature, salinity))
                set.seed(1)
                a <- anova(m, by = "margin", permutations = 999)             # (2)
                list(f = a["temperature", "F"], p = a["temperature", "Pr(>F)"])
            """,
            "Python": """
                {"pseudo-F": f, "p-value": p}
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="result", row="temperature",
        fields=("pseudo-F", "p-value"), tolerance=1e-9,
        choices=("RDA on the Hellinger-transformed counts (square roots of the shares; Legendre & Gallagher 2001), "
                 "never on raw counts.",
                 "each column tested after all the others (by = \"margin\"), so the order of using= does not matter; "
                 "anova's own default tests in sequence."),
        python_note="Python has no constrained ordination in SciPy or statsmodels, so the numbers come from R vegan.",
        also=TESTS_ALSO,
    ),
    Entry(
        word="table.explain_profiles_of", option='test_method="canonical correspondence"',
        data="resistome",
        ours=_ours("""
            result = table.explain_profiles_of(genes, using=["temperature", "salinity"],
                                               test_method="canonical correspondence")
            result
        """),
        code={
            "R": """
                # explain_profiles_of(genes, using=[...], test_method="canonical correspondence")
                m <- vegan::cca(x ~ temperature + salinity, data = data.frame(temperature, salinity))  # (1)
                set.seed(1); r2 <- vegan::RsquareAdj(m, permutations = 999)                           # (2)
                set.seed(1); a <- anova(m, permutations = 999)
                list(adj = r2$adj.r.squared, r2 = r2$r.squared, f = a$F[1], p = a[["Pr(>F)"]][1])
            """,
            "Python": """
                {"adjusted R squared": adj, "R squared": r2, "pseudo-F": f, "p-value": p}
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="result",
        fields=("adjusted R squared", "R squared", "pseudo-F", "p-value"), tolerance=1e-9,
        choices=("CCA on the counts themselves (chi-square distances), so no measure=.",
                 "CCA's adjusted R squared comes from permutations (vegan), after set.seed."),
        python_note="Python has no constrained ordination in SciPy or statsmodels, so the numbers come from R vegan.",
        also=TESTS_ALSO,
    ),
    Entry(
        word="table.explain_profiles_of", option="allowing_for=",
        data="resistome",
        ours=_ours("""
            result = table.explain_profiles_of(genes, using=["temperature"], allowing_for="site")
            result
        """),
        code={
            "R": """
                # explain_profiles_of(genes, using=["temperature"], allowing_for="site")
                d <- vegan::vegdist(x, method = "bray")
                env <- data.frame(temperature, site = factor(site))
                m <- vegan::dbrda(d ~ temperature + Condition(site), data = env)   # (1)
                r2 <- vegan::RsquareAdj(m)
                set.seed(1); a <- anova(m, permutations = 999)
                list(adj = r2$adj.r.squared, r2 = r2$r.squared, f = a$F[1], p = a[["Pr(>F)"]][1])
            """,
            "Python": """
                {"adjusted R squared": adj, "R squared": r2, "pseudo-F": f, "p-value": p}
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="result",
        fields=("adjusted R squared", "R squared", "pseudo-F", "p-value"), tolerance=1e-9,
        choices=("a partial analysis: site is taken into account first (vegan Condition()) and not tested, the same "
                 "meaning allowing_for= has on the other words.",),
        python_note="Python has no constrained ordination in SciPy or statsmodels, so the numbers come from R vegan.",
        also=TESTS_ALSO,
    ),
    # ------------------------------------------------------------------ Mantel and Procrustes
    Entry(
        word="table.find_correlation_between_profiles",
        data="resistome",
        ours=_ours("""
            result = table.find_correlation_between_profiles(first=genes, second=["temperature", "salinity"])
            result
        """),
        code={
            "R": """
                # find_correlation_between_profiles(first=genes, second=["temperature", "salinity"])
                set.seed(1)
                d1 <- vegan::vegdist(x, method = "bray")
                d2 <- stats::dist(scale(cbind(temperature, salinity)))       # (1)
                t <- vegan::mantel(d1, d2, method = "pearson", permutations = 999)  # (2)
                list(r = t$statistic, p = t$signif)
            """,
            "Python": """
                {"statistic": r, "p-value": p}
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="result", fields=("statistic", "p-value"), tolerance=1e-9,
        choices=("measurements (not counts) in second= get straight-line distances after each column is put on the "
                 "same scale; counts would get measure=.",
                 "the Pearson Mantel correlation with 999 permutations after set.seed(1)."),
        python_note="scikit-bio has a Mantel test, but it is not a simplydata dependency, so the numbers come from R "
                    "vegan.",
        also="simplydata also says which distance each set used and Legendre et al.'s caveat: Mantel is about "
             "distances, not the columns.",
    ),
    Entry(
        word="table.find_correlation_between_profiles", option='test_method="procrustes"',
        data="resistome",
        ours=_ours("""
            result = table.find_correlation_between_profiles(first=genes, second=["temperature", "salinity"],
                                                             test_method="procrustes")
            result
        """),
        code={
            "R": """
                # find_correlation_between_profiles(..., test_method="procrustes")
                set.seed(1)
                d1 <- vegan::vegdist(x, method = "bray")
                d2 <- stats::dist(scale(cbind(temperature, salinity)))
                t <- vegan::protest(stats::cmdscale(d1, k = 2), stats::cmdscale(d2, k = 2),  # (1)
                                    permutations = 999)
                list(r = t$t0, p = t$signif)
            """,
            "Python": """
                {"statistic": r, "p-value": p}
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="result", fields=("statistic", "p-value"), tolerance=1e-9,
        choices=("PROTEST on the first two principal coordinates of each set: the Procrustes correlation and its "
                 "permutation p-value.",),
        python_note="SciPy has procrustes (the fit, without the permutation test), so the numbers come from R vegan.",
        also="simplydata also says the correlation in words (0 = unrelated, 1 = the same map).",
    ),
    # ------------------------------------------------------------------ PERMANOVA family
    Entry(
        word="table.compare_profiles_of", option='test_method="anosim"',
        data="resistome",
        ours=_ours("""
            table.compare_profiles_of(genes, for_each_group_in="site", test_method="anosim")
        """),
        code={
            "R": """
                # compare_profiles_of(genes, for_each_group_in="site", test_method="anosim")
                set.seed(1)
                d <- vegan::vegdist(x, method = "bray")
                a <- vegan::anosim(d, factor(site), permutations = 999)       # (1)
                list(r = a$statistic, p = a$signif)
            """,
            "Python": """
                {"statistic": r, "p-value": p}
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="result", fields=("statistic", "p-value"), tolerance=1e-9,
        choices=("Clarke's ANOSIM R from ranked distances, 999 permutations after set.seed(1).",),
        python_note="scikit-bio has anosim, but it is not a simplydata dependency, so the numbers come from R vegan.",
        also="simplydata also runs the spread check (betadisper) and says what ANOSIM cannot show.",
    ),
    Entry(
        word="table.compare_profiles_of", option='show="contributions"',
        data="resistome",
        ours=_ours("""
            table.compare_profiles_of(genes, for_each_group_in="site", show="contributions")
        """),
        code={
            "R": """
                # compare_profiles_of(genes, for_each_group_in="site", show="contributions")
                s <- summary(vegan::simper(x, factor(site), permutations = 0))[[1]]  # (1)
                list(a = s$average[1], sd = s$sd[1], ratio = s$ratio[1], cum = s$cumsum[1])
            """,
            "Python": """
                {"average contribution": a, "standard deviation": sd, "ratio": ratio, "cumulative share": cum}
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="result",
        fields=("average contribution", "standard deviation", "ratio", "cumulative share"), tolerance=1e-9,
        choices=("SIMPER without permutation p-values (permutations = 0): Warton et al. 2012 show they mislead; the "
                 "table is a description, not a test.",),
        python_note="No Python package simplydata uses has SIMPER, so the numbers come from R vegan.",
        also="simplydata also prints Warton's caveat: large, variable columns rise to the top even when they do not "
             "differ.",
    ),
    Entry(
        word="table.compare_profiles_of", option='measure="aitchison"',
        data="resistome",
        ours=_ours("""
            table.compare_profiles_of(genes, for_each_group_in="site", measure="aitchison")
        """),
        code={
            "R": """
                # compare_profiles_of(genes, for_each_group_in="site", measure="aitchison")
                set.seed(1)
                r <- zCompositions::cmultRepl(x, method = "GBM", output = "p-counts",  # (1)
                                              z.delete = FALSE, suppress.print = TRUE)
                d <- vegan::vegdist(as.matrix(r), method = "aitchison")
                a <- vegan::adonis2(d ~ factor(site), permutations = 999)
                list(f = a$F[1], r2 = a$R2[1], p = a[["Pr(>F)"]][1])
            """,
            "Python": """
                {"statistic": f, "R squared": r2, "p-value": p}
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan", "zCompositions"), compare="result",
        fields=("statistic", "R squared", "p-value"), tolerance=1e-9,
        choices=("zeros replaced by estimated small values (GBM, no column deleted), then the Aitchison distance.",),
        python_note=COMP_NOTE,
        also="simplydata also prints one summary of the zeros and the spread check.",
    ),
    Entry(
        word="table.find_distances_between_rows", option='measure="aitchison"',
        data="resistome",
        ours=_ours("""
            table.find_distances_between_rows(columns=genes, measure="aitchison")
        """),
        code={
            "R": """
                # find_distances_between_rows(columns=genes, measure="aitchison")
                r <- zCompositions::cmultRepl(x, method = "GBM", output = "p-counts",  # (1)
                                              z.delete = FALSE, suppress.print = TRUE)
                d <- vegan::vegdist(as.matrix(r), method = "aitchison")              # (2)
                list(d = as.matrix(d))
            """,
            "Python": """
                import pandas as pd
                out = pd.DataFrame(d, columns=[str(i) for i in range(1, len(d) + 1)])
                out.insert(0, "row", [str(i) for i in range(1, len(d) + 1)])
                out
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan", "zCompositions"), compare="table", tolerance=1e-9,
        choices=("zeros replaced by estimated small values first (GBM, no column deleted); vegdist refuses zeros for "
                 "this distance.",
                 "the Aitchison distance: the straight-line distance between the rows' clr log ratios."),
        python_note=COMP_NOTE,
        also="simplydata also refuses non-whole numbers for the replacement and suggests measure=\"robust aitchison\".",
    ),
    # ------------------------------------------------------------------ clusters
    Entry(
        word="table.add_clusters", option='how_many="automatic"',
        data="resistome",
        ours=_ours("""
            table.add_clusters(columns=genes, how_many="automatic", test_method="hierarchical", measure="bray-curtis")
            table.keep_columns(*["cluster"])
        """),
        code={
            "R": """
                # add_clusters(columns=genes, how_many="automatic", test_method="hierarchical", measure="bray-curtis")
                d <- vegan::vegdist(x, method = "bray")
                h <- stats::hclust(d, method = "average")                         # (1)
                w <- sapply(2:10, function(k)                                     # (2)
                  summary(cluster::silhouette(stats::cutree(h, k), d))$avg.width)
                list(cluster = stats::cutree(h, (2:10)[which.max(w)]))            # (3)
            """,
            "Python": """
                import pandas as pd
                pd.DataFrame({"cluster": pd.factorize(cluster)[0] + 1})  # (4)
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan", "cluster"), compare="table", tolerance=1e-9,
        choices=("average linkage, simplydata's choice for Bray-Curtis distances (Ward assumes straight lines).",
                 "the average silhouette width (R cluster::silhouette) for 2 to 10 clusters.",
                 "the number with the largest width; on a tie, the fewer clusters.",
                 "the clusters numbered 1, 2, 3 in the order they first appear in the table."),
        python_note="SciPy makes the tree (simplydata's side uses SciPy linkage too); the silhouette comes from R "
                    "cluster.",
        also="simplydata also prints the width for each number of clusters and Kaufman and Rousseeuw's guide.",
    ),
    Entry(
        word="table.add_clusters", option="measure=",
        data="resistome",
        ours=_ours("""
            table.add_clusters(columns=genes, how_many=3, test_method="hierarchical", measure="bray-curtis")
            table.keep_columns(*["cluster"])
        """),
        code={
            "R": """
                # add_clusters(columns=genes, how_many=3, test_method="hierarchical", measure="bray-curtis")
                d <- vegan::vegdist(x, method = "bray")                         # (1)
                h <- stats::hclust(d, method = "average")                       # (2)
                list(cluster = stats::cutree(h, 3))
            """,
            "Python": """
                import pandas as pd
                pd.DataFrame({"cluster": pd.factorize(cluster)[0] + 1})
            """,
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="table", tolerance=1e-9,
        choices=("the counts as they are (no rescaling) for Bray-Curtis distances.",
                 "average linkage, chosen for Bray-Curtis (Ward is refused with it), the same as draw_cluster_tree."),
        python_note="SciPy's linkage gives the same tree on the same distances; the distances are vegan's.",
        also="simplydata also prints the average silhouette width when R is there.",
    ),
    Entry(
        word="draw_cluster_tree",
        data="resistome",
        ours=_ours("""
            chart = table.start_chart()
            chart.draw_cluster_tree(columns=genes, measure="bray-curtis", names="sample")
        """),
        code={
            "SciPy": """
                # draw_cluster_tree(columns=genes, measure="bray-curtis", names="sample")
                import matplotlib.pyplot as plt
                from scipy.cluster import hierarchy
                from scipy.spatial.distance import pdist
                import pandas as pd
                df = pd.read_csv("resistome.csv")
                x = df.iloc[:, 5:].to_numpy(dtype=float)
                tree = hierarchy.linkage(pdist(x, "braycurtis"), method="average")  # (1)
                found = hierarchy.dendrogram(tree, labels=list(df["sample"]), no_plot=True)
                fig, ax = plt.subplots()
                for xs, ys in zip(found["icoord"], found["dcoord"]):
                    ax.plot(xs, ys)
                ax.set_xticks(range(5, 10 * len(x), 10), found["ivl"])
            """,
        },
        compare="chart", check=("lines", "ticks"), tolerance=1e-9,
        choices=("average linkage for Bray-Curtis distances, the same choice as table.add_clusters, so the tree "
                 "matches the clusters.",),
        also="simplydata also prints the cophenetic correlation (SciPy cophenet): how well the tree keeps the "
             "distances.",
    ),
    # ------------------------------------------------------------------ discriminant and correspondence axes
    Entry(
        word="table.add_axes_that_separate_groups",
        data="resistome",
        ours=_ours("""
            table.add_axes_that_separate_groups(columns=["temperature", "salinity", "reads"], for_each_group_in="site")
            table.keep_columns(*["LD1", "LD2"])
        """),
        code={
            "R": """
                # add_axes_that_separate_groups(columns=[...], for_each_group_in="site")
                f <- MASS::lda(cbind(temperature, salinity, reads), site)       # (1)
                list(points = predict(f)$x[, 1:2])
            """,
            "Python": _flip(2, '["LD1", "LD2"]'),
        },
        r_inputs=RESISTOME, r_packages=("MASS",), compare="table", tolerance=1e-9,
        choices=("MASS's default prior chances: the group shares in the data.",
                 "each axis turned so its biggest value is positive."),
        python_note="scikit-learn has LinearDiscriminantAnalysis, but it is not a simplydata dependency and scales "
                    "the axes differently, so the numbers come from R MASS.",
        also="simplydata also prints each axis's share of the separation, the leave-one-out accuracy beside the "
             "chance level and the classification table.",
    ),
    Entry(
        word="table.add_correspondence_axes",
        data="resistome",
        ours=_ours("""
            table.add_correspondence_axes(columns=genes)
            table.keep_columns(*["CA1", "CA2"])
        """),
        code={
            "R": """
                # add_correspondence_axes(columns=genes)
                m <- vegan::cca(x)                                              # (1)
                s <- vegan::scores(m, display = "sites", scaling = "sites", choices = 1:2)  # (2)
                list(points = unname(as.matrix(s)))
            """,
            "Python": _flip(3, '["CA1", "CA2"]'),
        },
        r_inputs=RESISTOME, r_packages=("vegan",), compare="table", tolerance=1e-9,
        choices=("correspondence analysis as ter Braak's CA in vegan (cca with no explaining columns).",
                 "row scores with scaling = \"sites\" (vegan's default is \"species\").",
                 "each axis turned so its biggest value is positive."),
        python_note="No Python package simplydata uses has correspondence analysis, so the numbers come from R vegan.",
        also="simplydata also prints each axis's share of the inertia, and runs MCA (R ca::mjca) on text columns.",
    ),
]
