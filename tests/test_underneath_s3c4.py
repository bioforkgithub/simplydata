"""The same underneath for phase S3c-4 (small additions to known words). tests/test_underneath.py runs every entry of
UNDERNEATH, these included; this file checks that each new S3c-4 option and value has its entry, and that leaving
out one of simplydata's choices makes a comparison fail.
"""

import os

import pytest

from simplydata._underneath import UNDERNEATH, Entry, small_additions
from simplydata._underneath.check import check_entry

OPTIONS = ["table.find_percentile_of weights=", 'table.find_percentile_of weight_kind="analytic"',
           "table.find_median_of weights=", 'table.find_correlation_between show="covariance"',
           'table.forecast order="automatic"', 'table.add_adjusted_p_value_column test_method="storey"',
           'table.add_adjusted_p_value_column test_method="local fdr"',
           'table.compare_each_pair_of matched_by=, test_method="nemenyi"',
           'table.compare_each_pair_of matched_by=, test_method="conover"', 'table.compare_each_pair_of based_on="percents"']


@pytest.mark.parametrize("key", OPTIONS)
def test_every_s3c4_option_has_an_entry(key):
    assert key in UNDERNEATH, key
    assert all(e.key in UNDERNEATH for e in small_additions.ENTRIES)


@pytest.mark.parametrize("entry", small_additions.ENTRIES, ids=lambda e: e.key)
def test_each_option_entry_uses_its_option(entry):
    for part in entry.option.split(", "):
        assert part.split("=")[0] + "=" in entry.ours_code(), f"{entry.key}: ours= uses {part}"


@pytest.mark.parametrize("key, setting, replacement", [
    ("table.find_percentile_of weights=", 'np.repeat(df["price"].to_numpy(), df["count"].to_numpy())',
     'df["price"].to_numpy()'),
    ('table.compare_each_pair_of based_on="percents"', "correction=True", "correction=False"),
    ('table.add_adjusted_p_value_column test_method="storey"', "qvalue::qvalue(p)", "qvalue::qvalue(p, pi0 = 1)"),
    ('table.compare_each_pair_of matched_by=, test_method="conover"', 'p.adjust.method = "holm"',
     'p.adjust.method = "single-step"'),
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
