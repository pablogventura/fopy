"""First-order signatures."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Signature:
    """Language signature: function and relation symbols with arities."""

    functions: dict[str, int] = field(default_factory=dict)
    relations: dict[str, int] = field(default_factory=dict)

    def function(self, name: str) -> str:
        if name not in self.functions:
            raise KeyError(f"Unknown function symbol: {name}")
        return name

    def relation(self, name: str) -> str:
        if name not in self.relations:
            raise KeyError(f"Unknown relation symbol: {name}")
        return name

    def constant(self, name: str) -> str:
        if self.functions.get(name, -1) != 0:
            raise KeyError(f"Unknown constant symbol: {name}")
        return name

    def subtype(self, functions: list[str] | None = None, relations: list[str] | None = None) -> Signature:
        functions = functions or []
        relations = relations or []
        return Signature(
            functions={f: self.functions[f] for f in functions},
            relations={r: self.relations[r] for r in relations},
        )

    def __add__(self, other: Signature) -> Signature:
        merged_f = dict(self.functions)
        merged_f.update(other.functions)
        merged_r = dict(self.relations)
        merged_r.update(other.relations)
        return Signature(functions=merged_f, relations=merged_r)

    def __sub__(self, other: Signature) -> Signature:
        return Signature(
            functions={k: v for k, v in self.functions.items() if k not in other.functions},
            relations={k: v for k, v in self.relations.items() if k not in other.relations},
        )

    def is_subtype_of(self, other: Signature) -> bool:
        return all(
            k in other.functions and self.functions[k] == other.functions[k] for k in self.functions
        ) and all(
            k in other.relations and self.relations[k] == other.relations[k] for k in self.relations
        )
