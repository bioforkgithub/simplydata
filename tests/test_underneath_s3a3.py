"""The same underneath for phase S3a-3 (checking and comparing): the new words' entries and one entry for each
new option (simplydata._underneath.checking). Each runs its simplydata call next to the same job in the package
underneath (statsmodels, seaborn, R) and both must give the same result. R entries are skipped where R is
missing, except in CI (SIMPLYDATA_REQUIRE_R=1).
"""

import os

import pytest

from simplydata import learn
from simplydata._underneath import UNDERNEATH, UNDERNEATH_OPTIONS, Entry, checking
from simplydata._underneath.check import check_entry

OPTIONS = list(checking.OPTION_ENTRIES)
WORDS = list(checking.ENTRIES)


def _run(entry):
    outcomes = check_entry(entry)
    assert outcomes, entry.label
    skipped = [o for o in outcomes if o.skipped]
    if skipped:
        if os.environ.get("SIMPLYDATA_REQUIRE_R") == "1":
            pytest.fail(f"SIMPLYDATA_REQUIRE_R=1 but {entry.label} could not run: {skipped[0].skipped}")
        pytest.skip(skipped[0].skipped)
    failed = [f"{o.library} on a {o.engine} table: " + "; ".join(o.differences) for o in outcomes if not o.passed]
    assert not failed, f"{entry.label}: " + "\n".join(failed)


@pytest.mark.parametrize("entry", OPTIONS, ids=[e.label for e in OPTIONS])
def test_the_option_and_the_library_give_the_same_result(entry):
    _run(entry)


@pytest.mark.parametrize("entry", OPTIONS, ids=[e.label for e in OPTIONS])
def test_option_entry_is_complete_and_uses_the_option(entry):
    from test_underneath import test_entry_is_complete

    test_entry_is_complete(entry)
    assert entry.word in learn._all_keys() and not learn._old_names(entry.word), entry.word
    name = entry.option.split("=")[0] + "="
    if not name.startswith(("using", "for_each")):
        assert name in entry.ours_code(), f"{entry.label}: ours= uses the option"
    assert f".{learn._word(entry.word)}(" in entry.ours_code()


def test_the_new_words_have_entries_and_the_options_are_registered():
    for word in ("table.find_columns_that_predict", "table.find_group_levels_of", "draw_interaction_lines"):
        assert word in UNDERNEATH, word
    assert all(e in UNDERNEATH_OPTIONS for e in OPTIONS)


def test_every_s3a3_option_has_an_entry():
    shown = {(e.word, e.option.split("=")[0]) for e in OPTIONS}
    for word, option in [("table.explain", "spread_changes_with"), ("table.explain", "neighbours_alike_in_order_of"),
                         ("table.compare_models", "using"), ("table.compare_models", "check_on_left_out_rows"),
                         ("table.find_model_averages_of", "comparing"),
                         ("table.find_model_averages_of", "within_each_group_in"),
                         ("table.find_model_averages_of", "over_range_of"),
                         ("table.compare_averages_of", "grouped_by"), ("table.compare_averages_of", "for_each_group_in")]:
        assert (word, option) in shown, (word, option)


@pytest.mark.parametrize("label, setting, replacement", [
    ('table.compare_models (check_on_left_out_rows=True)', "K = 10", "K = 5"),
    ('table.find_columns_that_predict', 's = "lambda.1se"', 's = "lambda.min"'),
    ('table.explain (spread_changes_with="school")', "weights = nlme::varIdent(form = ~ 1 | school)",
     "weights = NULL"),
])
def test_leaving_out_a_choice_makes_the_comparison_fail(label, setting, replacement):
    entry = next(e for e in OPTIONS + WORDS if e.label == label)
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
    assert outcomes and not any(o.passed for o in outcomes), f"{label}: should fail without {setting}"
