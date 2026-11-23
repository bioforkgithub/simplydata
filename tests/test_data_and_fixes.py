"""Regression tests for the five "worth fixing" findings of the reference notebooks (simplydata_tests FINDINGS.md
A1, A4, A5, A6, A7), each against a certified or published value or against the same method run to convergence.

A1  table.explain on NIST Longley: standard errors from inv(R) inv(R)' of the QR factor (R summary.lm()'s chol2inv).
A4  table.fit_curve on NIST Wampler1 to Wampler5: no change (no existing least-squares routine does better on all of
    them without losing Filip); the shortfall is a stated precision limit, and Filip stays exact.
A5  compare_risks(show="attributable fractions"): the intervals are epiR's crude ones (score interval of the risk
    ratio; exact intervals of the two risks), and the printout says so instead of "Wald".
A6  the power for two percents is R power.prop.test()'s default (strict = FALSE).
A7  metafor (Paule-Mandel, REML), drc and extRemes (generalised Pareto) run to convergence.

The simplydata side reads its results with simplydata words only (get_column, get_row, get_cell_at,
keep_rows_where and undo); pandas, SciPy and R appear only on the reference side.
"""

import contextlib
import io
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata

NIST = Path(__file__).resolve().parents[1] / "validation" / "data" / "nist"


def read_nist(name):
    """(data: y and x, or y and x1 ... xk; certified [(estimate, standard deviation), ...]) of a NIST file."""
    lines = (NIST / f"{name}.dat").read_text(encoding="ascii").splitlines()
    first, last = map(int, re.search(r"Data\s*[:(]\s*lines\s+(\d+)\s+to\s+(\d+)", "\n".join(lines)).groups())
    data = np.array([[float(v) for v in line.split()] for line in lines[first - 1:last]])
    names = ["y", "x"] if data.shape[1] == 2 else ["y"] + [f"x{i}" for i in range(1, data.shape[1])]
    header = "\n".join(lines[:first - 1])
    certified = [(float(b), float(sd)) for b, sd in re.findall(r"^\s*B\d+\s+(\S+)\s+(\S+)\s*$", header, flags=re.M)]
    return pd.DataFrame(data, columns=names), certified


def lre(got, want):
    """Log relative error: the digits that agree (of 0 itself where NIST certifies 0), at most 15; 0 for NaN."""
    if not math.isfinite(got):
        return 0.0
    if got == want:
        return 15.0
    if want == 0:
        return min(15.0, -math.log10(abs(got)))
    return min(15.0, -math.log10(abs(got - want) / abs(want)))


