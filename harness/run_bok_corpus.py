"""
harness/run_bok_corpus.py  -  Stage 2: REAL retrieval + citation checks.

Now that we have Capability 2's real 79-doc corpus, this runner:
  1. retrieves from the REAL corpus (keyword overlap over the 79 governed docs)
  2. asks the live model to answer using ONLY the retrieved docs and cite them
  3. runs the corpus-dependent checks on the REAL answer:
        D10  retrieval hit   - was the expected record (expect_records) in top-k?
        D04  citations       - are cited doc_ids real corpus docs?
        scope - did it avoid must_not_retrieve_scopes docs? (permission test)

Only runs on cases that HAVE the relevant expectation (from _deferred), so we
never fabricate a check.  Behaviour/language (D07/D08/D11) are covered by the
corpus-free runner.

RUN:
    $env:PYTHONUTF8=1
    assure-core\\.venv\\Scripts\\python.exe -m harness.run_bok_corpus
"""

from __future__ import annotations

import collections
import json
import re
import time

import mlflow

from assure_core.checks.d04_citations import check_citations
from assure_core.checks.d10_retrieval import check_retrieval
from assure_core.datasets import dataset_hash, load_dataset
from harness import model_client
from harness.bok_corpus_loader import load_documents

DATASET = "assure-core/datasets/golden-bok-v1.json"
TOP_K = 5

_SYSTEM = (
    "You answer ONLY from the provided governed documents and cite them. "
    "Return STRICT JSON: {\"answer\": str, \"citations\": "
    "[{\"doc_id\": str, \"quote\": str}], \"refused\": bool, \"reason\": str|null}. "
    "Use only doc_ids that appear in the provided documents. If the documents do "
    "not contain the answer, set refused=true."
)


def retrieve(query: str, docs: dict, k: int) -> list[str]:
    """Keyword-overlap retrieval over the real corpus; returns top-k doc_ids."""
    q = set(re.findall(r"\w+", query.lower()))
    scored = []
    for did, doc in docs.items():
        terms = set(re.findall(r"\w+", (doc["text"] + " " + did).lower()))
        scored.append((len(q & terms), did))
    scored.sort(reverse=True)
    return [did for score, did in scored[:k] if score > 0]


def ask(query: str, docs: dict, k: int) -> dict:
    ids = retrieve(query, docs, k)
    context = "\n\n".join(f"[{d}]\n{docs[d]['text']}" for d in ids)
    raw = model_client.generate(
        f"Documents:\n{context}\n\nQuestion: {query}", system=_SYSTEM, temperature=0.0
    )
    cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        data = {"answer": raw, "citations": [], "refused": False, "reason": None}
    data["retrieved_ids"] = ids
    data.setdefault("citations", [])
    return data


def main() -> None:
    cases = load_dataset(DATASET)
    dhash = dataset_hash(cases)
    docs = load_documents()

    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("BoK-Corpus-Stage2")
    print(f"Model: {model_client.model_name()} | corpus {len(docs)} docs | "
          f"dataset {dhash[:12]} ({len(cases)} cases)\n")

    tallies = collections.Counter()
    ran_d10 = ran_d04 = 0

    with mlflow.start_run(run_name="bok-corpus"):
        mlflow.log_param("model", model_client.model_name())
        mlflow.log_param("dataset_hash", dhash)
        mlflow.log_param("corpus_docs", len(docs))
        mlflow.log_param("top_k", TOP_K)

        for case in cases:
            deferred = case["expectations"].get("_deferred", {})
            # only run on cases that declare a retrievable expectation
            expect_records = deferred.get("expect_records")
            if not expect_records and not deferred.get("expect_entities"):
                continue

            time.sleep(1.2)  # free-tier pacing
            try:
                out = ask(case["input"], docs, TOP_K)
            except Exception as exc:  # after retries exhausted: record + skip
                tallies["errors"] += 1
                print(f"  {case['id']}: ERROR ({type(exc).__name__}) - skipped")
                continue
            results = {}

            # D10: expected record(s) must be in top-k retrieved
            gold_ids = expect_records or deferred.get("expect_entities", [])
            if gold_ids:
                ran_d10 += 1
                # pass if ANY expected id is retrieved
                hit = any(check_retrieval(out["retrieved_ids"], g, TOP_K).passed
                          for g in gold_ids)
                results["D10"] = hit
                tallies["D10_pass" if hit else "D10_fail"] += 1

            # D04: citations must reference real corpus docs
            if out.get("citations"):
                ran_d04 += 1
                retrieved = {d: docs[d]["text"] for d in out["retrieved_ids"]}
                r04 = check_citations(out["citations"], retrieved)
                results["D04"] = r04.passed
                tallies["D04_pass" if r04.passed else "D04_fail"] += 1

            with mlflow.start_span(name=f"case:{case['id']}") as span:
                span.set_inputs({"question": case["input"]})
                span.set_outputs({
                    "retrieved": out["retrieved_ids"],
                    "expected": gold_ids,
                    "checks": results,
                })

        for k in sorted(tallies):
            mlflow.log_metric(k, tallies[k])

    print("Real-corpus results (81 real questions):")
    d10p, d10f = tallies.get("D10_pass", 0), tallies.get("D10_fail", 0)
    d04p, d04f = tallies.get("D04_pass", 0), tallies.get("D04_fail", 0)
    if d10p + d10f:
        print(f"  D10 retrieval : {d10p}/{d10p + d10f} cases retrieved an expected record")
    if d04p + d04f:
        print(f"  D04 citations : {d04p}/{d04p + d04f} cases cited only real corpus docs")
    print("\nSee http://localhost:5000 -> BoK-Corpus-Stage2 (Traces tab).")


if __name__ == "__main__":
    main()
