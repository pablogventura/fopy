"""Optional fast evaluation helpers (numpy / bitsets)."""

from __future__ import annotations

from collections.abc import Sequence
from itertools import product
from typing import Any, cast

from fopy.finite.models import Model
from fopy.finite.open_formulas import Formula, FormulaKind, Term, TermKind, Variable
from fopy.finite.relops import Relation
from fopy.finite.relops_bitset import RelationBitset

_MAX_FAST_UNIVERSE = 32
_SUB_TO_DIGIT = {ch: str(i) for i, ch in enumerate("₀₁₂₃₄₅₆₇₈₉")}


def _var_index(var: Variable) -> int | None:
    """Decode ``xᵢ`` style variable symbols to their index."""
    sym = var.sym
    if not sym.startswith("x"):
        return None
    tail = sym[1:]
    if not tail:
        return 0
    digits: list[str] = []
    for ch in tail:
        if ch in _SUB_TO_DIGIT:
            digits.append(_SUB_TO_DIGIT[ch])
        elif ch == "₋":
            digits.append("-")
        elif ch.isdigit():
            digits.append(ch)
        else:
            return None
    try:
        return int("".join(digits))
    except ValueError:
        return None


def _build_numpy_op_tables(model: Model) -> dict[str, Any] | None:
    """Build numpy index tables for operations on *model*."""
    try:
        import numpy as np
    except ImportError:
        return None
    n = len(model.universe)
    if n > _MAX_FAST_UNIVERSE:
        return None
    idx = {u: i for i, u in enumerate(model.universe)}
    tables: dict[str, Any] = {}
    for sym, op in model.operations.items():
        if op.arity == 0:
            val = next(iter(op.op.values()), model.universe[0])
            tables[sym] = np.int32(idx.get(val, val))
            continue
        shape = (n,) * op.arity
        table = np.zeros(shape, dtype=np.int32)
        for args, result in op.op.items():
            mapped = tuple(idx.get(a, a) for a in args)
            table[mapped] = idx.get(result, result)
        tables[sym] = table
    return tables


def _eval_open_term_numpy(
    term: Term,
    tables: dict[str, Any],
    var_grids: Sequence[Any],
) -> Any | None:
    """Evaluate an open term on numpy index grids."""
    if term.kind == TermKind.VARIABLE:
        assert term.variable is not None
        vi = _var_index(term.variable)
        if vi is None or vi >= len(var_grids):
            return None
        return var_grids[vi]
    if term.kind == TermKind.OP_TERM:
        assert term.sym is not None
        sym = term.sym.op
        if sym not in tables:
            return None
        base = tables[sym]
        if term.sym.arity == 0:
            return base
        args = [_eval_open_term_numpy(a, tables, var_grids) for a in term.args]
        if any(a is None for a in args):
            return None
        if term.sym.arity == 1:
            return cast(Any, base)[args[0]]
        if term.sym.arity == 2:
            return cast(Any, base)[args[0], args[1]]
    return None


def numpy_eq_extension(
    model: Model,
    formula: Formula,
    arity: int,
) -> set[tuple[int, ...]] | None:
    """Compute the extension of an equality formula using numpy term evaluation."""
    if formula.kind != FormulaKind.EQ or formula.t1 is None or formula.t2 is None:
        return None
    try:
        import numpy as np
    except ImportError:
        return None
    tables = _build_numpy_op_tables(model)
    if tables is None:
        return None
    n = len(model.universe)
    var_grids: list[Any]
    if arity == 1:
        var_grids = [np.arange(n, dtype=np.int32)]
    elif arity == 2:
        g0, g1 = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
        var_grids = [g0, g1]
    else:
        return None
    left = _eval_open_term_numpy(formula.t1, tables, var_grids)
    right = _eval_open_term_numpy(formula.t2, tables, var_grids)
    if left is None or right is None:
        return None
    mask = cast(Any, left == right)
    ext: set[tuple[int, ...]] = set()
    if arity == 1:
        for i in range(n):
            if bool(mask[i]):
                ext.add((model.universe[i],))
    else:
        for i in range(n):
            for j in range(n):
                if bool(mask[i, j]):
                    ext.add((model.universe[i], model.universe[j]))
    return ext


def try_bitset_extension_equal(
    model: Model,
    formula: Formula,
    target: Relation,
) -> bool | None:
    """Compare formula and target extensions via bitsets when arity ≤ 3.

    Returns:
        ``True``/``False`` when the fast path applies, else ``None``.
    """
    if target.arity > 3 or len(model.universe) > _MAX_FAST_UNIVERSE:
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


def try_numpy_extension_equal(
    model: Model,
    formula: Formula,
    target: Relation,
) -> bool | None:
    """Numpy-accelerated extension equality for unary/binary equality formulas.

    Returns:
        ``True``/``False`` when the numpy path applies, else ``None``.
    """
    if formula.kind != FormulaKind.EQ or target.arity > 2:
        return None
    ext = numpy_eq_extension(model, formula, target.arity)
    if ext is None:
        return None
    return ext == set(target.r)


def try_numpy_eval(model: Model, formula: Formula) -> bool | None:
    """Return whether *formula* is true on all assignments when numpy applies.

    Uses :func:`numpy_eq_extension` for unary/binary equalities; otherwise
    returns ``None``.
    """
    if formula.kind != FormulaKind.EQ:
        return None
    vs = formula.implied_declaration()
    arity = len(vs) if vs else 0
    if arity > 2:
        return None
    ext = numpy_eq_extension(model, formula, max(arity, 1))
    if ext is None:
        return None
    universe = model.universe
    if arity == 0:
        return () in ext or (len(ext) == 1 and next(iter(ext)) == ())
    full = set(product(universe, repeat=arity))
    return ext == full


def try_fast_defining_check(
    model: Model,
    formula: Formula,
    target: Relation,
) -> bool | None:
    """Return whether *formula* defines *target* using fast paths."""
    numpy_result = try_numpy_extension_equal(model, formula, target)
    if numpy_result is not None:
        return numpy_result
    return try_bitset_extension_equal(model, formula, target)
