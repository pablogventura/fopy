# fopy documentation

**fopy** is symbolic first-order logic for Python: formulas, finite structures,
open definability (HIT), and explainable certificates.

The **API reference** below is generated automatically from docstrings in
`src/fopy/`. Edit docstrings in source code — not these Markdown stubs.

For a full usage guide in Spanish, see [README.md](https://github.com/pabloventura/fopy/blob/main/README.md) in the repository.

## Quick links

| Topic | Module |
|-------|--------|
| FO formulas & structures | [`fopy`](api/index.md) |
| `.model` files & HIT | [`fopy.finite`](api/finite.md) |
| `explain_definability` | [`fopy.finite.explain`](api/finite.md#fopy.finite.explain) |
| Standard examples | [`fopy.builders`](api/builders.md) |
| Hasse diagrams | [`fopy.draw`](api/draw.md) |
| Universal algebra | [`fopy.universal`](api/universal.md) |

## Build locally

```bash
pip install -e ".[docs]"
mkdocs build --strict
# output: site/
mkdocs serve  # http://127.0.0.1:8000
```
