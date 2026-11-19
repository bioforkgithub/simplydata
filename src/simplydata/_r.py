"""The bridge to R, for the methods that no Python package gives with R's answers.

simplydata calls established packages. Where Python has nothing that matches R (cox.zph,
k-means, non-metric MDS, betadisper, ...), it calls the R package itself through rpy2. This
needs R (https://cran.r-project.org) and the optional extra: pip install "simplydata[r]".

r_call() puts NumPy arrays into R, runs a piece of R code and gives back what it makes as
NumPy arrays (or plain Python numbers and lists). Without R, rpy2 or the R package, it raises
a friendly SimplydataError that says what to install; there is never an own fallback method.
R's printing and messages stay silent; R's warnings are passed on as plain notes.
"""

from __future__ import annotations

import contextlib
import io
import math
import os
import re
import sys
import threading

import numpy as np

from ._errors import SimplydataError

_STATE: dict = {}
_LOCK = threading.RLock()  # R runs one thing at a time; calls from several threads wait their turn
BIGGEST_EXACT = 2 ** 53  # whole numbers above this cannot be held exactly as R numbers (doubles)


class RMissing(SimplydataError):
    """R, rpy2 or an R package is not there."""


def _install_text(packages, what, python_note=None) -> str:
    listed = ", ".join(f'"{p}"' for p in packages)
    missing = _STATE.get("missing", "package")
    lines = [f"{what} is done by R (the same code R users run), and R is not ready here."]
    if missing == "rpy2":
        import sys

        if sys.platform == "win32":  # rpy2 has no ready-made wheel for every Windows Python (3.13: none)
            lines.append('  - on Windows, first: set RPY2_CFFI_MODE=ABI   (PowerShell: $env:RPY2_CFFI_MODE = "ABI")')
        lines.append('  - pip install "simplydata[r]"   (rpy2, the bridge from Python to R), then restart Python')
        lines.append("  - install R from https://cran.r-project.org")
    elif missing == "R":
        lines.append("  - R did not start: " + _STATE.get("error", "unknown error").strip().splitlines()[0][:300])
        lines.append("  - install R from https://cran.r-project.org if it is not installed; if it is, set the "
                     "R_HOME environment variable to its folder and restart Python")
    if packages:
        lines.append(f"  - in R: install.packages(c({listed}))")
    if python_note:
        lines.append(f"({python_note})")
    return "\n".join(lines)


def _version_key(folder):
    """R-4.10.0 after R-4.9.3: compare the numbers, not the text."""
    return tuple(int(n) for n in re.findall(r"\d+", os.path.basename(folder)))


def _windows_paths():
    """On Windows, find R (R_HOME, else the newest R under Program Files or the per-user
    Programs folder) and put its DLL folder on PATH; without it R cannot load its own stats
    library."""
    import glob

    if sys.platform != "win32":
        return
    home = os.environ.get("R_HOME")
    if not home:
        places = [os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "R"),
                  os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "R")]
        found = [f for place in places if place for f in glob.glob(os.path.join(place, "R-*"))]
        if not found:
            return
        home = os.environ["R_HOME"] = max(found, key=_version_key)
    for folder in (os.path.join(home, "bin", "x64"), os.path.join(home, "bin")):
        if os.path.isdir(folder) and folder.lower() not in os.environ.get("PATH", "").lower():
            os.environ["PATH"] = folder + os.pathsep + os.environ.get("PATH", "")


@contextlib.contextmanager
def _quiet_fds():
    """Silence everything written to the process's stdout and stderr, including programs that
    rpy2 starts (on Windows it asks a shell for R's settings and the shell complains)."""
    saved = []
    for stream in (sys.stdout, sys.stderr):  # what was printed before goes out first, not into the null device
        with contextlib.suppress(Exception):
            stream.flush()
    try:
        for fd in (1, 2):
            saved.append((fd, os.dup(fd)))
        null = os.open(os.devnull, os.O_WRONLY)
        for fd, _ in saved:
            os.dup2(null, fd)
        os.close(null)
    except OSError:  # no real file descriptors (some notebooks): fall back to Python-level quiet
        for fd, copy in saved:
            os.dup2(copy, fd)
            os.close(copy)
        saved = []
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            yield
    finally:
        for stream in (sys.stdout, sys.stderr):
            with contextlib.suppress(Exception):
                stream.flush()
        for fd, copy in saved:
            os.dup2(copy, fd)
            os.close(copy)


