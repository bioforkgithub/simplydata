"""Real-data cases for phase U3, batch 6: the statistics and distribution words that got an underneath entry.

Each word is run on real or published data and compared with the package underneath (SciPy, statsmodels, NumPy)
and, where it is easy, with R. The datasets are the study's own (validation/cases.py DATASETS): Fisher's iris,
mtcars, Student's sleep data, birthwt, the Lake Huron levels, NIST's Michelson measurements, the dry cat food
study, and data read from R packages that other case files register (pROC's aSAH, mcr's creatinine, ca's wg93,
lavaan's Holzinger & Swineford, metadat's Hart 1999). simplydata's side reads its results with simplydata words
(get_cell_at, get_number_at, count ...).
"""

from __future__ import annotations

IRIS_TWO = """
    t = sdata.table(data)
    t.keep_rows_where("Species", is_one_of=["setosa", "versicolor"])
"""
SLEEP_SUMMARY = """
    g = data.groupby("group")["extra"]
    m, s, n = g.mean().tolist(), g.std().tolist(), g.count().tolist()
"""
FLUTD_COUNTS = """
    events, cats = data["flutd"].tolist(), data["cats"].tolist()
"""
BIRTHWT_COUNTS = """
    smoker, low = data["smoke"] == 1, data["low"] == 1
    tp, fn = int((smoker & low).sum()), int((~smoker & low).sum())
    fp, tn = int((smoker & ~low).sum()), int((~smoker & ~low).sum())
"""
MICHELSON_SUM = """
    n, total = len(data), float(data["y"].sum())
"""
HP_GAMMA = """
    hp = data["hp"].to_numpy(dtype=float)
    shape, rate = hp.mean() ** 2 / hp.var(ddof=1), hp.mean() / hp.var(ddof=1)
"""
HP_GAMMA_R = "shape <- mean(hp)^2 / var(hp); rate <- mean(hp) / var(hp); "
MPG_NORMAL = """
    m, s = data["mpg"].mean(), data["mpg"].std()
"""


def _join(*parts: str) -> str:
    import textwrap

    return "\n".join(textwrap.dedent(p).strip("\n") for p in parts) + "\n"


