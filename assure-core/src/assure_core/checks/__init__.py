"""Deterministic checks D01-D11 (plan §6).

Week 1 (W1-4): each module is a STUB. The function signature and docstring spec
are fixed now; implementation lands in Week 2 (W2-1) with positive, negative,
mutation and property tests.

HARD-gate checks (a failure blocks release, plan §8): D01, D02, D03, D04, D05,
D08, D11. SOFT/threshold checks: D06, D07, D09, D10 (gate on budgets/baselines).
"""

CHECK_IDS = [
    "D01", "D02", "D03", "D04", "D05", "D06",
    "D07", "D08", "D09", "D10", "D11",
]
