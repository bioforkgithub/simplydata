"""Small tables to practise with: sdata.get_example("marks").

Every number in these tables is invented: they are not real people, places, studies or countries. Seven of them
copy the columns of a real study so that the lessons can ask a real question ("bcg" and "passive_smoking" for
combining studies, "ability_tests" for hidden factors, "sea_levels" for extremes, "sampled_schools" for surveys,
"job_training", "job_search" and "drug_levels" for cause and effect and bioequivalence), but their values were drawn
with a fixed seed by docs/make_practice_tables.py and docs/make_job_search.py, with effects built in that the lessons
recover. simplydata was tested on the real data of those studies, which it does not ship (DATA_LICENSES.md at the top
of the repository).
"""

from __future__ import annotations

from importlib.resources import files

import pandas as pd

from .._errors import SimplydataError, suggest

# name -> (what it is, what each column means)
# Columns read as dates (the files keep them as year-month-day text).
DATE_COLUMNS = {"shop": ["date"], "visitors": ["month"], "river": ["date"],
                "admissions": ["admitted", "discharged", "first_esbl"]}
EXAMPLES = {
    "marks": (
        "Test marks of 18 made-up children in three classes.",
        {
            "name": "the child's first name",
            "class": "A, B or C",
            "subject": "Maths, Science or English",
            "hours": "hours spent studying for the test",
            "marks": "marks in the test, out of 100",
            "height": "the child's height in cm",
        },
    ),
    "weather": (
        "Weather in three made-up cities, month by month.",
        {
            "month": "Jan, Feb ... Dec",
            "month_number": "1 to 12",
            "city": "Sunnyvale, Rainbridge or Frostby",
            "temperature": "average temperature in °C",
            "rain": "rain that month in mm",
            "wind_direction": "where the wind mostly came from, in degrees (0 to 360)",
            "wind_speed": "average wind speed in km/h",
        },
    ),
    "fruit": (
        "Fruit sold by two made-up shops in one week. One row is one sale.",
        {
            "day": "Mon to Fri",
            "shop": "Corner shop or Market stall",
            "fruit": "apple, banana, cherry, grape, orange or pear",
            "count": "how many pieces of fruit were sold",
            "price": "price of one piece (made-up money)",
        },
    ),
    "growth": (
        "Population of four made-up countries, every two years from 2000 to 2024.",
        {
            "year": "2000, 2002 ... 2024",
            "country": "Applia, Bananaland, Cherria or Dateland",
            "population": "people, in millions",
            "forest": "how much of the land is forest, in %",
        },
    ),
    "sensor": (
        "Five seconds of a made-up sensor, 200 readings per second: cycles, a hum, a drift, noise and spikes.",
        {
            "time": "seconds from 0 to 4.995, one reading every 0.005 s",
            "signal": "the reading: a 5-per-second and a 20-per-second cycle, a 50-per-second hum, a slow drift, "
                      "noise and three spikes",
            "vibration": "a second sensor: the signal 0.03 s later at half size, plus its own noise",
        },
    ),
    "visitors": (
        "Monthly visitors to two made-up museums, 2014 to 2025: a rising trend, a yearly season and noise.",
        {
            "month": "the first day of each month from 2014-01-01 to 2025-12-01 (real dates)",
            "museum": "Harbour Museum or Hill Gallery",
            "visitors": "people who came that month",
        },
    ),
    "river": (
        "Daily water level and nitrate at two made-up river stations, 2024 to 2025. Some days and cells are missing.",
        {
            "date": "a day from 2024-01-01 to 2025-12-31 (real dates); 15 days have no row",
            "station": "Station A or Station B",
            "level": "water level in m: high in winter, low in summer; a few cells are empty",
            "nitrate": "nitrate in mg/L, rising slowly; at Station B it drops from 2025-04-01 (a new treatment works)",
        },
    ),
    "shop": (
        "Daily sales of two made-up shops from January to March 2026. Some cells are empty.",
        {
            "date": "every day from 2026-01-01 to 2026-03-31 (real dates)",
            "shop": "Northgate or Southside",
            "sales": "money taken that day (made-up money); empty on days the till broke",
            "customers": "how many people bought something; empty on days nobody counted",
        },
    ),
    "school": (
        "Made-up pupils in 12 schools, three classes in each: study, sleep and test marks. Some sleep cells are empty.",
        {
            "school": "School A to School L (15 pupils in each)",
            "pupil": "P001 to P180",
            "class": "red, blue or green: the pupil's class inside the school (5 pupils in each)",
            "hours": "hours spent studying for the test",
            "sleep": "hours of sleep the night before; empty when the pupil did not say",
            "breakfast": "yes or no: did the pupil eat breakfast that morning",
            "marks": "marks in the test, out of 100",
            "passed": "yes (50 marks or more) or no",
            "days_absent": "days the pupil missed school that term",
        },
    ),
    "meadow": (
        "Plants counted in 30 made-up plots of three fields, half of them grazed by sheep.",
        {
            "plot": "a short name for the plot, such as NG1",
            "field": "North field, South field or River field",
            "grazed": "yes or no: do sheep graze the plot",
            "clover": "how many clover plants in the plot",
            "daisy": "how many daisies",
            "buttercup": "how many buttercups",
            "dandelion": "how many dandelions",
            "nettle": "how many nettles",
            "thistle": "how many thistles",
            "moss": "how many patches of moss",
            "fern": "how many ferns",
            "orchid": "how many orchids",
            "yarrow": "how many yarrow plants",
        },
    ),
    "trial": (
        "120 made-up patients in a trial of a new medicine, followed for up to 3 years.",
        {
            "patient": "T001 to T120",
            "treatment": "new medicine or usual care",
            "age": "age in years when the patient joined",
            "days": "days from joining until the patient died or the follow-up ended",
            "died": "yes (died on that day) or no (still alive when the follow-up ended)",
        },
    ),
    "clinic": (
        "200 made-up patients in two hospital wards: tests for an infection, ratings, devices and pain.",
        {
            "patient": "C001 to C200",
            "ward": "ward A or ward B",
            "age_group": "under 50, 50 to 69, or 70 or over",
            "infected": "yes or no: did the patient have the infection (the truth, from a slow lab test)",
            "rapid_test": "positive or negative: the result of a quick test for the infection",
            "crp": "C-reactive protein in the blood (mg/dL); higher with infection",
            "procalcitonin": "procalcitonin in the blood (ng/mL); also higher with infection",
            "nurse_rating": "how ill the patient looked to a nurse: mild, moderate or severe",
            "doctor_rating": "how ill the patient looked to a doctor: mild, moderate or severe",
            "device_a": "blood pressure (mmHg) measured with device A",
            "device_b": "blood pressure (mmHg) measured with device B, at the same time",
            "pain_week_0": "pain score from 0 (none) to 10 at the start",
            "pain_week_4": "pain score 4 weeks later",
            "pain_week_8": "pain score 8 weeks later",
            "in_pain_before": "yes or no: in pain before a treatment",
            "in_pain_after": "yes or no: in pain after it",
            "infections": "infections caught in hospital",
            "caught_infection": "yes or no: did the patient catch an infection in hospital (infections above 0)",
            "patient_days": "days the patient was in hospital",
            "item_1": "answer from 1 (not at all) to 5 (very) to the first of five questions (items) on how "
                      "satisfied the patient was with the care",
            "item_2": "answer to the second question (1 to 5)",
            "item_3": "answer to the third question (1 to 5)",
            "item_4": "answer to the fourth question (1 to 5)",
            "item_5": "answer to the fifth question (1 to 5)",
        },
    ),
    "island": (
        "A map of a made-up island with two hills, on a 15 x 15 grid.",
        {
            "east": "how far east, 0 to 14 (km)",
            "north": "how far north, 0 to 14 (km)",
            "height": "height of the ground in m (below 0 is under the sea)",
        },
    ),
    # S3a-2 (lines and curves): a dose-response test and growth curves
    "toxicity": (
        "A made-up toxicity test: seedlings grown at eight concentrations of two chemicals, three dishes each.",
        {
            "chemical": "A or B",
            "concentration": "0, 0.5, 1, 2, 4, 8, 16 or 32 (mg per litre)",
            "dish": "1, 2 or 3",
            "root_length": "average root length of the seedlings in the dish, in mm",
            "seedlings": "seedlings in the dish (20)",
            "dead": "how many of them died",
        },
    ),
    "culture": (
        "Bacteria growing in three made-up flasks, measured every hour for a day.",
        {
            "flask": "A, B or C",
            "hour": "0 to 24",
            "density": "how cloudy the culture is (optical density at 600 nm)",
        },
    ),
    # S3b-3 (survival and person-time): dates to turn into time and event columns
    "admissions": (
        "300 made-up hospital admissions in 2024: when each patient came and left, and the first culture that grew "
        "ESBL-producing bacteria. Made up for practice, not real patients.",
        {
            "patient": "A001 to A300",
            "ward": "surgery or intensive care",
            "age": "age in years on admission",
            "admitted": "date of admission",
            "discharged": "date the patient left hospital, alive or dead",
            "died": "yes (died in hospital) or no",
            "first_esbl": "date of the first culture with ESBL-producing bacteria during the stay (empty if none)",
        },
    ),
    # S3c-1 (communities and resistomes): made up, labelled
    "resistome": (
        "MADE-UP DATA: antibiotic resistance genes counted in 24 made-up samples from a hospital effluent, a "
        "treatment plant, a harbour and a fjord sediment (6 each): the reads that matched each gene. Invented for "
        "practice; the numbers are not from any real study.",
        {
            "sample": "a short name for the sample, such as HE1 (hospital effluent 1)",
            "site": "hospital effluent, treatment plant, harbour or fjord sediment",
            "temperature": "water temperature in °C",
            "salinity": "salt in the water (practical salinity units; sea water is about 35)",
            "reads": "how many sequencing reads the sample got, in millions (its sequencing depth)",
            "blaTEM": "reads that matched TEM beta-lactamase genes",
            "blaCTXM": "reads that matched CTX-M extended-spectrum beta-lactamase genes",
            "blaOXA48": "reads that matched OXA-48 carbapenemase genes",
            "blaNDM": "reads that matched NDM carbapenemase genes",
            "sul1": "reads that matched sulfonamide resistance gene sul1",
            "sul2": "reads that matched sulfonamide resistance gene sul2",
            "tetA": "reads that matched tetracycline efflux gene tetA",
            "tetM": "reads that matched tetracycline ribosomal protection gene tetM",
            "qnrS": "reads that matched quinolone resistance gene qnrS",
            "ermB": "reads that matched macrolide resistance gene ermB",
            "aadA": "reads that matched aminoglycoside resistance gene aadA",
            "mphA": "reads that matched macrolide resistance gene mphA",
            "vanA": "reads that matched vancomycin resistance gene vanA",
            "mcr1": "reads that matched colistin resistance gene mcr-1",
        },
    ),
    # S3b-1 (combining studies): real, published study results (the only tables that are not made up)
    "bcg": (
        "MADE-UP DATA: 13 made-up trials of a vaccine against tuberculosis, one row per trial, with the columns "
        "of the BCG trials of Colditz et al. (1994). Built in: the vaccine lowers the risk more far from the "
        "equator (log risk ratio 0.6 - 0.035 x latitude, plus a between-trial spread). simplydata was tested on "
        "the real BCG trials (R metadat's dat.bcg); see DATA_LICENSES.md.",
        {
            "trial": "the trial's name and year",
            "year": "the year the trial was published",
            "tb_vaccinated": "vaccinated people who got tuberculosis",
            "vaccinated": "people vaccinated",
            "tb_unvaccinated": "unvaccinated people who got tuberculosis",
            "unvaccinated": "people not vaccinated",
            "latitude": "how far the trial's place is from the equator, in degrees",
            "allocation": "how people were put into the groups: random, alternate or systematic",
        },
    ),
    # S3c-3 (directions, places and extremes): stations and rain made up, sea_levels real (published)
    "stations": (
        "MADE-UP DATA: 60 made-up sampling stations in a fjord on a coast: where each one is, how deep, the direction "
        "its current mostly flows to and the zinc in its sediment. Invented for practice; not from any real survey.",
        {
            "station": "a short name for the station, S01 to S60",
            "east": "metres east of the south-west corner of the area (0 to 6000)",
            "north": "metres north of the south-west corner of the area (0 to 4000)",
            "lon": "longitude in degrees (made-up place near 5.2° E)",
            "lat": "latitude in degrees (made-up place near 60.4° N)",
            "depth": "water depth in m",
            "current_direction": "the direction the current mostly flows to, in degrees (0 = north, 90 = east); "
                                 "most point a little west or east of north, so they lie on both sides of 0 and 360",
            "zinc": "zinc in the sediment in mg/kg; higher near the old harbour and alike at nearby stations",
        },
    ),
    "rain": (
        "MADE-UP DATA: 10 years of daily rain at one made-up coastal station (2015 to 2024), with a few very wet "
        "days. Invented for practice; not from any real weather station.",
        {
            "date": "every day from 2015-01-01 to 2024-12-31 (real dates)",
            "rain": "rain that day in mm (0 on dry days)",
        },
    ),
    "sea_levels": (
        "MADE-UP DATA: the highest sea level of each year at a made-up coastal town, 1923 to 1987, like the Port "
        "Pirie series of Coles (2001). Built in: a GEV curve with location 3.87 m, scale 0.20 m and shape -0.05. "
        "simplydata was tested on the real Port Pirie data (R ismev's portpirie); see DATA_LICENSES.md.",
        {
            "year": "the year, 1923 to 1987",
            "sea_level": "the highest sea level reached that year, in metres",
        },
    ),
    "passive_smoking": (
        "MADE-UP DATA: 37 made-up studies of lung cancer in non-smoking women whose husbands smoked, one row per "
        "study, with the columns of Hackshaw, Law & Wald (1997). Built in: an odds ratio of about 1.25. "
        "simplydata was tested on the real studies (R metadat's dat.hackshaw1998); see DATA_LICENSES.md.",
        {
            "study": "the study's number and year",
            "year": "the year the study was published",
            "country": "where the study was done",
            "design": "cohort or case-control",
            "cases": "the number of women with lung cancer in the study",
            "odds ratio": "the odds of lung cancer with a smoking husband against a non-smoking husband",
            "odds ratio 95 % CI low": "the lower end of its 95 % confidence interval",
            "odds ratio 95 % CI high": "the upper end of its 95 % confidence interval",
        },
    ),
    # S3c-2 (hidden factors): real, published test scores
    "ability_tests": (
        "MADE-UP DATA: nine ability test scores of 301 made-up pupils of two schools, with the columns of "
        "Holzinger & Swineford (1939). Built in: three hidden factors, x1 to x3 visual, x4 to x6 verbal and x7 to "
        "x9 speed, which are correlated, and x9 also leans on the visual factor. simplydata was tested on the "
        "real scores (R lavaan's HolzingerSwineford1939); see DATA_LICENSES.md.",
        {
            "id": "the pupil's number",
            "sex": "1 or 2",
            "ageyr": "age, the years",
            "agemo": "age, the months on top of the years",
            "school": "Hillside or Riverside",
            "grade": "7 or 8 (one empty cell)",
            "x1": "visual perception",
            "x2": "cubes",
            "x3": "lozenges",
            "x4": "paragraph comprehension",
            "x5": "sentence completion",
            "x6": "word meaning",
            "x7": "speeded addition",
            "x8": "speeded counting of dots",
            "x9": "speeded discrimination of straight and curved capitals",
        },
    ),
    # S3c-4 (small additions): many p-values at once, for q-values and the local false discovery rate
    "many_tests": (
        "MADE-UP DATA: the results of testing 2000 made-up genes for a difference between two groups of samples, "
        "one row per gene; about 1 in 5 genes has a real difference. Invented for practice (for q-values and the "
        "local false discovery rate); not from any real study.",
        {
            "gene": "a made-up gene name, G0001 to G2000",
            "difference": "the difference between the two groups (on a log scale; 0 = no difference)",
            "p-value": "the p-value of the test of that gene",
        },
    ),
    # S3d-1 (planning and surveys): a real stratified survey sample, and made-up answers on a scale
    "sampled_schools": (
        "MADE-UP DATA: 200 made-up schools sampled at random within school type (100 elementary of 4400, 50 "
        "middle of 1000, 50 high of 750), with their weights, for survey-weighted answers "
        "(table.use_survey_design), with the columns of the California sample of R survey (apistrat). Built in: "
        "the 2000 score falls by 3 points for each percent of pupils with free meals. simplydata was tested on "
        "the real sample; see DATA_LICENSES.md.",
        {
            "school": "the school's name",
            "district": "the school district",
            "school_type": "elementary, middle or high: the strata of the sample",
            "score_2000": "the school's Academic Performance Index in 2000 (200 to 1000)",
            "score_1999": "the same index in 1999",
            "free_meals": "percent of pupils who get free or cheaper school meals",
            "english_learners": "percent of pupils still learning English",
            "pupils": "pupils enrolled",
            "met_target": "yes or no: did the school meet its growth target?",
            "award": "yes or no: did the school get an award?",
            "weight": "the sampling weight: how many schools of its type each sampled school stands for",
            "schools_of_type": "how many schools of this type there are (the population size of the stratum)",
        },
    ),
    "course_feedback": (
        "MADE-UP DATA: 120 made-up students rate a course on five statements, from strongly disagree to strongly "
        "agree (answers on a scale, Likert items). A few answers are empty. Invented for practice; not from any "
        "real study.",
        {
            "student": "a made-up student code, S001 to S120",
            "programme": "biology, chemistry or medicine",
            "teaching": "\"The teaching was clear\": strongly disagree, disagree, neutral, agree or strongly agree",
            "materials": "\"The materials helped me\" (same five answers)",
            "pace": "\"The pace was right\" (same five answers)",
            "workload": "\"The workload was fair\" (same five answers)",
            "would_recommend": "\"I would recommend the course\" (same five answers)",
        },
    ),
    # S3d-2 (epidemiology and cause and effect): two real studies, a real crossover, and made-up death counts
    "job_training": (
        "MADE-UP DATA: 614 made-up men, 185 who took a job training and 429 from a comparison survey, with the "
        "columns of the study of LaLonde (1986). The trained men differ from the others before the training "
        "(younger, less schooling, more often black and unmarried, lower earnings), so a plain comparison mixes "
        "the training with who took it. Built in: the training adds 1800 dollars to the 1978 earnings. simplydata "
        "was tested on the real data (R MatchIt's lalonde); see DATA_LICENSES.md.",
        {
            "treat": "1 = took part in the job training, 0 = from the comparison survey",
            "age": "age in years",
            "educ": "years of schooling",
            "race": "black, hispan or white",
            "married": "1 = married, 0 = not",
            "nodegree": "1 = no high-school degree, 0 = has one",
            "re74": "earnings in 1974 (US dollars)",
            "re75": "earnings in 1975 (US dollars)",
            "re78": "earnings in 1978, after the training (US dollars)",
        },
    ),
    "job_search": (
        "MADE-UP DATA: 899 made-up unemployed workers in a randomised job-search workshop, with the columns of the "
        "JOBS II study (Vinokur, Price & Schul 1995) as the R package mediation ships it (jobs), but every value "
        "drawn with a fixed seed (docs/make_job_search.py). For mediation: did the workshop lower depression through "
        "the workers' confidence in searching for a job? Built in: the workshop raises confidence by 0.30 points, "
        "each point of confidence lowers depression by 0.30, and the workshop lowers it by 0.04 directly, so the "
        "indirect effect is about -0.09. The real JOBS II records are in the R package mediation (data(jobs)).",
        {
            "treat": "1 = was offered the workshop, 0 = a booklet only (randomised)",
            "econ_hard": "economic hardship before the study (1 to 5)",
            "depress1": "depression before the study (1 to 5)",
            "sex": "1 = female, 0 = male",
            "age": "age in years",
            "nonwhite": "white0 or non.white1",
            "educ": "schooling: lt-hs, highsc, somcol, bach or gradwk",
            "income": "household income: lt15k, 15t24k, 25t39k, 40t49k or 50k+",
            "job_seek": "confidence in searching for a job, after the workshop (1 to 5)",
            "depress2": "depression six months after the workshop (1 to 5)",
            "work1": "psyemp (employed) or psyump (unemployed) six months after",
        },
    ),
    "drug_levels": (
        "MADE-UP DATA: a made-up 2 x 2 crossover bioequivalence study of 18 subjects: each had a test and a "
        "reference formulation, one in each of two periods, and the area under the blood-level curve was "
        "measured. Built in: the test gives 96 % of the reference's AUC, with a within-subject CV of 12 %. "
        "simplydata was tested on the reference datasets of Schütz, Labes & Fuglsang (2014), which it does not "
        "ship; see DATA_LICENSES.md.",
        {
            "subject": "the subject, 1 to 18",
            "period": "1 or 2",
            "formulation": "test or reference",
            "auc": "area under the blood-level curve (the amount of drug that reached the blood)",
        },
    ),
    "deaths_by_age": (
        "MADE-UP DATA: deaths and person-years in six age bands of four made-up counties, for standardised rates. "
        "Eastmere has many old people, Northvale few, so their crude death rates mislead. Invented for practice; "
        "not from any real place.",
        {
            "county": "Northvale, Eastmere, Southby or Westford",
            "age_band": "0-19, 20-39, 40-59, 60-69, 70-79 or 80+",
            "deaths": "deaths in that county and age band",
            "person_years": "person-years lived in that county and age band",
        },
    ),
}


