"""Let narwhals read every pandas time zone name, such as America/New_York.

narwhals (2.27 to 2.29 at least) reads the kind of a pandas date column from its written dtype,
"datetime64[us, America/New_York]", with a pattern whose zone part takes only letters and "/". A zone
name with "_", "-", "+" or a digit (America/New_York, America/Port-au-Prince, Etc/GMT+5,
America/Argentina/Buenos_Aires) does not match, so narwhals calls the column Unknown, and every date word
on a pandas table then stops or calls the column "other values". Polars tables are not affected.

The mend widens only that pattern, so the zone name is read as written; narwhals still makes the same
Datetime(time_unit, time_zone) kind, and every date step still runs in pandas' own methods (tz_convert,
dt.year, ...). Nothing is computed here. When narwhals reads these names itself, the check below sees it
and nothing is changed. A narwhals report with a small example is drafted for its authors.
"""

from __future__ import annotations

import re

# zone names narwhals must read; the widened character class adds digits, "_", "+" and "-"
_ZONE_EXAMPLES = ("America/New_York", "America/Port-au-Prince", "Etc/GMT+5", "America/Argentina/Buenos_Aires")
_NARROW = r"[a-zA-Z\/]+"
_WIDE = r"[a-zA-Z0-9_+\-\/]+"


def _reads_every_zone(pattern) -> bool:
    return all((m := pattern.match(f"datetime64[us, {zone}]")) and m.group("time_zone") == zone
               for zone in _ZONE_EXAMPLES)


def mend_pandas_time_zones() -> bool:
    """Widen narwhals' pandas datetime pattern when it misses zone names; True when it was changed."""
    try:
        from narwhals._pandas_like import utils
    except ImportError:  # pragma: no cover - narwhals moved its pandas code; tests/test_time_zone_names.py says so
        return False
    pattern = getattr(utils, "PATTERN_PD_DATETIME", None)
    if pattern is None or _reads_every_zone(pattern) or _NARROW not in pattern.pattern:
        return False
    wide = re.compile(pattern.pattern.replace(_NARROW, _WIDE), pattern.flags)
    if not _reads_every_zone(wide) or wide.match("datetime64[ns]") is None:  # pragma: no cover
        return False
    utils.PATTERN_PD_DATETIME = wide
    cached = getattr(utils, "non_object_native_to_narwhals_dtype", None)
    if hasattr(cached, "cache_clear"):  # kinds read before the mend (Unknown) are not kept
        cached.cache_clear()
    return True


MENDED = mend_pandas_time_zones()
