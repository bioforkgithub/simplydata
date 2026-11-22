"""Datasets of the reliability study that come from GPL or LGPL R packages, read from the installed packages.

Earlier versions stored copies of these tables in validation/data/. Their numbers are mostly old published facts,
but the copies were taken from R packages under the GPL or LGPL, so they are no longer passed on with simplydata
(see DATA_LICENSES.md): the cases and the tests read them from the R package that ships them, on this computer.
Nothing is downloaded. Without R, rpy2 or the package, the cases that need a table are skipped (and the tests skip,
or fail where SIMPLYDATA_REQUIRE_R=1).

Each entry gives the R packages it needs and R code whose last value is a named list of columns. read() turns it
into the same pandas table that the stored copy used to give: the same columns in the same order, whole numbers as
whole numbers and text as text (tests/test_validation.py checks the names, sizes and kinds).
"""

from __future__ import annotations

import io

import numpy as np
import pandas as pd

TABLES = {
    # R's datasets package (GPL-2 | GPL-3), which comes with R
    "sleep": ((), "d <- datasets::sleep; list(extra = d$extra, group = as.integer(as.character(d$group)), "
                  "ID = as.integer(as.character(d$ID)))"),
    "anscombe": ((), "d <- datasets::anscombe; list(x1 = as.integer(d$x1), x2 = as.integer(d$x2), "
                     "x3 = as.integer(d$x3), x4 = as.integer(d$x4), y1 = d$y1, y2 = d$y2, y3 = d$y3, y4 = d$y4)"),
    "infert": ((), "d <- datasets::infert; list(education = as.character(d$education), age = as.integer(d$age), "
                   "parity = as.integer(d$parity), induced = as.integer(d$induced), case = as.integer(d$case), "
                   "spontaneous = as.integer(d$spontaneous), stratum = as.integer(d$stratum), "
                   "pooled_stratum = as.integer(d$pooled.stratum))"),
    "stackloss": ((), "d <- datasets::stackloss; list(air_flow = as.integer(d$Air.Flow), "
                      "water_temp = as.integer(d$Water.Temp), acid_conc = as.integer(d$Acid.Conc.), "
                      "stack_loss = as.integer(d$stack.loss))"),
    "mtcars": ((), "d <- datasets::mtcars; list(model = rownames(d), mpg = d$mpg, cyl = as.integer(d$cyl), "
                   "disp = d$disp, hp = as.integer(d$hp), drat = d$drat, wt = d$wt, qsec = d$qsec, "
                   "vs = as.integer(d$vs), am = as.integer(d$am), gear = as.integer(d$gear), "
                   "carb = as.integer(d$carb))"),
    "swiss": ((), "d <- datasets::swiss; list(Province = rownames(d), Fertility = d$Fertility, "
                  "Agriculture = d$Agriculture, Examination = as.integer(d$Examination), "
                  "Education = as.integer(d$Education), Catholic = d$Catholic, Infant.Mortality = d$Infant.Mortality)"),
    "iris": ((), "d <- datasets::iris; list(Sepal.Length = d$Sepal.Length, Sepal.Width = d$Sepal.Width, "
                 "Petal.Length = d$Petal.Length, Petal.Width = d$Petal.Width, Species = as.character(d$Species))"),
    "warpbreaks": ((), "d <- datasets::warpbreaks; list(breaks = as.integer(d$breaks), wool = as.character(d$wool), "
                       "tension = as.character(d$tension))"),
    "lake_huron": ((), "x <- datasets::LakeHuron; list(year = as.integer(round(stats::time(x))), "
                       "level = as.numeric(x))"),
    "air_passengers": ((), "x <- datasets::AirPassengers; "
                           "list(month = format(seq(as.Date('1949-01-01'), by = 'month', length.out = length(x))), "
                           "passengers = as.integer(x))"),
    "seatbelts": ((), "s <- datasets::Seatbelts; t <- stats::time(s); "
                      "list(month = seq_len(nrow(s)), year = as.integer(floor(t + 1e-6)), "
                      "month_of_year = as.integer(stats::cycle(s)), drivers = as.integer(s[, 'drivers']), "
                      "DriversKilled = as.integer(s[, 'DriversKilled']), law = as.integer(s[, 'law']))"),
    "puromycin": ((), "d <- datasets::Puromycin; d <- d[d$state == 'treated', ]; "
                      "list(conc = d$conc, rate = as.integer(d$rate))"),
    # MASS (GPL-2 | GPL-3), which comes with R
    "birthwt": (("MASS",), "d <- MASS::birthwt; lapply(d[c('low', 'age', 'lwt', 'race', 'smoke', 'ptl', 'ht', 'ui', "
                           "'ftv', 'bwt')], as.integer)"),
    # lme4 (GPL >= 2)
    "verbagg": (("lme4",), "d <- lme4::VerbAgg; list(anger = as.integer(d$Anger), gender = as.character(d$Gender), "
                           "item = as.character(d$item), id = as.integer(as.character(d$id)), "
                           "btype = as.character(d$btype), situ = as.character(d$situ), mode = as.character(d$mode), "
                           "r2 = as.character(d$r2))"),
    # AER (GPL-2 | GPL-3): 7 of the 19 columns of NMES1988
    "nmes1988": (("AER",), "e <- new.env(); utils::data('NMES1988', package = 'AER', envir = e); d <- e$NMES1988; "
                           "list(visits = as.integer(d$visits), hospital = as.integer(d$hospital), "
                           "health = as.character(d$health), chronic = as.integer(d$chronic), "
                           "gender = as.character(d$gender), school = as.integer(d$school), "
                           "insurance = as.character(d$insurance))"),
    # alr4 (GPL >= 2)
    "galton_peas": (("alr4",), "e <- new.env(); utils::data('galtonpeas', package = 'alr4', envir = e); "
                               "d <- e$galtonpeas; list(parent = as.integer(d$Parent), progeny = d$Progeny, sd = d$SD)"),
    # mice (GPL-2 | GPL-3)
    "nhanes": (("mice",), "d <- mice::nhanes; list(age = as.integer(d$age), bmi = d$bmi, hyp = as.numeric(d$hyp), "
                          "chl = as.numeric(d$chl))"),
    # HH (GPL >= 2): the counts of Heiberger & Robbins (2014), JSS 57(5)
    "prof_chal": (("HH",), "e <- new.env(); utils::data('ProfChal', package = 'HH', envir = e); d <- e$ProfChal; "
                           "list(question = as.character(d$Question), subtable = as.character(d$Subtable), "
                           "strongly_disagree = as.integer(d[['Strongly Disagree']]), "
                           "disagree = as.integer(d$Disagree), no_opinion = as.integer(d[['No Opinion']]), "
                           "agree = as.integer(d$Agree), strongly_agree = as.integer(d[['Strongly Agree']]))"),
    # survival (LGPL >= 2)
    "lung": (("survival",), "d <- survival::lung; list(time = as.integer(d$time), age = as.integer(d$age), "
                            "sex = ifelse(d$sex == 1, 'male', 'female'), ph.ecog = as.numeric(d$ph.ecog), "
                            "died = ifelse(d$status == 2, 'yes', 'no'))"),
    "veteran": (("survival",), "d <- survival::veteran; list(trt = ifelse(d$trt == 1, 'standard', 'test'), "
                               "celltype = as.character(d$celltype), time = as.integer(d$time), "
                               "status = as.integer(d$status), karno = as.integer(d$karno), age = as.integer(d$age))"),
    "heart": (("survival",), "d <- survival::heart; list(id = as.integer(d$id), start = d$start, stop = d$stop, "
                             "event = as.integer(d$event), age = d$age, year = d$year, "
                             "surgery = as.integer(d$surgery), transplant = as.integer(as.character(d$transplant)))"),
    "mgus2": (("survival",), "d <- survival::mgus2; etime <- ifelse(d$pstat == 0, d$futime, d$ptime); "
                             "event <- ifelse(d$pstat == 0, 2 * d$death, 1); "
                             "list(id = as.integer(d$id), age = as.integer(d$age), sex = as.character(d$sex), "
                             "etime = as.integer(etime), "
                             "outcome = c('censored', 'pcm', 'death')[event + 1])"),
    # survey (GPL-2 | GPL-3)
    "apistrat": (("survey",), "e <- new.env(); utils::data('api', package = 'survey', envir = e); d <- e$apistrat; "
                              "list(stype = as.character(d$stype), pw = d$pw, fpc = as.integer(d$fpc), "
                              "api00 = as.integer(d$api00), "
                              "api99 = as.integer(d$api99), enroll = as.integer(d$enroll), meals = as.integer(d$meals), "
                              "ell = as.integer(d$ell), sch.wide = as.character(d$sch.wide), "
                              "awards = as.character(d$awards))"),
    "apiclus1": (("survey",), "e <- new.env(); utils::data('api', package = 'survey', envir = e); d <- e$apiclus1; "
                              "list(dnum = as.integer(d$dnum), api00 = as.integer(d$api00), "
                              "enroll = as.integer(d$enroll), pw = d$pw, fpc = as.integer(d$fpc), "
                              "sch.wide = as.character(d$sch.wide), stype = as.character(d$stype))"),
    # MatchIt (GPL >= 2)
    "lalonde": (("MatchIt",), "e <- new.env(); utils::data('lalonde', package = 'MatchIt', envir = e); d <- e$lalonde; "
                              "list(treat = as.integer(d$treat), age = as.integer(d$age), educ = as.integer(d$educ), "
                              "race = as.character(d$race), married = as.integer(d$married), "
                              "nodegree = as.integer(d$nodegree), re74 = d$re74, re75 = d$re75, re78 = d$re78)"),
}


