"""Tests for phase S3b-3, survival and person-time: at_time_points=, test_method="life table", allowing_for=,
followed_from=, average_time_up_to=, value= and competing_with= on the survival words, distribution= and
test_method="fine-gray" on explain_survival, Harrell's C, table.find_risk_over_time, chart.draw_risk_curves and
table.add_time_and_event_columns.

Reference values come from R 4.6.2 with survival 3.8.12, cmprsk 2.2.12, survRM2 1.0.4, KMsurv 0.1.6 and
adjustedCurves 0.12.0:
  d <- read.csv(".../data/trial.csv"); d$ev <- as.integer(d$died == "yes")
  mgus2: et <- ifelse(pstat == 1, ptime, futime); ev <- ifelse(pstat == 1, "pcm", ifelse(death == 1, "death", "alive"))
"""

import math

import numpy as np
import pandas as pd
import pytest

import simplydata as sdata
from simplydata import SimplydataError
from simplydata.table import table as make_table
from simplydata.table.survival import kaplan_meier

ENGINES = ["pandas", "polars"]


@pytest.fixture(params=ENGINES)
def engine(request):
    return request.param


def make(data, engine):
    if engine == "polars":
        pl = pytest.importorskip("polars")
        return make_table(pl.from_pandas(data))
    return make_table(data)


def frame(result):
    return result._frame.to_pandas()


@pytest.fixture
def trial():
    return sdata.get_example("trial")


def with_entry(trial):
    """Every third row followed from min(50.5, days / 2 + 0.25) (as in the R reference): no start time equals an
    event time (see test_a_start_time_on_an_event_time_is_named)."""
    d = trial.copy()
    d["entry"] = [min(50.5, t / 2 + 0.25) if (i + 1) % 3 == 0 else 0.0 for i, t in enumerate(d["days"])]
    return d


@pytest.fixture
def mgus2(needs_r):
    from simplydata._r import r_call

    f = r_call("d <- survival::mgus2; et <- ifelse(d$pstat == 1, d$ptime, d$futime); "
               "ev <- ifelse(d$pstat == 1, 'pcm', ifelse(d$death == 1, 'death', 'alive')); "
               "list(etime = et, event = ev, age = d$age, sex = as.character(d$sex))")
    return pd.DataFrame({k: (list(v) if k in ("event", "sex") else np.asarray(v, float)) for k, v in f.items()})


# ---------------------------------------------------------------- at_time_points=
def test_survival_at_time_points_matches_r(trial, engine, capsys):
    # summary(survfit(Surv(days, ev) ~ treatment, data = d), times = c(365, 730), extend = TRUE)
    out = frame(make(trial, engine).find_survival_over_time(time="days", event="died", for_each_group_in="treatment",
                                                            at_time_points=[730, 365, 5000]))
    assert list(out.columns) == ["treatment", "time", "at risk", "events by then", "survival", "95 % CI low",
                                 "95 % CI high"]
    got = out[out["time"] < 5000]
    assert got["survival"].tolist() == pytest.approx([0.760345192104403, 0.499529340108079, 0.643379890209158,
                                                      0.390062082323719], rel=1e-9)
    assert got["95 % CI low"].tolist() == pytest.approx([0.658011987159109, 0.367824515416416, 0.53152133606824,
                                                         0.271363809683686], rel=1e-9)
    assert got["at risk"].tolist() == [37, 13, 34, 12]
    assert out[out["time"] == 5000]["survival"].isna().all()
    printed = capsys.readouterr().out
    assert "read in order" in printed and "not followed that long" in printed and "extend = TRUE" in printed
    assert "76.0 % still without the event" in printed


def test_at_times_is_another_name(trial, capsys):
    out = frame(sdata.table(trial).find_survival_over_time(time="days", event="died", at_times=365))
    assert len(out) == 1
    assert "at_times= is at_time_points=" in capsys.readouterr().out


def test_time_points_are_checked(trial):
    t = sdata.table(trial)
    with pytest.raises(SimplydataError, match="below 0"):
        t.find_survival_over_time(time="days", event="died", at_time_points=[-1])
    with pytest.raises(SimplydataError, match="numbers"):
        t.find_survival_over_time(time="days", event="died", at_time_points=["a"])
    with pytest.raises(SimplydataError, match="twice"):
        t.find_survival_over_time(time="days", event="died", at_time_points=[1, 1])


