# fopy

Symbolic **first-order logic** for Python — a SymPy-style library for building,
transforming, evaluating, and printing FO formulas and finite structures.

## Install (local development)

```bash
pip install -e ".[dev,draw]"
```

## Quick start

```python
import fopy as fo

sig = fo.Signature(functions={"f": 2, "c": 0}, relations={"R": 2, "P": 1})
x, y = fo.symbols("x", "y")
f, c = sig.function("f"), sig.constant("c")
R, P = sig.relation("R"), sig.relation("P")

phi = fo.forall(x, fo.exists(y, R(f(x, c), y) & P(y)))
print(phi.free_vars())
print(fo.latex(phi))

A = fo.builders.from_upper_covers([[1], []], names=["0", "1"])
```

## Hasse diagrams (Freese-style layout)

```bash
python -m fopy.draw
```

```python
from fopy.draw import draw_lattice, boolean_lattice
draw_lattice(boolean_lattice(2), filename="out/B2.svg")
```

## Open definability (splitting + HIT)

```python
from fopy.finite import is_open_definable
from fopy.parse import parse_model

model = parse_model("path/to/model.model")
result = is_open_definable(model, model.targets["T0"])
```

## Tests

```bash
pytest                    # core (+ doctests)
pytest -m draw            # visualization
pytest -m finite            # HIT / .model regression
pytest --cov=fopy --cov-report=term-missing
python scripts/demo_fo.py
```

## License

MIT
