# Developer Guide

This guide is for engineers and economists who want to change the theory rather than only run scenarios.

## Where To Change The Model

The package separates algebra, dynamics, simulation, rules, and GUI wiring.

| Goal | Primary files | Notes |
|---|---|---|
| Change an algebraic equation | `src/realgrowthsim/model/equations.py` | Keep functions pure and add identity tests. |
| Change an ODE law | `src/realgrowthsim/model/dynamics.py` | `state_derivative` is the single right-hand-side entry point. |
| Add a state variable | `model/state.py`, `model/catalog.py`, `model/equations.py`, `model/dynamics.py` | Also update tests, scenario JSON, docs, and GUI tables. |
| Add a parameter | `model/params.py`, `model/catalog.py` | Prefer Pydantic bounds and a plain-language tooltip. |
| Add an event type | `model/events.py`, `sim/engine.py` | Preserve ordered handling: regime, physical, institutional. |
| Add a rule | `rules/registry.py` plus a focused `rules/*.py` helper | Include assumptions, formula, lever class, and test coverage. |
| Add an allocation policy | `optimize/`, `optimize/shares.py` | Check floors, nonnegativity, and `sum(shares) <= s_bar`. |
| Add a scenario preset | `sim/scenarios.py` and generated JSON under `src/realgrowthsim/data/presets/` | Presets should be synthetic or clearly marked as illustrative. |
| Change result interpretation | `sim/interpretation.py` | Keep GUI and reports consistent by changing this shared layer first. |
| Change GUI wording | `src/realgrowthsim/gui/app.py`, `gui/components.py`, `model/catalog.py` | Keep explanations visible without requiring users to read code. |

## Invariants To Preserve

These identities are central to the papers and should keep passing after theory changes:

```text
YR = OmegaP * OmegaI * YI
g = gP + gI
BPI = 1 - (Ceff + eps_C) / (C + eps_C)
v_h = Delta_h log(YR) / Delta_h log(YI), or NaN when the denominator is too small
```

Institutional states must remain in `[xi_floor, 1]`. Physical states must remain nonnegative. Information-layer states must remain positive and path-continuous at physical or institutional events.

## Suggested Workflow For Theory Changes

1. Edit the smallest theory module that owns the equation.
2. Add or update the variable/parameter explanation in `model/catalog.py`.
3. Add a focused unit test for the equation, inequality, or event identity.
4. Update `docs/theory_mapping.md` if a paper item now maps to a different implementation.
5. Run:

```powershell
uv run ruff check .
uv run pytest
uv run realgrowthsim validate --preset baseline
```

## GUI Design Rule

The GUI should not be a code front-end. It should answer four non-engineer questions directly:

- What is potential progress?
- What is realized output?
- What is blocking translation?
- Which model lever changes that result under the current assumptions?

Add visible explanations when a new metric would otherwise require reading the paper.

The `Current Reading` panel is intentionally generated from `sim.interpretation` rather than handwritten inside one Streamlit page. This keeps non-engineer guidance synchronized with exported reports and tests.
