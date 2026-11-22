"""Bayesian answers (phase S3d-3, design s3c_design.md Z01-Z06): test_method="bayesian" on compare_averages_of (two groups),
compare_before_and_after, compare_average_to, find_correlation_between and compare_counts_of (R BayesFactor), and on
explain and check_model_of (R rstanarm). The R calls are in bayes_r.py; this file checks the inputs and says the
answer in words.

Every printout follows the S3c-L11 rule: it names the prior, gives credible intervals with their meaning once, says
the Bayes factor as "the data are N times as likely if ... as if ...", prints with_seed=, has no p-value and no
verdict words (never "significant", "strong evidence", "proves"), and the model words check convergence (R-hat,
effective draws, divergent transitions) and print any warning, with what to do, before the estimates.
"""

from __future__ import annotations

import numpy as np

from .._errors import SimplydataError
from . import bayes_r
from .stat_tests import _list_words, _num

CREDIBLE_MEANING = ("95 % credible interval: given the data and the prior, a 95 % chance that the value lies in it")
BF_NOTE = ("A Bayes factor is not the chance that a hypothesis is true: it says how much the data shift the odds "
           "between the two (Wagenmakers et al. 2018). It depends on the prior width; prior_width=\"wide\" shows how "
           "much. There is no p-value in a Bayesian answer.")
T_PRIOR = ("the JZS prior: a Cauchy prior on the effect size (the difference in standard deviations) with width "
           "{width} ({name}; Rouder et al. 2009)")
R_PRIOR = ("a stretched beta prior on the correlation with width {width} ({name}; Ly, Verhagen & Wagenmakers 2016); "
           "JASP's default width is 1, so its Bayes factors differ")
COUNT_PRIOR = ("independent multinomial sampling with each group's total fixed (rows of the table), and the "
               "Gunel-Dickey prior with concentration 1 (Gunel & Dickey 1974; Jamil et al. 2017)")
RHAT_GUIDE, ESS_GUIDE = 1.01, 400  # Vehtari, Gelman, Simpson, Carpenter & Buerkner (2021)
WHAT_TO_DO = ("What to do: fewer columns in using=, number columns on similar scales (table.add_z_score_column), "
              "merge groups with very few rows, or more data; in R the same model with more iterations (stan_glm(iter "
              "= 4000)) or smaller steps (adapt_delta = 0.99). Do not report these numbers until the warning is gone.")
BAYES_OUTCOMES = tuple(bayes_r.FAMILIES)
OK_OPTIONS = "outcome=, grouped_by= and with_seed="


def check_bayes_options(step, given, light=True):
    """Refuse the options that do not go with test_method="bayesian" (given: [(option, value, default)]), and check prior_width=."""
    used = [name for name, value, default in given if not _same(value, default)]
    if used:
        what = ("a Bayes factor and a credible interval (no sides=, p_value_by= ...)" if light else
                f"a Bayesian model (it takes {OK_OPTIONS})")
        raise SimplydataError(f"{_list_words(used)} cannot be used with test_method=\"bayesian\", which gives {what}. "
                              f"Leave {'it' if len(used) == 1 else 'them'} out, or leave out test_method=\"bayesian\".")


def _same(value, default):
    if value is default:
        return True
    try:
        return bool(value == default)
    except Exception:  # noqa: BLE001 - arrays and other objects that do not compare to a default
        return False


def check_seed(with_seed):
    if isinstance(with_seed, bool) or not isinstance(with_seed, (int, np.integer)):
        raise SimplydataError("with_seed= is a whole number that fixes the random draws of the posterior, for example "
                              "with_seed=1.")
    return int(with_seed)


def _times(bf):
    """A Bayes factor said as "N times": three significant digits, whole numbers with thousands separators, and
    "more than a million" from a million up (the digits are in the result table)."""
    if bf >= 1e6:
        return "more than a million"
    return f"{bf:,.0f}" if bf >= 1000 else _num(bf)


def bf_sentence(found, alternative, null, noun, prior_words):
    """The data are N times as likely if <alternative> as if <null> (Bayes factor for <noun>, prior)."""
    bf, against = found["bf"], found["bf_against"]
    if bf >= 1:
        first = f"The data are {_times(bf)} times as likely if {alternative} as if {null}"
    else:
        first = f"The data are {_times(against)} times as likely if {null} as if {alternative}"
    return f"{first} (Bayes factor for {noun}: {_num(bf)}, with {prior_words})."


