"""Phase S3b-2, planning a study: the new routes of find_how_many_needed and find_chance_of_finding.

Published numbers: presize's JOSS paper (Haynes et al. 2021), the G*Power 3.1 manual (logistic regression, ch. 29;
multiple regression, ch. 13 = Cohen 1988 example 9.1), the Stata power manuals ([PSS-2] power logrank, Schoenfeld
and Freedman; power twomeans cluster, Ahn, Heo & Zhang 2015). R gives the rest (gsDesign, powerSurvEpi, pwrss, pwr).
"""

import numpy as np
import pytest
from scipy import stats

import simplydata as sdata
from simplydata._errors import SimplydataError


def row(result):
    return result.as_pandas().iloc[0]


find, chance = sdata.find_how_many_needed, sdata.find_chance_of_finding


# ---------------------------------------------------------------- U06: a percent's interval
def test_percent_interval_width_matches_presize_paper(capsys):
    got = row(find(interval_width=5, percents=[15]))
    assert got["values (exact)"] == pytest.approx(783.4897, abs=5e-5)  # Haynes et al. (2021), JOSS 6(60):3118
    assert got["values"] == 784
    assert "Wilson interval" in capsys.readouterr().out
    assert row(find(interval_width=10, percents=[30]))["values"] == 320


# ---------------------------------------------------------------- U13: survival, events first
def test_schoenfeld_events_and_people(capsys):
    got = row(find(for_test="compare_survival", effect_size=0.7, percents=[30, 40]))
    assert got["events (exact)"] == pytest.approx(246.7871, abs=5e-5)
    assert got["events"] == 247 and got["people per group"] == 353 and got["people in all"] == 706
    out = capsys.readouterr().out
    assert out.index("247 events") < out.index("706 people")  # events first
    assert "hazard ratio of 0.7 (" in out.splitlines()[0]  # the first sentence names the scale
    assert "Cohen" not in out  # never Cohen's labels for a hazard ratio


@pytest.mark.parametrize("kwargs, events", [
    (dict(effect_size=0.5), 66),                                    # Stata [PSS-2] power logrank, example 2
    (dict(effect_size=float(np.log(0.5) / np.log(0.6)), sides=1), 266),  # example 5 (Machin et al. 2009, p. 91)
])
def test_schoenfeld_events_published(kwargs, events):
    assert row(find(for_test="compare_survival", **kwargs))["events"] == events


def test_freedman_people():
    assert row(find(for_test="compare_survival", effect_size=0.5, percents=[100, 100], test_method="freedman"))[
        "people per group"] == 36  # Stata [PSS-2] power logrank, example 1
    assert row(find(for_test="compare_survival", effect_size=0.7, percents=[30, 40], test_method="freedman"))[
        "people per group"] == 361


def test_survival_power_with_people():
    got = row(chance(for_test="compare_survival", effect_size=0.7, values_per_group=353, percents=[30, 40]))
    assert got["power"] == pytest.approx(0.8004967, abs=1e-6)


# ---------------------------------------------------------------- U09: regression, Cohen's f²
def test_regression_f2(capsys):
    got = row(find(for_test="explain", effect_size=0.15, using=["temperature", "salinity", "depth"]))
    assert got["rows (exact)"] == pytest.approx(72.70583 + 4, abs=1e-4)  # R pwr.f2.test v = 72.70583
    assert got["rows"] == 77
    assert "temperature, salinity and depth" in capsys.readouterr().out
    # G*Power manual 13.3.1 = Cohen (1988) example 9.1: power 0.673586
    assert row(chance(for_test="explain", effect_size=0.1 / 0.9, using=5, values_per_group=95))["power"] == \
        pytest.approx(0.673586, abs=1e-6)


