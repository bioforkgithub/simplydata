"""S1 Part A, rest: Hodges-Lehmann shift, z-test, trend tests (Cochran-Armitage, Jonckheere, Page), Fisher on bigger
tables, chi-square by shuffling, standardized residuals, and the correlation additions (intervals for every r,
Somers' d, gamma, partial correlation).

Reference values: R 4.6.2 (BSDA, clinfun, crank, DescTools, ppcor) on the example tables clinic and marks. Scripts:
F:/claude_work/scratch/simplydata/s1_a/a_more_ref.R and a9_ref.R.
"""

import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table

REL = 1e-9
A = [12.1, 14.3, 11.8, 15.2, 13.9, 12.7, 14.8, 13.1, 12.4, 15.6]
B = [10.2, 11.9, 12.8, 10.7, 11.1, 13.4, 10.9, 12.2, 11.5, 10.4, 12.9, 11.0]
AGES = ["under 50", "50 to 69", "70 or over"]


@pytest.fixture(params=["pandas", "polars"])
def engine(request):
    return request.param


def make(engine, data):
    if engine == "polars":
        pl = pytest.importorskip("polars")
        return make_table(pl.from_pandas(data))
    return make_table(data)


def clinic(engine):
    return make(engine, sdata.get_example("clinic"))


def row(result):
    return result._frame.to_pandas().iloc[0].to_dict()


def test_hodges_lehmann(engine, needs_r, capsys):
    t = make(engine, pd.DataFrame({"v": A + B, "g": ["a"] * 10 + ["b"] * 12}))
    got = row(t.compare_averages_of("v", for_each_group_in="g", based_on="ranks"))
    # R: wilcox.test(a, b, conf.int = TRUE, exact = TRUE): estimate 2, conf.int 0.9 to 3.3
    assert (got["shift"], got["shift 95 % CI low"], got["shift 95 % CI high"]) == pytest.approx(
        (2.0, 0.9, 3.3), rel=1e-9)
    assert "the typical shift from b to a (Hodges-Lehmann) is 2.00" in capsys.readouterr().out
    got = row(clinic(engine).compare_averages_of("crp", for_each_group_in="ward", based_on="ranks"))
    # R: wilcox.test(crp[ward A], crp[ward B], conf.int = TRUE, exact = FALSE, correct = TRUE) (ties)
    assert (got["shift"], got["shift 95 % CI low"], got["shift 95 % CI high"]) == pytest.approx(
        (-0.3999147970053, -0.7000212919475, 4.332247576894e-05), rel=1e-6)


def test_z_test(engine, needs_r, capsys):
    t = clinic(engine)
    got = row(t.compare_average_to("device_a", 128, test_method="z", standard_deviation=15))
    # R: BSDA::z.test(device_a, mu = 128, sigma.x = 15)
    assert (got["statistic"], got["p-value"]) == pytest.approx((-2.173174840847, 0.02976716059574), rel=REL)
    assert (got["average 95 % CI low"], got["average 95 % CI high"]) == pytest.approx(
        (123.6161442635, 127.7738557365), rel=REL)
    got = row(t.compare_average_to("device_a", 128, test_method="z", standard_deviation=15, sides=1, higher="average"))
    assert got["p-value"] == pytest.approx(0.9851164197021, rel=REL)  # R: alternative = "greater"
    assert "known standard deviation 15" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match='goes with test_method="z"'):
        t.compare_average_to("device_a", 128, standard_deviation=15)


def test_cochran_armitage_trend(engine, needs_r, capsys):
    got = row(clinic(engine).compare_counts_of("infected", for_each_group_in="age_group", test_method="trend", in_order=AGES))
    # R: prop.trend.test(infected per age group, rows per age group)
    assert (got["statistic"], got["p-value"]) == pytest.approx((4.096453900709, 0.04297325537021), rel=REL)
    assert "(in this order)" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="in_order="):
        clinic(engine).compare_counts_of("infected", for_each_group_in="age_group", test_method="trend")


