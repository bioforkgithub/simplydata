"""Three small additions (branch three-words, approved by Manish 2026-11-23), each against its reference on real data.

* add_correspondence_axes(show="numbers") also gives each axis's eigenvalue and the total inertia: R vegan::cca on
  vegan's varespec, against the values Oksanen's vegan tutorial prints (0.5249, 0.3568 of 2.083) and R itself.
* find_correlation_between(allowing_for=, show="result table") gives the partial correlation as a one-row table:
  R ppcor::pcor.test on R's mtcars (mpg and wt, allowing for hp).
* trade_off_curve: chart.get_numbers_drawn() gives the best cut-off (Youden) in the value column of the marked dot,
  with the sensitivity (y) and 1 - specificity (x) there: R pROC::coords(roc, "best") on pROC's aSAH (s100b).

The pinned values were run on R 4.6.2 with vegan 2.7.6, ppcor 1.1 and pROC 1.19.1 (2026-11-23); each test also
runs R again where it is installed. The simplydata side uses simplydata words only.
"""

import numpy as np
import pytest

import simplydata as sdata
from simplydata import SimplydataError

# R 4.6.2, vegan 2.7.6: summary(eigenvals(cca(varespec)))[1:2, 1:2] and cca(varespec)$tot.chi
VARESPEC_EIGENVALUES = (0.52493199428049542, 0.35679802308395392)
VARESPEC_SHARES = (0.25198369129421067, 0.17127415338134275)
VARESPEC_TOTAL = 2.0831982878907676
# R 4.6.2, ppcor 1.1: pcor.test(mtcars$mpg, mtcars$wt, mtcars$hp) and the same with method = "spearman"
MTCARS_PARTIAL = {"pearson": (-0.75120490496186532, -6.1286952198104219, 1.1196471362000158e-06, 32),
                  "spearman": (-0.68441516084191023, -5.0551725452053331, 2.1759527159892452e-05, 32)}
# R 4.6.2, pROC 1.19.1: coords(roc(aSAH$outcome, aSAH$s100b, levels = c("Good", "Poor"), direction = "<"),
# "best", best.method = "youden", ret = c("threshold", "specificity", "sensitivity"))
ASAH_BEST = {"threshold": 0.20500000000000002, "specificity": 0.80555555555555558, "sensitivity": 0.63414634146341464}


# ---------------------------------------------------------------- correspondence analysis: eigenvalues, total inertia
def _varespec():
    varespec = sdata.get_example("varespec", from_r_package="vegan")
    return varespec, [c for c in varespec.get_column_names() if c != "row name"]


def test_correspondence_numbers_give_eigenvalues_and_total_inertia(needs_r, capsys):
    varespec, species = _varespec()
    numbers = varespec.add_correspondence_axes(columns=species, show="numbers")
    assert numbers.get_column_names() == ["row", "CA1", "CA2", "CA1 eigenvalue", "CA2 eigenvalue",
                                          "CA1 share of the inertia", "CA2 share of the inertia", "total inertia"]
    for k in (1, 2):
        assert numbers.get_cell_at(row=1, column=f"CA{k} eigenvalue") == pytest.approx(VARESPEC_EIGENVALUES[k - 1],
                                                                                       rel=1e-10)
        assert numbers.get_cell_at(row=1, column=f"CA{k} share of the inertia") == pytest.approx(
            VARESPEC_SHARES[k - 1], rel=1e-10)
    assert numbers.get_cell_at(row=1, column="total inertia") == pytest.approx(VARESPEC_TOTAL, rel=1e-10)
    # Oksanen's vegan tutorial prints 0.5249 and 0.3568 of a total inertia of 2.083
    assert round(numbers.get_cell_at(row=1, column="CA1 eigenvalue"), 4) == 0.5249
    assert round(numbers.get_cell_at(row=1, column="CA2 eigenvalue"), 4) == 0.3568
    assert round(numbers.get_cell_at(row=1, column="total inertia"), 3) == 2.083
    # the same number on every row: it belongs to the whole map
    assert set(numbers.get_column("total inertia")) == {numbers.get_cell_at(row=1, column="total inertia")}
    out = capsys.readouterr().out
    assert "(eigenvalue 0.525)" in out and "of the total inertia 2.08" in out


