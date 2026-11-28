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
            "control", "rpy2")


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

    namespace = {"data": data, "np": np, "pd": pd, "_rows": study._rows}
    with contextlib.redirect_stdout(io.StringIO()), warnings.catch_warnings():
        warnings.simplefilter("ignore")
        value, _, _ = run_python(textwrap.dedent(code).strip("\n"), namespace)
    import matplotlib.pyplot as plt

    plt.close("all")
    return {k: _number(v) for k, v in value.items()}


def run_r(code: str, data, packages) -> dict:
    from simplydata._r import need_r, r_call

    columns = {} if data is None else {c: data[c].to_numpy() for c in data.columns}
    # the packages are checked, not attached: the cases call them by name (drc::drm), and an attached package
    # can hide base R functions from later calls (drc's gaussian(), SparseM's matrix functions, mcr's coef())
    need_r(tuple(packages), "a validation case")
    found = r_call(textwrap.dedent(code).strip("\n"), what="a validation case", **columns)
    return {k: _number(v) for k, v in found.items()}


def _number(v) -> float:
    return float(np.asarray(v, dtype=float).reshape(-1)[0])


def lre(value: float, reference: float) -> float:
    """Log relative error: how many significant digits agree (15 when they are the same double)."""
    if not math.isfinite(value):  # an empty or infinite answer agrees to no digits (min() would give 15 for NaN)
        return 0.0
    if value == reference:
        return 15.0
    if reference == 0:
        return min(15.0, -math.log10(abs(value)))
    return min(15.0, -math.log10(abs(value - reference) / abs(reference)))


MIN_LRE = 9.0  # digits that must agree with a NIST certified value (every set used, NumAcc4's higher difficulty too)


def _key(case) -> str:
    """The word, or the word and the option a case checks ("table.explain weights=")."""
    return f"{case.word} {case.option}" if case.option else case.word


def check_case(case) -> list[dict]:
    """One row per number compared: simplydata against each reference."""
    rows = []
    r_data = {"aSAH (pROC)": ("pROC",), **getattr(study, "R_DATA", {})}  # datasets read from an R package
    if case.dataset in r_data and not r_ready(r_data[case.dataset]):
        packages = ", ".join(r_data[case.dataset])
        return [_skipped(case, f"R with {packages} (the data come from {packages})")]
    if case.local_data and not os.environ.get(case.local_data):
        # data that may not be passed on (DATA_LICENSES.md): read only from a file the user names
        return [_skipped(case, f"the data file named by {case.local_data} (not shipped; see DATA_LICENSES.md)",
                         local=True)]
    if case.ours_r is not None and not r_ready(case.ours_r):
        return [_skipped(case, "R" + (" with " + ", ".join(case.ours_r) if case.ours_r else "")
                         + " (simplydata runs R for this option)")]
    data = None if case.dataset in ("made-up", "standard normal table", "closed form (no data)",
                                   "published special-function tables (no data)") else study.load(case.dataset)
    try:
        ours = run(case.ours, data)
    except Exception as error:  # noqa: BLE001 - a crash is a failed check, reported
        return [dict(word=_key(case), case=case.title, dataset=case.dataset, kind=case.kind, name="(run)",
                     reference="simplydata", ours=float("nan"), theirs=float("nan"), tolerance="runs",
                     passed=False, skipped="", note=f"simplydata stopped: {error}")]
    for name, (value, tolerance, source) in case.published.items():
        if name not in ours:
            rows.append(_missing(case, name, source))
            continue
        got = ours[name]
        if isinstance(tolerance, str) and tolerance.startswith("lre"):
            # "lre": MIN_LRE digits; "lre:6": 6 digits (NIST StRD nonlinear problems, judged at 6 digits as in
            # McCullough (1999), "Assessing the reliability of statistical software", The American Statistician 53)
            least = float(tolerance.split(":")[1]) if ":" in tolerance else MIN_LRE
            digits = lre(got, value)
            row = _row(case, name, source, got, value, f"at least {least:.0f} digits (LRE {digits:.1f})",
                       digits >= least)
            if not row["passed"] and name in case.explained:
                row.update(passed=True, explained="precision limit: " + case.explained[name])
            rows.append(row)
        else:
            # a closed form is worked out from the formula: its tolerance allows for floating point, not rounding
            why = (" (exact formula)" if case.kind == "closed form" else "" if str(source).startswith("exact")
                   else " (printed rounding)")
            rows.append(_row(case, name, source, got, value, f"within {tolerance:g}{why}",
                             abs(got - value) <= tolerance))
    if case.parent:
        theirs = run(case.parent, data)
        rows.extend(_compared(case, ours, theirs, case.parent_label, case.parent_tolerance))
    if case.r:
        if not r_ready(case.r_packages):
            rows.append(_skipped(case, "R" + (" with " + ", ".join(case.r_packages) if case.r_packages else "")))
        else:
            theirs = run_r(case.r, data, case.r_packages)
            rows.extend(_compared(case, ours, theirs, "R", case.r_tolerance, case.r_explained))
    return rows


