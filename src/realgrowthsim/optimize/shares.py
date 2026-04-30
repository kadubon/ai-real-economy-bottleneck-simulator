from __future__ import annotations

import numpy as np

from realgrowthsim.model.equations import active_set, branch_values, normalized_shares
from realgrowthsim.model.params import ModelParams, SharePolicy, SharePolicyConfig
from realgrowthsim.model.state import BRANCH_NAMES, StateVector
from realgrowthsim.optimize.kkt import clipped_kkt_allocation
from realgrowthsim.optimize.robust import diversify_top_levers, robust_concentration_condition


def branch_impacts(state: StateVector, params: ModelParams) -> dict[str, float]:
    branches = branch_values(state, params.physical)
    minimum = min(branches.values())
    return {
        label: 1.0 / (1e-9 + max(value - minimum, 0.0) + minimum)
        for label, value in branches.items()
    }


def recommend_shares(
    state: StateVector,
    params: ModelParams,
    policy_config: SharePolicyConfig,
) -> dict[str, float]:
    investment = params.investment
    floors = {label: investment.share_floors.get(label, 0.0) for label in BRANCH_NAMES}
    residual = max(investment.s_bar - sum(floors.values()), 0.0)
    base = {label: investment.fixed_shares.get(label, floors[label]) for label in BRANCH_NAMES}

    if policy_config.policy == SharePolicy.fixed:
        return normalized_shares(base, investment)

    branches = branch_values(state, params.physical)
    act = active_set(branches)
    if policy_config.policy in {SharePolicy.active_bottleneck, SharePolicy.tie_aware}:
        shares = floors.copy()
        targets = act or ["C"]
        for label in targets:
            shares[label] += residual / len(targets)
        return normalized_shares(shares, investment)

    impacts = branch_impacts(state, params)
    if policy_config.policy == SharePolicy.robust_diversification:
        robust, top, _ = robust_concentration_condition(impacts, policy_config.robust_rho)
        if robust and top is not None:
            shares = floors.copy()
            shares[top] += residual
            return normalized_shares(shares, investment)
        return normalized_shares(diversify_top_levers(impacts, floors, investment.s_bar), investment)

    if policy_config.policy == SharePolicy.kkt:
        return normalized_shares(
            clipped_kkt_allocation(impacts, floors, investment.s_bar, policy_config.kkt_psi),
            investment,
        )

    if policy_config.policy == SharePolicy.cvar:
        # Conservative no-CVX fallback: blend inverse-slack impacts with equal diversification.
        equal = {label: floors[label] + residual / len(BRANCH_NAMES) for label in BRANCH_NAMES}
        kkt = clipped_kkt_allocation(impacts, floors, investment.s_bar, policy_config.kkt_psi)
        mix = {label: 0.5 * equal[label] + 0.5 * kkt[label] for label in BRANCH_NAMES}
        return normalized_shares(mix, investment)

    return normalized_shares(base, investment)


def shares_to_array(shares: dict[str, float]) -> np.ndarray:
    return np.array([shares[label] for label in BRANCH_NAMES], dtype=float)
