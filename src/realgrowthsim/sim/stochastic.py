from __future__ import annotations

import copy

import pandas as pd

from realgrowthsim.model.params import EventConfig, ScenarioConfig
from realgrowthsim.sim.engine import SimulationResult, simulate


def add_stochastic_incidents(
    config: ScenarioConfig,
    n_incidents: int,
    physical_scale: float = 0.08,
    institutional_scale: float = 0.04,
) -> ScenarioConfig:
    import numpy as np

    rng = np.random.default_rng(config.sim.seed)
    clone = copy.deepcopy(config)
    for idx in range(n_incidents):
        t = float(rng.uniform(0.1 * config.sim.horizon, 0.95 * config.sim.horizon))
        clone.events.append(
            EventConfig(
                time=t,
                name=f"stochastic incident {idx + 1}",
                kind="shock",
                physical_jumps={
                    "G": -abs(float(rng.normal(physical_scale, physical_scale / 3))),
                    "M": -abs(float(rng.normal(physical_scale, physical_scale / 3))),
                },
                institutional_jumps={
                    "S": -abs(float(rng.normal(institutional_scale, institutional_scale / 3))),
                    "R": -abs(float(rng.normal(institutional_scale, institutional_scale / 3))),
                },
            )
        )
    return clone


def run_monte_carlo(config: ScenarioConfig, n: int = 50, incidents: int = 2) -> tuple[list[SimulationResult], pd.DataFrame]:
    results = []
    rows = []
    for i in range(n):
        clone = copy.deepcopy(config)
        clone.sim.seed = config.sim.seed + i
        clone = add_stochastic_incidents(clone, incidents)
        result = simulate(clone)
        results.append(result)
        df = result.trace.copy()
        df["run"] = i
        rows.append(df)
    return results, pd.concat(rows, ignore_index=True)
