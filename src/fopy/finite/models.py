"""Finite first-order models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from fopy.finite.relops import Operation, Relation

if TYPE_CHECKING:
    from fopy.finite.explain import ExplainReport
    from fopy.finite.open_formulas import Formula, Variable
    from fopy.formulas import Formula as SymbolicFormula
    from fopy.structures import Structure
    from fopy.symbols import Variable as SymbolicVariable
    from fopy.universal import Congruence
    from fopy.universal.lattice_views import CongruenceLattice, SubalgebraLattice


@dataclass
class Model:
    """Finite first-order structure with named relations and operations.

    Attributes:
        universe: Sorted list of domain elements (integers).
        relations: Named base relations keyed by symbol.
        operations: Named operations keyed by symbol.
        targets: Target relations for definability queries (may overlap with
            ``relations``).
    """

    universe: list[int]
    relations: dict[str, Relation] = field(default_factory=dict)
    operations: dict[str, Operation] = field(default_factory=dict)
    targets: dict[str, Relation] = field(default_factory=dict)

    def models(self, formula: Formula) -> bool:
        """Return whether *formula* is valid on this model (universal satisfaction)."""
        from fopy.finite.model_checking import models as _models

        return _models(self, formula)

    def counterexample(self, formula: Formula) -> dict[Variable, int] | None:
        """Return one assignment falsifying *formula*, or ``None`` if none exists."""
        from fopy.finite.model_checking import counterexample as _ce

        return _ce(self, formula)

    def satisfying_assignments(self, formula: Formula) -> list[dict]:
        """List all variable assignments that satisfy *formula* on this model."""
        from fopy.finite.model_checking import satisfying_assignments as _sa

        return _sa(self, formula)

    def models_symbolic(
        self,
        formula: SymbolicFormula,
        *,
        max_universe: int = 8,
    ) -> bool:
        """Return whether a symbolic FO formula is valid on this model.

        Uses :func:`~fopy.finite.symbolic_model_checking.models_symbolic` to
        evaluate full first-order formulas (including quantifiers) after
        bridging to a symbolic :class:`~fopy.structures.Structure`.

        Args:
            formula: Formula from :mod:`fopy.formulas`.
            max_universe: Abort when ``|U|`` exceeds this bound.

        Returns:
            ``True`` iff the formula holds under the universal reading of
            free variables (see :func:`~fopy.finite.symbolic_model_checking.models_symbolic`).
        """
        from fopy.finite.symbolic_model_checking import models_symbolic as _models_symbolic

        return _models_symbolic(self, formula, max_universe=max_universe)

    def counterexample_symbolic(
        self,
        formula: SymbolicFormula,
        *,
        max_universe: int = 8,
    ) -> dict[SymbolicVariable, int] | None:
        """Return an assignment falsifying a symbolic FO formula, if any."""
        from fopy.finite.symbolic_model_checking import counterexample_symbolic as _ce

        result = _ce(self, formula, max_universe=max_universe)
        if result is None or isinstance(result, dict):
            return result
        return result.assignment

    def satisfying_assignments_symbolic(
        self,
        formula: SymbolicFormula,
        *,
        max_universe: int = 8,
    ) -> list[dict]:
        """List assignments satisfying a symbolic FO formula on this model."""
        from fopy.finite.symbolic_model_checking import (
            satisfying_assignments_symbolic as _sa,
        )

        return _sa(self, formula, max_universe=max_universe)

    def congruence_lattice(self) -> CongruenceLattice:
        """List all congruences on this algebra.

        See :func:`~fopy.universal.congruence_lattice`.
        """
        from fopy.universal import congruence_lattice

        return congruence_lattice(self)

    def subalgebra_lattice(self) -> SubalgebraLattice:
        """List all subuniverses closed under the operations of this model.

        See :func:`~fopy.universal.subalgebra_lattice`.
        """
        from fopy.universal import subalgebra_lattice

        return subalgebra_lattice(self)

    def is_subdirectly_irreducible(self) -> bool:
        """Return whether this algebra is subdirectly irreducible.

        See :func:`~fopy.universal.is_subdirectly_irreducible`.
        """
        from fopy.universal import is_subdirectly_irreducible

        return is_subdirectly_irreducible(self)

    def direct_product(self, other: Model) -> Model:
        """Form the direct product with another finite algebra.

        See :func:`~fopy.finite.products.direct_product`.
        """
        from fopy.finite.products import direct_product

        return direct_product(self, other)

    def draw_congruences(self, *, filename: str | None = None) -> object:
        """Draw the Hasse diagram of the congruence lattice.

        Requires the optional ``draw`` extra (``matplotlib``).

        Args:
            filename: When set, write SVG or PNG to this path.

        Returns:
            Matplotlib axes or path from the renderer.

        Raises:
            ImportError: If ``fopy[draw]`` is not installed.
        """
        try:
            from fopy.universal.draw import draw_congruence_lattice
        except ImportError as exc:
            raise ImportError("Drawing requires the draw extra: pip install 'fopy[draw]'") from exc
        return draw_congruence_lattice(self, filename=filename)

    def draw_subalgebras(self, *, filename: str | None = None) -> object:
        """Draw the Hasse diagram of the subalgebra lattice.

        Requires the optional ``draw`` extra (``matplotlib``).

        Args:
            filename: When set, write SVG or PNG to this path.

        Returns:
            Matplotlib axes or path from the renderer.

        Raises:
            ImportError: If ``fopy[draw]`` is not installed.
        """
        try:
            from fopy.universal.draw import draw_subalgebra_lattice
        except ImportError as exc:
            raise ImportError("Drawing requires the draw extra: pip install 'fopy[draw]'") from exc
        return draw_subalgebra_lattice(self, filename=filename)

    def hasse_diagram(
        self,
        relation: str = "leq",
        *,
        filename: str | None = None,
    ) -> object:
        """Draw a Hasse diagram for an order relation on this model.

        Bridges to a symbolic structure and calls
        :func:`~fopy.draw.draw_structure` on the named relation (default
        ``"leq"``). Requires the optional ``draw`` extra.

        Args:
            relation: Binary relation symbol defining the partial order.
            filename: When set, write SVG or PNG to this path.

        Returns:
            Matplotlib axes or output path.

        Raises:
            ImportError: If ``fopy[draw]`` is not installed.
            KeyError: If *relation* is absent from the model signature.
        """
        try:
            from fopy.bridge import from_finite_model
            from fopy.draw import draw_structure
        except ImportError as exc:
            raise ImportError("Drawing requires the draw extra: pip install 'fopy[draw]'") from exc
        if relation not in self.relations:
            raise KeyError(f"Relation {relation!r} not in model")
        return draw_structure(from_finite_model(self), relation=relation, filename=filename)

    def term_functions(self, max_depth: int) -> dict[int, set[tuple[int, ...]]]:
        """Enumerate term functions up to the given term depth.

        See :func:`~fopy.finite.algebra.term_functions`.
        """
        from fopy.finite.algebra import term_functions

        return term_functions(self, max_depth)

    def subalgebra_generated_by(self, generators: list[int]) -> set[int]:
        """Return the subuniverse generated by *generators* under all operations.

        See :func:`~fopy.finite.algebra.subalgebra_generated_by`.
        """
        from fopy.finite.algebra import subalgebra_generated_by

        return subalgebra_generated_by(self, generators)

    def show_tables(self) -> str:
        """Return a textual dump of operation and relation tables (notebook-friendly)."""
        lines = [f"universe: {self.universe}"]
        for sym in sorted(self.operations):
            op = self.operations[sym]
            lines.append(f"operation {sym} (arity {op.arity}):")
            for args, val in sorted(op.op.items()):
                lines.append(f"  {args} -> {val}")
        for sym in sorted(self.relations):
            rel = self.relations[sym]
            lines.append(f"relation {sym}: {sorted(rel.r)}")
        return "\n".join(lines)

    @classmethod
    def new(
        cls,
        universe: list[int],
        relations: dict[str, Relation] | None = None,
        operations: dict[str, Operation] | None = None,
        targets: dict[str, Relation] | None = None,
    ) -> Model:
        """Construct a model with a sorted copy of *universe*."""
        u = sorted(universe)
        return cls(
            universe=u,
            relations=dict(relations or {}),
            operations=dict(operations or {}),
            targets=dict(targets or {}),
        )


FiniteAlgebra = Model
"""Alias emphasizing universal-algebra usage of :class:`Model`."""
