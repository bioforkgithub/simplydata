"""A smooth curve through points, as an object: sdata.curve_through_points (families for 100 %, batch 16; G6).

curve = sdata.curve_through_points(x=depths, y=oxygen) makes a spline: pieces of polynomials joined smoothly at the
points. The curve can then be read anywhere (curve.find_value_at(12)), and its slope, area, zeros, pieces and knots
found. It is SciPy's spline objects underneath (scipy.interpolate: BSpline, PPoly, BPoly), so every number can be
checked there, and curve.as_scipy() hands the SciPy object over.

How the curve is made (said in the sentence):

* by default a cubic spline through every point with natural ends (no bend at the first and last point): SciPy
  make_interp_spline(bc_type="natural"), the same curve as table.find_values_at(joined_by="smooth curve") and R
  splinefun(method = "natural"). degree= 1 to 5 and ends= ("natural", "not-a-knot", "periodic", "clamped") choose
  another spline through the points (as splrep(s=0), InterpolatedUnivariateSpline);
* smoothness= a number (or "auto") passes near the points instead: the smoothing spline of R smooth.spline(), the same
  as find_values_at(smoothness=) (SciPy make_smoothing_spline, lambda on x rescaled to 0 to 1, as R);
* allowed_error= a number: the fewest knots for which the sum of squared distances to the points is at most that
  number (FITPACK's s: SciPy make_splrep with generate_knots, as splrep(s=) and UnivariateSpline);
* knots= a list of inner knots: least squares with those knots (SciPy make_lsq_spline, as LSQUnivariateSpline and R
  lm(y ~ splines::bs(x, knots = ...)));
* slopes= the slope at each point: the cubic curve with those slopes (SciPy CubicHermiteSpline);
* in_order=True: a path through the points in their order (x and y both follow a fraction from 0 to 1 along it;
  SciPy make_splprep, as splprep);
* z= heights: a surface over x and y (SciPy RectBivariateSpline on a full grid, SmoothBivariateSpline for scattered
  points, LSQBivariateSpline with knots=; as bisplrep and bisplev), on_sphere=True with x the latitude and y the
  longitude in degrees (RectSphereBivariateSpline, SmoothSphereBivariateSpline, LSQSphereBivariateSpline).

Places outside the points are empty (a spline carried on beyond its points is guesswork). Approved by Manish
2026-11-28 (plan section 2.6, G6: "spline" is an other name).
"""

from __future__ import annotations

import math

import numpy as np

from ._errors import SimplydataError, choice_error, friendly

WORDS = ("find_value_at", "find_slope_at", "find_area_between", "find_zeros", "turn_into_slope_curve",
         "turn_into_area_curve", "show_pieces", "show_knots", "as_scipy")
# names from SciPy and R -> the curve word (they never run)
HINTS = {"splev": "find_value_at(...)", "ev": "find_value_at(...)", "predict": "find_value_at(...)",
         "derivative": "turn_into_slope_curve() or find_slope_at(...)", "splder": "turn_into_slope_curve()",
         "antiderivative": "turn_into_area_curve()", "splantider": "turn_into_area_curve()",
         "integrate": "find_area_between(low, high)", "integral": "find_area_between(low, high)",
         "splint": "find_area_between(low, high)", "roots": "find_zeros()", "sproot": "find_zeros()",
         "solve": "find_zeros(where_value_is=...)", "spalde": 'find_slope_at(x, order="all")',
         "get_knots": "show_knots()", "get_coeffs": "show_knots()", "tck": "show_knots()", "t": "show_knots()",
         "c": "show_knots()", "from_spline": "show_pieces()", "from_power_basis": 'show_pieces(basis="bernstein")'}
ENDS = {"natural": "natural", "not-a-knot": "not-a-knot", "not a knot": "not-a-knot", "periodic": "periodic",
        "clamped": "clamped"}
PIECE_BASES = ("powers", "bernstein")
MIN_SMOOTHING_POINTS = 5


def _show(x) -> str:
    x = float(x)
    if math.isnan(x):
        return "empty"
    return "0" if abs(x) < 1e-300 else f"{x:.6g}"


def _numbers(values, name: str, example: str):
    """A 1-D float array from a list, simplydata numbers or a NumPy array."""
    if values is None:
        return None
    if hasattr(values, "as_numpy"):
        values = values.as_numpy()
    try:
        out = np.asarray(values, dtype=float).ravel()
    except (TypeError, ValueError):
        raise SimplydataError(f"{name}= needs numbers (a list, or sdata.number_list).\n"
                              f"For example:  {example}") from None
    if out.size == 0:
        raise SimplydataError(f"{name}= is empty.\nFor example:  {example}")
    if not np.all(np.isfinite(out)):
        raise SimplydataError(f"{name}= has an empty or infinite value; every point needs a number.")
    return out


def _result_numbers(values):
    from .numbers.numbers import number_list

    return number_list(list(np.asarray(values, dtype=float).ravel()))


def _table(data: dict):
    import pandas as pd

    from .table import Table

    return Table(pd.DataFrame(data))


