"""Small tables to practise with: sdata.get_example("marks").

Every number in these tables is invented (they are not real people, places or countries), except in "bcg" and
"passive_smoking" (the published results of real studies, for combining studies), "ability_tests" (the
published test scores of Holzinger & Swineford 1939, for hidden factors) and "sea_levels" (the yearly highest
sea levels at Port Pirie, published by Coles 2001), each with its source in its description.
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
        "REAL DATA: 13 trials of the BCG vaccine against tuberculosis, one row per trial (Colditz et al. 1994, "
        "JAMA 271:698-702: the counts published in the paper, facts; the same numbers as R metadat's dat.bcg).",
        {
            "trial": "the first author and the year of the trial",
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
        "REAL DATA: the highest sea level of each year at Port Pirie, South Australia, 1923 to 1987 (Coles, S. 2001, "
        "An Introduction to Statistical Modeling of Extreme Values, Springer, section 3.4.1: the published yearly "
        "maxima, facts; the same numbers as R ismev's portpirie).",
        {
            "year": "the year, 1923 to 1987",
            "sea_level": "the highest sea level reached that year, in metres",
        },
    ),
    "passive_smoking": (
        "REAL DATA: 37 studies of lung cancer in non-smoking women whose husbands smoked, one row per study "
        "(Hackshaw, Law & Wald 1997, BMJ 315:980-988: the odds ratios and intervals published in the paper, facts; "
        "the same numbers as R metadat's dat.hackshaw1998).",
        {
            "study": "the first author and the year of the study",
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
        "REAL DATA: nine mental ability tests taken by 301 pupils of two schools near Chicago in 1937 (Holzinger & "
        "Swineford 1939, Supplementary Educational Monographs 48: the scores as R lavaan ships them, "
        "HolzingerSwineford1939). The classic table for hidden factors: x1 to x3 are visual, x4 to x6 verbal, "
        "x7 to x9 speeded tests.",
        {
            "id": "the pupil's number",
            "sex": "1 or 2 (the source does not say which is which)",
            "ageyr": "age, the years",
            "agemo": "age, the months on top of the years",
            "school": "Pasteur or Grant-White",
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
}


def _list_examples() -> None:
    print("Example tables you can use (made up for practice, except bcg and passive_smoking, real published "
          "studies, ability_tests, real published test scores, and sea_levels, real published sea levels):\n")
    for name, (about, columns) in EXAMPLES.items():
        print(f'  sdata.get_example("{name}")')
        print(f"      {about}")
        print(f"      Columns: {', '.join(columns)}")
        print()
    print('Use one like this:  table = sdata.get_example("marks")  then  chart = sdata.chart(table)')


def get_example(name: str | None = None):
    """A small table to practise with. sdata.get_example("marks")

    sdata.get_example() with no name lists every table and its columns.
    The tables are: marks, weather, fruit, growth, sensor, visitors, river, shop, school, meadow, trial, clinic,
    island, toxicity, culture, admissions, resistome, stations, rain, sea_levels (real published sea levels), and,
    for combining studies, bcg and passive_smoking (real published studies), and, for hidden factors,
    ability_tests (real published test scores).
    "shop" has empty cells and a column of dates to practise with; "school" has empty cells too.
    """
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
