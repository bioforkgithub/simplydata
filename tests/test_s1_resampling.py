"""S1 Part B3: shuffling (permutation tests) and the bootstrap, through SciPy.

Reference values: R 4.6.2 (perm 1.0.0.4, coin 1.4.6, boot 1.3.32). Data (as in the design checks):
a <- c(12.1, 14.3, 11.8, 15.2, 13.9, 12.7, 14.8, 13.1, 12.4, 15.6)
b <- c(10.2, 11.9, 12.8, 10.7, 11.1, 13.4, 10.9, 12.2, 11.5, 10.4, 12.9, 11.0)
x <- c(1.2, 2.3, 2.9, 3.8, 4.1, 5.5, 6.0, 6.8, 7.7, 8.1, 9.4, 10.2)
y <- c(2.0, 2.1, 3.5, 3.1, 4.9, 4.4, 6.9, 6.1, 7.0, 9.2, 8.8, 9.9)
Exact p-values (every arrangement counted) must equal R; Monte Carlo ones are repeatable with
the seed and near the exact value; bootstrap intervals are near R's (different random draws).
"""

import numpy as np
import pandas as pd
import pytest

from simplydata import SimplydataError
from simplydata.table import table as make_table
from simplydata.table.resampling import average, bootstrap_interval, correlation, resample_p

A = [12.1, 14.3, 11.8, 15.2, 13.9, 12.7, 14.8, 13.1, 12.4, 15.6]
B = [10.2, 11.9, 12.8, 10.7, 11.1, 13.4, 10.9, 12.2, 11.5, 10.4, 12.9, 11.0]
X = [1.2, 2.3, 2.9, 3.8, 4.1, 5.5, 6.0, 6.8, 7.7, 8.1, 9.4, 10.2]
Y = [2.0, 2.1, 3.5, 3.1, 4.9, 4.4, 6.9, 6.1, 7.0, 9.2, 8.8, 9.9]
CHANGES = [1.2, -0.5, 2.0, 0.7, 1.1, -0.2, 0.9, 1.5]


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


def groups(engine, a=A, b=B):
    return make(pd.DataFrame({"v": a + b, "g": ["a"] * len(a) + ["b"] * len(b)}), engine)


def test_shuffling_exact_equals_r(engine, capsys):
    t = groups(engine, A[:6], B[:7])  # 1716 arrangements: all counted
    got = row(t.compare_averages_of("v", for_each_group_in="g", p_value_by="shuffling"))
    # R: perm::permTS(a[1:6], b[1:7], method = "exact.network")$p.values["p.twosided"]
    assert got["p-value"] == pytest.approx(0.033799533799534, rel=1e-9)
    assert got["p-value by"] == "shuffling, all 1,716 arrangements counted"
    assert "so the p-value is exact" in capsys.readouterr().out
    # R: perm::permTS(b[1:7], a[1:6], method = "exact.network", alternative = "less")$p.value
    got = row(t.compare_averages_of("v", for_each_group_in="g", p_value_by="shuffling", sides=1, higher="a"))
    assert got["p-value"] == pytest.approx(0.01689976689977, rel=1e-9)


def test_shuffling_monte_carlo_is_repeatable(engine, capsys):
    t = groups(engine)  # 646,646 arrangements: shuffled 9999 times
    first = row(t.compare_averages_of("v", for_each_group_in="g", p_value_by="shuffling"))
    second = row(t.compare_averages_of("v", for_each_group_in="g", p_value_by="shuffling"))
    assert first["p-value"] == second["p-value"]
    assert first["p-value by"] == "shuffled 9999 times, seed 1"
    # R: perm::permTS(a, b, method = "exact.network") p.twosided 0.001339218057 (exact); Monte Carlo SE ~ 0.0004
    assert first["p-value"] == pytest.approx(0.001339218057, abs=0.002)
    assert row(t.compare_averages_of("v", for_each_group_in="g", p_value_by="shuffling", with_seed=2))["p-value"] != first["p-value"]
    assert "the group labels were shuffled 9999 times (seed 1)" in capsys.readouterr().out


