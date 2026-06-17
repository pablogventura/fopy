"""First-order theories."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations, product
from typing import Iterator

from fopy.formulas import Formula
from fopy.semantics import satisfy
from fopy.signature import Signature
from fopy.structures import Structure


def _relation_powersets(universe: list[int], arity: int) -> list[frozenset[tuple[int, ...]]]:
    tuples = list(product(universe, repeat=arity))
    subsets: list[frozenset[tuple[int, ...]]] = []
    for k in range(len(tuples) + 1):
        for combo in combinations(range(len(tuples)), k):
            subsets.append(frozenset(tuples[i] for i in combo))
    return subsets


@dataclass
class Theory:
    """Closed FO theory: signature plus axiom set."""

    signature: Signature
    axioms: list[Formula] = field(default_factory=list)

    def models_of_cardinality(self, n: int, *, max_relations: int = 2) -> Iterator[Structure]:
        """
        Brute-force generator of models of size ``n`` satisfying all axioms.

        Only relation symbols with arity ≤ 2 are enumerated; intended for small ``n`` (≤ 3).
        """
        if n < 1:
            return
        if n > 3:
            raise ValueError("models_of_cardinality supports n <= 3 only")
        if self.signature.functions:
            raise NotImplementedError("Enumeration with function symbols is not implemented")
        if len(self.signature.relations) > max_relations:
            raise ValueError("Too many relation symbols for brute-force enumeration")

        universe = list(range(n))
        rel_names = list(self.signature.relations.keys())
        domains = [
            _relation_powersets(universe, self.signature.relations[name]) for name in rel_names
        ]

        for combo in product(*domains):
            relations = {name: set(combo[i]) for i, name in enumerate(rel_names)}
            structure = Structure.from_tables(self.signature, universe, relations=relations)
            if all(satisfy(ax, structure, {}) for ax in self.axioms):
                yield structure

    def satisfies(self, structure: Structure, formula: Formula) -> bool:
        """True if ``structure`` satisfies all axioms and ``formula``."""
        return self.entails(structure, formula)

    def entails(self, structure: Structure, formula: Formula) -> bool:
        """Check whether ``structure`` is a model of the theory and satisfies ``formula``."""
        if not all(satisfy(ax, structure, {}) for ax in self.axioms):
            return False
        return satisfy(formula, structure, {})

    def consequence(self, formula: Formula, n: int) -> bool:
        """True if every model of size ``n`` satisfying axioms also satisfies ``formula``."""
        for model in self.models_of_cardinality(n):
            if not satisfy(formula, model, {}):
                return False
        return True
