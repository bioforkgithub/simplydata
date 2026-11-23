"""S1 Part B6: power for two percents, for equivalence (same_within=) and for an interval width.

Reference values: R 4.6.2 (stats, TOSTER 0.8.6, presize).
"""

import pytest

import simplydata as sdata
from simplydata import SimplydataError


def row(result):
    return result._frame.to_pandas().iloc[0].to_dict()


def test_two_percents_power(capsys):
    got = row(sdata.find_chance_of_finding(for_test="compare_counts", percents=[30, 15], values_per_group=121))
    # R: power.prop.test(p1 = 0.3, p2 = 0.15, n = 121)$power 0.8017324227189 (strict = FALSE, the default).
    #    statsmodels power_proportions_2indep(alternative="two-sided") gives 0.8017330967, R's strict = TRUE (it also
    #    counts the far tail); simplydata asks it for one side at half the level, which is R's default exactly
    assert got["power"] == pytest.approx(0.8017324227189, rel=1e-12)
    assert "power_proportions_2indep" in capsys.readouterr().out


def test_two_percents_number_needed(needs_r):
    got = row(sdata.find_how_many_needed(for_test="compare_counts", percents=[30, 15]))
    # R: power.prop.test(p1 = 0.3, p2 = 0.15, power = 0.8)$n
    assert got["values per group (exact)"] == pytest.approx(120.4719381847, rel=1e-9)
    assert got["values per group"] == 121


def test_equivalence_power(needs_r):
    got = row(sdata.find_how_many_needed(same_within=5, spread=10))
    # R: TOSTER::power_t_TOST(delta = 0, sd = 10, eqb = 5, alpha = 0.05, power = 0.8, type = "two.sample")$n
    assert got["values per group (exact)"] == pytest.approx(69.19782200194, rel=1e-6)
    assert got["values per group"] == 70
    # R: TOSTER::power_t_TOST(n = 40, delta = 1, sd = 10, eqb = 5, alpha = 0.05, power = NULL, type = "two.sample")
    got = row(sdata.find_chance_of_finding(same_within=5, spread=10, difference=1, values_per_group=40))
    assert got["power"] == pytest.approx(0.3960616142224, rel=1e-8)
    # R: TOSTER::power_t_TOST(n = NULL, delta = 0, sd = 2, eqb = 1, alpha = 0.05, power = 0.9, type = "paired")$n
    got = row(sdata.find_how_many_needed(for_test="compare_before_after", same_within=1, spread=2, power=0.9))
    assert got["values per group (exact)"] == pytest.approx(44.67998225272, rel=1e-6)
    # R: power_t_TOST(n = 40, delta = 1, sd = 10, low_eqbound = -3, high_eqbound = 5, power = NULL)$power
    got = row(sdata.find_chance_of_finding(same_within=[-3, 5], spread=10, difference=1, values_per_group=40))
    assert got["power"] == pytest.approx(0.1118161018619, rel=1e-8)


def test_interval_width(needs_r, capsys):
    got = row(sdata.find_how_many_needed(interval_width=4, spread=10))
    # R: presize::prec_mean(mean = 0, sd = 10, conf.width = 4)$n
    assert got["values (exact)"] == pytest.approx(98.46625538073, rel=1e-8)
    assert got["values"] == 99
    assert "presize::prec_mean()" in capsys.readouterr().out


def test_power_additions_errors():
    with pytest.raises(SimplydataError, match="compare_counts"):
        sdata.find_chance_of_finding(percents=[30, 15], values_per_group=50)
    with pytest.raises(SimplydataError, match="two percents"):
        sdata.find_chance_of_finding(for_test="compare_counts", percents=[30], values_per_group=50)
    with pytest.raises(SimplydataError, match="based_on=\"ranks\" goes with"):  # S3b-2: ranks are simulated now
        sdata.find_how_many_needed(for_test="compare_counts", effect_size=0.3, based_on="ranks")
    with pytest.raises(SimplydataError, match="spread="):
        sdata.find_how_many_needed(same_within=5)
    with pytest.raises(SimplydataError, match="inside the margin"):
        sdata.find_chance_of_finding(same_within=5, spread=10, difference=6, values_per_group=40)
