"""Zeros of the maths functions and the points of the area rules (families for 100 %, plan section 2.3, approved by
Manish 2026-11-28).

* sdata.find_zeros_of(name, how_many=5, order=0): scipy.special's *_zeros functions (jn_zeros, jnp_zeros, yn_zeros,
  ynp_zeros, y0_zeros, y1_zeros, y1p_zeros, ai_zeros, bi_zeros, the Kelvin zeros, erf_zeros, fresnels_zeros,
  fresnelc_zeros, and jnjnp_zeros, jnyn_zeros, kelvin_zeros and fresnel_zeros that give several at once);
* sdata.find_area_points(name, how_many=5): the points and weights of Gauss's area rules, scipy.special's roots_*
  functions (and their short names p_roots, h_roots ...), and scipy.integrate's newton_cotes and lebedev_rule.

The functions have the plain names of numbers.take_function ("bessel J", "airy Ai", "legendre polynomial"): one
name table for the whole maths family. Each word is one SciPy call, named in the sentence it prints.
"""

from __future__ import annotations

import numpy as np

from ._errors import SimplydataError, choice_error, friendly

# plain name -> (SciPy function, uses order=, which answer of several, the answers are complex numbers)
ZEROS = {
    "bessel J": ("jn_zeros", True, None, False),
    "bessel J slope": ("jnp_zeros", True, None, False),
    "bessel Y": ("yn_zeros", True, None, False),
    "bessel Y slope": ("ynp_zeros", True, None, False),
    "bessel Y0": ("y0_zeros", False, 0, False),
    "bessel Y1": ("y1_zeros", False, 0, False),
    "bessel Y1 slope": ("y1p_zeros", False, 0, False),
    "airy Ai": ("ai_zeros", False, 0, False),
    "airy Ai slope": ("ai_zeros", False, 1, False),
    "airy Bi": ("bi_zeros", False, 0, False),
    "airy Bi slope": ("bi_zeros", False, 1, False),
    "kelvin ber": ("ber_zeros", False, None, False),
    "kelvin bei": ("bei_zeros", False, None, False),
    "kelvin ker": ("ker_zeros", False, None, False),
    "kelvin kei": ("kei_zeros", False, None, False),
    "kelvin ber slope": ("berp_zeros", False, None, False),
    "kelvin bei slope": ("beip_zeros", False, None, False),
    "kelvin ker slope": ("kerp_zeros", False, None, False),
    "kelvin kei slope": ("keip_zeros", False, None, False),
    "error function": ("erf_zeros", False, None, True),
    "fresnel S": ("fresnels_zeros", False, None, True),
    "fresnel C": ("fresnelc_zeros", False, None, True),
    "bessel J and J slope of every order": ("jnjnp_zeros", False, None, False),
}
# SciPy names that give the zeros of several functions at once -> (the plain names, in SciPy's order)
ZEROS_TOGETHER = {
    "jnyn_zeros": ("bessel J", "bessel J slope", "bessel Y", "bessel Y slope"),
    "kelvin_zeros": ("kelvin ber", "kelvin bei", "kelvin ker", "kelvin kei", "kelvin ber slope", "kelvin bei slope",
                     "kelvin ker slope", "kelvin kei slope"),
    "fresnel_zeros": ("fresnel S", "fresnel C"),
}
ZERO_SPELLINGS = {"bessel j0": "bessel J", "j0": "bessel J", "jn": "bessel J", "jv": "bessel J",
                  "bessel y0": "bessel Y0", "y0": "bessel Y0", "bessel y1": "bessel Y1", "y1": "bessel Y1",
                  "yn": "bessel Y", "ai": "airy Ai", "bi": "airy Bi", "airy": "airy Ai", "erf": "error function",
                  "ber": "kelvin ber", "bei": "kelvin bei", "ker": "kelvin ker", "kei": "kelvin kei",
                  "berp": "kelvin ber slope", "beip": "kelvin bei slope", "kerp": "kelvin ker slope",
                  "keip": "kelvin kei slope", "fresnels": "fresnel S", "fresnelc": "fresnel C",
                  "bessel j and its slope": "bessel J and J slope of every order"}

