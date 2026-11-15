"""Power: how many values a study needs, and its chance to find a real difference.

Before a study, two questions: how many values do I need (how_many_needed), and with the
values I can get, what is the chance to find a real difference of the size I expect
(chance_to_find, the "power")? test= names the simplydata test the study will use.
Numbers come from statsmodels' power classes (TTestIndPower, TTestPower, FTestAnovaPower,
GofChisquarePower, with their solve_power for the number needed) and, for correlations, from
R pwr::pwr.r.test through simplydata[r]; they match R, so results can be checked there:

* compare_averages, 2 groups: two-sample t-test power, R power.t.test() (type = "two.sample").
  Effect size: Cohen's d, the difference in standard deviations (or difference= / spread=).
  It uses the usual equal-spread formula; simplydata's compare_averages uses Welch's
  t-test, which gives almost the same power when the groups are the same size.
* compare_averages, 3 or more groups: one-way ANOVA power for groups of the same size,
  R pwr::pwr.anova.test(). Effect size: Cohen's f, the spread (standard deviation) of the
  group averages divided by the spread within the groups. Again the equal-spread formula,
  close to Welch's ANOVA when the groups are the same size.
* compare_before_after: paired t-test power, R power.t.test(type = "paired"). Effect size:
  Cohen's d_z, the average change divided by the standard deviation of the changes.
* compare_average_to: one-sample t-test power, R power.t.test(type = "one.sample").
* compare_counts: chi-square test power, R pwr::pwr.chisq.test(), with Cohen's w. groups=3
  means 3 groups compared on a yes/no outcome (2 degrees of freedom); groups=(3, 4) means
  3 groups and an outcome with 4 kinds: (3 - 1) x (4 - 1) = 6 degrees of freedom.
  values_per_group times the number of groups is R's N. The formula has no Yates
  correction, so for 2 x 2 tables it is a little hopeful compared with compare_counts.
* correlation_between: R pwr::pwr.r.test(), Fisher's arctanh approximation. Effect: r.

As in R power.t.test(), a two-sided t-test counts only the chance of finding the difference
in the right direction (strict = FALSE); the other direction adds almost nothing. With
statsmodels this is the one-sided power at half the significance level (alternative="larger",
alpha = significance / 2), which is exactly R's default. One-sided
tests (sides=1) look in the direction of the expected difference, so the sign of the effect
does not matter. The needed number is always rounded UP to a whole number; the exact value
is in the result too.

Cohen's rough words for effect sizes are only a hint (sizes from your own field are better):
d 0.2 small, 0.5 medium, 0.8 large; f 0.1, 0.25, 0.4; w 0.1, 0.3, 0.5; r 0.1, 0.3, 0.5.
"""

from __future__ import annotations

import math

from ._errors import SimplydataError, choice_error, friendly

TESTS = ("compare_averages", "compare_before_after", "compare_average_to", "compare_counts",
         "correlation_between")
# Cohen's (1988) rough sizes: small, medium, large
COHEN = {"d": (0.2, 0.5, 0.8), "f": (0.1, 0.25, 0.4), "w": (0.1, 0.3, 0.5), "r": (0.1, 0.3, 0.5)}
EFFECT_NAMES = {"d": "Cohen's d", "f": "Cohen's f", "w": "Cohen's w", "r": "correlation r"}
LARGEST = 1e9  # the most values per group searched (as R pwr; power.t.test stops at 1e7)


def _num(x) -> str:
    """3 significant digits without trailing zeros: 0.5, 0.05, 0.681, 10."""
    from .table.stat_tests import _num as num

    text = num(x)
    if "." in text and "e" not in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _percent(share: float) -> str:
    return f"{share * 100:.3g} %"


def _a(text: str) -> str:
    """'an 80 % chance', 'a 90 % chance'."""
    spoken_an = text.startswith("8") or (text[:2] in ("11", "18") and not text[:3].isdigit())
    return "an" if spoken_an else "a"


def _number(step, option, value, example):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise SimplydataError(f"{step}() needs {option}= as a number, for example {example}.")
    return float(value)


def _whole_or_num(x) -> str:
    return str(int(x)) if float(x).is_integer() else _num(x)


