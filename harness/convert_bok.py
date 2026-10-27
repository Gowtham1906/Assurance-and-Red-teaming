"""
harness/convert_bok.py  -  convert the real Capability 2 BoK golden JSONL into
our golden-case format.

Maps THEIR schema -> OUR expectations (only for checks we can run WITHOUT their
corpus; retrieval/citation/key-fact checks are recorded but deferred):

  their `language`           -> d07_language        (D07)
  their `expected_behavior`  -> d08_expected_behavior (D08, extended)
  behavior == refuse_injection -> d11_canaries (+ behavior)   (D11)

Corpus-dependent fields (expect_records, expect_entities, forbidden_evidence,
gold_key_facts, assert) are carried into a `deferred` block so nothing is lost;
they light up once the real corpus + judges (W3-2) are available.

RUN:
    assure-core\\.venv\\Scripts\\python.exe -m harness.convert_bok bok-golden.jsonl
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# A generic canary we assert must never appear in output for injection cases.
# (Their corpus would carry the real planted strings; this is the behaviour test.)
INJECTION_BEHAVIORS = {"refuse_injection"}


def convert_case(row: dict) -> dict:
    beh = row.get("expected_behavior", "answer")

    expectations: dict = {
        # D07: expected language (normalise ta-Latn -> our 'ta' script heuristic)
        "d07_language": "ta" if row.get("language") == "ta-Latn" else row.get("language", "en"),
        # D08: expected behaviour type (extended enum, see d08 adaptation)
        "d08_expected_behavior": beh,
    }

    # D11: injection cases must refuse and must not echo an injected payload.
    if beh in INJECTION_BEHAVIORS:
        expectations["d11_refuse_injection"] = True

    # Preserve corpus/judge-dependent expectations for later (not run yet).
    deferred = {}
    for k in ("expect_records", "expect_entities", "must_not_retrieve",
              "must_not_retrieve_scopes", "forbidden_evidence", "gold_key_facts",
              "assert", "expect_subtypes", "expect_retrieval_mode", "abstain_reason"):
        if k in row:
            deferred[k] = row[k]
    if deferred:
        expectations["_deferred"] = deferred

    return {
        "id": row["id"],
        "target": "bok",
        "input": row["question"],
        "expectations": expectations,
        "tags": [row.get("primary_category", ""), row.get("scope", ""),
                 row.get("difficulty", "")],
    }


def main(src: str, out: str = "assure-core/datasets/golden-bok-v1.json") -> None:
    rows = [json.loads(l) for l in Path(src).read_text(encoding="utf-8").splitlines() if l.strip()]
    cases = [convert_case(r) for r in rows]
    Path(out).write_text(json.dumps(cases, indent=2, ensure_ascii=False), encoding="utf-8")

    import collections
    beh = collections.Counter(r.get("expected_behavior") for r in rows)
    langs = collections.Counter(c["expectations"]["d07_language"] for c in cases)
    print(f"Converted {len(cases)} cases -> {out}")
    print(f"  behaviours: {dict(beh)}")
    print(f"  languages : {dict(langs)}")
    print(f"  corpus-dependent expectations preserved under '_deferred'")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "bok-golden.jsonl")
