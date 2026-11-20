"""How much shorter is a task in simplydata than in the libraries underneath? Run: python validation/count_reduction.py

Counts the manual's "same underneath" boxes (simplydata._underneath.UNDERNEATH): for each task, the simplydata
code (Entry.ours) against the library code (Entry.code). When an entry has an "R" block, its blocks are one
program, so all of them count; otherwise the blocks are other ways to do the same job, so only the first counts.
Lines: not empty and not a comment. Calls: each name followed by "(". The library code in the boxes is the
bare minimum: it leaves out the plain-sentence result and the checks simplydata prints.
"""

from __future__ import annotations

import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from simplydata._underneath import UNDERNEATH  # noqa: E402

CALL = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*\s*\(")


def lines_of(code: str) -> list[str]:
    return [line for line in code.splitlines() if line.strip() and not line.strip().startswith("#")]


def library_code(entry) -> str:
    blocks = list(entry.code.values())
    return "\n".join(blocks) if "R" in entry.code else blocks[0]


def count() -> dict:
    ours_lines, lib_lines, ours_calls, lib_calls = [], [], [], []
    for entry in UNDERNEATH.values():
        ours, lib = lines_of(entry.ours), lines_of(library_code(entry))
        ours_lines.append(len(ours))
        lib_lines.append(len(lib))
        ours_calls.append(sum(len(CALL.findall(line)) for line in ours))
        lib_calls.append(sum(len(CALL.findall(line)) for line in lib))
    return {"tasks": len(ours_lines), "lines": (sum(ours_lines), sum(lib_lines)),
            "median lines": (statistics.median(ours_lines), statistics.median(lib_lines)),
            "calls": (sum(ours_calls), sum(lib_calls))}


def main() -> None:
    c = count()
    ours, lib = c["lines"]
    print(f"{c['tasks']} tasks (the manual's same-underneath boxes)")
    print(f"lines: {ours} with simplydata, {lib} with the libraries ({100 * (1 - ours / lib):.0f} % fewer); "
          f"median per task {c['median lines'][0]:g} vs {c['median lines'][1]:g}")
    print(f"function calls: {c['calls'][0]} with simplydata, {c['calls'][1]} with the libraries")


if __name__ == "__main__":
    main()
