"""Families for 100 %, batches 3-4 (approved by Manish 2026-11-28): the scipy.stats tests, summaries, bins, best powers,
distances, sensitivity and censored fits of plan section 2.2, each next to the SciPy code that does the same job."""

from . import Entry

TOLD = "simplydata also says the answer in a sentence, with the method it used."
TESTED = "simplydata also prints the answer in words, with the test it used, and gives back a one-row result table."


def _summary(option, measure, call, data="marks", column="marks", tolerance=1e-12, choices=(), also=TOLD):
    """An entry for a find_summary_of(show=) measure: the measure of one column against one SciPy call."""
    return Entry(
        word="table.find_summary_of",
        option=option,
        data=data,
        ours=f"""
            table = sdata.get_example("{data}")
            summary = table.find_summary_of("{column}", show=["{measure}"])
            summary.get_cell_at(row=1, column="{measure}")
        """,
        code={"SciPy": f"""
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("{data}.csv")
            # find_summary_of("{column}", show=["{measure}"])
            values = df["{column}"].dropna().to_numpy(dtype=float)
            {call}
        """},
        compare="value",
        tolerance=tolerance,
        choices=choices,
        also=also,
    )


def _test(word, option, ours, call, data="marks", setup="", field="p-value", tolerance=1e-12, choices=(), also=TESTED):
    """An entry for a new test_method= value: one number of the result table against SciPy."""
    return Entry(
        word=word,
        option=option,
        data=data,
        ours=f"""
            table = sdata.get_example("{data}")
            {ours}
            result.get_cell_at(row=1, column="{field}")
        """,
        code={"SciPy": f"""
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("{data}.csv")
            {setup}
            {call}
        """},
        compare="value",
        tolerance=tolerance,
        choices=choices,
        also=also,
    )


MATHS = 'table.keep_rows_where("subject", is_equal_to="Maths")'
MATHS_DF = 'maths = df[df["subject"] == "Maths"]'
TWO_CLASSES = ('table.keep_rows_where("subject", is_equal_to="Maths")\n'
               '            table.keep_rows_where("class", is_one_of=["A", "B"])')
TWO_DF = ('maths = df[df["subject"] == "Maths"]\n'
          '            a, b = (maths.loc[maths["class"] == g, "marks"].dropna() for g in ("A", "B"))')

