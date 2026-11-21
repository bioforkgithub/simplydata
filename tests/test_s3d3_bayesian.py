"""S3d-3, Bayesian methods: bayesian=True on compare_averages_of, compare_before_and_after, compare_average_to,
find_correlation_between and compare_counts_of (R BayesFactor), and on explain and check_model_of (R rstanarm).

The numbers are checked against R with the same seed (the same draws), against long runs within four Monte Carlo
standard errors (MCSE), and the printouts for the S3c-L11 rules: the prior is named, the credible interval is
explained, with_seed= is printed, there is no p-value and no verdict word, and convergence warnings come before any
estimate. rstanarm is a large optional R package: its tests need it (SIMPLYDATA_REQUIRE_R=1 makes them fail, not skip,
when it is missing, as in CI).
"""

import os
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import bayes_r, bayes_words

DATA = Path(__file__).resolve().parents[1] / "validation" / "data"
VERDICT_WORDS = re.compile(r"significant|strong evidence|moderate evidence|anecdotal|proves|p-value =|\(p [=<]",
                           re.IGNORECASE)


def _sleep():
    d = pd.read_csv(DATA / "sleep.csv")
    return sdata.table(d.assign(group=d["group"].map({1: "drug 1", 2: "drug 2"})))


def _sleep_wide():
    d = pd.read_csv(DATA / "sleep.csv")
    return sdata.table(pd.DataFrame({"drug_1": d["extra"][:10].to_numpy(), "drug_2": d["extra"][10:].to_numpy()}))


def _need(packages):
    from simplydata._r import r_ready

    if not r_ready(packages):
        if os.environ.get("SIMPLYDATA_REQUIRE_R") == "1":
            pytest.fail(f"SIMPLYDATA_REQUIRE_R=1 but R or {', '.join(packages)} is missing")
        pytest.skip(f"needs R with {', '.join(packages)}")


@pytest.fixture
def needs_bayesfactor():
    _need(bayes_r.LIGHT_PACKAGES)


@pytest.fixture
def needs_rstanarm():
    _need(bayes_r.HEAVY_PACKAGES)


def _plain_rules(out):
    assert "credible interval: given the data and the prior, a 95 % chance" in out
    assert "with_seed=1" in out
    assert not VERDICT_WORDS.search(out), VERDICT_WORDS.search(out)


# ---------------------------------------------------------------- the light route: BayesFactor
def test_two_groups_give_the_bayes_factor_and_the_interval(needs_bayesfactor, capsys):
    r = _sleep().compare_averages_of("extra", for_each_group_in="group", bayesian=True).as_pandas()
    out = capsys.readouterr().out
    assert r["Bayes factor"][0] == pytest.approx(1.265925, rel=1e-6)  # BayesFactor's documentation: 1.27
    assert r["prior width"][0] == pytest.approx(np.sqrt(2) / 2)
    assert "The data are 1.27 times as likely if the averages of drug 1 and drug 2 differ as if they do not" in out
    assert "Cauchy prior on the effect size" in out and '"medium"' in out
    assert "There is no p-value" in out
    _plain_rules(out)
    assert r["difference 95 % credible interval low"][0] < r["difference"][0] < \
        r["difference 95 % credible interval high"][0]


def test_the_interval_is_r_with_the_same_seed(needs_bayesfactor):
    r = _sleep().compare_averages_of("extra", for_each_group_in="group", bayesian=True, with_seed=7).as_pandas()
    d = pd.read_csv(DATA / "sleep.csv")
    from simplydata._r import r_call

    found = r_call('b <- BayesFactor::ttestBF(x = x, y = y, rscale = "medium"); '
                   'set.seed(7, kind = "Mersenne-Twister", normal.kind = "Inversion", sample.kind = "Rejection"); '
                   'q <- summary(BayesFactor::posterior(b, iterations = 10000, progress = FALSE))$quantiles; '
                   'unname(q["beta (x - y)", c("2.5%", "50%", "97.5%")])', packages=("BayesFactor",),
                   x=d["extra"][:10].to_numpy(), y=d["extra"][10:].to_numpy())
    assert [r["difference 95 % credible interval low"][0], r["difference"][0],
            r["difference 95 % credible interval high"][0]] == pytest.approx(list(found), rel=1e-12)


