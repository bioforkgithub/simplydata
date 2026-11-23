"""Six new words and five fixes (PR words-and-fixes, 2026-11-21), each checked against its reference.

Words: chart.get_numbers_drawn(), show_rows_that_pull_model() giving back a table, check_model_of(show="numbers"),
table.repeat_each_row_by(), sdata.get_example(..., from_r_package=) and find_correlation_between(show="result table").
Fixes (reference tests, FINDINGS A20 to A24): "in order" ANOVA p-values on the full model's residual df (R anova()),
fit_formula's trust region and dogbox to NIST-level digits, MASE on the seasonal scale (R forecast::accuracy with a
seasonal ts), of_degree= for Savitzky-Golay, and the separator of one-column CSV files.

The simplydata side uses simplydata words only; the reference side calls SciPy, statsmodels or R directly, or gives
the published (NIST) or R value.
"""

import math
from pathlib import Path

import numpy as np
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from conftest import example_frame

NIST = Path(__file__).resolve().parents[1] / "validation" / "data" / "nist"


# ---------------------------------------------------------------- A24 / A18: the separator of a CSV file
@pytest.mark.parametrize("header, values", [("species", ["Adelie", "Gentoo", "Chinstrap"]),
                                            ("difference", ["6.1", "-8.4", "1.0", "2.0", "0.7"]),
                                            ("species name", ["Adelie penguin", "Gentoo penguin"])])
def test_a_one_column_file_stays_one_column(header, values, tmp_path, capsys):
    # simplydata 0.2.x split these at a letter: "species" became the columns "sp", "cies" (sniffed "e")
    path = tmp_path / "one.csv"
    path.write_text("\n".join([header] + values) + "\n", encoding="utf-8")
    table = sdata.table(str(path))
    assert table.get_column_names() == [header]
    assert len(table) == len(values)
    out = capsys.readouterr().out
    assert 'Read "one.csv" with "," between the columns (guessed). To be sure, give separator=",".' in out


@pytest.mark.parametrize("text, separator, said", [("a;b\n1,5;2\n3,1;4\n", ";", '";"'),
                                                   ("a\tb\n1\t2\n3\t4\n", "\t", "a tab"),
                                                   ("a|b\n1|2\n3|4\n", "|", '"|"'),
                                                   ("a,b\n1,2\n3,4\n", ",", '","')])
def test_semicolon_tab_bar_and_comma_are_found(text, separator, said, tmp_path, capsys):
    path = tmp_path / "two.csv"
    path.write_text(text, encoding="utf-8")
    table = sdata.table(str(path))
    assert table.get_column_names() == ["a", "b"]
    assert len(table) == 2
    assert f"with {said} between the columns (guessed)" in capsys.readouterr().out


def test_no_guess_line_when_the_separator_is_given(tmp_path, capsys):
    path = tmp_path / "semi.csv"
    path.write_text("a;b\n1;2\n", encoding="utf-8")
    table = sdata.table(str(path), separator=";")
    assert table.get_column_names() == ["a", "b"]
    assert "guessed" not in capsys.readouterr().out
    path.write_text("species\nAdelie\nGentoo\n", encoding="utf-8")
    assert sdata.table(str(path), separator=",").get_column_names() == ["species"]
    assert "guessed" not in capsys.readouterr().out


def test_spaces_and_letters_are_never_guessed(tmp_path):
    path = tmp_path / "spaces.txt"
    path.write_text("a b c\n1 2 3\n4 5 6\n", encoding="utf-8")
    assert sdata.table(str(path)).get_column_names() == ["a b c"]  # read as one column: give separator=
    assert sdata.table(str(path), separator="space").get_column_names() == ["a", "b", "c"]


def test_a_wide_file_and_a_ragged_file_keep_their_separator(tmp_path, capsys):
    # review: a file wider than the 64 KB sample, and rows of different lengths, must not fall back to one column
    wide = tmp_path / "wide.csv"
    header = ";".join(f"column{i}" for i in range(3000))
    row = ";".join(str(i) for i in range(3000))
    wide.write_text("\n".join([header] + [row] * 8) + "\n", encoding="utf-8")
    assert len(sdata.table(str(wide)).get_column_names()) == 3000
    ragged = tmp_path / "ragged.csv"
    ragged.write_text("a;b;c\n1;2;3\n4;5\n6;7;8\n9\n", encoding="utf-8")
    assert sdata.table(str(ragged)).get_column_names() == ["a", "b", "c"]
    capsys.readouterr()


