# References

The canonical sources behind each lie. Read these after playing with the
notebooks — the notebooks show you *that* it happens, these explain *why*.

## Floating point, generally

- David Goldberg, **What Every Computer Scientist Should Know About
  Floating-Point Arithmetic**, *ACM Computing Surveys* 23(1), 1991.
  <https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html>
- IEEE 754-2019, *Standard for Floating-Point Arithmetic*.
- *What Every Programmer Should Know About Floating-Point Arithmetic* —
  <https://floating-point-gui.de/>

## Comparing and inspecting floats

- Bruce Dawson, **Comparing Floating Point Numbers, 2012 Edition**.
  <https://randomascii.wordpress.com/2012/02/25/comparing-floating-point-numbers-2012-edition/>
- Bruce Dawson, **Float Precision Revisited: Nine Digit Float Portability**.
  <https://randomascii.wordpress.com/2013/02/07/float-precision-revisited-nine-digit-float-portability/>

## Summation and accuracy

- W. Kahan, **Further Remarks on Reducing Truncation Errors**, 1965
  (compensated summation).
- Arnold Neumaier, **Rundungsfehleranalyse einiger Verfahren zur Summation
  endlicher Summen**, 1974.
- Nicholas Higham, **Accuracy and Stability of Numerical Algorithms**, 2nd ed.,
  SIAM. (Ch. 1 cancellation, ch. 4 summation.)
- Jonathan Shewchuk, **Adaptive Precision Floating-Point Arithmetic and Fast
  Robust Geometric Predicates**, 1997. (`math.fsum`-style exact summation.)

## Chaos and predictability

- Edward Lorenz, **Deterministic Nonperiodic Flow**, 1963.
- Steven Strogatz, **Nonlinear Dynamics and Chaos**, ch. 10.
- The logistic map at `r = 4` has Lyapunov exponent `λ = ln 2` exactly.

## Geometric integration

- Ernst Hairer, Christian Lubich, Gerhard Wanner, **Geometric Numerical
  Integration**, 2nd ed., Springer.
- Verlet / leapfrog / Störmer methods preserve the symplectic structure and keep
  energy bounded for Hamiltonian systems.

## Reproducibility in HPC

- James Demmel & Hong Diep Nguyen, **Parallel Reproducible Summation**, 2013.
- Michael Müller et al., **Reproducible Floating-Point Aggregation in
  RDBMS**.
