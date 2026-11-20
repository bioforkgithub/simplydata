"""S2: the fit block of every explain() printout (an R squared, AIC and BIC), checked against R.

R 4.6.2, performance 0.15, lme4 2.1.0, MASS, nnet, betareg 3.2-6, pscl 1.5-9; the R call is next to each
value. The printout rounds to 3 significant figures (AIC, BIC) or 3 decimals (R squared), so each check
holds the R value rounded the same way.
"""

import re

import simplydata as sdata
from simplydata.table import table as make_table

from test_s2_grouped import FARMS
from test_s2_model_tools_more import school3
from test_s2_models import TRIES
from test_s2_more_outcomes import ZEROS, graded_school


class Line(str):
    """The "How well it fits:" line, with the whole printout as .out (for the Method line under it)."""


def fit_line(capsys):
    out = capsys.readouterr().out
    lines = [line for line in out.splitlines() if line.startswith("How well it fits:")]
    assert len(lines) == 1, lines
    found = Line(lines[0])
    found.out = out
    return found


def aic_bic(line):
    found = re.search(r"AIC (-?[\d.]+), BIC (-?[\d.]+)", line)
    return float(found.group(1)), float(found.group(2))


def test_least_squares_aic_bic(capsys):
    make_table(sdata.get_example("school")).explain("marks", using=["hours", "breakfast"])
    line = fit_line(capsys)
    # R: m <- lm(marks ~ hours + breakfast, data = s); AIC(m) 1292.49254833665; BIC(m) 1305.26437574021
    assert aic_bic(line) == (1292, 1305)
    assert "smaller is better, but only to compare models of the same rows" in line and "pseudo" not in line
    assert "Method: AIC and BIC as R AIC(), BIC()." in line.out


def test_logistic_mcfadden(capsys):
    make_table(sdata.get_example("school")).explain("passed", using=["hours", "breakfast"], outcome="yes or no")
    line = fit_line(capsys)
    # R: m <- glm(y ~ hours + breakfast, data = s, family = binomial); performance::r2_mcfadden(m) 0.192269138384149
    #    AIC 204.963040749707; BIC 214.541911302378
    #    performance::r2_nagelkerke(m) 0.310, r2_tjur(m) 0.243 (S3a: printed for yes/no rows)
    assert ("How well it fits: pseudo R squared 0.192 (0 = no better than no columns); other pseudo R squared: "
            "Nagelkerke 0.310, Tjur 0.243 (each measures something different; none is a share explained). AIC 205, "
            "BIC 215") in line
    assert "explains" not in line and "performance::" not in line  # a pseudo R squared is not a share explained
    assert ("Method: McFadden's pseudo R squared (1 - log-likelihood / log-likelihood with no columns) as R "
            "performance::r2_mcfadden(); Nagelkerke's") in line.out and "AIC and BIC as R AIC(), BIC()." in line.out
    assert aic_bic(line) == (205, 215)


def test_successes_out_of_tries_mcfadden(capsys):
    make_table(TRIES).explain("yes", using=["dose"], outcome="yes or no", out_of="tries")
    line = fit_line(capsys)
    # R: m <- glm(cbind(yes, tries - yes) ~ dose, data = k, family = binomial)
    #    1 - logLik(m) / logLik(update(m, . ~ 1)) 0.629841844972959; AIC 40.6696039348049; BIC 41.6394172343809
    assert "pseudo R squared 0.630" in line and aic_bic(line) == (40.7, 41.6)


def test_negative_binomial_mcfadden(capsys):
    make_table(sdata.get_example("meadow")).explain("nettle", using=["grazed", "field"], outcome="counts that vary a lot")
    line = fit_line(capsys)
    # R: m <- MASS::glm.nb(nettle ~ grazed + field, data = meadow); performance::r2_mcfadden(m) 0.131935806298581
    #    (the model with no columns refitted with its own theta, glm.nb(nettle ~ 1)); AIC 165.908562845658;
    #    BIC 172.914549753969
    assert "pseudo R squared 0.132" in line and aic_bic(line) == (166, 173)


def test_gamma_aic_bic(capsys):
    make_table(sdata.get_example("trial")).explain("days", using=["treatment", "age"], outcome="positive numbers")
    line = fit_line(capsys)
    # R: m <- glm(days ~ treatment + age, data = trial, family = Gamma(link = "log"))
    #    AIC(m) 1688.47620194811; BIC(m) 1699.62616891924 (dispersion deviance / n, as R logLik())
    assert aic_bic(line) == (1688, 1700) and "pseudo" not in line


def test_quasi_poisson_and_gee_say_there_is_no_likelihood(capsys):
    school = make_table(sdata.get_example("school"))
    school.explain("days_absent", using="hours", outcome="counts (overdispersed)")
    assert "Quasi-Poisson has no likelihood, so there is no AIC, BIC or pseudo R squared" in capsys.readouterr().out
    school.explain("marks", using=["hours"], grouped_by="school", effects="for the whole population")
    assert "GEE has no likelihood, so there is no AIC, BIC or R squared." in capsys.readouterr().out


