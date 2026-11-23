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


# Privacy: the R code simplydata runs never reaches the internet, installs anything or writes a file. R does its
# own networking (libcurl, sockets) and file writing, out of Python's sight, so r_call() refuses code that names a
# known network, install or file-writing function; tests/test_privacy.py checks every R code string in the source
# against the same list. It is a check of simplydata's own R code (a second line of defence), not a sandbox.
_R_FUNCTIONS_NOT_ALLOWED = (
    # the internet, installs and other programs
    "download.file", "download.packages", "install.packages", "update.packages", "available.packages", "url",
    "gzcon", "socketConnection", "socketAccept", "serverSocket", "make.socket", "browseURL", "curlGetHeaders",
    "system", "system2", "shell", "shell.exec", "pipe", ".Internal",
    # files (reading by name too: file() and friends open any address)
    "file", "gzfile", "bzfile", "xzfile", "unz", "fifo", "sink", "saveRDS", "save", "save.image", "serialize",
    "writeLines", "writeBin", "writeChar", "write.csv", "write.csv2", "write.table", "write", "dput", "dump",
    "file.create", "file.copy", "dir.create", "Rprof",
    # pictures written to a file
    "png", "jpeg", "tiff", "bmp", "svg", "postscript", "cairo_pdf", "cairo_ps", "ggsave", "dev.copy", "dev.print",
)
_R_PACKAGES_NOT_ALLOWED = ("curl", "httr", "httr2", "RCurl", "httpuv", "websocket", "remotes", "devtools", "pak",
                           "BiocManager", "pins", "piggyback", "googledrive", "googlesheets4", "aws.s3", "DBI", "odbc",
                           "RPostgres", "RMySQL", "mongolite", "redux", "svglite", "ggplot2")
_NAMES = "|".join(re.escape(name) for name in _R_FUNCTIONS_NOT_ALLOWED)
R_NOT_ALLOWED = re.compile(
    r"://"  # any web, ftp or file address
    rf"|(?<![\w.])(?:{_NAMES})\s*\("
    rf"|(?<![\w.])(?:get|get0|mget|match\.fun|do\.call|Map|lapply|sapply|vapply)\s*\([^()]*[\"'`]?(?:{_NAMES})\b"
    r"|(?<![\w.])pdf\s*\((?!\s*(?:file\s*=\s*)?NULL\s*\))"  # pdf(NULL) draws into nothing; pdf("x.pdf") is a file
    r"|(?<![\w.])(?:cat|capture\.output|print)\s*\((?:[^()]|\([^()]*\))*(?<![\w.])file\s*="  # (one level inside)
    r"|`[\w.]+`\s*\("  # a function called by its quoted name: `download.file`(...)
    rf"|(?<![\w.])(?:{'|'.join(re.escape(p) for p in _R_PACKAGES_NOT_ALLOWED)})\s*::")


def refuse_unsafe_r_code(code: str) -> None:
    """Raise SimplydataError when R code could reach the internet, install a package or write a file."""
    found = R_NOT_ALLOWED.search(code)
    if found:
        raise SimplydataError(
            f"simplydata does not run R code that could reach the internet or write a file ({found.group(0)!r}).\n"
            "This is a promise for people who work with sensitive data: your data stays on your computer.")


# R packages that come from Bioconductor (installed with BiocManager), not from CRAN
BIOCONDUCTOR = ("qvalue",)