def test_a_folder_says_its_guess_once(tmp_path, capsys):
    for name in ("one.csv", "two.csv"):
        (tmp_path / name).write_text("species\nAdelie\n", encoding="utf-8")
    table = sdata.table(str(tmp_path))
    assert len(table) == 2
    out = capsys.readouterr().out
    assert out.count("(guessed)") == 1 and "Read the files with" in out


def test_the_fast_engine_guesses_the_same_way(tmp_path, capsys):
    pytest.importorskip("polars")
    path = tmp_path / "one.csv"
    path.write_text("species\nAdelie\nGentoo\n", encoding="utf-8")
    assert sdata.table(str(path), fast=True).get_column_names() == ["species"]
    assert "(guessed)" in capsys.readouterr().out


# ---------------------------------------------------------------- A23: Savitzky-Golay takes of_degree=
def test_savitzky_golay_takes_of_degree(capsys):
    from scipy.signal import savgol_filter

    sensor = example_frame("sensor")
    table = sdata.table(sensor)
    table.add_smoothed_column("smooth", from_column="signal", test_method="savitzky-golay", window=11, of_degree=3,
                              sorted_by="time")
    expected = savgol_filter(sensor.sort_values("time")["signal"].to_numpy(), 11, 3, mode="interp")
    assert list(table.sort_by("time").get_column("smooth")) == pytest.approx(expected, rel=1e-12)
    smoothed = sdata.numbers(sensor["signal"].tolist()).smooth(test_method="savitzky-golay", window=7, of_degree=4)
    assert list(smoothed) == pytest.approx(savgol_filter(sensor["signal"].to_numpy(), 7, 4, mode="interp"), rel=1e-12)
    capsys.readouterr()


def test_savitzky_golay_degree_is_an_old_name_with_a_note(capsys):
    sensor = example_frame("sensor")
    sdata.table(sensor).add_smoothed_column("s", from_column="signal", test_method="savitzky-golay", window=11,
                                            degree=2, sorted_by="time")
    assert '"degree=" is now called "of_degree="' in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="of_degree= needs a whole number from 0 to 6"):
        sdata.numbers(sensor["signal"].tolist()).smooth(test_method="savitzky-golay", window=7, of_degree=7)


# ---------------------------------------------------------------- A20: "in order" p-values on the full model's df
def test_in_order_p_values_use_the_full_models_residual_df(capsys):
    import statsmodels.formula.api as smf
    from statsmodels.stats.anova import anova_lm

    school = example_frame("school")
    result = sdata.table(school).explain("marks", using=["class * breakfast"], table_of_tests="in order")
    reference = anova_lm(smf.ols("marks ~ C(Q('class')) * C(breakfast)", data=school).fit(), typ=1)
    for term, row in (("class", 0), ("breakfast", 1), ("class : breakfast", 2)):
        found = sdata.table(result).keep_rows_where("term", is_equal_to=f"{term} (test, in order)")
        assert found.get_cell_at(row=1, column="statistic") == pytest.approx(reference["F"].iloc[row], rel=1e-9)
        assert found.get_cell_at(row=1, column="p-value") == pytest.approx(reference["PR(>F)"].iloc[row], rel=1e-9)
    capsys.readouterr()


def test_in_order_p_values_match_r_anova_on_moore(needs_r, capsys):
    # R: anova(lm(conformity ~ fcategory * partner.status, carData::Moore)): partner.status p 0.0028742 on 1 and 39 df
    # (simplydata before the fix: 0.0027934, F taken on 41 df)
    moore = sdata.get_example("Moore", from_r_package="carData")
    result = moore.explain("conformity", using=["fcategory * partner.status"], table_of_tests="in order")
    status = sdata.table(result).keep_rows_where("term", is_equal_to="partner.status (test, in order)")
    assert status.get_cell_at(row=1, column="p-value") == pytest.approx(0.0028742, rel=1e-4)
    first = sdata.table(result).keep_rows_where("term", is_equal_to="fcategory (test, in order)")
    assert first.get_cell_at(row=1, column="p-value") == pytest.approx(0.915010, rel=1e-5)
    capsys.readouterr()