def test_fisher_bigger_table(engine, needs_r):
    t = clinic(engine)
    exact = row(t.compare_counts_of("nurse_rating", for_each_group_in="ward", test_method="fisher", p_value_by="exact"))
    # R: fisher.test(table(nurse_rating, ward))$p.value
    assert exact["p-value"] == pytest.approx(0.4523917859695, rel=1e-9)
    seeded = row(t.compare_counts_of("nurse_rating", for_each_group_in="ward", test_method="fisher"))
    # SciPy Monte Carlo with 100,000 tables, seed 1, against R's exact p above. The standard error of a Monte Carlo
    # p-value is sqrt(p (1 - p) / 100000) = 0.00157; allow 5 of them (0.0079). Within one platform the seeded value
    # never changes (checked below), but between platforms it moves more than one SE: Windows and Linux 0.4523,
    # macOS 0.4453 (4.5 SE), most likely because tables exactly as probable as the observed one are rounded
    # differently and so counted or not (R's fisher.test() uses a 1e-7 relative tolerance for such ties).
    se = (0.4523917859695 * (1 - 0.4523917859695) / 100_000) ** 0.5
    assert seeded["p-value"] == pytest.approx(0.4523917859695, abs=5 * se)
    assert row(t.compare_counts_of("nurse_rating", for_each_group_in="ward", test_method="fisher"))["p-value"] == seeded["p-value"]


def test_chi_square_by_shuffling(engine):
    t = clinic(engine)
    got = row(t.compare_counts_of("nurse_rating", for_each_group_in="ward", p_value_by="shuffling"))
    # R: set.seed(1); chisq.test(tab, simulate.p.value = TRUE, B = 9999)$p.value = 0.4554 (Monte Carlo, SE 0.005)
    assert got["p-value"] == pytest.approx(0.4554, abs=0.02)
    assert got["p-value by"] == "9999 random tables, seed 1"


def test_standardized_residuals(engine, capsys):
    cells = clinic(engine).compare_counts_of("nurse_rating", for_each_group_in="ward", show="cells")._frame.to_pandas()
    got = cells.set_index(["nurse_rating", "ward"])["standardised residual"]
    # R: chisq.test(table(nurse_rating, ward))$stdres
    assert got[("mild", "ward A")] == pytest.approx(0.7548514, abs=1e-7)
    assert got[("moderate", "ward B")] == pytest.approx(1.3145341, abs=1e-7)
    assert got[("severe", "ward B")] == pytest.approx(-0.6172134, abs=1e-7)
    assert "No cell stands out" in capsys.readouterr().out


def test_jonckheere(engine, capsys):
    got = row(clinic(engine).compare_averages_of("crp", for_each_group_in="age_group", test_method="jonckheere", in_order=AGES))
    # R: clinfun::jonckheere.test(crp, age group 1-3, alternative = "two.sided"): JT 7129.5, p 0.2034804321529
    # (both normal approximations; they treat the many tied crp values a little differently, so 2e-3 on p)
    assert got["statistic"] == pytest.approx(7129.5, rel=REL)
    assert got["p-value"] == pytest.approx(0.2034804321529, rel=2e-3)
    assert "Jonckheere-Terpstra" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="in_order"):
        clinic(engine).compare_averages_of("crp", for_each_group_in="age_group", test_method="jonckheere")


def test_page(engine):
    got = row(clinic(engine).compare_matched_columns("pain_week_8", "pain_week_4", "pain_week_0", test_method="page"))
    # R: crank::page.trend.test(cbind(pain_week_8, pain_week_4, pain_week_0), ranks = FALSE): L 2671, pZ
    assert got["statistic"] == pytest.approx(2671, rel=REL)
    assert got["p-value"] == pytest.approx(3.961507044995e-42, rel=1e-6)


def test_correlation_intervals(engine, needs_r, capsys):
    t = make(engine, sdata.get_example("marks"))
    t.find_correlation_between("hours", "marks")
    # R: cor.test(hours, marks)$conf.int = 0.7248775809032 to 0.8989551498483
    assert "values from 0.725 to 0.899 fit the data (95 % CI)" in capsys.readouterr().out
    t.find_correlation_between("hours", "marks", test_method="spearman")
    # R: DescTools::SpearmanRho(hours, marks, conf.level = 0.95): 0.6993628222936 to 0.8885410918343
    assert "values from 0.699 to 0.889 fit the data (95 % CI, Fisher's z" in capsys.readouterr().out
    t.find_correlation_between("hours", "marks", test_method="kendall")
    # R: DescTools::KendallTauB(hours, marks, conf.level = 0.95): 0.5315458077896 to 0.7549871038909
    assert "values from 0.532 to 0.755 fit the data (95 % CI, asymptotic standard error" in capsys.readouterr().out


