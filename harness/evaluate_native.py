"""
harness/evaluate_native.py  -  W3-1 "one command": run dataset x checks through
MLflow's OWN evaluation engine (mlflow.genai.evaluate), not manual logging.

Uses:
  * the real RAG app as predict_fn (live model answers)
  * the D01-D11 scorers from mlflow_adapter (native MLflow scorers)
  * the golden dataset as the evaluation data

RUN:
    $env:PYTHONUTF8=1
    assure-core\\.venv\\Scripts\\python.exe -m harness.evaluate_native
"""

from __future__ import annotations

import sys

import mlflow
import mlflow.genai

from assure_core.datasets import dataset_hash, load_dataset
from harness import model_client, rag_system
from harness.mlflow_adapter import ALL_SCORERS

DEFAULT = "assure-core/datasets/golden-rag.json"


def predict_fn(query: str) -> dict:
    """The app under test: MLflow passes each case's input field here."""
    return rag_system.ask(query, k=3)


def to_eval_data(cases: list[dict]) -> list[dict]:
    """Shape the golden cases into MLflow's evaluate() data format.

    MLflow requires `inputs` to be a dict of field->value; the field name
    ('query') must match predict_fn's parameter name.
    """
    return [
        {"inputs": {"query": c["input"]}, "expectations": c.get("expectations", {})}
        for c in cases
    ]


def main(path: str = DEFAULT) -> None:
    cases = load_dataset(path)
    dhash = dataset_hash(cases)

    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("Native-Eval-W3-1")

    print(f"Model: {model_client.model_name()} | dataset {dhash[:12]} "
          f"({len(cases)} cases)\nRunning mlflow.genai.evaluate ...\n")

    result = mlflow.genai.evaluate(
        data=to_eval_data(cases),
        scorers=ALL_SCORERS,
        predict_fn=predict_fn,
    )
    print("Done. Metrics:")
    for k, v in (result.metrics or {}).items():
        print(f"  {k}: {v}")
    print("\nSee http://localhost:5000 -> Native-Eval-W3-1 (Evaluation runs).")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)
