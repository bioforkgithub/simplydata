"""Number theory on a list of whole numbers (families for 100 %, batch 26, plan section 2.10, approved by Manish
2026-11-28, G13): numbers.check_if_prime(), numbers.find_prime_factors() and the family
numbers.find_number_fact("divisors") for SymPy's other number theory (sympy.ntheory).

Every answer comes from SymPy, one call for each number under simplydata's one time limit (_time_limit.py):
isprime; factorint (primefactors with show="different primes", factorrat for a fraction); and one SymPy function
for each fact (FACTS below). A list of numbers holds decimals, which are exact for whole numbers up to 2**53, so
numbers above that are refused, and an answer above it is given exactly as text in a table. Facts whose answer can
grow without end (primorial, partitions, binomial coefficients) take numbers up to a limit, so that no answer has
more than about 1000 digits (the rule of the formula words). Two facts list what a SymPy generator gives, in this
process, once SymPy (under the time limit) has shown how long the list is: "primes up to" (primerange, after
primepi) and "continued fraction convergents" (one for each term of continued_fraction). Own code is glue only.
"""

from __future__ import annotations

import math

import numpy as np

from .._errors import SimplydataError, friendly
from .._time_limit import one_deadline

BIGGEST_EXACT = 2 ** 53  # a decimal holds every whole number up to this exactly
MAX_FACT_NUMBERS = 10_000  # numbers in one call (each is one SymPy call in the helper)
MAX_LISTED = 100_000  # primes up to: at most this many primes listed