def test_mixed_model_nakagawa_and_reml_aic(capsys, needs_r):
    make_table(sdata.get_example("school")).explain("marks", using=["hours", "breakfast"], grouped_by="school")
    line = fit_line(capsys)
    # R: m <- lmer(marks ~ hours + breakfast + (1 | school), data = s); performance::r2_nakagawa(m):
    #    conditional 0.629324749460017, marginal 0.390814395007836; AIC(m) 1234.78852020829; BIC(m) 1250.75330446274
    assert "R squared 0.391 from the columns alone and 0.629 with the groups too" in line
    assert aic_bic(line) == (1235, 1251)
    assert ("Method: Nakagawa's R squared for mixed models (marginal: the columns alone; conditional: with the "
            "groups) as R performance::r2_nakagawa(); AIC and BIC of the REML fit as R AIC(), BIC().") in line.out


def test_nested_groups_nakagawa_from_r(capsys, needs_r):
    make_table(school3()).explain("marks", using=["hours", "breakfast"], grouped_by=["school", "class"])
    line = fit_line(capsys)
    # R: m <- lmer(marks ~ hours + breakfast + (1 | school/class), data = s3); performance::r2_nakagawa(m):
    #    conditional 0.638011803708462, marginal 0.386625831276217; AIC 1236.41678798779; BIC 1255.57452909313
    assert "R squared 0.387 from the columns alone and 0.638 with the groups too" in line
    assert aic_bic(line) == (1236, 1256)


def test_mixed_model_without_r_keeps_aic_and_leaves_nakagawa_out(capsys, monkeypatch):
    # no R: the mixed model is fitted by statsmodels as usual; Nakagawa's R squared (R performance) is left out
    from simplydata import _r

    monkeypatch.setattr(_r, "_STATE", {"error": "no R", "missing": "rpy2"})
    make_table(sdata.get_example("school")).explain("marks", using=["hours", "breakfast"], grouped_by="school")
    out = capsys.readouterr().out
    line = [row for row in out.splitlines() if row.startswith("How well it fits:")]
    assert len(line) == 1 and "Nakagawa" not in line[0]
    assert aic_bic(line[0]) == (1235, 1251) and "AIC and BIC of the REML fit as R AIC(), BIC()." in out
    assert ('The R squared is left out: for mixed models it comes from R performance (needs R: pip install '
            '"simplydata[r]").') in out


def test_own_slopes_nakagawa_from_r(capsys, needs_r):
    make_table(FARMS.copy()).explain("growth", using=["feed", "organic"], grouped_by="farm", own_slope_for="feed")
    line = fit_line(capsys)
    # R: m <- lmer(growth ~ feed + organic + (1 + feed | farm), data = slopes); performance::r2_nakagawa(m):
    #    conditional 0.965665519438447, marginal 0.273146515736974; AIC 849.835434577907; BIC 872.186132534138
    assert "R squared 0.273 from the columns alone and 0.966 with the groups too" in line
    assert aic_bic(line) == (850, 872)


def test_glmer_nakagawa_from_r(capsys, needs_r):
    make_table(sdata.get_example("school")).explain("passed", using=["hours"], outcome="yes or no", grouped_by="school")
    line = fit_line(capsys)
    # R: m <- glmer(y ~ hours + (1 | school), data = s, family = binomial); performance::r2_nakagawa(m):
    #    conditional 0.590535726400666, marginal 0.324197445162453; AIC 183.438326768241; BIC 193.017197320912
    assert "R squared 0.324 from the columns alone and 0.591 with the groups too" in line
    assert aic_bic(line) == (183, 193)


def test_ordered_and_groups_mcfadden(capsys):
    make_table(graded_school()).explain("grade", using=["hours", "breakfast"], outcome="ordered groups",
                                        in_order=["low", "middle", "high"])
    line = fit_line(capsys)
    # R: o <- MASS::polr(grade ~ hours + breakfast, data = s, Hess = TRUE, control = list(reltol = 1e-14,
    #    maxit = 10000)); performance::r2_mcfadden(o) 0.209120925129079; AIC 300.481089131691; BIC 313.252916535252
    assert "pseudo R squared 0.209" in line and aic_bic(line) == (300, 313)
    make_table(sdata.get_example("meadow")).explain("field", using=["clover", "nettle"], outcome="groups")
    line = fit_line(capsys)
    # R: mn <- nnet::multinom(field ~ clover + nettle, data = meadow, reltol = 1e-12, maxit = 1000)
    #    performance::r2_mcfadden(mn) 0.107239283471619; AIC 70.8478736410936; BIC 79.2550579310665
    assert "pseudo R squared 0.107" in line and aic_bic(line) == (70.8, 79.3)


