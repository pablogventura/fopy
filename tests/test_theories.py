"""Signature and theories."""

import pytest

import fopy as fo


def test_signature_merge():
    a = fo.Signature(functions={"f": 2})
    b = fo.Signature(relations={"R": 2})
    c = a + b
    assert c.functions["f"] == 2
    assert c.relations["R"] == 2


def test_signature_subtype():
    a = fo.Signature(functions={"f": 2, "g": 1})
    sub = a.subtype(functions=["f"])
    assert "g" not in sub.functions


def test_theory_models_of_cardinality():
    sig = fo.Signature(relations={"leq": 2})
    T = fo.Theory(sig, axioms=[])
    models = list(T.models_of_cardinality(2))
    assert (
        len(models) == 2**4
    )  # two binary relations on 2 elements... wait one relation arity 2 on 2 el = 2^4 subsets
    assert all(len(m.universe) == 2 for m in models)


def test_theory_models_too_large():
    T = fo.Theory(fo.Signature(relations={"leq": 2}))
    with pytest.raises(ValueError):
        list(T.models_of_cardinality(5))


def test_theory_consequence_reflexive():
    x = fo.symbols("x")
    sig = fo.Signature(relations={"leq": 2})
    leq = fo.RelSymbol("leq", 2)
    refl = fo.forall(x, leq(x, x))
    T = fo.Theory(sig, axioms=[refl])
    assert T.consequence(refl, 2)


def test_theory_models_with_unary_function():
    sig = fo.Signature(functions={"f": 1})
    T = fo.Theory(sig, axioms=[])
    models = list(T.models_of_cardinality(2))
    assert len(models) == 4
    assert all(len(m.universe) == 2 for m in models)


def test_theory_models_function_axiom_identity():
    x = fo.symbols("x")
    sig = fo.Signature(functions={"f": 1})
    f = fo.Function("f", 1)
    identity = fo.forall(x, fo.eq(f(x), x))
    T = fo.Theory(sig, axioms=[identity])
    models = list(T.models_of_cardinality(2))
    assert len(models) == 1


def test_free_algebra_generators():
    sig = fo.Signature(functions={"f": 1})
    T = fo.Theory(sig, axioms=[])
    F = T.free_algebra_generators(2, max_depth=2)
    assert len(F.universe) >= 3
    assert F.call_function("f", (0,)) in F.universe
