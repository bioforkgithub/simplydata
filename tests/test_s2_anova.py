"""S2: explain(..., test_type=) tables of tests (ANOVA tables), checked against R car and effectsize.

R 4.6.2, car 3.1, effectsize 1.0; s2 <- na.omit(school[, c("marks", "hours", "breakfast", "school")]).
"""


import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table


def rows_of_tests(result):
    frame = result.as_pandas()
    return {r["term"]: r for r in frame.to_dict("records") if "(test," in r["term"]}


@pytest.fixture
def school():
    return make_table(sdata.example("school"))


# R: m <- lm(marks ~ breakfast * school, data = s2)  (unbalanced: the three types differ)
@pytest.mark.parametrize("test_type, ss, f", [
    ("in order", (481.006020066891, 6133.28298456276, 343.775669585055),       # anova(m)
     (4.92409229022212, 5.70789519505128, 0.319932326217288)),
    ("type 2", (440.555671296297, 6133.28298456276, 343.775669585055),          # car::Anova(m, type = 2)
     (4.50999923897429, 5.70789519505129, 0.319932326217288)),
    ("type 3", (448.236863032311, 5874.74696588134, 343.775669585044),          # contr.sum; Anova(m, type = 3)
     (4.58863213633753, 5.4672905298999, 0.319932326217277)),
])
def test_anova_tables_match_car(school, capsys, test_type, ss, f):
    got = rows_of_tests(school.explain("marks", using=["breakfast * school"], test_type=test_type))
    out = capsys.readouterr().out
    for term, s, fv in zip(("breakfast", "school", "breakfast : school"), ss, f):
        row = got[f"{term} (test, {test_type})"]
        assert row["sum of squares"] == pytest.approx(s, rel=1e-9)
        assert row["statistic"] == pytest.approx(fv, rel=1e-9)
    assert "Tests for each column" in out and test_type in out


def test_anova_table_keeps_the_order_of_using(school):
    # R: car::Anova(lm(marks ~ hours + breakfast, data = s2), type = 2): hours SS 8473.78574370477, F 113.27
    got = rows_of_tests(school.explain("marks", using=["hours", "breakfast"], test_type="type 2"))
    assert got["hours (test, type 2)"]["sum of squares"] == pytest.approx(8473.78574370477, rel=1e-9)
    assert got["hours (test, type 2)"]["statistic"] == pytest.approx(113.265303108054, rel=1e-9)
    assert got["breakfast (test, type 2)"]["statistic"] == pytest.approx(5.71759468721852, rel=1e-9)


def test_partial_eta_squared_from_effectsize(school, capsys, needs_r):
    # R: effectsize::eta_squared(car::Anova(m, type = 2), partial = TRUE)$Eta2_partial
    got = rows_of_tests(school.explain("marks", using=["breakfast * school"], test_type="type 2"))
    etas = [got[f"{t} (test, type 2)"]["partial eta-squared"] for t in ("breakfast", "school", "breakfast : school")]
    assert etas == pytest.approx([0.0280979332151114, 0.286977247328723, 0.0220616349757232], rel=1e-6)
    assert "partial eta-squared 0.0281" in capsys.readouterr().out


def test_glm_type_3_likelihood_ratio_tests_match_car(school, needs_r):
    # R: options(contrasts = c("contr.sum", "contr.poly"))
    #    car::Anova(glm(y ~ hours + breakfast + school, family = binomial), type = 3, test.statistic = "LR")
    got = rows_of_tests(school.explain("passed", using=["hours", "breakfast", "school"], outcome="yes or no",
                                  test_type="type 3"))
    assert got["hours (test, type 3)"]["statistic"] == pytest.approx(58.4160253195805, rel=1e-6)
    assert got["breakfast (test, type 3)"]["p-value"] == pytest.approx(0.207597779626905, rel=1e-6)
    assert got["school (test, type 3)"]["degrees of freedom"] == 11


def test_test_type_spellings_and_checks(school):
    got = rows_of_tests(school.explain("marks", using=["hours", "breakfast"], test_type="II"))
    assert "hours (test, type 2)" in got
    with pytest.raises(SimplydataError, match='test_type= is "type 2"'):
        school.explain("marks", using="hours", test_type="type 4")
    with pytest.raises(SimplydataError, match="not available with grouped_by="):
        school.explain("marks", using="hours", grouped_by="school", test_type="type 2")


def test_separation_prints_infinite_instead_of_crashing(capsys):
    # a group column that splits yes and no completely: the odds ratio runs off to infinity
    data = sdata.example("school").assign(passed=lambda d: d.breakfast.map({"yes": "yes", "no": "no"}))
    make_table(data).explain("passed", using=["hours", "breakfast"], outcome="yes or no")
    out = capsys.readouterr().out
    assert "complete separation" in out
