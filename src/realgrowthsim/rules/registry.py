from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Rule:
    rule_id: str
    name: str
    input_indicators: tuple[str, ...]
    lever_class: str
    formula: str
    assumptions: str
    explanation: str
    evaluator: Callable[[pd.DataFrame, pd.DataFrame], RuleDiagnostic]


@dataclass(frozen=True)
class RuleDiagnostic:
    rule_id: str
    name: str
    status: str
    condition_satisfied: bool
    indicator_values: dict[str, float | str | bool]
    recommended_lever_class: str
    assumption_warnings: list[str]
    explanation: str

    def as_dict(self) -> dict[str, object]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "status": self.status,
            "condition_satisfied": self.condition_satisfied,
            "indicator_values": self.indicator_values,
            "recommended_lever_class": self.recommended_lever_class,
            "assumption_warnings": self.assumption_warnings,
            "explanation": self.explanation,
        }


def _status(ok: bool, warn: bool = False) -> str:
    if warn:
        return "yellow"
    return "green" if ok else "red"


def _last(trace: pd.DataFrame) -> pd.Series:
    return trace.iloc[-1]


def _core_speed(trace: pd.DataFrame, _events: pd.DataFrame) -> RuleDiagnostic:
    valid = trace["v_h"].dropna()
    avg = float(valid.mean()) if len(valid) else float("nan")
    dlog_yi = float(trace["YI"].iloc[-1] / trace["YI"].iloc[0] - 1.0)
    condition = bool(len(valid) and avg < 1.0 and dlog_yi > 0)
    return RuleDiagnostic(
        "T2",
        "Window speed identity",
        _status(not condition, condition),
        condition,
        {"average_v_h": avg, "YI_fractional_change": dlog_yi},
        "physical or institutional translation",
        [],
        "Persistent speed ratio below 1 with rising capability indicates translation deterioration.",
    )


def _event_attribution(trace: pd.DataFrame, events: pd.DataFrame) -> RuleDiagnostic:
    if events.empty:
        return RuleDiagnostic(
            "T3",
            "Event attribution",
            "green",
            True,
            {"event_count": 0},
            "event recovery",
            [],
            "No events were present; jump attribution is vacuously satisfied.",
        )
    max_residual = float(events["attribution_residual"].abs().max())
    ok = max_residual <= 1e-7
    return RuleDiagnostic(
        "T3",
        "Event attribution",
        _status(ok),
        ok,
        {"event_count": int(len(events)), "max_residual": max_residual},
        "split recovery across physical and institutional channels",
        [] if ok else ["Attribution residual exceeds tolerance."],
        "At event times, realized-output jumps should equal physical plus institutional reflection jumps.",
    )


def _gap_decomposition(trace: pd.DataFrame, _events: pd.DataFrame) -> RuleDiagnostic:
    err = float((trace["gap"] - trace["gapP"] - trace["gapI"]).abs().max())
    ok = err <= 1e-8
    return RuleDiagnostic(
        "T1",
        "Log gap decomposition",
        _status(ok),
        ok,
        {"max_gap_identity_error": err},
        "capability, physical, institutional",
        [] if ok else ["g != gP + gI within tolerance."],
        "The realized-output gap is the sum of physical and institutional log reflection losses.",
    )


def _long_run_identity(trace: pd.DataFrame, _events: pd.DataFrame) -> RuleDiagnostic:
    first = trace.iloc[0]
    last = trace.iloc[-1]
    dlog_yr = float(math.log(last["YR"]) - math.log(first["YR"]))
    dlog_yi = float(math.log(last["YI"]) - math.log(first["YI"]))
    dlog_omega_p = float(math.log(last["OmegaP"]) - math.log(first["OmegaP"]))
    dlog_omega_i = float(math.log(last["OmegaI"]) - math.log(first["OmegaI"]))
    residual = dlog_yr - (dlog_yi + dlog_omega_p + dlog_omega_i)
    ok = abs(residual) <= 1e-8
    return RuleDiagnostic(
        "T4",
        "Long-run realized growth identity",
        _status(ok),
        ok,
        {
            "delta_log_YR": dlog_yr,
            "delta_log_YI": dlog_yi,
            "delta_log_OmegaP": dlog_omega_p,
            "delta_log_OmegaI": dlog_omega_i,
            "identity_residual": residual,
        },
        "capability, physical, institutional",
        [] if ok else ["Long-window log identity residual exceeds tolerance."],
        "Over the full window, realized log growth equals capability log growth plus physical and institutional reflection changes.",
    )


