"""Lindenbaum join-irreducibles via subalgebra morphisms (no Minion).

Pure-Python generator for existential-positive (and open) Lindenbaum atoms on
a single finite algebra, using :mod:`fopy.universal` subalgebras and
homomorphisms. Intended for tiny universes (e.g. ``|U| <= 4``).
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from itertools import product
from typing import Literal

from fopy.finite.models import Model
from fopy.finite.relops import Operation
from fopy.universal import homomorphisms, subalgebra_lattice

FragmentKind = Literal["ep", "open", "qf"]


@dataclass(frozen=True)
class HomArrow:
    """Homomorphism between subuniverses of a shared ambient model."""

    mapping: dict[int, int]
    domain: frozenset[int]
    image: frozenset[int]

    def vector_call(self, tup: tuple[int, ...]) -> tuple[int, ...]:
        """Apply the arrow componentwise; raise if *tup* leaves the domain."""
        if not all(x in self.mapping for x in tup):
            raise ValueError("tuple outside homomorphism domain")
        return tuple(self.mapping[x] for x in tup)


@dataclass(frozen=True)
class LindenbaumResult:
    """Join-irreducible closures for one fragment and arity."""

    fragment: FragmentKind
    arity: int
    model_key: str
    join_irreducibles: list[frozenset[tuple[int, ...]]]

    @property
    def count(self) -> int:
        """Number of join-irreducible atoms."""
        return len(self.join_irreducibles)

    def fingerprints(self) -> list[str]:
        """Stable SHA256 prefixes of each JI extension (discovery order)."""
        return [relation_fingerprint(ji) for ji in self.join_irreducibles]


def relation_fingerprint(tuples: Iterable[tuple[int, ...]]) -> str:
    """Stable short fingerprint for a finite relation extension."""
    payload = "\n".join(",".join(map(str, row)) for row in sorted(tuples))
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def induce_submodel(model: Model, sub: set[int] | frozenset[int]) -> Model:
    """Restrict *model* operations to a closed subuniverse (same labels)."""
    universe = sorted(sub)
    operations: dict[str, Operation] = {}
    for name, op in model.operations.items():
        operations[name] = op.restrict(set(sub))
    return Model(universe=universe, operations=operations)


def chain_product_lattice(width: int, height: int) -> Model:
    """Build the tiporet lattice ``C_width x C_height`` (meet/join only).

    For ``2 x 2`` this is the Boolean lattice ``B_2``. Larger grids are direct
    products of Heyting chains with implication dropped.
    """
    from fopy.bridge import to_finite_model
    from fopy.builders import heyting_chain
    from fopy.builders.catalog import boolean_lattice
    from fopy.finite.products import direct_product

    if width < 1 or height < 1:
        raise ValueError("chain factors must be at least 1")
    if width == height == 2:
        return to_finite_model(boolean_lattice(2))
    left = to_finite_model(heyting_chain(width))
    right = to_finite_model(heyting_chain(height))
    model = direct_product(left, right)
    model.operations = {sym: op for sym, op in model.operations.items() if sym in ("meet", "join")}
    return model


def parse_grid_name(name: str) -> tuple[int, int]:
    """Parse ``\"2x2\"`` / ``\"3x3\"`` style lattice grid names."""
    raw = name.strip().lower().replace(" ", "")
    if "x" not in raw:
        raise ValueError(f"expected grid like '2x2', got {name!r}")
    left, right = raw.split("x", 1)
    return int(left), int(right)


def _normalize_fragment(fragment: str) -> FragmentKind:
    key = fragment.strip().lower()
    if key in ("ep", "existential-positive", "existential_positive"):
        return "ep"
    if key in ("open", "qf", "quantifier-free", "quantifier_free"):
        return "open"
    raise ValueError(f"unsupported Lindenbaum fragment {fragment!r}; use 'ep' or 'open'/'qf'")


def _subuniverses(model: Model) -> list[frozenset[int]]:
    if len(model.universe) > 8:
        raise ValueError("Lindenbaum morphism census requires |U| <= 8")
    items = list(subalgebra_lattice(model))
    return sorted((frozenset(s) for s in items), key=lambda s: (-len(s), sorted(s)))


