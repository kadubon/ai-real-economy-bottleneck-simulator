from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from realgrowthsim.model.params import (
    InstitutionalParams,
    InvestmentParams,
    ModelParams,
    PhysicalParams,
)
from realgrowthsim.model.state import BRANCH_NAMES, StateVector


@dataclass(frozen=True)
class DerivedIndicators:
    YI: float
    OmegaP: float
    OmegaI: float
    YR: float
    gap: float
    gapP: float
    gapI: float
    Ceff: float
    BPI: float
    branches: dict[str, float]
    active_set: list[str]
    tie_set: list[str]
    smooth_min_error_bound: float
    utilization: float


def psi(x: float) -> float:
    x = max(float(x), 0.0)
    return x / (1.0 + x)


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def safe_log(x: float, name: str = "value") -> float:
    if not np.isfinite(x) or x <= 0:
        raise ValueError(f"{name} must be positive for log; got {x!r}")
    return float(math.log(x))


def potential_output(state: StateVector, params: ModelParams) -> float:
    info = params.information
    return float((state.A**info.alpha) * (state.H**info.beta) * (state.C**info.gamma))


def theta_conversion(state: StateVector, params: ModelParams) -> float:
    info = params.information
    return float(
        info.theta_0
        * (1.0 + info.theta_A * psi(state.A))
        * (1.0 + info.theta_H * psi(state.H))
    )


def investment_flow(YR_left: float, params: InvestmentParams) -> float:
    y = max(float(YR_left), 0.0)
    return float(params.F_bar * y / (params.y_bar + y))


def branch_values(state: StateVector, params: PhysicalParams) -> dict[str, float]:
    return {
        "C": state.C,
        "E": params.kappa_E * state.E,
        "G": params.kappa_G * state.G,
        "M": params.kappa_M * state.M,
        "W": params.kappa_W * state.W,
        "L": params.kappa_L * state.L,
    }


def active_set(branches: dict[str, float], rel_tol: float = 1e-8, abs_tol: float = 1e-10) -> list[str]:
    minimum = min(branches.values())
    return [
        name
        for name, value in branches.items()
        if abs(value - minimum) <= max(abs_tol, rel_tol * max(abs(minimum), 1.0))
    ]


def smooth_min(values: list[float], p: float) -> float:
    arr = np.asarray(values, dtype=float)
    if np.any(arr <= 0):
        return float(np.min(arr))
    return float(np.sum(arr ** (-p)) ** (-1.0 / p))


def smooth_min_error_bound(values: list[float], p: float, theta_p: float, C: float, eps_C: float) -> float:
    """Conservative model-consistent bound for the smooth-min OmegaP error.

    The supplement states the differentiable-minimum envelope for
    u -> (u / (C + eps_C))^theta. The main model uses
    u -> ((u + eps_C) / (C + eps_C))^theta. This implementation uses the
    latter map, which is the conservative bound for the simulator's actual
    OmegaP calculation.
    """

    arr = np.asarray(values, dtype=float)
    arr = arr[arr > 0]
    if len(arr) == 0:
        return float("nan")
    n = len(arr)
    m = float(np.min(arr))
    lower = (n ** (-1.0 / p)) * m
    if theta_p >= 1:
        max_deriv = theta_p * ((m + eps_C) ** (theta_p - 1.0)) / ((C + eps_C) ** theta_p)
    else:
        max_deriv = theta_p * ((lower + eps_C) ** (theta_p - 1.0)) / (
            (C + eps_C) ** theta_p
        )
    return float(max_deriv * (1.0 - n ** (-1.0 / p)) * m)


def effective_compute(state: StateVector, params: PhysicalParams) -> float:
    values = list(branch_values(state, params).values())
    if params.smooth_min_enabled:
        return smooth_min(values, params.smooth_min_p)
    return float(min(values))


def omega_physical(Ceff: float, C: float, params: PhysicalParams) -> float:
    ratio = (Ceff + params.eps_C) / (C + params.eps_C)
    ratio = min(1.0, max(0.0, ratio))
    return float(ratio**params.theta_P)


def bottleneck_pressure(Ceff: float, C: float, eps_C: float) -> float:
    ratio = (Ceff + eps_C) / (C + eps_C)
    return float(min(1.0, max(0.0, 1.0 - ratio)))


