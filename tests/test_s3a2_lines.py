"""S3a-2, lines and curves: fit_dose_response (and its chart twin), fit_line(method=, y_error_over_x_error=,
with_bends=, changes_at=), fit_curve(of_kind=), find_best_power_of, explain(for_percentile=, changes_at=) and
method="loess" (add_smoothed_column(interval=), draw_smooth_line(with_confidence_band=)).

Each word is checked against the package underneath (SciPy, statsmodels) and, where it calls R or R is the
reference, against R itself on the same data. Made-up data only for edge cases.
"""

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata._errors import SimplydataError


def r(code, packages=(), **values):
    from simplydata._r import r_call

    return r_call(code, packages=packages, **values)


def one(value):
    return float(np.atleast_1d(value)[0])


@pytest.fixture
def ryegrass(needs_r):
    d = r("list(conc = drc::ryegrass$conc, rootl = drc::ryegrass$rootl)", ("drc",))
    return pd.DataFrame(d)


BLISS = pd.DataFrame({"dose": 10 ** np.array([1.6907, 1.7242, 1.7552, 1.7842, 1.8113, 1.8369, 1.8610, 1.8839]),
                      "beetles": [59, 60, 62, 56, 63, 59, 62, 60], "killed": [6, 13, 18, 28, 52, 53, 61, 60]})


# ---------------------------------------------------------------------------- fit_dose_response
def test_dose_response_matches_r_drc(ryegrass, capsys):
    out = sdata.table(ryegrass).fit_dose_response(x="conc", y="rootl", doses_for_effect=[10, 50, 90]).as_pandas()
    printed = capsys.readouterr().out
    ref = r("m <- drc::drm(rootl ~ conc, data = drc::ryegrass, fct = drc::LL.4()); "
            "e <- drc::ED(m, c(10, 50, 90), interval = 'delta', display = FALSE); "
            "list(coef = unname(coef(m)), se = unname(sqrt(diag(vcov(m)))), ed = unname(e[, 1]), low = unname(e[, 3]),"
            " high = unname(e[, 4]))", ("drc",))
    params = out[out["term"].str.match(r"^[bcde] \(")]
    assert params["estimate"].to_numpy() == pytest.approx(ref["coef"], rel=1e-6)
    ci = r("m <- drc::drm(rootl ~ conc, data = drc::ryegrass, fct = drc::LL.4()); "
           "k <- confint(m); list(low = unname(k[, 1]), high = unname(k[, 2]))", ("drc",))
    assert params["95 % CI low"].to_numpy() == pytest.approx(np.asarray(ci["low"], dtype=float), rel=1e-9)
    assert params["95 % CI high"].to_numpy() == pytest.approx(np.asarray(ci["high"], dtype=float), rel=1e-9)
    assert params["standard error"].to_numpy() == pytest.approx(ref["se"], rel=1e-6)
    eds = out[out["term"].str.startswith("ED")]
    assert list(eds["term"]) == ["ED10", "ED50", "ED90"]
    assert eds["estimate"].to_numpy() == pytest.approx(ref["ed"], rel=1e-6)
    assert eds["95 % CI low"].to_numpy() == pytest.approx(ref["low"], rel=1e-6)
    assert eds["95 % CI high"].to_numpy() == pytest.approx(ref["high"], rel=1e-6)
    assert "ED50) is 3.06 (95 % CI 2.67 to 3.45)" in printed  # Ritz et al. (2015): e = 3.06
    assert "studies like this one" in printed and 'interval = "delta"' in printed


def test_dose_response_yes_or_no_is_logistic_regression_on_log_dose(needs_r, capsys):
    """Bliss (1935) beetles: the 2 parameter log-logistic curve with binomial errors is logistic regression on
    log dose, so its LD50 is exp(-b0 / b1) of statsmodels' GLM (Dobson & Barnett: b0 -60.72, b1 34.27 on log10)."""
    import statsmodels.api as sm

    out = sdata.table(BLISS).fit_dose_response(x="dose", y="killed", outcome="yes or no", out_of="beetles",
                                               doses_for_effect=[10, 50]).as_pandas()
    X = sm.add_constant(np.log10(BLISS["dose"]))
    glm = sm.GLM(np.column_stack([BLISS["killed"], BLISS["beetles"] - BLISS["killed"]]), X,
                 family=sm.families.Binomial()).fit()
    b0, b1 = glm.params
    assert (b0, b1) == pytest.approx((-60.72, 34.27), abs=0.01)
    ld = out.set_index("term")["estimate"]
    assert ld["ED50"] == pytest.approx(10 ** (-b0 / b1), rel=1e-5)
    assert ld["ED10"] == pytest.approx(10 ** ((np.log(0.1 / 0.9) - b0) / b1), rel=1e-5)
    assert "LD50 when yes is death" in capsys.readouterr().out


