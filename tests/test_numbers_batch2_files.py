"""NumPy + SciPy phase, batch 2: blocks from netCDF files and back (P21, P22), text files of numbers (P38), and the
privacy rules of the file words: local files only, nothing over the network, show_whats_inside writes nothing.

Every result is compared with xarray (or NumPy, pandas, openpyxl) reading the same file directly.
"""

from __future__ import annotations

import os
import socket

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata.numbers.blocks import FileBlock, NumberBlock


@pytest.fixture
def xr():
    """xarray with h5netcdf (simplydata[xarray]): skipped where missing, except when SIMPLYDATA_REQUIRE_XARRAY=1 (CI)."""
    try:
        import h5netcdf  # noqa: F401
        import xarray
    except ImportError:
        if os.environ.get("SIMPLYDATA_REQUIRE_XARRAY") == "1":
            pytest.fail("SIMPLYDATA_REQUIRE_XARRAY=1 but xarray or h5netcdf is missing (pip install 'simplydata[xarray]')")
        pytest.skip("needs xarray and h5netcdf (pip install 'simplydata[xarray]')")
    return xarray


@pytest.fixture
def no_network(monkeypatch):
    """Any attempt to open a network connection fails the test."""
    def refuse(*args, **kwargs):
        raise AssertionError("a file word tried to use the network")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket.socket, "connect_ex", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)


RNG = np.random.default_rng(7)
SST = RNG.normal(12, 2, size=(24, 3, 4)).astype(np.float32)
TIMES = pd.date_range("2010-01-01", periods=24, freq="MS")
LATS = np.array([61.5, 60.5, 59.5])  # stored from north to south, as many ocean files are
LONS = np.array([2.0, 3.0, 4.0, 5.0])


def write_sst(xr, path, engine="h5netcdf", **more):
    ds = xr.Dataset({"sst": (("time", "latitude", "longitude"), SST, {"units": "degrees C", "long_name": "sea surface "
                                                                                                        "temperature"}),
                     **more},
                    coords={"time": TIMES, "latitude": LATS, "longitude": LONS}, attrs={"title": "made-up sst"})
    ds.to_netcdf(path, engine=engine)
    return ds


# ---------------------------------------------------------------------- reading (P21)
def test_number_block_reads_one_variable_with_names_and_labels(xr, tmp_path, no_network, capsys):
    path = tmp_path / "sst.nc"
    write_sst(xr, path)
    block = sdata.number_block(str(path), values="sst")
    with xr.open_dataset(path, engine="h5netcdf") as ds:
        expected = ds["sst"].values
    np.testing.assert_array_equal(block.as_numpy(), expected)
    assert block.find_direction_names() == ["time", "latitude", "longitude"]
    np.testing.assert_array_equal(block.get_labels_of("latitude").as_numpy(), LATS)
    assert block.get_labels_of("time").as_pandas()["time"].tolist() == list(TIMES)
    out = capsys.readouterr().out
    assert "sst: 24 times x 3 latitudes x 4 longitudes, degrees C" in out
    assert "latitude from 61.5 to 59.5 (runs downward)" in out
    assert "xarray open_dataset (h5netcdf engine)" in out


def test_classic_netcdf3_is_read_with_scipys_engine(xr, tmp_path, no_network):
    path = tmp_path / "classic.nc"
    write_sst(xr, path, engine="scipy")
    block = sdata.number_block(str(path), values="sst")
    with xr.open_dataset(path, engine="scipy") as ds:
        np.testing.assert_array_equal(block.as_numpy(), ds["sst"].values)


def test_values_list_stacks_variables_as_a_new_direction(xr, tmp_path):
    path = tmp_path / "uv.nc"
    write_sst(xr, path, u=(("time", "latitude", "longitude"), SST * 2))
    block = sdata.number_block(str(path), values=["sst", "u"])
    with xr.open_dataset(path, engine="h5netcdf") as ds:
        expected = ds[["sst", "u"]].to_dataarray(dim="variable")
        np.testing.assert_array_equal(block.as_numpy(), expected.values)
    assert block.find_direction_names()[0] == "variable"
    assert block.get_labels_of("variable").as_pandas()["variable"].tolist() == ["sst", "u"]