# ---------------------------------------------------------------- A21: trust region and dogbox reach NIST digits
def _nist_data(name):
    lines = (NIST / f"{name}.dat").read_text().splitlines()
    start = max(i for i, line in enumerate(lines) if line.startswith("Data:")) + 1
    rows = [line.split() for line in lines[start:] if line.strip()]
    return sdata.table({"y": [float(r[0]) for r in rows], "x": [float(r[1]) for r in rows]})


def _lre(found, certified):
    return 15.0 if found == certified else -math.log10(abs(found - certified) / abs(certified))


@pytest.mark.parametrize("method", ["trust region", "dogbox"])
def test_misra1a_trust_region_and_dogbox_reach_nist_digits(method, capsys):
    # NIST StRD Misra1a, start 2; certified b1 238.94212918 (s.e. 2.7070075241), b2 0.00055015643181 (7.2668688436e-6).
    # Before the fix the standard errors agreed to 4.6 digits (default stopping rule, SciPy's default step); the
    # Levenberg-Marquardt default reaches 7.4.
    data = _nist_data("Misra1a")
    result = data.fit_formula("y = b1*(1-exp(-b2*x))", start={"b1": 250, "b2": 0.0005}, test_method=method)
    certified = {"b1": (2.3894212918e02, 2.7070075241e00), "b2": (5.5015643181e-04, 7.2668688436e-06)}
    for name, (estimate, error) in certified.items():
        assert _lre(result.get_cell_at(row=1, column=name), estimate) >= 8
        assert _lre(result.get_cell_at(row=1, column=f"standard error of {name}"), error) >= 8
    capsys.readouterr()


# NIST StRD Lanczos1 (public domain): y at x = 0, 0.05, ..., 1.15, generated to 14 digits from
# 0.0951 exp(-x) + 0.8607 exp(-3x) + 1.5576 exp(-5x); certified estimates and standard errors (start 2: 0.5, 0.7, 3.6,
# 4.2, 4, 6.3)
LANCZOS1_Y = [2.5134, 2.044333373291, 1.668404436564, 1.366418021208, 1.123232487372, 0.9268897180037,
              0.7679338563728, 0.6388775523106, 0.5337835317402, 0.4479363617347, 0.377584788435, 0.3197393199326,
              0.2720130773746, 0.2324965529032, 0.1996589546065, 0.1722704126914, 0.1493405660168, 0.1300700206922,
              0.1138119324644, 0.1000415587559, 0.0883320908454, 0.0783354401935, 0.06976693743449,
              0.06239312536719]
LANCZOS1 = {"b1": (9.5100000027e-02, 5.3347304234e-11), "b2": (1.0000000001e00, 2.7473038179e-10),
            "b3": (8.6070000013e-01, 1.3576062225e-10), "b4": (3.0000000002e00, 3.3308253069e-10),
            "b5": (1.5575999998e00, 1.8815731448e-10), "b6": (5.0000000001e00, 1.1057500538e-10)}


