"""Errors A8 to A17 of the reference tests (simplydata_tests, notebooks 18 to 24), fixed or documented.

Each test checks simplydata against the reference value the reference tests found: a value printed in a paper
or help page where there is one, otherwise R 4.6.2 run on the same data (R lines in the comments). The
simplydata side uses only simplydata words (get_row) to read its answers.

A8   find_percentile_of(interval=): SciPy's Thompson interval, now named as such (not DescTools' for quartiles)
A9   Spearman's p-value for few rows: R cor.test()'s AS 89, not the t approximation
A10  Barnard's and Boschloo's tests: the for_each_group_in= groups are the two samples
A11  show="cells": no 0.5 added to a table with an empty cell
A12  Dunn's test with more than three groups: each p-value on its own pair
A13  Mann-Whitney with tied values: the exact p-value of R 4.6 wilcox.test()
A14  Krippendorff's alpha with three or more raters: R icr, not irr
A15  ICC(A,k): McGraw and Wong's interval (R psych::ICC), not irr's
A16  draw_smooth_line(): R lowess()'s default delta
A17  the smoothing spline with a number for smoothness=: R's curve differs by R's rounding (documented)
"""

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata

# R datasets::InsectSprays
INSECT_SPRAYS = {
    "A": [10, 7, 20, 14, 14, 12, 10, 23, 17, 20, 14, 13], "B": [11, 17, 21, 11, 16, 14, 17, 17, 19, 21, 7, 13],
    "C": [0, 1, 7, 2, 3, 1, 2, 1, 3, 0, 1, 4], "D": [3, 5, 12, 6, 4, 3, 5, 5, 5, 5, 2, 4],
    "E": [3, 5, 3, 5, 3, 6, 1, 1, 3, 2, 6, 4], "F": [11, 9, 15, 22, 15, 16, 13, 10, 26, 26, 24, 13]}
# R irr::anxiety (3 raters, 20 subjects)
ANXIETY = {"rater1": [3, 3, 3, 4, 5, 5, 2, 3, 5, 2, 2, 6, 1, 5, 2, 2, 1, 2, 4, 3],
           "rater2": [3, 6, 4, 6, 2, 4, 2, 4, 3, 3, 2, 3, 3, 3, 2, 2, 1, 3, 3, 4],
           "rater3": [2, 1, 4, 4, 3, 2, 1, 6, 1, 1, 1, 2, 3, 3, 1, 1, 3, 3, 2, 2]}
# R irr::diagnoses (6 raters, 30 patients), categories 1 to 5
DIAGNOSES = [
    [4, 2, 2, 5, 2, 1, 3, 1, 1, 5, 1, 1, 2, 1, 2, 3, 1, 1, 2, 1, 5, 2, 2, 1, 1, 2, 1, 2, 1, 5],
    [4, 2, 3, 5, 2, 1, 3, 1, 1, 5, 4, 2, 2, 4, 2, 3, 1, 1, 2, 3, 5, 4, 2, 1, 4, 2, 1, 2, 3, 5],
    [4, 2, 3, 5, 2, 3, 3, 3, 4, 5, 4, 4, 2, 4, 4, 3, 1, 1, 4, 3, 5, 4, 4, 4, 4, 2, 1, 4, 3, 5],
    [4, 5, 3, 5, 4, 3, 3, 3, 4, 5, 4, 4, 3, 4, 4, 3, 4, 1, 4, 5, 5, 4, 5, 4, 4, 2, 1, 4, 3, 5],
    [4, 5, 3, 5, 4, 3, 5, 3, 4, 5, 4, 4, 3, 4, 4, 3, 5, 1, 4, 5, 5, 4, 5, 4, 4, 2, 5, 4, 3, 5],
    [4, 5, 5, 5, 4, 3, 5, 4, 4, 5, 4, 4, 3, 4, 5, 5, 5, 2, 4, 5, 5, 4, 5, 4, 5, 4, 5, 4, 3, 5]]
