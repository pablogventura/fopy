"""DefLab CLI: check, Lindenbaum, fragment census, and discovery sweep."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from fopy.discovery.sweep import (
    DEFAULT_GRIDS,
    DEFAULT_JOBS,
    JobSpec,
    SMALL_MODEL_STEMS,
    default_runs_dir,
    run_sweep,
    write_run,
)
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
    result = check_definability(
        model,
        target,
        fragment=args.fragment,
        engine=args.engine,
    )
    payload: dict[str, Any] = {
        "fragment": args.fragment,
        "engine": args.engine,
        "backend": result.fragment,
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


def _parse_jobs(raw: str | None) -> tuple[JobSpec, ...]:
    if not raw:
        return DEFAULT_JOBS
    jobs: list[JobSpec] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if "/" in part:
            frag, eng = part.split("/", 1)
        else:
            frag, eng = part, "auto"
        jobs.append(JobSpec(frag.strip(), eng.strip()))
    if not jobs:
        return DEFAULT_JOBS
    return tuple(jobs)


def _cmd_sweep(args: argparse.Namespace) -> int:
    grids = tuple(g.strip() for g in args.grids.split(",") if g.strip()) or DEFAULT_GRIDS
    jobs = _parse_jobs(args.jobs)
    stem_set = None if args.all_models else SMALL_MODEL_STEMS
    runs_dir = Path(args.output_dir) if args.output_dir else default_runs_dir()
    runs_dir.mkdir(parents=True, exist_ok=True)
    from datetime import datetime, timezone

    stamp = args.tag or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    jsonl_path = runs_dir / f"{stamp}.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as fh:
        records = run_sweep(
            grids=grids,
            stems=stem_set,
            jobs=jobs,
            allow_large_morph=bool(args.allow_large_morph),
            max_models=args.max_models,
            max_universe=args.max_universe,
            rayon_threads=args.rayon_threads,
            job_timeout_s=args.job_timeout,
            jsonl_fh=fh,
        )
    _, summary_path = write_run(
        records, runs_dir=runs_dir, tag=stamp, jsonl_already_written=True
    )
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "jsonl": str(jsonl_path),
                "summary": str(summary_path),
                "total_rows": summary["total_rows"],
                "decided": summary["decided"],
                "skipped": summary["skipped"],
                "errors": summary["errors"],
                "disagreement_count": len(summary["disagreements"]),
                "disagreements": summary["disagreements"][:20],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 1 if summary["errors"] else 0


def build_parser() -> argparse.ArgumentParser:
    """Build the ``deflab`` argument parser."""
    parser = argparse.ArgumentParser(
        prog="deflab",
        description="DefLab CLI: fragment definability check, Lindenbaum, census, sweep",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    check_p = sub.add_parser("check", help="Decide definability of a target relation")
    check_p.add_argument(
        "--fragment",
        default="qf",
        help="Logic fragment (qf, qf_pos, ep, ex, pp, atomic_conj, fo, horn, gf, ...)",
    )
    check_p.add_argument(
        "--engine",
        default="auto",
        choices=["auto", "split", "merge", "ktypes", "hit"],
        help="Backend mode: split/merge/ktypes/hit (default auto per fragment)",
    )
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

    sweep_p = sub.add_parser(
        "sweep",
        help="Discovery sweep: grids + .model x targets x fragments -> JSONL",
    )
    sweep_p.add_argument(
        "--grids",
        default=",".join(DEFAULT_GRIDS),
        help="Comma-separated grid presets (default: 2x2 only; add 3x2 carefully)",
    )
    sweep_p.add_argument(
        "--jobs",
        default=None,
        help="Comma-separated fragment[/engine] list (default: built-in DEFAULT_JOBS)",
    )
    sweep_p.add_argument(
        "--all-models",
        action="store_true",
        help="Do not filter .model files by SMALL_MODEL_STEMS (still |U| capped)",
    )
    sweep_p.add_argument(
        "--allow-large-morph",
        action="store_true",
        help="Allow ep/ex/merge on |U|>4 (RAM risk)",
    )
    sweep_p.add_argument(
        "--max-universe",
        type=int,
        default=5,
        help="Skip models with |U| larger than this (default: 5)",
    )
    sweep_p.add_argument(
        "--rayon-threads",
        type=int,
        default=2,
        help="Cap RAYON_NUM_THREADS for Rust engines (default: 2)",
    )
    sweep_p.add_argument(
        "--job-timeout",
        type=float,
        default=20.0,
        help="Wall-clock seconds per cell (default: 20; 0 disables)",
    )
    sweep_p.add_argument(
        "--max-models",
        type=int,
        default=None,
        help="Cap number of loaded models (debug)",
    )
    sweep_p.add_argument(
        "--output-dir",
        default=None,
        help="Directory for JSONL + summary (default: fopy/discovery/runs)",
    )
    sweep_p.add_argument(
        "--tag",
        default=None,
        help="Run id stamp (default: UTC YYYYMMDD_HHMMSS)",
    )
    sweep_p.set_defaults(func=_cmd_sweep)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