@pytest.mark.parametrize("method", ["trust region", "dogbox", "levenberg-marquardt"])
def test_lanczos1_standard_errors_stop_at_the_double_precision_limit(method, capsys):
    # The residual standard deviation is 8.9e-14: the residuals are the rounding of the generated y to 13 digits, and
    # evaluating the formula in double precision moves each of them by about 1e-16 (adding the three terms in another
    # order moves the residual SD in its 4th digit). So the residual SD, and every standard error with it, agree with
    # NIST to 3 to 3.6 digits with all three methods, while the estimates reach 10 (simplydata_tests notebook 27:
    # 3.34 and 3.57 on Ubuntu, 3.5 for the default method; FINDINGS B1). The values are SciPy curve_fit's.
    from scipy import optimize

    x = np.arange(24) * 0.05
    y = np.asarray(LANCZOS1_Y)
    start = {"b1": 0.5, "b2": 0.7, "b3": 3.6, "b4": 4.2, "b5": 4.0, "b6": 6.3}
    data = sdata.table({"y": LANCZOS1_Y, "x": list(x)})
    result = data.fit_formula("y = b1*exp(-b2*x) + b3*exp(-b4*x) + b5*exp(-b6*x)", start=start, test_method=method)
    for name, (estimate, error) in LANCZOS1.items():
        assert _lre(result.get_cell_at(row=1, column=name), estimate) >= 10
        assert _lre(result.get_cell_at(row=1, column=f"standard error of {name}"), error) >= 2.9
    # the package underneath, called with the options simplydata passes, gives the same numbers
    if method == "levenberg-marquardt":
        options = {"method": "lm", "maxfev": 20000, "xtol": 1e-12, "ftol": 1e-12}
    else:
        options = {"method": {"trust region": "trf", "dogbox": "dogbox"}[method], "max_nfev": 20000, "xtol": 1e-15,
                   "ftol": 1e-15, "gtol": 1e-15, "jac": "3-point", "diff_step": np.finfo(float).eps ** (1 / 3)}
    found, cov = optimize.curve_fit(lambda x, b1, b2, b3, b4, b5, b6: b1 * np.exp(-b2 * x) + b3 * np.exp(-b4 * x)
                                    + b5 * np.exp(-b6 * x), x, y, p0=list(start.values()), **options)
    for name, value, error in zip(start, found, np.sqrt(np.diag(cov))):
        assert result.get_cell_at(row=1, column=name) == pytest.approx(value, rel=1e-9)
        assert result.get_cell_at(row=1, column=f"standard error of {name}") == pytest.approx(error, rel=1e-2)
    capsys.readouterr()


# ---------------------------------------------------------------- A22: MASE on the seasonal scale
def test_compare_forecasts_scales_mase_by_the_same_season_last_time(needs_r, capsys):
    # R: y <- ts(co2[1:456], frequency = 12); f <- forecast(HoltWinters(y), 12)
    #    accuracy(f, ts(co2[457:468], frequency = 12, start = tsp(f$mean)[1]))["Test set", "MASE"] = 0.234367722222975
    #    (the last 24: 0.209385843216968). With the test as plain numbers, as simplydata did before: 0.277792180071110
    #    (the last 24: 0.245796499443924), the one-step naive scale.
    co2 = sdata.get_example("co2", from_r_package="datasets")
    for last, expected in ((12, 0.234367722222975), (24, 0.209385843216968)):
        result = co2.compare_forecasts_for("co2", sorted_by="time", repeats_every=12, check_on_last=last,
                                           test_method=["exponential smoothing", "same season last time"])
        smoothing = result.keep_rows_where("method", is_equal_to="exponential smoothing")
        assert smoothing.get_cell_at(row=1, column="MASE") == pytest.approx(expected, rel=1e-9)
    capsys.readouterr()


# ---------------------------------------------------------------- word 1: chart.get_numbers_drawn()
def test_numbers_drawn_gives_the_dots_and_the_fitted_line(capsys):
    import statsmodels.api as sm

    marks = example_frame("marks")
    chart = sdata.chart(marks).draw_dots(x="hours", y="marks").fit_line()
    drawn = chart.get_numbers_drawn()
    assert drawn.get_column_names() == ["panel", "layer", "kind", "series", "x", "y", "low", "high", "value"]
    out = capsys.readouterr().out
    assert out.startswith("Read ") and "1 group of dots" in out and "1 line" in out
    dots = sdata.table(drawn).keep_rows_where("kind", is_equal_to="dot")
    assert sorted(zip(dots.get_column("x"), dots.get_column("y"))) == sorted(zip(marks["hours"], marks["marks"]))
    line = sdata.table(drawn).keep_rows_where("kind", is_equal_to="line")
    fit = sm.OLS(marks["marks"], sm.add_constant(marks["hours"])).fit()
    xs = np.asarray(list(line.get_column("x")))
    assert list(line.get_column("y")) == pytest.approx(fit.params.iloc[0] + fit.params.iloc[1] * xs, rel=1e-9)
    banded = sdata.chart(marks).draw_dots(x="hours", y="marks").fit_line(with_confidence_band=True)
    band = banded.get_numbers_drawn().keep_rows_where("kind", is_equal_to="band")
    assert len(band) > 0
    assert all(low <= high for low, high in zip(band.get_column("low"), band.get_column("high")))


