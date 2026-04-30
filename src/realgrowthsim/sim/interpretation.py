from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd

BRANCH_LABELS = {
    "C": "installed compute itself",
    "E": "electricity capacity",
    "G": "grid/interconnection throughput",
    "M": "materials throughput",
    "W": "cooling/water throughput",
    "L": "permitting/construction throughput",
}


@dataclass(frozen=True)
class SimulationInterpretation:
    realization_ratio: float
    main_drag: str
    active_bottleneck: str
    bottleneck_pressure: float
    speed_ratio: float | None
    headline: str
    bottleneck_sentence: str
    speed_sentence: str
    next_experiments: tuple[str, ...]


def _clean_speed(value: object) -> float | None:
    try:
        speed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(speed):
        return None
    return speed


def _drag_label(gap_p: float, gap_i: float) -> str:
    if gap_p > 1.2 * max(gap_i, 1e-12):
        return "physical"
    if gap_i > 1.2 * max(gap_p, 1e-12):
        return "institutional"
    return "mixed"


def _pressure_label(bpi: float) -> str:
    if bpi < 0.1:
        return "low"
    if bpi < 0.3:
        return "moderate"
    return "high"


def interpret_trace(trace: pd.DataFrame) -> SimulationInterpretation:
    """Convert a numerical trace into a stable, user-facing reading.

    This module deliberately sits outside Streamlit so GUI text, reports, and
    tests can share one interpretation layer without changing model equations.
    """

    if trace.empty:
        raise ValueError("trace must not be empty")
    last = trace.iloc[-1]
    yi = max(float(last["YI"]), 1e-12)
    yr = max(float(last["YR"]), 0.0)
    realization_ratio = min(max(yr / yi, 0.0), 1.0)
    gap_p = float(last["gapP"])
    gap_i = float(last["gapI"])
    main_drag = _drag_label(gap_p, gap_i)
    active = str(last["active_bottleneck"]) or "none"
    active_readable = ", ".join(BRANCH_LABELS.get(part, part) for part in active.split(",") if part)
    bpi = float(last["BPI"])
    pressure = _pressure_label(bpi)
    speed = _clean_speed(last.get("v_h"))

    if main_drag == "physical":
        headline = "Realized output is mainly limited by deployable physical capacity."
        next_experiments = (
            "Compare active-bottleneck and tie-aware allocation policies.",
            f"Raise the {active_readable or active} branch and rerun the same scenario.",
            "Check whether compute share remains high while Ceff/C is low.",
        )
    elif main_drag == "institutional":
        headline = "Realized output is mainly limited by institutional translation."
        next_experiments = (
            "Try the institutional acceleration preset or lower the risk parameter.",
            "Inspect S, R, U, and P to see which institutional state is weakest.",
            "Run Monte Carlo to test whether risk shocks push OmegaI below the floor.",
        )
    else:
        headline = "Physical and institutional bottlenecks both materially reduce realization."
        next_experiments = (
            "Compare coordinated physical relief with institutional acceleration.",
            "Use the allocation lab to see whether diversified policies reduce loss.",
            "Run Monte Carlo to check whether tail losses come from BPI or OmegaI.",
        )

    bottleneck_sentence = (
        f"Current physical pressure is {pressure}: BPI={bpi:.2f}, so roughly {100.0 * bpi:.0f}% "
        f"of installed compute is physically blocked in this scenario. Active branch: {active_readable or active}."
    )
    if speed is None:
        speed_sentence = "The speed ratio is not reported because potential progress barely moved over the selected window."
    elif speed < 0.9:
        speed_sentence = f"Realized growth is lagging capability growth: v_h={speed:.2f}."
    elif speed <= 1.1:
        speed_sentence = f"Realized growth is moving roughly with capability growth: v_h={speed:.2f}."
    else:
        speed_sentence = f"Realized growth is temporarily faster than capability growth: v_h={speed:.2f}."

    return SimulationInterpretation(
        realization_ratio=realization_ratio,
        main_drag=main_drag,
        active_bottleneck=active,
        bottleneck_pressure=bpi,
        speed_ratio=speed,
        headline=headline,
        bottleneck_sentence=bottleneck_sentence,
        speed_sentence=speed_sentence,
        next_experiments=next_experiments,
    )
