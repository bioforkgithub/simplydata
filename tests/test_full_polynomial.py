"""Families for 100 %, batch 13 (G5, approved by Manish 2026-11-28): sdata.polynomial, checked against scipy.special,
numpy.polynomial and SymPy called directly. sdata.polynomial is new, so every test fails on the code before."""

import contextlib
import io

import numpy as np
import pytest
from scipy import interpolate, special

import simplydata as sdata
from simplydata._errors import SimplydataError

sp = pytest.importorskip("sympy")

XS = np.linspace(-0.95, 0.95, 9)

# name, options, the same polynomial's values from scipy.special
SCIPY = [
    ("legendre", {}, lambda n, x: special.eval_legendre(n, x)),
    ("shifted legendre", {}, special.eval_sh_legendre),
    ("chebyshev", {}, special.eval_chebyt),
    ("chebyshev second kind", {}, special.eval_chebyu),
    ("shifted chebyshev", {}, special.eval_sh_chebyt),
    ("shifted chebyshev second kind", {}, special.eval_sh_chebyu),
    ("chebyshev c", {}, special.eval_chebyc),
    ("chebyshev s", {}, special.eval_chebys),
    ("hermite", {}, special.eval_hermite),
    ("probabilists hermite", {}, special.eval_hermitenorm),
    ("laguerre", {}, special.eval_laguerre),
    ("generalized laguerre", {"alpha": 1.5}, lambda n, x: special.eval_genlaguerre(n, 1.5, x)),
    ("jacobi", {"alpha": 1, "beta": 2}, lambda n, x: special.eval_jacobi(n, 1, 2, x)),
    ("gegenbauer", {"alpha": 0.75}, lambda n, x: special.eval_gegenbauer(n, 0.75, x)),
]


def _values(formula, xs):
    with contextlib.redirect_stdout(io.StringIO()):
        return np.asarray(formula.find_value_at(x=xs).as_numpy(), dtype=float)


@pytest.mark.parametrize("name, options, reference", SCIPY, ids=[s[0] for s in SCIPY])
@pytest.mark.parametrize("degree", [0, 1, 4, 7])
def test_each_name_matches_scipy_special(name, options, reference, degree):
    formula = sdata.polynomial(name, degree=degree, **options)
    expected = reference(degree, XS)
    if degree == 0:  # a constant has no letter x to give a value
        assert np.allclose(float(formula.as_sympy()), expected, rtol=1e-12)
        return
    assert np.allclose(_values(formula, XS), expected, rtol=1e-11, atol=1e-11 * max(1.0, np.abs(expected).max()))


@pytest.mark.parametrize("name, basis", [("legendre", np.polynomial.Legendre), ("chebyshev", np.polynomial.Chebyshev),
                                         ("hermite", np.polynomial.Hermite),
                                         ("probabilists hermite", np.polynomial.HermiteE),
                                         ("laguerre", np.polynomial.Laguerre)])
def test_each_name_matches_numpy_polynomial(name, basis):
    expected = basis.basis(5).convert(kind=np.polynomial.Polynomial).coef
    formula = sdata.polynomial(name, degree=5)
    got = [float(c) for c in reversed(sp.Poly(formula.as_sympy(), sp.Symbol("x")).all_coeffs())]
    assert np.allclose(got, expected, rtol=1e-12, atol=1e-12)


def test_the_polynomial_is_exact_and_a_formula():
    formula = sdata.polynomial("legendre", degree=3)
    x = sp.Symbol("x")
    assert sp.simplify(formula.as_sympy() - sp.legendre_poly(3, x)) == 0
    assert sp.simplify(formula.as_sympy() - (5 * x ** 3 - 3 * x) / 2) == 0
    slope = formula.find_slope_formula()
    assert sp.simplify(slope.as_sympy() - sp.diff(sp.legendre_poly(3, x), x)) == 0


def test_sympy_only_names():
    x = sp.Symbol("x")
    assert sdata.polynomial("cyclotomic", degree=6).as_sympy() == sp.cyclotomic_poly(6, x)
    assert sdata.polynomial("swinnerton-dyer", degree=2).as_sympy() == sp.swinnerton_dyer_poly(2, x)
    assert sp.expand(sdata.polynomial("bernoulli", degree=4).as_sympy() - sp.bernoulli(4, x)) == 0
    assert sp.expand(sdata.polynomial("euler", degree=4).as_sympy() - sp.euler(4, x)) == 0
    a, b, c = sp.symbols("a b c")
    assert sdata.polynomial("symmetric", degree=2, letters=["a", "b", "c"]).as_sympy() == sp.symmetric_poly(2, a, b, c)


def test_from_roots_from_numbers_and_through_points():
    roots = sdata.polynomial("from roots", roots=[1, 2, 3])
    assert np.allclose(_values(roots, np.array([0.0, 4.0, 5.5])), np.polyval(np.poly([1, 2, 3]), [0, 4, 5.5]))
    made = sdata.polynomial("from numbers", numbers=[2, 0, -3, 1])
    assert np.allclose(_values(made, XS), np.poly1d([2, 0, -3, 1])(XS))
    x, y = [0, 1, 2, 4], [1, 3, 7, 2]
    through = sdata.polynomial("through points", x=x, y=y)
    expected = interpolate.BarycentricInterpolator(x, y)([3.0, 0.5])
    assert np.allclose(_values(through, np.array([3.0, 0.5])), expected, rtol=1e-10)
    assert np.allclose(_values(through, np.array(x, dtype=float)), y)


def test_library_names_work_too_and_letter():
    t = sp.Symbol("t")
    assert sdata.polynomial("chebyt", degree=3, letter="t").as_sympy() == sp.chebyshevt_poly(3, t)
    assert sdata.polynomial("hermitenorm", degree=3).as_sympy() == sp.hermite_prob_poly(3, sp.Symbol("x"))
    assert sdata.polynomial("legendre_poly", degree=2).as_sympy() == sp.legendre_poly(2, sp.Symbol("x"))


def test_mistakes_are_explained():
    with pytest.raises(SimplydataError, match="legendre"):
        sdata.polynomial("legendr", degree=3)
    with pytest.raises(SimplydataError, match="degree="):
        sdata.polynomial("legendre")
    with pytest.raises(SimplydataError, match="alpha= and beta="):
        sdata.polynomial("jacobi", degree=2, alpha=1)
    with pytest.raises(SimplydataError, match="do not go with"):
        sdata.polynomial("legendre", degree=2, roots=[1, 2])
    with pytest.raises(SimplydataError, match="x values must all differ"):
        sdata.polynomial("through points", x=[1, 1], y=[2, 3])


def test_the_sentence_names_the_libraries(capsys):
    sdata.polynomial("chebyshev", degree=2)
    out = capsys.readouterr().out
    assert "The Chebyshev polynomial of degree 2: 2*x**2 - 1" in out
    assert "SymPy chebyshevt_poly" in out and "SciPy special.chebyt" in out and "NumPy polynomial.Chebyshev" in out


def test_polynomial_pointers(capsys):
    for typed in ("special.legendre", "sp.chebyshevt_poly", "np.polynomial.Hermite", "np.polyval", "np.poly"):
        sdata.help(typed)
        assert "sdata.polynomial(" in capsys.readouterr().out, typed
