from __future__ import annotations

import math


def exploration_floor_gaussian(delta: float, sigma: float, horizon_T: float) -> float:
    if delta <= 0 or sigma <= 0 or horizon_T <= 1:
        return 0.0
    return 2.0 * sigma**2 * math.log(horizon_T) / (delta**2)


def coherent_diversification_bound(rho_l1: float, rho_l2: float, theta: float) -> float:
    theta = min(1.0, max(0.0, theta))
    return theta * rho_l1 + (1.0 - theta) * rho_l2
