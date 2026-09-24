#!/usr/bin/env python3
"""Structural-only audit of immutable Mohonk EDI package edi.398.4.

Reads identities, dates, species names, headers, and whether selected stage/weather
fields are empty. It does NOT parse or compare biological count values.
"""
from __future__ import annotations
import csv, hashlib, io, json, urllib.request
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

BASE="https://pasta.lternet.edu/package/data/eml/edi/398/4"
ENTITIES={
    "species":"737389d6c2090ee27a3084898f2e7853",
    "weather":"5835a29e0fbe1ba179ee5ffe27121df6",
    "location":"ceaabc36d68cdfb681122ce1f0941420",
}
PRIMARY="Lithobates sylvaticus"
VALIDATION="Pseudacris crucifer crucifer"
STAGE_FIELDS=["ChorusCode","ChorusCount","Live_n","AmplectantPairs_n","EggMass_n","TadLarv_n"]
REQUIRED=["ScientificName","Location","Sample_Date",*STAGE_FIELDS]


def fetch(entity):
    url=f"{BASE}/{entity}"
    req=urllib.request.Request(url,headers={"User-Agent":"frog-mohonk-edi-structural-audit/0.1"})
    with urllib.request.urlopen(req,timeout=90) as r:
        return r.read()


def parse_csv(data):
    text=data.decode("utf-8-sig")
    reader=csv.DictReader(io.StringIO(text))
    return reader.fieldnames or [], list(reader)


def nonempty(v):
    return v is not None and str(v).strip()!=""

def main():
    blobs={k:fetch(v) for k,v in ENTITIES.items()}
    sha={k:hashlib.sha256(v).hexdigest() for k,v in blobs.items()}
    headers={}
    rows={}
    for k,b in blobs.items():
        headers[k],rows[k]=parse_csv(b)

    missing=sorted(set(REQUIRED)-set(headers["species"]))
    if missing:
        raise SystemExit(f"missing required species columns: {missing}")

    species_rows=Counter()
    pool_rows=Counter()
    year_rows=Counter()
    month_rows=Counter()
    species_pool_year=defaultdict(set)
    species_pool_year_visits=defaultdict(lambda: defaultdict(set))
    coverage={PRIMARY:Counter(),VALIDATION:Counter()}
    species_total=Counter()

    for row in rows["species"]:
        sp=(row.get("ScientificName") or "").strip()
        loc=(row.get("Location") or "").strip()
        raw=(row.get("Sample_Date") or "").strip()
        if not sp or not loc or not raw:
            continue
        d=date.fromisoformat(raw[:10])
        species_rows[sp]+=1
        pool_rows[loc]+=1
        year_rows[d.year]+=1
        month_rows[d.month]+=1
        if sp in (PRIMARY,VALIDATION):
            species_total[sp]+=1
            species_pool_year[sp].add((loc,d.year))
            species_pool_year_visits[sp][(loc,d.year)].add(d)
            for f in STAGE_FIELDS:
                if nonempty(row.get(f)):
                    coverage[sp][f]+=1

    weather_headers=headers["weather"]
    # Freeze identity columns from common documented names only.
    weather_location = "Location" if "Location" in weather_headers else None
    weather_date = "Sample_Date" if "Sample_Date" in weather_headers else (
        "Date" if "Date" in weather_headers else None
    )

    weather_keys=set()
    weather_nonempty=Counter()
    if weather_location and weather_date:
        for row in rows["weather"]:
            loc=(row.get(weather_location) or "").strip()
            raw=(row.get(weather_date) or "").strip()
            if not loc or not raw:
                continue
            try:
                d=date.fromisoformat(raw[:10])
            except ValueError:
                continue
            weather_keys.add((loc,d))
            for f in weather_headers:
                if f not in {weather_location,weather_date} and nonempty(row.get(f)):
                    weather_nonempty[f]+=1

    primary_dates=[]
    primary_join=0
    for row in rows["species"]:
        if (row.get("ScientificName") or "").strip()!=PRIMARY:
            continue
        loc=(row.get("Location") or "").strip()
        raw=(row.get("Sample_Date") or "").strip()
        if not loc or not raw: continue
        d=date.fromisoformat(raw[:10])
        if d.year>=1991:
            primary_dates.append((loc,d))
            if (loc,d) in weather_keys:
                primary_join+=1

    def species_struct(sp):
        py={x for x in species_pool_year[sp] if x[1]>=1991}
        years={y for _,y in py}
        pools={p for p,_ in py}
        ge2=sum(
            len(species_pool_year_visits[sp][key])>=2
            for key in py
        )
        total=species_total[sp]
        cov={
            f:(coverage[sp][f]/total if total else 0.0)
            for f in STAGE_FIELDS
        }
        return {
            "rows":total,
            "distinct_pools_since_1991":len(pools),
            "years_since_1991":len(years),
            "pool_years_since_1991":len(py),
            "pool_years_ge2_visits_since_1991":ge2,
            "nonempty_fraction_by_field":cov
        }

    primary=species_struct(PRIMARY)
    validation=species_struct(VALIDATION)
    join_fraction=primary_join/len(primary_dates) if primary_dates else 0.0

    gate=(
        primary["distinct_pools_since_1991"]>=8
        and primary["years_since_1991"]>=20
        and primary["pool_years_since_1991"]>=150
        and primary["pool_years_ge2_visits_since_1991"]>=100
        and primary["nonempty_fraction_by_field"]["ChorusCode"]>=0.75
        and primary["nonempty_fraction_by_field"]["EggMass_n"]>=0.75
        and primary["nonempty_fraction_by_field"]["TadLarv_n"]>=0.75
        and join_fraction>=0.75
    )

    result={
        "audit":"mohonk_edi398_4_structural_v0_1",
        "package_id":"edi.398.4",
        "entity_sha256":sha,
        "headers":headers,
        "row_counts":{k:len(v) for k,v in rows.items()},
        "all_species_row_counts":dict(sorted(species_rows.items())),
        "distinct_locations_in_species_table":len(pool_rows),
        "year_range_species":[min(year_rows),max(year_rows)] if year_rows else None,
        "month_row_counts":dict(sorted(month_rows.items())),
        "primary_species":PRIMARY,
        "primary_structure":primary,
        "parallel_validation_species":VALIDATION,
        "parallel_validation_structure":validation,
        "weather_identity_columns":{
            "location":weather_location,
            "date":weather_date
        },
        "weather_nonempty_counts":dict(sorted(weather_nonempty.items())),
        "primary_weather_same_pool_date_join_fraction_since_1991":join_fraction,
        "structural_gate_pass":gate,
        "biological_count_values_parsed":False,
        "stage_association_opened":False,
        "hydroclimate_effect_direction_opened":False
    }
    out=Path("frog_mohonk_edi398_4_structural_v0_1.json")
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(out.read_text(encoding="utf-8"))


if __name__=="__main__":
    main()
