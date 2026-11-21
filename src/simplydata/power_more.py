"""Planning a study, phase S3b-2: the newer routes of find_how_many_needed and find_chance_of_finding.

* interval_width= with one percent: the values needed for a percent's interval (R presize::prec_prop, Wilson).
* based_on="ranks" and drawing_from=: power by simulation with the very test simplydata runs (SciPy stats.power:
  Welch's t-test, Mann-Whitney, the paired t-test, Wilcoxon signed-rank, Levene's test), seeded, with the Monte
  Carlo error printed as the 95 % interval of the simulated chance (statsmodels proportion_confint, Wilson).
* by_running=: the learner's own function, one simulated study per seed; simplydata counts its p-values.
* for_test="explain" / "compare_models": regression power with Cohen's f² (statsmodels FTestPowerF2, as R pwr.f2.test);
  outcome="yes or no": logistic regression with one bell-shaped column (R pwrss, Demidenko with variance correction).
* for_test="compare_survival": events first by Schoenfeld's formula (R gsDesign), people with percents= (R
  powerSurvEpi); test_method="freedman" (R powerSurvEpi).
* in_clusters_of=, alike_within_clusters=: the design effect 1 + (m - 1) x ICC (Donner & Klar 2000), the one piece
  of arithmetic simplydata does itself here ([D] in clustered(); listed in tests/test_no_own_methods.py).
"""

from __future__ import annotations

import math
import numbers

from ._errors import SimplydataError, choice_error
from .power import (_a, _cohen_words, _num, _number, _percent, _result, _whole_or_num)

SIM_TESTS = ("compare_averages", "compare_before_after", "compare_spreads")
SIM_LARGEST = 20000  # the most values per group a simulation search goes up to
BATCH = 1000        # simulated studies drawn at a time (SciPy's default is all at once, which can fill the memory)
EXACT_LIMIT = 50     # as compare_averages_of: exact rank-test p-values below 50 values without ties
SURVIVAL_METHODS = ("schoenfeld", "freedman")


def _and(names) -> str:
    names = [str(n) for n in names]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def _two_sided(step, sides):
    if isinstance(sides, bool) or sides not in (1, 2):
        raise SimplydataError(f"{step}() needs sides=2 (a difference in either direction, the usual) or sides=1.")


def _significance(step, significance):
    significance = _number(step, "significance", significance, "significance=0.05")
    if not 0 < significance < 1:
        raise SimplydataError(f"{step}() needs significance= between 0 and 1, for example 0.05.")
    return significance


def ratio_effect(step, effect_size, name, example):
    """A hazard ratio or an odds ratio: more than 0, and not 1."""
    if effect_size is None:
        raise SimplydataError(f"{step}() needs effect_size= as the {name} you plan for, for example {example}.")
    value = _number(step, "effect_size", effect_size, example)
    if value <= 0:
        raise SimplydataError(f"effect_size= is a {name} here, and a {name} cannot be 0 or below. For example "
                              f"{example}.")
    if value == 1:
        raise SimplydataError(f"A {name} of 1 means no difference, which can never be found; give the smallest "
                              f"difference that matters, for example {example}.")
    return value


# ---------------------------------------------------------------- clusters (U15)
def check_clusters(step, in_clusters_of, alike_within_clusters):
    """(m, ICC), or None when neither is given."""
    if in_clusters_of is None and alike_within_clusters is None:
        return None
    if in_clusters_of is None or alike_within_clusters is None:
        raise SimplydataError(
            f"{step}() needs both in_clusters_of= (how many values in each cluster: a ward, a farm, a tank) and "
            "alike_within_clusters= (how alike values in one cluster are, the intracluster correlation ICC; 0.01 "
            "to 0.05 is common for people in wards or practices, Campbell et al. 2004), for example "
            "in_clusters_of=20, alike_within_clusters=0.05.")
    if isinstance(in_clusters_of, bool) or not isinstance(in_clusters_of, numbers.Integral) or in_clusters_of < 2:
        raise SimplydataError(f"{step}() needs in_clusters_of= as a whole number of 2 or more (the values in each "
                              "cluster), for example in_clusters_of=20.")
    icc = _number(step, "alike_within_clusters", alike_within_clusters, "alike_within_clusters=0.05")
    if not 0 <= icc <= 1:
        raise SimplydataError("alike_within_clusters= is the intracluster correlation (ICC), between 0 and 1, for "
                              "example 0.05.")
    return int(in_clusters_of), icc


