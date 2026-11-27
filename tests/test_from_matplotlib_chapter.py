"""The manual chapter "From matplotlib and seaborn to simplydata" (docs/manual/from_matplotlib.tex) is written by hand:
every example in it runs (with matplotlib's Agg backend, so no window opens), uses today's words, and the chapter is
part of the manual, after the pandas chapter."""

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
CHAPTER = ROOT / "docs" / "manual" / "from_matplotlib.tex"
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
    assert len(EXAMPLES) >= 30


@pytest.mark.parametrize("code, needs", EXAMPLES)
def test_every_example_in_the_chapter_runs(code, needs, tmp_path, monkeypatch):
    if needs:
        pytest.importorskip(needs)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SIMPLYDATA_NO_CITE_LIST", "1")
    printed = io.StringIO()
    try:
        with contextlib.redirect_stdout(printed):
            exec(compile("import simplydata as sdata\n" + code, "from_matplotlib.tex", "exec"),
                 {"__name__": "__chapter__"})
    finally:
        plt.close("all")
    out = printed.getvalue()
    assert "is now called" not in out, "the chapter teaches an old name:\n" + out
    assert "old name" not in out.lower(), out
    saved = [m for m in re.findall(r'(?:save|savefig)\("([^"]+)"', code)]
    assert all((tmp_path / name).is_file() for name in saved), saved  # every picture it saves is written


def test_the_simplydata_words_in_the_chapter_are_todays_words():
    """chart.<word>(, page.<word>(, sdata.<word>( and the table words in the boxes and in \\code{...} name current
    words, never old names."""
    words = {learn._word(k) for k in learn._all_keys()}
    text = TEXT.replace("\\_", "_")
    charts = {"chart", "page", "pairs", "dots", "bars", "boxes"}
    tables = {"table"} | set(re.findall(r"\b(\w+) = sdata\.get_example\(", text))
    calls = {(name, word) for name, word in re.findall(r"\b(\w+)\.(\w+)\(", text)
             if name in charts | tables | {"sdata"}}
    unknown = sorted(f"{name}.{word}" for name, word in calls
                     if word not in words and not (name == "sdata" and word in dir(sdata)))
    assert not unknown, unknown
    assert len({word for name, word in calls if name in charts}) > 50


def test_the_hand_over_lines_are_the_only_other_code():
    """Outside the hand-over (after chart.as_matplotlib() or page.as_matplotlib()), a box uses only simplydata words:
    no plt., ax. or fig. call before the hand-over, and no pandas."""
    for param in EXAMPLES:
        code = param.values[0]
        before = code.split(".as_matplotlib()")[0] if ".as_matplotlib()" in code else code
        assert not re.search(r"\b(plt|ax|fig|sns|pd)\.\w+\(", before), before
        assert "import pandas" not in code


def test_the_chapter_links_to_the_official_guides_and_copies_none():
    links = re.findall(r"\\href\{([^}]*)\}", TEXT)
    assert sum("matplotlib.org/stable/" in link for link in links) >= 20
    assert sum("seaborn.pydata.org/tutorial" in link for link in links) >= 9
    assert all(link.startswith("https://") for link in links)


def test_the_chapter_has_no_ggplot_section():
    """The owner's decision (2026-11-27): no ggplot2 or plotnine section in this chapter."""
    assert "ggplot" not in TEXT.lower() and "plotnine" not in TEXT.lower()


@pytest.mark.parametrize("topic", [
    # the matplotlib Quick start guide and User guide, in their order
    "from-matplotlib:first-chart", "from-matplotlib:parts", "from-matplotlib:data", "from-matplotlib:styles",
    "from-matplotlib:styling", "from-matplotlib:labels", "from-matplotlib:axes", "from-matplotlib:colour-maps",
    "from-matplotlib:several", "from-matplotlib:style", "from-matplotlib:marks", "from-matplotlib:3d",
    "from-matplotlib:animations", "from-matplotlib:saving",
    # the seaborn tutorial, in its order
    "from-matplotlib:relational", "from-matplotlib:distributions", "from-matplotlib:categorical",
    "from-matplotlib:error-bars", "from-matplotlib:regression", "from-matplotlib:grids",
    "from-matplotlib:aesthetics", "from-matplotlib:palettes",
    "from-matplotlib:left-out",
])
def test_the_chapter_follows_the_guides(topic):
    assert "}{" + topic + "}" in TEXT, topic


def test_the_topics_come_in_the_order_of_the_guides():
    order = re.findall(r"\\unsection\{[^}]*\}\{from-matplotlib:([^}]*)\}", TEXT)
    assert order.index("first-chart") < order.index("parts") < order.index("labels") < order.index("axes")
    assert order.index("colour-maps") < order.index("several") < order.index("saving") < order.index("relational")
    assert order.index("relational") < order.index("distributions") < order.index("categorical")
    assert order.index("regression") < order.index("grids") < order.index("aesthetics") < order.index("palettes")
    assert order[-1] == "left-out"


@pytest.mark.parametrize("job", ["quiver", "ax.table", "Polygon", "fig.add\\_axes", "Slider", "boxenplot",
                                 "FacetGrid.map", "rcParams", "FuncFormatter", "imread"])
def test_the_chapter_names_the_jobs_left_to_matplotlib_and_seaborn(job):
    assert job in TEXT, job


def test_the_chapter_is_in_the_manual():
    spec = importlib.util.spec_from_file_location("make_manual", ROOT / "docs" / "make_manual.py")
    make_manual = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(make_manual)
    tex = make_manual.make()
    assert r"\input{from_matplotlib}" in tex
    assert tex.index(r"\input{from_pandas}") < tex.index(r"\input{from_matplotlib}") < tex.index(r"\part{Solutions}")
    assert r"\part{From matplotlib and seaborn}\label{part:from-matplotlib}" in tex
    assert r"\unchapter{From matplotlib and seaborn to simplydata}" in TEXT


def test_the_lines_are_short():
    long = [line for line in TEXT.splitlines() if len(line) > 120]
    assert not long, long


def test_the_pointers_name_the_chapter_that_exists():
    """The pointers for the jobs left to matplotlib and seaborn (quiver, boxenplot ...) name this chapter by its
    title."""
    from simplydata._other_names import OTHER_NAMES

    named = [w for w in OTHER_NAMES["chart"].values() if "From matplotlib and seaborn" in w]
    assert named and all('"From matplotlib and seaborn to simplydata"' in w for w in named)
    assert OTHER_NAMES["chart"]["quiver"] in named and OTHER_NAMES["chart"]["boxenplot"] in named
