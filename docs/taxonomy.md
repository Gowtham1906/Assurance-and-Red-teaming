# W4-4 — Taxonomy skeleton (OWASP LLM 2025 + OWASP ASI 2026 × MITRE ATLAS)

**Pinned versions:** OWASP LLM Top 10 2025 · OWASP Agentic Top 10 2026 (Dec 2025) · **MITRE ATLAS v2026.10**
**ATLAS IDs:** every ID below exists in `redteam/atlas_v2026.10_techniques.csv`, generated from MITRE's `ATLAS.yaml` by `harness/probe_atlas.py`. Mappings (which ID goes with which OWASP item) are our judgement and need review.
**Owner / reviewer:** Gowtham · **Date:** 2026-10-29 · **Status:** draft for review

---

## 1. OWASP LLM Top 10 2025 × ATLAS

| OWASP | Name | ATLAS v2026.10 techniques | Our detection |
|---|---|---|---|
| LLM01 | Prompt Injection | AML.T0051 LLM Prompt Injection; AML.T0054 LLM Jailbreak | D11 canary, D08 refuse_injection |
| LLM02 | Sensitive Information Disclosure | AML.T0057 LLM Data Leakage; AML.T0024 Exfiltration via AI Inference API | D02 PII, D04 forbidden_evidence |
| LLM03 | Supply Chain | AML.T0010 AI Supply Chain Compromise; AML.T0058 Publish Poisoned Models | licence register, pinning |
| LLM04 | Data and Model Poisoning | AML.T0020 Poison Training Data; AML.T0019 Publish Poisoned Datasets | corpus-poisoning cases (planned) |
| LLM05 | Improper Output Handling | AML.T0067 LLM Trusted Output Components Manipulation | D01 schema |
| LLM06 | Excessive Agency | AML.T0053 AI Agent Tool Invocation; AML.T0101 Data Destruction via AI Agent Tool Invocation | D05 allowlist (agent) |
| LLM07 | System Prompt Leakage | AML.T0056 Extract LLM System Prompt | D11 system-prompt canary, D03 denylist |
| LLM08 | Vector and Embedding Weaknesses | AML.T0070 RAG Poisoning; AML.T0071 False RAG Entry Injection; AML.T0064 Gather RAG-Indexed Targets | D10, D04, scope filter |
| LLM09 | Misinformation | AML.T0062 Discover LLM Hallucinations; AML.T0060 Publish Hallucinated Entities | D04, key_facts + groundedness judges |
| LLM10 | Unbounded Consumption | AML.T0034 Cost Harvesting; AML.T0034.002 Agentic Resource Consumption; AML.T0029 Denial of AI Service | D06 limits |

## 2. OWASP Agentic Top 10 2026 × ATLAS

| ASI | Name | ATLAS v2026.10 techniques | Our detection |
|---|---|---|---|
| ASI01 | Agent Goal Hijack | AML.T0051 LLM Prompt Injection; AML.T0100 AI Agent Clickbait | D11, D08 |
| ASI02 | Tool Misuse and Exploitation | AML.T0053 AI Agent Tool Invocation; AML.T0086 Exfiltration via AI Agent Tool Invocation | D05 |
| ASI03 | Identity and Privilege Abuse | AML.T0083 Credentials from AI Agent Configuration; AML.T0098 AI Agent Tool Credential Harvesting; AML.T0082 RAG Credential Harvesting | permission cases (planned) |
| ASI04 | Agentic Supply Chain Vulnerabilities | AML.T0104 Publish Poisoned AI Agent Tool; AML.T0110 AI Agent Tool Poisoning; AML.T0109 AI Supply Chain Rug Pull | tool pinning, licence register |
| ASI05 | Unexpected Code Execution | AML.T0053 AI Agent Tool Invocation (code/shell tools) | sandbox + D05 forbidden sequences |
| ASI06 | Memory & Context Poisoning | AML.T0080 AI Agent Context Poisoning; AML.T0080.000 Memory; AML.T0070 RAG Poisoning | D11, D10 |
| ASI07 | Insecure Inter-Agent Communication | no direct technique found in v2026.10 | not covered |
| ASI08 | Cascading Failures | no direct technique; closest AML.T0031 Erode AI Model Integrity | not covered |
| ASI09 | Human-Agent Trust Exploitation | AML.T0048.003 User Harm (impact) | judge rubric (planned) |
| ASI10 | Rogue Agents | AML.T0081 Modify AI Agent Configuration; AML.T0103 Deploy AI Agent | not covered |

## 3. NIST AI 100-2 E2025 term (one per case)

Use one of: `evasion`, `poisoning`, `privacy`, `misuse`. LLM01/LLM07 → misuse;
LLM02 → privacy; LLM04/LLM08 → poisoning. See cheat sheet 4 (labels still to be
checked against the PDF).

## 4. Coverage today

| Covered with a running check | Planned | No coverage yet |
|---|---|---|
| LLM01, LLM02, LLM05, LLM07, LLM08, LLM09, LLM10 | LLM03, LLM04, LLM06/ASI01–06 (need Cap 3 agent) | ASI07, ASI08, ASI10 (need multi-agent setup) |

## 5. Corrected §9 allocation (replaces the plan's rows 10–11)

| # | Category | Cases | OWASP LLM | OWASP ASI |
|---|---|---|---|---|
| 10 | Excessive agency and tool misuse | 6 | LLM06 | ASI02, ASI03, ASI05 |
| 11 | Cost and resource exhaustion | 2 | LLM10 | — (ASI08 is Cascading Failures) |

The case schema is `redteam/schema/case.schema.json`; an example case is `redteam/cases/rt-001-system-prompt-extraction.json`.
