"""
harness/register_dataset.py  -  register a golden dataset in MLflow (W2-3 done-when).

Keeps assure-core MLflow-free: the dataset logic (load/validate/hash/split) lives
in assure_core.datasets; this thin adapter logs it to the MLflow server so every
run can reference the exact dataset VERSION (its content hash).

This works TODAY with the sample dataset, and will take the real 160-case
golden-v1.json later with no changes -- just pass its path.

RUN:
    $env:PYTHONUTF8=1
    assure-core\\.venv\\Scripts\\python.exe -m harness.register_dataset
    # or a specific file:
    assure-core\\.venv\\Scripts\\python.exe -m harness.register_dataset assure-core/datasets/golden-v1.json
"""

from __future__ import annotations

import json
import sys

import mlflow

from assure_core.datasets import dataset_hash, load_dataset, split_dev_sealed

DEFAULT = "assure-core/datasets/golden-rag.json"


def register(dataset_path: str) -> str:
    """Load, hash, split, and log the dataset to MLflow. Returns the content hash."""
    cases = load_dataset(dataset_path)
    dhash = dataset_hash(cases)
    dev, sealed = split_dev_sealed(cases, sealed_fraction=0.4)

    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("golden-datasets")

    with mlflow.start_run(run_name=f"register:{dataset_path.split('/')[-1]}"):
        # the dataset version is identified by its content hash
        mlflow.log_param("dataset_path", dataset_path)
        mlflow.log_param("dataset_hash", dhash)
        mlflow.log_param("n_cases", len(cases))
        mlflow.log_param("n_dev", len(dev))
        mlflow.log_param("n_sealed", len(sealed))
        mlflow.set_tag("dataset_hash", dhash)
        # store the id/target manifest as an artifact (dev split only - sealed
        # stays out of the visible record in a real deployment)
        manifest = [{"id": c["id"], "target": c["target"]} for c in dev]
        mlflow.log_text(json.dumps(manifest, indent=2), "dev_manifest.json")

    return dhash


def main(path: str = DEFAULT) -> None:
    dhash = register(path)
    cases = load_dataset(path)
    dev, sealed = split_dev_sealed(cases)
    print(f"Registered '{path}' in MLflow experiment 'golden-datasets'.")
    print(f"  version (content hash): {dhash}")
    print(f"  cases: {len(cases)}  (dev {len(dev)} / sealed {len(sealed)})")
    print("  See http://localhost:5000 -> golden-datasets")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)
