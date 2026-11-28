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
    ("lapack", "dpotri"),
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
    # numbers phase, batch 3: the user's own formula handed to SymPy lambdify, with lgamma pointed at SciPy gammaln
    # (the function itself, as R lgamma and fit_formula); nothing is computed by simplydata
    "_formula.py::Formula.find_value_at": "SymPy lambdify told to use scipy.special.gammaln for the formula's lgamma "
                                          "(a name mapping, as table/columns.py offers digamma)",
    "words/more_charts.py::_second_scale.inverse": "add_second_x / add_second_y(formula=): inverts the user's own "
                                                   "second-scale formula for tick positions with SciPy brentq "
                                                   "(matplotlib secondary_xaxis needs both directions); no "
                                                   "statistical method of our own",
    "table/columns.py": "digamma offered as a formula function users can type",
    # numbers phase, batch 4 (approved by Manish 2026-11-26): the matrix words are SciPy's own linalg calls, handed
    # the grid as it is (as R solve() and eigen()); nothing is computed by simplydata
    "numbers/numbers_4.py::GridWords4.take_inverse": "grid.take_inverse() is SciPy linalg.inv itself (LAPACK)",
    "numbers/numbers_4.py::GridWords4.find_eigenvalues": "grid.find_eigenvalues() is SciPy linalg.eigvalsh (symmetric "
                                                         "grid) or linalg.eigvals itself (LAPACK)",
    # numbers finishing (P41): solving and breaking down a grid are SciPy's own linalg calls, handed the grid as it is
    "numbers/solving_words.py::SolvingWords.solve_for": "grid.solve_for() is SciPy linalg.solve or linalg.lstsq "
                                                        "itself (LAPACK), as R solve() and qr.solve()",
    "numbers/solving_words.py::SolvingWords.break_down": "grid.break_down() is SciPy linalg.svd, qr, lu, cholesky, "
                                                         "schur, polar, ldl, hessenberg or qz itself (LAPACK)",
    "table/fitting.py::_not_pinned_down": "rank of the Jacobian from least_squares (thin check, T10)",
    "table/models.py::ModelWords._fit_one": "inverts the fixed-effects block of statsmodels' MixedLM Hessian (lme4 vcov)",
    "table/models.py::_nested_mixed": "inverts the fixed-effects block of statsmodels' MixedLM Hessian (lme4 vcov), groups inside groups",
    "table/models.py::_qr_unscaled_covariance": "R summary.lm()'s chol2inv(qr.R): NumPy's QR factor of the "
                                                "(whitened) columns and LAPACK dpotri (the routine chol2inv calls) "
                                                "for inv(R) inv(R)'; statsmodels' own inv(R'R) lost 4 to 5 digits on "
                                                "NIST Longley (data-and-fixes, A1). Approved by Manish 2026-11-22",
    "table/models.py::ModelWords._fit_model": "matrix_rank: checks the columns before fitting",
    "table/models.py::ModelWords._more_model": "matrix_rank: the same column check before fitting",
    "table/models.py::ModelWords._explain_matched": "matrix_rank: the same column check before conditional logistic "
                                                    "regression (statsmodels ConditionalLogit)",
    "table/models_extra.py::lost_columns": "matrix_rank: a bootstrap resample whose model columns lose rank is "
                                           "refused (a rare group drew no row), never fitted with a pseudo-inverse",
    "table/models.py::ModelWords._explain_more": "matrix_rank: the same column check for the zero part's own columns "
                                                 "(zero_part_using=)",
    "table/models.py::ModelWords._rank_problem": "names the columns that repeat others, for the error message",
    "table/models.py::ModelWords._whole_column_tests": "Wald chi-square b' V^-1 b from the fitted covariance",
    "table/models.py::ModelWords._model_notes": "variance inflation factors from the correlation matrix",
    # S3a-3
    "table/checking_more.py::manova": "matrix_rank: refuses columns that repeat others before statsmodels MANOVA",
    "table/checking_r.py::left_out_rows": "the error on the rows each model was fitted to, mean((y - fitted)^2), "
                                          "next to cv.glm's error on left-out rows (cv.glm's own cost function)",
    "table/checking_r.py::group_levels": "the 95 % interval of each group level, level +/- qnorm(0.975) * the "
                                         "conditional sd from ranef(condVar = TRUE), as lattice::dotplot draws it",
    # our own choices of preprocessing, written in R code (no building block to find; listed so they stay visible)
    "_forecast.py::r_change_points": "find_change_points divides the readings by mad(diff(x)) / sqrt(2) before "
                                     "changepoint::cpt.mean, which assumes noise with standard deviation 1. "
                                     "Our choice: neither the changepoint help nor Killick & Eckley (2014, JSS "
                                     "58(3)) prescribes a scaling; the MAD of the differences is a robust noise "
                                     "size that the jumps do not inflate. Said in the printed method sentence.",
}
# ALLOWED places whose choice lives in R code: the text that must still be in the file
IN_R_CODE = {"_forecast.py::r_change_points": "mad(diff(x)) / sqrt(2)",
             # S3a-3
             "table/checking_r.py::left_out_rows": "mean((y - stats::fitted(m))^2)",
             "table/checking_r.py::group_levels": "stats::qnorm(0.975) * sds"}



