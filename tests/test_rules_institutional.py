from realgrowthsim.model.params import InstitutionalParams
from realgrowthsim.rules.institutional import (
    cantelli_floor_condition,
    gate_slope_over_cost,
    gaussian_floor_condition,
    institutional_fixed_point,
    risk_adjusted_expected_log_growth,
)


def test_institutional_fixed_point_and_chance_checks():
    fixed, rate = institutional_fixed_point(a=0.1, b=0.05, lam=1.0, gamma=1.0, floor=0.1)
    assert 0.1 <= fixed <= 1.0
    assert rate > 0
    assert gaussian_floor_condition(mu=-0.05, sigma=0.01, omega_floor=0.90, delta=0.05)
    assert cantelli_floor_condition(mu=-0.02, sigma=0.01, omega_floor=0.90, delta=0.05)


def test_gate_roi_and_risk_adjusted_growth():
    params = InstitutionalParams()
    assert gate_slope_over_cost(0.72, params, cost_R=1.0) > 0
    assert risk_adjusted_expected_log_growth(0.1, 0.2, 0.5, -0.05) < 0.1
