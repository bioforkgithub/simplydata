"""The same work underneath: every entry of simplydata._underneath runs next to its word and gives the same result.

Each entry's simplydata code and its library code (pandas, Polars, NumPy, matplotlib, seaborn, SciPy,
statsmodels, R) are run and compared by the entry's compare= kind: numbers to its tolerance, tables by
values and column order, result tables field by field, and charts by their data (chart_facts), never by
pixels. Table words run on a pandas and on a Polars table. R entries are skipped where R is missing,
except in CI (SIMPLYDATA_REQUIRE_R=1), where they must run.
"""

import importlib.util
import re
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import learn
from simplydata._underneath import CHART_FACTS, COMPARE_KINDS, R_LABEL, UNDERNEATH, Entry, underneath_line
from simplydata._underneath.check import (chart_facts, check_entry, compare_charts, compare_legend_numbers, run_ours,
                                          run_python)

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = list(UNDERNEATH.values())


@pytest.mark.parametrize("entry", ENTRIES, ids=[e.word for e in ENTRIES])
def test_the_word_and_the_library_give_the_same_result(entry):
    outcomes = check_entry(entry)
    assert outcomes, entry.word
    skipped = [o for o in outcomes if o.skipped]
    if skipped:
        if os.environ.get("SIMPLYDATA_REQUIRE_R") == "1":
            pytest.fail(f"SIMPLYDATA_REQUIRE_R=1 but {entry.word} could not run: {skipped[0].skipped}")
        pytest.skip(skipped[0].skipped)
    failed = [f"{o.library} on a {o.engine} table: " + "; ".join(o.differences) for o in outcomes if not o.passed]
    assert not failed, f"{entry.word}: " + "\n".join(failed)


# ---------------------------------------------------------------- the keys follow the renames
@pytest.mark.parametrize("entry", ENTRIES, ids=[e.word for e in ENTRIES])
def test_keys_are_current_words_not_old_names(entry):
    assert entry.word in learn._all_keys(), f"{entry.word} is not a word of simplydata.learn"
    assert learn._lookup(entry.word) == entry.word
    assert not learn._old_names(entry.word), f"{entry.word} is an old name"


@pytest.mark.parametrize("entry", [e for e in ENTRIES if not e.uses_r], ids=[e.word for e in ENTRIES if not e.uses_r])
def test_ours_prints_no_old_name_note(entry):
    _, printed = run_ours(entry)
    assert "is now called" not in printed, printed
    plt.close("all")


def test_the_word_itself_is_called_in_ours():
    for entry in ENTRIES:
        assert f".{learn._word(entry.word)}(" in entry.ours_code(), entry.word


def test_library_code_names_no_simplydata_word_but_the_practice_table():
    """A rename then never touches the library code: only word= and ours= hold simplydata names."""
    import re

    for entry in ENTRIES:
        for library, language, source in entry.blocks():
            names = set(re.findall(r"\bsdata\.(\w+)", source)) | set(re.findall(r"\b(?:table|chart|nums)\.(\w+)\(",
                                                                                     source))
            assert names <= {"get_example"}, (entry.word, library, names)


# ---------------------------------------------------------------- the shape of each entry
@pytest.mark.parametrize("entry", ENTRIES, ids=[e.word for e in ENTRIES])
def test_entry_is_complete(entry):
    assert entry.compare in COMPARE_KINDS
    if entry.compare == "none":
        assert entry.note.strip(), f"{entry.word}: a word with nothing underneath needs a note="
        return
    assert entry.code, entry.word
    for library, language, source in entry.blocks():
        assert len(source.splitlines()) <= 14, f"{entry.word}: keep each block to about 12 lines ({library})"
        if language == "python":
            compile(source, entry.word, "exec")
    first_block = entry.blocks()[0][2]
    shown = first_block.splitlines()
    assert any(line.lstrip().startswith(("#",)) and learn._word(entry.word) in line for line in shown), (
        f"{entry.word}: the code starts its work with a comment naming the simplydata line it does")
    numbered = sorted({int(m) for _, _, src in entry.blocks() for line in src.splitlines() if "#" in line
                       for m in re.findall(r"\((\d+)\)", line.split("#", 1)[1])})
    assert numbered == list(range(1, len(entry.choices) + 1)), (
        f"{entry.word}: each (1), (2) ... mark in the code has one line in choices=, in order")
    if entry.compare == "chart":
        assert entry.check and set(entry.check) <= set(CHART_FACTS), entry.word
    if entry.compare == "result":
        assert entry.fields, entry.word
    if entry.uses_r:
        assert entry.r_inputs.strip() and entry.r_packages, entry.word
        assert entry.python_note.strip(), f"{entry.word}: say what Python alone gives"
    assert underneath_line(entry), entry.word


