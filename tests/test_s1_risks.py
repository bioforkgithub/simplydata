"""S1 Part C1-C2: compare_risks, compare_rates, rate_of (and sdata.compare_risks / compare_rates).

Reference values: R 4.6.2 (epitools 0.5.10.1, epiR 3.0.0, DescTools 0.99.60, TOSTER 0.8.6), on the example
tables trial (new medicine 25 of 60 died, usual care 34 of 60) and clinic (infected: ward B 30 of 100, ward A
20 of 100; infections: ward B 16 in 1600 patient-days, ward A 4 in 1803). Script:
F:/claude_work/scratch/simplydata/s1_c/c_ref.R.
"""

import math

import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table

REL = 1e-9


@pytest.fixture(params=["pandas", "polars"])
def engine(request):
    return request.param


def make(name, engine):
    data = sdata.example(name)
    if engine == "polars":
        pl = pytest.importorskip("polars")
        return make_table(pl.from_pandas(data))
    return make_table(data)


def rows(result):
    frame = result._frame.to_pandas()
    return {r["measure"] + ("" if pd.isna(r.get("group")) else " " + str(r["group"])): r.to_dict()
            for _, r in frame.iterrows()}


def test_compare_risks_trial(engine, capsys):
    got = rows(make("trial", engine).compare_risks("died", for_each="treatment", against="usual care"))
    new, usual = got["risk new medicine"], got["risk usual care"]
    assert (new["events"], new["out of"], usual["events"], usual["out of"]) == (25, 60, 34, 60)
    # R: binom.test(25, 60)$conf.int, binom.test(34, 60)$conf.int
    assert (new["estimate 95 % CI low"], new["estimate 95 % CI high"]) == pytest.approx(
        (0.2906806664704, 0.551162202246), rel=REL)
    assert (usual["estimate 95 % CI low"], usual["estimate 95 % CI high"]) == pytest.approx(
        (0.4324096535546, 0.6941185731578), rel=REL)
    rd = got["risk difference new medicine"]
    # R: DescTools::BinomDiffCI(25, 60, 34, 60, method = "score")
    assert (rd["estimate"], rd["estimate 95 % CI low"], rd["estimate 95 % CI high"]) == pytest.approx(
        (-0.15, -0.3152074568072, 0.0279682783099), rel=REL)
    # R: prop.test(c(25, 34), c(60, 60))$p.value
    assert rd["p-value"] == pytest.approx(0.1440713270668, rel=REL)
    rr = got["risk ratio new medicine"]
    # R: epitools::riskratio(matrix(c(26, 34, 35, 25), 2, byrow = TRUE), method = "wald")$measure[2, ]
    assert (rr["estimate"], rr["estimate 95 % CI low"], rr["estimate 95 % CI high"]) == pytest.approx(
        (0.7352941176471, 0.5067352538538, 1.066942620105), rel=REL)
    odds = got["odds ratio new medicine"]
    # R: epitools::oddsratio(..., method = "wald")$measure[2, ]
    assert (odds["estimate"], odds["estimate 95 % CI low"], odds["estimate 95 % CI high"]) == pytest.approx(
        (0.546218487395, 0.2648170497256, 1.126644361763), rel=REL)
    # R: epiR::epi.2by2(...)$massoc.detail$NNT.strata.wald$est = -6.666666666667 (6.67, rounded up to 7)
    nnt = got["number needed for one event fewer new medicine"]
    assert nnt["estimate"] == pytest.approx(6.666666666667, rel=REL)
    assert math.isnan(nnt["estimate 95 % CI low"])
    # the ends: 1 / the ends of R DescTools::BinomDiffCI(25, 60, 34, 60, method = "score")
    assert nnt["95 % CI end, one event fewer"] == pytest.approx(1 / 0.3152074568072, rel=REL)
    assert nnt["95 % CI end, one event more"] == pytest.approx(1 / 0.0279682783099, rel=REL)
    out = capsys.readouterr().out
    assert '"died" = "yes": 25 of 60 (41.7 %) in new medicine and 34 of 60 (56.7 %) in usual care.' in out
    assert "Out of 100, about 15 fewer in new medicine than in usual care" in out
    assert "Number needed for one event fewer: 7 (1 / 0.150, rounded up)" in out and "through infinity" in out
    assert "(the NNTB, if the event is harmful, such as death)" in out
    assert "odds are not risks" in out
    assert "about 14 of 100 studies" in out


