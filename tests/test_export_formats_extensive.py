"""Extensive TPTP and SMT-LIB export tests."""

from __future__ import annotations

import fopy as fo
from fopy.printing.smtlib import to_smtlib
from fopy.printing.tptp import to_tptp


def test_tptp_true_false():
    assert "$true" in to_tptp(fo.TrueF())
    assert "$false" in to_tptp(fo.FalseF())


def test_tptp_atom():
    x = fo.symbols("x")
    sig = fo.Signature(relations={"P": 1})
    P = sig.relation("P")
    out = to_tptp(fo.Atom(P, (x,)))
    assert "P" in out
    assert "fof(" in out


def test_tptp_forall_exists():
    x, y = fo.symbols("x y")
    phi = fo.ForAll(x, fo.Exists(y, fo.eq(x, y)))
    out = to_tptp(phi)
    assert "!" in out or "?" in out


def test_tptp_and_or():
    x = fo.symbols("x")
    sig = fo.Signature(relations={"P": 1, "Q": 1})
    P, Q = sig.relation("P"), sig.relation("Q")
    phi = fo.Atom(P, (x,)) & fo.Atom(Q, (x,))
    out = to_tptp(phi)
    assert "&" in out


def test_tptp_custom_name():
    x = fo.symbols("x")
    phi = fo.eq(x, x)
    out = to_tptp(phi, name="lemma1")
    assert "lemma1" in out


def test_smtlib_true():
    out = to_smtlib(fo.TrueF())
    assert out.startswith("(assert")
    assert "true" in out


def test_smtlib_eq():
    x, y = fo.symbols("x y")
    out = to_smtlib(fo.eq(x, y))
    assert "(=" in out


def test_smtlib_forall():
    x = fo.symbols("x")
    phi = fo.ForAll(x, fo.eq(x, x))
    out = to_smtlib(phi)
    assert "forall" in out


def test_smtlib_and_or():
    x, y = fo.symbols("x y")
    sig = fo.Signature(relations={"P": 1, "Q": 1})
    P, Q = sig.relation("P"), sig.relation("Q")
    phi = fo.Atom(P, (x,)) | fo.Atom(Q, (y,))
    out = to_smtlib(phi)
    assert "or" in out


def test_smtlib_apply_term():
    sig = fo.Signature(functions={"f": 1})
    x = fo.symbols("x")
    f = sig.function("f")
    t = fo.Apply(f, (x,))
    phi = fo.eq(t, x)
    out = to_smtlib(phi)
    assert "f" in out