def test_words_with_nothing_underneath_need_a_note():
    with pytest.raises(AssertionError):
        test_entry_is_complete(Entry(word="sdata.undo", ours="", compare="none"))
    test_entry_is_complete(Entry(word="sdata.undo", ours="", compare="none",
                                 note="simplydata's own: it keeps a copy of the table after each step"))
    outcome, = check_entry(Entry(word="sdata.undo", ours="", compare="none"))
    assert not outcome.passed


def test_r_label_says_simplydata_runs_it():
    assert "simplydata runs this in R for you" in R_LABEL


# ---------------------------------------------------------------- the marks are needed: leave one out and it fails
@pytest.mark.parametrize("word, setting", [
    ("draw_bars", "errorbar=None, "),
    ("draw_histogram", "bins=10, "),
    ("nums.find_median", "nan"),
    ("table.compare_averages_of", ", equal_var=False"),
])
def test_leaving_out_a_simplydata_choice_makes_the_comparison_fail(word, setting):
    entry = UNDERNEATH[word]
    library = next(iter(entry.code))
    changed = {library: entry.code[library].replace(setting, "")}
    if word == "nums.find_median":
        entry = Entry(**{**entry.__dict__, "ours": "sdata.numbers([12, None, 9, 20, 14]).find_median()"})
        changed = {library: entry.code[library].replace("[12, 15, 9, 20, 14]", "[12, np.nan, 9, 20, 14]")
                   .replace("nanmedian", "median")}
    outcomes = check_entry(Entry(**{**entry.__dict__, "code": changed}))
    assert outcomes and not any(o.passed for o in outcomes), f"{word}: the comparison should fail without {setting}"


# ---------------------------------------------------------------- chart_facts
def test_chart_facts_reads_bars_dots_lines_labels_and_legend():
    fig, ax = plt.subplots()
    ax.bar([0, 1], [3, 5], color=["red", "blue"])
    ax.scatter([1, 2, 3], [4, 5, 6], s=[10, 20, 40], c=["red", "red", "blue"])
    ax.plot([0, 1], [0, 1], label="line")
    ax.set_xlabel("x words")
    ax.set_ylabel("y words")
    ax.legend(title="key")
    facts = chart_facts(ax)
    assert [b[3] for b in facts["bars"]] == [3, 5]
    assert facts["bar_colour_groups"] == [0, 1]
    assert facts["dots"] == [(1, 4), (2, 5), (3, 6)]
    assert facts["dot_size_shares"] == [0.25, 0.5, 1.0]
    assert facts["dot_colour_groups"] == [0, 0, 1]
    assert facts["labels"] == ("x words", "y words", "")
    assert facts["legend"] == ["key", "line"]
    assert facts["scales"] == ("linear", "linear") and facts["panels"] == 1
    other = chart_facts(ax)
    assert compare_charts(facts, other, CHART_FACTS, 1e-9) == []
    ax.set_xlabel("other words")
    assert compare_charts(facts, chart_facts(ax), ("labels",), 1e-9)
    with pytest.raises(ValueError):
        compare_charts(facts, other, ("pixels",), 1e-9)
    plt.close("all")


def test_chart_facts_of_a_simplydata_chart():
    chart = sdata.chart(sdata.get_example("marks")).draw_bars(x="class", y="marks")
    facts = chart_facts(chart._render().axes[0])
    df = sdata.get_example("marks")
    heights = [b[3] for b in sorted(facts["bars"])]
    assert heights == pytest.approx(df.groupby("class", sort=False)["marks"].mean().tolist())
    plt.close("all")


def test_run_python_gives_the_last_line():
    value, printed, ns = run_python("x = 2\nprint('hi')\nx * 21")
    assert value == 42 and printed == "hi\n" and ns["x"] == 2
    value, _, _ = run_python("y = 1")
    assert value is None


def test_table_words_run_on_polars_too():
    entry = UNDERNEATH["table.find_average_of"]
    engines = {o.engine for o in check_entry(entry)}
    assert engines == {"pandas", "polars"}


# ---------------------------------------------------------------- the one-line name comes from the code
def test_underneath_line_is_read_from_the_code():
    assert underneath_line(UNDERNEATH["draw_bars"]) == "seaborn barplot()"
    assert underneath_line(UNDERNEATH["table.find_average_of"]) == (
        "pandas groupby().mean().reset_index() · Polars group_by().agg(), col().mean()")
    assert underneath_line(UNDERNEATH["table.keep_rows_where"]) == "pandas boolean indexing · Polars filter(), col()"
    assert underneath_line(UNDERNEATH["trade_off_curve"]).startswith("R pROC::roc(), pROC::ci.auc(), pROC::coords()")


