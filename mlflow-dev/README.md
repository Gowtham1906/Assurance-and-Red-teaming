# MLflow Dev Tracking Server (W1-3)

Dev **system of record** for Capability 4: traces, datasets, runs, prompt
registry, UI. Pinned to **mlflow 3.16.1** (Apache-2.0).

**Done when (plan §12):** runs and traces are visible in the UI, and the server
is **not publicly exposed**.

## Stack

| Component | Image | Role |
|-----------|-------|------|
| MLflow server | `ghcr.io/mlflow/mlflow:v3.16.1` | Tracking API + UI on :5000 |
| PostgreSQL | `postgres:16.4` | Backend store (runs, params, metrics) — **not SQLite** |
| Artifacts | local Docker volume `mlflow-artifacts` | Served via MLflow proxy |

Artifacts use **proxied access** (`--serve-artifacts --artifacts-destination`):
clients talk only to MLflow, never to the artifact store directly
(plan §5 hardening).

> **No MinIO on the dev box.** MinIO withdrew its images from Docker Hub
> (~Sep 2026) and the quay.io mirror now requires auth for every tag, so
> `minio/minio` is no longer anonymously pullable. The dev server uses a local
> artifact volume instead — no external image, same proxied-access guarantee.
> See "Scaling to blob storage" below for shared/real deployments.

## Run (Windows)

```bash
cd mlflow-dev
copy .env.example .env
# EDIT .env — set strong unique values for every secret
docker compose up -d
docker compose ps          # all services healthy
```

- MLflow UI: http://localhost:5000

Stop / reset:

```bash
docker compose down          # stop, keep data
docker compose down -v       # stop AND delete all data (postgres + artifact volumes)
```

## Troubleshooting

- **`pull access denied for minio/minio`** — expected; MinIO is gone from Docker
  Hub. This stack no longer uses it (see the note under "Stack").
- **`ports are not available: ... 127.0.0.1:5432 ... bind`** — a local PostgreSQL
  is already using 5432. This compose does **not** publish Postgres to the host
  (MLflow reaches it over the Docker network), so a fresh `docker compose up`
  avoids the clash. If you added a host mapping to inspect the DB, use `5433`.
- **`UnicodeEncodeError ... \U0001f3c3`** — cosmetic; see the UTF-8 note below.

## Smoke test — prove runs/traces are visible

From the `assure-core` venv (or any env with mlflow installed):

```powershell
pip install mlflow==3.16.1
# On Windows, enable UTF-8 so MLflow's emoji log lines don't crash cp1252:
$env:PYTHONUTF8=1
python -c "import mlflow; mlflow.set_tracking_uri('http://localhost:5000'); mlflow.set_experiment('smoke'); r=mlflow.start_run(); mlflow.log_param('p',1); mlflow.log_metric('m',0.5); mlflow.end_run(); print('logged', r.info.run_id)"
```

Then open http://localhost:5000 → experiment `smoke` → the run with param `p`
and metric `m` should appear. That satisfies "runs visible".

> **Windows UTF-8 note:** MLflow prints run links with emoji (🏃). The default
> Windows console (cp1252) raises `UnicodeEncodeError` on those characters —
> the run is still logged, only the final print crashes. Set `PYTHONUTF8=1`
> (or `$env:PYTHONUTF8=1` in PowerShell) to avoid it.

### Verified on this machine (2026-10-12)

- `GET http://localhost:5000/health` → **HTTP 200 OK**.
- Logged two runs to experiment `smoke`; both show **status=FINISHED** with
  their params/metrics when queried via `MlflowClient.search_runs`.
- Backend: PostgreSQL (container healthy). Artifacts: local volume, proxied.

## Security notes (plan §5) — READ BEFORE SHARING

This dev stack is deliberately **loopback-only**: every port binds to
`127.0.0.1`, so nothing is reachable from the LAN or Internet. That alone
satisfies "not publicly exposed" for a single-dev box.

For any **shared or real** deployment, add:

| Layer | Requirement |
|-------|-------------|
| Transport | **TLS reverse proxy** (nginx/Caddy/Traefik) in front of :5000; HTTPS only |
| Auth | **SSO** at the proxy. MLflow built-in basic-auth is experimental — do not rely on it |
| Network | Private network / VPC; no public ingress to :5000, :5432 |
| CORS / hosts | Review allowed-hosts and CORS on the proxy |
| Backend | PostgreSQL with strong creds in a secret store (not .env on disk) |
| Artifacts | Keep proxied access on; restrict who can load **pickled** model artifacts |
| Secrets | Judge-model API keys and store creds in a secret manager, not committed files |
| Patching | Pin to a patched MLflow release; watch advisories |

### Known risks (plan §15)

- Open-source MLflow has **no enterprise gating** (Databricks-managed is separate).
- **API churn across 3.x** — keep the version pinned; add an upgrade test in Week 3.
- **Exposure risk** if the proxy is skipped — never bind these ports to 0.0.0.0.

## Scaling to blob storage (shared / real deployments)

The dev server stores artifacts on a local volume. For shared or production use,
switch to an S3-compatible blob store **behind the proxy** (plan §5):

1. Provision a bucket (AWS S3, or a self-hosted S3 store you can pull/run).
2. Add to `.env`: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
   and (for non-AWS) `MLFLOW_S3_ENDPOINT_URL`.
3. In `docker-compose.yml`, pass those env vars to the `mlflow` service and
   change `--artifacts-destination` to `s3://<bucket>`. Keep `--serve-artifacts`
   so clients never hold storage creds.
4. If you need a self-hosted store, note MinIO is no longer on Docker Hub; pull
   it from an authenticated registry or use another S3-compatible server.

## Verification status

- **Verified:** version 3.16.1 + Apache-2.0 licence (plan §4);
  `docker compose config` validates.
- **Confirm on first `docker compose up`:** exact server CLI flags for 3.16 and
  the `ghcr.io/mlflow/mlflow:v3.16.1` tag; correct this file if flags differ.
