import numpy as np

from realgrowthsim.model.equations import active_set, branch_values, derived_indicators
from realgrowthsim.model.params import ScenarioConfig
from realgrowthsim.rules.physical import (
    deterministic_switch_time_upper_bound,
    heavy_traffic_gain,
    noisy_switch_time_moments,
    overbuild_penalty,
)


def test_active_and_tie_detection():
    config = ScenarioConfig()
    state = config.initial_state.with_updates(C=1.0, E=1.0, G=1.0)
    branches = branch_values(state, config.params.physical)
    active = active_set(branches)
    assert {"C", "E", "G"}.issubset(set(active))


def test_overbuild_penalty_sign_and_switch_time():
    assert overbuild_penalty(C=2.0, eps_C=1e-6, thetaP=0.5) < 0
    assert np.isclose(deterministic_switch_time_upper_bound(0.3, 0.1), 3.0)
    mean, var = noisy_switch_time_moments(0.3, 0.1, 0.02)
    assert np.isclose(mean, 3.0)
    assert var > 0


def test_smooth_min_error_bound_and_heavy_traffic():
    config = ScenarioConfig()
    d = derived_indicators(config.initial_state, config.params)
    assert np.isfinite(d.smooth_min_error_bound)
    assert 0.0 <= d.utilization < 1.0
    assert heavy_traffic_gain(0.9, 0.1, 0.2, 0.01) > heavy_traffic_gain(0.5, 0.1, 0.2, 0.01)