def test_dose_response_groups_give_drc_edcomp(needs_r, capsys):
    d = pd.DataFrame(r("list(dose = drc::S.alba$Dose, dm = drc::S.alba$DryMatter, "
                       "herbicide = as.character(drc::S.alba$Herbicide))", ("drc",)))
    out = sdata.table(d).fit_dose_response(x="dose", y="dm", for_each_group_in="herbicide").as_pandas()
    ref = r("m <- drc::drm(DryMatter ~ Dose, Herbicide, data = drc::S.alba, fct = drc::LL.4()); "
            "e <- drc::EDcomp(m, c(50, 50), interval = 'delta', display = FALSE); "
            "t <- drc::EDcomp(m, c(50, 50), display = FALSE); "
            "list(ratio = e[1, 1], low = e[1, 2], high = e[1, 3], se = t[1, 2], p = t[1, 4])", ("drc",))
    ratio = out[out["term"] == "ED50 ratio"].iloc[0]
    assert (ratio["estimate"], ratio["95 % CI low"], ratio["95 % CI high"], ratio["standard error"],
            ratio["p-value"]) == pytest.approx((one(ref["ratio"]), one(ref["low"]), one(ref["high"]), one(ref["se"]),
                                                one(ref["p"])), rel=1e-6)
    assert "relative potency" in capsys.readouterr().out


def test_dose_response_that_rises_with_dose_says_so(needs_r, capsys):
    """An increasing LL.4 curve (drc's b < 0): the sentence follows the sign of b, and the numbers are drc's."""
    rng = np.random.default_rng(5)
    dose = np.repeat([0.0, 0.5, 1, 2, 4, 8, 16, 32], 3)
    mean = np.where(dose > 0, 2 + 18 / (1 + np.exp(-1.5 * (np.log(np.where(dose > 0, dose, 1)) - np.log(4)))), 2.0)
    df = pd.DataFrame({"dose": dose, "growth": mean + rng.normal(0, 0.8, len(dose))})
    out = sdata.table(df).fit_dose_response(x="dose", y="growth", doses_for_effect=[10, 50]).as_pandas()
    printed = capsys.readouterr().out
    assert "the response rises with dose" in printed and "falls with dose" not in printed
    ref = r("m <- drc::drm(growth ~ dose, fct = drc::LL.4()); e <- drc::ED(m, c(10, 50), interval = 'delta', "
            "display = FALSE); list(b = coef(m)[1], ed = unname(e[, 1]))", ("drc",), dose=dose,
            growth=df["growth"].to_numpy())
    assert one(ref["b"]) < 0
    eds = out[out["term"].str.startswith("ED")]["estimate"].to_numpy()
    assert eds == pytest.approx(np.asarray(ref["ed"], dtype=float), rel=1e-6)
    assert eds[0] < eds[1]  # 10 % of the way up comes before 50 %


def test_dose_response_edge_cases(needs_r, capsys):
    table = sdata.table(pd.DataFrame({"dose": [-1.0, 1, 2, 3, 4, 5], "y": [9.0, 8, 6, 4, 2, 1]}))
    with pytest.raises(SimplydataError, match="negative doses"):
        table.fit_dose_response(x="dose", y="y")
    few = sdata.table(pd.DataFrame({"dose": [0.0, 1, 2, 3, 0, 1, 2, 3], "y": [9.0, 8, 5, 1, 9, 8, 5, 1]}))
    with pytest.raises(SimplydataError, match="at least 5 different doses"):
        few.fit_dose_response(x="dose", y="y")
    tox = sdata.table(sdata.get_example("toxicity"))
    with pytest.raises(SimplydataError, match="out_of="):
        tox.fit_dose_response(x="concentration", y="dead", outcome="yes or no")
    with pytest.raises(SimplydataError, match="doses_for_effect="):
        tox.fit_dose_response(x="concentration", y="root_length", doses_for_effect=[0, 50])
    with pytest.raises(SimplydataError, match="2 parameter log-logistic"):
        tox.fit_dose_response(x="concentration", y="root_length", of_kind="2 parameter log-logistic")
    tox.fit_dose_response(x="concentration", y="root_length", doses_for_effect=[50, 99.9])
    assert "outside the doses tested" in capsys.readouterr().out


