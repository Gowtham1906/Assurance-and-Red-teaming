"""D05 - Tool-call allowlist (HARD gate).

Spec (plan §6):
    Implementation : compare trace tool names and argument schemas to the policy
                     file; check scope and bounds.
    Pass criterion : zero calls outside the allowlist; zero forbidden sequences.
    OWASP          : LLM06 (excessive agency) · ASI02, ASI05.

Inspect the trace of tool calls an agent made and fail on any call not in the
policy allowlist, any out-of-schema arguments, or any forbidden call sequence.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from assure_core.result import CheckResult


def check_tool_allowlist(
    tool_calls: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any],
) -> CheckResult:
    """Fail on any tool call outside ``policy`` (name, args, scope, sequence)."""
    raise NotImplementedError("D05 tool-allowlist check — implemented in Week 2 (W2-1)")
