# ADR 010: FO definability via k-types

## Status

Accepted

## Decision

FO definability on finite models uses partition refinement by bounded FO types
(`fo_ktypes.py`), generalizing HIT (rank-0 term types). Witness formulas are
built from the final partition in the same pass.

Z3 may cross-check results in tests when `[solvers]` is installed.

## Consequences

`atomic_type` in explain uses `max_depth=1` by default for obstruction display.
