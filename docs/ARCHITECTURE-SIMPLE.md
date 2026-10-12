# Capability 4 — Assurance & Red-Teaming: Simple Architecture

A one-page explainer for the team. Goal: understand **what we build**, **how it
flows**, and **how it decides if an AI is safe to release**.

---

## 1. The end goal (in one line)

> A repeatable **"SAFE TO RELEASE?"** stamp for our AI systems — automatic, with
> evidence a risk team will trust.

Think of it as a **crash-test lab for AI**. Before an AI ships, we test it,
score it, attack it, and produce a safety report.

---

## 2. The two halves of what we do

```
   ┌───────────────────────────┐     ┌───────────────────────────┐
   │        ASSURANCE          │     │        RED-TEAMING         │
   │  "Does it work right on    │     │  "Can an attacker break    │
   │   what we EXPECT?"         │     │   it in ways we DON'T       │
   │                            │     │   expect?"                 │
   │  • golden Q&A dataset      │     │  • 50 attack cases (Nov)   │
   │  • D01–D11 fixed checks    │     │  • injection, data leak,   │
   │  • runs ALL the time       │     │    jailbreak, tool misuse  │
   │                            │     │  • runs before releases    │
   └───────────────────────────┘     └───────────────────────────┘
                 \                               /
                  \                             /
                   ▼                           ▼
             both feed into the SAME record + gate + report
```

---

## 3. Who uses it (the audience)

```
   AI Developers        Risk / Compliance        External Clients
  (Cap 2 & Cap 3)             Team                  (from Dec)
        │                      │                        │
   "Can I ship            "Prove it's safe,        "Audit my AI
    my change?"            with evidence"            system"
        │                      │                        │
        ▼                      ▼                        ▼
   fast PASS/FAIL         formal report with        Health Check
   in their pipeline      framework mapping          service
```

---

## 4. THE CORE ARCHITECTURE (the big picture)

```
                        ┌──────────────────────────────┐
                        │        INPUTS                 │
                        │                               │
   ┌───────────────┐    │  • Golden dataset             │
   │  AI under     │    │    (questions + known answers)│
   │  test:        │    │  • Sealed set (secret, anti-  │
   │  • BoK (RAG)  │───▶│    cheat, held by assurance)  │
   │  • Agent      │    │  • Policy file (the rules)    │
   └───────────────┘    └───────────────┬───────────────┘
         │ emits                         │
         │ traces                        ▼
         │              ┌────────────────────────────────┐
         │              │        THE HARNESS              │
         │              │   (the conductor script)        │
         │              │                                 │
         │              │  for each question:             │
         │              │   1. run the AI                 │
         │              │   2. apply DETERMINISTIC checks │
         │              │      D01–D11  (HARD gate)       │
         │              │   3. apply LLM JUDGES (soft)    │
         │              └───────────────┬─────────────────┘
         │                              │ results
         ▼                              ▼
   ┌─────────────────────────────────────────────────────┐
   │                 MLflow  (SYSTEM OF RECORD)           │
   │   stores: traces · runs · metrics · datasets         │
   │   this is the webpage you saw at localhost:5000      │
   └───────────────────────────┬─────────────────────────┘
                                │
                                ▼
   ┌─────────────────────────────────────────────────────┐
   │                   THE GATE  (decision)               │
   │   compares to BASELINE using statistics, then:       │
   │                                                      │
   │     deterministic check failed? ──▶ ❌ BLOCK          │
   │     judge score dropped a lot?  ──▶ ⚠️ REVIEW         │
   │     all good?                   ──▶ ✅ PASS           │
   │     something broken/unknown?   ──▶ ❌ FAIL (closed)  │
   └───────────────────────────┬─────────────────────────┘
                                │
                                ▼
   ┌─────────────────────────────────────────────────────┐
   │                    THE REPORT                        │
   │   • JUnit XML  → CI pipeline blocks/allows release   │
   │   • Markdown/PDF → humans: results, severity,        │
   │     evidence, limits, RELEASE RECOMMENDATION         │
   └─────────────────────────────────────────────────────┘
```

---

## 5. THE 9-STEP FLOW (section 2 of the plan)

