"""Canonical normalization of first-order terms."""

from __future__ import annotations

from typing import cast

from fopy.symbols import Variable
from fopy.terms import Apply, Constant, Term


def normalize_term(term: Term) -> Term:
    """Return a structurally canonical form of *term* (sorted argument order)."""
    if isinstance(term, (Variable, Constant)):
        return term
    if isinstance(term, Apply):
        args = tuple(normalize_term(cast(Term, a)) for a in term._args)
        return Apply(term.func, args)
    return term