# ---------------------------------------------------------------- method="life table"
def test_life_table(trial, engine, capsys, needs_r):
    out = frame(make(trial, engine).find_survival_over_time(time="days", event="died", for_each_group_in="treatment",
                                                            test_method="life table", at_time_points=[0, 365, 730]))
    new = out[out["treatment"] == "new medicine"].reset_index(drop=True)
    assert new["at start"].tolist() == [60, 37, 13]
    assert new["lost"].tolist() == [9, 14, 12] and new["events"].tolist() == [14, 10, 1]
    assert new["effective at risk"].tolist() == pytest.approx([55.5, 30.0, 7.0])
    assert new["survival at the start"][1] == pytest.approx(1 - 14 / 55.5, rel=1e-12)
    assert math.isnan(new["interval end"][2])
    printed = capsys.readouterr().out
    assert "actuarial assumption" in printed and "KMsurv::lifetab" in printed


def test_life_table_needs_points_from_zero(trial):
    t = sdata.table(trial)
    with pytest.raises(SimplydataError, match="needs at_time_points="):
        t.find_survival_over_time(time="days", event="died", test_method="life table")
    with pytest.raises(SimplydataError, match="start at 0"):
        t.find_survival_over_time(time="days", event="died", test_method="actuarial", at_time_points=[10, 365])
    with pytest.raises(SimplydataError, match="does not know"):
        t.find_survival_over_time(time="days", event="died", test_method="nelson")


# ---------------------------------------------------------------- allowing_for= (strata)
def test_stratified_cox_and_harrells_c_match_r(trial, engine, capsys, needs_r):
    # coxph(Surv(days, ev) ~ age + strata(treatment), data = d); concordance(f)
    out = frame(make(trial, engine).explain_survival(time="days", event="died", using="age", allowing_for="treatment"))
    assert out["coefficient"][0] == pytest.approx(0.0503473922428612, rel=1e-7)
    assert out["standard error"][0] == pytest.approx(0.0118856847596112, rel=1e-6)
    assert out["Harrell's C"][0] == pytest.approx(0.646797153024911, rel=1e-9)
    printed = capsys.readouterr().out
    assert "no hazard ratio for" in printed and "strata(treatment)" in printed
    assert "likely too high for new rows" in printed and "hopeful" not in printed


def test_stratified_log_rank_matches_r(trial, engine, capsys):
    # survdiff(Surv(days, ev) ~ treatment + strata(age > 60), data = d)
    data = trial.assign(older=np.where(trial["age"] > 60, "over 60", "60 or under"))
    r = frame(make(data, engine).compare_survival(time="days", event="died", for_each_group_in="treatment",
                                                  allowing_for="older")).iloc[0]
    assert r["statistic"] == pytest.approx(1.168889124194, rel=1e-9)
    assert r["test"] == "stratified log-rank test"
    assert "within each" in capsys.readouterr().out


def test_number_columns_are_refused_where_allowing_for_stratifies(trial):
    t = sdata.table(trial)
    with pytest.raises(SimplydataError, match="using="):
        t.explain_survival(time="days", event="died", using="treatment", allowing_for="age")
    with pytest.raises(SimplydataError, match="turn_into_text"):
        t.compare_survival(time="days", event="died", for_each_group_in="treatment", allowing_for="age")
    with pytest.raises(SimplydataError, match="one job"):
        t.explain_survival(time="days", event="died", using="treatment", allowing_for="treatment")


