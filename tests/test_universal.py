"""Universal algebra on finite models."""

from __future__ import annotations

import pytest

import fopy as fo
from fopy.bridge import to_finite_model
from fopy.universal import (
    congruence_lattice,
    homomorphisms,
    is_lattice,
    subalgebra,
)


@pytest.mark.finite
def test_subalgebra_generated():
    s = fo.builders.chain(3)
    m = to_finite_model(s)
    sub = subalgebra(m, [0])
    assert 0 in sub


@pytest.mark.finite
def test_congruence_lattice_small():
    s = fo.builders.chain(3)
    m = to_finite_model(s)
    latt = congruence_lattice(m)
    assert len(latt) >= 1


@pytest.mark.finite
def test_homomorphism_identity():
    s = fo.builders.chain(2)
    m = to_finite_model(s)
    maps = homomorphisms(m, m)
    assert any(all(hom[a] == a for a in m.universe) for hom in maps)


@pytest.mark.finite
def test_is_lattice_b2():
    s = fo.builders.boolean_lattice(2)
    m = to_finite_model(s)
    assert is_lattice(m, "join", "meet")
