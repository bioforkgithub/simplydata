"""The bridge to R, for the methods that no Python package gives with R's answers.

simplydata calls established packages. Where Python has nothing that matches R (cox.zph,
k-means, non-metric MDS, betadisper, ...), it calls the R package itself through rpy2. This
needs R (https://cran.r-project.org) and the optional extra: pip install "simplydata[r]".

r_call() puts NumPy arrays into R, runs a piece of R code and gives back what it makes as
NumPy arrays (or plain Python numbers and lists). Without R, rpy2 or the R package, it raises
a friendly SimplydataError that says what to install; there is never an own fallback method.
"""

from __future__ import annotations

import contextlib
import io

import numpy as np

from ._errors import SimplydataError

_STATE: dict = {}


class RMissing(SimplydataError):
    """R, rpy2 or an R package is not there."""


def _install_text(packages, what, python_note=None) -> str:
    listed = ", ".join(f'"{p}"' for p in packages)
    missing = _STATE.get("missing", "package")
    lines = [f"{what} is done by R (the same code R users run), and R is not ready here."]
    if missing == "rpy2":
        lines.append('  - pip install "simplydata[r]"   (rpy2, the bridge from Python to R)')
    if missing in ("rpy2", "R"):
        lines.append("  - install R from https://cran.r-project.org (if R is installed but not found, set the "
                     "R_HOME environment variable to its folder)")
    if packages:
        lines.append(f"  - in R: install.packages(c({listed}))")
    if python_note:
        lines.append(f"({python_note})")
    return "\n".join(line for line in lines if line)


def _windows_paths():
    """On Windows, find R (R_HOME, else the newest R under Program Files) and put its DLL folder
    on PATH; without it R cannot load its own stats library."""
    import glob
    import os
    import sys

    if sys.platform != "win32":
        return
    home = os.environ.get("R_HOME")
    if not home:
        found = sorted(glob.glob(os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "R", "R-*")))
        if not found:
            return
        home = os.environ["R_HOME"] = found[-1]
    for folder in (os.path.join(home, "bin", "x64"), os.path.join(home, "bin")):
        if os.path.isdir(folder) and folder.lower() not in os.environ.get("PATH", "").lower():
            os.environ["PATH"] = folder + os.pathsep + os.environ.get("PATH", "")


def _start():
    """Start R once; remember why if it cannot start."""
    if "r" in _STATE or "error" in _STATE:
        return _STATE.get("r")
    _windows_paths()
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            import rpy2.robjects as ro

            # R may start without its default packages when rpy2 cannot ask R for its settings
            # (on Windows it looks for "sh"); load them by name so every method finds them
            ro.r("suppressMessages(for (p in c('stats', 'utils', 'methods', 'graphics', 'grDevices')) "
                 "library(p, character.only = TRUE))")
        _STATE["r"] = ro
    except Exception as error:  # noqa: BLE001 - any failure means "R is not ready"
        _STATE["error"] = str(error)
        _STATE["missing"] = "rpy2" if isinstance(error, ImportError) else "R"
    return _STATE.get("r")


def r_ready(packages=()) -> bool:
    """True when R starts and every package in packages is installed."""
    ro = _start()
    if ro is None:
        return False
    for package in packages:
        key = f"has:{package}"
        if key not in _STATE:
            # isTRUE(): requireNamespace() answers invisibly, and rpy2 gives None for an invisible answer
            _STATE[key] = bool(ro.r(
                f'local({{ ok <- FALSE; invisible(utils::capture.output(utils::capture.output('
                f'ok <- isTRUE(suppressWarnings(requireNamespace("{package}", quietly = TRUE))), type = "message"), '
                f'type = "output")); ok }})')[0])
        if not _STATE[key]:
            return False
    return True


def need_r(packages, what, python_note=None):
    """Raise RMissing with install steps unless R and the packages are ready."""
    if not r_ready(packages):
        if "missing" not in _STATE:
            _STATE["missing"] = "package"
        raise RMissing(_install_text(packages, what, python_note))


def _to_r(ro, value):
    if isinstance(value, (bool, np.bool_)):
        return ro.BoolVector([bool(value)])
    if isinstance(value, (int, float, np.integer, np.floating)):
        return ro.FloatVector([float(value)])
    if isinstance(value, str):
        return ro.StrVector([value])
    array = np.asarray(value)
    if array.dtype == bool:
        return ro.BoolVector(array.ravel().tolist())
    if array.dtype.kind in "iuf":
        flat = ro.FloatVector(array.astype(float).ravel(order="F").tolist())
        if array.ndim == 2:
            return ro.r["matrix"](flat, nrow=array.shape[0], ncol=array.shape[1])
        return flat
    return ro.StrVector([str(v) for v in array.ravel().tolist()])


def _from_r(value):
    if value.__class__.__name__ in ("ListVector", "ListSexpVector"):
        try:
            names = [str(n) for n in value.names]
        except TypeError:  # an unnamed list
            names = [str(i) for i in range(len(value))]
        return {name: _from_r(item) for name, item in zip(names, value)}
    array = np.asarray(value)
    dim = getattr(value, "dim", None)
    try:
        dims = tuple(int(d) for d in dim) if dim is not None else ()
    except TypeError:
        dims = ()
    if len(dims) == 2:
        array = array.reshape(dims, order="F") if array.ndim == 1 else array
    return array


def _say_warnings(messages, source) -> None:
    """Each distinct R warning once, as a plain note: Note from R (vegan::betadisper): ... ."""
    for message in dict.fromkeys(" ".join(str(m).split()) for m in messages):
        if message:
            print(f"Note from R ({source}): {message if message.endswith('.') else message + '.'}")


def r_call(code: str, packages=(), what="This", python_note=None, source=None, **values):
    """Run R code with values put in as R variables; give back the code's result as NumPy/Python.

    The last expression of code is the result; a named R list comes back as a dict. R's printing
    stays silent; each warning R gives is passed on once as a plain note, labelled with
    source= (such as "vegan::betadisper"), or with what= when no source is given."""
    need_r(packages, what, python_note)
    ro = _STATE["r"]
    env = ro.r["new.env"]()
    for name, value in values.items():
        env[name] = _to_r(ro, value)
    for package in packages:  # quietly: start-up messages and notes such as "S3 method overwritten" stay in R
        ro.r(f"invisible(utils::capture.output(utils::capture.output(suppressPackageStartupMessages("
             f"library({package})), type = 'message'), type = 'output'))")
    env["simplydata_code"] = ro.StrVector([code])
    try:
        # R's own printing stays out of the answer; its warnings are collected (and kept from
        # printing in R) so that simplydata can pass them on in plain words
        result = ro.r["eval"](ro.r["parse"](text=(
            "local({ out <- NULL; warns <- character(0); "
            "utils::capture.output(out <- withCallingHandlers(eval(parse(text = simplydata_code)), "
            "warning = function(w) { warns <<- c(warns, conditionMessage(w)); invokeRestart('muffleWarning') })); "
            "list(value = out, warnings = warns) })")), envir=env)
    except Exception as error:  # noqa: BLE001
        raise SimplydataError(f"R stopped with: {str(error).strip()}") from None
    found = _from_r(result)
    _say_warnings(np.atleast_1d(found.get("warnings", [])).tolist(), source or what)
    return found.get("value")
