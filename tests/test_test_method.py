"""One option for choosing the method (2026-11-21): test_method= on every word.

test=, method=, rule= and methods= became test_method=, and bayesian=True became test_method="bayesian". The
planning words' test= (the word whose study is planned) became for_test=, and explain's test_type= became
table_of_tests=. The old names still work for one release, with a note once per session, and give the same
result; giving an old name and its new name together is refused.
"""

import importlib
import inspect

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import learn
from simplydata._errors import SimplydataError
from simplydata.table import bayes_words
from conftest import example_frame

NOTE_END = "The old name will stop working in a later version."
OLD_METHOD_NAMES = ("method", "test", "rule", "methods", "bayesian", "test_type")

# the words that take test_method= (test_method_mapping.csv of the plan, 58 words)
TEST_METHOD_WORDS = [
    "draw_smooth_line", "table.show_rows_with_outliers", "table.remove_rows_with_outliers",
    "table.find_percentile_of", "table.find_interval_of", "table.find_correlation_between",
    "table.compare_averages_of", "table.compare_each_pair_of", "table.compare_before_and_after",
    "table.compare_average_to", "table.compare_counts_of", "table.compare_shape_to",
    "table.add_adjusted_p_value_column", "table.compare_spreads_of", "table.compare_matched_columns",
    "sdata.compare_averages", "sdata.compare_counts", "table.compare_balanced_groups_of", "table.agreement_between",
    "table.fit_line", "table.fit_formula", "table.find_best_power_of", "sdata.find_where_smallest",
    "sdata.find_where_biggest", "sdata.solve", "table.explain", "table.check_model_of",
    "table.find_columns_that_predict", "table.add_clusters", "table.compare_profiles_of",
    "table.add_log_ratio_columns", "table.explain_profiles_of", "table.find_correlation_between_profiles",
    "table.find_hidden_factors_behind", "table.find_survival_over_time", "table.explain_survival",
    "table.combine_studies", "table.add_smoothed_column", "nums.smooth", "nums.remove_trend",
    "table.add_trend_and_season", "table.check_steady_over_time", "trend_and_season", "table.forecast",
    "nums.forecast", "forecast", "table.compare_forecasts_for", "table.find_spectrum_of", "nums.find_spectrum",
    "spectrum", "nums.keep_each_frequency_that", "nums.remove_each_frequency_that", "table.add_filtered_column",
    "sdata.frequency_filter", "sdata.find_how_many_needed", "sdata.find_chance_of_finding",
    "nums.change_time_step", "system.in_steps",
]
BAYESIAN_WORDS = ["table.compare_averages_of", "table.compare_before_and_after", "table.compare_average_to",
                  "table.compare_counts_of", "table.find_correlation_between", "table.explain", "table.check_model_of"]


def note(old, new):
    quoted = lambda name: name if '"' in name else f'"{name}"'  # noqa: E731
    return f"Note: {quoted(old)} is now called {quoted(new)}. {NOTE_END}"


def notes(out):
    """The old-name notes (other notes, such as a missing R package, are left out)."""
    return [line for line in out.splitlines() if line.startswith("Note:") and "is now called" in line]


def options_of(func):
    return [p for p in inspect.signature(func).parameters if p != "self"]


# ---------------------------------------------------------------- the guard: one name, everywhere
def test_no_public_word_has_an_old_method_option():
    """No word may take method=, test=, rule=, methods= or bayesian=: the method is chosen with test_method=."""
    found = [(key, name) for key, func in learn._words_with_options() if func is not None
             for name in options_of(func) if name in OLD_METHOD_NAMES]
    assert found == []


@pytest.mark.parametrize("key", TEST_METHOD_WORDS)
def test_each_method_word_takes_test_method(key):
    assert "test_method" in options_of(learn._function(key)), key


