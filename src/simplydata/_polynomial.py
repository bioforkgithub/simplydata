"""Families for 100 %, batch 13 (approved by Manish 2026-11-28, G5): sdata.polynomial, one maker for the polynomials of
NumPy, scipy.special and SymPy.

sdata.polynomial("legendre", degree=3) gives a formula, so every formula word works on it (find_value_at,
find_slope_formula, find_area_formula, turn_into_product, show_as_latex ...). The polynomial is made exactly by SymPy
(legendre_poly, chebyshevt_poly, hermite_poly, jacobi_poly, cyclotomic_poly, interpolating_poly ...), under simplydata's
one time limit for SymPy; the same polynomial in decimals is scipy.special's (legendre, chebyt, hermite, jacobi ...,
whose eval_* functions give its values) and numpy.polynomial's (Legendre, Chebyshev, Hermite, HermiteE, Laguerre,
Polynomial). The tests check each name against both. Own code is glue only.
"""

from __future__ import annotations

import contextlib
import io
import numbers as _nb

import numpy as np

from ._errors import SimplydataError, choice_error, friendly
from ._time_limit import one_deadline

# name -> (what it needs, the SymPy call, the same in SciPy / NumPy) ; the plain name first, library names after
POLYNOMIALS = {
    "legendre": ("degree=", "SymPy legendre_poly", "SciPy special.legendre, NumPy polynomial.Legendre"),
    "shifted legendre": ("degree=", "SymPy legendre_poly at 2x - 1", "SciPy special.sh_legendre"),
    "chebyshev": ("degree=", "SymPy chebyshevt_poly", "SciPy special.chebyt, NumPy polynomial.Chebyshev"),
    "chebyshev second kind": ("degree=", "SymPy chebyshevu_poly", "SciPy special.chebyu"),
    "shifted chebyshev": ("degree=", "SymPy chebyshevt_poly at 2x - 1", "SciPy special.sh_chebyt"),
    "shifted chebyshev second kind": ("degree=", "SymPy chebyshevu_poly at 2x - 1", "SciPy special.sh_chebyu"),
    "chebyshev c": ("degree=", "2 x SymPy chebyshevt_poly at x/2", "SciPy special.chebyc"),
    "chebyshev s": ("degree=", "SymPy chebyshevu_poly at x/2", "SciPy special.chebys"),
    "hermite": ("degree=", "SymPy hermite_poly", "SciPy special.hermite, NumPy polynomial.Hermite"),
    "probabilists hermite": ("degree=", "SymPy hermite_prob_poly", "SciPy special.hermitenorm, NumPy "
                                                                     "polynomial.HermiteE"),
    "laguerre": ("degree=", "SymPy laguerre_poly", "SciPy special.laguerre, NumPy polynomial.Laguerre"),
    "generalized laguerre": ("degree=, alpha=", "SymPy laguerre_poly(alpha=)", "SciPy special.genlaguerre"),
    "jacobi": ("degree=, alpha=, beta=", "SymPy jacobi_poly", "SciPy special.jacobi"),
    "gegenbauer": ("degree=, alpha=", "SymPy gegenbauer_poly", "SciPy special.gegenbauer"),
    "cyclotomic": ("degree= (the n of the n-th cyclotomic polynomial)", "SymPy cyclotomic_poly", ""),
    "swinnerton-dyer": ("degree= (the n: the polynomial has degree 2**n)", "SymPy swinnerton_dyer_poly", ""),
    "bernoulli": ("degree=", "SymPy bernoulli(n, x)", ""),
    "euler": ("degree=", "SymPy euler(n, x)", ""),
    "symmetric": ("degree=, letters=", "SymPy symmetric_poly", ""),
    "from roots": ("roots=", "SymPy, the product of (x - root)", "NumPy poly, polynomial.polyfromroots"),
    "from numbers": ("numbers= (highest power first)", "SymPy Poly", "NumPy poly1d, polynomial.Polynomial"),
    "through points": ("x=, y=", "SymPy interpolating_poly",
                       "SciPy interpolate.BarycentricInterpolator, NumPy polyfit"),
}
# library names that work too (G3) -> the plain name
OTHER_NAMES = {"legendre_poly": "legendre", "sh_legendre": "shifted legendre", "chebyt": "chebyshev",
               "chebyshevt": "chebyshev", "chebyshevt_poly": "chebyshev", "chebyshev first kind": "chebyshev",
               "chebyu": "chebyshev second kind", "chebyshevu": "chebyshev second kind",
               "chebyshevu_poly": "chebyshev second kind", "sh_chebyt": "shifted chebyshev",
               "sh_chebyu": "shifted chebyshev second kind", "chebyc": "chebyshev c", "chebys": "chebyshev s",
               "hermite_poly": "hermite", "physicists hermite": "hermite", "hermitenorm": "probabilists hermite",
               "hermite_e": "probabilists hermite",
               "hermite e": "probabilists hermite",
               "hermite_prob_poly": "probabilists hermite", "hermitee": "probabilists hermite",
               "laguerre_poly": "laguerre", "genlaguerre": "generalized laguerre",
               "assoc_laguerre": "generalized laguerre", "associated laguerre": "generalized laguerre",
               "jacobi_poly": "jacobi", "gegenbauer_poly": "gegenbauer", "ultraspherical": "gegenbauer",
               "cyclotomic_poly": "cyclotomic", "swinnerton_dyer_poly": "swinnerton-dyer",
               "symmetric_poly": "symmetric", "poly": "from roots", "polyfromroots": "from roots",
               "poly1d": "from numbers", "coefficients": "from numbers", "interpolating_poly": "through points",
               "lagrange": "through points", "interpolating": "through points"}
