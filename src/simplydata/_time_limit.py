"""One time limit for the heavy SymPy calls (simplify, factor, integrate, limit, series, solve, solveset, dsolve,
summation, apart, collect, and exact grid work): a call that takes longer than TIME_LIMIT seconds is stopped, with a
plain sentence, instead of hanging the session.

SymPy has no time limit of its own, and Windows has no alarm signal, so the call runs in one helper process on this
computer that is kept alive between calls (multiprocessing with the "spawn" start method, the same on every
system). The helper runs _sympy_worker.py on its own: it imports SymPy only, never simplydata, and gets each job as
a SymPy function with its values (pickled; never text to run). When the time is up the helper is stopped and a new
one starts at the next call.

Privacy: the helper is a local process. It talks to this one through two one-way multiprocessing pipes (named pipes
on Windows, os.pipe elsewhere; never a socket, so no network), writes no file, logs nothing, and is stopped when
Python exits
(atexit here, and as a daemon process by multiprocessing itself). Where no helper process can be started (inside
another daemon process, or on a system without processes), the call runs here without the time limit, and
simplydata says so once.
"""

from __future__ import annotations

import atexit
import os
import sys
import threading
import types
from contextlib import contextmanager

from ._errors import SimplydataError

TIME_LIMIT = 60.0  # seconds one SymPy call may take
START_LIMIT = 120.0  # seconds the helper may take to start (it imports SymPy once)
WORKER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_sympy_worker.py")

_LOCK = threading.RLock()
_STATE: dict = {"process": None, "jobs": None, "answers": None, "said_no_helper": False}


def _stop_message(what: str) -> str:
    return (f"{what} did not finish in {TIME_LIMIT:g} seconds, so simplydata stopped it.\n"
            "Try f.make_simpler() first, or leave out exactly=True for a decimal answer. To give SymPy as long as it "
            "needs, carry on in SymPy itself: f.as_sympy() gives the SymPy expression.")


@contextmanager
def _main_module_hidden():
    """Start the helper without running your script again in it.

    With the "spawn" start method the new process normally imports the main script (as __mp_main__), which runs a
    script's top-level lines a second time when they are not under if __name__ == "__main__". The helper needs
    nothing from the script, so the main module is swapped for an empty one while the helper starts.
    """
    real = sys.modules.get("__main__")
    sys.modules["__main__"] = types.ModuleType("__main__")
    try:
        yield
    finally:
        if real is not None:
            sys.modules["__main__"] = real


def _start():
    """The running helper (process, jobs pipe, answers pipe), started if needed; None where no process can start."""
    process = _STATE["process"]
    if process is not None and process.is_alive():
        return process, _STATE["jobs"], _STATE["answers"]
    _stop()
    import multiprocessing
    import runpy

    context = multiprocessing.get_context("spawn")
    try:
        job_reader, jobs = context.Pipe(duplex=False)  # one-way: this process writes jobs, the helper reads them
        answers, answer_writer = context.Pipe(duplex=False)  # one-way: the helper writes answers back
        process = context.Process(target=runpy.run_path, args=(WORKER_FILE,),
                                  kwargs={"init_globals": {"jobs": job_reader, "answers": answer_writer},
                                          "run_name": "simplydata_sympy_helper"},
                                  name="simplydata SymPy helper", daemon=True)
        with _main_module_hidden():
            process.start()
    except (AssertionError, OSError, RuntimeError, ValueError):  # e.g. a daemon process cannot have children
        return None
    job_reader.close()
    answer_writer.close()
    _STATE["process"], _STATE["jobs"], _STATE["answers"] = process, jobs, answers
    if not answers.poll(START_LIMIT):
        _stop()
        raise SimplydataError(f"The helper process for SymPy did not start in {START_LIMIT:g} seconds.")
    try:
        answers.recv()  # ("ready", None)
    except (EOFError, OSError):
        _stop()
        raise SimplydataError("The helper process for SymPy stopped while starting; is SymPy installed "
                              '(pip install "simplydata[exact]")?') from None
    return process, jobs, answers


def _stop() -> None:
    """Stop the helper (if any) and forget it. Also run when Python exits."""
    process, jobs, answers = _STATE["process"], _STATE["jobs"], _STATE["answers"]
    _STATE["process"] = _STATE["jobs"] = _STATE["answers"] = None
    if jobs is not None:
        try:
            if process is not None and process.is_alive():
                jobs.send(None)
        except (OSError, ValueError):
            pass
        jobs.close()
    if answers is not None:
        answers.close()
    if process is not None:
        process.join(0.5)
        if process.is_alive():
            process.terminate()
            process.join(2)
        if process.is_alive():  # pragma: no cover - terminate is enough on every system tried
            process.kill()
            process.join(2)
        process.close()


def _kill() -> None:
    """Stop a helper that is busy (it cannot read "stop" while SymPy works)."""
    process = _STATE["process"]
    if process is not None and process.is_alive():
        process.kill()
        process.join(5)
    _stop()


atexit.register(_stop)


def helper_is_running() -> bool:
    """Whether the helper process is alive now (for the tests and for sdata's own checks)."""
    process = _STATE["process"]
    return process is not None and process.is_alive()


def helper_process_id():
    """The process id of the helper, or None."""
    process = _STATE["process"]
    return process.pid if process is not None and process.is_alive() else None


def run_with_time_limit(call, *values, what: str = "SymPy", **named):
    """call(*values, **named) in the helper process, stopped after TIME_LIMIT seconds with a plain sentence.

    call is always a function of SymPy itself (sympy.simplify, sympy.integrate, a SymPy object's method ...), and
    the values are SymPy objects and numbers. SymPy's own errors come back as they are.
    """
    with _LOCK:
        if os.environ.get("SIMPLYDATA_SYMPY_HELPER") == "0" or (started := _start()) is None:
            if not _STATE["said_no_helper"] and os.environ.get("SIMPLYDATA_SYMPY_HELPER") != "0":
                _STATE["said_no_helper"] = True
                print(f"Note: no helper process can be started here, so SymPy runs without the {TIME_LIMIT:g}-second "
                      "time limit.")
            return call(*values, **named)
        process, jobs, answers = started
        try:
            jobs.send((call, values, named))
        except (OSError, ValueError):  # the helper went away between calls: start a new one once
            _kill()
            process, jobs, answers = _start()
            jobs.send((call, values, named))
        try:
            finished = answers.poll(TIME_LIMIT)
        except BaseException:  # Ctrl+C while waiting: the helper is mid-job, so stop it too
            _kill()
            raise
        if not finished:
            _kill()
            raise SimplydataError(_stop_message(what))
        try:
            status, answer = answers.recv()
        except (EOFError, OSError):
            _kill()
            raise SimplydataError(f"{what} stopped the helper process (it may have run out of memory). Try a "
                                  "simpler formula, or leave out exactly=True for a decimal answer.") from None
    if status == "error":
        raise answer
    return answer
