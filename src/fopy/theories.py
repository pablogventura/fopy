"""First-order theories and equational varieties."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from itertools import combinations, product
from typing import Any, cast

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
class Variety:
    """Equational variety (closed first-order theory).

    Packages a signature with a list of axioms (identities). Supports brute-force
    enumeration of small models, comparison with other varieties, and search for
    finite counterexamples.

    Attributes:
        signature: Language signature.
        axioms: Generating formulas for the variety (identities).
    """

    signature: Signature
    axioms: list[Formula] = field(default_factory=list)

    def models_of_cardinality(self, n: int, *, max_relations: int = 2) -> Iterator[Structure]:
        """Brute-force generator of models of size ``n`` satisfying all axioms.

        Only relation symbols with arity ≤ 2 are enumerated; intended for small
        ``n`` (≤ 3).

        Args:
            n: Universe cardinality.
            max_relations: Cap on relation symbols considered during enumeration.

        Yields:
            Structures of size ``n`` satisfying every axiom.

        Raises:
            ValueError: If ``n > 3`` or too many relation symbols.
            NotImplementedError: If function symbols are present.
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
            structure = Structure.from_tables(
                self.signature,
                universe,
                relations=cast(
                    Mapping[str, set[tuple[Any, ...]] | dict[tuple[Any, ...], bool]],
                    relations,
                ),
            )
            if all(satisfy(ax, structure, {}) for ax in self.axioms):
                yield structure

    def satisfies(self, structure: object) -> bool:
        """Return whether *structure* is a model of all axioms.

        Accepts a symbolic :class:`~fopy.structures.Structure` or a finite
        :class:`~fopy.finite.models.Model` (bridged automatically).
        """
        from fopy.finite.models import Model
        from fopy.structures import Structure

        if isinstance(structure, Model):
            from fopy.bridge import from_finite_model

            structure = from_finite_model(structure)
        if not isinstance(structure, Structure):
            raise TypeError("structure must be a Structure or finite Model")
        return all(satisfy(ax, structure, {}) for ax in self.axioms)

    def entails(self, structure: Structure, formula: Formula) -> bool:
        """Check whether ``structure`` is a model of the theory and satisfies ``formula``."""
        if not all(satisfy(ax, structure, {}) for ax in self.axioms):
            return False
        return satisfy(formula, structure, {})

    def consequence(self, formula: Formula, n: int) -> bool:
        """Return whether every size-``n`` model of the axioms satisfies ``formula``."""
        return all(satisfy(formula, model, {}) for model in self.models_of_cardinality(n))

    @property
    def identities(self) -> list[Formula]:
        """Alias for :attr:`axioms` (equational basis)."""
        return self.axioms

    def finite_counterexample(self, n: int) -> Structure | None:
        """Return a size-``n`` structure violating some axiom, if one exists.

        Args:
            n: Universe cardinality (≤ 3).

        Returns:
            Counterexample structure, or ``None`` when all structures satisfy axioms.

        Raises:
            ValueError: When ``n > 3``.
            NotImplementedError: When function symbols prevent enumeration.
        """
        if n < 1:
            return None
        if n > 3:
            raise ValueError("finite_counterexample supports n <= 3 only")
        if self.signature.functions:
            raise NotImplementedError("Enumeration with function symbols is not implemented")
        universe = list(range(n))
        rel_names = list(self.signature.relations.keys())
        domains = [
            _relation_powersets(universe, self.signature.relations[name]) for name in rel_names
        ]
        for combo in product(*domains):
            relations = {name: set(combo[i]) for i, name in enumerate(rel_names)}
            structure = Structure.from_tables(
                self.signature,
                universe,
                relations=cast(
                    Mapping[str, set[tuple[Any, ...]] | dict[tuple[Any, ...], bool]],
                    relations,
                ),
            )
            if not all(satisfy(ax, structure, {}) for ax in self.axioms):
                return structure
        return None

    def compare(self, other: Variety) -> str:
        """Compare this variety with *other* on small finite models.

        Args:
            other: Second variety.

        Returns:
            ``"equal"``, ``"strict_subvariety"``, ``"strict_supervariety"``, or
            ``"incomparable"``.
        """
        if self.signature != other.signature:
            return "incomparable"
        if self._axiom_set() == other._axiom_set():
            return "equal"
        for n in (1, 2, 3):
            for model in self.models_of_cardinality(n):
                if not all(satisfy(ax, model, {}) for ax in other.axioms):
                    return "incomparable"
            for model in other.models_of_cardinality(n):
                if not all(satisfy(ax, model, {}) for ax in self.axioms):
                    return "incomparable"
        if len(self.axioms) <= len(other.axioms):
            return "strict_subvariety"
        return "strict_supervariety"

    def _axiom_set(self) -> frozenset[str]:
        return frozenset(repr(ax) for ax in self.axioms)

    def free_algebra_generators(self, n: int) -> Structure:
        """Compute the free algebra on ``n`` generators (not implemented).

        Args:
            n: Number of free generators.

        Raises:
            NotImplementedError: Always; finite free algebras are future work.
        """
        raise NotImplementedError(
            "free_algebra_generators is not implemented; "
            "finite free algebras require term enumeration beyond current scope"
        )


Theory = Variety
