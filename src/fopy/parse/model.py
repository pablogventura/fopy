"""Parse .model files (OpenDefAlgSplitting format)."""

from __future__ import annotations

import gzip
import re
from pathlib import Path

from fopy.finite.models import Model
from fopy.finite.open_formulas import Variable, extension
from fopy.finite.open_parse import parse_open_formula
from fopy.finite.preprocessing import split_targets
from fopy.finite.relops import Operation, Relation


class ParseError(Exception):
    def __init__(self, line: int, message: str, path: str | None = None) -> None:
        self.line = line
        self.path = path
        self.message = message
        super().__init__(f"Line {line} of {path}: {message}")


def _clean_line(line: str) -> str:
    if "#" in line:
        line = line[: line.index("#")]
    return line.strip()


def parse_model(path: str | Path | None = None, preprocess: bool = True) -> Model:
    path_obj = Path(path) if path else None
    if path_obj and str(path_obj).endswith(".gz"):
        f = gzip.open(path_obj, "rt")
    elif path_obj:
        f = open(path_obj, encoding="utf-8")
    else:
        raise ParseError(0, "path required")

    universe: list[int] | None = None
    relations: dict[str, Relation] = {}
    operations: dict[str, Operation] = {}
    targets: dict[str, Relation] = {}
    current_rel: tuple[Relation, int] | None = None
    current_op: tuple[Operation, int] | None = None
    line_no = 0

    with f:
        for raw in f:
            line_no += 1
            line = _clean_line(raw)
            if not line:
                continue

            if universe is None:
                universe = [int(x) for x in line.split()]
                continue

            if current_rel is None and current_op is None:
                if "(" in line and not line.startswith("@"):
                    rel = _parse_def_formula(line, universe, relations, operations)
                    if rel.sym.startswith("T"):
                        targets[rel.sym] = rel
                    relations[rel.sym] = rel
                    continue
                parts = line.split()
                if len(parts) == 2:
                    sym, arity = parts[0], int(parts[1])
                    n = len(universe)
                    missing = n**arity
                    current_op = (Operation(sym, arity), missing)
                    continue
                if len(parts) == 3:
                    sym, ntuples, arity = parts[0], int(parts[1]), int(parts[2])
                    current_rel = (Relation(sym, arity), ntuples)
                    continue

            if current_rel is not None:
                rel, missing = current_rel
                tup = [int(x) for x in line.split()]
                rel.add(tup)
                missing -= 1
                if missing == 0:
                    relations[rel.sym] = rel
                    if rel.sym.startswith("T"):
                        targets[rel.sym] = rel
                    current_rel = None
                else:
                    current_rel = (rel, missing)
                continue

            if current_op is not None:
                op, missing = current_op
                tup = [int(x) for x in line.split()]
                op.add(tup)
                missing -= 1
                if missing == 0:
                    operations[op.sym] = op
                    current_op = None
                else:
                    current_op = (op, missing)

    if universe is None:
        raise ParseError(line_no, "Universe not defined", str(path_obj))

    model = Model(universe=universe, relations=relations, operations=operations, targets=targets)

    if preprocess:
        new_rels = dict(model.relations)
        for sym in list(new_rels):
            if sym.startswith("T"):
                rel = new_rels.pop(sym)
                for r in split_targets(rel):
                    new_rels[r.sym] = r
        model.relations = new_rels

    return model


def _parse_def_formula(
    line: str,
    universe: list[int],
    relations: dict[str, Relation],
    operations: dict[str, Operation],
) -> Relation:
    if "==" in line:
        raise ValueError("Must use eq(x,y) not ==")
    m = re.match(r"(\w+)\(([^)]*)\)\s*(.*)", line)
    if not m:
        raise ValueError(f"Bad formula line: {line}")
    sym, decl, fstr = m.group(1), m.group(2), m.group(3).strip()
    decl_vars = [d.strip() for d in decl.split(",") if d.strip()]
    if len(decl_vars) != len(set(decl_vars)):
        raise ValueError("Repeated variables in declaration")
    vars_map = {name: Variable.from_index(i) for i, name in enumerate(decl_vars)}
    formula = parse_open_formula(fstr, vars_map, operations)
    tmp_model = Model(universe=universe, relations=relations, operations=operations)
    ext = extension(formula, tmp_model, len(decl_vars))
    rel = Relation(sym, len(decl_vars))
    for t in ext:
        rel.add(list(t))
    return rel