DIAGNOSIS_NAMES = {1: "1. Depression", 2: "2. Personality Disorder", 3: "3. Schizophrenia", 4: "4. Neurosis",
                   5: "5. Other"}
# R datasets::mtcars
WEIGHT = [2.62, 2.875, 2.32, 3.215, 3.44, 3.46, 3.57, 3.19, 3.15, 3.44, 3.44, 4.07, 3.73, 3.78, 5.25, 5.424, 5.345,
          2.2, 1.615, 1.835, 2.465, 3.52, 3.435, 3.84, 3.845, 1.935, 2.14, 1.513, 3.17, 2.77, 3.57, 2.78]
MPG = [21.0, 21.0, 22.8, 21.4, 18.7, 18.1, 14.3, 24.4, 22.8, 19.2, 17.8, 16.4, 17.3, 15.2, 10.4, 10.4, 14.7, 32.4,
       30.4, 33.9, 21.5, 15.5, 15.2, 13.3, 19.2, 27.3, 26.0, 30.4, 15.8, 19.7, 15.0, 21.4]


def rows_of(result):
    return [result.get_row(i) for i in range(1, len(result) + 1)]


def pairs_of(result, column):
    return {(r["group 1"], r["group 2"]): r[column] for r in rows_of(result)}


def insect_sprays(order="ABCDEF"):
    return sdata.table(pd.DataFrame({"spray": [s for s in order for _ in INSECT_SPRAYS[s]],
                                     "count": [v for s in order for v in INSECT_SPRAYS[s]]}))


# ------------------------------------------------------------------------------------------------ A8
def test_a8_percentile_interval_is_thompsons_and_says_so(capsys):
    from scipy import stats

    # R datasets::airquality, Ozone in May
    ozone = [41, 36, 12, 18, None, 28, 23, 19, 8, None, 7, 16, 11, 14, 18, 14, 34, 6, 30, 11, 1, 11, 4, 32, None,
             None, None, 23, 45, 115, 37]
    t = sdata.table(pd.DataFrame({"Ozone": ozone}))
    got = t.find_percentile_of("Ozone", 25, interval=95).get_row(1)
    # SciPy quantile_test(x, q=11, p=0.25).confidence_interval(0.95): (4, 16). R DescTools::QuantileCI(x, probs =
    # 0.25, method = "exact") gives (4, 14): another pair of order statistics, both exact
    kept = np.array([v for v in ozone if v is not None], dtype=float)
    ci = stats.quantile_test(kept, q=11, p=0.25).confidence_interval(0.95)
    assert (got["percentile 25 of Ozone 95 % CI low"], got["percentile 25 of Ozone 95 % CI high"]) == (ci.low, ci.high)
    assert (ci.low, ci.high) == (4, 16)
    out = capsys.readouterr().out
    assert "Thompson's interval" in out and 'DescTools::QuantileCI(method = "exact") picks another pair' in out
    t.find_median_of("Ozone", interval=95)
    assert 'as R DescTools::MedianCI(method = "exact")' in capsys.readouterr().out
    t.find_percentile_of("Ozone", 50, interval=95)
    out = capsys.readouterr().out
    assert 'as R DescTools::MedianCI(method = "exact")' in out and "picks another pair" not in out


# ------------------------------------------------------------------------------------------------ A9
X_HW = [44.4, 45.9, 41.9, 53.3, 44.7, 44.1, 50.7, 45.2, 60.1]  # R cor.test help page (Hollander & Wolfe 1973)
Y_HW = [2.6, 3.1, 2.5, 5.0, 3.6, 4.0, 5.2, 2.8, 3.8]


