"""Linear systems (control): sdata.system(...) and sdata.frequency_filter(...). Every number comes from SciPy:

* the system is a scipy.signal.lti / dlti (TransferFunction; poles and zeros as SciPy gives them);
* responses: signal.step, impulse, lsim (continuous) and dstep, dimpulse, dlsim (in steps); a filter made
  by sdata.frequency_filter runs with sosfilt, as the filter words with both_ways=False;
* frequency response: signal.freqresp (continuous), freqz / sosfreqz (in steps);
* in_steps: signal.cont2discrete; table(form="state space"): signal.tf2ss.
* families for 100 %, batches 17-18 (plan 2.7, approved by Manish 2026-11-28): table(form="sections") is
  signal.tf2sos (the filter's own sections for sdata.frequency_filter), form="partial fractions" signal.residue
  (residuez in steps); sdata.system(sections=) is sos2tf, sdata.system(residues=, poles=) invres (invresz);
  move_poles_to is signal.place_poles on the tf2ss matrices; frequency_response(with_delay=True) adds
  signal.group_delay; sdata.frequency_filter(analog=True) is SciPy's analog design (butter(..., analog=True)
  and the others).

Own code is glue only: reading the formula (ast, never run; polynomial arithmetic with numpy.polynomial),
joining systems (series = product, parallel = sum, feedback = G / (1 + G H), as R control), and display
arithmetic on SciPy's output: gain in dB, unwrapped phase, damping ratio and natural frequency of each
pole (as R control::damp).

Rise time, settling time and overshoot (python-control step_info, on SciPy's step response) and the
gain and phase margins (python-control stability_margins) come from python-control, the established
Python package for control systems (R control has no stepinfo or margin). It is an optional extra:
pip install "simplydata[systems]"; without it the responses still come, with a note.
"""

from __future__ import annotations

import ast

import numpy as np

from ._errors import SimplydataError, choice_error, friendly

FORMULA_EXAMPLE = 'sdata.system("1 / (s**2 + 2*s + 5)")'
DISCRETE_METHODS = {"zero order hold": "zoh", "bilinear": "bilinear", "forward difference": "euler",
                    "backward difference": "backward_diff"}
METHOD_SPELLINGS = {"zoh": "zero order hold", "tustin": "bilinear", "euler": "forward difference",
                    "backward_diff": "backward difference", "forward euler": "forward difference",
                    "backward euler": "backward difference"}
UNITS = ("radians per second", "cycles per second")
UNIT_SPELLINGS = {"rad/s": "radians per second", "radians": "radians per second", "hz": "cycles per second",
                  "hertz": "cycles per second", "cycles per unit of time": "cycles per second"}
CHARTS = ("bode", "step", "impulse", "poles and zeros", "nyquist")
CHART_SPELLINGS = {"pole-zero": "poles and zeros", "pole zero": "poles and zeros", "pzmap": "poles and zeros",
                   "gain and phase": "bode"}
FORMS = ("transfer function", "state space", "poles and zeros", "sections", "partial fractions")
FORM_SPELLINGS = {"second-order sections": "sections", "sos": "sections", "residues": "partial fractions",
                  "zeros and poles": "poles and zeros", "zpk": "poles and zeros", "ss": "state space",
                  "tf": "transfer function"}
WORDS = ("step_response", "impulse_response", "response_to", "frequency_response", "poles", "zeros", "is_stable",
         "steady_gain", "in_steps", "then", "add", "with_feedback", "move_poles_to", "table", "chart")
# names from R control, SciPy and MATLAB -> the System word (they never run)
HINTS = {"step": "step_response()", "stepinfo": "step_response()", "impulse": "impulse_response()",
         "lsim": "response_to(inputs)", "simulate": "response_to(inputs)", "bode": "frequency_response() or .chart()",
         "freqresp": "frequency_response()", "freqs": "frequency_response()", "freqz": "frequency_response()",
         "margin": "frequency_response() (it prints the margins)", "nyquist": 'chart(show="nyquist")',
         "pzmap": 'chart(show="poles and zeros")', "pole": "poles()", "zero": "zeros()", "damp": "poles()",
         "isstable": "is_stable()", "dcgain": "steady_gain()", "c2d": "in_steps(time_step=0.1)",
         "cont2discrete": "in_steps(time_step=0.1)", "to_discrete": "in_steps(time_step=0.1)",
         "series": "then(other)", "parallel": "add(other)", "feedback": "with_feedback()",
         "tf2ss": 'table(form="state space")', "to_ss": 'table(form="state space")',
         "tf2zpk": 'table(form="poles and zeros")', "to_zpk": 'table(form="poles and zeros")',
         "tfdata": "table()", "num": "table()", "den": "table()", "units": "chart(unit=...)",
         "tf2sos": 'table(form="sections")', "zpk2sos": 'table(form="sections")', "to_sos": 'table(form="sections")',
         "residue": 'table(form="partial fractions")', "residuez": 'table(form="partial fractions")',
         "place": "move_poles_to([-2, -3])", "place_poles": "move_poles_to([-2, -3])",
         "acker": "move_poles_to([-2, -3])", "group_delay": "frequency_response(with_delay=True)",
         "grpdelay": "frequency_response(with_delay=True)"}


def _g(x, digits=6) -> str:
    x = float(x)
    if x == 0:
        return "0"
    return f"{x:.{digits}g}"


# ---------------------------------------------------------------------------------------- formula reading
def _formula_error(problem):
    return SimplydataError(f"{problem}\nA system formula is a ratio of polynomials in s (or z with time_step=), "
                           f"with numbers, + - * / ( ) and whole powers **, such as {FORMULA_EXAMPLE} or "
                           'sdata.system("0.1 / (z - 0.9)", time_step=0.1).')


def read_system_formula(text):
    """(numerator, denominator, variable) from "1 / (s**2 + 2*s + 5)": coefficients highest power first.
    The text is read with ast and never run; the arithmetic is numpy.polynomial's."""
    from numpy.polynomial import Polynomial as P

    if not isinstance(text, str) or not text.strip():
        raise _formula_error("sdata.system() needs a formula as text.")
    if "^" in text:
        raise _formula_error('Write powers with **, such as s**2 (not s^2).')
    try:
        tree = ast.parse(text.strip(), mode="eval")
    except SyntaxError:
        raise _formula_error(f'"{text}" is not a formula simplydata can read (write 2*s, not 2s).') from None
    used = set()

    def walk(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return P([float(node.value)]), P([1.0])
        if isinstance(node, ast.Name):
            if node.id not in ("s", "z"):
                raise _formula_error(f'"{node.id}" is not allowed: a system formula uses s (continuous time) or z '
                                     "(in steps) and numbers only.")
            used.add(node.id)
            return P([0.0, 1.0]), P([1.0])
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            top, bottom = walk(node.operand)
            return (-top if isinstance(node.op, ast.USub) else top), bottom
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Pow):
                power = node.right
                sign = 1
                if isinstance(power, ast.UnaryOp) and isinstance(power.op, ast.USub):
                    sign, power = -1, power.operand
                if not (isinstance(power, ast.Constant) and isinstance(power.value, int)
                        and not isinstance(power.value, bool)) or power.value > 50:
                    raise _formula_error("Powers must be whole numbers, such as s**2.")
                top, bottom = walk(node.left)
                top, bottom = top ** power.value, bottom ** power.value
                return (top, bottom) if sign == 1 else (bottom, top)
            (a, b), (c, d) = walk(node.left), walk(node.right)
            if isinstance(node.op, ast.Add):
                return a * d + c * b, b * d
            if isinstance(node.op, ast.Sub):
                return a * d - c * b, b * d
            if isinstance(node.op, ast.Mult):
                return a * c, b * d
            if isinstance(node.op, ast.Div):
                return a * d, b * c
        raise _formula_error(f'"{ast.get_source_segment(text.strip(), node) or text}" is not allowed in a system '
                             "formula.")

    top, bottom = walk(tree.body)
    if len(used) > 1:
        raise _formula_error("Use s or z in one formula, not both.")
    top, bottom = top.trim(), bottom.trim()
    if not np.any(bottom.coef):
        raise _formula_error("The bottom of the formula is 0.")
    return top.coef[::-1].copy(), bottom.coef[::-1].copy(), (used.pop() if used else None)


def _polynomial_text(coefficients, variable):
    """[1, 2, 5] -> "s**2 + 2*s + 5"."""
    c = np.atleast_1d(np.asarray(coefficients, dtype=float))
    n = len(c) - 1
    parts = []
    for i, value in enumerate(c):
        power = n - i
        if value == 0 and len(c) > 1:
            continue
        size = abs(value)
        term = variable if power == 1 else f"{variable}**{power}" if power > 1 else ""
        number = "" if (size == 1 and term) else _g(size)
        piece = f"{number}*{term}" if number and term else number or term
        parts.append((" - " if value < 0 else " + ") + piece)
    if not parts:
        return "0"
    text = "".join(parts)
    return ("-" + text[3:]) if text.startswith(" - ") else text[3:]


