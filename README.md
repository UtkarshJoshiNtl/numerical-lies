# Numerical Lies

Floating-point failure cases made concrete. Each entry is a **four-beat
notebook**: *the lie → the setup → the reality → the rule*. Everything runs
top-to-bottom and the figures are committed, so you can read it as a cheat sheet
or execute it as a lab.

This is an **executable cheat sheet**, not a novel format. The genre is old and
worth copying: Goldberg's *What Every Computer Scientist Should Know About
Floating-Point Arithmetic* (1991), Bruce Dawson's floating-point articles, and
the various "pitfalls" pages. The point here is that each lie is *reproduced*,
not just asserted.

## Cheat sheet

| # | the lie | the truth | notebook |
|---|---------|-----------|----------|
| 0 | "the numbers I type are what's stored" | every literal rounds to the nearest double first | [`00_representation`](notebooks/00_representation.ipynb) |
| 1 | "addition is associative" | order changes the sum; error grows with n | [`01_sum_order`](notebooks/01_sum_order.ipynb) |
| 2 | "subtracting close numbers is harmless" | it cancels leading digits and amplifies noise | [`02_cancellation`](notebooks/02_cancellation.ipynb) |
| 3 | "(a+b)+c == a+(b+c)" | false the moment magnitudes differ; compilers reassociate too | [`03_non_associativity`](notebooks/03_non_associativity.ipynb) |
| 4 | "a tiny input error stays tiny" | chaotic systems amplify it exponentially | [`04_chaos`](notebooks/04_chaos.ipynb) |
| 5 | "small dt / more bits makes any integrator fine" | Euler leaks energy; fp32 drifts; use symplectic methods | [`05_energy_drift`](notebooks/05_energy_drift.ipynb) |

## Golden rules

1. **Never compare floats with `==`.** Use `math.isclose` / `np.isclose` with a
   relative tolerance.
2. **Never sum large dynamic-range data naively.** Use `math.fsum`, Kahan, or a
   pairwise/tree reduction.
3. **Beware subtracting near-equal values.** Reformulate; prefer the standard
   library's stable forms: `log1p`, `expm1`, `hypot`.
4. **Floating point is not associative or distributive.** Don't let reduction
   order be accidental — pick it deliberately.
5. **Think in relative error.** Absolute error is meaningless without a scale.
6. **Know your ulp.** `double` carries ~15–16 decimal digits, `float` ~7.
7. **Prefer `double`** unless you're memory/bandwidth bound; fp32 drift
   accumulates over long runs.
8. **Use symplectic integrators** (Verlet/leapfrog) for conserved systems.
   Explicit Euler is a trap, not a small-`dt` choice.
9. **Chaotic systems have a hard prediction horizon**, no matter the precision.
10. **Validate against a properly rounded reference** — `fractions`, `decimal`,
    or `math.fsum` — never against another float computation.
11. **Don't trust `-ffast-math`** if you rely on IEEE semantics or exact
    reproducibility.

## Run it

```sh
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt

# build the notebooks from their source of truth
.venv/bin/python tools/build_notebooks.py

# execute them in place (regenerates committed outputs + figures/)
cd notebooks && ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace *.ipynb
```

To just read: open any notebook in `notebooks/`. The cells are executed and the
figures live in `figures/`.

## Layout

```
notebooks/   the six four-beat notebooks (executed)
figures/     PNGs exported by the notebooks
tools/       build_notebooks.py — single source of truth for the cells
references.md
requirements.txt
```
