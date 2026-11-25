"""S3c-4, small additions to known words: weighted percentiles and medians, the covariance table, the automatic ARIMA
order, Storey's q-values and the local false discovery rate, Nemenyi's and Conover's tests after Friedman's, and
pairwise comparisons of percents.

The numbers are checked against the packages underneath (NumPy, pandas, SciPy and statsmodels here; R in the tests
marked needs_r, and in the reliability study on published data).
"""

import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

import simplydata as sdata
from conftest import r_table
from simplydata import SimplydataError
from conftest import example_frame

DATA = Path(__file__).resolve().parents[1] / "validation" / "data"
WEIGHTED = pd.DataFrame({"length": [1.2, 2.1, 3.1, 5.0, 9.4, 2.2, 7.7], "n": [1, 3, 2, 1, 2, 1, 1],
                         "w": [0.5, 1.2, 3.0, 1.0, 2.0, 1.0, 1.0], "site": list("aabbaab")})


def _r(code, packages=()):
    from simplydata._r import r_call

    return r_call(code, packages=packages)


def _rounding():
    wide = pd.read_csv(DATA / "rounding_first_base.csv")
    return wide.melt(id_vars="player", value_vars=["round_out", "narrow_angle", "wide_angle"], var_name="method",
                     value_name="time")


def _smokers():
    rows = []
    for group, s, n in ((1, 83, 86), (2, 90, 93), (3, 129, 136), (4, 70, 82)):
        rows += [{"group": str(group), "smoker": "yes"}] * s + [{"group": str(group), "smoker": "no"}] * (n - s)
    return sdata.table(pd.DataFrame(rows))


# ---------------------------------------------------------------- A14: weighted percentiles
def test_frequency_weights_repeat_the_rows(capsys):
    t = sdata.table(WEIGHTED)
    rows = np.repeat(WEIGHTED["length"], WEIGHTED["n"])
    for percent in (10, 50, 90):
        assert t.find_percentile_of("length", percent, weights="n") == pytest.approx(np.percentile(rows, percent))
    assert t.find_median_of("length", weights="n") == pytest.approx(np.median(rows))
    out = capsys.readouterr().out
    assert "frequency weights" in out and "quantile(rep(x, w)" in out


def test_the_design_values_of_frequency_weights():
    t = sdata.table(WEIGHTED)  # R quantile(rep(x, w)) and Hmisc::wtd.quantile(x, w) give 2.1, 3.1 and 9.4
    got = [t.find_percentile_of("length", p, weights="n") for p in (10, 50, 90)]
    assert got == pytest.approx([2.1, 3.1, 9.4])


def test_weights_of_one_change_nothing():
    frame = pd.DataFrame({"x": [1.0, 2, 3, 4, 10], "one": 1})
    t = sdata.table(frame)
    for percent in (5, 30, 50, 77):
        assert t.find_percentile_of("x", percent, weights="one") == pytest.approx(np.percentile(frame["x"], percent))


def test_frequency_weights_keep_method():
    t = sdata.table(WEIGHTED)
    rows = np.repeat(WEIGHTED["length"], WEIGHTED["n"])
    assert t.find_percentile_of("length", 30, weights="n", test_method=6) == pytest.approx(
        np.percentile(rows, 30, method="weibull"))


NUMPY_2 = pytest.mark.skipif(np.lib.NumpyVersion(np.__version__) < "2.0.0", reason="percentile(weights=) needs NumPy 2")


@NUMPY_2
def test_analytic_weights_are_numpys_weighted_inverted_cdf(capsys):
    t = sdata.table(WEIGHTED)
    for percent in (10, 50, 90):
        got = t.find_percentile_of("length", percent, weights="w", weight_kind="analytic")
        assert got == pytest.approx(np.percentile(WEIGHTED["length"], percent, weights=WEIGHTED["w"],
                                                  method="inverted_cdf"))
    assert t.find_median_of("length", weights="w", weight_kind="analytic") == pytest.approx(
        np.percentile(WEIGHTED["length"], 50, weights=WEIGHTED["w"], method="inverted_cdf"))
    assert "svyquantile" in capsys.readouterr().out