def test_the_interval_is_within_monte_carlo_error_of_a_long_run(needs_bayesfactor):
    # The 10,000 draws of seed 1 have MCSE 0.027 (2.5 %), 0.012 (median) and 0.020 (97.5 %) (posterior::mcse_quantile
    # on these draws, 2026-11-21). A run of 200,000 draws (MCSE about a fifth of those) is the reference; four MCSE
    # of the short run leave a chance below 1 in 10,000 of a false failure for a correct interval.
    r = _sleep().compare_averages_of("extra", for_each_group_in="group", bayesian=True).as_pandas()
    d = pd.read_csv(DATA / "sleep.csv")
    from simplydata._r import r_call

    long = r_call('b <- BayesFactor::ttestBF(x = x, y = y, rscale = "medium"); set.seed(2); '
                  'p <- BayesFactor::posterior(b, iterations = 200000, progress = FALSE); '
                  'unname(stats::quantile(as.numeric(p[, "beta (x - y)"]), c(0.025, 0.5, 0.975)))',
                  packages=("BayesFactor",), x=d["extra"][:10].to_numpy(), y=d["extra"][10:].to_numpy())
    ours = [r["difference 95 % credible interval low"][0], r["difference"][0],
            r["difference 95 % credible interval high"][0]]
    for got, ref, mcse in zip(ours, long, (0.027, 0.012, 0.020)):
        assert abs(got - ref) < 4 * mcse


def test_paired_and_one_column(needs_bayesfactor, capsys):
    r = _sleep_wide().compare_before_and_after("drug_1", "drug_2", bayesian=True).as_pandas()
    assert r["Bayes factor"][0] == pytest.approx(17.25888, rel=1e-6)  # the example of R ttestBF's help
    out = capsys.readouterr().out
    assert "The data are 17.3 times as likely if the values changed on average" in out
    _plain_rules(out)
    one = _sleep_wide().compare_average_to("drug_1", 1, bayesian=True).as_pandas()
    # the posterior is that of the average minus 1 (the values average 0.75), not of the average itself
    assert one["difference"][0] < 0
    assert one["Bayes factor"][0] == pytest.approx(0.3356663, rel=1e-6)  # R ttestBF(x, mu = 1)
    out = capsys.readouterr().out
    assert "times as likely if it is 1 as if the average differs from 1" in out


def test_prior_width_changes_the_bayes_factor_and_is_printed(needs_bayesfactor, capsys):
    t = _sleep()
    medium = t.compare_averages_of("extra", for_each_group_in="group", bayesian=True).as_pandas()
    wide = t.compare_averages_of("extra", for_each_group_in="group", bayesian=True, prior_width="wide").as_pandas()
    number = t.compare_averages_of("extra", for_each_group_in="group", bayesian=True, prior_width=0.5).as_pandas()
    assert wide["prior width"][0] == pytest.approx(1.0) and number["prior width"][0] == pytest.approx(0.5)
    assert wide["Bayes factor"][0] != pytest.approx(medium["Bayes factor"][0])
    assert 'rscale = "wide"' in capsys.readouterr().out


def test_correlation_and_counts(needs_bayesfactor, capsys):
    m = sdata.table(pd.read_csv(DATA / "mtcars.csv"))
    r = m.find_correlation_between("mpg", "wt", bayesian=True).as_pandas()
    assert r["Bayes factor"][0] == pytest.approx(1.3286626e7, rel=1e-6)
    assert r["prior width"][0] == pytest.approx(1 / 3)
    assert -1 < r["r 95 % credible interval low"][0] < r["r"][0] < r["r 95 % credible interval high"][0] < 0
    out = capsys.readouterr().out
    assert "more than a million times as likely" in out and "JASP's default width is 1" in out
    _plain_rules(out)
    c = sdata.table(pd.read_csv(DATA / "mtcars.csv").astype({"am": str, "vs": str}))
    r = c.compare_counts_of("am", for_each_group_in="vs", bayesian=True).as_pandas()
    assert r["Bayes factor"][0] == pytest.approx(0.6313164, rel=1e-6)
    shares = r["share 0 in 0"][0] + r["share 1 in 0"][0]
    assert 0.95 < shares < 1.05  # posterior medians of two shares that add up to 1 in every draw
    out = capsys.readouterr().out
    assert "independent multinomial sampling" in out and "Gunel-Dickey" in out
    _plain_rules(out)


