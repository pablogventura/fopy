"""Export Hasse diagrams to external formats."""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Sequence


def _label(element: Hashable, labels: dict[Hashable, str] | None) -> str:
    if labels and element in labels:
        return labels[element]
    return str(element)


def hasse_to_mermaid(
    elements: Sequence[Hashable],
    covers: Iterable[tuple[Hashable, Hashable]],
    *,
    labels: dict[Hashable, str] | None = None,
) -> str:
    """Render Hasse covers as a Mermaid ``graph TD`` diagram.

    Args:
        elements: Poset elements (used for node declarations).
        covers: Hasse cover edges ``(lower, upper)``.
        labels: Optional display labels keyed by element.

    Returns:
        Mermaid source string.
    """
    lines = ["graph TD"]
    seen: set[Hashable] = set()
    for e in elements:
        if e not in seen:
            node_id = f"n{id(e)}"
            lines.append(f'    {node_id}["{_label(e, labels)}"]')
            seen.add(e)
    for a, b in covers:
        lines.append(f"    n{id(a)} --> n{id(b)}")
    return "\n".join(lines)


def hasse_to_graphviz(
    elements: Sequence[Hashable],
    covers: Iterable[tuple[Hashable, Hashable]],
    *,
    labels: dict[Hashable, str] | None = None,
) -> str:
    """Render Hasse covers as a Graphviz ``digraph`` source.

    Args:
        elements: Poset elements.
        covers: Hasse cover edges.
        labels: Optional display labels.

    Returns:
        DOT format string.
    """
    lines = ["digraph Hasse {"]
    for e in elements:
        lines.append(f'    n{id(e)} [label="{_label(e, labels)}"];')
    for a, b in covers:
        lines.append(f"    n{id(a)} -> n{id(b)};")
    lines.append("}")
    return "\n".join(lines)


def hasse_to_tikz(
    elements: Sequence[Hashable],
    covers: Iterable[tuple[Hashable, Hashable]],
    *,
    labels: dict[Hashable, str] | None = None,
) -> str:
    """Render Hasse covers as a minimal TikZ picture.

    Args:
        elements: Poset elements.
        covers: Hasse cover edges.
        labels: Optional display labels.

    Returns:
        LaTeX/TikZ source string.
    """
    lines = [
        "\\begin{tikzpicture}[every node/.style={circle,draw,minimum size=6mm}]",
    ]
    for i, e in enumerate(elements):
        lines.append(f"    \\node (n{id(e)}) at ({i},0) {{{_label(e, labels)}}};")
    for a, b in covers:
        lines.append(f"    \\draw (n{id(a)}) -- (n{id(b)});")
    lines.append("\\end{tikzpicture}")
    return "\n".join(lines)


def hasse_to_html(
    elements: Sequence[Hashable],
    covers: Iterable[tuple[Hashable, Hashable]],
    *,
    labels: dict[Hashable, str] | None = None,
    title: str = "Hasse diagram",
) -> str:
    """Render Hasse covers as a standalone HTML page with Mermaid.

    Args:
        elements: Poset elements.
        covers: Hasse cover edges.
        labels: Optional display labels.
        title: Page title.

    Returns:
        HTML document string embedding Mermaid markup.
    """
    mermaid = hasse_to_mermaid(elements, covers, labels=labels)
    return (
        "<!DOCTYPE html>\n"
        "<html><head>"
        f"<title>{title}</title>"
        '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>'
        "<script>mermaid.initialize({startOnLoad:true});</script>"
        "</head><body>"
        f"<h1>{title}</h1>\n"
        f'<pre class="mermaid">\n{mermaid}\n</pre>'
        "</body></html>"
    )
