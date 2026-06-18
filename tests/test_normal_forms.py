"""Normal form transforms."""

import fopy as fo


def test_to_nnf_idempotent():
    x, y = fo.symbols("x y")
    phi = fo.forall(x, fo.Not(fo.exists(y, fo.Not(fo.eq(x, y)))))
    nnf = fo.to_nnf(phi)
    assert fo.to_nnf(nnf) == nnf


def test_to_prenex():
    x, y = fo.symbols("x y")
    phi = fo.forall(x, fo.exists(y, fo.eq(x, y)))
    prenex = fo.to_prenex(phi)
    assert isinstance(prenex, fo.ForAll)
