"""The NumPy + SciPy phase, batch 2 (approved by Manish 2026-11-25): netCDF files, labels, dates and places on blocks,
smoothing grids and blocks, chances, random picks and counting. The same job in xarray, SciPy, NumPy or pandas."""

from . import Entry


def _e(word, ours, code, also, tolerance=1e-12, choices=(), option="", compare="value"):
    return Entry(word=word, ours=ours, code=code, compare=compare, tolerance=tolerance, also=also, choices=choices,
                 option=option)


# a small block with dates: 24 months x 3 latitudes x 4 longitudes
_SEA_OURS = """
            import numpy as np
            values = np.arange(24 * 3 * 4, dtype=float).reshape(24, 3, 4) % 17
            dates = sdata.make_run_of_dates("2010-01", how_many=24, every="month")
            block = sdata.number_block(values, directions_named=["time", "latitude", "longitude"],
                                       with_labels={"time": dates, "latitude": [62, 61, 60], "longitude": [1, 2, 3, 4]})
"""
_SEA_XR = """
            import numpy as np, pandas as pd, xarray as xr
            values = np.arange(24 * 3 * 4, dtype=float).reshape(24, 3, 4) % 17
            sst = xr.DataArray(values, dims=["time", "latitude", "longitude"], coords={
                "time": pd.date_range("2010-01-01", periods=24, freq="MS"), "latitude": [62, 61, 60],
                "longitude": [1, 2, 3, 4]})
"""


def _sea(code: str) -> str:
    return _SEA_XR.rstrip("\n") + "\n" + code


def _ours(code: str) -> str:
    return _SEA_OURS.rstrip("\n") + "\n" + code