_TEXT = pd.read_csv(io.StringIO("a" + chr(10) + "x" + chr(10)))["a"].dtype


def packages(name: str) -> tuple:
    """The R packages a table needs ("sleep" or "sleep.csv")."""
    return TABLES[name.removesuffix(".csv")][0]


def ready(name: str) -> bool:
    """True where R, rpy2 and the table's packages are installed."""
    try:
        from simplydata._r import r_ready
    except Exception:  # noqa: BLE001
        return False
    try:
        return bool(r_ready(packages(name)))
    except Exception:  # noqa: BLE001
        return False


def read(name: str) -> pd.DataFrame:
    """The table, read from its R package ("sleep" or "sleep.csv"). Needs R; raises simplydata's error without it."""
    from simplydata._r import need_r, r_call

    key = name.removesuffix(".csv")
    needed, code = TABLES[key]
    need_r(needed, f"the {key} data")
    found = r_call(code, what=f"the {key} data (from R)")
    columns = {}
    for column, values in found.items():
        array = np.asarray(values)
        if array.dtype.kind in "iu":
            if np.any(array == np.iinfo(np.int32).min):  # R's NA in a whole-number column
                raise ValueError(f"{key}: column {column} has empty cells; read it with as.numeric() in TABLES")
            columns[column] = array.astype("int64")
        elif array.dtype.kind == "f":
            columns[column] = array.astype(float)
        else:
            # text as pandas reads it from a file: the str type in pandas 3, object in pandas 2
            columns[column] = pd.Series([None if v in ("NA", None) else str(v) for v in array], dtype=_TEXT)
    return pd.DataFrame(columns)
