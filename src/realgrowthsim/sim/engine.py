from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from realgrowthsim.model.dynamics import make_step_context, state_derivative
from realgrowthsim.model.equations import (
    cumulative_reflection_loss,
    derived_indicators,
    safe_log,
    speed_ratio,
)
from realgrowthsim.model.events import apply_institutional_jumps, apply_physical_jumps
from realgrowthsim.model.investment import map_investments
from realgrowthsim.model.params import IntegrationMethod, RegimeConfig, ScenarioConfig
from realgrowthsim.model.state import StateVector
from realgrowthsim.optimize.shares import recommend_shares
from realgrowthsim.sim.integrators import euler_step, rk4_step, solve_ivp_step


@dataclass
class SimulationResult:
    scenario: ScenarioConfig
    trace: pd.DataFrame
    events: pd.DataFrame
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> dict[str, float | int | str]:
        last = self.trace.iloc[-1]
        valid_speed = self.trace["v_h"].dropna()
        return {
            "scenario": self.scenario.name,
            "final_time": float(last["t"]),
            "final_YR": float(last["YR"]),
            "final_gap": float(last["gap"]),
            "average_speed_ratio": float(valid_speed.mean()) if len(valid_speed) else float("nan"),
            "max_BPI": float(self.trace["BPI"].max()),
            "cumulative_reflection_loss": float(last["cumulative_reflection_loss"]),
            "event_count": int(len(self.events)),
        }


def _derivative_factory(
    scenario: ScenarioConfig,
    shares: dict[str, float],
    YR_left: float,
    regime: RegimeConfig,
):
    context = make_step_context(scenario, shares, YR_left, regime)

    def f(_t: float, y: np.ndarray) -> np.ndarray:
        return state_derivative(_t, y, scenario, context, regime)

    return f, context.investment_flow, context.controls


def _integrate_segment(
    scenario: ScenarioConfig,
    state: StateVector,
    start: float,
    end: float,
    shares: dict[str, float],
    YR_left: float,
    regime: RegimeConfig,
) -> StateVector:
    dt = end - start
    if dt <= 1e-15:
        return state
    f, _, _ = _derivative_factory(scenario, shares, YR_left, regime)
    y = state.to_array()
    method = scenario.sim.method
    if method == IntegrationMethod.euler:
        y_next = euler_step(f, start, y, dt)
    elif method == IntegrationMethod.solve_ivp:
        y_next = solve_ivp_step(f, start, y, dt)
    else:
        y_next = rk4_step(f, start, y, dt)
    return StateVector.from_array_guarded(y_next, scenario.params.institutional.xi_floor)


def _row(
    t: float,
    state: StateVector,
    scenario: ScenarioConfig,
    shares: dict[str, float],
    flow: float,
    controls: dict[str, float],
    regime_name: str,
) -> dict[str, float | str]:
    d = derived_indicators(state, scenario.params)
    row: dict[str, float | str] = {"t": float(t), "regime": regime_name}
    row.update(state.model_dump())
    row.update(
        {
            "YI": d.YI,
            "OmegaP": d.OmegaP,
            "OmegaI": d.OmegaI,
            "YR": d.YR,
            "gap": d.gap,
            "gapP": d.gapP,
            "gapI": d.gapI,
            "Ceff": d.Ceff,
            "BPI": d.BPI,
            "active_bottleneck": ",".join(d.active_set),
            "tie_set": ",".join(d.tie_set),
            "smooth_min_error_bound": d.smooth_min_error_bound,
            "utilization": d.utilization,
            "F": flow,
        }
    )
    for key, value in d.branches.items():
        row[f"branch_{key}"] = value
    for key, value in shares.items():
        row[f"share_{key}"] = value
        row[f"u_{key}"] = controls.get(key, 0.0)
    return row


def _event_attribution(before: StateVector, after: StateVector, scenario: ScenarioConfig) -> dict[str, float]:
    d0 = derived_indicators(before, scenario.params)
    d1 = derived_indicators(after, scenario.params)
    return {
        "delta_log_YR": safe_log(d1.YR, "YR_after") - safe_log(d0.YR, "YR_before"),
        "delta_log_OmegaP": safe_log(d1.OmegaP, "OmegaP_after") - safe_log(d0.OmegaP, "OmegaP_before"),
        "delta_log_OmegaI": safe_log(d1.OmegaI, "OmegaI_after") - safe_log(d0.OmegaI, "OmegaI_before"),
        "delta_log_YI": safe_log(d1.YI, "YI_after") - safe_log(d0.YI, "YI_before"),
    }