def _cohen_words(kind: str, size: float) -> str:
    small, medium, large = COHEN[kind]
    word = ("very small" if size < small else "small" if size < medium else
            "medium" if size < large else "large")
    return (f"Cohen's rough guide calls this a {word} effect "
            f"({EFFECT_NAMES[kind]}: {_num(small)} small, {_num(medium)} medium, {_num(large)} large); "
            "it is only a hint, sizes from your own field are better.")


def _plan(step, test, effect_size, difference, spread, significance, groups, sides):
    """Check the inputs and describe the calculation: power(n) for n values per group, and the words."""
    if not isinstance(test, str) or test not in TESTS:
        raise choice_error(step, "test", test, TESTS)
    if isinstance(sides, bool) or sides not in (1, 2):
        raise SimplydataError(f"{step}() needs sides=2 (a difference in either direction, the usual) "
                              "or sides=1 (only in the direction you expect).")
    significance = _number(step, "significance", significance, "significance=0.05")
    if not 0 < significance < 1:
        raise SimplydataError(f"{step}() needs significance= between 0 and 1, for example 0.05.")

    # ------------------------------------------------ groups and the kind of calculation
    df = None
    if test == "compare_counts":
        k, kinds = (tuple(groups) if isinstance(groups, (tuple, list)) and len(groups) == 2 else (groups, 2))
        for value in (k, kinds):
            if isinstance(value, bool) or not isinstance(value, int) or value < 2:
                raise SimplydataError(
                    f"{step}() needs groups= as a whole number of 2 or more (groups compared on a yes/no "
                    "outcome), or as (groups, kinds of outcome), for example groups=(3, 4).")
        kind, df = "w", (k - 1) * (kinds - 1)
    elif test == "compare_averages":
        if isinstance(groups, bool) or not isinstance(groups, int) or groups < 2:
            raise SimplydataError(f"{step}() needs groups= as a whole number of 2 or more, for example groups=3.")
        k = groups
        kind = "d" if k == 2 else "f"
        if kind == "f":
            df = k - 1
    else:
        if isinstance(groups, bool) or groups not in (1, 2):
            raise SimplydataError(f'groups= is not used with test="{test}"; leave it out.')
        k = 1
        kind = "r" if test == "correlation_between" else "d"
    if kind in ("f", "w") and sides == 1:
        what = "The F test (ANOVA)" if kind == "f" else "The chi-square test"
        raise SimplydataError(f"{what} looks for differences in every direction at once, so sides=1 "
                              "does not apply; leave sides= out.")

    # ------------------------------------------------ the effect size
    if effect_size is not None and (difference is not None or spread is not None):
        raise SimplydataError(f"{step}() needs effect_size= OR difference= and spread=, not both.")
    if effect_size is None and difference is None and spread is None:
        example = {"d": "effect_size=0.5 (Cohen's d), or difference=5, spread=10",
                   "f": "effect_size=0.25 (Cohen's f)", "w": "effect_size=0.3 (Cohen's w)",
                   "r": "effect_size=0.3 (the correlation r)"}[kind]
        raise SimplydataError(f"{step}() needs the size of the difference you hope to find, for example "
                              f"{example}.")
    given = {}
    if effect_size is None:
        if kind != "d":
            raise SimplydataError("difference= and spread= work for the t-tests (2 groups, before/after, "
                                  f"average to a value). Here give effect_size= ({EFFECT_NAMES[kind]}).")
        if difference is None or spread is None:
            raise SimplydataError(f"{step}() needs both difference= and spread= (the standard deviation), "
                                  "for example difference=5, spread=10.")
        difference = _number(step, "difference", difference, "difference=5")
        spread = _number(step, "spread", spread, "spread=10")
        if spread <= 0:
            raise SimplydataError("spread= (the standard deviation) must be more than 0.")
        effect = difference / spread
        given = {"difference": difference, "spread": spread}
    else:
        effect = _number(step, "effect_size", effect_size, "effect_size=0.5")
    if kind in ("f", "w") and effect < 0:
        raise SimplydataError(f"{EFFECT_NAMES[kind]} cannot be below 0.")
    if kind == "r" and not -1 < effect < 1:
        raise SimplydataError("A correlation r must be between -1 and 1.")
    effect = abs(effect)
    if effect == 0:
        raise SimplydataError("A difference of 0 can never be found; give the smallest difference that matters.")

    # ------------------------------------------------ power for n values per group (package calls)
    if kind == "d":
        from statsmodels.stats.power import TTestIndPower, TTestPower

        engine = TTestIndPower() if test == "compare_averages" else TTestPower()
        options = dict(effect_size=effect, alpha=significance / sides, alternative="larger")
        size = "nobs1" if test == "compare_averages" else "nobs"  # statsmodels' names for the group size

        def power(n):
            return float(engine.power(**{size: n}, **options))

        def solve(target):
            return float(engine.solve_power(**{size: None}, power=target, **options))
        lowest = 2.0
        method = {"compare_averages": "two-sample t-test power, as R power.t.test()",
                  "compare_before_after": 'paired t-test power, as R power.t.test(type = "paired")',
                  "compare_average_to": 'one-sample t-test power, as R power.t.test(type = "one.sample")'}[test]
    elif kind == "f":
        from statsmodels.stats.power import FTestAnovaPower

        def power(n):  # nobs is every value in all groups, as R pwr's k * n
            return float(FTestAnovaPower().power(effect_size=effect, nobs=n * k, alpha=significance, k_groups=k))

        def solve(target):
            return float(FTestAnovaPower().solve_power(effect_size=effect, nobs=None, alpha=significance,
                                                       power=target, k_groups=k)) / k
        lowest = 2.0
        method = "one-way ANOVA power for groups of the same size, as R pwr::pwr.anova.test()"
    elif kind == "w":
        from statsmodels.stats.power import GofChisquarePower

        def power(n):
            return float(GofChisquarePower().power(effect_size=effect, nobs=n * k, alpha=significance,
                                                   n_bins=df + 1))

        def solve(target):
            return float(GofChisquarePower().solve_power(effect_size=effect, nobs=None, alpha=significance,
                                                         power=target, n_bins=df + 1)) / k
        lowest = 1.0 / k
        method = "chi-square test power, as R pwr::pwr.chisq.test()"
    else:
        alternative = "two.sided" if sides == 2 else "greater"

        def _pwr(n=None, target=None):
            from ._r import r_call

            n_text = "NULL" if n is None else repr(float(n))
            power_text = "NULL" if target is None else repr(float(target))
            found = r_call(f'pwr::pwr.r.test(n = {n_text}, r = {effect!r}, sig.level = {significance!r}, '
                           f'power = {power_text}, alternative = "{alternative}")[c("n", "power")]',
                           packages=("pwr",), what="Power for a correlation (R pwr::pwr.r.test())",
                           python_note="statsmodels has no power class for correlations")
            return float(found["n"][0]), float(found["power"][0])

        def power(n):
            return _pwr(n=n)[1]

        def solve(target):
            return _pwr(target=target)[0]
        lowest = 4.0
        method = "correlation power (Fisher's arctanh approximation), as R pwr::pwr.r.test()"

    # ------------------------------------------------ words
    shown = _num(effect)
    if kind == "d":
        if given:
            sd_words = "a standard deviation of the changes" if test == "compare_before_after" else \
                "a standard deviation"
            sizes = f"{_num(abs(difference))} (with {sd_words} of {_num(spread)}: Cohen's d = {shown})"
        elif test == "compare_before_after":
            sizes = f"{shown} standard deviations of the changes (Cohen's d)"
        else:
            sizes = f"{shown} standard deviations (Cohen's d)"
        effect_words = {"compare_averages": f"a difference of {sizes}",
                        "compare_before_after": f"an average change of {sizes}",
                        "compare_average_to": f"a difference from your value of {sizes}"}[test]
    elif kind == "f":
        effect_words = (f"differences between the {k} group averages of Cohen's f = {shown} (the spread of "
                        "the group averages, in standard deviations)")
    elif kind == "w":
        effect_words = f"a difference in counts of Cohen's w = {shown}"
    else:
        effect_words = f"a correlation of r = {shown}"
    if kind in ("d", "r"):
        test_words = f"a {'two' if sides == 2 else 'one'}-sided test at {_num(significance)}"
    elif kind == "f":
        test_words = f"the F test at {_num(significance)}"
    else:
        test_words = (f"the chi-square test at {_num(significance)} ({df} degree{'' if df == 1 else 's'} "
                      "of freedom)")

    def amount(n):
        if test in ("compare_averages", "compare_counts"):
            return f"{_whole_or_num(n)} values in each group ({_whole_or_num(n * k)} in all)"
        if test == "compare_before_after":
            return f"{_whole_or_num(n)} pairs (a before and an after value each)"
        if test == "correlation_between":
            return f"{_whole_or_num(n)} pairs of values"
        return f"{_whole_or_num(n)} values"

    notes = []
    if test == "compare_averages":
        notes.append("Note: the calculation uses the usual equal-spread formula; compare_averages uses Welch's "
                     f"{'t-test' if k == 2 else 'ANOVA'}, which is very close to it when the groups are "
                     "the same size.")
    if kind == "w" and df == 1:
        notes.append("Note: the formula has no Yates correction, so for a 2 x 2 table compare_counts is a "
                     "little less likely to find the difference than this says.")
    notes.append(_cohen_words(kind, effect))

    method_name, r_function = method.split(", as R ")
    row = {"test": test, "method": method_name, "R function": r_function,
           "effect size name": EFFECT_NAMES[kind], "effect size": effect, **given, "groups": k}
    if df is not None:
        row["degrees of freedom"] = df
    if kind in ("d", "r"):
        row["sides"] = sides
    row["significance"] = significance
    return {"power": power, "solve": solve, "lowest": lowest, "method": method, "effect_words": effect_words,
            "test_words": test_words, "amount": amount, "notes": notes, "row": row, "k": k}