def _width_words(found_width, asked):
    name = f'"{asked}", BayesFactor\'s default' if asked == "medium" else (
        f'"{asked}"' if isinstance(asked, str) else "chosen with prior_width=")
    return _num(found_width), name


def _method(call, width, seed):
    rscale = f'"{width}"' if isinstance(width, str) else f"{width:g}"
    return (f"Method: R BayesFactor::{call} (rscale = {rscale}); the interval from {bayes_r.DRAWS:,} draws of the "
            f"posterior (BayesFactor::posterior()), with_seed={seed}: the same seed gives the same draws again.")


def _interval_sentence(what, est, unit=""):
    low, mid, high = est
    return (f"Given the data and the prior, {what} is probably between {_num(low)}{unit} and {_num(high)}{unit} "
            f"({CREDIBLE_MEANING}); its middle value (the posterior median) is {_num(mid)}{unit}.")


# ---------------------------------------------------------------- the light route
def two_groups(table, column, for_each, groups, width, seed):
    """compare_averages_of(..., test_method="bayesian") with two groups: R BayesFactor::ttestBF(x, y)."""
    (n1, a), (n2, b) = groups
    if np.min(a) == np.max(a) and np.min(b) == np.max(b):
        raise SimplydataError(f'Every value is the same within each group of "{for_each}", so the spread cannot be '
                              "measured and the groups cannot be compared the Bayesian way.")
    found = bayes_r.t_test("two groups", a, b, width=width, seed=seed)
    shown, name = _width_words(found["width"], width)
    prior = T_PRIOR.format(width=shown, name=name)
    print(f'Comparing the average "{column}" in {n1} and {n2} the Bayesian way ({len(a)} and {len(b)} rows).')
    print(bf_sentence(found, f"the averages of {n1} and {n2} differ", "they do not differ", "a difference", prior))
    print(_interval_sentence(f"the difference ({n1} minus {n2})", found["est"]) + " The effect size (the difference "
          f"in standard deviations) is probably between {_num(found['effect'][0])} and {_num(found['effect'][2])}.")
    print(_method("ttestBF(x, y)", width, seed))
    print(BF_NOTE)
    row = {"test": "Bayes factor t-test (JZS prior)", "what it compares": f'the average of "{column}" in each '
           f'"{for_each}" ({n1}, {n2}): differ against do not differ', "Bayes factor": found["bf"], "Bayes factor error": found["error"],
           "prior used": f"Cauchy on the effect size, width {shown}", "prior width": found["width"],
           "difference": found["est"][1], "difference 95 % credible interval low": found["est"][0],
           "difference 95 % credible interval high": found["est"][2],
           "effect size name": "difference in standard deviations (delta)", "effect size": found["effect"][1],
           "effect size 95 % credible interval low": found["effect"][0],
           "effect size 95 % credible interval high": found["effect"][2],
           f"count in {n1}": len(a), f"count in {n2}": len(b), f"average in {n1}": float(np.mean(a)),
           f"average in {n2}": float(np.mean(b))}
    return table._result_table(row)


def matched(table, before, after, b_values, a_values, width, seed):
    """compare_before_and_after(..., test_method="bayesian"): R BayesFactor::ttestBF(after, before, paired = TRUE)."""
    found = bayes_r.t_test("matched", a_values, b_values, width=width, seed=seed)
    shown, name = _width_words(found["width"], width)
    prior = T_PRIOR.format(width=shown, name=name)
    print(f'Comparing "{after}" with "{before}" row by row the Bayesian way ({len(a_values)} rows).')
    print(bf_sentence(found, "the values changed on average", "they did not change", "a change", prior))
    print(_interval_sentence(f'the average change ("{after}" minus "{before}")', found["est"])
          + f" The effect size (the change in standard deviations of the changes) is probably between "
          f"{_num(found['effect'][0])} and {_num(found['effect'][2])}.")
    print(_method("ttestBF(x = after, y = before, paired = TRUE)", width, seed))
    print(BF_NOTE)
    row = {"test": "Bayes factor paired t-test (JZS prior)",
           "what it compares": f'"{after}" minus "{before}", row by row: changed against did not change',
           "Bayes factor": found["bf"], "Bayes factor error": found["error"], "prior used": f"Cauchy on the effect size, width {shown}",
           "prior width": found["width"], "average change": found["est"][1],
           "average change 95 % credible interval low": found["est"][0],
           "average change 95 % credible interval high": found["est"][2],
           "effect size name": "change in standard deviations of the changes (delta)",
           "effect size": found["effect"][1], "effect size 95 % credible interval low": found["effect"][0],
           "effect size 95 % credible interval high": found["effect"][2], "rows": len(a_values)}
    return table._result_table(row)


