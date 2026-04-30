"""Research simulator for AI capability growth and real-economy bottlenecks."""

from realgrowthsim.model.params import ScenarioConfig
from realgrowthsim.model.state import StateVector
from realgrowthsim.sim.engine import simulate

__all__ = ["ScenarioConfig", "StateVector", "simulate"]
__version__ = "0.1.0"
