"""S1 Part B4: intervals for summaries, interval_of (bootstrap), harmonic and winsorized averages,
percentile rules, z-scores.

Reference values: R 4.6.2 on sdata.get_example("marks"): m <- read.csv(".../marks.csv").
"""

import math

import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table


@pytest.fixture(params=["pandas", "polars"])
def marks(request):
    data = sdata.get_example("marks")
    if request.param == "polars":
        pl = pytest.importorskip("polars")
        return make_table(pl.from_pandas(data))
    return make_table(data)


def frame(result):
    return result._frame.to_pandas()


def test_average_interval(marks, capsys):
    got = frame(marks.find_average_of("marks", for_each_group_in="class", interval=95))
    # R: t.test(m$marks[m$class == "A"])$conf.int (and B, C)
    assert got["average of marks 95 % CI low"].tolist() == pytest.approx(
        [64.9994097456, 56.88642231031, 51.55951455139], rel=1e-10)
    assert got["average of marks 95 % CI high"].tolist() == pytest.approx(
        [78.66725692107, 71.66913324524, 65.66270767083], rel=1e-10)
    assert got["count"].tolist() == [18, 18, 18]
    assert "t interval, as R t.test()" in capsys.readouterr().out
    # R: t.test(m$marks, conf.level = 0.9)$conf.int
    got = frame(marks.find_average_of("marks", interval=90))
    assert got.iloc[0, 1:3].tolist() == pytest.approx([61.48389955903, 68.33091525578], rel=1e-10)


def test_median_and_percentile_interval(marks, capsys):
    got = frame(marks.find_median_of("marks", for_each_group_in="class", interval=95))
    # R: DescTools::MedianCI(x, method = "exact") per class: 61-81, 57-74, 48-71
    assert got["median of marks 95 % CI low"].tolist() == [61, 57, 48]
    assert got["median of marks 95 % CI high"].tolist() == [81, 74, 71]
    # R: DescTools::QuantileCI(m$marks, probs = 0.25, method = "exact"): 54.25, 47 to 59
    got = frame(marks.find_percentile_of("marks", 25, interval=95))
    assert got.iloc[0].tolist()[:3] == [54.25, 47, 59]
    got = frame(marks.find_percentile_of("marks", 90, for_each_group_in="class", interval=95))
    assert math.isnan(got["percentile 90 of marks 95 % CI high"][0])  # R QuantileCI: NA too
    assert "too few values for an upper end" in capsys.readouterr().out


def test_standard_deviation_interval(marks, needs_r):
    got = frame(marks.find_standard_deviation_of("marks", for_each_group_in="class", interval=95))
    # R: sqrt(DescTools::VarCI(x, method = "classic")) per class
    assert got["standard deviation of marks 95 % CI low"].tolist() == pytest.approx(
        [10.31210965379, 11.15325143633, 10.64056921688], rel=1e-10)
    assert got["standard deviation of marks 95 % CI high"].tolist() == pytest.approx(
        [20.60180273904, 22.28225782159, 21.25800785649], rel=1e-10)


def test_interval_of(marks, capsys):
    got = frame(marks.find_interval_of("marks", "average"))
    # R: set.seed(1); boot.ci(boot(m$marks, function(v, i) mean(v[i]), R = 20000), type = "bca")
    #    and t.test(m$marks)$conf.int 61.2 to 68.6: the bootstrap interval is near both
    assert got["average of marks"][0] == pytest.approx(64.9074074074, rel=1e-10)
    assert got["average of marks 95 % CI low"][0] == pytest.approx(60.9, abs=0.6)
    assert got["average of marks 95 % CI high"][0] == pytest.approx(68.6, abs=0.6)
    again = frame(marks.find_interval_of("marks", "average"))
    assert again.equals(got)
    assert "9999 times (seed 1)" in capsys.readouterr().out
    got = frame(marks.find_interval_of("marks", "median", for_each_group_in="class", method="percentile bootstrap"))
    assert got["count"].tolist() == [18, 18, 18]
    got = frame(marks.find_interval_of("marks", lambda v: v.max() - v.min()))
    assert got.columns[0] == "<lambda> of marks"


def test_interval_errors(marks):
    with pytest.raises(SimplydataError, match="jackknife"):
        marks.find_interval_of("marks", "average", method="jackknife")
    with pytest.raises(SimplydataError, match="one number"):
        marks.find_interval_of("marks", "count")
    with pytest.raises(SimplydataError, match="every= and across="):
        marks.find_average_of("marks", for_each_group_in="class", across="subject", interval=95)
    with pytest.raises(SimplydataError, match="leave out method="):
        marks.find_percentile_of("marks", 90, method=6, interval=95)


def test_harmonic_and_winsorized(marks, capsys):
    got = frame(marks.find_summary_of("marks", for_each_group_in="class",
                                 show=["harmonic mean", "winsorised average", "winsorized mean 10"]))
    # R: psych::harmonic.mean(x); WRS2::winmean(x, tr = 0.2) per class
    assert got["harmonic mean"].tolist() == pytest.approx([69.048959223, 60.19762942099, 55.10949376722], rel=1e-10)
    assert got["winsorised average 20 %"].tolist() == pytest.approx(
        [71.77777777778, 65.44444444444, 58.72222222222], rel=1e-10)
    assert "WRS2::winmean(x, tr = 0.1)" in capsys.readouterr().out


def test_percentile_rules(marks):
    # R: quantile(m$marks, 0.9, type = 1 ... 9)
    expected = [81, 81, 81, 81, 81.5, 83.5, 81, 82.16666666667, 82]
    for r_type, value in enumerate(expected, start=1):
        assert marks.find_percentile_of("marks", 90, method=r_type) == pytest.approx(value, rel=1e-10)
    assert marks.find_percentile_of("marks", 90, method="weibull") == pytest.approx(83.5)
    with pytest.raises(SimplydataError, match="method="):
        marks.find_percentile_of("marks", 90, method=10)


def test_z_scores(marks):
    marks.add_z_score_column("z", from_column="marks")
    marks.add_z_score_column("z in class", from_column="marks", for_each_group_in="class")
    got = frame(marks)
    # R: scale(m$marks)[1:5]; ave(m$marks, m$class, FUN = function(v) scale(v)[, 1])[1:5]
    assert got["z"][:5].tolist() == pytest.approx(
        [-0.26001960621526, 0.07270690410759, 0.80470522681786, 0.53852401855958, 2.20215657017383], rel=1e-10)
    assert got["z in class"][:5].tolist() == pytest.approx(
        [-0.78831579768628, -0.42447773721569, 0.37596599581961, 0.08489554744314, 1.90408584979610], rel=1e-10)