def physical_utilization(branches: dict[str, float], eps_C: float) -> float:
    """Local utilization proxy in [0,1) for heavy-traffic diagnostics.

    The heavy-traffic theorem uses rho in (0,1). The simulator estimates rho
    as installed compute divided by the smallest non-compute physical branch,
    clipped below one. This is separate from C/Ceff, which can exceed one.
    """

    non_compute = [value for key, value in branches.items() if key != "C"]
    physical_capacity = max(min(non_compute), eps_C) if non_compute else eps_C
    return float(min(max(branches["C"] / (physical_capacity + eps_C), 0.0), 0.999999))


def regulatory_gate(R: float, params: InstitutionalParams) -> float:
    return float(params.g0 + (1.0 - params.g0) * sigmoid(params.kappa_R * (R - params.R_star)))


def omega_institutional(state: StateVector, params: InstitutionalParams) -> float:
    gate = regulatory_gate(state.R, params)
    value = (state.S**params.nu_S) * (state.U**params.nu_U) * (state.P**params.nu_P) * gate
    return float(min(1.0, max(0.0, value)))


def realized_output(YI: float, OmegaP: float, OmegaI: float) -> float:
    return float(OmegaP * OmegaI * YI)


def derived_indicators(state: StateVector, params: ModelParams) -> DerivedIndicators:
    branches = branch_values(state, params.physical)
    Ceff = effective_compute(state, params.physical)
    OmegaP = omega_physical(Ceff, state.C, params.physical)
    OmegaI = omega_institutional(state, params.institutional)
    YI = potential_output(state, params)
    YR = realized_output(YI, OmegaP, OmegaI)
    gapP = -safe_log(OmegaP, "OmegaP")
    gapI = -safe_log(OmegaI, "OmegaI")
    gap = safe_log(YI, "YI") - safe_log(YR, "YR")
    act = active_set(branches)
    error_bound = smooth_min_error_bound(
        list(branches.values()),
        params.physical.smooth_min_p,
        params.physical.theta_P,
        state.C,
        params.physical.eps_C,
    )
    return DerivedIndicators(
        YI=YI,
        OmegaP=OmegaP,
        OmegaI=OmegaI,
        YR=YR,
        gap=gap,
        gapP=gapP,
        gapI=gapI,
        Ceff=Ceff,
        BPI=bottleneck_pressure(Ceff, state.C, params.physical.eps_C),
        branches=branches,
        active_set=act,
        tie_set=act if len(act) > 1 else [],
        smooth_min_error_bound=error_bound,
        utilization=physical_utilization(branches, params.physical.eps_C),
    )


def speed_ratio(log_yi: np.ndarray, log_yr: np.ndarray, times: np.ndarray, window: float, eps_v: float) -> np.ndarray:
    out = np.full(len(times), np.nan)
    for i, t in enumerate(times):
        target = t - window
        if target < times[0] - 1e-12:
            continue
        j = int(np.searchsorted(times, target, side="left"))
        if j >= len(times):
            continue
        denom = log_yi[i] - log_yi[j]
        if abs(denom) <= eps_v:
            out[i] = np.nan
        else:
            out[i] = (log_yr[i] - log_yr[j]) / denom
    return out


def cumulative_reflection_loss(times: np.ndarray, YI: np.ndarray, YR: np.ndarray) -> np.ndarray:
    loss_flow = np.maximum(YI - YR, 0.0)
    out = np.zeros(len(times))
    for i in range(1, len(times)):
        dt = times[i] - times[i - 1]
        out[i] = out[i - 1] + 0.5 * dt * (loss_flow[i] + loss_flow[i - 1])
    return out


def normalized_shares(shares: dict[str, float], investment: InvestmentParams) -> dict[str, float]:
    floors = {name: float(investment.share_floors.get(name, 0.0)) for name in BRANCH_NAMES}
    clean = {name: max(float(shares.get(name, floors[name])), floors[name]) for name in BRANCH_NAMES}
    total = sum(clean.values())
    if total <= investment.s_bar + 1e-12:
        return clean
    floor_total = sum(floors.values())
    residual = max(investment.s_bar - floor_total, 0.0)
    extra_total = max(total - floor_total, 1e-12)
    return {
        name: floors[name] + residual * max(clean[name] - floors[name], 0.0) / extra_total
        for name in BRANCH_NAMES
    }
