# Cheat Sheet 1 — OWASP Top 10 for LLM Applications 2025

**One-pager for Capability 4.** Primary taxonomy for our red-team cases.
**Source:** https://genai.owasp.org/llm-top-10/
**Verification status:** List **verified** against the OWASP GenAI site (plan §3). Read the full project PDF for depth before writing cases.
**Second reader:** Gowtham · **Date:** 2026-10-22

---

## The ten risks

| ID | Name | Plain meaning | Our relevant checks |
|----|------|---------------|---------------------|
| **LLM01** | Prompt Injection | Attacker text (direct or hidden in a document) makes the model ignore its instructions | D11 canary, D05 tool allowlist |
| **LLM02** | Sensitive Information Disclosure | Model reveals PII, secrets, or data the user shouldn't see | D02 PII, D03 secrets |
| **LLM03** | Supply Chain | Compromised models, datasets, plugins, or dependencies | Licence register (W1-5), dependency pinning |
| **LLM04** | Data and Model Poisoning | Malicious data in training/fine-tune/retrieval corpus skews behaviour | D10 retrieval hit, corpus poisoning cases |
| **LLM05** | Improper Output Handling | Downstream system trusts model output unsafely (XSS, SQLi, command exec) | D01 schema, output encoding |
| **LLM06** | Excessive Agency | Agent has too much permission/autonomy and acts beyond intent | D05 tool allowlist, D06 limits |
| **LLM07** | System Prompt Leakage | Hidden system prompt (and anything in it) gets exposed | D03 banned strings, leakage cases |
| **LLM08** | Vector and Embedding Weaknesses | RAG retrieval abused: cross-user leakage, embedding inversion, poisoning | D04 citations, D10 retrieval, RAG permission cases |
| **LLM09** | Misinformation | Confident wrong/fabricated answers, bad citations, stale content | D04 citation validity, groundedness judge |
| **LLM10** | Unbounded Consumption | Cost/compute blowups, denial-of-wallet, resource exhaustion | D06 latency/token/cost limits |

---

## How we use it

- **Mapping:** every red-team case (plan §9) carries one or more LLM01–10 IDs.
- **Hard vs soft:** LLM01, LLM02, LLM07 map mostly to **deterministic** checks (hard gate). LLM09 leans on **judges** (soft, trend).
- **Coverage target (Nov 50 cases):** injection (direct+indirect) and RAG permission leakage get the most cases.

## Watch-outs

- Don't confuse the **2023** list with **2025**: names and ordering changed (e.g., "Sensitive Information Disclosure" rose to LLM02).
- Pair with **OWASP Agentic (ASI01–10)** for agent targets — see cheat sheet 2.

**Claim provenance:** all ten IDs/names above are quoted from plan §3 which marks them *Verified* against the OWASP GenAI site. Confirm against the live page before customer-facing use.
