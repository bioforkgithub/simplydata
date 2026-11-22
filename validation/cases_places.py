"""The reliability study for phase S3c-3, directions, places and extremes: find_average_direction_of, the Rayleigh test
(compare_shape_to with full_turn=), Moran's I (find_autocorrelation_of with x= and y=), find_variogram_of,
draw_variogram, find_return_levels_of, draw_threshold_check and the GEV family of fit_distribution_to.

cases.py loads this file at its end and calls add_to(), which adds the datasets and cases below to its own DATASETS
and CASES and teaches load() the datasets read from R packages (circular, sp, ismev: not stored here, their licence is
the packages', GPL, so they are read where they are published).

Published answers: Coles (2001), An Introduction to Statistical Modeling of Extreme Values (Port Pirie, section
3.4.1; daily rain, section 4.4.1), at the printed rounding; the gstat vignette for the meuse variogram. Moran's I is
checked against ape::Moran.I (another package, the same 1 / distance weights) and its p-value against spdep.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

R_DATA_PLACES = {
    "turtles (circular)": (("circular",), 'e <- new.env(); utils::data("turtles", package = "circular", envir = e); '
                                          "list(arrival = as.numeric(e$turtles$arrival))"),
    "ICU arrivals (circular)": (("circular",), 'e <- new.env(); utils::data("fisherB1c", package = "circular", '
                                               "envir = e); list(hour = as.numeric(e$fisherB1c))"),
    "meuse (sp)": (("sp",), 'e <- new.env(); utils::data("meuse", package = "sp", envir = e); '
                            "list(x = e$meuse$x, y = e$meuse$y, zinc = e$meuse$zinc, log_zinc = log(e$meuse$zinc))"),
    "meuse in longitude and latitude (sp, sf)": (
        ("sp", "sf"), 'e <- new.env(); utils::data("meuse", package = "sp", envir = e); '
                      'p <- sf::st_transform(sf::st_as_sf(e$meuse, coords = c("x", "y"), crs = 28992), 4326); '
                      "xy <- sf::st_coordinates(p); list(lon = xy[, 1], lat = xy[, 2], log_zinc = log(e$meuse$zinc))"),
    "Port Pirie (ismev)": (("ismev",), 'e <- new.env(); utils::data("portpirie", package = "ismev", envir = e); '
                                       "list(year = e$portpirie$Year, sea_level = e$portpirie$SeaLevel)"),
    "Coles rain (ismev)": (("ismev",), 'e <- new.env(); utils::data("rain", package = "ismev", envir = e); '
                                       "list(rain = as.numeric(e$rain))"),
}
OURS_R = {"table.find_average_direction_of": None, "table.compare_shape_to": ("circular",),
          "table.find_autocorrelation_of": ("spdep", "sf"), "table.find_variogram_of": ("gstat", "sf"),
          "draw_variogram": ("gstat", "sf"), "table.find_return_levels_of": ("extRemes",),
          "draw_threshold_check": ("extRemes",), "table.fit_distribution_to": None}
COLES = "Coles (2001), An Introduction to Statistical Modeling of Extreme Values"


def _datasets(Dataset):
    return [
        Dataset("turtles (circular)", "", "the directions from which 10 green sea turtles, displaced to the open sea, "
                "came back to Ascension Island (degrees)",
                "Luschi, P. et al. (2001). Testing the navigational abilities of ocean migrants: displacement experiments "
                "on green sea turtles (Chelonia mydas). Behavioral Ecology and Sociobiology 50, 528-534. Shipped with the "
                "R package circular (turtles; Agostinelli & Lund).",
                "GPL-2 (circular); read from the installed package, so it needs R.",
                "https://doi.org/10.1007/s002650100396"),
        Dataset("ICU arrivals (circular)", "", "the time of day (24-hour clock) at which 254 patients arrived at an "
                "intensive care unit over about 12 months",
                "Cox, D. R. & Lewis, P. A. W. (1966). The Statistical Analysis of Series of Events. Methuen, pp. 254-255; "
                "Fisher, N. I. (1993). Statistical Analysis of Circular Data. Cambridge University Press, data set B.1. "
                "Shipped with the R package circular (fisherB1c).",
                "GPL-2 (circular); read from the installed package, so it needs R.",
                "https://cran.r-project.org/package=circular"),
        Dataset("meuse (sp)", "", "155 topsoil samples in the flood plain of the river Meuse near Stein (NL): where "
                "each was taken (x, y in metres, RD New) and its zinc in mg/kg",
                "Rikken, M. G. J. & Van Rijn, R. P. G. (1993). Soil pollution with heavy metals: an inquiry into spatial "
                "variation, cost of mapping and the risk evaluation of copper, cadmium, lead and zinc in the floodplains "
                "of the Meuse west of Stein. Doctoraalveldwerkverslag, Utrecht University. Shipped with the R package sp "
                "(meuse); its variogram is the gstat vignette's example (Pebesma 2004, Computers & Geosciences 30, "
                "683-691).", "GPL-2 | GPL-3 (sp); read from the installed package, so it needs R.",
                "https://cran.r-project.org/package=sp"),
        Dataset("meuse in longitude and latitude (sp, sf)", "", "the same 155 meuse samples, their places turned "
                "from the Dutch grid (RD New, EPSG 28992) into longitude and latitude (EPSG 4326) by R sf::st_transform",
                "As meuse (sp) above; the transformation by PROJ through R sf (Pebesma, E. (2018). Simple Features "
                "for R. The R Journal 10(1), 439-446).",
                "GPL-2 | GPL-3 (sp); read from the installed package and transformed there, so it needs R.",
                "https://doi.org/10.32614/RJ-2018-009"),
        Dataset("Port Pirie (ismev)", "", "the highest sea level of each year at Port Pirie, South Australia, "
                "1923-1987 (metres)",
                f"{COLES}, Springer, section 3.4.1. Shipped with the R package ismev (portpirie); simplydata's "
                "practice table sea_levels is made up after it.",
                "GPL (>= 2) (ismev); read from the installed package, so it needs R.",
                "https://doi.org/10.1007/978-1-4471-3675-0"),
        Dataset("Coles rain (ismev)", "", "17,531 daily rainfall totals at one site in south-west England, 1914-1962 (mm)",
                f"{COLES}, Springer, section 4.4.1. Shipped with the R package ismev (rain).",
                "GPL (>= 2) (ismev); read from the installed package, so it needs R.",
                "https://doi.org/10.1007/978-1-4471-3675-0"),
    ]


def _cases(Case):
    return [
        # ---------------------------------------------------------------- AC01: circular summaries
        Case("table.find_average_direction_of", "turtles: the average direction of 10 homing turtles",
             "turtles (circular)", "real data",
             ours="""
                 r = sdata.table(data).find_average_direction_of("arrival", full_turn=360).as_pandas()
                 {"average direction": r["average direction"][0], "resultant length": r["resultant length"][0],
                  "circular standard deviation (degrees)": r["circular standard deviation"][0]}
             """,
             parent="""
                 import numpy as np
                 from scipy import stats
                 a = data["arrival"].to_numpy(dtype=float)
                 t = np.deg2rad(a)
                 {"average direction": stats.circmean(a, high=360, low=0),
                  "resultant length": stats.directional_stats(np.column_stack([np.cos(t), np.sin(t)])).mean_resultant_length,
                  "circular standard deviation (degrees)": stats.circstd(a, high=360, low=0)}
             """, parent_label="SciPy circmean, directional_stats, circstd",
             r="""
                 a <- circular::circular(arrival, units = "degrees", template = "none")
                 m <- as.numeric(circular::mean.circular(a))
                 list(`average direction` = (m + 360) %% 360, `resultant length` = circular::rho.circular(a),
                      `circular standard deviation (degrees)` = as.numeric(circular::sd.circular(a)) * 180 / pi)
             """, r_packages=("circular",), r_tolerance=1e-9,
             note="R circular gives the mean as -42.76 degrees; shown here from 0 to 360 (317.24), as simplydata gives "
                  "it. R sd.circular gives radians; shown here in degrees."),
        Case("table.find_average_direction_of", "ICU arrivals: the average time of day of 254 arrivals (full_turn=24)",
             "ICU arrivals (circular)", "real data",
             ours="""
                 r = sdata.table(data).find_average_direction_of("hour", full_turn=24).as_pandas()
                 {"average hour": r["average direction"][0], "resultant length": r["resultant length"][0]}
             """,
             r="""
                 a <- circular::circular(hour, units = "hours", template = "none")
                 list(`average hour` = (as.numeric(circular::mean.circular(a)) + 24) %% 24,
                      `resultant length` = circular::rho.circular(a))
             """, r_packages=("circular",), r_tolerance=1e-9,
             note="R circular gives -6.74 hours, the same time of day as 17.26 (about 17:16)."),
        # ---------------------------------------------------------------- AC02: Rayleigh
        Case("table.compare_shape_to", 'shape="even around the circle": turtles, the Rayleigh test',
             "turtles (circular)", "real data",
             ours="""
                 r = sdata.table(data).compare_shape_to("arrival", shape="even around the circle",
                                                        full_turn=360).as_pandas()
                 {"resultant length": r["statistic"][0], "p-value": r["p-value"][0]}
             """,
             r="""
                 t <- circular::rayleigh.test(circular::circular(arrival, units = "degrees", template = "none"))
                 list(`resultant length` = t$statistic, `p-value` = t$p.value)
             """, r_packages=("circular",), r_tolerance=1e-9,
             note="Without units = \"degrees\" R circular reads the degrees as radians and gives p = 0.15 instead of "
                  "0.0003 (the trap simplydata avoids by always giving the units)."),
        Case("table.compare_shape_to", 'shape="even around the circle": ICU arrivals by hour (full_turn=24)',
             "ICU arrivals (circular)", "real data",
             ours="""
                 r = sdata.table(data).compare_shape_to("hour", shape="even around the circle", full_turn=24).as_pandas()
                 {"resultant length": r["statistic"][0], "p-value": r["p-value"][0]}
             """,
             r="""
                 t <- circular::rayleigh.test(circular::circular(hour, units = "hours", template = "none"))
                 list(`resultant length` = t$statistic, `p-value` = t$p.value)
             """, r_packages=("circular",), r_tolerance=1e-9),
        # ---------------------------------------------------------------- AC08: Moran's I
        Case("table.find_autocorrelation_of", "x=: meuse, Moran's I of log zinc with 1 / distance weights",
             "meuse (sp)", "real data",
             ours="""
                 r = sdata.table(data).find_autocorrelation_of("log_zinc", x="x", y="y").as_pandas()
                 {"Moran's I": r["Moran's I"][0], "p-value (999 shuffles, seed 1)": r["p-value"][0]}
             """,
             r="""
                 w <- 1 / as.matrix(stats::dist(cbind(x, y))); diag(w) <- 0
                 pts <- sf::st_as_sf(data.frame(x = x, y = y), coords = c("x", "y"))
                 lw <- spdep::nb2listwdist(spdep::dnearneigh(pts, 0, Inf), pts, type = "idw", alpha = 1, style = "W")
                 set.seed(1)
                 list(`Moran's I` = ape::Moran.I(log_zinc, w)$observed,
                      `p-value (999 shuffles, seed 1)` = spdep::moran.mc(log_zinc, lw, nsim = 999)$p.value)
             """, r_packages=("ape", "spdep", "sf"), r_tolerance=1e-9,
             note="Moran's I from ape::Moran.I on the 1 / distance weights (ape scales each row to 1 itself): 0.1191, "
                  "the number of the design's check; the p-value from spdep::moran.mc."),
        Case("table.find_autocorrelation_of", "nearest=: meuse, Moran's I of log zinc with the 8 nearest samples",
             "meuse (sp)", "real data",
             ours="""
                 r = sdata.table(data).find_autocorrelation_of("log_zinc", x="x", y="y", nearest=8).as_pandas()
                 {"Moran's I": r["Moran's I"][0]}
             """,
             r="""
                 nb <- spdep::knn2nb(spdep::knearneigh(cbind(x, y), k = 8))
                 list(`Moran's I` = spdep::moran(log_zinc, spdep::nb2listw(nb, style = "W"), length(x),
                                                 spdep::Szero(spdep::nb2listw(nb, style = "W")))$I)
             """, r_packages=("spdep",), r_tolerance=1e-9,
             note="With only the 8 nearest neighbours Moran's I is 0.49 instead of 0.12: the weights change the answer."),
        Case("table.find_autocorrelation_of", "on_globe=: meuse in longitude and latitude, great-circle 1 / distance",
             "meuse in longitude and latitude (sp, sf)", "real data",
             ours="""
                 r = sdata.table(data).find_autocorrelation_of("log_zinc", x="lon", y="lat", on_globe=True).as_pandas()
                 {"Moran's I": r["Moran's I"][0]}
             """,
             r="""
                 pts <- sf::st_as_sf(data.frame(x = lon, y = lat), coords = c("x", "y"), crs = 4326)
                 lw <- spdep::nb2listwdist(spdep::dnearneigh(pts, 0, Inf), pts, type = "idw", alpha = 1, style = "W")
                 list(`Moran's I` = spdep::moran(log_zinc, lw, length(log_zinc), spdep::Szero(lw))$I)
             """, r_packages=("spdep", "sf"), r_tolerance=1e-9,
             note="Over 3 km great-circle and grid distances hardly differ, so Moran's I is close to the grid's 0.1191."),
        # ---------------------------------------------------------------- AC09: variogram
        Case("table.find_variogram_of", "meuse: the spherical variogram of log zinc", "meuse (sp)", "published",
             ours="""
                 r = sdata.table(data).find_variogram_of("log_zinc", x="x", y="y").as_pandas()
                 {"nugget": r["nugget"][0], "partial sill": r["partial sill"][0], "range": r["range"][0],
                  "first bin semivariance": r["semivariance"][0]}
             """,
             published={"nugget": (0.0507, 0.00005, "gstat vignette (Pebesma)"),
                        "partial sill": (0.5906, 0.00005, "gstat vignette (Pebesma)"),
                        "range": (897.0, 0.5, "gstat vignette (Pebesma)")},
             r="""
                 v <- gstat::variogram(log_zinc ~ 1, locations = ~ x + y, data = data.frame(x = x, y = y, log_zinc = log_zinc))
                 f <- gstat::fit.variogram(v, gstat::vgm("Sph"))
                 list(nugget = f$psill[1], `partial sill` = f$psill[2], range = f$range[2],
                      `first bin semivariance` = v$gamma[1])
             """, r_packages=("gstat", "sf"), r_tolerance=1e-7,
             note="The gstat vignette fits vgm(1, \"Sph\", 900, 1) and prints nugget 0.0507, partial sill 0.5906 and "
                  "range 897; simplydata lets gstat choose its own start values and reaches the same fit."),
        Case("draw_variogram", "meuse: the dots and the curve of the variogram of log zinc", "meuse (sp)", "real data",
             ours="""
                 chart = sdata.chart(data).draw_variogram("log_zinc", x="x", y="y")
                 ax = chart._render().axes[0]
                 dots = ax.collections[0].get_offsets()
                 line = ax.get_lines()[0]
                 {"last bin distance": dots[-1][0], "last bin semivariance": dots[-1][1],
                  "curve at its end": line.get_ydata()[-1]}
             """,
             r="""
                 v <- gstat::variogram(log_zinc ~ 1, locations = ~ x + y, data = data.frame(x = x, y = y, log_zinc = log_zinc))
                 f <- gstat::fit.variogram(v, gstat::vgm("Sph"))
                 l <- gstat::variogramLine(f, maxdist = max(v$dist), n = 200)
                 list(`last bin distance` = v$dist[15], `last bin semivariance` = v$gamma[15],
                      `curve at its end` = l$gamma[200])
             """, r_packages=("gstat", "sf"), r_tolerance=1e-7),
        # ---------------------------------------------------------------- AB07: block maxima
        Case("table.find_return_levels_of", "Port Pirie: the 10- and 100-year sea levels", "Port Pirie (ismev)",
             "published",
             ours="""
                 r = sdata.table(data).find_return_levels_of("sea_level", once_in=[10, 100], sorted_by="year").as_pandas()
                 {"10-year level": r["level"][0], "100-year level": r["level"][1],
                  "100-year normal 95 % CI low": r["normal 95 % CI low"][1],
                  "100-year normal 95 % CI high": r["normal 95 % CI high"][1]}
             """,
             published={"10-year level": (4.30, 0.005, f"{COLES}, 3.4.1"),
                        "100-year level": (4.69, 0.005, f"{COLES}, 3.4.1"),
                        "100-year normal 95 % CI low": (4.38, 0.005, f"{COLES}, 3.4.1"),
                        "100-year normal 95 % CI high": (5.00, 0.005, f"{COLES}, 3.4.1")},
             r="""
                 f <- extRemes::fevd(sea_level, type = "GEV", method = "MLE")
                 rl <- matrix(as.numeric(extRemes::return.level(f, return.period = c(10, 100), do.ci = TRUE)), ncol = 3)
                 list(`10-year level` = rl[1, 2], `100-year level` = rl[2, 2],
                      `100-year normal 95 % CI low` = rl[2, 1], `100-year normal 95 % CI high` = rl[2, 3])
             """, r_packages=("extRemes",), r_tolerance=1e-9),
        Case("table.find_return_levels_of", "Port Pirie: the profile-likelihood interval of the 100-year level",
             "Port Pirie (ismev)", "real data",
             ours="""
                 r = sdata.table(data).find_return_levels_of("sea_level", once_in=[100], sorted_by="year")
                 {"100-year profile 95 % CI low": r.get_cell_at(row=1, column="95 % CI low"),
                  "100-year profile 95 % CI high": r.get_cell_at(row=1, column="95 % CI high")}
             """,
             r="""
                 f <- extRemes::fevd(sea_level, type = "GEV", method = "MLE")
                 rl <- as.numeric(extRemes::return.level(f, return.period = 100, do.ci = TRUE)); w <- rl[3] - rl[1]
                 p <- extRemes::ci.fevd(f, type = "return.level", return.period = 100, method = "proflik",
                                        xrange = c(rl[1], rl[3] + 2 * w), nint = 200)
                 list(`100-year profile 95 % CI low` = p[1], `100-year profile 95 % CI high` = p[3])
             """, r_packages=("extRemes",), r_tolerance=1e-9,
             note="The same grid simplydata asks extRemes for (200 levels from the lower normal end to two widths "
                  "above the upper one), so the ends agree to 1e-9. How close a 200-point grid comes to the exact "
                  "profile ends is the next case."),
        Case("table.find_return_levels_of",
             "Port Pirie: the profile-likelihood interval of the 100-year level, against the exact profile",
             "Port Pirie (ismev)", "real data",
             ours="""
                 r = sdata.table(data).find_return_levels_of("sea_level", once_in=[100], sorted_by="year")
                 {"100-year profile 95 % CI low": r.get_cell_at(row=1, column="95 % CI low"),
                  "100-year profile 95 % CI high": r.get_cell_at(row=1, column="95 % CI high")}
             """,
             r="""
                 f <- extRemes::fevd(sea_level, type = "GEV", method = "MLE",
                                     optim.args = list(method = "BFGS", control = list(reltol = 1e-14, maxit = 1e5)))
                 par <- f$results$par; best <- f$results$value; p <- 1 / 100
                 nll <- function(z, s, xi) { mu <- z + s / xi * (1 - (-log(1 - p))^(-xi))
                   t <- 1 + xi * (sea_level - mu) / s; if (s <= 0 || any(t <= 0)) return(1e10)
                   sum(log(s) + (1 + 1 / xi) * log(t) + t^(-1 / xi)) }
                 prof <- function(z) stats::optim(par[2:3], function(q) nll(z, q[1], q[2]),
                                                  control = list(reltol = 1e-14, maxit = 1e5))$value
                 g <- function(z) 2 * (prof(z) - best) - stats::qchisq(0.95, 1)
                 zhat <- par[1] - par[2] / par[3] * (1 - (-log(1 - p))^(-par[3]))
                 list(`100-year profile 95 % CI low` = stats::uniroot(g, c(zhat - 1, zhat), tol = 1e-12)$root,
                      `100-year profile 95 % CI high` = stats::uniroot(g, c(zhat, zhat + 3), tol = 1e-12)$root)
             """, r_packages=("extRemes",), r_tolerance=2.5e-3,
             note="The exact ends: the profile log-likelihood of the 100-year level (the GEV written with the level "
                  "as a parameter, Coles 2001, section 3.3.3) maximised over the other two at each level, and the "
                  "level where it falls by half the chi-square 95 % point found by root finding (uniroot, to "
                  "1e-12). extRemes reads the ends off its grid, so simplydata's ends may lie one grid step (0.0093 "
                  "here, 1/200 of the range searched; 0.2 % of the level) from the exact ones: the tolerance is "
                  "that step, a stated limit of the grid, not of the fit. A finer grid takes minutes for the "
                  "threshold fits."),
        Case("table.fit_distribution_to", 'distribution="gev": Port Pirie, the GEV parameters', "Port Pirie (ismev)",
             "published",
             ours="""
                 r = sdata.table(data).fit_distribution_to("sea_level", distribution="gev").turn_into_table().as_pandas()
                 {"location": r["location"][0], "scale": r["scale"][0], "shape": r["shape"][0]}
             """,
             published={"location": (3.87, 0.005, f"{COLES}, 3.4.1"), "scale": (0.198, 0.0005, f"{COLES}, 3.4.1"),
                        "shape": (-0.050, 0.0005, f"{COLES}, 3.4.1")},
             parent="""
                 from scipy import optimize, stats
                 def tight(func, x0, args=(), disp=0):
                     return optimize.fmin(func, x0, args=args, xtol=1e-14, ftol=1e-14, maxiter=100000, maxfun=100000,
                                          disp=0)
                 c, loc, scale = stats.genextreme.fit(data["sea_level"].to_numpy(dtype=float), optimizer=tight)
                 {"location": loc, "scale": scale, "shape": -c}
             """, parent_label="SciPy genextreme.fit run to 1e-14 (shape c = -xi)", parent_tolerance=1e-6,
             r="""
                 p <- extRemes::fevd(sea_level, type = "GEV", method = "MLE",
                                     optim.args = list(method = "BFGS",
                                                       control = list(reltol = 1e-14, maxit = 100000)))$results$par
                 list(location = p[["location"]], scale = p[["scale"]], shape = p[["shape"]])
             """, r_packages=("extRemes",), r_tolerance=1e-6,
             note="SciPy's own fit stops a little short of the maximum (by up to 8e-5 here), so simplydata polishes "
                  "it. Both references are run to 1e-14 (SciPy's fit with a tighter Nelder-Mead, R extRemes with "
                  "optim's reltol 1e-14) and agree with simplydata to 1e-6; the shape, near 0, is the least "
                  "precise (2e-7 relative). Before, the default fits were the references, at 5e-3 and 1e-4."),
        # ---------------------------------------------------------------- AB08: above a threshold
        Case("table.find_return_levels_of", "values_above=: Coles's daily rain above 30 mm, the 100-year level",
             "Coles rain (ismev)", "published",
             ours="""
                 daily = data.assign(date=pd.date_range("1914-01-01", periods=len(data), freq="D"))
                 r = sdata.table(daily).find_return_levels_of("rain", once_in=[100], values_above=30,
                                                             sorted_by="date").as_pandas()
                 {"100-year level": r["level"][0], "100-year normal 95 % CI low": r["normal 95 % CI low"][0],
                  "100-year normal 95 % CI high": r["normal 95 % CI high"][0]}
             """,
             published={"100-year level": (106.3, 0.05, f"{COLES}, 4.4.1")},
             r="""
                 f <- extRemes::fevd(rain, threshold = 30, type = "GP", time.units = "days",
                                     optim.args = list(method = "BFGS", control = list(reltol = 1e-14, maxit = 100000)))
                 rl <- as.numeric(extRemes::return.level(f, return.period = 100, do.ci = TRUE))
                 list(`100-year level` = rl[2], `100-year normal 95 % CI low` = rl[1],
                      `100-year normal 95 % CI high` = rl[3])
             """, r_packages=("extRemes",), r_tolerance=1e-9,
             note="Coles fits sigma 7.44 and xi 0.184 above 30 mm; simplydata gives them in its printout (7.44, 0.184). "
                  "The R reference is fevd run to reltol 1e-14; with optim's default stopping rule the 100-year level "
                  "stopped 1e-6 to 9e-6 short, so simplydata asks for reltol 1e-12."),
        Case("table.fit_distribution_to", 'distribution="generalised pareto": Coles rain, the amounts above 30 mm',
             "Coles rain (ismev)", "published",
             ours="""
                 above = pd.DataFrame({"excess": data["rain"][data["rain"] > 30] - 30})
                 r = sdata.table(above).fit_distribution_to("excess", distribution="generalised pareto")
                 r = r.turn_into_table().as_pandas()
                 {"scale": r["scale"][0], "shape": r["shape"][0]}
             """,
             published={"scale": (7.44, 0.005, f"{COLES}, 4.4.1"), "shape": (0.184, 0.0005, f"{COLES}, 4.4.1")},
             r="""
                 p <- extRemes::fevd(rain, threshold = 30, type = "GP", method = "MLE")$results$par
                 list(scale = p[["scale"]], shape = p[["shape"]])
             """, r_packages=("extRemes",), r_tolerance=1e-4),
        Case("draw_threshold_check", "Coles's daily rain: the mean excess and the shape from 20 to 40 mm",
             "Coles rain (ismev)", "real data",
             ours="""
                 chart = sdata.chart(data).draw_threshold_check(x="rain", between=[20, 40])
                 top, bottom = chart._render().axes[0].child_axes
                 m = top.get_lines()[0]
                 shape = bottom.get_lines()[0].get_ydata()
                 {"first mean excess": m.get_ydata()[0], "first threshold shown": m.get_xdata()[0],
                  "shape at 20": shape[0], "shape at 40": shape[-1]}
             """,
             r="""
                 r <- range(rain); u <- seq(r[1], r[2] - 1, length.out = 100)
                 m <- extRemes::mrlplot(rain, nint = 100)
                 first <- which(u >= 20)[1]
                 tr <- extRemes::threshrange.plot(rain, r = c(20, 40), nint = 10, type = "GP")
                 list(`first mean excess` = m[first, 2], `first threshold shown` = u[first],
                      `shape at 20` = tr[1, "shape"], `shape at 40` = tr[10, "shape"])
             """, r_packages=("extRemes",), r_tolerance=1e-9,
             note="Coles (2001, 4.4.1, Figures 4.1 and 4.2) reads both panels as settling from about 30 mm."),
    ]


def add_to(namespace) -> None:
    """Add the S3c-3 datasets and cases to cases.py, and teach its load() the datasets read from R packages."""
    Dataset, Case = namespace["Dataset"], namespace["Case"]
    for d in _datasets(Dataset):
        namespace["DATASETS"][d.name] = d
    import dataclasses

    cases = []
    for c in _cases(Case):
        head = c.title.split(":")[0]
        option = head if "=" in head else ""
        cases.append(dataclasses.replace(c, ours_r=OURS_R.get(c.word), option=option))
    namespace["CASES"].extend(cases)
    namespace.setdefault("R_DATA", {}).update({name: packages for name, (packages, _) in R_DATA_PLACES.items()})
    plain_load = namespace["load"]

    def load(name: str) -> pd.DataFrame:
        if name in R_DATA_PLACES:
            from simplydata._r import need_r, r_call

            packages, code = R_DATA_PLACES[name]
            need_r(packages, f"the {name} data")
            found = r_call(code, what=f"the {name} data")
            return pd.DataFrame({k: np.asarray(v, dtype=float) for k, v in found.items()})
        return plain_load(name)

    namespace["load"] = load