# ---------------------------------------------------------------- followed_from=
def test_delayed_entry_matches_r(trial, engine, capsys, needs_r):
    d = with_entry(trial)
    t = make(d, engine)
    # summary(survfit(Surv(entry, days, ev) ~ 1), times = c(200, 500))
    at = frame(t.find_survival_over_time(time="days", event="died", followed_from="entry", at_time_points=[200, 500]))
    assert at["survival"].tolist() == pytest.approx([0.80864307977089, 0.590886079325898], rel=1e-9)
    assert at["at risk"].tolist() == [99, 53]
    # coxph(Surv(entry, days, ev) ~ age + treatment)
    cox = frame(t.explain_survival(time="days", event="died", using=["age", "treatment"], followed_from="entry"))
    assert cox["coefficient"].tolist() == pytest.approx([0.0497666177412231, 0.28508129380669], rel=1e-6)
    # the log-rank test with start times = the score test of coxph(..., ties = "exact"), tied times and all (with
    # ties = "breslow" it differs a little); summary() of an exact-ties fit has no score test, so coxph()$score
    from simplydata._r import r_call

    lr = frame(t.compare_survival(time="days", event="died", for_each_group_in="treatment", followed_from="entry"))
    want = r_call("m <- survival::coxph(survival::Surv(s, t, e) ~ g, ties = 'exact'); "
                  "c(unname(m$score), stats::pchisq(unname(m$score), 1, lower.tail = FALSE))",
                  s=d["entry"].to_numpy(float), t=d["days"].to_numpy(float),
                  e=(d["died"] == "yes").to_numpy(float), g=d["treatment"].to_numpy(object))
    assert lr["statistic"][0] == pytest.approx(float(want[0]), rel=1e-9)
    assert lr["p-value"][0] == pytest.approx(float(want[1]), rel=1e-9)
    out = capsys.readouterr().out
    assert 'ties = "exact"' in out and "breslow" not in out


def test_kaplan_meier_with_entry_counts_rows_at_risk_after_their_start():
    km = kaplan_meier([3, 5, 7, 9], [True, False, True, True], entry=[0, 1, 2, 6])
    assert km["at_risk"].tolist() == [3, 2, 1]


def test_rows_that_start_at_an_event_time_are_fitted_as_r_does(capsys, needs_r):
    # statsmodels PHReg counts a row as at risk at an event time equal to its start; R coxph does not, and R is
    # right for split rows (one person would count twice), so such data are fitted by R:
    # coxph(Surv(s, t, e) ~ x) = -0.52140133 (statsmodels PHReg(entry=) gives -0.54883975)
    data = pd.DataFrame({"t": [3, 5, 7, 9, 4, 6, 8, 10], "e": [1, 1, 1, 0, 1, 0, 1, 1], "x": [1, 2, 3, 4, 2, 1, 5, 3],
                         "s": [0, 0, 5, 0, 0, 0, 0, 0]})
    out = frame(sdata.table(data).explain_survival(time="t", event="e", using="x", followed_from="s"))
    assert out["coefficient"][0] == pytest.approx(-0.52140133, rel=1e-6)
    assert "starts at an event time" in capsys.readouterr().out


def test_stanford_heart_transplant_matches_coxph(needs_r):
    # coxph(Surv(start, stop, event) ~ age + surgery + transplant, data = heart) (Crowley & Hu 1977)
    from pathlib import Path

    heart = pd.read_csv(Path(__file__).resolve().parents[1] / "validation" / "data" / "heart.csv")
    out = frame(sdata.table(heart).explain_survival(time="stop", event="event", using=["age", "surgery", "transplant"],
                                                    followed_from="start"))
    assert out["coefficient"].tolist() == pytest.approx([0.0305363149142, -0.7733276453, 0.0160956052965], rel=1e-6)


def test_followed_from_is_checked(trial):
    d = with_entry(trial)
    with pytest.raises(SimplydataError, match="must be before"):
        sdata.table(d.assign(entry=d["days"])).find_survival_over_time(time="days", event="died", followed_from="entry")
    d.loc[0, "entry"] = np.nan
    with pytest.raises(SimplydataError, match="empty"):
        sdata.table(d).explain_survival(time="days", event="died", using="age", followed_from="entry")


