"""Signature and Structure edge cases."""

from __future__ import annotations

import pytest

import fopy as fo


def test_signature_add_sub():
    a = fo.Signature(functions={"f": 2}, relations={"R": 1})
    b = fo.Signature(functions={"g": 1}, relations={"S": 2})
    c = a + b
    assert "f" in c.functions and "S" in c.relations
    d = c - b
    assert "g" not in d.functions


def test_signature_is_subtype_false():
    a = fo.Signature(functions={"f": 2})
    b = fo.Signature(functions={"f": 3})
    assert not a.is_subtype_of(b)


def test_structure_missing_function_raises():
    sig = fo.Signature(functions={"f": 2})
    with pytest.raises(ValueError):
        fo.Structure(sig, [0], functions={}, relations={})


def test_structure_missing_relation_raises():
    sig = fo.Signature(relations={"R": 1})
    with pytest.raises(ValueError):
        fo.Structure(sig, [0], functions={}, relations={})


def test_structure_from_tables_missing_key():
    sig = fo.Signature(functions={"f": 2})
    with pytest.raises(KeyError):
        fo.Structure.from_tables(sig, [0], functions={})


def test_call_function_dict(b2_structure):
    assert b2_structure.call_function("meet", (0, 1)) is not None


def test_call_relation_set(b2_structure):
    assert isinstance(b2_structure.call_relation("leq", (0, 0)), bool)


def test_structure_name_default():
    s = fo.builders.chain(2)
    assert s.name == ""
