"""One time limit for the heavy SymPy calls (simplify, factor, expand, integrate, limit, series, solve, solveset,
dsolve, summation, apart, collect, subs and evalf of formulas, and exact grid work): a call that takes longer than
TIME_LIMIT seconds is stopped, with a plain sentence, instead of hanging the session. A word that makes several
SymPy calls (a limit from both sides, solve with its completeness check, a sum with its decimal) shares one deadline
of TIME_LIMIT seconds for all of them (one_deadline); each thread keeps its own deadline.

SymPy has no time limit of its own, and Windows has no alarm signal, so the call runs in a helper process on this
computer that is kept alive between calls (multiprocessing with the "spawn" start method, the same on every
system; on Linux and macOS multiprocessing also starts its own small resource-tracker process). The helper runs
_sympy_worker.py on its own: it imports SymPy only, never simplydata and never your script, and gets each job as a
SymPy function with its values (pickled; never text to run). When the time is up the helper is stopped and a new
one starts at the next call. The helper has a memory limit (half the memory free when it starts, at least 1 GB and
at most 4 GB), so a sum whose numbers grow without end stops with MemoryError instead of filling the computer. macOS
does not honour that limit inside the helper, so there this process looks at the helper's memory (its physical
footprint, read with proc_pid_rusage) every WATCH_EVERY seconds while it waits, and stops the helper at the limit.
On macOS the limit is 1 GB (the helper cannot read the free memory there, so it takes the smallest limit).

Privacy: the helper is a local process. It talks to this one through two one-way multiprocessing pipes (named pipes
on Windows, os.pipe elsewhere; never a socket, so no network), writes no file, logs nothing, sends its own output
to the null device, and is stopped when Python exits (atexit here, and as a daemon process by multiprocessing
itself); a watchdog thread in the helper ends it when this process is gone, even in the middle of a job. Where no
helper process can be started (inside another daemon process, an embedded Python whose executable is not Python,
or a system without processes), the call runs here without the time limit, and simplydata says so once.
"""

from __future__ import annotations

import atexit
import functools
import os
import pickle
import sys
import threading
import time

from ._errors import SimplydataError

TIME_LIMIT = 60.0  # seconds one SymPy call (or one word's SymPy calls together) may take
START_LIMIT = 120.0  # seconds the helper may take to start (it imports SymPy once)
WORKER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_sympy_worker.py")
FORMULA_HINT = ("Try f.make_simpler() first, or carry on in SymPy itself, which has no time limit: f.as_sympy() "
                "gives the SymPy expression.")
EXACTLY_HINT = "Leave out exactly=True for the answer in decimals (SciPy and NumPy)."

_LOCK = threading.RLock()
_STATE: dict = {"process": None, "jobs": None, "answers": None, "said_no_helper": False, "memory_limit": None}
WATCH_EVERY = 0.05  # seconds between two looks at the helper's memory on macOS
# per thread: the deadline of the word running in this thread, and whether this thread is starting the helper
_LOCAL = threading.local()


def _stop_message(what: str, seconds: float, hint: str) -> str:
    return f"{what} did not finish in {seconds:g} seconds, so simplydata stopped it.\n{hint}"


def one_deadline(func):
    """All the SymPy calls of one word share one deadline of TIME_LIMIT seconds (the first word called sets it).

    The deadline belongs to the thread that runs the word (threading.local), so words in two threads never share or
    clear each other's deadline."""
    @functools.wraps(func)
    def word(*args, **kwargs):
        if getattr(_LOCAL, "deadline", None) is not None:  # a word inside a word: the outer deadline holds
            return func(*args, **kwargs)
        _LOCAL.deadline = time.monotonic() + TIME_LIMIT
        try:
            return func(*args, **kwargs)
        finally:
            _LOCAL.deadline = None
    return word


def current_deadline():
    """The deadline of the word running in this thread (time.monotonic() seconds), or None."""
    return getattr(_LOCAL, "deadline", None)


