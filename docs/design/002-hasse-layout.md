# ADR 002: Hasse layout (Freese / LatDraw)

## Status

Accepted

## Context

Lattice and poset diagrams need readable Hasse layouts. Freese's algorithm
(rank layers, 3D coordinates, force simulation, best 2D projection) is the
standard approach in LatDraw.

## Decision

`fopy.draw` implements ranking, 3D layout, force refinement, projection search,
and matplotlib/SVG rendering as an optional extra (`pip install -e ".[draw]"`).

## Consequences

- Core `fopy` has no numpy/matplotlib dependency.
- `draw_structure` bridges `fopy.structures.Structure` with a binary order relation.
