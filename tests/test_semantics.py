"""Semantics and satisfaction."""

import fopy as fo


def test_satisfy_chain():
    s = fo.builders.chain(3)
    x, y = fo.symbols("x y")
    leq = fo.RelSymbol("leq", 2)
    f = leq(x, y)
    assert fo.satisfy(f, s, {x: 0, y: 2})
    assert not fo.satisfy(f, s, {x: 2, y: 0})


def test_extension_equality():
    s = fo.builders.chain(2)
    x, y = fo.symbols("x y")
    diag = fo.extension(fo.eq(x, y), s, 2, [x, y])
    assert diag == {(0, 0), (1, 1)}


def test_evaluate_term():
    table = {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 0}
    sig = fo.Signature(functions={"f": 2})
    s = fo.structures.Structure.from_tables(sig, [0, 1], functions={"f": table})
    x, y = fo.symbols("x y")
    t = fo.Apply("f", (x, y))
    assert fo.evaluate(t, s, {x: 0, y: 1}) == 1