# Display arithmetic on package output: plain arithmetic, so the building-block search above cannot see
# it; listed here so each place is named, has its reason, and is marked [D] in the code. Bayes' rule at a
# stated prevalence: no Python package gives it, and R epiR::epi.tests() has no prevalence argument (R bdpv
# BDtest(pr =) does, from counts only, and is not a simplydata dependency). Each entry approved by Manish
# 2026-11-15.
ALLOWED_ARITHMETIC = {
    "table/risk_words.py::_nnt": "definitional conversion of package output: NNT = 1 / risk difference (Altman "
                                 "1998), its interval ends 1 / the ends of statsmodels' Newcombe interval",
    "table/risk_words.py::risk_engine": "\"out of 100\": the risk difference (statsmodels) times 100",
    "table/risk_words.py::rate_rows": "rates per 1000: events / time and statsmodels confint_poisson's interval, "
                                      "times per=",
    "table/accuracy_words.py::at_prevalence": "Bayes' rule on sensitivity, specificity and prevalence (PPV and NPV "
                                              "at a stated prevalence)",
    "table/accuracy_words.py::_per_1000": "natural frequencies: each share times 1000, rounded",
    "table/agreement_words.py::AgreementWords._cohen": "the chance agreement read back from statsmodels' unweighted "
                                                       "kappa: (raw - kappa) / (1 - kappa)",
    "table/models_extra.py::other_pseudo": "Nagelkerke's pseudo R squared = statsmodels' Cox-Snell divided by its "
                                           "largest value, 1 - exp(2 llnull / n), and Tjur's = the average fitted "
                                           "chance among yes minus among no (the definitions R performance uses)",
    "table/models_extra.py::standardise": "z-scores (value - average) / standard deviation of the rows used, before "
                                          "the statsmodels refit, as R effectsize::standardize_parameters(method = "
                                          "\"refit\")",
    "table/lines_more.py::explain_percentile": "the Wald 95 % interval estimate +/- t x quantreg's \"nid\" standard "
                                               "error, which goes with the t-test summary.rq prints (quantreg prints "
                                               "no interval for se = \"nid\")",
    # S3a-3 (proposed at build, for Manish's approval)
    "table/checking_more.py::compare_many": "Akaike weights exp(-difference / 2) scaled to 1, and the differences, "
                                            "from statsmodels' AIC / AICc (as R AICcmodavg::aictab; no Python package "
                                            "gives the weights)",
    "table/checking_more.py::calibration": "the Brier score mean((p - y)^2) of statsmodels' fitted chances (as R "
                                           "DescTools::BrierScore), the no-skill reference share * (1 - share), and "
                                           "each tenth's average chance and share of yes for the picture",
    "table/checking_more.py::nested_averages": "the raw group averages, and the share of lme4's two variances that "
                                               "lies between units",
    "table/checking_more.py::manova": "each group's averages of the compared columns, for the printout (the test "
                                      "itself is statsmodels MANOVA)",
    # S3b-2 (decision 14 of the S3b design). PENDING MANISH'S APPROVAL before release; the alternative is R epiR at
    # run time (epi.sscompc(design = DE)), whose base answer uses the normal (z) formula and differs from
    # find_how_many_needed's t-test answer. The reliability study checks it against epiR.
    "power_more.py::clustered": "the design effect 1 + (m - 1) x ICC (Donner & Klar 2000), the values needed = the "
                                "independent number (statsmodels or R) times it, rounded up, whole clusters of m, "
                                "m / design effect (what one cluster counts as) and a given number / design effect "
                                "(the independent values it counts as)",
    # data-and-fixes, A1. Approved by Manish 2026-11-22
    "table/models.py::_qr_unscaled_covariance": "the unscaled covariance of a least-squares fit as R summary.lm() "
                                                "computes it, chol2inv(qr.R(qr(X))): R's own method, done with "
                                                "NumPy's QR and LAPACK dpotri (the routine chol2inv calls)",
    # review fixes (2026-11-21)
    "_trend_season.py::lag1_after_sen_line": "the readings minus SciPy theilslopes' line (the residuals), the input "
                                             "of statsmodels acf and acorr_ljungbox for find_trend_of's check of "
                                             "independent readings",
}


