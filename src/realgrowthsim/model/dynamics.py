from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from realgrowthsim.model.equations import derived_indicators, theta_conversion
from realgrowthsim.model.investment import map_investments
from realgrowthsim.model.params import RegimeConfig, ScenarioConfig
from realgrowthsim.model.regimes import regime_value
from realgrowthsim.model.state import INSTITUTIONAL_STATES, STATE_NAMES, StateVector


@dataclass(frozen=True)
class StepContext:
    shares: dict[str, float]
    investment_flow: float
    controls: dict[str, float]
    demand: float
    risk: float


def institutional_drivers(
    xi: str,
    yi: float,
    risk: float,
    scenario: ScenarioConfig,
) -> tuple[float, float]:
    inst = scenario.params.institutional
    beta = getattr(inst, f"beta_{xi}")
    omega = getattr(inst, f"omega_{xi}")
    psi_risk = getattr(inst, f"psi_{xi}")
    lam = 1.0 + beta * np.tanh(omega * np.log1p(max(yi, 0.0)))
    gamma = 1.0 + psi_risk * risk
    return float(max(lam, 0.0)), float(max(gamma, 0.0))


def make_step_context(
    scenario: ScenarioConfig,
    shares: dict[str, float],
    YR_left: float,
    regime: RegimeConfig,
) -> StepContext:
    params = scenario.params
    flow, controls = map_investments(YR_left, shares, params.investment)
    demand = regime.demand_D if regime.demand_D is not None else params.information.demand_D
    risk = regime.risk if regime.risk is not None else params.institutional.risk
    return StepContext(shares=shares, investment_flow=flow, controls=controls, demand=demand, risk=risk)


def state_derivative(
    _t: float,
    y: np.ndarray,
    scenario: ScenarioConfig,
    context: StepContext,
    regime: RegimeConfig,
) -> np.ndarray:
    params = scenario.params
    info = params.information
    phys = params.physical
    inst = params.institutional
    state = StateVector.from_array_guarded(y, inst.xi_floor)
    d = derived_indicators(state, params)
    dy = np.zeros(len(STATE_NAMES), dtype=float)

    dy[0] = (
        info.chi_A
        * (state.A**info.phi)
        * (state.H**info.lambda_H)
        * (state.C**info.mu)
        * (context.demand**info.nu_D)
        - info.delta_A * state.A
    )
    dy[1] = (
        info.chi_H
        * (state.H**info.rho)
        * (1.0 + info.eta_A * state.A / (1.0 + state.A))
        * (1.0 + info.eta_C * state.C / (1.0 + state.C))
        - info.delta_H * state.H
    )
    dy[2] = context.controls["C"] * theta_conversion(state, params) - info.delta_C * state.C

    for idx, key in zip([3, 4, 7], ["E", "G", "L"], strict=True):
        chi = getattr(phys, f"chi_{key}") * regime_value(regime, key)
        psi_k = getattr(phys, f"psi_{key}")
        delta = getattr(phys, f"delta_{key}")
        dy[idx] = chi * (context.controls[key] ** psi_k) - delta * getattr(state, key)

    ell_M = phys.ell_M0 + phys.ell_M_slope * d.Ceff
    ell_W = phys.ell_W0 + phys.ell_W_slope * d.Ceff
    dy[5] = (
        phys.chi_M * regime_value(regime, "M") * (context.controls["M"] ** phys.psi_M)
        - (phys.delta_M + ell_M) * state.M
    )
    dy[6] = (
        phys.chi_W * regime_value(regime, "W") * (context.controls["W"] ** phys.psi_W)
        - (phys.delta_W + ell_W) * state.W
    )

    for idx, xi in zip([8, 9, 10, 11], INSTITUTIONAL_STATES, strict=True):
        a = getattr(inst, f"a_{xi}")
        b = getattr(inst, f"b_{xi}")
        lam, gamma = institutional_drivers(xi, d.YI, context.risk, scenario)
        value = getattr(state, xi)
        dy[idx] = a * (1.0 - value) * lam - b * (value - inst.xi_floor) * gamma

    return dy
