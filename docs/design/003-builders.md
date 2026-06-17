# ADR 003: Builders for finite structures

## Status

Accepted

## Context

Users need quick ways to define standard examples (chains, B_n, M3, N5) and
custom structures from covers or Cayley tables.

## Decision

`fopy.builders` provides `from_covers`, `from_upper_covers`, `from_cayley`, a
catalog, and a fluent `StructureBuilder`.

## Consequences

- Builders produce `fopy.structures.Structure` for the symbolic FO layer.
- Finite `.model` files are parsed into `fopy.finite.Model` for HIT.