# ---------------------------------------------------------------- average_time_up_to=
def test_restricted_mean_and_difference(trial, engine, capsys, needs_r):
    t = make(trial, engine)
    out = frame(t.find_survival_over_time(time="days", event="died", for_each_group_in="treatment",
                                          average_time_up_to=700))
    # summary(survfit(Surv(days, ev) ~ treatment), rmean = 700)$table[, c("rmean", "se(rmean)")]
    assert out["average time without the event"].tolist() == pytest.approx([528.286503, 473.486464], rel=1e-8)
    printed = capsys.readouterr().out
    assert "spent on average" in printed and "lived" not in printed and "restricted mean survival time" in printed
    r = frame(t.compare_survival(time="days", event="died", for_each_group_in="treatment",
                                 average_time_up_to=700)).iloc[0]
    assert r["difference in average time"] == pytest.approx(473.486464 - 528.286503, rel=1e-6)
    assert r["statistic"] == pytest.approx(1.53, abs=0.01)  # the log-rank test is still first
    with pytest.raises(SimplydataError, match="at most 1046"):
        t.compare_survival(time="days", event="died", for_each_group_in="treatment", average_time_up_to=2000)


def test_rmst_difference_on_lung_matches_survrm2(needs_r):
    from simplydata._r import r_call

    f = r_call("l <- survival::lung; list(time = l$time, status = l$status - 1, sex = as.character(l$sex))")
    data = pd.DataFrame({"time": f["time"], "status": f["status"], "sex": ["male" if s == "1" else "female"
                                                                            for s in f["sex"]]})
    r = frame(sdata.table(data).compare_survival(time="time", event="status", for_each_group_in="sex",
                                                 average_time_up_to=365)).iloc[0]
    # survRM2::rmst2(time, status, sex == 2, tau = 365): female - male = 55.970324 (26.6529364 to 85.2877123)
    assert r["difference in average time"] == pytest.approx(-55.970324, rel=1e-6)  # "male" minus "female"
    assert r["average time in male"] == pytest.approx(241.49509, rel=1e-6)


# ---------------------------------------------------------------- three kinds of outcome (S3b-L6)
def test_three_kinds_are_refused_and_point_to_find_risk_over_time(trial):
    data = trial.assign(died=np.where(trial["age"] > 75, "moved away", trial["died"]))
    t = sdata.table(data)
    for call in (lambda: t.find_survival_over_time(time="days", event="died"),
                 lambda: t.compare_survival(time="days", event="died", for_each_group_in="treatment"),
                 lambda: t.explain_survival(time="days", event="died", using="age"),
                 lambda: t.find_survival_over_time(time="days", event="died", value="yes"),
                 lambda: t.find_risk_over_time(time="days", event="died", value="yes"),
                 lambda: sdata.chart(data).draw_survival_curves(time="days", event="died")):
        with pytest.raises(SimplydataError, match="find_risk_over_time"):
            call()
    with pytest.raises(SimplydataError, match="3 kinds"):
        sdata.table(trial.assign(died=[0, 1, 2] * 40)).find_survival_over_time(time="days", event="died")


def test_value_names_the_event_in_a_two_valued_column(trial, capsys):
    data = trial.assign(died=np.where(trial["died"] == "yes", "dead", "alive"))
    base = frame(sdata.table(trial).find_survival_over_time(time="days", event="died"))
    got = frame(sdata.table(data).find_survival_over_time(time="days", event="died", value="dead"))
    assert got["survival"].tolist() == pytest.approx(base["survival"].tolist())
    with pytest.raises(SimplydataError, match="value='dead'"):
        sdata.table(data).find_survival_over_time(time="days", event="died")
    with pytest.raises(SimplydataError, match="is not in the event column"):
        sdata.table(data).find_survival_over_time(time="days", event="died", value="gone")


# ---------------------------------------------------------------- find_risk_over_time
def test_risk_with_one_kind_is_one_minus_kaplan_meier(trial, engine, capsys):
    risk = frame(make(trial, engine).find_risk_over_time(time="days", event="died", for_each_group_in="treatment"))
    surv = frame(make(trial, engine).find_survival_over_time(time="days", event="died", for_each_group_in="treatment"))
    assert risk["risk"].tolist() == pytest.approx((1 - surv["survival"]).tolist())
    assert risk["95 % CI low"].tolist() == pytest.approx((1 - surv["95 % CI high"]).tolist())
    assert "1 minus the Kaplan-Meier" in capsys.readouterr().out


