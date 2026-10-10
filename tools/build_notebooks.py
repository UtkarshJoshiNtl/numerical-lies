"""Build the Numerical Lies notebooks.

Single source of truth for the .ipynb files. Run:

    python tools/build_notebooks.py

then execute them with nbconvert (see README). Keeping the cells here makes the
notebooks reproducible and diffable without hand-editing JSON.
"""

from __future__ import annotations

import pathlib

import nbformat as nbf

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "notebooks"


def md(text: str):
    return nbf.v4.new_markdown_cell(text.strip("\n"))


def code(text: str):
    return nbf.v4.new_code_cell(text.strip("\n"))


def notebook(cells):
    nb = nbf.v4.new_notebook()
    nb.cells = cells
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    }
    return nb


BOOTSTRAP = """
%matplotlib inline
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path

matplotlib.rcParams["figure.dpi"] = 110
FIG = Path("../figures")
FIG.mkdir(exist_ok=True)
rng = np.random.default_rng(0)
"""


# ---------------------------------------------------------------------------
# 00. Representation
# ---------------------------------------------------------------------------
nb00 = notebook([
    md("""
# 0. Representation — `0.1 + 0.2` is not `0.3`

**The lie.** *"The numbers I type are the numbers the machine stores."*

Floating point is a finite set of points on the real line. Every decimal you
type is first rounded to the nearest representable point, and that rounding
happens *before* any arithmetic. This notebook shows the gap.
"""),
    md("## The setup"),
    code(BOOTSTRAP),
    code("""
from fractions import Fraction

print("0.1 + 0.2      =", repr(0.1 + 0.2))
print("0.1 + 0.2 == 0.3 ?", 0.1 + 0.2 == 0.3)
print("0.1 + 0.2 as exact rational:", Fraction(0.1 + 0.2))
"""),
    md("""
`Fraction(0.1)` is the *true* value of the double nearest to `0.1` — 55
significant bits of a binary fraction, nowhere near `1/10`.
"""),
    code("""
print("Fraction(0.1) =", Fraction(0.1))
print("1/10          =", Fraction(1, 10))
print("stored - 1/10 =", float(Fraction(0.1) - Fraction(1, 10)))
"""),
    md("## The reality"),
    code("""
# The gap between neighbours is not fixed; it doubles at every power of two.
for x in [1.0, 2.0, 4.0, 1e6, 1e16]:
    print(f"x = {x:>10.1e}   ulp = {np.spacing(x):.3e}   relative gap = {np.spacing(x)/x:.3e}")

print()
print("0.1 + 0.2 prints as", format(0.1 + 0.2, ".17f"))
print("0.3        prints as", format(0.3, ".17f"))
"""),
    code("""
xs = np.arange(0.1, 1.0, 0.1)
err = np.array([float(Fraction(float(x)) - Fraction(x).limit_denominator(10**12)) for x in xs])

fig, ax = plt.subplots(1, 2, figsize=(11, 4))

mag = np.logspace(-8, 8, 400)
ax[0].loglog(mag, np.spacing(mag), "o", ms=2)
ax[0].set_xlabel("magnitude x")
ax[0].set_ylabel("gap to next double (ulp)")
ax[0].set_title("Absolute precision is relative\\nstep doubles every power of two")

ax[1].bar([f"{x:.1f}" for x in xs], err)
ax[1].axhline(0, color="k", lw=0.8)
ax[1].set_ylabel("stored value - intended decimal")
ax[1].set_title("Every 'round' decimal is off by a different amount")
ax[1].tick_params(axis="x", rotation=45)

fig.tight_layout()
fig.savefig(FIG / "00_representable_gap.png", bbox_inches="tight")
plt.show()
"""),
    md("""
## The rule

- A decimal literal is **rounded to the nearest double** first; the error is up
  to half an ulp *relative* to its size.
- There is no fixed absolute resolution. `1e16` has no room for `1.0`.
- `repr()` / `format(x, ".17g")` shows the true neighbour. `print(0.1)` lies
  prettily.

```python
# fragile
if x == 0.3: ...
# robust
import math
if math.isclose(x, 0.3, rel_tol=1e-12): ...
```
"""),
    md("""
## Taking it further

- Goldberg, *What Every Computer Scientist Should Know About Floating-Point
  Arithmetic*, §1 (formats, relative error, ulps).
- `float.as_integer_ratio()` — inspect any float exactly.
- `math.ulp(x)` (3.9+) — the local gap without `numpy`.
"""),
])


