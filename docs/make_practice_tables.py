"""Make seven practice tables of simplydata (src/simplydata/data/): MADE-UP data with built-in effects.

Earlier versions shipped real data in these tables: copies of data in GPL R packages (bcg and passive_smoking from
metadat, ability_tests from lavaan, sea_levels from ismev, sampled_schools from survey, job_training from MatchIt)
and the Schütz et al. (2014) supplement (drug_levels, (c) AAPS with no open licence). The owner decided on
2026-11-22 to ship none of them. Each table below keeps the columns and the number of rows of the table it replaces,
so the lessons and examples ask the same questions, but every value is drawn here from a fixed seed, with effects
built in that a reader can recover. The real data are still used to test simplydata: the tests and the reliability
study read them from the installed R packages (validation/r_data.py), and the Schütz data from a file the user names
(DATA_LICENSES.md).

Run once from the repository root: python docs/make_practice_tables.py. It writes the same files on every computer.
The made-up job_search table has its own script, docs/make_job_search.py.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

OUT = Path(__file__).resolve().parents[1] / "src" / "simplydata" / "data"


def bcg(seed=20261122):
    """13 made-up vaccine trials. Built in: the log risk ratio is 0.6 - 0.035 x latitude (the vaccine protects
    more far from the equator), plus a between-trial spread with standard deviation 0.15."""
    rng = np.random.default_rng(seed)
    k = 13
    year = np.sort(rng.integers(1935, 1981, k))
    latitude = rng.integers(13, 56, k)
    allocation = rng.choice(["random", "alternate", "systematic"], k, p=[0.55, 0.2, 0.25])
    vaccinated = rng.integers(120, 20000, k)
    unvaccinated = (vaccinated * rng.uniform(0.8, 1.3, k)).astype(int)
    base = rng.uniform(0.002, 0.04, k)
    log_rr = 0.6 - 0.035 * latitude + rng.normal(0, 0.15, k)
    tb_unvaccinated = rng.binomial(unvaccinated, base)
    tb_vaccinated = rng.binomial(vaccinated, np.clip(base * np.exp(log_rr), 0, 1))
    names = [f"Trial {chr(65 + i)} {y}" for i, y in enumerate(year)]
    return pd.DataFrame({"trial": names, "year": year, "tb_vaccinated": tb_vaccinated, "vaccinated": vaccinated,
                         "tb_unvaccinated": tb_unvaccinated, "unvaccinated": unvaccinated, "latitude": latitude,
                         "allocation": allocation})


def passive_smoking(seed=20261123):
    """37 made-up studies of lung cancer in non-smoking women married to smokers. Built in: a common odds ratio
    of 1.25 (log 0.22) with a between-study spread of 0.15; smaller studies have wider intervals."""
    rng = np.random.default_rng(seed)
    k = 37
    year = np.sort(rng.integers(1981, 1998, k))
    country = rng.choice(["USA", "Japan", "China", "Europe", "Hong Kong"], k, p=[0.4, 0.15, 0.2, 0.15, 0.1])
    design = rng.choice(["case-control", "cohort"], k, p=[0.85, 0.15])
    cases = rng.integers(20, 650, k)
    se = 4.0 / np.sqrt(cases)
    log_or = 0.22 + rng.normal(0, 0.15, k) + rng.normal(0, se)
    odds, low, high = np.exp(log_or), np.exp(log_or - 1.96 * se), np.exp(log_or + 1.96 * se)
    return pd.DataFrame({"study": [f"Study {i + 1} {y}" for i, y in enumerate(year)], "year": year,
                         "country": country, "design": design, "cases": cases, "odds ratio": odds.round(2),
                         "odds ratio 95 % CI low": low.round(2), "odds ratio 95 % CI high": high.round(2)})


def ability_tests(seed=20261124):
    """301 made-up pupils, nine test scores. Built in: three factors, visual (x1 to x3), verbal (x4 to x6) and
    speed (x7 to x9), with loadings 0.75, 0.6 and 0.55 and factor correlations 0.45 (visual-verbal), 0.30
    (visual-speed) and 0.25 (verbal-speed); x9 also loads 0.3 on visual."""
    rng = np.random.default_rng(seed)
    n = 301
    corr = np.array([[1, 0.45, 0.30], [0.45, 1, 0.25], [0.30, 0.25, 1]])
    f = rng.multivariate_normal(np.zeros(3), corr, n)
    load = np.zeros((9, 3))
    load[0:3, 0] = [0.75, 0.6, 0.55]
    load[3:6, 1] = [0.85, 0.8, 0.8]
    load[6:9, 2] = [0.7, 0.75, 0.55]
    load[8, 0] = 0.3
    unique = np.sqrt(np.clip(1 - (load @ corr * load).sum(1), 0.1, None))
    z = f @ load.T + rng.normal(0, 1, (n, 9)) * unique
    means = np.array([4.9, 6.1, 2.2, 3.1, 4.3, 2.2, 4.2, 5.5, 5.4])
    sds = np.array([1.2, 1.2, 1.1, 1.2, 1.3, 1.1, 1.1, 1.0, 1.0])
    scores = (means + z * sds).round(4)
    school = np.where(np.arange(n) < 156, "Hillside", "Riverside")
    grade = rng.choice([7.0, 8.0], n)
    grade[rng.integers(0, n)] = np.nan  # one empty grade, so the table has an empty cell to practise with
    out = pd.DataFrame({"id": np.arange(1, n + 1), "sex": rng.integers(1, 3, n), "ageyr": rng.integers(11, 17, n),
                        "agemo": rng.integers(0, 12, n), "school": school, "grade": grade})
    for j in range(9):
        out[f"x{j + 1}"] = scores[:, j]
    return out


def sea_levels(seed=20261125):
    """65 made-up yearly highest sea levels (m), 1923 to 1987. Built in: a GEV curve with location 3.87, scale 0.20
    and shape -0.05 (a short upper tail), so the 100-year level is about 4.67 m."""
    rng = np.random.default_rng(seed)
    levels = stats.genextreme(c=0.05, loc=3.87, scale=0.20).rvs(65, random_state=rng)
    return pd.DataFrame({"year": np.arange(1923, 1988), "sea_level": levels.round(2)})


def sampled_schools(seed=20261126):
    """200 made-up schools sampled within school type (100 elementary of 4400, 50 middle of 1000, 50 high of 750).
    Built in: the score of 2000 falls by 3 points for each percent of pupils with free meals; a school met its
    target when its score rose by 20 points or more since 1999; awards went to most of those."""
    rng = np.random.default_rng(seed)
    kinds = [("elementary", 100, 4400, 0), ("middle", 50, 1000, -20), ("high", 50, 750, -40)]
    rows = []
    number = 0
    for kind, n, population, shift in kinds:
        for _ in range(n):
            number += 1
            meals = int(np.clip(rng.normal(45, 28), 0, 100))
            ell = int(np.clip(meals * 0.5 + rng.normal(0, 12), 0, 100))
            score = int(np.clip(830 + shift - 3 * meals + rng.normal(0, 45), 350, 990))
            growth = int(rng.normal(30, 25))
            met = growth >= 20
            rows.append({"school": f"School {number:03d}", "district": f"District {rng.integers(1, 41)}",
                         "school_type": kind, "score_2000": score, "score_1999": score - growth,
                         "free_meals": meals, "english_learners": ell,
                         "pupils": int(np.clip(rng.lognormal(6.4 if kind == "elementary" else 7.0, 0.5), 50, 4000)),
                         "met_target": "yes" if met else "no",
                         "award": "yes" if met and rng.random() < 0.85 else "no",
                         "weight": population / n, "schools_of_type": population})
    return pd.DataFrame(rows)


def job_training(seed=20261127):
    """614 made-up men: 185 took a job training, 429 come from a comparison survey. Built in: the training adds
    1,800 dollars to the 1978 earnings, but the trained men were younger, had less schooling, were more often black
    and unmarried, and earned less before (1974, 1975), so a plain comparison of 1978 earnings is misleading."""
    rng = np.random.default_rng(seed)
    n = 614
    age = rng.normal(28, 9, n).clip(16, 55).round().astype(int)
    educ = rng.normal(10.6, 2.5, n).clip(3, 18).round().astype(int)
    race = rng.choice(["black", "hispan", "white"], n, p=[0.40, 0.11, 0.49])
    married = (rng.random(n) < 0.42).astype(int)
    nodegree = (educ < 12).astype(int)
    re74 = np.where(rng.random(n) < 0.62, rng.lognormal(8.7, 0.8, n), 0.0)
    re75 = np.where(rng.random(n) < 0.65, 0.6 * re74 + rng.lognormal(7.8, 0.9, n), 0.0)
    # who took the training: younger, less schooled, black, unmarried men with low earnings before
    score = (1.0 - 0.06 * (age - 28) - 0.15 * (educ - 10.6) + 1.6 * (race == "black") - 0.8 * married
             - 0.00025 * re74 - 0.0001 * re75)
    chance = np.exp(score) / np.exp(score).sum()
    trained = rng.choice(n, 185, replace=False, p=chance)
    treat = np.zeros(n, int)
    treat[trained] = 1
    order = np.r_[np.flatnonzero(treat == 1), np.flatnonzero(treat == 0)]  # the trained men first, as before
    re78 = np.clip(2000 + 0.7 * re74 + 0.4 * re75 + 250 * (educ - 10) + 40 * (age - 28) + 1800 * treat
                   + rng.normal(0, 3500, n), 0, None)
    out = pd.DataFrame({"treat": treat, "age": age, "educ": educ, "race": race, "married": married,
                        "nodegree": nodegree, "re74": re74.round(3), "re75": re75.round(3), "re78": re78.round(3)})
    return out.iloc[order].reset_index(drop=True)


def drug_levels(seed=20261128):
    """A made-up 2 x 2 crossover bioequivalence study of 18 subjects (the same sequences as before). Built in: the
    test formulation gives 96 % of the reference's AUC, with a within-subject CV of 12 % and a small period effect,
    so the 90 % interval of the ratio lies inside 80 to 125 %."""
    rng = np.random.default_rng(seed)
    first_test = {3, 5, 6, 8, 11, 13, 14, 15, 18}
    sigma_w = np.sqrt(np.log(1 + 0.12 ** 2))
    rows = []
    for subject in range(1, 19):
        level = rng.normal(np.log(200), 0.35)
        for period in (1, 2):
            test = (period == 1) == (subject in first_test)
            log_auc = level + (np.log(0.96) if test else 0) + (0.02 if period == 2 else 0) + rng.normal(0, sigma_w)
            rows.append({"subject": subject, "period": period, "formulation": "test" if test else "reference",
                         "auc": round(float(np.exp(log_auc)), 2)})
    return pd.DataFrame(rows)


TABLES = {"bcg": bcg, "passive_smoking": passive_smoking, "ability_tests": ability_tests, "sea_levels": sea_levels,
          "sampled_schools": sampled_schools, "job_training": job_training, "drug_levels": drug_levels}


if __name__ == "__main__":
    for name, make in TABLES.items():
        make().to_csv(OUT / f"{name}.csv", index=False, lineterminator="\n")
        print(f"wrote {OUT / name}.csv")
