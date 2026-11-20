"""Privacy: simplydata never sends, uploads or logs your data, and writes files only where you ask.

simplydata is used on sensitive data (patients, surveillance, ...). These tests hold it to that, on every change:

(a) the source has no network code, except the reader of a web address the user gives (_data.py, _download);
(b) no R code that simplydata runs can reach the internet, install a package or write a file, and r_call()
    refuses such code at run time;
(c) the whole test suite runs with outgoing connections blocked (tests/conftest.py, no_network), and that guard is
    checked here to work;
(d) the list of packages used (sdata.show_packages_used() and the list at the end of a script) never holds a value,
    a column name or a group of your table;
(e) importing simplydata adds no logging handler that writes a file, and a script writes only the files it asks for.
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

import simplydata as sdata
from simplydata._r import R_NOT_ALLOWED, refuse_unsafe_r_code

PACKAGE = Path(sdata.__file__).resolve().parent
SRC = PACKAGE.parent
SOURCE_FILES = sorted(PACKAGE.rglob("*.py"))


def _name(path: Path) -> str:
    return path.relative_to(PACKAGE).as_posix()


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _with_functions(tree):
    """(node, name of the function it is in, or "<module>") for every node."""
    def walk(node, function):
        for child in ast.iter_child_nodes(node):
            inside = child.name if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) else function
            yield child, inside
            yield from walk(child, inside)

    yield from walk(tree, "<module>")


def _dotted(node) -> str:
    """"urllib.request.urlopen" for an attribute chain; "" for anything else."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return ""


# ---------------------------------------------------------------- (a) no network code
# Modules that can talk to the network (or start programs that can), and telemetry or crash-report packages
NETWORK_MODULES = {
    "urllib", "urllib3", "http", "socket", "socketserver", "ssl", "requests", "httpx", "aiohttp", "ftplib",
    "smtplib", "poplib", "imaplib", "nntplib", "telnetlib", "xmlrpc", "webbrowser", "asyncio", "subprocess", "pty",
    "pycurl", "paramiko", "websocket", "websockets", "grpc", "boto3", "botocore", "fsspec", "pooch", "sentry_sdk",
    "posthog", "mixpanel", "analytics", "segment", "rollbar", "bugsnag", "opentelemetry", "datadog", "newrelic",
}
# Calls that fetch from the web or start other programs, whatever module they come from
NETWORK_CALLS = {
    "load_dataset", "get_dataset_names", "get_rdataset", "webuse", "urlopen", "urlretrieve", "read_html",
    "system", "popen", "startfile", "spawnl", "spawnv", "execv", "execl", "execvp", "execlp", "open_connection",
    "create_connection", "check_output", "check_call", "Popen",
}
# The one place simplydata reaches the network: sdata.table("https://...") with a web address the user gives
ALLOWED_IMPORTS = {("_data.py", "<module>", "urllib.error"), ("_data.py", "<module>", "urllib.parse"),
                   ("_data.py", "<module>", "urllib.request")}
ALLOWED_USES = {  # (file, function) where urllib.<part>.<name> may be used
    "urllib.request": {("_data.py", "_download")},
    "urllib.error": {("_data.py", "_download")},
    "urllib.parse": {("_data.py", "_read_web")},
}


def _network_code(files=None, base=PACKAGE) -> list[str]:
    found = []
    for path in SOURCE_FILES if files is None else files:
        name = path.relative_to(base).as_posix()
        for node, function in _with_functions(_tree(path)):
            modules = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
                modules = [node.module] + [f"{node.module}.{alias.name}" for alias in node.names]
            elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "__import__"
                  or isinstance(node, ast.Call) and _dotted(node.func).endswith("import_module")):
                modules = [a.value for a in node.args if isinstance(a, ast.Constant) and isinstance(a.value, str)]
            for module in modules:
                if module.split(".")[0] in NETWORK_MODULES and (name, function, module) not in ALLOWED_IMPORTS:
                    if not (isinstance(node, ast.ImportFrom) and module != node.module):
                        found.append(f"{name}:{node.lineno} ({function}) imports {module}")
            if isinstance(node, ast.Attribute):
                dotted = _dotted(node)
                for prefix, places in ALLOWED_USES.items():
                    if dotted.startswith(prefix + ".") and (name, function) not in places:
                        found.append(f"{name}:{node.lineno} ({function}) uses {dotted}")
            if isinstance(node, ast.Call):
                called = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
                if called in NETWORK_CALLS and not (name, function) in ALLOWED_USES["urllib.request"]:
                    found.append(f"{name}:{node.lineno} ({function}) calls {_dotted(node.func) or called}()")
    return found


