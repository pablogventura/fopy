# AGENTS.md — fopy

Guide for coding agents working in this repo. See [README.md](README.md) for user-facing docs.

## Stack

- **Python** ≥3.10 (CI: 3.10–3.12), **setuptools** (`src/` layout: `src/fopy/`)
- **Core**: pure Python, no runtime deps
- **Optional**: `numpy`, `matplotlib` (`[draw]` extra)
- **Dev**: `pytest`, `pytest-cov`, `ruff`, `mypy`, `hypothesis`
- **Docs**: `mkdocs`, `mkdocs-material`, `mkdocstrings` (`[docs]` extra)
- **Optional extras**: `[solvers]` (z3), `[viz]`, `[fast]` (numpy eval hooks), `[draw]` (matplotlib Hasse).
- **CI**: GitHub Actions jobs `test` (ruff + mypy + pytest core/finite), `docs`, `solvers`, `viz`.
- **Agent rules**: `.cursor/rules/static-analysis.mdc`, `.cursor/rules/docstrings-manual.mdc`, `.cursor/rules/type-annotations.mdc`, `.cursor/rules/docs-autogen.mdc`
- **License**: MIT

## Important commands

```bash
# install (local dev)
pip install -e ".[dev,draw]"        # default dev
pip install -e ".[dev,solvers]"     # Z3 tests
pip install -e ".[all]"

# lint + format + types (CI)
ruff check src tests
ruff format --check src tests    # apply: ruff format src tests
mypy src/fopy

# tests — full local check (matches dev workflow)
pytest tests/ -m "not slow" --cov=fopy --cov-report=term-missing

# tests — as in CI (split steps in test job)
pytest tests/ -m "not slow and not finite" --cov=fopy --cov-fail-under=85
pytest tests/ -m "finite and not slow" --cov=fopy.finite --cov-fail-under=70
pytest tests/ -m solvers -q       # CI solvers job (needs z3)
pytest tests/test_viz_exports.py -q   # CI viz job

# API docs (from docstrings; CI gate)
pip install -e ".[docs,draw]"
mkdocs build --strict
mkdocs serve   # http://127.0.0.1:8000

# quick / targeted
pytest tests/test_core.py -q
pytest tests/test_remaining_gaps.py -q
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
| `src/fopy/api.py` | Notebook-style aliases (`Function`, `Relation`, `Vars`) |
| `src/fopy/theories.py`, `theory_free_algebra.py` | `Variety` / `Theory`, bounded free term algebras |
| `src/fopy/bridge.py`, `sorts.py` | `Structure` ↔ `Model` bridge; many-sorted lite |
| `src/fopy/formulas.py`, `terms.py`, `symbols.py`, `semantics.py`, `transform.py` | Symbolic FO layer (incl. TPTP/TFF export) |
| `src/fopy/builders/` | `Structure` builders (covers, Cayley, catalog B₂/M₃/N₅…) |
| `src/fopy/parse/` | `parse_formula`, `parse_model` (`.model` format) |
| `src/fopy/printing/` | `sstr`, `pprint`, `latex` |
| `src/fopy/finite/` | Finite models, HIT, **multi-fragment definability** (`fragments/`), `explain_definability` |
| `src/fopy/finite/fragments/` | Bounded k-type checkers: `pp`, `ep`, `horn`, `fo` |
| `src/fopy/solvers/` | Optional Z3 (`to_z3`, `prove_formula`, `check_sat_smt`) |
| `src/fopy/universal/` | Congruences, subalgebras, `CongruenceLattice.draw()` |
| `src/fopy/draw/` | Hasse layout (Freese/LatDraw-style), SVG render |
| `tests/` | pytest suite; `tests/fixtures/*.model` for regression |
| `docs/design/` | ADRs (HIT vs constellations, Hasse, builders) |
| `scripts/` | `demo_fo.py` — manual FO demo |
| `todo/` | Future vision notes (not part of v0.1 scope) |

## Architecture notes

- **Two layers**: (1) symbolic `Structure` + FO formulas; (2) `fopy.finite.Model` for algorithms on integers/universe tables.
- **Open definability**: `fopy.finite.check_definability` / `Definability.explain` — fragments `qf` (HIT), `pp`, `ep`, `horn`, `fo` (k-types, small `|U|`). Legacy alias: `is_open_definable` (= `qf`).
- **Eval cache / fast paths**: `eval_cache`, `eval_fast` (numpy/bitsets when `[fast]` or draw deps present).
- **Theories**: `Variety.models_of_cardinality` brute-forces small models (n ≤ 3, capped); `free_algebra_generators` uses `theory_free_algebra`.
- **Hash-cons**: `fopy.core.hashcons.enable_hashcons()` interns `Variable`, `Apply`, `Constant`, `Atom`, `Eq`.
- **`.model` parser**: OpenDefAlgSplitting format; `eq(x,y)` not `==`.
- **`draw`**: optional extra; keep core importable without numpy/matplotlib.

## Conventions

- **Language**: English for code, docstrings, tests, errors, and docs.
- **Docstrings**: Google style; API docs via **mkdocs** + mkdocstrings (see `.cursor/rules/docstrings-manual.mdc`, `.cursor/rules/docs-autogen.mdc`).
- **Types**: every function/method in `src/fopy/` fully annotated; `mypy src/fopy` must pass (`disallow_untyped_defs`). See `.cursor/rules/type-annotations.mdc`.
- **Style**: `ruff` lint + format, `mypy` on `src/fopy` only, line length 100, target Python 3.10. Per-file: `N802` in `api.py`; `RUF001`/`RUF002` for logic Unicode.
- **Scope**: minimal diffs; match existing patterns; avoid drive-by refactors.
- **Commits**: not automated here; use conventional commits if asked (`feat`, `fix`, `test`, …).
- **No PyPI** yet — local editable install only.

## Tests

- Location: `tests/test_*.py`, shared fixtures in `tests/conftest.py`.
- Run one file: `pytest tests/test_finite.py -q`
- Markers: `@pytest.mark.draw`, `@pytest.mark.finite`, `@pytest.mark.solvers`, `@pytest.mark.viz`, `@pytest.mark.slow` (reserved; CI excludes `slow`).
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
- [docs/design/001-hit-definability.md](docs/design/001-hit-definability.md) — HIT vs constellations
