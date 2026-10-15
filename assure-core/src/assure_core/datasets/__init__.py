"""Golden dataset handling (plan §7, W2-3).

A golden case is a JSON object with deterministic expectations attached, so the
harness can run checks D01-D11 against it. Datasets are split into:

  * dev   - visible to developers
  * sealed- held by the assurance team; kept out of prompts/retrieval; CI only

This module:
  * defines the case schema (``validate_case``)
  * loads a dataset file (``load_dataset``)
  * computes a stable CONTENT HASH for versioning (``dataset_hash``)
  * splits dev/sealed deterministically by case id (``split_dev_sealed``)

The hash + split let us record "which exact dataset version produced this run",
which the plan requires for auditable, contamination-controlled gating.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

# Required top-level fields on every golden case.
REQUIRED_FIELDS = ("id", "target", "input", "expectations")
VALID_TARGETS = ("bok", "agent")


def validate_case(case: dict[str, Any]) -> list[str]:
    """Return a list of validation errors for one case (empty = valid)."""
    errors: list[str] = []
    for f in REQUIRED_FIELDS:
        if f not in case:
            errors.append(f"missing field '{f}'")
    if "target" in case and case["target"] not in VALID_TARGETS:
        errors.append(f"target must be one of {VALID_TARGETS}, got '{case['target']}'")
    if "expectations" in case and not isinstance(case["expectations"], dict):
        errors.append("expectations must be an object")
    return errors


def load_dataset(path: str | Path) -> list[dict[str, Any]]:
    """Load and validate a JSON dataset file (a list of cases)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("dataset must be a JSON array of cases")
    all_errors: dict[str, list[str]] = {}
    seen_ids: set[str] = set()
    for i, case in enumerate(data):
        errs = validate_case(case)
        cid = case.get("id", f"<index {i}>")
        if cid in seen_ids:
            errs.append(f"duplicate id '{cid}'")
        seen_ids.add(cid)
        if errs:
            all_errors[cid] = errs
    if all_errors:
        raise ValueError(f"dataset validation failed: {all_errors}")
    return data


def dataset_hash(cases: list[dict[str, Any]]) -> str:
    """Stable SHA-256 over the dataset content (order-independent by id).

    Sorting by id and using canonical JSON means the same logical dataset always
    hashes identically, regardless of file ordering or key order.
    """
    canonical = json.dumps(
        sorted(cases, key=lambda c: c["id"]),
        sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def split_dev_sealed(
    cases: list[dict[str, Any]], sealed_fraction: float = 0.4
) -> tuple[list[dict], list[dict]]:
    """Deterministically split cases into (dev, sealed).

    Assignment is by a hash of the case id, so the same case always lands in the
    same split regardless of run order (reproducible contamination control).
    """
    dev, sealed = [], []
    for case in cases:
        h = int(hashlib.sha256(case["id"].encode("utf-8")).hexdigest(), 16)
        bucket = (h % 1000) / 1000.0
        (sealed if bucket < sealed_fraction else dev).append(case)
    return dev, sealed


__all__ = [
    "validate_case", "load_dataset", "dataset_hash", "split_dev_sealed",
    "REQUIRED_FIELDS", "VALID_TARGETS",
]
