import numpy as np

from realgrowthsim.model.params import EventConfig, ScenarioConfig
from realgrowthsim.sim.engine import simulate


def test_event_attribution_identity_and_yi_continuity():
    config = ScenarioConfig()
    config.sim.horizon = 2.0
    config.sim.dt = 0.5
    config.events = [
        EventConfig(
            time=1.0,
            name="shock",
            physical_jumps={"G": -0.2},
            institutional_jumps={"S": -0.1},
        )
    ]
    result = simulate(config)
    event = result.events.iloc[0]
    assert abs(event["attribution_residual"]) < 1e-8
    assert abs(event["delta_log_YI"]) < 1e-8
    assert np.isclose(
        event["delta_log_YR"],
        event["delta_log_OmegaP"] + event["delta_log_OmegaI"],
    )


def test_jump_projections_keep_domains():
    config = ScenarioConfig()
    config.sim.horizon = 1.0
    config.sim.dt = 0.5
    config.events = [
        EventConfig(
            time=0.5,
            name="large shock",
            physical_jumps={"E": -100.0, "M": -100.0},
            institutional_jumps={"S": -100.0, "R": -100.0},
        )
    ]
    result = simulate(config)
    assert result.trace["E"].min() >= 0.0
    assert result.trace["M"].min() >= 0.0
    assert result.trace["S"].min() >= config.params.institutional.xi_floor
    assert result.trace["R"].min() >= config.params.institutional.xi_floor


def test_coincident_events_are_grouped_and_ordered():
    config = ScenarioConfig()
    config.sim.horizon = 1.0
    config.sim.dt = 0.5
    config.regimes["stress"] = config.regimes["baseline"].model_copy(update={"name": "stress"})
    config.events = [
        EventConfig(time=0.5, name="institutional same time", institutional_jumps={"S": -0.1}),
        EventConfig(time=0.5, name="physical same time", physical_jumps={"G": -0.2}),
        EventConfig(time=0.5, name="regime same time", kind="regime", regime="stress"),
    ]
    result = simulate(config)
    assert len(result.events) == 1
    assert result.events.iloc[0]["regime"] == "stress"
    assert "institutional same time" in result.events.iloc[0]["name"]
    assert abs(result.events.iloc[0]["attribution_residual"]) < 1e-8