def test_shuffling_paired_equals_r(engine, capsys):
    before = X[:8]
    data = pd.DataFrame({"before": before, "after": [v + c for v, c in zip(before, CHANGES)]})
    t = make(data, engine)
    # R: coin::pvalue(coin::symmetry_test(y ~ g | id, distribution = "exact")) (the 2^8 sign changes)
    assert row(t.compare_before_and_after("before", "after", p_value_by="shuffling"))["p-value"] == \
        pytest.approx(0.0390625, rel=1e-12)
    got = row(t.compare_before_and_after("before", "after", p_value_by="shuffling", sides=1, higher="after"))
    assert got["p-value"] == pytest.approx(0.01953125, rel=1e-12)  # R: the same, alternative = "greater"
    assert got["p-value by"] == "shuffling, all 256 arrangements counted"


def test_shuffling_correlation_equals_r():
    # R: every one of the 5040 orders of y[1:7] counted, two-sided = twice the smaller one-sided share
    found = resample_p((X[:7], [2.0, 2.1, 3.5, 3.1, 4.9, 4.4, 6.9]), correlation("pearson"), "pairings")
    assert found["exact"] and found["arrangements"] == 5040
    assert found["p"] == pytest.approx(0.006349206349206, rel=1e-9)
    found = resample_p((X[:7], [2.0, 2.1, 3.5, 3.1, 4.9, 4.4, 6.9]), correlation("pearson"), "pairings", "greater")
    assert found["p"] == pytest.approx(0.003174603174603, rel=1e-9)


def test_correlation_with_shuffling_and_bootstrap(engine, capsys):
    t = make(pd.DataFrame({"x": X, "y": Y}), engine)
    r = t.find_correlation_between("x", "y", p_value_by="shuffling", interval_by="bootstrap")
    assert r == pytest.approx(0.961687213010519, rel=1e-12)  # R: cor(x, y)
    out = capsys.readouterr().out
    assert "shuffled against the other 9999 times (seed 1)" in out
    assert "95 % bootstrap CI" in out and "often too narrow" in out
    t.find_correlation_between("x", "y", method="spearman", p_value_by="shuffling")
    assert "SciPy permutation_test" in capsys.readouterr().out


def test_bootstrap_near_r():
    # R: set.seed(1); boot.ci(boot(a, function(v, i) mean(v[i]), R = 20000), type = "bca"): 12.83 to 14.40
    low, high, words, note = bootstrap_interval((A,), average)
    assert (low, high) == pytest.approx((12.83, 14.40), abs=0.05)
    assert bootstrap_interval((A,), average)[:2] == (low, high)  # the same seed, the same interval
    assert "9999 times (seed 1)" in words and "too narrow" in note
    # R: set.seed(1); boot.ci(boot(data.frame(X, Y), function(d, i) cor(d$X[i], d$Y[i]), R = 20000), type = "bca")
    low, high, _, _ = bootstrap_interval((X, Y), correlation("pearson"), paired=True)
    assert (low, high) == pytest.approx((0.9039929710036, 0.9859878367157), abs=0.01)


def test_shuffling_errors(engine):
    t = groups(engine)
    with pytest.raises(SimplydataError, match='Did you mean p_value_by="shuffling"'):
        t.compare_averages_of("v", for_each_group_in="g", p_value_by="shufling")
    with pytest.raises(SimplydataError, match="2 groups"):
        t.compare_averages_of("v", for_each_group_in="g", p_value_by="shuffling", based_on="ranks")
    with pytest.raises(SimplydataError, match="seed="):
        t.compare_averages_of("v", for_each_group_in="g", p_value_by="shuffling", with_seed=1.5)
    with pytest.raises(SimplydataError, match="shuffles="):
        t.compare_averages_of("v", for_each_group_in="g", p_value_by="shuffling", shuffles=10)
    c = make(pd.DataFrame({"x": X, "y": Y, "z": A + [1.0, 2.0]}), engine)
    with pytest.raises(SimplydataError, match="two columns"):
        c.find_correlation_between("x", "y", "z", p_value_by="shuffling")
