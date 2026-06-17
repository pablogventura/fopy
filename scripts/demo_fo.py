#!/usr/bin/env python3
"""Demo: FO formulas, builders, and open definability."""

from __future__ import annotations

from pathlib import Path

import fopy as fo


def main() -> None:
    print("=== fopy demo ===\n")

    x, y = fo.symbols("x y")
    f = fo.FuncSymbol("f", 2)
    c = fo.ConstantSymbol("c")
    R = fo.RelSymbol("R", 2)
    P = fo.RelSymbol("P", 1)

    phi = fo.forall(x, fo.exists(y, R(f(x, c), y) & P(y)))
    print("Formula:", phi)
    print("LaTeX:", fo.latex(phi))
    print("Free vars:", fo.free_vars(phi))

    chain = fo.builders.chain(4)
    leq = fo.RelSymbol("leq", 2)
    order = fo.forall(x, fo.forall(y, leq(x, y) >> leq(y, x)))
    print("\nChain order axiom satisfiable:", order.satisfy(chain))

    minimal = Path(__file__).resolve().parent.parent / "tests/fixtures/minimal.model"
    if minimal.exists():
        m = fo.parse_model(minimal)
        target = m.targets.get("T0")
        if target is None:
            target = next(v for k, v in m.relations.items() if k.startswith("T"))
        result = fo.finite.is_open_definable(m, target)
        print(f"\nOpen definability ({minimal.name}): definable={result.definable}")

    print("\nDone.")


if __name__ == "__main__":
    main()
