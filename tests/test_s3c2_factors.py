"""Hidden factors (phase S3c-2): table.find_hidden_factors_behind (R psych) and table.check_hidden_factors (R lavaan).

The numbers come from R; the tests that need R ask for needs_r (skipped without R, except in CI). The checks of the
input run without R: they stop before R is called. Published numbers: Rosseel (2012), Journal of Statistical
Software 48(2), the three-factor model of Holzinger & Swineford's nine tests.
"""

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata._errors import MissingWordError, SimplydataError

COLUMNS = [f"x{i}" for i in range(1, 10)]
MEASURED_BY = {"visual": ["x1", "x2", "x3"], "textual": ["x4", "x5", "x6"], "speed": ["x7", "x8", "x9"]}


@pytest.fixture
def tests_table():
    return sdata.table(sdata.get_example("ability_tests"))


def _by(result, key):
    return result.as_pandas().set_index(key)


# ---------------------------------------------------------------- the practice table
def test_ability_tests_is_the_published_table():
    data = sdata.get_example("ability_tests")
    assert data.shape == (301, 15)
    assert data["school"].value_counts().to_dict() == {"Pasteur": 156, "Grant-White": 145}
    assert int(data.isna().sum().sum()) == 1  # one grade is empty in the source
    assert data["x1"].iloc[0] == pytest.approx(3.3333333)


def test_ability_tests_equals_lavaans_copy(needs_r):
    from simplydata._r import r_call

    found = r_call("d <- lavaan::HolzingerSwineford1939; list(x = as.matrix(d[, paste0('x', 1:9)]), id = d$id)")
    ours = sdata.get_example("ability_tests")
    assert np.allclose(ours[COLUMNS].to_numpy(), np.asarray(found["x"], dtype=float).reshape(301, 9, order="F"),
                       rtol=1e-12, atol=0)
    assert list(ours["id"]) == [int(v) for v in np.asarray(found["id"])]


# ---------------------------------------------------------------- find_hidden_factors_behind
def test_defaults_parallel_analysis_minres_oblimin(tests_table, needs_r, capsys):
    result = tests_table.find_hidden_factors_behind(COLUMNS)
    out = capsys.readouterr().out
    frame = _by(result, "column")
    assert list(result.as_pandas().columns) == ["column", "factor 1", "factor 2", "factor 3", "shared part",
                                                "own part"]
    # R psych 2.6.9: fa(x, 3, fm = "minres", rotate = "oblimin")
    assert frame.loc["x4", "factor 1"] == pytest.approx(0.846, abs=5e-4)
    assert frame.loc["x3", "factor 2"] == pytest.approx(0.686, abs=5e-4)
    assert frame.loc["x7", "factor 3"] == pytest.approx(0.737, abs=5e-4)
    assert frame.loc["x1", "shared part"] == pytest.approx(0.4767540, abs=1e-6)
    assert frame.loc["x1", "own part"] == pytest.approx(0.5232460, abs=1e-6)
    assert "Parallel analysis suggests 3 factors" in out and "with_seed=1" in out
    assert "principal components (add_principal_components) only sum the columns up" in out
    assert "Correlations between the factors: factor 1 with factor 2 0.32" in out
    assert '"x9" goes with more than one factor' in out
    assert 'psych::fa(x, nfactors = 3, fm = "minres", rotate = "oblimin")' in out
    assert "set.seed(1)" in out and "simplydata chooses: minres" in out and "You chose" not in out
    assert "KMO" not in out.split("Method:")[1].split("\n", 1)[1]  # KMO 0.75: no note
    for word in ("significant", "good fit", "true factors"):
        assert word not in out


def test_loadings_below_three_tenths_are_blank_in_print_but_kept(tests_table, needs_r, capsys):
    result = tests_table.find_hidden_factors_behind(COLUMNS)
    out = capsys.readouterr().out
    x4 = next(line for line in out.splitlines() if line.strip().startswith("x4 "))
    assert "0.85" in x4 and "0.02" not in x4
    assert _by(result, "column").loc["x4", "factor 2"] == pytest.approx(0.016, abs=5e-4)


