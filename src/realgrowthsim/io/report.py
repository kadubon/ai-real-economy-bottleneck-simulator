from __future__ import annotations

import json

from realgrowthsim.io.export import diagnostics_to_json
from realgrowthsim.model.params import ScenarioConfig
from realgrowthsim.rules.registry import RuleDiagnostic
from realgrowthsim.sim.engine import SimulationResult
from realgrowthsim.sim.interpretation import interpret_trace


def markdown_report(result: SimulationResult, diagnostics: list[RuleDiagnostic]) -> str:
    summary = result.summary()
    config: ScenarioConfig = result.scenario
    interpretation = interpret_trace(result.trace)
    return f"""# AI Real-Economy Bottleneck Simulation Report

## Scenario
- Name: {config.name}
- Description: {config.description}
- Units: {config.units}
- Horizon: {config.sim.horizon}
- dt: {config.sim.dt}
- Seed: {config.sim.seed}

## Summary
```json
{json.dumps(summary, indent=2)}
```

## Plain-Language Reading
- Potential realized: {100.0 * interpretation.realization_ratio:.1f}%
- Main drag: {interpretation.main_drag}
- Active physical branch: {interpretation.active_bottleneck}
- Reading: {interpretation.headline}
- Bottleneck pressure: {interpretation.bottleneck_sentence}
- Speed: {interpretation.speed_sentence}

## Key Diagnostics
```json
{diagnostics_to_json(diagnostics)}
```

## Assumption Notes
- This is a research simulation tool.
- Not financial, investment, energy-policy, or regulatory advice.
- Scenario values are synthetic, normalized, or paper-inspired examples, not forecasts.
- Do not enter personal, confidential, financial, health, biometric, or sensitive data.

## Citations
- ai-real-economy-bottleneck-simulator contributors. (2026). "AI Real-Economy Bottleneck Simulator" (v0.1.0). Zenodo. DOI: 10.5281/zenodo.19904514
- K. Takahashi, "From AI Capability Growth to Real-Economy Growth: A Semi-Endogenous Model of Physical and Institutional Bottlenecks," 2026. DOI: 10.5281/zenodo.18677068
- K. Takahashi, "Operational Deductive Rules for Real-Economy Acceleration in the AI Era," 2026. DOI: 10.5281/zenodo.18688712

## License
Apache License 2.0.
"""
