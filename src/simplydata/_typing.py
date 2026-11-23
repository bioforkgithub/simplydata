"""Type hints for editors only (VS Code's Pylance, Jupyter's Jedi): no behaviour.

A step that gives back the same table, chart or numbers is written def step(self: _Same, ...) -> _Same, so after
t = sdata.table(...), t.keep_rows_where(...).sort_by(...) completes in the editor. typing.Self says the same,
but Jedi (Jupyter, IPython) does not read it yet, and a TypeVar on self works in both.
"""

from typing import TypeVar

_Same = TypeVar("_Same")
