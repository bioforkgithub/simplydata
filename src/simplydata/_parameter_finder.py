"""sdata.find_parameter_that_gives: the parameter of a distribution that gives a chance at a value (families for 100 %,
batches 5-6; approved by Manish 2026-11-28, plan section 2.2).

    sdata.find_parameter_that_gives("t", chance_below=0.975, at_value=2.1)   # the degrees of freedom

Give the distribution's name, the chance (chance_below=, chance_at_most=, chance_above= or chance_at_least=), the value
it is at (at_value=), and every parameter but one: the missing one is found. The work is done by scipy.special's
inverse functions (stdtridf, chdtriv, fdtridfd, gdtria, gdtrib, btdtria, btdtrib, bdtri, bdtrin, nbdtri, nbdtrin,
pdtri, nrdtrimn, nrdtrisd, chndtridf, chndtrinc, ncfdtridfd, ncfdtridfn, ncfdtrinc, nctdtridf, nctdtrinc). For
counts, chance_below= is the chance of fewer than at_value, as find_chance_that_value(is_below=), and chance_at_most=
includes it.
"""

from __future__ import annotations

import math
import numbers as _nb

from ._errors import SimplydataError, friendly

# family (plain name) -> {missing parameter: (scipy.special function, how its arguments are made)}; the arguments
# are named: p (the chance at or below), x (the value) and the known parameters by their plain names
INVERSES = {
    "t": {"degrees_of_freedom": ("stdtridf", ("p", "x"))},
    "chi-square": {"degrees_of_freedom": ("chdtriv", ("p", "x"))},
    "F": {"degrees_of_freedom_2": ("fdtridfd", ("degrees_of_freedom_1", "p", "x"))},
    "gamma": {"rate": ("gdtria", ("p", "shape", "x")), "shape": ("gdtrib", ("rate", "p", "x"))},
    "beta": {"shape1": ("btdtria", ("p", "shape2", "x")), "shape2": ("btdtrib", ("shape1", "p", "x"))},
    "binomial": {"chance": ("bdtri", ("x", "tries", "p")), "tries": ("bdtrin", ("x", "p", "chance"))},
    "negative binomial": {"chance": ("nbdtri", ("x", "size", "p")), "size": ("nbdtrin", ("x", "p", "chance"))},
    "poisson": {"average": ("pdtri", ("x", "p"))},
    "normal": {"average": ("nrdtrimn", ("p", "standard_deviation", "x")),
               "standard_deviation": ("nrdtrisd", ("average", "p", "x"))},
    "noncentral chi-square": {"degrees_of_freedom": ("chndtridf", ("x", "p", "noncentrality")),
                              "noncentrality": ("chndtrinc", ("x", "degrees_of_freedom", "p"))},
    "noncentral F": {"degrees_of_freedom_2": ("ncfdtridfd", ("degrees_of_freedom_1", "p", "noncentrality", "x")),
                     "degrees_of_freedom_1": ("ncfdtridfn", ("p", "degrees_of_freedom_2", "noncentrality", "x")),
                     "noncentrality": ("ncfdtrinc", ("degrees_of_freedom_1", "degrees_of_freedom_2", "p", "x"))},
    "noncentral t": {"degrees_of_freedom": ("nctdtridf", ("p", "noncentrality", "x")),
                     "noncentrality": ("nctdtrinc", ("degrees_of_freedom", "p", "x"))},
}
COUNTS = ("binomial", "negative binomial", "poisson")
CHANCES = ("chance_below", "chance_at_most", "chance_above", "chance_at_least")
EXAMPLE = 'sdata.find_parameter_that_gives("t", chance_below=0.975, at_value=2.1)'


def _family_name(name):
    from .distributions import Family, _find_family

    found = _find_family(name, "find_parameter_that_gives")
    plain = found.name if isinstance(found, Family) else getattr(found, "plain", None)
    if plain not in INVERSES:
        raise SimplydataError(f'find_parameter_that_gives() knows the distributions {", ".join(map(repr, INVERSES))} '
                              f'(scipy.special has their inverse functions); not "{name}".\nFor example:  {EXAMPLE}')
    return plain


