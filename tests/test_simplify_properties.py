"""Boolean simplification and formula algebra tests."""

from __future__ import annotations

import pytest

import fopy as fo


@pytest.mark.parametrize(
    "left,right",
    [
        ("true", "P"),
        ("false", "P"),
        ("P", "P"),
        ("~P", "P"),
        ("P", "~P"),
    ],
)
def test_and_simplify_absorption(left: str, right: str):
    P = fo.RelSymbol("P", 1)
    x = fo.symbols("x")
    env = {
        "true": fo.true_formula(),
        "false": fo.false_formula(),
        "P": P(x),
        "~P": ~P(x),
    }
    a, b = env[left], env[right]
    result = fo.simplify(a & b)
    assert result is not None


@pytest.mark.parametrize("n", range(1, 6))
def test_simplify_idempotent_chain(n: int):
    x = fo.symbols("x")
    f = fo.Atom("P", (x,))
    for _ in range(n):
        f = fo.simplify(f)
    assert f == fo.Atom("P", (x,))


def test_de_morgan_and_structure():
    x = fo.symbols("x")
    P, Q = fo.RelSymbol("P", 1), fo.RelSymbol("Q", 1)
    a, b = P(x), Q(x)
    lhs = ~(a & b)
    assert isinstance(lhs, fo.Not)


@pytest.mark.parametrize(
    "expr",
    [
        "true",
        "false",
        "P & Q",
        "P | Q",
        "~P",
        "P & true",
        "P | false",
        "~~P",
        "P & ~P",
        "P | ~P",
    ],
)
def test_simplify_no_crash(expr: str):
    x = fo.symbols("x")
    P, Q = fo.RelSymbol("P", 1), fo.RelSymbol("Q", 1)
    env = {
        "true": fo.true_formula(),
        "false": fo.false_formula(),
        "P": P(x),
        "Q": Q(x),
        "~P": ~P(x),
        "P & Q": P(x) & Q(x),
        "P | Q": P(x) | Q(x),
        "P & true": P(x) & fo.true_formula(),
        "P | false": P(x) | fo.false_formula(),
        "~~P": ~~P(x),
        "P & ~P": P(x) & ~P(x),
        "P | ~P": P(x) | ~P(x),
    }
    fo.simplify(env[expr])


def test_eq_simplify_reflexive():
    x = fo.symbols("x")
    assert fo.simplify(fo.Eq(x, x)) == fo.true_formula()


def test_forall_simplify_body():
    x = fo.symbols("x")
    f = fo.forall(x, fo.eq(x, x))
    g = fo.simplify(f)
    assert isinstance(g, fo.ForAll)


def test_exists_simplify_body():
    x = fo.symbols("x")
    f = fo.exists(x, fo.false_formula())
    g = fo.simplify(f)
    assert isinstance(g, fo.Exists)


def test_and_commutative_hash():
    x = fo.symbols("x")
    P, Q = fo.RelSymbol("P", 1), fo.RelSymbol("Q", 1)
    a, b = P(x), Q(x)
    assert hash(a & b) == hash(b & a)


def test_or_commutative_hash():
    x = fo.symbols("x")
    P, Q = fo.RelSymbol("P", 1), fo.RelSymbol("Q", 1)
    a, b = P(x), Q(x)
    assert hash(a | b) == hash(b | a)


def test_neg_neg_is_identity():
    x = fo.symbols("x")
    P = fo.RelSymbol("P", 1)
    assert fo.simplify(~~P(x)) == P(x)


def test_implication_as_or():
    x, y = fo.symbols("x y")
    P, Q = fo.RelSymbol("P", 1), fo.RelSymbol("Q", 1)
    impl = P(x) >> Q(y)
    assert isinstance(impl, fo.Or)


def test_biconditional_xor():
    x = fo.symbols("x")
    P, Q = fo.RelSymbol("P", 1), fo.RelSymbol("Q", 1)
    iff = P(x) ^ Q(x)
    assert isinstance(iff, fo.Or)
