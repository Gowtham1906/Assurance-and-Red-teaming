"""D08 - Refusal-reason typing (HARD gate).

Spec (plan §6):
    Implementation : output carries an enum reason; assert it matches case label.
    Pass criterion : 100% on refusal-labelled cases; false-refusal rate in budget.
    OWASP          : supports jailbreak/over-blocking measurement (plan §9).

On cases labelled as "should refuse", assert the output carries the correct
enum refusal reason. Also tracks false refusals (over-blocking) on benign cases.
"""

from __future__ import annotations

from assure_core.result import CheckResult


def check_refusal(output: dict, expected_reason: str | None) -> CheckResult:
    """Fail if refusal reason enum doesn't match the case's expected label."""
    raise NotImplementedError("D08 refusal-reason check — implemented in Week 2 (W2-1)")
