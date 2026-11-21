"""S3c-3, directions, places and extremes: find_average_direction_of, the Rayleigh test (compare_shape_to with
full_turn=), Moran's I (find_autocorrelation_of with x= and y=), find_variogram_of, find_return_levels_of, the GEV and
generalised Pareto families, draw_variogram, draw_threshold_check and draw_polar(full_turn=).

The numbers are checked against the packages underneath (SciPy here; R in the tests marked needs_r, and in the
reliability study on published data). Permutation p-values are only checked where they sit at their floor.
"""

import math

import numpy as np
import pandas as pd
import pytest
from scipy import stats

import simplydata as sdata
from simplydata import SimplydataError


def _table(name):
    return sdata.table(sdata.get_example(name))


def _r(code):
    from simplydata._r import r_call

    return r_call(code, packages=())


# ---------------------------------------------------------------- practice tables
def test_stations_and_rain_are_made_up_and_say_so():
    from simplydata.data import EXAMPLES

    for name in ("stations", "rain"):
        assert EXAMPLES[name][0].startswith("MADE-UP DATA")
    frame = sdata.get_example("stations")
    assert len(frame) == 60 and frame["station"].is_unique
    assert {"east", "north", "lon", "lat", "depth", "current_direction", "zinc"} <= set(frame.columns)
    assert frame["current_direction"].between(0, 359).all()
    assert len(sdata.get_example("rain")) == 3653


def test_sea_levels_are_the_published_port_pirie_series():
    from simplydata.data import EXAMPLES

    assert EXAMPLES["sea_levels"][0].startswith("REAL DATA") and "Coles" in EXAMPLES["sea_levels"][0]
    frame = sdata.get_example("sea_levels")
    assert len(frame) == 65 and frame["year"].tolist() == list(range(1923, 1988))
    assert frame["sea_level"].iloc[:4].tolist() == [4.03, 3.83, 3.65, 3.88]


# ---------------------------------------------------------------- AC01: circular summaries
def test_average_direction_is_scipys_circular_mean(capsys):
    result = _table("stations").find_average_direction_of("current_direction", full_turn=360).as_pandas()
    d = sdata.get_example("stations")["current_direction"].to_numpy(dtype=float)
    assert result["average direction"][0] == pytest.approx(stats.circmean(d, high=360, low=0), rel=1e-12)
    assert result["circular standard deviation"][0] == pytest.approx(stats.circstd(d, high=360, low=0), rel=1e-12)
    assert result["resultant length"][0] == pytest.approx(1 - stats.circvar(d, high=360, low=0), rel=1e-9)
    out = capsys.readouterr().out
    assert "354°" in out and "close together" in out and "clustered" not in out


def test_350_and_10_average_to_north_not_south():
    table = sdata.table(pd.DataFrame({"heading": [350.0, 10.0]}))
    result = table.find_average_direction_of("heading", full_turn=360).as_pandas()
    assert min(result["average direction"][0], 360 - result["average direction"][0]) == pytest.approx(0, abs=1e-9)


def test_full_turn_is_required_and_understood():
    table = _table("stations")
    with pytest.raises(SimplydataError, match="needs full_turn="):
        table.find_average_direction_of("current_direction")
    with pytest.raises(SimplydataError, match="full_turn"):
        table.find_average_direction_of("current_direction", full_turn=-1)
    hours = sdata.table(pd.DataFrame({"hour": [23.0, 1.0, 0.5, 23.5]}))
    result = hours.find_average_direction_of("hour", full_turn=24).as_pandas()
    assert min(result["average direction"][0], 24 - result["average direction"][0]) == pytest.approx(0, abs=1e-9)
    radians = sdata.table(pd.DataFrame({"angle": [0.1, 0.2, 6.2]}))
    by_name = radians.find_average_direction_of("angle", full_turn="radians").as_pandas()
    by_number = radians.find_average_direction_of("angle", full_turn=2 * math.pi).as_pandas()
    assert by_name["average direction"][0] == pytest.approx(by_number["average direction"][0])


