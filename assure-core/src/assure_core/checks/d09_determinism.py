"""D09 - Determinism and regression diff (threshold gate).

Spec (plan §6):
    Implementation : run twice at temperature 0 / fixed seed; diff against
                     baseline on deterministic fields.
    Pass criterion : no unexplained diffs; approved-change list for free text.
    OWASP          : regression safety.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from assure_core.result import CheckResult, GateType, failed_result, passed_result


def check_determinism(
    run_a: Mapping[str, Any],
    run_b: Mapping[str, Any],
    approved_changes: Iterable[str] = (),
) -> CheckResult:
    """Fail on any deterministic-field diff not covered by approved_changes.

    Compares the union of keys in run_a and run_b. Fields listed in
    approved_changes are allowed to differ (e.g. free-text 'answer').
    """
    approved = set(approved_changes)
    diffs: list[dict] = []

    for key in set(run_a) | set(run_b):
        if key in approved:
            continue
        a = run_a.get(key, "<missing>")
        b = run_b.get(key, "<missing>")
        if a != b:
            diffs.append({"field": key, "a": a, "b": b})

    if diffs:
        return failed_result("D09", f"{len(diffs)} unexplained diff(s)",
                             gate=GateType.SOFT, diffs=diffs)
    return passed_result("D09")