def test_risk_with_competing_events_matches_r(mgus2, engine, capsys):
    out = frame(make(mgus2, engine).find_risk_over_time(time="etime", event="event", value="pcm",
                                                        competing_with="death", for_each_group_in="sex",
                                                        at_time_points=[120, 240]))
    f = out[(out["sex"] == "F") & (out["time"] == 120)].set_index("event")
    # summary(survfit(Surv(etime, factor(event, c("alive", "pcm", "death"))) ~ sex), times = c(120, 240))$pstate
    assert f.loc["pcm", "risk"] == pytest.approx(0.07388566, rel=1e-6)
    assert f.loc["death", "risk"] == pytest.approx(0.4804900, rel=1e-6)
    assert f.loc["pcm", "95 % CI low"] == pytest.approx(0.05552473, rel=1e-6)
    printed = capsys.readouterr().out
    assert '"alive": 409 rows' in printed  # every other value is counted aloud
    assert "the chance of" in printed and "would come out as" in printed and "too high" in printed


def test_competing_values_are_checked(mgus2):
    t = sdata.table(mgus2)
    with pytest.raises(SimplydataError, match="needs value="):
        t.find_risk_over_time(time="etime", event="event", competing_with="death")
    with pytest.raises(SimplydataError, match="is not in the event column"):
        t.find_risk_over_time(time="etime", event="event", value="pcm", competing_with="dead")
    with pytest.raises(SimplydataError, match="twice"):
        t.find_risk_over_time(time="etime", event="event", value="pcm", competing_with=["pcm"])


# ---------------------------------------------------------------- Gray's test, cause-specific, Fine-Gray
def test_grays_test_matches_cmprsk(mgus2, capsys):
    r = frame(sdata.table(mgus2).compare_survival(time="etime", event="event", value="pcm", competing_with="death",
                                                  for_each_group_in="sex")).iloc[0]
    assert r["test"] == "Gray's test"
    assert r["statistic"] == pytest.approx(1.194508, rel=1e-6)
    assert r["p-value"] == pytest.approx(0.274422157, rel=1e-6)
    assert "11.7" in capsys.readouterr().out  # the competing event's own test


def test_fine_gray_matches_crr_and_finegray(mgus2, capsys):
    from simplydata._r import r_call

    out = frame(sdata.table(mgus2).explain_survival(time="etime", event="event", value="pcm", competing_with="death",
                                                    using=["age", "sex"], test_method="fine-gray"))
    assert out["coefficient"].tolist() == pytest.approx([-0.01733815, -0.26003824], rel=1e-6)
    printed = capsys.readouterr().out
    assert "its size is not how many times higher" in printed and "subdistribution hazard ratio" in printed
    # the check engine: survival::finegray() + weighted coxph agrees to about 3 digits
    fg = r_call("d <- survival::mgus2; d$et <- ifelse(d$pstat == 1, d$ptime, d$futime); "
                "d$ev <- factor(ifelse(d$pstat == 1, 1, 2 * d$death), 0:2, c('censor', 'pcm', 'death')); "
                "w <- survival::finegray(survival::Surv(et, ev) ~ ., data = d, etype = 'pcm'); "
                "unname(coef(survival::coxph(survival::Surv(fgstart, fgstop, fgstatus) ~ age + sex, weights = fgwt, "
                "data = w)))")
    assert out["coefficient"].tolist() == pytest.approx(list(fg), abs=1e-3)


def test_cause_specific_is_a_cox_model_with_the_competing_event_censored(mgus2, capsys):
    t = sdata.table(mgus2)
    cs = frame(t.explain_survival(time="etime", event="event", value="pcm", competing_with="death",
                                  using=["age", "sex"], test_method="cause-specific"))
    plain = frame(sdata.table(mgus2.assign(pcm=(mgus2["event"] == "pcm").astype(int))).explain_survival(
        time="etime", event="pcm", using=["age", "sex"]))
    assert cs["coefficient"].tolist() == pytest.approx(plain["coefficient"].tolist(), rel=1e-12)
    assert "among those still free of both events" in capsys.readouterr().out


def test_model_choices_are_checked(trial, mgus2):
    t = sdata.table(trial)
    with pytest.raises(SimplydataError, match="needs value= and competing_with="):
        t.explain_survival(time="days", event="died", using="age", test_method="fine-gray")
    with pytest.raises(SimplydataError, match="cause-specific"):
        t.explain_survival(time="days", event="died", using="age", test_method="cause-specific")
    with pytest.raises(SimplydataError, match="parametric"):
        sdata.table(mgus2).explain_survival(time="etime", event="event", value="pcm", competing_with="death",
                                            using=["age"], test_method="fine-gray", distribution="weibull")


