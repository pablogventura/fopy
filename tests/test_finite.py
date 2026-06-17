"""Finite models, parsing, and HIT definability."""

from pathlib import Path

import pytest

from fopy.finite import Model, is_open_definable
from fopy.parse import parse_model


def test_parse_minimal_model(minimal_model: Model):
    assert minimal_model.universe == [0, 1]
    assert "f" in minimal_model.operations
    assert "T0" in minimal_model.targets


def test_parse_algebra_model(fixtures_dir: Path):
    model = parse_model(fixtures_dir / "algebra.model", preprocess=False)
    assert len(model.universe) >= 2


def test_formula_con_igual_rejects_eq(fixtures_dir: Path):
    with pytest.raises(ValueError, match="eq"):
        parse_model(fixtures_dir / "formula_con_igual.model", preprocess=False)


def test_is_open_definable_minimal(minimal_model: Model):
    target = minimal_model.targets["T0"]
    result = is_open_definable(minimal_model, target)
    assert isinstance(result.definable, bool)


@pytest.mark.finite
def test_split_targets_extension(minimal_model: Model):
    from fopy.finite.preprocessing import split_targets

    rel = minimal_model.targets["T0"]
    parts = split_targets(rel)
    assert len(parts) >= 1


def test_open_formula_parser():
    from fopy.finite.open_formulas import Variable
    from fopy.finite.open_parse import parse_open_formula
    from fopy.finite.relops import Operation

    ops = {"f": Operation.new("f", 2)}
    vars_map = {"x": Variable.new("x"), "y": Variable.new("y")}
    f = parse_open_formula("eq(f(x,y),x) & -eq(f(x,y),y)", vars_map, ops)
    assert f is not None
