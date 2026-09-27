#!/usr/bin/env python3
"""Download fixed IPT DwC-A versions and perform a structural-only overlap audit.

This program is deliberately forbidden from reading individualCount or estimating
any adult-to-downstream ecological association. It opens only source structure:
stable event/location identity, target-species row presence, life-stage labels,
repeat visits, temporal ordering, and whether larval sampling-effort metadata exists.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

SOURCES = {
    "chorus": {
        "url": "https://ipt.inbo.be/archive.do?r=meetnetten-amphibia-roepkoren-occurrences&v=1.27",
        "doi": "10.15468/d4bu8j",
        "version": "1.27",
    },
    "downstream": {
        "url": "https://ipt.inbo.be/archive.do?r=meetnetten-amfibieen-larven-metamorfen-occurrences&v=1.24",
        "doi": "10.15468/swgure",
        "version": "1.24",
    },
}
TARGETS = ("Hyla arborea", "Pelobates fuscus")
DOWN_STAGES = {"larva", "metamorph"}
DWC_TEXT_NS = {"dwc": "http://rs.tdwg.org/dwc/text/"}


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "frog-demographic-decoupling-structural-audit/0.1"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()


def local_term(term: str) -> str:
    if not term:
        return ""
    return term.rsplit("/", 1)[-1].rsplit("#", 1)[-1]


def decode_sep(value: str | None, default: str) -> str:
    if value is None:
        return default
    return bytes(value, "utf-8").decode("unicode_escape")


def load_meta(archive: bytes):
    zf = zipfile.ZipFile(io.BytesIO(archive))
    meta = ET.fromstring(zf.read("meta.xml"))
    return zf, meta


def section_rows(zf: zipfile.ZipFile, section: ET.Element):
    files = section.find("dwc:files", DWC_TEXT_NS)
    if files is None:
        raise ValueError("DwC-A section missing files")
    location = files.find("dwc:location", DWC_TEXT_NS)
    if location is None or not location.text:
        raise ValueError("DwC-A section missing location")
    filename = location.text.strip()

    encoding = section.attrib.get("encoding", "UTF-8")
    delimiter = decode_sep(section.attrib.get("fieldsTerminatedBy"), "\t")
    quote = decode_sep(section.attrib.get("fieldsEnclosedBy"), '"')
    ignore = int(section.attrib.get("ignoreHeaderLines", "0"))

    id_el = section.find("dwc:id", DWC_TEXT_NS)
    coreid_el = section.find("dwc:coreid", DWC_TEXT_NS)
    id_index = int(id_el.attrib["index"]) if id_el is not None else None
    coreid_index = int(coreid_el.attrib["index"]) if coreid_el is not None else None

    fields = {}
    for field in section.findall("dwc:field", DWC_TEXT_NS):
        fields[local_term(field.attrib.get("term", ""))] = int(field.attrib["index"])

    text = zf.read(filename).decode(encoding.replace("-", ""), errors="strict")
    reader = csv.reader(io.StringIO(text), delimiter=delimiter, quotechar=quote or '"')
    for _ in range(ignore):
        next(reader, None)
    for row in reader:
        yield row, fields, id_index, coreid_index


def find_section(meta: ET.Element, kind: str, contains: str | None = None) -> ET.Element:
    if kind == "core":
        section = meta.find("dwc:core", DWC_TEXT_NS)
        if section is None:
            raise ValueError("missing core")
        return section
    candidates = meta.findall("dwc:extension", DWC_TEXT_NS)
    if contains:
        for section in candidates:
            if contains.lower() in section.attrib.get("rowType", "").lower():
                return section
    raise ValueError(f"missing extension containing {contains!r}")


def field(row, fields, name, default=""):
    idx = fields.get(name)
    if idx is None or idx >= len(row):
        return default
    return row[idx].strip()


def core_events(zf, meta):
    section = find_section(meta, "core")
    out = {}
    for row, fields, id_index, _ in section_rows(zf, section):
        core_id = row[id_index].strip() if id_index is not None else field(row, fields, "eventID")
        event_id = field(row, fields, "eventID", core_id)
        location_id = field(row, fields, "locationID")
        event_date = field(row, fields, "eventDate")
        if not location_id or not event_date:
            raise ValueError(f"event lacks locationID/eventDate: {event_id}")
        out[core_id] = {
            "eventID": event_id,
            "locationID": location_id,
            "date": date.fromisoformat(event_date[:10]),
        }
    return out


def occurrence_structure(zf, meta, events, downstream=False):
    section = find_section(meta, "extension", "Occurrence")
    keys = defaultdict(set)
    status_counts = Counter()
    stage_counts = Counter()
    for row, fields, _, coreid_index in section_rows(zf, section):
        if "individualCount" in fields:
            # Guardrail: the structural audit must never read abundance values.
            pass
        core_id = row[coreid_index].strip()
        if core_id not in events:
            raise ValueError(f"occurrence references unknown core id {core_id}")
        species = field(row, fields, "scientificName")
        if species not in TARGETS:
            continue
        status = field(row, fields, "occurrenceStatus")
        stage = field(row, fields, "lifeStage")
        event = events[core_id]
        key = (event["locationID"], species, event["date"].year)

        if downstream:
            if stage not in DOWN_STAGES:
                continue
            keys[key].add(core_id)
            stage_counts[(species, stage)] += 1
            status_counts[(species, stage, status)] += 1
        else:
            # Target-species record existence is enough for the structural audit.
            keys[key].add(core_id)
            status_counts[(species, "chorus", status)] += 1
    return keys, status_counts, stage_counts


def effort_events(zf, meta):
    try:
        section = find_section(meta, "extension", "MeasurementOrFact")
    except ValueError:
        return set()
    events = set()
    for row, fields, _, coreid_index in section_rows(zf, section):
        if field(row, fields, "measurementType") == "number of sweeps":
            core_id = row[coreid_index].strip()
            value = field(row, fields, "measurementValue")
            if value != "":
                events.add(core_id)
    return events


def main():
    archives = {name: download(spec["url"]) for name, spec in SOURCES.items()}
    sha256 = {name: hashlib.sha256(data).hexdigest() for name, data in archives.items()}

    cz, cm = load_meta(archives["chorus"])
    dz, dm = load_meta(archives["downstream"])
    chorus_events = core_events(cz, cm)
    downstream_events = core_events(dz, dm)

    chorus_keys, chorus_status, _ = occurrence_structure(cz, cm, chorus_events, downstream=False)
    downstream_keys, downstream_status, stage_counts = occurrence_structure(
        dz, dm, downstream_events, downstream=True
    )
    sweeps = effort_events(dz, dm)

    overlap = set(chorus_keys) & set(downstream_keys)
    by_species = Counter(key[1] for key in overlap)

    repeat_chorus = 0
    ordered = 0
    effort_covered = 0
    overlap_stage = Counter()

    for key in overlap:
        cids = chorus_keys[key]
        dids = downstream_keys[key]
        if len(cids) >= 2:
            repeat_chorus += 1
        if any(chorus_events[c]["date"] <= downstream_events[d]["date"] for c in cids for d in dids):
            ordered += 1
        if any(d in sweeps for d in dids):
            effort_covered += 1

        species = key[1]
        for d in dids:
            # stage is reconstructed without reading abundance; scan only stage label for this event/species.
            pass

    result = {
        "audit": "meetnetten_structural_overlap_v0_1",
        "source_versions": {
            name: {
                "doi": SOURCES[name]["doi"],
                "version": SOURCES[name]["version"],
                "sha256": sha256[name],
                "bytes": len(archives[name]),
            }
            for name in SOURCES
        },
        "core_event_counts": {
            "chorus": len(chorus_events),
            "downstream": len(downstream_events),
        },
        "target_species": list(TARGETS),
        "shared_location_species_years": len(overlap),
        "shared_by_species": dict(sorted(by_species.items())),
        "shared_units_with_ge2_chorus_events": repeat_chorus,
        "shared_units_with_chorus_not_after_downstream": ordered,
        "shared_units_with_number_of_sweeps_metadata": effort_covered,
        "downstream_stage_row_counts": {
            f"{species}|{stage}": count
            for (species, stage), count in sorted(stage_counts.items())
        },
        "chorus_status_row_counts": {
            f"{species}|{status}": count
            for (species, _stage, status), count in sorted(chorus_status.items())
        },
        "downstream_status_row_counts": {
            f"{species}|{stage}|{status}": count
            for (species, stage, status), count in sorted(downstream_status.items())
        },
        "structural_gate": {
            "min_shared_units": 30,
            "min_ge2_chorus_units": 20,
            "min_temporally_ordered_units": 20,
            "requires_effort_metadata": True,
            "pass": (
                len(overlap) >= 30
                and repeat_chorus >= 20
                and ordered >= 20
                and effort_covered > 0
            ),
        },
        "abundance_columns_read": False,
        "adult_downstream_association_opened": False,
        "environment_effect_direction_opened": False,
    }

    out = Path("frog_meetnetten_structural_audit_v0_1.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