@pytest.mark.parametrize("call, message", [
    (lambda t: t.compare_averages_of("extra", for_each_group_in="group", bayesian=True, test="student"),
     "test= cannot be used with bayesian=True"),
    (lambda t: t.compare_averages_of("extra", for_each_group_in="group", prior_width="wide"),
     "prior_width= sets the prior"),
    (lambda t: t.compare_averages_of("extra", for_each_group_in="group", bayesian="yes"), "bayesian=True"),
    (lambda t: t.compare_averages_of("extra", for_each_group_in="group", bayesian=True, prior_width=-1),
     "prior_width= takes"),
    (lambda t: t.compare_averages_of("extra", for_each_group_in="group", bayesian=True, with_seed=1.5),
     "with_seed= is a whole number"),
    (lambda t: t.compare_average_to("extra", 1, with_seed=3), "leave it out"),
    (lambda t: t.find_correlation_between("extra", "ID", "extra", bayesian=True), "two different columns"),
    (lambda t: t.compare_counts_of("group", for_each_group_in="ID", bayesian=True, test="fisher"),
     "test= cannot be used"),
])
def test_wrong_bayesian_calls_are_explained(call, message):
    t = sdata.table(pd.read_csv(DATA / "sleep.csv").assign(group=lambda d: d["group"].astype(str)))
    with pytest.raises(SimplydataError, match=re.escape(message)):
        call(t)


def test_three_groups_are_refused(needs_bayesfactor):
    with pytest.raises(SimplydataError, match="2 groups"):
        sdata.table(sdata.get_example("marks")).compare_averages_of("marks", for_each_group_in="class", bayesian=True)


def test_without_r_the_bayesian_words_say_what_to_install():
    from simplydata._r import r_ready

    if r_ready(bayes_r.LIGHT_PACKAGES):
        pytest.skip("BayesFactor is installed here")
    with pytest.raises(SimplydataError, match="BayesFactor"):
        _sleep().compare_averages_of("extra", for_each_group_in="group", bayesian=True)


# ---------------------------------------------------------------- the heavy route: rstanarm
def test_convergence_warnings_say_what_to_do():
    found = {"par": ["a", "b"], "rhat": np.array([1.002, 1.05]), "ess_bulk": np.array([900.0, 120.0]),
             "ess_tail": np.array([800.0, 90.0]), "divergent": 3, "treedepth": 0, "draws": 4000}
    warnings, summary = bayes_words.convergence(found)
    text = " ".join(warnings)
    assert "R-hat above 1.01 for 1 of 2" in text and "too few effective draws" in text
    assert "3 divergent transitions" in text and text.count("What to do") == 3
    good = dict(found, rhat=np.array([1.0, 1.001]), ess_bulk=np.array([900.0, 1000.0]),
                ess_tail=np.array([800.0, 700.0]), divergent=0)
    assert bayes_words.convergence(good)[0] == []
    assert "R-hat at most 1.00" in bayes_words.convergence(good)[1]


def test_warnings_come_before_the_estimates(needs_rstanarm, monkeypatch, capsys):
    real = bayes_r.stan_model

    def troubled(model, seed):
        found = real(model, seed)
        found["rhat"] = found["rhat"] + 0.2
        return found

    monkeypatch.setattr(bayes_r, "stan_model", troubled)
    sdata.table(sdata.get_example("school")).explain("marks", using=["hours"], bayesian=True)
    out = capsys.readouterr().out
    assert out.index("Warning: the 4 chains do not agree") < out.index("Explaining")


