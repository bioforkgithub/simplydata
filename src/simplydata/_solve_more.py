"""More exact solving (families for 100 %, batches 24-26, plan section 2.10, approved by Manish 2026-11-28):
sdata.check_solution, sdata.find_product_of_series, sdata.list_ways_to_choose and sdata.list_ways_to_order, and the
kinds of equations sdata.solve(..., exactly=True) takes besides ordinary ones: whole-number solutions
(whole_numbers_only=True), sequences ("a(n + 1) = 2*a(n) + 1", with at_start=) and partial differential equations
("du/dx + 2*du/dy = 0").

Every answer comes from SymPy, each call under simplydata's one time limit (_time_limit.py): checksol, checkodesol
and checkpdesol; product; diophantine (permute=True: signs and orders included; a family is said to be SymPy's);
rsolve; pdsolve;
subsets, variations and cartes (SymPy's generators, listed in this process once SymPy has counted the ways under the
time limit: binomial, ff, or a power). Own code is glue only: reading the text, naming the letters and functions, and
writing SymPy's answers back as tables and formulas.
"""

from __future__ import annotations

import math
import re

from ._errors import SimplydataError, friendly
from ._time_limit import one_deadline

MAX_WAYS = 100_000  # list_ways_to_*: at most this many ways listed
MAX_CHOSEN = 100  # list_ways_to_*: at most this many things in one way (the columns of the table)
MAX_WAY_CELLS = 1_000_000  # list_ways_to_*: ways times things in each, the cells of the table
MAX_PRODUCT_TERMS = 1000  # a finite product of more terms is refused (as factorial(1000) at most in formula text)
_SECOND = re.compile(r"(?<![\w])d\s*\^?\s*2\s*([A-Za-z]\w*?)\s*/\s*d\s*([A-Za-z][A-Za-z_]*?)\s*\^?\s*2(?![\w])")
_FIRST = re.compile(r"(?<![\w])d([A-Za-z]\w*?)\s*/\s*d([A-Za-z]\w*?)(?![\w])")
_CALL = re.compile(r"(?<![\w.])([A-Za-z]\w*)\s*\(")
_SHIFT = re.compile(r"^\s*([A-Za-z]\w*)\s*(?:([+-])\s*(\d+))?\s*$")  # n, n + 1, n - 2: a term of a sequence
ORDINALS = ("1st", "2nd", "3rd")


def _column(i: int) -> str:
    return ORDINALS[i] if i < 3 else f"{i + 1}th"


# ------------------------------------------------------------------------------------------------ reading text
def _changes_in(text: str):
    """The derivatives written in an equation: [(token, function name, letter, order)] for dy/dx and d2y/dx2.

    d, a name, /d and a name is read as a slope only when each name is one letter (dy/dx, dN/dt) or is a letter of
    the equation elsewhere (dvolume/dt = -volume): distance/duration and dose/dw are letters divided, not slopes."""
    found = []
    for match in _SECOND.finditer(text):
        found.append((match.group(0), match.group(1), match.group(2), 2))
    rest = _SECOND.sub(" ", text)
    for match in _FIRST.finditer(rest):
        found.append((match.group(0), match.group(1), match.group(2), 1))
    outside = text
    for token, *_ in found:
        outside = outside.replace(token, " ")
    words = set(re.findall(r"[A-Za-z]\w*", outside))
    return [item for item in found if all(len(part) == 1 or part in words for part in item[1:3])]


def _unknown_calls(text: str) -> list:
    """(name, start, end, inside) of each call of a name that is not a function of formula text: a(n + 1)."""
    from ._formula import FUNCTIONS, SPELLINGS

    out, position = [], 0
    for match in _CALL.finditer(text):
        if match.group(1) in FUNCTIONS or match.group(1) in SPELLINGS or match.start() < position:
            continue
        depth, end = 0, None
        for i in range(match.end() - 1, len(text)):
            depth += {"(": 1, ")": -1}.get(text[i], 0)
            if depth == 0:
                end = i
                break
        if end is None:
            return out
        out.append((match.group(1), match.start(), end, text[match.end():end]))
        position = end + 1
    return out


