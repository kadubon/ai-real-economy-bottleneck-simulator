from __future__ import annotations

import copy

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from realgrowthsim.gui.components import (
    CHART_EXPLANATIONS,
    DISCLAIMER,
    interpretation_panel,
    label,
    metric_row,
    show_glossary,
    top_growth_comparison,
)
from realgrowthsim.io.export import diagnostics_to_json
from realgrowthsim.io.report import markdown_report
from realgrowthsim.io.schema import scenario_from_json, scenario_to_json
from realgrowthsim.model.catalog import (
    STATE_CATALOG,
    help_text,
)
from realgrowthsim.model.params import ScenarioConfig, SharePolicy
from realgrowthsim.rules.physical import (
    deterministic_switch_time_upper_bound,
    lead_time_preemption_deadline,
    noisy_switch_time_moments,
    overbuild_penalty,
)
from realgrowthsim.rules.registry import evaluate_rules
from realgrowthsim.sim.engine import SimulationResult, simulate
from realgrowthsim.sim.scenarios import preset_configs
from realgrowthsim.sim.stochastic import run_monte_carlo


def _init_state() -> None:
    if "presets" not in st.session_state:
        st.session_state.presets = preset_configs()
    if "scenario" not in st.session_state:
        st.session_state.scenario = copy.deepcopy(st.session_state.presets["baseline"])
    if "result" not in st.session_state:
        st.session_state.result = simulate(st.session_state.scenario)


def _run(config: ScenarioConfig) -> SimulationResult:
    result = simulate(config)
    st.session_state.scenario = config
    st.session_state.result = result
    return result


def quick_scenario_bar() -> None:
    st.subheader("Try One-Click Scenarios")
    st.caption("Use these first if you only want to understand the model behavior without editing parameters.")
    presets: dict[str, ScenarioConfig] = st.session_state.presets
    choices = [
        (
            "baseline",
            "Baseline",
            "Balanced AI, physical capacity, and institutions.",
        ),
        (
            "information_fast_reflection_slow",
            "AI fast / bottlenecks slow",
            "Capability grows quickly, but translation cannot keep up.",
        ),
        (
            "physical_coordination_push",
            "Physical coordination",
            "Relieves electricity, grid, materials, cooling, and permitting together.",
        ),
        (
            "resource_trust_shock",
            "Resource + trust shock",
            "Adds adverse physical and institutional events.",
        ),
    ]
    cols = st.columns(len(choices))
    for col, (key, title, description) in zip(cols, choices, strict=True):
        col.markdown(f"**{title}**")
        col.caption(description)
        if col.button("Run", key=f"quick_run_{key}", width="stretch"):
            _run(copy.deepcopy(presets[key]))
            st.rerun()


def overview_tab(result: SimulationResult) -> None:
    st.subheader("Model Overview")
    st.info(DISCLAIMER)
    st.markdown(
        """
The simulator separates latent AI capability growth from realized real-economy growth.
Potential progress first arises from algorithmic knowledge, AI-augmented research effort,
and installed compute. Realized output is then filtered by physical and institutional
reflection factors.
"""
    )
    st.markdown(
        """
Plain-language reading: the app asks whether AI progress is merely increasing *potential*
or whether the physical economy and institutions can convert that potential into realized output.
"""
    )
    st.markdown(
        """
What this can show:

- whether realized output `YR` keeps pace with potential progress `YI`
- whether the translation gap is mainly physical, institutional, or both
- which physical branch is currently binding
- whether compute investment is outpacing electricity, grid, materials, cooling, or permitting
- how model-based allocation rules change losses and bottleneck pressure
"""
    )
    fig = go.Figure()
    nodes = ["AI capability layer", "Physical reflection", "Institutional reflection", "Realized growth"]
    for i, node_label in enumerate(nodes):
        fig.add_annotation(x=i, y=0, text=node_label, showarrow=False, bgcolor="#eef2ff", bordercolor="#2563eb", borderwidth=1)
        if i < len(nodes) - 1:
            fig.add_annotation(x=i + 0.55, y=0, ax=i + 0.15, ay=0, xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=3)
    fig.update_xaxes(visible=False, range=[-0.4, 3.4])
    fig.update_yaxes(visible=False, range=[-0.8, 0.8])
    fig.update_layout(height=180, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, width="stretch")
    st.write(f"Current scenario: **{result.scenario.name}**")
    st.write(result.scenario.description)
    metric_row(result)
    interpretation_panel(result)
    show_glossary()


