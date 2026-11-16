"""R_ENTRY_POINTS in conftest.py must name functions that exist: a renamed word that drops out of the
list makes CI without R fail (its R error is no longer recognised as expected)."""
import pathlib
import re

from conftest import R_ENTRY_POINTS


def test_r_entry_points_name_real_functions():
    root = pathlib.Path(__file__).resolve().parent.parent / "src" / "simplydata"
    for file, name in R_ENTRY_POINTS:
        text = (root / file).read_text(encoding="utf-8")
        assert re.search(rf"def {re.escape(name)}\b", text), f"{file}: no function {name}"