def _is_sequence(text: str) -> bool:
    """Whether the text is a sequence: one name written with at least two whole-number steps of one letter, such as
    a(n + 1) and a(n). abs-like names (Abs(x) = 2), f(x) = 2 and a(x + 1) = 4 are not."""
    shifts: dict = {}
    for name, _, _, inside in _unknown_calls(text):
        found = _SHIFT.match(inside)
        if found:
            step = int(found.group(3) or 0) * (-1 if found.group(2) == "-" else 1)
            shifts.setdefault((name, found.group(1)), set()).add(step)
    return any(len(steps) >= 2 for steps in shifts.values())


def kind_of_equations(texts) -> str | None:
    """"sequence" for a(n + 1) = ..., "partial" for an equation with du/dx and du/dy, else None."""
    for text in texts:
        if not isinstance(text, str):
            continue
        tokens = _changes_in(text)
        letters_by_function: dict = {}
        for _, name, letter, _ in tokens:
            letters_by_function.setdefault(name, set()).add(letter)
        if any(len(v) > 1 for v in letters_by_function.values()):
            return "partial"
        if _is_sequence(text):
            return "sequence"
    return None


def _read_with_changes(sp, text: str, what: str, known=None):
    """An equation with derivatives as SymPy: (relation, function, letters it depends on). dy/dx and d2y/dx2 become
    SymPy's Derivative of y(x); du/dx + du/dy of u(x, y)."""
    from ._formula import parse
    from ._maths_formula import split_equation

    tokens = _changes_in(text)
    if not tokens:
        return None
    names = {name for _, name, _, _ in tokens}
    if len(names) != 1:
        raise SimplydataError(f'"{text}" has slopes of {len(names)} things ({", ".join(sorted(names))}); simplydata '
                              "works with equations for one changing value.")
    name = names.pop()
    letters = list(dict.fromkeys(letter for _, _, letter, _ in tokens))
    if name in letters:
        raise SimplydataError(f'"{text}": what changes and the letter it changes with cannot be the same letter.')
    written = text
    swaps_text = {}
    for token, _, letter, order in sorted(tokens, key=lambda t: -len(t[0])):
        place = f"d{order if order == 2 else ''}{name}_d{letter}{order if order == 2 else ''}"
        swaps_text[place] = (letter, order)
        written = written.replace(token, f" {place} ")
    left, sign, right = split_equation(written)
    if sign != "=":
        raise SimplydataError(f'"{text}" needs an = sign: an equation, not a rule.')
    a, b = parse(left, what, known), parse(right, what, known)
    function = sp.Function(name)
    by_name = {str(s): s for s in (a.free_symbols | b.free_symbols)}
    symbols = [by_name.get(letter, sp.Symbol(letter)) for letter in letters]
    applied = function(*symbols)
    swaps = {by_name[place]: applied.diff(by_name.get(letter, sp.Symbol(letter)), order)
             for place, (letter, order) in swaps_text.items() if place in by_name}
    if name in by_name:
        swaps[by_name[name]] = applied
    return sp.Eq(a.xreplace(swaps), b.xreplace(swaps)), function, symbols


