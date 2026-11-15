"""S2: explain(..., smooth_for=): a smooth curve for a number column (generalised additive model), R mgcv::gam()
itself, checked against R.

R 4.6.2, mgcv 1.9; s <- read.csv("school.csv"); s$y <- as.numeric(s$passed == "yes"). The R call is next to
each value.
"""

import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table


def by_term(result):
    return {r["term"]: r for r in result.as_pandas().to_dict("records")}


@pytest.fixture
def school():
    return make_table(sdata.example("school"))


def test_smooth_curve_for_numbers_matches_mgcv(school, capsys, needs_r):
    got = by_term(school.explain("marks", using=["hours", "breakfast"], smooth_for="hours"))
    # R: m <- gam(marks ~ s(hours) + breakfast, data = s, method = "REML"); summary(m)
    #    p.table: (Intercept) 46.41599316760981 (SE 1.07290222893301); breakfastyes 3.20974982461081
    #    (SE 1.34233936586278, p 1.78438689028329e-02); s.table: s(hours) edf 1.00040658566988, F 113.169207155025;
    #    r.sq 0.396685484745066, dev.expl 0.403427799435268; AIC 1292.49397851561, BIC 1305.26840198472
    assert got["(intercept)"]["effect"] == pytest.approx(46.41599316760981, rel=1e-6)
    assert got["breakfast (yes)"]["effect"] == pytest.approx(3.20974982461081, rel=1e-5)
    assert got["breakfast (yes)"]["standard error"] == pytest.approx(1.34233936586278, rel=1e-5)
    assert got["breakfast (yes)"]["p-value"] == pytest.approx(1.78438689028329e-02, rel=1e-4)
    assert got["s(hours)"]["effective degrees of freedom"] == pytest.approx(1.00040658566988, rel=1e-4)
    assert got["s(hours)"]["statistic"] == pytest.approx(113.169207155025, rel=1e-4)
    out = capsys.readouterr().out
    assert 'mgcv::gam(marks ~ s(hours) + breakfast, family = gaussian, method = "REML")' in out
    assert "adjusted R squared = 0.397 and 40.3 % of the deviance explained" in out
    assert "AIC = 1292 and BIC = 1305" in out


def test_smooth_curve_for_yes_or_no_and_counts(school, capsys, needs_r):
    got = by_term(school.explain("passed", using=["hours", "breakfast"], outcome="yes or no", smooth_for="hours"))
    # R: gam(y ~ s(hours) + breakfast, family = binomial, method = "REML"): breakfastyes 0.415554697646004
    #    (SE 0.360914505989340, p 0.2495702939759683); s(hours) edf 1.00009556981405, Chi.sq 32.2422168032856
    assert got["breakfast (yes)"]["log odds ratio"] == pytest.approx(0.415554697646004, rel=1e-5)
    assert got["breakfast (yes)"]["p-value"] == pytest.approx(0.2495702939759683, rel=1e-4)
    assert got["s(hours)"]["statistic"] == pytest.approx(32.2422168032856, rel=1e-4)
    capsys.readouterr()
    got = by_term(school.explain("days_absent", using=["hours", "sleep"], outcome="counts",
                                 smooth_for=["hours", "sleep"]))
    # R: gam(days_absent ~ s(hours) + s(sleep), family = poisson, method = "REML"): (Intercept) 1.0119461386039;
    #    s(sleep) edf 1.45777356558205, Chi.sq 5.42817643673411, p 0.0351776063378378; AIC 603.651014940321
    assert got["(intercept)"]["log rate ratio"] == pytest.approx(1.0119461386039, rel=1e-5)
    assert got["s(sleep)"]["effective degrees of freedom"] == pytest.approx(1.45777356558205, rel=1e-3)
    assert got["s(sleep)"]["p-value"] == pytest.approx(0.0351776063378378, rel=1e-3)
    assert "AIC = 604 and" in capsys.readouterr().out


def test_smooth_for_checks(school):
    with pytest.raises(SimplydataError, match="column of using= on its own"):
        school.explain("marks", using=["hours * breakfast"], smooth_for="hours")
    with pytest.raises(SimplydataError, match="needs a column of numbers"):
        school.explain("marks", using=["hours", "breakfast"], smooth_for="breakfast")
    with pytest.raises(SimplydataError, match="cannot be used with grouped_by="):
        school.explain("marks", using=["hours"], smooth_for="hours", grouped_by="school")
    with pytest.raises(SimplydataError, match='works with outcome="numbers"'):
        school.explain("marks", using=["hours"], smooth_for="hours", outcome="positive numbers")
