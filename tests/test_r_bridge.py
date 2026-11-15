"""The bridge to R (simplydata._r): starting, messages, warnings and conversions."""

import numpy as np
import pytest

from simplydata import SimplydataError, _r
from simplydata._r import RMissing, _version_key, r_call


# ---------------------------------------------------------------- without R
def test_newest_r_folder_is_chosen_by_number():
    folders = [r"C:\Program Files\R\R-4.9.3", r"C:\Program Files\R\R-4.10.0", r"C:\Program Files\R\R-4.2.1"]
    assert max(folders, key=_version_key).endswith("R-4.10.0")


def test_r_that_did_not_start_says_why(monkeypatch):
    monkeypatch.setattr(_r, "_STATE", {"error": "R_HOME points to a folder without R", "missing": "R"})
    with pytest.raises(RMissing, match="R did not start: R_HOME points to a folder without R") as error:
        _r.need_r(("vegan",), "NMDS")
    assert "set the R_HOME environment variable" in str(error.value)


def test_missing_rpy2_says_restart(monkeypatch):
    monkeypatch.setattr(_r, "_STATE", {"error": "No module named 'rpy2'", "missing": "rpy2"})
    with pytest.raises(RMissing, match=r'pip install "simplydata\[r\]".*then restart Python'):
        _r.need_r(("vegan",), "NMDS")


# ---------------------------------------------------------------- with R
def test_messages_are_silent_and_warnings_become_notes(needs_r, capsys):
    assert r_call("message('hello from R'); print('printed'); 1")[0] == 1
    assert capsys.readouterr().out == ""
    assert r_call("warning('test warning'); 2", source="test")[0] == 2
    assert capsys.readouterr().out == "Note from R (test): test warning.\n"


def test_missing_values_go_to_r_as_na(needs_r):
    assert r_call("sum(is.na(x))", x=[1.0, None, 3.0])[0] == 1
    assert r_call("sum(is.na(x))", x=np.array([1.0, np.nan]))[0] == 1
    assert r_call("sum(is.na(x))", x=np.array(["a", None, "c"], dtype=object))[0] == 1
    assert r_call("is.logical(x) && sum(is.na(x)) == 1", x=np.array([True, None], dtype=object))[0]


def test_values_come_back_from_r(needs_r):
    assert r_call("NULL") is None
    assert r_call("factor(c('b', 'a', NA))").tolist() == ["b", "a", None]
    assert r_call("list(a = 1, b = 'x')")["b"].tolist() == ["x"]
    assert r_call("matrix(1:6, nrow = 2)").shape == (2, 3)


def test_too_big_whole_numbers_are_refused(needs_r):
    with pytest.raises(SimplydataError, match="too big to pass to R exactly"):
        r_call("x", x=np.array([2 ** 60], dtype=np.int64))
