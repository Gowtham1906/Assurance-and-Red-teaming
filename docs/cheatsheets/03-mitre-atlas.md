# Cheat Sheet 3 — MITRE ATLAS

**One-pager for Capability 4.** Adversarial-ML attack taxonomy; we pin a version in every red-team case.
**Source:** https://atlas.mitre.org
**Verification status:** ⚠️ **UNVERIFIED counts.** Plan §3 reports *one secondary source* claims **v2026.09 (15 Sep 2026), 16 tactics, 120 techniques**. The site and version MUST be checked and the exact version pinned.
**Second reader:** `____________` · **Date:** `__________`

---

## What ATLAS is

ATLAS = **A**dversarial **T**hreat **L**andscape for **A**rtificial-**I**ntelligence **S**ystems.
It is MITRE ATT&CK's structure applied to AI/ML: a matrix of **tactics**
(the attacker's goal at a stage) and **techniques** (how they achieve it).
Each technique has an ID like `AML.T0080`.

## Structure

- **Tactics** = columns (e.g., Reconnaissance, Initial Access, ML Attack Staging, Exfiltration, Impact).
- **Techniques** = cells under each tactic (the concrete methods).
- Techniques carry stable IDs; always cite **ID + ATLAS version**.

## Agent-relevant techniques we'll map to (provisional IDs from plan §3)

| Technique ID | Name (provisional) | Maps to our cases |
|--------------|--------------------|--------------------|
| `AML.T0080` | Agent Context Poisoning | Indirect injection, memory poisoning (ASI06) |
| `AML.T0086` | Exfiltration via Tool Invocation | Data exfiltration via agent tools |
| `AML.T0101` | Data Destruction via Agent Tools | Unsafe state-changing action |

---

## How we use it

- Every red-team case records: **ATLAS version** + **technique ID(s)**.
- ATLAS sits alongside OWASP (what-category) as the **how-attack** mapping.
- Refresh cases after each ATLAS release (plan §9.3).

## Watch-outs

- **Pin the version.** Technique IDs and counts change between releases;
  an unpinned citation is not auditable.
- Counts (16/120) and the three technique IDs above are **unverified** (plan §16).
  Action: open atlas.mitre.org, confirm current version, correct this sheet.

**Claim provenance:** version/counts/IDs all from plan §3 single-secondary-source note, flagged unverified in §16.
