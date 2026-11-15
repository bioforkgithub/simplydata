"""S2: the fit block of every explain() printout (an R squared, AIC and BIC), checked against R.

R 4.6.2, performance 0.15, lme4 2.1.0, MASS, nnet, betareg 3.2-6, pscl 1.5-9; the R call is next to each
value. The printout rounds to 3 significant figures (AIC, BIC) or 3 decimals (R squared), so each check
holds the R value rounded the same way.
"""

import re

import numpy as np
import pytest

import simplydata as sdata
from simplydata.table import table as make_table

from test_s2_grouped import FARMS
from test_s2_model_tools_more import school3
from test_s2_models import TRIES
from test_s2_more_outcomes import ZEROS, graded_school


def fit_line(capsys):
    lines = [line for line in capsys.readouterr().out.splitlines() if line.startswith("How well it fits:")]
    assert len(lines) == 1, lines
    return lines[0]


def aic_bic(line):
    found = re.search(r"AIC = (-?[\d.]+) and BIC = (-?[\d.]+)", line)
    return float(found.group(1)), float(found.group(2))


def test_least_squares_aic_bic(capsys):
    make_table(sdata.example("school")).explain("marks", using=["hours", "breakfast"])
    line = fit_line(capsys)
    # R: m <- lm(marks ~ hours + breakfast, data = s); AIC(m) 1292.49254833665; BIC(m) 1305.26437574021
    assert aic_bic(line) == (1292, 1305)
    assert "as R AIC() and BIC()" in line and "pseudo" not in line


def test_logistic_mcfadden(capsys):
    make_table(sdata.example("school")).explain("passed", using=["hours", "breakfast"], outcome="yes or no")
    line = fit_line(capsys)
    # R: m <- glm(y ~ hours + breakfast, data = s, family = binomial); performance::r2_mcfadden(m) 0.192269138384149
    #    AIC 204.963040749707; BIC 214.541911302378
    assert "McFadden's pseudo R squared = 0.192" in line and "performance::r2_mcfadden()" in line
    assert aic_bic(line) == (205, 215)


def test_successes_out_of_tries_mcfadden(capsys):
    make_table(TRIES).explain("yes", using=["dose"], outcome="yes or no", out_of="tries")
    line = fit_line(capsys)
    # R: m <- glm(cbind(yes, tries - yes) ~ dose, data = k, family = binomial)
    #    1 - logLik(m) / logLik(update(m, . ~ 1)) 0.629841844972959; AIC 40.6696039348049; BIC 41.6394172343809
    assert "McFadden's pseudo R squared = 0.630" in line and aic_bic(line) == (40.7, 41.6)


def test_negative_binomial_mcfadden(capsys):
    make_table(sdata.example("meadow")).explain("nettle", using=["grazed", "field"], outcome="counts that vary a lot")
    line = fit_line(capsys)
    # R: m <- MASS::glm.nb(nettle ~ grazed + field, data = meadow); performance::r2_mcfadden(m) 0.131935806298581
    #    (the model with no columns refitted with its own theta, glm.nb(nettle ~ 1)); AIC 165.908562845658;
    #    BIC 172.914549753969
    assert "McFadden's pseudo R squared = 0.132" in line and aic_bic(line) == (166, 173)


def test_gamma_aic_bic(capsys):
    make_table(sdata.example("trial")).explain("days", using=["treatment", "age"], outcome="positive numbers")
    line = fit_line(capsys)
    # R: m <- glm(days ~ treatment + age, data = trial, family = Gamma(link = "log"))
    #    AIC(m) 1688.47620194811; BIC(m) 1699.62616891924 (dispersion deviance / n, as R logLik())
    assert aic_bic(line) == (1688, 1700) and "pseudo" not in line


def test_quasi_poisson_and_gee_say_there_is_no_likelihood(capsys):
    school = make_table(sdata.example("school"))
    school.explain("days_absent", using="hours", outcome="counts (overdispersed)")
    assert "Quasi-Poisson has no likelihood, so there is no AIC, BIC or pseudo R squared" in capsys.readouterr().out
    school.explain("marks", using=["hours"], grouped_by="school", effects="for the whole population")
    assert "GEE has no likelihood, so there is no AIC, BIC or R squared." in capsys.readouterr().out


def test_mixed_model_nakagawa_and_reml_aic(capsys):
    make_table(sdata.example("school")).explain("marks", using=["hours", "breakfast"], grouped_by="school")
    line = fit_line(capsys)
    # R: m <- lmer(marks ~ hours + breakfast + (1 | school), data = s); performance::r2_nakagawa(m):
    #    conditional 0.629324749460017, marginal 0.390814395007836; AIC(m) 1234.78852020829; BIC(m) 1250.75330446274
    assert "(Nakagawa) = 0.391 from the columns alone (marginal) and 0.629 with the groups too" in line
    assert aic_bic(line) == (1235, 1251) and "of the REML fit" in line


