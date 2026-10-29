# Cheat Sheet 5 — MLflow 3.16 GenAI Evaluation

**One-pager for Capability 4.** MLflow is our system of record: traces, datasets, runs, UI.
**Source:** https://github.com/mlflow/mlflow · docs https://mlflow.org/docs/latest/
**Verification status:** ✅ **Verified 2026-10-29 against the installed package `mlflow==3.16.1`** (attribute checks, `inspect.signature`, `mlflow server --help`) and by running it: `harness/evaluate_native.py` executes `mlflow.genai.evaluate` with our D-check scorers.
**Second reader:** Gowtham · **Date:** 2026-10-29

---

## API we use (all present in 3.16.1)

| Symbol | Verified signature / behaviour |
|---|---|
| `mlflow.genai.evaluate(data, scorers, predict_fn=None, model_id=None)` | runs the evaluation; `data[i]["inputs"]` **must be a dict**, and its keys are passed as keyword args to `predict_fn` (we hit this error and fixed it) |
| `@mlflow.genai.scorer(name=..., aggregations=..., pass_if=...)` | scorer functions receive a subset of `inputs`, `outputs`, `expectations`, `trace`; returning `None` skips the case |
| `mlflow.genai.make_judge` | present (custom LLM judges) |
| `mlflow.genai.create_dataset` | present (registered evaluation datasets) |
| `mlflow.genai.scorers` built-ins | `Safety`, `RelevanceToQuery`, `Correctness`, `RetrievalGroundedness`, `RetrievalRelevance`, `RetrievalSufficiency`, `Guidelines` all present |
| `mlflow.start_span`, `MlflowClient.search_traces(locations=[...])` | tracing; `experiment_ids=` is deprecated in favour of `locations=` |

> Design rule: `assure-core` has no MLflow dependency. `harness/mlflow_adapter.py` wraps the checks as scorers.

## Server flags we use (present in `mlflow server --help`)

`--backend-store-uri`, `--artifacts-destination`, `--serve-artifacts`,
`--allowed-hosts`, `--cors-allowed-origins`, `--app-name`.
The 3.16 server log says its security middleware defaults to localhost-only;
`--allowed-hosts` and `--cors-allowed-origins` must be set before exposing it.

## Secure self-hosting (dev server, W1-3)

| Layer | Our setting |
|---|---|
| Server | ports bound to `127.0.0.1` only |
| Backend | PostgreSQL 16.4 (no host port published) |
| Artifacts | local volume with `--serve-artifacts` (MinIO left Docker Hub in Sep 2026) |
| Shared deployment | still needs a TLS reverse proxy + SSO; built-in basic auth is not relied on |

## Watch-outs

- Pin `mlflow==3.16.1`; API names changed across 3.x.
- The OSS server has no enterprise gating; our gate lives in `assure_core.gate`.

**Claim provenance:** every symbol and flag above was checked on the installed 3.16.1 package on 2026-10-29.
