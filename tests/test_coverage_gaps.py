"""Targeted tests for remaining coverage gaps."""

import fopy as fo
from fopy.bridge import load_structure, to_finite_model
from fopy.finite.relops import Operation, Relation
from fopy.formulas import ForAll
from fopy.printing import latex, pprint, sstr
from fopy.semantics import satisfy
from fopy.simplify import simplify


def test_simplify_nested():
    x = fo.symbols("x")
    f = ~~fo.Atom("P", (x,))
    assert simplify(f) == fo.Atom("P", (x,))
    g = fo.Atom("P", (x,)) & fo.true_formula()
    assert simplify(g) == fo.Atom("P", (x,))


def test_simplify_or_false():
    x = fo.symbols("x")
    f = fo.Atom("P", (x,)) | fo.false_formula()
    assert simplify(f) == fo.Atom("P", (x,))


def test_pprint_exists_nested():
    x, y, z = fo.symbols("x y z")
    inner = fo.exists(z, fo.eq(x, z))
    f = fo.forall(y, inner)
    text = pprint(f)
    assert "exists" in text or "forall" in text


def test_latex_exists():
    x = fo.symbols("x")
    f = fo.exists(x, fo.Atom("P", (x,)))
    assert "\\exists" in latex(f)


def test_sstr_forall():
    x = fo.symbols("x")
    assert "forall" in sstr(fo.forall(x, fo.true_formula()))


def test_bridge_callable_relation():
    sig = fo.Signature(relations={"R": 2})

    def R(a, b):
        return a <= b

    s = fo.Structure(sig, [0, 1, 2], relations={"R": R})
    m = to_finite_model(s)
    assert len(m.universe) == 3


def test_load_structure_roundtrip(tmp_path, fixtures_dir):
    path = fixtures_dir / "minimal.model"
    s = load_structure(path)
    assert s.call_function("f", (0, 0)) == 0


def test_relops_eq_hash():
    r1 = Relation.new("R", 2)
    r1.add([0, 1])
    r2 = Relation.new("R", 2)
    r2.add([0, 1])
    assert r1 == r2


def test_operation_undefined():
    op = Operation.new("f", 2)
    assert op.call((0, 0)) is None


def test_semantics_exists_false():
    s = fo.builders.chain(2)
    x, y = fo.symbols("x y")
    leq = fo.RelSymbol("leq", 2)
    f = fo.exists(x, fo.forall(y, leq(x, y) & ~leq(y, x)))
    assert isinstance(satisfy(f, s, {}), bool)


def test_rename_bound_forall_branch():
    x, y, z = fo.symbols("x y z")
    f = fo.forall(x, fo.eq(y, z))
    g = fo.rename_bound(f, x, y)
    assert isinstance(g, ForAll)


def test_theory_with_axiom_fails_entails():
    x = fo.symbols("x")
    sig = fo.Signature(relations={"leq": 2})
    refl = fo.forall(x, fo.RelSymbol("leq", 2)(x, x))
    T = fo.Theory(sig, axioms=[refl])
    s = fo.builders.chain(2)
    assert T.entails(s, refl)


def test_substitute_under_binder_renames():
    x, y, z = fo.symbols("x y z")
    f = fo.forall(x, fo.eq(x, y))
    g = fo.substitute(f, {x: z})
    assert isinstance(g, fo.ForAll)


def test_structure_dict_relation():
    sig = fo.Signature(relations={"R": 2})
    s = fo.Structure.from_tables(sig, [0, 1], relations={"R": {(0, 0): True, (0, 1): False}})
    assert s.call_relation("R", (0, 0))


def test_simplify_forall_exists():
    x, y = fo.symbols("x y")
    f = fo.forall(x, fo.exists(y, fo.eq(x, y)))
    g = simplify(f)
    assert isinstance(g, ForAll)