def _ratio_text(num, den, variable):
    top, bottom = _polynomial_text(num, variable), _polynomial_text(den, variable)
    if len(np.trim_zeros(np.asarray(num, dtype=float), "f")) > 1:
        top = f"({top})"
    if bottom == "1":
        return top
    return f"{top} / ({bottom})" if len(np.trim_zeros(np.asarray(den, dtype=float), "f")) > 1 else f"{top} / {bottom}"


def _pole_text(values):
    """-1 +/- 2i, -3 ..."""
    out, skip = [], set()
    values = list(values)
    for i, p in enumerate(values):
        if i in skip:
            continue
        if abs(p.imag) > 1e-12 * max(1.0, abs(p)):
            for j in range(i + 1, len(values)):
                if j not in skip and abs(values[j] - np.conj(p)) <= 1e-9 * max(1.0, abs(p)):
                    skip.add(j)
                    break
            out.append(f"{_g(p.real, 4)} +/- {_g(abs(p.imag), 4)}i")
        else:
            out.append(_g(p.real, 4))
    return ", ".join(out)


# ---------------------------------------------------------------------------------------- the System
class System:
    """A linear system with one input and one output. Make one with sdata.system(...).

    Words: step_response, impulse_response, response_to, frequency_response, poles, zeros, is_stable,
    steady_gain, in_steps, then, add, with_feedback, move_poles_to, table, chart.
    """

    _OLD_WORDS: dict = {}  # no old names (sdata.help reads this, as for tables and charts)

    def __init__(self, numerator, denominator, time_step=None, sos=None, label=None, units="radians per second",
                 designed=False):
        num = np.trim_zeros(np.atleast_1d(np.asarray(numerator, dtype=float)), "f")
        den = np.trim_zeros(np.atleast_1d(np.asarray(denominator, dtype=float)), "f")
        if not len(den):
            raise SimplydataError("The denominator of a system cannot be 0.")
        if not len(num):
            num = np.array([0.0])
        if len(num) > len(den):
            raise SimplydataError("The top of the formula has a higher power than the bottom (an improper system): "
                                  "no real system responds like that. Check the formula.")
        num, den = num / den[0], den / den[0]  # leading coefficient 1, as SciPy's TransferFunction
        # rounding noise from conversions (such as 4e-16 from ss2tf) is not a coefficient; coefficients SciPy designed
        # (a filter, sections) are kept whole: an analog filter's last coefficient is (2 pi x cutoff) ** order times
        # its first, so a relative trim would remove real coefficients
        if not designed:
            noise = 1e-13 * max(np.abs(num).max(), np.abs(den).max())
            num, den = np.where(np.abs(num) < noise, 0.0, num), np.where(np.abs(den) < noise, 0.0, den)
        num = np.trim_zeros(num, "f") if np.any(num) else np.array([0.0])
        self._num, self._den = num, den
        self._time_step = None if time_step is None else float(time_step)
        self._sos = sos
        self._label = label
        self._units = units

    # ------------------------------------------------------------------ basics
    @classmethod
    def from_coefficients(cls, numerator, denominator, time_step=None, sos=None, label=None):
        """A System from its coefficients (highest power first); used by sdata.frequency_filter."""
        return cls(numerator, denominator, time_step, sos, label,
                   units="cycles per second" if sos is not None or label else "radians per second", designed=True)

    @property
    def _variable(self):
        return "s" if self._time_step is None else "z"

    def _lti(self):
        from scipy import signal

        if self._time_step is None:
            return signal.lti(self._num, self._den)
        return signal.dlti(self._num, self._den, dt=self._time_step)

    def _poles(self):
        from scipy import signal

        if self._sos is not None:
            return signal.sos2zpk(self._sos)[1]
        return np.asarray(self._lti().poles, dtype=complex)

    def _zeros(self):
        from scipy import signal

        if self._sos is not None:
            return signal.sos2zpk(self._sos)[0]
        return np.asarray(self._lti().zeros, dtype=complex)

    def _stable(self):
        poles = self._poles()
        if not len(poles):
            return True
        if self._time_step is None:
            return bool(np.all(poles.real < -1e-12))
        return bool(np.all(np.abs(poles) < 1 - 1e-12))

    def _steady(self):
        point = 0.0 if self._time_step is None else 1.0
        top, bottom = np.polyval(self._num, point), np.polyval(self._den, point)
        if abs(bottom) < 1e-14 * max(1.0, np.abs(self._den).max()):
            return np.inf if abs(top) > 0 else np.nan
        return float(top / bottom)

    def _formula(self):
        return _ratio_text(self._num, self._den, self._variable)

    def _describe(self):
        kind = ("A continuous system" if self._time_step is None else
                f"A system in steps of {_g(self._time_step)}")
        if self._label:
            kind = (f"{self._label} as a continuous system" if self._time_step is None else
                    f"{self._label} as a system in steps of {_g(self._time_step)}")
        lines = [f"{kind}: output / input = {self._formula()}."]
        poles = self._poles()
        if len(poles):
            rule = ("every pole has a negative real part" if self._time_step is None else
                    "every pole lies inside the unit circle: its distance from 0 is below 1")
            stable = self._stable()
            lines.append(f"Poles {_pole_text(poles)}: " + (f"stable ({rule})." if stable else
                                                          "not stable (" + self._unstable_reason() + ")."))
        gain = self._steady()
        if np.isfinite(gain) and self._stable():
            lines.append(f"Steady gain {_g(gain, 4)}: a constant input of 1 settles at {_g(gain, 4)}.")
        return " ".join(lines)

    def _unstable_reason(self):
        poles = self._poles()
        if self._time_step is None:
            if np.any(poles.real > 1e-12):
                return "a pole has a positive real part, so the output grows without end"
            return "a pole lies on the imaginary axis, so the output never settles"
        if np.any(np.abs(poles) > 1 + 1e-12):
            return "a pole lies outside the unit circle, so the output grows without end"
        return "a pole lies on the unit circle, so the output never settles"

    def __repr__(self):
        return self._describe()

    @classmethod
    def _word_names(cls) -> list[str]:
        return list(WORDS)

    def __dir__(self):
        return list(WORDS)

    def __getattr__(self, name):
        from ._errors import MissingWordError, suggest

        if name.startswith("_"):
            raise AttributeError(name)
        lines = [f"A system has no word called .{name}()."]
        if name in HINTS:
            lines.append(f"In simplydata this is system.{HINTS[name]}.")
        else:
            guesses = suggest(name, list(WORDS))
            if guesses:
                lines.append("Did you mean " + " or ".join(f".{g}()" for g in guesses) + "?")
        lines.append("Every word for a system: " + ", ".join(WORDS))
        raise MissingWordError("\n".join(lines))

    def _result(self, data):
        import pandas as pd

        from .table import Table

        return Table(pd.DataFrame(data))

    # ------------------------------------------------------------------ responses
    def _times(self, until, how_many, time_points, step_name, from_zero=False):
        if time_points is not None:
            t = np.asarray(getattr(time_points, "_values", time_points), dtype=float).ravel()
            if len(t) < 2 or np.any(np.diff(t) <= 0):
                raise SimplydataError(f"{step_name}() needs time_points= as increasing times, such as "
                                      "time_points=sdata.number_list(0, to=5, step=0.01).")
            if not np.allclose(np.diff(t), t[1] - t[0], rtol=1e-6, atol=1e-12):
                raise SimplydataError(f"{step_name}() needs evenly spaced time_points= (SciPy works out the response "
                                      "in equal steps).")
            if from_zero and not np.isclose(t[0], 0, rtol=0, atol=1e-12 * max(1.0, abs(t[-1]))):
                raise SimplydataError(f"{step_name}() needs time_points= that start at 0, the moment the input "
                                      f"arrives (here they start at {_g(t[0])}). For a later part of the response, "
                                      f"use until= and keep the rows you want.")
            if from_zero and self._time_step is not None and not np.isclose(t[1] - t[0], self._time_step,
                                                                             rtol=1e-6, atol=0):
                raise SimplydataError(f"{step_name}() needs time_points= {_g(self._time_step)} apart, the system's "
                                      f"time step (here they are {_g(t[1] - t[0])} apart), such as time_points="
                                      f"sdata.number_list(0, to=5, step={_g(self._time_step)}).")
            return t
        if isinstance(how_many, bool) or not isinstance(how_many, (int, np.integer)) or how_many < 2:
            raise SimplydataError(f"{step_name}() needs how_many= as a whole number of 2 or more.")
        if until is None:
            return None
        if isinstance(until, bool) or not isinstance(until, (int, float)) or until <= 0:
            raise SimplydataError(f"{step_name}() needs until= as the last time, such as until=10.")
        if self._time_step is not None:
            return np.arange(int(np.floor(until / self._time_step + 1e-9)) + 1) * self._time_step
        return np.linspace(0, float(until), int(how_many))

    def _response(self, kind, until, how_many, time_points, step_name):
        from scipy import signal

        t = self._times(until, how_many, time_points, step_name, from_zero=True)
        if self._time_step is None:
            sys = self._lti()
            out = (signal.step if kind == "step" else signal.impulse)(sys, T=t, N=int(how_many))
            return np.asarray(out[0], dtype=float), np.asarray(out[1], dtype=float).ravel()
        n = int(how_many) if t is None else len(t)
        if self._sos is not None:
            u = np.ones(n) if kind == "step" else signal.unit_impulse(n)
            return np.arange(n) * self._time_step, signal.sosfilt(self._sos, u)
        out = (signal.dstep if kind == "step" else signal.dimpulse)(self._lti(), n=n)
        return np.asarray(out[0], dtype=float), np.asarray(out[1][0], dtype=float).ravel()

    @friendly(renamed={"steps": "how_many", "times": "time_points"})
    def step_response(self, until=None, how_many=200, time_points=None):
        """How the output answers an input that jumps from 0 to 1 and stays there.

        system.step_response(until=10)
        Gives back a table: time, output. until= is the last time (SciPy picks it from the poles when left
        out); how_many= how many time points (200; systems in steps use their own time step); time_points=
        your own evenly spaced times, starting at 0 (for a system in steps, its time step apart). Prints the
        final value, peak, overshoot, rise time (from the first time the output reaches 10 % of the final
        value to the first time it reaches 90 %) and settling time (the first time shown after which the
        output stays within 2 % of the final value), from python-control step_info on the times shown
        (no interpolation between them; needs simplydata[systems]). SciPy signal.step (dstep in steps),
        as R control::step(sys, t).
        """
        t, y = self._response("step", until, how_many, time_points, "step_response")
        sentence, measured = self._step_sentence(t, y)
        print(sentence)
        print("Method: SciPy signal." + ("step" if self._time_step is None else "dstep") +
              ", as R control::step(sys, t)" + ("; rise time, settling time and overshoot from python-control "
                                                "step_info(y, T, yfinal) on that response." if measured else "."))
        return self._result({"time": t, "output": y})

    def _step_sentence(self, t, y):
        """(sentence, whether python-control measured the response)."""
        final = self._steady()
        if not (self._stable() and np.isfinite(final)) or final == 0:
            return (f"Step response over {len(t)} times up to {_g(t[-1], 4)}: the output does not settle at a "
                    f"steady value (it reaches {_g(y[-1], 4)} at the last time)."), False
        parts = [f"Step response: the output settles at {_g(final, 4)}"]
        if _control() is None:
            return ", ".join(parts) + ". " + _control_note("Rise time, settling time and overshoot"), False
        info = step_info(t, y, final)
        if info["overshoot"] > 0:
            parts.append(f"peaks at {_g(info['peak'], 4)} at time {_g(info['peak time'], 4)} "
                         f"(overshoot {info['overshoot']:.1f} %)")
        if np.isfinite(info["rise time"]):
            parts.append(f"rise time {_g(info['rise time'], 4)} (10 % to 90 %)")
        else:
            parts.append("it has not reached 90 % of that by the last time shown (use a larger until=)")
        if np.isfinite(info["settling time"]):
            parts.append(f"settling time {_g(info['settling time'], 4)} (within 2 %)")
        else:
            parts.append("it has not settled within 2 % by the last time shown (use a larger until=)")
        return ", ".join(parts) + ".", True

    @friendly(renamed={"steps": "how_many", "times": "time_points"})
    def impulse_response(self, until=None, how_many=200, time_points=None):
        """How the output answers a short kick at time 0 (an impulse of size 1).

        system.impulse_response(until=10)
        Gives back a table: time, output. Options as step_response. SciPy signal.impulse (dimpulse in
        steps: a 1 at the first step), as R control::impulse(sys, t).
        """
        t, y = self._response("impulse", until, how_many, time_points, "impulse_response")
        biggest = int(np.argmax(np.abs(y)))
        print(f"Impulse response over {len(t)} times up to {_g(t[-1], 4)}: the biggest output is {_g(y[biggest], 4)} "
              f"at time {_g(t[biggest], 4)}; at the last time it is {_g(y[-1], 4)}.")
        print("Method: SciPy signal." + ("impulse" if self._time_step is None else "dimpulse") +
              ", as R control::impulse(sys, t).")
        return self._result({"time": t, "output": y})

    @friendly(renamed={"times": "time_points"})
    def response_to(self, inputs=None, time_points=None):
        """How the output answers any input you give: a simulation.

        system.response_to(sdata.make_wave("square", frequency=0.2, time_step=0.05, how_many=400))
        inputs= are the input values (Numbers or a list), one per time. time_points= are the times (evenly
        spaced); left out, they come from the time step the numbers remember (or the system's own
        time step). The system starts at rest and each input value holds until the next time (zero order
        hold). Gives back a table: time, input, output. SciPy signal.lsim(interp=False) (dlsim in steps;
        sosfilt for a frequency_filter), as R control::lsim(sys, u, t).
        """
        from scipy import signal

        if inputs is None:
            raise SimplydataError("response_to() needs inputs=, such as system.response_to(sdata.make_wave(\"square\", "
                                  "frequency=0.2, time_step=0.05, how_many=400)).")
        u = np.asarray(getattr(inputs, "_values", inputs), dtype=float).ravel()
        if len(u) < 2 or np.isnan(u).any():
            raise SimplydataError("response_to() needs at least 2 input values and no empty ones.")
        remembered = getattr(inputs, "_time_step", None)
        if time_points is None and self._time_step is not None and remembered is not None and                 not np.isclose(remembered, self._time_step, rtol=1e-6, atol=0):
            raise SimplydataError(f"The inputs remember a time step of {_g(remembered)}, but the system works in steps "
                                  f"of {_g(self._time_step)}. Change the inputs' time step first "
                                  f"(inputs.change_time_step(to={_g(self._time_step)})), or make the system for "
                                  f"steps of {_g(remembered)} (system.in_steps(time_step={_g(remembered)}) from the "
                                  "continuous system).")
        step = self._time_step if self._time_step is not None else remembered
        if time_points is None:
            if step is None:
                raise SimplydataError("response_to() needs time_points= (or inputs that remember their time step, "
                                      "such as sdata.make_wave(...)).")
            t = np.arange(len(u)) * step
        else:
            t = self._times(None, 2, time_points, "response_to")
            if len(t) != len(u):
                raise SimplydataError(f"response_to() needs one time point per input: {len(u)} inputs, {len(t)} time "
                                      "points.")
            if self._time_step is not None and not np.isclose(t[1] - t[0], self._time_step):
                raise SimplydataError(f"The time points must be {_g(self._time_step)} apart, the system's time step.")
        if self._time_step is None:
            y = signal.lsim(self._lti(), u, t, interp=False)[1]
            name = "lsim"
        elif self._sos is not None:
            y, name = signal.sosfilt(self._sos, u), "sosfilt"
        else:
            y = signal.dlsim(self._lti(), u, t=t)[1].ravel()
            name = "dlsim"
        y = np.asarray(y, dtype=float).ravel()
        print(f"Response to {len(u)} inputs up to time {_g(t[-1], 4)}, starting at rest: the output ends at "
              f"{_g(y[-1], 4)} (biggest size {_g(np.max(np.abs(y)), 4)}).")
        print(f"Method: SciPy signal.{name}, as R control::lsim(sys, u, t).")
        return self._result({"time": t, "input": u, "output": y})

    # ------------------------------------------------------------------ frequencies
    def _read_units(self, unit, step_name="frequency_response"):
        if unit is None:
            return self._units
        chosen = UNIT_SPELLINGS.get(str(unit).strip().lower(), str(unit).strip().lower())
        if chosen not in UNITS:
            raise choice_error(step_name, "unit", unit, list(UNITS))
        return chosen

    def _complex_response(self, w):
        """H at the angular frequencies w (radians per unit of time)."""
        from scipy import signal

        if self._time_step is None:
            return signal.freqresp(self._lti(), w=w)[1]
        fs = 1 / self._time_step
        f = w / (2 * np.pi)
        if self._sos is not None:
            return signal.sosfreqz(self._sos, worN=f, fs=fs)[1]
        # freqz reads coefficients as powers of 1/z: pad the top so both have the same length
        top = np.concatenate([np.zeros(len(self._den) - len(self._num)), self._num])
        return signal.freqz(top, self._den, worN=f, fs=fs)[1]

    def _default_w(self, how_many):
        from scipy import signal

        if self._time_step is None:
            return signal.findfreqs(self._num, self._den, int(how_many))
        nyquist = np.pi / self._time_step
        return np.logspace(np.log10(nyquist) - 3, np.log10(nyquist), int(how_many), endpoint=False)

    @friendly(renamed={"steps": "how_many", "units": "unit", "group_delay": "with_delay"})
    def frequency_response(self, between=None, how_many=200, unit=None, with_delay=False):
        """How much the system passes each frequency (gain) and how much it delays it (phase): the Bode data.

        system.frequency_response(between=[0.1, 100])
        Gives back a table: frequency, gain, gain (decibels), phase (degrees, unwrapped). between=[low, high]
        is the range (spaced evenly on a log scale; SciPy picks it from the poles and zeros when left out);
        how_many= how many frequencies (200). unit="radians per second" (the default for sdata.system, as R
        control and SciPy; 2 radians per second is 0.32 cycles per second) or "cycles per second" ("hertz"
        is accepted; cycles per unit of time, the default for sdata.frequency_filter).
        Prints the gain and phase margins (how far the system is from becoming unstable when a feedback
        loop is closed around it), read from the response. SciPy signal.freqresp (freqz / sosfreqz in
        steps), as R control::bode(sys, w). with_delay=True (a system in steps) adds the column delay: how long
        each frequency takes to get through (the group delay, SciPy signal.group_delay in steps, times the time
        step; as R gsignal::grpdelay).
        """
        units = self._read_units(unit)
        if not isinstance(with_delay, bool):
            raise SimplydataError("with_delay= needs True or False (no quotes).")
        if with_delay and self._time_step is None:
            raise SimplydataError("with_delay=True works on a system in steps (SciPy group_delay is for systems in "
                                  "steps): system.in_steps(time_step=0.01).frequency_response(with_delay=True).")
        scale = 1.0 if units == "radians per second" else 2 * np.pi
        if isinstance(how_many, bool) or not isinstance(how_many, (int, np.integer)) or how_many < 2:
            raise SimplydataError("frequency_response() needs how_many= as a whole number of 2 or more.")
        if between is None:
            w = self._default_w(how_many)
        else:
            if not (isinstance(between, (list, tuple)) and len(between) == 2 and 0 < between[0] < between[1]):
                raise SimplydataError("between= needs two frequencies above 0, the lower first, such as "
                                      "between=[0.1, 100].")
            w = np.logspace(np.log10(between[0] * scale), np.log10(between[1] * scale), int(how_many))
        if self._time_step is not None and w.max() > np.pi / self._time_step * (1 + 1e-9):
            raise SimplydataError(f"The highest frequency a system in steps of {_g(self._time_step)} can show is "
                                  f"{_g(np.pi / self._time_step / scale)} {units} (half the steps per unit of time).")
        h = self._complex_response(w)
        gain = np.abs(h)
        with np.errstate(divide="ignore"):
            decibels = 20 * np.log10(gain)
        phase = np.degrees(np.unwrap(np.angle(h)))
        print(f"Frequency response at {len(w)} frequencies from {_g(w[0] / scale, 4)} to {_g(w[-1] / scale, 4)} "
              f"{units}: the gain is {_g(gain[0], 4)} ({decibels[0]:.2f} decibels, dB) at the lowest and "
              f"{_g(gain[-1], 4)} ({decibels[-1]:.2f} dB) at the highest.")
        if not self._label:  # margins are about closing a feedback loop: not shown for a filter
            print(self._margin_sentence(units, scale))
        fn = "freqresp" if self._time_step is None else ("sosfreqz" if self._sos is not None else "freqz")
        columns = {"frequency": w / scale, "gain": gain, "gain (decibels)": decibels, "phase (degrees)": phase}
        extra = ""
        if with_delay:
            columns["delay"] = self._group_delay(w)
            extra = (f" The delay is SciPy signal.group_delay (in steps) times the time step {_g(self._time_step)}, "
                     "as R gsignal::grpdelay.")
        print(f"Method: SciPy signal.{fn}, as R control::bode(sys, w) (gain in decibels, phase in degrees).{extra}")
        return self._result(columns)

    def _group_delay(self, w):
        """The group delay in units of time at the angular frequencies w: SciPy signal.group_delay (in steps of the
        system) times the time step, added up over the second-order sections when the system has them (the
        multiplied-out formula of a steep or narrow filter loses the digits group_delay needs). Where SciPy finds the
        delay singular (the gain is 0 there) the delay is empty and the frequencies are named; where SciPy warns that
        the bottom of the formula is nearly 0, the frequencies are named too."""
        import warnings

        from scipy import signal

        if self._sos is not None:
            parts = [(row[:3], row[3:]) for row in np.asarray(self._sos, dtype=float)]
        else:
            parts = [(np.concatenate([np.zeros(len(self._den) - len(self._num)), self._num]), self._den)]
        delay = np.zeros(len(w))
        undefined, unsure = [], []
        for i, one in enumerate(np.asarray(w, dtype=float) * self._time_step):
            for b, a in parts:
                with warnings.catch_warnings(record=True) as said:
                    warnings.simplefilter("always")
                    delay[i] += signal.group_delay((b, a), w=[one])[1][0]
                text = " ".join(str(x.message) for x in said)
                if "is singular at" in text:
                    undefined.append(i)
                elif "extremely small" in text:
                    unsure.append(i)
        delay = delay * self._time_step
        scale = self._units == "cycles per second"
        shown = (lambda idx: ", ".join(_g(w[j] / (2 * np.pi) if scale else w[j], 4) for j in idx[:5])
                 + (" ..." if len(idx) > 5 else ""))
        if undefined:
            delay[sorted(set(undefined))] = np.nan
            print(f"Note: the delay is undefined at {shown(sorted(set(undefined)))} (the system passes nothing there: "
                  "SciPy group_delay finds it singular), so it is empty there.")
        if unsure:
            print(f"Note: SciPy group_delay warns that the bottom of the formula is nearly 0 near "
                  f"{shown(sorted(set(unsure)))}: the delay may not be exact there.")
        return delay

    def _margins(self):
        """(gain margin in dB, frequency, phase margin in degrees, frequency) in radians per unit of time;
        inf where the curve never crosses: python-control stability_margins (None without python-control)."""
        control = _control()
        if control is None:
            return None
        if self._time_step is None:
            sys = control.tf(self._num, self._den)
        else:
            sys = control.tf(self._num, self._den, self._time_step)
        return read_margins(control, sys)

    def _margin_sentence(self, units, scale):
        margins = self._margins()
        if margins is None:
            return _control_note("The gain and phase margins")
        gm, wg, pm, wp = margins
        if not np.isfinite(gm) and not np.isfinite(pm):
            return ("Margins: the phase never reaches -180 degrees and the gain never crosses 1 (0 decibels), so "
                    "both margins are without limit.")
        parts = []
        parts.append(f"gain margin {gm:.2f} decibels at {_g(wg / scale, 4)} {units}" if np.isfinite(gm) else
                     "gain margin without limit (the phase never reaches -180 degrees)")
        parts.append(f"phase margin {pm:.2f} degrees at {_g(wp / scale, 4)} {units}" if np.isfinite(pm) else
                     "phase margin without limit (the gain never crosses 1)")
        return "Margins: " + "; ".join(parts) + " (python-control stability_margins)."

    # ------------------------------------------------------------------ poles, stability
    def _pole_table(self, values, what):
        if self._time_step is None:
            s = values
        else:
            with np.errstate(divide="ignore", invalid="ignore"):
                s = np.log(values.astype(complex)) / self._time_step  # as R control::damp for discrete
        speed = np.abs(s)
        with np.errstate(divide="ignore", invalid="ignore"):
            damping = np.where(speed > 0, -s.real / speed, np.nan)
        data = {"real part": values.real, "imaginary part": values.imag, "distance from 0": np.abs(values),
                "damping ratio": damping, "natural frequency": speed}
        print(f"{len(values)} {what}" + (f": {_pole_text(values)}." if len(values) else "."))
        print("Method: SciPy (signal.lti / dlti " + what + "), as R control::pole / zero and damp(sys).")
        return self._result(data)

    @friendly
    def poles(self):
        """The poles: the values of s (or z) where the bottom of the formula is 0. They set how it moves.

        system.poles()
        Gives back a table: real part, imaginary part, distance from 0 (the size of the pole, also called its
        magnitude), damping ratio, natural frequency (radians per unit of time; for a system in steps worked
        out from log(pole) / time step, as R control::damp).
        """
        return self._pole_table(self._poles(), "poles")

    @friendly
    def zeros(self):
        """The zeros: the values of s (or z) where the top of the formula is 0 (inputs that do not get through).

        system.zeros()
        Gives back a table as poles().
        """
        return self._pole_table(self._zeros(), "zeros")

    @friendly
    def is_stable(self):
        """True when every response to a bounded input stays bounded (and settles). system.is_stable()

        Continuous: every pole has a negative real part. In steps: every pole lies inside the unit circle
        (distance from 0 below 1). A pole on the edge (real part 0, or distance 1) is not stable: the output
        never settles.
        """
        stable = self._stable()
        rule = ("every pole has a negative real part" if self._time_step is None else
                "every pole lies inside the unit circle: its distance from 0 is below 1")
        print(f"Stable: {rule}." if stable else f"Not stable: {self._unstable_reason()}.")
        return stable

    @friendly
    def steady_gain(self):
        """Where the output settles for a constant input of 1 (the DC gain). system.steady_gain()

        The formula at s = 0 (z = 1 in steps), as R control::dcgain(sys).
        """
        gain = self._steady()
        if not np.isfinite(gain):
            print("The steady gain is without limit: the output keeps growing for a constant input (a pole at "
                  + ("s = 0)." if self._time_step is None else "z = 1)."))
        elif not self._stable():
            print(f"The formula gives {_g(gain, 6)} at " + ("s = 0" if self._time_step is None else "z = 1") +
                  ", but the system is not stable, so the output never settles there.")
        else:
            print(f"Steady gain {_g(gain, 6)}: a constant input of 1 settles at {_g(gain, 6)}. (As R control::dcgain.)")
        return gain

    # ------------------------------------------------------------------ new systems
    @friendly(renamed={"method": "test_method"})
    def in_steps(self, time_step=None, test_method="zero order hold"):
        """The same system in steps of time_step (discrete time), for a computer that reads and acts in steps.

        system.in_steps(time_step=0.1)
        test_method="zero order hold" (the input stays constant between steps; R control::c2d(sys, 0.1)),
        "bilinear" ("tustin"; as R signal::bilinear), "forward difference" ("euler") or "backward
        difference". SciPy signal.cont2discrete.
        """
        from scipy import signal

        if self._time_step is not None:
            raise SimplydataError("This system is already in steps.")
        if isinstance(time_step, bool) or not isinstance(time_step, (int, float)) or time_step <= 0:
            raise SimplydataError("in_steps() needs time_step= as the time between steps, such as "
                                  "system.in_steps(time_step=0.1).")
        chosen = METHOD_SPELLINGS.get(str(test_method).strip().lower(), str(test_method).strip().lower())
        if chosen not in DISCRETE_METHODS:
            raise choice_error("in_steps", "test_method", test_method, list(DISCRETE_METHODS))
        num, den, _ = signal.cont2discrete((self._num, self._den), float(time_step), method=DISCRETE_METHODS[chosen])
        made = System(np.asarray(num, dtype=float).ravel(), den, time_step=float(time_step))
        print(f"In steps of {_g(time_step)} ({chosen}): output / input = {made._formula()}.")
        print(f"Method: SciPy signal.cont2discrete(method=\"{DISCRETE_METHODS[chosen]}\")" +
              (", as R control::c2d(sys, " + _g(time_step) + ")." if chosen == "zero order hold" else "."))
        return made

    def _other(self, other, step_name):
        if isinstance(other, (int, float)) and not isinstance(other, bool):
            return System([float(other)], [1.0], time_step=self._time_step)
        if not isinstance(other, System):
            raise SimplydataError(f"{step_name}() needs another system (sdata.system(...)) or a number.")
        if (self._time_step is None) != (other._time_step is None) or (
                self._time_step is not None and not np.isclose(self._time_step, other._time_step)):
            raise SimplydataError(f"{step_name}() needs two systems of the same kind: both continuous, or both in "
                                  "the same steps (system.in_steps(time_step=...)).")
        return other

    def _joined(self, num, den, words, r_call):
        made = System(num, den, time_step=self._time_step)
        print(f"{words}: output / input = {made._formula()}.")
        print(f"Method: polynomial arithmetic (numpy.polynomial), as R {r_call}.")
        return made

    @friendly
    def then(self, other):
        """This system, then another one after it (in series): the output of this one feeds the other.

        system.then(sdata.system("1 / s"))
        The formulas multiply, as R control::series(sys1, sys2).
        """
        other = self._other(other, "then")
        return self._joined(np.polymul(self._num, other._num), np.polymul(self._den, other._den),
                            "In series", "control::series(sys1, sys2)")

    @friendly
    def add(self, other):
        """This system and another side by side, their outputs added (in parallel): both get the same input.

        system.add(sdata.system("1 / (s + 3)"))
        The formulas add, as R control::parallel(sys1, sys2). (To put one after the other, use then.)
        """
        other = self._other(other, "add")
        num = np.polyadd(np.polymul(self._num, other._den), np.polymul(other._num, self._den))
        return self._joined(num, np.polymul(self._den, other._den),
                            "Side by side, outputs added (in parallel)", "control::parallel(sys1, sys2)")

    @friendly(renamed={"other": "through"})
    def with_feedback(self, through=1, sign="negative"):
        """The closed loop: the output is fed back (through a sensor, say) and taken from the input.

        system.with_feedback()   system.with_feedback(through=sdata.system("1 / (0.1*s + 1)"))
        through= is the system in the feedback path (1: the output itself). sign="negative" (the usual
        loop, G / (1 + G H)) or "positive" (G / (1 - G H)). As R control::feedback(sys1, sys2).
        """
        if sign not in ("negative", "positive"):
            raise choice_error("with_feedback", "sign", sign, ["negative", "positive"])
        other = self._other(through, "with_feedback")
        num = np.polymul(self._num, other._den)
        loop = np.polymul(self._num, other._num)
        den = np.polyadd(np.polymul(self._den, other._den), loop if sign == "negative" else -loop)
        return self._joined(num, den, f"With {sign} feedback", "control::feedback(sys1, sys2" +
                            (", +1)" if sign == "positive" else ")"))

    @friendly(renamed={"poles": "to", "places": "to"})
    def move_poles_to(self, to=None):
        """The system with its poles moved to new places by feeding back its inner state (pole placement).

        system.move_poles_to([-2, -3])
        to= the new poles, one for each pole of the system (complex ones in pairs, such as [-1+2j, -1-2j]).
        The system is written in state space (SciPy tf2ss, controller form) and SciPy signal.place_poles finds the
        gains K of the feedback u = r - K x (x the inner state, r the new input); the new system is
        x' = (A - B K) x + B r, y = (C - D K) x + D r (SciPy ss2tf). Prints the gains, in the order of the state
        of system.table(form="state space"). Gives back the new System.
        """
        from scipy import signal

        if to is None:
            raise SimplydataError("move_poles_to() needs the new poles, such as system.move_poles_to([-2, -3]).")
        wanted = np.atleast_1d(np.asarray(to, dtype=complex))
        a, b, c, d = signal.tf2ss(self._num, self._den)
        if len(wanted) != a.shape[0]:
            raise SimplydataError(f"move_poles_to() needs {a.shape[0]} poles, one for each pole of the system; you "
                                  f"gave {len(wanted)}.")
        if not np.allclose(np.sort_complex(wanted), np.sort_complex(np.conj(wanted))):
            raise SimplydataError("Complex poles must come in pairs (such as -1+2j and -1-2j).")
        if self._time_step is not None and np.any(np.abs(wanted) >= 1):
            print("Note: a pole at a distance of 1 or more from 0 makes a system in steps unstable.")
        wanted = np.real_if_close(wanted)
        if len(np.unique(np.round(np.atleast_1d(wanted), 12))) < len(np.atleast_1d(wanted)):
            raise SimplydataError("SciPy place_poles cannot put a pole in the same place twice for a system with one "
                                  "input (each pole may be given once). Give poles a little apart, such as "
                                  "[-2, -2.01]. "
                                  "(R control::acker allows repeated poles; SciPy has no acker.)")
        try:
            placed = signal.place_poles(a, b, wanted)
        except ValueError as error:
            raise SimplydataError(f"SciPy place_poles could not place those poles ({error}).") from None
        k = np.asarray(placed.gain_matrix, dtype=float)
        num, den = signal.ss2tf(a - b @ k, b, c - d @ k, d)
        made = System(np.asarray(num, dtype=float).ravel(), den, time_step=self._time_step)
        print(f"Moved the poles to {_pole_text(np.asarray(placed.computed_poles, dtype=complex))} with the gains "
              + ", ".join(_g(v, 6) for v in k.ravel()) + f": output / input = {made._formula()}.")
        print("Method: SciPy signal.place_poles on the state-space form (signal.tf2ss), then signal.ss2tf; the new "
              "system's steady gain changes too (check it with steady_gain()).")
        return made

    # ------------------------------------------------------------------ table and chart
    @friendly
    def table(self, form="transfer function"):
        """The system as numbers: form="transfer function" (the coefficients of the top and the bottom,
        highest power first: power of s (power of z in steps), numerator, denominator), "state space" (the
        matrices A, B, C, D in controller form: matrix, row, column, value; SciPy tf2ss, as R control::tf2ss),
        "poles and zeros" (kind, real part, imaginary part; the last row is the gain), "sections" (second-order
        sections, one row each: numerator 1 to 3 and denominator 1 to 3, highest power first, as SciPy's sos rows;
        SciPy tf2sos, or the filter's own sections, as R gsignal::tf2sos) or "partial fractions" (the formula as
        a sum of residue / (s - pole) terms, plus any direct terms: SciPy residue, residuez in steps, as R
        gsignal::residue and residuez). system.table()
        """
        from scipy import signal

        if isinstance(form, str):
            form = FORM_SPELLINGS.get(form.strip().lower(), form)
        if form not in FORMS:
            raise choice_error("table", "form", form, list(FORMS))
        if form == "sections":
            if self._time_step is None:
                raise SimplydataError('form="sections" is for a system in steps (second-order sections run on '
                                      "readings): system.in_steps(time_step=0.1).table(form=\"sections\").")
            delay = 0
            if self._sos is not None:
                sos = self._sos
            else:
                # SciPy's sections are in powers of 1/z, and tf2sos and zpk2sos both drop the delay of a top shorter
                # than the bottom (tf2sos strips the leading zeros of the padded top). So the sections are SciPy
                # zpk2sos of the poles and zeros (tf2zpk), followed by one section [0, 0, 1 | 1, 0, 0] (two steps
                # of delay) or [0, 1, 0 | 1, 0, 0] (one step) for each step the top is shorter: exactly the formula.
                sos = signal.zpk2sos(*signal.tf2zpk(self._num, self._den))
                delay = len(self._den) - len(self._num)
                rows = [[0.0, 0.0, 1.0, 1.0, 0.0, 0.0]] * (delay // 2) + [[0.0, 1.0, 0.0, 1.0, 0.0, 0.0]] * (delay % 2)
                if rows:
                    sos = np.vstack([sos, rows])
            sos = np.atleast_2d(np.asarray(sos, dtype=float))
            data = {"section": list(range(1, len(sos) + 1))}
            for i in range(3):
                data[f"numerator {i + 1}"] = sos[:, i]
            for i in range(3):
                data[f"denominator {i + 1}"] = sos[:, 3 + i]
            print(f"{len(sos)} second-order section{'s' if len(sos) != 1 else ''}, run one after the other "
                  "(SciPy " + ("sections of the filter)." if self._sos is not None else "signal.zpk2sos of tf2zpk)")
                  + (f"; the last {'one is' if (delay + 1) // 2 == 1 else str((delay + 1) // 2) + ' are'} the delay of "
                     f"{delay} step{'s' if delay != 1 else ''} (the top of the formula is shorter than the bottom)."
                     if delay else ""))
            return self._result(data)
        if form == "partial fractions":
            return self._partial_fractions()
        if form == "transfer function":
            n = len(self._den)
            top = np.concatenate([np.zeros(n - len(self._num)), self._num])
            return self._result({f"power of {self._variable}": list(range(n - 1, -1, -1)), "numerator": top,
                                 "denominator": self._den})
        if form == "state space":
            a, b, c, d = signal.tf2ss(self._num, self._den)
            rows = []
            for name, m in (("A", a), ("B", b), ("C", c), ("D", d)):
                for i in range(m.shape[0]):
                    for j in range(m.shape[1]):
                        rows.append((name, i + 1, j + 1, float(m[i, j])))
            return self._result({"matrix": [r[0] for r in rows], "row": [r[1] for r in rows],
                                 "column": [r[2] for r in rows], "value": [r[3] for r in rows]})
        if self._sos is not None:
            z, p, k = signal.sos2zpk(self._sos)
        else:
            z, p, k = signal.tf2zpk(self._num, self._den)
        kinds = ["zero"] * len(z) + ["pole"] * len(p) + ["gain"]
        values = list(z) + list(p) + [complex(k)]
        print("The last row is the gain, the number in front of the formula.")
        return self._result({"kind": kinds, "real part": [v.real for v in values],
                             "imaginary part": [v.imag for v in values]})

    def _partial_fractions(self):
        """The partial fractions: SciPy residue (residuez for a system in steps)."""
        from scipy import signal

        if self._time_step is None:
            r, p, k = signal.residue(self._num, self._den)
            fn, term = "residue", "residue / (s - pole)"
        else:
            top = np.concatenate([np.zeros(len(self._den) - len(self._num)), self._num])
            r, p, k = signal.residuez(top, self._den)
            fn, term = "residuez", "residue / (1 - pole / z)"
        r, p, k = np.asarray(r, dtype=complex), np.asarray(p, dtype=complex), np.atleast_1d(np.asarray(k, dtype=float))
        kinds = ["fraction"] * len(r) + ["direct term"] * len(k)
        power = [np.nan] * len(r) + list(range(len(k) - 1, -1, -1) if self._time_step is None else range(len(k)))
        data = {"kind": kinds, "residue (real part)": list(r.real) + list(k),
                "residue (imaginary part)": list(r.imag) + [0.0] * len(k),
                "pole (real part)": list(p.real) + [np.nan] * len(k),
                "pole (imaginary part)": list(p.imag) + [np.nan] * len(k),
                "power": power}
        print(f"The formula as {len(r)} fraction{'s' if len(r) != 1 else ''} {term}" +
              (f" plus {len(k)} direct term{'s' if len(k) != 1 else ''} (power: of "
               + ("s" if self._time_step is None else "1/z") + ")" if len(k) else "") +
              f". Method: SciPy signal.{fn}, as R gsignal::{fn}.")
        return self._result(data)

    @friendly(renamed={"units": "unit"})
    def chart(self, show="bode", between=None, until=None, unit=None):
        """A chart of the system: show="bode" (gain in decibels and phase against frequency on a log scale,
        two panels; "gain and phase" is accepted), "step", "impulse", "poles and zeros" (x for poles, o for
        zeros; the unit circle for a system in steps; "pole-zero" is accepted) or "nyquist" (the frequency
        response as one curve; a feedback loop is stable when it stays clear of -1). system.chart()

        between= (frequencies, with "bode") and unit= as in frequency_response; until= (the last time, with
        "step" and "impulse") as in step_response. Gives back a chart (or a page of two charts for "bode"):
        .save("bode.png") or .show().
        """
        import contextlib
        import io

        import pandas as pd

        from .chart import Chart
        from .words.layout import put_one_above_other

        show = CHART_SPELLINGS.get(str(show).strip().lower(), show) if isinstance(show, str) else show
        if show not in CHARTS:
            raise choice_error("chart", "show", show, list(CHARTS))
        for option, value, fits in (("between", between, ("bode",)), ("unit", unit, ("bode",)),
                                    ("until", until, ("step", "impulse"))):
            if value is not None and show not in fits:
                raise SimplydataError(f'{option}= goes with show=' + " or ".join(f'"{f}"' for f in fits) +
                                      f'; the chart show="{show}" does not use it.')
        quiet = io.StringIO()
        if show in ("step", "impulse"):
            with contextlib.redirect_stdout(quiet):
                got = (self.step_response if show == "step" else self.impulse_response)(until=until)
            frame = got._frame.to_pandas() if hasattr(got._frame, "to_pandas") else got._frame
            made = Chart(frame).draw_lines(x="time", y="output")
            if show == "step" and self._stable() and np.isfinite(self._steady()):
                made.draw_line_at_y(self._steady(), labelled="settles at")
            return made.write_title_on_top("Step response" if show == "step" else "Impulse response")
        if show == "bode":
            shown = self._read_units(unit, "chart")
            with contextlib.redirect_stdout(quiet):
                got = self.frequency_response(between=between, unit=shown)
            frame = got._frame.to_pandas() if hasattr(got._frame, "to_pandas") else got._frame
            top = Chart(frame).draw_lines(x="frequency", y="gain (decibels)").use_log_scale_x().label_x(
                f"frequency ({shown})")
            bottom = Chart(frame).draw_lines(x="frequency", y="phase (degrees)").use_log_scale_x().label_x(
                f"frequency ({shown})")
            return put_one_above_other(top, bottom, same_x=True)
        if show == "poles and zeros":
            poles, zeros = self._poles(), self._zeros()
            frame = pd.DataFrame({"real part": np.concatenate([poles.real, zeros.real]),
                                  "imaginary part": np.concatenate([poles.imag, zeros.imag])})
            made = Chart(frame)
            made._need_axes("pole_zero")
            return made._add("pole_zero", "draw", _draw_pole_zero, poles=poles, zeros=zeros,
                             circle=self._time_step is not None).write_title_on_top("Poles (x) and zeros (o)")
        w = self._default_w(400)
        h = self._complex_response(w)
        frame = pd.DataFrame({"real part": h.real, "imaginary part": h.imag})
        made = Chart(frame)
        made._need_axes("nyquist")
        return made._add("nyquist", "draw", _draw_nyquist, h=h).write_title_on_top("Nyquist curve")


def _draw_pole_zero(ctx, poles, zeros, circle):
    import matplotlib

    ax = ctx.ax
    colour = matplotlib.rcParams["axes.prop_cycle"].by_key()["color"]
    if circle:
        angle = np.linspace(0, 2 * np.pi, 361)
        ax.plot(np.cos(angle), np.sin(angle), linestyle="--", color="grey", linewidth=1)
        ax.set_aspect("equal", adjustable="datalim")
    ax.axhline(0, color="grey", linewidth=0.8)
    ax.axvline(0, color="grey", linewidth=0.8)
    ax.scatter(poles.real, poles.imag, marker="x", s=80, color=colour[0], label="poles", zorder=3)
    if len(zeros):
        ax.scatter(zeros.real, zeros.imag, marker="o", s=80, facecolors="none", edgecolors=colour[1], label="zeros",
                   zorder=3)
    ax.set_xlabel("real part")
    ax.set_ylabel("imaginary part")
    ax.legend()


def _draw_nyquist(ctx, h):
    import matplotlib

    ax = ctx.ax
    colour = matplotlib.rcParams["axes.prop_cycle"].by_key()["color"][0]
    ax.plot(h.real, h.imag, color=colour, linewidth=2, label="positive frequencies")
    ax.plot(h.real, -h.imag, color=colour, linewidth=1.2, linestyle="--", label="negative frequencies")
    ax.scatter([-1], [0], marker="+", s=120, color="red", zorder=3, label="-1")
    ax.set_xlabel("real part")
    ax.set_ylabel("imaginary part")
    ax.legend()


# ---------------------------------------------------------------------------------------- python-control
def _control():
    """The python-control package (simplydata[systems]), or None when it is not installed."""
    try:
        import control
    except ImportError:
        return None
    return control


def _control_note(what) -> str:
    return (f"Note: {what} come from python-control (the established Python package for control systems), "
            'which is not installed here: pip install "simplydata[systems]" (or pip install control), then '
            "restart Python.")


def step_info(t, y, final):
    """Rise time (10 % to 90 % of final), settling time (within 2 %), peak, peak time and overshoot (%):
    python-control step_info on the response as given (its rules: the first sample at or past each level,
    no interpolation). Needs python-control."""
    import warnings

    control = _control()
    t, y = np.asarray(t, dtype=float), np.asarray(y, dtype=float)
    sign = 1.0 if final > 0 else -1.0
    if not np.any(sign * y >= 0.9 * abs(final)):
        # python-control step_info needs the response to reach 90 % of the final value
        top = int(np.argmax(sign * y))
        return {"rise time": np.nan, "settling time": np.nan, "peak": y[top], "peak time": t[top], "overshoot": 0.0}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        info = control.step_info(y, T=t, yfinal=final, SettlingTimeThreshold=0.02, RiseTimeLimits=(0.1, 0.9))
    at = int(np.argmin(np.abs(t - info["PeakTime"])))
    return {"rise time": info["RiseTime"], "settling time": info["SettlingTime"], "peak": y[at],
            "peak time": info["PeakTime"], "overshoot": info["Overshoot"]}


def read_margins(control, sys):
    """(gain margin in dB, its frequency, phase margin in degrees, its frequency) from python-control
    stability_margins: the smallest of each, inf (and nan frequency) where the curve never crosses."""
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        gm, pm, _, wpc, wgc, _ = control.stability_margins(sys)
    gm, pm = float(gm), float(pm)
    decibels = 20 * np.log10(gm) if np.isfinite(gm) else np.inf
    return decibels, float(wpc), pm, float(wgc)


# ---------------------------------------------------------------------------------------- sdata words
@friendly(renamed={"sos": "sections", "residue": "residues", "k": "direct_terms"})
def system(formula=None, numerator=None, denominator=None, poles=None, zeros=None, gain=1, a=None, b=None, c=None,
           d=None, time_step=None, A=None, B=None, C=None, D=None, num=None, den=None, sections=None, residues=None,
           direct_terms=None):
    """A linear system (one input, one output) from its formula, coefficients, poles or matrices.

    sdata.system("1 / (s**2 + 2*s + 5)")
    The formula is a ratio of polynomials in s (continuous time) or z (in steps of time_step=):
    sdata.system("0.1 / (z - 0.9)", time_step=0.1). Or numerator= and denominator= (highest power first,
    as R control::tf and SciPy; num= and den=, as in R and MATLAB, are accepted), poles= and zeros= with
    gain= (the number in front of the formula, not the steady gain), or the state-space matrices a=, b=,
    c=, d= (A= to D= are accepted). sections= (with time_step=) is a filter as second-order sections, one row
    of six numbers each, as system.table(form="sections") gives them (SciPy sos2tf). residues= with poles=
    (and direct_terms=) builds the formula back from its partial fractions, as system.table(form="partial
    fractions") gives them (SciPy invres; invresz with time_step=). Prints the formula, the poles and whether it
    is stable. Words on it: step_response, impulse_response, response_to, frequency_response, poles, zeros,
    is_stable, steady_gain, in_steps, then, add, with_feedback, move_poles_to, table, chart. SciPy signal.lti /
    dlti, as R control::tf.
    """
    from scipy import signal

    spellings = (("numerator", numerator, "num", num), ("denominator", denominator, "den", den), ("a", a, "A", A),
                 ("b", b, "B", B), ("c", c, "C", C), ("d", d, "D", D))
    for main, value, other, other_value in spellings:
        if value is not None and other_value is not None:
            raise SimplydataError(f"Give {main}= or {other}= (two spellings of the same option), not both.")
    numerator = numerator if numerator is not None else num
    denominator = denominator if denominator is not None else den
    a, b, c, d = (x if x is not None else y for x, y in ((a, A), (b, B), (c, C), (d, D)))
    if time_step is not None and (isinstance(time_step, bool) or not isinstance(time_step, (int, float))
                                  or time_step <= 0):
        raise SimplydataError("time_step= needs a number above 0: the time between steps.")
    if direct_terms is not None and residues is None:
        raise SimplydataError("direct_terms= goes with residues= and poles=.")
    if residues is not None:
        if poles is None or zeros is not None or formula is not None or numerator is not None or sections is not None:
            raise SimplydataError("residues= goes with poles= (and direct_terms=) only, as system.table(form=\"partial "
                                  "fractions\") gives them.")
        return _from_partial_fractions(residues, poles, direct_terms, time_step)
    if sections is not None:
        if any(x is not None for x in (formula, numerator, denominator, poles, zeros, a, b, c, d)):
            raise SimplydataError("sections= makes a system on its own: leave out the other ways.")
        return _from_sections(sections, time_step)
    ways = [formula is not None, numerator is not None or denominator is not None,
            poles is not None or zeros is not None, any(x is not None for x in (a, b, c, d))]
    if sum(ways) != 1:
        raise SimplydataError("sdata.system() needs one of: a formula, numerator= and denominator=, poles= (and "
                              "zeros=), a=, b=, c=, d=, sections= or residues= with poles=.\nFor example, "
                              + FORMULA_EXAMPLE)
    if formula is not None:
        num_, den_, variable = read_system_formula(formula)
        if variable == "z" and time_step is None:
            raise _formula_error("A formula in z is a system in steps: give time_step=, such as "
                                 'sdata.system("0.1 / (z - 0.9)", time_step=0.1).')
        if variable == "s" and time_step is not None:
            raise _formula_error("A formula in s is a continuous system: leave out time_step= (or write the formula "
                                 "in z), or turn it into steps with system.in_steps(time_step=...).")
    elif ways[1]:
        if numerator is None or denominator is None:
            raise SimplydataError("sdata.system() needs both numerator= and denominator=, such as numerator=[1], "
                                  "denominator=[1, 2, 5].")
        num_, den_ = np.atleast_1d(np.asarray(numerator, dtype=float)), np.atleast_1d(np.asarray(denominator,
                                                                                              dtype=float))
    elif ways[2]:
        zeros = [] if zeros is None else zeros
        poles = [] if poles is None else poles
        num_, den_ = signal.zpk2tf(np.asarray(zeros, dtype=complex), np.asarray(poles, dtype=complex), float(gain))
        num_, den_ = np.real_if_close(num_), np.real_if_close(den_)
        if np.iscomplexobj(num_) or np.iscomplexobj(den_):
            raise SimplydataError("Complex poles and zeros must come in pairs (such as -1+2j and -1-2j).")
    else:
        if any(x is None for x in (a, b, c)):
            raise SimplydataError("A state-space system needs a=, b= and c= (d= is 0 when left out).")
        a_, b_, c_ = (np.atleast_2d(np.asarray(x, dtype=float)) for x in (a, b, c))
        d_ = np.zeros((c_.shape[0], b_.shape[1])) if d is None else np.atleast_2d(np.asarray(d, dtype=float))
        if b_.shape[1] != 1 or c_.shape[0] != 1:
            raise SimplydataError("simplydata's systems have one input and one output: b= needs one column and c= "
                                  "one row. (Systems with several inputs or outputs come with matrices in a later "
                                  "version.)")
        num_, den_ = signal.ss2tf(a_, b_, c_, d_)
        num_ = num_.ravel()
    made = System(num_, den_, time_step=time_step)
    print(made._describe())
    if ways[2]:
        steady = made._steady()
        line = f"gain={_g(gain, 6)} is the number in front of the formula"
        if np.isfinite(steady) and made._stable() and not np.isclose(steady, float(gain)):
            line += f"; the steady gain is {_g(steady, 4)}"
        print(line + ".")
    print("Method: SciPy signal." + ("lti" if time_step is None else "dlti") + ", as R control::tf(num, den" +
          ("" if time_step is None else f", {_g(time_step)}") + ").")
    return made


def _from_sections(sections, time_step):
    """sdata.system(sections=...): SciPy sos2tf (the System runs the sections themselves)."""
    from scipy import signal

    if time_step is None:
        raise SimplydataError("sections= is a filter in steps: give time_step=, such as sdata.system(sections=rows, "
                              "time_step=0.005).")
    frame = getattr(sections, "_frame", None)
    if frame is not None:  # the table of system.table(form="sections"): its section column is a count, not a number
        frame = frame.to_pandas() if hasattr(frame, "to_pandas") else frame
        frame = frame.drop(columns=[c for c in ("section",) if c in frame.columns])
        sections = frame.to_numpy()
    # a C-ordered copy: SciPy's sosfilt needs one it can use, and a table gives a read-only or column-ordered array
    sos = np.atleast_2d(np.array(getattr(sections, "_values", sections), dtype=float, order="C"))
    if sos.ndim != 2 or sos.shape[1] != 6:
        raise SimplydataError("sections= needs one row of six numbers for each section (numerator 1 to 3, denominator "
                              "1 to 3), as system.table(form=\"sections\") gives them.")
    if np.any(sos[:, 3] == 0):
        raise SimplydataError("The first denominator number of each section (denominator 1) cannot be 0.")
    num, den = signal.sos2tf(sos)
    made = System(num, den, time_step=float(time_step), sos=sos, designed=True)
    print(made._describe())
    print(f"Method: SciPy signal.sos2tf ({len(sos)} sections; the system runs them one after the other, as R "
          "gsignal::sos2tf).")
    return made


def _from_partial_fractions(residues, poles, direct_terms, time_step):
    """sdata.system(residues=, poles=, direct_terms=): SciPy invres (invresz in steps)."""
    from scipy import signal

    r = np.atleast_1d(np.asarray(residues, dtype=complex))
    p = np.atleast_1d(np.asarray(poles, dtype=complex))
    k = np.atleast_1d(np.asarray([] if direct_terms is None else direct_terms, dtype=float))
    if len(r) != len(p) or not len(r):
        raise SimplydataError("residues= and poles= need the same number of values, one residue for each pole.")
    fn = "invres" if time_step is None else "invresz"
    num, den = getattr(signal, fn)(r, p, k)
    num, den = np.real_if_close(num), np.real_if_close(den)
    if np.iscomplexobj(num) or np.iscomplexobj(den):
        raise SimplydataError("Complex poles (and their residues) must come in pairs, such as -1+2j and -1-2j.")
    if time_step is not None:  # invresz gives powers of 1/z: as powers of z, the same numbers over the same length
        size = max(len(num), len(den))
        num = np.concatenate([num, np.zeros(size - len(num))])
        den = np.concatenate([den, np.zeros(size - len(den))])
    made = System(np.asarray(num, dtype=float), np.asarray(den, dtype=float), time_step=time_step)
    print(made._describe())
    print(f"Method: SciPy signal.{fn} (the partial fractions added up)"
          + (", as R gsignal::rresidue." if time_step is None else "."))
    return made


@friendly(renamed={"method": "test_method", "numtaps": "how_many_weights"})
def frequency_filter(keep_below=None, keep_above=None, keep_between=None, remove_between=None, remove_at=None,
                     time_step=None, test_method="butterworth", steepness=4, ripple=0.5, removed_by=40, width=1,
                     and_multiples=False, sampling_rate=None, fs=None, how_many_weights=None, window_shape="hamming",
                     transition_width=None, find_order_for=None, with_least_delay=False, analog=False):
    """The filter of add_filtered_column as a system in steps, to look at before using it.

    sdata.frequency_filter(keep_below=10, time_step=0.005)
    One condition (keep_below=, keep_above=, keep_between=, remove_between=, remove_at=) and the options of
    numbers.keep_each_frequency_that (test_method= with the FIR filters, steepness=, how_many_weights=,
    transition_width=, find_order_for={"loss_at": 20}, ...). Gives back a System:
    .frequency_response() (in cycles per unit of time), .chart() (the Bode chart), .poles(), .table(),
    .response_to(numbers) (forwards only, from rest, as both_ways=False). analog=True gives the continuous
    (analog) filter instead, with no time_step=: SciPy's design with analog=True (the prototypes buttap,
    cheb1ap, cheb2ap, ellipap, besselap moved to the cutoff by lp2lp, lp2hp, lp2bp or lp2bs).
    """
    from . import _filters
    from ._time_axis import read_time_step

    if not isinstance(analog, bool):
        raise SimplydataError("analog= needs True or False (no quotes).")
    if analog:
        return _analog_filter(keep_below, keep_above, keep_between, remove_between, remove_at, time_step,
                              sampling_rate, fs, test_method, steepness, ripple, removed_by, find_order_for)

    given = [(k, v) for k, v in (("keep_below", keep_below), ("keep_above", keep_above), ("keep_between", keep_between),
                                 ("remove_between", remove_between), ("remove_at", remove_at)) if v is not None]
    if len(given) != 1:
        raise SimplydataError("frequency_filter() needs exactly one of keep_below=, keep_above=, keep_between=, "
                              "remove_between= or remove_at=, such as sdata.frequency_filter(keep_below=10, "
                              "time_step=0.005).")
    step, _ = read_time_step(time_step, sampling_rate, fs, None, "frequency_filter")
    option, value = given[0]
    if option == "remove_at":
        made = _filters.design_single(False, value, step, width, and_multiples, "frequency_filter")
    else:
        if option.endswith("between") and not (isinstance(value, (list, tuple)) and len(value) == 2
                                                and value[0] < value[1]):
            raise SimplydataError(f"{option}= needs two frequencies, the lower first, such as {option}=[1, 5].")
        kind = {"keep_below": "low", "keep_above": "high", "keep_between": "pass", "remove_between": "stop"}[option]
        chosen = _filters.read_method(test_method, "frequency_filter")
        made = _filters.design(kind, value, step, chosen, steepness, ripple, removed_by, how_many_weights, window_shape,
                               step_name="frequency_filter", transition_width=transition_width,
                               find_order_for=find_order_for, with_least_delay=with_least_delay)
    b, a = _filters.coefficients(made)
    what = (f"between {value[0]:g} and {value[1]:g}" if option.endswith("between") else
            f"at {value:g}" if option == "remove_at" else f"{option.split('_')[1]} {value:g}")
    verb = "keeps" if option.startswith("keep") else "removes"
    label = (f"The {made['words']}" if option == "remove_at" else
             f"The filter that {verb} the frequencies {what} ({made['words']})")
    system_ = System.from_coefficients(b, a, time_step=step, sos=made.get("sos"), label=label)
    print(system_._describe())
    print(f"Method: {made['r_call']}." if made.get("scipy_only") else f"Method: SciPy, as R {made['r_call']}.")
    return system_


def _analog_filter(keep_below, keep_above, keep_between, remove_between, remove_at, time_step, sampling_rate, fs,
                   test_method, steepness, ripple, removed_by, find_order_for):
    """sdata.frequency_filter(analog=True): the continuous filter of SciPy's design functions with analog=True,
    cutoffs in cycles per unit of time (handed to SciPy as 2 pi x the cutoff, radians per unit of time)."""
    from . import _filter_design as fd
    from . import _filters

    if time_step is not None or sampling_rate is not None or fs is not None:
        raise SimplydataError("analog=True makes a continuous filter: leave out time_step= (it has no steps).")
    if remove_at is not None:
        raise SimplydataError("remove_at= (a notch) is made in steps only: give time_step= instead of analog=True.")
    given = [(k, v) for k, v in (("keep_below", keep_below), ("keep_above", keep_above), ("keep_between", keep_between),
                                 ("remove_between", remove_between)) if v is not None]
    if len(given) != 1:
        raise SimplydataError("frequency_filter(analog=True) needs exactly one of keep_below=, keep_above=, "
                              "keep_between= or remove_between=, such as sdata.frequency_filter(keep_below=10, "
                              "analog=True).")
    option, value = given[0]
    if option.endswith("between") and not (isinstance(value, (list, tuple)) and len(value) == 2
                                            and 0 < value[0] < value[1]):
        raise SimplydataError(f"{option}= needs two frequencies above 0, the lower first, such as {option}=[1, 5].")
    cut = np.atleast_1d(np.asarray(value, dtype=float))
    if (cut <= 0).any():
        raise SimplydataError("The frequencies must be above 0.")
    if isinstance(steepness, bool) or not isinstance(steepness, (int, np.integer)) or not 1 <= steepness <= 20:
        raise SimplydataError("frequency_filter() needs steepness= as a whole number from 1 to 20 (the filter order).")
    kind = {"keep_below": "low", "keep_above": "high", "keep_between": "pass", "remove_between": "stop"}[option]
    chosen = _filters.read_method(test_method, "frequency_filter")
    n, natural, found = int(steepness), None, ""
    if find_order_for is not None:
        if steepness != 4:
            raise SimplydataError("find_order_for= finds the steepness itself: leave out steepness=.")
        loss_at = fd.read_order_request(find_order_for, kind, cut, np.inf, analog=True)
        n, natural, found = fd.find_order(chosen, kind, cut, loss_at, None, ripple, removed_by, analog=True)
        if n > 20:
            raise SimplydataError(f"That needs steepness {n}, more than 20: ask for less (a smaller removed_by=, a "
                                  '"loss_at" further from the cutoff).')
    b, a, call = fd.design_analog(kind, cut, chosen, n, ripple, removed_by, natural)
    what = (f"between {value[0]:g} and {value[1]:g}" if option.endswith("between") else
            f"{option.split('_')[1]} {value:g}")
    verb = "keeps" if option.startswith("keep") else "removes"
    label = (f"The analog filter that {verb} the frequencies {what} ({_filters.NAMES[chosen]}, "
             f"{found or f'steepness {n}'})")
    made = System(b, a, time_step=None, label=label, units="cycles per second", designed=True)
    print(f"{label}: output / input = {made._formula()} (s in radians per unit of time).")
    print(f"Method: SciPy signal.{call}(..., analog=True) at 2 pi x the cutoff"
          + (" (SciPy signal." + fd.ORDER_FINDERS[chosen] + "(..., analog=True) for the steepness)" if found else "")
          + ", as R gsignal::" + {"butter": "butter", "cheby1": "cheby1", "cheby2": "cheby2", "ellip": "ellip",
                                   "bessel": "besself"}[call] + "(..., \"s\").")
    return made