def _percents(step, test, percents, sides, significance):
    """percents=[30, 15]: the two percents of a yes/no outcome the study expects (compare_counts, 2 groups)."""
    if test != "compare_counts":
        raise SimplydataError('percents= goes with test="compare_counts" (two groups compared on a yes/no outcome).')
    if (not isinstance(percents, (list, tuple)) or len(percents) != 2
            or not all(isinstance(v, (int, float)) and not isinstance(v, bool) and 0 < v < 100 for v in percents)):
        raise SimplydataError(f"{step}() needs percents= as two percents between 0 and 100, the percent with the "
                              "outcome expected in each group, for example percents=[30, 15].")
    if percents[0] == percents[1]:
        raise SimplydataError("The two percents are the same, so there is no difference to find.")
    if isinstance(sides, bool) or sides not in (1, 2):
        raise SimplydataError(f"{step}() needs sides=2 (the usual) or sides=1.")
    significance = _number(step, "significance", significance, "significance=0.05")
    if not 0 < significance < 1:
        raise SimplydataError(f"{step}() needs significance= between 0 and 1, for example 0.05.")
    return percents[0] / 100, percents[1] / 100, significance


def _percents_words(p1, p2, sides, significance):
    return (f"{_num(p1 * 100)} % against {_num(p2 * 100)} % with the outcome", f"a {'two' if sides == 2 else 'one'}"
            f"-sided test at {_num(significance)}")


