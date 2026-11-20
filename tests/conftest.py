import os

import matplotlib

matplotlib.use("Agg")

# The test run is a script that uses many words: no list of packages at its end (tests/test_cite.py checks it in
# scripts of its own)
os.environ.setdefault("SIMPLYDATA_NO_CITE_LIST", "1")

import numpy as np
import pandas as pd
import pytest

from simplydata import _errors


@pytest.fixture(autouse=True)
def progress_in_a_temporary_file(tmp_path, monkeypatch):
    """sdata.start_30_days() and sdata.show_today() keep their progress in a temporary file, never in the home folder."""
    monkeypatch.setenv("SIMPLYDATA_PROGRESS_FILE", str(tmp_path / "simplydata_progress" / "progress.json"))
    yield


@pytest.fixture(autouse=True)
def fresh_old_name_notes():
    """Each test starts like a new session: an old name prints its note again the first time."""
    _errors._NOTED.clear()
    yield


@pytest.fixture
def marks():
    """A small class-marks table used by many tests."""
    rng = np.random.default_rng(1)
    names = ["Asha", "Ben", "Chen", "Dina"]
    rows = []
    for test in (1, 2, 3):
        for cls in ("A", "B"):
            for name in names:
                rows.append({"name": name, "class": cls, "test": test,
                             "marks": float(rng.integers(30, 100)), "height": float(rng.normal(150, 8))})
    return pd.DataFrame(rows)


# The R packages simplydata's words call (CI installs the same list: .github/workflows/tests.yml)
R_PACKAGES = ("survival", "vegan", "mice", "lme4", "betareg", "pscl", "car", "effectsize", "emmeans", "pbkrtest",
              "lmerTest", "afex", "geepack", "sandwich", "performance", "mgcv", "MASS", "nnet",
              "tseries", "lomb", "trend", "forecast", "changepoint",
              "pwr", "Exact", "exact2x2", "nortest", "BSDA", "rstatix", "DescTools", "FSA", "PMCMRplus",
              "multcompView", "TOSTER", "presize", "epiR", "pROC", "irr", "psych", "BlandAltmanLeh", "ppcor", "cocor",
              "outliers", "EnvStats",
              # S3a-2 (lines and curves)
              "drc", "segmented", "smatr", "mcr", "quantreg", "deming",
              # S3a-3 (checking and comparing)
              "nlme", "glmnet", "boot", "lmtest", "AICcmodavg",
              # S3b-3 (survival and person-time)
              "cmprsk", "adjustedCurves", "riskRegression", "KMsurv", "survRM2",
              # S3b-1 (combining studies): metafor (with its data package metadat); meta for the reliability study
              "metafor", "metadat", "meta",
              # S3b-2 (planning a study): gsDesign, powerSurvEpi and pwrss (pwrss is CRAN only, like presize)
              "gsDesign", "powerSurvEpi", "pwrss",
              # S3c-1 (communities and resistomes): zero replacement and log ratios; MCA; silhouettes and LDA
              "zCompositions", "compositions", "ca", "cluster", "MASS",
              # S3c-2 (hidden factors): GPArotation (the rotations of psych::fa) and lavaan; psych is listed above
              "GPArotation", "lavaan")


@pytest.fixture
def needs_r():
    """For tests of methods that call R (simplydata[r]): skipped where R, rpy2 or the R
    packages are missing, except when SIMPLYDATA_REQUIRE_R=1 (CI), where they must run."""
    import os

    from simplydata._r import r_ready

    if not r_ready(R_PACKAGES):
        listed = ", ".join(R_PACKAGES)
        if os.environ.get("SIMPLYDATA_REQUIRE_R") == "1":
            pytest.fail(f"SIMPLYDATA_REQUIRE_R=1 but R, rpy2 or one of the R packages {listed} is missing")
        pytest.skip(f"needs R with {listed} (pip install 'simplydata[r]')")


@pytest.fixture
def needs_control():
    """For tests of the measures that come from python-control (simplydata[systems]): skipped where it is
    not installed, except when SIMPLYDATA_REQUIRE_CONTROL=1 (CI), where they must run."""
    import os

    try:
        import control  # noqa: F401
    except ImportError:
        if os.environ.get("SIMPLYDATA_REQUIRE_CONTROL") == "1":
            pytest.fail("SIMPLYDATA_REQUIRE_CONTROL=1 but python-control is missing (pip install 'simplydata[systems]')")
        pytest.skip("needs python-control (pip install 'simplydata[systems]')")


