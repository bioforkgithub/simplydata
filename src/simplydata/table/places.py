"""Directions, places and extremes (phase S3c-3): table.find_average_direction_of, table.find_variogram_of and
table.find_return_levels_of, and the circular and spatial branches of compare_shape_to(full_turn=) and
find_autocorrelation_of(x=, y=).

Every number comes from a package: SciPy for the circular summaries (circmean, circstd, circvar,
directional_stats), R circular for the Rayleigh test, R spdep for Moran's I, R gstat for the variogram and R
extRemes for the extremes (table/places_r.py). simplydata checks the columns, chooses and prints the defaults, and
words the answer (design_evidence_private/s3c_design.md, items AC01, AC02, AC08, AC09, AB07 and AB08, with the
independent review of 2026-11-20).

* Directions: full_turn= is required (no default), because a column in radians read as degrees gives a wrong
  answer without a word (R circular's trap). The average is given from 0 up to the full turn.
* Places: Moran's I with all pairs weighted by 1 / distance, each row's weights summing to 1 (row-standardised), and
  a permutation p-value after set.seed(with_seed); nearest=8 uses the 8 nearest places instead. The weights are
  always printed, because they change the answer.
* Extremes: maximum likelihood (extRemes), profile-likelihood intervals for the return levels (Coles 2001, 3.3.3),
  the shape in the extRemes and Coles sign (xi), no silent declustering, and an extremal-index note.
"""

from __future__ import annotations

import math
import re

import narwhals as nw
import numpy as np

from .._errors import SimplydataError, friendly
from .checking_more import _new_rows_table
from .patterns import _permutation_p_sentence
from .stat_tests import _list_words
from .summaries import _key, _order, _p_sentence, _p_shown, _say_label

DIRECTION_EXAMPLE = 'table.find_average_direction_of("current_direction", full_turn=360)   (with sdata.get_example("stations"))'
FULL_TURN_HELP = ("say how big a full turn of your values is: full_turn=360 (degrees), full_turn=24 (hours of the day), "
                  "full_turn=12 (months), full_turn=365 (days of the year; 366 for leap years, 365.25 for long records) "
                  'or full_turn="radians" (2 x pi)')
FULL_TURN_WORDS = {"degrees": 360.0, "degree": 360.0, "hours": 24.0, "hour": 24.0, "radians": 2 * math.pi,
                   "radian": 2 * math.pi}
NO_DIRECTION = 0.1  # a resultant length below 0.1: no clear average direction (design AC01)
LEAST_FOR_RAYLEIGH = 5
CIRCLE_SHAPES = ("even around the circle", "even round the circle", "uniform on a circle", "uniform on the circle",
                 "circular uniform", "even on a circle")
DIRECTION_NAME = re.compile(r"(direction|bearing|heading|azimuth|wind_?dir|current_?dir|^dir$|^dir_|_dir$)", re.I)

PLACE_EXAMPLE = 'table.find_autocorrelation_of("zinc", x="east", y="north")   (with sdata.get_example("stations"))'
FEW_PLACES = 10  # fewer rows: a note (design AC08)
LONGITUDE = re.compile(r"^(lon|long|lng|longitude)$", re.I)
LATITUDE = re.compile(r"^(lat|latitude)$", re.I)

VARIOGRAM_EXAMPLE = 'table.find_variogram_of("zinc", x="east", y="north")   (with sdata.get_example("stations"))'
VARIOGRAM_KINDS = ("spherical", "exponential", "gaussian", "matern")
VARIOGRAM_SPELLINGS = {"sph": "spherical", "exp": "exponential", "gau": "gaussian", "gauss": "gaussian",
                       "mat": "matern", "matérn": "matern"}
FEW_FOR_VARIOGRAM = 30  # fewer rows: a note (design AC09)

RETURN_EXAMPLE = 'table.find_return_levels_of("sea_level", once_in=[10, 50, 100])   (with sdata.get_example("sea_levels"))'
FEW_BLOCKS = 15  # fewer blocks: a note ("the 100-year level from 20 years is uncertain")
LEAST_BLOCKS = 5
FEW_ABOVE = 30  # fewer values above the threshold: a note
LEAST_ABOVE = 10
RUNS_GUIDE = 0.7  # an extremal index below 0.7: the values above come in runs (design AB08)
# time step of the readings (series_of unit, step) -> extRemes time.units
TIME_UNITS = {("days", 1.0): "days", ("seconds", 3600.0): "hours", ("seconds", 60.0): "minutes",
              ("months", 1.0): "months"}