def test_a9_spearman_p_value_is_r_cor_test(needs_r, capsys):
    t = sdata.table(pd.DataFrame({"x": X_HW, "y": Y_HW}))
    t.find_correlation_between("x", "y", test_method="spearman")
    out = capsys.readouterr().out
    # R: cor.test(x, y, method = "spearman")$p.value = 0.0967978395061728 (AS 89); SciPy's t approximation: 0.088
    assert "(p = 0.097)" in out and "algorithm AS 89" in out
    # the table of pairs gives the number itself
    data = pd.DataFrame({"x": X_HW, "y": Y_HW, "z": [1.0, 3, 2, 5, 4, 7, 6, 9, 8]})
    pairs = rows_of(sdata.table(data).find_correlation_between("x", "y", "z", test_method="spearman",
                                                                show="each pair"))
    first = next(r for r in pairs if (r["column 1"], r["column 2"]) == ("x", "y"))
    assert first["p-value"] == pytest.approx(0.0967978395061728, rel=1e-9)
    out = capsys.readouterr().out
    assert "algorithm AS 89" in out and "t approximation for the others" not in out
    # one-sided: R cor.test(x, y, method = "spearman", alternative = "greater")$p.value
    t.find_correlation_between("x", "y", test_method="spearman", sides=1, higher="positive")
    assert "(p = 0.048)" in capsys.readouterr().out


def test_a9_spearman_with_ties_stays_the_t_approximation(needs_r):
    from scipy import stats

    x = [1.0, 2, 2, 3, 4, 5, 6, 7, 8]
    data = pd.DataFrame({"x": x, "y": Y_HW, "z": X_HW})
    pairs = rows_of(sdata.table(data).find_correlation_between("x", "y", "z", test_method="spearman",
                                                                show="each pair"))
    first = next(r for r in pairs if (r["column 1"], r["column 2"]) == ("x", "y"))
    # R cor.test(method = "spearman") with ties: the t approximation too (it warns it cannot give the exact value)
    assert first["p-value"] == pytest.approx(stats.spearmanr(x, Y_HW).pvalue, rel=1e-12)


# ------------------------------------------------------------------------------------------------ A10
def twins():
    # R fisher.test help page: Fisher (1962), convictions of like-sex twins of criminals
    return pd.DataFrame({"twins": ["Dizygotic"] * 17 + ["Monozygotic"] * 13,
                         "convicted": ["yes"] * 2 + ["no"] * 15 + ["yes"] * 10 + ["no"] * 3})


@pytest.mark.parametrize("test, expected", [
    # R: Exact::exact.test(matrix(c(2, 10, 15, 3), 2), method = "z-pooled" / "boschloo")$p.value, the twin types as
    # the two samples (rows); with the outcome as the samples it would be 0.000280 for both (the old answer)
    ("barnard", 0.000347966328249), ("boschloo", 0.000259677487134)])
def test_a10_barnard_and_boschloo_take_the_groups_as_samples(needs_r, capsys, test, expected):
    got = sdata.table(twins()).compare_counts_of("convicted", for_each_group_in="twins", test_method=test).get_row(1)
    assert got["p-value"] == pytest.approx(expected, rel=1e-8)
    assert 'with the "twins" groups as the two samples' in capsys.readouterr().out
    got = sdata.compare_counts([[2, 15], [10, 3]], test_method=test).get_row(1)
    assert got["p-value"] == pytest.approx(expected, rel=1e-8)
    assert "with the rows as the two samples" in capsys.readouterr().out