def test_chart_dose_response_draws_the_r_curve(ryegrass):
    from simplydata._underneath.check import chart_facts

    chart = sdata.chart(ryegrass).draw_dots(x="conc", y="rootl").fit_dose_response()
    facts = chart_facts(chart._render().axes[0])
    xs, ys = facts["lines"][0]
    ref = r("m <- drc::drm(rootl ~ conc, data = drc::ryegrass, fct = drc::LL.4()); "
            "list(y = unname(predict(m, newdata = data.frame(conc = at))))", ("drc",), at=xs)
    assert ys == pytest.approx(np.asarray(ref["y"], dtype=float), rel=1e-6)
    assert facts["legend"][-1].startswith("ED50 3.06 (95 % CI 2.67 to 3.45)")


# ---------------------------------------------------------------------------- fit_line(method=)
def test_theil_sen_and_siegel_are_scipy():
    from scipy import stats

    df = sdata.get_example("marks")
    t = sdata.table(df).fit_line(x="hours", y="marks", method="theil-sen").as_pandas().iloc[0]
    ref = stats.theilslopes(df["marks"], df["hours"], alpha=0.95, method="separate")
    assert (t["slope"], t["intercept"], t["slope 95 % CI low"], t["slope 95 % CI high"]) == pytest.approx(
        (ref.slope, ref.intercept, ref.low_slope, ref.high_slope), rel=1e-12)
    s = sdata.table(df).fit_line(x="hours", y="marks", method="siegel").as_pandas().iloc[0]
    ref = stats.siegelslopes(df["marks"], df["hours"], method="hierarchical")
    assert (s["slope"], s["intercept"]) == pytest.approx((ref.slope, ref.intercept), rel=1e-12)


@pytest.mark.parametrize("method, r_method", [("standardised major axis", "SMA"), ("major axis", "MA"),
                                              ("reduced major axis", "SMA")])
def test_major_axis_lines_are_smatr(needs_r, method, r_method):
    d = r("list(lma = log10(smatr::leaflife$lma), longev = log10(smatr::leaflife$longev))", ("smatr",))
    out = sdata.table(pd.DataFrame(d)).fit_line(x="lma", y="longev", method=method).as_pandas().iloc[0]
    ref = r(f"f <- smatr::sma(longev ~ lma, data = data.frame(lma = lma, longev = longev), method = '{r_method}'); "
            "k <- f$coef[[1]]; list(i = k[1, 1], s = k[2, 1], lo = k[2, 2], hi = k[2, 3])", ("smatr",),
            lma=np.asarray(d["lma"]), longev=np.asarray(d["longev"]))
    assert (out["slope"], out["intercept"], out["slope 95 % CI low"], out["slope 95 % CI high"]) == pytest.approx(
        (one(ref["s"]), one(ref["i"]), one(ref["lo"]), one(ref["hi"])), rel=1e-9)


def test_deming_error_ratio_is_y_over_x(needs_r, capsys):
    """y_error_over_x_error=4 means the errors in y vary 4 times as much as those in x. R deming::deming(ystd = 2,
    xstd = 1) says the same thing independently; mcr gets error.ratio = 1 / 4 (its ratio is x over y)."""
    d = r("d <- na.omit(mcr::creatinine); list(x = d$serum.crea, y = d$plasma.crea)", ("mcr",))
    x, y = np.asarray(d["x"], dtype=float), np.asarray(d["y"], dtype=float)
    out = sdata.table(pd.DataFrame({"x": x, "y": y})).fit_line(x="x", y="y", method="deming",
                                                              y_error_over_x_error=4).as_pandas().iloc[0]
    other = r("f <- deming::deming(y ~ x, xstd = rep(1, length(x)), ystd = rep(2, length(x))); "
              "list(s = unname(coef(f)[2]), i = unname(coef(f)[1]))", ("deming",), x=x, y=y)
    assert out["slope"] == pytest.approx(one(other["s"]), rel=1e-6)
    assert out["intercept"] == pytest.approx(one(other["i"]), abs=1e-5)  # deming() iterates to 1e-7
    mcr = r("m <- mcr::mcreg(x, y, error.ratio = 0.25, method.reg = 'Deming', method.ci = 'analytical'); "
            "list(s = m@para[2, 'EST'], lo = m@para[2, 'LCI'])", ("mcr",), x=x, y=y)
    assert (out["slope"], out["slope 95 % CI low"]) == pytest.approx((one(mcr["s"]), one(mcr["lo"])), rel=1e-9)
    assert "error.ratio = 0.250" in capsys.readouterr().out
    wrong = r("m <- mcr::mcreg(x, y, error.ratio = 4, method.reg = 'Deming', method.ci = 'analytical'); "
              "list(s = m@para[2, 'EST'])", ("mcr",), x=x, y=y)
    assert out["slope"] != pytest.approx(one(wrong["s"]), rel=1e-4)  # passing 4 straight through would be wrong