# ------------------------------------------------------------------------------------------------ check_solution
@friendly
@one_deadline
def check_solution(equation=None, solution=None, known=None):
    """Whether a solution makes an equation true, checked by SymPy.
    answer = sdata.check_solution("dy/dx = y", "y = 3*exp(x)")

    sdata.check_solution("dy/dx = y", "y = 3*exp(x)") gives True: put into the equation, the solution leaves 0 (SymPy
    checkodesol). An equation with slopes in two letters ("du/dx + du/dy = 0", "u = (x - y)**2") is a partial
    differential equation (checkpdesol); any other equation is checked with checksol: sdata.check_solution("x**2 = 4",
    "x = 2") or with several letters sdata.check_solution("x + y = 3", {"x": 1, "y": 2}). Gives True or False, and
    None when SymPy cannot tell (which simplydata says); what is left over is printed when it is not 0. known= fixes
    letters that are numbers. As SymPy checksol, checkodesol, checkpdesol.
    """
    from ._formula import _guarded, _show, exact_number, need_sympy, parse
    from ._maths_formula import split_equation

    sp = need_sympy("sdata.check_solution()")
    example = 'sdata.check_solution("dy/dx = y", "y = 3*exp(x)")'
    if not isinstance(equation, str) or solution is None:
        raise SimplydataError(f"check_solution() needs an equation in quotes and a solution.\nFor example:  {example}")
    from ._calculus import _exact_values

    values = _exact_values(sp, known)
    with_changes = _read_with_changes(sp, equation, "check_solution()", values)
    if with_changes is not None:
        relation, function, symbols = with_changes
        if not isinstance(solution, str):
            raise SimplydataError(f'The solution of "{equation}" is a formula for {function}, in quotes, such as '
                                  f'"{function} = 3*exp({symbols[0]})".')
        left, _, right = split_equation(solution)
        if left.strip() != str(function):
            raise SimplydataError(f'The solution should start with "{function} =", as in "{function} = '
                                  f'3*exp({symbols[0]})".')
        answer_side = parse(right, "check_solution()", values, symbols={str(s): s for s in symbols})
        written = sp.Eq(function(*symbols), answer_side)
        name = "checkodesol" if len(symbols) == 1 else "checkpdesol"
        works, rest = _guarded(getattr(sp, name), relation, written, what=f"SymPy {name}")
        said = f"{function} = {_show(answer_side)}"
        if works:
            print(f"{said} solves {equation}: put in, it leaves 0   (SymPy {name})")
            return True
        print(f"{said} does not solve {equation}: put in, it leaves {_show(rest)}, not 0   (SymPy {name})")
        return False
    left, sign, right = split_equation(equation)
    relation = {"=": sp.Eq, "<": sp.StrictLessThan, ">": sp.StrictGreaterThan, "<=": sp.LessThan,
                ">=": sp.GreaterThan}[sign](parse(left, "check_solution()", values),
                                            parse(right, "check_solution()", values))
    letters = {str(s): s for s in relation.free_symbols}
    pairs = _solution_pairs(solution, example)
    unknown = [k for k in pairs if k not in letters]
    if unknown:
        raise SimplydataError(f"{', '.join(unknown)} {'is' if len(unknown) == 1 else 'are'} not a letter of "
                              f'"{equation}"; its letters: {", ".join(sorted(letters)) or "none"}.')
    missing = sorted(k for k in letters if k not in pairs)
    if missing:
        example = ", ".join(repr(k) + ": 1" for k in sorted(letters))
        raise SimplydataError(f"The solution gives no value for {', '.join(missing)}: a solution of \"{equation}\" "
                              f"gives every letter a value, such as {{{example}}}.")
    chosen = {letters[k]: (parse(v, "check_solution()", values) if isinstance(v, str) else exact_number(sp, v))
              for k, v in pairs.items()}
    said = ", ".join(f"{k} = {_show(v)}" for k, v in chosen.items())
    if sign != "=":  # a rule: put the values in and let SymPy say whether it holds
        holds = _guarded(relation.subs, chosen, what="SymPy subs")
        if holds not in (sp.true, sp.false):
            print(f"SymPy cannot tell whether {said} makes {equation} true   (SymPy subs)")
            return None
        print(f"{said} {'makes' if holds == sp.true else 'does not make'} {equation} true   (SymPy subs)")
        return holds == sp.true
    found = _guarded(sp.checksol, relation, chosen, what="SymPy checksol")
    if found is None:
        print(f"SymPy cannot tell whether {said} makes {equation} true   (SymPy checksol)")
        return None
    print(f"{said} {'makes' if found else 'does not make'} {equation} true   (SymPy checksol)")
    return bool(found)


def _solution_pairs(solution, example: str) -> dict:
    from ._maths_formula import split_equation

    if isinstance(solution, dict) and solution:
        return dict(solution)
    texts = [solution] if isinstance(solution, str) else solution
    if not isinstance(texts, (list, tuple)) or not texts or not all(isinstance(t, str) for t in texts):
        raise SimplydataError("The solution is a value for each letter: \"x = 2\", a list of them, or a dict such as "
                              f'{{"x": 2}}.\nFor example:  {example}')
    out = {}
    for text in texts:
        left, sign, right = split_equation(text)
        if sign != "=" or not left.strip().isidentifier():
            raise SimplydataError(f'"{text}" should give one letter its value, such as "x = 2".')
        out[left.strip()] = right
    return out


