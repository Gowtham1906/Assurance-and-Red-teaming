"""D07 - Language check (SOFT/threshold gate).

Spec (plan §6):
    Implementation : langdetect, fastText or lingua vs expected language.
    Pass criterion : >= 99% on expected language.
    OWASP          : supports multilingual cases (plan §9 row 12).

Detect the output language and fail if it is not the expected language above
the required rate.
"""

from __future__ import annotations

from assure_core.result import CheckResult


def check_language(output: str, expected_lang: str) -> CheckResult:
    """Fail if detected language of ``output`` != ``expected_lang``."""
    raise NotImplementedError("D07 language check — implemented in Week 2 (W2-1)")
