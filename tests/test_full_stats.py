"""Families for 100 %, batches 3-4 (approved by Manish 2026-11-28): the SciPy statistics of plan section 2.2 (tests,
summaries, bins, best powers, distances, sensitivity and censored fits). Each new option and value is checked
against scipy.stats itself, on both table engines where a table is used."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest
from scipy import stats

import simplydata as sdata
from simplydata._errors import SimplydataError

ENGINES = [False, True]  # pandas, then Polars (fast=True)


def _table(name, fast=False):
    return sdata.table(sdata.get_example(name), fast=fast)


def _frame(name):
    return sdata.get_example(name).as_pandas()


def _maths(fast=False):
    """One subject of the marks table: one row per child."""
    table = _table("marks", fast)
    table.keep_rows_where("subject", is_equal_to="Maths")
    return table


def _cell(result, column, row=1):
    return result.get_cell_at(row=row, column=column)


# ---------------------------------------------------------------- find_summary_of: the new measures
MEASURES = [
    ("geometric standard deviation", lambda v: stats.gstd(v)),
    ("power mean 3", lambda v: stats.pmean(v, 3)),
    ("power mean -1", lambda v: stats.pmean(v, -1)),
    ("cumulant 2", lambda v: stats.kstat(v, 2)),
    ("cumulant 4", lambda v: stats.kstat(v, 4)),
    ("cumulant variance 2", lambda v: stats.kstatvar(v, 2)),
    ("l-moment 2", lambda v: stats.lmoment(v, order=2)),
    ("l-moment 3", lambda v: stats.lmoment(v, order=3, standardize=False)),
    ("l-skewness", lambda v: stats.lmoment(v, order=3)),
    ("l-kurtosis", lambda v: stats.lmoment(v, order=4)),
    ("central moment 3", lambda v: stats.moment(v, order=3)),
    ("expectile 90", lambda v: stats.expectile(v, alpha=0.9)),
    ("average between 40 and 80", lambda v: stats.tmean(v, (40, 80))),
    ("standard deviation between 40 and 80", lambda v: stats.tstd(v, (40, 80))),
    ("variance between 40 and 80", lambda v: stats.tvar(v, (40, 80))),
    ("standard error between 40 and 80", lambda v: stats.tsem(v, (40, 80))),
    ("smallest from 50", lambda v: stats.tmin(v, lowerlimit=50)),
    ("biggest up to 80", lambda v: stats.tmax(v, upperlimit=80)),
    ("circular average in radians", lambda v: stats.circmean(v)),
    ("circular standard deviation in degrees", lambda v: stats.circstd(v, high=360)),
    ("circular variance in radians", lambda v: stats.circvar(v)),
    ("circular average in hours", lambda v: stats.circmean(v, high=24)),
    ("differential entropy", lambda v: stats.differential_entropy(v)),
    ("percentile rank 70", lambda v: stats.estimated_cdf(v, 70) * 100),
    ("percent at or below 70", lambda v: stats.percentileofscore(v, 70, kind="weak")),
    ("sigma-clipped average", lambda v: np.mean(stats.sigmaclip(v).clipped)),
    ("sigma-clipped average 1.5", lambda v: np.mean(stats.sigmaclip(v, 1.5, 1.5).clipped)),
]


@pytest.mark.parametrize("fast", ENGINES)
@pytest.mark.parametrize("name, scipy_measure", MEASURES, ids=[m[0] for m in MEASURES])
def test_each_new_summary_measure_matches_scipy_for_each_group(name, scipy_measure, fast, capsys):
    df = _frame("marks")
    result = _table("marks", fast).find_summary_of("marks", show=[name], for_each_group_in="class")
    for row, (group, part) in enumerate(df.dropna(subset=["marks"]).groupby("class"), start=1):
        assert _cell(result, "class", row) == group
        assert _cell(result, name, row) == pytest.approx(float(scipy_measure(part["marks"].to_numpy(float))),
                                                         rel=1e-12, abs=1e-12)
    assert f"{name} " in capsys.readouterr().out


def test_scipy_names_of_the_measures_and_their_numbers_are_read(capsys):
    table = _maths()
    result = table.find_summary_of("marks", show=["gstd", "pmean 2", "kstat 3", "circmean in degrees"])
    v = _frame("marks").query("subject == 'Maths'")["marks"].to_numpy(float)
    assert _cell(result, "geometric standard deviation") == pytest.approx(stats.gstd(v), rel=1e-12)
    assert _cell(result, "power mean 2") == pytest.approx(stats.pmean(v, 2), rel=1e-12)
    assert _cell(result, "cumulant 3") == pytest.approx(stats.kstat(v, 3), rel=1e-12)
    assert _cell(result, "circular average in degrees") == pytest.approx(stats.circmean(v, high=360), rel=1e-12)


@pytest.mark.parametrize("show", ["circular average", "circular standard deviation", "circular variance", "circmean"])
def test_circular_measures_need_the_unit_of_the_angles(show):
    # degrees such as 350, 10, 20, 5, 355 were read as radians before: the unit must now be written
    df = pd.DataFrame({"angle": [350.0, 10.0, 20.0, 5.0, 355.0]})
    with pytest.raises(SimplydataError, match="needs the unit of the angles"):
        sdata.table(df).find_summary_of("angle", show=[show])
    found = sdata.table(df).find_summary_of("angle", show=["circular average in degrees"])
    assert _cell(found, "circular average in degrees") == pytest.approx(stats.circmean(df["angle"], high=360))


def test_each_new_measure_prints_its_method_and_units(capsys):
    df = pd.DataFrame({"angle": [350.0, 10.0, 20.0, 5.0, 355.0, 3.0, 8.0, 12.0, 351.0, 2.0, 4.0]})
    sdata.table(df).find_summary_of("angle", show=["circular average in degrees", "circular variance in degrees",
                                                   "differential entropy", "l-skewness", "percentile rank 10"])
    out = capsys.readouterr().out
    assert 'Method of "circular average in degrees":' in out and "the answer in degrees" in out
    assert "with no unit" in out and "in nats" in out and "tau_3" in out and "inverse of" in out


def test_l_moments_are_named_for_what_they_are():
    v = _frame("marks")["marks"].dropna().to_numpy(float)
    found = _table("marks").find_summary_of("marks", show=["l-moment 3", "l-skewness"])
    assert _cell(found, "l-moment 3") == pytest.approx(stats.lmoment(v, order=3, standardize=False), rel=1e-12)
    assert _cell(found, "l-skewness") == pytest.approx(stats.lmoment(v, order=3), rel=1e-12)
    assert _cell(found, "l-moment 3") != pytest.approx(_cell(found, "l-skewness"))


def test_in_bins_of_with_a_decimal_width_puts_values_on_an_edge_in_the_right_bin(capsys):
    df = pd.DataFrame({"depth": [3.82, 3.9, 3.95, 4.0, 4.05], "oxygen": [1.0, 2.0, 3.0, 4.0, 5.0]})
    result = sdata.table(df).find_summary_of("oxygen", show=["count", "total"], in_bins_of={"depth": 0.1})
    assert result.get_column("depth from").as_numpy().tolist() == [3.8, 3.9, 4.0]
    assert result.get_column("depth to").as_numpy().tolist() == [3.9, 4.0, 4.1]
    assert result.get_column("total").as_numpy().tolist() == [1.0, 5.0, 9.0]  # 3.9 in [3.9, 4.0), 4.0 in [4.0, 4.1]
    assert "3.8000000000000003" not in capsys.readouterr().out


@pytest.mark.parametrize("show, says", [
    ("cumulant 5", "from 1 to 4"), ("cumulant variance 3", "from 1 to 2"), ("expectile 100", "in percent"),
    ("power mean 0", "geometric mean"), ("average between 80 and 40", "lower limit first"),
    ("power mean", "needs a number after it"), ("running count", "needs in_bins_of="),
])
def test_new_measures_say_what_is_wrong(show, says):
    with pytest.raises(SimplydataError, match=says):
        _maths().find_summary_of("marks", show=[show])


def test_a_measure_with_too_few_values_or_no_positive_numbers_is_empty_with_a_note(capsys):
    df = pd.DataFrame({"g": ["a", "a", "b", "b", "b"], "x": [-1.0, 2.0, 3.0, 4.0, 5.0]})
    result = sdata.table(df).find_summary_of("x", show=["geometric standard deviation", "smallest from 10"],
                                             for_each_group_in="g")
    assert _cell(result, "geometric standard deviation", 1) is None
    assert _cell(result, "geometric standard deviation", 2) == pytest.approx(stats.gstd([3.0, 4.0, 5.0]))
    out = capsys.readouterr().out
    assert "needs numbers above 0" in out and "has no value of 10 or more" in out


# ---------------------------------------------------------------- find_summary_of(in_bins_of=)
@pytest.mark.parametrize("fast", ENGINES)
def test_in_bins_of_matches_scipy_binned_statistic(fast, capsys):
    df = _frame("marks").dropna(subset=["marks", "hours"])
    result = _table("marks", fast).find_summary_of("marks", show=["average", "count", "median"],
                                                   in_bins_of={"hours": 2})
    edges = np.arange(0, 12, 2.0)  # hours run from 0 to 10: bins of 2 from 0, the last one holding 10
    means = stats.binned_statistic(df["hours"], df["marks"], "mean", bins=edges)
    counts = stats.binned_statistic(df["hours"], df["marks"], "count", bins=edges).statistic
    medians = stats.binned_statistic(df["hours"], df["marks"], "median", bins=edges).statistic
    kept = counts > 0
    assert result.count_rows() == int(kept.sum())
    assert result.get_column("hours from").as_numpy().tolist() == edges[:-1][kept].tolist()
    assert result.get_column("hours to").as_numpy().tolist() == edges[1:][kept].tolist()
    assert result.get_column("average").as_numpy() == pytest.approx(means.statistic[kept], rel=1e-12)
    assert result.get_column("count").as_numpy().tolist() == counts[kept].tolist()
    assert result.get_column("median").as_numpy() == pytest.approx(medians[kept], rel=1e-12)
    out = capsys.readouterr().out
    assert 'Summary of "marks" in bins of "hours" in 5 bins 2 wide, from 0 to 10' in out
    assert "SciPy binned_statistic" in out


def test_in_bins_of_with_edges_leaves_out_values_outside_them_as_scipy(capsys):
    df = _frame("marks").dropna(subset=["marks", "hours"])
    edges = [1, 3, 6, 9]
    result = _table("marks").find_summary_of("marks", show=["total"], in_bins_of={"hours": edges})
    found = stats.binned_statistic(df["hours"], df["marks"], "sum", bins=edges).statistic
    assert result.get_column("total").as_numpy() == pytest.approx(found, rel=1e-12)
    assert "values outside them left out" in capsys.readouterr().out


@pytest.mark.parametrize("fast", ENGINES)
def test_in_bins_of_two_columns_matches_binned_statistic_2d(fast):
    df = _frame("marks").dropna(subset=["marks", "hours", "height"])
    result = _table("marks", fast).find_summary_of("marks", show=["average"], in_bins_of={"hours": 5,
                                                                                          "height": 20})
    x_edges = np.arange(0, 15, 5.0)
    low = math.floor(df["height"].min() / 20) * 20
    y_edges = np.arange(low, df["height"].max() + 20, 20.0)
    found = stats.binned_statistic_2d(df["hours"], df["height"], df["marks"], "mean", bins=[x_edges, y_edges])
    expected = []
    for i in range(len(x_edges) - 1):
        for j in range(len(y_edges) - 1):
            if not np.isnan(found.statistic[i, j]):
                expected.append((x_edges[i], y_edges[j], found.statistic[i, j]))
    got = list(zip(result.get_column("hours from").as_numpy(), result.get_column("height from").as_numpy(),
                   result.get_column("average").as_numpy()))
    assert len(got) == len(expected)
    for (a, b, m), (c, d, e) in zip(sorted(got), sorted(expected)):
        assert (a, b) == (c, d) and m == pytest.approx(e, rel=1e-12)


def test_running_count_and_share_of_values_match_cumfreq_and_relfreq():
    df = _frame("marks").dropna(subset=["hours"])
    result = _table("marks").find_summary_of("hours", show=["running count", "share of values"],
                                             in_bins_of={"hours": 2})
    cumulative = stats.cumfreq(df["hours"], numbins=5, defaultreallimits=(0, 10)).cumcount
    relative = stats.relfreq(df["hours"], numbins=5, defaultreallimits=(0, 10)).frequency
    assert result.get_column("running count").as_numpy().tolist() == cumulative.tolist()
    assert result.get_column("share of values").as_numpy() == pytest.approx(relative, rel=1e-12)
    assert "count" not in result.get_column_names()


# ---------------------------------------------------------------- tests: new test_method= values
@pytest.mark.parametrize("fast", ENGINES)
def test_wilcoxon_rank_sum_and_bws_match_scipy(fast, capsys):
    table = _maths(fast)
    table.keep_rows_where("class", is_one_of=["A", "B"])
    df = _frame("marks").query("subject == 'Maths' and `class` in ['A', 'B']")
    a, b = (df.loc[df["class"] == g, "marks"].dropna().to_numpy(float) for g in ("A", "B"))
    result = table.compare_averages_of("marks", for_each_group_in="class", test_method="wilcoxon rank sum")
    found = stats.ranksums(a, b)
    assert _cell(result, "statistic") == pytest.approx(found.statistic, rel=1e-12)
    assert _cell(result, "p-value") == pytest.approx(found.pvalue, rel=1e-12)
    result = table.compare_averages_of("marks", for_each_group_in="class", test_method="ranksums", sides=1,
                                       higher="A")
    assert _cell(result, "p-value") == pytest.approx(stats.ranksums(a, b, alternative="greater").pvalue, rel=1e-12)
    result = table.compare_averages_of("marks", for_each_group_in="class", test_method="baumgartner-weiss-schindler")
    found = stats.bws_test(a, b, method=stats.PermutationMethod(n_resamples=9999, rng=np.random.default_rng(1)))
    assert _cell(result, "statistic") == pytest.approx(found.statistic, rel=1e-12)
    assert _cell(result, "p-value") == pytest.approx(found.pvalue, rel=1e-12)
    out = capsys.readouterr().out
    assert "Test: Wilcoxon rank-sum test" in out and "Test: Baumgartner-Weiss-Schindler test" in out


def test_two_group_rank_tests_refuse_three_groups():
    with pytest.raises(SimplydataError, match="compares exactly 2 groups"):
        _maths().compare_averages_of("marks", for_each_group_in="class", test_method="wilcoxon rank sum")


@pytest.mark.parametrize("fast", ENGINES)
@pytest.mark.parametrize("test, scipy_test", [
    ("cramer-von mises", lambda a, b: stats.cramervonmises_2samp(a, b)),
    ("epps-singleton", lambda a, b: stats.epps_singleton_2samp(a, b)),
    ("anderson-darling", None),
])
def test_compare_shapes_of_new_tests_match_scipy(test, scipy_test, fast, capsys):
    table = _maths(fast)
    table.keep_rows_where("class", is_one_of=["A", "C"])
    df = _frame("marks").query("subject == 'Maths' and `class` in ['A', 'C']")
    a, c = (df.loc[df["class"] == g, "marks"].dropna().to_numpy(float) for g in ("A", "C"))
    result = table.compare_shapes_of("marks", for_each_group_in="class", test_method=test)
    if scipy_test is None:
        found = stats.anderson_ksamp([a, c], midrank=True)
    else:
        found = scipy_test(a, c)
    assert _cell(result, "statistic") == pytest.approx(found.statistic, rel=1e-10)
    if scipy_test is not None:
        assert _cell(result, "p-value") == pytest.approx(found.pvalue, rel=1e-10)
    assert "which compares the whole shapes" in capsys.readouterr().out


def test_compare_shapes_of_two_group_tests_refuse_three_groups():
    with pytest.raises(SimplydataError, match="compares 2 groups"):
        _maths().compare_shapes_of("marks", for_each_group_in="class", test_method="cramer-von mises")


@pytest.mark.parametrize("test, scipy_test", [("skewness", stats.skewtest), ("kurtosis", stats.kurtosistest),
                                              ("skewtest", stats.skewtest)])
def test_compare_shape_to_skewness_and_kurtosis_tests_match_scipy(test, scipy_test, capsys):
    df = _frame("marks")  # 18 values in each class (the skewness test needs 8)
    result = _table("marks").compare_shape_to("marks", "normal", for_each_group_in="class", test_method=test)
    for row, (_, part) in enumerate(df.groupby("class"), start=1):
        found = scipy_test(part["marks"].dropna().to_numpy(float))
        assert _cell(result, "statistic", row) == pytest.approx(found.statistic, rel=1e-12)
        assert _cell(result, "p-value", row) == pytest.approx(found.pvalue, rel=1e-12)


@pytest.mark.parametrize("test, lam", [("g", "log-likelihood"), ("freeman-tukey", "freeman-tukey"),
                                       ("neyman", "neyman"), ("modified g", "mod-log-likelihood"),
                                       ("cressie-read", "cressie-read")])
def test_compare_counts_to_power_divergence_family_matches_scipy(test, lam, capsys):
    table = _table("school")
    df = _frame("school")
    result = table.compare_counts_to("breakfast", expected={"yes": 0.6, "no": 0.4}, test_method=test)
    counts = df["breakfast"].value_counts()
    observed = np.array([counts["no"], counts["yes"]], dtype=float)
    found = stats.power_divergence(observed, observed.sum() * np.array([0.4, 0.6]), lambda_=lam)
    assert _cell(result, "statistic") == pytest.approx(found.statistic, rel=1e-12)
    assert _cell(result, "p-value") == pytest.approx(found.pvalue, rel=1e-12)
    assert "power_divergence" in capsys.readouterr().out


@pytest.mark.parametrize("fast", ENGINES)
def test_obrien_test_matches_scipy_obrientransform_then_f_oneway(fast):
    df = _frame("marks").query("subject == 'Maths'")
    groups = [g["marks"].dropna().to_numpy(float) for _, g in df.groupby("class")]
    result = _maths(fast).compare_spreads_of("marks", for_each_group_in="class", test_method="o'brien")
    found = stats.f_oneway(*stats.obrientransform(*groups))
    assert _cell(result, "statistic") == pytest.approx(found.statistic, rel=1e-12)
    assert _cell(result, "p-value") == pytest.approx(found.pvalue, rel=1e-12)


def test_new_correlation_measures_match_scipy(capsys):
    df = _frame("marks").query("subject == 'Maths'").dropna(subset=["hours", "marks"])
    x, y = df["hours"].to_numpy(float), df["marks"].to_numpy(float)
    table = _maths()
    assert table.find_correlation_between("hours", "marks", test_method="chatterjee xi") == pytest.approx(
        stats.chatterjeexi(x, y).statistic, rel=1e-12)
    assert table.find_correlation_between("hours", "marks", test_method="weightedtau") == pytest.approx(
        stats.weightedtau(x, y).statistic, rel=1e-12)
    found = stats.multiscale_graphcorr(x, y, reps=1000, random_state=np.random.default_rng(1))
    assert table.find_correlation_between("hours", "marks", test_method="multiscale graph") == pytest.approx(
        found.statistic, rel=1e-10)
    out = capsys.readouterr().out
    assert "Chatterjee's xi" in out and f"p = {found.pvalue:.3f}".replace("p = 0.000", "p < 0.001")[:5] in out


def test_new_correlation_measures_take_two_columns_only():
    with pytest.raises(SimplydataError, match="two columns"):
        _maths().find_correlation_between("hours", "marks", "height", test_method="chatterjee xi")


def test_e_test_of_two_rates_matches_scipy_poisson_means_test(capsys):
    df = _frame("clinic")
    sums = df.groupby("ward")[["infections", "patient_days"]].sum()
    result = _table("clinic").compare_rates("infections", time="patient_days", for_each_group_in="ward",
                                            against="ward A", test_method="e-test")
    found = stats.poisson_means_test(int(sums.loc["ward B", "infections"]), sums.loc["ward B", "patient_days"],
                                     int(sums.loc["ward A", "infections"]), sums.loc["ward A", "patient_days"])
    assert _cell(result, "statistic") == pytest.approx(found.statistic, rel=1e-12)
    assert _cell(result, "p-value") == pytest.approx(found.pvalue, rel=1e-12)
    assert "poisson_means_test" in capsys.readouterr().out


@pytest.mark.parametrize("summary, place", [("average", 0), ("variance", 1), ("standard deviation", 2)])
def test_bayesian_interval_matches_scipy_bayes_mvs(summary, place):
    df = _frame("marks").query("subject == 'Maths'")
    result = _maths().find_interval_of("marks", summary, for_each_group_in="class", test_method="bayesian")
    for row, (_, part) in enumerate(df.groupby("class"), start=1):
        found = stats.bayes_mvs(part["marks"].dropna().to_numpy(float), alpha=0.95)[place]
        assert _cell(result, f"{summary} of marks", row) == pytest.approx(found.statistic, rel=1e-12)
        assert _cell(result, f"{summary} of marks 95 % CI low", row) == pytest.approx(found.minmax[0], rel=1e-12)
        assert _cell(result, f"{summary} of marks 95 % CI high", row) == pytest.approx(found.minmax[1], rel=1e-12)


@pytest.mark.parametrize("method, scipy_method", [("fisher", "fisher"), ("stouffer", "stouffer"),
                                                  ("pearson", "pearson"), ("tippett", "tippett"),
                                                  ("mudholkar-george", "mudholkar_george")])
def test_combine_studies_p_values_matches_scipy_combine_pvalues(method, scipy_method, capsys):
    df = pd.DataFrame({"study": ["a", "b", "c", "d"], "p": [0.04, 0.20, 0.11, 0.35], "n": [40, 120, 60, 25]})
    result = sdata.table(df).combine_studies(names="study", p_values="p", test_method=method)
    found = stats.combine_pvalues(df["p"], method=scipy_method)
    assert _cell(result, "statistic") == pytest.approx(found.statistic, rel=1e-12)
    assert _cell(result, "p-value") == pytest.approx(found.pvalue, rel=1e-12)
    weighted = sdata.table(df).combine_studies(p_values="p", test_method="stouffer", counts="n")
    assert _cell(weighted, "p-value") == pytest.approx(
        stats.combine_pvalues(df["p"], method="stouffer", weights=np.sqrt(df["n"])).pvalue, rel=1e-12)


# ---------------------------------------------------------------- find_best_power_of(show=, test_method="tukey lambda")
def test_best_power_tables_match_scipy_llf_and_normplot():
    days = _frame("trial")["days"].to_numpy(float)
    table = _table("trial")
    powers = np.linspace(-2, 2, 41)
    found = table.find_best_power_of("days", show="log-likelihood")
    assert found.get_column("log-likelihood").as_numpy() == pytest.approx([stats.boxcox_llf(p, days) for p in powers],
                                                                          rel=1e-12)
    found = table.find_best_power_of("days", test_method="yeo-johnson", show="log-likelihood")
    assert found.get_column("log-likelihood").as_numpy() == pytest.approx(
        [stats.yeojohnson_llf(p, days) for p in powers], rel=1e-12)
    found = table.find_best_power_of("days", show="normal plot correlation")
    assert found.get_column("normal plot correlation").as_numpy() == pytest.approx(
        stats.boxcox_normplot(days, -2, 2, N=41)[1], rel=1e-12)
    found = table.find_best_power_of("days", test_method="yeo-johnson", show="normal plot correlation")
    assert found.get_column("normal plot correlation").as_numpy() == pytest.approx(
        stats.yeojohnson_normplot(days, -2, 2, N=41)[1], rel=1e-12)


def test_review_wording_energy_units_pearson_statistic_and_no_false_r_claims(capsys):
    df = _frame("marks")
    sdata.table(df).compare_distributions_for("marks", for_each_group_in="class", show="energy distance")
    assert "square root of the values' units" in capsys.readouterr().out
    p = pd.DataFrame({"p": [0.04, 0.2, 0.11]})
    result = sdata.table(p).combine_studies(p_values="p", test_method="pearson")
    assert _cell(result, "statistic name") != "chi-square" and _cell(result, "statistic") <= 0
    table = _maths()
    table.keep_rows_where("class", is_one_of=["A", "B"])
    table.compare_shapes_of("marks", for_each_group_in="class", test_method="cramer-von mises")
    table.find_correlation_between("hours", "marks", test_method="chatterjee xi")
    out = capsys.readouterr().out
    assert "as R twosamples" not in out and "one-sided" in out
    assert "HH::hov" not in (type(table).compare_spreads_of.__doc__ or "")


def test_best_power_by_normal_plot_and_tukey_lambda_match_scipy(capsys):
    days = _frame("trial")["days"].to_numpy(float)
    table = _table("trial")
    assert _cell(table.find_best_power_of("days", show="best by normal plot"), "power") == pytest.approx(
        stats.boxcox_normmax(days, method="pearsonr"), rel=1e-9)
    assert _cell(table.find_best_power_of("days", test_method="tukey lambda"), "lambda") == pytest.approx(
        stats.ppcc_max(days), rel=1e-9)
    found = table.find_best_power_of("days", test_method="tukey lambda", show="normal plot correlation")
    assert found.get_column("normal plot correlation").as_numpy() == pytest.approx(
        stats.ppcc_plot(days, -2, 2, dist="tukeylambda", N=41)[1], rel=1e-12)
    assert "ppcc_max" in capsys.readouterr().out


# ---------------------------------------------------------------- compare_distributions_for(show=)
@pytest.mark.parametrize("fast", ENGINES)
def test_distances_between_groups_match_scipy(fast, capsys):
    df = _frame("marks").query("subject == 'Maths'")
    parts = {g: p for g, p in df.dropna(subset=["marks", "hours"]).groupby("class")}
    table = _maths(fast)
    result = table.compare_distributions_for("marks", for_each_group_in="class", show="wasserstein distance")
    assert _cell(result, "wasserstein distance") == pytest.approx(
        stats.wasserstein_distance(parts["A"]["marks"], parts["B"]["marks"]), rel=1e-12)
    assert result.count_rows() == 3
    result = table.compare_distributions_for("marks", for_each_group_in="class", show="energy distance")
    assert _cell(result, "energy distance", 3) == pytest.approx(
        stats.energy_distance(parts["B"]["marks"], parts["C"]["marks"]), rel=1e-12)
    result = table.compare_distributions_for(["marks", "hours"], for_each_group_in="class",
                                             show="wasserstein distance")
    assert _cell(result, "wasserstein distance") == pytest.approx(
        stats.wasserstein_distance_nd(parts["A"][["marks", "hours"]].to_numpy(),
                                      parts["B"][["marks", "hours"]].to_numpy()),
        rel=1e-9)


# ---------------------------------------------------------------- sdata.find_sensitivity_of
def test_find_sensitivity_of_matches_scipy_sobol_indices(capsys):
    def ishigami(x):
        return (np.sin(x[0]) + 7 * np.sin(x[1]) ** 2 + 0.1 * x[2] ** 4 * np.sin(x[0])).reshape(1, -1)

    ranges = {"x1": [-math.pi, math.pi], "x2": [-math.pi, math.pi], "x3": [-math.pi, math.pi]}
    result = sdata.find_sensitivity_of("sin(x1) + 7*sin(x2)**2 + 0.1*x3**4*sin(x1)", ranges=ranges, how_many=4096)
    found = stats.sobol_indices(func=ishigami, n=4096, dists=[stats.uniform(-math.pi, 2 * math.pi)] * 3,
                                rng=np.random.default_rng(1))
    assert result.get_column("first-order index").as_numpy() == pytest.approx(found.first_order.ravel(), abs=1e-12)
    assert result.get_column("total index").as_numpy() == pytest.approx(found.total_order.ravel(), abs=1e-12)
    # the Ishigami function's indices are known exactly (Saltelli et al. 2010): S1 = 0.314, 0.442, 0
    assert result.get_column("first-order index").as_numpy() == pytest.approx([0.3139, 0.4424, 0.0], abs=0.03)
    assert "x1 matters most" in capsys.readouterr().out


@pytest.mark.parametrize("ranges, says", [({"a": [0, 1]}, "needs a range for"), ({"a": [1, 0], "b": [0, 1]},
                                                                                   "lowest value, then a higher"),
                                          ({"a": [0, 1], "b": [0, 1], "c": [0, 1]}, "does not use")])
def test_find_sensitivity_of_says_what_is_wrong(ranges, says):
    with pytest.raises(SimplydataError, match=says):
        sdata.find_sensitivity_of("a + 2*b", ranges=ranges)


# ---------------------------------------------------------------- fit_distribution_to(censored_by=)
@pytest.mark.parametrize("fast", ENGINES)
@pytest.mark.parametrize("name, scipy_name, held", [("weibull", "weibull_min", {"floc": 0}),
                                                    ("lognormal", "lognorm", {"floc": 0}),
                                                    ("exponential", "expon", {"floc": 0}),
                                                    ("normal", "norm", {})])
def test_censored_fit_matches_scipy_fit_of_censored_data(name, scipy_name, held, fast, capsys):
    df = _frame("trial")
    table = sdata.table(df.assign(still_alive=df["died"] == "no"), fast=fast)
    fit = table.fit_distribution_to("days", name, censored_by="still_alive")
    data = stats.CensoredData(uncensored=df.loc[df["died"] == "yes", "days"].to_numpy(float),
                              right=df.loc[df["died"] == "no", "days"].to_numpy(float))
    dist = getattr(stats, scipy_name)
    found = dist.fit(data, **held, method="MLE")
    ll_ours = fit._fit_info["log-likelihood"]
    frozen = dist(*found)
    ll_scipy = float(np.sum(frozen.logpdf(data._uncensored)) + np.sum(frozen.logsf(data._right)))
    assert ll_ours >= ll_scipy - 1e-6  # the maximum: at least as high as SciPy's fit
    assert fit.find_percentile(50) == pytest.approx(frozen.median(), rel=1e-4)
    out = capsys.readouterr().out
    assert f"{int((df['died'] == 'no').sum())} of them censored" in out and 'where "still_alive" says so' in out


def test_censored_weibull_matches_survreg_numbers_on_the_trial_table(capsys):
    """R: survreg(Surv(days, died == "yes") ~ 1, dist = "weibull") on the trial table: shape 1 / scale, scale
    exp(intercept); the same maximum as SciPy's fit of CensoredData."""
    df = _frame("trial")
    table = sdata.table(df.assign(still_alive=df["died"] == "no"))
    fit = table.fit_distribution_to("days", "weibull", censored_by="still_alive")
    data = stats.CensoredData(uncensored=df.loc[df["died"] == "yes", "days"].to_numpy(float),
                              right=df.loc[df["died"] == "no", "days"].to_numpy(float))
    c, _, scale = stats.weibull_min.fit(data, floc=0)
    params = fit.show_parameters()
    assert params["shape"] == pytest.approx(c, rel=1e-4)
    assert params["scale"] == pytest.approx(scale, rel=1e-4)
    assert "fitdistrplus::fitdistcens" in capsys.readouterr().out


