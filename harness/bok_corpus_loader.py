"""
harness/bok_corpus_loader.py  -  load the REAL Capability 2 BoK corpus.

Turns the 4 governed document types (KPI cards, playbooks, standards, case
studies) into retrievable documents keyed by their REAL ids, so D10 retrieval
and D04 citations can run against the actual corpus the golden set references.

Each document:
    {"doc_id", "type", "text", "scopes"}   # scopes = applicable sub-industries

(The root-cause-tag-reconciliation file is metadata, not a retrievable doc, so
it is loaded separately for reference, not indexed.)
"""

from __future__ import annotations

import json
from pathlib import Path

_DIR = Path(__file__).resolve().parent / "bok_corpus"


def _read(name: str):
    return json.loads((_DIR / name).read_text(encoding="utf-8"))


def load_documents() -> dict[str, dict]:
    """Return {doc_id: {doc_id, type, text, scopes}} for all retrievable docs."""
    docs: dict[str, dict] = {}

    # KPI cards
    for k in _read("bok_kpi_cards.json"):
        did = k["kpi_id"]
        text = (f"KPI: {k.get('kpi_name','')}\n"
                f"Aliases: {', '.join(k.get('aliases', []))}\n"
                f"Definition: {k.get('definition','')}\n"
                f"Formula: {k.get('formula','')}\n"
                f"Unit: {k.get('unit','')}\n"
                f"Benchmark: {k.get('benchmark_note','')}")
        docs[did] = {"doc_id": did, "type": "kpi_card", "text": text,
                     "scopes": k.get("applicable_sub_industries", [])}

    # Playbooks
    for p in _read("bok_playbooks.json"):
        did = p["playbook_id"]
        actions = p.get("recommended_actions", [])
        # recommended_actions are dicts like {"root_cause_tag", "action"}
        action_texts = [a.get("action", "") if isinstance(a, dict) else str(a)
                        for a in actions]
        text = (f"Playbook: {did}\n"
                f"Symptom: {p.get('symptom_description','')}\n"
                f"Framework: {p.get('root_cause_framework','')}\n"
                f"Diagnostic steps: {'; '.join(p.get('diagnostic_steps', []))}\n"
                f"Recommended actions: {'; '.join(action_texts)}")
        docs[did] = {"doc_id": did, "type": "playbook", "text": text,
                     "scopes": p.get("applicable_sub_industries", [])}

    # Standards
    for s in _read("bok_standards.json"):
        did = s["standard_id"]
        text = (f"Standard: {s.get('name','')} ({did})\n"
                f"Summary: {s.get('structural_summary','')}\n"
                f"Governs KPIs: {', '.join(s.get('governs_kpi_ids', []))}\n"
                f"Licence: {s.get('license_note','')}")
        docs[did] = {"doc_id": did, "type": "standard", "text": text,
                     "scopes": s.get("applicable_sub_industries", [])}

    # Case studies
    for c in _read("bok_case_studies.json"):
        did = c["case_id"]
        text = (f"Case study {did} ({c.get('visibility','')}):\n"
                f"Situation: {c.get('situation','')}\n"
                f"Diagnosis: {c.get('diagnosis','')}\n"
                f"Action: {c.get('action_taken','')}\n"
                f"Outcome: {c.get('outcome','')}")
        docs[did] = {"doc_id": did, "type": "case_study", "text": text,
                     "scopes": [c.get("sub_industry", "")]}

    return docs


def corpus_summary() -> dict:
    docs = load_documents()
    from collections import Counter
    return {"total": len(docs), "by_type": dict(Counter(d["type"] for d in docs.values()))}


if __name__ == "__main__":
    s = corpus_summary()
    print("Real BoK corpus loaded:", s)
    docs = load_documents()
    for probe in ("oee", "scrap_rate", "IATF-16949", "scrap_or_copq_spike"):
        print(f"  '{probe}' present:", probe in docs)