# ------------------------------------------------------------------------------------------------ A11
def test_a11_cell_residuals_with_an_empty_cell_are_r_chisq_test(capsys):
    # R fisher.test help page: job satisfaction by income (Agresti 2002), one cell is 0
    job = [[1, 3, 10, 6], [2, 3, 10, 7], [1, 6, 14, 12], [0, 1, 9, 11]]
    income = ["< 15k", "15-25k", "25-40k", "> 40k"]
    satisfaction = ["VeryD", "LittleD", "ModerateS", "VeryS"]
    data = pd.DataFrame([(income[i], satisfaction[j]) for i in range(4) for j in range(4) for _ in range(job[i][j])],
                        columns=["income", "satisfaction"])
    cells = rows_of(sdata.table(data).compare_counts_of("satisfaction", for_each_group_in="income", show="cells"))
    got = {(r["satisfaction"], r["income"]): (r["standardised residual"], r["expected count"]) for r in cells}
    # R: chisq.test(Job)$stdres and $expected, Job <- matrix(c(1,2,1,0, 3,3,6,1, 10,10,14,9, 6,7,12,11), 4, 4)
    assert got[("VeryD", "< 15k")] == pytest.approx((0.209608985431101, 0.833333333333333), rel=1e-9)
    assert got[("VeryD", "> 40k")] == pytest.approx((-1.081062279507482, 0.875), rel=1e-9)
    assert got[("LittleD", "15-25k")] == pytest.approx((0.0147852165436014, 2.97916666666667), rel=1e-9)
    assert got[("VeryS", "> 40k")] == pytest.approx((1.593638145779191, 7.875), rel=1e-9)
    assert "shift_zeros=False" in capsys.readouterr().out


# ------------------------------------------------------------------------------------------------ A12
# R: r <- FSA::dunnTest(count ~ spray, data = InsectSprays, method = "none")$res: Comparison, Z and
# p.adjust(r$P.unadj, "holm") (= PMCMRplus::kwAllPairsDunnTest(p.adjust.method = "holm")). FSA's own "holm" gave
# B - F 0.926028 (no running maximum, A25); Holm's steps give 1
DUNN = {("A", "B"): (-0.312733845267036, 1.0), ("A", "C"): (4.774077606654594, 2.34692588071616e-05),
        ("B", "C"): (5.086811451921631, 5.09786923649587e-06), ("A", "D"): (3.117565520005764, 1.27645986419524e-02),
        ("B", "D"): (3.430299365272800, 4.82332532083788e-03), ("C", "D"): (-1.656512086648831, 5.85708956559377e-01),
        ("A", "E"): (3.850535469850379, 1.17859858819944e-03), ("B", "E"): (4.163269315117415, 3.45095263365611e-04),
        ("C", "E"): (-0.923542136804215, 1.0), ("D", "E"): (0.732969949844615, 1.0),
        ("A", "F"): (-0.405576705580687, 1.0), ("B", "F"): (-0.092842860313651, 1.0),
        ("C", "F"): (-5.179654312235281, 3.33446187777777e-06), ("D", "F"): (-3.523142225586451, 3.83816198213718e-03),
        ("E", "F"): (-4.256112175431067, 2.49614844898269e-04)}


def _dunn_expected(first, second):  # z is the first group's mean rank minus the second's
    if (first, second) in DUNN:
        return DUNN[(first, second)]
    z, p = DUNN[(second, first)]
    return -z, p


@pytest.mark.parametrize("order", ["ABCDEF", "FCAEBD"])
def test_a12_dunn_p_values_belong_to_their_pairs(needs_r, order):
    result = insect_sprays(order).compare_each_pair_of("count", for_each_group_in="spray", test_method="dunn")
    rows = rows_of(result)
    assert len(rows) == 15
    for r in rows:
        z, p = _dunn_expected(r["group 1"], r["group 2"])
        assert (r["statistic"], r["p-value (adjusted)"]) == pytest.approx((z, p), rel=1e-9), (r["group 1"],
                                                                                                r["group 2"])
    # the case the reference tests found: C - B was given D - C's p-value (0.586)
    got = pairs_of(result, "p-value (adjusted)")
    assert got.get(("B", "C"), got.get(("C", "B"))) == pytest.approx(5.09786923649587e-06, rel=1e-9)


