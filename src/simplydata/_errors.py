"""Friendly error messages.

simplydata never shows a beginner a confusing library error if it can help it.
Every message says what went wrong, guesses what was meant, and shows what is available.
"""

from __future__ import annotations

import difflib
import functools
import inspect
import re
import threading
from typing import Any, Callable, TypeVar, overload

ISSUES_URL = "https://github.com/bioforkgithub/simplydata/issues"

# Words people may type in either spelling. Left side is accepted, right side is used.
SPELLINGS = {
    "color": "colour",
    "colors": "colours",
    "gray": "grey",
    "labeled": "labelled",
}
# Words people may type in either spelling at the start of an option name (neighbors_alike_in_order_of=)
FIRST_WORD_SPELLINGS = {
    "neighbors": "neighbours",
}


class SimplydataError(Exception):
    """A problem explained in plain English."""


class MissingWordError(SimplydataError, AttributeError):
    """Raised when someone asks for a step simplydata does not have.

    It is also an AttributeError so that Python tools such as hasattr() keep working.
    """


def suggest(word: str, options, n: int = 3, cutoff: float = 0.6) -> list[str]:
    """Return the closest matches to `word` among `options`."""
    return difflib.get_close_matches(str(word), [str(o) for o in options], n=n, cutoff=cutoff)


def column_error(name, columns) -> SimplydataError:
    cols = [str(c) for c in columns]
    lines = [f'Column "{name}" not found.']
    guess = suggest(name, cols, n=1)
    if guess:
        lines.append(f'Did you mean "{guess[0]}"?')
    if cols:
        lines.append("Columns you have: " + ", ".join(cols))
    else:
        lines.append("There are no columns yet. Start from a table with data, for example "
                     'sdata.table("your_file.xlsx") or sdata.chart("your_file.xlsx").')
    return SimplydataError("\n".join(lines))


def missing_word_error(word: str, known) -> MissingWordError:
    lines = [f"simplydata has no step called .{word}()."]
    guesses = suggest(word, known)
    if guesses:
        lines.append("Did you mean " + " or ".join(f".{g}()" for g in guesses) + "?")
    lines.append("Type sdata.show_all_words() to see every step.")
    lines.append(f"Missing something? Ask for it at {ISSUES_URL}")
    return MissingWordError("\n".join(lines))


# ---------------------------------------------------------------- other names
# Names from other tools and everyday maths (minimize, curve_fit, groupby, hist ...) never run:
# they point to the simplydata word. The list is in _other_names.py.
_PREFIXES = ("sdata", "table", "chart", "nums", "grid", "block", "dist")
_TARGET = re.compile(r"(?:sdata|table|chart|numbers|nums|grid|block|distribution|dist)\.(\w+)\(")


def other_name_target(written: str) -> str:
    """The word a pointer names: "sdata.find_where_smallest(...)" -> "find_where_smallest"."""
    found = _TARGET.search(written)
    return found.group(1) if found else written


def other_name_pointer(kind: str, name: str, known=None, prefix: str | None = None) -> str | None:
    """The line "In simplydata this is table.join_with(...)." for an other name, or None.

    kind is "sdata", "table", "chart" or "numbers". With known= (the words of the object) and
    prefix= (how the object is written, such as "grid"), a pointer to a word the object lacks
    is not given, and "numbers." is written as the prefix.
    """
    from ._other_names import OTHER_NAMES

    written = OTHER_NAMES.get(kind, {}).get(str(name))
    if written is None:
        return None
    if known is not None:
        own = f"{kind}."
        if written.startswith(own) and other_name_target(written) not in known:
            return None
        if prefix and written.startswith(own):
            written = prefix + "." + written[len(own):]
    return f"In simplydata this is {written}."


def other_name_error(kind: str, name: str, known=None, prefix: str | None = None) -> MissingWordError | None:
    """A friendly error for a name from another tool (it never runs), or None if it is not one."""
    pointer = other_name_pointer(kind, name, known, prefix)
    if pointer is None:
        return None
    shown = f"word called sdata.{name}()" if kind == "sdata" else f"step called .{name}()"
    word = other_name_target(pointer)
    return MissingWordError(f"simplydata has no {shown}.\n{pointer}\n"
                            f'Type sdata.help("{word}") to learn more.')