def test_passing_bablok_is_mcr(needs_r):
    d = r("d <- na.omit(mcr::creatinine); list(x = d$serum.crea, y = d$plasma.crea)", ("mcr",))
    out = sdata.table(pd.DataFrame(d)).fit_line(x="x", y="y", method="passing-bablok").as_pandas().iloc[0]
    ref = r("m <- mcr::mcreg(x, y, method.reg = 'PaBa', method.ci = 'analytical'); "
            "list(s = m@para[2, 'EST'], i = m@para[1, 'EST'], lo = m@para[2, 'LCI'])", ("mcr",),
            x=np.asarray(d["x"]), y=np.asarray(d["y"]))
    assert (out["slope"], out["intercept"], out["slope 95 % CI low"]) == pytest.approx(
        (one(ref["s"]), one(ref["i"]), one(ref["lo"])), rel=1e-9)


def test_line_method_refusals():
    table = sdata.table(sdata.get_example("marks"))
    with pytest.raises(SimplydataError, match="method"):
        table.fit_line(x="hours", y="marks", method="wiggly")
    with pytest.raises(SimplydataError, match='method="deming"'):
        table.fit_line(x="hours", y="marks", y_error_over_x_error=2)
    with pytest.raises(SimplydataError, match="above 0"):
        table.fit_line(x="hours", y="marks", method="deming", y_error_over_x_error=0)
    with pytest.raises(SimplydataError, match="the data find|lets the data find"):
        table.fit_line(x="hours", y="marks", with_bends=1, changes_at=3)
    with pytest.raises(SimplydataError, match="at least 10 pairs"):
        sdata.table(pd.DataFrame({"a": [1.0, 2, 3, 4], "b": [1.0, 2, 4, 3]})).fit_line(x="a", y="b",
                                                                                     method="passing-bablok")


# ---------------------------------------------------------------------------- fit_line(with_bends=)
def test_bends_are_r_segmented(needs_r, capsys):
    d = r("data(stagnant, package = 'segmented'); list(x = stagnant$x, y = stagnant$y)", ("segmented",))
    out = sdata.table(pd.DataFrame(d)).fit_line(x="x", y="y", with_bends=1).as_pandas().iloc[0]
    ref = r("data(stagnant, package = 'segmented'); o <- lm(y ~ x, data = stagnant); "
            "s <- segmented::segmented(o, seg.Z = ~ x, npsi = 1, control = segmented::seg.control(seed = 1)); sl <- segmented::slope(s, digits = 15)$x; "
            "list(psi = s$psi[1, 'Est.'], s1 = sl[1, 1], s2 = sl[2, 1], p = segmented::davies.test(o, seg.Z = ~ x)$p.value)",
            ("segmented",))
    assert (out["bend 1"], out["slope 1"], out["slope 2"], out["Davies p-value"]) == pytest.approx(
        (one(ref["psi"]), one(ref["s1"]), one(ref["s2"]), one(ref["p"])), rel=1e-6)
    printed = capsys.readouterr().out
    assert "bends at" in printed and "Davies' test" in printed and "if the line truly had no bend" in printed.lower()


def test_bends_need_enough_rows():
    table = sdata.table(pd.DataFrame({"x": np.arange(8.0), "y": np.arange(8.0)}))
    with pytest.raises(SimplydataError, match="at least 5 rows for each"):
        table.fit_line(x="x", y="y", with_bends=1)
    with pytest.raises(SimplydataError, match="1, 2 or 3"):
        table.fit_line(x="x", y="y", with_bends=4)


