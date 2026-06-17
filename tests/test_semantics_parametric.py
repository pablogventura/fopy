"""Parametrized semantics tests on standard structures."""

from __future__ import annotations

import pytest

import fopy as fo
from fopy.semantics import evaluate, extension, satisfy


@pytest.fixture
def leq_sym():
    return fo.RelSymbol("leq", 2)


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6])
def test_chain_reflexive(n: int, leq_sym):
    s = fo.builders.chain(n)
    x = fo.symbols("x")
    f = fo.forall(x, leq_sym(x, x))
    assert satisfy(f, s, {})


@pytest.mark.parametrize("n", [2, 3, 4])
def test_chain_transitive(n: int, leq_sym):
    s = fo.builders.chain(n)
    x, y, z = fo.symbols("x y z")
    trans = fo.forall(x, fo.forall(y, fo.forall(z, (leq_sym(x, y) & leq_sym(y, z)) >> leq_sym(x, z))))
    assert satisfy(trans, s, {})


@pytest.mark.parametrize("a,b,expected", [(0, 0, True), (0, 1, True), (1, 0, False), (1, 1, True)])
def test_chain_assignments(a: int, b: int, expected: bool, leq_sym):
    s = fo.builders.chain(2)
    x, y = fo.symbols("x y")
    assert satisfy(leq_sym(x, y), s, {x: a, y: b}) is expected


def test_b2_meet_equals_and(b2_structure):
    x, y = fo.symbols("x y")
    meet = fo.FuncSymbol("meet", 2)
    for a in b2_structure.universe:
        for b in b2_structure.universe:
            ma = evaluate(meet(x, y), b2_structure, {x: a, y: b})
            assert isinstance(ma, int)


def test_extension_diagonal(b2_structure):
    x, y = fo.symbols("x y")
    diag = extension(fo.eq(x, y), b2_structure, 2, [x, y])
    assert all(a == b for a, b in diag)


def test_m3_incomparable_exists(m3_structure, leq_sym):
    x, y = fo.symbols("x y")
    f = fo.exists(x, fo.exists(y, leq_sym(x, y) & ~leq_sym(y, x)))
    assert satisfy(f, m3_structure, {})


def test_n5_not_total_order(n5_structure, leq_sym):
    x, y = fo.symbols("x y")
    total = fo.forall(x, fo.forall(y, leq_sym(x, y) | leq_sym(y, x)))
    assert not satisfy(total, n5_structure, {})


def test_retrombo_top_exists(retrombo_structure, leq_sym):
    x, y = fo.symbols("x y")
    f = fo.exists(x, fo.forall(y, leq_sym(x, y)))
    assert satisfy(f, retrombo_structure, {})


def test_evaluate_constant_zero_ary():
    sig = fo.Signature(functions={"c": 0})
    s = fo.structures.Structure.from_tables(sig, [0], functions={"c": 42})
    assert evaluate(fo.Constant("c"), s, {}) == 42


def test_satisfy_true_false(b2_structure):
    assert satisfy(fo.true_formula(), b2_structure, {})
    assert not satisfy(fo.false_formula(), b2_structure, {})
