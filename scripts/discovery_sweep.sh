#!/usr/bin/env bash
# DefLab discovery sweep wrapper (RAM-safe defaults).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/fopy/src${PYTHONPATH:+:$PYTHONPATH}"
# Cap Rust rayon before any engine spawn (override with --rayon-threads).
export RAYON_NUM_THREADS="${RAYON_NUM_THREADS:-2}"

cd "$ROOT/fopy"
exec python3 -m fopy.cli.deflab sweep "$@"
