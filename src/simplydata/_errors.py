"""Friendly error messages.

simplydata never shows a beginner a confusing library error if it can help it.
Every message says what went wrong, guesses what was meant, and shows what is available.
"""

from __future__ import annotations

import difflib
import functools
import inspect
import re

ISSUES_URL = "https://github.com/bioforkgithub/simplydata/issues"

# Words people may type in either spelling. Left side is accepted, right side is used.
SPELLINGS = {
    "color": "colour",
    "colors": "colours",
    "gray": "grey",
    "labeled": "labelled",
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
_PREFIXES = ("sdata", "table", "chart", "nums", "grid", "dist")
_TARGET = re.compile(r"(?:sdata|table|chart|nums|grid|dist)\.(\w+)\(")


def other_name_target(written: str) -> str:
    """The word a pointer names: "sdata.find_where_smallest(...)" -> "find_where_smallest"."""
    found = _TARGET.search(written)
    return found.group(1) if found else written


def other_name_pointer(kind: str, name: str, known=None, prefix: str | None = None) -> str | None:
    """The line "In simplydata this is table.join_with(...)." for an other name, or None.

    kind is "sdata", "table", "chart" or "numbers". With known= (the words of the object) and
    prefix= (how the object is written, such as "grid"), a pointer to a word the object lacks
    is not given, and "nums." is written as the prefix.
    """
    from ._other_names import OTHER_NAMES

    written = OTHER_NAMES.get(kind, {}).get(str(name))
    if written is None:
        return None
    if known is not None:
        own = f"{'nums' if kind == 'numbers' else kind}."
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
    key = f"other {other}="
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


def friendly(func=None, *, renamed: dict | None = None, others: dict | None = None):
    """Decorator for every public step.

    * accepts both spellings (color/colour, gray/grey) for option names
    * turns unknown options into a friendly message with a suggestion
    * renamed={"band": "confidence_band"}: an old option name still works, with a note once
    * others={"tp": "found"}: an option name from another tool or field works too, with a pointer
      once per session ("Note: tp= is found= in simplydata."), as alternative= is translated

    Use it as @friendly, or as @friendly(renamed={...}, others={...}).
    """
    if func is None:
        return lambda f: friendly(f, renamed=renamed, others=others)
    renamed = renamed or {}
    others = others or {}
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
            if key in renamed and key not in params:
                new = renamed[key]
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
            if key not in params and not takes_any:
                raise option_error(func.__name__, key, params)
            fixed[key] = value
        try:
            return func(*args, **fixed)
        except SimplydataError as exc:
            said = exc.args[0] if exc.args and isinstance(exc.args[0], str) else None
            if said is not None and "." in said:
                now = public_words(said)
                if now != said:
                    exc.args = (now, *exc.args[1:])
            raise

    wrapper._renamed_options = dict(renamed)
    wrapper._other_options = dict(others)
    return wrapper