def missing_sdata_word(name: str, known) -> MissingWordError:
    """sdata.<name> for a name simplydata does not have: a pointer, or did-you-mean."""
    error = other_name_error("sdata", name)
    if error is not None:
        return error
    lines = [f"simplydata has no word called sdata.{name}."]
    guesses = suggest(name, [k for k in known if not k[0].isupper() and not k.startswith("_")])
    if guesses:
        lines.append("Did you mean " + " or ".join(f"sdata.{g}()" for g in guesses) + "?")
    lines.append("Type sdata.show_all_words() to see every word.")
    lines.append(f"Missing something? Ask for it at {ISSUES_URL}")
    return MissingWordError("\n".join(lines))


def option_error(step: str, option: str, known) -> SimplydataError:
    lines = [f".{step}() has no option called {option}=."]
    guesses = suggest(option, known)
    if guesses:
        lines.append("Did you mean " + " or ".join(f"{g}=" for g in guesses) + "?")
    if known:
        lines.append(f"Options for .{step}(): " + ", ".join(f"{k}=" for k in known))
    return SimplydataError("\n".join(lines))


def choice_error(step: str, option: str, value, choices) -> SimplydataError:
    lines = [f'.{step}() does not know {option}="{value}".']
    guesses = suggest(value, choices, n=1)
    if guesses:
        lines.append(f'Did you mean {option}="{guesses[0]}"?')
    lines.append("You can use: " + ", ".join(f'"{c}"' for c in choices))
    return SimplydataError("\n".join(lines))


# ---------------------------------------------------------------- old names
# When a word or option gets a better name, the old one keeps working for one release.
# The first time it is used in a session, one gentle line says what it is called now.
_NOTED: set = set()


def _quoted(name: str) -> str:
    return name if '"' in name else f'"{name}"'


def renamed_note(old: str, new: str) -> None:
    """Print, once per session, that an old word or option now has a new name.

    The note is remembered for the pair (old, new): the same old name can stand for different new
    words on different objects (table.chart is start_chart, dist.chart is draw_chart), and each
    of them gets its own note.
    """
    if (old, new) in _NOTED:
        return
    _NOTED.add((old, new))
    print(f"Note: {_quoted(old)} is now called {_quoted(new)}. "
          "The old name will stop working in a later version.")


def old_word(obj, name: str, old_words: dict):
    """The word an old name now stands for (after the note), or None if it is not an old name.

    old_words maps an old name to the new name, or to (new name to show, attribute to use)
    when the old word behaves a little differently from the new one.
    """
    new = old_words.get(name)
    if new is None:
        return None
    shown, attribute = new if isinstance(new, tuple) else (new, new)
    renamed_note(name, shown)
    return getattr(obj, attribute)


_CHART_WORDS_NOW = None


def public_words(text: str) -> str:
    """A message with the chart words as they are written now: chart steps keep short inner names
    (bars, title_top ...), so ".bars(" in a message becomes ".draw_bars(". Old names that are still
    words of their own are left alone."""
    global _CHART_WORDS_NOW
    if _CHART_WORDS_NOW is None:
        from ._core import BaseChart

        words = set(BaseChart._word_names())
        from .chart import Chart

        words |= set(Chart._word_names())
        found = {old: new for old, new in Chart._OLD_WORDS.items()
                 if isinstance(new, str) and old not in words and new in words}
        pattern = re.compile(r"(?<![\w])(\.|chart\.|page\.)(%s)\(" % "|".join(sorted(found, key=len, reverse=True)))
        _CHART_WORDS_NOW = (pattern, found)
    pattern, found = _CHART_WORDS_NOW
    return pattern.sub(lambda m: f"{m.group(1)}{found[m.group(2)]}(", text)


def other_option_note(other: str, own: str) -> None:
    """Print, once per session, that an option name from another tool is written another way here."""
    key = f"other {other}={own}="
    if key in _NOTED:
        return
    _NOTED.add(key)
    print(f"Note: {other}= is {own}= in simplydata.")


def other_value_note(option: str, other, own) -> None:
    """Print, once per session, that a value from another tool is written another way here."""
    key = f"other {option}={other!r}"
    if key in _NOTED:
        return
    _NOTED.add(key)
    print(f'Note: {option}="{other}" is {option}="{own}" in simplydata.')


_LEAVE_OUT = object()  # in a value map of renamed=: the old value means "leave the new option out"


def _value_text(value) -> str:
    return f'"{value}"' if isinstance(value, str) else repr(value)