class Curve:
    """A smooth curve (a spline) through or near points. Make one with sdata.curve_through_points(x=..., y=...).

    Words: find_value_at, find_slope_at, find_area_between, find_zeros, turn_into_slope_curve, turn_into_area_curve,
    show_pieces, show_knots, as_scipy.
    """

    _OLD_WORDS: dict = {}  # no old names (sdata.help reads this, as for tables and charts)

    def __init__(self, spline, shape, said, low=None, high=None, extra=None):
        self._spline = spline  # the SciPy object
        self._shape = shape  # "curve", "path" or "surface"
        self._said = said
        self._low, self._high = low, high
        self._extra = extra or {}

    def __repr__(self):
        return self._said

    @classmethod
    def _word_names(cls) -> list[str]:
        return list(WORDS)

    def __dir__(self):
        return list(WORDS)

    def __getattr__(self, name):
        from ._errors import MissingWordError, suggest

        if name.startswith("_"):
            raise AttributeError(name)
        lines = [f"A curve has no word called .{name}()."]
        if name in HINTS:
            lines.append(f"In simplydata this is curve.{HINTS[name]}.")
        else:
            guesses = suggest(name, list(WORDS))
            if guesses:
                lines.append("Did you mean " + " or ".join(f".{g}()" for g in guesses) + "?")
        lines.append("Every word for a curve: " + ", ".join(WORDS))
        raise MissingWordError("\n".join(lines))

    # ------------------------------------------------------------------ helpers
    def _need(self, word, *shapes):
        if self._shape not in shapes:
            kinds = {"curve": "a curve of y over x", "path": "a path (in_order=True)", "surface": "a surface (z=)"}
            raise SimplydataError(f"curve.{word}() works on {' or '.join(kinds[s] for s in shapes)}; this is "
                                  f"{kinds[self._shape]}.")

    def _places(self, at, word, name="at"):
        places = _numbers(at, name, f"curve.{word}(12)")
        if places is None:
            raise SimplydataError(f"curve.{word}() needs a place (a number or a list), such as curve.{word}(12).")
        return places

    def _outside_note(self, places):
        out = int(np.count_nonzero((places < self._low) | (places > self._high)))
        if out:
            print(f"Note: {out} place{'s are' if out > 1 else ' is'} outside the points ({_show(self._low)} to "
                  f"{_show(self._high)}), so {'they are' if out > 1 else 'it is'} empty: a curve carried on beyond "
                  "its points is guesswork.")

    def _one_or_many(self, at, values):
        values = np.asarray(values, dtype=float)
        if np.ndim(at) == 0 and not hasattr(at, "as_numpy"):
            return float(values.ravel()[0])
        return _result_numbers(values)

    def _surface_places(self, word, x, y):
        xs = self._places(x, word, "x")
        ys = self._places(y, word, "y")
        if xs.size != ys.size:
            if xs.size == 1:
                xs = np.full(ys.size, xs[0])
            elif ys.size == 1:
                ys = np.full(xs.size, ys[0])
            else:
                raise SimplydataError(f"curve.{word}() needs as many x as y (they are read as pairs); there are "
                                      f"{xs.size} and {ys.size}.")
        if self._extra.get("sphere"):
            return np.radians(90.0 - xs), np.radians(np.mod(ys, 360.0)), xs, ys
        return xs, ys, xs, ys

    # ------------------------------------------------------------------ words
    @friendly(others={"x": "at", "u": "at"})
    def find_value_at(self, at=None, y=None):
        """The curve's value at a place, or at a list of places. curve.find_value_at(12)

        For a curve of y over x: the y at x = at (a number gives a number, a list gives numbers); SciPy BSpline (or
        PPoly) called at the places, as splev and R predict(splinefun(...)). For a path (in_order=True): at is the
        fraction along the path (0 at the first point, 1 at the last), and the answer is a table of x and y. For a
        surface (z=): curve.find_value_at(x, y) gives the height at each pair (SciPy ev, as bisplev). Places outside
        the points are empty.
        """
        if self._shape == "surface":
            if y is None:
                raise SimplydataError("A surface needs two places: curve.find_value_at(x, y).")
            u, v, xs, ys = self._surface_places("find_value_at", at, y)
            values = self._spline.ev(u, v)
            name = getattr(self._spline, "scipy_name", type(self._spline).__name__)
            print(f"The surface at {xs.size} place{'s' if xs.size != 1 else ''} (SciPy {name}.ev).")
            return self._one_or_many(at if np.ndim(at) else y, values)
        if y is not None:
            raise SimplydataError("y= is for a surface (z=); a curve is read at one place: curve.find_value_at(12).")
        places = self._places(at, "find_value_at")
        if self._shape == "path":
            if np.any((places < 0) | (places > 1)):
                raise SimplydataError("On a path, find_value_at() takes the fraction along it, from 0 (the first "
                                      "point) to 1 (the last).")
            found = np.asarray(self._spline(places), dtype=float).reshape(2, -1).T  # SciPy gives (x and y, places)
            print(f"The path at {places.size} fraction{'s' if places.size != 1 else ''} along it (SciPy BSpline of "
                  "make_splprep, as splev).")
            return _table({"fraction": places, self._extra["x"]: found[:, 0], self._extra["y"]: found[:, 1]})
        values = np.asarray(self._spline(places), dtype=float)
        values = np.where((places < self._low) | (places > self._high), np.nan, values)
        self._outside_note(places)
        if places.size == 1:
            print(f"The curve at {self._extra['x']} = {_show(places[0])}: {self._extra['y']} = {_show(values[0])}.")
        else:
            print(f"The curve at {places.size} places of {self._extra['x']} ({type(self._spline).__name__} of SciPy, "
                  "as splev).")
        return self._one_or_many(at, values)

    @friendly(others={"nu": "order", "der": "order", "dx": "order"})
    def find_slope_at(self, at=None, y=None, order=1, along="x"):
        """The slope of the curve at a place (order=2: the slope of the slope). curve.find_slope_at(12)

        order=1 is the slope (dy/dx), 2 the bend, up to the degree of the curve; order="all" at one place gives a
        table of the value and every slope there (SciPy spalde). SciPy BSpline.derivative, as splev(der=) and R
        splinefun(...)(x, deriv = 1). A path gives dx and dy along the fraction; a surface (curve.find_slope_at(x, y,
        along="y")) the slope along x or y (SciPy ev(dx=, dy=)).
        """
        degree = self._extra.get("degree", 3)
        if order == "all":
            self._need("find_slope_at", "curve")
            places = self._places(at, "find_slope_at")
            if places.size != 1:
                raise SimplydataError('order="all" gives every slope at one place; give one number for at=.')
            values = [float(self._spline.derivative(k)(places[0])) if k else float(self._spline(places[0]))
                      for k in range(degree + 1)]
            print(f"The value and every slope of the curve at {self._extra['x']} = {_show(places[0])} (as SciPy "
                  "spalde).")
            return _table({"order": list(range(degree + 1)), "value": values})
        if isinstance(order, bool) or not isinstance(order, (int, np.integer)) or not 1 <= order <= degree:
            raise SimplydataError(f'order= is a whole number from 1 to {degree} (the degree of the curve), or "all".')
        order = int(order)
        if self._shape == "surface":
            if y is None:
                raise SimplydataError('A surface needs two places: curve.find_slope_at(x, y, along="x").')
            if along not in ("x", "y"):
                raise choice_error("find_slope_at", "along", along, ["x", "y"])
            if self._extra.get("sphere"):
                raise SimplydataError("Slopes of a surface on a sphere are not given; curve.as_scipy() has them in "
                                      "radians.")
            u, v, xs, _ys = self._surface_places("find_slope_at", at, y)
            values = self._spline.ev(u, v, dx=order if along == "x" else 0, dy=order if along == "y" else 0)
            print(f"The slope of the surface along {along} (order {order}) at {xs.size} place"
                  f"{'s' if xs.size != 1 else ''} (SciPy ev(dx=, dy=)).")
            return self._one_or_many(at if np.ndim(at) else y, values)
        places = self._places(at, "find_slope_at")
        if self._shape == "path":
            found = np.asarray(self._spline.derivative(order)(places), dtype=float).reshape(2, -1).T
            print(f"The slope of the path along the fraction (order {order}): dx and dy at {places.size} place"
                  f"{'s' if places.size != 1 else ''}.")
            return _table({"fraction": places, f"d{self._extra['x']}": found[:, 0],
                           f"d{self._extra['y']}": found[:, 1]})
        values = np.asarray(self._spline.derivative(order)(places), dtype=float)
        values = np.where((places < self._low) | (places > self._high), np.nan, values)
        self._outside_note(places)
        what = "slope" if order == 1 else f"slope of order {order}"
        if places.size == 1:
            print(f"The {what} of the curve at {self._extra['x']} = {_show(places[0])}: {_show(values[0])} (SciPy "
                  f"{type(self._spline).__name__}.derivative).")
        else:
            print(f"The {what} of the curve at {places.size} places (SciPy {type(self._spline).__name__}.derivative).")
        return self._one_or_many(at, values)

    @friendly(others={"a": "low", "b": "high"})
    def find_area_between(self, low=None, high=None, y_between=None):
        """The area under the curve from low to high (the integral). curve.find_area_between(0, 20)

        SciPy BSpline.integrate (as splint and R integrate(splinefun(...), low, high)); the area below 0 counts as
        minus. For a surface, y_between=[low, high] gives the volume over that rectangle (SciPy integral).
        """
        for v, n in ((low, "low"), (high, "high")):
            if isinstance(v, bool) or not isinstance(v, (int, float, np.integer, np.floating)) or not math.isfinite(v):
                raise SimplydataError(f"find_area_between() needs two numbers, low and high; {n} is {v!r}.\n"
                                      "For example:  curve.find_area_between(0, 20)")
        if self._shape == "surface":
            if not (isinstance(y_between, (list, tuple)) and len(y_between) == 2):
                raise SimplydataError("A surface needs a range of y too: curve.find_area_between(0, 1, "
                                      "y_between=[0, 2]).")
            if not hasattr(self._spline, "integral") or self._extra.get("sphere"):
                raise SimplydataError("The volume under a surface on a sphere is not given; curve.as_scipy() hands the "
                                      "spline over.")
            value = float(self._spline.integral(float(low), float(high), float(y_between[0]), float(y_between[1])))
            print(f"The volume under the surface for x from {_show(low)} to {_show(high)} and y from "
                  f"{_show(y_between[0])} to {_show(y_between[1])}: {_show(value)} (SciPy integral).")
            return value
        self._need("find_area_between", "curve")
        if y_between is not None:
            raise SimplydataError("y_between= is for a surface (z=).")
        room = 1e-12 * max(1.0, abs(self._low), abs(self._high))
        if not (self._low - room <= low and high <= self._high + room):
            raise SimplydataError(f"find_area_between() works inside the points ({_show(self._low)} to "
                                  f"{_show(self._high)}); a curve carried on beyond them is guesswork.")
        value = float(self._spline.integrate(float(low), float(high)))
        print(f"The area under the curve for {self._extra['x']} from {_show(low)} to {_show(high)}: {_show(value)} "
              f"(SciPy {type(self._spline).__name__}.integrate, exact for the spline).")
        return value

    @friendly(others={"value": "where_value_is", "y": "where_value_is"})
    def find_zeros(self, where_value_is=0):
        """Where the curve is 0 (or where_value_is=). zeros = curve.find_zeros()

        Every place inside the points where the curve crosses or touches the value, from the pieces of the spline
        (SciPy PPoly.solve, as sproot for cubic splines). Gives back numbers (none if it never gets there).
        """
        self._need("find_zeros", "curve")
        from scipy import interpolate

        if isinstance(where_value_is, bool) or not isinstance(where_value_is, (int, float, np.integer, np.floating)):
            raise SimplydataError("where_value_is= needs a number, such as where_value_is=5.")
        pieces = (self._spline if isinstance(self._spline, interpolate.PPoly) else
                  interpolate.PPoly.from_spline(self._spline, extrapolate=False))
        found = np.asarray(pieces.solve(float(where_value_is), extrapolate=False), dtype=float)
        found = found[np.isfinite(found)]
        found = np.unique(np.round(found, 12)) if found.size else found
        target = "0" if where_value_is == 0 else _show(where_value_is)
        if found.size:
            print(f"The curve is {target} at {self._extra['x']} = {', '.join(_show(v) for v in found[:10])}"
                  f"{' ...' if found.size > 10 else ''} (SciPy PPoly.solve on the pieces).")
        else:
            print(f"The curve never reaches {target} between {_show(self._low)} and {_show(self._high)}.")
        return _result_numbers(found)

    @friendly(others={"nu": "order"})
    def turn_into_slope_curve(self, order=1):
        """A new curve: the slope of this one (order=2, the slope of the slope). slopes = curve.turn_into_slope_curve()

        SciPy BSpline.derivative (as splder and R splinefun(..., deriv = 1)); its degree is one less for each order.
        """
        self._need("turn_into_slope_curve", "curve")
        degree = self._extra.get("degree", 3)
        if isinstance(order, bool) or not isinstance(order, (int, np.integer)) or not 1 <= order <= degree:
            raise SimplydataError(f"order= is a whole number from 1 to {degree} (the degree of the curve).")
        made = self._spline.derivative(int(order))
        extra = dict(self._extra, degree=degree - int(order), y=f"slope of {self._extra['y']}")
        said = (f"The slope{'' if order == 1 else ' of order ' + str(order)} of the curve: a spline of degree "
                f"{degree - int(order)} (SciPy {type(made).__name__}.derivative, as splder).")
        print(said)
        return Curve(made, "curve", said, self._low, self._high, extra)

    @friendly
    def turn_into_area_curve(self):
        """A new curve: the area under this one from the first point. areas = curve.turn_into_area_curve()

        Its value at x is the area from the first point to x (0 at the first point). SciPy BSpline.antiderivative,
        as splantider; its degree is one more.
        """
        self._need("turn_into_area_curve", "curve")
        degree = self._extra.get("degree", 3)
        made = self._spline.antiderivative()
        start = float(made(self._low))
        if start != 0.0 and hasattr(made, "c"):  # the area starts at 0 at the first point
            from scipy import interpolate

            if isinstance(made, interpolate.BSpline):
                made = interpolate.BSpline(made.t, made.c - start, made.k, extrapolate=made.extrapolate)
            else:
                made = interpolate.PPoly(made.c.copy(), made.x, extrapolate=made.extrapolate)
                made.c[-1] -= start
        extra = dict(self._extra, degree=degree + 1, y=f"area under {self._extra['y']}")
        said = (f"The area under the curve from {self._extra['x']} = {_show(self._low)}: a spline of degree "
                f"{degree + 1} (SciPy {type(made).__name__}.antiderivative, as splantider).")
        print(said)
        return Curve(made, "curve", said, self._low, self._high, extra)

    @friendly
    def show_pieces(self, basis="powers"):
        """The polynomial pieces of the curve, one row per piece. pieces = curve.show_pieces()

        basis="powers": each piece as a + b*(x - from) + c*(x - from)**2 ... (SciPy PPoly.from_spline);
        "bernstein": in the Bernstein basis on the piece (SciPy BPoly.from_power_basis), the control values of a
        Bezier curve. Gives back a table: from, to and the numbers of each piece.
        """
        self._need("show_pieces", "curve")
        from scipy import interpolate

        if basis not in PIECE_BASES:
            raise choice_error("show_pieces", "basis", basis, list(PIECE_BASES))
        pieces = (self._spline if isinstance(self._spline, interpolate.PPoly) else
                  interpolate.PPoly.from_spline(self._spline))
        edges = np.asarray(pieces.x, dtype=float)
        keep = np.diff(edges) > 0  # repeated knots at the ends make pieces of no width
        data = {"from": edges[:-1][keep], "to": edges[1:][keep]}
        if basis == "powers":
            k = pieces.c.shape[0] - 1
            for row in range(pieces.c.shape[0]):
                power = k - row
                name = "constant" if power == 0 else (f"(x - from)" if power == 1 else f"(x - from)**{power}")
                data[name] = pieces.c[row][keep]
            data = {"from": data["from"], "to": data["to"], **{n: data[n] for n in reversed(list(data)[2:])}}
            how = "PPoly.from_spline"
        else:
            bernstein = interpolate.BPoly.from_power_basis(pieces)
            for row in range(bernstein.c.shape[0]):
                data[f"control value {row}"] = bernstein.c[row][keep]
            how = "BPoly.from_power_basis"
        print(f"The curve has {int(keep.sum())} polynomial pieces (SciPy {how}).")
        return _table(data)

    @friendly
    def show_knots(self):
        """The knots of the spline and its numbers (coefficients). knots = curve.show_knots()

        A B-spline is fixed by its knots, its coefficients and its degree (SciPy BSpline t, c and k, as splrep's
        tck); for a surface, the knots along x and along y (get_knots). Gives back a table.
        """
        from scipy import interpolate

        spline = self._spline
        if self._shape == "surface":
            tx, ty = spline.get_knots()
            size = max(len(tx), len(ty))
            pad = lambda v: list(map(float, v)) + [math.nan] * (size - len(v))  # noqa: E731
            print(f"The surface has {len(tx)} knots along x and {len(ty)} along y (SciPy get_knots).")
            return _table({"knot along x": pad(tx), "knot along y": pad(ty)})
        if not isinstance(spline, interpolate.BSpline):
            print("This curve is made of pieces with given slopes (SciPy CubicHermiteSpline, a PPoly): its knots are "
                  "the points.")
            return _table({"knot": np.asarray(spline.x, dtype=float)})
        knots = np.asarray(spline.t, dtype=float)
        coefficients = np.asarray(spline.c, dtype=float)
        if coefficients.ndim == 1:
            column = list(coefficients) + [math.nan] * (knots.size - coefficients.size)
            data = {"knot": knots, "coefficient": column}
        else:
            data = {"knot": knots}
            for j, name in enumerate((self._extra.get("x", "x"), self._extra.get("y", "y"))):
                data[f"coefficient of {name}"] = list(coefficients[:, j]) + [math.nan] * (knots.size -
                                                                                      coefficients.shape[0])
        print(f"A spline of degree {spline.k} with {knots.size} knots and {coefficients.shape[0]} coefficients "
              "(SciPy BSpline t, c, k).")
        return _table(data)

    def as_scipy(self):
        """The SciPy object behind the curve, for SciPy's own words. spline = curve.as_scipy()

        A BSpline (or a PPoly for slopes=; a bivariate spline for a surface): scipy.interpolate works on it directly.
        """
        return getattr(self._spline, "spline", self._spline)


