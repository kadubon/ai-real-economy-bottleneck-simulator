from __future__ import annotations

from dataclasses import dataclass

from realgrowthsim.model.equations import derived_indicators
from realgrowthsim.model.params import ScenarioConfig


@dataclass
class ValidationMessage:
    level: str
    message: str


def validate_scenario(config: ScenarioConfig) -> list[ValidationMessage]:
    messages: list[ValidationMessage] = []
    floors = config.params.investment.share_floors
    if sum(floors.values()) > config.params.investment.s_bar:
        messages.append(ValidationMessage("error", "Share floors exceed s_bar."))
    d = derived_indicators(config.initial_state.guarded(config.params.institutional.xi_floor), config.params)
    if not 0.0 < d.OmegaP <= 1.0:
        messages.append(ValidationMessage("error", "OmegaP is outside (0,1] at initialization."))
    if not 0.0 < d.OmegaI <= 1.0:
        messages.append(ValidationMessage("error", "OmegaI is outside (0,1] at initialization."))
    if d.BPI < 0.0 or d.BPI >= 1.0:
        messages.append(ValidationMessage("warning", "BPI is outside the intended [0,1) range."))
    if config.params.physical.smooth_min_enabled:
        messages.append(ValidationMessage("info", "Smooth-min is enabled; reported Ceff is a differentiable approximation."))
    return messages
