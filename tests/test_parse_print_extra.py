"""Parse and printing extended coverage."""

import fopy as fo
from fopy.parse import parse_formula


def test_parse_biconditional():
    f = parse_formula("P(x) <-> Q(x)", rels={"P": 1, "Q": 1})
    assert isinstance(f, fo.And)


def test_parse_implication_reverse():
    f = parse_formula("P(x) <- Q(x)", rels={"P": 1, "Q": 1})
    assert f is not None


def test_parse_unicode_quantifiers():
    f = parse_formula("∀x ∃y R(x,y)", rels={"R": 2})
    assert isinstance(f, fo.ForAll)


def test_printing_false_true():
    assert "true" in fo.sstr(fo.true_formula())
    assert "false" in fo.sstr(fo.false_formula())


def test_latex_and_or():
    x = fo.symbols("x")
    f = fo.Atom("P", (x,)) & fo.Atom("Q", (x,))
    tex = fo.latex(f)
    assert "\\land" in tex


def test_pprint_forall():
    x = fo.symbols("x")
    f = fo.forall(x, fo.Atom("P", (x,)))
    assert "forall" in fo.pprint(f)