def test_values_outside_the_turn_get_a_note_and_groups_work(capsys):
    table = sdata.table(pd.DataFrame({"d": [370.0, 20, 15, 180, 190, 170], "g": ["a", "a", "a", "b", "b", "b"]}))
    result = table.find_average_direction_of("d", full_turn=360, for_each_group_in="g").as_pandas()
    out = capsys.readouterr().out
    assert "outside 0 to 360" in out
    assert result["average direction"].tolist() == pytest.approx([15.0, 180.0], abs=1e-9)


def test_the_average_is_below_the_full_turn():
    table = sdata.table(pd.DataFrame({"h": [23.0, 1.0, 2.0, 22.0]}))
    result = table.find_average_direction_of("h", full_turn=24).as_pandas()
    assert 0 <= result["average direction"][0] < 24


def test_a_flat_spread_says_there_is_no_clear_direction(capsys):
    table = sdata.table(pd.DataFrame({"d": [0.0, 90, 180, 270]}))
    table.find_average_direction_of("d", full_turn=360)
    assert "no clear average direction" in capsys.readouterr().out


def test_find_average_of_warns_on_a_direction_column(capsys):
    _table("stations").find_average_of("current_direction")
    assert "find_average_direction_of" in capsys.readouterr().out


# ---------------------------------------------------------------- AC02: Rayleigh
def test_rayleigh_is_r_circular(needs_r, capsys):
    table = _table("stations")
    result = table.compare_shape_to("current_direction", shape="even around the circle", full_turn=360).as_pandas()
    from simplydata._r import r_call

    found = r_call('r <- circular::rayleigh.test(circular::circular(x, units = "degrees", template = "none")); '
                   "c(r$statistic, r$p.value)", packages=(),
                   x=sdata.get_example("stations")["current_direction"].to_numpy(dtype=float))
    assert result["statistic"][0] == pytest.approx(found[0], rel=1e-12)
    assert result["p-value"][0] == pytest.approx(found[1], rel=1e-9)
    out = capsys.readouterr().out
    assert "If the directions were spread evenly around the circle" in out and 'units = "degrees"' in out
    again = table.compare_shape_to("current_direction", test="rayleigh", full_turn=360).as_pandas()
    assert again["p-value"][0] == result["p-value"][0]
    default = table.compare_shape_to("current_direction", full_turn=360).as_pandas()  # Rayleigh with full_turn=
    assert default["p-value"][0] == result["p-value"][0]


def test_rayleigh_on_hours_matches_degrees(needs_r):
    hours = [22.0, 23.0, 1.0, 2.0, 0.5, 3.0, 21.5]
    a = sdata.table(pd.DataFrame({"h": hours})).compare_shape_to("h", shape="even around the circle", full_turn=24)
    b = sdata.table(pd.DataFrame({"h": [v * 15 for v in hours]})).compare_shape_to(
        "h", shape="even around the circle", full_turn=360)
    assert a.as_pandas()["p-value"][0] == pytest.approx(b.as_pandas()["p-value"][0], rel=1e-9)


def test_rayleigh_refusals():
    table = _table("stations")
    with pytest.raises(SimplydataError, match="needs full_turn="):
        table.compare_shape_to("current_direction", shape="even around the circle")
    with pytest.raises(SimplydataError, match="a shape on a line"):
        table.compare_shape_to("current_direction", sdata.distribution("normal"), full_turn=360)
    with pytest.raises(SimplydataError, match="not offered there"):
        table.compare_shape_to("current_direction", shape="von mises", full_turn=360)
    few = sdata.table(pd.DataFrame({"d": [1.0, 2, 3, 4]}))
    with pytest.raises(SimplydataError, match="at least 5"):
        few.compare_shape_to("d", shape="even around the circle", full_turn=360)


def test_uniform_on_a_direction_column_gets_a_note(capsys):
    # without full_turn= the line test of "uniform" still runs; the note comes first
    _table("stations").compare_shape_to("current_direction", shape="uniform", samples=99)
    assert "looks like directions" in capsys.readouterr().out


