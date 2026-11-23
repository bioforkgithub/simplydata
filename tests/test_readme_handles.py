"""What simplydata handles stays complete and true, and the motto is the same everywhere.

The README keeps a short "What simplydata handles" section (the counts and how much is checked); the full lists
are in docs/what_simplydata_handles.md. Required for every batch of new words: each R package simplydata runs (any
packages=(...) or r_packages=(...) in src) must be in that page's table of R packages it runs; each R package that
only the tests (conftest.R_PACKAGES) or the reliability study (validation/*.py) load must be in the table of
packages used only to check; each Python package of pyproject.toml must be in the Python table. The README
summary's counts of words, options, R packages and reliability checks must match the code.
"""

import inspect
import re
from pathlib import Path

from conftest import R_PACKAGES

from simplydata import learn

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
HANDLES_PAGE = "docs/what_simplydata_handles.md"
HANDLES = (ROOT / HANDLES_PAGE).read_text(encoding="utf-8")
MOTTO = ("Learn basic Python, and simplydata takes you from your first table to sound statistics, "
         "in plain words, with its results checked against the field's standard tools.")
OLD_MOTTO = "publication-ready"
# R's own packages come with R; they are not listed
R_BASE = {"base", "stats", "utils", "methods", "graphics", "grDevices", "splines", "grid", "tools", "parallel",
          "stats4", "tcltk", "datasets", "compiler"}
NAME = re.compile(r"^[A-Za-z][A-Za-z0-9.]*$")
TUPLE = re.compile(r'\(\s*((?:"[^"\n]+"\s*,\s*)*"[^"\n]+"\s*,?\s*)\)')
PACKAGES_CALL = re.compile(r"(?<![A-Za-z_])(?:r_)?packages\s*(?:=|\+=)\s*\(([^)]*)\)")
RUN_TABLE = ("R packages that simplydata runs", "R packages used only to check")
CHECK_TABLE = ("R packages used only to check", "## By task")
PYTHON_TABLE = ("Python packages:", "R packages that simplydata runs")


def _section(start: str, end: str, text: str = HANDLES) -> str:
    return text[text.index(start):text.index(end)]


def _names(text: str) -> set:
    return {n for n in re.findall(r'"([^"]+)"', text) if NAME.match(n)}


def _checking_packages() -> set:
    """Every R package the tests (conftest.R_PACKAGES) and the reliability study (validation/*.py) load."""
    found = set(R_PACKAGES)
    for path in (ROOT / "validation").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for group in re.findall(r"r_packages\s*=\s*\(([^)]*)\)", text):
            found |= _names(group)
        for group in re.findall(r'\(\(("[^"]+"(?:\s*,\s*"[^"]+")*),?\)\s*,', text):  # the datasets' R loaders
            found |= _names(group)
    return found - R_BASE


def _run_packages(known: set) -> set:
    """The R packages simplydata itself runs: every package in a packages=(...) or r_packages=(...) in src, and
    every tuple in src made only of known R package names (the tables of pair tests and of R refits)."""
    found = set()
    for path in (ROOT / "src" / "simplydata").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for group in PACKAGES_CALL.findall(text):
            found |= _names(group)
        for match in TUPLE.finditer(text):
            names = re.findall(r'"([^"]+)"', match.group(1))
            if names and all(n in known for n in names):
                found |= set(names)
    return found - R_BASE


def _first_column(start: str, end: str) -> set:
    rows = [line for line in _section(start, end).splitlines() if line.startswith("| ") and "---" not in line]
    return set(re.findall(r"[A-Za-z][A-Za-z0-9.-]*", " ".join(row.split("|")[1] for row in rows)))


def test_every_r_package_simplydata_runs_is_in_the_packages_table():
    run = _run_packages(_checking_packages())
    missing = sorted(run - _first_column(*RUN_TABLE), key=str.lower)
    assert not missing, f"add these R packages to the README's table of R packages simplydata runs: {missing}"
    assert {"lme4", "metafor", "vegan", "rstatix", "nnet"} <= run  # the scan finds both kinds of place
    assert f"{len(run)} R packages that it runs" in README


def test_every_r_package_used_only_for_checking_is_listed():
    checking = _checking_packages()
    run = _run_packages(checking)
    listed = _first_column(*CHECK_TABLE)
    missing = sorted((checking - run) - listed, key=str.lower)
    assert not missing, f"add these R packages to the README's table of packages used only to check: {missing}"
    assert f"and {len(checking - run)} more used only to check its answers" in README
    wrong = sorted(listed & run, key=str.lower)
    assert not wrong, f"simplydata runs these, so they belong in the table of R packages it runs: {wrong}"


def test_every_python_package_is_in_the_packages_table():
    import tomllib

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    wanted = list(project["dependencies"])
    for extra, packages in project["optional-dependencies"].items():
        if extra != "test":
            wanted += packages
    names = {re.split(r"[<>=!~\[ ]", w, maxsplit=1)[0].lower() for w in wanted}
    listed = {n.lower() for n in _first_column(*PYTHON_TABLE)}
    listed |= {n.removeprefix("python-") for n in listed}  # python-control is installed as "control"
    missing = sorted(names - listed)
    assert not missing, f"add these Python packages to the README's Python table: {missing}"
    assert f"{len(names)} Python packages" in README