def _renamed_value(old: str, new: tuple, value):
    """The new option and its value for an old switch, with the note once: renamed={"bayesian":
    ("test_method", {True: "bayesian", False: None})} turns bayesian=True into test_method="bayesian". An old
    value that maps to None leaves the new option out (its default), so bayesian=False changes nothing."""
    name, values = new
    # the old values are switches: True or False (NumPy's too), nothing else
    value_key = bool(value) if type(value).__name__ in ("bool", "bool_") else None
    if value_key not in values:
        shown = " or ".join(f"{old}={_value_text(v)}" for v in values)
        raise SimplydataError(f"{old}= is now {name}= (it takes {shown}); it got {old}={value!r}.\n"
                              + "".join(f"Write {name}={_value_text(n)} for {old}={_value_text(o)}. "
                                        for o, n in values.items() if n is not None).rstrip())
    now = values[value_key]
    if now is None:
        return name, _LEAVE_OUT
    renamed_note(f"{old}={_value_text(value_key)}", f"{name}={_value_text(now)}")
    return name, now


# Chart words whose colour= can be a column, so one colour per group (2026-11-23, new-user study): on them
# for_each_group_in= means the same as colour= a column, as on draw_qq_dots and the table words. Words whose
# colour= is only one colour (draw_line_at_x, draw_curve, fit_line ...) are not here.
GROUP_COLOUR_WORDS = frozenset({
    "draw_bars", "draw_lines", "draw_dots", "draw_area", "draw_histogram", "draw_boxes", "draw_violins",
    "draw_count_bars", "draw_all_dots", "draw_density", "draw_polar", "draw_band", "draw_cumulative_share",
    "draw_survival_curves", "draw_risk_curves", "draw_richness_curves", "draw_interaction_lines", "draw_sticks",
    "draw_trade_off_curve", "draw_all_pairs",
})
GROUP_COLOUR_WORDS = GROUP_COLOUR_WORDS | {"draw_rug_lines", "draw_lines_3d"}  # charts phase, batch 2


# Option names from pandas, seaborn, dplyr and scikit-learn that mean exactly one simplydata option, on every
# word that has that option (2026-11-23, new-user study). Used only when the word has no option of that name.
COMMON_OTHERS = {"by": "for_each_group_in", "groupby": "for_each_group_in", "group_by": "for_each_group_in",
                 "random_state": "with_seed"}


def _columns_of(thing):
    """The column names of a chart's data or a table, or None when they cannot be seen."""
    for name in ("_data", "_frame"):
        found = getattr(thing, name, None)
        if found is not None and hasattr(found, "columns"):
            return [str(c) for c in found.columns]
    return [str(c) for c in thing.columns] if hasattr(thing, "columns") else None


def _group_colour(word: str, value, args, kwargs, note: bool = True) -> None:
    """Checks for for_each_group_in= on a chart word, where it means colour= a column; the note once."""
    example = f'chart.{word}(..., for_each_group_in="class")'
    names = [value] if isinstance(value, str) else list(value) if isinstance(value, (list, tuple)) else None
    if not names or not all(isinstance(n, str) for n in names):
        raise SimplydataError(f"for_each_group_in= takes a column name, for example {example}; it got {value!r}.")
    if "colour" in kwargs or "color" in kwargs:
        raise SimplydataError(f"Give for_each_group_in= or colour=, not both: on .{word}() they mean the same "
                              "(one colour for each group).")
    columns = _columns_of(args[0]) if args else None
    if columns is not None:
        missing = [n for n in names if n not in columns]
        if missing:
            raise column_error(missing[0], columns)
    key = "same for_each_group_in=colour="
    if note and key not in _NOTED:
        _NOTED.add(key)
        shown = f'"{names[0]}"' if isinstance(value, str) else repr(names)
        print(f"Note: on a chart, for_each_group_in={shown} is the same as colour={shown}: each group gets its "
              "own colour.")


_CALLS = threading.local()  # how deep inside words a call is: only the outermost word is checked by the survey guard


_Word = TypeVar("_Word", bound=Callable[..., Any])


@overload
def friendly(func: _Word, *, renamed: dict | None = None, others: dict | None = None,
             pointers: dict | None = None) -> _Word: ...


@overload
def friendly(func: None = None, *, renamed: dict | None = None,
             others: dict | None = None, pointers: dict | None = None) -> Callable[[_Word], _Word]: ...