def one_column(table, column, value, values, width, seed):
    """compare_average_to(..., test_method="bayesian"): R BayesFactor::ttestBF(x - value)."""
    found = bayes_r.t_test("one", values, value=value, width=width, seed=seed)
    shown, name = _width_words(found["width"], width)
    prior = T_PRIOR.format(width=shown, name=name)
    shown_value = f"{value:g}"
    print(f'Comparing the average "{column}" with {shown_value} the Bayesian way ({len(values)} rows).')
    print(bf_sentence(found, f"the average differs from {shown_value}", f"it is {shown_value}", "a difference",
                      prior))
    print(_interval_sentence(f"the average minus {shown_value}", found["est"]))
    print(_method("ttestBF(x - value)", width, seed) + " (BayesFactor's posterior() leaves out mu =, so the values "
          "are compared with the value by taking it away first, as ttestBF does for its Bayes factor.)")
    print(BF_NOTE)
    row = {"test": "Bayes factor one-sample t-test (JZS prior)",
           "what it compares": f'the average of "{column}" against {shown_value}: differs against does not differ',
           "Bayes factor": found["bf"], "Bayes factor error": found["error"], "prior used": f"Cauchy on the effect size, width {shown}",
           "prior width": found["width"], "value": float(value), "difference": found["est"][1],
           "difference 95 % credible interval low": found["est"][0],
           "difference 95 % credible interval high": found["est"][2],
           "effect size name": "difference in standard deviations (delta)", "effect size": found["effect"][1],
           "effect size 95 % credible interval low": found["effect"][0],
           "effect size 95 % credible interval high": found["effect"][2], "average": float(np.mean(values)),
           "rows": len(values)}
    return table._result_table(row)


def correlation(table, a_name, b_name, a, b, width, seed):
    """find_correlation_between(a, b, test_method="bayesian"): R BayesFactor::correlationBF(a, b)."""
    found = bayes_r.correlation(a, b, width=width, seed=seed)
    shown, name = _width_words(found["width"], width)
    prior = R_PRIOR.format(width=shown, name=name)
    print(f'The correlation between "{a_name}" and "{b_name}", the Bayesian way ({len(a)} rows).')
    print(bf_sentence(found, f'"{a_name}" and "{b_name}" are correlated', "they are not", "a correlation", prior))
    print(_interval_sentence("the correlation (Pearson's r in the population)", found["rho"]))
    print(_method("correlationBF(y, x)", width, seed))
    print(BF_NOTE)
    row = {"test": "Bayes factor for a correlation (stretched beta prior)",
           "what it compares": f'"{a_name}" and "{b_name}": correlated against not correlated',
           "Bayes factor": found["bf"], "Bayes factor error": found["error"], "prior used": f"stretched beta on the correlation, width {shown}",
           "prior width": found["width"], "r": found["rho"][1], "r 95 % credible interval low": found["rho"][0],
           "r 95 % credible interval high": found["rho"][2], "rows": len(a)}
    return table._result_table(row)


