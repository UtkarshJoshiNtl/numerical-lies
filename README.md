# Numerical Lies

A repo of floating-point failure cases made visible: chaotic divergence,
summation order changing the result, fp32 energy drift, cancellation, and
non-associativity. Every case is a small experiment with a plot.

## Purpose

Floating point does not behave like real numbers. This repo collects the
concrete, reproducible ways it bites — so the failure modes are learned once
instead of rediscovered in production.

## Planned cases

```
summation_order/      same data, different order, different answer
cancellation/         catastrophic cancellation in the quadratic formula
non_associativity/    (a + b) + c != a + (b + c)
chaotic_divergence/   tiny perturbation -> totally different trajectory
energy_drift/         fp32 vs fp64 drift in a conservative system
plotting/             scripts that turn each experiment into a figure
```

Status: folder skeleton and intent only. Code and figures to follow.