def test_correspondence_numbers_match_vegan_run_now(needs_r, capsys):
    from simplydata._r import r_call

    varespec, species = _varespec()
    numbers = varespec.add_correspondence_axes(columns=species, show="numbers")
    x = np.array([varespec.get_column(c) for c in species], dtype=float).T
    r = r_call("m <- vegan::cca(x); list(eig = summary(vegan::eigenvals(m))[1, 1:2], total = m$tot.chi)",
               packages=("vegan",), x=x)
    for k in (1, 2):
        assert numbers.get_cell_at(row=1, column=f"CA{k} eigenvalue") == pytest.approx(float(r["eig"][k - 1]),
                                                                                       rel=1e-10)
    assert numbers.get_cell_at(row=1, column="total inertia") == pytest.approx(float(r["total"][0]), rel=1e-10)
    capsys.readouterr()


def test_multiple_correspondence_numbers_give_the_total_adjusted_inertia(needs_r, capsys):
    from simplydata._r import r_call

    answers = {"a": list("xyxzyxzzxy"), "b": list("pqqppqqppq"), "c": list("uuvvuvuvvu")}
    numbers = sdata.table(answers).add_correspondence_axes(columns=["a", "b", "c"], show="numbers")
    assert numbers.get_column_names() == ["row", "CA1", "CA2", "CA1 share of the inertia",
                                          "CA2 share of the inertia", "total inertia"]
    r = r_call("d <- data.frame(a, b, c, stringsAsFactors = TRUE); m <- ca::mjca(d, lambda = 'adjusted'); "
               "list(share = m$inertia.e, total = m$inertia.t)", packages=("ca",),
               **{k: np.array(v, dtype=object) for k, v in answers.items()})
    assert numbers.get_cell_at(row=1, column="total inertia") == pytest.approx(float(r["total"][0]), rel=1e-10)
    assert numbers.get_cell_at(row=1, column="CA1 share of the inertia") == pytest.approx(float(r["share"][0]),
                                                                                        rel=1e-10)
    capsys.readouterr()


# ---------------------------------------------------------------- partial correlation as a result table
@pytest.mark.parametrize("method", ["pearson", "spearman"])
def test_partial_correlation_result_table_matches_ppcor(method, needs_r, capsys):
    cars = sdata.get_example("mtcars", from_r_package="datasets")
    found = cars.find_correlation_between("mpg", "wt", allowing_for="hp", test_method=method,
                                          show="result table")
    assert found.get_column_names() == ["column 1", "column 2", "allowing for", "method", "r", "statistic name",
                                        "statistic", "p-value", "tested", "rows", "strength"]
    r, statistic, p, n = MTCARS_PARTIAL[method]
    assert found.get_cell_at(row=1, column="r") == pytest.approx(r, rel=1e-10)
    assert found.get_cell_at(row=1, column="statistic") == pytest.approx(statistic, rel=1e-10)
    assert found.get_cell_at(row=1, column="p-value") == pytest.approx(p, rel=1e-8)
    assert found.get_cell_at(row=1, column="rows") == n
    assert found.get_cell_at(row=1, column="statistic name") == "t"
    assert found.get_cell_at(row=1, column="allowing for") == "hp"
    # the number given back without show= is the same r
    assert cars.find_correlation_between("mpg", "wt", allowing_for="hp", test_method=method) == pytest.approx(
        r, rel=1e-10)
    capsys.readouterr()