# The places that are meant to run R (each calls simplydata._r.r_call). Reaching R from anywhere
# else is a mistake: a word that should work without R.
R_ENTRY_POINTS = {
    ("power.py", "_pwr"),
    ("table/patterns.py", "_r_kmeans"), ("table/patterns.py", "_r_nmds"), ("table/patterns.py", "_r_permanova"),
    ("table/survival.py", "cox_zph"), ("table/between.py", "__init__"), ("table/models.py", "_explain_imputed"),
    ("table/post_hoc.py", "pair_letters"), ("table/summaries.py", "_summary_interval"),
    ("power.py", "find_how_many_needed"), ("power.py", "_interval_width_needed"), ("power.py", "call"),
    ("table/accuracy_words.py", "roc_engine"), ("table/accuracy_words.py", "compare_accuracy"),
    ("table/risk_words.py", "_prop_test_one_sided"), ("table/agreement_words.py", "_icc"),
    ("table/agreement_words.py", "_krippendorff"), ("table/agreement_words.py", "_ccc"),
    ("table/agreement_words.py", "limits_of_agreement"), ("table/agreement_words.py", "reliability_of"),
    ("words/agreement_charts.py", "_roc_points"), ("words/agreement_charts.py", "trade_off_curve"),
    ("words/agreement_charts.py", "_draw_difference_dots"), ("words/agreement_charts.py", "difference_dots"),
    ("table/stat_tests.py", "_z_test"), ("table/stat_tests.py", "_trend_test"), ("table/stat_tests.py", "_counts_engine"),
    ("table/summaries.py", "_ordinal_association"), ("table/summaries.py", "_partial_correlation"),
    ("table/correlation_words.py", "compare_correlations"), ("table/rows.py", "_test_outliers"),
    ("table/models.py", "_glmer"), ("table/models_more.py", "fit_shares"), ("table/models_more.py", "fit_zeros"),
    ("table/anova_tables.py", "eta_squared"), ("table/anova_tables.py", "anova_glm"),
    ("table/anova_tables.py", "need_r_for"),
    ("table/models_r.py", "emmeans_table"), ("table/models_r.py", "lmer_r"), ("table/models_r.py", "geeglm_r"),
    ("table/models_r.py", "repeated_anova"), ("table/models_r.py", "group_influence"), ("table/models_r.py", "robust_cov"),
    ("table/models_r.py", "vif_r"), ("table/models_r.py", "gam_r"), ("table/models_r.py", "nakagawa_r"),
    ("table/models_r.py", "profile_intervals"),
    ("table/time_series.py", "check_steady_over_time"), ("_signals.py", "_lomb_scargle"),
    ("_trend_season.py", "_r_stl_periodic"), ("_trend_season.py", "_r_mann_kendall"),
    ("_forecast.py", "r_forecast"), ("_forecast.py", "r_change_points"), ("_smoothing.py", "smooth"),
    # S3a-2 (lines and curves)
    ("table/lines_r.py", "dose_response"), ("table/lines_r.py", "dose_response_curve"), ("table/lines_r.py", "bends"),
    ("table/lines_r.py", "two_error_line"), ("table/lines_r.py", "loess"), ("table/lines_r.py", "percentile_lines"),
    ("table/lines_r.py", "self_start"), ("table/lines_r.py", "power_transform"),
    # S3a-3 (checking and comparing)
    ("table/checking_r.py", "gls"), ("table/checking_r.py", "lasso"), ("table/checking_r.py", "left_out_rows"),
    ("table/checking_r.py", "hosmer"), ("table/checking_r.py", "model_contrasts"),
    ("table/checking_r.py", "group_levels"), ("table/checking_r.py", "nested_anova"),
    # S3b-3 (survival and person-time)
    ("table/survival_r.py", "risk_curves"), ("table/survival_r.py", "grays_test"), ("table/survival_r.py", "fine_gray"),
    ("table/survival_r.py", "survival_regression"), ("table/survival_r.py", "restricted_means"),
    ("table/survival_r.py", "rmst_difference"), ("table/survival_r.py", "life_table"),
    ("table/survival_r.py", "adjusted_curves"), ("table/survival_r.py", "cox_start_stop"),
    ("words/survival.py", "draw_risk_curves"),
    # S3b-1 (combining studies)
    ("table/meta_r.py", "combine"),
    # S3b-2 (planning a study)
    ("power_r.py", "_r"),
    # S3c-1 (communities and resistomes)
    ("table/community_r.py", "_need"),
    ("table/community_r.py", "_call"),
    ("table/community_r.py", "r_distances"),
    ("table/community_r.py", "diversity"),
    ("table/community_r.py", "richness_curves"),
    ("table/community_r.py", "log_ratios"),
    ("table/community_r.py", "principal_coordinates"),
    ("table/community_r.py", "constrained"),
    ("table/community_r.py", "anosim"),
    ("table/community_r.py", "simper"),
    ("table/community_r.py", "profile_correlation"),
    ("table/community_r.py", "silhouettes"),
    ("table/community_r.py", "discriminant"),
    ("table/community_r.py", "correspondence"),
    ("table/community_r.py", "multiple_correspondence"),
    ("words/community_charts.py", "draw_richness_curves"), ("words/community_charts.py", "_draw_richness"),
    # S3c-2 (hidden factors)
    ("table/factor_r.py", "explore"), ("table/factor_r.py", "confirm"),
}


def _through_r_entry_point(tb) -> bool:
    import traceback

    for frame in traceback.extract_tb(tb):
        path = frame.filename.replace("\\", "/")
        if any(path.endswith("simplydata/" + file) and frame.name == name for file, name in R_ENTRY_POINTS):
            return True
    return False


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """A test stopped by "R is not ready" (RMissing):
    - SIMPLYDATA_REQUIRE_R=1 (CI with R): fails, the R tests must run;
    - SIMPLYDATA_NO_R=1 (CI without R): skipped only when R was reached through one of
      R_ENTRY_POINTS (or the test asks for needs_r); otherwise it fails, so a word that should
      not need R is caught;
    - otherwise (a computer without R): skipped."""
    import os

    outcome = yield
    error = outcome.excinfo
    if error is None or os.environ.get("SIMPLYDATA_REQUIRE_R") == "1":
        return
    from simplydata._r import RMissing

    if not isinstance(error[1], RMissing):
        return
    if os.environ.get("SIMPLYDATA_NO_R") == "1" and not _through_r_entry_point(error[2]):
        return  # keep the failure: this code was not meant to need R
    outcome.force_exception(pytest.skip.Exception("needs R (pip install 'simplydata[r]' and R)"))
