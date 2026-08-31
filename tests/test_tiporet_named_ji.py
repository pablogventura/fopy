"""Regression: tiporet 2x2 arity-3 EP JI match NamedTernaryAtom catalogue (22/22)."""

from __future__ import annotations

from itertools import product

import pytest

from fopy.finite.lindenbaum import chain_product_lattice, join_irreducibles, relation_fingerprint

pytestmark = pytest.mark.finite


def _le(meet, a: int, b: int) -> bool:
    return meet.call((a, b)) == a


def _named_forms(model):
    """Python mirror of Lean NamedTernaryAtom on the chain-product lattice."""
    meet = model.operations["meet"]
    join = model.operations["join"]
    universe = list(model.universe)
    all_triples = list(product(universe, repeat=3))

    def m(a, b):
        return meet.call((a, b))

    def j(a, b):
        return join.call((a, b))

    def le(a, b):
        return _le(meet, a, b)

    forms: dict[str, set[tuple[int, ...]]] = {}
    forms["diag3"] = {t for t in all_triples if t[0] == t[1] == t[2]}
    forms["eq01"] = {t for t in all_triples if t[0] == t[1]}
    forms["eq02"] = {t for t in all_triples if t[0] == t[2]}
    forms["eq12"] = {t for t in all_triples if t[1] == t[2]}
    forms["eq01Ge02"] = {t for t in all_triples if t[0] == t[1] and le(t[2], t[0])}
    forms["eq01Le02"] = {t for t in all_triples if t[0] == t[1] and le(t[0], t[2])}
    forms["eq02Le12"] = {t for t in all_triples if t[0] == t[2] and le(t[1], t[2])}
    forms["eq02Ge12"] = {t for t in all_triples if t[0] == t[2] and le(t[2], t[1])}
    forms["eq12Le01"] = {t for t in all_triples if t[1] == t[2] and le(t[0], t[1])}
    forms["eq12Ge01"] = {t for t in all_triples if t[1] == t[2] and le(t[1], t[0])}
    forms["meetGraph"] = {t for t in all_triples if t[2] == m(t[0], t[1])}
    forms["joinGraph"] = {t for t in all_triples if t[2] == j(t[0], t[1])}
    forms["meetGraph02"] = {t for t in all_triples if t[1] == m(t[0], t[2])}
    forms["meetGraph12"] = {t for t in all_triples if t[0] == m(t[1], t[2])}
    forms["joinGraph02"] = {t for t in all_triples if t[1] == j(t[0], t[2])}
    forms["joinGraph12"] = {t for t in all_triples if t[0] == j(t[1], t[2])}
    forms["le012"] = {t for t in all_triples if le(t[0], t[1]) and le(t[1], t[2])}
    forms["ge012"] = {t for t in all_triples if le(t[2], t[1]) and le(t[1], t[0])}
    forms["cornerTopBot"] = {t for t in all_triples if le(t[1], t[2]) and le(t[2], t[0])}
    forms["cornerBotTop"] = {t for t in all_triples if le(t[2], t[1]) and le(t[0], t[2])}
    forms["cornerAtomTopBot"] = {t for t in all_triples if le(t[2], t[0]) and le(t[0], t[1])}
    forms["cornerAtomBotTop"] = {t for t in all_triples if le(t[0], t[2]) and le(t[1], t[0])}
    return forms


def test_tiporet_ep_ji_all_named_22():
    model = chain_product_lattice(2, 2)
    ep = join_irreducibles(model, 3, fragment="ep", model_key="C2x2")
    forms = _named_forms(model)
    form_fps = {name: relation_fingerprint(frozenset(rel)) for name, rel in forms.items()}

    assert ep.count == 22
    unnamed: list[str] = []
    for ji in ep.join_irreducibles:
        fp = relation_fingerprint(ji)
        if not any(f == fp for f in form_fps.values()):
            unnamed.append(fp)
    assert unnamed == [], f"unnamed JI fingerprints: {unnamed}"


def test_corner_ji_fingerprints():
    """Golden fingerprints for the four non-chain corner JI (N1a)."""
    model = chain_product_lattice(2, 2)
    forms = _named_forms(model)
    expected = {
        "cornerTopBot": "8e484da6175975ec",
        "cornerBotTop": "828ce1c5bde3adba",
        "cornerAtomTopBot": "fce4d0995f7dcb24",
        "cornerAtomBotTop": "13b795af6b817059",
    }
    for name, fp in expected.items():
        assert relation_fingerprint(frozenset(forms[name])) == fp


def test_tiporet_end_orbits_match_named_ji():
    """Th2 spine: |End|=16 and every End-orbit of a triple equals a named JI."""
    from fopy.finite.lindenbaum import algebra_polymorphisms

    model = chain_product_lattice(2, 2)
    endos = algebra_polymorphisms(model, max_arity=1)[1]
    assert len(endos) == 16

    forms = _named_forms(model)
    form_sets = {frozenset(rel) for rel in forms.values()}
    assert len(form_sets) == 22

    universe = list(model.universe)
    orbits: set[frozenset[tuple[int, ...]]] = set()
    for t in product(universe, repeat=3):
        orb = frozenset(tuple(e[x] for x in t) for e in endos)
        orbits.add(orb)
        assert orb in form_sets, f"orbit of {t} not a named JI"
    assert len(orbits) == 22