MCSE = study.MONTE_CARLO  # "4 mcse", a Monte Carlo tolerance: within 4 Monte Carlo standard errors of the difference
MCSE_SUFFIX = " MCSE"


def _compared(case, ours: dict, theirs: dict, label: str, tolerance, explained: tuple = ()) -> list[dict]:
    """simplydata against one reference. A number tolerance is relative. The tolerance "4 mcse" is for a Monte Carlo
    answer checked against another generator or an exact limit: the difference must lie within 4 Monte Carlo
    standard errors, read from "<name> MCSE" in the reference's numbers (or in simplydata's, when the Monte Carlo
    error is simplydata's alone); those entries are not compared themselves.

    explained = (suffix, reason): the reference also works every number out on simplydata's rules and gives it as
    "<name><suffix>" (not compared itself). A number that differs is an explained difference only when every number
    of the case, worked out that way, is simplydata's own; otherwise it fails (_explain)."""
    suffix, reason = explained or ("", "")
    out = []
    for name, value in theirs.items():
        if name.endswith(MCSE_SUFFIX) or (suffix and name.endswith(suffix)):
            continue
        if name not in ours:
            out.append(_missing(case, name, label))
            continue
        if tolerance == MCSE:
            se = theirs.get(name + MCSE_SUFFIX, ours.get(name + MCSE_SUFFIX))
            if se is None or not se > 0:
                row = _row(case, name, label, ours[name], value, "4 Monte Carlo SE", False)
                row["note"] = f"no positive '{name}{MCSE_SUFFIX}' given"
                out.append(row)
                continue
            out.append(_row(case, name, label, ours[name], value, f"within 4 Monte Carlo SE ({4 * se:.3g})",
                            abs(ours[name] - value) <= 4 * se))
        else:
            out.append(_row(case, name, label, ours[name], value, _relative(tolerance),
                            _close(ours[name], value, tolerance)))
    if suffix and any(not row["passed"] for row in out):
        _explain(out, ours, theirs, suffix, reason, tolerance)
    return out


def _explain(rows: list[dict], ours: dict, theirs: dict, suffix: str, reason: str, tolerance) -> None:
    """Marks the differing rows as explained when the reference, on simplydata's rules, gives simplydata's numbers:
    every compared number must have its "<name><suffix>" twin, and each twin must agree with simplydata within the
    case's tolerance. One missing or differing twin and every differing row stays a failure."""
    same = all(row["name"] + suffix in theirs and row["name"] in ours
               and _close(ours[row["name"]], theirs[row["name"] + suffix], tolerance) for row in rows)
    if same:
        for row in rows:
            if not row["passed"]:
                row.update(passed=True, explained=reason)


def _relative(tol: float) -> str:
    return "exact" if tol == 0 else f"relative {tol:g}"


def _close(a: float, b: float, tol: float) -> bool:
    return a == b or math.isclose(a, b, rel_tol=tol, abs_tol=1e-300 if tol == 0 else 1e-12)


def _row(case, name, reference, ours, theirs, tolerance, passed) -> dict:
    return dict(word=_key(case), case=case.title, dataset=case.dataset, kind=case.kind, name=name,
                reference=reference, ours=float(ours), theirs=float(theirs), tolerance=tolerance,
                passed=bool(passed), skipped="", note="", explained="")


def _missing(case, name: str, reference: str) -> dict:
    """A reference gives a number the simplydata side does not: a failed check, never a silent gap."""
    row = _row(case, name, reference, float("nan"), float("nan"), "", False)
    row["note"] = "the simplydata code gives no number with this name"
    return row


def _skipped(case, what: str, local: bool = False) -> dict:
    """A case that cannot run here. local=True: it needs a data file that is not shipped (DATA_LICENSES.md) and
    that the user may name; such a skip is not a missing R part, so --require-r does not count it."""
    return dict(word=_key(case), case=case.title, dataset=case.dataset, kind=case.kind, name="(all)",
                reference=what, ours=float("nan"), theirs=float("nan"), tolerance="", passed=False,
                skipped=f"needs {what}, which is not " + ("given here" if local else "installed here"), note="",
                explained="", local=local)