# plain name -> (SymPy function, what it needs, what it gives, about, biggest number it takes)
# needs: None, "other" (other=), "modulo" (modulo=), "modulo power" (modulo= and power=), "modulo base" (modulo= and
# base=), "power" (power=), "base" (base=); "list" facts take the whole list as their input.
# gives: "number", "yes or no", "numbers" (a list for each number), "pair", "pairs", "fraction"
FACTS = {
    "divisors": ("divisors", None, "numbers", "every whole number that divides it, 1 and itself included", None),
    "number of divisors": ("divisor_count", None, "number", "how many divisors it has", None),
    "proper divisors": ("proper_divisors", None, "numbers", "its divisors without itself", None),
    "number of proper divisors": ("proper_divisor_count", None, "number", "how many proper divisors it has", None),
    "abundance": ("abundance", None, "number", "the sum of its divisors minus twice the number", None),
    "perfect": ("is_perfect", None, "yes or no", "the sum of its proper divisors is the number itself (6, 28)", None),
    "abundant": ("is_abundant", None, "yes or no", "the sum of its proper divisors is bigger than the number", None),
    "deficient": ("is_deficient", None, "yes or no", "the sum of its proper divisors is smaller than the number",
                  None),
    "amicable with": ("is_amicable", "other", "yes or no", "each is the sum of the other's proper divisors "
                      "(220 and 284)", None),
    "carmichael": ("is_carmichael", None, "yes or no", "a Carmichael number: not prime, yet it passes Fermat's test "
                   "for every base it shares no factor with (561)", None),
    "mersenne prime": ("is_mersenne_prime", None, "yes or no", "a prime that is one less than a power of 2", None),
    "perfect power": ("perfect_power", None, "pair", "the base and power with base**power the number (64 = 2**6), "
                      "empty when there is none", None),
    "next prime": ("nextprime", None, "number", "the smallest prime above it", None),
    "previous prime": ("prevprime", None, "number", "the biggest prime below it", None),
    "nth prime": ("prime", None, "number", "the prime in that place (the 1st is 2)", 10 ** 9),
    "nth composite": ("composite", None, "number", "the composite number in that place (the 1st is 4)", 10 ** 9),
    "primes up to": ("primerange", None, "numbers", "every prime up to the number", 10 ** 7),
    "number of composites up to": ("compositepi", None, "number", "how many composite numbers are up to it",
                                   10 ** 12),
    "primorial": ("primorial", None, "number", "the product of the first n primes", 300),
    "partitions": ("npartitions", None, "number", "the number of ways to write it as a sum of whole numbers",
                   100_000),
    "nth mersenne exponent": ("mersenne_prime_exponent", None, "number", "the power p of the nth Mersenne prime "
                              "2**p - 1", 51),
    "binomial coefficients": ("binomial_coefficients_list", None, "numbers", "the row of Pascal's triangle",
                              1000),
    "multinomial coefficients": ("multinomial_coefficients", "other", "pairs", "the coefficients of (x1 + ... + "
                                 "xm)**n, m in other=, with the powers of each term", 30),
    "times divisible by": ("multiplicity", "other", "number", "how many times other= divides it", None),
    "primitive root": ("primitive_root", None, "number", "the smallest primitive root modulo the number (empty "
                       "when it has none)", None),
    "primitive root modulo": ("is_primitive_root", "modulo", "yes or no", "it is a primitive root modulo modulo=",
                              None),
    "quadratic residue modulo": ("is_quad_residue", "modulo", "yes or no", "it is a square modulo modulo=", None),
    "power residue modulo": ("is_nthpow_residue", "modulo power", "yes or no", "it is a power= power modulo "
                             "modulo=", None),
    "order modulo": ("n_order", "modulo", "number", "the smallest k with number**k = 1 modulo modulo=", None),
    "discrete log": ("discrete_log", "modulo base", "number", "the smallest k with base**k = number modulo modulo=",
                     None),
    "square roots modulo": ("sqrt_mod", "modulo", "numbers", "every r with r**2 = number modulo modulo=", None),
    "nth roots modulo": ("nthroot_mod", "modulo power", "numbers", "every r with r**power = number modulo modulo=",
                         None),
    "quadratic residues": ("quadratic_residues", None, "numbers", "the squares modulo the number", 10 ** 5),
    "inverse modulo": ("mod_inverse", "modulo", "number", "the k with number*k = 1 modulo modulo=", None),
    "whole nth root": ("integer_nthroot", "power", "pair", "the whole part of the power= root, and whether it is "
                       "exact", None),
    "whole log": ("integer_log", "base", "pair", "the whole part of the log to base=, and whether it is exact", None),
    "number of digits": ("num_digits", "base", "number", "how many digits it has in base= (10 by itself)", None),
    "trailing zero bits": ("trailing", None, "number", "how many 0s end it in binary (the power of 2 in it)", None),
    "continued fraction": ("continued_fraction", None, "numbers", "the terms of its continued fraction (as the "
                           "exact fraction the decimal stands for)", None),
    "continued fraction convergents": ("continued_fraction_convergents", None, "fractions", "the fractions that "
                                       "come closer and closer to it", None),
    "egyptian fraction": ("egyptian_fraction", None, "numbers", "the bottoms of different fractions 1/a + 1/b + ... "
                          "that add up to it (greedy, Fibonacci-Sylvester)", None),
    # the whole list is the input
    "greatest common divisor": ("igcd", "list", "number", "the biggest whole number that divides them all", None),
    "least common multiple": ("ilcm", "list", "number", "the smallest whole number they all divide", None),
    "number from continued fraction": ("continued_fraction_reduce", "list", "fraction", "the number whose continued "
                                       "fraction the list is", None),
    "periodic continued fraction": ("continued_fraction_periodic", "list", "numbers", "the continued fraction of "
                                    "(p + sqrt(d))/q for the list [p, q, d]; the repeating terms in brackets", None),
    "quadratic congruence": ("quadratic_congruence", "list modulo", "numbers", "every x with a*x**2 + b*x + c = 0 "
                             "modulo modulo=, for the list [a, b, c]", None),
}
FACT_SPELLINGS = {}
for _name, (_function, *_) in FACTS.items():
    FACT_SPELLINGS[_function] = _name
del _name, _function
FACT_SPELLINGS.update({"divisor count": "number of divisors", "is_perfect": "perfect", "is perfect": "perfect",
                       "is abundant": "abundant", "is deficient": "deficient", "amicable": "amicable with",
                       "is carmichael": "carmichael", "nextprime": "next prime", "prevprime": "previous prime",
                       "prime": "nth prime", "composite": "nth composite", "primerange": "primes up to",
                       "primes": "primes up to", "gcd": "greatest common divisor", "lcm": "least common multiple",
                       "mod_inverse": "inverse modulo", "modular inverse": "inverse modulo",
                       "multiplicity": "times divisible by", "npartitions": "partitions",
                       "binomial_coefficients": "binomial coefficients", "pascal row": "binomial coefficients",
                       "sqrt_mod_iter": "square roots modulo", "continued_fraction_iterator": "continued fraction",
                       "digits": "number of digits", "order": "order modulo", "discrete logarithm": "discrete log"})
FACTORS_SHOW = ("factors", "different primes")
FACTORS_SPELLINGS = {"factorint": "factors", "primefactors": "different primes", "primes": "different primes",
                     "different": "different primes"}


