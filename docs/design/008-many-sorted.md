# ADR 008: Many-sorted logic (lite)

## Status

Accepted

## Decision

- `Sort` names sorts; `DEFAULT_SORT = U` is implicit for legacy unisort code.
- `Variable` carries optional `sort`; `Signature` may list extra sorts.
- Single-sort structures and models remain the default path.

## Consequences

TPTP/TFF export gains sort annotations when multi-sort signatures are used.