# ------------------------------------------------------------------------------------------------ products
@friendly
@one_deadline
def find_product_of_series(formula=None, between=None, for_letter=None, known=None):
    """The product of a formula for every whole number from one end to the other.
    product = sdata.find_product_of_series("k/(k + 1)", between=[1, "n"])

    sdata.find_product_of_series("k/(k + 1)", between=[1, "n"]) gives factorial(n)/RisingFactorial(2, n), which is
    1/(n + 1): (1/2)(2/3)(3/4)... up to n (SymPy product; product.make_simpler(by="gamma functions") writes it as
    1/(n + 1)). The ends are whole numbers, "infinity", or a letter; a finite product has up to 1000 terms.
    for_letter= says which letter counts when there are several; known= fixes others. sdata.find_sum_of_series
    adds the terms instead. Gives a formula. As SymPy product (Product); MATLAB symprod.
    """
    from ._calculus import _check_term_sizes, _exact_expr, _sum_end
    from ._formula import Formula, _guarded, _show, float_of, need_sympy

    sp = need_sympy("sdata.find_product_of_series()")
    example = 'sdata.find_product_of_series("k/(k + 1)", between=[1, "n"])'
    if formula is None:
        raise SimplydataError(f"find_product_of_series() needs a formula in quotes.\nFor example:  {example}")
    expr = _exact_expr(sp, formula, formula, "find_product_of_series()", known)
    letters = sorted(str(s) for s in expr.free_symbols)
    if for_letter is None:
        if len(letters) != 1:
            raise SimplydataError(f"{_show(expr)} has {len(letters)} letters ({', '.join(letters) or 'none'}): say "
                                  "which one counts with for_letter=.\nFor example:  "
                                  'sdata.find_product_of_series("a*k", between=[1, 5], for_letter="k")')
        for_letter = letters[0]
    if not isinstance(for_letter, str) or for_letter not in letters:
        raise SimplydataError(f"for_letter= needs one of the letters of {_show(expr)} in quotes: "
                              f"{', '.join(repr(n) for n in letters) or 'none'}.")
    if isinstance(between, (str, bytes)) or not isinstance(between, (list, tuple)) or len(between) != 2:
        raise SimplydataError(f"find_product_of_series() needs between= the first and the last whole number.\n"
                              f"For example:  {example}")
    own = {str(s): s for s in expr.free_symbols}
    low, high = (_sum_end(sp, v, own, example) for v in between)
    if for_letter in (str(low), str(high)):
        raise SimplydataError(f"between= cannot end at {for_letter}: that is the letter that counts.")
    if low.is_number and high.is_number and low > high:
        raise SimplydataError(f"between= must go from the smaller end to the bigger one; it was "
                              f"[{_show(low)}, {_show(high)}].")
    k = sp.Symbol(for_letter, integer=True)
    term = expr.subs(own[for_letter], k)
    said = (f"The product of {formula.strip() if isinstance(formula, str) else _show(expr)} for {k} from "
            f"{_show(low)} to {_show(high)}")
    if low.is_Integer and high.is_Integer:
        if int(high) - int(low) + 1 > MAX_PRODUCT_TERMS:
            raise SimplydataError(f"{said} has {int(high) - int(low) + 1:,} terms; simplydata multiplies up to "
                                  f"{MAX_PRODUCT_TERMS:,} exactly (as factorial(1000) at most). For the formula up to "
                                  'a letter, use between=[1, "n"].')
        _check_term_sizes(sp, term, k, (low, high), said)
    found = _guarded(sp.product, term, (k, low, high), what="SymPy product")
    if found.has(sp.Product):
        raise SimplydataError(f"{said}: SymPy found no formula (SymPy product left it unworked). formula.as_sympy() "
                              "hands the formula to SymPy itself.")
    if found is sp.nan or found.has(sp.nan, sp.zoo):
        print(f"{said} does not settle on a number   (SymPy product)")
        return math.nan
    about = f" (about {float_of(found):.10g})" if not found.free_symbols and found.is_real and found.is_finite else ""
    print(f"{said}: {_show(found)}{about}   (SymPy product)")
    return Formula(found)


