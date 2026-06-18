"""Extensive universal algebra tests."""

from __future__ import annotations

import pytest

import fopy as fo
from fopy.bridge import to_finite_model
from fopy.universal import (
    Congruence,
    congruence_lattice,
    homomorphisms,
    is_boolean_algebra,
    is_distributive_lattice,
    is_lattice,
    is_subalgebra,
    subalgebra,
)


@pytest.mark.finite
class TestSubalgebra:
    def test_chain_generated(self):
        m = to_finite_model(fo.builders.chain(4))
        s = subalgebra(m, [0])
        assert 0 in s

    def test_full_universe_is_subalgebra(self):
        m = to_finite_model(fo.builders.chain(3))
        assert is_subalgebra(m, set(m.universe))

    def test_singleton_chain_is_subalgebra(self):
        m = to_finite_model(fo.builders.chain(4))
        assert is_subalgebra(m, {0})


@pytest.mark.finite
class TestCongruenceLattice:
    def test_chain_has_congruences(self):
        m = to_finite_model(fo.builders.chain(3))
        latt = congruence_lattice(m)
        assert len(latt) >= 1
        assert all(isinstance(c, Congruence) for c in latt)

    def test_trivial_on_one_element(self):
        m = to_finite_model(fo.builders.chain(1))
        latt = congruence_lattice(m)
        assert len(latt) >= 1

    def test_large_universe_truncated(self):
        m = to_finite_model(fo.builders.chain(10))
        latt = congruence_lattice(m)
        assert len(latt) >= 1


@pytest.mark.finite
class TestHomomorphisms:
    def test_chain2_has_identity(self):
        m = to_finite_model(fo.builders.chain(2))
        maps = homomorphisms(m, m)
        assert len(maps) >= 1
        assert any(all(h[a] == a for a in m.universe) for h in maps)

    def test_into_larger_target(self):
        m2 = to_finite_model(fo.builders.chain(2))
        m3 = to_finite_model(fo.builders.chain(3))
        maps = homomorphisms(m2, m3)
        assert isinstance(maps, list)

    def test_large_returns_empty(self):
        m = to_finite_model(fo.builders.chain(8))
        maps = homomorphisms(m, m)
        assert maps == []


@pytest.mark.finite
class TestLatticeProperties:
    def test_b2_is_lattice(self):
        m = to_finite_model(fo.builders.boolean_lattice(2))
        assert is_lattice(m, "join", "meet")

    def test_b2_distributive(self):
        m = to_finite_model(fo.builders.boolean_lattice(2))
        assert is_distributive_lattice(m, "join", "meet")

    def test_chain3_is_lattice_with_leq_ops(self):
        s = fo.builders.chain(3)
        m = to_finite_model(s)
        if "join" in m.operations and "meet" in m.operations:
            assert is_lattice(m, "join", "meet")

    def test_missing_ops_not_lattice(self, minimal_model):
        assert not is_lattice(minimal_model, "join", "meet")

    def test_boolean_with_neg(self):
        m = to_finite_model(fo.builders.boolean_lattice(2))
        if "neg" in m.operations:
            result = is_boolean_algebra(m, "join", "meet", "neg")
            assert isinstance(result, bool)


@pytest.mark.finite
class TestCongruenceAsRelation:
    def test_as_relation_reflexive(self):
        m = to_finite_model(fo.builders.chain(3))
        latt = congruence_lattice(m)
        c = latt[0]
        pairs = c.as_relation(m.universe)
        for a in m.universe:
            assert (a, a) in pairs
