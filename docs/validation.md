# Validation

The test suite checks:

- `YR = OmegaP * OmegaI * YI`
- `g = gP + gI`
- `BPI in [0,1)` under valid positive inputs
- `OmegaP` and `OmegaI` in `(0,1]`
- speed ratio returns `NaN` when the denominator is too small
- event attribution identity
- coincident event ordering by timestamp group
- institutional states remain within bounds
- physical states remain nonnegative
- active bottleneck and tie detection
- overbuild penalty sign
- deterministic/noisy switch-time formulas
- Gaussian and Cantelli institutional floor checks
- robust concentration/diversification
- KKT allocation floors and budget
- CVaR sample tail loss
- preset load and simulation
- Streamlit entrypoint import
- variable catalog availability for GUI tooltips

Run:

```powershell
uv run pytest
uv run realgrowthsim validate --preset baseline
```
