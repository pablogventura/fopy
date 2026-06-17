"""Golden/reference output tests."""

import fopy as fo


def test_latex_forall_exists():
    x, y = fo.symbols("x y")
    f = fo.forall(x, fo.exists(y, fo.eq(x, y)))
    tex = fo.latex(f)
    assert "\\forall" in tex
    assert "\\exists" in tex


def test_sstr_implication():
    x, y = fo.symbols("x y")
    f = fo.parse_formula("R(x,y) -> P(x)", rels={"R": 2, "P": 1})
    assert "forall" not in fo.sstr(f)
    assert "|" in fo.sstr(f) or "~" in fo.sstr(f)


def test_unicode_parser():
    f = fo.parse_formula("∀x ∃y R(x,y)", rels={"R": 2})
    assert isinstance(f, fo.ForAll)
