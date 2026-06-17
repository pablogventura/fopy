"""Bridge module extended tests."""

from __future__ import annotations

import pytest

import fopy as fo


def test_to_finite_model_string_universe_raises():
    sig = fo.Signature(relations={"leq": 2})
    s = fo.Structure.from_tables(
        sig,
        ["a", "b"],
        relations={"leq": {("a", "a"), ("a", "b"), ("b", "b")}},
    )
    with pytest.raises((TypeError, ValueError)):
        fo.to_finite_model(s, int_universe=True)


def test_from_finite_model_with_targets():
    from fopy.finite.models import Model
    from fopy.finite.relops import Operation, Relation

    op = Operation.new("f", 2)
    op.add([0, 0, 0])
    rel = Relation.new("T0", 1)
    rel.add([0])
    m = Model.new([0, 1], operations={"f": op}, relations={"leq": Relation.new("leq", 2)}, targets={"T0": rel})
    sig = fo.Signature(functions={"f": 2}, relations={"leq": 2})
    s = fo.from_finite_model(m, sig)
    assert len(s.universe) == 2


def test_load_structure_cadena(models_dir):
    path = models_dir / "cadena4.model"
    if not path.exists():
        pytest.skip("fixture missing")
    s = fo.load_structure(path)
    assert len(s.universe) == 4


def test_bridge_all_tuples_helper():
    from fopy.bridge import _all_tuples

    assert len(_all_tuples([0, 1], 2)) == 4
    assert _all_tuples([0], 0) == [()]
