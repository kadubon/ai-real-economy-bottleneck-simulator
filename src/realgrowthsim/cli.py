from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from realgrowthsim.io.export import export_trace_csv
from realgrowthsim.model.params import ScenarioConfig
from realgrowthsim.rules.registry import evaluate_rules
from realgrowthsim.sim.engine import simulate
from realgrowthsim.sim.scenarios import load_preset, write_preset_files
from realgrowthsim.sim.validation import validate_scenario


def _load_scenario(path: str | None, preset: str | None) -> ScenarioConfig:
    if path:
        return ScenarioConfig.model_validate_json(Path(path).read_text(encoding="utf-8"))
    return load_preset(preset or "baseline")


def cmd_run(args: argparse.Namespace) -> int:
    config = _load_scenario(args.scenario, args.preset)
    result = simulate(config)
    export_trace_csv(result.trace, args.out)
    print(json.dumps(result.summary(), indent=2))
    if result.warnings:
        print("Warnings:", file=sys.stderr)
        for warning in result.warnings:
            print(f"- {warning}", file=sys.stderr)
    return 0


def cmd_gui(_args: argparse.Namespace) -> int:
    entrypoint = Path(__file__).resolve().parents[2] / "streamlit_app.py"
    if not entrypoint.exists():
        entrypoint = Path("streamlit_app.py")
    return subprocess.call([sys.executable, "-m", "streamlit", "run", str(entrypoint)])


def cmd_validate(args: argparse.Namespace) -> int:
    write_preset_files()
    config = _load_scenario(args.scenario, args.preset)
    messages = validate_scenario(config)
    result = simulate(config)
    diagnostics = evaluate_rules(result.trace, result.events)
    payload = {
        "messages": [m.__dict__ for m in messages],
        "summary": result.summary(),
        "diagnostics": [d.as_dict() for d in diagnostics],
    }
    print(json.dumps(payload, indent=2))
    return 0 if not any(m.level == "error" for m in messages) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="realgrowthsim")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run a scenario and export a CSV trace.")
    run.add_argument("--scenario", help="Path to scenario JSON.")
    run.add_argument("--preset", default="baseline", help="Preset name if --scenario is omitted.")
    run.add_argument("--out", default="outputs/simulation.csv", help="CSV output path.")
    run.set_defaults(func=cmd_run)

    gui = sub.add_parser("gui", help="Launch the Streamlit GUI.")
    gui.set_defaults(func=cmd_gui)

    validate = sub.add_parser("validate", help="Validate preset and rule diagnostics.")
    validate.add_argument("--scenario", help="Path to scenario JSON.")
    validate.add_argument("--preset", default="baseline")
    validate.set_defaults(func=cmd_validate)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
