# Data licences

simplydata's code is under the MIT licence ([LICENSE](LICENSE)). This file says what covers the data that come with
it: the practice tables in `src/simplydata/data/` (installed with the package, `sdata.get_example()`) and the
reference data of the reliability study in `validation/data/` (in the repository and the source distribution only).

In short:

- **The MIT licence covers the code and the made-up tables.** The made-up practice tables were invented for
  simplydata; their descriptions start with "MADE-UP DATA" or say "made-up".
- **Each real table keeps its source's terms.** They are listed below, each with its source, how to cite it and the
  licence its source states. Most are numbers published in a paper or a book; numbers as such are facts, but cite the
  source when you use them.
- **The reliability study's copies of tables from GPL or LGPL R packages are not passed on.** It reads them from the R
  package installed on your own computer (`validation/r_data.py`); nothing is stored or downloaded. Five of the real
  practice tables below hold the same numbers as data in GPL R packages (`sampled_schools`, `job_training`,
  `ability_tests`, `sea_levels`, and the published counts of `bcg` and `passive_smoking`); they are kept as published
  facts with their citations, which is a decision for the owner (see the end of this file).

## Practice tables (`src/simplydata/data/`, installed with simplydata)

### Made up (MIT, as the code)

marks, weather, fruit, growth, sensor, visitors, river, shop, school, meadow, trial, clinic, island, toxicity,
culture, admissions, resistome, stations, rain, many_tests, course_feedback, deaths_by_age and job_search.

`job_search` has the columns of the JOBS II study (as the R package mediation ships it), but every value was drawn
with a fixed seed by [`docs/make_job_search.py`](docs/make_job_search.py), with effects built in that the lessons
recover (the workshop raises job-search confidence by 0.30 points, each point of confidence lowers depression by
0.30, and the workshop lowers it by 0.04 directly). It replaces the real JOBS II records that earlier versions
shipped: those are human-subject records distributed by ICPSR (study 2739), whose terms do not allow passing them on.

### Real data

| table | what | source and citation | licence stated by the source |
|---|---|---|---|
| `bcg` | 13 trials of the BCG vaccine (counts) | Colditz, G. A. et al. (1994). Efficacy of BCG vaccine in the prevention of tuberculosis. JAMA 271, 698-702. The same numbers as `dat.bcg` of the R package metadat | The article is (c) American Medical Association; the counts are published facts, copied as numbers only. metadat is GPL (>= 2); nothing of it is copied but the numbers, which are the paper's |
| `passive_smoking` | 37 published odds ratios with their intervals | Hackshaw, A. K., Law, M. R. & Wald, N. J. (1997). The accumulated evidence on lung cancer and environmental tobacco smoke. BMJ 315, 980-988. The same numbers as `dat.hackshaw1998` of metadat | The article is (c) BMJ; the numbers are published facts |
| `ability_tests` | 9 test scores of 301 pupils (1937) | Holzinger, K. J. & Swineford, F. (1939). A study in factor analysis: the stability of a bi-factor solution. Supplementary Educational Monographs 48, University of Chicago. As shipped by the R package lavaan (`HolzingerSwineford1939`; Rosseel 2012, JSS 48(2)) | The monograph states no licence (published 1939); the scores are facts. lavaan is GPL (>= 2) |
| `sea_levels` | 65 yearly maximum sea levels at Port Pirie | Coles, S. (2001). An Introduction to Statistical Modeling of Extreme Values. Springer, section 3.4.1. The same numbers as `portpirie` of the R package ismev | The book is (c) Springer; 65 published numbers (facts). ismev is GPL (>= 2) |
| `sampled_schools` | 200 California schools (stratified sample) | California Department of Education, Academic Performance Index 2000; the stratified sample `apistrat` of the R package survey (Lumley, T. (2010). Complex Surveys. Wiley) | Public accountability data of a state agency; no licence stated. survey is GPL-2 \| GPL-3 |
| `job_training` | 614 men of the National Supported Work study and a survey comparison group | LaLonde, R. J. (1986). Evaluating the econometric evaluations of training programs with experimental data. American Economic Review 76, 604-620; Dehejia, R. H. & Wahba, S. (1999). Causal effects in nonexperimental studies: reevaluating the evaluation of training programs. Journal of the American Statistical Association 94, 1053-1062. As shipped by the R package MatchIt (`lalonde`) | **No licence was stated by the source** (Dehejia posted the data on his web page; the study was run by MDRC for the US Department of Labor). Widely redistributed (MatchIt, and Python packages); kept with these citations. MatchIt is GPL (>= 2) |
| `drug_levels` | AUC of 18 subjects in a 2 x 2 crossover | Sauter et al. (1992), as cited by the next source; reference dataset A of Schütz, H., Labes, D. & Fuglsang, A. (2014). Reference datasets for 2-treatment, 2-sequence, 2-period bioequivalence studies. The AAPS Journal 16, 1292-1297 (supplementary material) | See "The Schütz 2014 supplement" below: free to read, but no open licence is stated |

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
| `bioequivalence_reference.csv` | Schütz, Labes & Fuglsang (2014), supplementary data sets A (Sauter et al. 1992), B (Clayton & Leslie 1981) and C | See "The Schütz 2014 supplement" below |

Read from the installed R packages instead of stored (`validation/r_data.py`), because the copies came from GPL or
LGPL packages: from R's datasets package (GPL-2 | GPL-3) sleep, anscombe, infert, stackloss, mtcars, swiss, iris,
warpbreaks, LakeHuron, AirPassengers, Seatbelts and Puromycin; from MASS birthwt; from lme4 VerbAgg; from AER
NMES1988; from alr4 galtonpeas; from mice nhanes; from HH ProfChal; from survival (LGPL) lung, veteran, heart and
mgus2; from survey apistrat and apiclus1; from MatchIt lalonde; and from mediation the JOBS II records (jobs). The
other R data the study uses (metadat, vegan, ismev, KMsurv and more) were never stored. Each is cited in
[validation/README.md](validation/README.md).

## Open decision: practice tables with the same numbers as GPL R data

`sampled_schools` (survey's apistrat), `job_training` (MatchIt's lalonde), `ability_tests` (lavaan's
HolzingerSwineford1939), `sea_levels` (ismev's portpirie), `bcg` and `passive_smoking` (metadat) hold the same numbers
as data in GPL R packages. They are measured or published values (facts) from the original studies, cited above, and
not creative work of the packages' authors, so they are kept; but the reliability study's copies were removed for
the more cautious reading. If the owner prefers the cautious reading here too, these tables would be replaced by
made-up look-alikes, as `job_search` was.

## The Schütz 2014 supplement

Checked on 2026-11-21. The article (The AAPS Journal 16, 1292-1297, doi:10.1208/s12248-014-9661-0) is free to read
in PubMed Central (PMC4389751) and on the journal's site, and its nine supplementary files (the data sets) can be
downloaded there. But the article carries "© American Association of Pharmaceutical Scientists 2014" and names no
Creative Commons or other open licence, for the article or for the supplementary files. So it is **free to read, not
clearly open** for passing on. The tables hold measured values from published studies (36 numbers in `drug_levels`,
98 rows in `bioequivalence_reference.csv`), which are facts rather than creative work, and no installed R package
ships them to read from instead. They are kept, with their citations, until the owner decides; replacing
`drug_levels` with a made-up crossover, as was done for `job_search`, is the alternative.