def test_a_file_pattern_joins_files_by_their_labels(xr, tmp_path):
    ds = write_sst(xr, tmp_path / "whole.nc")
    ds.isel(time=slice(0, 12)).to_netcdf(tmp_path / "argo_2010.nc", engine="h5netcdf")
    ds.isel(time=slice(12, 24)).to_netcdf(tmp_path / "argo_2011.nc", engine="h5netcdf")
    block = sdata.number_block(str(tmp_path / "argo_*.nc"), values="sst")
    np.testing.assert_array_equal(block.as_numpy(), SST)
    assert block.get_labels_of("time").as_pandas()["time"].tolist() == list(TIMES)


def test_empty_values_and_fill_values(xr, tmp_path):
    values = SST.copy()
    values[0, 0, 0] = -999
    ds = xr.Dataset({"sst": (("time", "latitude", "longitude"), values)},
                    coords={"time": TIMES, "latitude": LATS, "longitude": LONS})
    ds.to_netcdf(tmp_path / "gaps.nc", engine="h5netcdf")
    block = sdata.number_block(str(tmp_path / "gaps.nc"), values="sst", empty_values=[-999])
    with xr.open_dataset(tmp_path / "gaps.nc", engine="h5netcdf") as opened:
        expected = opened["sst"].where(opened["sst"] != -999).values
    np.testing.assert_array_equal(block.as_numpy(), expected)
    assert block.count_empty_numbers() == 1


def test_plain_errors_name_the_variables(xr, tmp_path):
    path = tmp_path / "uv.nc"
    write_sst(xr, path, u=(("time", "latitude", "longitude"), SST))
    with pytest.raises(sdata.SimplydataError, match="2 variables: sst, u"):
        sdata.number_block(str(path))
    with pytest.raises(sdata.SimplydataError, match='Did you mean "sst"'):
        sdata.number_block(str(path), values="ssst")
    with pytest.raises(sdata.SimplydataError, match="not found"):
        sdata.number_block(str(tmp_path / "missing.nc"), values="sst")
    (tmp_path / "plain.nc").write_text("not netcdf")
    with pytest.raises(sdata.SimplydataError, match="not a netCDF file"):
        sdata.number_block(str(tmp_path / "plain.nc"), values="sst")


def test_without_xarray_a_plain_error_with_the_install_line(tmp_path, monkeypatch):
    import sys

    path = tmp_path / "x.nc"
    path.write_bytes(b"\x89HDF\r\n\x1a\n" + b"\0" * 64)
    monkeypatch.setitem(sys.modules, "xarray", None)
    with pytest.raises(sdata.SimplydataError, match=r'pip install "simplydata\[xarray\]"'):
        sdata.number_block(str(path), values="sst")
    with pytest.raises(sdata.SimplydataError, match=r'pip install "simplydata\[xarray\]"'):
        sdata.number_block([[1.0, 2.0]]).save(str(tmp_path / "out.nc"))


# ---------------------------------------------------------------------- saving
def test_save_round_trip_equals_xarray(xr, tmp_path, no_network, capsys):
    block = sdata.number_block(SST.astype(float), directions_named=["time", "latitude", "longitude"],
                               with_labels={"time": TIMES, "latitude": LATS, "longitude": LONS})
    block.save(str(tmp_path / "out.nc"))
    assert "netCDF-4, compressed" in capsys.readouterr().out
    with xr.open_dataset(tmp_path / "out.nc", engine="h5netcdf") as ds:
        np.testing.assert_array_equal(ds["values"].values, SST.astype(float))
        np.testing.assert_array_equal(ds["latitude"].values, LATS)
        assert list(ds["values"].dims) == ["time", "latitude", "longitude"]
        assert ds["values"].encoding.get("zlib") or ds["values"].encoding.get("compression") == "gzip"


