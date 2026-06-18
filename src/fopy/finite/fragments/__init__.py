"""Logic-fragment definability checks via k-type partitions."""

from __future__ import annotations

from fopy.finite.definability import DefinabilityResult
from fopy.finite.fragments.ep_ktypes import is_ep_definable
from fopy.finite.fragments.fo_ktypes import is_fo_definable
from fopy.finite.fragments.horn_ktypes import is_horn_definable
from fopy.finite.fragments.pp_ktypes import is_pp_definable
from fopy.finite.models import Model
from fopy.finite.relops import Relation

__all__ = ["check_fragment"]


def _int_kw(kwargs: dict[str, object], key: str, default: int) -> int:
    value = kwargs.get(key, default)
    return value if isinstance(value, int) else default


def check_fragment(
    model: Model,
    target: Relation,
    fragment: str,
    **kwargs: object,
) -> DefinabilityResult:
    """Route a normalised fragment name to the corresponding k-type checker.

    Args:
        model: Finite model providing the signature.
        target: Relation under test.
        fragment: Canonical fragment key (``"pp"``, ``"ep"``, ``"horn"``, ``"fo"``).
        **kwargs: Fragment-specific options (``max_depth``, ``max_k``, …).

    Returns:
        :class:`~fopy.finite.definability.DefinabilityResult` from the selected
        fragment module.

    Raises:
        NotImplementedError: If *fragment* is not handled by the k-type layer.
        ValueError: If tuple enumeration exceeds the partition size guard.
    """
    match fragment:
        case "pp":
            max_depth = _int_kw(kwargs, "max_depth", 2)
            return is_pp_definable(model, target, max_depth=max_depth)
        case "ep":
            max_depth = _int_kw(kwargs, "max_depth", 2)
            max_existentials = _int_kw(kwargs, "max_existentials", 1)
            return is_ep_definable(
                model,
                target,
                max_depth=max_depth,
                max_existentials=max_existentials,
            )
        case "horn":
            max_depth = _int_kw(kwargs, "max_depth", 2)
            max_clauses = _int_kw(kwargs, "max_clauses", 4)
            max_atoms = _int_kw(kwargs, "max_atoms", 2)
            return is_horn_definable(
                model,
                target,
                max_depth=max_depth,
                max_clauses=max_clauses,
                max_atoms=max_atoms,
            )
        case "fo":
            max_k = _int_kw(kwargs, "max_k", 2)
            return is_fo_definable(model, target, max_k=max_k)
        case _:
            raise NotImplementedError(f"Fragment {fragment!r} is not supported by k-type checkers.")
