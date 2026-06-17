# AGENTS.md — fopy

Guide for coding agents working in this repo. See [README.md](README.md) for user-facing docs.

## Stack

- **Python** ≥3.10, **setuptools** (`src/` layout: `src/fopy/`)
- **Core**: pure Python, no runtime deps
- **Optional**: `numpy`, `matplotlib` (`[draw]` extra)
- **Dev**: `pytest`, `pytest-cov`, `ruff`, `hypothesis`
- **CI**: GitHub Actions (`.github/workflows/ci.yml`)
- **License**: MIT

## Important commands

```bash
# install (local dev)
pip install -e ".[dev,draw]"

# lint (CI)
ruff check src tests

# tests (CI)
pytest tests/ -m "not slow" --cov=fopy --cov-report=term-missing

# quick / targeted
pytest tests/test_core.py -q
pytest -m draw          # needs matplotlib
pytest -m finite

# Hasse examples CLI
python -m fopy.draw
# or: fopy-draw
```

Not detected: `make`, `mypy`/pyright, `tox`, Docker, migrations.

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

## Architecture notes

- **Two layers**: (1) symbolic `Structure` + FO formulas; (2) `fopy.finite.Model` for algorithms on integers/universe tables.
- **Open definability**: use `fopy.finite.is_open_definable` (splitting + HIT). Do **not** port constellation/Minion from `definability`.
- **`.model` parser**: OpenDefAlgSplitting format; `eq(x,y)` not `==`.
- **`draw`**: optional extra; keep core importable without numpy/matplotlib.

## Conventions

- **Language**: English for code, docstrings, tests, errors, and docs.
- **Style**: `ruff`, line length 100, target Python 3.10.
- **Scope**: minimal diffs; match existing patterns; avoid drive-by refactors.
- **Commits**: not automated here; use conventional commits if asked (`feat`, `fix`, `test`, …).
- **No PyPI** yet — local editable install only.

## Tests

- Location: `tests/test_*.py`, shared fixtures in `tests/conftest.py`.
- Run one file: `pytest tests/test_finite.py -q`
- Markers: `@pytest.mark.draw`, `@pytest.mark.finite`, `@pytest.mark.slow` (CI excludes `slow`).
- **Coverage**: `fail_under = 85` for core (see `omit` in `pyproject.toml`: `hit`, draw internals). Finite: `pytest -m finite` with separate threshold in CI.
- Add regression `.model` fixtures under `tests/fixtures/` when touching `parse/model.py` or `finite/`.

## Do not

- Add constellation/Minion definability or new heavy runtime deps without explicit request.
- Break `import fopy` when `[draw]` is not installed.
- Delete or weaken tests to green the suite.
- Disable ruff/coverage gates without justification.
- Commit secrets, reformat unrelated files, or change public API surface casually.
- Add AI attribution in code, commits, or docs unless Pablo asks.

## Further reading

- [README.md](README.md) — quick start
- [docs/design/001-hit-definability.md](docs/design/001-hit-definability.md) — why HIT, not constellations
- [docs/design/002-hasse-layout.md](docs/design/002-hasse-layout.md) — draw module
- [docs/design/003-builders.md](docs/design/003-builders.md) — structure builders
