# Varieties (`fopy.theories`)

```python
from fopy import Variety, eq, symbols
from fopy.signature import Signature

x, y, z = symbols("x y z")
sig = Signature(functions={"f": 2})
V = Variety(
    signature=sig,
    axioms=[eq(x, y)],  # identities / axioms
)

# Finite model check (Structure or finite Model)
V.satisfies(my_model)

# Search for small counterexamples (n <= 3)
V.finite_counterexample(3)

# Compare on models of size 1..3
V.compare(other_variety)
```

`Theory` is an alias of `Variety`. `free_algebra_generators` is reserved for
future work and raises `NotImplementedError` with an explicit scope note.

See also [design/003-builders.md](../design/003-builders.md) for catalogued
finite structures.
