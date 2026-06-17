"""Structure builders."""

import fopy as fo


def test_chain():
    s = fo.builders.chain(5)
    assert len(s.universe) == 5
    assert "leq" in s.signature.relations


def test_boolean_lattice_b2(b2_structure):
    assert len(b2_structure.universe) == 4


def test_m3_covers(m3_structure):
    assert len(m3_structure.universe) == 4
    leq = m3_structure.relations["leq"]
    assert ("0", "3") in leq


def test_from_cayley():
    sig = fo.Signature(functions={"f": 2})
    s = fo.builders.from_cayley(sig, "f", [0, 1], [[0, 1], [1, 0]])
    assert s.call_function("f", (0, 1)) == 1


def test_fluent_builder():
    sig = fo.Signature(relations={"leq": 2})
    b = (
        fo.builders.build(sig)
        .universe(0, 1, 2)
        .relation("leq", {(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)})
        .build()
    )
    assert len(b.universe) == 3
