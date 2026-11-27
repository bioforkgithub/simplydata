"""The manual chapter "From pandas (and Polars) to simplydata" (docs/manual/from_pandas.tex) is written by hand: every
example in it runs, uses today's words, and the chapter is part of the manual."""

import contextlib
import importlib.util
import io
import re
from pathlib import Path

import pytest

import simplydata as sdata
from simplydata import learn

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "docs" / "manual" / "from_pandas.tex"
TEXT = CHAPTER.read_text(encoding="utf-8")
BLOCK = re.compile(r"(?:% needs: (?P<needs>\w+)\n)?\\begin\{lstlisting\}\[style=py\]\n(?P<code>.*?)\\end\{lstlisting\}",
                   re.S)


def _examples():
    found = []
    for m in BLOCK.finditer(TEXT):
        section = re.findall(r"\\unsection\{[^}]*\}\{([^}]*)\}", TEXT[:m.start()])
        found.append(pytest.param(m.group("code"), m.group("needs"),
                                  id=f"{section[-1] if section else 'start'}-{len(found) + 1}"))
    return found


EXAMPLES = _examples()


def test_the_chapter_has_its_examples():
    assert len(EXAMPLES) >= 40


@pytest.mark.parametrize("code, needs", EXAMPLES)
def test_every_example_in_the_chapter_runs(code, needs, tmp_path, monkeypatch):
    if needs:
        pytest.importorskip(needs)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SIMPLYDATA_NO_CITE_LIST", "1")
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        exec(compile("import simplydata as sdata\n" + code, "from_pandas.tex", "exec"), {"__name__": "__chapter__"})
    out = printed.getvalue()
    assert "is now called" not in out, "the chapter teaches an old name:\n" + out
    assert "old name" not in out.lower(), out


def test_the_simplydata_words_in_the_chapter_are_todays_words():
    """table.<word>( and sdata.<word>( in the boxes and in \\code{...} name current words, never old names."""
    words = {learn._word(k) for k in learn._all_keys()}
    text = TEXT.replace("\\_", "_")
    tables = {"table"} | set(re.findall(r"\b(\w+) = (?:sdata\.(?:get_example|table)|clean)\(", text))
    tables |= set(re.findall(r"\b(\w+) = \w+\.(?:find_\w+|run_sql)\(", text))  # the new table of a find_ word
    calls = {(name, word) for name, word in re.findall(r"\b(\w+)\.(\w+)\(", text) if name in tables | {"sdata"}}
    unknown = sorted(f"{name}.{word}" for name, word in calls
                     if word not in words and not (name == "sdata" and word in dir(sdata)))
    assert not unknown, unknown
    assert len({word for _, word in calls}) > 50


def test_the_chapter_links_to_both_official_guides_and_copies_neither():
    links = re.findall(r"\\href\{([^}]*)\}", TEXT)
    assert sum("pandas.pydata.org/docs/user_guide/" in link for link in links) >= 15
    assert sum("docs.pola.rs/user-guide/" in link for link in links) >= 12
    assert all(link.startswith("https://") for link in links)


@pytest.mark.parametrize("task", [
    # the 14 tasks the tables design leaves out (to pandas and Polars, or to another phase)
    "to\\_numpy", "memory\\_usage", "loc[lambda d: ...]", "sort\\_index", "groupby().apply(f)", "corr",
    "add(other, fill\\_value=0)", "Duplicate", "cat.codes", "to\\_period", "set\\_index", "Lazy API",
    "to\\_numeric(downcast=)", "pipe(f)",
    # the six gaps of the API audit of pandas 3.1.1 and Polars 2.1.0
    "The different values of a column", "Different measures for different columns", "The next value",
    "A yes/no column from a text match", "Join the text of each group", "A table for a report",
])
def test_the_chapter_covers_the_left_out_tasks_and_the_audit_gaps(task):
    assert task in TEXT, task


def test_the_chapter_is_in_the_manual():
    spec = importlib.util.spec_from_file_location("make_manual", ROOT / "docs" / "make_manual.py")
    make_manual = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(make_manual)
    tex = make_manual.make()
    assert r"\input{from_pandas}" in tex
    assert tex.index(r"\input{ideas}") < tex.index(r"\input{from_pandas}") < tex.index(r"\part{Solutions}")


def test_the_pointers_name_the_chapter_that_exists():
    from simplydata._other_names import OTHER_NAMES

    named = {w for kind in OTHER_NAMES.values() for w in kind.values() if "manual chapter" in w}
    assert named and all('"From pandas (and Polars) to simplydata"' in w for w in named)
    assert r"\unchapter{From pandas (and Polars) to simplydata}" in TEXT
