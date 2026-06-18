# ADR 007: Complexity bounds for exponential APIs

## Status

Accepted

## Decision

Every algorithm exponential in `|U|`, arity, or formula depth documents explicit
thresholds and fails gracefully (`ValueError`, truncated result, or
`NotImplementedError` with guidance).

Defaults: `|U| ≤ 8` for FO model checking; `|U|^arity ≤ 256` for tuple partitions;
`|U| ≤ 6` for homomorphism enumeration; `max_k ≤ |U|` for FO k-types.

## Consequences

Tests use only tiny fixtures. No full `.model` catalog batch in CI.
