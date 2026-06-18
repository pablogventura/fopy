"""TPTP and SMT-LIB export."""

import fopy as fo
from fopy.printing.smtlib import to_smtlib
from fopy.printing.tptp import to_tptp


def test_tptp_export():
    x, y = fo.symbols("x y")
    phi = fo.forall(x, fo.eq(x, y))
    out = to_tptp(phi)
    assert out.startswith("fof(")
    assert "conjecture" in out


def test_smtlib_export():
    x, y = fo.symbols("x y")
    phi = fo.eq(x, y)
    out = to_smtlib(phi)
    assert out.startswith("(assert")
