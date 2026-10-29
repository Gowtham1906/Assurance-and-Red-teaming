"""Statistics module (plan §7).

Three tools, standard methods, pure-Python (stdlib only):

    wilson_interval(successes, n, confidence=0.95) -> (low, high)
        Confidence interval for a binomial proportion (better than normal
        approximation at small n). We GATE ON THE LOWER BOUND (plan §7).

    mcnemar_exact(b, c) -> p_value
        Exact (binomial) McNemar test for PAIRED binary outcomes.
        b = # cases baseline PASS but candidate FAIL
        c = # cases baseline FAIL but candidate PASS

    paired_bootstrap(baseline, candidate, resamples=10000, confidence=0.95, seed=0)
        -> (mean_diff, low, high)
        Bootstrap CI for the mean paired score difference (candidate - baseline).

Design rule (plan §7): gate on the LOWER BOUND of the interval, not the point
estimate.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence

# Two-sided z critical values for common confidence levels.
_Z = {0.90: 1.6448536269514722, 0.95: 1.959963984540054, 0.99: 2.5758293035489004}


def _z_for(confidence: float) -> float:
    if confidence in _Z:
        return _Z[confidence]
    # Fallback: inverse normal via a rational approximation (Acklam).
    return _inv_norm_cdf(1.0 - (1.0 - confidence) / 2.0)


def wilson_interval(
    successes: int, n: int, confidence: float = 0.95
) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion.

    Returns (low, high), each in [0, 1]. At n=0 returns (0.0, 1.0).
    """
    if successes < 0 or n < 0 or successes > n:
        raise ValueError("require 0 <= successes <= n")
    if n == 0:
        return (0.0, 1.0)

    z = _z_for(confidence)
    p = successes / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (p + z2 / (2 * n)) / denom
    margin = (z * math.sqrt((p * (1 - p) + z2 / (4 * n)) / n)) / denom
    low = max(0.0, center - margin)
    high = min(1.0, center + margin)
    # Clamp tiny floating-point residuals (e.g. 3e-18) to exact bounds.
    if low < 1e-12:
        low = 0.0
    if high > 1.0 - 1e-12:
        high = 1.0
    return (low, high)


def mcnemar_exact(b: int, c: int) -> float:
    """Exact McNemar test p-value (two-sided) using the binomial distribution.

    Only the discordant pairs (b, c) matter. Under H0 each discordant pair is
    equally likely to flip either way, i.e. Binomial(n=b+c, p=0.5).
    Returns a p-value in [0, 1]. If b + c == 0, returns 1.0 (no evidence).
    """
    if b < 0 or c < 0:
        raise ValueError("b and c must be non-negative")
    n = b + c
    if n == 0:
        return 1.0

    k = min(b, c)
    # Two-sided exact p = 2 * P(X <= k), capped at 1.0.
    cumulative = sum(math.comb(n, i) for i in range(k + 1)) * (0.5**n)
    return min(1.0, 2.0 * cumulative)


def paired_bootstrap(
    baseline: Sequence[float],
    candidate: Sequence[float],
    resamples: int = 10000,
    confidence: float = 0.95,
    seed: int = 0,
) -> tuple[float, float, float]:
    """Percentile bootstrap CI for the mean paired difference (candidate - baseline).

    Returns (mean_diff, low, high). Pairs are resampled together (paired design).
    """
    if len(baseline) != len(candidate):
        raise ValueError("baseline and candidate must have equal length")
    n = len(baseline)
    if n == 0:
        raise ValueError("need at least one pair")

    diffs = [candidate[i] - baseline[i] for i in range(n)]
    mean_diff = sum(diffs) / n

    rng = random.Random(seed)
    boot_means = []
    for _ in range(resamples):
        total = 0.0
        for _ in range(n):
            total += diffs[rng.randrange(n)]
        boot_means.append(total / n)
    boot_means.sort()

    alpha = 1.0 - confidence
    low = boot_means[max(0, int((alpha / 2.0) * resamples))]
    high = boot_means[min(resamples - 1, int((1.0 - alpha / 2.0) * resamples))]
    return (mean_diff, low, high)


def cohen_kappa(rater_a: Sequence, rater_b: Sequence) -> float:
    """Cohen's kappa for two raters over the same items (any hashable labels).

    kappa = (p_o - p_e) / (1 - p_e). Returns 1.0 when both raters give the same
    single label to every item (p_e == 1). Used for judge calibration: the plan
    uses kappa >= 0.6 between judge and human consensus as a working threshold.
    """
    if len(rater_a) != len(rater_b):
        raise ValueError("raters must label the same number of items")
    n = len(rater_a)
    if n == 0:
        raise ValueError("need at least one item")
    p_o = sum(1 for a, b in zip(rater_a, rater_b) if a == b) / n
    labels = set(rater_a) | set(rater_b)
    p_e = sum((list(rater_a).count(lab) / n) * (list(rater_b).count(lab) / n)
              for lab in labels)
    if p_e == 1.0:
        return 1.0
    return (p_o - p_e) / (1.0 - p_e)


def _inv_norm_cdf(p: float) -> float:
    """Inverse standard-normal CDF (Acklam's algorithm). Used only for odd confidences."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0, 1)")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p <= phigh:
        q = p - 0.5
        r = q*q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    q = math.sqrt(-2 * math.log(1 - p))
    return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
            ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)


__all__ = ["wilson_interval", "mcnemar_exact", "paired_bootstrap", "cohen_kappa"]