def test_the_planning_words_and_explain_keep_their_other_choices_apart():
    for key in ("sdata.find_how_many_needed", "sdata.find_chance_of_finding"):
        assert {"for_test", "test_method"} <= set(options_of(learn._function(key)))
    assert {"table_of_tests", "test_method"} <= set(options_of(learn._function("table.explain")))


# ---------------------------------------------------------------- old names: one note, the same result
def test_old_test_name_gives_the_same_result_with_one_note(marks, capsys):
    table = sdata.table(marks)
    new = table.compare_averages_of("marks", for_each_group_in="class", test_method="student").as_pandas()
    capsys.readouterr()
    old = table.compare_averages_of("marks", for_each_group_in="class", test="student").as_pandas()
    table.compare_averages_of("marks", for_each_group_in="class", test="student")
    pd.testing.assert_frame_equal(old, new)
    assert notes(capsys.readouterr().out) == [note("test=", "test_method=")]


@pytest.mark.parametrize("call, old", [
    (lambda t, **o: t.find_percentile_of("marks", 25, **o), {"method": 6}),
    (lambda t, **o: t.remove_rows_with_outliers("marks", **o), {"rule": "3 IQR"}),
])
def test_old_method_and_rule_give_the_same_result(marks, capsys, call, old):
    (name, value), = old.items()
    new = call(sdata.table(marks), test_method=value)
    capsys.readouterr()
    got = call(sdata.table(marks), **old)
    if hasattr(new, "as_pandas"):
        pd.testing.assert_frame_equal(got.as_pandas(), new.as_pandas())
    else:
        assert got == new
    assert notes(capsys.readouterr().out) == [note(f"{name}=", "test_method=")]


def test_old_method_on_adjusted_p_values(capsys):
    table = sdata.table(pd.DataFrame({"p-value": [0.01, 0.02, 0.03, 0.2]}))
    new = table.add_adjusted_p_value_column("p", test_method="bonferroni").as_pandas()
    capsys.readouterr()
    old = sdata.table(pd.DataFrame({"p-value": [0.01, 0.02, 0.03, 0.2]})).add_adjusted_p_value_column(
        "p", method="bonferroni").as_pandas()
    pd.testing.assert_frame_equal(old, new)
    assert notes(capsys.readouterr().out) == [note("method=", "test_method=")]


def test_old_method_on_numbers(capsys):
    values = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    new = sdata.numbers(values).smooth(test_method="median", window=3).as_numpy()
    capsys.readouterr()
    old = sdata.numbers(values).smooth(method="median", window=3).as_numpy()
    assert np.array_equal(old, new, equal_nan=True)
    assert notes(capsys.readouterr().out) == [note("method=", "test_method=")]


def test_old_methods_on_compare_forecasts_for(capsys):
    visitors = example_frame("visitors")
    chosen = ["last value", "average"]
    options = dict(sorted_by="month", repeats_every="year", for_each_group_in="museum")
    new = sdata.table(visitors).compare_forecasts_for("visitors", test_method=chosen, **options).as_pandas()
    capsys.readouterr()
    old = sdata.table(visitors).compare_forecasts_for("visitors", methods=chosen, **options).as_pandas()
    pd.testing.assert_frame_equal(old, new)
    assert notes(capsys.readouterr().out) == [note("methods=", "test_method=")]


@pytest.mark.parametrize("old", [{"test": "student"}, {"bayesian": True}])
def test_an_old_name_and_its_new_name_together_are_refused(marks, old):
    with pytest.raises(SimplydataError, match="Give test_method= only once"):
        sdata.table(marks).compare_averages_of("marks", for_each_group_in="class", test_method="welch", **old)


# ---------------------------------------------------------------- bayesian=True is test_method="bayesian"
@pytest.fixture
def bayes_route(monkeypatch):
    """The Bayesian route without R: the word's call of the R side is recorded instead."""
    seen = []
    monkeypatch.setattr(bayes_words, "two_groups", lambda table, column, for_each, groups, width, seed:
                        seen.append(("two groups", column, for_each, width, seed)) or "the Bayesian answer")
    return seen


