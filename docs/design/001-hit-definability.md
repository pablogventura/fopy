# ADR 001: Open definability via HIT

## Status

Accepted

## Context

Open definability of a target relation in a finite algebra can be decided by
several algorithms. The legacy `definability` project uses constellation search
with external solvers (Minion). OpenDefAlgSplitting uses pattern splitting plus
the HIT term-tree search.

## Decision

`fopy.finite.is_open_definable` uses **pattern splitting** (`split_targets`) and
**HIT** (`is_open_def`) ported from OpenDefAlgSplitting. We do not port
constellation/Minion code.

## Consequences

- Regression tests use `.model` fixtures from OpenDefAlgSplitting.
- The finite layer uses its own open-term AST (`fopy.finite.open_formulas`).
- FO symbolic layer (`fopy.formulas`) remains independent for general use.