def friendly(func=None, *, renamed: dict | None = None, others: dict | None = None, pointers: dict | None = None):
    """Decorator for every public step.

    * accepts both spellings (color/colour, gray/grey) for option names
    * turns unknown options into a friendly message with a suggestion
    * renamed={"band": "confidence_band"}: an old option name still works, with a note once
    * renamed={"bayesian": ("test_method", {True: "bayesian", False: None})}: an old switch is now one value of
      a new option; bayesian=True becomes test_method="bayesian" (with a note once) and bayesian=False is
      left out (the new option's default)
    * others={"tp": "found"}: an option name from another tool or field works too, with a pointer
      once per session ("Note: tp= is found= in simplydata."), as alternative= is translated
    * pointers={"left_on": 'using={"name": "student"}'}: an option name from another tool that has no one-to-one
      simplydata option; it never runs, it stops with "In simplydata this is ..."

    Use it as @friendly, or as @friendly(renamed={...}, others={...}).
    """
    if func is None:
        def decorate(word):
            return friendly(word, renamed=renamed, others=others, pointers=pointers)

        return decorate
    renamed = renamed or {}
    others = others or {}
    pointers = pointers or {}
    sig = inspect.signature(func)
    params = [p for p in sig.parameters if p != "self"]
    takes_any = any(p.kind is p.VAR_KEYWORD for p in sig.parameters.values())

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        fixed = {}
        for key, value in kwargs.items():
            for us, uk in SPELLINGS.items():
                if key == us or key.endswith("_" + us):
                    candidate = key[: len(key) - len(us)] + uk
                    if candidate in params:
                        key = candidate
                    break
            for us, uk in FIRST_WORD_SPELLINGS.items():
                if key.startswith(us + "_") and uk + key[len(us):] in params:
                    key = uk + key[len(us):]
            if key in ("for_each_group_in", "hue") and key not in params and func.__name__ in GROUP_COLOUR_WORDS:
                _group_colour(func.__name__, value, args, kwargs, note=key == "for_each_group_in")
                if key == "hue":
                    other_option_note("hue", "colour")  # seaborn's hue=
                key = "colour"
            elif (key in COMMON_OTHERS and key not in params and key not in renamed and key not in others
                  and COMMON_OTHERS[key] in params):
                new = COMMON_OTHERS[key]
                other_option_note(key, new)
                if new in kwargs or new in fixed:
                    raise SimplydataError(f"Give {new}= only once ({key}= is another name for it).")
                key = new
            if key in renamed and key not in params:
                new = renamed[key]
                if isinstance(new, tuple):  # the old option was a switch that is now one value of the new one
                    new, value = _renamed_value(key, new, value)
                    if value is _LEAVE_OUT:  # bayesian=False: the usual answer, the new option's default
                        renamed_note(f"{key}=", f"{new}=")
                        continue
                else:
                    renamed_note(f"{key}=", f"{new}=")
                if new in kwargs or new in fixed:
                    raise SimplydataError(f"Give {new}= only once ({key}= is its old name).")
                key = new
            elif key in others and key not in params:
                new = others[key]
                other_option_note(key, new)
                if new in kwargs or new in fixed:
                    raise SimplydataError(f"Give {new}= only once ({key}= is another name for it).")
                key = new
            if key in pointers and key not in params:
                raise SimplydataError(f".{func.__name__}() has no option called {key}= (a name from another tool).\n"
                                      f"In simplydata this is {pointers[key]}.")
            if key not in params and not takes_any:
                raise option_error(func.__name__, key, params)
            fixed[key] = value
        outer = not getattr(_CALLS, "depth", 0)
        note = ""
        if outer and args and "." in func.__qualname__:  # a table's word under a survey design (S3d-1)
            guard = getattr(type(args[0]), "_survey_guard", None)
            if guard is not None:
                guard(args[0], func.__name__)
            repeats = getattr(type(args[0]), "_repeated_rows_note", None)  # rows that repeat one person
            if repeats is not None:
                try:
                    note = repeats(args[0], func.__name__, params, args[1:], fixed)
                except Exception:  # noqa: BLE001 - a note never stops a word
                    note = ""
        _CALLS.depth = getattr(_CALLS, "depth", 0) + 1
        try:
            result = func(*args, **fixed)
            if note:
                print(note)
            return result
        except SimplydataError as exc:
            said = exc.args[0] if exc.args and isinstance(exc.args[0], str) else None
            if said is not None and "." in said:
                now = public_words(said)
                if now != said:
                    exc.args = (now, *exc.args[1:])
            raise
        finally:
            _CALLS.depth -= 1

    wrapper._renamed_options = dict(renamed)
    wrapper._other_options = dict(others)
    wrapper._option_pointers = dict(pointers)
    return wrapper