@friendly(others={"x": "at_value", "value": "at_value", "p": "chance_below"})
def find_parameter_that_gives(distribution=None, chance_below=None, chance_at_most=None, chance_above=None,
                              chance_at_least=None, at_value=None, **known):
    """The parameter that gives a chance. df = sdata.find_parameter_that_gives("t", chance_below=0.975, at_value=2.1)

    degrees = sdata.find_parameter_that_gives("t", chance_below=0.975, at_value=2.1)
    Give the distribution, one chance (chance_below=, chance_at_most=, chance_above= or chance_at_least=), the value
    it is at (at_value=) and every other parameter by its plain name: the one parameter left out is found, such as
    the degrees of freedom of a t distribution, the chance of a binomial (tries= given) or the standard deviation of a
    normal (average= given). For counts, chance_below= is the chance of fewer than at_value (as
    find_chance_that_value(is_below=)), chance_at_most= includes it. Names: t, chi-square, F, gamma, beta, binomial,
    negative binomial, poisson, normal, noncentral chi-square, noncentral F, noncentral t. scipy.special's inverse
    functions do the work (stdtridf, bdtri, nrdtrisd ...). Gives back the number; check it with
    sdata.distribution(...).find_chance_that_value(...).
    """
    from scipy import special

    from .distributions import _answer, _say

    if distribution is None:
        raise SimplydataError(f"find_parameter_that_gives() needs the name of a distribution.\nFor example:  {EXAMPLE}")
    family = _family_name(distribution)
    given = {k: v for k, v in zip(CHANCES, (chance_below, chance_at_most, chance_above, chance_at_least))
             if v is not None}
    if len(given) != 1:
        raise SimplydataError(f"Give one chance: chance_below=, chance_at_most=, chance_above= or chance_at_least=.\n"
                              f"For example:  {EXAMPLE}")
    (side, chance), = given.items()
    if isinstance(chance, bool) or not isinstance(chance, _nb.Real) or not 0 < chance < 1:
        raise SimplydataError(f"{side}= is a chance above 0 and below 1, such as 0.975.")
    if isinstance(at_value, bool) or not isinstance(at_value, _nb.Real) or not math.isfinite(at_value):
        raise SimplydataError(f"at_value= is the value the chance is at, a number.\nFor example:  {EXAMPLE}")
    counts = family in COUNTS
    if counts and side in ("chance_at_most", "chance_above") and not float(at_value).is_integer():
        raise SimplydataError("at_value= is a count here: a whole number.")
    if not counts and side in ("chance_at_most", "chance_at_least"):
        side = {"chance_at_most": "chance_below", "chance_at_least": "chance_above"}[side]  # the same when smooth
    choices = INVERSES[family]
    params = _spelled(family, known)
    missing = [m for m in choices if m not in params]
    every = sorted({a for _, args in choices.values() for a in args if a not in ("p", "x")} | set(choices))
    unknown = [k for k in params if k not in every]
    if unknown:
        raise SimplydataError(f"The {family} distribution here has no parameter called {unknown[0]}=; its parameters: "
                              f"{', '.join(n + '=' for n in every)}.")
    if len(missing) != 1:
        left = " or ".join(m + "=" for m in choices)
        raise SimplydataError(f"Leave out exactly one parameter, the one to find ({left}), and give the others.\n"
                              f"For example:  {EXAMPLE}")
    target = missing[0]
    function_name, arguments = choices[target]
    # the chance at or below a value: what the scipy.special functions take
    x = float(at_value)
    p = float(chance)
    if counts:
        if side == "chance_below":  # fewer than at_value: at most at_value - 1
            x = math.ceil(x) - 1
        elif side == "chance_above":  # more than at_value: 1 - at most at_value
            p = 1 - p
        elif side == "chance_at_least":  # at least at_value: 1 - at most at_value - 1
            x, p = math.ceil(x) - 1, 1 - p
    elif side == "chance_above":
        p = 1 - p
    values = {"p": p, "x": x, **params}
    need = [a for a in arguments if a not in values]
    if need:
        raise SimplydataError(f"To find {target}= the {family} distribution needs {', '.join(n + '=' for n in need)}.")
    found = float(getattr(special, function_name)(*[values[a] for a in arguments]))
    # scipy.special answers "no such value" with codes such as 1e100 or 1e-100: put the answer back into the forward
    # function and keep it only when it gives the chance, inside the parameter's range
    back = None
    if math.isfinite(found) and abs(found) < 1e99 and _in_domain(family, target, found):
        back = _forward(family, {**params, target: found}, x)
    if back is None or not math.isfinite(back) or abs(back - p) > 1e-5:  # cdflib's searches give about 6 digits
        raise SimplydataError(f"No {target.replace('_', ' ')} gives that chance at {_say(at_value)} with these "
                              "values (scipy.special finds none).")
    whole_note = ""
    if family == "binomial" and target == "tries" and not float(found).is_integer():
        low, high = math.floor(found), math.ceil(found)
        chance_low, chance_high = (_forward(family, {**params, "tries": n}, x) for n in (low, high))
        whole_note = (f" A binomial needs a whole number of tries: {low} tries give a chance of {_say(chance_low)} at "
                      f"or below {_say(x)}, {high} tries {_say(chance_high)} (scipy.special bdtrin gives the number "
                      "between them).")
    words = {"chance_below": "below", "chance_at_most": "at or below", "chance_above": "above",
             "chance_at_least": "at or above"}[next(iter(given))]
    if counts:
        words = {"chance_below": "fewer than", "chance_at_most": "at most", "chance_above": "more than",
                 "chance_at_least": "at least"}[next(iter(given))]
    known_text = ", ".join(f"{k.replace('_', ' ')} {_say(v)}" for k, v in params.items())
    print(f"The {target.replace('_', ' ')} (the parameter) that gives a chance of {_say(chance)} of a value {words} "
          f"{_say(at_value)} "
          f"in a {family} distribution{' with ' + known_text if known_text else ''} is {_answer(found)} (scipy.special "
          f"{function_name}; put back into the distribution, it gives the chance again).{whole_note}")
    return found