# plain name -> (SciPy function, its short name, the options in order, the interval, the weight function)
AREA_RULES = {
    "legendre polynomial": ("roots_legendre", "p_roots", (), "-1 to 1", "1"),
    "shifted legendre polynomial": ("roots_sh_legendre", "ps_roots", (), "0 to 1", "1"),
    "chebyshev T": ("roots_chebyt", "t_roots", (), "-1 to 1", "1 / sqrt(1 - x**2)"),
    "chebyshev U": ("roots_chebyu", "u_roots", (), "-1 to 1", "sqrt(1 - x**2)"),
    "chebyshev C": ("roots_chebyc", "c_roots", (), "-2 to 2", "1 / sqrt(1 - (x / 2)**2)"),
    "chebyshev S": ("roots_chebys", "s_roots", (), "-2 to 2", "sqrt(1 - (x / 2)**2)"),
    "shifted chebyshev T": ("roots_sh_chebyt", "ts_roots", (), "0 to 1", "1 / sqrt(x - x**2)"),
    "shifted chebyshev U": ("roots_sh_chebyu", "us_roots", (), "0 to 1", "sqrt(x - x**2)"),
    "jacobi polynomial": ("roots_jacobi", "j_roots", ("alpha", "beta"), "-1 to 1", "(1 - x)**alpha (1 + x)**beta"),
    "shifted jacobi polynomial": ("roots_sh_jacobi", "js_roots", ("p", "q"), "0 to 1",
                                  "(1 - x)**(p - q) x**(q - 1)"),
    "gegenbauer polynomial": ("roots_gegenbauer", "cg_roots", ("alpha",), "-1 to 1", "(1 - x**2)**(alpha - 1/2)"),
    "laguerre polynomial": ("roots_laguerre", "l_roots", (), "0 to infinity", "e**-x"),
    "generalized laguerre polynomial": ("roots_genlaguerre", "la_roots", ("alpha",), "0 to infinity",
                                        "x**alpha e**-x"),
    "hermite polynomial": ("roots_hermite", "h_roots", (), "-infinity to infinity", "e**(-x**2)"),
    "probabilists hermite polynomial": ("roots_hermitenorm", "he_roots", (), "-infinity to infinity",
                                        "e**(-x**2 / 2)"),
    "newton cotes": ("newton_cotes", "", (), "0 to how_many - 1 (equal steps of 1)", "1"),
    "lebedev": ("lebedev_rule", "", ("degree",), "the sphere of radius 1", "1"),
}
AREA_SPELLINGS = {"legendre": "legendre polynomial", "gauss legendre": "legendre polynomial",
                  "chebyshev": "chebyshev T", "chebyshevt": "chebyshev T", "chebyshevu": "chebyshev U",
                  "jacobi": "jacobi polynomial", "gegenbauer": "gegenbauer polynomial",
                  "laguerre": "laguerre polynomial", "genlaguerre": "generalized laguerre polynomial",
                  "hermite": "hermite polynomial", "hermitenorm": "probabilists hermite polynomial",
                  "hermite_prob": "probabilists hermite polynomial", "gauss hermite": "hermite polynomial",
                  "gauss laguerre": "laguerre polynomial", "lebedev rule": "lebedev", "lebedev_rule": "lebedev",
                  "newton_cotes": "newton cotes"}


def _key(text: str) -> str:
    from ._maths_functions import normal

    return normal(text)


def _find(name, table: dict, spellings: dict, library: dict):
    """The plain name of a value of name= (plain name, SciPy name or short name, any capitals), or None."""
    if not isinstance(name, str):
        return None
    text = name.strip()
    for head in ("scipy.special.", "special.", "scipy.integrate.", "integrate."):
        if text.lower().startswith(head):
            text = text[len(head):]
    key = _key(text)
    for plain in table:
        if _key(plain) == key:
            return plain
    for other, plain in spellings.items():
        if _key(other) == key:
            return plain
    for plain, found in library.items():
        if key in {_key(n) for n in found if n}:
            return plain
    return None


def _whole(value, option: str, example: str, least: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer, float, np.floating)) or \
            not float(value).is_integer() or value < least:
        raise SimplydataError(f"{option}= needs a whole number of {least} or more.\nFor example:  {example}")
    return int(value)


