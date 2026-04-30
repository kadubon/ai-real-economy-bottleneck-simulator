from __future__ import annotations


def required_physical_relief(v_star: float, gI: float, gC_plus: float, gOmegaI: float, thetaP: float) -> float:
    return gC_plus + ((v_star - 1.0) * gI - gOmegaI) / thetaP


def required_institutional_drift(
    v_star: float,
    gI: float,
    gCeff_plus: float,
    gC_plus: float,
    thetaP: float,
) -> float:
    return v_star * gI - gI - thetaP * (gCeff_plus - gC_plus)


def non_contraction_threshold(gI: float, gCeff_plus: float, gC_plus: float, thetaP: float) -> float:
    return -gI - thetaP * (gCeff_plus - gC_plus)