# ---------------------------------------------------------------------------
# 01. Summation order
# ---------------------------------------------------------------------------
nb01 = notebook([
    md("""
# 1. Summation order — same data, different answer

**The lie.** *"Addition is associative, so the order I add things in can't
matter."*

In floating point, `(a + b) + c` and `a + (b + c)` are generally different, and
the difference grows with the *dynamic range* of the data and the number of
terms. This is not a rounding curiosity — it is why two parallel reductions of
the same array can disagree.
"""),
    md("## The setup"),
    code(BOOTSTRAP),
    code("""
def naive_sum(a):
    s = 0.0
    for x in a:
        s += x
    return s

def pairwise_sum(a):
    a = np.asarray(a, dtype=float)
    if a.size <= 8:
        return float(np.sum(a))
    m = a.size // 2
    return pairwise_sum(a[:m]) + pairwise_sum(a[m:])

def kahan_sum(a):
    s = 0.0
    c = 0.0
    for x in a:
        y = x - c
        t = s + y
        c = (t - s) - y
        s = t
    return s
"""),
    md("## The reality"),
    code("""
big = 1e16
tiny = 1.0
print("naive  [1e16, 1, -1e16] =", (big + tiny) + (-big))
print("true                     =", 1.0)
print()
a = [big] + [tiny] * 100000
print("naive sum   =", naive_sum(a))
print("fsum (exact)=", __import__("math").fsum(a))
"""),
    code("""
ns = [10, 100, 1_000, 10_000, 100_000, 1_000_000]
naive_err, kahan_err, pw_err = [], [], []
for n in ns:
    a = rng.standard_normal(n) * 10.0 ** rng.integers(-8, 8, n)
    ref = __import__("math").fsum(a.tolist())
    naive_err.append(abs(naive_sum(a.tolist()) - ref) / max(abs(ref), 1e-300))
    kahan_err.append(abs(kahan_sum(a.tolist()) - ref) / max(abs(ref), 1e-300))
    pw_err.append(abs(pairwise_sum(a) - ref) / max(abs(ref), 1e-300))

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.loglog(ns, naive_err, "o-", label="naive (sequential)")
ax.loglog(ns, pw_err, "s-", label="pairwise (tree)")
ax.loglog(ns, kahan_err, "^-", label="Kahan compensated")
ax.loglog(ns, np.array(ns) * np.finfo(float).eps, "k--", lw=0.8, label="n * eps")
ax.set_xlabel("number of terms n")
ax.set_ylabel("relative error vs exact")
ax.set_title("Error grows with n — but only for the naive order")
ax.legend()
fig.tight_layout()
fig.savefig(FIG / "01_sum_order.png", bbox_inches="tight")
plt.show()
"""),
    md("""
## The rule

- Sequential summation accumulates error ~ `n * eps` (worst case), typically
  ~`sqrt(n) * eps` for random data. **Tree/pairwise summation** cuts it to
  ~`log2(n) * eps`.
- When it must be exact, use a compensated sum: `math.fsum` (correctly rounded),
  Kahan/Neumaier, or sort by magnitude before summing.
- In parallel code the reduction *order is not fixed*; you must choose an
  order-insensitive algorithm, not hope.

```python
math.fsum(data)                 # correctly rounded, use it by default
np.sum(data)                    # pairwise under the hood, good
data.sort(key=abs)              # then naive sum — also fine
```
"""),
    md("""
## Taking it further

- Kahan (1965); Neumaier (1974) — compensated summation.
- Higham, *Accuracy and Stability of Numerical Algorithms*, ch. 4.
- `math.fsum` is exact (correctly rounded) by construction.
"""),
])