def test_the_source_has_no_network_code_except_reading_a_web_address_you_give():
    found = _network_code()
    assert not found, ("simplydata must not reach the network (README, Privacy). Found:\n  " + "\n  ".join(found))


def test_the_scan_finds_network_code(tmp_path):
    """The scan itself works: these lines would be caught."""
    probe = tmp_path / "probe.py"
    probe.write_text(textwrap.dedent("""
        import requests
        import seaborn as sns
        from urllib.request import urlopen
        def chart():
            sns.load_dataset("tips")
            os.system("curl https://example.org")
    """), encoding="utf-8")
    found = "\n".join(_network_code([probe], tmp_path))
    for what in ("imports requests", "imports urllib.request", "calls sns.load_dataset()", "calls os.system()"):
        assert what in found, what


def test_a_web_address_sends_nothing_but_the_request_for_the_file():
    """_download asks for the file (a GET request with the address and the User-Agent "simplydata"); it sends
    no data, no cookies and nothing about you or your tables."""
    tree = _tree(PACKAGE / "_data.py")
    download = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_download")
    requests = [n for n in ast.walk(download) if isinstance(n, ast.Call) and _dotted(n.func) == "urllib.request.Request"]
    assert len(requests) == 1
    request = requests[0]
    assert [ast.unparse(a) for a in request.args] == ["url"]
    assert [k.arg for k in request.keywords] == ["headers"]
    assert ast.literal_eval(request.keywords[0].value) == {"User-Agent": "simplydata"}
    opens = [n for n in ast.walk(download) if isinstance(n, ast.Call) and _dotted(n.func) == "urllib.request.urlopen"]
    assert len(opens) == 1 and [ast.unparse(a) for a in opens[0].args] == ["request"]
    assert {k.arg for k in opens[0].keywords} == {"timeout"}


def test_only_a_web_address_reaches_the_reader_of_web_addresses():
    from simplydata import _data

    assert _data._is_web_address("https://example.org/a.csv") and _data._is_web_address("HTTP://example.org/a.csv")
    for local in ("a.csv", "C:/data/a.csv", "/home/me/a.csv", "data/http_log.csv", "ftp://example.org/a.csv",
                  "file:///home/me/a.csv"):
        assert not _data._is_web_address(local)


def test_practice_tables_come_from_the_package_not_the_web():
    from simplydata import data

    folder = Path(data.__file__).parent
    for name in data.EXAMPLES:
        assert (folder / f"{name}.csv").is_file(), name
        assert len(sdata.get_example(name)) > 0


# ---------------------------------------------------------------- (b) R code: no internet, no installs, no files
def _looks_like_r(text: str) -> bool:
    return bool(re.search(r"<-|::|\blist\(|\$", text))


