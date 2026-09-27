#!/usr/bin/env python3
"""Structural-only join audit for Meetnetten amphibian monitoring exports.

The audit never reads individualCount and never computes an adult-downstream
association. It asks only whether publisher-defined identities and repeated
sampling are sufficient to justify opening a later ecological model.

Inputs are normalized extracts containing:
  chorus_events: eventID,eventDate,locationID
  chorus_taxa:   eventID,scientificName,occurrenceStatus
  down_events:  eventID,eventDate,locationID
  down_taxa:    eventID,scientificName,occurrenceStatus,lifeStage

Coordinate and locality fields are deliberately forbidden.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

EVENT_RE = re.compile(r"^INBO:MEETNET:EVENT:\d{6}$")
LOCATION_RE = re.compile(r"^INBO:MEETNET:LOCATION:\d{6}$")
SHARED_TARGETS = {"Hyla arborea", "Pelobates fuscus"}
STATUS = {"present", "absent"}
DOWN_STAGES = {"larva", "metamorph", "adult"}


def _read(path: Path, required: set[str]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = required - fields
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}")
        forbidden = {"decimalLatitude", "decimalLongitude", "locality"} & fields
        if forbidden:
            raise ValueError(
                f"{path}: spatial rescue columns forbidden in identity audit: {sorted(forbidden)}"
            )
        return [dict(row) for row in reader]


def _events(rows: list[dict[str, str]]) -> dict[str, tuple[str, date]]:
    out: dict[str, tuple[str, date]] = {}
    for line, row in enumerate(rows, 2):
        event_id = row["eventID"].strip()
        location_id = row["locationID"].strip()
        if not EVENT_RE.fullmatch(event_id):
            raise ValueError(f"line {line}: invalid eventID")
        if not LOCATION_RE.fullmatch(location_id):
            raise ValueError(f"line {line}: invalid locationID")
        if event_id in out:
            raise ValueError(f"duplicate eventID: {event_id}")
        try:
            event_date = date.fromisoformat(row["eventDate"].strip())
        except ValueError as exc:
            raise ValueError(f"line {line}: invalid ISO eventDate") from exc
        out[event_id] = (location_id, event_date)
    return out


def audit(
    chorus_events: Path,
    chorus_taxa: Path,
    down_events: Path,
    down_taxa: Path,
) -> dict:
    chorus_event_rows = _read(chorus_events, {"eventID", "eventDate", "locationID"})
    down_event_rows = _read(down_events, {"eventID", "eventDate", "locationID"})
    chorus_event_map = _events(chorus_event_rows)
    down_event_map = _events(down_event_rows)

    chorus_occ = _read(
        chorus_taxa, {"eventID", "scientificName", "occurrenceStatus"}
    )
    down_occ = _read(
        down_taxa,
        {"eventID", "scientificName", "occurrenceStatus", "lifeStage"},
    )

    chorus_keys: dict[tuple[str, str, int], set[str]] = defaultdict(set)
    down_keys: dict[tuple[str, str, int], set[str]] = defaultdict(set)
    stage_rows = Counter()

    for line, row in enumerate(chorus_occ, 2):
        event_id = row["eventID"].strip()
        if event_id not in chorus_event_map:
            raise ValueError(f"chorus taxa line {line}: unknown eventID")
        species = row["scientificName"].strip()
        status = row["occurrenceStatus"].strip()
        if status not in STATUS:
            raise ValueError(f"chorus taxa line {line}: invalid occurrenceStatus")
        if species in SHARED_TARGETS:
            location_id, event_date = chorus_event_map[event_id]
            chorus_keys[(location_id, species, event_date.year)].add(event_id)

    for line, row in enumerate(down_occ, 2):
        event_id = row["eventID"].strip()
        if event_id not in down_event_map:
            raise ValueError(f"downstream taxa line {line}: unknown eventID")
        species = row["scientificName"].strip()
        status = row["occurrenceStatus"].strip()
        stage = row["lifeStage"].strip()
        if status not in STATUS:
            raise ValueError(f"downstream taxa line {line}: invalid occurrenceStatus")
        if stage not in DOWN_STAGES:
            raise ValueError(
                f"downstream taxa line {line}: unexpected lifeStage {stage!r}"
            )
        if species in SHARED_TARGETS and stage in {"larva", "metamorph"}:
            location_id, event_date = down_event_map[event_id]
            down_keys[(location_id, species, event_date.year)].add(event_id)
            stage_rows[(species, stage)] += 1

    overlap = set(chorus_keys) & set(down_keys)
    overlap_by_species = Counter(key[1] for key in overlap)
    repeat_chorus = sum(len(chorus_keys[key]) >= 2 for key in overlap)

    ordered = 0
    for key in overlap:
        chorus_dates = [chorus_event_map[event_id][1] for event_id in chorus_keys[key]]
        downstream_dates = [down_event_map[event_id][1] for event_id in down_keys[key]]
        if any(c <= d for c in chorus_dates for d in downstream_dates):
            ordered += 1

    return {
        "publisher_identity_join_only": True,
        "join_key": ["locationID", "scientificName", "calendar_year"],
        "coordinate_join_used": False,
        "shared_location_species_years": len(overlap),
        "shared_by_species": dict(sorted(overlap_by_species.items())),
        "shared_units_with_ge2_chorus_events": repeat_chorus,
        "shared_units_with_at_least_one_chorus_event_not_after_downstream": ordered,
        "downstream_stage_rows": {
            f"{species}|{stage}": count
            for (species, stage), count in sorted(stage_rows.items())
        },
        "ecological_association_opened": False,
        "structural_candidate_pass": (
            len(overlap) >= 30
            and repeat_chorus >= 20
            and ordered >= 20
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chorus-events", type=Path, required=True)
    parser.add_argument("--chorus-taxa", type=Path, required=True)
    parser.add_argument("--down-events", type=Path, required=True)
    parser.add_argument("--down-taxa", type=Path, required=True)
    args = parser.parse_args()
    result = audit(
        args.chorus_events,
        args.chorus_taxa,
        args.down_events,
        args.down_taxa,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
