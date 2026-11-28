"""Circle charts are drawn by the R package circlize (Gu et al. 2014): this is the one place that opens R's picture
device for them (decision Z1, approved by Manish 2026-11-27).

simplydata's privacy rule says the R code it runs never writes a file, and simplydata._r.r_call() refuses R code that
opens a picture file (png(), svg(), pdf("x.pdf") ...). circlize can only draw onto an R picture device, so this
module holds one controlled exception, open_device(): it opens the device from Python (not from an R code string),
and only on
  * the exact file the user named in circle_chart.save("x.svg"),
  * a picture in a private temporary folder for circle_chart.show(), which is deleted afterwards, or
  * no file at all (R's null pdf device), to read back what circlize drew (circle_chart.get_numbers_drawn()).
The R code that draws stays under r_call()'s check. circlize::circos.clear() runs before and after every picture,
in R (on.exit) and again from Python (finally), and the device is always closed, so no setting leaks from one
picture to the next, even after an error. tests/test_circle_charts.py checks that open_device() is the only place
in simplydata that opens an R picture device, and that save("x.svg") leaves exactly x.svg in the folder.

Nothing is downloaded: circlize reaches the internet only when it is given species= (UCSC genome files), and
simplydata never passes it (decision Z2; a test bans "species" in the R code of circle charts).
"""

from __future__ import annotations

import contextlib
import os
import shutil
import tempfile

from ._errors import SimplydataError

# The R packages a circle chart needs; R's own install line first, then conda (decision Z12)
PACKAGES = ("circlize",)
WHAT = "Circle charts"
CONDA = "with conda: conda install -c conda-forge r-circlize"
FORMATS = ("png", "svg", "pdf")

# The R code that wraps every circle chart program: circos.clear() first, and again when the code ends (on.exit),
# also after an error. The program's last value (what circlize drew, read back) is the answer.
WRAP = ("local({{\n"
        "  circlize::circos.clear()\n"
        "  on.exit(circlize::circos.clear(), add = TRUE)\n"
        "{body}\n"
        "}})")


def need_circlize() -> None:
    """Stop with the install steps unless R, rpy2 and circlize are ready."""
    from ._r import need_r

    need_r(PACKAGES, WHAT, python_note=CONDA)


def _cairo(ro) -> bool:
    """Whether R can draw with cairo here (PNG and SVG without a screen)."""
    return bool(ro.r("isTRUE(capabilities('cairo'))")[0])


def open_device(ro, kind, path, width, height, resolution):
    """Open R's picture device and give back its number. The only place simplydata opens one (Z1).

    kind "png", "svg" or "pdf" draws into path (the file the user named, or a file in a private temporary folder);
    kind None draws into nothing (R's null pdf device), for reading back what circlize drew."""
    if kind is None:
        ro.r["pdf"](file=ro.NULL, width=width, height=height)
    elif kind == "pdf":
        ro.r["pdf"](file=str(path), width=width, height=height, useDingbats=False)
    elif kind == "svg":
        if not _cairo(ro):
            raise SimplydataError("R on this computer cannot draw .svg pictures (it was built without cairo). "
                                  "Save the circle chart as .pdf or .png instead.")
        ro.r["svg"](filename=str(path), width=width, height=height)
    elif kind == "png":
        extra = {"type": "cairo"} if _cairo(ro) else {}
        ro.r["png"](filename=str(path), width=width, height=height, units="in", res=resolution, **extra)
    else:  # pragma: no cover - the words check the kind first
        raise SimplydataError(f"A circle chart is saved as .png, .svg or .pdf, not .{kind}.")
    return int(ro.r["dev.cur"]()[0])


def _close_device(ro, number) -> None:
    """Close the device this module opened (and only that one), and clear circlize's settings."""
    with contextlib.suppress(Exception):
        if number in [int(n) for n in (ro.r("as.integer(grDevices::dev.list())") or [])]:
            ro.r["dev.off"](which=number)
    with contextlib.suppress(Exception):
        ro.r("invisible(circlize::circos.clear())")


def run(body, values, kind=None, path=None, width=7.0, height=7.0, resolution=300):
    """Run one circle chart program (the R code body, with the data as the R variables in values) on a picture
    device, and give back what the program's last line gives (what circlize drew, read back)."""
    from . import _r

    code = WRAP.format(body=body)
    _r.refuse_unsafe_r_code(code)
    need_circlize()
    with _r._LOCK:
        ro = _r._STATE["r"]
        number = open_device(ro, kind, path, float(width), float(height), int(resolution))
        try:
            return _r.r_call(code, packages=PACKAGES, what=WHAT, source="circlize", **values)
        finally:
            _close_device(ro, number)


def draw_into_file(body, values, path, width, height, resolution):
    """circle_chart.save(): draw straight into the file the user named."""
    kind = os.path.splitext(str(path))[1].lower().lstrip(".")
    return run(body, values, kind=kind, path=path, width=width, height=height, resolution=resolution)


def draw_for_showing(body, values, width, height, resolution=100) -> bytes:
    """circle_chart.show(): draw a PNG into a private temporary folder, read it, and delete the folder."""
    folder = tempfile.mkdtemp(prefix="simplydata-circle-")
    try:
        path = os.path.join(folder, "circle_chart.png")
        run(body, values, kind="png", path=path, width=width, height=height, resolution=resolution)
        with open(path, "rb") as picture:
            return picture.read()
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def show_png(data: bytes) -> None:
    """Show a PNG: in a notebook as a picture, elsewhere in a matplotlib window (as chart.show() does)."""
    try:
        from IPython import get_ipython

        shell = get_ipython()
    except ImportError:
        shell = None
    if shell is not None and getattr(shell, "kernel", None) is not None:  # Jupyter, VS Code notebooks
        from IPython.display import Image, display

        display(Image(data=data))
        return
    import io

    import matplotlib.image as mpimg
    import matplotlib.pyplot as plt

    from ._core import _NO_WINDOW_BACKENDS

    if str(plt.get_backend()).lower() in _NO_WINDOW_BACKENDS:  # no screen (a script saving files, the tests)
        return
    pixels = mpimg.imread(io.BytesIO(data), format="png")
    height, width = pixels.shape[:2]
    figure = plt.figure(figsize=(width / 100, height / 100), dpi=100)
    axes = figure.add_axes((0, 0, 1, 1))
    axes.imshow(pixels)
    axes.set_axis_off()
    plt.show()
    if not plt.isinteractive():
        plt.close(figure)
