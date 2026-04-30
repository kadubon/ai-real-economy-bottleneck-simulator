from __future__ import annotations

from realgrowthsim.model.params import RegimeConfig


def regime_value(regime: RegimeConfig, key: str, default: float = 1.0) -> float:
    return float(regime.chi_multipliers.get(key, default))
