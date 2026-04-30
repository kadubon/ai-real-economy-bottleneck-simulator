from __future__ import annotations

from realgrowthsim.model.params import EventConfig
from realgrowthsim.model.state import INSTITUTIONAL_STATES, PHYSICAL_STATES, StateVector


def apply_physical_jumps(state: StateVector, event: EventConfig) -> StateVector:
    data = state.model_dump()
    for key, jump in event.physical_jumps.items():
        if key in PHYSICAL_STATES:
            data[key] = max(0.0, float(data[key]) + float(jump))
    return StateVector(**data)


def apply_institutional_jumps(state: StateVector, event: EventConfig, xi_floor: float) -> StateVector:
    data = state.model_dump()
    for key, jump in event.institutional_jumps.items():
        if key in INSTITUTIONAL_STATES:
            data[key] = min(1.0, max(xi_floor, float(data[key]) + float(jump)))
    return StateVector(**data)
