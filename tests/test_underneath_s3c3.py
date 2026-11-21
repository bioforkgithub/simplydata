"""The same underneath for phase S3c-3 (directions, places and extremes). tests/test_underneath.py runs every entry of
UNDERNEATH, these included; this file checks that each S3c-3 word and option has its entry, and that leaving out
one of simplydata's choices makes a comparison fail.
"""

import os

import pytest

from simplydata._underneath import UNDERNEATH, Entry, places
from simplydata._underneath.check import check_entry

WORDS = ("table.find_average_direction_of", "table.find_variogram_of", "table.find_return_levels_of",
         "draw_variogram", "draw_threshold_check")
OPTIONS = ['table.compare_shape_to shape="even around the circle"', "table.find_autocorrelation_of x=",
           "table.find_autocorrelation_of nearest=", "table.find_return_levels_of values_above=",
           'table.fit_distribution_to distribution="gev"']


def test_the_new_words_have_entries():
    for word in WORDS:
        assert word in UNDERNEATH, word
    assert all(e.key in UNDERNEATH for e in places.ENTRIES)


@pytest.mark.parametrize("key", OPTIONS)
def test_every_s3c3_option_has_an_entry(key):
    assert key in UNDERNEATH, key


@pytest.mark.parametrize("entry", [e for e in places.ENTRIES if e.option], ids=lambda e: e.key)
def test_each_option_entry_uses_its_option(entry):
    assert entry.option.split("=")[0] + "=" in entry.ours_code(), f"{entry.key}: ours= uses the option"


@pytest.mark.parametrize("key, setting, replacement", [
    ("table.find_average_direction_of", "high=360, low=0),                      # (1)",
     "high=360, low=-180),                   # (1)"),
    ("table.find_autocorrelation_of x=", 'type = "idw", alpha = 1', 'type = "idw", alpha = 2'),
    ('table.compare_shape_to shape="even around the circle"', 'units = "degrees", ', ""),
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