def _options_of(func):
    out = []
    for p in inspect.signature(func).parameters.values():
        if p.name == "self" or p.kind is p.VAR_KEYWORD or (p.kind is p.VAR_POSITIONAL and p.name == "extra"):
            continue
        if p.kind is not p.VAR_POSITIONAL and p.default is not p.empty:
            out.append(p.name)
    return out


def test_summary_counts_match_the_code():
    words = sum(1 for _, keys in learn.GROUPS for key in keys if learn._kind(key) != "option")
    options = {opt for _, func in learn._words_with_options() if func is not None for opt in _options_of(func)}
    summary = _section("## What simplydata handles", "### Can I trust it?", README)
    assert f"**{words} words (commands) in {len(learn.GROUPS)} groups, with {len(options)} different options" in summary
    report = (ROOT / "validation" / "report.md").read_text(encoding="utf-8")
    checks = re.search(r"\*\*(\d+) checks passed", report).group(1)
    assert f"{checks} reliability checks" in summary


def test_handles_comes_before_the_philosophy():
    assert README.index("## What simplydata handles") < README.index("## Why simplydata exists")


def test_readme_starts_with_the_quick_start_and_links_the_full_lists():
    """A new user meets install and a quick start before the long parts; the long lists are one link away."""
    assert README.index("## Install") < README.index("## Quick start") < README.index("## Questions new users ask")
    assert README.index("## Quick start") < README.index("## What simplydata handles")
    assert f"({HANDLES_PAGE})" in _section("## What simplydata handles", "### Can I trust it?", README)
    for heading in ("## How much simplydata reduces the problem", "## Packages underneath", "## By task",
                    "## Across the sciences", "## The lessons, one by one"):
        assert heading in HANDLES, heading
        assert not re.search(rf"^#+ {re.escape(heading.lstrip('# '))}$", README, flags=re.M), f"{heading} moved to {HANDLES_PAGE}"


def test_motto_is_the_same_everywhere():
    import simplydata

    assert f"**{MOTTO}**" in README.split("## ", 1)[0]
    assert (simplydata.__doc__ or "").splitlines()[0] == MOTTO
    assert f'description = "{MOTTO}"' in (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert MOTTO in (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    assert MOTTO in (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    for script in ("make_manual.py", "make_dictionary.py", "make_30_days.py"):
        assert MOTTO in (ROOT / "docs" / script).read_text(encoding="utf-8"), script


def test_the_old_motto_is_gone():
    """The motto of before 2026-11-23 ("... to publication-ready statistics ...") is nowhere in the text files."""
    skip = {".git", "__pycache__", "build", "dist", ".pytest_cache"}
    found = []
    for path in ROOT.rglob("*"):
        if (path.suffix in {".md", ".py", ".toml", ".cff", ".tex", ".txt", ".yml", ".yaml", ".cfg", ".ipynb"}
                and not skip & set(path.relative_to(ROOT).parts) and path != Path(__file__).resolve()
                and path.is_file() and OLD_MOTTO in path.read_text(encoding="utf-8", errors="replace")):
            found.append(str(path.relative_to(ROOT)))
    assert not found, f"the old motto is still in: {found}"


def test_reduction_table_matches_the_code():
    import importlib.util

    spec = importlib.util.spec_from_file_location("count_reduction", ROOT / "validation" / "count_reduction.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    c = module.count()
    table = _section("## How much simplydata reduces the problem", "## Packages underneath")
    assert f"{c['lines'][1]} lines and {c['calls'][1]} function calls in the {c['tasks']} tasks" in table
    assert f"{c['lines'][0]} lines and {c['calls'][0]} calls" in table
    words = sum(1 for _, keys in learn.GROUPS for key in keys if learn._kind(key) != "option")
    options = {opt for _, func in learn._words_with_options() if func is not None for opt in _options_of(func)}
    assert f"{words + len(options)} names: {words} commands and {len(options)} options" in table


def test_words_compared_in_the_reliability_study_match_the_report():
    """The README says how many words the reliability study compares; count them in validation/report.md (the words
    named in its part 1 headings and its part 2 table), so the claim stays true when either changes."""
    words = [key for _, keys in learn.GROUPS for key in keys if learn._kind(key) != "option"]
    report = (ROOT / "validation" / "report.md").read_text(encoding="utf-8")
    part1 = report[report.index("## 1."):report.index("## 2.")]
    part2 = report[report.index("## 2."):report.index("## Choices")]
    named = set(re.findall(r"^### `([^ `(]+)", part1, flags=re.M)) | set(re.findall(r"^\| `([^ `(]+)`", part2, flags=re.M))
    compared = sum(1 for word in words if word in named)
    checks = re.search(r"\*\*(\d+) checks passed", report).group(1)
    assert f"compares {compared} of the\n{len(words)} words with the package underneath and with R ({checks} checks)" in README
    assert f"The other {len(words) - compared} words are not compared in the reliability study yet." in README
    assert f"most words ({compared} of the {len(words)} so far)" in README
