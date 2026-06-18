"""Direct products of finite algebras."""

from __future__ import annotations

from itertools import product

from fopy.finite.models import Model
from fopy.finite.relops import Operation, Relation


def direct_product(left: Model, right: Model) -> Model:
    """Form the direct product ``left × right``.

    Universe elements are pairs ``(a, b)`` encoded as ``a * |V_R| + b``.
    Operations apply componentwise when both algebras define the same symbol.

    Args:
        left: First factor algebra.
        right: Second factor algebra.

    Returns:
        Product model on the Cartesian product of universes.

    Raises:
        KeyError: If operation symbols disagree between factors.
        ValueError: If a shared operation has mismatched arity.
    """
    n_l, n_r = len(left.universe), len(right.universe)
    universe = list(range(n_l * n_r))

    def encode(a: int, b: int) -> int:
        return a * n_r + b

    def decode_ab(c: int) -> tuple[int, int]:
        return c // n_r, c % n_r

    operations: dict[str, Operation] = {}
    for sym, op_l in left.operations.items():
        op_r = right.operations.get(sym)
        if op_r is None:
            raise KeyError(f"Operation {sym!r} missing in right factor")
        if op_l.arity != op_r.arity:
            raise ValueError(f"Arity mismatch for operation {sym!r}")
        op = Operation(sym, op_l.arity)
        if op_l.arity == 0:
            a = op_l.call(())
            b = op_r.call(())
            if a is not None and b is not None:
                op.add([encode(a, b)])
        else:
            for args in product(universe, repeat=op_l.arity):
                decoded = [decode_ab(x) for x in args]
                vals_l = tuple(d[0] for d in decoded)
                vals_r = tuple(d[1] for d in decoded)
                a = op_l.call(vals_l)
                b = op_r.call(vals_r)
                if a is not None and b is not None:
                    op.add(list(args) + [encode(a, b)])
        operations[sym] = op

    relations: dict[str, Relation] = {}
    for sym, rel_l in left.relations.items():
        rel_r = right.relations.get(sym)
        if rel_r is None or rel_l.arity != rel_r.arity:
            continue
        rel = Relation(sym, rel_l.arity)
        for args in product(universe, repeat=rel_l.arity):
            decoded = [decode_ab(x) for x in args]
            vals_l = tuple(d[0] for d in decoded)
            vals_r = tuple(d[1] for d in decoded)
            if rel_l.contains(vals_l) and rel_r.contains(vals_r):
                rel.add(list(args))
        relations[sym] = rel

    return Model(universe=universe, relations=relations, operations=operations)
