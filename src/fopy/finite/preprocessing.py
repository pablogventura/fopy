"""Target relation preprocessing by tuple equality patterns."""

from __future__ import annotations

from dataclasses import dataclass, field

from fopy.finite import open_formulas as formulas
from fopy.finite.open_formulas import Formula, Term, Variable
from fopy.finite.relops import Relation


@dataclass
class Pattern:
    tuple: list[int]
    pruned_tuple: list[int]
    pattern: set[frozenset[int]] = field(default_factory=set)

    @classmethod
    def new(cls, tuple_: list[int]) -> Pattern:
        by_value: dict[int, set[int]] = {}
        pruned_list: list[int] = []
        for i, a in enumerate(tuple_):
            by_value.setdefault(a, set()).add(i)
            if len(by_value[a]) == 1:
                pruned_list.append(a)
        pattern_set = {frozenset(indices) for indices in by_value.values()}
        return cls(tuple=tuple_, pruned_tuple=pruned_list, pattern=pattern_set)

    def name(self) -> str:
        result = "|"
        classes = sorted(self.pattern, key=lambda cls: min(cls))
        for cls in classes:
            result += ",".join(str(i) for i in sorted(cls))
            result += "|"
        result += f"a{len(self.pruned_tuple)}"
        return result

    def preprocessed_formula(self) -> Formula:
        vs = formulas.variables(list(range(len(self.tuple))))
        representatives = sorted(min(cls) for cls in self.pattern)
        rep_vars = [vs[i] for i in representatives]
        f = formulas.true_formula(set(rep_vars))
        if len(rep_vars) == 1:
            v = rep_vars[0]
            f = f.and_formula(formulas.eq(Term.variable(v), Term.variable(v)))
        for i, v in enumerate(rep_vars):
            for j, w in enumerate(rep_vars):
                if i != j:
                    f = f.and_formula(
                        formulas.eq(Term.variable(v), Term.variable(w)).neg()
                    )
        return f

    def postprocessed_formula(self) -> Formula:
        vs = formulas.variables(list(range(len(self.tuple))))
        differents: list[Variable] = []
        f = formulas.true_formula(None)
        classes = sorted(self.pattern, key=lambda cls: min(cls))
        for cls in classes:
            cls_list = sorted(cls)
            for w0, w1 in zip(cls_list, cls_list[1:], strict=False):
                f = f.and_formula(
                    formulas.eq(Term.variable(vs[w0]), Term.variable(vs[w1]))
                )
            repr_var = vs[min(cls)]
            for other in differents:
                f = f.and_formula(
                    formulas.eq(Term.variable(repr_var), Term.variable(other)).neg()
                )
            differents.append(repr_var)
        return f

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pattern):
            return NotImplemented
        return self.pattern == other.pattern

    def __hash__(self) -> int:
        return hash(tuple(sorted(tuple(sorted(p)) for p in self.pattern)))


def preprocesamiento2(target: Relation) -> list[Relation]:
    """Split a target relation into pattern-equivalence classes."""
    return split_targets(target)


def split_targets(target: Relation) -> list[Relation]:
    pruned_relations: dict[Pattern, list[list[int]]] = {}
    for t in target.r:
        pattern = Pattern.new(list(t))
        pruned_relations.setdefault(pattern, []).append(pattern.pruned_tuple)
    result: list[Relation] = []
    for pattern, tuples in pruned_relations.items():
        first_tuple = tuples[0]
        arity = len(first_tuple)
        r = Relation.new(f"{target.sym}{pattern.name()}", arity)
        for t in tuples:
            r.add(t)
        r.pattern = pattern
        r.superrel_sym = target.sym
        r.superrel = target
        result.append(r)
    return result
