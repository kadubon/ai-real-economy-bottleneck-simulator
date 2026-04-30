from __future__ import annotations


def robust_concentration_condition(impacts: dict[str, float], rho: float) -> tuple[bool, str | None, float]:
    """Return whether the top estimated lever remains top under multiplicative uncertainty."""

    if not impacts:
        return False, None, float("nan")
    ordered = sorted(impacts.items(), key=lambda item: item[1], reverse=True)
    top, top_value = ordered[0]
    if len(ordered) == 1:
        return True, top, float("inf")
    runner_up = max(value for _, value in ordered[1:])
    margin = (1.0 - rho) * top_value - (1.0 + rho) * runner_up
    return margin >= 0.0, top, margin


def diversify_top_levers(impacts: dict[str, float], floors: dict[str, float], budget: float, top_n: int = 3) -> dict[str, float]:
    labels = list(impacts)
    floor = {label: max(float(floors.get(label, 0.0)), 0.0) for label in labels}
    remaining = max(float(budget) - sum(floor.values()), 0.0)
    ordered = [label for label, _ in sorted(impacts.items(), key=lambda item: item[1], reverse=True)]
    chosen = ordered[: max(1, min(top_n, len(ordered)))]
    shares = floor.copy()
    for label in chosen:
        shares[label] += remaining / len(chosen)
    return shares
