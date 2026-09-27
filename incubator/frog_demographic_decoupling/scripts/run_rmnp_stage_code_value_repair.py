#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, re, urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
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
UPSTREAM_TERMS=("adult","aural","call")
DOWNSTREAM_TERMS=("egg","larv","tad")

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-stage-code-v0.2","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-stage-code-v0.2"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def file_url(f):
    return f.get("downloadUri") or f.get("url") or f.get("uri")

def find_file(item,name):
    for f in item.get("files") or []:
        if (f.get("name") or "")==name:
            u=file_url(f)
            if not u:
                raise RuntimeError(f"{name}: no download URI")
            return u
    raise RuntimeError(f"missing file {name}")

def norm(s):
    return " ".join((s or "").split())

def metadata_enums(xml_bytes):
    root=ET.fromstring(xml_bytes)
    out={}
    for attr in root.findall(".//attr"):
        label=norm(attr.findtext("attrlabl"))
        if label not in STAGE_COLS:
            continue
        enums={}
        for edom in attr.findall(".//edom"):
            code=norm(edom.findtext("edomv"))
            desc=norm(edom.findtext("edomvd"))
            if code:
                enums[code]=desc
        out[label]={"definition":norm(attr.findtext("attrdef")),"enumerated":enums}
    return out

def year_from_string(s):
    if not s:
        return None
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(s))
    return int(m.group(1)) if m else None

def semantic(desc):
    s=(desc or "").lower()
    return {
        "upstream":any(t in s for t in UPSTREAM_TERMS),
        "downstream":any(t in s for t in DOWNSTREAM_TERMS),
    }

def main():
    item=get_json(ITEM_URL)
    csv_bytes=get_bytes(find_file(item,CSV_NAME))
    xml_bytes=get_bytes(find_file(item,XML_NAME))
    if hashlib.sha256(csv_bytes).hexdigest()!="aa42c97dcc506b96f832c2ea4180f057527b1efeec302586d06801751c1cda3a":
        raise SystemExit("CSV hash drift")
    if hashlib.sha256(xml_bytes).hexdigest()!="b4d7926a1eadfc469c8bb491bd2553477ea6eb197b442fd7508595f9313cece3":
        raise SystemExit("metadata XML hash drift")

    meta=metadata_enums(xml_bytes)
    reader=csv.DictReader(io.StringIO(csv_bytes.decode("utf-8-sig",errors="strict")))
    headers=reader.fieldnames or []
    required={"date","site_name",*STAGE_COLS}
    missing=sorted(required-set(headers))
    if missing:
        raise SystemExit(f"missing required columns: {missing}")

    stage_counts={c:Counter() for c in STAGE_COLS}
    stage_siteyears={c:defaultdict(set) for c in STAGE_COLS}
    visits=defaultdict(set)

    for row in reader:
        site=(row.get("site_name") or "").strip()
        raw_date=(row.get("date") or "").strip()
        year=year_from_string(raw_date)
        if site and year and year>=2003:
            visits[(site,year)].add(raw_date)
        for col in STAGE_COLS:
            code=(row.get(col) or "").strip()
            if not code:
                continue
            stage_counts[col][code]+=1
            if site and year and year>=2003:
                stage_siteyears[col][code].add((site,year))

    receipts={}
    qualified=[]
    all_documented=True
    for col,species in STAGE_COLS.items():
        enums=(meta.get(col) or {}).get("enumerated",{})
        observed=stage_counts[col]
        observed_info={}
        has_up=False
        has_down=False
        for code,n in sorted(observed.items()):
            desc=enums.get(code)
            flags=semantic(desc or "")
            if desc is None:
                all_documented=False
            has_up = has_up or flags["upstream"]
            has_down = has_down or flags["downstream"]
            observed_info[code]={
                "rows":n,
                "post2002_site_years":len(stage_siteyears[col][code]),
                "documented":desc is not None,
                "publisher_definition":desc,
                "semantic_flags":flags,
            }
        if has_up and has_down and observed:
            qualified.append(species)
        receipts[col]={
            "species":species,
            "metadata_definition":(meta.get(col) or {}).get("definition",""),
            "publisher_enumerated_codes":enums,
            "observed_stage_codes":observed_info,
            "observed_has_upstream_code":has_up,
            "observed_has_downstream_code":has_down,
        }

    result={
        "audit":"rmnp_stage_code_value_repair_v0_2",
        "csv_sha256":hashlib.sha256(csv_bytes).hexdigest(),
        "metadata_xml_sha256":hashlib.sha256(xml_bytes).hexdigest(),
        "post2002_site_years":len(visits),
        "post2002_site_years_ge2_visits":sum(len(v)>=2 for v in visits.values()),
        "stage_columns":receipts,
        "taxa_with_observed_documented_upstream_and_downstream_codes":qualified,
        "all_observed_nonmissing_stage_codes_documented":all_documented,
        "structural_gate_pass":(
            len(visits)>=100
            and sum(len(v)>=2 for v in visits.values())>=50
            and len(qualified)>=2
            and all_documented
        ),
        "species_detection_columns_read":False,
        "environment_values_read":False,
        "adult_downstream_joint_state_opened":False,
    }
    out=Path("frog_rmnp_stage_code_value_repair_v0_2.json")
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(out.read_text(encoding="utf-8"))

if __name__=="__main__":
    main()