POSITIVE = ("degrees_of_freedom", "degrees_of_freedom_1", "degrees_of_freedom_2", "rate", "shape", "shape1", "shape2",
            "tries", "size", "standard_deviation")


def _in_domain(family, target, value) -> bool:
    """The parameter's own range: above 0 for the spreads, shapes, sizes and degrees of freedom, a chance from 0 to 1,
    0 or more for a noncentrality and a Poisson average."""
    if target in POSITIVE:
        return value > 0
    if target == "chance":
        return 0 < value <= 1
    if target == "noncentrality" or (target == "average" and family == "poisson"):
        return value >= 0
    return True


def _forward(family, params, x):
    """The chance at or below x with these parameters: scipy.special's forward functions."""
    from scipy import special

    q = params.get
    forward = {
        "t": lambda: special.stdtr(q("degrees_of_freedom"), x),
        "chi-square": lambda: special.chdtr(q("degrees_of_freedom"), x),
        "F": lambda: special.fdtr(q("degrees_of_freedom_1"), q("degrees_of_freedom_2"), x),
        "gamma": lambda: special.gdtr(q("rate"), q("shape"), x),
        "beta": lambda: special.betainc(q("shape1"), q("shape2"), x),
        # the incomplete beta forms, which also take a number of tries between whole numbers (bdtr would cut it)
        "binomial": lambda: special.betainc(q("tries") - x, x + 1, 1 - q("chance")) if q("tries") > x else 1.0,
        "negative binomial": lambda: special.betainc(q("size"), x + 1, q("chance")),
        "poisson": lambda: special.pdtr(x, q("average")),
        "normal": lambda: special.ndtr((x - q("average")) / q("standard_deviation")),
        "noncentral chi-square": lambda: special.chndtr(x, q("degrees_of_freedom"), q("noncentrality")),
        "noncentral F": lambda: special.ncfdtr(q("degrees_of_freedom_1"), q("degrees_of_freedom_2"),
                                               q("noncentrality"), x),
        "noncentral t": lambda: special.nctdtr(q("degrees_of_freedom"), q("noncentrality"), x),
    }[family]
    return float(forward())


def _spelled(family, known):
    """The known parameters by their plain names (R's names and SciPy's work too)."""
    from ._distribution_names import LOOKUP, Named
    from .distributions import FAMILY, Family, _key

    out = {}
    fam = FAMILY.get(family)
    spelled = {}
    if isinstance(fam, Family):
        for p in fam.params:
            spelled[p.name] = p.name
            spelled.update({a: p.name for a in p.aliases})
        spelled.update({"degrees_of_freedom": "degrees_of_freedom_1"} if family == "F" else {})
    else:
        named = Named(LOOKUP[_key(family)])
        spelled = {plain: plain for plain in named.names.values()}
        spelled.update({scipy: plain for scipy, plain in named.names.items()})
    for key, value in known.items():
        name = spelled.get(key, key)
        if isinstance(value, bool) or not isinstance(value, _nb.Real) or not math.isfinite(value):
            raise SimplydataError(f"{key}= needs a number.")
        out[name] = float(value)
    return out