def scenario_builder_tab() -> None:
    st.subheader("Scenario Builder")
    st.write(
        "Build a scenario by changing initial conditions, model parameters, and allocation rules. "
        "All values are dimensionless index values unless the preset says it is paper-inspired."
    )
    st.info(
        "How to read numbers: for `A,H,C,E,G,M,W,L`, 1.0 is the preset baseline and 2.0 is roughly twice that index. "
        "`S,R,U,P` are bounded institutional scores from weak to 1.0. `BPI=0.30` means about 30% physical blockage."
    )
    presets: dict[str, ScenarioConfig] = st.session_state.presets
    config: ScenarioConfig = copy.deepcopy(st.session_state.scenario)
    preset_names = list(presets)
    selected = st.selectbox(
        "Preset scenario",
        preset_names,
        format_func=lambda key: presets[key].name,
        index=preset_names.index("baseline") if "baseline" in preset_names else 0,
        help="Paper scenario families plus additional stress tests.",
    )
    col_a, col_b, col_c = st.columns(3)
    if col_a.button("Reset to preset", width="stretch"):
        config = copy.deepcopy(presets[selected])
        st.session_state.scenario = config
    config = copy.deepcopy(st.session_state.scenario)

    with st.form("scenario_form"):
        st.caption(DISCLAIMER)
        c1, c2, c3 = st.columns(3)
        config.sim.horizon = c1.slider("Horizon", 2.0, 60.0, float(config.sim.horizon), 1.0, help=help_text("horizon"))
        config.sim.dt = c2.slider("dt", 0.02, 1.0, float(config.sim.dt), 0.02, help=help_text("dt"))
        config.sim.seed = c3.number_input("Random seed", 0, 10_000_000, int(config.sim.seed), help=help_text("seed"))
        config.units = st.radio(
            "Units",
            ["normalized", "paper_inspired"],
            index=0 if config.units == "normalized" else 1,
            horizontal=True,
            help="Normalized units are synthetic index values. Paper-inspired units are illustrative calibration anchors, not forecasts.",
        )
        config.share_policy.policy = SharePolicy(
            st.selectbox(
                "Share policy",
                [p.value for p in SharePolicy],
                index=[p.value for p in SharePolicy].index(config.share_policy.policy.value),
                help="Rule used to allocate bounded investment across compute and bottleneck-relief branches.",
            )
        )
        st.caption("Most users can choose a preset and click Run simulation. Open advanced sections only when you want to edit the model inputs directly.")

        with st.expander("Advanced: initial state", expanded=False):
            st.caption("Initial states describe where the simulated economy starts before the first time step.")
            cols = st.columns(6)
            for i, name in enumerate(["A", "H", "C", "E", "G", "M"]):
                setattr(
                    config.initial_state,
                    name,
                    cols[i].number_input(
                        label(name),
                        0.0001,
                        100.0,
                        float(getattr(config.initial_state, name)),
                        help=help_text(name),
                    ),
                )
            cols = st.columns(6)
            for i, name in enumerate(["W", "L", "S", "R", "U", "P"]):
                setattr(
                    config.initial_state,
                    name,
                    cols[i].number_input(
                        label(name),
                        0.0001,
                        1.0 if name in ["S", "R", "U", "P"] else 100.0,
                        float(getattr(config.initial_state, name)),
                        help=help_text(name),
                    ),
                )

        with st.expander("Advanced: growth and bottleneck parameters", expanded=False):
            st.caption("Core parameters control how fast capability, infrastructure, and institutions move.")
            c1, c2, c3, c4 = st.columns(4)
            config.params.information.chi_A = c1.slider("chi_A", 0.0, 0.3, float(config.params.information.chi_A), 0.005, help=help_text("chi_A"))
            config.params.information.chi_H = c2.slider("chi_H", 0.0, 0.3, float(config.params.information.chi_H), 0.005, help=help_text("chi_H"))
            config.params.physical.theta_P = c3.slider("theta_P", 0.05, 2.0, float(config.params.physical.theta_P), 0.05, help=help_text("theta_P"))
            config.params.institutional.risk = c4.slider("Risk", 0.0, 0.5, float(config.params.institutional.risk), 0.01, help=help_text("risk"))

        with st.expander("Advanced: investment shares", expanded=False):
            st.caption("Shares allocate the bounded investment flow F across compute and physical bottleneck branches.")
            cols = st.columns(6)
            for i, branch in enumerate(["C", "E", "G", "M", "W", "L"]):
                config.params.investment.fixed_shares[branch] = cols[i].slider(
                    f"s_{branch} ({STATE_CATALOG[branch].name if branch in STATE_CATALOG else branch})",
                    0.0,
                    0.8,
                    float(config.params.investment.fixed_shares.get(branch, 0.0)),
                    0.01,
                    help=f"Fixed share for {branch}. Shares are automatically clipped to floors and s_bar.",
            )
        submitted = st.form_submit_button("Run simulation", width="stretch")
    if submitted:
        _run(config)
        st.success("Simulation complete.")

    export_json = scenario_to_json(st.session_state.scenario)
    col_b.download_button(
        "Export scenario JSON",
        export_json,
        file_name="scenario.json",
        mime="application/json",
        width="stretch",
        key="scenario_builder_export_json",
    )
    uploaded = st.file_uploader("Import scenario JSON", type=["json"], help="Processed in session only. The app does not persist uploads.")
    text_json = st.text_area("Or paste scenario JSON", height=120)
    if col_c.button("Import pasted/uploaded JSON", width="stretch"):
        raw = text_json
        if uploaded is not None:
            raw = uploaded.getvalue().decode("utf-8")
        if raw.strip():
            try:
                _run(scenario_from_json(raw))
                st.success("Imported scenario and ran simulation.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Could not import scenario: {exc}")
    show_glossary()


