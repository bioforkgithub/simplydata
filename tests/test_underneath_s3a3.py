"""The same underneath for phase S3a-3 (checking and comparing). tests/test_underneath.py runs every entry of
UNDERNEATH, these included (the new words and their options, keyed "word option="); this file checks that each
S3a-3 word and option has its entry, and that leaving out one of simplydata's choices makes a comparison fail.
"""

import os

import pytest

from simplydata._underneath import UNDERNEATH, Entry, checking
from simplydata._underneath.check import check_entry


def test_the_new_words_have_entries():
    for word in ("table.find_columns_that_predict", "table.find_group_levels_of", "draw_interaction_lines"):
        assert word in UNDERNEATH, word
    assert all(e.key in UNDERNEATH for e in checking.ENTRIES)


def test_every_s3a3_option_has_an_entry():
    shown = {(e.word, e.option.split("=")[0]) for e in checking.ENTRIES if e.option}
    for word, option in [("table.explain", "spread_changes_with"), ("table.explain", "neighbours_alike_in_order_of"),
                         ("table.compare_models", "using"), ("table.compare_models", "check_on_left_out_rows"),
                         ("table.find_model_averages_of", "comparing"),
                         ("table.find_model_averages_of", "within_each_group_in"),
                         ("table.find_model_averages_of", "over_range_of"),
                         ("table.compare_averages_of", "grouped_by"), ("table.compare_averages_of", "for_each_group_in")]:
        assert (word, option) in shown, (word, option)


@pytest.mark.parametrize("entry", [e for e in checking.ENTRIES if e.option], ids=lambda e: e.key)
def test_each_option_entry_uses_its_option(entry):
    name = entry.option.split("=")[0] + "="
    if not name.startswith(("using", "for_each")):  # a list of models, a list of columns: shown by the call itself
        assert name in entry.ours_code(), f"{entry.key}: ours= uses the option"


@pytest.mark.parametrize("key, setting, replacement", [
    ("table.compare_models check_on_left_out_rows=True", "K = 10", "K = 5"),
    ("table.find_columns_that_predict", 's = "lambda.1se"', 's = "lambda.min"'),
    ("table.explain spread_changes_with=", "weights = nlme::varIdent(form = ~ 1 | school)", "weights = NULL"),
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