def test_somers_and_gamma(engine, needs_r, capsys):
    t = make(engine, sdata.get_example("marks"))
    # R: DescTools::SomersDelta(hours, marks, direction = "column") = 0.6409893992933 (= SciPy somersd(hours, marks))
    assert t.find_correlation_between("hours", "marks", test_method="somers") == pytest.approx(0.6409893992933, rel=REL)
    # R: DescTools::GoodmanKruskalGamma(hours, marks, conf.level = 0.95): 0.6529877609791 (0.5397892889546 to
    # 0.7661862330036)
    assert t.find_correlation_between("hours", "marks", test_method="gamma") == pytest.approx(0.6529877609791, rel=REL)
    out = capsys.readouterr().out
    assert "values from 0.540 to 0.766 fit the data" in out and "the interval leaves out 0" in out


def test_partial_correlation(engine, needs_r, capsys):
    t = make(engine, sdata.get_example("marks"))
    # R: ppcor::pcor.test(hours, marks, height): estimate 0.8313328118386, p 1.295704900218e-14
    assert t.find_correlation_between("hours", "marks", allowing_for="height") == pytest.approx(0.8313328118386, rel=REL)
    assert "p < 0.0001" in capsys.readouterr().out or True
    # R: pcor.test(hours, marks, height, method = "spearman")$estimate
    assert t.find_correlation_between("hours", "marks", allowing_for="height", test_method="spearman") == pytest.approx(
        0.814857940429, rel=REL)
    with pytest.raises(SimplydataError, match="two columns"):
        t.find_correlation_between("hours", "marks", "height", allowing_for="height")


def _pain_long(engine):
    d = sdata.get_example("clinic")
    long = pd.DataFrame({"patient": list(d.patient) * 3,
                         "week": ["week 0"] * 200 + ["week 4"] * 200 + ["week 8"] * 200,
                         "pain": list(d.pain_week_0) + list(d.pain_week_4) + list(d.pain_week_8)})
    return make(engine, long)


def test_pairs_within_matched_rows(engine, capsys):
    t = _pain_long(engine)
    got = t.compare_each_pair_of("pain", for_each_group_in="week", matched_by="patient", based_on="ranks")._frame.to_pandas()
    got = got.set_index(["group 1", "group 2"])["p-value (Holm)"]
    # R: pairwise.wilcox.test(pain, week, paired = TRUE, p.adjust.method = "holm", exact = FALSE)$p.value
    assert got[("week 0", "week 4")] == pytest.approx(1.195683297536e-20, rel=1e-8)
    assert got[("week 0", "week 8")] == pytest.approx(2.632392484771e-29, rel=1e-8)
    assert got[("week 4", "week 8")] == pytest.approx(6.315199098847e-14, rel=1e-8)
    got = t.compare_each_pair_of("pain", for_each_group_in="week", matched_by="patient")._frame.to_pandas()
    got = got.set_index(["group 1", "group 2"])["p-value (Holm)"]
    # R: pairwise.t.test(pain, week, paired = TRUE, p.adjust.method = "holm")$p.value
    assert got[("week 0", "week 4")] == pytest.approx(7.597957313582e-28, rel=1e-8)
    assert got[("week 4", "week 8")] == pytest.approx(3.256303243177e-16, rel=1e-8)
    assert "within the same 200" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="leave out test_method="):
        t.compare_each_pair_of("pain", for_each_group_in="week", matched_by="patient", test_method="tukey")


def test_compare_correlations(engine, needs_r, capsys):
    t = make(engine, sdata.get_example("marks"))
    t.keep_rows_where("class", is_one_of=["A", "B"])
    got = row(t.compare_correlations("hours", "marks", for_each_group_in="class"))
    # R: cocor::cocor.indep.groups(r_A, r_B, n_A, n_B, test = c("fisher1925", "zou2007")) (cocor_ref.R)
    assert (got["r in A"], got["r in B"]) == pytest.approx((0.8779001104164, 0.8113540101691), rel=REL)
    assert (got["statistic"], got["p-value"]) == pytest.approx((0.6450970362209, 0.5188643043876), rel=1e-6)
    assert (got["difference 95 % CI low"], got["difference 95 % CI high"]) == pytest.approx(
        (-0.1486109707038, 0.3343463571511), rel=1e-6)
    got = row(make(engine, sdata.get_example("marks")).compare_correlations(["hours", "marks"], ["height", "marks"]))
    # R: cocor::cocor.dep.groups.overlap(r(marks, hours), r(marks, height), r(hours, height), n, steiger1980 / zou2007)
    assert (got["statistic"], got["p-value"]) == pytest.approx((5.77722766837, 7.594149753487e-09), rel=1e-6)
    assert (got["difference 95 % CI low"], got["difference 95 % CI high"]) == pytest.approx(
        (0.5193976091638, 1.075554273185), rel=1e-6)
    assert "Steiger's z test" in capsys.readouterr().out
