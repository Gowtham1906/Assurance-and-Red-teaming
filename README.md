# Capability 4 — Assurance and Red-teaming

Repeatable machinery to prove an AI system is safe enough to release, and to keep proving it.
See `Capability-4-Assurance-and-Red-Teaming-October-Plan.md` for the full plan.

## Repository layout

```
.
├── assure-core/            # Our deterministic-check package (NO MLflow dependency)
│   ├── pyproject.toml
│   ├── src/assure_core/    # Package source: checks D01–D11, stats, report
│   └── tests/              # Unit tests, negative fixtures, mutation cases
├── mlflow-dev/             # Dev MLflow tracking server (Docker Compose + Postgres)
│   ├── docker-compose.yml
│   ├── .env.example
│   └── README.md           # Run + security notes
├── docs/
│   ├── scope-and-risk-tiers.md   # W1-1
│   ├── licence-register.md       # W1-5
│   └── cheatsheets/              # W1-2 (five one-pagers)
└── README.md
```

## Week 1 deliverables (1–9 Oct)

| ID | Deliverable | Location | Done when |
|----|-------------|----------|-----------|
| W1-1 | Scope & risk-tier register | `docs/scope-and-risk-tiers.md` | Tier and owner recorded |
| W1-2 | Five cheat sheets | `docs/cheatsheets/` | Second reader; claims linked |
| W1-3 | MLflow dev server | `mlflow-dev/` | Runs/traces visible; not publicly exposed |
| W1-4 | `assure-core` layout + D01–D11 specs | `assure-core/` | Reviewed |
| W1-5 | Licence register | `docs/licence-register.md` | Register in repo |

## Quick start

```bash
# 1. assure-core package (editable install)
cd assure-core
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -e ".[dev]"
pytest

# 2. MLflow dev server
cd ../mlflow-dev
copy .env.example .env       # then edit secrets
docker compose up -d
# UI at http://localhost:5000 (behind proxy in a real deployment)
```