# ---------------------------------------------------------------- distribution=
def test_parametric_model_matches_survreg(trial, engine, capsys, needs_r):
    # survreg(Surv(days, ev) ~ treatment + age, data = d, dist = "lognormal")
    out = frame(make(trial, engine).explain_survival(time="days", event="died", using=["treatment", "age"],
                                                     distribution="log-normal"))
    assert out["coefficient"].tolist() == pytest.approx([-0.395884553361934, -0.0367169830621584], rel=1e-6)
    assert out["time ratio"][0] == pytest.approx(math.exp(-0.395884553361934), rel=1e-6)
    printed = capsys.readouterr().out
    assert "times as long" in printed and "AIC" in printed
    with pytest.raises(SimplydataError, match="times above 0"):
        sdata.table(trial.assign(days=trial["days"].where(trial.index > 0, 0))).explain_survival(
            time="days", event="died", using="age", distribution="weibull")


# ---------------------------------------------------------------- adjusted curves
def test_adjusted_curves_are_adjustedcurves_direct(trial, needs_r, capsys):
    from simplydata._r import r_call

    out = frame(sdata.table(trial).find_survival_over_time(time="days", event="died", for_each_group_in="treatment",
                                                           allowing_for=["age"], at_time_points=[365, 730]))
    want = r_call("d <- data.frame(time = days, event = as.numeric(died == 'yes'), group = factor(g), age = age); "
                  "m <- survival::coxph(survival::Surv(time, event) ~ group + age, data = d, x = TRUE); "
                  "a <- adjustedCurves::adjustedsurv(data = d, variable = 'group', ev_time = 'time', event = 'event', "
                  "method = 'direct', outcome_model = m, conf_int = TRUE, times = c(365, 730)); a$adj$surv",
                  days=trial["days"].to_numpy(float), died=trial["died"].to_numpy(object),
                  g=trial["treatment"].to_numpy(object), age=trial["age"].to_numpy(float))
    assert out["survival"].tolist() == pytest.approx(list(want), rel=1e-9)
    assert "not the curves of an \"average\" row" in capsys.readouterr().out
    with pytest.raises(SimplydataError, match="needs for_each_group_in="):
        sdata.table(trial).find_survival_over_time(time="days", event="died", allowing_for=["age"])


def test_adjusted_chart_and_its_refusals(trial, needs_r):
    chart = sdata.chart(trial).draw_survival_curves(time="days", event="died", colour="treatment",
                                                    allowing_for=["age"])
    lines = [ln for ln in chart._render().axes[0].lines if ln.get_drawstyle().startswith("steps")]
    assert len(lines) == 2
    with pytest.raises(SimplydataError, match="number at risk"):
        sdata.chart(trial).draw_survival_curves(time="days", event="died", colour="treatment", allowing_for="age",
                                                with_at_risk_table=True)
    with pytest.raises(SimplydataError, match="needs colour="):
        sdata.chart(trial).draw_survival_curves(time="days", event="died", allowing_for="age")


def test_delayed_entry_chart_draws_the_table_numbers(trial):
    d = with_entry(trial)
    chart = sdata.chart(d).draw_survival_curves(time="days", event="died", followed_from="entry",
                                                with_at_risk_table=True)
    line = [ln for ln in chart._render().axes[0].lines if ln.get_drawstyle().startswith("steps")][0]
    table = frame(sdata.table(d).find_survival_over_time(time="days", event="died", followed_from="entry"))
    assert line.get_ydata()[1:-1].tolist() == pytest.approx(table["survival"].tolist())


# ---------------------------------------------------------------- draw_risk_curves
def test_risk_curves_rise_as_one_minus_kaplan_meier(trial):
    chart = sdata.chart(trial).draw_risk_curves(time="days", event="died", colour="treatment",
                                                with_confidence_band=True)
    ax = chart._render().axes[0]
    lines = [ln for ln in ax.lines if ln.get_drawstyle().startswith("steps")]
    table = frame(sdata.table(trial).find_risk_over_time(time="days", event="died", for_each_group_in="treatment"))
    new = table[table["treatment"] == "new medicine"]["risk"].tolist()
    assert lines[0].get_ydata()[1:-1].tolist() == pytest.approx(new)
    assert ax.get_ylabel().startswith("Risk")