def clustered(m, icc, independent=None, given=None):
    """[D] The design effect 1 + (m - 1) x ICC (Donner & Klar 2000) and what follows from it: the values needed
    (the independent number times the design effect, rounded up), whole clusters of m, how many independent values
    one cluster counts as (m / design effect), and the independent values a given number counts as.
    Pending Manish's approval (decision 14); the alternative is R epiR at run time."""
    design = 1 + (m - 1) * icc  # [D] the design effect
    out = {"design effect": design, "counts as": m / design}  # [D] one cluster counts as m / DE independent values
    if independent is not None:
        values = math.ceil(independent * design - 1e-9)  # [D] the independent number times the design effect
        clusters = math.ceil(values / m - 1e-9)  # [D] whole clusters
        out.update({"values": values, "clusters": clusters, "in whole clusters": clusters * m})
    if given is not None:
        out["effective"] = given / design  # [D] the independent values a given number counts as
        out["given clusters"] = given / m  # [D] the clusters a given number makes
    return out


def cluster_needed_words(m, icc, found, unit="values", each=True):
    per = " in each group" if each else ""
    per_group = " per group" if each else ""
    words = [f"Values in a cluster are alike (intracluster correlation, ICC, {_num(icc)}), so each cluster of {m} "
             f"counts as about {_num(found['counts as'])} independent values (design effect 1 + ({m} - 1) x "
             f"{_num(icc)} = {_num(found['design effect'])}). You need {found['values']} {unit}{per}, which is "
             f"{found['clusters']} clusters of {m} ({found['in whole clusters']} {unit}){per_group}."]
    if found["clusters"] < 10:
        words.append(few_clusters_note(each))
    words.append("Note: this assumes clusters of the same size; with unequal clusters more are needed (Eldridge, "
                 "Ashby & Kerry 2006).")
    return words


def few_clusters_note(each=True):
    where = "in each group" if each else "in all"
    rule = "adds one cluster to each group" if each else "adds one cluster"
    return (f"Note: with fewer than about 10 clusters {where}, the design-effect answer is too small; a common rule "
            f"{rule} (Hayes & Moulton 2017, Cluster Randomised Trials).")


def cluster_row(m, icc, found):
    row = {"cluster size": m, "intracluster correlation": icc, "design effect": found["design effect"]}
    if "values" in found:
        row.update({"clusters per group": found["clusters"], "values in whole clusters": found["in whole clusters"]})
    if "effective" in found:
        row["counts as independent values"] = found["effective"]
    return row


# ---------------------------------------------------------------- a percent's interval (U06)
def percent_interval_needed(step, width, percents, significance):
    width = _number(step, "interval_width", width, "interval_width=10")
    if (not isinstance(percents, (list, tuple)) or len(percents) != 1 or isinstance(percents[0], bool)
            or not isinstance(percents[0], (int, float)) or not 0 < percents[0] < 100):
        raise SimplydataError(f"{step}() with interval_width= takes percents= as one percent between 0 and 100 (the "
                              "percent you expect), for example interval_width=10, percents=[30].")
    if not 0 < width < 100:
        raise SimplydataError("interval_width= is the width of the percent's interval in percentage points, "
                              "between 0 and 100, for example interval_width=10.")
    significance = _significance(step, significance)
    from . import power_r

    exact = power_r.prec_prop(percents[0] / 100, width / 100, significance)
    needed = math.ceil(exact - 1e-9)
    level = _num((1 - significance) * 100)
    print(f"For a {level} % confidence interval of a percent near {_num(percents[0])} % that is {_num(width)} "
          f"percentage points wide (from end to end, Wilson interval), you need {needed} values. Method: R "
          "presize::prec_prop(method = \"wilson\").")
    return _result({"method": "sample size for the width of a percent's interval",
                    "R function": "presize::prec_prop()", "percent": percents[0], "interval width": width,
                    "interval level": (1 - significance) * 100, "values (exact)": exact, "values": needed})


