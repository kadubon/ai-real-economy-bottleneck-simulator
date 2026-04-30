import numpy as np

from realgrowthsim.model.equations import derived_indicators, speed_ratio
from realgrowthsim.model.params import ScenarioConfig


def test_realized_output_identity_and_gap_decomposition():
    config = ScenarioConfig()
    d = derived_indicators(config.initial_state, config.params)
    assert np.isclose(d.YR, d.OmegaP * d.OmegaI * d.YI)
    assert np.isclose(d.gap, d.gapP + d.gapI)


def test_bpi_and_reflection_bounds():
    config = ScenarioConfig()
    d = derived_indicators(config.initial_state, config.params)
    assert 0.0 <= d.BPI < 1.0
    assert 0.0 < d.OmegaP <= 1.0
    assert 0.0 < d.OmegaI <= 1.0


def test_speed_ratio_nan_when_denominator_too_small():
    times = np.array([0.0, 1.0])
    log_yi = np.array([1.0, 1.0 + 1e-12])
    log_yr = np.array([1.0, 1.2])
    ratio = speed_ratio(log_yi, log_yr, times, window=1.0, eps_v=1e-8)
    assert np.isnan(ratio[-1])