def test_risk_curves_with_competing_events(mgus2):
    chart = sdata.chart(mgus2).draw_risk_curves(time="etime", event="event", value="pcm", competing_with="death",
                                                colour="sex")
    lines = [ln for ln in chart._render().axes[0].lines if ln.get_drawstyle().startswith("steps")]
    table = frame(sdata.table(mgus2).find_risk_over_time(time="etime", event="event", value="pcm",
                                                         competing_with="death", for_each_group_in="sex"))
    f = table[(table["sex"] == "F") & (table["event"] == "pcm")]["risk"].tolist()
    assert lines[0].get_ydata()[1:len(f) + 1].tolist() == pytest.approx(f)
    with pytest.raises(SimplydataError, match="competing_with="):
        sdata.chart(mgus2).draw_risk_curves(time="etime", event="event", value="pcm")


# ---------------------------------------------------------------- add_time_and_event_columns
ADMISSIONS = pd.DataFrame({
    "admitted": pd.to_datetime(["2024-01-01", "2024-01-05", "2024-02-01", "2024-03-01", "2024-03-10", "2024-12-20"]),
    "discharged": pd.to_datetime(["2024-01-10", None, "2024-02-03", "2024-03-01", "2024-03-20", None]),
    "first_esbl": pd.to_datetime([None, "2024-01-09", "2024-02-03", None, "2024-03-05", "2025-02-01"]),
})


def test_time_and_event_columns(engine, capsys):
    t = make(ADMISSIONS, engine)
    t.add_time_and_event_columns(from_date="admitted", to_date="discharged", event_date="first_esbl",
                                 until="2024-12-31")
    out = frame(t)
    # follow-up to the first of first_esbl, discharged, 2024-12-31; the event on the same day as discharge counts
    assert out["time"].tolist()[:4] == [9, 4, 2, 0]
    assert out["event"].tolist()[:4] == [0, 1, 1, 0]
    assert pd.isna(out["time"][4]) and pd.isna(out["event"][4])  # ESBL before admission: a prevalent case
    assert out["time"][5] == 11 and out["event"][5] == 0  # still followed at until=
    printed = capsys.readouterr().out
    assert "prevalent" in printed and "Person-time in all: 26 days" in printed and "add 1 day" in printed


def test_units_count_365_25_days_to_a_year(capsys):
    t = sdata.table(ADMISSIONS.iloc[:2])
    t.add_time_and_event_columns(from_date="admitted", event_date="first_esbl", until="2024-12-31", unit="year",
                                 time="years", event="esbl")
    out = frame(t)
    assert out["years"].tolist() == pytest.approx([365 / 365.25, 4 / 365.25])
    assert "365.25 days" in capsys.readouterr().out


def test_competing_dates_name_the_first_event(capsys):
    t = sdata.table(ADMISSIONS.iloc[:4])
    t.add_time_and_event_columns(from_date="admitted", event_date="first_esbl", competing_with=["discharged"],
                                 until="2024-12-31")
    assert frame(t)["event"].tolist() == ["discharged", "first_esbl", "first_esbl", "discharged"]
    assert 'competing_with=["discharged"]' in capsys.readouterr().out


def test_time_and_event_errors():
    t = sdata.table(ADMISSIONS)
    with pytest.raises(SimplydataError, match="turn_into_dates"):
        sdata.table(ADMISSIONS.assign(admitted="x")).add_time_and_event_columns(from_date="admitted",
                                                                                until="2024-12-31")
    with pytest.raises(SimplydataError, match="end of follow-up"):
        t.add_time_and_event_columns(from_date="admitted")
    with pytest.raises(SimplydataError, match="no end of follow-up"):
        t.add_time_and_event_columns(from_date="admitted", to_date="discharged")
    with pytest.raises(SimplydataError, match="before"):
        sdata.table(ADMISSIONS.assign(discharged=pd.to_datetime("2023-01-01"))).add_time_and_event_columns(
            from_date="admitted", to_date="discharged")
    with pytest.raises(SimplydataError, match="already has a column"):
        sdata.table(ADMISSIONS.assign(time=1)).add_time_and_event_columns(from_date="admitted", until="2024-12-31")
    with pytest.raises(SimplydataError, match="does not know"):
        t.add_time_and_event_columns(from_date="admitted", until="2024-12-31", unit="hours")
    with pytest.raises(SimplydataError, match="should be a date"):
        t.add_time_and_event_columns(from_date="admitted", until="soon")


