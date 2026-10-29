# W1-2 — Reading Cheat Sheets

Five one-page references for Capability 4. **Done when:** a second reader has
reviewed each and every claim is linked to a source (plan §12, W1-2).

| # | Sheet | Status (2026-10-29) | Second reader |
|---|-------|--------|---------------|
| 1 | [OWASP LLM Top 10 2025](01-owasp-llm-top10-2025.md) | ✅ list verified | Gowtham |
| 2 | [OWASP Agentic Top 10 2026](02-owasp-agentic-top10-2026.md) | ✅ ASI01–10 names verified; PDF wording not re-read | Gowtham |
| 3 | [MITRE ATLAS](03-mitre-atlas.md) | ✅ verified, pinned **v2026.10** | Gowtham |
| 4 | [NIST AI 100-2 E2025](04-nist-ai-100-2.md) | ✅ publication + dimensions verified; ⚠️ attack-class labels to check in PDF | Gowtham |
| 5 | [MLflow 3.16 GenAI](05-mlflow-3.16-genai.md) | ✅ API + server flags verified on installed 3.16.1 | Gowtham |

## Corrections found during verification

- OWASP Agentic: **ASI05 is Unexpected Code Execution** and **ASI08 is Cascading
  Failures**. The plan used them for "unsafe autonomous action" and "cost
  exhaustion". Fixed in cheat sheet 2, `CHECK-SPECS.md` and D06.
- ATLAS: the plan's "v2026.09, 120 techniques" is out of date. Pinned v2026.10 has
  16 tactics, 101 techniques, 69 sub-techniques.

## Convention

Each sheet states its verification status at the top and a claim-provenance line
at the bottom. "Unverified" content must not be quoted to customers (plan §16).