def _r_problems_in_literals() -> list[str]:
    """Every string in the source (R code is written as strings in Python) checked against R_NOT_ALLOWED. Plain
    words for people may name these things: install advice ("in R: install.packages(...)"), web addresses and
    "a file (...)" in sentences that are not R code."""
    found = []
    for path in SOURCE_FILES:
        name = _name(path)
        tree = _tree(path)
        the_rule = set()  # the rule itself, and docstrings (words for people, never run as R)
        for node in ast.walk(tree):
            if (isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body
                    and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)):
                the_rule.add(id(node.body[0].value))
            if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "R_NOT_ALLOWED" for t in node.targets):
                the_rule |= {id(n) for n in ast.walk(node)}
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Constant) and isinstance(node.value, str)) or id(node) in the_rule:
                continue
            text = node.value
            for match in R_NOT_ALLOWED.finditer(text):
                said = match.group(0)
                before = text[max(0, match.start() - 6):match.start()]
                if not _looks_like_r(text) and (
                        said == "://" or re.search(r"\s\($", said)
                        or said.startswith("install.packages") and re.search(r"in R:? $", before)):
                    continue
                found.append(f"{name}:{node.lineno}: {said!r} in {text[:100]!r}")
    return found


def test_no_r_code_in_the_source_reaches_the_internet_or_writes_files():
    found = _r_problems_in_literals()
    assert not found, ("R code in simplydata must not reach the internet, install packages or write files:\n  "
                       + "\n  ".join(found))


def test_the_underneath_r_code_reaches_nothing():
    """The R code shown in the manual's boxes, which the tests and the reliability report run."""
    from simplydata._underneath import UNDERNEATH

    found = []
    for key, entry in UNDERNEATH.items():
        for library, language, source in entry.blocks():
            if language == "r" and R_NOT_ALLOWED.search(source):
                found.append(f"{key} ({library}): {R_NOT_ALLOWED.search(source).group(0)!r}")
    assert not found, found


def _r_call_code_strings() -> list[tuple[str, str]]:
    """(where, R code) of every literal first argument of r_call() and ro.r()."""
    found = []
    for path in SOURCE_FILES:
        for node in ast.walk(_tree(path)):
            if isinstance(node, ast.Call) and node.args:
                called = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
                if called in ("r_call", "r") and isinstance(node.args[0], (ast.Constant, ast.JoinedStr, ast.BinOp)):
                    text = "".join(n.value for n in ast.walk(node.args[0])
                                   if isinstance(n, ast.Constant) and isinstance(n.value, str))
                    found.append((f"{_name(path)}:{node.lineno}", text))
    return found


def test_every_written_out_r_call_is_clean():
    codes = _r_call_code_strings()
    assert len(codes) > 40  # the scan finds the R code
    found = [f"{where}: {R_NOT_ALLOWED.search(code).group(0)!r}" for where, code in codes if R_NOT_ALLOWED.search(code)]
    assert not found, found


@pytest.mark.parametrize("code", [
    'download.file("https://example.org/x.csv", "x.csv")',
    "utils::download.file(u, f)",
    'readLines(url("https://example.org"))',
    'read.csv("https://example.org/data.csv")',
    'install.packages("vegan")',
    "curl::curl_fetch_memory(u)",
    "httr::POST(u, body = d)",
    "httr2::request(u)",
    "RCurl::getURL(u)",
    "con <- socketConnection('example.org', 80)",
    "write.csv(d, 'patients.csv')",
    "saveRDS(d, 'd.rds')",
    "sink('log.txt')",
    "pdf('Rplots.pdf')",
    "system('curl example.org')",
    "browseURL('https://example.org')",
])
def test_r_call_refuses_r_code_that_could_leak(code):
    from simplydata._r import r_call

    with pytest.raises(sdata.SimplydataError, match="could reach the internet or write a file"):
        r_call(code)  # refused before R is even started: no R needed for this test


@pytest.mark.parametrize("code", [
    "stats::median(x)", "list(p = t.test(x)$p.value)", "m <- lme4::lmer(y ~ x + (1 | g)); summary(m)",
    "utils::capture.output(print(x))", "vegan::vegdist(x, 'bray')", "suppressWarnings(stats::cor.test(x, y))",
    "fit$fitted.values", "k <- ncol(X); profile(m)",
])
def test_ordinary_r_code_is_not_refused(code):
    refuse_unsafe_r_code(code)  # no error


