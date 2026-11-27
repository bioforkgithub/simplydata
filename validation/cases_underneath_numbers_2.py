"""Real-data cases for the NumPy + SciPy phase, batch 2 (approved by Manish 2026-11-25): netCDF files, labels, dates
and places on blocks, smoothing grids and blocks, chances, random picks and counting. cases_underneath.py loads this
file and adds cases(Case) to the study.

The data are the study's own: the El Nino sea surface temperatures (NOAA, 732 months, 1950-2010; as a series with
dates and as a grid of 61 years x 12 months), the AirPassengers series (12 years x 12 months, labelled by year and
month), Fisher's iris data, Michelson's speed-of-light measurements (NIST) and the Lake Huron levels. Each case is
compared with the parent package doing the same job directly (xarray, SciPy, NumPy or pandas) and, where base R has
the same calculation, with R. The netCDF cases write a small netCDF file from El Nino inside the case and read it
back: nothing is downloaded.

simplydata's side reads its results with simplydata words (get_all_numbers, get_labels_of ...); the other sides
flatten in the same order (the last direction fastest), so every number is compared, not only a summary.

sdata.show_whats_inside has nothing underneath to compare (it prints what a file holds), so it has no case.
"""

from __future__ import annotations

import textwrap

R_FLAT = ("flat <- function(x) { v <- if (is.null(dim(x))) as.vector(x) else as.vector(aperm(x)); "
          "setNames(as.list(as.numeric(v)), as.character(seq_along(v) - 1)) }\n")
NP_FLAT = "{str(i): float(v) for i, v in enumerate(np.ravel(x))}"

# El Nino as a series with dates (732 months)
NINO_OURS = """
    dates = sdata.make_run_of_dates("1950-01", how_many=732, every="month")
    block = sdata.number_block(data["temperature"].tolist(), directions_named=["time"], with_labels={"time": dates})
"""
NINO_XR = """
    import numpy as np, pandas as pd, xarray as xr
    sst = xr.DataArray(data["temperature"].to_numpy(), dims=["time"],
                       coords={"time": pd.date_range("1950-01-01", periods=732, freq="MS")})
"""
R_NINO = R_FLAT + "mo <- ((month - 1) %% 12) + 1\n"

# El Nino as a grid: 61 years x 12 months, labelled by year and month
NINO_GRID_OURS = """
    rows = sdata.number_block(data["temperature"].tolist()).change_shape_to(61, 12)
    block = sdata.number_block(rows, directions_named=["year", "month"],
                               with_labels={"year": list(range(1950, 2011)), "month": list(range(1, 13))})
"""
NINO_GRID_NP = """
    import numpy as np
    m = data["temperature"].to_numpy().reshape(61, 12)
"""
R_NINO_GRID = R_FLAT + "m <- matrix(temperature, nrow = 61, byrow = TRUE)\n"

# AirPassengers: 12 years x 12 months, labelled by year and month
AIR_OURS = """
    rows = sdata.number_block(data["passengers"].astype(float).tolist()).change_shape_to(12, 12)
    block = sdata.number_block(rows, directions_named=["year", "month"],
                               with_labels={"year": list(range(1949, 1961)), "month": list(range(1, 13))})
"""
AIR_NP = """
    import numpy as np
    m = data["passengers"].to_numpy(dtype=float).reshape(12, 12)
    years, months = np.arange(1949, 1961), np.arange(1, 13)
"""
R_AIR = R_FLAT + "m <- matrix(as.numeric(passengers), nrow = 12, byrow = TRUE)\n"


def _code(*parts: str) -> str:
    return "\n".join(textwrap.dedent(p).strip("\n") for p in parts) + "\n"


def _ours_flat(result: str) -> str:
    return f"{{str(i): v for i, v in enumerate({result})}}"


