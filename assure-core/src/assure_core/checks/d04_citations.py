"""D04 - Citation span validity (HARD gate).

Spec (plan §6):
    Implementation : cited document IDs exist in the retrieved set; quoted span
                     is a normalised substring of that chunk, or offsets match.
    Pass criterion : 100% of citations resolve; unsupported-citation rate 0.
    OWASP          : LLM09, LLM08.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from assure_core.result import CheckResult, failed_result, passed_result


def _normalise(text: str) -> str:
    """Lowercase + collapse whitespace for robust substring matching."""
    return re.sub(r"\s+", " ", text).strip().lower()


def check_citations(
    citations: Sequence[Mapping[str, Any]],
    retrieved: Mapping[str, str],
) -> CheckResult:
    """Fail if any citation's doc_id is missing or its quote isn't in that doc.

    Each citation: {"doc_id": str, "quote": str}. ``retrieved`` maps doc_id->text.
    """
    problems: list[dict] = []

    for i, cite in enumerate(citations):
        doc_id = cite.get("doc_id")
        quote = cite.get("quote", "")
        if doc_id not in retrieved:
            problems.append({"index": i, "doc_id": doc_id, "reason": "doc_id not retrieved"})
            continue
        if quote and _normalise(quote) not in _normalise(retrieved[doc_id]):
            problems.append(
                {"index": i, "doc_id": doc_id, "reason": "quote not found in document"}
            )

    if problems:
        return failed_result(
            "D04", f"{len(problems)} unsupported citation(s)", problems=problems
        )
    return passed_result("D04")