def test_weighted_percentile_for_each_group():
    result = sdata.table(WEIGHTED).find_percentile_of("length", 90, weights="n", for_each_group_in="site").as_pandas()
    for site, rows in WEIGHTED.groupby("site"):
        expected = np.percentile(np.repeat(rows["length"], rows["n"]), 90)
        assert result.loc[result["site"] == site, "weighted percentile 90 of length"].item() == pytest.approx(expected)


def test_weighted_percentile_skips_empty_cells(capsys):
    frame = WEIGHTED.copy()
    frame.loc[0, "n"] = np.nan
    got = sdata.table(frame).find_percentile_of("length", 50, weights="n")
    kept = frame.dropna()
    assert got == pytest.approx(np.percentile(np.repeat(kept["length"], kept["n"].astype(int)), 50))
    assert "1 row with an empty cell" in capsys.readouterr().out


@pytest.mark.parametrize("options, words", [
    (dict(weights="w"), "whole numbers"),
    (dict(weights="n", weight_kind="analytic", test_method=8), "test_method= cannot be changed"),
    (dict(weight_kind="analytic"), "goes with weights="),
    (dict(weights="n", interval=95), "do not go together"),
    (dict(weights="length"), "column other than"),
    (dict(weights="n", weight_kind="precision"), "weight_kind"),
])
def test_weighted_percentile_refusals(options, words):
    with pytest.raises(SimplydataError, match=words):
        sdata.table(WEIGHTED).find_percentile_of("length", 90, **options)


def test_negative_weights_are_refused():
    frame = WEIGHTED.assign(n=[1, -1, 1, 1, 1, 1, 1])
    with pytest.raises(SimplydataError, match="below 0"):
        sdata.table(frame).find_median_of("length", weights="n")


# ---------------------------------------------------------------- A25: covariance matrix
def test_covariance_table_is_pandas_cov(capsys):
    frame = example_frame("marks")
    result = sdata.table(frame).find_correlation_between("hours", "marks", "height", show="covariance").as_pandas()
    expected = frame[["hours", "marks", "height"]].cov()
    assert list(result.columns) == ["column", "hours", "marks", "height"]
    assert np.allclose(result[["hours", "marks", "height"]].to_numpy(), expected.to_numpy(), rtol=1e-12)
    out = capsys.readouterr().out
    assert "units of the two columns multiplied" in out and "pairwise.complete.obs" in out


def test_covariance_uses_the_rows_each_pair_has():
    frame = r_table("mtcars.csv")
    frame.loc[3, "wt"] = np.nan
    result = sdata.table(frame).find_correlation_between("mpg", "wt", show="covariance").as_pandas()
    assert result["wt"][0] == pytest.approx(frame[["mpg", "wt"]].dropna().cov().loc["mpg", "wt"], rel=1e-12)
    assert result["mpg"][0] == pytest.approx(frame["mpg"].var(), rel=1e-12)  # the whole column for its variance


@pytest.mark.parametrize("options", [dict(test_method="spearman"), dict(sides=1, higher="positive"),
                                     dict(p_value_by="shuffling"), dict(allowing_for="height")])
def test_covariance_refuses_test_options(options):
    with pytest.raises(SimplydataError, match="covariance"):
        sdata.table(sdata.get_example("marks")).find_correlation_between("hours", "marks", show="covariance",
                                                                         **options)


# ---------------------------------------------------------------- AA11: automatic ARIMA order
def _passengers():
    table = sdata.table(r_table("air_passengers.csv"))
    table.turn_into_dates("month")
    return table


def test_automatic_order_refuses_a_seasonal_order_before_r():
    with pytest.raises(SimplydataError, match="leave out seasonal_order="):
        _passengers().forecast("passengers", sorted_by="month", test_method="arima", order="automatic",
                               seasonal_order=(0, 1, 1), repeats_every=12)


def test_order_text_other_than_automatic_is_refused():
    with pytest.raises(SimplydataError, match='order="automatic"'):
        _passengers().forecast("passengers", sorted_by="month", test_method="arima", order="best", repeats_every=12)


