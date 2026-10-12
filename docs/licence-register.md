# W1-5 — Licence Register

**Deliverable:** Capability 4, Week 1, item W1-5.
**Done when:** a register for every tool used is in the repo (plan §12).
**Source:** October plan §4 (versions/licences from GitHub API + PyPI, 1 Oct 2026).
**Verification status:** licences/versions **as recorded in the plan**; re-confirm
against each project's `LICENSE` file + PyPI before any customer-facing use (plan §16).
**Last updated:** 2026-10-12 · **Reviewer:** `____________`

---

## Why this register exists

Supply-chain risk is OWASP **LLM03**. Before we build on a tool we record its
licence, version, and any licensing/ownership caveat. Three items need explicit
flags (plan §12): **promptfoo ownership**, **Langfuse `ee/`**, **Llama Guard licence**.

## Licence legend

- **Permissive OSI** (Apache-2.0, MIT): safe to use and build on.
- ⚠️ **Caveat:** mixed licence, non-OSI component, ownership change, or archived.
- 🚫 **Do not adopt / build on.**

---

## 1. Evaluation tools (plan §4.1)

| Tool | Version | Licence | Flag | Notes / action |
|------|---------|---------|------|----------------|
| **MLflow** | 3.16.1 | Apache-2.0 | OK | System of record. OSS server has no enterprise gating |
| Inspect AI (UK AISI) | 0.3.273 | MIT | OK | Agent/tool-use evals; shared with Cap 3 |
| promptfoo | current | MIT | ⚠️ | **OpenAI announced acquisition 9 Mar 2026**; README confirms OpenAI ownership + MIT. Vendor-neutrality risk — monitor licence on each upgrade |
| DeepEval | 4.2.7 | Apache-2.0 | OK | Pytest-style metrics |
| Giskard (`giskard-oss`) | 3.0.0 | Apache-2.0 | ⚠️ | v3 is a major change — re-check API before adopting |
| Evidently | 0.7.23 | Apache-2.0 | OK | Monitoring/drift |
| TruLens | 2.14.0 | MIT | OK | RAG-triad feedback |
| Ragas | 0.4.3 | Apache-2.0 | ⚠️ | Repo moved orgs; PyPI looks stale — reference only |
| lm-evaluation-harness | 0.4.13 | MIT | OK | Model benchmarks, not app assurance |
| Langfuse | 4.16.0 SDK | MIT core | ⚠️ | **`ee/` directories are a separate non-OSI licence — avoid `ee/` features** |
| OpenAI evals | — | NOASSERTION | 🚫 | Licence unclear; historic — do not adopt |

## 2. Red-teaming tools (plan §4.2)

| Tool | Version | Licence | Flag | Notes / action |
|------|---------|---------|------|----------------|
| garak (NVIDIA) | 0.17.0 | Apache-2.0 | OK | Broad probe sweeps vs HTTP target |
| **PyRIT** (Microsoft) | 1.1.0 | MIT | OK | Multi-turn + multilingual (Tamil/Hindi/Tanglish) |
| promptfoo red-team | current | MIT | ⚠️ | Same OpenAI-ownership caveat as above |
| Giskard | 3.0.0 | Apache-2.0 | ⚠️ | RAG scan; v3 API change |
| DeepTeam | 1.0.9 | Apache-2.0 | OK | Maps to OWASP; judge-heavy |
| AgentDojo (ETH) | 0.1.35 | MIT | OK | Indirect-injection agent benchmark; use for method |
| StrongREJECT | — (not on PyPI) | MIT | ⚠️ | Install from source; grader for jailbreak harm |
| NeMo Guardrails | 0.24.1 | Apache-2.0 | OK | **Defence under test**, not an attacker |
| Guardrails AI | 0.11.0 | Apache-2.0 | OK | **Defence under test** |
| **Llama Guard / PurpleLlama** | — | **Llama Community (non-OSI)** | ⚠️ | **Flag the licence** — community licence has use restrictions; review before any deployment |
| FuzzyAI | — (not on PyPI) | Apache-2.0 | ⚠️ | Slowing; low priority |
| HarmBench | stale (2024-25) | MIT | ⚠️ | Dataset source only |
| JailbreakBench | stale (2024-25) | MIT | ⚠️ | Dataset source only |
| **LLM Guard** | 0.3.16 | MIT | 🚫 | **Repo archived — do not build on it** |
| Counterfit | dormant since 2023 | MIT | 🚫 | Classical ML — skip |

## 3. Our own package

| Component | Version | Licence | Notes |
|-----------|---------|---------|-------|
| `assure-core` | 0.1.0 | Proprietary (internal) | No MLflow dependency; runtime dep: pydantic (MIT) |

## 4. Runtime dependencies of assure-core

| Dependency | Licence | Used for |
|------------|---------|----------|
| pydantic | MIT | D01 schema validation |
| pytest (dev) | MIT | tests |
| hypothesis (dev) | MPL-2.0 | property tests |

---

## Flagged items summary (the three the plan calls out)

1. **promptfoo** — OpenAI-owned since Mar 2026; still MIT. Re-check the licence
   on every upgrade; have a fallback (plain pytest gate) so we're not locked in.
2. **Langfuse `ee/`** — enterprise directories carry a separate non-OSI licence.
   Use the MIT core only; **do not enable `ee/` features**.
3. **Llama Guard / PurpleLlama** — Llama Community licence (non-OSI) with use
   restrictions; review terms before using as an output classifier.

## Policy

- Pin exact versions (plan §15 vendor-drift risk).
- Re-review this register whenever a tool is upgraded or added.
- 🚫 items must not be imported into `assure-core` or the harness.
