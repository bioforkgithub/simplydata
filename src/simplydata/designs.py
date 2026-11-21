"""Planning an experiment (phase S3d-1): sdata.make_random_assignments and sdata.make_design_table.

simplydata makes no random numbers of its own here. Both words hand the checked inputs to an established R package
and give back its list as a simplydata table:

* make_random_assignments: R blockrand::blockrand() (Snow), permuted blocks of random sizes, one list for each name in
  for_each_of= (stratified randomisation). blockrand counts block sizes in multiples of the number of groups
  (block.sizes = 1:2 gives blocks of 2 and 4 with two groups), so simplydata takes real block sizes, checks that each
  is a multiple of the number of groups, and R divides them.
* make_design_table: R agricolae (de Mendiburu) design.crd, design.rcbd, design.ab (every combination of several
  factors), design.lsd and design.split, with R's default random number generator (kinds = "Mersenne-Twister")
  instead of agricolae's own default "Super-Duper", so that with_seed= gives the layout an R user gets after
  set.seed(). The standard order is R's expand.grid() order (the first factor changes fastest, Yates' order).

make_random_assignments sets R's generator in full (set.seed(kind = "Mersenne-Twister", normal.kind = "Inversion",
sample.kind = "Rejection")): sample() changed in R 3.6.0, so a list made with an older R differs for the same seed.
agricolae sets its own seed with kinds = "Mersenne-Twister" and reads seed 0 as "choose at random", so
make_design_table takes seeds from 1. "plot" numbers the plots 1, 2, 3 ... in the order of agricolae's book
(agricolae's own codes, such as 101 or 11, repeat when a block has 10 or more plots).
"""

from __future__ import annotations

import numbers

import numpy as np

from ._errors import SimplydataError, friendly

KINDS = {"completely random": "completely random", "completely randomised": "completely random",
         "completely randomized": "completely random", "crd": "completely random",
         "randomised blocks": "randomised blocks", "randomized blocks": "randomised blocks",
         "randomised complete blocks": "randomised blocks", "randomized complete blocks": "randomised blocks",
         "blocks": "randomised blocks", "rcbd": "randomised blocks",
         "latin square": "latin square", "lsd": "latin square",
         "split plot": "split plot", "split-plot": "split plot"}
SEED_RULE = 'set.seed(seed, kind = "Mersenne-Twister", normal.kind = "Inversion", sample.kind = "Rejection")'
R36_NOTE = ("R's sample() changed in R 3.6.0, so a list made with an older R differs for the same seed; the printout "
            "names the R version that made this one.")


def _seed(step, with_seed, example, smallest=0):
    if with_seed is None:
        return None
    if not isinstance(with_seed, numbers.Integral) or isinstance(with_seed, bool) or with_seed < smallest:
        why = " (agricolae reads 0 as 'choose at random')" if smallest else ""
        thing = "list" if step == "make_random_assignments" else "table"
        raise SimplydataError(f"with_seed= needs a whole number of {smallest} or more, like with_seed=1{why}. The same "
                              f"seed gives the same {thing} again.\nFor example:  {example}")
    return int(with_seed)


def _whole(step, option, value, example, smallest=1):
    if not isinstance(value, numbers.Integral) or isinstance(value, bool) or value < smallest:
        raise SimplydataError(f"{option} needs a whole number of {smallest} or more (you gave {value!r}).\n"
                              f"For example:  {example}")
    return int(value)


def _names(step, option, values, example, at_least=2):
    if isinstance(values, (str, bytes)) or not isinstance(values, (list, tuple)):
        raise SimplydataError(f"{option} needs a list of names in square brackets, like {option}"
                              f"[\"Bergen\", \"Tromsø\"] (you gave {values!r}).\nFor example:  {example}")
    names = [str(v) for v in values]
    if len(names) < at_least:
        raise SimplydataError(f"{option} needs at least {at_least} names (you gave {len(names)}).\n"
                              f"For example:  {example}")
    if len(set(names)) < len(names):
        twice = next(n for n in names if names.count(n) > 1)
        raise SimplydataError(f'{option} names "{twice}" twice; give each name once.\nFor example:  {example}')
    return names


def _r_version():
    from ._r import r_call

    return str(np.atleast_1d(r_call("paste(R.version$major, R.version$minor, sep = '.')", _cite=False))[0])


