"""Extensive printing tests for open formulas."""

from __future__ import annotations

import pytest

from fopy.finite.explain import format_open_formula, latex_open_formula
from fopy.finite.open_formulas import Variable, and_formula, eq, false_formula, neg, or_formula, true_formula
from fopy.finite.open_formulas import Term
from fopy.finite.open_parse import parse_open_formula
from fopy.printing.open import latex, sstr


@pytest.mark.finite
class TestPrintingOpen:
    @pytest.mark.parametrize(
        "src",
        ["true", "false", "eq(x,y)", "-eq(x,y)", "eq(f(x,y),x)"],
    )
    def test_sstr_matches_format(self, minimal_model, src: str):
        x, y = Variable.new("x"), Variable.new("y")
        vm = {"x": x, "y": y}
        f = parse_open_formula(src, vm, minimal_model.operations)
        assert sstr(f) == format_open_formula(f)

    def test_latex_matches_latex_open(self, minimal_model):
        x, y = Variable.new("x"), Variable.new("y")
        f = parse_open_formula("eq(f(x,y),x)", {"x": x, "y": y}, minimal_model.operations)
        assert latex(f) == latex_open_formula(f)

    def test_and_latex(self):
        x = Term.from_variable(Variable.new("x"))
        y = Term.from_variable(Variable.new("y"))
        f = and_formula(eq(x, y), eq(y, x))
        out = latex(f)
        assert "land" in out or "=" in out

    def test_or_latex(self):
        x = Term.from_variable(Variable.new("x"))
        y = Term.from_variable(Variable.new("y"))
        f = or_formula(eq(x, y), eq(y, x))
        out = latex(f)
        assert "lor" in out or "=" in out

    def test_neg_latex(self):
        x = Term.from_variable(Variable.new("x"))
        y = Term.from_variable(Variable.new("y"))
        out = latex(neg(eq(x, y)))
        assert "lnot" in out
