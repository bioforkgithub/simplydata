"""S1 Part B4, rest: multinomial intervals on count_each, and outlier tests (Grubbs, Dixon, Rosner) on the outlier
words.

Reference values: R 4.6.2 (DescTools 0.99.60, outliers, EnvStats).
DescTools::MultinomCI(sort(table(fruit$fruit), decreasing = TRUE)) (Sison-Glaz, its default);
x <- c(12.1, 14.3, 11.8, 15.2, 13.9, 12.7, 14.8, 13.1, 12.4, 25.6, 3.0, 13.3):
outliers::grubbs.test(x)$p.value = 0.02053415795634 (25.6 tested, outliers::outlier(x));
EnvStats::rosnerTest(x, k = 3)$all.stats: 25.6 (obs 10) and 3.0 (obs 11) are outliers, 15.2 is not;
outliers::dixon.test(x): 25.6, p below 0.05.
"""

import pandas as pd
import pytest

import simplydata as sdata
from simplydata.table import table as make_table
from conftest import example_frame

X = [12.1, 14.3, 11.8, 15.2, 13.9, 12.7, 14.8, 13.1, 12.4, 25.6, 3.0, 13.3]


@pytest.fixture(params=["pandas", "polars"])
def engine(request):
    return request.param


def make(engine, data):
    if engine == "polars":
        pl = pytest.importorskip("polars")
        return make_table(data, fast=True)
    return make_table(data)


def test_count_each_interval(engine, capsys):
    got = make(engine, example_frame("fruit")).count_each("fruit", interval=95)._frame.to_pandas().set_index("fruit")
    # R: DescTools::MultinomCI(table): apple 0.1212121212121 to 0.447361627938; pear 0 to 0.265543446120
    assert got.loc["apple", "percent 95 % CI low"] == pytest.approx(12.12121212121, rel=1e-9)
    assert got.loc["apple", "percent 95 % CI high"] == pytest.approx(44.7361627938, rel=1e-9)
    assert got.loc["pear", "percent 95 % CI high"] == pytest.approx(26.5543446120, rel=1e-9)
    assert "Sison and Glaz" in capsys.readouterr().out


@pytest.mark.parametrize("rule, flagged", [("grubbs", [10]), ("dixon", [10]), ("rosner", [10, 11])])
def test_outlier_tests(engine, needs_r, capsys, rule, flagged):
    t = make(engine, pd.DataFrame({"v": X}))
    t.show_rows_with_outliers("v", test_method=rule)
    out = capsys.readouterr().out
    assert f"Found {len(flagged)} row" in out
    assert f"remove_rows_by_position({', '.join(map(str, flagged))})" in out or \
        f"remove_rows_by_position([{', '.join(map(str, flagged))}])" in out
    t.remove_rows_with_outliers("v", test_method=rule)
    assert len(t._frame) == len(X) - len(flagged)


def test_grubbs_by_group(engine, needs_r, capsys):
    t = make(engine, pd.DataFrame({"v": X + X[:9], "g": ["a"] * 12 + ["b"] * 9}))
    t.show_rows_with_outliers("v", for_each_group_in="g", test_method="grubbs")
    out = capsys.readouterr().out
    # R: grubbs.test(x)$p.value = 0.02053415795634 in group a; group b (no outlier) is not flagged
    assert "a: the value farthest from the average, 25.6, is an outlier (p = 0.0205" in out
    assert "Found 1 row" in out
