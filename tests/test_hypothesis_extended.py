"""Extended Hypothesis property tests."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

import fopy as fo


@given(st.integers(min_value=2, max_value=8))
@settings(max_examples=30)
def test_chain_has_reflexive_leq(n: int):
    s = fo.builders.chain(n)
    x = fo.symbols("x")
    leq = fo.RelSymbol("leq", 2)
    assert fo.satisfy(fo.forall(x, leq(x, x)), s, {})


@given(st.integers(min_value=1, max_value=3))
@settings(max_examples=20)
def test_boolean_lattice_universe_size(n: int):
    s = fo.builders.boolean_lattice(n)
    assert len(s.universe) == 2**n


@given(st.booleans(), st.booleans(), st.booleans())
@settings(max_examples=40)
def test_simplify_and_true_false(a: bool, b: bool, c: bool):
    x = fo.symbols("x")
    P = fo.RelSymbol("P", 1)
    parts = []
    if a:
        parts.append(P(x))
    if b:
        parts.append(fo.true_formula())
    if c:
        parts.append(fo.false_formula())
    if not parts:
        return
    f = parts[0]
    for p in parts[1:]:
        f = f & p
    s = fo.simplify(f)
    assert s is not None


@given(st.integers(min_value=0, max_value=5))
@settings(max_examples=20)
def test_variable_from_index_roundtrip(i: int):
    v = fo.Variable.from_index(i)
    assert v.sym.startswith("x")


@given(st.text(alphabet="abc", min_size=1, max_size=3))
@settings(max_examples=15)
def test_symbols_parse_names(name: str):
    if not name.strip():
        return
    v = fo.symbols(name)
    assert isinstance(v, fo.Variable)