# ---------------------------------------------------------------- AC08: Moran's I
def test_moran_refusals_need_no_r():
    table = _table("stations")
    with pytest.raises(SimplydataError, match="not both"):
        table.find_autocorrelation_of("zinc", x="east", y="north", sorted_by="depth")
    with pytest.raises(SimplydataError, match="both x= and y="):
        table.find_autocorrelation_of("zinc", x="east")
    with pytest.raises(SimplydataError, match="at most 59"):
        table.find_autocorrelation_of("zinc", x="east", y="north", nearest=60)
    with pytest.raises(SimplydataError, match="longitude"):
        table.find_autocorrelation_of("zinc", x="east", y="north", on_globe=True)
    same = sdata.table(pd.DataFrame({"e": [0.0, 0, 1, 2, 3, 4], "n": [0.0, 0, 1, 2, 3, 5], "z": [1.0, 2, 3, 4, 5, 6]}))
    with pytest.raises(SimplydataError, match='find_average_of\\("z", for_each_group_in=\\["e", "n"\\]\\)'):
        same.find_autocorrelation_of("z", x="e", y="n")
    with pytest.raises(SimplydataError, match="permutations= and with_seed="):
        table.find_autocorrelation_of("zinc", sorted_by="depth", permutations=99)


def test_moran_is_spdeps_on_meuse(needs_r, capsys):
    found = _r('e <- new.env(); utils::data("meuse", package = "sp", envir = e); '
               "list(x = e$meuse$x, y = e$meuse$y, z = log(e$meuse$zinc))")
    table = sdata.table(pd.DataFrame({"east": found["x"], "north": found["y"], "log_zinc": found["z"]}))
    result = table.find_autocorrelation_of("log_zinc", x="east", y="north").as_pandas()
    assert result["Moran's I"][0] == pytest.approx(0.1191262, abs=5e-7)  # the same as ape::Moran.I (design AC08)
    assert result["p-value"][0] == pytest.approx(0.001)
    out = capsys.readouterr().out
    assert "1 / distance" in out and "at most about 1 of 1000" in out
    k8 = table.find_autocorrelation_of("log_zinc", x="east", y="north", nearest=8).as_pandas()
    assert k8["Moran's I"][0] == pytest.approx(0.4896063, abs=5e-7)
    assert "8 nearest" in capsys.readouterr().out


def test_moran_on_the_globe_and_the_lon_lat_note(needs_r, capsys):
    table = _table("stations")
    table.find_autocorrelation_of("zinc", x="lon", y="lat")
    assert "look like longitude and latitude" in capsys.readouterr().out
    table.find_autocorrelation_of("zinc", x="lon", y="lat", on_globe=True)
    out = capsys.readouterr().out
    assert "crs = 4326" in out and "look like longitude" not in out


# ---------------------------------------------------------------- AC09: variogram
def test_variogram_is_gstats_on_meuse(needs_r, capsys):
    found = _r('e <- new.env(); utils::data("meuse", package = "sp", envir = e); '
               "list(x = e$meuse$x, y = e$meuse$y, z = log(e$meuse$zinc))")
    table = sdata.table(pd.DataFrame({"east": found["x"], "north": found["y"], "log_zinc": found["z"]}))
    result = table.find_variogram_of("log_zinc", x="east", y="north").as_pandas()
    # the gstat vignette's spherical fit: nugget 0.0507, partial sill 0.5906, range 897
    assert result["nugget"][0] == pytest.approx(0.0507, abs=5e-4)
    assert result["partial sill"][0] == pytest.approx(0.5906, abs=5e-4)
    assert result["range"][0] == pytest.approx(897.0, abs=0.5)
    assert len(result) == 15
    out = capsys.readouterr().out
    assert "become unrelated beyond about 897" in out
    table.find_variogram_of("log_zinc", x="east", y="north", of_kind="exponential")
    assert "three times the range parameter 450" in capsys.readouterr().out


def test_variogram_refusals():
    table = _table("stations")
    with pytest.raises(SimplydataError, match="of_kind"):
        table.find_variogram_of("zinc", x="east", y="north", of_kind="wavy")
    with pytest.raises(SimplydataError, match="from 0"):
        table.find_variogram_of("zinc", x="east", y="north", between=[100, 1500])