def test_maximum_likelihood_varimax_matches_factanal(tests_table, needs_r, capsys):
    result = tests_table.find_hidden_factors_behind(COLUMNS, how_many=3, test_method="maximum likelihood", rotation="varimax")
    out = capsys.readouterr().out
    own = result.as_pandas()["own part"].to_numpy()
    # base R stats::factanal(x, 3, rotation = "varimax")$uniquenesses
    factanal = [0.5125282, 0.7487350, 0.5427768, 0.2791926, 0.2428767, 0.3052171, 0.5022002, 0.4685578, 0.5432436]
    assert np.allclose(own, factanal, rtol=1e-4)
    # the rotation too: base R stats::factanal(x, 3, rotation = "varimax")$loadings (same order and signs here)
    loadings = result.as_pandas()[["factor 1", "factor 2", "factor 3"]].to_numpy()
    assert loadings[0] == pytest.approx([0.277, 0.623, 0.151], abs=1e-3)
    assert loadings[8] == pytest.approx([0.132, 0.406, 0.524], abs=1e-3)
    assert "Parallel analysis" not in out and "maximum likelihood, varimax rotation" in out
    assert "stats::varimax" in out and "GPArotation" not in out.split("Method:")[1].split("\n")[0]
    assert "You chose test_method='maximum likelihood', rotation='varimax' and how_many=3" in out
    assert "simplydata chooses" not in out
    assert "Correlations between the factors" not in out  # varimax keeps them uncorrelated


def test_one_factor_and_other_spellings(tests_table, needs_r, capsys):
    result = tests_table.find_hidden_factors_behind(["x4", "x5", "x6"], how_many=1, test_method="Principal Axis",
                                                    rotation="no rotation")
    out = capsys.readouterr().out
    assert list(result.as_pandas().columns) == ["column", "factor 1", "shared part", "own part"]
    assert "1 hidden factor, principal axis, no rotation needed" in out
    assert "Correlations" not in out
    assert "fewer than 3 columns for each factor" not in out


def test_notes_for_few_rows(needs_r, capsys):
    table = sdata.table(sdata.get_example("ability_tests").head(40))
    table.find_hidden_factors_behind(COLUMNS, how_many=2)
    out = capsys.readouterr().out
    assert "40 rows for 9 columns (fewer than 5 rows for each column)" in out


def test_a_factor_with_few_columns_gets_a_note(tests_table, needs_r, capsys):
    tests_table.find_hidden_factors_behind(COLUMNS, how_many=4)
    assert "fewer than 3 columns of 0.3 or more that go mainly with" in capsys.readouterr().out


def test_promax_prints_factor_correlations(tests_table, needs_r, capsys):
    tests_table.find_hidden_factors_behind(COLUMNS, how_many=3, rotation="promax")
    out = capsys.readouterr().out
    assert "Correlations between the factors: factor 1 with factor 2" in out
    assert "simplydata chooses: minres" in out and "You chose rotation='promax' and how_many=3." in out


def test_columns_that_share_little_get_the_kmo_note(needs_r, capsys):
    # how_many=1: no parallel analysis, whose outcome on random columns differs between platforms (BLAS)
    rng = np.random.default_rng(3)
    noise = pd.DataFrame(rng.normal(size=(200, 6)), columns=list("abcdef"))
    sdata.table(noise).find_hidden_factors_behind(list("abcdef"), how_many=1)
    out = capsys.readouterr().out
    assert "the columns share little (KMO = " in out


def test_parallel_analysis_that_finds_nothing_is_explained(tests_table, monkeypatch):
    # R's answer is stood in for, so the refusal is tested the same way on every platform (and without R)
    from simplydata.table import factor_r

    monkeypatch.setattr(factor_r, "explore", lambda *args, **kwargs: {"suggested": np.nan, "kmo": 0.5})
    with pytest.raises(SimplydataError, match="Parallel analysis finds no hidden factor.*how_many=1"):
        tests_table.find_hidden_factors_behind(COLUMNS)


def test_rows_with_empty_cells_are_skipped_with_a_note(needs_r, capsys):
    data = sdata.get_example("ability_tests")
    data.loc[:4, "x2"] = np.nan
    sdata.table(data).find_hidden_factors_behind(COLUMNS, how_many=3)
    out = capsys.readouterr().out
    assert "5 rows with an empty cell" in out and "(296 rows)" in out


def test_works_on_a_polars_table(needs_r):
    pl = pytest.importorskip("polars")
    table = sdata.table(pl.from_pandas(sdata.get_example("ability_tests")))
    result = table.find_hidden_factors_behind(COLUMNS, how_many=3)
    assert result.as_pandas().set_index("column").loc["x5", "factor 1"] == pytest.approx(0.886, abs=5e-4)