def test_explain_matches_r_and_a_long_run(needs_rstanarm, capsys):
    mt = pd.read_csv(DATA / "mtcars.csv")
    r = sdata.table(mt).explain("mpg", using=["wt", "hp"], bayesian=True).as_pandas().set_index("term")
    out = capsys.readouterr().out
    assert "Prior used" in out and "Adjusted prior" in out and "R-hat at most" in out
    assert "There are no p-values" in out and "seed = with_seed" in out
    _plain_rules(out)
    from simplydata._r import r_call

    long = r_call("m <- rstanarm::stan_glm(mpg ~ wt + hp, data = data.frame(mpg, wt, hp), seed = 2, refresh = 0, "
                  "cores = 1, iter = 20000); ci <- rstanarm::posterior_interval(m, prob = 0.95); "
                  "c(unname(coef(m)['wt']), ci['wt', 1], ci['wt', 2])", packages=bayes_r.HEAVY_PACKAGES,
                  mpg=mt["mpg"].to_numpy(dtype=float), wt=mt["wt"].to_numpy(dtype=float),
                  hp=mt["hp"].to_numpy(dtype=float))
    # MCSE of the 4000 draws for wt (posterior::mcse_median, mcse_quantile; 2026-11-21): 0.018, 0.036, 0.046
    ours = [r.loc["wt", "effect"], r.loc["wt", "95 % credible interval low"], r.loc["wt", "95 % credible interval high"]]
    for got, ref, mcse in zip(ours, long, (0.018, 0.036, 0.046)):
        assert abs(got - ref) < 4 * mcse
    assert (r["R-hat"].dropna() < 1.01).all() and (r["effective draws (middle)"].dropna() > 400).all()


def test_yes_or_no_gives_odds_ratios_and_the_mixed_model_runs(needs_rstanarm, capsys):
    mt = pd.read_csv(DATA / "mtcars.csv")
    r = sdata.table(mt).explain("am", using=["wt"], outcome="yes or no", bayesian=True).as_pandas()
    from simplydata._r import r_call

    found = r_call("m <- rstanarm::stan_glm(am ~ wt, data = data.frame(am, wt), family = binomial(), seed = 1, "
                   "refresh = 0, cores = 1); unname(exp(coef(m)))", packages=bayes_r.HEAVY_PACKAGES,
                   am=mt["am"].to_numpy(dtype=float), wt=mt["wt"].to_numpy(dtype=float))
    assert r["effect"].tolist() == pytest.approx(list(found), rel=1e-12)
    assert "odds ratio" in capsys.readouterr().out
    g = sdata.table(sdata.get_example("school")).explain("marks", using=["hours"], grouped_by="school",
                                                        bayesian=True).as_pandas()
    assert 'spread between the "school" groups (standard deviation)' in g["term"].tolist()
    assert "stan_glmer(marks ~ hours + (1 | school)" in capsys.readouterr().out


def test_explain_refuses_what_it_does_not_fit():
    t = sdata.table(sdata.get_example("school"))
    with pytest.raises(SimplydataError, match="robust_errors= cannot be used with bayesian=True"):
        t.explain("marks", using=["hours"], bayesian=True, robust_errors=True)
    with pytest.raises(SimplydataError, match='outcome="numbers", "yes or no" or "counts"'):
        t.explain("marks", using=["hours"], bayesian=True, outcome="positive numbers")


def test_check_model_draws_the_predictive_checks(needs_rstanarm, capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    t = sdata.table(sdata.get_example("school"))
    chart = t.check_model_of("marks", using=["hours", "breakfast"], bayesian=True)
    numbers = chart._check_numbers
    assert numbers["made"].shape == (50, 256) and len(numbers["observed"]) == 256
    out = capsys.readouterr().out
    assert "Posterior predictive check" in out and "posterior_predict(draws = 50" in out
    prior = t.check_model_of("marks", using=["hours", "breakfast"], bayesian=True, show="prior check")
    # the prior allows far more than the data: its made-up sets spread wider than the data
    assert np.ptp(prior._check_numbers["grid"]) > np.ptp(numbers["grid"])
    assert "prior_PD = TRUE" in capsys.readouterr().out
    # privacy: nothing was written in the working folder (rstanarm's models are compiled when it is installed)
    assert list(tmp_path.iterdir()) == []


def test_check_model_refuses_show_without_bayesian():
    t = sdata.table(sdata.get_example("school"))
    with pytest.raises(SimplydataError, match="go with bayesian=True"):
        t.check_model_of("marks", using=["hours"], show="prior check")
    with pytest.raises(SimplydataError):
        t.check_model_of("marks", using=["hours"], bayesian=True, show="posterior")
