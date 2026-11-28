"""The manual chapter "From SymPy to simplydata" (docs/manual/from_sympy.tex) is written by hand: every example in it
runs (SymPy through simplydata's helper, under its time limit), uses today's words, hands over to SymPy only after
as_sympy(), and the chapter is part of the manual, after the NumPy and SciPy chapter."""

import contextlib
import importlib.util
import io
import re
from pathlib import Path

import pytest

import simplydata as sdata
from simplydata import learn

pytest.importorskip("sympy")

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "docs" / "manual" / "from_sympy.tex"
TEXT = CHAPTER.read_text(encoding="utf-8")
BLOCK = re.compile(r"\\begin\{lstlisting\}\[style=py\]\n(?P<code>.*?)\\end\{lstlisting\}", re.S)
OBJECTS = {"formula", "grid", "flat", "sdata", "root", "third", "back", "slope", "area", "wave", "cosine", "moved"}


def _examples():
    found = []
    for m in BLOCK.finditer(TEXT):
        section = re.findall(r"\\unsection\{[^}]*\}\{([^}]*)\}", TEXT[:m.start()])
        found.append(pytest.param(m.group("code"), id=f"{section[-1] if section else 'start'}-{len(found) + 1}"))
    return found


EXAMPLES = _examples()


def test_the_chapter_has_its_examples():
    assert len(EXAMPLES) >= 10


@pytest.mark.parametrize("code", EXAMPLES)
def test_every_example_in_the_chapter_runs(code, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SIMPLYDATA_NO_CITE_LIST", "1")
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        exec(compile("import simplydata as sdata\n" + code, "from_sympy.tex", "exec"), {"__name__": "__chapter__"})
    out = printed.getvalue()
    assert "is now called" not in out, "the chapter teaches an old name:\n" + out


def test_the_simplydata_words_in_the_chapter_are_todays_words():
    """<object>.<word>( in the boxes and in \\code{...} names a current word, never an old name."""
    words = {learn._word(k) for k in learn._all_keys()}
    text = TEXT.replace("\\_", "_")
    calls = {(name, word) for name, word in re.findall(r"\b(\w+)\.(\w+)\(", text) if name in OBJECTS}
    unknown = sorted(f"{name}.{word}" for name, word in calls
                     if word not in words and not (name == "sdata" and word in dir(sdata)))
    assert not unknown, unknown
    assert len({word for _, word in calls}) > 25


def test_the_hand_over_lines_are_the_only_other_code():
    """Before the hand-over (as_sympy()), a box uses only simplydata words: no sp. or sympy. call."""
    for param in EXAMPLES:
        code = param.values[0]
        before = code.split(".as_sympy()")[0]
        assert not re.search(r"\b(sp|sympy)\.\w+", before), before
        assert "import sympy" not in before and "import pandas" not in code and "import numpy" not in code


def test_every_hand_over_comes_back_to_simplydata():
    for param in EXAMPLES:
        code = param.values[0]
        if ".as_sympy()" in code:
            assert "sdata.formula(str(" in code.split(".as_sympy()", 1)[1], code


def test_the_chapter_links_to_the_official_tutorial_and_copies_none():
    links = re.findall(r"\\href\{([^}]*)\}", TEXT)
    assert sum("docs.sympy.org/latest/tutorials/intro-tutorial/" in link for link in links) >= 10
    assert all(link.startswith("https://") for link in links)


TOPICS = ["first", "intro", "gotchas", "basic-operations", "printing", "simplification", "calculus", "solvers",
          "matrices", "left-out"]


@pytest.mark.parametrize("topic", TOPICS)
def test_the_chapter_follows_the_tutorial(topic):
    assert "}{from-sympy:" + topic + "}" in TEXT, topic


def test_the_topics_come_in_the_order_of_the_tutorial():
    assert re.findall(r"\\unsection\{[^}]*\}\{from-sympy:([^}]*)\}", TEXT) == TOPICS


@pytest.mark.parametrize("job", ["srepr", "trigsimp", "rref", "sympy.physics", "codegen", "legendre"])
def test_the_chapter_names_the_jobs_left_to_sympy(job):
    assert job in TEXT.replace("\\_", "_"), job


@pytest.mark.parametrize("word", ["solve_for([1, 0], exactly=True)", "find_sum_of_series", "group_by_powers_of"])
def test_the_chapter_teaches_todays_exact_words(word):
    assert word in TEXT.replace("\\_", "_"), word


def test_the_chapter_is_in_the_manual():
    spec = importlib.util.spec_from_file_location("make_manual", ROOT / "docs" / "make_manual.py")
    make_manual = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(make_manual)
    tex = make_manual.make()
    assert r"\part{From SymPy}\label{part:from-sympy}" in tex
    assert tex.index(r"\input{from_numpy}") < tex.index(r"\input{from_sympy}") < tex.index(r"\part{Solutions}")
    assert r"\unchapter{From SymPy to simplydata}" in TEXT


def test_the_lines_are_short():
    long = [line for line in TEXT.splitlines() if len(line) > 120]
    assert not long, long