# ---------------------------------------------------------------- simulation (U07, U16)
def _sim_plan(step, test, effect_size, difference, spread, drawing_from, based_on, groups, sides, significance):
    """The data, the test and the words of a simulation."""
    from scipy import stats

    if test not in SIM_TESTS:
        raise SimplydataError(f'{step}() simulates the power of for_test="compare_averages", "compare_before_and_after" or '
                              f'"compare_spreads_of"; for for_test="{test}" leave out based_on="ranks" and drawing_from=.')
    if based_on not in ("averages", "ranks"):
        raise choice_error(step, "based_on", based_on, ("averages", "ranks"))
    if test == "compare_spreads" and based_on == "ranks":
        raise SimplydataError('based_on="ranks" goes with compare_averages and compare_before_and_after; '
                              'compare_spreads_of uses Levene\'s test.')
    if groups != 2:
        raise SimplydataError(f"{step}() simulates two groups (or one set of changes); leave groups= out.")
    if sides != 2:
        raise SimplydataError(f"{step}() simulates two-sided tests; leave sides= out.")
    significance = _significance(step, significance)
    wanted = 1 if test == "compare_before_after" else 2
    from .distributions import Distribution

    if drawing_from is not None:
        if effect_size is not None or difference is not None or spread is not None:
            raise SimplydataError("drawing_from= already says how the groups differ; leave effect_size=, "
                                  "difference= and spread= out.")
        dists = list(drawing_from) if isinstance(drawing_from, (list, tuple)) else [drawing_from]
        if len(dists) != wanted or not all(isinstance(d, Distribution) for d in dists):
            example = ('drawing_from=[sdata.distribution("normal", average=0, standard_deviation=1)] (the changes)'
                       if wanted == 1 else 'drawing_from=[sdata.distribution("lognormal", ...), '
                                           'sdata.distribution("lognormal", ...)]')
            raise SimplydataError(f"{step}() with for_test=\"{test}\" needs drawing_from= as {wanted} "
                                  f"distribution{'s' if wanted == 2 else ''} made with sdata.distribution(), for "
                                  f"example {example}.")
        continuous = not any(d.is_discrete for d in dists)
        makers = [lambda rng, d=d: (lambda size: d._frozen.rvs(size=size, random_state=rng)) for d in dists]
        what = ("changes drawn from the " + dists[0].label + " distribution" if wanted == 1 else
                "values drawn from the " + dists[0].label + " and the " + dists[1].label + " distributions")
        effect, kind = None, None
    else:
        if test == "compare_spreads":
            raise SimplydataError('for_test="compare_spreads_of" in power needs drawing_from= with two distributions of '
                                  'different spread, for example drawing_from=[sdata.distribution("normal", '
                                  'average=0, standard_deviation=1), sdata.distribution("normal", average=0, '
                                  'standard_deviation=2)].')
        if effect_size is not None and (difference is not None or spread is not None):
            raise SimplydataError(f"{step}() needs effect_size= OR difference= and spread=, not both.")
        if effect_size is None:
            if difference is None or spread is None:
                raise SimplydataError(f"{step}() needs the size of the difference you hope to find, for example "
                                      "effect_size=0.5 (Cohen's d), or difference=5, spread=10.")
            spread = _number(step, "spread", spread, "spread=10")
            if spread <= 0:
                raise SimplydataError("spread= (the standard deviation) must be more than 0.")
            effect = _number(step, "difference", difference, "difference=5") / spread
        else:
            effect = _number(step, "effect_size", effect_size, "effect_size=0.5")
        effect = abs(effect)
        if effect == 0:
            raise SimplydataError("A difference of 0 can never be found; give the smallest difference that matters.")
        continuous, kind = True, "d"
        if wanted == 1:
            makers = [lambda rng: (lambda size: rng.normal(effect, 1.0, size=size))]
            what = f"bell-shaped changes with an average of {_num(effect)} standard deviations (Cohen's d)"
        else:
            makers = [lambda rng: (lambda size: rng.standard_normal(size=size)),
                      lambda rng: (lambda size: rng.normal(effect, 1.0, size=size))]
            what = (f"bell-shaped values whose averages differ by {_num(effect)} standard deviations (Cohen's d)")

    def method_for(n):
        return "exact" if continuous and n < EXACT_LIMIT else None

    if test == "compare_averages" and based_on == "ranks":
        def run(x, y, axis=-1):
            exact = method_for(x.shape[-1])
            return stats.mannwhitneyu(x, y, axis=axis, method=exact or "asymptotic", use_continuity=True).pvalue
        name, function = "the Mann-Whitney test", "scipy.stats.mannwhitneyu"
    elif test == "compare_averages":
        def run(x, y, axis=-1):
            return stats.ttest_ind(x, y, equal_var=False, axis=axis).pvalue
        name, function = "Welch's t-test", "scipy.stats.ttest_ind(equal_var=False)"
    elif based_on == "ranks":
        def run(x, axis=-1):
            exact = method_for(x.shape[-1])
            return stats.wilcoxon(x, axis=axis, zero_method="wilcox", correction=True,
                                  method=exact or "approx").pvalue
        name, function = "the Wilcoxon signed-rank test", "scipy.stats.wilcoxon"
    elif test == "compare_before_after":
        def run(x, axis=-1):
            return stats.ttest_1samp(x, 0.0, axis=axis).pvalue
        name, function = "the paired t-test", "scipy.stats.ttest_1samp (on the changes)"
    else:
        def run(x, y, axis=-1):
            return stats.levene(x, y, center="median", axis=axis).pvalue
        name, function = "Levene's test centred on the medians", "scipy.stats.levene(center=\"median\")"
    unit = "pairs" if wanted == 1 else "values in each group"
    return {"run": run, "makers": makers, "wanted": wanted, "name": name, "function": function, "what": what,
            "unit": unit, "significance": significance, "effect": effect, "kind": kind}


def _check_tries(step, tries, with_seed):
    from .numbers._base import check_seed, check_whole

    tries = check_whole(step, "tries=", tries, f"sdata.{step}(..., tries=10000)", smallest=1)
    if tries < 100:
        raise SimplydataError("tries= needs at least 100 simulated studies (10000 is usual) for a useful answer.")
    seed = check_seed(with_seed, f"sdata.{step}(..., with_seed=1)")
    if seed is None:
        raise SimplydataError("with_seed= needs a whole number here, like with_seed=1, so the answer repeats.")
    return tries, seed


def _powers(plan, sizes, tries, seed):
    """SciPy stats.power for each number of values (a fresh generator with the seed each time, so every call
    repeats)."""
    import numpy as np
    from scipy import stats

    rng = np.random.default_rng(seed)
    rvs = tuple(make(rng) for make in plan["makers"])
    sizes = np.asarray(sizes, dtype=int)
    result = stats.power(plan["run"], rvs, tuple(sizes for _ in rvs), significance=plan["significance"],
                         n_resamples=tries, batch=BATCH)
    return np.atleast_1d(np.asarray(result.power, dtype=float))


def _monte_carlo(share, tries):
    """The 95 % interval of a simulated chance (statsmodels proportion_confint, Wilson)."""
    from statsmodels.stats.proportion import proportion_confint

    low, high = proportion_confint(round(share * tries), tries, alpha=0.05, method="wilson")
    return float(low), float(high)


def _sim_sentence(plan, n, share, tries):
    low, high = _monte_carlo(share, tries)
    amount = f"{_whole_or_num(n)} {'pairs' if plan['wanted'] == 1 else 'values in each group'}"
    return (f"In {tries} simulated studies with {amount}, {plan['name']} found a difference in {_percent(share)} "
            f"(95 % interval {_num(low * 100)} to {_num(high * 100)} %: the Monte Carlo error, the wobble that comes from "
            f"simulating {tries} studies and not infinitely many)."), low, high


def _sim_method(plan, tries, seed):
    return (f"Method: power by simulation, SciPy stats.power() with {plan['function']} at {_num(plan['significance'])}"
            f", {tries} tries, with_seed={seed}; data: {plan['what']}.")


def simulate_chance(step, test, effect_size, difference, spread, values_per_group, drawing_from, based_on, groups,
                    sides, significance, tries, with_seed):
    plan = _sim_plan(step, test, effect_size, difference, spread, drawing_from, based_on, groups, sides, significance)
    tries, seed = _check_tries(step, tries, with_seed)
    sizes = list(values_per_group) if isinstance(values_per_group, (list, tuple)) else [values_per_group]
    for n in sizes:
        if isinstance(n, bool) or not isinstance(n, numbers.Integral) or n < 3:
            raise SimplydataError(f"{step}() needs values_per_group= as a whole number of 3 or more, or a list of "
                                  "them, for example values_per_group=[10, 20, 30].")
    shares = [float(_powers(plan, [n], tries, seed)[0]) for n in sizes]  # each number on its own, so it repeats
    rows = []
    for n, share in zip(sizes, shares):
        sentence, low, high = _sim_sentence(plan, n, float(share), tries)
        print(sentence)
        rows.append({"test": test, "method": "power by simulation", "function": plan["function"],
                     "values per group": n, "tries": tries, "seed": seed, "significance": plan["significance"],
                     "power": float(share), "power 95 % CI low": low, "power 95 % CI high": high})
    print(_sim_method(plan, tries, seed))
    if plan["kind"] == "d":
        print(_cohen_words("d", plan["effect"]))
    import pandas as pd

    from .table import table

    return table(pd.DataFrame(rows))