def _percents_power(p1, p2, n, sides, significance):
    """statsmodels power_proportions_2indep (as R power.prop.test())."""
    from statsmodels.stats.proportion import power_proportions_2indep

    alternative = "two-sided" if sides == 2 else ("larger" if p1 > p2 else "smaller")
    return float(power_proportions_2indep(p1 - p2, p2, n, ratio=1, alpha=significance,
                                          alternative=alternative).power)


def _equivalence_plan(step, test, same_within, difference, spread, significance):
    """same_within= in power: R TOSTER::power_t_TOST (Python has no power for two one-sided tests)."""
    from .table.equivalence import margin

    kinds = {"compare_averages": "two.sample", "compare_before_after": "paired", "compare_average_to": "one.sample"}
    if test not in kinds:
        raise SimplydataError('same_within= in power works with test="compare_averages", "compare_before_after" '
                              'or "compare_average_to".')
    if spread is None:
        raise SimplydataError(f"{step}() with same_within= needs spread= (the standard deviation), for example "
                              "same_within=5, spread=10.")
    low, high = margin(step, same_within)
    spread = _number(step, "spread", spread, "spread=10")
    difference = 0.0 if difference is None else _number(step, "difference", difference, "difference=0")
    significance = _number(step, "significance", significance, "significance=0.05")
    if spread <= 0:
        raise SimplydataError("spread= (the standard deviation) must be more than 0.")
    if not low < difference < high:
        raise SimplydataError("difference= (the true difference you expect) must lie inside the margin.")

    def call(n=None, power=None):
        from ._r import r_call

        found = r_call("r <- TOSTER::power_t_TOST(n = if (is.na(n)) NULL else n, delta = d, sd = s, low_eqbound = lo, high_eqbound = hi, "
                       "alpha = a, power = if (is.na(pw)) NULL else pw, type = ty); list(n = r$n, power = r$power)", packages=("TOSTER",),
                       what="Power for two one-sided tests (R TOSTER::power_t_TOST())",
                       python_note="Python has no power calculation for equivalence tests",
                       n=math.nan if n is None else float(n), d=difference, s=spread, lo=low, hi=high,
                       a=significance, pw=math.nan if power is None else float(power), ty=kinds[test])
        return float(found["n"][0]), float(found["power"][0])

    words = (f"that the difference lies within {low:g} to {high:g} (when the true difference is {_num(difference)} "
             f"and the standard deviation {_num(spread)})", f"two one-sided tests at {_num(significance)}")
    row = {"test": test, "method": "power of two one-sided tests (TOST)", "R function": "TOSTER::power_t_TOST()",
           "difference": difference, "spread": spread, "margin low": low, "margin high": high,
           "significance": significance}
    return call, words, row


