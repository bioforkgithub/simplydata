"""The maths family on numbers, grids and blocks (families for 100 %, plan section 2.3, approved by Manish
2026-11-28, G1-G3 and G10).

* take_function(name, **options): every maths function of scipy.special and every NumPy function that works
  number by number, from the one name table of _maths_functions.py (the same names work in formula text);
* work_on_bits(how, with_numbers=): NumPy's bit words (bitwise_and, bitwise_or, bitwise_xor, invert, bitwise_count,
  left_shift, right_shift, packbits, unpackbits).

Each word is one library call, named in the sentence it prints.
"""

from __future__ import annotations

import textwrap

import numpy as np

from .._errors import SimplydataError, friendly, suggest
from .._typing import _Same
from ._base import BaseNumbers, amount, note_empty, to_array

PARTS = ("real", "imaginary", "size", "angle")  # take_function(part=) for answers that are complex numbers
PART_SPELLINGS = {"imag": "imaginary", "re": "real", "im": "imaginary", "abs": "size", "absolute value": "size",
                  "modulus": "size", "magnitude": "size", "phase": "angle", "argument": "angle", "arg": "angle"}

# work_on_bits(how=): plain name -> (NumPy function, what it does, what it needs)
BITS = {
    "and": ("bitwise_and", "1 where both numbers have a 1 bit", "with_numbers"),
    "or": ("bitwise_or", "1 where either number has a 1 bit", "with_numbers"),
    "only one": ("bitwise_xor", "1 where exactly one of the numbers has a 1 bit", "with_numbers"),
    "flip": ("invert", "every bit turned over (0 to 1, 1 to 0); for whole numbers that is -number - 1", ""),
    "count ones": ("bitwise_count", "how many 1 bits each number has (of its size, for numbers below 0)", ""),
    "shift left": ("left_shift", "the bits moved left by= places: times 2 for each place", "by"),
    "shift right": ("right_shift", "the bits moved right by= places: halved and rounded down for each place", "by"),
    "pack into bytes": ("packbits", "each run of 8 yes or no values (1 or 0) packed into one whole number from 0 "
                                    "to 255", ""),
    "unpack bytes": ("unpackbits", "each whole number from 0 to 255 unpacked into its 8 bits (1 or 0)", ""),
}
# NumPy's names and other spellings -> the plain name
BITS_SPELLINGS = {"bitwise_and": "and", "&": "and", "bitwise_or": "or", "|": "or", "xor": "only one",
                  "bitwise_xor": "only one", "^": "only one", "either but not both": "only one", "not": "flip",
                  "invert": "flip", "bitwise_not": "flip", "bitwise_invert": "flip", "~": "flip",
                  "bitwise_count": "count ones", "popcount": "count ones", "count bits": "count ones",
                  "left_shift": "shift left", "bitwise_left_shift": "shift left", "<<": "shift left",
                  "right_shift": "shift right", "bitwise_right_shift": "shift right", ">>": "shift right",
                  "packbits": "pack into bytes", "pack": "pack into bytes", "unpackbits": "unpack bytes",
                  "unpack": "unpack bytes"}


def _shown(value) -> str:
    if isinstance(value, (BaseNumbers, list, tuple, np.ndarray)):
        return "other numbers"
    return repr(value)


def maths_function_list(width: int = 78) -> str:
    """Every name of the maths family, group by group (what take_function() with no name prints)."""
    from .._maths_functions import GROUP_ORDER, TABLE

    lines = ["The maths functions of numbers.take_function (plain names; the SciPy, NumPy and SymPy names work too):"]
    for group in GROUP_ORDER:
        names = []
        for entry in TABLE:
            if entry.group != group:
                continue
            options = ", ".join(f"{o}=" for o in entry.options)
            names.append(f'"{entry.plain}"' + (f" ({options})" if options else ""))
        lines.append("")
        lines.append(f"{group[0].upper()}{group[1:]}:")
        lines.extend(textwrap.wrap("; ".join(names), width=width, initial_indent="  ", subsequent_indent="  "))
    lines.append("")
    lines.append('For example:  numbers.take_function("bessel J", order=1)   or   numbers.take_function("erfinv")')
    lines.append('Inside formula text the same names work with _ for spaces: sdata.formula("bessel_j(1, x)")')
    return "\n".join(lines)


