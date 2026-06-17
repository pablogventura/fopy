"""Bridge between symbolic structures and finite models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fopy.finite.models import Model
from fopy.finite.relops import Operation, Relation
from fopy.parse.model import parse_model
from fopy.signature import Signature
from fopy.structures import Structure


def to_finite_model(structure: Structure, *, int_universe: bool = True) -> Model:
    """
    Convert a :class:`~fopy.structures.Structure` to a :class:`~fopy.finite.models.Model`.

    The universe must be integers (or coercible) when ``int_universe`` is True.
    """
    universe: list[int] = []
    index: dict[Any, int] = {}
    for i, elem in enumerate(structure.universe):
        val = int(elem) if int_universe else elem
        if not isinstance(val, int):
            raise TypeError("Universe elements must be integers for finite Model conversion")
        universe.append(val)
        index[elem] = val

    operations: dict[str, Operation] = {}
    for sym, arity in structure.signature.functions.items():
        op = Operation.new(sym, arity)
        interp = structure.functions[sym]
        if arity == 0:
            result = structure.call_function(sym, ())
            op.add([index.get(result, result)])
            operations[sym] = op
            continue
        if isinstance(interp, dict):
            for args, result in interp.items():
                mapped = tuple(index.get(a, a) for a in args)
                op.add(list(mapped) + [index.get(result, result)])
        operations[sym] = op

    relations: dict[str, Relation] = {}
    targets: dict[str, Relation] = {}
    for sym, arity in structure.signature.relations.items():
        rel = Relation.new(sym, arity)
        interp = structure.relations[sym]
        tuples: set[tuple[Any, ...]]
        if isinstance(interp, set):
            tuples = interp
        elif isinstance(interp, dict):
            tuples = {k for k, v in interp.items() if v}
        else:
            tuples = {
                tuple(args)
                for args in _all_tuples(structure.universe, arity)
                if structure.call_relation(sym, args)
            }
        for t in tuples:
            rel.add([index.get(a, a) for a in t])
        if sym.startswith("T"):
            targets[sym] = rel
        relations[sym] = rel

    return Model.new(universe=sorted(set(universe)), relations=relations, operations=operations, targets=targets)


def from_finite_model(model: Model, signature: Signature | None = None) -> Structure:
    """Convert a finite :class:`~fopy.finite.models.Model` to a :class:`~fopy.structures.Structure`."""
    functions: dict[str, dict[tuple[int, ...], int] | int] = {}
    relations: dict[str, set[tuple[int, ...]]] = {}

    sig = signature or Signature(
        functions={s: op.arity for s, op in model.operations.items()},
        relations={s: rel.arity for s, rel in model.relations.items()},
    )

    for sym, op in model.operations.items():
        if op.arity == 0:
            for row, result in op.op.items():
                functions[sym] = result
            if sym not in functions and op.op:
                functions[sym] = next(iter(op.op.values()))
            continue
        table: dict[tuple[int, ...], int] = {}
        for args, result in op.op.items():
            table[args] = result
        functions[sym] = table

    for sym, rel in model.relations.items():
        relations[sym] = set(rel.r)

    return Structure.from_tables(sig, list(model.universe), functions=functions, relations=relations)


def load_structure(path: str | Path, *, preprocess: bool = True) -> Structure:
    """Load a ``.model`` file as a symbolic :class:`~fopy.structures.Structure`."""
    model = parse_model(path, preprocess=preprocess)
    return from_finite_model(model)


def _all_tuples(universe: list[Any], arity: int) -> list[tuple[Any, ...]]:
    if arity == 0:
        return [()]
    result: list[tuple[Any, ...]] = [()]
    for _ in range(arity):
        result = [r + (u,) for r in result for u in universe]
    return result
