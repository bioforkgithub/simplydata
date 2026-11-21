"""The R calls of phase S3d-2 for epidemiology: attributable fractions and standardised rates, all from R epiR.
simplydata counts the rows, puts the counts in and words the answer; every number comes from epiR.

* compare_risks(show="attributable fractions"): R epiR::epi.2by2(method = "cohort.count") gives the attributable
  fraction among the exposed ($massoc.detail$AFRisk.strata.wald) and in the whole population (PAFRisk.strata.wald),
  Wald intervals from the risk ratio (Rothman, Greenland & Lash 2008). For an exposure that goes with fewer events
  (risk ratio below 1), the preventable fraction among the exposed (1 - risk ratio) is epiR's attributable fraction
  with the two groups' roles swapped: the same call with the rows of the 2 x 2 table in the other order.
  epiR before 2.0 named these AFest and PAFest; the code reads the names and stops with a sentence when they change.
* rate_of(allowing_for=, standard_population=): direct standardisation, R epiR::epi.directadj(obs, tar, std, units,
  conf.level): the crude rate with its exact interval and the adjusted rate with Fay & Feuer's (1997) gamma
  interval, the same numbers as R epitools::ageadjust.direct().
* compare_rates(allowing_for=, standard_rates=): indirect standardisation, R epiR::epi.indirectadj(obs, pop, std,
  units, conf.level): the expected events from the standard rates, the standardised ratio observed / expected (SMR)
  with its exact Poisson interval, and the p-value of R stats::poisson.test(observed, expected) (the same
  interval).
"""

from __future__ import annotations

import math

import numpy as np

from .._errors import SimplydataError

# epiR 2.0 renamed the attributable fractions (AFest -> AFRisk); the names read from $massoc.detail
AF_NAMES = ("AFRisk.strata.wald", "PAFRisk.strata.wald")
_R_2BY2 = ("r <- epiR::epi.2by2(dat = as.table(matrix(n, nrow = 2, byrow = TRUE)), method = \"cohort.count\", "
           "conf.level = level); d <- r$massoc.detail; "
           "list(names = names(d), af = unlist(d$AFRisk.strata.wald), paf = unlist(d$PAFRisk.strata.wald), "
           "rr = unlist(d$RR.strata.wald), version = as.character(utils::packageVersion(\"epiR\")))")

_R_DIRECT = ("obs <- matrix(o, nrow = ng, dimnames = list(g, b)); tar <- matrix(t, nrow = ng, dimnames = list(g, b)); "
             "std <- matrix(s, nrow = 1, dimnames = list(\"\", b)); "
             "r <- epiR::epi.directadj(obs = obs, tar = tar, std = std, units = per, conf.level = level); "
             "list(crude = r$crude.strata$est, crude_low = r$crude.strata$lower, crude_high = r$crude.strata$upper, "
             "adj = r$adj.strata$est, adj_low = r$adj.strata$lower, adj_high = r$adj.strata$upper, "
             "names = as.character(r$adj.strata$strata), crude_names = as.character(r$crude.strata$strata))")

# the standard rates are given per `per` units of time; epiR wants them per one unit: rate / per (listed for the
# owner's approval as a unit conversion, like the "times per=" of rate_of)
_R_INDIRECT = ("obs <- matrix(o, ncol = 1, dimnames = list(g, \"\")); pop <- matrix(t, nrow = ng, dimnames = list(g, b)); "
               "std <- matrix(c(s / per, NA), nrow = 1, dimnames = list(\"\", c(b, \"Total\"))); "
               "r <- epiR::epi.indirectadj(obs = obs, pop = pop, std = std, units = per, conf.level = level); "
               # epiR sorts the strata by name (as text, by the locale): read them back by name, never by position
               "sm <- r$smr.strata[match(g, rownames(r$smr.strata)), , drop = FALSE]; "
               "list(obs = sm$obs, exp = sm$exp, smr = sm$est, low = sm$lower, high = sm$upper, "
               "p = sapply(seq_len(nrow(sm)), function(i) stats::poisson.test(round(sm$obs[i]), sm$exp[i])$p.value), "
               "names = rownames(sm))")

