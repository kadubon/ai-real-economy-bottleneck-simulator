from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CatalogItem:
    symbol: str
    name: str
    plain: str
    technical: str
    units: str = "normalized index"
    paper_ref: str = ""


STATE_CATALOG: dict[str, CatalogItem] = {
    "A": CatalogItem(
        "A",
        "Algorithmic knowledge",
        "How strong the underlying AI methods are.",
        "Algorithmic knowledge stock entering potential output and idea production.",
        paper_ref="Main Eq. 6-7",
    ),
    "H": CatalogItem(
        "H",
        "AI-augmented research effort",
        "How much effective research capacity exists after AI assistance.",
        "Research-effort state with AI and compute augmentation.",
        paper_ref="Main Eq. 8",
    ),
    "C": CatalogItem(
        "C",
        "Installed compute",
        "How much compute has been built or purchased.",
        "Installed accelerator-equivalent compute stock.",
        paper_ref="Main Eq. 10",
    ),
    "E": CatalogItem(
        "E",
        "Electricity capacity",
        "Power capacity available to run compute.",
        "Deliverable electricity capacity branch.",
        paper_ref="Main Eq. 16,19",
    ),
    "G": CatalogItem(
        "G",
        "Grid/interconnection throughput",
        "Ability to connect and deliver power through networks.",
        "Stock capacity for interconnection and grid transfer capability.",
        paper_ref="Main Eq. 16,19; Remark 4.2",
    ),
    "M": CatalogItem(
        "M",
        "Materials throughput",
        "Flow of chips, equipment, and other critical inputs.",
        "Consumable-flow capacity with stress loss from effective compute.",
        paper_ref="Main Eq. 16,20",
    ),
    "W": CatalogItem(
        "W",
        "Cooling/water throughput",
        "Ability to cool and support data-center operation.",
        "Consumable-flow cooling or water branch.",
        paper_ref="Main Eq. 16,20",
    ),
    "L": CatalogItem(
        "L",
        "Permitting/construction throughput",
        "How fast projects can be approved and built.",
        "Stock capacity for permits, construction, and deployment throughput.",
        paper_ref="Main Eq. 16,19",
    ),
    "S": CatalogItem(
        "S",
        "Social acceptance",
        "Public and stakeholder acceptance of deployment.",
        "Bounded institutional state in OmegaI.",
        paper_ref="Main Eq. 21,23",
    ),
    "R": CatalogItem(
        "R",
        "Regulatory readiness",
        "Whether rules and approvals are ready enough for deployment.",
        "Institutional state entering the smooth regulatory gate.",
        paper_ref="Main Eq. 21-23",
    ),
    "U": CatalogItem(
        "U",
        "Institutional readiness",
        "Organizational ability to adopt and coordinate the technology.",
        "Bounded institutional readiness state in OmegaI.",
        paper_ref="Main Eq. 21,23",
    ),
    "P": CatalogItem(
        "P",
        "Operational maturity",
        "How reliably organizations can operate the deployed system.",
        "Bounded operational maturity state in OmegaI.",
        paper_ref="Main Eq. 21,23",
    ),
}