def _functions(tree):
    """Qualified names of every function and method in a module."""
    out = set()

    def visit(node, names):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not isinstance(child, ast.ClassDef):
                    out.add(".".join(names + [child.name]))
                visit(child, names + [child.name])

    visit(tree, [])
    return out


@pytest.mark.parametrize("key", sorted(ALLOWED_ARITHMETIC))
def test_each_arithmetic_place_exists_and_is_marked(key):
    relative, _, where = key.partition("::")
    path = SOURCE / relative
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    assert where in _functions(tree), f"{key} is gone; remove it from ALLOWED_ARITHMETIC"
    node = next(n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and n.name == where.split(".")[-1])
    assert "[D]" in ast.get_source_segment(text, node), f"{key}: mark the display arithmetic with [D]"


def _imported_blocks(tree):
    """Names brought in with `from scipy.optimize import brentq` (or `... import brentq as b`) that
    are building blocks: {local name: "optimize.brentq"}."""
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            owner = node.module.split(".")[-1]
            for alias in node.names:
                if (owner, alias.name) in BUILDING_BLOCKS:
                    out[alias.asname or alias.name] = f"{owner}.{alias.name}"
    return out


def _uses(tree):
    """(function qualname, block) for every building block used inside a function, whether
    written as optimize.brentq(...) or imported by name and called as brentq(...)."""
    found = []
    imported = _imported_blocks(tree)

    def visit(node, names):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                visit(child, names + [child.name])
                continue
            where = ".".join(n for n in names if n)
            if isinstance(child, ast.Attribute) and isinstance(child.value, (ast.Attribute, ast.Name)):
                owner = child.value.attr if isinstance(child.value, ast.Attribute) else child.value.id
                if (owner, child.attr) in BUILDING_BLOCKS:
                    found.append((where, f"{owner}.{child.attr}"))
            elif isinstance(child, ast.Name) and child.id in imported and isinstance(child.ctx, ast.Load):
                found.append((where, imported[child.id]))
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
    if key in IN_R_CODE:
        text = (SOURCE / relative).read_text(encoding="utf-8")
        assert IN_R_CODE[key] in text and f"def {where}(" in text, f"{key} has changed; update ALLOWED"
        return
    uses = [(r, w) for r, w, _ in _all_uses() if r == relative]
    assert uses, f"{relative} no longer uses any building block; remove it from ALLOWED"
    if where:
        assert any(w == where or w.startswith(where + ".") for _, w in uses), \
            f"{key} no longer uses any building block; remove it from ALLOWED"
