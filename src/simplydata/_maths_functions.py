"""The one name table of the maths family (families for 100 %, plan section 2.3, approved by Manish 2026-11-28, G1-G3).

Each maths function of scipy.special and each NumPy function that works number by number has ONE plain name here
("bessel J", "inverse error function"), and its library names work too ("jv", "erfinv", "special.jv"). The same
table serves:

* numbers.take_function("bessel J", order=1) (and grid.take_function, block.take_function): the numbers are the
  input written x below, the other inputs are options with plain names (order=, degree=, a= ...);
* formula text (table.add_column, table.fit_formula, sdata.find_where_smallest, sdata.solve, sdata.formula ...):
  the formula name (the plain name with _ for spaces: bessel_j(1, x)), the library name (jv is the one exception,
  below) and SymPy's own name where SymPy has the same function (besseli(1, x), erfinv(x), LambertW(x)). Inside
  formula text the inputs come in the order of the library (the numbers where x stands); SymPy's name takes SymPy's
  order. sdata.formula keeps SymPy's function where there is one, so its exact words (slopes, series, limits) know it;
  a function SymPy does not have is worked out by SciPy (SymPy implemented_function) and keeps its name.
* sdata.find_zeros_of and sdata.find_area_points use the same plain names for the functions and polynomials.

Names that already meant something in formula text keep that meaning: besselJ(x, nu) and besselj(x, nu) (R's
order), jv, gammaln, loggamma and psi (a pointer to besselJ, lgamma and digamma), round, sign, log10, log1p, cbrt,
floor and ceil. SciPy's jn and yn (Bessel J and Y of whole order) are SciPy's in formula text; SymPy's jn and yn
(spherical Bessel functions) are spherical_bessel_j and spherical_bessel_y there.

Every name is tested against its library on sample numbers, with negative numbers and 0 (tests/test_maths_family.py).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np

# ---------------------------------------------------------------------------------------------------------- groups
TRIG = "angles and hyperbolic functions"
POWER = "powers, logs and exponentials"
PARTS = "parts and signs of numbers"
WHOLE = "whole numbers and counting"
GAMMA = "gamma and beta functions"
ERROR = "error functions and integrals"
BESSEL = "Bessel, Struve and Kelvin functions"
AIRY = "Airy functions"
ELLIPTIC = "elliptic integrals and functions"
HYPER = "hypergeometric and parabolic cylinder functions"
POLY = "polynomials and Legendre functions"
WAVES = "Mathieu and spheroidal wave functions"
OTHER = "zeta, Lambert W and other functions"
STATS = "functions from statistics and machine learning"
GROUP_ORDER = (TRIG, POWER, PARTS, WHOLE, GAMMA, ERROR, BESSEL, AIRY, ELLIPTIC, HYPER, POLY, WAVES, OTHER, STATS)

NUMBERS_TRY = (-1.5, 0.0, 0.5, 2.0)  # the numbers each name is tested on: a negative number, 0 and two above 0


@dataclass(frozen=True)
class MathsFunction:
    """One function of the family.

    plain:    the plain name (unique); its formula name is the plain name with _ for spaces (bessel_j)
    library:  "special.jv" (scipy.special) or "np.sinh" (NumPy)
    inputs:   the inputs in the library's order; "x" is where the numbers go, the others are options
    about:    one line on what it is
    group:    where sdata.help lists it
    names:    other names (the library's short name is one by itself)
    defaults: options that may be left out -> their value
    part:     which answer, for a library function that gives several (airy gives Ai, Ai', Bi, Bi')
    sympy:    SymPy's own function with the same values, as a call in input names ("besseli(order, x)"); that name
              works in formula text too, in SymPy's order
    sympy_expr: the same function written with SymPy functions (no name of its own in formula text)
    sample:   options for the tests and the examples
    numbers:  the numbers for the tests (a negative number and 0 among them where the function takes them)
    whole:    inputs that are whole numbers (the numbers are, when "x" is in it)
    compute:  how to work it out when the library function is not called directly (non-ufuncs, one answer of
              several); called with the inputs in order
    also:     other library functions that give the same values (np.exp2 and special.exp2)
    formula:  whether formula text knows it (not for answers that are complex numbers)
    complex_answer: the library gives complex numbers (take_function(part=) chooses the part)
    yes_no:   the answers are yes or no values
    domain:   where the function has a value, for the note about empty answers
    library_is_name: whether the library's short name is a name of this entry (not when another entry has it)
    """

    plain: str
    library: str
    inputs: tuple
    about: str
    group: str
    names: tuple = ()
    defaults: dict = field(default_factory=dict)
    part: int | None = None
    sympy: str = ""
    sympy_expr: str = ""
    sample: dict = field(default_factory=dict)
    numbers: tuple = NUMBERS_TRY
    whole: tuple = ()
    compute: object = None
    also: tuple = ()
    formula: bool = True
    complex_answer: bool = False
    yes_no: bool = False
    domain: str = ""
    library_is_name: bool = True

    @property
    def library_name(self) -> str:
        return self.library.split(".", 1)[1]

    @property
    def namespace(self) -> str:
        return self.library.split(".", 1)[0]

    @property
    def options(self) -> tuple:
        return tuple(name for name in self.inputs if name != "x")

    @property
    def needed(self) -> tuple:
        return tuple(name for name in self.options if name not in self.defaults)

    @property
    def formula_name(self) -> str:
        return snake(self.plain)

    def library_function(self):
        module = _module(self.namespace)
        return getattr(module, self.library_name)

    def library_call(self, numbers: str = "x", values: dict | None = None) -> str:
        """How the call is written in the library: special.jv(1, x)."""
        shown = []
        for name in self.inputs:
            if name == "x":
                shown.append(numbers)
            elif values is not None and name in values:
                shown.append(_short(values[name]))
            else:
                shown.append(name)
        head = "special" if self.namespace == "special" else "np"
        tail = "" if self.part is None else f"[{self.part}]"
        return f"{head}.{self.library_name}({', '.join(shown)}){tail}"

    def evaluate(self, *values):
        """The answer for the inputs in order (NumPy arrays or numbers), as the library gives it."""
        with np.errstate(all="ignore"):
            if self.compute is not None:
                out = self.compute(*values)
            else:
                out = self.library_function()(*values)
        if self.part is not None and self.compute is None:
            out = out[self.part]
        return out


def snake(text: str) -> str:
    """The formula name of a plain name: bessel J -> bessel_j, (exp(x) - 1) / x -> its letters joined by _."""
    return re.sub(r"[^0-9a-z]+", "_", text.lower()).strip("_")


def normal(text: str) -> str:
    """A name as it is looked up: small letters, and spaces, _ and - all the same."""
    return re.sub(r"[\s_\-]+", " ", str(text).strip().lower())


def _module(namespace: str):
    if namespace == "special":
        from scipy import special

        return special
    return np


def _short(value) -> str:
    if isinstance(value, (list, tuple, np.ndarray)) or hasattr(value, "_values"):
        return "other_numbers"
    if isinstance(value, float) and value.is_integer():
        return repr(value)
    return repr(value)


# ------------------------------------------------------------------------------------------- computing helpers
def _sp():
    from scipy import special

    return special


def _each(function):
    """A function of single numbers made to work number by number (np.vectorize, decimals out)."""
    return np.vectorize(function, otypes=[float])


def _first(values):
    """The first slice of SciPy's newer Legendre functions, which put the slopes in front: the values themselves."""
    return np.asarray(values)[0]


def _bernoulli(n):
    def one(k):
        if not (k >= 0 and float(k).is_integer()):
            return np.nan
        return float(_sp().bernoulli(int(k))[int(k)])
    return _each(one)(n)


def _euler(n):
    def one(k):
        if not (k >= 0 and float(k).is_integer()):
            return np.nan
        return float(_sp().euler(int(k))[int(k)])
    return _each(one)(n)


def _whole_or_nan(function):
    """Call function(k, *rest) only when k is a whole number 0 or above (the sequences of SciPy need one)."""
    def one(k, *rest):
        if not (k >= 0 and float(k).is_integer()):
            return np.nan
        return float(np.real(function(int(k), *rest)))
    return _each(one)


def _lmbda(v, x, which):
    def one(order, point):
        values = _sp().lmbda(order, point)[which]
        return float(values[-1])
    return _each(one)(v, x)


def _riccati(kind, n, x, which):
    function = _sp().riccati_jn if kind == "j" else _sp().riccati_yn
    return _whole_or_nan(lambda k, point: function(k, point)[which][k])(n, x)


def _lqn(n, x, which):
    return _whole_or_nan(lambda k, point: _sp().lqn(k, point)[which][k])(n, x)


def _lqmn(m, n, x):
    def one(order, degree, point):
        if not (order >= 0 and degree >= 0 and float(order).is_integer() and float(degree).is_integer()):
            return np.nan
        return float(_sp().lqmn(int(order), int(degree), point)[0][int(order), int(degree)])
    return _each(one)(m, n, x)


def _mathieu_coefficient(kind, m, q, k):
    function = _sp().mathieu_even_coef if kind == "even" else _sp().mathieu_odd_coef

    def one(order, strength, which):
        if not (order >= 0 and float(order).is_integer() and which >= 0 and float(which).is_integer()):
            return np.nan
        values = function(int(order), strength)
        return float(values[int(which)]) if int(which) < len(values) else np.nan
    return _each(one)(m, q, k)


def _multigammaln(a, d):
    return _each(lambda value, size: _sp().multigammaln(value, int(size)) if value > (size - 1) / 2 else np.nan)(a, d)


def _ellip_harm(h2, k2, n, p, s):
    return _each(lambda *v: _sp().ellip_harm(v[0], v[1], int(v[2]), int(v[3]), v[4]))(h2, k2, n, p, s)


def _ellip_harm_2(h2, k2, n, p, s):
    return _each(lambda *v: _sp().ellip_harm_2(v[0], v[1], int(v[2]), int(v[3]), v[4]))(h2, k2, n, p, s)


def _ellip_normal(h2, k2, n, p):
    return _each(lambda *v: _sp().ellip_normal(v[0], v[1], int(v[2]), int(v[3])))(h2, k2, n, p)


def _diric(x, n):
    return _each(lambda value, size: _sp().diric(value, int(size)))(x, n)


def _softmax(x):
    values = np.asarray(x, dtype=float)
    return _sp().softmax(values, axis=None)


def _log_softmax(x):
    values = np.asarray(x, dtype=float)
    return _sp().log_softmax(values, axis=None)


def _logsumexp(x):
    values = np.asarray(x, dtype=float)
    return _sp().logsumexp(values)


def _lambertw(z, k):
    return _sp().lambertw(z, np.asarray(k).astype(int) if np.ndim(k) else int(k))


def _frexp(which):
    return lambda x: np.frexp(x)[which]


def _divmod(which):
    return lambda x, y: np.divmod(x, y)[which]


def _sh_jacobi(n, p, q, x):
    return _sp().eval_sh_jacobi(n, p, q, x)


def _lower_gamma(a, x):
    return _sp().gammainc(a, x) * _sp().gamma(a)


def _upper_gamma(a, x):
    return _sp().gammaincc(a, x) * _sp().gamma(a)


def _zeta(x, q):
    return _sp().zeta(x) if q is None else _sp().zeta(x, q)


def _spence(x):
    return _sp().spence(x)


# ---------------------------------------------------------------------------------------------------- the table
def _f(plain, library, inputs, about, group, **options) -> MathsFunction:
    if isinstance(inputs, str):
        inputs = tuple(inputs.split())
    for key in ("names", "whole", "also", "numbers"):
        if isinstance(options.get(key), str):
            options[key] = tuple(options[key].split())
    return MathsFunction(plain, library, inputs, about, group, **options)


WHOLE_TRY = (0.0, 1.0, 2.0, 5.0)  # numbers for functions of whole numbers
ABOVE_ZERO = (0.25, 0.5, 1.5, 3.0)
UNIT = (-0.9, 0.0, 0.3, 0.75)  # inside -1 to 1
CHANCES = (0.0, 0.1, 0.5, 0.9)

TABLE: list[MathsFunction] = [
    # ---------------------------------------------------------------- angles and hyperbolic functions (NumPy)
    _f("inverse sine", "np.arcsin", "x", "the angle (radians) whose sine is the number, for numbers from -1 to 1",
       TRIG, names="asin arcsine", sympy="asin(x)", numbers=(-1.5, -1.0, 0.0, 0.5), domain="from -1 to 1",
       formula=False),
    _f("inverse cosine", "np.arccos", "x", "the angle (radians) whose cosine is the number, for numbers from -1 to 1",
       TRIG, names="acos arccosine", sympy="acos(x)", numbers=(-1.5, -1.0, 0.0, 0.5), domain="from -1 to 1",
       formula=False),
    _f("inverse tangent", "np.arctan", "x", "the angle (radians, from -pi/2 to pi/2) whose tangent is the number",
       TRIG, names="atan arctangent", sympy="atan(x)", formula=False),
    _f("angle of point", "np.arctan2", "x x_values", "the angle (radians, from -pi to pi) of the point (x_values, "
       "number): numbers are the y values", TRIG, names="atan2", sympy="atan2(x, x_values)",
       sample={"x_values": -1.0}, formula=False),
    _f("hyperbolic sine", "np.sinh", "x", "(e**x - e**-x) / 2", TRIG, names="sinh", sympy="sinh(x)"),
    _f("hyperbolic cosine", "np.cosh", "x", "(e**x + e**-x) / 2", TRIG, names="cosh", sympy="cosh(x)"),
    _f("hyperbolic tangent", "np.tanh", "x", "sinh(x) / cosh(x), between -1 and 1", TRIG, names="tanh",
       sympy="tanh(x)"),
    _f("inverse hyperbolic sine", "np.arcsinh", "x", "the number whose sinh is x", TRIG, names="asinh",
       sympy="asinh(x)"),
    _f("inverse hyperbolic cosine", "np.arccosh", "x", "the number (0 or above) whose cosh is x, for x of 1 or "
       "above", TRIG, names="acosh", sympy="acosh(x)", numbers=(-1.5, 0.0, 1.0, 2.0), domain="of 1 or above"),
    _f("inverse hyperbolic tangent", "np.arctanh", "x", "the number whose tanh is x, for x between -1 and 1", TRIG,
       names="atanh", sympy="atanh(x)", numbers=(-1.5, -1.0, 0.0, 0.5), domain="between -1 and 1"),
    _f("hypotenuse", "np.hypot", "x other", "sqrt(x**2 + other**2): the long side of a right triangle", TRIG,
       names="hypot", sympy_expr="sqrt(x**2 + other**2)", sample={"other": 3.0}),
    _f("sine of degrees", "special.sindg", "x", "the sine of an angle in degrees", TRIG, names="sindg",
       sympy_expr="sin(pi*x/180)", numbers=(-90.0, 0.0, 30.0, 180.0)),
    _f("cosine of degrees", "special.cosdg", "x", "the cosine of an angle in degrees", TRIG, names="cosdg",
       sympy_expr="cos(pi*x/180)", numbers=(-90.0, 0.0, 60.0, 180.0)),
    _f("tangent of degrees", "special.tandg", "x", "the tangent of an angle in degrees", TRIG, names="tandg",
       sympy_expr="tan(pi*x/180)", numbers=(-45.0, 0.0, 30.0, 90.0)),
    _f("cotangent of degrees", "special.cotdg", "x", "the cotangent (1 / tangent) of an angle in degrees", TRIG,
       names="cotdg", sympy_expr="cot(pi*x/180)", numbers=(-45.0, 0.0, 30.0, 90.0)),
    _f("degrees minutes seconds to radians", "special.radian", "x minutes seconds", "an angle given as degrees, "
       "minutes and seconds, in radians", TRIG, names="radian", sample={"minutes": 30.0, "seconds": 15.0},
       sympy_expr="pi*(x + minutes/60 + seconds/3600)/180"),
    _f("cosine minus 1", "special.cosm1", "x", "cos(x) - 1, exact also for x near 0", TRIG, names="cosm1",
       sympy_expr="cos(x) - 1"),
    _f("sinc", "np.sinc", "x", "sin(pi x) / (pi x), and 1 at 0 (as NumPy and scipy.special sinc)", TRIG,
       names="normalized_sinc", also=("special.sinc",), formula=False),
    # ---------------------------------------------------------------- powers, logs and exponentials
    _f("two to the power", "np.exp2", "x", "2 ** x", POWER, names="exp2", also=("special.exp2",),
       sympy_expr="2**x"),
    _f("ten to the power", "special.exp10", "x", "10 ** x", POWER, names="exp10", sympy_expr="10**x"),
    _f("exp minus 1", "np.expm1", "x", "e**x - 1, exact also for x near 0", POWER, names="expm1",
       also=("special.expm1",), sympy_expr="exp(x) - 1"),
    _f("log of 1 plus", "np.log1p", "x", "log(1 + x), exact also for x near 0; x above -1", POWER,
       also=("special.log1p",), domain="above -1", formula=False),
    _f("relative exp", "special.exprel", "x", "(e**x - 1) / x, and 1 at 0", POWER, names="exprel"),
    _f("power minus 1", "special.powm1", "x power", "x ** power - 1, exact also when the answer is near 0", POWER,
       names="powm1", sample={"power": 0.5}, numbers=(0.0, 0.5, 1.0, 4.0)),
    _f("log of sum of exps", "np.logaddexp", "x other", "log(e**x + e**other), without overflow", POWER,
       names="logaddexp", sympy_expr="log(exp(x) + exp(other))", sample={"other": 1.0}),
    _f("log2 of sum of powers of 2", "np.logaddexp2", "x other", "log2(2**x + 2**other), without overflow", POWER,
       names="logaddexp2", sympy_expr="log(2**x + 2**other, 2)", sample={"other": 1.0}),
    _f("x times log y", "special.xlogy", "x y", "x * log(y), and 0 where x is 0", POWER, names="xlogy",
       sample={"y": 2.0}),
    _f("x times log of 1 plus y", "special.xlog1py", "x y", "x * log(1 + y), and 0 where x is 0", POWER,
       names="xlog1py", sample={"y": 2.0}),
    _f("cube root", "special.cbrt", "x", "the number whose cube is x, also below 0 (numbers.take_cube_root does it "
       "too)", POWER, also=("np.cbrt",), formula=False),
    _f("reciprocal", "np.reciprocal", "x", "1 / x (worked out in decimals; 1 / 0 is inf)", POWER,
       sympy_expr="1/x"),
    # ---------------------------------------------------------------- parts and signs of numbers (NumPy)
    _f("sign", "np.sign", "x", "-1 for a number below 0, 0 for 0, 1 above 0", PARTS, formula=False),
    _f("with sign of", "np.copysign", "x sign_from", "the size of each number with the sign of sign_from", PARTS,
       names="copysign", sample={"sign_from": -1.0}),
    _f("has minus sign", "np.signbit", "x", "yes where the number has a minus sign (also -0.0)", PARTS,
       names="signbit", yes_no=True, formula=False),
    _f("mantissa", "np.frexp", "x", "the m of x = m * 2**e, with m from 0.5 to 1 (in size)", PARTS,
       compute=_frexp(0), formula=False),
    _f("exponent of two", "np.frexp", "x", "the e of x = m * 2**e (a whole number)", PARTS, compute=_frexp(1),
       formula=False),
    _f("times power of two", "np.ldexp", "x power", "x * 2**power, for a whole power", PARTS, names="ldexp",
       sample={"power": 3}, whole=("power",), sympy_expr="x*2**power"),
    _f("next decimal towards", "np.nextafter", "x towards", "the next decimal number the computer can hold, from x "
       "towards another number", PARTS, names="nextafter", sample={"towards": 10.0}, formula=False),
    _f("gap to next decimal", "np.spacing", "x", "the distance from x to the next decimal number the computer can "
       "hold", PARTS, names="spacing", formula=False),
    _f("remainder", "np.remainder", "x divisor", "what is left after dividing by divisor, with the sign of divisor "
       "(as Python's %)", PARTS, names="mod", sample={"divisor": 2.0}),
    _f("remainder with sign of number", "np.fmod", "x divisor", "what is left after dividing by divisor, with the "
       "sign of the number (as C's fmod)", PARTS, names="fmod", sample={"divisor": 2.0}),
    _f("division rounded down", "np.floor_divide", "x divisor", "x / divisor rounded down (as Python's //); "
       "numbers.divide_by(rounding_down=True) does it too", PARTS, sample={"divisor": 2.0}, compute=_divmod(0),
       names="floor_divide"),
    _f("step function", "np.heaviside", "x at_zero", "0 below 0, 1 above 0, and at_zero= at 0 (half, unless "
       "given)", PARTS, names="heaviside", defaults={"at_zero": 0.5}, sympy="Heaviside(x, at_zero)"),
    _f("unchanged", "np.positive", "x", "the numbers themselves (+x)", PARTS, names="positive", sympy_expr="x"),
    _f("complex conjugate", "np.conjugate", "x", "the complex conjugate: simplydata numbers are real, so they stay "
       "the same", PARTS, names="conjugate conj", sympy="conjugate(x)", formula=False),
    _f("angle of complex number", "np.angle", "x", "the angle of a complex number: for real numbers 0 (or pi below "
       "0)", PARTS, names="angle", formula=False),
    _f("real part", "np.real", "x", "the real part: simplydata numbers are real, so they stay the same", PARTS,
       names="real", formula=False),
    _f("imaginary part", "np.imag", "x", "the imaginary part: 0 for real numbers", PARTS, names="imag",
       formula=False),
    _f("round to whole number", "special.round", "x", "the nearest whole number, halves to the even one", PARTS,
       formula=False),
    # ---------------------------------------------------------------- whole numbers and counting
    _f("greatest common divisor", "np.gcd", "x other", "the biggest whole number that divides both", WHOLE,
       names="gcd", sample={"other": 12}, numbers=(-8.0, 0.0, 9.0, 18.0), whole=("x", "other")),
    _f("least common multiple", "np.lcm", "x other", "the smallest whole number both divide", WHOLE, names="lcm",
       sample={"other": 4}, numbers=(-6.0, 0.0, 3.0, 10.0), whole=("x", "other")),
    _f("binomial coefficient", "special.binom", "x k", "x choose k, for any numbers (as R choose)", WHOLE,
       names="binomial", sympy="binomial(x, k)", sample={"k": 2.0}, numbers=(-1.5, 0.0, 3.0, 6.0)),
    _f("rising factorial", "special.poch", "x steps", "x (x + 1) ... (x + steps - 1), the Pochhammer symbol",
       WHOLE, names="pochhammer", sympy="RisingFactorial(x, steps)", sample={"steps": 3.0}),
    _f("double factorial", "special.factorial2", "x", "x (x - 2) (x - 4) ... down to 1 or 2 (0 below 0)", WHOLE,
       sympy="factorial2(x)", numbers=(-1.0, 0.0, 5.0, 6.0), whole=("x",),
       compute=lambda x: _sp().factorial2(x, exact=False)),
    _f("multifactorial", "special.factorialk", "x k", "x (x - k) (x - 2k) ... (0 below 0)", WHOLE,
       sample={"k": 3}, numbers=(-1.0, 0.0, 5.0, 7.0), whole=("x", "k"),
       compute=lambda x, k: _each(lambda n, step: _sp().factorialk(int(n), int(step), exact=False))(x, k)),
    _f("stirling number of the second kind", "special.stirling2", "x k", "the ways to split x things into k groups "
       "that are not empty", WHOLE, names="stirling2", sample={"k": 2}, numbers=(0.0, 2.0, 4.0, 6.0),
       whole=("x", "k"), compute=lambda x, k: _sp().stirling2(x, k, exact=False)),
    _f("bernoulli number", "special.bernoulli", "x", "the Bernoulli number B_x (B_1 = -1/2, as SciPy; SymPy's own "
       "bernoulli(1) is +1/2)", WHOLE, numbers=(0.0, 1.0, 2.0, 4.0), whole=("x",), compute=_bernoulli),
    _f("euler number", "special.euler", "x", "the Euler number E_x", WHOLE, sympy="euler(x)",
       numbers=(0.0, 1.0, 2.0, 4.0), whole=("x",), compute=_euler),
    # ---------------------------------------------------------------- gamma and beta
    _f("gamma", "special.gamma", "x", "the gamma function: (x - 1)! for whole numbers", GAMMA,
       numbers=(-1.5, 0.5, 1.0, 4.0), formula=False),
    _f("log of gamma size", "special.gammaln", "x", "log of the size of gamma(x) (R lgamma)", GAMMA,
       numbers=(-1.5, 0.5, 1.0, 4.0), formula=False),
    _f("complex log gamma", "special.loggamma", "x", "the principal log of gamma(x); for real x below 0 it has no "
       "real value", GAMMA, numbers=(-1.5, 0.5, 1.0, 4.0), formula=False, domain="above 0 (as real numbers)"),
    _f("gamma sign", "special.gammasgn", "x", "the sign of gamma(x): 1 or -1", GAMMA, names="gammasgn",
       numbers=(-1.5, -0.5, 0.5, 4.0)),
    _f("reciprocal gamma", "special.rgamma", "x", "1 / gamma(x), 0 at 0 and the whole numbers below it", GAMMA,
       names="rgamma", sympy_expr="1/gamma(x)", numbers=(-1.5, 0.0, 0.5, 4.0)),
    _f("digamma", "special.digamma", "x", "the slope of log gamma: psi(x)", GAMMA, names="psi",
       numbers=(-1.5, 0.5, 1.0, 4.0), formula=False),
    _f("polygamma", "special.polygamma", "order x", "the order-th slope of digamma", GAMMA,
       sympy="polygamma(order, x)", sample={"order": 1}, whole=("order",), numbers=(-1.5, 0.5, 1.0, 4.0)),
    _f("log of multivariate gamma", "special.multigammaln", "x dimension", "the log of the multivariate gamma "
       "function, for x above (dimension - 1) / 2", GAMMA, names="multigammaln", sample={"dimension": 3},
       whole=("dimension",), numbers=(0.5, 1.5, 2.0, 4.0), compute=_multigammaln, domain="above (dimension - 1) / 2"),
    _f("regularized lower incomplete gamma", "special.gammainc", "a x", "the share of gamma(a) from 0 to x (the "
       "gamma distribution's chance below x)", GAMMA, names="gammainc", sample={"a": 2.0},
       sympy_expr="lowergamma(a, x)/gamma(a)", numbers=(-1.5, 0.0, 0.5, 2.0), domain="of 0 or above"),
    _f("regularized upper incomplete gamma", "special.gammaincc", "a x", "1 - the regularized lower incomplete "
       "gamma", GAMMA, names="gammaincc", sample={"a": 2.0}, sympy_expr="uppergamma(a, x)/gamma(a)",
       numbers=(-1.5, 0.0, 0.5, 2.0), domain="of 0 or above"),
    _f("inverse regularized lower incomplete gamma", "special.gammaincinv", "a x", "the x where the regularized "
       "lower incomplete gamma reaches the number", GAMMA, names="gammaincinv", sample={"a": 2.0}, numbers=CHANCES,
       domain="from 0 to 1"),
    _f("inverse regularized upper incomplete gamma", "special.gammainccinv", "a x", "the x where the regularized "
       "upper incomplete gamma falls to the number", GAMMA, names="gammainccinv", sample={"a": 2.0},
       numbers=CHANCES, domain="from 0 to 1"),
    _f("lower incomplete gamma", "special.gammainc", "a x", "the area under t**(a-1) e**-t from 0 to x (SymPy "
       "lowergamma)", GAMMA, sympy="lowergamma(a, x)", sample={"a": 2.0}, compute=_lower_gamma, library_is_name=False,
       numbers=(-1.5, 0.0, 0.5, 2.0), domain="of 0 or above"),
    _f("upper incomplete gamma", "special.gammaincc", "a x", "the area under t**(a-1) e**-t from x on (SymPy "
       "uppergamma)", GAMMA, sympy="uppergamma(a, x)", sample={"a": 2.0}, compute=_upper_gamma, library_is_name=False,
       numbers=(-1.5, 0.0, 0.5, 2.0), domain="of 0 or above"),
    _f("beta", "special.beta", "x b", "the beta function B(x, b)", GAMMA, sample={"b": 2.0}, formula=False),
    _f("log of beta size", "special.betaln", "x b", "log of the size of beta(x, b) (R lbeta)", GAMMA,
       names="betaln", sample={"b": 2.0}, numbers=(-1.5, 0.5, 1.0, 4.0)),
    _f("regularized incomplete beta", "special.betainc", "a b x", "the share of beta(a, b) from 0 to x (the beta "
       "distribution's chance below x)", GAMMA, names="betainc", sample={"a": 2.0, "b": 3.0},
       sympy_expr="betainc_regularized(a, b, 0, x)", numbers=(-0.5, 0.0, 0.5, 1.0), domain="from 0 to 1"),
    _f("complementary regularized incomplete beta", "special.betaincc", "a b x", "1 - the regularized incomplete "
       "beta", GAMMA, names="betaincc", sample={"a": 2.0, "b": 3.0}, numbers=(-0.5, 0.0, 0.5, 1.0),
       domain="from 0 to 1"),
    _f("inverse regularized incomplete beta", "special.betaincinv", "a b x", "the x where the regularized "
       "incomplete beta reaches the number", GAMMA, names="betaincinv", sample={"a": 2.0, "b": 3.0},
       numbers=CHANCES, domain="from 0 to 1"),
    _f("inverse complementary regularized incomplete beta", "special.betainccinv", "a b x", "the x where 1 - the "
       "regularized incomplete beta reaches the number", GAMMA, names="betainccinv", sample={"a": 2.0, "b": 3.0},
       numbers=CHANCES, domain="from 0 to 1"),
    # ---------------------------------------------------------------- error functions and integrals
    _f("error function", "special.erf", "x", "erf(x)", ERROR, formula=False),
    _f("complementary error function", "special.erfc", "x", "1 - erf(x)", ERROR, formula=False),
    _f("scaled complementary error function", "special.erfcx", "x", "e**(x**2) erfc(x), without overflow", ERROR,
       names="erfcx", sympy_expr="exp(x**2)*erfc(x)"),
    _f("imaginary error function", "special.erfi", "x", "-i erf(i x)", ERROR, sympy="erfi(x)"),
    _f("inverse error function", "special.erfinv", "x", "the number whose erf is x, for x from -1 to 1", ERROR,
       sympy="erfinv(x)", numbers=(-1.5, -0.5, 0.0, 0.9), domain="from -1 to 1"),
    _f("inverse complementary error function", "special.erfcinv", "x", "the number whose erfc is x, for x from 0 "
       "to 2", ERROR, sympy="erfcinv(x)", numbers=(-0.5, 0.0, 0.5, 1.5), domain="from 0 to 2"),
    _f("faddeeva", "special.wofz", "x", "e**(-x**2) erfc(-i x), a complex number", ERROR, names="wofz",
       complex_answer=True, formula=False),
    _f("dawson integral", "special.dawsn", "x", "e**(-x**2) times the area under e**(t**2) from 0 to x", ERROR,
       names="dawsn dawson", sympy_expr="sqrt(pi)/2*exp(-x**2)*erfi(x)"),
    _f("voigt profile", "special.voigt_profile", "x sigma gamma", "a normal curve (sigma) and a Cauchy curve "
       "(gamma) put together", ERROR, sample={"sigma": 1.0, "gamma": 0.5}),
    _f("fresnel S", "special.fresnel", "x", "the area under sin(pi t**2 / 2) from 0 to x", ERROR, part=0,
       sympy="fresnels(x)"),
    _f("fresnel C", "special.fresnel", "x", "the area under cos(pi t**2 / 2) from 0 to x", ERROR, part=1,
       sympy="fresnelc(x)"),
    _f("modified fresnel plus F", "special.modfresnelp", "x", "the modified Fresnel integral F+ (complex)", ERROR,
       part=0, complex_answer=True, formula=False),
    _f("modified fresnel plus K", "special.modfresnelp", "x", "the modified Fresnel integral K+ (complex)", ERROR,
       part=1, complex_answer=True, formula=False),
    _f("modified fresnel minus F", "special.modfresnelm", "x", "the modified Fresnel integral F- (complex)", ERROR,
       part=0, complex_answer=True, formula=False),
    _f("modified fresnel minus K", "special.modfresnelm", "x", "the modified Fresnel integral K- (complex)", ERROR,
       part=1, complex_answer=True, formula=False),
    _f("sine integral", "special.sici", "x", "Si(x): the area under sin(t) / t from 0 to x", ERROR, part=0,
       sympy="Si(x)"),
    _f("cosine integral", "special.sici", "x", "Ci(x): Euler's gamma + log(x) + the area under (cos(t) - 1) / t; "
       "for x above 0", ERROR, part=1, sympy="Ci(x)", numbers=(-1.5, 0.0, 0.5, 2.0)),
    _f("hyperbolic sine integral", "special.shichi", "x", "Shi(x): the area under sinh(t) / t from 0 to x", ERROR,
       part=0, sympy="Shi(x)"),
    _f("hyperbolic cosine integral", "special.shichi", "x", "Chi(x); for x above 0", ERROR, part=1,
       sympy="Chi(x)", numbers=(-1.5, 0.0, 0.5, 2.0)),
    _f("exponential integral Ei", "special.expi", "x", "Ei(x): the principal value of the area under e**t / t up "
       "to x", ERROR, names="expi Ei", sympy="Ei(x)"),
    _f("exponential integral E1", "special.exp1", "x", "E1(x): the area under e**-t / t from x on, for x above 0",
       ERROR, names="exp1 E1", sympy_expr="expint(1, x)", numbers=(-1.5, 0.0, 0.5, 2.0), domain="above 0"),
    _f("exponential integral En", "special.expn", "order x", "En(x): the area under e**(-x t) / t**n from 1 on",
       ERROR, names="expn", sympy="expint(order, x)", sample={"order": 2}, whole=("order",),
       numbers=(-1.5, 0.0, 0.5, 2.0), domain="of 0 or above"),
    # ---------------------------------------------------------------- Bessel, Struve and Kelvin functions
    _f("bessel J", "special.jv", "order x", "the Bessel function of the first kind (formula text: bessel_j(order, "
       "x), or besselJ(x, order) as R)", BESSEL, names="jn bessel_first_kind", sample={"order": 1.0},
       sympy_expr="besselj(order, x)"),
    _f("bessel J scaled", "special.jve", "order x", "jv(order, x) * e**-|imaginary part of x|: the same as bessel "
       "J for real numbers", BESSEL, names="jve", sample={"order": 1.0}),
    _f("bessel J0", "special.j0", "x", "the Bessel function of the first kind of order 0", BESSEL, names="j0",
       sympy_expr="besselj(0, x)"),
    _f("bessel J1", "special.j1", "x", "the Bessel function of the first kind of order 1", BESSEL, names="j1",
       sympy_expr="besselj(1, x)"),
    _f("bessel Y", "special.yv", "order x", "the Bessel function of the second kind, for x above 0", BESSEL,
       names="yv bessel_second_kind", sample={"order": 1.0}, sympy="bessely(order, x)", domain="above 0"),
    _f("bessel Y whole order", "special.yn", "order x", "the Bessel function of the second kind of a whole order",
       BESSEL, names="yn", sample={"order": 1}, whole=("order",), sympy_expr="bessely(order, x)", domain="above 0"),
    _f("bessel Y scaled", "special.yve", "order x", "yv(order, x) * e**-|imaginary part of x|", BESSEL,
       names="yve", sample={"order": 1.0}, domain="above 0"),
    _f("bessel Y0", "special.y0", "x", "the Bessel function of the second kind of order 0", BESSEL, names="y0",
       sympy_expr="bessely(0, x)", domain="above 0"),
    _f("bessel Y1", "special.y1", "x", "the Bessel function of the second kind of order 1", BESSEL, names="y1",
       sympy_expr="bessely(1, x)", domain="above 0"),
    _f("bessel I", "special.iv", "order x", "the modified Bessel function of the first kind", BESSEL,
       names="iv modified_bessel_first_kind", sample={"order": 1.0}, sympy="besseli(order, x)"),
    _f("bessel I scaled", "special.ive", "order x", "iv(order, x) * e**-|x|", BESSEL, names="ive",
       sample={"order": 1.0}),
    _f("bessel I0", "special.i0", "x", "the modified Bessel function of the first kind of order 0 (NumPy i0 too)",
       BESSEL, also=("np.i0",), sympy_expr="besseli(0, x)"),
    _f("bessel I1", "special.i1", "x", "the modified Bessel function of the first kind of order 1", BESSEL,
       names="i1", sympy_expr="besseli(1, x)"),
    _f("bessel I0 scaled", "special.i0e", "x", "i0(x) * e**-|x|", BESSEL, names="i0e"),
    _f("bessel I1 scaled", "special.i1e", "x", "i1(x) * e**-|x|", BESSEL, names="i1e"),
    _f("bessel K", "special.kv", "order x", "the modified Bessel function of the second kind, for x above 0",
       BESSEL, names="kv modified_bessel_second_kind", sample={"order": 1.0}, sympy="besselk(order, x)",
       domain="above 0"),
    _f("bessel K whole order", "special.kn", "order x", "the modified Bessel function of the second kind of a "
       "whole order", BESSEL, names="kn", sample={"order": 1}, whole=("order",), sympy_expr="besselk(order, x)",
       domain="above 0"),
    _f("bessel K scaled", "special.kve", "order x", "kv(order, x) * e**x", BESSEL, names="kve",
       sample={"order": 1.0}, domain="above 0"),
    _f("bessel K0", "special.k0", "x", "the modified Bessel function of the second kind of order 0", BESSEL,
       names="k0", sympy_expr="besselk(0, x)", domain="above 0"),
    _f("bessel K1", "special.k1", "x", "the modified Bessel function of the second kind of order 1", BESSEL,
       names="k1", sympy_expr="besselk(1, x)", domain="above 0"),
    _f("bessel K0 scaled", "special.k0e", "x", "k0(x) * e**x", BESSEL, names="k0e", domain="above 0"),
    _f("bessel K1 scaled", "special.k1e", "x", "k1(x) * e**x", BESSEL, names="k1e", domain="above 0"),
    _f("hankel H1", "special.hankel1", "order x", "the Hankel function of the first kind, J + iY (complex)", BESSEL,
       sample={"order": 1.0}, complex_answer=True, formula=False, numbers=ABOVE_ZERO),
    _f("hankel H1 scaled", "special.hankel1e", "order x", "hankel1(order, x) * e**(-i x) (complex)", BESSEL,
       sample={"order": 1.0}, complex_answer=True, formula=False, numbers=ABOVE_ZERO),
    _f("hankel H2", "special.hankel2", "order x", "the Hankel function of the second kind, J - iY (complex)", BESSEL,
       sample={"order": 1.0}, complex_answer=True, formula=False, numbers=ABOVE_ZERO),
    _f("hankel H2 scaled", "special.hankel2e", "order x", "hankel2(order, x) * e**(i x) (complex)", BESSEL,
       sample={"order": 1.0}, complex_answer=True, formula=False, numbers=ABOVE_ZERO),
    _f("bessel J slope", "special.jvp", "order x how_many_times", "the slope (how_many_times=2: the slope of the "
       "slope) of bessel J", BESSEL, defaults={"how_many_times": 1}, sample={"order": 1.0}, whole=("how_many_times",)),
    _f("bessel Y slope", "special.yvp", "order x how_many_times", "the slope of bessel Y", BESSEL,
       defaults={"how_many_times": 1}, sample={"order": 1.0}, whole=("how_many_times",), domain="above 0"),
    _f("bessel I slope", "special.ivp", "order x how_many_times", "the slope of bessel I", BESSEL,
       defaults={"how_many_times": 1}, sample={"order": 1.0}, whole=("how_many_times",)),
    _f("bessel K slope", "special.kvp", "order x how_many_times", "the slope of bessel K", BESSEL,
       defaults={"how_many_times": 1}, sample={"order": 1.0}, whole=("how_many_times",), domain="above 0"),
    _f("hankel H1 slope", "special.h1vp", "order x how_many_times", "the slope of hankel H1 (complex)", BESSEL,
       defaults={"how_many_times": 1}, sample={"order": 1.0}, whole=("how_many_times",), complex_answer=True,
       formula=False, numbers=ABOVE_ZERO),
    _f("hankel H2 slope", "special.h2vp", "order x how_many_times", "the slope of hankel H2 (complex)", BESSEL,
       defaults={"how_many_times": 1}, sample={"order": 1.0}, whole=("how_many_times",), complex_answer=True,
       formula=False, numbers=ABOVE_ZERO),
    _f("spherical bessel j", "special.spherical_jn", "order x", "the spherical Bessel function of the first kind "
       "(SymPy jn)", BESSEL, sample={"order": 1}, whole=("order",), sympy_expr="jn(order, x)"),
    _f("spherical bessel j slope", "special.spherical_jn", "order x", "the slope of spherical bessel j", BESSEL,
       sample={"order": 1}, whole=("order",)),
    _f("spherical bessel y", "special.spherical_yn", "order x", "the spherical Bessel function of the second kind "
       "(SymPy yn), for x above 0", BESSEL, sample={"order": 1}, whole=("order",), sympy_expr="yn(order, x)",
       domain="above 0"),
    _f("spherical bessel y slope", "special.spherical_yn", "order x", "the slope of spherical bessel y", BESSEL,
       sample={"order": 1}, whole=("order",), domain="above 0"),
    _f("modified spherical bessel i", "special.spherical_in", "order x", "the modified spherical Bessel function of "
       "the first kind", BESSEL, sample={"order": 1}, whole=("order",)),
    _f("modified spherical bessel i slope", "special.spherical_in", "order x", "the slope of modified spherical "
       "bessel i", BESSEL, sample={"order": 1}, whole=("order",)),
    _f("modified spherical bessel k", "special.spherical_kn", "order x", "the modified spherical Bessel function of "
       "the second kind, for x above 0", BESSEL, sample={"order": 1}, whole=("order",), domain="above 0"),
    _f("modified spherical bessel k slope", "special.spherical_kn", "order x", "the slope of modified spherical "
       "bessel k", BESSEL, sample={"order": 1}, whole=("order",), domain="above 0"),
    _f("riccati bessel first kind", "special.riccati_jn", "order x", "x times the spherical bessel j of the order",
       BESSEL, sample={"order": 2}, whole=("order",), compute=lambda n, x: _riccati("j", n, x, 0)),
    _f("riccati bessel first kind slope", "special.riccati_jn", "order x", "the slope of the riccati bessel first "
       "kind", BESSEL, sample={"order": 2}, whole=("order",), compute=lambda n, x: _riccati("j", n, x, 1)),
    _f("riccati bessel second kind", "special.riccati_yn", "order x", "x times the spherical bessel y of the order, "
       "for x above 0", BESSEL, sample={"order": 2}, whole=("order",), compute=lambda n, x: _riccati("y", n, x, 0),
       numbers=ABOVE_ZERO),
    _f("riccati bessel second kind slope", "special.riccati_yn", "order x", "the slope of the riccati bessel "
       "second kind", BESSEL, sample={"order": 2}, whole=("order",), compute=lambda n, x: _riccati("y", n, x, 1),
       numbers=ABOVE_ZERO),
    _f("jahnke emde lambda", "special.lmbda", "order x", "the Jahnke-Emde Lambda function, Lambda_order(x)", BESSEL,
       sample={"order": 1.5}, compute=lambda v, x: _lmbda(v, x, 0), numbers=(-1.5, 0.5, 1.0, 2.0)),
    _f("jahnke emde lambda slope", "special.lmbda", "order x", "the slope of the Jahnke-Emde Lambda function",
       BESSEL, sample={"order": 1.5}, compute=lambda v, x: _lmbda(v, x, 1), numbers=(-1.5, 0.5, 1.0, 2.0)),
    _f("bessel polynomial integral", "special.besselpoly", "x power order", "the area under t**power J_order(2 x t) "
       "from 0 to 1", BESSEL, names="besselpoly", sample={"power": 1.0, "order": 0.0}),
    _f("area under bessel J0", "special.itj0y0", "x", "the area under J0 from 0 to x", BESSEL, part=0),
    _f("area under bessel Y0", "special.itj0y0", "x", "the area under Y0 from 0 to x", BESSEL, part=1,
       numbers=ABOVE_ZERO),
    _f("area under 1 minus bessel J0 over t", "special.it2j0y0", "x", "the area under (1 - J0(t)) / t from 0 to x",
       BESSEL, part=0),
    _f("area under bessel Y0 over t", "special.it2j0y0", "x", "the area under Y0(t) / t from x to infinity",
       BESSEL, part=1, numbers=ABOVE_ZERO),
    _f("area under bessel I0", "special.iti0k0", "x", "the area under I0 from 0 to x", BESSEL, part=0),
    _f("area under bessel K0", "special.iti0k0", "x", "the area under K0 from 0 to x", BESSEL, part=1,
       numbers=ABOVE_ZERO),
    _f("area under bessel I0 minus 1 over t", "special.it2i0k0", "x", "the area under (I0(t) - 1) / t from 0 to x",
       BESSEL, part=0),
    _f("area under bessel K0 over t", "special.it2i0k0", "x", "the area under K0(t) / t from x to infinity",
       BESSEL, part=1, numbers=ABOVE_ZERO),
    _f("struve H", "special.struve", "order x", "the Struve function H", BESSEL, names="struve",
       sample={"order": 1.0}),
    _f("struve L", "special.modstruve", "order x", "the modified Struve function L", BESSEL, names="modstruve",
       sample={"order": 1.0}),
    _f("area under struve H0", "special.itstruve0", "x", "the area under H0 from 0 to x", BESSEL,
       names="itstruve0"),
    _f("area under struve H0 over t", "special.it2struve0", "x", "the area under H0(t) / t from x to infinity",
       BESSEL, names="it2struve0", numbers=ABOVE_ZERO),
    _f("area under struve L0", "special.itmodstruve0", "x", "the area under L0 from 0 to x", BESSEL,
       names="itmodstruve0"),
    _f("kelvin ber", "special.ber", "x", "the Kelvin function ber", BESSEL, names="ber"),
    _f("kelvin bei", "special.bei", "x", "the Kelvin function bei", BESSEL, names="bei"),
    _f("kelvin ker", "special.ker", "x", "the Kelvin function ker, for x above 0", BESSEL, names="ker",
       domain="above 0"),
    _f("kelvin kei", "special.kei", "x", "the Kelvin function kei, for x above 0", BESSEL, names="kei",
       domain="above 0"),
    _f("kelvin ber slope", "special.berp", "x", "the slope of ber", BESSEL, names="berp"),
    _f("kelvin bei slope", "special.beip", "x", "the slope of bei", BESSEL, names="beip"),
    _f("kelvin ker slope", "special.kerp", "x", "the slope of ker", BESSEL, names="kerp", domain="above 0"),
    _f("kelvin kei slope", "special.keip", "x", "the slope of kei", BESSEL, names="keip", domain="above 0"),
    # ---------------------------------------------------------------- Airy functions
    _f("airy Ai", "special.airy", "x", "the Airy function Ai", AIRY, part=0, sympy="airyai(x)"),
    _f("airy Ai slope", "special.airy", "x", "the slope of Ai", AIRY, part=1, sympy="airyaiprime(x)"),
    _f("airy Bi", "special.airy", "x", "the Airy function Bi", AIRY, part=2, sympy="airybi(x)"),
    _f("airy Bi slope", "special.airy", "x", "the slope of Bi", AIRY, part=3, sympy="airybiprime(x)"),
    _f("airy Ai scaled", "special.airye", "x", "Ai(x) * e**(2/3 x**1.5)", AIRY, part=0, numbers=ABOVE_ZERO),
    _f("airy Ai slope scaled", "special.airye", "x", "Ai'(x) * e**(2/3 x**1.5)", AIRY, part=1, numbers=ABOVE_ZERO),
    _f("airy Bi scaled", "special.airye", "x", "Bi(x) * e**(-|2/3 x**1.5|)", AIRY, part=2, numbers=ABOVE_ZERO),
    _f("airy Bi slope scaled", "special.airye", "x", "Bi'(x) * e**(-|2/3 x**1.5|)", AIRY, part=3,
       numbers=ABOVE_ZERO),
    _f("area under airy Ai", "special.itairy", "x", "the area under Ai from 0 to x, for x of 0 or above", AIRY,
       part=0, numbers=(0.0, 0.5, 1.0, 2.0)),
    _f("area under airy Bi", "special.itairy", "x", "the area under Bi from 0 to x", AIRY, part=1,
       numbers=(0.0, 0.5, 1.0, 2.0)),
    _f("area under airy Ai of minus t", "special.itairy", "x", "the area under Ai(-t) from 0 to x", AIRY, part=2,
       numbers=(0.0, 0.5, 1.0, 2.0)),
    _f("area under airy Bi of minus t", "special.itairy", "x", "the area under Bi(-t) from 0 to x", AIRY, part=3,
       numbers=(0.0, 0.5, 1.0, 2.0)),
    # ---------------------------------------------------------------- elliptic integrals and functions
    _f("complete elliptic integral first kind", "special.ellipk", "x", "K(m), with the parameter m = k**2 (SymPy "
       "elliptic_k)", ELLIPTIC, names="ellipk", sympy="elliptic_k(x)", numbers=(-1.5, 0.0, 0.5, 0.9),
       domain="below 1"),
    _f("complete elliptic integral first kind near 1", "special.ellipkm1", "x", "K(1 - p), exact for p near 0",
       ELLIPTIC, names="ellipkm1", sympy_expr="elliptic_k(1 - x)", numbers=(0.01, 0.1, 0.5, 1.0),
       domain="above 0"),
    _f("complete elliptic integral second kind", "special.ellipe", "x", "E(m) (SymPy elliptic_e)", ELLIPTIC,
       names="ellipe", sympy="elliptic_e(x)", numbers=(-1.5, 0.0, 0.5, 1.0), domain="of 1 or below"),
    _f("elliptic integral first kind", "special.ellipkinc", "x parameter", "F(phi, m): the numbers are phi "
       "(radians)", ELLIPTIC, names="ellipkinc", sympy="elliptic_f(x, parameter)", sample={"parameter": 0.5}),
    _f("elliptic integral second kind", "special.ellipeinc", "x parameter", "E(phi, m): the numbers are phi "
       "(radians)", ELLIPTIC, names="ellipeinc", sympy_expr="elliptic_e(x, parameter)", sample={"parameter": 0.5}),
    _f("jacobi sn", "special.ellipj", "x parameter", "the Jacobi elliptic function sn(u, m)", ELLIPTIC, part=0,
       sample={"parameter": 0.5}),
    _f("jacobi cn", "special.ellipj", "x parameter", "the Jacobi elliptic function cn(u, m)", ELLIPTIC, part=1,
       sample={"parameter": 0.5}),
    _f("jacobi dn", "special.ellipj", "x parameter", "the Jacobi elliptic function dn(u, m)", ELLIPTIC, part=2,
       sample={"parameter": 0.5}),
    _f("jacobi amplitude", "special.ellipj", "x parameter", "the amplitude phi with u = F(phi, m)", ELLIPTIC,
       part=3, sample={"parameter": 0.5}),
    _f("carlson RC", "special.elliprc", "x y", "Carlson's degenerate symmetric elliptic integral RC(x, y)",
       ELLIPTIC, names="elliprc", sample={"y": 2.0}, numbers=(-1.5, 0.0, 0.5, 2.0)),
    _f("carlson RD", "special.elliprd", "x y z", "Carlson's symmetric elliptic integral of the second kind RD",
       ELLIPTIC, names="elliprd", sample={"y": 1.0, "z": 2.0}, numbers=(-1.5, 0.0, 0.5, 2.0)),
    _f("carlson RF", "special.elliprf", "x y z", "Carlson's symmetric elliptic integral of the first kind RF",
       ELLIPTIC, names="elliprf", sample={"y": 1.0, "z": 2.0}, numbers=(-1.5, 0.0, 0.5, 2.0)),
    _f("carlson RG", "special.elliprg", "x y z", "Carlson's completely symmetric elliptic integral RG", ELLIPTIC,
       names="elliprg", sample={"y": 1.0, "z": 2.0}, numbers=(-1.5, 0.0, 0.5, 2.0)),
    _f("carlson RJ", "special.elliprj", "x y z p", "Carlson's symmetric elliptic integral of the third kind RJ",
       ELLIPTIC, names="elliprj", sample={"y": 1.0, "z": 2.0, "p": 3.0}, numbers=(-1.5, 0.0, 0.5, 2.0)),
    _f("ellipsoidal harmonic E", "special.ellip_harm", "h_squared k_squared degree order x", "the ellipsoidal "
       "harmonic E^p_n(s)", ELLIPTIC, names="ellip_harm", sample={"h_squared": 5.0, "k_squared": 8.0, "degree": 1,
                                                                  "order": 1},
       whole=("degree", "order"), compute=_ellip_harm, numbers=(2.5, 3.0, 4.0, 5.0), formula=False),
    _f("ellipsoidal harmonic F", "special.ellip_harm_2", "h_squared k_squared degree order x", "the ellipsoidal "
       "harmonic of the second kind F^p_n(s)", ELLIPTIC, names="ellip_harm_2",
       sample={"h_squared": 5.0, "k_squared": 8.0, "degree": 1, "order": 1}, whole=("degree", "order"),
       compute=_ellip_harm_2, numbers=(3.0, 4.0, 5.0, 8.0), formula=False),
    _f("ellipsoidal harmonic normalization", "special.ellip_normal", "x k_squared degree order", "the "
       "normalization constant gamma^p_n of the ellipsoidal harmonics: the numbers are h squared", ELLIPTIC,
       names="ellip_normal", sample={"k_squared": 8.0, "degree": 1, "order": 1}, whole=("degree", "order"),
       compute=_ellip_normal, numbers=(1.0, 2.0, 4.0, 5.0), formula=False),
    # ---------------------------------------------------------------- hypergeometric and parabolic cylinder
    _f("hypergeometric 0F1", "special.hyp0f1", "b x", "the confluent hypergeometric limit function 0F1(; b; x)",
       HYPER, names="hyp0f1", sample={"b": 1.5}, sympy_expr="hyper((), (b,), x)"),
    _f("confluent hypergeometric 1F1", "special.hyp1f1", "a b x", "Kummer's function 1F1(a; b; x)", HYPER,
       names="hyp1f1 kummer_M", sample={"a": 0.5, "b": 1.5}, sympy_expr="hyper((a,), (b,), x)"),
    _f("hypergeometric 2F1", "special.hyp2f1", "a b c x", "the Gauss hypergeometric function 2F1(a, b; c; x)",
       HYPER, names="hyp2f1", sample={"a": 0.5, "b": 1.0, "c": 1.5}, sympy_expr="hyper((a, b), (c,), x)",
       numbers=(-1.5, 0.0, 0.5, 0.9)),
    _f("confluent hypergeometric U", "special.hyperu", "a b x", "Tricomi's function U(a, b, x), for x above 0",
       HYPER, names="hyperu tricomi_U", sample={"a": 0.5, "b": 1.5}, numbers=ABOVE_ZERO),
    _f("parabolic cylinder D", "special.pbdv", "order x", "the parabolic cylinder function D_order(x)", HYPER,
       part=0, sample={"order": 1.0}),
    _f("parabolic cylinder D slope", "special.pbdv", "order x", "the slope of D_order(x)", HYPER, part=1,
       sample={"order": 1.0}),
    _f("parabolic cylinder V", "special.pbvv", "order x", "the parabolic cylinder function V_order(x)", HYPER,
       part=0, sample={"order": 1.0}),
    _f("parabolic cylinder V slope", "special.pbvv", "order x", "the slope of V_order(x)", HYPER, part=1,
       sample={"order": 1.0}),
    _f("parabolic cylinder W", "special.pbwa", "a x", "the parabolic cylinder function W(a, x), for x from -5 to 5",
       HYPER, part=0, sample={"a": 1.0}),
    _f("parabolic cylinder W slope", "special.pbwa", "a x", "the slope of W(a, x)", HYPER, part=1,
       sample={"a": 1.0}),
    # ---------------------------------------------------------------- polynomials and Legendre functions
    _f("legendre polynomial", "special.eval_legendre", "degree x", "the Legendre polynomial P_degree(x)", POLY,
       names="legendre", sympy="legendre(degree, x)", sample={"degree": 3}),
    _f("shifted legendre polynomial", "special.eval_sh_legendre", "degree x", "P_degree(2x - 1), on 0 to 1",
       POLY, names="sh_legendre", sympy_expr="legendre(degree, 2*x - 1)", sample={"degree": 3}),
    _f("chebyshev T", "special.eval_chebyt", "degree x", "the Chebyshev polynomial of the first kind", POLY,
       names="chebyshevt chebyt chebyshev_first_kind", sympy="chebyshevt(degree, x)", sample={"degree": 3}),
    _f("chebyshev U", "special.eval_chebyu", "degree x", "the Chebyshev polynomial of the second kind", POLY,
       names="chebyshevu chebyu chebyshev_second_kind", sympy="chebyshevu(degree, x)", sample={"degree": 3}),
    _f("chebyshev C", "special.eval_chebyc", "degree x", "2 T_degree(x / 2), on -2 to 2", POLY, names="chebyc",
       sympy_expr="2*chebyshevt(degree, x/2)", sample={"degree": 3}),
    _f("chebyshev S", "special.eval_chebys", "degree x", "U_degree(x / 2), on -2 to 2", POLY, names="chebys",
       sympy_expr="chebyshevu(degree, x/2)", sample={"degree": 3}),
    _f("shifted chebyshev T", "special.eval_sh_chebyt", "degree x", "T_degree(2x - 1), on 0 to 1", POLY,
       names="sh_chebyt",
       sympy_expr="chebyshevt(degree, 2*x - 1)", sample={"degree": 3}),
    _f("shifted chebyshev U", "special.eval_sh_chebyu", "degree x", "U_degree(2x - 1), on 0 to 1", POLY,
       names="sh_chebyu",
       sympy_expr="chebyshevu(degree, 2*x - 1)", sample={"degree": 3}),
    _f("jacobi polynomial", "special.eval_jacobi", "degree alpha beta x", "the Jacobi polynomial "
       "P_degree^(alpha, beta)(x)", POLY, names="jacobi", sympy="jacobi(degree, alpha, beta, x)",
       sample={"degree": 3, "alpha": 0.5, "beta": 1.5}),
    _f("shifted jacobi polynomial", "special.eval_sh_jacobi", "degree p q x", "the shifted Jacobi polynomial "
       "G_degree^(p, q)(x), on 0 to 1", POLY, names="sh_jacobi", sample={"degree": 3, "p": 2.0, "q": 1.0},
       compute=_sh_jacobi),
    _f("gegenbauer polynomial", "special.eval_gegenbauer", "degree alpha x", "the Gegenbauer (ultraspherical) "
       "polynomial C_degree^(alpha)(x)", POLY, names="gegenbauer", sympy="gegenbauer(degree, alpha, x)",
       sample={"degree": 3, "alpha": 1.5}),
    _f("laguerre polynomial", "special.eval_laguerre", "degree x", "the Laguerre polynomial L_degree(x)", POLY,
       names="laguerre", sympy="laguerre(degree, x)", sample={"degree": 3}),
    _f("generalized laguerre polynomial", "special.eval_genlaguerre", "degree alpha x", "the generalized "
       "(associated) Laguerre polynomial L_degree^(alpha)(x)", POLY, names="assoc_laguerre genlaguerre",
       sympy="assoc_laguerre(degree, alpha, x)", sample={"degree": 3, "alpha": 1.5}),
    _f("hermite polynomial", "special.eval_hermite", "degree x", "the physicists' Hermite polynomial H_degree(x)",
       POLY, names="hermite", sympy="hermite(degree, x)", sample={"degree": 3}, whole=("degree",)),
    _f("probabilists hermite polynomial", "special.eval_hermitenorm", "degree x", "the probabilists' Hermite "
       "polynomial He_degree(x)", POLY, names="hermite_prob hermitenorm", sympy="hermite_prob(degree, x)",
       sample={"degree": 3}, whole=("degree",)),
    _f("associated legendre function", "special.lpmv", "order degree x", "P_degree^order(x), with the "
       "Condon-Shortley sign (-1)**order (SymPy assoc_legendre)", POLY, names="lpmv",
       sympy="assoc_legendre(degree, order, x)", sample={"order": 1, "degree": 2}, numbers=UNIT),
    _f("associated legendre polynomial", "special.assoc_legendre_p", "degree order x", "SciPy's newer associated "
       "Legendre polynomial P_degree^order(x)", POLY, sample={"degree": 2, "order": 1}, whole=("degree", "order"),
       compute=lambda n, m, z: _first(_sp().assoc_legendre_p(np.asarray(n).astype(int), np.asarray(m).astype(int),
                                                             z)), numbers=UNIT),
    _f("spherical legendre polynomial", "special.sph_legendre_p", "degree order x", "the spherical Legendre "
       "polynomial of the angle theta (radians)", POLY, sample={"degree": 2, "order": 1}, whole=("degree", "order"),
       compute=lambda n, m, t: _first(_sp().sph_legendre_p(np.asarray(n).astype(int), np.asarray(m).astype(int),
                                                           t))),
    _f("spherical harmonic", "special.sph_harm_y", "degree order x phi", "the spherical harmonic Y_degree^order "
       "(theta, phi): the numbers are theta (complex)", POLY, sample={"degree": 2, "order": 1, "phi": 0.3},
       whole=("degree", "order"), complex_answer=True, formula=False,
       compute=lambda n, m, t, p: _sp().sph_harm_y(np.asarray(n).astype(int), np.asarray(m).astype(int), t, p)),
    _f("legendre Q", "special.lqn", "degree x", "the Legendre function of the second kind Q_degree(x)", POLY,
       sample={"degree": 2}, whole=("degree",), compute=lambda n, x: _lqn(n, x, 0), numbers=UNIT),
    _f("legendre Q slope", "special.lqn", "degree x", "the slope of Q_degree(x)", POLY, sample={"degree": 2},
       whole=("degree",), compute=lambda n, x: _lqn(n, x, 1), numbers=UNIT),
    _f("associated legendre Q", "special.lqmn", "order degree x", "the associated Legendre function of the second "
       "kind Q_degree^order(x)", POLY, sample={"order": 1, "degree": 2}, whole=("order", "degree"),
       compute=_lqmn, numbers=(-0.9, 0.0, 0.3, 0.75)),
    # ---------------------------------------------------------------- Mathieu and spheroidal wave functions
    _f("mathieu characteristic a", "special.mathieu_a", "order x", "the characteristic value a_order(q) of the even "
       "Mathieu functions: the numbers are q", WAVES, names="mathieu_a", sample={"order": 1}, whole=("order",)),
    _f("mathieu characteristic b", "special.mathieu_b", "order x", "the characteristic value b_order(q) of the odd "
       "Mathieu functions", WAVES, names="mathieu_b", sample={"order": 1}, whole=("order",)),
    _f("mathieu even coefficient", "special.mathieu_even_coef", "order x which", "Fourier coefficient number which "
       "(from 0) of the even Mathieu functions: the numbers are q", WAVES, sample={"order": 2, "which": 1},
       whole=("order", "which"), compute=lambda m, q, k: _mathieu_coefficient("even", m, q, k),
       numbers=(0.0, 0.5, 1.0, 2.0)),
    _f("mathieu odd coefficient", "special.mathieu_odd_coef", "order x which", "Fourier coefficient number which "
       "(from 0) of the odd Mathieu functions", WAVES, sample={"order": 2, "which": 1}, whole=("order", "which"),
       compute=lambda m, q, k: _mathieu_coefficient("odd", m, q, k), numbers=(0.0, 0.5, 1.0, 2.0)),
]

# the Mathieu functions: (plain, library) -> value and slope, the numbers are x in degrees
for _plain, _library, _about in [
        ("mathieu ce", "mathieu_cem", "the even Mathieu function ce_order(x, q)"),
        ("mathieu se", "mathieu_sem", "the odd Mathieu function se_order(x, q)"),
        ("modified mathieu ce first kind", "mathieu_modcem1", "the even modified Mathieu function of the first kind"),
        ("modified mathieu ce second kind", "mathieu_modcem2", "the even modified Mathieu function of the second "
                                                               "kind"),
        ("modified mathieu se first kind", "mathieu_modsem1", "the odd modified Mathieu function of the first kind"),
        ("modified mathieu se second kind", "mathieu_modsem2", "the odd modified Mathieu function of the second "
                                                               "kind")]:
    _angle = "the numbers are x in degrees" if _library in ("mathieu_cem", "mathieu_sem") else "the numbers are x"
    _try = (-90.0, 0.0, 30.0, 120.0) if _library in ("mathieu_cem", "mathieu_sem") else ABOVE_ZERO
    for _part, _tail in ((0, ""), (1, " slope")):
        TABLE.append(_f(_plain + _tail, "special." + _library, "order q x",
                        (_about + f" ({_angle})") if not _part else f"the slope of {_plain}", WAVES, part=_part,
                        sample={"order": 1, "q": 0.5}, whole=("order",), numbers=_try))

# the spheroidal wave functions: value and slope of each, without and with a characteristic value given
for _kind, _name in (("pro", "prolate"), ("obl", "oblate")):
    TABLE.append(_f(f"{_name} characteristic value", f"special.{_kind}_cv", "order degree x", f"the characteristic "
                    f"value of the {_name} spheroidal wave functions: the numbers are c", WAVES,
                    sample={"order": 0, "degree": 1}, whole=("order", "degree"), numbers=(0.5, 1.0, 2.0, 3.0),
                    names=f"{_kind}_cv"))
    for _what, _about in (("ang1", "angular function of the first kind"), ("rad1", "radial function of the first "
                                                                                    "kind"),
                          ("rad2", "radial function of the second kind")):
        _try = (-0.9, 0.0, 0.3, 0.75) if _what == "ang1" else (2.0, 2.5, 3.0, 4.0)
        for _cv in ("", "_cv"):
            _inputs = "order degree c x" if not _cv else "order degree c characteristic_value x"
            _sample = {"order": 0, "degree": 1, "c": 1.0}
            if _cv:
                _sample["characteristic_value"] = None  # filled in by the tests from pro_cv / obl_cv
            for _part, _tail in ((0, ""), (1, " slope")):
                _plain = f"{_name} {_about}" + (" with characteristic value" if _cv else "") + _tail
                TABLE.append(_f(_plain, f"special.{_kind}_{_what}{_cv}", _inputs,
                                f"the {_name} spheroidal {_about}" + (", given its characteristic value" if _cv else "")
                                + (" (slope)" if _part else ""), WAVES, part=_part, sample=_sample,
                                whole=("order", "degree"), numbers=_try, formula=not _cv))

TABLE += [
    # ---------------------------------------------------------------- zeta, Lambert W and other functions
    _f("zeta", "special.zeta", "x shift", "the Riemann zeta function, or Hurwitz's with shift= (zeta(x, q))", OTHER,
       defaults={"shift": None}, sympy="zeta(x, shift)", numbers=(-1.5, 0.0, 0.5, 2.0), compute=_zeta),
    _f("zeta minus 1", "special.zetac", "x", "zeta(x) - 1, exact for big x", OTHER, names="zetac",
       sympy_expr="zeta(x) - 1"),
    _f("lambert W", "special.lambertw", "x branch", "W(x): the w with w e**w = x (branch 0, or branch=-1); "
       "complex where x is below -1/e", OTHER, names="lambertw LambertW", defaults={"branch": 0}, whole=("branch",),
       sympy="LambertW(x, branch)", complex_answer=True, compute=_lambertw),
    _f("wright omega", "special.wrightomega", "x", "the Wright Omega function: the w with w + log(w) = x", OTHER,
       names="wrightomega"),
    _f("wright bessel", "special.wright_bessel", "a b x", "Wright's generalized Bessel function, for x of 0 or "
       "above", OTHER, sample={"a": 0.5, "b": 1.0}, numbers=(0.0, 0.5, 1.0, 2.0)),
    _f("log of wright bessel", "special.log_wright_bessel", "a b x", "the log of Wright's generalized Bessel "
       "function", OTHER, sample={"a": 0.5, "b": 1.0}, numbers=(0.0, 0.5, 1.0, 2.0)),
    _f("spence", "special.spence", "x", "the dilogarithm Li2(1 - x) (SymPy polylog(2, 1 - x)), for x of 0 or above",
       OTHER, names="dilogarithm", sympy_expr="polylog(2, 1 - x)", numbers=(-1.5, 0.0, 0.5, 2.0),
       compute=_spence, domain="of 0 or above"),
    _f("arithmetic geometric mean", "special.agm", "x other", "the arithmetic-geometric mean of two numbers", OTHER,
       names="agm", sample={"other": 2.0}),
    _f("dirichlet kernel", "special.diric", "x n", "the periodic sinc function sin(n x / 2) / (n sin(x / 2))",
       OTHER, names="diric", sample={"n": 3}, whole=("n",), compute=_diric),
    # ---------------------------------------------------------------- statistics and machine learning
    _f("box cox", "special.boxcox", "x power", "(x**power - 1) / power, or log(x) for power 0", STATS,
       names="boxcox", sample={"power": 0.5}),
    _f("box cox of 1 plus", "special.boxcox1p", "x power", "the box cox of 1 + x", STATS, names="boxcox1p",
       sample={"power": 0.5}),
    _f("inverse box cox", "special.inv_boxcox", "x power", "the x whose box cox is the number", STATS,
       names="inv_boxcox", sample={"power": 0.5}),
    _f("inverse box cox of 1 plus", "special.inv_boxcox1p", "x power", "the x whose box cox of 1 plus is the number",
       STATS, names="inv_boxcox1p", sample={"power": 0.5}),
    _f("log of expit", "special.log_expit", "x", "log(1 / (1 + e**-x)), without overflow", STATS,
       names="log_expit log_sigmoid"),
    _f("softplus", "special.softplus", "x", "log(1 + e**x), without overflow", STATS,
       compute=lambda x: _sp().softplus(x)),
    _f("softmax", "special.softmax", "x", "e**x divided by the total of e**x over all the numbers (they add up to "
       "1)", STATS, compute=_softmax, formula=False),
    _f("log of softmax", "special.log_softmax", "x", "the log of the softmax of all the numbers", STATS,
       names="log_softmax", compute=_log_softmax, formula=False),
    _f("entropy term", "special.entr", "x", "-x log(x), 0 at 0 (minus infinity below 0)", STATS, names="entr"),
    _f("relative entropy term", "special.rel_entr", "x y", "x log(x / y): one term of the relative entropy", STATS,
       names="rel_entr", sample={"y": 0.5}),
    _f("kullback leibler term", "special.kl_div", "x y", "x log(x / y) - x + y: one term of the "
       "Kullback-Leibler divergence", STATS, names="kl_div", sample={"y": 0.5}),
    _f("huber loss", "special.huber", "delta x", "r**2 / 2 for |r| up to delta, else delta (|r| - delta / 2): the "
       "numbers are r", STATS, names="huber", sample={"delta": 1.0}),
    _f("pseudo huber loss", "special.pseudo_huber", "delta x", "delta**2 (sqrt(1 + (r / delta)**2) - 1)", STATS,
       names="pseudo_huber", sample={"delta": 1.0}),
]

# the spherical Bessel slopes, and the parts (made above without their compute)
_SPHERICAL = {"spherical bessel j": ("spherical_jn", False), "spherical bessel j slope": ("spherical_jn", True),
              "spherical bessel y": ("spherical_yn", False), "spherical bessel y slope": ("spherical_yn", True),
              "modified spherical bessel i": ("spherical_in", False),
              "modified spherical bessel i slope": ("spherical_in", True),
              "modified spherical bessel k": ("spherical_kn", False),
              "modified spherical bessel k slope": ("spherical_kn", True)}


def _spherical(name: str, derivative: bool):
    return lambda n, z: getattr(_sp(), name)(np.asarray(n).astype(int), z, derivative=derivative)


TABLE = [MathsFunction(**{**e.__dict__, "compute": _spherical(*_SPHERICAL[e.plain])}) if e.plain in _SPHERICAL
         else e for e in TABLE]

# Library names that give several answers at once, or a whole run of them: their parts have plain names of their
# own (take_function and formula text name the part; the library name alone says which parts there are)
SEVERAL_PARTS = {
    "airy": ("airy Ai", "airy Ai slope", "airy Bi", "airy Bi slope"),
    "airye": ("airy Ai scaled", "airy Ai slope scaled", "airy Bi scaled", "airy Bi slope scaled"),
    "itairy": ("area under airy Ai", "area under airy Bi", "area under airy Ai of minus t",
               "area under airy Bi of minus t"),
    "fresnel": ("fresnel S", "fresnel C"),
    "modfresnelp": ("modified fresnel plus F", "modified fresnel plus K"),
    "modfresnelm": ("modified fresnel minus F", "modified fresnel minus K"),
    "sici": ("sine integral", "cosine integral"),
    "shichi": ("hyperbolic sine integral", "hyperbolic cosine integral"),
    "ellipj": ("jacobi sn", "jacobi cn", "jacobi dn", "jacobi amplitude"),
    "pbdv": ("parabolic cylinder D", "parabolic cylinder D slope"),
    "pbvv": ("parabolic cylinder V", "parabolic cylinder V slope"),
    "pbwa": ("parabolic cylinder W", "parabolic cylinder W slope"),
    "itj0y0": ("area under bessel J0", "area under bessel Y0"),
    "it2j0y0": ("area under 1 minus bessel J0 over t", "area under bessel Y0 over t"),
    "iti0k0": ("area under bessel I0", "area under bessel K0"),
    "it2i0k0": ("area under bessel I0 minus 1 over t", "area under bessel K0 over t"),
    "kelvin": ("kelvin ber", "kelvin bei", "kelvin ker", "kelvin kei", "kelvin ber slope", "kelvin bei slope",
               "kelvin ker slope", "kelvin kei slope"),
    "frexp": ("mantissa", "exponent of two"),
    "divmod": ("division rounded down", "remainder"),
    "riccati_jn": ("riccati bessel first kind", "riccati bessel first kind slope"),
    "riccati_yn": ("riccati bessel second kind", "riccati bessel second kind slope"),
    "lmbda": ("jahnke emde lambda", "jahnke emde lambda slope"),
    "lqn": ("legendre Q", "legendre Q slope"),
    "spherical_jn": ("spherical bessel j", "spherical bessel j slope"),
    "spherical_yn": ("spherical bessel y", "spherical bessel y slope"),
    "spherical_in": ("modified spherical bessel i", "modified spherical bessel i slope"),
    "spherical_kn": ("modified spherical bessel k", "modified spherical bessel k slope"),
    "mathieu_cem": ("mathieu ce", "mathieu ce slope"),
    "mathieu_sem": ("mathieu se", "mathieu se slope"),
    "mathieu_modcem1": ("modified mathieu ce first kind", "modified mathieu ce first kind slope"),
    "mathieu_modcem2": ("modified mathieu ce second kind", "modified mathieu ce second kind slope"),
    "mathieu_modsem1": ("modified mathieu se first kind", "modified mathieu se first kind slope"),
    "mathieu_modsem2": ("modified mathieu se second kind", "modified mathieu se second kind slope"),
}
for _kind, _name in (("pro", "prolate"), ("obl", "oblate")):
    for _what, _about in (("ang1", "angular function of the first kind"),
                          ("rad1", "radial function of the first kind"),
                          ("rad2", "radial function of the second kind")):
        for _cv in ("", "_cv"):
            _plain = f"{_name} {_about}" + (" with characteristic value" if _cv else "")
            SEVERAL_PARTS[f"{_kind}_{_what}{_cv}"] = (_plain, _plain + " slope")

# Library names of a function that gives a whole run of answers (all degrees up to n, every order, every
# coefficient): take_function gives the one asked for. name -> (plain name, what the library name gives)
RUNS = {
    "legendre_p": ("legendre polynomial", "special.legendre_p(n, z) is SciPy's newer Legendre polynomial (with "
                                          "slopes on request): the same values as eval_legendre"),
    "legendre_p_all": ("legendre polynomial", "special.legendre_p_all(n, z) gives every degree up to n at once"),
    "assoc_legendre_p_all": ("associated legendre polynomial", "special.assoc_legendre_p_all(n, m, z) gives every "
                                                               "degree and order up to n and m at once"),
    "sph_legendre_p_all": ("spherical legendre polynomial", "special.sph_legendre_p_all(n, m, theta) gives every "
                                                            "degree and order up to n and m at once"),
    "sph_harm_y_all": ("spherical harmonic", "special.sph_harm_y_all(n, m, theta, phi) gives every degree and order "
                                             "up to n and m at once"),
    "lqmn": ("associated legendre Q", "special.lqmn(m, n, z) gives every order and degree up to m and n at once"),
    "pbdn_seq": ("parabolic cylinder D", "special.pbdn_seq(n, z) gives D_0 to D_n and their slopes at once"),
    "pbdv_seq": ("parabolic cylinder D", "special.pbdv_seq(v, x) gives D_v0 to D_v and their slopes at once"),
    "pbvv_seq": ("parabolic cylinder V", "special.pbvv_seq(v, x) gives V_v0 to V_v and their slopes at once"),
    "pro_cv_seq": ("prolate characteristic value", "special.pro_cv_seq(m, n, c) gives the characteristic values for "
                                                   "the degrees m to n at once"),
    "obl_cv_seq": ("oblate characteristic value", "special.obl_cv_seq(m, n, c) gives the characteristic values for "
                                                  "the degrees m to n at once"),
    "logsumexp": ("log of sum of exps", "special.logsumexp(numbers) gives log(e**x1 + e**x2 + ...) of all the "
                                        "numbers: numbers.take_function(\"log of sum of exps\", other=...) gives it "
                                        "for two at a time (np.logaddexp); for all of them, "
                                        "numbers.take_function(\"log of softmax\") minus each number"),
}

# ----------------------------------------------------------------------------------------------- lookups
BY_PLAIN = {entry.plain: entry for entry in TABLE}
if len(BY_PLAIN) != len(TABLE):  # pragma: no cover - a mistake in the table above
    raise ValueError("two maths functions have the same plain name")


def _lookup_table() -> dict:
    """Every name (plain name, formula name, library name, other names) -> its plain name."""
    found: dict = {}
    for entry in TABLE:
        spellings = [entry.plain, entry.formula_name, *entry.names]
        if entry.library_is_name and entry.library_name not in SEVERAL_PARTS and entry.library_name not in RUNS:
            spellings.append(entry.library_name)
        for spelling in spellings:
            key = normal(spelling)
            if key in found and found[key] != entry.plain:
                raise ValueError(f"{spelling!r} names two maths functions: {found[key]} and {entry.plain}")
            found[key] = entry.plain
    return found


NAMES = _lookup_table()


def find(name):
    """The MathsFunction of a name (any spelling), or None. Library names of several parts give None."""
    if not isinstance(name, str):
        return None
    text = name.strip()
    for head in ("scipy.special.", "special.", "numpy.", "np.", "sympy.", "sp."):
        if text.lower().startswith(head):
            text = text[len(head):]
    plain = NAMES.get(normal(text))
    return BY_PLAIN[plain] if plain else None


def several_parts(name):
    """The plain names of the parts, for a library name that gives several answers (airy), else None."""
    if not isinstance(name, str):
        return None
    text = name.strip().split(".")[-1]
    return SEVERAL_PARTS.get(text) or SEVERAL_PARTS.get(text.lower())


def run_of(name):
    """(plain name, what the library name gives) for a library name that gives a whole run of answers, else None."""
    if not isinstance(name, str):
        return None
    return RUNS.get(name.strip().split(".")[-1])


def all_names() -> list[str]:
    """Every plain name, in the order of the groups."""
    return [e.plain for group in GROUP_ORDER for e in TABLE if e.group == group]


# ------------------------------------------------------------------------------------------- formula text
# Names that formula text already uses for something else, or points from (table/columns.py, _formula.py): they keep
# their meaning
_TAKEN = {"round", "abs", "sqrt", "log", "exp", "sin", "cos", "tan", "erf", "erfc", "gamma", "lgamma", "digamma",
          "beta", "besselJ", "besselj", "sinc", "log10", "log1p", "sign", "cbrt", "floor", "ceil", "arcsin", "arccos",
          "arctan", "arctan2", "atan", "asin", "acos", "atan2", "pi", "jv", "gammaln", "loggamma", "psi", "mean",
          "avg", "sum", "min", "max", "n", "len", "power", "pow", "average", "median", "total", "count", "smallest",
          "biggest", "length", "count_text", "add_working_days", "count_working_days", "nchar", "str_length",
          "len_chars", "str_len", "str_count", "count_matches", "busday_offset", "add_business_days",
          "busday_count", "business_day_count", "Integer", "Float", "Rational", "Symbol", "Function", "Lambda", "Add",
          "Mul", "Pow", "E", "I", "S", "N", "D", "x", "y", "e"}


@dataclass(frozen=True)
class FormulaName:
    """One name of formula text: its function, how many values it takes, and the order they come in."""

    name: str
    entry: MathsFunction
    order: tuple  # the entry's inputs in the order this name takes them
    sympy_name: str = ""  # SymPy's own function, when this name is SymPy's

    @property
    def fewest(self) -> int:
        return len([n for n in self.order if n not in self.entry.defaults])

    @property
    def most(self) -> int:
        return len(self.order)


def _sympy_parts(text: str) -> tuple[str, tuple]:
    head, _, rest = text.partition("(")
    return head.strip(), tuple(part.strip() for part in rest.rstrip(")").split(","))


def _formula_names() -> dict:
    found: dict = {}

    def add(name, entry, order, sympy_name=""):
        if name in _TAKEN or not name.isidentifier():
            return
        if name in found and found[name].entry.plain != entry.plain:
            raise ValueError(f"formula name {name} for {found[name].entry.plain} and {entry.plain}")
        found.setdefault(name, FormulaName(name, entry, order, sympy_name))

    for entry in TABLE:
        if not entry.formula:
            continue
        add(entry.formula_name, entry, entry.inputs)
        if entry.library_is_name and entry.library_name not in SEVERAL_PARTS:
            add(entry.library_name, entry, entry.inputs)
        if entry.sympy:
            head, order = _sympy_parts(entry.sympy)
            add(head, entry, order, head)
        for other in entry.names:
            add(other, entry, entry.inputs)
    return found


FORMULA_NAMES = _formula_names()
# fewest and most values of each formula name (the form of table/columns.py FUNCTIONS)
FORMULA_SIZES = {name: (spec.fewest, spec.most) for name, spec in FORMULA_NAMES.items()}


def prepare(entry: MathsFunction, values: list) -> tuple[list, np.ndarray | bool]:
    """The inputs of an entry (in its order) made ready for the library: decimals, and whole numbers (int64) for
    the inputs that must be whole. Returns the inputs and where an input that must be whole is not (a decimal, or
    empty): the answer is empty there (False when every input is fine). None stays None (an option left out)."""
    ready, bad = [], False
    for key, value in zip(entry.inputs, values):
        if value is None:
            ready.append(None)
            continue
        value = np.asarray(value, dtype=float)
        if key in entry.whole:
            fine = np.isfinite(value) & (value == np.round(value))
            bad = bad | ~fine
            value = np.where(fine, value, 0).astype(np.int64)
        ready.append(value)
    return ready, bad


def work_out(entry: MathsFunction, values: list):
    """The entry worked out on its inputs (in its order), with empty answers where a whole input is not whole."""
    ready, bad = prepare(entry, values)
    out = np.asarray(entry.evaluate(*ready))
    if np.any(bad):
        bad = np.broadcast_to(bad, out.shape)
        out = np.where(bad, np.nan, out.astype(complex if out.dtype.kind == "c" else float))
    return out


def _value(spec: FormulaName, *values):
    given = dict(zip(spec.order, values))
    inputs = [given.get(key, spec.entry.defaults.get(key)) for key in spec.entry.inputs]
    try:
        out = work_out(spec.entry, inputs)
    except (TypeError, ValueError):
        shape = np.broadcast_shapes(*[np.shape(v) for v in inputs if v is not None])
        return np.full(shape, np.nan)
    if out.dtype.kind == "c":
        real = np.real(out)
        keep = np.abs(np.imag(out)) <= 1e-15 * np.maximum(1.0, np.abs(real))
        return np.where(keep, real, np.nan)
    return out.astype(float)


def formula_value(name: str, *values):
    """A formula name worked out on NumPy arrays (values in the order of that name): real numbers; a complex answer
    with no imaginary part is its real part, any other is empty (NaN), as a formula keeps to real numbers."""
    return _value(FORMULA_NAMES[name], *values)


# -------------------------------------------------------------------------------------------------- SymPy
_IMPLEMENTED: dict = {}


def sympy_functions(evaluate: bool = True) -> dict:
    """Formula name -> a function that makes the SymPy expression from the values in the name's order. SymPy's own
    function where there is one (sympy, sympy_expr); else a SymPy implemented_function worked out by SciPy, named by
    the formula name."""
    import sympy as sp

    made: dict = {}
    for name, spec in FORMULA_NAMES.items():
        made[name] = _sympy_maker(sp, spec, evaluate)
    return made


def _sympy_maker(sp, spec: FormulaName, evaluate: bool):
    entry = spec.entry
    flag = {} if evaluate else {"evaluate": False}
    if spec.sympy_name:  # SymPy's own name, in SymPy's order
        function = getattr(sp, spec.sympy_name)
        defaults = [entry.defaults.get(k) for k in spec.order]

        def own(*values, **_):
            values = list(values) + defaults[len(values):]
            while values and values[-1] is None:  # zeta(x) and LambertW(x): the optional value left out
                values.pop()
            return function(*values, **flag)
        return own
    if entry.sympy or entry.sympy_expr:
        text = entry.sympy or entry.sympy_expr
        names = entry.inputs

        def built(*values, **_):
            given = dict(zip(spec.order, values))
            local = {key: given.get(key, entry.defaults.get(key)) for key in names}
            if entry.sympy and any(v is None for v in local.values()):
                head, order = _sympy_parts(entry.sympy)
                args = [local[k] for k in order if local[k] is not None]
                return getattr(sp, head)(*args, **flag)
            local = {k: (sp.nan if v is None else sp.sympify(v)) for k, v in local.items()}
            from sympy.parsing.sympy_parser import parse_expr

            context = {n: getattr(sp, n) for n in re.findall(r"[A-Za-z_][A-Za-z_0-9]*", text)
                       if n not in names and hasattr(sp, n)}
            return parse_expr(text, local_dict={**context, **local}, global_dict={"__builtins__": {}, **_SAFE(sp)},
                              evaluate=evaluate)
        return built
    function = _implemented(sp, spec.entry)

    def numeric(*values, **_):
        given = dict(zip(spec.order, values))
        args = [given.get(k, entry.defaults.get(k)) for k in entry.inputs]
        args = [sp.nan if a is None else a for a in args]
        return function(*args, **flag)
    return numeric


def _SAFE(sp) -> dict:  # noqa: N802 - the global names SymPy's reader needs
    return {"Integer": sp.Integer, "Float": sp.Float, "Rational": sp.Rational, "Symbol": sp.Symbol,
            "Add": sp.Add, "Mul": sp.Mul, "Pow": sp.Pow, "Tuple": sp.Tuple}


def _implemented(sp, entry: MathsFunction):
    """The SymPy function of an entry SymPy does not have: a SymPy Function named by the formula name whose decimal
    value (evalf) and numbers (lambdify, through sympy_numbers) are worked out by SciPy or NumPy. Its class lives in
    this module (made on first use), so a formula with it can go to the helper process of the time limit."""
    return _table_class(entry.formula_name)


_CLASS_PREFIX = "_sympy_function_"


def _table_base():
    """The SymPy Function class the table's own functions are made from (once)."""
    if "base" in _IMPLEMENTED:
        return _IMPLEMENTED["base"]
    import sympy as sp

    class TableFunction(sp.Function):
        """A maths function of the table that SymPy does not have: worked out by SciPy or NumPy."""

        @classmethod
        def eval(cls, *args):
            return None

        def _eval_evalf(self, prec):
            values = [arg.evalf(prec) for arg in self.args]
            if not all(value.is_number and value.is_real for value in values):
                return None
            spec = _SPECS_BY_CLASS[self.func.__name__]
            found = float(np.asarray(_value(spec, *[float(value) for value in values])).reshape(-1)[0])
            return sp.Float(found, prec) if np.isfinite(found) else (sp.nan if np.isnan(found) else
                                                                       sp.oo if found > 0 else -sp.oo)

    TableFunction.__module__ = __name__
    TableFunction.__qualname__ = _CLASS_PREFIX + "base"
    _IMPLEMENTED["base"] = TableFunction
    return TableFunction


# the formula name of each entry SymPy does not have -> how it is worked out by number
_SPECS_BY_CLASS = {entry.formula_name: FormulaName(entry.formula_name, entry, entry.inputs) for entry in TABLE
                   if entry.formula and not (entry.sympy or entry.sympy_expr)}


def _table_class(name: str):
    if name in _IMPLEMENTED:
        return _IMPLEMENTED[name]
    made = type(name, (_table_base(),), {"__module__": __name__})
    made.__qualname__ = _CLASS_PREFIX + name
    _IMPLEMENTED[name] = made
    return made


def __getattr__(attribute: str):
    """The table's SymPy classes by the names pickle looks for (_sympy_function_<name>), made on first use."""
    if attribute.startswith(_CLASS_PREFIX):
        name = attribute[len(_CLASS_PREFIX):]
        if name == "base":
            return _table_base()
        if name in _SPECS_BY_CLASS:
            return _table_class(name)
    raise AttributeError(f"module {__name__!r} has no attribute {attribute!r}")


def sympy_numbers() -> dict:
    """SymPy function name -> the NumPy function lambdify uses for it (in SymPy's order): the table's own functions
    instead of SciPy names SymPy may not know (elliptic_k) or may give in another way."""
    out: dict = {}
    for entry in TABLE:
        if entry.sympy:
            head, order = _sympy_parts(entry.sympy)
            out.setdefault(head, _numbers_in_order(FormulaName(head, entry, order)))
    for name, spec in _SPECS_BY_CLASS.items():  # the table's own functions, by their formula name
        out[name] = _numbers_in_order(spec)
    out["elliptic_e"] = _elliptic_e_numbers  # elliptic_e(m) is complete, elliptic_e(phi, m) is not
    out["hyper"] = _hyper_numbers
    out["polylog"] = _polylog_numbers
    out["betainc_regularized"] = _betainc_numbers
    out["jn"] = lambda n, x: _sp().spherical_jn(np.asarray(n).astype(int), x)
    out["yn"] = lambda n, x: _sp().spherical_yn(np.asarray(n).astype(int), x)
    return out


def _numbers_in_order(spec: FormulaName):
    def numbers(*values):
        return _value(spec, *values)
    return numbers


def _elliptic_e_numbers(*values):
    special = _sp()
    return special.ellipe(values[0]) if len(values) == 1 else special.ellipeinc(values[0], values[1])


def _polylog_numbers(order, x):
    if np.any(np.asarray(order) != 2):
        raise ValueError("polylog is worked out by number for order 2 only (SciPy spence)")
    return _sp().spence(1 - np.asarray(x, dtype=float))


def _betainc_numbers(a, b, low, high):
    special = _sp()
    return special.betainc(a, b, high) - special.betainc(a, b, low)


def _hyper_numbers(top, bottom, x):
    special = _sp()
    top, bottom = tuple(top), tuple(bottom)
    with np.errstate(all="ignore"):
        if len(top) == 0 and len(bottom) == 1:
            return special.hyp0f1(bottom[0], x)
        if len(top) == 1 and len(bottom) == 1:
            return special.hyp1f1(top[0], bottom[0], x)
        if len(top) == 2 and len(bottom) == 1:
            return special.hyp2f1(top[0], top[1], bottom[0], x)
    raise ValueError("only 0F1, 1F1 and 2F1 are worked out by number")


# SymPy's elementary functions: they never make big exact numbers, so they are not special functions
_ELEMENTARY = {"sqrt", "exp", "log", "sin", "cos", "tan", "cot", "sinh", "cosh", "tanh", "asinh", "acosh", "atanh",
               "asin", "acos", "atan", "atan2", "conjugate", "pi"}


def sympy_classes() -> tuple:
    """The SymPy function classes of the table: their numbers are worked out under the time limit, and may be at most
    as big as the other special functions allow."""
    import sympy as sp

    heads = {_sympy_parts(entry.sympy)[0] for entry in TABLE if entry.sympy}
    heads |= set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", " ".join(entry.sympy_expr for entry in TABLE)))
    found = []
    for name in sorted(heads):
        function = getattr(sp, name, None)
        if isinstance(function, type) and issubclass(function, sp.Function) and name not in _ELEMENTARY:
            found.append(function)
    return tuple(found)


def hyper_name(top: int, bottom: int) -> str | None:
    """The formula name of SymPy's hyper with this many values on top and below (hyper((a,), (b,), x) is
    hyp1f1(a, b, x)); None for the others, which formula text does not know."""
    return {(0, 1): "hyp0f1", (1, 1): "hyp1f1", (2, 1): "hyp2f1"}.get((top, bottom))


def formula_help_line() -> str:
    return ("  bessel_j(1, x)  erfinv(x)  every maths function of numbers.take_function, by its formula name (the "
            "plain name with _), its SciPy name or SymPy's name; sdata.help(\"take_function\") lists them")


# ------------------------------------------------------------------------------------- help pointers (G21)
def _call_text(entry: MathsFunction) -> str:
    options = "".join(f", {k}={entry.sample[k]!r}" for k in entry.needed if entry.sample.get(k) is not None)
    options += "".join(f", {k}=..." for k in entry.needed if entry.sample.get(k) is None)
    return f'numbers.take_function("{entry.plain}"{options})'


def pointer_groups(taken: dict) -> dict:
    """The help pointers of the maths family, made from the one table: namespace kind ("special", "numpy", "sympy",
    "scipy") -> [(how the simplydata word is written, the other names)]. taken: kind -> the names the hand-written
    lists of _other_names.py already point (those keep their pointer)."""
    from ._special_points import AREA_RULES, ZEROS, ZEROS_TOGETHER

    groups: dict = {"special": [], "numpy": [], "sympy": [], "scipy": []}
    used: dict = {kind: set(taken.get(kind, ())) for kind in groups}

    def add(kind, written, names):
        fresh = [n for n in dict.fromkeys(names) if n.isidentifier() and n not in used[kind]]
        used[kind].update(fresh)
        if fresh:
            groups[kind].append((written, " ".join(fresh)))

    for entry in TABLE:
        kind = "special" if entry.namespace == "special" else "numpy"
        names = [n for n in entry.names if n.isidentifier()]
        if entry.library_is_name and entry.library_name not in SEVERAL_PARTS and entry.library_name not in RUNS:
            names.insert(0, entry.library_name)
        add(kind, _call_text(entry), names)
        for other in entry.also:
            add("special" if other.startswith("special.") else "numpy", _call_text(entry), [other.split(".", 1)[1]])
        if entry.sympy and entry.formula:
            head, order = _sympy_parts(entry.sympy)
            add("sympy", f'sdata.formula("{entry.sympy}"): SymPy\'s {head} inside formula text '
                         f"(in SymPy's order), or {_call_text(entry)} for numbers", [head])
        elif entry.sympy:  # formula text keeps to real numbers: the word for numbers only
            add("sympy", _call_text(entry), [_sympy_parts(entry.sympy)[0]])
    for name, parts in SEVERAL_PARTS.items():
        kind = "numpy" if name in ("frexp", "divmod") else "special"
        others = ", ".join(f'"{p}"' for p in parts[1:])
        add(kind, f"{_call_text(BY_PLAIN[parts[0]])}: one answer of {name} by its own name (also {others})", [name])
    for name, (plain, about) in RUNS.items():
        add("special", f"{_call_text(BY_PLAIN[plain])}: {about}; take_function gives the one asked for", [name])
    for plain, (function_name, uses_order, _, _) in ZEROS.items():
        order = ", order=0" if uses_order else ""
        add("special", f'sdata.find_zeros_of("{plain}"{order}, how_many=5)', [function_name])
    for name, parts in ZEROS_TOGETHER.items():
        others = ", ".join(f'"{p}"' for p in parts[1:])
        add("special", f'sdata.find_zeros_of("{parts[0]}", how_many=5): one of the functions {name} gives at once '
                       f"(also {others})", [name])
    for plain, (function_name, short, needs, _, _) in AREA_RULES.items():
        sample = {"alpha": 0.5, "beta": 1.5, "p": 2.0, "q": 1.0, "degree": 7}
        options = "".join(f", {k}={sample[k]}" for k in needs)
        count = "" if plain == "lebedev" else ", how_many=5"
        kind = "scipy" if function_name in ("newton_cotes", "lebedev_rule") else "special"
        add(kind, f'sdata.find_area_points("{plain}"{count}{options})', [function_name, short])
    from .numbers.function_words import BITS
    from .numbers.more_number_words import NUMBER_KINDS

    for how, (function_name, _, needs) in BITS.items():
        option = ", with_numbers=6" if needs == "with_numbers" else ", by=2" if needs == "by" else ""
        names = [function_name] + [n for n, plain in _BITS_NAMES.items() if plain == how]
        on = {"packbits": ", on yes or no values: numbers.turn_into_yes_or_no(is_above=...) first",
              "unpackbits": ", on whole numbers from 0 to 255 (bytes), as numbers.round_to(...) gives"}
        add("numpy", f'numbers.work_on_bits("{how}"{option}){on.get(function_name, "")}', names)
    for kind_name, (function_name, _) in NUMBER_KINDS.items():
        add("numpy", f'numbers.turn_into_yes_or_no(is_="{kind_name}")', [function_name])
    return groups


# NumPy's other bit names -> work_on_bits(how=)
_BITS_NAMES = {"bitwise_not": "flip", "bitwise_invert": "flip", "bitwise_left_shift": "shift left",
               "bitwise_right_shift": "shift right"}
