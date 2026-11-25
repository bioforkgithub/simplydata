# Data licences

simplydata's code is under the MIT licence ([LICENSE](LICENSE)). This file says what covers the data that come with
it, and which real data simplydata was tested on without shipping them.

In short:

- **Every practice table is made up**, and the MIT licence covers it as it covers the code
  (`src/simplydata/data/`, installed with the package, `sdata.get_example()`).
- **The reliability study stores only public-domain and published-fact data** (`validation/data/`, in the repository
  and the source distribution only): the NIST files and a few small tables typed from papers or help-page examples.
- **Real data that may not be passed on are not shipped.** simplydata was tested on them: the reliability study and
  the tests read them from the R package installed on your own computer (`validation/r_data.py`), or, for one
  supplement with no open licence, from a file you name. Nothing is downloaded at any time.

## Practice tables (`src/simplydata/data/`): all made up (MIT)

marks, weather, fruit, growth, sensor, visitors, river, shop, school, meadow, trial, clinic, island, toxicity,
culture, admissions, resistome, stations, rain, many_tests, course_feedback, deaths_by_age, the four fjord tables
(fjord_samples, fjord_lab, fjord_stations, fjord_logger: one made-up cruise, messy on purpose, drawn with a fixed seed
by [`docs/make_fjord_tables.py`](docs/make_fjord_tables.py); no real data in them), and the eight below.

Eight tables copy the columns of a real study, so that the lessons can ask the real question, but every value was
drawn with a fixed seed by [`docs/make_practice_tables.py`](docs/make_practice_tables.py) (and
[`docs/make_job_search.py`](docs/make_job_search.py)), with effects built in that the lessons recover. Until
2026-11-22 seven of them held the real data; the owner decided to ship none of it.

| table | made up after | built in | simplydata tested on the real data |
|---|---|---|---|
| `bcg` | Colditz, G. A. et al. (1994). Efficacy of BCG vaccine in the prevention of tuberculosis. JAMA 271, 698-702 | log risk ratio 0.6 - 0.035 x latitude, between-trial spread 0.15 | from R metadat (`dat.bcg`, GPL >= 2): `combine_studies` against metafor, meta and the values of Viechtbauer (2010), in the reliability study and the tests |
| `passive_smoking` | Hackshaw, A. K., Law, M. R. & Wald, N. J. (1997). BMJ 315, 980-988 | odds ratio 1.25 | from R metadat (`dat.hackshaw1998`): `combine_studies(estimates=)` against metafor |
| `ability_tests` | Holzinger, K. J. & Swineford, F. (1939). Supplementary Educational Monographs 48, University of Chicago | three correlated factors (visual, verbal, speed) | from R lavaan (`HolzingerSwineford1939`, GPL >= 2): the published fit of Rosseel (2012, JSS 48(2)), and psych, factanal and statsmodels |
| `sea_levels` | Coles, S. (2001). An Introduction to Statistical Modeling of Extreme Values. Springer, section 3.4.1 (Port Pirie) | GEV with location 3.87, scale 0.20, shape -0.05 | from R ismev (`portpirie`, GPL >= 2): Coles's printed values, extRemes and SciPy |
| `sampled_schools` | California Department of Education, API 2000; the stratified sample `apistrat` of R survey (Lumley 2010) | score falls 3 points per percent of free meals | from R survey (`apistrat`, GPL-2 \| GPL-3): survey-weighted answers against R survey |
| `job_training` | LaLonde, R. J. (1986). American Economic Review 76, 604-620; Dehejia, R. H. & Wahba, S. (1999). JASA 94, 1053-1062 | the training adds 1800 dollars | from R MatchIt (`lalonde`, GPL >= 2; the source states no licence): WeightIt, MatchIt and the MatchIt vignette's 894 |
| `job_search` | Vinokur, A. D., Price, R. H. & Schul, Y. (1995). American Journal of Community Psychology 23, 39-74 (JOBS II) | indirect effect about -0.09 | from R mediation (`jobs`; ICPSR study 2739, whose terms do not allow passing the records on): mediation against the product of coefficients |
| `drug_levels` | Schütz, H., Labes, D. & Fuglsang, A. (2014). The AAPS Journal 16, 1292-1297, reference dataset A | ratio 96 %, within-subject CV 12 % | from a local file (see "The Schütz 2014 data" below) |