# ---------------------------------------------------------------------------
# 02. Cancellation
# ---------------------------------------------------------------------------
nb02 = notebook([
    md("""
# 2. Catastrophic cancellation

**The lie.** *"Subtracting two close numbers is a harmless operation."*

When you subtract nearly equal quantities, the leading digits cancel and what
survives is pure rounding noise, magnified. The cure is almost always an
**algebraic reformulation** that avoids the subtraction.
"""),
    md("## The setup"),
    code(BOOTSTRAP),
    code("""
from decimal import Decimal, getcontext
getcontext().prec = 60

def quad_naive(a, b, c):
    disc = np.sqrt(b * b - 4 * a * c)
    return (-b + disc) / (2 * a), (-b - disc) / (2 * a)

def quad_stable(a, b, c):
    disc = np.sqrt(b * b - 4 * a * c)
    q = -0.5 * (b + np.copysign(disc, b))
    return c / q, q / a

def quad_exact(a, b, c):
    a, b, c = Decimal(a), Decimal(b), Decimal(c)
    disc = (b * b - 4 * a * c).sqrt()
    return float((-b + disc) / (2 * a)), float((-b - disc) / (2 * a))
"""),
    md("## The reality"),
    code("""
a, b, c = 1.0, 1e8, 1.0
naive = quad_naive(a, b, c)
stable = quad_stable(a, b, c)
exact = quad_exact(a, b, c)
print("root next to zero:  naive =", repr(naive[0]))
print("                    stable=", repr(stable[0]))
print("                    exact =", repr(exact[0]))
print("relative error naive :", abs(naive[0] - exact[0]) / abs(exact[0]))
print("relative error stable:", abs(stable[0] - exact[0]) / abs(exact[0]))
"""),
    code("""
# 1 - cos(x) for small x: subtracts two numbers that both approach 1.
xs = np.logspace(-1, -8, 60)
naive = 1.0 - np.cos(xs)
stable = 2.0 * np.sin(xs / 2.0) ** 2
# high-precision reference from the series 1 - cos x = x^2/2 - x^4/24 + ...
truth = xs**2 / 2 - xs**4 / 24

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.loglog(xs, np.abs(naive - truth) / truth, "o-", label="1 - cos(x)")
ax.loglog(xs, np.abs(stable - truth) / truth, "s-", label="2 sin^2(x/2)")
ax.axhline(np.finfo(float).eps, color="k", ls=":", lw=0.8, label="eps")
ax.set_xlabel("x")
ax.set_ylabel("relative error")
ax.set_title("Cancellation destroys precision as x -> 0")
ax.invert_xaxis()
ax.legend()
fig.tight_layout()
fig.savefig(FIG / "02_cancellation.png", bbox_inches="tight")
plt.show()
"""),
    md("""
## The rule

- Identify subtractions of near-equal values; they are the danger.
- Reformulate:
  - quadratic formula → the stable `q = -½(b + sign(b)√disc)` form;
  - `1 − cos x` → `2 sin²(x/2)`;
  - `log(1+x)` → `math.log1p(x)`; `exp(x) − 1` → `math.expm1(x)`;
  - `√(x²+y²)` → `math.hypot(x, y)`.
- The standard library already ships the stable forms — **use them.**

```python
math.log1p(x)   # not log(1 + x)
math.expm1(x)   # not exp(x) - 1
math.hypot(x, y)# not sqrt(x*x + y*y)
```
"""),
    md("""
## Taking it further

- Goldberg §1.4 (Cancellation) and the quadratic-formula example.
- Higham, ch. 1 (cancellation as loss of leading digits).
- `numpy`/`scipy.special` use the stable forms internally — e.g. `np.log1p`.
"""),
])


