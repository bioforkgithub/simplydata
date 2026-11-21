"""The same underneath for phase S3c-1 (communities and resistomes). tests/test_underneath.py runs every entry of
UNDERNEATH, these included; this file checks that each S3c-1 word and option has its entry, and that leaving out
one of simplydata's choices makes a comparison fail.
"""

import os

import pytest

from simplydata._underneath import UNDERNEATH, Entry, communities
from simplydata._underneath.check import check_entry

WORDS = ("table.add_diversity_columns", "draw_richness_curves", "table.add_log_ratio_columns",
         "table.add_principal_coordinates", "table.explain_profiles_of", "table.find_correlation_between_profiles",
         "draw_cluster_tree", "table.add_axes_that_separate_groups", "table.add_correspondence_axes")
OPTIONS = ["table.add_diversity_columns at_total_count=", 'table.add_diversity_columns show="chao1"',
           'table.add_diversity_columns show="hill numbers"', 'table.add_log_ratio_columns test_method="alr"',
           'table.add_log_ratio_columns test_method="ilr"', 'table.add_log_ratio_columns zeros_replaced_by="adding 1"',
           'table.add_principal_coordinates measure="aitchison"', 'table.explain_profiles_of measure="hellinger"',
           'table.explain_profiles_of test_method="canonical correspondence"', "table.explain_profiles_of allowing_for=",
           'table.find_correlation_between_profiles test_method="procrustes"', 'table.compare_profiles_of test_method="anosim"',
           'table.compare_profiles_of show="contributions"', 'table.compare_profiles_of measure="aitchison"',
           'table.find_distances_between_rows measure="aitchison"', 'table.add_clusters how_many="automatic"',
           "table.add_clusters measure="]


def test_the_new_words_have_entries():
    for word in WORDS:
        assert word in UNDERNEATH, word
    assert all(e.key in UNDERNEATH for e in communities.ENTRIES)


@pytest.mark.parametrize("key", OPTIONS)
def test_every_s3c1_option_has_an_entry(key):
    assert key in UNDERNEATH, key


@pytest.mark.parametrize("entry", [e for e in communities.ENTRIES if e.option], ids=lambda e: e.key)
def test_each_option_entry_uses_its_option(entry):
    assert entry.option.split("=")[0] + "=" in entry.ours_code(), f"{entry.key}: ours= uses the option"


@pytest.mark.parametrize("key, setting, replacement", [
    ("table.add_log_ratio_columns", 'method = "GBM"', 'method = "CZM"'),
    ("table.add_clusters measure=", 'method = "average"', 'method = "single"'),
    ('table.explain_profiles_of measure="hellinger"', 'by = "margin"', 'by = "terms"'),
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
