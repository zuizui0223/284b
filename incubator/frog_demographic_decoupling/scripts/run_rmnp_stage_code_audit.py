#!/usr/bin/env python3
"""Outcome-blind RMNP stage-code metadata audit for the wide ScienceBase table.

Reads only *_stage categorical codes and FGDC definitions. It never reads psma/lisy/amma
values, never cross-tabulates upstream vs downstream states, and never reads environmental
values for effect estimation.
"""
from __future__ import annotations
import csv, hashlib, io, json, re, urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

ITEM_ID="657ca143d34e23d35331ce9d"
ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
CSV_NAME="ROMO_data_release.csv"
XML_NAME="romo_datarelease.xml"
STAGE_COLS={
    "psma_stage":"Pseudacris maculata",
    "lisy_stage":"Lithobates sylvaticus",
    "amma_stage":"Ambystoma mavortium",
}
UPSTREAM=("adult","aural","call")
DOWNSTREAM=("egg","larv","tad")


def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-stage-code-audit/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-stage-code-audit/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()


def file_url(f):
    return f.get("downloadUri") or f.get("url") or f.get("uri")


def norm_text(x):
    return " ".join((x or "").split())


def find_file(item,name):
    for f in item.get("files") or []:
        if (f.get("name") or "") == name:
            u=file_url(f)
            if not u: raise RuntimeError(f"{name}: no download URI")
            return u
    raise RuntimeError(f"missing ScienceBase file {name}")


def attr_records(root):
    out={}
    for attr in root.findall(".//attr"):
        label=attr.findtext("attrlabl")
        if not label: continue
        label=label.strip()
        rec={
            "definition":norm_text(attr.findtext("attrdef")),
            "enumerated":{},
            "unrepresentable":[],
            "ranges":[],
        }
        for edom in attr.findall(".//edom"):
            v=norm_text(edom.findtext("edomv"))
            d=norm_text(edom.findtext("edomvd"))
            if v: rec["enumerated"][v]=d
        for udom in attr.findall(".//udom"):
            t=norm_text(udom.text)
            if t: rec["unrepresentable"].append(t)
        for rdom in attr.findall(".//rdom"):
            rec["ranges"].append({
                "min":norm_text(rdom.findtext("rdommin")),
                "max":norm_text(rdom.findtext("rdommax")),
                "unit":norm_text(rdom.findtext("attrunit"))
            })
        out[label]=rec
    return out


def semantic_flags(text):
    s=text.lower()
    return {
        "upstream":any(k in s for k in UPSTREAM),
        "downstream":any(k in s for k in DOWNSTREAM),
    }


def parse_date(value):
    s=(value or "").strip()
    if not s:
        return None
    candidates=[s, s.split(" ")[0], s.split("T")[0]]
    formats=("%Y-%m-%d","%m/%d/%Y","%m/%d/%y","%Y/%m/%d")
    for candidate in candidates:
        for fmt in formats:
            try:
                return datetime.strptime(candidate,fmt).date()
            except ValueError:
                pass
    # Final structural-only fallback: extract a four-digit year but do not invent month/day.
    m=re.search(r"(19|20)\\d{2}",s)
    if m:
        return date(int(m.group(0)),1,1)
    return None


def main():
    item=get_json(ITEM_URL)
    csv_data=get_bytes(find_file(item,CSV_NAME))
    xml_data=get_bytes(find_file(item,XML_NAME))
    if hashlib.sha256(csv_data).hexdigest()!="aa42c97dcc506b96f832c2ea4180f057527b1efeec302586d06801751c1cda3a":
        raise SystemExit("RMNP CSV hash drift from v0.10 structural receipt")

    metadata=attr_records(ET.fromstring(xml_data))
    text=csv_data.decode("utf-8-sig",errors="strict")
    reader=csv.DictReader(io.StringIO(text))
    headers=reader.fieldnames or []
    missing=[c for c in STAGE_COLS if c not in headers]
    if missing: raise SystemExit(f"missing frozen stage columns: {missing}")

    code_counts={c:Counter() for c in STAGE_COLS}
    site_year_by_code={c:defaultdict(set) for c in STAGE_COLS}
    all_site_years=set()
    visits=defaultdict(set)

    for row in reader:
        rawdate=(row.get("date") or "").strip()
        site=(row.get("site_name") or "").strip()
        if not rawdate or not site: continue
        d=parse_date(rawdate)
        if d is None or d.year<2003:
            continue
        key=(site,d.year)
        all_site_years.add(key)
        visits[key].add(rawdate)
        for col in STAGE_COLS:
            value=(row.get(col) or "").strip()
            if value:
                code_counts[col][value]+=1
                site_year_by_code[col][value].add(key)

    receipt={}
    qualified=[]
    for col,species in STAGE_COLS.items():
        meta=metadata.get(col,{})
        enums=meta.get("enumerated",{})
        code_info={}
        union_semantic_text=(meta.get("definition","")+" "+" ".join(f"{k} {v}" for k,v in enums.items()))
        overall_flags=semantic_flags(union_semantic_text)
        for code,n in sorted(code_counts[col].items()):
            definition=enums.get(code,"")
            flags=semantic_flags(f"{code} {definition}")
            code_info[code]={
                "rows":n,
                "post2002_site_years":len(site_year_by_code[col][code]),
                "publisher_definition":definition,
                "semantic_flags":flags,
            }
        if overall_flags["upstream"] and overall_flags["downstream"]:
            qualified.append(species)
        receipt[col]={
            "species":species,
            "metadata_definition":meta.get("definition",""),
            "publisher_enumerated_codes":enums,
            "observed_stage_code_structure":code_info,
            "documented_semantic_flags":overall_flags,
        }

    result={
        "audit":"rmnp_stage_code_schema_v0_1",
        "sciencebase_item_id":ITEM_ID,
        "csv_sha256":hashlib.sha256(csv_data).hexdigest(),
        "metadata_xml_sha256":hashlib.sha256(xml_data).hexdigest(),
        "post2002_site_years":len(all_site_years),
        "post2002_site_years_ge2_visits":sum(len(v)>=2 for v in visits.values()),
        "stage_columns":receipt,
        "taxa_with_metadata_documenting_upstream_and_downstream_semantics":qualified,
        "repaired_structural_gate_pass":(
            len(all_site_years)>=100
            and sum(len(v)>=2 for v in visits.values())>=50
            and len(qualified)>=2
        ),
        "psma_lisy_amma_values_read":False,
        "adult_downstream_joint_state_opened":False,
        "environment_effect_direction_opened":False,
    }
    out=Path("frog_rmnp_stage_code_schema_v0_1.json")
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(out.read_text(encoding="utf-8"))


if __name__=="__main__":
    main()
