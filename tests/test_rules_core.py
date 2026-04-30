from realgrowthsim.rules.core import (
    non_contraction_threshold,
    required_institutional_drift,
    required_physical_relief,
)
from realgrowthsim.rules.registry import evaluate_rules, rule_registry
from realgrowthsim.sim.engine import simulate
from realgrowthsim.sim.scenarios import load_preset


def test_required_threshold_formulas():
    assert required_physical_relief(1.0, 0.5, 0.2, 0.0, 0.5) == 0.2
    assert required_institutional_drift(1.0, 0.5, 0.1, 0.2, 0.5) == 0.05
    assert non_contraction_threshold(0.5, 0.1, 0.2, 0.5) == -0.45


def test_registry_includes_long_run_and_pressure_rules():
    ids = {rule.rule_id for rule in rule_registry()}
    assert {"T1", "T2", "T3", "T4", "T7", "P1", "P6", "P8"}.issubset(ids)
    result = simulate(load_preset("baseline"))
    diagnostics = {diag.rule_id: diag for diag in evaluate_rules(result.trace, result.events)}
    assert diagnostics["T4"].condition_satisfied
    assert "delay_amplification_proxy" in diagnostics["P8"].indicator_values
