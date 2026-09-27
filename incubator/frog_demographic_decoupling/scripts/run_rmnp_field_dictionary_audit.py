#!/usr/bin/env python3
"""Read only publisher FGDC definitions for prespecified RMNP fields.

No CSV outcome values are opened. This is a schema-only audit to decide whether
species columns are detection/presence indicators and which habitat variables
are interpretable before any biological model is fitted.
"""
from __future__ import annotations
import json, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ITEM_ID="657ca143d34e23d35331ce9d"
ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
XML_NAME="romo_datarelease.xml"
FIELDS=[
    "psma","psma_stage","lisy","lisy_stage","amma","amma_stage",
    "fish","perc_surveyed","weather","wind","air_temp_c","water_temp_c",
    "site_length_m","site_width_m","max_depth","date","site_name"
]


def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-field-dictionary/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-field-dictionary/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()


def file_url(f):
    return f.get("downloadUri") or f.get("url") or f.get("uri")


def clean(x):
    return " ".join((x or "").split())


def main():
    item=get_json(ITEM_URL)
    xml_url=None
    for f in item.get("files") or []:
        if (f.get("name") or "")==XML_NAME:
            xml_url=file_url(f)
            break
    if not xml_url:
        raise SystemExit("metadata XML not found")
    root=ET.fromstring(get_bytes(xml_url))

    attrs={}
    for attr in root.findall(".//attr"):
        label=clean(attr.findtext("attrlabl"))
        if label not in FIELDS:
            continue
        enums={}
        for edom in attr.findall(".//edom"):
            v=clean(edom.findtext("edomv"))
            d=clean(edom.findtext("edomvd"))
            if v:
                enums[v]=d
        attrs[label]={
            "definition":clean(attr.findtext("attrdef")),
            "definition_source":clean(attr.findtext("attrdefs")),
            "enumerated":enums,
            "unrepresentable":[clean(x.text) for x in attr.findall(".//udom") if clean(x.text)],
            "range":[
                {
                    "min":clean(r.findtext("rdommin")),
                    "max":clean(r.findtext("rdommax")),
                    "unit":clean(r.findtext("attrunit"))
                }
                for r in attr.findall(".//rdom")
            ]
        }

    result={
        "audit":"rmnp_prespecified_field_dictionary_v0_1",
        "sciencebase_item_id":ITEM_ID,
        "requested_fields":FIELDS,
        "field_dictionary":attrs,
        "csv_values_read":False,
        "biological_outcomes_opened":False,
        "environment_effect_direction_opened":False
    }
    out=Path("frog_rmnp_field_dictionary_v0_1.json")
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(out.read_text(encoding="utf-8"))


if __name__=="__main__":
    main()