```
  1. SCOPE      pick targets + risk tier + owner        (BoK=T2, Agent=T1)
      ▼
  2. TRACE      make the AI record everything it does
      ▼
  3. DATASET    build golden Q&A; split dev (visible) + sealed (secret)
      ▼
  4. RUN        harness: dataset × D01–D11 checks × judges → MLflow
      ▼
  5. COMPARE    stats vs the stored baseline (real drop or just noise?)
      ▼
  6. GATE       policy decides: PASS / FAIL / REVIEW   (deterministic = hard)
      ▼
  7. ATTACK     red-team library probes what the golden set misses
      ▼
  8. REPORT     results + uncertainty + limits + release recommendation
      ▼
  9. RETEST     every fix adds a regression case → can't silently return
```

---

## 6. KEY DESIGN RULE (the smart part — explain this to the team)

```
   ┌────────────────────────────┬────────────────────────────┐
   │   DETERMINISTIC CHECKS       │        LLM JUDGES          │
   │   (D01–D11)                  │   (Safety, quality, etc.)  │
   ├────────────────────────────┼────────────────────────────┤
   │  same answer every time      │  drift when model updates  │
   │  free                        │  cost money                │
   │  auditable                   │  can disagree with itself  │
   │                              │                            │
   │  ►►  HARD GATE  ◄◄            │  ►►  SOFT SIGNAL  ◄◄        │
   │  a failure BLOCKS release    │  only warns / trends       │
   └────────────────────────────┴────────────────────────────┘

   RULE:  Hard gate = deterministic.  Judges trend & flag for review.
          A judge can block only when statistics PROVE a real drop.
```

Why: we never block (or allow) a release on a guess. The hard decisions use
rules that are reproducible and auditable; the fuzzy AI opinions only advise.

---

## 7. The deterministic checks D01–D11 (the "safety rules")

| ID | Checks that... | Blocks release? |
|----|----------------|-----------------|
| D01 | output is in the right format | ✅ hard |
| D02 | no personal data (PII) leaked | ✅ hard |
| D03 | no secrets / banned words | ✅ hard |
| D04 | citations are real and accurate | ✅ hard |
| D05 | agent only called allowed tools | ✅ hard |
| D06 | within time / token / cost budget | threshold |
| D07 | answer in the expected language | threshold |
| D08 | refused for the right reason | ✅ hard |
| D09 | no unexplained change vs last run | threshold |
| D10 | retrieved the right document | threshold |
| D11 | no prompt-injection "canary" leaked | ✅ hard |

---

## 8. One real story (follow a change through the system)

```
  Developer changes agent code
          │
          ▼
  Opens a Pull Request  ──▶  harness auto-runs fast checks
          │
          ▼
  D11 (injection canary) FAILS  — hidden instruction triggered a bad tool call
          │
          ▼
  GATE: ❌ BLOCK.  Developer sees the exact case + the trace evidence
          │
          ▼
  Developer fixes it  +  a NEW regression case is added for this attack
          │
          ▼
  Re-run ──▶ ✅ PASS.  At release: sealed set + full red-team run
          │
          ▼
  All pass ──▶ GATE allows release ──▶ MLflow saves this as new BASELINE
          │
          ▼
  REPORT: what was tested, fixed, and "recommended for release"
```

The developer never had to judge safety by hand — the machinery did, with proof.

---

## 9. What we have vs. what's next

```
  ✅ DONE (Week 1)                    ⬜ COMING
  ───────────────                    ─────────
  • Scope & risk tiers                • Check LOGIC (D01–D11)   → Week 2
  • MLflow record (running)           • Golden dataset           → Week 2
  • Check SPECS (recipes)             • Statistics               → Week 2
  • Licence register                  • Harness + judges         → Week 3
  • Reading cheat sheets              • CI gate (auto block)     → Week 4 / Nov
                                      • 50 red-team cases        → Nov
                                      • First report + offer     → Dec
```

We've built the **foundation + record-keeper**. Next we add the **brains**
(checks + stats), the **conductor** (harness), the **attacker** (red-team),
and the **gatekeeper** (CI).

---

## 10. The 10-second summary for the team

```
  ASSURANCE  = test the EXPECTED  (golden dataset + fixed checks + judges)
  RED-TEAM   = attack the UNEXPECTED  (50 severity-scored attack cases)
  BOTH  →  MLflow (record)  →  GATE (decide)  →  REPORT (prove)
  GOAL  =  a trustworthy, repeatable "SAFE TO RELEASE?" with evidence
```
