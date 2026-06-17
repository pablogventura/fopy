"""Finite first-order models."""

from __future__ import annotations

from dataclasses import dataclass, field

from fopy.finite.relops import Operation, Relation


@dataclass
class Model:
    universe: list[int]
    relations: dict[str, Relation] = field(default_factory=dict)
    operations: dict[str, Operation] = field(default_factory=dict)
    targets: dict[str, Relation] = field(default_factory=dict)

    @classmethod
    def new(
        cls,
        universe: list[int],
        relations: dict[str, Relation] | None = None,
        operations: dict[str, Operation] | None = None,
        targets: dict[str, Relation] | None = None,
    ) -> Model:
        u = sorted(universe)
        return cls(
            universe=u,
            relations=dict(relations or {}),
            operations=dict(operations or {}),
            targets=dict(targets or {}),
        )
