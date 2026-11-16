"""S1 B4: weights= on average_of and standard_deviation_of, and fit_distribution("kernel density").

Reference values: R 4.6.2 with Hmisc 5 (the R call is next to each number).
x <- c(12.1, 14.3, 11.8, 15.2, 13.9, 12.7, 14.8, 13.1, 12.4, 15.6)
w <- c(1, 2, 3, 1, 2, 4, 1, 2, 3, 1)
wa <- c(0.5, 1.2, 2.0, 0.7, 1.1, 3.3, 0.9, 1.4, 2.2, 0.6)
"""

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table

X = [12.1, 14.3, 11.8, 15.2, 13.9, 12.7, 14.8, 13.1, 12.4, 15.6]
W = [1, 2, 3, 1, 2, 4, 1, 2, 3, 1]
WA = [0.5, 1.2, 2.0, 0.7, 1.1, 3.3, 0.9, 1.4, 2.2, 0.6]
G = list("aabbaabbab")


@pytest.fixture(params=["pandas", "polars"])
def engine(request):
    return request.param


def make(data, engine):
    if engine == "polars":
        pl = pytest.importorskip("polars")
        return make_table(pl.from_pandas(data))
    return make_table(data)


@pytest.fixture
def weighted(engine):
    return make(pd.DataFrame({"x": X + [None], "w": W + [1], "wa": WA + [1.0], "g": G + ["a"]}), engine)


# ---------------------------------------------------------------------------- weights=
def test_weighted_average(weighted, capsys):
    # R: weighted.mean(x, w)
    assert weighted.find_average_of("x", weights="w") == pytest.approx(13.185, rel=1e-12)
    out = capsys.readouterr().out
    assert '1 row with an empty cell in "x" or "w" was skipped' in out
    # 13.185 sits on a rounding edge, so the last printed figure can be 8 or 9 depending on the platform's floats
    assert ('weighted by "w", is 13.19' in out or 'weighted by "w", is 13.18' in out) and "R weighted.mean(x, w)" in out
    got = weighted.find_average_of("x", weights="w", for_each_group_in="g")._frame.to_pandas()
    # R: sapply(split(data.frame(x, w), g), function(d) weighted.mean(d$x, d$w))
    assert dict(zip(got["g"], got["weighted average of x"])) == pytest.approx(
        {"a": 13.0416666666667, "b": 13.4}, rel=1e-12)


def test_weighted_standard_deviation(weighted, capsys):
    # R: sqrt(Hmisc::wtd.var(x, w)) (frequency weights, normwt = FALSE)
    assert weighted.find_standard_deviation_of("x", weights="w") == pytest.approx(1.16405597622686, rel=1e-12)
    assert "frequency weights" in capsys.readouterr().out
    # R: sqrt(Hmisc::wtd.var(x, wa, normwt = TRUE)) (analytic weights): wtd.var 1.44051748921897
    got = weighted.find_standard_deviation_of("x", weights="wa", weight_kind="analytic")
    assert got == pytest.approx(np.sqrt(1.44051748921897), rel=1e-12)
    assert "normwt = TRUE" in capsys.readouterr().out
    # R: sqrt(Hmisc::wtd.var(x, wa)): non-whole frequency weights 1.34130165634934
    assert weighted.find_standard_deviation_of("x", weights="wa") == pytest.approx(np.sqrt(1.34130165634934), rel=1e-12)


def test_weights_errors(weighted, engine):
    with pytest.raises(SimplydataError, match="name of a column of weights"):
        weighted.find_average_of("x", weights=W + [1])
    with pytest.raises(SimplydataError, match="interval= do not go together"):
        weighted.find_average_of("x", weights="w", interval=95)
    with pytest.raises(SimplydataError, match="goes with weights="):
        weighted.find_standard_deviation_of("x", weight_kind="analytic")
    with pytest.raises(SimplydataError, match='Did you mean weight_kind="analytic"'):
        weighted.find_standard_deviation_of("x", weights="w", weight_kind="analytc")
    negative = make(pd.DataFrame({"x": [1.0, 2.0, 3.0], "w": [1.0, -1.0, 2.0]}), engine)
    with pytest.raises(SimplydataError, match="cannot be below 0"):
        negative.find_average_of("x", weights="w")


