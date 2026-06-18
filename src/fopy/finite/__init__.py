"""Finite structures, open formulas, and HIT definability."""

from fopy.finite.certificates import TrustedKernel, deserialize_certificate, serialize_certificate
from fopy.finite.definability import (
    Definability,
    DefinabilityResult,
    check_definability,
    is_open_definable,
)
from fopy.finite.eval_cache import EvalCache, satisfy_cached
from fopy.finite.explain import (
    ExplainReport,
    Obstruction,
    atomic_type,
    explain_definability,
    explain_obstruction,
    format_open_formula,
    latex_open_formula,
    normalize_fragment,
    resolve_target,
    verify_certificate,
)
from fopy.finite.formula_search import FormulaSearch
from fopy.finite.hit import (
    Block,
    Counterexample,
    HitConfig,
    IndicesTupleGenerator,
    TupleHistory,
    information_gain_from_counts,
    is_open_def,
)
from fopy.finite.model_checking import counterexample, models, satisfying_assignments
from fopy.finite.models import FiniteAlgebra, Model
from fopy.finite.open_formulas import (
    Formula,
    OpSym,
    Term,
    Variable,
    and_formula,
    eq,
    extension,
    false_formula,
    neg,
    or_formula,
    satisfy,
    true_formula,
    variables,
)
from fopy.finite.preprocessing import Pattern, preprocesamiento2, split_targets
from fopy.finite.products import direct_product
from fopy.finite.relops import Operation, Relation
from fopy.finite.synthesis import (
    SynthesisResult,
    formula_complexity,
    formula_max_term_depth,
    synthesize_defining_formula,
)
from fopy.finite.synthesis_cegis import CegisResult, cegis_synthesize
from fopy.finite.synthesis_smt import SmtSynthesisResult, smt_synthesize

__all__ = [
    "Block",
    "CegisResult",
    "Counterexample",
    "Definability",
    "DefinabilityResult",
    "EvalCache",
    "ExplainReport",
    "FiniteAlgebra",
    "Formula",
    "FormulaSearch",
    "HitConfig",
    "IndicesTupleGenerator",
    "Model",
    "Obstruction",
    "OpSym",
    "Operation",
    "Pattern",
    "Relation",
    "SmtSynthesisResult",
    "SynthesisResult",
    "Term",
    "TrustedKernel",
    "TupleHistory",
    "Variable",
    "and_formula",
    "atomic_type",
    "cegis_synthesize",
    "check_definability",
    "counterexample",
    "deserialize_certificate",
    "direct_product",
    "eq",
    "explain_definability",
    "explain_obstruction",
    "extension",
    "false_formula",
    "format_open_formula",
    "formula_complexity",
    "formula_max_term_depth",
    "information_gain_from_counts",
    "is_open_def",
    "is_open_definable",
    "latex_open_formula",
    "models",
    "neg",
    "normalize_fragment",
    "or_formula",
    "preprocesamiento2",
    "resolve_target",
    "satisfy",
    "satisfy_cached",
    "satisfying_assignments",
    "serialize_certificate",
    "smt_synthesize",
    "split_targets",
    "synthesize_defining_formula",
    "true_formula",
    "variables",
    "verify_certificate",
]