def _list_examples() -> None:
    print("Example tables you can use (made up for practice, except bcg and passive_smoking, real published "
          "studies, ability_tests, real published test scores, sea_levels, real published sea levels, and "
          "sampled_schools, a real survey sample):\n")
    for name, (about, columns) in EXAMPLES.items():
        print(f'  sdata.get_example("{name}")')
        print(f"      {about}")
        print(f"      Columns: {', '.join(columns)}")
        print()
    print('Use one like this:  table = sdata.get_example("marks")  then  chart = sdata.chart(table)')


def get_example(name: str | None = None, from_r_package: str | None = None):
    """A small table to practise with. sdata.get_example("marks")

    sdata.get_example() with no name lists every table and its columns.
    The tables, all made up, are: marks, weather, fruit, growth, sensor, visitors, river, shop, school, meadow,
    trial, clinic, island, toxicity, culture, admissions, resistome, stations, rain, sea_levels (yearly highest sea
    levels), and, for combining studies, bcg and passive_smoking, for hidden factors, ability_tests, for q-values,
    many_tests, for planning and surveys, sampled_schools and course_feedback (answers on a scale), and, for cause
    and effect, job_training, job_search, drug_levels and deaths_by_age. Seven of them copy the columns of a real
    study; simplydata was tested on the real data (DATA_LICENSES.md).
    "shop" has empty cells and a column of dates to practise with; "school" has empty cells too.
    from_r_package="survival" loads a dataset that comes with an installed R package instead, as a
    simplydata table: sdata.get_example("lung", from_r_package="survival"). R itself loads it
    (utils::data); groups (factors) become text, R's NA empty cells, and row names that carry
    information become a first column, "row name". Needs simplydata[r] and the R package already
    installed: nothing is downloaded or installed.
    """
    if from_r_package is not None:
        from .from_r import from_r_package as _load_from_r

        return _load_from_r(name, from_r_package)
    if name is None:
        _list_examples()
        return None
    key = str(name).strip().lower()
    if key.endswith(".csv"):
        key = key[:-4]
    if key not in EXAMPLES:
        lines = [f'There is no example table called "{name}".']
        guess = suggest(key, EXAMPLES, n=1)
        if guess:
            lines.append(f'Did you mean sdata.get_example("{guess[0]}")?')
        lines.append("Tables you can use: " + ", ".join(EXAMPLES))
        raise SimplydataError("\n".join(lines))
    with (files(__name__) / f"{key}.csv").open("r", encoding="utf-8") as fh:
        return pd.read_csv(fh, parse_dates=DATE_COLUMNS.get(key, False))