def test_automatic_order_is_auto_arima_with_the_full_search(needs_r, capsys):
    result = _passengers().forecast("passengers", sorted_by="month", test_method="arima", order="auto",
                                    repeats_every=12).as_pandas()
    found = _r('x <- stats::ts(as.numeric(datasets::AirPassengers), frequency = 12); '
               "fit <- forecast::auto.arima(x, stepwise = FALSE, approximation = FALSE); "
               "f <- forecast::forecast(fit, h = 12, level = 95); "
               "list(mean = as.numeric(f$mean), low = as.numeric(f$lower), arma = fit$arma)", ("forecast",))
    assert np.allclose(result["forecast"], found["mean"], rtol=1e-9)
    assert np.allclose(result["forecast 95 % prediction low"], found["low"], rtol=1e-9)
    p, q, sp, sq, m, d, sd = (int(v) for v in np.asarray(found["arma"], dtype=float))
    label = f"ARIMA({p},{d},{q})({sp},{sd},{sq})[{m}]"  # the order R itself chose (it can change with versions)
    assert result["method"][0].startswith(label)
    out = capsys.readouterr().out
    assert f"auto.arima chose {label}" in out and "a little too narrow" in out
    assert "stepwise = FALSE, approximation = FALSE" in out and 'table.add_column("log passengers"' in out


def test_automatic_order_on_the_log_gives_the_airline_model(needs_r):
    frame = r_table("air_passengers.csv")
    table = sdata.table(frame.assign(log_passengers=np.log(frame["passengers"])))
    model = table.forecast("log_passengers", test_method="arima", order="automatic", repeats_every=12,
                           show="model").as_pandas()
    from simplydata._r import r_call

    found = r_call("fit <- forecast::auto.arima(stats::ts(log(x), frequency = 12), stepwise = FALSE, "
                   "approximation = FALSE); list(terms = names(fit$coef), coef = unname(fit$coef))",
                   packages=("forecast",), x=frame["passengers"].to_numpy(dtype=float))
    terms = [str(t) for t in np.atleast_1d(found["terms"])]
    assert list(model["term"][:len(terms)]) == terms
    assert model["estimate"][:len(terms)].tolist() == pytest.approx(np.atleast_1d(found["coef"]).tolist(), rel=1e-9)


def test_compare_forecasts_with_an_automatic_order(needs_r, capsys):
    result = _passengers().compare_forecasts_for("passengers", sorted_by="month", test_method=["arima", "average"],
                                                 order="automatic", repeats_every=12).as_pandas()
    assert any("chosen by auto.arima" in m for m in result["method"])
    assert "on the readings before the last 12" in capsys.readouterr().out


# ---------------------------------------------------------------- G03: q-values and local FDR
def test_the_install_line_names_bioconductor_for_qvalue():
    from simplydata._r import _install_text

    text = _install_text(("qvalue", "vegan"), "Storey's q-values")
    assert 'install.packages(c("vegan"))' in text
    assert "Bioconductor" in text and "BiocManager" in text and "bioconductor-qvalue" in text
    assert 'install.packages(c("qvalue"))' not in text


def test_storey_q_values_are_qvalues(needs_r, capsys):
    frame = example_frame("many_tests")
    result = sdata.table(frame).add_adjusted_p_value_column(test_method="q-values").as_pandas()
    from simplydata._r import r_call

    found = r_call("q <- qvalue::qvalue(p); list(q = q$qvalues, pi0 = q$pi0)", packages=("qvalue",),
                   p=frame["p-value"].to_numpy(dtype=float))
    assert np.allclose(result["p-value (Storey q-value)"], found["q"], rtol=1e-12)
    out = capsys.readouterr().out
    assert f"pi0 = {float(np.asarray(found['pi0']).ravel()[0]):.3f}" in out
    assert "Benjamini-Hochberg" in out and "pi0 = 1" in out


def test_local_fdr_has_its_own_column_name(needs_r, capsys):
    frame = example_frame("many_tests")
    result = sdata.table(frame).add_adjusted_p_value_column(test_method="lfdr").as_pandas()
    from simplydata._r import r_call

    found = r_call("qvalue::qvalue(p)$lfdr", packages=("qvalue",), p=frame["p-value"].to_numpy(dtype=float))
    assert np.allclose(result["local false discovery rate"], found, rtol=1e-12)
    assert "not an adjusted p-value" in capsys.readouterr().out


