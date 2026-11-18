"""Build simplydata's reliability report: every check, its reference, its tolerance and whether it passed.

    python validation/make_report.py                 # write validation/report.md
    python validation/make_report.py --out x.md      # write it somewhere else
    python validation/make_report.py --check         # check only: exit code 1 if any check fails; the
                                                     # report goes to the system's temporary folder (or --out)
    python validation/make_report.py --check --require-r   # and a skipped R part counts as a failure

SIMPLYDATA_REQUIRE_R=1 does the same as --require-r (CI sets it on the setups that have R).

Two kinds of check go into the report:

1. Published and real data (validation/cases.py): a word runs on real data, and what it gives is
   compared with the published answer (NIST certified values, numbers printed in the paper), with the
   parent package called directly (NumPy, pandas, SciPy, seaborn), and with R where R is installed.
2. The same underneath (src/simplydata/_underneath/): every "same underneath" box of the manual is run
   next to its word and compared, as tests/test_underneath.py does.

R parts are skipped (and say so) where R, rpy2 or the R package is missing.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import importlib.metadata
import importlib.util
import math
import os
import platform
import sys
import textwrap
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def _load_cases():
    """validation/cases.py, loaded by its path under a name of its own (nothing is added to sys.path)."""
    name = "simplydata_validation_cases"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE / "cases.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses look the module up while it loads
    spec.loader.exec_module(module)
    return module


study = _load_cases()

PACKAGES = ("simplydata", "pandas", "polars", "narwhals", "numpy", "scipy", "statsmodels", "matplotlib", "seaborn",
            "rpy2")


# ---------------------------------------------------------------- the setup
def versions() -> dict[str, str]:
    """The versions the report ran with: simplydata's from the module that was imported (and where it is),
    the others from their installed metadata."""
    import simplydata

    here = Path(simplydata.__file__).resolve().parent
    where = "src/simplydata of this copy" if here == (ROOT / "src" / "simplydata").resolve() else "the installed package"
    found = {"simplydata": f"{simplydata.__version__} (imported from {where})"}
    for name in PACKAGES[1:]:
        try:
            found[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            found[name] = "not installed"
    found["R"] = r_version() or "not available"
    return found


def r_version() -> str | None:
    if os.environ.get("SIMPLYDATA_NO_R") == "1":
        return None
    try:
        from simplydata._r import r_call, r_ready

        if not r_ready():
            return None
        return str(np.atleast_1d(r_call("R.version.string"))[0]).replace("R version ", "")
    except Exception:  # noqa: BLE001 - no R is a normal setup
        return None


def r_ready(packages=()) -> bool:
    if os.environ.get("SIMPLYDATA_NO_R") == "1":
        return False
    try:
        from simplydata._r import r_ready as ready

        return ready(tuple(packages))
    except Exception:  # noqa: BLE001
        return False


# ---------------------------------------------------------------- running a case
def run(code: str, data):
    """Run code with data, sdata, np and pd; give back the dict its last line makes."""
    import contextlib
    import io

    from simplydata._underneath.check import run_python

    namespace = {"data": data, "np": np, "pd": pd}
    with contextlib.redirect_stdout(io.StringIO()), warnings.catch_warnings():
        warnings.simplefilter("ignore")
        value, _, _ = run_python(textwrap.dedent(code).strip("\n"), namespace)
    import matplotlib.pyplot as plt

    plt.close("all")
    return {k: _number(v) for k, v in value.items()}


def run_r(code: str, data, packages) -> dict:
    from simplydata._r import r_call

    columns = {} if data is None else {c: data[c].to_numpy() for c in data.columns}
    found = r_call(textwrap.dedent(code).strip("\n"), packages=tuple(packages), what="a validation case", **columns)
    return {k: _number(v) for k, v in found.items()}


def _number(v) -> float:
    return float(np.asarray(v, dtype=float).reshape(-1)[0])


def lre(value: float, reference: float) -> float:
    """Log relative error: how many significant digits agree (15 when they are the same double)."""
    if value == reference:
        return 15.0
    if reference == 0:
        return min(15.0, -math.log10(abs(value)))
    return min(15.0, -math.log10(abs(value - reference) / abs(reference)))


MIN_LRE = 9.0  # digits that must agree with a NIST certified value (every set used, NumAcc4's higher difficulty too)


def check_case(case) -> list[dict]:
    """One row per number compared: simplydata against each reference."""
    rows = []
    needs_r_data = study.DATASETS[case.dataset].file == "" and case.dataset == "aSAH (pROC)"
    if needs_r_data and not r_ready(("pROC",)):
        return [_skipped(case, "R with pROC (the data come from pROC)")]
    data = None if case.dataset in ("made-up", "standard normal table") else study.load(case.dataset)
    try:
        ours = run(case.ours, data)
    except Exception as error:  # noqa: BLE001 - a crash is a failed check, reported
        return [dict(word=case.word, case=case.title, dataset=case.dataset, kind=case.kind, name="(run)",
                     reference="simplydata", ours=float("nan"), theirs=float("nan"), tolerance="runs",
                     passed=False, skipped="", note=f"simplydata stopped: {error}")]
    for name, (value, tolerance, source) in case.published.items():
        if name not in ours:
            rows.append(_missing(case, name, source))
            continue
        got = ours[name]
        if tolerance == "lre":
            digits = lre(got, value)
            rows.append(_row(case, name, source, got, value, f"at least {MIN_LRE:.0f} digits (LRE {digits:.1f})",
                             digits >= MIN_LRE))
        else:
            why = "" if source == "exact" else " (printed rounding)"
            rows.append(_row(case, name, source, got, value, f"within {tolerance:g}{why}",
                             abs(got - value) <= tolerance))
    if case.parent:
        theirs = run(case.parent, data)
        for name, value in theirs.items():
            if name not in ours:
                rows.append(_missing(case, name, case.parent_label))
                continue
            rows.append(_row(case, name, case.parent_label, ours[name], value,
                             _relative(case.parent_tolerance), _close(ours[name], value, case.parent_tolerance)))
    if case.r:
        if not r_ready(case.r_packages):
            rows.append(_skipped(case, "R" + (" with " + ", ".join(case.r_packages) if case.r_packages else "")))
        else:
            theirs = run_r(case.r, data, case.r_packages)
            for name, value in theirs.items():
                if name not in ours:
                    rows.append(_missing(case, name, "R"))
                    continue
                rows.append(_row(case, name, "R", ours[name], value, _relative(case.r_tolerance),
                                 _close(ours[name], value, case.r_tolerance)))
    return rows


def _relative(tol: float) -> str:
    return "exact" if tol == 0 else f"relative {tol:g}"


def _close(a: float, b: float, tol: float) -> bool:
    return a == b or math.isclose(a, b, rel_tol=tol, abs_tol=1e-300 if tol == 0 else 1e-12)


def _row(case, name, reference, ours, theirs, tolerance, passed) -> dict:
    return dict(word=case.word, case=case.title, dataset=case.dataset, kind=case.kind, name=name,
                reference=reference, ours=float(ours), theirs=float(theirs), tolerance=tolerance,
                passed=bool(passed), skipped="", note="")


def _missing(case, name: str, reference: str) -> dict:
    """A reference gives a number the simplydata side does not: a failed check, never a silent gap."""
    row = _row(case, name, reference, float("nan"), float("nan"), "", False)
    row["note"] = "the simplydata code gives no number with this name"
    return row


def _skipped(case, what: str) -> dict:
    return dict(word=case.word, case=case.title, dataset=case.dataset, kind=case.kind, name="(all)",
                reference=what, ours=float("nan"), theirs=float("nan"), tolerance="", passed=False,
                skipped=f"needs {what}, which is not installed here", note="")


def underneath_rows() -> list[dict]:
    from simplydata._underneath import UNDERNEATH
    from simplydata._underneath.check import check_entry

    rows = []
    for entry in UNDERNEATH.values():
        if entry.uses_r and not r_ready(entry.r_packages):
            rows.append(dict(word=entry.word, library=" + ".join(entry.code), engine="-", compare=entry.compare,
                             tolerance=entry.tolerance, passed=False,
                             skipped="needs R with " + ", ".join(entry.r_packages), differences=[]))
            continue
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()), warnings.catch_warnings():
            warnings.simplefilter("ignore")
            outcomes = check_entry(entry)
        for o in outcomes:
            rows.append(dict(word=o.word, library=o.library, engine=o.engine, compare=o.compare,
                             tolerance=o.tolerance, passed=o.passed, skipped=o.skipped, differences=o.differences))
    return rows


# ---------------------------------------------------------------- the report
def _status(row) -> str:
    return "skipped" if row["skipped"] else ("pass" if row["passed"] else "**FAIL**")


def _fmt(v: float) -> str:
    return "" if isinstance(v, float) and math.isnan(v) else f"{v:.15g}"


def _md(text: str) -> str:
    return str(text).replace("|", "\\|")


def report(case_rows: list[dict], box_rows: list[dict], setup: dict, when: str) -> str:
    from simplydata._underneath import COMPARE_KINDS, UNDERNEATH

    all_rows = case_rows + box_rows
    passed = sum(1 for r in all_rows if r["passed"] and not r["skipped"])
    failed = sum(1 for r in all_rows if not r["passed"] and not r["skipped"])
    skipped = sum(1 for r in all_rows if r["skipped"])
    out = [
        "# simplydata reliability report",
        "",
        f"Made by `python validation/make_report.py` on {when}. Generated: do not edit by hand.",
        "",
        "Each simplydata word is run on real, published data and compared with the published answer, with the "
        "package simplydata uses underneath called directly, and with R. Each \"same underneath\" box of the "
        "manual is run next to its word and compared too. How it works, and the datasets with their licences: "
        "[validation/README.md](README.md).",
        "",
        f"**{passed} checks passed, {failed} failed, {skipped} skipped** (skipped: R or an R package is not "
        "installed on this computer).",
        "",
        "## Setup",
        "",
        "| | |",
        "|---|---|",
        f"| system | {platform.system()} {platform.release()} ({platform.machine()}) |",
        f"| Python | {platform.python_version()} |",
    ]
    out += [f"| {name} | {version} |" for name, version in setup.items()]
    out += ["", "## 1. Published and real data", "",
            "Kinds: *published* = real data with a published or certified answer; *real data* = real data, "
            "compared with the parent package and R; *made-up* = a made-up edge case (empty cells, no rows left, "
            "an exact line) that no real dataset tests.", ""]
    words = list(dict.fromkeys(r["word"] for r in case_rows))
    for word in words:
        out.append(f"### `{word}`")
        out.append("")
        for title in dict.fromkeys(r["case"] for r in case_rows if r["word"] == word):
            rows = [r for r in case_rows if r["word"] == word and r["case"] == title]
            first = rows[0]
            out.append(f"**{_md(title)}** ({first['kind']}; data: {_md(first['dataset'])})")
            out.append("")
            out.append("| number | compared with | simplydata | reference | tolerance | result |")
            out.append("|---|---|---|---|---|---|")
            for r in rows:
                if r["skipped"]:
                    out.append(f"| {r['name']} | {_md(r['reference'])} | | | | skipped: {_md(r['skipped'])} |")
                    continue
                result = _status(r) + (f" ({_md(r['note'])})" if r["note"] else "")
                out.append(f"| {_md(r['name'])} | {_md(r['reference'])} | {_fmt(r['ours'])} | {_fmt(r['theirs'])} "
                           f"| {r['tolerance']} | {result} |")
            case = next(c for c in study.CASES if c.word == word and c.title == title)
            if case.note:
                out += ["", f"Note: {_md(case.note)}"]
            out.append("")
    out += ["## 2. The same underneath (the manual's boxes)", "",
            "Each box's library code is run next to the simplydata word and compared. Table words run on a "
            "pandas and on a Polars table.", "",
            "| word | compared with | table | how | tolerance | result |",
            "|---|---|---|---|---|---|"]
    for r in box_rows:
        result = _status(r)
        if r["skipped"]:
            result += f": {_md(r['skipped'])}"
        elif r["differences"]:
            result += ": " + _md("; ".join(r["differences"]))
        out.append(f"| `{r['word']}` | {_md(r['library'])} | {r['engine']} | {r['compare']} | "
                   f"relative {r['tolerance']:g} | {result} |")
    out += ["", "How each kind is compared:", ""]
    out += [f"- **{kind}**: {what}" for kind, what in COMPARE_KINDS.items() if kind != "none"]
    out += ["", "## Choices simplydata makes", "",
            "Where simplydata's default differs from the package underneath, it is listed here, so a difference "
            "is never hidden. The manual shows each one as a numbered mark in the code.", ""]
    for entry in UNDERNEATH.values():
        for i, choice in enumerate(entry.choices, start=1):
            out.append(f"- `{entry.word}` ({i}): {_md(choice)}")
    out += ["", "## Datasets", "", "| dataset | what | source | licence |", "|---|---|---|---|"]
    used = list(dict.fromkeys(c.dataset for c in study.CASES))
    for name in used:
        d = study.DATASETS[name]
        link = f"[{_md(d.name)}]({d.url})" if d.url else _md(d.name)
        out.append(f"| {link} | {_md(d.what)} | {_md(d.source)} | {_md(d.licence)} |")
    return "\n".join(out) + "\n"


def build(require_r: bool = False) -> tuple[str, int, int]:
    """(report text, failed checks, skipped checks); with require_r a skipped R part also counts as failed."""
    case_rows = [row for case in study.CASES for row in check_case(case)]
    box_rows = underneath_rows()
    when = _dt.date.today().isoformat()
    text = report(case_rows, box_rows, versions(), when)
    rows = case_rows + box_rows
    failed = sum(1 for r in rows if not r["passed"] and not r["skipped"])
    skipped = sum(1 for r in rows if r["skipped"])
    return text, failed + (skipped if require_r else 0), skipped


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build simplydata's reliability report.")
    parser.add_argument("--out", help="where to write the report (normally validation/report.md; with --check, "
                                      "the system's temporary folder)")
    parser.add_argument("--check", action="store_true", help="exit with code 1 if any check fails")
    parser.add_argument("--require-r", action="store_true", help="a skipped R part counts as a failure")
    args = parser.parse_args(argv)
    try:
        import simplydata  # noqa: F401  (installed, or run from a checkout)
    except ImportError:  # pragma: no cover - a checkout without pip install -e
        sys.path.insert(0, str(ROOT / "src"))
    import tempfile

    import matplotlib

    matplotlib.use("Agg")
    require_r = args.require_r or os.environ.get("SIMPLYDATA_REQUIRE_R") == "1"
    if args.out:
        out = Path(args.out)
    elif args.check:
        out = Path(tempfile.gettempdir()) / "simplydata_reliability_report.md"
    else:
        out = HERE / "report.md"
    text, failed, skipped = build(require_r)
    out.write_text(text, encoding="utf-8", newline="\n")
    note = f" ({skipped} skipped, counted as failed because R is required)" if require_r and skipped else ""
    print(f"Wrote {out}: {failed} failed{note}" if failed else f"Wrote {out}: every check passed or was skipped")
    return 1 if (failed and args.check) else 0


if __name__ == "__main__":
    sys.exit(main())