def _equivalence_amount(test, n):
    if test == "compare_averages":
        return f"{_whole_or_num(n)} values in each group ({_whole_or_num(2 * n)} in all)"
    if test == "compare_before_after":
        return f"{_whole_or_num(n)} pairs (a before and an after value each)"
    return f"{_whole_or_num(n)} values"


def _no_ranks(step, based_on):
    if based_on == "ranks":
        raise SimplydataError(f"{step}() for rank tests is not offered: no established Python or R package gives it "
                              "in a form simplydata can call. The t-test numbers are a close guide for rank tests "
                              "on bell-shaped values (a rank test needs about 5 % more).")
    if based_on != "averages":
        raise choice_error(step, "based_on", based_on, ("averages", "ranks"))


def _interval_width_needed(step, width, spread, significance):
    """how_many_needed(interval_width=, spread=): R presize::prec_mean (Python has none)."""
    width = _number(step, "interval_width", width, "interval_width=4")
    if spread is None:
        raise SimplydataError(f"{step}() with interval_width= needs spread= (the standard deviation you expect), "
                              "for example interval_width=4, spread=10.")
    spread = _number(step, "spread", spread, "spread=10")
    significance = _number(step, "significance", significance, "significance=0.05")
    if width <= 0 or spread <= 0:
        raise SimplydataError("interval_width= and spread= must be more than 0.")
    from ._r import r_call

    exact = float(r_call("presize::prec_mean(mean = 0, sd = s, conf.width = w, conf.level = 1 - a)$n",
                         packages=("presize",), what="The number needed for an interval width (R presize::prec_mean())",
                         python_note="Python has no function for it", s=spread, w=width, a=significance)[0])
    needed = math.ceil(exact - 1e-9)
    level = _num((1 - significance) * 100)
    print(f"For a {level} % confidence interval of an average that is {_num(width)} wide (from end to end), with a "
          f"standard deviation of {_num(spread)}, you need {needed} values. Method: R presize::prec_mean().")
    return _result({"method": "sample size for an interval width", "R function": "presize::prec_mean()",
                    "interval width": width, "spread": spread, "interval level": (1 - significance) * 100,
                    "values (exact)": exact, "values": needed})


def _result(row: dict):
    import pandas as pd

    from .table import table

    return table(pd.DataFrame([row]))