def cases(Case):
    return [
        # ---------------------------------------------------------------- tests of counts, shapes and order
        Case("table.compare_counts_to", "mtcars: are the cars spread evenly over 3, 4 and 5 gears?", "mtcars",
             "real data",
             ours="""
                 r = sdata.table(data).compare_counts_to("gear")
                 {"chi-square": r.get_cell_at(row=1, column="statistic"),
                  "p-value": r.get_cell_at(row=1, column="p-value")}
             """,
             parent="""
                 from scipy import stats
                 res = stats.chisquare(data["gear"].value_counts().sort_index().to_numpy())
                 {"chi-square": res.statistic, "p-value": res.pvalue}
             """, parent_label="SciPy stats.chisquare", parent_tolerance=1e-12,
             r="""
                 t <- chisq.test(table(gear))
                 list(`chi-square` = unname(t$statistic), `p-value` = t$p.value)
             """, r_tolerance=1e-12),
        Case("table.compare_shapes_of", "Fisher's iris: do the sepal lengths of the three species differ in shape?",
             "iris", "real data",
             ours="""
                 r = sdata.table(data).compare_shapes_of("Sepal.Length", for_each_group_in="Species")
                 {"T": r.get_cell_at(row=1, column="statistic")}
             """,
             parent="""
                 from scipy import stats
                 groups = [g["Sepal.Length"].to_numpy() for _, g in data.groupby("Species")]
                 {"T": stats.anderson_ksamp(groups, midrank=True).statistic}
             """, parent_label="SciPy stats.anderson_ksamp(midrank=True)", parent_tolerance=1e-12,
             note="SciPy's midrank version is version 2 of R kSamples::ad.test(), which gives T.AD = 51.231 here."),
        Case("table.compare_shapes_of", "Student's sleep data: do the two drugs differ in shape (tied values)?",
             "Student's sleep data", "real data", option="two groups", ours_r=(),
             ours="""
                 r = sdata.table(data).compare_shapes_of("extra", for_each_group_in="group")
                 {"D": r.get_cell_at(row=1, column="statistic"), "p-value": r.get_cell_at(row=1, column="p-value")}
             """,
             parent="""
                 from scipy import stats
                 a, b = (data.loc[data["group"] == g, "extra"] for g in ("drug 1", "drug 2"))
                 {"D": stats.ks_2samp(a, b, method="exact").statistic}
             """, parent_label="SciPy stats.ks_2samp", parent_tolerance=1e-12,
             r="""
                 t <- suppressWarnings(ks.test(extra[group == "drug 1"], extra[group == "drug 2"]))
                 list(D = unname(t$statistic), `p-value` = t$p.value)
             """, r_tolerance=1e-12),
        Case("table.check_if_random_order", "Lake Huron: do the yearly levels come in a random order?", "Lake Huron",
             "real data",
             ours="""
                 r = sdata.table(data).check_if_random_order("level", sorted_by="year")
                 {"z": r.get_cell_at(row=1, column="statistic"), "runs": r.get_cell_at(row=1, column="runs")}
             """,
             parent="""
                 from statsmodels.sandbox.stats.runs import Runs
                 x = data.sort_values("year")["level"].to_numpy()
                 m = np.median(x)
                 runs = Runs((x[x != m] > m).astype(int))
                 {"z": runs.runs_test(correction=False)[0], "runs": runs.n_runs}
             """, parent_label="statsmodels Runs.runs_test(correction=False)", parent_tolerance=1e-12,
             r="""
                 x <- level[order(year)]
                 s <- x[x != median(x)] > median(x)
                 n1 <- sum(s); n2 <- sum(!s); runs <- 1 + sum(s[-1] != s[-length(s)])
                 mu <- 2 * n1 * n2 / (n1 + n2) + 1
                 v <- 2 * n1 * n2 * (2 * n1 * n2 - n1 - n2) / ((n1 + n2)^2 * (n1 + n2 - 1))
                 list(z = (runs - mu) / sqrt(v), runs = runs)
             """, r_tolerance=1e-12,
             note="The R code is the runs test of R randtests::runs.test(), written out in base R."),
        Case("table.compare_correlations", "Fisher's iris: sepal and petal length, setosa against versicolor",
             "iris", "real data", ours_r=("cocor",),
             ours=_join(IRIS_TWO, """
                 r = t.compare_correlations("Sepal.Length", "Petal.Length", for_each_group_in="Species")
                 {"r in setosa": r.get_cell_at(row=1, column="r in setosa"),
                  "z": r.get_cell_at(row=1, column="statistic"), "p-value": r.get_cell_at(row=1, column="p-value")}
             """),
             parent="""
                 from scipy import stats
                 s = data[data["Species"] == "setosa"]
                 {"r in setosa": stats.pearsonr(s["Sepal.Length"], s["Petal.Length"]).statistic}
             """, parent_label="SciPy stats.pearsonr", parent_tolerance=1e-12,
             r="""
                 a <- Species == "setosa"; b <- Species == "versicolor"
                 r1 <- cor(Sepal.Length[a], Petal.Length[a]); r2 <- cor(Sepal.Length[b], Petal.Length[b])
                 t <- cocor::cocor.indep.groups(r1, r2, sum(a), sum(b), test = "fisher1925")
                 list(`r in setosa` = r1, z = t@fisher1925$statistic, `p-value` = t@fisher1925$p.value)
             """, r_packages=("cocor",), r_tolerance=1e-10),
        # ---------------------------------------------------------------- from summary numbers and counts
        Case("sdata.compare_averages", "Student's sleep data: Welch's t-test from each drug's average, standard "
                                       "deviation and count", "Student's sleep data", "real data", ours_r=("BSDA",),
             ours=_join(SLEEP_SUMMARY, """
                 r = sdata.compare_averages(averages=m, standard_deviations=s, counts=n)
                 {"t": r.get_cell_at(row=1, column="statistic"),
                  "degrees of freedom": r.get_cell_at(row=1, column="degrees of freedom"),
                  "95 % CI low": r.get_cell_at(row=1, column="difference 95 % CI low")}
             """),
             parent="""
                 from scipy import stats
                 a, b = (data.loc[data["group"] == g, "extra"] for g in ("drug 1", "drug 2"))
                 res = stats.ttest_ind(a, b, equal_var=False)
                 {"t": res.statistic, "degrees of freedom": res.df, "95 % CI low": res.confidence_interval().low}
             """, parent_label="SciPy stats.ttest_ind on the rows (Welch)", parent_tolerance=1e-9,
             r="""
                 t <- t.test(extra ~ group)
                 list(t = unname(t$statistic), `degrees of freedom` = unname(t$parameter), `95 % CI low` = t$conf.int[1])
             """, r_tolerance=1e-9,
             note="The summary numbers give the same test as the rows (R t.test())."),
        Case("sdata.compare_counts", "dry cat food and FLUTD: the 2 x 2 table of counts", "dry cat food and FLUTD",
             "real data",
             ours=_join(FLUTD_COUNTS, """
                 r = sdata.compare_counts([[events[0], cats[0] - events[0]], [events[1], cats[1] - events[1]]])
                 {"chi-square": r.get_cell_at(row=1, column="statistic"),
                  "p-value": r.get_cell_at(row=1, column="p-value")}
             """),
             parent="""
                 from scipy import stats
                 e, n = data["flutd"].to_numpy(), data["cats"].to_numpy()
                 res = stats.chi2_contingency(np.column_stack([e, n - e]))
                 {"chi-square": res.statistic, "p-value": res.pvalue}
             """, parent_label="SciPy stats.chi2_contingency (Yates)", parent_tolerance=1e-12,
             r="""
                 t <- chisq.test(cbind(flutd, cats - flutd))
                 list(`chi-square` = unname(t$statistic), `p-value` = t$p.value)
             """, r_tolerance=1e-10),
        Case("sdata.compare_risks", "dry cat food and FLUTD: the risk ratio of dry food against other food",
             "dry cat food and FLUTD", "real data",
             ours=_join(FLUTD_COUNTS, """
                 r = sdata.compare_risks(events=events, out_of=cats, names=data["food"].tolist(), against="other food")
                 r.keep_rows_where("measure", is_equal_to="risk ratio")
                 {"risk ratio": r.get_cell_at(row=1, column="estimate"),
                  "95 % CI low": r.get_cell_at(row=1, column="estimate 95 % CI low"),
                  "p-value": r.get_cell_at(row=1, column="p-value")}
             """),
             parent="""
                 from statsmodels.stats.contingency_tables import Table2x2
                 e, n = data["flutd"].to_numpy(), data["cats"].to_numpy()
                 t = Table2x2(np.column_stack([e, n - e]).astype(float))
                 {"risk ratio": t.riskratio, "95 % CI low": t.riskratio_confint()[0]}
             """, parent_label="statsmodels Table2x2", parent_tolerance=1e-12,
             r="""
                 rr <- (flutd[1] / cats[1]) / (flutd[2] / cats[2])
                 se <- sqrt(1 / flutd[1] - 1 / cats[1] + 1 / flutd[2] - 1 / cats[2])
                 list(`risk ratio` = rr, `95 % CI low` = exp(log(rr) - qnorm(0.975) * se),
                      `p-value` = prop.test(flutd, cats)$p.value)
             """, r_tolerance=1e-9),
        Case("sdata.compare_rates", "Hart 1999: strokes per patient-year with warfarin and with placebo, the first "
                                    "trial", "Hart 1999 (metadat)", "real data", ours_r=(),
             ours="""
                 first = data.iloc[0]
                 # the counts come from R as decimals (12.0); counts are whole numbers
                 r = sdata.compare_rates(events=[int(first["x1i"]), int(first["x2i"])], time=[first["t1i"], first["t2i"]],
                                         names=["warfarin", "placebo"], against="placebo")
                 r.keep_rows_where("measure", is_equal_to="rate ratio")
                 {"rate ratio": r.get_cell_at(row=1, column="estimate"),
                  "95 % CI high": r.get_cell_at(row=1, column="estimate 95 % CI high"),
                  "p-value": r.get_cell_at(row=1, column="p-value")}
             """,
             parent="""
                 from statsmodels.stats.rates import test_poisson_2indep
                 first = data.iloc[0]
                 res = test_poisson_2indep(int(first["x1i"]), first["t1i"], int(first["x2i"]), first["t2i"],
                                           method="exact-cond")
                 {"rate ratio": res.ratio, "p-value": res.pvalue}
             """, parent_label="statsmodels test_poisson_2indep(method=\"exact-cond\")", parent_tolerance=1e-10,
             r="""
                 t <- poisson.test(c(x1i[1], x2i[1]), c(t1i[1], t2i[1]))
                 list(`rate ratio` = unname(t$estimate), `95 % CI high` = t$conf.int[2], `p-value` = t$p.value)
             """, r_tolerance=1e-9),
        # ---------------------------------------------------------------- diagnostic tests
        Case("table.compare_to_truth", "birthwt: the mother's smoking as a marker of a low birth weight",
             "birthwt", "real data",
             ours="""
                 r = sdata.table(data).compare_to_truth("smoke", truth="low")
                 r.keep_rows_where("measure", is_equal_to="sensitivity")
                 {"sensitivity": r.get_cell_at(row=1, column="estimate"),
                  "95 % CI low": r.get_cell_at(row=1, column="estimate 95 % CI low")}
             """,
             parent="""
                 from statsmodels.stats.proportion import proportion_confint
                 low = data[data["low"] == 1]
                 found = int((low["smoke"] == 1).sum())
                 {"sensitivity": found / len(low), "95 % CI low": proportion_confint(found, len(low), method="beta")[0]}
             """, parent_label="statsmodels proportion_confint(method=\"beta\")", parent_tolerance=1e-12,
             r="""
                 b <- binom.test(sum(smoke == 1 & low == 1), sum(low == 1))
                 list(sensitivity = unname(b$estimate), `95 % CI low` = b$conf.int[1])
             """, r_tolerance=1e-9),
        Case("table.compare_to_truth", "aSAH: the AUC of s100b for a poor outcome", "aSAH (pROC)", "real data",
             option="a column of numbers", ours_r=("pROC",),
             ours="""
                 r = sdata.table(data).compare_to_truth("s100b", truth="outcome")
                 {"AUC": r.get_cell_at(row=1, column="estimate"),
                  "95 % CI low": r.get_cell_at(row=1, column="estimate 95 % CI low")}
             """,
             r="""
                 r <- pROC::roc(outcome, s100b, levels = c("Good", "Poor"), direction = "<", quiet = TRUE)
                 a <- pROC::ci.auc(r, method = "delong")
                 list(AUC = as.numeric(a[2]), `95 % CI low` = as.numeric(a[1]))
             """, r_packages=("pROC",), r_tolerance=1e-12,
             note="Robin et al. (2011) show the same curve in pROC's paper (AUC 0.731)."),
        Case("table.compare_accuracy", "birthwt: the mother's weight against her age as a marker of a low birth "
                                       "weight (lower scores count)", "birthwt", "real data", ours_r=("pROC",),
             ours="""
                 r = sdata.table(data).compare_accuracy("lwt", "age", truth="low", positive_when="lower")
                 r.keep_rows_where("measure", is_equal_to="difference in AUC (lwt minus age)")
                 {"difference": r.get_cell_at(row=1, column="estimate"), "z": r.get_cell_at(row=1, column="statistic"),
                  "p-value": r.get_cell_at(row=1, column="p-value")}
             """,
             r="""
                 r1 <- pROC::roc(low, lwt, levels = c(0, 1), direction = ">", quiet = TRUE)
                 r2 <- pROC::roc(low, age, levels = c(0, 1), direction = ">", quiet = TRUE)
                 t <- pROC::roc.test(r1, r2, method = "delong", paired = TRUE)
                 list(difference = unname(t$estimate[1] - t$estimate[2]), z = unname(t$statistic), `p-value` = t$p.value)
             """, r_packages=("pROC",), r_tolerance=1e-10),
        Case("sdata.compare_to_truth", "birthwt: smoking against a low birth weight, from the four counts",
             "birthwt", "real data", ours_r=("epiR",),
             ours=_join(BIRTHWT_COUNTS, """
                 r = sdata.compare_to_truth(found=tp, missed=fn, false_alarms=fp, correct_negatives=tn)
                 r.keep_rows_where("measure", is_one_of=["specificity", "positive likelihood ratio"])
                 {"specificity": r.get_cell_at(row=1, column="estimate"),
                  "positive likelihood ratio": r.get_cell_at(row=2, column="estimate"),
                  "its 95 % CI low": r.get_cell_at(row=2, column="estimate 95 % CI low")}
             """),
             parent=_join(BIRTHWT_COUNTS, """
                 {"specificity": tn / (tn + fp), "positive likelihood ratio": (tp / (tp + fn)) / (fp / (fp + tn))}
             """), parent_label="the shares of the counts (pandas)", parent_tolerance=1e-12,
             r="""
                 t <- as.table(matrix(c(sum(smoke == 1 & low == 1), sum(smoke == 0 & low == 1),
                                        sum(smoke == 1 & low == 0), sum(smoke == 0 & low == 0)), nrow = 2))
                 d <- epiR::epi.tests(t, method = "exact")$detail
                 k <- d$statistic == "lr.pos"
                 list(`positive likelihood ratio` = d$est[k], `its 95 % CI low` = d$lower[k])
             """, r_packages=("epiR",), r_tolerance=1e-9),
        # ---------------------------------------------------------------- agreement and reliability
        Case("table.agreement_between", "wg93: how alike do the same people answer questions A and B?",
             "wg93 (ca)", "real data",
             ours="""
                 r = sdata.table(data).agreement_between("A", "B")
                 {"kappa": r.get_cell_at(row=1, column="estimate"), "z": r.get_cell_at(row=1, column="statistic")}
             """,
             parent="""
                 from statsmodels.stats.inter_rater import cohens_kappa
                 seen = sorted(set(data["A"]) | set(data["B"]))
                 counts = pd.crosstab(data["A"], data["B"]).reindex(index=seen, columns=seen, fill_value=0)
                 res = cohens_kappa(counts.to_numpy())
                 {"kappa": res["kappa"], "z": res["z_value"]}
             """, parent_label="statsmodels cohens_kappa", parent_tolerance=1e-12,
             r="""
                 k <- irr::kappa2(data.frame(A, B))
                 list(kappa = k$value)
             """, r_packages=("irr",), r_tolerance=1e-12),
        Case("table.agreement_between", "creatinine: serum and plasma measurements of the same samples (ICC)",
             "creatinine (mcr)", "real data", option="columns of numbers", ours_r=("irr",),
             ours="""
                 r = sdata.table(data).agreement_between("serum", "plasma")
                 {"ICC": r.get_cell_at(row=1, column="estimate"),
                  "95 % CI low": r.get_cell_at(row=1, column="estimate 95 % CI low")}
             """,
             r="""
                 i <- irr::icc(cbind(serum, plasma), model = "twoway", type = "agreement", unit = "single")
                 list(ICC = i$value, `95 % CI low` = i$lbound)
             """, r_packages=("irr",), r_tolerance=1e-12),
        Case("table.limits_of_agreement", "creatinine: serum minus plasma, the Bland-Altman limits",
             "creatinine (mcr)", "real data", ours_r=("BlandAltmanLeh", "DescTools"),
             ours="""
                 r = sdata.table(data).limits_of_agreement("serum", "plasma")
                 {"lower limit": r.get_cell_at(row=1, column="lower limit"),
                  "upper limit": r.get_cell_at(row=1, column="upper limit"),
                  "upper limit 95 % CI high": r.get_cell_at(row=1, column="upper limit 95 % CI high")}
             """,
             parent="""
                 d = (data["serum"] - data["plasma"]).to_numpy()
                 {"lower limit": d.mean() - 1.96 * d.std(ddof=1), "upper limit": d.mean() + 1.96 * d.std(ddof=1)}
             """, parent_label="NumPy mean and standard deviation (n - 1)", parent_tolerance=1e-12,
             r="""
                 s <- BlandAltmanLeh::bland.altman.stats(serum, plasma)
                 list(`lower limit` = s$lower.limit, `upper limit` = s$upper.limit,
                      `upper limit 95 % CI high` = unname(s$CI.lines[6]))
             """, r_packages=("BlandAltmanLeh",), r_tolerance=1e-12),
        Case("table.reliability_of", "Holzinger & Swineford: Cronbach's alpha of the three visual tests",
             "Holzinger & Swineford 1939 (lavaan)", "real data", ours_r=("psych",),
             ours="""
                 r = sdata.table(data).reliability_of(["x1", "x2", "x3"])
                 {"alpha": r.get_cell_at(row=1, column="estimate"),
                  "95 % CI low": r.get_cell_at(row=1, column="estimate 95 % CI low")}
             """,
             parent="""
                 x = data[["x1", "x2", "x3"]].to_numpy()
                 k = x.shape[1]
                 {"alpha": k / (k - 1) * (1 - x.var(axis=0, ddof=1).sum() / x.sum(axis=1).var(ddof=1))}
             """, parent_label="NumPy, Cronbach's formula", parent_tolerance=1e-12,
             r="""
                 a <- psych::alpha(data.frame(x1, x2, x3), check.keys = FALSE)
                 f <- psych::alpha.ci(a$total$raw_alpha, n.obs = length(x1), n.var = 3, p.val = 0.05)
                 list(alpha = a$total$raw_alpha, `95 % CI low` = f$lower.ci)
             """, r_packages=("psych",), r_tolerance=1e-12),
        Case("draw_difference_dots", "creatinine: serum minus plasma against their average, with the limits",
             "creatinine (mcr)", "real data", ours_r=("BlandAltmanLeh",),
             ours="""
                 drawn = sdata.chart(data).difference_dots(first="serum", second="plasma").get_numbers_drawn()
                 # rows 1 and 2 are the bands of the limits' intervals, then one line each: average, lower, upper limit
                 average, lower = drawn.get_cell_at(row=3, column="y"), drawn.get_cell_at(row=5, column="y")
                 drawn.keep_rows_where("kind", is_equal_to="dot")
                 {"dots": drawn.get_column("y").count(), "average difference": average, "lower limit": lower,
                  "first dot up": drawn.get_cell_at(row=1, column="y")}
             """,
             parent="""
                 d = (data["serum"] - data["plasma"]).to_numpy()
                 {"dots": len(d), "average difference": d.mean(), "lower limit": d.mean() - 1.96 * d.std(ddof=1),
                  "first dot up": d[0]}
             """, parent_label="NumPy differences, mean and standard deviation (n - 1)", parent_tolerance=1e-12,
             r="""
                 s <- BlandAltmanLeh::bland.altman.stats(serum, plasma)
                 list(`lower limit` = s$lower.limit, `average difference` = s$mean.diffs)
             """, r_packages=("BlandAltmanLeh",), r_tolerance=1e-12),
        # ---------------------------------------------------------------- finding and solving
        Case("sdata.find_where_smallest", "Michelson: the value closest to all 100 measurements (least squares) is "
                                          "their mean", "NIST Michelso", "published",
             ours=_join(MICHELSON_SUM, """
                 # the sum of (x - y)**2 over the measurements is n x**2 - 2 x (their total) + a number that does not
                 # change with x
                 r = sdata.find_where_smallest(f"{n}*x**2 - 2*{total!r}*x", between=[299, 301])
                 {"mean": r.get_cell_at(row=1, column="x")}
             """),
             published={"mean": (299.8524, 1e-8, "NIST certified")},
             parent="""
                 from scipy import optimize
                 y = data["y"].to_numpy()
                 f = optimize.minimize_scalar(lambda x: ((x - y) ** 2).sum(), bounds=(299, 301), method="bounded",
                                              options={"xatol": 1e-10, "maxiter": 10000})
                 {"mean": f.x}
             """, parent_label="SciPy optimize.minimize_scalar(method=\"bounded\", xatol=1e-10)", parent_tolerance=1e-12,
             r="""
                 list(mean = optimize(function(x) sum((y - x)^2), c(299, 301), tol = 1e-10)$minimum)
             """, r_tolerance=1e-11,
             note="The mean of the measurements makes the sum of squared distances smallest."),
        Case("sdata.find_where_biggest", "Michelson: minus the sum of squared distances is biggest at the mean",
             "NIST Michelso", "published",
             ours=_join(MICHELSON_SUM, """
                 r = sdata.find_where_biggest(f"2*{total!r}*x - {n}*x**2", between=[299, 301])
                 {"mean": r.get_cell_at(row=1, column="x")}
             """),
             published={"mean": (299.8524, 1e-8, "NIST certified")},
             parent="""
                 from scipy import optimize
                 y = data["y"].to_numpy()
                 f = optimize.minimize_scalar(lambda x: ((x - y) ** 2).sum(), bounds=(299, 301), method="bounded",
                                              options={"xatol": 1e-10, "maxiter": 10000})
                 {"mean": f.x}
             """, parent_label="SciPy optimize.minimize_scalar on minus the formula", parent_tolerance=1e-12,
             r="""
                 list(mean = optimize(function(x) -sum((y - x)^2), c(299, 301), maximum = TRUE, tol = 1e-10)$maximum)
             """, r_tolerance=1e-11),
        Case("sdata.solve", "Michelson: the value from which the 100 measurements add up to 0 is their mean",
             "NIST Michelso", "published",
             ours=_join(MICHELSON_SUM, """
                 # the sum of (x - y) over the measurements is n x minus their total
                 r = sdata.solve(f"{n}*x - {total!r} = 0", between=[299, 301])
                 {"mean": r.get_cell_at(row=1, column="x"), "solutions": r.count_rows()}
             """),
             published={"mean": (299.8524, 1e-8, "NIST certified"), "solutions": (1.0, 0.0, "exact")},
             parent="""
                 from scipy import optimize
                 y = data["y"].to_numpy()
                 {"mean": optimize.brentq(lambda x: (x - y).sum(), 299, 301, xtol=1e-12)}
             """, parent_label="SciPy optimize.brentq", parent_tolerance=1e-12,
             r="""
                 list(mean = uniroot(function(x) sum(x - y), c(299, 301), tol = 1e-12)$root)
             """, r_tolerance=1e-12),
        # ---------------------------------------------------------------- values between points
        Case("table.values_at", "Lake Huron: the level halfway between two years, and before the first year",
             "Lake Huron", "real data",
             ours="""
                 r = sdata.table(data).values_at("level", at={"year": [1874, 1900.5, 1950.25]})
                 c = r.get_column("level")
                 {"1900.5": c.get_number_at(2), "1950.25": c.get_number_at(3), "empty": c.count_empty_numbers()}
             """,
             parent="""
                 x = np.interp([1874, 1900.5, 1950.25], data["year"], data["level"], left=np.nan)
                 {"1900.5": x[1], "1950.25": x[2], "empty": int(np.isnan(x).sum())}
             """, parent_label="NumPy interp", parent_tolerance=1e-12,
             r="""
                 a <- approx(year, level, xout = c(1874, 1900.5, 1950.25))$y
                 list(`1900.5` = a[2], `1950.25` = a[3], empty = sum(is.na(a)))
             """, r_tolerance=1e-12),
        Case("table.make_map_of", "Fisher's iris: petal length over a map of sepal length and width (flat "
                                  "triangles)", "iris", "real data",
             ours="""
                 r = sdata.table(data).make_map_of("Petal.Length", across=["Sepal.Length", "Sepal.Width"], steps=5)
                 c = r.get_column("Petal.Length")
                 {"middle of the map": c.get_number_at(13), "places": r.count_rows(), "empty": c.count_empty_numbers()}
             """,
             parent="""
                 from scipy import interpolate
                 known = data.groupby(["Sepal.Length", "Sepal.Width"])["Petal.Length"].mean()
                 points = np.array(known.index.tolist())
                 lines = [np.linspace(points[:, k].min(), points[:, k].max(), 5) for k in (0, 1)]
                 a, b = np.meshgrid(*lines, indexing="ij")
                 z = interpolate.griddata(points, known.to_numpy(), np.column_stack([a.ravel(), b.ravel()]))
                 {"middle of the map": z[12], "places": len(z), "empty": int(np.isnan(z).sum())}
             """, parent_label="SciPy interpolate.griddata(method=\"linear\")", parent_tolerance=1e-12,
             note="Several flowers share a place; their average is used, as SciPy needs distinct points."),
        # ---------------------------------------------------------------- fitting distributions
        Case("table.compare_distributions_for", "mtcars: horsepower, the lognormal fit among four", "mtcars",
             "real data",
             ours="""
                 r = sdata.table(data).compare_distributions_for("hp")
                 r.keep_rows_where("distribution", is_equal_to="lognormal")
                 {"AIC": r.get_cell_at(row=1, column="AIC"),
                  "Kolmogorov-Smirnov statistic": r.get_cell_at(row=1, column="Kolmogorov-Smirnov statistic")}
             """,
             parent="""
                 from scipy import stats
                 x = data["hp"].to_numpy(dtype=float)
                 p = stats.lognorm.fit(x, floc=0)
                 {"AIC": 4 - 2 * stats.lognorm.logpdf(x, *p).sum(),
                  "Kolmogorov-Smirnov statistic": stats.kstest(x, stats.lognorm.cdf, args=p).statistic}
             """, parent_label="SciPy lognorm.fit(floc=0) and kstest", parent_tolerance=1e-9,
             r="""
                 mu <- mean(log(hp)); s <- sqrt(mean((log(hp) - mu)^2))
                 x <- sort(hp); n <- length(x); u <- plnorm(x, mu, s)
                 list(AIC = 4 - 2 * sum(dlnorm(hp, mu, s, log = TRUE)),
                      `Kolmogorov-Smirnov statistic` = max(c(seq_len(n) / n - u, u - (seq_len(n) - 1) / n)))
             """, r_tolerance=1e-9,
             note="The R code is the closed-form lognormal fit of R MASS::fitdistr() and the statistic of R "
                  "fitdistrplus::gofstat(), written out in base R."),
        Case("nums.fit_distribution", "mtcars: a gamma distribution fitted to horsepower", "mtcars", "real data",
             ours="""
                 fit = sdata.numbers(data["hp"].tolist()).fit_distribution("gamma")
                 t = fit.turn_into_table()
                 {"shape": t.get_cell_at(row=1, column="shape"), "rate": t.get_cell_at(row=1, column="rate")}
             """,
             parent="""
                 from scipy import stats
                 a, _, scale = stats.gamma.fit(data["hp"].to_numpy(dtype=float), floc=0)
                 {"shape": a, "rate": 1 / scale}
             """, parent_label="SciPy gamma.fit(floc=0)", parent_tolerance=1e-9,
             r="""
                 f <- MASS::fitdistr(hp / 100, "gamma")
                 list(shape = unname(f$estimate["shape"]), rate = unname(f$estimate["rate"]) / 100)
             """, r_packages=("MASS",), r_tolerance=1e-4,
             note="R fitdistr is given horsepower in hundreds (its search starts badly on the raw scale) and stops "
                  "at its own tolerance, so it agrees to 4 digits."),
        # ---------------------------------------------------------------- one distribution
        Case("dist.find_density_at", "mtcars: the height of a normal curve shaped like fuel use, at 20 miles per "
                                     "gallon", "mtcars", "real data",
             ours=_join(MPG_NORMAL, """
                 {"density at 20": sdata.distribution("normal", average=m, standard_deviation=s).find_density_at(20)}
             """),
             parent=_join(MPG_NORMAL, """
                 from scipy import stats
                 {"density at 20": stats.norm(loc=m, scale=s).pdf(20)}
             """), parent_label="SciPy stats.norm.pdf", parent_tolerance=1e-14,
             r="""
                 list(`density at 20` = dnorm(20, mean(mpg), sd(mpg)))
             """, r_tolerance=1e-12),
        Case("dist.find_cut_off", "the value with a 2.5 % chance above it in the standard normal distribution",
             "standard normal table", "published",
             ours="""
                 {"cut-off": sdata.distribution("normal", average=0, standard_deviation=1)
                             .find_cut_off(with_chance_above=0.025)}
             """,
             # the table gives 0.47500 for z = 1.96: 2.5 % lies above 1.96, printed to 2 decimals
             published={"cut-off": (1.96, 0.005, "NIST/SEMATECH e-Handbook, table 1.3.6.7.1")},
             parent="""
                 from scipy import stats
                 {"cut-off": stats.norm.isf(0.025)}
             """, parent_label="SciPy stats.norm.isf", parent_tolerance=1e-14,
             r="""
                 list(`cut-off` = qnorm(0.025, lower.tail = FALSE))
             """, r_tolerance=1e-14,
             note="No data: the published value is the standard normal table."),
        Case("dist.find_middle_range", "the middle 95 % of the standard normal distribution",
             "standard normal table", "published",
             ours="""
                 r = sdata.distribution("normal", average=0, standard_deviation=1).find_middle_range(95)
                 {"low": r.get_number_at(1), "high": r.get_number_at(2)}
             """,
             published={"low": (-1.96, 0.005, "NIST/SEMATECH e-Handbook, table 1.3.6.7.1"),
                        "high": (1.96, 0.005, "NIST/SEMATECH e-Handbook, table 1.3.6.7.1")},
             parent="""
                 from scipy import stats
                 {"low": stats.norm.ppf(0.025), "high": stats.norm.isf(0.025)}
             """, parent_label="SciPy stats.norm.ppf and isf", parent_tolerance=1e-14,
             r="""
                 q <- qnorm(c(0.025, 0.975))
                 list(low = q[1], high = q[2])
             """, r_tolerance=1e-14,
             note="No data: the published value is the standard normal table."),
        Case("dist.find_average", "mtcars: the average of a gamma distribution shaped like horsepower (moments)",
             "mtcars", "real data",
             ours=_join(HP_GAMMA, """
                 {"average": sdata.distribution("gamma", shape=shape, rate=rate).find_average()}
             """),
             parent=_join(HP_GAMMA, """
                 from scipy import stats
                 {"average": stats.gamma(a=shape, scale=1 / rate).mean()}
             """), parent_label="SciPy stats.gamma.mean", parent_tolerance=1e-14,
             r=HP_GAMMA_R + "list(average = shape / rate)", r_tolerance=1e-12,
             note="The shape and rate come from the average and variance of horsepower, so the average is theirs."),
        Case("dist.find_median", "mtcars: the median of a gamma distribution shaped like horsepower", "mtcars",
             "real data",
             ours=_join(HP_GAMMA, """
                 {"median": sdata.distribution("gamma", shape=shape, rate=rate).find_median()}
             """),
             parent=_join(HP_GAMMA, """
                 from scipy import stats
                 g = stats.gamma(a=shape, scale=1 / rate)
                 {"median": g.median()}
             """), parent_label="SciPy stats.gamma.median", parent_tolerance=1e-14,
             r=HP_GAMMA_R + "list(median = qgamma(0.5, shape, rate))", r_tolerance=1e-10),
        Case("dist.find_standard_deviation", "mtcars: the standard deviation of a gamma distribution shaped like "
                                             "horsepower", "mtcars", "real data",
             ours=_join(HP_GAMMA, """
                 {"standard deviation": sdata.distribution("gamma", shape=shape, rate=rate).find_standard_deviation()}
             """),
             parent=_join(HP_GAMMA, """
                 from scipy import stats
                 {"standard deviation": stats.gamma(a=shape, scale=1 / rate).std()}
             """), parent_label="SciPy stats.gamma.std", parent_tolerance=1e-14,
             r=HP_GAMMA_R + "list(`standard deviation` = sqrt(shape) / rate)", r_tolerance=1e-12),
        Case("dist.find_variance", "mtcars: the variance of a gamma distribution shaped like horsepower", "mtcars",
             "real data",
             ours=_join(HP_GAMMA, """
                 {"variance": sdata.distribution("gamma", shape=shape, rate=rate).find_variance()}
             """),
             parent=_join(HP_GAMMA, """
                 from scipy import stats
                 {"variance": stats.gamma(a=shape, scale=1 / rate).var()}
             """), parent_label="SciPy stats.gamma.var", parent_tolerance=1e-14,
             r=HP_GAMMA_R + "list(variance = var(hp))", r_tolerance=1e-12,
             note="Shaped by its moments, the distribution has the variance of horsepower itself."),
        Case("dist.show_summary", "mtcars: the skewness and excess kurtosis of a gamma distribution shaped like "
                                  "horsepower", "mtcars", "real data",
             ours=_join(HP_GAMMA, """
                 r = sdata.distribution("gamma", shape=shape, rate=rate).show_summary()
                 {"skewness": r.get_cell_at(row=1, column="skewness"),
                  "excess kurtosis": r.get_cell_at(row=1, column="excess kurtosis")}
             """),
             parent=_join(HP_GAMMA, """
                 from scipy import stats
                 _, _, skew, kurt = stats.gamma(a=shape, scale=1 / rate).stats(moments="mvsk")
                 {"skewness": skew, "excess kurtosis": kurt}
             """), parent_label="SciPy stats.gamma.stats(moments=\"mvsk\")", parent_tolerance=1e-14,
             r=HP_GAMMA_R + "list(skewness = 2 / sqrt(shape), `excess kurtosis` = 6 / shape)", r_tolerance=1e-12),
        Case("dist.make_random_numbers", "mtcars: random numbers from a normal curve shaped like fuel use, seed 1",
             "mtcars", "real data",
             ours=_join(MPG_NORMAL, """
                 nums = sdata.distribution("normal", average=m, standard_deviation=s).make_random_numbers(
                     how_many=32, with_seed=1)
                 {"first": nums.get_number_at(1), "total": nums.find_total()}
             """),
             parent=_join(MPG_NORMAL, """
                 from scipy import stats
                 x = stats.norm(loc=m, scale=s).rvs(size=32, random_state=np.random.default_rng(1))
                 {"first": x[0], "total": x.sum()}
             """), parent_label="SciPy stats.norm.rvs with NumPy default_rng(1)", parent_tolerance=1e-12,
             note="Random numbers have no published answer; the check is that the same seed gives SciPy's numbers."),
        Case("dist.draw_chart", "mtcars: the curve of a normal distribution shaped like fuel use", "mtcars",
             "real data",
             ours=_join(MPG_NORMAL, """
                 drawn = sdata.distribution("normal", average=m, standard_deviation=s).draw_chart().get_numbers_drawn()
                 points = drawn.get_column("x").count()
                 {"first x": drawn.get_cell_at(row=1, column="x"), "last x": drawn.get_cell_at(row=points, column="x"),
                  "points": points, "highest": drawn.get_column("y").find_biggest()}
             """),
             parent=_join(MPG_NORMAL, """
                 from scipy import stats
                 d = stats.norm(loc=m, scale=s)
                 xs = np.linspace(d.ppf(0.001), d.ppf(0.999), 200)
                 {"first x": xs[0], "last x": xs[-1], "points": len(xs), "highest": d.pdf(xs).max()}
             """), parent_label="SciPy ppf and pdf on 200 places (matplotlib draws them)", parent_tolerance=1e-12,
             r="""
                 list(`first x` = qnorm(0.001, mean(mpg), sd(mpg)), `last x` = qnorm(0.999, mean(mpg), sd(mpg)))
             """, r_tolerance=1e-12),
        Case("dist.turn_into_table", "mtcars: a normal distribution shaped like fuel use, as a table", "mtcars",
             "real data",
             ours=_join(MPG_NORMAL, """
                 t = sdata.distribution("normal", average=m, standard_deviation=s).turn_into_table()
                 {"average": t.get_cell_at(row=1, column="average"),
                  "standard deviation": t.get_cell_at(row=1, column="standard deviation")}
             """),
             parent="""
                 {"average": data["mpg"].mean(), "standard deviation": data["mpg"].std()}
             """, parent_label="pandas mean and std", parent_tolerance=1e-14,
             r="""
                 list(average = mean(mpg), `standard deviation` = sd(mpg))
             """, r_tolerance=1e-12),
        # ---------------------------------------------------------------- principal components
        Case("table.find_principal_components_of", "Fisher's iris: the principal components of the four "
                                                   "measurements", "iris", "real data",
             ours="""
                 r = sdata.table(data).find_principal_components_of()
                 {"PC1 standard deviation": r.get_cell_at(row=1, column="standard deviation"),
                  "PC1 share (%)": r.get_cell_at(row=1, column="spread explained (%)"),
                  "PC1 weight of petal length": abs(r.get_cell_at(row=1, column="weight of Petal.Length"))}
             """,
             parent="""
                 x = data.select_dtypes("number")
                 z = ((x - x.mean()) / x.std()).to_numpy()
                 _, sv, vt = np.linalg.svd(z, full_matrices=False)
                 sd = sv / np.sqrt(len(z) - 1)
                 {"PC1 standard deviation": sd[0], "PC1 share (%)": sd[0] ** 2 / (sd ** 2).sum() * 100,
                  "PC1 weight of petal length": abs(vt[0, 2])}
             """, parent_label="NumPy linalg.svd", parent_tolerance=1e-12,
             r="""
                 p <- prcomp(cbind(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width), scale. = TRUE)
                 list(`PC1 standard deviation` = p$sdev[1], `PC1 share (%)` = p$sdev[1]^2 / sum(p$sdev^2) * 100,
                      `PC1 weight of petal length` = abs(p$rotation[3, 1]))
             """, r_tolerance=1e-12,
             note="The sign of a component is arbitrary, so the weight is compared without its sign."),
    ]
