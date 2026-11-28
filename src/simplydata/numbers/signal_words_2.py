"""Numbers words for signals, families for 100 %, batches 17-18 (plan 2.7, approved by Manish 2026-11-28)."""

from __future__ import annotations

import numpy as np

from .._errors import SimplydataError, friendly


class SignalNumberWords2:
    @friendly(renamed={"periods": "period"})
    def find_phase_locking_to(self, period=None):
        """How strongly events keep time with a cycle: the vector strength (0 none, 1 always at the same phase).

        numbers.find_phase_locking_to(period=0.1)   (the numbers are the times of the events)
        The numbers are the times of the events, such as the moments a nerve cell fires; period= is the length of
        the cycle in the same unit (a list of periods gives a table, one row each). Each event becomes a point on
        a circle at its phase in the cycle; the strength is the length of the average of those points (1: every
        event at the same phase, near 0: no link to the cycle) and the phase is where they gather (degrees, 0 at
        the start of the cycle). SciPy signal.vectorstrength. Gives back the strength (a table for several
        periods: period, strength, phase (degrees)).
        """
        import pandas as pd

        from .._signal_spectra import phase_locking
        from ..table import Table

        events = np.asarray(self._values, dtype=float).ravel()
        if np.isnan(events).any():
            raise SimplydataError("find_phase_locking_to() needs the time of every event; leave the empty ones out "
                                  "first (numbers.remove_empty_numbers()).")
        if not len(events):
            raise SimplydataError("find_phase_locking_to() needs the times of some events.")
        if period is None:
            raise SimplydataError("find_phase_locking_to() needs period=, the length of the cycle, such as "
                                  "event_times.find_phase_locking_to(period=0.1).")
        periods = np.atleast_1d(np.asarray(period, dtype=float))
        if periods.ndim != 1 or not len(periods) or np.any(~np.isfinite(periods)) or np.any(periods <= 0):
            raise SimplydataError("period= needs a length of time above 0 (or a list of them).")
        strength, phase = phase_locking(events, periods if len(periods) > 1 else float(periods[0]))
        print("Method: SciPy signal.vectorstrength (the length and angle of the average point on the circle of "
              "phases).")
        if len(periods) == 1:
            print(f"Phase locking of {len(events)} events to a cycle of {periods[0]:g}: strength {strength[0]:.4g} "
                  f"(1 = always at the same phase), gathered at phase {phase[0]:.4g} degrees.")
            return float(strength[0])
        best = int(np.argmax(strength))
        print(f"Phase locking of {len(events)} events to {len(periods)} cycle lengths: the strongest is "
              f"{strength[best]:.4g} at a cycle of {periods[best]:g}.")
        return Table(pd.DataFrame({"period": periods, "strength": strength, "phase (degrees)": phase}))