# ---------------------------------------------------------------- random assignments (V03)
_R_BLOCKRAND = """
if (!is.null(seed)) {SEED_RULE}
k <- length(lv)
out <- NULL
for (s in lists) {
  b <- blockrand::blockrand(n = n, num.levels = k, levels = lv, block.sizes = sizes / k,
                            stratum = if (nzchar(s)) s else NULL)
  b$stratum <- s
  out <- rbind(out, b)
}
list(list = as.character(out$stratum), number = as.numeric(out$id),
     block = as.numeric(as.character(out$block.id)), size = as.numeric(out$block.size),
     group = as.character(out$treatment))
""".replace("{SEED_RULE}", SEED_RULE)


@friendly(others={"n": "how_many", "levels": "groups", "treatments": "groups", "block_sizes": "in_blocks_of",
                  "block_size": "in_blocks_of", "strata": "for_each_of", "stratum": "for_each_of",
                  "seed": "with_seed"})
def make_random_assignments(how_many=None, groups=2, in_blocks_of=None, for_each_of=None, with_seed=None):
    """A list that says which group each new participant goes to, in random blocks (a randomisation list).

    sdata.make_random_assignments(how_many=60, groups=["A", "B"], in_blocks_of=[4, 6], with_seed=1)
    how_many=60          how many places the list needs (for each list; the last block is completed)
    groups=["A", "B"]    the names of the groups, or how many: groups=3 gives A, B and C
    in_blocks_of=[4, 6]  block sizes, each a multiple of the number of groups; with two or more sizes each
                         block's size is chosen at random, so nobody can guess the end of a block. The default
                         is 2 and 3 times the number of groups (4 and 6 for two groups).
    for_each_of=["Bergen", "Tromsø"]  a separate list for each centre (stratified randomisation)
    with_seed=1          the same list again (with the same version of R)

    Each block holds every group equally often, so the groups stay about the same size all the way through.
    Keep the list away from the people who recruit (allocation concealment).
    Underneath: R blockrand::blockrand() (needs R, see sdata.help("make_random_assignments")).
    """
    step = "make_random_assignments"
    example = 'sdata.make_random_assignments(how_many=60, groups=["A", "B"], in_blocks_of=[4, 6], with_seed=1)'
    if how_many is None:
        raise SimplydataError(f"{step}() needs how_many=, the number of places the list needs.\nFor example:  {example}")
    n = _whole(step, "how_many=", how_many, example)
    if isinstance(groups, numbers.Integral) and not isinstance(groups, bool):
        if groups < 2 or groups > 26:
            raise SimplydataError(f"groups= needs 2 or more groups (up to 26 by number; you gave {groups}). Give the "
                                  f"groups' names for more.\nFor example:  {example}")
        names = [chr(ord("A") + i) for i in range(int(groups))]
    else:
        names = _names(step, "groups=", groups, example)
    k = len(names)
    if in_blocks_of is None:
        sizes, chose = None, True
    else:
        given = in_blocks_of if isinstance(in_blocks_of, (list, tuple)) else [in_blocks_of]
        sizes = [_whole(step, "in_blocks_of=", s, example) for s in given]
        if not sizes:
            raise SimplydataError(f"in_blocks_of= needs at least one block size.\nFor example:  {example}")
        bad = [s for s in sizes if s % k]
        if bad:
            raise SimplydataError(
                f"Each block holds every group equally often, so a block size must be a multiple of the number of "
                f"groups ({k}); {bad[0]} is not. For example in_blocks_of=[{k * 2}, {k * 3}].\nFor example:  "
                f"sdata.make_random_assignments(how_many={n}, groups={names!r}, in_blocks_of=[{k * 2}, {k * 3}])")
        sizes, chose = list(dict.fromkeys(sizes)), False
    lists = [""] if for_each_of is None else _names(step, "for_each_of=", for_each_of,
                                                    'sdata.make_random_assignments(how_many=60, groups=["A", "B"], '
                                                    'for_each_of=["Bergen", "Tromsø"], with_seed=1)', at_least=1)
    seed = _seed(step, with_seed, example)
    from ._r import need_r, r_call

    # checked, not attached (every call names its package), so that nothing hides another package's functions
    need_r(("blockrand",), "A randomisation list in random blocks (R blockrand::blockrand())",
           "Python has no package for permuted-block randomisation lists")
    found = r_call(_R_BLOCKRAND, packages=(),
                   what="A randomisation list in random blocks (R blockrand::blockrand())",
                   python_note="Python has no package for permuted-block randomisation lists",
                   source="blockrand::blockrand",
                   n=float(n), lv=np.array(names, dtype=object),
                   sizes=np.array([2 * k, 3 * k] if sizes is None else sizes, dtype=float),
                   lists=np.array(lists, dtype=object), seed=None if seed is None else float(seed))
    import pandas as pd

    frame = pd.DataFrame({"list": [str(v) for v in np.atleast_1d(found["list"])],
                          "number": np.atleast_1d(found["number"]).astype(np.int64),
                          "block": np.atleast_1d(found["block"]).astype(np.int64),
                          "block size": np.atleast_1d(found["size"]).astype(np.int64),
                          "group": [str(v) for v in np.atleast_1d(found["group"])]})
    if for_each_of is None:
        frame = frame.drop(columns="list")
    from .table import Table

    used = sorted(set(frame["block size"]))
    say_sizes = " and ".join(str(s) for s in used) if len(used) <= 4 else ", ".join(str(s) for s in used)
    where = f" for each of {', '.join(lists[:-1]) + ' and ' + lists[-1] if len(lists) > 1 else lists[0]}" \
        if for_each_of is not None else ""
    counts = frame.groupby("list" if for_each_of is not None else np.zeros(len(frame)), sort=False).size()
    extra = [int(c) for c in counts if int(c) != n]
    print(f"{len(frame)} assignments to {', '.join(names[:-1])} and {names[-1]}{where}, in random blocks of "
          f"{say_sizes} (R blockrand::blockrand()); each block holds every group equally often.")
    if extra:
        print(f"Each list was {n} places long at least: the last block is completed, so a list can be a little longer "
              f"(here {', '.join(str(c) for c in sorted(set(extra)))}). Use the places in order, from number 1.")
    print("Keep the list away from the people who recruit, so nobody knows the next group in advance (allocation "
          "concealment).")
    if chose:
        print(f"simplydata chooses blocks of {2 * k} and {3 * k} places (2 and 3 times the number of groups), of random "
              "sizes, so the end of a block cannot be guessed; in_blocks_of= sets other sizes.")
    if seed is None:
        print("Note: with_seed= was not given, so the next call makes another list. Give with_seed=1 (any whole "
              "number) to make the same list again, and keep a copy of the list itself.")
    else:
        print(f"with_seed={seed} makes the same list again with R {_r_version()} or newer ({R36_NOTE.split(', so')[0]}).")
    return Table(frame)


