# AGENTS.md — fopy

Guide for coding agents working in this repo. See [README.md](README.md) for user-facing docs.

## Stack

- **Python** ≥3.10 (CI: 3.10–3.12), **setuptools** (`src/` layout: `src/fopy/`)
- **Core**: pure Python, no runtime deps
- **Optional**: `numpy`, `matplotlib` (`[draw]` extra)
- **Dev**: `pytest`, `pytest-cov`, `ruff`, `mypy`, `hypothesis`
- **Docs**: `mkdocs`, `mkdocs-material`, `mkdocstrings` (`[docs]` extra)
- **CI**: GitHub Actions (`.github/workflows/ci.yml`) — tests + `mkdocs build --strict`
- **Agent rules**: `.cursor/rules/static-analysis.mdc`, `.cursor/rules/docstrings-manual.mdc`, `.cursor/rules/type-annotations.mdc`, `.cursor/rules/docs-autogen.mdc`
- **License**: MIT

## Important commands

```bash
# install (local dev)
pip install -e ".[dev,draw]"

# lint + format + types (CI)
ruff check src tests
ruff format --check src tests    # apply: ruff format src tests
mypy src/fopy

# tests — full local check (matches dev workflow)
pytest tests/ -m "not slow" --cov=fopy --cov-report=term-missing

# tests — as in CI (split jobs)
pytest tests/ -m "not slow and not finite" --cov=fopy --cov-fail-under=85
pytest tests/ -m "finite and not slow" --cov=fopy.finite --cov-fail-under=70

# API docs (from docstrings; CI gate)
pip install -e ".[docs,draw]"
mkdocs build --strict
mkdocs serve   # http://127.0.0.1:8000

# quick / targeted
pytest tests/test_core.py -q
pytest -m draw          # needs matplotlib
pytest -m finite
python scripts/demo_fo.py

# Hasse examples CLI
python -m fopy.draw
# or: fopy-draw
```

Not detected: `make`, `tox`, Docker, migrations, build/publish to PyPI.

## Project layout

| Path | Purpose |
|------|---------|
| `src/fopy/` | Public API (`import fopy as fo`) |
| `src/fopy/core/` | `Basic` AST base, `walk`/`transform` |
| `src/fopy/formulas.py`, `terms.py`, `symbols.py`, `semantics.py`, `transform.py` | Symbolic FO layer |
| `src/fopy/builders/` | `Structure` builders (covers, Cayley, catalog B₂/M₃/N₅…) |
| `src/fopy/parse/` | `parse_formula`, `parse_model` (`.model` format) |
| `src/fopy/printing/` | `sstr`, `pprint`, `latex` |
| `src/fopy/finite/` | Finite models, splitting, **HIT** open definability |
| `src/fopy/draw/` | Hasse layout (Freese/LatDraw-style), SVG render |
| `tests/` | pytest suite; `tests/fixtures/*.model` for regression |
| `docs/design/` | ADRs (HIT vs constellations, Hasse, builders) |
| `scripts/` | `demo_fo.py` — manual FO demo |
| `todo/` | Future vision notes (not part of v0.1 scope) |

## Architecture notes

- **Two layers**: (1) symbolic `Structure` + FO formulas; (2) `fopy.finite.Model` for algorithms on integers/universe tables.
- **Open definability**: use `fopy.finite.is_open_definable` (splitting + HIT). Do **not** port constellation/Minion from `definability`.
- **`.model` parser**: OpenDefAlgSplitting format; `eq(x,y)` not `==`.
- **`draw`**: optional extra; keep core importable without numpy/matplotlib.

## Conventions

- **Language**: English for code, docstrings, tests, errors, and docs.
- **Docstrings**: Google style, **very explanatory** (manual is generated from source); see `.cursor/rules/docstrings-manual.mdc`. Build API HTML with `pdoc -o docs/api fopy --docformat google`.
- **Types**: every function/method in `src/fopy/` fully annotated; `mypy src/fopy` must pass (`disallow_untyped_defs`). See `.cursor/rules/type-annotations.mdc`.
- **Style**: `ruff` lint + format, `mypy` on `src/fopy` only, line length 100, target Python 3.10.
- **Scope**: minimal diffs; match existing patterns; avoid drive-by refactors.
- **Commits**: not automated here; use conventional commits if asked (`feat`, `fix`, `test`, …).
- **No PyPI** yet — local editable install only.

## Tests

- Location: `tests/test_*.py`, shared fixtures in `tests/conftest.py`.
- Run one file: `pytest tests/test_finite.py -q`
- Markers: `@pytest.mark.draw`, `@pytest.mark.finite`, `@pytest.mark.slow` (reserved; CI excludes `slow`).
- **Do not** add tests that exhaustively run HIT, synthesis, homomorphism search, congruence/subalgebra enumeration, or full `.model` catalog batches. Those APIs are exponential or worse; test only on **tiny** curated fixtures (`|U| ≤ 4`) or unit-test structure without calling the heavy kernel.
- **Coverage**: `fail_under = 85` for core (`pyproject.toml`; `omit`: `hit`, some `draw` internals). Finite job: **70%** on `fopy.finite` in CI.
- Add regression `.model` fixtures under `tests/fixtures/` when touching `parse/model.py` or `finite/`.

## Do not

- Add constellation/Minion definability or new heavy runtime deps without explicit request.
- Break `import fopy` when `[draw]` is not installed.
- Delete or weaken tests to green the suite.
- Disable ruff/mypy/coverage gates without justification.
- Commit secrets, reformat unrelated files, or change public API surface casually.
- Treat `todo/` as implementation backlog unless Pablo asks.
- Add AI attribution in code, commits, or docs unless Pablo asks.

## Further reading

- [README.md](README.md) — quick start
- [.cursor/rules/static-analysis.mdc](.cursor/rules/static-analysis.mdc) — lint/type gates
- [docs/design/001-hit-definability.md](docs/design/001-hit-definability.md) — why HIT, not constellations
- [docs/design/002-hasse-layout.md](docs/design/002-hasse-layout.md) — draw module
- [docs/design/003-builders.md](docs/design/003-builders.md) — structure builders
