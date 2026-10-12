# W1-1 — Scope and Risk-Tier Register

**Deliverable:** Capability 4, Week 1, item W1-1
**Done when:** tier and owner recorded for each in-scope target.
**Last updated:** 2026-10-12

---

## 1. Purpose

Record which AI systems Capability 4 assurance applies to in October, assign a
risk tier to each, and name a single accountable owner. This register is the
starting point for the harness (what we test), the gating policy (how hard we
gate), and the red-team library (what we attack).

The October plan says: **BoK (Capability 2) and the agent sandbox (Capability 3)
first.** Everything else is out of scope for October.

---

## 2. Risk-tier definitions

Tiers decide how hard the release gate is and how much red-teaming a target gets.

| Tier | Meaning | Example triggers | Gate strictness |
|------|---------|------------------|-----------------|
| **T1 — Critical** | Can take state-changing actions, touch multiple users' data, or run with real tools/credentials | Agent with write-access tools; multi-tenant RAG over sensitive data | Full deterministic gate + sealed-set paired tests + full red-team suite; any Critical/High finding blocks release |
| **T2 — High** | Reads sensitive or user-scoped data, answers that users act on, but no state-changing tools | RAG over internal docs; single-user assistant | Deterministic gate + sealed set; High findings block unless approved exception |
| **T3 — Moderate** | Read-only over non-sensitive content, low blast radius | Public-docs Q&A; demo sandbox | Deterministic smoke set + nightly trend; Medium findings get an SLA |
| **T4 — Low** | Experimental, non-production, synthetic data only | Throwaway spikes | Smoke checks only |

Modifiers that **raise** a tier: higher agent autonomy, write/tool access,
real (non-synthetic) data, multi-tenant exposure.
Modifiers that **lower** a tier: mandatory human confirmation step, read-only,
non-production environment.

---

## 3. In-scope targets (October)

> Fill in the **Owner** column with a real person. One accountable owner each.

### Target 1 — BoK (Capability 2 Body of Knowledge)

| Field | Value |
|-------|-------|
| System ID | `bok-rag` |
| Type | RAG application (retrieval + generation) |
| Description | Answers questions over the Body of Knowledge corpus |
| Data sensitivity | Internal content; check for any PII or restricted docs in corpus |
| State-changing actions | None (read-only Q&A) |
| Tools enabled | Retrieval only |
| Environment | Dev / sandbox |
| **Proposed risk tier** | **T2 — High** (user-scoped reads, answers acted on; raise to T1 if corpus holds sensitive/multi-tenant data) |
| **Owner** | `____________` |
| First datasets | 80 BoK questions (plan §7) |
| Priority checks | D01, D02, D03, D04, D10, D11 |

### Target 2 — Agent sandbox (Capability 3)

| Field | Value |
|-------|-------|
| System ID | `agent-sandbox` |
| Type | Tool-using agent |
| Description | Agent that plans and calls tools in a sandbox |
| Data sensitivity | Synthetic data in sandbox; confirm no real credentials |
| State-changing actions | Possible (depends on tools enabled) |
| Tools enabled | Per sandbox policy file (allowlist) |
| Environment | Dev / sandbox |
| **Proposed risk tier** | **T1 — Critical** (tool use + potential state change = highest blast radius) |
| **Owner** | `____________` |
| First datasets | 80 agent cases (plan §7) |
| Priority checks | D01, D05, D06, D08, D09, D11 |

---

## 4. Out of scope for October

- The 50-case red-team library (November).
- Release gating that blocks merges (November).
- The Health Check customer offer (December).
- Any production system or real customer data.

---

## 5. Sign-off

| Role | Name | Date |
|------|------|------|
| Register author | `____________` | |
| Second reviewer | `____________` | |
| Capability 4 lead | `____________` | |

**Status:** DRAFT — owners not yet assigned. Complete the Owner fields and
reviewer sign-off to mark W1-1 done.
