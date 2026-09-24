#!/usr/bin/env python3
"""Structural-only join audit for Meetnetten amphibian monitoring exports.

This script deliberately does NOT read individualCount or compute any adult-downstream
association. It tests whether publisher-defined identities provide enough exact shared
site-years to justify opening a later ecological model.

Inputs are normalized extracts containing only:
  chorus_events: eventID,eventDate,locationID
  chorus_taxa:   eventID,scientificName,occurrenceStatus
  down_events:  eventID,eventDate,locationID
  down_taxa:    eventID,scientificName,occurrenceStatus,lifeStage

No coordinate columns are accepted or used.
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
    with path.open(newline="", encoding="utf-8") as h:
        r = csv.DictReader(h)
        fields = set(r.fieldnames or [])
        miss = required - fields
        if miss:
            raise ValueError(f"{path}: missing columns {sorted(miss)}")
        forbidden = {"decimalLatitude", "decimalLongitude", "locality"} & fields
        if forbidden:
            raise ValueError(f"{path}: spatial rescue columns forbidden in identity audit: {sorted(forbidden)}")
        return [dict(x) for x in r]


def _events(rows: list[dict[str, str]]) -> dict[str, tuple[str, int]]:
    out = {}
    for i, r in enumerate(rows, 2):
        eid = r["eventID"].strip()
        lid = r["locationID"].strip()
        if not EVENT_RE.fullmatch(eid):
            raise ValueError(f"line {i}: invalid eventID")
        if not LOCATION_RE.fullmatch(lid):
            raise ValueError(f"line {i}: invalid locationID")
        if eid in out:
            raise ValueError(f"duplicate eventID: {eid}")
        y = date.fromisoformat(r["eventDate"].strip()).year
        out[eid] = (lid, y)
    return out


def audit(chorus_events: Path, chorus_taxa: Path, down_events: Path, down_taxa: Path) -> dict:
    ce = _events(_read(chorus_events, {"eventID","eventDate","locationID"}))
    de = _events(_read(down_events, {"eventID","eventDate","locationID"}))
    ct = _read(chorus_taxa, {"eventID","scientificName","occurrenceStatus"})
    dt = _read(down_taxa, {"eventID","scientificName","occurrenceStatus","lifeStage"})

    chorus_keys = defaultdict(set)
    down_keys = defaultdict(set)
    stage_rows = Counter()

    for i, r in enumerate(ct, 2):
        eid = r["eventID"].strip()
        if eid not in ce:
            raise ValueError(f"chorus taxa line {i}: unknown eventID")
        sp = r["scientificName"].strip()
        st = r["occurrenceStatus"].strip()
        if st not in STATUS:
            raise ValueError(f"chorus taxa line {i}: invalid occurrenceStatus")
        if sp in SHARED_TARGETS:
            lid, y = ce[eid]
            chorus_keys[(lid, sp, y)].add(eid)

    for i, r in enumerate(dt, 2):
        eid = r["eventID"].strip()
        if eid not in de:
            raise ValueError(f"downstream taxa line {i}: unknown eventID")
        sp = r["scientificName"].strip()
        st = r["occurrenceStatus"].strip()
        stage = r["lifeStage"].strip()
        if st not in STATUS:
            raise ValueError(f"downstream taxa line {i}: invalid occurrenceStatus")
        if stage not in DOWN_STAGES:
            raise ValueError(f"downstream taxa line {i}: unexpected lifeStage {stage!r}")
        if sp in SHARED_TARGETS and stage in {"larva","metamorph"}:
            lid, y = de[eid]
            down_keys[(lid, sp, y)].add(eid)
            stage_rows[(sp, stage)] += 1

    overlap = set(chorus_keys) & set(down_keys)
    by_species = Counter(k[1] for k in overlap)
    repeat_chorus = sum(len(chorus_keys[k]) >= 2 for k in overlap)
    temporal_order_ok = 0
    for key in overlap:
        c_dates = [date.fromisoformat(next(r["eventDate"] for r in _read(chorus_events, {"eventID","eventDate","locationID"}) if r["eventID"] == eid)) for eid in chorus_keys[key]]
        d_dates = [date.fromisoformat(next(r["eventDate"] for r in _read(down_events, {"eventID","eventDate","locationID"}) if r["eventID"] == eid)) for eid in down_keys[key]]
        if c_dates and d_dates and min(c_dates) <= max(d_dates):
            temporal_order_ok += 1

    return {
        "publisher_identity_join_only": True,
        "coordinate_join_used": False,
        "shared_location_species_years": len(overlap),
        "shared_by_species": dict(sorted(by_species.items())),
        "shared_units_with_ge2_chorus_events": repeat_chorus,
        "shared_units_with_chorus_not_after_all_downstream_events": temporal_order_ok,
        "downstream_stage_rows": {
            f"{sp}|{stage}": n for (sp,stage),n in sorted(stage_rows.items())
        },
        "ecological_association_opened": False,
        "structural_candidate_pass": len(overlap) >= 30 and repeat_chorus >= 20,
    }


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--chorus-events",type=Path,required=True)
    p.add_argument("--chorus-taxa",type=Path,required=True)
    p.add_argument("--down-events",type=Path,required=True)
    p.add_argument("--down-taxa",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(audit(args.chorus_events,args.chorus_taxa,args.down_events,args.down_taxa),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
