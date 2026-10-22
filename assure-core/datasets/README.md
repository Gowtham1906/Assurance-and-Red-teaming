# Golden Datasets (W2-3)

Golden cases with deterministic expectations, used by the harness to run D01-D11.

**Status:** structure + a 5-case **sample** (`golden-sample.json`). The real v1
dataset is the **80 BoK questions + 80 agent cases** from Capabilities 2 & 3
(plan §7) — drop those in here in the same schema when available.

## Case schema

```json
{
  "id": "bok-001",                      // unique, stable
  "target": "bok" | "agent",
  "input": "the question / task",
  "expectations": { ...deterministic expectations the checks read... },
  "tags": ["optional", "labels"]
}
```

`expectations` carries the per-case inputs for the checks, e.g.
`d05_allowed_tools`, `d10_gold_doc`, `d11_canaries`, `d08_expected_refusal`.

## Dev vs sealed split (contamination control, plan §7)

- **dev** — visible to developers.
- **sealed** — held by the assurance team; kept out of prompts and the retrieval
  index; run only in CI; refreshed quarterly.

The split is **deterministic by case id** (hash-based), so a given case always
lands in the same bucket regardless of run order. See
`assure_core.datasets.split_dev_sealed`.

## Versioning & hashing

`assure_core.datasets.dataset_hash(cases)` produces a stable SHA-256 over the
canonical, id-sorted content. Record this hash on every run so results are tied
to an exact dataset version. Registering the same version as an MLflow dataset
(the plan's "done when") is handled by the Week 3 MLflow adapter.

## Who holds the sealed set

**Owner: Gowtham** (assurance team). The sealed cases must not be committed
to a developer-visible location in a real deployment — the sample here is for
structure only.
