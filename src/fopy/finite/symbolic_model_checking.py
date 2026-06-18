"""Model checking for symbolic :mod:`fopy.formulas` on finite models."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import TYPE_CHECKING

from fopy.bridge import from_finite_model
from fopy.finite.models import Model
from fopy.semantics import satisfy
from fopy.symbols import Variable as SymbolicVariable
from fopy.transform import free_vars

if TYPE_CHECKING:
    from fopy.formulas import Formula


@dataclass
class SymbolicCounterexample:
    """Witness falsifying a symbolic formula on a finite model.

    Attributes:
        assignment: Variable assignment (empty dict for false sentences).
        trace: Short human-readable evaluation hint.
    """

    assignment: dict[SymbolicVariable, int]
    trace: str


def models_symbolic(
    model: Model,
    formula: Formula,
    *,
    max_universe: int = 8,
) -> bool:
    """Return whether *formula* is universally valid on *model*.

    Converts the finite model to a symbolic :class:`~fopy.structures.Structure`
    and evaluates the full first-order formula (including quantifiers). When
    free variables remain, checks truth under **all** assignments to those
    variables — the same convention as :meth:`~fopy.finite.models.Model.models`
    for open formulas.

    Args:
        model: Finite algebra / structure with integer universe.
        formula: Symbolic first-order formula from :mod:`fopy.formulas`.
        max_universe: Reject models with ``|U|`` larger than this bound.

    Returns:
        ``True`` iff every required assignment makes *formula* true.

    Raises:
        ValueError: If ``len(model.universe) > max_universe``.
    """
    _check_universe_bound(model, max_universe)
    structure = from_finite_model(model)
    fv = free_vars(formula)
    if not fv:
        return bool(satisfy(formula, structure, {}))
    ordered = sorted(fv, key=lambda v: v.sym)
    for vals in product(structure.universe, repeat=len(ordered)):
        assignment = dict(zip(ordered, vals, strict=True))
        if not satisfy(formula, structure, assignment):
            return False
    return True


def counterexample_symbolic(
    model: Model,
    formula: Formula,
    *,
    max_universe: int = 8,
    with_trace: bool = False,
) -> dict[SymbolicVariable, int] | SymbolicCounterexample | None:
    """Return one assignment falsifying *formula*, or ``None`` if none exists.

    For closed sentences returns ``None`` when true and ``{}`` when false.

    Args:
        model: Finite structure.
        formula: Symbolic first-order formula.
        max_universe: Universe size guard (see :func:`models_symbolic`).

    Returns:
        A variable assignment witnessing falsity, or ``None`` when the formula
        is valid on the model under the universal reading of free variables.

    Raises:
        ValueError: If the universe exceeds *max_universe*.
    """
    _check_universe_bound(model, max_universe)
    structure = from_finite_model(model)
    fv = free_vars(formula)
    if not fv:
        if satisfy(formula, structure, {}):
            return None
        witness: dict[SymbolicVariable, int] = {}
        if with_trace:
            return SymbolicCounterexample(assignment=witness, trace="closed sentence is false")
        return witness
    ordered = sorted(fv, key=lambda v: v.sym)
    for vals in product(structure.universe, repeat=len(ordered)):
        assignment = dict(zip(ordered, vals, strict=True))
        if not satisfy(formula, structure, assignment):
            if with_trace:
                vals_txt = ", ".join(f"{v.sym}={assignment[v]}" for v in ordered)
                return SymbolicCounterexample(
                    assignment=assignment,
                    trace=f"falsified under assignment {{{vals_txt}}}",
                )
            return assignment
    return None


def satisfying_assignments_symbolic(
    model: Model,
    formula: Formula,
    *,
    max_universe: int = 8,
) -> list[dict[SymbolicVariable, int]]:
    """List assignments satisfying *formula* (may be large; bounded universe).

    Args:
        model: Finite structure.
        formula: Symbolic first-order formula.
        max_universe: Universe size guard.

    Returns:
        Every assignment under which *formula* evaluates to true. For a false
        closed sentence the list is empty; for a true closed sentence ``[{}]``.

    Raises:
        ValueError: If the universe exceeds *max_universe*.
    """
    _check_universe_bound(model, max_universe)
    structure = from_finite_model(model)
    fv = free_vars(formula)
    if not fv:
        return [{}] if satisfy(formula, structure, {}) else []
    ordered = sorted(fv, key=lambda v: v.sym)
    result: list[dict[SymbolicVariable, int]] = []
    for vals in product(structure.universe, repeat=len(ordered)):
        assignment = dict(zip(ordered, vals, strict=True))
        if satisfy(formula, structure, assignment):
            result.append(assignment)
    return result


def _check_universe_bound(model: Model, max_universe: int) -> None:
    if len(model.universe) > max_universe:
        raise ValueError(f"Universe size {len(model.universe)} exceeds max_universe={max_universe}")
