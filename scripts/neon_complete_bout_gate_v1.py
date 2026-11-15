#!/usr/bin/env python3
"""Fail-closed 400m² NEON plant bout label gate for later, authorized use.

This module is a *pure function*. It does not access NEON plot data.
Validating input structure cannot establish true absence or data-source independence.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import re

SUBPLOTS_1 = frozenset({
    "31_1_1", "32_1_2", "32_1_4", "40_1_1", "40_1_3", "41_1_4",
})
SUBPLOTS_10 = frozenset(x.replace("_1_", "_10_") for x in SUBPLOTS_1)
SUBPLOTS_100 = frozenset({"31_100", "32_100", "40_100", "41_100"})
STATES = {"detected", "protocol_conditional_non_detection", "unresolved"}


def _unresolved(reason: str) -> dict[str, str]:
    return {"state": "unresolved", "reason": reason}


def evaluate_400m2_bout(
    one_m2: Sequence[Mapping[str, object]],
    larger: Sequence[Mapping[str, object]],
    *,
    focal_scientific_name: str,
) -> dict[str, str]:
    """Return a **protocol-conditional** detection, non-detection, or unresolved.

    Requirements are conservative for RELEASE-2026, >=2020 basePlot bouts.
    A full survey needs 6 1m², 6 10m², and 4 100m² subplots; all records
    must come from the *same* eventID/plot/site/bout and meet quality gates.
    Observations in 10m²/100m² are incremental to nested 1m² observations,
    so the target detection is the union over both tables.
    """
    if not isinstance(focal_scientific_name, str) or not re.fullmatch(
        r"[A-Z][a-z-]+ [a-z-]+", focal_scientific_name
    ):
        raise ValueError("focal taxon must be a strict binomial")
    r1 = list(one_m2)
    rl = list(larger)
    if not r1 or not rl:
        return _unresolved("required_nested_table_missing")
    rows = r1 + rl
    required = (
        "siteID", "plotID", "eventID", "boutNumber", "endDate",
        "subplotID", "samplingImpractical", "biophysicalCriteria",
        "targetTaxaPresent", "scientificName", "taxonRank",
        "identificationQualifier", "morphospeciesID"
    )
    if any(set(required) - set(row) for row in rows):
        return _unresolved("required_quality_or_taxonomy_column_missing")
    for k in ("siteID", "plotID", "eventID", "boutNumber"):
        values = {str(r.get(k) or "").strip() for r in rows}
        if len(values) != 1 or not next(iter(values)):
            return _unresolved("mixed_or_missing_plot_event_identity")
    if not all(str(r["endDate"])[:4] in {"2020","2021","2022","2023","2024"} for r in rows):
        return _unresolved("outside_primary_2020_2024_period")
    s1 = {str(r["subplotID"]).strip() for r in r1}
    sl = {str(r["subplotID"]).strip() for r in rl}
    if s1 != SUBPLOTS_1 or sl != SUBPLOTS_10 | SUBPLOTS_100:
        return _unresolved("not_all_16_expected_baseplot_subplots_documented")
    if any(str(r["samplingImpractical"]).strip() != "OK" for r in rows):
        return _unresolved("sampling_impractical_or_unknown")
    if any(str(r["biophysicalCriteria"]).strip() != "OK - no known exceptions" for r in rows):
        return _unresolved("taxonomic_visibility_conditions_suboptimal_or_unknown")

    # All subplot rows have a protocol targetTaxaPresent value, including
    # those with no plant detections. Do not take NA codes as negative.
    if any(str(r["targetTaxaPresent"]).strip() not in {"Y", "N"} for r in rows):
        return _unresolved("unknown_subsubplot_species_observability")
    target_genus = focal_scientific_name.split()[0]
    definitely_detected = False
    ambiguous = False
    for r in rows:
        present = str(r["targetTaxaPresent"]).strip() == "Y"
        if not present:
            # A protocol-level no-taxa sentinel must never carry an identified
            # species or morphospecies record. Contradictory survey rows cannot
            # be treated as a trustworthy non-detection.
            if str(r["scientificName"] or "").strip() or str(r["morphospeciesID"] or "").strip():
                return _unresolved("contradictory_targetTaxaPresent_N_with_taxon_metadata")
            continue
        name = str(r["scientificName"] or "").strip()
        rank = str(r["taxonRank"] or "").strip().upper()
        qualifier = str(r["identificationQualifier"] or "").strip()
        morph = str(r["morphospeciesID"] or "").strip()
        genus = name.split()[0] if name else ""
        if not name or morph:
            ambiguous = True
            continue
        if rank not in {"SPECIES", "SUBSPECIES", "VARIETY"}:
            # Genus/family/higher-rank or questionable plant identifications
            # cannot license a negative focal-species inference.
            ambiguous = True
            continue
        if genus == target_genus:
            if rank != "SPECIES" or qualifier:
                ambiguous = True
                continue
            if name == focal_scientific_name:
                definitely_detected = True
        # A reliably identified species of another genus is not evidence
        # that the focal taxon occurred in this completed plot.
    if definitely_detected:
        return {"state": "detected", "reason": "exact_focal_taxon_record_on_complete_bout"}
    if ambiguous:
        return _unresolved("potentially_unidentified_focal_taxon_in_completed_bout")
    return {"state": "protocol_conditional_non_detection",
            "reason": "complete_400m2_bout_without_identified_focal_taxon"}


__all__ = ("evaluate_400m2_bout", "SUBPLOTS_1", "SUBPLOTS_10", "SUBPLOTS_100")
