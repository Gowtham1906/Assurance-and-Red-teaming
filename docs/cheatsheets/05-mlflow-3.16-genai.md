# Cheat Sheet 5 — MLflow 3.16 GenAI Evaluation

**One-pager for Capability 4.** MLflow is our **system of record**: traces, datasets, runs, prompt registry, UI.
**Source:** https://github.com/mlflow/mlflow · docs at https://mlflow.org/docs/latest/
**Verification status:** Version **verified**: mlflow **3.16.1 (16 Sep 2026), Apache-2.0** (plan §4/§5). API names below are ⚠️ **from training knowledge — re-check the 3.16 docs** (plan §5/§16).
**Second reader:** `____________` · **Date:** `__________`

---

## What we use it for

| Feature | Role in our harness |
|---------|---------------------|
| **Tracking server + UI** | One place to see runs, metrics, traces |
| **Traces** (OpenTelemetry-compatible) | Every eval/agent run emits a trace |
| **Datasets** | Register golden sets with a content hash |
| **Prompt registry** | Versioned prompts |
| **Scorers / judges** | Wrap our deterministic checks + LLM judges |
| **Human feedback** | Assessments attached to traces |

## Key API surface (⚠️ UNVERIFIED — pin and re-check in 3.16 docs)

| Symbol | Purpose | Note |
|--------|---------|------|
| `mlflow.genai.evaluate(data, predict_fn, scorers)` | Entry point to run an eval | Confirm signature in 3.16 |
| `mlflow.genai.scorers` | Built-in judges: Safety, RelevanceToQuery, Correctness, RetrievalGroundedness, RetrievalRelevance, RetrievalSufficiency, Guidelines | **Names changed 3.0→3.x** — import by name, keep upgrade test |
| `make_judge` | Build a custom judge | From ~3.4; confirm |
| `@scorer` decorator | Wrap a plain-Python check as a scorer | Our D01–D11 adapt here |

> **Design rule (plan §5):** `assure-core` has **no MLflow dependency**. The
> MLflow *adapter* wraps our checks via `@scorer`; checks also run in plain pytest.

---

## Secure self-hosting (plan §5) — dev server (W1-3)

| Layer | Setting |
|-------|---------|
| Server | `mlflow server` behind a **TLS reverse proxy + SSO**; never exposed directly |
| Auth | Built-in basic-auth is **experimental** — prefer the proxy; review allowed-hosts/CORS |
| Backend store | **PostgreSQL** (not SQLite) |
| Artifact store | Blob storage with **proxied artifact access** (clients never hold storage creds) |
| Hardening | Private network; restrict loading pickled models; judge API keys in a secret store |

## Watch-outs

- **API churn across 3.x** (plan §15): pin `mlflow==3.16.1`, add an upgrade test.
- Open-source server has **no enterprise gating** (Databricks-managed MLflow is a separate product).
- Everything in the API table is **unverified from docs** (plan §16) — verify before building the adapter in Week 3.

**Claim provenance:** version + licence verified (plan §4). API names from training knowledge, flagged unverified (plan §5, §16). Action: read 3.16 GenAI docs, confirm each symbol, flip to Verified.