def test_numbers_drawn_names_the_bars_and_the_series(capsys):
    marks = example_frame("marks")
    drawn = sdata.chart(marks).draw_bars(x="class", y="marks").get_numbers_drawn()
    assert drawn.get_column("x") == ["A", "B", "C"]
    averages = marks.groupby("class")["marks"].mean()
    assert list(drawn.get_column("y")) == pytest.approx(averages.to_list(), rel=1e-12)
    drawn = sdata.chart(marks).draw_dots(x="hours", y="marks", colour="class").fit_line().get_numbers_drawn()
    lines = sdata.table(drawn).keep_rows_where("kind", is_equal_to="line")
    assert set(lines.get_column("series")) == {"A", "B", "C"}
    capsys.readouterr()


def test_numbers_drawn_reads_dates_cells_slices_and_error_bars(capsys):
    visitors = example_frame("visitors")
    drawn = sdata.chart(visitors).draw_lines(x="month", y="visitors", colour="museum").get_numbers_drawn()
    first = drawn.get_row(1)
    assert str(first["x"])[:10] == str(visitors["month"].min())[:10]
    weather = example_frame("weather")
    cells = sdata.chart(weather).draw_heatmap(x="month", y="city", value="rain").get_numbers_drawn()
    assert set(cells.get_column("kind")) == {"cell"}
    assert len(cells) == weather[["month", "city"]].drop_duplicates().shape[0]
    fruit = example_frame("fruit")
    pie = sdata.chart(fruit).draw_pie(labels="fruit", values="count").get_numbers_drawn()
    assert sum(pie.get_column("value")) == pytest.approx(1.0)
    errors = sdata.chart(sdata.get_example("marks")).draw_lines(x="subject", y="marks", colour="class")
    errors.draw_error_bars("standard error")
    kinds = set(errors.get_numbers_drawn().get_column("kind"))
    assert "error bar" in kinds
    empty = sdata.chart(sdata.get_example("marks")).get_numbers_drawn()
    assert len(empty) == 0
    assert "no drawn numbers yet" in capsys.readouterr().out


def test_numbers_drawn_on_a_page_and_on_parts(capsys):
    marks = example_frame("marks")
    page = sdata.put_side_by_side(sdata.chart(marks).draw_bars(x="class", y="marks"),
                                  sdata.chart(marks).draw_dots(x="hours", y="marks"))
    drawn = page.get_numbers_drawn()
    assert set(drawn.get_column("panel")) == {1, 2}
    pairs = sdata.draw_all_pairs(marks, columns=["hours", "marks"]).get_numbers_drawn()
    assert len(set(pairs.get_column("panel"))) == 4
    table = sdata.table(sdata.get_example("visitors"))
    table.keep_rows_where("museum", is_equal_to="Harbour Museum")
    parts = table.start_chart().trend_and_season(x="month", y="visitors", repeats_every="year").get_numbers_drawn()
    assert len(set(parts.get_column("panel"))) == 4
    capsys.readouterr()


def test_numbers_drawn_of_a_forecast_has_its_band(needs_r, capsys):
    visitors = example_frame("visitors")
    chart = sdata.chart(visitors).draw_lines(x="month", y="visitors", colour="museum")
    drawn = chart.forecast(steps_ahead=12, repeats_every="year").get_numbers_drawn()
    assert "band" in set(drawn.get_column("kind"))
    capsys.readouterr()


# ---------------------------------------------------------------- word 2: show_rows_that_pull_model() gives a table
@pytest.mark.parametrize("engine", ["pandas", "polars"])
def test_new_tables_work_on_both_engines(engine, capsys):
    if engine == "polars":
        pytest.importorskip("polars")
    data = sdata.table(sdata.get_example("school"), fast=engine == "polars")
    found = sdata.table(data).show_rows_that_pull_model("marks", using=["hours", "breakfast"])
    assert found.get_cell_at(row=1, column="row") == 48
    numbers = sdata.table(data).check_model_of("marks", using=["hours", "sleep"], show="numbers")
    assert len(numbers) == 5
    result = sdata.table(data).find_correlation_between("hours", "marks", show="result table")
    assert len(result) == 1
    capsys.readouterr()