# ---------------------------------------------------------------------------- changes_at=
def test_line_that_changes_at_a_point_is_statsmodels_ols(capsys):
    import statsmodels.formula.api as smf

    rng = np.random.default_rng(3)
    month = np.arange(1.0, 61.0)
    cases = 50 + 0.4 * month - 8 * (month >= 37) - 0.3 * np.clip(month - 37, 0, None) + rng.normal(0, 1, 60)
    df = pd.DataFrame({"month": month, "cases": cases})
    out = sdata.table(df).fit_line(x="month", y="cases", changes_at=37).as_pandas().iloc[0]
    df["after"] = (df["month"] >= 37).astype(float)
    df["since"] = df["after"] * (df["month"] - 37)
    ref = smf.ols("cases ~ month + after + since", df).fit()
    assert (out["level change"], out["slope change"], out["level change p-value"]) == pytest.approx(
        (ref.params["after"], ref.params["since"], ref.pvalues["after"]), rel=1e-9)
    assert "Lag-1 autocorrelation" in capsys.readouterr().out
    exp = sdata.table(df[["month", "cases"]]).explain("cases", using=["month"], changes_at={"month": 37}).as_pandas()
    assert exp.set_index("term").loc["after month 37", "effect"] == pytest.approx(ref.params["after"], rel=1e-9)


def test_explain_changes_at_with_dates_keeps_the_time_trend(capsys):
    """Monthly dates with a true jump of -8 at 2023-01: explain keeps the trend before the change (days since the
    first date), so its jump is fit_line's, not a jump that also has to carry the whole trend."""
    rng = np.random.default_rng(11)
    dates = pd.date_range("2020-01-01", periods=60, freq="MS")
    month = np.arange(60.0)
    after = (dates >= "2023-01-01").astype(float)
    cases = 40 + 0.5 * month - 8 * after + rng.normal(0, 1, 60)
    df = pd.DataFrame({"date": dates, "cases": cases})
    line = sdata.table(df).fit_line(x="date", y="cases", changes_at="2023-01-01").as_pandas().iloc[0]
    exp = sdata.table(df).explain("cases", using=["date"], changes_at={"date": "2023-01-01"}).as_pandas()
    jump = exp.set_index("term").loc["after date 2023-01-01", "effect"]
    assert jump == pytest.approx(line["level change"], rel=1e-9)
    assert jump == pytest.approx(-8, abs=1.5)
    printed = capsys.readouterr().out
    assert '"date in days since 2020-01-01"' in printed


def test_explain_changes_at_needs_a_dict():
    table = sdata.table(pd.DataFrame({"month": np.arange(20.0), "cases": np.arange(20.0)}))
    with pytest.raises(SimplydataError, match=r'changes_at=\{"month": 10\}'):
        table.explain("cases", using=["month"], changes_at=10)


# ---------------------------------------------------------------------------- fit_curve(of_kind=)
KIND_DATA = {  # R's own self-start examples: data, x, y
    "logistic growth": ("ChickWeight[ChickWeight$Chick == 1, ]", "Time", "weight"),
    "4 parameter logistic": ("ChickWeight[ChickWeight$Chick == 1, ]", "Time", "weight"),
    "michaelis-menten": ("Puromycin[Puromycin$state == 'treated', ]", "conc", "rate"),
    "rise to a limit": ("Loblolly[Loblolly$Seed == 329, ]", "age", "height"),
    "rise or fall to a limit": ("Loblolly[Loblolly$Seed == 329, ]", "age", "height"),
    "gompertz growth": ("transform(DNase[DNase$Run == 1, ], lconc = log(conc))", "lconc", "density"),
    "weibull growth": ("ChickWeight[ChickWeight$Chick == 6 & ChickWeight$Time > 0, ]", "Time", "weight"),
    "two exponentials": ("Indometh[Indometh$Subject == 1, ]", "time", "conc"),
}


@pytest.mark.parametrize("kind", list(KIND_DATA))
def test_curve_kinds_match_r_nls_with_and_without_r_start(needs_r, kind, monkeypatch):
    from simplydata.table.lines_r import SELF_START

    data, x, y = KIND_DATA[kind]
    model, names = SELF_START[kind]
    found = r(f"d <- {data}; f <- nls({y} ~ {model}({x}, {', '.join(names)}), data = d); "
              f"list(x = d${x}, y = d${y}, b = unname(coef(f)), se = unname(sqrt(diag(vcov(f)))), "
              "rss = sum(residuals(f)^2))")
    df = pd.DataFrame({"x": np.asarray(found["x"], dtype=float), "y": np.asarray(found["y"], dtype=float)})
    out = sdata.table(df).fit_curve(x="x", y="y", of_kind=kind).as_pandas()
    # R nls() stops at a relative offset of 1e-5 (its default), so its values agree to about 1e-4; the
    # least-squares minimum itself is checked by the residual sum of squares, which may not be bigger than R's
    assert out["estimate"].to_numpy() == pytest.approx(np.asarray(found["b"], dtype=float), rel=2e-4)
    rss = one(out["residual standard error"].iloc[0]) ** 2 * one(out["degrees of freedom"].iloc[0])
    assert rss <= one(found["rss"]) * (1 + 1e-9)
    assert out["standard error"].to_numpy() == pytest.approx(np.asarray(found["se"], dtype=float), rel=1e-3)
    import simplydata._r as bridge

    monkeypatch.setattr(bridge, "r_ready", lambda packages=(): False)  # no R: a search of the whole range
    alone = sdata.table(df).fit_curve(x="x", y="y", of_kind=kind).as_pandas()
    assert alone["estimate"].to_numpy() == pytest.approx(out["estimate"].to_numpy(), rel=1e-4)


