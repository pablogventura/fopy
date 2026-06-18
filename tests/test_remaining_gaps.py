"""Tests for remaining vision-doc-01 gaps."""

from __future__ import annotations

import pytest

import fopy as fo
from fopy.core.hashcons import clear_pool, disable_hashcons, enable_hashcons
from fopy.finite.eval_cache import EvalCache
from fopy.finite.model_checking import models
from fopy.semantics import satisfy, sort_carrier
from fopy.solvers import prove_formula, z3_available
from fopy.terms import Apply


def test_eval_cache_used_by_model_checking(minimal_model):
    from fopy.finite.open_formulas import Term as OTerm
    from fopy.finite.open_formulas import Variable as OVar
    from fopy.finite.open_formulas import eq

    v0 = OVar.from_index(0)
    f = eq(OTerm.from_variable(v0), OTerm.from_variable(v0))
    cache = EvalCache()
    assert models(minimal_model, f, cache=cache)
    assert cache.misses >= 1


def test_many_sorted_semantics():
    from fopy.sorts import Sort

    sig = fo.Signature()
    s = fo.Structure(
        sig,
        universe=[0, 1, 2],
        universes={"U": [0, 1], "V": [0, 2]},
    )
    assert sort_carrier(s, "U") == [0, 1]
    assert sort_carrier(s, Sort("V")) == [0, 2]
    x = fo.Variable("x", Sort("U"))
    y = fo.Variable("y", Sort("V"))
    phi = fo.forall(x, fo.exists(y, fo.eq(x, y)))
    assert not satisfy(phi, s, {})


def test_hashcons_apply():
    disable_hashcons()
    clear_pool()
    a = Apply("f", (fo.symbols("x"),))
    b = Apply("f", (fo.symbols("x"),))
    assert a is not b
    enable_hashcons()
    clear_pool()
    x = fo.symbols("x")
    c = Apply("f", (x,))
    d = Apply("f", (x,))
    assert c is d
    disable_hashcons()
    clear_pool()


def test_tff_export():
    phi = fo.parse_formula("forall x:U exists y:V R(x,y)", rels={"R": 2})
    assert phi.to_tff().startswith("tff(")
    assert "y:V" in phi.to_tff()


@pytest.mark.finite
def test_formula_search_pp_fragment(minimal_model):
    from fopy.finite import FormulaSearch

    tname = next(iter(minimal_model.targets))
    rel = minimal_model.targets[tname]
    result = FormulaSearch(minimal_model, rel, fragment="pp").run()
    assert result.formula is not None


def test_formula_complexity():
    from fopy.finite.open_formulas import Term as OTerm
    from fopy.finite.open_formulas import Variable as OVar
    from fopy.finite.open_formulas import eq
    from fopy.finite.synthesis import formula_complexity

    v = OVar.from_index(0)
    t = OTerm.from_variable(v)
    score = formula_complexity(eq(t, t))
    assert score[0] >= 0 and score[1] >= 1


@pytest.mark.solvers
def test_prove_tautology():
    if not z3_available():
        pytest.skip("z3 not installed")
    x = fo.symbols("x")
    assert prove_formula(fo.eq(x, x)) is True


def test_numpy_eq_extension(minimal_model):
    from fopy.finite.eval_fast import numpy_eq_extension, try_fast_defining_check
    from fopy.finite.open_formulas import OpSym, eq
    from fopy.finite.open_formulas import Term as OTerm
    from fopy.finite.open_formulas import Variable as OVar

    v0 = OVar.from_index(0)
    x = OTerm.from_variable(v0)
    fx = OTerm.op_term(OpSym("f", 2), (x, x))
    f = eq(fx, x)
    ext = numpy_eq_extension(minimal_model, f, 1)
    assert ext is not None
    assert (0,) in ext
    tname = next(iter(minimal_model.targets))
    rel = minimal_model.targets[tname]
    assert try_fast_defining_check(minimal_model, f, rel) in (True, False, None)


@pytest.mark.solvers
def test_smt_synthesize_reflexive(minimal_model):
    from fopy.finite.synthesis_smt import smt_synthesize

    if not z3_available():
        pytest.skip("z3 not installed")
    tname = next(iter(minimal_model.targets))
    rel = minimal_model.targets[tname]
    result = smt_synthesize(minimal_model, rel, max_depth=1)
    assert result.formula is not None
    assert result.backend.startswith("z3")
