"""Red-team case validation (plan section 9.2, W4-4).

Pure Python (no jsonschema dependency) so it runs in plain pytest and CI.
Mirrors redteam/schema/case.schema.json and adds two checks JSON Schema can't
express: every ATLAS ID must exist in the pinned release, and min_pass <= runs.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

REQUIRED = ("id", "title", "version", "category", "taxonomy", "target_type", "turns",
            "expected_safe_behaviour", "detection", "default_severity",
            "pass_criteria", "safety_handling", "provenance")
CATEGORIES = {"direct_injection", "indirect_injection", "system_prompt_leakage",
              "sensitive_data_disclosure", "cross_user_leakage", "vector_poisoning",
              "jailbreak", "harmful_content", "misinformation", "excessive_agency",
              "resource_exhaustion", "multilingual"}
SEVERITIES = {"critical", "high", "medium", "low", "info"}
NIST_TERMS = {"evasion", "poisoning", "privacy", "misuse"}
KNOWN_CHECKS = {f"D{n:02d}_{s}" for n, s in [(1, "schema"), (2, "pii"), (3, "banned"),
                (4, "citations"), (5, "tool"), (6, "limits"), (7, "language"),
                (8, "behavior"), (9, "determinism"), (10, "retrieval"), (11, "canary")]}


def validate_redteam_case(case: dict, atlas_ids: Iterable[str] | None = None,
                          atlas_version: str | None = None) -> list[str]:
    """Return a list of errors (empty list = valid)."""
    e: list[str] = []
    for f in REQUIRED:
        if f not in case:
            e.append(f"missing '{f}'")
    if e:
        return e
    if not re.fullmatch(r"rt-\d{3}(-[a-z0-9-]+)?", str(case["id"])):
        e.append("id must look like rt-001 or rt-001-short-name")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(case["version"])):
        e.append("version must be semver")
    if case["category"] not in CATEGORIES:
        e.append(f"unknown category '{case['category']}'")
    if case["target_type"] not in ("rag", "agent"):
        e.append("target_type must be rag or agent")
    if case["default_severity"] not in SEVERITIES:
        e.append(f"unknown severity '{case['default_severity']}'")

    tax = case["taxonomy"]
    for k in ("owasp_llm", "atlas_version", "atlas_ids", "nist_term"):
        if k not in tax:
            e.append(f"taxonomy missing '{k}'")
    for x in tax.get("owasp_llm", []):
        if not re.fullmatch(r"LLM(0[1-9]|10)", x):
            e.append(f"bad OWASP LLM id '{x}'")
    for x in tax.get("owasp_asi", []):
        if not re.fullmatch(r"ASI(0[1-9]|10)", x):
            e.append(f"bad OWASP ASI id '{x}'")
    if tax.get("nist_term") not in NIST_TERMS:
        e.append(f"unknown NIST term '{tax.get('nist_term')}'")
    if atlas_version and tax.get("atlas_version") != atlas_version:
        e.append(f"atlas_version {tax.get('atlas_version')} != pinned {atlas_version}")
    known = set(atlas_ids) if atlas_ids is not None else None
    for x in tax.get("atlas_ids", []):
        if not re.fullmatch(r"AML\.T\d{4}(\.\d{3})?", x):
            e.append(f"bad ATLAS id format '{x}'")
        elif known is not None and x not in known:
            e.append(f"ATLAS id '{x}' not in pinned release")

    if not case["turns"] or not all(t.get("role") in ("user", "document", "tool") and
                                    t.get("content") for t in case["turns"]):
        e.append("turns must be non-empty with role in user/document/tool and content")
    checks = case["detection"].get("checks", [])
    if not checks:
        e.append("detection.checks must list at least one check")
    for c in checks:
        if c not in KNOWN_CHECKS:
            e.append(f"unknown check '{c}'")
    pc = case["pass_criteria"]
    if not (isinstance(pc.get("runs"), int) and isinstance(pc.get("min_pass"), int)
            and 1 <= pc["min_pass"] <= pc["runs"]):
        e.append("pass_criteria needs integers with 1 <= min_pass <= runs")
    if "source" not in case["provenance"] or "date_added" not in case["provenance"]:
        e.append("provenance needs source and date_added")
    return e


__all__ = ["validate_redteam_case"]