@pytest.mark.parametrize("order", ["DCBA", "EBDCA"])
def test_a12_dunn_with_four_and_five_groups_against_r(needs_r, order):
    from simplydata._r import r_call

    result = insect_sprays(order).compare_each_pair_of("count", for_each_group_in="spray", test_method="dunn")
    y = np.concatenate([INSECT_SPRAYS[s] for s in order]).astype(float)
    g = np.repeat(np.array(list(order), dtype=object), 12)
    # R itself, with the groups in the order given: FSA matches nothing by position here, only by name
    ref = r_call("r <- FSA::dunnTest(y ~ factor(g, levels = unique(g)), method = 'none')$res; "
                 "list(pair = as.character(r$Comparison), z = r$Z, p = p.adjust(r$P.unadj, 'holm'))", y=y, g=g)
    expected = {}
    for name, z, p in zip(ref["pair"], np.asarray(ref["z"], float), np.asarray(ref["p"], float)):
        first, second = str(name).split(" - ")
        expected[(first, second)], expected[(second, first)] = (z, p), (-z, p)
    rows = rows_of(result)
    assert len(rows) == len(order) * (len(order) - 1) // 2
    for r in rows:
        assert (r["statistic"], r["p-value (adjusted)"]) == pytest.approx(expected[(r["group 1"], r["group 2"])],
                                                                          rel=1e-9)


# ------------------------------------------------------------------------------------------------ A13
# R 4.6.2: pairwise.wilcox.test(InsectSprays$count, InsectSprays$spray, p.adjust.method = "holm")$p.value (exact
# with ties since R 4.6.0; the normal approximation gave C - A 5.1e-4)
PAIRWISE_WILCOX = {("A", "C"): 1.62712506231149e-05, ("B", "C"): 1.62712506231149e-05,
                   ("A", "D"): 3.99385242567367e-05, ("C", "D"): 1.10319079224719e-02,
                   ("A", "E"): 1.10940345157602e-05, ("C", "E"): 2.45695884409035e-01,
                   ("D", "E"): 6.77327787302212e-01, ("C", "F"): 1.10940345157602e-05,
                   ("A", "B"): 1.0, ("A", "F"): 1.0}


def test_a13_pairwise_mann_whitney_with_ties_is_exact(needs_r_4_6, capsys):
    result = insect_sprays().compare_each_pair_of("count", for_each_group_in="spray", based_on="ranks")
    got = pairs_of(result, "p-value (Holm)")
    for pair, expected in PAIRWISE_WILCOX.items():
        assert got[pair] == pytest.approx(expected, rel=1e-9), pair
    assert "exact p-value given the tied values, from R wilcox.test()" in capsys.readouterr().out


def test_a13_two_groups_with_ties_is_exact(needs_r_4_6, capsys):
    data = pd.DataFrame({"spray": ["C"] * 12 + ["A"] * 12, "count": INSECT_SPRAYS["C"] + INSECT_SPRAYS["A"]})
    got = sdata.table(data).compare_averages_of("count", for_each_group_in="spray", based_on="ranks").get_row(1)
    # R 4.6.2: wilcox.test(A, C)$p.value (Wilcoxon rank sum exact test; the groups in sorted order), W = 143.5
    assert got["p-value"] == pytest.approx(1.47920460210136e-06, rel=1e-9)
    assert got["statistic"] == 143.5
    # the Hodges-Lehmann shift and its interval as R 4.6 gives them with ties (exact, Bauer 1972):
    # R: wilcox.test(A, C, conf.int = TRUE): estimate 12, conf.int 9 to 16
    assert (got["shift"], got["shift 95 % CI low"], got["shift 95 % CI high"]) == pytest.approx((12, 9, 16), abs=1e-6)
    assert "exact p-value given the tied values" in capsys.readouterr().out


