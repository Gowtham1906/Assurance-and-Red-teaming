"""D01 - Schema and format validity (HARD gate).

Spec (plan §6):
    Implementation : pydantic or JSON Schema on output and tool-call arguments.
    Pass criterion : 100% valid.
    OWASP          : LLM05 (improper output handling), LLM01 (agent args).

Validate that the model output and any tool-call arguments conform to the
expected schema. Any invalid structure fails.
"""

from __future__ import annotations

from typing import Any

from assure_core.result import CheckResult


def check_schema(output: Any, schema: Any) -> CheckResult:
    """Validate ``output`` against ``schema`` (pydantic model or JSON Schema).

    Returns a passing CheckResult only if the output fully validates.
    """
    raise NotImplementedError("D01 schema check — implemented in Week 2 (W2-1)")
