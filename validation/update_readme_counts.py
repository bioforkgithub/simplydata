"""Write the generated numbers of README.md and docs/what_simplydata_handles.md from the code,
validation/report.md and count_reduction.py.

    python validation/update_readme_counts.py           # update both files
    python validation/update_readme_counts.py --check   # exit 1 when either is out of date

The numbers it writes are the ones tests/test_readme_handles.py compares (test_summary_counts_match_the_code,
test_reduction_table_matches_the_code, test_words_compared_in_the_reliability_study_match_the_report): the words,
groups and options, the reliability checks passed and the words the study compares (from validation/report.md, so
run validation/make_report.py first), and the lines and calls of the "same underneath" tasks. The GitHub workflow rebuild-docs.yml runs it after rebuilding the report. Everything else in the README is
written by hand.
"""

from __future__ import annotations

import importlib.util
import inspect
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
HANDLES = ROOT / "docs" / "what_simplydata_handles.md"
FILES = [README, HANDLES]
sys.path.insert(0, str(ROOT / "src"))

from simplydata import learn  # noqa: E402


def _options_of(func) -> list[str]:
    """The options of one word: its parameters with a default (the same rule as the README test)."""
    out = []
    for p in inspect.signature(func).parameters.values():
        if p.name == "self" or p.kind is p.VAR_KEYWORD or (p.kind is p.VAR_POSITIONAL and p.name == "extra"):
            continue
        if p.kind is not p.VAR_POSITIONAL and p.default is not p.empty:
            out.append(p.name)
    return out


def counts() -> dict:
    words = sum(1 for _, keys in learn.GROUPS for key in keys if learn._kind(key) != "option")
    options = {opt for _, func in learn._words_with_options() if func is not None for opt in _options_of(func)}
    report = (ROOT / "validation" / "report.md").read_text(encoding="utf-8")
    checks = int(re.search(r"\*\*(\d+) checks passed", report).group(1))
    # the words the study compares: named in part 1's headings or part 2's table (as the README test counts them)
    part1 = report[report.index("## 1."):report.index("## 2.")]
    part2 = report[report.index("## 2."):report.index("## Choices")]
    named = set(re.findall(r"^### `([^ `(]+)", part1, flags=re.M)) | set(re.findall(r"^\| `([^ `(]+)`", part2, flags=re.M))
    compared = sum(1 for _, keys in learn.GROUPS for key in keys if learn._kind(key) != "option" and key in named)
    spec = importlib.util.spec_from_file_location("count_reduction", ROOT / "validation" / "count_reduction.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {"words": words, "groups": len(learn.GROUPS), "options": len(options), "checks": checks,
            "compared": compared, "reduction": module.count()}


def update(texts: dict, c: dict) -> dict:
    r = c["reduction"]
    (ours_lines, lib_lines), (ours_calls, lib_calls) = r["lines"], r["calls"]
    ours_median, lib_median = r["median lines"]
    fewer = round(100 * (1 - ours_lines / lib_lines))
    swaps = [
        (r"\*\*\d+ words \(commands\) in \d+ groups, with \d+ different options",
         f"**{c['words']} words (commands) in {c['groups']} groups, with {c['options']} different options"),
        (r"checked by \d+ reliability checks", f"checked by {c['checks']} reliability checks"),
        (r"\d+ names: \d+ commands and \d+ options",
         f"{c['words'] + c['options']} names: {c['words']} commands and {c['options']} options"),
        (r"\d+ lines and \d+ function calls in the \d+ tasks",
         f"{lib_lines} lines and {lib_calls} function calls in the {r['tasks']} tasks"),
        (r"\(median [\d.]+ lines a task\); this library code",
         f"(median {lib_median:g} lines a task); this library code"),
        (r"\d+ lines and \d+ calls \(median [\d.]+ lines a task\), about \d+ % fewer lines",
         f"{ours_lines} lines and {ours_calls} calls (median {ours_median:g} lines a task), about {fewer} % fewer lines"),
        (r"compares \d+ of the\n\d+ words with the package underneath and with R \(\d+ checks\)",
         f"compares {c['compared']} of the\n{c['words']} words with the package underneath and with R ({c['checks']} checks)"),
        (r"The other \d+ words are not compared in the reliability study yet",
         f"The other {c['words'] - c['compared']} words are not compared in the reliability study yet"),
        (r"most words \(\d+ of the \d+ so far\)", f"most words ({c['compared']} of the {c['words']} so far)"),
    ]
    for pattern, new in swaps:
        found = 0
        for path in texts:
            texts[path], n = re.subn(pattern, lambda _m, new=new: new, texts[path])
            found += n
        if found != 1:
            raise SystemExit(f"README.md and {HANDLES.name}: expected one match of {pattern!r}, found {found}; "
                             "update this script")
    return texts


def main(argv: list[str]) -> int:
    old = {path: path.read_text(encoding="utf-8") for path in FILES}
    new = update(dict(old), counts())
    if "--check" in argv:
        print("up to date" if new == old else "the counts are out of date: run python validation/update_readme_counts.py")
        return 0 if new == old else 1
    changed = [path for path in FILES if new[path] != old[path]]
    for path in changed:
        path.write_text(new[path], encoding="utf-8", newline="\n")
        print(f"Updated the counts in {path.relative_to(ROOT).as_posix()}")
    if not changed:
        print("The counts are up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