def test_shares_and_zeros_fit_lines(capsys, needs_r):
    growth = sdata.get_example("growth").assign(share=lambda d: d.forest / 100)
    make_table(growth).explain("share", using=["year", "country"], outcome="shares")
    line = fit_line(capsys)
    # R: b <- betareg::betareg(share ~ year + country, data = g); b$pseudo.r.squared 0.982552259439924
    #    (= performance::r2(b)); AIC -238.224539374173; BIC -226.517077062685
    assert "pseudo R squared 0.983" in line and aic_bic(line) == (-238, -227)
    make_table(ZEROS).explain("count", using=["depth", "site"], outcome="counts with many zeros")
    line = fit_line(capsys)
    # R: z <- pscl::zeroinfl(count ~ depth + site, data = zeros, dist = "poisson")
    #    1 - logLik(z) / logLik(zeroinfl(count ~ 1 | 1, data = zeros, dist = "poisson")) 0.0890169403612794
    #    AIC 186.664237375923; BIC 199.230304749256
    assert "pseudo R squared 0.089" in line and aic_bic(line) == (187, 199)


def test_glmer_own_slopes_singular_fit_has_no_nakagawa(capsys, needs_r):
    make_table(FARMS.copy()).explain("sick", using=["feed"], outcome="yes or no", grouped_by="farm",
                                     own_slope_for="feed")
    line = fit_line(capsys)
    # R: m <- glmer(y ~ feed + (1 + feed | farm), data = slopes, family = binomial) (singular fit);
    #    performance::r2_nakagawa(m): conditional NA ("Can't compute r-squared. Some variance components equal
    #    zero"); AIC 212.592690298482; BIC 228.557474552933
    assert "no R squared for this model" in line
    assert aic_bic(line) == (213, 229)


# ---------------------------------------------------------------- review fixes: one row per group, R refusing the refit
def test_one_row_per_group_is_refused_before_fitting(capsys):
    import pytest

    from simplydata import SimplydataError

    school = sdata.get_example("school")
    # R: s$pid <- s$pupil; lmer(marks ~ hours + (1 | pid), data = s): Error: number of levels of each grouping
    #    factor must be < number of observations (problems: pid)
    with pytest.raises(SimplydataError, match='grouped_by="pid" has 180 groups for 180 rows'):
        make_table(school.assign(pid=school.pupil)).explain("marks", using=["hours"], grouped_by="pid")
    # R: s$cls <- s$pupil; lmer(marks ~ hours + (1 | school/cls), data = s): Error: number of levels of each
    #    grouping factor must be < number of observations (problems: cls:school)
    with pytest.raises(SimplydataError, match='"cls" inside "school" has 180 groups for 180 rows'):
        make_table(school.assign(cls=school.pupil)).explain("marks", using=["hours"], grouped_by=["school", "cls"])
    # R: glmer(passed ~ hours + (1 | pid), family = binomial) stops with the same lme4 check
    with pytest.raises(SimplydataError, match="has 180 groups for 180 rows"):
        make_table(school.assign(pid=school.pupil)).explain("passed", using=["hours"], outcome="yes or no",
                                                            grouped_by="pid")
    assert capsys.readouterr().out == ""


def test_r_refusing_the_nakagawa_refit_gives_a_plain_note(capsys, monkeypatch, needs_r):
    # with the group check set aside, statsmodels fits one row per group quietly; R lme4::lmer() refuses the refit
    # (R: lmer(marks ~ hours + (1 | pid), data = s): Error: number of levels of each grouping factor must be <
    # number of observations), which now gives "no R squared" instead of an error after the printout
    from simplydata.table.models import ModelWords

    monkeypatch.setattr(ModelWords, "_check_group_sizes", staticmethod(lambda *args: None))
    school = sdata.get_example("school")
    make_table(school.assign(pid=school.pupil)).explain("marks", using=["hours"], grouped_by="pid")
    assert "How well it fits: no R squared for this model." in fit_line(capsys)


def test_r_stopping_in_nakagawa_is_caught_in_the_fit_block(capsys, monkeypatch):
    # any stop inside R (SimplydataError "R stopped with: ...") leaves the R squared out with a plain note
    from simplydata import SimplydataError
    from simplydata.table import models_r

    def stopped(model):
        raise SimplydataError("R stopped with: number of levels of each grouping factor must be < number of "
                              "observations")

    monkeypatch.setattr(models_r, "nakagawa_r", stopped)
    make_table(sdata.get_example("school")).explain("marks", using=["hours", "breakfast"], grouped_by="school")
    line = fit_line(capsys)
    # R: AIC(lmer(marks ~ hours + breakfast + (1 | school), data = s)) 1234.78852020829; BIC 1250.75330446274
    assert "no R squared" in line and aic_bic(line) == (1235, 1251)