def test_mixed_model_nakagawa_exact(capsys):
    from simplydata.table.models import ModelWords

    seen = {}
    original = ModelWords._fit_block

    def spy(model):
        seen["model"] = model
        return original(model)

    ModelWords._fit_block = staticmethod(spy)
    try:
        make_table(school3()).explain("marks", using=["hours", "breakfast"], grouped_by=["school", "class"])
    finally:
        ModelWords._fit_block = staticmethod(original)
    fit = seen["model"]["fit"]
    fixed = float(np.var(seen["model"]["X"] @ fit["beta"], ddof=1))
    total = fixed + fit["between"] + fit["inner"] + fit["within"]
    # R: m <- lmer(marks ~ hours + breakfast + (1 | school/class), data = s3); performance::r2_nakagawa(m):
    #    conditional 0.638011803708462, marginal 0.386625831276217; AIC 1236.41678798779; BIC 1255.57452909313
    assert fixed / total == pytest.approx(0.386625831276217, rel=1e-5)
    assert (total - fit["within"]) / total == pytest.approx(0.638011803708462, rel=1e-5)
    assert aic_bic(fit_line(capsys)) == (1236, 1256)


def test_own_slopes_nakagawa_from_r(capsys, needs_r):
    make_table(FARMS.copy()).explain("growth", using=["feed", "organic"], grouped_by="farm", own_slope_for="feed")
    line = fit_line(capsys)
    # R: m <- lmer(growth ~ feed + organic + (1 + feed | farm), data = slopes); performance::r2_nakagawa(m):
    #    conditional 0.965665519438447, marginal 0.273146515736974; AIC 849.835434577907; BIC 872.186132534138
    assert "(Nakagawa) = 0.273 from the columns alone (marginal) and 0.966 with the groups too" in line
    assert aic_bic(line) == (850, 872)


def test_glmer_nakagawa_from_r(capsys, needs_r):
    make_table(sdata.example("school")).explain("passed", using=["hours"], outcome="yes or no", grouped_by="school")
    line = fit_line(capsys)
    # R: m <- glmer(y ~ hours + (1 | school), data = s, family = binomial); performance::r2_nakagawa(m):
    #    conditional 0.590535726400666, marginal 0.324197445162453; AIC 183.438326768241; BIC 193.017197320912
    assert "(Nakagawa) = 0.324 from the columns alone (marginal) and 0.591 with the groups too" in line
    assert aic_bic(line) == (183, 193)


def test_ordered_and_groups_mcfadden(capsys):
    make_table(graded_school()).explain("grade", using=["hours", "breakfast"], outcome="ordered groups",
                                        in_order=["low", "middle", "high"])
    line = fit_line(capsys)
    # R: o <- MASS::polr(grade ~ hours + breakfast, data = s, Hess = TRUE, control = list(reltol = 1e-14,
    #    maxit = 10000)); performance::r2_mcfadden(o) 0.209120925129079; AIC 300.481089131691; BIC 313.252916535252
    assert "McFadden's pseudo R squared = 0.209" in line and aic_bic(line) == (300, 313)
    make_table(sdata.example("meadow")).explain("field", using=["clover", "nettle"], outcome="groups")
    line = fit_line(capsys)
    # R: mn <- nnet::multinom(field ~ clover + nettle, data = meadow, reltol = 1e-12, maxit = 1000)
    #    performance::r2_mcfadden(mn) 0.107239283471619; AIC 70.8478736410936; BIC 79.2550579310665
    assert "McFadden's pseudo R squared = 0.107" in line and aic_bic(line) == (70.8, 79.3)


def test_shares_and_zeros_fit_lines(capsys, needs_r):
    growth = sdata.example("growth").assign(share=lambda d: d.forest / 100)
    make_table(growth).explain("share", using=["year", "country"], outcome="shares")
    line = fit_line(capsys)
    # R: b <- betareg::betareg(share ~ year + country, data = g); b$pseudo.r.squared 0.982552259439924
    #    (= performance::r2(b)); AIC -238.224539374173; BIC -226.517077062685
    assert "pseudo R squared = 0.983" in line and aic_bic(line) == (-238, -227)
    make_table(ZEROS).explain("count", using=["depth", "site"], outcome="counts with many zeros")
    line = fit_line(capsys)
    # R: z <- pscl::zeroinfl(count ~ depth + site, data = zeros, dist = "poisson")
    #    1 - logLik(z) / logLik(zeroinfl(count ~ 1 | 1, data = zeros, dist = "poisson")) 0.0890169403612794
    #    AIC 186.664237375923; BIC 199.230304749256
    assert "McFadden's pseudo R squared = 0.089" in line and aic_bic(line) == (187, 199)


def test_glmer_own_slopes_singular_fit_has_no_nakagawa(capsys, needs_r):
    make_table(FARMS.copy()).explain("sick", using=["feed"], outcome="yes or no", grouped_by="farm",
                                     own_slope_for="feed")
    line = fit_line(capsys)
    # R: m <- glmer(y ~ feed + (1 + feed | farm), data = slopes, family = binomial) (singular fit);
    #    performance::r2_nakagawa(m): conditional NA ("Can't compute r-squared. Some variance components equal
    #    zero"); AIC 212.592690298482; BIC 228.557474552933
    assert "no R squared (R performance::r2_nakagawa() cannot give one for this model)" in line
    assert aic_bic(line) == (213, 229)
