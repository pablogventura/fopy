"""Structure ↔ finite Model bridge."""

import fopy as fo
from fopy.finite import Model
from fopy.parse import parse_model


def test_roundtrip_chain():
    s = fo.builders.chain(3)
    m = fo.to_finite_model(s)
    s2 = fo.from_finite_model(m, s.signature)
    x, y = fo.symbols("x y")
    leq = fo.RelSymbol("leq", 2)
    f = leq(x, y)
    assert fo.satisfy(f, s, {x: 0, y: 2}) == fo.satisfy(f, s2, {x: 0, y: 2})


def test_load_structure_minimal(tmp_path, fixtures_dir):
    path = fixtures_dir / "minimal.model"
    s = fo.load_structure(path)
    assert len(s.universe) == 2
    m = parse_model(path)
    assert isinstance(m, Model)


def test_bridge_retrombo(retrombo_structure):
    m = fo.to_finite_model(retrombo_structure)
    assert len(m.universe) == 4
