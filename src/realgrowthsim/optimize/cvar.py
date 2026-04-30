from __future__ import annotations

import numpy as np
from scipy.optimize import minimize


def sample_cvar(losses: np.ndarray | list[float], alpha: float = 0.9) -> float:
    arr = np.sort(np.asarray(losses, dtype=float))
    if arr.size == 0:
        raise ValueError("loss sample is empty")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    cutoff = int(np.ceil(alpha * arr.size))
    tail = arr[min(cutoff, arr.size - 1) :]
    return float(np.mean(tail))


def cvar_objective(losses: np.ndarray | list[float], eta: float, alpha: float = 0.9) -> float:
    arr = np.asarray(losses, dtype=float)
    return float(eta + np.mean(np.maximum(arr - eta, 0.0)) / (1.0 - alpha))


def cvar_allocation(
    loss_matrix: np.ndarray,
    floors: np.ndarray,
    budget: float,
    alpha: float = 0.9,
) -> np.ndarray:
    """Minimize sample CVaR of linear portfolio losses loss_matrix @ shares."""

    loss_matrix = np.asarray(loss_matrix, dtype=float)
    floors = np.asarray(floors, dtype=float)
    n = loss_matrix.shape[1]
    if floors.shape != (n,):
        raise ValueError("floors shape does not match loss matrix")
    if budget < floors.sum() - 1e-12:
        raise ValueError("budget below floors")
    x0 = floors + (budget - floors.sum()) / n

    def objective(shares: np.ndarray) -> float:
        return sample_cvar(loss_matrix @ shares, alpha)

    constraints = [{"type": "eq", "fun": lambda x: np.sum(x) - budget}]
    bounds = [(float(f), float(budget)) for f in floors]
    result = minimize(objective, x0, method="SLSQP", bounds=bounds, constraints=constraints)
    if not result.success:
        return x0
    return np.asarray(result.x, dtype=float)
