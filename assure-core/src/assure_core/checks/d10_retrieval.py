"""D10 - Retrieval hit (threshold gate).

Spec (plan §6):
    Implementation : gold document in top-k.
    Pass criterion : recall@k at or above baseline minus budget.
    OWASP          : LLM08, LLM04.
"""

from __future__ import annotations

from collections.abc import Sequence

from assure_core.result import CheckResult, GateType, failed_result, passed_result


def check_retrieval(retrieved_ids: Sequence[str], gold_id: str, k: int) -> CheckResult:
    """Fail if gold_id is not within the top-k of retrieved_ids."""
    if k <= 0:
        return failed_result("D10", "k must be positive", k=k)
    topk = list(retrieved_ids)[:k]
    if gold_id in topk:
        return passed_result("D10", rank=topk.index(gold_id) + 1, k=k)
    return failed_result(
        "D10", f"gold doc '{gold_id}' not in top-{k}",
        gate=GateType.SOFT, gold_id=gold_id, topk=topk,
    )
