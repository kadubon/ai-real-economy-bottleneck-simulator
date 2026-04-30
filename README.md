# AI Real-Economy Bottleneck Simulator
This repository turns the Takahashi (2026) AI bottleneck-growth papers into a browser simulator.
It shows when AI capability becomes realized output, and when electricity, grid, materials, cooling, permitting, trust, regulation, or operations block that translation.

[![CI](https://github.com/kadubon/ai-real-economy-bottleneck-simulator/actions/workflows/ci.yml/badge.svg)](https://github.com/kadubon/ai-real-economy-bottleneck-simulator/actions/workflows/ci.yml)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-real-economy-bottleneck-simulator-cnqmwyr7ke6rhyekvbfxzq.streamlit.app/)

An Apache-2.0, browser-based research simulator for the question:

> When AI capability grows quickly, what physical and institutional bottlenecks determine how much of that capability becomes realized real-economy growth?

The app is designed for non-engineers, economists, policy researchers, and software engineers. Non-engineers can use the Streamlit web GUI. Researchers and engineers can run reproducible scenario JSON files, inspect the equations, and modify the model modules.

## Search Keywords

AI growth, real-economy growth, bottleneck simulator, physical bottlenecks, institutional bottlenecks, effective compute, deployment constraints, semi-endogenous growth, Streamlit, Plotly, Python, uv, Apache-2.0.

## What You Can Learn

The simulator is built to answer scenario questions, not to forecast the world.

- Does realized output `YR` keep pace with potential progress `YI`?
- Is the translation gap mainly physical, institutional, or both?
- Which branch is binding: compute, electricity, grid/interconnection, materials, cooling/water, or permitting/construction?
- Are compute investments becoming an overbuild because complementary branches lag?
- How do alternative allocation rules change final output, reflection loss, bottleneck pressure, and downside risk inside the model?

## Browser GUI

For non-engineers, use the hosted Streamlit Community Cloud app:

```text
https://ai-real-economy-bottleneck-simulator-cnqmwyr7ke6rhyekvbfxzq.streamlit.app/
```

The hosted app runs from the public GitHub repository through Streamlit Community Cloud.

The GUI includes:

- Overview with a plain-language model diagram
- Scenario Builder with tooltips and variable explanations
- Simulation Dashboard for `YI`, `YR`, gaps, reflection factors, `Ceff`, `BPI`, and speed ratio
- Bottleneck Diagnostics for active branches, ties, switch-time forecasts, and overbuild warnings
- Policy / Allocation Lab for alternative share rules
- Rule Engine for theorem-level diagnostics
- Monte Carlo / Risk stress tests
- Export / Report downloads

## Local Installation

This project uses `uv`.

```powershell
uv sync --extra dev
uv run realgrowthsim gui
```

Direct Streamlit launch:

```powershell
uv run streamlit run streamlit_app.py
```

CLI examples:

```powershell
uv run realgrowthsim run --preset baseline --out outputs/baseline.csv
uv run realgrowthsim validate --preset baseline
```

## Streamlit Cloud Deployment

Use a public GitHub repository and set:

- Repository: `ai-real-economy-bottleneck-simulator`
- Branch: `main`
- Main file path: `streamlit_app.py`
- Python: `3.12`

The repository uses `pyproject.toml` and `uv.lock` for dependency reproducibility. Avoid adding a competing `requirements.txt` unless deployment testing proves it is necessary.

GitHub Pages is not used for the Python GUI because GitHub Pages is static HTML/CSS/JS hosting. It can be used only for static documentation or a landing page.

## Theory Implemented

The implementation follows two papers:

- K. Takahashi, "From AI Capability Growth to Real-Economy Growth: A Semi-Endogenous Model of Physical and Institutional Bottlenecks," 2026. DOI: `10.5281/zenodo.18677068`
- K. Takahashi, "Operational Deductive Rules for Real-Economy Acceleration in the AI Era: A Machine-Readable Supplement on Physical and Institutional Translation Bottlenecks," 2026. DOI: `10.5281/zenodo.18688712`

Core model:

```text
YI = A^alpha * H^beta * C^gamma
Ceff = min(C, kappa_E E, kappa_G G, kappa_M M, kappa_W W, kappa_L L)
OmegaP = ((Ceff + eps_C) / (C + eps_C))^theta_P
OmegaI = S^nuS * U^nuU * P^nuP * G_R(R)
YR = OmegaP * OmegaI * YI
g = log(YI) - log(YR) = -log(OmegaP) - log(OmegaI)
BPI = 1 - (Ceff + eps_C) / (C + eps_C)
v_h = Delta_h log(YR) / Delta_h log(YI)
```

The simulator implements hybrid ODE-jump dynamics with ordered event handling:

```text
regime update -> physical jumps -> institutional jumps
```

If several events share the same timestamp, they are grouped and applied in that deterministic order.

## Variable Glossary

State variables:

- `A`: algorithmic knowledge, the strength of AI methods.
- `H`: AI-augmented research effort.
- `C`: installed compute.
- `E`: electricity capacity.
- `G`: grid/interconnection throughput.
- `M`: materials throughput.
- `W`: cooling/water throughput.
- `L`: permitting/construction throughput.
- `S`: social acceptance.
- `R`: regulatory readiness.
- `U`: institutional readiness.
- `P`: operational maturity.

Derived indicators:

- `YI`: potential information-layer progress.
- `YR`: realized output after physical and institutional reflection.
- `OmegaP`: physical reflection factor, in `(0, 1]`.
- `OmegaI`: institutional reflection factor, in `(0, 1]`.
- `Ceff`: effective compute after the tightest physical branch.
- `BPI`: bottleneck pressure index, in `[0, 1)`.
- `g`, `gP`, `gI`: total, physical, and institutional translation gaps.
- `v_h`: window speed ratio. Missing values mean the denominator was too small.

## Repository Architecture

```text
src/realgrowthsim/
  model/       state, parameters, equations, dynamics, events, regimes, variable catalog
  sim/         hybrid simulation engine, integrators, scenarios, interpretation, stochastic stress tests
  rules/       operational theorem/rule registry and diagnostic formulas
  optimize/    KKT, robust allocation, CVaR, and share policies
  io/          JSON, CSV, diagnostics, and Markdown report exports
  gui/         Streamlit GUI and reusable UI components
  data/        scenario presets
tests/         algebraic, simulation, event, rule, allocation, and GUI smoke tests
docs/          theory mapping, model reference, developer guide, validation, limitations, audit notes
SECURITY.md    security policy and public-deployment data-handling notes
```

The dynamics are intentionally split from the simulation loop:

- `model.equations`: pure algebraic equations and indicators.
- `model.dynamics`: ODE right-hand side and institutional drivers.
- `sim.engine`: hybrid time stepping, predictable feedback, event grouping, trace storage.
- `sim.interpretation`: plain-language reading shared by the GUI and Markdown reports.
- `gui.components`: reusable Streamlit panels, glossary, metrics, and chart explanations.

This separation makes it easier to modify the theory without rewriting the GUI or CLI.

## Scenario Presets

- Baseline endogenous co-growth
- Information-fast / reflection-slow
- Physical coordination push
- Institutional acceleration
- Resource and trust shock
- Conservative finite-resource stress
- Compute-only overbuild stress
- Active bottleneck preemption
- Institutional risk shock
- Tail-risk-aware allocation

All presets are synthetic, normalized, or paper-inspired examples. They are not forecasts.

## Testing and Validation

```powershell
uv run ruff check .
uv run pytest
uv run realgrowthsim validate --preset baseline
```

The suite checks algebraic identities, positivity and boundedness, event attribution, speed-ratio missingness, active bottleneck detection, smooth-min error bounds, institutional chance checks, KKT allocation, CVaR, scenario loading, and Streamlit import safety.

## Security and Privacy

- No telemetry from this app.
- No external API calls by default.
- No secrets.
- No hidden data upload.
- Scenario JSON imports are processed in the current browser session only.
- Do not enter personal, confidential, financial, health, biometric, or sensitive data.

Community Cloud limitations:

- Hosted service availability is controlled by Streamlit/Snowflake.
- Public apps are viewable by others.
- Community Cloud currently hosts apps in the United States.
- Streamlit/Snowflake may change service terms or limitations.

## Disclaimer

This is a research simulation tool. It is not financial, investment, energy-policy, or regulatory advice. Outputs are scenario-sensitive and should not be interpreted as real-world predictions.

## Documentation

- [Theory mapping](docs/theory_mapping.md)
- [Theory audit](docs/theory_audit.md)
- [Model reference](docs/model_reference.md)
- [Developer guide](docs/developer_guide.md)
- [GUI guide](docs/gui_guide.md)
- [Security audit checklist](docs/security_audit.md)
- [Validation](docs/validation.md)
- [Limitations](docs/limitations.md)

## License and Citation

Apache License 2.0. See [LICENSE](LICENSE).

Citation metadata is in [CITATION.cff](CITATION.cff).
