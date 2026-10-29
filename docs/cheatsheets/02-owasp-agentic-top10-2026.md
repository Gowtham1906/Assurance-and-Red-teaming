# Cheat Sheet 2 — OWASP Top 10 for Agentic Applications 2026 (ASI01–ASI10)

**One-pager for Capability 4.** Taxonomy for agent (tool-using) targets.
**Official source:** https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ (published 9 Dec 2025; full text in the downloadable PDF)
**Verification status:** ✅ **Names verified 2026-10-29.** Publication date and title confirmed on the official OWASP page. The ten names were taken from Giskard's summary (https://www.giskard.ai/knowledge/owasp-top-10-for-agentic-application-2026) and match AppSentinels and Modulos. The official PDF itself was not read; re-check wording against it before quoting in a customer contract.
**Second reader:** Gowtham · **Date:** 2026-10-29

---

## Why a separate list

The LLM Top 10 covers single-turn text risks. Agents add planning, tool calls,
memory, identity and talking to other agents. This list covers those.

## The ten risks

| ID | Name | Plain meaning | Our relevant checks |
|----|------|---------------|---------------------|
| **ASI01** | Agent Goal Hijack | Injected content (documents, email, web) redirects the agent's goal | D11 canary, D05 allowlist |
| **ASI02** | Tool Misuse and Exploitation | Legitimate tools used unsafely (wrong tool, over-privileged, exfiltration via tool) | D05 allowlist + argument schema |
| **ASI03** | Identity and Privilege Abuse | Agent acts with privileges or credentials it should not use (confused deputy) | permission / cross-user cases |
| **ASI04** | Agentic Supply Chain Vulnerabilities | Compromised tools, MCP servers or templates loaded at runtime | licence register, tool pinning |
| **ASI05** | Unexpected Code Execution (RCE) | Agent generates and runs code or shell commands that cause harm | sandbox + D05 forbidden sequences |
| **ASI06** | Memory & Context Poisoning | Poisoned memory or RAG data biases later decisions | D11, D10, corpus-poisoning cases |
| **ASI07** | Insecure Inter-Agent Communication | Messages between agents spoofed, intercepted or replayed | not covered yet |
| **ASI08** | Cascading Failures | One faulty agent's output propagates through others | not covered yet |
| **ASI09** | Human-Agent Trust Exploitation | Agent persuades a human into a harmful approval | judge rubric (future) |
| **ASI10** | Rogue Agents | Agent drifts from its purpose (reward hacking, self-replication) | not covered yet |

---

## Corrections to earlier drafts and to the October plan

The first draft of this sheet and the plan's §9 case table used two wrong mappings:

| Plan / old draft said | Correct |
|---|---|
| ASI05 = unsafe autonomous / state-changing action | ASI05 = **Unexpected Code Execution**. Unsafe state-changing tool use is **ASI02** (and ASI03 when privilege is involved) |
| ASI08 = resource / cost exhaustion | ASI08 = **Cascading Failures**. Cost exhaustion stays under **LLM10** only |

Action for November: update the §9 allocation table (row 10 → ASI02/ASI03/ASI05; row 11 → LLM10 only).

## How we use it

- Agent cases carry ASI IDs in addition to LLM IDs.
- Pair with MITRE ATLAS agent techniques (cheat sheet 3).
- ASI07, ASI08 and ASI10 need multi-agent setups; none exist in Capability 3 yet.

**Claim provenance:** title and date from the official OWASP page; names and descriptions from the Giskard summary, consistent with two other independent summaries.
