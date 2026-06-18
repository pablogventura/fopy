# ADR 009: Definability fragments

## Status

Accepted

## Decision

`check_definability(model, target, fragment=...)` routes:

| Fragment | Kernel |
|----------|--------|
| `qf` / `open` | HIT (`is_open_definable`) |
| `pp`, `ep`, `horn`, `fo` | k-type partition refiners in `fopy.finite.fragments` |

Certificates remain offline-verifiable; Z3 is auxiliary only.

## Consequences

`explain_definability` supports all listed fragments via `normalize_fragment`.