def test_compare_risks_exact(engine):
    got = rows(make("trial", engine).compare_risks("died", for_each="treatment", against="usual care",
                                                   p_value_by="exact"))
    odds = got["odds ratio new medicine"]
    # R: fisher.test(matrix(c(25, 35, 34, 26), 2, byrow = TRUE)): p 0.1437702219435, conditional MLE
    # 0.5490137095958 (0.2484058682228 to 1.197489368143); SciPy's optimiser agrees to about 1e-5
    assert odds["p-value"] == pytest.approx(0.1437702219435, rel=1e-9)
    assert (odds["estimate"], odds["estimate 95 % CI low"], odds["estimate 95 % CI high"]) == pytest.approx(
        (0.5490137095958, 0.2484058682228, 1.197489368143), rel=1e-4)


def test_compare_risks_level(engine):
    got = rows(make("trial", engine).compare_risks("died", for_each="treatment", against="usual care", interval=90))
    # R: riskratio(..., method = "wald", conf.level = 0.90)$measure[2, 2]
    assert got["risk ratio new medicine"]["estimate 90 % CI low"] == pytest.approx(0.5379909643905, rel=REL)


def test_compare_risks_mantel_haenszel(engine, needs_r, capsys):
    got = rows(make("clinic", engine).compare_risks("infected", for_each="ward", allowing_for="age_group"))
    mh = got["odds ratio allowing for age_group ward B"]
    # R: mantelhaen.test(arr): estimate, conf.int, p.value (continuity correction, the R default)
    assert (mh["estimate"], mh["estimate 95 % CI low"], mh["estimate 95 % CI high"]) == pytest.approx(
        (1.758985209617, 0.9109510889195, 3.396481990401), rel=REL)
    assert mh["p-value"] == pytest.approx(0.12606272825, rel=1e-9)
    rr = got["risk ratio allowing for age_group ward B"]
    # R: epiR::epi.2by2(as.table(arr), method = "cohort.count")$massoc.detail$RR.mh.wald
    assert (rr["estimate"], rr["estimate 95 % CI low"], rr["estimate 95 % CI high"]) == pytest.approx(
        (1.524478401411, 0.9287370293685, 2.502360003829), rel=1e-9)
    # R: DescTools::BreslowDayTest(arr)$p.value
    assert got["same odds ratio in each age_group (Breslow-Day) ward B"]["p-value"] == pytest.approx(
        0.1067144793978, rel=1e-9)
    out = capsys.readouterr().out
    assert 'compared against "ward A" (the first in sorted order' in out
    assert 'The odds ratio is about the same in every "age_group"' in out


def test_compare_risks_equivalence(engine, capsys):
    t = make("clinic", engine)
    got = rows(t.compare_risks("infected", for_each="ward", same_within=15))
    eq = got["risk difference (percentage points), equivalence ward B"]
    # R: TOSTER::twoprop_test(p1 = .3, p2 = .2, n1 = 100, n2 = 100, null = c(-.15, .15), alternative = "equivalence")
    assert eq["p-value"] == pytest.approx(0.2055398893617, rel=1e-9)
    assert (eq["estimate 90 % CI low"], eq["estimate 90 % CI high"]) == pytest.approx(
        (-5.254009845539e-05 * 100, 0.2000525400985 * 100), rel=1e-6)
    assert eq["answer"] == "the data cannot tell"
    # R: twoprop_test(..., null = -0.15, alternative = "greater")$p.value
    got = rows(t.compare_risks("infected", for_each="ward", same_within=15, sides=1, higher="ward B"))
    assert got["risk difference (percentage points), non-inferiority ward B"]["p-value"] == pytest.approx(
        1.978512496173e-05, rel=1e-8)
    # R: twoprop_test(..., null = 0.15, alternative = "less")$p.value
    got = rows(t.compare_risks("infected", for_each="ward", same_within=15, sides=1, lower="ward B"))
    assert got["risk difference (percentage points), non-inferiority ward B"]["p-value"] == pytest.approx(
        0.2055398893617, rel=1e-9)
    assert "TOSTER::twoprop_test" in capsys.readouterr().out


