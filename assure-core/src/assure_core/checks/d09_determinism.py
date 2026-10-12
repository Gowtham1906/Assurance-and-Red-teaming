"""D09 - Determinism and regression diff (threshold gate).

Spec (plan §6):
    Implementation : run twice at temperature 0 or fixed seed; diff against
                     baseline on deterministic fields.
    Pass criterion : no unexplained diffs; approved-change list for free text.
    OWASP          : regression safety.

Compare two runs (or a run vs baseline) on deterministic fields and fail on any
diff not covered by an approved-change allowlist.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from assure_core.result import CheckResult


def check_determinism(
    run_a: Mapping[str, Any],
    run_b: Mapping[str, Any],
    approved_changes: Iterable[str] = (),
) -> CheckResult:
    """Fail on any deterministic-field diff not in ``approved_changes``."""
    raise NotImplementedError("D09 determinism check — implemented in Week 2 (W2-1)")