def test_curve_kind_refusals():
    table = sdata.table(sdata.get_example("culture"))
    with pytest.raises(SimplydataError, match="cannot be given together"):
        table.fit_curve(x="hour", y="density", of_kind="logistic growth", of_degree=3)
    with pytest.raises(SimplydataError, match="of_kind"):
        table.fit_curve(x="hour", y="density", of_kind="s curve")
    tiny = sdata.table(pd.DataFrame({"x": [1.0, 2, 3], "y": [1.0, 2, 2.5]}))
    with pytest.raises(SimplydataError, match="needs at least 4 rows"):
        tiny.fit_curve(x="x", y="y", of_kind="logistic growth")


def test_logistic_is_another_spelling_of_logistic_growth(capsys):
    table = sdata.table(sdata.get_example("culture")).keep_rows_where("flask", is_equal_to="A")
    capsys.readouterr()
    a = table.fit_curve(x="hour", y="density", of_kind="logistic").as_pandas()
    b = table.fit_curve(x="hour", y="density", of_kind="logistic growth").as_pandas()
    assert a["estimate"].tolist() == b["estimate"].tolist()


# ---------------------------------------------------------------------------- find_best_power_of
def test_best_power_of_one_column_is_scipy_boxcox(capsys):
    from scipy import stats

    df = sdata.get_example("trial")
    out = sdata.table(df).find_best_power_of("days").as_pandas().iloc[0]
    _, lmb, (lo, hi) = stats.boxcox(df["days"].dropna().to_numpy(dtype=float), alpha=0.05)
    assert (out["power"], out["95 % CI low"], out["95 % CI high"]) == pytest.approx((lmb, lo, hi), rel=1e-9)
    yj = sdata.table(df).find_best_power_of("days", method="yeo-johnson").as_pandas().iloc[0]
    assert yj["power"] == pytest.approx(stats.yeojohnson(df["days"].dropna().to_numpy(dtype=float))[1], rel=1e-9)
    assert "closest to a normal shape" in capsys.readouterr().out


def test_best_power_one_column_is_the_car_likelihood(needs_r):
    df = sdata.get_example("trial")
    out = sdata.table(df).find_best_power_of("days").as_pandas().iloc[0]
    ref = r("list(p = unname(car::powerTransform(y ~ 1)$lambda))", ("car",), y=df["days"].to_numpy(dtype=float))
    assert out["power"] == pytest.approx(one(ref["p"]), abs=1e-4)


def test_best_power_with_using_is_car_and_box_cox_poisons(needs_r, capsys):
    """Box & Cox (1964): the poisons survival times, power about -0.75 (reciprocal suggested)."""
    d = pd.DataFrame(r("p <- boot::poisons; list(time = p$time, poison = as.character(p$poison), "
                       "treat = as.character(p$treat))", ("boot",)))
    out = sdata.table(d).find_best_power_of("time", using=["poison", "treat"]).as_pandas().iloc[0]
    ref = r("p <- boot::poisons; s <- summary(car::powerTransform(lm(time ~ poison + treat, data = p)))$result; "
            "list(p = s[1, 1], lo = s[1, 3])", ("car", "boot"))
    assert (out["power"], out["95 % CI low"]) == pytest.approx((one(ref["p"]), one(ref["lo"])), rel=1e-6)
    assert out["power"] == pytest.approx(-0.75, abs=0.01) and out["simple power"] == -1
    assert "If the log (power 0) were truly right" in capsys.readouterr().out


