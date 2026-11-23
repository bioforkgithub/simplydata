"""The reliability study for phase S3c-1, communities and resistomes: add_diversity_columns, draw_richness_curves,
add_log_ratio_columns, add_principal_coordinates, explain_profiles_of, find_correlation_between_profiles,
draw_cluster_tree, add_axes_that_separate_groups, add_correspondence_axes, and the new options of
compare_profiles_of, find_distances_between_rows and add_clusters.

cases.py loads this file at its end and calls add_to(), which adds the datasets and cases below to its own DATASETS
and CASES and teaches load() the datasets read from R packages (vegan, MASS, ca: not stored here, their licence is
the packages', GPL, so they are read where they are published). Printed numbers (shares in %, rounded to one
decimal) are read from the printout and compared with R at the printed rounding.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

VEGAN_DATA = 'e <- new.env(); utils::data(list = c({names}), package = "vegan", envir = e); '
R_DATA_COMMUNITIES = {
    "dune (vegan)": (("vegan",), VEGAN_DATA.format(names='"dune", "dune.env"') + (
        "c(as.list(e$dune), list(Management = as.character(e$dune.env$Management), A1 = e$dune.env$A1))")),
    "varespec and varechem (vegan)": (("vegan",), VEGAN_DATA.format(names='"varespec", "varechem"') + (
        "c(as.list(e$varespec), as.list(e$varechem))")),
    "BCI (vegan)": (("vegan",), VEGAN_DATA.format(names='"BCI"') + "as.list(e$BCI)"),
    "mite (vegan)": (("vegan",), VEGAN_DATA.format(names='"mite", "mite.env"') + (
        "c(as.list(e$mite), list(Topo = as.character(e$mite.env$Topo)))")),
    "crabs (MASS)": (("MASS",), "d <- MASS::crabs; list(kind = paste(d$sp, d$sex), FL = d$FL, RW = d$RW, CL = d$CL, "
                                "CW = d$CW, BD = d$BD)"),
    "wg93 (ca)": (("ca",), 'e <- new.env(); utils::data("wg93", package = "ca", envir = e); '
                           "lapply(e$wg93[, 1:4], as.character)"),
}
DUNE_ENV = ("Management", "A1")
VARECHEM = ("N", "P", "K", "Ca", "Mg", "S", "Al", "Fe", "Mn", "Zn", "Mo", "Baresoil", "Humdepth", "pH")
LOAD = {
    "dune": ('e <- new.env(); utils::data(list = c("dune", "dune.env"), package = "vegan", envir = e); '
             "x <- as.matrix(e$dune); "),
    "vare": ('e <- new.env(); utils::data(list = c("varespec", "varechem"), package = "vegan", envir = e); '
             "x <- as.matrix(e$varespec); env <- e$varechem; "),
    "bci": 'e <- new.env(); utils::data("BCI", package = "vegan", envir = e); x <- as.matrix(e$BCI); ',
    "mite": ('e <- new.env(); utils::data(list = c("mite", "mite.env"), package = "vegan", envir = e); '
             "x <- as.matrix(e$mite); "),
}
GBM = ('r <- as.matrix(zCompositions::cmultRepl(x, method = "GBM", output = "p-counts", z.delete = FALSE, '
       "suppress.print = TRUE)); ")
FLIP = "s <- sign(p[cbind(apply(abs(p), 2, which.max), seq_len(ncol(p)))]); p <- sweep(p, 2, s, `*`); "
IND = " " * 17  # the indent of the case blocks below, so a block joined to these lines dedents as one
PRINTED = """
{i}import contextlib, io, re
{i}out = io.StringIO()
{i}with contextlib.redirect_stdout(out):
{i}    {call}
{i}text = out.getvalue()"""


def _printed(call):
    return PRINTED.format(i=IND, call=call)


def _datasets(Dataset):
    vegan = ("Shipped with the R package vegan (GPL-2); read from the installed package, so it needs R.")
    return [
        Dataset("dune (vegan)", "", "20 meadow plots in the Netherlands: the cover of 30 plant species, and how each "
                "meadow was managed (Management) and the thickness of the soil's A1 horizon",
                "Jongman, R. H., ter Braak, C. J. F. & van Tongeren, O. F. R. (1987, 1995). Data Analysis in Community "
                "and Landscape Ecology. Pudoc / Cambridge University Press. Shipped with the R package vegan (dune, "
                "dune.env).", vegan, "https://cran.r-project.org/package=vegan"),
        Dataset("varespec and varechem (vegan)", "", "24 lichen pastures in Finnish Lapland: the cover of 44 plant "
                "and lichen species and 14 soil measurements (N, P, K ...)",
                "Väre, H., Ohtonen, R. & Oksanen, J. (1995). Effects of reindeer grazing on understorey vegetation in "
                "dry Pinus sylvestris forests. Journal of Vegetation Science 6, 523-530. Shipped with the R package "
                "vegan (varespec, varechem); analysed in Oksanen, J. (2015). Multivariate analysis of ecological "
                "communities in R: vegan tutorial.", vegan, "https://doi.org/10.2307/3236351"),
        Dataset("BCI (vegan)", "", "Trees counted in 50 one-hectare plots of the Barro Colorado Island forest "
                "plot, Panama: 225 species",
                "Condit, R. et al. (2002). Beta-diversity in tropical forest trees. Science 295, 666-669. Shipped with "
                "the R package vegan (BCI).", vegan, "https://doi.org/10.1126/science.1066854"),
        Dataset("mite (vegan)", "", "Oribatid mites counted in 70 soil cores of a peat bog: 35 species (whole "
                "counts with many zeros), and the microtopography of each core (Topo: blanket or hummock)",
                "Borcard, D. & Legendre, P. (1994). Environmental control and spatial structure in ecological "
                "communities: an example using oribatid mites (Acari, Oribatei). Environmental and Ecological "
                "Statistics 1, 37-61. Shipped with the R package vegan (mite, mite.env).", vegan,
                "https://doi.org/10.1007/BF00714196"),
        Dataset("crabs (MASS)", "", "200 Leptograpsus crabs from Western Australia: five shell measurements, two "
                "colour forms and both sexes (four groups of 50)",
                "Campbell, N. A. & Mahon, R. J. (1974). A multivariate study of variation in two species of rock crab "
                "of genus Leptograpsus. Australian Journal of Zoology 22, 417-425; Venables, W. N. & Ripley, B. D. "
                "(2002). Modern Applied Statistics with S, 4th ed., section 12.1. Shipped with the R package MASS.",
                "GPL-2 | GPL-3 (MASS, which comes with R); read from the installed package, so it needs R.",
                "https://doi.org/10.1071/ZO9740417"),
        Dataset("wg93 (ca)", "", "871 answers of the 1993 International Social Survey Programme (West Germany) to "
                "four questions on science and the environment (A to D, answers 1 to 5)",
                "Greenacre, M. (2007). Correspondence Analysis in Practice, 2nd ed. Chapman & Hall/CRC; Nenadić, O. & "
                "Greenacre, M. (2007). Correspondence analysis in R, with two- and three-dimensional graphics: the ca "
                "package. Journal of Statistical Software 20(3) (CC BY). Shipped with the R package ca (wg93).",
                "GPL (>= 2) (ca); read from the installed package, so it needs R.",
                "https://doi.org/10.18637/jss.v020.i03"),
    ]


def _cases(Case):
    dune = f"\n{IND}species = [c for c in data.columns if c not in {DUNE_ENV!r}]"
    vare = f"\n{IND}species = [c for c in data.columns if c not in {VARECHEM!r}]"
    mite = f'\n{IND}species = [c for c in data.columns if c != "Topo"]'
    bci = f"\n{IND}species = list(data.columns)"
    nl = "\n" + IND
    rows3 = ("{{" + ", ".join(f'"{{name}} plot {i + 1}": r["{{column}}"][{i}]' for i in range(3)) + "}}")

    def three(name, column):
        return rows3.format(name=name, column=column)

    oksanen = "Oksanen (2015), vegan tutorial: CA eigenvalues 0.5249 and 0.3568 of total inertia 2.083"
    nenadic = "Nenadić & Greenacre (2007), JSS 20(3), and Greenacre (2007): adjusted inertia of wg93 A to D"
    return [
        # ---------------------------------------------------------------- diversity
        Case("table.add_diversity_columns", "BCI: richness, Shannon and Simpson of the first three plots",
             "BCI (vegan)", "real data",
             ours=bci + nl + "r = sdata.table(data).add_diversity_columns(columns=species).as_pandas()" + nl
                  + "{**" + three("richness", "richness") + ", **" + three("Shannon", "shannon") + ", **"
                  + three("Simpson", "simpson") + "}",
             r=LOAD["bci"] + """
                 s <- vegan::specnumber(x); h <- vegan::diversity(x); d <- vegan::diversity(x, "simpson")
                 list(`richness plot 1` = s[1], `richness plot 2` = s[2], `richness plot 3` = s[3],
                      `Shannon plot 1` = h[1], `Shannon plot 2` = h[2], `Shannon plot 3` = h[3],
                      `Simpson plot 1` = d[1], `Simpson plot 2` = d[2], `Simpson plot 3` = d[3])
             """, r_packages=("vegan",), r_tolerance=1e-12,
             note="vegan's own help computes these on BCI (Shannon 4.018, 3.848 and 3.814; Simpson 0.975, 0.968 and "
                  "0.965 for the first three plots); the check is against vegan itself."),
        Case("table.add_diversity_columns", "at_total_count=: BCI, the expected richness in 20 trees",
             "BCI (vegan)", "real data",
             ours=bci + nl + "r = sdata.table(data).add_diversity_columns(columns=species, show=\"richness\", "
                        "at_total_count=20).as_pandas()" + nl + three("rarefied", "expected richness at 20"),
             r=LOAD["bci"] + """
                 r <- vegan::rarefy(x, sample = 20)
                 list(`rarefied plot 1` = r[1], `rarefied plot 2` = r[2], `rarefied plot 3` = r[3])
             """, r_packages=("vegan",), r_tolerance=1e-12,
             note="vegan's rarefy help example: 16.361, 15.670 and 15.301 for the first three plots."),
        Case("table.add_diversity_columns", 'show="chao1": BCI, the bias-corrected Chao1 of the first three plots',
             "BCI (vegan)", "real data",
             ours=bci + nl + "r = sdata.table(data).add_diversity_columns(columns=species, show=\"chao1\").as_pandas()"
                  + nl + "{**" + three("Chao1", "chao1") + ", **" + three("Chao1 SE", "chao1 standard error") + "}",
             r=LOAD["bci"] + """
                 e <- vegan::estimateR(x)
                 list(`Chao1 plot 1` = e[2, 1], `Chao1 plot 2` = e[2, 2], `Chao1 plot 3` = e[2, 3],
                      `Chao1 SE plot 1` = e[3, 1], `Chao1 SE plot 2` = e[3, 2], `Chao1 SE plot 3` = e[3, 3])
             """, r_packages=("vegan",), r_tolerance=1e-12),
        Case("table.add_diversity_columns", 'show="hill numbers": BCI, Hill numbers of order 1 and 2',
             "BCI (vegan)", "real data",
             ours=bci + nl + "r = sdata.table(data).add_diversity_columns(columns=species, show=\"hill numbers\")"
                        ".as_pandas()" + nl + "{**" + three("q1", "hill number 1") + ", **" + three("q2", "hill number 2")
                  + "}",
             r=LOAD["bci"] + """
                 h <- vegan::renyi(x, scales = c(1, 2), hill = TRUE)
                 list(`q1 plot 1` = h[1, 1], `q1 plot 2` = h[2, 1], `q1 plot 3` = h[3, 1],
                      `q2 plot 1` = h[1, 2], `q2 plot 2` = h[2, 2], `q2 plot 3` = h[3, 2])
             """, r_packages=("vegan",), r_tolerance=1e-12,
             note="Hill number 1 is exp(Shannon) and 2 the inverse Simpson index (Jost 2006)."),
        Case("draw_richness_curves", "BCI: the first plot's curve", "BCI (vegan)", "real data",
             ours=bci + """
                 chart = sdata.table(data).start_chart()
                 chart.draw_richness_curves(columns=species)
                 line = chart._render().axes[0].get_lines()[0]
                 {"second point": line.get_xdata()[1], "richness there": line.get_ydata()[1],
                  "richness at the end": line.get_ydata()[-1]}
             """,
             r=LOAD["bci"] + """
                 step <- max(1, floor(min(rowSums(x)) / 50))
                 list(`second point` = 1 + step, `richness there` = vegan::rarefy(x[1, ], 1 + step),
                      `richness at the end` = vegan::specnumber(x[1, ]))
             """, r_packages=("vegan",), r_tolerance=1e-9),
        # ---------------------------------------------------------------- log ratios
        Case("table.add_log_ratio_columns", "mite: clr of 35 mite species, zeros replaced by estimated small values",
             "mite (vegan)", "real data",
             ours=mite + """
                 r = sdata.table(data).add_log_ratio_columns(columns=species).as_pandas()
                 {"clr row 1 first": r["clr_" + species[0]][0], "clr row 2 last": r["clr_" + species[-1]][1],
                  "clr row 70 first": r["clr_" + species[0]][69]}
             """,
             r=LOAD["mite"] + GBM + """
                 m <- unclass(compositions::clr(r))
                 list(`clr row 1 first` = m[1, 1], `clr row 2 last` = m[2, ncol(m)], `clr row 70 first` = m[70, 1])
             """, r_packages=("zCompositions", "compositions"), r_tolerance=1e-9),
        Case("table.add_log_ratio_columns", 'test_method="alr": mite, every species over the first one',
             "mite (vegan)", "real data",
             ours=mite + """
                 r = sdata.table(data).add_log_ratio_columns(columns=species, test_method="alr",
                                                             against=species[0]).as_pandas()
                 {"alr row 1 second": r["alr_" + species[1]][0], "alr row 5 last": r["alr_" + species[-1]][4]}
             """,
             r=LOAD["mite"] + GBM + """
                 m <- unclass(compositions::alr(r, ivar = 1))
                 list(`alr row 1 second` = m[1, 1], `alr row 5 last` = m[5, ncol(m)])
             """, r_packages=("zCompositions", "compositions"), r_tolerance=1e-9),
        Case("table.add_log_ratio_columns", 'test_method="ilr": mite, isometric log ratios', "mite (vegan)", "real data",
             ours=mite + """
                 r = sdata.table(data).add_log_ratio_columns(columns=species, test_method="ilr").as_pandas()
                 {"ilr1 row 1": r["ilr1"][0], "ilr34 row 3": r["ilr34"][2]}
             """,
             r=LOAD["mite"] + GBM + """
                 m <- unclass(compositions::ilr(r))
                 list(`ilr1 row 1` = m[1, 1], `ilr34 row 3` = m[3, 34])
             """, r_packages=("zCompositions", "compositions"), r_tolerance=1e-9),
        Case("table.add_log_ratio_columns", 'zeros_replaced_by="adding 1": mite, clr after adding 1',
             "mite (vegan)", "real data",
             ours=mite + """
                 r = sdata.table(data).add_log_ratio_columns(columns=species, zeros_replaced_by="adding 1").as_pandas()
                 {"clr row 1 first": r["clr_" + species[0]][0], "clr row 9 fifth": r["clr_" + species[4]][8]}
             """,
             r=LOAD["mite"] + """
                 m <- as.matrix(vegan::decostand(x, "clr", pseudocount = 1))
                 list(`clr row 1 first` = m[1, 1], `clr row 9 fifth` = m[9, 5])
             """, r_packages=("vegan",), r_tolerance=1e-9),
        # ---------------------------------------------------------------- PCoA
        Case("table.add_principal_coordinates", "dune: PCoA of the Bray-Curtis distances", "dune (vegan)",
             "real data",
             ours=dune + _printed("table = sdata.table(data).add_principal_coordinates(columns=species)") + """
                 r = table.as_pandas()
                 {"PCo1 row 1": r["PCo1"][0], "PCo2 row 20": r["PCo2"][19],
                  "PCo1 % of positive": float(re.search(r"PCo1 shows ([\\d.]+) %", text).group(1)),
                  "PCo1 % (vegan, ape)": float(re.search(r"report ([\\d.]+) % for PCo1", text).group(1)),
                  "negative eigenvalues": float(re.search(r"(\\d+) of \\d+ eigenvalues are negative", text).group(1))}
             """,
             r=LOAD["dune"] + """
                 d <- vegan::vegdist(x); f <- stats::cmdscale(d, k = 2, eig = TRUE); p <- f$points
             """ + FLIP + """
                 list(`PCo1 row 1` = p[1, 1], `PCo2 row 20` = p[20, 2],
                      `PCo1 % of positive` = round(100 * stats::cmdscale(d, k = 1, eig = TRUE)$GOF[2], 1),
                      `PCo1 % (vegan, ape)` = round(100 * summary(vegan::eigenvals(vegan::wcmdscale(d, eig = TRUE)))[2, 1], 1),
                      `negative eigenvalues` = sum(f$eig < -1e-8 * max(abs(f$eig))))
             """, r_packages=("vegan",), r_tolerance=1e-9,
             note="The shares are read from the printout (one decimal) and compared with R rounded the same way; the "
                  "design check found 37.4 % of the positive eigenvalues, 39.9 % in vegan and ape, and 5 negative "
                  "eigenvalues."),
        Case("table.add_principal_coordinates", 'measure="aitchison": mite, PCoA of the Aitchison distances',
             "mite (vegan)", "real data",
             ours=mite + """
                 r = sdata.table(data).add_principal_coordinates(columns=species, measure="aitchison").as_pandas()
                 {"PCo1 row 1": r["PCo1"][0], "PCo2 row 70": r["PCo2"][69]}
             """,
             r=LOAD["mite"] + GBM + "p <- stats::cmdscale(vegan::vegdist(r, \"aitchison\"), k = 2); " + FLIP
               + "list(`PCo1 row 1` = p[1, 1], `PCo2 row 70` = p[70, 2])",
             r_packages=("vegan", "zCompositions"), r_tolerance=1e-8),
        # ---------------------------------------------------------------- constrained ordination
        Case("table.explain_profiles_of", "varespec and varechem: db-RDA on Bray-Curtis with N, P and K",
             "varespec and varechem (vegan)", "real data",
             ours=vare + """
                 r = sdata.table(data).explain_profiles_of(species, using=["N", "P", "K"]).as_pandas().set_index("term")
                 {"adjusted R squared": r.loc["all together", "adjusted R squared"],
                  "R squared": r.loc["all together", "R squared"], "p N": r.loc["N", "p-value"],
                  "p P": r.loc["P", "p-value"], "p K": r.loc["K", "p-value"], "F N": r.loc["N", "pseudo-F"]}
             """,
             r=LOAD["vare"] + """
                 m <- vegan::dbrda(x ~ N + P + K, data = env, distance = "bray"); r2 <- vegan::RsquareAdj(m)
                 set.seed(1); a <- anova(m, by = "margin", permutations = 999)
                 list(`adjusted R squared` = r2$adj.r.squared, `R squared` = r2$r.squared, `p N` = a["N", 4],
                      `p P` = a["P", 4], `p K` = a["K", 4], `F N` = a["N", "F"])
             """, r_packages=("vegan",), r_tolerance=1e-9,
             note="The design check found adjusted R squared 0.0753 and marginal p-values 0.171, 0.265 and 0.496."),
        Case("table.explain_profiles_of", 'measure="hellinger": varespec and varechem, RDA with N, P and K',
             "varespec and varechem (vegan)", "real data",
             ours=vare + """
                 r = sdata.table(data).explain_profiles_of(species, using=["N", "P", "K"],
                                                           measure="hellinger").as_pandas().set_index("term")
                 {"adjusted R squared": r.loc["all together", "adjusted R squared"],
                  "F all": r.loc["all together", "pseudo-F"], "p all": r.loc["all together", "p-value"]}
             """,
             r=LOAD["vare"] + """
                 m <- vegan::rda(vegan::decostand(x, "hellinger") ~ N + P + K, data = env)
                 set.seed(1); a <- anova(m, permutations = 999)
                 list(`adjusted R squared` = vegan::RsquareAdj(m)$adj.r.squared, `F all` = a$F[1], `p all` = a[1, 4])
             """, r_packages=("vegan",), r_tolerance=1e-9,
             note="The design check found adjusted R squared 0.0825."),
        Case("table.explain_profiles_of", 'test_method="canonical correspondence": varespec, CCA with Al, P and K',
             "varespec and varechem (vegan)", "real data",
             ours=vare + """
                 r = sdata.table(data).explain_profiles_of(species, using=["Al", "P", "K"],
                                                           test_method="canonical correspondence").as_pandas()
                 r = r.set_index("term")
                 {"R squared": r.loc["all together", "R squared"], "F all": r.loc["all together", "pseudo-F"],
                  "p Al": r.loc["Al", "p-value"]}
             """,
             r=LOAD["vare"] + """
                 m <- vegan::cca(x ~ Al + P + K, data = env)
                 set.seed(1); a <- anova(m, by = "margin", permutations = 999)
                 list(`R squared` = vegan::RsquareAdj(m)$r.squared, `F all` = anova(m, permutations = 9)$F[1],
                      `p Al` = a["Al", 4])
             """, r_packages=("vegan",), r_tolerance=1e-9,
             note="The model of Oksanen's vegan tutorial (cca(varespec ~ Al + P + K, varechem))."),
        Case("table.explain_profiles_of", "allowing_for=: dune, management after allowing for the A1 horizon",
             "dune (vegan)", "real data",
             ours=dune + """
                 r = sdata.table(data).explain_profiles_of(species, using="Management", allowing_for="A1").as_pandas()
                 {"adjusted R squared": r["adjusted R squared"][0], "F": r["pseudo-F"][0], "p": r["p-value"][0]}
             """,
             r=LOAD["dune"] + """
                 m <- vegan::dbrda(vegan::vegdist(x) ~ Management + Condition(A1), data = e$dune.env)
                 set.seed(1); a <- anova(m, permutations = 999)
                 list(`adjusted R squared` = vegan::RsquareAdj(m)$adj.r.squared, F = a$F[1], p = a[1, 4])
             """, r_packages=("vegan",), r_tolerance=1e-9),
        # ---------------------------------------------------------------- Mantel, Procrustes
        Case("table.find_correlation_between_profiles", "varespec and varechem: Mantel test",
             "varespec and varechem (vegan)", "real data",
             ours=vare + """
                 r = sdata.table(data).find_correlation_between_profiles(first=species, second=list({chem})).as_pandas()
                 {{"Mantel r": r["statistic"][0], "p": r["p-value"][0]}}
             """.format(chem=VARECHEM),
             r=LOAD["vare"] + """
                 set.seed(1)
                 t <- vegan::mantel(vegan::vegdist(x), stats::dist(scale(env)), permutations = 999)
                 list(`Mantel r` = t$statistic, p = t$signif)
             """, r_packages=("vegan",), r_tolerance=1e-9,
             note="The design check found r 0.305 (p 0.001)."),
        Case("table.find_correlation_between_profiles", 'test_method="procrustes": varespec and varechem',
             "varespec and varechem (vegan)", "real data",
             ours=vare + """
                 r = sdata.table(data).find_correlation_between_profiles(first=species, second=list({chem}),
                                                                         test_method="procrustes").as_pandas()
                 {{"Procrustes correlation": r["statistic"][0], "p": r["p-value"][0]}}
             """.format(chem=VARECHEM),
             r=LOAD["vare"] + """
                 set.seed(1)
                 t <- vegan::protest(stats::cmdscale(vegan::vegdist(x), k = 2),
                                     stats::cmdscale(stats::dist(scale(env)), k = 2), permutations = 999)
                 list(`Procrustes correlation` = t$t0, p = t$signif)
             """, r_packages=("vegan",), r_tolerance=1e-9),
        # ---------------------------------------------------------------- compare_profiles_of, distances
        Case("table.compare_profiles_of", 'test_method="anosim": dune by management', "dune (vegan)", "real data",
             ours=dune + """
                 r = sdata.table(data).compare_profiles_of(species, for_each_group_in="Management",
                                                           test_method="anosim").as_pandas()
                 {"ANOSIM R": r["statistic"][0], "p": r["p-value"][0]}
             """,
             r=LOAD["dune"] + """
                 set.seed(1); a <- vegan::anosim(vegan::vegdist(x), e$dune.env$Management, permutations = 999)
                 list(`ANOSIM R` = a$statistic, p = a$signif)
             """, r_packages=("vegan",), r_tolerance=1e-9,
             note="The example of vegan's anosim help; the design check found R 0.258."),
        Case("table.compare_profiles_of", 'show="contributions": dune by management (SIMPER)', "dune (vegan)",
             "real data",
             ours=dune + """
                 r = sdata.table(data).compare_profiles_of(species, for_each_group_in="Management",
                                                           show="contributions").as_pandas()
                 {"first average contribution": r["average contribution"][0], "first ratio": r["ratio"][0],
                  "first cumulative share": r["cumulative share"][0]}
             """,
             r=LOAD["dune"] + """
                 s <- summary(vegan::simper(x, e$dune.env$Management, permutations = 0))[[1]]
                 list(`first average contribution` = s$average[1], `first ratio` = s$ratio[1],
                      `first cumulative share` = s$cumsum[1])
             """, r_packages=("vegan",), r_tolerance=1e-9),
        Case("table.compare_profiles_of", 'measure="aitchison": mite by microtopography (PERMANOVA)',
             "mite (vegan)", "real data",
             ours=mite + """
                 r = sdata.table(data).compare_profiles_of(species, for_each_group_in="Topo",
                                                           measure="aitchison").as_pandas()
                 {"pseudo-F": r["statistic"][0], "R squared": r["R squared"][0], "p": r["p-value"][0]}
             """,
             r=LOAD["mite"] + "set.seed(1); " + GBM + """
                 a <- vegan::adonis2(vegan::vegdist(r, "aitchison") ~ factor(e$mite.env$Topo), permutations = 999)
                 list(`pseudo-F` = a$F[1], `R squared` = a$R2[1], p = a[1, 5])
             """, r_packages=("vegan", "zCompositions"), r_tolerance=1e-9),
        Case("table.find_distances_between_rows", 'measure="aitchison": mite, cores 1, 2 and 70',
             "mite (vegan)", "real data",
             ours=mite + """
                 r = sdata.table(data).find_distances_between_rows(columns=species, measure="aitchison").as_pandas()
                 {"1 to 2": r["2"][0], "1 to 70": r["70"][0]}
             """,
             r=LOAD["mite"] + GBM + """
                 d <- as.matrix(vegan::vegdist(r, "aitchison"))
                 list(`1 to 2` = d[1, 2], `1 to 70` = d[1, 70])
             """, r_packages=("vegan", "zCompositions"), r_tolerance=1e-9),
        # ---------------------------------------------------------------- clusters
        Case("table.add_clusters", 'how_many="automatic": dune, Bray-Curtis, average linkage', "dune (vegan)",
             "real data",
             ours=dune + """
                 r = sdata.table(data).add_clusters(columns=species, how_many="automatic", test_method="hierarchical",
                                                    measure="bray-curtis").as_pandas()
                 {"clusters": r["cluster"].max(), "size of cluster 1": (r["cluster"] == 1).sum()}
             """,
             r=LOAD["dune"] + """
                 d <- vegan::vegdist(x); h <- stats::hclust(d, "average")
                 w <- sapply(2:10, function(k) summary(cluster::silhouette(stats::cutree(h, k), d))$avg.width)
                 k <- (2:10)[which.max(w)]; g <- stats::cutree(h, k)
                 list(clusters = k, `size of cluster 1` = sum(g == g[1]))
             """, r_packages=("vegan", "cluster"), r_tolerance=0),
        Case("table.add_clusters", "measure=: dune, Bray-Curtis, average linkage, 3 clusters", "dune (vegan)",
             "real data",
             ours=dune + """
                 r = sdata.table(data).add_clusters(columns=species, how_many=3, test_method="hierarchical",
                                                    measure="bray-curtis", show="silhouette").as_pandas()
                 {"average silhouette width": r["silhouette width"].mean(), "width of row 1": r["silhouette width"][0]}
             """,
             r=LOAD["dune"] + """
                 d <- vegan::vegdist(x); s <- cluster::silhouette(stats::cutree(stats::hclust(d, "average"), 3), d)
                 list(`average silhouette width` = summary(s)$avg.width, `width of row 1` = s[1, 3])
             """, r_packages=("vegan", "cluster"), r_tolerance=1e-9,
             note="The design check found an average width of 0.286."),
        Case("draw_cluster_tree", "dune: Bray-Curtis, average linkage", "dune (vegan)", "real data",
             ours=dune + """
                 chart = sdata.table(data).start_chart()
                 chart.draw_cluster_tree(columns=species, measure="bray-curtis")
                 lines = chart._render().axes[0].get_lines()
                 {"top join": max(max(l.get_ydata()) for l in lines), "lowest join": min(max(l.get_ydata()) for l in lines)}
             """,
             r=LOAD["dune"] + """
                 h <- stats::hclust(vegan::vegdist(x), "average")
                 list(`top join` = max(h$height), `lowest join` = min(h$height))
             """, r_packages=("vegan",), r_tolerance=1e-9),
        # ---------------------------------------------------------------- discriminant and correspondence axes
        Case("table.add_axes_that_separate_groups", "crabs: four groups (colour form and sex) from five measurements",
             "crabs (MASS)", "real data",
             ours=_printed('table = sdata.table(data).add_axes_that_separate_groups(columns=["FL", "RW", "CL", "CW", '
                           '"BD"], for_each_group_in="kind")') + """
                 from simplydata.table.community_r import discriminant
                 shown = [float(v) for v in re.findall(r"LD\\d ([\\d.]+) %", text)]
                 found = discriminant(data[["FL", "RW", "CL", "CW", "BD"]].to_numpy(dtype=float), data["kind"].to_numpy())
                 assert all(abs(a - 100 * v) <= 0.05 + 1e-9 for a, v in zip(shown, found["trace"]))  # the printout
                 {"LD1 share of trace": found["trace"][0], "LD2 share of trace": found["trace"][1],
                  "LD3 share of trace": found["trace"][2],
                  "leave-one-out % correct": 100 * float(np.mean(found["loo"] == data["kind"].to_numpy())),
                  "LD1 row 1 size": abs(table.get_cell_at(row=1, column="LD1"))}
             """,
             r="""
                 d <- MASS::crabs; g <- paste(d$sp, d$sex); x <- as.matrix(d[, c("FL", "RW", "CL", "CW", "BD")])
                 f <- MASS::lda(x, g); cv <- MASS::lda(x, g, CV = TRUE)
                 share <- round(f$svd^2 / sum(f$svd^2), 4)  # as MASS:::print.lda prints them
                 list(`LD1 share of trace` = share[1], `LD2 share of trace` = share[2], `LD3 share of trace` = share[3],
                      `leave-one-out % correct` = 100 * mean(cv$class == g),
                      `LD1 row 1 size` = abs(predict(f)$x[1, 1]))
             """, r_packages=("MASS",), r_tolerance=1e-9,
             note="simplydata takes the shares of the trace from MASS's own print (4 decimals, as print.lda rounds "
                  "them), so R's side rounds svd^2 / sum(svd^2) the same way and they must agree exactly; the "
                  "leave-one-out share and the scores are compared unrounded. (Before, the check read the "
                  "one-decimal printout and allowed 0.4 %.) The design check found 0.686, 0.300 and 0.014, and 95 % "
                  "correct."),
        Case("table.add_correspondence_axes", "varespec: correspondence analysis (CA)",
             "varespec and varechem (vegan)", "published",
             ours=vare + _printed("table = sdata.table(data).add_correspondence_axes(columns=species)") + """
                 shares = [float(v) for v in re.findall(r"CA\\d ([\\d.]+) %", text)]
                 {"CA1 %": shares[0], "CA2 %": shares[1], "CA1 row 1 size": abs(table.as_pandas()["CA1"][0])}
             """,
             published={"CA1 %": (25.2, 0.05, oksanen), "CA2 %": (17.1, 0.05, oksanen)},
             r=LOAD["vare"] + """
                 m <- vegan::cca(x); e2 <- summary(vegan::eigenvals(m))
                 s <- vegan::scores(m, display = "sites", scaling = "sites", choices = 1)
                 list(`CA1 %` = round(100 * e2[2, 1], 1), `CA2 %` = round(100 * e2[2, 2], 1), `CA1 row 1 size` = abs(s[1, 1]))
             """, r_packages=("vegan",), r_tolerance=1e-9,
             note="The tutorial gives the eigenvalues (0.5249 and 0.3568 of 2.083); the printout gives their shares."),
        Case("table.add_correspondence_axes", "wg93: multiple correspondence analysis (MCA) of questions A to D",
             "wg93 (ca)", "published",
             ours=_printed('table = sdata.table(data).add_correspondence_axes(columns=["A", "B", "C", "D"])') + """
                 shares = [float(v) for v in re.findall(r"axis \\d ([\\d.]+) %", text)]
                 {"axis 1 %": shares[0], "axis 2 %": shares[1]}
             """,
             published={"axis 1 %": (44.9, 0.05, nenadic), "axis 2 %": (34.2, 0.05, nenadic)},
             r="""
                 e <- new.env(); utils::data("wg93", package = "ca", envir = e)
                 m <- ca::mjca(e$wg93[, 1:4], lambda = "adjusted")
                 list(`axis 1 %` = round(100 * m$inertia.e[1], 1), `axis 2 %` = round(100 * m$inertia.e[2], 1))
             """, r_packages=("ca",), r_tolerance=1e-9),
    ]


OURS_R = {"table.add_log_ratio_columns": ("zCompositions", "compositions"),
          "table.add_axes_that_separate_groups": ("MASS",),
          "table.add_clusters": ("vegan", "cluster")}


def add_to(namespace) -> None:
    """Add the S3c-1 datasets and cases to cases.py, and teach its load() the datasets read from R packages."""
    Dataset, Case = namespace["Dataset"], namespace["Case"]
    for d in _datasets(Dataset):
        namespace["DATASETS"][d.name] = d
    import dataclasses

    cases = []
    for c in _cases(Case):
        head = c.title.split(":")[0]
        option = head if "=" in head else ""
        needs = OURS_R.get(c.word, ("vegan",))
        if c.dataset == "wg93 (ca)":
            needs = ("ca",)
        if "aitchison" in option or (c.word == "table.add_log_ratio_columns" and "adding 1" not in option):
            needs = tuple(dict.fromkeys(needs + ("vegan", "zCompositions", "compositions")))
        cases.append(dataclasses.replace(c, ours_r=needs, option=option))
    namespace["CASES"].extend(cases)
    namespace.setdefault("R_DATA", {}).update({name: packages for name, (packages, _) in R_DATA_COMMUNITIES.items()})
    plain_load = namespace["load"]

    def load(name: str) -> pd.DataFrame:
        if name in R_DATA_COMMUNITIES:
            from simplydata._r import need_r, r_call

            packages, code = R_DATA_COMMUNITIES[name]
            need_r(packages, f"the {name} data")
            found = r_call(code, what=f"the {name} data")
            return pd.DataFrame({k: (np.asarray(v, dtype=float) if np.asarray(v).dtype.kind in "iuf" else list(v))
                                 for k, v in found.items()})
        return plain_load(name)

    namespace["load"] = load