# ---------------------------------------------------------------- AB07 / AB08: return levels
def test_port_pirie_return_levels_are_extremes(needs_r, capsys):
    result = _table("sea_levels").find_return_levels_of("sea_level", once_in=[10, 100], sorted_by="year").as_pandas()
    # Coles (2001) 3.4.1 and extRemes: 10-year 4.30, 100-year 4.69; profile interval of the 100-year level 4.49 to 5.26
    assert result["level"].tolist() == pytest.approx([4.296212, 4.688404], abs=5e-6)
    assert result["95 % CI low"][1] == pytest.approx(4.495, abs=0.003)
    assert result["95 % CI high"][1] == pytest.approx(5.257, abs=0.003)
    assert result["normal 95 % CI low"][1] == pytest.approx(4.377125, abs=5e-6)
    assert (result["interval"] == "profile likelihood").all()
    out = capsys.readouterr().out
    assert "A level of 4.69 is reached on average once in 100 years (a 1-in-100 chance in any one year)" in out
    assert "Shape xi = -0.050" in out and "c = -xi" in out


def test_return_level_refusals_need_no_r():
    rain = _table("rain")
    rain.turn_into_dates("date")
    with pytest.raises(SimplydataError, match="several rows per year"):
        rain.find_return_levels_of("rain", sorted_by="date")
    with pytest.raises(SimplydataError, match="needs sorted_by="):
        rain.find_return_levels_of("rain", values_above=20)
    with pytest.raises(SimplydataError, match="above 1"):
        _table("sea_levels").find_return_levels_of("sea_level", once_in=[1, 10])
    with pytest.raises(SimplydataError, match="dates"):
        _table("sea_levels").find_return_levels_of("sea_level", values_above=4, sorted_by="year")
    repeated = sdata.table(pd.DataFrame({"year": [2000, 2000, 2001, 2002, 2003, 2004], "v": [1.0, 2, 3, 4, 5, 6]}))
    with pytest.raises(SimplydataError, match="several rows per year"):
        repeated.find_return_levels_of("v", sorted_by="year")


def test_yearly_maxima_with_their_dates_are_block_maxima(needs_r):
    frame = sdata.get_example("sea_levels")
    rng = np.random.default_rng(5)
    days = pd.to_datetime([f"{y}-01-01" for y in frame["year"]]) + pd.to_timedelta(rng.integers(0, 365, len(frame)),
                                                                                    unit="D")
    dated = sdata.table(pd.DataFrame({"date": days, "sea_level": frame["sea_level"]}))
    result = dated.find_return_levels_of("sea_level", once_in=[10], sorted_by="date").as_pandas()
    assert result["level"][0] == pytest.approx(4.296212, abs=5e-6)
    assert result["time unit"][0] == "years"


def test_moran_says_less_alike_only_when_the_test_says_so(needs_r, capsys):
    rng = np.random.default_rng(2)
    grid = pd.DataFrame({"e": np.repeat(np.arange(8.0), 8), "n": np.tile(np.arange(8.0), 8)})
    flat = grid.assign(v=grid["e"] * 0 + rng.normal(size=len(grid)))
    sdata.table(flat).find_autocorrelation_of("v", x="e", y="n")
    out = capsys.readouterr().out
    assert ("less alike" not in out) or ('alternative = "less"' in out)
    checker = grid.assign(v=np.where((grid["e"] + grid["n"]) % 2 == 0, 1.0, -1.0) + rng.normal(0, 0.1, len(grid)))
    sdata.table(checker).find_autocorrelation_of("v", x="e", y="n", nearest=4)
    assert "less alike" in capsys.readouterr().out


def test_values_above_a_threshold(needs_r, capsys):
    rain = _table("rain")
    rain.turn_into_dates("date")
    result = rain.find_return_levels_of("rain", once_in=[10], values_above=20, sorted_by="date").as_pandas()
    x = sdata.get_example("rain")["rain"].to_numpy(dtype=float)
    from simplydata._r import r_call

    found = r_call("f <- extRemes::fevd(x, threshold = 20, type = 'GP', time.units = 'days'); "
                   "as.numeric(extRemes::return.level(f, return.period = 10))", packages=(), x=x)
    assert result["level"][0] == pytest.approx(float(np.atleast_1d(found)[0]), rel=1e-9)
    out = capsys.readouterr().out
    assert "extremal index" in out and "genpareto uses the same sign" in out


