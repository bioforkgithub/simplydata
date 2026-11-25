"""sdata.show_packages_used(): which packages did the work behind your simplydata words, and how to cite them.

simplydata calls established packages (pandas, Polars, NumPy, SciPy, statsmodels, matplotlib, seaborn, R and
its packages); the people who wrote them ask to be cited. Asked for by the owner on 2026-11-20: "this should
happen for any package the user uses even for pandas or polars or scipy anything".

How a package is known to have done work:
- each public word (sdata.<word>, chart, table, numbers, grid, distribution and system words) is wrapped by
  install(): when the word finishes without an error, its key ("table.find_average_of") is remembered. A word
  that fails remembers nothing, and neither do the words it called on the way. The wrapper only adds the key to
  a set: it never changes what the word gives back or prints.
- a table word also remembers what holds the table (pandas or Polars, through narwhals).
- r_call() (simplydata/_r.py) remembers R, its packages and rpy2 after R has answered.
- only when the list is shown are the keys turned into packages: the libraries the word's UNDERNEATH entry
  imports, the libraries the word's own code imports or names, else the imports of the file it is written in.

The references come from the packages themselves (simplydata never makes one up): R's utils::citation() and
packageVersion() for R and its packages, _citations.py for Python packages (each package's own request), and
name, version and home page from the installed metadata for a package that asks for no paper.

At the end of a script (not in an interactive session or a notebook, where nobody would see it) a short list is
printed. SIMPLYDATA_NO_CITE_LIST=1 or sdata.show_packages_used(at_end=False) switches it off.
"""

from __future__ import annotations

import ast
import atexit
import functools
import importlib.metadata as metadata
import inspect
import os
import platform
import re
import sys
import textwrap
import threading
import types

from ._citations import CITATIONS, NAMES
from ._errors import SimplydataError

WIDTH = 78
OFF_VARIABLE = "SIMPLYDATA_NO_CITE_LIST"

# simplydata's own reference (the same as CITATION.cff, which a test checks)
SIMPLYDATA_DOI = "10.5281/zenodo.24210045"
SIMPLYDATA_TITLE = "simplydata: simple words for data science in Python"
SIMPLYDATA_AUTHOR = ("Victor", "Manish Prakash")
SIMPLYDATA_YEAR = "2026"

# Python packages whose work can be behind a word (the import name)
WORK_PACKAGES = ("pandas", "polars", "narwhals", "numpy", "scipy", "statsmodels", "patsy", "matplotlib", "seaborn",
                 "lifelines", "control", "pyreadstat", "docx", "openpyxl", "pyarrow", "duckdb", "plotly",
                 "sympy")
# R's own packages: they are cited as R itself (citation("stats") gives R's reference)
R_BASE = {"base", "stats", "utils", "methods", "graphics", "grDevices", "splines", "grid", "tools", "parallel",
          "stats4", "tcltk", "datasets", "compiler"}
# Words that only teach or help: simplydata's own, nothing underneath
OWN_WORDS = {"sdata.help", "sdata.show_all_words", "sdata.show_lesson", "sdata.start_30_days", "sdata.show_today",
             "sdata.show_day", "sdata.show_answers", "sdata.go_to_next_day", "sdata.show_packages_used"}
# What every word of a kind uses (tables: narwhals, and pandas or Polars, found when the word runs)
KIND_PACKAGES = {"chart": ("matplotlib",), "table": ("narwhals",), "numbers": ("numpy",), "grid": ("numpy",)}
WORD_PACKAGES = {"sdata.chart": ("matplotlib",), "sdata.table": ("narwhals",)}
# What holds a table is found when the word runs, never from the code (a word's code names both)
HOLDERS = ("pandas", "polars")