# ---------------------------------------------------------------- check_hidden_factors
def test_the_published_three_factor_model(tests_table, needs_r, capsys):
    result = tests_table.check_hidden_factors(measured_by=MEASURED_BY)
    out = capsys.readouterr().out
    terms = _by(result, "term")
    # Rosseel (2012), JSS 48(2), section 4
    assert terms.loc["chi-square", "estimate"] == pytest.approx(85.306, abs=5e-4)
    assert terms.loc["chi-square", "degrees of freedom"] == 24
    assert terms.loc["CFI", "estimate"] == pytest.approx(0.931, abs=5e-4)
    assert terms.loc["TLI", "estimate"] == pytest.approx(0.896, abs=5e-4)
    assert terms.loc["RMSEA", "estimate"] == pytest.approx(0.092, abs=5e-4)
    assert terms.loc["RMSEA", "90 % CI low"] == pytest.approx(0.071, abs=5e-4)
    assert terms.loc["RMSEA", "90 % CI high"] == pytest.approx(0.114, abs=5e-4)
    assert terms.loc["SRMR", "estimate"] == pytest.approx(0.065, abs=5e-4)
    assert terms.loc["visual measured by x1", "estimate"] == pytest.approx(0.772, abs=5e-4)
    assert terms.loc["visual with textual", "estimate"] == pytest.approx(0.459, abs=5e-4)
    assert terms.loc["visual with textual", "row kind"] == "correlation"
    assert "If the model were exactly right" in out and "fewer than 1 in 1000 studies like this one" in out
    assert "a small one is expected with many rows (300 or more) even for a useful model" in out
    assert "treat them as guides, not pass marks" in out and "Hu & Bentler 1999" in out
    assert "visual: x1 0.77, x2 0.42 and x3 0.58." in out
    assert "visual may also be measured by x9 (36.4)" in out
    assert "how much the chi-square would drop" in out
    assert "CFI and TLI 0.95 or more" in out
    assert "Change the model only for a reason you can defend" in out
    assert "visual =~ x1 + x2 + x3; textual =~ x4 + x5 + x6; speed =~ x7 + x8 + x9" in out
    assert 'missing = "ml"' not in out.split("Method:")[1].split(")")[0]
    for word in ("significant", "good fit", "the model is right.", "proves"):
        assert word not in out


def test_empty_cells_keep_every_row(tests_table, needs_r, capsys):
    data = sdata.get_example("ability_tests")
    data.loc[:29, "x1"] = np.nan
    result = sdata.table(data).check_hidden_factors(measured_by=MEASURED_BY)
    out = capsys.readouterr().out
    assert "30 rows have empty cells; lavaan uses every value given" in out
    assert "missing at random" in out
    assert "(301 rows)" in out
    assert 'lavaan::cfa(model, data, estimator = "ML", missing = "ml")' in out
    assert _by(result, "term").loc["chi-square", "estimate"] != pytest.approx(85.306, abs=5e-4)


def test_a_row_with_nothing_is_left_out_with_a_note(needs_r, capsys):
    data = sdata.get_example("ability_tests")
    data.loc[0, COLUMNS] = np.nan
    data.loc[1:5, "x1"] = np.nan
    sdata.table(data).check_hidden_factors(measured_by=MEASURED_BY)
    out = capsys.readouterr().out
    assert "1 row has no value in any of these columns and is left out" in out
    assert "(300 rows)" in out and "5 rows have empty cells" in out


def test_check_hidden_factors_on_a_polars_table(needs_r):
    pl = pytest.importorskip("polars")
    result = sdata.table(pl.from_pandas(sdata.get_example("ability_tests"))).check_hidden_factors(
        measured_by=MEASURED_BY)
    assert result.as_pandas().set_index("term").loc["chi-square", "estimate"] == pytest.approx(85.306, abs=5e-4)


def test_formula_with_comments_labels_and_constraints(tests_table, needs_r):
    result = tests_table.check_hidden_factors(formula="# two factors\nvisual =~ x1 + a*x2 + a*x3\n"
                                                      "speed =~ x7 + x8 + x9  # speeded tests\nvisual ~~ speed")
    assert "visual measured by x2" in set(result.as_pandas()["term"])


def test_formula_in_lavaan_syntax_gives_paths(tests_table, needs_r, capsys):
    result = tests_table.check_hidden_factors(formula="visual =~ x1 + x2 + x3; speed =~ x7 + x8 + x9\n"
                                                      "speed ~ visual")
    out = capsys.readouterr().out
    row = _by(result, "term").loc["speed explained by visual"]
    assert row["row kind"] == "explained by"
    assert 0 < row["estimate"] < 1
    assert "Paths (standardised): speed explained by visual" in out
    assert "lavaan::sem(model, data" in out


def test_column_names_need_not_suit_lavaan(needs_r):
    data = sdata.get_example("ability_tests").rename(columns={"x1": "visual perception", "x2": "cubes (score)"})
    result = sdata.table(data).check_hidden_factors(
        measured_by={"seeing things": ["visual perception", "cubes (score)", "x3"], "speed": ["x7", "x8", "x9"]})
    assert "seeing things measured by cubes (score)" in set(result.as_pandas()["term"])


