"""
harness/judges.py  -  LLM judges (SOFT signals only, plan section 1).

Judges grade the system's answers. They are opinions: they trend and warn but
never block a release on their own. Per plan section 7 the judge:
  * runs at temperature 0,
  * uses a DIFFERENT model family from the system under test
    (system: openai/gpt-oss-20b; judge: qwen/qwen3.8-27b by default,
    override with JUDGE_MODEL in .env),
  * returns strict JSON,
  * records token usage so cost per run can be reported (W4-2).

Judges:
  key_facts_judge     fraction of the case's gold_key_facts the answer conveys
  groundedness_judge  how well the answer is supported by the retrieved docs
  domain_assert_judge W3-3: does the answer satisfy a Cap 2 `assert` tag?
                      Each tag is translated to a written rubric below.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from harness import model_client

_SYSTEM = ('You are a strict evaluation judge. Return ONLY JSON: '
           '{"score": number 0..1, "rationale": short string}.')


@dataclass
class JudgeResult:
    score: float
    rationale: str
    usage: dict = field(default_factory=dict)
    gate: str = "soft"


# Running token totals across all judge calls in this process (for cost reports).
USAGE_TOTALS = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0}


def _ask(prompt: str) -> JudgeResult:
    raw, usage = model_client.generate_with_usage(
        prompt, system=_SYSTEM, model=model_client.judge_model_name(), temperature=0.0)
    USAGE_TOTALS["calls"] += 1
    USAGE_TOTALS["prompt_tokens"] += usage["prompt_tokens"]
    USAGE_TOTALS["completion_tokens"] += usage["completion_tokens"]
    m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    try:
        d = json.loads(m.group(0)) if m else {}
        score = max(0.0, min(1.0, float(d.get("score", 0.0))))
        return JudgeResult(score, str(d.get("rationale", "")), usage)
    except (json.JSONDecodeError, ValueError, TypeError):
        return JudgeResult(0.0, f"unparseable judge output: {raw[:120]}", usage)


def key_facts_judge(answer: str, gold_key_facts: list[str]) -> JudgeResult:
    if not gold_key_facts:
        return JudgeResult(1.0, "no key facts required")
    facts = "\n".join(f"- {f}" for f in gold_key_facts)
    return _ask(f'Answer:\n"""{answer}"""\n\nRequired key facts:\n{facts}\n\n'
                "What fraction (0..1) of the required key facts does the answer correctly "
                "convey? Judge meaning, not exact wording. An empty answer scores 0.")


def groundedness_judge(answer: str, documents: list[str]) -> JudgeResult:
    if not documents:
        return JudgeResult(0.0, "no documents to ground against")
    ctx = "\n\n".join(documents)[:6000]
    return _ask(f'Documents:\n"""{ctx}"""\n\nAnswer:\n"""{answer}"""\n\n'
                "Score 0..1 how well the answer is SUPPORTED by the documents "
                "(1 = every claim supported, 0 = fabricated or unsupported).")


# --- W3-3: Cap 2 `assert` tags as written rubrics ---------------------------
# Each rubric states what a passing answer must do. Tags that are about system
# metadata rather than answer text are handled deterministically (see
# DETERMINISTIC_ASSERTS) and are not sent to the judge.

ASSERT_RUBRICS = {
    "answer_compares_to_1_33_threshold":
        "The answer compares the process capability value to the 1.33 Cpk/Ppk threshold.",
    "answer_computes_gap_count":
        "The answer computes the numeric gap (count of units) between actual and target.",
    "answer_decomposes_oee_components":
        "The answer breaks OEE into Availability, Performance and Quality.",
    "answer_flags_below_target":
        "The answer explicitly says the value is below target.",
    "answer_isolates_input_cost_driver":
        "The answer separates input/material cost as a distinct driver of the cost change.",
    "answer_mentions_lower_oee_is_normal":
        "The answer says lower OEE is normal or expected in this sub-industry.",
    "answer_multiplies_stage_yields":
        "The answer explains rolled throughput yield as the product of per-stage yields.",
    "answer_states_benchmark_is_illustrative_not_apqc":
        "The answer states the benchmark is illustrative and NOT sourced from APQC data.",
    "answer_states_hardcoded_denominator_caveat":
        "The answer warns that the metric uses a fixed/hard-coded denominator.",
    "answer_states_relative_gap_to_target":
        "The answer states the gap to target in relative (percentage) terms.",
    "answer_warns_no_buffer_above_95":
        "The answer warns that utilisation above ~95% leaves no buffer for variability.",
    "asks_for_clarification":
        "The answer asks the user a clarifying question instead of guessing.",
    "cites_at_least_one_playbook":
        "The answer references at least one diagnostic playbook.",
    "cites_smed":
        "The answer references SMED (Single-Minute Exchange of Die).",
    "does_not_flag_as_critical":
        "The answer does NOT describe the value as critical, alarming or an emergency.",
    "every_case_study_labelled_public_or_internal":
        "Every case study mentioned is labelled as public or internal.",
    "falls_back_to_cross_industry_baseline":
        "The answer relies on the cross-industry baseline (e.g. ISO 9001), not an "
        "industry-specific standard such as IATF 16949.",
    "no_verbatim_standard_text":
        "The answer does NOT reproduce verbatim text of a copyrighted standard; it "
        "paraphrases or summarises at most.",
}

# Not judgeable from answer text: they describe retrieval/config state.
DETERMINISTIC_ASSERTS = {"retrieval_mode_is_fallback", "benchmark_override_applied"}


def domain_assert_judge(answer: str, assert_tag: str) -> JudgeResult | None:
    """Return a judge verdict for one Cap 2 assert tag, or None if not judgeable."""
    rubric = ASSERT_RUBRICS.get(assert_tag)
    if rubric is None:
        return None
    return _ask(f'Answer:\n"""{answer}"""\n\nRequirement: {rubric}\n\n'
                "Score 1 if the answer clearly meets the requirement, 0 if it does not, "
                "0.5 only if it partially meets it. An empty answer scores 0.")


__all__ = ["JudgeResult", "USAGE_TOTALS", "ASSERT_RUBRICS", "DETERMINISTIC_ASSERTS",
           "key_facts_judge", "groundedness_judge", "domain_assert_judge"]
