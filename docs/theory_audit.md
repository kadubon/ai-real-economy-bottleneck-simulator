# Theory Audit

This audit compares the implementation against the two cited Takahashi 2026 papers.

## Alignment Summary

- The 12-state vector matches the main paper: `A,H,C,E,G,M,W,L,S,R,U,P`.
- The information layer implements the paper equations for `YI`, `A_dot`, `H_dot`, `C_dot`, and canonical `Theta(A,H)`.
- The investment closure uses the bounded map `F = F_bar * YR / (y_bar + YR)` and share constraints with floors and `sum(s) <= s_bar`.
- The physical channel implements the exact minimum over compute-equivalent branches, plus an optional smooth-min approximation.
- The institutional channel implements bounded `S,R,U,P` dynamics, the regulatory gate, and `OmegaI`.
- Event handling now groups coincident timestamps and applies `regime update -> physical jumps -> institutional jumps`.
- Information-layer states remain path-continuous at events.
- The rule engine covers the main operational families: decomposition, speed identity, event attribution, cumulative loss, physical bottlenecks, overbuild, institutional floor checks, robust diversification, KKT, and CVaR helpers.
- GUI variable and parameter explanations are generated from `model.catalog`, reducing the risk that labels drift away from implemented equations.
- The GUI's `Current Reading` panel is generated from `sim.interpretation`, a testable non-GUI module, so intuitive explanations are not hard-coded separately from reports.
- The first GUI panel now plots `YI` and `YR` against model time, making the paper's information-space versus realized-output distinction visible before users enter the tab workflow.
- One-click scenario buttons expose the main paper scenario families without requiring parameter editing, while still running the same simulation engine and presets.

## Code Review Notes

- The ODE right-hand side is isolated in `model.dynamics.state_derivative`; this is the main extension point for theory changes.
- Algebraic identities remain in pure functions under `model.equations`; tests exercise these without going through Streamlit.
- Event grouping is implemented in `sim.engine._apply_ordered_event_group`, so simultaneous events do not depend on JSON list order across event classes.
- Institutional initial-state controls in the GUI are bounded by `[0, 1]`, matching the Pydantic state schema and the paper's bounded institutional state assumption.
- Numerical integration now converts arrays back to states through `StateVector.from_array_guarded`, so small solver overshoots are clipped to the admissible domain instead of becoming schema failures.
- Rule registry now exposes T4 long-run identity, P6 BPI safety barrier, and P8 heavy-traffic diagnostics in addition to the prior core diagnostics.

## Conservative Interpretations

- Smooth-min error bound: the supplement states a bound for the map `u -> (u / (C + eps_C))^theta`. The simulator's physical reflection equation uses `u -> ((u + eps_C) / (C + eps_C))^theta`, so the implementation reports a model-consistent conservative bound for the actual simulated `OmegaP`.
- Heavy-traffic utilization: the theorem assumes `rho in (0,1)`. The simulator estimates `rho` as installed compute divided by the smallest non-compute physical capacity, clipped below one. This avoids using `C/Ceff`, which can exceed one and would not match the theorem domain.
- CVaR allocation: the code provides sample CVaR evaluation and an SLSQP solver for convex linear-loss samples. The GUI's `cvar` share policy remains a conservative heuristic unless a user supplies a formal loss matrix.

## Known Gaps

- The GUI rule engine presents the most operational subset of theorem outputs. It does not expose every proof-level assumption from the papers as an editable field.
- Stochastic diffusion for institutional states is represented through seeded incident simulations and risk formulas, not a full continuous-time SDE solver.
- Estimation and identification protocols from the main paper are documented but not implemented as SMC/PMCMC estimators.

## Audit Commands

```powershell
uv run ruff check .
uv run pytest
uv run realgrowthsim validate --preset baseline
```