# ------------------------------------------------------------------------------------------------ ways
def _things(out_of, step: str, example: str) -> list:
    if isinstance(out_of, bool) or out_of is None:
        raise SimplydataError(f"{step}() needs out_of=, the things to choose from: a list, or a whole number n for "
                              f"1 to n.\nFor example:  {example}")
    if isinstance(out_of, int):
        if not 1 <= out_of <= MAX_WAYS:
            raise SimplydataError(f"out_of= as a number is how many things there are, from 1 to {MAX_WAYS:,}.")
        return list(range(1, out_of + 1))
    if hasattr(out_of, "_values"):
        return [v.item() if hasattr(v, "item") else v for v in out_of._values.ravel()]
    if isinstance(out_of, (list, tuple)) and out_of:
        return list(out_of)
    raise SimplydataError(f"out_of= needs a list of things, or a whole number n for 1 to n.\nFor example:  {example}")


def _ways_table(ways, fast: bool, size: int):
    from ._formula import _result_rows

    if not ways:
        import pandas as pd

        from .table import table

        return table(pd.DataFrame(columns=[_column(i) for i in range(size)]), fast=fast)
    return _result_rows([{_column(i): item for i, item in enumerate(way)} for way in ways], fast)


def _size_check(how_many: int, step: str):
    """Refuse a way of more than MAX_CHOSEN things before SymPy counts or makes any way."""
    if how_many > MAX_CHOSEN:
        raise SimplydataError(f"{step}() lists ways of up to {MAX_CHOSEN} things each (one column for each); "
                              f"{how_many:,} is too many. sdata.count_ways_to_choose() and count_ways_to_order() count "
                              "ways of any size without listing them.")


def _count_check(count, step: str, how_many: int = 1):
    """Refuse more than MAX_WAYS ways, or a table of more than MAX_WAY_CELLS cells, before any way is made."""
    if int(count) > MAX_WAYS:
        raise SimplydataError(f"{step}() lists up to {MAX_WAYS:,} ways; there are {int(count):,}. "
                              "sdata.count_ways_to_choose() and count_ways_to_order() count them without listing.")
    if int(count) * max(how_many, 1) > MAX_WAY_CELLS:
        raise SimplydataError(f"{step}() would make a table of {int(count) * how_many:,} cells ({int(count):,} ways of "
                              f"{how_many} things); it makes up to {MAX_WAY_CELLS:,}. Choose fewer things.")


@friendly
def list_ways_to_choose(how_many=None, out_of=None, with_repeats=False, one_from_each=None, fast=False):
    """Every way to choose some things out of more, when the order does not matter.
    ways = sdata.list_ways_to_choose(2, out_of=["A", "B", "C", "D"])

    sdata.list_ways_to_choose(2, out_of=["A", "B", "C", "D"]) gives the 6 pairs AB, AC, AD, BC, BD, CD, one row
    each (SymPy subsets). with_repeats=True lets a thing be chosen again (AA ...). one_from_each=[["red", "blue"],
    ["S", "M", "L"]] gives one from each list instead, every combination (SymPy cartes, the Cartesian product).
    out_of= may be a whole number n for 1 to n. Up to 100,000 ways; sdata.count_ways_to_choose counts them. Gives a
    table: 1st, 2nd ... As SymPy subsets; R combn; Python itertools.combinations.
    """
    from ._formula import _guarded, need_sympy

    sp = need_sympy("sdata.list_ways_to_choose()")
    example = 'sdata.list_ways_to_choose(2, out_of=["A", "B", "C", "D"])'
    if not isinstance(with_repeats, bool):
        raise SimplydataError("with_repeats= is True or False.")
    if one_from_each is not None:
        if how_many is not None or out_of is not None or with_repeats:
            raise SimplydataError("one_from_each= takes one thing from each list: leave out how_many, out_of= and "
                                  "with_repeats=.")
        if not isinstance(one_from_each, (list, tuple)) or len(one_from_each) < 2 or not all(
                isinstance(group, (list, tuple)) and group for group in one_from_each):
            raise SimplydataError('one_from_each= needs two or more lists, such as one_from_each=[["red", "blue"], '
                                  '["S", "M", "L"]].')
        _size_check(len(one_from_each), "list_ways_to_choose")
        count = _guarded(sp.prod, [len(g) for g in one_from_each], what="SymPy prod")
        _count_check(count, "list_ways_to_choose", len(one_from_each))
        ways = list(sp.cartes(*one_from_each))  # SymPy's generator, after the count
        print(f"{int(count):,} way{'s' if count != 1 else ''} to take one from each list   (SymPy cartes)")
        return _ways_table(ways, fast, len(one_from_each))
    things = _things(out_of, "list_ways_to_choose", example)
    n = len(things)
    if isinstance(how_many, bool) or not isinstance(how_many, int) or how_many < 0 or (
            how_many > n and not with_repeats):
        raise SimplydataError(f"how_many is how many to choose, a whole number from 0 to {n} (more with "
                              f"with_repeats=True).\nFor example:  {example}")
    _size_check(how_many, "list_ways_to_choose")
    count = _guarded(sp.binomial, n + how_many - 1 if with_repeats else n, how_many, what="SymPy binomial")
    _count_check(count, "list_ways_to_choose", how_many)
    ways = list(sp.subsets(things, how_many, repetition=with_repeats))  # SymPy's generator, after the count
    print(f"{int(count):,} way{'s' if count != 1 else ''} to choose {how_many} out of {n}"
          f"{' with repeats' if with_repeats else ''} (order does not matter)   (SymPy subsets)")
    return _ways_table(ways, fast, how_many)


