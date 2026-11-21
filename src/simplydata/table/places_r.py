"""The R calls of directions, places and extremes (S3c-3), through rpy2 (simplydata[r]).

Each function runs R's own code and gives back plain NumPy values; the words in places.py check the input and say
the result in words. None of these packages is attached: circular masks sd and var, extRemes masks qqnorm, ape masks
trans, and spdep attaches sf. Each is checked with need_r() and called as pkg::fun.

* circular::rayleigh.test on circular(x, units = ...), with the units always given (R circular reads plain numbers
  as radians without a word).
* spdep: the neighbours (all pairs, dnearneigh(0, Inf), or the k nearest, knearneigh), their weights
  (nb2listwdist(type = "idw"): 1 / distance; or nb2listw: each of the k nearest alike), row-standardised
  (style = "W"), and moran.mc() after set.seed(with_seed); moran.test() for the value I takes with no pattern.
  The places are an sf object, so on_globe=True gives great-circle distances (crs 4326).
* gstat: variogram() with its own cutoff and bins, fit.variogram() with gstat's own start values (vgm(model) with
  no numbers) and its default fit.method = 7; variogramLine() for the fitted curve.
* extRemes: fevd() by maximum likelihood (GEV for block maxima, GP for values above a threshold), return.level()
  with the normal-approximation interval, and ci.fevd(method = "proflik") for the profile-likelihood interval;
  extremalindex() for the runs of values above a threshold; mrlplot() and threshrange.plot() for the threshold
  check.
"""

from __future__ import annotations

import math

import numpy as np

# full_turn= -> the units R circular knows; any other full turn is put into degrees first (a change of unit)
CIRCULAR_UNITS = {360.0: "degrees", 24.0: "hours", round(2 * math.pi, 12): "radians"}
# of_kind= -> gstat's model code
VARIOGRAM_MODELS = {"spherical": "Sph", "exponential": "Exp", "gaussian": "Gau", "matern": "Mat"}
MEAN_EXCESS_POINTS = 100  # extRemes::mrlplot's own nint
SHAPE_POINTS = 10  # extRemes::threshrange.plot's own nint


def _need(packages, what):
    from .._r import need_r

    need_r(tuple(packages), what)


def _call(code, what, packages, source, **values):
    """Run R code with the packages checked but not attached (they are called as pkg::fun)."""
    from .._r import r_call

    _need(packages, what)
    return r_call(code, packages=(), what=what, source=source, **values)


def _number(value):
    return float(np.atleast_1d(np.asarray(value, dtype=float))[0])


def _numbers(value):
    return np.atleast_1d(np.asarray(value, dtype=float))


def circular_call(full_turn) -> str:
    """The circular() call for these values, as R code (shown in the printout)."""
    units = CIRCULAR_UNITS.get(round(float(full_turn), 12))
    if units:
        return f'circular::circular(x, units = "{units}", template = "none")'
    return f'circular::circular(x * 360 / {full_turn:g}, units = "degrees", template = "none")'


# ---------------------------------------------------------------- Rayleigh test
def rayleigh(x, full_turn):
    """circular::rayleigh.test(): the mean resultant length (its statistic) and the p-value."""
    code = f"r <- circular::rayleigh.test({circular_call(full_turn)}); list(statistic = r$statistic, p = r$p.value)"
    found = _call(code, "The Rayleigh test (R circular::rayleigh.test())", ("circular",), "circular::rayleigh.test",
                  x=np.asarray(x, dtype=float))
    return {"statistic": _number(found["statistic"]), "p": _number(found["p"])}


# ---------------------------------------------------------------- Moran's I
def moran_code(on_globe, nearest, permutations, seed) -> str:
    crs = ", crs = 4326" if on_globe else ""
    if nearest:
        weights = (f"nb <- spdep::knn2nb(spdep::knearneigh(pts, k = {int(nearest)})); "
                   'lw <- spdep::nb2listw(nb, style = "W"); ')
    else:
        weights = ('nb <- spdep::dnearneigh(pts, 0, Inf); '
                   'lw <- spdep::nb2listwdist(nb, pts, type = "idw", alpha = 1, style = "W"); ')
    return (f'pts <- sf::st_as_sf(data.frame(x = x, y = y), coords = c("x", "y"){crs}); {weights}'
            f"set.seed({int(seed)}); m <- spdep::moran.mc(z, lw, nsim = {int(permutations)}); "
            "t <- spdep::moran.test(z, lw); "
            'l <- spdep::moran.test(z, lw, alternative = "less"); '
            'list(i = m$statistic, p = m$p.value, expected = t$estimate[["Expectation"]], p_less = l$p.value)')


