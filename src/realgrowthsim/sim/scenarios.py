from __future__ import annotations

import copy
import json
from pathlib import Path

from realgrowthsim.model.params import EventConfig, ScenarioConfig, SharePolicy

PRESET_DIR = Path(__file__).resolve().parents[1] / "data" / "presets"


def baseline_config() -> ScenarioConfig:
    return ScenarioConfig()


def preset_configs() -> dict[str, ScenarioConfig]:
    base = baseline_config()
    presets: dict[str, ScenarioConfig] = {"baseline": base}

    c = copy.deepcopy(base)
    c.name = "Information-fast / reflection-slow"
    c.description = "Rapid A,H,C improvement with slower physical and institutional reflection."
    c.params.information.chi_A = 0.14
    c.params.information.chi_H = 0.10
    c.params.information.theta_A = 0.8
    c.params.physical.chi_E = 0.18
    c.params.physical.chi_G = 0.17
    c.params.institutional.a_R = 0.035
    c.params.institutional.a_S = 0.04
    presets["information_fast_reflection_slow"] = c

    c = copy.deepcopy(base)
    c.name = "Physical coordination push"
    c.description = "Investment tilts toward near-term active physical bottlenecks."
    c.share_policy.policy = SharePolicy.active_bottleneck
    c.params.physical.chi_E = 0.45
    c.params.physical.chi_G = 0.42
    c.params.physical.chi_L = 0.38
    presets["physical_coordination_push"] = c

    c = copy.deepcopy(base)
    c.name = "Institutional acceleration"
    c.description = "Faster S,R,U,P drift and lower institutional risk."
    c.params.institutional.a_S = 0.14
    c.params.institutional.a_R = 0.13
    c.params.institutional.a_U = 0.13
    c.params.institutional.a_P = 0.13
    c.params.institutional.risk = 0.01
    presets["institutional_acceleration"] = c

    c = copy.deepcopy(base)
    c.name = "Resource and trust shock"
    c.description = "Joint physical and institutional disturbances with delayed recovery."
    c.events = [
        EventConfig(
            time=5.0,
            name="resource and trust shock",
            kind="shock",
            physical_jumps={"G": -0.35, "M": -0.25, "W": -0.20},
            institutional_jumps={"S": -0.18, "R": -0.12, "U": -0.10},
        ),
        EventConfig(
            time=9.0,
            name="recovery package",
            kind="policy",
            physical_jumps={"G": 0.18, "M": 0.12, "W": 0.10},
            institutional_jumps={"S": 0.07, "R": 0.05, "U": 0.05},
        ),
    ]
    presets["resource_trust_shock"] = c

    c = copy.deepcopy(base)
    c.name = "Conservative finite-resource stress"
    c.description = "Lower investment ceiling and slower physical conversion."
    c.units = "paper_inspired"
    c.params.investment.F_bar = 0.18
    c.params.information.chi_A = 0.11
    c.params.physical.chi_E = 0.15
    c.params.physical.chi_G = 0.14
    c.params.physical.chi_M = 0.18
    c.params.physical.chi_W = 0.18
    c.params.physical.chi_L = 0.12
    presets["conservative_stress"] = c

    c = copy.deepcopy(base)
    c.name = "Compute-only overbuild stress"
    c.description = "Compute investment expands faster than deployable feasibility."
    c.params.investment.fixed_shares = {"C": 0.70, "E": 0.03, "G": 0.03, "M": 0.03, "W": 0.03, "L": 0.03}
    presets["compute_only_overbuild_stress"] = c

    c = copy.deepcopy(base)
    c.name = "Active bottleneck preemption"
    c.description = "Tie-aware allocation begins before grid and permitting bottlenecks bind."
    c.share_policy.policy = SharePolicy.tie_aware
    c.initial_state.G = 0.88
    c.initial_state.L = 0.9
    c.params.physical.chi_G = 0.46
    c.params.physical.chi_L = 0.44
    presets["active_bottleneck_preemption"] = c

    c = copy.deepcopy(base)
    c.name = "Institutional risk shock"
    c.description = "Regulatory and social-readiness risk shock with endogenous recovery."
    c.params.institutional.risk = 0.12
    c.events = [
        EventConfig(
            time=6.0,
            name="institutional risk shock",
            kind="shock",
            institutional_jumps={"S": -0.22, "R": -0.20, "P": -0.12},
        )
    ]
    presets["institutional_risk_shock"] = c

    c = copy.deepcopy(base)
    c.name = "Tail-risk-aware allocation"
    c.description = "Diversifies share policy to reduce severe downside exposure."
    c.share_policy.policy = SharePolicy.cvar
    c.share_policy.cvar_alpha = 0.9
    c.events = [
        EventConfig(time=4.0, name="materials drawdown", kind="shock", physical_jumps={"M": -0.16}),
        EventConfig(time=7.5, name="cooling delay", kind="shock", physical_jumps={"W": -0.12}),
    ]
    presets["tail_risk_aware_allocation"] = c
    return presets


def load_preset(name: str) -> ScenarioConfig:
    path = PRESET_DIR / f"{name}.json"
    if path.exists():
        return ScenarioConfig.model_validate_json(path.read_text(encoding="utf-8"))
    presets = preset_configs()
    if name not in presets:
        raise KeyError(f"unknown preset: {name}")
    return presets[name]


def write_preset_files() -> None:
    PRESET_DIR.mkdir(parents=True, exist_ok=True)
    for name, config in preset_configs().items():
        (PRESET_DIR / f"{name}.json").write_text(
            json.dumps(config.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )
