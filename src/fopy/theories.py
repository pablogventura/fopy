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


_MAX_FUNCTION_TABLES = 4096
_MAX_TOTAL_STRUCTURES = 65536


def _function_table_domains(
    universe: list[int],
    arity: int,
) -> list[dict[tuple[int, ...], int] | int]:
    """Enumerate all function interpretations on *universe* for symbol arity *arity*."""
    n = len(universe)
    if arity == 0:
        return list(universe)
    inputs = list(product(universe, repeat=arity))
    domain_size = len(inputs)
    total = n**domain_size
    if total > _MAX_FUNCTION_TABLES:
        msg = (
            f"Cannot enumerate arity-{arity} functions on |U|={n}: "
            f"{total} tables exceed cap {_MAX_FUNCTION_TABLES}."
        )
        raise ValueError(msg)
    tables: list[dict[tuple[int, ...], int]] = []
    for code in range(total):
        table: dict[tuple[int, ...], int] = {}
        for idx, args in enumerate(inputs):
            output_idx = (code // (n**idx)) % n
            table[args] = universe[output_idx]
        tables.append(table)
    return cast(list[dict[tuple[int, ...], int] | int], tables)


def _structure_domains(
    signature: Signature,
    universe: list[int],
    *,
    max_relations: int,
) -> tuple[list[str], list[list[Any]], list[str], list[list[frozenset[tuple[int, ...]]]]]:
    """Build Cartesian domains for function and relation symbols."""
    fn_names = sorted(signature.functions)
    rel_names = list(signature.relations.keys())
    if len(rel_names) > max_relations:
        raise ValueError("Too many relation symbols for brute-force enumeration")
    fn_domains = [_function_table_domains(universe, signature.functions[name]) for name in fn_names]
    rel_domains = [_relation_powersets(universe, signature.relations[name]) for name in rel_names]
    total = 1
    for domain in fn_domains + rel_domains:
        total *= len(domain)
    if total > _MAX_TOTAL_STRUCTURES:
        msg = f"Cannot enumerate structures: {total} candidates exceed cap {_MAX_TOTAL_STRUCTURES}."
        raise ValueError(msg)
    return fn_names, fn_domains, rel_names, rel_domains


def _iter_structures(
    signature: Signature,
    universe: list[int],
    *,
    max_relations: int = 2,
) -> Iterator[Structure]:
    """Yield every structure of size ``len(universe)`` matching *signature* tables."""
    fn_names, fn_domains, rel_names, rel_domains = _structure_domains(
        signature,
        universe,
        max_relations=max_relations,
    )
    fn_combos = product(*fn_domains) if fn_domains else [()]
    rel_combos = product(*rel_domains) if rel_domains else [()]
    for fn_combo in fn_combos:
        functions = {name: fn_combo[i] for i, name in enumerate(fn_names)}
        for rel_combo in rel_combos:
            relations = {name: set(rel_combo[i]) for i, name in enumerate(rel_names)}
            yield Structure.from_tables(
                signature,
                universe,
                functions=cast(
                    dict[str, dict[tuple[Any, ...], Any] | Any],
                    functions,
                ),
                relations=cast(
                    Mapping[str, set[tuple[Any, ...]] | dict[tuple[Any, ...], bool]],
                    relations,
                ),
            )


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

        Only relation symbols with arity ≤ 2 are enumerated; function symbols are
        supported when the total search space stays below internal caps.
        Intended for small ``n`` (≤ 3).

        Args:
            n: Universe cardinality.
            max_relations: Cap on relation symbols considered during enumeration.

        Yields:
            Structures of size ``n`` satisfying every axiom.

        Raises:
            ValueError: If ``n > 3``, too many relation symbols, or enumeration explodes.
        """
        if n < 1:
            return
        if n > 3:
            raise ValueError("models_of_cardinality supports n <= 3 only")

        universe = list(range(n))
        try:
            structures = _iter_structures(
                self.signature,
                universe,
                max_relations=max_relations,
            )
        except ValueError:
            raise
        for structure in structures:
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
            ValueError: When ``n > 3`` or enumeration explodes.
        """
        if n < 1:
            return None
        if n > 3:
            raise ValueError("finite_counterexample supports n <= 3 only")
        universe = list(range(n))
        for structure in _iter_structures(self.signature, universe):
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

    def free_algebra_generators(self, n: int, *, max_depth: int = 2) -> Structure:
        """Compute a bounded free term algebra on ``n`` generators.

        Closes the signature under term formation up to *max_depth* and checks
        that all variety axioms hold. Supports ``1 <= n <= 3`` and functional
        signatures only.

        Args:
            n: Number of free generators.
            max_depth: Maximum term depth when closing under operations.

        Returns:
            Structure whose universe is term indices ``0 .. |T|-1``.

        Raises:
            ValueError: When parameters are out of bounds or axioms fail.
            NotImplementedError: When relation symbols are present.
        """
        from fopy.theory_free_algebra import free_algebra_for_variety

        return free_algebra_for_variety(
            self.signature,
            self.axioms,
            n,
            max_depth=max_depth,
        )


Theory = Variety
