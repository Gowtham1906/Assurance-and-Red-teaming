"""Tests for the golden dataset module (W2-3)."""

from __future__ import annotations

from pathlib import Path

import pytest

from assure_core.datasets import (
    dataset_hash,
    load_dataset,
    split_dev_sealed,
    validate_case,
)

SAMPLE = Path(__file__).resolve().parents[1] / "datasets" / "golden-sample.json"


def test_sample_loads_and_validates():
    cases = load_dataset(SAMPLE)
    assert len(cases) == 5
    assert {c["target"] for c in cases} == {"bok", "agent"}


def test_validate_case_missing_field():
    errs = validate_case({"id": "x", "target": "bok"})
    assert any("input" in e for e in errs)
    assert any("expectations" in e for e in errs)


def test_validate_case_bad_target():
    errs = validate_case({"id": "x", "target": "nope", "input": "q", "expectations": {}})
    assert any("target" in e for e in errs)


def test_hash_is_stable_and_order_independent():
    cases = load_dataset(SAMPLE)
    h1 = dataset_hash(cases)
    h2 = dataset_hash(list(reversed(cases)))  # reordering must not change the hash
    assert h1 == h2
    assert len(h1) == 64  # sha-256 hex


def test_hash_changes_when_content_changes():
    cases = load_dataset(SAMPLE)
    h1 = dataset_hash(cases)
    mutated = [dict(c) for c in cases]
    mutated[0]["input"] = "CHANGED"
    assert dataset_hash(mutated) != h1


def test_split_is_deterministic_and_disjoint():
    cases = load_dataset(SAMPLE)
    dev1, sealed1 = split_dev_sealed(cases, sealed_fraction=0.4)
    dev2, sealed2 = split_dev_sealed(cases, sealed_fraction=0.4)
    # deterministic
    assert [c["id"] for c in dev1] == [c["id"] for c in dev2]
    assert [c["id"] for c in sealed1] == [c["id"] for c in sealed2]
    # disjoint + complete
    dev_ids = {c["id"] for c in dev1}
    sealed_ids = {c["id"] for c in sealed1}
    assert dev_ids.isdisjoint(sealed_ids)
    assert dev_ids | sealed_ids == {c["id"] for c in cases}


def test_duplicate_id_rejected(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(
        '[{"id":"a","target":"bok","input":"q","expectations":{}},'
        '{"id":"a","target":"bok","input":"q2","expectations":{}}]',
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        load_dataset(bad)
