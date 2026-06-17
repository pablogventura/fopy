"""Open first-order terms and formulas (equality fragment)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from fopy.finite.models import Model
from fopy.finite.relops import Operation


_SUBSCRIPT = "₀₁₂₃₄₅₆₇₈₉"


def _subscript(n: int) -> str:
    return "".join(
        "₋" if c == "-" else _SUBSCRIPT[int(c)] if c.isdigit() else c for c in str(n)
    )


@dataclass(frozen=True, order=True)
class Variable:
    sym: str

    @classmethod
    def new(cls, sym: str) -> Variable:
        return cls(sym=sym)

    @classmethod
    def from_index(cls, i: int) -> Variable:
        return cls(sym=f"x{_subscript(i)}")

    def __str__(self) -> str:
        return self.sym


@dataclass(frozen=True, order=True)
class OpSym:
    op: str
    arity: int

    @classmethod
    def new(cls, op: str, arity: int) -> OpSym:
        return cls(op=op, arity=arity)

    def __str__(self) -> str:
        return self.op


class TermKind(Enum):
    VARIABLE = auto()
    OP_TERM = auto()


@dataclass(frozen=True)
class Term:
    kind: TermKind
    variable: Variable | None = None
    sym: OpSym | None = None
    args: tuple[Term, ...] = ()

    @classmethod
    def variable(cls, v: Variable) -> Term:  # noqa: F811
        return cls(TermKind.VARIABLE, variable=v)

    @classmethod
    def op_term(cls, sym: OpSym, args: list[Term] | tuple[Term, ...]) -> Term:
        return cls(TermKind.OP_TERM, sym=sym, args=tuple(args))

    def free_vars(self) -> set[Variable]:
        if self.kind == TermKind.VARIABLE:
            assert self.variable is not None
            return {self.variable}
        return set().union(*(a.free_vars() for a in self.args))

    def grade(self) -> int:
        if self.kind == TermKind.VARIABLE:
            return 0
        return 1 + max((a.grade() for a in self.args), default=0)

    def evaluate(
        self,
        operations: dict[str, Operation],
        vector: dict[Variable, int],
    ) -> int:
        if self.kind == TermKind.VARIABLE:
            assert self.variable is not None
            if self.variable not in vector:
                raise KeyError(f"Variable {self.variable.sym} not bound")
            return vector[self.variable]
        assert self.sym is not None
        args_vals = [a.evaluate(operations, vector) for a in self.args]
        op: Operation | None = operations.get(self.sym.op)
        if op is None:
            raise KeyError(f"Operation {self.sym.op} not found")
        result = op.call(args_vals)
        if result is None:
            raise ValueError(f"Operation {self.sym.op} undefined for args {args_vals}")
        return result

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Term):
            return NotImplemented
        return self.grade() == other.grade() and repr(self) == repr(other)

    def __hash__(self) -> int:
        if self.kind == TermKind.VARIABLE:
            assert self.variable is not None
            return hash(("var", self.variable))
        assert self.sym is not None
        return hash(("op", self.sym, self.args))

    def __lt__(self, other: Term) -> bool:
        if not isinstance(other, Term):
            return NotImplemented
        if self.grade() != other.grade():
            return self.grade() < other.grade()
        return repr(self) < repr(other)

    def __str__(self) -> str:
        if self.kind == TermKind.VARIABLE:
            assert self.variable is not None
            return str(self.variable)
        assert self.sym is not None
        inner = ", ".join(str(a) for a in self.args)
        return f"{self.sym}({inner})"


class FormulaKind(Enum):
    TRUE = auto()
    FALSE = auto()
    EQ = auto()
    NEG = auto()
    AND = auto()
    OR = auto()


@dataclass(frozen=True)
class Formula:
    kind: FormulaKind
    orphan_vars: frozenset[Variable] = frozenset()
    t1: Term | None = None
    t2: Term | None = None
    inner: Formula | None = None
    parts: frozenset[Formula] = frozenset()

    def free_vars(self) -> set[Variable]:
        match self.kind:
            case FormulaKind.TRUE | FormulaKind.FALSE:
                return set(self.orphan_vars)
            case FormulaKind.EQ:
                assert self.t1 is not None and self.t2 is not None
                return self.t1.free_vars() | self.t2.free_vars()
            case FormulaKind.NEG:
                assert self.inner is not None
                return self.inner.free_vars()
            case FormulaKind.AND | FormulaKind.OR:
                return set().union(*(p.free_vars() for p in self.parts))
        return set()

    def implied_declaration(self) -> list[Variable]:
        return sorted(self.free_vars(), key=lambda v: v.sym)

    def satisfy(self, model: Model, vector: dict[Variable, int]) -> bool:
        match self.kind:
            case FormulaKind.TRUE:
                return True
            case FormulaKind.FALSE:
                return False
            case FormulaKind.EQ:
                assert self.t1 is not None and self.t2 is not None
                try:
                    v1 = self.t1.evaluate(model.operations, vector)
                    v2 = self.t2.evaluate(model.operations, vector)
                except (KeyError, ValueError):
                    return False
                return v1 == v2
            case FormulaKind.NEG:
                assert self.inner is not None
                return not self.inner.satisfy(model, vector)
            case FormulaKind.AND:
                return all(p.satisfy(model, vector) for p in self.parts)
            case FormulaKind.OR:
                return any(p.satisfy(model, vector) for p in self.parts)
        return False

    def extension(self, model: Model, arity: int | None = None) -> set[tuple[int, ...]]:
        vs = self.implied_declaration()
        a = arity if arity is not None else len(vs)
        match self.kind:
            case FormulaKind.TRUE:
                if arity is not None:
                    return set(_cartesian_product(model.universe, arity))
                return set()
            case FormulaKind.FALSE:
                return set()
            case _:
                if not vs:
                    return set()
                result: set[tuple[int, ...]] = set()
                for tuple_vals in _cartesian_product(model.universe, len(vs)):
                    vector = dict(zip(vs, tuple_vals, strict=True))
                    if self.satisfy(model, vector):
                        result.add(tuple(vector[v] for v in vs))
                if a != len(vs):
                    return {t[:a] for t in result}
                return result

    def and_formula(self, other: Formula) -> Formula:
        if self.kind == FormulaKind.TRUE:
            return other
        if other.kind == FormulaKind.TRUE:
            return self
        if self.kind == FormulaKind.FALSE and other.kind == FormulaKind.FALSE:
            return false_formula(self.orphan_vars | other.orphan_vars)
        if self.kind == FormulaKind.FALSE:
            return self
        if other.kind == FormulaKind.FALSE:
            return other
        if (
            (self.kind == FormulaKind.NEG and other == self.inner)
            or (other.kind == FormulaKind.NEG and self == other.inner)
        ):
            return false_formula(self.free_vars() | other.free_vars())
        if self.kind == FormulaKind.AND and other.kind == FormulaKind.AND:
            return Formula(FormulaKind.AND, parts=self.parts | other.parts)
        if self.kind == FormulaKind.AND:
            return Formula(FormulaKind.AND, parts=self.parts | {other})
        if other.kind == FormulaKind.AND:
            return Formula(FormulaKind.AND, parts=other.parts | {self})
        return Formula(FormulaKind.AND, parts=frozenset({self, other}))

    def or_formula(self, other: Formula) -> Formula:
        if self.kind == FormulaKind.FALSE:
            return other
        if other.kind == FormulaKind.FALSE:
            return self
        if self.kind == FormulaKind.TRUE and other.kind == FormulaKind.TRUE:
            return true_formula(self.orphan_vars | other.orphan_vars)
        if self.kind == FormulaKind.TRUE:
            return self
        if other.kind == FormulaKind.TRUE:
            return other
        if (
            (self.kind == FormulaKind.NEG and other == self.inner)
            or (other.kind == FormulaKind.NEG and self == other.inner)
        ):
            return true_formula(self.free_vars() | other.free_vars())
        if self.kind == FormulaKind.OR and other.kind == FormulaKind.OR:
            return Formula(FormulaKind.OR, parts=self.parts | other.parts)
        if self.kind == FormulaKind.OR:
            return Formula(FormulaKind.OR, parts=self.parts | {other})
        if other.kind == FormulaKind.OR:
            return Formula(FormulaKind.OR, parts=other.parts | {self})
        return Formula(FormulaKind.OR, parts=frozenset({self, other}))

    def neg(self) -> Formula:
        match self.kind:
            case FormulaKind.TRUE:
                return false_formula(self.orphan_vars)
            case FormulaKind.FALSE:
                return true_formula(self.orphan_vars)
            case FormulaKind.NEG:
                assert self.inner is not None
                return self.inner
            case _:
                return Formula(FormulaKind.NEG, inner=self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Formula):
            return NotImplemented
        return _formula_hash(self) == _formula_hash(other)

    def __hash__(self) -> int:
        return _formula_hash(self)

    def __str__(self) -> str:
        match self.kind:
            case FormulaKind.TRUE:
                vars_str = ",".join(v.sym for v in sorted(self.orphan_vars, key=lambda x: x.sym))
                return f"⊤({vars_str})"
            case FormulaKind.FALSE:
                vars_str = ",".join(v.sym for v in sorted(self.orphan_vars, key=lambda x: x.sym))
                return f"⊥({vars_str})"
            case FormulaKind.EQ:
                assert self.t1 is not None and self.t2 is not None
                return f"{self.t1} == {self.t2}"
            case FormulaKind.NEG:
                assert self.inner is not None
                return f"¬{self.inner}"
            case FormulaKind.AND:
                parts = " ∧ ".join(str(p) for p in sorted(self.parts, key=repr))
                return f"({parts})"
            case FormulaKind.OR:
                parts = " ∨ ".join(str(p) for p in sorted(self.parts, key=repr))
                return f"({parts})"
        return ""


def variables(indices: list[int]) -> list[Variable]:
    return [Variable.from_index(i) for i in indices]


def eq(t1: Term, t2: Term) -> Formula:
    if t1 == t2:
        return true_formula(t1.free_vars() | t2.free_vars())
    return Formula(FormulaKind.EQ, t1=t1, t2=t2)


def true_formula(orphan_vars: set[Variable] | frozenset[Variable] | None = None) -> Formula:
    ov = frozenset(orphan_vars or ())
    return Formula(FormulaKind.TRUE, orphan_vars=ov)


def false_formula(orphan_vars: set[Variable] | frozenset[Variable] | None = None) -> Formula:
    ov = frozenset(orphan_vars or ())
    return Formula(FormulaKind.FALSE, orphan_vars=ov)


def neg(f: Formula) -> Formula:
    return f.neg()


def and_formula(a: Formula, b: Formula) -> Formula:
    return a.and_formula(b)


def or_formula(a: Formula, b: Formula) -> Formula:
    return a.or_formula(b)


def satisfy(f: Formula, model: Model, vector: dict[Variable, int]) -> bool:
    return f.satisfy(model, vector)


def extension(f: Formula, model: Model, arity: int | None = None) -> set[tuple[int, ...]]:
    return f.extension(model, arity)


def _cartesian_product(universe: list[int], n: int) -> list[tuple[int, ...]]:
    result: list[tuple[int, ...]] = [()]
    for _ in range(n):
        result = [r + (u,) for r in result for u in universe]
    return result


def _formula_hash(f: Formula) -> int:
    match f.kind:
        case FormulaKind.TRUE:
            return hash(("T", tuple(sorted(f.orphan_vars, key=lambda v: v.sym))))
        case FormulaKind.FALSE:
            return hash(("F", tuple(sorted(f.orphan_vars, key=lambda v: v.sym))))
        case FormulaKind.EQ:
            assert f.t1 is not None and f.t2 is not None
            return hash(("eq", f.t1, f.t2))
        case FormulaKind.NEG:
            assert f.inner is not None
            return hash(("neg", _formula_hash(f.inner)))
        case FormulaKind.AND:
            return hash(("and", tuple(sorted(map(_formula_hash, f.parts)))))
        case FormulaKind.OR:
            return hash(("or", tuple(sorted(map(_formula_hash, f.parts)))))
    return 0
