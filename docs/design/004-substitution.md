# ADR 004: Capture-safe substitution

## Status

Accepted

## Context

FO substitution must avoid variable capture when replacing under binders.

## Decision

`substitute` and `subs` rename bound variables via fresh names before applying mappings under `ForAll`/`Exists`. `rename_bound` provides explicit alpha-renaming.

## Consequences

- Regression tests cover capture cases in `tests/test_transform.py`.
- Public API: `fo.substitute`, `fo.subs`, `fo.rename_bound`, `Formula.subs`.
