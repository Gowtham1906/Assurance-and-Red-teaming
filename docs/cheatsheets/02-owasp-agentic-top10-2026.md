# Cheat Sheet 2 — OWASP Top 10 for Agentic Applications 2026 (ASI01–ASI10)

**One-pager for Capability 4.** Taxonomy for agent (tool-using) targets.
**Source:** https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
**Verification status:** ⚠️ **UNVERIFIED.** Plan §3 notes the ASI names come from *secondary summaries* that are "consistent across sources" but the **PDF must be read** before these are quoted. Treat IDs below as provisional.
**Second reader:** `____________` · **Date:** `__________`

---

## Why a separate list

The standard LLM Top 10 covers single-shot text risks. **Agents** add: memory,
planning, multi-step tool calls, and interaction with other agents. The Agentic
list targets those agent-specific failure modes.

## Provisional risks (CONFIRM AGAINST PDF)

The official list is **ASI01–ASI10**. Only the IDs our red-team cases actually
use are shown below (plan §9). The remaining IDs will be added **with their real
names from the official PDF** when needed — we don't list empty placeholders.

| ID | Theme (provisional) | Plain meaning | Our relevant checks |
|----|--------------------|----------------|---------------------|
| **ASI01** | Agent prompt/goal manipulation | Injected instructions redirect the agent's goal | D11 canary, D05 tool allowlist |
| **ASI02** | Tool misuse / excessive agency | Agent calls tools it shouldn't, or with bad args | D05 allowlist + arg schema |
| **ASI03** | Identity / permission abuse | Agent acts across users/scopes it shouldn't | RAG permission + cross-user cases |
| **ASI05** | Unsafe autonomous action | State-changing action without proper confirmation | D05, confirmation-step cases |
| **ASI06** | Memory / context poisoning | Poisoned context or memory steers later steps | D11, indirect-injection cases |
| **ASI08** | Resource / cost exhaustion | Agent loops or over-consumes | D06 limits |

> Shows the six ASI IDs referenced by the plan's §9 case table. The full
> ASI01–ASI10 names must be taken from the official OWASP Agentic PDF before use.

---

## How we use it

- Agent-target cases (plan §9 rows 2, 5, 6, 10) carry ASI IDs **in addition to** LLM IDs.
- Pair with **MITRE ATLAS** agent techniques (cheat sheet 3): AML.T0080 context poisoning, AML.T0086 exfiltration via tool invocation.

## Watch-outs

- **Do not quote ASI names to customers** until the PDF is read and this sheet
  is updated to "Verified." (plan §16 lists this as unverified.)

**Claim provenance:** all content provisional, from plan §3/§16 secondary-source note. Action: read the official OWASP Agentic PDF, correct the table, flip status to Verified.
