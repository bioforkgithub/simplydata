"""Build the simplydata cheat sheet (docs/simplydata_cheat_sheet.tex and .pdf) from the code.

The cheat sheet is a set of learning cards, one card for each group of words (the groups of
sdata.show_all_words() and the manual). Each card is a table with three columns:

    Command            a short example of the word, from its docstring (or its help example)
    What it does       the first sentence of the word's docstring
    Package it calls   the call underneath, read from the tested code of simplydata._underneath

Under each command, a small line lists its options. Everything is read from simplydata itself, so the
cheat sheet cannot drift from the code; tests/test_learn.py checks that every word is on it and that the
.tex matches the code.

    python docs/make_cheat_sheet.py          # write the .tex and compile the PDF (pdflatex)
    python docs/make_cheat_sheet.py --tex    # only write the .tex

The PDF is built on GitHub by .github/workflows/rebuild-docs.yml, next to the manual.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import make_dictionary  # noqa: E402  (the options line, as in the dictionary)
import make_manual  # noqa: E402  (the LaTeX helpers and the "Underneath" line)
from make_manual import code, esc, rich  # noqa: E402

import simplydata  # noqa: E402
from simplydata import learn  # noqa: E402

TEX = HERE / "simplydata_cheat_sheet.tex"
PDF = HERE / "simplydata_cheat_sheet.pdf"
MANUAL_URL = "https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydata_manual.pdf"
DICTIONARY_URL = "https://github.com/bioforkgithub/simplydata/blob/main/docs/manual/simplydataDictionary.pdf"

PREAMBLE = r"""
% ---------------------------------------------------------------------------------------------
% The simplydata cheat sheet. This file is made by docs/make_cheat_sheet.py from simplydata's own
% code. Do not edit it by hand: run  python docs/make_cheat_sheet.py
% ---------------------------------------------------------------------------------------------
\documentclass[10pt,a4paper,landscape]{article}
% no dates or random IDs in the PDF, so it only changes when the cheat sheet changes
\pdfinfoomitdate=1
\pdftrailerid{}
\pdfsuppressptexinfo=-1
\usepackage[T1]{fontenc}
\usepackage{XCharter}
\usepackage[lining,scale=0.88]{FiraSans}
\usepackage[varqu,varl,scaled=0.92]{zi4}
\usepackage{microtype}
\usepackage[a4paper,landscape,top=1.5cm,bottom=1.4cm,left=1.4cm,right=1.4cm,headheight=14pt,headsep=0.4cm]{geometry}
\usepackage[dvipsnames,table]{xcolor}
\usepackage{array}
\usepackage{longtable}
\usepackage{needspace}
\usepackage{fancyhdr}
\usepackage[hidelinks]{hyperref}
\usepackage{bookmark}

\setlength{\parindent}{0pt}
\setlength{\parskip}{0.4em plus 0.2em}
\setlength{\emergencystretch}{3em}
\tolerance=3000
\raggedbottom

\definecolor{brand}{HTML}{1F5F99}
\definecolor{brandlight}{HTML}{E8F0F8}
\definecolor{codefg}{HTML}{24292F}
\definecolor{inkgrey}{HTML}{5A6570}
\hypersetup{colorlinks=true,linkcolor=brand,urlcolor=brand,
  pdftitle={simplydata cheat sheet},pdfauthor={The simplydata project},
  pdfsubject={Every simplydata command on learning cards: what it does and the package it calls}}

