"""D07 - Language check (threshold gate).

Spec (plan §6):
    Implementation : langdetect, fastText or lingua against expected language.
    Pass criterion : >= 99% on expected language.
    OWASP          : multilingual cases (plan §9 row 12).

NOTE: to keep assure-core dependency-free, this uses a lightweight script-based
heuristic (Latin / Tamil / Devanagari-Hindi). A production deployment can swap in
``lingua`` or ``fastText`` behind the same function signature.
"""

from __future__ import annotations

from assure_core.result import CheckResult, GateType, failed_result, passed_result


def _detect_lang(text: str) -> str:
    """Very small script-based detector: returns 'ta', 'hi', 'en', or 'unknown'."""
    tamil = sum(1 for ch in text if "\u0b80" <= ch <= "\u0bff")
    devanagari = sum(1 for ch in text if "\u0900" <= ch <= "\u097f")
    latin = sum(1 for ch in text if ("a" <= ch.lower() <= "z"))
    counts = {"ta": tamil, "hi": devanagari, "en": latin}
    best = max(counts, key=counts.get)
    return best if counts[best] > 0 else "unknown"


def check_language(output: str, expected_lang: str) -> CheckResult:
    """Fail if the detected language of output != expected_lang."""
    detected = _detect_lang(output)
    if detected != expected_lang:
        return failed_result(
            "D07", f"expected '{expected_lang}', detected '{detected}'",
            gate=GateType.SOFT, detected=detected, expected=expected_lang,
        )
    return passed_result("D07", detected=detected)
