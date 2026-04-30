from __future__ import annotations

from realgrowthsim.model.params import ScenarioConfig


def scenario_from_json(text: str) -> ScenarioConfig:
    return ScenarioConfig.model_validate_json(text)


def scenario_to_json(config: ScenarioConfig) -> str:
    return config.model_dump_json(indent=2)