def counts(table, column, for_each, values, groups, value_order, group_order, seed):
    """compare_counts_of(..., test_method="bayesian"): R BayesFactor::contingencyTableBF(indepMulti, rows fixed)."""
    found = bayes_r.counts(values, groups, value_order, group_order, seed=seed)
    print(f'Comparing how often each "{column}" turns up in each "{for_each}", the Bayesian way ({len(values)} rows).')
    print(bf_sentence(found, f'the shares of "{column}" differ between the groups', "they do not differ",
                      "a difference", COUNT_PRIOR))
    shown_values = value_order if len(value_order) > 2 else value_order[-1:]
    for g in group_order:
        parts = [f'"{v}" {_num(found["share"][(g, v)][1])} ({_num(found["share"][(g, v)][0])} to '
                 f'{_num(found["share"][(g, v)][2])})' for v in shown_values]
        print(f"  in {g}: share of {_list_words(parts)}")
    print(f"Each share is the posterior median with its {CREDIBLE_MEANING}.")
    print(f"Method: R BayesFactor::contingencyTableBF(sampleType = \"indepMulti\", fixedMargin = \"rows\") with the "
          f'"{for_each}" groups as rows; the shares from {bayes_r.DRAWS:,} draws of the posterior '
          f"(BayesFactor::posterior()), with_seed={seed}: the same seed gives the same draws again.")
    print(BF_NOTE.replace(" It depends on the prior width; prior_width=\"wide\" shows how much.", ""))
    row = {"test": "Bayes factor for a table of counts (independent multinomial)",
           "what it compares": f'"{column}" in each "{for_each}" ({", ".join(str(g) for g in group_order)}): differ '
                               "against do not differ", "Bayes factor": found["bf"], "Bayes factor error": found["error"],
           "prior used": "Gunel-Dickey, concentration 1, each group's total fixed"}
    for g in group_order:
        for v in value_order:
            low, mid, high = found["share"][(g, v)]
            row[f"share {v} in {g}"] = mid
            row[f"share {v} in {g} 95 % credible interval low"] = low
            row[f"share {v} in {g} 95 % credible interval high"] = high
    row["rows"] = len(values)
    return table._result_table(row)


# ---------------------------------------------------------------- the heavy route
def _model_for(table, step, column, using, outcome, grouped_by):
    if outcome not in BAYES_OUTCOMES:
        raise SimplydataError(f'test_method="bayesian" fits outcome="numbers", "yes or no" or "counts" (R rstanarm stan_glm and '
                              f'stan_glmer); outcome="{outcome}" is not offered the Bayesian way yet.')
    if grouped_by is not None and not isinstance(grouped_by, str):
        raise SimplydataError("test_method=\"bayesian\" takes one grouped_by= column (a mixed model with its own starting level "
                              'for each group, R rstanarm::stan_glmer(... + (1 | group))), such as grouped_by="school".')
    bayes_r.need_heavy("A Bayesian model")
    model, pieces = table._one_model(step, column, using, outcome, grouped_by, fit=False)
    return model, pieces


def _formula(model, pieces, grouped_by):
    from .models import _r_name

    rhs = " + ".join(pieces) if pieces else "1"
    family = {"numbers": "gaussian()", "yes or no": "binomial()", "counts": "poisson()"}[model["outcome"]]
    if grouped_by is not None:
        return (f"rstanarm::stan_glmer({_r_name(model['column'])} ~ {rhs} + (1 | {_r_name(grouped_by)}), family = "
                f"{family}, chains = {bayes_r.CHAINS}, iter = {bayes_r.ITERATIONS}, seed = with_seed)")
    return (f"rstanarm::stan_glm({_r_name(model['column'])} ~ {rhs}, family = {family}, chains = {bayes_r.CHAINS}, "
            f"iter = {bayes_r.ITERATIONS}, seed = with_seed)")


def _prior_lines(found):
    skip = ("Priors for model", "------", "See help(")
    return ["    " + line.rstrip() for line in found["prior"] if line.strip() and not line.startswith(skip)]


