"""The reliability study (validation/): real, published data give the published answers.

Each case of validation/cases.py runs a word on real data and compares it with the published or certified
answer, the parent package and R (skipped where R is missing, except in CI with SIMPLYDATA_REQUIRE_R=1).
"""

import importlib.util
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "validation"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, VALIDATION / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


report = _load("make_report")
study = report.study


# words that make something from a formula and take no data: their cases may be closed forms (kind "closed form")
NO_DATA_BY_NATURE = ("sdata.system", "system.", "sdata.frequency_filter", "sdata.make_wave", "sdata.make_window_shape",
                     # numbers phase, batch 3: a formula is the input, so the answer worked out by hand is the check
                     "sdata.formula", "f.", "sdata.solve", "sdata.find_area_under", "sdata.find_volume_under",
                     "sdata.find_path_over_time",
                     # families for 100 %, batch 15: the path between two ends has no data either
                     "sdata.find_path_between_ends",
                     # numbers phase, batch 4: the sum of a formula's series has no data either
                     "sdata.find_sum_of_series",
                     # seaborn's colour tools: a set of colours and a changed colour are made from no data
                     "sdata.show_colours", "sdata.change_colour",
                     # families for 100 %, batches 24-26: an equation and its solution, a product of a formula, the
                     # ways to choose from a few things and facts of whole numbers (number theory) are their own
                     # inputs, checked against closed forms and the OEIS
                     "sdata.check_solution", "sdata.find_product_of_series", "sdata.list_ways_to_",
                     "nums.check_if_prime", "nums.find_prime_factors", "nums.find_number_fact")
# a word whose option alone has no data by nature: an exact grid of a few cells with letters (number_grid(exactly=True))
NO_DATA_OPTIONS = {("sdata.number_grid", "exactly=")}


def _no_data_by_nature(case) -> bool:
    return case.word.startswith(NO_DATA_BY_NATURE) or (case.word, case.option) in NO_DATA_OPTIONS


def test_every_dataset_has_a_source_a_licence_and_its_file():
    for name, d in study.DATASETS.items():
        assert d.source.strip() and d.licence.strip() and d.what.strip(), name
        if d.file:
            assert (VALIDATION / "data" / d.file).is_file(), d.file
    readme = (VALIDATION / "README.md").read_text(encoding="utf-8")
    for d in study.DATASETS.values():
        if d.file:
            assert f"data/{d.file}" in readme, f"{d.file} is not in validation/README.md"


def test_every_case_uses_a_known_dataset_and_a_current_word():
    from simplydata import learn

    for case in study.CASES:
        assert case.dataset in study.DATASETS, case.title
        assert case.word in learn._all_keys() and learn._lookup(case.word) == case.word, case.word
        assert case.kind in ("published", "real data", "made-up", "closed form"), case.kind
        if case.kind in ("published", "closed form"):
            assert case.published, f"{case.title}: a {case.kind} case names its published or worked answer"
        if case.kind == "closed form":
            assert case.dataset == "closed form (no data)" and _no_data_by_nature(case), case.title
        if case.kind == "made-up":
            assert case.dataset == "made-up", case.title
        assert case.published or case.parent or case.r, case.title


def test_every_underneath_entry_has_a_case_on_real_data():
    from simplydata._underneath import UNDERNEATH

    # a closed-form case (no data) counts only for a word that has no data by nature: a system, a wave or a window
    # shape is made from a formula, so the answer worked out from that formula is its check; every other word
    # needs a case on real data
    real = {f"{c.word} {c.option}" if c.option else c.word for c in study.CASES
            if c.kind not in ("made-up", "closed form") or _no_data_by_nature(c)}
    # a word with nothing underneath (help, undo ...) computes nothing, so there is nothing to check on real data
    computed = {key for key, entry in UNDERNEATH.items() if entry.compare != "none"}
    assert computed <= real, computed - real