def _whole_numbers(values, step: str, allow_fraction: bool = False) -> list:
    """The numbers of a list as Python whole numbers (checked: no empty ones, none above 2**53)."""
    flat = np.asarray(values, dtype=float).ravel()
    if flat.size == 0:
        raise SimplydataError(f"numbers.{step}() needs at least one number.")
    if flat.size > MAX_FACT_NUMBERS:
        raise SimplydataError(f"numbers.{step}() works on up to {MAX_FACT_NUMBERS:,} numbers at a time; this list has "
                              f"{flat.size:,}.")
    if np.isnan(flat).any():
        raise SimplydataError(f"numbers.{step}() needs every number: remove the empty ones first "
                              "(numbers.remove_empty_numbers()).")
    if np.isinf(flat).any() or (np.abs(flat) > BIGGEST_EXACT).any():
        raise SimplydataError(f"numbers.{step}() takes numbers up to {BIGGEST_EXACT:,} (2**53): a list of numbers "
                              "holds decimals, which are exact only up to there.")
    if not allow_fraction and not np.all(flat == np.round(flat)):
        bad = flat[flat != np.round(flat)][0]
        raise SimplydataError(f"numbers.{step}() works on whole numbers; {bad:g} is not one.")
    return [int(v) if v == round(v) else float(v) for v in flat]


def _exact(sp, value):
    from .._formula import exact_number

    return exact_number(sp, value)


def _plain(sp, value):
    """A SymPy answer as a Python value: a whole number, a fraction as text, or True/False."""
    if value is None:
        return None
    if isinstance(value, (bool, np.bool_)) or value in (sp.true, sp.false):
        return bool(value)
    if isinstance(value, int):
        return value
    if isinstance(value, sp.Integer):
        return int(value)
    return value


def _out_number(value):
    """A whole-number answer as a decimal, when a decimal holds it exactly; else None."""
    return float(value) if value is not None and abs(value) <= BIGGEST_EXACT else None