def moran(x, y, z, on_globe=False, nearest=None, permutations=999, seed=1):
    """spdep::moran.mc() on 1 / distance weights between all pairs (or the k nearest), row-standardised."""
    found = _call(moran_code(on_globe, nearest, permutations, seed), "Moran's I (R spdep::moran.mc())",
                  ("spdep", "sf"), "spdep::moran.mc", x=np.asarray(x, dtype=float), y=np.asarray(y, dtype=float),
                  z=np.asarray(z, dtype=float))
    return {"i": _number(found["i"]), "p": _number(found["p"]), "expected": _number(found["expected"]),
            "p_less": _number(found["p_less"])}


# ---------------------------------------------------------------- variogram
def variogram(x, y, z, kind, cutoff=None, line_points=0):
    """gstat::variogram() (gstat's cutoff, a third of the diagonal, and 15 bins, unless cutoff= is given), then
    gstat::fit.variogram(v, vgm(model)) with gstat's own start values; the fitted curve at line_points distances
    (gstat::variogramLine) when asked."""
    model = VARIOGRAM_MODELS[kind]
    cut = f", cutoff = {float(cutoff)!r}" if cutoff is not None else ""
    line = (f"l <- gstat::variogramLine(f, maxdist = max(v$dist), n = {int(line_points)}); "
            if line_points else "l <- NULL; ")
    code = (
        "caught <- character(0); "
        f'v <- gstat::variogram(z ~ 1, locations = ~ x + y, data = data.frame(x = x, y = y, z = z){cut}); '
        f'f <- withCallingHandlers(gstat::fit.variogram(v, gstat::vgm("{model}")), '
        "warning = function(w) { caught <<- c(caught, conditionMessage(w)); invokeRestart('muffleWarning') }); "
        f"{line}"
        "list(dist = v$dist, gamma = v$gamma, np = v$np, nugget = f$psill[1], psill = f$psill[2], "
        "range = f$range[2], kappa = f$kappa[2], singular = isTRUE(attr(f, 'singular')), "
        "fitted = gstat::variogramLine(f, dist_vector = v$dist)$gamma, "
        "warnings = caught, line_dist = if (is.null(l)) NULL else l$dist, "
        "line_gamma = if (is.null(l)) NULL else l$gamma)")
    found = _call(code, "The variogram (R gstat::variogram() and fit.variogram())", ("gstat", "sf"),
                  "gstat::fit.variogram", x=np.asarray(x, dtype=float), y=np.asarray(y, dtype=float),
                  z=np.asarray(z, dtype=float))
    warnings = found.get("warnings")
    out = {k: _numbers(found[k]) for k in ("dist", "gamma", "np", "fitted")}
    out.update({k: _number(found[k]) for k in ("nugget", "psill", "range", "kappa")})
    out["singular"] = bool(np.atleast_1d(found["singular"])[0])
    out["warnings"] = [] if warnings is None else [str(w) for w in np.atleast_1d(warnings)]
    out["line_dist"] = None if found.get("line_dist") is None else _numbers(found["line_dist"])
    out["line_gamma"] = None if found.get("line_gamma") is None else _numbers(found["line_gamma"])
    return out


# ---------------------------------------------------------------- extremes
# The profile-likelihood interval of each return level: extRemes::ci.fevd(method = "proflik") needs the range of
# levels to search (its own default range is too wide for its grid of 20 and fails), and its profile is worked out
# point by point from the low end of that range, so the range must start where the fit is possible. The search runs
# from the low end of the normal-approximation interval (profile intervals of return levels lie above it) to two of
# its widths above its high end, on a grid of 200; when an end of the interval touches an end of the range, or
# extRemes gives no interval, the range is widened (twice at most). The ends themselves are extRemes's.
_PROFILE = """
profile_one <- function(f, period, low, high) {
  w <- high - low
  for (xr in list(c(low, high + 2 * w), c(low - w / 2, high + 3 * w), c(low - w, high + 5 * w))) {
    p <- tryCatch(as.numeric(extRemes::ci.fevd(f, type = "return.level", return.period = period,
                                               method = "proflik", xrange = xr, nint = 200,
                                               verbose = FALSE))[c(1, 3)],
                  error = function(e) c(NA_real_, NA_real_))
    step <- (xr[2] - xr[1]) / 200
    if (!any(is.na(p)) && p[1] > xr[1] + step && p[2] < xr[2] - step) return(p)
  }
  c(NA_real_, NA_real_)
}
"""