# ---------------------------------------------------------------- (c) the network guard of the whole test suite
def test_the_suite_runs_with_the_network_blocked():
    import socket

    import conftest

    before = len(conftest.NETWORK["attempts"])
    with pytest.raises(conftest.NetworkBlocked):
        socket.create_connection(("example.org", 443), timeout=1)
    with pytest.raises(conftest.NetworkBlocked):
        socket.socket().connect(("93.184.215.14", 80))
    with pytest.raises(conftest.NetworkBlocked):  # even this computer, outside tests marked network
        socket.socket().connect(("127.0.0.1", 80))
    assert len(conftest.NETWORK["attempts"]) == before + 3
    del conftest.NETWORK["attempts"][before:]  # the guard worked; this test itself passes


def test_a_web_address_is_blocked_in_the_tests():
    """sdata.table("https://...") outside a test marked network is stopped, so no test can download quietly."""
    import conftest

    before = len(conftest.NETWORK["attempts"])
    with pytest.raises(conftest.NetworkBlocked):
        sdata.table("https://example.org/patients.csv")
    assert len(conftest.NETWORK["attempts"]) > before
    del conftest.NETWORK["attempts"][before:]


# ---------------------------------------------------------------- scripts run as a user would
MARK_VALUE = "ZQXPATIENT4711"
MARK_COLUMN = "ZQXWARD0815"
# Put in front of every script: the same network guard as the test suite, for the separate Python process
GUARD = textwrap.dedent('''
    import atexit, socket, sys
    _tried = []
    def _refuse(what):
        _tried.append(what)
        raise RuntimeError("network access in a privacy test: " + what)
    _real = socket.socket.connect
    def _connect(self, address):
        if isinstance(address, tuple):
            _refuse(repr(address))
        return _real(self, address)
    socket.socket.connect = _connect
    socket.socket.connect_ex = _connect
    _lookup = socket.getaddrinfo
    def _getaddrinfo(host, *args, **kwargs):
        if host not in (None, "localhost", "127.0.0.1", "::1", b"localhost"):
            _refuse("look up " + repr(host))
        return _lookup(host, *args, **kwargs)
    socket.getaddrinfo = _getaddrinfo
    def _report():
        if _tried:
            sys.stderr.write("NETWORK ATTEMPTS: " + "; ".join(_tried) + "\\n")
    atexit.register(_report)
''')


def _run(tmp_path, body, env_extra=None):
    """Run a script in an empty folder, with an empty home folder; give back (result, folder, home)."""
    work, home, elsewhere = tmp_path / "work", tmp_path / "home", tmp_path / "elsewhere"
    for folder in (work, home, elsewhere):
        folder.mkdir()
    script = elsewhere / "script.py"
    script.write_text(GUARD + textwrap.dedent(body), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != "SIMPLYDATA_NO_CITE_LIST"}
    env.pop("SIMPLYDATA_PROGRESS_FILE", None)
    env.update(PYTHONPATH=str(SRC) + os.pathsep + env.get("PYTHONPATH", ""), MPLBACKEND="Agg",
               PYTHONIOENCODING="utf-8", HOME=str(home), USERPROFILE=str(home),
               MPLCONFIGDIR=str(elsewhere / "mpl"), XDG_CACHE_HOME=str(elsewhere / "cache"))
    env.update(env_extra or {})
    result = subprocess.run([sys.executable, str(script)], cwd=work, env=env, capture_output=True, text=True,
                            encoding="utf-8", timeout=600, stdin=subprocess.DEVNULL)
    assert "NETWORK ATTEMPTS" not in result.stderr, result.stderr
    return result, work, home


def _table_with_marks():
    return textwrap.dedent(f'''
        import simplydata as sdata
        school = sdata.get_example("school").rename(columns={{"school": "{MARK_COLUMN}"}})
        school["{MARK_COLUMN}"] = "{MARK_VALUE}-" + school["{MARK_COLUMN}"].astype(str)
        table = sdata.table(school)
    ''')


def _r_ready() -> bool:
    from simplydata._r import r_ready

    return r_ready(("lme4", "lmerTest"))