def convergence(found):
    """The warnings (printed before any estimate) and the one-line summary of R-hat, effective draws and divergences."""
    rhat, bulk, tail = found["rhat"], found["ess_bulk"], found["ess_tail"]
    total = len(found["par"])
    warnings = []
    finite = rhat[np.isfinite(rhat)]
    high = int(np.sum(finite > RHAT_GUIDE))
    if high or len(finite) < total:
        worst = _num(float(np.nanmax(rhat))) if len(finite) else "not available"
        warnings.append(f"Warning: the {bayes_r.CHAINS} chains do not agree (R-hat above {RHAT_GUIDE} for {high} of "
                        f"{total} parameters, largest {worst}), so the draws do not yet describe the posterior. "
                        + WHAT_TO_DO)
    low = int(np.sum(~((bulk >= ESS_GUIDE) & (tail >= ESS_GUIDE))))
    if low:
        warnings.append(f"Warning: too few effective draws for {low} of {total} parameters "
                        f"(smallest {_num(float(np.nanmin(bulk)))} in the middle and {_num(float(np.nanmin(tail)))} in "
                        f"the tails; at least {ESS_GUIDE} are needed for reliable medians and intervals, Vehtari et al. "
                        "2021). " + WHAT_TO_DO)
    if found["divergent"]:
        warnings.append(f"Warning: {found['divergent']} divergent transition{'s' if found['divergent'] != 1 else ''} "
                        "after warm-up: the sampler could not follow the posterior everywhere, so the draws may be "
                        "biased. " + WHAT_TO_DO)
    if found["treedepth"]:
        warnings.append(f"Note: {found['treedepth']} draws reached the largest tree depth "
                        f"({found['max_treedepth']}): sampling was slow "
                        "there; this is about speed, not bias (Stan's guide).")
    largest = _num(float(np.nanmax(rhat))) if len(finite) else "not available"
    summary = (f"Convergence: R-hat at most {largest} (rank-normalised; the guide is "
               f"{RHAT_GUIDE} or below), at least {_num(float(np.nanmin(bulk)))} effective draws in the middle and "
               f"{_num(float(np.nanmin(tail)))} in the tails (the guide: {ESS_GUIDE} or more), "
               f"{found['divergent']} divergent transitions; over all {total} parameters and {found['draws']:,} "
               "draws, the posterior package's rhat(), ess_bulk() and ess_tail() (Vehtari et al. 2021).")
    return warnings, summary


def explain(table, column, using, outcome, grouped_by, seed):
    """explain(..., test_method="bayesian"): R rstanarm stan_glm() or stan_glmer()."""
    from .models import INTERCEPT, _quoted

    step = "explain"
    model, pieces = _model_for(table, step, column, using, outcome, grouped_by)
    found = bayes_r.stan_model(model, seed)
    labels = list(model["labels"])
    if len(labels) != len(found["names"]):
        raise SimplydataError(f"R rstanarm made {len(found['names'])} model columns where simplydata expected "
                              f"{len(labels)}; write the interaction with both of its columns in using=.")
    warnings, summary = convergence(found)
    for line in warnings:
        print(line)
    ratio = bayes_r.RATIO_OUTCOMES.get(outcome)
    names = _list_words(_quoted(v) for v in model["variables"]) or "nothing (the intercept only)"
    groups = f', with its own starting level for each "{grouped_by}"' if grouped_by is not None else ""
    print(f'Explaining "{column}" from {names}{groups} the Bayesian way ({found["rows"]} rows). Each effect below '
          "holds the other columns fixed:")
    rows = []
    by_name = dict(zip(found["par"], zip(found["rhat"], found["ess_bulk"], found["ess_tail"])))
    missing = [n for n in found["names"] if n not in by_name]
    if missing:
        raise SimplydataError(f"R rstanarm gave no convergence measures for {_list_words(missing)}.")
    checks = [by_name[n] for n in found["names"]]
    for label, est, low, high, (rhat, bulk, tail) in zip(labels, found["est"], found["low"], found["high"], checks):
        group = any(part[1] is not None for part in model["parts_of"][labels.index(label)])
        span = f"{_num(low)} to {_num(high)}"
        if label == INTERCEPT:
            what = ("the odds of yes" if outcome == "yes or no" else "the average count" if outcome == "counts"
                    else f'the expected "{column}"') + (" when every number column is 0 and every group column is "
                                                        "at its baseline")
            print(f"  intercept: {_num(est)} ({span}), {what}.")
        elif ratio:
            thing = "the odds of yes" if outcome == "yes or no" else "the average count"
            step_words = "in this group than in the baseline group" if group else f'for each 1 more "{label}"'
            verb = "are" if outcome == "yes or no" else "is"
            print(f"  {label}: {ratio} {_num(est)} ({span}): {thing} {verb} {_num(est)} times as high {step_words}.")
        elif group:
            print(f'  {label} against the baseline group: "{column}" is {_num(est)} higher ({span}).')
        else:
            print(f'  {label}: each 1 more "{label}" goes with {_num(est)} more "{column}" ({span}).')
        rows.append({"term": label, "effect": float(est), "95 % credible interval low": float(low),
                     "95 % credible interval high": float(high), "R-hat": float(rhat),
                     "effective draws (middle)": float(bulk), "effective draws (tails)": float(tail)})
    if "sigma" in found:
        low, _, high = found["sigma_ci"][0], None, found["sigma_ci"][1]
        print(f'  spread around the model (sigma): {_num(found["sigma"])} ({_num(low)} to {_num(high)}) in "{column}".')
        r, b, t = by_name.get("sigma", (np.nan, np.nan, np.nan))
        rows.append({"term": "spread around the model (sigma)", "effect": found["sigma"],
                     "95 % credible interval low": low, "95 % credible interval high": high, "R-hat": float(r),
                     "effective draws (middle)": float(b), "effective draws (tails)": float(t)})
    if "group_var" in found:
        low, high = found["group_var_ci"]
        scale = {"yes or no": " on the log-odds scale", "counts": " on the log scale of the counts"}.get(outcome, "")
        print(f'  variance between the "{grouped_by}" groups (of their own starting levels{scale}): '
              f'{_num(found["group_var"])} ({_num(low)} to {_num(high)}).')
        r, b, t = by_name.get("Sigma[g:(Intercept),(Intercept)]", (np.nan, np.nan, np.nan))
        rows.append({"term": f'variance between the "{grouped_by}" groups', "effect": found["group_var"],
                     "95 % credible interval low": low, "95 % credible interval high": high, "R-hat": float(r),
                     "effective draws (middle)": float(b), "effective draws (tails)": float(t)})
    scale = f" (the effects as {ratio}s, the intercept as {'odds' if outcome == 'yes or no' else 'a count'})" \
        if ratio else ""
    print(f"Each number: the posterior median with its {CREDIBLE_MEANING}{scale}. There are no p-values in a "
          "Bayesian model.")
    print("Prior used (rstanarm's default weakly informative priors, scaled to the spread of the data; R "
          "rstanarm::prior_summary()):")
    for line in _prior_lines(found):
        print(line)
    print(summary)
    print(f"Method: R {_formula(model, pieces, grouped_by)}: {bayes_r.CHAINS} chains of "
          f"{bayes_r.KEPT} draws after {bayes_r.WARMUP} warm-up, the posterior median and the "
          f"central 95 % interval (posterior_interval()); with_seed={seed} gives the same draws again on the same "
          "computer. The prior scales follow the spread of the data, so they change when the data change.")
    print("A link does not show that one thing causes the other.")
    import narwhals as nw

    frame = nw.from_dict({k: [r[k] for r in rows] for k in rows[0]}, backend=table._frame.implementation)
    return table._new_table(frame)


