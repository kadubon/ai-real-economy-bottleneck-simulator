from __future__ import annotations

from scipy.stats import norm

from realgrowthsim.model.equations import regulatory_gate
from realgrowthsim.model.params import InstitutionalParams


def institutional_fixed_point(a: float, b: float, lam: float, gamma: float, floor: float) -> tuple[float, float]:
    rate = a * lam + b * gamma
    if rate <= 0:
        return floor, 0.0
    return (a * lam + b * gamma * floor) / rate, rate


def gate_slope_over_cost(R: float, params: InstitutionalParams, cost_R: float) -> float:
    gate = regulatory_gate(R, params)
    sig = (gate - params.g0) / max(1.0 - params.g0, 1e-12)
    slope = (1.0 - params.g0) * params.kappa_R * sig * (1.0 - sig)
    return slope / (max(cost_R, 1e-12) * max(gate, 1e-12))


def gaussian_floor_condition(mu: float, sigma: float, omega_floor: float, delta: float) -> bool:
    margin = mu - norm.ppf(1.0 - delta) * sigma
    return bool(margin >= __import__("math").log(omega_floor))


def cantelli_floor_condition(mu: float, sigma: float, omega_floor: float, delta: float) -> bool:
    import math

    return bool(mu - math.log(omega_floor) >= math.sqrt((1.0 - delta) / delta) * sigma)


def risk_adjusted_expected_log_growth(a: float, b: float, jump_intensity: float, expected_jump: float) -> float:
    return a - 0.5 * b**2 + jump_intensity * expected_jump
