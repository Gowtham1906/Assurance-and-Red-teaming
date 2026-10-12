"""D04 - Citation span validity (HARD gate).

Spec (plan §6):
    Implementation : cited document IDs exist in the retrieved set; quoted span
                     is a normalised substring of that chunk, or offsets match.
    Pass criterion : 100% of citations resolve; unsupported-citation rate 0.
    OWASP          : LLM09 (misinformation), LLM08 (vector/embedding).

Verify every citation points to a retrieved document and the quoted text really
appears in that document.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from assure_core.result import CheckResult


def check_citations(
    citations: Sequence[Mapping[str, Any]],
    retrieved: Mapping[str, str],
) -> CheckResult:
    """Fail if any citation's doc id is missing or its span isn't in the doc."""
    raise NotImplementedError("D04 citation check — implemented in Week 2 (W2-1)")
