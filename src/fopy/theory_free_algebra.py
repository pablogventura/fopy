"""Bounded construction of finite free term algebras."""

from __future__ import annotations

from itertools import product
from typing import Any, cast

from fopy.formulas import Formula
from fopy.semantics import satisfy
from fopy.signature import Signature
from fopy.structures import Structure
from fopy.terms import Apply, Constant, Term

_MAX_GENERATORS = 3
_MAX_DEPTH = 3
_MAX_TERMS = 64


def _term_key(term: Term) -> tuple[Any, ...]:
    if isinstance(term, Constant):
        return ("c", term.name)
    if isinstance(term, Apply):
        return ("a", term.func, tuple(_term_key(cast(Term, a)) for a in term._args))
    return ("?", repr(term))


def _term_depth(term: Term) -> int:
    if isinstance(term, Constant):
        return 0
    if isinstance(term, Apply):
        if not term._args:
            return 1
        return 1 + max(_term_depth(cast(Term, a)) for a in term._args)
    return 0


def build_free_term_algebra(
    signature: Signature,
    n_generators: int,
    *,
    max_depth: int = 2,
) -> Structure:
    """Build a finite term algebra on *n_generators* closed under signature operations.

    Universe elements are indices of unique terms built from generator constants
    ``g0``, …, ``g{n-1}`` up to term depth *max_depth*. Intended for small
    functional signatures (``|U|`` capped at :data:`_MAX_TERMS`).

    Args:
        signature: Functional signature (no relation symbols).
        n_generators: Number of free generators (1-3).
        max_depth: Maximum term depth to close under operations.

    Returns:
        :class:`~fopy.structures.Structure` interpreting each function symbol by
        term construction.

    Raises:
        ValueError: On invalid parameters or excessive term growth.
        NotImplementedError: When relation symbols are present.
    """
    if n_generators < 1 or n_generators > _MAX_GENERATORS:
        raise ValueError(f"n_generators must be between 1 and {_MAX_GENERATORS}")
    if max_depth < 0 or max_depth > _MAX_DEPTH:
        raise ValueError(f"max_depth must be between 0 and {_MAX_DEPTH}")
    if signature.relations:
        raise NotImplementedError("free term algebras require a functional signature")
    if not signature.functions:
        raise ValueError("signature must declare at least one function symbol")

    pool: list[Term] = [Constant(f"g{i}") for i in range(n_generators)]
    keys = {_term_key(t) for t in pool}
    changed = True
    while changed:
        changed = False
        new_terms: list[Term] = []
        for fname, arity in sorted(signature.functions.items()):
            if arity == 0:
                t = Apply(fname, ())
                if _term_depth(t) > max_depth:
                    continue
                k = _term_key(t)
                if k not in keys:
                    keys.add(k)
                    new_terms.append(t)
                continue
            for combo in product(pool, repeat=arity):
                t = Apply(fname, combo)
                if _term_depth(t) > max_depth:
                    continue
                k = _term_key(t)
                if k not in keys:
                    keys.add(k)
                    new_terms.append(t)
        if new_terms:
            changed = True
            pool.extend(new_terms)
            if len(pool) > _MAX_TERMS:
                raise ValueError(
                    f"Free term algebra exceeded {_MAX_TERMS} terms; "
                    "reduce generators, depth, or signature size"
                )

    key_to_idx = {_term_key(t): i for i, t in enumerate(pool)}
    sink = Constant("_")
    sink_key = _term_key(sink)
    if sink_key not in key_to_idx:
        key_to_idx[sink_key] = len(pool)
        pool.append(sink)
    sink_idx = key_to_idx[sink_key]
    universe = list(range(len(pool)))

    fn_tables: dict[str, dict[tuple[int, ...], int] | int] = {}
    for sym, arity in signature.functions.items():
        if arity == 0:
            t = Apply(sym, ())
            fn_tables[sym] = key_to_idx[_term_key(t)]
            continue
        table: dict[tuple[int, ...], int] = {}
        for args in product(universe, repeat=arity):
            arg_terms = tuple(pool[i] for i in args)
            result = Apply(sym, arg_terms)
            rk = _term_key(result)
            table[args] = key_to_idx.get(rk, sink_idx)
        fn_tables[sym] = table

    return Structure.from_tables(
        signature,
        universe,
        functions=fn_tables,
        relations={},
        name=f"F_{n_generators}",
        universes={"U": universe},
    )


def free_algebra_for_variety(
    signature: Signature,
    axioms: list[Formula],
    n_generators: int,
    *,
    max_depth: int = 2,
) -> Structure:
    """Build a free term algebra and verify variety axioms on it.

    Raises:
        ValueError: When axioms fail on the generated structure.
    """
    structure = build_free_term_algebra(signature, n_generators, max_depth=max_depth)
    for ax in axioms:
        if not satisfy(ax, structure, {}):
            raise ValueError("Axiom failed on generated free term algebra; increase max_depth")
    return structure
