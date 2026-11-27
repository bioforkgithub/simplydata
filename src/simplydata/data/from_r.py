"""sdata.get_example(name, from_r_package="survival"): a dataset shipped with an installed R package, as a simplydata
table. R itself loads it (utils::data(list = name, package =), the dataset as R users get it); simplydata only turns
R's columns into a table: factors become text, R's NA becomes an empty cell, dates stay dates, and row names that
carry information (such as mtcars's car names) become a first column "row name". Nothing is downloaded or installed:
the R package must already be installed (needs simplydata[r])."""

from __future__ import annotations

import re

import numpy as np

from .._errors import SimplydataError

ROW_NAME_COLUMN = "row name"
_PACKAGE_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9.]*[A-Za-z0-9]$")  # an R package name (CRAN's rule)

_R_LOAD = """
if (!requireNamespace(pkg, quietly = TRUE)) stop("simplydata_no_package")
e <- new.env()
listed <- utils::data(package = pkg)$results
full <- if (length(listed)) listed[, "Item"] else character(0)
items <- sub(" .*", "", full)
# "lung (cancer)": the object lung is kept in the data file cancer
files <- ifelse(grepl("(", full, fixed = TRUE), sub(")", "", sub(".*[(]", "", full), fixed = TRUE), items)
if (!(name %in% items)) {
  list(found = FALSE, items = items)
} else {
  loaded <- suppressWarnings(utils::data(list = files[match(name, items)], package = pkg, envir = e))
  x <- if (exists(name, envir = e, inherits = FALSE)) base::get(name, envir = e, inherits = FALSE) else NULL
  if (stats::is.ts(x)) {
    m <- as.matrix(x)
    x <- data.frame(time = as.numeric(stats::time(x)), m, check.names = FALSE)
    if (ncol(m) == 1) names(x)[2] <- name
  } else if (is.table(x)) {
    x <- as.data.frame(x, stringsAsFactors = FALSE)
  } else if (is.matrix(x)) {
    x <- as.data.frame(x, stringsAsFactors = FALSE)
  }
  if (!is.data.frame(x)) {
    list(found = TRUE, table = FALSE, what = class(x)[1])
  } else {
    one <- function(v) {
      if (!is.null(dim(v))) v <- apply(as.matrix(v), 1, paste, collapse = " ")
      kind <- if (inherits(v, "Date")) "date" else if (inherits(v, "POSIXt")) "datetime" else
        if (is.logical(v)) "logical" else if (is.numeric(v) && !is.factor(v)) "number" else "text"
      gone <- which(is.na(v))
      shown <- if (kind == "number") as.numeric(v) else if (kind == "date") format(v, "%Y-%m-%d") else
        if (kind == "datetime") format(v, "%Y-%m-%d %H:%M:%S") else as.character(v)
      if (kind != "number") shown[is.na(shown)] <- ""
      list(kind = kind, values = shown, gone = gone)
    }
    automatic <- is.integer(attr(x, "row.names")) ||
      identical(rownames(x), as.character(seq_len(nrow(x))))
    list(found = TRUE, table = TRUE, names = names(x), columns = unname(lapply(x, one)),
         rows = nrow(x), rownames = if (automatic) character(0) else rownames(x))
  }
}
"""


