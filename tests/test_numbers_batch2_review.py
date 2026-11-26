"""NumPy + SciPy phase, batch 2: fixes after the independent review. Each test failed before its fix and checks the
result against the parent library (h5py, xarray, pandas, SciPy) directly.

1-2 privacy: no variable from another file (HDF5 external links, virtual datasets); no network shares or tool chains.
3-4 joining files: labels or units that differ are refused, never filled with empty values or relabelled.
5 text files: only the markers given mean "no value". 6 stacked variables keep their units on save.
7 smooth(ends=) uses SciPy's names. 8 time-zone dates stay dates. 9 places outside the labels counted right.
10 files kept on disk are closed once read, and saving over an open file is refused plainly.
"""

from __future__ import annotations

import os
import socket

import numpy as np
import pandas as pd
import pytest
from scipy import ndimage

import simplydata as sdata


@pytest.fixture
def xr():
    try:
        import h5netcdf  # noqa: F401
        import h5py  # noqa: F401
        import xarray
    except ImportError:
        if os.environ.get("SIMPLYDATA_REQUIRE_XARRAY") == "1":
            pytest.fail("SIMPLYDATA_REQUIRE_XARRAY=1 but xarray or h5netcdf is missing")
        pytest.skip("needs xarray and h5netcdf (pip install 'simplydata[xarray]')")
    return xarray


@pytest.fixture
def no_network(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("a file word tried to use the network")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)


# ---------------------------------------------------------------------- 1. variables from another file
def _file_with_external_link(xr, folder):
    import h5py

    with h5py.File(folder / "secret.h5", "w") as handle:
        handle["data"] = np.array([42.0, 43.0])
    xr.DataArray(np.zeros(2), dims=["x"], name="v").to_netcdf(folder / "ext.nc", engine="h5netcdf")
    with h5py.File(folder / "ext.nc", "a") as handle:
        handle["leak"] = h5py.ExternalLink(str(folder / "secret.h5"), "/data")
    with h5py.File(folder / "ext.nc", "r") as handle:  # h5py itself follows the link to the other file
        np.testing.assert_array_equal(handle["leak"][()], [42.0, 43.0])
    return folder / "ext.nc"


def test_external_links_are_refused_before_reading(xr, tmp_path, no_network):
    path = _file_with_external_link(xr, tmp_path)
    for read in (lambda: sdata.number_block(str(path), values="leak"),
                 lambda: sdata.number_block(str(path), values="v"),
                 lambda: sdata.number_block(str(path), values="v", keep_on_disk=True),
                 lambda: sdata.number_block(str(tmp_path / "ex*.nc"), values="v"),
                 lambda: sdata.show_whats_inside(str(path))):
        with pytest.raises(sdata.SimplydataError, match='"leak" \\(a link to .*secret.h5\\) comes from another file'):
            read()


def test_virtual_datasets_are_refused(xr, tmp_path):
    import h5py

    with h5py.File(tmp_path / "source.h5", "w") as handle:
        handle["data"] = np.arange(4.0)
    xr.DataArray(np.zeros(2), dims=["x"], name="v").to_netcdf(tmp_path / "vds.nc", engine="h5netcdf")
    layout = h5py.VirtualLayout(shape=(4,), dtype="f8")
    layout[:] = h5py.VirtualSource(str(tmp_path / "source.h5"), "data", shape=(4,))
    with h5py.File(tmp_path / "vds.nc", "a") as handle:
        handle.create_virtual_dataset("joined", layout)
    with pytest.raises(sdata.SimplydataError, match='"joined" \\(made from .*source.h5\\)'):
        sdata.number_block(str(tmp_path / "vds.nc"), values="v")


# ---------------------------------------------------------------------- 2. tool chains refused, shares allowed
@pytest.mark.parametrize("name", ["simplecache::x.nc", "zip::archive.nc", "simplecache::x_*.nc",
                                  "https://example.org/x.nc", "file://C:/x.nc", "dap://server/x.nc"])
