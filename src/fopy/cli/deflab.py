"""DefLab CLI: check, Lindenbaum, and fragment census."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from fopy.finite.definability import check_definability
from fopy.finite.lindenbaum import (
    census_fingerprints,
    chain_product_lattice,
    join_irreducibles,
    parse_grid_name,
)
from fopy.finite.models import Model
from fopy.parse import parse_model


def _load_model(spec: str) -> tuple[Model, str]:
    """Load a preset grid (``2x2``) or a ``.model`` path."""
    path = Path(spec)
    if path.is_file():
        return parse_model(str(path), preprocess=True), path.stem
    width, height = parse_grid_name(spec)
    model = chain_product_lattice(width, height)
    return model, f"C{width}x{height}"


def _cmd_check(args: argparse.Namespace) -> int:
    model, _ = _load_model(args.model)
    target = args.target
    if target is None:
        if not model.targets:
            print("error: --target required when model has no T* targets", file=sys.stderr)
            return 2
        target = next(iter(model.targets))
    result = check_definability(model, target, fragment=args.fragment)
    payload: dict[str, Any] = {
        "fragment": args.fragment,
        "target": target if isinstance(target, str) else getattr(target, "sym", str(target)),
        "definable": result.definable,
    }
    if result.formula is not None:
        payload["formula"] = str(result.formula)
    if result.witness_tuples is not None:
        payload["witness_tuples"] = [list(t) for t in result.witness_tuples]
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.definable else 1


def _cmd_lindenbaum(args: argparse.Namespace) -> int:
    model, key = _load_model(args.model)
    result = join_irreducibles(
        model,
        args.arity,
        fragment=args.fragment,
        model_key=key,
    )
    payload = {
        "fragment": result.fragment,
        "model": args.model,
        "model_key": result.model_key,
        "arity": result.arity,
        "universe_size": len(model.universe),
        "join_irreducible_count": result.count,
        "fingerprints": result.fingerprints(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _cmd_census(args: argparse.Namespace) -> int:
    model, key = _load_model(args.model)
    payload = census_fingerprints(
        model,
        args.arity,
        fragment=args.fragment,
        model_key=key,
    )
    payload["model"] = args.model
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the ``deflab`` argument parser."""
    parser = argparse.ArgumentParser(
        prog="deflab",
        description="DefLab CLI: fragment definability check, Lindenbaum, census",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    check_p = sub.add_parser("check", help="Decide definability of a target relation")
    check_p.add_argument("--fragment", default="qf", help="Logic fragment (qf, ep, pp, ...)")
    check_p.add_argument(
        "--model",
        required=True,
        help="Preset grid (e.g. 2x2) or path to a .model file",
    )
    check_p.add_argument(
        "--target",
        default=None,
        help="Target relation symbol (default: first T*)",
    )
    check_p.set_defaults(func=_cmd_check)

    lind_p = sub.add_parser("lindenbaum", help="Join-irreducibles of the Lindenbaum algebra")
    lind_p.add_argument("--fragment", default="ep", help="ep or open/qf")
    lind_p.add_argument("--model", required=True, help="Preset grid (e.g. 2x2) or .model path")
    lind_p.add_argument("--arity", type=int, required=True, help="Tuple arity")
    lind_p.set_defaults(func=_cmd_lindenbaum)

    census_p = sub.add_parser("census", help="Fingerprint census of Lindenbaum JIs")
    census_p.add_argument("--fragment", default="ep", help="ep or open/qf")
    census_p.add_argument("--model", required=True, help="Preset grid (e.g. 2x2) or .model path")
    census_p.add_argument("--arity", type=int, required=True, help="Tuple arity")
    census_p.add_argument("-o", "--output", default=None, help="Write JSON to this path")
    census_p.set_defaults(func=_cmd_census)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