def test_a13_without_r_the_normal_approximation_says_so(monkeypatch):
    from scipy import stats

    from simplydata import _r
    from simplydata.table.stat_tests import _mann_whitney

    def no_r(*args, **kwargs):
        raise _r.RMissing("no R here")

    monkeypatch.setattr(_r, "r_call", no_r)
    a, b = np.array(INSECT_SPRAYS["C"], float), np.array(INSECT_SPRAYS["A"], float)
    u, p, how = _mann_whitney(a, b)
    assert p == pytest.approx(stats.mannwhitneyu(a, b, method="asymptotic").pvalue, rel=1e-12)
    assert how.startswith("normal approximation") and "R 4.6 or later gives the exact p-value" in how
    # without ties nothing needs R: SciPy's exact p-value is R's
    u, p, how = _mann_whitney(np.array([1.0, 2, 3]), np.array([4.0, 5, 6, 7]))
    assert how == "exact p-value"


# ------------------------------------------------------------------------------------------------ A14
def test_a14_icr_gives_krippendorffs_published_examples(needs_r):
    from simplydata._r import r_call

    # Krippendorff (2011), Computing Krippendorff's alpha-reliability: 4 coders, 12 units, with gaps;
    # published alpha 0.743 (nominal), 0.815 (ordinal), 0.849 (interval), 0.797 (ratio)
    data = np.array([[1, 2, 3, 3, 2, 1, 4, 1, 2, np.nan, np.nan, np.nan],
                     [1, 2, 3, 3, 2, 2, 4, 1, 2, 5, np.nan, 3],
                     [np.nan, 3, 3, 3, 2, 3, 4, 2, 2, 5, 1, np.nan],
                     [1, 2, 3, 3, 2, 4, 4, 1, 2, 5, 1, np.nan]])
    for metric, published in (("nominal", 0.743), ("ordinal", 0.815), ("interval", 0.849), ("ratio", 0.797)):
        alpha = float(np.asarray(r_call("icr::krippalpha(x, metric = m)$alpha", x=data, m=metric))[0])
        assert round(alpha, 3) == published, metric


def test_a14_krippendorff_three_or_more_raters(needs_r, capsys):
    got = sdata.table(pd.DataFrame(ANXIETY)).agreement_between("rater1", "rater2", "rater3",
                                                               test_method="krippendorff").get_row(1)
    # Krippendorff's coincidence-matrix formula written out (reference tests) and R icr::krippalpha: 0.1701;
    # irr::kripp.alpha gave 0.1631 (each pair weighted 1 instead of 1 / (m - 1))
    assert got["estimate"] == pytest.approx(0.170098607888631, rel=1e-9)
    assert "icr::krippalpha" in got["method"]
    data = pd.DataFrame({f"rater{i + 1}": [DIAGNOSIS_NAMES[v] for v in rater] for i, rater in enumerate(DIAGNOSES)})
    got = sdata.table(data).agreement_between(*data.columns, test_method="krippendorff").get_row(1)
    # the same two references: 0.4334 (irr: 0.4309)
    assert got["estimate"] == pytest.approx(0.4334098, abs=1e-7)
    assert "Hayes and Krippendorff 2007" in capsys.readouterr().out


# ------------------------------------------------------------------------------------------------ A15
def test_a15_icc_average_of_raters_agreement_interval(needs_r, capsys):
    t = sdata.table(pd.DataFrame(ANXIETY))
    got = t.agreement_between("rater1", "rater2", "rater3", of="average of raters").get_row(1)
    # R: psych::ICC(anxiety, lmer = FALSE)$results["Average_random_raters", ] (ICC2k), the same as McGraw and Wong's
    # (1996) formula written out; irr::icc gave (-0.1373, 0.7463)
    assert (got["estimate"], got["estimate 95 % CI low"], got["estimate 95 % CI high"]) == pytest.approx(
        (0.425498753117207, -0.12658270270946, 0.74514928854521), rel=1e-9)
    assert (got["statistic"], got["p-value"]) == pytest.approx((1.82677165354331, 0.0562012735474978), rel=1e-9)
    assert "psych::ICC(lmer = FALSE), its row ICC2k" in capsys.readouterr().out


