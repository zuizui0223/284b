#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

URL = "https://dwca-exports.ala.org.au/dr14760.zip"
NS = {"dwc": "http://rs.tdwg.org/dwc/text/"}


def fetch() -> bytes:
    req = urllib.request.Request(
        URL, headers={"User-Agent": "frogid-chorus-synchrony-structural-audit/0.3"}
    )
    with urllib.request.urlopen(req, timeout=180) as response:
        return response.read()


def local_term(term: str) -> str:
    if not term:
        return ""
    return term.rsplit("/", 1)[-1].rsplit("#", 1)[-1]


def decode_sep(value: str | None, default: str) -> str:
    if value is None:
        return default
    return bytes(value, "utf-8").decode("unicode_escape")


def core_reader(zf: zipfile.ZipFile):
    meta = ET.fromstring(zf.read("meta.xml"))
    core = meta.find("dwc:core", NS)
    if core is None:
        raise RuntimeError("DwC-A missing core")

    files = core.find("dwc:files", NS)
    location = files.find("dwc:location", NS) if files is not None else None
    if location is None or not location.text:
        raise RuntimeError("DwC-A core missing file location")
    table = location.text.strip()

    delimiter = decode_sep(core.attrib.get("fieldsTerminatedBy"), "\t")
    quotechar = decode_sep(core.attrib.get("fieldsEnclosedBy"), '"')
    ignore = int(core.attrib.get("ignoreHeaderLines", "0"))
    encoding = core.attrib.get("encoding", "UTF-8").replace("-", "")

    fields = {
        local_term(field.attrib.get("term", "")): int(field.attrib["index"])
        for field in core.findall("dwc:field", NS)
    }
    id_el = core.find("dwc:id", NS)
    id_index = int(id_el.attrib["index"]) if id_el is not None else None

    raw = zf.read(table).decode(encoding, errors="replace")
    reader = csv.reader(
        io.StringIO(raw),
        delimiter=delimiter,
        quotechar=quotechar or '"',
    )
    for _ in range(ignore):
        next(reader, None)

    return table, fields, id_index, reader


def get(row: list[str], fields: dict[str, int], name: str) -> str:
    idx = fields.get(name)
    if idx is None or idx >= len(row):
        return ""
    return row[idx].strip()


def parse_date(raw: str):
    s = str(raw or "").strip()
    m = re.search(
        r"(?<!\d)((?:19|20)\d{2})[-/]?(\d{2})?[-/]?(\d{2})?(?!\d)",
        s,
    )
    if not m:
        return None
    year = int(m.group(1))
    month = int(m.group(2) or 1)
    day = int(m.group(3) or 1)
    return (year, month, day)


def main() -> None:
    data = fetch()
    source_sha = hashlib.sha256(data).hexdigest()
    zf = zipfile.ZipFile(io.BytesIO(data))
    table, fields, id_index, reader = core_reader(zf)

    required = {"eventID", "scientificName", "eventDate"}
    missing = sorted(required - set(fields))
    if missing:
        raise SystemExit(f"DwC-A meta.xml missing required terms: {missing}; terms={sorted(fields)}")

    event_species: dict[str, set[str]] = defaultdict(set)
    dates = []
    states = Counter()
    behaviors = Counter()
    protocols = Counter()
    coordinate_uncertainty = Counter()

    occurrence_rows = 0
    date_events = set()
    time_events = set()
    coord_events = set()

    for row in reader:
        occurrence_rows += 1
        event_id = get(row, fields, "eventID")
        scientific_name = get(row, fields, "scientificName")
        if not event_id and id_index is not None and id_index < len(row):
            # Never substitute occurrenceID for eventID. This is only retained as a
            # diagnostic guard to show that a row ID exists while eventID is missing.
            pass
        if event_id and scientific_name:
            event_species[event_id].add(scientific_name)

        parsed = parse_date(get(row, fields, "eventDate"))
        if parsed:
            dates.append(parsed)
            if event_id:
                date_events.add(event_id)

        if get(row, fields, "eventTime") and event_id:
            time_events.add(event_id)

        lat = get(row, fields, "decimalLatitude")
        lon = get(row, fields, "decimalLongitude")
        try:
            la = float(lat)
            lo = float(lon)
            if -90 <= la <= 90 and -180 <= lo <= 180 and event_id:
                coord_events.add(event_id)
        except Exception:
            pass

        state = get(row, fields, "stateProvince")
        if state:
            states[state] += 1
        behavior = get(row, fields, "behavior")
        if behavior:
            behaviors[behavior] += 1
        protocol = get(row, fields, "samplingProtocol")
        if protocol:
            protocols[protocol] += 1
        uncertainty = get(row, fields, "coordinateUncertaintyInMeters")
        if uncertainty:
            coordinate_uncertainty[uncertainty] += 1

    richness = Counter(len(species) for species in event_species.values())
    events = len(event_species)
    min_date = min(dates) if dates else None
    max_date = max(dates) if dates else None

    multispecies_ge2 = sum(n for richness_value, n in richness.items() if richness_value >= 2)
    multispecies_ge3 = sum(n for richness_value, n in richness.items() if richness_value >= 3)

    v7_compatible = bool(
        occurrence_rows >= 1_000_000
        and max_date is not None
        and max_date >= (2024, 11, 1)
    )

    result = {
        "audit": "frogid_external_validation_structural_v0_3",
        "source_url": URL,
        "source_sha256": source_sha,
        "archive_files": zf.namelist(),
        "core_table": table,
        "core_terms": sorted(fields),
        "occurrence_rows": occurrence_rows,
        "distinct_eventIDs": events,
        "min_event_date": min_date,
        "max_event_date": max_date,
        "v7_compatible_by_frozen_rule": v7_compatible,
        "event_date_coverage_fraction": len(date_events) / events if events else 0.0,
        "event_time_coverage_fraction": len(time_events) / events if events else 0.0,
        "coordinate_coverage_fraction": len(coord_events) / events if events else 0.0,
        "distinct_state_territory_labels": len(states),
        "state_territory_row_counts": dict(sorted(states.items())),
        "behavior_marginal_counts": dict(sorted(behaviors.items())),
        "samplingProtocol_marginal_counts": dict(sorted(protocols.items())),
        "coordinate_uncertainty_marginal_top20": dict(coordinate_uncertainty.most_common(20)),
        "event_species_richness_histogram": {
            str(k): v for k, v in sorted(richness.items())
        },
        "multispecies_recordings_ge2": multispecies_ge2,
        "multispecies_recordings_ge3": multispecies_ge3,
        "max_species_per_recording": max(richness) if richness else 0,
        "structural_gate_pass": (
            events >= 100_000
            and multispecies_ge2 >= 30_000
            and multispecies_ge3 >= 5_000
            and len(states) >= 6
            and (len(date_events) / events if events else 0.0) >= 0.99
            and (len(coord_events) / events if events else 0.0) >= 0.90
        ),
        "weather_values_read": False,
        "weather_synchrony_association_opened": False,
    }

    out = Path("frog_frogid_validation_structural_v0_3.json")
    out.write_text(
        json.dumps(result, indent=2, sort_keys=True, default=list) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True, default=list))


if __name__ == "__main__":
    main()
