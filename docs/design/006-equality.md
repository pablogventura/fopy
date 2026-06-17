# ADR 006: Equality in two layers

## Status

Accepted

## Context

The symbolic FO layer and the finite open-term layer both use equality with different AST types.

## Decision

- **Symbolic**: `fopy.formulas.Eq` and `fo.eq(t1, t2)` with simplification `t = t → ⊤`.
- **Finite/open**: `fopy.finite.open_formulas` uses `eq` with `==` in string form; `.model` files require `eq(x,y)` syntax, not `==`.

## Consequences

- Parser rejects `==` in `.model` formula lines (OpenDefAlgSplitting compatibility).
- Bridge conversion preserves operation tables; equality is formula-level only.
