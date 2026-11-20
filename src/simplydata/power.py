"""Power: how many values a study needs, and its chance to find a real difference.

Before a study, two questions: how many values do I need (find_how_many_needed), and with the
values I can get, what is the chance to find a real difference of the size I expect
(find_chance_of_finding, the "power")? test= names the simplydata test the study will use.
Numbers come from statsmodels' power classes (TTestIndPower, TTestPower, FTestAnovaPower,
GofChisquarePower, with their solve_power for the number needed) and, for correlations, from
R pwr::pwr.r.test through simplydata[r]; they match R, so results can be checked there:

* compare_averages, 2 groups: two-sample t-test power, R power.t.test() (type = "two.sample").
  Effect size: Cohen's d, the difference in standard deviations (or difference= / spread=).
  It uses the usual equal-spread formula; simplydata's compare_averages_of uses Welch's
  t-test, which gives almost the same power when the groups are the same size.
* compare_averages, 3 or more groups: one-way ANOVA power for groups of the same size,
  R pwr::pwr.anova.test(). Effect size: Cohen's f, the spread (standard deviation) of the
  group averages divided by the spread within the groups. Again the equal-spread formula,
  close to Welch's ANOVA when the groups are the same size.
* compare_before_and_after: paired t-test power, R power.t.test(type = "paired"). Effect size:
  Cohen's d_z, the average change divided by the standard deviation of the changes.
* compare_average_to: one-sample t-test power, R power.t.test(type = "one.sample").
* compare_counts: chi-square test power, R pwr::pwr.chisq.test(), with Cohen's w. groups=3
  means 3 groups compared on a yes/no outcome (2 degrees of freedom); groups=(3, 4) means
  3 groups and an outcome with 4 kinds: (3 - 1) x (4 - 1) = 6 degrees of freedom.
  values_per_group times the number of groups is R's N. The formula has no Yates
  correction, so for 2 x 2 tables it is a little hopeful compared with compare_counts.
* find_correlation_between: R pwr::pwr.r.test(), Fisher's arctanh approximation. Effect: r.

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
# S3b-2: tests with routes of their own (power_more.py)
MORE_TESTS = ("explain", "compare_models", "compare_survival", "compare_spreads")
# test= may also name the table word as it is written now (2026-11-16 talking rewrite)
TEST_WORDS = {"compare_averages_of": "compare_averages", "compare_before_and_after": "compare_before_after",
              "compare_counts_of": "compare_counts", "find_correlation_between": "correlation_between",
              "compare_spreads_of": "compare_spreads"}
# Cohen's (1988) rough sizes: small, medium, large
# (never printed for a hazard ratio or an odds ratio)
COHEN = {"d": (0.2, 0.5, 0.8), "f": (0.1, 0.25, 0.4), "w": (0.1, 0.3, 0.5), "r": (0.1, 0.3, 0.5),
         "f2": (0.02, 0.15, 0.35)}
EFFECT_NAMES = {"d": "Cohen's d", "f": "Cohen's f", "w": "Cohen's w", "r": "correlation r", "f2": "Cohen's f²"}
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
    if isinstance(test, str):
        test = TEST_WORDS.get(test, test)
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
        notes.append("Note: the calculation uses the usual equal-spread formula; table.compare_averages_of uses Welch's "
                     f"{'t-test' if k == 2 else 'ANOVA'}, which is very close to it when the groups are "
                     "the same size.")
    if kind == "w" and df == 1:
        notes.append("Note: the formula has no Yates correction, so for a 2 x 2 table table.compare_counts_of is a "
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


def _route(step, test, based_on, drawing_from, by_running, interval_width, percents, same_within, using, against,
           outcome, method, clusters, values_per_group=None):
    """Which calculation a call asks for, and a clear error for options that do not go with it."""
    if isinstance(test, str):
        test = TEST_WORDS.get(test, test)
    if not isinstance(test, str) or test not in TESTS + MORE_TESTS:
        raise choice_error(step, "test", test, TESTS + MORE_TESTS)
    if based_on not in ("averages", "ranks"):
        raise choice_error(step, "based_on", based_on, ("averages", "ranks"))
    if outcome not in ("numbers", "yes or no"):
        raise SimplydataError("outcome= in power is \"numbers\" (regression, with Cohen's f²) or \"yes or no\" "
                              "(logistic regression), with test=\"explain\".")
    if based_on == "ranks" and test not in ("compare_averages", "compare_before_after"):
        raise SimplydataError('based_on="ranks" goes with test="compare_averages" (Mann-Whitney) and '
                              '"compare_before_and_after" (Wilcoxon signed-rank).')
    if by_running is not None:
        route = "by_running"
    elif interval_width is not None:
        route = "interval"
    elif test == "compare_survival":
        route = "survival"
    elif test in ("explain", "compare_models"):
        route = "logistic" if outcome == "yes or no" else "regression"
    elif based_on == "ranks" or drawing_from is not None or test == "compare_spreads":
        route = "simulation"
    elif percents is not None:
        route = "percents"
    elif same_within is not None:
        route = "same_within"
    else:
        route = "formula"
    uses = {"using": route in ("regression", "logistic"), "against": route == "regression",
            "outcome": route in ("regression", "logistic"), "method": route == "survival",
            "clusters": route in ("formula", "percents"), "drawing_from": route == "simulation",
            "percents": route in ("interval", "survival", "logistic", "percents")}
    given = {"using": using is not None, "against": against is not None, "outcome": outcome != "numbers",
             "method": method is not None, "clusters": clusters is not None, "drawing_from": drawing_from is not None,
             "percents": percents is not None}
    for option, is_given in given.items():
        if is_given and not uses[option]:
            name = {"clusters": "in_clusters_of= and alike_within_clusters="}.get(option, option + "=")
            where = {"using": 'test="explain" or test="compare_models"', "against": 'test="compare_models"',
                     "outcome": 'test="explain"', "method": 'test="compare_survival"',
                     "clusters": 'the formula routes (compare_averages, compare_counts, compare_average_to, '
                                 'compare_before_and_after)',
                     "drawing_from": 'test="compare_averages", "compare_before_and_after" or "compare_spreads_of"',
                     "percents": 'test="compare_counts", test="compare_survival", outcome="yes or no" or '
                                 'interval_width='}[option]
            raise SimplydataError(f"{name} goes with {where}; it does not apply to this call, so leave it out.")
    if route != "simulation" and based_on == "ranks":
        raise SimplydataError('based_on="ranks" goes with test="compare_averages" (Mann-Whitney) and '
                              '"compare_before_and_after" (Wilcoxon signed-rank).')
    if route == "simulation" and same_within is not None:
        raise SimplydataError("same_within= is worked out by formula; leave based_on= and drawing_from= out.")
    if clusters is not None and test == "correlation_between":
        raise SimplydataError("in_clusters_of= goes with the tests that compare groups or values, not with "
                              "correlation_between.")
    if values_per_group is not None and isinstance(values_per_group, (list, tuple)) and route != "simulation":
        raise SimplydataError("A list of values_per_group= (a power curve) goes with based_on=\"ranks\" or "
                              "drawing_from=; here give one number.")
    return test, route


def _interval_width_needed(step, width, spread, significance):
    """find_how_many_needed(interval_width=, spread=): R presize::prec_mean (Python has none)."""
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




def _formula_needed(step, plan, target, clusters):
    """The formula route of find_how_many_needed (t-tests, ANOVA, chi-square, correlation), with clusters."""
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
    row = dict(plan["row"])
    row["power wanted"] = target
    if clusters is None:
        print(f"To find {plan['effect_words']} with {_a(_percent(target))} {_percent(target)} chance, using "
              f"{plan['test_words']}, you need {plan['amount'](needed)}. Method: {plan['method']}.")
        row.update({"values per group (exact)": exact, "values per group": needed, "values in all": needed * k,
                    "power with that many": chance(needed)})
    else:
        from .power_more import cluster_needed_words, cluster_row, clustered

        m, icc = clusters
        found = clustered(m, icc, independent=exact)
        test = plan["row"]["test"]
        print(f"To find {plan['effect_words']} with {_a(_percent(target))} {_percent(target)} chance, using "
              f"{plan['test_words']}, you would need {plan['amount'](needed)} if every value were independent. "
              f"Method: {plan['method']}, times the design effect.")
        for line in cluster_needed_words(m, icc, found, unit="pairs" if test == "compare_before_after" else "values",
                                         each=test in ("compare_averages", "compare_counts")):
            print(line)
        effective = clustered(m, icc, given=found["values"])["effective"]
        row.update({"values per group if independent (exact)": exact, "values per group if independent": needed,
                    **cluster_row(m, icc, found), "values per group": found["values"],
                    "values in all": found["values"] * k, "power with that many": chance(effective)})
    for note in notes:
        print(note)
    return _result(row)


def _clusters_of(step, in_clusters_of, alike_within_clusters):
    if in_clusters_of is None and alike_within_clusters is None:
        return None
    from .power_more import check_clusters

    return check_clusters(step, in_clusters_of, alike_within_clusters)


@friendly
def find_how_many_needed(test="compare_averages", effect_size=None, difference=None, spread=None, power=0.8,
                         significance=0.05, groups=2, sides=2, percents=None, same_within=None, interval_width=None,
                         based_on="averages", using=None, against=None, outcome="numbers", method=None,
                         in_clusters_of=None, alike_within_clusters=None, drawing_from=None, tries=10000,
                         with_seed=1):
    """How many values (in each group) does a study need to find a real difference?

    sdata.find_how_many_needed(effect_size=0.5)       (two groups, a medium difference: 64 in each)
    test= is the simplydata test the study will use: "compare_averages" (2 groups: t-test;
    groups=3 or more: ANOVA with Cohen's f), "compare_before_after" (paired, Cohen's d of the
    changes), "compare_average_to" (one sample), "compare_counts" (chi-square with Cohen's w;
    groups=(groups, kinds of outcome)) or "correlation_between" (r; the answer is pairs).
    The size of the difference: effect_size= (the first sentence always names its scale), or
    difference= and spread= (the standard deviation) for the t-tests. Plan with the smallest
    difference that matters, never with the one a finished study found ("observed power").
    power= is the chance you want to find it (0.8 is usual); significance= is the p-value
    limit (0.05); sides=1 looks only in the direction you expect.
    The t-tests use the usual equal-spread formula (R power.t.test()), very close to Welch's
    t-test when the groups are the same size; the others match R pwr. The number is rounded
    UP to a whole number; the exact value is in the result. Gives back a one-row table.

    More:
    test="compare_counts", percents=[30, 15]: two percents (R power.prop.test()).
    same_within=5, spread=10: show the groups are the same within 5 (R TOSTER::power_t_TOST()).
    interval_width=4, spread=10: a 95 % interval of an average 4 wide (R presize::prec_mean());
    interval_width=10, percents=[30]: a percent's interval 10 points wide (R presize::prec_prop()).
    test="compare_survival", effect_size=0.7 (a hazard ratio), percents=[30, 40]: the events
    first (Schoenfeld, R gsDesign::nEvents()), then the people if 30 % of the first group and
    40 % of the second have the event; method="freedman" uses Freedman's formula (R powerSurvEpi).
    test="explain", effect_size=0.15, using=["temperature", "salinity", "depth"]: regression with
    Cohen's f² (statsmodels FTestPowerF2, as R pwr.f2.test()); test="compare_models", using=,
    against= (the columns of each model, as on compare_models): the columns in one and not the other.
    test="explain", outcome="yes or no", using=["dose"], percents=[20], effect_size=1.5: logistic
    regression, 20 % with the outcome at the average dose, odds ratio 1.5 per standard deviation
    of dose (R pwrss::power.z.logistic(), Demidenko with variance correction).
    in_clusters_of=20, alike_within_clusters=0.05: values come in clusters of 20 (wards, farms,
    tanks) that are alike (intracluster correlation 0.05); the answer is times the design effect.
    based_on="ranks": rank tests (Mann-Whitney, Wilcoxon) by simulation (SciPy stats.power);
    drawing_from=[dist_a, dist_b]: simulate from your own distributions (sdata.distribution);
    tries=10000, with_seed=1 set the simulation.
    """
    step = "find_how_many_needed"
    clusters = _clusters_of(step, in_clusters_of, alike_within_clusters)
    test, route = _route(step, test, based_on, drawing_from, None, interval_width, percents, same_within, using,
                         against, outcome, method, clusters)
    target = _number(step, "power", power, "power=0.8")
    if not 0 < target < 1:
        raise SimplydataError(f"{step}() needs power= between 0 and 1, for example 0.8 (an 80 % chance).")
    from . import power_more

    if route == "interval":
        if percents is not None:
            return power_more.percent_interval_needed(step, interval_width, percents, significance)
        return _interval_width_needed(step, interval_width, spread, significance)
    if route == "survival":
        plan = power_more.survival_plan(step, effect_size, percents, method, groups, sides, significance, difference,
                                        spread)
        return power_more.survival_needed(step, plan, target)
    if route == "simulation":
        return power_more.simulate_needed(step, test, effect_size, difference, spread, target, drawing_from, based_on,
                                          groups, sides, significance, tries, with_seed)
    if route == "logistic":
        plan = power_more.logistic_plan(step, test, effect_size, using, against, percents, significance, sides)
        if target <= plan["significance"]:
            raise SimplydataError("power= must be more than significance=: even with no real difference, a test "
                                  "finds one that often by chance.")
        from . import power_r

        exact, _ = power_r.logistic(plan["percent"], plan["ratio"], plan["significance"], plan["sides"], power=target)
        needed = math.ceil(exact - 1e-9)
        _, reached = power_r.logistic(plan["percent"], plan["ratio"], plan["significance"], plan["sides"], n=needed)
        print(f"To find {plan['effect_words']}, with {_a(_percent(target))} {_percent(target)} chance, using "
              f"{plan['test_words']}, you need {needed} values. Method: {power_more.LOGISTIC_METHOD}.")
        for note in plan["notes"]:
            print(note)
        row = dict(plan["row"])
        row.update({"power wanted": target, "values (exact)": exact, "values": needed, "power with that many": reached})
        return _result(row)
    if route == "regression":
        plan = power_more.regression_plan(step, test, effect_size, using, against, significance, sides)
        if target <= plan["row"]["significance"]:
            raise SimplydataError("power= must be more than significance=: even with no real difference, a test "
                                  "finds one that often by chance.")
        exact = plan["solve"](target)
        needed = max(math.ceil(exact - 1e-9), int(plan["lowest"]))
        print(f"To find {plan['effect_words']} with {_a(_percent(target))} {_percent(target)} chance, using "
              f"{plan['test_words']}, you need {needed} rows (each with a value in every column). Method: "
              f"{plan['method']}.")
        for note in plan["notes"]:
            print(note)
        row = dict(plan["row"])
        row.update({"power wanted": target, "rows (exact)": exact, "rows": needed,
                    "power with that many": plan["power"](needed)})
        return _result(row)
    if route == "percents":
        return _percents_needed(step, test, percents, sides, significance, target, clusters)
    if route == "same_within":
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
    return _formula_needed(step, plan, target, clusters)


def _percents_needed(step, test, percents, sides, significance, target, clusters):
    """Two percents: R power.prop.test(), with clusters."""
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
    row = {"test": test, "method": "power for two percents", "R function": "power.prop.test()",
           "percent 1": p1 * 100, "percent 2": p2 * 100, "sides": sides, "significance": alpha, "power wanted": target}
    if clusters is None:
        print(f"To find {effect} with {_a(_percent(target))} {_percent(target)} chance, using {test_words}, you "
              f"need {needed} values in each group ({2 * needed} in all). Method: power for two percents, as R "
              "power.prop.test().")
        row.update({"values per group (exact)": exact, "values per group": needed, "values in all": 2 * needed,
                    "power with that many": _percents_power(p1, p2, needed, sides, alpha)})
        return _result(row)
    from . import power_more

    m, icc = clusters
    found = power_more.clustered(m, icc, independent=exact)
    print(f"To find {effect} with {_a(_percent(target))} {_percent(target)} chance, using {test_words}, you would "
          f"need {needed} values in each group if every value were independent. Method: power for two percents, as "
          "R power.prop.test(), times the design effect.")
    for line in power_more.cluster_needed_words(m, icc, found):
        print(line)
    effective = power_more.clustered(m, icc, given=found["values"])["effective"]
    row.update({"values per group if independent (exact)": exact, "values per group if independent": needed,
                **power_more.cluster_row(m, icc, found), "values per group": found["values"],
                "values in all": 2 * found["values"],
                "power with that many": _percents_power(p1, p2, effective, sides, alpha)})
    return _result(row)


@friendly
def find_chance_of_finding(test="compare_averages", effect_size=None, difference=None, spread=None,
                           values_per_group=None, significance=0.05, groups=2, sides=2, percents=None, same_within=None,
                           based_on="averages", using=None, against=None, outcome="numbers", method=None,
                           in_clusters_of=None, alike_within_clusters=None, drawing_from=None, tries=10000,
                           with_seed=1, by_running=None):
    """What chance does a study have to find a real difference of a given size (its power)?

    sdata.find_chance_of_finding(effect_size=0.5, values_per_group=30)   (two groups of 30: about 48 %)
    The same options as find_how_many_needed(), with values_per_group= instead of power=: the
    number in each group (pairs for compare_before_and_after and find_correlation_between; all the
    values for compare_average_to; rows for explain; people in each group for compare_survival).
    The t-tests use the usual equal-spread formula (R power.t.test()), very close to Welch's
    t-test when the groups are the same size; the others match R pwr. Gives back a one-row table.

    More:
    test="compare_counts", percents=[30, 15]: two percents (statsmodels power_proportions_2indep).
    same_within=5, spread=10: two one-sided tests (R TOSTER::power_t_TOST()).
    test="compare_survival", effect_size=0.7, values_per_group=353, percents=[30, 40] (R powerSurvEpi).
    test="explain", effect_size=0.15, using=3, values_per_group=77 (Cohen's f²); outcome="yes or no".
    in_clusters_of=20, alike_within_clusters=0.05: values in clusters (the design effect).
    based_on="ranks" or drawing_from=[dist_a, dist_b], values_per_group=[10, 20, 30]: simulated
    power, one row for each number (tries=10000, with_seed=1; SciPy stats.power).
    by_running=one_study, tries=1000: your own simulation for any test. one_study(seed) makes one
    study's data with that seed and gives back its p-value:
        def one_study(seed):
            rng = np.random.default_rng(seed)
            ...
            return p_value
    simplydata runs it with seeds 1, 2, ... (so the answer repeats; everything it prints is silenced)
    and counts the p-values below significance=.
    """
    step = "find_chance_of_finding"
    clusters = _clusters_of(step, in_clusters_of, alike_within_clusters)
    test, route = _route(step, test, based_on, drawing_from, by_running, None, percents, same_within, using,
                         against, outcome, method, clusters, values_per_group)
    from . import power_more

    if route == "by_running":
        if values_per_group is not None or effect_size is not None:
            raise SimplydataError("With by_running= your function makes each study's data, so leave values_per_group= "
                                  "and effect_size= out.")
        return power_more.chance_by_running(step, by_running, tries, with_seed, significance)
    if values_per_group is None:
        raise SimplydataError(f"{step}() needs values_per_group=, the number of values in each group, "
                              "for example values_per_group=30.")
    if route == "simulation":
        return power_more.simulate_chance(step, test, effect_size, difference, spread, values_per_group, drawing_from,
                                          based_on, groups, sides, significance, tries, with_seed)
    n = _number(step, "values_per_group", values_per_group, "values_per_group=30")
    if n <= 0:
        raise SimplydataError(f"{step}() needs values_per_group= as a number more than 0, for example "
                              "values_per_group=30.")
    if route == "survival":
        plan = power_more.survival_plan(step, effect_size, percents, method, groups, sides, significance, difference,
                                        spread)
        return power_more.survival_chance(step, plan, n)
    if route == "logistic":
        plan = power_more.logistic_plan(step, test, effect_size, using, against, percents, significance, sides)
        from . import power_r

        _, chance = power_r.logistic(plan["percent"], plan["ratio"], plan["significance"], plan["sides"], n=n)
        shown = _percent(chance)
        print(f"With {_whole_or_num(n)} values, a study has {_a(shown)} {shown} chance (power = {_num(chance)}) to "
              f"find {plan['effect_words']}, using {plan['test_words']}. Method: {power_more.LOGISTIC_METHOD}.")
        for note in plan["notes"]:
            print(note)
        row = dict(plan["row"])
        row.update({"values": n, "power": chance})
        return _result(row)
    if route == "regression":
        plan = power_more.regression_plan(step, test, effect_size, using, against, significance, sides)
        if n < plan["lowest"]:
            raise SimplydataError(f"{step}() needs at least {int(plan['lowest'])} rows for this model "
                                  "(values_per_group= is the rows here).")
        chance = plan["power"](n)
        shown = _percent(chance)
        print(f"With {_whole_or_num(n)} rows, a study has {_a(shown)} {shown} chance (power = {_num(chance)}) to find "
              f"{plan['effect_words']}, using {plan['test_words']}. Method: {plan['method']}.")
        for note in plan["notes"]:
            print(note)
        row = dict(plan["row"])
        row.update({"rows": n, "power": chance})
        return _result(row)
    found = None if clusters is None else power_more.clustered(clusters[0], clusters[1], given=n)
    effective = n if found is None else found["effective"]
    in_clusters = "" if found is None else f" in clusters of {clusters[0]}"
    cluster_words = None if found is None else (
        f"Values in a cluster are alike (intracluster correlation, ICC, {_num(clusters[1])}; design effect "
        f"{_num(found['design effect'])}), so these {_whole_or_num(n)} count as about {_num(effective)} independent "
        "values; the chance is worked out for those.")
    if route == "percents":
        p1, p2, alpha = _percents(step, test, percents, sides, significance)
        if effective < 2:
            raise SimplydataError(f"{step}() needs values_per_group= worth at least 2 independent values in each group.")
        chance = _percents_power(p1, p2, effective, sides, alpha)
        effect, test_words = _percents_words(p1, p2, sides, alpha)
        shown = _percent(chance)
        print(f"With {_whole_or_num(n)} values in each group{in_clusters}, a study has {_a(shown)} {shown} chance "
              f"(power = {_num(chance)}) to find {effect}, using {test_words}. Method: statsmodels "
              "power_proportions_2indep(), as R power.prop.test().")
        if cluster_words:
            print(cluster_words)
        row = {"test": test, "method": "power for two percents", "R function": "power.prop.test()",
               "percent 1": p1 * 100, "percent 2": p2 * 100, "sides": sides, "significance": alpha,
               "values per group": n, "values in all": 2 * n}
        if found is not None:
            row.update(power_more.cluster_row(clusters[0], clusters[1], found))
        row["power"] = chance
        return _result(row)
    if route == "same_within":
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
    if effective < least:
        raise SimplydataError(f"In clusters of {clusters[0]} (ICC {_num(clusters[1])}), {_whole_or_num(n)} values count "
                              f"as only about {_num(effective)} independent values; at least {least} are needed. Give "
                              "more values_per_group=.")
    chance = plan["power"](effective)
    k = plan["k"]
    shown = _percent(chance)
    print(f"With {plan['amount'](n)}{in_clusters}, a study has {_a(shown)} {shown} chance (power = {_num(chance)}) to "
          f"find {plan['effect_words']}, using {plan['test_words']}. Method: {plan['method']}.")
    if cluster_words:
        print(cluster_words)
        if found["given clusters"] < 10:
            from .power_more import few_clusters_note

            print(few_clusters_note(k > 1 or test == "compare_averages"))
    if chance < 0.8:
        print("Note: this is below the usual 80 %; find_how_many_needed() tells you how many values you need.")
    for note in plan["notes"]:
        print(note)
    row = dict(plan["row"])
    row.update({"values per group": n, "values in all": n * k})
    if found is not None:
        row.update(power_more.cluster_row(clusters[0], clusters[1], found))
    row["power"] = chance
    return _result(row)
