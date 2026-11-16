"""The S1 renames Manish approved on 2026-11-15 (design_evidence_private/retro_name_review_2026-11-15.md).

check_random_order (was compare_to_random_order), interval_by= on the percent words (was method=),
names= on sdata.compare_averages (was groups=), not_lower= / not_higher= for non-inferiority (was
sides=1, higher= with same_within=) and "reverse percentile bootstrap" (was "basic bootstrap"). The
old spellings still work, each with one note. The conftest resets the notes before each test.

Reference values: R 4.6.2 (the R call is next to each number).
"""

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table

NOTE_END = "The old name will stop working in a later version."
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


def notes(out):
    return [line for line in out.splitlines() if line.endswith(NOTE_END)]


# ---------------------------------------------------------------------------- check_random_order
def test_check_random_order_old_name(engine, capsys):
    t = make(sdata.get_example("marks"), engine)
    new = row(t.check_if_random_order("marks"))
    capsys.readouterr()
    old = row(t.compare_to_random_order("marks"))
    assert old == new
    assert notes(capsys.readouterr().out) == [
        f'Note: "compare_to_random_order" is now called "check_if_random_order". {NOTE_END}']


# ---------------------------------------------------------------------------- interval_by= on percents
def test_percent_interval_by_and_old_method(engine, capsys):
    school = make(sdata.get_example("school"), engine)
    got = row(school.compare_percent_to("passed", value="yes", percent=50, interval_by="wilson"))
    # R: DescTools::BinomCI(78, 180, method = "wilson"): 0.363081784442 to 0.506370948614
    assert got["percent 95 % CI low"] == pytest.approx(36.3081784442, rel=1e-9)
    capsys.readouterr()
    old = row(school.compare_percent_to("passed", value="yes", percent=50, method="wilson"))
    assert old == got
    assert notes(capsys.readouterr().out) == [f'Note: "method=" is now called "interval_by=". {NOTE_END}']
    with pytest.raises(SimplydataError, match="only once"):
        school.compare_percent_to("passed", value="yes", percent=50, method="wilson", interval_by="wilson")
    marks = make(sdata.get_example("marks"), engine)
    marks.find_percent_of_rows_where("marks", is_above=60, method="wilson")
    # R: DescTools::BinomCI(33, 54, method = "wilson"): 0.477882985382 to 0.729580661709
    assert "95 % CI 47.8 % to 73.0 %, Wilson score interval" in capsys.readouterr().out


# ---------------------------------------------------------------------------- names= on sdata.compare_averages
SUMMARY = dict(averages=[71.8333333333333333, 64.2777777777777778, 58.6111111111111111],
               standard_deviations=[13.7423775663628, 14.8633206469347, 14.1800974396755], counts=[18, 18, 18])


def test_summary_names_and_old_groups(capsys):
    got = row(sdata.compare_averages(**SUMMARY, names=["A", "B", "C"]))
    # R: oneway.test(marks ~ class, m) on the rows (these are their averages and standard deviations)
    assert got["p-value"] == pytest.approx(0.0276731022463, rel=1e-9)
    assert got["what it compares"] == "the averages of A, B and C, from summary numbers"
    capsys.readouterr()
    old = row(sdata.compare_averages(**SUMMARY, groups=["A", "B", "C"]))
    assert old == got
    assert notes(capsys.readouterr().out) == [f'Note: "groups=" is now called "names=". {NOTE_END}']
    with pytest.raises(SimplydataError, match="needs a list of 3 names"):
        sdata.compare_averages(**SUMMARY, names=3)
    with pytest.raises(SimplydataError, match="3 different names"):
        sdata.compare_averages(**SUMMARY, names=["A", "A", "C"])


# ---------------------------------------------------------------------------- not_lower= / not_higher=
@pytest.fixture
def groups(engine):
    return make(pd.DataFrame({"v": A + B, "g": ["a"] * 10 + ["b"] * 12}), engine)


def test_not_lower_two_groups(groups, capsys):
    got = row(groups.compare_averages_of("v", for_each_group_in="g", same_within=1, not_lower="b"))
    # R: t.test(a, b, mu = 1, alternative = "less") (Welch): is b lower than a by no more than 1?
    assert got["p-value"] == pytest.approx(0.9637320342953, rel=REL)
    assert got["difference one-sided 95 % CI high"] == pytest.approx(2.9212653765479, rel=REL)
    assert got["sides"] == "one-sided: b not lower by more than 1"
    out = capsys.readouterr().out
    assert "b is not lower than a by more than 1" in out and not notes(out) and "Note:" not in out
    # not_higher="a" is the same test, said from a's side
    mirror = row(groups.compare_averages_of("v", for_each_group_in="g", same_within=1, not_higher="a"))
    assert mirror["p-value"] == pytest.approx(0.9637320342953, rel=REL)
    assert mirror["sides"] == "one-sided: a not higher by more than 1"
    assert "a is not higher than b by more than 1" in capsys.readouterr().out