EXAMPLE = 'sdata.polynomial("legendre", degree=3)'


def _plain(name) -> str:
    if not isinstance(name, str):
        raise SimplydataError(f"sdata.polynomial() needs the name of a polynomial in quotes.\nFor example:  {EXAMPLE}")
    key = name.strip().lower().replace("_", " ") if name.strip().lower() not in OTHER_NAMES else name.strip().lower()
    key = OTHER_NAMES.get(key, OTHER_NAMES.get(key.replace(" ", "_"), key))
    key = key.replace("probabilist's", "probabilists").replace("physicist's", "physicists").replace("generalised",
                                                                                                     "generalized")
    key = OTHER_NAMES.get(key, key)
    if key not in POLYNOMIALS:
        raise choice_error("polynomial", "name", name, list(POLYNOMIALS))
    return key


def _degree(degree, name: str, smallest: int = 0) -> int:
    if isinstance(degree, bool) or not isinstance(degree, _nb.Integral) or degree < smallest:
        raise SimplydataError(f'sdata.polynomial("{name}") needs degree= a whole number from {smallest} up, such as '
                              "degree=3.")
    return int(degree)


def _number(sp, value, option: str, name: str, above=None):
    if isinstance(value, bool) or not isinstance(value, _nb.Real):
        raise SimplydataError(f'sdata.polynomial("{name}") needs {option}= a number, such as {option}=1.')
    if above is not None and not value > above:
        raise SimplydataError(f'sdata.polynomial("{name}") needs {option}= above {above}.')
    return sp.nsimplify(value)


def _numbers(value, option: str, name: str) -> list:
    from .numbers._base import to_array

    found = to_array(value, f"{option}=", f'sdata.polynomial("{name}", {option}=[1, 2, 3])').ravel()
    if not found.size or np.isnan(found.astype(float)).any():
        raise SimplydataError(f"{option}= needs a list of numbers without empty values.")
    return found.tolist()