def simulate_needed(step, test, effect_size, difference, spread, target, drawing_from, based_on, groups, sides,
                    significance, tries, with_seed):
    """The smallest number of values whose simulated power reaches the target, from a power table read in steps."""
    plan = _sim_plan(step, test, effect_size, difference, spread, drawing_from, based_on, groups, sides, significance)
    tries, seed = _check_tries(step, tries, with_seed)
    if target <= plan["significance"]:
        raise SimplydataError("power= must be more than significance=: even with no real difference, a test "
                              "finds one that often by chance.")
    cache = {}

    def at(n):  # the simulated power at n values, each n with the same seed, so any one answer repeats on its own
        if n not in cache:
            cache[n] = float(_powers(plan, [n], tries, seed)[0])
        return cache[n]

    start = 8
    if plan["kind"] == "d":  # the t-test answer is a close start
        from statsmodels.stats.power import TTestIndPower, TTestPower

        engine = TTestIndPower() if plan["wanted"] == 2 else TTestPower()
        start = max(3, math.ceil(float(engine.solve_power(effect_size=plan["effect"], power=target,
                                                          alpha=plan["significance"] / 2, alternative="larger"))))
    low = max(3, int(start * 0.7))
    if at(low) >= target:
        low = 3
    high = start
    while at(high) < target:
        high = math.ceil(high * 1.5)
        if high > SIM_LARGEST:
            raise SimplydataError(f"The difference is too small to find with any practical study (more than "
                                  f"{SIM_LARGEST} values in each group by simulation). Check the distributions.")
    while high - low > 20:  # read the power table in steps, then one by one
        grid = sorted({int(round(low + (high - low) * i / 10)) for i in range(11)})
        first = next(i for i, n in enumerate(grid) if at(n) >= target or n == high)
        low, high = grid[max(first - 1, 0)], grid[first]
    needed = next(n for n in range(low, high + 1) if at(n) >= target or n == high)
    share = at(needed)
    sentence, low_ci, high_ci = _sim_sentence(plan, needed, share, tries)
    amount = f"{needed} {'pairs' if plan['wanted'] == 1 else 'values in each group'}"
    print(f"With {plan['what']}: to find the difference with {_a(_percent(target))} {_percent(target)} chance, "
          f"using {plan['name']} (two-sided, at "
          f"{_num(plan['significance'])}), you need about {amount}: the smallest number whose simulated chance "
          f"reaches {_percent(target)}. {sentence}")
    print(_sim_method(plan, tries, seed))
    print("Note: a simulated answer moves a little with the seed; for a firmer number, use more tries.")
    if plan["kind"] == "d":
        print(_cohen_words("d", plan["effect"]))
    row = {"test": test, "method": "power by simulation", "function": plan["function"], "tries": tries,
           "seed": seed, "significance": plan["significance"], "power wanted": target, "values per group": needed,
           "values in all": needed * plan["wanted"], "power with that many": share, "power 95 % CI low": low_ci,
           "power 95 % CI high": high_ci}
    if plan["wanted"] == 1:
        row["values in all"] = needed
    return _result(row)


def chance_by_running(step, one_study, tries, with_seed, significance):
    """by_running=: the learner's function makes one study's data with a seed and gives back its p-value;
    simplydata runs it once per seed (with_seed, with_seed + 1, ...) and counts the p-values below significance=."""
    import contextlib
    import io

    import numpy as np

    if not callable(one_study):
        raise SimplydataError("by_running= takes a function you wrote that makes one study's data with a seed and "
                              "gives back its p-value, for example\n  def one_study(seed):\n      ...\n      return "
                              "p_value\nthen by_running=one_study.")
    tries, seed = _check_tries(step, tries, with_seed)
    significance = _significance(step, significance)
    seeds = range(seed, seed + tries)
    found = []
    with contextlib.redirect_stdout(io.StringIO()):
        if one_study(seed) != one_study(seed):
            raise SimplydataError("Your function gives a different p-value each time it is run with the same seed, so "
                                  "the answer would not repeat; make every random number with the seed it is given, "
                                  "for example rng = np.random.default_rng(seed), not np.random on its own.")
        for s in seeds:
            value = one_study(s)
            if (isinstance(value, bool) or not isinstance(value, (int, float, np.floating, np.integer))
                    or not 0 <= float(value) <= 1):
                raise SimplydataError(f"by_running= runs your function with a seed; it must give back one p-value "
                                      f"(a number from 0 to 1), but with seed {s} it gave {value!r}.")
            found.append(float(value))
    if len(set(found)) == 1:
        raise SimplydataError("Your function gives the same p-value every time; make its random numbers with the seed "
                              "it is given, for example rng = np.random.default_rng(seed), or "
                              "sdata.distribution(...).make_random_numbers(how_many=30, with_seed=seed).")
    count = sum(1 for p in found if p < significance)  # counting, as SciPy stats.power counts
    share = count / tries
    low, high = _monte_carlo(share, tries)
    print(f"In {tries} studies made by your function (seeds {seed} to {seed + tries - 1}), {count} gave a p-value "
          f"below {_num(significance)}: a {_percent(share)} chance to find the difference (Monte Carlo error: 95 % "
          f"interval {_num(low * 100)} to {_num(high * 100)} %).")
    print("Method: power by simulation; simplydata runs your function once per seed and counts the p-values below "
          "significance= (the interval from statsmodels proportion_confint, Wilson). Everything your function prints "
          "is silenced.")
    return _result({"method": "power by simulation (your function)", "tries": tries, "first seed": seed,
                    "significance": significance, "p-values below significance": count, "power": share,
                    "power 95 % CI low": low, "power 95 % CI high": high})


