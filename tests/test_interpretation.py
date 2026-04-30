from realgrowthsim.sim.engine import simulate
from realgrowthsim.sim.interpretation import interpret_trace
from realgrowthsim.sim.scenarios import load_preset


def test_interpretation_returns_actionable_reading():
    result = simulate(load_preset("baseline"))
    reading = interpret_trace(result.trace)
    assert 0.0 < reading.realization_ratio <= 1.0
    assert reading.main_drag in {"physical", "institutional", "mixed"}
    assert reading.active_bottleneck
    assert reading.headline
    assert len(reading.next_experiments) == 3