# ---------------------------------------------------------------------------
# 03. Non-associativity
# ---------------------------------------------------------------------------
nb03 = notebook([
    md("""
# 3. Non-associativity — `(a+b)+c != a+(b+c)`

**The lie.** *"Parenthesisation is a formatting choice."*

Because every intermediate result rounds, regrouping changes the answer. And
because compilers and parallel runtimes are free to reassociate (unless
forbidden), **the same source can produce different bits on different machines.**
"""),
    md("## The setup"),
    code(BOOTSTRAP),
    code("""
def mismatch_rate(spread, n=200_000):
    e = rng.integers(0, spread + 1, (n, 3))
    a = 10.0 ** e[:, 0]
    b = -10.0 ** e[:, 1]
    c = 10.0 ** e[:, 2]
    left = (a + b) + c
    right = a + (b + c)
    return float(np.mean(left != right))
"""),
    md("## The reality"),
    code("""
a, b, c = 1e16, -1e16, 1.0
print("(a + b) + c =", (a + b) + c)
print("a + (b + c) =", a + (b + c))
print()
spreads = list(range(0, 25, 4))
rates = [mismatch_rate(s) for s in spreads]
for s, r in zip(spreads, rates):
    print(f"exponent spread {s:2d}:  {r*100:5.1f}% of random triples regroup differently")
"""),
    code("""
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(spreads, np.array(rates) * 100, "o-")
ax.set_xlabel("spread between largest and smallest addend (orders of magnitude)")
ax.set_ylabel("% of triples where (a+b)+c != a+(b+c)")
ax.set_title("Associativity fails as soon as magnitudes differ")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / "03_associativity.png", bbox_inches="tight")
plt.show()
"""),
    md("""
### Does the *compiler* reassociate too?

Yes. With `-ffast-math` (or `-Ofast`) GCC/Clang may reorder your arithmetic and
delete your carefully constructed failure. This is the one place a C compiler
teaches the lesson better than Python. The cell below compiles a tiny program if
`gcc` is available.
"""),
    code("""
import shutil, subprocess, tempfile, pathlib

src = r'''
#include <stdio.h>
#include <math.h>
int main(void) {
    volatile double a = 1e16, b = -1e16, c = 1.0;
    double left  = (a + b) + c;
    double right = a + (b + c);
    printf("(a+b)+c = %.17g\\na+(b+c) = %.17g\\n", left, right);
    printf("equal? %s\\n", left == right ? "yes" : "NO");
    return 0;
}
'''
if shutil.which("gcc"):
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "assoc.c"
        p.write_text(src)
        for flags in ([], ["-O2"], ["-O2", "-ffast-math"]):
            exe = pathlib.Path(d) / "a.out"
            subprocess.run(["gcc", *flags, str(p), "-lm", "-o", str(exe)], check=True)
            out = subprocess.run([str(exe)], capture_output=True, text=True).stdout
            print(f"gcc {' '.join(flags) or '(no flags)'}")
            print(out.strip())
            print()
else:
    print("gcc not found — skipping the compiler demo")
"""),
    md("""
## The rule

- Treat floating-point `+` as **not associative, not distributive**. Write
  reductions so the order is fixed and intentional (see notebook 1).
- Test **against a properly rounded reference** (`fsum`, `Fraction`, `decimal`),
  not against another float computation.
- If numerical reproducibility matters, disable fast-math and fix reduction
  order; don't assume the compiler preserves your parentheses.
"""),
    md("""
## Taking it further

- Goldberg §1.1–1.2; IEEE-754 rounding.
- "Reproducible BLAS" (Demmel & Nguyen) — the HPC face of this problem.
- Compiler flag docs: `-ffast-math`, `-fassociative-math`, `-fno-signed-zeros`.
"""),
])