def _made_label(title, count):
    return f"{count} sets made up from the prior" if title.startswith("Prior") else f"{count} sets made up by the model"


def _draw_density_check(ctx, numbers, column, title):
    ax = ctx.ax
    for line in numbers["made"]:
        ax.plot(numbers["grid"], line, color="#9ecae1", linewidth=0.7, alpha=0.6, zorder=1)
    ax.plot(numbers["grid"], numbers["observed"], color="#08306b", linewidth=2.2, zorder=3)
    from matplotlib.lines import Line2D

    ax.legend([Line2D([0], [0], color="#08306b", linewidth=2.2), Line2D([0], [0], color="#9ecae1", linewidth=1)],
              ["the data", _made_label(title, len(numbers["made"]))], frameon=False)
    ax.set_xlabel(column)
    ax.set_ylabel("density")
    ax.set_title(title)


def _draw_bar_check(ctx, numbers, column, title):
    ax = ctx.ax
    grid, made = numbers["grid"], numbers["made"]
    ax.bar(grid, numbers["observed"], color="#c6dbef", edgecolor="#6baed6", label="the data")
    # [D] display only: the error bars are drawn as distances from the median, as matplotlib's errorbar asks
    ax.errorbar(grid, made[:, 1], yerr=[made[:, 1] - made[:, 0], made[:, 2] - made[:, 1]], fmt="o", color="#08306b",
                capsize=3, label=_made_label(title, bayes_r.PREDICTED_DRAWS) + ": median and 90 % interval")
    ax.legend(frameon=False)
    ax.set_xlabel(column)
    ax.set_ylabel("count")
    ax.set_title(title)