def test_box_cox_refuses_zeros_and_shows_yeo_johnson():
    table = sdata.table(pd.DataFrame({"v": [0.0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}))
    with pytest.raises(SimplydataError, match=r'find_best_power_of\("v", method="yeo-johnson"\)'):
        table.find_best_power_of("v")
    with pytest.raises(SimplydataError, match="at least 10"):
        sdata.table(pd.DataFrame({"v": [1.0, 2, 3]})).find_best_power_of("v")


# ---------------------------------------------------------------------------- explain(for_percentile=)
def test_percentile_lines_are_r_quantreg(needs_r, capsys):
    import statsmodels.formula.api as smf

    d = pd.DataFrame(r("data(engel, package = 'quantreg'); list(income = engel$income, food = engel$foodexp)",
                       ("quantreg",)))
    out = sdata.table(d).explain("food", using=["income"], for_percentile=[50, 90]).as_pandas()
    ref = r("data(engel, package = 'quantreg'); s <- summary(quantreg::rq(foodexp ~ income, tau = 0.9, data = engel), "
            "se = 'nid')$coefficients; list(b = unname(s[, 1]), se = unname(s[, 2]), p = unname(s[, 4]))", ("quantreg",))
    ninety = out[out["percentile"] == 90]
    assert ninety["estimate"].to_numpy() == pytest.approx(np.asarray(ref["b"], dtype=float), rel=1e-9)
    assert ninety["standard error"].to_numpy() == pytest.approx(np.asarray(ref["se"], dtype=float), rel=1e-9)
    sm = smf.quantreg("food ~ income", d).fit(q=0.9)
    assert ninety["estimate"].to_numpy() == pytest.approx(np.asarray(sm.params), rel=1e-5)  # statsmodels agrees
    assert "90th percentile" in capsys.readouterr().out


def test_percentile_refusals():
    table = sdata.table(sdata.get_example("school"))
    with pytest.raises(SimplydataError, match="from 1 to 99"):
        table.explain("marks", using=["hours"], for_percentile=100)
    with pytest.raises(SimplydataError, match='outcome="numbers"'):
        table.explain("marks", using=["hours"], for_percentile=90, outcome="counts")
    with pytest.raises(SimplydataError, match="grouped_by="):
        table.explain("marks", using=["hours"], for_percentile=90, grouped_by="school")


# ---------------------------------------------------------------------------- loess
def test_loess_column_and_band_are_r(needs_r, capsys):
    df = sdata.get_example("culture")
    a = df[df["flask"] == "A"].reset_index(drop=True)
    out = sdata.table(a).add_smoothed_column("smooth", from_column="density", sorted_by="hour", method="loess",
                                             interval=95).as_pandas()
    ref = r("m <- loess(y ~ x, span = 0.75, degree = 2); p <- predict(m, se = TRUE); "
            "q <- qt(0.975, m$one.delta^2 / m$two.delta); list(f = p$fit, lo = p$fit - q * p$se.fit)",
            x=a["hour"].to_numpy(dtype=float), y=a["density"].to_numpy(dtype=float))
    assert out["smooth"].to_numpy() == pytest.approx(np.asarray(ref["f"], dtype=float), rel=1e-9)
    assert out["smooth 95 % CI low"].to_numpy() == pytest.approx(np.asarray(ref["lo"], dtype=float), rel=1e-9)
    assert "not lowess" in capsys.readouterr().out


def test_loess_is_no_longer_another_spelling_of_lowess(needs_r):
    from simplydata._underneath.check import chart_facts

    df = sdata.get_example("culture")
    a = df[df["flask"] == "A"]
    lo = chart_facts(sdata.chart(a).draw_dots(x="hour", y="density").draw_smooth_line(method="loess",
                                                                                      with_confidence_band=True)
                     ._render().axes[0])
    xs, ys = lo["lines"][0]
    ref = r("list(f = predict(loess(y ~ x, span = 0.75, degree = 2), newdata = data.frame(x = at)))",
            x=a["hour"].to_numpy(dtype=float), y=a["density"].to_numpy(dtype=float), at=xs)
    assert ys == pytest.approx(np.asarray(ref["f"], dtype=float), rel=1e-9)
    with pytest.raises(SimplydataError, match='method="loess"'):
        sdata.chart(a).draw_dots(x="hour", y="density").draw_smooth_line(with_confidence_band=True)
    with pytest.raises(SimplydataError, match='method="loess"'):
        sdata.table(a).add_smoothed_column("s", from_column="density", sorted_by="hour", interval=95)


def test_an_attached_drc_does_not_hide_gaussian_from_other_r_words(needs_r, capsys):
    """drc has its own gaussian(); with drc attached (as the reliability study and the underneath boxes do),
    mgcv's family must still be stats::gaussian."""
    r("invisible(TRUE)", ("drc",))  # attaches drc, as r_call(packages=("drc",)) does
    out = sdata.table(sdata.get_example("school")).explain("marks", using=["hours", "breakfast"],
                                                           curve_for="hours").as_pandas()
    assert len(out) > 0


def test_attached_packages_hide_nothing_the_r_words_need(needs_r, capsys):
    """quantreg (SparseM masks base matrix functions), mcr (coef, summary), segmented (MASS, nlme) and drc
    (getInitial, gaussian) attached first: a getInitial-based word and a word with base matrix code in R still
    give R's answers."""
    r("invisible(TRUE)", ("drc", "quantreg", "mcr", "segmented"))
    where = r("list(e = environmentName(environment(get('getInitial'))))")["e"]
    assert str(np.atleast_1d(where)[0]) == "drc"  # getInitial is drc's now: the words must not rely on it
    culture = sdata.get_example("culture")
    a = culture[culture["flask"] == "A"]
    fit = sdata.table(a).fit_curve(x="hour", y="density", of_kind="logistic growth").as_pandas()
    ref = r("f <- stats::nls(y ~ stats::SSlogis(x, Asym, xmid, scal)); list(b = unname(stats::coef(f)))",
            x=a["hour"].to_numpy(dtype=float), y=a["density"].to_numpy(dtype=float))
    assert fit["estimate"].to_numpy() == pytest.approx(np.asarray(ref["b"], dtype=float), rel=2e-4)
    school = sdata.table(sdata.get_example("school"))
    out = school.explain("marks", using=["hours"], grouped_by="school", p_value_by="satterthwaite").as_pandas()
    assert out["p-value"].notna().all()


def _printed_lag1(text):
    import re

    return float(re.search(r"Lag-1 autocorrelation of the leftovers \(observed minus fitted.*?\): (-?\d+\.\d+)",
                           text).group(1))


def _its_rows(seed=4):
    rng = np.random.default_rng(seed)
    month = np.arange(1.0, 49.0)
    noise = np.cumsum(rng.normal(0, 1, 48)) * 0.6 + rng.normal(0, 1, 48)  # leftovers that are alike in order
    cases = 30 + 0.4 * month - 6 * (month >= 25) + noise
    cases[[5, 30]] += 25  # two outliers, so a robust fit differs from least squares
    w = np.ones(48)
    w[[5, 30]] = 40.0  # the outliers count a lot in the weighted fit
    df = pd.DataFrame({"month": month, "cases": cases, "w": w})
    df["after"] = (df["month"] >= 25).astype(float)
    df["since"] = df["after"] * (df["month"] - 25)
    return df


def _acf1(values):
    from statsmodels.tsa.stattools import acf

    return float(acf(values, nlags=1, fft=False)[1])


def test_explain_changes_at_takes_the_leftovers_of_the_weighted_model(capsys):
    import statsmodels.api as sm

    df = _its_rows()
    sdata.table(df[["month", "cases", "w"]]).explain("cases", using=["month"], changes_at={"month": 25}, weights="w")
    printed = _printed_lag1(capsys.readouterr().out)
    X = sm.add_constant(df[["month", "after", "since"]])
    weighted = sm.WLS(df["cases"], X, weights=df["w"]).fit()
    plain = sm.OLS(df["cases"], X).fit()
    expected = _acf1(df["cases"] - weighted.fittedvalues)
    assert printed == pytest.approx(expected, abs=0.006)
    assert abs(expected - _acf1(df["cases"] - plain.fittedvalues)) > 0.01  # the two differ, so the test can tell


def test_explain_changes_at_takes_the_leftovers_of_the_robust_model(capsys):
    import statsmodels.api as sm

    df = _its_rows()
    sdata.table(df[["month", "cases"]]).explain("cases", using=["month"], changes_at={"month": 25},
                                                giving_outliers_less_weight=True)
    printed = _printed_lag1(capsys.readouterr().out)
    X = sm.add_constant(df[["month", "after", "since"]])
    robust = sm.RLM(df["cases"], X, M=sm.robust.norms.HuberT()).fit(scale_est="mad")
    plain = sm.OLS(df["cases"], X).fit()
    expected = _acf1(df["cases"] - robust.fittedvalues)
    assert printed == pytest.approx(expected, abs=0.006)
    assert abs(expected - _acf1(df["cases"] - plain.fittedvalues)) > 0.01


def test_explain_changes_at_refuses_options_without_one_set_of_fitted_values(capsys):
    table = sdata.table(_its_rows()[["month", "cases"]])
    with pytest.raises(SimplydataError, match="curve_for="):
        table.explain("cases", using=["month"], changes_at={"month": 25}, curve_for="month")
    assert "Interrupted time series" not in capsys.readouterr().out
