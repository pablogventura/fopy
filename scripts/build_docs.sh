#!/usr/bin/env bash
# Build the documentation site from docstrings (mkdocs + mkdocstrings).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -e ".[docs,draw]"
python3 -m mkdocs build --strict
echo "Built site/ — open site/index.html or run: mkdocs serve"
