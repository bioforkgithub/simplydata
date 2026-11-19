"""Rewrite the underneath entries after a rename: the keys (word=) and the simplydata code (ours=).

The old-to-new table is the one simplydata itself uses for old names: each object's _OLD_WORDS (words)
and the renamed= of @friendly (options), the same table tests/test_old_names.py checks. The library
code is never touched: it holds no simplydata names except sdata.get_example().

    python docs/rename_underneath_keys.py           # show what would change
    python docs/rename_underneath_keys.py --write   # change the files in src/simplydata/_underneath/

tests/test_underneath.py fails while an entry still uses an old name, and names it.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "src" / "simplydata" / "_underneath"


def rename_table() -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    """({old key: new key}, {new key: {old option: new option}}) from simplydata's own old names."""
    import simplydata
    from simplydata import learn

    words: dict[str, str] = {}
    for cls, kind in learn._classes():
        for old, new in cls._OLD_WORDS.items():
            new = new[0] if isinstance(new, tuple) else new
            prefix = "" if kind == "chart" else learn._PREFIX[kind] + "."
            if prefix + new in learn._all_keys():
                words.setdefault(prefix + old, prefix + new)
    for old, new in simplydata._OLD_WORDS.items():
        if f"sdata.{new}" in learn._all_keys():
            words.setdefault(f"sdata.{old}", f"sdata.{new}")
    options = {key: dict(func._renamed_options) for key, func in learn._words_with_options()
               if getattr(func, "_renamed_options", None)}
    return words, options


def _word(key: str) -> str:
    return key.rsplit(".", 1)[-1]


def rewrite(source: str, words: dict[str, str], options: dict[str, dict[str, str]]) -> str:
    """The source of an underneath file with old keys and old names in ours= made current."""
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line))
    edits = []  # (start, end, new text)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and getattr(node.func, "id", None) == "Entry"):
            continue
        kw = {k.arg: k.value for k in node.keywords}
        word = kw.get("word")
        if not isinstance(word, ast.Constant):
            continue
        old_key = word.value
        new_key = words.get(old_key, old_key)
        for name in ("word", "ours"):
            value = kw.get(name)
            if not isinstance(value, ast.Constant):
                continue
            start = starts[value.lineno - 1] + value.col_offset
            end = starts[value.end_lineno - 1] + value.end_col_offset
            text = source[start:end]
            if name == "word":
                new = text.replace(old_key, new_key)
            else:
                new = text
                if new_key != old_key:
                    new = re.sub(rf"\.{re.escape(_word(old_key))}\(", f".{_word(new_key)}(", new)
                for old_opt, new_opt in options.get(new_key, {}).items():
                    new = re.sub(rf"(?<![\w.]){re.escape(old_opt)}=(?!=)", f"{new_opt}=", new)
            if new != text:
                edits.append((start, end, new))
    for start, end, new in sorted(edits, reverse=True):
        source = source[:start] + new + source[end:]
    return source


def changes() -> dict[Path, str]:
    """{file: new source} for each underneath file that uses an old name."""
    words, options = rename_table()
    found = {}
    for path in sorted(FOLDER.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        new = rewrite(text, words, options)
        if new != text:
            found[path] = new
    return found


def main(argv: list[str]) -> None:
    sys.path.insert(0, str(ROOT / "src"))
    found = changes()
    if not found:
        print("Every underneath entry uses the current names.")
        return
    import difflib

    for path, new in found.items():
        old = path.read_text(encoding="utf-8")
        sys.stdout.writelines(difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True),
                                                   str(path.relative_to(ROOT)), str(path.relative_to(ROOT))))
        if "--write" in argv:
            path.write_text(new, encoding="utf-8", newline="\n")
    print("Changed the files." if "--write" in argv else "Run with --write to change the files.")


if __name__ == "__main__":
    main(sys.argv[1:])
