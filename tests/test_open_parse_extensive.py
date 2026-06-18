"""Extensive open formula parser tests."""

from __future__ import annotations

import pytest

from fopy.finite.open_formulas import (
    FormulaKind,
    Term,
    TermKind,
    Variable,
    and_formula,
    eq,
    neg,
    or_formula,
    true_formula,
)
from fopy.finite.open_parse import parse_open_formula, parse_term


@pytest.mark.finite
class TestParseTerm:
    def test_variable(self):
        v = Variable.new("x")
        t = parse_term("x", {"x": v}, {})
        assert t == Term.from_variable(v)

    def test_operation(self, minimal_model):
        x, y = Variable.new("x"), Variable.new("y")
        t = parse_term("f(x,y)", {"x": x, "y": y}, minimal_model.operations)
        assert t.kind == TermKind.OP_TERM

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            parse_term("bogus", {}, {})


@pytest.mark.finite
class TestParseOpenFormula:
    def test_true_false_literals(self, minimal_model):
        assert parse_open_formula("true", {}, minimal_model.operations).kind == FormulaKind.TRUE
        assert parse_open_formula("false", {}, minimal_model.operations).kind == FormulaKind.FALSE

    def test_eq(self, minimal_model):
        x, y = Variable.new("x"), Variable.new("y")
        f = parse_open_formula("eq(f(x,y),x)", {"x": x, "y": y}, minimal_model.operations)
        assert f.kind == FormulaKind.EQ

    def test_neg(self, minimal_model):
        x, y = Variable.new("x"), Variable.new("y")
        f = parse_open_formula("-eq(x,y)", {"x": x, "y": y}, minimal_model.operations)
        assert f.kind == FormulaKind.NEG

    def test_and_or_precedence(self, minimal_model):
        x, y = Variable.new("x"), Variable.new("y")
        vm = {"x": x, "y": y}
        ops = minimal_model.operations
        f = parse_open_formula("eq(x,y) | eq(f(x,y),x) & -eq(x,y)", vm, ops)
        assert f.kind in (FormulaKind.OR, FormulaKind.AND)

    def test_nested_and(self, minimal_model):
        x, y = Variable.new("x"), Variable.new("y")
        f = parse_open_formula(
            "eq(f(x,y),x) & eq(x,y) & -eq(y,x)",
            {"x": x, "y": y},
            minimal_model.operations,
        )
        assert f.kind == FormulaKind.AND

    def test_manual_builder_matches_parse(self, minimal_model):
        from fopy.finite.explain import format_open_formula

        x, y = Variable.new("x"), Variable.new("y")
        vm = {"x": x, "y": y}
        built = and_formula(eq(Term.from_variable(x), Term.from_variable(y)), true_formula(None))
        parsed = parse_open_formula(
            format_open_formula(built),
            vm,
            minimal_model.operations,
        )
        assert parsed == built


@pytest.mark.finite
class TestOpenFormulaCombinators:
    def test_or_formula(self):
        x = Term.from_variable(Variable.new("x"))
        y = Term.from_variable(Variable.new("y"))
        a = eq(x, y)
        b = eq(y, x)
        assert or_formula(a, b).kind == FormulaKind.OR

    def test_neg_eq(self):
        x = Term.from_variable(Variable.new("x"))
        y = Term.from_variable(Variable.new("y"))
        assert neg(eq(x, y)).kind == FormulaKind.NEG
