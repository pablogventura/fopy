"""First-order formulas."""

from __future__ import annotations

from typing import cast

from fopy.core.basic import Basic
from fopy.symbols import Variable
from fopy.terms import Term


def _and_formula(a: Formula, b: Formula) -> Formula:
    if isinstance(a, TrueF):
        return b
    if isinstance(b, TrueF):
        return a
    if isinstance(a, FalseF) or isinstance(b, FalseF):
        return FalseF()
    if isinstance(a, Not) and a.arg == b:
        return FalseF()
    if isinstance(b, Not) and b.arg == a:
        return FalseF()
    if isinstance(a, And) and isinstance(b, And):
        return And(a.children | b.children)
    if isinstance(a, And):
        return And(a.children | {b})
    if isinstance(b, And):
        return And(b.children | {a})
    return And(frozenset({a, b}))


def _or_formula(a: Formula, b: Formula) -> Formula:
    if isinstance(a, FalseF):
        return b
    if isinstance(b, FalseF):
        return a
    if isinstance(a, TrueF) or isinstance(b, TrueF):
        return TrueF()
    if isinstance(a, Not) and a.arg == b:
        return TrueF()
    if isinstance(b, Not) and b.arg == a:
        return TrueF()
    if isinstance(a, Or) and isinstance(b, Or):
        return Or(a.children | b.children)
    if isinstance(a, Or):
        return Or(a.children | {b})
    if isinstance(b, Or):
        return Or(b.children | {a})
    return Or(frozenset({a, b}))


def _neg(f: Formula) -> Formula:
    if isinstance(f, TrueF):
        return FalseF()
    if isinstance(f, FalseF):
        return TrueF()
    if isinstance(f, Not):
        return f.arg
    return Not(f)


class Formula(Basic):
    """Base class for first-order logical formulas."""

    is_Formula = True

    def free_vars(self) -> set[Variable]:
        """Return variables that appear free in this formula."""
        raise NotImplementedError

    def bound_vars(self) -> set[Variable]:
        """Return variables bound by quantifiers in this formula."""
        raise NotImplementedError

    def subs(self, mapping: dict[Variable, Term]) -> Formula:
        """Capture-safe substitution with simplification."""
        from fopy.transform import subs

        return subs(self, mapping)

    def satisfy(self, structure: object, assignment: dict[Variable, object] | None = None) -> bool:
        """Evaluate truth in a :class:`~fopy.structures.Structure`."""
        from fopy.semantics import satisfy as _satisfy
        from fopy.structures import Structure

        if not isinstance(structure, Structure):
            raise TypeError("structure must be a fopy.structures.Structure")
        return _satisfy(self, structure, assignment)

    def __and__(self, other: Formula) -> Formula:
        """Return the conjunction of this formula with *other*."""
        return _and_formula(self, other)

    def __or__(self, other: Formula) -> Formula:
        """Return the disjunction of this formula with *other*."""
        return _or_formula(self, other)

    def __invert__(self) -> Formula:
        """Return the negation of this formula."""
        return _neg(self)

    def __rshift__(self, other: Formula) -> Formula:
        """Return implication ``self → other``."""
        return _or_formula(_neg(self), other)

    def __lshift__(self, other: Formula) -> Formula:
        """Return reverse implication ``other → self``."""
        return _or_formula(other, _neg(self))

    def __xor__(self, other: Formula) -> Formula:
        """Return exclusive-or of this formula with *other*."""
        return _or_formula(_and_formula(self, _neg(other)), _and_formula(_neg(self), other))

    def to_tptp(self, name: str = "conjecture") -> str:
        """Export this formula as a TPTP ``fof`` conjecture string."""
        from fopy.printing.tptp import to_tptp

        return to_tptp(self, name=name)

    def to_smtlib(self) -> str:
        """Export this formula as an SMT-LIB ``(assert ...)`` fragment."""
        from fopy.printing.smtlib import to_smtlib

        return to_smtlib(self)

    def to_z3(self) -> object | None:
        """Export this formula as a Z3 boolean expression when Z3 is installed."""
        from fopy.solvers.z3_formula import formula_to_z3

        return formula_to_z3(self)

    def latex(self) -> str:
        """Return a LaTeX typesetting of this formula."""
        from fopy.printing.latex import latex

        return latex(self)

    def py(self) -> str:
        """Return a Python API expression that reconstructs this formula."""
        from fopy.printing.str import to_python

        return to_python(self)


