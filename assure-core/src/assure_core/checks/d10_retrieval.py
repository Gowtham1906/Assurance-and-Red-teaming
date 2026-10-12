"""D10 - Retrieval hit (SOFT/threshold gate).

Spec (plan §6):
    Implementation : gold document in top-k.
    Pass criterion : recall@k at or above baseline minus budget.
    OWASP          : LLM08 (vector/embedding), LLM04 (poisoning).

Check that the known-gold document appears in the top-k retrieved set; track
recall@k against baseline.
"""

from __future__ import annotations

from collections.abc import Sequence

from assure_core.result import CheckResult


def check_retrieval(retrieved_ids: Sequence[str], gold_id: str, k: int) -> CheckResult:
    """Fail if ``gold_id`` is not within the top-``k`` of ``retrieved_ids``."""
    raise NotImplementedError("D10 retrieval check — implemented in Week 2 (W2-1)")