ENTRIES = [
    # ---- files
    Entry(word="sdata.show_whats_inside", ours="""
            import os, tempfile
            path = os.path.join(tempfile.mkdtemp(), "plate.nc")
            sdata.number_block(of_shape=(2, 3), filled_with=1.5).save(path)
            sdata.show_whats_inside(path)
        """, compare="none",
          note="It only reads and prints what a file holds: for a netCDF file the names, directions, sizes, units and "
               "labels that xarray's open_dataset(path) reads without loading the numbers (print(ds) shows the same "
               "facts); for .npz and .npy NumPy's np.lib.format header readers; for .xlsx openpyxl's sheet sizes. "
               "Nothing is worked out."),
    _e("block.save", _ours("""
            import os, tempfile
            path = os.path.join(tempfile.mkdtemp(), "sst.nc")
            block.save(path)
            sdata.number_block(path, values="values").get_all_numbers()
        """), {"xarray": _sea("""
            import os, tempfile
            path = os.path.join(tempfile.mkdtemp(), "sst.nc")
            # block.save("sst.nc")
            sst.rename("values").to_netcdf(path, engine="h5netcdf", encoding={"values": {"zlib": True}})  # (1)
            xr.open_dataset(path, engine="h5netcdf")["values"].values.ravel()
        """)}, "The names of the directions and their labels go into the file; a block read from a netCDF file also "
               "keeps its variable name and units. Web addresses are refused.",
       choices=("netCDF-4 with the h5netcdf engine, every variable compressed (zlib, level 4); the numbers come back "
                "exactly.",)),
    _e("sdata.number_block", """
            import os, tempfile
            import numpy as np
            path = os.path.join(tempfile.mkdtemp(), "plate.nc")
            sdata.number_block(np.arange(12.0).reshape(3, 4), directions_named=["row", "column"]).save(path)
            block = sdata.number_block(path, values="values", keep_on_disk=True)
            block.keep_by_position_in("row", 2).get_all_numbers()
        """, {"xarray": """
            import os, tempfile
            import numpy as np, xarray as xr
            path = os.path.join(tempfile.mkdtemp(), "plate.nc")
            xr.DataArray(np.arange(12.0).reshape(3, 4), dims=["row", "column"], name="values").to_netcdf(path, engine="h5netcdf")
            # number_block("plate.nc", values="values", keep_on_disk=True)
            lazy = xr.open_dataset(path, engine="h5netcdf")["values"]  # (1)
            lazy.isel(row=[1]).values.ravel()
        """}, "Only the part kept is read from the file; any other word reads the numbers once, with a note.",
       option="keep_on_disk=",
       choices=("the file stays open and only its labels are read; xarray isel cuts it in the file.",)),
    # ---- labels, dates and places
    _e("block.get_labels_of", _ours("""
            block.get_labels_of("latitude")
        """), {"xarray": _sea("""
            # block.get_labels_of("latitude")
            sst.coords["latitude"].values
        """)}, "Dates and text come back as a table with one column named after the direction."),
    _e("block.add_labels_to", _ours("""
            block.add_labels_to("latitude", [60.5, 61.5, 62.5])
            block.get_labels_of("latitude")
        """), {"xarray": _sea("""
            # block.add_labels_to("latitude", [60.5, 61.5, 62.5])
            sst = sst.assign_coords(latitude=[60.5, 61.5, 62.5])
            sst.coords["latitude"].values
        """)}, "One label for each position, all different; undo() takes them back."),
    _e("block.find_values_at", _ours("""
            block.find_values_at(latitude=60.5, longitude=[1.5, 2.25])
        """), {"SciPy": _sea("""
            from scipy.interpolate import interpn
            # block.find_values_at(latitude=60.5, longitude=[1.5, 2.25])
            moved = np.moveaxis(values, [1, 2], [0, 1])
            where = np.stack(np.meshgrid([60.5], [1.5, 2.25], indexing="ij"), axis=-1)
            out = interpn(([62, 61, 60], [1, 2, 3, 4]), moved, where, bounds_error=False, fill_value=np.nan)  # (1)
            np.moveaxis(out, [0, 1], [1, 2])[:, 0, :]
        """), "xarray": _sea("""
            # block.find_values_at(latitude=60.5, longitude=[1.5, 2.25])
            sst.interp(latitude=60.5, longitude=[1.5, 2.25]).values
        """)}, "A single label removes that direction; a list gives it the new labels. Dates as labels go through "
               "xarray interp.",
       choices=('straight lines between the neighbours (test_method="linear"); places outside the labels are empty.',)),
    _e("block.get_numbers_nearest_to", _ours("""
            block.get_numbers_nearest_to(latitude=60.4, longitude=3.7)
        """), {"xarray": _sea("""
            # block.get_numbers_nearest_to(latitude=60.4, longitude=3.7)
            sst.sel(latitude=60.4, longitude=3.7, method="nearest").values
        """)}, "The sentence names the labels found; within= refuses a label further away (xarray tolerance=)."),
    _e("block.turn_into_change_from_average", _ours("""
            block.turn_into_change_from_average(in_each="month")
        """), {"xarray": _sea("""
            # block.turn_into_change_from_average(in_each="month")
            usual = sst.groupby("time.month").mean()
            (sst.groupby("time.month") - usual).values
        """)}, "over= a direction subtracts the average along it instead (NumPy nanmean with keepdims=True). The "
               "step can be undone."),
    _e("block.turn_into_change_from_average", _ours("""
            block.turn_into_change_from_average(in_each="month", from_years=["2011", "2011"])
        """), {"xarray": _sea("""
            # block.turn_into_change_from_average(in_each="month", from_years=["2011", "2011"])
            usual = sst.sel(time=slice("2011", "2011")).groupby("time.month").mean()
            (sst.groupby("time.month") - usual).values
        """)}, "A month the years do not cover is refused, so no anomaly is left without its usual value.",
       option="from_years="),
    _e("block.smooth", _ours("""
            block.smooth(over=["latitude", "longitude"], window=3)
        """), {"SciPy": _sea("""
            from scipy import ndimage
            # block.smooth(over=["latitude", "longitude"], window=3)
            out = ndimage.uniform_filter(values, size=3, mode="reflect", axes=(1, 2))
            out[:, [0, -1], :] = np.nan  # (1)
            out[:, :, [0, -1]] = np.nan
            out
        """)}, 'test_method="gaussian" (ndimage.gaussian_filter, width=) and "median" (ndimage.median_filter) work the '
               "same way along the directions named.",
       choices=('ends="empty": the places without a full window are left empty, as numbers.smooth; ends="reflect" and '
                "\"mirror\" keep SciPy's edges of those names.",)),
    _e("grid.smooth", """
            grid = sdata.number_grid([[1.0, 4, 2, 8, 5], [3, 9, 7, 1, 6], [2, 2, 8, 4, 3], [6, 5, 1, 9, 2]])
            grid.smooth(test_method="gaussian", width=1)
        """, {"SciPy": """
            import numpy as np
            from scipy import ndimage
            grid = np.array([[1.0, 4, 2, 8, 5], [3, 9, 7, 1, 6], [2, 2, 8, 4, 3], [6, 5, 1, 9, 2]])
            # grid.smooth(test_method="gaussian", width=1)
            ndimage.gaussian_filter(grid, sigma=1, truncate=4.0, mode="reflect", axes=(0, 1))  # (1)
        """}, "Without over= a grid is smoothed along its rows and its columns, as a picture is blurred.",
       choices=('the bell curve is cut at 4 standard deviations and the edge number is repeated (mode "reflect"), '
                "SciPy's own defaults.",)),
    _e("block.change_size_to", _ours("""
            block.change_size_to(latitude=5, longitude=7)
        """), {"SciPy": _sea("""
            from scipy import ndimage
            # block.change_size_to(latitude=5, longitude=7)
            ndimage.zoom(values, (1, 5 / 3, 7 / 4), order=1)  # (1)
        """)}, "Number labels are filled in the same way, so they stay with their numbers.",
       choices=('test_method="linear" (spline order 1); "nearest" is order 0 and "cubic" order 3.',)),
    _e("block.rotate", _ours("""
            block.rotate(by_degrees=30, over=["latitude", "longitude"])
        """), {"SciPy": _sea("""
            from scipy import ndimage
            # block.rotate(by_degrees=30, over=["latitude", "longitude"])
            ndimage.rotate(values, 30, axes=(2, 1), reshape=False, order=1, mode="constant", cval=np.nan)  # (1)
        """)}, "The size and labels stay; by_quarter_turns= turns by quarter turns without filling in (np.rot90).",
       option="by_degrees=",
       choices=("the corners that come from outside are empty (cval=nan), and the size is kept (reshape=False).",)),
    # ---- summaries by dates and in groups
    _e("block.find_average", _ours("""
            block.find_average(in_each="month")
        """), {"xarray": _sea("""
            # block.find_average(in_each="month")
            sst.groupby("time.month").mean().values
        """)}, '"season", "year", "quarter", "day of year" and "hour" group the same way; empty values are skipped.',
       option='in_each="month"'),
    _e("block.find_average", _ours("""
            block.find_average(every="quarter")
        """), {"xarray": _sea("""
            # block.find_average(every="quarter")
            sst.resample(time="QS").mean().values
        """)}, '"hour", "day", "week" (from Monday), "month" and "year" are the other steps, as table.find_average_of '
               "every=.", option="every="),
    _e("block.find_average", _ours("""
            block.find_average(in_groups_of={"longitude": 2})
        """), {"NumPy": _sea("""
            # block.find_average(in_groups_of={"longitude": 2})
            np.nanmean(values.reshape(24, 3, 2, 2), axis=3)
        """), "xarray": _sea("""
            # block.find_average(in_groups_of={"longitude": 2})
            sst.coarsen(longitude=2, boundary="exact").mean().values
        """)}, "The labels of the groups are their average label (xarray coarsen does the same).",
       option="in_groups_of="),
    # ---- numbers
    _e("nums.make_random_picks", """
            numbers = sdata.number_list([4.2, 5.1, 3.8, 6.0, 4.9])
            numbers.make_random_picks(how_many=8, with_chances=[0.1, 0.2, 0.3, 0.2, 0.2], with_seed=3)
        """, {"NumPy": """
            import numpy as np
            values = np.array([4.2, 5.1, 3.8, 6.0, 4.9])
            # make_random_picks(how_many=8, with_chances=[0.1, 0.2, 0.3, 0.2, 0.2], with_seed=3)
            rng = np.random.default_rng(3)
            rng.choice(values, size=8, replace=True, p=[0.1, 0.2, 0.3, 0.2, 0.2])  # (1)
        """}, "with_chances= must add up to 1, as NumPy asks; putting_back=False picks each number at most once.",
       choices=("putting each pick back is the default, as NumPy's choice and a bootstrap sample.",)),
    _e("nums.take_log_odds", """
            numbers = sdata.number_list([0.1, 0.5, 0.8, 0.0])
            numbers.take_log_odds()
        """, {"SciPy": """
            import numpy as np
            from scipy import special
            values = np.array([0.1, 0.5, 0.8, 0.0])
            # take_log_odds()
            np.where((values <= 0) | (values >= 1), np.nan, special.logit(values))  # (1)
        """}, "turn_into_chances() takes it back.",
       choices=("0 and 1 have no log-odds (SciPy gives -inf and inf): they become empty, with a note.",)),
    _e("nums.turn_into_chances", """
            numbers = sdata.number_list([-2.2, 0.0, 1.386])
            numbers.turn_into_chances()
        """, {"SciPy": """
            import numpy as np
            from scipy import special
            # turn_into_chances()
            special.expit(np.array([-2.2, 0.0, 1.386]))
        """}, "Grids and blocks work the same way, number by number."),
    _e("sdata.count_ways_to_choose", """
            sdata.count_ways_to_choose(3, out_of=10)
        """, {"SciPy": """
            from scipy import special
            # count_ways_to_choose(3, out_of=10)
            special.comb(10, 3, exact=True)
        """}, "Exact whole numbers however big (Python integers)."),
    _e("sdata.count_ways_to_order", """
            sdata.count_ways_to_order(3, out_of=10)
        """, {"SciPy": """
            from scipy import special
            # count_ways_to_order(3, out_of=10)
            special.perm(10, 3, exact=True)
        """}, "Exact whole numbers however big (Python integers)."),
    _e("sdata.number_list", """
            import os, tempfile
            path = os.path.join(tempfile.mkdtemp(), "readings.txt")
            with open(path, "w") as f:
                f.write("12.5\\n-999\\n13.1\\n-999.0\\n12.9\\n")
            sdata.number_list(path, empty_values=[-999])
        """, {"pandas": """
            import os, tempfile
            import pandas as pd
            path = os.path.join(tempfile.mkdtemp(), "readings.txt")
            with open(path, "w") as f:
                f.write("12.5\\n-999\\n13.1\\n-999.0\\n12.9\\n")
            # number_list("readings.txt", empty_values=[-999])
            pd.read_csv(path, sep=r"\\s+", header=None, na_values=[-999]).iloc[:, 0].to_numpy()
        """}, "A first line that is not a number is taken as the name; text among the numbers is refused with the "
               "markers to name.", option="empty_values="),
    _e("sdata.make_random_numbers", """
            sdata.make_random_numbers(of_shape=(2, 3, 4), average=10, standard_deviation=2, with_seed=5)
        """, {"NumPy": """
            import numpy as np
            # make_random_numbers(of_shape=(2, 3, 4), average=10, standard_deviation=2, with_seed=5)
            np.random.default_rng(5).normal(10, 2, (2, 3, 4))
        """}, "A block, with the names sdata.number_block gives (page, row, column).", option="of_shape="),
]
