"""Serialize :class:`~fopy.finite.models.Model` to OpenDefAlgSplitting ``.model`` format."""

from __future__ import annotations

from itertools import product
from pathlib import Path

from fopy.finite.models import Model
from fopy.finite.relops import Operation, Relation


def _write_operation_lines(op: Operation, universe: list[int]) -> list[str]:
    lines: list[str] = [f"{op.sym} {op.arity}"]
    if op.arity == 0:
        result = op.op.get(())
        if result is None:
            raise ValueError(f"Constant operation {op.sym!r} is undefined on empty args")
        lines.append(str(result))
        return lines
    for args in product(universe, repeat=op.arity):
        result = op.op.get(args)
        if result is None:
            raise ValueError(f"Operation {op.sym!r} undefined on {args}")
        lines.append(" ".join(str(x) for x in (*args, result)))
    return lines


def _write_relation_lines(rel: Relation) -> list[str]:
    tuples = sorted(rel.r)
    lines = [f"{rel.sym} {len(tuples)} {rel.arity}"]
    for tup in tuples:
        lines.append(" ".join(str(x) for x in tup))
    return lines


def write_model(model: Model, path: str | Path) -> None:
    """Write *model* to a ``.model`` file understood by OpenDefAlgSplitting.

    Args:
        model: Finite structure to serialize.
        path: Destination path.

    Raises:
        ValueError: If an operation table is incomplete over *model.universe*.
    """
    path_obj = Path(path)
    lines: list[str] = [" ".join(str(x) for x in model.universe), ""]

    for op in sorted(model.operations.values(), key=lambda o: o.sym):
        lines.extend(_write_operation_lines(op, model.universe))
        lines.append("")

    for rel in sorted(model.relations.values(), key=lambda r: r.sym):
        if rel.sym.startswith("T"):
            continue
        lines.extend(_write_relation_lines(rel))
        lines.append("")

    for rel in sorted(model.targets.values(), key=lambda r: r.sym):
        lines.extend(_write_relation_lines(rel))
        if not lines[-1]:
            continue
        lines.append("")

    while lines and lines[-1] == "":
        lines.pop()

    path_obj.write_text("\n".join(lines) + "\n", encoding="utf-8")