def underneath_rows() -> list[dict]:
    from simplydata._underneath import UNDERNEATH
    from simplydata._underneath.check import check_entry

    rows = []
    for entry in UNDERNEATH.values():
        needed = tuple(dict.fromkeys(entry.r_packages + entry.ours_r))
        if entry.uses_r and not r_ready(needed):
            rows.append(dict(word=entry.key, library=" + ".join(entry.code), engine="-", compare=entry.compare,
                             tolerance=entry.tolerance, passed=False,
                             skipped="needs R with " + ", ".join(needed), differences=[]))
            continue
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()), warnings.catch_warnings():
            warnings.simplefilter("ignore")
            outcomes = check_entry(entry)
        for o in outcomes:
            rows.append(dict(word=entry.key, library=o.library, engine=o.engine, compare=o.compare,
                             tolerance=o.tolerance, passed=o.passed, skipped=o.skipped, differences=o.differences))
    return rows


# ---------------------------------------------------------------- the report
EXPLAINED = "explained difference"


def _status(row) -> str:
    if row["skipped"]:
        return "skipped"
    if row.get("explained"):
        return f"{EXPLAINED} – {row['explained']}"
    return "pass" if row["passed"] else "**FAIL**"


def _fmt(v: float) -> str:
    return "" if isinstance(v, float) and math.isnan(v) else f"{v:.15g}"


def _md(text: str) -> str:
    return str(text).replace("|", "\\|")


def report(case_rows: list[dict], box_rows: list[dict], setup: dict, when: str) -> str:
    from simplydata._underneath import COMPARE_KINDS, UNDERNEATH

    all_rows = case_rows + box_rows
    passed = sum(1 for r in all_rows if r["passed"] and not r["skipped"] and not r.get("explained"))
    explained = sum(1 for r in all_rows if r.get("explained"))
    failed = sum(1 for r in all_rows if not r["passed"] and not r["skipped"])
    skipped = sum(1 for r in all_rows if r["skipped"])
    local = sum(1 for r in all_rows if r.get("local"))
    out = [
        "# simplydata reliability report",
        "",
        f"Made by `python validation/make_report.py` on {when}. Generated: do not edit by hand.",
        "",
        "Each simplydata word is run on real, published data and compared with the published answer, with the "
        "package simplydata uses underneath called directly, and with R. Each \"same underneath\" box of the "
        "manual is run next to its word and compared too. How it works, and the datasets with their licences: "
        "[validation/README.md](README.md); which words are compared here, which in the separate test study "
        "(simplydata_tests) and which have nothing to compare: its section \"Which words are compared, and where\".",
        "",
        f"**{passed} checks passed, {explained} explained differences, {failed} failed, {skipped} skipped** "
        f"(skipped: R or an R package is not installed on this computer, or, for {local}, the data may not be "
        "passed on and no file was given; an explained difference falls short of its tolerance for a stated "
        "reason, a limit of precision or R reading a different copy of the time-zone data (R, on simplydata's "
        "rules, then gives simplydata's numbers), and is listed with that reason).",
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
            "an exact line) that no real dataset tests; *closed form* = no data at all: a word that makes "
            "something from a formula (a system, a wave, a window shape) checked against the answer worked out by "
            "hand from that formula (and against the parent package and R).", ""]
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
            case = next(c for c in study.CASES if _key(c) == word and c.title == title)
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
    nothing = [k for k, e in UNDERNEATH.items() if e.compare == "none"]
    if nothing:
        out += [f"- **none** ({len(nothing)} words: " + ", ".join(f"`{k}`" for k in nothing) + "): help, learning, "
                "undo and show-steps words. They print help, a lesson, the packages used or the steps taken, or put "
                "a table back as it was; they compute no number, so there is nothing to compare them with. Their box "
                "is run to show that it runs."]
    out += ["", "## Choices simplydata makes", "",
            "Where simplydata's default differs from the package underneath, it is listed here, so a difference "
            "is never hidden. The manual shows each one as a numbered mark in the code.", ""]
    for entry in UNDERNEATH.values():
        for i, choice in enumerate(entry.choices, start=1):
            out.append(f"- `{entry.key}` ({i}): {_md(choice)}")
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
    missing_r = sum(1 for r in rows if r["skipped"] and not r.get("local"))
    return text, failed + (missing_r if require_r else 0), skipped


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