def test_a_block_read_from_a_file_keeps_its_name_and_units(xr, tmp_path):
    write_sst(xr, tmp_path / "sst.nc")
    sdata.number_block(str(tmp_path / "sst.nc"), values="sst").save(str(tmp_path / "again.nc"))
    with xr.open_dataset(tmp_path / "again.nc", engine="h5netcdf") as ds:
        assert ds["sst"].attrs["units"] == "degrees C"
        np.testing.assert_array_equal(ds["sst"].values, SST)


def test_saving_csv_still_writes_the_long_table(tmp_path):
    block = sdata.number_block([[1, 2], [3, 4]])
    block.save(str(tmp_path / "b.csv"))
    assert pd.read_csv(tmp_path / "b.csv")["value"].tolist() == [1, 2, 3, 4]


# ---------------------------------------------------------------------- keep_on_disk=True
def test_keep_on_disk_reads_only_the_part_kept(xr, tmp_path, no_network, capsys):
    write_sst(xr, tmp_path / "sst.nc")
    block = sdata.number_block(str(tmp_path / "sst.nc"), values="sst", keep_on_disk=True)
    assert isinstance(block, FileBlock) and block._on_disk()
    assert block.find_shape() == (24, 3, 4)
    block.keep_where("latitude", is_between=[60, 62])  # written low to high on labels that run downward
    block.keep_by_position_in("time", 1, to=6)
    assert block._on_disk(), "cutting must not read the numbers"
    assert block.find_shape() == (6, 2, 4)
    capsys.readouterr()
    total = block.find_total()
    assert "from sst.nc now" in capsys.readouterr().out
    with xr.open_dataset(tmp_path / "sst.nc", engine="h5netcdf") as ds:
        expected = ds["sst"].sel(latitude=slice(62, 60)).isel(time=slice(0, 6)).values
    assert total == pytest.approx(float(np.nansum(expected)), rel=1e-6)
    np.testing.assert_array_equal(block.get_labels_of("latitude").as_numpy(), [61.5, 60.5])


def test_keep_on_disk_undo_and_nearest(xr, tmp_path):
    write_sst(xr, tmp_path / "sst.nc")
    block = sdata.number_block(str(tmp_path / "sst.nc"), values="sst", keep_on_disk=True)
    block.keep_by_position_in("time", [1, 2])
    block.undo()
    assert block.find_shape() == (24, 3, 4) and block._on_disk()
    station = block.get_numbers_nearest_to(latitude=60.4, longitude=4.6)
    with xr.open_dataset(tmp_path / "sst.nc", engine="h5netcdf") as ds:
        expected = ds["sst"].sel(latitude=60.4, longitude=4.6, method="nearest").values
    np.testing.assert_array_equal(station.as_numpy(), expected)
    assert block._on_disk(), "only the station's numbers were read"


# ---------------------------------------------------------------------- sdata.show_whats_inside (P22)
def test_show_whats_inside_netcdf_reads_metadata_and_writes_nothing(xr, tmp_path, no_network, capsys, monkeypatch):
    write_sst(xr, tmp_path / "sst.nc")
    monkeypatch.chdir(tmp_path)
    before = sorted(os.listdir(tmp_path))
    assert sdata.show_whats_inside("sst.nc") is None
    assert sorted(os.listdir(tmp_path)) == before
    out = capsys.readouterr().out
    with xr.open_dataset(tmp_path / "sst.nc", engine="h5netcdf") as ds:
        for name, var in ds.data_vars.items():
            assert f"{name}: 24 times x 3 latitudes x 4 longitudes, {var.attrs['units']}" in out
        assert f"title: {ds.attrs['title']}" in out
    assert "sea surface temperature" in out