INDICATOR_CATALOG: dict[str, CatalogItem] = {
    "YI": CatalogItem(
        "YI",
        "Potential progress",
        "What AI capability could produce before real-world bottlenecks.",
        "Information-layer output A^alpha H^beta C^gamma.",
        paper_ref="Main Eq. 6",
    ),
    "YR": CatalogItem(
        "YR",
        "Realized output",
        "What remains after physical and institutional translation losses.",
        "OmegaP * OmegaI * YI.",
        paper_ref="Main Eq. 1",
    ),
    "OmegaP": CatalogItem(
        "OmegaP",
        "Physical reflection factor",
        "How much installed compute can actually be deployed physically.",
        "((Ceff + eps_C) / (C + eps_C))^theta_P.",
        units="0 to 1",
        paper_ref="Main Eq. 17",
    ),
    "OmegaI": CatalogItem(
        "OmegaI",
        "Institutional reflection factor",
        "How much deployment survives trust, regulation, readiness, and operations.",
        "S^nuS * U^nuU * P^nuP * G_R(R).",
        units="0 to 1",
        paper_ref="Main Eq. 23",
    ),
    "Ceff": CatalogItem(
        "Ceff",
        "Effective compute",
        "The usable compute after the tightest physical branch is applied.",
        "min(C, kE E, kG G, kM M, kW W, kL L), unless smooth-min is enabled.",
        paper_ref="Main Eq. 16",
    ),
    "BPI": CatalogItem(
        "BPI",
        "Bottleneck Pressure Index",
        "A 0-to-1 measure of how much installed compute is blocked physically.",
        "1 - (Ceff + eps_C) / (C + eps_C).",
        units="0 to <1",
        paper_ref="Main Eq. 18",
    ),
    "gap": CatalogItem(
        "g",
        "Translation gap",
        "How far potential progress is from realized progress.",
        "log(YI) - log(YR) = -log(OmegaP) - log(OmegaI).",
        paper_ref="Main Eq. 2-3",
    ),
    "gapP": CatalogItem(
        "gP",
        "Physical gap",
        "The part of the gap caused by physical deployment limits.",
        "-log(OmegaP).",
        paper_ref="Main Eq. 3",
    ),
    "gapI": CatalogItem(
        "gI",
        "Institutional gap",
        "The part of the gap caused by institutional limits.",
        "-log(OmegaI).",
        paper_ref="Main Eq. 3",
    ),
    "v_h": CatalogItem(
        "v_h",
        "Window speed ratio",
        "Whether realized growth is keeping up with capability growth over a time window.",
        "Delta_h log(YR) / Delta_h log(YI), NaN if denominator is too small.",
        paper_ref="Main Eq. 5; Supplement Eq. 3",
    ),
}


PARAMETER_CATALOG: dict[str, CatalogItem] = {
    "horizon": CatalogItem(
        "horizon",
        "Simulation horizon",
        "How far into simulated time the scenario runs.",
        "End time for the numerical simulation.",
        units="time units",
        paper_ref="Simulation algorithm",
    ),
    "dt": CatalogItem(
        "dt",
        "Step size",
        "How fine the time grid is.",
        "Numerical integration step used by Euler/RK4 grid modes.",
        units="time units",
        paper_ref="Simulation algorithm",
    ),
    "seed": CatalogItem(
        "seed",
        "Random seed",
        "A number that makes stochastic stress tests reproducible.",
        "Seed for pseudo-random incident generation.",
        units="integer",
        paper_ref="Stochastic incident simulations",
    ),
    "chi_A": CatalogItem(
        "chi_A",
        "Algorithmic progress intensity",
        "How quickly algorithmic knowledge grows before depreciation.",
        "Scale factor in dA/dt.",
        paper_ref="Main Eq. 7",
    ),
    "chi_H": CatalogItem(
        "chi_H",
        "Research effort growth intensity",
        "How quickly AI-augmented research effort grows before depreciation.",
        "Scale factor in dH/dt.",
        paper_ref="Main Eq. 8",
    ),
    "theta_P": CatalogItem(
        "theta_P",
        "Physical reflection elasticity",
        "How strongly physical shortfalls reduce realized output.",
        "Exponent in OmegaP.",
        paper_ref="Main Eq. 17",
    ),
    "risk": CatalogItem(
        "risk",
        "Institutional risk pressure",
        "Stress that erodes social, regulatory, organizational, and operational states.",
        "Risk_t driver in institutional Gamma terms.",
        paper_ref="Main Eq. 21",
    ),
    "s_bar": CatalogItem(
        "s_bar",
        "Maximum deployable investment share",
        "The largest total share of output that can be redirected into deployment levers.",
        "Upper bound on the sum of allocation shares.",
        units="0 to 1",
        paper_ref="Main Eq. 15",
    ),
}