def _sorted_points(x, y, example, distinct=True):
    order = np.argsort(x, kind="stable")
    x, y = x[order], y[order]
    if distinct and np.any(np.diff(x) == 0):
        raise SimplydataError("Two points have the same x, so no curve passes through both. Average them first, or "
                              "give smoothness= (a curve that passes near the points).\nFor example:  " + example)
    return x, y, order


@friendly(others={"s": "allowed_error", "k": "degree", "t": "knots", "w": "weights", "dydx": "slopes",
                  "bc_type": "ends", "lam": "smoothness"})
def curve_through_points(x=None, y=None, z=None, smoothness=0, degree=3, ends="natural", knots=None,
                         allowed_error=None, slopes=None, weights=None, in_order=False, on_sphere=False):
    """A smooth curve (a spline) through points. curve = sdata.curve_through_points(x=[0, 5, 10], y=[8.1, 7.9, 6.2])

    curve = sdata.curve_through_points(x=depths, y=oxygen), then curve.find_value_at(12). x= and y= are lists of
    numbers (sdata.number_list, or table.get_column("depth")). By default a cubic spline through every point with
    natural ends (SciPy make_interp_spline, the same curve as find_values_at(joined_by="smooth curve") and R
    splinefun(method = "natural")); degree= (1 to 5) and ends= ("natural", "not-a-knot", "periodic", "clamped")
    choose another. smoothness= a number (or "auto") passes near the points (R smooth.spline(lambda =), SciPy
    make_smoothing_spline); allowed_error= gives the fewest knots that keep the sum of squared distances at most that
    (SciPy make_splrep, FITPACK s); knots=[...] fits by least squares with those inner knots (make_lsq_spline);
    slopes= gives the slope at each point (CubicHermiteSpline); weights= counts some points more. in_order=True
    makes a path through the points in their order (make_splprep). z= makes a surface over x and y
    (RectBivariateSpline or SmoothBivariateSpline); on_sphere=True reads x and y as latitude and longitude in
    degrees. Prints how the curve was made. Words on the curve: find_value_at, find_slope_at, find_area_between,
    find_zeros, turn_into_slope_curve, turn_into_area_curve, show_pieces, show_knots, as_scipy.
    """
    example = "curve = sdata.curve_through_points(x=[0, 5, 10, 20], y=[8.1, 7.9, 6.2, 5.0])"
    xs = _numbers(x, "x", example)
    ys = _numbers(y, "y", example)
    if xs is None or ys is None:
        raise SimplydataError(f"curve_through_points() needs x= and y=, the points the curve goes through.\n"
                              f"For example:  {example}")
    if xs.size != ys.size:
        raise SimplydataError(f"x= and y= need the same number of values (they are read as points); there are "
                              f"{xs.size} and {ys.size}.")
    if isinstance(degree, bool) or not isinstance(degree, (int, np.integer)) or not 1 <= degree <= 5:
        raise SimplydataError("degree= is a whole number from 1 (straight lines) to 5; 3 (cubic) is the usual one.")
    degree = int(degree)
    w = _numbers(weights, "weights", example)
    if w is not None and (w.size != xs.size or np.any(w <= 0)):
        raise SimplydataError("weights= needs one number above 0 for each point.")
    names = {"x": "x", "y": "y"}
    chosen = [n for n, v in (("smoothness=", smoothness not in (0, None)), ("knots=", knots is not None),
                             ("allowed_error=", allowed_error is not None), ("slopes=", slopes is not None)) if v]
    if len(chosen) > 1:
        raise SimplydataError(f"{' and '.join(chosen)} are different ways to make the curve; give one of them.")
    if allowed_error is not None and (isinstance(allowed_error, bool) or not isinstance(
            allowed_error, (int, float, np.integer, np.floating)) or not allowed_error >= 0):
        raise SimplydataError("allowed_error= is a number of 0 or more: the largest sum of squared distances from the "
                              "points (0 passes through every point).")
    if z is not None:
        return _surface(xs, ys, _numbers(z, "z", example), degree, knots, allowed_error, w, on_sphere, chosen)
    if on_sphere:
        raise SimplydataError("on_sphere=True is for a surface: give z= too (the value at each latitude x and "
                              "longitude y).")
    if in_order:
        return _path(xs, ys, degree, allowed_error, w, chosen)
    return _curve(xs, ys, smoothness, degree, ends, knots, allowed_error, slopes, w, names, example)