@friendly
def find_zeros_of(name=None, how_many=5, order=0):
    """The first zeros of a maths function, from SciPy. zeros = sdata.find_zeros_of("bessel J", order=0, how_many=5)

    name= a function by the plain names of numbers.take_function: "bessel J" (order=), "bessel J slope", "bessel Y",
    "bessel Y slope" (order=), "bessel Y0", "bessel Y1", "bessel Y1 slope", "airy Ai", "airy Ai slope", "airy Bi",
    "airy Bi slope", "kelvin ber" (and bei, ker, kei and their slopes), "error function", "fresnel S", "fresnel C";
    SciPy's names work too ("jn_zeros", "ai_zeros"). Real zeros come back as numbers, smallest first in size (the
    Airy zeros are below 0). The zeros of the error function and the Fresnel integrals are complex numbers: they
    come back as a table with a real part and an imaginary part column. "bessel J and J slope of every order"
    (SciPy jnjnp_zeros) gives a table of the zeros of J and its slope for the orders together, smallest first.
    """
    from scipy import special

    example = 'zeros = sdata.find_zeros_of("bessel J", order=0, how_many=5)'
    together = ZEROS_TOGETHER.get(str(name).strip().split(".")[-1]) if isinstance(name, str) else None
    plain = _find(name, ZEROS, ZERO_SPELLINGS, {p: (spec[0],) for p, spec in ZEROS.items()})
    if together:
        listed = ", ".join(f'"{p}"' for p in together)
        print(f"special.{name.strip().split('.')[-1]} gives the zeros of {len(together)} functions at once; "
              f"find_zeros_of gives one by its own name ({listed}): here the first, {together[0]}.")
        plain = together[0]
    if plain is None:
        if name is None:
            raise SimplydataError(f'find_zeros_of() needs the name of a function, such as "bessel J".\n'
                                  f"For example:  {example}")
        raise choice_error("find_zeros_of", "name", name, list(ZEROS))
    function_name, uses_order, which, is_complex = ZEROS[plain]
    count = _whole(how_many, "how_many", example, least=1)
    function = getattr(special, function_name)
    if uses_order:
        degree = _whole(order, "order", example)
        found = function(degree, count)
        call = f"special.{function_name}({degree}, {count})"
        about = f"{plain} of order {degree}"
    else:
        if order != 0:
            raise SimplydataError(f'order= is for "bessel J", "bessel J slope", "bessel Y" and "bessel Y slope"; '
                                  f'"{plain}" has no order.\nFor example:  {example}')
        found = function(count)
        call = f"special.{function_name}({count})"
        about = plain
    if function_name == "jnjnp_zeros":
        return _jnjnp_table(found, count, call)
    if which is not None:
        found = found[which]
        call += f"[{which}]"
    values = np.asarray(found)
    from .table import table as make_table
    from .numbers.numbers import Numbers

    if is_complex:
        shown = ", ".join(f"{complex(v):.4g}" for v in values[:3])
        print(f"The first {count} zeros of the {about} are complex numbers ({shown} ...), as a table of their real "
              f"and imaginary parts. SciPy: {call}")
        return make_table({"zero": list(range(1, count + 1)), "real part": np.real(values).tolist(),
                           "imaginary part": np.imag(values).tolist()})
    values = np.real(values).astype(float)
    shown = ", ".join(f"{v:.6g}" for v in values[:5]) + (" ..." if count > 5 else "")
    print(f"The first {count} zeros of the {about}: {shown}. SciPy: {call}")
    return Numbers(values)


def _jnjnp_table(found, count, call):
    from .table import table as make_table

    zeros, orders, numbers, kinds = found
    print(f"The first {count} zeros of bessel J and its slope, every order together, smallest first. SciPy: {call}")
    return make_table({"zero": np.asarray(zeros, dtype=float).tolist(),
                       "order": np.asarray(orders, dtype=int).tolist(),
                       "number": np.asarray(numbers, dtype=int).tolist(),
                       "function": ["bessel J" if k == 0 else "bessel J slope" for k in kinds]})


