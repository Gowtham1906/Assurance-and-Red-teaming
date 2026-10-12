"""Shared result types for all deterministic checks.

Every check returns a ``CheckResult``. These types are deliberately plain
(no MLflow) so checks run under bare ``pytest`` and are easy for the Week 3
MLflow adapter to translate into scorers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Status(str, Enum):
    """Outcome of a single check on a single case."""

    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"  # the check itself blew up (treated as fail: fail-closed)


class GateType(str, Enum):
    """Whether a check is a hard release gate or a soft signal (plan §1)."""

    HARD = "hard"  # deterministic; a failure blocks release
    SOFT = "soft"  # trend/warn only


@dataclass(frozen=True)
class CheckResult:
    """Result of one check against one case.

    Attributes:
        check_id: e.g. "D02".
        status: pass / fail / error.
        gate: hard or soft.
        message: short human-readable reason.
        evidence: structured detail for the report/finding (spans, counts, etc.).
    """

    check_id: str
    status: Status
    gate: GateType = GateType.HARD
    message: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status is Status.PASS


def passed_result(check_id: str, **evidence: Any) -> CheckResult:
    return CheckResult(check_id=check_id, status=Status.PASS, evidence=evidence)


def failed_result(check_id: str, message: str, **evidence: Any) -> CheckResult:
    return CheckResult(
        check_id=check_id, status=Status.FAIL, message=message, evidence=evidence
    )