_USED_WORDS: dict[tuple, None] = {}  # (word key, the options given), in the order first used
_USED_PYTHON: dict[str, None] = {}  # Python packages found while a word ran (a table's pandas or Polars, rpy2)
_USED_R: dict[str, None] = {}  # R packages ("R" for R itself)
_SETTINGS = {"at_end": True}
_LOCAL = threading.local()
_LOCK = threading.Lock()


# ---------------------------------------------------------------- recording
def _frames() -> list:
    frames = getattr(_LOCAL, "frames", None)
    if frames is None:
        frames = _LOCAL.frames = []
    return frames


def outermost_word() -> str | None:
    """The word the user called (the outermost word running), as "draw_bars", or None: chart.undo() names it."""
    keys = getattr(_LOCAL, "keys", None)
    return keys[0].rsplit(".", 1)[-1] if keys else None


def _commit(found: list) -> None:
    with _LOCK:
        for kind, name in found:
            {"word": _USED_WORDS, "python": _USED_PYTHON, "r": _USED_R}[kind].setdefault(name, None)


def _note(items) -> None:
    """Remember what did work: kept with the word that is running (and dropped if it fails), else at once."""
    frames = _frames()
    if frames:
        frames[-1].extend(items)
    else:
        _commit(list(items))


def record_r(packages=(), code: str = "") -> None:
    """Called by r_call() after R answered: R itself, the packages it loaded and the pkg:: names in the code."""
    named = list(packages) + re.findall(r"\b([A-Za-z][A-Za-z0-9.]*)::", code)
    items = [("r", "R"), ("python", "rpy2")]
    items += [("r", "R" if p in R_BASE else p) for p in dict.fromkeys(named)]
    _note(items)


def _table_holder(value) -> str | None:
    """pandas or polars: what holds a simplydata table (or the pandas or Polars table a word gave back)."""
    try:
        frame = getattr(value, "__dict__", {}).get("_frame")
        native = value if frame is None else frame.to_native()
        name = type(native).__module__.split(".")[0]
    except Exception:  # noqa: BLE001 - never let the record change a word
        return None
    return name if name in HOLDERS else None


def _wrap(func, key: str):
    """The word, remembering its key once it has finished without an error."""
    table_word = key.startswith("table.") or key == "sdata.table"

    @functools.wraps(func)
    def word(*args, **kwargs):
        frames = _frames()
        frames.append([])
        keys = getattr(_LOCAL, "keys", None)
        if keys is None:
            keys = _LOCAL.keys = []
        keys.append(key)
        try:
            result = func(*args, **kwargs)
        except BaseException:
            frames.pop()
            raise
        finally:
            keys.pop()
        found = frames.pop()
        found.append(("word", (key, tuple(sorted(k for k, v in kwargs.items() if v is not None)))))
        if table_word:
            for value in (args[0] if args else None, result):
                holder = _table_holder(value)
                if holder:
                    found.append(("python", holder))
        if frames:
            frames[-1].extend(found)
        else:
            _commit(found)
        return result

    word._simplydata_word = func
    return word


def install(namespace: dict) -> None:
    """Wrap every public word: the sdata functions in namespace (simplydata's own) and the words of every
    object with steps. A word with two spellings keeps one wrapper, so both spellings stay the same word."""
    from . import learn

    for name in namespace["__all__"]:
        value = namespace.get(name)
        key = f"sdata.{name}"
        if isinstance(value, types.FunctionType) and key not in OWN_WORDS:
            word = _wrap(getattr(value, "_simplydata_word", value), key)
            # pickle finds a function by its module and name: sdata.make_wave, not simplydata._waves.make_wave
            word.__module__, word.__qualname__ = namespace["__name__"], name
            namespace[name] = word
    for cls, kind in learn._classes():
        prefix = "" if kind == "chart" else learn._PREFIX[kind] + "."
        made: dict = {}
        for name in cls._word_names():
            raw = inspect.getattr_static(cls, name)
            if not isinstance(raw, types.FunctionType):
                continue
            func = getattr(raw, "_simplydata_word", raw)
            if id(func) not in made:
                word = made[id(func)] = _wrap(func, prefix + func.__name__)
                # pickle finds Chart.draw_bars on Chart, where the wrapper now is
                canonical = func.__name__ if func.__name__ in cls._word_names() else name
                word.__module__, word.__qualname__ = cls.__module__, f"{cls.__qualname__}.{canonical}"
            setattr(cls, name, made[id(func)])


