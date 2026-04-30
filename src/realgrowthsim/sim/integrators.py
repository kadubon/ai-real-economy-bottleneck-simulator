from __future__ import annotations

from collections.abc import Callable

import numpy as np
from scipy.integrate import solve_ivp

Derivative = Callable[[float, np.ndarray], np.ndarray]


def euler_step(f: Derivative, t: float, y: np.ndarray, dt: float) -> np.ndarray:
    return y + dt * f(t, y)


def rk4_step(f: Derivative, t: float, y: np.ndarray, dt: float) -> np.ndarray:
    k1 = f(t, y)
    k2 = f(t + 0.5 * dt, y + 0.5 * dt * k1)
    k3 = f(t + 0.5 * dt, y + 0.5 * dt * k2)
    k4 = f(t + dt, y + dt * k3)
    return y + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def solve_ivp_step(f: Derivative, t: float, y: np.ndarray, dt: float) -> np.ndarray:
    result = solve_ivp(f, (t, t + dt), y, method="RK45", rtol=1e-7, atol=1e-9)
    if not result.success:
        raise RuntimeError(result.message)
    return result.y[:, -1]