def _helper_can_start() -> bool:
    """False inside a daemon process, or in an embedded Python whose executable is not a Python."""
    import multiprocessing
    from multiprocessing import spawn

    if multiprocessing.current_process().daemon:
        return False
    # on Linux and macOS multiprocessing keeps the executable as bytes (os.fsencode), on Windows as text
    name = os.path.basename(os.fsdecode(spawn.get_executable() or "")).lower()
    return bool(name) and name.startswith(("python", "pypy"))


def _preparation_without_main(real):
    """multiprocessing's get_preparation_data, leaving the main script out only for the thread that starts the
    helper (any other thread, and any other start, gets multiprocessing's own data unchanged)."""
    def get_preparation_data(name):
        data = real(name)
        if getattr(_LOCAL, "starting_helper", False):
            data.pop("init_main_from_path", None)
            data.pop("init_main_from_name", None)
        return data

    get_preparation_data.simplydata_wrapped = real
    return get_preparation_data


_WRAP_LOCK = threading.Lock()


def _start_without_main(process) -> None:
    """Start the helper without running your script again in it.

    With the "spawn" start method a new process normally imports the main script (as __mp_main__), which runs a
    script's top-level lines a second time when they are not under if __name__ == "__main__". The helper needs
    nothing from the script, so while it starts, multiprocessing's preparation data leaves the main script out.
    multiprocessing's get_preparation_data is wrapped once, and the wrapper leaves the script out only in the thread
    that is starting the helper at that moment (threading.local), so a process another thread starts at the same
    time keeps its main script; __main__ is never touched.
    """
    from multiprocessing import spawn

    with _WRAP_LOCK:
        if not hasattr(spawn.get_preparation_data, "simplydata_wrapped"):
            spawn.get_preparation_data = _preparation_without_main(spawn.get_preparation_data)
    _LOCAL.starting_helper = True
    try:
        process.start()
    finally:
        _LOCAL.starting_helper = False


def _start():
    """The running helper (process, jobs pipe, answers pipe), started if needed; None where no process can start."""
    process = _STATE["process"]
    if process is not None and process.is_alive():
        return process, _STATE["jobs"], _STATE["answers"]
    _stop()
    import multiprocessing
    import runpy

    if not _helper_can_start():
        return None
    context = multiprocessing.get_context("spawn")
    pipes = []
    try:
        job_reader, jobs = context.Pipe(duplex=False)  # one-way: this process writes jobs, the helper reads them
        answers, answer_writer = context.Pipe(duplex=False)  # one-way: the helper writes answers back
        pipes = [job_reader, jobs, answers, answer_writer]
        process = context.Process(target=runpy.run_path, args=(WORKER_FILE,),
                                  kwargs={"init_globals": {"jobs": job_reader, "answers": answer_writer},
                                          "run_name": "simplydata_sympy_helper"},
                                  name="simplydata SymPy helper", daemon=True)
        _start_without_main(process)
    except (AssertionError, OSError, RuntimeError, ValueError):  # e.g. a daemon process cannot have children
        for pipe in pipes:
            pipe.close()
        return None
    job_reader.close()
    answer_writer.close()
    _STATE["process"], _STATE["jobs"], _STATE["answers"] = process, jobs, answers
    if not answers.poll(START_LIMIT):
        _kill()
        raise SimplydataError(f"The helper process for SymPy did not start in {START_LIMIT:g} seconds.")
    try:
        _, _STATE["memory_limit"] = answers.recv()  # ("ready", the helper's memory limit in bytes)
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


def _run_here(call, values, named):
    if not _STATE["said_no_helper"] and os.environ.get("SIMPLYDATA_SYMPY_HELPER") != "0":
        _STATE["said_no_helper"] = True
        print(f"Note: no helper process can be started here, so SymPy runs without the {TIME_LIMIT:g}-second time "
              "limit.")
    return call(*values, **named)


def _send(jobs, job, what: str) -> None:
    try:
        jobs.send(job)
    except (pickle.PicklingError, AttributeError, TypeError) as error:  # never for SymPy's own functions
        raise SimplydataError(f"{what} could not be handed to the helper process ({error}).") from None


def _memory_message(what: str, hint: str) -> str:
    return (f"{what} needed more memory than the helper may use, so simplydata stopped it. The numbers grow too big "
            f"to work with exactly.\n{hint}")