def test_compare_risks_one_sided(engine, needs_r, capsys):
    got = rows(make("clinic", engine).compare_risks("infected", for_each="ward", sides=1, higher="ward B"))
    # R: prop.test(c(30, 20), c(100, 100), alternative = "greater")$p.value
    assert got["risk difference ward B"]["p-value"] == pytest.approx(0.07082234514757, rel=1e-9)
    assert "One-sided, as you asked before seeing the data: it only looks for ward B higher" in capsys.readouterr().out


def test_compare_risks_errors(engine):
    t = make("trial", engine)
    with pytest.raises(SimplydataError, match="two values"):
        t.compare_risks("age", for_each="treatment")
    with pytest.raises(SimplydataError, match='Did you mean against="usual care"'):
        t.compare_risks("died", for_each="treatment", against="usual cere")
    with pytest.raises(SimplydataError, match="value="):
        t.compare_risks("died", for_each="treatment", value="maybe")
    with pytest.raises(SimplydataError, match="The interval should be from 0 to 100"):
        t.compare_risks("died", for_each="treatment", interval=120)
    with pytest.raises(SimplydataError, match="sides=1"):
        t.compare_risks("died", for_each="treatment", higher="usual care")


def test_compare_rates(engine, capsys, needs_r):
    got = rows(make("clinic", engine).compare_rates("infections", time="patient_days", for_each="ward",
                                                    against="ward A"))
    b, a = got["rate ward B"], got["rate ward A"]
    # R: poisson.test(16, 1600)$conf.int * 1000, poisson.test(4, 1803)$conf.int * 1000
    assert (b['rate 95 % CI low'], b['rate 95 % CI high']) == pytest.approx((5.715864033526, 16.23937349848), rel=REL)
    assert (a['rate 95 % CI low'], a['rate 95 % CI high']) == pytest.approx((0.604473307613, 5.680304312481), rel=REL)
    ratio = got["rate ratio ward B"]
    # R: poisson.test(c(16, 4), c(1600, 1803)): estimate, conf.int, p.value
    assert ratio["estimate"] == pytest.approx(4.5075, rel=REL)
    assert ratio["p-value"] == pytest.approx(0.00321758778564, rel=1e-9)
    assert (ratio["estimate 95 % CI low"], ratio["estimate 95 % CI high"]) == pytest.approx(
        (1.454066042353, 18.52769398141), rel=1e-9)
    out = capsys.readouterr().out
    assert '"infections" per 1000 "patient_days": 10.0 in ward B' in out
    assert "16 events in 1600" in out and "Rate ratio 4.51 (95 % CI 1.45 to 18.5)" in out


def test_compare_rates_equivalence(engine, needs_r):
    t = make("clinic", engine)
    got = rows(t.compare_rates("infections", time="patient_days", for_each="ward", against="ward A", same_within=2))
    eq = got["rate ratio, equivalence ward B"]
    # R: poisson.test(c(16, 4), c(1600, 1803), r = 0.5, alternative = "greater")$p.value and r = 2, "less"
    assert eq["p-value against the low margin"] == pytest.approx(7.861933280129e-06, rel=1e-8)
    assert eq["p-value against the high margin"] == pytest.approx(0.9636853574692, rel=1e-9)
    # R: poisson.test(c(16, 4), c(1600, 1803), conf.level = 0.9)$conf.int
    assert (eq["estimate 90 % CI low"], eq["estimate 90 % CI high"]) == pytest.approx(
        (1.683090065535, 14.66588822402), rel=1e-9)
    assert eq["answer"] == "different"
    got = rows(t.compare_rates("infections", time="patient_days", for_each="ward", against="ward A", same_within=2,
                               sides=1, lower="ward B"))
    ni = got["rate ratio, non-inferiority ward B"]
    # R: poisson.test(c(16, 4), c(1600, 1803), r = 2, alternative = "less")$p.value; conf.int[2] (one-sided)
    assert ni["p-value"] == pytest.approx(0.9636853574692, rel=1e-9)
    assert ni["estimate one-sided 95 % CI high"] == pytest.approx(14.66588822402, rel=1e-9)


def test_rate_of(engine, capsys):
    got = make("clinic", engine).rate_of("infections", time="patient_days", for_each="ward", per=100)._frame
    got = got.to_pandas().set_index("group")
    # R: poisson.test(4, 1803)$conf.int * 100
    assert got.loc["ward A", "rate 95 % CI low"] == pytest.approx(0.0604473307613, rel=REL)
    assert got.loc["ward A", "rate"] == pytest.approx(400 / 1803, rel=REL)
    assert got.loc["ward A", "per"] == "100 patient_days"
    assert "exact Poisson intervals" in capsys.readouterr().out