def _morphisms(model: Model, fragment: FragmentKind) -> list[HomArrow]:
    """Enumerate subalgebra morphisms for EP (homs) or open (isos)."""
    subs = _subuniverses(model)
    arrows: list[HomArrow] = []
    seen: set[tuple[frozenset[int], frozenset[int], tuple[tuple[int, int], ...]]] = set()

    for source_sub in subs:
        src_model = induce_submodel(model, source_sub)
        for target_sub in subs:
            tgt_model = induce_submodel(model, target_sub)
            for mapping in homomorphisms(src_model, tgt_model):
                image = frozenset(mapping.values())
                if fragment == "open" and image != target_sub:
                    continue
                if fragment == "open" and len(image) != len(source_sub):
                    continue
                key = (source_sub, image, tuple(sorted(mapping.items())))
                if key in seen:
                    continue
                seen.add(key)
                arrows.append(HomArrow(mapping=dict(mapping), domain=source_sub, image=image))
                if len(image) == len(source_sub):
                    inv = {t: s for s, t in mapping.items()}
                    inv_arrow = HomArrow(mapping=inv, domain=image, image=source_sub)
                    inv_key = (image, source_sub, tuple(sorted(inv.items())))
                    if inv_key not in seen:
                        seen.add(inv_key)
                        arrows.append(inv_arrow)
    return arrows


def _closure(
    seed: tuple[int, ...],
    arrows: Sequence[HomArrow],
) -> frozenset[tuple[int, ...]]:
    """Saturate *seed* under componentwise application of *arrows*."""
    result: list[tuple[int, ...]] = [seed]
    checked: list[tuple[int, ...]] = []
    while len(result) != len(checked):
        for tup in list(result):
            if tup in checked:
                continue
            for arrow in arrows:
                try:
                    image = arrow.vector_call(tup)
                except ValueError:
                    continue
                if image not in result:
                    result.append(image)
                    result.sort()
            checked.append(tup)
            checked.sort()
    return frozenset(result)


def join_irreducibles(
    model: Model,
    arity: int,
    *,
    fragment: str = "ep",
    model_key: str = "M",
) -> LindenbaumResult:
    """Join-irreducibles of the Lindenbaum algebra for *fragment* on *model*.

    Algorithm (single-model family): enumerate subalgebra morphisms (EP: all
    homs; open/QF: isomorphisms), saturate each arity-*arity* tuple under those
    arrows, and discard seeds already covered by a prior closure. Matches the
    classical ``existential_positive_lindenbaum`` / open variants without Minion.

    Args:
        model: Finite algebra (operations only matter).
        arity: Tuple arity of the generated atoms.
        fragment: ``\"ep\"`` or ``\"open\"`` / ``\"qf\"``.
        model_key: Label stored on the result (for CLI/census).

    Returns:
        :class:`LindenbaumResult` with JI closures in discovery order.

    Raises:
        ValueError: On unsupported fragment, bad arity, or oversized universe.
    """
    if arity < 1:
        raise ValueError("arity must be at least 1")
    kind = _normalize_fragment(fragment)
    arrows = _morphisms(model, kind)
    singletons: list[tuple[int, ...]] = [tuple(t) for t in product(model.universe, repeat=arity)]
    jis: list[frozenset[tuple[int, ...]]] = []
    while singletons:
        seed = singletons.pop()
        closed = _closure(seed, arrows)
        jis.append(closed)
        for tup in closed:
            if tup in singletons:
                singletons.remove(tup)
    return LindenbaumResult(
        fragment=kind,
        arity=arity,
        model_key=model_key,
        join_irreducibles=jis,
    )


def existential_positive_lindenbaum(
    model: Model,
    arity: int,
    *,
    model_key: str = "M",
) -> LindenbaumResult:
    """EP Lindenbaum join-irreducibles (alias of :func:`join_irreducibles`)."""
    return join_irreducibles(model, arity, fragment="ep", model_key=model_key)


def open_lindenbaum(
    model: Model,
    arity: int,
    *,
    model_key: str = "M",
) -> LindenbaumResult:
    """Open/QF Lindenbaum join-irreducibles via subalgebra isomorphisms."""
    return join_irreducibles(model, arity, fragment="open", model_key=model_key)


def census_fingerprints(
    model: Model,
    arity: int,
    *,
    fragment: str = "ep",
    model_key: str = "M",
) -> dict[str, object]:
    """Run Lindenbaum and return a JSON-serializable census row."""
    result = join_irreducibles(model, arity, fragment=fragment, model_key=model_key)
    return {
        "fragment": result.fragment,
        "arity": result.arity,
        "model_key": result.model_key,
        "universe_size": len(model.universe),
        "join_irreducible_count": result.count,
        "fingerprints": result.fingerprints(),
    }
