#!/usr/bin/env python3
"""Outcome-blind structural audit of FrogID v6 using Darwin Core Archive meta.xml.

The source has ~1M occurrence rows. This implementation treats meta.xml as the schema
authority and streams the core table into a temporary SQLite database. It opens only
event identity, species identity, date/time, coordinates, recorder, and state. It never
reads rainfall or computes a weather-synchrony effect.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sqlite3
import tempfile
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

URL = "https://dwca-exports.ala.org.au/dr14760.zip"
NS = {"dwc": "http://rs.tdwg.org/dwc/text/"}
WANTED = {
    "eventID",
    "scientificName",
    "eventDate",
    "eventTime",
    "decimalLatitude",
    "decimalLongitude",
    "recordedBy",
    "stateProvince",
}


def fetch() -> bytes:
    req = urllib.request.Request(
        URL, headers={"User-Agent": "frogid-synchrony-dwca-structural-audit/0.2.1"}
    )
    with urllib.request.urlopen(req, timeout=240) as response:
        return response.read()


def local_term(term: str) -> str:
    if not term:
        return ""
    return term.rsplit("/", 1)[-1].rsplit("#", 1)[-1]


def decode_sep(value: str | None, default: str) -> str:
    if value is None:
        return default
    return bytes(value, "utf-8").decode("unicode_escape")


def core_schema(zf: zipfile.ZipFile):
    root = ET.fromstring(zf.read("meta.xml"))
    core = root.find("dwc:core", NS)
    if core is None:
        raise SystemExit("DwC-A meta.xml has no core")

    files = core.find("dwc:files", NS)
    location = files.find("dwc:location", NS) if files is not None else None
    if location is None or not (location.text or "").strip():
        raise SystemExit("DwC-A core has no file location")

    id_el = core.find("dwc:id", NS)
    fields = {}
    for field in core.findall("dwc:field", NS):
        name = local_term(field.attrib.get("term", ""))
        if name in WANTED:
            fields[name] = int(field.attrib["index"])

    return {
        "filename": location.text.strip(),
        "rowType": core.attrib.get("rowType", ""),
        "encoding": core.attrib.get("encoding", "UTF-8"),
        "delimiter": decode_sep(core.attrib.get("fieldsTerminatedBy"), "\t"),
        "quotechar": decode_sep(core.attrib.get("fieldsEnclosedBy"), '"') or '"',
        "ignoreHeaderLines": int(core.attrib.get("ignoreHeaderLines", "0")),
        "id_index": int(id_el.attrib["index"]) if id_el is not None else None,
        "fields": fields,
    }


def field(row: list[str], fields: dict[str, int], name: str) -> str:
    idx = fields.get(name)
    if idx is None or idx >= len(row):
        return ""
    return row[idx].strip()


def main():
    data = fetch()
    source_sha = hashlib.sha256(data).hexdigest()
    zf = zipfile.ZipFile(io.BytesIO(data))
    schema = core_schema(zf)

    missing = sorted({"eventID", "scientificName"} - set(schema["fields"]))
    if missing:
        raise SystemExit(f"FrogID core missing required fields: {missing}")

    with tempfile.NamedTemporaryFile(suffix=".sqlite") as tmp:
        con = sqlite3.connect(tmp.name)
        con.executescript(
            """
            PRAGMA journal_mode=OFF;
            PRAGMA synchronous=OFF;
            PRAGMA temp_store=FILE;
            CREATE TABLE event_species (
              event_id TEXT NOT NULL,
              species TEXT NOT NULL,
              PRIMARY KEY(event_id, species)
            ) WITHOUT ROWID;
            CREATE TABLE events (
              event_id TEXT PRIMARY KEY,
              coord_present INTEGER NOT NULL DEFAULT 0,
              coord_first TEXT,
              coord_consistent INTEGER NOT NULL DEFAULT 1,
              date_present INTEGER NOT NULL DEFAULT 0,
              date_first TEXT,
              date_consistent INTEGER NOT NULL DEFAULT 1,
              time_present INTEGER NOT NULL DEFAULT 0,
              time_first TEXT,
              time_consistent INTEGER NOT NULL DEFAULT 1,
              recorder_present INTEGER NOT NULL DEFAULT 0,
              state TEXT
            );
            """
        )

        row_count = 0
        batch_species = []
        event_updates: dict[str, dict[str, object]] = {}
        states_seen: set[str] = set()

        def merge_value(rec, prefix, value):
            if not value:
                return
            present_key = f"{prefix}_present"
            first_key = f"{prefix}_first"
            ok_key = f"{prefix}_consistent"
            if not rec[present_key]:
                rec[present_key] = True
                rec[first_key] = value
            elif rec[first_key] != value:
                rec[ok_key] = False

        def flush():
            nonlocal batch_species, event_updates
            if batch_species:
                con.executemany(
                    "INSERT OR IGNORE INTO event_species(event_id,species) VALUES (?,?)",
                    batch_species,
                )
                batch_species = []
            if event_updates:
                for event_id, rec in event_updates.items():
                    cur = con.execute(
                        "SELECT coord_present,coord_first,coord_consistent,"
                        "date_present,date_first,date_consistent,"
                        "time_present,time_first,time_consistent,recorder_present,state "
                        "FROM events WHERE event_id=?",
                        (event_id,),
                    ).fetchone()
                    if cur is None:
                        con.execute(
                            "INSERT INTO events(event_id,coord_present,coord_first,"
                            "coord_consistent,date_present,date_first,date_consistent,"
                            "time_present,time_first,time_consistent,recorder_present,state)"
                            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                            (
                                event_id,
                                int(rec["coord_present"]),
                                rec["coord_first"],
                                int(rec["coord_consistent"]),
                                int(rec["date_present"]),
                                rec["date_first"],
                                int(rec["date_consistent"]),
                                int(rec["time_present"]),
                                rec["time_first"],
                                int(rec["time_consistent"]),
                                int(rec["recorder_present"]),
                                rec["state"] or None,
                            ),
                        )
                    else:
                        (
                            old_cp, old_coord, old_cok,
                            old_dp, old_date, old_dok,
                            old_tp, old_time, old_tok,
                            old_rec, old_state,
                        ) = cur
                        coord_ok = bool(old_cok) and bool(rec["coord_consistent"])
                        if old_cp and rec["coord_present"] and old_coord != rec["coord_first"]:
                            coord_ok = False
                        date_ok = bool(old_dok) and bool(rec["date_consistent"])
                        if old_dp and rec["date_present"] and old_date != rec["date_first"]:
                            date_ok = False
                        time_ok = bool(old_tok) and bool(rec["time_consistent"])
                        if old_tp and rec["time_present"] and old_time != rec["time_first"]:
                            time_ok = False
                        con.execute(
                            "UPDATE events SET "
                            "coord_present=?,coord_first=?,coord_consistent=?,"
                            "date_present=?,date_first=?,date_consistent=?,"
                            "time_present=?,time_first=?,time_consistent=?,"
                            "recorder_present=?,state=? WHERE event_id=?",
                            (
                                int(bool(old_cp) or bool(rec["coord_present"])),
                                old_coord or rec["coord_first"],
                                int(coord_ok),
                                int(bool(old_dp) or bool(rec["date_present"])),
                                old_date or rec["date_first"],
                                int(date_ok),
                                int(bool(old_tp) or bool(rec["time_present"])),
                                old_time or rec["time_first"],
                                int(time_ok),
                                int(bool(old_rec) or bool(rec["recorder_present"])),
                                old_state or rec["state"] or None,
                                event_id,
                            ),
                        )
                event_updates = {}
            con.commit()

        raw = zf.open(schema["filename"])
        text = io.TextIOWrapper(
            raw,
            encoding=schema["encoding"].replace("-", ""),
            errors="replace",
            newline="",
        )
        reader = csv.reader(
            text,
            delimiter=schema["delimiter"],
            quotechar=schema["quotechar"],
        )
        for _ in range(schema["ignoreHeaderLines"]):
            next(reader, None)

        for row in reader:
            row_count += 1
            event_id = field(row, schema["fields"], "eventID")
            if not event_id:
                continue
            species = field(row, schema["fields"], "scientificName")
            if species:
                batch_species.append((event_id, species))

            lat = field(row, schema["fields"], "decimalLatitude")
            lon = field(row, schema["fields"], "decimalLongitude")
            coord = ""
            try:
                la = float(lat)
                lo = float(lon)
                if -90 <= la <= 90 and -180 <= lo <= 180:
                    coord = f"{la:.8f},{lo:.8f}"
            except Exception:
                pass

            date_value = field(row, schema["fields"], "eventDate")
            time_value = field(row, schema["fields"], "eventTime")
            recorder = field(row, schema["fields"], "recordedBy")
            state = field(row, schema["fields"], "stateProvince")

            # Batch keeps only the latest row's structural values; flush logic compares
            # those with the already persisted event. To preserve within-batch conflicts,
            # merge before assignment here.
            rec = event_updates.get(event_id)
            if rec is None:
                rec = {
                    "coord_present": False, "coord_first": None, "coord_consistent": True,
                    "date_present": False, "date_first": None, "date_consistent": True,
                    "time_present": False, "time_first": None, "time_consistent": True,
                    "recorder_present": False, "state": None,
                }
                event_updates[event_id] = rec
            merge_value(rec, "coord", coord)
            merge_value(rec, "date", date_value)
            merge_value(rec, "time", time_value)
            rec["recorder_present"] = bool(rec["recorder_present"]) or bool(recorder)
            if state:
                states_seen.add(state)
                if not rec["state"]:
                    rec["state"] = state

            if row_count % 20000 == 0:
                flush()

        flush()

        event_count = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        multispecies = con.execute(
            "SELECT COUNT(*) FROM ("
            "SELECT event_id FROM event_species GROUP BY event_id HAVING COUNT(*)>=2)"
        ).fetchone()[0]
        distinct_species = con.execute(
            "SELECT COUNT(DISTINCT species) FROM event_species"
        ).fetchone()[0]
        richness_rows = con.execute(
            "SELECT richness,COUNT(*) FROM ("
            "SELECT event_id,COUNT(*) richness FROM event_species GROUP BY event_id)"
            " GROUP BY richness ORDER BY richness"
        ).fetchall()
        richness = {str(k): v for k, v in richness_rows}

        stats = con.execute(
            "SELECT "
            "SUM(coord_present),SUM(date_present),SUM(time_present),SUM(recorder_present),"
            "SUM(CASE WHEN coord_present=1 AND coord_consistent=1 THEN 1 ELSE 0 END),"
            "SUM(CASE WHEN date_present=1 AND date_consistent=1 THEN 1 ELSE 0 END),"
            "SUM(CASE WHEN time_present=1 AND time_consistent=1 THEN 1 ELSE 0 END)"
            " FROM events"
        ).fetchone()
        (
            coord_events,
            date_events,
            time_events,
            recorder_events,
            coord_consistent,
            date_consistent,
            time_consistent,
        ) = [int(x or 0) for x in stats]

        states = len(states_seen)

    def frac(value):
        return value / event_count if event_count else 0.0

    result = {
        "audit": "frogid_v6_synchrony_structural_v0_2_1",
        "source_url": URL,
        "source_sha256": source_sha,
        "archive_files": zf.namelist(),
        "dwca_core": {
            "filename": schema["filename"],
            "rowType": schema["rowType"],
            "encoding": schema["encoding"],
            "delimiter_repr": repr(schema["delimiter"]),
            "ignoreHeaderLines": schema["ignoreHeaderLines"],
            "mapped_fields": sorted(schema["fields"]),
        },
        "occurrence_rows": row_count,
        "events": event_count,
        "distinct_species": distinct_species,
        "distinct_states": int(states),
        "multispecies_events": int(multispecies),
        "event_species_richness_histogram": richness,
        "coordinate_event_coverage_fraction": frac(coord_events),
        "date_event_coverage_fraction": frac(date_events),
        "time_event_coverage_fraction": frac(time_events),
        "recordedBy_event_coverage_fraction": frac(recorder_events),
        "coordinate_consistency_fraction_all_events": frac(coord_consistent),
        "date_consistency_fraction_all_events": frac(date_consistent),
        "time_consistency_fraction_all_events": frac(time_consistent),
        "structural_gate_pass": (
            event_count >= 100000
            and multispecies >= 10000
            and states >= 5
            and frac(coord_events) >= 0.95
            and frac(date_events) >= 0.99
            and frac(time_events) >= 0.90
            and frac(coord_consistent) >= 0.99
        ),
        "rainfall_values_read": False,
        "weather_synchrony_association_opened": False,
    }
    Path("frog_frogid_v6_synchrony_structural_v0_2.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
