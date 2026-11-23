"""Write the generated numbers of README.md from the code, validation/report.md and count_reduction.py.

    python validation/update_readme_counts.py           # update README.md
    python validation/update_readme_counts.py --check   # exit 1 when README.md is out of date

The numbers it writes are the ones tests/test_readme_handles.py compares (test_summary_counts_match_the_code,
test_reduction_table_matches_the_code): the words, groups and options, the reliability checks passed (from
validation/report.md, so run validation/make_report.py first), and the lines and calls of the "same underneath"
tasks. The GitHub workflow rebuild-docs.yml runs it after rebuilding the report. Everything else in the README is
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
    spec = importlib.util.spec_from_file_location("count_reduction", ROOT / "validation" / "count_reduction.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {"words": words, "groups": len(learn.GROUPS), "options": len(options), "checks": checks,
            "reduction": module.count()}


def update(text: str, c: dict) -> str:
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
    ]
    for pattern, new in swaps:
        text, n = re.subn(pattern, lambda _m, new=new: new, text)
        if n != 1:
            raise SystemExit(f"README.md: expected one match of {pattern!r}, found {n}; update this script")
    return text


def main(argv: list[str]) -> int:
    old = README.read_text(encoding="utf-8")
    new = update(old, counts())
    if "--check" in argv:
        print("up to date" if new == old else "README.md counts are out of date: run python validation/update_readme_counts.py")
        return 0 if new == old else 1
    if new != old:
        README.write_text(new, encoding="utf-8", newline="\n")
        print("Updated the counts in README.md")
    else:
        print("README.md counts are up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