def test_rows_that_pull_come_back_as_a_table(capsys):
    import statsmodels.api as sm
    from statsmodels.stats.outliers_influence import OLSInfluence

    school = example_frame("school")
    found = sdata.table(school).show_rows_that_pull_model("marks", using=["hours", "breakfast"])
    assert found.get_column_names() == ["row", "Cook's distance", "leverage", "studentised residual"]
    used = school.dropna(subset=["marks", "hours", "breakfast"])
    X = sm.add_constant(np.column_stack([used["hours"], (used["breakfast"] == "yes").astype(float)]))
    influence = OLSInfluence(sm.OLS(used["marks"].to_numpy(), X).fit())
    cooks = influence.cooks_distance[0]
    above = np.sort(cooks[cooks > 4 / len(used)])[::-1]
    assert list(found.get_column("Cook's distance")) == pytest.approx(above, rel=1e-9)
    assert found.get_cell_at(row=1, column="row") == 48  # R: which.max(cooks.distance(m)) on the whole table
    out = capsys.readouterr().out
    assert "Gives back a table of the" in out


def test_groups_that_pull_come_back_as_a_table(needs_r, capsys):
    school = sdata.table(sdata.get_example("school"))
    found = school.show_rows_that_pull_model("marks", using=["hours", "breakfast"], grouped_by="school")
    assert found.get_column_names() == ["school", "rows", "Cook's distance"]
    capsys.readouterr()


# ---------------------------------------------------------------- word 3: check_model_of(show="numbers")
def test_check_numbers_are_the_printed_tests(capsys):
    import statsmodels.api as sm
    from statsmodels.stats.diagnostic import het_breuschpagan

    school = example_frame("school")
    numbers = sdata.table(school).check_model_of("marks", using=["hours", "sleep"], show="numbers")
    assert numbers.get_column_names() == ["check", "term", "value", "df", "p-value"]
    used = school.dropna(subset=["marks", "hours", "sleep"])
    X = sm.add_constant(used[["hours", "sleep"]].to_numpy())
    fit = sm.OLS(used["marks"].to_numpy(), X).fit()
    bp, bp_p, _, _ = het_breuschpagan(fit.resid, X, robust=True)
    row = sdata.table(numbers).keep_rows_where("check", is_equal_to="Breusch-Pagan test (chi-square)")
    assert row.get_cell_at(row=1, column="value") == pytest.approx(bp, rel=1e-9)
    assert row.get_cell_at(row=1, column="p-value") == pytest.approx(bp_p, rel=1e-9)
    vif = sdata.table(numbers).keep_rows_where("check", is_equal_to="variance inflation factor")
    assert vif.get_column("term") == ["hours", "sleep"]
    capsys.readouterr()


def test_check_numbers_refuses_mixed_models_and_unknown_choices():
    school = sdata.table(sdata.get_example("school"))
    with pytest.raises(SimplydataError, match="pictures only"):
        school.check_model_of("marks", using=["hours"], grouped_by="school", show="numbers")
    with pytest.raises(SimplydataError, match="prior check"):
        school.check_model_of("marks", using=["hours"], show="prior check")


# ---------------------------------------------------------------- word 4: table.repeat_each_row_by()
@pytest.mark.parametrize("engine", ["pandas", "polars"])
def test_repeat_each_row_by_count(engine, capsys):
    data = {"answer": ["yes", "no", "maybe"], "count": [12, 5, 0]}
    if engine == "polars":
        pl = pytest.importorskip("polars")
        data = pl.DataFrame(data)
    table = sdata.table(data)
    table.repeat_each_row_by("count")
    assert table.get_column_names() == ["answer"]
    assert table.get_column("answer") == ["yes"] * 12 + ["no"] * 5
    out = capsys.readouterr().out
    assert 'Repeated 3 rows into 17 rows by "count".' in out
    assert 'The column "count" is left out' in out and "1 row with a count of 0 is left out" in out
    table.undo()
    assert table.get_column_names() == ["answer", "count"]


@pytest.mark.parametrize("counts, message", [([1.5, 2], "not a whole number"), ([-1, 2], "below 0"),
                                             ([None, 2], "1 empty cell"), (["a", "b"], "holds text")])
