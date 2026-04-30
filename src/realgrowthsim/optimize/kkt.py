from __future__ import annotations

import numpy as np
from scipy.optimize import brentq


def clipped_kkt_allocation(
    impacts: dict[str, float],
    floors: dict[str, float],
    budget: float,
    psi: float = 0.75,
) -> dict[str, float]:
    """Solve max sum_j a_j s_j^psi subject to floors and sum shares = budget."""

    if not 0.0 < psi < 1.0:
        raise ValueError("psi must be in (0, 1)")
    labels = list(impacts)
    a = {label: max(float(impacts[label]), 1e-12) for label in labels}
    floor = {label: max(float(floors.get(label, 0.0)), 0.0) for label in labels}
    floor_sum = sum(floor.values())
    if budget < floor_sum - 1e-12:
        raise ValueError("budget is below share floors")
    if abs(budget - floor_sum) <= 1e-12:
        return floor

    exponent = 1.0 / (1.0 - psi)

    def total_for_lambda(lam: float) -> float:
        return sum(max(floor[label], (a[label] * psi / lam) ** exponent) for label in labels)

    low = 1e-12
    high = max(a.values()) * psi / (max(budget, 1e-12) ** (1.0 - psi))
    while total_for_lambda(high) > budget:
        high *= 2.0
    lam = brentq(lambda x: total_for_lambda(x) - budget, low, high, maxiter=200)
    shares = {label: max(floor[label], (a[label] * psi / lam) ** exponent) for label in labels}
    total = sum(shares.values())
    if not np.isclose(total, budget):
        scale = (budget - floor_sum) / max(total - floor_sum, 1e-12)
        shares = {label: floor[label] + scale * (shares[label] - floor[label]) for label in labels}
    return shares