NOTE = "without R, compare_risks() without show= gives the risk ratio from statsmodels"


def attributable(exposed, unexposed, level):
    """{af, paf, rr} (each (estimate, low, high) as shares) from R epiR::epi.2by2; exposed and unexposed are
    (events, total)."""
    from .._r import r_call

    (e1, n1), (e0, n0) = exposed, unexposed
    counts = np.array([e1, n1 - e1, e0, n0 - e0], dtype=float)
    found = r_call(_R_2BY2, packages=("epiR",), what="Attributable fractions (R epiR::epi.2by2())",
                   python_note=NOTE, source="epiR::epi.2by2", n=counts, level=level / 100)
    names = [str(n) for n in np.atleast_1d(found.get("names"))]
    if not all(n in names for n in AF_NAMES) or found.get("af") is None:
        raise SimplydataError(
            f"R epiR {np.atleast_1d(found.get('version'))[0]} names its attributable fractions differently "
            f"({', '.join(n for n in names if 'AF' in n) or 'none found'}); simplydata reads {AF_NAMES[0]} and "
            f"{AF_NAMES[1]} (epiR 2.0 and later). Update epiR in R: install.packages(\"epiR\").")

    def three(key):
        values = [float(v) for v in np.asarray(found[key], dtype=float).ravel()[:3]]
        return tuple(values + [math.nan] * (3 - len(values)))

    return {"af": three("af"), "paf": three("paf"), "rr": three("rr")}


def _in_order(found, groups, keys, what):
    """The R answer as arrays in the order of groups; stops when R's strata names are not the groups in that order."""
    wanted = [str(x) for x in groups]
    for key in keys:
        got = [str(x) for x in np.atleast_1d(found.get(key))]
        if got != wanted:
            raise SimplydataError(f"{what} gave its groups in another order ({got[:5]}) than simplydata sent "
                                  f"({wanted[:5]}); this is a bug in simplydata, please report it.")
    return {k: np.asarray(v, dtype=float).ravel() for k, v in found.items() if k not in keys}


def direct(groups, bands, events, times, standard, per, level):
    """epiR::epi.directadj: {crude, crude_low, crude_high, adj, adj_low, adj_high}, one value per group (per `per`
    units of time). events, times: arrays groups x bands; standard: one population size per band."""
    from .._r import r_call

    found = r_call(_R_DIRECT, packages=("epiR",), what="Direct standardisation (R epiR::epi.directadj())",
                   python_note="without R, rate_of() without allowing_for= gives the crude rates (statsmodels)",
                   source="epiR::epi.directadj", o=np.asarray(events, dtype=float), t=np.asarray(times, dtype=float),
                   s=np.asarray(standard, dtype=float), ng=float(len(groups)), g=[str(x) for x in groups],
                   b=[str(x) for x in bands], per=float(per), level=level / 100)
    return _in_order(found, groups, ("names", "crude_names"), "R epiR::epi.directadj()")


def indirect(groups, bands, events, times, rates, per, level):
    """epiR::epi.indirectadj: {obs, exp, smr, low, high, p}, one value per group. events: total per group; times:
    groups x bands; rates: the standard rate of each band per `per` units of time."""
    from .._r import r_call

    found = r_call(_R_INDIRECT, packages=("epiR",),
                   what="Indirect standardisation, observed / expected (R epiR::epi.indirectadj())",
                   python_note="without R, compare_rates() without standard_rates= compares the groups' rates "
                               "(statsmodels)",
                   source="epiR::epi.indirectadj", o=np.asarray(events, dtype=float),
                   t=np.asarray(times, dtype=float), s=np.asarray(rates, dtype=float), ng=float(len(groups)),
                   g=[str(x) for x in groups], b=[str(x) for x in bands], per=float(per), level=level / 100)
    return _in_order(found, groups, ("names",), "R epiR::epi.indirectadj()")