## Reliability study (`validation/data/`, repository and source distribution only)

| data | source and citation | licence stated by the source |
|---|---|---|
| NIST StRD files (`nist/`: Norris, Michelso, Mavro, NumAcc4, Filip, Longley, Wampler1 to Wampler5, Rat42, Misra1a, BoxBOD, Roszman1) | National Institute of Standards and Technology, Statistical Reference Datasets, https://www.itl.nist.gov/div898/strd/ ; each file names its original source | Works of the US Government: public domain in the United States (17 U.S.C. 105); stored unchanged |
| `bliss.csv` | Bliss, C. I. (1935). Annals of Applied Biology 22, 134-167 | Published facts (1935), typed from the paper |
| `rat_glycogen.csv` | Sokal, R. R. & Rohlf, F. J. (1981). Biometry, 2nd ed., Box 10.1 | 36 published numbers (facts), typed from the book |
| `chest_sizes.csv` | Quetelet, A. (1846). Lettres sur la théorie des probabilités; Stigler, S. M. (1986). The History of Statistics | Published 1846 (public domain) |
| `rounding_first_base.csv` | Hollander, M. & Wolfe, D. A. (1973). Nonparametric Statistical Methods, p. 140 (the example of R's `friedman.test` help) | Published facts |
| `smokers.csv` | Fleiss, J. L. (1981). Statistical Methods for Rates and Proportions, 2nd ed., p. 139 (the example of R's `prop.test` help) | Published facts |
| `flutd.csv` | Willeberg, P. (1977). Acta Veterinaria Scandinavica 18 (Suppl. 64) (the first example of R `epiR::epi.2by2`) | Published counts (facts) |
| `down_syndrome.csv` | Selvin, S. (2004). Statistical Analysis of Epidemiologic Data, 3rd ed. (the example of R `epitools::ageadjust.direct`) | Published counts (facts) |
| `crowder_seeds.csv` | Crowder, M. J. (1978). Applied Statistics 27, 34-37; the copy in the R package agridat (`crowder.seeds`) | Published counts (facts); agridat is MIT licensed |

Read from the installed R packages instead of stored (`validation/r_data.py`), because the copies came from GPL or
LGPL packages: from R's datasets package (GPL-2 | GPL-3) sleep, anscombe, infert, stackloss, mtcars, swiss, iris,
warpbreaks, LakeHuron, AirPassengers, Seatbelts and Puromycin; from MASS birthwt; from lme4 VerbAgg; from AER
NMES1988; from alr4 galtonpeas; from mice nhanes; from HH ProfChal; from survival (LGPL) lung, veteran, heart and
mgus2; from survey apistrat and apiclus1; from MatchIt lalonde; from mediation the JOBS II records (jobs); and, for
the tests of published answers on the practice-table studies, from metadat, lavaan and ismev. The other R data the
study uses (vegan, KMsurv and more) were never stored. Each is cited in [validation/README.md](validation/README.md).

## The Schütz 2014 data

The article (The AAPS Journal 16, 1292-1297, doi:10.1208/s12248-014-9661-0) is free to read in PubMed Central
(PMC4389751) and on the journal's site, and its supplementary files hold the three reference datasets. But it carries
"(c) American Association of Pharmaceutical Scientists 2014" and names no Creative Commons or other open licence for
the article or its supplementary files (checked 2026-11-21). So simplydata does not ship them: the practice table
`drug_levels` is made up, and `validation/data/bioequivalence_reference.csv` was removed.

simplydata was tested on them. On 2026-11-21 `compare_averages_of(period=)` (the 2 x 2 crossover, the EMA model) gave
for datasets A, B and C the ratios 95.09 %, 71.10 % and 58.56 % with 90 % intervals 90.76 to 99.62 %, 51.45 to
98.26 % and 39.41 to 87.03 %: equal to Table II of the article (where R, SAS and WinNonlin agree) at its 2 printed
decimals of percent, and to R `lm()` on the same model to 1e-9 (relative), with the within-subject CVs equal to R's
too. To rerun these checks, save the three datasets as one CSV file with the columns `dataset` (A, B or C), `subject`,
`period`, `formulation` (test or reference) and `auc`, and name it in the environment variable
`SIMPLYDATA_SCHUTZ2014_FILE`; the reliability study and the tests then read it, and skip those checks otherwise.
