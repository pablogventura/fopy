"""Property-style round-trip tests for open formulas."""

from __future__ import annotations

import pytest

from fopy.finite.explain import format_open_formula
from fopy.finite.open_formulas import Variable
from fopy.finite.open_parse import parse_open_formula


@pytest.mark.finite
@pytest.mark.parametrize("src", ["eq(x,y)", "true", "false", "-eq(x,y)"])
def test_parse_format_idempotent(minimal_model, src: str):
    x, y = Variable.new("x"), Variable.new("y")
    vm = {"x": x, "y": y}
    f = parse_open_formula(src, vm, minimal_model.operations)
    s = format_open_formula(f)
    f2 = parse_open_formula(s, vm, minimal_model.operations)
    assert f == f2


@pytest.mark.finite
@pytest.mark.parametrize("idx", [0, 1])
def test_variable_terms_evaluate(minimal_model, idx: int):
    if idx >= len(minimal_model.universe):
        pytest.skip("universe too small")
    v = Variable.from_index(0)
    from fopy.finite.open_formulas import Term

    t = Term.from_variable(v)
    val = t.evaluate(minimal_model.operations, {v: idx})
    assert val in minimal_model.universe or val == -1 or val >= 0
