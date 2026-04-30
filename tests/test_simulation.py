from realgrowthsim.model.params import ScenarioConfig
from realgrowthsim.model.state import StateVector
from realgrowthsim.sim.engine import simulate
from realgrowthsim.sim.scenarios import preset_configs


def test_simulation_preserves_bounds():
    config = ScenarioConfig()
    config.sim.horizon = 3.0
    config.sim.dt = 0.2
    result = simulate(config)
    assert (result.trace[["A", "H", "C"]] > 0).all().all()
    assert (result.trace[["E", "G", "M", "W", "L"]] >= 0).all().all()
    assert (result.trace[["S", "R", "U", "P"]] >= config.params.institutional.xi_floor).all().all()
    assert (result.trace[["S", "R", "U", "P"]] <= 1.0).all().all()


def test_preset_runs_short():
    for config in preset_configs().values():
        config.sim.horizon = 1.0
        result = simulate(config)
        assert not result.trace.empty
        assert result.trace["YR"].iloc[-1] > 0


def test_state_from_array_guarded_clips_numerical_overshoot():
    state = StateVector.from_array_guarded(
        [0.0, 0.0, 0.0, -1.0, -1.0, -1.0, -1.0, -1.0, 1.0000001, -0.1, 2.0, 0.0],
        xi_floor=0.05,
    )
    assert state.A > 0
    assert state.C > 0
    assert state.E == 0.0
    assert state.S == 1.0
    assert state.R == 0.05
    assert state.U == 1.0
    assert state.P == 0.05
