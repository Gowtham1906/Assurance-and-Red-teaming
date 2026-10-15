"""Week 1 smoke tests: the package imports and the result contract works.

Check implementations land in Week 2 (W2-1); here we only prove the skeleton
is wired up correctly.
"""

from __future__ import annotations

import importlib

import pytest

from assure_core import CheckResult, GateType, Status, failed_result, passed_result
from assure_core.checks import CHECK_IDS


def test_package_imports():
    assert len(CHECK_IDS) == 11
    assert CHECK_IDS[0] == "D01"
    assert CHECK_IDS[-1] == "D11"


def test_result_contract():
    ok = passed_result("D01", valid=True)
    bad = failed_result("D02", "leaked email", value="a@b.com")
    assert ok.passed is True
    assert ok.status is Status.PASS
    assert ok.gate is GateType.HARD
    assert bad.passed is False
    assert bad.message == "leaked email"
    assert bad.evidence["value"] == "a@b.com"


MODULES = [
    ("d01_schema", "check_schema"),
    ("d02_pii", "check_pii"),
    ("d03_banned", "check_banned"),
    ("d04_citations", "check_citations"),
    ("d05_tool_allowlist", "check_tool_allowlist"),
    ("d06_limits", "check_limits"),
    ("d07_language", "check_language"),
    ("d08_refusal", "check_refusal"),
    ("d09_determinism", "check_determinism"),
    ("d10_retrieval", "check_retrieval"),
    ("d11_canary", "check_canary"),
]


@pytest.mark.parametrize("module_name, func_name", MODULES)
def test_every_check_stub_exists(module_name, func_name):
    """Each D01-D11 module exposes its function (a stub for now)."""
    mod = importlib.import_module(f"assure_core.checks.{module_name}")
    assert hasattr(mod, func_name), f"{module_name}.{func_name} missing"


def test_checks_are_implemented():
    """Week 2: stubs are now real; a clean canary input passes."""
    from assure_core.checks import d11_canary

    result = d11_canary.check_canary("a clean answer", [], ["CANARY-123"])
    assert result.passed
