"""Guard: simplydata calls established packages and does not write out its own methods.

simplydata checks inputs, calls SciPy / statsmodels (or R through rpy2) with R-matching
options, and words the result. Writing out an algorithm (a solver, a decomposition, a
search, a hand-made likelihood) is not allowed. This test finds the low-level building blocks
such code is made of (linear algebra, root finders, optimisers, digamma/gammaln, cumulative
products, polyfit) and fails when one turns up in a function that is not on the list below.

Each listed function says why it may use them. Items marked "R bridge" go when the R
methods arrive through simplydata[r] (design_evidence_private/own_code_review.md).

Limit: a method written only with plain arithmetic and loops (no building block) is not
caught here; the code review still has to look for those.
"""

import ast
import pathlib

import pytest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / "src" / "simplydata"

BUILDING_BLOCKS = {
    ("linalg", "solve"), ("linalg", "inv"), ("linalg", "qr"), ("linalg", "svd"), ("linalg", "lstsq"),
    ("linalg", "eig"), ("linalg", "eigh"), ("linalg", "eigvals"), ("linalg", "eigvalsh"), ("linalg", "pinv"),
    ("linalg", "cholesky"), ("linalg", "matrix_rank"),
    ("optimize", "minimize"), ("optimize", "brentq"), ("optimize", "newton"), ("optimize", "root_scalar"),
    ("optimize", "ridder"), ("optimize", "bisect"), ("optimize", "fsolve"), ("optimize", "least_squares"),
    ("special", "digamma"), ("special", "gammaln"), ("special", "polygamma"),
    ("np", "cumprod"), ("np", "polyfit"),
}

ALLOWED = {
    # glue: SciPy's optimisers asked to do the search, inputs and outputs translated
    "distributions.py::_maximise": "scipy.optimize.minimize on the log-likelihood (SciPy's own .fit stops short "
                                   "for t, Cauchy, chi-square; kept, decided 2026-11-14)",
    "distributions.py::_standard_errors": "inverts statsmodels' Hessian to get the covariance",
    "distributions.py::_weibull_shape": "Weibull score equation with brentq (SciPy weibull_min.fit stops at 1e-7; "
                                        "kept, decided 2026-11-14)",
    "distributions.py::_nbinom_size": "negative binomial size with brentq (statsmodels NegativeBinomial planned)",
    "finding.py": "find/solve words: the user's own equation handed to scipy.optimize (glue by design)",
    "table/columns.py": "digamma offered as a formula function users can type",
    "table/fitting.py::_not_pinned_down": "rank of the Jacobian from least_squares (thin check, T10)",
    "table/models.py::ModelWords._fit_one": "inverts the fixed-effects block of statsmodels' MixedLM Hessian (lme4 vcov)",
    "table/models.py::ModelWords._fit_model": "matrix_rank: checks the columns before fitting",
    "table/models.py::ModelWords._explain_more": "matrix_rank: the same column check before fitting",
    "table/models.py::ModelWords._rank_problem": "names the columns that repeat others, for the error message",
    "table/models.py::ModelWords._whole_column_tests": "Wald chi-square b' V^-1 b from the fitted covariance",
    "table/models.py::ModelWords._model_notes": "variance inflation factors from the correlation matrix",
}


def _uses(tree):
    """(function qualname, block) for every building block called inside a function."""
    found = []

    def visit(node, names):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                visit(child, names + [child.name])
                continue
            if isinstance(child, ast.Attribute) and isinstance(child.value, (ast.Attribute, ast.Name)):
                owner = child.value.attr if isinstance(child.value, ast.Attribute) else child.value.id
                if (owner, child.attr) in BUILDING_BLOCKS:
                    found.append((".".join(n for n in names if n), f"{owner}.{child.attr}"))
            visit(child, names)

    visit(tree, [])
    return found


def _all_uses():
    out = []
    for path in sorted(SOURCE.rglob("*.py")):
        relative = path.relative_to(SOURCE).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        out.extend((relative, where, block) for where, block in _uses(tree))
    return out


def _allowed(relative, where):
    if relative in ALLOWED:
        return True
    # a nested helper (def inside def) counts as its outer function
    parts = where.split(".")
    return any(f"{relative}::{'.'.join(parts[:i])}" in ALLOWED for i in range(1, len(parts) + 1))


def test_no_new_own_methods():
    new = [f"{relative}::{where or '(module)'} uses {block}" for relative, where, block in _all_uses()
           if not _allowed(relative, where)]
    assert not new, ("simplydata calls established packages instead of writing out methods. New calculation "
                     "code found:\n  " + "\n  ".join(new) + "\nCall SciPy/statsmodels (or R via simplydata[r]); "
                     "if this really is glue, add it to ALLOWED in tests/test_no_own_methods.py with the reason.")


@pytest.mark.parametrize("key", sorted(ALLOWED))
def test_each_allowed_place_still_exists(key):
    # remove an entry once its code is gone, so the list only names real exceptions
    relative, _, where = key.partition("::")
    uses = [(r, w) for r, w, _ in _all_uses() if r == relative]
    assert uses, f"{relative} no longer uses any building block; remove it from ALLOWED"
    if where:
        assert any(w == where or w.startswith(where + ".") for _, w in uses), \
            f"{key} no longer uses any building block; remove it from ALLOWED"
