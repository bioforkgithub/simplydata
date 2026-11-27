"""NumPy + SciPy phase, batch 2: labels, dates and places on blocks (P26-P30, P32, P46, P47), compared with xarray,
SciPy, NumPy and pandas doing the same job directly; tight tolerances, never against simplydata itself.

The block rules hold: directions are found by name, labels move with their numbers and are never left out without a
note, and words with a NumPy/SciPy path give the same numbers with and without xarray installed.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import pytest
from scipy import ndimage
from scipy.interpolate import interpn

import simplydata as sdata


@pytest.fixture
def xr():
    try:
        import xarray
    except ImportError:
        if os.environ.get("SIMPLYDATA_REQUIRE_XARRAY") == "1":
            pytest.fail("SIMPLYDATA_REQUIRE_XARRAY=1 but xarray is missing (pip install 'simplydata[xarray]')")
        pytest.skip("needs xarray (pip install 'simplydata[xarray]')")
    return xarray


@pytest.fixture
def without_xarray(monkeypatch):
    monkeypatch.setitem(sys.modules, "xarray", None)


RNG = np.random.default_rng(23)
VALUES = RNG.normal(12, 2, size=(48, 4, 6))
VALUES[3, 1, 2] = np.nan  # one empty value, skipped by the summaries
TIMES = pd.date_range("2008-01-01", periods=48, freq="MS")
LATS = np.array([63.0, 62.0, 61.0, 60.0])  # north to south
LONS = np.array([0.5, 1.5, 2.5, 3.5, 4.5, 5.5])


def sea():
    return sdata.number_block(VALUES.copy(), directions_named=["time", "latitude", "longitude"],
                              with_labels={"time": TIMES, "latitude": LATS, "longitude": LONS})


def sea_xr(xr, values=VALUES):
    return xr.DataArray(values, dims=["time", "latitude", "longitude"],
                        coords={"time": TIMES, "latitude": LATS, "longitude": LONS})


# ---------------------------------------------------------------------- P47 labels
def test_labels_at_creation_and_later(xr):
    block = sea()
    np.testing.assert_array_equal(block.get_labels_of("latitude").as_numpy(), sea_xr(xr).coords["latitude"].values)
    assert block.get_labels_of("time").as_pandas()["time"].tolist() == list(TIMES)
    block.add_labels_to("latitude", [10, 20, 30, 40])
    expected = sea_xr(xr).assign_coords(latitude=[10, 20, 30, 40]).coords["latitude"].values
    np.testing.assert_array_equal(block.get_labels_of("latitude").as_numpy(), expected)
    block.undo()
    np.testing.assert_array_equal(block.get_labels_of("latitude").as_numpy(), LATS)


def test_labels_from_a_run_of_dates_and_text():
    plate = sdata.number_block(of_shape=(3, 2), directions_named=["month", "well"])
    plate.add_labels_to("month", sdata.make_run_of_dates("2020-01", how_many=3, every="month"))
    assert plate.get_labels_of("month").as_pandas()["month"].tolist() == list(pd.date_range("2020-01-01", periods=3,
                                                                                           freq="MS"))
    plate.add_labels_to("well", ["A1", "A2"])
    assert plate.get_labels_of("well").as_pandas()["well"].tolist() == ["A1", "A2"]


def test_labels_are_checked():
    block = sea()
    with pytest.raises(sdata.SimplydataError, match="needs 4 labels; 3 were given"):
        block.add_labels_to("latitude", [1, 2, 3])
    with pytest.raises(sdata.SimplydataError, match="must be different"):
        block.add_labels_to("latitude", [1, 1, 2, 3])
    bare = sdata.number_block(of_shape=(2, 3))
    with pytest.raises(sdata.SimplydataError, match="has no labels"):
        bare.get_labels_of("row")


# ---------------------------------------------------------------------- P26 in_each= and every=
@pytest.mark.parametrize("step, method", [("average", "mean"), ("total", "sum"), ("median", "median"),
                                          ("smallest", "min"), ("biggest", "max")])
def test_in_each_month_equals_xarray_groupby(xr, step, method):
    got = getattr(sea(), f"find_{step}")(in_each="month")
    expected = getattr(sea_xr(xr).groupby("time.month"), method)()
    np.testing.assert_allclose(got.as_numpy(), expected.values, rtol=1e-12)
    assert got.find_direction_names() == ["month", "latitude", "longitude"]
    np.testing.assert_array_equal(got.get_labels_of("month").as_numpy(), np.arange(1, 13))
    np.testing.assert_array_equal(got.get_labels_of("latitude").as_numpy(), LATS)


def test_standard_deviation_and_percentile_by_season(xr):
    got = sea().find_standard_deviation(in_each="season")
    expected = sea_xr(xr).groupby("time.season").std(ddof=1)
    np.testing.assert_allclose(got.as_numpy(), expected.values, rtol=1e-12)
    assert got.get_labels_of("season").as_pandas()["season"].tolist() == list(expected["season"].values)
    got = sea().find_percentile(90, in_each="year")
    expected = sea_xr(xr).groupby("time.year").quantile(0.9)
    np.testing.assert_allclose(got.as_numpy(), expected.values, rtol=1e-12)


@pytest.mark.parametrize("every, freq", [("month", "MS"), ("quarter", "QS"), ("year", "YS")])
def test_every_equals_xarray_resample(xr, every, freq):
    got = sea().find_average(every=every)
    expected = sea_xr(xr).resample(time=freq).mean()
    np.testing.assert_allclose(got.as_numpy(), expected.values, rtol=1e-12)
    assert list(got.get_labels_of("time").as_pandas()["time"]) == list(pd.DatetimeIndex(expected["time"].values))


def test_month_and_calendar_month_sentences_differ(xr, capsys):
    sea().find_average(in_each="month")
    assert "12 averages, one for each month (all years together)" in capsys.readouterr().out
    sea().find_average(every="month")
    assert "48 averages, one for each month of the calendar" in capsys.readouterr().out


def test_dates_needed_and_xarray_needed(xr, without_xarray):
    with pytest.raises(sdata.SimplydataError, match=r'pip install "simplydata\[xarray\]"'):
        sea().find_average(in_each="month")


def test_in_each_month_without_dates_is_explained(xr):
    plain = sdata.number_block(VALUES.copy(), directions_named=["time", "latitude", "longitude"])
    with pytest.raises(sdata.SimplydataError, match="No direction of this block has dates"):
        plain.find_average(in_each="month")


# ---------------------------------------------------------------------- P46 in_groups_of=
@pytest.mark.parametrize("step, method", [("average", "mean"), ("total", "sum"), ("biggest", "max")])
def test_in_groups_of_equals_xarray_coarsen(xr, step, method):
    got = getattr(sea(), f"find_{step}")(in_groups_of={"latitude": 2, "longitude": 3})
    expected = getattr(sea_xr(xr).coarsen(latitude=2, longitude=3, boundary="exact"), method)()
    np.testing.assert_allclose(got.as_numpy(), expected.values, rtol=1e-12)
    np.testing.assert_allclose(got.get_labels_of("latitude").as_numpy(), expected["latitude"].values)
    np.testing.assert_allclose(got.get_labels_of("longitude").as_numpy(), expected["longitude"].values)


def test_in_groups_of_without_xarray_gives_the_same(without_xarray):
    got = sea().find_average(in_groups_of={"longitude": 2})
    expected = np.nanmean(VALUES.reshape(48, 4, 3, 2), axis=3)
    np.testing.assert_allclose(got.as_numpy(), expected, rtol=1e-12)


def test_in_groups_of_dates_says_the_labels_were_left_out(capsys):
    got = sea().find_average(in_groups_of={"time": 12})
    assert "The labels of time (dates or text) were left out" in capsys.readouterr().out
    np.testing.assert_allclose(got.as_numpy(), np.nanmean(VALUES.reshape(4, 12, 4, 6), axis=1), rtol=1e-12)
    with pytest.raises(sdata.SimplydataError, match="cannot be split into groups of 5"):
        sea().find_average(in_groups_of={"time": 5})


# ---------------------------------------------------------------------- P27 find_values_at
def test_find_values_at_equals_xarray_interp_and_interpn(xr):
    block = sdata.number_block(np.nan_to_num(VALUES, nan=12.0), directions_named=["time", "latitude", "longitude"],
                               with_labels={"latitude": LATS, "longitude": LONS})
    got = block.find_values_at(latitude=60.75, longitude=[1.0, 2.2, 5.0])
    expected = sea_xr(xr, np.nan_to_num(VALUES, nan=12.0)).interp(latitude=60.75, longitude=[1.0, 2.2, 5.0])
    np.testing.assert_allclose(got.as_numpy(), expected.values, rtol=1e-12)
    assert got.find_direction_names() == ["time", "longitude"]
    np.testing.assert_array_equal(got.get_labels_of("longitude").as_numpy(), [1.0, 2.2, 5.0])
    for method in ("nearest", "cubic"):
        got = block.find_values_at(latitude=[60.75], test_method=method)
        moved = np.moveaxis(np.nan_to_num(VALUES, nan=12.0), 1, 0)
        out = interpn((LATS,), moved, np.array([[60.75]]), method=method, bounds_error=False, fill_value=np.nan)
        np.testing.assert_allclose(got.as_numpy(), np.moveaxis(out, 0, 1), rtol=1e-12)


def test_find_values_at_outside_is_empty_and_same_without_xarray(without_xarray):
    block = sdata.number_block([[1.0, 2.0], [3.0, 4.0]], directions_named=["y", "x"],
                               with_labels={"y": [0, 1], "x": [0, 10]})
    got = block.find_values_at(y=0.5, x=[5, 20])
    np.testing.assert_allclose(got.as_numpy(), [2.5, np.nan])


def test_find_values_at_dates_through_xarray(xr):
    block = sdata.number_block(np.arange(4.0), directions_named=["time"],
                               with_labels={"time": pd.date_range("2020-01-01", periods=4, freq="D")})
    got = block.find_values_at(time=["2020-01-01T12:00"])
    np.testing.assert_allclose(got.as_numpy(), [0.5])


# ---------------------------------------------------------------------- P28 get_numbers_nearest_to
def test_nearest_equals_xarray_sel_nearest(xr):
    got = sea().get_numbers_nearest_to(latitude=60.4, longitude=5.3)
    expected = sea_xr(xr).sel(latitude=60.4, longitude=5.3, method="nearest")
    np.testing.assert_array_equal(got.as_numpy(), expected.values)
    got = sea().get_numbers_nearest_to(latitude=[62.2, 60.1])
    expected = sea_xr(xr).sel(latitude=[62.2, 60.1], method="nearest")
    np.testing.assert_array_equal(got.as_numpy(), expected.values)
    np.testing.assert_array_equal(got.get_labels_of("latitude").as_numpy(), expected["latitude"].values)
    got = sea().get_numbers_nearest_to(time="2009-03-14", within="15 days")
    expected = sea_xr(xr).sel(time="2009-03-14", method="nearest", tolerance=pd.Timedelta("15 days"))
    np.testing.assert_array_equal(got.as_numpy(), expected.values)


def test_nearest_within_refuses_far_labels_and_works_without_xarray(without_xarray):
    with pytest.raises(sdata.SimplydataError, match="within 0.2"):
        sea().get_numbers_nearest_to(latitude=60.5, within=0.2)
    one = sea().get_numbers_nearest_to(time="2008-01-01", latitude=63, longitude=0.5)
    assert one == pytest.approx(VALUES[0, 0, 0])


# ---------------------------------------------------------------------- P29 turn_into_change_from_average
def test_anomalies_equal_xarray(xr):
    block = sea()
    block.turn_into_change_from_average(in_each="month")
    da = sea_xr(xr)
    expected = da.groupby("time.month") - da.groupby("time.month").mean()
    np.testing.assert_allclose(block.as_numpy(), expected.values, rtol=1e-12, equal_nan=True)
    block.undo()
    np.testing.assert_array_equal(block.as_numpy(), VALUES)
    block.turn_into_change_from_average(in_each="month", from_years=["2009", "2010"])
    usual = da.sel(time=slice("2009", "2010")).groupby("time.month").mean()
    np.testing.assert_allclose(block.as_numpy(), (da.groupby("time.month") - usual).values, rtol=1e-12,
                               equal_nan=True)


def test_anomalies_over_a_direction_equal_numpy(without_xarray):
    block = sea()
    block.turn_into_change_from_average(over="longitude")
    np.testing.assert_allclose(block.as_numpy(), VALUES - np.nanmean(VALUES, axis=2, keepdims=True), rtol=1e-12,
                               equal_nan=True)


def test_anomalies_baseline_is_an_other_name_and_short_periods_are_refused(xr, capsys):
    block = sea()
    block.turn_into_change_from_average(in_each="month", baseline=["2008", "2009"])
    assert "from_years=" in capsys.readouterr().out
    with pytest.raises(sdata.SimplydataError, match="No time falls in the years"):
        sea().turn_into_change_from_average(in_each="month", from_years=["1990", "1991"])


# ---------------------------------------------------------------------- P30 smooth(over=)
def test_block_smooth_moving_average_equals_uniform_filter():
    block = sdata.number_block(np.nan_to_num(VALUES), directions_named=["time", "latitude", "longitude"],
                               with_labels={"latitude": LATS})
    block.smooth(over=["latitude", "longitude"], window=3)
    expected = ndimage.uniform_filter(np.nan_to_num(VALUES), size=3, mode="reflect", axes=(1, 2))
    expected[:, [0, -1], :] = np.nan
    expected[:, :, [0, -1]] = np.nan
    np.testing.assert_allclose(block.as_numpy(), expected, rtol=1e-12, equal_nan=True)
    np.testing.assert_array_equal(block.get_labels_of("latitude").as_numpy(), LATS)  # labels stay


def test_smooth_along_one_direction_matches_nums_smooth():
    values = np.nan_to_num(VALUES)
    block = sdata.number_block(values, directions_named=["time", "latitude", "longitude"])
    block.smooth(over="time", window=5)
    line = sdata.number_list(values[:, 2, 3].tolist())
    line.smooth(window=5)
    np.testing.assert_allclose(block.as_numpy()[:, 2, 3], line.as_numpy(), rtol=1e-12, equal_nan=True)


@pytest.mark.parametrize("method, call", [
    ("gaussian", lambda v: ndimage.gaussian_filter(v, sigma=1.5, truncate=4.0, mode="reflect", axes=(0, 1))),
    ("median", lambda v: ndimage.median_filter(v, size=3, mode="reflect", axes=(0, 1)))])
def test_grid_smooth_equals_scipy(method, call):
    values = RNG.normal(size=(7, 9))
    grid = sdata.number_grid(values.tolist())
    if method == "gaussian":
        grid.smooth(test_method="gaussian", width=1.5)
    else:
        grid.smooth(test_method="median", window=3)
    np.testing.assert_allclose(grid.as_numpy(), call(values), rtol=1e-12)


def test_smooth_refuses_empty_values_and_other_methods():
    with pytest.raises(sdata.SimplydataError, match="are empty"):
        sea().smooth(over="time", window=3)
    with pytest.raises(sdata.SimplydataError, match="needs over="):
        sea().smooth(window=3)
    with pytest.raises(sdata.SimplydataError, match='"moving average", "gaussian" or "median"'):
        sdata.number_grid([[1.0, 2, 3]] * 3).smooth(test_method="lowess")


# ---------------------------------------------------------------------- P32 block versions
def test_change_size_to_equals_zoom_and_labels_follow():
    values = np.nan_to_num(VALUES)
    block = sdata.number_block(values, directions_named=["time", "latitude", "longitude"],
                               with_labels={"latitude": LATS, "longitude": LONS})
    block.change_size_to(latitude=7, longitude=11)
    expected = ndimage.zoom(values, (1, 7 / 4, 11 / 6), order=1)
    np.testing.assert_allclose(block.as_numpy(), expected, rtol=1e-12)
    np.testing.assert_allclose(block.get_labels_of("latitude").as_numpy(), np.linspace(63, 60, 7), rtol=1e-12)
    np.testing.assert_allclose(block.get_labels_of("longitude").as_numpy(), np.linspace(0.5, 5.5, 11), rtol=1e-12)
    for method, order in (("nearest", 0), ("cubic", 3)):
        b = sdata.number_block(values, directions_named=["time", "latitude", "longitude"])
        b.change_size_to(longitude=12, test_method=method)
        np.testing.assert_allclose(b.as_numpy(), ndimage.zoom(values, (1, 1, 2), order=order), rtol=1e-12)


def test_rotate_by_degrees_equals_ndimage_rotate():
    values = np.nan_to_num(VALUES)
    block = sdata.number_block(values, directions_named=["time", "latitude", "longitude"],
                               with_labels={"latitude": LATS})
    block.rotate(by_degrees=20, over=["latitude", "longitude"])
    expected = ndimage.rotate(values, 20, axes=(2, 1), reshape=False, order=1, mode="constant", cval=np.nan)
    np.testing.assert_allclose(block.as_numpy(), expected, rtol=1e-12, equal_nan=True)
    np.testing.assert_array_equal(block.get_labels_of("latitude").as_numpy(), LATS)
    picture = sdata.number_block(np.arange(25.0).reshape(5, 5))
    picture.rotate(by_degrees=90)  # 90 degrees is the same quarter turn as np.rot90
    np.testing.assert_allclose(picture.as_numpy(), np.rot90(np.arange(25.0).reshape(5, 5)), atol=1e-9)