NUMERIC_HINTS: dict[str, str] = {
    "A": "Index scale: 1.0 is the preset baseline; 2.0 means roughly twice the algorithmic stock.",
    "H": "Index scale: 1.0 is baseline research capacity; 0.5 is about half, 2.0 about double.",
    "C": "Index scale: 1.0 is baseline installed compute; higher values can be wasted if Ceff does not rise.",
    "E": "Physical capacity index: compare kappa_E*E with C. If kappa_E*E < C, electricity constrains compute.",
    "G": "Physical capacity index: compare kappa_G*G with C. If it is smallest, grid/interconnection is binding.",
    "M": "Throughput index: low M means supply/input flow cannot support installed compute.",
    "W": "Throughput index: low W means cooling or water support is limiting deployment.",
    "L": "Throughput index: low L means permits/construction cannot keep up with installed compute.",
    "S": "Bounded 0-1 state: 0.8 means fairly strong acceptance; 1.0 is the model maximum.",
    "R": "Bounded 0-1 state: values near R_star open the regulatory gate; below it, YR is discounted.",
    "U": "Bounded 0-1 state: 0.7 is weaker adoption readiness than 0.9.",
    "P": "Bounded 0-1 state: 0.9 means mature operation; lower values reduce OmegaI.",
    "YI": "Index output before bottlenecks. If YI=2 and YR=1, half the potential is not realized.",
    "YR": "Index output after bottlenecks. Compare it with YI to see translation loss.",
    "OmegaP": "Multiplier: 0.8 means physical bottlenecks pass through about 80% of potential after other factors.",
    "OmegaI": "Multiplier: 0.7 means institutions pass through about 70% of physically feasible potential.",
    "Ceff": "Usable compute index. If C=2 and Ceff=1.2, only 60% of installed compute is physically usable.",
    "BPI": "Pressure gauge: 0.3 means about 30% physical blockage of installed compute.",
    "gap": "Log gap: 0 means no translation loss; larger values mean a wider YI-to-YR wedge.",
    "gapP": "Physical log loss. A larger value points to physical relief rather than capability expansion.",
    "gapI": "Institutional log loss. A larger value points to trust, regulation, adoption, or operations.",
    "v_h": "Speed ratio: 1 means YR grows as fast as YI; 0.7 means realized growth captures about 70% of capability growth over the window.",
    "horizon": "Example: 20 runs from t=0 to t=20 in model time, not calendar years unless calibrated.",
    "dt": "Smaller dt is more detailed but slower. Example: 0.1 stores about 10 points per model time unit.",
    "seed": "Same seed gives the same stochastic incidents; change it to sample another stress path.",
    "chi_A": "Higher values make A grow faster. Example: 0.10 is faster algorithmic progress than 0.05.",
    "chi_H": "Higher values make effective research effort grow faster.",
    "theta_P": "Higher values make the same physical shortfall more damaging to YR.",
    "risk": "Higher values accelerate institutional erosion in the model.",
    "s_bar": "Example: 0.85 means at most 85% of the bounded investment flow can be allocated across levers.",
}


def catalog_table(items: dict[str, CatalogItem]) -> list[dict[str, str]]:
    return [
        {
            "Symbol": item.symbol,
            "Plain meaning": item.plain,
            "Technical definition": item.technical,
            "How to read numbers": NUMERIC_HINTS.get(item.symbol, ""),
            "Units": item.units,
            "Paper reference": item.paper_ref,
        }
        for item in items.values()
    ]


def help_text(symbol: str) -> str:
    item = STATE_CATALOG.get(symbol) or INDICATOR_CATALOG.get(symbol) or PARAMETER_CATALOG.get(symbol)
    if item is None:
        return symbol
    hint = NUMERIC_HINTS.get(symbol, "")
    return f"{item.name}: {item.plain} Technical: {item.technical} {hint}".strip()
