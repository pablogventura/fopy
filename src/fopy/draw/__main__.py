"""CLI entry point: render standard example Hasse diagrams."""

from __future__ import annotations

from pathlib import Path

from fopy.draw import boolean_lattice, chain, draw_lattice, m3, n5


def main() -> None:
    out = Path("out")
    out.mkdir(parents=True, exist_ok=True)

    examples = [
        ("B2.svg", boolean_lattice(2)),
        ("B3.svg", boolean_lattice(3)),
        ("chain5.svg", chain(5)),
        ("M3.svg", m3()),
        ("N5.svg", n5()),
    ]

    for name, spec in examples:
        path = out / name
        draw_lattice(spec, filename=path)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