def _start():
    """Start R once; remember why if it cannot start."""
    with _LOCK:
        if "r" in _STATE or "error" in _STATE:
            return _STATE.get("r")
        _windows_paths()
        try:
            with _quiet_fds():
                import rpy2.rinterface_lib.callbacks as callbacks
                import rpy2.robjects as ro

                # R's console output is never shown; simplydata words the results itself
                callbacks.consolewrite_print = lambda text: None
                callbacks.consolewrite_warnerror = lambda text: None
                # R may start without its default packages when rpy2 cannot ask R for its settings
                # (on Windows it looks for "sh"); load them by name so every method finds them
                ro.r("invisible(utils::capture.output(suppressMessages(suppressWarnings(for (p in c('stats', 'utils', "
                     "'methods', 'graphics', 'grDevices')) library(p, character.only = TRUE)))))")
            _STATE["r"] = ro
        except Exception as error:  # noqa: BLE001 - any failure means "R is not ready"
            _STATE["error"] = str(error) or type(error).__name__
            _STATE["missing"] = "rpy2" if isinstance(error, ImportError) else "R"
        return _STATE.get("r")


def r_ready(packages=()) -> bool:
    """True when R starts and every package in packages is installed. Only a package that is
    there is remembered, so one installed during the session is found on the next call."""
    with _LOCK:
        ro = _start()
        if ro is None:
            return False
        for package in packages:
            key = f"has:{package}"
            if not _STATE.get(key):
                # isTRUE(): requireNamespace() answers invisibly, and rpy2 gives None for an invisible answer
                # inside R's own output capture too: loading can print notes such as
                # "Registered S3 method overwritten" (the same fix as on the v0.6 branch)
                _STATE[key] = bool(ro.r(
                    f'local({{ ok <- FALSE; invisible(utils::capture.output(utils::capture.output('
                    f'ok <- isTRUE(suppressMessages(suppressWarnings(requireNamespace("{package}", quietly = TRUE)))), '
                    f'type = "message"), type = "output")); ok }})')[0])
            if not _STATE[key]:
                return False
        return True


def need_r(packages, what, python_note=None):
    """Raise RMissing with install steps unless R and the packages are ready."""
    if not r_ready(packages):
        if "missing" not in _STATE:
            _STATE["missing"] = "package"
        raise RMissing(_install_text(packages, what, python_note))
    if _STATE.get("missing") == "package":  # a package that was missing has been installed since
        del _STATE["missing"]


def _is_missing(v) -> bool:
    return v is None or (isinstance(v, (float, np.floating)) and math.isnan(v))


def _to_r(ro, value):
    """A Python value as an R vector: numbers as doubles, True/False as logicals, text as
    characters; None and NaN become R's NA."""
    if value is None:
        return ro.NULL
    if isinstance(value, (bool, np.bool_)):
        return ro.BoolVector([bool(value)])
    if isinstance(value, str):
        return ro.StrVector([value])
    if isinstance(value, (int, float, np.integer, np.floating)):
        value = [value]
    array = np.asarray(value)
    if array.dtype.kind in "iu" and array.size and np.abs(array).max() > BIGGEST_EXACT:
        raise SimplydataError("A whole number is too big to pass to R exactly (above 2**53).")
    if array.dtype == bool:
        flat = ro.BoolVector(array.ravel(order="F").tolist())
    elif array.dtype.kind in "iuf":
        flat = ro.FloatVector([ro.NA_Real if math.isnan(v) else v for v in array.astype(float).ravel(order="F")])
    else:
        items = array.ravel(order="F").tolist()
        given = [v for v in items if not _is_missing(v)]
        if given and all(isinstance(v, (bool, np.bool_)) for v in given):
            flat = ro.BoolVector([ro.NA_Logical if _is_missing(v) else bool(v) for v in items])
        elif given and all(isinstance(v, (int, float, np.integer, np.floating)) for v in given):
            if any(isinstance(v, (int, np.integer)) and abs(int(v)) > BIGGEST_EXACT for v in given):
                raise SimplydataError("A whole number is too big to pass to R exactly (above 2**53).")
            flat = ro.FloatVector([ro.NA_Real if _is_missing(v) else float(v) for v in items])
        else:
            flat = ro.StrVector([ro.NA_Character if _is_missing(v) else str(v) for v in items])
    if array.ndim == 2:
        return ro.r["matrix"](flat, nrow=array.shape[0], ncol=array.shape[1])
    return flat