def test_compare_models_tests_the_extra_columns():
    got = row(find(for_test="compare_models", effect_size=0.4285714, using=["a"], against=["a", "b", "c"],
                   significance=0.001))
    assert got["columns tested"] == 2 and got["columns in all"] == 3
    # pwr vignette (Kutner et al. 8.43): u = 2, f2 = 0.4285714, sig.level 0.001, power 0.8 -> v = 49.88971
    assert got["rows (exact)"] == pytest.approx(49.88971 + 3 + 1, abs=1e-4)


# ---------------------------------------------------------------- U11: logistic regression
def test_logistic_matches_gpower_manual(capsys):
    got = row(find(for_test="explain", outcome="yes or no", using=["dose"], percents=[50], effect_size=1.5, power=0.95))
    assert got["values"] == 337  # G*Power 3.1 manual 29.4: Demidenko with variance correction
    out = capsys.readouterr().out
    assert "odds ratio of 1.5 per standard deviation of dose" in out and "Cohen" not in out
    assert row(chance(for_test="explain", outcome="yes or no", using="dose", percents=[50], effect_size=1.5,
                      values_per_group=337))["power"] == pytest.approx(0.950077, abs=1e-6)


# ---------------------------------------------------------------- U15: clusters
def test_clusters_design_effect(capsys):
    got = row(find(effect_size=0.5, in_clusters_of=20, alike_within_clusters=0.05))
    assert got["design effect"] == pytest.approx(1.95)
    assert got["values per group"] == 125 and got["clusters per group"] == 7
    out = capsys.readouterr().out
    assert "7 clusters of 20 (140 values) per group" in out  # the review's arithmetic fix
    assert "fewer than about 10 clusters" in out


def test_clusters_published_stata_example():
    # Stata [PSS-2] power twomeans, cluster, example 1 (Ahn, Heo & Zhang 2015): K = 13 clusters, N = 260 per arm
    got = row(find(difference=1.1, spread=3.67, in_clusters_of=20, alike_within_clusters=0.025))
    assert got["clusters per group"] == 13 and got["values in whole clusters"] == 260


def test_icc_zero_gives_todays_answer():
    plain = row(find(effect_size=0.5))
    got = row(find(effect_size=0.5, in_clusters_of=20, alike_within_clusters=0))
    assert got["values per group"] == plain["values per group"]


def test_clusters_on_chance_and_percents():
    got = row(chance(effect_size=0.5, values_per_group=140, in_clusters_of=20, alike_within_clusters=0.05))
    assert got["counts as independent values"] == pytest.approx(140 / 1.95)
    assert got["power"] == pytest.approx(row(chance(effect_size=0.5, values_per_group=140 / 1.95))["power"])
    assert row(find(for_test="compare_counts", percents=[30, 15], in_clusters_of=10, alike_within_clusters=0.02))[
        "values per group"] == 143


# ---------------------------------------------------------------- U07 and U16: simulation
def test_rank_power_by_simulation_repeats_and_is_close_to_known(capsys):
    a = row(chance(effect_size=0.5, values_per_group=64, based_on="ranks"))
    b = row(chance(effect_size=0.5, values_per_group=64, based_on="ranks"))
    assert a["power"] == b["power"]  # seeded
    assert a["power"] == pytest.approx(0.782, abs=0.015)  # ARE 0.955 against the t-test's 0.80
    assert a["power 95 % CI low"] < a["power"] < a["power 95 % CI high"]
    assert "Monte Carlo error" in capsys.readouterr().out


def test_power_curve_gives_one_row_each():
    got = chance(effect_size=0.5, values_per_group=[10, 20, 30], based_on="ranks", tries=2000).as_pandas()
    assert list(got["values per group"]) == [10, 20, 30]
    assert got["power"].is_monotonic_increasing


def test_drawing_from_agrees_with_the_formula():
    normal0 = sdata.distribution("normal", average=0, standard_deviation=1)
    normal1 = sdata.distribution("normal", average=0.5, standard_deviation=1)
    simulated = row(chance(drawing_from=[normal0, normal1], values_per_group=64))
    formula = row(chance(effect_size=0.5, values_per_group=64))
    assert simulated["power 95 % CI low"] - 0.005 < formula["power"] < simulated["power 95 % CI high"] + 0.005