# ---------------------------------------------------------------- regression (U09) and logistic regression (U11)
def _columns(step, value, option):
    """using= / against=: a list of column names (or one name), or a whole number of columns."""
    if isinstance(value, bool):
        value = None
    if isinstance(value, int) and value >= 1:
        return value, None
    if isinstance(value, str):
        return 1, [value]
    if isinstance(value, (list, tuple)) and value and all(isinstance(v, str) for v in value):
        if any("*" in v or ":" in v for v in value):
            raise SimplydataError(f"{step}() counts each name in {option}= as one column; an interaction such as "
                                  "\"a * b\" adds more than one. Give the number of columns instead, for example "
                                  f"{option}=3.")
        return len(value), list(value)
    raise SimplydataError(f'{step}() needs {option}= as the columns of the model, for example {option}=["temperature", '
                          f'"salinity", "depth"], or as a whole number of columns, for example {option}=3.')


def regression_plan(step, test, effect_size, using, against, significance, sides):
    """Cohen's f² for a whole model (explain) or for the columns in one model and not the other (compare_models)."""
    if sides != 2:
        raise SimplydataError("The F test of a regression looks for an effect in every direction at once, so sides=1 "
                              "does not apply; leave sides= out.")
    significance = _significance(step, significance)
    if using is None:
        raise SimplydataError(f'{step}() with for_test="{test}" needs using= (the columns of the model), for example '
                              'using=["temperature", "salinity", "depth"], or using=3.')
    count, names = _columns(step, using, "using")
    if test == "compare_models":
        if against is None:
            raise SimplydataError(f'{step}() with for_test="compare_models" needs using= and against=, the columns of the '
                                  'two models (as on compare_models), for example using=["temperature"], '
                                  'against=["temperature", "salinity", "depth"].')
        other, other_names = _columns(step, against, "against")
        if count == other:
            raise SimplydataError("using= and against= have the same number of columns, so there is no extra column to "
                                  "test; one model must hold more columns than the other.")
        big, small = (names, other_names) if count > other else (other_names, names)
        if big is not None and small is not None and not set(small) <= set(big):
            raise SimplydataError("The two models must be nested: every column of the smaller model must also be in "
                                  "the bigger one (as compare_models tests them).")
        tested = abs(count - other)
        total = max(count, other)
        tested_names = None if big is None or small is None else [c for c in big if c not in small]
        kept = total - tested
    else:
        if against is not None:
            raise SimplydataError('against= goes with for_test="compare_models"; for one model, give using= only.')
        tested, total, tested_names, kept = count, count, names, 0
    if effect_size is None:
        raise SimplydataError(f"{step}() needs effect_size= as Cohen's f² here, for example effect_size=0.15 (a medium "
                              "effect).")
    f2 = _number(step, "effect_size", effect_size, "effect_size=0.15")
    if f2 <= 0:
        raise SimplydataError("Cohen's f² must be more than 0.")
    from statsmodels.stats.power import FTestPowerF2

    engine = FTestPowerF2()

    def power(rows):  # the denominator degrees of freedom are the rows minus the columns minus 1
        return float(engine.power(effect_size=f2, df_num=tested, df_denom=rows - total - 1, alpha=significance))

    def solve(target):
        return float(engine.solve_power(effect_size=f2, df_num=tested, df_denom=None, alpha=significance,
                                        power=target)) + total + 1
    listed = f" ({_and(tested_names)})" if tested_names else ""
    meaning = (f"the tested columns would explain {_num(f2)} times as much of the spread as the model leaves "
               "unexplained")
    if test == "compare_models":
        effect_words = (f"Cohen's f² = {_num(f2)} for the {tested} column{'s' if tested > 1 else ''} in one model and "
                        f"not the other{listed}, with {kept} more column{'s' if kept != 1 else ''} in both models "
                        f"({meaning})")
    else:
        effect_words = f"Cohen's f² = {_num(f2)} for {tested} column{'s' if tested > 1 else ''}{listed} ({meaning})"
    notes = ["Note: each name counts as one column (one degree of freedom). A column of groups with k kinds counts as "
             "k - 1, and an interaction more; then give using= (and against=) as the number of columns.",
             _cohen_words("f2", f2)]
    row = {"test": test, "method": "regression power (Cohen's f²)", "R function": "pwr::pwr.f2.test()",
           "effect size name": "Cohen's f²", "effect size": f2, "columns tested": tested, "columns in all": total,
           "significance": significance}
    return {"power": power, "solve": solve, "lowest": total + 2.0, "effect_words": effect_words,
            "test_words": f"the F test at {_num(significance)}", "notes": notes, "row": row,
            "method": "regression power (Cohen's f², statsmodels FTestPowerF2), as R pwr::pwr.f2.test()"}


