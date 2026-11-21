"""Write docs/how_simplydata_chooses.md from simplydata._method_basis (BASIS, REFERENCES, PRINCIPLES).

    python docs/make_method_basis.py          # write the file
    python docs/make_method_basis.py --check  # exit 1 when the file is out of date

Nothing in the document is written by hand: change the registry, then run this script. A test
(tests/test_method_basis.py) fails when the file does not match the registry.
"""

from __future__ import annotations

import sys
from pathlib import Path

from simplydata import learn
from simplydata._method_basis import BASIS, EVIDENCE, PRINCIPLE_REFERENCES, PRINCIPLES, REFERENCES

HERE = Path(__file__).resolve().parent
OUT = HERE / "how_simplydata_chooses.md"

INTRO = """\
# How simplydata chooses methods

simplydata often chooses a method, an option value or a setting for you: Welch's t-test when you compare two
averages, Holm's method when you adjust many p-values, REML and Hartung-Knapp intervals when you combine
studies. This document answers the question a reviewer asks first: *how does simplydata know which method is
right, and what logic does it use?*

The answer is five principles, applied in order, and one entry for each of the {count} choices simplydata
makes. Each entry gives the default, the alternatives (and the option that asks for them), why simplydata
chose it, the published evidence, and what simplydata checks in your data before it uses the method.

## The five principles

{principles}

## How to read the tables

- **Word or option**: the simplydata word, or a word with one of its options (`table.combine_studies test_method=`).
- **Default**: what simplydata does when you do not say otherwise.
- **Alternatives**: what else you can ask for, and how.
- **Why**: the principle followed (P1 to P5), the reasoning and the evidence, then **Checks**: what simplydata
  checks in your data, and when it refuses or warns and says what to use instead.
- **References**: short citations; the full list with links is at the end.

The basis of each default is one of three kinds. {evidence}. Of the {count} defaults, {published} rest on
published guidelines or method comparisons, {convention} follow the convention of the package named so that
results match it, and {starting} are simplydata's own starting values, marked as such, each changed with the
option named.

Every reference was checked before it was cited: each DOI was looked up in Crossref
(`https://api.crossref.org/works/<doi>`), which is where the authors, year, title and journal below come from;
the few references without a DOI were checked at their URL. The numbers themselves are checked against the
packages underneath in the reliability study (`validation/`), and every default can be changed with an option.

## How the defaults were reviewed

The defaults of the later batches (S3a, S3b and S3c) were set in design briefs, and each brief was read by an
independent reviewer before it was built; the defaults of the earlier releases follow the rules of `PLAN.md`
(state every choice; match R and SciPy) and the docstrings. Then, in November 2026, every entry of this document
was read again by independent reviewers acting as hostile statistical referees. They checked each reason against
the literature, looked every reference up in Crossref to confirm that it exists and supports the claim it is
attached to, and compared about 50 entries with the code. Their findings were applied: misattributed references
were replaced, overstated reasons were toned down, and the kind of basis was corrected. Where the evidence favours
another default than the one simplydata uses, the entry now says so; changing a default is a separate decision.

This document is made from `src/simplydata/_method_basis.py` by `docs/make_method_basis.py`; a test fails when
a word that chooses a method has no entry, or when this file is out of date.
"""


def cell(text: str) -> str:
    """Text for one markdown table cell."""
    return " ".join(text.replace("|", "\\|").split())


def word_cell(key: str) -> str:
    word, _, option = key.partition(" ")
    shown = learn._call_form(word) if word in learn._all_keys() and not word.endswith("=") else word
    return f"`{shown}`" + (f" `{option}`" if option else "")


def grouped() -> list[tuple[str, list[str]]]:
    """BASIS keys in learn.GROUPS order: each word, then its options in the order written."""
    out, placed = [], set()
    for group, words in learn.GROUPS:
        keys = []
        for word in words:
            for key in BASIS:
                if key == word or key.startswith(word + " "):
                    keys.append(key)
        keys = [k for k in keys if k not in placed]
        placed.update(keys)
        if keys:
            out.append((group, keys))
    missing = [k for k in BASIS if k not in placed]
    if missing:
        raise ValueError(f"these entries belong to no group of simplydata.learn: {missing}")
    return out


def refs_cell(keys) -> str:
    return "; ".join(f"[{REFERENCES[k].short}]({REFERENCES[k].link})" for k in keys)


def make() -> str:
    counts = {kind: sum(b.evidence == kind for b in BASIS.values()) for kind in EVIDENCE}
    principles = "\n".join(
        f"{i}. **{key}.** {text}" + (f" ({refs_cell(PRINCIPLE_REFERENCES[key])})" if PRINCIPLE_REFERENCES[key] else "")
        for i, (key, text) in enumerate(PRINCIPLES.items(), start=1))
    evidence = "; ".join(f"*{kind}*: {text}" for kind, text in EVIDENCE.items())
    lines = [INTRO.format(count=len(BASIS), principles=principles, evidence=evidence,
                          published=counts["published"], convention=counts["convention"],
                          starting=counts["starting value"])]
    for group, keys in grouped():
        lines.append(f"## {group}\n")
        lines.append("| Word or option | Default | Alternatives | Why | References |")
        lines.append("|---|---|---|---|---|")
        for key in keys:
            b = BASIS[key]
            why = f"**{b.principle}.** {b.why}"
            if b.evidence != "published":
                why += f" *Basis: {b.evidence}.*"
            if b.checks:
                why += f" **Checks:** {b.checks}"
            lines.append(f"| {word_cell(key)} | {cell(b.default)} | {cell(b.alternatives)} | {cell(why)} | "
                         f"{refs_cell(b.references)} |")
        lines.append("")
    lines.append("## References\n")
    used = {r for b in BASIS.values() for r in b.references} | {r for v in PRINCIPLE_REFERENCES.values() for r in v}
    for key in sorted(used, key=lambda k: (REFERENCES[k].text.lower(), k)):
        ref = REFERENCES[key]
        where = f"doi:[{ref.doi}]({ref.link})" if ref.doi else f"<{ref.url}>"
        lines.append(f"- {ref.text} {where}")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str]) -> int:
    text = make()
    if "--check" in argv:
        same = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print("up to date" if same else f"{OUT.name} is out of date: run python docs/make_method_basis.py")
        return 0 if same else 1
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"Wrote {OUT} ({len(BASIS)} defaults)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