def quiet(call, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return call(*args, **kwargs)


def cell(result, column, where, value):
    """One cell of a simplydata result: the row whose column `where` holds `value`, read with simplydata words."""
    with contextlib.redirect_stdout(io.StringIO()):
        result.keep_rows_where(where, is_equal_to=value)
        found = result.get_cell_at(row=1, column=column)
        result.undo()
    return found


# ---------------------------------------------------------------- A1: NIST Longley
def test_explain_reaches_the_nist_longley_standard_errors():
    data, certified = read_nist("Longley")
    got = quiet(sdata.table(data).explain, "y", using=[f"x{i}" for i in range(1, 7)])
    effects, errors = list(got.get_column("effect")), list(got.get_column("standard error"))
    assert len(effects) == len(certified) == 7
    # statsmodels' inv(R'R) after its QR fit gave 7.97 to 9.42 digits for the standard errors; inv(R) inv(R)' of the
    # QR factor (R summary.lm()'s chol2inv) gives 12.6 to 14.2 here, the estimates 10.9 to 13.1
    for (b, sd), estimate, error in zip(certified, effects, errors):
        assert lre(estimate, b) >= 10
        assert lre(error, sd) >= 12


def test_the_qr_covariance_is_r_summary_lm_on_an_easy_problem():
    from statsmodels.regression.linear_model import OLS

    from simplydata.table.models import _qr_unscaled_covariance

    x = np.array([1.0, 2, 3, 4, 5, 6, 7, 8])
    X = np.column_stack([np.ones(8), x, x ** 2])
    assert _qr_unscaled_covariance(X) == pytest.approx(np.linalg.inv(X.T @ X), rel=1e-10)
    assert _qr_unscaled_covariance(X) == pytest.approx(OLS(np.sin(x), X).fit().normalized_cov_params, rel=1e-10)


# ---------------------------------------------------------------- A4: NIST Wampler1 to Wampler5, Filip
@pytest.mark.parametrize("name, estimates, errors", [
    # lowest LRE of the estimates and of the standard errors: a stated precision limit, reported in the reliability
    # study as an explained difference. The number of digits varies with the computer's linear-algebra library
    # (BLAS/LAPACK): on Windows (local) Wampler1 8.99 and 8.73, Wampler3 8.98, Wampler4 8.93, Wampler5 8.04; on
    # GitHub's runners (run 45088415254) as low as 8.40 for Wampler1 (macOS) and 7.08 for Wampler5 (Ubuntu and
    # Windows, Python 3.12 and 3.13). Each bound is the lowest seen on any runner, less a margin of about 0.1
    ("Wampler1", 8.3, 8.3), ("Wampler2", 11.5, 13.0), ("Wampler3", 8.3, 13.0), ("Wampler4", 8.3, 13.0),
    ("Wampler5", 7.0, 13.0),
])
def test_fit_curve_on_the_wampler_problems_keeps_its_digits(name, estimates, errors):
    data, certified = read_nist(name)
    got = quiet(sdata.table(data).fit_curve, x="x", y="y", of_degree=5)
    assert min(lre(e, b) for (b, _), e in zip(certified, got.get_column("estimate"))) >= estimates
    assert min(lre(s, sd) for (_, sd), s in zip(certified, got.get_column("standard error"))) >= errors


def test_fit_curve_keeps_filip_exact():
    data, certified = read_nist("Filip")
    got = quiet(sdata.table(data).fit_curve, x="x", y="y", of_degree=10)
    for (b, sd), estimate, error in zip(certified, got.get_column("estimate"), got.get_column("standard error")):
        assert lre(estimate, b) >= 13 and lre(error, sd) >= 13


def test_the_wampler_shortfalls_are_explained_in_the_reliability_study():
    import importlib.util

    path = Path(__file__).resolve().parents[1] / "validation" / "cases_lines.py"
    spec = importlib.util.spec_from_file_location("simplydata_cases_lines_for_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert set(module.EXPLAINED_WAMPLER) == {"Wampler1", "Wampler3", "Wampler4", "Wampler5"}
    assert "double precision" in module.WAMPLER_LIMIT


# ---------------------------------------------------------------- A5: attributable fractions
def _flutd():
    rows = ([("dry", "yes")] * 13 + [("dry", "no")] * 2163 + [("other", "yes")] * 5 + [("other", "no")] * 3349)
    return pd.DataFrame(rows, columns=["food", "flutd"])


def test_attributable_fraction_intervals_are_named_as_epir_makes_them(needs_r, capsys):
    from scipy import stats

    from simplydata._r import r_call

    got = sdata.table(_flutd()).compare_risks("flutd", for_each_group_in="food", against="other",
                                              show="attributable fractions")
    out = capsys.readouterr().out
    methods = list(got.get_column("method"))
    assert "Wald" not in out and "Wald" not in " ".join(methods)
    assert "score interval of the risk ratio" in methods[0] and "exact intervals of the two risks" in out
    # Willeberg (1977), the first example of epiR::epi.2by2: 13 of 2176 on dry food, 5 of 3354 on other food
    score = r_call("r <- epiR::epi.2by2(as.table(matrix(c(13, 2163, 5, 3349), nrow = 2, byrow = TRUE)), "
                   "method = 'cohort.count'); unlist(r$massoc.detail$RR.strata.score)", packages=("epiR",))
    rr, low, high = (float(v) for v in np.asarray(score)[:3])
    af, paf = got.get_row(1), got.get_row(2)
    assert af["estimate"] == pytest.approx((rr - 1) / rr, rel=1e-12)
    assert af["estimate 95 % CI low"] == pytest.approx((low - 1) / low, rel=1e-12)
    assert af["estimate 95 % CI high"] == pytest.approx((high - 1) / high, rel=1e-12)
    # the population fraction's interval: the more extreme ends of (risk in all - risk unexposed) / risk in all, with
    # the exact (Clopper-Pearson) intervals of both risks
    everyone = stats.binomtest(18, 5530).proportion_ci(method="exact")
    unexposed = stats.binomtest(5, 3354).proportion_ci(method="exact")
    ends = [(everyone.low - unexposed.low) / everyone.low, (everyone.high - unexposed.high) / everyone.high]
    assert paf["estimate 95 % CI low"] == pytest.approx(min(ends), rel=1e-9)
    assert paf["estimate 95 % CI high"] == pytest.approx(max(ends), rel=1e-9)
    # FINDINGS A5: 0.329129 to 0.907214 and 0.323759 to 0.749138
    assert (af["estimate 95 % CI low"], af["estimate 95 % CI high"]) == pytest.approx((0.329129, 0.907214), abs=1e-6)
    assert (paf["estimate 95 % CI low"], paf["estimate 95 % CI high"]) == pytest.approx((0.323759, 0.749138), abs=1e-6)


# ---------------------------------------------------------------- A6: power for two percents
def test_two_percent_power_is_power_prop_test_default():
    got = sdata.find_chance_of_finding(for_test="compare_counts", percents=[50, 75], values_per_group=50)
    # R's help page of power.prop.test: power.prop.test(n = 50, p1 = .50, p2 = .75) prints power = 0.7401659
    # (strict = FALSE, the default); with strict = TRUE it is 0.7401672, which statsmodels' two-sided call gave
    power = got.get_cell_at(row=1, column="power")
    assert power == pytest.approx(0.7401659, abs=5e-8)
    assert power == pytest.approx(0.7401659013313877, rel=1e-12)


def test_two_percent_power_with_that_many_matches_r(needs_r):
    from simplydata._r import r_call

    for p1, p2 in ((50, 75), (30, 15), (10, 5)):
        got = sdata.find_how_many_needed(for_test="compare_counts", percents=[p1, p2]).get_row(1)
        r = r_call(f"power.prop.test(n = {int(got['values per group'])}, p1 = {p1 / 100}, p2 = {p2 / 100})$power")
        assert got["power with that many"] == pytest.approx(float(np.asarray(r)[0]), rel=1e-10)


# ---------------------------------------------------------------- A7: converged R fits
def _bcg():
    """The 13 BCG trials (Colditz et al. 1994), read from the installed R package metadat (dat.bcg)."""
    from simplydata._r import r_call

    d = r_call('e <- new.env(); utils::data("dat.bcg", package = "metadat", envir = e); d <- e$dat.bcg; '
               "list(trial = d$trial, tpos = d$tpos, tneg = d$tneg, cpos = d$cpos, cneg = d$cneg)",
               packages=("metadat",))
    tpos, tneg, cpos, cneg = (np.asarray(d[k], dtype=float) for k in ("tpos", "tneg", "cpos", "cneg"))
    return pd.DataFrame({"trial": [str(int(t)) for t in np.asarray(d["trial"])], "tb_vaccinated": tpos,
                         "vaccinated": tpos + tneg, "tb_unvaccinated": cpos, "unvaccinated": cpos + cneg})


BCG = dict(names="trial", events=["tb_vaccinated", "tb_unvaccinated"], out_of=["vaccinated", "unvaccinated"])


@pytest.mark.parametrize("method, tau2, p", [
    # metafor with control = list(tol = 1e-12, threshold = 1e-12, maxiter = 1000) (R 4.6.2, metafor 4.8); with its
    # default stopping rule (1e-5) simplydata gave Paule-Mandel tau^2 0.3180937, 7.9e-5 away
    ("paule-mandel", 0.31806845220502394, 0.0019192718312779982),
    ("reml", 0.3132432581364859, 0.001920015096057295),
])
def test_combine_studies_runs_metafor_to_convergence(needs_r, method, tau2, p):
    got = quiet(sdata.table(_bcg()).combine_studies, **BCG, test_method=method)
    assert cell(got, "tau squared", "row kind", "combined") == pytest.approx(tau2, rel=1e-8)
    assert cell(got, "p-value", "row kind", "combined") == pytest.approx(p, rel=1e-8)


def _ryegrass():
    from simplydata._r import r_call

    d = r_call('e <- new.env(); utils::data("ryegrass", package = "drc", envir = e); '
               "list(conc = e$ryegrass$conc, rootl = e$ryegrass$rootl)", packages=("drc",))
    return pd.DataFrame({"conc": np.asarray(d["conc"], dtype=float), "root_length": np.asarray(d["rootl"], dtype=float)})


def test_fit_dose_response_runs_drc_to_convergence(needs_r):
    from scipy.optimize import curve_fit

    data = _ryegrass()
    got = quiet(sdata.table(data).fit_dose_response, x="conc", y="root_length", doses_for_effect=[10, 50, 90])

    def estimate(term):
        return cell(got, "estimate", "term", term)

    def ll4(x, b, c, d, e):
        with np.errstate(divide="ignore"):
            return c + (d - c) / (1 + np.exp(b * (np.log(x) - np.log(e))))

    (b, c, d, e), _ = curve_fit(ll4, data["conc"], data["root_length"], p0=[3, 0.5, 7.8, 3], xtol=1e-15, ftol=1e-15,
                                gtol=1e-15, maxfev=100000)
    # the optimum is flat: SciPy run to 1e-15 and drc run to relTol 1e-15 agree to 3e-8 (b) to 7e-7 (c); drc's default
    # stopping rule (relTol 1e-7) gave b 2.982219, 3.2e-6 away, and ED10 1.463706, 4e-6 away
    assert estimate("b (steepness)") == pytest.approx(b, rel=2e-7)
    assert estimate("c (lower limit)") == pytest.approx(c, rel=2e-6)
    assert estimate("d (upper limit)") == pytest.approx(d, rel=2e-7)
    assert estimate("ED50") == pytest.approx(e, rel=5e-7)
    assert estimate("ED10") == pytest.approx(e * (10 / 90) ** (1 / b), rel=5e-7)


def test_find_return_levels_above_a_threshold_runs_extremes_to_convergence(needs_r):
    from simplydata._r import r_call

    d = r_call('e <- new.env(); utils::data("rain", package = "ismev", envir = e); as.numeric(e$rain)',
               packages=("ismev",))
    rain = pd.DataFrame({"rain": np.asarray(d, dtype=float)})
    rain["date"] = pd.date_range("1914-01-01", periods=len(rain), freq="D")
    got = quiet(sdata.table(rain).find_return_levels_of, "rain", once_in=[100], values_above=30, sorted_by="date")
    level = got.get_cell_at(row=1, column="level")
    # extRemes::fevd(threshold = 30, type = "GP", time.units = "days") with optim's reltol 1e-14, on this computer
    # (106.3427642503 on Windows, 106.3427381844 on macOS: the likelihood is that flat); optim's default stopping rule
    # gave 106.342311 on Windows (4.3e-6 away). Coles (2001), section 4.4.1, prints 106.3
    tight = r_call('f <- extRemes::fevd(x, threshold = 30, type = "GP", time.units = "days", optim.args = '
                   'list(method = "BFGS", control = list(reltol = 1e-14, maxit = 100000))); '
                   "as.numeric(extRemes::return.level(f, return.period = 100))", packages=("extRemes",),
                   x=rain["rain"].to_numpy())
    assert level == pytest.approx(float(np.asarray(tight)[0]), rel=1e-9)
    assert level == pytest.approx(106.3427642503051, rel=1e-6)
    assert level == pytest.approx(106.3, abs=0.05)


# ---------------------------------------------------------------- claims in the repository stay true
def test_the_underneath_docstring_counts_are_true():
    from simplydata import _underneath, learn
    from simplydata._underneath import UNDERNEATH

    words = [key for _, keys in learn.GROUPS for key in keys if learn._kind(key) != "option"]
    with_entry = {key.split(" ")[0] for key in UNDERNEATH}
    text = " ".join(_underneath.__doc__.split())
    assert f"tested entries for {len(with_entry)} of simplydata's {len(words)} words" in text
    assert f"There are {len(UNDERNEATH)} entries: one for each of {len(with_entry)} words" in text
    assert f"the other {len(words) - len(with_entry)} words have none" in text
    assert "one tested entry per" not in text
