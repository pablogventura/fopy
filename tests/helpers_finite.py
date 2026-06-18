"""Test helpers for finite definability."""

from __future__ import annotations

from fopy.finite import explain_definability, is_open_definable
from fopy.finite.models import Model
from fopy.finite.open_formulas import Formula
from fopy.finite.relops import Relation


def assert_formula_defines(model: Model, formula: Formula, relation: Relation) -> None:
    """Assert that open formula *formula* has the same extension as *relation* on *model*.

    Args:
        model: Finite algebra used for evaluation.
        formula: Quantifier-free witness formula.
        relation: Expected target relation.

    Raises:
        AssertionError: If extensions differ.
    """
    ext = formula.extension(model, relation.arity)
    assert ext == set(relation.r)


def assert_explain_agrees_with_check(model: Model, target: Relation) -> None:
    """Assert :func:`~fopy.finite.explain_definability` matches :func:`~fopy.finite.is_open_definable`.

    Args:
        model: Finite model under test.
        target: Target relation whose symbol is passed to ``explain_definability``.

    Raises:
        AssertionError: If definability verdicts disagree.
    """
    check = is_open_definable(model, target)
    report = explain_definability(model, target.sym, max_synth_depth=0)
    assert report.definable == check.definable
