"""High-level open definability interface."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from fopy.finite.hit import Counterexample, HitConfig, is_open_def
from fopy.finite.models import Model
from fopy.finite.open_formulas import Formula, false_formula
from fopy.finite.preprocessing import preprocesamiento2
from fopy.finite.relops import Relation

if TYPE_CHECKING:
    from fopy.finite.explain import ExplainReport
    from fopy.structures import Structure


@dataclass
class DefinabilityResult:
    """Outcome of an open-definability decision procedure.

    Attributes:
        definable: Whether a defining open formula exists.
        formula: Witness formula when definable.
        counterexample: HIT obstruction when not definable.
        fragment: Logic fragment label (typically ``"open"``).
        witness_tuples: Tuple witnesses extracted from a counterexample.
    """

    definable: bool
    formula: Formula | None = None
    counterexample: Counterexample | None = None
    fragment: str = "open"
    witness_tuples: list[tuple[int, ...]] | None = None


def is_open_definable(
    model: Model,
    target: Relation,
    config: HitConfig | None = None,
) -> DefinabilityResult:
    """Decide whether *target* is open-definable from the operations of *model*.

    Args:
        model: Finite structure providing the signature.
        target: Relation to define in terms of operations.
        config: Optional HIT search configuration.

    Returns:
        :class:`DefinabilityResult` with a formula or counterexample.
    """
    cfg = config or HitConfig()
    preprocessed = preprocesamiento2(target)
    combined = false_formula(None)
    for prep_target in preprocessed:
        result = is_open_def(model, [prep_target], cfg)
        if isinstance(result, Counterexample):
            witnesses = [tuple(t) for t in result.tuples]
            return DefinabilityResult(
                definable=False,
                counterexample=result,
                fragment="open",
                witness_tuples=witnesses,
            )
        post = prep_target.pattern.postprocessed_formula() if prep_target.pattern else result
        combined = combined.or_formula(result.and_formula(post))
    return DefinabilityResult(definable=True, formula=combined, fragment="open")


def check_definability(
    model: Model,
    target: Relation | str,
    fragment: str = "qf",
    **kwargs: object,
) -> DefinabilityResult:
    """Decide definability of *target* in the requested logic *fragment*.

    Routes quantifier-free fragments to :func:`is_open_definable` (HIT) and
    dispatches ``pp``, ``ep``, ``horn``, and ``fo`` to the bounded k-type
    checkers under :mod:`fopy.finite.fragments`.

    Args:
        model: Finite structure providing the signature.
        target: Relation to define.
        fragment: Fragment name (``"qf"``, ``"open"``, ``"pp"``, ``"ep"``,
            ``"horn"``, ``"fo"``, …).
        **kwargs: Forwarded to fragment-specific checkers (``config`` for QF,
            ``max_depth`` / ``max_k`` for k-type layers).

    Returns:
        :class:`DefinabilityResult` for the selected fragment.

    Raises:
        NotImplementedError: If *fragment* is not supported.
        ValueError: If k-type enumeration exceeds the partition size guard.
    """
    from fopy.finite.explain import normalize_fragment, resolve_target

    norm = normalize_fragment(fragment)
    rel = resolve_target(model, target)
    if norm == "qf":
        config = kwargs.get("config")
        hit_cfg = config if isinstance(config, HitConfig) else None
        return is_open_definable(model, rel, hit_cfg)
    from fopy.finite.fragments import check_fragment

    return check_fragment(model, rel, norm, **kwargs)


class Definability:
    """Namespace for definability checks and explanations (doc-style API)."""

    @staticmethod
    def check(
        model: Model,
        target: Relation | str,
        fragment: str = "qf",
        **kwargs: object,
    ) -> DefinabilityResult:
        """Alias for :func:`check_definability`."""
        return check_definability(model, target, fragment=fragment, **kwargs)

    @staticmethod
    def explain(
        algebra: Model | Structure,
        target: Relation | str,
        *,
        fragment: str = "qf",
        config: object | None = None,
        max_synth_depth: int = 3,
    ) -> ExplainReport:
        """Alias for :func:`~fopy.finite.explain.explain_definability`."""
        from fopy.finite.explain import explain_definability

        return explain_definability(
            algebra,
            target,
            fragment=fragment,
            config=config,
            max_synth_depth=max_synth_depth,
        )