def test_tool_chains_and_schemes_are_refused_before_opening(name, no_network, monkeypatch):
    import builtins

    def no_open(*args, **kwargs):
        raise AssertionError("a file was opened before the name was checked")

    monkeypatch.setattr(builtins, "open", no_open)
    for call in (lambda: sdata.number_block(name, values="v"), lambda: sdata.show_whats_inside(name),
                 lambda: sdata.number_block([[1.0]]).save(name.replace("*", "1")),
                 lambda: sdata.numbers(name.replace(".nc", ".txt").replace("*", "1"))):
        with pytest.raises(sdata.SimplydataError, match="opens only the file you name; it never downloads"):
            call()


@pytest.mark.parametrize("name", [r"\\server\share\x.nc", "//server/share/x.nc", r"\\?\UNC\server\share\x.nc",
                                  r"N:\data\sst.nc"])
def test_files_on_network_shares_and_mapped_drives_are_allowed(name):
    """Manish, 2026-11-26: a file the user names on a share or a mapped drive is read like any other file (as
    sdata.table reads it); only web addresses, scheme:// paths and :: chains are refused. Checked on the name alone,
    so the test needs no share."""
    from simplydata.numbers.block_files import refuse_network_path

    refuse_network_path(name, "sdata.number_block()")  # no error


# ---------------------------------------------------------------------- 3, 4. joining files
def test_files_whose_labels_differ_are_refused_not_filled(xr, tmp_path, recwarn):
    times = pd.date_range("2010-01-01", periods=4, freq="D")
    xr.DataArray(np.ones((2, 3)), dims=["time", "lat"], coords={"time": times[:2], "lat": [60, 61, 62]},
                 name="t").to_netcdf(tmp_path / "a_1.nc", engine="h5netcdf")
    xr.DataArray(np.ones((2, 2)), dims=["time", "lat"], coords={"time": times[2:], "lat": [60, 61.5]},
                 name="t").to_netcdf(tmp_path / "a_2.nc", engine="h5netcdf")
    with xr.open_dataset(tmp_path / "a_1.nc") as a, xr.open_dataset(tmp_path / "a_2.nc") as b:
        outer = xr.combine_by_coords([a, b], join="outer")  # what xarray's default join does: empty places
        assert int(outer["t"].isnull().sum()) == 6
    with pytest.raises(sdata.SimplydataError, match="the labels of lat differ"):
        sdata.number_block(str(tmp_path / "a_*.nc"), values="t")
    assert not [w for w in recwarn if issubclass(w.category, FutureWarning)]


def test_files_with_other_units_are_refused(xr, tmp_path):
    xr.DataArray(np.ones(2), dims=["time"], coords={"time": pd.date_range("2010-01-01", periods=2)}, name="t",
                 attrs={"units": "degC"}).to_netcdf(tmp_path / "u_1.nc", engine="h5netcdf")
    xr.DataArray(np.ones(2) * 300, dims=["time"], coords={"time": pd.date_range("2010-01-03", periods=2)}, name="t",
                 attrs={"units": "K"}).to_netcdf(tmp_path / "u_2.nc", engine="h5netcdf")
    with pytest.raises(sdata.SimplydataError, match=r"different units \(degC in u_1.nc; K in u_2.nc\)"):
        sdata.number_block(str(tmp_path / "u_*.nc"), values="t")


# ---------------------------------------------------------------------- 5. only the markers given
def test_text_na_is_refused_unless_it_is_a_marker(tmp_path):
    path = tmp_path / "r.txt"
    path.write_text("12.5\n-999\nNA\n13.1\n")
    assert pd.read_csv(path, header=None, na_values=[-999]).iloc[:, 0].isna().sum() == 2  # pandas' own NA list
    with pytest.raises(sdata.SimplydataError, match='text among its numbers, such as "NA"'):
        sdata.numbers(str(path), empty_values=[-999])
    got = sdata.numbers(str(path), empty_values=[-999, "NA"])
    expected = pd.read_csv(path, header=None, na_values=[-999, "NA"], keep_default_na=False).iloc[:, 0].to_numpy()
    np.testing.assert_array_equal(got.as_numpy(), expected)


