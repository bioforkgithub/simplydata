"""The worker process behind simplydata's time limit for SymPy (the parent side is _time_limit.py).

This file is run on its own in one local helper process (multiprocessing, started with runpy.run_path), so the
helper imports SymPy and nothing from simplydata. It reads a job from one one-way pipe, runs it and writes the answer
to the other (two one-way pipes: on Windows named pipes, elsewhere os.pipe, never a socket):

* a job is (SymPy function, values, named values), always a function of SymPy itself, never text to run;
* the answer is ("done", what SymPy gave) or ("error", the error SymPy raised);
* None, or a closed pipe (the parent has stopped), ends the helper.

Nothing is written, logged or sent anywhere else: the answers pipe to the parent process is the helper's only way
out.
"""

from __future__ import annotations


def serve(jobs, answers) -> None:
    """Run jobs from the parent until it says stop (None) or goes away."""
    import signal

    try:  # Ctrl+C is for the parent: it stops the helper itself when it needs to
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    except (ValueError, OSError):  # pragma: no cover - not the main thread of the helper
        pass
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
        except Exception as error:
            answer = ("error", error)
        try:
            answers.send(answer)
        except Exception as error:  # SymPy's answer or error cannot be sent back as it is
            answers.send(("error", RuntimeError(f"{type(error).__name__}: {error}")))


if "jobs" in globals():  # run by runpy.run_path(..., init_globals={"jobs": ..., "answers": ...}) in the helper
    serve(globals()["jobs"], globals()["answers"])
