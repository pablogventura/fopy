# ADR 004: explain_definibility and ExplainReport

## Status

Accepted

## Context

Open definability is decided by `fopy.finite.is_open_definable` (HIT + splitting).
Researchers need human-readable explanations and offline-verifiable certificates,
not only boolean answers.

## Decision

- Add `explain_definability(model, target, *, fragment="qf") -> ExplainReport` in
  `fopy.finite.explain`, exported from `fopy.finite`.
- `ExplainReport` wraps `DefinabilityResult`; same logical outcome as
  `is_open_definable`.
- Supported fragments (aliases): `"qf"`, `"open"`, `"quantifier-free"`.
  Other fragments raise `NotImplementedError`.
- `certificate()` returns JSON-serializable dict; `verify_certificate(cert, model)`
  recomputes the verdict offline.
- Formula minimality (`formula_minimal`, `min_term_depth`) is Phase 2 via
  `synthesize_defining_formula`.

## Consequences

- English default for `pretty()` and obstruction text.
- No new top-level package `fopy.definability`; lives under `fopy.finite`.
- Golden tests use hybrid asserts + EN snapshots under `tests/fixtures/expected/explain/`.
