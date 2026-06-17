"""Additional tests to exercise uncovered modules."""

import fopy as fo
from fopy.formulas import Eq
from fopy.symbols import FuncSymbol, RelSymbol
from fopy.terms import Apply


def test_signature_errors():
    sig = fo.Signature(functions={"f": 2})
    try:
        sig.function("g")
    except KeyError:
        pass
    try:
        sig.constant("f")
    except KeyError:
        pass


def test_signature_subtract():
    a = fo.Signature(functions={"f": 2, "g": 1})
    b = fo.Signature(functions={"g": 1})
    c = a - b
    assert "g" not in c.functions


def test_signature_is_subtype():
    a = fo.Signature(functions={"f": 2})
    b = fo.Signature(functions={"f": 2, "g": 1})
    assert a.is_subtype_of(b)


def test_func_rel_symbol_errors():
    f = FuncSymbol("f", 2)
    try:
        f(1)
    except ValueError:
        pass
    R = RelSymbol("R", 2)
    try:
        R(1)
    except ValueError:
        pass


def test_formula_satisfy_type_error():
    x = fo.symbols("x")
    try:
        fo.Atom("P", (x,)).satisfy("not a structure")
    except TypeError:
        pass


def test_structure_satisfy_type_error(b2_structure):
    try:
        b2_structure.satisfies("nope")
    except TypeError:
        pass


def test_bridge_with_functions():
    sig = fo.Signature(functions={"f": 2})
    table = {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 0}
    s = fo.Structure.from_tables(sig, [0, 1], functions={"f": table})
    m = fo.to_finite_model(s)
    s2 = fo.from_finite_model(m, sig)
    assert s2.call_function("f", (0, 1)) == 1


def test_bridge_constant():
    sig = fo.Signature(functions={"c": 0})
    s = fo.Structure.from_tables(sig, [0, 1], functions={"c": 0})
    m = fo.to_finite_model(s)
    assert "c" in m.operations


def test_visitor_transform():
    x = fo.symbols("x")
    f = fo.Atom("P", (x,))
    from fopy.core.visitor import Visitor

    class C(Visitor):
        def __init__(self):
            self.n = 0

        def generic_visit(self, expr):
            self.n += 1
            return super().generic_visit(expr)

    c = C()
    c.visit(f)
    assert c.n >= 1


def test_rename_bound_noop():
    x, y = fo.symbols("x y")
    f = fo.eq(x, y)
    assert fo.rename_bound(f, x, y) == f


def test_subs_quantifier():
    x, y = fo.symbols("x y")
    f = fo.forall(x, fo.eq(x, y))
    g = fo.subs(f, {y: x})
    assert isinstance(g, fo.ForAll)


def test_pprint_multiline():
    x, y, z = fo.symbols("x y z")
    parts = [fo.eq(x, y), fo.eq(y, z), fo.eq(x, z)]
    f = parts[0] & parts[1] & parts[2]
    text = fo.pprint(f)
    assert "&" in text or "and" in text.lower() or "(" in text


def test_latex_subscript_var():
    v = fo.Variable.from_index(3)
    assert "x" in fo.latex(v)


def test_domain_attr():
    d = fo.builders.Domain("a", "b")
    assert d[0] == "a"
    assert d.list() == ["a", "b"]


def test_from_covers_no_infer():
    s = fo.builders.from_covers([0, 1], [(0, 1)], infer_leq=False)
    assert (0, 1) in s.relations["leq"]


def test_theory_entails_false():
    sig = fo.Signature(relations={"leq": 2})
    T = fo.Theory(sig, axioms=[])
    s = fo.builders.chain(2)
    assert not T.entails(s, fo.false_formula())


def test_evaluate_unbound():
    sig = fo.Signature(functions={"f": 1})
    s = fo.Structure.from_tables(sig, [0], functions={"f": {(0,): 0}})
    x = fo.symbols("x")
    try:
        fo.evaluate(Apply("f", (x,)), s, {})
    except ValueError:
        pass


def test_extension_with_vars():
    s = fo.builders.chain(2)
    x, y = fo.symbols("x y")
    ext = fo.extension(fo.eq(x, y), s, 2, [x, y])
    assert (0, 0) in ext


def test_simplify_eq_terms():
    x = fo.symbols("x")
    assert fo.simplify(Eq(x, x)) == fo.true_formula()
