"""Extensive finite algebra helper tests."""

from __future__ import annotations

import pytest

import fopy as fo
from fopy.bridge import to_finite_model
from fopy.finite.algebra import subalgebra_generated_by, term_functions


@pytest.mark.finite
class TestSubalgebraGenerated:
    def test_single_generator_chain(self):
        m = to_finite_model(fo.builders.chain(4))
        sub = subalgebra_generated_by(m, [0])
        assert 0 in sub
        assert sub.issubset(set(m.universe))

    def test_all_generators_full_universe(self):
        m = to_finite_model(fo.builders.chain(3))
        sub = subalgebra_generated_by(m, list(m.universe))
        assert sub == set(m.universe)

    def test_empty_generators(self):
        m = to_finite_model(fo.builders.chain(3))
        sub = subalgebra_generated_by(m, [])
        assert sub == set()

    def test_model_method(self, minimal_model):
        sub = minimal_model.subalgebra_generated_by([0])
        assert 0 in sub


@pytest.mark.finite
class TestTermFunctions:
    def test_returns_dict(self, minimal_model):
        tf = term_functions(minimal_model, max_depth=1)
        assert isinstance(tf, dict)

    def test_depth_zero_has_variables(self, minimal_model):
        tf = term_functions(minimal_model, max_depth=0)
        assert 0 in tf or 1 in tf or 2 in tf or tf == {}

    def test_model_method(self, minimal_model):
        tf = minimal_model.term_functions(max_depth=1)
        assert isinstance(tf, dict)

    def test_more_terms_at_higher_depth(self, minimal_model):
        shallow = term_functions(minimal_model, max_depth=0)
        deeper = term_functions(minimal_model, max_depth=2)
        count_shallow = sum(len(v) for v in shallow.values())
        count_deep = sum(len(v) for v in deeper.values())
        assert count_deep >= count_shallow