def _install_text(packages, what, python_note=None) -> str:
    missing = _STATE.get("missing", "package")
    lines = [f"{what} is done by R (the same code R users run), and R is not ready here."]
    if missing == "rpy2":
        import sys

        if sys.platform == "win32":  # rpy2 has no ready-made wheel for every Windows Python (3.13: none)
            lines.append('  - on Windows, first: set RPY2_CFFI_MODE=ABI   (PowerShell: $env:RPY2_CFFI_MODE = "ABI")')
        lines.append('  - pip install "simplydata[r]"   (rpy2, the bridge from Python to R), then restart Python')
        lines.append("  - install R from https://cran.r-project.org")
    elif missing == "R":
        lines += _r_start_text()
    cran = [p for p in packages if p not in BIOCONDUCTOR]
    if cran:
        lines.append("  - in R: install.packages(c(" + ", ".join(f'"{p}"' for p in cran) + "))")
    for name in (p for p in packages if p in BIOCONDUCTOR):
        lines.append(f'  - {name} is on Bioconductor, not CRAN: in R: install.packages("BiocManager"), then install '
                     f'"{name}" with BiocManager (https://bioconductor.org/packages/{name}); with conda: '
                     f"bioconductor-{name.lower()} from bioconda")
    if python_note:
        lines.append(f"({python_note})")
    return "\n".join(lines)


def _r_start_text() -> list:
    """Why R did not start, in plain words: R not found, or found but not started from Python. rpy2's own error
    (such as "list index out of range") says nothing to a reader, so it is not shown."""
    import shutil

    home = os.environ.get("R_HOME")
    if not home and not shutil.which("R") and not shutil.which("Rscript"):
        return ["  - R was not found on this computer: install R from https://cran.r-project.org, then restart Python",
                "  - if R is installed in a folder of your own, set the R_HOME environment variable to that folder "
                "and restart Python"]
    if home and not os.path.isdir(os.path.join(home, "bin")):
        return [f"  - R_HOME is set to {home}, but that folder has no R in it (no bin folder)",
                "  - set R_HOME to the folder R is installed in (the one that holds bin), or install R from "
                "https://cran.r-project.org, then restart Python"]
    where = f" (in {home})" if home else ""
    lines = [f"  - R is installed{where} but did not start from Python"]
    if sys.platform == "win32":
        lines.append("  - on Windows, start Python from PowerShell or the Command Prompt (cmd): from Git Bash or "
                     "another Unix-like shell rpy2 cannot ask R for its settings")
    lines.append("  - check that R_HOME is the folder of the R you want (the one that holds bin), then restart Python")
    return lines


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
                # a method that draws (plot = TRUE by default somewhere) draws into nothing, never into an
                # Rplots.pdf file in your folder
                ro.r("options(device = function(...) grDevices::pdf(file = NULL))")
            _STATE["r"] = ro
            from ._cite import register_at_exit

            register_at_exit()  # the list of packages used is printed before rpy2 shuts R down
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
            if package in ("agricolae", "AlgDesign") and not _STATE.get("model.matrix kept"):
                _keep_base_model_matrix(ro)
        return True


def _keep_base_model_matrix(ro) -> None:
    """agricolae imports AlgDesign, whose namespace registers its own model.matrix.formula for the whole R session;
    it stops with "data must be a data.frame" when no data are given, as R metafor's formulas do (combine_studies
    with subgroups). simplydata uses no AlgDesign function, so the method is taken out again and R's own
    model.matrix.default answers, as before agricolae was loaded."""
    ro.r('local({ tbl <- get(".__S3MethodsTable__.", envir = asNamespace("stats")); '
         'f <- tbl[["model.matrix.formula"]]; '
         'if (!is.null(f) && environmentName(environment(f)) == "AlgDesign") rm("model.matrix.formula", envir = tbl) })')
    _STATE["model.matrix kept"] = True


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
        codes = np.array(value, copy=True).astype(np.int64)  # R's NA code is the smallest integer
        return np.array([levels[c - 1] if 1 <= c <= len(levels) else None for c in codes], dtype=object)
    # A copy, never a view: np.asarray on an rpy2 vector points straight into R's memory without keeping
    # the R object alive, so after R collects it the array would silently fill with other data.
    array = np.array(value, copy=True)
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


