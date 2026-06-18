"""Human-readable open definability explanations and certificates."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

from fopy.bridge import to_finite_model
from fopy.finite.definability import DefinabilityResult, check_definability
from fopy.finite.hit import Counterexample
from fopy.finite.models import Model
from fopy.finite.open_formulas import (
    Formula,
    FormulaKind,
    OpSym,
    Term,
    Variable,
)
from fopy.finite.relops import Relation
from fopy.structures import Structure

QF_FRAGMENTS = frozenset({"qf", "open", "quantifier-free"})
KTYPE_FRAGMENTS = frozenset({"pp", "ep", "horn", "fo"})
SUPPORTED_FRAGMENTS = QF_FRAGMENTS | KTYPE_FRAGMENTS
CERT_VERSION = 2
CERT_VERSION_LEGACY = 1


def normalize_fragment(fragment: str) -> str:
    """Normalize a logic fragment name to a canonical key.

    Args:
        fragment: User-facing fragment name (e.g. ``"open"``, ``"pp"``, ``"fo"``).

    Returns:
        Canonical fragment key among ``"qf"``, ``"pp"``, ``"ep"``, ``"horn"``,
        and ``"fo"``.

    Raises:
        NotImplementedError: If *fragment* is not a supported alias.
    """
    key = fragment.strip().lower()
    if key in QF_FRAGMENTS:
        return "qf"
    if key in KTYPE_FRAGMENTS:
        return key
    supported = ", ".join(sorted({"qf", "open", "pp", "ep", "horn", "fo"}))
    raise NotImplementedError(f"Fragment {fragment!r} is not supported. Supported: {supported}.")


def resolve_target(model: Model, target: Relation | str) -> Relation:
    """Resolve a target relation name or object on *model*.

    Args:
        model: Finite model carrying relations and targets.
        target: Relation instance or symbol name.

    Returns:
        The :class:`~fopy.finite.relops.Relation` for *target*.

    Raises:
        KeyError: If *target* is a name not present in ``model.targets`` or
            ``model.relations``.
    """
    if isinstance(target, Relation):
        return target
    if target in model.targets:
        return model.targets[target]
    if target in model.relations:
        return model.relations[target]
    raise KeyError(f"Target relation {target!r} not found in model")


def _term_signature(
    model: Model,
    tuple_vals: tuple[int, ...],
    *,
    max_depth: int = 3,
) -> tuple[Any, ...]:
    """Atomic type label: evaluations of terms up to *max_depth* on *tuple_vals*."""
    arity = len(tuple_vals)
    vector = {Variable.from_index(i): tuple_vals[i] for i in range(arity)}
    ops_by_arity: dict[int, list[str]] = {}
    for sym, op in model.operations.items():
        ops_by_arity.setdefault(op.arity, []).append(sym)
    for syms in ops_by_arity.values():
        syms.sort()

    terms: list[Term] = [Term.from_variable(Variable.from_index(i)) for i in range(arity)]
    signatures: list[int] = []

    for depth in range(max_depth + 1):
        current = [t for t in terms if t.grade() == depth]
        current.sort(key=str)
        for term in current:
            try:
                signatures.append(term.evaluate(model.operations, vector))
            except (KeyError, ValueError):
                signatures.append(-1)
        if depth == max_depth:
            break
        next_terms: list[Term] = []
        for ar, syms in sorted(ops_by_arity.items()):
            if ar == 0:
                continue
            for sym in syms:
                for args in _term_arg_tuples(terms, ar):
                    next_terms.append(Term.op_term(OpSym.new(sym, ar), list(args)))
        terms.extend(next_terms)

    return tuple(signatures)


def _term_arg_tuples(terms: list[Term], arity: int) -> list[tuple[Term, ...]]:
    if arity == 0:
        return [()]
    if arity == 1:
        return [(t,) for t in terms]
    result: list[tuple[Term, ...]] = [()]
    for _ in range(arity):
        result = [r + (t,) for r in result for t in terms]
    return result


def atomic_type(
    model: Model,
    tuple_vals: tuple[int, ...] | list[int],
    *,
    max_depth: int = 3,
) -> tuple[Any, ...]:
    """Compute an atomic type label for a tuple of universe elements.

    Two tuples share a label when no quantifier-free formula over the model
    signature can distinguish them at the given term depth.

    Args:
        model: Finite model providing operation tables.
        tuple_vals: Universe indices forming the tuple to classify.
        max_depth: Maximum term nesting depth when evaluating signatures.

    Returns:
        Hashable signature tuple used to compare atomic types.
    """
    return _term_signature(model, tuple(tuple_vals), max_depth=max_depth)


@dataclass(frozen=True)
class Obstruction:
    """Witness pair for non-definability in the QF fragment.

    Attributes:
        tuple_in: Tuple that belongs to the target relation.
        tuple_out: Tuple that does not belong to the target relation.
        atomic_label: Shared atomic type signature of both tuples.
        message: Human-readable explanation of the obstruction.
    """

    tuple_in: tuple[int, ...]
    tuple_out: tuple[int, ...]
    atomic_label: tuple[Any, ...]
    message: str


_FRAGMENT_LABELS = {
    "qf": "quantifier-free",
    "pp": "positive primitive",
    "ep": "existential positive",
    "horn": "Horn",
    "fo": "first-order",
}


def _fragment_phrase(fragment: str) -> str:
    return _FRAGMENT_LABELS.get(fragment, fragment)


def explain_obstruction(
    model: Model,
    target: Relation,
    counterexample: Counterexample,
    *,
    max_depth: int = 1,
    fragment: str = "qf",
) -> Obstruction:
    """Build a human-readable obstruction from a HIT counterexample.

    Args:
        model: Finite model used during the definability check.
        target: Target relation under test.
        counterexample: HIT counterexample listing indistinguishable tuples.
        max_depth: Term depth bound when comparing atomic types.

    Returns:
        :class:`Obstruction` with witness pair and explanatory message.
    """
    tuples = [tuple(t) for t in counterexample.tuples]
    in_target = [t for t in tuples if target.contains(t)]
    out_target = [t for t in tuples if not target.contains(t)]
    t_in, t_out = _best_witness_pair(
        model, in_target, out_target, tuples, max_depth=max_depth, target=target
    )
    label = atomic_type(model, t_in, max_depth=max_depth)
    frag = _fragment_phrase(fragment)
    message = (
        f"Relation {target.sym} is not definable in the {_fragment_phrase(fragment)} fragment.\n"
        f"Obstruction: tuples {t_in} (in {target.sym}) and {t_out} (not in {target.sym}) "
        f"share the same atomic term type and cannot be separated by any {frag} formula "
        f"over this signature."
    )
    return Obstruction(tuple_in=t_in, tuple_out=t_out, atomic_label=label, message=message)


def _best_witness_pair(
    model: Model,
    in_target: list[tuple[int, ...]],
    out_target: list[tuple[int, ...]],
    fallback: list[tuple[int, ...]],
    *,
    max_depth: int,
    target: Relation,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    if in_target and out_target:
        return in_target[0], out_target[0]
    for t_in in in_target:
        label = atomic_type(model, t_in, max_depth=max_depth)
        for t_out in out_target:
            if atomic_type(model, t_out, max_depth=max_depth) == label:
                return t_in, t_out
    if len(model.universe) ** target.arity <= 256:
        found = _search_obstruction_pair(model, target, max_depth=max_depth)
        if found is not None:
            return found
    arity = target.arity
    valid = [t for t in fallback if len(t) == arity]
    for i, t_in in enumerate(valid):
        for t_out in valid[i + 1 :]:
            if target.contains(t_in) != target.contains(t_out):
                if target.contains(t_in):
                    return t_in, t_out
                return t_out, t_in
    if len(valid) >= 2:
        return valid[0], valid[1]
    single = fallback[0] if fallback else (0,)
    return single, single


def _search_obstruction_pair(
    model: Model,
    target: Relation,
    *,
    max_depth: int,
) -> tuple[tuple[int, ...], tuple[int, ...]] | None:
    from itertools import product

    arity = target.arity
    universe = model.universe
    for t_in in product(universe, repeat=arity):
        if not target.contains(t_in):
            continue
        label = atomic_type(model, t_in, max_depth=max_depth)
        for t_out in product(universe, repeat=arity):
            if target.contains(t_out):
                continue
            if atomic_type(model, t_out, max_depth=max_depth) == label:
                return t_in, t_out
    return None


def format_open_formula(formula: Formula) -> str:
    """Pretty-print an open formula in the ``open_parse`` dialect.

    Args:
        formula: Open formula AST node.

    Returns:
        String suitable for parsing with :func:`~fopy.finite.open_parse.parse_open_formula`.
    """
    match formula.kind:
        case FormulaKind.TRUE:
            return "true"
        case FormulaKind.FALSE:
            return "false"
        case FormulaKind.EQ:
            assert formula.t1 is not None
            assert formula.t2 is not None
            return f"eq({_format_open_term(formula.t1)},{_format_open_term(formula.t2)})"
        case FormulaKind.NEG:
            assert formula.inner is not None
            return f"-{format_open_formula(formula.inner)}"
        case FormulaKind.AND:
            parts = sorted(
                (format_open_formula(p) for p in formula.parts),
                key=len,
            )
            return " & ".join(parts)
        case FormulaKind.OR:
            parts = sorted(
                (format_open_formula(p) for p in formula.parts),
                key=len,
            )
            return " | ".join(parts)
    return ""


def _format_open_term(term: Term) -> str:
    from fopy.finite.open_formulas import TermKind

    if term.kind == TermKind.VARIABLE:
        assert term.variable is not None
        return term.variable.sym
    assert term.sym is not None
    args = ",".join(_format_open_term(a) for a in term.args)
    return f"{term.sym.op}({args})"


def latex_open_formula(formula: Formula) -> str:
    """Render an open formula as LaTeX.

    Args:
        formula: Open formula AST node.

    Returns:
        LaTeX math fragment (no surrounding math delimiters).
    """
    match formula.kind:
        case FormulaKind.TRUE:
            return r"\top"
        case FormulaKind.FALSE:
            return r"\bot"
        case FormulaKind.EQ:
            assert formula.t1 is not None
            assert formula.t2 is not None
            return f"{_latex_open_term(formula.t1)} = {_latex_open_term(formula.t2)}"
        case FormulaKind.NEG:
            assert formula.inner is not None
            return rf"\lnot ({latex_open_formula(formula.inner)})"
        case FormulaKind.AND:
            parts = r" \land ".join(latex_open_formula(p) for p in sorted(formula.parts, key=str))
            return rf"({parts})"
        case FormulaKind.OR:
            parts = r" \lor ".join(latex_open_formula(p) for p in sorted(formula.parts, key=str))
            return rf"({parts})"
    return ""


def _latex_open_term(term: Term) -> str:
    from fopy.finite.open_formulas import TermKind

    if term.kind == TermKind.VARIABLE:
        assert term.variable is not None
        sym = term.variable.sym
        if sym.startswith("x") and len(sym) > 1:
            return f"x_{{{sym[1:]}}}"
        return sym
    assert term.sym is not None
    args = ", ".join(_latex_open_term(a) for a in term.args)
    return rf"\mathrm{{{term.sym.op}}}({args})"


def model_fingerprint(model: Model) -> str:
    """Compute a stable short hash of universe and operation tables.

    Args:
        model: Finite model to fingerprint.

    Returns:
        First 16 hex digits of a SHA-256 digest of canonical model data.
    """
    parts: list[str] = [",".join(str(u) for u in model.universe)]
    for sym in sorted(model.operations):
        op = model.operations[sym]
        rows = sorted(f"{args}->{val}" for args, val in op.op.items())
        parts.append(f"{sym}:{';'.join(rows)}")
    digest = hashlib.sha256("|".join(parts).encode()).hexdigest()
    return digest[:16]


@dataclass
class ExplainReport:
    """Human-readable definability report wrapping :class:`DefinabilityResult`.

    Attributes:
        definable: Whether the target is definable in the requested fragment.
        fragment: Normalized fragment name (typically ``"qf"``).
        target_sym: Symbol of the target relation.
        formula: Witness open formula when definable.
        counterexample: Raw HIT counterexample when not definable.
        witness_tuples: Distinguished tuple pair for negative certificates.
        obstruction: Parsed obstruction witness when not definable.
        formula_minimal: Whether the witness formula is term-minimal (optional).
        min_term_depth: Minimal term depth of a witness formula (optional).
        synthesis_exhausted: Whether bounded synthesis explored its full search space.
        model_fingerprint: Short hash tying the report to a concrete model.
    """

    definable: bool
    fragment: str
    target_sym: str
    formula: Formula | None = None
    counterexample: Counterexample | None = None
    witness_tuples: list[tuple[int, ...]] = field(default_factory=list)
    obstruction: Obstruction | None = None
    formula_minimal: bool | None = None
    min_term_depth: int | None = None
    synthesis_exhausted: bool | None = None
    model_fingerprint: str | None = None

    @classmethod
    def from_check(
        cls,
        result: DefinabilityResult,
        model: Model,
        target: Relation,
        fragment: str,
    ) -> ExplainReport:
        """Build a report from a raw :class:`~fopy.finite.definability.DefinabilityResult`.

        Args:
            result: Outcome of :func:`~fopy.finite.definability.is_open_definable`.
            model: Finite model that was checked.
            target: Target relation that was checked.
            fragment: Normalized fragment label stored on the report.

        Returns:
            Populated :class:`ExplainReport` with obstruction data when applicable.
        """
        witnesses: list[tuple[int, ...]] = []
        obstruction: Obstruction | None = None
        if result.counterexample is not None:
            obstruction = explain_obstruction(
                model, target, result.counterexample, fragment=fragment
            )
            witnesses = [obstruction.tuple_in, obstruction.tuple_out]
        return cls(
            definable=result.definable,
            fragment=fragment,
            target_sym=target.sym,
            formula=result.formula,
            counterexample=result.counterexample,
            witness_tuples=witnesses,
            obstruction=obstruction,
        )

    def pretty(self) -> str:
        """Return a multi-line human-readable summary of the report."""
        if self.definable:
            ftxt = format_open_formula(self.formula) if self.formula else "(none)"
            lines = [
                f"Relation {self.target_sym} is definable in fragment {self.fragment} "
                f"({_fragment_phrase(self.fragment)}).",
                "",
                "A defining formula is:",
                "",
                f"    {ftxt}",
            ]
            if self.formula_minimal is not None and self.min_term_depth is not None:
                lines.extend(
                    [
                        "",
                        f"Minimal term depth: {self.min_term_depth} "
                        f"(minimal in search space: {self.formula_minimal}).",
                    ]
                )
                if self.synthesis_exhausted and self.formula_minimal:
                    lines.append(
                        "No simpler equivalent formula exists within the bounded "
                        "synthesis depth searched."
                    )
                elif self.synthesis_exhausted and not self.formula_minimal:
                    lines.append(
                        "Bounded synthesis exhausted its search space; a shorter "
                        "equivalent formula may exist outside the depth bound."
                    )
            return "\n".join(lines)
        if self.obstruction is not None:
            return self.obstruction.message
        return f"Relation {self.target_sym} is not definable in fragment {self.fragment}."

    def proof_sketch(self) -> str:
        """Return a short textual justification for the definability verdict."""
        if self.definable and self.formula is not None:
            return (
                "Positive certificate: the open formula above has the same extension "
                f"as {self.target_sym} on this finite model (verify via formula.extension)."
            )
        if self.obstruction is not None:
            o = self.obstruction
            frag = _fragment_phrase(self.fragment)
            return (
                f"Negative certificate: tuples {o.tuple_in} and {o.tuple_out} lie in the same "
                f"atomic type but differ on the target; no {frag} formula can separate them."
            )
        return "No proof sketch available."

    def counterexample_table(self) -> str:
        """Return a tab-separated table of witness tuples (up to 20 rows)."""
        if not self.witness_tuples:
            return "(no witness tuples)"
        lines = ["tuple\tin_target"]
        tin = self.obstruction.tuple_in if self.obstruction else None
        tout = self.obstruction.tuple_out if self.obstruction else None
        for t in self.witness_tuples[:20]:
            if tin is not None and t == tin:
                flag = "yes"
            elif tout is not None and t == tout:
                flag = "no"
            elif not self.definable and len(self.witness_tuples) >= 2:
                flag = "yes" if t == self.witness_tuples[0] else "no"
            else:
                flag = "?"
            lines.append(f"{t}\t{flag}")
        return "\n".join(lines)

    def latex(self) -> str:
        """Return LaTeX for the witness formula, or obstruction summary if undefinable."""
        if self.definable and self.formula is not None:
            return latex_open_formula(self.formula)
        if self.obstruction is not None:
            return (
                rf"\text{{Obstruction: }} {self.obstruction.tuple_in} "
                rf"\notin {self.obstruction.tuple_out}"
            )
        return ""

    def certificate(self) -> dict[str, Any]:
        """Serialize an offline-checkable certificate as a JSON-friendly dict."""
        return {
            "version": CERT_VERSION,
            "fragment": self.fragment,
            "definable": self.definable,
            "target_sym": self.target_sym,
            "formula": format_open_formula(self.formula) if self.formula else None,
            "witness_tuples": [list(t) for t in self.witness_tuples],
            "model_fingerprint": self.model_fingerprint,
        }

    def certificate_with_model(self, model: Model) -> dict[str, Any]:
        """Like :meth:`certificate`, embedding a fingerprint of *model*."""
        cert = self.certificate()
        cert["model_fingerprint"] = model_fingerprint(model)
        return cert

    def _repr_html_(self) -> str:
        """Jupyter/HTML representation with collapsible detail sections."""
        status = "definable" if self.definable else "not definable"
        color = "#1b5e20" if self.definable else "#b71c1c"
        summary = self.pretty().split("\n", 1)[0]
        body = self.pretty().replace("\n", "<br>")
        table = self.counterexample_table().replace("\n", "<br>")
        sketch = self.proof_sketch()
        parts = [
            f'<div style="border-left:4px solid {color};padding:0.5em 1em">',
            f"<strong>{self.target_sym}</strong> — {status} ({self.fragment})",
            f"<details open><summary>{summary}</summary>",
            f"<pre style='margin:0.5em 0'>{body}</pre></details>",
        ]
        if self.witness_tuples:
            parts.append(
                f"<details><summary>Witness table</summary>"
                f"<pre style='margin:0.5em 0'>{table}</pre></details>"
            )
        if sketch:
            parts.append(
                f"<details><summary>Proof sketch</summary>"
                f"<p style='margin:0.5em 0'>{sketch}</p></details>"
            )
        parts.append("</div>")
        return "".join(parts)


def explain_definability(
    algebra: Model | Structure,
    target: Relation | str,
    *,
    fragment: str = "qf",
    config: object | None = None,
    max_synth_depth: int = 3,
) -> ExplainReport:
    """Explain whether *target* is definable in the given *fragment*.

    Wraps :func:`~fopy.finite.definability.is_open_definable` and adds
    human-readable output and offline certificates.

    Args:
        algebra: Finite model or symbolic structure (converted via bridge).
        target: Target relation name or :class:`~fopy.finite.relops.Relation`.
        fragment: Logic fragment; ``"qf"``, ``"open"``, ``"pp"``, ``"ep"``,
            ``"horn"``, or ``"fo"``.
        config: Optional :class:`~fopy.finite.hit.HitConfig` for the HIT search.
        max_synth_depth: Term depth bound when searching for a minimal defining formula.
            ``0`` skips synthesis (faster; uses the formula from the HIT check only).

    Returns:
        :class:`ExplainReport` with formula or obstruction witnesses.

    Raises:
        NotImplementedError: If *fragment* is not supported.
        KeyError: If *target* is not found on the model.
    """
    from fopy.finite.hit import HitConfig
    from fopy.finite.synthesis import synthesize_defining_formula

    norm = normalize_fragment(fragment)
    model = to_finite_model(algebra) if isinstance(algebra, Structure) else algebra
    rel = resolve_target(model, target)
    hit_cfg = config if isinstance(config, HitConfig) else None
    result = check_definability(model, rel, fragment=norm, config=hit_cfg)
    report = ExplainReport.from_check(result, model, rel, norm)
    report.model_fingerprint = model_fingerprint(model)
    if report.definable and max_synth_depth > 0:
        syn = synthesize_defining_formula(model, rel, max_depth=max_synth_depth)
        if syn.formula is not None:
            report.formula = syn.formula
            report.formula_minimal = syn.minimal
            report.min_term_depth = syn.min_term_depth
            report.synthesis_exhausted = syn.exhausted
    return report


def verify_certificate(cert: dict[str, Any], model: Model, target: Relation | str) -> bool:
    """Verify an offline certificate against *model*.

    Args:
        cert: Certificate dict produced by :meth:`ExplainReport.certificate`.
        model: Finite model the certificate claims to describe.
        target: Target relation name or object verified by the certificate.

    Returns:
        ``True`` when the certificate matches *model* and supports its verdict.
    """
    version = cert.get("version")
    if version not in (CERT_VERSION, CERT_VERSION_LEGACY):
        return False
    rel = resolve_target(model, target)
    fp = cert.get("model_fingerprint")
    if fp is not None and fp != model_fingerprint(model):
        return False
    definable = cert.get("definable")
    if not isinstance(definable, bool):
        return False
    if definable:
        ftxt = cert.get("formula")
        if not isinstance(ftxt, str) or not ftxt:
            return False
        from fopy.finite.open_parse import parse_open_formula

        vars_map = {Variable.from_index(i).sym: Variable.from_index(i) for i in range(rel.arity)}
        try:
            formula = parse_open_formula(ftxt, vars_map, model.operations)
        except ValueError:
            return False
        ext = formula.extension(model, rel.arity)
        target_ext = set(rel.r)
        return ext == target_ext
    witnesses = cert.get("witness_tuples")
    if not isinstance(witnesses, list) or len(witnesses) < 2:
        return False
    t_in = tuple(witnesses[0])
    t_out = tuple(witnesses[1])
    if rel.contains(t_in) == rel.contains(t_out):
        from fopy.finite.definability import is_open_definable

        return not is_open_definable(model, rel).definable
    if atomic_type(model, t_in) == atomic_type(model, t_out):
        return True
    from fopy.finite.definability import is_open_definable

    return not is_open_definable(model, rel).definable
