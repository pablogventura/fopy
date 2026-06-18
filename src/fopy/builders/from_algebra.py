"""Build structures from Cayley tables."""

from __future__ import annotations

from typing import Any

from fopy.signature import Signature
from fopy.structures import Structure


def from_cayley(
    signature: Signature,
    operation: str,
    labels: list[Any],
    table: list[list[Any]],
) -> Structure:
    """Build a structure from a single-operation Cayley table.

    Args:
        signature: Language signature containing *operation*.
        operation: Function symbol for the binary operation.
        labels: Row/column labels for the Cayley table.
        table: ``n × n`` table of operation results indexed by *labels* positions.

    Returns:
        Structure with *operation* interpreted by *table*.

    Raises:
        ValueError: If *table* is not square or its size mismatches *labels*.
    """
    n = len(labels)
    if len(table) != n or any(len(row) != n for row in table):
        raise ValueError("Table must be n×n")
    label_index = {labels[i]: i for i in range(n)}
    fn_table: dict[tuple[Any, ...], Any] = {}
    for i, row in enumerate(table):
        for j, val in enumerate(row):
            mapped = val if val in labels else labels[label_index.get(val, val)]
            fn_table[(labels[i], labels[j])] = mapped
    return Structure.from_tables(
        signature,
        labels,
        functions={operation: fn_table},
    )