# ---------------------------------------------------------------------- 6. stacked variables keep their units
def test_stacked_variables_keep_their_units_on_save(xr, tmp_path):
    ds = xr.Dataset({"u": (["x"], np.array([1.0, 2.0]), {"units": "m/s"}),
                     "v": (["x"], np.array([1.5, 2.5]), {"units": "degC"})})
    ds.to_netcdf(tmp_path / "s.nc", engine="h5netcdf")
    sdata.number_block(str(tmp_path / "s.nc"), values=["u", "v"]).save(str(tmp_path / "back.nc"))
    with xr.open_dataset(tmp_path / "back.nc", engine="h5netcdf") as back:
        assert back["u"].attrs["units"] == "m/s" and back["v"].attrs["units"] == "degC"
        np.testing.assert_array_equal(back["v"].values, [1.5, 2.5])


# ---------------------------------------------------------------------- 7. ends= with SciPy's names
@pytest.mark.parametrize("ends", ["mirror", "reflect"])
def test_smooth_ends_use_scipys_modes(ends):
    row = np.array([1.0, 2, 3, 10, 5])
    grid = sdata.number_grid([row.tolist()] * 3)
    grid.smooth(over="column", window=3, ends=ends)
    expected = ndimage.uniform_filter1d(row, 3, mode=ends)
    np.testing.assert_allclose(grid.as_numpy()[0], expected, rtol=1e-12)
    if ends == "mirror":
        np.testing.assert_allclose(grid.as_numpy()[0, [0, -1]], [5 / 3, 25 / 3], rtol=1e-12)
    values = np.random.default_rng(1).normal(size=(5, 6))
    g = sdata.number_grid(values.tolist())
    g.smooth(test_method="gaussian", width=1, ends=ends)
    np.testing.assert_allclose(g.as_numpy(), ndimage.gaussian_filter(values, 1, mode=ends), rtol=1e-12)


@pytest.mark.parametrize("ends", ["mirror", "reflect"])
def test_ends_mean_the_same_scipy_mode_on_numbers_tables_grids_and_blocks(ends):
    # ends="mirror" is SciPy "mirror" and ends="reflect" SciPy "reflect" everywhere (2026-11-26). Before, nums.smooth
    # and table.add_smoothed_column turned "mirror" into SciPy "reflect", so the "mirror" case fails on that mapping.
    row = np.array([1.0, 2, 3, 10, 5, 4, 8])
    expected = ndimage.convolve1d(row, np.ones(3) / 3, mode=ends)
    nums = sdata.numbers(row.tolist())
    nums.smooth(window=3, ends=ends)
    np.testing.assert_allclose(nums.as_numpy(), expected, rtol=1e-12)
    table = sdata.table(pd.DataFrame({"t": range(7), "v": row}))
    table.add_smoothed_column("s", from_column="v", window=3, ends=ends)
    np.testing.assert_allclose(table.as_pandas()["s"].to_numpy(), expected, rtol=1e-12)
    grid = sdata.number_grid([row.tolist()] * 2)
    grid.smooth(over="column", window=3, ends=ends)
    np.testing.assert_allclose(grid.as_numpy()[0], expected, rtol=1e-12)
    block = sdata.number_block([[row.tolist()]] * 2, directions_named=["page", "row", "column"])
    block.smooth(over="column", window=3, ends=ends)
    np.testing.assert_allclose(block.as_numpy()[0, 0], expected, rtol=1e-12)
    if ends == "mirror":  # 1 2 3 ... mirrored about the end reading: (2 + 1 + 2) / 3
        assert nums.as_numpy()[0] == pytest.approx(5 / 3, rel=1e-12)
    gauss = sdata.numbers(row.tolist())
    gauss.smooth(test_method="gaussian", width=1, ends=ends)
    np.testing.assert_allclose(gauss.as_numpy(), ndimage.gaussian_filter1d(row, 1, truncate=4.0, mode=ends),
                               rtol=1e-12)


# ---------------------------------------------------------------------- 8. time-zone dates stay dates
def test_time_zone_dates_are_kept_as_dates_in_utc(xr, capsys):
    local = pd.Series(pd.date_range("2024-01-01", periods=48, freq="h", tz="Europe/Oslo"))
    block = sdata.number_block(np.arange(48.0), directions_named=["time"])
    block.add_labels_to("time", local)
    assert "kept as the same moments in UTC" in capsys.readouterr().out
    utc = pd.DatetimeIndex(local).tz_convert("UTC").tz_localize(None)
    assert block.get_labels_of("time").as_pandas()["time"].tolist() == list(utc)
    got = block.find_average(in_each="hour")
    expected = xr.DataArray(np.arange(48.0), dims=["time"], coords={"time": utc}).groupby("time.hour").mean()
    np.testing.assert_allclose(got.as_numpy(), expected.values)


