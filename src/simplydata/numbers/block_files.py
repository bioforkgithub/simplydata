"""Blocks of numbers from files and back (NumPy + SciPy phase, batch 2; approved by Manish 2026-11-25).

    sst = sdata.number_block("sst_monthly.nc", values="sst")     one block per variable (decision 2)
    sdata.number_block("argo_*.nc", values="temp")                 several files joined by their labels
    sdata.number_block("sst.nc", values=["u", "v"])                 two variables stacked as a new direction "variable"
    sdata.number_block("big.nc", values="sst", keep_on_disk=True)   the numbers stay in the file until a word needs them
    sst.save("out.nc")                                              netCDF, compressed
    sdata.show_whats_inside("sst_monthly.nc")                       names, sizes and units; nothing is loaded

Every reading and writing step is xarray's (open_dataset, combine_by_coords, to_netcdf) with the h5netcdf engine for
netCDF-4 files and SciPy's engine for classic netCDF-3 files; NumPy reads .npy and .npz headers, openpyxl the sheets
of an Excel file. xarray and h5netcdf are the optional extra simplydata[xarray] (decision 3).

Privacy (sensitive data): these words read and write local files only. A web address or any "scheme://" path
(http, https, s3, OPeNDAP ...) is refused before anything is opened, so nothing goes over the network; the file is
handed to xarray as an absolute local path with the engine named, so xarray never guesses a remote backend, and
nothing is cached or downloaded.
"""

from __future__ import annotations

import glob as _glob
import os
import re
from pathlib import Path

import numpy as np

from .._errors import SimplydataError
from ._directions import say_shape

INSTALL = 'pip install "simplydata[xarray]"'
NETCDF_ENDINGS = (".nc", ".nc4", ".cdf", ".netcdf")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*://")
_HDF5_MAGIC = b"\x89HDF\r\n\x1a\n"


# ---------------------------------------------------------------------- local files only
def is_file_name(value) -> bool:
    return isinstance(value, (str, os.PathLike)) and not isinstance(value, bytes)


def refuse_network_path(text: str, step: str) -> None:
    """Refuse, before anything is opened or resolved, every name that could reach another computer: a web address or
    any scheme:// (http, s3, OPeNDAP, file:// ...), a network share (\\\\server\\share or //server/share) and an fsspec
    chain ("simplecache::x.nc")."""
    stripped = text.strip()
    why = None
    if _SCHEME.match(stripped) or stripped.lower().startswith(("http:", "https:", "s3:", "gs:", "ftp:")):
        why = "web addresses"
    elif stripped.startswith(("\\\\", "//", "\\/", "/\\")):
        why = "network shares (\\\\server\\share or //server/share)"
    elif "::" in stripped:
        why = 'chains of other tools ("simplecache::...")'
    if why:
        raise SimplydataError(
            f"{step} reads and writes files on this computer only, so it does not open {why} (\"{text}\"). This keeps "
            "sensitive data off the network. Copy the file to this computer yourself, then give its name, such as "
            "\"sst.nc\".")


def local_path(name, step: str) -> Path:
    """The file as an absolute local path; network names are refused first (no network)."""
    text = os.fspath(name)
    if not isinstance(text, str):
        raise SimplydataError(f"{step} needs a file name in quotes, such as \"sst.nc\".")
    refuse_network_path(text, step)
    path = Path(text).expanduser().resolve()
    refuse_network_path(str(path), step)  # a mapped name that resolves to a share
    return path


def _existing(path: Path, step: str) -> Path:
    if not path.is_file():
        from .._data import _missing_file_error

        raise _missing_file_error(path)
    return path


def need_xarray(step: str, engine: bool = False):
    """xarray (and, for netCDF-4 files, h5netcdf), or a plain error with the install line."""
    try:
        import xarray
    except ImportError:
        raise SimplydataError(f"{step} needs xarray, the optional extra for labelled blocks and netCDF files.\n"
                              f"Install it with:  {INSTALL}") from None
    if engine:
        try:
            import h5netcdf  # noqa: F401
            import h5py  # noqa: F401
        except ImportError:
            raise SimplydataError(f"{step} needs h5netcdf (with h5py) to read and write netCDF-4 files.\n"
                                  f"Install them with:  {INSTALL}") from None
    return xarray


def engine_for(path: Path) -> str:
    """h5netcdf for netCDF-4 (an HDF5 file), scipy for classic netCDF-3; read from the file's first bytes."""
    with open(path, "rb") as handle:
        start = handle.read(8)
    if start.startswith(_HDF5_MAGIC):
        return "h5netcdf"
    if start[:3] == b"CDF":
        return "scipy"
    raise SimplydataError(f'"{path.name}" is not a netCDF file (netCDF-4 or classic netCDF-3). simplydata reads '
                          ".nc files; for tables use sdata.table(...).")