def _memory_in_use(pid: int):
    """The memory the process pid uses now on macOS (its physical footprint, compressed pages included), or None."""
    try:
        import ctypes

        class Usage(ctypes.Structure):  # struct rusage_info_v0 of <sys/resource.h>
            _fields_ = [("uuid", ctypes.c_uint8 * 16), ("user_time", ctypes.c_uint64),
                        ("system_time", ctypes.c_uint64), ("idle_wakeups", ctypes.c_uint64),
                        ("interrupt_wakeups", ctypes.c_uint64), ("pageins", ctypes.c_uint64),
                        ("wired_size", ctypes.c_uint64), ("resident_size", ctypes.c_uint64),
                        ("phys_footprint", ctypes.c_uint64), ("start_time", ctypes.c_uint64),
                        ("exit_time", ctypes.c_uint64)]

        library = _STATE.get("libproc")
        if library is False:  # loading it failed once: do not try again every WATCH_EVERY seconds
            return None
        if library is None:
            _STATE["libproc"] = False
            library = _STATE["libproc"] = ctypes.CDLL("/usr/lib/libproc.dylib")
        usage = Usage()
        if library.proc_pid_rusage(ctypes.c_int(pid), ctypes.c_int(0), ctypes.byref(usage)) != 0:  # RUSAGE_INFO_V0
            return None
        return int(usage.phys_footprint)
    except (AttributeError, OSError, ValueError):  # pragma: no cover - not macOS, or no libproc
        return None


def _wait(process, answers, seconds: float):
    """Wait up to seconds for the helper's answer: True when it is there, False when the time is up, None when (on
    macOS, which ignores the helper's own memory limit) the helper went over its memory limit."""
    limit = _STATE["memory_limit"]
    if sys.platform != "darwin" or not limit:
        return answers.poll(seconds)
    end = time.monotonic() + seconds
    while True:
        left = end - time.monotonic()
        if answers.poll(max(0.0, min(WATCH_EVERY, left))):
            return True
        used = _memory_in_use(process.pid)
        if used is not None and used > limit:
            return True if answers.poll(0) else None  # an answer that came in just now is kept
        if left <= WATCH_EVERY:
            return False


def run_with_time_limit(call, *values, what: str = "SymPy", hint: str = FORMULA_HINT, **named):
    """call(*values, **named) in the helper process, stopped after TIME_LIMIT seconds with a plain sentence.

    call is always a function of SymPy itself (sympy.simplify, sympy.integrate, a SymPy object's method ...), and
    the values are SymPy objects and numbers. SymPy's own errors come back as they are; hint= is the advice the
    stop sentence gives (it depends on the word).
    """
    with _LOCK:
        if os.environ.get("SIMPLYDATA_SYMPY_HELPER") == "0":
            return _run_here(call, values, named)
        started = _start()
        if started is None:
            return _run_here(call, values, named)
        process, jobs, answers = started
        job = (call, values, named)
        try:
            _send(jobs, job, what)
        except (OSError, ValueError):  # the helper went away between calls: start a new one once
            _kill()
            started = _start()
            if started is None:
                return _run_here(call, values, named)
            process, jobs, answers = started
            _send(jobs, job, what)
        deadline = current_deadline()
        seconds = TIME_LIMIT if deadline is None else max(0.0, deadline - time.monotonic())
        try:
            finished = _wait(process, answers, seconds)
        except BaseException:  # Ctrl+C while waiting: the helper is mid-job, so stop it too
            _kill()
            raise
        if finished is None:  # macOS: the helper went over its memory limit
            _kill()
            raise SimplydataError(_memory_message(what, hint))
        if not finished:
            _kill()
            raise SimplydataError(_stop_message(what, TIME_LIMIT, hint))
        try:
            status, answer = answers.recv()
        except (EOFError, OSError):
            _kill()
            raise SimplydataError(f"{what} stopped the helper process (it may have run out of memory). Try a "
                                  f"simpler formula.\n{hint}") from None
    if status == "error":
        if isinstance(answer, MemoryError):
            raise SimplydataError(_memory_message(what, hint))
        raise answer
    return answer
