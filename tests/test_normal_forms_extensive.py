"""Tests for CNF and DNF normal forms."""

from __future__ import annotations

import fopy as fo


def test_nnf_double_negation():
    x = fo.symbols("x")
    phi = fo.Not(fo.Not(fo.eq(x, x)))
    nnf = fo.to_nnf(phi)
    assert isinstance(nnf, (fo.Eq, fo.TrueF))


def test_cnf_from_or_and():
    x, y = fo.symbols("x y")
    phi = (fo.eq(x, y) & fo.Not(fo.eq(x, x))) | fo.eq(y, y)
    cnf = fo.to_cnf(phi)
    assert cnf is not None


def test_dnf_from_or_and():
    x, y = fo.symbols("x y")
    phi = (fo.eq(x, y) & fo.Not(fo.eq(x, x))) | fo.eq(y, y)
    dnf = fo.to_dnf(phi)
    assert dnf is not None