def test_nist_files_are_read_with_their_certified_values():
    data, certified = study.read_nist("nist/Norris.dat")
    assert data.shape == (36, 2)
    assert certified["slope"] == 1.00211681802045 and certified["intercept"] == -0.262323073774029
    assert certified["R squared"] == 0.999993745883712
    data, certified = study.read_nist("nist/Michelso.dat")
    assert data.shape == (100, 1) and certified["mean"] == 299.8524
    data, certified = study.read_nist("nist/NumAcc4.dat")
    assert data.shape == (1001, 1) and certified["mean"] == 10000000.2


@pytest.mark.parametrize("case", study.CASES, ids=[f"{c.word}: {c.title}"[:80] for c in study.CASES])
def test_case_gives_the_published_and_the_parent_answer(case):
    rows = report.check_case(case)
    assert rows
    failed = [r for r in rows if not r["passed"] and not r["skipped"]]
    assert not failed, [(r["name"], r["reference"], r["ours"], r["theirs"], r["tolerance"], r["note"]) for r in failed]
    # a data file that is not shipped, or a newer package version (checked where it is installed): not R
    skipped = [r for r in rows if r["skipped"] and not r.get("local") and not r.get("newer")]
    if skipped and os.environ.get("SIMPLYDATA_REQUIRE_R") == "1":
        pytest.fail(f"SIMPLYDATA_REQUIRE_R=1 but {skipped[0]['skipped']}")


def test_lre_counts_the_digits_that_agree():
    assert report.lre(1.0, 1.0) == 15
    assert report.lre(1.000001, 1.0) == pytest.approx(6, abs=0.01)
    assert report.lre(1e-9, 0.0) == pytest.approx(9)


def test_report_lists_setup_checks_choices_and_datasets():
    case_rows = report.check_case(study.CASES[0])
    text = report.report(case_rows, [], {"simplydata": "x", "R": "not available"}, "2026-01-01")
    for part in ("# simplydata reliability report", "## Setup", "| Python |", "## 1. Published and real data",
                 "## 2. The same underneath", "## Choices simplydata makes", "## Datasets", "NIST certified"):
        assert part in text, part


def test_committed_report_exists_and_names_every_trial_word():
    text = (VALIDATION / "report.md").read_text(encoding="utf-8")
    from simplydata._underneath import UNDERNEATH

    for word in UNDERNEATH:
        assert f"`{word}`" in text, word
    assert "**FAIL**" not in text


def test_a_reference_number_without_a_simplydata_number_fails_the_case():
    """A misspelt name on either side must fail, not drop the comparison silently."""
    case = study.Case("nums.find_median", "a misspelt name", "made-up", "made-up",
                      ours="""
                          {"median": sdata.number_list([1, 2, 3]).find_median()}
                      """,
                      published={"mediann": (2.0, 1e-12, "exact")},
                      parent="""
                          {"median": 2.0, "the middle": 2.0}
                      """, parent_label="NumPy")
    rows = report.check_case(case)
    missing = [r for r in rows if not r["passed"]]
    assert {r["name"] for r in missing} == {"mediann", "the middle"}
    assert all("no number with this name" in r["note"] for r in missing)


def test_check_writes_no_tracked_report_and_require_r_counts_skips(tmp_path, monkeypatch):
    calls = {}

    def fake_build(require_r=False):
        calls["require_r"] = require_r
        return "# report\n", (1 if require_r else 0), 1

    monkeypatch.setattr(report, "build", fake_build)
    monkeypatch.setattr("tempfile.gettempdir", lambda: str(tmp_path))
    before = (VALIDATION / "report.md").read_text(encoding="utf-8")
    monkeypatch.delenv("SIMPLYDATA_REQUIRE_R", raising=False)
    assert report.main(["--check"]) == 0
    assert (tmp_path / "simplydata_reliability_report.md").is_file()
    assert (VALIDATION / "report.md").read_text(encoding="utf-8") == before
    assert report.main(["--check", "--require-r"]) == 1 and calls["require_r"] is True
    monkeypatch.setenv("SIMPLYDATA_REQUIRE_R", "1")
    assert report.main(["--check", "--out", str(tmp_path / "x.md")]) == 1


