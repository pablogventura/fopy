# ADR 005: Force simulation in Hasse layout

## Status

Accepted

## Context

3D node positions need refinement after rank-based initialization to reduce edge crossings and overlap.

## Decision

`fopy.draw.forces.simulate_forces` applies repulsive and attractive forces on cover edges for a fixed number of iterations with deterministic seed.

## Consequences

- Layout quality depends on `seed`; tests use fixed seeds.
- Force parameters live in `forces.py`; changes require visual/regression review.