# ---------------------------------------------------------------------------- small helpers
def _say(x) -> str:
    """A number for a sentence: 3 significant digits, whole numbers from 1000 on."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "nan"
    if abs(x) >= 1000:
        return f"{x:,.0f}"
    return f"{x:#.3g}".rstrip(".")


def full_turn_of(step, full_turn, example=DIRECTION_EXAMPLE) -> float:
    """full_turn= as a number; it has no default (independent review 5.2)."""
    if full_turn is None:
        raise SimplydataError(f"{step}() needs full_turn=: {FULL_TURN_HELP}.\nFor example, {example}")
    if isinstance(full_turn, str):
        key = full_turn.strip().lower()
        if key in FULL_TURN_WORDS:
            return FULL_TURN_WORDS[key]
        raise SimplydataError(f"{step}() does not know full_turn={full_turn!r}; {FULL_TURN_HELP}.")
    if isinstance(full_turn, bool) or not isinstance(full_turn, (int, float, np.integer, np.floating)) or \
            not math.isfinite(full_turn) or full_turn <= 0:
        raise SimplydataError(f"{step}() needs full_turn= as a number above 0; {FULL_TURN_HELP}.")
    return float(full_turn)


def _spread(value, full_turn) -> str:
    """A circular standard deviation: a size in the units of the column, not a direction."""
    if full_turn == 360:
        return f"{value:.0f}°" if value >= 10 else f"{value:.1f}°"
    if math.isclose(full_turn, 2 * math.pi):
        return f"{value:.3g} radians"
    return f"{value:.3g} (in the units of the column)"


def _direction(value, full_turn) -> str:
    if full_turn == 360:
        return f"{value:.0f}°" if value >= 10 else f"{value:.1f}°"
    if math.isclose(full_turn, 2 * math.pi):
        return f"{value:.3g} radians"
    return f"{value:.3g} (of {full_turn:g})"


def looks_like_direction(name) -> bool:
    return isinstance(name, str) and bool(DIRECTION_NAME.search(name))


def direction_note(column) -> None:
    """The note find_average_of gives on a column named like a direction (design 1.4)."""
    if looks_like_direction(column):
        print(f'Note: "{column}" looks like directions. Directions cannot be averaged as plain numbers (the average '
              f"of 350° and 10° is 180°, the opposite way); use table.find_average_direction_of(\"{column}\", "
              "full_turn=360).")


def _outside_note(values, full_turn) -> None:
    outside = int(((values < 0) | (values >= full_turn)).sum())
    if outside:
        print(f"Note: {outside} value{'' if outside == 1 else 's'} lie outside 0 to {full_turn:g}; they are read round "
              f"the circle ({full_turn:g} + 10 is the same direction as 10).")


def _groups_of(words, step, frame, column, for_each_group_in):
    groups = words._group_columns(step, for_each_group_in, [column]) if for_each_group_in is not None else []
    values = frame.select(nw.col(column).cast(nw.Float64))[column].to_numpy().astype(float)
    keys = [_key(r) for r in frame.select(groups).rows()] if groups else [()] * len(values)
    by_group: dict = {}
    for key, v in zip(keys, values):
        by_group.setdefault(key, [])
        if not math.isnan(v):
            by_group[key].append(v)
    order = sorted(by_group, key=lambda k: tuple(_order(v) for v in k))
    skipped = int(np.isnan(values).sum())
    return groups, by_group, order, skipped


def _whole_number(step, option, value, least):
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < least:
        raise SimplydataError(f"{step}() needs {option}= as a whole number from {least}, not {value!r}.")
    return int(value)


def _two_columns(words, step, x, y, example):
    if x is None or y is None:
        raise SimplydataError(f"{step}() needs both x= and y=: the columns that say where each row is (east and "
                              f"north, or longitude and latitude).\nFor example, {example}")
    for option, name in (("x", x), ("y", y)):
        if not isinstance(name, str):
            raise SimplydataError(f"{step}() needs {option}= as one column name in quotes.\nFor example, {example}")
    if x == y:
        raise SimplydataError(f"{step}() needs two different columns for x= and y=.")


def _places(words, step, column, x, y, example):
    """The rows with a value and a place: (x, y, values, rows left out)."""
    _two_columns(words, step, x, y, example)
    words._need_name(step, "the column", column, example)
    if column in (x, y):
        raise SimplydataError(f'"{column}" cannot be both the column and one of x= and y=.')
    frame = words._number_frame(step, [column, x, y])
    data = {c: frame.select(nw.col(c).cast(nw.Float64))[c].to_numpy().astype(float) for c in (column, x, y)}
    keep = ~(np.isnan(data[column]) | np.isnan(data[x]) | np.isnan(data[y]))
    return data[x][keep], data[y][keep], data[column][keep], int((~keep).sum()), np.flatnonzero(keep)


def _lon_lat_note(x, y, xs, ys, on_globe, step) -> None:
    if on_globe:
        return
    if (LONGITUDE.match(x) or LATITUDE.match(y)) and np.all(np.abs(xs) <= 180) and np.all(np.abs(ys) <= 90):
        extra = ", on_globe=True" if step == "find_autocorrelation_of" else ""
        fix = (f'add on_globe=True, for distances along the earth: table.{step}(..., x="{x}", y="{y}"{extra})'
               if step == "find_autocorrelation_of" else "turn them into east and north in metres first (a map "
                                                         "projection)")
        print(f"Note: these look like longitude and latitude. Straight-line distances on degrees are wrong away "
              f"from the equator (a degree east is shorter further north); {fix}. simplydata does not guess.")


def _same_places(words, step, column, x, y, xs, ys, rows):
    """Two rows at the same place cannot be weighted by 1 / distance; say which, and how to average them."""
    pairs = {}
    for i, (a, b) in enumerate(zip(xs, ys)):
        pairs.setdefault((a, b), []).append(int(rows[i]) + 1)
    same = [r for r in pairs.values() if len(r) > 1]
    if same:
        shown = "; ".join("rows " + ", ".join(str(r) for r in group) for group in same[:3])
        raise SimplydataError(
            f"{step}() needs one row per place, but {len(same)} place{' has' if len(same) == 1 else 's have'} more "
            f"than one row ({shown}{' ...' if len(same) > 3 else ''}). A station sampled many times needs its "
            "values averaged first:\n"
            f'  places = table.find_average_of("{column}", for_each_group_in=["{x}", "{y}"])\n'
            f'  places.{step}("average of {column}", x="{x}", y="{y}")')


# ---------------------------------------------------------------------------- the words
class PlaceWords:
    # ------------------------------------------------------------------ AC01: circular summaries
    @friendly(others={"period": "full_turn", "units": "full_turn", "high": "full_turn", "turn": "full_turn"},
              renamed={"for_each": "for_each_group_in"})
    def find_average_direction_of(self, column=None, full_turn=None, for_each_group_in=None):
        """The average direction of a column of directions, angles or times of day, and how close together they are.

        table.find_average_direction_of("current_direction", full_turn=360)   (with sdata.get_example("stations"))
        Directions cannot be averaged as plain numbers: the average of 350° and 10° is 0°
        (north), not 180°. full_turn= is required and says how big a full turn of your values
        is: 360 (degrees), 24 (hours of the day), 12 (months), 365 (days of the year) or
        "radians". Prints the average direction (from 0 up to the full turn), the resultant
        length (1 = all the same direction, 0 = no average direction) and the circular
        standard deviation, in the same units. Gives back one row per group
        (for_each_group_in=): rows, average direction, resultant length, circular standard
        deviation and circular variance (1 - resultant length). Numbers from SciPy (circmean,
        circstd, circvar, directional_stats), the same as R circular. To test whether the
        directions have a preferred direction at all: compare_shape_to(..., shape="even around the
        circle", full_turn=360) (the Rayleigh test).
        Other names: circular mean, mean direction, circmean, mean.circular.
        """
        from scipy import stats

        step = "find_average_direction_of"
        self._need_name(step, "the column", column, DIRECTION_EXAMPLE)
        turn = full_turn_of(step, full_turn)
        frame = self._number_frame(step, [column])
        groups, by_group, order, skipped = _groups_of(self, step, frame, column, for_each_group_in)
        if skipped:
            print(f"Note: {skipped} empty cell{'' if skipped == 1 else 's'} in \"{column}\" "
                  f"{'is' if skipped == 1 else 'are'} left out.")
        everything = np.concatenate([np.asarray(v, dtype=float) for v in by_group.values()]) if by_group else \
            np.array([])
        if not len(everything):
            raise SimplydataError(f'{step}() found no values in "{column}".')
        _outside_note(everything, turn)
        rows, lines = [], []
        for key in order:
            v = np.asarray(by_group[key], dtype=float)
            label = " / ".join(_say_label(x) for x in key)
            if not len(v):
                lines.append(f"  {label}: no values (skipped)")
                continue
            average = float(stats.circmean(v, high=turn, low=0)) % turn  # SciPy can give the full turn itself
            angles = v / turn * 2 * math.pi  # onto the unit circle, for SciPy directional_stats
            length = float(stats.directional_stats(np.column_stack([np.cos(angles), np.sin(angles)])).mean_resultant_length)
            spread = float(stats.circstd(v, high=turn, low=0))
            variance = float(stats.circvar(v, high=turn, low=0))
            row = {g: k for g, k in zip(groups, key)}
            row.update({"rows": len(v), "average direction": average, "resultant length": length,
                        "circular standard deviation": spread, "circular variance": variance})
            rows.append(row)
            clear = ("the directions are close together" if length >= 0.7 else
                     "the directions are spread out" if length >= NO_DIRECTION else
                     "there is no clear average direction")
            if groups:
                lines.append(f"  {label}: {_direction(average, turn)} (resultant length {length:.2f}: {clear}; "
                             f"circular standard deviation {_spread(spread, turn)}"
                             f"{' (not meaningful here)' if length < NO_DIRECTION else ''}; {len(v)} values)")
            else:
                lines.append(f'The average direction of "{column}" is {_direction(average, turn)} (resultant length '
                             f"{length:.2f}: {clear}; 1 = all the same direction, 0 = no average direction). "
                             f"Circular standard deviation {_spread(spread, turn)}"
                             f"{' (not meaningful here)' if length < NO_DIRECTION else ''} ({len(v)} values).")
                if length < NO_DIRECTION:
                    lines.append("The average direction is still given, but with a resultant length this small it "
                                 "means little: the directions point every way (or to two opposite sides).")
        if groups:
            print(f'The average direction of "{column}" for each {_list_words(chr(34) + g + chr(34) for g in groups)} '
                  f"(full turn {turn:g}):")
        for line in lines:
            print(line)
        print(f"Method: SciPy stats.circmean, circstd and circvar with low=0, high={turn:g}, and "
              "directional_stats for the resultant length; the same numbers as R circular's mean.circular, rho.circular, "
              "sd.circular and var.circular with the units given.")
        print(f"simplydata chooses: the average from 0 up to {turn:g} (R circular gives the same direction from "
              f"-{turn / 2:g} to {turn / 2:g}{', such as -43° for 317°' if turn == 360 else ''}), and the circular "
              "standard deviation "
              "sqrt(-2 ln(resultant length)), as R sd.circular, in the units of the column.")
        return _new_rows_table(self, rows)

    # ------------------------------------------------------------------ AC02: the Rayleigh test
    def _circle_shape_wanted(self, shape, test, full_turn) -> bool:
        """compare_shape_to asks about a circle: an even-around-the-circle shape, test_method="rayleigh", or "uniform" with
        full_turn= given (on directions a straight-line test of "uniform" depends on where 0 is)."""
        name = shape.strip().lower() if isinstance(shape, str) else None
        if name in CIRCLE_SHAPES or (isinstance(test, str) and test.strip().lower() == "rayleigh"):
            return True
        return full_turn is not None and name in ("uniform", "even", "evenly spread")

    def _compare_circle(self, step, column, shape, full_turn, for_each_group_in, test):
        from . import places_r

        example = (f'table.compare_shape_to("{column}", shape="even around the circle", full_turn=360)   '
                   '(with sdata.get_example("stations"))')
        name = shape.strip().lower() if isinstance(shape, str) else shape
        if test is not None and not isinstance(test, str):
            raise SimplydataError(f'test_method= is a name in quotes; on a circle it is test_method="rayleigh".\nFor example, {example}')
        if name not in CIRCLE_SHAPES and name not in ("uniform", "even", "evenly spread", "normal"):
            raise SimplydataError(f'On a circle (full_turn=) the shape to compare with is "even around the circle" (the '
                                  f"Rayleigh test); {shape!r} is not offered there.\nFor example, {example}")
        if test is not None and test.strip().lower() != "rayleigh":
            raise SimplydataError(f'On a circle the test is "rayleigh" (test_method="{test}" is a test of a bell shape).\n'
                                  f"For example, {example}")
        turn = full_turn_of(step, full_turn, example)
        frame = self._number_frame(step, [column])
        groups, by_group, order, skipped = _groups_of(self, step, frame, column, for_each_group_in)
        if skipped:
            print(f"Note: {skipped} empty cell{'' if skipped == 1 else 's'} in \"{column}\" "
                  f"{'is' if skipped == 1 else 'are'} left out.")
        everything = np.concatenate([np.asarray(v, dtype=float) for v in by_group.values()]) if by_group else \
            np.array([])
        _outside_note(everything, turn)
        null = "the directions were spread evenly around the circle"
        far = "directions this close together or closer"
        rows, lines, any_even = [], [], False
        for key in order:
            v = np.asarray(by_group[key], dtype=float)
            label = " / ".join(_say_label(x) for x in key)
            problem = None
            if len(v) < LEAST_FOR_RAYLEIGH:
                problem = f"only {len(v)} value{'' if len(v) == 1 else 's'}: the Rayleigh test needs at least " \
                          f"{LEAST_FOR_RAYLEIGH}"
            if problem and not groups:
                raise SimplydataError(f'{step}() cannot test "{column}": {problem}.')
            r = math.nan
            p = math.nan
            if not problem:
                found = places_r.rayleigh(v, turn)
                r, p = found["statistic"], found["p"]
            row = {g: k for g, k in zip(groups, key)}
            row.update({"test": "Rayleigh test", "what it compares": f'the directions of "{column}" with directions '
                        "spread evenly around the circle", "statistic name": "resultant length", "statistic": r,
                        "p-value": p, "rows": len(v)})
            rows.append(row)
            if problem:
                lines.append(f"  {label}: not tested ({problem}).")
                continue
            even = p >= 0.05
            any_even = any_even or even
            looks = "could well be spread evenly around the circle" if even else "have a preferred direction"
            if groups:
                lines.append(f"  {label}: {looks} (resultant length {r:.2f}, {_p_shown(p)}, {len(v)} values)")
            else:
                lines.append(f'The directions of "{column}" {looks} (Rayleigh test: resultant length {r:.2f}, '
                             f"{len(v)} values).")
                lines.append(_p_sentence(p, null, far, "that they are spread evenly"))
        if groups:
            print(f'Are the directions of "{column}" spread evenly around the circle in each '
                  f"{_list_words(chr(34) + g + chr(34) for g in groups)}? The Rayleigh test; each p-value says how "
                  f"often {far} would turn up if {null}:")
        for line in lines:
            print(line)
        print(f"Test: the Rayleigh test, R {places_r.circular_call(turn).replace('circular::circular(', 'circular::rayleigh.test(circular::circular(')})"
              " (the units are always given: R circular reads plain numbers as radians).")
        if any_even:
            print("Note: the Rayleigh test looks for one preferred direction; directions gathered at two opposite "
                  "sides (such as a tidal current that runs in and out) can look even. Draw them first: "
                  f'chart.draw_polar(angle="{column}", distance=..., full_turn={turn:g}).')
        return _new_rows_table(self, rows)

    # ------------------------------------------------------------------ AC08: Moran's I
    def _spatial_autocorrelation(self, column, x, y, on_globe, nearest, permutations, with_seed):
        from . import places_r

        step = "find_autocorrelation_of"
        if not isinstance(on_globe, bool):
            raise SimplydataError(f"{step}() needs on_globe= as True or False.")
        xs, ys, z, left_out, rows = _places(self, step, column, x, y, PLACE_EXAMPLE)
        n = len(z)
        if n < 5:
            raise SimplydataError(f"{step}() needs at least 5 places with a value; there are {n}.")
        if nearest is not None:
            nearest = _whole_number(step, "nearest", nearest, 1)
            if nearest >= n:
                raise SimplydataError(f"{step}() has {n} places, so nearest= can be at most {n - 1}.")
        permutations = _whole_number(step, "permutations", permutations, 99)
        if isinstance(with_seed, bool) or not isinstance(with_seed, (int, np.integer)) or not 0 <= with_seed < 2 ** 31:
            raise SimplydataError(f"{step}() needs with_seed= as a whole number from 0 (for example with_seed=1).")
        if on_globe and (np.any(np.abs(xs) > 180) or np.any(np.abs(ys) > 90)):
            raise SimplydataError(f'on_globe=True needs x= as longitude (-180 to 180) and y= as latitude (-90 to 90); '
                                  f'"{x}" or "{y}" goes beyond that.')
        if np.ptp(z) == 0:
            raise SimplydataError(f'Every value of "{column}" is the same, so there is no pattern to find.')
        _same_places(self, step, column, x, y, xs, ys, rows)
        found = places_r.moran(xs, ys, z, on_globe=on_globe, nearest=nearest, permutations=permutations,
                               seed=int(with_seed))
        i, p, expected = found["i"], found["p"], found["expected"]
        if nearest:
            weights = (f"each place's {nearest} nearest places count, alike, and the others not at all "
                       f"(each row's weights summing to 1)")
            short = f"the {nearest} nearest places"
        else:
            weights = ("every pair counts, nearer pairs more (weights 1 / distance, each row's weights summing to 1)")
            short = "1 / distance, all pairs"
        if left_out:
            print(f"Note: {left_out} row{'' if left_out == 1 else 's'} with an empty cell in \"{column}\", \"{x}\" or "
                  f'"{y}" {"is" if left_out == 1 else "are"} left out.')
        no_pattern = f"no pattern gives about 0, here {expected:.3f}"
        if i > expected and p < 0.05:
            print(f'Nearby places have more alike values of "{column}" than distant ones: Moran\'s I = {i:.3f} '
                  f"({no_pattern}), where {weights}.")
        elif i < expected and found["p_less"] < 0.05:
            print(f'Nearby places have less alike values of "{column}" than distant ones: Moran\'s I = {i:.3f} '
                  f"({no_pattern}), where {weights}. The test below looks for nearby places being more alike.")
        else:
            print(f'Moran\'s I of "{column}" is {i:.3f} ({no_pattern}), where {weights}: nearby places are not clearly '
                  "more alike than distant ones.")
        print(_permutation_p_sentence(p, permutations, "the values were scattered over the places at random",
                                      "nearby values at least this alike", "that the values are scattered at random"))
        call = places_r.moran_code(on_globe, nearest, permutations, int(with_seed)).split("t <- spdep::moran.test")[0]
        print(f"Method: R {call.strip()} ({n} places; spdep::moran.test for the value with no pattern, and with "
              'alternative = "less" before a sentence about nearby places being less alike).')
        chosen = [("the 1 / distance weights between all pairs, row-standardised" if not nearest else None),
                  f"{permutations:,} permutations after set.seed({int(with_seed)})",
                  "a one-sided test (nearby places more alike), spdep's default"]
        if on_globe:
            chosen.append("great-circle distances (on_globe=True, in km)")
        print(f"simplydata chooses: {_list_words(c for c in chosen if c)}. The weights change Moran's I, so say them "
              "when you report it.")
        _lon_lat_note(x, y, xs, ys, on_globe, step)
        if n < FEW_PLACES:
            print(f"Note: only {n} places; Moran's I from so few places is rough.")
        return _new_rows_table(self, [{"Moran's I": i, "value with no pattern": expected, "p-value": p,
                                       "permutations": permutations, "places": n, "weights": short}])

    # ------------------------------------------------------------------ AC09: the variogram
    def _variogram_input(self, step, column, x, y, of_kind, between, example):
        kind = of_kind.strip().lower() if isinstance(of_kind, str) else of_kind
        kind = VARIOGRAM_SPELLINGS.get(kind, kind)
        if kind not in VARIOGRAM_KINDS:
            raise SimplydataError(f"{step}() does not know of_kind={of_kind!r}. It takes "
                                  f"{', '.join(chr(34) + k + chr(34) for k in VARIOGRAM_KINDS)}.")
        cutoff = None
        if between is not None:
            if not isinstance(between, (list, tuple)) or len(between) != 2 or not all(
                    isinstance(b, (int, float, np.integer, np.floating)) and not isinstance(b, bool) for b in between):
                raise SimplydataError(f"{step}() needs between= as two distances, from 0 to the largest, such as "
                                      "between=[0, 1500].")
            if between[0] != 0 or not between[1] > 0:
                raise SimplydataError(f"{step}() reads between= from 0 to the largest distance (the variogram always "
                                      f"starts at 0), such as between=[0, {between[1]!r}].")
            cutoff = float(between[1])
        xs, ys, z, left_out, rows = _places(self, step, column, x, y, example)
        if len(z) < 5:
            raise SimplydataError(f"{step}() needs at least 5 places with a value; there are {len(z)}.")
        if np.ptp(z) == 0:
            raise SimplydataError(f'Every value of "{column}" is the same, so there is no variogram to find.')
        if left_out:
            print(f"Note: {left_out} row{'' if left_out == 1 else 's'} with an empty cell in \"{column}\", \"{x}\" or "
                  f'"{y}" {"is" if left_out == 1 else "are"} left out.')
        places = {(a, b) for a, b in zip(xs, ys)}
        if len(places) < len(z):
            print(f"Note: {len(z) - len(places)} rows share their place with another row; their differences count at "
                  "distance 0 and add to the nugget.")
        _lon_lat_note(x, y, xs, ys, False, step)
        if len(z) < FEW_FOR_VARIOGRAM:
            print(f"Note: only {len(z)} places; a variogram usually needs 30 or more (and 100 or more for a clear "
                  "curve).")
        return kind, cutoff, xs, ys, z

    @friendly(others={"model": "of_kind", "kind": "of_kind", "cutoff": "between"})
    def find_variogram_of(self, column=None, x=None, y=None, of_kind="spherical", between=None):
        """A variogram: how different two values are, on average, at each distance apart.

        table.find_variogram_of("zinc", x="east", y="north")   (with sdata.get_example("stations"))
        Places close together usually have alike values; further apart they differ more, until
        beyond some distance (the range) they are unrelated. The variogram shows this: the
        semivariance (half the average squared difference) of all pairs of places in bins of
        distance, with a curve fitted through them. Prints the range (in the units of x and y),
        the nugget (differences even between very close places: measurement error or variation
        at shorter distances than were sampled) and the partial sill (the rise from the nugget
        to the plateau). of_kind="spherical" (default), "exponential", "gaussian" or "matern"
        chooses the curve; between=[0, 1500] sets the largest distance (default: a third of the
        diagonal of the area, as R gstat). Gives back one row per distance bin: distance,
        semivariance, pairs, the fitted semivariance, and the fitted nugget, partial sill and range.
        Numbers from R gstat (variogram, fit.variogram). The chart: chart.draw_variogram(...).
        Needs R (gstat). Other names: semivariogram, gstat.
        """
        from . import places_r

        step = "find_variogram_of"
        kind, cutoff, xs, ys, z = self._variogram_input(step, column, x, y, of_kind, between, VARIOGRAM_EXAMPLE)
        found = places_r.variogram(xs, ys, z, kind, cutoff)
        problem = variogram_problem(found, kind, column, x, y)
        if problem:
            raise SimplydataError(problem)
        nugget, psill, rng = found["nugget"], found["psill"], found["range"]
        units = f'in the units of "{x}" and "{y}"'
        if kind == "spherical":
            print(f'Values of "{column}" become unrelated beyond about {_say(rng)} (the range, {units}).')
        else:
            times = {"exponential": "three times", "gaussian": "about 1.7 times",
                     "matern": "three times (with kappa 0.5, as here)" if math.isclose(found["kappa"], 0.5)
                     else "a few times"}[kind]
            print(f'Values of "{column}" become nearly unrelated at about {times} the range parameter {_say(rng)} '
                  f"({units}): for the {kind} curve, gstat's range is not the distance where the curve levels off.")
        print(f"Nugget {_say(nugget)} (differences even between very close places: measurement error or variation at "
              f"shorter distances than were sampled), partial sill {_say(psill)} (the further rise from the nugget up "
              "to the plateau).")
        cut = f", cutoff = {cutoff:g}" if cutoff is not None else ""
        model = places_r.VARIOGRAM_MODELS[kind]
        print(f"Method: R gstat::variogram(z ~ 1, locations = ~ x + y, data{cut}) ({len(found['dist'])} distance bins"
              f"{'' if cutoff is not None else ', up to a third of the diagonal'}), then gstat::fit.variogram(v, "
              f'gstat::vgm("{model}")) with gstat\'s own start values and fit.method = 7 (weighted least squares, '
              "the weights the number of pairs / distance^2).")
        print(f"simplydata chooses: the {kind} curve{' (the default)' if kind == 'spherical' else ''}, gstat's own "
              "start values, and the range said in words, because for the exponential, Gaussian and Matern curves "
              "gstat's range parameter is not the practical range.")
        rows = [{"distance": float(d), "semivariance": float(g), "pairs": int(n), "fitted semivariance": float(f),
                 "nugget": nugget, "partial sill": psill, "range": rng}
                for d, g, n, f in zip(found["dist"], found["gamma"], found["np"], found["fitted"])]
        return _new_rows_table(self, rows)

    # ------------------------------------------------------------------ AB07 / AB08: return levels
    @friendly(others={"return_period": "once_in", "return_periods": "once_in", "period": "once_in",
                      "peaks_above": "values_above", "threshold": "values_above", "over": "values_above",
                      "peaks_over_threshold": "values_above"})
    def find_return_levels_of(self, column=None, once_in=(10, 50, 100), values_above=None, sorted_by=None):
        """Return levels: the level reached on average once in 10, 50 or 100 years (extreme values).

        table.find_return_levels_of("sea_level", once_in=[10, 50, 100])   (with sdata.get_example("sea_levels"))
        A return level is the level reached on average once in a given number of years: the
        100-year level has a 1-in-100 chance of being reached in any one year (it can happen twice
        in a decade, or not in 200 years). Two ways:
        - each row is the largest value of one block, such as a year (block maxima): a GEV curve
          (generalised extreme value) is fitted to the rows. Give sorted_by="year" so the word can
          check there is one row per year; daily readings are refused (take the yearly largest
          first: table.find_biggest_of("sea_level", for_each_group_in="date", every="year")).
        - values_above=30 uses every reading above 30 (peaks over a threshold): a generalised
          Pareto curve is fitted to the amounts above it. sorted_by= (dates) is then needed, to
          know how many readings make a year. Choose the threshold with chart.draw_threshold_check().
        Prints each return level with its 95 % profile-likelihood interval (asymmetric, as return
        levels are), and the shape of the curve. Gives back one row per return period. For lows
        (low oxygen, low water), turn the column round first (table.add_column("minus_oxygen",
        "-oxygen")). Numbers from R extRemes (fevd, return.level, ci). Needs R (extRemes).
        Other names: GEV, GPD, peaks over threshold, return period, fevd.
        """
        from . import places_r

        step = "find_return_levels_of"
        self._need_name(step, "the column", column, RETURN_EXAMPLE)
        periods = _periods(step, once_in)
        if values_above is not None:
            if isinstance(values_above, bool) or not isinstance(values_above, (int, float, np.integer, np.floating)) \
                    or not math.isfinite(values_above):
                raise SimplydataError(f"{step}() needs values_above= as one number, the threshold, such as "
                                      "values_above=30.")
            if sorted_by is None:
                raise SimplydataError(
                    f"{step}() with values_above= needs sorted_by=, a column of dates: the word must know how many "
                    f"readings make a year to say 'once in 100 years'.\nFor example, table.{step}(\"{column}\", "
                    f'once_in=[10, 100], values_above={values_above!r}, sorted_by="date")')
            return self._peaks_over_threshold(step, column, periods, float(values_above), sorted_by)
        values, unit = self._block_maxima_input(step, column, sorted_by)
        found = places_r.block_maxima(values, periods)
        location, scale, shape = (float(v) for v in found["par"])
        print(f'GEV (generalised extreme value) curve fitted to {len(values)} block maxima of "{column}" '
              f"(each row the largest value of one {unit[:-1] if unit.endswith('s') else unit}).")
        rows = self._say_return_levels(found, periods, unit)
        low, high = float(found["par_low"][2]), float(found["par_high"][2])
        self._say_shape(shape, low, high, f"Location {_say(location)}, scale {_say(scale)}.", "GEV")
        self._convergence_note(found)
        print('Method: R extRemes::fevd(x, type = "GEV", method = "MLE"); extRemes::return.level(); '
              'extRemes::ci.fevd(type = "return.level", method = "proflik") for each interval.')
        self._extremes_choices()
        if len(values) < FEW_BLOCKS:
            print(f"Note: only {len(values)} blocks; a {max(periods):g}-{unit[:-1] if unit.endswith('s') else unit} "
                  f"level from {len(values)} blocks is very uncertain.")
        return _new_rows_table(self, rows)

    def _block_maxima_input(self, step, column, sorted_by):
        from .._time_axis import series_of

        frame = self._number_frame(step, [column])
        if sorted_by is None:
            values = frame.select(nw.col(column).cast(nw.Float64))[column].to_numpy().astype(float)
            unit = "blocks"
            print("Each row is taken as the largest value of one block (for example a year); give sorted_by= with "
                  "the years to be sure.")
        else:
            self._need_columns(sorted_by)
            dtype = self._frame.schema[sorted_by]
            if dtype.is_numeric():
                years = self._frame[sorted_by].to_numpy()
                if len(set(years.tolist())) < len(years):
                    raise SimplydataError(_several_per_year(step, column, sorted_by, "the same value in several rows"))
            elif dtype.is_temporal():
                # yearly maxima are often stored with the date each happened: one row per calendar year is the test
                years = self._frame.select(nw.col(sorted_by).dt.year())[sorted_by].to_list()
                if len(set(years)) < len(years):
                    raise SimplydataError(_several_per_year(step, column, sorted_by, "more than one row in a year"))
            series = series_of(self, column, sorted_by, None, step, RETURN_EXAMPLE)[0]
            values = series.values
            unit = "years" if dtype.is_temporal() else _block_unit(series, sorted_by, column, step)
        empty = int(np.isnan(values).sum())
        if empty:
            print(f"Note: {empty} empty cell{'' if empty == 1 else 's'} in \"{column}\" {'is' if empty == 1 else 'are'} "
                  "left out.")
            values = values[~np.isnan(values)]
        if len(values) < LEAST_BLOCKS:
            raise SimplydataError(f"{step}() needs at least {LEAST_BLOCKS} block maxima; there are {len(values)}.")
        if np.ptp(values) == 0:
            raise SimplydataError(f'Every value of "{column}" is the same, so no curve can be fitted.')
        return values, unit

    def _peaks_over_threshold(self, step, column, periods, threshold, sorted_by):
        from .._time_axis import series_of
        from . import places_r

        series = series_of(self, column, sorted_by, None, step, RETURN_EXAMPLE)[0]
        if series.unit not in ("days", "seconds", "months"):
            raise SimplydataError(f'{step}() with values_above= needs sorted_by= as dates (daily, hourly or monthly '
                                  f'readings), so that it knows how many readings make a year; "{sorted_by}" '
                                  "holds plain numbers.")
        units = TIME_UNITS.get((series.unit, float(series.step)))
        if units is None or not series.regular:
            raise SimplydataError(f"{step}() with values_above= needs evenly spaced readings: one a day, an hour, a "
                                  f'minute or a month. "{sorted_by}" has {"uneven steps" if not series.regular else "another step"}.')
        empty = int(np.isnan(series.values).sum())
        if empty:
            raise SimplydataError(
                f'"{column}" has {empty} empty cell{"" if empty == 1 else "s"}. Above a threshold, the word counts '
                f"readings to make years ({units}), so empty readings would make the years too short. Fill them only "
                "if you know their values; otherwise use the yearly largest values (block maxima) instead.")
        values = series.values
        above = int((values > threshold).sum())
        if above < LEAST_ABOVE:
            raise SimplydataError(f"Only {above} values lie above {threshold:g}; a curve needs at least {LEAST_ABOVE} "
                                  "(usually 30 or more). Choose a lower threshold: chart.draw_threshold_check(...).")
        found = places_r.over_threshold(values, threshold, units, periods)
        scale, shape = (float(v) for v in found["par"])
        print(f'Generalised Pareto curve fitted to the {above} values of "{column}" above {threshold:g} '
              f"(of {len(values):,} readings, one {'an hour' if units == 'hours' else 'a ' + units[:-1]}).")
        rows = self._say_return_levels(found, periods, "years")
        low, high = float(found["par_low"][1]), float(found["par_high"][1])
        self._say_shape(shape, low, high, f"Scale {_say(scale)} (of the amounts above {threshold:g}).", "GP")
        self._convergence_note(found)
        print(f'Method: R extRemes::fevd(x, threshold = {threshold:g}, type = "GP", time.units = "{units}"); '
              'extRemes::return.level(); extRemes::ci.fevd(type = "return.level", method = "proflik") for each '
              f"interval; extRemes::extremalindex(x, {threshold:g}) for the runs.")
        self._extremes_choices()
        theta = found.get("extremal_index", math.nan)
        if math.isfinite(theta) and theta < RUNS_GUIDE:
            print(f"Note: the values above {threshold:g} come in runs (extremal index {theta:.2f}, below "
                  f"{RUNS_GUIDE}): one storm gives several of them, which the curve counts as separate. Consider "
                  "keeping one peak per run; simplydata does not do this for you.")
        elif math.isfinite(theta):
            print(f"The values above {threshold:g} come mostly one at a time (extremal index {theta:.2f}; 1 = never "
                  "in runs).")
        if above < FEW_ABOVE:
            print(f"Note: only {above} values above the threshold; with fewer than {FEW_ABOVE} the curve is rough.")
        return _new_rows_table(self, rows)

    @staticmethod
    def _say_return_levels(found, periods, unit):
        rows = []
        word = unit[:-1] if unit.endswith("s") else unit
        for j, t in enumerate(periods):
            level = float(found["level"][j])
            low, high = float(found["profile_low"][j]), float(found["profile_high"][j])
            n_low, n_high = float(found["normal_low"][j]), float(found["normal_high"][j])
            profile = math.isfinite(low) and math.isfinite(high)
            if not profile:
                low, high = n_low, n_high
            how = "profile likelihood" if profile else "normal approximation"
            each = (f"a 1-in-{t:g} chance in any one {word}" if unit == "years" else
                    "years, if each row is one year")
            print(f"A level of {_say(level)} is reached on average once in {t:g} {unit} ({each}); 95 % CI "
                  f"{_say(low)} to {_say(high)} ({how}).")
            if not profile:
                print(f"Note: extRemes found no profile-likelihood interval for once in {t:g}; the normal "
                      "approximation is given, which is too narrow for long return periods.")
            rows.append({"once in": float(t), "time unit": unit, "level": level, "95 % CI low": low,
                         "95 % CI high": high, "interval": how, "normal 95 % CI low": n_low,
                         "normal 95 % CI high": n_high})
        return rows

    @staticmethod
    def _say_shape(shape, low, high, rest, kind):
        light = "a Gumbel curve" if kind == "GEV" else "an exponential tail"
        if low <= 0 <= high:
            reading = f"its interval includes 0, so the upper tail is close to {light}"
        elif shape < 0:
            reading = "below 0: the values have an upper limit"
        else:
            reading = f"above 0: a heavy upper tail, where very high values are more likely than {light} says"
        sign = "SciPy's genextreme uses c = -xi" if kind == "GEV" else "SciPy's genpareto uses the same sign"
        print(f"Shape xi = {shape:.3f} (95 % CI {low:.3f} to {high:.3f}, normal approximation): {reading}. {rest} (xi in the sign of extRemes "
              f"and Coles 2001; {sign}.)")

    @staticmethod
    def _convergence_note(found):
        if found.get("convergence", 0) != 0:
            print("Note: extRemes's search for the best curve did not settle (optim convergence code "
                  f"{found['convergence']:g}); the numbers above may be off. Check the data, or try more blocks.")

    @staticmethod
    def _extremes_choices():
        print("simplydata chooses: maximum likelihood; profile-likelihood intervals (Coles 2001, section 3.3.3: the "
              "normal approximation is too narrow and too symmetric for long return periods); no declustering. "
              "The levels are in the units of the column.")


def variogram_problem(found, kind, column, x, y):
    """Why gstat's fit cannot be used (singular, no convergence, no range), or None; for the word and the chart."""
    text = " ".join(found["warnings"]).strip()
    if found["singular"] or "convergence" in text.lower() or not math.isfinite(found["range"]) or found["range"] <= 0:
        others = [k for k in VARIOGRAM_KINDS if k != kind]
        return (f"gstat could not fit a {kind} curve to these points{' (' + text + ')' if text else ''}. Try another "
                f'curve, such as of_kind="{others[0]}", or look at the points first: table.find_variogram_of("{column}", '
                f'x="{x}", y="{y}").')
    return None


def _periods(step, once_in):
    values = [once_in] if isinstance(once_in, (int, float, np.integer, np.floating)) and not isinstance(once_in, bool) \
        else once_in
    if not isinstance(values, (list, tuple)) or not values or not all(
            isinstance(t, (int, float, np.integer, np.floating)) and not isinstance(t, bool) and math.isfinite(t)
            for t in values):
        raise SimplydataError(f"{step}() needs once_in= as a number or a list of numbers, such as "
                              "once_in=[10, 50, 100].")
    if any(t <= 1 for t in values):
        raise SimplydataError(f"{step}() needs once_in= above 1: a level reached once in 1 year or less is not an "
                              "extreme.")
    return [float(t) for t in dict.fromkeys(values)]


def _block_unit(series, sorted_by, column, step) -> str:
    """The block of each row: years (dates a year or more apart, or year numbers), else refused: daily readings are
    not block maxima (independent review 5.3)."""
    times = series.times
    gaps = np.diff(times) if times is not None and len(times) > 1 else np.array([])
    if times is not None and len(gaps) and np.all(times == np.round(times)) and gaps.min() >= 1 and             np.all((times >= 1000) & (times <= 3000)):
        return "years"
    return "blocks"


def _several_per_year(step, column, sorted_by, what) -> str:
    return (f'{step}() reads each row as the largest value of one year (block maxima), but "{sorted_by}" has '
            f"several rows per year ({what}). Take the largest value of each year first:\n"
            f'  yearly = table.find_biggest_of("{column}", for_each_group_in="{sorted_by}", every="year")\n'
            f'or use every reading above a threshold: table.{step}("{column}", values_above=..., sorted_by="{sorted_by}").')
