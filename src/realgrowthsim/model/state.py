from __future__ import annotations

from typing import ClassVar

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_validator

STATE_NAMES = ("A", "H", "C", "E", "G", "M", "W", "L", "S", "R", "U", "P")
INFO_STATES = ("A", "H", "C")
PHYSICAL_STATES = ("E", "G", "M", "W", "L")
INSTITUTIONAL_STATES = ("S", "R", "U", "P")
BRANCH_NAMES = ("C", "E", "G", "M", "W", "L")


class StateVector(BaseModel):
    """Twelve-dimensional hybrid system state."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    A: float = Field(1.0, gt=0)
    H: float = Field(1.0, gt=0)
    C: float = Field(1.0, gt=0)
    E: float = Field(2.0, ge=0)
    G: float = Field(2.0, ge=0)
    M: float = Field(2.0, ge=0)
    W: float = Field(2.0, ge=0)
    L: float = Field(2.0, ge=0)
    S: float = Field(0.82, ge=0, le=1)
    R: float = Field(0.78, ge=0, le=1)
    U: float = Field(0.84, ge=0, le=1)
    P: float = Field(0.86, ge=0, le=1)

    names: ClassVar[tuple[str, ...]] = STATE_NAMES

    @field_validator("*")
    @classmethod
    def finite(cls, value: float) -> float:
        if not np.isfinite(value):
            raise ValueError("state values must be finite")
        return float(value)

    def to_array(self) -> np.ndarray:
        return np.array([getattr(self, name) for name in STATE_NAMES], dtype=float)

    @classmethod
    def from_array(cls, values: np.ndarray | list[float]) -> StateVector:
        return cls(**{name: float(values[i]) for i, name in enumerate(STATE_NAMES)})

    @classmethod
    def from_array_guarded(
        cls,
        values: np.ndarray | list[float],
        xi_floor: float = 0.05,
        eps: float = 1e-12,
    ) -> StateVector:
        data = {name: float(values[i]) for i, name in enumerate(STATE_NAMES)}
        for key in INFO_STATES:
            data[key] = max(data[key], eps)
        for key in PHYSICAL_STATES:
            data[key] = max(data[key], 0.0)
        for key in INSTITUTIONAL_STATES:
            data[key] = min(1.0, max(data[key], xi_floor))
        return cls(**data)

    def guarded(self, xi_floor: float = 0.05, eps: float = 1e-12) -> StateVector:
        data = self.model_dump()
        for key in INFO_STATES:
            data[key] = max(float(data[key]), eps)
        for key in PHYSICAL_STATES:
            data[key] = max(float(data[key]), 0.0)
        for key in INSTITUTIONAL_STATES:
            data[key] = min(1.0, max(float(data[key]), xi_floor))
        return StateVector(**data)

    def with_updates(self, **updates: float) -> StateVector:
        data = self.model_dump()
        data.update(updates)
        return StateVector(**data)
