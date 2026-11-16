"""S1 Part B5: equivalence (same_within=, TOST) and non-inferiority (same_within= with sides=1).

Reference values: R 4.6.2, TOSTER 0.8.6.
a <- c(12.1, 14.3, 11.8, 15.2, 13.9, 12.7, 14.8, 13.1, 12.4, 15.6)
b <- c(10.2, 11.9, 12.8, 10.7, 11.1, 13.4, 10.9, 12.2, 11.5, 10.4, 12.9, 11.0)
rm3: 8 rows x 3 columns (s1_design_checks/data.R); the first two columns are w1, w2.
"""

import numpy as np
import pandas as pd
import pytest

from simplydata import SimplydataError
from simplydata.table import table as make_table

A = [12.1, 14.3, 11.8, 15.2, 13.9, 12.7, 14.8, 13.1, 12.4, 15.6]
B = [10.2, 11.9, 12.8, 10.7, 11.1, 13.4, 10.9, 12.2, 11.5, 10.4, 12.9, 11.0]
RM = np.array([5.1, 6.0, 6.8, 4.2, 4.9, 5.5, 6.3, 6.1, 7.4, 5.0, 5.9, 6.6, 4.8, 5.2, 5.0, 5.5, 6.6, 7.1, 6.0, 6.4,
               7.9, 4.4, 5.1, 5.8]).reshape(-1, 3)
REL = 1e-9


@pytest.fixture(params=["pandas", "polars"])
def engine(request):
    return request.param


def make(data, engine):
    if engine == "polars":
        pl = pytest.importorskip("polars")
        return make_table(pl.from_pandas(data))
    return make_table(data)


def row(result):
    return result._frame.to_pandas().iloc[0].to_dict()


@pytest.fixture
def groups(engine):
    return make(pd.DataFrame({"v": A + B, "g": ["a"] * 10 + ["b"] * 12}), engine)


def test_tost_two_groups(groups, capsys):
    got = row(groups.compare_averages_of("v", for_each_group_in="g", same_within=2.5))
    # R: TOSTER::t_TOST(x = a, y = b, eqb = 2.5)$TOST$p.value (Welch): lower 7.622562779918e-08, upper 0.1805239677
    assert got["p-value against the low margin"] == pytest.approx(7.622562779918e-08, rel=1e-8)
    assert got["p-value against the high margin"] == pytest.approx(0.1805239676677, rel=REL)
    assert got["p-value"] == pytest.approx(0.1805239676677, rel=REL)
    # R: t_TOST(...)$effsize lower.ci / upper.ci of the raw difference (90 %)
    assert (got["difference 90 % CI low"], got["difference 90 % CI high"]) == pytest.approx(
        (1.092067956785, 2.921265376548), rel=REL)
    assert got["answer"] == "different"
    out = capsys.readouterr().out
    assert "TOST, Welch" in out and "TOSTER::t_TOST()" in out and "The 90 % interval goes with" in out


def test_tost_answers(groups, engine, capsys):
    # R: t_TOST(x = a, y = b, low_eqbound = -3, high_eqbound = 5)$TOST$p.value: 1.731657060930e-08, 1.368738675564e-05
    got = row(groups.compare_averages_of("v", for_each_group_in="g", same_within=[-3, 5]))
    assert got["p-value"] == pytest.approx(1.368738675564e-05, rel=1e-8)
    assert got["answer"] == "the same within the margin"
    assert "a and b are the same within -3 to 5" in capsys.readouterr().out
    two = make(pd.DataFrame({"v": A[:4] + B[:4], "g": ["a"] * 4 + ["b"] * 4}), engine)
    got = row(two.compare_averages_of("v", for_each_group_in="g", same_within=1))
    assert got["answer"] == "the data cannot tell"
    assert "the data cannot tell whether" in capsys.readouterr().out


def test_tost_paired(engine):
    t = make(pd.DataFrame({"w1": RM[:, 0], "w2": RM[:, 1]}), engine)
    got = row(t.compare_before_and_after("w1", "w2", same_within=1))
    # R: t_TOST(x = rm3[, 2], y = rm3[, 1], paired = TRUE, eqb = 1)$TOST$p.value and $effsize (90 %)
    assert got["p-value against the low margin"] == pytest.approx(5.160764132815e-06, rel=1e-8)
    assert got["p-value against the high margin"] == pytest.approx(0.01571751551749, rel=REL)
    assert (got["difference 90 % CI low"], got["difference 90 % CI high"]) == pytest.approx(
        (0.3387970822876, 0.8862029177124), rel=REL)
    assert got["answer"] == "the same within the margin"


def test_tost_one_sample(engine):
    t = make(pd.DataFrame({"x": A}), engine)
    got = row(t.compare_average_to("x", 13, same_within=1))
    # R: t_TOST(x = a - 13, eqb = 1)$TOST$p.value: lower 0.002438666286013, upper 0.182128148412461
    #    (TOSTER's mu= moves only its plain t-test, not the margin, so the values are shifted first)
    assert got["p-value against the low margin"] == pytest.approx(0.002438666286013, rel=1e-8)
    assert got["p-value against the high margin"] == pytest.approx(0.182128148412461, rel=REL)
    # R: t_TOST(x = a, mu = 13, eqb = 1)$effsize: 90 % interval of the average 12.80346850877 to 14.37653149123
    assert (got["difference 90 % CI low"], got["difference 90 % CI high"]) == pytest.approx(
        (12.80346850877 - 13, 14.37653149123 - 13), rel=REL)
    assert got["answer"] == "the data cannot tell"


def test_non_inferiority(groups, engine, capsys):
    got = row(groups.compare_averages_of("v", for_each_group_in="g", same_within=1, not_lower="b"))
    # R: t.test(a, b, mu = 1, alternative = "less") (Welch): is b lower than a by no more than 1?
    assert got["p-value"] == pytest.approx(0.9637320342953, rel=REL)
    assert got["difference one-sided 95 % CI high"] == pytest.approx(2.9212653765479, rel=REL)
    assert got["answer"] == "the data cannot tell"
    assert "b is not lower than a by more than 1" in capsys.readouterr().out
    t = make(pd.DataFrame({"x": A}), engine)
    got = row(t.compare_average_to("x", 13, same_within=1, not_lower="average"))
    # R: t.test(a, mu = 12, alternative = "greater"): p 0.002438666286013, interval from 12.8034685 (minus 13)
    assert got["p-value"] == pytest.approx(0.002438666286013, rel=1e-8)
    assert got["difference one-sided 95 % CI low"] == pytest.approx(12.803468508771104 - 13, rel=1e-8)
    assert got["answer"] == "not worse than the margin"


def test_same_within_errors(groups):
    with pytest.raises(SimplydataError, match="above 0"):
        groups.compare_averages_of("v", for_each_group_in="g", same_within=-1)
    with pytest.raises(SimplydataError, match="low below 0"):
        groups.compare_averages_of("v", for_each_group_in="g", same_within=[1, 5])
    with pytest.raises(SimplydataError, match="2 groups"):
        groups.compare_averages_of("v", for_each_group_in="g", same_within=1, based_on="ranks")