# ---------------------------------------------------------------------------
# 04. Chaos
# ---------------------------------------------------------------------------
nb04 = notebook([
    md("""
# 4. Chaotic divergence — a 1e-16 nudge changes everything

**The lie.** *"A tiny error in the initial condition stays tiny."*

For chaotic systems, nearby trajectories separate *exponentially*:
`|Δ(t)| ≈ Δ₀ · e^{λt}`. Precision sets how far you can predict, but it can never
make a chaotic system predictable forever.
"""),
    md("## The setup"),
    code(BOOTSTRAP),
    code("""
def logistic(r, x0, n):
    x = np.empty(n)
    x[0] = x0
    for i in range(1, n):
        x[i] = r * x[i - 1] * (1.0 - x[i - 1])
    return x

r = 4.0                     # fully chaotic; Lyapunov exponent = ln 2
n = 60
x0 = 0.3
perturb = 1e-16
"""),
    md("## The reality"),
    code("""
a = logistic(r, x0, n)
b = logistic(r, x0 + perturb, n)
sep = np.abs(a - b)
first_sat = np.argmax(sep > 1e-1)

fig, ax = plt.subplots(1, 2, figsize=(11, 4))

ax[0].plot(a, "-", label="x0 = 0.3")
ax[0].plot(b, "--", label=f"x0 + {perturb:g}")
ax[0].set_xlabel("iteration")
ax[0].set_ylabel("x")
ax[0].set_title("Two trajectories, indistinguishable at first")
ax[0].legend()

ax[1].semilogy(sep, "o", ms=3, label="|Δ|")
tt = np.arange(n)
ax[1].semilogy(tt, perturb * np.exp(np.log(2) * tt), "k--", lw=1, label="Δ0 · 2^t")
ax[1].axvline(first_sat, color="r", ls=":", lw=1)
ax[1].set_xlabel("iteration")
ax[1].set_ylabel("separation |Δ|")
ax[1].set_title(f"Exponential growth, saturated by t={first_sat}")
ax[1].legend()

fig.tight_layout()
fig.savefig(FIG / "04_chaos.png", bbox_inches="tight")
plt.show()

lam = np.polyfit(tt[2:first_sat], np.log(sep[2:first_sat]), 1)[0]
print(f"measured Lyapunov exponent = {lam:.4f}   (ln 2 = {np.log(2):.4f})")
print(f"halving the initial error buys only {np.log(2)/lam:.1f} more iterations of prediction")
"""),
    md("""
## The rule

- Chaotic systems **amplify** initial error; better precision buys only
  `log(Δ_tol/Δ₀) / λ` extra iterations — logarithmically, not linearly.
- Forecast skill has a hard horizon. Ensemble methods track the *distribution*,
  not the exact trajectory.
- Do not use a chaotic benchmark to claim a method is "more accurate"; measure
  statistics (invariant measures, Lyapunov exponents), not pointwise agreement.
"""),
    md("""
## Taking it further

- Lorenz (1963); Strogatz, *Nonlinear Dynamics and Chaos*, ch. 10.
- Lyapunov exponent λ; the logistic map at r=4 has λ = ln 2 exactly.
- Lyapunov time = 1/λ — the natural clock of predictability.
"""),
])