def _from_r(value):
    """An R value as Python: NULL -> None, a named list -> dict, a factor -> its labels,
    a matrix -> a 2-D array, any other vector -> a NumPy array."""
    kind = value.__class__.__name__
    if kind in ("NULLType", "RNULLType") or value is None:
        return None
    if kind in ("ListVector", "ListSexpVector"):
        try:
            names = [str(n) for n in value.names]
        except TypeError:  # an unnamed list
            names = [str(i) for i in range(len(value))]
        return {name: _from_r(item) for name, item in zip(names, value)}
    if kind == "FactorVector":
        levels = [str(level) for level in value.levels]
        codes = np.asarray(value).astype(np.int64)  # R's NA code is the smallest integer
        return np.array([levels[c - 1] if 1 <= c <= len(levels) else None for c in codes], dtype=object)
    array = np.asarray(value)
    dim = getattr(value, "dim", None)
    try:
        dims = tuple(int(d) for d in dim) if dim is not None else ()
    except TypeError:
        dims = ()
    if len(dims) == 2:
        array = array.reshape(dims, order="F") if array.ndim == 1 else array
    return array


def _say_warnings(messages, source, note_words=None) -> None:
    """Each distinct R warning once, as a plain note: Note from R (vegan::betadisper): ... ; note_words=,
    if given, rewrites each one (such as codes sent to R back into the names in the table)."""
    for message in dict.fromkeys(" ".join(str(m).split()) for m in messages):
        message = note_words(message) if note_words else message
        if message:
            print(f"Note from R ({source}): {message if message.endswith('.') else message + '.'}")


def r_call(code: str, packages=(), what="This", python_note=None, source=None, note_words=None, **values):
    """Run R code with values put in as R variables; give back the code's result as NumPy/Python.

    The last expression of code is the result; a named R list comes back as a dict. R's printing
    and messages stay silent; each warning R gives is passed on once as a plain note, labelled
    with source= (such as "vegan::betadisper"), or with what= when no source is given; note_words= (a
    function of the note) rewrites each note first."""
    need_r(packages, what, python_note)
    with _LOCK:
        ro = _STATE["r"]
        env = ro.r["new.env"]()
        for name, value in values.items():
            env[name] = _to_r(ro, value)
        env["simplydata_code"] = ro.StrVector([code])
        env["simplydata_packages"] = ro.StrVector(list(packages))
        try:
            # R's own printing stays out of the answer; messages are muffled; warnings are
            # collected (and kept from printing in R) so that simplydata can pass them on
            result = ro.r["eval"](ro.r["parse"](text=(
                "local({ out <- NULL; warns <- character(0); "
                "utils::capture.output(out <- withCallingHandlers({ "
                # the loop variable has a simplydata_ name so it cannot overwrite a value called p
                "for (simplydata_package in simplydata_packages) invisible(utils::capture.output("
                "utils::capture.output(suppressPackageStartupMessages(library(simplydata_package, "
                "character.only = TRUE)), type = 'message'))); "
                "eval(parse(text = simplydata_code)) }, "
                "warning = function(w) { warns <<- c(warns, conditionMessage(w)); invokeRestart('muffleWarning') }, "
                "message = function(m) invokeRestart('muffleMessage'))); "
                "list(value = out, warnings = warns) })")), envir=env)
        except Exception as error:  # noqa: BLE001
            raise SimplydataError(f"R stopped with: {str(error).strip()}") from None
        found = _from_r(result)
    warnings = found.get("warnings")
    _say_warnings([] if warnings is None else np.atleast_1d(warnings).tolist(), source or what, note_words)
    return found.get("value")
