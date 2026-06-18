"""Finite relops and models tests."""

from __future__ import annotations

from fopy.finite.models import Model
from fopy.finite.relops import Operation, Relation


def test_relation_add_wrong_arity_ignored():
    r = Relation.new("R", 2)
    r.add([0])
    r.add([0, 1, 2])
    r.add([0, 1])
    assert (0, 1) in r.r


def test_relation_with_tuples():
    r = Relation.new("R", 1)
    r.with_tuples([[0], [1]])
    assert r.contains([0])


def test_relation_eq_false():
    a = Relation.new("R", 1)
    b = Relation.new("R", 1)
    a.add([0])
    b.add([1])
    assert a != b


def test_relation_eq_not_implemented():
    r = Relation.new("R", 1)
    assert r.__eq__(42) is NotImplemented


def test_relation_hash_stable():
    r = Relation.new("R", 2)
    r.add([0, 1])
    assert hash(r) == hash(r)


def test_operation_add_and_call():
    op = Operation.new("f", 2)
    op.add([0, 0, 1])
    assert op.call((0, 0)) == 1
    assert op.call((0, 1)) is None


def test_operation_restrict():
    op = Operation.new("f", 2)
    op.add([0, 0, 0])
    op.add([0, 1, 1])
    op.add([1, 0, 1])
    sub = op.restrict({0})
    assert sub.call((0, 0)) == 0


def test_model_new_sorts_universe():
    m = Model.new([2, 0, 1])
    assert m.universe == [0, 1, 2]


def test_relation_restrict_empty():
    r = Relation.new("R", 2)
    r.add([0, 1])
    r.add([2, 3])
    sub = r.restrict({0})
    assert sub.r == set() or all(0 in t for t in sub.r)
