"""
harness/judge_study.py  -  W3-2 / W3-3 / W4-2 over the real BoK answers.

Reads the answers saved by run_bok_full.py (results/bok_full_cases.jsonl), so
judges grade exactly the answers the deterministic checks saw.

  run    - for every case with gold_key_facts or a judgeable assert tag:
             key_facts_judge, groundedness_judge (answer cases), and
             domain_assert_judge per assert tag,
           each repeated RUNS times (default 3) -> variance study (W4-2),
           token usage summed -> cost per run (W4-2),
           writes results/judge_scores.json, results/judge_study.md,
           results/calibration_sheet.csv (for human labels, W3-3),
           and merges soft metrics into results/bok_full_metrics.json.

  kappa  - after a human fills `human_pass` (1/0) in calibration_sheet.csv,
           computes Cohen's kappa judge-vs-human and writes results/kappa.md.

RUN:
    $env:PYTHONUTF8=1
    assure-core\\.venv\\Scripts\\python.exe -m harness.judge_study run 3
    assure-core\\.venv\\Scripts\\python.exe -m harness.judge_study kappa
"""

from __future__ import annotations

import csv
import json
import statistics
import sys
import time
from pathlib import Path

import mlflow

from assure_core.datasets import load_dataset
from assure_core.stats import cohen_kappa
from harness import model_client
from harness.bok_corpus_loader import load_documents
from harness.judges import (DETERMINISTIC_ASSERTS, USAGE_TOTALS, domain_assert_judge,
                            groundedness_judge, key_facts_judge)

CASES = Path("results/bok_full_cases.jsonl")
DATASET = "assure-core/datasets/golden-bok-v1.json"
SCORES = Path("results/judge_scores.json")
REPORT = Path("results/judge_study.md")
SHEET = Path("results/calibration_sheet.csv")
METRICS = Path("results/bok_full_metrics.json")
KAPPA = Path("results/kappa.md")
PASS_AT = 0.5   # a judge score >= 0.5 counts as "pass" for pass-rates and kappa
PACE_S = 0.6


def _items(answers: dict, golden: dict, docs: dict) -> list[dict]:
    """Build the list of (case, judge, target) items to score."""
    items = []
    for cid, rec in answers.items():
        exp = golden[cid]["expectations"]
        deferred = exp.get("_deferred", {})
        answer = str(rec.get("answer") or "")
        if deferred.get("gold_key_facts") and exp["d08_expected_behavior"] == "answer":
            items.append({"id": cid, "judge": "key_facts", "target": "",
                          "args": (answer, deferred["gold_key_facts"])})
            if answer.strip():
                retrieved = [docs[d]["text"] for d in rec["retrieved_ids"] if d in docs]
                items.append({"id": cid, "judge": "groundedness", "target": "",
                              "args": (answer, retrieved)})
        for tag in deferred.get("assert", []):
            if tag not in DETERMINISTIC_ASSERTS:
                items.append({"id": cid, "judge": "domain_assert", "target": tag,
                              "args": (answer, tag)})
    return items


def _score(item: dict):
    fn = {"key_facts": key_facts_judge, "groundedness": groundedness_judge,
          "domain_assert": domain_assert_judge}[item["judge"]]
    return fn(*item["args"])