class FunctionWords:
    """take_function and work_on_bits, shared by Numbers, NumberGrid and NumberBlock (through MathsWords)."""

    # ------------------------------------------------------------------ the maths family
    @friendly
    def take_function(self, name=None, part=None, **options):
        """A maths function of every number, by its plain or SciPy name. numbers.take_function("bessel J", order=1)

        The functions of scipy.special and the NumPy functions that work number by number: "bessel J", "erfinv"
        (or "inverse error function"), "hyperbolic sine", "legendre polynomial" (degree=3), "lambert W", "zeta" ...
        numbers.take_function() with no name lists them all, group by group. The other inputs of a function are
        options with plain names (order=, degree=, a=, b= ...): a number, or numbers of the same shape. The library
        names work too ("jv", "special.erfinv", "np.sinh"), and the same names work inside formula text with _ for
        spaces (sdata.formula("bessel_j(1, x)"), table.add_column("y", "erfinv(share)")). Where a function has no
        value (erfinv of 2, a log of a negative number) the answer is empty and a note says how many; an answer too
        big to hold is inf. simplydata numbers are real numbers: a function whose answers are complex numbers
        (hankel H1, faddeeva, spherical harmonic) gives their real part, or part="imaginary", "size" or "angle".
        It changes the numbers (undo() takes it back); a grid or block keeps its shape.
        """
        from .. import _maths_functions as table

        if name is None:
            print(maths_function_list())
            return None
        if not isinstance(name, str):
            raise SimplydataError("take_function() needs the name of a function in quotes."
                                  + self._example('take_function("bessel J", order=1)'))
        entry = table.find(name)
        if entry is None:
            parts = table.several_parts(name)
            if parts:
                listed = ", ".join(f'"{p}"' for p in parts)
                raise SimplydataError(f'{name.strip()} gives {len(parts)} answers at once; take_function gives one '
                                      f"of them by its own name: {listed}."
                                      + self._example(f'take_function("{parts[0]}")'))
            run = table.run_of(name)
            if run is None:
                guesses = suggest(table.normal(name), list(table.NAMES), n=3)
                lines = [f'take_function() does not know a function called "{name}".']
                if guesses:
                    lines.append("Did you mean " + " or ".join(f'"{g}"' for g in guesses) + "?")
                lines.append("numbers.take_function() with no name lists every function.")
                raise SimplydataError("\n".join(lines))
            entry = table.BY_PLAIN[run[0]]
            print(f'{run[1]}; take_function("{entry.plain}") gives the one asked for.')
        return self._take(entry, part, options)

    def _take(self, entry, part, options):
        from .. import _maths_functions as table

        example = self._example(_example_call(entry))
        unknown = [k for k in options if k not in entry.options]
        if unknown:
            known = ", ".join(f"{o}=" for o in entry.options) or "none"
            given = ", ".join(u + "=" for u in unknown)
            raise SimplydataError(f'take_function("{entry.plain}") does not take {given}. Its options: {known}.'
                                  + example)
        missing = [k for k in entry.needed if k not in options]
        if missing:
            raise SimplydataError(f'take_function("{entry.plain}") needs {" and ".join(m + "=" for m in missing)} '
                                  f"({entry.about})." + example)
        if part is not None and not entry.complex_answer:
            raise SimplydataError(f'part= is for functions whose answers are complex numbers; the {entry.plain} gives '
                                  "real numbers, so leave it out." + example)
        if entry.complex_answer:
            part = "real" if part is None else PART_SPELLINGS.get(str(part).strip().lower(), str(part).strip().lower())
            if part not in PARTS:
                raise SimplydataError(f'part= takes "real", "imaginary", "size" or "angle", not {part!r}.'
                                      + self._example(f'take_function("{entry.plain}", part="imaginary")'))
        values = self._values
        if values.dtype.kind == "b":
            values = values.astype(float)
        shape = values.shape
        inputs, shown = [], {}
        for key in entry.inputs:
            if key == "x":
                inputs.append(values)
                continue
            value = options.get(key, entry.defaults.get(key))
            shown[key] = value
            if value is None:
                inputs.append(None)
                continue
            inputs.append(self._function_option(entry, key, value, shape))
        table.check_whole_options(entry, inputs)  # order= of expn must be whole: a plain sentence, not empty answers
        not_whole = np.zeros(shape, dtype=bool)
        if "x" in entry.whole:
            floats = values.astype(float)
            not_whole = np.isfinite(floats) & (floats != np.round(floats))
        try:
            result = np.asarray(table.work_out(entry, inputs))
        except (TypeError, ValueError) as error:
            raise SimplydataError(f'The {entry.plain} could not be worked out on these numbers ({error}).' + example) \
                from None
        if result.shape != shape:
            try:
                result = np.broadcast_to(result, shape).copy()
            except ValueError:
                raise SimplydataError(f'The {entry.plain} gave {result.size} answers for {values.size} numbers.') \
                    from None
        complex_note = ""
        if result.dtype.kind == "c":
            real, imaginary = np.real(result), np.imag(result)
            if np.all((np.abs(imaginary) <= 1e-15 * np.maximum(1.0, np.abs(real))) | np.isnan(result)) \
                    and part == "real":
                result = real
            else:
                result = {"real": real, "imaginary": imaginary, "size": np.abs(result),
                          "angle": np.angle(result)}[part]
                complex_note = (f" The answers are complex numbers; these are their {part} part"
                                f"{'s' if part != 'size' else 's (sizes)'}"
                                + ('; part="imaginary", "size" or "angle" gives another.' if part == "real" else "."))
        filled = ~np.isnan(values.astype(float)) if values.dtype.kind in "fc" else np.ones(shape, dtype=bool)
        if result.dtype.kind == "f":
            note_empty(int(np.count_nonzero(np.isnan(result) & filled & not_whole)),
                       f"the {entry.plain} takes whole numbers only")
            empty = int(np.count_nonzero(np.isnan(result) & filled & ~not_whole))
            if empty:
                where = f"has a value only for numbers {entry.domain}" if entry.domain else \
                    "has no value there (outside where it is defined)"
                note_empty(empty, f"the {entry.plain} {where}")
            endless = int(np.count_nonzero(np.isinf(result) & filled))
            if endless:
                print(f"Note: {amount(endless, 'answer')} {'is' if endless == 1 else 'are'} infinite (inf): the "
                      f"{entry.plain} has no finite value there, or it is too big to hold.")
        library = "SciPy" if entry.namespace == "special" else "NumPy"
        settings = "".join(f", {k}={_shown(v)}" for k, v in shown.items())
        print(f"The {entry.plain} of every number{settings}: {entry.about}. {library}: "
              f"{entry.library_call(self._name, shown)}.{complex_note}")
        return self._change(f"take {entry.plain}", result)

    def _function_option(self, entry, key, value, shape):
        """One option of take_function: a number, or numbers that line up with these."""
        from ._base import is_number

        example = self._example(_example_call(entry))
        if isinstance(value, bool) or isinstance(value, str):
            raise SimplydataError(f"{key}= needs a number (or numbers) for the {entry.plain}." + example)
        if is_number(value):
            return np.asarray(value, dtype=float)
        array = np.asarray(value._values if isinstance(value, BaseNumbers) else
                           to_array(value, f'take_function("{entry.plain}", {key}=...)', example.strip()),
                           dtype=float)
        try:
            np.broadcast_shapes(array.shape, shape)
        except ValueError:
            raise SimplydataError(f"{key}= has {array.size} numbers, which do not line up with the "
                                  f"{amount(int(np.prod(shape)))} here: give one number, or one for each number."
                                  + example) from None
        return array

    # ------------------------------------------------------------------ bits (G10)
    @friendly
    def work_on_bits(self: _Same, how=None, with_numbers=None, by=None) -> _Same:
        """The bits of whole numbers, as NumPy's bit words do. numbers.work_on_bits("and", with_numbers=6)

        how= "and", "or", "only one" (xor), "flip" (not), "count ones", "shift left" (by=2), "shift right" (by=2),
        "pack into bytes" or "unpack bytes"; NumPy's names work too ("bitwise_and", "left_shift", "packbits").
        with_numbers= the other whole numbers for "and", "or" and "only one" (one number, or one for each). Whole
        numbers only: an empty number or a decimal stops with a plain sentence. "pack into bytes" packs each run of
        8 values of 1 or 0 (along the last direction of a grid or block) into one number from 0 to 255, padded with
        0 at the end; "unpack bytes" does the opposite. It changes the numbers (undo() takes it back).
        """
        key = str(how).strip().lower() if isinstance(how, str) else None
        key = BITS_SPELLINGS.get(key, key)
        if key not in BITS:
            if how is None:
                raise SimplydataError('work_on_bits() needs how=, such as "and", "or", "only one", "flip", '
                                      '"count ones", "shift left", "shift right", "pack into bytes" or "unpack bytes".'
                                      + self._example('work_on_bits("and", with_numbers=6)'))
            from .._errors import choice_error

            raise choice_error("work_on_bits", "how", how, list(BITS))
        function_name, about, needs = BITS[key]
        values = self._whole_values("work_on_bits", key)
        if needs == "with_numbers":
            if with_numbers is None:
                raise SimplydataError(f'work_on_bits("{key}") needs with_numbers=, the other whole numbers.'
                                      + self._example(f'work_on_bits("{key}", with_numbers=6)'))
            if by is not None:
                raise SimplydataError(f'by= is for "shift left" and "shift right"; "{key}" takes with_numbers=.')
            other = self._whole_other(with_numbers, "with_numbers", key)
            result = getattr(np, function_name)(values, other)
            call = f"np.{function_name}({self._name}, {_shown(with_numbers)})"
        elif needs == "by":
            if by is None:
                raise SimplydataError(f'work_on_bits("{key}") needs by=, how many places to move the bits.'
                                      + self._example(f'work_on_bits("{key}", by=2)'))
            if with_numbers is not None:
                raise SimplydataError(f'with_numbers= is for "and", "or" and "only one"; "{key}" takes by=.')
            places = self._whole_other(by, "by", key)
            if np.any(places < 0) or np.any(places >= 64):
                raise SimplydataError("by= needs a whole number of places from 0 to 63.")
            result = getattr(np, function_name)(values, places)
            call = f"np.{function_name}({self._name}, {_shown(by)})"
        else:
            if with_numbers is not None or by is not None:
                raise SimplydataError(f'work_on_bits("{key}") takes no other numbers; leave out with_numbers= and by=.')
            if function_name in ("packbits", "unpackbits"):
                result, call = self._pack(function_name, values, key)
            else:
                result = getattr(np, function_name)(values)
                call = f"np.{function_name}({self._name})"
        print(f'Bits ({key}): {about}. NumPy: {call}')
        return self._change(f"work on bits ({key})", np.asarray(result).astype(np.int64))

    def _whole_values(self, step, key):
        values = self._values
        if values.dtype.kind == "b":
            return values.astype(np.int64)
        if values.dtype.kind == "u" and values.size and values.max() >= 2 ** 63:
            _fits_in_64_bits(values.astype(float), f'{step}("{key}")')
        if values.dtype.kind in "iu":
            return values.astype(np.int64)
        floats = values.astype(float)
        if np.isnan(floats).any():
            empty = int(np.isnan(floats).sum())
            raise SimplydataError(f'{step}("{key}") needs whole numbers, and {empty} of these are empty. Fill or '
                                  f"remove them first: {self._name}.fill_empty_numbers(with_value=0)")
        if not np.all(floats == np.round(floats)):
            raise SimplydataError(f'{step}("{key}") needs whole numbers; some of these have decimals. Round them '
                                  f"first: {self._name}.round_to(0)")
        _fits_in_64_bits(floats, f'{step}("{key}")')
        return floats.astype(np.int64)

    def _whole_other(self, value, option, key):
        from ._base import is_number

        if isinstance(value, (bool, str)):
            raise SimplydataError(f"{option}= needs whole numbers.")
        array = np.asarray(value if is_number(value) else
                           (value._values if isinstance(value, BaseNumbers) else
                            to_array(value, f"work_on_bits({option}=...)", f'work_on_bits("{key}", {option}=6)')))
        floats = array.astype(float)
        if np.isnan(floats).any() or not np.all(floats == np.round(floats)):
            raise SimplydataError(f"{option}= needs whole numbers (no decimals, none empty).")
        if array.dtype.kind not in "iu":
            _fits_in_64_bits(floats, f"{option}=")
        try:
            np.broadcast_shapes(array.shape, self._values.shape)
        except ValueError:
            raise SimplydataError(f"{option}= has {array.size} numbers, which do not line up with these: give one "
                                  "number, or one for each number.") from None
        return floats.astype(np.int64)

    def _pack(self, function_name, values, key):
        if getattr(self, "_is_simplydata_block", False):
            raise SimplydataError(f'work_on_bits("{key}") changes how many numbers there are along a direction, '
                                  "which a block's labels cannot follow. Hand the block to NumPy: "
                                  f"np.{function_name}(block.as_numpy().astype(np.uint8), axis=-1)")
        if function_name == "packbits":
            if np.any((values != 0) & (values != 1)):
                raise SimplydataError('work_on_bits("pack into bytes") needs yes or no values, or numbers that are '
                                      "1 or 0.")
            packed = np.packbits(values.astype(np.uint8), axis=-1)
        else:
            if np.any((values < 0) | (values > 255)):
                raise SimplydataError('work_on_bits("unpack bytes") needs whole numbers from 0 to 255 (bytes).')
            packed = np.unpackbits(values.astype(np.uint8), axis=-1)
        if packed.ndim != values.ndim:  # pragma: no cover - axis=-1 keeps the number of directions
            raise SimplydataError(f'work_on_bits("{key}") would change how many directions the numbers have.')
        axis = "" if values.ndim == 1 else ", axis=-1"
        return packed, f"np.{function_name}({self._name}.astype(np.uint8){axis})"


def _fits_in_64_bits(floats, what: str) -> None:
    """Bit words work on 64-bit whole numbers: a number from 2**63 on (or below -2**63) would wrap round silently."""
    if np.any(np.abs(floats) >= 2.0 ** 63) and not np.all(floats[np.abs(floats) >= 2.0 ** 63] == -2.0 ** 63):
        raise SimplydataError(f"{what} works on whole numbers that fit in 64 bits (from -2**63 to 2**63 - 1); some of "
                              "these are bigger, and NumPy would wrap them round to wrong numbers.")


def _example_call(entry) -> str:
    options = "".join(f", {k}={entry.sample[k]!r}" for k in entry.needed if entry.sample.get(k) is not None)
    if any(entry.sample.get(k) is None for k in entry.needed):
        options += "".join(f", {k}=..." for k in entry.needed if entry.sample.get(k) is None)
    return f'take_function("{entry.plain}"{options})'
