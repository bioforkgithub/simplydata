"""Every dependency in pyproject.toml has a tested version range (MAINTAINING.md).

The lower bound is the oldest release CI tests (.github/workflows/oldest-versions.yml); the upper bound
stops a new major release, which nobody has tested yet, from reaching users on its own.
"""

import tomllib
from pathlib import Path

import pytest
from packaging.requirements import Requirement

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def _all_requirements():
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]
    found = [("dependencies", text) for text in project.get("dependencies", [])]
    for extra, texts in project.get("optional-dependencies", {}).items():
        found += [(f"[{extra}]", text) for text in texts]
    return found


def test_pyproject_has_dependencies():
    assert _all_requirements(), "no dependencies found in pyproject.toml"


@pytest.mark.parametrize("where, text", _all_requirements())
def test_dependency_has_lower_and_upper_bound(where, text):
    requirement = Requirement(text)
    operators = {spec.operator for spec in requirement.specifier}
    assert operators & {">=", ">", "==", "~="}, f"{text} in {where} has no lower bound"
    assert operators & {"<", "<=", "==", "~="}, f"{text} in {where} has no upper bound"