# ---------------------------------------------------------------- design tables (V04 / V06)
_R_DESIGN = """
if (is.null(seed)) seed <- 0
lev <- lapply(seq_along(nlev), function(i) labels[(sum(nlev[seq_len(i - 1)]) + 1):sum(nlev[seq_len(i)])])
k <- length(nlev)
if (kind == "latin square") {
  d <- agricolae::design.lsd(lev[[1]], serie = 0, seed = seed, kinds = "Mersenne-Twister")
  b <- d$book
  out <- list(plot = as.numeric(seq_len(nrow(b))), row = as.numeric(as.character(b$row)),
              column = as.numeric(as.character(b$col)), f1 = as.character(b[[4]]))
} else if (kind == "split plot") {
  d <- agricolae::design.split(lev[[1]], lev[[2]], r = r, design = "rcbd", serie = 0, seed = seed,
                               kinds = "Mersenne-Twister")
  b <- d$book
  out <- list(whole = as.numeric(b$plots), part = as.numeric(as.character(b$splots)),
              block = as.numeric(as.character(b$block)), f1 = as.character(b[[4]]), f2 = as.character(b[[5]]))
} else {
  how <- if (kind == "randomised blocks") "rcbd" else "crd"
  if (k == 1) {
    d <- if (how == "rcbd") agricolae::design.rcbd(lev[[1]], r = r, serie = 0, seed = seed, kinds = "Mersenne-Twister")
         else agricolae::design.crd(lev[[1]], r = r, serie = 0, seed = seed, kinds = "Mersenne-Twister")
    b <- d$book
    f <- list(as.character(b[[3]]))
  } else {
    d <- agricolae::design.ab(nlev, r = r, design = how, serie = 0, seed = seed, kinds = "Mersenne-Twister")
    b <- d$book
    f <- lapply(seq_len(k), function(i) lev[[i]][as.integer(as.character(b[[2 + i]]))])
  }
  g <- expand.grid(lev, stringsAsFactors = FALSE)
  key <- function(x) do.call(paste, c(lapply(x, as.character), sep = "\\r"))
  out <- c(list(plot = as.numeric(seq_len(nrow(b))), second = as.numeric(as.character(b[[2]]))),
           stats::setNames(f, paste0("f", seq_len(k))),
           list(standard = as.numeric(match(key(f), key(g)))))
}
out
"""
_R_FUNCTIONS = {"completely random": "agricolae::design.crd()", "randomised blocks": "agricolae::design.rcbd()",
                "latin square": "agricolae::design.lsd()", "split plot": 'agricolae::design.split(design = "rcbd")'}


