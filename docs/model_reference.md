# Model Reference

The simulator uses a 12-state hybrid ODE-jump model:

`A, H, C, E, G, M, W, L, S, R, U, P`

`A,H,C` are information-layer states. `E,G,L` are stock physical capacities. `M,W` are consumable-flow states. `S,R,U,P` are bounded institutional states. The user-facing variable glossary is implemented in `realgrowthsim.model.catalog`.

Most non-institutional state values are normalized indexes. In a normalized preset, `1.0` means the preset baseline, `0.5` means roughly half that index, and `2.0` means roughly twice that index. Institutional states are bounded scores: `1.0` is the model maximum and values nearer the institutional floor represent weak translation conditions.

## Plain-Language State Glossary

| Symbol | Meaning |
|---|---|
| `A` | Algorithmic knowledge: the strength of AI methods. |
| `H` | AI-augmented research effort: effective research capacity after AI assistance. |
| `C` | Installed compute: compute that has been built or purchased. |
| `E` | Electricity capacity: power available to run compute. |
| `G` | Grid/interconnection throughput: ability to connect and deliver power. |
| `M` | Materials throughput: flow of chips, equipment, and other critical inputs. |
| `W` | Cooling/water throughput: cooling and water support for operation. |
| `L` | Permitting/construction throughput: ability to approve and build projects. |
| `S` | Social acceptance: public and stakeholder acceptance. |
| `R` | Regulatory readiness: readiness of rules, approvals, and gates. |
| `U` | Institutional readiness: organizational adoption and coordination capacity. |
| `P` | Operational maturity: reliability of operating the deployed system. |

## Information Layer

Potential progress:

```text
YI = A^alpha * H^beta * C^gamma
```

Algorithmic knowledge, research effort, and installed compute are integrated between events using Euler, RK4, or `solve_ivp`. The ODE right-hand side is isolated in `realgrowthsim.model.dynamics` so economists can alter theory equations without touching the GUI.

## Physical Channel

Scaled branches:

```text
C, kappa_E E, kappa_G G, kappa_M M, kappa_W W, kappa_L L
```

Effective compute is the exact minimum by default. A smooth-min approximation is available for differentiable diagnostics. The reported smooth-min error bound is model-consistent with the simulator's `eps_C` numerator.

```text
OmegaP = ((Ceff + eps_C) / (C + eps_C))^theta_P
BPI = 1 - (Ceff + eps_C) / (C + eps_C)
```

## Institutional Channel

Institutional states follow bounded improvement/erosion dynamics. The regulatory gate is a smooth threshold:

```text
G_R(R) = g0 + (1 - g0) * sigmoid(kappa_R * (R - R_star))
OmegaI = S^nuS * U^nuU * P^nuP * G_R(R)
```

## Realized Output

```text
YR = OmegaP * OmegaI * YI
g = log(YI) - log(YR)
gP = -log(OmegaP)
gI = -log(OmegaI)
```

The simulator enforces positivity and institutional bounds before every stored step.

Coincident events are grouped by timestamp and applied in the paper order:

```text
regime update -> physical jumps -> institutional jumps
```