class NumberTheoryWords:
    """Number theory on a list of whole numbers (Numbers takes these words from here)."""

    @friendly
    @one_deadline
    def check_if_prime(self):
        """Whether each number is prime, as yes or no values. answer = numbers.check_if_prime()

        numbers = sdata.number_list([2, 9, 11, 561]), then numbers.check_if_prime() gives yes, no, yes, no (SymPy
        isprime: exact for every number up to 2**64, and a list of numbers holds whole numbers up to 2**53 exactly).
        0, 1 and numbers below 0 are not prime; a number with a decimal part is refused. Gives yes or no values,
        one for each number. As SymPy isprime; R numbers::isPrime.
        """
        from .._formula import _guarded, need_sympy
        from .numbers import Numbers

        sp = need_sympy("numbers.check_if_prime()")
        values = _whole_numbers(self._values, "check_if_prime")
        answers = [bool(_guarded(sp.isprime, v, what="SymPy isprime")) for v in values]
        primes = [v for v, a in zip(values, answers) if a]
        shown = ", ".join(str(v) for v in primes[:20]) + (" ..." if len(primes) > 20 else "")
        print(f"{len(primes)} of the {len(values)} numbers {'is' if len(primes) == 1 else 'are'} prime"
              + (f": {shown}" if primes else "") + "   (SymPy isprime)")
        return Numbers(np.array(answers, dtype=bool))

    @friendly
    @one_deadline
    def find_prime_factors(self, show="factors", fast=False):
        """The prime factors of each number, with how many times each divides it. factors = numbers.find_prime_factors()

        numbers = sdata.number_list([12, 35]), then numbers.find_prime_factors() gives the table 12: 2 (2 times) and
        3 (once); 35: 5 and 7 (SymPy factorint). show="different primes" lists each prime once, without times
        (SymPy primefactors). A number with a decimal part is taken as the fraction it stands for, and the primes of
        its bottom get a minus number of times (0.75 = 3/4: 2 -2 times, 3 once; SymPy factorrat). Gives a table:
        number, prime, times. As SymPy factorint; R gmp::factorize.
        """
        from .._formula import _guarded, _result_rows, need_sympy
        from .._formula_algebra import _value

        sp = need_sympy("numbers.find_prime_factors()")
        key = _value({k: k for k in FACTORS_SHOW}, FACTORS_SPELLINGS, show, "find_prime_factors", "show")
        values = _whole_numbers(self._values, "find_prime_factors", allow_fraction=True)
        rows, said, used = [], [], set()
        for v in values:
            if isinstance(v, float):
                if key != "factors":
                    raise SimplydataError(f'show="different primes" works on whole numbers; {v:g} is not one.')
                fraction = _exact(sp, v)
                found = _guarded(sp.factorrat, fraction, what="SymPy factorrat")
                how = "factorrat"
            elif key == "factors":
                found = _guarded(sp.factorint, v, what="SymPy factorint")
                how = "factorint"
            else:
                found = {p: None for p in _guarded(sp.primefactors, v, what="SymPy primefactors")}
                how = "primefactors"
            used.add(how)
            pairs = sorted(found.items(), key=lambda item: int(item[0]))
            for prime, times in pairs:
                row = {"number": float(v), "prime": float(prime)}
                if key == "factors":
                    row["times"] = int(times)
                rows.append(row)
            written = " * ".join(f"{p}" + (f"**{t}" if t not in (None, 1) else "") for p, t in pairs)
            said.append(f"{v:g} = {written or '1 (no prime factor)'}" if key == "factors" else
                        f"{v:g}: {', '.join(str(p) for p, _ in pairs) or 'none'}")
        shown = "; ".join(said[:10]) + (" ..." if len(said) > 10 else "")
        print(f"The prime factors: {shown}   (SymPy {' and '.join(sorted(used))})")
        if not rows:
            import pandas as pd

            from ..table import table

            columns = ["number", "prime", "times"] if key == "factors" else ["number", "prime"]
            return table(pd.DataFrame(columns=columns), fast=fast)
        return _result_rows(rows, fast)

    @friendly
    @one_deadline
    def find_number_fact(self, name=None, other=None, modulo=None, power=None, base=None, fast=False):
        """A fact of whole numbers from number theory, by name (SymPy's ntheory).
        divisors = numbers.find_number_fact("divisors")

        numbers = sdata.number_list([12, 28]), then numbers.find_number_fact("divisors") gives the table of 1, 2, 3,
        4, 6, 12 and 1, 2, 4, 7, 14, 28 (SymPy divisors). For each number: "divisors", "number of divisors", "proper
        divisors", "number of proper divisors", "abundance", "perfect", "abundant", "deficient", "amicable with"
        (other=), "carmichael", "mersenne prime", "perfect power", "next prime", "previous prime", "nth prime", "nth
        composite", "primes up to", "number of composites up to", "primorial", "partitions", "nth mersenne
        exponent", "binomial coefficients", "multinomial coefficients" (other= terms), "times divisible by"
        (other=), "primitive root", "primitive root modulo", "quadratic residue modulo", "order modulo", "inverse
        modulo", "square roots modulo" (modulo=), "power residue modulo", "nth roots modulo" (modulo= and power=),
        "discrete log" (modulo= and base=), "quadratic residues", "whole nth root" (power=), "whole log" (base=),
        "number of digits" (base=), "trailing zero bits", "continued fraction", "continued fraction convergents"
        and "egyptian fraction". Of the whole list: "greatest common divisor", "least common multiple", "number from
        continued fraction", "periodic continued fraction" ([p, q, d]) and "quadratic congruence" ([a, b, c],
        modulo=). SymPy's names work too ("divisor_count", "totient" is in formula text). A yes-or-no fact gives
        yes or no values; a one-number fact gives numbers (a table with exact digits when one is above 2**53); a
        fact with several answers gives a table: number, answer.
        """
        from .._formula import _guarded, _result_rows, _show, need_sympy
        from .._formula_algebra import _value
        from .numbers import Numbers

        sp = need_sympy("numbers.find_number_fact()")
        if name is None:
            raise SimplydataError('numbers.find_number_fact() needs the name of a fact, such as '
                                  'numbers.find_number_fact("divisors"). Names: ' + ", ".join(f'"{n}"' for n in FACTS))
        key = _value(FACTS, FACT_SPELLINGS, name, "find_number_fact", "name")
        function_name, needs, gives, about, most = FACTS[key]
        call = getattr(sp, function_name)
        what = f"SymPy {function_name}"
        needs = needs or ""
        wanted = {"other": "other" in needs or key in ("amicable with", "multinomial coefficients",
                                                        "times divisible by"),
                  "modulo": "modulo" in needs, "power": "power" in needs, "base": "base" in needs or
                  key == "number of digits"}
        given = {"other": other, "modulo": modulo, "power": power, "base": base}
        for option, value in given.items():
            if value is not None and not wanted[option]:
                raise SimplydataError(f'{option}= does not go with find_number_fact("{key}"); leave it out.')
            if value is None and wanted[option] and not (option == "base" and key == "number of digits"):
                raise SimplydataError(f'find_number_fact("{key}") needs {option}=, a whole number, such as '
                                      f'numbers.find_number_fact("{key}", {option}=7).')
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, np.integer))
                                      or not abs(value) <= BIGGEST_EXACT):
                raise SimplydataError(f"{option}= needs a whole number, such as {option}=7.")
        extra = {k: int(v) for k, v in given.items() if v is not None}
        fractions_ok = key in ("continued fraction", "continued fraction convergents", "egyptian fraction")
        values = _whole_numbers(self._values, "find_number_fact", allow_fraction=fractions_ok)

        # ---------------------------------------------------------------- facts of the whole list
        if needs.startswith("list"):
            return self._list_fact(sp, key, call, what, values, extra, fast)

        rows, answers = [], []
        for v in values:
            if most is not None and not 0 <= v <= most:
                raise SimplydataError(f'find_number_fact("{key}") takes numbers from 0 to {most:,}, so that no answer '
                                      f"is too big to work with; {v} is outside.")
            arguments = self._arguments(sp, key, v, extra)
            if function_name == "primerange":
                count = _guarded(sp.primepi, v, what="SymPy primepi")
                if int(count) > MAX_LISTED:
                    raise SimplydataError(f'find_number_fact("primes up to") lists up to {MAX_LISTED:,} primes; up '
                                          f"to {v} there are {int(count):,}.")
                found = list(sp.primerange(2, v + 1))  # SymPy's own sieve, after primepi showed the size
            elif function_name == "continued_fraction_convergents":
                terms = _guarded(sp.continued_fraction, *arguments, what="SymPy continued_fraction")
                found = list(sp.continued_fraction_convergents(terms))  # one fraction for each term
            else:
                named = {"all_roots": True} if function_name in ("sqrt_mod", "nthroot_mod") else {}
                try:
                    found = _guarded(call, *arguments, what=what, **named)
                except ValueError as error:  # SymPy's own "no answer" (no inverse, no discrete log ...)
                    raise SimplydataError(f'find_number_fact("{key}") has no answer for {v:g}: {error} '
                                          f"({what}).") from None
            answers.append(found)
            rows += self._fact_rows(sp, key, gives, v, found)
        said = "; ".join(f"{v:g}: {self._said(sp, gives, a)}" for v, a in list(zip(values, answers))[:10])
        print(f'find_number_fact("{key}") ({about}): {said}' + (" ..." if len(values) > 10 else "")
              + f"   ({what})")
        if gives == "yes or no":
            return Numbers(np.array([bool(a) for a in answers], dtype=bool))
        if gives == "number":
            plain = [_plain(sp, a) for a in answers]
            decimals = [_out_number(a) if isinstance(a, int) else (None if a is None else float(a)) for a in plain]
            if all(d is not None for d in decimals):
                return Numbers(np.array(decimals, dtype=float))
            if all(a is None or isinstance(a, int) for a in plain) and all(
                    d is not None for a, d in zip(plain, decimals) if a is not None):
                return Numbers(np.array([math.nan if d is None else d for d in decimals], dtype=float))
            return _result_rows([{"number": float(v), "answer": math.nan if d is None else d,
                                  "answer exactly": "" if a is None else _show(a)}
                                 for v, a, d in zip(values, plain, decimals)], fast)
        if not rows:
            import pandas as pd

            from ..table import table

            return table(pd.DataFrame(columns=["number", "answer"]), fast=fast)
        return _result_rows(rows, fast)

    # ------------------------------------------------------------------------------------------- helpers
    @staticmethod
    def _arguments(sp, key: str, v, extra: dict) -> list:
        """The values the SymPy function of a fact takes, in its own order."""
        if key in ("continued fraction", "continued fraction convergents", "egyptian fraction"):
            if key == "egyptian fraction" and not v > 0:
                raise SimplydataError('find_number_fact("egyptian fraction") works on numbers above 0.')
            return [_exact(sp, v)]
        if key == "amicable with":
            return [v, extra["other"]]
        if key == "multinomial coefficients":
            return [extra["other"], v]
        if key == "times divisible by":
            return [extra["other"], v]
        if key in ("primitive root modulo", "quadratic residue modulo", "order modulo", "inverse modulo",
                   "square roots modulo"):
            return [v, extra["modulo"]]
        if key in ("power residue modulo", "nth roots modulo"):
            return [v, extra["power"], extra["modulo"]]
        if key == "discrete log":
            return [extra["modulo"], v, extra["base"]]
        if key == "whole nth root":
            return [v, extra["power"]]
        if key == "whole log":
            return [v, extra["base"]]
        if key == "number of digits":
            return [v, extra.get("base", 10)]
        return [v]

    @staticmethod
    def _said(sp, gives: str, answer) -> str:
        from .._formula import _show

        if answer is None or answer is False and gives == "pair":
            return "none"
        if gives == "yes or no":
            return "yes" if answer else "no"
        if gives in ("numbers", "fractions"):
            items = list(answer)
            return ", ".join(_show(i) for i in items[:12]) + (" ..." if len(items) > 12 else "")
        if gives == "pairs":
            return f"{len(answer)} terms"
        if gives == "pair":
            return ", ".join(_show(i) for i in answer)
        return _show(answer)

    @staticmethod
    def _fact_rows(sp, key: str, gives: str, v, found) -> list:
        """The rows of a fact with several answers for one number."""
        from .._formula import _show

        number = float(v)
        if gives in ("numbers", "fractions"):
            out = []
            for item in found:
                if isinstance(item, list):  # the repeating part of a periodic continued fraction
                    out.append({"number": number, "answer": math.nan, "answer exactly": "[" + ", ".join(
                        _show(i) for i in item) + "]"})
                    continue
                value = sp.Rational(item)
                whole = value.q == 1
                out.append({"number": number, "answer": float(value) if not whole or abs(value) <= BIGGEST_EXACT
                            else math.nan, "answer exactly": _show(value)})
            return out
        if gives == "pair":
            empty = found is None or found is False
            first, second = (math.nan, math.nan) if empty else found
            if key == "perfect power":
                return [{"number": number, "base": float(first), "power": float(second)}]
            name = "root" if key == "whole nth root" else "log"
            return [{"number": number, name: float(first), "exact": bool(second) if not empty else False}]
        if gives == "pairs":
            return [{"number": number, "powers": str(tuple(int(p) for p in powers)), "coefficient": float(c)
                     if c <= BIGGEST_EXACT else math.nan, "coefficient exactly": str(c)}
                    for powers, c in sorted(found.items(), reverse=True)]
        return []

    def _list_fact(self, sp, key, call, what, values, extra, fast):
        from .._formula import _guarded, _result_rows, _show
        from .._formula_algebra import _back

        if key == "greatest common divisor" or key == "least common multiple":
            found = _guarded(call, *values, what=what)
            print(f"The {key} of {', '.join(str(v) for v in values[:12])}"
                  f"{' ...' if len(values) > 12 else ''}: {found}   ({what})")
            return _out_number(int(found)) if _out_number(int(found)) is not None else _show(found)
        if key == "number from continued fraction":
            found = _guarded(call, values, what=what)
            print(f"The number with the continued fraction {values}: {_show(found)}   ({what})")
            return _back(sp, found)
        if key == "periodic continued fraction":
            if len(values) != 3 or values[1] == 0 or values[2] < 0:
                raise SimplydataError('find_number_fact("periodic continued fraction") needs the list [p, q, d] for '
                                      "(p + sqrt(d))/q, q not 0 and d at least 0.")
            found = _guarded(call, *values, what=what)
            print(f"The continued fraction of ({values[0]} + sqrt({values[2]}))/{values[1]}: {found}; the terms in "
                  f"brackets repeat   ({what})")
            rows = self._fact_rows(sp, key, "numbers", values[0], found)
            return _result_rows([{"answer": r["answer"], "answer exactly": r["answer exactly"]} for r in rows], fast)
        # quadratic congruence
        if len(values) != 3:
            raise SimplydataError('find_number_fact("quadratic congruence") needs the list [a, b, c] of a*x**2 + b*x + '
                                  "c, and modulo=.")
        if "modulo" not in extra:
            raise SimplydataError('find_number_fact("quadratic congruence") needs modulo=, such as modulo=8.')
        found = _guarded(call, *values, extra["modulo"], what=what)
        a, b, c = values
        print(f"{a}*x**2 + {b}*x + {c} = 0 modulo {extra['modulo']} when x is "
              f"{', '.join(str(r) for r in found) or 'never'}   ({what})")
        from .numbers import Numbers

        return Numbers(np.array([float(r) for r in found], dtype=float))