@one_deadline
def _make(sp, name, degree, x, alpha, beta, roots, numbers, at_x, at_y, letters):
    from ._formula import _guarded

    def run(call, *values):
        return _guarded(call, *values, what=POLYNOMIALS[name][1])

    if name == "from roots":
        found = [sp.nsimplify(r) for r in _numbers(roots, "roots", name)]
        return run(sp.expand, sp.Mul(*[x - r for r in found]))
    if name == "from numbers":
        found = [sp.nsimplify(c) for c in _numbers(numbers, "numbers", name)]
        return run(sp.expand, sum(c * x ** (len(found) - 1 - i) for i, c in enumerate(found)))
    if name == "through points":
        xs, ys = _numbers(at_x, "x", name), _numbers(at_y, "y", name)
        if len(xs) != len(ys) or len(set(xs)) != len(xs):
            raise SimplydataError("x= and y= need the same number of values, and the x values must all differ.")
        return run(sp.expand, sp.interpolating_poly(len(xs), x, [sp.nsimplify(v) for v in xs],
                                                    [sp.nsimplify(v) for v in ys]))
    n = _degree(degree, name, 1 if name in ("cyclotomic", "swinnerton-dyer", "symmetric") else 0)
    if name == "symmetric":
        if letters is None or isinstance(letters, str) or not all(isinstance(v, str) for v in letters):
            raise SimplydataError('sdata.polynomial("symmetric") needs letters=, such as letters=["x", "y", "z"].')
        symbols = sp.symbols(list(letters))
        if n > len(symbols):
            raise SimplydataError(f"degree= is at most the number of letters ({len(symbols)}).")
        return run(sp.symmetric_poly, n, *symbols)
    shifted, half = 2 * x - 1, x / 2
    # name -> (SymPy function, its values); each call is handed to the helper process as it is (picklable)
    makers = {
        "legendre": (sp.legendre_poly, n, x), "shifted legendre": (sp.legendre_poly, n, shifted),
        "chebyshev": (sp.chebyshevt_poly, n, x), "chebyshev second kind": (sp.chebyshevu_poly, n, x),
        "shifted chebyshev": (sp.chebyshevt_poly, n, shifted),
        "shifted chebyshev second kind": (sp.chebyshevu_poly, n, shifted),
        "chebyshev c": (sp.chebyshevt_poly, n, half), "chebyshev s": (sp.chebyshevu_poly, n, half),
        "hermite": (sp.hermite_poly, n, x), "probabilists hermite": (sp.hermite_prob_poly, n, x),
        "laguerre": (sp.laguerre_poly, n, x), "cyclotomic": (sp.cyclotomic_poly, n, x),
        "swinnerton-dyer": (sp.swinnerton_dyer_poly, n, x), "bernoulli": (sp.bernoulli, n, x),
        "euler": (sp.euler, n, x)}
    if name == "generalized laguerre":
        found = run(sp.laguerre_poly, n, x, _number(sp, alpha, "alpha", name, -1))
    elif name == "jacobi":
        found = run(sp.jacobi_poly, n, _number(sp, alpha, "alpha", name, -1), _number(sp, beta, "beta", name, -1), x)
    elif name == "gegenbauer":
        from sympy.polys.orthopolys import gegenbauer_poly

        found = run(gegenbauer_poly, n, _number(sp, alpha, "alpha", name, -0.5), x)
    else:
        func, *values = makers[name]
        found = run(func, *values)
    if name == "chebyshev c":
        found = 2 * found
    return run(sp.expand, found)


_PROPER = {"legendre": "Legendre", "chebyshev": "Chebyshev", "hermite": "Hermite", "laguerre": "Laguerre",
           "jacobi": "Jacobi", "gegenbauer": "Gegenbauer", "swinnerton-dyer": "Swinnerton-Dyer",
           "bernoulli": "Bernoulli", "euler": "Euler", "c": "C", "s": "S", "probabilists": "probabilists'"}


