from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from realgrowthsim.model.catalog import (
    INDICATOR_CATALOG,
    PARAMETER_CATALOG,
    STATE_CATALOG,
    catalog_table,
)
from realgrowthsim.sim.engine import SimulationResult
from realgrowthsim.sim.interpretation import interpret_trace

DISCLAIMER = (
    "Research simulation tool. Not financial, investment, energy-policy, or regulatory advice. "
    "Do not enter personal, confidential, financial, health, biometric, or sensitive data."
)

CHART_EXPLANATIONS = {
    "YI vs YR": "YI is the model's latent capability output; YR is what remains after physical and institutional translation losses.",
    "log YI vs log YR": "The vertical distance between these log series is the translation gap.",
    "Gaps": "Total gap equals physical gap plus institutional gap. Larger values mean more capability is failing to translate.",
    "Reflection factors": "OmegaP and OmegaI are multipliers between 0 and 1. Lower values mean stronger bottlenecks.",
    "C, Ceff, Ceff/C": "Installed compute can exceed effective compute when electricity, grid, materials, cooling, or permitting bind.",
    "BPI": "BPI is a physical pressure gauge: 0 means no physical shortfall; values near 1 mean severe physical blockage.",
    "Institutional states": "S, R, U, and P summarize social acceptance, regulation, institutional readiness, and operations.",
    "Speed ratio v_h": "A value below 1 means realized growth is slower than capability growth over the chosen window.",
    "Cumulative reflection loss": "Cumulative area between potential and realized output.",
}


def label(symbol: str) -> str:
    item = STATE_CATALOG.get(symbol) or INDICATOR_CATALOG.get(symbol)
    return f"{symbol} - {item.name}" if item else symbol


def show_glossary() -> None:
    with st.expander("Variable glossary", expanded=False):
        st.markdown(
            "State variables are the model stocks. Most are normalized indexes: `1.0` means the preset baseline, "
            "`2.0` is roughly twice that level, and institutional states `S,R,U,P` run from weak to the model maximum `1.0`."
        )
        st.dataframe(pd.DataFrame(catalog_table(STATE_CATALOG)), width="stretch", hide_index=True)
        st.dataframe(pd.DataFrame(catalog_table(INDICATOR_CATALOG)), width="stretch", hide_index=True)
    with st.expander("Core parameter glossary", expanded=False):
        st.markdown("Parameters are controls that change the equations rather than stocks measured in the trace.")
        st.dataframe(pd.DataFrame(catalog_table(PARAMETER_CATALOG)), width="stretch", hide_index=True)


def metric_row(result: SimulationResult) -> None:
    summary = result.summary()
    cols = st.columns(5)
    cols[0].metric("Realized output YR", f"{summary['final_YR']:.3f}")
    cols[1].metric("Gap YI to YR", f"{summary['final_gap']:.3f}")
    avg = summary["average_speed_ratio"]
    cols[2].metric("Speed ratio v_h", "n/a" if pd.isna(avg) else f"{avg:.3f}")
    cols[3].metric("Max BPI", f"{summary['max_BPI']:.3f}")
    cols[4].metric("Lost output L(T)", f"{summary['cumulative_reflection_loss']:.3f}")


def top_growth_comparison(result: SimulationResult) -> None:
    df = result.trace
    interpretation = interpret_trace(df)
    st.subheader("AI Capability Growth vs Real-Economy Growth")
    st.caption(
        "Horizontal axis is model time. The blue line is information-space potential `YI`; "
        "the green line is realized real-economy output `YR` after bottlenecks."
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["t"],
            y=df["YI"],
            mode="lines",
            name="YI - information-space AI potential",
            line=dict(color="#2563eb", width=3),
            hovertemplate="time=%{x:.2f}<br>YI=%{y:.3f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["t"],
            y=df["YR"],
            mode="lines",
            name="YR - realized real-economy output",
            line=dict(color="#16a34a", width=3),
            fill="tonexty",
            fillcolor="rgba(37, 99, 235, 0.10)",
            hovertemplate="time=%{x:.2f}<br>YR=%{y:.3f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_title="Time",
        yaxis_title="Normalized output index",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
    )
    st.plotly_chart(fig, width="stretch")
    st.write(
        f"Current reading: {100.0 * interpretation.realization_ratio:.1f}% of potential is realized at the horizon. "
        f"Main drag: **{interpretation.main_drag}**. Active physical branch: **{interpretation.active_bottleneck}**."
    )
    with st.expander("How to read this chart", expanded=True):
        st.markdown(
            """
1. Start with the distance between the blue and green lines. A larger shaded area means more AI potential is not becoming real output.
2. If the green line bends away from the blue line, open **Bottleneck Diagnostics** to see which physical branch is binding.
3. Use the one-click scenarios above to test whether the gap is caused by fast AI growth, slow physical deployment, institutional drag, or shocks.
"""
        )


def interpretation_panel(result: SimulationResult) -> None:
    interpretation = interpret_trace(result.trace)
    st.subheader("Current Reading")
    st.info(interpretation.headline)
    cols = st.columns(4)
    cols[0].metric("Potential realized", f"{100.0 * interpretation.realization_ratio:.1f}%")
    cols[1].metric("Main drag", interpretation.main_drag)
    cols[2].metric("Active branch", interpretation.active_bottleneck)
    speed = "n/a" if interpretation.speed_ratio is None else f"{interpretation.speed_ratio:.2f}"
    cols[3].metric("v_h", speed)
    st.write(interpretation.bottleneck_sentence)
    st.write(interpretation.speed_sentence)
    with st.expander("Next scenario experiments", expanded=False):
        for item in interpretation.next_experiments:
            st.markdown(f"- {item}")