def test_censored_fit_needs_a_yes_no_column_and_one_group():
    table = _table("trial")
    with pytest.raises(SimplydataError, match="yes/no column"):
        table.fit_distribution_to("days", "weibull", censored_by="age")
    with pytest.raises(SimplydataError, match="fits one group"):
        table.fit_distribution_to("days", "weibull", censored_by="died", for_each_group_in="treatment")
    with pytest.raises(SimplydataError, match="not counts"):
        table.fit_distribution_to("days", "poisson", censored_by="died")


# ---------------------------------------------------------------- pointers: every 2.2 name of these batches
STATS_POINTERS = {
    "alexandergovern": "alexander-govern", "ansari": "ansari", "barnard_exact": "barnard", "bartlett": "bartlett",
    "bayes_mvs": 'test_method="bayesian"', "mvsdist": 'test_method="bayesian"',
    "binned_statistic": "in_bins_of=", "binned_statistic_2d": "in_bins_of=", "binned_statistic_dd": "in_bins_of=",
    "binomtest": "compare_percent_to", "boschloo_exact": "boschloo", "boxcox_llf": "log-likelihood",
    "boxcox_normmax": 'show="best by normal plot"', "boxcox_normplot": "normal plot correlation",
    "brunnermunzel": "brunner-munzel", "bws_test": "baumgartner-weiss-schindler", "chatterjeexi": "chatterjee xi",
    "chisquare": "compare_counts_to", "circstd": "circular standard deviation", "circvar": "circular variance",
    "combine_pvalues": "p_values=", "cramervonmises": "cramer-von-mises", "cramervonmises_2samp": "cramer-von mises",
    "cumfreq": "running count", "differential_entropy": "differential entropy",
    "directional_stats": "find_average_direction_of",
    "energy_distance": "energy distance", "entropy": "entropy", "epps_singleton_2samp": "epps-singleton",
    "estimated_cdf": "percentile rank", "expectile": "expectile", "fligner": "fligner", "gmean": "geometric mean",
    "goodness_of_fit": "compare_shape_to", "gstd": "geometric standard deviation", "gzscore": "add_z_score_column",
    "hmean": "harmonic mean", "iqr": "interquartile range", "kstat": "cumulant", "kstatvar": "cumulant variance",
    "kurtosistest": 'test_method="kurtosis"', "levene": "levene", "lmoment": "l-moment",
    "median_abs_deviation": "median absolute deviation", "median_test": '"median"', "moment": "central moment",
    "monte_carlo_test": "shuffling", "mood": "mood", "multiscale_graphcorr": "multiscale graph",
    "obrientransform": "o'brien", "percentileofscore": "percent at or below", "permutation_test": "shuffling",
    "pmean": "power mean", "pointbiserialr": "find_correlation_between", "poisson_means_test": "e-test",
    "power": "find_chance_of_finding", "power_divergence": "compare_counts_to", "ppcc_max": "tukey lambda",
    "ppcc_plot": "tukey lambda", "probplot": "draw_qq", "quantile_test": "find_median_of",
    "ranksums": "wilcoxon rank sum", "relfreq": "share of values", "scoreatpercentile": "percentile",
    "sigmaclip": "sigma-clipped average", "skewtest": 'test_method="skewness"', "sobol_indices":
        "find_sensitivity_of", "spearmanrho": "spearman", "tiecorrect": "mann-whitney", "tmax": "biggest up to",
    "tmean": "average between", "tmin": "smallest from", "trim1": "trimmed average", "trim_mean": "trimmed average",
    "trimboth": "trimmed average", "tsem": "standard error between", "tstd": "standard deviation between",
    "ttest_1samp": "compare_average_to", "tukey_hsd": "tukey", "tvar": "variance between", "variation":
        "coefficient of variation", "wasserstein_distance": "wasserstein distance",
    "wasserstein_distance_nd": "wasserstein distance", "weightedtau": "weighted kendall",
    "yeojohnson_llf": "log-likelihood", "yeojohnson_normmax": "yeo-johnson",
    "yeojohnson_normplot": "normal plot correlation", "zmap": "add_z_score_column",
    "CensoredData": "censored_by=", "BootstrapMethod": "bootstrap", "MonteCarloMethod": "shuffling",
    "PermutationMethod": "shuffling",
}


@pytest.mark.parametrize("name", sorted(STATS_POINTERS))
def test_every_scipy_stats_name_of_batches_3_4_points_to_its_word(name, capsys):
    sdata.help(f"scipy.stats.{name}")
    out = capsys.readouterr().out
    assert "name from other tools" in out.splitlines()[0], out
    assert STATS_POINTERS[name] in out, out