def test_a_monte_carlo_tolerance_uses_four_standard_errors():
    """r_tolerance="4 mcse": the difference may be 4 Monte Carlo standard errors, read from "<name> MCSE"."""
    case = study.Case("nums.find_median", "a Monte Carlo check", "made-up", "made-up",
                      ours="""
                          {"share": 0.50}
                      """,
                      parent="""
                          {"share": 0.52, "share MCSE": 0.004}
                      """, parent_label="another generator", parent_tolerance=report.MCSE)
    rows = report.check_case(case)
    assert len(rows) == 1 and not rows[0]["passed"] and "4 Monte Carlo SE" in rows[0]["tolerance"]
    near = study.Case("nums.find_median", "a Monte Carlo check", "made-up", "made-up",
                      ours="""
                          {"share": 0.50, "share MCSE": 0.006}
                      """,
                      parent="""
                          {"share": 0.52}
                      """, parent_label="an exact limit", parent_tolerance=report.MCSE)
    assert [r["passed"] for r in report.check_case(near)] == [True]
    missing = study.Case("nums.find_median", "a Monte Carlo check", "made-up", "made-up",
                         ours="""
                             {"share": 0.50}
                         """,
                         parent="""
                             {"share": 0.50}
                         """, parent_label="no standard error", parent_tolerance=report.MCSE)
    assert [r["passed"] for r in report.check_case(missing)] == [False]


def test_an_r_difference_is_explained_only_when_r_on_simplydata_rules_agrees():
    """r_explained=(suffix, reason): R also gives "<name><suffix>", worked out on simplydata's rules (the Oslo case:
    R on IANA's main data). Only when every such twin is simplydata's number is a difference explained."""
    suffix = " [R on IANA's main data]"
    case = study.Case("table.change_time_zone_in", "an explained difference", "made-up", "made-up", ours="",
                      r_explained=(suffix, "time-zone data: a stated reason"))
    ours = {"summer": 6.0, "sum": 240075.0}
    theirs = {"summer": 12.0, "sum": 238530.0}

    def compared(twins):
        return report._compared(case, ours, {**theirs, **twins}, "R", 0.0, case.r_explained)

    rows = compared({"summer" + suffix: 6.0, "sum" + suffix: 240075.0})
    assert [r["name"] for r in rows] == ["summer", "sum"]  # the twins are not compared themselves
    assert all(r["passed"] and r["explained"] == "time-zone data: a stated reason" for r in rows)
    assert report._status(rows[0]).startswith("explained difference – time-zone data")
    for twins in ({"summer" + suffix: 6.0, "sum" + suffix: 1.0},              # one twin differs
                  {"summer" + suffix: 6.0},                                    # one twin missing
                  {"summer" + suffix: float("nan"), "sum" + suffix: float("nan")},  # R's guard gave NA
                  {}):
        assert not any(r["passed"] or r["explained"] for r in compared(twins)), twins
    same = report._compared(case, ours, {**ours, "summer" + suffix: 0.0}, "R", 0.0, case.r_explained)
    assert all(r["passed"] and not r["explained"] for r in same)  # nothing differs: a plain pass


def test_tables_from_gpl_and_lgpl_r_packages_are_not_stored():
    """DATA_LICENSES.md: copies of data from GPL or LGPL R packages are read from the installed package instead."""
    r_data = study._r_data()
    for key in r_data.TABLES:
        assert not (VALIDATION / "data" / f"{key}.csv").exists(), key
    assert not (VALIDATION / "data" / "bioequivalence_reference.csv").exists()
    assert not (VALIDATION / "data" / "jobs_ii.csv").exists()
    for name, key in study.R_TABLES.items():
        d = study.DATASETS[name]
        assert d.file == "" and "read from the installed R package" in d.licence, name
        assert name in study.R_DATA, name
    assert set(study.R_TABLES.values()) == set(r_data.TABLES) - set(r_data.PRACTICE), "every table is read by a dataset"
    for d in study.DATASETS.values():
        assert d.file.removesuffix(".csv") not in r_data.TABLES, d.name


