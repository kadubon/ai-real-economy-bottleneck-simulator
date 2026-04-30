# GUI Guide

Open the Streamlit app URL or run locally:

```powershell
uv run realgrowthsim gui
```

The first screen starts with one-click scenarios and a time-series comparison of `YI` and `YR`: information-space AI potential versus realized real-economy output. The horizontal axis is model time, and the shaded gap is the lost translation from bottlenecks.

Suggested first use:

1. Click **Baseline** and look at the blue-green gap.
2. Click **AI fast / bottlenecks slow** and check whether the green line falls further behind.
3. Click **Physical coordination** to see whether coordinated bottleneck relief narrows the gap.
4. Click **Resource + trust shock** to see how adverse events are attributed.

The app has eight tabs. Each tab includes plain-language text so the screen can be read without consulting the paper first:

1. Overview: model diagram and current scenario summary.
2. Scenario Builder: select presets and run; advanced sections contain direct state, parameter, and share editing.
3. Simulation Dashboard: start with `Current Reading`, then chart outputs, gaps, reflections, bottlenecks, speed ratio, and events.
4. Bottleneck Diagnostics: current active branch, tie set, BPI, switch-time benchmarks, and overbuild warning.
5. Policy / Allocation Lab: compare fixed, active-bottleneck, tie-aware, robust, KKT, and CVaR-style policies.
6. Rule Engine: theorem/rule diagnostics with status colors and recommended lever classes.
7. Monte Carlo / Risk: stochastic incidents, quantile bands, and tail-loss estimates.
8. Export / Report: CSV, JSON, and Markdown exports.

Do not enter personal, confidential, financial, health, biometric, or sensitive data.

Variable tooltips are generated from the model catalog:

- `A,H,C`: capability and compute layer.
- `E,G,M,W,L`: physical translation layer.
- `S,R,U,P`: institutional translation layer.
- `YI,YR,OmegaP,OmegaI,Ceff,BPI,g,v_h`: derived indicators.

The `Current Reading` panel translates the trace into four plain-language checks: how much potential is realized, whether the main drag is physical or institutional, which physical branch is active, and whether realized growth is keeping up with capability growth.