def test_partial_correlation_result_table_matches_ppcor_run_now(needs_r, capsys):
    from simplydata._r import r_call

    cars = sdata.get_example("mtcars", from_r_package="datasets")
    found = cars.find_correlation_between("mpg", "wt", allowing_for="hp", test_method="kendall",
                                          show="result table")
    x, y, z = (np.asarray(cars.get_column(c), dtype=float) for c in ("mpg", "wt", "hp"))
    r = r_call("p <- ppcor::pcor.test(x, y, z, method = 'kendall'); list(r = p$estimate, s = p$statistic, "
               "p = p$p.value, n = p$n)", packages=("ppcor",), x=x, y=y, z=z)
    assert found.get_cell_at(row=1, column="statistic name") == "z"
    for column, key in (("r", "r"), ("statistic", "s"), ("p-value", "p")):
        assert found.get_cell_at(row=1, column=column) == pytest.approx(float(r[key][0]), rel=1e-10)
    assert found.get_cell_at(row=1, column="rows") == int(r["n"][0])
    capsys.readouterr()


def test_partial_correlation_result_table_still_refuses_other_options(capsys):
    marks = sdata.get_example("marks")
    with pytest.raises(SimplydataError, match="two-sided partial correlation"):
        marks.find_correlation_between("hours", "marks", allowing_for="height", show="result table", sides=1,
                                       higher="positive")
    with pytest.raises(SimplydataError, match="pearson"):
        marks.find_correlation_between("hours", "marks", test_method="somers", show="result table")


# ---------------------------------------------------------------- trade_off_curve: the best cut-off as a number
def test_trade_off_curve_gives_the_best_cut_off_as_a_number(needs_r, capsys):
    asah = sdata.get_example("aSAH", from_r_package="pROC")
    chart = sdata.chart(asah)
    chart.trade_off_curve(score="s100b", truth="outcome", positive="Poor")
    best = chart.get_numbers_drawn().keep_rows_where("kind", is_equal_to="dot")
    assert len(best) == 1
    assert best.get_cell_at(row=1, column="value") == pytest.approx(ASAH_BEST["threshold"], rel=1e-12)
    assert best.get_cell_at(row=1, column="y") == pytest.approx(ASAH_BEST["sensitivity"], rel=1e-12)
    assert best.get_cell_at(row=1, column="x") == pytest.approx(1 - ASAH_BEST["specificity"], rel=1e-12)
    assert best.get_cell_at(row=1, column="series").startswith("s100b: AUC")
    # the same cut-off, sensitivity and specificity as table.compare_to_truth's result table
    found = asah.compare_to_truth("s100b", truth="outcome", positive="Poor")
    measures = list(found.get_column("measure"))
    cut = found.get_cell_at(row=measures.index("best cut-off (Youden's index)") + 1, column="estimate")
    assert cut == pytest.approx(best.get_cell_at(row=1, column="value"), rel=1e-12)
    capsys.readouterr()


def test_trade_off_curve_cut_off_matches_proc_run_now(needs_r, capsys):
    from simplydata._r import r_call

    asah = sdata.get_example("aSAH", from_r_package="pROC")
    chart = sdata.chart(asah)
    chart.trade_off_curve(score="s100b", truth="outcome", positive="Poor")
    best = chart.get_numbers_drawn().keep_rows_where("kind", is_equal_to="dot")
    truth = np.array([v == "Poor" for v in asah.get_column("outcome")], dtype=float)
    r = r_call("r <- pROC::roc(truth, score, levels = c(0, 1), direction = '<', quiet = TRUE); "
               "b <- pROC::coords(r, 'best', best.method = 'youden', ret = c('threshold', 'sensitivity'), "
               "transpose = FALSE); list(cut = b$threshold[1], se = b$sensitivity[1])", packages=("pROC",),
               truth=truth, score=np.asarray(asah.get_column("s100b"), dtype=float))
    assert best.get_cell_at(row=1, column="value") == pytest.approx(float(r["cut"][0]), rel=1e-12)
    assert best.get_cell_at(row=1, column="y") == pytest.approx(float(r["se"][0]), rel=1e-12)
    capsys.readouterr()


def test_other_charts_leave_the_value_column_empty(capsys):
    chart = sdata.chart(sdata.get_example("marks"))
    chart.draw_lines(x="hours", y="marks")
    drawn = chart.get_numbers_drawn()
    assert all(v is None or v != v for v in drawn.get_column("value"))  # empty: None or NaN
    capsys.readouterr()