@friendly(others={"replicates": "repeats", "r": "repeats", "reps": "repeats",
                  "design": "of_kind", "kind": "of_kind", "main_plots": "whole_plots", "whole_plot": "whole_plots",
                  "seed": "with_seed"})
def make_design_table(factors=None, repeats=None, of_kind="completely random", whole_plots=None, with_seed=None):
    """A table that says which treatment goes on which plot, in random order: the layout of an experiment.

    sdata.make_design_table({"temperature": [10, 20], "salinity": [30, 35]}, repeats=3, with_seed=1)
    The first thing in the brackets names each factor and its levels; every combination is used (a full
    factorial: here 2 x 2 = 4 combinations, each 3 times, 12 plots in random order).
    repeats=3            how many times each combination is used (the number of blocks with of_kind=
                         "randomised blocks")
    of_kind=             "completely random" (the default: every plot in one random order),
                         "randomised blocks" (each repeat is a block: every combination once in each block, in its
                         own random order), "latin square" (one factor; each level once in every row and every
                         column) or "split plot" (two factors; whole_plots= names the one put on whole plots)
    with_seed=1          the same table again

    The table has a "plot" column (do the plots in this order) and, for the full factorial, the "standard order"
    (R expand.grid() order, the first factor changing fastest).
    Underneath: R agricolae (needs R, see sdata.help("make_design_table")).
    """
    step = "make_design_table"
    example = 'sdata.make_design_table({"temperature": [10, 20], "salinity": [30, 35]}, repeats=3, with_seed=1)'
    levels_of = factors
    if not isinstance(levels_of, dict) or not levels_of:
        raise SimplydataError(f"{step}() needs the factors and their levels first, as a dict in curly brackets: "
                              f"{{\"factor\": [levels], ...}}.\nFor example:  {example}")
    factors, labels, nlev = [], [], []
    for name, levels in levels_of.items():
        if not isinstance(name, str) or not name.strip():
            raise SimplydataError(f"Each factor needs a name in quotes (you gave {name!r}).\nFor example:  {example}")
        names = _names(step, f'the levels of "{name}"', levels, example)
        factors.append(name)
        labels.extend(names)
        nlev.append(len(names))
    if not isinstance(of_kind, str) or of_kind.strip().lower() not in KINDS:
        from ._errors import choice_error

        raise choice_error(step, "of_kind", of_kind, ["completely random", "randomised blocks", "latin square",
                                                      "split plot"])
    kind = KINDS[of_kind.strip().lower()]
    reserved = {"plot", "block", "repeat", "standard order", "row", "column", "whole plot", "part of plot"}
    clash = [f for f in factors if f in reserved]
    if clash:
        raise SimplydataError(f'"{clash[0]}" is a column the table makes itself; give the factor another name, such '
                              f'as "{clash[0]}_level".')
    if kind == "latin square":
        if len(factors) != 1:
            raise SimplydataError(
                "A latin square lays out one factor in rows and columns (each level once in every row and every "
                f"column), so give exactly one factor (you gave {len(factors)}).\nFor example:  "
                'sdata.make_design_table({"variety": ["A", "B", "C", "D"]}, of_kind="latin square", with_seed=1)')
        square = 'sdata.make_design_table({"variety": ["A", "B", "C", "D"]}, of_kind="latin square", with_seed=1)'
        if nlev[0] < 3:
            raise SimplydataError("A latin square needs at least 3 levels (with 2 there is only one layout up to "
                                  f"swapping rows).\nFor example:  {square}")
        if repeats is not None:
            raise SimplydataError("A latin square is one square: the number of levels sets the rows and columns, so "
                                  f"repeats= does not apply. Make two tables (two seeds) for two squares.\nFor example:  "
                                  f"{square}")
        if whole_plots is not None:
            raise SimplydataError(f'whole_plots= goes with of_kind="split plot".\nFor example:  {square}')
        r = None
    else:
        if repeats is None:
            raise SimplydataError(f"{step}() needs repeats=, how many times each combination is used.\n"
                                  f"For example:  {example}")
        r = _whole(step, "repeats=", repeats, example, smallest=2 if kind != "completely random" else 1)
        if kind == "split plot":
            split_example = ('sdata.make_design_table({"irrigation": ["dry", "wet"], "variety": ["A", "B", "C"]}, '
                             'repeats=3, of_kind="split plot", whole_plots="irrigation", with_seed=1)')
            if len(factors) != 2:
                raise SimplydataError("A split plot has two factors: one on whole plots and one on the parts of each "
                                      f"plot (you gave {len(factors)}).\nFor example:  {split_example}")
            if whole_plots not in factors:
                raise SimplydataError("whole_plots= names the factor put on whole plots (the one that is hard to change "
                                      f"plot by plot, such as irrigation): one of {factors}.\nFor example:  "
                                      f"{split_example}")
            if whole_plots != factors[0]:
                factors.reverse()
                nlev.reverse()
                labels = [str(v) for f in factors for v in levels_of[f]]
        elif whole_plots is not None:
            raise SimplydataError('whole_plots= goes with of_kind="split plot".\nFor example:  '
                                  'sdata.make_design_table({"irrigation": ["dry", "wet"], "variety": ["A", "B", "C"]}, '
                                  'repeats=3, of_kind="split plot", whole_plots="irrigation", with_seed=1)')
    seed = _seed(step, with_seed, example, smallest=1)
    from ._r import need_r, r_call

    # checked, not attached: an attached agricolae hides objects that R metafor's formulas look up
    need_r(("agricolae",), f"A design table (R {_R_FUNCTIONS[kind]})",
           "Python has no package for randomised experimental layouts")
    found = r_call(_R_DESIGN, packages=(), what=f"A design table (R {_R_FUNCTIONS[kind]})",
                   python_note="Python has no package for randomised experimental layouts", source="agricolae",
                   nlev=np.array(nlev, dtype=float), labels=np.array(labels, dtype=object), kind=kind,
                   r=None if r is None else float(r), seed=None if seed is None else float(seed))
    import pandas as pd

    def ints(key):
        return np.atleast_1d(found[key]).astype(np.int64)

    if kind == "latin square":
        frame = pd.DataFrame({"plot": ints("plot"), "row": ints("row"), "column": ints("column"),
                              factors[0]: [str(v) for v in np.atleast_1d(found["f1"])]})
    elif kind == "split plot":
        frame = pd.DataFrame({"whole plot": ints("whole"), "part of plot": ints("part"), "block": ints("block"),
                              factors[0]: [str(v) for v in np.atleast_1d(found["f1"])],
                              factors[1]: [str(v) for v in np.atleast_1d(found["f2"])]})
    else:
        second = "block" if kind == "randomised blocks" else "repeat"
        frame = pd.DataFrame({"plot": ints("plot"), second: ints("second")})
        for i, name in enumerate(factors, 1):
            frame[name] = [str(v) for v in np.atleast_1d(found[f"f{i}"])]
        frame["standard order"] = ints("standard")
    # the levels keep the type they were given in (numbers stay numbers)
    for name in factors:
        given = list(levels_of[name])
        lookup = {str(v): v for v in given}
        if all(isinstance(v, numbers.Number) and not isinstance(v, bool) for v in given):
            frame[name] = frame[name].map(lookup)
    from .table import Table

    combos = " x ".join(str(n) for n in nlev)
    if kind == "completely random":
        said = f"every plot in one random order, each combination {r} time{'s' * (r != 1)}"
    elif kind == "randomised blocks":
        said = f"{r} randomised blocks: every combination once in each block, in its own random order"
    elif kind == "latin square":
        said = (f"a {nlev[0]} x {nlev[0]} latin square: each level of '{factors[0]}' once in every row and every "
                "column")
    else:
        said = f"a split plot in {r} blocks: '{factors[0]}' on whole plots, '{factors[1]}' on the parts of each one"
    full = len(factors) > 1 and kind in ("completely random", "randomised blocks")
    what = (f"{len(frame)} plots: " + (f"the {combos} = {frame['standard order'].nunique()} combinations of "
                                       f"{' and '.join(factors) if len(factors) == 2 else ', '.join(factors)}; " if full else "") + said)
    r_name = _R_FUNCTIONS[kind] if not full else f'agricolae::design.ab(design = "{"rcbd" if kind == "randomised blocks" else "crd"}")'
    print(f"A design table of {what} (R {r_name}).")
    order = "whole plot" if kind == "split plot" else "plot"
    print(f'Work through the plots in the order of "{order}"; the randomisation spreads unknown differences (soil, '
          "position, time of day) evenly over the treatments.")
    if "standard order" in frame:
        print('"standard order" numbers the combinations as R expand.grid() lists them (the first factor changes '
              "fastest), the order of design textbooks.")
    if seed is None:
        print("Note: with_seed= was not given, so the next call makes another table. Give with_seed=1 (any whole "
              "number) to make the same table again.")
    else:
        print(f"with_seed={seed} makes the same table again (R's Mersenne-Twister generator, as after set.seed() in R "
              f"{_r_version()}; agricolae's own default generator, Super-Duper, gives another layout).")
    return Table(frame)