@friendly
def find_area_points(name=None, how_many=5, alpha=None, beta=None, p=None, q=None, degree=None):
    """The points and weights of an area rule, from SciPy. points = sdata.find_area_points("legendre", how_many=5)

    A table with a point and a weight column: the area under f between the ends of the rule is about the total of
    weight * f(point), and exact for a polynomial of degree up to 2 * how_many - 1 (Gauss's rule). name= the
    polynomial by the plain names of numbers.take_function: "legendre polynomial" (or "legendre"; from -1 to 1),
    "shifted legendre polynomial", "chebyshev T", "chebyshev U", "chebyshev C", "chebyshev S", "shifted chebyshev T",
    "shifted chebyshev U", "jacobi polynomial" (alpha=, beta=), "shifted jacobi polynomial" (p=, q=), "gegenbauer
    polynomial" (alpha=), "laguerre polynomial" (0 to infinity), "generalized laguerre polynomial" (alpha=),
    "hermite polynomial", "probabilists hermite polynomial"; SciPy's names work too ("roots_legendre", "p_roots").
    "newton cotes" gives the weights of how_many equally spaced points (scipy.integrate newton_cotes), and
    "lebedev" the points on a sphere for degree= (scipy.integrate lebedev_rule): a table with x, y, z and weight.
    """
    from scipy import integrate, special

    example = 'points = sdata.find_area_points("legendre", how_many=5)'
    plain = _find(name, AREA_RULES, AREA_SPELLINGS, {k: (v[0], v[1]) for k, v in AREA_RULES.items()})
    if plain is None:
        if name is None:
            raise SimplydataError('find_area_points() needs the name of a rule, such as "legendre".\n'
                                  f"For example:  {example}")
        raise choice_error("find_area_points", "name", name, list(AREA_RULES))
    function_name, _short, needs, interval, weight_function = AREA_RULES[plain]
    given = {"alpha": alpha, "beta": beta, "p": p, "q": q, "degree": degree}
    extra = [k for k, v in given.items() if v is not None and k not in needs]
    if extra:
        raise SimplydataError(f'find_area_points("{plain}") does not take {", ".join(e + "=" for e in extra)}.'
                              f"\nFor example:  {_rule_example(plain, needs)}")
    missing = [k for k in needs if given[k] is None]
    if missing:
        raise SimplydataError(f'find_area_points("{plain}") needs {" and ".join(m + "=" for m in missing)}.'
                              f"\nFor example:  {_rule_example(plain, needs)}")
    from .table import table as make_table

    if function_name == "lebedev_rule":
        level = _whole(degree, "degree", _rule_example(plain, needs), least=1)
        try:
            points, weights = integrate.lebedev_rule(level)
        except (ValueError, NotImplementedError) as error:
            raise SimplydataError(f"lebedev has no rule of degree {level} ({error}); degrees 3, 5, 7 ... 131 work, "
                                  "with some gaps.") from None
        print(f"The {weights.size} points and weights of the Lebedev rule of degree {level} on the sphere of radius 1: "
              "the area of f over the sphere is about the total of weight * f(x, y, z). SciPy: "
              f"integrate.lebedev_rule({level})")
        return make_table({"x": points[0].tolist(), "y": points[1].tolist(), "z": points[2].tolist(),
                           "weight": weights.tolist()})
    count = _whole(how_many, "how_many", example, least=1)
    if function_name == "newton_cotes":
        if count < 2:
            raise SimplydataError("newton cotes needs how_many= of 2 or more points.")
        weights, error_part = integrate.newton_cotes(count - 1, 1)
        print(f"The weights of the Newton-Cotes rule for {count} equally spaced points (step 1): the area is about "
              f"step * the total of weight * f(point); the error coefficient is {error_part:.6g}. SciPy: "
              f"integrate.newton_cotes({count - 1}, 1)")
        return make_table({"point": list(range(count)), "weight": np.asarray(weights, dtype=float).tolist()})
    values = [float(given[k]) for k in needs]
    points, weights = getattr(special, function_name)(count, *values)
    settings = "".join(f", {k}={given[k]!r}" for k in needs)
    call = f"special.{function_name}({count}{''.join(f', {v!r}' for v in values)})"
    print(f"The {count} points and weights of Gauss's rule for the {plain}{settings}: from {interval}, the area under "
          f"{weight_function} * f is about the total of weight * f(point). SciPy: {call}")
    return make_table({"point": np.asarray(points, dtype=float).tolist(),
                       "weight": np.asarray(weights, dtype=float).tolist()})


def _rule_example(plain: str, needs: tuple) -> str:
    sample = {"alpha": 0.5, "beta": 1.5, "p": 2.0, "q": 1.0, "degree": 7}
    options = "".join(f", {k}={sample[k]}" for k in needs)
    count = "" if plain == "lebedev" else ", how_many=5"
    return f'points = sdata.find_area_points("{plain}"{count}{options})'
