"""Release gate (W3-4): decide PASS / FAIL / REVIEW from metrics vs policy + baseline.

Uses the stats module: gates on the Wilson LOWER BOUND of each pass-rate, not
the point estimate (plan section 7). Pure Python - the policy is passed in as a
dict (the harness loads the YAML), so assure-core stays dependency-light.

Decision rules (plan section 8):
  * HARD metric below its floor (lower bound)      -> FAIL (blocks release)
  * HARD metric regressed beyond budget vs baseline -> FAIL
  * SOFT metric below floor / regressed            -> REVIEW (warn, don't block)
  * missing required metric (fail_closed)          -> FAIL
  * otherwise                                       -> PASS
"""

from __future__ import annotations

from dataclasses import dataclass, field

from assure_core.stats import wilson_interval


@dataclass
class MetricOutcome:
    name: str
    gate: str            # hard | soft
    passed: int
    total: int
    point: float
    lower_bound: float
    floor: float
    baseline_point: float | None
    verdict: str         # pass | fail | review
    reason: str


@dataclass
class GateResult:
    decision: str                 # PASS | FAIL | REVIEW
    outcomes: list[MetricOutcome] = field(default_factory=list)

    @property
    def summary(self) -> str:
        fails = [o.name for o in self.outcomes if o.verdict == "fail"]
        reviews = [o.name for o in self.outcomes if o.verdict == "review"]
        parts = [f"decision={self.decision}"]
        if fails:
            parts.append(f"FAIL: {', '.join(fails)}")
        if reviews:
            parts.append(f"REVIEW: {', '.join(reviews)}")
        return " | ".join(parts)


def evaluate_gate(
    run_metrics: dict[str, tuple[int, int]],   # name -> (passed, total)
    policy: dict,
    baseline: dict[str, float] | None = None,  # name -> baseline point pass-rate
) -> GateResult:
    """Apply the policy to a run's metrics and return the overall gate decision."""
    confidence = policy.get("confidence", 0.95)
    fail_closed = policy.get("fail_closed", True)
    metrics_policy = policy.get("metrics", {})
    baseline = baseline or {}

    outcomes: list[MetricOutcome] = []
    any_fail = False
    any_review = False

    for name, spec in metrics_policy.items():
        gate = spec.get("gate", "soft")
        floor = float(spec.get("floor", 0.0))
        budget = float(spec.get("regression_budget", 0.0))

        if name not in run_metrics:
            # metric not measured in this run - skip unless fail_closed demands it.
            # We only fail-closed on HARD metrics (soft ones may legitimately be absent).
            if fail_closed and gate == "hard":
                outcomes.append(MetricOutcome(name, gate, 0, 0, 0.0, 0.0, floor,
                                              baseline.get(name), "fail",
                                              "required hard metric missing (fail-closed)"))
                any_fail = True
            continue

        passed, total = run_metrics[name]
        point = passed / total if total else 0.0
        low, _ = wilson_interval(passed, total, confidence) if total else (0.0, 1.0)
        base = baseline.get(name)

        verdict, reason = "pass", "within policy"
        # Floor check: a run whose POINT estimate already meets the floor passes.
        # Otherwise we gate on the Wilson LOWER BOUND (plan section 7) to require
        # statistical confidence the floor is genuinely met.
        if point < floor and low < floor:
            verdict = "fail" if gate == "hard" else "review"
            reason = f"point {point:.3f} / lower bound {low:.3f} < floor {floor:.2f}"
        # regression check vs baseline point estimate
        elif base is not None and (base - point) > budget:
            verdict = "fail" if gate == "hard" else "review"
            reason = f"regressed {base - point:.3f} > budget {budget:.2f} vs baseline"

        if verdict == "fail":
            any_fail = True
        elif verdict == "review":
            any_review = True

        outcomes.append(MetricOutcome(name, gate, passed, total, point, low, floor,
                                      base, verdict, reason))

    decision = "FAIL" if any_fail else ("REVIEW" if any_review else "PASS")
    return GateResult(decision=decision, outcomes=outcomes)


__all__ = ["evaluate_gate", "GateResult", "MetricOutcome"]
