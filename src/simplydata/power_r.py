"""The R calls behind the power words' S3b-2 routes (planning a study). Nothing is calculated here: each function
hands the checked inputs to an R package and gives back that package's own numbers. The packages are checked with
need_r() but never attached (every call names its package, gsDesign::nEvents), so none can hide a base function.

* presize::prec_prop(method = "wilson"): the values needed for a percent's interval of a chosen width.
* gsDesign::nEvents(): the events a log-rank test needs (Schoenfeld 1983), and the power of a number of events.
* powerSurvEpi::ssizeEpi.default() / powerEpi.default() with p = 0.5 (two groups of the same size): the people
  (events divided by the share expected to have the event, Schoenfeld's formula as Hsieh & Lavori 2000 write it).
* powerSurvEpi::ssizeCT.default() / powerCT.default(): Freedman's (1982) formula.
* pwrss::power.z.logistic(method = "demidenko(vc)"): logistic regression with one bell-shaped column
  (Demidenko 2007 with the variance correction; it gives G*Power's 337 in the G*Power manual's example).
"""

from __future__ import annotations

import math

SURVIVAL_NOTE = "Python has no power calculation for survival (statsmodels has none)"


def _r(code, packages, what, python_note, **values):
    from ._r import need_r, r_call

    need_r(packages, what, python_note)
    return r_call(code, packages=(), what=what, **values)


def _first(value) -> float:
    import numpy as np

    return float(np.asarray(value, dtype=float).reshape(-1)[0])


def prec_prop(percent, width, significance):
    """The exact number needed for a percent's interval (presize::prec_prop, Wilson interval)."""
    found = _r("presize::prec_prop(p = p, conf.width = w, conf.level = 1 - a, method = \"wilson\")$n",
               ("presize",), "The number needed for the width of a percent's interval (R presize::prec_prop())",
               "Python has no function for it", p=percent, w=width, a=significance)
    return _first(found)


def schoenfeld_events(hazard_ratio, significance, power, sides):
    """Events needed (exact), as gsDesign::nEvents(ratio = 1)."""
    found = _r("gsDesign::nEvents(hr = hr, alpha = a, beta = 1 - pw, ratio = 1, sided = s)",
               ("gsDesign",), "Power for survival (R gsDesign::nEvents())", SURVIVAL_NOTE,
               hr=hazard_ratio, a=significance, pw=power, s=int(sides))
    return _first(found)


def schoenfeld_events_power(hazard_ratio, events, significance, sides):
    found = _r("gsDesign::nEvents(hr = hr, alpha = a, ratio = 1, sided = s, n = d)",
               ("gsDesign",), "Power for survival (R gsDesign::nEvents())", SURVIVAL_NOTE,
               hr=hazard_ratio, a=significance, s=int(sides), d=float(events))
    return _first(found)


def schoenfeld_people(hazard_ratio, first, second, significance, power):
    """People needed in all (powerSurvEpi rounds up) and the share of everyone expected to have the event."""
    found = _r("psi <- mean(c(pE, pC)); list(n = powerSurvEpi::ssizeEpi.default(power = pw, theta = hr, p = 0.5, "
               "psi = psi, rho2 = 0, alpha = a), psi = psi)",
               ("powerSurvEpi",), "People needed for survival (R powerSurvEpi::ssizeEpi.default())", SURVIVAL_NOTE,
               hr=hazard_ratio, pE=first, pC=second, a=significance, pw=power)
    return _first(found["n"]), _first(found["psi"])


def schoenfeld_people_power(hazard_ratio, first, second, people, significance):
    found = _r("psi <- mean(c(pE, pC)); list(power = powerSurvEpi::powerEpi.default(n = n, theta = hr, p = 0.5, "
               "psi = psi, rho2 = 0, alpha = a), psi = psi)",
               ("powerSurvEpi",), "Power for survival (R powerSurvEpi::powerEpi.default())", SURVIVAL_NOTE,
               hr=hazard_ratio, pE=first, pC=second, a=significance, n=float(people))
    return _first(found["power"]), _first(found["psi"])


def freedman_people(hazard_ratio, first, second, significance, power):
    """People needed in each group by Freedman's formula (powerSurvEpi rounds up)."""
    found = _r("powerSurvEpi::ssizeCT.default(power = pw, k = 1, pE = pE, pC = pC, RR = hr, alpha = a)",
               ("powerSurvEpi",), "People needed for survival (R powerSurvEpi::ssizeCT.default())", SURVIVAL_NOTE,
               hr=hazard_ratio, pE=first, pC=second, a=significance, pw=power)
    return _first(found)


def freedman_power(hazard_ratio, first, second, people, significance):
    found = _r("powerSurvEpi::powerCT.default(nE = n, nC = n, pE = pE, pC = pC, RR = hr, alpha = a)",
               ("powerSurvEpi",), "Power for survival (R powerSurvEpi::powerCT.default())", SURVIVAL_NOTE,
               hr=hazard_ratio, pE=first, pC=second, a=significance, n=float(people))
    return _first(found)


def logistic(percent, odds_ratio, significance, sides, power=None, n=None):
    """pwrss::power.z.logistic (Demidenko with variance correction): (exact n, power)."""
    found = _r(
        "r <- pwrss::power.z.logistic(base.prob = p0, odds.ratio = ratio, n = if (is.na(n)) NULL else n, "
        "power = if (is.na(pw)) NULL else pw, alpha = a, alternative = alt, distribution = \"normal\", "
        "method = \"demidenko(vc)\", ceil.n = FALSE, verbose = 0); list(n = r$n, power = r$power)",
        ("pwrss",), "Power for logistic regression (R pwrss::power.z.logistic())",
        "Python has no power calculation for logistic regression",
        p0=percent, ratio=odds_ratio, a=significance, alt="two.sided" if sides == 2 else "one.sided",
        n=math.nan if n is None else float(n), pw=math.nan if power is None else float(power))
    return _first(found["n"]), _first(found["power"])
