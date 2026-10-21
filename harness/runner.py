"""
harness/runner.py  -  the REAL, dynamic assurance runner.

For each case in a golden dataset:
  1. send the real question to the real RAG system (live OpenAI call)
  2. dispatch each declared expectation to the matching D01-D11 check
     (dynamic - nothing hardcoded per case; add an expectation key and it runs)
  3. log the result + a trace to MLflow

Supports any case type via the ``expectations`` keys. RAG and agent targets both
flow through the same dispatcher.

RUN:
    $env:PYTHONUTF8=1
    assure-core\\.venv\\Scripts\\python.exe -m harness.runner
    # or point at a specific dataset:
    assure-core\\.venv\\Scripts\\python.exe -m harness.runner assure-core/datasets/golden-rag.json
"""

from __future__ import annotations

import sys

import mlflow

from assure_core.checks.d01_schema import check_schema
from assure_core.checks.d02_pii import check_pii
from assure_core.checks.d03_banned import check_banned
from assure_core.checks.d04_citations import check_citations
from assure_core.checks.d07_language import check_language
from assure_core.checks.d08_refusal import check_refusal
from assure_core.checks.d10_retrieval import check_retrieval
from assure_core.checks.d11_canary import check_canary
from assure_core.datasets import dataset_hash, load_dataset
from assure_core.result import CheckResult
from harness import model_client, rag_system

DEFAULT_DATASET = "assure-core/datasets/golden-rag.json"


def run_expectations(case: dict, result: dict) -> list[CheckResult]:
    """Dynamically dispatch each expectation key to its check against REAL output."""
    exp = case.get("expectations", {})
    out: list[CheckResult] = []

    if "d01_schema" in exp:
        out.append(check_schema(result, exp["d01_schema"]))
    if exp.get("d02_pii"):
        out.append(check_pii(result.get("answer", "")))
    if "d03_banned" in exp:
        out.append(check_banned(result.get("answer", ""), denylist=exp["d03_banned"]))
    if exp.get("d04_citations"):
        retrieved = {doc_id: rag_system._load_corpus().get(doc_id, "")
                     for doc_id in result.get("retrieved_ids", [])}
        out.append(check_citations(result.get("citations", []), retrieved))
    if "d07_language" in exp:
        out.append(check_language(result.get("answer", ""), exp["d07_language"]))
    if "d08_expected_refusal" in exp:
        out.append(check_refusal(result, exp["d08_expected_refusal"]))
    if "d10_gold_doc" in exp:
        out.append(check_retrieval(result.get("retrieved_ids", []),
                                   exp["d10_gold_doc"], exp.get("d10_k", 3)))
    if "d11_canaries" in exp:
        out.append(check_canary(result.get("answer", ""), [], exp["d11_canaries"]))
    return out


def main(dataset_path: str = DEFAULT_DATASET) -> None:
    cases = load_dataset(dataset_path)
    dhash = dataset_hash(cases)
    print(f"Model: {model_client.model_name()}  |  dataset {dhash[:12]} ({len(cases)} cases)\n")

    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("Real-RAG-Assurance")

    with mlflow.start_run(run_name="real-rag-run"):
        mlflow.log_param("model", model_client.model_name())
        mlflow.log_param("dataset_hash", dhash)
        passed = 0

        for case in cases:
            cid = case["id"]
            with mlflow.start_span(name=f"case:{cid}") as span:
                span.set_inputs({"question": case["input"]})
                # --- REAL model call ---
                result = rag_system.ask(case["input"], k=case["expectations"].get("d10_k", 3))
                checks = run_expectations(case, result)
                verdict = all(c.passed for c in checks)
                passed += int(verdict)
                failed = [c.check_id for c in checks if not c.passed]
                span.set_outputs({
                    "answer": result.get("answer", ""),
                    "refused": result.get("refused"),
                    "retrieved_ids": result.get("retrieved_ids"),
                    "verdict": "PASS" if verdict else "FAIL",
                    "failed_checks": failed,
                })
            print(f"  {cid}: {'PASS' if verdict else 'FAIL'}"
                  + (f"  (failed: {failed})" if failed else ""))

        mlflow.log_metric("cases_passed", passed)
        mlflow.log_metric("cases_total", len(cases))
        print(f"\n{passed}/{len(cases)} cases passed. "
              f"See http://localhost:5000 -> Real-RAG-Assurance (Traces tab).")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATASET)
