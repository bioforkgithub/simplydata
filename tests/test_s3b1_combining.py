"""Combining studies (phase S3b-1): table.combine_studies, forest_plot's diamonds and size=, draw_funnel_plot.

The numbers come from R metafor; the tests that need R ask for needs_r (skipped without R, except in CI). The
checks of the input (one way in, columns, values) run without R: they stop before R is called.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata._errors import SimplydataError

CALL = dict(names="trial", events=["tb_vaccinated", "tb_unvaccinated"], out_of=["vaccinated", "unvaccinated"])


@pytest.fixture
def bcg():
    return sdata.table(sdata.get_example("bcg"))


def _row(result, kind):
    frame = result.as_pandas()
    return frame[frame["row kind"] == kind].iloc[0]


# ---------------------------------------------------------------- the numbers (Viechtbauer 2010, JSS 36(3))
def test_bcg_risk_ratios_reml_hartung_knapp(bcg, needs_r, capsys):
    result = bcg.combine_studies(**CALL)
    out = capsys.readouterr().out
    row = _row(result, "combined")
    assert row["estimate"] == pytest.approx(np.exp(-0.7145323), rel=1e-6)
    assert row["tau squared"] == pytest.approx(0.3132433, rel=1e-5)
    assert row["I squared %"] == pytest.approx(92.22139, rel=1e-5)
    assert row["Q"] == pytest.approx(152.233, rel=1e-5)
    assert row["estimate 95 % CI low"] == pytest.approx(0.3300722, rel=1e-5)
    pi = _row(result, "prediction interval")
    assert pi["estimate 95 % CI low"] == pytest.approx(0.1359, abs=1e-4)
    assert pi["estimate 95 % CI high"] == pytest.approx(1.7629, abs=1e-4)
    assert "sets of studies like these" in out and "studies like this one" not in out
    assert "In a new setting like these studies, the true risk ratio would lie between 0.136 and 1.76" in out
    assert "t with 12 degrees of freedom" in out
    assert "by a factor of about 1.75 up or down" in out
    assert "it says how much of the spread is real, not how big it is" in out
    assert "Peters' test" in out and "not proof of publication bias" in out
    assert "Trim and fill (a what-if, not a correction): 1 study might be missing on the right" in out
    assert "rough guess" in out  # I-squared above 50 %
    assert "Hartung-Knapp (for the interval and the p-value)" in out
    assert "significant" not in out
    weights = result.as_pandas().query("`row kind` == 'study'")["weight %"]
    assert weights.sum() == pytest.approx(100)


def test_normal_interval_matches_the_published_one(bcg, needs_r):
    row = _row(bcg.combine_studies(**CALL, interval_by="normal"), "combined")
    # Viechtbauer (2010): -0.7145 (95 % CI -1.0669 to -0.3622) on the log scale
    assert np.log(row["estimate 95 % CI low"]) == pytest.approx(-1.0669, abs=1e-4)
    assert np.log(row["estimate 95 % CI high"]) == pytest.approx(-0.3622, abs=1e-4)


def test_methods(bcg, needs_r, capsys):
    dl = _row(bcg.combine_studies(**CALL, method="DL"), "combined")
    assert dl["tau squared"] == pytest.approx(0.3088, abs=1e-4)
    mh = _row(bcg.combine_studies(**CALL, method="Mantel-Haenszel"), "combined")
    assert mh["estimate"] == pytest.approx(0.6353, abs=1e-4)
    out = capsys.readouterr().out
    assert "common effect, Mantel-Haenszel" in out and "no prediction interval" in out
    peto = _row(bcg.combine_studies(**CALL, method="peto"), "combined")
    assert peto["estimate"] == pytest.approx(0.6222, abs=1e-4)
    assert "odds ratio" in capsys.readouterr().out


def test_subgroups_print_the_difference_test_first(bcg, needs_r, capsys):
    result = bcg.combine_studies(**CALL, for_each_group_in="allocation")
    out = capsys.readouterr().out
    assert out.index("Test of subgroup difference") < out.index('"random": combined')
    assert "Sun et al. 2010" in out and "guessed from almost nothing" in out
    row = _row(result, "subgroup difference")
    assert row["Q degrees of freedom"] == 2
    assert set(result.as_pandas().query("`row kind` == 'combined in subgroup'")["subgroup"]) == {
        "alternate", "random", "systematic"}


def test_meta_regression(bcg, needs_r, capsys):
    result = bcg.combine_studies(**CALL, using=["latitude"])
    out = capsys.readouterr().out
    slope = result.as_pandas().query("`row kind` == 'meta-regression' and study != 'intercept'").iloc[0]
    assert slope["estimate"] == pytest.approx(-0.02910166, rel=1e-5)
    assert "accounts for 76 % of the between-study spread" in out
    assert "ecological" in out


def test_estimates_with_their_intervals(needs_r, capsys):
    table = sdata.table(sdata.get_example("passive_smoking"))
    row = _row(table.combine_studies(names="study", estimates="odds ratio", method="DL", interval_by="normal"),
               "combined")
    # Hackshaw, Law & Wald (1997): excess risk 24 % (95 % CI 13 % to 36 %)
    assert round(row["estimate"], 2) == 1.24
    assert round(row["estimate 95 % CI low"], 2) == 1.13 and round(row["estimate 95 % CI high"], 2) == 1.36
    out = capsys.readouterr().out
    assert "combined on the log scale" in out and "Egger's regression test" in out


def test_standard_errors_route_gives_the_same_as_metafor(needs_r):
    frame = pd.DataFrame({"study": list("abcdef"), "log odds": [0.1, 0.3, -0.2, 0.5, 0.2, 0.0],
                          "se": [0.2, 0.3, 0.25, 0.4, 0.15, 0.3]})
    row = _row(sdata.table(frame).combine_studies(names="study", estimates="log odds", standard_errors="se"),
               "combined")
    from simplydata._r import need_r, r_call

    need_r(("metafor",), "the check")  # checked, never attached
    theirs = r_call("f <- metafor::rma(y, sei = s, test = 'adhoc'); c(f$b[1], f$ci.lb)",
                    y=frame["log odds"].to_numpy(), s=frame["se"].to_numpy())
    assert row["estimate"] == pytest.approx(theirs[0]) and row["estimate 95 % CI low"] == pytest.approx(theirs[1])


def test_averages_and_correlations(needs_r):
    frame = pd.DataFrame({"study": ["a", "b", "c"], "m1": [10, 12, 9], "m2": [9, 10, 9.5], "s1": [2, 3, 2],
                          "s2": [2, 2.5, 2], "n1": [8, 20, 15], "n2": [7, 22, 15], "r": [0.3, 0.5, 0.1],
                          "n": [50, 60, 40]})
    table = sdata.table(frame)
    g = table.combine_studies(names="study", averages=["m1", "m2"], standard_deviations=["s1", "s2"],
                              counts=["n1", "n2"]).as_pandas()
    assert g["estimate"].iloc[0] == pytest.approx(0.47049, abs=1e-5)  # metafor's Hedges' g (not statsmodels')
    r = _row(table.combine_studies(names="study", correlations="r", counts="n"), "combined")
    assert r["estimate"] == pytest.approx(0.3217, abs=1e-4)


def test_peters_test_matches_r_meta(bcg, needs_r):
    r = bcg.combine_studies(**CALL).as_pandas()
    row = r[r["row kind"] == "small-study effects"].iloc[0]
    assert row["estimate"] == pytest.approx(-1.2701894, rel=1e-6)  # meta::metabias(method.bias = "Peters")
    assert row["p-value"] == pytest.approx(0.2302269, rel=1e-6)


def test_mantel_haenszel_with_a_double_zero_study(needs_r, capsys):
    frame = pd.DataFrame({"trial": list("abcde"), "e1": [0, 3, 0, 5, 2], "n1": [20, 30, 25, 40, 30],
                          "e2": [2, 6, 0, 9, 4], "n2": [20, 30, 25, 40, 30]})
    r = sdata.table(frame).combine_studies(names="trial", events=["e1", "e2"], out_of=["n1", "n2"],
                                           method="Mantel-Haenszel")
    out = capsys.readouterr().out
    row = _row(r, "combined")
    assert row["studies"] == 4 and row["Q degrees of freedom"] == 3
    assert "Combining 4 studies" in out and "; 4 studies)" in out


def test_subgroups_with_one_study_and_an_empty_group(needs_r, capsys):
    frame = pd.DataFrame({"trial": list("abcdefg"), "e1": [3, 5, 2, 4, 6, 0, 7], "n1": [30] * 7,
                          "e2": [6, 9, 4, 8, 9, 0, 9], "n2": [30] * 7,
                          "place": ["x", "x", "x", "y", "y", "z", "w"]})
    r = sdata.table(frame).combine_studies(names="trial", events=["e1", "e2"], out_of=["n1", "n2"],
                                           for_each_group_in="place").as_pandas()
    out = capsys.readouterr().out
    assert '"z" of "place" has no study with an event' in out
    assert "One study: it is its own result" in out and "With 1 studies" not in out
    assert set(r.query("`row kind` == 'combined in subgroup'")["subgroup"]) == {"x", "y", "w"}


def test_ratio_names_are_whole_words(needs_r, capsys):
    frame = pd.DataFrame({"study": list("abcde"), "OR": [1.2, 1.5, 0.9, 1.3, 1.1], "se": [0.2, 0.3, 0.25, 0.2, 0.3],
                          "duration": [2.0, 3.0, 2.5, 4.0, 3.5]})
    table = sdata.table(frame)
    ratio = table.combine_studies(names="study", estimates="OR", standard_errors="se")
    assert "combined on the log scale" in capsys.readouterr().out
    plain = table.combine_studies(names="study", estimates="duration", standard_errors="se")
    assert "combined on the log scale" not in capsys.readouterr().out
    assert _row(plain, "combined")["combined on"] == "plain scale"
    ax = ratio.start_chart().forest_plot(x="estimate", y="study")._render().axes[0]
    assert ax.get_xscale() == "log"
    ax = plain.start_chart().forest_plot(x="estimate", y="study")._render().axes[0]
    assert ax.get_xscale() == "linear"
    plt.close("all")


def test_meta_regression_with_two_columns(bcg, needs_r):
    r = bcg.combine_studies(**CALL, using=["latitude", "year"]).as_pandas()
    assert len(r.query("`row kind` == 'meta-regression'")) == 3


def test_polars_tables_work_too(needs_r):
    import polars as pl

    frame = pl.from_pandas(sdata.get_example("bcg"))
    row = _row(sdata.table(frame).combine_studies(**CALL), "combined")
    assert row["estimate"] == pytest.approx(np.exp(-0.7145323), rel=1e-6)


def test_two_studies_have_no_prediction_interval(needs_r, capsys):
    frame = sdata.get_example("bcg").head(2)
    sdata.table(frame).combine_studies(**CALL)
    out = capsys.readouterr().out
    assert "no prediction interval (it needs 3)" in out and "honest, not an error" in out


def test_double_zero_study_is_left_out_and_said(needs_r, capsys):
    frame = pd.DataFrame({"trial": list("abcd"), "e1": [0, 3, 0, 5], "n1": [20, 30, 25, 40], "e2": [2, 6, 0, 9],
                          "n2": [20, 30, 25, 40]})
    result = sdata.table(frame).combine_studies(names="trial", events=["e1", "e2"], out_of=["n1", "n2"])
    out = capsys.readouterr().out
    assert 'no events in either group ("c")' in out and "added 1/2" in out
    assert np.isnan(result.as_pandas().query("study == 'c'")["estimate"].iloc[0])


# ---------------------------------------------------------------- checks before R
@pytest.mark.parametrize("options, words", [
    (dict(events=["tb_vaccinated", "tb_unvaccinated"], averages=["a", "b"]), "one way in at a time"),
    (dict(events=["tb_vaccinated", "tb_unvaccinated"]), "needs out_of="),
    (dict(events="tb_vaccinated", out_of=["vaccinated", "unvaccinated"]), "list of two column names"),
    (dict(**CALL, show="ratios of averages"), "worked out from averages="),
    (dict(**CALL, show="risk ratios", method="Peto"), "odds ratios only"),
    (dict(**CALL, method="common effect", interval_by="Hartung-Knapp"), "is for random effects"),
    (dict(**CALL, method="banana"), "does not know method="),
    (dict(**CALL, for_each_group_in="allocation", using=["latitude"]), "not both"),
    (dict(**CALL, using=["allocation"]), "For a text column, use for_each_group_in="),
    (dict(**CALL, method="Peto", using=["latitude"]), "needs the default"),
    (dict(names="trial", estimates="latitude"), "Two ways in"),
    (dict(**CALL, estimates_are_ratios=True), "goes with estimates="),
])
def test_wrong_calls_are_explained(bcg, options, words):
    with pytest.raises(SimplydataError, match=words.replace("(", r"\(").replace("=", "=")):
        bcg.combine_studies(**options)


def test_show_does_not_go_with_estimates():
    with pytest.raises(SimplydataError, match="Leave out show="):
        sdata.table(sdata.get_example("passive_smoking")).combine_studies(names="study", estimates="odds ratio",
                                                                          show="odds ratios")


def test_more_events_than_people_is_refused():
    frame = pd.DataFrame({"t": ["a", "b"], "e1": [5, 3], "n1": [4, 30], "e2": [2, 6], "n2": [20, 30]})
    with pytest.raises(SimplydataError, match="cannot be more events than people"):
        sdata.table(frame).combine_studies(names="t", events=["e1", "e2"], out_of=["n1", "n2"])


def test_one_study_is_refused():
    with pytest.raises(SimplydataError, match="at least 2 studies"):
        sdata.table(sdata.get_example("bcg").head(1)).combine_studies(**CALL)


def test_spellings_of_methods_and_shows():
    from simplydata.table.meta_words import (INTERVAL_SPELLINGS, INTERVALS, METHOD_SPELLINGS, METHODS, SHOW,
                                             SHOW_SPELLINGS, _text_choice)

    assert _text_choice("random effects", METHOD_SPELLINGS, tuple(METHODS), "method") == "REML"
    assert _text_choice("fixed effect", METHOD_SPELLINGS, tuple(METHODS), "method") == "common effect"
    assert _text_choice("reml", METHOD_SPELLINGS, tuple(METHODS), "method") == "REML"
    assert _text_choice("MH", METHOD_SPELLINGS, tuple(METHODS), "method") == "Mantel-Haenszel"
    assert _text_choice("hksj", INTERVAL_SPELLINGS, tuple(INTERVALS), "interval_by") == "Hartung-Knapp"
    assert _text_choice("hedges g", SHOW_SPELLINGS, tuple(SHOW), "show") == "standardised differences"
    assert _text_choice("response ratios", SHOW_SPELLINGS, tuple(SHOW), "show") == "ratios of averages"


# ---------------------------------------------------------------- charts
def test_forest_plot_draws_squares_diamonds_and_the_prediction_interval(bcg, needs_r, tmp_path):
    result = bcg.combine_studies(**CALL)
    chart = result.start_chart().forest_plot(x="estimate", y="study", size="weight %")
    ax = chart._render().axes[0]
    assert ax.get_xscale() == "log"
    sizes = ax.collections[-1].get_sizes() if len(ax.collections) else []
    assert len(ax.patches) == 1  # one diamond
    labels = [t.get_text() for t in ax.get_yticklabels()]
    assert labels[-1] == "prediction interval" and "combined" in labels
    chart.save(str(tmp_path / "forest.png"))
    plt.close("all")
    assert sizes is not None


def test_forest_plot_without_row_kind_is_unchanged(tmp_path):
    table = sdata.table(sdata.get_example("marks"))
    pairs = table.compare_each_pair_of("marks", for_each_group_in="class", test="tukey")
    ax = pairs.start_chart().forest_plot(x="difference", y="group 1")._render().axes[0]
    assert not ax.patches
    plt.close("all")


def test_funnel_plot(bcg, needs_r, capsys):
    result = bcg.combine_studies(**CALL)
    ax = result.start_chart().draw_funnel_plot(x="estimate", y="standard error")._render().axes[0]
    assert ax.get_xscale() == "log"
    assert len(ax.collections[0].get_offsets()) == 13
    low, high = ax.get_ylim()
    assert low > high == 0  # 0 at the top
    assert "not proof of publication bias" in capsys.readouterr().out
    plt.close("all")


def test_funnel_plot_needs_a_combined_result():
    with pytest.raises(SimplydataError, match="draws the result of table.combine_studies"):
        sdata.chart(sdata.get_example("bcg")).draw_funnel_plot(x="latitude", y="year")


def test_other_names_point_to_the_new_words():
    from simplydata._errors import MissingWordError
    from simplydata.table import Table

    with pytest.raises(MissingWordError, match="combine_studies"):
        Table(sdata.get_example("bcg")).hksj
    with pytest.raises(MissingWordError, match="draw_funnel_plot"):
        sdata.chart(sdata.get_example("bcg")).funnel_plot


def test_group_heading_is_join_and_reshape():
    from simplydata import learn

    names = [g for g, _ in learn.GROUPS]
    assert "Join and reshape" in names and "Combine and reshape" not in names and "Combining studies" in names


# ---------------------------------------------------------------- the same underneath
def test_the_new_words_and_options_have_entries():
    from simplydata._underneath import UNDERNEATH

    for key in ("table.combine_studies", "draw_funnel_plot", "table.combine_studies estimates=",
                "table.combine_studies method=", 'table.combine_studies method="Mantel-Haenszel"',
                'table.combine_studies method="Peto"', "table.combine_studies interval_by=",
                "table.combine_studies for_each_group_in=", "table.combine_studies using="):
        assert key in UNDERNEATH, key


@pytest.mark.parametrize("key, setting, replacement", [
    ("table.combine_studies", 'test = "adhoc"', 'test = "z"'),
    ("table.combine_studies", 'method = "REML"', 'method = "DL"'),
    ("table.combine_studies method=", 'method = "DL"', 'method = "REML"'),
])
def test_leaving_out_a_choice_makes_the_comparison_fail(key, setting, replacement, needs_r):
    from simplydata._underneath import UNDERNEATH, Entry
    from simplydata._underneath.check import check_entry

    entry = UNDERNEATH[key]
    assert setting in entry.code["R"]
    changed = dict(entry.code)
    changed["R"] = entry.code["R"].replace(setting, replacement)
    outcomes = check_entry(Entry(**{**entry.__dict__, "code": changed}))
    assert outcomes and not any(o.passed for o in outcomes), f"{key}: should fail without {setting}"