@friendly
def list_ways_to_order(how_many=None, out_of=None, with_repeats=False, fast=False):
    """Every way to pick some things out of more in order (first, second ...).
    ways = sdata.list_ways_to_order(2, out_of=["A", "B", "C"])

    sdata.list_ways_to_order(2, out_of=["A", "B", "C"]) gives the 6 orders AB, AC, BA, BC, CA, CB, one row each
    (SymPy variations). with_repeats=True lets a thing come again (AA ...). out_of= may be a whole number n for 1 to
    n. Up to 100,000 ways; sdata.count_ways_to_order counts them. Gives a table: 1st, 2nd ... As SymPy variations;
    Python itertools.permutations.
    """
    from ._formula import _guarded, need_sympy

    sp = need_sympy("sdata.list_ways_to_order()")
    example = 'sdata.list_ways_to_order(2, out_of=["A", "B", "C"])'
    if not isinstance(with_repeats, bool):
        raise SimplydataError("with_repeats= is True or False.")
    things = _things(out_of, "list_ways_to_order", example)
    n = len(things)
    if isinstance(how_many, bool) or not isinstance(how_many, int) or how_many < 0 or (
            how_many > n and not with_repeats):
        raise SimplydataError(f"how_many is how many to pick, a whole number from 0 to {n} (more with "
                              f"with_repeats=True).\nFor example:  {example}")
    _size_check(how_many, "list_ways_to_order")
    count = (_guarded(sp.Pow, n, how_many, what="SymPy Pow") if with_repeats
             else _guarded(sp.ff, n, how_many, what="SymPy ff"))
    _count_check(count, "list_ways_to_order", how_many)
    ways = list(sp.variations(things, how_many, repetition=with_repeats))  # SymPy's generator, after the count
    print(f"{int(count):,} way{'s' if count != 1 else ''} to order {how_many} out of {n}"
          f"{' with repeats' if with_repeats else ''} (order matters)   (SymPy variations)")
    return _ways_table(ways, fast, how_many)


# ------------------------------------------------------------------------------------------------ solve(exactly=True)
@one_deadline
def solve_more(texts, kind, known, fast, for_letter=None, whole_numbers_only=False, at_start=None):
    """sdata.solve(exactly=True) for whole-number solutions, sequences and partial differential equations."""
    from ._calculus import _exact_values
    from ._formula import need_sympy

    sp = need_sympy("sdata.solve(exactly=True)")
    values = _exact_values(sp, known)
    if len(texts) != 1 or not isinstance(texts[0], str):
        what = {"sequence": "a sequence", "partial": "a partial differential equation"}.get(kind, "whole numbers")
        raise SimplydataError(f"solve(exactly=True) solves {what} one equation at a time, in quotes.")
    text = texts[0]
    if kind == "partial":
        if whole_numbers_only or at_start is not None:
            raise SimplydataError("A partial differential equation takes no whole_numbers_only= or at_start=.")
        return _partial(sp, text, values)
    if kind == "sequence":
        if whole_numbers_only:
            raise SimplydataError("A sequence takes no whole_numbers_only=: its letter counts in whole numbers "
                                  "already.")
        return _sequence(sp, text, values, at_start)
    if at_start is not None:
        raise SimplydataError('at_start= gives the first terms of a sequence, such as sdata.solve("a(n + 1) = 2*a(n)", '
                              'exactly=True, at_start={0: 1}).')
    return _whole_numbers(sp, text, values, fast, for_letter)


