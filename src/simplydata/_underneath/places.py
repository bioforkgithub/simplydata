"""Directions, places and extremes (phase S3c-3): the new words find_average_direction_of, find_variogram_of,
find_return_levels_of, draw_variogram and draw_threshold_check, and one entry for each new option or value that
changes what a word calls (keyed by word and option), on the practice tables "stations" (made up), "rain" (made up)
and "sea_levels" (real: Port Pirie, Coles 2001).
"""

from . import Entry

STATIONS = """
    df = sdata.get_example("stations")
    x = df["east"].to_numpy(dtype=float)
    y = df["north"].to_numpy(dtype=float)
    z = df["zinc"].to_numpy(dtype=float)
    direction = df["current_direction"].to_numpy(dtype=float)
    lon = df["lon"].to_numpy(dtype=float)
    lat = df["lat"].to_numpy(dtype=float)
"""
SEALEVEL = """
    df = sdata.get_example("sea_levels")
    x = df["sea_level"].to_numpy(dtype=float)
"""
RAIN = """
    df = sdata.get_example("rain")
    x = df["rain"].to_numpy(dtype=float)
"""
SPDEP_NOTE = ("PySAL's esda gives Moran's I in Python, but it is not a simplydata dependency (it brings geopandas, "
              "pyproj, shapely and scikit-learn), so the numbers come from R spdep, the reference of Bivand & Wong "
              "(2018).")
GSTAT_NOTE = ("scikit-gstat gives variograms in Python, but it is not a simplydata dependency and its bins and fitting "
              "differ from gstat's, so the numbers come from R gstat.")
EXTREMES_NOTE = ("SciPy fits the GEV (genextreme, with c = -xi) and the generalised Pareto curve, but gives no return "
                 "levels and no profile-likelihood intervals, so the numbers come from R extRemes.")
PROFILE = ("profile-likelihood intervals (Coles 2001, section 3.3.3): the normal approximation of return.level() is "
           "too narrow and too symmetric for long return periods; the search range starts at the normal interval "
           "(R extRemes needs one).")