def test_few_p_values_get_a_note(needs_r, capsys):
    rng = np.random.default_rng(1)
    p = np.r_[rng.uniform(0, 0.01, 10), rng.uniform(0, 1, 40)]
    sdata.table(pd.DataFrame({"p": p})).add_adjusted_p_value_column(from_column="p", test_method="storey")
    assert "fewer than 100 p-values" in capsys.readouterr().out


def test_qvalue_failure_is_a_friendly_refusal(needs_r):
    with pytest.raises(SimplydataError, match='could not estimate.*test_method="benjamini-hochberg"'):
        sdata.table(pd.DataFrame({"p": [0.001, 0.01, 0.02, 0.03]})).add_adjusted_p_value_column(from_column="p",
                                                                                                test_method="storey")


def test_unknown_adjust_method_lists_storey():
    with pytest.raises(SimplydataError, match="storey"):
        sdata.table(pd.DataFrame({"p": [0.01, 0.2]})).add_adjusted_p_value_column(from_column="p", test_method="qq")


# ---------------------------------------------------------------- G09: Nemenyi and Conover after Friedman
def test_nemenyi_matches_pmcmrplus(needs_r, capsys):
    result = sdata.table(_rounding()).compare_each_pair_of("time", for_each_group_in="method", matched_by="player",
                                                           test_method="nemenyi").as_pandas()
    assert result["p-value (adjusted)"].tolist() == pytest.approx([0.63742717, 0.06137076, 0.00440982], abs=1e-8)
    assert set(result["statistic name"]) == {"q"} and "degrees of freedom" not in result.columns
    out = capsys.readouterr().out
    assert "no further adjustment" in out and "Benavoli" in out
    assert "narrow_angle ranks lower than round_out" in out or "narrow_angle ranks higher than round_out" in out
    assert 'the two groups had the same typical "time" (in ranks)' in out


def test_conover_after_friedman_is_holm_adjusted(needs_r, capsys):
    result = sdata.table(_rounding()).compare_each_pair_of("time", for_each_group_in="method", matched_by="player",
                                                           based_on="ranks", test_method="conover").as_pandas()
    assert result["p-value (adjusted)"].tolist() == pytest.approx([0.30120902, 0.02456571, 0.00207436], abs=1e-8)
    out = capsys.readouterr().out
    assert "Holm" in out and "single-step" in out
    assert set(result["statistic name"]) == {"t"} and (result["degrees of freedom"] == 42).all()  # 22 * 3 - 3 - 22 + 1


def test_friedman_pair_tests_need_three_groups():
    frame = _rounding()
    frame = frame[frame["method"] != "wide_angle"]
    with pytest.raises(SimplydataError, match="3 or more groups"):
        sdata.table(frame).compare_each_pair_of("time", for_each_group_in="method", matched_by="player",
                                                test_method="nemenyi")


def test_other_tests_are_refused_with_matched_by():
    with pytest.raises(SimplydataError, match='test_method="nemenyi" or test_method="conover"'):
        sdata.table(_rounding()).compare_each_pair_of("time", for_each_group_in="method", matched_by="player",
                                                      test_method="tukey")


# ---------------------------------------------------------------- D13: pairwise comparisons of percents
def test_pairs_of_percents_match_pairwise_prop_test(capsys):
    result = _smokers().compare_each_pair_of("smoker", for_each_group_in="group", based_on="percents",
                                              value="yes").as_pandas()
    # R pairwise.prop.test(c(83, 90, 129, 70), c(86, 93, 136, 82)): Yates' correction and Holm, as simplydata
    assert result["p-value (Holm)"].tolist() == pytest.approx([1, 1, 0.1185648, 1, 0.0932173, 0.1237680], abs=1e-6)
    tab = np.array([[83, 3], [70, 12]])
    assert result["p-value"][2] == pytest.approx(stats.chi2_contingency(tab, correction=True).pvalue, rel=1e-12)
    out = capsys.readouterr().out
    assert "Yates" in out and "pairwise.prop.test" in out and "Newcombe" in out
    assert 'the two groups had the same percent "yes"' in out and "expected count is below 5" in out