def _physical_bottleneck(trace: pd.DataFrame, _events: pd.DataFrame) -> RuleDiagnostic:
    last = _last(trace)
    bpi = float(last["BPI"])
    active = str(last["active_bottleneck"])
    warn = bpi > 0.25
    return RuleDiagnostic(
        "P1",
        "Active bottleneck detection",
        _status(not warn, warn),
        bool(active),
        {"BPI": bpi, "active_set": active},
        "active physical branch",
        [],
        "With a unique active branch, first-order physical relief should target that branch.",
    )


def _bpi_barrier(trace: pd.DataFrame, _events: pd.DataFrame) -> RuleDiagnostic:
    threshold = 0.5
    max_bpi = float(trace["BPI"].max())
    ok = max_bpi <= threshold
    return RuleDiagnostic(
        "P6",
        "BPI safety barrier",
        _status(ok, not ok),
        ok,
        {"max_BPI": max_bpi, "threshold": threshold},
        "physical safety filter",
        [] if ok else ["BPI exceeded the default safety threshold."],
        "BPI should remain below a chosen safety threshold when deployment pressure is constrained.",
    )


def _heavy_traffic(trace: pd.DataFrame, _events: pd.DataFrame) -> RuleDiagnostic:
    last = _last(trace)
    util = float(last.get("utilization", 0.0))
    warn = util >= 0.9
    amplification = min(1.0 / max((1.0 - min(util, 0.999999)) ** 2, 1e-12), 1e6)
    return RuleDiagnostic(
        "P8",
        "Heavy-traffic delay amplification",
        _status(not warn, warn),
        not warn,
        {"utilization": util, "delay_amplification_proxy": amplification},
        "congestion relief",
        [] if not warn else ["Utilization is close to one; small relief can have large delay effects."],
        "When utilization approaches one, delay sensitivity rises nonlinearly; the displayed proxy is capped for readability.",
    )


def _overbuild(trace: pd.DataFrame, _events: pd.DataFrame) -> RuleDiagnostic:
    last = _last(trace)
    ratio = float(last["Ceff"] / max(last["C"], 1e-12))
    warn = ratio < 0.8 and float(last.get("share_C", 0.0)) > 0.25
    return RuleDiagnostic(
        "C3",
        "Overbuild penalty",
        _status(not warn, warn),
        warn,
        {"Ceff_over_C": ratio, "share_C": float(last.get("share_C", 0.0))},
        "deprioritize compute-only expansion",
        [],
        "Compute expansion under fixed deployable feasibility lowers translation efficiency.",
    )


def _institutional_floor(trace: pd.DataFrame, _events: pd.DataFrame) -> RuleDiagnostic:
    last = _last(trace)
    omega_i = float(last["OmegaI"])
    warn = omega_i < 0.65
    return RuleDiagnostic(
        "I4/I5",
        "Institutional floor",
        _status(not warn, warn),
        not warn,
        {"OmegaI": omega_i, "S": float(last["S"]), "R": float(last["R"]), "U": float(last["U"]), "P": float(last["P"])},
        "institutional mean lift or variance reduction",
        [],
        "Institutional safety margins should be checked when OmegaI approaches low-floor thresholds.",
    )


