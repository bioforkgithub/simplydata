# Governance

## Who looks after simplydata

Manish Prakash Victor ([bioforkgithub](https://github.com/bioforkgithub)) is the lead
maintainer. He reviews and merges pull requests, makes the releases and has the final say.

There is room for co-maintainers. Someone who has contributed good pull requests and reviews
over some months can be invited by the lead maintainer. A co-maintainer can review and merge
pull requests and look after the warning issues and the Dependabot pull requests
([MAINTAINING.md](MAINTAINING.md)).

## How decisions are made

- Ideas and problems start as GitHub issues, so the reasons are public.
- Changes reach `main` only through pull requests that pass all required checks.
- Most decisions are made by agreement in the issue or the pull request. When people do not
  agree, the lead maintainer decides and writes down why.
- Changes to the core rules below need the lead maintainer's approval.

## The core rules

1. **No own computation.** Every number comes from the parent package (pandas, Polars, NumPy,
   SciPy, statsmodels, matplotlib, seaborn, python-control) or from R. simplydata chooses,
   checks and explains; it does not compute results itself.
2. **No network.** simplydata never sends data anywhere: no telemetry, no logging of user data.
   Tests enforce this ([SECURITY.md](SECURITY.md)).
3. **Only plain words.** Each word reads like talking to the program, and plain words are used
   where the parent syntax is hard.
4. **Honest labels.** A result says which method and which package gave it, and what it does not
   show.

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to take part.
