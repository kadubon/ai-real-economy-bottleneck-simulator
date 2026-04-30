from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from realgrowthsim.model.state import BRANCH_NAMES, StateVector


class IntegrationMethod(StrEnum):
    euler = "euler"
    rk4 = "rk4"
    solve_ivp = "solve_ivp"


class SharePolicy(StrEnum):
    fixed = "fixed"
    active_bottleneck = "active_bottleneck"
    tie_aware = "tie_aware"
    robust_diversification = "robust_diversification"
    kkt = "kkt"
    cvar = "cvar"


class InformationParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alpha: float = Field(0.4, gt=0)
    beta: float = Field(0.25, gt=0)
    gamma: float = Field(0.35, gt=0)
    chi_A: float = Field(0.08, ge=0)
    phi: float = Field(0.55, gt=0, lt=1)
    lambda_H: float = Field(0.25, ge=0)
    mu: float = Field(0.35, ge=0)
    nu_D: float = Field(0.05, ge=0)
    delta_A: float = Field(0.015, ge=0)
    chi_H: float = Field(0.06, ge=0)
    rho: float = Field(0.55, gt=0, lt=1)
    eta_A: float = Field(0.5, ge=0)
    eta_C: float = Field(0.4, ge=0)
    delta_H: float = Field(0.02, ge=0)
    delta_C: float = Field(0.05, ge=0)
    theta_0: float = Field(1.0, gt=0)
    theta_A: float = Field(0.5, ge=0)
    theta_H: float = Field(0.4, ge=0)
    demand_D: float = Field(1.0, ge=0)


class InvestmentParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    F_bar: float = Field(0.35, gt=0)
    y_bar: float = Field(1.0, gt=0)
    s_bar: float = Field(0.85, gt=0, lt=1)
    share_floors: dict[str, float] = Field(
        default_factory=lambda: {name: 0.02 for name in BRANCH_NAMES}
    )
    fixed_shares: dict[str, float] = Field(
        default_factory=lambda: {
            "C": 0.24,
            "E": 0.15,
            "G": 0.15,
            "M": 0.11,
            "W": 0.10,
            "L": 0.10,
        }
    )

    @model_validator(mode="after")
    def validate_shares(self) -> InvestmentParams:
        for label in BRANCH_NAMES:
            self.share_floors.setdefault(label, 0.0)
            self.fixed_shares.setdefault(label, self.share_floors[label])
        if any(v < 0 for v in self.share_floors.values()):
            raise ValueError("share floors must be nonnegative")
        if any(v < 0 for v in self.fixed_shares.values()):
            raise ValueError("fixed shares must be nonnegative")
        if sum(self.share_floors.values()) > self.s_bar + 1e-12:
            raise ValueError("share floors exceed s_bar")
        return self


class PhysicalParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kappa_E: float = Field(1.0, gt=0)
    kappa_G: float = Field(1.0, gt=0)
    kappa_M: float = Field(1.0, gt=0)
    kappa_W: float = Field(1.0, gt=0)
    kappa_L: float = Field(1.0, gt=0)
    theta_P: float = Field(0.5, gt=0)
    eps_C: float = Field(1e-6, gt=0)
    chi_E: float = Field(0.8, ge=0)
    chi_G: float = Field(0.8, ge=0)
    chi_M: float = Field(0.8, ge=0)
    chi_W: float = Field(0.8, ge=0)
    chi_L: float = Field(0.8, ge=0)
    psi_E: float = Field(0.85, gt=0, le=1)
    psi_G: float = Field(0.85, gt=0, le=1)
    psi_M: float = Field(0.9, gt=0, le=1)
    psi_W: float = Field(0.9, gt=0, le=1)
    psi_L: float = Field(0.8, gt=0, le=1)
    delta_E: float = Field(0.04, ge=0)
    delta_G: float = Field(0.04, ge=0)
    delta_M: float = Field(0.05, ge=0)
    delta_W: float = Field(0.05, ge=0)
    delta_L: float = Field(0.04, ge=0)
    ell_M0: float = Field(0.005, ge=0)
    ell_W0: float = Field(0.005, ge=0)
    ell_M_slope: float = Field(0.002, ge=0)
    ell_W_slope: float = Field(0.002, ge=0)
    smooth_min_enabled: bool = False
    smooth_min_p: float = Field(16.0, gt=0)
    heavy_traffic_enabled: bool = False
    heavy_traffic_a: float = Field(0.15, ge=0)
    heavy_traffic_kappa: float = Field(0.25, ge=0)


class InstitutionalParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    xi_floor: float = Field(0.05, gt=0, lt=1)
    a_S: float = Field(0.12, ge=0)
    a_R: float = Field(0.11, ge=0)
    a_U: float = Field(0.12, ge=0)
    a_P: float = Field(0.12, ge=0)
    b_S: float = Field(0.02, ge=0)
    b_R: float = Field(0.02, ge=0)
    b_U: float = Field(0.02, ge=0)
    b_P: float = Field(0.02, ge=0)
    beta_S: float = Field(0.25, ge=-0.99, le=0.99)
    beta_R: float = Field(0.2, ge=-0.99, le=0.99)
    beta_U: float = Field(0.2, ge=-0.99, le=0.99)
    beta_P: float = Field(0.2, ge=-0.99, le=0.99)
    omega_S: float = Field(0.5, ge=0)
    omega_R: float = Field(0.5, ge=0)
    omega_U: float = Field(0.5, ge=0)
    omega_P: float = Field(0.5, ge=0)
    psi_S: float = Field(0.5, ge=0)
    psi_R: float = Field(0.5, ge=0)
    psi_U: float = Field(0.5, ge=0)
    psi_P: float = Field(0.5, ge=0)
    nu_S: float = Field(0.45, gt=0)
    nu_U: float = Field(0.35, gt=0)
    nu_P: float = Field(0.25, gt=0)
    g0: float = Field(0.2, gt=0, lt=1)
    kappa_R: float = Field(8.0, gt=0)
    R_star: float = Field(0.72, ge=0, le=1)
    risk: float = Field(0.05, ge=0)


class SimulationParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    horizon: float = Field(20.0, gt=0)
    dt: float = Field(0.1, gt=0)
    method: IntegrationMethod = IntegrationMethod.rk4
    seed: int = 1234
    speed_window: float = Field(1.0, gt=0)
    eps_v: float = Field(1e-8, gt=0)
    max_step_warnings: int = Field(50, ge=0)


class SharePolicyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy: SharePolicy = SharePolicy.fixed
    robust_rho: float = Field(0.25, ge=0, lt=1)
    cvar_alpha: float = Field(0.9, gt=0, lt=1)
    kkt_psi: float = Field(0.75, gt=0, lt=1)


class ModelParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    information: InformationParams = Field(default_factory=InformationParams)
    investment: InvestmentParams = Field(default_factory=InvestmentParams)
    physical: PhysicalParams = Field(default_factory=PhysicalParams)
    institutional: InstitutionalParams = Field(default_factory=InstitutionalParams)


class EventConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    time: float = Field(..., ge=0)
    name: str = "event"
    kind: Literal["policy", "shock", "regime"] = "shock"
    regime: str | None = None
    physical_jumps: dict[str, float] = Field(default_factory=dict)
    institutional_jumps: dict[str, float] = Field(default_factory=dict)

    @field_validator("physical_jumps")
    @classmethod
    def validate_physical_keys(cls, value: dict[str, float]) -> dict[str, float]:
        bad = set(value) - {"E", "G", "M", "W", "L"}
        if bad:
            raise ValueError(f"invalid physical jump keys: {sorted(bad)}")
        return value

    @field_validator("institutional_jumps")
    @classmethod
    def validate_institutional_keys(cls, value: dict[str, float]) -> dict[str, float]:
        bad = set(value) - {"S", "R", "U", "P"}
        if bad:
            raise ValueError(f"invalid institutional jump keys: {sorted(bad)}")
        return value


class RegimeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = "baseline"
    chi_multipliers: dict[str, float] = Field(
        default_factory=lambda: {"E": 1.0, "G": 1.0, "M": 1.0, "W": 1.0, "L": 1.0}
    )
    demand_D: float | None = None
    risk: float | None = None


class ScenarioConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = "Baseline endogenous co-growth"
    description: str = "Output-driven investment with moderate physical and institutional frictions."
    units: Literal["normalized", "paper_inspired"] = "normalized"
    initial_state: StateVector = Field(default_factory=StateVector)
    params: ModelParams = Field(default_factory=ModelParams)
    sim: SimulationParams = Field(default_factory=SimulationParams)
    share_policy: SharePolicyConfig = Field(default_factory=SharePolicyConfig)
    events: list[EventConfig] = Field(default_factory=list)
    regimes: dict[str, RegimeConfig] = Field(
        default_factory=lambda: {"baseline": RegimeConfig(name="baseline")}
    )
    default_regime: str = "baseline"

    @model_validator(mode="after")
    def validate_scenario(self) -> ScenarioConfig:
        if self.default_regime not in self.regimes:
            self.regimes[self.default_regime] = RegimeConfig(name=self.default_regime)
        if self.sim.dt > self.sim.horizon:
            raise ValueError("dt must not exceed horizon")
        return self