def check_no_links_out(path: Path, step: str) -> None:
    """Refuse a netCDF-4 (HDF5) file whose variables come from another file: an external link or a virtual dataset
    would make the word read a file you never named, perhaps on another computer. Checked with h5py before xarray
    opens the file (opening alone follows nothing; reading would)."""
    import h5py

    found = []
    with h5py.File(path, "r") as handle:
        seen = set()

        def walk(group, prefix):
            if group.id.__hash__() in seen:
                return
            seen.add(group.id.__hash__())
            for key in group.keys():
                link = group.get(key, getlink=True)
                where = f"{prefix}{key}"
                if isinstance(link, h5py.ExternalLink):
                    found.append(f'"{where}" (a link to {link.filename})')
                    continue
                if isinstance(link, h5py.SoftLink):
                    target = group.get(key)
                    if target is None:
                        found.append(f'"{where}" (a link to {link.path}, which is not in the file)')
                    continue
                item = group.get(key)
                if isinstance(item, h5py.Dataset) and item.is_virtual:
                    sources = sorted({vs.file_name for vs in item.virtual_sources()})
                    found.append(f'"{where}" (made from {", ".join(sources)})')
                elif isinstance(item, h5py.Group):
                    walk(item, f"{where}/")

        walk(handle, "")
    if found:
        raise SimplydataError(
            f"{step} does not read \"{path.name}\": the variable {found[0]} comes from another file, so reading it "
            "would open a file you did not name (perhaps on another computer). simplydata reads only numbers stored in "
            "the file itself. Copy the numbers into the file, or open that file yourself."
            + (f" Other variables like this: {', '.join(found[1:])}." if len(found) > 1 else ""))


def _open(path: Path, step: str):
    """One local netCDF file as an xarray Dataset (lazy: only its labels are read)."""
    engine = engine_for(path)
    xr = need_xarray(step, engine=engine == "h5netcdf")
    if engine == "h5netcdf":
        check_no_links_out(path, step)
    return xr.open_dataset(path, engine=engine, cache=False), engine


def _files(name, step: str) -> list[Path]:
    text = os.fspath(name)
    if any(ch in text for ch in "*?["):
        refuse_network_path(text, step)  # before looking for files
        found = sorted(Path(p).resolve() for p in _glob.glob(os.path.expanduser(text)))
        found = [p for p in found if p.is_file()]
        if not found:
            raise SimplydataError(f'No file matches "{text}". simplydata is looking in: {Path(".").resolve()}')
        return found
    return [_existing(local_path(text, step), step)]


# ---------------------------------------------------------------------- what a block says about its labels
def _say_labels(name, labels) -> str:
    labels = np.asarray(labels)
    if labels.size == 0:
        return ""
    if labels.dtype.kind == "M":
        first, last = (str(np.datetime_as_string(x, unit="D")) for x in (labels[0], labels[-1]))
    elif labels.dtype.kind in "iuf":
        first, last = (f"{float(x):g}" for x in (labels[0], labels[-1]))
    else:
        first, last = str(labels[0]), str(labels[-1])
    down = ""
    if labels.size > 1 and labels.dtype.kind in "iufM":
        if (labels[1:] < labels[:-1]).all():
            down = " (runs downward)"
    return f"{name} from {first} to {last}{down}" if first != last else f"{name} {first}"


def describe(name, values, names, labels, attrs) -> str:
    units = attrs.get("units")
    text = f"{name}: {say_shape(np.shape(values), names)}" + (f", {units}" if units else "")
    said = [_say_labels(n, labels[n]) for n in names if n in labels]
    return text + "".join(f"; {s}" for s in said if s)