def test_bayesian_true_is_translated(marks, capsys, bayes_route):
    two = sdata.table(marks)  # classes A and B
    assert two.compare_averages_of("marks", for_each_group_in="class", test_method="bayesian") == "the Bayesian answer"
    assert notes(capsys.readouterr().out) == []
    assert two.compare_averages_of("marks", for_each_group_in="class", bayesian=True,
                                   prior_width="wide") == "the Bayesian answer"
    assert notes(capsys.readouterr().out) == ['Note: "bayesian=True" is now called test_method="bayesian". '
                                              + NOTE_END]
    assert bayes_route == [("two groups", "marks", "class", "medium", 1), ("two groups", "marks", "class", "wide", 1)]


def test_bayesian_false_is_the_usual_test(marks, capsys, bayes_route):
    table = sdata.table(marks)
    new = table.compare_averages_of("marks", for_each_group_in="class").as_pandas()
    capsys.readouterr()
    for false in (False, np.False_):
        old = table.compare_averages_of("marks", for_each_group_in="class", bayesian=false).as_pandas()
        pd.testing.assert_frame_equal(old, new)
    # bayesian=False beside the method it leaves alone is not a clash
    student = table.compare_averages_of("marks", for_each_group_in="class", test_method="student").as_pandas()
    both = table.compare_averages_of("marks", for_each_group_in="class", test_method="student",
                                     bayesian=False).as_pandas()
    pd.testing.assert_frame_equal(student, both)
    assert bayes_route == []


def test_bayesian_takes_only_true_or_false(marks):
    with pytest.raises(SimplydataError, match='(?s)bayesian= is now test_method=.*Write test_method="bayesian"'):
        sdata.table(marks).compare_averages_of("marks", for_each_group_in="class", bayesian="yes")


@pytest.mark.parametrize("key", BAYESIAN_WORDS)
def test_every_bayesian_word_translates_bayesian_true(key):
    func = learn._function(key)
    assert func._renamed_options["bayesian"] == ("test_method", {True: "bayesian", False: None})
    assert "prior_width" in options_of(func) or key in ("table.compare_counts_of", "table.explain",
                                                         "table.check_model_of")


def test_prior_width_goes_with_test_method_bayesian(marks):
    with pytest.raises(SimplydataError, match='goes with test_method="bayesian"'):
        sdata.table(marks).compare_averages_of("marks", for_each_group_in="class", prior_width="wide")


def test_check_model_of_takes_only_bayesian(marks):
    with pytest.raises(SimplydataError, match='does not know test_method="welch".\nYou can use: "bayesian"'):
        sdata.table(sdata.get_example("school")).check_model_of("marks", using=["hours"], test_method="welch")


# ---------------------------------------------------------------- help
def test_help_names_test_method_for_the_old_names(capsys):
    sdata.help("method=")
    out = capsys.readouterr().out
    assert '"method=" is now called "test_method=" in' in out
    sdata.help("bayesian=")
    out = capsys.readouterr().out
    assert '"bayesian=True" is now called test_method="bayesian" in table.' in out
    sdata.help("rule=")
    assert '"rule=" is now called "test_method=" in table.show_rows_with_outliers()' in capsys.readouterr().out


def test_help_explains_test_method(capsys):
    sdata.help("test_method=")
    out = capsys.readouterr().out
    assert "test_method= chooses the method (the test, estimator or rule) the word uses" in out
    assert "table.compare_averages_of()" in out and "sdata.solve()" in out
    sdata.help("table.add_adjusted_p_value_column")
    assert "(chooses the method (the test, estimator or rule) the word uses)" in capsys.readouterr().out