@friendly
def how_many_needed(test="compare_averages", effect_size=None, difference=None, spread=None, power=0.8,
                    significance=0.05, groups=2, sides=2, percents=None, same_within=None, interval_width=None,
                    based_on="averages"):
    """How many values (in each group) does a study need to find a real difference?

    sdata.how_many_needed(effect_size=0.5)       (two groups, a medium difference: 64 in each)
    test= is the simplydata test the study will use: "compare_averages" (2 groups: t-test;
    groups=3 or more: ANOVA with Cohen's f), "compare_before_after" (paired, Cohen's d of the
    changes), "compare_average_to" (one sample), "compare_counts" (chi-square with Cohen's w;
    groups=(groups, kinds of outcome)) or "correlation_between" (r; the answer is pairs).
    The size of the difference: effect_size= (Cohen's d, f, w or r, the sentence says which),
    or difference= and spread= (the standard deviation) for the t-tests.
    power= is the chance you want to find it (0.8 is usual); significance= is the p-value
    limit (0.05); sides=1 looks only in the direction you expect.
    The t-tests use the usual equal-spread formula (R power.t.test()), very close to Welch's
    t-test when the groups are the same size; the others match R pwr. Numbers come from
    statsmodels (correlations: R pwr.r.test through simplydata[r]). The number is rounded
    UP to a whole number; the exact value is in the result. Gives back a one-row table.
    test="compare_counts", percents=[30, 15]: two groups compared on a yes/no outcome, with the
    percents you expect (R power.prop.test(), run through simplydata[r]; chance_to_find gives
    the same power from statsmodels power_proportions_2indep).
    same_within=5, spread=10 (difference=0 by default): the number needed to show the groups are
    the same within 5 with two one-sided tests (R TOSTER::power_t_TOST()).
    interval_width=4, spread=10: the number needed for a 95 % interval of an average that is 4
    wide from end to end (R presize::prec_mean()).
    """
    step = "how_many_needed"
    _no_ranks(step, based_on)
    target = _number(step, "power", power, "power=0.8")
    if not 0 < target < 1:
        raise SimplydataError(f"{step}() needs power= between 0 and 1, for example 0.8 (an 80 % chance).")
    if interval_width is not None:
        return _interval_width_needed(step, interval_width, spread, significance)
    if percents is not None:
        p1, p2, alpha = _percents(step, test, percents, sides, significance)
        from ._r import r_call

        found = r_call("power.prop.test(p1 = p1, p2 = p2, sig.level = a, power = pw, alternative = alt)$n",
                       packages=(), what="The number needed to compare two percents (R power.prop.test())",
                       python_note="statsmodels samplesize_proportions_2indep_onetail() gives a one-tail "
                                   "approximation that differs from R",
                       p1=p1, p2=p2, a=alpha, pw=target, alt="two.sided" if sides == 2 else "one.sided")
        exact = float(found[0])
        needed = math.ceil(exact - 1e-9)
        effect, test_words = _percents_words(p1, p2, sides, alpha)
        print(f"To find {effect} with {_a(_percent(target))} {_percent(target)} chance, using {test_words}, you need "
              f"{needed} values in each group ({2 * needed} in all). Method: power for two percents, as R "
              "power.prop.test().")
        return _result({"test": test, "method": "power for two percents", "R function": "power.prop.test()",
                        "percent 1": p1 * 100, "percent 2": p2 * 100, "sides": sides, "significance": alpha,
                        "power wanted": target, "values per group (exact)": exact, "values per group": needed,
                        "values in all": 2 * needed,
                        "power with that many": _percents_power(p1, p2, needed, sides, alpha)})
    if same_within is not None:
        call, (effect, test_words), row = _equivalence_plan(step, test, same_within, difference, spread, significance)
        exact = call(power=target)[0]
        needed = math.ceil(exact - 1e-9)
        print(f"To show {effect} with {_a(_percent(target))} {_percent(target)} chance, using {test_words}, you need "
              f"{_equivalence_amount(test, needed)}. Method: power of two one-sided tests, as R "
              "TOSTER::power_t_TOST().")
        row.update({"power wanted": target, "values per group (exact)": exact, "values per group": needed,
                    "power with that many": call(n=needed)[1]})
        return _result(row)
    plan = _plan(step, test, effect_size, difference, spread, significance, groups, sides)
    if target <= plan["row"]["significance"]:
        raise SimplydataError("power= must be more than significance=: even with no real difference, a test "
                              "finds one that often by chance.")
    chance, lowest, k = plan["power"], plan["lowest"], plan["k"]
    notes = list(plan["notes"])
    if chance(lowest) >= target:
        exact = lowest
        notes.insert(0, "Note: the difference is so large that even the smallest possible study reaches this "
                        "chance.")
    else:
        if chance(LARGEST) < target:
            raise SimplydataError("The difference is too small to find with any practical study (more than "
                                  f"{LARGEST:,.0f} values in each group). Check the effect size.")
        exact = plan["solve"](target)
    needed = max(math.ceil(exact - 1e-9), math.ceil(lowest))
    reached = chance(needed)
    print(f"To find {plan['effect_words']} with {_a(_percent(target))} {_percent(target)} chance, using "
          f"{plan['test_words']}, you need {plan['amount'](needed)}. Method: {plan['method']}.")
    for note in notes:
        print(note)
    row = dict(plan["row"])
    row.update({"power wanted": target, "values per group (exact)": exact, "values per group": needed,
                "values in all": needed * k, "power with that many": reached})
    return _result(row)


