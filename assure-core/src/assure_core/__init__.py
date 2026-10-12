"""assure-core: deterministic assurance checks (D01-D11). No MLflow dependency."""

from __future__ import annotations

from assure_core.result import (
    CheckResult,
    GateType,
    Status,
    failed_result,
    passed_result,
)

__version__ = "0.1.0"

__all__ = [
    "CheckResult",
    "GateType",
    "Status",
    "failed_result",
    "passed_result",
    "__version__",
]
