"""Builder and catalog exhaustive tests."""

from __future__ import annotations

import pytest

import fopy as fo


@pytest.mark.parametrize("n", range(2, 8))
def test_chain_sizes(n: int):
    s = fo.builders.chain(n)
    assert len(s.universe) == n


@pytest.mark.parametrize("n", range(1, 4))
def test_boolean_lattice_sizes(n: int):
    s = fo.builders.boolean_lattice(n)
    assert len(s.universe) == 2**n


def test_from_leq_direct():
    elems = [0, 1, 2]
    s = fo.builders.from_leq(elems, lambda a, b: a <= b)
    assert s.call_relation("leq", (0, 2))


def test_from_covers_infer():
    s = fo.builders.from_covers([0, 1, 2], [(0, 1), (1, 2)])
    assert s.call_relation("leq", (0, 2))


def test_from_upper_covers_names():
    s = fo.builders.from_upper_covers([[1], [2], []], names=["a", "b", "c"])
    assert "a" in s.universe


def test_hasse_covers_chain():
    covers = fo.builders.hasse_covers([0, 1, 2, 3], covers=[(0, 1), (1, 2), (2, 3)])
    assert (0, 1) in covers


def test_from_cayley_xor():
    sig = fo.Signature(functions={"xor": 2})
    table = [[0, 1], [1, 0]]
    s = fo.builders.from_cayley(sig, "xor", [0, 1], table)
    assert s.call_function("xor", (1, 1)) == 0


def test_from_cayley_bad_table():
    sig = fo.Signature(functions={"f": 2})
    with pytest.raises(ValueError):
        fo.builders.from_cayley(sig, "f", [0, 1], [[0]])


def test_fluent_builder_name():
    sig = fo.Signature(relations={"R": 2})
    s = fo.builders.build(sig).universe(0, 1).relation("R", {(0, 0), (1, 1)}).name("test").build()
    assert s.name == "test"


def test_domain_index_and_len():
    d = fo.builders.Domain(10, 20, 30)
    assert len(d) == 3
    assert d.index(20) == 1


def test_domain_getattr_error():
    d = fo.builders.Domain("a")
    with pytest.raises(AttributeError):
        _ = d.missing


def test_m3_n5_retrombo_sizes():
    assert len(fo.builders.m3().universe) == 4
    assert len(fo.builders.n5().universe) == 5
    assert len(fo.builders.retrombo().universe) == 4


def test_b3_catalog():
    assert len(fo.builders.b3().universe) == 8
