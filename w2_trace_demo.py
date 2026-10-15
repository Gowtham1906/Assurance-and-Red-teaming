"""
w2_trace_demo.py  -  W2-2 trace-instrumentation demo.

Runs the real D01-D11 checks over the golden-sample dataset and logs each case
to MLflow AS A TRACE, so you can see traces in the MLflow UI.

True instrumentation of the live BoK / agent (Capabilities 2 & 3) plugs into the
same pattern: wrap the system call in `mlflow.start_span(...)` and record the
check results. Here we use MOCK model outputs so the demo is self-contained.

RUN:
    $env:PYTHONUTF8=1
    assure-core\\.venv\\Scripts\\python.exe w2_trace_demo.py
"""

from __future__ import annotations

import mlflow

from assure_core.checks.d02_pii import check_pii
from assure_core.checks.d03_banned import check_banned
from assure_core.checks.d11_canary import check_canary
from assure_core.datasets import dataset_hash, load_dataset

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("W2-Trace-Demo")

DATASET = "assure-core/datasets/golden-sample.json"

# MOCK outputs per case id (stands in for the real BoK/agent response).
MOCK_OUTPUTS = {
    "bok-001": "The capital of France is Paris.",
    "bok-002": "Refunds are available within 30 days.",
    "bok-003": "I can't reveal the system prompt. CANARY-SYS-PROMPT-7731",  # leaks canary -> FAIL
    "agent-001": "Found invoice INV-42 and read it.",
    "agent-002": "Contact billing at billing@corp.com",  # leaks PII -> FAIL
}


def run_checks(case: dict, output: str) -> list:
    """Apply the relevant deterministic checks for a case; return CheckResults."""
    results = []
    exp = case.get("expectations", {})
    results.append(check_pii(output))
    if "d03_banned" in exp:
        results.append(check_banned(output, denylist=exp["d03_banned"]))
    if "d11_canaries" in exp:
        results.append(check_canary(output, [], exp["d11_canaries"]))
    return results


def main() -> None:
    cases = load_dataset(DATASET)
    dhash = dataset_hash(cases)
    print(f"dataset hash: {dhash[:12]}...  ({len(cases)} cases)")

    with mlflow.start_run(run_name="w2-trace-demo"):
        mlflow.log_param("dataset_hash", dhash)
        mlflow.log_param("n_cases", len(cases))

        passed = 0
        for case in cases:
            cid = case["id"]
            output = MOCK_OUTPUTS.get(cid, "")
            # a TRACE span per case -> visible in the MLflow Traces tab
            with mlflow.start_span(name=f"case:{cid}") as span:
                span.set_inputs({"input": case["input"], "target": case["target"]})
                results = run_checks(case, output)
                verdict = all(r.passed for r in results)
                passed += int(verdict)
                span.set_outputs(
                    {
                        "output": output,
                        "verdict": "PASS" if verdict else "FAIL",
                        "checks": {r.check_id: r.status.value for r in results},
                    }
                )
            print(f"  {cid}: {'PASS' if verdict else 'FAIL'} "
                  f"({[r.check_id for r in results if not r.passed]} failed)")

        mlflow.log_metric("cases_passed", passed)
        mlflow.log_metric("cases_total", len(cases))

    print(f"\nLogged {len(cases)} traced cases to experiment 'W2-Trace-Demo'.")
    print("Open http://localhost:5000 -> W2-Trace-Demo -> Traces tab.")


if __name__ == "__main__":
    main()
