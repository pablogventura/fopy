"""Bounded search for term identities (Malcev, majority, NU)."""

from __future__ import annotations

from fopy.finite.model_checking import models
from fopy.finite.models import Model
from fopy.finite.open_formulas import Formula, OpSym, Term, Variable, eq


def _enumerate_terms(model: Model, arity: int, max_depth: int) -> list[Term]:
    """List open terms of fixed arity up to *max_depth* using model operations."""
    vars_ = [Variable.from_index(i) for i in range(arity)]
    terms: list[Term] = [Term.from_variable(v) for v in vars_]
    ops_by_arity: dict[int, list[str]] = {}
    for sym, op in model.operations.items():
        ops_by_arity.setdefault(op.arity, []).append(sym)
    for _depth in range(1, max_depth + 1):
        new_terms: list[Term] = []
        for ar, syms in sorted(ops_by_arity.items()):
            for sym in syms:
                if ar == 0:
                    new_terms.append(Term.op_term(OpSym.new(sym, 0), []))
                else:
                    for combo in _term_combos(terms, ar):
                        new_terms.append(Term.op_term(OpSym.new(sym, ar), list(combo)))
        terms.extend(new_terms)
    return terms


def _term_combos(terms: list[Term], arity: int) -> list[tuple[Term, ...]]:
    if arity == 0:
        return [()]
    result: list[tuple[Term, ...]] = [()]
    for _ in range(arity):
        result = [r + (t,) for r in result for t in terms]
    return result


def _substitute_term(term: Term, mapping: dict[Variable, Term]) -> Term:
    from fopy.finite.open_formulas import TermKind

    if term.kind == TermKind.VARIABLE:
        assert term.variable is not None
        return mapping.get(term.variable, term)
    assert term.sym is not None
    return Term.op_term(term.sym, [_substitute_term(a, mapping) for a in term.args])


def _instantiate(term: Term, args: list[Term]) -> Term:
    mapping = {Variable.from_index(i): args[i] for i in range(len(args))}
    return _substitute_term(term, mapping)



def _expand_unknown(term: Term, open_term: Term) -> Term:
    """Replace unknown-term marker nodes with *term* applied to sub-args."""
    from fopy.finite.open_formulas import TermKind

    if open_term.kind == TermKind.OP_TERM and open_term.sym is not None:
        if open_term.sym.op == "τ":
            arg_terms = [_expand_unknown(term, a) for a in open_term.args]
            var_args = []
            for at in arg_terms:
                if at.kind == TermKind.VARIABLE:
                    assert at.variable is not None
                    var_args.append(at)
                else:
                    return open_term
            return _instantiate(term, var_args)
        return Term.op_term(
            open_term.sym,
            [_expand_unknown(term, a) for a in open_term.args],
        )
    return open_term


def _expand_formula_unknown(term: Term, formula: Formula) -> Formula:
    from fopy.finite.open_formulas import FormulaKind

    if formula.kind == FormulaKind.EQ:
        assert formula.t1 is not None and formula.t2 is not None
        return eq(_expand_unknown(term, formula.t1), _expand_unknown(term, formula.t2))
    return formula


def find_term_identity(
    model: Model,
    equations: list[Formula],
    *,
    max_depth: int = 2,
) -> Term | None:
    """Search for a term satisfying open equations on *model*.

    Equations may use the placeholder operation ``τ`` applied to variables
    to mark where the unknown term is applied (for example ``τ(x, x, y) = y``).
    Otherwise, equations are checked as written against each candidate term
    of arity inferred from variable count.

    Args:
        model: Finite algebra used for evaluation.
        equations: Identity formulas involving ``τ`` or variables only.
        max_depth: Maximum term grade to enumerate.

    Returns:
        Witness term, or ``None`` if no term is found within the bound.
    """
    if not equations:
        return None
    has_tau = any("τ" in str(f) for f in equations)
    arity = max((len(f.implied_declaration()) for f in equations), default=3)
    if arity == 0:
        arity = 3
    for term in _enumerate_terms(model, arity, max_depth):
        if has_tau:
            expanded = [_expand_formula_unknown(term, f) for f in equations]
        else:
            expanded = equations
        if all(models(model, f) for f in expanded):
            return term
    return None


def _search_ternary(
    model: Model,
    equations_builder: object,
    max_depth: int,
) -> Term | None:
    for term in _enumerate_terms(model, 3, max_depth):
        eqs: list[Formula] = equations_builder(term)  # type: ignore[operator]
        if all(models(model, f) for f in eqs):
            return term
    return None


def is_malcev(model: Model, *, max_depth: int = 2) -> bool:
    """Return whether *model* has a Malcev term within the search bound.

    A Malcev term ``t(x, y, z)`` satisfies ``t(x, x, y) = y`` and
    ``t(x, y, y) = x`` as identities on the algebra.

    Args:
        model: Finite algebra.
        max_depth: Maximum term grade for the search.

    Returns:
        ``True`` when a witness term is found.
    """
    x, y, z = Variable.from_index(0), Variable.from_index(1), Variable.from_index(2)
    tx, ty, tz = Term.from_variable(x), Term.from_variable(y), Term.from_variable(z)

    def equations(t: Term) -> list[Formula]:
        return [
            eq(_instantiate(t, [tx, tx, ty]), ty),
            eq(_instantiate(t, [tx, ty, ty]), tx),
        ]

    return _search_ternary(model, equations, max_depth) is not None


def has_majority_term(model: Model, *, max_depth: int = 2) -> bool:
    """Return whether *model* admits a majority term (bounded search).

    A majority term ``m(x, y, z)`` satisfies ``m(x, x, y) = x``, ``m(x, y, x) = x``,
    and ``m(y, x, x) = x`` on all assignments.

    Args:
        model: Finite algebra.
        max_depth: Maximum term grade for the search.

    Returns:
        ``True`` when a majority term is found within the bound.
    """
    x, y, z = Variable.from_index(0), Variable.from_index(1), Variable.from_index(2)
    tx, ty, tz = Term.from_variable(x), Term.from_variable(y), Term.from_variable(z)

    def equations(t: Term) -> list[Formula]:
        return [
            eq(_instantiate(t, [tx, tx, ty]), tx),
            eq(_instantiate(t, [tx, ty, tx]), tx),
            eq(_instantiate(t, [ty, tx, tx]), tx),
        ]

    return _search_ternary(model, equations, max_depth) is not None


def has_near_unanimity_term(model: Model, *, max_depth: int = 2, arity: int = 3) -> bool:
    """Return whether *model* has a near-unanimity term of given arity.

    An ``n``-ary near-unanimity term ``t`` satisfies: if at least ``n - 1``
    arguments agree, then ``t`` returns that majority value.

    Args:
        model: Finite algebra.
        max_depth: Maximum term grade for the search.
        arity: Arity of the candidate term (default 3).

    Returns:
        ``True`` when a witness term is found within the bound.
    """
    vars_ = [Variable.from_index(i) for i in range(arity)]
    term_vars = [Term.from_variable(v) for v in vars_]

    def equations(t: Term) -> list[Formula]:
        result: list[Formula] = []
        for dissent in range(arity):
            args = [term_vars[0]] * arity
            if arity > 1:
                args[dissent] = term_vars[1]
            result.append(eq(_instantiate(t, args), term_vars[0]))
        return result

    for term in _enumerate_terms(model, arity, max_depth):
        if all(models(model, f) for f in equations(term)):
            return True
    return False