# ---------------------------------------------------------------- the new distribution families
def test_gev_fit_keeps_xi_and_matches_scipy_with_c_turned_round():
    fit = _table("sea_levels").fit_distribution_to("sea_level", "gev")
    shape = fit.turn_into_table().as_pandas()["shape"][0]
    assert shape == pytest.approx(-0.0501095, abs=2e-5)  # extRemes / Coles: xi = -0.050
    x = sdata.get_example("sea_levels")["sea_level"].to_numpy(dtype=float)
    c, loc, scale = stats.genextreme.fit(x)
    assert -c == pytest.approx(shape, abs=2e-3)
    assert fit.find_percentile(99) == pytest.approx(
        stats.genextreme(c=-shape, loc=fit.turn_into_table().as_pandas()["location"][0],
                         scale=fit.turn_into_table().as_pandas()["scale"][0]).ppf(0.99), rel=1e-9)
    assert "extRemes::devd" in repr(fit) and 'type = "GEV"' in repr(fit)


def test_pareto_points_to_the_generalised_pareto():
    assert "generalised pareto" in repr(sdata.distribution("pareto", shape=3, scale=2))


def test_generalised_pareto_has_scipys_sign():
    rng = np.random.default_rng(3)
    x = stats.genpareto(c=0.2, scale=5).rvs(size=400, random_state=rng)
    fit = sdata.numbers(list(x)).fit_distribution("generalized pareto")
    table = fit.turn_into_table().as_pandas()
    c, _, scale = stats.genpareto.fit(x, floc=0)
    assert table["shape"][0] == pytest.approx(c, abs=2e-3)
    assert table["scale"][0] == pytest.approx(scale, rel=2e-3)
    assert sdata.distribution("gpd", scale=5, shape=0.2).find_percentile(90) == pytest.approx(
        stats.genpareto(c=0.2, scale=5).ppf(0.9))


# ---------------------------------------------------------------- charts
def test_draw_polar_full_turn_is_a_compass():
    frame = pd.DataFrame({"hour": [0.0, 6, 12], "n": [1.0, 2, 3]})
    ax = sdata.chart(frame).draw_polar(angle="hour", distance="n", full_turn=24)._render().axes[0]
    assert np.allclose(ax.collections[0].get_offsets()[:, 0], [0, np.pi / 2, np.pi])
    assert ax.get_theta_direction() == -1 and ax.get_theta_offset() == pytest.approx(np.pi / 2)
    maths = sdata.chart(pd.DataFrame({"angle": [0.0, 90], "n": [1.0, 2]})).draw_polar(angle="angle", distance="n")
    assert maths._render().axes[0].get_theta_direction() == 1
    wind = sdata.chart(sdata.get_example("weather")).draw_polar(angle="wind_direction", distance="wind_speed")
    assert wind._render().axes[0].get_theta_direction() == -1


def test_draw_variogram_and_threshold_check(needs_r):
    chart = sdata.chart(sdata.get_example("stations")).draw_variogram("zinc", x="east", y="north")
    ax = chart._render().axes[0]
    assert len(ax.collections[0].get_offsets()) == 15 and len(ax.get_lines()[0].get_xdata()) == 200
    check = sdata.chart(sdata.get_example("rain")).draw_threshold_check(x="rain", between=[10, 30])
    fig = check._render()
    top, bottom = fig.axes[0].child_axes
    assert top.get_ylabel() == "Mean excess" and bottom.get_ylabel() == "Shape (xi)"
    assert min(top.get_lines()[0].get_xdata()) >= 10 and max(top.get_lines()[0].get_xdata()) <= 30


def test_chart_refusals():
    with pytest.raises(SimplydataError, match="between="):
        sdata.chart(sdata.get_example("rain")).draw_threshold_check(x="rain")
    with pytest.raises(SimplydataError, match="too few"):
        sdata.chart(sdata.get_example("rain")).draw_threshold_check(x="rain", between=[10, 500])
    with pytest.raises(SimplydataError, match="x= and y="):
        sdata.chart(sdata.get_example("stations")).draw_variogram("zinc")
