"""Direct HIT and preprocessing coverage."""

import pytest

from fopy.finite.hit import HitConfig, is_open_def
from fopy.finite.preprocessing import split_targets
from fopy.finite.relops import Relation


def test_split_targets_unary(minimal_model):
    rel = Relation.new("T", 1)
    rel.add([0])
    rel.add([1])
    parts = split_targets(rel)
    assert len(parts) >= 1


def test_hit_config_defaults():
    cfg = HitConfig(use_information_gain=True, ig_sample=5)
    assert cfg.ig_sample == 5


def test_is_open_def_direct():
    from fopy.finite.preprocessing import split_targets
    from fopy.parse import parse_model
    from pathlib import Path

    path = Path(__file__).resolve().parent / "fixtures" / "minimal.model"
    model = parse_model(path, preprocess=True)
    targets = [r for s, r in model.relations.items() if s.startswith("T")]
    if not targets:
        pytest.skip("no target")
    prepped = split_targets(targets[0])
    result = is_open_def(model, prepped[:1], HitConfig())
    assert result is not None


def test_information_gain():
    from fopy.finite.hit import information_gain_from_counts

    gain = information_gain_from_counts(10, 5, {(0, True): (3, 2), (1, False): (2, 3)})
    assert gain >= 0


def test_relops_restrict():
    rel = Relation.new("R", 2)
    rel.add([0, 1])
    sub = rel.restrict({0})
    assert all(all(x in {0} for x in t) for t in sub.r)


def test_open_formula_extension(minimal_model):
    from fopy.finite.open_formulas import Variable, eq
    from fopy.finite.open_formulas import Term

    x = Variable.new("x")
    t = Term.variable(x)
    f = eq(t, t)
    ext = f.extension(minimal_model, 1)
    assert ext
