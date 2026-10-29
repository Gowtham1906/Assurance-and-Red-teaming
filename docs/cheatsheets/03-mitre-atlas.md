# Cheat Sheet 3 — MITRE ATLAS

**One-pager for Capability 4.** Adversarial-AI attack taxonomy; every red-team case pins an ATLAS version.
**Official sources:** https://atlas.mitre.org · data: https://github.com/mitre-atlas/atlas-data
**Verification status:** ✅ **Verified 2026-10-29** from MITRE's published data file (`dist/ATLAS.yaml`) via `harness/probe_atlas.py`.
**Pinned version:** **ATLAS release v2026.10** (published 2026-10-28), data schema version 5.6.0.
**Second reader:** Gowtham · **Date:** 2026-10-29

---

## What ATLAS is

ATLAS (Adversarial Threat Landscape for Artificial-Intelligence Systems) applies
MITRE ATT&CK's structure to AI: **tactics** (the attacker's goal at a stage) and
**techniques** (how they achieve it), each with a stable ID like `AML.T0051`.

## Size of the pinned version

| | Count (v2026.10) |
|---|---|
| Tactics | 16 |
| Techniques | 101 |
| Sub-techniques | 69 |

The plan quoted "v2026.09, 16 tactics, 120 techniques" from one secondary source.
That version was superseded on 28 Oct 2026, and "120" matched neither the
technique count (101) nor the total with sub-techniques (170).

## Techniques we map to (all IDs confirmed present in v2026.10)

| Technique ID | Name | Our cases / checks |
|---|---|---|
| `AML.T0051` | LLM Prompt Injection | direct + indirect injection; D11, D08 refuse_injection |
| `AML.T0054` | LLM Jailbreak | jailbreak cases |
| `AML.T0057` | LLM Data Leakage | PII / restricted-doc leakage; D02, forbidden_evidence |
| `AML.T0080` | AI Agent Context Poisoning | memory / context poisoning (ASI06) |
| `AML.T0086` | Exfiltration via AI Agent Tool Invocation | agent exfiltration; D05 |
| `AML.T0101` | Data Destruction via AI Agent Tool Invocation | unsafe destructive tool use; D05 forbidden sequences |

## How we use it

- Every red-team case records **`atlas_version: v2026.10`** plus technique IDs.
- Re-run `python -m harness.probe_atlas` before each release of the case library;
  if the tag changes, review mappings and bump the pin.

**Claim provenance:** all counts, names and IDs read programmatically from MITRE's `ATLAS.yaml` at release v2026.10.
