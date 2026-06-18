"""Bridge between symbolic structures and finite models."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from fopy.finite.models import Model
from fopy.finite.relops import Operation, Relation
from fopy.parse.model import parse_model
from fopy.signature import Signature
from fopy.structures import Structure


def to_finite_model(structure: Structure, *, int_universe: bool = True) -> Model:
    """Convert a symbolic :class:`~fopy.structures.Structure` to a finite model.

    Builds a :class:`~fopy.finite.models.Model` from *structure*.
    :class:`~fopy.finite.relops.Operation` / :class:`~fopy.finite.relops.Relation`
    objects suitable for HIT and open-formula algorithms.

    Args:
        structure: Source structure with finite universe.
        int_universe: If ``True``, coerce universe elements to ``int``.

    Returns:
        Finite model with the same operations and relations.

    Raises:
        TypeError: If ``int_universe`` is ``True`` and an element is not coercible to ``int``.
    """
    universe: list[int] = []
    index: dict[Any, int] = {}
    for _i, elem in enumerate(structure.universe):
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

    return Model.new(
        universe=sorted(set(universe)),
        relations=relations,
        operations=operations,
        targets=targets,
    )


def from_finite_model(model: Model, signature: Signature | None = None) -> Structure:
    """Convert a finite :class:`~fopy.finite.models.Model` to a :class:`~fopy.structures.Structure`.

    Args:
        model: Finite algebra with integer universe and table-encoded ops.
        signature: Optional signature override; inferred from *model* when omitted.

    Returns:
        Structure with dict/set interpretations for functions and relations.
    """
    functions: dict[str, dict[tuple[int, ...], int] | int] = {}
    relations: dict[str, set[tuple[int, ...]]] = {}

    sig = signature or Signature(
        functions={s: op.arity for s, op in model.operations.items()},
        relations={s: rel.arity for s, rel in model.relations.items()},
    )

    for sym, op in model.operations.items():
        if op.arity == 0:
            for _row, result in op.op.items():
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

    return Structure.from_tables(
        sig,
        list(model.universe),
        functions=functions,
        relations=cast(Mapping[str, set[tuple[Any, ...]] | dict[tuple[Any, ...], bool]], relations),
        universes={"U": list(model.universe)},
    )


def load_structure(path: str | Path, *, preprocess: bool = True) -> Structure:
    """Load an OpenDefAlg ``.model`` file as a :class:`~fopy.structures.Structure`.

    Args:
        path: Path to a ``.model`` or ``.model.gz`` file.
        preprocess: If ``True``, run target splitting like :func:`~fopy.parse.parse_model`.

    Returns:
        Symbolic structure equivalent to the parsed finite model.
    """
    model = parse_model(path, preprocess=preprocess)
    return from_finite_model(model)


def _all_tuples(universe: list[Any], arity: int) -> list[tuple[Any, ...]]:
    if arity == 0:
        return [()]
    result: list[tuple[Any, ...]] = [()]
    for _ in range(arity):
        result = [r + (u,) for r in result for u in universe]
    return result
