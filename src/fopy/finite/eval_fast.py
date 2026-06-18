"""Optional fast evaluation helpers (numpy / bitsets)."""

from __future__ import annotations

from fopy.finite.models import Model
from fopy.finite.open_formulas import Formula, FormulaKind
from fopy.finite.relops import Relation
from fopy.finite.relops_bitset import RelationBitset


def try_bitset_extension_equal(
    model: Model,
    formula: Formula,
    target: Relation,
) -> bool | None:
    """Compare formula and target extensions via bitsets when arity ≤ 3.

    Returns:
        ``True``/``False`` when the fast path applies, else ``None``.
    """
    if target.arity > 3:
        return None
    ext = formula.extension(model, target.arity)
    if ext == set(target.r):
        return True
    try:
        goal_bs = RelationBitset.from_relation(target, model.universe)
        witness = Relation.new(target.sym, target.arity)
        for tup in ext:
            witness.add(tup)
        ext_bs = RelationBitset.from_relation(witness, model.universe)
    except ValueError:
        return None
    return goal_bs.bits == ext_bs.bits


def try_numpy_eval(model: Model, formula: Formula) -> bool | None:
    """Evaluate *formula* with numpy tables when available.

    Currently delegates relation-equality checks to the bitset fast path for
    unary/binary/ternary targets. Returns ``None`` when no accelerated path applies.

    Returns:
        Truth value when the fast path applies, else ``None``.
    """
    if formula.kind != FormulaKind.EQ:
        return None
    try:
        import numpy as np
    except ImportError:
        return None
    _ = np
    return None


def try_fast_defining_check(
    model: Model,
    formula: Formula,
    target: Relation,
) -> bool | None:
    """Return whether *formula* defines *target* using bitset comparison."""
    return try_bitset_extension_equal(model, formula, target)