ENTRIES = [
    # ---------------------------------------------------------------- find_summary_of: the scipy.stats measures
    _summary('show="geometric standard deviation"', "geometric standard deviation",
             "stats.gstd(values)                                    # (1)",
             choices=("the standard deviation of the logs with n - 1 (SciPy's default ddof=1), as R exp(sd(log(x)));"
                      " only for numbers above 0.",)),
    _summary('show="power mean p"', "power mean 3", "stats.pmean(values, 3)"),
    _summary('show="cumulant k"', "cumulant 2",
             "stats.kstat(values, 2)                                # (1)",
             choices=("the unbiased estimate of the cumulant (k-statistic); \"cumulant variance 2\" gives its "
                      "variance (SciPy kstatvar).",)),
    _summary('show="cumulant variance k"', "cumulant variance 2", "stats.kstatvar(values, 2)"),
    _summary('show="l-moment k"', "l-moment 3",
             "stats.lmoment(values, order=3, standardize=False)      # (1)",
             choices=("the L-moment lambda_k itself (standardize=False); \"l-skewness\" and \"l-kurtosis\" are the "
                      "ratios tau_3 and tau_4, SciPy's default and R lmom::samlmu's.",)),
    _summary('show="central moment k"', "central moment 3",
             "stats.moment(values, order=3)                          # (1)",
             choices=("divided by n, around the average (SciPy moment's center=None).",)),
    _summary('show="expectile p"', "expectile 90",
             "stats.expectile(values, alpha=0.9)                     # (1)",
             choices=("written in percent, as percentile 90: expectile 90 is alpha = 0.9.",)),
    _summary('show="average between a and b"', "average between 40 and 80",
             "stats.tmean(values, (40, 80))                          # (1)",
             choices=("both limits included (SciPy's inclusive=(True, True)); the standard deviation, variance "
                      "and standard error the same with n - 1 (tstd, tvar, tsem).",)),
    _summary('show="smallest from a"', "smallest from 50",
             "stats.tmin(values, lowerlimit=50)                      # (1)",
             choices=("the limit included; \"biggest up to 80\" is SciPy tmax(upperlimit=80).",)),
    _summary('show="circular average"', "circular average in degrees",
             "stats.circmean(values, high=360, low=0)                # (1)",
             choices=("angles from 0 to 360 with \"in degrees\", otherwise radians from 0 to 2 pi (SciPy's "
                      "default); circstd and circvar the same.",)),
    _summary('show="differential entropy"', "differential entropy",
             "stats.differential_entropy(values)                     # (1)",
             choices=("SciPy's automatic estimator (Vasicek below 10 values, Ebrahimi from 10 to 1000).",)),
    _summary('show="percentile rank v"', "percentile rank 70",
             "float(stats.estimated_cdf(values, 70)) * 100           # (1)",
             choices=("the inverse of \"percentile p\" (R type 7, SciPy method=\"linear\"), in percent.",)),
    _summary('show="percent at or below v"', "percent at or below 70",
             'stats.percentileofscore(values, 70, kind="weak")      # (1)',
             choices=("the values at or below 70 count (kind=\"weak\"), so it is a plain share in percent.",)),
    _summary('show="sigma-clipped average"', "sigma-clipped average",
             "stats.sigmaclip(values).clipped.mean()                 # (1)",
             choices=("values more than 4 standard deviations from the average are cut, again until none is "
                      "(SciPy's default low=4, high=4); \"sigma-clipped average 3\" cuts at 3.",)),
    # ---------------------------------------------------------------- find_summary_of(in_bins_of=)
    Entry(
        word="table.find_summary_of",
        option="in_bins_of=",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            summary = table.find_summary_of("marks", show=["average"], in_bins_of={"hours": 2})
            summary.get_cell_at(row=2, column="average")
        """,
        code={"SciPy": """
            import numpy as np
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("marks.csv").dropna(subset=["marks", "hours"])
            # find_summary_of("marks", show=["average"], in_bins_of={"hours": 2})
            edges = np.arange(0, 12, 2)                            # (1)
            found = stats.binned_statistic(df["hours"], df["marks"], "mean", bins=edges)
            found.statistic[1]                                     # (2)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("bins 2 wide from the multiple of 2 at or below the smallest value to the first at or above the "
                 "biggest; a bin holds its lower edge, the last one its upper edge too (as binned_statistic).",
                 "bins with no values are left out, where SciPy gives an empty number (NaN).",),
        also="Each row names its bin (\"hours from\", \"hours to\"); every find_summary_of measure works per bin, and "
             "two columns or more make bins of each (binned_statistic_2d, binned_statistic_dd).",
    ),
    Entry(
        word="table.find_summary_of",
        option="in_bins_of= two columns",
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            summary = table.find_summary_of("marks", show=["average"], in_bins_of={"hours": 5, "height": 20})
            summary.get_cell_at(row=1, column="average")
        """,
        code={"SciPy": """
            import numpy as np
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("marks.csv").dropna(subset=["marks", "hours", "height"])
            # find_summary_of("marks", show=["average"], in_bins_of={"hours": 5, "height": 20})
            low = np.floor(df["height"].min() / 20) * 20
            edges = [np.arange(0, 15, 5), np.arange(low, df["height"].max() + 20, 20)]   # (1)
            found = stats.binned_statistic_2d(df["hours"], df["height"], df["marks"], "mean", bins=edges)
            found.statistic[~np.isnan(found.statistic)][0]          # (2)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("each column cut as with one column: bins 5 and 20 wide from a multiple of the width.",
                 "the rows go bin after bin of the first column, then of the second, the empty bins left out.",),
        also=TOLD,
    ),
    Entry(
        word="table.find_summary_of",
        option='show="running count"',
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            summary = table.find_summary_of("hours", show=["running count"], in_bins_of={"hours": 2})
            summary.get_cell_at(row=3, column="running count")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("marks.csv")
            # find_summary_of("hours", show=["running count"], in_bins_of={"hours": 2})
            found = stats.cumfreq(df["hours"].dropna(), numbins=5, defaultreallimits=(0, 10))   # (1)
            found.cumcount[2]
        """},
        compare="value",
        tolerance=0.0,
        choices=("the counts of the bins of in_bins_of= added up in their order; \"share of values\" gives each "
                 "bin's share instead (SciPy relfreq).",),
        also=TOLD,
    ),
    Entry(
        word="table.find_summary_of",
        option='show="share of values"',
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            summary = table.find_summary_of("hours", show=["share of values"], in_bins_of={"hours": 2})
            summary.get_cell_at(row=4, column="share of values")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("marks.csv")
            # find_summary_of("hours", show=["share of values"], in_bins_of={"hours": 2})
            found = stats.relfreq(df["hours"].dropna(), numbins=5, defaultreallimits=(0, 10))   # (1)
            found.frequency[3]
        """},
        compare="value",
        tolerance=1e-12,
        choices=("each bin's count divided by all the values in the bins.",),
        also=TOLD,
    ),
    # ---------------------------------------------------------------- new test_method= values
    _test("table.compare_averages_of", 'test_method="wilcoxon rank sum"',
          TWO_CLASSES + '\n            result = table.compare_averages_of("marks", for_each_group_in="class", '
                        'test_method="wilcoxon rank sum")',
          "stats.ranksums(a, b).pvalue                              # (1)",
          setup=TWO_DF + "\n            # compare_averages_of(\"marks\", for_each_group_in=\"class\", "
                         "test_method=\"wilcoxon rank sum\")",
          choices=("the rank sum against the normal curve, with no continuity correction and no allowance for ties "
                   "(SciPy ranksums); test_method=\"mann-whitney\" is exact for small groups.",)),
    _test("table.compare_averages_of", 'test_method="baumgartner-weiss-schindler"',
          TWO_CLASSES + '\n            result = table.compare_averages_of("marks", for_each_group_in="class", '
                        'test_method="baumgartner-weiss-schindler")',
          "stats.bws_test(a, b, method=shuffles).pvalue             # (1)",
          setup=TWO_DF + "\n            # compare_averages_of(\"marks\", for_each_group_in=\"class\", "
                         "test_method=\"baumgartner-weiss-schindler\")\n"
                         "            import numpy as np\n"
                         "            rng = np.random.default_rng(1)\n"
                         "            shuffles = stats.PermutationMethod(n_resamples=9999, rng=rng)",
          choices=("the p-value from shuffling the group labels: every way when there are fewer than 9999, "
                   "otherwise 9999 random ways with seed 1.",)),
    _test("table.compare_shapes_of", 'test_method="cramer-von mises"',
          TWO_CLASSES + '\n            result = table.compare_shapes_of("marks", for_each_group_in="class", '
                        'test_method="cramer-von mises")',
          "stats.cramervonmises_2samp(a, b).pvalue                  # (1)",
          setup=TWO_DF + "\n            # compare_shapes_of(\"marks\", for_each_group_in=\"class\", "
                         "test_method=\"cramer-von mises\")",
          choices=("SciPy's method=\"auto\": exact when both groups have 20 values or fewer.",)),
    _test("table.compare_shapes_of", 'test_method="epps-singleton"',
          TWO_CLASSES + '\n            result = table.compare_shapes_of("marks", for_each_group_in="class", '
                        'test_method="epps-singleton")',
          "stats.epps_singleton_2samp(a, b).pvalue                  # (1)",
          setup=TWO_DF + "\n            # compare_shapes_of(\"marks\", for_each_group_in=\"class\", "
                         "test_method=\"epps-singleton\")",
          choices=("SciPy's two points t = (0.4, 0.8) and its small-sample correction.",)),
    _test("table.compare_shape_to", 'test_method="skewness"',
          'result = table.compare_shape_to("marks", "normal", test_method="skewness")',
          "stats.skewtest(df[\"marks\"].dropna()).pvalue            # (1)",
          setup='# compare_shape_to("marks", "normal", test_method="skewness")',
          choices=("D'Agostino's test of the skewness alone, from 8 values (as SciPy skewtest).",)),
    _test("table.compare_shape_to", 'test_method="kurtosis"',
          'result = table.compare_shape_to("marks", "normal", test_method="kurtosis")',
          "stats.kurtosistest(df[\"marks\"].dropna()).pvalue        # (1)",
          setup='# compare_shape_to("marks", "normal", test_method="kurtosis")',
          choices=("the Anscombe-Glynn test of the kurtosis alone (SciPy kurtosistest; its warning below 20 values "
                   "is left out).",)),
    _test("table.compare_counts_to", 'test_method="g"',
          'result = table.compare_counts_to("breakfast", expected={"yes": 0.6, "no": 0.4}, test_method="g")',
          'stats.power_divergence(seen, seen.sum() * shares, lambda_="log-likelihood").pvalue   # (1)',
          data="school",
          setup='# compare_counts_to("breakfast", expected={"yes": 0.6, "no": 0.4}, test_method="g")\n'
                '            counts = df["breakfast"].value_counts()\n'
                '            seen = counts[["no", "yes"]].to_numpy(float)\n'
                "            shares = pd.Series([0.4, 0.6]).to_numpy()",
          choices=("the G-test (lambda_=\"log-likelihood\"); \"freeman-tukey\", \"neyman\", \"modified g\" and "
                   "\"cressie-read\" are the other lambda_ values of power_divergence.",)),
    _test("table.compare_spreads_of", 'test_method="o\'brien"',
          MATHS + '\n            result = table.compare_spreads_of("marks", for_each_group_in="class", '
                  "test_method=\"o'brien\")",
          "stats.f_oneway(*stats.obrientransform(*groups)).pvalue  # (1)",
          setup=MATHS_DF + "\n            # compare_spreads_of(\"marks\", for_each_group_in=\"class\", "
                           "test_method=\"o'brien\")\n"
                           '            groups = [g["marks"].dropna() for _, g in maths.groupby("class")]',
          choices=("the one-way ANOVA of O'Brien's scores, whose group averages are the group variances.",)),
    Entry(
        word="table.find_correlation_between",
        option='test_method="chatterjee xi"',
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_rows_where("subject", is_equal_to="Maths")
            table.find_correlation_between("hours", "marks", test_method="chatterjee xi")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("marks.csv")
            # find_correlation_between("hours", "marks", test_method="chatterjee xi")
            maths = df[df["subject"] == "Maths"].dropna(subset=["hours", "marks"])
            stats.chatterjeexi(maths["hours"], maths["marks"]).statistic   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("xi of the second column given the first (it is not symmetric); ties broken as SciPy does, "
                 "y_continuous=False.",),
        also="simplydata also prints the p-value and what xi measures.",
    ),
    Entry(
        word="table.find_correlation_between",
        option='test_method="weighted kendall"',
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_rows_where("subject", is_equal_to="Maths")
            table.find_correlation_between("hours", "marks", test_method="weighted kendall")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("marks.csv")
            # find_correlation_between("hours", "marks", test_method="weighted kendall")
            maths = df[df["subject"] == "Maths"].dropna(subset=["hours", "marks"])
            stats.weightedtau(maths["hours"], maths["marks"]).statistic    # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("SciPy's hyperbolic weights, ranked by both columns (rank=True).",),
        also=TOLD,
    ),
    Entry(
        word="table.find_correlation_between",
        option='test_method="multiscale graph"',
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            table.keep_rows_where("subject", is_equal_to="Maths")
            table.find_correlation_between("hours", "marks", test_method="multiscale graph")
        """,
        code={"SciPy": """
            import numpy as np
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("marks.csv")
            # find_correlation_between("hours", "marks", test_method="multiscale graph")
            maths = df[df["subject"] == "Maths"].dropna(subset=["hours", "marks"])
            x, y = maths["hours"].to_numpy(), maths["marks"].to_numpy()
            stats.multiscale_graphcorr(x, y, reps=1000, random_state=np.random.default_rng(1)).statistic   # (1)
        """},
        compare="value",
        tolerance=1e-10,
        choices=("1000 shuffles for the p-value, seed 1 (printed).",),
        also="simplydata also prints the p-value.",
    ),
    _test("table.compare_rates", 'test_method="e-test"',
          'result = table.compare_rates("infections", time="patient_days", for_each_group_in="ward", '
          'against="ward A", test_method="e-test")',
          "stats.poisson_means_test(k1, n1, k2, n2).pvalue          # (1)",
          data="clinic",
          setup='# compare_rates("infections", time="patient_days", for_each_group_in="ward", test_method="e-test")\n'
                '            sums = df.groupby("ward")[["infections", "patient_days"]].sum()\n'
                '            (k1, n1), (k2, n2) = sums.loc["ward B"], sums.loc["ward A"]',
          choices=("the other group against against=, with diff=0 (equal rates).",)),
    Entry(
        word="table.find_interval_of",
        option='test_method="bayesian"',
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            interval = table.find_interval_of("marks", "average", test_method="bayesian")
            interval.get_cell_at(row=1, column="average of marks 95 % CI low")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("marks.csv")
            # find_interval_of("marks", "average", test_method="bayesian")
            average, variance, spread = stats.bayes_mvs(df["marks"].dropna(), alpha=0.95)
            average.minmax[0]                                       # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("Jeffreys' uninformative prior, as SciPy bayes_mvs; \"variance\" and \"standard deviation\" take "
                 "its other two parts.",),
        also=TOLD,
    ),
    Entry(
        word="table.combine_studies",
        option="p_values=",
        data="many_tests",
        ours="""
            table = sdata.get_example("many_tests")
            table.keep_first_rows(10)
            result = table.combine_studies(names="gene", p_values="p-value", test_method="fisher")
            result.get_cell_at(row=1, column="p-value")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("many_tests.csv").head(10)
            # combine_studies(names="gene", p_values="p-value", test_method="fisher")
            stats.combine_pvalues(df["p-value"], method="fisher").pvalue   # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("Fisher's method when test_method= is left out (\"stouffer\", \"pearson\", \"tippett\" and "
                 "\"mudholkar-george\" are SciPy's others); no R needed.",),
        also=TESTED,
    ),
    # ---------------------------------------------------------------- find_best_power_of
    Entry(
        word="table.find_best_power_of",
        option='show="log-likelihood"',
        data="trial",
        ours="""
            table = sdata.get_example("trial")
            powers = table.find_best_power_of("days", show="log-likelihood")
            powers.get_cell_at(row=21, column="log-likelihood")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("trial.csv")
            # find_best_power_of("days", show="log-likelihood")
            stats.boxcox_llf(0.0, df["days"].dropna())               # (1)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the powers -2 to 2 in steps of 0.1 (row 21 is power 0, the log); yeojohnson_llf with "
                 "test_method=\"yeo-johnson\".",),
        also=TOLD,
    ),
    Entry(
        word="table.find_best_power_of",
        option='show="normal plot correlation"',
        data="trial",
        ours="""
            table = sdata.get_example("trial")
            powers = table.find_best_power_of("days", show="normal plot correlation")
            powers.get_cell_at(row=31, column="normal plot correlation")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("trial.csv")
            # find_best_power_of("days", show="normal plot correlation")
            powers, found = stats.boxcox_normplot(df["days"].dropna(), -2, 2, N=41)   # (1)
            found[30]
        """},
        compare="value",
        tolerance=1e-12,
        choices=("41 powers from -2 to 2 (SciPy N=41); yeojohnson_normplot with test_method=\"yeo-johnson\" and "
                 "ppcc_plot of the Tukey lambda shape with test_method=\"tukey lambda\".",),
        also=TOLD,
    ),
    Entry(
        word="table.find_best_power_of",
        option='show="best by normal plot"',
        data="trial",
        ours="""
            table = sdata.get_example("trial")
            best = table.find_best_power_of("days", show="best by normal plot")
            best.get_cell_at(row=1, column="power")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("trial.csv")
            # find_best_power_of("days", show="best by normal plot")
            stats.boxcox_normmax(df["days"].dropna(), method="pearsonr")   # (1)
        """},
        compare="value",
        tolerance=1e-9,
        choices=("the Box-Cox power with the straightest normal probability plot; show=\"power\" (the default) is "
                 "the one by maximum likelihood.",),
        also=TOLD,
    ),
    Entry(
        word="table.find_best_power_of",
        option='test_method="tukey lambda"',
        data="trial",
        ours="""
            table = sdata.get_example("trial")
            best = table.find_best_power_of("days", test_method="tukey lambda")
            best.get_cell_at(row=1, column="lambda")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("trial.csv")
            # find_best_power_of("days", test_method="tukey lambda")
            stats.ppcc_max(df["days"].dropna())                       # (1)
        """},
        compare="value",
        tolerance=1e-9,
        choices=("the Tukey lambda shape (SciPy's default dist=\"tukeylambda\") whose probability plot correlation "
                 "is biggest.",),
        also="simplydata also says which usual shape the lambda is close to (Cauchy, logistic, normal, uniform).",
    ),
    # ---------------------------------------------------------------- compare_distributions_for(show=)
    Entry(
        word="table.compare_distributions_for",
        option='show="wasserstein distance"',
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            result = table.compare_distributions_for("marks", for_each_group_in="class", show="wasserstein distance")
            result.get_cell_at(row=1, column="wasserstein distance")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("marks.csv").dropna(subset=["marks"])
            # compare_distributions_for("marks", for_each_group_in="class", show="wasserstein distance")
            a, b = (df.loc[df["class"] == g, "marks"] for g in ("A", "B"))   # (1)
            stats.wasserstein_distance(a, b)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("one row per pair of groups, in sorted order (A and B first); a list of columns uses "
                 "wasserstein_distance_nd.",),
        also=TOLD,
    ),
    Entry(
        word="table.compare_distributions_for",
        option='show="energy distance"',
        data="marks",
        ours="""
            table = sdata.get_example("marks")
            result = table.compare_distributions_for("marks", for_each_group_in="class", show="energy distance")
            result.get_cell_at(row=3, column="energy distance")
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("marks.csv").dropna(subset=["marks"])
            # compare_distributions_for("marks", for_each_group_in="class", show="energy distance")
            b, c = (df.loc[df["class"] == g, "marks"] for g in ("B", "C"))   # (1)
            stats.energy_distance(b, c)
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the pairs in sorted order: A and B, A and C, then B and C (row 3).",),
        also=TOLD,
    ),
    # ---------------------------------------------------------------- the new word and the censored fit
    Entry(
        word="sdata.find_sensitivity_of",
        ours="""
            answer = sdata.find_sensitivity_of("a * x**2 + b", ranges={"a": [0, 1], "b": [0, 5], "x": [0, 2]})
            answer.get_cell_at(row=3, column="total index")
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import stats
            # find_sensitivity_of("a * x**2 + b", ranges={"a": [0, 1], "b": [0, 5], "x": [0, 2]})
            def formula(p):                                       # (1): a, x, b
                return (p[0] * p[1] ** 2 + p[2]).reshape(1, -1)
            dists = [stats.uniform(0, 1), stats.uniform(0, 2), stats.uniform(0, 5)]
            found = stats.sobol_indices(func=formula, n=1024, dists=dists, rng=np.random.default_rng(1))   # (2)
            found.total_order.ravel()[2]
        """},
        compare="value",
        tolerance=1e-12,
        choices=("the names in the order they first turn up in the formula, each spread evenly over its range.",
                 "1024 points in each base sample and seed 1 unless how_many= and with_seed= say otherwise.",),
        also="simplydata also names the input that matters most and gives a table with both indices per input.",
    ),
    Entry(
        word="table.fit_distribution_to",
        option="censored_by=",
        data="trial",
        ours="""
            table = sdata.get_example("trial")
            table.add_group_column("still_alive", rules={'died == "no"': "yes"}, otherwise="no")
            fit = table.fit_distribution_to("days", "weibull", censored_by="still_alive")
            fit.find_percentile(50)
        """,
        code={"SciPy": """
            import pandas as pd
            from scipy import stats
            df = pd.read_csv("trial.csv")
            # fit_distribution_to("days", "weibull", censored_by="still_alive")
            seen, alive = df.loc[df["died"] == "yes", "days"], df.loc[df["died"] == "no", "days"]
            data = stats.CensoredData(uncensored=seen, right=alive)          # (1)
            shape, _, scale = stats.weibull_min.fit(data, floc=0)            # (2)
            stats.weibull_min(shape, scale=scale).ppf(0.5)                  # the middle value
        """},
        compare="value",
        tolerance=1e-4,
        choices=("the rows where censored_by= says yes are right-censored: their value is only a lower limit.",
                 "no location for the Weibull, as R; simplydata polishes SciPy's search, so the two agree to about "
                 "5 digits.",),
        also="simplydata also gives the log-likelihood and AIC and says how many values were censored; it gives no "
             "standard errors for a censored fit (no package it uses gives them).",
    ),
]