def test_old_sides_higher_with_same_within(groups, capsys):
    new = row(groups.compare_averages_of("v", for_each_group_in="g", same_within=1, not_lower="b"))
    capsys.readouterr()
    old = row(groups.compare_averages_of("v", for_each_group_in="g", same_within=1, sides=1, higher="b"))
    assert old == new
    assert ('Note: sides=1, higher="b" with same_within= is a non-inferiority test; it is written not_lower="b".'
            in capsys.readouterr().out)
    old = row(groups.compare_averages_of("v", for_each_group_in="g", same_within=1, sides=1, lower="a"))
    assert old["p-value"] == pytest.approx(0.9637320342953, rel=REL)
    assert 'it is written not_higher="a"' in capsys.readouterr().out


def test_not_lower_paired_and_one_sample(engine):
    t = make(pd.DataFrame({"w1": RM[:, 0], "w2": RM[:, 1]}), engine)
    got = row(t.compare_before_and_after("w1", "w2", same_within=1, not_lower="after"))
    # R: t.test(w2, w1, paired = TRUE, mu = -1, alternative = "greater"): p and the interval's low end
    assert got["p-value"] == pytest.approx(5.16076413281542e-06, rel=1e-8)
    assert got["difference one-sided 95 % CI low"] == pytest.approx(0.338797082287649, rel=REL)
    got = row(t.compare_before_and_after("w1", "w2", same_within=1, not_higher="after"))
    # R: t.test(w2, w1, paired = TRUE, mu = 1, alternative = "less")
    assert got["p-value"] == pytest.approx(0.0157175155174882, rel=REL)
    assert got["difference one-sided 95 % CI high"] == pytest.approx(0.8862029177123512, rel=REL)
    assert got["answer"] == "not worse than the margin"
    x = make(pd.DataFrame({"x": A}), engine)
    got = row(x.compare_average_to("x", 13, same_within=1, not_lower="average"))
    # R: t.test(a, mu = 12, alternative = "greater")
    assert got["p-value"] == pytest.approx(0.002438666286013, rel=1e-8)
    got = row(x.compare_average_to("x", 13, same_within=1, not_higher="average"))
    # R: t.test(a, mu = 14, alternative = "less"): p and the interval's high end (minus 13)
    assert got["p-value"] == pytest.approx(0.182128148412461, rel=REL)
    assert got["difference one-sided 95 % CI high"] == pytest.approx(14.376531491228896 - 13, rel=1e-8)
    assert got["answer"] == "the data cannot tell"


def test_not_lower_errors(groups):
    with pytest.raises(SimplydataError, match="needs same_within="):
        groups.compare_averages_of("v", for_each_group_in="g", not_lower="b")
    with pytest.raises(SimplydataError, match="both not_lower= and not_higher="):
        groups.compare_averages_of("v", for_each_group_in="g", same_within=1, not_lower="b", not_higher="a")
    with pytest.raises(SimplydataError, match="leave out higher= and lower="):
        groups.compare_averages_of("v", for_each_group_in="g", same_within=1, not_lower="b", higher="b")
    with pytest.raises(SimplydataError, match='does not know not_lower="B "'):
        groups.compare_averages_of("v", for_each_group_in="g", same_within=1, not_lower="B ")


# ---------------------------------------------------------------------------- reverse percentile bootstrap
def test_reverse_percentile_bootstrap(engine, capsys):
    t = make(sdata.get_example("marks"), engine)
    new = t.find_interval_of("marks", "median", method="reverse percentile bootstrap")._frame.to_pandas()
    out = capsys.readouterr().out
    assert "bootstrap interval (reverse percentile)" in out and 'boot.ci(type = "basic")' in out
    # the reverse percentile interval is 2 x median minus the percentile interval, reversed
    # (R: boot.ci(type = "basic") is 2 * t0 - the percentile ends)
    perc = t.find_interval_of("marks", "median", method="percentile bootstrap")._frame.to_pandas()
    median = new["median of marks"][0]
    assert new["median of marks 95 % CI low"][0] == pytest.approx(2 * median - perc["median of marks 95 % CI high"][0])
    assert new["median of marks 95 % CI high"][0] == pytest.approx(2 * median - perc["median of marks 95 % CI low"][0])
    capsys.readouterr()
    old = t.find_interval_of("marks", "median", method="basic bootstrap")._frame.to_pandas()
    assert old.equals(new)
    assert notes(capsys.readouterr().out) == [
        f'Note: method="basic bootstrap" is now called method="reverse percentile bootstrap". {NOTE_END}']