# ---------------------------------------------------------------------- reading a block
def _pick_values(ds, values, path_words: str, step: str):
    variables = [str(v) for v in ds.data_vars]
    example = f'sdata.number_block("{path_words}", values="{variables[0] if variables else "sst"}")'
    if not variables:
        raise SimplydataError(f'"{path_words}" holds no variables of numbers.')
    if values is None:
        if len(variables) == 1:
            print(f'The file holds one variable, "{variables[0]}"; values= names it next time.')
            return ds[variables[0]], variables[0]
        raise SimplydataError(f"The file holds {len(variables)} variables: " + ", ".join(variables)
                              + f". values= says which one.\nFor example:  {example}")
    wanted = [values] if isinstance(values, str) else values
    if (not isinstance(wanted, (list, tuple)) or not wanted
            or not all(isinstance(v, str) for v in wanted)):
        raise SimplydataError(f"values= needs a variable name in quotes, or a list of them.\nFor example:  {example}")
    missing = [v for v in wanted if v not in ds.data_vars]
    if missing:
        from .._errors import suggest

        guess = suggest(missing[0], variables)
        hint = f' Did you mean "{guess[0]}"?' if guess else ""
        raise SimplydataError(f'The file has no variable called "{missing[0]}".{hint} Its variables are: '
                              + ", ".join(variables) + f".\nFor example:  {example}")
    if isinstance(values, str):
        return ds[values], values
    dims = {tuple(ds[v].dims) for v in wanted}
    if len(dims) != 1:
        raise SimplydataError("The variables in values= need the same directions to be stacked: "
                              + "; ".join(f"{v}: {', '.join(ds[v].dims)}" for v in wanted) + ".")
    stacked = ds[list(wanted)].to_dataarray(dim="variable")
    stacked.attrs["simplydata_variables"] = {v: dict(ds[v].attrs) for v in wanted}
    return stacked, "+".join(wanted)


def read_block(source, values=None, keep_on_disk=False, empty_values=None, directions_named=None):
    """sdata.number_block("file.nc", values=...): a NumberBlock (or a FileBlock with keep_on_disk=True)."""
    from .blocks import NumberBlock, _from_xarray
    from ._directions import check_names

    step = "sdata.number_block()"
    if not isinstance(keep_on_disk, bool):
        raise SimplydataError("keep_on_disk= needs True or False (no quotes).")
    text = os.fspath(source)
    if not text.lower().endswith(NETCDF_ENDINGS) and not any(ch in text for ch in "*?["):
        local_path(text, step)
        raise SimplydataError(f'sdata.number_block() reads netCDF files (.nc). "{Path(text).name}" is another kind: '
                              'for a table use sdata.table(...), for one list of numbers sdata.numbers(...).')
    files = _files(source, step)
    if keep_on_disk and len(files) > 1:
        raise SimplydataError(f"keep_on_disk=True keeps one file on disk; {len(files)} files match. Read them without "
                              "keep_on_disk=, or one file at a time.")
    datasets, engines = [], set()
    try:
        for path in files:
            ds, engine = _open(path, step)
            datasets.append(ds)
            engines.add(engine)
        if len(datasets) > 1:
            ds = _join(datasets, files, values, step)
            how = f"{len(files)} files joined by their labels (xarray combine_by_coords, join=\"exact\")"
        else:
            ds = datasets[0]
            how = "xarray open_dataset"
        da, name = _pick_values(ds, values, text, step)
        variables = da.attrs.pop("simplydata_variables", None)
        markers = _markers(empty_values) if empty_values is not None else None
        if markers is not None and not keep_on_disk:
            hits = int(da.isin(markers).sum())
            da = da.where(~da.isin(markers))
            print(f"{hits} value{'' if hits == 1 else 's'} equal to {', '.join(f'{m:g}' for m in markers)} "
                  f"{'is' if hits == 1 else 'are'} now empty (xarray where).")
        attrs = dict(da.attrs)
        about = {"name": name, "attrs": attrs, "variables": variables}
        engine_words = " and ".join(sorted(engines))
        if keep_on_disk:
            from .blocks import FileBlock

            names = [str(d) for d in da.dims]
            labels = {n: np.asarray(da.coords[n].values) for n in names if n in da.coords and da.coords[n].ndim == 1}
            if directions_named is not None:
                new = check_names(directions_named, len(names), "number_block", 'sdata.number_block("sst.nc", '
                                  'values="sst", directions_named=["time", "latitude", "longitude"])')
                da = da.rename(dict(zip(names, new)))
                labels = {new[names.index(o)]: lab for o, lab in labels.items()}
                names = new
            print(describe(name, np.broadcast_to(0, da.shape), names, labels, attrs)
                  + f". The numbers stay in the file until a word needs them. {how} ({engine_words} engine), "
                  "not loaded"
                  + (f". Values equal to {', '.join(f'{m:g}' for m in markers)} become empty when the numbers are read"
                     if markers is not None else ""))
            return FileBlock(da, names, labels, about, files[0], datasets[0], markers)
        da = da.load()
    finally:
        if not keep_on_disk:
            for d in datasets:
                d.close()
    arr, names, labels = _from_xarray(da)
    if directions_named is not None:
        new = check_names(directions_named, arr.ndim, "number_block", 'sdata.number_block("sst.nc", values="sst", '
                          'directions_named=["time", "latitude", "longitude"])')
        labels = {new[names.index(o)]: lab for o, lab in labels.items()}
        names = new
    print(describe(name, arr, names, labels, attrs) + f". {how} ({engine_words} engine)")
    block = NumberBlock(arr, names, [True] * len(names), labels)
    object.__setattr__(block, "_about", about)
    return block


