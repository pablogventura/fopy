"""Verifiable certificates and trusted kernel."""

from __future__ import annotations

import json
from typing import Any, cast

from fopy.finite.explain import CERT_VERSION, verify_certificate
from fopy.finite.models import Model
from fopy.finite.relops import Relation


class TrustedKernel:
    """Minimal verifier for definability certificates."""

    @staticmethod
    def verify(cert: dict[str, Any] | str, model: Model, target: Relation | str) -> bool:
        """Return whether *cert* is a valid definability certificate for *target*.

        Args:
            cert: Certificate dict or JSON string.
            model: Structure the certificate refers to.
            target: Target relation or its symbol name.

        Returns:
            ``True`` if the certificate verifies; ``False`` otherwise.
        """
        data: dict[str, Any]
        if isinstance(cert, str):
            try:
                data = cast(dict[str, Any], json.loads(cert))
            except json.JSONDecodeError:
                return False
        else:
            data = cert
        if data.get("version") != CERT_VERSION:
            return False
        return verify_certificate(data, model, target)


def serialize_certificate(cert: dict[str, Any]) -> str:
    """Serialize a certificate dict to canonical JSON."""
    return json.dumps(cert, sort_keys=True)


def deserialize_certificate(data: str) -> dict[str, Any]:
    """Parse a certificate from JSON produced by :func:`serialize_certificate`."""
    return cast(dict[str, Any], json.loads(data))
