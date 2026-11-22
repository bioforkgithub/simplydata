"""The reliability study for phase S3d-1, planning an experiment and survey answers: randomisation lists
(sdata.make_random_assignments, R blockrand), design tables (sdata.make_design_table, R agricolae), stratified random
rows (keep_random_rows(for_each_group_in=, percent=)), patterns of empty cells (count_empty_cells_in(show="patterns")),
answers on a scale (count_each(columns=, in_order=), chart.draw_answer_bars) and the survey words
(table.use_survey_design, then find_average_of, find_total_of, find_median_of, find_percentile_of,
find_percent_of_rows_where, count_rows, explain, compare_averages_of and compare_counts_of).

cases.py loads this file at its end and calls add_to(), which adds the datasets and cases below to its own DATASETS
and CASES.

Published answers: Lumley (2010) and the R survey help for the api samples (the stratified mean 662.29 with standard
error 9.41, the total enrolment 3,687,178 with 114,642, the one-stage cluster mean 644.17 with 23.54, and 197
degrees of freedom: 200 schools in 3 strata); van Buuren & Groothuis-Oudshoorn (2011) for the patterns of empty cells
in nhanes (13, 3, 1, 1 and 7 rows); Heiberger & Robbins (2014) for the answers of the professional challenges survey;
the definition of permuted blocks (every block holds every group equally often; Schulz & Grimes 2002) and Yates'
standard order of a 2 x 2 x 2 factorial (Montgomery, Design and Analysis of Experiments: (1), a, b, ab, c, ac, bc,
abc). The other numbers are checked against R (survey, blockrand, agricolae, base R) and pandas: the packages
simplydata runs, or base R by definition.
"""

from __future__ import annotations

import textwrap

LUMLEY = "Lumley (2010), Complex Surveys, and the R survey help (api)"
STRAT = 'data.frame(stype, pw, fpc, api00, enroll, meals, ell, sch = as.numeric(sch.wide == "Yes"), awards)'
STRAT_R = f"d <- survey::svydesign(ids = ~1, strata = ~stype, weights = ~pw, fpc = ~fpc, data = {STRAT})\n"
OURS_STRAT = """
    t = sdata.table(data)
    t.use_survey_design(weights="pw", strata="stype", population_sizes="fpc")
"""
LEVELS = '["strongly_disagree", "disagree", "no_opinion", "agree", "strongly_agree"]'
PROF = """
    answers = ["strongly_disagree", "disagree", "no_opinion", "agree", "strongly_agree"]
    first = data.iloc[0]
    rows = pd.DataFrame({"all": [a for a in answers for _ in range(int(first[a]))]})
"""


def _join(*parts) -> str:
    return "\n".join(textwrap.dedent(part).strip("\n") for part in parts)


def _datasets(Dataset):
    return [
        Dataset("api stratified sample (survey)", "apistrat.csv",
                "200 California schools sampled at random within school type (100 elementary, 50 middle, 50 high): "
                "the Academic Performance Index of 2000 and 1999, enrolment, free meals, English learners, the "
                "sampling weight (pw) and the number of schools of each type (fpc)",
                "California Department of Education, Academic Performance Index 2000; the stratified sample of R's "
                "survey package (apistrat; Lumley, T. (2010). Complex Surveys: A Guide to Analysis Using R. Wiley).",
                "Public data of the California Department of Education; the survey package copy is GPL-2 | GPL-3. "
                "Columns stored unchanged.",
                "https://cran.r-project.org/package=survey"),
        Dataset("api cluster sample (survey)", "apiclus1.csv",
                "183 California schools in 15 school districts sampled at random (a one-stage cluster sample): the "
                "Academic Performance Index of 2000, enrolment, the weight (pw) and the number of districts (fpc)",
                "California Department of Education, Academic Performance Index 2000; R's survey package (apiclus1; "
                "Lumley 2010).",
                "Public data of the California Department of Education; the survey package copy is GPL-2 | GPL-3.",
                "https://cran.r-project.org/package=survey"),
        Dataset("nhanes (mice)", "nhanes.csv",
                "25 people of the US National Health and Nutrition Examination Survey: age group, body mass index, "
                "hypertension and cholesterol, with empty cells",
                "Schafer, J. L. (1997). Analysis of Incomplete Multivariate Data. Chapman & Hall, p. 237; the nhanes "
                "data of R mice and its patterns in van Buuren, S. & Groothuis-Oudshoorn, K. (2011). mice: "
                "Multivariate Imputation by Chained Equations in R. Journal of Statistical Software 45(3).",
                "A US Government survey (public domain); the mice copy is GPL-2 | GPL-3.",
                "https://doi.org/10.18637/jss.v045.i03"),
        Dataset("professional challenges (HH)", "prof_chal.csv",
                "565 answers to a survey question on professional challenges, from strongly disagree to strongly "
                "agree, in total and by employment sector, race, gender and more (counts of each answer)",
                "Heiberger, R. M. & Robbins, N. B. (2014). Design of Diverging Stacked Bar Charts for Likert Scales "
                "and Other Applications. Journal of Statistical Software 57(5); R HH (ProfChal).",
                "The JSS article is CC BY; the HH copy is GPL (>= 2). Counts stored unchanged.",
                "https://doi.org/10.18637/jss.v057.i05"),
        Dataset("designs (no data)", "",
                "no data: a randomisation list and a design table are made, and their published properties checked "
                "(blocks hold every group equally often; Yates' standard order)",
                "Schulz, K. F. & Grimes, D. A. (2002). Generation of allocation sequences in randomised trials: "
                "chance, not choice. The Lancet 359, 515-519; Montgomery, D. C. (2017). Design and Analysis of "
                "Experiments, 9th ed. Wiley, the standard order of a 2^k design.",
                "No data stored (facts of the methods).", "https://doi.org/10.1016/S0140-6736(02)07683-3"),
    ]