def dashboard_tab(result: SimulationResult) -> None:
    st.subheader("Simulation Dashboard")
    st.write("Read this page as a translation dashboard: capability enters at YI, bottlenecks lower it to YR.")
    df = result.trace
    metric_row(result)
    interpretation_panel(result)
    for title, columns in [
        ("YI vs YR", ["YI", "YR"]),
        ("log YI vs log YR", ["YI", "YR"]),
        ("Gaps", ["gap", "gapP", "gapI"]),
        ("Reflection factors", ["OmegaP", "OmegaI"]),
        ("C, Ceff, Ceff/C", ["C", "Ceff"]),
        ("BPI", ["BPI"]),
        ("Institutional states", ["S", "R", "U", "P"]),
        ("Speed ratio v_h", ["v_h"]),
        ("Cumulative reflection loss", ["cumulative_reflection_loss"]),
    ]:
        st.caption(CHART_EXPLANATIONS.get(title, ""))
        plot_df = df[["t", *columns]].copy()
        if title == "log YI vs log YR":
            plot_df["log YI"] = plot_df["YI"].apply(lambda x: __import__("math").log(x))
            plot_df["log YR"] = plot_df["YR"].apply(lambda x: __import__("math").log(x))
            plot_df = plot_df[["t", "log YI", "log YR"]]
        if title == "C, Ceff, Ceff/C":
            plot_df["Ceff/C"] = df["Ceff"] / df["C"]
        st.plotly_chart(px.line(plot_df, x="t", y=[c for c in plot_df.columns if c != "t"], title=title), width="stretch")
    branch_cols = [c for c in df.columns if c.startswith("branch_")]
    st.caption("Each branch is measured in compute-equivalent capacity. The smallest branch is the active physical bottleneck.")
    st.plotly_chart(px.line(df, x="t", y=branch_cols, title="Branch values"), width="stretch")
    st.caption("Active bottleneck timeline shows which branch is currently limiting effective compute.")
    st.plotly_chart(px.scatter(df, x="t", y="active_bottleneck", title="Active bottleneck timeline"), width="stretch")
    share_cols = [c for c in df.columns if c.startswith("share_")]
    st.caption("Investment shares show how the model allocates the bounded deployment budget over time.")
    st.plotly_chart(px.area(df, x="t", y=share_cols, title="Investment shares"), width="stretch")
    if not result.events.empty:
        st.dataframe(result.events, width="stretch")