def test_tables_read_from_r_have_their_columns_and_rows(needs_r):
    sizes = {"sleep": (20, 3), "mtcars": (32, 12), "verbagg": (7584, 8), "nmes1988": (4406, 7), "lung": (228, 5),
             "mgus2": (1384, 5), "apistrat": (200, 10), "lalonde": (614, 9), "galton_peas": (7, 3)}
    r_data = study._r_data()
    for key, shape in sizes.items():
        if not r_data.ready(key):
            if os.environ.get("SIMPLYDATA_REQUIRE_R") == "1":
                pytest.fail(f"SIMPLYDATA_REQUIRE_R=1 but the R package for {key} is missing")
            continue
        table = r_data.read(key)
        assert table.shape == shape, key
    mtcars = r_data.read("mtcars")
    assert list(mtcars.columns[:3]) == ["model", "mpg", "cyl"] and mtcars["cyl"].dtype.kind == "i"
    assert mtcars.loc[0, "model"] == "Mazda RX4" and mtcars.loc[0, "mpg"] == 21.0


def test_readme_counts_of_the_study_are_true():
    """validation/README.md says how many cases, datasets and words the study has: counted, not written by hand."""
    import re

    from simplydata import learn
    from simplydata._underneath import UNDERNEATH

    text = " ".join((VALIDATION / "README.md").read_text(encoding="utf-8").split())
    kinds = {k: sum(1 for c in study.CASES if c.kind == k) for k in ("published", "real data", "made-up",
                                                                     "closed form")}
    datasets = {c.dataset for c in study.CASES} - {"made-up"}
    assert sum(kinds.values()) == len(study.CASES), "every case is of one of the kinds the README names"
    assert f"The other {kinds['closed form']} are closed-form checks" in text
    found = re.search(r"The study now has (\d+) cases on (\d+) datasets \((\d+) with a published or certified answer, "
                      r"(\d+) compared with the parent package and R, (\d+) made-up edge cases\)", text)
    assert found, "the sentence with the study's counts is missing from validation/README.md"
    assert tuple(map(int, found.groups())) == (len(study.CASES), len(datasets), kinds["published"],
                                               kinds["real data"], kinds["made-up"])
    no_data = sum(1 for c in study.CASES if c.dataset == "checks against R (no published example)")
    assert f"{no_data} of the {kinds['real data']} are simulation and formula checks against R that use no data at "            f"all; the other {kinds['real data'] - no_data} run on real data" in text
    words = {c.word for c in study.CASES}
    options = {(c.word, c.option) for c in study.CASES}
    assert f"They cover {len(words)} words, or {len(options)} words and options" in text
    assert f"{kinds['made-up']} of the {len(study.CASES)} cases, each labelled" in text
    all_words = [k for _, keys in learn.GROUPS for k in keys if learn._kind(k) != "option"]
    with_entry = {k.split(" ")[0] for k in UNDERNEATH} & set(all_words)  # words only, not show= and error=
    assert f"For {len(with_entry)} of simplydata's {len(all_words)} words ({len(UNDERNEATH)} entries" in text
    tables = [getattr(e, "data", None) for e in UNDERNEATH.values()]
    from simplydata.data import EXAMPLES

    made_up = sum(1 for t in tables if t and (t == "made-up" or "MADE-UP" in EXAMPLES.get(t, ("REAL",))[0]
                                              or "made-up" in EXAMPLES.get(t, ("REAL",))[0].lower()))
    real = sum(1 for t in tables if t in EXAMPLES) - sum(1 for t in tables if t in EXAMPLES and (
        "MADE-UP" in EXAMPLES[t][0] or "made-up" in EXAMPLES[t][0].lower()))
    none = sum(1 for t in tables if not t)
    assert real == 0, "every practice table is made up (DATA_LICENSES.md)"
    assert f"{made_up} of the {len(UNDERNEATH)} run on made-up practice tables (all practice tables are made up; " \
           f"{none} need no table)" in text
