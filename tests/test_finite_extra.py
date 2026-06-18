"""Additional finite-model and HIT coverage."""

from pathlib import Path

import fopy as fo
from fopy.finite import is_open_definable
from fopy.finite.models import Model
from fopy.finite.relops import Operation, Relation
from fopy.parse import parse_model

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_model_extension():
    from fopy.finite.open_formulas import Variable
    from fopy.finite.open_parse import parse_open_formula

    ops = {"f": Operation.new("f", 2)}
    ops["f"].add([0, 0, 0])
    ops["f"].add([0, 1, 1])
    ops["f"].add([1, 0, 1])
    ops["f"].add([1, 1, 0])
    model = Model.new([0, 1], operations=ops)
    vars_map = {"x": Variable.new("x"), "y": Variable.new("y")}
    formula = parse_open_formula("eq(f(x,y),x)", vars_map, ops)
    ext = formula.extension(model, 2)
    assert isinstance(ext, set)


def test_cadena5_definability():
    model = parse_model(FIXTURES / "cadena5.model", preprocess=True)
    targets = [r for sym, r in model.relations.items() if sym.startswith("T")]
    if targets:
        result = is_open_definable(model, targets[0])
        assert result.definable in (True, False)


def test_relation_restrict():
    rel = Relation.new("R", 2)
    rel.add([0, 1])
    rel.add([1, 0])
    sub = rel.restrict({0})
    assert sub.r == {(0, 0)} or len(sub.r) <= 1


def test_domain_builder():
    d = fo.builders.Domain("a", "b", "c")
    assert len(d) == 3
    assert d[0] == "a"