def _events_at_time(events: list, start_idx: int) -> tuple[list, int]:
    if start_idx >= len(events):
        return [], start_idx
    t0 = events[start_idx].time
    idx = start_idx
    group = []
    while idx < len(events) and abs(events[idx].time - t0) <= 1e-12:
        group.append(events[idx])
        idx += 1
    return group, idx


def _apply_ordered_event_group(
    state: StateVector,
    group: list,
    scenario: ScenarioConfig,
    regime: RegimeConfig,
    regime_name: str,
) -> tuple[StateVector, RegimeConfig, str, dict[str, float]]:
    before = state
    for event in group:
        if event.regime:
            regime_name = event.regime
            regime = scenario.regimes.get(regime_name, regime)
    after_physical = before
    for event in group:
        after_physical = apply_physical_jumps(after_physical, event)
    after = after_physical
    for event in group:
        after = apply_institutional_jumps(
            after,
            event,
            scenario.params.institutional.xi_floor,
        )
    after = after.guarded(scenario.params.institutional.xi_floor)
    return after, regime, regime_name, _event_attribution(before, after, scenario)


def simulate(config: ScenarioConfig) -> SimulationResult:
    warnings: list[str] = []
    events = sorted(config.events, key=lambda e: e.time)
    event_idx = 0
    regime_name = config.default_regime
    regime = config.regimes[regime_name]
    state = config.initial_state.guarded(config.params.institutional.xi_floor)
    t = 0.0
    rows: list[dict[str, float | str]] = []
    event_rows: list[dict[str, float | str]] = []

    initial_d = derived_indicators(state, config.params)
    shares = recommend_shares(state, config.params, config.share_policy)
    flow, controls = map_investments(initial_d.YR, shares, config.params.investment)
    rows.append(_row(t, state, config, shares, flow, controls, regime_name))

    grid = list(np.arange(config.sim.dt, config.sim.horizon + config.sim.dt * 0.5, config.sim.dt))
    grid = [min(float(x), config.sim.horizon) for x in grid if x <= config.sim.horizon + 1e-12]
    for target in grid:
        d_left = derived_indicators(state, config.params)
        shares = recommend_shares(state, config.params, config.share_policy)
        flow, controls = map_investments(d_left.YR, shares, config.params.investment)

        while event_idx < len(events) and t < events[event_idx].time <= target + 1e-12:
            group, next_event_idx = _events_at_time(events, event_idx)
            event_time = group[0].time
            state = _integrate_segment(config, state, t, event_time, shares, d_left.YR, regime)
            t = float(event_time)
            before = state
            after, regime, regime_name, attribution = _apply_ordered_event_group(
                before,
                group,
                config,
                regime,
                regime_name,
            )
            residual = attribution["delta_log_YR"] - (
                attribution["delta_log_OmegaP"] + attribution["delta_log_OmegaI"]
            )
            if abs(residual) > 1e-8:
                warnings.append(f"Event attribution residual at t={t:.4f}: {residual:.3e}")
            event_rows.append(
                {
                    "t": t,
                    "name": "; ".join(event.name for event in group),
                    "kind": "+".join(sorted({event.kind for event in group})),
                    "regime": regime_name,
                    **attribution,
                    "attribution_residual": residual,
                }
            )
            state = after
            event_idx = next_event_idx
            d_left = derived_indicators(state, config.params)
            shares = recommend_shares(state, config.params, config.share_policy)
            flow, controls = map_investments(d_left.YR, shares, config.params.investment)

        state = _integrate_segment(config, state, t, target, shares, d_left.YR, regime)
        t = float(target)
        rows.append(_row(t, state, config, shares, flow, controls, regime_name))

    trace = pd.DataFrame(rows).drop_duplicates(subset=["t"], keep="last").reset_index(drop=True)
    times = trace["t"].to_numpy(dtype=float)
    log_yi = np.log(trace["YI"].to_numpy(dtype=float))
    log_yr = np.log(trace["YR"].to_numpy(dtype=float))
    trace["v_h"] = speed_ratio(log_yi, log_yr, times, config.sim.speed_window, config.sim.eps_v)
    trace["cumulative_reflection_loss"] = cumulative_reflection_loss(
        times,
        trace["YI"].to_numpy(dtype=float),
        trace["YR"].to_numpy(dtype=float),
    )
    if len(warnings) > config.sim.max_step_warnings:
        warnings = warnings[: config.sim.max_step_warnings] + ["Additional warnings suppressed."]
    return SimulationResult(config, trace, pd.DataFrame(event_rows), warnings)