def _robust_diversification(trace: pd.DataFrame, _events: pd.DataFrame) -> RuleDiagnostic:
    last = _last(trace)
    active = str(last["active_bottleneck"])
    tie = str(last["tie_set"])
    condition = bool(tie)
    return RuleDiagnostic(
        "A1/C5",
        "Robust concentration/diversification",
        _status(not condition, condition),
        condition,
        {"active_set": active, "tie_set": tie},
        "diversified top-lever allocation",
        [],
        "Ties or near-ties make hidden deterministic concentration fragile; diversify across likely active levers.",
    )


def _cumulative_loss(trace: pd.DataFrame, _events: pd.DataFrame) -> RuleDiagnostic:
    last = _last(trace)
    loss = float(last["cumulative_reflection_loss"])
    gap = float(last["gap"])
    warn = gap > 0.25
    return RuleDiagnostic(
        "T7",
        "Cumulative reflection loss",
        _status(not warn, warn),
        loss >= 0.0,
        {"loss": loss, "final_gap": gap},
        "gap reduction",
        [],
        "Persistent positive gaps imply cumulative lost realized output relative to latent capability.",
    )


def rule_registry() -> list[Rule]:
    return [
        Rule("T1", "Off-event log-growth decomposition", ("gap", "gapP", "gapI"), "all channels", "g = gP + gI", "positive outputs", "Decomposes realized growth into capability and translation channels.", _gap_decomposition),
        Rule("T2", "Window speed identity", ("v_h", "YI"), "translation", "v_h = Delta log YR / Delta log YI", "nonzero denominator", "Diagnoses whether realized speed lags capability speed.", _core_speed),
        Rule("T3", "Event attribution", ("jump_logYR", "jump_logOmegaP", "jump_logOmegaI"), "recovery", "Delta log YR = Delta log OmegaP + Delta log OmegaI", "YI path-continuous at events", "Separates event losses into physical and institutional components.", _event_attribution),
        Rule("T4", "Long-run realized growth identity", ("YI", "YR", "OmegaP", "OmegaI"), "all channels", "Delta log YR = Delta log YI + Delta log OmegaP + Delta log OmegaI", "positive outputs", "Checks the full-window reflection-adjusted growth identity.", _long_run_identity),
        Rule("T7", "Cumulative reflection-loss lower bound", ("gap", "YI", "YR"), "gap reduction", "L(T)=int(YI-YR)dt", "positive gap window", "Turns persistent gaps into cumulative loss diagnostics.", _cumulative_loss),
        Rule("P1", "Active bottleneck marginal effect", ("active_set", "BPI"), "physical", "argmin branch has first-order return", "unique or tie-aware active set", "Targets the binding physical branch.", _physical_bottleneck),
        Rule("P6", "BPI safety barrier", ("BPI",), "physical", "sup_t BPI_t <= threshold", "chosen safety threshold", "Flags physical pressure threshold breaches.", _bpi_barrier),
        Rule("P8", "Heavy-traffic delay amplification", ("utilization",), "physical", "delay gain proportional to (1-rho)^-2", "rho in [0,1)", "Flags congestion sensitivity near high utilization.", _heavy_traffic),
        Rule("C3", "Overbuild penalty", ("Ceff/C", "share_C"), "physical", "d log YR / dC < 0 at fixed Ceff", "fixed deployable feasibility", "Flags compute-only overbuild.", _overbuild),
        Rule("I4/I5", "Institutional floor conditions", ("OmegaI",), "institutional", "Gaussian or Cantelli margin", "mean/variance forecasts available for formal chance checks", "Flags institutional reflection weakness.", _institutional_floor),
        Rule("A1/C5", "Robust diversification trigger", ("active_set", "tie_set"), "allocation", "worst-best robust margin", "impact uncertainty", "Flags concentration fragility.", _robust_diversification),
    ]


def evaluate_rules(trace: pd.DataFrame, events: pd.DataFrame) -> list[RuleDiagnostic]:
    return [rule.evaluator(trace, events) for rule in rule_registry()]
