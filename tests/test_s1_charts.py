"""S1 chart words: trade_off_curve (ROC), difference_dots (Bland-Altman), forest_plot.

The drawn lines are checked against the package numbers: R pROC 1.19.1 on clinic crp against infected (AUC
0.8926, DeLong 0.845472585868 to 0.939727414132, Youden cut-off 2.15 with sensitivity 0.9 and specificity 0.78)
and R BlandAltmanLeh::bland.altman.stats(device_a, device_b) (average difference -2.18, limits -11.68858126898
and 7.328581268977). Scripts: F:/claude_work/scratch/simplydata/s1_c/acc_ref.R and s1_d/d_ref.R.
"""

import numpy as np
import pytest

import simplydata as sdata
from simplydata import SimplydataError


@pytest.fixture
def clinic():
    return sdata.table(sdata.example("clinic"))


def test_trade_off_curve(clinic, needs_r):
    chart = clinic.chart()
    chart.trade_off_curve(score="crp", truth="infected")
    ax = chart._render().axes[0]
    labels = [ln.get_label() for ln in ax.lines]
    assert "crp: AUC 0.893 (95 % CI 0.845 to 0.940)" in labels and "no better than chance" in labels
    curve = next(ln for ln in ax.lines if ln.get_label().startswith("crp"))
    x, y = curve.get_xdata(), curve.get_ydata()
    assert (x[0], y[0], x[-1], y[-1]) == (0, 0, 1, 1)
    # the area under the drawn steps is pROC's AUC (trapezoids between pROC's own points)
    assert np.trapezoid(y, x) == pytest.approx(0.8926, rel=1e-9)
    best = next(ln for ln in ax.lines if ln.get_marker() == "o")
    assert (best.get_xdata()[0], best.get_ydata()[0]) == pytest.approx((1 - 0.78, 0.9), rel=1e-12)
    assert any(t.get_text() == "cut-off 2.15" for t in ax.texts)


def test_trade_off_curve_two_scores(clinic, needs_r):
    chart = clinic.chart()
    chart.trade_off_curve(score=["crp", "procalcitonin"], truth="infected")
    labels = [ln.get_label() for ln in chart._render().axes[0].lines]
    # R: pROC::ci.auc(roc(truth, procalcitonin, direction = "<")): 0.7151333333 (0.6356566991 to 0.7946...)
    assert any(lab.startswith("procalcitonin: AUC 0.715 (95 % CI 0.636 to") for lab in labels)


def test_difference_dots(clinic, needs_r):
    chart = clinic.chart()
    chart.difference_dots(first="device_a", second="device_b")
    ax = chart._render().axes[0]
    levels = sorted(float(ln.get_ydata()[0]) for ln in ax.lines)
    # average difference (statsmodels mean_diff_plot) and the limits from R BlandAltmanLeh::bland.altman.stats
    assert levels == pytest.approx([-11.68858126898, -2.18, 7.328581268977], rel=1e-9)
    # the shaded intervals of the limits: bland.altman.stats()$CI.lines
    spans = sorted((p.get_y(), p.get_y() + p.get_height()) for p in ax.patches)
    assert np.ravel(spans) == pytest.approx([-12.860244, -10.516919, 6.156919, 8.500244], abs=1e-6)
    assert ax.get_ylabel() == "device_a minus device_b"
    points = ax.collections[0].get_offsets()
    assert len(points) == 200


def test_forest_plot():
    pairs = sdata.table(sdata.example("marks")).compare_each_pair("marks", for_each="class", test="tukey")
    frame = pairs._frame.to_pandas()
    chart = pairs.chart()
    chart.forest_plot(x="difference", y="group 1")
    ax = chart._render().axes[0]
    dots = next(ln for ln in ax.lines if ln.get_marker() == "o")
    assert list(dots.get_xdata()) == pytest.approx(list(frame["difference"]))
    ticks = sorted(zip(ax.get_yticks(), (t.get_text() for t in ax.get_yticklabels())), reverse=True)
    assert [label for _, label in ticks] == list(frame["group 1"])  # the first row at the top
    assert ax.get_xscale() == "linear" and "95 % confidence interval" in ax.get_xlabel()


def test_forest_plot_ratios():
    t = sdata.table(sdata.example("trial"))
    risks = t.compare_risks("died", for_each="treatment", against="usual care")
    risks.keep_rows("measure", one_of=["risk ratio", "odds ratio"])
    chart = risks.chart()
    chart.forest_plot(x="estimate", y="measure")
    ax = chart._render().axes[0]
    assert ax.get_xscale() == "log"
    assert "the line: 1, no effect" in ax.get_xlabel()


def test_chart_errors(clinic):
    chart = clinic.chart()
    with pytest.raises(SimplydataError, match="score="):
        chart.trade_off_curve(truth="infected")
    with pytest.raises(SimplydataError, match="columns of numbers"):
        chart.difference_dots(first="device_a", second="ward")
    with pytest.raises(SimplydataError, match="95 % CI low"):
        chart.forest_plot(x="crp", y="patient")


def test_difference_dots_old_names(clinic, needs_r, capsys):
    chart = clinic.chart()
    chart.difference_dots(x="device_a", y="device_b")
    assert chart._render().axes[0].get_ylabel() == "device_a minus device_b"
    assert '"x=" is now called "first="' in capsys.readouterr().out


def test_forest_plot_log_scale_and_line_at(capsys):
    t = sdata.table(sdata.example("trial"))
    risks = t.compare_risks("died", for_each="treatment", against="usual care")
    risks.keep_rows("measure", one_of=["risk ratio", "odds ratio"])
    chart = risks.chart()
    chart.forest_plot(x="estimate", y="measure", log_scale=False, line_at=1.25)
    ax = chart._render().axes[0]
    assert ax.get_xscale() == "linear"
    assert "(the line: 1.25)" in ax.get_xlabel()
    chart = risks.chart()
    chart.forest_plot(x="estimate", y="measure", ratios=True)
    assert chart._render().axes[0].get_xscale() == "log"
    assert '"ratios=" is now called "log_scale="' in capsys.readouterr().out


def test_forest_plot_says_which_level_it_drew(capsys):
    risks = sdata.table(sdata.example("clinic")).compare_risks("caught_infection", for_each="ward",
                                                              against="ward A", same_within=15)
    chart = risks.chart()
    chart.forest_plot(x="estimate", y="measure")
    ax = chart._render().axes[0]
    labels = [t.get_text() for t in ax.get_yticklabels()]
    assert labels == ["risk", "risk"]  # the 90 % row of the equivalence test is left out
    out = capsys.readouterr().out
    assert "the table holds 95 % and 90 % intervals; forest_plot draws the 95 % intervals" in out
    assert '"risk difference (percentage points), equivalence"' in out


def test_forest_plot_of_rates_and_shift():
    rates = sdata.table(sdata.example("clinic")).rate_of("infections", time="patient_days", for_each="ward")
    chart = rates.chart()
    chart.forest_plot(x="rate", y="group")
    dots = next(ln for ln in chart._render().axes[0].lines if ln.get_marker() == "o")
    # R: poisson.test(4, 1803)$estimate * 1000, poisson.test(16, 1600)$estimate * 1000
    assert list(dots.get_xdata()) == pytest.approx([2.218524681087, 10.0], rel=1e-9)