def _curve(xs, ys, smoothness, degree, ends, knots, allowed_error, slopes, w, names, example):
    from scipy import interpolate

    if smoothness not in (0, None):  # the smoothing spline of find_values_at (R smooth.spline)
        from .table.between import SmoothingSpline, smoothness_choice

        smoothness = smoothness_choice("curve_through_points", smoothness)
        if degree != 3:
            raise SimplydataError("smoothness= gives a cubic smoothing spline (as R smooth.spline), so it takes no "
                                  "degree=.")
        found = SmoothingSpline(xs, ys, smoothness)  # lambda (and R's choice for "auto"), with ties averaged
        from .table.between import unique_mean

        ux, uy, counts = unique_mean(xs, ys)
        weights = counts.astype(float) if w is None else None
        if w is not None:
            raise SimplydataError("weights= with smoothness= is not given; R smooth.spline weights the repeated x by "
                                  "how many there are.")
        unit = interpolate.make_smoothing_spline((ux - found.low) / found.size, uy, w=weights, lam=found.lam)
        spline = interpolate.BSpline(found.low + found.size * unit.t, unit.c, unit.k, extrapolate=False)
        how = (f"a smoothing spline that passes near the points (lambda {found.lam:.4g} on x rescaled to 0 to 1"
               f"{', chosen by R' if smoothness == 'auto' else ''}), SciPy make_smoothing_spline, as R "
               f"smooth.spline(x, y, all.knots = TRUE)")
        low, high = float(ux[0]), float(ux[-1])
    elif slopes is not None:
        dydx = _numbers(slopes, "slopes", example)
        if dydx.size != xs.size:
            raise SimplydataError("slopes= needs one slope for each point.")
        xs, ys, order = _sorted_points(xs, ys, example)
        if degree != 3:
            raise SimplydataError("slopes= gives a cubic curve (Hermite), so it takes no degree=.")
        spline = interpolate.CubicHermiteSpline(xs, ys, dydx[order], extrapolate=False)
        how = "a cubic curve through every point with the given slopes (SciPy CubicHermiteSpline)"
        low, high = float(xs[0]), float(xs[-1])
    elif knots is not None:
        inner = _numbers(knots, "knots", example)
        xs, ys, order = _sorted_points(xs, ys, example, distinct=False)
        if np.any((inner <= xs[0]) | (inner >= xs[-1])):
            raise SimplydataError(f"knots= are inner knots: each must lie between the first and last x "
                                  f"({_show(xs[0])} and {_show(xs[-1])}).")
        t = np.concatenate([[xs[0]] * (degree + 1), np.sort(inner), [xs[-1]] * (degree + 1)])
        try:
            spline = interpolate.make_lsq_spline(xs, ys, t, k=degree, w=None if w is None else w[order])
        except (ValueError, np.linalg.LinAlgError) as error:
            raise SimplydataError(f"The knots do not fit the points ({error}): each piece between knots needs points "
                                  "(Schoenberg-Whitney). Use fewer knots, or move them.") from None
        spline = interpolate.BSpline(spline.t, spline.c, spline.k, extrapolate=False)
        how = (f"a least-squares spline of degree {degree} with {inner.size} inner knots (SciPy make_lsq_spline, as "
               f"R lm(y ~ splines::bs(x, knots = ..., degree = {degree})))")
        low, high = float(xs[0]), float(xs[-1])
    elif allowed_error is not None:
        xs, ys, order = _sorted_points(xs, ys, example)
        if xs.size <= degree:
            raise SimplydataError(f"A spline of degree {degree} needs at least {degree + 1} points; there are "
                                  f"{xs.size}.")
        spline = interpolate.make_splrep(xs, ys, s=float(allowed_error), k=degree,
                                         w=None if w is None else w[order])
        spline = interpolate.BSpline(spline.t, spline.c, spline.k, extrapolate=False)
        gap = float(np.sum(((ys - spline(xs)) * (1 if w is None else w[order])) ** 2))
        how = (f"a spline of degree {degree} with the fewest knots ({spline.t.size - 2 * (degree + 1)} inner) that "
               f"keep the sum of squared distances at most {_show(allowed_error)} (here {_show(gap)}; SciPy "
               "make_splrep, FITPACK s, as splrep(s=))")
        low, high = float(xs[0]), float(xs[-1])
    else:
        xs, ys, order = _sorted_points(xs, ys, example)
        if w is not None:
            raise SimplydataError("weights= is for a curve that passes near the points (allowed_error=, knots=); "
                                  "a curve through every point meets each point exactly.")
        key = ENDS.get(str(ends).strip().lower()) if isinstance(ends, str) else None
        if key is None:
            raise choice_error("curve_through_points", "ends", ends, ["natural", "not-a-knot", "periodic", "clamped"])
        if xs.size <= degree and not (degree == 3 and key == "natural" and xs.size >= 2):
            raise SimplydataError(f"A spline of degree {degree} through every point needs at least {degree + 1} "
                                  f"points; there are {xs.size}.")
        if key == "periodic" and not math.isclose(ys[0], ys[-1], rel_tol=1e-9, abs_tol=1e-12):
            raise SimplydataError("ends=\"periodic\" is for a cycle: the first and last y must be the same.")
        if degree != 3 and key not in ("natural", "periodic"):
            raise SimplydataError(f'ends="{key}" is for a cubic spline (degree=3); other degrees take the SciPy ends '
                                  '(leave ends= out) or ends="periodic".')
        bc = key if degree == 3 or key == "periodic" else None  # natural ends exist only for cubic splines
        spline = interpolate.make_interp_spline(xs, ys, k=degree, bc_type=bc)
        spline = interpolate.BSpline(spline.t, spline.c, spline.k, extrapolate=False)
        end_words = {"natural": "natural ends (no bend at the first and last point)", "not-a-knot": "not-a-knot ends",
                     "periodic": "periodic ends (a cycle)", "clamped": "clamped ends (slope 0 at both ends)"}
        how = (f"a spline of degree {degree} through every point"
               + (f" with {end_words[key]}" if bc else "")
               + " (SciPy make_interp_spline"
               + (', as R splinefun(method = "natural")' if degree == 3 and key == "natural" else "")
               + ")")
        low, high = float(xs[0]), float(xs[-1])
    said = f"A curve through {xs.size} points, from x = {_show(low)} to {_show(high)}: {how}."
    print(said)
    return Curve(spline, "curve", said, low, high, {"degree": degree, **names})


