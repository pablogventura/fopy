# Solvers (optional Z3)

Install the extra:

```bash
pip install 'fopy[solvers]'
```

## Formula export

```python
import fopy as fo

x = fo.symbols("x")
phi = fo.eq(x, x)
z3_expr = phi.to_z3()  # requires z3-solver
```

## SAT helpers

```python
from fopy.solvers import check_sat_smt, z3_available
```

Z3 is used for auxiliary verification and bounded SMT synthesis
(`fopy.finite.synthesis_smt`); definability kernels remain HIT / k-types in pure
Python.