def test_show_whats_inside_npz_npy_and_excel(tmp_path, capsys, monkeypatch):
    from openpyxl import Workbook, load_workbook

    np.savez(tmp_path / "arrays.npz", plate=np.zeros((24, 8, 12)), blank=np.ones((8, 12), dtype=np.int32))
    np.save(tmp_path / "one.npy", np.arange(10.0))
    book = Workbook()
    book.active.title = "plate 1"
    for row in range(5):
        book.active.append([1, 2, 3])
    book.create_sheet("notes").append(["x"])
    book.save(tmp_path / "lab.xlsx")
    before = sorted(os.listdir(tmp_path))
    for name in ("arrays.npz", "one.npy", "lab.xlsx"):
        sdata.show_whats_inside(str(tmp_path / name))
    assert sorted(os.listdir(tmp_path)) == before
    out = capsys.readouterr().out
    with np.load(tmp_path / "arrays.npz") as found:
        for key in found.files:
            assert f"{key}: shape {found[key].shape} ({found[key].dtype})" in out
    assert "one.npy: one NumPy array, shape (10,) (float64)" in out
    for sheet in load_workbook(tmp_path / "lab.xlsx").worksheets:
        assert f'"{sheet.title}": {sheet.max_row} rows x {sheet.max_column} columns' in out


# ---------------------------------------------------------------------- privacy: no web addresses
@pytest.mark.parametrize("address", ["https://example.org/sst.nc", "http://example.org/sst.nc",
                                     "s3://bucket/sst.nc", "dap://server/sst.nc", "file://C:/sst.nc",
                                     "https://example.org/argo_*.nc"])
def test_file_words_refuse_web_addresses_before_opening(address, no_network, tmp_path):
    with pytest.raises(sdata.SimplydataError, match="opens only the file you name; it never downloads"):
        sdata.number_block(address, values="sst")
    with pytest.raises(sdata.SimplydataError, match="opens only the file you name; it never downloads"):
        sdata.show_whats_inside(address)
    with pytest.raises(sdata.SimplydataError, match="opens only the file you name; it never downloads"):
        sdata.number_block([[1.0, 2.0]]).save(address.replace("*", "x"))
    with pytest.raises(sdata.SimplydataError, match="opens only the file you name; it never downloads"):
        sdata.number_list(address.replace(".nc", ".txt").replace("*", "x"))


# ---------------------------------------------------------------------- sdata.number_list from a text file (P38)
def test_numbers_from_a_text_file_with_empty_values_equal_pandas(tmp_path, no_network, capsys):
    path = tmp_path / "readings.txt"
    path.write_text("depth\n12.5\n-999\n13.1\n-999.0\n12.9\n")
    nums = sdata.number_list(str(path), empty_values=[-999])
    expected = pd.read_csv(path, sep=r"\s+", header=0, na_values=[-999]).iloc[:, 0].to_numpy()
    np.testing.assert_array_equal(nums.as_numpy(), expected)
    assert nums.count_empty_numbers() == 2
    assert '"depth", is the name' in capsys.readouterr().out
    csv = tmp_path / "r.csv"
    csv.write_text("1\n2\nNA\n4\n")
    np.testing.assert_array_equal(sdata.number_list(str(csv), empty_values=["NA"]).as_numpy(),
                                  pd.read_csv(csv, header=None, na_values=["NA"],
                                              keep_default_na=False).iloc[:, 0].to_numpy())


def test_numbers_from_text_refuse_text_and_columns(tmp_path):
    (tmp_path / "bad.txt").write_text("1\nbroken\n3\n")
    with pytest.raises(sdata.SimplydataError, match='empty_values=\\["broken"\\]'):
        sdata.number_list(str(tmp_path / "bad.txt"))
    assert sdata.number_list(str(tmp_path / "bad.txt"), empty_values=["broken"]).count_empty_numbers() == 1
    (tmp_path / "two.csv").write_text("1,2\n3,4\n")
    with pytest.raises(sdata.SimplydataError, match="2 columns"):
        sdata.number_list(str(tmp_path / "two.csv"))
    with pytest.raises(sdata.SimplydataError, match="goes with a file"):
        sdata.number_list([1, 2], empty_values=[-999])


def test_block_from_a_file_is_an_ordinary_block(xr, tmp_path):
    write_sst(xr, tmp_path / "sst.nc")
    block = sdata.number_block(str(tmp_path / "sst.nc"), values="sst")
    assert type(block) is NumberBlock
    np.testing.assert_allclose(block.find_average(over="time").as_numpy(), np.nanmean(SST, axis=0), rtol=1e-6)