def _path(xs, ys, degree, allowed_error, w, chosen):
    from scipy import interpolate

    if chosen and chosen != ["allowed_error="]:
        raise SimplydataError(f"A path (in_order=True) takes allowed_error= or nothing; not {chosen[0]}.")
    if xs.size <= degree:
        raise SimplydataError(f"A path of degree {degree} needs at least {degree + 1} points; there are {xs.size}.")
    spline, _fractions = interpolate.make_splprep([xs, ys], s=0.0 if allowed_error is None else float(allowed_error),
                                                  k=degree, w=w)
    said = (f"A path through {xs.size} points in their order (x and y along a fraction from 0 to 1): a spline of "
            f"degree {degree}{' through every point' if not allowed_error else ''} (SciPy make_splprep, as splprep).")
    print(said)
    return Curve(spline, "path", said, 0.0, 1.0, {"degree": degree, "x": "x", "y": "y"})


def _surface(xs, ys, zs, degree, knots, allowed_error, w, on_sphere, chosen):
    from scipy import interpolate

    if zs.size != xs.size:
        raise SimplydataError("x=, y= and z= need the same number of values (one height for each point).")
    if [c for c in chosen if c not in ("knots=", "allowed_error=")]:
        raise SimplydataError("A surface (z=) takes knots= or allowed_error=; not smoothness= or slopes=.")
    if degree > 5:
        raise SimplydataError("degree= is at most 5 for a surface.")
    ux, uy = np.unique(xs), np.unique(ys)
    full = ux.size * uy.size == xs.size and ux.size > 1 and uy.size > 1 and \
        np.unique(np.column_stack([xs, ys]), axis=0).shape[0] == xs.size
    s = 0.0 if allowed_error is None else float(allowed_error)
    if on_sphere:
        if np.any(np.abs(xs) > 90):
            raise SimplydataError("on_sphere=True reads x as the latitude, from -90 to 90 degrees.")
        theta, phi = np.radians(90.0 - xs), np.radians(np.mod(ys, 360.0))
        if knots is not None:
            tt, tp = _surface_knots(knots)
            spline = interpolate.LSQSphereBivariateSpline(theta, phi, zs, np.sort(np.radians(90.0 - tt)),
                                                          np.sort(np.radians(np.mod(tp, 360.0))), w=w)
            how = "a least-squares spline on the sphere with the given knots (SciPy LSQSphereBivariateSpline)"
        elif full and w is None:
            lat, lon = np.unique(theta), np.unique(phi)
            grid = np.full((lat.size, lon.size), np.nan)
            grid[np.searchsorted(lat, theta), np.searchsorted(lon, phi)] = zs
            spline = interpolate.RectSphereBivariateSpline(lat, lon - np.pi, grid, s=s)
            spline = _ShiftedLongitude(spline)
            how = "a spline on the sphere over the grid of latitudes and longitudes (SciPy RectSphereBivariateSpline)"
        else:
            spline = interpolate.SmoothSphereBivariateSpline(theta, phi, zs, w=w, s=s if allowed_error is not None
                                                             else float(xs.size))
            how = "a smoothing spline on the sphere through scattered points (SciPy SmoothSphereBivariateSpline)"
        said = f"A surface over {xs.size} points on a sphere (x the latitude, y the longitude): {how}."
        print(said)
        return Curve(spline, "surface", said, extra={"degree": 3, "sphere": True, "x": "x", "y": "y"})
    if knots is not None:
        tx, ty = _surface_knots(knots)
        spline = interpolate.LSQBivariateSpline(xs, ys, zs, np.sort(tx), np.sort(ty), w=w, kx=degree, ky=degree)
        how = f"a least-squares spline of degree {degree} with the given knots (SciPy LSQBivariateSpline)"
    elif full and w is None:
        grid = np.full((ux.size, uy.size), np.nan)
        grid[np.searchsorted(ux, xs), np.searchsorted(uy, ys)] = zs
        if ux.size <= degree or uy.size <= degree:
            raise SimplydataError(f"A surface of degree {degree} needs at least {degree + 1} values along x and along "
                                  "y.")
        spline = interpolate.RectBivariateSpline(ux, uy, grid, kx=degree, ky=degree, s=s)
        how = (f"a spline of degree {degree} over the full grid of points"
               f"{' through every point' if s == 0 else ''} (SciPy RectBivariateSpline, as bisplrep on a grid)")
    else:
        if xs.size < (degree + 1) ** 2:
            raise SimplydataError(f"A surface of degree {degree} through scattered points needs at least "
                                  f"{(degree + 1) ** 2} points; there are {xs.size}.")
        spline = interpolate.SmoothBivariateSpline(xs, ys, zs, w=w, kx=degree, ky=degree,
                                                   s=s if allowed_error is not None else None)
        how = (f"a smoothing spline of degree {degree} through scattered points (SciPy SmoothBivariateSpline, as "
               "bisplrep)")
    said = f"A surface over {xs.size} points: {how}."
    print(said)
    return Curve(spline, "surface", said, extra={"degree": degree, "x": "x", "y": "y"})


def _surface_knots(knots):
    if not (isinstance(knots, dict) and set(knots) == {"x", "y"}):
        raise SimplydataError('knots= for a surface is a dict of inner knots along each direction: '
                              'knots={"x": [2, 4], "y": [1]}.')
    return _numbers(knots["x"], "knots", 'knots={"x": [2, 4], "y": [1]}'), \
        _numbers(knots["y"], "knots", 'knots={"x": [2, 4], "y": [1]}')


class _ShiftedLongitude:
    """RectSphereBivariateSpline wants longitudes from -pi to pi: this reads longitudes from 0 to 2 pi."""

    def __init__(self, spline):
        self.spline = spline
        self.scipy_name = type(spline).__name__

    def ev(self, theta, phi, dx=0, dy=0):
        return self.spline.ev(theta, np.asarray(phi) - np.pi, dtheta=dx, dphi=dy)

    def get_knots(self):
        return self.spline.get_knots()
