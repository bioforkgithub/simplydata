import matplotlib

matplotlib.use("Agg")

import numpy as np
import pandas as pd
import pytest

from simplydata import _errors


@pytest.fixture(autouse=True)
def progress_in_a_temporary_file(tmp_path, monkeypatch):
    """sdata.start_30_days() and sdata.today() keep their progress in a temporary file, never in the home folder."""
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
R_PACKAGES = ("survival", "vegan", "mice", "tseries", "lomb", "trend", "forecast", "changepoint")


@pytest.fixture
def needs_r():
    """For tests of methods that call R (simplydata[r]): skipped where R, rpy2 or the R
    packages are missing, except when SIMPLYDATA_REQUIRE_R=1 (CI), where they must run."""
    import os

    from simplydata._r import r_ready

    if not r_ready(R_PACKAGES):
        if os.environ.get("SIMPLYDATA_REQUIRE_R") == "1":
            pytest.fail("SIMPLYDATA_REQUIRE_R=1 but R, rpy2 or one of the R packages is missing: " + ", ".join(R_PACKAGES))
        pytest.skip("needs R with " + ", ".join(R_PACKAGES) + " (pip install 'simplydata[r]')")


# The places that are meant to run R (each calls simplydata._r.r_call). Reaching R from anywhere
# else is a mistake: a word that should work without R.
R_ENTRY_POINTS = {
    ("table/patterns.py", "_r_kmeans"), ("table/patterns.py", "_r_nmds"), ("table/patterns.py", "_r_permanova"),
    ("table/survival.py", "cox_zph"), ("table/between.py", "__init__"), ("table/models.py", "_explain_imputed"),
    ("table/time_series.py", "check_steady"), ("_signals.py", "_lomb_scargle"),
    ("_trend_season.py", "_r_stl_periodic"), ("_trend_season.py", "_r_mann_kendall"),
    ("_forecast.py", "r_forecast"), ("_forecast.py", "r_change_points"),
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
