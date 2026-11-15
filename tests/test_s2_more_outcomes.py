"""S2: explain() with ordered groups, groups, shares, counts with many zeros, and link=, against R.

R 4.6.2: MASS 7.3-66, nnet 7.3-21, betareg 3.2-6, pscl 1.5-9; the R call is next to each value.
The zeros table is made here; the same rows went to R as zeros.csv.
"""

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table

ZEROS = pd.DataFrame({
    "depth": [3.1, 1.8, 3.4, 2.8, 0.4, 3.9, 3.0, 3.1, 0.5, 1.8, 1.5, 3.7, 2.6, 3.3, 1.8, 0.9, 2.2, 0.3, 3.3, 2.5,
              3.0, 1.4, 3.9, 3.6, 3.1, 0.8, 1.9, 0.2, 0.6, 2.7, 3.0, 3.9, 1.3, 1.5, 1.9, 0.8, 0.5, 1.9, 0.9, 2.7,
              1.7, 3.3, 2.8, 1.2, 3.3, 3.2, 1.5, 1.2, 2.7, 0.6, 0.8, 0.0, 3.1, 2.7, 2.8, 3.1, 1.8, 2.3, 0.6, 0.5],
    "site": ["shore", "deep"] * 30,
    "count": [4, 0, 5, 1, 3, 0, 3, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 1, 2, 7, 0, 6, 0, 0, 0, 4, 0, 0, 0, 0, 6, 1, 0,
              0, 1, 2, 0, 0, 3, 2, 3, 0, 3, 4, 5, 4, 0, 0, 1, 1, 0, 0, 0, 0, 2, 5, 2, 0, 0],
})


def rows(result, key="term"):
    frame = result.as_pandas()
    return {r[key] if isinstance(key, str) else tuple(r[k] for k in key): r for r in frame.to_dict("records")}


def check(got, expected, rel=1e-6):
    for name, value in expected.items():
        assert got[name] == pytest.approx(value, rel=rel), name


def graded_school():
    s = sdata.example("school")
    s["grade"] = np.where(s.marks < 40, "low", np.where(s.marks < 55, "middle", "high"))
    s.loc[s.marks.isna(), "grade"] = None
    return s


# ---------------------------------------------------------------- ordered groups
def test_ordered_groups_match_polr(capsys):
    got = rows(make_table(graded_school()).explain("grade", using=["hours", "breakfast"], outcome="ordered groups",
                                                   in_order=["low", "middle", "high"]))
    out = capsys.readouterr().out
    # R: s$grade <- factor(..., levels = c("low", "middle", "high"))
    #    o <- MASS::polr(grade ~ hours + breakfast, data = s, Hess = TRUE,
    #                    control = list(reltol = 1e-14, maxit = 10000)); summary(o); AIC(o) 300.481089131691
    # (with its default stopping rule polr stops about 1e-3 short: breakfast 0.5714, AIC 300.481097)
    check(got["hours"], {"log odds ratio": 0.629198717154245, "standard error": 0.08624217160664})
    check(got["breakfast (yes)"], {"log odds ratio": 0.57069354416778, "standard error": 0.322739025954841})
    check(got["cut-point low | middle"], {"log odds ratio": 1.5170810109757})
    check(got["cut-point middle | high"], {"log odds ratio": 4.60008359109989})
    assert "(low < middle < high)" in out and "MASS::polr(grade ~ hours + breakfast)" in out
    assert "Cut-points between the groups" in out and "AIC = 300 and" in out
    assert 'the odds of a higher "grade" are 1.77 times as high' in out


def test_ordered_groups_need_their_order_and_three_groups():
    with pytest.raises(SimplydataError, match="needs the order of the groups"):
        make_table(graded_school()).explain("grade", using="hours", outcome="ordered groups")
    with pytest.raises(SimplydataError, match="does not have 'high'"):
        make_table(graded_school()).explain("grade", using="hours", outcome="ordered groups",
                                            in_order=["low", "middle"])
    with pytest.raises(SimplydataError, match='For 2 groups use outcome="yes or no"'):
        make_table(sdata.example("school")).explain("breakfast", using="hours", outcome="groups")