# ---------------------------------------------------------------- the rename helper
def _rename_helper():
    spec = importlib.util.spec_from_file_location("rename_underneath_keys", ROOT / "docs" / "rename_underneath_keys.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rename_helper_rewrites_keys_and_ours_only():
    helper = _rename_helper()
    source = '''Entry(
        word="table.show_first",
        ours="""
            table = sdata.table(sdata.get_example("marks"))
            table.show_first(2, colour_by="x")
        """,
        code={"pandas": """
            df.show_first(2)   # not a simplydata name: library code is left alone
        """},
    )
'''
    words = {"table.show_first": "table.show_first_rows"}
    options = {"table.show_first_rows": {"colour_by": "colour"}}
    out = helper.rewrite(source, words, options)
    assert 'word="table.show_first_rows"' in out
    assert "table.show_first_rows(2, colour=\"x\")" in out
    assert "df.show_first(2)" in out


def test_rename_helper_finds_nothing_to_change_now():
    helper = _rename_helper()
    assert helper.changes() == {}, "an underneath entry uses an old name: run python docs/rename_underneath_keys.py --write"


def test_rename_table_comes_from_the_old_names():
    words, options = _rename_helper().rename_table()
    assert words.get("table.show_first") == "table.show_first_rows"
    assert all(new in learn._all_keys() for new in words.values())
    assert isinstance(options, dict)
    assert pd.Series(list(words)).is_unique


# ---------------------------------------------------------------- the manual and the dictionary are made from the entries
def _docs_module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "docs" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manual_shows_each_entry_in_a_grey_box_after_its_example():
    manual = _docs_module("make_manual")
    tex = (ROOT / "docs" / "manual" / "simplydata_manual.tex").read_text(encoding="utf-8")
    for key in learn._all_keys():
        start = tex.index("}{" + manual.label(key) + "}\n")
        end = tex.find("\\wordentry{", start)
        part = tex[start:end if end > 0 else len(tex)]
        mine = [e for e in ENTRIES if e.word == key]
        if not mine:
            assert "underneathbox" not in part, key
            continue
        assert part.index("Example you can run") < part.index(r"\begin{underneathbox}"), key
        for entry in mine:
            for library, language, source in entry.blocks():
                assert source in part, f"{entry.key}: the {library} code in the manual is the tested code"
            if entry.uses_r:
                assert manual.esc(R_LABEL) in part
            if entry.option:
                assert r"\textbf{With " + manual.code(entry.option) + "}" in part, entry.key
            if entry.compare == "chart":
                assert "The chart simplydata draws." in part
                assert (ROOT / "docs" / "manual" / manual.underneath_figure(key)).is_file(), key
        assert r"\wordfield{Underneath}{" + manual.underneath_name(key) + "}" in part


def test_table_boxes_show_pandas_then_polars():
    for entry in ENTRIES:
        if entry.word.startswith("table.") and "Polars" in entry.code:
            assert list(entry.code)[:2] == ["pandas", "Polars"], entry.word


def test_dictionary_underneath_line_comes_from_the_entries():
    manual = _docs_module("make_manual")
    tex = (ROOT / "docs" / "manual" / "simplydataDictionary.tex").read_text(encoding="utf-8")
    for key, entry in UNDERNEATH.items():
        if not entry.option:
            assert r"\field{Underneath}{" + manual.underneath_name(key) + "}" in tex, key
    assert tex.count(r"\field{Underneath}{") == len(learn._all_keys())


def test_a_simplydata_side_that_gives_no_chart_is_an_error_not_a_match():
    """The library side may draw on the current figure; the simplydata side must give its chart back, or the
    library's chart would be compared with itself."""
    entry = UNDERNEATH["draw_bars"]
    broken = Entry(**{**entry.__dict__, "ours": "chart = sdata.chart(sdata.get_example('marks'))\nNone"})
    with pytest.raises(TypeError, match="not a chart"):
        check_entry(broken)
    plt.close("all")


def test_legend_numbers_are_compared_to_the_printed_digits():
    entry = Entry(word="trade_off_curve", ours="", compare="chart", check=("lines",),
                  legend_pattern=UNDERNEATH["trade_off_curve"].legend_pattern,
                  legend_numbers=("auc", "auc_low", "auc_high"))
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], label="crp: AUC 0.831 (95 % CI 0.750 to 0.912)")
    ax.legend()
    assert compare_legend_numbers(entry, ax, {"auc": 0.8312, "auc_low": 0.7504, "auc_high": 0.9116}) == []
    assert compare_legend_numbers(entry, ax, {"auc": 0.84, "auc_low": 0.7504, "auc_high": 0.9116})
    assert compare_legend_numbers(entry, ax, {"auc": 0.8312, "auc_low": 0.7504})  # R gave no auc_high
    plt.close("all")