class TrueF(Formula):
    """The true propositional constant (⊤)."""

    __slots__ = ()

    @property
    def args(self) -> tuple:
        """Return an empty argument tuple."""
        return ()

    def free_vars(self) -> set[Variable]:
        """Return the empty set (no free variables)."""
        return set()

    def bound_vars(self) -> set[Variable]:
        """Return the empty set (no bound variables)."""
        return set()

    def __repr__(self) -> str:
        return "⊤"


class FalseF(Formula):
    """The false propositional constant (⊥)."""

    __slots__ = ()

    @property
    def args(self) -> tuple:
        """Return an empty argument tuple."""
        return ()

    def free_vars(self) -> set[Variable]:
        """Return the empty set (no free variables)."""
        return set()

    def bound_vars(self) -> set[Variable]:
        """Return the empty set (no bound variables)."""
        return set()

    def __repr__(self) -> str:
        return "⊥"


class Atom(Formula):
    """Atomic formula ``rel(term₁, …, termₙ)``."""

    __slots__ = ("_args", "rel")

    def __init__(self, rel: str, args: tuple[Term, ...]) -> None:
        """Build an atom for relation *rel* applied to *args*."""
        super().__init__()
        self.rel = rel
        self._args = args

    @property
    def args(self) -> tuple:
        """Return ``(rel,) + term arguments``."""
        return (self.rel,) + self._args

    def free_vars(self) -> set[Variable]:
        """Return variables occurring free in the term arguments."""
        result: set[Variable] = set()
        for a in self._args:
            if isinstance(a, Variable):
                result.add(a)
            elif isinstance(a, Term):
                result |= a.free_vars() if hasattr(a, "free_vars") else set()
        return result

    def bound_vars(self) -> set[Variable]:
        """Return the empty set (atoms bind no variables)."""
        return set()

    def __repr__(self) -> str:
        inner = ", ".join(repr(a) for a in self._args)
        return f"{self.rel}({inner})"


class Eq(Formula):
    """Equality formula ``left = right`` between terms."""

    __slots__ = ("left", "right")

    def __init__(self, left: Term, right: Term) -> None:
        """Build equality between *left* and *right*."""
        super().__init__()
        self.left = left
        self.right = right

    @property
    def args(self) -> tuple:
        """Return ``(left, right)``."""
        return (self.left, self.right)

    def _term_vars(self, t: Term) -> set[Variable]:
        if isinstance(t, Variable):
            return {t}
        free_vars = getattr(t, "free_vars", None)
        if callable(free_vars):
            return cast(set[Variable], free_vars())
        return set()

    def free_vars(self) -> set[Variable]:
        """Return variables free in either side of the equality."""
        return self._term_vars(self.left) | self._term_vars(self.right)

    def bound_vars(self) -> set[Variable]:
        """Return the empty set (equality binds no variables)."""
        return set()

    def __repr__(self) -> str:
        return f"{self.left} = {self.right}"


class Not(Formula):
    """Negation ``¬arg`` of a subformula."""

    __slots__ = ("arg",)

    def __init__(self, arg: Formula) -> None:
        """Negate subformula *arg*."""
        super().__init__()
        self.arg = arg

    @property
    def args(self) -> tuple[Formula]:
        """Return ``(arg,)``."""
        return (self.arg,)

    def free_vars(self) -> set[Variable]:
        """Return free variables of the negated subformula."""
        return self.arg.free_vars()

    def bound_vars(self) -> set[Variable]:
        """Return bound variables of the negated subformula."""
        return self.arg.bound_vars()

    def __repr__(self) -> str:
        return f"¬{self.arg}"