def cases(Case):
    nino = dict(dataset="El Nino sea surface temperatures", kind="real data")
    air = dict(dataset="AirPassengers", kind="real data")
    iris = dict(dataset="iris", kind="real data")
    huron = dict(dataset="Lake Huron", kind="real data")

    return [
        # ---------------------------------------------------------------- netCDF files (written and read back here)
        Case("block.save", "El Nino: 732 months with their dates saved as netCDF and read back", **nino,
             ours=_code(NINO_OURS, """
                 import os, shutil, tempfile
                 folder = tempfile.mkdtemp()
                 path = os.path.join(folder, "nino.nc")
                 block.save(path)
                 again = sdata.number_block(path, values="values")
                 shutil.rmtree(folder)
             """, _ours_flat("again.get_all_numbers()")),
             parent=_code(NINO_XR, """
                 import os, shutil, tempfile
                 folder = tempfile.mkdtemp()
                 path = os.path.join(folder, "nino.nc")
                 sst.rename("values").to_netcdf(path, engine="h5netcdf", encoding={"values": {"zlib": True}})
                 with xr.open_dataset(path, engine="h5netcdf") as ds:
                     x = ds["values"].values
                 shutil.rmtree(folder)
             """, NP_FLAT), parent_label="xarray to_netcdf and open_dataset (h5netcdf)", parent_tolerance=0.0,
             r=R_FLAT + "flat(temperature)", r_tolerance=0.0),
        Case("sdata.number_block", "El Nino in a netCDF file: the years 2000-2009 cut in the file, then read",
             **nino, option="keep_on_disk=",
             ours=_code(NINO_OURS, """
                 import os, shutil, tempfile
                 folder = tempfile.mkdtemp()
                 path = os.path.join(folder, "nino.nc")
                 block.save(path)
                 lazy = sdata.number_block(path, values="values", keep_on_disk=True)
                 lazy.keep_where("time", is_between=["2000-01-01", "2009-12-01"])
                 kept = lazy.get_all_numbers()
                 shutil.rmtree(folder)
             """, _ours_flat("kept")),
             parent=_code(NINO_XR, """
                 import os, shutil, tempfile
                 folder = tempfile.mkdtemp()
                 path = os.path.join(folder, "nino.nc")
                 sst.rename("values").to_netcdf(path, engine="h5netcdf")
                 with xr.open_dataset(path, engine="h5netcdf") as ds:
                     x = ds["values"].sel(time=slice("2000-01-01", "2009-12-01")).values
                 shutil.rmtree(folder)
             """, NP_FLAT), parent_label="xarray open_dataset and sel", parent_tolerance=0.0,
             r=R_FLAT + "flat(temperature[year >= 2000 & year <= 2009])", r_tolerance=0.0),
        # ---------------------------------------------------------------- labels
        Case("block.get_labels_of", "AirPassengers: the years along the first direction", **air,
             ours=_code(AIR_OURS, _ours_flat('block.get_labels_of("year")')),
             parent=_code(AIR_NP, "x = years", NP_FLAT), parent_label="NumPy arange (the labels given)",
             parent_tolerance=0.0, r=R_AIR + "flat(1949:1960)", r_tolerance=0.0),
        Case("block.add_labels_to", "El Nino: each month labelled by its decimal year (1950, 1950.083 ...)", **nino,
             ours=_code(NINO_GRID_OURS, """
                 series = sdata.number_block(data["temperature"].tolist(), directions_named=["time"])
                 series.add_labels_to("time", (data["year"] + (data["month"] - 1) % 12 / 12).tolist())
             """, _ours_flat('series.get_labels_of("time")')),
             parent=_code(NINO_XR, """
                 sst = sst.assign_coords(time=(data["year"] + (data["month"] - 1) % 12 / 12).to_numpy())
                 x = sst.coords["time"].values
             """, NP_FLAT), parent_label="xarray assign_coords", parent_tolerance=1e-15,
             r=R_NINO + "flat(year + (mo - 1) / 12)", r_tolerance=1e-12),
        # ---------------------------------------------------------------- summaries by dates and in groups
        Case("block.find_average", "El Nino: the usual temperature of each month of the year (1950-2010)", **nino,
             option='in_each="month"',
             ours=_code(NINO_OURS, _ours_flat('block.find_average(in_each="month").get_all_numbers()')),
             parent=_code(NINO_XR, 'x = sst.groupby("time.month").mean().values', NP_FLAT),
             parent_label='xarray groupby("time.month").mean()', parent_tolerance=1e-12,
             r=R_NINO + "flat(tapply(temperature, mo, mean))", r_tolerance=1e-12),
        Case("block.find_average", "El Nino: the average of each calendar quarter (244 quarters)", **nino,
             option="every=",
             ours=_code(NINO_OURS, _ours_flat('block.find_average(every="quarter").get_all_numbers()')),
             parent=_code(NINO_XR, 'x = sst.resample(time="QS").mean().values', NP_FLAT),
             parent_label='xarray resample(time="QS").mean()', parent_tolerance=1e-12,
             r=R_NINO + "flat(tapply(temperature, (year - 1950) * 4 + (mo - 1) %/% 3, mean))", r_tolerance=1e-12),
        Case("block.find_average", "El Nino grid: the average of each 3 months of each year (61 years x 4)", **nino,
             option="in_groups_of=",
             ours=_code(NINO_GRID_OURS, _ours_flat('block.find_average(in_groups_of={"month": 3}).get_all_numbers()')),
             parent=_code(NINO_GRID_NP, """
                 import xarray as xr
                 x = xr.DataArray(m, dims=["year", "month"]).coarsen(month=3, boundary="exact").mean().values
             """, NP_FLAT), parent_label='xarray coarsen(month=3, boundary="exact").mean()', parent_tolerance=1e-12,
             r=R_NINO_GRID + "flat(t(apply(m, 1, function(r) tapply(r, rep(1:4, each = 3), mean))))",
             r_tolerance=1e-12),
        # ---------------------------------------------------------------- anomalies
        Case("block.turn_into_change_from_average", "El Nino: each month minus the usual value of its month", **nino,
             ours=_code(NINO_OURS, 'block.turn_into_change_from_average(in_each="month")',
                        _ours_flat("block.get_all_numbers()")),
             parent=_code(NINO_XR, 'x = (sst.groupby("time.month") - sst.groupby("time.month").mean()).values',
                          NP_FLAT), parent_label="xarray groupby minus its mean", parent_tolerance=1e-12,
             r=R_NINO + "flat(temperature - ave(temperature, mo))", r_tolerance=1e-12),
        Case("block.turn_into_change_from_average", "El Nino: anomalies against the usual values of 1981-2010", **nino,
             option="from_years=",
             ours=_code(NINO_OURS, 'block.turn_into_change_from_average(in_each="month", from_years=["1981", "2010"])',
                        _ours_flat("block.get_all_numbers()")),
             parent=_code(NINO_XR, """
                 usual = sst.sel(time=slice("1981", "2010")).groupby("time.month").mean()
                 x = (sst.groupby("time.month") - usual).values
             """, NP_FLAT), parent_label="xarray sel, groupby and mean", parent_tolerance=1e-12,
             r=R_NINO + "base <- tapply(temperature[year >= 1981 & year <= 2010], mo[year >= 1981 & year <= 2010], mean)"
                        "\nflat(temperature - base[mo])", r_tolerance=1e-12),
        # ---------------------------------------------------------------- places
        Case("block.find_values_at", "AirPassengers: passengers between the labels (year 1950.5, months 2.5 and 6.25)",
             **air,
             ours=_code(AIR_OURS, _ours_flat("block.find_values_at(year=1950.5, month=[2.5, 6.25]).get_all_numbers()")),
             parent=_code(AIR_NP, """
                 from scipy.interpolate import interpn
                 where = np.array([[1950.5, 2.5], [1950.5, 6.25]])
                 x = interpn((years, months), m, where, method="linear")
             """, NP_FLAT), parent_label="SciPy interpolate.interpn (linear)", parent_tolerance=1e-12,
             r=R_AIR + "a <- approx(1:12, m[2, ], c(2.5, 6.25))$y; b <- approx(1:12, m[3, ], c(2.5, 6.25))$y\n"
                       "flat((a + b) / 2)", r_tolerance=1e-12),
        Case("block.get_numbers_nearest_to", "AirPassengers: the months of the year nearest to 1953.4", **air,
             ours=_code(AIR_OURS, _ours_flat("block.get_numbers_nearest_to(year=1953.4).get_all_numbers()")),
             parent=_code(AIR_NP, """
                 import xarray as xr
                 x = xr.DataArray(m, dims=["year", "month"], coords={"year": years}).sel(year=1953.4,
                                                                                        method="nearest").values
             """, NP_FLAT), parent_label='xarray sel(method="nearest")', parent_tolerance=0.0,
             r=R_AIR + "flat(m[which.min(abs(1949:1960 - 1953.4)), ])", r_tolerance=0.0),
        # ---------------------------------------------------------------- smoothing, size and turning
        Case("block.smooth", "El Nino grid: the average of each 3 x 3 neighbourhood of years and months", **nino,
             ours=_code(NINO_GRID_OURS, """
                 block.smooth(over=["year", "month"], window=3)
                 block.keep_by_position_in("year", 2, to=60).keep_by_position_in("month", 2, to=11)
             """, _ours_flat("block.get_all_numbers()")),
             parent=_code(NINO_GRID_NP, """
                 from scipy import ndimage
                 x = ndimage.uniform_filter(m, size=3, mode="reflect")[1:-1, 1:-1]
             """, NP_FLAT), parent_label="SciPy ndimage.uniform_filter", parent_tolerance=1e-12,
             r=R_NINO_GRID + "f <- function(v) as.numeric(stats::filter(v, rep(1 / 3, 3), sides = 2))\n"
                             "s <- apply(t(apply(m, 1, f)), 2, f)\nflat(s[2:60, 2:11])", r_tolerance=1e-12),
        Case("grid.smooth", "AirPassengers grid blurred by a bell curve (standard deviation 1 place)", **air,
             ours=_code("""
                 grid = sdata.number_grid(data["passengers"].astype(float).to_numpy().reshape(12, 12).tolist())
                 grid.smooth(test_method="gaussian", width=1)
             """, _ours_flat("grid.get_all_numbers()")),
             parent=_code(AIR_NP, """
                 from scipy import ndimage
                 x = ndimage.gaussian_filter(m, sigma=1, truncate=4.0, mode="reflect")
             """, NP_FLAT), parent_label="SciPy ndimage.gaussian_filter", parent_tolerance=1e-12),
        Case("block.change_size_to", "El Nino grid filled in to 121 years x 23 months (linear)", **nino,
             ours=_code(NINO_GRID_OURS, 'block.change_size_to(year=121, month=23)',
                        _ours_flat("block.get_all_numbers()")),
             parent=_code(NINO_GRID_NP, """
                 from scipy import ndimage
                 x = ndimage.zoom(m, (121 / 61, 23 / 12), order=1)
             """, NP_FLAT), parent_label="SciPy ndimage.zoom (order 1)", parent_tolerance=1e-12,
             r=R_NINO_GRID + "flat(t(apply(apply(m, 2, function(v) approx(1:61, v, n = 121)$y), 1, "
                             "function(v) approx(1:12, v, n = 23)$y)))", r_tolerance=1e-12),
        Case("block.rotate", "AirPassengers grid turned by 30 degrees round its centre", **air, option="by_degrees=",
             ours=_code(AIR_OURS, """
                 block.rotate(by_degrees=30)
                 block.replace_each_number_that(is_empty=True, with_value=-1)
             """, _ours_flat("block.get_all_numbers()")),
             parent=_code(AIR_NP, """
                 from scipy import ndimage
                 x = ndimage.rotate(m, 30, reshape=False, order=1, mode="constant", cval=np.nan)
                 x = np.where(np.isnan(x), -1, x)
             """, NP_FLAT), parent_label="SciPy ndimage.rotate (reshape=False, order 1)", parent_tolerance=1e-12),
        # ---------------------------------------------------------------- numbers
        Case("nums.make_random_picks", "Michelson: a bootstrap sample of the 100 measurements (seed 2026)",
             "NIST Michelso", "real data",
             ours=_code('picks = sdata.number_list(data["y"].tolist()).make_random_picks(how_many=100, with_seed=2026)',
                        _ours_flat("picks")),
             parent=_code("""
                 import numpy as np
                 x = np.random.default_rng(2026).choice(data["y"].to_numpy(), size=100, replace=True)
             """, NP_FLAT), parent_label="NumPy random.default_rng(2026).choice", parent_tolerance=0.0),
        Case("nums.take_log_odds", "iris: the log-odds of each flower's sepal width as a share of its length",
             **iris,
             ours=_code("""
                 share = sdata.number_list((data["Sepal.Width"] / data["Sepal.Length"]).tolist()).take_log_odds()
             """, _ours_flat("share")),
             parent=_code("""
                 import numpy as np
                 from scipy import special
                 x = special.logit((data["Sepal.Width"] / data["Sepal.Length"]).to_numpy())
             """, NP_FLAT), parent_label="SciPy special.logit", parent_tolerance=1e-14,
             r=R_FLAT + "flat(qlogis(Sepal.Width / Sepal.Length))", r_tolerance=1e-12),
        Case("nums.turn_into_chances", "Lake Huron: the levels around their average turned into chances", **huron,
             ours=_code("""
                 levels = sdata.number_list(data["level"].tolist())
                 levels.subtract(levels.find_average()).turn_into_chances()
             """, _ours_flat("levels")),
             parent=_code("""
                 import numpy as np
                 from scipy import special
                 x = special.expit(data["level"].to_numpy() - data["level"].to_numpy().mean())
             """, NP_FLAT), parent_label="SciPy special.expit", parent_tolerance=1e-14,
             r=R_FLAT + "flat(plogis(level - mean(level)))", r_tolerance=1e-12),
        Case("sdata.count_ways_to_choose", "iris: the ways to choose 3 of the 150 flowers", **iris,
             ours="""
                 {"ways": sdata.count_ways_to_choose(3, out_of=len(data))}
             """,
             parent="""
                 from scipy import special
                 {"ways": special.comb(len(data), 3, exact=True)}
             """, parent_label="SciPy special.comb(exact=True)", parent_tolerance=0.0,
             r="list(ways = choose(length(Species), 3))", r_tolerance=0.0),
        Case("sdata.count_ways_to_order", "iris: the ways to pick 3 of the 150 flowers in order", **iris,
             ours="""
                 {"ways": sdata.count_ways_to_order(3, out_of=len(data))}
             """,
             parent="""
                 from scipy import special
                 {"ways": special.perm(len(data), 3, exact=True)}
             """, parent_label="SciPy special.perm(exact=True)", parent_tolerance=0.0,
             r="list(ways = choose(length(Species), 3) * factorial(3))", r_tolerance=0.0),
        Case("sdata.number_list", "Lake Huron levels in a text file with every tenth reading marked -999", **huron,
             option="empty_values=",
             ours=_code("""
                 import os, shutil, tempfile
                 folder = tempfile.mkdtemp()
                 path = os.path.join(folder, "huron.txt")
                 marked = [-999 if i % 10 == 9 else v for i, v in enumerate(data["level"].tolist())]
                 with open(path, "w") as f:
                     f.write("\\n".join(str(v) for v in marked))
                 levels = sdata.number_list(path, empty_values=[-999]).remove_empty_numbers()
                 shutil.rmtree(folder)
             """, _ours_flat("levels")),
             parent=_code("""
                 import os, shutil, tempfile
                 import numpy as np, pandas as pd
                 folder = tempfile.mkdtemp()
                 path = os.path.join(folder, "huron.txt")
                 marked = [-999 if i % 10 == 9 else v for i, v in enumerate(data["level"].tolist())]
                 with open(path, "w") as f:
                     f.write("\\n".join(str(v) for v in marked))
                 x = pd.read_csv(path, header=None, sep=r"\\s+", na_values=[-999]).iloc[:, 0].dropna().to_numpy()
                 shutil.rmtree(folder)
             """, NP_FLAT), parent_label="pandas read_csv(na_values=[-999])", parent_tolerance=0.0,
             r=R_FLAT + "flat(level[seq_along(level) %% 10 != 0])", r_tolerance=0.0),
        Case("sdata.make_random_numbers", "iris-sized block of 3 x 50 x 4 bell-shaped numbers with the iris average",
             **iris, option="of_shape=",
             ours=_code("""
                 m = sdata.number_list(data["Sepal.Length"].tolist()).find_average()
                 block = sdata.make_random_numbers(of_shape=(3, 50, 4), average=m, standard_deviation=1, with_seed=7)
             """, _ours_flat("block.get_all_numbers()")),
             parent=_code("""
                 import numpy as np
                 x = np.random.default_rng(7).normal(data["Sepal.Length"].mean(), 1, (3, 50, 4))
             """, NP_FLAT), parent_label="NumPy random.default_rng(7).normal", parent_tolerance=1e-12),
    ]
