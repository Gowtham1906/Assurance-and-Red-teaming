"""
harness/run_bok_judges.py  -  W3-2: run the SOFT LLM judges on the real BoK set.

For each real case that declares gold_key_facts:
  1. retrieve from the real 79-doc corpus
  2. get the live model's answer
  3. judge it (SOFT signals, never a hard gate):
        key_facts_judge     - does the answer convey the required key facts?
        groundedness_judge  - is the answer supported by the retrieved docs?

Logs mean judge scores to MLflow. These are TRENDS/WARNINGS, not pass/fail
gates (plan §1: judges trend, deterministic checks gate).

To limit free-tier cost/time, runs on a sample (default 15 cases); pass an int
to change: `... -m harness.run_bok_judges 30`.

RUN:
    $env:PYTHONUTF8=1
    assure-core\\.venv\\Scripts\\python.exe -m harness.run_bok_judges 15
"""

from __future__ import annotations

import sys
import time

import mlflow

from assure_core.datasets import load_dataset
from harness import model_client
from harness.bok_corpus_loader import load_documents
from harness.judges import groundedness_judge, key_facts_judge
from harness.run_bok_corpus import ask  # reuse real-corpus retrieval + answer

DATASET = "assure-core/datasets/golden-bok-v1.json"
TOP_K = 5


def main(limit: int = 15) -> None:
    cases = [c for c in load_dataset(DATASET)
             if c["expectations"].get("_deferred", {}).get("gold_key_facts")]
    cases = cases[:limit]
    docs = load_documents()

    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("BoK-Judges-W3-2")
    print(f"Model/judge: {model_client.model_name()} | {len(cases)} cases with gold_key_facts\n")

    kf_scores, gnd_scores = [], []

    with mlflow.start_run(run_name="bok-judges"):
        mlflow.log_param("judge_model", model_client.model_name())
        mlflow.log_param("n_cases", len(cases))
        mlflow.set_tag("signal_type", "soft (advisory, never a hard gate)")

        for case in cases:
            facts = case["expectations"]["_deferred"]["gold_key_facts"]
            time.sleep(1.2)
            try:
                out = ask(case["input"], docs, TOP_K)
            except Exception as exc:
                print(f"  {case['id']}: ERROR ({type(exc).__name__}) - skipped")
                continue
            retrieved_text = [docs[d]["text"] for d in out.get("retrieved_ids", []) if d in docs]

            time.sleep(1.2)
            kf = key_facts_judge(out.get("answer", ""), facts)
            time.sleep(1.2)
            gnd = groundedness_judge(out.get("answer", ""), retrieved_text)
            kf_scores.append(kf.score)
            gnd_scores.append(gnd.score)

            with mlflow.start_span(name=f"judge:{case['id']}") as span:
                span.set_inputs({"question": case["input"], "gold_key_facts": facts})
                span.set_outputs({
                    "answer": out.get("answer", "")[:300],
                    "key_facts_score": kf.score,
                    "groundedness_score": gnd.score,
                })
            print(f"  {case['id']}: key_facts={kf.score:.2f}  grounded={gnd.score:.2f}")

        if kf_scores:
            mlflow.log_metric("key_facts_mean", sum(kf_scores) / len(kf_scores))
            mlflow.log_metric("groundedness_mean", sum(gnd_scores) / len(gnd_scores))

    if kf_scores:
        print(f"\nSOFT judge means (advisory):")
        print(f"  key_facts    : {sum(kf_scores)/len(kf_scores):.2f}")
        print(f"  groundedness : {sum(gnd_scores)/len(gnd_scores):.2f}")
    print("\nReminder: judges are SOFT signals - they trend/warn, never block alone.")
    print("See http://localhost:5000 -> BoK-Judges-W3-2 (Traces tab).")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 15)