def _title(plain, degree, roots, numbers, x) -> str:
    if plain == "from roots":
        return f"The polynomial with the roots {', '.join(str(v) for v in np.asarray(roots).ravel().tolist())}"
    if plain == "from numbers":
        return "The polynomial with these numbers (highest power first)"
    if plain == "through points":
        return f"The polynomial of lowest degree through the {np.size(x)} points"
    words = " ".join(_PROPER.get(w, w) for w in plain.split())
    if plain in ("cyclotomic", "swinnerton-dyer"):
        return f"The {words} polynomial number {degree}"
    return f"The {words} polynomial of degree {degree}"


@friendly
def polynomial(name=None, degree=None, letter="x", alpha=None, beta=None, roots=None, numbers=None, x=None, y=None,
               letters=None):
    """A named polynomial, as a formula. formula = sdata.polynomial("legendre", degree=3)

    Names: "legendre", "chebyshev" (first kind), "chebyshev second kind", "hermite" (physicists'), "probabilists
    hermite", "laguerre", "generalized laguerre" (alpha=), "jacobi" (alpha=, beta=), "gegenbauer" (alpha=), the
    shifted ones ("shifted legendre", "shifted chebyshev" ...), "chebyshev c", "chebyshev s", "cyclotomic",
    "swinnerton-dyer", "bernoulli", "euler" and "symmetric" (letters=), each with degree=; "from roots" (roots=),
    "from numbers" (numbers=, highest power first) and "through points" (x= and y=: the polynomial of lowest degree
    through them). SciPy's and SymPy's names work too ("chebyt", "hermitenorm", "legendre_poly"). Made exactly by SymPy
    (legendre_poly, chebyshevt_poly, jacobi_poly ...); scipy.special (legendre, chebyt, eval_legendre ...) and
    numpy.polynomial (Legendre, Chebyshev, Hermite ...) give the same polynomial in decimals. letter= the letter to use
    (x when not given).
    """
    from ._formula import Formula, _show, need_sympy

    plain = _plain(name)
    sp = need_sympy("sdata.polynomial()")
    if not isinstance(letter, str) or not letter.isidentifier():
        raise SimplydataError('letter= needs a letter in quotes, such as letter="t".')
    if plain not in ("jacobi", "generalized laguerre", "gegenbauer") and (alpha is not None or beta is not None):
        raise SimplydataError('alpha= and beta= go with "jacobi", "generalized laguerre" (alpha=) and "gegenbauer" '
                              "(alpha=).")
    if plain in ("generalized laguerre", "gegenbauer") and alpha is None:
        raise SimplydataError(f'sdata.polynomial("{plain}") needs alpha=, such as alpha=1.')
    if plain == "jacobi" and (alpha is None or beta is None):
        raise SimplydataError('sdata.polynomial("jacobi") needs alpha= and beta=, such as alpha=1, beta=2.')
    given = {"roots": roots, "numbers": numbers, "x": x, "y": y, "letters": letters}
    needed = {"from roots": {"roots"}, "from numbers": {"numbers"}, "through points": {"x", "y"},
              "symmetric": {"letters"}}.get(plain, set())
    extra = [k for k, v in given.items() if v is not None and k not in needed]
    if extra:
        raise SimplydataError(f'{", ".join(k + "=" for k in extra)} do not go with sdata.polynomial("{plain}"); it '
                              f"needs {POLYNOMIALS[plain][0]}")
    if needed and degree is not None and plain != "symmetric":
        raise SimplydataError(f'sdata.polynomial("{plain}") takes {POLYNOMIALS[plain][0]}, not degree=.')
    symbol = sp.Symbol(letter)
    expr = _make(sp, plain, degree, symbol, alpha, beta, roots, numbers, x, y, letters)
    same = POLYNOMIALS[plain][2]
    with contextlib.redirect_stdout(io.StringIO()):
        made = Formula(expr)
    print(f"{_title(plain, degree, roots, numbers, x)}: {_show(expr)}   ({POLYNOMIALS[plain][1]}, exact"
          + (f"; the same in decimals: {same})" if same else ")"))
    return made