def from_r_package(name, package):
    """The dataset name of the installed R package as a simplydata table (see the module's docstring)."""
    import pandas as pd

    from .._r import need_r, r_call

    if not isinstance(package, str) or not _PACKAGE_NAME.match(package.strip()):
        raise SimplydataError('from_r_package= is the name of an installed R package, in quotes, such as '
                              'sdata.get_example("lung", from_r_package="survival").')
    package = package.strip()
    if not isinstance(name, str) or not name.strip():
        raise SimplydataError(f'get_example() needs the name of a dataset of the R package {package}, such as '
                              'sdata.get_example("lung", from_r_package="survival").')
    name = name.strip()
    need_r((), f'Loading "{name}" from the R package {package}')
    try:
        out = r_call(_R_LOAD, what=f'Loading "{name}" from the R package {package}', source=f"utils::data",
                     _cite=False, name=name, pkg=package)
    except SimplydataError as error:
        if "simplydata_no_package" in str(error):
            raise SimplydataError(
                f'The R package {package} is not installed, so "{name}" cannot be loaded from it. simplydata never '
                f'installs anything itself; to install it, in R: install.packages("{package}")') from None
        raise
    if not bool(np.atleast_1d(out["found"])[0]):
        items = [str(i) for i in np.atleast_1d(out.get("items") if out.get("items") is not None else [])]
        from .._errors import suggest

        guess = suggest(name, items, n=1) if items else []
        lines = [f'The R package {package} has no dataset called "{name}".']
        if guess:
            lines.append(f'Did you mean sdata.get_example("{guess[0]}", from_r_package="{package}")?')
        if items:
            shown = ", ".join(items[:40]) + (f" ... ({len(items)} in all)" if len(items) > 40 else "")
            lines.append(f"Its datasets: {shown}")
        else:
            lines.append("It ships no datasets.")
        raise SimplydataError("\n".join(lines))
    if not bool(np.atleast_1d(out["table"])[0]):
        what = str(np.atleast_1d(out["what"])[0])
        raise SimplydataError(f'"{name}" in the R package {package} is not a table (R calls it a "{what}"), so it '
                              "cannot become a simplydata table.")
    names = [str(n) for n in np.atleast_1d(out["names"])]
    columns = {}
    kinds = []
    if len(set(names)) < len(names):
        twice = next(n for n in names if names.count(n) > 1)
        raise SimplydataError(f'"{name}" in the R package {package} has two columns called "{twice}", so it cannot '
                              "become a simplydata table as it is.")
    for column_name, column in zip(names, out["columns"].values()):
        kind = str(np.atleast_1d(column["kind"])[0])
        kinds.append(kind)
        values = np.atleast_1d(column["values"])
        gone = np.atleast_1d(column["gone"]).astype(int) - 1 if column.get("gone") is not None else []
        if kind == "number":
            series = pd.Series(values.astype(float))
            whole = series.notna().all() and np.allclose(series, np.round(series)) and series.abs().max() < 2 ** 53
            if len(series) and whole:
                series = series.astype("int64")
        elif kind == "logical":
            series = pd.Series([v == "TRUE" for v in values.tolist()], dtype=object)
            series.iloc[list(gone)] = None
        elif kind in ("date", "datetime"):
            missing = set(int(i) for i in gone)
            series = pd.to_datetime(pd.Series([None if i in missing else v for i, v in enumerate(values.tolist())]))
        else:
            series = pd.Series([str(v) for v in values.tolist()], dtype=object)
            series.iloc[list(gone)] = None
        columns[column_name] = series
    frame = pd.DataFrame(columns)
    row_names = out.get("rownames")
    has_names = row_names is not None and len(np.atleast_1d(row_names)) == len(frame) and len(frame)
    if has_names:
        frame.insert(0, ROW_NAME_COLUMN if ROW_NAME_COLUMN not in frame.columns else "R row name",
                     [str(v) for v in np.atleast_1d(row_names).tolist()])
    from .._cite import record_r

    record_r((package,), "")
    from ..table.table import table

    made = table(frame)
    texts = sum(k == "text" for k in kinds)
    empty = int(frame.isna().sum().sum())
    rows, columns = len(frame), frame.shape[1]
    print(f'Loaded "{name}" from the R package {package}: {rows:,} row{"" if rows == 1 else "s"}, '
          f'{columns} column{"" if columns == 1 else "s"} (R utils::data('
          f'{name}, package = "{package}")).'
          + (" Groups (factors) became text." if texts else "")
          + (f" {empty:,} empty cell{'s' if empty != 1 else ''} (R's NA)." if empty else "")
          + (' Its row names are the first column, "row name".' if has_names else ""))
    return made
