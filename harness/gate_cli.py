"""
harness/gate_cli.py  -  W3-4 baseline + gate command.

Two actions:

  record-baseline  - store a run's per-metric (passed,total) in MLflow tagged
                     `baseline=prod` with the dataset hash, and save it locally
                     so the gate can compare future runs to it.

  gate             - load the policy (thresholds.yaml) + the stored baseline,
                     apply assure_core.gate.evaluate_gate to a run's metrics,
                     and print PASS / FAIL / REVIEW.

Metrics are passed as a small JSON file: {"D02_pii": [100,100], ...}
(each value is [passed, total]). In the full pipeline these come straight from
the runners; here we keep it explicit and auditable.

RUN:
    # store the current results as the baseline
    ...-m harness.gate_cli record-baseline results/bok_metrics.json <dataset_hash>

    # gate a new run against policy + baseline
    ...-m harness.gate_cli gate results/bok_metrics.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import mlflow
import yaml

from assure_core.gate import evaluate_gate

POLICY_PATH = "assure-core/policy/thresholds.yaml"
BASELINE_PATH = "assure-core/policy/baseline.json"


def _load_metrics(path: str) -> dict[str, tuple[int, int]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return {k: (int(v[0]), int(v[1])) for k, v in raw.items()}


def _load_policy() -> dict:
    return yaml.safe_load(Path(POLICY_PATH).read_text(encoding="utf-8"))


def record_baseline(metrics_path: str, dataset_hash: str) -> None:
    metrics = _load_metrics(metrics_path)
    points = {k: (p / t if t else 0.0) for k, (p, t) in metrics.items()}

    # save locally for the gate to read
    Path(BASELINE_PATH).write_text(
        json.dumps({"dataset_hash": dataset_hash, "points": points,
                    "raw": {k: list(v) for k, v in metrics.items()}}, indent=2),
        encoding="utf-8",
    )
    # tag a run in MLflow as baseline=prod
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("baselines")
    with mlflow.start_run(run_name="baseline=prod"):
        mlflow.set_tag("baseline", "prod")
        mlflow.set_tag("dataset_hash", dataset_hash)
        for k, v in points.items():
            mlflow.log_metric(k, v)
    print(f"Baseline recorded -> {BASELINE_PATH} and MLflow (baseline=prod, "
          f"dataset_hash={dataset_hash[:12]}).")


def gate(metrics_path: str) -> None:
    metrics = _load_metrics(metrics_path)
    policy = _load_policy()
    baseline_points = None
    if Path(BASELINE_PATH).exists():
        baseline_points = json.loads(Path(BASELINE_PATH).read_text(encoding="utf-8"))["points"]

    result = evaluate_gate(metrics, policy, baseline=baseline_points)

    print(f"\nGATE DECISION: {result.decision}\n" + "-" * 50)
    for o in result.outcomes:
        mark = {"pass": "OK ", "review": "REV", "fail": "XXX"}[o.verdict]
        base = f" base={o.baseline_point:.2f}" if o.baseline_point is not None else ""
        print(f"  [{mark}] {o.name:16s} {o.passed}/{o.total} "
              f"point={o.point:.2f} low={o.lower_bound:.2f} floor={o.floor:.2f}"
              f"{base}  ({o.gate})")
    print("-" * 50)
    print(result.summary)
    # exit code: 0 pass, 2 review, 1 fail (useful for CI later)
    sys.exit(0 if result.decision == "PASS" else (2 if result.decision == "REVIEW" else 1))


def main(argv: list[str]) -> None:
    if len(argv) >= 3 and argv[0] == "record-baseline":
        record_baseline(argv[1], argv[2])
    elif len(argv) >= 2 and argv[0] == "gate":
        gate(argv[1])
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