def check(table, column, using, outcome, grouped_by, seed, show):
    """check_model_of(..., test_method="bayesian"): the posterior predictive picture; show="prior check" the prior one."""
    step = "check_model_of"
    prior_only = show == "prior check"
    model, pieces = _model_for(table, step, column, using, outcome, grouped_by)
    found = bayes_r.predictive_check(model, seed, prior_only=prior_only)
    warnings, summary = convergence(found)
    for line in warnings:
        print(line)
    title = "Prior predictive check" if prior_only else "Posterior predictive check"
    sets = bayes_r.PREDICTED_DRAWS
    if prior_only:
        print(f'{title} of the model of "{column}" ({found["rows"]} rows): {sets} sets of values the model would make '
              "up from the prior alone, before seeing the data (R rstanarm, prior_PD = TRUE), against the data. They "
              f'should cover every value "{column}" could take, without going far beyond anything possible; the '
              "prior is meant to rule out the impossible, not to say where the answer lies (Gabry et al. 2019).")
    else:
        print(f'{title} of the model of "{column}" ({found["rows"]} rows): {sets} sets of values made up by the fitted '
              "model (R rstanarm::posterior_predict()), against the data. If the model fits, the data look like one "
              "more made-up set; a gap that every set shows (a second hump, a longer tail, more zeros) is what the "
              "model misses (Gabry et al. 2019).")
    if outcome == "numbers":
        print("Each line is a density: R stats::density() with bw.nrd0, as bayesplot::ppc_dens_overlay.")
    else:
        print("Bars: how often each value turns up in the data; dots and lines: the median and 90 % interval of its "
              "count in the made-up sets, as bayesplot::ppc_bars.")
    print("Prior used (R rstanarm::prior_summary()):")
    for line in _prior_lines(found):
        print(line)
    if not prior_only:
        print(summary)
    print(f"Method: R {_formula(model, pieces, grouped_by)}{', prior_PD = TRUE' if prior_only else ''}, then "
          f"posterior_predict(draws = {sets}, seed = with_seed); with_seed={seed}.")
    if show == "numbers":
        return _check_numbers(table, found, model["outcome"])
    import pandas as pd

    from ..chart import chart as make_chart

    frame = pd.DataFrame({column: found["grid"]})
    made = make_chart(frame)
    drawer = _draw_density_check if outcome == "numbers" else _draw_bar_check
    made._add("predictive check", "draw", drawer, numbers=found, column=column, title=title)
    made._check_numbers = found
    return made


def _check_numbers(table, found, outcome):
    """check_model_of(..., test_method="bayesian", show="numbers"): the numbers behind the check as a table: R-hat and
    the effective draws of each parameter (posterior::summarise_draws), the divergent transitions (rstan), and the
    posterior predictive check: the data's density (or count of each value) against the median and 90 % range of
    the made-up sets, all from R."""
    import math

    import narwhals as nw

    rows = []

    def add(check, term, value, at=math.nan, low=math.nan, high=math.nan):
        rows.append({"check": check, "term": term, "at": float(at), "value": float(value), "low": float(low),
                     "high": float(high)})

    for par, rhat, bulk, tail in zip(found["par"], found["rhat"], found["ess_bulk"], found["ess_tail"]):
        add("R-hat", str(par), rhat)
        add("effective draws in the middle (bulk)", str(par), bulk)
        add("effective draws in the tails", str(par), tail)
    add("divergent transitions", "", np.atleast_1d(found["divergent"])[0])
    if outcome == "numbers":
        band = found["made_band"]
        for x, observed, (low, middle, high) in zip(found["grid"], found["observed"], band):
            add("posterior predictive check", "density of the data", observed, at=x)
            add("posterior predictive check", "density of the made-up sets (median, 90 % range)", middle, at=x,
                low=low, high=high)
    else:
        for x, observed, (low, middle, high) in zip(found["grid"], found["observed"], found["made"]):
            add("posterior predictive check", "count in the data", observed, at=x)
            add("posterior predictive check", "count in the made-up sets (median, 90 % interval)", middle, at=x,
                low=low, high=high)
    print(f'Gives back {len(rows)} numbers of the check as a table (show="numbers"): R-hat and effective draws of each '
          "parameter, the divergent transitions, and the predictive check at each value (at=); leave out show= for "
          "the picture.")
    frame = nw.from_dict({k: [r[k] for r in rows] for k in rows[0]}, backend=table._frame.implementation)
    return table._new_table(frame)