# ---------------------------------------------------------------------------
# 05. Energy drift
# ---------------------------------------------------------------------------
nb05 = notebook([
    md("""
# 5. Energy drift — `fp32` leaks, and Euler is not even close

**The lie.** *"Smaller `dt` or more bits makes any integrator fine."*

A harmonic oscillator has constant energy `E = ½(v² + x²)`. Watch three
integrators in double precision, then watch symplectic Verlet accumulate drift
when you drop to float32.
"""),
    md("## The setup"),
    code(BOOTSTRAP),
    code("""
def euler(dt, n, dtype):
    x, v = dtype(1.0), dtype(0.0)
    E = np.empty(n, dtype=np.float64)
    for i in range(n):
        E[i] = float(x) ** 2 / 2 + float(v) ** 2 / 2
        x, v = x + dt * v, v - dt * x
    return E

def rk4(dt, n, dtype):
    x, v = dtype(1.0), dtype(0.0)
    E = np.empty(n, dtype=np.float64)
    for i in range(n):
        E[i] = float(x) ** 2 / 2 + float(v) ** 2 / 2
        k1x, k1v = v, -x
        k2x, k2v = v + dt/2*k1v, -(x + dt/2*k1x)
        k3x, k3v = v + dt/2*k2v, -(x + dt/2*k2x)
        k4x, k4v = v + dt*k3v,   -(x + dt*k3x)
        x = x + dt/6*(k1x + 2*k2x + 2*k3x + k4x)
        v = v + dt/6*(k1v + 2*k2v + 2*k3v + k4v)
    return E

def verlet(dt, n, dtype):
    x, v = dtype(1.0), dtype(0.0)
    E = np.empty(n, dtype=np.float64)
    a = -x
    for i in range(n):
        E[i] = float(x) ** 2 / 2 + float(v) ** 2 / 2
        v_half = v + dt/2 * a
        x = x + dt * v_half
        a = -x
        v = v_half + dt/2 * a
    return E
"""),
    md("## The reality"),
    code("""
dt, n = 0.05, 40000
E0 = 0.5

fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))

for name, fn, style in [("Euler", euler, "-"), ("RK4", rk4, "--"), ("Verlet", verlet, ":")]:
    E = fn(dt, n, np.float64)
    ax[0].plot(np.arange(n) * dt, (E - E0) / E0, style, lw=1.4, label=name)

ax[0].set_xlabel("time")
ax[0].set_ylabel("relative energy error (E - E0)/E0")
ax[0].set_title("Same dt, double precision")
ax[0].legend()

for name, fn, style in [("Verlet fp64", np.float64, "-"), ("Verlet fp32", np.float32, "-")]:
    E = verlet(dt, n, fn)
    ax[1].plot(np.arange(n) * dt, (E - E0) / E0, style, lw=1.2, label=name)

ax[1].set_xlabel("time")
ax[1].set_ylabel("relative energy error")
ax[1].set_title("Symplectic integrator: fp32 vs fp64")
ax[1].legend()

fig.tight_layout()
fig.savefig(FIG / "05_energy_drift.png", bbox_inches="tight")
plt.show()

for name, fn in [("Euler", euler), ("RK4", rk4), ("Verlet", verlet)]:
    e = (fn(dt, n, np.float64) - E0) / E0
    print(f"{name:7s} final |drift| = {abs(e[-1]):.3e}   max |drift| = {abs(e).max():.3e}")
"""),
    md("""
## The rule

- **Explicit Euler is unconditionally wrong for Hamiltonian systems** — energy
  grows without bound. It is not a "small dt" problem.
- **Symplectic methods (Verlet / leapfrog / Störmer) keep energy bounded** — it
  oscillates but does not drift, because they preserve the geometry.
- Precision is separate from *method*: symplectic + float32 still beats
  non-symplectic + float64 for long-time energy behaviour, but accumulate enough
  steps and float32's coarser rounding shows up as slow drift. Choose the method
  for structure, the precision for duration.
"""),
    md("""
## Taking it further

- Hairer, Lubich & Wanner, *Geometric Numerical Integration* — why symplectic.
- Leapfrog/Verlet is the default for molecular dynamics; forward Euler never is.
- This is the numerical-analysis face of "structure-preserving algorithms."
"""),
])


def main():
    OUT.mkdir(exist_ok=True)
    for name, nb in [
        ("00_representation", nb00),
        ("01_sum_order", nb01),
        ("02_cancellation", nb02),
        ("03_non_associativity", nb03),
        ("04_chaos", nb04),
        ("05_energy_drift", nb05),
    ]:
        path = OUT / f"{name}.ipynb"
        nbf.write(nb, path)
        print("wrote", path)


if __name__ == "__main__":
    main()
