# Judge study (W3-2 / W3-3 / W4-2)

- Judge model: `qwen/qwen3.8-27b`; system under test: `openai/gpt-oss-20b` (different families).
- Runs: 3, temperature 0. Pass threshold: score >= 0.5.

| Judge | Items | Run means | Range (pts) | Verdict flips | Within 5 pts? |
|---|---|---|---|---|---|
| key_facts | 39 | [0.256, 0.256, 0.256] | 0.0 | 0 | yes |
| groundedness | 30 | [0.828, 0.828, 0.828] | 0.0 | 0 | yes |
| domain_assert | 28 | [0.411, 0.411, 0.411] | 0.0 | 0 | yes |

## Cost per run

| Run | Calls | Prompt tokens | Completion tokens | Seconds |
|---|---|---|---|---|
| 1 | 97 | 42409 | 6207 | 317.7 |
| 2 | 97 | 42409 | 6212 | 376.2 |
| 3 | 97 | 42409 | 6215 | 375.6 |

Average per run: 42409 prompt + 6211 completion tokens. Groq free tier: $0. To price a paid tier, multiply by the provider's current per-token rate (not hard-coded here because rates change).

## Calibration status

Human labels are required before any judge can gate (plan section 7). Fill `human_pass` (1/0) in `results\calibration_sheet.csv` for at least 30 rows, then run `python -m harness.judge_study kappa`.