def test_the_list_of_packages_never_holds_your_data(tmp_path):
    """Values, column names and groups of the table are printed by the words themselves (to your own screen),
    but never in sdata.show_packages_used(), its BibTeX file or the list at the end of the script."""
    use_r = _r_ready()
    body = _table_with_marks() + textwrap.dedent(f'''
        table.find_average_of("marks", for_each_group_in="{MARK_COLUMN}")
        table.keep_rows_where("{MARK_COLUMN}", is_equal_to="{MARK_VALUE}-" + str(sdata.get_example("school")["school"].iloc[0]))
        table.start_chart().draw_bars(x="{MARK_COLUMN}", y="marks").save("asked.png")
        table.save("asked.csv")
        {'big = sdata.table(school); big.explain("marks", using=["hours", "breakfast"], grouped_by="' + MARK_COLUMN
         + '", p_value_by="satterthwaite")' if use_r else ''}
        print("=== FULL LIST ===")
        sdata.show_packages_used(save_as="asked.bib")
        print("=== END OF SCRIPT ===")
    ''')
    result, work, home = _run(tmp_path, body)
    assert result.returncode == 0, result.stderr
    out = result.stdout
    assert MARK_VALUE in out.split("=== FULL LIST ===")[0]  # the words did show the table on screen
    full, at_end = out.split("=== FULL LIST ===")[1].split("=== END OF SCRIPT ===")
    assert "Packages simplydata used in this script" in at_end
    if use_r:
        assert "lme4" in full
    for text in (full, at_end, (work / "asked.bib").read_text(encoding="utf-8"), result.stderr):
        assert MARK_VALUE not in text and MARK_COLUMN not in text
        assert "ZQX" not in text


def test_a_script_writes_only_the_files_it_asks_for(tmp_path):
    body = _table_with_marks() + textwrap.dedent('''
        table.find_average_of("marks")
        table.start_chart().draw_histogram(x="marks").save("chart.png")
        table.save("clean.csv")
        sdata.show_packages_used()
    ''')
    result, work, home = _run(tmp_path, body)
    assert result.returncode == 0, result.stderr
    assert sorted(p.name for p in work.iterdir()) == ["chart.png", "clean.csv"]
    assert list(home.iterdir()) == []  # nothing in your home folder


# ---------------------------------------------------------------- (e) no log files, nothing written on import
def test_the_source_does_not_log():
    found = [f"{_name(p)}:{n.lineno}" for p in SOURCE_FILES for n in ast.walk(_tree(p))
             if isinstance(n, (ast.Import, ast.ImportFrom))
             and any((getattr(n, "module", None) or a.name).split(".")[0] == "logging" for a in n.names)]
    assert not found, f"simplydata keeps no logs: {found}"


def test_importing_simplydata_adds_no_log_file_and_writes_nothing(tmp_path):
    body = textwrap.dedent('''
        import logging
        before = {id(h) for lg in [logging.getLogger()] + [l for l in logging.root.manager.loggerDict.values()
                  if isinstance(l, logging.Logger)] for h in lg.handlers}
        import simplydata as sdata
        loggers = [logging.getLogger()] + [l for l in logging.root.manager.loggerDict.values()
                                           if isinstance(l, logging.Logger)]
        handlers = [h for lg in loggers for h in lg.handlers  # a NullHandler (some packages add one) drops all
                    if id(h) not in before and not isinstance(h, logging.NullHandler)]
        files = [h for lg in loggers for h in lg.handlers
                 if isinstance(h, logging.FileHandler) or getattr(h, "baseFilename", None)]
        print("FILE HANDLERS", len(files))
        print("NEW HANDLERS", [type(h).__name__ for h in handlers])
    ''')
    result, work, home = _run(tmp_path, body, env_extra={"SIMPLYDATA_NO_CITE_LIST": "1"})
    assert result.returncode == 0, result.stderr
    assert "FILE HANDLERS 0" in result.stdout
    assert "NEW HANDLERS []" in result.stdout
    assert list(work.iterdir()) == [] and list(home.iterdir()) == []