ENTRIES = [
    # ------------------------------------------------------------------ AC01: circular summaries
    Entry(
        word="table.find_average_direction_of",
        data="stations",
        ours="""
            table = sdata.table(sdata.get_example("stations"))
            table.find_average_direction_of("current_direction", full_turn=360)
        """,
        code={"SciPy": """
            import numpy as np
            from scipy import stats
            df = sdata.get_example("stations")
            # find_average_direction_of("current_direction", full_turn=360)
            d = df["current_direction"].to_numpy(dtype=float)
            t = np.deg2rad(d)
            {"average direction": stats.circmean(d, high=360, low=0),                      # (1)
             "resultant length": stats.directional_stats(
                 np.column_stack([np.cos(t), np.sin(t)])).mean_resultant_length,
             "circular standard deviation": stats.circstd(d, high=360, low=0),            # (2)
             "circular variance": stats.circvar(d, high=360, low=0)}
        """},
        compare="result",
        fields=("average direction", "resultant length", "circular standard deviation", "circular variance"),
        tolerance=1e-9,
        choices=("the average from 0 up to the full turn; R circular::mean.circular gives the same direction from "
                 "-180 to 180.",
                 "the circular standard deviation sqrt(-2 ln R), in the units of the column, as R sd.circular (which "
                 "gives radians)."),
        also="simplydata also requires full_turn= (no default: radians read as degrees give a wrong answer without a "
             "word), reads values outside 0 to the full turn round the circle, and words the resultant length.",
    ),
    # ------------------------------------------------------------------ AC02: Rayleigh
    Entry(
        word="table.compare_shape_to", option='shape="even around the circle"',
        data="stations",
        ours="""
            table = sdata.table(sdata.get_example("stations"))
            table.compare_shape_to("current_direction", shape="even around the circle", full_turn=360)
        """,
        code={
            "R": """
                # compare_shape_to("current_direction", shape="even around the circle", full_turn=360)
                r <- circular::rayleigh.test(
                  circular::circular(direction, units = "degrees", template = "none"))   # (1)
                list(statistic = r$statistic, p = r$p.value)
            """,
            "Python": """
                {"statistic": statistic, "p-value": p}
            """,
        },
        r_inputs=STATIONS, r_packages=("circular",), compare="result", fields=("statistic", "p-value"),
        tolerance=1e-9,
        choices=("the units are always given to R circular, which reads plain numbers as radians without a word.",),
        python_note="SciPy has no Rayleigh test, so the p-value comes from R circular.",
        also="simplydata also refuses fewer than 5 directions and notes that directions at two opposite sides can look "
             "even to the Rayleigh test.",
    ),
    # ------------------------------------------------------------------ AC08: Moran's I
    Entry(
        word="table.find_autocorrelation_of", option="x=",
        data="stations",
        ours="""
            table = sdata.table(sdata.get_example("stations"))
            table.find_autocorrelation_of("zinc", x="east", y="north")
        """,
        code={
            "R": """
                # find_autocorrelation_of("zinc", x="east", y="north")
                pts <- sf::st_as_sf(data.frame(x = x, y = y), coords = c("x", "y"))
                nb <- spdep::dnearneigh(pts, 0, Inf)                                       # (1)
                lw <- spdep::nb2listwdist(nb, pts, type = "idw", alpha = 1, style = "W")  # (2)
                set.seed(1)
                m <- spdep::moran.mc(z, lw, nsim = 999)                                    # (3)
                t <- spdep::moran.test(z, lw)
                list(i = m$statistic, p = m$p.value, e = t$estimate[["Expectation"]])
            """,
            "Python": """
                {"Moran's I": i, "p-value": p, "value with no pattern": e}
            """,
        },
        r_inputs=STATIONS, r_packages=("spdep", "sf"), compare="result",
        fields=("Moran's I", "p-value", "value with no pattern"), tolerance=1e-9,
        choices=("every pair of places is a neighbour (all pairs, not a distance band).",
                 "weights 1 / distance, each row's weights summing to 1 (row-standardised): nearer pairs count more.",
                 "a permutation p-value from 999 shuffles after set.seed(1), one-sided (nearby places more alike), "
                 "spdep's default."),
        python_note=SPDEP_NOTE,
        also="simplydata also prints the weights in words, refuses two rows at one place (with the line that "
             "averages them), notes longitude and latitude without on_globe=True and gives the permutation floor.",
    ),
    Entry(
        word="table.find_autocorrelation_of", option="nearest=",
        data="stations",
        ours="""
            table = sdata.table(sdata.get_example("stations"))
            table.find_autocorrelation_of("zinc", x="east", y="north", nearest=6)
        """,
        code={
            "R": """
                # find_autocorrelation_of("zinc", x="east", y="north", nearest=6)
                pts <- sf::st_as_sf(data.frame(x = x, y = y), coords = c("x", "y"))
                nb <- spdep::knn2nb(spdep::knearneigh(pts, k = 6))                         # (1)
                lw <- spdep::nb2listw(nb, style = "W")
                set.seed(1)
                m <- spdep::moran.mc(z, lw, nsim = 999)
                list(i = m$statistic, p = m$p.value)
            """,
            "Python": """
                {"Moran's I": i, "p-value": p}
            """,
        },
        r_inputs=STATIONS, r_packages=("spdep", "sf"), compare="result", fields=("Moran's I", "p-value"),
        tolerance=1e-9,
        choices=("each place's k nearest places count alike, the others not at all, each row's weights summing to 1.",),
        python_note=SPDEP_NOTE,
        also="simplydata also says that the weights change Moran's I, so the report must name them.",
    ),
    Entry(
        word="table.find_autocorrelation_of", option="on_globe=",
        data="stations",
        ours="""
            table = sdata.table(sdata.get_example("stations"))
            table.find_autocorrelation_of("zinc", x="lon", y="lat", on_globe=True)
        """,
        code={
            "R": """
                # find_autocorrelation_of("zinc", x="lon", y="lat", on_globe=True)
                pts <- sf::st_as_sf(data.frame(x = lon, y = lat), coords = c("x", "y"),
                                    crs = 4326)                                            # (1)
                nb <- spdep::dnearneigh(pts, 0, Inf)
                lw <- spdep::nb2listwdist(nb, pts, type = "idw", alpha = 1, style = "W")
                set.seed(1)
                m <- spdep::moran.mc(z, lw, nsim = 999)
                list(i = m$statistic, p = m$p.value)
            """,
            "Python": """
                {"Moran's I": i, "p-value": p}
            """,
        },
        r_inputs=STATIONS, r_packages=("spdep", "sf"), compare="result", fields=("Moran's I", "p-value"),
        tolerance=1e-9,
        choices=("longitude and latitude as places on the earth (crs 4326): great-circle distances in km.",),
        python_note=SPDEP_NOTE,
        also="simplydata also refuses on_globe=True on columns beyond -180 to 180 and -90 to 90.",
    ),
    # ------------------------------------------------------------------ AC09: variogram
    Entry(
        word="table.find_variogram_of",
        data="stations",
        ours="""
            table = sdata.table(sdata.get_example("stations"))
            table.find_variogram_of("zinc", x="east", y="north")
        """,
        code={
            "R": """
                # find_variogram_of("zinc", x="east", y="north")
                v <- gstat::variogram(z ~ 1, locations = ~ x + y,
                                      data = data.frame(x = x, y = y, z = z))     # (1)
                f <- gstat::fit.variogram(v, gstat::vgm("Sph"))                  # (2)
                list(d = v$dist[1], g = v$gamma[1], nugget = f$psill[1], psill = f$psill[2], range = f$range[2])
            """,
            "Python": """
                {"distance": d, "semivariance": g, "nugget": nugget, "partial sill": psill, "range": range}
            """,
        },
        r_inputs=STATIONS, r_packages=("gstat", "sf"), compare="result",
        fields=("distance", "semivariance", "nugget", "partial sill", "range"), tolerance=1e-7,
        choices=("gstat's own bins: up to a third of the diagonal of the area, in 15 bins.",
                 "the spherical curve, fitted with gstat's own start values (vgm with no numbers) and its default "
                 "weighted least squares (fit.method = 7)."),
        python_note=GSTAT_NOTE,
        also="simplydata also says the range in words (for the exponential, Gaussian and Matern curves gstat's range is "
             "not where the curve levels off) and explains a fit that does not converge.",
    ),
    Entry(
        word="draw_variogram",
        data="stations",
        ours="""
            chart = sdata.chart(sdata.get_example("stations"))
            chart.draw_variogram("zinc", x="east", y="north")
        """,
        code={
            "R": """
                # draw_variogram("zinc", x="east", y="north")
                v <- gstat::variogram(z ~ 1, locations = ~ x + y, data = data.frame(x = x, y = y, z = z))
                f <- gstat::fit.variogram(v, gstat::vgm("Sph"))
                l <- gstat::variogramLine(f, maxdist = max(v$dist), n = 200)     # (1)
                list(dist = v$dist, gamma = v$gamma, line_dist = l$dist, line_gamma = l$gamma)
            """,
            "matplotlib": """
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.scatter(dist, gamma)
                ax.plot(line_dist, line_gamma)
                ax.set_xlabel("Distance (in the units of x and y)")
                ax.set_ylabel("Semivariance (half the average squared difference)")
            """,
        },
        r_inputs=STATIONS, r_packages=("gstat", "sf"), compare="chart", check=("dots", "lines", "labels"),
        tolerance=1e-7,
        choices=("the fitted curve at 200 distances up to the largest bin, from gstat::variogramLine.",),
        python_note=GSTAT_NOTE,
        also="simplydata also starts both axes at 0.",
    ),
    # ------------------------------------------------------------------ AB07: block maxima
    Entry(
        word="table.find_return_levels_of",
        data="sea_levels",
        ours="""
            table = sdata.table(sdata.get_example("sea_levels"))
            table.find_return_levels_of("sea_level", once_in=[100], sorted_by="year")
        """,
        code={
            "R": """
                # find_return_levels_of("sea_level", once_in=[100], sorted_by="year")
                f <- extRemes::fevd(x, type = "GEV", method = "MLE")                       # (1)
                rl <- extRemes::return.level(f, return.period = 100, do.ci = TRUE)
                w <- rl[3] - rl[1]
                p <- extRemes::ci.fevd(f, type = "return.level", return.period = 100,
                                       method = "proflik", xrange = c(rl[1], rl[3] + 2 * w),
                                       nint = 200)                                         # (2)
                list(level = rl[2], low = p[1], high = p[3])
            """,
            "Python": """
                {"level": level, "95 % CI low": low, "95 % CI high": high}
            """,
        },
        r_inputs=SEALEVEL, r_packages=("extRemes",), compare="result", fields=("level", "95 % CI low", "95 % CI high"),
        tolerance=1e-9,
        choices=("the GEV by maximum likelihood (extRemes's default method).", PROFILE),
        python_note=EXTREMES_NOTE,
        also="simplydata also refuses daily readings (each row must be one block, such as a year), says the shape in "
             "the extRemes sign (xi) with its interval, widens the search range when an interval touches its end, and "
             "says a 100-year level as a 1-in-100 chance in any one year.",
    ),
    Entry(
        word="table.find_return_levels_of", option="values_above=",
        data="rain",
        ours="""
            table = sdata.table(sdata.get_example("rain"))
            table.turn_into_dates("date")
            table.find_return_levels_of("rain", once_in=[10], values_above=20, sorted_by="date")
        """,
        code={
            "R": """
                # find_return_levels_of("rain", once_in=[10], values_above=20, sorted_by="date")
                f <- extRemes::fevd(x, threshold = 20, type = "GP", time.units = "days",  # (1)
                                    optim.args = list(method = "BFGS",
                                                      control = list(reltol = 1e-12,
                                                                     maxit = 10000)))   # (3)
                rl <- extRemes::return.level(f, return.period = 10, do.ci = TRUE)
                w <- rl[3] - rl[1]
                p <- extRemes::ci.fevd(f, type = "return.level", return.period = 10,
                                       method = "proflik", xrange = c(rl[1], rl[3] + 2 * w),
                                       nint = 200)                                         # (2)
                list(level = rl[2], low = p[1], high = p[3])
            """,
            "Python": """
                {"level": level, "95 % CI low": low, "95 % CI high": high}
            """,
        },
        r_inputs=RAIN, r_packages=("extRemes",), compare="result", fields=("level", "95 % CI low", "95 % CI high"),
        tolerance=1e-9,
        choices=("the readings per year from the dates: daily readings are time.units = \"days\" (365.25 a year).",
                 PROFILE,
                 "a tighter stopping rule for optim (reltol 1e-12) than its default, so that the fit has converged; "
                 "the method is the same."),
        python_note=EXTREMES_NOTE,
        also="simplydata also gives the extremal index (extRemes::extremalindex) and, below 0.7, says the values above "
             "come in runs; it does not decluster without asking.",
    ),
    Entry(
        word="draw_threshold_check",
        data="rain",
        ours="""
            chart = sdata.chart(sdata.get_example("rain"))
            chart.draw_threshold_check(x="rain", between=[10, 30])
        """,
        code={
            "R": """
                # draw_threshold_check(x="rain", between=[10, 30])
                m <- extRemes::mrlplot(x, nint = 100)                                        # (1)
                tr <- extRemes::threshrange.plot(x, r = c(10, 30), nint = 10, type = "GP")   # (2)
                list(mean = m[, 2], shape = tr[, "shape"])
            """,
            "matplotlib": """
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.set_axis_off()
                top = ax.inset_axes([0, 0.56, 1, 0.42])
                bottom = ax.inset_axes([0, 0, 1, 0.42], sharex=top)
            """,
        },
        r_inputs=RAIN, r_packages=("extRemes",), compare="chart", check=("panels",), tolerance=1e-9,
        choices=("the mean excess at extRemes::mrlplot's own 100 thresholds, drawn from the lowest to the highest "
                 "threshold asked for.",
                 "the shape at 10 thresholds from the lowest to the highest, as extRemes::threshrange.plot."),
        python_note="Python has no threshold check in SciPy or statsmodels, so the numbers come from R extRemes; "
                    "matplotlib draws them in two panels (the reliability study checks the numbers).",
        also="simplydata also refuses a highest threshold with fewer than 10 values above it.",
    ),
    # ------------------------------------------------------------------ the new distribution families
    Entry(
        word="table.fit_distribution_to", option='distribution="gev"',
        data="sea_levels",
        ours="""
            table = sdata.table(sdata.get_example("sea_levels"))
            table.fit_distribution_to("sea_level", distribution="gev").turn_into_table()
        """,
        code={
            "R": """
                # fit_distribution_to("sea_level", distribution="gev")
                f <- extRemes::fevd(x, type = "GEV", method = "MLE",   # (1)
                                    optim.args = list(method = "BFGS", control = list(reltol = 1e-14, maxit = 1e5)))
                p <- f$results$par
                list(location = p[["location"]], scale = p[["scale"]], shape = p[["shape"]])
            """,
            "Python": """
                {"location": location, "scale": scale, "shape": shape}
            """,
        },
        r_inputs=SEALEVEL, r_packages=("extRemes",), compare="result", fields=("location", "scale", "shape"),
        # SciPy fit + polish against extRemes run to reltol 1e-14: two optimisers, both converged, agree to 1e-7
        tolerance=1e-6,
        choices=("the shape kept in the sign of extRemes and Coles (xi); SciPy's genextreme, which simplydata uses for "
                 "the numbers, takes c = -xi.",),
        python_note="simplydata fits it with SciPy (genextreme.fit, then a numerical polish of the likelihood); "
                    "R extRemes is the check.",
        also="simplydata also accepts \"generalised pareto\" (\"generalized pareto\", \"gpd\") for the amounts above a "
             "threshold, with the same sign as SciPy's genpareto.",
    ),
    Entry(
        word="table.fit_distribution_to", option='distribution="generalised pareto"',
        data="rain",
        ours="""
            table = sdata.table(sdata.get_example("rain"))
            table.keep_rows_where("rain > 20")
            table.add_column("excess", "rain - 20")
            table.fit_distribution_to("excess", distribution="generalised pareto").turn_into_table()
        """,
        code={
            "R": """
                # fit_distribution_to("excess", distribution="generalised pareto") on the rain above 20
                f <- extRemes::fevd(x, threshold = 20, type = "GP", method = "MLE",   # (1)
                                    optim.args = list(method = "BFGS", control = list(reltol = 1e-14, maxit = 1e5)))
                p <- f$results$par
                list(scale = p[["scale"]], shape = p[["shape"]])
            """,
            "Python": """
                {"scale": scale, "shape": shape}
            """,
        },
        r_inputs=RAIN, r_packages=("extRemes",), compare="result", fields=("scale", "shape"), tolerance=1e-5,
        # SciPy genpareto + polish against extRemes run to reltol 1e-14: two optimisers, both converged, agree to 1e-6
        choices=("the shape in the sign of extRemes, Coles and SciPy's genpareto (xi), with the threshold at 0: the "
                 "values are the amounts above a threshold.",),
        python_note="simplydata fits it with SciPy (genpareto.fit with loc = 0, then a numerical polish of the "
                    "likelihood); R extRemes is the check.",
        also="simplydata also names the classical \"pareto\" as another family in both printouts.",
    ),
]
