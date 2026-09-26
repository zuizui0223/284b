"""Pre-discordance feasibility decisions for same-target reference calibration."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReferenceFeasibility:
    eligible_taxa: int
    minimum_required_taxa: int
    discordance_opening_authorized: bool
    state: str


def evaluate_reference_feasibility(eligible_taxa: int, *, minimum_required_taxa: int = 30) -> ReferenceFeasibility:
    """Freeze whether one procedure-by-M cell can proceed to paired discordance.

    This decision is intentionally based only on the number of taxa for which
    both independent source answers have sealed final fits and pass the frozen
    source-specific prediction-adequacy gate. It never consumes prediction
    surfaces or discordance values.
    """
    n = int(eligible_taxa)
    minimum = int(minimum_required_taxa)
    if n < 0:
        raise ValueError("eligible_taxa must be >= 0")
    if minimum < 1:
        raise ValueError("minimum_required_taxa must be >= 1")
    authorized = n >= minimum
    return ReferenceFeasibility(
        eligible_taxa=n,
        minimum_required_taxa=minimum,
        discordance_opening_authorized=authorized,
        state=(
            "reference_discordance_opening_authorized"
            if authorized
            else "reference_calibration_unresolved_pre_discordance"
        ),
    )


__all__ = ["ReferenceFeasibility", "evaluate_reference_feasibility"]
