from __future__ import annotations

from realgrowthsim.model.equations import investment_flow, normalized_shares
from realgrowthsim.model.params import InvestmentParams


def map_investments(YR_left: float, shares: dict[str, float], params: InvestmentParams) -> tuple[float, dict[str, float]]:
    clean = normalized_shares(shares, params)
    flow = investment_flow(YR_left, params)
    controls = {name: clean[name] * flow for name in clean}
    return flow, controls
