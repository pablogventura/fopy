"""Property-based tests (optional hypothesis)."""

import fopy as fo
from hypothesis import given
from hypothesis import strategies as st


@given(st.booleans(), st.booleans())
def test_simplify_idempotent_bool(a: bool, b: bool):
    x = fo.symbols("x")
    f = fo.Atom("P", (x,)) if a else fo.true_formula()
    g = fo.Atom("Q", (x,)) if b else fo.false_formula()
    h = f & g
    s1 = fo.simplify(h)
    s2 = fo.simplify(s1)
    assert s1 == s2


@given(st.integers(min_value=2, max_value=6))
def test_chain_covers(n: int):
    s = fo.builders.chain(n)
    assert len(s.universe) == n
