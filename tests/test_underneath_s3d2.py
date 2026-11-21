"""The same underneath for phase S3d-2 (epidemiology and cause and effect). tests/test_underneath.py runs every entry of
UNDERNEATH, these included; this file checks that each new S3d-2 word and option has its entry, and that leaving out one
of simplydata's choices makes a comparison fail.
"""

import os

import pytest

from simplydata._underneath import UNDERNEATH, Entry, causal
from simplydata._underneath.check import check_entry

KEYS = ["table.compare_balanced_groups_of", 'table.compare_balanced_groups_of method="matching"',
        'table.compare_risks show="attributable fractions"', "table.rate_of standard_population=",
        "table.compare_rates standard_rates=", "table.explain through=", "table.compare_averages_of period=",
        'table.find_correlation_between empty_cells="multiple imputation"']


@pytest.mark.parametrize("key", KEYS)
def test_every_s3d2_word_and_option_has_an_entry(key):
    assert key in UNDERNEATH, key
    assert all(e.key in UNDERNEATH for e in causal.ENTRIES)


@pytest.mark.parametrize("entry", [e for e in causal.ENTRIES if e.option], ids=lambda e: e.key)
def test_each_option_entry_uses_its_option(entry):
    for part in entry.option.split(", "):
        assert part.split("=")[0] + "=" in entry.ours_code(), f"{entry.key}: ours= uses {part}"


@pytest.mark.parametrize("key, setting, replacement", [
    ("table.compare_balanced_groups_of", 'estimand = "ATE"', 'estimand = "ATT"'),
    ('table.compare_balanced_groups_of method="matching"', "cluster = ~subclass", "cluster = NULL"),
    ("table.compare_rates standard_rates=", "s / 1000", "s / 100"),
    ("table.compare_averages_of period=", "alpha=0.10", "alpha=0.05"),
])
def test_leaving_out_a_choice_makes_the_comparison_fail(key, setting, replacement):
    entry = UNDERNEATH[key]
    from simplydata._r import r_ready

    if entry.uses_r and not r_ready(entry.r_packages):
        if os.environ.get("SIMPLYDATA_REQUIRE_R") == "1":
            pytest.fail("needs R")
        pytest.skip("needs R")
    library = next(iter(entry.code))
    assert setting in entry.code[library]
    changed = dict(entry.code)
    changed[library] = entry.code[library].replace(setting, replacement)
    outcomes = check_entry(Entry(**{**entry.__dict__, "code": changed}))
    assert outcomes and not any(o.passed for o in outcomes), f"{key}: should fail without {setting}"