def diagnostics_tab(result: SimulationResult) -> None:
    st.subheader("Bottleneck Diagnostics")
    st.write(
        "This tab explains what is currently limiting realized growth. "
        "The active bottleneck is the smallest compute-equivalent branch."
    )
    df = result.trace
    last = df.iloc[-1]
    cols = st.columns(4)
    cols[0].metric("Active bottleneck", str(last["active_bottleneck"]))
    cols[1].metric("Tie set", str(last["tie_set"]) or "none")
    cols[2].metric("BPI", f"{last['BPI']:.3f}")
    cols[3].metric("Smooth-min bound", f"{last['smooth_min_error_bound']:.3e}")
    branch_cols = [c for c in df.columns if c.startswith("branch_")]
    latest_branches = {c.replace("branch_", ""): float(last[c]) for c in branch_cols}
    st.bar_chart(pd.Series(latest_branches, name="branch value"))
    st.caption("Lower branch values are more restrictive. Equal low values indicate a tie set.")
    sorted_branches = sorted(latest_branches.items(), key=lambda item: item[1])
    if len(sorted_branches) >= 2:
        h0 = max(0.0, __import__("math").log(sorted_branches[1][1] / max(sorted_branches[0][1], 1e-12)))
        eta = 0.03
        tau = deterministic_switch_time_upper_bound(h0, eta)
        mean_tau, var_tau = noisy_switch_time_moments(h0, eta, sigma=0.02)
        st.write(f"Switch-time benchmark: deterministic upper bound {tau:.2f}; noisy mean {mean_tau:.2f}, variance {var_tau:.2f}.")
        st.write(f"Lead-time preemption deadline with 1.5 time-unit lead quantile: {lead_time_preemption_deadline(tau, 1.5):.2f}.")
    st.write(f"Overbuild penalty sign check: {overbuild_penalty(float(last['C']), result.scenario.params.physical.eps_C, result.scenario.params.physical.theta_P):.4f}")
    if float(last["BPI"]) > 0.3:
        st.warning("Bottleneck pressure is high; realized growth is limited mainly by deployable feasibility.")
    else:
        st.success("Bottleneck pressure is not high under the current scenario.")


def allocation_lab_tab(result: SimulationResult) -> None:
    st.subheader("Policy / Allocation Lab")
    st.caption("Model-based diagnostic, not a real-world policy prescription.")
    st.write(
        "The lab reruns the same scenario under alternative share rules. "
        "It compares outcomes, not real-world policy recommendations."
    )
    policies = [
        SharePolicy.fixed,
        SharePolicy.active_bottleneck,
        SharePolicy.tie_aware,
        SharePolicy.robust_diversification,
        SharePolicy.kkt,
        SharePolicy.cvar,
    ]
    rows = []
    for policy in policies:
        cfg = copy.deepcopy(result.scenario)
        cfg.share_policy.policy = policy
        trial = simulate(cfg)
        summary = trial.summary()
        rows.append(
            {
                "policy": policy.value,
                "final_YR": summary["final_YR"],
                "average_speed_ratio": summary["average_speed_ratio"],
                "cumulative_reflection_loss": summary["cumulative_reflection_loss"],
                "max_BPI": summary["max_BPI"],
                "worst_tail_loss": float((trial.trace["YI"] - trial.trace["YR"]).quantile(0.95)),
                "safety_violations": int((trial.trace["BPI"] > 0.5).sum()),
            }
        )
    comp = pd.DataFrame(rows)
    st.dataframe(comp, width="stretch")
    st.plotly_chart(px.bar(comp, x="policy", y="final_YR", title="Final realized output by policy"), width="stretch")
    best = comp.sort_values(["final_YR", "max_BPI"], ascending=[False, True]).iloc[0]
    st.info(f"Current model-based allocation diagnostic favors: {best['policy']}.")


def rule_engine_tab(result: SimulationResult) -> None:
    st.subheader("Rule Engine")
    st.write(
        "Rules translate theorem-level identities and inequalities into diagnostics. "
        "Green means no issue detected; yellow means attention; red means an identity or constraint failed."
    )
    diagnostics = evaluate_rules(result.trace, result.events)
    rows = [d.as_dict() for d in diagnostics]
    table = pd.DataFrame(
        {
            "rule_id": [r["rule_id"] for r in rows],
            "name": [r["name"] for r in rows],
            "status": [r["status"] for r in rows],
            "condition_satisfied": [r["condition_satisfied"] for r in rows],
            "lever": [r["recommended_lever_class"] for r in rows],
            "explanation": [r["explanation"] for r in rows],
        }
    )
    st.dataframe(table, width="stretch")
    st.download_button(
        "Download rule diagnostics JSON",
        diagnostics_to_json(diagnostics),
        "rule_diagnostics.json",
        "application/json",
        key="rule_engine_download_diagnostics",
    )