# ---------------------------------------------------------------- the two other renames
def test_planning_test_is_now_for_test(capsys):
    new = sdata.find_how_many_needed(for_test="compare_averages", effect_size=0.5).as_pandas()
    capsys.readouterr()
    old = sdata.find_how_many_needed(test="compare_averages", effect_size=0.5).as_pandas()
    pd.testing.assert_frame_equal(old, new)
    assert notes(capsys.readouterr().out) == [note("test=", "for_test=")]
    sdata.help("test=")
    out = capsys.readouterr().out
    assert '"test=" is now called "test_method=" in table.compare_averages_of()' in out
    assert '"test=" is now called "for_test=" in sdata.find_how_many_needed(), sdata.find_chance_of_finding()' in out


def test_explain_test_type_is_now_table_of_tests(capsys):
    school = sdata.table(sdata.get_example("school"))
    new = school.explain("marks", using=["hours", "breakfast"], table_of_tests="type 2").as_pandas()
    capsys.readouterr()
    old = school.explain("marks", using=["hours", "breakfast"], test_type="type 2").as_pandas()
    pd.testing.assert_frame_equal(old, new)
    assert notes(capsys.readouterr().out) == [note("test_type=", "table_of_tests=")]


# ---------------------------------------------------------------- the values
def test_combine_studies_values_are_lower_case_and_old_spellings_still_work():
    meta = importlib.import_module("simplydata.table.meta_words")

    assert list(meta.METHODS) == ["reml", "dersimonian-laird", "paule-mandel", "common effect", "mantel-haenszel",
                                  "peto"]
    for spelling in ("REML", "reml", "DerSimonian-Laird", "Mantel-Haenszel", "Peto"):
        assert meta._text_choice(spelling, meta.METHOD_SPELLINGS, tuple(meta.METHODS), "test_method") == \
            spelling.lower()


def test_percentile_rules_with_spaces(marks, capsys):
    table = sdata.table(marks)
    spaced = table.find_percentile_of("marks", 25, test_method="median unbiased")
    numpy_name = table.find_percentile_of("marks", 25, test_method="median_unbiased")
    r_number = table.find_percentile_of("marks", 25, test_method=8)
    assert spaced == numpy_name == r_number
    with pytest.raises(SimplydataError, match='"median unbiased"'):
        table.find_percentile_of("marks", 25, test_method="median-unbiassed")


def test_fisher_on_pairs_of_averages_says_what_it_means_now(marks):
    with pytest.raises(SimplydataError, match='based_on="percents".*test_method="lsd"'):
        sdata.table(marks).compare_each_pair_of("marks", for_each_group_in="class", test_method="fisher")


def test_fishers_lsd_keeps_both_spellings(needs_r):
    example = sdata.table(sdata.get_example("marks"))
    lsd = example.compare_each_pair_of("marks", for_each_group_in="class", test_method="fisher's lsd").as_pandas()
    same = example.compare_each_pair_of("marks", for_each_group_in="class", test_method="lsd").as_pandas()
    pd.testing.assert_frame_equal(lsd, same)


# ---------------------------------------------------------------- review fixes: refusals kept, pointers current
def test_test_method_is_still_refused_where_it_was(marks):
    table = sdata.table(sdata.get_example("school"))
    with pytest.raises(SimplydataError, match="test_method="):
        table.compare_averages_of(["marks", "hours"], for_each_group_in="breakfast", test_method="kruskal-wallis")


def test_fm_points_to_test_method(capsys):
    func = learn._function("table.find_hidden_factors_behind")
    assert func._other_options["fm"] == "test_method"


def test_bayesian_false_beside_test_method_gives_the_note(marks, capsys):
    sdata.table(marks).compare_averages_of("marks", for_each_group_in="class", test_method="student", bayesian=False)
    assert notes(capsys.readouterr().out) == [note("bayesian=", "test_method=")]


def test_percentile_rule_number_as_text(marks):
    table = sdata.table(marks)
    assert table.find_percentile_of("marks", 25, test_method="8") == table.find_percentile_of("marks", 25,
                                                                                              test_method=8)