def _join(datasets, files, values, step):
    """Several files as one Dataset: xarray combine_by_coords with join="exact", so labels that differ between files
    are refused instead of filled with empty values; and units that differ are refused, not hidden."""
    xr = need_xarray(step)
    wanted = [values] if isinstance(values, str) else list(values or [])
    for var in wanted:
        units = {}
        for path, ds in zip(files, datasets):
            if var in ds.data_vars:
                units.setdefault(str(ds[var].attrs.get("units")), path.name)
        if len(units) > 1:
            said = "; ".join(f"{u} in {f}" for u, f in units.items())
            raise SimplydataError(f'The files give "{var}" in different units ({said}), so joining them would mix them '
                                  "up. Change the numbers of one file to the other's units first, and read the files "
                                  "one at a time.")
    try:
        return xr.combine_by_coords(datasets, combine_attrs="override", join="exact", data_vars="all")
    except ValueError:
        differ = []
        dims = sorted({str(d) for ds in datasets for d in ds.dims})
        for dim in dims:
            labels = [np.asarray(ds[dim].values) for ds in datasets if dim in ds.coords]
            if len(labels) < 2:
                continue
            same = all(lab.shape == labels[0].shape and (lab == labels[0]).all() for lab in labels)
            apart = all(np.intersect1d(a, b).size == 0 for i, a in enumerate(labels) for b in labels[i + 1:])
            if not same and not apart:
                differ.append(dim)
            elif not same and apart and len({lab.size for lab in labels}) > 0:
                continue
        if not differ:
            differ = [d for d in dims if any(d in ds.dims for ds in datasets)]
        raise SimplydataError(f"The files cannot be joined: the labels of {', '.join(differ)} differ from file to file, "
                              "so some places would be empty. Files are joined only when every other direction has the "
                              "same labels. Read the files one at a time and keep the same labels in each "
                              "(block.keep_where).") from None


def _markers(empty_values) -> list:
    from ._base import is_number

    if is_number(empty_values):
        empty_values = [empty_values]
    if not isinstance(empty_values, (list, tuple, set)) or not empty_values or not all(is_number(v) for v in
                                                                                        empty_values):
        raise SimplydataError("empty_values= is a list of the numbers that mean \"no value\" in your file, such as "
                              "empty_values=[-999].")
    return [float(v) for v in empty_values]


# ---------------------------------------------------------------------- saving a block
def save_block(block, file_name) -> None:
    """block.save("out.nc"): xarray to_netcdf, h5netcdf engine, every variable compressed (zlib level 4)."""
    step = "block.save()"
    path = local_path(file_name, step)
    xr = need_xarray(step, engine=True)
    about = getattr(block, "_about", None) or {}
    name = about.get("name") or "values"
    values = block._values  # a block kept on disk is read now, and its file closed
    coords = {n: np.asarray(lab) for n, lab in block._labels.items() if n in block._names}
    variables = about.get("variables")
    if variables and "variable" in block._names and "variable" in block._labels:
        da = xr.DataArray(values, dims=list(block._names), coords=coords)
        ds = da.to_dataset(dim="variable")
        for var in ds.data_vars:
            ds[var].attrs.update(variables.get(str(var), {}))
        names_said = ", ".join(str(v) for v in ds.data_vars)
    else:
        if "+" in name:
            name = "values"
        ds = xr.DataArray(values, dims=list(block._names), coords=coords, name=name,
                          attrs=dict(about.get("attrs") or {})).to_dataset()
        names_said = name
    encoding = {str(var): {"zlib": True, "complevel": 4} for var in ds.data_vars}
    try:
        ds.to_netcdf(path, engine="h5netcdf", encoding=encoding)
    except OSError:
        raise SimplydataError(f'"{Path(file_name).name}" cannot be written: it is open, perhaps in another block read '
                              "with keep_on_disk=True. Save under another name, or read that block's numbers first "
                              "(any word that needs them closes the file).") from None
    print(f"Saved {say_shape(values.shape, block._names)} as \"{names_said}\" to {Path(file_name).name} (netCDF-4, "
          f"compressed). xarray to_netcdf(engine=\"h5netcdf\")")


