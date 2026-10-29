"""Tests for the statistics module (W2-4). Values checked against known results."""

from __future__ import annotations

import math

import pytest

from assure_core.stats import mcnemar_exact, paired_bootstrap, wilson_interval


# ---------------- Wilson interval ----------------

def test_wilson_known_value_90_of_100():
    # 90/100 at 95% -> standard reference ~ (0.825, 0.945); plan quotes ~+-6 pts.
    low, high = wilson_interval(90, 100, 0.95)
    assert low == pytest.approx(0.8238, abs=0.002)
    assert high == pytest.approx(0.9445, abs=0.002)


def test_wilson_half():
    low, high = wilson_interval(50, 100, 0.95)
    # symmetric around 0.5
    assert (low + high) / 2 == pytest.approx(0.5, abs=1e-9)
    assert low == pytest.approx(0.4038, abs=0.002)


def test_wilson_bounds_clamped():
    low, high = wilson_interval(100, 100, 0.95)
    assert high <= 1.0
    assert low > 0.0
    low0, high0 = wilson_interval(0, 100, 0.95)
    assert low0 == 0.0


def test_wilson_n_zero():
    assert wilson_interval(0, 0) == (0.0, 1.0)


def test_wilson_invalid():
    with pytest.raises(ValueError):
        wilson_interval(5, 3)


def test_wilson_lower_bound_is_what_we_gate_on():
    # The whole point (plan §7): lower bound < point estimate.
    low, high = wilson_interval(95, 100, 0.95)
    assert low < 0.95 < high


# ---------------- McNemar exact ----------------

def test_mcnemar_no_discordant():
    assert mcnemar_exact(0, 0) == 1.0


def test_mcnemar_symmetric_high_p():
    # equal flips -> no evidence of difference
    assert mcnemar_exact(5, 5) == pytest.approx(1.0, abs=1e-9)


def test_mcnemar_known_value():
    # b=1, c=9, n=10: two-sided exact p = 2 * P(X<=1) = 2*(C(10,0)+C(10,1))*0.5^10
    expected = 2 * (1 + 10) * (0.5**10)
    assert mcnemar_exact(1, 9) == pytest.approx(expected, abs=1e-12)
    assert mcnemar_exact(1, 9) < 0.05  # significant


def test_mcnemar_all_one_direction():
    # b=0, c=8 -> p = 2 * 0.5^8
    assert mcnemar_exact(0, 8) == pytest.approx(2 * (0.5**8), abs=1e-12)


def test_mcnemar_capped_at_one():
    assert mcnemar_exact(4, 5) <= 1.0


def test_mcnemar_invalid():
    with pytest.raises(ValueError):
        mcnemar_exact(-1, 2)


# ---------------- paired bootstrap ----------------

def test_bootstrap_zero_difference():
    scores = [0.8, 0.9, 0.7, 0.85, 0.95]
    mean_diff, low, high = paired_bootstrap(scores, scores, resamples=2000, seed=1)
    assert mean_diff == pytest.approx(0.0, abs=1e-9)
    assert low == pytest.approx(0.0, abs=1e-9)
    assert high == pytest.approx(0.0, abs=1e-9)


def test_bootstrap_positive_improvement():
    baseline = [0.5] * 20
    candidate = [0.7] * 20  # uniformly +0.2
    mean_diff, low, high = paired_bootstrap(baseline, candidate, resamples=2000, seed=1)
    assert mean_diff == pytest.approx(0.2, abs=1e-9)
    assert low == pytest.approx(0.2, abs=1e-9)  # no variance -> tight CI


def test_bootstrap_ci_contains_mean():
    baseline = [0.6, 0.7, 0.5, 0.8, 0.65, 0.55, 0.75, 0.6]
    candidate = [0.65, 0.72, 0.58, 0.79, 0.7, 0.6, 0.74, 0.66]
    mean_diff, low, high = paired_bootstrap(baseline, candidate, resamples=5000, seed=42)
    assert low <= mean_diff <= high


def test_bootstrap_deterministic_with_seed():
    b = [0.4, 0.6, 0.5, 0.7]
    c = [0.5, 0.65, 0.55, 0.8]
    r1 = paired_bootstrap(b, c, resamples=1000, seed=7)
    r2 = paired_bootstrap(b, c, resamples=1000, seed=7)
    assert r1 == r2


def test_bootstrap_length_mismatch():
    with pytest.raises(ValueError):
        paired_bootstrap([0.1, 0.2], [0.1])


def test_bootstrap_empty():
    with pytest.raises(ValueError):
        paired_bootstrap([], [])



# ---------------- Cohen's kappa ----------------

from assure_core.stats import cohen_kappa  # noqa: E402


def test_kappa_perfect_agreement():
    assert cohen_kappa([1, 0, 1, 0], [1, 0, 1, 0]) == pytest.approx(1.0)


def test_kappa_chance_agreement_is_zero():
    # each rater 50/50, observed agreement 0.5 == expected 0.5 -> kappa 0
    assert cohen_kappa([1, 1, 0, 0], [1, 0, 1, 0]) == pytest.approx(0.0)


def test_kappa_known_textbook_value():
    # 2x2 table: a=20 both yes, b=5 A yes/B no, c=10 A no/B yes, d=15 both no
    # p_o = 35/50 = 0.70; p_e = (25*30 + 25*20)/2500 = 0.50; kappa = 0.40
    a = [1] * 20 + [1] * 5 + [0] * 10 + [0] * 15
    b = [1] * 20 + [0] * 5 + [1] * 10 + [0] * 15
    assert cohen_kappa(a, b) == pytest.approx(0.40)


def test_kappa_total_disagreement_negative():
    assert cohen_kappa([1, 0, 1, 0], [0, 1, 0, 1]) == pytest.approx(-1.0)


def test_kappa_length_mismatch():
    with pytest.raises(ValueError):
        cohen_kappa([1], [1, 0])
