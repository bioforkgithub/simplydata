"""The worker process behind simplydata's time limit for SymPy (the parent side is _time_limit.py).

This file is run on its own in one local helper process (multiprocessing, started with runpy.run_path), so the
helper imports SymPy and nothing from simplydata. It reads a job from one one-way pipe, runs it and writes the answer
to the other (two one-way pipes: on Windows named pipes, elsewhere os.pipe, never a socket):

* a job is (SymPy function, values, named values), always a function of SymPy itself, never text to run;
* the answer is ("done", what SymPy gave) or ("error", the error SymPy raised);
* None, or a closed pipe (the parent has stopped), ends the helper.

Three guards keep the helper from outliving or troubling the parent:

* a watchdog thread waits on the parent process and ends the helper at once when the parent is gone, even in the
  middle of a SymPy job (a job does not read the pipe, so it would not notice otherwise);
* its standard output and error go to the null device, so it never holds the pipes of a program that reads the
  parent's output;
* a memory limit (half the memory that is free when the helper starts, at least 1 GB and at most 4 GB): a job that
  needs more gets MemoryError, and the computer keeps memory for everything else.

Nothing is written, logged or sent anywhere else: the answers pipe to the parent process is the helper's only way
out.
"""

from __future__ import annotations

import os
import sys

GIGABYTE = 1024 ** 3


MOST_MEMORY = 4 * GIGABYTE  # the helper's memory limit is never above this
LEAST_MEMORY = GIGABYTE  # nor below this (SymPy itself needs a few hundred MB)


def _memory_free_now() -> int:
    """The memory this computer has free now (Windows: available physical memory; Linux: MemAvailable)."""
    try:
        if sys.platform == "win32":
            import ctypes

            class Status(ctypes.Structure):
                _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong), ("total", ctypes.c_ulonglong),
                            ("available", ctypes.c_ulonglong), ("total_page", ctypes.c_ulonglong),
                            ("available_page", ctypes.c_ulonglong), ("total_virtual", ctypes.c_ulonglong),
                            ("available_virtual", ctypes.c_ulonglong), ("extended", ctypes.c_ulonglong)]

            status = Status()
            status.length = ctypes.sizeof(Status)
            if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                raise OSError("GlobalMemoryStatusEx")
            return int(status.available)
        if os.path.exists("/proc/meminfo"):
            with open("/proc/meminfo", encoding="ascii") as info:
                for line in info:
                    if line.startswith("MemAvailable:"):
                        return int(line.split()[1]) * 1024
        return int(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_AVPHYS_PAGES"))
    except (AttributeError, OSError, ValueError):  # pragma: no cover - no way to ask: the smallest limit
        return 2 * LEAST_MEMORY


def memory_limit() -> int:
    """Half the memory free now, at least 1 GB and at most 4 GB."""
    return max(LEAST_MEMORY, min(MOST_MEMORY, _memory_free_now() // 2))


def _limit_memory() -> None:
    """Give the helper a memory limit: a Job object on Windows, RLIMIT_AS elsewhere (where the system honours it)."""
    limit = memory_limit()
    try:
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes

            class Basic(ctypes.Structure):
                _fields_ = [("per_process_time", ctypes.c_longlong), ("per_job_time", ctypes.c_longlong),
                            ("flags", wintypes.DWORD), ("minimum_working_set", ctypes.c_size_t),
                            ("maximum_working_set", ctypes.c_size_t), ("active_processes", wintypes.DWORD),
                            ("affinity", ctypes.c_size_t), ("priority", wintypes.DWORD),
                            ("scheduling", wintypes.DWORD)]

            class Counters(ctypes.Structure):
                _fields_ = [(name, ctypes.c_ulonglong) for name in ("reads", "writes", "others", "read_bytes",
                                                                     "written_bytes", "other_bytes")]

            class Extended(ctypes.Structure):
                _fields_ = [("basic", Basic), ("io", Counters), ("process_memory", ctypes.c_size_t),
                            ("job_memory", ctypes.c_size_t), ("peak_process", ctypes.c_size_t),
                            ("peak_job", ctypes.c_size_t)]

            kernel = ctypes.windll.kernel32
            kernel.CreateJobObjectW.restype = wintypes.HANDLE
            kernel.GetCurrentProcess.restype = wintypes.HANDLE
            job = kernel.CreateJobObjectW(None, None)
            info = Extended()
            info.basic.flags = 0x100  # JOB_OBJECT_LIMIT_PROCESS_MEMORY
            info.process_memory = limit
            kernel.SetInformationJobObject(wintypes.HANDLE(job), 9, ctypes.byref(info), ctypes.sizeof(info))
            kernel.AssignProcessToJobObject(wintypes.HANDLE(job), wintypes.HANDLE(kernel.GetCurrentProcess()))
        else:
            import resource

            resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    except (AttributeError, OSError, ValueError, ImportError, TypeError, ArithmeticError):  # pragma: no cover
        pass


def _quiet_output() -> None:
    """Send the helper's own output to the null device (also the inherited handles, not only Python's objects)."""
    null = os.open(os.devnull, os.O_RDWR)
    for stream, number in ((sys.stdout, 1), (sys.stderr, 2)):
        try:
            if stream is not None:
                stream.flush()
            os.dup2(null, number)
        except (OSError, ValueError):  # pragma: no cover - no such handle in this process
            pass
    sys.stdout = sys.stderr = open(os.devnull, "w", encoding="utf-8")


def _watch_parent() -> None:
    """End the helper as soon as the process that started it is gone."""
    import threading
    from multiprocessing import parent_process
    from multiprocessing.connection import wait

    parent = parent_process()
    if parent is None:  # pragma: no cover - always set for a process started by multiprocessing
        return

    def watch():
        wait([parent.sentinel])
        os._exit(0)

    threading.Thread(target=watch, name="simplydata parent watchdog", daemon=True).start()


def serve(jobs, answers) -> None:
    """Run jobs from the parent until it says stop (None) or goes away."""
    import signal

    try:  # Ctrl+C is for the parent: it stops the helper itself when it needs to
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    except (ValueError, OSError):  # pragma: no cover - not the main thread of the helper
        pass
    _watch_parent()
    _quiet_output()
    _limit_memory()
    import sympy  # noqa: F401  - loaded once, so the first job does not wait for it

    answers.send(("ready", None))
    while True:
        try:
            job = jobs.recv()
        except (EOFError, OSError):
            return
        except Exception as error:  # a job that cannot be read back (it is not run)
            answers.send(("error", RuntimeError(f"the helper could not read the job: {error}")))
            continue
        if job is None:
            return
        call, values, named = job
        try:
            answer = ("done", call(*values, **named))
        except MemoryError:
            answer = ("error", MemoryError())
        except Exception as error:
            answer = ("error", error)
        try:
            answers.send(answer)
        except Exception as error:  # SymPy's answer or error cannot be sent back as it is
            answers.send(("error", RuntimeError(f"{type(error).__name__}: {error}")))


if "jobs" in globals():  # run by runpy.run_path(..., init_globals={"jobs": ..., "answers": ...}) in the helper
    serve(globals()["jobs"], globals()["answers"])
