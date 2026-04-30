from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from realgrowthsim.io.schema import scenario_to_json
from realgrowthsim.model.params import ScenarioConfig
from realgrowthsim.rules.registry import RuleDiagnostic


def export_trace_csv(trace: pd.DataFrame, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    trace.to_csv(path, index=False)


def export_scenario_json(config: ScenarioConfig, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(scenario_to_json(config), encoding="utf-8")


def diagnostics_to_json(diagnostics: list[RuleDiagnostic]) -> str:
    return json.dumps([item.as_dict() for item in diagnostics], indent=2)
