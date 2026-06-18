#!/usr/bin/env python3
"""Demo: explain_definability on a .model fixture."""

from __future__ import annotations

import sys
from pathlib import Path

from fopy.finite import TrustedKernel, explain_definability
from fopy.parse import parse_model

DEFAULT = Path(__file__).resolve().parent.parent / "tests/fixtures/models/minimal.model"


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    model = parse_model(path, preprocess=True)
    targets = [s for s in model.targets] or [s for s in model.relations if s.startswith("T")]
    if not targets:
        print("No target relation found", file=sys.stderr)
        return 1
    name = targets[0]
    report = explain_definability(model, name)
    print(report.pretty())
    print()
    print(report.proof_sketch())
    cert = report.certificate()
    ok = TrustedKernel.verify(cert, model, name)
    print(f"\nCertificate verifies: {ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
