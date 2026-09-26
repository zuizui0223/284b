#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ITEM_ID="657ca143d34e23d35331ce9d"
ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
XML_NAME="romo_datarelease.xml"
XML_SHA="b4d7926a1eadfc469c8bb491bd2553477ea6eb197b442fd7508595f9313cece3"
FIELDS={
    "psma","psma_stage","lisy","lisy_stage","fish","perc_surveyed",
    "weather","wind","air_temp_c","water_temp_c","max_depth",
    "site_length_m","site_width_m","date","site_name"
}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-dictionary-audit/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-dictionary-audit/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def file_url(f):
    return f.get("downloadUri") or f.get("url") or f.get("uri")

def norm(s):
    return " ".join((s or "").split())

def main():
    item=get_json(ITEM_URL)
    url=None
    for f in item.get("files") or []:
        if (f.get("name") or "")==XML_NAME:
            url=file_url(f)
            break
    if not url:
        raise SystemExit("metadata XML missing")
    data=get_bytes(url)
    if hashlib.sha256(data).hexdigest()!=XML_SHA:
        raise SystemExit("metadata hash drift")
    root=ET.fromstring(data)
    out={}
    for attr in root.findall(".//attr"):
        label=norm(attr.findtext("attrlabl"))
        if label not in FIELDS:
            continue
        enums={}
        for edom in attr.findall(".//edom"):
            v=norm(edom.findtext("edomv"))
            d=norm(edom.findtext("edomvd"))
            if v:
                enums[v]=d
        ranges=[]
        for rdom in attr.findall(".//rdom"):
            ranges.append({
                "min":norm(rdom.findtext("rdommin")),
                "max":norm(rdom.findtext("rdommax")),
                "unit":norm(rdom.findtext("attrunit")),
            })
        out[label]={
            "definition":norm(attr.findtext("attrdef")),
            "source":norm(attr.findtext("attrdefs")),
            "enumerated":enums,
            "ranges":ranges,
            "unrepresentable":[norm(x.text) for x in attr.findall(".//udom") if norm(x.text)],
        }
    missing=sorted(FIELDS-set(out))
    result={
        "audit":"rmnp_fgdc_model_dictionary_v0_1",
        "metadata_sha256":hashlib.sha256(data).hexdigest(),
        "fields":out,
        "missing_requested_fields":missing,
        "csv_values_read":False,
        "joint_stage_states_opened":False,
        "environment_effects_opened":False
    }
    Path("frog_rmnp_fgdc_model_dictionary_v0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
