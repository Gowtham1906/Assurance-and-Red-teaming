"""Statistics module (plan §7) — IMPLEMENTED IN WEEK 2 (W2-4).

Planned functions:
    wilson_interval(successes, n, confidence)       -> (low, high)
    mcnemar_exact(b, c)                             -> p-value
    paired_bootstrap(diffs, resamples=10_000)       -> (low, high)

Gate on the LOWER BOUND of the interval, not the point estimate (plan §7).
"""