class And(Formula):
    """Conjunction of a set of subformulas."""

    __slots__ = ("children",)

    def __init__(self, children: frozenset[Formula]) -> None:
        """Build conjunction from the set of conjuncts *children*."""
        super().__init__()
        self.children = children

    @property
    def args(self) -> tuple:
        """Return ``(children,)``."""
        return (self.children,)

    def free_vars(self) -> set[Variable]:
        """Return free variables appearing in any conjunct."""
        result: set[Variable] = set()
        for c in self.children:
            result |= c.free_vars()
        return result

    def bound_vars(self) -> set[Variable]:
        """Return bound variables appearing in any conjunct."""
        result: set[Variable] = set()
        for c in self.children:
            result |= c.bound_vars()
        return result

    def __repr__(self) -> str:
        parts = sorted(repr(c) for c in self.children)
        return "(" + " ∧ ".join(parts) + ")"


class Or(Formula):
    """Disjunction of a set of subformulas."""

    __slots__ = ("children",)

    def __init__(self, children: frozenset[Formula]) -> None:
        """Build disjunction from the set of disjuncts *children*."""
        super().__init__()
        self.children = children

    @property
    def args(self) -> tuple:
        """Return ``(children,)``."""
        return (self.children,)

    def free_vars(self) -> set[Variable]:
        """Return free variables appearing in any disjunct."""
        result: set[Variable] = set()
        for c in self.children:
            result |= c.free_vars()
        return result

    def bound_vars(self) -> set[Variable]:
        """Return bound variables appearing in any disjunct."""
        result: set[Variable] = set()
        for c in self.children:
            result |= c.bound_vars()
        return result

    def __repr__(self) -> str:
        parts = sorted(repr(c) for c in self.children)
        return "(" + " ∨ ".join(parts) + ")"


class ForAll(Formula):
    """Universal quantification ``∀var body``."""

    __slots__ = ("body", "var")

    def __init__(self, var: Variable, body: Formula) -> None:
        """Quantify *var* universally over *body*."""
        super().__init__()
        self.var = var
        self.body = body

    @property
    def args(self) -> tuple:
        """Return ``(var, body)``."""
        return (self.var, self.body)

    def free_vars(self) -> set[Variable]:
        """Return free variables of *body* except the bound *var*."""
        return self.body.free_vars() - {self.var}

    def bound_vars(self) -> set[Variable]:
        """Return bound variables of *body* plus *var*."""
        return self.body.bound_vars() | {self.var}

    def __repr__(self) -> str:
        return f"∀{self.var} {self.body}"


class Exists(Formula):
    """Existential quantification ``∃var body``."""

    __slots__ = ("body", "var")

    def __init__(self, var: Variable, body: Formula) -> None:
        """Quantify *var* existentially over *body*."""
        super().__init__()
        self.var = var
        self.body = body

    @property
    def args(self) -> tuple:
        """Return ``(var, body)``."""
        return (self.var, self.body)

    def free_vars(self) -> set[Variable]:
        """Return free variables of *body* except the bound *var*."""
        return self.body.free_vars() - {self.var}

    def bound_vars(self) -> set[Variable]:
        """Return bound variables of *body* plus *var*."""
        return self.body.bound_vars() | {self.var}

    def __repr__(self) -> str:
        return f"∃{self.var} {self.body}"


def forall(var: Variable, body: Formula) -> ForAll:
    """Build universal quantification ``∀var body``.

    Args:
        var: Bound variable.
        body: Formula in which *var* is quantified.

    Returns:
        A :class:`ForAll` node.
    """
    return ForAll(var, body)


def exists(var: Variable, body: Formula) -> Exists:
    """Build existential quantification ``∃var body``.

    Args:
        var: Bound variable.
        body: Formula in which *var* is quantified.

    Returns:
        A :class:`Exists` node.
    """
    return Exists(var, body)


# Term.free_vars for Apply
def _apply_free_vars(self: Term) -> set[Variable]:
    from fopy.terms import Apply, Constant

    if isinstance(self, Variable):
        return {self}
    if isinstance(self, Constant):
        return set()
    if isinstance(self, Apply):
        result: set[Variable] = set()
        for a in self._args:
            result |= _apply_free_vars(cast(Term, a))
        return result
    return set()


Term.free_vars = _apply_free_vars  # type: ignore[attr-defined]