def test_new_columns_go_straight_into_rate_of_and_the_survival_words(capsys):
    t = sdata.table(ADMISSIONS)
    t.add_time_and_event_columns(from_date="admitted", to_date="discharged", event_date="first_esbl",
                                 until="2024-12-31")
    t.rate_of("event", time="time")
    t.find_survival_over_time(time="time", event="event")
    assert "Note: 1 row with an empty cell" in capsys.readouterr().out


# ---------------------------------------------------------------- review fixes
def test_stratified_log_rank_with_start_times_is_refused_not_crashed(trial):
    d = with_entry(trial).assign(older=np.where(trial["age"] > 60, "over 60", "60 or under"))
    with pytest.raises(SimplydataError, match="not both"):
        sdata.table(d).compare_survival(time="days", event="died", for_each_group_in="treatment",
                                        allowing_for="older", followed_from="entry")


def test_no_end_date_may_come_before_the_start():
    early = ADMISSIONS.assign(died=pd.to_datetime("2023-06-01"))
    with pytest.raises(SimplydataError, match="before"):
        sdata.table(early).add_time_and_event_columns(from_date="admitted", event_date="first_esbl",
                                                      competing_with="died", until="2024-12-31")
    with pytest.raises(SimplydataError, match='until="2024-03-01" is before'):
        sdata.table(ADMISSIONS).add_time_and_event_columns(from_date="admitted", event_date="first_esbl",
                                                           until="2024-03-01")
    with pytest.raises(SimplydataError, match="needs event_date="):
        sdata.table(ADMISSIONS).add_time_and_event_columns(from_date="admitted", competing_with="discharged",
                                                           until="2024-12-31")


def test_fine_gray_p_values_are_not_rounded(mgus2):
    from simplydata._r import r_call

    out = frame(sdata.table(mgus2).explain_survival(time="etime", event="event", value="pcm", competing_with="death",
                                                    using=["age", "sex"], test_method="fine-gray"))
    want = r_call("2 * pnorm(-abs(c(-0.01733815, -0.26003824) / c(0.005737103, 0.185681035)))")
    assert out["p-value"].tolist() == pytest.approx(list(want), rel=1e-5)


def test_a_group_without_events_is_named_with_competing_events(mgus2, capsys):
    data = pd.concat([mgus2, pd.DataFrame({"etime": [10.0, 20.0, 30.0], "event": ["alive"] * 3, "age": [60.0] * 3,
                                           "sex": ["X"] * 3})], ignore_index=True)
    sdata.table(data).find_risk_over_time(time="etime", event="event", value="pcm", competing_with="death",
                                          for_each_group_in="sex")
    assert "X, no events of any kind" in capsys.readouterr().out


def test_adjusted_times_after_the_last_follow_up_are_left_out(trial, needs_r, capsys):
    out = frame(sdata.table(trial).find_survival_over_time(time="days", event="died", for_each_group_in="treatment",
                                                           allowing_for=["age"], at_time_points=[365, 5000]))
    assert set(out["time"]) == {365.0}
    assert "left out" in capsys.readouterr().out


def test_time_points_can_be_a_column(trial):
    out = frame(sdata.table(trial).find_survival_over_time(time="days", event="died",
                                                           at_time_points=pd.Series([365, 730])))
    assert out["time"].tolist() == [365.0, 730.0]


def test_split_rows_get_the_delayed_entry_note(capsys):
    data = pd.DataFrame({"start": [0, 40, 0, 0], "stop": [40, 90, 60, 80], "e": [0, 1, 1, 0]})
    sdata.table(data).find_survival_over_time(time="stop", event="e", followed_from="start")
    assert "split into rows" in capsys.readouterr().out
