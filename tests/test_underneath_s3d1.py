"""The same underneath for phase S3d-1 (planning an experiment and survey answers). tests/test_underneath.py runs every
entry of UNDERNEATH, these included; this file checks that each new S3d-1 word and option has its entry, and that
leaving out one of simplydata's choices makes a comparison fail.
"""

import os

import pytest

from simplydata._underneath import UNDERNEATH, Entry, planning_surveys
from simplydata._underneath.check import check_entry

KEYS = ["sdata.make_random_assignments", "sdata.make_design_table",
        'sdata.make_design_table of_kind="randomised blocks"', 'sdata.make_design_table of_kind="latin square"',
        'sdata.make_design_table of_kind="split plot"', "table.keep_random_rows for_each_group_in=",
        "table.keep_random_rows percent=", 'table.count_empty_cells_in show="patterns"',
        "table.count_each columns=, in_order=", "draw_answer_bars"] + [
    f"table.{w} after use_survey_design()" for w in (
        "find_average_of", "find_total_of", "find_median_of", "find_percentile_of", "find_percent_of_rows_where",
        "count_rows", "explain", "compare_averages_of", "compare_counts_of")]


@pytest.mark.parametrize("key", KEYS)
def test_every_s3d1_word_and_option_has_an_entry(key):
    assert key in UNDERNEATH, key
    assert all(e.key in UNDERNEATH for e in planning_surveys.ENTRIES)


@pytest.mark.parametrize("entry", [e for e in planning_surveys.ENTRIES if "=" in e.option],
                         ids=lambda e: e.key)
def test_each_option_entry_uses_its_option(entry):
    for part in entry.option.split(", "):
        assert part.split("=")[0] + "=" in entry.ours_code(), f"{entry.key}: ours= uses {part}"


@pytest.mark.parametrize("entry", [e for e in planning_surveys.ENTRIES if "use_survey_design" in e.option],
                         ids=lambda e: e.key)
def test_each_survey_entry_sets_the_design_first(entry):
    assert "use_survey_design(" in entry.ours_code()


@pytest.mark.parametrize("key, setting, replacement", [
    ("table.keep_random_rows for_each_group_in=", "random_state=1", "random_state=2"),
    ('table.count_empty_cells_in show="patterns"', "ascending=[True, False]", "ascending=[True, True]"),
    ("sdata.make_design_table", 'kinds = "Mersenne-Twister"', 'kinds = "Super-Duper"'),
    ("sdata.make_random_assignments", "block.sizes = c(4, 6) / 2", "block.sizes = c(4, 6)"),
    ("table.find_average_of after use_survey_design()", "df = survey::degf(d)", "df = Inf"),
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
