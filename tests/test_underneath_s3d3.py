"""The same underneath for phase S3d-3 (Bayesian methods). tests/test_underneath.py runs every entry of UNDERNEATH,
these included; this file checks that each word that takes test_method="bayesian" has its entry, and that leaving out one of
simplydata's choices makes a comparison fail.
"""

import os

import pytest

from simplydata._underneath import UNDERNEATH, Entry, bayesian
from simplydata._underneath.check import check_entry

KEYS = [f"table.{w} test_method=\"bayesian\"" for w in (
    "compare_averages_of", "compare_before_and_after", "compare_average_to", "find_correlation_between",
    "compare_counts_of", "explain", "check_model_of")] + ["table.explain test_method=\"bayesian\", grouped_by="]


@pytest.mark.parametrize("key", KEYS)
def test_every_bayesian_word_has_an_entry(key):
    assert key in UNDERNEATH, key
    assert all(e.key in UNDERNEATH for e in bayesian.ENTRIES)


@pytest.mark.parametrize("entry", bayesian.ENTRIES, ids=lambda e: e.key)
def test_each_entry_uses_its_option(entry):
    for part in entry.option.split(", "):
        assert part.split("=")[0] + "=" in entry.ours_code(), f"{entry.key}: ours= uses {part}"


@pytest.mark.parametrize("key, setting, replacement", [
    ("table.compare_averages_of test_method=\"bayesian\"", 'rscale = "medium"', 'rscale = "wide"'),
    ("table.compare_before_and_after test_method=\"bayesian\"", "set.seed(1,", "set.seed(2,"),
    ("table.compare_average_to test_method=\"bayesian\"", "x = x - 5", "x = x, mu = 5"),
    ("table.compare_counts_of test_method=\"bayesian\"", 'fixedMargin = "rows"', 'fixedMargin = "cols"'),
    ("table.explain test_method=\"bayesian\"", "seed = 1,", "seed = 2,"),
])
def test_leaving_out_a_choice_makes_the_comparison_fail(key, setting, replacement):
    entry = UNDERNEATH[key]
    from simplydata._r import r_ready

    if not r_ready(entry.r_packages):
        if os.environ.get("SIMPLYDATA_REQUIRE_R") == "1":
            pytest.fail("needs R")
        pytest.skip("needs R")
    library = next(iter(entry.code))
    assert setting in entry.code[library]
    changed = dict(entry.code)
    changed[library] = entry.code[library].replace(setting, replacement)
    outcomes = check_entry(Entry(**{**entry.__dict__, "code": changed}))
    assert outcomes and not any(o.passed for o in outcomes), f"{key}: should fail without {setting}"