def r_call(code: str, packages=(), what="This", python_note=None, source=None, note_words=None, _cite=True,
           **values):
    """Run R code with values put in as R variables; give back the code's result as NumPy/Python.

    The last expression of code is the result; a named R list comes back as a dict. R's printing
    and messages stay silent; each warning R gives is passed on once as a plain note, labelled
    with source= (such as "vegan::betadisper"), or with what= when no source is given; note_words= (a
    function of the note) rewrites each note first. Once R has answered, R, the packages and the pkg:: names in
    code are remembered for sdata.show_packages_used() (not with _cite=False). Code that could reach the internet
    or write a file is refused (refuse_unsafe_r_code)."""
    refuse_unsafe_r_code(code)
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
    if _cite:
        from ._cite import record_r

        record_r(packages, code)
    warnings = found.get("warnings")
    _say_warnings([] if warnings is None else np.atleast_1d(warnings).tolist(), source or what, note_words)
    return found.get("value")


_FACTS_CODE = r"""
local({
  one <- function(p) {
    x <- tryCatch(suppressWarnings(utils::citation(p)), error = function(e) NULL)
    d <- suppressWarnings(utils::packageDescription(p))
    source <- if (p == "base") "R" else if (!is.null(d$Priority) && d$Priority == "base") "R" else
      if (!is.null(d$biocViews)) "Bioconductor" else if (is.null(d$Repository)) "unknown" else
      if (d$Repository %in% c("CRAN", "RSPM", "P3M")) "CRAN" else
      if (grepl("r-universe", d$Repository, fixed = TRUE)) "R-universe" else d$Repository
    version <- if (p == "base") paste(R.version$major, R.version$minor, sep = ".") else
      as.character(utils::packageVersion(p))
    first <- ""; many <- FALSE; year <- ""; title <- ""; link <- ""
    if (length(x)) {
      e <- unclass(x)[[1]]
      a <- e$author
      if (length(a)) {
        fam <- a[[1]]$family; giv <- a[[1]]$given
        first <- paste(if (length(fam)) fam else giv, collapse = " ")
        many <- length(a) > 1
      }
      if (!is.null(e$year)) year <- as.character(e$year)
      if (!is.null(e$title)) title <- gsub("[{}]", "", as.character(e$title))
      link <- if (!is.null(e$doi)) paste0("doi:", e$doi) else if (!is.null(e$url)) as.character(e$url) else ""
    }
    list(version = version, source = source, first = first, many = many, year = year, title = title,
         link = link,
         text = if (length(x)) paste(gsub("\\s+", " ", format(x, style = "text")), collapse = " ") else "",
         bibtex = if (length(x)) paste(as.character(utils::toBibtex(x)), collapse = "\n") else "")
  }
  out <- lapply(simplydata_wanted, function(p) tryCatch(one(p), error = function(e) list(version = "")))
  names(out) <- simplydata_wanted
  out
})
"""


def r_package_facts(packages) -> dict:
    """{package: facts} for sdata.show_packages_used(): version (packageVersion()), source (CRAN, Bioconductor,
    R for R's own packages) and references (utils::citation(): as text and as toBibtex()). "base" is R itself."""
    found = r_call(_FACTS_CODE, _cite=False, simplydata_wanted=list(packages)) or {}
    out = {}
    for package, raw in found.items():
        def one(name, default=""):
            value = raw.get(name)
            if value is None or not np.size(value):
                return default
            return np.atleast_1d(value).tolist()[0]

        version = str(one("version"))
        if not version:
            continue
        first, year, title, link = str(one("first")), str(one("year")), str(one("title")), str(one("link"))
        who = (first + (" et al." if bool(one("many", False)) else "")).strip() or package
        short = f"{who} ({year})" if year else who
        out[package] = dict(name=package, version=version, language="R", source=str(one("source")),
                            one_line=", ".join(p for p in (short, title, link) if p),
                            text=str(one("text")) or f'type citation("{package}") in R',
                            bibtex=str(one("bibtex")), cite=f"{who} {year}".strip())
    return out