# ------------------------------------------------------------------------------------------------ A16
def test_a16_smooth_line_is_r_lowess_default():
    # no simplydata word gives back the numbers a chart draws, so this reads the drawn line from matplotlib
    from simplydata.chart import Chart

    # R: lowess(mtcars$wt, mtcars$mpg)$y (f = 2/3, iter = 3, delta = 0.01 * diff(range(wt)))
    r_lowess = [31.507092675983, 30.62374722422, 28.728197685098, 27.880539448508, 26.18178726804, 25.694303010452,
                24.722566890279, 23.473789391725, 22.322232981841, 21.291299374814, 21.244594734866, 20.71496972638,
                19.588332479204, 19.472594392314, 19.340496866707, 19.177434958506, 17.887555860686, 17.856548111509,
                17.856548111509, 17.856548111509, 17.732517114799, 17.380983926609, 17.101262745516, 17.101262745516,
                16.243855291361, 15.985916513265, 15.683177662286, 15.658310258661, 14.828126754649, 11.980844920192,
                11.706299667678, 11.478285254921]
    chart = Chart(pd.DataFrame({"wt": WEIGHT, "mpg": MPG})).draw_dots(x="wt", y="mpg").draw_smooth_line()
    ax = chart._render().axes[0]
    line = next(line for line in ax.lines if len(line.get_ydata()) == len(WEIGHT))
    assert np.max(np.abs(np.asarray(line.get_ydata()) - r_lowess)) < 1e-8  # was 5e-4 with delta = 0


# ------------------------------------------------------------------------------------------------ A17
def test_a17_spline_with_repeated_x_is_within_rs_rounding():
    # R: predict(smooth.spline(mtcars$wt, mtcars$mpg, all.knots = TRUE, lambda = 0.001), at)$y (some weights
    # repeat). R's curve differs from SciPy's by about 1e-5 with or without repeated x; SciPy's makes the
    # penalised sum smaller (195.00654515 against R's 195.00655222), so the difference is R's rounding.
    at = [1.513, 2.311163265306, 3.508408163265, 4.705653061224, 5.424]
    r_curve = [31.802929318492, 25.317171384304, 17.30492461936, 13.469631934336, 11.649845625156]
    t = sdata.table(pd.DataFrame({"wt": WEIGHT, "mpg": MPG}))
    got = [r["mpg"] for r in rows_of(t.find_values_at("mpg", at={"wt": at}, smoothness=0.001))]
    assert np.max(np.abs(np.asarray(got) - r_curve) / np.abs(r_curve)) < 2e-5


@pytest.mark.parametrize("smoothness", [0.01, 0.001])
def test_a17_spline_is_scipys_curve_at_the_same_lambda(smoothness, capsys):
    # The package simplydata calls: SciPy make_smoothing_spline on the distinct weights (x mapped onto 0 to 1, as R
    # does), the mpg of repeated weights averaged with weight = how many (as R smooth.spline). The gap to R is not
    # about the repeats: with every weight made distinct (+ 1e-4 per row) R and SciPy still differ by 1.17e-5 at
    # lambda = 0.01, and SciPy's curve gives the smaller penalised sum (checked 2026-11-23, R 4.6.2, SciPy 1.18.1).
    from scipy.interpolate import make_smoothing_spline

    ux, where, counts = np.unique(WEIGHT, return_inverse=True, return_counts=True)
    uy = np.bincount(where, weights=MPG) / counts
    at = np.linspace(min(WEIGHT), max(WEIGHT), 9)
    scipy_curve = make_smoothing_spline((ux - ux[0]) / (ux[-1] - ux[0]), uy, w=counts.astype(float),
                                        lam=smoothness)((at - ux[0]) / (ux[-1] - ux[0]))
    t = sdata.table(pd.DataFrame({"wt": WEIGHT, "mpg": MPG}))
    got = [r["mpg"] for r in rows_of(t.find_values_at("mpg", at={"wt": list(at)}, smoothness=smoothness))]
    assert np.asarray(got) == pytest.approx(scipy_curve, rel=1e-12)
    capsys.readouterr()
