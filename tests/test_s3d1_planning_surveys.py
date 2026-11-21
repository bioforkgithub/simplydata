"""S3d-1, planning an experiment and survey answers: sdata.make_random_assignments (R blockrand),
sdata.make_design_table (R agricolae), keep_random_rows(for_each_group_in=, percent=) (pandas),
count_empty_cells_in(show="patterns") (pandas, as R mice::md.pattern), count_each(columns=, in_order=) and
chart.draw_answer_bars (pandas, matplotlib) and table.use_survey_design with the survey words (R survey).

The design words have no published answer (a random list): their tests check the properties (every block holds
every group equally often, each latin row and column holds each level once) and that R gives the same list for the
same seed. The survey numbers are checked against R survey on its own api data (Lumley 2010) here and in the
reliability study.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError

DATA = Path(__file__).resolve().parents[1] / "validation" / "data"
LEVELS = ["strongly disagree", "disagree", "neutral", "agree", "strongly agree"]
QUESTIONS = ["teaching", "materials", "pace", "workload", "would_recommend"]
DESIGN = dict(weights="weight", strata="school_type", population_sizes="schools_of_type")


def _r(code, packages=(), **values):
    from simplydata._r import r_call

    return r_call(code, packages=packages, **values)


def _schools():
    t = sdata.table(sdata.get_example("sampled_schools"))
    t.use_survey_design(**DESIGN)
    return t


# ---------------------------------------------------------------- V02: stratified random rows (no R)
def test_rows_from_each_group_are_pandas_groupby_sample():
    df = sdata.get_example("marks")
    t = sdata.table(df)
    t.keep_random_rows(2, for_each_group_in="class", with_seed=1)
    expected = df.groupby("class").sample(n=2, random_state=1).sort_index().reset_index(drop=True)
    pd.testing.assert_frame_equal(t.as_pandas(), expected)


def test_percent_of_each_group_and_at_least_one_row(capsys):
    df = pd.DataFrame({"site": ["a"] * 20 + ["b"] * 3, "x": range(23)})
    t = sdata.table(df)
    t.keep_random_rows(percent=10, for_each_group_in="site", with_seed=1)
    kept = t.as_pandas()["site"].value_counts()
    assert kept["a"] == 2 and kept["b"] == 1
    assert "too small" in capsys.readouterr().out


def test_a_small_group_is_kept_whole_with_a_note(capsys):
    df = pd.DataFrame({"site": ["a"] * 6 + ["b"] * 2, "x": range(8)})
    t = sdata.table(df)
    t.keep_random_rows(3, for_each_group_in="site", with_seed=1)
    assert t.as_pandas()["site"].value_counts().to_dict() == {"a": 3, "b": 2}
    assert "all its rows are kept: b" in capsys.readouterr().out


def test_grouped_rows_are_the_same_on_polars():
    pytest.importorskip("polars")
    a = sdata.table(sdata.get_example("marks"))
    b = sdata.table(sdata.get_example("marks"), fast=True)
    a.keep_random_rows(3, for_each_group_in=["class", "subject"], with_seed=4)
    b.keep_random_rows(3, for_each_group_in=["class", "subject"], with_seed=4)
    pd.testing.assert_frame_equal(a.as_pandas(), b.as_pandas())


def test_percent_without_groups_and_the_refusals():
    t = sdata.table(sdata.get_example("marks"))
    t.keep_random_rows(percent=50, with_seed=1)
    assert len(t) == 27
    t = sdata.table(sdata.get_example("marks"))
    with pytest.raises(SimplydataError, match="not both"):
        t.keep_random_rows(3, percent=10)
    with pytest.raises(SimplydataError, match="above 0 and up to"):
        t.keep_random_rows(percent=150)
    with pytest.raises(SimplydataError, match="column name in quotes"):
        t.keep_random_rows(2, for_each_group_in=3)


# ---------------------------------------------------------------- X06: patterns of empty cells (no R)
def test_patterns_match_isna_value_counts():
    df = pd.read_csv(DATA / "nhanes.csv")
    found = sdata.table(df).count_empty_cells_in(show="patterns").as_pandas()
    assert found["rows with this pattern"].tolist() == [13, 3, 1, 1, 7]
    assert found["empty cells"].tolist() == [0, 1, 1, 2, 3]
    assert found["rows with this pattern"].sum() == len(df)
    pattern = found.loc[found["empty cells"] == 3, ["age", "hyp", "bmi", "chl"]].iloc[0].tolist()
    assert pattern == ["filled", "empty", "empty", "empty"]
    expected = df.isna().value_counts()
    assert sorted(found["rows with this pattern"]) == sorted(expected.tolist())


def test_patterns_count_blank_text_as_empty_and_refuse_other_values():
    df = pd.DataFrame({"a": ["x", " ", None, "y"], "b": [1.0, 2.0, np.nan, 4.0]})
    found = sdata.table(df).count_empty_cells_in(show="patterns").as_pandas()
    assert found["rows with this pattern"].tolist() == [2, 1, 1]
    with pytest.raises(SimplydataError):
        sdata.table(df).count_empty_cells_in(show="pattern of everything")


# ---------------------------------------------------------------- W06: answers on a scale (no R)
def test_answer_counts_percents_top_two_and_median():
    df = sdata.get_example("course_feedback")
    found = sdata.table(df).count_each(columns=QUESTIONS, in_order=LEVELS).as_pandas()
    assert found["question"].tolist() == QUESTIONS
    for _, row in found.iterrows():
        x = df[row["question"]].dropna()
        counts = x.value_counts().reindex(LEVELS, fill_value=0)
        assert [row[lv] for lv in LEVELS] == counts.tolist()
        assert row["answers"] == len(x)
        assert row["percent agree"] == pytest.approx(counts["agree"] * 100 / len(x))
        assert row["percent in top two"] == pytest.approx(x.isin(LEVELS[-2:]).mean() * 100)
        places = x.map({v: i for i, v in enumerate(LEVELS)}).to_numpy()
        assert row["median answer"] == LEVELS[int(np.quantile(places, 0.5, method="inverted_cdf"))]


def test_answers_need_in_order_and_refuse_unknown_answers():
    t = sdata.table(sdata.get_example("course_feedback"))
    with pytest.raises(SimplydataError, match="in_order="):
        t.count_each(columns=["teaching"])
    with pytest.raises(SimplydataError, match="not in in_order="):
        t.count_each(columns=["teaching"], in_order=LEVELS[:4])
    with pytest.raises(SimplydataError, match="at least 3"):
        t.count_each(columns=["teaching"], in_order=["no", "yes"])
    with pytest.raises(SimplydataError, match="interval="):
        t.count_each(columns=["teaching"], in_order=LEVELS, interval=95)


def test_the_median_answer_matches_r_quantile_type_1_and_the_old_count_each_still_works(capsys):
    t = sdata.table(pd.DataFrame({"q": ["no", "no", "maybe", "yes"]}))
    found = t.count_each(columns=["q"], in_order=["no", "maybe", "yes"]).as_pandas()
    assert found["median answer"][0] == "no"  # quantile(c(1, 1, 2, 3), 0.5, type = 1) is 1
    out = sdata.table(sdata.get_example("fruit")).count_each("fruit").as_pandas()
    assert list(out.columns) == ["fruit", "count", "percent"]


def test_answer_bars_are_centred_on_the_middle_answer():
    df = sdata.get_example("course_feedback")
    chart = sdata.chart(df).draw_answer_bars(columns=["teaching", "pace"], in_order=LEVELS)
    from simplydata._underneath.check import _axes_of, chart_facts

    facts = chart_facts(_axes_of(chart))
    bars = facts["bars"]
    assert len(bars) == 10
    p = df["teaching"].value_counts(normalize=True).reindex(LEVELS, fill_value=0) * 100
    middle = [b for b in bars if abs(b[2] - p["neutral"]) < 1e-9 and b[1] > 0.5]
    assert middle and middle[0][0] == pytest.approx(-p["neutral"] / 2)


def test_answer_colours_mirror_each_other():
    from simplydata.words.answer_charts import MIDDLE_COLOUR, answer_colours

    for k in (3, 4, 5, 6, 7):
        colours = answer_colours(k)
        assert len(colours) == k
        assert (MIDDLE_COLOUR in colours) == bool(k % 2)


# ---------------------------------------------------------------- V03: random assignments (R blockrand)
def test_assignments_are_blockrand_with_the_seed(needs_r):
    t = sdata.make_random_assignments(how_many=30, groups=["A", "B", "C"], in_blocks_of=[3, 6], with_seed=7)
    found = _r('set.seed(7, kind = "Mersenne-Twister", normal.kind = "Inversion", sample.kind = "Rejection"); '
               'b <- blockrand::blockrand(n = 30, num.levels = 3, levels = c("A", "B", "C"), block.sizes = c(1, 2)); '
               "list(g = as.character(b$treatment), s = b$block.size)", ("blockrand",))
    df = t.as_pandas()
    assert df["group"].tolist() == list(found["g"])
    assert df["block size"].tolist() == [int(v) for v in found["s"]]


def test_every_block_holds_every_group_equally_often(needs_r):
    df = sdata.make_random_assignments(how_many=50, groups=["A", "B"], for_each_of=["Bergen", "Tromsø"],
                                       with_seed=3).as_pandas()
    assert set(df["list"]) == {"Bergen", "Tromsø"}
    for (_, _), block in df.groupby(["list", "block"]):
        counts = block["group"].value_counts()
        assert len(counts) == 2 and counts.nunique() == 1 and len(block) == block["block size"].iloc[0]
    assert set(df["block size"]) <= {4, 6}
    assert (df.groupby("list").size() >= 50).all()


def test_assignments_refuse_bad_block_sizes_and_take_a_number_of_groups(needs_r):
    with pytest.raises(SimplydataError, match="multiple of the number of groups"):
        sdata.make_random_assignments(how_many=20, groups=3, in_blocks_of=[4])
    with pytest.raises(SimplydataError, match="how_many="):
        sdata.make_random_assignments(groups=2)
    df = sdata.make_random_assignments(how_many=8, groups=2, in_blocks_of=4, with_seed=1).as_pandas()
    assert set(df["group"]) == {"A", "B"} and list(df.columns) == ["number", "block", "block size", "group"]


# ---------------------------------------------------------------- V04 / V06: design tables (R agricolae)
def test_full_factorial_has_every_combination_repeats_times(needs_r):
    df = sdata.make_design_table({"temperature": [10, 20], "salinity": [30, 35], "dose": [0, 1, 2]}, repeats=2,
                                 with_seed=1).as_pandas()
    assert len(df) == 24 and sorted(df["plot"]) == list(range(1, 25))
    assert (df.groupby(["temperature", "salinity", "dose"]).size() == 2).all()
    # the standard order is R expand.grid() order: the first factor changes fastest
    first = df.loc[df["standard order"] == 2].iloc[0]
    assert (first["temperature"], first["salinity"], first["dose"]) == (20, 30, 0)
    assert df["temperature"].dtype.kind in "iu"


def test_randomised_blocks_hold_each_combination_once(needs_r):
    df = sdata.make_design_table({"temperature": [10, 20], "salinity": [30, 35]}, repeats=3,
                                 of_kind="randomised blocks", with_seed=2).as_pandas()
    assert (df.groupby(["block", "temperature", "salinity"]).size() == 1).all()
    assert sorted(df["block"].unique()) == [1, 2, 3]


def test_latin_square_has_each_level_once_in_every_row_and_column(needs_r):
    df = sdata.make_design_table({"variety": ["A", "B", "C", "D", "E"]}, of_kind="latin square",
                                 with_seed=5).as_pandas()
    assert len(df) == 25
    assert (df.groupby("row")["variety"].nunique() == 5).all()
    assert (df.groupby("column")["variety"].nunique() == 5).all()


def test_split_plot_puts_the_named_factor_on_whole_plots(needs_r):
    df = sdata.make_design_table({"variety": ["A", "B", "C"], "irrigation": ["dry", "wet"]}, repeats=2,
                                 of_kind="split plot", whole_plots="irrigation", with_seed=1).as_pandas()
    assert list(df.columns) == ["whole plot", "part of plot", "block", "irrigation", "variety"]
    assert (df.groupby("whole plot")["irrigation"].nunique() == 1).all()
    assert (df.groupby("whole plot")["variety"].nunique() == 3).all()


def test_design_table_refusals(needs_r):
    with pytest.raises(SimplydataError, match="one factor"):
        sdata.make_design_table({"a": [1, 2, 3], "b": [1, 2]}, of_kind="latin square")
    with pytest.raises(SimplydataError, match="whole_plots="):
        sdata.make_design_table({"a": [1, 2], "b": [1, 2]}, repeats=2, of_kind="split plot")
    with pytest.raises(SimplydataError, match="repeats="):
        sdata.make_design_table({"a": [1, 2]})
    with pytest.raises(SimplydataError, match="the table makes itself"):
        sdata.make_design_table({"block": [1, 2]}, repeats=2)
    with pytest.raises(SimplydataError):
        sdata.make_design_table({"a": [1, 2]}, repeats=2, of_kind="random everything")


def test_the_same_seed_gives_the_same_table(needs_r):
    a = sdata.make_design_table({"a": ["x", "y", "z"]}, repeats=3, with_seed=9).as_pandas()
    b = sdata.make_design_table({"a": ["x", "y", "z"]}, repeats=3, with_seed=9).as_pandas()
    pd.testing.assert_frame_equal(a, b)


# ---------------------------------------------------------------- W01 / W02: survey designs (R survey)
API_R = ('d <- survey::svydesign(ids = ~1, strata = ~stype, weights = ~pw, fpc = ~fpc, data = '
         'data.frame(stype, pw, fpc, api00, enroll, sch, awards, meals, ell)); ')


def _api():
    df = pd.read_csv(DATA / "apistrat.csv")
    return dict(stype=df["stype"].to_numpy(dtype=object), pw=df["pw"].to_numpy(dtype=float),
                fpc=df["fpc"].to_numpy(dtype=float), api00=df["api00"].to_numpy(dtype=float),
                enroll=df["enroll"].to_numpy(dtype=float), sch=(df["sch.wide"] == "Yes").to_numpy(dtype=float),
                awards=df["awards"].to_numpy(dtype=object), meals=df["meals"].to_numpy(dtype=float),
                ell=df["ell"].to_numpy(dtype=float))


def test_survey_average_and_total_are_lumleys_numbers(needs_r):
    t = _schools()
    mean = t.find_average_of("score_2000").as_pandas().iloc[0]
    assert mean["average of score_2000"] == pytest.approx(662.287363, abs=5e-6)
    assert mean["standard error"] == pytest.approx(9.408941, abs=5e-6)  # Lumley 2010, the survey help: 662.29 (9.41)
    total = t.find_total_of("pupils").as_pandas().iloc[0]
    assert total["total of pupils"] == pytest.approx(3687178, abs=1)
    assert total["standard error"] == pytest.approx(114642, abs=1)
    found = _r(API_R + "m <- survey::svymean(~api00, d); ci <- confint(m, df = survey::degf(d)); "
                       "list(low = ci[1], high = ci[2])", ("survey",), **_api())
    assert mean["average of score_2000 95 % CI low"] == pytest.approx(float(found["low"][0]), rel=1e-10)
    assert mean["average of score_2000 95 % CI high"] == pytest.approx(float(found["high"][0]), rel=1e-10)
    assert mean["degrees of freedom"] == 197


def test_survey_groups_quantiles_and_percents_match_r(needs_r):
    t = _schools()
    by = t.find_average_of("score_2000", for_each_group_in="award").as_pandas()
    found = _r(API_R + "m <- survey::svyby(~api00, ~awards, d, survey::svymean); list(est = coef(m), se = survey::SE(m))",
               ("survey",), **_api())
    assert by["average of score_2000"].tolist() == pytest.approx(list(found["est"]), rel=1e-10)
    assert by["standard error"].tolist() == pytest.approx(list(found["se"]), rel=1e-10)
    med = t.find_median_of("score_2000").as_pandas().iloc[0]
    q = _r(API_R + 'q <- survey::svyquantile(~api00, d, quantiles = 0.5, qrule = "math", ci = TRUE, '
                   "df = survey::degf(d))$api00; list(q = q[1, 1], low = q[1, 2], high = q[1, 3])", ("survey",), **_api())
    assert (med["median of score_2000"], med["median of score_2000 95 % CI low"],
            med["median of score_2000 95 % CI high"]) == pytest.approx((float(q["q"][0]), float(q["low"][0]),
                                                                         float(q["high"][0])))
    pct = t.find_percent_of_rows_where("met_target", is_equal_to="yes").as_pandas().iloc[0]
    p = _r(API_R + 'p <- survey::svyciprop(~sch, d, method = "logit"); list(est = coef(p), ci = attr(p, "ci"))',
           ("survey",), **_api())
    assert pct["percent"] == pytest.approx(float(p["est"][0]) * 100, rel=1e-10)
    assert pct["percent 95 % CI low"] == pytest.approx(float(p["ci"][0]) * 100, rel=1e-10)
    assert round(pct["percent"], 1) == 82.8  # the survey help: 0.828 (0.775 to 0.871)


def test_survey_counts_models_and_tests_match_r(needs_r):
    t = _schools()
    count = t.count_rows().as_pandas().iloc[0]
    assert count["population count"] == pytest.approx(6194, abs=1e-3)
    share = t.count_rows(for_each_group_in="award", in_percent=True).as_pandas()
    assert share["percent"].sum() == pytest.approx(100)
    fit = t.explain("score_2000", using=["english_learners", "free_meals"]).as_pandas().set_index("term")
    assert fit.loc["free_meals", "estimate"] == pytest.approx(-3.1106, abs=5e-5)  # Lumley 2010 / survey help
    assert fit.loc["(Intercept)", "estimate"] == pytest.approx(823.8579, abs=5e-5)
    tt = t.compare_averages_of("score_2000", for_each_group_in="award").as_pandas().iloc[0]
    assert tt["t"] == pytest.approx(2.3036, abs=5e-5) and tt["degrees of freedom"] == 196
    chi = t.compare_counts_of("award", for_each_group_in="school_type").as_pandas().iloc[0]
    assert chi["F"] == pytest.approx(14.169, abs=5e-4)


def test_a_cluster_design_matches_lumleys_numbers(needs_r):
    df = pd.read_csv(DATA / "apiclus1.csv")
    t = sdata.table(df)
    t.use_survey_design(weights="pw", clusters="dnum", population_sizes="fpc")
    mean = t.find_average_of("api00").as_pandas().iloc[0]
    assert mean["average of api00"] == pytest.approx(644.17, abs=0.005)  # Lumley 2010: 644.17 (23.54)
    assert mean["standard error"] == pytest.approx(23.54, abs=0.005)
    assert mean["degrees of freedom"] == 14


def test_other_statistics_words_refuse_under_a_survey_design(needs_r, capsys):
    t = _schools()
    with pytest.raises(SimplydataError, match="does not use survey designs"):
        t.find_standard_deviation_of("score_2000")
    with pytest.raises(SimplydataError, match="count_rows"):
        t.count_each("award")
    with pytest.raises(SimplydataError, match="takes only"):
        t.find_average_of("score_2000", interval=95)
    with pytest.raises(SimplydataError, match="two groups"):
        t.compare_averages_of("score_2000", for_each_group_in="school_type")
    t.show_first_rows(2)  # data words still work
    assert "a survey" in repr(t)
    t.keep_rows_where("pupils", is_above=500)
    with pytest.raises(SimplydataError, match="removing rows"):
        t.find_average_of("score_2000")
    t.undo()
    t.use_survey_design()
    assert "off" in capsys.readouterr().out
    assert t.find_average_of("score_2000") == pytest.approx(652.82)


def test_survey_design_refuses_empty_design_cells_and_bad_weights(needs_r):
    df = sdata.get_example("sampled_schools")
    bad = df.copy()
    bad.loc[3, "weight"] = np.nan
    with pytest.raises(SimplydataError, match="empty cell"):
        sdata.table(bad).use_survey_design(weights="weight")
    bad = df.copy()
    bad.loc[3, "weight"] = 0
    with pytest.raises(SimplydataError, match="above 0"):
        sdata.table(bad).use_survey_design(weights="weight")
    with pytest.raises(SimplydataError, match="one column name"):
        sdata.table(df).use_survey_design(clusters=["district", "school"])


def test_a_lonely_cluster_is_adjusted_with_a_note(needs_r, capsys):
    df = pd.DataFrame({"s": ["a", "a", "b", "c", "c"], "c": ["1", "2", "3", "4", "5"], "w": [2.0] * 5,
                       "y": [1.0, 2.0, 3.0, 4.0, 6.0]})
    t = sdata.table(df)
    t.use_survey_design(weights="w", strata="s", clusters="c")
    assert "only one cluster" in capsys.readouterr().out
    found = t.find_average_of("y").as_pandas().iloc[0]
    r = _r('options(survey.lonely.psu = "adjust"); d <- survey::svydesign(ids = ~c, strata = ~s, weights = ~w, '
           "data = data.frame(s, c, w, y), nest = TRUE); m <- survey::svymean(~y, d); list(se = survey::SE(m))",
           ("survey",), s=df["s"].to_numpy(dtype=object), c=df["c"].to_numpy(dtype=object),
           w=df["w"].to_numpy(dtype=float), y=df["y"].to_numpy(dtype=float))
    assert found["standard error"] == pytest.approx(float(np.ravel(r["se"])[0]), rel=1e-10)
