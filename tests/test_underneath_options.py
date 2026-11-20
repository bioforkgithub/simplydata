"""The same underneath, for single options of a word (S3a-2 on): each entry of UNDERNEATH_OPTIONS runs its
simplydata call with that option next to the same job in the package underneath (SciPy, statsmodels, R) and
both must give the same result. R entries are skipped where R is missing, except in CI (SIMPLYDATA_REQUIRE_R=1).
"""

import os

import pytest

from simplydata import learn
from simplydata._underneath import UNDERNEATH, UNDERNEATH_OPTIONS
from simplydata._underneath.check import check_entry

ENTRIES = UNDERNEATH_OPTIONS


@pytest.mark.parametrize("entry", ENTRIES, ids=[e.label for e in ENTRIES])
def test_the_option_and_the_library_give_the_same_result(entry):
    outcomes = check_entry(entry)
    assert outcomes, entry.label
    skipped = [o for o in outcomes if o.skipped]
    if skipped:
        if os.environ.get("SIMPLYDATA_REQUIRE_R") == "1":
            pytest.fail(f"SIMPLYDATA_REQUIRE_R=1 but {entry.label} could not run: {skipped[0].skipped}")
        pytest.skip(skipped[0].skipped)
    failed = [f"{o.library} on a {o.engine} table: " + "; ".join(o.differences) for o in outcomes if not o.passed]
    assert not failed, f"{entry.label}: " + "\n".join(failed)


@pytest.mark.parametrize("entry", ENTRIES, ids=[e.label for e in ENTRIES])
def test_option_entry_is_complete_and_uses_the_option(entry):
    from test_underneath import test_entry_is_complete

    test_entry_is_complete(entry)
    assert entry.word in learn._all_keys() and not learn._old_names(entry.word), entry.word
    name = entry.option.split("=")[0] + "="
    assert name in entry.ours_code(), f"{entry.label}: ours= uses the option"
    assert f".{learn._word(entry.word)}(" in entry.ours_code()


def test_option_labels_are_distinct_and_not_word_keys():
    labels = [e.label for e in ENTRIES]
    assert len(labels) == len(set(labels))
    assert not set(labels) & set(UNDERNEATH)


def test_every_s3a2_option_has_an_entry():
    shown = {(e.word, e.option.split("=")[0]) for e in ENTRIES}
    for word, option in [("table.fit_line", "method"), ("table.fit_line", "with_bends"),
                         ("table.fit_line", "changes_at"), ("table.fit_curve", "of_kind"),
                         ("table.explain", "for_percentile"), ("table.explain", "changes_at"),
                         ("table.add_smoothed_column", "method"), ("draw_smooth_line", "method")]:
        assert (word, option) in shown, (word, option)


@pytest.mark.parametrize("label, setting, replacement", [
    ('table.fit_line (method="deming", y_error_over_x_error=)', "error.ratio = 1 / 4", "error.ratio = 4"),
    ('table.fit_line (method="theil-sen")', 'method="separate"', 'method="joint"'),
])
def test_leaving_out_a_choice_makes_the_option_comparison_fail(label, setting, replacement):
    entry = next(e for e in ENTRIES if e.label == label)
    if entry.uses_r:
        from simplydata._r import r_ready

        if not r_ready(entry.r_packages):
            pytest.skip("needs R")
    library = next(iter(entry.code))
    assert setting in entry.code[library]
    changed = dict(entry.code)
    changed[library] = entry.code[library].replace(setting, replacement)
    from simplydata._underneath import Entry

    outcomes = check_entry(Entry(**{**entry.__dict__, "code": changed}))
    assert outcomes and not any(o.passed for o in outcomes), f"{label}: should fail without {setting}"