\newcommand{\code}[1]{\texttt{\color{codefg}#1}}
% one card: a coloured title bar, then the table of its words
\newcommand{\card}[2]{\par\Needspace{9\baselineskip}\vspace{0.5em}\phantomsection\pdfbookmark[1]{#1}{card:#2}%
  \noindent\colorbox{brand}{\parbox{\dimexpr\linewidth-2\fboxsep}{\sffamily\bfseries\color{white}\strut #1}}\par\nopagebreak}
\newenvironment{cardtable}{\par\small\setlength{\LTpre}{0.1em}\setlength{\LTpost}{0.4em}%
  \rowcolors{2}{white}{brandlight}%
  \begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.37\linewidth}%
  >{\raggedright\arraybackslash}p{0.35\linewidth}>{\raggedright\arraybackslash}p{0.24\linewidth}@{}}
  \hiderowcolors\sffamily\bfseries\color{brand}Command & \sffamily\bfseries\color{brand}What it does
  & \sffamily\bfseries\color{brand}Package it calls\\\hline\endhead\showrowcolors}{\end{longtable}}
\newcommand{\cmd}[3]{#1 & #2 & {\footnotesize #3}\\}
\newcommand{\opts}[1]{\newline{\footnotesize\color{inkgrey}\sffamily options:\enspace}{\footnotesize #1}}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\sffamily\small\bfseries\color{brand}simplydata cheat sheet}
\fancyhead[R]{\sffamily\small\color{inkgrey}@VERSION@}
\fancyfoot[C]{\sffamily\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{\sffamily\small\thepage}\renewcommand{\headrulewidth}{0pt}}
"""

FRONT = r"""
{\fontsize{24}{28}\selectfont\sffamily\bfseries\color{brand} simplydata cheat sheet\par}
\vspace{0.2em}
{\sffamily Every command on one set of cards: type the command, read what it does, and see which package does the
work. @WORDS@ commands in @CARDS@ cards, version @VERSION@.\par}
\vspace{0.2em}
{\sffamily\small\color{inkgrey} Start with \code{import simplydata as sdata}. A command that begins with
\code{table.} works on a table from \code{sdata.table(...)}; \code{chart.} on a chart from
\code{table.start\_chart()} or \code{sdata.chart(...)}; \code{numbers.} on numbers from \code{sdata.number\_list(...)}.
The small grey line under a command names its options. For the full story of a command, use
\code{sdata.help("word")}, the \href{@MANUAL@}{manual} or the \href{@DICTIONARY@}{dictionary}. These cards are
made from simplydata's own code by \code{docs/make\_cheat\_sheet.py}, so they always match the version above.\par}
"""

MAX_OPTIONS = 10  # more than this and the options line names the first ones, then "and N more"


def options_line(key: str) -> str:
    """The options of a word in one short line ("" for options such as show= and words without any)."""
    if key in learn.OPTIONS:
        return ""
    keep = make_dictionary.MAX_OPTIONS
    make_dictionary.MAX_OPTIONS = MAX_OPTIONS
    try:
        line = make_dictionary.main_options(key)
    finally:
        make_dictionary.MAX_OPTIONS = keep
    return "" if line == "none" else line


def row(key: str) -> str:
    command = code(learn._short_example(key))
    options = options_line(key)
    if options:
        command += f"\\opts{{{options}}}"
    return f"\\cmd{{{command}}}{{{rich(learn._summary(key))}}}{{{make_manual.underneath_name(key)}}}"


def make() -> str:
    """The whole cheat sheet as LaTeX text."""
    front = (FRONT.strip().replace("@VERSION@", esc(simplydata.__version__))
             .replace("@WORDS@", str(len(learn._all_keys()))).replace("@CARDS@", str(len(learn.GROUPS)))
             .replace("@MANUAL@", MANUAL_URL).replace("@DICTIONARY@", DICTIONARY_URL))
    out = [PREAMBLE.strip().replace("@VERSION@", "version " + esc(simplydata.__version__)),
           r"\begin{document}", r"\thispagestyle{plain}", front]
    for number, (group, keys) in enumerate(learn.GROUPS, start=1):
        out.append(f"\\card{{{esc(group)}}}{{{number}}}")
        out.append(r"\begin{cardtable}")
        out.extend(row(key) for key in keys)
        out.append(r"\end{cardtable}")
    out.append(r"\end{document}")
    return "\n\n".join(out) + "\n"


def compile_pdf() -> None:
    build = make_manual.latex_folder()
    env = dict(os.environ, SOURCE_DATE_EPOCH="0", FORCE_SOURCE_DATE="1")
    for run in range(2):  # the bookmarks settle on the second run
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={build}", TEX.name],
            cwd=HERE, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode != 0:
            log = (build / f"{TEX.stem}.log").read_text(encoding="utf-8", errors="replace")
            print(log[-4000:])
            raise SystemExit(f"pdflatex failed on the cheat sheet (run {run + 1}); the full log is in {build}")
    shutil.copyfile(build / PDF.name, PDF)


def build(pdf: bool = True) -> None:
    TEX.write_text(make(), encoding="utf-8", newline="\n")
    print(f"Wrote {TEX}")
    if pdf:
        compile_pdf()
        print(f"Wrote {PDF}")


if __name__ == "__main__":
    build(pdf="--tex" not in sys.argv[1:])
