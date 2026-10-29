"""D04 - Citation span validity (HARD gate).

Spec (plan §6):
    Implementation : cited document IDs exist in the retrieved set; quoted span
                     is a normalised substring of that chunk, or offsets match.
    Pass criterion : 100% of citations resolve; unsupported-citation rate 0.
    OWASP          : LLM09, LLM08.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping, Sequence
from typing import Any

from assure_core.result import CheckResult, failed_result, passed_result

_DASHES = re.compile(r"[\u2010\u2011\u2012\u2013\u2014\u2015\u2212]")
_SQUOTES = re.compile(r"[\u2018\u2019\u201a\u201b]")
_DQUOTES = re.compile(r"[\u201c\u201d\u201e\u201f]")


def _normalise(text: str) -> str:
    """NFKC + unify dash/quote variants + lowercase + collapse whitespace.

    Models often emit typographic characters (e.g. U+2011 non-breaking hyphen)
    where the source has ASCII; those must not count as a fabricated quote.
    """
    text = unicodedata.normalize("NFKC", text)
    text = _DASHES.sub("-", text)
    text = _SQUOTES.sub("'", text)
    text = _DQUOTES.sub('"', text)
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
