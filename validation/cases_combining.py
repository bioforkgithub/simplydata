"""The reliability study for phase S3b-1, combining studies: table.combine_studies (counts, estimates with their
intervals, averages, events and time, correlations; REML with Hartung-Knapp, DerSimonian-Laird, Paule-Mandel, a
common effect, Mantel-Haenszel and Peto; subgroups and meta-regression) and chart.draw_funnel_plot.

cases.py loads this file at its end and calls add_to(), which adds the datasets and cases below to its own DATASETS
and CASES and teaches load() the datasets read from R metadat (not stored here: their licence is the package's, GPL,
so they are read where they are published; the R package metafor installs metadat).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# datasets read from an R package at run time: name -> (R packages, R code giving a named list of columns)
R_DATA_COMBINING = {
    "BCG trials (metadat)": (("metadat",), (
        "d <- metadat::dat.bcg; list(trial = paste(d$author, d$year), tpos = d$tpos, tneg = d$tneg, cpos = d$cpos, "
        "cneg = d$cneg, vaccinated = d$tpos + d$tneg, unvaccinated = d$cpos + d$cneg, ablat = d$ablat, "
        "alloc = d$alloc)")),
    "passive smoking (metadat)": (("metadat",), (
        "d <- metadat::dat.hackshaw1998; list(study = paste(d$author, d$year), `odds ratio` = d$or, "
        "`odds ratio 95 % CI low` = d$or.lb, `odds ratio 95 % CI high` = d$or.ub)")),
    "Normand 1999 (metadat)": (("metadat",), (
        "d <- metadat::dat.normand1999; list(setting = d$source, m1i = d$m1i, sd1i = d$sd1i, n1i = d$n1i, "
        "m2i = d$m2i, sd2i = d$sd2i, n2i = d$n2i)")),
    "Curtis 1998 (metadat)": (("metadat",), (
        "d <- metadat::dat.curtis1998; list(id = as.character(d$id), m1i = d$m1i, sd1i = d$sd1i, n1i = d$n1i, "
        "m2i = d$m2i, sd2i = d$sd2i, n2i = d$n2i)")),
    "Hart 1999 (metadat)": (("metadat",), (
        "d <- metadat::dat.hart1999; list(trial = as.character(d$trial), x1i = d$x1i, t1i = d$t1i, x2i = d$x2i, "
        "t2i = d$t2i)")),
    "McDaniel 1994 (metadat)": (("metadat",), (
        "d <- metadat::dat.mcdaniel1994; list(study = as.character(d$study), ri = d$ri, ni = d$ni)")),
}

BCG = 'names="trial", events=["tpos", "cpos"], out_of=["vaccinated", "unvaccinated"]'
RR = ("e <- metafor::escalc(measure = 'RR', ai = tpos, bi = tneg, ci = cpos, di = cneg); ")


def _datasets(Dataset):
    metadat = ("The numbers are facts published in the paper; the metadat copy is GPL (>= 2). Read here from metadat "
               "(installed with metafor), so it needs R; the practice tables bcg and passive_smoking hold the same "
               "published numbers.")
    return [
        Dataset("BCG trials (metadat)", "",
                "13 trials of the BCG vaccine against tuberculosis: cases among the vaccinated and the unvaccinated, "
                "the absolute latitude of the place and how people were put into the groups",
                "Colditz, G. A. et al. (1994). Efficacy of BCG vaccine in the prevention of tuberculosis: "
                "meta-analysis of the published literature. JAMA 271, 698-702. Analysed in Viechtbauer, W. (2010). "
                "Conducting meta-analyses in R with the metafor package. Journal of Statistical Software 36(3), "
                "1-48 (CC BY 3.0). Shipped with the R package metadat (dat.bcg); a copy is the practice table bcg.",
                metadat, "https://doi.org/10.18637/jss.v036.i03"),
        Dataset("passive smoking (metadat)", "",
                "37 studies of lung cancer in non-smoking women whose husbands smoked: the odds ratio of each study "
                "with its 95 % interval",
                "Hackshaw, A. K., Law, M. R. & Wald, N. J. (1997). The accumulated evidence on lung cancer and "
                "environmental tobacco smoke. BMJ 315, 980-988 (pooled excess risk 24 %, 95 % CI 13 % to 36 %). "
                "Shipped with the R package metadat (dat.hackshaw1998); a copy is the practice table passive_smoking.",
                metadat, "https://doi.org/10.1136/bmj.315.7114.980"),
        Dataset("Normand 1999 (metadat)", "",
                "9 trials of specialist stroke rehabilitation: average length of hospital stay (days), its standard "
                "deviation and the patients in each group",
                "Normand, S.-L. T. (1999). Meta-analysis: formulating, evaluating, combining, and reporting. "
                "Statistics in Medicine 18, 321-359. Shipped with the R package metadat (dat.normand1999).",
                metadat, "https://cran.r-project.org/package=metadat"),
        Dataset("Curtis 1998 (metadat)", "",
                "102 experiments on the growth of woody plants under raised and ambient CO2: average biomass, its "
                "standard deviation and the plants in each group",
                "Curtis, P. S. & Wang, X. (1998). A meta-analysis of elevated CO2 effects on woody plant mass, form, "
                "and physiology. Oecologia 113, 299-313; the log response ratio of Hedges, L. V., Gurevitch, J. & "
                "Curtis, P. S. (1999). Ecology 80, 1150-1156. Shipped with the R package metadat (dat.curtis1998).",
                metadat, "https://cran.r-project.org/package=metadat"),
        Dataset("Hart 1999 (metadat)", "",
                "6 trials of warfarin against placebo in atrial fibrillation: strokes and patient-years in each group",
                "Hart, R. G., Benavente, O., McBride, R. & Pearce, L. A. (1999). Antithrombotic therapy to prevent "
                "stroke in patients with atrial fibrillation: a meta-analysis. Annals of Internal Medicine 131, "
                "492-501. Shipped with the R package metadat (dat.hart1999).",
                metadat, "https://cran.r-project.org/package=metadat"),
        Dataset("McDaniel 1994 (metadat)", "",
                "160 studies of the correlation between employment interview ratings and job performance, with the "
                "number of people in each",
                "McDaniel, M. A., Whetzel, D. L., Schmidt, F. L. & Maurer, S. D. (1994). The validity of employment "
                "interviews: a comprehensive review and meta-analysis. Journal of Applied Psychology 79, 599-616. "
                "Shipped with the R package metadat (dat.mcdaniel1994).",
                metadat, "https://cran.r-project.org/package=metadat"),
    ]


def _cases(Case):
    combined = """
        r = sdata.table(data).combine_studies({call}).as_pandas()
        c = r[r["row kind"] == "combined"].iloc[0]
        {{"estimate": c["estimate"], "low": c["estimate 95 % CI low"], "high": c["estimate 95 % CI high"],
         "p-value": c["p-value"]{more}}}
    """
    viechtbauer = "Viechtbauer (2010), JSS 36(3)"
    return [
        Case("table.combine_studies", "BCG trials: risk ratios, random effects (REML) with Hartung-Knapp",
             "BCG trials (metadat)", "published",
             ours=combined.format(call=BCG, more=', "log estimate": np.log(c["estimate"]), "tau squared": c["tau '
                                                 'squared"], "I squared %": c["I squared %"], "Q": c["Q"]'),
             published={"log estimate": (-0.7145, 5e-5, viechtbauer), "tau squared": (0.3132, 5e-5, viechtbauer),
                        "I squared %": (92.22, 5e-3, viechtbauer), "Q": (152.2330, 5e-5, viechtbauer)},
             r=RR + """
                 f <- metafor::rma(yi, vi, data = e, method = "REML", test = "adhoc")
                 p <- predict(f, transf = exp)
                 list(estimate = p$pred, low = p$ci.lb, high = p$ci.ub, `p-value` = f$pval,
                      `tau squared` = f$tau2, `I squared %` = f$I2, Q = f$QE)
             """, r_packages=("metafor",), r_tolerance=1e-8,
             note="The published numbers are the estimate, tau-squared, I-squared and Q, which Hartung-Knapp does not "
                  "change; its interval is checked against R metafor itself."),
        Case("table.combine_studies", "interval_by=: BCG trials, the normal (z) interval", "BCG trials (metadat)",
             "published",
             ours=combined.format(call=BCG + ', interval_by="normal"',
                                  more=', "log low": np.log(c["estimate 95 % CI low"]), '
                                       '"log high": np.log(c["estimate 95 % CI high"])'),
             published={"log low": (-1.0669, 5e-5, viechtbauer), "log high": (-0.3622, 5e-5, viechtbauer)},
             r=RR + """
                 f <- metafor::rma(yi, vi, data = e, method = "REML", test = "z")
                 p <- predict(f, transf = exp)
                 list(estimate = p$pred, low = p$ci.lb, high = p$ci.ub, `p-value` = f$pval)
             """, r_packages=("metafor",), r_tolerance=1e-8),
        Case("table.combine_studies", "test_method=: BCG trials, DerSimonian-Laird", "BCG trials (metadat)", "published",
             ours=combined.format(call=BCG + ', test_method="DerSimonian-Laird", interval_by="normal"',
                                  more=', "tau squared": c["tau squared"]'),
             published={"tau squared": (0.3088, 5e-5, viechtbauer)},
             parent="""
                 from statsmodels.stats.meta_analysis import combine_effects
                 a, b, c_, d = data["tpos"], data["tneg"], data["cpos"], data["cneg"]
                 y = np.log((a / (a + b)) / (c_ / (c_ + d)))
                 v = 1 / a - 1 / (a + b) + 1 / c_ - 1 / (c_ + d)
                 r = combine_effects(y, v, method_re="dl").summary_frame()
                 {"estimate": np.exp(r.loc["random effect", "eff"]), "low": np.exp(r.loc["random effect", "ci_low"]),
                  "high": np.exp(r.loc["random effect", "ci_upp"])}
             """, parent_label="statsmodels combine_effects (DerSimonian-Laird)", parent_tolerance=1e-8,
             r=RR + """
                 f <- metafor::rma(yi, vi, data = e, method = "DL", test = "z")
                 p <- predict(f, transf = exp)
                 list(estimate = p$pred, low = p$ci.lb, high = p$ci.ub, `p-value` = f$pval, `tau squared` = f$tau2)
             """, r_packages=("metafor",), r_tolerance=1e-8,
             note="The study's log risk ratios are written out for statsmodels (the parent check), which has no "
                  "escalc; simplydata itself takes them from R metafor."),
        Case("table.combine_studies", "test_method=: BCG trials, Paule-Mandel", "BCG trials (metadat)", "real data",
             ours=combined.format(call=BCG + ', test_method="Paule-Mandel"', more=', "tau squared": c["tau squared"]'),
             r=RR + """
                 f <- metafor::rma(yi, vi, data = e, method = "PM", test = "adhoc")
                 p <- predict(f, transf = exp)
                 list(estimate = p$pred, low = p$ci.lb, high = p$ci.ub, `p-value` = f$pval, `tau squared` = f$tau2)
             """, r_packages=("metafor",), r_tolerance=1e-6,
             note="Paule-Mandel is found by iteration, so the numbers agree to metafor's own tolerance."),
        Case("table.combine_studies", "test_method=: BCG trials, a common effect", "BCG trials (metadat)", "real data",
             ours=combined.format(call=BCG + ', test_method="common effect"', more=""),
             r=RR + """
                 f <- metafor::rma(yi, vi, data = e, method = "EE")
                 p <- predict(f, transf = exp)
                 list(estimate = p$pred, low = p$ci.lb, high = p$ci.ub, `p-value` = f$pval)
             """, r_packages=("metafor",), r_tolerance=1e-8),
        Case("table.combine_studies", 'test_method="Mantel-Haenszel": BCG trials, risk ratios', "BCG trials (metadat)",
             "real data",
             ours=combined.format(call=BCG + ', test_method="Mantel-Haenszel"', more=""),
             parent="""
                 from statsmodels.stats.contingency_tables import StratifiedTable
                 tables = [np.array([[a, b], [c_, d]]) for a, b, c_, d in
                           zip(data["tpos"], data["tneg"], data["cpos"], data["cneg"])]
                 {"estimate": StratifiedTable(tables).riskratio_pooled}
             """, parent_label="statsmodels StratifiedTable (riskratio_pooled)", parent_tolerance=1e-8,
             r="""
                 f <- metafor::rma.mh(ai = tpos, bi = tneg, ci = cpos, di = cneg, measure = "RR")
                 p <- predict(f, transf = exp)
                 list(estimate = p$pred, low = p$ci.lb, high = p$ci.ub, `p-value` = f$pval)
             """, r_packages=("metafor",), r_tolerance=1e-8),
        Case("table.combine_studies", 'test_method="Peto": BCG trials, odds ratios', "BCG trials (metadat)", "real data",
             ours=combined.format(call=BCG + ', test_method="Peto"', more=""),
             r="""
                 f <- metafor::rma.peto(ai = tpos, bi = tneg, ci = cpos, di = cneg)
                 p <- predict(f, transf = exp)
                 list(estimate = p$pred, low = p$ci.lb, high = p$ci.ub, `p-value` = f$pval)
             """, r_packages=("metafor",), r_tolerance=1e-8),
        Case("table.combine_studies", "for_each_group_in=: BCG trials by how people were allocated",
             "BCG trials (metadat)", "real data",
             ours="""
                 r = sdata.table(data).combine_studies(names="trial", events=["tpos", "cpos"],
                                                       out_of=["vaccinated", "unvaccinated"],
                                                       for_each_group_in="alloc").as_pandas()
                 d = r[r["row kind"] == "subgroup difference"].iloc[0]
                 s = r[(r["row kind"] == "combined in subgroup") & (r["subgroup"] == "random")].iloc[0]
                 {"Q between": d["Q"], "p between": d["p-value"], "random": s["estimate"], "random tau2": s["tau squared"]}
             """,
             r=RR + """
                 g <- sort(unique(alloc))
                 f <- lapply(g, function(x) metafor::rma(yi, vi, data = e, subset = alloc == x, test = "adhoc"))
                 z <- lapply(g, function(x) metafor::rma(yi, vi, data = e, subset = alloc == x, test = "z"))
                 b <- sapply(z, function(m) m$b[1]); s <- sapply(z, function(m) m$se)
                 q <- metafor::rma(b, sei = s, mods = ~ factor(g), method = "EE")
                 list(`Q between` = q$QM, `p between` = q$QMp, random = exp(f[[2]]$b[1]), `random tau2` = f[[2]]$tau2)
             """, r_packages=("metafor",), r_tolerance=1e-8,
             note="Each subgroup has its own between-study variance; the test of their difference uses each "
                  "subgroup's estimate with its normal (z) standard error, as RevMan and R meta do (the next case "
                  "checks it against meta), not metafor's rma(mods = ~ alloc), which shares one variance."),
        Case("table.combine_studies", "using=: BCG trials, meta-regression on latitude", "BCG trials (metadat)",
             "real data",
             ours="""
                 r = sdata.table(data).combine_studies(names="trial", events=["tpos", "cpos"],
                                                       out_of=["vaccinated", "unvaccinated"], using=["ablat"]).as_pandas()
                 s = r[r["study"] == 'per 1 more "ablat"'].iloc[0]
                 {"slope": s["estimate"], "low": s["estimate 95 % CI low"], "p-value": s["p-value"]}
             """,
             r=RR + """
                 f <- metafor::rma(yi, vi, mods = ~ ablat, data = e, method = "REML", test = "adhoc")
                 list(slope = f$b[2], low = f$ci.lb[2], `p-value` = f$pval[2])
             """, r_packages=("metafor",), r_tolerance=1e-8),
        Case("table.combine_studies", "estimates=: passive smoking, odds ratios with their 95 % intervals",
             "passive smoking (metadat)", "published",
             ours="""
                 r = sdata.table(data).combine_studies(names="study", estimates="odds ratio",
                                                       test_method="DerSimonian-Laird", interval_by="normal").as_pandas()
                 c = r[r["row kind"] == "combined"].iloc[0]
                 {"estimate": c["estimate"], "low": c["estimate 95 % CI low"], "high": c["estimate 95 % CI high"]}
             """,
             published={"estimate": (1.24, 0.005, "Hackshaw et al. (1997), BMJ 315:980"),
                        "low": (1.13, 0.005, "Hackshaw et al. (1997), BMJ 315:980"),
                        "high": (1.36, 0.005, "Hackshaw et al. (1997), BMJ 315:980")},
             r="""
                 e <- metafor::conv.wald(out = `odds ratio`, ci.lb = `odds ratio 95 % CI low`,
                                         ci.ub = `odds ratio 95 % CI high`, transf = log)
                 p <- predict(metafor::rma(yi, vi, data = e, method = "DL", test = "z"), transf = exp)
                 list(estimate = p$pred, low = p$ci.lb, high = p$ci.ub)
             """, r_packages=("metafor",), r_tolerance=1e-8,
             note="The paper's excess risk of 24 % (95 % CI 13 % to 36 %) is the pooled odds ratio 1.24 (1.13 to 1.36)."),
        Case("table.combine_studies", "averages=: Normand 1999, standardised differences (Hedges' g)",
             "Normand 1999 (metadat)", "real data",
             ours="""
                 r = sdata.table(data).combine_studies(names="setting", averages=["m1i", "m2i"],
                                                       standard_deviations=["sd1i", "sd2i"],
                                                       counts=["n1i", "n2i"]).as_pandas()
                 c = r[r["row kind"] == "combined"].iloc[0]
                 {"estimate": c["estimate"], "low": c["estimate 95 % CI low"], "first study": r["estimate"].iloc[0]}
             """,
             r="""
                 e <- metafor::escalc(measure = "SMD", m1i = m1i, sd1i = sd1i, n1i = n1i, m2i = m2i, sd2i = sd2i,
                                      n2i = n2i)
                 f <- metafor::rma(yi, vi, data = e, test = "adhoc")
                 list(estimate = f$b[1], low = f$ci.lb, `first study` = e$yi[1])
             """, r_packages=("metafor",), r_tolerance=1e-8,
             note="metafor's Hedges' g (exact correction, large-sample variance) is the reference; statsmodels' "
                  "effectsize_smd uses an approximate correction and another variance, so it differs slightly."),
        Case("table.combine_studies", 'show="ratios of averages": Curtis 1998, the log response ratio of plant mass '
                                      "under raised CO2", "Curtis 1998 (metadat)", "real data",
             ours="""
                 r = sdata.table(data).combine_studies(names="id", averages=["m1i", "m2i"],
                                                       standard_deviations=["sd1i", "sd2i"], counts=["n1i", "n2i"],
                                                       show="ratios of averages").as_pandas()
                 c = r[r["row kind"] == "combined"].iloc[0]
                 {"estimate": c["estimate"], "tau squared": c["tau squared"]}
             """,
             r="""
                 e <- metafor::escalc(measure = "ROM", m1i = m1i, sd1i = sd1i, n1i = n1i, m2i = m2i, sd2i = sd2i,
                                      n2i = n2i)
                 f <- metafor::rma(yi, vi, data = e, test = "adhoc")
                 list(estimate = exp(f$b[1]), `tau squared` = f$tau2)
             """, r_packages=("metafor",), r_tolerance=1e-6),
        Case("table.combine_studies", "time=: Hart 1999, rate ratios of stroke with warfarin",
             "Hart 1999 (metadat)", "real data",
             ours="""
                 r = sdata.table(data).combine_studies(names="trial", events=["x1i", "x2i"],
                                                       time=["t1i", "t2i"]).as_pandas()
                 c = r[r["row kind"] == "combined"].iloc[0]
                 {"estimate": c["estimate"], "low": c["estimate 95 % CI low"], "high": c["estimate 95 % CI high"]}
             """,
             r="""
                 e <- metafor::escalc(measure = "IRR", x1i = x1i, t1i = t1i, x2i = x2i, t2i = t2i)
                 p <- predict(metafor::rma(yi, vi, data = e, test = "adhoc"), transf = exp)
                 list(estimate = p$pred, low = p$ci.lb, high = p$ci.ub)
             """, r_packages=("metafor",), r_tolerance=1e-8),
        Case("table.combine_studies", "correlations=: McDaniel 1994, interview ratings and job performance",
             "McDaniel 1994 (metadat)", "real data",
             ours="""
                 r = sdata.table(data).combine_studies(names="study", correlations="ri", counts="ni").as_pandas()
                 c = r[r["row kind"] == "combined"].iloc[0]
                 {"estimate": c["estimate"], "low": c["estimate 95 % CI low"]}
             """,
             r="""
                 e <- metafor::escalc(measure = "ZCOR", ri = ri, ni = ni)
                 p <- predict(metafor::rma(yi, vi, data = e, test = "adhoc"), transf = metafor::transf.ztor)
                 list(estimate = p$pred, low = p$ci.lb)
             """, r_packages=("metafor",), r_tolerance=1e-8),
        Case("table.combine_studies", "BCG trials: Peters' test of small-study effects (risk ratios from counts)",
             "BCG trials (metadat)", "real data",
             ours="""
                 r = sdata.table(data).combine_studies(names="trial", events=["tpos", "cpos"],
                                                       out_of=["vaccinated", "unvaccinated"]).as_pandas()
                 s = r[r["row kind"] == "small-study effects"].iloc[0]
                 {"t": s["estimate"], "p-value": s["p-value"]}
             """,
             r="""
                 m <- meta::metabin(tpos, tpos + tneg, cpos, cpos + cneg, sm = "RR")
                 b <- meta::metabias(m, method.bias = "Peters", k.min = 10)
                 list(t = unname(b$statistic), `p-value` = b$pval)
             """, r_packages=("meta",), r_tolerance=1e-6,
             note="R meta's Peters test (Peters et al. 2006), a second package: simplydata runs metafor::regtest() "
                  "with Peters' weights and 1 / n as the predictor."),
        Case("table.combine_studies", "passive smoking: Egger's test and trim and fill", "passive smoking (metadat)",
             "real data",
             ours="""
                 r = sdata.table(data).combine_studies(names="study", estimates="odds ratio").as_pandas()
                 s = r[r["row kind"] == "small-study effects"].iloc[0]
                 f = r[r["row kind"] == "trim and fill"].iloc[0]
                 {"t": s["estimate"], "p-value": s["p-value"], "studies added": f["studies added"],
                  "filled odds ratio": f["estimate"]}
             """,
             r="""
                 e <- metafor::conv.wald(out = `odds ratio`, ci.lb = `odds ratio 95 % CI low`,
                                         ci.ub = `odds ratio 95 % CI high`, transf = log)
                 m <- meta::metagen(e$yi, sqrt(e$vi), sm = "OR")
                 b <- meta::metabias(m, method.bias = "Egger", k.min = 10)
                 f <- metafor::trimfill(metafor::rma(yi, vi, data = e, test = "adhoc"))
                 list(t = unname(b$statistic), `p-value` = b$pval, `studies added` = f$k0,
                      `filled odds ratio` = exp(f$b[1]))
             """, r_packages=("meta", "metafor"), r_tolerance=1e-6,
             note="Egger's test from R meta (metabias, method \"Egger\"), a second package; trim and fill from "
                  "metafor (estimator L0, side estimated)."),
        Case("table.combine_studies", "for_each_group_in=: BCG trials by allocation, against R meta's test of "
                                      "subgroup differences", "BCG trials (metadat)", "real data",
             ours="""
                 r = sdata.table(data).combine_studies(names="trial", events=["tpos", "cpos"],
                                                       out_of=["vaccinated", "unvaccinated"],
                                                       for_each_group_in="alloc").as_pandas()
                 d = r[r["row kind"] == "subgroup difference"].iloc[0]
                 {"Q between": d["Q"], "p between": d["p-value"]}
             """,
             r="""
                 m <- meta::metabin(tpos, tpos + tneg, cpos, cpos + cneg, sm = "RR", method = "Inverse",
                                    method.tau = "REML", subgroup = alloc)
                 list(`Q between` = m$Q.b.random, `p between` = m$pval.Q.b.random)
             """, r_packages=("meta",), r_tolerance=1e-4,
             note="R meta (each subgroup its own between-study variance, REML) is a second package; meta's REML stops "
                  "at its own tolerance, so the numbers agree to about 1e-5."),
        Case("draw_funnel_plot", "passive smoking: each study's odds ratio and standard error",
             "passive smoking (metadat)", "real data",
             ours="""
                 r = sdata.table(data).combine_studies(names="study", estimates="odds ratio")
                 ax = r.start_chart().draw_funnel_plot(x="estimate", y="standard error")._render().axes[0]
                 dots = ax.collections[0].get_offsets()
                 {"first odds ratio": dots[0][0], "first standard error": dots[0][1], "last standard error": dots[-1][1]}
             """,
             r="""
                 e <- metafor::conv.wald(out = `odds ratio`, ci.lb = `odds ratio 95 % CI low`,
                                         ci.ub = `odds ratio 95 % CI high`, transf = log)
                 list(`first odds ratio` = exp(e$yi[1]), `first standard error` = sqrt(e$vi[1]),
                      `last standard error` = sqrt(e$vi[37]))
             """, r_packages=("metafor",), r_tolerance=1e-8),
    ]


def add_to(namespace) -> None:
    """Add the S3b-1 datasets and cases to cases.py, and teach its load() the datasets read from R metadat."""
    Dataset, Case = namespace["Dataset"], namespace["Case"]
    for d in _datasets(Dataset):
        namespace["DATASETS"][d.name] = d
    import dataclasses

    cases = []
    for c in _cases(Case):
        head = c.title.split(":")[0]
        option = head if "=" in head else ""
        cases.append(dataclasses.replace(c, ours_r=("metafor",), option=option))
    namespace["CASES"].extend(cases)
    namespace.setdefault("R_DATA", {}).update({name: packages for name, (packages, _) in R_DATA_COMBINING.items()})
    plain_load = namespace["load"]

    def load(name: str) -> pd.DataFrame:
        if name in R_DATA_COMBINING:
            from simplydata._r import need_r, r_call

            packages, code = R_DATA_COMBINING[name]
            need_r(packages, f"the {name} data")  # checked, not attached: the code names its package
            found = r_call(code, what=f"the {name} data")
            return pd.DataFrame({k: (np.asarray(v, dtype=float) if np.asarray(v).dtype.kind in "iuf" else list(v))
                                 for k, v in found.items()})
        return plain_load(name)

    namespace["load"] = load