def test_pairs_of_percents_give_the_difference_with_newcombes_interval():
    from statsmodels.stats.proportion import confint_proportions_2indep

    result = _smokers().compare_each_pair_of("smoker", for_each_group_in="group", based_on="percents",
                                              value="yes").as_pandas()
    low, high = confint_proportions_2indep(83, 86, 70, 82, method="newcomb", compare="diff")
    row = result.iloc[2]
    assert row["difference"] == pytest.approx(83 / 86 - 70 / 82, rel=1e-12)
    assert (row["difference 95 % CI low"], row["difference 95 % CI high"]) == pytest.approx((low, high), rel=1e-12)
    assert row["share yes in group 1"] == pytest.approx(83 / 86) and row["count in group 2"] == 82


def test_pairs_of_percents_with_fisher():
    result = _smokers().compare_each_pair_of("smoker", for_each_group_in="group", based_on="percents",
                                              test_method="fisher").as_pandas()
    raw = [stats.fisher_exact(np.array([[a, n - a], [b, m - b]])).pvalue
           for (a, n), (b, m) in [((83, 86), (90, 93)), ((83, 86), (129, 136)), ((83, 86), (70, 82)),
                                  ((90, 93), (129, 136)), ((90, 93), (70, 82)), ((129, 136), (70, 82))]]
    assert result["p-value"].tolist() == pytest.approx(raw, rel=1e-12)
    assert result["p-value (Holm)"][2] == pytest.approx(0.07496816, abs=1e-7)  # R rstatix::pairwise_fisher_test


def test_a_pair_with_one_value_has_no_p_value(capsys):
    frame = pd.DataFrame({"g": ["a"] * 5 + ["b"] * 5 + ["c"] * 6,
                          "y": ["yes"] * 5 + ["yes"] * 5 + ["no", "yes", "no", "no", "no", "no"]})
    result = sdata.table(frame).compare_each_pair_of("y", for_each_group_in="g", based_on="percents",
                                                     value="yes").as_pandas()
    assert math.isnan(result["p-value"][0]) and math.isnan(result["p-value (Holm)"][0])
    assert not math.isnan(result["p-value (Holm)"][1])
    assert "no p-value" in capsys.readouterr().out


@pytest.mark.parametrize("options, words", [
    (dict(value="yes"), "goes with based_on"),
    (dict(based_on="percents", show="letters"), "leave out"),
    (dict(based_on="percents", test_method="tukey"), "test"),
])
def test_percent_pair_refusals(options, words):
    with pytest.raises(SimplydataError, match=words):
        _smokers().compare_each_pair_of("smoker", for_each_group_in="group", **options)


@NUMPY_2
def test_infinite_weights_are_refused():
    frame = WEIGHTED.assign(n=[1, np.inf, 1, 1, 1, 1, 1])
    for kind in ("frequency", "analytic"):
        with pytest.raises(SimplydataError, match="infinite"):
            sdata.table(frame).find_percentile_of("length", 50, weights="n", weight_kind=kind)


@NUMPY_2
def test_method_linear_is_refused_with_analytic_weights_too():
    with pytest.raises(SimplydataError, match="test_method= cannot be changed"):
        sdata.table(WEIGHTED).find_percentile_of("length", 90, weights="w", weight_kind="analytic", test_method="linear")


def test_seasonal_order_automatic_points_to_order():
    with pytest.raises(SimplydataError, match="chooses the seasonal order too"):
        _passengers().forecast("passengers", sorted_by="month", test_method="arima", order=(0, 1, 1),
                               seasonal_order="automatic", repeats_every=12)


def test_chart_forecast_takes_the_automatic_order(needs_r):
    chart = sdata.chart(r_table("air_passengers.csv", parse_dates=["month"]))
    chart.draw_forecast(x="month", y="passengers", test_method="arima", order="automatic", repeats_every=12)
    import matplotlib.pyplot as plt

    plt.close("all")


def test_the_log_note_needs_positive_values(needs_r, capsys):
    frame = r_table("air_passengers.csv")
    frame["change"] = frame["passengers"].diff().fillna(0)
    table = sdata.table(frame)
    table.turn_into_dates("month")
    table.forecast("change", sorted_by="month", test_method="arima", order="automatic", repeats_every=12)
    assert "log of the column" not in capsys.readouterr().out
