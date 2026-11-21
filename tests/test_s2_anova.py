"""S2: explain(..., table_of_tests=) tables of tests (ANOVA tables), checked against R car and effectsize.

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
    return make_table(sdata.get_example("school"))


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
    got = rows_of_tests(school.explain("marks", using=["breakfast * school"], table_of_tests=test_type))
    out = capsys.readouterr().out
    for term, s, fv in zip(("breakfast", "school", "breakfast : school"), ss, f):
        row = got[f"{term} (test, {test_type})"]
        assert row["sum of squares"] == pytest.approx(s, rel=1e-9)
        assert row["statistic"] == pytest.approx(fv, rel=1e-9)
    assert "Tests for each column" in out and test_type in out


def test_anova_table_keeps_the_order_of_using(school):
    # R: car::Anova(lm(marks ~ hours + breakfast, data = s2), type = 2): hours SS 8473.78574370477, F 113.27
    got = rows_of_tests(school.explain("marks", using=["hours", "breakfast"], table_of_tests="type 2"))
    assert got["hours (test, type 2)"]["sum of squares"] == pytest.approx(8473.78574370477, rel=1e-9)
    assert got["hours (test, type 2)"]["statistic"] == pytest.approx(113.265303108054, rel=1e-9)
    assert got["breakfast (test, type 2)"]["statistic"] == pytest.approx(5.71759468721852, rel=1e-9)


def test_partial_eta_squared_from_effectsize(school, capsys, needs_r):
    # R: effectsize::eta_squared(car::Anova(m, type = 2), partial = TRUE)$Eta2_partial
    got = rows_of_tests(school.explain("marks", using=["breakfast * school"], table_of_tests="type 2"))
    etas = [got[f"{t} (test, type 2)"]["partial eta-squared"] for t in ("breakfast", "school", "breakfast : school")]
    assert etas == pytest.approx([0.0280979332151114, 0.286977247328723, 0.0220616349757232], rel=1e-6)
    assert "partial eta-squared 0.0281" in capsys.readouterr().out


def test_glm_type_3_likelihood_ratio_tests_match_car(school, needs_r):
    # R: options(contrasts = c("contr.sum", "contr.poly"))
    #    car::Anova(glm(y ~ hours + breakfast + school, family = binomial), type = 3, test.statistic = "LR")
    got = rows_of_tests(school.explain("passed", using=["hours", "breakfast", "school"], outcome="yes or no",
                                  table_of_tests="type 3"))
    assert got["hours (test, type 3)"]["statistic"] == pytest.approx(58.4160253195805, rel=1e-6)
    assert got["breakfast (test, type 3)"]["p-value"] == pytest.approx(0.207597779626905, rel=1e-6)
    assert got["school (test, type 3)"]["degrees of freedom"] == 11


def test_test_type_spellings_and_checks(school):
    got = rows_of_tests(school.explain("marks", using=["hours", "breakfast"], table_of_tests="II"))
    assert "hours (test, type 2)" in got
    with pytest.raises(SimplydataError, match='table_of_tests= is "type 2"'):
        school.explain("marks", using="hours", table_of_tests="type 4")
    with pytest.raises(SimplydataError, match="not available with grouped_by="):
        school.explain("marks", using="hours", grouped_by="school", table_of_tests="type 2")


def test_separation_prints_infinite_instead_of_crashing(capsys):
    # a group column that splits yes and no completely: the odds ratio runs off to infinity
    data = sdata.get_example("school").assign(passed=lambda d: d.breakfast.map({"yes": "yes", "no": "no"}))
    make_table(data).explain("passed", using=["hours", "breakfast"], outcome="yes or no")
    out = capsys.readouterr().out
    assert "complete separation" in out


# ---------------------------------------------------------------- review fixes: type 1 order, checks first, contr.sum
def test_in_order_follows_using_with_a_number_before_a_group(school):
    # R: s1 <- na.omit(school[, c("marks", "hours", "breakfast")]); anova(lm(marks ~ hours + breakfast, data = s1))
    #    Sum Sq 8527.0378884069, 427.753875364763; F 113.977100702809, 5.71759468721852;
    #    Pr(>F) 7.43531680315258e-21, 0.0178444296535825; residual SS 13242.0082362283
    got = rows_of_tests(school.explain("marks", using=["hours", "breakfast"], table_of_tests="in order"))
    hours, breakfast = got["hours (test, in order)"], got["breakfast (test, in order)"]
    assert hours["sum of squares"] == pytest.approx(8527.0378884069, rel=1e-9)
    assert hours["statistic"] == pytest.approx(113.977100702809, rel=1e-9)
    assert hours["p-value"] == pytest.approx(7.43531680315258e-21, rel=1e-6)
    assert breakfast["sum of squares"] == pytest.approx(427.753875364763, rel=1e-9)
    assert breakfast["statistic"] == pytest.approx(5.71759468721852, rel=1e-9)
    assert breakfast["p-value"] == pytest.approx(0.0178444296535825, rel=1e-9)


def test_in_order_with_an_interaction_written_first(school):
    # R: anova(lm(marks ~ hours * breakfast + school, data = s2)): R's own order hours, breakfast, school,
    #    hours:breakfast; Sum Sq 8527.0378884069 427.753875364763 5473.27690458503 14.3630194461791;
    #    F 181.44111743752 9.10188768363879 10.5874715081097 0.305621052960802
    got = rows_of_tests(school.explain("marks", using=["hours * breakfast", "school"], table_of_tests="in order"))
    terms = ("hours", "breakfast", "school", "hours : breakfast")
    assert list(got) == [f"{t} (test, in order)" for t in terms]
    for t, ss, f in zip(terms, (8527.0378884069, 427.753875364763, 5473.27690458503, 14.3630194461791),
                        (181.44111743752, 9.10188768363879, 10.5874715081097, 0.305621052960802)):
        assert got[f"{t} (test, in order)"]["sum of squares"] == pytest.approx(ss, rel=1e-9)
        assert got[f"{t} (test, in order)"]["statistic"] == pytest.approx(f, rel=1e-9)


def test_in_order_partial_eta_squared_follows_the_same_order(school, needs_r):
    # R: effectsize::eta_squared(anova(lm(marks ~ hours + breakfast, data = s1)), partial = TRUE)$Eta2_partial
    #    0.391704709502966 0.0312919765444925
    got = rows_of_tests(school.explain("marks", using=["hours", "breakfast"], table_of_tests="in order"))
    assert got["hours (test, in order)"]["partial eta-squared"] == pytest.approx(0.391704709502966, rel=1e-6)
    assert got["breakfast (test, in order)"]["partial eta-squared"] == pytest.approx(0.0312919765444925, rel=1e-6)
    # R: eta_squared(anova(lm(marks ~ hours * breakfast + school, data = s2)), partial = TRUE): hours
    #    0.523728588510405, breakfast 0.0522790867160376, school 0.413775605172793, hours:breakfast 0.00184882432317826
    got = rows_of_tests(school.explain("marks", using=["hours * breakfast", "school"], table_of_tests="in order"))
    etas = [got[f"{t} (test, in order)"]["partial eta-squared"] for t in ("hours", "breakfast", "school",
                                                                             "hours : breakfast")]
    assert etas == pytest.approx([0.523728588510405, 0.0522790867160376, 0.413775605172793, 0.00184882432317826],
                                 rel=1e-6)


def test_test_type_problems_are_said_before_anything_is_printed(school, capsys, monkeypatch):
    # R: lme4 models have no car::Anova(type = 2) F table here; the check comes before the model is printed
    with pytest.raises(SimplydataError, match="not available with grouped_by="):
        school.explain("marks", using=["hours"], grouped_by="school", table_of_tests="type 2")
    assert capsys.readouterr().out == ""
    # without R: the likelihood-ratio tests of R car::Anova(m, type = 2, test.statistic = "LR") cannot run, and
    # that is said before the model is printed, not after
    from simplydata import _r

    monkeypatch.setattr(_r, "_STATE", {"error": "no R", "missing": "rpy2"})
    with pytest.raises(_r.RMissing, match="car::Anova"):
        school.explain("passed", using=["hours", "breakfast"], outcome="yes or no", table_of_tests="type 2")
    assert capsys.readouterr().out == ""


def test_type_3_coding_is_put_back_even_when_r_stops(needs_r):
    # R: getOption("contrasts") is c(unordered = "contr.treatment", ordered = "contr.poly") at the start; the type 3
    #    code sets contr.sum inside a function with on.exit(options(op)), so a stop() leaves R's coding as it was
    from simplydata._r import r_call
    from simplydata.table.anova_tables import _in_r_with_coding

    with pytest.raises(SimplydataError, match="on purpose"):
        r_call(_in_r_with_coding("type 3", "stop('on purpose')"))
    assert [str(v) for v in r_call("unname(getOption('contrasts'))")] == ["contr.treatment", "contr.poly"]
    assert [str(v) for v in r_call(_in_r_with_coding("type 3", "unname(getOption('contrasts'))"))] == \
        ["contr.sum", "contr.poly"]