# ---------------------------------------------------------------------- sdata.show_whats_inside
def show_whats_inside(file_name=None) -> None:
    """Show what a file holds without loading its numbers: its variables, directions, sizes and units.

    sdata.show_whats_inside("sst_monthly.nc")
    netCDF files (.nc): each variable with its directions, sizes, units and description, the labels' first and last
    values, then the file's own notes (xarray open_dataset reads only these). .npz and .npy: each array's name, shape
    and number type (NumPy reads the headers). .xlsx: each sheet with its rows and columns (openpyxl, read only).
    Nothing is written and nothing goes over the network.
    """
    step = "sdata.show_whats_inside()"
    if file_name is None:
        raise SimplydataError('sdata.show_whats_inside() needs a file name.\nFor example:  '
                              'sdata.show_whats_inside("sst_monthly.nc")')
    path = _existing(local_path(file_name, step), step)
    ending = path.suffix.lower()
    if ending in NETCDF_ENDINGS:
        _inside_netcdf(path, step)
    elif ending == ".npz":
        _inside_npz(path)
    elif ending == ".npy":
        _inside_npy(path)
    elif ending in (".xlsx", ".xlsm"):
        _inside_excel(path)
    else:
        raise SimplydataError(f'sdata.show_whats_inside() looks inside .nc, .npz, .npy and .xlsx files; "{path.name}" '
                              "is another kind. For a table file, sdata.table(...) reads it and table.show() shows "
                              "it.")
    return None


def _inside_netcdf(path: Path, step: str) -> None:
    ds, engine = _open(path, step)
    try:
        lines = [f"{path.name}: netCDF ({'netCDF-4' if engine == 'h5netcdf' else 'classic netCDF-3'}), "
                 f"{len(ds.data_vars)} variable{'' if len(ds.data_vars) == 1 else 's'}"]
        for name, var in ds.data_vars.items():
            labels = {str(d): np.asarray(ds.coords[d].values) for d in var.dims if d in ds.coords}
            lines.append("  " + describe(str(name), np.broadcast_to(0, var.shape), [str(d) for d in var.dims],
                                         labels, var.attrs) + f" ({var.dtype})")
            about = var.attrs.get("long_name") or var.attrs.get("standard_name") or var.attrs.get("description")
            if about:
                lines.append(f"      {about}")
        if ds.attrs:
            lines.append("Notes in the file:")
            for key, value in ds.attrs.items():
                text = str(value).replace("\n", " ")
                lines.append(f"  {key}: {text[:200]}{'...' if len(text) > 200 else ''}")
        lines.append(f'Read with xarray open_dataset ({engine} engine): only the names, sizes, units and labels; '
                     f'sdata.number_block("{path.name}", values="...") reads the numbers.')
    finally:
        ds.close()
    print("\n".join(lines))


def _inside_npz(path: Path) -> None:
    import zipfile

    lines = []
    with zipfile.ZipFile(path) as archive:
        for member in archive.namelist():
            if not member.endswith(".npy"):
                continue
            with archive.open(member) as handle:
                version = np.lib.format.read_magic(handle)
                shape, fortran, dtype = (np.lib.format.read_array_header_1_0(handle) if version == (1, 0)
                                         else np.lib.format.read_array_header_2_0(handle))
            lines.append(f"  {member[:-4]}: shape {tuple(int(n) for n in shape)} ({dtype})")
    print(f"{path.name}: {len(lines)} NumPy array{'' if len(lines) == 1 else 's'} (.npz)")
    print("\n".join(lines))
    print("Read with NumPy's header readers (np.lib.format); the numbers were not loaded.")


def _inside_npy(path: Path) -> None:
    with open(path, "rb") as handle:
        version = np.lib.format.read_magic(handle)
        shape, fortran, dtype = (np.lib.format.read_array_header_1_0(handle) if version == (1, 0)
                                 else np.lib.format.read_array_header_2_0(handle))
    print(f"{path.name}: one NumPy array, shape {tuple(int(n) for n in shape)} ({dtype}).")
    print("Read with NumPy's header reader (np.lib.format); the numbers were not loaded.")


def _inside_excel(path: Path) -> None:
    from openpyxl import load_workbook

    book = load_workbook(path, read_only=True, data_only=True)
    try:
        lines = [f"{path.name}: {len(book.sheetnames)} sheet{'' if len(book.sheetnames) == 1 else 's'}"]
        for sheet in book.worksheets:
            rows, columns = sheet.max_row, sheet.max_column
            lines.append(f'  "{sheet.title}": {rows} rows x {columns} columns'
                         if rows is not None and columns is not None else f'  "{sheet.title}"')
        lines.append("Read with openpyxl (read only); sdata.table(\"file.xlsx\", sheet=\"...\") reads a sheet.")
    finally:
        book.close()
    print("\n".join(lines))