def logistic_plan(step, test, effect_size, using, against, percents, significance, sides):
    if test != "explain":
        raise SimplydataError('outcome="yes or no" in power goes with for_test="explain".')
    if against is not None:
        raise SimplydataError('against= goes with for_test="compare_models".')
    count, names = _columns(step, using if using is not None else 1, "using")
    if count != 1:
        raise SimplydataError(f'{step}() with outcome="yes or no" plans for one number column, for example '
                              'using=["dose"]. For several columns, simulate with find_chance_of_finding(by_running=).')
    if (not isinstance(percents, (list, tuple)) or len(percents) != 1 or isinstance(percents[0], bool)
            or not isinstance(percents[0], (int, float)) or not 0 < percents[0] < 100):
        raise SimplydataError(f'{step}() with outcome="yes or no" needs percents= as one percent: the percent with the '
                              'outcome at the average of the column, for example percents=[20]. For a yes/no column '
                              'instead of a number column, use for_test="compare_counts", percents=[30, 15].')
    _two_sided(step, sides)
    significance = _significance(step, significance)
    ratio = ratio_effect(step, effect_size, "odds ratio", "effect_size=1.5 (an odds ratio per standard deviation)")
    column = names[0] if names else "the column"
    at_average = f"the average {column}" if names else "its average"
    effect_words = (f"an odds ratio of {_num(ratio)} per standard deviation of {column} (each standard deviation more "
                    f"multiplies the odds of the outcome by {_num(ratio)}), with {_num(percents[0])} % having the "
                    f"outcome at {at_average}")
    row = {"test": "explain", "outcome": "yes or no", "method": "logistic-regression power (Demidenko, variance "
           "corrected)", "R function": "pwrss::power.z.logistic()", "effect size name": "odds ratio per standard "
           "deviation", "effect size": ratio, "percent at the average": percents[0], "sides": sides,
           "significance": significance}
    notes = [f"Note: {column} is taken to be bell-shaped (normal). An odds ratio per unit from a paper becomes one per "
             "standard deviation by raising it to the power of the standard deviation: 1.02 per mg with a standard "
             "deviation of 20 mg is 1.02 ** 20, about 1.49."]
    return {"percent": percents[0] / 100, "ratio": ratio, "significance": significance, "sides": sides,
            "effect_words": effect_words, "row": row, "notes": notes,
            "test_words": f"a {'two' if sides == 2 else 'one'}-sided test at {_num(significance)}"}


LOGISTIC_METHOD = ("logistic-regression power by Demidenko's (2007) formula with variance correction, as R "
                   "pwrss::power.z.logistic() and G*Power")


# ---------------------------------------------------------------- survival (U13)
def survival_plan(step, effect_size, percents, method, groups, sides, significance, difference, spread):
    if difference is not None or spread is not None:
        raise SimplydataError('for_test="compare_survival" takes the hazard ratio as effect_size=, not difference= and '
                              'spread=.')
    if groups != 2:
        raise SimplydataError('for_test="compare_survival" in power compares two groups; leave groups= out.')
    method = "schoenfeld" if method is None else method
    if not isinstance(method, str) or method.lower() not in SURVIVAL_METHODS:
        raise choice_error(step, "test_method", method, SURVIVAL_METHODS)
    method = method.lower()
    _two_sided(step, sides)
    significance = _significance(step, significance)
    ratio = ratio_effect(step, effect_size, "hazard ratio", "effect_size=0.7 (a hazard ratio)")
    first = second = None
    if percents is not None:
        if (not isinstance(percents, (list, tuple)) or len(percents) != 2
                or not all(isinstance(v, (int, float)) and not isinstance(v, bool) and 0 < v <= 100
                           for v in percents)):
            raise SimplydataError(f'{step}() with for_test="compare_survival" takes percents= as two percents, the percent '
                                  'of each group expected to have the event during the study (the first group, then '
                                  'the second), for example percents=[30, 40].')
        first, second = percents[0] / 100, percents[1] / 100
    if method == "freedman" and percents is None:
        raise SimplydataError('test_method="freedman" gives people, so it needs percents= (the percent of each group '
                              'expected to have the event), for example percents=[30, 40].')
    if percents is not None and sides == 1:
        raise SimplydataError('With percents=, survival power is two-sided only (R powerSurvEpi); leave sides= out, '
                              'or leave percents= out to get the events of a one-sided test.')
    effect_words = (f"a hazard ratio of {_num(ratio)} (in the first group the event happens {_num(ratio)} times as "
                    "often at any moment as in the second)")
    return {"ratio": ratio, "first": first, "second": second, "method": method, "sides": sides,
            "significance": significance, "effect_words": effect_words,
            "test_words": f"a {'two' if sides == 2 else 'one'}-sided log-rank test at {_num(significance)}"}


SURVIVAL_NOTE = ("Note: this assumes the hazard ratio stays the same over time (proportional hazards) and plans no "
                 "recruitment time and no people lost to follow-up; plan for more people if some will drop out.")


