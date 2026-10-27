"""Tests for the release gate (W3-4)."""

from __future__ import annotations

from assure_core.gate import evaluate_gate

POLICY = {
    "confidence": 0.95,
    "fail_closed": True,
    "metrics": {
        "D02_pii": {"gate": "hard", "floor": 1.00, "regression_budget": 0.00},
        "D10_retrieval": {"gate": "soft", "floor": 0.80, "regression_budget": 0.05},
        "key_facts": {"gate": "soft", "floor": 0.70, "regression_budget": 0.02},
    },
}


def test_all_pass():
    # perfect PII, good retrieval + judge -> PASS
    metrics = {"D02_pii": (100, 100), "D10_retrieval": (95, 100), "key_facts": (90, 100)}
    r = evaluate_gate(metrics, POLICY)
    assert r.decision == "PASS"


def test_hard_fail_blocks():
    # one PII leak -> hard metric below floor -> FAIL
    metrics = {"D02_pii": (99, 100), "D10_retrieval": (95, 100)}
    r = evaluate_gate(metrics, POLICY)
    assert r.decision == "FAIL"
    assert any(o.name == "D02_pii" and o.verdict == "fail" for o in r.outcomes)


def test_soft_below_floor_is_review_not_fail():
    # retrieval below floor but it's SOFT -> REVIEW, not FAIL
    metrics = {"D02_pii": (100, 100), "D10_retrieval": (50, 100)}
    r = evaluate_gate(metrics, POLICY)
    assert r.decision == "REVIEW"


def test_fail_closed_on_missing_hard_metric():
    # D02 (hard) not measured -> fail-closed -> FAIL
    metrics = {"D10_retrieval": (95, 100)}
    r = evaluate_gate(metrics, POLICY)
    assert r.decision == "FAIL"


def test_regression_vs_baseline():
    # retrieval still above floor but dropped a lot vs baseline -> REVIEW (soft)
    metrics = {"D02_pii": (100, 100), "D10_retrieval": (82, 100)}
    baseline = {"D10_retrieval": 0.95}
    r = evaluate_gate(metrics, POLICY, baseline=baseline)
    assert r.decision == "REVIEW"
    assert any(o.name == "D10_retrieval" and "regressed" in o.reason for o in r.outcomes)


def test_perfect_hard_metric_passes_floor_1():
    # 100/100 with floor 1.00 must PASS (point estimate meets the floor), even
    # though the Wilson lower bound (0.963) is < 1.0. A perfect run isn't punished.
    metrics = {"D02_pii": (100, 100)}
    policy = {"confidence": 0.95, "fail_closed": False,
              "metrics": {"D02_pii": {"gate": "hard", "floor": 1.00, "regression_budget": 0.0}}}
    r = evaluate_gate(metrics, policy)
    assert r.decision == "PASS"


def test_genuine_shortfall_fails_on_lower_bound():
    # small sample below floor: 7/10 with floor 0.9 -> point and lower bound below -> FAIL
    metrics = {"D02_pii": (7, 10)}
    policy = {"confidence": 0.95, "fail_closed": False,
              "metrics": {"D02_pii": {"gate": "hard", "floor": 0.90, "regression_budget": 0.0}}}
    r = evaluate_gate(metrics, policy)
    assert r.decision == "FAIL"
