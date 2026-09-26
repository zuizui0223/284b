#!/usr/bin/env python3
"""Fail-closed estimability audit for amphibian life-stage monitoring exports.

This script never classifies a biological recruitment failure. It only asks whether a
local export has enough explicit sampling structure to support later stage-specific
observation models.

Expected input is a normalized CSV created from a publisher export with at least:
    site_id, event_id, date, stage, status, count

Allowed normalized stages:
    adult_breeding, egg, larva, juvenile

Allowed status values:
    present, absent, missing, unsurveyed

The normalizer from source-specific Darwin Core fields is intentionally not guessed here.
It must be written after raw column names and vocabularies are inspected.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

REQUIRED = {"site_id", "event_id", "date", "stage", "status", "count"}
STAGES = ("adult_breeding", "egg", "larva", "juvenile")
STATUSES = {"present", "absent", "missing", "unsurveyed"}


def audit(path: Path) -> dict:
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = sorted(REQUIRED - fields)
        if missing:
            raise ValueError(f"missing required columns: {missing}")
        for i, row in enumerate(reader, start=2):
            stage = row["stage"].strip()
            status = row["status"].strip()
            if stage not in STAGES:
                raise ValueError(f"line {i}: unknown stage {stage!r}")
            if status not in STATUSES:
                raise ValueError(f"line {i}: unknown status {status!r}")
            if not row["site_id"].strip() or not row["event_id"].strip():
                raise ValueError(f"line {i}: blank site_id/event_id")
            try:
                d = date.fromisoformat(row["date"].strip())
            except Exception as exc:
                raise ValueError(f"line {i}: invalid ISO date") from exc
            raw_count = row["count"].strip()
            count = None if raw_count == "" else float(raw_count)
            if count is not None and count < 0:
                raise ValueError(f"line {i}: negative count")
            if status == "present" and (count is None or count <= 0):
                raise ValueError(f"line {i}: present requires count > 0")
            if status in {"missing", "unsurveyed"} and count is not None:
                raise ValueError(f"line {i}: {status} must not carry a count")
            rows.append({**row, "_date": d, "_count": count})

    event_keys = set()
    duplicate_event_stage = []
    site_year_events = defaultdict(set)
    stage_status = Counter()
    stage_positive_site_year = defaultdict(set)
    stage_dates = defaultdict(list)

    for row in rows:
        key = (row["event_id"], row["stage"])
        if key in event_keys:
            duplicate_event_stage.append(key)
        event_keys.add(key)
        sy = (row["site_id"], row["_date"].year)
        site_year_events[sy].add(row["event_id"])
        stage_status[(row["stage"], row["status"])] += 1
        if row["status"] == "present":
            stage_positive_site_year[row["stage"]].add(sy)
            stage_dates[row["stage"]].append(row["_date"].timetuple().tm_yday)

    visits = [len(v) for v in site_year_events.values()]
    repeated = sum(v >= 2 for v in visits)
    three_plus = sum(v >= 3 for v in visits)

    positive_sy = {s: len(stage_positive_site_year[s]) for s in STAGES}
    stage_date_range = {
        s: ([min(stage_dates[s]), max(stage_dates[s])] if stage_dates[s] else None)
        for s in STAGES
    }

    result = {
        "rows": len(rows),
        "site_years": len(site_year_events),
        "repeated_site_years_ge2": repeated,
        "repeated_site_years_ge3": three_plus,
        "visits_min": min(visits) if visits else 0,
        "visits_max": max(visits) if visits else 0,
        "positive_site_years_by_stage": positive_sy,
        "stage_doy_range": stage_date_range,
        "stage_status_counts": {
            s: {st: stage_status[(s, st)] for st in sorted(STATUSES)}
            for s in STAGES
        },
        "duplicate_event_stage_rows": len(duplicate_event_stage),
        "full_chain_estimability_candidate": (
            len(site_year_events) >= 30
            and three_plus >= 20
            and all(positive_sy[s] >= 10 for s in STAGES)
            and not duplicate_event_stage
        ),
        "biological_failure_classified": False,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--json", dest="json_path", type=Path)
    args = parser.parse_args()
    result = audit(args.csv)
    payload = json.dumps(result, indent=2, sort_keys=True)
    print(payload)
    if args.json_path:
        args.json_path.write_text(payload + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