# ---------------------------------------------------------------------------- kernel density
def test_kernel_density_matches_r(engine, capsys):
    marks = make(sdata.get_example("marks"), engine)
    k = marks.fit_distribution_to("marks", "kernel density")
    out = capsys.readouterr().out
    assert "bandwidth 6.09041" in out and "R: density(x, bw = 6.09041)" in out
    # R: bw.nrd0(x) (the standard deviation is the smaller here, so R's 1.34 and statsmodels' 1.349 agree)
    assert k.show_parameters()["bandwidth"] == pytest.approx(6.09040757171597, rel=1e-12)
    # R: d <- density(x, n = 2^14, from = 20, to = 110); approx(d$x, d$y, xout = c(40, 60, 64.5, 80, 100))$y
    want = [0.00817033374534132, 0.01915915784930166, 0.02175859122121886, 0.01852627961902715,
            0.00192648056656740]
    assert list(k.find_density_at([40, 60, 64.5, 80, 100])) == pytest.approx(want, rel=1e-6)
    # R: mean(pnorm(60, x, bw.nrd0(x))) (the chance below 60 under the kernel density)
    assert k.find_chance_that_value(is_below=60) == pytest.approx(0.366843907855645, rel=1e-9)
    # R: uniroot(function(q) mean(pnorm(q, x, bw)) - 0.9, c(0, 150), tol = 1e-12)$root
    assert k.find_percentile(90) == pytest.approx(84.6414641426136, rel=1e-8)
    # R: c(mean(x), mean(x^2) - mean(x)^2 + bw^2): the average and variance of the kernel density
    assert k.find_average() == pytest.approx(64.9074074074074, rel=1e-7)
    assert k.find_variance() == pytest.approx(258.7326391495606, rel=1e-6)
    a = k.make_random_numbers(how_many=5, with_seed=1)
    assert list(a._values) == list(k.make_random_numbers(how_many=5, with_seed=1)._values)
    row = k.turn_into_table()._frame.to_pandas().iloc[0].to_dict()
    assert row["distribution"] == "kernel density" and row["rows"] == 54


def test_kernel_density_bandwidth_when_the_iqr_is_smaller(capsys):
    s = [31.2, 35.0, 36.1, 40.2, 41.0, 41.5, 42.0, 43.3, 60.1, 88.8, 95.5]
    k = sdata.numbers(s).fit_distribution("kernel density")
    # statsmodels bw_silverman divides the IQR by 1.349; R bw.nrd0 by 1.34 (5.63376165129813), as printed
    assert k.show_parameters()["bandwidth"] == pytest.approx(5.596175398620828, rel=1e-12)
    assert "divides the IQR by 1.34" in capsys.readouterr().out
    # R: d <- density(s, bw = 5.596175398620828, n = 2^14, from = 0, to = 130); approx(..., xout = 40)$y
    #    and the exact mean(dnorm(40, s, 5.596175398620828)) = 0.0419570209361939
    assert k.find_density_at(40) == pytest.approx(0.0419570209361939, rel=1e-12)
    assert k.find_density_at(40) == pytest.approx(0.04195700428026317, rel=1e-5)


def test_kernel_density_errors(engine):
    marks = make(sdata.get_example("marks"), engine)
    with pytest.raises(SimplydataError, match="one group at a time"):
        marks.fit_distribution_to("marks", "kernel density", for_each_group_in="class")
    with pytest.raises(SimplydataError, match="a kernel density has none"):
        marks.fit_distribution_to("marks", "kernel density", fixed={"bandwidth": 5})
    same = make(pd.DataFrame({"x": [3.0, 3.0, 3.0]}), engine)
    with pytest.raises(SimplydataError, match="no spread"):
        same.fit_distribution_to("x", "kernel density")