def _partial(sp, text, values):
    from ._formula import Formula, _guarded, _show

    relation, function, symbols = _read_with_changes(sp, text, "solve()", values)
    try:
        found = _guarded(sp.pdsolve, relation, function(*symbols), what="SymPy pdsolve")
    except NotImplementedError as error:
        raise SimplydataError(f"SymPy cannot solve {text} ({error}); it solves first-order linear partial equations "
                              "with numbers in front of the slopes.") from None
    answer = found.rhs
    names = sorted({str(f.func) for f in answer.atoms(sp.Function) if isinstance(f, sp.core.function.AppliedUndef)})
    print(f"{text}: {function}({', '.join(str(s) for s in symbols)}) = {_show(answer)}   (SymPy pdsolve)")
    if names:
        print(f"{' and '.join(names)} {'is any function' if len(names) == 1 else 'are any functions'} of what is "
              "inside the brackets: every such function gives a solution.")
    return Formula(answer)


def _sequence(sp, text, values, at_start):
    from ._formula import Formula, _guarded, _show, exact_number, parse
    from ._maths_formula import split_equation

    calls, written, name = [], "", None
    position = 0
    for found_name, start_at, end, inside in _unknown_calls(text):
        if name is not None and found_name != name:
            raise SimplydataError(f'"{text}" has two sequences ({name} and {found_name}); simplydata solves one.')
        name = found_name
        place = f"{name}_term_{len(calls)}"
        calls.append((place, inside))
        written += text[position:start_at] + f" {place} "
        position = end + 1
    written += text[position:]
    inner = [parse(t, "solve()", values) for _, t in calls]
    letters = sorted({str(s) for e in inner for s in e.free_symbols})
    if len(letters) != 1:
        raise SimplydataError(f'"{text}": the terms of {name} need one letter that counts, such as {name}(n + 1) and '
                              f"{name}(n); these have {', '.join(letters) or 'none'}.")
    n = sp.Symbol(letters[0], integer=True)
    inner = [e.xreplace({s: n for s in e.free_symbols}) for e in inner]
    left, sign, right = split_equation(written)
    if sign != "=":
        raise SimplydataError(f'"{text}" needs an = sign.')
    a, b = parse(left, "solve()", values), parse(right, "solve()", values)
    function = sp.Function(name)
    by_name = {str(s): s for s in (a.free_symbols | b.free_symbols)}
    swaps = {by_name[place]: function(e) for (place, _), e in zip(calls, inner) if place in by_name}
    if letters[0] in by_name:
        swaps[by_name[letters[0]]] = n
    equation = (a - b).xreplace(swaps)
    start = None
    if at_start is not None:
        if not isinstance(at_start, dict) or not at_start:
            raise SimplydataError('at_start= gives the first terms, such as at_start={0: 1, 1: 1} (or '
                                  f'{{"{name}(0)": 1}}).')
        start = {}
        for key, value in at_start.items():
            if isinstance(key, str):
                found = re.fullmatch(rf"\s*{re.escape(name)}\s*\(\s*(-?\d+)\s*\)\s*", key)
                if not found:
                    raise SimplydataError(f'at_start= names terms as {name}(0) or as the number 0; "{key}" is '
                                          "neither.")
                key = int(found.group(1))
            if isinstance(key, bool) or not isinstance(key, int):
                raise SimplydataError(f"at_start= names terms by whole numbers, such as {{0: 1}}; {key!r} is not one.")
            start[function(key)] = exact_number(sp, value) if not isinstance(value, str) else parse(value, "solve()")
    found = _guarded(sp.rsolve, equation, function(n), start, what="SymPy rsolve")
    if found is None and start:
        general = _guarded(sp.rsolve, equation, function(n), what="SymPy rsolve")
        if general is not None:
            said = ", ".join(f"{k} = {_show(v)}" for k, v in start.items())
            raise SimplydataError(f"The starting values {said} contradict {text}: no sequence of it has them. Its "
                                  f"terms are {name}({n}) = {_show(general)} (SymPy rsolve); give fewer starting "
                                  "values, or ones that fit.")
    if found is None:
        raise SimplydataError(f"SymPy found no formula for {text} (SymPy rsolve).")
    starts = (" with " + ", ".join(f"{k} = {_show(v)}" for k, v in start.items())) if start else ""
    print(f"{text}{starts}: {name}({n}) = {_show(found)}   (SymPy rsolve)")
    constants = sorted(str(s) for s in found.free_symbols if re.fullmatch(r"C\d+", str(s)))
    if constants:
        print(f"{' and '.join(constants)} {'is a constant' if len(constants) == 1 else 'are constants'} that any "
              f"number fits; at_start= fixes {'it' if len(constants) == 1 else 'them'}.")
    return Formula(found)