# ---------------------------------------------------------------- from words to packages
def _top(name: str) -> str:
    return name.split(".")[0]


def _imports_in(tree) -> dict[str, str]:
    """{name as written in the code: package} for every import in a piece of code."""
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found[alias.asname or _top(alias.name)] = _top(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            for alias in node.names:
                found[alias.asname or alias.name] = _top(node.module)
    return found


@functools.lru_cache(maxsize=None)
def _module_imports(module_name: str) -> dict[str, str]:
    module = sys.modules.get(module_name)
    try:
        return _imports_in(ast.parse(inspect.getsource(module)))
    except (OSError, TypeError, SyntaxError):
        return {}


@functools.lru_cache(maxsize=None)
def _code_of(func):
    """(the packages a function's own code imports or names, the simplydata functions it calls by name, the
    names it calls on self)."""
    try:
        tree = ast.parse(textwrap.dedent(inspect.getsource(func)))
    except (OSError, TypeError, SyntaxError):
        return frozenset(), (), ()
    found = set(_imports_in(tree).values())
    module = sys.modules.get(func.__module__)
    top = _module_imports(func.__module__)
    helpers, on_self = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if node.id in top:
                found.add(top[node.id])
            value = getattr(module, node.id, None)
            if isinstance(value, types.FunctionType) and value.__module__.startswith("simplydata"):
                helpers.append(value)
        elif (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self"):
            on_self.append(node.attr)
    return frozenset(found & set(WORK_PACKAGES)), tuple(helpers), tuple(on_self)


def _function_packages(func, owner=None, depth: int = 3, seen=None) -> set[str]:
    """The packages a word's code imports or names, and those of the simplydata helpers it calls (by name, or on
    self when owner, the class, is known), three calls deep."""
    seen = set() if seen is None else seen
    func = getattr(func, "_simplydata_word", func)
    if id(func) in seen:
        return set()
    seen.add(id(func))
    found, helpers, on_self = _code_of(func)
    found = set(found)
    if depth:
        for helper in helpers:
            found |= _function_packages(helper, owner, depth - 1, seen)
        for name in on_self if owner is not None else ():
            value = inspect.getattr_static(owner, name, None)
            if isinstance(value, (staticmethod, classmethod)):
                value = value.__func__
            if isinstance(value, types.FunctionType):
                found |= _function_packages(value, owner, depth - 1, seen)
    return found


def _underneath_packages(key: str, options=()) -> tuple[set[str], bool]:
    """The Python packages the word's UNDERNEATH entry imports, with the entries of the options given
    ("table.explain weights=" when weights= was given), and whether the word has an entry of its own (some words
    only have entries for options)."""
    from ._underneath import UNDERNEATH

    entries = [e for e in UNDERNEATH.values() if e.word == key]
    found = set()
    for entry in entries:
        given = re.match(r"\s*(\w+)\s*=", entry.option) if entry.option else None
        if entry.option and (given is None or given.group(1) not in options):
            continue
        for _library, language, source in entry.blocks():
            if language == "python":
                try:
                    found |= set(_imports_in(ast.parse(source)).values())
                except SyntaxError:
                    pass
    return found & set(WORK_PACKAGES), any(not e.option for e in entries)


def _word_function(key: str):
    from . import learn

    try:
        func = learn._function(key)
    except AttributeError:
        return None
    return getattr(func, "_simplydata_word", func)


def _owner(key: str):
    from . import learn

    kind = learn._kind(key)
    return next((cls for cls, k in learn._classes() if k == kind), None)


@functools.lru_cache(maxsize=None)
def packages_of_word(key: str, options=()) -> tuple[str, ...]:
    """The Python packages behind a word. From its UNDERNEATH entry when it has one; else from its own code and
    the simplydata helpers it calls, or the imports of the file it is written in. With the entries of the
    options given. Always with what every word of its kind uses. What holds a table (pandas or Polars) and R are
    found when the word runs, not here."""
    from . import learn

    if key in OWN_WORDS:
        return ()
    table_word = key.startswith("table.") or key == "sdata.table"
    found, own_entry = _underneath_packages(key, options)
    func = None if own_entry and found else _word_function(key)  # an entry that names no Python package (R, or nothing) falls back to the code
    if func is not None:
        code = _function_packages(func, _owner(key))
        if not code - set(HOLDERS if table_word else ()):
            code |= set(_module_imports(func.__module__).values()) & set(WORK_PACKAGES)
        found |= code
    found |= set(WORD_PACKAGES.get(key, ())) | set(KIND_PACKAGES.get(learn._kind(key), ()))
    if table_word:
        found -= set(HOLDERS)
    return tuple(p for p in WORK_PACKAGES if p in found)


# ---------------------------------------------------------------- facts about a package
def _source(distribution: str) -> str:
    """conda-forge (or conda, from another channel) when conda installed it (its record in conda-meta), else
    PyPI."""
    import json

    folder = os.path.join(sys.prefix, "conda-meta")
    if not os.path.isdir(folder):
        return "PyPI"
    record = re.compile(re.escape(distribution.lower().replace("_", "-")) + r"-\d.*\.json$")
    try:
        for name in os.listdir(folder):
            if record.match(name.lower()):
                with open(os.path.join(folder, name), encoding="utf-8") as file:
                    channel = str(json.load(file).get("channel", ""))
                return "conda-forge" if "conda-forge" in channel else "conda"
    except (OSError, ValueError):
        pass
    return "PyPI"


def _version(distribution: str, module_name: str) -> str:
    try:
        return metadata.version(distribution)
    except metadata.PackageNotFoundError:
        return str(getattr(sys.modules.get(module_name), "__version__", "") or "version unknown")


def _home_page(distribution: str) -> str:
    try:
        meta = metadata.metadata(distribution)
    except metadata.PackageNotFoundError:
        return ""
    if meta.get("Home-page"):
        return meta["Home-page"]
    urls = meta.get_all("Project-URL") or []
    for wanted in ("homepage", "home", "source", "repository", "documentation"):
        for item in urls:
            label, _, url = item.partition(",")
            if label.strip().lower() == wanted:
                return url.strip()
    return urls[0].partition(",")[2].strip() if urls else ""


def _author_year(one_line: str) -> str:
    """'McKinney (2010), Proc. ...' -> 'McKinney 2010'; 'Vink et al., pola-rs ...' -> 'Vink et al.'."""
    m = re.match(r"(.+?) \((\d{4})\)", one_line)
    return f"{m.group(1)} {m.group(2)}" if m else one_line.split(",")[0]


def _python_facts(module_name: str) -> dict:
    if module_name in CITATIONS:
        shown, dist, one_line, text, bibtex = CITATIONS[module_name]
    else:
        shown, dist = NAMES.get(module_name, (module_name, module_name))
        home = _home_page(dist)
        one_line = text = f"{shown}, {home}" if home else shown
        bibtex = ""
    version = _version(dist, module_name)
    if not bibtex:
        home = _home_page(dist)
        key = re.sub(r"[^A-Za-z0-9-]", "", shown)
        bibtex = "@misc{%s,\n  title = {%s},\n  note = {Python package version %s}%s\n}" % (
            key, shown, version, ",\n  howpublished = {\\url{" + home + "}}" if home else "")
    return dict(name=shown, version=version, language="Python", source=_source(dist), one_line=one_line,
                text=text, bibtex=bibtex, cite=_author_year(one_line) if module_name in CITATIONS else "")


def _simplydata_facts() -> dict:
    from . import __version__

    family, given = SIMPLYDATA_AUTHOR
    initials = " ".join(part[0] + "." for part in given.split())
    text = (f"{family}, {initials} ({SIMPLYDATA_YEAR}). {SIMPLYDATA_TITLE} (version {__version__}). Zenodo. "
            f"doi:{SIMPLYDATA_DOI}.")
    bibtex = ("@software{simplydata,\n"
              f"  author = {{{family}, {given}}},\n"
              f"  title = {{{SIMPLYDATA_TITLE}}},\n"
              f"  version = {{{__version__}}},\n"
              f"  year = {{{SIMPLYDATA_YEAR}}},\n"
              "  publisher = {Zenodo},\n"
              f"  doi = {{{SIMPLYDATA_DOI}}},\n"
              f"  url = {{https://doi.org/{SIMPLYDATA_DOI}}}\n}}")
    return dict(name="simplydata", version=__version__, language="Python", source=_source("simplydata"),
                one_line=f"{family} ({SIMPLYDATA_YEAR}), doi:{SIMPLYDATA_DOI}", text=text, bibtex=bibtex,
                cite=f"{family} {SIMPLYDATA_YEAR}")


_R_FACTS: dict[str, dict] = {}


def _r_facts(packages: list[str]) -> dict[str, dict]:
    """version, source and references of R and its packages, from R itself (asked once per package)."""
    wanted = [p for p in packages if p not in _R_FACTS]
    if wanted:
        from ._r import r_package_facts

        from ._r import _LOCK as r_lock

        if r_lock.acquire(timeout=10):  # R busy in another thread for that long (at exit): no references
            try:
                _R_FACTS.update(r_package_facts(["base" if p == "R" else p for p in wanted]))
            except Exception:  # noqa: BLE001 - R has gone (or never came): name the package, without a reference
                pass
            finally:
                r_lock.release()
        if "base" in _R_FACTS:
            _R_FACTS["R"] = dict(_R_FACTS.pop("base"), name="R", source="CRAN")
    out = {}
    for p in packages:
        how = "type citation() in R" if p == "R" else f'type citation("{p}") in R'
        out[p] = _R_FACTS.get(p) or dict(name=p, version="version unknown", language="R", source="CRAN",
                                         one_line=how, text=how, bibtex="", cite=p)
    return out


def packages_used() -> list[dict]:
    """The facts of every package used so far: simplydata first, then Python packages, R, then R packages."""
    with _LOCK:
        words, python, r = list(_USED_WORDS), list(_USED_PYTHON), list(_USED_R)
    names: dict[str, None] = {}
    for key, options in words:
        for package in packages_of_word(key, options):
            names.setdefault(package, None)
    for package in python:
        names.setdefault(package, None)
    facts = [_simplydata_facts()] + [_python_facts(p) for p in names]
    if r:
        ordered = (["R"] if "R" in r else []) + [p for p in r if p != "R"]
        facts += list(_r_facts(ordered).values())
    return facts


def _main_packages() -> set[str]:
    """Top-level packages your own script or notebook has imported (the modules and objects in __main__)."""
    main = sys.modules.get("__main__")
    found = set()
    for value in list(getattr(main, "__dict__", {}).values()):
        if isinstance(value, types.ModuleType):
            found.add(_top(value.__name__))
        else:
            module = getattr(value, "__module__", None)
            if isinstance(module, str):
                found.add(_top(module))
    return found


BEFORE_SIMPLYDATA: set[str] = set()  # top-level packages loaded before simplydata (filled by __init__)


def loaded_yourself(used: list[dict]) -> list[dict]:
    """Packages with a known reference that you imported yourself but no simplydata word used."""
    used_names = {f["name"] for f in used}
    yours = (_main_packages() | BEFORE_SIMPLYDATA) & set(sys.modules)
    return [_python_facts(p) for p in CITATIONS if p in yours and CITATIONS[p][0] not in used_names]


# ---------------------------------------------------------------- printing
def _row(f: dict) -> str:
    return f"{f['name']} {f['version']} ({f['language']}, {f['source']})"


def _named(f: dict) -> str:
    return f"{f['name']} {f['version']}" + (f" ({f['cite']})" if f["cite"] else "")


def methods_sentence(facts: list[dict]) -> str:
    python = [f for f in facts if f["language"] == "Python" and f["name"] != "simplydata"]
    r = [f for f in facts if f["language"] == "R"]
    parts = [f"Data were analysed in Python {platform.python_version()} with simplydata {facts[0]['version']} "
             f"({facts[0]['cite']})"]
    if python:
        listed = [_named(f) for f in python]
        parts.append(", which used " + _and(listed))
    sentence = "".join(parts)
    if r:
        base = next((f for f in r if f["name"] == "R"), None)
        others = [_named(f) for f in r if f["name"] != "R"]
        tail = _named(base) if base else "R"
        if others:
            tail += " with the packages " + _and(others)
        sentence += "; " + ("and " if python else "") + tail
    return sentence + "."


def _and(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def short_list(facts: list[dict]) -> str:
    rows = [(f["name"], f["version"], f["language"], f["source"], f["one_line"]) for f in facts]
    widths = [max(len(r[i]) for r in rows) for i in range(4)]
    lines = ["Packages simplydata used in this script. Their authors ask you to cite them too:"]
    for r in rows:
        lines.append("  " + "  ".join(r[i].ljust(widths[i]) for i in range(4)) + "  " + r[4])
    lines.append("The full references and a sentence for your methods: sdata.show_packages_used(). "
                 f"This list off: sdata.show_packages_used(at_end=False) or {OFF_VARIABLE}=1.")
    return "\n".join(lines)


def _indent(text: str, indent: str = "    ") -> str:
    return textwrap.fill(" ".join(text.split()), WIDTH, initial_indent=indent, subsequent_indent=indent)


def full_text(facts: list[dict], yours: list[dict]) -> str:
    title = "Packages that did the work behind your simplydata words"
    lines = [title, "=" * len(title)]
    if len(facts) == 1:
        lines.append("No simplydata word has used another package yet in this session.")
    lines.append("Please cite them as their authors ask:")
    lines.append("")
    for f in facts:
        lines.append(_row(f))
        lines.append(_indent(f["text"]))
    lines += ["", "A sentence for your methods:", _indent(methods_sentence(facts))]
    if yours:
        lines += ["", "You also loaded these yourself (cite them if you used them):"]
        for f in yours:
            lines.append("  " + _row(f))
            lines.append(_indent(f["text"], "      "))
    lines += ["", 'As BibTeX for your reference manager: sdata.show_packages_used(save_as="references.bib")']
    return "\n".join(lines)


def _bibtex_with_keys(f: dict) -> str:
    """R's toBibtex() often leaves the key empty ("@Manual{,"): give each entry one, R-vegan, R-vegan-2 ..."""
    count = [0]
    base = "R" if f["name"] == "R" else f"R-{f['name']}"

    def key(m):
        count[0] += 1
        if m.group(2).strip():
            return m.group(0)
        return f"{m.group(1)}{{{base if count[0] == 1 else f'{base}-{count[0]}'},"

    if f["language"] != "R":
        return f["bibtex"]
    return re.sub(r"(@\w+)\{([^,\n]*),", key, f["bibtex"])


def bibtex(facts: list[dict]) -> str:
    entries = [_bibtex_with_keys(f).strip() for f in facts if f["bibtex"].strip()]
    return "\n\n".join(entries) + "\n"


def _say(text: str) -> None:
    """print(), but a character the console cannot show (a name with an accent on a Windows console) becomes ?
    instead of an error."""
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "ascii"
        print(text.encode(encoding, errors="replace").decode(encoding, errors="replace"))


def show_packages_used(save_as=None, at_end=None) -> None:
    """List the packages that did the work behind your simplydata words, and how to cite them.
    sdata.show_packages_used()

    simplydata calls established packages (pandas, Polars, NumPy, SciPy, statsmodels, matplotlib, seaborn, and R
    with its packages); their authors ask to be cited. This prints each one with its version, language, where it
    comes from (PyPI, conda-forge, CRAN, Bioconductor) and its reference: R's own citation() for R packages, the
    package's own request for Python packages. Then a sentence for the methods section of a paper, and the
    packages you imported yourself (cite them if you used them). simplydata itself comes first.

    save_as= a file name, such as "references.bib", also writes the references as BibTeX.
    at_end= True or False: whether a short list is printed when your script ends (normally True; never in an
    interactive session or a notebook). The environment variable SIMPLYDATA_NO_CITE_LIST=1 switches it off too.
    """
    if save_as is not None and (not isinstance(save_as, (str, os.PathLike)) or not str(save_as).strip()):
        raise SimplydataError('save_as= is a file name, such as save_as="references.bib".')
    if at_end is not None:
        if not isinstance(at_end, bool):
            raise SimplydataError(f"at_end= is True or False, not {at_end!r}.")
        _SETTINGS["at_end"] = at_end
        if save_as is None:
            if not at_end:
                print("No list of packages at the end of the script. sdata.show_packages_used() still shows it.")
            elif _switched_off():
                print(f"The list of packages stays off at the end of the script: {OFF_VARIABLE} is set.")
            else:
                print("The list of packages used will be printed when your script ends.")
            return None
    facts = packages_used()
    _say(full_text(facts, loaded_yourself(facts)))
    if save_as is not None:
        with open(save_as, "w", encoding="utf-8") as file:
            file.write(bibtex(facts))
        print(f"Saved the references as BibTeX in {save_as}")
    return None


# ---------------------------------------------------------------- at the end of a script
def _interactive() -> bool:
    if hasattr(sys, "ps1") or sys.flags.interactive:
        return True
    if "ipykernel" in sys.modules:
        return True
    ipython = sys.modules.get("IPython")
    try:
        return ipython is not None and ipython.get_ipython() is not None
    except Exception:  # noqa: BLE001
        return False


def _switched_off() -> bool:
    return os.environ.get(OFF_VARIABLE, "").strip() not in ("", "0")


def _ended_by_an_error() -> bool:
    """The script stopped with an error: its message stays the last thing printed."""
    return getattr(sys, "last_exc", None) is not None or getattr(sys, "last_value", None) is not None


def _worker_process() -> bool:
    """A process started by multiprocessing (a Pool or joblib worker): only the main script prints the list."""
    mp = sys.modules.get("multiprocessing")
    try:
        return mp is not None and mp.parent_process() is not None
    except Exception:  # noqa: BLE001
        return False


def _at_exit() -> None:
    try:
        if (not _SETTINGS["at_end"] or _switched_off() or _interactive() or _ended_by_an_error()
                or _worker_process()):
            return
        with _LOCK:
            nothing = not (_USED_WORDS or _USED_PYTHON or _USED_R)
        if nothing:
            return
        facts = packages_used()
        if len(facts) == 1:
            return
        print()
        _say(short_list(facts))
        sys.stdout.flush()
    except Exception:  # noqa: BLE001 - the end of a script never fails because of this list
        pass


def register_at_exit() -> None:
    """(Again) ask Python to print the list at the end: called at import and once R has started, so that the
    list is printed before rpy2 shuts R down (exit steps run last-registered first)."""
    atexit.unregister(_at_exit)
    atexit.register(_at_exit)
