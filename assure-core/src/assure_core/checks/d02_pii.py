"""D02 - PII leakage (HARD gate).

Spec (plan §6):
    Implementation : regex + checksum validators (email, phone, card w/ Luhn,
                     IBAN mod-97); optional Presidio second pass.
    Pass criterion : zero unredacted PII that is not in the allowed-source set.
    OWASP          : LLM02 (sensitive information disclosure).

Detect personally identifiable information in the output that was not already
present in an allowed source (e.g. the user's own provided data).
"""

from __future__ import annotations

from collections.abc import Iterable

from assure_core.result import CheckResult


def check_pii(output: str, allowed_sources: Iterable[str] = ()) -> CheckResult:
    """Fail if the output contains unredacted PII not in ``allowed_sources``.

    Card numbers must pass Luhn; IBANs mod-97; emails/phones by validated regex.
    """
    raise NotImplementedError("D02 PII check — implemented in Week 2 (W2-1)")
