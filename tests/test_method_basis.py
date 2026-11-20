"""How simplydata chooses methods: every default has its published basis (simplydata._method_basis).

These tests make every future word that chooses a method add its basis: a "simplydata chooses" line in
simplydata._underneath without an entry in BASIS fails here, and so does an entry whose word or option no
longer exists, a reference without a DOI or URL, and a docs/how_simplydata_chooses.md that is out of date.
"""

from __future__ import annotations

import importlib.util
import inspect
import re
from pathlib import Path

import pytest

from simplydata import learn
from simplydata._method_basis import BASIS, EVIDENCE, PRINCIPLE_REFERENCES, PRINCIPLES, REFERENCES
from simplydata._underneath import UNDERNEATH

ROOT = Path(__file__).resolve().parents[1]
DOI = re.compile(r"^10\.\d{4,9}/\S+$")


def _script():
    spec = importlib.util.spec_from_file_location("make_method_basis", ROOT / "docs" / "make_method_basis.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_underneath_choice_has_a_basis():
    missing = [key for key, entry in UNDERNEATH.items() if entry.choices and key not in BASIS]
    assert not missing, f"add an entry to BASIS in src/simplydata/_method_basis.py for: {missing}"


@pytest.mark.parametrize("key", list(BASIS))
def test_every_key_is_a_current_word_and_option(key):
    keys = set(learn._all_keys())
    if key in keys:  # a word, or an option word such as "show="
        return
    word, _, option = key.partition(" ")
    assert word in keys, f"{key!r}: {word!r} is not a current word (renamed?)"
    params = set(inspect.signature(learn._function(word)).parameters)
    for name in re.findall(r"(\w+)=", option):
        assert name in params, f"{key!r}: {word} has no option {name}="


@pytest.mark.parametrize("key", list(BASIS))
def test_every_entry_is_complete(key):
    b = BASIS[key]
    assert b.default.strip() and b.alternatives.strip() and b.why.strip()
    assert b.principle in PRINCIPLES
    assert b.evidence in EVIDENCE
    assert all(r in REFERENCES for r in b.references), [r for r in b.references if r not in REFERENCES]
    if b.evidence == "published":  # a published basis names its source
        assert b.references, f"{key!r} says its basis is published but cites nothing"


@pytest.mark.parametrize("key", list(REFERENCES))
def test_every_reference_has_a_doi_or_url(key):
    ref = REFERENCES[key]
    assert ref.short and ref.text
    assert ref.doi or ref.url, f"{key} has neither a DOI nor a URL"
    if ref.doi:
        assert DOI.match(ref.doi), ref.doi
    else:
        assert ref.url.startswith("https://"), ref.url


def test_every_reference_is_cited_and_short_names_are_unique():
    used = {r for b in BASIS.values() for r in b.references} | {r for v in PRINCIPLE_REFERENCES.values() for r in v}
    assert set(REFERENCES) == used, f"not cited: {sorted(set(REFERENCES) - used)}"
    shorts = [r.short for r in REFERENCES.values()]
    assert len(shorts) == len(set(shorts)), "two references share a short name"


def test_every_entry_belongs_to_a_group():
    placed = [k for _, keys in _script().grouped() for k in keys]
    assert sorted(placed) == sorted(BASIS)


def test_the_document_is_up_to_date():
    text = (ROOT / "docs" / "how_simplydata_chooses.md").read_text(encoding="utf-8")
    assert text == _script().make(), "run python docs/make_method_basis.py"