# ---------------------------------------------------------------------- 9. places outside the labels
def test_places_outside_are_counted_from_the_labels(capsys):
    values = np.arange(12.0).reshape(3, 4)
    values[1, 1] = np.nan  # an empty value inside the labels is not "outside"
    block = sdata.number_block(values, directions_named=["y", "x"], with_labels={"y": [0, 1, 2], "x": [0, 1, 2, 3]})
    capsys.readouterr()
    block.find_values_at(x=[0.5, 1.5])
    assert "outside" not in capsys.readouterr().out
    block.find_values_at(x=[-1, 0.5, 9])
    assert "6 places outside the labels are empty" in capsys.readouterr().out  # 2 x-places beyond x 0..3, 3 rows


# ---------------------------------------------------------------------- 10. files kept on disk are closed
def test_a_file_kept_on_disk_is_closed_once_read_and_can_be_saved_over(xr, tmp_path, capsys):
    import h5py

    xr.DataArray(np.arange(6.0).reshape(2, 3), dims=["r", "c"], name="v", attrs={"units": "K"}).to_netcdf(
        tmp_path / "k.nc", engine="h5netcdf")
    block = sdata.number_block(str(tmp_path / "k.nc"), values="v", keep_on_disk=True)
    block.keep_by_position_in("r", 1)
    block.save(str(tmp_path / "k.nc"))  # reads the numbers, closes the file, then writes over it
    with xr.open_dataset(tmp_path / "k.nc", engine="h5netcdf") as ds:
        np.testing.assert_array_equal(ds["v"].values, [[0.0, 1.0, 2.0]])
        assert ds["v"].attrs["units"] == "K"
    with h5py.File(tmp_path / "k.nc", "a"):  # nothing holds the file open any more
        pass


def test_saving_over_a_file_still_open_in_another_block_is_refused(xr, tmp_path):
    xr.DataArray(np.arange(3.0), dims=["x"], name="v").to_netcdf(tmp_path / "o.nc", engine="h5netcdf")
    still_open = sdata.number_block(str(tmp_path / "o.nc"), values="v", keep_on_disk=True)
    with pytest.raises(sdata.SimplydataError, match="is open, perhaps in another block read with keep_on_disk=True"):
        sdata.number_block([1.0, 2.0, 3.0], directions_named=["x"]).save(str(tmp_path / "o.nc"))
    del still_open
    import gc

    gc.collect()  # deleting the block closes its file
    sdata.number_block([1.0, 2.0, 3.0], directions_named=["x"]).save(str(tmp_path / "o.nc"))


def test_empty_values_with_keep_on_disk_read_nothing_until_needed(xr, tmp_path, capsys):
    values = np.arange(6.0)
    values[2] = -999
    xr.DataArray(values, dims=["x"], name="v").to_netcdf(tmp_path / "e.nc", engine="h5netcdf")
    block = sdata.number_block(str(tmp_path / "e.nc"), values="v", keep_on_disk=True, empty_values=[-999])
    assert block._on_disk()
    assert "become empty when the numbers are read" in capsys.readouterr().out
    with xr.open_dataset(tmp_path / "e.nc", engine="h5netcdf") as ds:
        expected = ds["v"].where(ds["v"] != -999).values
    np.testing.assert_array_equal(block.as_numpy(), expected)
    assert "1 value equal to -999 is now empty" in capsys.readouterr().out


def test_start_again_reads_a_closed_file_again(xr, tmp_path):
    xr.DataArray(np.arange(6.0).reshape(2, 3), dims=["r", "c"], name="v").to_netcdf(tmp_path / "k2.nc",
                                                                                   engine="h5netcdf")
    block = sdata.number_block(str(tmp_path / "k2.nc"), values="v", keep_on_disk=True)
    block.keep_by_position_in("r", 2)
    block.add(1)
    np.testing.assert_array_equal(block.as_numpy(), [[4.0, 5.0, 6.0]])
    block.start_again()
    np.testing.assert_array_equal(block.as_numpy(), np.arange(6.0).reshape(2, 3))
