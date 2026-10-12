"""D06 - Latency, token and cost limits (SOFT/threshold gate).

Spec (plan §6):
    Implementation : read from trace spans; p95 and hard maximum.
    Pass criterion : p95 within budget; max within cap.
    OWASP          : LLM10 (unbounded consumption) · ASI08.

Read latency / token / cost from the trace and fail if p95 exceeds the budget
or any single run exceeds the hard cap.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from assure_core.result import CheckResult


def check_limits(
    spans: Sequence[Mapping[str, Any]],
    budget: Mapping[str, float],
) -> CheckResult:
    """Fail if p95 over budget or max over the hard cap for latency/tokens/cost."""
    raise NotImplementedError("D06 limits check — implemented in Week 2 (W2-1)")
