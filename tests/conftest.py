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


@pytest.fixture
def needs_r():
    """For tests of methods that call R (simplydata[r]): skipped where R, rpy2 or the R
    packages are missing, except when SIMPLYDATA_REQUIRE_R=1 (CI), where they must run."""
    import os

    from simplydata._r import r_ready

    if not r_ready(("survival", "vegan", "mice")):
        if os.environ.get("SIMPLYDATA_REQUIRE_R") == "1":
            pytest.fail("SIMPLYDATA_REQUIRE_R=1 but R, rpy2 or the R packages survival, vegan, mice are missing")
        pytest.skip("needs R with survival, vegan and mice (pip install 'simplydata[r]')")