def test_needed_by_simulation_reaches_the_target():
    got = row(find(effect_size=0.5, based_on="ranks"))
    assert got["power with that many"] >= 0.8
    assert 60 <= got["values per group"] <= 72


def test_by_running_counts_the_p_values():
    def one_study(seed):
        rng = np.random.default_rng(seed)
        return stats.ttest_ind(rng.normal(0, 1, 20), rng.normal(0.8, 1, 20)).pvalue

    got = row(chance(by_running=one_study, tries=300))
    expected = sum(one_study(s) < 0.05 for s in range(1, 301))
    assert got["p-values below significance"] == expected
    assert got["power"] == pytest.approx(expected / 300)


def test_by_running_refuses_a_function_that_ignores_its_seed():
    with pytest.raises(SimplydataError, match="same p-value every time"):
        chance(by_running=lambda seed: 0.2, tries=200)


# ---------------------------------------------------------------- errors
@pytest.mark.parametrize("call, message", [
    (lambda: find(for_test="compare_survival", effect_size=1), "of 1 means no difference"),
    (lambda: find(for_test="compare_survival", effect_size=-0.5), "cannot be 0 or below"),
    (lambda: find(for_test="compare_survival", effect_size=0.7, test_method="freedman"), "needs percents="),
    (lambda: find(for_test="compare_survival", effect_size=0.7, test_method="cox"), "test_method="),
    (lambda: find(for_test="compare_survival", effect_size=0.7, percents=[30, 40], sides=1), "two-sided only"),
    (lambda: chance(for_test="compare_survival", effect_size=0.7, values_per_group=100), "needs percents="),
    (lambda: find(for_test="explain", outcome="yes or no", using=["dose"], percents=[20], effect_size=0), "odds ratio"),
    (lambda: find(for_test="explain", outcome="yes or no", using=["a", "b"], percents=[20], effect_size=1.5),
     "one number column"),
    (lambda: find(for_test="explain", outcome="yes or no", using=["a"], effect_size=1.5), "percents="),
    (lambda: find(for_test="explain", effect_size=0.15), "needs using="),
    (lambda: find(for_test="compare_models", effect_size=0.15, using=["a"]), "using= and against="),
    (lambda: find(for_test="compare_models", effect_size=0.15, using=["a", "b"], against=["c"]), "nested"),
    (lambda: find(for_test="explain", effect_size=0.15, using=3, sides=1), "sides=1"),
    (lambda: find(effect_size=0.5, in_clusters_of=20), "alike_within_clusters="),
    (lambda: find(effect_size=0.5, in_clusters_of=20, alike_within_clusters=1.5), "between 0 and 1"),
    (lambda: find(effect_size=0.5, in_clusters_of=1, alike_within_clusters=0.05), "2 or more"),
    (lambda: find(for_test="compare_survival", effect_size=0.7, in_clusters_of=20, alike_within_clusters=0.05),
     "in_clusters_of= and alike_within_clusters= goes with"),
    (lambda: find(effect_size=0.5, using=["a"]), "using= goes with"),
    (lambda: find(effect_size=0.5, test_method="schoenfeld"), "test_method= goes with"),
    (lambda: find(for_test="compare_counts", effect_size=0.3, based_on="ranks"), 'based_on="ranks" goes with'),
    (lambda: find(for_test="compare_spreads", effect_size=0.5), "drawing_from="),
    (lambda: chance(drawing_from=[1, 2], values_per_group=20), "sdata.distribution"),
    (lambda: chance(effect_size=0.5, values_per_group=[10, 20]), "power curve"),
    (lambda: chance(effect_size=0.5, values_per_group=20, based_on="ranks", tries=10), "at least 100"),
    (lambda: chance(by_running=5), "takes a function"),
    (lambda: find(interval_width=10, percents=[30, 40]), "one percent"),
    (lambda: find(interval_width=150, percents=[30]), "percentage points"),
])
def test_errors_say_what_to_do(call, message):
    with pytest.raises(SimplydataError, match=message.replace("(", r"\(").replace(")", r"\)")):
        call()


