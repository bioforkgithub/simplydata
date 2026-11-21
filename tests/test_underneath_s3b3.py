"""The same underneath for phase S3b-3 (survival and person-time). tests/test_underneath.py runs every entry of
UNDERNEATH, these included; this file checks that each S3b-3 word and option has its entry, and that leaving out
one of simplydata's choices makes a comparison fail.
"""

import os

import pytest

from simplydata._underneath import UNDERNEATH, Entry, survival
from simplydata._underneath.check import check_entry


def test_the_new_words_have_entries():
    for word in ("table.add_time_and_event_columns", "table.find_risk_over_time", "draw_risk_curves"):
        assert word in UNDERNEATH, word
    assert all(e.key in UNDERNEATH for e in survival.ENTRIES)


def test_every_s3b3_option_has_an_entry():
    shown = {(e.word, e.option.split("=")[0]) for e in survival.ENTRIES if e.option}
    for word, options in [("table.find_survival_over_time", ("at_time_points", "test_method", "allowing_for",
                                                             "followed_from", "average_time_up_to")),
                          ("table.compare_survival", ("allowing_for", "followed_from", "average_time_up_to",
                                                      "competing_with")),
                          ("table.explain_survival", ("allowing_for", "followed_from", "competing_with", "test_method",
                                                      "distribution")),
                          ("draw_survival_curves", ("allowing_for", "followed_from")),
                          ("draw_risk_curves", ("competing_with",))]:
        for option in options:
            assert (word, option) in shown, (word, option)


@pytest.mark.parametrize("entry", [e for e in survival.ENTRIES if e.option], ids=lambda e: e.key)
def test_each_option_entry_uses_its_option(entry):
    assert entry.option.split("=")[0] + "=" in entry.ours_code(), f"{entry.key}: ours= uses the option"


@pytest.mark.parametrize("key, setting, replacement", [
    ("table.compare_survival allowing_for=", "strata=df[\"age\"] > 70", "strata=None"),
    ("table.compare_survival average_time_up_to=", "tau = 700", "tau = 600"),
    ("table.find_risk_over_time", 'levels = c("still followed", "first_esbl", "discharged")',
     'levels = c("discharged", "first_esbl", "still followed")'),
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