def test_repeat_each_row_by_refuses_bad_counts(counts, message):
    with pytest.raises(SimplydataError, match=message):
        sdata.table({"answer": ["yes", "no"], "count": counts}).repeat_each_row_by("count")


# ---------------------------------------------------------------- word 5: get_example(from_r_package=)
def test_get_example_from_an_r_package(needs_r, capsys):
    mtcars = sdata.get_example("mtcars", from_r_package="datasets")
    assert mtcars.get_column_names()[:2] == ["row name", "mpg"]
    assert mtcars.get_cell_at(row=1, column="row name") == "Mazda RX4"
    lung = sdata.get_example("lung", from_r_package="survival")  # kept in the data file "cancer"
    assert len(lung) == 228
    moore = sdata.get_example("Moore", from_r_package="carData")
    assert moore.get_cell_at(row=1, column="partner.status") == "low"  # a factor became text
    out = capsys.readouterr().out
    assert 'Loaded "lung" from the R package survival: 228 rows, 10 columns' in out
    with pytest.raises(SimplydataError, match='Did you mean sdata.get_example\\("lung", from_r_package="survival"\\)'):
        sdata.get_example("lunk", from_r_package="survival")
    with pytest.raises(SimplydataError, match="is not installed.*never installs"):
        sdata.get_example("lung", from_r_package="noSuchPackageHere")


def test_get_example_from_r_package_checks_the_name():
    with pytest.raises(SimplydataError, match="name of an installed R package"):
        sdata.get_example("lung", from_r_package="survival; q()")


# ---------------------------------------------------------------- word 6: find_correlation_between(show="result table")
def test_correlation_result_table_for_two_columns(capsys):
    from scipy import stats

    marks = example_frame("marks")
    result = sdata.table(marks).find_correlation_between("hours", "marks", show="result table")
    assert result.get_column_names() == ["column 1", "column 2", "method", "r", "95 % CI low", "95 % CI high",
                                         "interval from", "p-value", "p-value from", "tested", "rows", "strength"]
    reference = stats.pearsonr(marks["hours"], marks["marks"])
    ci = reference.confidence_interval(0.95)
    row = result.get_row(1)
    assert row["r"] == pytest.approx(reference.statistic, rel=1e-12)
    assert row["p-value"] == pytest.approx(reference.pvalue, rel=1e-9)
    assert (row["95 % CI low"], row["95 % CI high"]) == pytest.approx((ci.low, ci.high), rel=1e-12)
    assert row["rows"] == 54 and row["p-value from"] == "formula" and row["tested"] == "both directions"
    shuffled = sdata.table(marks).find_correlation_between("hours", "marks", show="result table", p_value_by="shuffling",
                                                           interval_by="bootstrap", shuffles=999, resamples=999)
    assert shuffled.get_cell_at(row=1, column="p-value from") == "shuffling"
    assert shuffled.get_cell_at(row=1, column="interval from") == "bootstrap (BCa)"
    capsys.readouterr()


def test_correlation_result_table_for_three_columns_is_each_pair(capsys):
    table = sdata.table(sdata.get_example("marks"))
    result = table.find_correlation_between("hours", "marks", "height", show="result table")
    assert len(result) == 3 and "column 1" in result.get_column_names()
    capsys.readouterr()


# ---------------------------------------------------------------- four more options (approved 2026-11-22)
def test_survival_show_median_gives_the_printed_medians(capsys):
    from statsmodels.duration.survfunc import SurvfuncRight

    trial = example_frame("trial")
    medians = sdata.table(trial).find_survival_over_time(time="days", event="died", for_each_group_in="treatment",
                                                         show="median")
    assert medians.get_column_names() == ["treatment", "rows", "events", "median", "95 % CI low", "95 % CI high"]
    for i, group in enumerate(medians.get_column("treatment"), start=1):
        rows = trial[trial["treatment"] == group]
        fit = SurvfuncRight(rows["days"], (rows["died"] == "yes").astype(float))
        assert medians.get_cell_at(row=i, column="median") == pytest.approx(fit.quantile(0.5), rel=1e-12)
        assert medians.get_cell_at(row=i, column="rows") == len(rows)
    assert 'show="median"' in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="leave out"):
        sdata.table(trial).find_survival_over_time(time="days", event="died", at_time_points=[365], show="median")


