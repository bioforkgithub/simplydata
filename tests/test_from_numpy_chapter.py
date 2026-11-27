"""The manual chapter "From NumPy and SciPy to simplydata" (docs/manual/from_numpy.tex) is written by hand: every example
in it runs, uses today's words, hands over to NumPy only after as_numpy(), and the chapter is part of the manual,
after the matplotlib chapter."""

import contextlib
import importlib.util
import io
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pytest  # noqa: E402

import simplydata as sdata  # noqa: E402
from simplydata import learn  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "docs" / "manual" / "from_numpy.tex"
TEXT = CHAPTER.read_text(encoding="utf-8")
BLOCK = re.compile(r"\\begin\{lstlisting\}\[style=py\]\n(?P<code>.*?)\\end\{lstlisting\}", re.S)
OBJECTS = {"numbers", "grid", "block", "formula", "distribution", "sdata", "a", "b", "back", "again", "temperatures",
           "steps", "every_five", "zeros", "prices", "counts", "both", "rain", "readings", "heights", "picked",
           "wave", "flow", "foods", "growth", "signal", "noise", "island", "chances", "waits", "tone", "a_big",
           "b_big", "parts", "frequencies", "arrivals", "dice", "path", "amounts", "wet"}


def _examples():
    found = []
    for m in BLOCK.finditer(TEXT):
        section = re.findall(r"\\unsection\{[^}]*\}\{([^}]*)\}", TEXT[:m.start()])
        found.append(pytest.param(m.group("code"), id=f"{section[-1] if section else 'start'}-{len(found) + 1}"))
    return found


EXAMPLES = _examples()


def test_the_chapter_has_its_examples():
    assert len(EXAMPLES) >= 25


@pytest.mark.parametrize("code", EXAMPLES)
def test_every_example_in_the_chapter_runs(code, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SIMPLYDATA_NO_CITE_LIST", "1")
    printed = io.StringIO()
    try:
        with contextlib.redirect_stdout(printed):
            exec(compile("import simplydata as sdata\n" + code, "from_numpy.tex", "exec"), {"__name__": "__chapter__"})
    finally:
        plt.close("all")
    out = printed.getvalue()
    assert "is now called" not in out, "the chapter teaches an old name:\n" + out
    saved = re.findall(r'\.save\("([^"]+)"', code)
    assert all((tmp_path / name).is_file() for name in saved), saved


def test_the_simplydata_words_in_the_chapter_are_todays_words():
    """<object>.<word>( in the boxes and in \\code{...} names a current word, never an old name."""
    words = {learn._word(k) for k in learn._all_keys()}
    text = TEXT.replace("\\_", "_")
    calls = {(name, word) for name, word in re.findall(r"\b(\w+)\.(\w+)\(", text) if name in OBJECTS}
    unknown = sorted(f"{name}.{word}" for name, word in calls
                     if word not in words and not (name == "sdata" and word in dir(sdata)))
    assert not unknown, unknown
    assert len({word for _, word in calls}) > 70


def test_the_hand_over_lines_are_the_only_other_code():
    """Before the hand-over (as_numpy()), a box uses only simplydata words: no np., scipy. or pandas call."""
    for param in EXAMPLES:
        code = param.values[0]
        before = code.split(".as_numpy()")[0]
        assert not re.search(r"\b(np|numpy|scipy|pd|stats|linalg)\.\w+", before), before
        assert "import numpy" not in before and "import scipy" not in before and "import pandas" not in code


def test_every_hand_over_comes_back_to_simplydata():
    for param in EXAMPLES:
        code = param.values[0]
        if ".as_numpy()" in code:
            after = code.split(".as_numpy()", 1)[1]
            assert re.search(r"sdata\.number_(list|grid|block)\(", after), code


def test_the_chapter_links_to_the_official_guides_and_copies_none():
    links = re.findall(r"\\href\{([^}]*)\}", TEXT)
    assert sum("numpy.org/doc/stable/" in link for link in links) >= 15
    assert sum("docs.scipy.org/doc/scipy/tutorial/" in link for link in links) >= 12
    assert all(link.startswith("https://") for link in links)


NUMPY_TOPICS = ["making", "shape", "indexing", "maths", "broadcasting", "summaries", "reshaping", "sorting",
                "conditions", "empty", "random", "files", "matrices"]
SCIPY_TOPICS = ["fourier", "integration", "optimization", "interpolation", "signals", "linalg", "spatial", "special",
                "statistics", "ndimage", "file-io"]


@pytest.mark.parametrize("topic", ["first", *NUMPY_TOPICS, *SCIPY_TOPICS, "left-out"])
def test_the_chapter_follows_the_guides(topic):
    assert "}{from-numpy:" + topic + "}" in TEXT, topic


def test_the_topics_come_in_the_order_of_the_guides():
    order = re.findall(r"\\unsection\{[^}]*\}\{from-numpy:([^}]*)\}", TEXT)
    assert order == ["first", *NUMPY_TOPICS, *SCIPY_TOPICS, "left-out"]


@pytest.mark.parametrize("job", ["np.einsum", "np.diff", "np.histogram", "np.argsort", "np.meshgrid",
                                 "np.linalg.norm", "scipy.sparse", "np.polynomial"])
def test_the_chapter_names_the_jobs_left_to_numpy_and_scipy(job):
    assert job in TEXT.replace("\\_", "_"), job


@pytest.mark.parametrize("word", ["solve_for", "break_down", "between=[0, None]"])
def test_the_chapter_teaches_the_words_of_this_phase(word):
    assert word in TEXT.replace("\\_", "_"), word


def test_the_chapter_is_in_the_manual():
    spec = importlib.util.spec_from_file_location("make_manual", ROOT / "docs" / "make_manual.py")
    make_manual = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(make_manual)
    tex = make_manual.make()
    assert r"\part{From NumPy and SciPy}\label{part:from-numpy}" in tex
    assert tex.index(r"\input{from_matplotlib}") < tex.index(r"\input{from_numpy}") < tex.index(
        r"\input{from_sympy}") < tex.index(r"\part{Solutions}")
    assert r"\unchapter{From NumPy and SciPy to simplydata}" in TEXT


def test_the_lines_are_short():
    long = [line for line in TEXT.splitlines() if len(line) > 120]
    assert not long, long
