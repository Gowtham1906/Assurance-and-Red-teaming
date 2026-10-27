# BoK Assurance Report — Interim (Weeks 1–3)

**System under test:** Capability 2 BoK (governed manufacturing RAG)
**Prepared by:** Gowtham · **Date:** 2026-10-27
**Harness:** Capability 4 `assure-core` + MLflow · **Model used:** `openai/gpt-oss-20b` (Groq)
**Status:** INTERIM — a test-harness milestone, **not yet a release verdict** (see Limitations).

---

## 1. Executive summary & release recommendation

We built a working, repeatable assurance harness and ran it end-to-end against
the **real** Capability 2 golden set (81 questions) and the **real** 79-document
corpus. The machinery is complete: real deterministic checks, soft LLM judges,
statistics, and a release **gate** that returns PASS / FAIL / REVIEW.

**Release recommendation: DO NOT yet treat these numbers as a BoK verdict.**
The current results were produced by *our* stand-in retriever over Cap 2's
documents — **not** Capability 2's deployed BoK system. They establish that the
harness works and give a first baseline; a true verdict needs Cap 2's running
endpoint (see §9).

---

## 2. Scope, architecture, dates

- **Target:** Capability 2 BoK, risk tier **T2** (reads sensitive content; answers acted on).
- **Golden set:** 81 real SME-written cases (`bok-golden.jsonl`), registered in
  MLflow, hash `58de038a…`, split 49 dev / 32 sealed.
- **Corpus:** 79 real governed documents (25 KPI cards, 21 playbooks, 17
  standards, 16 case studies).
- **Test dates:** 2026-10-22 → 2026-10-27.

---

## 3. Method, taxonomy, tooling

- **Deterministic checks (hard gate):** D01–D11 in `assure-core`, mapped to
  OWASP LLM 2025 / ASI 2026 (see `assure-core/docs/CHECK-SPECS.md`).
- **Judges (soft signal):** key-facts coverage, groundedness (LLM-graded,
  temperature 0). Judges **never block alone** (plan §1).
- **Statistics:** Wilson lower bound, McNemar, paired bootstrap (gate on the
  lower bound, plan §7).
- **Gate:** `assure-core/policy/thresholds.yaml` + `assure_core.gate`.
- **Record:** MLflow (experiments: `golden-datasets`, `BoK-CorpusFree-Stage1`,
  `BoK-Corpus-Stage2`, `BoK-Judges-W3-2`, `baselines`).

---

## 4. Results (real measurements)

| Check | Result | Rate | Gate |
|-------|--------|------|------|
| D07 language | 57 / 81 | 70% | soft |
| D08 behaviour (answer/clarify/abstain/refuse) | 43 / 81 | 53% | hard |
| D11 injection refusal | 1 / 5 | 20% | hard |
| D10 retrieval hit (real corpus) | 31 / 45 | 69% | soft |
| D04 citation validity (real corpus) | 26 / 33 | 79% | hard |
| key-facts judge (mean) | — | 0.23 | soft |
| groundedness judge (mean) | — | 0.68 | soft |

**Gate decision on these numbers: FAIL** (hard checks below floor + fail-closed
on checks not run). This is the gate *working as designed*, not a BoK verdict.

---

## 5. Findings (interpretation)

- **D11 injection (1/5)** — the stand-in setup mostly failed to refuse injection
  attempts. Worth a real test against the deployed BoK, which may have defences
  our stand-in lacks. *Severity if confirmed on the real system: High.*
- **D08 behaviour (53%)** — many mismatches are because our stand-in *answers*
  where the real BoK would *abstain* (no governance/retrieval gating in our
  wrapper). Likely overstated.
- **D10 / D04 (69% / 79%)** — reflect our simple keyword retriever over the real
  corpus, not Cap 2's retrieval. A floor, not a ceiling.
- **key-facts (0.23)** — low largely because our retriever often didn't fetch the
  right document, so the model couldn't state the facts.

---

## 6. What held / what the harness proved

- The full loop runs on real data: dataset → checks + judges → MLflow → gate.
- Checks genuinely discriminate (verified: fail on corrupted inputs; judges score
  good answers high, bad answers low).
- The gate correctly separates **hard** (block) from **soft** (review) and
  **fails closed** on unmeasured hard checks.
- 92 automated tests pass.

---

## 7. Remediation roadmap

| Owner | Action | Unlocks |
|-------|--------|---------|
| Cap 2 | Provide a running BoK endpoint | true system verdict (replaces stand-in) |
| Cap 4 | Run D01/D02/D03/D05 in the corpus pipeline | remove fail-closed gaps |
| Cap 4 | Calibrate judges vs human labels (plan §7) | trustworthy soft signals |
| Cap 2/4 | Agree real threshold floors in `thresholds.yaml` | meaningful gate |

---

## 8. Retest

Every future run re-registers the dataset by hash and re-runs the gate against
the stored `baseline=prod`. Any regression beyond budget → REVIEW/FAIL.

---

## 9. Limitations & non-determinism (read this)

1. **Stand-in, not the real BoK.** We tested *our* RAG wrapper over Cap 2's
   corpus, not Capability 2's deployed system. Scores are a harness baseline,
   **not a verdict on their BoK.**
2. **Simple retriever.** Keyword overlap, not vector/governed retrieval — it
   understates D10/D04/key-facts.
3. **Placeholder thresholds.** Floors in `thresholds.yaml` are proposed defaults.
4. **Judge variance.** Judges not yet calibrated against humans; treat as soft.
5. **Single model, free tier.** One model (`gpt-oss-20b`); rate-limited.

---

## 10. Appendices

- Golden set: `bok-golden.jsonl` → `assure-core/datasets/golden-bok-v1.json`
- Corpus: `harness/bok_corpus/` (79 docs) · loader `harness/bok_corpus_loader.py`
- Checks: `assure-core/src/assure_core/checks/` · specs `.../docs/CHECK-SPECS.md`
- Judges: `harness/judges.py` · Gate: `assure-core/src/assure_core/gate.py`
- Policy: `assure-core/policy/thresholds.yaml` · Baseline: `.../policy/baseline.json`
- Runners: `harness/run_bok_corpusfree.py`, `run_bok_corpus.py`, `run_bok_judges.py`, `gate_cli.py`
- Evidence: MLflow at http://localhost:5000
