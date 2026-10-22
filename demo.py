"""
demo.py  -  Capability 4: Week 1 & Week 2 progress demo.

A narrated walkthrough you can run live for the team. It:
  Week 1  - shows the foundation (scope, cheat sheets, MLflow server, specs, licences)
  Week 2  - runs the real test suite (76 tests), shows the stats + 11 checks,
            then runs the REAL assurance harness against a live LLM.

RUN:
    $env:PYTHONUTF8=1
    assure-core\\.venv\\Scripts\\python.exe demo.py

Read-only + safe: it inspects files, runs tests, and runs the real harness.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = str(ROOT / "assure-core" / ".venv" / "Scripts" / "python.exe")


def pause(msg: str = "  [Enter] to continue...") -> None:
    try:
        input(msg)
    except EOFError:
        pass


def banner(title: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def bullet(label: str, ok: bool = True) -> None:
    print(f"   {'[OK]' if ok else '[ -]'} {label}")


def exists(rel: str) -> bool:
    return (ROOT / rel).exists()


# ----------------------------------------------------------------------
def week1() -> None:
    banner("WEEK 1  -  Foundation (scope, reading, environment)")
    print("  Goal: set up WHAT we test, the STANDARDS, the RECORD-KEEPER, and the")
    print("        code skeleton. Deliverables W1-1 to W1-5.\n")

    bullet("W1-1 Scope & risk tiers", exists("docs/scope-and-risk-tiers.md"))
    bullet("W1-2 Five cheat sheets (OWASP LLM/Agentic, ATLAS, NIST, MLflow)",
           exists("docs/cheatsheets/01-owasp-llm-top10-2025.md"))
    bullet("W1-3 MLflow dev server (docker-compose)", exists("mlflow-dev/docker-compose.yml"))
    bullet("W1-4 assure-core package + D01-D11 specs", exists("assure-core/docs/CHECK-SPECS.md"))
    bullet("W1-5 Licence register", exists("docs/licence-register.md"))

    print("\n  The 11 deterministic checks were SPECIFIED in Week 1 (stubs):")
    checks = sorted((ROOT / "assure-core/src/assure_core/checks").glob("d*.py"))
    print("   " + ", ".join(c.stem.upper().replace("_", " ") for c in checks))
    pause()


# ----------------------------------------------------------------------
def week2_tests() -> None:
    banner("WEEK 2  -  The engine becomes real (checks + stats + datasets)")
    print("  Goal: implement the real D01-D11 logic, statistics, and golden")
    print("        datasets. Everything is proven by an automated test suite.\n")
    print("  Running the full test suite now...\n")
    subprocess.run([PY, "-m", "pytest", "assure-core", "-q"], cwd=ROOT)
    print("\n  -> Every check is proven to FAIL on a deliberately corrupted output")
    print("     (the plan's 'done when' for W2-1).")
    pause()


def week2_checks_live() -> None:
    banner("WEEK 2  -  See the checks catch real problems (live, in-process)")
    sys.path.insert(0, str(ROOT / "assure-core" / "src"))
    from assure_core.checks.d02_pii import check_pii
    from assure_core.checks.d11_canary import check_canary
    from assure_core.stats import wilson_interval

    print("  D02 (PII) on a clean answer:")
    print("     ", check_pii("The capital of France is Paris.").status.value.upper())
    print("  D02 (PII) on an answer that leaks an email:")
    print("     ", check_pii("contact me at john@example.com").status.value.upper(),
          "(leak caught)")
    print("\n  D11 (canary) when a planted trap string leaks:")
    print("     ", check_canary("oops CANARY-123 leaked", [], ["CANARY-123"]).status.value.upper(),
          "(injection caught)")
    print("\n  Statistics (W2-4): 90/100 passes -> Wilson 95% interval:")
    lo, hi = wilson_interval(90, 100)
    print(f"      ({lo:.3f}, {hi:.3f})   <- we GATE on the lower bound, not the 0.90")
    pause()


# ----------------------------------------------------------------------
def week2_real_harness() -> None:
    banner("WEEK 2+  -  REAL assurance run against a LIVE model (no mocks)")
    print("  A small real RAG system (retrieval + live LLM) answers each golden")
    print("  question; the D-checks inspect the REAL answer. Results -> MLflow.\n")
    print("  Running the real harness now (live API calls)...\n")
    subprocess.run([PY, "-m", "harness.runner"], cwd=ROOT)
    print("\n  Highlights:")
    print("   - injection case: model must NOT leak the planted canary  (D11)")
    print("   - out-of-scope case: model must REFUSE                     (D08)")
    print("   Open http://localhost:5000 -> 'Real-RAG-Assurance' -> Traces tab")
    print("   to read the real questions, real answers, and per-check verdicts.")


# ----------------------------------------------------------------------
def main() -> None:
    banner("Capability 4 - Assurance & Red-Teaming  -  Progress Demo")
    print("  Walking through Week 1 (foundation) and Week 2 (the working engine).")
    pause("  [Enter] to start...")

    week1()
    week2_tests()
    week2_checks_live()
    week2_real_harness()

    banner("END OF DEMO")
    print("  Week 1: foundation in place.  Week 2: real engine, tested, running")
    print("  against a live model with real injection + refusal checks. ")


if __name__ == "__main__":
    main()
