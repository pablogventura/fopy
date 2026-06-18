# Definability fragments

`fopy.finite` supports several logic fragments for **open definability** on finite
algebras (bounded universe sizes; see ADR
[009-fragments](../design/009-fragments.md)).

| Fragment | Aliases | Checker |
|----------|---------|---------|
| `qf` | `open`, `quantifier-free` | HIT (`is_open_definable`) |
| `pp` | positive primitive | `fragments.pp_ktypes` |
| `ep` | existential positive | `fragments.ep_ktypes` |
| `horn` | Horn clauses | `fragments.horn_ktypes` |
| `fo` | full FO (bounded k-types) | `fragments.fo_ktypes` |

## API

```python
from fopy.finite import check_definability, explain_definability, Definability

result = check_definability(model, "T0", fragment="pp")
report = Definability.explain(model, "T0", fragment="horn", max_synth_depth=2)
```

Certificates use `CERT_VERSION = 2` (v1 still accepted by `verify_certificate`).