def test_rates_errors(engine):
    t = make("clinic", engine)
    with pytest.raises(SimplydataError, match="rate_of"):
        t.compare_rates("infections", time="patient_days")
    with pytest.raises(SimplydataError, match="numbers"):
        t.compare_rates("ward", time="patient_days", for_each="age_group")
    with pytest.raises(SimplydataError, match="rate ratio above 1"):
        t.compare_rates("infections", time="patient_days", for_each="ward", same_within=0.5)


def test_rates_without_r_keep_python_part(engine, monkeypatch, capsys):
    from simplydata import _r

    def missing(*args, **kwargs):
        raise _r.RMissing("no R")

    monkeypatch.setattr(_r, "r_call", missing)
    got = rows(make("clinic", engine).compare_rates("infections", time="patient_days", for_each="ward",
                                                    against="ward A"))
    assert got["rate ratio ward B"]["p-value"] == pytest.approx(0.00321758778564, rel=1e-9)
    assert math.isnan(got["rate ratio ward B"]["estimate 95 % CI low"])
    assert "comes from R (poisson.test())" in capsys.readouterr().out


# ---------------------------------------------------------------- the names approved on 2026-11-15 (Part C/D review)
def test_compare_risks_column_and_value(engine, capsys):
    t = make("trial", engine)
    new = rows(t.compare_risks(column="died", for_each="treatment", against="usual care", value="yes"))
    old = rows(t.compare_risks(outcome="died", for_each="treatment", against="usual care", positive="yes"))
    assert new["risk ratio new medicine"]["estimate"] == old["risk ratio new medicine"]["estimate"]
    out = capsys.readouterr().out
    assert '"died" = "yes" (chosen with value=)' in out
    assert '"outcome=" is now called "column="' in out and "positive= is value= in simplydata." in out


def test_clear_effect_and_nnt_more(engine, capsys):
    got = rows(make("clinic", engine).compare_risks("caught_infection", for_each="ward", against="ward A"))
    rd = got["risk difference ward B"]
    # R: DescTools::BinomDiffCI(16, 100, 4, 100, method = "score"): 0.12, 0.0369716789414, 0.2076491211102
    assert (rd["estimate"], rd["estimate 95 % CI low"], rd["estimate 95 % CI high"]) == pytest.approx(
        (0.12, 0.0369716789414, 0.2076491211102), rel=REL)
    # R: prop.test(c(16, 4), c(100, 100))$p.value
    assert rd["p-value"] == pytest.approx(0.009521891184099, rel=REL)
    # R: epitools::riskratio(matrix(c(96, 84, 4, 16), 2), method = "wald")$measure[2, ]
    rr = got["risk ratio ward B"]
    assert (rr["estimate"], rr["estimate 95 % CI low"], rr["estimate 95 % CI high"]) == pytest.approx(
        (4, 1.385805784702, 11.54562939239), rel=REL)
    nnt = got["number needed for one event more ward B"]
    # 1 / 0.12, and 1 / the ends of the Newcombe interval above
    assert (nnt["estimate"], nnt["estimate 95 % CI low"], nnt["estimate 95 % CI high"]) == pytest.approx(
        (1 / 0.12, 1 / 0.2076491211102, 1 / 0.0369716789414), rel=REL)
    assert "Number needed for one event more: 9 (1 / 0.120, rounded up; 95 % CI 4.82 to 27.0)" in \
        capsys.readouterr().out


