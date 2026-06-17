"""Builder equivalence tests."""

import fopy as fo


def test_chain_vs_covers(chain5_structure):
    covers = [(i, i + 1) for i in range(4)]
    s2 = fo.builders.from_covers(list(range(5)), covers)
    assert len(s2.universe) == len(chain5_structure.universe)


def test_b2_vs_catalog(b2_structure):
    s = fo.builders.boolean_lattice(2)
    assert len(s.universe) == len(b2_structure.universe)


def test_retrombo_size(retrombo_structure):
    assert len(retrombo_structure.universe) == 4


def test_b3_size(b3_structure):
    assert len(b3_structure.universe) == 8
