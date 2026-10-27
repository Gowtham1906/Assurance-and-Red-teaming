"""
harness/judges.py  -  W3-2 LLM judges (SOFT signals only).

A judge is a model grading another model's answer. Unlike the deterministic
D01-D11 checks (fixed rules = HARD gate), judges are opinions: they WARN and
TREND, they NEVER block a release on their own (plan §1).

Judges here (both map to the real BoK golden set):
  * key_facts_judge  - does the answer contain the case's gold_key_facts?
  * groundedness_judge - is the answer supported by the retrieved documents
                         (no fabrication)?

Each returns a float score in [0,1] + a short rationale. To reduce judge
variance (plan §7) the judge runs at temperature 0 and returns strict JSON.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from harness import model_client


@dataclass
class JudgeResult:
    score: float          # 0.0 - 1.0
    rationale: str
    gate: str = "soft"    # judges are ALWAYS soft (never block alone)


def _ask_json(prompt: str) -> dict:
    raw = model_client.generate(
        prompt,
        system=("You are a strict evaluation judge. Return ONLY JSON: "
                "{\"score\": number 0..1, \"rationale\": short string}."),
        temperature=0.0,
    )
    cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        d = json.loads(cleaned)
        return {"score": float(d.get("score", 0.0)), "rationale": str(d.get("rationale", ""))}
    except (json.JSONDecodeError, ValueError, TypeError):
        return {"score": 0.0, "rationale": f"unparseable judge output: {raw[:120]}"}


def key_facts_judge(answer: str, gold_key_facts: list[str]) -> JudgeResult:
    """Score = fraction of the gold key facts the answer conveys (judge's opinion)."""
    if not gold_key_facts:
        return JudgeResult(1.0, "no key facts required")
    facts = "\n".join(f"- {f}" for f in gold_key_facts)
    prompt = (
        f"Answer:\n\"\"\"{answer}\"\"\"\n\n"
        f"Required key facts:\n{facts}\n\n"
        "What fraction (0..1) of the required key facts does the answer correctly "
        "convey? Judge meaning, not exact wording."
    )
    r = _ask_json(prompt)
    return JudgeResult(max(0.0, min(1.0, r["score"])), r["rationale"])


def groundedness_judge(answer: str, documents: list[str]) -> JudgeResult:
    """Score = how well the answer is supported by the provided documents."""
    if not documents:
        return JudgeResult(0.0, "no documents to ground against")
    ctx = "\n\n".join(documents)[:6000]
    prompt = (
        f"Documents:\n\"\"\"{ctx}\"\"\"\n\n"
        f"Answer:\n\"\"\"{answer}\"\"\"\n\n"
        "Score 0..1 how well the answer is SUPPORTED by the documents "
        "(1 = fully grounded, 0 = fabricated / unsupported)."
    )
    r = _ask_json(prompt)
    return JudgeResult(max(0.0, min(1.0, r["score"])), r["rationale"])


__all__ = ["JudgeResult", "key_facts_judge", "groundedness_judge"]
