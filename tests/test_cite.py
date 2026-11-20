"""sdata.show_packages_used(): the packages that did the work behind the words, and how to cite them.

Asked for by the owner (2026-11-20): "this should happen for any package the user uses even for pandas or polars
or scipy anything". No test here uses the network.
"""

import inspect
import os
import re
import subprocess
import sys
import textwrap
import types
from pathlib import Path

import pytest

import simplydata as sdata
from simplydata import _cite, learn
from simplydata._citations import CITATIONS

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(sdata.__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def fresh_record(monkeypatch):
    """Each test starts with nothing used."""
    for used in (_cite._USED_WORDS, _cite._USED_PYTHON, _cite._USED_R):
        used.clear()
    monkeypatch.setitem(_cite._SETTINGS, "at_end", True)
    yield
    for used in (_cite._USED_WORDS, _cite._USED_PYTHON, _cite._USED_R):
        used.clear()


def _names(facts=None):
    return [f["name"] for f in (facts if facts is not None else _cite.packages_used())]


# ---------------------------------------------------------------- which packages each word uses
WORD_KEYS = [k for k in learn._all_keys() if not k.endswith("=")]


@pytest.mark.parametrize("key", WORD_KEYS)
def test_every_word_resolves_to_at_least_one_package(key):
    found = _cite.packages_of_word(key)
    if key in _cite.OWN_WORDS:
        assert found == ()
    else:
        assert found, f"{key} resolves to no package"
        assert set(found) <= set(_cite.WORK_PACKAGES)


def test_own_words_are_real_words():
    assert _cite.OWN_WORDS <= set(WORD_KEYS)


def test_every_public_word_is_wrapped():
    for key in WORD_KEYS:
        if key in _cite.OWN_WORDS:
            continue
        func = learn._function(key)
        assert hasattr(func, "_simplydata_word"), key


def test_wrapping_keeps_name_signature_text_and_spellings():
    word = sdata.Chart.draw_bars
    assert word.__name__ == "draw_bars"
    assert inspect.signature(word) == inspect.signature(word._simplydata_word)
    assert inspect.getdoc(word) == inspect.getdoc(word._simplydata_word)
    # a word with two spellings is still one word
    for key, others in learn._aliases().items():
        cls = next(c for c, k in learn._classes() if k == learn._kind(key))
        for other in others:
            assert getattr(cls, other) is getattr(cls, learn._word(key))


def test_a_table_word_records_its_packages_and_what_holds_the_table():
    table = sdata.table(sdata.get_example("marks"))
    table.find_average_of("marks", for_each_group_in="class")
    names = _names()
    assert names[0] == "simplydata"
    assert {"pandas", "narwhals"} <= set(names)
    assert "Polars" not in names  # the table is held by pandas


def test_a_polars_table_records_polars():
    pytest.importorskip("polars")
    table = sdata.table(sdata.get_example("marks"), fast=True)
    table.find_average_of("marks")
    assert "Polars" in _names()


def test_a_chart_word_records_matplotlib_and_seaborn():
    chart = sdata.chart(sdata.get_example("marks"))
    chart.draw_bars(x="class", y="marks")
    assert {"matplotlib", "seaborn"} <= set(_names())


def test_a_statistics_word_records_scipy():
    table = sdata.table(sdata.get_example("trial"))
    table.compare_averages_of("days", for_each_group_in="treatment")
    assert "SciPy" in _names()


def test_an_option_with_its_own_underneath_entry_adds_its_packages():
    # table.explain has entries only for its options; with_knots= (a natural spline) is the one that uses patsy
    assert "patsy" not in _cite.packages_of_word("table.explain", ())
    assert "patsy" in _cite.packages_of_word("table.explain", ("with_knots",))
    assert "statsmodels" in _cite.packages_of_word("table.explain", ())  # from the word's own code


def test_an_option_entry_written_with_its_value_is_found_by_the_option_name():
    from simplydata._underneath import UNDERNEATH

    entry = UNDERNEATH['table.explain outcome="yes or no (overdispersed)"']
    found, own = _cite._underneath_packages("table.explain", ("outcome",))
    assert not own and "statsmodels" in found
    assert entry.word == "table.explain"


def test_every_wrapped_word_can_be_pickled():
    import pickle

    for key in WORD_KEYS:
        func = learn._function(key)
        assert pickle.loads(pickle.dumps(func)) is func, key


def test_a_word_that_fails_records_nothing():
    table = sdata.table(sdata.get_example("marks"))
    _cite._USED_WORDS.clear()
    _cite._USED_PYTHON.clear()
    with pytest.raises(Exception):
        table.find_average_of("no such column")
    assert not _cite._USED_WORDS and not _cite._USED_PYTHON
    assert _names() == ["simplydata"]


def test_words_called_inside_a_word_that_fails_are_dropped_too():
    inner = _cite._wrap(lambda: _cite.record_r(("vegan",)), "nums.find_median")

    def outer_body():
        inner()
        raise ValueError("stop")

    outer = _cite._wrap(outer_body, "nums.find_average")
    with pytest.raises(ValueError):
        outer()
    assert not _cite._USED_WORDS and not _cite._USED_R and not _cite._USED_PYTHON


def test_recording_never_changes_what_a_word_gives_or_prints(capsys):
    word = sdata.Numbers.find_median
    nums = sdata.numbers([12, 15, 9, 20, 14])
    first = word(nums)
    printed = capsys.readouterr().out
    second = word._simplydata_word(nums)
    assert first == second
    assert capsys.readouterr().out == printed


def test_record_r_maps_base_packages_to_r_and_adds_rpy2():
    _cite.record_r(("vegan",), "stats::lm(y ~ x); survival::coxph(f)")
    assert list(_cite._USED_R) == ["R", "vegan", "survival"]
    assert "rpy2" in _cite._USED_PYTHON


def test_without_r_an_r_package_still_gets_a_line(monkeypatch):
    import simplydata._r as bridge

    def no_r(packages):
        raise bridge.RMissing("no R")

    monkeypatch.setattr(bridge, "r_package_facts", no_r)
    monkeypatch.setattr(_cite, "_R_FACTS", {})
    _cite.record_r(("vegan",))
    facts = {f["name"]: f for f in _cite.packages_used()}
    assert facts["vegan"]["language"] == "R" and 'citation("vegan")' in facts["vegan"]["text"]
    assert facts["R"]["language"] == "R"


# ---------------------------------------------------------------- the references
def test_simplydata_comes_first_with_the_doi_of_citation_cff():
    cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    doi = re.search(r'^doi:\s*"?([^"\n]+)"?', cff, re.M).group(1)
    title = re.search(r'^title:\s*"([^"]+)"', cff, re.M).group(1)
    assert doi == _cite.SIMPLYDATA_DOI and title == _cite.SIMPLYDATA_TITLE
    assert re.search(r"family-names:\s*Victor", cff) and re.search(r"given-names:\s*Manish Prakash", cff)
    first = _cite.packages_used()[0]
    assert first["name"] == "simplydata" and first["version"] == sdata.__version__
    assert _cite.SIMPLYDATA_DOI in first["text"] and _cite.SIMPLYDATA_DOI in first["bibtex"]


@pytest.mark.parametrize("module_name", list(CITATIONS))
def test_each_python_reference_is_complete(module_name):
    shown, dist, one_line, text, bib = CITATIONS[module_name]
    assert shown and dist and one_line and text
    assert len(_entries(bib)) >= 1


def test_a_package_without_a_reference_gets_its_name_version_and_home_page():
    facts = _cite._python_facts("narwhals")
    assert facts["name"] == "narwhals" and facts["version"] not in ("", "version unknown")
    assert facts["text"].startswith("narwhals") and facts["cite"] == ""
    assert _entries(facts["bibtex"])[0][0] == "misc"


def _entries(text):
    """A small BibTeX reader: [(type, key, fields)]; fails on unbalanced braces or a missing key."""
    found = []
    i = 0
    while True:
        m = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,").search(text, i)
        if not m:
            break
        depth, j = 1, m.end()
        while depth:
            assert j < len(text), "unbalanced braces"
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        body = text[m.end():j - 1]
        fields = {k.lower() for k in re.findall(r"(\w+)\s*=", body)}
        found.append((m.group(1).lower(), m.group(2), fields))
        i = j
    assert len(re.findall(r"^\s*@\w+\s*\{", text, re.M)) == len(found), "an entry without a key"
    return found


def test_bibtex_parses_with_one_key_each(tmp_path, capsys):
    table = sdata.table(sdata.get_example("trial"))
    table.compare_averages_of("days", for_each_group_in="treatment")
    sdata.chart(sdata.get_example("marks")).draw_bars(x="class", y="marks")
    file = tmp_path / "references.bib"
    sdata.show_packages_used(save_as=str(file))
    assert "Saved the references as BibTeX" in capsys.readouterr().out
    entries = _entries(file.read_text(encoding="utf-8"))
    keys = [key for _, key, _ in entries]
    assert len(keys) == len(set(keys))
    assert keys[0] == "simplydata"
    assert {"2020SciPy-NMeth", "Hunter:2007", "Waskom2021"} <= set(keys)
    assert all("title" in fields for _, _, fields in entries)


def test_r_bibtex_without_keys_gets_keys():
    f = dict(name="survival", language="R",
             bibtex="@Manual{,\n  title = {A},\n  year = {2026},\n}\n\n@Book{survival-book,\n  title = {B},\n}\n\n"
                    "@Article{,\n  title = {C},\n}")
    text = _cite._bibtex_with_keys(f)
    assert [k for _, k, _ in _entries(text)] == ["R-survival", "survival-book", "R-survival-3"]


# ---------------------------------------------------------------- printing
def test_show_packages_used_prints_the_list_a_methods_sentence_and_the_save_hint(capsys):
    sdata.table(sdata.get_example("marks")).find_average_of("marks")
    capsys.readouterr()
    sdata.show_packages_used()
    out = capsys.readouterr().out
    assert out.startswith("Packages that did the work behind your simplydata words")
    assert "simplydata " + sdata.__version__ + " (Python, " in out
    assert "A sentence for your methods:" in out
    sentence = " ".join(out.split("A sentence for your methods:")[1].split("As BibTeX")[0].split())
    assert sentence.startswith("Data were analysed in Python ") and "pandas" in sentence
    assert 'save_as="references.bib"' in out


def test_nothing_used_yet_says_so(capsys):
    sdata.show_packages_used()
    assert "No simplydata word has used another package yet" in capsys.readouterr().out


def test_packages_you_loaded_yourself_are_listed_apart(monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "sklearn", types.ModuleType("sklearn"))
    monkeypatch.setattr(_cite, "BEFORE_SIMPLYDATA", {"sklearn"})
    sdata.show_packages_used()
    out = capsys.readouterr().out
    assert "You also loaded these yourself (cite them if you used them):" in out
    assert "scikit-learn" in out.split("You also loaded these yourself")[1]


def test_methods_sentence_with_r():
    facts = [_cite._simplydata_facts(), _cite._python_facts("numpy"),
             dict(name="R", version="4.6.2", language="R", cite="R Core Team 2026"),
             dict(name="vegan", version="2.7.6", language="R", cite="Oksanen et al. 2026")]
    sentence = _cite.methods_sentence(facts)
    assert sentence.endswith("; and R 4.6.2 (R Core Team 2026) with the packages vegan 2.7.6 (Oksanen et al. 2026).")
    assert "NumPy " in sentence and "(Harris et al. 2020)" in sentence


def test_at_end_and_save_as_are_checked(capsys):
    with pytest.raises(sdata.SimplydataError, match="True or False"):
        sdata.show_packages_used(at_end="no")
    with pytest.raises(sdata.SimplydataError, match="file name"):
        sdata.show_packages_used(save_as=3)
    sdata.show_packages_used(at_end=False)
    assert "No list of packages at the end" in capsys.readouterr().out
    assert _cite._SETTINGS["at_end"] is False


def test_help_points_from_other_names():
    from simplydata._errors import other_name_pointer

    for name in ("cite", "citation", "citations", "references", "cite_packages", "sessionInfo", "session_info",
                 "bibtex"):
        assert "show_packages_used" in other_name_pointer("sdata", name), name


# ---------------------------------------------------------------- at the end of a script
SCRIPT = """
import simplydata as sdata
{before}
table = sdata.table(sdata.get_example("marks"))
print(table.find_average_of("marks"))
print("END OF SCRIPT")
"""


def _run_script(tmp_path, before="", env_extra=None, args=(), stdin=None):
    script = tmp_path / "script.py"
    script.write_text(textwrap.dedent(SCRIPT.format(before=before)), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != _cite.OFF_VARIABLE}
    env["PYTHONPATH"] = str(SRC) + os.pathsep + env.get("PYTHONPATH", "")
    env["MPLBACKEND"] = "Agg"
    env["PYTHONIOENCODING"] = "utf-8"
    env.update(env_extra or {})
    return subprocess.run([sys.executable, *args, str(script)], cwd=tmp_path, env=env, capture_output=True,
                          text=True, encoding="utf-8", timeout=300,
                          **({"input": stdin} if stdin is not None else {"stdin": subprocess.DEVNULL}))


def test_a_script_prints_the_short_list_at_the_end(tmp_path):
    result = _run_script(tmp_path)
    assert result.returncode == 0, result.stderr
    out = result.stdout
    assert "Packages simplydata used in this script" in out
    after = out.split("END OF SCRIPT")[1]
    assert "Packages simplydata used in this script" in after
    lines = after.strip().splitlines()
    assert lines[1].split()[:3] == ["simplydata", sdata.__version__, "Python"]
    assert any(line.split()[0] == "pandas" for line in lines[1:])
    assert "SIMPLYDATA_NO_CITE_LIST=1" in lines[-1]


def test_the_environment_variable_switches_it_off(tmp_path):
    result = _run_script(tmp_path, env_extra={_cite.OFF_VARIABLE: "1"})
    assert result.returncode == 0, result.stderr
    assert "END OF SCRIPT" in result.stdout and "Packages simplydata used" not in result.stdout


def test_at_end_false_switches_it_off(tmp_path):
    result = _run_script(tmp_path, before="sdata.show_packages_used(at_end=False)")
    assert result.returncode == 0, result.stderr
    assert "END OF SCRIPT" in result.stdout and "Packages simplydata used in this script" not in result.stdout


def test_silent_after_an_error_that_stops_the_script(tmp_path):
    result = _run_script(tmp_path, before="")
    script = tmp_path / "script.py"
    script.write_text(script.read_text(encoding="utf-8") + "raise ValueError('stopped here')\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != _cite.OFF_VARIABLE}
    env["PYTHONPATH"] = str(SRC) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run([sys.executable, str(script)], cwd=tmp_path, env=env, capture_output=True,
                            text=True, encoding="utf-8", timeout=300)
    assert result.returncode != 0 and "stopped here" in result.stderr
    assert "END OF SCRIPT" in result.stdout and "Packages simplydata used" not in result.stdout


def test_silent_in_a_worker_process(tmp_path):
    before = textwrap.dedent("""
        import multiprocessing
        multiprocessing.parent_process = lambda: object()   # as in a Pool worker
    """)
    result = _run_script(tmp_path, before=before)
    assert result.returncode == 0, result.stderr
    assert "Packages simplydata used" not in result.stdout


def test_at_end_true_says_when_the_environment_variable_keeps_it_off(monkeypatch, capsys):
    monkeypatch.setenv(_cite.OFF_VARIABLE, "1")
    sdata.show_packages_used(at_end=True)
    assert "SIMPLYDATA_NO_CITE_LIST is set" in capsys.readouterr().out


def test_a_bad_save_as_prints_nothing_first(capsys):
    with pytest.raises(sdata.SimplydataError):
        sdata.show_packages_used(save_as="")
    assert capsys.readouterr().out == ""


def test_r_without_a_reference_says_how_to_ask_r(monkeypatch):
    monkeypatch.setattr(_cite, "_R_FACTS", {})
    import simplydata._r as bridge

    monkeypatch.setattr(bridge, "r_package_facts", lambda packages: {})
    facts = _cite._r_facts(["R", "vegan"])
    assert facts["R"]["text"] == "type citation() in R"
    assert facts["vegan"]["text"] == 'type citation("vegan") in R'


def test_silent_in_an_interactive_session(tmp_path):
    # python -i: the prompt waits for input; the plain prompt (PYTHON_BASIC_REPL, Python 3.13's new prompt can
    # wait for a console on Windows) reads the end of the input and stops
    result = _run_script(tmp_path, args=("-i",), env_extra={"PYTHON_BASIC_REPL": "1"}, stdin="")
    assert "END OF SCRIPT" in result.stdout
    assert "Packages simplydata used in this script" not in result.stdout


def test_silent_when_python_says_it_is_interactive(tmp_path):
    result = _run_script(tmp_path, before="import sys; sys.ps1 = '>>> '")
    assert result.returncode == 0, result.stderr
    assert "END OF SCRIPT" in result.stdout and "Packages simplydata used" not in result.stdout


def test_silent_in_a_notebook_kernel(tmp_path):
    result = _run_script(tmp_path, before="import sys, types; sys.modules['ipykernel'] = types.ModuleType('ipykernel')")
    assert result.returncode == 0, result.stderr
    assert "Packages simplydata used in this script" not in result.stdout


def test_a_script_that_uses_no_word_prints_nothing(tmp_path):
    script = tmp_path / "plain.py"
    script.write_text("import simplydata as sdata\nprint('done')\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != _cite.OFF_VARIABLE}
    env["PYTHONPATH"] = str(SRC) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run([sys.executable, str(script)], cwd=tmp_path, env=env, capture_output=True, text=True,
                            encoding="utf-8", timeout=300)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "done"


# ---------------------------------------------------------------- R
def test_r_call_records_r_and_its_packages(needs_r):
    from simplydata._r import r_call

    r_call("stats::median(x)", packages=("vegan",), x=[1.0, 2.0, 3.0])
    assert list(_cite._USED_R) == ["R", "vegan"]
    facts = {f["name"]: f for f in _cite.packages_used()}
    assert facts["R"]["source"] == "CRAN" and re.match(r"\d+\.\d+\.\d+", facts["R"]["version"])
    assert "R Core Team" in facts["R"]["text"] and facts["R"]["cite"].startswith("R Core Team")
    vegan = facts["vegan"]
    assert vegan["language"] == "R" and vegan["source"] == "CRAN" and re.match(r"\d", vegan["version"])
    assert "vegan" in vegan["text"] and vegan["bibtex"].lstrip().startswith("@")
    keys = [k for _, k, _ in _entries(_cite.bibtex(list(facts.values())))]
    assert {"R", "R-vegan"} <= set(keys) and len(keys) == len(set(keys))


def test_r_call_that_fails_records_nothing(needs_r):
    from simplydata._r import r_call

    with pytest.raises(sdata.SimplydataError):
        r_call("stop('no')", packages=("vegan",))
    assert not _cite._USED_R


def test_a_script_with_r_prints_the_r_references_before_r_stops(tmp_path, needs_r):
    before = textwrap.dedent("""
        from simplydata._r import r_call
        r_call("stats::median(x)", packages=("vegan",), x=[1.0, 2.0, 3.0])
    """)
    result = _run_script(tmp_path, before=before)
    assert result.returncode == 0, result.stderr
    after = result.stdout.split("END OF SCRIPT")[1]
    rows = {line.split()[0]: line for line in after.splitlines() if line.startswith("  ")}
    assert "R" in rows and "vegan" in rows
    assert "version unknown" not in rows["vegan"] and "CRAN" in rows["vegan"]
