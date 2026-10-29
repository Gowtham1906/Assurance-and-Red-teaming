"""Tests for red-team case validation (W4-4)."""

from __future__ import annotations

import copy
import csv
import json
from pathlib import Path

import pytest

from assure_core.redteam import validate_redteam_case

ROOT = Path(__file__).resolve().parents[2]
CASES = sorted((ROOT / "redteam" / "cases").glob("*.json"))
ATLAS_CSV = ROOT / "redteam" / "atlas_v2026.10_techniques.csv"
ATLAS_IDS = {r["id"] for r in csv.DictReader(ATLAS_CSV.open(encoding="utf-8"))} if ATLAS_CSV.exists() else None


@pytest.mark.parametrize("path", CASES, ids=[p.stem for p in CASES])
def test_repo_cases_are_valid(path):
    case = json.loads(path.read_text(encoding="utf-8"))
    assert validate_redteam_case(case, ATLAS_IDS, "v2026.10") == []


def _example():
    return json.loads(CASES[0].read_text(encoding="utf-8"))


def test_unknown_atlas_id_rejected():
    c = _example()
    c["taxonomy"]["atlas_ids"] = ["AML.T9999"]
    assert any("not in pinned release" in e for e in validate_redteam_case(c, ATLAS_IDS))


def test_wrong_atlas_version_rejected():
    c = _example()
    c["taxonomy"]["atlas_version"] = "v2026.09"
    assert validate_redteam_case(c, ATLAS_IDS, "v2026.10")


def test_min_pass_above_runs_rejected():
    c = _example()
    c["pass_criteria"] = {"runs": 3, "min_pass": 5}
    assert validate_redteam_case(c)


def test_unknown_check_rejected():
    c = _example()
    c["detection"]["checks"] = ["D99_magic"]
    assert validate_redteam_case(c)


def test_missing_field_rejected():
    c = copy.deepcopy(_example())
    del c["safety_handling"]
    assert validate_redteam_case(c) == ["missing 'safety_handling'"]
