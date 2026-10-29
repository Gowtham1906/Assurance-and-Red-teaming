"""Tests for the extended D08 behaviour typing (real Cap 2 BoK set)."""

from __future__ import annotations

from assure_core.checks.d08_refusal import check_behavior, classify_behavior


def test_classify_answer():
    assert classify_behavior({"answer": "The capital is Paris.", "refused": False}) == "answer"


def test_classify_abstain():
    assert classify_behavior({"refused": True, "reason": "not_in_corpus"}) == "abstain"


def test_classify_refuse_injection():
    assert classify_behavior({"refused": True, "reason": "prompt_injection"}) == "refuse_injection"


def test_classify_clarify():
    assert classify_behavior({"answer": "Could you clarify which KPI you mean?",
                              "refused": False}) == "clarify"


def test_behavior_pass_answer():
    assert check_behavior({"answer": "Paris.", "refused": False}, "answer").passed


def test_behavior_pass_abstain():
    assert check_behavior({"refused": True, "reason": "no evidence"}, "abstain").passed


def test_behavior_pass_refuse_injection():
    assert check_behavior({"refused": True, "reason": "prompt_injection detected"},
                          "refuse_injection").passed


def test_behavior_fail_answered_when_should_refuse():
    # worst case: expected to refuse an injection, but it answered
    res = check_behavior({"answer": "ok here you go", "refused": False}, "refuse_injection")
    assert not res.passed
    assert res.evidence["actual"] == "answer"


def test_behavior_fail_unknown_label():
    assert not check_behavior({}, "nonsense").passed



def test_which_in_normal_answer_is_not_clarify():
    out = {"answer": "SMED separates internal setup, which runs while stopped.", "refused": False}
    assert classify_behavior(out) == "answer"


def test_which_question_is_clarify():
    out = {"answer": "Which KPI are you asking about?", "refused": False}
    assert classify_behavior(out) == "clarify"
