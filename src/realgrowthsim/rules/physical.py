from __future__ import annotations

import math

import numpy as np


def unique_active_marginal_effect(Ceff: float, C: float, eps_C: float, thetaP: float) -> float:
    return thetaP * Ceff / (Ceff + eps_C)


def overbuild_penalty(C: float, eps_C: float, thetaP: float) -> float:
    return -thetaP / (C + eps_C)


def deterministic_switch_time_upper_bound(h0: float, eta: float) -> float:
    if h0 <= 0 or eta <= 0:
        return math.inf
    return h0 / eta


def noisy_switch_time_moments(h0: float, eta: float, sigma: float) -> tuple[float, float]:
    if h0 <= 0 or eta <= 0:
        return math.inf, math.inf
    return h0 / eta, h0 * sigma**2 / eta**3


def lead_time_preemption_deadline(tau_switch: float, lead_quantile: float) -> float:
    return tau_switch - lead_quantile


def heavy_traffic_gain(rho_util: float, a: float, kappa: float, delta_rho: float) -> float:
    rho = min(max(rho_util, 0.0), 0.999999)
    return a * kappa * delta_rho / ((1.0 - rho) ** 2)


def tie_aware_expected_change(deltas: dict[str, float], probs: dict[str, float]) -> float:
    return float(sum(probs.get(k, 0.0) * v for k, v in deltas.items()))


def bpi_barrier_satisfied(bpi: np.ndarray, threshold: float) -> bool:
    return bool(np.nanmax(bpi) <= max(float(bpi[0]), threshold) + 1e-12)