def monte_carlo_tab(result: SimulationResult) -> None:
    st.subheader("Monte Carlo / Risk")
    st.write(
        "Monte Carlo runs add seeded synthetic incidents to estimate downside sensitivity. "
        "These are stress tests, not probabilistic forecasts."
    )
    c1, c2 = st.columns(2)
    n = c1.slider("Runs", 5, 200, 30, 5)
    incidents = c2.slider("Incidents per run", 0, 8, 2, 1)
    if st.button("Run Monte Carlo", width="stretch"):
        with st.spinner("Running stochastic simulations..."):
            _, mc = run_monte_carlo(result.scenario, n=n, incidents=incidents)
        st.session_state.mc = mc
    mc = st.session_state.get("mc")
    if mc is not None:
        quant = mc.groupby("t")[["YR", "gap", "BPI", "OmegaI"]].quantile([0.05, 0.5, 0.95]).reset_index()
        for metric in ["YR", "gap", "BPI", "OmegaI"]:
            q = quant.pivot(index="t", columns="level_1", values=metric).reset_index()
            q.columns = ["t", "q05", "q50", "q95"]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=q["t"], y=q["q95"], line=dict(width=0), showlegend=False))
            fig.add_trace(go.Scatter(x=q["t"], y=q["q05"], fill="tonexty", line=dict(width=0), name="5-95%"))
            fig.add_trace(go.Scatter(x=q["t"], y=q["q50"], name="median"))
            fig.update_layout(title=f"{metric} quantile band")
            st.plotly_chart(fig, width="stretch")
        horizon_loss = mc.groupby("run").apply(lambda g: float(g["YI"].iloc[-1] - g["YR"].iloc[-1]), include_groups=False)
        st.metric("Horizon CVaR 90%", f"{horizon_loss[horizon_loss >= horizon_loss.quantile(0.9)].mean():.3f}")
        st.download_button(
            "Export Monte Carlo CSV",
            mc.to_csv(index=False),
            "monte_carlo.csv",
            "text/csv",
            key="monte_carlo_download_csv",
        )


def export_report_tab(result: SimulationResult) -> None:
    st.subheader("Export / Report")
    st.write("Export reproducible traces, scenarios, diagnostics, and a compact report for review.")
    diagnostics = evaluate_rules(result.trace, result.events)
    st.download_button("Download CSV trace", result.trace.to_csv(index=False), "trace.csv", "text/csv", key="export_download_trace")
    st.download_button("Download scenario JSON", scenario_to_json(result.scenario), "scenario.json", "application/json", key="export_download_scenario")
    st.download_button(
        "Download rule diagnostics JSON",
        diagnostics_to_json(diagnostics),
        "rule_diagnostics.json",
        "application/json",
        key="export_download_diagnostics",
    )
    report = markdown_report(result, diagnostics)
    st.download_button("Download Markdown report", report, "simulation_report.md", "text/markdown", key="export_download_report")


def main() -> None:
    st.set_page_config(page_title="AI Real-Economy Bottleneck Simulator", layout="wide")
    _init_state()
    result: SimulationResult = st.session_state.result
    st.title("AI Real-Economy Bottleneck Simulator")
    st.caption(DISCLAIMER)
    quick_scenario_bar()
    top_growth_slot = st.container()
    tabs = st.tabs(
        [
            "Overview",
            "Scenario Builder",
            "Simulation Dashboard",
            "Bottleneck Diagnostics",
            "Policy / Allocation Lab",
            "Rule Engine",
            "Monte Carlo / Risk",
            "Export / Report",
        ]
    )
    with tabs[0]:
        overview_tab(result)
    with tabs[1]:
        scenario_builder_tab()
    result = st.session_state.result
    with top_growth_slot:
        top_growth_comparison(result)
    with tabs[2]:
        dashboard_tab(result)
    with tabs[3]:
        diagnostics_tab(result)
    with tabs[4]:
        allocation_lab_tab(result)
    with tabs[5]:
        rule_engine_tab(result)
    with tabs[6]:
        monte_carlo_tab(result)
    with tabs[7]:
        export_report_tab(result)


if __name__ == "__main__":
    main()
