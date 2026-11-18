"""The reliability study (validation/): real, published data give the published answers.

Each case of validation/cases.py runs a word on real data and compares it with the published or certified
answer, the parent package and R (skipped where R is missing, except in CI with SIMPLYDATA_REQUIRE_R=1).
"""

import importlib.util
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "validation"


def _load(name):
    sys.path.insert(0, str(VALIDATION))
    try:
        spec = importlib.util.spec_from_file_location(name, VALIDATION / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(VALIDATION))


report = _load("make_report")
study = report.study


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
        assert case.kind in ("published", "real data", "made-up"), case.kind
        if case.kind == "published":
            assert case.published, f"{case.title}: a published case names its published answer"
        if case.kind == "made-up":
            assert case.dataset == "made-up", case.title
        assert case.published or case.parent or case.r, case.title


def test_the_ten_trial_words_have_a_case_on_real_data():
    from simplydata._underneath import UNDERNEATH

    real = {c.word for c in study.CASES if c.kind != "made-up"}
    assert set(UNDERNEATH) <= real


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
    skipped = [r for r in rows if r["skipped"]]
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
