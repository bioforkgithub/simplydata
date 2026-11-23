"""Make the practice table job_search (src/simplydata/data/job_search.csv): MADE-UP data for mediation.

The table has the columns of the JOBS II study as the R package mediation ships it (jobs), so the lessons can ask the
same question, but every value is drawn here from a fixed random seed. The real JOBS II records (ICPSR study 2739)
are not ours to redistribute; the reliability study reads them from the installed R package mediation instead
(validation/cases_causal.py).

The effects built in, which a reader can recover with explain("depress2", using="treat", through="job_seek",
allowing_for=["econ_hard", "sex", "age"]):
  * the workshop (treat = 1, offered to about two in three at random) raises job-search confidence (job_seek) by
    0.30 points;
  * each point of confidence lowers depression six months later (depress2) by 0.30 points;
  * the workshop also lowers depression by 0.04 points directly.
So the indirect effect is about 0.30 x -0.30 = -0.09 and the total effect about -0.13 (a little less after the
scores are kept between 1 and 5 and rounded as questionnaire scores are).

Run once from the repository root: python docs/make_job_search.py. It writes the same file on every computer.
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20261121
N = 899
OUT = Path(__file__).resolve().parents[1] / "src" / "simplydata" / "data" / "job_search.csv"


def make() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    treat = (rng.random(N) < 2 / 3).astype(int)
    sex = (rng.random(N) < 0.54).astype(int)
    age = np.clip(rng.normal(37.5, 10.5, N), 18, 70).round(1)
    # questionnaire scores: averages of a few items from 1 to 5, so they come in steps
    econ_hard = np.clip(np.round(rng.normal(3.0, 1.0, N) * 3) / 3, 1, 5).round(2)
    depress1 = np.clip(rng.normal(1.85, 0.55, N), 1, 3).round(2)
    nonwhite = np.where(rng.random(N) < 0.17, "non.white1", "white0")
    educ = rng.choice(["lt-hs", "highsc", "somcol", "bach", "gradwk"], N, p=[0.06, 0.30, 0.35, 0.16, 0.13])
    income = rng.choice(["lt15k", "15t24k", "25t39k", "40t49k", "50k+"], N, p=[0.18, 0.23, 0.24, 0.12, 0.23])
    seek = 3.70 + 0.30 * treat - 0.10 * (econ_hard - 3) + 0.05 * sex + rng.normal(0, 0.65, N)
    job_seek = np.clip(np.round(seek * 6) / 6, 1, 5).round(2)
    mood = (0.95 + 0.45 * depress1 + 0.08 * econ_hard - 0.04 * treat - 0.30 * (job_seek - 3.7)
            + rng.normal(0, 0.50, N))
    depress2 = np.clip(mood, 1, 5).round(2)
    employed = rng.random(N) < 1 / (1 + np.exp(-(-0.80 + 0.50 * (job_seek - 3.7) + 0.10 * treat)))
    work1 = np.where(employed, "psyemp", "psyump")
    return pd.DataFrame({"treat": treat, "econ_hard": econ_hard, "depress1": depress1, "sex": sex, "age": age,
                         "nonwhite": nonwhite, "educ": educ, "income": income, "job_seek": job_seek,
                         "depress2": depress2, "work1": work1})


if __name__ == "__main__":
    make().to_csv(OUT, index=False, lineterminator="\n")
    print(f"wrote {OUT}")