def test_a_model_that_is_not_identified_is_refused(tests_table, needs_r):
    with pytest.raises(SimplydataError, match="not identified"):
        tests_table.check_hidden_factors(measured_by={"visual": ["x1", "x2"]})


def test_a_column_in_two_factors_is_a_cross_loading(tests_table, needs_r, capsys):
    tests_table.check_hidden_factors(measured_by={"visual": ["x1", "x2", "x3", "x9"], "speed": ["x7", "x8", "x9"]})
    out = capsys.readouterr().out
    assert '"x9" measures more than one factor (visual and speed): a cross-loading' in out


# ---------------------------------------------------------------- input checks (no R needed)
@pytest.mark.parametrize("call, message", [
    (dict(), "needs the columns that may share hidden factors"),
    (dict(columns="x1"), "needs columns as a list"),
    (dict(columns=["x1", "x2"]), "at least 3 columns"),
    (dict(columns=COLUMNS, how_many=0), 'how_many= as "automatic"'),
    (dict(columns=COLUMNS, how_many=6), "from 1 to 5 \\(9 columns can pin down at most 5 factors\\)"),
    (dict(columns=["x1", "x2", "x3"], how_many=2), "from 1 to 1"),
    (dict(columns=COLUMNS, how_many=True), 'how_many= as "automatic"'),
    (dict(columns=COLUMNS, rotation="quartimax"), "does not know rotation='quartimax'.*\n.*rotation=\"oblimin\""),
    (dict(columns=COLUMNS, test_method="wls"), "does not know test_method='wls'"),
    (dict(columns=COLUMNS, with_seed=-1), "with_seed= as a whole number"),
    (dict(columns=["x1", "x2", "school"]), '"school" does not hold numbers.*\n.*ability_tests'),
])
def test_find_hidden_factors_behind_explains_wrong_input(tests_table, call, message):
    with pytest.raises(SimplydataError, match=message):
        tests_table.find_hidden_factors_behind(**call)


def test_a_column_with_one_value_is_refused(tests_table):
    data = sdata.get_example("ability_tests").assign(same=1.0)
    with pytest.raises(SimplydataError, match='"same" has the same value in every row'):
        sdata.table(data).find_hidden_factors_behind(["x1", "x2", "same"])


@pytest.mark.parametrize("call, message", [
    (dict(), "needs measured_by="),
    (dict(measured_by=MEASURED_BY, formula="visual =~ x1 + x2"), "one of them"),
    (dict(measured_by=["x1", "x2"]), "measured_by= as a dict"),
    (dict(measured_by={"visual": ["x1"]}), 'The hidden factor "visual" has 1 column'),
    (dict(measured_by={"visual": "x1"}), 'The hidden factor "visual" has 1 column'),
    (dict(measured_by={"x1": ["x2", "x3"]}), '"x1" is the name of a column'),
    (dict(measured_by={"visual": ["x1", "x99"]}), "x99"),
    (dict(measured_by={"visual": ["x1", "school"]}), '"school" does not hold numbers'),
    (dict(formula="visual =~ x1 + x2 + x3; visual ~~ nothing_here"), "nothing_here"),
    (dict(formula="x1 = a * x2 + b"), "not a formula like those of fit_formula"),
    (dict(formula="x1 ~ x2 + x3"), "needs at least one hidden factor"),
    (dict(formula="visual =~ x1 + x2 + x99"), "x99"),
    (dict(formula=""), "formula= as text"),
])
def test_check_hidden_factors_explains_wrong_input(tests_table, call, message):
    with pytest.raises(SimplydataError, match=message):
        tests_table.check_hidden_factors(**call)


def test_names_from_other_tools_point_to_the_words(tests_table, capsys):
    with pytest.raises(SimplydataError, match="needs the columns"):
        tests_table.find_hidden_factors_behind(factors=3)
    assert "how_many=" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="needs at least one hidden factor"):
        tests_table.check_hidden_factors(model="x1 ~ x2")
    for name, word in (("fa", "find_hidden_factors_behind"), ("factanal", "find_hidden_factors_behind"),
                       ("parallel_analysis", "find_hidden_factors_behind"), ("cfa", "check_hidden_factors"),
                       ("lavaan", "check_hidden_factors"), ("rmsea", "check_hidden_factors")):
        with pytest.raises(MissingWordError) as info:
            getattr(tests_table, name)
        assert word in str(info.value)


def test_help_finds_both_words(capsys):
    sdata.help("find_hidden_factors_behind")
    sdata.help("check_hidden_factors")
    out = capsys.readouterr().out
    assert "ability_tests" in out and "measured_by=" in out
