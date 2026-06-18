"""Printing for open formulas."""

from __future__ import annotations

import pytest

from fopy.finite.open_formulas import Variable
from fopy.finite.open_parse import parse_open_formula
from fopy.printing.open import latex, sstr


@pytest.mark.finite
def test_sstr_roundtrip(minimal_model):
    ops = minimal_model.operations
    x, y = Variable.new("x"), Variable.new("y")
    f = parse_open_formula("eq(f(x,y),x) & -eq(x,y)", {"x": x, "y": y}, ops)
    s = sstr(f)
    f2 = parse_open_formula(s, {"x": x, "y": y}, ops)
    assert f == f2


@pytest.mark.finite
def test_latex_open():
    x = Variable.new("x")
    y = Variable.new("y")
    from fopy.finite.open_formulas import Term, eq

    f = eq(Term.from_variable(x), Term.from_variable(y))
    assert "x" in latex(f)