# ---------------------------------------------------------------- the same underneath
def test_every_s3b2_option_has_an_entry():
    from simplydata._underneath import UNDERNEATH

    for key in ("sdata.find_how_many_needed", "sdata.find_chance_of_finding",
                "sdata.find_how_many_needed interval_width=", "sdata.find_how_many_needed test_method=",
                "sdata.find_how_many_needed test_method=", "sdata.find_how_many_needed using=",
                "sdata.find_how_many_needed outcome=", "sdata.find_how_many_needed in_clusters_of=",
                "sdata.find_how_many_needed based_on=", "sdata.find_chance_of_finding drawing_from=",
                "sdata.find_chance_of_finding by_running="):
        assert key in UNDERNEATH, key


@pytest.mark.parametrize("key, setting, replacement", [
    ("sdata.find_how_many_needed in_clusters_of=", "design = 1 + (20 - 1) * 0.05", "design = 1.0"),
    ("sdata.find_how_many_needed", "alpha=0.05 / 2", "alpha=0.05"),
    ("sdata.find_chance_of_finding drawing_from=", "equal_var=False", "equal_var=True"),
])
def test_leaving_out_a_choice_makes_the_comparison_fail(key, setting, replacement):
    from simplydata._underneath import UNDERNEATH, Entry
    from simplydata._underneath.check import check_entry

    entry = UNDERNEATH[key]
    library = next(iter(entry.code))
    assert setting in entry.code[library]
    changed = dict(entry.code)
    changed[library] = entry.code[library].replace(setting, replacement)
    outcomes = check_entry(Entry(**{**entry.__dict__, "code": changed}))
    assert outcomes and not any(o.passed for o in outcomes), f"{key}: should fail without {setting}"


def test_the_design_effect_is_the_only_own_arithmetic_and_is_marked():
    import inspect

    from simplydata import power_more

    assert "[D]" in inspect.getsource(power_more.clustered)


# ---------------------------------------------------------------- review fixes
def test_a_power_curve_gives_each_number_its_single_answer():
    curve = chance(effect_size=0.5, values_per_group=[10, 20], based_on="ranks", tries=2000).as_pandas()
    alone = row(chance(effect_size=0.5, values_per_group=20, based_on="ranks", tries=2000))
    assert curve["power"].iloc[1] == alone["power"]


def test_too_few_values_in_clusters_are_refused_not_nan():
    with pytest.raises(SimplydataError, match="independent values"):
        chance(effect_size=0.5, values_per_group=3, in_clusters_of=20, alike_within_clusters=0.5)


def test_by_running_refuses_a_function_that_does_not_repeat():
    def careless(seed):
        return float(np.random.default_rng().random())

    with pytest.raises(SimplydataError, match="different p-value each time"):
        chance(by_running=careless, tries=200)


@pytest.mark.parametrize("call", [
    lambda: chance(for_test="compare_survival", effect_size=0.7, values_per_group=0, percents=[30, 40]),
    lambda: chance(effect_size=0.5, values_per_group=-5),
])
def test_values_per_group_must_be_more_than_0(call):
    with pytest.raises(SimplydataError, match="more than 0"):
        call()


def test_numpy_whole_numbers_are_accepted():
    assert row(find(effect_size=0.5, in_clusters_of=np.int64(20), alike_within_clusters=0.05))["clusters per group"] == 7


def test_first_sentences_name_the_scale(capsys):
    find(for_test="explain", effect_size=0.15, using=3)
    assert "times as much of the spread" in capsys.readouterr().out.splitlines()[0]
