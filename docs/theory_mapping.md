# Theory Mapping

| Paper item | Formula/rule | Implementation | Test | GUI location |
|---|---|---|---|---|
| Main Def. 3.1 / Supplement Def. 2.1 | `YR = OmegaP * OmegaI * YI` | `model.equations.realized_output`, `derived_indicators` | `test_equations.py` | Dashboard |
| Main Eq. 6 | `YI = A^alpha H^beta C^gamma` | `model.equations.potential_output` | `test_equations.py` | Dashboard |
| Main Eq. 7-11 | Information-layer dynamics | `model.dynamics.state_derivative` | `test_simulation.py` | Scenario Builder |
| Main Eq. 12-15 | Investment map and share constraints | `model.investment`, `model.equations.normalized_shares` | `test_allocation.py` | Scenario Builder / Allocation Lab |
| Main Eq. 16-18 | Physical branches, `Ceff`, `OmegaP`, `BPI` | `model.equations.branch_values`, `effective_compute`, `omega_physical` | `test_equations.py`, `test_rules_physical.py` | Diagnostics |
| Main Eq. 19-20 | Stock and flow physical dynamics | `model.dynamics.state_derivative` | `test_simulation.py` | Dashboard |
| Main Eq. 21-23 | Institutional dynamics, regulatory gate, `OmegaI` | `model.equations.regulatory_gate`, `omega_institutional` | `test_rules_institutional.py` | Rule Engine |
| Main Eq. 24-25 | Ordered event jumps | `model.events`, `sim.engine._apply_ordered_event_group` | `test_events.py` | Event table |
| T1 | Off-event log-growth decomposition | `rules.registry`, trace columns | `test_rules_core.py` | Rule Engine |
| T2 | Window speed identity | `model.equations.speed_ratio` | `test_equations.py`, `test_rules_core.py` | Dashboard / Rule Engine |
| T3 | Event attribution | `sim.engine._event_attribution` | `test_events.py` | Dashboard / Rule Engine |
| T4 | Long-run realized growth identity | `rules.registry._long_run_identity` | `test_rules_core.py` | Rule Engine |
| T5-T6 | Required physical/institutional relief | `rules.core` | `test_rules_core.py` | Rule Engine |
| P1-P2 | Active and tie-aware bottlenecks | `model.equations.active_set`, `optimize.shares` | `test_rules_physical.py` | Diagnostics / Allocation Lab |
| C3 | Overbuild penalty | `rules.physical.overbuild_penalty` | `test_rules_physical.py` | Diagnostics |
| P3-P5 | Switch-time and preemption | `rules.physical` | `test_rules_physical.py` | Diagnostics |
| P6 | BPI safety barrier | `rules.registry._bpi_barrier`, `rules.physical.bpi_barrier_satisfied` | `test_rules_core.py`, `test_rules_physical.py` | Rule Engine / Diagnostics |
| P7 | Smooth-min approximation bound | `model.equations.smooth_min_error_bound` | `test_rules_physical.py` | Diagnostics |
| P8 | Heavy-traffic gain | `rules.physical.heavy_traffic_gain`, `rules.registry._heavy_traffic` | `test_rules_core.py`, `test_rules_physical.py` | Rule Engine / Diagnostics |
| I1 | Institutional fixed point | `rules.institutional.institutional_fixed_point` | `test_rules_institutional.py` | Rule Engine |
| I2 | Gate-aware ROI | `rules.institutional.gate_slope_over_cost` | `test_rules_institutional.py` | Rule Engine |
| I3-I5 | Risk and chance constraints | `rules.institutional` | `test_rules_institutional.py` | Monte Carlo / Risk |
| A1/C5 | Robust concentration/diversification | `optimize.robust` | `test_allocation.py` | Allocation Lab |
| A2 | KKT allocation with floors | `optimize.kkt` | `test_allocation.py` | Allocation Lab |
| A7 | CVaR tail risk | `optimize.cvar` | `test_allocation.py` | Monte Carlo / Risk |
| Variable definitions | State and indicator glossary | `model.catalog` | `test_gui_smoke.py` | Overview / Scenario Builder |
| User interpretation layer | Plain-language reading of current trace | `sim.interpretation`, `gui.components.interpretation_panel` | `test_interpretation.py` | Overview / Dashboard |
