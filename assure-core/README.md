# assure-core

Deterministic assurance checks for Capability 4. **The hard release gate.**

**Design rule (plan §5):** this package has **NO MLflow dependency**. Checks are
plain Python and run under plain `pytest`. An MLflow *adapter* (built in Week 3,
outside this package) wraps each check as a `@scorer`.

## Layout

```
assure-core/
├── pyproject.toml
├── src/assure_core/
│   ├── __init__.py
│   ├── result.py          # CheckResult, Severity, Status (shared types)
│   ├── checks/            # D01–D11, one module each (STUBS in Week 1)
│   ├── stats/             # paired bootstrap, McNemar, Wilson (Week 2)
│   └── report/            # JUnit XML + Markdown/HTML report builder (Week 2)
├── tests/                 # unit + negative fixtures + mutation + property tests
└── docs/CHECK-SPECS.md    # D01–D11 specifications (W1-4 deliverable)
```

## Status

**Week 1 (W1-4): layout + specs only.** Check modules are stubs that raise
`NotImplementedError`; the shared `CheckResult` type and the registry are real so
tests and the adapter can be wired in Week 2. See `docs/CHECK-SPECS.md`.

## Install (editable, dev)

```bash
cd assure-core
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest
```