def _whole_numbers(sp, text, values, fast, for_letter):
    from ._formula import _guarded, _result_rows, _show, parse
    from ._maths_formula import split_equation

    left, sign, right = split_equation(text)
    if sign != "=":
        raise SimplydataError("whole_numbers_only=True solves equations (=) in whole numbers, not rules.")
    expr = parse(left, "solve()", values) - parse(right, "solve()", values)
    names = sorted(str(s) for s in expr.free_symbols)
    if not names:
        raise SimplydataError(f'"{text}" has no letter to find.')
    order = names
    if for_letter is not None:
        wanted = [for_letter] if isinstance(for_letter, str) else list(for_letter)
        if sorted(wanted) != names:
            raise SimplydataError(f"whole_numbers_only=True finds every letter ({', '.join(names)}); for_letter= may "
                                  "only give their order.")
        order = wanted
    by_name = {str(s): s for s in expr.free_symbols}
    symbols = [by_name[n] for n in order]
    if not expr.is_polynomial(*symbols):
        raise SimplydataError(f'whole_numbers_only=True solves polynomial equations (whole powers of letters) in whole '
                              f'numbers; "{text}" is not one.')
    from sympy.solvers.diophantine.diophantine import classify_diop

    try:
        kind = _guarded(classify_diop, sp.expand(expr), what="SymPy classify_diop")[2].replace("_", " ")
        found = _guarded(sp.diophantine, expr, what="SymPy diophantine", syms=tuple(symbols), permute=True)
    except (NotImplementedError, TypeError, ValueError) as error:
        raise SimplydataError(f"SymPy cannot solve {text} in whole numbers ({error}).") from None
    method = f"SymPy diophantine ({kind}, whole numbers)"
    rows, said, free = [], [], set()
    for solution in sorted(found, key=lambda s: [str(v) for v in s]):
        row = {}
        for n, value in zip(order, solution):
            if value.free_symbols:
                free |= {str(s) for s in value.free_symbols}
                row[n] = math.nan
            else:
                row[n] = float(value)
            row[f"{n} exactly"] = _show(value)
        row["method"] = method
        rows.append(row)
        said.append(", ".join(f"{n} = {_show(v)}" for n, v in zip(order, solution)))
    if not rows:
        print(f"{text} has no whole-number solutions   ({method})")
        import pandas as pd

        from .table import table

        columns = [c for n in order for c in (n, f"{n} exactly")] + ["method"]
        return table(pd.DataFrame(columns=columns), fast=fast)
    shown = "; ".join(said[:12]) + (" ..." if len(said) > 12 else "")
    if free:
        print(f"{text} in whole numbers: {shown}   ({method}: SymPy's family of solutions)")
        print(f"{' and '.join(sorted(free))} {'is any whole number' if len(free) == 1 else 'are any whole numbers'}: "
              "each gives a solution. The family may leave solutions out: for some equations multiples and swaps "
              "of its members are solutions too (x**2 + y**2 = z**2 has 9, 12, 15 and 4, 3, 5, which SymPy's "
              "primitive family leaves out).")
    else:
        print(f"{text} in whole numbers: {shown}   ({method}, with every sign and order)")
    return _result_rows(rows, fast)