def run(runs: int = 3) -> None:
    answers = {json.loads(l)["id"]: json.loads(l) for l in CASES.read_text(encoding="utf-8").splitlines() if l.strip()}
    golden = {c["id"]: c for c in load_dataset(DATASET)}
    docs = load_documents()
    items = _items(answers, golden, docs)
    judge = model_client.judge_model_name()
    print(f"Judge {judge} (system under test: {model_client.model_name()}) | "
          f"{len(items)} items x {runs} runs\n")

    per_run_usage = []
    for r in range(runs):
        before = dict(USAGE_TOTALS)
        t0 = time.time()
        for it in items:
            time.sleep(PACE_S)
            res = _score(it)
            it.setdefault("scores", []).append(None if res is None else res.score)
            it.setdefault("rationales", []).append(None if res is None else res.rationale)
        per_run_usage.append({
            "calls": USAGE_TOTALS["calls"] - before["calls"],
            "prompt_tokens": USAGE_TOTALS["prompt_tokens"] - before["prompt_tokens"],
            "completion_tokens": USAGE_TOTALS["completion_tokens"] - before["completion_tokens"],
            "seconds": round(time.time() - t0, 1),
        })
        print(f"  run {r + 1}: {per_run_usage[-1]}")

    # --- aggregate per judge type, per run ---
    summary = {}
    for jt in ("key_facts", "groundedness", "domain_assert"):
        its = [i for i in items if i["judge"] == jt]
        if not its:
            continue
        run_means = [statistics.mean(i["scores"][r] for i in its) for r in range(runs)]
        run_pass = [sum(i["scores"][r] >= PASS_AT for i in its) for r in range(runs)]
        flips = sum(1 for i in its if len({s >= PASS_AT for s in i["scores"]}) > 1)
        summary[jt] = {
            "n": len(its),
            "run_means": [round(m, 3) for m in run_means],
            "mean": round(statistics.mean(run_means), 3),
            "range_points": round((max(run_means) - min(run_means)) * 100, 1),
            "pass_counts": run_pass,
            "items_flipping_verdict": flips,
        }

    # median-of-runs verdict per item (plan: run 3x, take the median)
    for it in items:
        it["median"] = statistics.median(it["scores"])
        it["judge_pass"] = int(it["median"] >= PASS_AT)

    SCORES.write_text(json.dumps({"judge_model": judge, "runs": runs, "summary": summary,
                                  "usage_per_run": per_run_usage,
                                  "items": [{k: v for k, v in i.items() if k != "args"} for i in items]},
                                 indent=2, ensure_ascii=False), encoding="utf-8")

    # --- merge soft metrics (median verdicts) into the gate metrics file ---
    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    for jt in summary:
        its = [i for i in items if i["judge"] == jt]
        metrics[jt] = [sum(i["judge_pass"] for i in its), len(its)]
    METRICS.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    # --- calibration sheet for humans (W3-3) ---
    with SHEET.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "judge", "target", "question", "answer", "requirement",
                    "judge_score_median", "judge_pass", "judge_rationale", "human_pass"])
        for it in items:
            req = (" | ".join(golden[it["id"]]["expectations"]["_deferred"].get("gold_key_facts", []))
                   if it["judge"] == "key_facts" else
                   "answer supported by retrieved docs" if it["judge"] == "groundedness" else it["target"])
            w.writerow([it["id"], it["judge"], it["target"], answers[it["id"]]["question"],
                        str(answers[it["id"]].get("answer") or "")[:600], req,
                        it["median"], it["judge_pass"], (it["rationales"][0] or "")[:200], ""])

    # --- markdown report (W4-2) ---
    lines = [f"# Judge study (W3-2 / W3-3 / W4-2)", "",
             f"- Judge model: `{judge}`; system under test: `{model_client.model_name()}` (different families).",
             f"- Runs: {runs}, temperature 0. Pass threshold: score >= {PASS_AT}.", "",
             "| Judge | Items | Run means | Range (pts) | Verdict flips | Within 5 pts? |",
             "|---|---|---|---|---|---|"]
    for jt, s in summary.items():
        lines.append(f"| {jt} | {s['n']} | {s['run_means']} | {s['range_points']} | "
                     f"{s['items_flipping_verdict']} | {'yes' if s['range_points'] <= 5 else 'NO'} |")
    tot_p = sum(u["prompt_tokens"] for u in per_run_usage) / runs
    tot_c = sum(u["completion_tokens"] for u in per_run_usage) / runs
    lines += ["", "## Cost per run", "",
              "| Run | Calls | Prompt tokens | Completion tokens | Seconds |", "|---|---|---|---|---|"]
    for i, u in enumerate(per_run_usage, 1):
        lines.append(f"| {i} | {u['calls']} | {u['prompt_tokens']} | {u['completion_tokens']} | {u['seconds']} |")
    lines += ["", f"Average per run: {tot_p:.0f} prompt + {tot_c:.0f} completion tokens. "
              "Groq free tier: $0. To price a paid tier, multiply by the provider's current "
              "per-token rate (not hard-coded here because rates change).", "",
              "## Calibration status", "",
              f"Human labels are required before any judge can gate (plan section 7). "
              f"Fill `human_pass` (1/0) in `{SHEET}` for at least 30 rows, then run "
              "`python -m harness.judge_study kappa`."]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("BoK-Judges-W3-2")
    with mlflow.start_run(run_name=f"judge-study-x{runs}"):
        mlflow.log_params({"judge_model": judge, "runs": runs, "items": len(items)})
        for jt, s in summary.items():
            mlflow.log_metric(f"{jt}_mean", s["mean"])
            mlflow.log_metric(f"{jt}_range_points", s["range_points"])
        mlflow.log_metric("tokens_per_run", tot_p + tot_c)
        mlflow.log_artifact(str(REPORT))
        mlflow.log_artifact(str(SHEET))

    print("\n" + REPORT.read_text(encoding="utf-8"))


def kappa() -> None:
    rows = list(csv.DictReader(SHEET.open(encoding="utf-8")))
    labelled = [r for r in rows if r["human_pass"].strip() in ("0", "1")]
    if len(labelled) < 30:
        print(f"Only {len(labelled)} rows labelled; plan section 7 needs >= 30. "
              f"Fill human_pass (1/0) in {SHEET}.")
        sys.exit(2)
    lines = ["# Judge calibration (Cohen's kappa, judge vs human)", "",
             "| Judge | Labelled | Agreement | Kappa | Can gate (kappa >= 0.6)? |", "|---|---|---|---|---|"]
    for jt in sorted({r["judge"] for r in labelled}):
        sub = [r for r in labelled if r["judge"] == jt]
        j = [int(r["judge_pass"]) for r in sub]
        h = [int(r["human_pass"]) for r in sub]
        k = cohen_kappa(j, h)
        agree = sum(a == b for a, b in zip(j, h)) / len(sub)
        lines.append(f"| {jt} | {len(sub)} | {agree:.0%} | {k:.2f} | {'yes' if k >= 0.6 else 'no'} |")
    KAPPA.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(KAPPA.read_text(encoding="utf-8"))


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "kappa":
        kappa()
    else:
        run(int(sys.argv[2]) if len(sys.argv) >= 3 else 3)