def test_survival_show_median_matches_r(needs_r, capsys):
    from simplydata._r import r_call

    trial = example_frame("trial")
    medians = sdata.table(trial).find_survival_over_time(time="days", event="died", for_each_group_in="treatment",
                                                         show="median")
    groups = medians.get_column("treatment")
    r = r_call("t <- summary(survival::survfit(survival::Surv(days, died == 'yes') ~ treatment))$table; "
               "list(median = t[, 'median'], low = t[, '0.95LCL'], high = t[, '0.95UCL'], "
               "names = sub('treatment=', '', rownames(t)))", packages=("survival",),
               days=trial["days"].to_numpy(dtype=float), died=trial["died"].to_numpy(dtype=str),
               treatment=trial["treatment"].to_numpy(dtype=str))
    for name, median, low, high in zip(r["names"], r["median"], r["low"], r["high"]):
        row = groups.index(str(name)) + 1
        for column, expected in (("median", median), ("95 % CI low", low), ("95 % CI high", high)):
            got = medians.get_cell_at(row=row, column=column)
            assert (got is None and np.isnan(expected)) or got == pytest.approx(float(expected), rel=1e-9)
    capsys.readouterr()


def test_fit_formula_note_says_converged_and_the_warnings(capsys):
    data = _nist_data("Misra1a")
    good = data.fit_formula("y = b1*(1-exp(-b2*x))", start={"b1": 250, "b2": 0.0005})
    assert good.get_cell_at(row=1, column="note") == "converged"
    # NIST BoxBOD from its far start 1: the search stops in a flat region (FINDINGS A2), and the note says so
    bad = _nist_data("BoxBOD").fit_formula("y = b1*(1-exp(-b2*x))", start={"b1": 1, "b2": 1})
    note = bad.get_cell_at(row=1, column="note")
    assert note.startswith("did not converge; ") and "flat region" in note
    capsys.readouterr()


def test_nmds_show_numbers_matches_vegan(needs_r, capsys):
    from simplydata._r import r_call

    meadow = example_frame("meadow")
    species = ["clover", "daisy", "buttercup", "dandelion", "nettle", "thistle", "moss", "fern", "orchid", "yarrow"]
    numbers = sdata.table(meadow).add_nmds(columns=species, show="numbers")
    assert numbers.get_column_names() == ["row", "NMDS1", "NMDS2", "stress"]
    assert list(numbers.get_column("row")) == list(range(1, len(meadow) + 1))
    stress = r_call("set.seed(1); f <- vegan::metaMDS(vegan::vegdist(x, method = 'bray'), k = 2, try = 20, "
                    "trymax = 100, autotransform = FALSE, trace = 0); f$stress", packages=("vegan",),
                    x=meadow[species].to_numpy(dtype=float))
    assert numbers.get_cell_at(row=1, column="stress") == pytest.approx(float(np.atleast_1d(stress)[0]), rel=1e-9)
    added = sdata.table(meadow).add_nmds(columns=species)
    assert list(added.get_column("NMDS1")) == pytest.approx(list(numbers.get_column("NMDS1")), rel=1e-12)
    capsys.readouterr()


def test_correspondence_show_numbers_matches_vegan(needs_r, capsys):
    from simplydata._r import r_call

    genes = ["blaTEM", "blaCTXM", "sul1", "sul2", "tetA", "tetM"]
    resistome = example_frame("resistome")
    numbers = sdata.table(resistome).add_correspondence_axes(columns=genes, show="numbers")
    assert numbers.get_column_names() == ["row", "CA1", "CA2", "CA1 eigenvalue", "CA2 eigenvalue",
                                          "CA1 share of the inertia", "CA2 share of the inertia", "total inertia"]
    share = r_call("summary(vegan::eigenvals(vegan::cca(x)))[2, 1:2]", packages=("vegan",),
                   x=resistome[genes].to_numpy(dtype=float))
    assert numbers.get_cell_at(row=1, column="CA1 share of the inertia") == pytest.approx(float(share[0]), rel=1e-9)
    assert numbers.get_cell_at(row=1, column="CA2 share of the inertia") == pytest.approx(float(share[1]), rel=1e-9)
    capsys.readouterr()