def survival_needed(step, plan, target):
    from . import power_r

    if target <= plan["significance"]:
        raise SimplydataError("power= must be more than significance=: even with no real difference, a test "
                              "finds one that often by chance.")
    ratio, sig = plan["ratio"], plan["significance"]
    row = {"test": "compare_survival", "effect size name": "hazard ratio", "effect size": ratio, "sides": plan["sides"],
           "significance": sig, "power wanted": target}
    head = (f"To find {plan['effect_words']} with {_a(_percent(target))} {_percent(target)} chance, using "
            f"{plan['test_words']}, you need")
    if plan["method"] == "freedman":
        exact = power_r.freedman_people(ratio, plan["first"], plan["second"], sig, target)
        people = math.ceil(exact - 1e-9)
        reached = power_r.freedman_power(ratio, plan["first"], plan["second"], people, sig)
        print(f"{head} {people} people in each group ({2 * people} in all), if {_num(plan['first'] * 100)} % of the "
              f"first group and {_num(plan['second'] * 100)} % of the second have the event during the study. "
              "Method: Freedman's (1982) formula, which gives people directly (not events first), as R "
              "powerSurvEpi::ssizeCT.default().")
        row.update({"method": "Freedman's formula", "R function": "powerSurvEpi::ssizeCT.default()",
                    "percent 1": plan["first"] * 100, "percent 2": plan["second"] * 100,
                    "people per group": people, "people in all": 2 * people, "power with that many": reached})
        print(SURVIVAL_NOTE)
        return _result(row)
    exact = power_r.schoenfeld_events(ratio, sig, target, plan["sides"])
    events = math.ceil(exact - 1e-9)
    row.update({"method": "log-rank power, Schoenfeld's formula", "R function": "gsDesign::nEvents()",
                "events (exact)": exact, "events": events,
                "power with that many": power_r.schoenfeld_events_power(ratio, events, sig, plan["sides"])})
    sentence = f"{head} {events} events."
    method = "Method: log-rank power by Schoenfeld's (1983) formula, as R gsDesign::nEvents()"
    if plan["first"] is not None:
        people, share = power_r.schoenfeld_people(ratio, plan["first"], plan["second"], sig, target)
        per_group = math.ceil(people / 2 - 1e-9)
        sentence += (f" If {_num(plan['first'] * 100)} % of the first group and {_num(plan['second'] * 100)} % of "
                     f"the second have the event during the study ({_num(share * 100)} % of everyone), that is "
                     f"{per_group * 2} people ({per_group} in each group).")
        method += "; people as R powerSurvEpi::ssizeEpi.default()"
        row.update({"percent 1": plan["first"] * 100, "percent 2": plan["second"] * 100,
                    "people per group": per_group, "people in all": per_group * 2})
    else:
        sentence += " Give percents=[30, 40] (the percent of each group expected to have the event) to turn events " \
                    "into people."
    print(f"{sentence} {method}.")
    print(SURVIVAL_NOTE)
    return _result(row)


def survival_chance(step, plan, people):
    from . import power_r

    ratio, sig = plan["ratio"], plan["significance"]
    if plan["first"] is None:
        raise SimplydataError(f'{step}() with for_test="compare_survival" needs percents= (the percent of each group '
                              'expected to have the event), to turn people into events, for example '
                              'values_per_group=353, percents=[30, 40].')
    if people < 2:
        raise SimplydataError(f"{step}() needs values_per_group= of at least 2 people in each group.")
    row = {"test": "compare_survival", "effect size name": "hazard ratio", "effect size": ratio,
           "percent 1": plan["first"] * 100, "percent 2": plan["second"] * 100, "sides": 2, "significance": sig,
           "people per group": people, "people in all": 2 * people}
    if plan["method"] == "freedman":
        chance = power_r.freedman_power(ratio, plan["first"], plan["second"], people, sig)
        method = "Freedman's (1982) formula, as R powerSurvEpi::powerCT.default()"
        row.update({"method": "Freedman's formula", "R function": "powerSurvEpi::powerCT.default()"})
    else:
        chance, _ = power_r.schoenfeld_people_power(ratio, plan["first"], plan["second"], 2 * people, sig)
        method = "log-rank power by Schoenfeld's (1983) formula, as R powerSurvEpi::powerEpi.default()"
        row.update({"method": "log-rank power, Schoenfeld's formula", "R function": "powerSurvEpi::powerEpi.default()"})
    shown = _percent(chance)
    print(f"With {_whole_or_num(people)} people in each group, of whom {_num(plan['first'] * 100)} % and "
          f"{_num(plan['second'] * 100)} % have the event during the study, a study has {_a(shown)} {shown} chance "
          f"(power = {_num(chance)}) to find {plan['effect_words']}, using {plan['test_words']}. Method: {method}.")
    if chance < 0.8:
        print("Note: this is below the usual 80 %; find_how_many_needed() tells you how many events and people you "
              "need.")
    print(SURVIVAL_NOTE)
    row["power"] = chance
    return _result(row)