def _extremes_code(fit_call, periods_r, extra=""):
    return (_PROFILE +
            f"f <- {fit_call}; "
            "par <- f$results$par; "
            'pci <- extRemes::ci.fevd(f, type = "parameter", method = "normal"); '
            f"rl <- extRemes::return.level(f, return.period = {periods_r}, do.ci = TRUE); "
            "rl <- matrix(as.numeric(rl), ncol = 3); "
            "prof <- t(sapply(seq_len(nrow(rl)), function(i) profile_one(f, "
            f"{periods_r}[i], rl[i, 1], rl[i, 3]))); "
            "list(par = par, names = names(par), par_low = pci[, 1], par_high = pci[, 3], "
            "convergence = f$results$convergence, level = rl[, 2], normal_low = rl[, 1], normal_high = rl[, 3], "
            f"profile_low = prof[, 1], profile_high = prof[, 2]{extra})")


def _periods_r(once_in):
    return "c(" + ", ".join(repr(float(t)) for t in once_in) + ")"


def _extremes_result(found):
    out = {k: _numbers(found[k]) for k in ("par", "par_low", "par_high", "level", "normal_low", "normal_high",
                                            "profile_low", "profile_high")}
    out["names"] = [str(n) for n in np.atleast_1d(found["names"])]
    out["convergence"] = _number(found["convergence"])
    for k in ("extremal_index", "clusters", "above"):
        if k in found and found[k] is not None:
            out[k] = _number(found[k])
    return out


def block_maxima(x, once_in):
    """extRemes::fevd(x, type = "GEV", method = "MLE"): the GEV and its return levels."""
    code = _extremes_code('extRemes::fevd(x, type = "GEV", method = "MLE")', _periods_r(once_in))
    found = _call(code, "Return levels (R extRemes::fevd())", ("extRemes",), "extRemes::fevd",
                  x=np.asarray(x, dtype=float))
    return _extremes_result(found)


def over_threshold(x, threshold, time_units, once_in):
    """extRemes::fevd(x, threshold = u, type = "GP", time.units = ...): the generalised Pareto fit to the values
    above the threshold, its return levels per year, and the extremal index (extRemes::extremalindex)."""
    fit = f'extRemes::fevd(x, threshold = {float(threshold)!r}, type = "GP", time.units = "{time_units}")'
    extra = (", extremal_index = e[[1]], clusters = e[[2]], above = sum(x > "
             f"{float(threshold)!r})")
    code = (f"e <- extRemes::extremalindex(x, {float(threshold)!r}); " + _extremes_code(fit, _periods_r(once_in), extra))
    found = _call(code, "Return levels above a threshold (R extRemes::fevd())", ("extRemes",), "extRemes::fevd",
                  x=np.asarray(x, dtype=float))
    return _extremes_result(found)


def threshold_check(x, low, high):
    """The two panels of the threshold check: extRemes::mrlplot() (the mean excess with its 95 % interval, at
    mrlplot's own thresholds) and extRemes::threshrange.plot(type = "GP") (the GP shape with its 95 % interval, at
    SHAPE_POINTS thresholds from low to high). Both draw into nothing; their values are drawn by matplotlib."""
    code = (
        "r <- range(x, finite = TRUE); "
        # the thresholds of extRemes::mrlplot, written as in its source (seq(r[1], r[2] - 1, , nint)); it returns
        # the values only, so they are rebuilt here; tests/test_s3c3_places.py and the reliability case check them
        f"mu <- seq(r[1], r[2] - 1, length.out = {MEAN_EXCESS_POINTS}); "
        f"m <- extRemes::mrlplot(x, nint = {MEAN_EXCESS_POINTS}); "
        f"su <- seq({float(low)!r}, {float(high)!r}, length.out = {SHAPE_POINTS}); "  # threshrange.plot's own
        f'tr <- extRemes::threshrange.plot(x, r = c({float(low)!r}, {float(high)!r}), nint = {SHAPE_POINTS}, '
        'type = "GP"); '
        "list(mean_u = mu, mean_low = m[, 1], mean = m[, 2], mean_high = m[, 3], shape_u = su, "
        'shape_low = tr[, "low.shape"], shape = tr[, "shape"], shape_high = tr[, "up.shape"])')
    found = _call(code, "The threshold check (R extRemes::mrlplot() and threshrange.plot())", ("extRemes",),
                  "extRemes::threshrange.plot", x=np.asarray(x, dtype=float))
    return {k: _numbers(v) for k, v in found.items()}