def _survey_case(Case, word, title, ours, published=None, r="", tolerance=1e-9, dataset="api stratified sample (survey)"):
    return Case(word, title, dataset, "published" if published else "real data", ours=ours,
                published=published or {}, r=r, r_packages=("survey",), r_tolerance=tolerance,
                option="after use_survey_design()", ours_r=("survey",))


def _cases(Case):
    return [
        # ---------------------------------------------------------------- V03: randomisation lists
        Case("sdata.make_random_assignments", "permuted blocks: every block holds both groups equally often",
             "designs (no data)", "published",
             ours="""
                 t = sdata.make_random_assignments(how_many=60, groups=["A", "B"], in_blocks_of=[4, 6],
                                                   for_each_of=["Bergen", "Oslo"], with_seed=1).as_pandas()
                 counts = t.groupby(["list", "block", "group"]).size().unstack()
                 {"largest imbalance within a block": float((counts["A"] - counts["B"]).abs().max()),
                  "first group (A = 1)": float(t["group"].iloc[0] == "A"),
                  "places in the first list": float((t["list"] == "Bergen").sum())}
             """,
             published={"largest imbalance within a block": (0.0, 0.0, "exact")},
             r="""
                 set.seed(1, kind = "Mersenne-Twister", normal.kind = "Inversion", sample.kind = "Rejection")
                 b <- blockrand::blockrand(n = 60, num.levels = 2, levels = c("A", "B"), block.sizes = c(2, 3),
                                           stratum = "Bergen")
                 list(`first group (A = 1)` = as.numeric(b$treatment[1] == "A"),
                      `places in the first list` = nrow(b))
             """, r_packages=("blockrand",), r_tolerance=0, ours_r=("blockrand",),
             note="Schulz & Grimes (2002): a permuted block holds every group equally often; R blockrand gives the "
                  "same list for the same seed."),
        # ---------------------------------------------------------------- V04 / V06: design tables
        Case("sdata.make_design_table", "Yates' standard order of a 2 x 2 x 2 factorial", "designs (no data)",
             "published",
             ours="""
                 t = sdata.make_design_table({"a": [0, 1], "b": [0, 1], "c": [0, 1]}, repeats=2, with_seed=1).as_pandas()
                 row = {int(k): g.iloc[0] for k, g in t.groupby("standard order")}
                 {"standard order of ab": float(next(k for k, r in row.items() if (r.a, r.b, r.c) == (1, 1, 0))),
                  "standard order of c": float(next(k for k, r in row.items() if (r.a, r.b, r.c) == (0, 0, 1))),
                  "plots": float(len(t)), "first plot's a": float(t["a"].iloc[0])}
             """,
             published={"standard order of ab": (4.0, 0.0, "exact"), "standard order of c": (5.0, 0.0, "exact"),
                        "plots": (16.0, 0.0, "exact")},
             r="""
                 d <- agricolae::design.ab(c(2, 2, 2), r = 2, design = "crd", serie = 0, seed = 1,
                                           kinds = "Mersenne-Twister")
                 list(`first plot's a` = as.numeric(as.character(d$book$A[1])) - 1, plots = nrow(d$book))
             """, r_packages=("agricolae",), r_tolerance=0, ours_r=("agricolae",),
             note="Montgomery (2017): (1), a, b, ab, c, ac, bc, abc, the order of R expand.grid()."),
        Case("sdata.make_design_table", 'of_kind="randomised blocks": each block holds every combination once',
             "designs (no data)", "published",
             ours="""
                 t = sdata.make_design_table({"a": [0, 1], "b": [0, 1]}, repeats=4, of_kind="randomised blocks",
                                             with_seed=3).as_pandas()
                 {"largest count of a combination in a block": float(t.groupby(["block", "a", "b"]).size().max()),
                  "smallest count of a combination in a block": float(t.groupby(["block", "a", "b"]).size().min()),
                  "first plot's b": float(t["b"].iloc[0])}
             """,
             published={"largest count of a combination in a block": (1.0, 0.0, "exact"),
                        "smallest count of a combination in a block": (1.0, 0.0, "exact")},
             r="""
                 d <- agricolae::design.ab(c(2, 2), r = 4, design = "rcbd", serie = 0, seed = 3,
                                           kinds = "Mersenne-Twister")
                 list(`first plot's b` = as.numeric(as.character(d$book$B[1])) - 1)
             """, r_packages=("agricolae",), r_tolerance=0, ours_r=("agricolae",),
             option='of_kind="randomised blocks"'),
        Case("sdata.make_design_table", 'of_kind="latin square": each level once in every row and column',
             "designs (no data)", "published",
             ours="""
                 t = sdata.make_design_table({"v": ["A", "B", "C", "D"]}, of_kind="latin square",
                                             with_seed=2).as_pandas()
                 {"levels in every row": float(t.groupby("row")["v"].nunique().min()),
                  "levels in every column": float(t.groupby("column")["v"].nunique().min()),
                  "first plot is A": float(t["v"].iloc[0] == "A")}
             """,
             published={"levels in every row": (4.0, 0.0, "exact"), "levels in every column": (4.0, 0.0, "exact")},
             r="""
                 d <- agricolae::design.lsd(c("A", "B", "C", "D"), serie = 0, seed = 2, kinds = "Mersenne-Twister")
                 list(`first plot is A` = as.numeric(d$book[[4]][1] == "A"))
             """, r_packages=("agricolae",), r_tolerance=0, ours_r=("agricolae",), option='of_kind="latin square"'),
        Case("sdata.make_design_table", 'of_kind="split plot": one irrigation per whole plot, every variety in it',
             "designs (no data)", "published",
             ours="""
                 t = sdata.make_design_table({"irrigation": ["dry", "wet"], "variety": ["A", "B", "C"]}, repeats=3,
                                             of_kind="split plot", whole_plots="irrigation", with_seed=4).as_pandas()
                 {"irrigations in a whole plot": float(t.groupby("whole plot")["irrigation"].nunique().max()),
                  "varieties in a whole plot": float(t.groupby("whole plot")["variety"].nunique().min()),
                  "first part is A": float(t["variety"].iloc[0] == "A")}
             """,
             published={"irrigations in a whole plot": (1.0, 0.0, "exact"),
                        "varieties in a whole plot": (3.0, 0.0, "exact")},
             r="""
                 d <- agricolae::design.split(c("dry", "wet"), c("A", "B", "C"), r = 3, design = "rcbd", serie = 0,
                                              seed = 4, kinds = "Mersenne-Twister")
                 list(`first part is A` = as.numeric(d$book[[5]][1] == "A"))
             """, r_packages=("agricolae",), r_tolerance=0, ours_r=("agricolae",), option='of_kind="split plot"'),
        # ---------------------------------------------------------------- V02: stratified random rows
        Case("table.keep_random_rows", "for_each_group_in=: 10 schools of each type from the api sample",
             "api stratified sample (survey)", "real data",
             ours="""
                 t = sdata.table(data)
                 t.keep_random_rows(10, for_each_group_in="stype", with_seed=2)
                 k = t.as_pandas()
                 {"elementary schools": float((k["stype"] == "E").sum()), "high schools": float((k["stype"] == "H").sum()),
                  "total score": float(k["api00"].sum())}
             """,
             parent="""
                 k = data.groupby("stype").sample(n=10, random_state=2)
                 {"elementary schools": float((k["stype"] == "E").sum()), "high schools": float((k["stype"] == "H").sum()),
                  "total score": float(k["api00"].sum())}
             """, parent_label="pandas groupby().sample()", parent_tolerance=0, option="for_each_group_in="),
        Case("table.keep_random_rows", "percent=: 10 % of each school type from the api sample",
             "api stratified sample (survey)", "real data",
             ours="""
                 t = sdata.table(data)
                 t.keep_random_rows(percent=10, for_each_group_in="stype", with_seed=2)
                 k = t.as_pandas()
                 {"rows": float(len(k)), "middle schools": float((k["stype"] == "M").sum()), "total score": float(k["api00"].sum())}
             """,
             parent="""
                 k = data.groupby("stype").sample(frac=0.1, random_state=2)
                 {"rows": float(len(k)), "middle schools": float((k["stype"] == "M").sum()), "total score": float(k["api00"].sum())}
             """, parent_label="pandas groupby().sample(frac=)", parent_tolerance=0, option="percent="),
        # ---------------------------------------------------------------- X06: patterns of empty cells
        Case("table.count_empty_cells_in", 'show="patterns": nhanes, the patterns of van Buuren & Groothuis-Oudshoorn',
             "nhanes (mice)", "published",
             ours="""
                 p = sdata.table(data).count_empty_cells_in(show="patterns").as_pandas()
                 n = p.set_index("empty cells")["rows with this pattern"]
                 {"complete rows": float(n.loc[0]), "rows with 3 empty cells": float(n.loc[3]),
                  "patterns": float(len(p)), "rows with 1 empty cell": float(n.loc[1].sum())}
             """,
             published={"complete rows": (13.0, 0.0, "exact"), "rows with 3 empty cells": (7.0, 0.0, "exact"),
                        "patterns": (5.0, 0.0, "exact"), "rows with 1 empty cell": (4.0, 0.0, "exact")},
             r="""
                 m <- mice::md.pattern(data.frame(age, bmi, hyp, chl), plot = FALSE)
                 k <- m[-nrow(m), ncol(m)]
                 n <- as.numeric(rownames(m)[-nrow(m)])
                 list(`complete rows` = sum(n[k == 0]), `rows with 3 empty cells` = sum(n[k == 3]),
                      patterns = length(n), `rows with 1 empty cell` = sum(n[k == 1]))
             """, r_packages=("mice",), r_tolerance=0, option='show="patterns"'),
        # ---------------------------------------------------------------- W06: answers on a scale
        Case("table.count_each", "columns=, in_order=: the professional challenges survey, all 565 answers",
             "professional challenges (HH)", "published",
             ours=_join(PROF, f"""
                 r = sdata.table(rows).count_each(columns=["all"], in_order={LEVELS}).as_pandas().iloc[0]
                 {{"agree": float(r["agree"]), "strongly agree": float(r["strongly_agree"]),
                  "percent in top two": float(r["percent in top two"]), "percent no opinion": float(r["percent no_opinion"])}}
             """),
             published={"agree": (230.0, 0.0, "exact"), "strongly agree": (283.0, 0.0, "exact")},
             r="""
                 x <- c(strongly_disagree[1], disagree[1], no_opinion[1], agree[1], strongly_agree[1])
                 p <- prop.table(x) * 100
                 list(`percent in top two` = p[4] + p[5], `percent no opinion` = p[3])
             """, r_tolerance=1e-12, option="columns=, in_order=",
             note="Heiberger & Robbins (2014) publish the counts; the percents are R prop.table()."),
        Case("draw_answer_bars", "the professional challenges survey: the middle answer split across 0",
             "professional challenges (HH)", "published",
             ours=_join(PROF, f"""
                 from simplydata._underneath.check import _axes_of, chart_facts
                 chart = sdata.chart(rows).draw_answer_bars(columns=["all"], in_order={LEVELS})
                 bars = sorted(chart_facts(_axes_of(chart))["bars"])
                 {{"left end": bars[0][0], "middle bar starts at": bars[2][0], "bars": float(len(bars))}}
             """),
             published={"bars": (5.0, 0.0, "exact")},
             r="""
                 x <- c(strongly_disagree[1], disagree[1], no_opinion[1], agree[1], strongly_agree[1])
                 p <- prop.table(x) * 100
                 list(`left end` = -(p[1] + p[2] + p[3] / 2), `middle bar starts at` = -p[3] / 2)
             """, r_tolerance=1e-12,
             note="Heiberger & Robbins (2014): diverging bars centred on the middle answer."),
        # ---------------------------------------------------------------- W01 / W02: survey designs
        # waiting for a word: no simplydata word gives a survey design's degrees of freedom yet (its name waits for
        # approval), so this case reads t._survey["df"] for now
        Case("table.use_survey_design", "the stratified api sample: 197 degrees of freedom (200 schools, 3 strata)",
             "api stratified sample (survey)", "published",
             ours=_join(OURS_STRAT, """
                 {"degrees of freedom": float(t._survey["df"])}
             """),
             published={"degrees of freedom": (197.0, 0.0, "exact")},
             r=STRAT_R + "list(`degrees of freedom` = survey::degf(d))", r_packages=("survey",), r_tolerance=0,
             ours_r=("survey",)),
        _survey_case(Case, "table.find_average_of", "the stratified api sample: the mean API 2000 (Lumley 2010)",
                     _join(OURS_STRAT, """
                         r = t.find_average_of("api00").as_pandas().iloc[0]
                         {"mean": r["average of api00"], "standard error": r["standard error"],
                          "95 % CI low": r["average of api00 95 % CI low"]}
                     """),
                     {"mean": (662.29, 0.005, LUMLEY), "standard error": (9.4089, 0.00005, LUMLEY)},
                     STRAT_R + "m <- survey::svymean(~api00, d); ci <- confint(m, df = survey::degf(d)); "
                               "list(mean = coef(m), `standard error` = survey::SE(m), `95 % CI low` = ci[1])"),
        _survey_case(Case, "table.find_average_of", "the one-stage cluster sample: the mean API 2000 (Lumley 2010)",
                     """
                         t = sdata.table(data)
                         t.use_survey_design(weights="pw", clusters="dnum", population_sizes="fpc")
                         r = t.find_average_of("api00").as_pandas().iloc[0]
                         {"mean": r["average of api00"], "standard error": r["standard error"],
                          "degrees of freedom": r["degrees of freedom"]}
                     """,
                     {"mean": (644.17, 0.005, LUMLEY), "standard error": (23.542, 0.0005, LUMLEY),
                      "degrees of freedom": (14.0, 0.0, LUMLEY)},
                     "d <- survey::svydesign(ids = ~dnum, weights = ~pw, fpc = ~fpc, data = data.frame(dnum, pw, fpc, "
                     "api00)); m <- survey::svymean(~api00, d); list(mean = coef(m), `standard error` = survey::SE(m))",
                     dataset="api cluster sample (survey)"),
        _survey_case(Case, "table.find_total_of", "the stratified api sample: the total enrolment (Lumley 2010)",
                     _join(OURS_STRAT, """
                         r = t.find_total_of("enroll").as_pandas().iloc[0]
                         {"total": r["total of enroll"], "standard error": r["standard error"],
                          "95 % CI high": r["total of enroll 95 % CI high"]}
                     """),
                     {"total": (3687178.0, 0.5, LUMLEY), "standard error": (114642.0, 0.5, LUMLEY)},
                     STRAT_R + "m <- survey::svytotal(~enroll, d); ci <- confint(m, df = survey::degf(d)); "
                               "list(total = coef(m), `standard error` = survey::SE(m), `95 % CI high` = ci[2])"),
        _survey_case(Case, "table.find_median_of", "the stratified api sample: the median API 2000 and Woodruff's interval",
                     _join(OURS_STRAT, """
                         r = t.find_median_of("api00").as_pandas().iloc[0]
                         {"median": r["median of api00"], "95 % CI low": r["median of api00 95 % CI low"],
                          "95 % CI high": r["median of api00 95 % CI high"], "standard error": r["standard error"]}
                     """), None,
                     STRAT_R + 'q <- survey::svyquantile(~api00, d, quantiles = 0.5, qrule = "math", ci = TRUE, '
                               "df = survey::degf(d))$api00; list(median = q[1, 1], `95 % CI low` = q[1, 2], "
                               "`95 % CI high` = q[1, 3], `standard error` = q[1, 4])"),
        _survey_case(Case, "table.find_percentile_of", "the stratified api sample: the 90th percentile of API 2000",
                     _join(OURS_STRAT, """
                         r = t.find_percentile_of("api00", 90).as_pandas().iloc[0]
                         {"percentile 90": r["percentile 90 of api00"], "95 % CI low": r["percentile 90 of api00 95 % CI low"]}
                     """), None,
                     STRAT_R + 'q <- survey::svyquantile(~api00, d, quantiles = 0.9, qrule = "math", ci = TRUE, '
                               "df = survey::degf(d))$api00; list(`percentile 90` = q[1, 1], `95 % CI low` = q[1, 2])"),
        _survey_case(Case, "table.find_percent_of_rows_where",
                     "the stratified api sample: the percent of schools that met their target",
                     _join(OURS_STRAT, """
                         r = t.find_percent_of_rows_where("sch.wide", is_equal_to="Yes").as_pandas().iloc[0]
                         {"percent": r["percent"], "95 % CI low": r["percent 95 % CI low"],
                          "95 % CI high": r["percent 95 % CI high"]}
                     """), None,
                     STRAT_R + 'p <- survey::svyciprop(~sch, d, method = "logit"); ci <- attr(p, "ci"); '
                               "list(percent = coef(p) * 100, `95 % CI low` = ci[1] * 100, `95 % CI high` = ci[2] * 100)"),
        _survey_case(Case, "table.count_rows", "the stratified api sample: the schools with an award in California",
                     _join(OURS_STRAT, """
                         r = t.count_rows(for_each_group_in="awards").as_pandas().set_index("awards")
                         s = t.count_rows(for_each_group_in="awards", in_percent=True).as_pandas().set_index("awards")
                         {"schools with an award": r.loc["Yes", "population count"],
                          "standard error": r.loc["Yes", "standard error"], "percent with an award": s.loc["Yes", "percent"]}
                     """), None,
                     STRAT_R + "m <- survey::svyby(~one, ~awards, stats::update(d, one = 1), survey::svytotal); "
                               "s <- survey::svymean(~awards, d); list(`schools with an award` = coef(m)[2], "
                               "`standard error` = survey::SE(m)[2], `percent with an award` = coef(s)[2] * 100)"),
        _survey_case(Case, "table.explain", "the stratified api sample: API 2000 from English learners and free meals",
                     _join(OURS_STRAT, """
                         r = t.explain("api00", using=["ell", "meals"]).as_pandas().set_index("term")
                         {"meals": r.loc["meals", "estimate"], "meals standard error": r.loc["meals", "standard error"],
                          "ell p-value": r.loc["ell", "p-value"], "intercept": r.loc["(Intercept)", "estimate"]}
                     """), None,
                     STRAT_R + "s <- summary(survey::svyglm(api00 ~ ell + meals, design = d))$coefficients; "
                               "list(meals = s[3, 1], `meals standard error` = s[3, 2], `ell p-value` = s[2, 4], "
                               "intercept = s[1, 1])"),
        _survey_case(Case, "table.compare_averages_of", "the stratified api sample: API 2000 with and without an award",
                     _join(OURS_STRAT, """
                         r = t.compare_averages_of("api00", for_each_group_in="awards").as_pandas().iloc[0]
                         {"difference": r["difference"], "t": r["t"], "p-value": r["p-value"]}
                     """), None,
                     STRAT_R + "r <- survey::svyttest(api00 ~ awards, d); list(difference = r$estimate, "
                               "t = r$statistic, `p-value` = r$p.value)"),
        _survey_case(Case, "table.compare_counts_of", "the stratified api sample: awards by school type (Rao-Scott)",
                     _join(OURS_STRAT, """
                         r = t.compare_counts_of("awards", for_each_group_in="stype").as_pandas().iloc[0]
                         {"F": r["F"], "p-value": r["p-value"], "design degrees of freedom": r["design degrees of freedom"]}
                     """), None,
                     STRAT_R + "r <- survey::svychisq(~awards + stype, d); list(F = r$statistic, `p-value` = r$p.value, "
                               "`design degrees of freedom` = r$parameter[2])"),
    ]


def add_to(namespace) -> None:
    """Add the S3d-1 datasets and cases to cases.py, and teach its load() the design cases, which need no data."""
    Dataset, Case = namespace["Dataset"], namespace["Case"]
    for d in _datasets(Dataset):
        namespace["DATASETS"][d.name] = d
    namespace["CASES"].extend(_cases(Case))
    plain_load = namespace["load"]

    def load(name: str):
        if name == "designs (no data)":  # the design words make their own tables
            return None
        return plain_load(name)

    namespace["load"] = load