def test_risk_not_lower_and_not_higher(engine, capsys):
    t = make("trial", engine)
    got = rows(t.compare_risks("died", for_each="treatment", against="usual care", same_within=10,
                               not_higher="new medicine"))
    ni = got["risk difference (percentage points), non-inferiority new medicine"]
    # R: TOSTER::twoprop_test(p1 = 25/60, p2 = 34/60, n1 = 60, n2 = 60, null = 0.10, alternative = "less")$p.value
    assert ni["p-value"] == pytest.approx(0.002799841334382, rel=1e-9)
    # R: (p1 - p2 + qnorm(0.95) * sqrt(p1*(1-p1)/60 + p2*(1-p2)/60)) * 100
    assert ni["estimate one-sided 95 % CI high"] == pytest.approx(-0.1566030770977, rel=1e-8)
    assert ni["sides"] == "one-sided: new medicine not higher by more than 10"
    out = capsys.readouterr().out
    assert "same_within=10 on risks means risk differences from -10 to 10 percentage points." in out
    assert "the risk in new medicine is not higher than in usual care by more than 10 percentage points" in out
    # the older spelling gives the same test, with a note
    old = rows(t.compare_risks("died", for_each="treatment", against="usual care", same_within=10, sides=1,
                               lower="new medicine"))
    assert old["risk difference (percentage points), non-inferiority new medicine"]["p-value"] == ni["p-value"]
    assert 'it is written not_higher="new medicine"' in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="not_lower= is a non-inferiority test"):
        t.compare_risks("died", for_each="treatment", not_lower="new medicine")


def test_risk_margin_below_one_is_noted(engine, capsys):
    make("trial", engine).compare_risks("died", for_each="treatment", same_within=0.1)
    assert "same_within= is in percentage points: 0.1 means 0.1 points. Did you mean 10?" in capsys.readouterr().out


def test_sdata_risks_names_and_not_lower(capsys):
    import simplydata as sdata

    got = rows(sdata.compare_risks(events=[20, 30], out_of=[60, 60], names=["a", "b"], against="b",
                                   same_within=[-5, 15], not_lower="a"))
    ni = got["risk difference (percentage points), non-inferiority a"]
    # R: TOSTER::twoprop_test(p1 = 20/60, p2 = 30/60, n1 = 60, n2 = 60, null = -0.05, alternative = "greater")
    assert ni["p-value"] == pytest.approx(0.9057569809663, rel=1e-9)
    assert ni["estimate one-sided 95 % CI low"] == pytest.approx(-31.25900336675, rel=1e-9)
    old = rows(sdata.compare_risks(events=[20, 30], out_of=[60, 60], groups=["a", "b"], against="b"))
    assert "risk ratio a" in old
    assert '"groups=" is now called "names="' in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="names= needs a list"):
        sdata.compare_risks(events=[20, 30], out_of=[60, 60], names="a")


def test_rate_not_lower_with_ratio_words(engine, needs_r, capsys):
    t = make("clinic", engine)
    got = rows(t.compare_rates("infections", time="patient_days", for_each="ward", against="ward A",
                               same_within=[0.8, 1.25], not_lower="ward B"))
    ni = got["rate ratio, non-inferiority ward B"]
    # R: poisson.test(c(16, 4), c(1600, 1803), r = 0.8, alternative = "greater")$p.value; and its conf.int[1]
    assert ni["p-value"] == pytest.approx(0.0005249342662995, rel=1e-8)
    assert ni["estimate one-sided 95 % CI low"] == pytest.approx(1.683090065535, rel=1e-9)
    out = capsys.readouterr().out
    assert "same_within=[0.8, 1.25] on rates means rate ratios from 0.8 to 1.25." in out
    assert "so the rate ratio is not below 0.800: the rate in ward B is not lower than in ward A" in out
    # not_higher="ward A" is the same claim from the other side
    got = rows(t.compare_rates("infections", time="patient_days", for_each="ward", against="ward A",
                               same_within=5, not_higher="ward A"))
    # R: poisson.test(c(16, 4), c(1600, 1803), r = 0.2, alternative = "greater")$p.value
    assert got["rate ratio, non-inferiority ward B"]["p-value"] == pytest.approx(1.866245152636e-10, rel=1e-6)
    out = capsys.readouterr().out
    assert "Note: a ratio margin of 5 means 0.2 to 5, a very wide margin." in out
    assert "the rate in ward A is not higher than in ward B by more than the margin" in out


def test_sdata_rates_names(capsys):
    import simplydata as sdata

    got = sdata.compare_rates(events=[4, 16], time=[1803, 1600], names=["ward A", "ward B"],
                              against="ward A")._frame.to_pandas()
    rates = got[got["measure"] == "rate"].set_index("group")
    # R: poisson.test(16, 1600)$estimate * 1000
    assert rates.loc["ward B", "rate"] == pytest.approx(10.0, rel=REL)
    assert rates.loc["ward B", "per"] == "1000 units of time"
