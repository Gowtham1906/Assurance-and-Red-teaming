"""D03 - Banned strings and secrets (HARD gate).

Spec (plan §6):
    Implementation : denylist + secret regexes or detect-secrets.
    Pass criterion : zero matches.
    OWASP          : LLM02, LLM07 (system prompt leakage).

Fail if the output contains any denylisted string or anything matching a
secret pattern (API keys, tokens, private keys).
"""

from __future__ import annotations

from collections.abc import Iterable

from assure_core.result import CheckResult


def check_banned(output: str, denylist: Iterable[str] = ()) -> CheckResult:
    """Fail on any denylist hit or secret-pattern match in ``output``."""
    raise NotImplementedError("D03 banned/secrets check — implemented in Week 2 (W2-1)")
