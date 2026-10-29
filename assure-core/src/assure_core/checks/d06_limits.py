"""D06 - Latency, token and cost limits (threshold gate).

Spec (plan §6):
    Implementation : read from trace spans; p95 and hard maximum.
    Pass criterion : p95 within budget; max within cap.
    OWASP          : LLM10 (ASI08 is Cascading Failures, not cost - see cheat sheet 2).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from assure_core.result import CheckResult, GateType, failed_result, passed_result


def _percentile(values: list[float], pct: float) -> float:
    """Nearest-rank percentile (pct in [0,100])."""
    if not values:
        return 0.0
    s = sorted(values)
    k = max(0, min(len(s) - 1, int(round((pct / 100.0) * (len(s) - 1)))))
    return s[k]


def check_limits(
    spans: Sequence[Mapping[str, Any]],
    budget: Mapping[str, float],
) -> CheckResult:
    """Fail if p95 exceeds budget or any value exceeds the hard cap, per metric.

    budget keys: "<metric>_p95" and/or "<metric>_max", e.g.
        {"latency_ms_p95": 2000, "latency_ms_max": 5000, "cost_usd_max": 0.05}
    Each span is a dict of metric -> value.
    """
    violations: list[dict] = []
    # collect metric values across spans
    metrics: dict[str, list[float]] = {}
    for span in spans:
        for k, v in span.items():
            if isinstance(v, (int, float)):
                metrics.setdefault(k, []).append(float(v))

    for key, limit in budget.items():
        if key.endswith("_p95"):
            metric = key[:-4]
            if metric in metrics:
                val = _percentile(metrics[metric], 95)
                if val > limit:
                    violations.append({"metric": metric, "stat": "p95", "value": val, "limit": limit})
        elif key.endswith("_max"):
            metric = key[:-4]
            if metric in metrics:
                val = max(metrics[metric])
                if val > limit:
                    violations.append({"metric": metric, "stat": "max", "value": val, "limit": limit})

    if violations:
        return failed_result(
            "D06", f"{len(violations)} budget violation(s)",
            gate=GateType.SOFT, violations=violations,
        )
    return passed_result("D06")