@friendly
def chance_to_find(test="compare_averages", effect_size=None, difference=None, spread=None,
                   values_per_group=None, significance=0.05, groups=2, sides=2, percents=None, same_within=None,
                   based_on="averages"):
    """What chance does a study have to find a real difference of a given size (its power)?

    sdata.chance_to_find(effect_size=0.5, values_per_group=30)   (two groups of 30: about 48 %)
    The same options as how_many_needed(), with values_per_group= instead of power=: the
    number in each group (pairs for compare_before_after and correlation_between; all the
    values for compare_average_to). The t-tests use the usual equal-spread formula (R
    power.t.test()), very close to Welch's t-test when the groups are the same size; the
    others match R pwr. Gives back a one-row table.
    test="compare_counts", percents=[30, 15]: two groups compared on a yes/no outcome
    (statsmodels power_proportions_2indep, as R power.prop.test()). same_within=5, spread=10:
    the chance that two one-sided tests show the groups are the same within 5 (R
    TOSTER::power_t_TOST()).
    """
    step = "chance_to_find"
    _no_ranks(step, based_on)
    if values_per_group is None:
        raise SimplydataError(f"{step}() needs values_per_group=, the number of values in each group, "
                              "for example values_per_group=30.")
    n = _number(step, "values_per_group", values_per_group, "values_per_group=30")
    if percents is not None:
        p1, p2, alpha = _percents(step, test, percents, sides, significance)
        chance = _percents_power(p1, p2, n, sides, alpha)
        effect, test_words = _percents_words(p1, p2, sides, alpha)
        shown = _percent(chance)
        print(f"With {_whole_or_num(n)} values in each group, a study has {_a(shown)} {shown} chance (power = "
              f"{_num(chance)}) to find {effect}, using {test_words}. Method: statsmodels "
              "power_proportions_2indep(), as R power.prop.test().")
        return _result({"test": test, "method": "power for two percents", "R function": "power.prop.test()",
                        "percent 1": p1 * 100, "percent 2": p2 * 100, "sides": sides, "significance": alpha,
                        "values per group": n, "values in all": 2 * n, "power": chance})
    if same_within is not None:
        call, (effect, test_words), row = _equivalence_plan(step, test, same_within, difference, spread, significance)
        chance = call(n=n)[1]
        shown = _percent(chance)
        print(f"With {_equivalence_amount(test, n)}, a study has {_a(shown)} {shown} chance (power = {_num(chance)}) "
              f"to show {effect}, using {test_words}. Method: power of two one-sided tests, as R "
              "TOSTER::power_t_TOST().")
        row.update({"values per group": n, "power": chance})
        return _result(row)
    plan = _plan(step, test, effect_size, difference, spread, significance, groups, sides)
    least = 4 if test == "correlation_between" else 2
    if n < least:
        raise SimplydataError(f"{step}() needs values_per_group= of at least {least}"
                              f"{' (pairs of values)' if least == 4 else ''}.")
    chance = plan["power"](n)
    k = plan["k"]
    shown = _percent(chance)
    print(f"With {plan['amount'](n)}, a study has {_a(shown)} {shown} chance (power = {_num(chance)}) to find "
          f"{plan['effect_words']}, using {plan['test_words']}. Method: {plan['method']}.")
    if chance < 0.8:
        print("Note: this is below the usual 80 %; how_many_needed() tells you how many values you need.")
    for note in plan["notes"]:
        print(note)
    row = dict(plan["row"])
    row.update({"values per group": n, "values in all": n * k, "power": chance})
    return _result(row)