# ---------------------------------------------------------------- groups
def test_groups_match_multinom(capsys):
    got = rows(make_table(sdata.example("meadow")).explain("field", using=["clover", "nettle"], outcome="groups"),
               key=("group", "term"))
    out = capsys.readouterr().out
    # R: mn <- nnet::multinom(field ~ clover + nettle, data = meadow, reltol = 1e-12, maxit = 1000)
    #    coef(mn); summary(mn)$standard.errors; AIC(mn) 70.8478736410936
    check(got[("River field", "(intercept)")], {"log odds ratio": -2.07199223132445, "standard error": 1.22372803187254},
          rel=1e-5)
    check(got[("River field", "nettle")], {"log odds ratio": 0.202932893581286, "standard error": 0.112447294165939},
          rel=1e-5)
    check(got[("South field", "clover")], {"log odds ratio": -0.0222104124408451,
                                            "standard error": 0.0404653363238205}, rel=1e-5)
    assert 'Being "River field" rather than "North field":' in out and "nnet::multinom" in out
    assert "AIC = 70.8" in out


# ---------------------------------------------------------------- shares
def test_shares_match_betareg(capsys, needs_r):
    growth = sdata.example("growth").assign(share=lambda d: d.forest / 100)
    got = rows(make_table(growth).explain("share", using=["year", "country"], outcome="shares"))
    out = capsys.readouterr().out
    # R: g$share <- g$forest / 100; b <- betareg::betareg(share ~ year + country, data = g); summary(b)
    check(got["year"], {"log odds ratio": -0.0197402541278879, "standard error": 0.00193542422126351})
    check(got["country (Dateland)"], {"log odds ratio": -1.5851761230799, "standard error": 0.0430310507824135})
    assert "Precision 436" in out and "betareg::betareg(share ~ year + country)" in out  # phi 435.58365308945


def test_shares_must_be_between_0_and_1():
    with pytest.raises(SimplydataError, match="They look like percents"):
        make_table(sdata.example("growth")).explain("forest", using="year", outcome="shares")


# ---------------------------------------------------------------- counts with many zeros
def test_counts_with_many_zeros_match_zeroinfl(capsys, needs_r):
    got = rows(make_table(ZEROS).explain("count", using=["depth", "site"], outcome="counts with many zeros"),
               key=("part", "term"))
    out = capsys.readouterr().out
    # R: z <- pscl::zeroinfl(count ~ depth + site, data = zeros, dist = "poisson"); summary(z); logLik(z) -87.3321
    check(got[("count", "depth")], {"log ratio": 0.370663489064861, "standard error": 0.122351244231846})
    check(got[("count", "site (shore)")], {"log ratio": 0.504302892548438, "standard error": 0.251873660326751})
    check(got[("extra zeros", "(intercept)")], {"log ratio": 0.644142719074429, "standard error": 0.815318405615273})
    check(got[("extra zeros", "depth")], {"log ratio": -0.182052094618183, "standard error": 0.280996076340669})
    assert "33 of them 0" in out and "A 0 can come two ways" in out and "Extra zeros (the zero part" in out
    assert "pscl::zeroinfl(count ~ depth + site" in out


def test_counts_with_many_zeros_need_zeros():
    with pytest.raises(SimplydataError, match="has no zeros"):
        make_table(ZEROS.assign(count=ZEROS["count"] + 1)).explain("count", using="depth",
                                                                    outcome="counts with many zeros")


# ---------------------------------------------------------------- link=
def test_probit_link_matches_r(capsys):
    got = rows(make_table(sdata.example("school")).explain("passed", using=["hours", "breakfast"],
                                                           outcome="yes or no", link="probit"))
    out = capsys.readouterr().out
    # R: glm(y ~ hours + breakfast, data = s, family = binomial(link = "probit")); AIC 205.170654676779
    check(got["hours"], {"effect (probit scale)": 0.301691204944371, "standard error": 0.049647106403719}, rel=1e-5)
    check(got["(intercept)"], {"effect (probit scale)": -1.83120076540911, "standard error": 0.30768829939729},
          rel=1e-5)
    assert 'binomial(link = "probit")' in out and "changes the probit of yes by 0.302" in out
    assert "Each effect (probit scale) below" in out and "AIC = 205" in out


def test_link_checks():
    school = make_table(sdata.example("school"))
    with pytest.raises(SimplydataError, match="link= for outcome=\"yes or no\" is one of"):
        school.explain("passed", using="hours", outcome="yes or no", link="sqrt")
    with pytest.raises(SimplydataError, match="link= works with"):
        school.explain("marks", using="hours", link="log")
